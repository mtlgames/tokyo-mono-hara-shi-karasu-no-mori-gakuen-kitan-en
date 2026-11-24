"""gfx_menus.py: system menu atlases (group menus). Writes gfx/out/menus/*.png and gfx/menus.tsv.

    python -X utf8 tools/gfx_menus.py

Rows are in work/gfx/menus.txt; every label is drawn inside the box that held the Japanese (`Atlas.put`), the
rects it touched are handed to gfx.save, which fails on any pixel changed outside them.
"""
import gfx
import typeset
from PIL import Image

GROUP = "menus"
WHITE = (255, 255, 255, 255)
SOFT = (232, 232, 232, 255)
BLACK = (0, 0, 0, 255)
PANEL = (0, 0, 0, 153)             # flat translucent black of the status panels
notes = []                         # (path, text) labels that needed more squeeze than the brief allows


class Atlas:
    def __init__(self, path):
        self.path, self.img, self.rects = path, gfx.original(path), []

    def put(self, box, text, font="sans-b", size=12, fill=WHITE, bg=None, align="l", valign="m", xscale=None,
            stroke=None, shadow=None, spacing=0, tracking=0, min_x=0.7):
        """Replace the Japanese in box (x, y, w, h) by text. bg: None = make the box transparent, 'panel' = grey/white
        text pixels become the translucent panel colour (borders stay), 'inpaint' = diffuse the surroundings (text over
        art), an RGBA = flat paint. xscale None squeezes only as far as needed to fit."""
        x, y, w, h = box
        self.rects.append(box)
        if bg == "inpaint":
            self.img.paste(typeset.inpaint(self.img, (x, y, x + w, y + h)), (0, 0))
        elif bg == "panel":
            px = self.img.load()
            for yy in range(y, y + h):
                for xx in range(x, x + w):
                    r, g, b, al = px[xx, yy]
                    if al and (r, g, b, al) != PANEL and abs(r - g) < 12 and abs(g - b) < 12:
                        px[xx, yy] = PANEL
        elif bg == "black":     # neutral grey/white glyph pixels on a black tile -> black
            px = self.img.load()
            for yy in range(y, y + h):
                for xx in range(x, x + w):
                    r, g, b, al = px[xx, yy]
                    if al and abs(r - g) < 14 and abs(g - b) < 14 and r > 30:
                        px[xx, yy] = BLACK
        elif bg == "keep":
            pass
        elif bg is None:
            gfx.clear(self.img, box)
        else:
            self.img.paste(bg, (x, y, x + w, y + h))
        if not text:
            return
        f = typeset.font(font, size)
        sw = stroke[0] if stroke else 0
        tw = max(f.getlength(t) for t in text.split("\n")) + 2 * sw + (abs(shadow[0]) if shadow else 0)
        xscale = min(1.0 if xscale is None else xscale, (w - 6) / tw)   # squeeze to fit; the layer carries 4px of margin
        if xscale < min_x:
            notes.append((self.path, f"{text!r} xscale {xscale:.2f} in {w}px"))
        t = typeset.text_image(w, h, text, font, size=size, fill=fill, stroke=stroke, shadow=shadow, xscale=xscale,
                               align=align, valign=valign, spacing=spacing, tracking=tracking, pad=1)
        self.img.alpha_composite(t, (x, y))

    def stack(self, cells, text, font="impact", size=12, fill=WHITE, span=None, align="c", min_x=0.7, dx=0):
        """Vertical tab label: the game stacks the atlas cells (u, v, w, h[, x offset]) top to bottom, so one English
        word is drawn rotated (reads downwards) over their combined height and sliced back into the cells. span = (top,
        length) restricts the lettering to part of the stack (the rest stays transparent); text '' blanks the cells."""
        W = max((c[4] if len(c) > 4 else 0) + c[2] for c in cells)
        L = sum(c[3] for c in cells)
        canvas = Image.new("RGBA", (W, L), (0, 0, 0, 0))
        if text:
            top, length = span or (0, L)
            f = typeset.font(font, size)
            xs = min(1.0, (length - 4) / f.getlength(text))
            if xs < min_x:
                notes.append((self.path, f"{text!r} xscale {xs:.2f} in {length}px"))
            t = typeset.text_image(length, W, text, font, size=size, fill=fill, xscale=xs, align=align, pad=0)
            canvas.alpha_composite(t.rotate(-90, expand=True), (dx, top))
        y = 0
        for c in cells:
            u, v, w, h = c[:4]
            ox = c[4] if len(c) > 4 else 0
            self.rects.append((u, v, w, h))
            gfx.clear(self.img, (u, v, w, h))
            self.img.paste(canvas.crop((ox, y, ox + w, y + h)), (u, v))
            y += h

    def glow(self, box, text, rotate=False, font="sans-b", size=15, halo=(255, 153, 0, 255), radius=2, strength=0.8,
             fill=WHITE, min_x=0.7, margin=10, crisp=False):
        """Lettering with a soft coloured halo (orange map labels); rotate = reads downwards in a tall cell; crisp =
        hard-edged white letters (small text on a 16-colour palette, where grey edges snap to the halo colour)."""
        x, y, w, h = box
        self.rects.append(box)
        gfx.clear(self.img, box)
        L, Wd = (h, w) if rotate else (w, h)
        f = typeset.font(font, size)
        xs = min(1.0, (L - margin) / f.getlength(text))
        if xs < min_x:
            notes.append((self.path, f"{text!r} xscale {xs:.2f} in {L}px"))
        t = typeset.text_image(L, Wd, text, font, size=size, fill=fill, xscale=xs, pad=0)
        if crisp:
            t.putalpha(t.split()[3].point(lambda v: 255 if v > 100 else 0))
        gfx.glow(self.img, box, t.rotate(-90, expand=True) if rotate else t, halo, radius=radius, strength=strength)

    def hstack(self, cells, text, **kw):
        """Several (u, v, w, h) cells the game lays side by side: draw one word across them, slice it back."""
        W, H = sum(c[2] for c in cells), max(c[3] for c in cells)
        canvas = Atlas.__new__(Atlas)
        canvas.path, canvas.img, canvas.rects = self.path, Image.new("RGBA", (W, H), (0, 0, 0, 0)), []
        canvas.put((0, 0, W, H), text, bg="keep", **kw)
        x = 0
        for u, v, w, h in cells:
            self.rects.append((u, v, w, h))
            gfx.clear(self.img, (u, v, w, h))
            self.img.paste(canvas.img.crop((x, 0, x + w, h)), (u, v))
            x += w

    def save(self):
        return (self.path, gfx.save(self.img, GROUP, self.path, self.rects), "")


def category_icon():
    a = Atlas("system/category_icon.pak/system/category_icon.gim")
    # item-menu category tabs: 全 (all) is the only kanji among the pictograms (16x16 cells)
    a.put((0, 0, 16, 16), "All", "sans-b", 8, WHITE, align="c", min_x=0.6)
    return a


def report_card01():
    a = Atlas("system/_report_card.pak/system/report_card01.gim")
    # 成績表 title (white on transparent, x 3..78, y 0..22)
    a.put((3, 0, 76, 23), "Report Card", "serif-b", 16, WHITE, align="c")
    return a


def status01():
    a = Atlas("system/status01.gim")
    # attribute table (panel x 0..219; header y 42..53; rows 56..137)
    a.put((3, 42, 55, 12), "Attribute", size=11, bg="panel", align="c")
    a.put((62, 42, 53, 12), "Value", size=11, bg="panel", align="c")
    a.put((122, 42, 95, 12), "Affects", size=11, bg="panel", align="c")
    attrs = [("Stamina", "HP, Defense"), ("Reflexes", "Damage"), ("Willpower", "Hanafuda Power"),
             ("Speed", "AP"), ("Judgment", "All Attacks")]
    for (name, what), (y, h) in zip(attrs, [(55, 17), (73, 15), (89, 16), (106, 16), (123, 15)]):
        a.put((2, y, 56, h), name, size=12, bg="panel", xscale=0.9)
        a.put((120, y, 97, h), what, "sans", 11, SOFT, bg="panel")
    # subject table (panel x 224..443; header y 2..13; rows 16..131)
    a.put((227, 2, 55, 12), "Subject", size=11, bg="panel", align="c")
    a.put((286, 2, 53, 12), "Value", size=11, bg="panel", align="c")
    a.put((346, 2, 95, 12), "Affects", size=11, bg="panel", align="c")
    subs = [("Japanese", "Inscription Decoding"), ("Math", "Chest Unlocking"), ("Languages", "Quests"),
            ("P.E.", "Jump Distance"), ("Soc. Studies", "Item Discounts"), ("Health", "Auto HP Recovery"),
            ("Biology", "Ailment Evasion")]
    rows = [(16, 16), (33, 15), (49, 16), (66, 16), (83, 16), (100, 16), (117, 15)]
    for (name, what), (y, h) in zip(subs, rows):
        a.put((226, y, 56, h), name, size=12, bg="panel", xscale=0.9)
        a.put((344, y, 97, h), what, "sans", 11, SOFT, bg="panel")
    # report-card selection banner (dark strip y 195..208)
    a.put((20, 195, 194, 14), "Select a character's report card", size=12, bg="panel", align="c")
    # bonus panels, stat panel, profile panel
    a.put((3, 275, 77, 14), "Subject Bonus", size=11, bg="panel", align="c")
    a.put((4, 293, 60, 16), "Left", size=12, bg="panel")
    a.put((3, 323, 77, 14), "Attribute Bonus", size=11, bg="panel", align="c")
    a.put((4, 342, 60, 16), "Left", size=12, bg="panel")
    for text, (y, h) in zip(["HP", "AP", "Arcane Eye"], [(278, 15), (294, 15), (309, 15)]):
        a.put((99, y, 86, h), text, size=12, bg="panel")
    for text, (y, h) in zip(["Condition", "Club", "Notes"], [(277, 14), (292, 15), (309, 15)]):
        a.put((259, y, 120, h), text, size=12, bg="panel")
    # skill / level panels
    a.put((3, 365, 55, 15), "Level", size=11, bg="panel")
    a.put((60, 366, 93, 14), "Active Skill", size=11, bg="panel", align="r")
    a.put((3, 398, 60, 13), "Uses", size=11, bg="panel")
    a.put((3, 421, 55, 16), "Level", size=11, bg="panel")
    a.put((60, 421, 94, 16), "Passive Skill", size=11, bg="panel", align="r")
    a.put((2, 461, 39, 16), "Level", size=13, bg="panel")
    a.put((48, 460, 104, 16), "Experience", size=13, bg="panel")
    a.put((48, 477, 104, 12), "Next Level", size=11, bg="panel")
    return a


def status02():
    a = Atlas("system/status02.gim")
    # 成績表 on three tilted black tiles: wipe each glyph, one outlined title over all three
    for box in [(10, 6, 24, 24), (41, 6, 22, 22), (65, 4, 24, 24)]:
        a.put(box, "", bg="black")
    a.put((6, 6, 86, 24), "Report Card", "serif-b", 15, WHITE, stroke=(1, BLACK), align="c", bg="keep")
    legend = ["Previous Buddy", "Details", "", "Add Bonus", "Buddy List", "Next Buddy"]
    for i, text in enumerate(legend):
        y = 288 + 16 * i
        if i == 2:
            a.put((17, y, 50, 16), "Back", size=11, stroke=(1, BLACK))
            a.put((68, y, 57, 16), "Confirm", size=11, stroke=(1, BLACK))
        else:
            a.put((17, y, 108, 16), text, size=11, stroke=(1, BLACK))
    return a


def ui_lsmap01():
    a = Atlas("system/_ui_map.pak/adv/freemove/ui_lsmap01.gim")
    # two vertical captions: 鴉乃杜學園 (x 80..101) and 新宿区周辺 (x 102..127), rotated to read downwards
    a.stack([(80, 0, 22, 128)], "Karasu no Mori Academy", size=12)
    a.stack([(102, 0, 26, 128)], "Shinjuku Area", size=14)
    return a


def ui_map04():
    a = Atlas("system/_ui_map.pak/system/ui_map04.gim")
    # left tab strip: the game stacks 24px cells top to bottom (offsets from ui_map.g2d)
    a.stack([(0, 0, 24, 24), (0, 24, 24, 24)], "All", size=15)                             # 全 体
    a.stack([(0, 48, 24, 16, 0), (24, 48, 16, 16, 8), (25, 0, 23, 24, 1)], "Map", size=15)  # マ ッ プ
    # 24px cells hold two short lines (a 6-letter word rotated would need ~45px)
    for cell, word in [((48, 0, 24, 24), "Spr\ning"), ((48, 25, 24, 23), "Sum\nmer"),
                       ((72, 0, 24, 24), "Aut\numn"), ((72, 25, 24, 23), "Win\nter")]:  # 春 夏 秋 冬
        a.put(cell, word, size=10, align="c", spacing=-1)
    a.put((40, 48, 24, 16), "")                                                           # の
    a.put((25, 24, 23, 24), "Hol\nlow", size=10, align="c", spacing=-1)                   # 洞
    a.stack([(104, 0, 24, 72)], "Ryujudo", size=15)                                       # 龍珠堂
    a.stack([(104, 72, 24, 56), (72, 56, 24, 72)], "Drill Ground", size=15)               # 模擬 演習場
    return a


def ui_album05():
    a = Atlas("system/_ui_myroom.pak/system/ui_album05.gim")
    # album tabs: vertical stacks of cells (ui_album.g2d). 第 N 話 = "Ep." + digit cell; 話 stays blank
    a.stack([(96, 0, 24, 80)], "Album", size=17)                                        # アルバム
    a.stack([(0, 0, 24, 24)], "Ep.", size=15)                                           # 第
    a.put((0, 25, 24, 23), "")                                                          # 話
    for cell, n in [((0, 48, 24, 16), "1"), ((0, 66, 24, 16), "2"), ((0, 81, 24, 23), "3"), ((0, 105, 24, 16), "4"),
                    ((24, 64, 24, 24), "5"), ((24, 88, 24, 24), "6"), ((48, 80, 24, 24), "7"),
                    ((48, 104, 24, 24), "8"), ((72, 88, 24, 24), "9"), ((97, 88, 24, 24), "10")]:   # 一 .. 十
        a.stack([cell], n, size=15)
    a.stack([(24, 0, 24, 64)], "Other", size=15)                                        # その他
    # エンディング: cell 49,0,23,80 (rows 16..39 are also the ン cell, 72,64 the グ cell: keep those blank)
    a.stack([(49, 0, 23, 80)], "Ending", size=15, span=(40, 40))
    # プロローグ: cells 72,0,24,40 / 72,24,24,16 / 72,40,24,48; rows 64..88 are Ending's グ cell, so only rows 40..64 can hold text
    a.put((72, 0, 24, 40), "")
    a.stack([(72, 40, 24, 48)], "Intro", size=15, span=(0, 24))
    return a


def cardarc():
    a = Atlas("system/cardarc.gim")
    # month plants, 32x32 cells; 菖蒲 / 牡丹 / 紅葉 are two cells the game puts side by side
    kw = dict(font="impact", size=12, align="c", spacing=-2, min_x=0.7)
    for (u, v), word in [((128, 0), "Pine"), ((160, 0), "Plum"), ((192, 0), "Cherry"), ((224, 0), "Wis-\nteria"),
                         ((384, 0), "Bush\nClover"), ((128, 32), "Pampas"), ((160, 32), "Chrys."),
                         ((256, 32), "Willow"), ((288, 32), "Pau-\nlownia")]:        # 松 梅 桜 藤 萩 芒 菊 柳 桐
        a.put((u, v, 32, 32), word, **kw)
    a.hstack([(256, 0, 32, 32), (288, 0, 32, 32)], "Iris", **kw)                  # 菖蒲
    a.hstack([(320, 0, 32, 32), (352, 0, 32, 32)], "Peony", **kw)                 # 牡丹
    a.hstack([(192, 32, 32, 32), (224, 32, 32, 32)], "Maple", **kw)               # 紅葉
    return a


def map0999():
    a = Atlas("system/map_view/map0100.pak/system/map_view/map0999.gim")
    # 第N階層へ (floors are 1F..4F in the game text), horizontal rows then vertical columns (4, 3, 2, 1), 地上へ both ways
    for i in range(4):
        a.glow((0, 24 * i, 96, 24), f"To {i + 1}F")
        a.glow((96 + 24 * i, 0, 24, 96), f"To {4 - i}F", rotate=True)
    a.glow((192, 0, 64, 24), "To Surface")
    a.glow((192, 24, 24, 72), "To Surface", rotate=True)
    return a


def ui_saveload01():
    a = Atlas("system/saveload.pak/system/ui_saveload01.gim")
    # セーブ / ロード are 24px cells laid side by side (ー is an 8px-tall slice shared by both words, so the whole
    # English word goes in the first cell and the rest stay blank); ・ (32,24) is kept as the separator
    a.put((0, 0, 24, 24), "Save", "impact", 14)                                             # セ
    for cell in [(0, 24, 8, 24), (8, 24, 24, 8), (24, 0, 24, 24), (48, 0, 16, 24)]:         # ー ー ブ ド
        a.put(cell, "")
    a.put((8, 32, 24, 16), "Load", "impact", 12)                                            # ロ
    # はじめから = one 80x24 cell, but から (48,64,32,24) is also the tail of つづきから: keep x 48.. blank
    a.put((0, 64, 48, 24), "New\nGame", size=11, align="c", spacing=-2)
    a.put((48, 64, 32, 24), "")
    a.put((0, 88, 56, 24), "Continue", size=13, align="c")                                 # つづき
    return a


def ui_equip05():
    a = Atlas("system/ui_equip.pak/system/ui_equip05.gim")
    a.stack([(34, 16, 27, 48)], "Equip", size=20)                                           # 装備
    tab_purple(a, (102, 24, 26, 40), (102, 64, 26, 40))                                     # 武器 防具 (halo runs 2px left of the cell)
    return a


def ui_exitem01():
    a = Atlas("system/ui_exitem.pak/system/ui_exitem01.gim")
    # 貴 重 品: three 24px cells the game stacks top to bottom
    a.stack([(136, 48, 24, 24), (160, 48, 24, 24), (184, 48, 24, 24)], "Key Items", size=18)
    return a


def ui_flowercard01():
    a = Atlas("system/ui_flowercard.pak/system/ui_flowercard01.gim")
    # 札強 (104,0,24,56) + 化 (80,48,24,16) stacked; the bottom-row pieces at y 48..64 (x 96..128) stay (unclear use)
    a.stack([(104, 0, 24, 56), (80, 48, 24, 16)], "Enhance", size=18)
    return a


def tab_purple(a, weapon, armor):
    """武器 / 防具 tabs: white letters in a purple halo (shared by ui_equip05 and ui_hensei03)."""
    for cell, word in [(weapon, "Weapon"), (armor, "Armor")]:
        a.glow(cell, word, rotate=True, font="sans-b", size=11, halo=(102, 0, 102, 255), radius=1, strength=0.5,
               margin=4, crisp=True)


def ui_hensei03():
    a = Atlas("system/ui_hensei.pak/system/ui_hensei03.gim")
    a.stack([(152, 136, 24, 96)], "Explore Prep", size=17)                                  # 探索準備
    tab_purple(a, (176, 136, 24, 40), (176, 176, 24, 40))
    return a


def ui_item05():
    a = Atlas("system/ui_item.pak/system/ui_item05.gim")
    a.stack([(96, 24, 24, 24), (89, 48, 23, 64, 1)], "Items", size=18)                       # ア イテム
    return a


def ui_itemchange05():
    a = Atlas("system/ui_itemchange.pak/system/ui_itemchange05.gim")
    a.stack([(104, 0, 24, 48)], "Swap", size=18)                                            # 入替
    return a


def ui_itemget05():
    a = Atlas("system/ui_itemget.pak/system/ui_itemget05.gim")
    a.stack([(169, 80, 23, 48)], "Obtain", size=18)                                         # 入手
    return a


def ui_itemgive01():
    a = Atlas("system/ui_itemgive.pak/system/ui_itemgive01.gim")
    a.stack([(104, 0, 24, 88)], "Items", size=18)                                           # アイテム
    return a


def ui_loading():
    a = Atlas("system/ui_loading.pak/system/ui_loading.gim")
    # 読み込み中… is revealed left to right (cells 8,80 x 24..136 wide are prefixes of one strip)
    a.put((8, 80, 136, 24), "Loading...", size=20, align="l", tracking=3)
    return a


def ui_shop05():
    a = Atlas("system/ui_shop.pak/system/ui_shop05.gim")
    # brush shop signs; the Siddham seed syllable (88,48,40,56) stays
    sign = dict(font="KaushanScript-Regular.ttf", fill=WHITE)
    a.put((88, 0, 56, 24), "Sundries", size=16, align="c", **sign)                          # 雑貨
    a.put((88, 24, 64, 24), "", bg=None)                                                    # 雑貨 reflection, redrawn below
    glint = typeset.text_image(64, 24, "Sundries", sign["font"], size=16, fill=(255, 255, 255, 110), align="c")
    a.img.alpha_composite(glint, (88, 24))
    a.put((88, 104, 64, 32), "School\nStore", size=14, align="c", spacing=-3, **sign)       # 購買
    a.stack([(88, 160, 32, 32), (90, 192, 30, 32, 2), (88, 224, 32, 32)], "Toy Store", font=sign["font"], size=22)  # 玩具屋
    return a


ROWS = [category_icon, report_card01,status01, status02, ui_lsmap01, ui_map04, ui_album05, cardarc, map0999, ui_saveload01,
        ui_equip05, ui_exitem01, ui_flowercard01, ui_hensei03, ui_item05, ui_itemchange05, ui_itemget05,
        ui_itemgive01, ui_loading, ui_shop05]


def main():
    out = []
    for fn in ROWS:
        out.append(fn().save())
    gfx.write_tsv(GROUP, out)
    for n in notes:
        print("NOTE", *n)


if __name__ == "__main__":
    main()
