# Text: encoding, script files, tables, EBOOT strings

Encoding everywhere: **Shift-JIS (cp932)**, standard (verified: phase 4 roundtrip of every extracted string, see
`tests/test_extract.py`), except 7 UTF-8 save-dialog strings in the EBOOT. Fonts are the game's own bitmap fonts, not
sceFont: `app_init.pak/system/font/{advfont08,advfont14,sysfont18,mobilefont}.ipk` plus `jis2ucs.bin`/`ucs2jis.bin`
(guess: the .ipk glyphs are indexed by Unicode via jis2ucs; decode the .ipk format in phase 5).

## Repo text format (phase 4, `tools/extract.py`)
`script/` JSON (indent 1, UTF-8), one list of entries per file; `id` is stable and address-based, `jp` is the
decoded original, `en` is for the translation, optional `notes`/`status`. `extract.py` writes missing files only;
`--force` regenerates jp/context and keeps en/notes/status by id, printing ids whose jp changed.
- `script/pw/<dir>/<stem>.json`: scene spans `<stem>:<block>:<span>` with `speaker` (JP, see speakers.json) and
  `kind: caption` for `{...}` location captions; then the scene's choices `<stem>:ksf:<offset>` (`kind: choice`,
  `slot` 30 bytes).
- `script/speakers.json`: each 【speaker】 name once (`lines` = uses); the build writes 【en】 for every 【jp】.
- `script/tables/<stem>.json`: one entry per distinct pool offset, id `<stem>:<row>:<col offset hex>` of its first
  pointer, `refs` = pointers sharing it.
- `script/eboot.json`: id `eboot:<file offset hex>`, `slot` (bytes to the next non-zero byte), `refs`, `enc`.
Totals: 29,758 script spans in 438 .pwx, 1,225 choices, 221 speakers, 8,113 table strings in 40 tables, 1,255
EBOOT strings (40,572 entries with speakers). Text markup inside `jp`: `\n` line break, `{px}`/`{pm}`/`{pn}` player
full name / surname / given name (guess for pm/pn), `{ruby:base|reading}` furigana, `{x:HHHH}` a SJIS pair cp932
can't roundtrip (none occur).

## Story/event script: `pw/{dg,fd,fn,in,ms,qs}/*.pwx` (verified: roundtrip + coverage test)
438 files (47 zdv-compressed in CROW.PAK), 2.24 MB, 11,006 blocks. Each `.pwx` has a sibling `.ksf` (below).
- Layout: u16 offset table at 0, values in **4-byte units**; the first value is the table size (= first block's
  offset). Unused slots are 0 and come last; dg00_31 pads its table with 10 of them, so the rebuild keeps the original
  table size (`pwx.pack(blocks, head_size)`). A slot may point at the file end (an empty block: the "3 blocks without
  `_`" are these). Blocks are 4-aligned, end with `_`, zero-padded to 4 (0-3 zeros). Max addressable 256 KB per file.
- Text is double-byte SJIS only; control codes are **single-byte ASCII mnemonics with ASCII arguments**, e.g. `r`
  line break, `wc` wait for button + clear box, `_` end of block, `【name】` speaker line (literal SJIS brackets),
  `vo#####`/`vos#####` voice, `ch#####` portrait, `ef##x+000y+000w+000h+000s#` screen effect, `ci##`/`co##` fade,
  `mo##`, `mr##`, `mi#`, `mfin##`/`mfout##` music, `seplay,NAME,nn,n`, `sebl,NAME`, `sebf,NAME`, `bg####`, `bi##`,
  `w##` wait, `time##`, `shopwait#`, `iget`, `nameclear`, `eyecatch`, `{...}` location caption, `}NAME` (`}mail`),
  `dic,DI..`, `exi##exg####`. No byte in 0xA0-0xDF (half-width kana) occurs, so a lead-byte scan splits ASCII from
  SJIS exactly.
- **Text spans** (`pwx.spans`): a run of SJIS chars plus the inline codes between them: `r` (only when more text
  follows), `px`/`pm`/`pn`, ruby `l<base>(<reading>)` (also inside 【】 speaker names). Anything else ends the span.
  A span that is `【name】` + `r` + text gives `speaker` + `jp`; `【name】` alone (6 cases, a voice or effect code follows) is speaker only.
- **Consequence for English:** ASCII letters are commands, so English text cannot be plain ASCII in this format.
  Phase 5 spike: full-width Latin (SJIS 0x8260..) through a VWF, or an engine hook adding a half-width text mode.

## Choices: `pw/*/*.ksf` (verified: decoded, 1,225 hits fit one record shape)
The .ksf is the scene's event/flag data (rest of the format unknown). Each choice option = byte `0x01` + a 30-byte
slot holding a NUL-terminated SJIS string, zero-padded; the next record follows the slot. Every SJIS-looking run in
.ksf outside these is binary noise (single chars, 0x80 runs). English options must fit 29 bytes unless phase 5 finds
the reader (`ksf.py`).

## Tables: CSVB (`app_init.pak/table/*.bin`, `table/*.bin`, `dungeon/*/table/dNNscr.bin`) (verified: roundtrip)
Chunked: `CSVB` u32 size, then chunks tag + u32 size (incl. header): `Info` (u16 row size, u16 rows, u16 0, u16 ?),
`OfsB` (u16 row offsets of the **string-pointer fields**, 0xFFFF-terminated), `KITB` (index), `TblB` (rows, then a
pool of NUL-terminated strings; a pointer field is a u32 offset from the TblB start, 0 = none), `Term`. Table strings
are plain C strings: ASCII allowed, `\n` = 0x0A, printf formats (`%s`, `%3d`) occur. Rows share pool strings
(dedupe) and one enemydb pointer lands inside another string. **Insertion:** append new strings at the TblB end and
repoint (pointers are u32, no width limit); never rebuild the pool in place: obj, skill, effset, motsyncscreff and
dNNscr keep non-string data in it.
A pointer column can point at binary blobs (`SSCR` scripts, layout data): `tables.text()` takes a string when it
decodes exactly, has no control byte but `\n`, and its column holds double-byte text. Not extracted (waived with
counts in `tests/test_extract.py`): SSCR node labels inside enemyai (1,391), skill (247) and the 22 dNNscr
dungeon-trigger tables (e.g. 誘導用検知セット, 通常攻撃　セット; dev names, guess: never drawn, the marker build will show
any that are), binary noise in enemy/questvoice/dungeonuimoya, an orphan copy of 猪牙の印章 in obj.

## EBOOT (decrypted ELF, `work/exe/NPJH50215_EBOOT.BIN`; `eboot_text.py`)
Relocatable module: vaddr = file offset - 0xC0 (both segments); sections present (.text, .rodata, .data...).
1,255 strings in rodata/data: menus, save/load prompts, item messages, place names, character names and readings,
nickname formats (`pnセンパイ`, `pnyhっちゃん`: the pwx name codes as ASCII; `yh` guess: first kana of the reading),
name-entry character sets (kana, Greek, Cyrillic, symbols), printf formats, 7 UTF-8 save-dialog strings. Rule
(`is_text`): kana / full-width / 2+ double-byte chars, or one referenced double-byte char at or after the string pool
(0x2B0600; before it .rodata pointer tables decode as one-char noise). `refs` = u32 data pointers + lui/addiu pairs;
53 strings have refs 0 (struct arrays: the nickname table at 0x2D3A10 has 0x24-byte rows, options table 0x2D2388
0x18-byte rows). Also two dev messages (`scePsmfPlayerCreate : 作成失敗`, `Font Area Over!!`): not shown.
Patch in place inside each slot or relocate (phase 5); re-sign the ELF before shipping (`platform-psp.md`).
Non-text (verified: marker build, name entry grid showed markers; `insert.NON_TEXT`, never replaced): the 240
name-entry cells 0x2B1154-0x2B1514 (one char per 4-byte slot; the 英数 page already holds full-width A-Z a-z, which
the font patch draws as English) and the full-width ASCII table at 0x2B7F04. In-place room: `insert.eboot_room` (the
original bytes + NUL, up to the next 4-byte boundary).

## Other data with SJIS (checked phase 4: no player-visible text)
- `system/key_icon.pak/system/sfk/namedic.bin` (2.8 MB): name-entry kana-kanji dictionary (guess); phase 5 decides
  the English name entry.
- `dungeon/*.pak/dungeon/block/*.bin`, `.g3a`, `.znt`, `.z3n`, `.gim`, `.at3`, `system/sysfile*.bin`: no kana run of
  3+ chars that decodes as text (binary noise).
- `effect/*.bpc`, `effect/gpeffect.ini`, `dungeon/*.ini`, `system/site/site_ch0031_00.lay`: developer names and
  comments, not shown.

## Free space
File-based: CROW.PAK is rebuilt, so scripts and tables can grow (zdv recompressed). EBOOT: none found yet; strings
are slot-bound until a relocation area is found (phase 5).
