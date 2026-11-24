"""gfx_adv_ui.py: adventure-part UI atlases. Writes gfx/out/adv_ui/*.png and gfx/adv_ui.tsv.

    python -X utf8 tools/gfx_adv_ui.py

Rows: ui_scene02 (31 speaker/place name plates, 80x16 / 128x16 / 48x16 cells), ui_tansaku01 (探索中 banner; the
GIM is shared by adv/ui_scene.pak and adv/freemove/ui_lsmap.pak, the build writes every copy), adv_emotion (8 emotion
words, 32x32 cells), adv_talk01 (次へ 速度 自動). Not rows: ui_lsmap07 (map-pin icons, no text) and ui_lsmap01 (same
GIM bytes as system/_ui_map.pak/adv/freemove/ui_lsmap01.gim, which gfx/menus.tsv already writes). `paint` comes from
gfx_phone.py.
"""
import gfx
import typeset
from gfx_phone import paint, SANS, SANSB, SERIF

SERIFB = "LiberationSerif-Bold.ttf"
BRUSH = "KaushanScript-Regular.ttf"
BLACK = (0, 0, 0, 255)

COL1 = ["Zero Chiaki", "Ichiru Muto", "Toji Dan", "Minori Hosaka", "Nagahide Shishido", "Tomoe Tobisaka",
        "Shu Takarakata", "Gio Onimaru", "Migiri Kashima", "Angie D.", "Kaname Kotokuji", "Dokai Gamo", "Hideo Kamon",
        "Ayahito Konosu", "Rin Himukai", "Benio Sawakami"]                      # x 0, 80x16 cells, row i at y 16 i
COL3 = ["Mao", "Ken", "Suzu", "Asako Hatori", "Seishiro Hatori", "Daisuke Isachi", "Nobuyuki Chikushi",
        "Hisae Makimura", "Hanako Togashi", "Gengo Shibukawa", "Kalpataru T. Shankar", "Banri Takadono", None,
        "Buy Goods", "School Store", "Buy Toys"]                               # x 128, 128x16 cells
MID = {1: "Exit", 2: "Shelf"}                                                  # x 80, 48x16 cells; row 0 is "???"
NAME_SIZE = 11


def ui_scene02():
    path = "adv/ui_scene.pak/adv/ui_scene02.gim"
    img, rects = gfx.original(path), []
    cells = [(0, 16 * i, 80, 16, t) for i, t in enumerate(COL1)] + [(128, 16 * i, 128, 16, t) for i, t in
                                                                      enumerate(COL3) if t]
    cells += [(80, 16 * i, 48, 16, t) for i, t in MID.items()]
    for x, y, w, h, text in cells:
        f = typeset.font(SERIF, NAME_SIZE).getlength(text)
        paint(img, rects, (x, y, w, h), text, SERIF, NAME_SIZE, halo=BLACK, radius=0.8, strength=3, align="c", pad=0,
              xs=min(1.0, (w - 4) / f))
    gfx.clear(img, (128, 192, 128, 1))                 # last glow row of 楼 万黎 spills one pixel below its cell
    rects.append((128, 192, 128, 1))
    return path, img, rects, "name plates / place labels (Mao, Ken, Suzu are the names); ??? kept"


def ui_tansaku01():
    path = "adv/ui_scene.pak/adv/ui_tansaku01.gim"
    img, rects = gfx.original(path), []
    cell = (0, 0, 128, 48)
    paint(img, rects, cell, "Exploring", BRUSH, 30, fill=BLACK, halo=(255, 255, 255, 255), radius=1.5, strength=3,
          align="c", pad=0)
    return path, img, rects, "Exploring banner (same GIM under adv/freemove/ui_lsmap.pak)"


def adv_emotion():
    path = "adv/talk/adv_emotion.pak/adv/talk/adv_emotion.gim"
    img, rects = gfx.original(path), []
    # the wheel's middle row is Sorrow Worry <centre> Friend Passion, diamonds 24 px apart: short words there
    # (悲 Sad, 燃 Fire as on the quest_site wheel) pushed away from their neighbour (align), so no two touch
    words = [(0, 0, "Joy", "c"), (32, 0, "Friend", "l"), (65, 0, "Dislike", "c"), (96, 0, "Worry", "r"),
             (1, 32, "Love", "c"), (33, 32, "Fire", "r"), (65, 32, "Anger", "c"), (96, 32, "Sad", "l")]
    gfx.clear(img, (0, 0, 128, 64))
    rects.append((0, 0, 128, 64))
    for x, y, text, al in words:
        f = typeset.font(SERIFB, 11).getlength(text)
        paint(img, rects, (x + 1, y + 6, 30, 18), text, SERIFB, 11, align=al, pad=0, clear=False, xs=min(1.0, 27 / f))
    return path, img, rects, "eight emotion words"


def adv_talk01():
    path = "adv/talk/adv_talk.pak/adv/talk/adv_talk01.gim"
    img, rects = gfx.original(path), []
    paint(img, rects, (0, 0, 32, 16), "Next", SANS, 12, align="c", pad=0)
    paint(img, rects, (32, 0, 32, 18), "Speed", SANSB, 11, halo=BLACK, radius=1, strength=3, align="c", pad=0,
          xs=0.9)
    paint(img, rects, (0, 16, 31, 17), "Auto", SANSB, 12, halo=BLACK, radius=1, strength=3, align="c", pad=0)
    return path, img, rects, "Next / Speed / Auto"


ROWS = [ui_scene02, ui_tansaku01, adv_emotion, adv_talk01]


def main():
    rows = []
    for fn in ROWS:
        path, img, rects, note = fn()
        rows.append((path, gfx.save(img, "adv_ui", path, rects), note))
    gfx.write_tsv("adv_ui", rows)


if __name__ == "__main__":
    main()
