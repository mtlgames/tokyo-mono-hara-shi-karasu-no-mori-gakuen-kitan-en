"""gfx_dungeon_titles.py: brush-script boss/enemy title cards of the dungeon (event_scenes atlases).
Writes gfx/out/dungeon_titles/*.png and gfx/dungeon_titles.tsv.

    python -X utf8 tools/gfx_dungeon_titles.py [--only 0003,0010]

Each atlas holds one card: the word cells (black brush on a white glow, a few coloured) plus flower/animal art that
stays. A word is a `seed` rect (what to wipe: neutral black/white pixels only, so the coloured art survives) and the
English text, redrawn in KaushanScript black with a white glow in the ink's bbox (or an explicit `box` = the cell).

Where a cell sits on screen comes from the .g2d tracks: the first sprite of a card is placed at the RIGHT (x ~370) and
the next ones to its left (vertical-writing order, right to left); only 0006-0008 run left to right. English reads left
to right, so each card lists its English words in reading order and puts them into the cells left to right (= the
Japanese sprites in reverse): a name keeps each part in its own cell (the Japanese family|given, right to left, becomes
Given Family left to right), a title is reversed ("Pine and Crane" goes into the 鶴 cell + the 松 cell). Cells that
carry a particle with no English (ニ ノ 三) are only wiped. 0013 tex002 is art only (no row).
"""
import argparse

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi

import gfx
import typeset

BRUSH = "KaushanScript-Regular.ttf"
INK = (4, 4, 4, 255)
PATH = "dungeon/event_scenes/scenes%s_001_tex001.gim"
CAP, ONI_CAP, PAD, MAXREL, ROT_BELOW = 90, 80, 4, 1.4, 28
RED, PINK = (214, 0, 0), (255, 136, 136)


class W:
    """One word cell. seed: rect or [rects] to wipe; box: draw area (default ink bbox +6); text None = wipe only;
    rot: True/False forces top-to-bottom (rotated 90 clockwise, like the Japanese) or horizontal, None = by the card;
    also: extra colours to wipe/read as ink; full: wipe everything in the seed (no art inside)."""

    def __init__(self, seed, text, grp="c", box=None, rot=None, also=(), fill=INK, full=False):
        self.seeds = seed if isinstance(seed, list) else [seed]
        self.text, self.grp, self.box, self.rotf, self.also, self.fill, self.full = text, grp, box, rot, also, fill, full


def R(x0, y0, x1, y1):
    return (x0, y0, x1, y1)


# image -> words. grp "oni" is shared by every big 隠人 cell ("Oni"), "oni_s" the small one; cards that hold two
# cards (0006, 0011) use groups a / b.
CARDS = {
    # 乙型 遠呂智 七號 -> Type-B Orochi #7 (七號 cell is leftmost)
    "0000": [W(R(0, 0, 66, 150), "#7"), W(R(66, 0, 196, 250), "Orochi"), W(R(196, 0, 356, 250), "Type-B")],
    # 武藤 いちる -> Ichiru Muto
    "0001": [W(R(0, 0, 176, 256), "Muto"), W(R(176, 0, 286, 256), "Ichiru")],
    # 隠人 佐波守 紅緒 (紅 red) -> Benio Sawakami Oni
    "0002": [W(R(0, 0, 194, 235), "Oni", "oni"), W(R(194, 0, 316, 240), "Sawakami", box=R(194, 0, 316, 234)),
             W(R(316, 0, 458, 192), "Benio", box=R(316, 0, 458, 184), also=(RED,), full=True)],
    # 式神 白面 -> Shikigami Hakumen
    "0003": [W(R(0, 0, 162, 252), "Hakumen"), W(R(162, 0, 324, 256), "Shikigami", box=R(160, 0, 320, 256))],
    # 隠人 宍戸 長英 -> Nagahide Shishido Oni
    "0004": [W(R(0, 0, 192, 236), "Oni", "oni"), W(R(192, 0, 284, 232), "Shishido", box=R(192, 0, 282, 228)),
             W(R(284, 0, 384, 232), "Nagahide", box=R(282, 0, 376, 228))],
    # 鬼丸 義王 -> Gio Onimaru
    "0005": [W(R(0, 0, 118, 256), "Onimaru"), W(R(118, 0, 270, 256), "Gio", box=R(118, 0, 266, 256))],
    # 香ノ巣 絢人 / 日向 輪 (laid out left to right) -> Ayahito Konosu / Rin Himukai
    "0006": [W(R(0, 0, 176, 112), "Ayahito", "a", box=R(0, 0, 176, 108)),
             W(R(176, 0, 334, 112), "Konosu", "a", box=R(176, 0, 332, 104)),
             W(R(0, 116, 144, 216), "Rin", "b", box=R(0, 120, 144, 208)),
             W(R(144, 108, 256, 226), "Himukai", "b", box=R(144, 112, 256, 224))],
    # アンジー、 D (left to right)
    "0007": [W(R(0, 0, 384, 156), "Angie", box=R(0, 0, 380, 152)),
             W(R(384, 16, 500, 150), "D.", box=R(384, 16, 496, 144))],
    # 鬼印 盗賊団 (left to right)
    "0008": [W(R(0, 0, 190, 176), "Oni\nMark"), W(R(190, 10, 490, 178), "Bandits")],
    # 隠人 桜 幕 (one column, top to bottom) -> Cherry / Curtain Oni
    "0009": [W(R(0, 0, 194, 230), "Oni", "oni"), W(R(194, 0, 384, 106), "Cherry", box=R(196, 0, 384, 104)),
             W(R(194, 106, 384, 256), "Curtain", box=R(196, 104, 384, 256))],
    # 蒲生 道佳 + pink ミカみゅん -> Dokai Gamo (+ Mi ka myun)
    "0010": [W(R(0, 0, 160, 250), "Gamo"), W(R(160, 0, 344, 252), "Dokai", box=R(166, 96, 334, 246)),
             W(R(326, 16, 426, 134), "Mi", "p", also=(PINK,), fill=PINK + (255,), full=True),
             W(R(424, 0, 512, 142), "ka", "p", also=(PINK,), fill=PINK + (255,), full=True),
             W([R(330, 130, 412, 222), R(412, 140, 424, 165)], "myun", "p", also=(PINK,), fill=PINK + (255,), full=True,
               box=R(338, 134, 424, 218))],
    # 隠人 鹿島 御霧 -> Migiri Kashima Oni; アンジー D -> Angie D.
    "0011": [W(R(0, 0, 90, 108), "Oni", "oni_s"),
             W(R(88, 0, 176, 174), "Kashima", "a", box=R(88, 0, 176, 170)),
             W(R(176, 0, 264, 170), "Migiri", "a", box=R(176, 0, 264, 166)),
             W(R(264, 0, 352, 220), "D.", "b", box=R(264, 0, 352, 216)),
             W(R(352, 0, 434, 92), "Angie", "b", box=R(352, 0, 432, 88))],
    # 松 ニ 鶴 -> Pine and | Crane
    "0012": [W(R(0, 0, 196, 146), "Crane"), W(R(0, 146, 196, 256), None),
             W(R(196, 0, 452, 200), "Pine and", box=R(196, 0, 452, 176))],
    # 隠人 筑紫 信維 -> Nobuyuki Chikushi Oni
    "0013": [W(R(0, 0, 190, 236), "Oni", "oni"), W(R(190, 0, 316, 196), "Chikushi"),
             W(R(316, 0, 456, 196), "Nobuyuki", box=R(318, 0, 452, 196))],
    # 隠人 月 芒 ニ 壱式 -> Pampas and | Moon | I Oni (壱式 is the leftmost cell, 月 and 芒ニ one sprite)
    "0014": [W(R(0, 0, 192, 236), "Oni", "oni"), W([R(190, 0, 296, 250), R(296, 184, 316, 250)], "Moon", box=R(192, 0, 284, 250), rot=True),
             W(R(284, 0, 372, 112), "I", box=R(283, 0, 372, 112), rot=False), W(R(284, 112, 372, 184), None),
             W(R(372, 0, 448, 190), "Pampas and", box=R(372, 0, 446, 186), rot=True)],
    # 隠人 月 芒 ニ 分ケ身 -> Pampas and | Moon | Twin Oni
    "0015": [W(R(0, 0, 190, 236), "Oni", "oni"), W(R(190, 0, 282, 250), "Moon", rot=True),
             W(R(282, 0, 340, 152), "Twin", box=R(282, 0, 342, 152), rot=True), W(R(282, 152, 340, 226), None),
             W(R(340, 0, 412, 186), "Pampas and", rot=True)],
    # 佐波守 紅緒 -> Benio Sawakami
    "0016": [W(R(0, 0, 192, 250), "Sawakami"), W(R(192, 0, 360, 250), "Benio", box=R(192, 0, 360, 248))],
    # 雉明 零 -> Zero Chiaki
    "0017": [W(R(0, 0, 216, 226), "Chiaki", box=R(0, 0, 216, 224)), W(R(216, 0, 346, 256), "Zero", box=R(216, 0, 344, 256))],
    # 五光 ノ 獣 -> Five Brights | Beast
    "0018": [W(R(0, 0, 200, 250), "Beast", box=R(0, 0, 200, 248)),
             W(R(200, 0, 416, 202), "Five\nBrights", box=R(200, 0, 416, 200))],
    # 楼 万 黎 -> Banri | Takadono (黎 sprite is the left one)
    "0019": [W(R(0, 0, 254, 246), "Takadono", box=R(0, 0, 254, 244)), W(R(256, 0, 488, 166), "Banri", box=R(256, 0, 488, 164))],
    # 三 乗 ノ 王 -> Cubed | King (三 and ノ wiped)
    "0020": [W(R(0, 0, 100, 148), None), W(R(0, 148, 100, 230), None),
             W(R(100, 0, 264, 206), "King", box=R(100, 0, 264, 200)), W(R(264, 0, 392, 166), "Cubed")],
    # 隠人 春 秋 ノ 連 -> Spring-Autumn | Link Oni
    "0021": [W([R(0, 0, 128, 64), R(0, 64, 194, 236)], "Oni", "oni"), W(R(128, 0, 194, 64), None),
             W(R(194, 0, 332, 127), "Link", box=R(196, 0, 330, 127)), W(R(194, 127, 358, 204), None),
             W([R(332, 0, 480, 140), R(480, 96, 512, 120)], "Spring-\nAutumn", box=R(334, 0, 478, 140))],
    # 隠人 冬 夏 ノ 理 -> Winter-Summer | Law Oni
    "0022": [W(R(0, 0, 194, 236), "Oni", "oni"), W(R(170, 0, 280, 94), "Law"), W(R(170, 94, 292, 218), None),
             W([R(270, 0, 398, 132), R(398, 64, 470, 132)], "Winter-\nSummer", box=R(270, 0, 398, 118)),
             W(R(398, 0, 470, 64), None)],
    # 隠人 桐 ニ 鳳凰 -> Paulownia | Phoenix Oni
    "0023": [W(R(0, 0, 186, 230), "Oni", "oni"), W(R(322, 0, 442, 80), "Phoenix", box=R(320, 0, 440, 74)),
             W(R(322, 80, 442, 126), None), W(R(186, 0, 362, 256), "Paulownia", box=R(186, 0, 340, 256))],
    # 隠人 柳 ニ 雨 -> Willow and | Rain Oni
    "0024": [W(R(0, 0, 190, 236), "Oni", "oni"), W(R(190, 0, 330, 138), "Rain"), W(R(190, 138, 330, 232), None),
             W(R(330, 0, 470, 172), "Willow\nand")],
}


def solid_squares(a):
    """Mask of the opaque pure-black 32x32 marker blocks: never touched."""
    blk = (a[..., 3] == 255) & (a[..., :3].max(2) == 0)
    core = ndi.binary_erosion(blk, structure=np.ones((32, 32), bool))
    return ndi.binary_dilation(core, structure=np.ones((32, 32), bool)) & blk


def wipe_mask(a, rects, also, full=False):
    """full: everything in the seeds (only where no art sits: coloured brush edges don't match `also`)."""
    rgb = a[..., :3].astype(int)
    m = np.ones(rgb.shape[:2], bool) if full else (rgb.max(2) - rgb.min(2)) < 24
    for c in also:
        m |= (np.abs(rgb - np.array(c)).sum(2) < 90) & (a[..., 3] > 0)
    sel = np.zeros(m.shape, bool)
    for x0, y0, x1, y1 in rects:
        sel[y0:y1, x0:x1] = True
    return m & sel


def ink_bbox(a, rects, also):
    rgb = a[..., :3].astype(int)
    ink = (a[..., 3] > 150) & (rgb.max(2) < 90)
    for c in also:
        ink |= (np.abs(rgb - np.array(c)).sum(2) < 60) & (a[..., 3] > 200)
    sel = np.zeros(ink.shape, bool)
    for x0, y0, x1, y1 in rects:
        sel[y0:y1, x0:x1] = True
    ys, xs = np.nonzero(ink & sel)
    return (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1) if len(xs) else None


def render(text, size, xs, fill):
    """Ink-cropped RGBA of text (lines stacked tight)."""
    lines = []
    for ln in text.split("\n"):
        # padded: the script's flourishes overhang the advance width and text_image clips there
        t = typeset.text_image(1000, 300, f"  {ln}  ", BRUSH, size=size, fill=fill, xscale=xs)
        lines.append(t.crop(t.getchannel("A").getbbox()))
    gap = round(size * 0.04)
    w, h = max(i.width for i in lines), sum(i.height for i in lines) + gap * (len(lines) - 1)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    y = 0
    for i in lines:
        out.alpha_composite(i, ((w - i.width) // 2, y))
        y += i.height + gap
    return out


def fit(text, bw, bh, xs, cap, rot=False):
    """Largest size whose ink fits the box; rot = written top-to-bottom (rotated 90 clockwise), like the Japanese."""
    if rot:
        bw, bh = bh, bw
    for size in range(cap, 7, -1):
        t = render(text, size, xs, INK)
        if t.width <= bw - 2 * PAD and t.height <= bh - 2 * PAD:
            return size
    return 8


def fits(w, xs, cap, rot):
    return fit(w.text, w.box[2] - w.box[0], w.box[3] - w.box[1], xs, cap, rot)


def run_image(num, words):
    path = PATH % num
    img = gfx.original(path)
    a0 = np.array(img)
    prot = solid_squares(a0)
    for w in words:
        w.ink = ink_bbox(a0, w.seeds, w.also)
        if w.text is None:
            continue
        if w.box is None:
            x0, y0, x1, y1 = w.ink
            w.box = R(max(0, x0 - 6), max(0, y0 - 6), min(img.width, x1 + 6), min(img.height, y1 + 6))
    return path, img, a0, prot


def size_group(ws):
    """Sizes for one card: its tightest cell sets the size, roomier cells may go MAXREL times bigger. Condense once per
    card (xscale .85) when that buys >8%; a card whose horizontal lines would be under ROT_BELOW px runs top-to-bottom."""
    auto = [w for w in ws if w.rotf is None]
    f1 = [fits(w, 1.0, CAP, False) for w in auto]
    f2 = [fits(w, 0.85, CAP, False) for w in auto]
    fr = [fits(w, 1.0, CAP, True) for w in auto]
    xs = 0.85 if auto and min(f2) > 1.08 * min(f1) else 1.0
    fs = f2 if xs < 1 else f1
    rot = bool(auto) and min(fs) < ROT_BELOW and min(fr) >= 1.4 * min(fs)
    for w in ws:
        w.rot = rot if w.rotf is None else w.rotf
        w.xs = 1.0 if w.rot else xs
        w.fit = fits(w, w.xs, CAP, w.rot)
    base = min(w.fit for w in ws)
    for w in ws:
        w.size = min(w.fit, int(base * MAXREL))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    only = [s for s in ap.parse_args().only.split(",") if s]
    nums = [n for n in CARDS if not only or n in only]
    prep = {n: run_image(n, CARDS[n]) for n in nums}
    groups = {}
    for n in nums:
        for w in CARDS[n]:
            if w.text:
                groups.setdefault(w.grp if w.grp.startswith("oni") else f"{n}{w.grp}", []).append(w)
    for g, ws in groups.items():
        if g.startswith("oni"):  # every Oni cell is the same artwork: one size
            s = min(fits(w, 1.0, ONI_CAP, False) for w in ws)
            for w in ws:
                w.xs, w.rot, w.size = 1.0, False, s
        else:
            size_group(ws)
    rows = []
    for n in nums:
        path, img, a0, prot = prep[n]
        words = CARDS[n]
        rects = [r for w in words for r in w.seeds] + [w.box for w in words if w.text]
        a = a0.copy()
        wm = np.zeros(a.shape[:2], bool)
        for w in words:
            wm |= wipe_mask(a0, w.seeds, w.also, w.full)
        wm &= ~prot
        a[wm] = (255, 255, 255, 0)
        out = Image.fromarray(a)
        left = ndi.label(ndi.binary_dilation((a[..., 3] > 150) & (a[..., :3].max(2) < 90) & ~prot, iterations=2))
        left = [(s[1].start, s[0].start, s[1].stop, s[0].stop) for s in ndi.find_objects(left[0])]
        glow = (a[..., 3] > 8) & (a[..., 3] < 255) & (a[..., :3].min(2) > 240)  # white glow the seeds missed
        gl = [(s[1].start, s[0].start, s[1].stop, s[0].stop) for s in ndi.find_objects(ndi.label(glow)[0])
              if glow[s].sum() > 12]
        print(n, "dark ink left (art unless it sits in a cell):", left, "glow left:", gl)
        clip = np.zeros(a.shape[:2], bool)
        for x0, y0, x1, y1 in rects:
            clip[y0:y1, x0:x1] = True
        clip &= ~prot
        art = (a[..., 3] > 0) & ((a[..., :3].max(2).astype(int) - a[..., :3].min(2)) >= 24)
        layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        halo = np.zeros(a.shape[:2], np.uint8)
        for w in words:
            if not w.text:
                continue
            t = render(w.text, w.size, w.xs, w.fill)
            if w.rot:
                t = t.rotate(-90, expand=True)
            bx0, by0, bx1, by1 = w.box
            x, y = bx0 + (bx1 - bx0 - t.width) // 2, by0 + (by1 - by0 - t.height) // 2
            tl = Image.new("RGBA", img.size, (0, 0, 0, 0))
            tl.alpha_composite(t, (x, y))
            s = min(1.0, max(0.3, w.size / 70))
            ta = tl.getchannel("A")
            soft = ta.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1.5 + 2.5 * s)).point(lambda v: min(255, v * 2))
            core = ta.filter(ImageFilter.MaxFilter(5)).point(lambda v: 255 if v else 0)  # opaque ring: edge pixels stay opaque grey
            halo = np.maximum.reduce([halo, np.array(soft), np.array(core)])
            layer.alpha_composite(tl)
        halo[~clip | art] = 0
        hl = Image.new("RGBA", img.size, (255, 255, 255, 0))
        hl.putalpha(Image.fromarray(halo))
        la = np.array(layer)
        la[~clip, 3] = 0
        out.alpha_composite(hl)
        out.alpha_composite(Image.fromarray(la))
        rr = [(x0, y0, x1 - x0, y1 - y0) for x0, y0, x1, y1 in rects]
        png = gfx.save(out, "dungeon_titles", path, rr)
        rows.append((path, png, " / ".join(w.text.replace("\n", " ") if w.text else "-" for w in words)))
        print(n, [(w.text, w.size, w.xs, w.rot) for w in words if w.text])
    if not only:
        gfx.write_tsv("dungeon_titles", rows)


if __name__ == "__main__":
    main()
