"""gfx_quest_site.py: quest result/shop/avatar textures and the OXAS-site help panels (group quest_site).
Writes gfx/out/quest_site/*.png and gfx/quest_site.tsv.

    python -X utf8 tools/gfx_quest_site.py

Rows: work/gfx/quest_site.txt. Cells come from the .g2d beside each GIM (tools/g2d.py); panels the game draws whole
(k_phon_qa_*) are re-laid freely inside their cell. The helpers (erase, draw) are reused by gfx_dungeon_ui.py.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

import gfx
import typeset

GROUP = "quest_site"
SANS_B, SANS = "LiberationSans-Bold.ttf", "LiberationSans-Regular.ttf"
SERIF_B, SERIF = "LiberationSerif-Bold.ttf", "LiberationSerif-Regular.ttf"
BRUSH, ANTON = "KaushanScript-Regular.ttf", "Anton-Regular.ttf"
WHITE = (255, 255, 255, 255)


# ---- helpers (shared with gfx_dungeon_ui) ----------------------------------------------------------------------
def white(lo=170, hi=None):
    """pred: near-white (min channel > lo) opaque pixels."""
    return lambda r: (r[..., :3].min(axis=2) > lo) & (r[..., 3] > 60)


def grey(lo=110, spread=70):
    """pred: low-saturation light pixels (grey / lavender lettering on a saturated bar)."""
    return lambda r: (r[..., :3].min(axis=2) > lo) & (r[..., :3].max(axis=2) - r[..., :3].min(axis=2) < spread)


def erase(img, box, pred=None, grow=2, iters=80):
    """Remove lettering inside box (x, y, w, h). pred None: the cell is transparent there, clear it. Otherwise pred(region)
    marks the lettering pixels and the surrounding art is diffused into them."""
    x, y, w, h = box
    if pred is None:
        gfx.clear(img, box)
        return
    reg = np.array(img.crop((x, y, x + w, y + h))).astype(float)
    mask = pred(reg)
    if grow:
        mask = ndimage.binary_dilation(mask, iterations=grow)
    known, cur = ~mask, reg.copy()
    cur[mask] = 0
    for _ in range(iters):
        wsum, acc = np.zeros(mask.shape), np.zeros(reg.shape)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            k, v = np.roll(known, (dy, dx), (0, 1)), np.roll(cur, (dy, dx), (0, 1))
            wsum += k
            acc += v * k[..., None]
        fill = mask & ~known & (wsum > 0)
        cur[fill] = acc[fill] / wsum[fill][:, None]
        known = known | fill
    img.paste(Image.fromarray(cur.clip(0, 255).astype("uint8")), (x, y))


def layer(parts, font, size, fill, stroke=None, shadow=None, xscale=1.0, tracking=0):
    """RGBA layer of one line; parts is a str or [(text, colour|None)]. Cropped horizontally to the ink, full line height."""
    f = typeset.font(font, size)
    parts = [(parts, None)] if isinstance(parts, str) else parts
    sw = stroke[0] if stroke else 0
    asc, desc = f.getmetrics()
    adv = [sum(f.getlength(c) + tracking for c in s) for s, _ in parts]
    big = Image.new("RGBA", (int(sum(adv)) + 2 * sw + 8, asc + desc + 2 * sw + 4), (0, 0, 0, 0))
    for fillpass in ((False, True) if stroke else (True,)):
        d = ImageDraw.Draw(big)
        x = sw + 3
        for (s, c), a in zip(parts, adv):
            for ch in s:
                if fillpass:
                    d.text((x, sw + 2), ch, font=f, fill=c or fill)
                else:
                    d.text((x, sw + 2), ch, font=f, fill=stroke[1], stroke_width=sw, stroke_fill=stroke[1])
                x += f.getlength(ch) + tracking
    bb = big.getbbox()
    if not bb:
        return big
    big = big.crop((bb[0], 0, bb[2], big.height))
    if shadow:   # (dx, dy, colour)
        sh = Image.new("RGBA", big.size, shadow[2])
        sh.putalpha(big.split()[3].point(lambda v: v * shadow[2][3] // 255))
        out = Image.new("RGBA", (big.width + abs(shadow[0]), big.height + abs(shadow[1])), (0, 0, 0, 0))
        out.alpha_composite(sh, (max(shadow[0], 0), max(shadow[1], 0)))
        out.alpha_composite(big, (max(-shadow[0], 0), max(-shadow[1], 0)))
        big = out
    if xscale != 1.0:
        big = big.resize((max(1, round(big.width * xscale)), big.height), Image.LANCZOS)
    return big


def draw(img, box, parts, font=SANS, size=10, fill=WHITE, align="c", valign="m", stroke=None, shadow=None, xscale=1.0,
         tracking=0, angle=0, glow=None, dy=0, dx=0, post=None):
    """Draw one line of text inside box (x, y, w, h) of img. glow=(colour, radius, strength) puts a halo behind it;
    post(layer) recolours the rendered line (gradient_fill)."""
    x, y, w, h = box
    lay = layer(parts, font, size, fill, stroke, shadow, xscale, tracking)
    if post:
        lay = post(lay)
    if lay.width > w and not angle:   # never overflow the box: squeeze, and say so when it is a lot
        k = w / lay.width
        if k < 0.85:
            print(f"squeezed x{k:.2f}: {parts if isinstance(parts, str) else [s for s, _ in parts]}")
        lay = lay.resize((w, lay.height), Image.LANCZOS)
    if angle:
        lay = lay.rotate(angle, Image.BICUBIC, expand=True)
    ox = {"l": 0, "c": (w - lay.width) // 2, "r": w - lay.width}[align] + dx
    oy = {"t": 0, "m": (h - lay.height) // 2, "b": h - lay.height}[valign] + dy
    cv = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    cx, cy = max(-ox, 0), max(-oy, 0)
    clip = lay.crop((cx, cy, min(lay.width, w - ox), min(lay.height, h - oy)))
    cv.alpha_composite(clip, (ox + cx, oy + cy))
    if glow:
        gfx.glow(img, box, cv, glow[0], radius=glow[1], strength=glow[2])
    else:
        img.alpha_composite(cv, (x, y))
    return lay


def gradient_fill(top, bottom, outline):
    """post for draw(): the white of a line drawn with stroke=(w, outline) becomes a top-to-bottom gradient."""
    def post(lay):
        a = np.array(lay).astype(float)
        h = a.shape[0]
        rows = np.nonzero((a[..., 3] > 0).any(axis=1))[0]
        g = np.clip((np.arange(h) - rows.min()) / max(1, rows.max() - rows.min()), 0, 1)[:, None, None]   # over the ink
        grad = np.array(top[:3], float) * (1 - g) + np.array(bottom[:3], float) * g
        t = np.clip((a[..., :1] - outline[0]) / (255.0 - outline[0]), 0, 1)
        a[..., :3] = np.array(outline[:3], float) * (1 - t) + grad * t
        return Image.fromarray(a.clip(0, 255).astype("uint8"))
    return post


def vertical(img, box, text, font=SANS, size=10, fill=WHITE, align="c", **kw):
    """Draw text rotated 90 degrees clockwise (reads top to bottom) into box (x, y, w, h), as Japanese vertical menus do."""
    x, y, w, h = box
    cv = Image.new("RGBA", (h, w), (0, 0, 0, 0))
    draw(cv, (0, 0, h, w), text, font, size, fill, align, **kw)
    img.alpha_composite(cv.rotate(-90, expand=True), (x, y))


class Edit:
    """One image: erase()/draw() record every rect they touch so save() can refuse changes outside them."""

    group = GROUP

    def __init__(self, path):
        self.path, self.img, self.rects, self.clears = path, gfx.original(path), [], []

    def erase(self, box, pred=None, **kw):
        self.rects.append(box)
        if pred is None:
            self.clears.append(box)   # transparent-cell clears: rectcover.py checks these against the original
        erase(self.img, box, pred, **kw)

    def draw(self, box, *a, **kw):
        self.rects.append(box)
        return draw(self.img, box, *a, **kw)

    def vertical(self, box, *a, **kw):
        self.rects.append(box)
        vertical(self.img, box, *a, **kw)

    def colour(self, box):
        c = typeset.dominant(self.img.crop((box[0], box[1], box[0] + box[2], box[1] + box[3])))
        return c + (255,)

    def row(self, note):
        return (self.path, gfx.save(self.img, self.group, self.path, self.rects), note)


# ---- the images ------------------------------------------------------------------------------------------------
def shirt():
    # 廃人 brush print on the shirt (white on alpha 0)
    e = Edit("system/quest/player_avatar.pak/system/quest/player_body03.gim")
    e.erase((1, 178, 62, 44))
    e.draw((1, 178, 62, 44), "WASTED", BRUSH, 15, WHITE, angle=-9)
    return e.row("shirt print 廃人 -> WASTED")


def downloading():
    e = Edit("system/quest/ui_download.pak/system/quest/ui_download07.gim")
    e.erase((0, 1, 132, 24))
    e.draw((0, 1, 132, 24), "Downloading…", SERIF, 17, WHITE, align="l")
    return e.row("ダウンロード中…")


def quest_clear():
    # 依頼達成！ stacked in three bands (y 124-160, 170-207, 215-250); orange-white gradient, red glow
    e = Edit("system/quest/ui_download.pak/system/quest/ui_quest02.gim")
    box = (166, 119, 90, 137)
    e.erase(box)
    cv = Image.new("RGBA", box[2:], (0, 0, 0, 0))
    for (y0, y1), word, xs in (((124, 160), "QUEST", 1.0), ((170, 207), "COMPLETE", 0.76), ((215, 250), "!", 1.0)):
        tmp = Image.new("RGBA", box[2:], (0, 0, 0, 0))
        draw(tmp, (0, y0 - box[1], box[2], y1 - y0 + 1), word, ANTON, 27, WHITE, xscale=xs)
        grad = Image.new("RGBA", box[2:], (0, 0, 0, 0))
        gd = ImageDraw.Draw(grad)
        for yy in range(y0 - box[1], y1 - box[1] + 1):
            t = (yy - (y0 - box[1])) / max(1, y1 - y0)
            gd.line([(0, yy), (box[2], yy)], fill=(254, int(236 - 60 * t), int(215 - 100 * t), 255))
        grad.putalpha(tmp.split()[3])
        cv.alpha_composite(grad)
    gfx.glow(e.img, box, cv, (244, 13, 17, 255), radius=2, strength=2)
    return e.row("依頼達成！ -> QUEST / COMPLETE / !")


def info_broker():
    # 情報屋 title (+ the haloed ghost copy of the lettering below); QUEST SHOP stays
    e = Edit("system/quest/ui_quest.pak/system/quest/ui_quest01.gim")
    main, ghost = (3, 0, 104, 33), (3, 46, 104, 26)
    e.erase(main)
    e.erase(ghost)
    kw = dict(font=SERIF_B, size=16, xscale=0.9)
    e.draw(main, "INFO BROKER", fill=WHITE, **kw)
    # ghost: soft halo around the lettering with the glyph itself left transparent
    cv = Image.new("RGBA", ghost[2:], (0, 0, 0, 0))
    draw(cv, (0, 0) + ghost[2:], "INFO BROKER", fill=WHITE, **kw, dy=0)
    a = cv.split()[3]
    halo = a.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1)).point(lambda v: v * 3 // 5)
    hole = a.point(lambda v: 255 - v)
    out = Image.new("RGBA", cv.size, (255, 255, 255, 0))
    out.putalpha(Image.fromarray(np.minimum(np.array(halo), np.array(hole))))
    e.img.alpha_composite(out, ghost[:2])
    return e.row("情報屋 -> INFO BROKER (title + halo ghost); QUEST SHOP kept")


def switch_label():
    e = Edit("system/site/k_phon_qa_01.pak/system/site/k_phon_qa_01.gim")
    e.erase((171, 13, 34, 20), white(170))
    e.draw((171, 13, 34, 20), "Switch", SANS_B, 10, WHITE, align="l")
    light = lambda r: (r[..., :3].sum(axis=2) > 300) & (r[..., 2] - r[..., 0] < 100)
    for box, word, c in (((44, 48, 40, 18), "None", (146, 141, 156, 255)), ((65, 86, 56, 20), "Examine", (176, 168, 214, 255))):
        e.erase(box, light)
        e.draw(box, word, SANS, 11, c, align="l")
    return e.row("切替 / なし / 調べる")


def arcane_eye():
    e = Edit("system/site/k_phon_qa_06.pak/system/site/k_phon_qa_06.gim")
    box = (40, 12, 70, 22)
    e.erase(box, white(170), grow=3)
    e.draw(box, "Arcane Eye", SERIF_B, 12, WHITE, stroke=(1, (0, 0, 0, 255)))
    return e.row("秘法眼")


def atk():
    e = Edit("system/site/k_phon_qa_13.pak/system/site/k_phon_qa_13.gim")
    box = (16, 16, 26, 20)
    warm = lambda r: ((r[..., 0] > 190) & (r[..., 1] > 90) & (r[..., 2] < 120)) | ((r[..., 0] > 150) & (r[..., 1] < 50) & (r[..., 2] < 50))
    e.erase(box, warm, grow=2)
    e.draw(box, "ATK", SANS_B, 11, (255, 200, 40, 255), stroke=(1, (140, 10, 10, 255)))
    return e.row("攻 -> ATK (shortened: one-kanji cell)")


SEASON = {"Spring": (251, 148, 147, 255), "Summer": (154, 251, 136, 255), "Autumn": (251, 166, 124, 255),
          "Winter": (117, 211, 223, 255)}
PLATE = dict(font=SANS_B, size=10, fill=(244, 244, 244, 255))      # green plate headers (curses, weapons, ailments)
PLATE_TEXT = lambda r: r[..., 0] > 20          # the plate is one green (R=1) with an alpha gradient: any redder pixel is lettering
BODY = dict(font=SANS, size=11, fill=(238, 238, 238, 255))         # panel body text
HALO = ((255, 255, 255, 200), 1.5, 1)


def season_wheel():
    e = Edit("system/site/k_phon_qa_18.pak/system/site/k_phon_qa_18.gim")
    for name, box, al in (("Spring", (106, 0, 42, 25), "c"), ("Summer", (195, 52, 60, 24), "l"),
                          ("Winter", (2, 52, 60, 24), "r"), ("Autumn", (98, 104, 60, 24), "c")):
        e.erase(box)
        e.draw(box, name, SANS_B, 12, SEASON[name], align=al, glow=HALO)
    for name, box, al, c in (("Strong", (148, 3, 34, 21), "r", (248, 7, 6, 255)), ("Weak", (227, 3, 29, 21), "l", (16, 142, 248, 255))):
        e.erase(box)
        e.draw(box, name, SANS_B, 10, c, align=al, glow=HALO)
    return e.row("春夏秋冬 -> Spring/Summer/Autumn/Winter, 強弱 -> Strong/Weak")


def curse_legend():
    e = Edit("system/site/k_phon_qa_20.pak/system/site/k_phon_qa_20.gim")
    rows = (("Wind Curse", "Spring", "Summer"), ("Fire Curse", "Summer", "Autumn"), ("Earth Curse", "Autumn", "Winter"),
            ("Ice Curse", "Winter", "Spring"))
    for i, (name, a, b) in enumerate(rows):
        y = 40 * i
        e.erase((60, 25 + y, 56, 16), PLATE_TEXT, grow=1)
        e.draw((60, 25 + y, 56, 16), name, **PLATE)
        box = (22, 43 + y, 232, 17)
        e.erase(box)
        e.draw(box, [("Becomes ", None), (a, SEASON[a]), (" (", None), (b, SEASON[b]), (" damage +10%)", None)], align="l", **BODY)
    return e.row("curse legend: 風呪 炎呪 土呪 氷呪 + 属性化 lines")


def weapon_ranges():
    e = Edit("system/site/k_phon_qa_23.pak/system/site/k_phon_qa_23.gim")
    names = (("Knife", "Greatsword"), ("Longsword", "Gloves"), ("Spear", "Gun"))
    for r, (l, rt) in enumerate(names):
        for box, word in (((56, 12 + 80 * r, 64, 17), l), ((161, 12 + 80 * r, 62, 17), rt)):
            e.erase(box, PLATE_TEXT, grow=1)
            e.draw(box, word, **PLATE)
    return e.row("weapon range plates ナイフ 大剣 長剣 グローブ 槍 銃")


def ailment_panel(path, note, plates):
    """plates: [(y, name, desc, [(label, text, y)...]|[(None, text, y)...])]; desc/body positions per k_phon_qa_2x layout."""
    e = Edit(path)
    # the game draws qa_25 from x 0, qa_26 from x 32 and qa_27 from x 32 to 240: lettering stays inside that cell
    px, dx, m, rmax = {"25": (44, 112, 12, 252), "26": (76, 143, 44, 254), "27": (76, 143, 44, 238)}[path[-6:-4]]
    for y, name, desc, lines in plates:
        e.erase((px, y, 56, 16), PLATE_TEXT, grow=1)
        e.draw((px, y, 56, 16), name, **PLATE)
        box = (dx, y + 3, rmax - dx, 14)
        e.erase(box)
        e.draw(box, "<<< " + desc, align="l", **{**BODY, "size": 10})
        indent = 0
        for label, text, ly in lines:
            e.erase((m - 2, ly - 2, rmax - m + 2, 15))
            if label:   # "Self:" / "Enemy:" prefix column; "" continues under the previous line's text
                indent = int(typeset.font(SANS, 11).getlength(label + " ")) + 2
                e.draw((m, ly - 2, indent, 15), label, align="l", **{**BODY, "fill": (200, 220, 255, 255)})
            x0 = m + (indent if label is not None else 0)
            e.draw((x0, ly - 2, rmax - x0, 15), text, align="l", **BODY)
    return e.row(note)


def ailments():
    p = "system/site/k_phon_qa_%d.pak/system/site/k_phon_qa_%d.gim"
    rows = []
    rows.append(ailment_panel(p % (25, 25), "封呪 骨折 捻挫 panel", [
        (24, "Seal Curse", "Heals after 5 turns", [("Self:", "Card Enhance and placement undone", 46),
                                                   (None, "Sealing System cannot be used", 62),
                                                   ("Enemy:", "Sealing System triggers when a", 86),
                                                   (None, "Seal Cursed enemy is defeated", 102)]),
        (128, "Fracture", "No natural recovery", [(None, "Max AP cut to 1/5", 150)]),
        (176, "Sprain", "No natural recovery", [(None, "Max AP cut to 1/2", 198),
                                                (None, "Becomes Fracture if inflicted twice", 214)])]))
    rows.append(ailment_panel(p % (26, 26), "麻痺 睡眠 目潰し panel", [
        (24, "Paralysis", "Heals naturally", [(None, "Weapon attacks disabled", 46)]),
        (72, "Sleep", "Heals naturally", [("Self:", "Until you are hit,", 94), ("", "no movement or palette use", 108),
                                          ("Enemy:", "Cannot act until hit", 127)]),
        (152, "Blind", "Heals naturally", [("Self:", "You cannot see", 174), ("Enemy:", "Cannot act", 195)])]))
    rows.append(ailment_panel(p % (27, 27), "悪寒 吐き気 頭痛 panel", [
        (24, "Chills", "Heals naturally", [(None, "Attack range: 1 square ahead", 46),
                                           (None, "Aim wavers with ranged weapons", 62)]),
        (88, "Nausea", "Heals naturally", [(None, "Cannot use food items", 110)]),
        (136, "Headache", "Heals naturally", [(None, "All subject stats become 0", 158)])]))
    return rows


def phone_menu():
    # 電話で呼ぶ / プロフィール on two bars of the call menu (white lettering over dark art)
    e = Edit("system/site/k_phon_qa_35.pak/system/site/k_phon_qa_35.gim")
    for box, word in (((41, 31, 72, 17), "Call by Phone"), ((41, 56, 72, 16), "Profile")):
        e.erase(box, white(170), grow=2)
        e.draw(box, word, SANS, 11, WHITE, align="l")
    return e.row("電話で呼ぶ / プロフィール")


def survey_answers():
    # vertical アンケートを覚えている / いない: rotated lettering, one column each
    e = Edit("system/site/k_phon_qa_39.gim")
    for box, word in (((51, 17, 15, 121), "Remember the survey"), ((33, 17, 15, 128), "Don't remember the survey")):
        e.erase(box, white(160), grow=2)
        e.vertical(box, word, SERIF, 11, (232, 232, 232, 255), align="l")
    return e.row("アンケートを覚えている / いない (vertical, rotated)")


FONT3X5 = {   # 3x5 pixel capitals: the emotion tiles are ~20 px diamonds, too small for any outline font
    "A": "010101111101101", "D": "110101101101110", "E": "111100110100111", "F": "111100110100100",
    "G": "011100101101011", "H": "101101111101101", "I": "111010010010111", "J": "001001001101010",
    "L": "100100100100111", "O": "111101101101111", "P": "110101110100100", "R": "110101110101101",
    "S": "011100010001110", "T": "111010010010010", "U": "101101101101111", "V": "101101101101010",
    "Y": "101101010010010"}


def pixel_text(img, cx, cy, word, colour=(240, 240, 240, 255)):
    """Stamp word in FONT3X5 centred on (cx, cy): 3 px letters, 1 px gaps."""
    w = 4 * len(word) - 1
    x0, y0 = cx - w // 2, cy - 2
    for i, ch in enumerate(word):
        for k, bit in enumerate(FONT3X5[ch]):
            if bit == "1":
                img.putpixel((x0 + 4 * i + k % 3, y0 + k // 3), colour)


def emotion_wheel():
    # eight one-kanji emotion tiles (愛 喜 嫌 怒 悲 困 友 燃) on ~20 px diamonds: 3x5 pixel capitals
    e = Edit("system/site/k_phon_qa_40.gim")
    # word, kanji centre (x, y), lettering centre x, brightest stroke value (燃 is pure white, pale skin sits beside the rest)
    tiles = (("LOVE", 57, 28, 57, 215), ("JOY", 57, 44, 57, 215), ("HATE", 57, 73, 57, 215), ("RAGE", 57, 87, 57, 215),
             ("SAD", 28, 58, 25, 215), ("UPSET", 44, 58, 42, 215), ("PAL", 77, 58, 77, 215), ("FIRE", 95, 58, 95, 256))
    for word, cx, cy, tx, vmax in tiles:
        box = (cx - 11, cy - 10, 23, 21)

        def glyph(r, cx=cx, cy=cy, box=box, vmax=vmax):
            yy, xx = np.mgrid[0:r.shape[0], 0:r.shape[1]]
            inside = np.abs(xx + box[0] - cx) / 10.0 + np.abs(yy + box[1] - cy) / 9.0 < 1   # inside the black diamond
            lo, hi = r[..., :3].min(axis=2), r[..., :3].max(axis=2)
            return inside & (lo > 28) & (hi < vmax) & (hi - lo < 45)   # grey / white strokes
        e.erase(box, glyph, grow=1)
        pixel_text(e.img, tx, cy, word)
    return e.row("emotion wheel -> LOVE JOY HATE RAGE SAD UPSET PAL(友 friend, shortened) FIRE(燃, shortened)")


def main():
    rows = [shirt(), downloading(), quest_clear(), info_broker(), switch_label(), arcane_eye(), atk(), season_wheel(),
            curse_legend(), weapon_ranges()] + ailments() + [phone_menu(), survey_answers(), emotion_wheel()]
    gfx.write_tsv(GROUP, rows)


if __name__ == "__main__":
    main()
