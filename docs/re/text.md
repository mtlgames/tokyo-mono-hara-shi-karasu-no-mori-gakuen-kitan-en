# Text: encoding, script files, tables, EBOOT strings

Encoding everywhere found so far: **Shift-JIS (cp932)**, standard (verified: every `.pwx` block and the CSVB tables
decode as readable Japanese with Python's cp932). Fonts are the game's own bitmap fonts, not sceFont:
`app_init.pak/system/font/{advfont08,advfont14,sysfont18,mobilefont}.ipk` plus `jis2ucs.bin`/`ucs2jis.bin`
(guess: the .ipk glyphs are indexed by Unicode via jis2ucs; decode the .ipk format in phase 5).

## Story/event script: `pw/{dg,fd,fn,in,ms,qs}/*.pwx` (verified by decoding)
438 files (47 zdv-compressed in CROW.PAK), 2.24 MB, 11,006 blocks, ~663,000 SJIS characters. Each `.pwx` has a
sibling `.ksf` (event/flag data; holds a few SJIS labels, guess: debug names, not shown).
- Layout: u16 offset table at 0, values in **4-byte units**; the first value is the table size (so it is also the
  first block's offset); the table ends with 0 padding to a 4-byte boundary. Each block starts on a 4-byte boundary,
  ends with `_`, zero-padded. 3 of 11,006 blocks don't end in `_` (check in phase 4). Max addressable: 256 KB per
  file (largest original 116 KB). Block index = what `.ksf`/code refers to (guess); offsets are recomputed on insert,
  so block sizes may change freely.
- Text is double-byte SJIS only; all control codes are **single-byte ASCII mnemonics with fixed-width ASCII
  arguments**, e.g.: `r` line break, `wc` wait for button + clear box, `_` end of block, `【name】` speaker
  line (literal SJIS brackets), `vo#####`/`vos#####` voice, `ch#####` portrait, `ef##x+000y+000w+000h+000s#..`
  screen effect, `ci##`/`co##` fade in/out, `mo##`, `mr##`, `mi#`, `mfin##`/`mfout##` music, `seplay,NAME,nn,n`,
  `sebl,NAME`, `sebf,NAME`, `bg####`, `bi##`, `w##` wait, `time##`, `shopwait#`, `iget`, `nameclear`,
  `eyecatch`, `{...}` location caption, `}NAME` (e.g. `}mail`), `l漢字(かな)` ruby, `px` full player name,
  `pm`/`pn` player surname / given name (guess), `exi##exg####`.
  **Consequence for English:** ASCII letters are commands, so English text cannot be plain ASCII in this format.
  Phase 5 spike: full-width Latin (SJIS 0x8260..) through a VWF, or an engine hook adding a half-width text mode.
- Names inside text are literal (`【伊佐地】`), so speaker names are translated in place.

## Tables: `app_init.pak/table/*.bin` (82 files) and `table/*.bin` (3): CSVB
Chunked: `CSVB` u32 size, then chunks tag+u32 size: `Info` (guess: u16 ncols, u16 nrows, ...), `OfsB` (column
offsets), `KITB` (column types), `TblB` (fixed-size rows, strings inline in fixed slots), `Term`.
Text-bearing (SJIS hits): buddymes 3939, dictionary 2015, item 1698, enemyai 1391, obj 952, questsent 663,
mail 596, systemtext 594, enemydb 544, help 473, enemy 425, hanafuda 316, skill 247, dungeonfloorinfo 229,
dungeonsysmes 219, questshoptext 229, exitem 200, questwordenemy 113, playerquestsent 113, dialogmessage 107,
questwordkill 91, questwordpkill 84, questwordcomment 71, clctbgm 58, tokkidata 52, questwordplace 45,
questplayerview 39, dungeondoorexplain 32, questwordhint 28, dungeonareainfo 22, clctinterior 16, keymessage 13,
siteinfo 11, questrewarditem 11, questclnt 10, clctmelody 10, questvoice 6, delivery 3; table/proftext,
inputproftext (139 hits). Slot widths limit English length: phase 4 must find each column's width; relocation to
a string pool would need code work (guess).

## Other data with SJIS
- `dungeon/*.pak/dungeon/block/*.bin` (77 with hits, 4,498 runs): guess mostly binary noise; check in phase 4.
- `system/key_icon.pak/system/sfk/namedic.bin` (2.8 MB): name-entry dictionary (guess).
- `system/site/site_ch0031_00.lay`: one dev string (作業用フォルダ), not shown.
- `dungeon/*.ini`: developer comments, not shown. `system/sysfile*.bin`: save icons (PNG), noise.

## EBOOT (decrypted ELF, `work/exe/NPJH50215_EBOOT.BIN`)
265 SJIS strings with kana, in 0x2b06b4-0x2b7ba0 and 0x2d3c18-0x2d3cc4 (file offsets): menus, save/load prompts,
item messages, character names and readings (武藤 いちる / むとう いちる ...). 5 UTF-8 strings (save dialog:
title "東京鬼祓師 鴉乃杜學園奇譚 ダウンロードクエスト", セーブが完了しました。 etc.). Patch in place inside each NUL
slot; re-sign the ELF before shipping (`platform-psp.md`).

## Free space
File-based: CROW.PAK is rebuilt, so scripts and tables can grow (zdv recompressed). EBOOT: none found yet; strings
are slot-bound until a relocation area is found (phase 5).
