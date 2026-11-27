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

# Sprite-layout byte patches (path, offset, original hex, new hex, why): for words the game builds from repeated cells.
SAVELOAD = "system/saveload.pak/system/saveload.g2d"
LAYOUT = [
    # ゲーム|オ|ー|バ|ー banner (dungeon.g2d sprite of 4 quads, uv = 4 int16 at +8): the 2nd and 4th quads reuse the ー
    # cell; point them at two free 32x32 cells of dungeon08 so "GAME OVER" can run across all 7 (gfx_dungeon_ui).
    ("dungeon/ui/ui_dungeon.pak/dungeon/ui/dungeon.g2d", 0x8B38, "800060009f007f00", "c000c000df00df00", "game over"),
    ("dungeon/ui/ui_dungeon.pak/dungeon/ui/dungeon.g2d", 0x8B78, "800060009f007f00", "e000c000ff00df00", "game over"),
    # Turn cards: 人/隠人/罠/相手 + の + 手番 (dungeon03) reuse the の cell and 人 is the tail of 隠人, so the player card
    # reads "ni ap Turn". Point its first quad at the free "Your" cell (128,160) of the redraw, blank every の quad
    # (a transparent px), and start the 手番 quad after the new possessive to leave a word space.
    ("dungeon/ui/ui_dungeon.pak/dungeon/ui/dungeon.g2d", 0x69EC, "0000000027001f002000c0004700df00",
     "0000000033001f008000a000b300bf00", "player turn"),
    ("dungeon/ui/ui_dungeon.pak/dungeon/ui/dungeon.g2d", 0x6A0C, "2400000043001f006800c0008700df00",
     "0000000000000000fa009b00fb009c00", "player turn"),
    ("dungeon/ui/ui_dungeon.pak/dungeon/ui/dungeon.g2d", 0x6A90, "4400000063001f006800c0008700df00",
     "0000000000000000fa009b00fb009c00", "oni turn"),
    ("dungeon/ui/ui_dungeon.pak/dungeon/ui/dungeon.g2d", 0x6AB0, "60000000a7001f00b800e000ff00ff00",
     "4e00000095001f00b800e000ff00ff00", "oni turn"),
    ("dungeon/ui/ui_dungeon.pak/dungeon/ui/dungeon.g2d", 0x6B34, "4000000087001f00b800e000ff00ff00",
     "4a00000091001f00b800e000ff00ff00", "trap turn"),
    ("dungeon/ui/ui_dungeon.pak/dungeon/ui/dungeon.g2d", 0x92A0, "400000005f001f006800c0008700df00",
     "0000000000000000fa009b00fb009c00", "foe turn"),
    ("dungeon/ui/ui_dungeon.pak/dungeon/ui/dungeon.g2d", 0x92C0, "60000000a7001f00b800e000ff00ff00",
     "4c00000093001f00b800e000ff00ff00", "foe turn"),
    # 迎撃 plate under each enemy (x 2..33, u 224..255): "Counter" fills 208..255 of dungeon04, so the quad takes all
    # 48 px, centred on the old one (x -6..41).
    ("dungeon/ui/ui_dungeon.pak/dungeon/ui/dungeon.g2d", 0x81D0, "0200000021000f00e0005800ff006700",
     "faff000029000f00d0005800ff006700", "counter"),
    # Save/Load diamonds: セ|ー|ブ and ロ|ー|ド quads (x0,y0,x1,y1,u0,v0,u1,v1, inclusive) share the ー cell and the
    # vertical title's cells, so "Save"/"Load" were squeezed into the first cell. The first quad of each word now spans
    # the whole word from a free strip of ui_saveload01 (gfx_menus.ui_saveload01), the other two draw a transparent px.
    (SAVELOAD, 0x63C, "040005001b001c000000000017001700", "0400090049001800380058007d006700", "save"),
    (SAVELOAD, 0x65C, "1b000d0032001400080018001f001f00", "00000000000000007f006f007f006f00", "save"),
    (SAVELOAD, 0x67C, "3200050049001c00180000002f001700", "00000000000000007f006f007f006f00", "save"),
    (SAVELOAD, 0x6C0, "06000a001d001900080020001f002f00", "06000900470018000000700041007f00", "load"),
    (SAVELOAD, 0x6E0, "1d000d0034001400080018001f001f00", "00000000000000007f006f007f006f00", "load"),
    (SAVELOAD, 0x700, "3800050047001c00300000003f001700", "00000000000000007f006f007f006f00", "load"),
]
SAVE_STRIP, LOAD_STRIP = (56, 88, 70, 16), (0, 112, 66, 16)  # atlas rects of the two words (quads above)


def layout_edits():
    """{unpacked path: patched bytes} for LAYOUT; refuses a patch whose original bytes differ."""
    from source import members
    want = {p for p, *_ in LAYOUT}
    out = {p: bytearray(d) for p, d in members(*want) if p in want}
    for p, off, old, new, why in LAYOUT:
        o, n = bytes.fromhex(old), bytes.fromhex(new)
        if out[p][off:off + len(o)] != o:
            raise ValueError(f"LAYOUT {why}: {p}+{off:#x} is not {old}")
        out[p][off:off + len(n)] = n
    return {p: bytes(d) for p, d in out.items()}


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
    """{md5: [paths]} and {path: bytes} for every GIM in CROW.PAK. A GIM inside another file (a .znt model's
    texture) is `container@0xOFFSET`, as `gimsheet.py --embedded` names it."""
    from gimsheet import MAGIC, embedded
    from source import members
    by, data = {}, {}
    for p, d in members(""):
        found = [(p, d)] if d[:11] == MAGIC else [(f"{p}@{o:#x}", g) for o, g in embedded(d)] if MAGIC in d else []
        for name, g in found:
            by.setdefault(hashlib.md5(g).hexdigest(), []).append(name)
            data[name] = g
    return by, data


def unpacked_gim(path):
    """GIM bytes of a path (or container@0xOFFSET) from work/unpacked."""
    from gimsheet import embedded
    file, _, off = path.partition("@")
    d = (ROOT / "work" / "unpacked" / file).read_bytes()
    return dict(embedded(d))[int(off, 16)] if off else d


def decode(d):
    w, h, px = gim.to_rgba(d, gim.parse(d)[0])
    return Image.frombytes("RGBA", (w, h), b"".join(px))


def original(path):
    """Original image of one GIM path, from work/unpacked (tools/unpack_all.py) so generators need no ISO scan."""
    return decode(unpacked_gim(path))


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
        if path.endswith(".png"):        # a plain PNG file in CROW.PAK (system/newdataicon.png): shipped as is
            out[path] = png.read_bytes()
            continue
        if path not in data:
            raise KeyError(f"gfx/{group}.tsv: no GIM {path}")
        new = encode(data[path], png)
        for p in by[hashlib.md5(data[path]).hexdigest()]:
            if p in out and out[p] != new:
                raise ValueError(f"{p}: two rows write different images")
            out[p] = new
    out = splice_embedded(out)
    out.update(layout_edits())
    return out


# zdv copies of CROW.PAK files compiled into the EBOOT (file offset, unpacked path): the dungeon loader draws these,
# not the CROW.PAK ones. A scan of the ELF for zdv headers found only these two (worker 13).
EBOOT_COPIES = [(0x2A6918, "system/ui_loading.pak/system/ui_loading.gim")]


def eboot_copies(d, out):
    """Write the new bytes of each EBOOT_COPIES file into the ELF bytearray d, recompressed in its original zdv slot."""
    import zdv
    for off, path in EBOOT_COPIES:
        if path not in out:
            continue
        u, u2, one, cs = (int.from_bytes(d[off + i:off + i + 4], "little") for i in range(0, 16, 4))
        if u != u2 or one != 1 or d[off + 16] != 0x78:
            raise ValueError(f"EBOOT {off:#x}: no zdv header for {path}")
        new = zdv.deflate(out[path], level=9)
        if len(new) > 16 + cs:
            raise ValueError(f"EBOOT {off:#x}: {path} recompressed {len(new)} B > slot {16 + cs} B")
        d[off:off + 16 + cs] = new + b"\0" * (16 + cs - len(new))
    return d


def splice_embedded(out):
    """Turn container@0xOFFSET entries into whole-container payloads (the GIM keeps its size: same image size and
    palette, so nothing after it in the model moves)."""
    from source import members
    want = {k.partition("@")[0] for k in out if "@" in k}
    if not want:
        return out
    whole = {p: bytearray(d) for p, d in members(*want) if p in want}
    for k in [k for k in out if "@" in k]:
        file, _, off = k.partition("@")
        o, new = int(off, 16), out.pop(k)
        old = whole[file][o:o + len(new)]
        if old[:11] != b"MIG.00.1PSP" or int.from_bytes(old[0x14:0x18], "little") + 0x10 != len(new):
            raise ValueError(f"{k}: new GIM size {len(new)} differs from the original")
        whole[file][o:o + len(new)] = new
    out.update({p: bytes(d) for p, d in whole.items()})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sheet", type=Path, help="write original|English pair images into this folder")
    a = ap.parse_args()
    by, data = gims()
    bad = 0
    for group, path, png in rows():
        if path.endswith(".png"):
            print(f"{group}\t{path}\tplain file" if png.exists() else f"ERROR {group}\t{path}\tno {png}")
            bad += not png.exists()
            continue
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
