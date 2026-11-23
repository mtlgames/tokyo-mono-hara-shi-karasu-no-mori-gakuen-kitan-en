"""engine.py: the English engine changes to the EBOOT (docs/re/engine.md).

ADV text (dialogue and speaker name) is drawn by the vertical text drawer 0x08816F18(font, str, count, f12 x,
f13 y): one glyph per cell down a column. The ADV gives each message line (max 3) its own canvas, columns right to
left. patch() makes the drawer horizontal and proportional (x advances by each glyph's width from the font, no
vertical-form rotation) and stacks the line canvases top to bottom. Every text the game draws through this drawer
becomes horizontal.

    python -X utf8 tools/engine.py      # apply to the ELF in memory and list the patched words
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from eboot import Patcher  # noqa: E402

LINE_PITCH = 20.0   # px between ADV text lines
NAME_XY = (8.0, 6.0)     # speaker name canvas (original 116, 8: right-hand column)
TEXT_XY = (8.0, 28.0)    # dialogue line 0 canvas (original 84, 8)
CAP_TEXT = (0.0, 32.0)    # location caption text (original 368, 32); insert.py right-aligns it to CAPTION_RIGHT
CHOICE_PITCH = 20.0       # px between .ksf choice rows (original: columns 32 px apart)
CHOICE_BAR_Y = 92.0       # choice cursor bar on row 0 (rows' text at y 89 + CHOICE_PITCH * i); fill drawn y-6..y+h+6
CHOICE_BAR_H = 10.0


def hi(f):
    """lui immediate of a float whose low half is 0."""
    v = struct.unpack("<I", struct.pack("<f", f))[0]
    assert v & 0xFFFF == 0, f
    return v >> 16


def patch(p: Patcher):
    # vertical drawer, after each glyph: x += glyph width (was y += cell height). Newlines never reach it: the ADV
    # gives each line its own canvas (below).
    p.asm(0x0881732C, "add.s $f25, $f25, $f20", [0x4600BDC0])
    # no vertical-form rotation (8815a54 types 1, 2)
    p.asm(0x0881728C, "nop", [0x1043_0037])
    p.asm(0x08817294, "nop", [0x5043_004E])
    # canvas positions (lui of a float constant)
    p.asm(0x089F1838, f"lui $at, {hi(NAME_XY[0]):#x}", [0x3C0142E8])
    p.asm(0x089F1840, f"lui $at, {hi(NAME_XY[1]):#x}", [0x3C014100])
    p.asm(0x089F1F4C, f"lui $at, {hi(TEXT_XY[0]):#x}", [0x3C0142A8])
    p.asm(0x089F1F54, f"lui $at, {hi(TEXT_XY[1]):#x}", [0x3C014100])
    # ADV message setup 0x089F1A20 makes up to 3 line canvases at (x, y), (x-32, y), (x-64, y): make them
    # (x, y + pitch * line)
    for addr, line in ((0x089F1BCC, 1), (0x089F1E88, 2)):
        p.asm(addr, f"lui $at, {hi(LINE_PITCH * line):#x}; mtc1 $at, $f13; add.s $f13, $f22, $f13",
              [0x3C014200 if line == 1 else 0x3C014280, 0x44816000, 0x460CAB01])
    p.asm(0x089F1BDC, "mov.s $f12, $f21", [0x4600B346])
    p.asm(0x089F1E94, "mov.s $f12, $f21", [0x4600B346])
    # ADV text replace pass 0x089EE5FC: 38 (from, to) pairs at 0x08ADC2E8 / 0x08ADC250 turn punctuation into
    # vertical forms (- = ~ !! !? ― 『』 、。 small kana...), which mangles English. Keep only pairs 28-29 (【 】 -> the
    # ❖ name marks).
    p.asm(0x089EE634, "addiu $s4, $zero, 28", [0x0000A021])
    p.asm(0x089EE63C, "addiu $s3, $zero, 112", [0x00009821])
    p.asm(0x089EE74C, "slti $v0, $s4, 30", [0x2A820026])
    # location caption `{...}`: text canvas made at 0x089F12D8 (368, 32), drawn down the fixed red-diamond strip
    # graphic at the right. English: one horizontal line ending left of the strip (insert.py pads it with spaces).
    p.asm(0x089F12D8, f"lui $at, {hi(CAP_TEXT[0]):#x}", [0x3C0143B8])
    p.asm(0x089F12E0, f"lui $at, {hi(CAP_TEXT[1]):#x}", [0x3C014200])
    # .ksf choice menu: the loop at 0x089F0DF4 makes one canvas per option at (x0 - 32 * i, y0), columns right to
    # left. English: rows (x0, y0 + CHOICE_PITCH * i).
    p.asm(0x089F0DE0, f"lui $at, {hi(CHOICE_PITCH):#x}", [0x3C01C200])
    p.asm(0x089F0DF8, "mov.s $f12, $f22; cvt.s.w $f13, $f0", [0x4600AB46, 0x46800320])
    p.asm(0x089F0E0C, "mul.s $f13, $f13, $f23", [0x46176302])
    p.asm(0x089F0E1C, "add.s $f13, $f21, $f13", [0x460CB300])
    # choice cursor: a red bar object (made 0x089F09DC, only user) sized 20 wide x len*18 tall (state 2,
    # 0x089FE704) and moved by lerping x only (state 4, 0x089FE73C). English: len*18 wide x 20 tall, lerp y.
    p.asm(0x089FE728, f"lui $at, {hi(CHOICE_BAR_H):#x}", [0x3C0141A0])
    p.asm(0x089FE730, "swc1 $f0, 0x28($a0)", [0xE4800024])
    p.asm(0x089FE738, "swc1 $f1, 0x24($a0)", [0xE4810028])
    p.asm(0x089FE73C, "lwc1 $f3, 0x1C($a0)", [0xC4830018])
    p.asm(0x089FE740, "lwc1 $f0, 0x14($a0)", [0xC4800010])
    p.asm(0x089FE774, "swc1 $f3, 0xC($a0)", [0xE4830008])
    # bar draw 0x089FE8A0: a translucent fill rect (x-5, y-6, w+10, h+12), then a vertical bracket frame (sprites
    # 0x15-0x17, middle stretched h/40) that can't lie flat: draw only the fill
    # (keystone rejects absolute branch targets this high, and pads `b` with a nop: encode beq $0, $0 by hand)
    p.asm(0x089FE9FC, f".word {0x10000000 | (0x089FEB50 - 0x089FEA00) >> 2:#x}", [0x2402FF8C])
    # per frame (0x089F0A1C) target x = 116 - 32 * sel -> target y = CHOICE_BAR_Y + CHOICE_PITCH * sel
    p.asm(0x089F0A1C, f"lui $at, {hi(CHOICE_BAR_Y):#x}", [0x3C0142E8])
    p.asm(0x089F0A38, f"lui $at, {hi(CHOICE_PITCH):#x}", [0x3C01C200])
    p.asm(0x089F0A4C, "swc1 $f0, 4($sp)", [0xE7A00000])
    # choice keys: LEFT (0x80) = next, RIGHT (0x20) = previous -> DOWN (0x40), UP (0x10)
    p.asm(0x089F2A10, "andi $v0, $v0, 0x40", [0x30420080])
    p.asm(0x089F2A2C, "andi $v0, $v0, 0x10", [0x30420020])
    return p.d


if __name__ == "__main__":
    p = Patcher()
    before = bytes(p.d)
    patch(p)
    for k in range(0, len(before), 4):
        if before[k:k + 4] != p.d[k:k + 4]:
            print(f"{k - 0xC0 + 0x08804000:08x} {before[k:k + 4][::-1].hex()} -> {bytes(p.d[k:k + 4])[::-1].hex()}")
