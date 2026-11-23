"""pwx.py: story/event script codec (pw/*/*.pwx). Format: docs/re/text.md.

File: u16 offset table (4-byte units; the first value is the table size), then 4-aligned blocks, each ending `_`.
A block mixes ASCII command mnemonics (kept as is) with Shift-JIS text. A text span is a run of SJIS characters
plus the inline codes between them:
    r -> newline, px/pm/pn -> {px}/{pm}/{pn} (player name), l<base>(<reading>) -> {ruby:base|reading}
Anything else ASCII ends the span. A SJIS pair that cp932 doesn't roundtrip is kept as {x:HHHH}.

    python -X utf8 tools/pwx.py FILE.pwx            # print every span with its id
"""
import re
import struct
import sys

PV = (b"px", b"pm", b"pn")
TOKEN = re.compile(r"\n|\{(px|pm|pn)\}|\{ruby:([^|}]*)\|([^}]*)\}|\{x:([0-9A-Fa-f]{4})\}")


def lead(c):
    return 0x81 <= c <= 0x9F or 0xE0 <= c <= 0xFC


def blocks(d):
    """File bytes -> list of block bytes (each with its trailing zero padding). Unused table slots are 0 and come last;
    a slot may point at the file end (an empty last block, 2 files)."""
    n = struct.unpack_from("<H", d, 0)[0] * 4
    offs = [o * 4 for o in struct.unpack_from(f"<{n // 2}H", d, 0)]
    offs = offs[:offs.index(0)] if 0 in offs else offs
    return [d[o:e] for o, e in zip(offs, offs[1:] + [len(d)])]


def pack(bl, head=0):
    """Inverse of blocks(): offset table (at least `head` bytes: the original's table size, which some files pad
    with unused slots) + 4-aligned blocks (zero padding)."""
    bl = [b.rstrip(b"\0") + b"\0" * (-len(b.rstrip(b"\0")) % 4) for b in bl]
    head = max(head, (2 * len(bl) + 3) // 4 * 4)
    offs, pos = [], head
    for b in bl:
        offs.append(pos // 4)
        pos += len(b)
    if pos > 0x40000:
        raise ValueError("pwx too large for u16 offsets in 4-byte units")
    return struct.pack(f"<{len(offs)}H", *offs).ljust(head, b"\0") + b"".join(bl)


def head_size(d):
    return struct.unpack_from("<H", d, 0)[0] * 4


def ruby_end(b, j):
    """End offset of an l<SJIS+>(<SJIS*>) ruby starting at j, else None."""
    if b[j:j + 1] != b"l" or j + 1 >= len(b) or not lead(b[j + 1]):
        return None
    k = j + 1
    while k < len(b) and lead(b[k]):
        k += 2
    if b[k:k + 1] != b"(":
        return None
    k += 1
    while k < len(b) and lead(b[k]):
        k += 2
    return k + 1 if b[k:k + 1] == b")" else None


def _continues(b, j):
    while b[j:j + 1] == b"r":
        j += 1
    return j < len(b) and (lead(b[j]) or ruby_end(b, j) is not None or b[j:j + 2] in PV)


def spans(b):
    """[(start, end)] of every text span in block bytes b. Every SJIS byte of b lies in one."""
    out, i = [], 0
    while i < len(b):
        if not lead(b[i]):
            i += 1
            continue
        s = e = i
        if i >= 2 and b[i - 2:i] in PV:
            s = i - 2
        elif i >= 1 and b[i - 1:i] == b"l" and ruby_end(b, i - 1):
            s, e = i - 1, ruby_end(b, i - 1)
        while e < len(b):
            r = ruby_end(b, e)
            if lead(b[e]):
                e += 2
            elif r:
                e = r
            elif b[e:e + 2] in PV:
                e += 2
            elif b[e:e + 1] == b"r" and _continues(b, e + 1):
                e += 1
            else:
                break
        out.append((s, e))
        i = e
    return out


def _sjis(b):
    out = []
    for k in range(0, len(b), 2):
        pair = b[k:k + 2]
        try:
            c = pair.decode("cp932")
            ok = c.encode("cp932") == pair
        except UnicodeError:
            ok = False
        out.append(c if ok else f"{{x:{pair.hex().upper()}}}")
    return "".join(out)


def decode(b):
    """Span bytes -> text."""
    out, i = [], 0
    while i < len(b):
        r = ruby_end(b, i)
        if lead(b[i]):
            j = i
            while j < len(b) and lead(b[j]):
                j += 2
            out.append(_sjis(b[i:j]))
            i = j
        elif r:
            base, reading = b[i + 1:r - 1].split(b"(", 1)
            out.append(f"{{ruby:{_sjis(base)}|{_sjis(reading)}}}")
            i = r
        elif b[i:i + 2] in PV:
            out.append("{" + b[i:i + 2].decode() + "}")
            i += 2
        elif b[i:i + 1] == b"r":
            out.append("\n")
            i += 1
        else:
            raise ValueError(f"not span bytes at {i}: {b[i:i + 8]!r}")
    return "".join(out)


def _enc_sjis(t):
    out, pos = bytearray(), 0
    for m in re.finditer(r"\{x:([0-9A-Fa-f]{4})\}", t):
        out += t[pos:m.start()].encode("cp932") + bytes.fromhex(m[1])
        pos = m.end()
    return bytes(out + t[pos:].encode("cp932"))


def encode(t):
    """Text -> span bytes (Japanese / full-width text only; English encoding is decided in phase 5)."""
    out, pos = bytearray(), 0
    for m in TOKEN.finditer(t):
        out += _enc_sjis(t[pos:m.start()])
        if m[0] == "\n":
            out += b"r"
        elif m[1]:
            out += m[1].encode()
        elif m[4]:
            out += bytes.fromhex(m[4])
        else:
            out += b"l" + _enc_sjis(m[2]) + b"(" + _enc_sjis(m[3]) + b")"
        pos = m.end()
    return bytes(out + _enc_sjis(t[pos:]))


SPEAKER = re.compile(r"【([^】]*)】(?:\n|$)")


def split_speaker(t):
    """'【name】\\ntext' -> ('name', 'text'); no speaker -> (None, t)."""
    m = SPEAKER.match(t)
    return (m[1], t[m.end():]) if m else (None, t)


def join_speaker(speaker, t):
    return t if speaker is None else f"【{speaker}】" + ("\n" + t if t else "")


def entries(d, stem):
    """File bytes -> [{id, speaker?, kind?, jp}] in file order; id = stem:block:span."""
    out = []
    for bi, b in enumerate(blocks(d)):
        for si, (s, e) in enumerate(spans(b)):
            speaker, text = split_speaker(decode(b[s:e]))
            x = {"id": f"{stem}:{bi:03d}:{si:02d}"}
            if speaker is not None:
                x["speaker"] = speaker
            if b[s - 1:s] == b"{":
                x["kind"] = "caption"
            x["jp"] = text
            out.append(x)
    return out


if __name__ == "__main__":
    data = open(sys.argv[1], "rb").read()
    for x in entries(data, sys.argv[1]):
        print(x["id"], x.get("speaker", ""), repr(x["jp"]))
