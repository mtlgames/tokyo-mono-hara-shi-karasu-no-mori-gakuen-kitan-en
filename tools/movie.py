"""movie.py: English chapter title cards (STORYTITLE01-10.PMF) -> gfx/movie/*.PMF, spliced in by build.py.

    python -X utf8 tools/movie.py [--only 01] [--keep]     # writes gfx/movie/STORYTITLEnn.PMF
    python -X utf8 tools/movie.py --test                    # self-check of the column finder and the reveal curve

Each card is ~270 frames: a red city backdrop, then vertical brush calligraphy fading in column by column (right
column 第N話, then two title columns) and out again. Per frame: the Japanese ink (cream: high green and blue, the
backdrop is red/black) is found in the columns' rects, those rects are replaced by a clean plate (a frame before any
text, scaled to the frame's brightness so fades still work), and the English lines are drawn with each line's alpha
following its Japanese column's ink. Then x264 re-encodes with the original keyframes and `pmf.swap` pads every
frame to its original size, so the PSMF container is untouched (tools/pmf.py). Videos only: these PMFs carry no audio.
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import pmf  # noqa: E402
from PIL import ImageDraw, ImageFont  # noqa: E402

MOVIE = ROOT / "work" / "iso" / "PSP_GAME" / "USRDIR" / "MOVIE"
OUT = ROOT / "gfx" / "movie"
WORK = ROOT / "work" / "movie"
FONT = str(ROOT / "fonts" / "KaushanScript-Regular.ttf")
CREAM = (246, 238, 222)

# card -> (chapter label, title lines); titles translated from the cards (docs/decisions.md D22)
CARDS = {
    "01": ("Chapter 1", ["The Lightning", "Transfer Student"]),
    "02": ("Chapter 2", ["The Swordsman of", "the Six Paths"]),
    "03": ("Chapter 3", ["Envoy of the", "East Wind"]),
    "04": ("Chapter 4", ["The Witch of", "the Heat Haze"]),
    "05": ("Chapter 5", ["The Hour of", "Awakening"]),
    "06": ("Chapter 6", ["Love Like", "Banked Embers"]),
    "07": ("Chapter 7", ["The Pride of", "a Late Bloom"]),
    "08": ("Chapter 8", ["A Fleeting", "Future"]),
    "09": ("Chapter 9", ["Herald of the", "Dark South Wind"]),
    "10": ("Final Chapter", ["A Grand Finale", "Woven of Cards"]),
}


def ink(a):
    """0..1 Japanese ink weight of an RGB frame array: cream text has high G and B, the backdrop doesn't."""
    gb = np.minimum(a[..., 1], a[..., 2]).astype(np.float32)
    return np.clip((gb - 100) / 70, 0, 1)


def columns(peak, min_gap=6, min_w=12):
    """Column x ranges (x0, x1) of the ink, right to left, from the max-over-time ink map."""
    prof = (peak > 0.5).sum(axis=0) > 3
    cols, x = [], 0
    while x < len(prof):
        if prof[x]:
            s = x
            gap = 0
            while x < len(prof) and gap < min_gap:
                gap = 0 if prof[x] else gap + 1
                x += 1
            e = x - gap
            if e - s >= min_w:
                cols.append((s, e))
        x += 1
    return sorted(cols, reverse=True)


def line(text, size, alpha, shadow=(120, 10, 10)):
    """One line of brush text with a soft dark-red glow, as an RGBA layer at the given alpha."""
    f = ImageFont.truetype(FONT, size)
    x0, y0, x1, y1 = f.getbbox(text)
    pad = 8
    layer = Image.new("RGBA", (x1 - x0 + 2 * pad + size // 4, y1 - y0 + 2 * pad), (0, 0, 0, 0))  # italic overhang
    glow = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).text((pad - x0, pad - y0), text, font=f, fill=shadow + (255,), stroke_width=3,
                              stroke_fill=shadow + (255,))
    glow = glow.filter(ImageFilter.GaussianBlur(3))
    layer.alpha_composite(glow)
    ImageDraw.Draw(layer).text((pad - x0, pad - y0), text, font=f, fill=CREAM + (255,))
    if alpha < 1:
        layer.putalpha(layer.getchannel("A").point(lambda v: int(v * alpha)))
    return layer


def lowpass(d, w, block=8, passes=6):
    """Normalized convolution: d (h, w, 3, already multiplied by the weights w) averaged over weighted pixels in
    8x8 blocks, blurred, back to full size. Fills the zero-weight boxes from around them."""
    h, wd = w.shape
    bh, bw = h // block, wd // block
    num = d[:bh * block, :bw * block].reshape(bh, block, bw, block, 3).sum(axis=(1, 3))
    den = w[:bh * block, :bw * block].reshape(bh, block, bw, block).sum(axis=(1, 3))[..., None]
    for _ in range(passes):                          # 3x3 box blur, edge-padded
        num = sum(np.pad(num, ((1, 1), (1, 1), (0, 0)), mode="edge")[y:y + bh, x:x + bw]
                  for y in range(3) for x in range(3))
        den = sum(np.pad(den, ((1, 1), (1, 1), (0, 0)), mode="edge")[y:y + bh, x:x + bw]
                  for y in range(3) for x in range(3))
    small = num / np.maximum(den, 1e-3)
    return np.dstack([np.asarray(Image.fromarray(small[..., c].astype(np.float32), "F").resize((wd, h),
                      Image.BILINEAR)) for c in range(3)])


def curve(weights):
    """Per-frame alpha from a column's ink sum: 0..1 of its own maximum, smoothed by 3 frames."""
    w = np.asarray(weights, np.float32)
    w = np.convolve(w, np.ones(3) / 3, mode="same")
    m = w.max()
    return np.clip(w / m * 1.15, 0, 1) if m > 0 else w


def decode(src, d):
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(src), "-fps_mode", "passthrough",
                    str(d / "%04d.png")], check=True)
    return sorted(d.glob("*.png"))


def mist(a, grow=9):
    """Soft mask of the pale pixels (ink, the white mist glyphs rise from) of an RGB frame, grown by grow px."""
    gb = np.minimum(a[..., 1], a[..., 2]).astype(np.float32)
    m = Image.fromarray((np.clip((gb - 45) / 50, 0, 1) * 255).astype(np.uint8))
    return np.asarray(m.filter(ImageFilter.MaxFilter(grow)).filter(ImageFilter.GaussianBlur(3)), np.float32) / 255


def load(card, n):
    return np.asarray(Image.open(WORK / card / "orig" / f"{n + 1:04d}.png").convert("RGB"))


def prep(card, frames):
    """Columns, their rects and reveal curves, and the soft box mask of one card."""
    arr = [np.asarray(Image.open(f).convert("RGB")) for f in frames]
    inks = [ink(a) for a in arr]
    shown = [i for i in inks if i.sum() > 200]
    peak = np.mean([i > 0.5 for i in shown], axis=0) * 2   # ink in >= 1/4 of the text frames (flashes are not)
    cols = columns(peak)
    if len(cols) < 3:
        raise ValueError(f"{card}: found columns {cols}")
    cols = cols[:3]
    h = arr[0].shape[0]
    # rect of each column's ink (y range from the peak map), grown for the glow
    rects = []
    for x0, x1 in cols:
        ys = np.nonzero((peak[:, x0:x1] > 0.5).any(axis=1))[0]
        rects.append((max(x0 - 12, 0), max(ys[0] - 12, 0), min(x1 + 12, arr[0].shape[1]), min(ys[-1] + 12, h)))
    area = np.zeros(peak.shape, np.float32)          # where the text and its white reveal mist can be
    area[:, max(min(r[0] for r in rects) - 40, 0):] = 1
    boxes = np.zeros(peak.shape, np.uint8)           # the glyphs and their dark outlines
    for x0, y0, x1, y1 in rects:
        boxes[y0:y1, x0:x1] = 255
    boxes = np.asarray(Image.fromarray(boxes).filter(ImageFilter.GaussianBlur(6)), np.float32) / 255
    alphas = [curve([i[:, x0:x1].sum() for i in inks]) for x0, x1 in cols]
    text = [inks[n].sum() >= 1 or any(al[n] > 0 for al in alphas) for n in range(len(arr))]
    return dict(rects=rects, area=area, boxes=boxes, alphas=alphas, text=text)


def render(cards, info, nframes):
    """All cards' frames: the Japanese and its mist replaced by a clean backdrop, the English drawn on top.
    The ten cards share one backdrop animation frame for frame, so the backdrop at frame n is the weighted mean of
    the cards' frame n, each pixel weighted by how far it is from any pale (text or mist) pixel in that card."""
    for card in cards:
        (WORK / card / "en").mkdir(parents=True, exist_ok=True)
    for n in range(nframes):
        need = [c for c in cards if info[c]["text"][n]]
        for c in cards:
            if c not in need:                         # no text: the frame as it was (keeps it small)
                Image.fromarray(load(c, n)).save(WORK / c / "en" / f"{n + 1:04d}.png")
        if not need:
            continue
        arrs = {c: load(c, n) for c in CARDS}
        masks = {c: np.maximum(mist(a), info[c]["boxes"] * info[c]["text"][n]) for c, a in arrs.items()}
        wsum = np.zeros(masks["01"].shape, np.float32)
        acc = np.zeros(arrs["01"].shape, np.float32)
        for c, a in arrs.items():
            w = (1 - masks[c]) ** 4 + 1e-4
            wsum += w
            acc += a * w[..., None]
        plate = acc / wsum[..., None]
        for c in need:
            i = info[c]
            r = (masks[c] * i["area"])[..., None]
            img = arrs[c] * (1 - r) + plate * r
            im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
            label, title = CARDS[c]
            right, y = i["rects"][0][2] - 4, i["rects"][0][1] + 6   # label at the 第N話 column's top, right-aligned
            for k, (t, size) in enumerate([(label, 22)] + [(t, 34) for t in title]):
                layer = line(t, size, float(i["alphas"][min(k, 2)][n]))
                im.alpha_composite(layer, (right - layer.width, y))
                y += layer.height + (14 if k == 0 else 2)
            im.convert("RGB").save(WORK / c / "en" / f"{n + 1:04d}.png")


def encode(png_dir, keys, crf, out):
    expr = "+".join(f"eq(n,{k})" for k in keys)
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-framerate", "30000/1001",
                    "-i", str(png_dir / "%04d.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "main",
                    "-level", "2.1", "-bf", "0", "-refs", "1", "-crf", str(crf), "-colorspace", "smpte170m",
                    "-force_key_frames", f"expr:{expr}",
                    "-x264-params", "keyint=9999:min-keyint=1:scenecut=0:aud=1:open-gop=0",
                    "-bsf:v", "filter_units=remove_types=6", "-f", "h264", str(out)], check=True)
    return pmf.access_units(out.read_bytes())


def build(cards, keep=False):
    info, nframes = {}, None
    for card in CARDS:                                # every card: they are each other's backdrop source
        src = MOVIE / f"STORYTITLE{card}.PMF"
        frames = decode(src, WORK / card / "orig")
        nframes = nframes or len(frames)
        if len(frames) != nframes:
            raise ValueError(f"{card}: {len(frames)} frames, card 01 has {nframes}")
        info[card] = prep(card, frames)
    render(cards, info, nframes)
    for card in cards:
        encode_card(card, info[card]["rects"])
    if not keep:
        for card in CARDS:
            shutil.rmtree(WORK / card / "orig")


def encode_card(card, rects):
    src = MOVIE / f"STORYTITLE{card}.PMF"
    data = src.read_bytes()
    old = pmf.access_units(pmf.es(data))
    keys = [i for i, au in enumerate(old) if pmf.is_key(au)]
    d = WORK / card
    for crf in range(18, 46, 3):
        new = encode(d / "en", keys, crf, d / "en.264")
        over = [i for i, (o, n) in enumerate(zip(old, new)) if len(n) > len(o)]
        if len(new) == len(old) and not over:
            break
        print(f"  {card} crf {crf}: {len(over)} frames over their original size",
              [(i, len(new[i]), len(old[i])) for i in over[:4]] if len(new) == len(old) else len(new))
    else:
        raise ValueError(f"{card}: frames still too big at crf {crf}")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / src.name).write_bytes(pmf.swap(data, new))
    print(f"{src.name}: crf {crf}, columns {rects}")


def selftest():
    peak = np.zeros((40, 100), np.float32)
    peak[5:30, 80:95] = 1
    peak[5:35, 40:70] = 1
    peak[5:35, 10:30] = 1
    peak[10:12, 34:36] = 1                       # a speck between columns is no column
    assert columns(peak) == [(80, 95), (40, 70), (10, 30)], columns(peak)
    c = curve([0, 0, 5, 10, 10, 10, 0])
    assert c.max() == 1 and c[0] == 0
    src = MOVIE / "STORYTITLE01.PMF"
    if src.exists():                                 # swapping in the same frames gives the file back
        data = src.read_bytes()
        assert pmf.swap(data, pmf.access_units(pmf.es(data))) == data
    print("movie self-test ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--keep", action="store_true", help="keep the decoded original frames")
    ap.add_argument("--test", action="store_true")
    a = ap.parse_args()
    if a.test:
        return selftest()
    build(a.only or list(CARDS), a.keep)


if __name__ == "__main__":
    sys.exit(main())
