"""gfx_phone.py: cell-phone UI atlases (system/_k_phon.pak). Writes gfx/out/phone/*.png and gfx/phone.tsv.

    python -X utf8 tools/gfx_phone.py

Rows: icon (call labels, button words), menu01 (phone main menu), name (16 profile name plates), sait01 / sait02
(OXAS site headings, ailments, tabs, kana index, small tags), set (settings labels). Every label is cleared inside its
own padded box and redrawn there; gfx.save refuses any pixel changed outside the boxes. `paint` is shared with
gfx_adv_ui.py and gfx_adv_bg.py.
"""
import gfx
import typeset

D = "system/_k_phon.pak/system/"
SANS, SANSB, SERIF = "LiberationSans-Regular.ttf", "LiberationSans-Bold.ttf", "LiberationSerif-Regular.ttf"
WHITE = (255, 255, 255, 255)


def paint(img, rects, box, text, font=SANSB, size=12, fill=WHITE, halo=None, xs=1.0, align="l", stroke=None,
          shadow=None, tracking=0, pad=4, spacing=0, radius=1.2, strength=2, valign="m", clear=True, wipe=None):
    """Clear `wipe` (default box) padded by `pad`, draw `text` inside box (x, y, w, h; align l/c/r), optional glow `halo`."""
    x, y, w, h = box
    wx, wy, ww, wh = wipe or box
    wr = (max(wx - pad, 0), max(wy - pad, 0), min(wx + ww + pad, img.width), min(wy + wh + pad, img.height))
    if clear:
        gfx.clear(img, (wr[0], wr[1], wr[2] - wr[0], wr[3] - wr[1]))
    # canvas = wipe rect plus the text box (English may stick out of the JP extent into empty space)
    r = (min(wr[0], x), min(wr[1], y), max(wr[2], x + w), max(wr[3], y + h))
    r = (r[0], r[1], r[2] - r[0], r[3] - r[1])
    t =typeset.text_image(r[2], r[3], text, font, size=size, fill=fill, xscale=xs, align=align, valign=valign,
                           stroke=stroke, shadow=shadow, tracking=tracking, spacing=spacing, pad=0,
                           box=(x - r[0], y - r[1], w, h))
    if halo:
        gfx.glow(img, r, t, halo, radius=radius, strength=strength)
    else:
        img.alpha_composite(t, r[:2])
    rects.append(r)


def icon():
    path = D + "k_phon_icon.gim"
    img, rects = gfx.original(path), []
    halo = (134, 99, 217, 255)
    for box, text, size, xs in (((9, 130, 80, 20), "Calling...", 16, 1.0), ((9, 154, 80, 20), "In Call...", 16, 1.0)):
        paint(img, rects, box, text, SANSB, size, halo=halo, xs=xs)
    paint(img, rects, (30, 178, 34, 11), "Answer", SANSB, 10, halo=halo, xs=0.9)
    paint(img, rects, (30, 195, 34, 10), "Decline", SANSB, 10, halo=halo, xs=0.9)
    paint(img, rects, (2, 213, 38, 14), "Confirm", SANSB, 11, halo=halo, xs=0.85)
    paint(img, rects, (4, 236, 44, 15), "Partner", SANSB, 12, halo=halo, xs=0.9)
    paint(img, rects, (50, 236, 46, 15), "Client", SANSB, 12, halo=halo, align="c")
    paint(img, rects, (100, 236, 72, 15), "Player", SANSB, 12, halo=halo)
    return path, img, rects, "call labels + button words"


def menu01():
    path = D + "k_phon_menu01.gim"
    img, rects = gfx.original(path), []
    shadow = (1, 1, (255, 255, 255, 90))
    for rule, text in ((22, "Profile Book"), (62, "Mail"), (102, "Check Quests"), (142, "OXAS Official Site"),
                       (182, "Phone Settings"), (230, "Enter Profile")):
        # label band sits above the white rule line; the English subtitle below the rule stays
        paint(img, rects, (46, rule - 20, 205, 19), text, SANS, 17, shadow=shadow, tracking=1, pad=1,
              wipe=(44, rule - 20, 207, 19))
    return path, img, rects, "main menu labels (English subtitles beneath kept)"


NAMES = [  # (x, row y, cell width, English name): 2 columns, 8 rows, 32 px pitch
    (5, 0, 96, "Zero Chiaki"), (116, 0, 108, "Migiri Kashima"),
    (5, 32, 130, "Ichiru Muto"), (146, 32, 86, "Rin Himukai"),
    (5, 64, 86, "Toji Dan"), (116, 64, 130, "Angie D."),
    (5, 96, 108, "Minori Hosaka"), (116, 96, 108, "Kaname Kotokuji"),
    (5, 128, 108, "Nagahide Shishido"), (116, 128, 108, "Dokai Gamo"),
    (5, 160, 86, "Tomoe Tobisaka"), (116, 160, 108, "Hideo Kamon"),
    (5, 192, 96, "Shu Takarakata"), (116, 192, 134, "Ayahito Konosu"),
    (5, 224, 108, "Gio Onimaru"), (116, 224, 134, "Benio Sawakami"),
]


def name():
    path = D + "k_phon_name.gim"
    img, rects = gfx.original(path), []
    for x, y, w, text in NAMES:
        f = typeset.font(SANS, 14).getlength(text)
        wipe = (x - 2, y + 1, 127 if x < 100 else 253 - x, 30)   # whole JP extent of the column, text only within its cell
        paint(img, rects, (x, y + 2, w - 4, 28), text, SANS, 14, halo=(119, 85, 204, 255), xs=min(1.0, (w - 4) / f),
              pad=3, radius=1, strength=2, wipe=wipe)
    return path, img, rects, "16 profile name plates (Western order)"


def sait01():
    path = D + "k_phon_sait01.gim"
    img, rects = gfx.original(path), []
    halo = (68, 51, 153, 255)
    for box, text in (((93, 5, 90, 20), "Oni"), ((93, 32, 95, 21), "Glossary"), ((93, 60, 95, 21), "Guide")):
        paint(img, rects, box, text, SANS, 19, halo=halo, radius=1, strength=2, pad=3)
    for y, text in ((5, "Seal Curse"), (25, "Fracture"), (45, "Sprain"), (65, "Paralysis"), (85, "Sleep"), (105, "Blind")):
        paint(img, rects, (197, y, 58, 14), text, SANSB, 11, halo=halo, radius=1, strength=2, xs=0.92, pad=4)
    for x, w, text, wipe in ((129, 40, "Menu", (123, 126, 52, 14)), (46, 36, "Move", (46, 126, 29, 14)),
                             (84, 42, "Explore", (84, 126, 28, 14)), (185, 42, "Other", (185, 126, 42, 14))):
        paint(img, rects, (x, 126, w, 14), text, SANSB, 11, halo=halo, radius=1, strength=2, pad=3, wipe=wipe)
    for i, (x, text) in enumerate(zip((6, 31, 55, 78, 102, 126, 150, 173, 198, 220), "AKSTNHMYRW")):
        paint(img, rects, (x - 3, 148, 20, 16), text, SANSB, 13, halo=halo, radius=1, strength=2, align="c", pad=3)
    return path, img, rects, "OXAS site headings, ailments, tabs, kana index -> A K S T N H M Y R W"


def sait02():
    path = D + "k_phon_sait02.gim"
    img, rects = gfx.original(path), []
    # (text box, English, size, xscale, wipe = JP extent); white on transparent like the original, English tags kept
    tags = [
        ((3, 2, 27, 12), "New", 12, 1.0, (3, 2, 27, 12)),
        ((3, 20, 70, 15), "Glossary", 13, 1.0, (3, 20, 70, 15)),
        ((80, 2, 15, 12), "Sp", 10, 1.0, (82, 2, 12, 12)), ((96, 2, 15, 12), "Su", 10, 1.0, (98, 2, 12, 12)),
        ((80, 18, 15, 12), "Au", 10, 1.0, (82, 18, 12, 12)), ((96, 18, 15, 12), "Wi", 10, 1.0, (98, 18, 12, 12)),
        ((78, 33, 33, 13), "Element", 10, 0.78, (82, 33, 27, 13)),
        ((79, 50, 32, 12), "Disarm", 10, 0.78, (83, 50, 27, 12)),
        ((3, 66, 27, 12), "Move", 11, 0.8, (3, 66, 26, 12)),
        ((3, 82, 27, 12), "Turn", 11, 0.9, (3, 82, 26, 12)),
        ((34, 82, 38, 12), "Total AP", 10, 0.8, (34, 82, 36, 12)),
        ((3, 98, 34, 12), "Attack", 10, 0.9, (3, 98, 21, 12)),
        ((3, 114, 80, 12), "Items Obtained", 11, 0.95, (3, 114, 81, 12)),
        ((134, 59, 29, 10), "Back", 10, 1.0, (138, 59, 20, 10)),
        ((134, 75, 29, 10), "OK", 10, 1.0, (138, 75, 20, 10)),
        ((134, 91, 29, 10), "Select", 10, 0.85, (137, 91, 21, 10)),
        ((2, 202, 14, 12), "A", 11, 1.0, (3, 202, 11, 12)), ((17, 202, 14, 12), "B", 11, 1.0, (17, 202, 13, 12)),
        ((2, 218, 14, 12), "C", 11, 1.0, (2, 218, 12, 12)), ((16, 217, 17, 13), "Div", 10, 0.85, (17, 217, 13, 13)),
    ]
    for box, text, size, xs, wipe in tags:
        paint(img, rects, box, text, SANSB, size, xs=xs, pad=1, wipe=wipe, align="c" if len(text) == 1 else "l")
    return path, img, rects, "tags"


def set_():
    path = D + "k_phon_set.gim"
    img, rects = gfx.original(path), []
    halo = (159, 120, 224, 255)
    for x, y, w, text in (
            (4, 5, 112, "Basic Text Speed"), (133, 5, 112, "Aiming Cursor Speed"),
            (4, 29, 112, "Auto Text Advance"), (133, 29, 112, "Emotion Input Hold"),
            (4, 54, 90, "Effects Volume"), (108, 54, 98, "Confirm Turn End"),   # boxes inside the g2d cells
            (2, 78, 60, "Voice Volume"), (77, 78, 70, "Navi Voice"), (165, 78, 82, "Ringtone"),
            (3, 102, 84, "BGM Volume")):
        xs = min(1.0, w / typeset.font(SANS, 12).getlength(text))
        paint(img, rects, (x, y, w, 14), text, SANS, 12, halo=halo, xs=xs, pad=4, radius=1, strength=1.5)
    return path, img, rects, "settings labels"


GROUPS = [icon, menu01, name, sait01, sait02, set_]


def main():
    rows = []
    for fn in GROUPS:
        path, img, rects, note = fn()
        rows.append((path, gfx.save(img, "phone", path, rects), note))
    gfx.write_tsv("phone", rows)


if __name__ == "__main__":
    main()
