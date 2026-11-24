import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))
import pak  # noqa: E402
import zdv  # noqa: E402


def make_pak(files):
    """Minimal one-dir pak: {name: bytes} under the root '.'."""
    names = b".\0" + b"".join(n.encode() + b"\0" for n in files)
    nt = 0x10 + 12 + 12 * len(files)
    ds = nt + len(names) + (-(nt + len(names)) % 4)
    head = struct.pack("<4I", 1, len(files), nt + len(names), ds) + struct.pack("<I4H", 0, 1, 0, 0, len(files))
    recs, data, no = b"", b"", 2
    for n, d in files.items():
        recs += struct.pack("<3I", no, len(data), len(d))
        no += len(n) + 1
        data += d + b"\0" * (-len(d) % 4)
    return (head + recs + names).ljust(ds, b"\0") + data


def contents(d):
    ds, _, files = pak.parse(d)
    return {p: d[ds + o:ds + o + s] for p, o, s, _ in files}


def test_nested_edit():
    inner = make_pak({"c.txt": b"old text", "d.bin": b"keep"})
    outer = make_pak({"a.bin": b"abc", "b.zdv": zdv.deflate(inner), "e.zdv": zdv.deflate(b"raw", stored=True)})
    assert pak.repack(outer) == outer and pak.member(outer, "o.pak", {}, force=True) == outer
    new = pak.member(outer, "o.pak", {"b/c.txt": b"new, longer text", "a.bin": b"x", "e": b"stored!"})
    top = contents(new)
    assert top["a.bin"] == b"x" and zdv.is_stored(top["e.zdv"]) and zdv.inflate(top["e.zdv"]) == b"stored!"
    assert contents(zdv.inflate(top["b.zdv"])) == {"c.txt": b"new, longer text", "d.bin": b"keep"}
    with pytest.raises(KeyError):
        pak.member(outer, "o.pak", {"nope/x": b""})


@pytest.mark.skipif(not (ROOT / "rom").is_dir() or not any((ROOT / "rom").glob("*.iso")), reason="no ROM")
def test_eboot_copies():
    """gfx.eboot_copies recompresses a file into the EBOOT's own zdv slot: the slot inflates to the new bytes."""
    import gfx
    off, path = gfx.EBOOT_COPIES[0]
    u, cs = 0x200, 0x100
    d = bytearray(off + 16 + cs + 8)
    d[off:off + 16 + cs] = zdv.deflate(bytes(u)).ljust(16 + cs, b"\0")
    struct.pack_into("<I", d, off + 12, cs)
    new = b"MIG.00.1PSP" * 40
    gfx.eboot_copies(d, {path: new})
    assert zdv.inflate(bytes(d[off:off + 16 + cs])) == new and d[off + 16 + cs:] == bytes(8)


def test_identity_build(tmp_path):
    """Phase 3: rebuilding every nested pak and recompressing every zdv, with no edits, gives the original ISO."""
    import build
    assert build.build(tmp_path / "id.iso", force=True) == build.SHA1.lower()
