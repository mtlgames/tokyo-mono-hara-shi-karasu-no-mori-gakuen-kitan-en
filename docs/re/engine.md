# Engine: fonts, text drawing, English path (phase 5)

RAM addresses as PPSSPP loads the EBOOT (module base 0x08804000; file offset = RAM - 0x08804000 + 0xC0).
Disassemble with `disasm.py dis work/exe/main_ram.bin ADDR N --arch mips --base 08804000` (write to a file: the
output is large). Tools: `tools/ipk.py` (font codec), `tools/fontpatch.py` (English encoding + font patch),
`tools/eboot.py` (ELF patcher with relocation guard), `tools/engine.py` (the code patches), debug probes
`tools/debug/{ramfind,fpregs,watchw,bplog}.py`.

## Fonts: `app_init.pak/system/font/*.ipk` (verified: `tools/ipk.py` sheets, `tests/test_engine.py`)
`IPK ` + u32 size, chunks INFO/CLUT/IMG /TERM. INFO: u16 glyphs, u16 2, u16 page w, page h, cell w, cell h, then
6-byte entries sorted by **SJIS code** (ASCII and half-width kana as one byte): u16 code, u8 width (advance), u8 ink
height, u16 0. IMG: u32 ?, u32 page bytes, then 4bpp linear pages (low nibble left), glyph i = cell i of the pages.
| font | cell | page | glyphs | used by |
|---|---|---|---|---|
| sysfont18 | 18x18 | 288x108 | 5473 | ADV dialogue + speaker name (verified: read watch), other screens tbd |
| advfont14 | 14x14 | 448x56 | 5473 | not read during ADV dialogue; tbd |
| advfont08 | 8x8 | 128x280 | 560 | tbd (small labels) |
| mobilefont | 12x12 | 256x96 | 3996 | phone mail (guess) |
Every font has proportional ASCII (widths in INFO). In RAM (PPSSPP, MS00_00 state): sysfont18 0x093DF740,
advfont08 0x094C3BA0, advfont14 0x094CD590, mobilefont 0x095591B0. Font object: +8 = INFO chunk pointer; glyph
lookup 0x08A01C38 (binary search by code), 0x08A01CB0/0x08A01D88 GetGlyph(font, code, out{u, v, w, h});
0x08A01E68 = cell w, 0x08A01E74 = cell h.

## Text drawers (verified: breakpoints, spike builds)
- **0x08816F18 vertical** (font, str, count, f12 x, f13 y): SJIS or single-byte chars, one per cell down
  (y += cell w), 0x0A = next column (x -= 32); 0x08815A54(code) picks rotated vertical forms (types 1, 2).
  Callers: 0x089F90B8 (ADV canvas draw, both speaker name and dialogue lines), 0x0883CBCC, 0x088A69C8 (tbd).
- **0x088169F0 horizontal** (font, str, f12 x, f13 y, f14 first, f15 last char): x += glyph width, 0x0A = next
  line (y += cell h). Public wrapper 0x08816EB0; callers 0x08980B70/0x08980BF4.
- ADV canvases: constructor 0x089F934C (canvas+0xC x, +0x10 y, string at +0x49, char count at +0x258).
  Speaker name canvas made at 0x089F1838 (x 116, y 8). Message setup **0x089F1A20** makes one canvas per line,
  **max 3 lines**: (84, 8), (84-32, 8), (84-64, 8), x/y from 0x089F1F4C. Line count byte ADVctx+0x38C6. Ruby
  (furigana) canvases are placed in the loop at 0x089F1C9C (col pitch 32, 18 px per char): English drops ruby.
- The ADV turns some punctuation into vertical-form codes before drawing (、 -> 8748, 。 -> 8749, ― -> 8744..,
  ❖ name marks 8742/8743). English uses full-width stand-ins, which are not converted (verified in spike).
- Strings `Y_Font Canvas`, `Char Font Canvas`, `Font Area Over!!` (0x08ABBD30..) belong to this module
  (0x089F8000-0x089FA200).

## English path (decided phase 5, D8)
- Script text: full-width SJIS stand-ins for ASCII (`fontpatch.to_sjis_text`; ' -> ’, " -> ”, space -> U+3000);
  every font's full-width Latin glyphs replaced by its own proportional ASCII glyph + width. Tables/EBOOT strings are
  C strings: plain ASCII may work there directly (to verify per screen in the marker build).
- `engine.patch`: vertical drawer advances x by glyph width, rotation skipped; line canvases stacked at y + 20*i,
  x fixed; name at (8, 6), text at (8, 28). Result (spike, MS00_00 block 0): 3 horizontal lines across the screen,
  ~50 sysfont18 chars per line at 464 px.
- Relocations: the EBOOT is a relocatable module; `eboot.Patcher.asm` refuses to change any word with a relocation
  (jal/j/lui of addresses). The build ships the patched **plain ELF** (PPSSPP boots it); re-signing to `~PSP` is
  still to do before release.

## Open (next steps)
- Readability: the left-hand gradient panel (sprites in `adv/talk/adv_talk.g2d`, `adv_emotion2.gim` gradient strips)
  no longer sits behind the text; the right half of each line is over the bare background. Redesign the panel as a
  top band (g2d layout) or add a text shadow.
- The page-wait icon and 0x089F0A1C (x = 116 - 32*n) still use vertical geometry.
- Other vertical drawer callers (0x0883CBCC, 0x088A69C8) and location captions `{...}` (drawn vertically in red
  diamonds, MS00_00 opening): check in the marker build.
- Space width (sysfont18 9 px) looks wide; tune in the font patch if the width gate needs it.
