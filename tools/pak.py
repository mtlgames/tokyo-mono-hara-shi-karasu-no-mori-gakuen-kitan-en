"""pak.py: CROW.PAK archive (the game's one data archive) list / extract / rebuild, nested paks included.

Header (LE u32): ndirs, nfiles, names_end, data_start. Then ndirs x 12-byte dir records
(name_off u32, first_subdir u16, n_subdirs u16, first_file u16, n_files u16), nfiles x 12-byte file records
(name_off u32, offset u32 relative to data_start, size u32), then the NUL-terminated name table.
CROW.PAK files are 0x800-aligned, nested paks 4-aligned, both zero-padded. See docs/re/pak.md.

Edits are keyed by the path unpack_all.py writes: nested members as <outer.pak>/<inner path>, x.zdv as x
(the payload is inflated; the build recompresses it). `editor()` turns {path: bytes} into a rebuild callback.

    python -X utf8 tools/pak.py list PAK
    python -X utf8 tools/pak.py x PAK OUTDIR
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import zdv  # noqa: E402

ALIGN = 0x800
NESTED_ALIGN = 4  # every one of the 1401 nested paks repacks byte-identical with this


def is_pak(d):
    """True when bytes d start with a PAK header (root dir named '.')."""
    if len(d) < 16:
        return False
    nd, nf, _, ds = struct.unpack_from("<4I", d)
    nt = 0x10 + nd * 12 + nf * 12
    return 0 < nd < 0x1000 and nf < 0x10000 and nt + 2 <= ds <= len(d) and d[nt:nt + 2] == b".\0"


def parse(d):
    """d: bytes holding at least the TOC. Returns (data_start, file_rec offset, [(path, offset, size, index)])."""
    ndirs, nfiles, _, data_start = struct.unpack_from("<4I", d)
    fe = 0x10 + ndirs * 12
    nt = fe + nfiles * 12
    name = lambda o: d[nt + o:d.index(b"\0", nt + o)].decode("ascii")
    dirs = [struct.unpack_from("<I4H", d, 0x10 + i * 12) for i in range(ndirs)]
    parent = {0: ""}
    owner = {}
    for i, (n, s1, c1, s2, c2) in enumerate(dirs):
        for j in range(s1, s1 + c1):
            parent[j] = f"{parent[i]}{name(dirs[j][0])}/"
        for k in range(s2, s2 + c2):
            owner[k] = i
    files = []
    for k in range(nfiles):
        n, off, size = struct.unpack_from("<3I", d, fe + k * 12)
        files.append((parent[owner[k]] + name(n), off, size, k))
    return data_start, fe, files


class Pak:
    """A PAK file on disk, or one stored at byte `base` (length `length`) inside a bigger file such as the ISO."""

    def __init__(self, path, base=0, length=None):
        self.path, self.base = Path(path), base
        self.length = self.path.stat().st_size - base if length is None else length
        with open(path, "rb") as f:
            f.seek(base)
            head = f.read(16)
            self.nfiles, ds = struct.unpack_from("<I", head, 4)[0], struct.unpack_from("<I", head, 12)[0]
            f.seek(base)
            self.toc = f.read(ds)
        self.data_start, self.file_rec, self.files = parse(self.toc)

    def read(self, k):
        _, off, size, _ = self.files[k]
        with open(self.path, "rb") as f:
            f.seek(self.base + self.data_start + off)
            return f.read(size)

    def rebuild(self, out, edit=None):
        """Write a new PAK to out. edit(k, raw) -> bytes gives each member's new bytes (None: all unchanged). Layout is
        recomputed in original disc order with 0x800 alignment, so no edits reproduce the original byte for byte."""
        toc = bytearray(self.toc)
        order = sorted(range(self.nfiles), key=lambda k: self.files[k][1])
        with open(self.path, "rb") as src, open(out, "wb") as dst:
            dst.write(toc)
            pos = 0
            for k in order:
                _, off, size, _ = self.files[k]
                src.seek(self.base + self.data_start + off)
                data = src.read(size)
                if edit:
                    data = edit(k, data)
                struct.pack_into("<II", toc, self.file_rec + k * 12 + 4, pos, len(data))
                dst.write(data)
                pad = -len(data) % ALIGN
                dst.write(b"\0" * pad)
                pos += len(data) + pad
            tail = self.length - dst.tell()  # the original ends with zero padding past the last file
            if tail > 0:
                dst.write(b"\0" * tail)
            dst.seek(0)
            dst.write(toc)


def repack(d, repl=None, align=NESTED_ALIGN):
    """Rebuild a nested pak held in bytes d; repl {index: bytes}. Original disc order, `align` zero padding."""
    repl = repl or {}
    ds, fe, files = parse(d)
    out = bytearray(d[:ds])
    pos = 0
    for _, off, size, k in sorted(files, key=lambda f: f[1]):
        data = repl.get(k, d[ds + off:ds + off + size])
        struct.pack_into("<II", out, fe + k * 12 + 4, pos, len(data))
        pad = -len(data) % align
        out += data + b"\0" * pad
        pos += len(data) + pad
    return bytes(out)


def unpacked(name):
    return name[:-4] if name.endswith(".zdv") else name


def group(files, edits):
    """{path: bytes} -> {member index: {rest of path ('' = the member itself): bytes}}."""
    names = {unpacked(p): k for p, _, _, k in files}
    by = {}
    for key, v in edits.items():
        parts = key.split("/")
        for i in range(len(parts), 0, -1):
            k = names.get("/".join(parts[:i]))
            if k is not None:
                by.setdefault(k, {})["/".join(parts[i:])] = v
                break
        else:
            raise KeyError(f"no archive member for edit {key}")
    return by


def member(raw, name, edits, force=False):
    """New raw bytes for one member stored as `name`. force: rebuild nested paks and recompress zdv even unedited
    (the identity build uses it to prove both writers)."""
    if not edits and not force:
        return raw
    z = name.endswith(".zdv")
    body = zdv.inflate(raw) if z else raw
    if "" in edits:
        body = edits[""]
    elif is_pak(body):
        ds, _, files = parse(body)
        sub = group(files, edits)
        repl = {k: member(body[ds + off:ds + off + size], p, sub.get(k, {}), force)
                for p, off, size, k in files if force or k in sub}
        body = repack(body, repl)
    elif edits:
        raise KeyError(f"{name} is not a pak, cannot edit {sorted(edits)}")
    return zdv.deflate(body, stored=zdv.is_stored(raw)) if z else body


def editor(pak, edits, force=False):
    """Rebuild callback for Pak.rebuild applying {unpacked path: bytes}."""
    by = group(pak.files, edits)
    return lambda k, raw: member(raw, pak.files[k][0], by.get(k, {}), force)


def main(argv):
    if len(argv) < 2 or argv[0] not in ("list", "x"):
        sys.exit(__doc__)
    p = Pak(argv[1])
    if argv[0] == "list":
        for path, off, size, k in p.files:
            print(f"{k:5d} {off:#010x} {size:9d} {path}")
    else:
        outdir = Path(argv[2])
        for path, off, size, k in p.files:
            o = outdir / path
            o.parent.mkdir(parents=True, exist_ok=True)
            o.write_bytes(p.read(k))
        print(f"{p.nfiles} files -> {outdir}")


if __name__ == "__main__":
    main(sys.argv[1:])
