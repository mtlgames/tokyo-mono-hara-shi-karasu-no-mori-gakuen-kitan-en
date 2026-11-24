"""fontpatch.py: English text encoding for the script and the font change that makes it proportional.

ASCII bytes are commands in .pwx, so English script text is stored as full-width SJIS (`to_sjis_text`), and every
font's full-width Latin glyphs are replaced by its own proportional ASCII glyphs and widths (`patch`). ' and " have
no full-width form in cp932: they use ’ (8166) and ” (8168), whose glyphs get the ASCII ' and ".

    python -X utf8 tools/fontpatch.py      # self-test
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ipk import Font  # noqa: E402

FONTS = [f"app_init.pak/system/font/{n}.ipk" for n in ("advfont08", "advfont14", "sysfont18", "mobilefont")]
SPECIAL = {" ": "　", "'": "’", '"': "”"}
DASH = "―"  # SJIS 815C: script text "--" (a full-width dash glyph)
KEEP = "~"  # its stand-in ～ keeps the font's own wave dash: the ASCII tilde glyph is a tiny raised dash


def fw(c):
    """ASCII char -> its full-width stand-in (str of one char)."""
    return SPECIAL.get(c) or chr(ord(c) + 0xFEE0)


def to_sjis_text(t):
    """English text -> full-width stand-ins (newlines and {..} markup kept as is)."""
    out, depth = [], 0
    for c in t.replace("--", DASH):  # two ASCII hyphens drew as "- -" with a gap: use the font's own dash

        depth += c == "{"
        out.append(c if depth or c in "\n" + DASH or not (" " <= c <= "~") else fw(c))
        depth -= c == "}"
    return "".join(out)


def code(c):
    b = c.encode("cp932")
    return b[0] << 8 | b[1]


def patch(data):
    """Font file bytes -> bytes with full-width Latin drawn as proportional ASCII."""
    f = Font(data)
    for c in range(0x20, 0x7F):
        k, k2 = f.codes.get(c), f.codes.get(code(fw(chr(c))))
        if k is not None and k2 is not None and chr(c) not in KEEP:
            g = f.glyph(k)
            w, h = f.metrics(k)
            # the drawer clips each glyph to its advance; most glyphs lose 1 px (outline), sysfont18 '!' lost 3
            ink = max((x + 1 for r in g for x, v in enumerate(r) if v), default=0)
            f.set_glyph(k2, g)
            f.set_metrics(k2, max(w, ink - 1), h)
    return bytes(f.data)


if __name__ == "__main__":
    for c in map(chr, range(0x20, 0x7F)):
        assert len(fw(c).encode("cp932")) == 2, c
    assert to_sjis_text("It's {px}!\nOK") == "Ｉｔ’ｓ　{px}！\nＯＫ"
    assert to_sjis_text("so--{pn}-") == "ｓｏ―{pn}－"
    print("ok")
