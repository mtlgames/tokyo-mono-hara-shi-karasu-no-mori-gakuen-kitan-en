"""widthgate.py: write the width-gate override file (build.py --qa) and print each test line's sysfont18 width.

    python -X utf8 tools/widthgate.py [OUT.tsv]     # default work/qa/widthgate.tsv

Each test fills a box variant to an exact pixel width with a ruler (`|` at both ends) so a zoomed shot shows the
last column that still draws. Results go in docs/re/engine.md §Width gate.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import insert  # noqa: E402

TORTURE = "".join(c for c in map(chr, range(0x21, 0x7F)) if c not in "{}" + insert.SCRIPT_BAD)  # {} = markup


def ruler(t, px, head=""):
    """head + digits up to px - width('|'), then '|' (exactly px when the font allows; else just under)."""
    s, k = "|" + head, 0
    while t.px(s + str(k % 10) + "|") <= px:
        s += str(k % 10)
        k += 1
    return s + "|"


def tests(t):
    return {
        # MS00_00 opening: caption, then 3-line boxes (speaker 図書館員)
        "ms00_00:000:00": ruler(t, insert.CAPTION_RIGHT, "cap336 "),
        "ms00_00:000:01": "\\n".join([TORTURE[:45], TORTURE[45:], "Wait!! What?! A-B=C~D.  Double  spaces."]),
        "ms00_00:000:03": "\\n".join([ruler(t, 464, "464 "), ruler(t, 472, "472 "), ruler(t, 480, "480 ")]),
        "図書館員": "WWWWWWWWWWWWWWWWW",  # NAME_MAX chars, widest glyph
    }


if __name__ == "__main__":
    t = insert.Text("en")
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else insert.ROOT / "work" / "qa" / "widthgate.tsv"
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = tests(t)
    out.write_text("".join(f"{k}\t{v}\n" for k, v in rows.items()), encoding="utf-8")
    for k, v in rows.items():
        print(k, [t.px(x) for x in v.split("\\n")], v[:60])
