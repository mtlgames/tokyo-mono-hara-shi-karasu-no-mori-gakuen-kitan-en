"""eboot_text.py: Japanese strings in the decrypted EBOOT ELF (work/exe/NPJH50215_EBOOT.BIN, from the ISO's
PSP_GAME/SYSDIR/EBOOT.BIN; docs/re/text.md). A relocatable module: vaddr = file offset - 0xC0 for the code/rodata
segment, and data pointers hold vaddrs.

A string is a NUL-terminated run in a rodata/data section that starts after a NUL, decodes exactly as cp932 (or
UTF-8: the save dialog strings), holds no control byte but \\n, and passes is_text(). refs = u32 data pointers to it +
MIPS lui + addiu/ori pairs building its address (0 for struct-array members). `slot` = bytes up to the next non-zero
byte, the room an in-place edit has. Strings keep the pwx inline codes as ASCII (pn/pm player name, yh: guess).

    python -X utf8 tools/eboot_text.py [ELF]    # print id, refs, slot, text
"""
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ELF = ROOT / "work" / "exe" / "NPJH50215_EBOOT.BIN"
BASE = 0xC0  # file offset of vaddr 0
CAND = re.compile(rb"(?<=\0)[^\0]*[\x81-\x9f\xe0-\xef][^\0]*\0")


def segments(d):
    """[(vaddr, file offset, file size, flags)] of the ELF program headers."""
    phoff, = struct.unpack_from("<I", d, 0x1C)
    phentsize, phnum = struct.unpack_from("<HH", d, 0x2A)
    out = []
    for i in range(phnum):
        _, off, vaddr, _, fsz, _, flags, _ = struct.unpack_from("<8I", d, phoff + i * phentsize)
        out.append((vaddr, off, fsz, flags))
    return out


def data_ranges(d):
    """[(file offset, end)] of the allocated, non-executable sections (rodata, data): where strings live."""
    shoff, = struct.unpack_from("<I", d, 0x20)
    shentsize, shnum = struct.unpack_from("<HH", d, 0x2E)
    out = []
    for i in range(shnum):
        _, typ, flags, _, off, size = struct.unpack_from("<6I", d, shoff + i * shentsize)
        if flags & 2 and not flags & 4 and typ == 1:  # SHF_ALLOC, not SHF_EXECINSTR, PROGBITS
            out.append((off, off + size))
    return out


def code_refs(d):
    """{vaddr: count} of addresses built by lui rX,hi then addiu/ori rY,rX,lo within 12 instructions."""
    seg = next(s for s in segments(d) if s[3] & 1)  # executable
    _, off, size, _ = seg
    words = struct.unpack_from(f"<{size // 4}I", d, off)
    refs = {}
    for i, w in enumerate(words):
        if w >> 26 != 0x0F:  # lui
            continue
        rt, hi = (w >> 16) & 31, w & 0xFFFF
        for w2 in words[i + 1:i + 13]:
            op, rs = w2 >> 26, (w2 >> 21) & 31
            if op in (0x09, 0x0D) and rs == rt:
                lo = w2 & 0xFFFF
                a = (hi << 16) + (lo - 0x10000 if op == 0x09 and lo & 0x8000 else lo)
                refs[a & 0xFFFFFFFF] = refs.get(a & 0xFFFFFFFF, 0) + 1
            if (w2 >> 16) & 31 == rt and op in (0x0F, 0x09, 0x0D, 0x23, 0x21):  # rt overwritten
                break
    return refs


def decode(raw):
    if any(c < 0x20 and c != 0x0A for c in raw):
        return None
    for enc in ("cp932", "utf-8"):
        try:
            s = raw.decode(enc)
        except UnicodeDecodeError:
            continue
        if s.encode(enc) == raw:
            return s, enc
    return None


def is_text(s, raw, refs, off):
    """Kana / full-width / 2+ double-byte chars = text, referenced or not (struct arrays such as the nickname table
    at 0x2d3a10 are reached by base + index). A lone double-byte char is text only when referenced, pure, and inside
    the string pool: before POOL, .rodata holds pointer tables whose words decode as one SJIS char."""
    if KANA.search(s) or len(raw) - len(s) >= 2 or off in LONE:
        return True
    return refs > 0 and off >= POOL and all(c >= 0x80 for c in raw)


KANA = re.compile("[　-ヿ！-～]")
POOL = 0x2B0600
# lone chars the rule above misses: text speed 瞬 (24-byte slots "1" "2" "3" 瞬, phone settings, unreferenced);
# item menu 円 (second byte 0x7E) and the equipped mark 装 (its lui/addiu pair is not found in the ELF)
# profile birthday spinners %2d月 / %2d日 and blood type %s型 (format code makes them impure)
LONE = {0x2D2538, 0x2B5210, 0x2B5214, 0x2B448C, 0x2B4494, 0x2B4360}
# strings CAND can't see: the byte before is struct data, not NUL (options row 保持する, partner of 2d2388 保持しない;
# release.py jp found it; a sweep for kana runs after a control byte found no other)
ROW_START = {0x2D2370}


def strings(d):
    """[{id, off, enc, refs, slot, jp}] for every Japanese string; refs = data pointers + code lui/addiu pairs."""
    data = {}
    for (v,) in struct.iter_unpack("<I", d[:len(d) // 4 * 4]):
        data[v] = data.get(v, 0) + 1
    code = code_refs(d)
    out = []
    for lo, hi in data_ranges(d):
        for m in CAND.finditer(d, lo, hi):
            raw, off = m[0][:-1], m.start()
            dec = decode(raw)
            refs = data.get(off - BASE, 0) + code.get(off - BASE, 0)
            if not dec or not any(c >= 0x80 for c in raw) or not is_text(dec[0], raw, refs, off):
                continue
            end = m.end()
            while end < len(d) and d[end] == 0:
                end += 1
            out.append({"id": f"eboot:{off:06x}", "off": off, "enc": dec[1], "refs": refs, "slot": end - off,
                        "jp": dec[0]})
    for off in ROW_START:
        raw = d[off:d.index(b"\0", off)]
        end = off + len(raw)
        while d[end] == 0:
            end += 1
        out.append({"id": f"eboot:{off:06x}", "off": off, "enc": "cp932", "refs": data.get(off - BASE, 0)
                    + code.get(off - BASE, 0), "slot": end - off, "jp": raw.decode("cp932")})
    return sorted(out, key=lambda x: x["off"])


if __name__ == "__main__":
    d = Path(sys.argv[1] if len(sys.argv) > 1 else ELF).read_bytes()
    for x in strings(d):
        print(x["id"], x["refs"], x["slot"], x["enc"], repr(x["jp"]))
