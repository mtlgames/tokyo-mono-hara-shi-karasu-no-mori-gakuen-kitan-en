"""gfx_title.py: title screen atlas (pilot group). Writes gfx/out/title/*.png and gfx/title.tsv.

    python -X utf8 tools/gfx_title.py

Cells from title/title.pak/title/title.g2d (64x32 menu words, 160x48 subtitle); the logo 東京鬼祓師 stays (D5).
"""
import gfx
import typeset

PATH = "title/title.pak/title/tit01.gim"
BRUSH = "KaushanScript-Regular.ttf"
MENU = ["New Game", "Continue"]          # 初めから 続きから
SUB = "Strange Tales of\nKarasu no Mori Academy"   # 鴉乃杜學園奇譚


def main():
    img = gfx.original(PATH)
    rects = [(64 * i, y, 64, 32) for i in range(2) for y in (128, 160)] + [(224, 144, 160, 48)]
    for i, word in enumerate(MENU):
        # selected (orange glow, y 128) and normal (white, y 160) cells
        for y, fill, halo in ((128, (255, 190, 90, 255), (190, 70, 0, 150)), (160, (255, 255, 255, 255), None)):
            r = (64 * i, y, 64, 32)
            gfx.clear(img, r)
            t = typeset.text_image(64, 32, word, BRUSH, size=13, fill=fill,
                                   shadow=None if halo else (1, 1, (0, 0, 0, 200)))
            if halo:
                gfx.glow(img, r, t, halo, radius=1.5, strength=1)
            else:
                img.alpha_composite(t, r[:2])
    r = (224, 144, 160, 48)
    gfx.clear(img, r)
    img.alpha_composite(typeset.text_image(160, 48, SUB, BRUSH, size=15, fill=(255, 255, 255, 255),
                                           stroke=(1, (30, 20, 20, 255)), spacing=-2), r[:2])
    gfx.write_tsv("title", [(PATH, gfx.save(img, "title", PATH, rects), "menu words + subtitle; logo kept (D5)")])


if __name__ == "__main__":
    main()
