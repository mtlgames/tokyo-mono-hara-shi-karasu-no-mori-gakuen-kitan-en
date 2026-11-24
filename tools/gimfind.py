"""gimfind.py: find every GIM in CROW.PAK that holds a copy of one cell of another GIM (by alpha, exact match).

    python -X utf8 tools/gimfind.py dungeon/ui/ui_dungeon.pak/dungeon/ui/dungeon03.gim 74,81,48,15

For "a frame still shows the Japanese label": the game ships the same label in other atlases with different bytes,
which gfx.py's same-bytes copy rule misses. Prints path and x,y of each hit (the source cell itself included).
"""
import argparse
import hashlib

import numpy as np

import gfx


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", help="unpacked GIM path, or a screenshot .png (with --lum)")
    ap.add_argument("--lum", type=int, default=170, help="screenshot: luminance above this counts as ink (negative: below -N, dark text)")
    ap.add_argument("rect", help="x,y,w,h")
    ap.add_argument("--match", type=float, default=1.0, help="share of equal alpha pixels for a hit (0.9: restyled copies)")
    a = ap.parse_args()
    x, y, w, h = map(int, a.rect.split(","))
    if a.path.endswith(".png"):   # a screenshot: bright pixels of the rect stand for the glyph's alpha
        from PIL import Image
        lum = np.array(Image.open(a.path).convert("L"))[y:y + h, x:x + w]
        want = lum < -a.lum if a.lum < 0 else lum > a.lum
    else:
        want = np.array(gfx.original(a.path))[y:y + h, x:x + w, 3] > 64
    assert want.sum() > 8, "cell is (almost) empty"
    by, data = gfx.gims()
    for md5, paths in by.items():
        try:
            rgba = np.array(gfx.decode(data[paths[0]]))
            al = rgba[:, :, 3] > 64
            if a.path.endswith(".png") and a.lum < 0:   # dark text may be baked into an opaque image
                al &= rgba[:, :, :3].mean(axis=2) < -a.lum
        except Exception:  # noqa: BLE001 - a few GIM formats gim.py can't decode; skip them
            continue
        H, W = al.shape
        if H < h or W < w:
            continue
        win = np.lib.stride_tricks.sliding_window_view(al, (h, w))
        hits = np.argwhere((win == want).mean(axis=(2, 3)) >= a.match)
        for yy, xx in hits[:4]:
            print(f"{', '.join(paths)}\t{xx},{yy}")


if __name__ == "__main__":
    main()
