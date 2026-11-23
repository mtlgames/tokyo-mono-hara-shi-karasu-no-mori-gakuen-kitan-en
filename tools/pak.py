"""pak.py: CROW.PAK archive (the game's one data archive) list / extract / rebuild.

Header (LE u32): ndirs, nfiles, names_end, data_start. Then ndirs x 12-byte dir records
(name_off u32, first_subdir u16, n_subdirs u16, first_file u16, n_files u16), nfiles x 12-byte file records
(name_off u32, offset u32 relative to data_start, size u32), then the NUL-terminated name table.
Files are 0x800-aligned and zero-padded. See docs/re/pak.md.

    python -X utf8 tools/pak.py list PAK
    python -X utf8 tools/pak.py x PAK OUTDIR
"""
import struct
import sys
from pathlib import Path

ALIGN = 0x800


def is_pak(d):
    """True when bytes d start with a PAK header (root dir named '.')."""
    if len(d) < 16:
        return False
    nd, nf, _, ds = struct.unpack_from("<4I", d)
    nt = 0x10 + nd * 12 + nf * 12
    return 0 < nd < 0x1000 and nf < 0x10000 and nt + 2 <= ds <= len(d) and d[nt:nt + 2] == b".\0"


class Pak:
    def __init__(self, path):
        self.path = Path(path)
        with open(path, "rb") as f:
            head = f.read(16)
            self.ndirs, self.nfiles, self.names_end, self.data_start = struct.unpack("<4I", head)
            f.seek(0)
            self.toc = f.read(self.data_start)
        d = self.toc
        fe = 0x10 + self.ndirs * 12
        self.file_rec = fe
        nt = fe + self.nfiles * 12
        name = lambda o: d[nt + o:d.index(b"\0", nt + o)].decode("ascii")
        dirs = [struct.unpack_from("<I4H", d, 0x10 + i * 12) for i in range(self.ndirs)]
        parent = {0: ""}
        for i, (n, s1, c1, s2, c2) in enumerate(dirs):
            base = parent[i]
            for j in range(s1, s1 + c1):
                parent[j] = f"{base}{name(dirs[j][0])}/"
        self.files = []  # (path, offset, size, index)
        owner = {}
        for i, (n, s1, c1, s2, c2) in enumerate(dirs):
            for k in range(s2, s2 + c2):
                owner[k] = parent[i]
        for k in range(self.nfiles):
            n, off, size = struct.unpack_from("<3I", d, fe + k * 12)
            self.files.append((owner[k] + name(n), off, size, k))

    def read(self, k):
        _, off, size, _ = self.files[k]
        with open(self.path, "rb") as f:
            f.seek(self.data_start + off)
            return f.read(size)

    def rebuild(self, out, repl=None):
        """Write a new PAK to out. repl: {index or path: bytes}. Unchanged files keep their bytes; layout is
        recomputed in file-index order with 0x800 alignment (the original layout is reproduced when nothing changes)."""
        repl = repl or {}
        bypath = {p: k for p, _, _, k in self.files}
        repl = {(bypath[k] if isinstance(k, str) else k): v for k, v in repl.items()}
        toc = bytearray(self.toc)
        order = sorted(range(self.nfiles), key=lambda k: self.files[k][1])
        with open(self.path, "rb") as src, open(out, "wb") as dst:
            dst.write(toc)
            pos = 0
            for k in order:
                _, off, size, _ = self.files[k]
                if k in repl:
                    data = repl[k]
                else:
                    src.seek(self.data_start + off)
                    data = src.read(size)
                struct.pack_into("<II", toc, self.file_rec + k * 12 + 4, pos, len(data))
                dst.write(data)
                pad = -len(data) % ALIGN
                dst.write(b"\0" * pad)
                pos += len(data) + pad
            tail = self.path.stat().st_size - dst.tell()  # the original ends with zero padding past the last file
            if tail > 0:
                dst.write(b"\0" * tail)
            dst.seek(0)
            dst.write(toc)


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
