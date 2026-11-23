"""Phase 6 wave bookkeeping: a group = 5 consecutive batches named by its first (g074 = b074-b078).

    python -X utf8 tools/wave.py done g074 [g079 ...]   merge the group's batches, write work/tl/review/<g>.txt
    python -X utf8 tools/wave.py minors                 append every review's Minor lines to docs/polish.md (once each)
    python -X utf8 tools/wave.py terms                  NEW TERM lines from all translator reports, deduplicated
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TL = ROOT / "work" / "tl"
LAST = 308


def batches(group):
    n = int(group[1:])
    return [f"b{i:03d}" for i in range(n, min(n + 5, LAST + 1))]


def done(group):
    bs = batches(group)
    r = subprocess.run([sys.executable, "-X", "utf8", "tools/batches.py", "merge", *bs, "--partial"],
                       cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    (TL / f"merge_{group}.log").write_text(r.stdout + r.stderr, encoding="utf-8")
    ok = sum(line.endswith(": OK") for line in r.stdout.splitlines())
    subprocess.run([sys.executable, "-X", "utf8", "tools/pairs.py", f"work/tl/review/{group}.txt", *bs], cwd=ROOT,
                   capture_output=True)
    print(f"{group}: merge exit {r.returncode}, {ok}/{len(bs)} OK")


def minors():
    polish = ROOT / "docs" / "polish.md"
    have = polish.read_text(encoding="utf-8")
    add = []
    for rep in sorted((TL / "review").glob("g*.md")):
        if f"<!-- {rep.stem} -->" in have:
            continue
        sec = re.search(r"### Minor\n(.*?)(?=\n### |\Z)", rep.read_text(encoding="utf-8"), re.S)
        lines = [l[2:].strip() for l in (sec.group(1) if sec else "").splitlines() if l.startswith("- ")]
        lines = [l for l in lines if l.lower() not in ("none", "none.")]
        add.append(f"\n<!-- {rep.stem} -->\n" + "".join(f"- [ ] {l}\n" for l in lines))
    polish.write_text(have.rstrip("\n") + "\n" + "".join(add), encoding="utf-8")
    print(len(add), "reviews added")


def terms():
    seen = {}
    for rep in sorted(TL.glob("b*.report.txt")):
        for m in re.finditer(r"NEW TERM:\s*(.+?)\s*->\s*(.+)", rep.read_text(encoding="utf-8")):
            seen.setdefault(m.group(1), set()).add(m.group(2).strip())
    for jp, ens in sorted(seen.items()):
        print(f"{jp}\t{' | '.join(sorted(ens))}")


def main(argv):
    cmd = argv[0] if argv else ""
    if cmd == "done":
        for g in argv[1:]:
            done(g)
    elif cmd == "minors":
        minors()
    elif cmd == "terms":
        terms()
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
