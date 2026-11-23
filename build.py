"""build.py: original ISO -> build/karasu_en.iso.

    python -X utf8 build.py              # build; prints the output sha1 (equal to the original while nothing is edited)
    python -X utf8 build.py --marker     # every string -> #n marker (build/karasu_marker.iso, work/marker_ids.tsv)
    python -X utf8 build.py --identity   # rebuild every nested pak and recompress every .zdv with no edits; exit 1
                                         # unless the ISO is byte-identical to the original (phase 3 test)

Steps: check the dump against rom.sha1, rebuild CROW.PAK with the edits (pak.editor), patch it into a copy of the ISO.
"""
import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
import check_rom  # noqa: E402
import iso9660  # noqa: E402
from pak import Pak, editor  # noqa: E402

SHA1, ISO_NAME = next(l for l in (ROOT / "rom.sha1").read_text(encoding="utf-8").splitlines()
                      if l.strip() and not l.startswith("#")).split(None, 1)
ISO = ROOT / ISO_NAME.strip().lstrip("*")
OUT = ROOT / "build" / "karasu_en.iso"
CROW = "/PSP_GAME/USRDIR/CROW.PAK"
EBOOT = "/PSP_GAME/SYSDIR/EBOOT.BIN"


def edits(text):
    """{unpacked CROW.PAK path: new payload}: the fonts (tools/fontpatch.py), the text (tools/insert.py) and the
    English graphics (tools/gfx.py, gfx/*.tsv)."""
    import fontpatch
    import gfx
    import insert
    from source import members
    out = {p: fontpatch.patch(d) for p, d in members(*fontpatch.FONTS)}
    out.update(insert.file_edits(text))
    if text.mode == "en":
        out.update(gfx.edits())
    return out


def crow_pak(iso=ISO):
    with open(iso, "rb") as f:
        lba, size = next((lba, ln) for p, lba, ln, _ in iso9660.listing(f) if p == CROW)
    return Pak(iso, lba * 2048, size)


def sha1(path):
    with open(path, "rb") as f:
        return hashlib.file_digest(f, "sha1").hexdigest()


def eboot(text):
    """Patched EBOOT: the engine changes (tools/engine.py) and EBOOT strings in the decrypted ELF. shortcut: ships the
    plain ELF, which only PPSSPP boots; re-sign it into a ~PSP EBOOT before release (docs/status.md)."""
    import engine
    import insert
    from eboot import Patcher
    return bytes(insert.eboot_patch(engine.patch(Patcher()), text, insert.scripts()))


def read_qa(path):
    """--qa FILE: `id<TAB>text` lines (\\n = line break) overriding single strings, for width tests."""
    if not path:
        return {}
    rows = (l.split("\t", 1) for l in Path(path).read_text(encoding="utf-8").splitlines() if l and l[0] != "#")
    return {i: t.replace("\\n", "\n") for i, t in rows}


def build(out=OUT, force=False, mode="en", qa=None):
    import insert
    check_rom.check()
    out.parent.mkdir(parents=True, exist_ok=True)
    text = insert.Text(mode, read_qa(qa))
    pak = crow_pak()
    tmp = out.with_name(out.stem + ".CROW.PAK")
    pak.rebuild(tmp, editor(pak, {} if force else edits(text), force))
    files = {CROW: tmp.read_bytes()}
    if not force:
        files[EBOOT] = eboot(text)
    text.save_ids()
    iso9660.patch(str(ISO), str(out), files)
    tmp.unlink()
    return sha1(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--identity", action="store_true")
    ap.add_argument("--marker", action="store_true", help="every string -> #n + filler (work/marker_ids.tsv)")
    ap.add_argument("--long", action="store_true", help="marker build with full-length table/EBOOT strings (widths)")
    ap.add_argument("--qa", help="TSV of id<TAB>text overrides (width tests); \\n = line break")
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args()
    mode = "long" if a.long else "marker" if a.marker else "en"
    a.out = a.out or (OUT if mode == "en" else OUT.with_name(f"karasu_{mode}.iso"))
    h = build(a.out, a.identity, mode, a.qa)
    same = h == SHA1.lower()
    print(f"{a.out} sha1 {h}" + (" (identical to the original)" if same else ""))
    if a.identity and not same:
        sys.exit("identity build differs from the original ISO")
