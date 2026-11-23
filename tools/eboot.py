"""eboot.py: code patches in the decrypted EBOOT ELF (work/exe/NPJH50215_EBOOT.BIN; docs/re/engine.md).

The ELF is a relocatable PSP module: the loader adds the load base to every word that has a relocation entry
(sections of type 0x700000A0), so a patch must never overwrite such a word with something else. `Patcher.asm`
refuses it. Addresses below are RAM addresses as PPSSPP loads the module (base 0x08804000); file offset =
RAM - 0x08804000 + 0xC0 for the code/rodata segment.

    python -X utf8 tools/eboot.py ADDR [COUNT]   # show words at ADDR and whether each has a relocation
"""
import hashlib
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ELF = ROOT / "work" / "exe" / "NPJH50215_EBOOT.BIN"
ELF_SHA1 = "cf3ccb0a69200d44c40cbb12769e1ac14f7b52a1"
LOAD = 0x08804000
FILE0 = 0xC0  # file offset of vaddr 0


def load():
    d = ELF.read_bytes()
    if hashlib.sha1(d).hexdigest() != ELF_SHA1:
        sys.exit(f"{ELF}: not the PPSSPP dump this project patches (docs/re/pak.md, EBOOT)")
    return bytearray(d)


def relocs(d):
    """Set of RAM addresses whose word the loader relocates."""
    shoff, = struct.unpack_from("<I", d, 0x20)
    shnum, = struct.unpack_from("<H", d, 0x30)
    phoff, = struct.unpack_from("<I", d, 0x1C)
    seg = [struct.unpack_from("<I", d, phoff + 32 * i + 8)[0] for i in range(struct.unpack_from("<H", d, 0x2C)[0])]
    out = set()
    for i in range(shnum):
        _, typ, _, _, off, size = struct.unpack_from("<6I", d, shoff + 40 * i)
        if typ != 0x700000A0:
            continue
        for k in range(0, size, 8):
            r_off, info = struct.unpack_from("<II", d, off + k)
            out.add(LOAD + seg[(info >> 8) & 0xFF] + r_off)
    return out


def pointers(d):
    """{target vaddr: [(kind, site vaddr, addr-base vaddr, hi site or None)]}: every absolute address the loader
    relocates. kind 'word' (R_MIPS_32: the word holds target - base) or 'lo' (R_MIPS_LO16 instruction; its lui is the
    HI16 just before it, or the one of the previous LO16 when several LO16s share one lui)."""
    seg = [s[0] for s in __import__("eboot_text").segments(d)]
    shoff, = struct.unpack_from("<I", d, 0x20)
    shnum, = struct.unpack_from("<H", d, 0x30)
    word = lambda va: struct.unpack_from("<I", d, va + FILE0)[0]
    out, his, last = {}, [], []
    for i in range(shnum):
        _, typ, _, _, off, size = struct.unpack_from("<6I", d, shoff + 40 * i)
        if typ != 0x700000A0:
            continue
        for k in range(0, size, 8):
            r_off, info = struct.unpack_from("<II", d, off + k)
            t, site, base = info & 0xFF, seg[(info >> 8) & 0xFF] + r_off, seg[(info >> 16) & 0xFF]
            if t == 2:
                out.setdefault(word(site) + base, []).append(("word", site, base, None))
            elif t == 5:
                his.append(site)
            elif t == 6:
                last, his = (his or last), []
                lo = word(site) & 0xFFFF
                for a in {((word(h) & 0xFFFF) << 16) + lo - (0x10000 if lo & 0x8000 else 0) + base: h
                          for h in last}.items():  # one entry per target even when several luis share a hi
                    out.setdefault(a[0], []).append(("lo", site, base, a[1]))
    return out


def same_hi(a, b):
    """True if a lui computed for address a also serves b once the module is loaded at LOAD (the loader carries the
    low half of the load base into the HI16 word, so a lo16 may change only inside its rounded hi window)."""
    return (a + LOAD + 0x8000) >> 16 == (b + LOAD + 0x8000) >> 16


def file_off(d, va):
    """File offset of vaddr va (any PT_LOAD segment's file-backed bytes)."""
    for vaddr, off, fsz, _ in __import__("eboot_text").segments(d):
        if vaddr <= va < vaddr + fsz and off:
            return va - vaddr + off
    raise ValueError(f"{va:x} is in no segment's file data")


def add_segment(d, data):
    """Append `data` to the ELF bytearray d as a new PT_LOAD segment placed past the end of every segment's memory
    (past .bss), its program header inserted after the other PT_LOADs (relocations name segments by index: the
    existing ones keep theirs). Returns the new segment's vaddr; its file offset is the old end of file, 64-aligned.
    The program header table must have a free 32-byte slot before the first segment's data (0x94..0xC0 here)."""
    phoff, = struct.unpack_from("<I", d, 0x1C)
    phnum, = struct.unpack_from("<H", d, 0x2C)
    ph = [list(struct.unpack_from("<8I", d, phoff + 32 * i)) for i in range(phnum)]
    first = min(p[1] for p in ph if p[0] == 1)
    if phoff + 32 * (phnum + 1) > first:
        raise ValueError("no room for another program header")
    va = (max(p[2] + p[5] for p in ph if p[0] == 1) + 0x3F) & ~0x3F
    d += bytes(-len(d) % 64)
    off = len(d)
    d += data
    k = max(i for i, p in enumerate(ph) if p[0] == 1) + 1
    ph.insert(k, [1, off, va, 0, len(data), len(data), 6, 0x40])
    for i, p in enumerate(ph):
        struct.pack_into("<8I", d, phoff + 32 * i, *p)
    struct.pack_into("<H", d, 0x2C, phnum + 1)
    return va


class Patcher:
    def __init__(self, d=None):
        self.d = d if d is not None else load()
        self.rel = relocs(self.d)
        from keystone import Ks, KS_ARCH_MIPS, KS_MODE_MIPS32, KS_MODE_LITTLE_ENDIAN
        self.ks = Ks(KS_ARCH_MIPS, KS_MODE_MIPS32 + KS_MODE_LITTLE_ENDIAN)

    def off(self, addr):
        return addr - LOAD + FILE0

    def word(self, addr):
        return struct.unpack_from("<I", self.d, self.off(addr))[0]

    def asm(self, addr, code, expect=None):
        """Assemble `code` (';'-separated, branch targets absolute) at RAM addr and write it. expect: the original
        words (list of ints) as a guard against patching the wrong build."""
        enc = bytes(self.ks.asm(code, addr)[0])
        for k in range(0, len(enc), 4):
            a = addr + k
            if a in self.rel and enc[k:k + 4] != self.d[self.off(a):self.off(a) + 4]:
                raise ValueError(f"{a:08x} has a relocation; patching it would be corrupted at load")
            if expect is not None and self.word(a) != expect[k // 4]:
                raise ValueError(f"{a:08x}: found {self.word(a):08x}, expected {expect[k // 4]:08x}")
        self.d[self.off(addr):self.off(addr) + len(enc)] = enc


if __name__ == "__main__":
    p = Patcher()
    a, n = int(sys.argv[1], 16), int(sys.argv[2]) if len(sys.argv) > 2 else 8
    for k in range(n):
        print(f"{a + 4 * k:08x} {p.word(a + 4 * k):08x}{'  reloc' if a + 4 * k in p.rel else ''}")
