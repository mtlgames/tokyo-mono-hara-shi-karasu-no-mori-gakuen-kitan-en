"""gfx_adv_bg.py: full-screen adventure backgrounds that carry Japanese text. Writes gfx/out/adv_bg/*.png, gfx/adv_bg.tsv.

    python -X utf8 tools/gfx_adv_bg.py

ebg0121 (fiction disclaimer), ebg0122 (完 -> The End), exbg0021-0024 (prologue voice lines, white on transparent),
exbg0083 (handwritten card note), exbg0106 (ransom letter, tilted handwriting), exbg0136 (emotion-input tutorial
panel). Text over artwork is removed with a mask diffusion (`inpaint_mask`), then the English is drawn on top.
The three little emotion-wheel screenshots at the bottom of exbg0136 carry tiny kanji inside the picture and stay.
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import gfx
import typeset

D = "adv/bg/"
SERIF, SERIFB, BRUSH = "LiberationSerif-Regular.ttf", "LiberationSerif-Bold.ttf", "KaushanScript-Regular.ttf"
WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)


def text(img, box, s, font, size, fill=WHITE, align="l", xs=1.0, blur=0.0, **kw):
    """Draw s inside box (x, y, w, h); lines separated by \\n; optional soft blur of the ink."""
    x, y, w, h = box
    t = typeset.text_image(w, h, s, font, size=size, fill=fill, align=align, xscale=xs, pad=0, **kw)
    if blur:
        t = t.filter(ImageFilter.GaussianBlur(blur))
    img.alpha_composite(t, (x, y))


def inpaint_mask(img, mask, iters=80):
    """Replace the pixels where mask (bool array, image sized) is True by diffusing the surrounding colours in."""
    a = np.array(img.convert("RGBA")).astype(float)
    known = ~mask
    cur = a.copy()
    cur[mask] = 0
    for _ in range(iters):
        wsum = np.zeros(mask.shape)
        acc = np.zeros(a.shape)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            k = np.roll(known, (dy, dx), (0, 1))
            wsum += k
            acc += np.roll(cur, (dy, dx), (0, 1)) * k[..., None]
        fill = mask & ~known & (wsum > 0)
        cur[fill] = acc[fill] / wsum[fill][:, None]
        known = known | fill
        if known.all():
            break
    return Image.fromarray(cur.clip(0, 255).astype("uint8"))


def grow(mask, n=1):
    for _ in range(n):
        m = mask.copy()
        m[1:] |= mask[:-1]
        m[:-1] |= mask[1:]
        m[:, 1:] |= mask[:, :-1]
        m[:, :-1] |= mask[:, 1:]
        mask = m
    return mask


def ebg0121():
    path = D + "ebg0121.gim"
    img = gfx.original(path)
    wipe = (62, 92, 376, 80)
    img.paste(BLACK, (wipe[0], wipe[1], wipe[0] + wipe[2], wipe[1] + wipe[3]))
    lines = ["This story is a work of fiction.", "It has no connection to any real persons or organizations.",
             "Please never imitate any dangerous acts."]
    for cy, s in zip((105, 131, 157), lines):
        text(img, (70, cy - 12, 380, 24), s, SERIF, 16)
    return path, img, [wipe], "fiction disclaimer"


def ebg0122():
    path = D + "ebg0122.gim"
    img = gfx.original(path)
    wipe = (384, 188, 76, 68)
    img.paste(BLACK, (wipe[0], wipe[1], wipe[0] + wipe[2], wipe[1] + wipe[3]))
    text(img, (320, 190, 130, 64), "The End", BRUSH, 34, align="r", valign="m")
    return path, img, [(320, 188, 140, 68)], "完 -> The End (right-aligned where the kanji stood)"


def voice(name, lines, wipe, note):
    path = D + name + ".gim"
    img = gfx.original(path)
    gfx.clear(img, wipe)
    for cy, s in lines:
        dash = 0
        if s.endswith("--"):                              # the Japanese ends in a long dash (――――): draw it as a line
            s, dash = s[:-2].rstrip(), 70
        w = typeset.font(BRUSH, 24).getlength(s) + (12 + dash if dash else 0)
        x0 = 240 - w / 2
        text(img, (int(x0), cy - 20, 400, 40), s, BRUSH, 24, align="l", valign="m")
        if dash:
            xe = int(x0 + w - dash)
            ImageDraw.Draw(img).line([(xe, cy + 3), (xe + dash, cy + 3)], fill=WHITE, width=2)
    return path, img, [wipe, (0, min(c for c, _ in lines) - 20, 480, 40 + max(c for c, _ in lines) - min(c for c, _ in lines))], note


def exbg0021():
    return voice("exbg0021", [(136, "Do you desire power?")], (136, 115, 208, 42), "prologue voice 1")


def exbg0022():
    return voice("exbg0022", [(117, "You who possess the arcane eyes,"), (153, "you who descend from a noble bloodline.")],
                 (88, 98, 306, 76), "prologue voice 2")


def exbg0023():
    return voice("exbg0023", [(117, "If it is power you desire,"), (154, "take me in hand--")],
                 (100, 98, 280, 76), "prologue voice 3")


def exbg0024():
    return voice("exbg0024", [(136, "Come--")], (158, 116, 162, 40), "prologue voice 4")


def exbg0083():
    path = D + "exbg0083.gim"
    img = gfx.original(path)
    # the two handwritten lines (rows 114-141, left of the seal doodle) sit on a smooth cream gradient: rebuild the rows
    # by interpolating between the clean rows above (y 110-112) and below (y 143-145) in every column
    x, y, w, h = 126, 113, 130, 30
    a = np.array(img).astype(float)
    top = a[110:113, x:x + w].mean(axis=0)
    bot = a[143:146, x:x + w].mean(axis=0)
    t = ((np.arange(y, y + h) - 111.5) / 32.0)[:, None, None]
    a[y:y + h, x:x + w] = top[None] * (1 - t) + bot[None] * t
    img = Image.fromarray(a.clip(0, 255).astype("uint8"))
    ink = (112, 66, 56, 235)
    text(img, (128, 108, 132, 66), "After school,\nI'll be waiting\non the roof.", BRUSH, 14, fill=ink, blur=0.35,
         spacing=1, valign="t")
    return path, img, [(x - 3, y - 6, w + 6, 70)], "card note: After school, I'll be waiting on the roof."


# ransom letter: paper tilted 22 degrees counter-clockwise, columns of cursive on it
TILT = math.radians(22)
LETTER = ("We have your schoolmate, Miss Minori Hosaka. If you want her returned unharmed, hand over all of the "
          "hanafuda. We shall await you at dusk, beneath Yahiro Academy--")
CREASES = [((203, 3), (273, 128)), ((123, 47), (183, 163)), ((250, 0), (283, 60)), ((157, 33), (163, 50))]


def seg_dist(xx, yy, p, q):
    (px, py), (qx, qy) = p, q
    dx, dy = qx - px, qy - py
    t = np.clip(((xx - px) * dx + (yy - py) * dy) / (dx * dx + dy * dy), 0, 1)
    return np.hypot(xx - (px + t * dx), yy - (py + t * dy))


def exbg0106():
    path = D + "exbg0106.gim"
    img = gfx.original(path)
    a = np.array(img.convert("RGB")).astype(float)
    lum = a.mean(axis=2)
    yy, xx = np.mgrid[0:lum.shape[0], 0:lum.shape[1]]
    u = xx * math.cos(TILT) - yy * math.sin(TILT)                # paper axes: u along the lines, v down the paper
    v = xx * math.sin(TILT) + yy * math.cos(TILT)
    mask = (lum < 178) & (u > 76) & (u < 266) & (v > 92) & (v < 300) & (xx > 105) & (yy > 22)
    mask &= ~((xx >= 196) & (yy >= 198))                          # the cat / seal doodles below the text stay
    for p, q in CREASES:
        mask &= seg_dist(xx, yy, p, q) > 3.5
    mask = grow(mask, 1)
    ys, xs = np.nonzero(mask)
    rects = [(int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1))]
    img = inpaint_mask(img, mask)
    wrap = typeset.wrap(LETTER, BRUSH, 13, 176)
    t = typeset.text_image(184, 176, wrap, BRUSH, size=13, fill=(62, 62, 70, 225), align="l", valign="t", pad=0,
                           spacing=3)
    t = t.filter(ImageFilter.GaussianBlur(0.3)).rotate(math.degrees(TILT), expand=True, resample=Image.BICUBIC)
    cu, cv = 172, 192                                            # centre of the text block in paper coordinates
    cx, cy = cu * math.cos(TILT) + cv * math.sin(TILT), -cu * math.sin(TILT) + cv * math.cos(TILT)
    pos = (int(cx - t.width / 2), int(cy - t.height / 2))
    img.alpha_composite(t, pos)
    rects.append(pos + t.size)
    return path, img, rects,"ransom letter (text from ms07_01:163), English written along the tilted paper"


def exbg0136():
    path = D + "exbg0136.gim"
    img = gfx.original(path)
    rects = []
    # headings sit on the dark-red banners: remove the near-white lettering, then redraw
    for box, s in (((18, 3, 185, 24), "About Emotion Input"), ((18, 84, 100, 24), "Controls")):
        img = typeset.inpaint(img, (box[0], box[1], box[0] + box[2], box[1] + box[3]), white_min=105)
        text(img, (box[0] + 4, box[1], box[2], box[3]), s, SERIFB, 18, valign="m", shadow=(1, 1, (0, 0, 0, 200)))
        rects.append(box)
    body = [(29, "Sometimes during a conversation, you will be asked how you feel."),
            (45, "At those times, your chosen emotion can change the flow of the talk,"),
            (61, "and the other person's feelings toward you can change."),
            (109, None), (125, "Keep holding to fill the gauge; the stronger emotion lights up white."),
            (141, "Release the D-pad to input the emotion that was lit white at that moment.")]
    for y, s in body:
        wipe = (28, y - 1, 440, 17)
        img.paste(BLACK, (wipe[0], wipe[1], wipe[0] + wipe[2], wipe[1] + wipe[3]))
        rects.append(wipe)
        if s:
            text(img, (32, y - 1, 436, 17), s, SERIF, 14, valign="m")
    red = (254, 112, 116, 255)
    hold = "Hold the D-pad"
    text(img, (32, 108, 200, 17), hold, SERIF, 14, fill=red, valign="m")
    text(img, (32 + int(typeset.font(SERIF, 14).getlength(hold)), 108, 300, 17), " toward the emotion you want to input.",
         SERIF, 14, valign="m")
    return path, img, rects, "tutorial panel text; the kanji inside the three wheel screenshots stay"


ROWS = [ebg0121, ebg0122, exbg0021, exbg0022, exbg0023, exbg0024, exbg0083, exbg0106, exbg0136]


def main():
    rows = []
    for fn in ROWS:
        path, img, rects, note = fn()
        rows.append((path, gfx.save(img, "adv_bg", path, rects), note))
    gfx.write_tsv("adv_bg", rows)


if __name__ == "__main__":
    main()
