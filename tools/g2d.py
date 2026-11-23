"""g2d.py: list the sprite cells a .g2d layout cuts from its GIM atlases (where each label is drawn from).

    python -X utf8 tools/g2d.py work/unpacked/title/title.pak/title/title.g2d [--at X,Y]

Prints the texture names, then one line per sprite: texture-space rect u,v,w,h and its local quad x0,y0 (offset from
the sprite anchor). Records are found by shape (16-bit quad x0,y0,x1,y1 then u0,v0,u1,v1 with the same size), so a
cell is reported once per use. --at X,Y keeps only cells holding that texture pixel. shortcut: heuristic scan, not a
full parse of the G2D header; enough to size a redraw, verify one cell by eye when it looks odd.
"""
import argparse
import struct
from pathlib import Path


def textures(d):
    out, p = [], 0x24
    while p + 4 < len(d) and d[p:p + 1].isalpha():
        out.append(d[p:p + 28].split(b"\0")[0].decode("ascii", "replace"))
        p += 32
    return out


def cells(d, max_uv=1024):
    seen = []
    for p in range(0, len(d) - 16, 2):
        x0, y0, x1, y1, u0, v0, u1, v1 = struct.unpack_from("<8h", d, p)
        if (0 <= u0 < u1 < max_uv and 0 <= v0 < v1 < max_uv and x1 - x0 == u1 - u0 and y1 - y0 == v1 - v0
                and x0 <= 0 <= x1 and y0 <= 0 <= y1 and (u1 - u0) * (v1 - v0) >= 16):
            c = (u0, v0, u1 - u0 + 1, v1 - v0 + 1, x0, y0)
            if c not in seen:
                seen.append(c)
    return seen


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("g2d", type=Path)
    ap.add_argument("--at", help="X,Y: only cells containing this texture pixel")
    a = ap.parse_args()
    d = a.g2d.read_bytes()
    print("textures:", ", ".join(textures(d)))
    at = tuple(map(int, a.at.split(","))) if a.at else None
    for u, v, w, h, x0, y0 in cells(d):
        if at and not (u <= at[0] < u + w and v <= at[1] < v + h):
            continue
        print(f"{u},{v},{w},{h}\tquad at {x0},{y0}")


if __name__ == "__main__":
    main()
