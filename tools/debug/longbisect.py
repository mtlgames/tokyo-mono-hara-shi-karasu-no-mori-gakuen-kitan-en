"""longbisect.py: find which long table string crashes a scene in the long build (build.py --long).

Builds build/bis.iso in long mode with only some tables (or, with --stem, some entries of one table) long, the
rest as in the marker build, warps SCENE and halves the set until one is left (assumes a single culprit).

    python -X utf8 tools/debug/longbisect.py field_ch01                  # which table
    python -X utf8 tools/debug/longbisect.py field_ch01 --stem systemtext # which entry of it
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import insert  # noqa: E402

OUT = ROOT / "build" / "bis.iso"


def crashes(scene, keep):
    """Build with only entries whose table stem or id is in keep long; True if the warp fails."""
    orig = insert.Text._get

    def _get(self, x, kind, room=None):
        if self.mode == "long" and kind == "table" and not ({x["id"], x["id"].split(":")[0]} & keep):
            self.mode = "marker"
            try:
                return orig(self, x, kind, room)
            finally:
                self.mode = "long"
        return orig(self, x, kind, room)
    insert.Text._get = _get
    try:
        build.build(OUT, False, "long")
    finally:
        insert.Text._get = orig
    r = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "tools" / "debug" / "warp.py"), str(OUT), scene,
                        "--tag", "bis"], capture_output=True)
    return r.returncode != 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scene"); ap.add_argument("--stem")
    a = ap.parse_args()
    sc = insert.scripts()
    cur = ([x["id"] for x in sc[f"tables/{a.stem}.json"]] if a.stem
           else [p[7:-5] for p in sc if p.startswith("tables/")])
    while len(cur) > 1:
        half = cur[:len(cur) // 2]
        bad = crashes(a.scene, set(half))
        print(("crash: " if bad else "ok: ") + f"{half[0]}..+{len(half)}", flush=True)
        cur = half if bad else cur[len(half):]
    print("culprit:", cur[0])


if __name__ == "__main__":
    main()
