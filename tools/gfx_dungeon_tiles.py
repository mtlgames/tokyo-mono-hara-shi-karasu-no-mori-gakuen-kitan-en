"""gfx_dungeon_tiles.py: kanji numerals on dungeon puzzle textures (inside .znt models) -> Arabic numerals.

    python -X utf8 tools/gfx_dungeon_tiles.py

Cells from the .znt survey (docs/re/graphics.md, qa-findings.md "Dungeon textures inside .znt models"). Each glyph's
pixels are found by colour inside its rect, filled from their neighbours, and the digit drawn over the glyph's box.
Also the 敵/将 map markers (Foe/Boss) and the 鬼 plate (Oni).
The virtue/horse/是非 tiles stay kanji: the obj text names them in English and a word would not fit a tile; so does
the 12x16 px 点火 sign on bg0008_obj014 (too small for an English word).
"""
import gfx
import typeset

BRUSH, SERIF = "KaushanScript-Regular.ttf", "LiberationSerif-Bold.ttf"


def yellow(p):
    return p[3] > 0 and p[0] > 150 and p[1] > 110 and p[0] - p[2] > 70


def ink(p):
    return p[3] > 0 and 0.3 * p[0] + 0.59 * p[1] + 0.11 * p[2] < 120


WALLS = [(f"dungeon/bg11_00.pak/dungeon/bg0011_obj00{n}.znt@{off}", str(i)) for i, (n, off) in
         enumerate([(3, "0x20"), (4, "0x20"), (5, "0x20"), (6, "0x1130")], 1)]
TILES4 = "dungeon/waginoma.pak/dungeon/bg0011_004.znt@0x12440"
SLIPS = "dungeon/jugon_hanahuda01.znt@0x20"
MARKERS = "dungeon/jugon_boss.znt@0x20"
ONI = "dungeon/seihennoma.pak/dungeon/bg0007_015.znt@0x1a2d0"
# 壱 肆 貮 伍 参 slips: rect of the white oval each sits in (x, y, w, h), digit
SLIP_CELLS = [((10, 14, 12, 25), "1"), ((43, 9, 11, 24), "4"), ((10, 54, 12, 24), "2"), ((43, 50, 11, 24), "5"),
              ((10, 95, 12, 24), "3")]


def fill(img, mask, iters=40):
    """Diffuse the surrounding colours into the masked pixels (set of (x, y))."""
    px = img.load()
    todo = set(mask)
    for x, y in todo:
        px[x, y] = (0, 0, 0, 0)
    for _ in range(iters):
        if not todo:
            break
        done = {}
        for x, y in todo:
            nb = [px[x + dx, y + dy] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                  if 0 <= x + dx < img.width and 0 <= y + dy < img.height and (x + dx, y + dy) not in todo]
            if nb:
                done[(x, y)] = tuple(sum(c[i] for c in nb) // len(nb) for i in range(4))
        for k, v in done.items():
            px[k] = v
        todo -= set(done)


def glow(p):
    """Red glyph and its pink halo on grey stone."""
    return p[3] > 0 and p[0] - p[1] > 18 and p[0] - p[2] > 22


def disc(cx, cy, r):
    """Limit a pick to a circle (the marker ring around a glyph must stay)."""
    return lambda x, y: (x - cx) ** 2 + (y - cy) ** 2 <= r * r


def redo(img, rect, pick, text, font, colour, stroke=None, grow=1, where=None, box=None, patch=None):
    """Wipe the pixels pick() selects inside rect (and where(x, y), grown by `grow` px) and draw text centred on
    their box (or on box=(x, y, w, h))."""
    x0, y0, w, h = rect
    px = img.load()
    hit = [(x, y) for x in range(x0, x0 + w) for y in range(y0, y0 + h)
           if pick(px[x, y]) and (where is None or where(x, y))]
    if not hit:
        raise ValueError(f"no glyph pixels in {rect}")
    bx0, by0 = min(x for x, _ in hit), min(y for _, y in hit)
    bx1, by1 = max(x for x, _ in hit), max(y for _, y in hit)
    mask = {(x + dx, y + dy) for x, y in hit for dx in range(-grow, grow + 1) for dy in range(-grow, grow + 1)
            if x0 <= x + dx < x0 + w and y0 <= y + dy < y0 + h}
    if patch:                           # tile a clean patch of the surface over the glyph (big glyphs smear)
        sx, sy, sw, sh = patch
        tile = img.crop((sx, sy, sx + sw, sy + sh)).load()
        mirror = lambda v, n: v % n if v // n % 2 == 0 else n - 1 - v % n  # noqa: E731  (no seams)
        for x, y in mask:
            px[x, y] = tile[mirror(x, sw), mirror(y, sh)]
    else:
        fill(img, mask)
    side = max(bx1 - bx0, by1 - by0) + 1
    cx, cy = (bx0 + bx1) // 2, (by0 + by1) // 2
    box = box or (cx - side // 2 - 2, cy - side // 2 - 2, side + 4, side + 4)
    typeset.text_image(0, 0, text, font, fill=colour, stroke=stroke, canvas=img, box=box, pad=0, max_size=side + 6)


def main():
    rows = []
    for path, digit in WALLS:           # yellow brush numeral on a stone wall
        img = gfx.original(path)
        redo(img, (0, 0, img.width, img.height), yellow, digit, BRUSH, (247, 206, 49, 255), grow=2)
        rows.append((path, gfx.save(img, "dungeon_tiles", path), f"wall numeral {digit}"))
    img = gfx.original(TILES4)
    for i, digit in enumerate("1234"):  # 2x2 stone tiles, 64 px each: 一 二 / 三 四
        redo(img, (64 * (i % 2) + 6, 64 * (i // 2) + 6, 52, 52), yellow, digit, BRUSH, (247, 206, 49, 255), grow=2)
    rows.append((TILES4, gfx.save(img, "dungeon_tiles", TILES4), "floor tiles 1-4"))
    img = gfx.original(SLIPS)
    for rect, digit in SLIP_CELLS:      # paper slips with an ink numeral (Seated Petitioner 1-5)
        redo(img, rect, ink, digit, SERIF, (40, 32, 24, 255))
    rows.append((SLIPS, gfx.save(img, "dungeon_tiles", SLIPS), "petitioner slips 1-5"))
    img = gfx.original(MARKERS)         # gold ring markers: 敵 (enemy) small, 将 (general) large
    redo(img, (34, 4, 28, 27), yellow, "Foe", SERIF, (214, 160, 24, 255), where=disc(47.5, 17, 11))
    redo(img, (68, 6, 56, 56), yellow, "Boss", SERIF, (214, 160, 24, 255), where=disc(95, 34, 22.5),
         box=(76, 22, 39, 24))
    rows.append((MARKERS, gfx.save(img, "dungeon_tiles", MARKERS), "map markers Foe/Boss"))
    img = gfx.original(ONI)             # glowing red 鬼 on a stone plate
    # spaces: the brush font's italic overhang is outside its measured width
    redo(img, (16, 16, 96, 96), glow, " Oni ", BRUSH, (250, 150, 40, 255), stroke=(2, (210, 40, 20, 255)), grow=2,
         box=(18, 30, 92, 64), patch=(16, 16, 20, 20))
    rows.append((ONI, gfx.save(img, "dungeon_tiles", ONI), "stone plate Oni"))
    gfx.write_tsv("dungeon_tiles", rows)


if __name__ == "__main__":
    main()
