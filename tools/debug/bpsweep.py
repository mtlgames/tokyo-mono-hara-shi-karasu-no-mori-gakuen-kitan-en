"""bpsweep.py: which warp states hit code breakpoints (e.g. who calls a drawer), one bplog run per state.

    python -X utf8 tools/debug/bpsweep.py ISO STATES_DIR ADDR [ADDR..] [--mash 120:-]

Prints `scene: hits` per state and the first logged hit; logs in work/qa/bpsweep/<scene>.txt.
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("iso"); ap.add_argument("states", type=Path); ap.add_argument("addrs", nargs="+")
    ap.add_argument("--mash", default="120:-")
    a = ap.parse_args()
    out = ROOT / "work" / "qa" / "bpsweep"
    out.mkdir(parents=True, exist_ok=True)
    for st in sorted(a.states.glob("*.ppst")):
        r = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "tools" / "debug" / "bplog.py"), a.iso,
                            "--out", str(out / st.stem), "--state", str(st), "--mash", a.mash, "--max", "3",
                            *a.addrs], capture_output=True, text=True)
        pcs = {f"pc={x.lower():0>8}" for x in a.addrs}  # bplog also logs the stop that a state load causes
        hits = [l for l in r.stdout.splitlines() if l.startswith("f") and l.split()[1] in pcs]
        (out / f"{st.stem}.txt").write_text(r.stdout + r.stderr, encoding="utf-8")
        print(f"{st.stem}: {len(hits)}" + (f"  {hits[0][:60]}" if hits else ""), flush=True)


if __name__ == "__main__":
    main()
