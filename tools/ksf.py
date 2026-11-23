"""ksf.py: player choice menus in the .ksf beside each .pwx (docs/re/text.md). Format of the rest unknown.

A choice is byte 0x01 then a 30-byte slot holding a NUL-terminated SJIS string, zero-padded (1,225 in the game; the
next record follows the slot). A hit counts when the string decodes exactly as cp932, has no control byte and the
rest of its slot is zero; other SJIS-looking bytes in .ksf are binary noise (single chars, 0x80 runs).

    python -X utf8 tools/ksf.py FILE.ksf
"""
import re
import sys

SLOT = 30
CHOICE = re.compile(rb"(?<=\x01)[\x81-\x9f\xe0-\xfc][^\0]*\0")


def choices(d):
    """[(offset, text)] of every choice string."""
    out = []
    for m in CHOICE.finditer(d):
        a, raw = m.start(), m[0][:-1]
        if len(raw) >= SLOT or any(d[a + len(raw):a + SLOT]):
            continue
        try:
            s = raw.decode("cp932")
        except UnicodeDecodeError:
            continue
        if s.encode("cp932") == raw and not any(c < 0x20 for c in raw):
            out.append((a, s))
    return out


def entries(d, stem):
    return [{"id": f"{stem}:ksf:{a:05x}", "kind": "choice", "jp": s, "slot": SLOT} for a, s in choices(d)]


if __name__ == "__main__":
    for a, s in choices(open(sys.argv[1], "rb").read()):
        print(hex(a), s)
