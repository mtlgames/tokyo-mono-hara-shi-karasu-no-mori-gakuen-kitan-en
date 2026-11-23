"""Width/buffer probe for fit-queue columns: write a --qa TSV that fills every row of the given table columns to N bytes.

    python -X utf8 tools/fitprobe.py item:04=32 item:10=40 hanafuda:04=28 hanafuda:08=14 > work/qa/fit.tsv
    python -X utf8 build.py --qa work/qa/fit.tsv --out build/karasu_fit.iso
    python -X utf8 tools/debug/warp.py build/karasu_fit.iso menu_item --tag fit

Each string is `#<row>` then a ruler of digits (`0123456789` repeated), so a shot shows how many bytes draw and a
crash shows the buffer is smaller. Rows whose original is empty are skipped (the game never shows them).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def fill(row, n):
    s = f"#{row}:"
    return (s + "0123456789" * 20)[:n]


def main(args):
    for spec in args:
        col, n = spec.split("=")
        stem, c = col.split(":")
        for e in json.loads((ROOT / "script/tables" / f"{stem}.json").read_text(encoding="utf-8")):
            _, row, ec = e["id"].split(":")
            if ec == c and e["jp"]:
                print(f"{e['id']}\t{fill(row, int(n))}")


if __name__ == "__main__":
    assert fill("0001", 8) == "#0001:01" and len(fill("1", 40)) == 40
    main(sys.argv[1:])
