"""QA-only build whose dungeons start in a chosen room: rewrites `startfloor` (and optionally `startpos`) in
dungeon/<section>.ini, so a dun_area warp (scenes dun_bg04/07/11) lands in a deep room (.znt texture checks).

    python -X utf8 tools/debug/startroom.py bg11_00=waginoma bg07_00=seihennoma[:ichidake_door01_] [--out ISO]
    python -X utf8 tools/debug/warp.py build/karasu_room.iso dun_bg11 --tag room

Never ship this build: it changes game data.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import build  # noqa: E402


def ini_edit(section, floor, pos=None):
    key = f"dungeon/{section}.pak/dungeon/{section}.ini"
    d = (ROOT / "work" / "unpacked" / key).read_bytes()
    if not re.search(rb"\nname\s*=\s*" + re.escape(floor.encode()) + rb"\b", d):
        sys.exit(f"{section}: no floor {floor}")
    d, n = re.subn(rb"(startfloor\s*=\s*)\S+", rb"\g<1>" + floor.encode(), d, count=1)
    if pos:
        d, m = re.subn(rb"(startpos\s*=\s*)\S+", rb"\g<1>" + pos.encode(), d, count=1)
        n &= m
    if n != 1:
        sys.exit(f"{section}: startfloor/startpos line not found")
    return key, d


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rooms", nargs="+", help="section=floor[:startpos]")
    ap.add_argument("--out", type=Path, default=ROOT / "build" / "karasu_room.iso")
    a = ap.parse_args()
    extra = {}
    for r in a.rooms:
        section, rest = r.split("=", 1)
        floor, _, pos = rest.partition(":")
        k, d = ini_edit(section, floor, pos or None)
        extra[k] = d
    print(f"{a.out} sha1 {build.build(a.out, extra=extra)}")


if __name__ == "__main__":
    main()
