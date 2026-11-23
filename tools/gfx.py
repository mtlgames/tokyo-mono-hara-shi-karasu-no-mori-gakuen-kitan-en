"""gfx.py: English graphics -> GIM edits for the build.

    python -X utf8 tools/gfx.py              # list every row and check its PNG (size, every copy found)
    python -X utf8 tools/gfx.py --sheet OUT  # original | English pairs of every row, for the eye

Rows: gfx/<group>.tsv, `path<TAB>png[<TAB>note]` (header line starts with #). `path` is one unpacked GIM path as the
survey lists it (work/survey/*.tsv), `png` the full-size RGBA English image (repo-relative, gfx/out/<group>/...). The
build writes the PNG into every GIM in CROW.PAK with the same original bytes (the game ships copies under several
names). Group generators (tools/gfx_<group>.py) write the PNGs; docs/graphics-brief.md has the workflow.
"""
import argparse
import hashlib
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("TYPESET_FONTS", str(ROOT / "fonts"))  # typeset.py (imported by generators) reads fonts/
sys.path.insert(0, str(ROOT / "tools"))
from skill import SCRIPTS  # noqa: E402

sys.path.insert(0, SCRIPTS)
import gim  # noqa: E402
from PIL import Image  # noqa: E402

GFX = ROOT / "gfx"


def rows():
    """[(group, path, png)] from gfx/*.tsv."""
    out = []
    for t in sorted(GFX.glob("*.tsv")):
        for n, line in enumerate(t.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip() or line.startswith("#"):
                continue
            c = line.split("\t")
            if len(c) < 2:
                raise ValueError(f"{t.name}:{n}: want path<TAB>png")
            out.append((t.stem, c[0], ROOT / c[1]))
    return out


def gims():
    """{md5: [paths]} and {path: bytes} for every GIM in CROW.PAK."""
    from source import members
    by, data = {}, {}
    for p, d in members(""):
        if d[:11] == b"MIG.00.1PSP":
            by.setdefault(hashlib.md5(d).hexdigest(), []).append(p)
            data[p] = d
    return by, data


def decode(d):
    w, h, px = gim.to_rgba(d, gim.parse(d)[0])
    return Image.frombytes("RGBA", (w, h), b"".join(px))


def original(path):
    """Original image of one GIM path, from work/unpacked (tools/unpack_all.py) so generators need no ISO scan."""
    return decode((ROOT / "work" / "unpacked" / path).read_bytes())


def clear(img, rect):
    """Make rect (x, y, w, h) fully transparent: the atlas cells carry text on alpha 0."""
    x, y, w, h = rect
    img.paste((0, 0, 0, 0), (x, y, x + w, y + h))


def glow(img, rect, text_img, colour, radius=2, strength=2):
    """Composite text_img (RGBA, rect-sized) onto img at rect with a blurred halo in colour behind it."""
    from PIL import ImageFilter
    a = text_img.split()[3].filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(radius))
    a = a.point(lambda v: min(255, v * strength))
    halo = Image.new("RGBA", text_img.size, colour)
    halo.putalpha(a)
    halo.alpha_composite(text_img)
    img.alpha_composite(halo, rect[:2])


def outside(orig, new, rects):
    """Pixels changed outside the declared rects [(x, y, w, h)]: a count, 0 when only the labels changed."""
    from PIL import ImageChops
    diff = ImageChops.difference(orig, new).convert("L").point(lambda v: 255 if v else 0)
    for x, y, w, h in rects:
        diff.paste(0, (x, y, x + w, y + h))
    return sum(1 for v in diff.getdata() if v)


def save(img, group, path, rects=None):
    """Write gfx/out/<group>/<path with _>.png; return its repo-relative name for the tsv. rects: the declared edit
    rects; raises when any pixel outside them changed."""
    if rects is not None:
        n = outside(original(path), img, rects)
        if n:
            raise ValueError(f"{path}: {n} pixels changed outside the declared rects")
    out = GFX / "out" / group / (path.replace("/", "_").removesuffix(".gim") + ".png")
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    return out.relative_to(ROOT).as_posix()


def write_tsv(group, rows_):
    """gfx/<group>.tsv from [(path, png, note)]."""
    lines = ["#path\tpng\tnote"] + ["\t".join(r) for r in rows_]
    (GFX / f"{group}.tsv").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def encode(d, png):
    """GIM bytes d with the image replaced by png (same size). Always keeps the original palette (nearest colour):
    a new median-cut palette for one label bands every other picture in the atlas."""
    im = Image.open(png).convert("RGBA")
    g = gim.parse(d)[0]
    if im.size != (g.w, g.h):
        raise ValueError(f"{png}: {im.size}, GIM is {(g.w, g.h)}")
    b = im.tobytes()
    return gim.encode(d, g, [b[y * 4 * g.w:(y + 1) * 4 * g.w] for y in range(g.h)], repalette=False)


def edits():
    """{unpacked path: new GIM bytes} for every row and every copy of its GIM."""
    rs = rows()
    if not rs:
        return {}
    by, data = gims()
    out = {}
    for group, path, png in rs:
        if path not in data:
            raise KeyError(f"gfx/{group}.tsv: no GIM {path}")
        new = encode(data[path], png)
        for p in by[hashlib.md5(data[path]).hexdigest()]:
            if p in out and out[p] != new:
                raise ValueError(f"{p}: two rows write different images")
            out[p] = new
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sheet", type=Path, help="write original|English pair images into this folder")
    a = ap.parse_args()
    by, data = gims()
    bad = 0
    for group, path, png in rows():
        try:
            new = encode(data[path], png)
            copies = by[hashlib.md5(data[path]).hexdigest()]
            print(f"{group}\t{path}\t{len(copies)} cop{'y' if len(copies) == 1 else 'ies'}")
            if a.sheet:
                o, e = decode(data[path]), decode(new)
                s = Image.new("RGBA", (o.width * 2 + 8, o.height), (40, 40, 40, 255))
                s.alpha_composite(o, (0, 0))
                s.alpha_composite(e, (o.width + 8, 0))
                a.sheet.mkdir(parents=True, exist_ok=True)
                s.save(a.sheet / (path.replace("/", "_") + ".png"))
        except (KeyError, ValueError, OSError) as x:
            bad += 1
            print(f"ERROR {group}\t{path}\t{x}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
