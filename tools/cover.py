"""Text coverage at script level (PPSSPP has no Lua: the warp's trace_pw breakpoints log each .pwx the game loads).

    python -X utf8 tools/cover.py logs work/qa/tour_en.log [more.log ..]   # warp stdout -> work/qa/cover/<log>/log.txt
    python -X utf8 tools/cover.py sweep build/karasu_en.iso [--jobs 3]     # warp into every script no log reached
    python -X utf8 tools/cover.py report                                    # textcover.py; exit 1 while any is unshown

A "string" here is one .pwx script with English text (id = its load name, e.g. MS05_00): reached = the game loaded
it (a warp's "warp: ... -> NAME" line or a trace "load NAME" line). Tables and EBOOT strings are loaded whole at boot,
so their per-string reads are not logged (waived as groups in docs/text_unshown.tsv; the menu tours show them).
The sweep warps into each unreached script (cold boot, mash circle 900 frames) and keeps its exit code in
work/qa/cover/sweep.tsv: a non-zero exit there is a crash/blank-screen lead, not only a coverage gap.
"""
import argparse, json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SCRIPTS  # noqa: E402

COVER = ROOT / "work" / "qa" / "cover"
STRINGS = COVER / "strings.tsv"
WAIVE = ROOT / "docs" / "text_unshown.tsv"
LOADED = re.compile(r"(?:load|warp: ADV params at \w+ ->) ([A-Z]+\d\d_\d+)")


def scripts():
    """Load names of every .pwx with at least one English entry, in a fixed order."""
    out = []
    for p in sorted((ROOT / "script" / "pw").glob("*/*.json")):
        if any(e.get("en") for e in json.loads(p.read_text(encoding="utf-8"))):
            out.append(p.stem.upper())
    return out


def write_strings():
    COVER.mkdir(parents=True, exist_ok=True)
    names = scripts()
    STRINGS.write_text("".join(f"{n}\t{i:x}\n" for i, n in enumerate(names)), encoding="utf-8")
    return {n: i for i, n in enumerate(names)}


def to_log(raw, out_dir, index):
    """warp/trace stdout -> out_dir/log.txt with one TEXT line per script it loaded."""
    seen = {m for m in LOADED.findall(Path(raw).read_text(encoding="utf-8", errors="replace")) if m in index}
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "log.txt").write_text("".join(f"TEXT {index[n]:x}\n" for n in sorted(seen)), encoding="utf-8")
    return seen


def seen_all(index):
    out = set()
    for log in COVER.glob("**/log.txt"):
        out |= {int(a, 16) for a in re.findall(r"^TEXT (\w+)", log.read_text(encoding="utf-8"), re.M)}
    return {n for n, i in index.items() if i in out}


def sweep_one(iso, name, index):
    d = COVER / "sweep" / name
    d.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, "-X", "utf8", "-c",
           "import sys; sys.path.insert(0, sys.argv[1]); import warp; warp.TAG = 'cover'; import os; "
           "os.makedirs(os.path.dirname(warp.state_path('x')), exist_ok=True); "
           "sys.exit(warp.run_scene(sys.argv[2], sys.argv[3], f'script={sys.argv[3]} mash=900:circle', sys.argv[4]))",
           str(ROOT / "tools" / "debug"), str(iso), name, str(d)]
    try:
        with open(d / "raw.log", "w", encoding="utf-8") as f:
            code = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, timeout=900).returncode
    except subprocess.TimeoutExpired:
        code = 124
    to_log(d / "raw.log", d, index)
    return name, code


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["logs", "sweep", "report"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--jobs", type=int, default=3)
    a = ap.parse_args()
    index = write_strings()
    if a.cmd == "logs":
        for raw in a.args:
            print(raw, len(to_log(raw, COVER / Path(raw).stem, index)), "scripts")
    elif a.cmd == "sweep":
        todo = [n for n in index if n not in seen_all(index)]
        print(f"{len(todo)} of {len(index)} scripts unreached; sweeping", flush=True)
        with ThreadPoolExecutor(a.jobs) as ex, open(COVER / "sweep.tsv", "a", encoding="utf-8") as tsv:
            for name, code in ex.map(lambda n: sweep_one(a.args[0], n, index), todo):
                print(name, code, flush=True); tsv.write(f"{name}\t{code}\n"); tsv.flush()
    else:
        sys.exit(subprocess.run([sys.executable, "-X", "utf8", str(Path(SCRIPTS) / "textcover.py"), str(COVER),
                                 str(STRINGS), "--waive", str(WAIVE)]).returncode)


if __name__ == "__main__":
    main()
