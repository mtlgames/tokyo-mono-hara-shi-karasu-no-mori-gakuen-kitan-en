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
CHOICE_BAR_DY = 3         # choice cursor bar y on row 0 = rows' y0 (89 in a dialogue choice) + 3; fill y-6..y+h+6
CHOICE_BAR_H = 10.0
NAME_TAB_CENTRE = 24  # Hira (30 px) at x 9, Kata/ABC (32) at 8: ink 2 px clear of the borders (f003880 name_entry)


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
    # per frame (0x089F0A1C) target x = 116 - 32 * sel -> target y = box y + CHOICE_BAR_DY + CHOICE_PITCH * sel. The
    # box y (0x089F04B0's v1, the rows' y0) sits at 0x14($sp); a fixed y 92 missed the survey choice (rows at y ~33).
    assert CHOICE_PITCH == 20.0
    p.asm(0x089F0A1C, "lwc1 $f2, 0x14($sp); lbu $v0, 0x39ec($v0); lw $a0, 0xa8($v1); sll $t0, $v0, 4;"
          f"sll $v0, $v0, 2; addu $v0, $v0, $t0; addiu $v0, $v0, {CHOICE_BAR_DY}; mtc1 $v0, $f1; cvt.s.w $f0, $f1;"
          "move $a1, $sp; add.s $f0, $f0, $f2",
          [0x3C0142E8, 0x44811000, 0x90420000 | 0x39EC, 0x8C640000 | 0xA8, 0x03A02821, 0x44820800, 0x46800820,
           0x3C01C200, 0x44810800, 0x46010002, 0x46020000])
    p.asm(0x089F0A4C, "swc1 $f0, 4($sp)", [0xE7A00000])
    # name entry mode tabs (Hira/Kata/ABC, eboot 2b1518..): drawn at x 10.0 (0x0883A500), tabs inside x 8-39, so
    # "Kata"/"ABC" (32 px) lost their last letter and a fixed x left "Hira" on the selected tab's border: centred
    right_align(p, 0x0883A508, NAME_TAB_CENTRE, centre=True)
    # phone Profile Book submenu labels (Locked/Profile/Report Card) at x 294.0: "Report Card" touched the bezel (~374)
    for site in (0x0893D38C, 0x0893D5E4, 0x0893D660, 0x0893D6C8):
        p.asm(site, f"lui $at, {hi(290.0):#x}", [0x3C014393])
    # school/city map help bar "✕ Back ○ OK": Back at x 392.0 ran into the ○ icon (~425): x 388 (✕ ends ~386)
    for site in (0x08952650, 0x08952A68):
        p.asm(site, f"lui $at, {hi(388.0):#x}", [0x3C0143C4])
    choice_bar_px(p)
    menu_right(p)
    hud_name(p)
    shadow(p)
    status_labels(p)
    status_name(p)
    ticker(p)
    defense_value(p)
    money_plate(p)
    phone_settings(p)
    help_bars(p)
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
    # The buffer is zeroed only to sp+0x1d and strncpy adds no NUL, so a name of 15+ chars matched nothing (id -1) and
    # a {px} line after it crashed (ms01_00:022:08, Soft Girl's Voice): zero it to sp+0x24 (17 chars + NUL fit).
    for sw, lw, clr in ((0x089E8544, 0x089E8640, 0x089E8554), (0x089E86A4, 0x089E879C, 0x089E86B4)):
        p.asm(sw, "sw $s0, 0x48($sp)", [0xAFB00020])
        p.asm(lw, "lw $s0, 0x48($sp)", [0x8FB00020])
        p.asm(clr, "addiu $v1, $sp, 0x24", [0x27A3001D])
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
    jal_to(p, 0x089F09DC, BAR_MAKE, va)
    # state 2: width = len (px), was len*18
    p.asm(0x089FE708, "nop; nop; nop", [0x00021900, 0x00021040, 0x00431021])


# Main/pause menu labels (obj+0x29+0x20*i, 7 rows): x is a constant per row (0x08924524.., 432 - the JP width in
# advfont14), so English starts where the JP did and runs off screen. The draw loop calls the text wrapper at
# 0x08923BFC (a0 font, a1 string, f12 x, f13 y); a stub sums the string's advfont14 advances and sets
# f12 = MENU_RIGHT - width before jumping on to the wrapper.
DRAW_TEXT = 0x08816988
MENU_RIGHT = 432
PXRIGHT = """
    move $t8, $ra
    bal here
here:
    move $t9, $ra
    move $ra, $t8
    move $t3, $a1
    move $t2, $zero
ch:
    lbu $t4, 0($t3)
    beq $t4, $zero, done
    addiu $t3, $t3, 1
    sltiu $t6, $t4, 0x81
    addu $t5, $t9, $t4
    bne $t6, $zero, one
    addiu $t3, $t3, 1
one:
    lbu $t5, {tbl}($t5)
    addu $t2, $t2, $t5
    b ch
done:{half}
    ori $t6, $zero, {right}
    subu $t2, $t6, $t2{keep}
    mtc1 $t2, $f12
    cvt.s.w $f12, $f12
    lui $t5, {dhi}
    ori $t5, $t5, {dlo}
    addu $t5, $t9, $t5
    jr $t5
"""  # shortcut: a byte >= 0x81 counts as a 2-byte SJIS char (half-width kana would skip a byte); labels are ASCII
KEEP_X = """
    trunc.w.s $f0, $f12
    mfc1 $t6, $f0
    slt $t7, $t6, $t2
    movn $t2, $t6, $t7"""  # x = min(x, right - width): text only moves left when it would pass `right`
# School floor/room list (free movement, field_ch01): x 383 from obj+0xb2 (animated), ~90 px to the screen edge;
# room names run to 159 px. Draw call 0x088E4168: long names shift left to end at FLOOR_RIGHT. The red panel is
# x 378-480 (same list on the city map), so names stay within 97 px (start >= 380; short forms, fit-queue).
FLOOR_RIGHT = 477
FLOOR_MAX = 97


def jal_to(p, site, target, va, op=0x0C000000):
    """Point the relocated jal (op 0x08000000: j) at `site` (calling `target`) at vaddr va in the added segment."""
    import eboot
    assert site in p.rel, "the jal must be relocated so the new target moves with the load base"
    o = p.off(site)
    old = bytes(p.d[o:o + 4])
    assert struct.unpack("<I", old)[0] == op | ((target - eboot.LOAD) >> 2)
    new = struct.pack("<I", op | (va >> 2))
    p.d[o:o + 4] = new
    p.log.append((o, old, new, f"{site:08x} jal stub (vaddr {va:x})"))


def right_align(p, site, right, keep=False, centre=False):
    """Stub (code + advfont14 width table, 0x200 bytes in the added segment) for the DRAW_TEXT call at `site`:
    f12 = right - width, or with keep min(f12, right - width); with centre f12 = right - width / 2."""
    import eboot
    import insert
    w = insert.font_widths("advfont14")
    table = bytes(w.get(c, 0 if c < 0x20 else 14) for c in range(256))  # >= 0x81: one 14 px SJIS cell
    va = eboot.add_segment(p.d, bytes(0x200))
    off = len(p.d) - 0x200
    here = eboot.LOAD + va + 12
    delta = (DRAW_TEXT - here) & 0xFFFFFFFF
    src = PXRIGHT.format(tbl=0x100 - 12, dhi=delta >> 16, dlo=delta & 0xFFFF, right=right,
                         keep=KEEP_X if keep else "", half="\n    srl $t2, $t2, 1" if centre else "")
    code = bytes(p.ks.asm(src, eboot.LOAD + va)[0])
    assert len(code) <= 0x100, len(code)
    p.d[off:off + len(code)] = code
    p.d[off + 0x100:off + 0x200] = table
    jal_to(p, site, DRAW_TEXT, va)


def menu_right(p):
    right_align(p, 0x08923BFC, MENU_RIGHT)
    right_align(p, 0x088E4168, FLOOR_RIGHT, keep=True)


# Dungeon/battle HUD player name: sprintf(buf, "%s %s", surname 0x089D3AB8(0), given 0x089D3A84(0)) at 0x088A6550,
# drawn by `j VDRAW` at 0x088A69C8 (x 5, y obj+0x248) down the dark strip under the LV gauge. Horizontal it lay
# over the AP gauge: given name first (D1) and a stub moves it HUD_NAME_DY px down, onto the strip's top.
VDRAW = 0x08816F18
HUD_NAME_DY = 48.0
HUDNAME = """
    lui $at, {dy}
    mtc1 $at, $f0
    add.s $f13, $f13, $f0
    move $t8, $ra
    bal here
here:
    move $t9, $ra
    move $ra, $t8
    lui $t5, {dhi}
    ori $t5, $t5, {dlo}
    addu $t5, $t9, $t5
    jr $t5
"""


# Status page (main menu > report card, scene `report`): 49 labels made by 0x0892B6B0(obj, a1 x, a2 y, a3 colour,
# t0 systemtext(id)) with x as `addiu $a1, $zero, X` immediates (the JP x centres each label in its grid cell at 14 px
# a char; list: tools/debug/labels.py). English: centre the labels that sit in grid cells by their advfont14
# width, never left of the cell (too-wide names run right, over the divider; values start ~20 px further right).
# (x-immediate site, label en, cell left, cell right); cells measured on work/qa/warp/jp/report/final.png.
STATUS_CELLS = [
    (0x0892B940, "Stats", 5, 61), (0x0892B964, "Value", 64, 116), (0x0892B9AC, "Subject", 249, 306),
    (0x0892B9D0, "Grade", 309, 360),
    # cells drawn from 16 px frame tiles by code (no layout found to widen): short forms, full names in fit-queue
    (0x0892BBEC, "Stamina", 5, 61), (0x0892BC10, "Reflex", 5, 61), (0x0892BC34, "Will", 5, 61),
    (0x0892BC58, "Speed", 5, 61), (0x0892BC7C, "Judgmt", 5, 61),
    (0x0892BCAC, "Jpn.", 249, 306), (0x0892BCD0, "Math", 249, 306), (0x0892BCF4, "Lang.", 249, 306),
    (0x0892BD18, "P.E.", 249, 306), (0x0892BD3C, "Soc. St.", 249, 306), (0x0892BD60, "Health", 249, 306),
    (0x0892BD84, "Biology", 249, 306),
    # top-right box: labels left of the values' divider (~x 378); JP centred ~x 316
    (0x0892B848, "Current Lv", 249, 377), (0x0892B86C, "HP Current/Max", 249, 377), (0x0892B8B0, "AP Max", 249, 377),
    (0x0892B8D4, "Arcane Eye Max", 249, 377), (0x0892B8F8, "EXP to Next Lv", 249, 377),
]
STATUS_LEFT = [(0x0892B818, 80, 76),   # Condition: 4 px left, clear of the value ("Name": status_name)
               (0x0892D0CC, 406, 372), (0x0892DCC0, 406, 372)]  # Forte (得意科目) value: room for "Social Studies"
# The value columns (stats x 82, subjects 325, ▲ at -14, a 0's ▼ at +20) stay at the original x: worker 8 moved them
# right (89/336, ▼ +16) for wide names, which put the ▼ on the Summary divider; the names are short forms now.


def status_labels(p):
    import insert
    import json
    w = insert.font_widths("advfont14")
    st = Path(__file__).resolve().parents[1] / "script" / "tables" / "systemtext.json"
    ens = {e.get("en") for e in json.loads(st.read_text(encoding="utf-8"))}
    for site, en, left, right in STATUS_CELLS:
        assert en in ens, f"status label {en!r} is no longer a systemtext string: update STATUS_CELLS"
        o = p.off(site)
        old = struct.unpack_from("<I", p.d, o)[0]
        assert old >> 16 == 0x2405, hex(old)
        x = max(left + 1, (left + right - sum(w[ord(c)] for c in en)) // 2)
        # guard only: "Social St." (64 px, 57 px cell) crossed its divider by its "." (now "Soc. St."), "Willpower" (68) too
        assert sum(w[ord(c)] for c in en) <= right - left + 7, f"status label {en!r} wider than its cell"
        p.asm(site, f"addiu $a1, $zero, {x}", [old])
    for site, x0, x in STATUS_LEFT:
        p.asm(site, f"addiu $a1, $zero, {x}", [0x24050000 | x0])


# Status page name box (labels made at 0x0892CFB8..0x0892D034, same maker 0x0892B6B0): furigana surname/given at
# (114, 10)/(175, 10) and surname/given at (117, 32)/(177, 32) in two fixed slots, so English names overlapped and
# read surname first. English: the furigana and the "Name" label go off screen, the first slot shows the whole name
# "given surname" (D1) from x 80 (stub: sprintf into a buffer in the added segment), the second slot an empty string.
SURNAME, GIVEN, SPRINTF = 0x089D3AB8, 0x089D3A84, 0x08A82800
NAME_X = 80
REPORT_NAME_X = 324  # report card Name row, "Name" label off screen (box inside x ~319-471)
OFFSCREEN = 600
# A whole name wider than NAME_MAX_PX (sysfont18) ran out of both boxes ("WWWWW WWWWW" 189 px; status box x 80-~231,
# report card 324-469): the stub then returns the given name alone. "Kazuki Shichidai" is 143 px.
NAME_MAX_PX = 145
NAME_CELL = 18
FULLNAME = """
    move $t8, $ra
    bal here
here:
    addiu $sp, $sp, -16
    sw $t8, 0($sp)
    sw $s0, 4($sp)
    sw $s1, 8($sp)
    sw $a0, 12($sp)
    move $s0, $ra
    lui $t5, {sur_hi}
    ori $t5, $t5, {sur_lo}
    addu $t5, $s0, $t5
    jalr $t5
    move $s1, $v0
    lw $a0, 12($sp)
    lui $t5, {giv_hi}
    ori $t5, $t5, {giv_lo}
    addu $t5, $s0, $t5
    jalr $t5
    move $a2, $v0
    move $a3, $s1
    move $s1, $v0
    addiu $a0, $s0, {buf}
    addiu $a1, $s0, {fmt}
    lui $t5, {spr_hi}
    ori $t5, $t5, {spr_lo}
    addu $t5, $s0, $t5
    jalr $t5
    addiu $t0, $s0, {buf}
    move $t2, $zero
ch:
    lbu $t4, 0($t0)
    beq $t4, $zero, done
    addiu $t0, $t0, 1
    sltiu $t6, $t4, 0x80
    beq $t6, $zero, sjis
    addu $t5, $s0, $t4
    lbu $t5, {t1}($t5)
    b add
sjis:
    addiu $t3, $t4, -0x81
    sltiu $t3, $t3, 2
    beq $t3, $zero, other
    lbu $t6, 0($t0)
    sll $t4, $t4, 8
    addu $t5, $s0, $t4
    addu $t5, $t5, $t6
    lbu $t5, {t81}($t5)
    b skip
other:
    addiu $t5, $zero, {cell}
skip:
    addiu $t0, $t0, 1
add:
    addu $t2, $t2, $t5
    b ch
done:
    addiu $v0, $s0, {buf}
    sltiu $t6, $t2, {maxw}
    movz $v0, $s1, $t6
    lw $ra, 0($sp)
    lw $s0, 4($sp)
    lw $s1, 8($sp)
    addiu $sp, $sp, 16
    jr $ra
"""
EMPTY = """
    move $t8, $ra
    bal here
here:
    addiu $v0, $ra, {empty}
    jr $t8
"""


def name_widths():
    """Width tables for FULLNAME (sysfont18, the name font): ASCII bytes, then the 0x81 and 0x82 SJIS pages by
    second byte (the English stand-ins: fontpatch.fw); any other double-byte char counts NAME_CELL."""
    import fontpatch
    import insert
    w = insert.font_widths("sysfont18")
    t = bytearray([0] * 0x20 + [NAME_CELL] * 0xE0) + bytearray([NAME_CELL] * 0x200)
    for c, px in w.items():
        t[c] = px
        lead, second = fontpatch.fw(chr(c)).encode("cp932")
        if lead in (0x81, 0x82):
            t[0x100 * (lead - 0x80) + second] = px
    return bytes(t)


def status_name(p):
    import eboot
    # code 0x00-0x13F, EMPTY 0x140, "%s %s\0" + empty string at 0x160, name buffer 0x170-0x1FF, name_widths() 0x200
    size, e, fmt, buf = 0x500, 0x140, 0x160, 0x170
    va = eboot.add_segment(p.d, bytes(size))
    off = len(p.d) - size
    ram = eboot.LOAD + va
    here = ram + 12  # bal at +4, its nop at +8 (both stubs start the same way)
    rel = lambda t: ((t - here) & 0xFFFFFFFF)
    a = FULLNAME.format(sur_hi=rel(SURNAME) >> 16, sur_lo=rel(SURNAME) & 0xFFFF, giv_hi=rel(GIVEN) >> 16,
                        giv_lo=rel(GIVEN) & 0xFFFF, spr_hi=rel(SPRINTF) >> 16, spr_lo=rel(SPRINTF) & 0xFFFF,
                        buf=buf - 12, fmt=fmt - 12, t1=0x200 - 12, t81=0x300 - 0x8100 - 12, cell=NAME_CELL,
                        maxw=NAME_MAX_PX + 1)
    code = bytes(p.ks.asm(a, ram)[0])
    assert len(code) <= e, len(code)
    b = bytes(p.ks.asm(EMPTY.format(empty=fmt + 6 - (e + 12)), ram + e)[0])
    p.d[off:off + len(code)] = code
    p.d[off + e:off + e + len(b)] = b
    p.d[off + fmt:off + fmt + 7] = b"%s %s\0\0"
    p.d[off + 0x200:off + 0x500] = name_widths()
    jal_to(p, 0x0892CFF4, SURNAME, va)
    jal_to(p, 0x0892D018, GIVEN, va + e)
    p.asm(0x0892D000, f"addiu $a1, $zero, {NAME_X}", [0x24050075])
    p.asm(0x0892CFB8, f"addiu $a1, $zero, {OFFSCREEN}", [0x24050072])
    p.asm(0x0892CFDC, f"addiu $a1, $zero, {OFFSCREEN}", [0x240500AF])
    p.asm(0x0892B7F4, f"addiu $a1, $zero, {OFFSCREEN}", [0x24050050])
    # the same box rebuilt for the shown character (L/R, report card): 0x0892DBCC..0x0892DC78, a0 = character id
    jal_to(p, 0x0892DC2C, SURNAME, va)
    jal_to(p, 0x0892DC5C, GIVEN, va + e)
    p.asm(0x0892DC38, f"addiu $a1, $zero, {NAME_X}", [0x24050075])
    p.asm(0x0892DBD8, f"addiu $a1, $zero, {OFFSCREEN}", [0x24050072])
    p.asm(0x0892DC04, f"addiu $a1, $zero, {OFFSCREEN}", [0x240500AF])
    # report card page Name row: surname at (381, 41), given at (427, 41) overprinted; whole name from REPORT_NAME_X
    # (player 0x0892D660.., shown character 0x0892DED4..). Teacher row value x 381 touched the "Teacher" label.
    for sur, giv, xsite in ((0x0892D660, 0x0892D684, 0x0892D66C), (0x0892DED4, 0x0892DEFC, 0x0892DEE0)):
        jal_to(p, sur, SURNAME, va)
        jal_to(p, giv, GIVEN, va + e)
        p.asm(xsite, f"addiu $a1, $zero, {REPORT_NAME_X}", [0x2405017D])
    for site in (0x0892D768, 0x0892E120):
        p.asm(site, "addiu $a1, $zero, 377", [0x2405017D])
    # the "Name" label goes (the full name needs the row); Club/Teacher labels stay at 323 (box inside x 320-469)
    p.asm(0x0892BE60, f"addiu $a1, $zero, {OFFSCREEN}", [0x24050143])
    # Club value: centred in a 98 px field from x 373, so "Go-Home Club" (106 px) ran from 369 over the right frame:
    # field from 364 (x 360-466, clear of "Club" ending at 355)
    for site in (0x0892D724, 0x0892DF90):
        p.asm(site, "addiu $s0, $s0, 364", [0x26100175])


# ADV text shadow: the canvas draw (speaker name, dialogue lines, captions) sets the text colour as GE material
# ambient colour/alpha (cmds 0x55/0x58 written to the display list at GE_STATE+0x74, cached at GE_STATE+0x1CC), then
# tail-jumps to VDRAW at 0x089F90B8. White English text vanished over white windows and skies (qa-findings §Worker
# 17): the stub first draws the same text in black (same alpha, so fades match) at each SHADOW offset, then restores
# the colour and jumps on to VDRAW with the original arguments.
# `lui 0x76; addiu 0x4740` (0x089F8FB8): data relocations are relative to seg1 (vaddr 0x2C3B00), so RAM is
# LOAD + 0x2C3B00 + 0x764740 (read back from PPSSPP: lui 0x0923, addiu 0xC240), not LOAD + 0x764740
GE_STATE = 0x0922C240
SHADOW = [(1.0, 0.0), (0.0, 1.0), (1.0, 1.0)]  # a 1 px drop shadow alone still lost words over white windows
SHADOW_COLOUR = """
    lw $t3, 0x74($t9)
    sll $t1, $t0, 8
    srl $t1, $t1, 8
    lui $t4, 0x5500
    or $t4, $t4, $t1
    sw $t4, 0($t3)
    srl $t1, $t0, 24
    lui $t4, 0x5800
    or $t4, $t4, $t1
    sw $t4, 4($t3)
    addiu $t3, $t3, 8
    sw $t3, 0x74($t9)
    sw $t0, 0x1cc($t9)"""  # t0 = colour (ABGR), t9 = GE_STATE: emit AMC + AMA, update the cache
SHADOW_ARGS = """
    lw $a0, 4($sp)
    lw $a1, 8($sp)
    lw $a2, 12($sp)
    lwc1 $f12, 16($sp)
    lwc1 $f13, 20($sp)
    lw $t9, 28($sp)
    lui $t6, {d_hi}
    ori $t6, $t6, {d_lo}
    subu $t5, $t9, $t6"""  # t5 = VDRAW (GE_STATE - d)
SHADOW_HEAD = """
    addiu $sp, $sp, -32
    sw $ra, 0($sp)
    sw $a0, 4($sp)
    sw $a1, 8($sp)
    sw $a2, 12($sp)
    swc1 $f12, 16($sp)
    swc1 $f13, 20($sp)
    bal here
here:
    lui $t9, {st_hi}
    ori $t9, $t9, {st_lo}
    addu $t9, $ra, $t9
    sw $t9, 28($sp)
    lw $t0, 0x1cc($t9)
    sw $t0, 24($sp)
    lui $t1, 0xff00
    and $t0, $t0, $t1""" + SHADOW_COLOUR
SHADOW_PASS = SHADOW_ARGS + """
    lui $at, {dx}
    mtc1 $at, $f0
    add.s $f12, $f12, $f0
    lui $at, {dy}
    mtc1 $at, $f0
    add.s $f13, $f13, $f0
    jalr $t5"""
SHADOW_TAIL = """
    lw $t9, 28($sp)
    lw $t0, 24($sp)""" + SHADOW_COLOUR + SHADOW_ARGS + """
    lw $ra, 0($sp)
    addiu $sp, $sp, 32
    jr $t5"""


def shadow(p):
    import eboot
    size = 0x200
    va = eboot.add_segment(p.d, bytes(size))
    off = len(p.d) - size
    ram = eboot.LOAD + va
    st = (GE_STATE - (ram + 4 * 9)) & 0xFFFFFFFF  # $ra after the bal (7 saves, bal, its nop)
    d = GE_STATE - VDRAW
    args = dict(d_hi=d >> 16, d_lo=d & 0xFFFF)
    src = (SHADOW_HEAD.format(st_hi=st >> 16, st_lo=st & 0xFFFF)
           + "".join(SHADOW_PASS.format(dx=hex(hi(dx)), dy=hex(hi(dy)), **args) for dx, dy in SHADOW)
           + SHADOW_TAIL.format(**args))
    code = bytes(p.ks.asm(src, ram)[0])
    assert len(code) <= size, len(code)
    p.d[off:off + len(code)] = code
    jal_to(p, 0x089F90B8, VDRAW, va, op=0x08000000)


def hud_name(p):
    import eboot
    # the same sprintf for the second "%s %s" (0x08927B18): given name first there too
    p.asm(0x088A655C, "move $a2, $v0", [0x02003021])
    p.asm(0x088A6564, "move $a3, $s0", [0x00403821])
    p.asm(0x08927B24, "move $a2, $v0", [0x02203021])
    p.asm(0x08927B2C, "move $a3, $s1", [0x00403821])
    va = eboot.add_segment(p.d, bytes(0x40))
    off = len(p.d) - 0x40
    ram = eboot.LOAD + va
    delta = (VDRAW - (ram + 24)) & 0xFFFFFFFF  # bal at +16 (nop +20): $ra = ram + 24
    code = bytes(p.ks.asm(HUDNAME.format(dy=hi(HUD_NAME_DY), dhi=delta >> 16, dlo=delta & 0xFFFF), ram)[0])
    assert len(code) <= 0x40, len(code)
    p.d[off:off + len(code)] = code
    jal_to(p, 0x088A69C8, VDRAW, va, op=0x08000000)


# OXAS news ticker (phone/dungeon OXAS top page): the siteinfo items are joined into one string drawn at x 170; up to
# 32 bytes it is static (0x08940AF8), longer it scrolls a 32-byte window in 2-byte steps (0x08940ECC reset,
# 0x08940F18 window end). 32 JP bytes are 16 chars (~175 px); 32 ASCII chars run ~35 px past the panel.
TICKER_BYTES = 24  # 26 ended at x 365 of the panel's 367 (work/qa/warp/w6/dun_oxas); even: the scroll steps 2 bytes


def ticker(p):
    n = TICKER_BYTES
    p.asm(0x08940AF8, f"sltiu $v0, $v0, {n + 1}", [0x2C420021])
    p.asm(0x08940ECC, f"addiu $s0, $s0, {n}", [0x26100020])
    p.asm(0x08940F18, f"addiu $s0, $s2, {n}", [0x26500020])


# Item details armor line (0x089B20A8): label eboot:2b5168 drawn from x0 = centre - strlen * 3.5, its "%3d" value at
# x0 + 42 (防御力 = 3 x 14 px). English "Defense" is 56 px in advfont14, so the value ran into it ("Defense87"):
# value at x0 + 56 (the %4d spaces are the gap); the label keeps 4 trailing spaces so strlen centres label + value.
# Weapon line (eboot:2b5148, vaddr 0x2B5088): "%4d" attack at x0 + 42, "%3d" AP cost at x0 + 140; "Attack" is 46 px,
# so a 4-digit attack touched it ("Attack3150"): attack at + 50, "AP Cost" moved right by spaces in the label (ends
# at 154), AP value at + 154. Each line has two copies of the draw (item details, and a second panel at 0x089B23xx).
DEF_VALUE_DX = 56
ATK_VALUE_DX = 50
AP_VALUE_DX = 154


def defense_value(p):
    for site in (0x089B2180, 0x089B2494):
        p.asm(site, f"addiu $v0, $v0, {DEF_VALUE_DX}", [0x2442002A])
    for site in (0x089B201C, 0x089B26B4):
        p.asm(site, f"addiu $v0, $v0, {ATK_VALUE_DX}", [0x2442002A])
    for site in (0x089B207C, 0x089B2774):
        p.asm(site, f"addiu $v0, $v0, {AP_VALUE_DX}", [0x2442008C])


# Menu money plate (0x08922F94 labels, 0x08923218 number): the 8-digit number ends at x 148 (t0 = 140), the unit
# label (systemtext 0647) at x 150. "yen" (25 px vs 円 14) ran into the plate's arrow tip (~170): both move left;
# 9,999,999 then starts ~2 px right of the fixed colon of "Money:" (x 67).
MONEY_DX = 7


def money_plate(p):
    p.asm(0x08923224, f"addiu $t0, $zero, {140 - MONEY_DX}", [0x2408008C])
    p.asm(0x08923000, f"addiu $a2, $zero, {150 - MONEY_DX}", [0x24060096])


# Phone settings values (scene `phone_set`): row r draws its values from x 251 + start, each next one at the previous
# end (measured width) + gap; (start, gap) halfwords for the 10 rows at 0x08AAF4E8 (copied to the stack at 0x08942E6C).
# English "Long Normal Short" ran to x 380 and "1 2 3 Instant" to ~371, past the phone screen (~372).
PHONE_ROWS = 0x08AAF4E8
PHONE_FIX = {0: (12, 8), 5: (0, 5), 6: (0, 5)}  # text speed, aiming cursor speed, emotion input hold


def phone_settings(p):
    o = p.off(PHONE_ROWS)
    old = bytes(p.d[o:o + 40])
    assert struct.unpack("<20h", old) == (12, 12, 26, 24, 4, 6, 4, 6, 4, 6, 4, 10, 4, 10, 14, 24, 14, 24, 4, 4)
    rows = list(struct.unpack("<20h", old))
    for r, (start, gap) in PHONE_FIX.items():
        rows[2 * r:2 * r + 2] = start, gap
    new = struct.pack("<20h", *rows)
    p.d[o:o + 40] = new
    p.log.append((o, old, new, f"{PHONE_ROWS:08x} phone settings value x (start, gap) per row"))


# Menu help bars: 0x089D0850(bar, slot, x, y) places a slot (button icon at x+2..x+13, label from x+16), 0x089D086C(bar,
# slot, systemtext row) sets its label; each menu lays its slots out with immediates (`addiu $a2, $zero, x`).
# English labels ran under the next icon (cards "Remove Range", equip). Each bar keeps its rightmost slot and moves
# the others left just enough for the widest label the slot can show (rows from the T calls after the bar's P calls).
# Bars: (site of the x immediate, original x, labels) in x order.
HELP_GAP = 16 + 3
HELP_BARS = [
    [(0x089BADB8, 252, ["Remove"]), (0x089BADEC, 300, ["Range", "Details"]), (0x089BAE20, 352, ["Back"]),
     (0x089BAE54, 402, ["Select"])],  # cards
    [(0x089C0044, 252, ["Remove"]), (0x089C0078, 307, ["Details", "Range"]), (0x089C00AC, 358, ["Back"]),
     (0x089C00E0, 408, ["Select", "OK"])],  # equip
    [(0x089C6B40, 252, ["Remove", "Take All"]), (0x089C6B74, 313, ["Details"]), (0x089C6BA8, 360, ["Back"]),
     (0x089C6BDC, 406, ["Get"])],
    [(0x089CDDE0, 268, ["Details", "Weapon", "Armor", "Gear Details", "Enhance Effect"]),
     (0x089CDE18, 348, ["Back"]), (0x089CDDFC, 398, ["Select", "OK"])],
]
HELP_LEFT = 20 + HELP_GAP + 61  # end of the "Category" label in the SELECT slot at x 20 (32 in equip)


def help_layout(xs, widths):
    """New x per slot: the last stays, each other ends its label HELP_GAP before the next icon, never moves right."""
    out = list(xs)
    for k in range(len(xs) - 2, -1, -1):
        out[k] = min(xs[k], out[k + 1] - HELP_GAP - widths[k])
    return out


assert help_layout([252, 300, 352, 402], [55, 47, 34, 41]) == [209, 283, 349, 402]


def help_bars(p):
    import insert
    import json
    w = insert.font_widths("advfont14")
    st = Path(__file__).resolve().parents[1] / "script" / "tables" / "systemtext.json"
    ens = {e.get("en") for e in json.loads(st.read_text(encoding="utf-8"))}
    for bar in HELP_BARS:
        for _, _, labels in bar:
            assert set(labels) <= ens, f"help label {labels} is no longer a systemtext string: update HELP_BARS"
        xs = help_layout([x for _, x, _ in bar], [max(sum(w[ord(c)] for c in s) for s in ls) for _, _, ls in bar])
        assert xs[0] >= HELP_LEFT, (bar, xs)
        for (site, x0, _), x in zip(bar, xs):
            if x != x0:
                p.asm(site, f"addiu $a2, $zero, {x}", [0x24060000 | x0])


if __name__ == "__main__":
    p = Patcher()
    before = bytes(p.d)
    patch(p)
    for k in range(0, len(before), 4):
        if before[k:k + 4] != p.d[k:k + 4]:
            print(f"{k - 0xC0 + 0x08804000:08x} {before[k:k + 4][::-1].hex()} -> {bytes(p.d[k:k + 4])[::-1].hex()}")
