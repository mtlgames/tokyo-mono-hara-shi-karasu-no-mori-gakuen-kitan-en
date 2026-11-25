"""Polish pass over docs/polish.md: split unticked lines into chunks for agents, tick them from their verdicts.

    python -X utf8 tools/polish.py split N       work/polish/cNN.txt: `LINENO<TAB>line` per unticked line, N chunks
    python -X utf8 tools/polish.py apply [F..]   tick each `LINENO<TAB>fixed: ...|waived: ...` row (default: every
                                                 work/polish/*.ticks.tsv); the line must still be unticked
    python -X utf8 tools/polish.py count         unticked lines left
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLISH = ROOT / "docs/polish.md"
WORK = ROOT / "work/polish"
OPEN = "- [ ] "


def lines():
    return POLISH.read_text(encoding="utf-8").split("\n")


def split(n):
    todo = [(i + 1, s) for i, s in enumerate(lines()) if s.startswith(OPEN)]
    WORK.mkdir(parents=True, exist_ok=True)
    size = -(-len(todo) // n)
    for k in range(n):
        part = todo[k * size:(k + 1) * size]
        if part:
            (WORK / f"c{k + 1:02d}.txt").write_text("".join(f"{i}\t{s}\n" for i, s in part), encoding="utf-8")
    print(f"{len(todo)} unticked lines in {n} chunks of <= {size} in {WORK}")


def apply(files):
    text = lines()
    done = bad = 0
    for f in files or sorted(WORK.glob("*.ticks.tsv")):
        for row in Path(f).read_text(encoding="utf-8").splitlines():
            if not row.strip():
                continue
            num, note = row.split("\t", 1)
            i = int(num) - 1
            note = note.strip()
            if not (note.startswith("fixed") or note.startswith("waived")):
                print(f"{f}: line {num}: verdict must start fixed/waived: {note!r}")
                bad += 1
            elif not text[i].startswith(OPEN):
                if not text[i].startswith("- [x] "):
                    print(f"{f}: line {num} is not a polish line: {text[i][:60]!r}")
                    bad += 1
            else:
                text[i] = "- [x] " + text[i][len(OPEN):] + f" [{note}]"
                done += 1
    POLISH.write_text("\n".join(text), encoding="utf-8", newline="\n")
    print(f"ticked {done}, {bad} bad rows, {sum(s.startswith(OPEN) for s in text)} unticked left")
    return 1 if bad else 0


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        sys.exit(__doc__)
    if argv[0] == "split":
        return split(int(argv[1]))
    if argv[0] == "apply":
        return apply(argv[1:])
    if argv[0] == "count":
        left = sum(s.startswith(OPEN) for s in lines())
        print(left, "unticked")
        return 1 if left else 0
    sys.exit(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
