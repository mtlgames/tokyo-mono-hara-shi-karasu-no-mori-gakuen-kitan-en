"""gfx_newdata.py: the save dialog's "new data" icon, system/newdataicon.png (144x80 PNG, not a GIM: the GIM survey
missed it; found in the stress_names save screen). 新規作成 / しんきさくせい -> "New Save" / "new save data".

    python -X utf8 tools/gfx_newdata.py     # writes gfx/out/newdata/newdataicon.png and gfx/newdata.tsv
"""
from pathlib import Path

from PIL import Image, ImageFilter

import gfx  # noqa: F401  (puts the skill's typeset.py on the path, fonts/ as its font dir)
import typeset

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "work" / "unpacked" / "system" / "newdataicon.png"
OUT = ROOT / "gfx" / "out" / "newdata" / "newdataicon.png"
BRUSH = "KaushanScript-Regular.ttf"


def main():
    img = Image.open(SRC).convert("RGBA")
    # erase only the white strokes (bright, unsaturated pixels in the text band, grown 2 px) with a min fill, so
    # the red card and the feathers stay
    mask = Image.new("L", img.size, 0)
    for y in range(20, 62):
        for x in range(10, 134):
            r, g, b, _ = img.getpixel((x, y))
            if min(r, g, b) > 70 and max(r, g, b) - min(r, g, b) < 60:
                mask.putpixel((x, y), 255)
    mask = mask.filter(ImageFilter.MaxFilter(5))
    fill = img.filter(ImageFilter.MinFilter(9)).filter(ImageFilter.GaussianBlur(2))
    img = Image.composite(fill, img, mask)
    img.alpha_composite(typeset.text_image(144, 34, "New Save", BRUSH, size=22,
                                           shadow=(1, 1, (0, 0, 0, 220))), (0, 14))
    img.alpha_composite(typeset.text_image(144, 16, "new save data", "serif", size=10,
                                           fill=(220, 220, 220, 255)), (0, 48))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(OUT, optimize=True)
    (ROOT / "gfx" / "newdata.tsv").write_text(
        "#path\tpng\tnote\nsystem/newdataicon.png\tgfx/out/newdata/newdataicon.png\tsave dialog new-data icon\n",
        encoding="utf-8")
    print(OUT, OUT.stat().st_size, "bytes (original", SRC.stat().st_size, ")")


if __name__ == "__main__":
    main()
