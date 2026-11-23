"""gimsheet.py: graphics-text survey sheets. Decodes every unique GIM under a folder into numbered contact sheets.

    python -X utf8 tools/gimsheet.py SRC_DIR OUT_DIR [--prefix adv/bg] [--max 256] [--page 1600x1200]
Writes OUT_DIR/<tag>_NN.png and OUT_DIR/<tag>.tsv (cell number, sheet, md5, path, w, h). Duplicates (same md5) are
listed once; every GIM that fails to decode is printed (never dropped silently).
"""
import argparse
import hashlib
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from skill import SCRIPTS  # noqa: E402

sys.path.insert(0, SCRIPTS)
import gim  # noqa: E402


def decode(path):
    d = Path(path).read_bytes()
    im = gim.parse(d)[0]
    w, h, rows = gim.to_rgba(d, im)
    return Image.frombytes("RGBA", (w, h), b"".join(rows))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--prefix", default="", help="only paths under SRC/PREFIX")
    ap.add_argument("--max", type=int, default=256, help="longest side of a thumbnail")
    ap.add_argument("--page", default="1600x1200")
    ap.add_argument("--tag", default=None)
    a = ap.parse_args()
    pw, ph = map(int, a.page.split("x"))
    root = Path(a.src)
    base = root / a.prefix if a.prefix else root
    tag = a.tag or (a.prefix.replace("/", "_").replace(".", "") or "all")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    seen, cells = set(), []
    for p in sorted(base.rglob("*.gim")):
        md5 = hashlib.md5(p.read_bytes()).hexdigest()
        if md5 in seen:
            continue
        seen.add(md5)
        try:
            img = decode(p)
        except Exception as e:  # noqa: BLE001
            print(f"SKIP {p}: {e}")
            continue
        w, h = img.size
        s = min(1.0, a.max / max(w, h))
        t = img.resize((max(1, int(w * s)), max(1, int(h * s))), Image.LANCZOS) if s < 1 else img
        cells.append((p.relative_to(root).as_posix(), md5, w, h, t))
    rows, x, y, rh, page, sheets = [], 0, 0, 0, [], []
    for n, (path, md5, w, h, t) in enumerate(cells):
        cw, chh = t.width + 4, t.height + 14
        if x + cw > pw:
            x, y, rh = 0, y + rh, 0
        if y + chh > ph and page:
            sheets.append(page)
            page, x, y, rh = [], 0, 0, 0
        page.append((n, x, y, t))
        rows.append((n, len(sheets), md5, path, w, h))
        x += cw
        rh = max(rh, chh)
    if page:
        sheets.append(page)
    for i, page in enumerate(sheets):
        im = Image.new("RGBA", (pw, ph), (60, 60, 100, 255))
        dr = ImageDraw.Draw(im)
        for n, x, y, t in page:
            bg = Image.new("RGBA", t.size, (60, 60, 100, 255))
            bg.alpha_composite(t)
            im.paste(bg, (x, y + 12))
            dr.text((x, y), str(n), fill=(255, 255, 0, 255))
        im.convert("RGB").save(out / f"{tag}_{i:02d}.png")
    with open(out / f"{tag}.tsv", "w", encoding="utf-8") as f:
        for r in rows:
            f.write("\t".join(map(str, r)) + "\n")
    print(f"{tag}: {len(cells)} unique GIMs on {len(sheets)} sheets")


if __name__ == "__main__":
    main()
