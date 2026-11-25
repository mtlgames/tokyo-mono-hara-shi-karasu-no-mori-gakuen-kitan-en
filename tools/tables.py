"""tables.py: text in CSVB tables (csvb.py). One entry per distinct string offset a text pointer reaches.

A pointer column (OfsB) can also point at binary blobs (SSCR scripts, layout data); a string is text when it decodes
as cp932 exactly, holds no control byte but \\n, and holds at least one double-byte character, or sits in a column
whose other strings are text (ASCII-only labels such as "OK" in a menu column).

    python -X utf8 tools/tables.py FILE.bin   # print the entries
"""
import re
import sys

sys.path.insert(0, __import__("os").path.dirname(__file__))
import csvb  # noqa: E402

SJIS_RUN = re.compile(rb"(?:[\x81-\x9f\xe0-\xfc][\x40-\x7e\x80-\xfc]){2,}")


def text(raw):
    """raw bytes -> str if raw is a text string, else None."""
    if not raw or raw.startswith(b"SSCR") or any(c < 0x20 and c != 0x0A for c in raw):
        return None
    try:
        return raw.decode("cp932")  # IBM-extension kanji (FB5E 猪 in obj:0817:04) decode but don't re-encode the same
    except UnicodeDecodeError:
        return None


def entries(b, stem):
    """[{id, jp, refs}] for every text string; id = stem:row:col of the first pointer, refs = pointer count."""
    ss = csvb.strings(b)
    dbl = {col for _, col, _, raw in ss if text(raw) and any(c >= 0x80 for c in raw)}
    out, seen = [], {}
    for r, col, p, raw in ss:
        t = text(raw)
        if t is None or col not in dbl or not t.strip():
            continue
        if p in seen:
            seen[p]["refs"] += 1
            continue
        seen[p] = {"id": f"{stem}:{r:04d}:{col:02x}", "jp": t, "refs": 1}
        if t.encode("cp932") != raw:
            seen[p]["raw"] = raw.hex()  # the original bytes, for the roundtrip test
        out.append(seen[p])
    return out


def offsets(b):
    """{pool offset: id} for the entries, same order rules as entries() (for insertion)."""
    ss = csvb.strings(b)
    first = {}
    for r, col, p, _ in ss:
        first.setdefault(p, (r, col))
    return first


def uncovered(b):
    """SJIS runs (2+ chars) in TblB that no text entry covers: missed text, or Japanese inside binary blobs."""
    t = csvb.chunks(b)["TblB"]
    cov = bytearray(len(t))
    ss = csvb.strings(b)
    dbl = {col for _, col, _, raw in ss if text(raw) and any(c >= 0x80 for c in raw)}
    for _, col, p, raw in ss:
        if text(raw) is not None and col in dbl:
            cov[p:p + len(raw)] = b"\1" * len(raw)
    return [(m.start(), m[0]) for m in SJIS_RUN.finditer(t) if not any(cov[m.start():m.end()])]


if __name__ == "__main__":
    b = open(sys.argv[1], "rb").read()
    for x in entries(b, "t"):
        print(x["id"], x["refs"], repr(x["jp"]))
    for o, run in uncovered(b):
        print("uncovered", hex(o), run.decode("cp932", "replace"))
