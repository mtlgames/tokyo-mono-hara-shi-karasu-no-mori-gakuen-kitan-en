"""gfx_survey.py: the new-game questionnaire sheet (name entry + three questions). Writes gfx/out/survey/*.png and
gfx/survey.tsv.

    python -X utf8 tools/gfx_survey.py

The sheet is a texture of the 3D model system/name_input.znt (GIM 0 = the sheet, 1 = the footer strip, 2 = blank
parchment), found by `gimsheet.py --embedded`. The game circles an answer at a fixed spot, so every English answer
starts where its Japanese one did. Text cells are wiped with the blank parchment (same pattern); the gold header bands
get their band colour back. Wording follows tables/inputproftext (the game's unused text copy of this sheet).
"""
from collections import Counter

import gfx
import typeset

SHEET = "system/name_input.znt@0x30"
FOOT = "system/name_input.znt@0x20140"
BLANK = "system/name_input.znt@0x22250"
SERIF, BOLD = "LiberationSerif-Regular.ttf", "LiberationSerif-Bold.ttf"
INK = (107, 89, 49, 255)

# (x, y top of the JP line, text): x = the JP line's first ink column, y = its top row (measured from the original).
LINES = [
    (106, 43, "Reading", 64), (88, 62, "Name", 0),   # label cells: centred in x 67-130 (see main)
    (67, 94, "Read each question carefully and answer the ones that apply."),
    (75, 123, "Q1"), (116, 123, "About Studying"),
    (90, 138, "Which subject are you interested in?"),
    (89, 154, "Choose one of the following."),
    (107, 178, "Japanese"), (179, 178, "Math"), (249, 178, "Biology"), (322, 178, "Social Studies"),
    (106, 198, "Languages"), (179, 198, "Health"), (249, 198, "P.E."),
    (75, 246, "Q2"), (116, 246, "About the Library"),
    (90, 262, "How often do you usually use the library?"),
    (89, 278, "Choose the one that applies."),
    (107, 302, "Often"), (250, 302, "Sometimes"),
    (106, 322, "Not much"), (250, 322, "Almost never"),
    (75, 371, "Q3"), (117, 371, "About Part-Time Jobs"),
    (91, 386, "Have you ever had a part-time job,"),
    (91, 402, "or would you like to have one?"),
    (92, 418, "And if so, what for?"),
    (90, 434, "Choose the one that applies."),
    (107, 458, "For the money"), (248, 458, "To broaden my horizons"),
    (107, 479, "Some other reason"), (250, 479, "I don't work part-time"),
]
# Japanese ink boxes (x0, y0, x1, y1), measured: every one is wiped before the English goes on.
JP = [(74, 43, 125, 54), (88, 62, 110, 74), (67, 94, 390, 107), (75, 123, 194, 134), (90, 138, 363, 151),
      (89, 154, 301, 167), (107, 178, 376, 191), (106, 198, 273, 211), (75, 246, 208, 259), (90, 262, 391, 275),
      (89, 278, 399, 291), (107, 302, 341, 314), (106, 322, 371, 334), (75, 371, 236, 382), (91, 386, 378, 398),
      (91, 402, 266, 414), (92, 418, 280, 430), (90, 434, 400, 447), (107, 458, 357, 470), (107, 479, 371, 490)]
HEADER = (52, 8, 333, 33)        # title band x 52-332; JP ink 67-308 x 12-29
FOOT_BAND = (52, 0, 428, 19)     # footer strip band; JP ink 82-392 x 2-14


def band_fill(img, rect):
    """Replace the dark lettering inside a gold band by the band's most common colour."""
    x0, y0, x1, y1 = rect
    px = img.load()
    lum = lambda p: 0.3 * p[0] + 0.59 * p[1] + 0.11 * p[2]
    base = Counter(px[x, y] for x in range(x0, x1) for y in range(y0, y1) if lum(px[x, y]) > 180).most_common(1)[0][0]
    for y in range(y0, y1):
        for x in range(x0, x1):
            if lum(px[x, y]) <= 180:
                px[x, y] = base


def put(img, x, y, text, font=SERIF, size=13):
    t = typeset.text_image(480, 18, text, font, size=size, fill=INK, align="l", valign="t", pad=0)
    img.alpha_composite(t, (x - 2, y - 4))     # text_image pads 2 px; Liberation's ascent puts caps ~4 px down


def main():
    img, blank = gfx.original(SHEET), gfx.original(BLANK)
    rects = []
    for x0, y0, x1, y1 in JP:
        r = (x0 - 2, y0 - 2, x1 + 3, y1 + 3)
        img.paste(blank.crop(r), r[:2])
        rects.append((r[0], r[1], r[2] - r[0], r[3] - r[1]))
    band_fill(img, HEADER)
    rects.append((HEADER[0], HEADER[1], HEADER[2] - HEADER[0], HEADER[3] - HEADER[1]))
    typeset.text_image(0, 0, "Survey on Daily Life and Attitudes", BOLD, size=15, fill=INK, align="l", valign="m",
                       canvas=img, box=(66, 9, 262, 22), pad=0)
    for row in LINES:
        x, y, text = row[:3]
        if text in ("Reading", "Name"):     # label cells x 67-130
            typeset.text_image(0, 0, text, SERIF, size=12, fill=INK, canvas=img, box=(67, y - 3, 63, 16), pad=0)
            continue
        put(img, x, y, text, BOLD if text.startswith("Q") and len(text) == 2 else SERIF)
    # English answers run past some JP boxes: grow each declared rect to the drawn ink (checked by gfx.save)
    rects.append((68, 40, 62, 38))      # label cells, inside their frame lines
    rects.append((60, 90, 420, 410))
    rects.append((60, 410, 420, 85))
    sheet = gfx.save(img, "survey", SHEET, rects)

    foot = gfx.original(FOOT)
    band_fill(foot, FOOT_BAND)
    typeset.text_image(0, 0, "When you have finished, turn the sheet over.", SERIF, size=13, fill=INK, canvas=foot,
                       box=(52, 0, 376, 17), pad=0)
    foot_png = gfx.save(foot, "survey", FOOT, [(52, 0, 376, 19)])
    gfx.write_tsv("survey", [(SHEET, sheet, "questionnaire sheet (name_input.znt texture 0)"),
                             (FOOT, foot_png, "questionnaire footer strip (texture 1)")])


if __name__ == "__main__":
    main()
