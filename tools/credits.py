"""credits.py: English staff credits in the ending movies -> gfx/movie/<MOVIE>.PMF, spliced in by build.py.

    python -X utf8 tools/credits.py scan [MOVIE..]    # find the text runs -> work/movie/credits/ (labelled sheets)
    python -X utf8 tools/credits.py build [MOVIE..]   # render, re-encode, swap -> gfx/movie/
    python -X utf8 tools/credits.py --test            # self-check of the run finder

Two kinds of credits (docs/re/graphics.md "Outside the GIMs"):
- ROLL (BADENDLOST, BADENDSEAL, TRUEEND): one staff roll scrolling up a black panel on the left at a constant
  speed (measured per movie, ~0.92-0.94 px/frame). The roll is stitched from the frames, its text runs (one line,
  split at wide gaps) are keyed roll:N in reading order; the three movies show the same roll.
- CARDS (EPSOTD_END01-09): blocks of lines on the right half over falling red cards (black and dark red, G=B~0)
  and tilted sepia photos (left). Each card slides in from the left (~20 frames, eased), holds, then drifts out to
  the right and off screen; the closing 企画 アトラス card fades in mid-screen. A card is found where it holds
  still, keyed by its first sighting, <MOVIE>@<hold start>, and found again in the other movies by its text mask;
  then followed frame by frame out of the hold (Tracker: x shift by correlation over its text rows, alpha).
English for every run is in gfx/credits/credits.tsv (key, jp, en; en "-" = erase only, "=" = leave as is). Per frame the Japanese ink in each
run box is filled from around it (normalized Gaussian convolution: the backdrop there is flat black / dark red /
the panel's dark gradient), then the English is drawn left-aligned in the box at the Japanese line's height, faded
with the Japanese ink (cards) or scrolled with sub-pixel steps (roll). Video only: `pmf.swap` keeps the audio and
the container byte for byte.
"""
import argparse
import csv
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import binary_dilation, gaussian_filter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import pmf  # noqa: E402

MOVIE = ROOT / "work" / "iso" / "PSP_GAME" / "USRDIR" / "MOVIE"
OUT = ROOT / "gfx" / "movie"
WORK = ROOT / "work" / "movie" / "credits"
TSV = ROOT / "gfx" / "credits" / "credits.tsv"   # not gfx/*.tsv: gfx.py reads those as GIM groups
FONT = str(ROOT / "fonts" / "LiberationSerif-Regular.ttf")
W, H = 480, 272
ROLL = ["BADENDLOST", "BADENDSEAL", "TRUEEND"]
CARDS = [f"EPSOTD_END{n:02d}" for n in range(1, 10)]
BAND = 200            # roll: the panel and its gradient edge, x < BAND
PANEL = 150           # roll: English must end left of this (the panel is pure black up to ~145)
CARD_X = 255          # cards: a held card's text is right of this (the tilted photos reach ~250)
LOGO_X = 150          # cards: the closing card's text is right of this
GAP = 12              # px of blank that splits a line into runs


def frames(src, every=1):
    """RGB frames of a movie as (n, uint8 array), decoded through an ffmpeg pipe."""
    p = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(src), "-fps_mode",
                          "passthrough", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    n = 0
    while True:
        b = p.stdout.read(W * H * 3)
        if len(b) < W * H * 3:
            break
        if n % every == 0:
            yield n, np.frombuffer(b, np.uint8).reshape(H, W, 3)
        n += 1
    p.wait()


def runs(mask, gap=GAP, x_off=0, y_off=0):
    """Text runs of a bool mask: line bands (rows with ink, 2-row gaps bridged), split at blank gaps > gap.
    [(x0, y0, x1, y1)] in reading order (top to bottom, left to right), end-exclusive."""
    rows = mask.any(axis=1)
    out, y = [], 0
    while y < len(rows):
        if not rows[y]:
            y += 1
            continue
        y0, blank = y, 0
        while y < len(rows) and blank <= 2:
            blank = 0 if rows[y] else blank + 1
            y += 1
        y1 = y - blank
        cols = mask[y0:y1].any(axis=0)
        x = 0
        while x < len(cols):
            if not cols[x]:
                x += 1
                continue
            x0, blank = x, 0
            while x < len(cols) and blank <= gap:
                blank = 0 if cols[x] else blank + 1
                x += 1
            x1 = x - blank
            if (x1 - x0) * (y1 - y0) >= 6:            # specks (noise, a lone dot) are no run
                ys = np.nonzero(mask[y0:y1, x0:x1].any(axis=1))[0]
                out.append((x0 + x_off, y0 + ys[0] + y_off, x1 + x_off, y0 + ys[-1] + 1 + y_off))
    return out


# ---------------------------------------------------------------- roll

def roll_scan(name):
    """Speed (px/frame) and stitched roll (gray, BAND wide) of a ROLL movie. Roll row Y shows at frame row
    Y - v * n."""
    band = {n: f[:, :BAND].min(axis=2) for n, f in frames(MOVIE / f"{name}.PMF", every=2)}  # min: not the orange sky
    ns = sorted(band)
    lit = [n for n in ns if (band[n][:, :PANEL] > 150).sum() > 300]

    def shift(a, b, lo=150, hi=215):
        a, b = a[:, :130].astype(np.float32), b[:, :130].astype(np.float32)
        r = np.array([((a[d:] - b[:H - d]) ** 2).mean() for d in range(lo, hi)])
        i = int(np.clip(np.argmin(r), 1, len(r) - 2))
        return lo + i + 0.5 * (r[i - 1] - r[i + 1]) / (r[i - 1] - 2 * r[i] + r[i + 1])

    pairs = [n for n in lit[::20] if n + 200 in band and (band[n + 200][:, :PANEL] > 150).sum() > 300]
    v = float(np.median([shift(band[n], band[n + 200]) / 200 for n in pairs]))
    total = int(v * ns[-1]) + H
    roll = np.zeros((total, BAND), np.uint8)
    best = np.full(total, 9.0)
    for n in ns:                                       # each roll row from the frame where it sat on a whole pixel
        s = v * n
        fr = abs(s - round(s))
        for r in range(100, 180):
            y = int(round(s)) + r
            if y < total and fr < best[y]:
                best[y], roll[y] = fr, band[n][r]
    return v, roll


def roll_runs(roll):
    m = roll[:, :BAND] > 90
    m[:, PANEL + 28:] = False                          # the longest lines end ~175; the sky starts ~185
    return runs(m)


# ---------------------------------------------------------------- cards

def ink(f):
    """Card text weight (uint8 HxW): near-neutral pixels, min(G, B) where G ~ B and R >= G (white ink over black /
    dark red, whose G = B ~ 0; the sepia photos have G > B, END06-07's teal cards and photos R < G = B)."""
    r, g, b = (f[..., i].astype(np.int16) for i in range(3))
    return np.where((np.abs(g - b) < 16) & (r + 16 >= g), np.minimum(g, b), 0).astype(np.uint8)


def card_holds(name):
    """[(first, last, ref)] of the stretches (15+ frames) where a card stands still: successive frames' ink right
    of CARD_X alike (normalized correlation > 0.97). ref: the brightest frame's ink, from CARD_X on, or from
    LOGO_X on when its text reaches past CARD_X (the closing 企画 アトラス card sits mid-screen, with no photos)."""
    out, cur, prev = [], None, None
    for n, f in frames(MOVIE / f"{name}.PMF"):
        full = ink(f)
        g = full.copy()
        g[:, :CARD_X] = 0
        a = g.astype(np.float32)
        s = float(a.sum())
        still = prev is not None and s > 12000 and \
            float((a * prev).sum()) / np.sqrt(float((a * a).sum()) * float((prev * prev).sum()) + 1e-6) > 0.97
        if still:
            if cur is None:
                cur = [n - 1, n, -1.0, None]
            cur[1] = n
            if s > cur[2]:
                if (g[:, CARD_X] > 60).any():
                    g = full
                    g[:, :LOGO_X] = 0
                cur[2], cur[3] = s, g
        else:
            if cur is not None and cur[1] - cur[0] >= 15:
                out.append((cur[0], cur[1], cur[3]))
            cur = None
        prev = a
    if cur is not None and cur[1] - cur[0] >= 15:
        out.append((cur[0], cur[1], cur[3]))
    return out


def same_card(a, ra, b, rb):
    """Two cards (ref ink, runs) show the same text: the same run boxes (+-2 px) and IoU of their dilated
    masks > 0.75 (same-length names in the same spots differ in their glyphs)."""
    if len(ra) != len(rb) or np.abs(np.array(ra) - np.array(rb)).max() > 2:
        return False
    ma, mb = binary_dilation(a > 60, iterations=1), binary_dilation(b > 60, iterations=1)
    return (ma & mb).sum() / max((ma | mb).sum(), 1) > 0.75


def card_index(names):
    """{movie: [(key, first, last, runs, ref)]}: every held card of the movies, keyed by its first sighting in
    CARDS order (scanning all of CARDS keeps the keys stable whichever movies are built). A card shown twice in a
    row (a hold broken by a passing photo) is one card."""
    seen, out = [], {}
    for name in CARDS:
        out[name] = []
        for first, last, ref in card_holds(name):
            rs = runs(ref > 60)
            if not rs:
                continue
            key = next((k for k, im, r in seen if same_card(im, r, ref, rs)), None)
            if key is None:
                key = f"{name}@{first:04d}"
                seen.append((key, ref, rs))
            prev = out[name][-1] if out[name] else None
            if prev and prev[0] == key and first - prev[2] < 30:
                out[name][-1] = (key, prev[1], last, prev[3], prev[4])
            else:
                out[name].append((key, first, last, rs, ref))
    return {n: out[n] for n in names}


DX = (-330, 200)     # cards: x shifts from the hold place searched while a card slides in / drifts out
REACH = 90            # cards: frames before / after a hold that the card may still show (slides ~20, fades)


class Tracker:
    """Finds one card in a frame's ink: the x shift dx with the best normalized correlation of the card's ref
    over its text rows (cards only slide sideways), and its brightness alpha against the ref."""
    N = 1024           # FFT width: > W + the widest card, so no shift wraps onto another

    def __init__(self, ref, rs):
        ys = sorted({y for b in rs for y in range(max(b[1] - 1, 0), min(b[3] + 1, H))})
        self.ys = np.array(ys)
        sup = (ref > 30)[self.ys]                     # r lives inside sup, so score <= 1 (Cauchy-Schwarz)
        r = ref[self.ys].astype(np.float32) * sup
        self.R = np.conj(np.fft.rfft(r, self.N, axis=1))
        sup = sup.astype(np.float32)
        self.S = np.conj(np.fft.rfft(sup, self.N, axis=1))
        self.dx = np.arange(DX[0], DX[1] + 1)
        cum = np.r_[0, np.cumsum((r * r).sum(axis=0))]   # ref energy still on screen at each shift
        self.rr = cum[np.clip(W - self.dx, 0, W)] - cum[np.clip(-self.dx, 0, W)]

    def __call__(self, g):
        """(dx, alpha, score) for frame ink g."""
        f = g[self.ys].astype(np.float32)
        c = np.fft.irfft((np.fft.rfft(f, self.N, axis=1) * self.R).sum(axis=0), self.N)[self.dx % self.N]
        e = np.fft.irfft((np.fft.rfft(f * f, self.N, axis=1) * self.S).sum(axis=0), self.N)[self.dx % self.N]
        rr = np.maximum(self.rr, 1)
        score = c / np.sqrt(np.maximum(e, 1) * rr) * (self.rr > self.rr.max() / 5)
        i, i0 = int(np.argmax(score)), -DX[0]
        return int(self.dx[i]), float(c[i] / rr[i]), float(score[i]), float(c[i0] / rr[i0])


def card_track(name, cards):
    """{frame: [(card index, dx, alpha)]}: each card followed out from its hold, frame by frame, while it still
    matches (score > 0.6) and moves on smoothly (slides in from the left, drifts out to the right: dx never
    turns back, steps < 45 px)."""
    trs = [Tracker(ref, rs) for _, _, _, rs, ref in cards]
    near = {}
    for n, f in frames(MOVIE / f"{name}.PMF"):
        hit = [i for i, c in enumerate(cards) if c[1] - REACH <= n <= c[2] + REACH]
        if hit:
            g = ink(f)
            near[n] = {i: trs[i](g) for i in hit}
    out = {}
    for i, (_, first, last, _, _) in enumerate(cards):
        mid = (first + last) // 2
        for step, stop in ((-1, first - REACH - 1), (1, last + REACH + 1)):
            prev = 0
            for n in range(mid, stop, step):
                if n not in near:
                    break
                dx, al, sc, al0 = near[n][i]
                if sc < 0.6 or al < 0.03 or abs(dx - prev) > 45 or (dx - prev) * step < -1:
                    if not first <= n <= last:
                        break
                    dx, al = 0, al0                        # held: the card is there whatever passes over it
                if n != mid or step < 0:
                    out.setdefault(n, []).append((i, dx, min(al, 1.0)))
                prev = dx
    return out


# ---------------------------------------------------------------- text

def table():
    if not TSV.exists():
        return {}
    with TSV.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.reader(fh, delimiter="\t", quoting=csv.QUOTE_NONE))   # "Kirifuda" keeps its quotes
    for r in rows:
        if len(r) != 3:
            raise ValueError(f"{TSV.name}: row {r} has {len(r)} columns, want key, jp, en")
    return {r[0]: r[2] for r in rows[1:]}


def layer(text, box, limit, colour, size=None):
    """RGBA image of one English run, left-aligned at the box, as tall as the Japanese line (or size px), shrunk
    to fit limit (the x it must end before). Returns (image, x, y)."""
    x0, y0, x1, y1 = box
    h = y1 - y0
    size = size or (15 if h >= 14 else 13 if h == 13 else 11)   # names / section heads / roles, notes
    f = ImageFont.truetype(FONT, size)
    l, t, r, b = f.getbbox(text)
    im = Image.new("L", (r - l + 2, h + size), 0)
    ImageDraw.Draw(im).text((-l + 1, 0), text, font=f, fill=255)
    if x0 + im.width > limit:                          # too wide: condense rather than shrink
        im = im.resize((max(limit - x0, 8), im.height), Image.LANCZOS)
    cap = f.getbbox("H")
    y = y0 + (h - (cap[3] - cap[1])) // 2 - cap[1]     # cap height centred on the Japanese line
    if abs(x0 + x1 - W) < 24:                          # a line centred on screen stays centred
        x0 = (x0 + x1 - im.width) // 2 + 1
    return im, x0 - 1, y, colour


def fill(img, mask, box):
    """img (float HxWx3) with mask (0..1) pixels replaced by the weighted mean of the unmasked ones around them,
    inside box (grown so the blur sees context)."""
    x0, y0, x1, y1 = box
    x0, y0, x1, y1 = max(x0 - 8, 0), max(y0 - 8, 0), min(x1 + 8, W), min(y1 + 8, H)
    m = mask[y0:y1, x0:x1]
    if not m.any():
        return
    w = 1 - m
    sub = img[y0:y1, x0:x1]
    den = gaussian_filter(w, 2.5) + 1e-4
    for c in range(3):
        num = gaussian_filter(sub[..., c] * w, 2.5)
        sub[..., c] = sub[..., c] * w + num / den * m


def text_mask(f, box, lo):
    """0..1 weight of near-white ink in a box of an RGB frame (min channel above lo), grown by a pixel."""
    x0, y0, x1, y1 = box
    m = np.zeros((H, W), np.float32)
    x0, y0, x1, y1 = max(x0 - 3, 0), max(y0 - 3, 0), min(x1 + 3, W), min(y1 + 3, H)
    if x1 <= x0 or y1 <= y0:
        return m
    mn = f[y0:y1, x0:x1].min(axis=2).astype(np.float32)
    w = np.clip((mn - lo) / 30, 0, 1)
    w = np.maximum(w, binary_dilation(w > 0.3, iterations=1) * 1.0)
    m[y0:y1, x0:x1] = w
    return m


def stamp(img, lay, alpha=1.0, dy=0.0):
    """Composite a white-ish run layer onto img (float), at sub-pixel vertical offset dy."""
    im, x, y, colour = lay
    a = np.asarray(im, np.float32) / 255 * alpha
    if dy:
        a = (1 - dy) * a + dy * np.vstack([np.zeros((1, a.shape[1]), np.float32), a[:-1]])
    ys, xs = slice(max(y, 0), min(y + a.shape[0], H)), slice(max(x, 0), min(x + a.shape[1], W))
    if ys.stop <= ys.start or xs.stop <= xs.start:
        return
    a = a[ys.start - y:ys.stop - y, xs.start - x:xs.stop - x][..., None]
    img[ys, xs] = img[ys, xs] * (1 - a) + np.array(colour, np.float32) * a


# ---------------------------------------------------------------- encode

def encode(src, keys, crf, out):
    """x264 with IDR frames exactly at keys, given as times (ffmpeg's force_key_frames expr overflows at ~130
    keys; the input is 30000/1001 fps, a key is forced on the first frame at or after its time)."""
    times = ",".join(f"{max(k * 1001 / 30000 - 0.005, 0):.4f}" for k in keys)
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(src), "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", "-profile:v", "main", "-level", "2.1", "-bf", "0", "-refs", "1",
                    "-crf", str(crf), "-colorspace", "smpte170m", "-force_key_frames", times,
                    "-x264-params", "keyint=9999:min-keyint=1:scenecut=0:aud=1:open-gop=0",
                    "-bsf:v", "filter_units=remove_types=6", "-f", "h264", str(out)], check=True)
    return pmf.access_units(out.read_bytes())


def write(name, render):
    """Render every frame through render(n, frame) into a lossless intermediate, then x264 at the lowest crf
    where every frame fits its original size, and swap the stream into the PMF."""
    src = MOVIE / f"{name}.PMF"
    WORK.mkdir(parents=True, exist_ok=True)
    mid = WORK / f"{name}.mkv"
    enc = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt",
                            "rgb24", "-s", f"{W}x{H}", "-framerate", "30000/1001", "-i", "-", "-c:v", "ffv1",
                            str(mid)], stdin=subprocess.PIPE)
    changed = []
    for n, f in frames(src):
        out = render(n, f)
        changed.append(out is not f and not np.array_equal(out, f))
        enc.stdin.write(out.tobytes())
    enc.stdin.close()
    if enc.wait():
        raise RuntimeError(f"{name}: ffv1 encode failed")
    data = src.read_bytes()
    old = pmf.access_units(pmf.es(data))
    keys = [i for i, au in enumerate(old) if pmf.is_key(au)]
    # GOPs (IDR to IDR, each with its own SPS/PPS) with no frame drawn on keep their original access units
    gop = np.searchsorted(keys, np.arange(len(old)), side="right") - 1
    redo = {g for g, c in zip(gop, changed) if c}
    # each GOP takes the lowest crf at which all its frames fit their original sizes (GOPs are independent)
    new, todo, used = list(old), set(redo), {}
    for crf in range(16, 52, 2):
        enc = encode(mid, keys, crf, WORK / f"{name}.264")
        if len(enc) != len(old):
            raise ValueError(f"{name}: x264 gave {len(enc)} frames, want {len(old)}")
        for g in sorted(todo):
            idx = [i for i in range(len(old)) if gop[i] == g]
            if all(len(enc[i]) <= len(old[i]) for i in idx):
                for i in idx:
                    new[i] = enc[i]
                todo.discard(g)
                used[crf] = used.get(crf, 0) + 1
        if not todo:
            break
    else:
        raise ValueError(f"{name}: GOPs {sorted(todo)} still too big at crf {crf}")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / src.name).write_bytes(pmf.swap(data, new))
    mid.unlink()
    print(f"{src.name}: GOPs per crf {used}, {len(keys) - len(redo)} of {len(keys)} GOPs kept as they were")


def match_runs(ref, rs, tol=4):
    """Keys roll:N of runs rs from the reference roll's runs ref (BADENDLOST): the three rolls show the same
    text from a different start row, so take the y offset most box pairs agree on, then match each box (x0, x1,
    y0 within tol). None for a run with no counterpart (scenery before the roll, the closing logo)."""
    votes = {}
    for a in ref[:40]:
        for b in rs[:60]:
            if abs(a[0] - b[0]) <= 1 and abs(a[2] - b[2]) <= 1:
                votes[a[1] - b[1]] = votes.get(a[1] - b[1], 0) + 1
    off = max(votes, key=votes.get)
    keys = []
    for b in rs:
        hit = [i for i, a in enumerate(ref) if abs(a[0] - b[0]) <= tol and abs(a[2] - b[2]) <= tol
               and abs(a[1] - b[1] - off) <= tol]
        keys.append(f"roll:{hit[0]:03d}" if len(hit) == 1 else None)
    return keys


def build_roll(name, text):
    v, roll = roll_scan(name)
    rs = roll_runs(roll)
    keys = [f"roll:{i:03d}" for i in range(len(rs))]
    if name != ROLL[0]:
        keys = match_runs(roll_runs(roll_scan(ROLL[0])[1]), rs)
        print(f"  {name}: {keys.count(None)} runs with no counterpart in {ROLL[0]} (kept):",
              [b for b, k in zip(rs, keys) if k is None])
    lays = []
    for key, box in zip(keys, rs):
        en = text.get(key, "") if key else "="
        if not en:
            raise KeyError(f"{name}: {key} has no English in {TSV.name}")
        lays.append(en if en in "-=" else layer(en, box, PANEL + 22, (238, 238, 238)))  # the JP reaches ~175

    def render(n, f):
        img = f.astype(np.float32)
        s = v * n
        iy, dy = int(np.floor(s)), s - np.floor(s)
        mask = np.zeros((H, W), np.float32)
        live = [(box, lay) for box, lay in zip(rs, lays)
                if lay != "=" and box[3] - s > -4 and box[1] - s < H + 4]
        for box, _ in live:
            b = (box[0], box[1] - iy - 1, box[2], box[3] - iy + 1)
            mask = np.maximum(mask, text_mask(f, b, 6))
        for box, _ in live:
            fill(img, mask, (box[0], box[1] - iy - 1, box[2], box[3] - iy + 1))
        for box, lay in live:
            if lay != "-":
                im, x, y, c = lay
                stamp(img, (im, x, y - iy - 1, c), 1.0, 1 - dy)
        return np.clip(img + 0.5, 0, 255).astype(np.uint8)

    write(name, render)


def shift_x(a, dx):
    """a (HxW) moved dx px right, zeros shifted in."""
    out = np.zeros_like(a)
    if dx >= 0:
        out[:, dx:] = a[:, :W - dx]
    else:
        out[:, :W + dx] = a[:, -dx:]
    return out


def build_cards(name, cards, text):
    plan = []                                          # (runs, layers, erase mask at the hold place)
    for key, first, last, rs, ref in cards:
        lays = []
        for i, box in enumerate(rs):
            en = text.get(f"{key}:{i}", "")
            if not en:
                raise KeyError(f"{name}: {key}:{i} has no English in {TSV.name}")
            nxt = [b[0] for b in rs if b[0] > box[2] and b[1] < box[3] and b[3] > box[1]]
            size = 15 if box[3] - box[1] >= 15 else 12  # two sizes on a card (JP 16-18 px names, 11-14 px roles)
            lays.append(en if en in "-=" else layer(en, box, min(nxt + [W - 4]) - 4, (235, 235, 235), size))
        keep = [i for i, lay in enumerate(lays) if lay != "="]
        erase = np.zeros((H, W), bool)
        for i in keep:
            x0, y0, x1, y1 = rs[i]
            erase[max(y0 - 3, 0):y1 + 3, max(x0 - 3, 0):x1 + 3] = True
        erase &= binary_dilation(ref > 12, iterations=2)
        plan.append(([rs[i] for i in keep], [lays[i] for i in keep], erase.astype(np.float32)))
    track = card_track(name, cards)
    last_dx = {}

    def render(n, f):
        if n not in track:
            return f
        img = f.astype(np.float32)
        for i, dx, al in track[n]:
            rs, lays, erase = plan[i]
            if not rs:
                continue
            v = abs(dx - last_dx.get(i, dx))           # px moved since the last frame: the JP is smeared that far
            last_dx[i] = dx
            m = shift_x(erase, dx)
            if v > 1:
                m = np.maximum(m, binary_dilation(m > 0, np.ones((1, 2 * (v // 2) + 1), bool)).astype(np.float32))
            for x0, y0, x1, y1 in rs:
                fill(img, m, (max(x0 + dx - v, 0), y0, min(x1 + dx + v, W), y1))
            for (x0, y0, x1, y1), lay in zip(rs, lays):
                if lay != "-" and al > 0.01:
                    im, x, y, c = lay
                    stamp(img, (im, x + dx, y, c), al)
        return np.clip(img + 0.5, 0, 255).astype(np.uint8)

    write(name, render)


# ---------------------------------------------------------------- scan output

def sheet(img, rs, keys, out, zoom=2):
    """Gray image with each run boxed and labelled with its key, zoomed, for transcription."""
    im = Image.fromarray(img).convert("RGB").resize((img.shape[1] * zoom, img.shape[0] * zoom), Image.NEAREST)
    pad = Image.new("RGB", (im.width + 90, im.height), (0, 0, 40))
    pad.paste(im, (90, 0))
    d = ImageDraw.Draw(pad)
    for (x0, y0, x1, y1), k in zip(rs, keys):
        d.rectangle((90 + x0 * zoom - 1, y0 * zoom - 1, 90 + x1 * zoom, y1 * zoom), outline=(255, 60, 60))
        d.text((2, y0 * zoom), k, fill=(255, 220, 0))
    pad.save(out)


def strips(crops, out, cols=3, per=90, zoom=2):
    """Pages of labelled run crops [(key, gray array)], cols across, for reading every run in few images."""
    cw = 110 + 190 * zoom
    for p in range(0, len(crops), per):
        part = crops[p:p + per]
        rows = (len(part) + cols - 1) // cols
        page = Image.new("RGB", (cw * cols, rows * (18 * zoom + 4)), (0, 0, 40))
        d = ImageDraw.Draw(page)
        for i, (key, a) in enumerate(part):
            x, y = (i % cols) * cw, (i // cols) * (18 * zoom + 4)
            d.text((x + 2, y + 4), key, fill=(255, 220, 0))
            im = Image.fromarray(a[:18, :190]).resize((min(a.shape[1], 190) * zoom, min(a.shape[0], 18) * zoom),
                                                      Image.NEAREST)
            page.paste(im, (x + 108, y + 2))
        page.save(f"{out}_{p // per:02d}.png")


def scan(names):
    WORK.mkdir(parents=True, exist_ok=True)
    rows, crops = [], []
    for name in [n for n in names if n in ROLL]:
        v, roll = roll_scan(name)
        rs = roll_runs(roll)
        Image.fromarray(roll).save(WORK / f"{name}_roll.png")
        print(f"{name}: {v:.5f} px/frame, roll {roll.shape[0]} rows, {len(rs)} runs")
        for p, y in enumerate(range(0, roll.shape[0], 500)):
            part = [(i, (b[0], b[1] - y, b[2], b[3] - y)) for i, b in enumerate(rs) if y <= b[1] < y + 500]
            sheet(roll[y:y + 520, :PANEL + 40], [b for _, b in part], [f"roll:{i:03d}" for i, _ in part],
                  WORK / f"{name}_roll_{p:02d}.png")
        rows += [(f"roll:{i:03d}", name, *b) for i, b in enumerate(rs)]
        strips([(f"roll:{i:03d}", roll[max(b[1] - 1, 0):b[3] + 1, max(b[0] - 1, 0):b[2] + 1])
                for i, b in enumerate(rs)],
               WORK / f"{name}_runs")
    cards = [n for n in names if n in CARDS]
    if cards:
        done = set()
        for name, cs in card_index(cards).items():
            print(f"{name}: {len(cs)} cards", [(k, a, b, len(rs)) for k, a, b, rs, _ in cs])
            for key, first, last, rs, img in cs:
                rows += [(f"{key}:{i}", name, *b) for i, b in enumerate(rs)]
                if key not in done:
                    done.add(key)
                    crops += [(f"{key}:{i}", img[max(b[1] - 1, 0):b[3] + 1, max(b[0] - 1, 0):b[2] + 1])
                              for i, b in enumerate(rs)]
                    sheet(img[:, CARD_X:], [(b[0] - CARD_X, b[1], b[2] - CARD_X, b[3]) for b in rs],
                          [f"{key}:{i}" for i in range(len(rs))], WORK / f"card_{key.replace('@', '_')}.png", 3)
    if crops:
        strips(crops, WORK / "card_runs")
    with (WORK / "runs.tsv").open("w", encoding="utf-8", newline="") as fh:
        csv.writer(fh, delimiter="\t", lineterminator="\n").writerows([("key", "movie", "x0", "y0", "x1", "y1")]
                                                                      + rows)


DONE = ROLL + CARDS  # movies whose every run has English in credits.tsv


def stamp_of():
    import hashlib
    return hashlib.sha1(TSV.read_bytes() + Path(__file__).read_bytes()).hexdigest()


def pmfs():
    """{ISO path: English PMF} for build.py. gfx/movie is gitignored: movies missing there, or rendered from an
    older credits.tsv / credits.py (gfx/movie/credits.stamp), are rendered first (~2-3 min each)."""
    st = OUT / "credits.stamp"
    stale = not st.exists() or st.read_text() != stamp_of()
    todo = [n for n in DONE if stale or not (OUT / f"{n}.PMF").exists()]
    if todo:
        build(todo)
        st.write_text(stamp_of())
    return {f"/PSP_GAME/USRDIR/MOVIE/{n}.PMF": (OUT / f"{n}.PMF").read_bytes() for n in DONE}


def build(names):
    text = table()
    for name in [n for n in names if n in ROLL]:
        build_roll(name, text)
    cards = [n for n in names if n in CARDS]
    if cards:
        for name, cs in card_index(cards).items():
            build_cards(name, cs, text)


def selftest():
    m = np.zeros((40, 120), bool)
    m[5:15, 10:20] = m[5:15, 24:30] = True            # one run: a 4 px gap is inside a line
    m[5:15, 60:70] = True                             # 30 px gap: a second run
    m[30:38, 10:40] = True
    m[22, 100] = True                                 # a speck is no run
    assert runs(m) == [(10, 5, 30, 15), (60, 5, 70, 15), (10, 30, 40, 38)], runs(m)
    img = np.zeros((H, W, 3), np.float32)
    img[:, :, 0] = 40
    img[100:104, 100:110] = 255
    mask = np.zeros((H, W), np.float32)
    mask[100:104, 100:110] = 1
    fill(img, mask, (100, 100, 110, 104))
    assert abs(img[102, 105, 0] - 40) < 1 and img[102, 105, 1] < 1, img[102, 105]
    print("credits self-test ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", nargs="?", choices=["scan", "build"])
    ap.add_argument("movies", nargs="*")
    ap.add_argument("--test", action="store_true")
    a = ap.parse_args()
    if a.test or not a.cmd:
        return selftest()
    names = a.movies or ROLL + CARDS
    if a.cmd == "scan":
        return scan(names)
    build(names)
    if set(DONE) <= set(names):
        (OUT / "credits.stamp").write_text(stamp_of())


if __name__ == "__main__":
    sys.exit(main())
