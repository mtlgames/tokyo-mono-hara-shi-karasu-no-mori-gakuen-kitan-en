"""tour_sheets.py: one contact sheet per scene of a warp tour, then the visual-QA manifest.

    python -X utf8 tools/tour_sheets.py [--tag en] [--build build/karasu_en.iso]

Reads work/qa/warp/<tag>/<scene>/f*.png (warp.py --all --tag <tag> --shot-every N), writes
work/qa/tour/<scene>_sheet.png (paged: _sheet_2.png ...) and runs `qa_gate.py init work/qa/manifest.tsv work/qa/tour
--build BUILD`, then `qa_gate.py todo` into work/qa/chunks (8 sheets per chunk).
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SCRIPTS  # noqa: E402

QA = ROOT / "work" / "qa"


def run(*args):
    subprocess.run([sys.executable, "-X", "utf8", *map(str, args)], check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tag", default="en")
    ap.add_argument("--build", default=str(ROOT / "build" / "karasu_en.iso"))
    a = ap.parse_args()
    out = QA / "tour"
    out.mkdir(parents=True, exist_ok=True)
    for scene in sorted(p for p in (QA / "warp" / a.tag).iterdir() if p.is_dir()):
        if any(scene.glob("f*.png")):
            run(Path(SCRIPTS) / "sheet.py", scene, "--out", out / f"{scene.name}_sheet.png")  # a dir: argv limit
    gate = Path(SCRIPTS) / "qa_gate.py"
    run(gate, "init", QA / "manifest.tsv", out, "--build", a.build)
    run(gate, "todo", QA / "manifest.tsv", QA / "verdicts", "--size", "8", "--out-dir", QA / "chunks")


if __name__ == "__main__":
    main()
