"""Bisect helper: build the English ISO with parts switched off, to find which part breaks a scene.

    python -X utf8 tools/debug/buildvar.py OUT.iso [--no-eboot-text] [--no-engine] [--qa F.tsv]

--no-eboot-text: EBOOT gets only the engine patch (no EBOOT strings, no pool moves).
--no-engine: EBOOT gets only the strings (the ADV drawer stays vertical).
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("out", type=Path)
ap.add_argument("--no-eboot-text", action="store_true")
ap.add_argument("--no-engine", action="store_true")
ap.add_argument("--no-font", action="store_true", help="fonts stay original (tools/fontpatch.py off)")
ap.add_argument("--only", help="regex: only ids matching it get English (speakers, tables, scripts, EBOOT)")
ap.add_argument("--qa")
a = ap.parse_args()


def eboot(text):
    import engine
    import insert
    from eboot import Patcher
    d = Patcher().d if a.no_engine else engine.patch(Patcher())
    return bytes(d if a.no_eboot_text else insert.eboot_patch(d, text, insert.scripts()))


def edits(text):
    import insert
    return insert.file_edits(text)


build.eboot = eboot
if a.only:
    import re
    import insert
    get = insert.Text.get
    insert.Text.get = lambda self, x, *r, **k: get(self, x, *r, **k) if re.search(a.only, x["id"]) else None
if a.no_font:
    build.edits = edits
print(a.out, build.build(a.out, qa=a.qa))
