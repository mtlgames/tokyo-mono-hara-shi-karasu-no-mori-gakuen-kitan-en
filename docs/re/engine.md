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

## Phase 5 marker build findings (verified: `build.py --marker`, `--qa` width tests, shots in work/qa/warp/wg/)
- **ADV replace pass 0x089EE5FC** (verified: table dump + shots): before display, 38 (from, to) SJIS pairs (from
  0x08ADC2E8, to 0x08ADC250) turn text into vertical forms: 、。 small kana ー ─ ！！ ！？ 【 】 ―(runs) ＝ 『』 － ～
  -> 0x8740-0x874F codes. English `-` drew as │, `=` as ‖, `~` as ∫, `!!`/`!?` as ligatures. `engine.patch` limits
  the loop to pairs 28-29 (【 】 -> ❖ name marks, kept: English names show as ❖Name❖ like the original).
  Search is char-aligned (0x089EE554), so no false matches across characters.
- **Chars that break script text** (`insert.SCRIPT_BAD`, the build refuses them): ＠ hangs the ADV before the box
  shows (cause not traced); sysfont18 has no `_` glyph (blank); `\` draws ¥. `{`/`}` are markup (a raw brace would
  be an ASCII command in the .pwx; the build checks every encoded span decodes back).
- **Glyph clipping:** the drawer draws each glyph quad as wide as its advance; nearly every ASCII glyph has 1 px of
  outline past it (clipped, fine), sysfont18 `!` had 3 px (only its dot showed). `fontpatch.patch` widens any
  stand-in whose ink runs 2+ px past the advance (sysfont18 `!` 3 -> 5).
- **Speaker names: max 17 chars** (`insert.NAME_MAX`; 17 W = 306 px shows fine, 18 or 22 chars of any width crash
  PPSSPP when the name appears; a ~40-byte buffer holding `【name】`, not found: not the ctx+0x254 name buffer
  (161 bytes), the replace pass (161), the player-name pass 0x089EE1D8 (161) or canvas set-text 0x089F8900 (510)).
- **Location captions `{...}`:** canvas made at 0x089F12D8 (368, 32); the red-diamond strip is a fixed graphic.
  English: canvas x = 0 (`engine.CAP_TEXT`), `insert` right-aligns the text to x 336 (left of the strip) with spaces;
  max 336 px (build refuses longer).
- Line buffers: ADVctx +0x5C/+0x104/+0x1AC, 0xA8 bytes each (83 stand-in chars); name buffer ctx+0x254.
- 0x08A13C50 is a scene-graph draw loop that calls canvas draw methods (the caption's drawer call came from there).

## Width gate (sysfont18 stand-ins, `tools/widthgate.py` -> `build.py --qa`; widths from `insert.font_widths`)
| variant | budget | how measured |
|---|---|---|
| ADV dialogue line | **464 px**, 3 lines per box | ruler lines at 454/466/476 px: `|` at 472 still draws, 476 clips at the screen edge (x 8 + 472 = 480); 464 keeps an 8 px right margin. work/qa/warp/wg/wg/f003160.png |
| speaker name | **17 chars** (crash at 18), 306 px seen | 17 W shows with ❖ marks |
| location caption | **336 px**, one line | 333 px ruler right-aligned beside the strip |
| choice (.ksf) | 29 bytes ASCII; rows at x 116 (~364 px to the screen edge) | scene `choice` (MS00_01 握手する/しない), rows since `engine.CHOICE_PITCH` |
| system notice (systemtext, boot autosave notes) | **160 bytes** total (161 crashes PPSSPP when the box opens), 4 lines of ~40 chars, ~420 px box | `--qa` byte tests on systemtext:0226:00, work/qa/buf160 |
| city map destinations (EBOOT 2b1ec4..) | ~11 chars visible (list at x ~380, clipped by the screen edge) | work/qa/warp/emove/city_map |
| choice cursor | highlight = len*18 px wide (bytes-based), one row | work/qa/choice_bar_zoom.png |
| dungeon area label (EBOOT `%s　%s`) | ~370 px, one line at x 5 (to the minimap) | bpsweep + marker dun1 |
| HUD label systemtext:0411 (良好, field status) | **40 bytes** ok, 48 crash | `--qa` byte tests, work/qa/buf0411.log |
| other table strings (bytes) | **max(16, 3 x JP bytes), within the column max** (`insert.LONG_ROW/LONG_MIN`): the whole long tour passes with every row at that length | long build tour (below) |

**Menu pixel budgets** (long build vs original, `work/qa/wg_menus1.png` / `wg_menus2.png`, left = original;
menu font ~8 px/char for ASCII, likely advfont14; measure with `insert.font_widths` once the font is confirmed).
Text never wraps or shrinks: past the budget it overlaps the next element or the screen edge.
| screen | element (source) | budget |
|---|---|---|
| every menu | bottom help bar labels (systemtext 0007-0011 etc.) | **fixed slots**: icons stay where the JP layout put them (verified: same x in orig and long); ~40-55 px per label (△/▢/✕/○), ~95 px for the SELECT label. Tight: candidate for engine work (lay icons out by text width) before abbreviating |
| field | floor list right (EBOOT 2b1f28..) | ~90 px (x 384 to screen edge) |
| main menu | items (systemtext 40500-40504, 40045, 40023) | start x fixed per item (JP right-aligned at 432, staggered); text may run to ~470: 90-130 px |
| item list | item names (item.json) | ~145 px (x 62 to the count column ~210) |
| item list | description line (x 260) | ~210 px |
| equip | slot item names | ~150 px (x 92 to the panel edge 240) |
| cards | card name / text | ~200 px (x 248-462), text box 2 lines |
| save/load | help bar only | as above |
| report card | grid cells | label cols ~58 px, value cols ~55 px, 概要 cols ~110 px, top-right labels ~136 px, bottom help lines ~188 px |
| shop | left menu list | ~78 px (x 0-78, clipped); shop talk is the ADV path (464 px) |
| city map | destinations | ~11 chars (above) |

**Long build** (`build.py --long` -> build/karasu_long.iso): every table row max(16, 3 x its JP bytes) long, within
its column's longest line/string; EBOOT strings fill their slot. The first version (column max for every row)
crashed at `field_ch01`: `tools/debug/longbisect.py` blamed `systemtext:0411:00` 良好 (field HUD label; 40 bytes ok,
48 crash). With per-row caps **`warp.py --all --tag long` passes all 52 scenes** (2026-11-24, work/qa/long_tour.log,
shots work/qa/warp/long/). Screens the tour doesn't reach (battle menus beyond the first turn, quests in progress,
album) are unmeasured: the same byte rule applies there unproven; check in phase 8.

## Name codes (verified 2026-11-24: `tools/debug/bpstr.py` breakpoints, warp field_ch01)
- Codes (table 0x2D822C / 0x2D8380 -> strings 0x2B7878..): `pmyh pnyh pm1 pn1 pm pn` (6 name buffers of 161 bytes:
  first char of surname/given name or reading, full surname, given name) and `px` (full name from the speaker's
  character record, 0x1CFB54(speaker | 0x8000)). Splice = find (0x089EBE00, SJIS-aware) + strncpy prefix + strcat
  name + strcat rest, per code until none is left.
- Passes: whole message 0x089EBEE0 / 0x089EC200 / 0x089EC4EC (from 0x089EEE24 for dialogue), per canvas 0x089EE1D8
  (callers 0x089F894C set-text, 0x089F9858 speaker name into a 256-byte stack buffer).
- **Bug fixed in `engine.patch`:** the three message passes clear only 33 bytes of their 161-byte scratch before
  every splice after the first; strncpy leaves no NUL past byte 32, strcat runs on into the stale text (which still
  holds the code) and the splice loops until it overflows: two name codes with the later one past byte 32 of the
  message crashed (ms01_00:011:49 "...right!! {pn} {pm}-kun!!"). JP never has that (max 17). The clear now covers
  161 bytes (6 `addiu rX, sp, 0x21` -> 0xa1).
- Message pass output goes through a 161-byte .bss buffer (0x76299C, then 147 bytes of gap to the name pass output at
  0x762AD0); messages over ~300 bytes after splicing would reach it (English max ~230).

## Open (next steps)
- Readability (polish): the left gradient panel (`adv/talk/adv_talk.g2d`, `adv_emotion2.gim`) covers only x 0-150;
  text has a dark outline and reads on bright backgrounds, so this is polish, not a blocker.
- The page-wait icon now sits bottom-left (x = 116 - 32*n geometry of 0x089F0A1C): polish.
- Other vertical drawer callers (`tools/debug/bpsweep.py` over the 51 marker states, work/qa/bpsweep.log):
  **0x088A69C8** = dungeon area label (EBOOT `%s　%s` 2b1ce4, area + floor; font 2 at x 5, y = obj+0x248), hit in
  every dungeon/battle state; drawn down the dark strip at the left originally, now one horizontal line at x 5
  (reads fine, white with outline, work/qa/warp/marker/dun1/final.png): budget up to the minimap, ~370 px.
  **0x0883CBCC** (a text object with a horizontal/vertical flag; horizontal branch 0x0883CB70) never fired: if
  some screen uses it, the patched drawer already lays it out left to right.
- **.ksf choice menu: done** (scenes `choice_pre` / `choice`; original look work/qa/warp/orig/choice/final.png:
  vertical columns 32 px apart from x 116 leftwards, a vertical red bar marks the selected one). `engine.patch`:
  rows (x 116, y 89 + 20*i; loop 0x089F0DF4); keys DOWN = next / UP = previous (0x089F2A10 / 0x089F2A2C, were
  LEFT 0x80 / RIGHT 0x20); cursor = the bar object turned flat (verified work/qa/choice_bar*: highlight follows
  DOWN/UP, circle picks). Bar object (made 0x089F09DC via 0x89fed28(obj, &pos, len = ctx+0x668/2, f12 63.0), only
  user): +8/+0xC x/y, +0x10/+0x14 target, +0x18/+0x1C start, +0x24/+0x28 w/h (state 2 at 0x089FE704: 20 x
  len*18), state 4 lerps x only; draw 0x089FE898 = fill rect (x-5, y-6, w+10, h+12) + a vertical bracket frame
  (sprites 0x15-0x17). English: w = len*18, h = 10, lerp y, target y = 92 + 20*sel (0x089F0A1C), frame skipped.
  Polish: bar width = len*18 tracks bytes, not px (a little wide for narrow text).
  Graphics: the emotion-input wheel (愛喜悲困友燃嫌怒, MS00_01) is graphics text: check it is in docs/re/graphics.md.
- Space width (sysfont18 9 px) looks wide; tune in the font patch if the width gate needs it.
