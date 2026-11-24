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
    choice_bar_px(p)
    # choice keys: LEFT (0x80) = next, RIGHT (0x20) = previous -> DOWN (0x40), UP (0x10)
    p.asm(0x089F2A10, "andi $v0, $v0, 0x40", [0x30420080])
    p.asm(0x089F2A2C, "andi $v0, $v0, 0x10", [0x30420020])
    # player-name splice passes 0x089EBEE0 / 0x089EC200 / 0x089EC4EC (whole message, pmyh pnyh pm1 pn1 pm pn px):
    # before each splice after the first they clear only 33 bytes of the 161-byte scratch at sp, then strncpy(sp,
    # text, pos) leaves no NUL when pos > 32 and strcat runs on into the old text, which still holds the code, so
    # it splices forever and overflows (crash: two name codes past byte 32 of a message, JP never does). Clear all
    # 161 bytes (docs/re/engine.md §Name codes).
    for addr, reg, word in ((0x089EC01C, "s2", 0x27B20021), (0x089EC040, "v1", 0x27A30021),
                            (0x089EC328, "s1", 0x27B10021), (0x089EC348, "v1", 0x27A30021),
                            (0x089EC604, "s2", 0x27B20021), (0x089EC624, "v1", 0x27A30021)):
        p.asm(addr, f"addiu ${reg}, $sp, 0xa1", [word])
    # speaker -> character id lookups 0x089E8540 / 0x089E86A0 (caller 0x089EEAD0): strncpy(sp, name + 2, len - 4)
    # into a 29-byte stack buffer, saved $s0 at sp+0x20. A 17-char English name (34 bytes) overwrote $s0's low half,
    # so the caller stored the id through a bad pointer and the speaker plate stopped changing (18 chars crashed).
    # Save $s0 in the frame's unused sp+0x48 instead: names up to 18 chars (36 bytes, to $s1 at 0x24) are safe.
    for sw, lw in ((0x089E8544, 0x089E8640), (0x089E86A4, 0x089E879C)):
        p.asm(sw, "sw $s0, 0x48($sp)", [0xAFB00020])
        p.asm(lw, "lw $s0, 0x48($sp)", [0x8FB00020])
    return p.d


# choice cursor bar width in px: the bar is made at 0x089F09DC by 0x089FED28(obj, &pos, len, f12) with len =
# (longest option's strlen, ctx+0x668) / 2, and state 2 (0x089FE704) sizes it len*18 (one full-width char a byte
# pair). English options are proportional ASCII, so len*18 misses the text (docs/re/engine.md §Open). A routine in a
# new ELF segment sums each option's glyph advances (sysfont18 table) and passes the longest as len; state 2 uses it
# as is. Options: count u8 ctx+0x39EB, strings ctx+0x3CC + 0xA8*i (read at the `choice` state).
BAR_MAKE = 0x089FED28
CHOICE_BAR_PAD = 8  # px added to the longest option (centres the ink in the fill: work/qa/warp/bar/choice)
PXBAR = """
    move $t8, $ra
    bal here
here:
    move $t9, $ra
    move $ra, $t8
    lbu $t1, 0x39eb($t7)
    addiu $t0, $t7, 0x3cc
    move $a2, $zero
opt:
    beq $t1, $zero, done
    move $t2, $zero
    move $t3, $t0
ch:
    lbu $t4, 0($t3)
    beq $t4, $zero, chdone
    addiu $t3, $t3, 1
    addu $t5, $t9, $t4
    lbu $t5, {tbl}($t5)
    addu $t2, $t2, $t5
    b ch
chdone:
    slt $t6, $a2, $t2
    movn $a2, $t2, $t6
    addiu $t0, $t0, 0xa8
    addiu $t1, $t1, -1
    b opt
done:
    addiu $a2, $a2, {pad}
    lui $t5, {dhi}
    ori $t5, $t5, {dlo}
    addu $t5, $t9, $t5
    jr $t5
"""  # keystone fills each of the 6 delay slots with a nop itself


def choice_bar_px(p):
    import eboot
    import insert
    w = insert.font_widths("sysfont18")
    table = bytes(w.get(c, 0 if c < 0x20 else 18) for c in range(256))
    size = 0x100 + 0x100  # code (assembled below, < 0x100) then the width table
    off = len(p.d) + (-len(p.d) % 64)  # add_segment's file offset for the new data
    va = eboot.add_segment(p.d, bytes(size))
    ram = eboot.LOAD + va
    here = ram + 12  # `here` label: bal sits at ram + 4, so $ra = ram + 12
    delta = (BAR_MAKE - here) & 0xFFFFFFFF
    # pad: ink starts 3 px right of the text x and ends ~2 px past the advance sum; the fill spans x-5..x+w+5
    src = PXBAR.format(tbl=0x100 - 12, dhi=delta >> 16, dlo=delta & 0xFFFF, pad=CHOICE_BAR_PAD)
    code = bytes(p.ks.asm(src, ram)[0])
    # keystone adds one nop per delay slot (6 branches); bal at +4, its nop at +8, so `here` is +12
    assert len(code) == 4 * (PXBAR.count("\n    ") + 6) <= 0x100, len(code)
    p.d[off:off + len(code)] = code
    p.d[off + 0x100:off + 0x200] = table
    # caller: ctx (s0) into t7 instead of `lb v0, 0x668(s0)` (a2 from it is replaced), jal BAR_MAKE -> jal pxbar
    p.asm(0x089F09B8, "move $t7, $s0", [0x82020668])
    site = 0x089F09DC
    assert site in p.rel, "the bar jal must be relocated so the new target moves with the load base"
    o = p.off(site)
    old = bytes(p.d[o:o + 4])
    assert struct.unpack("<I", old)[0] == 0x0C000000 | ((BAR_MAKE - eboot.LOAD) >> 2)
    new = struct.pack("<I", 0x0C000000 | (va >> 2))  # relocated jal: target field holds the vaddr
    p.d[o:o + 4] = new
    p.log.append((o, old, new, f"{site:08x} jal pxbar (vaddr {va:x})"))
    # state 2: width = len (px), was len*18
    p.asm(0x089FE708, "nop; nop; nop", [0x00021900, 0x00021040, 0x00431021])


if __name__ == "__main__":
    p = Patcher()
    before = bytes(p.d)
    patch(p)
    for k in range(0, len(before), 4):
        if before[k:k + 4] != p.d[k:k + 4]:
            print(f"{k - 0xC0 + 0x08804000:08x} {before[k:k + 4][::-1].hex()} -> {bytes(p.d[k:k + 4])[::-1].hex()}")
