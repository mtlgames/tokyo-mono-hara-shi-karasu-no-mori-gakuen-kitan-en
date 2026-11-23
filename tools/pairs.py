"""Reviewer pairs file from translated batches (docs/reviewer-brief.md).

    python -X utf8 tools/pairs.py OUT.txt b074 b075 ...

Each entry, in batch (story) order: `>> id | speaker | form`, then `JP: ...` and `EN: ...`.
"""
import csv
import sys
from pathlib import Path

TL = Path(__file__).resolve().parent.parent / "work" / "tl"


def rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE))


def pairs(batch):
    en = {r[0]: r[1] for r in rows(TL / f"{batch}.out.tsv") if len(r) >= 2}
    for r in rows(TL / f"{batch}.tsv"):
        if r:
            yield f">> {r[0]} | {r[1]} | {r[2]}\nJP: {r[4]}\nEN: {en.get(r[0], '<missing>')}\n"


def main(argv):
    out, batches = Path(argv[0]), argv[1:]
    out.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(f"## {b}\n" + "".join(pairs(b)) for b in batches)
    out.write_text(text, encoding="utf-8")
    print(out, text.count("\n>> "), "entries")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
