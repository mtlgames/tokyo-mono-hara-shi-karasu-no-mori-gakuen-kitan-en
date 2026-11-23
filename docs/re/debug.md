# Debug tool: script loader, warp, field, saves

Addresses are RAM (EBOOT `main` module loaded at 0x08804000 in PPSSPP; RAM = 0x08804000 + ELF vaddr, ELF vaddr =
file offset - 0xC0 for the code/rodata segment). `work/exe/main_ram.bin` is the relocated module dumped from RAM at
the title screen (`tools/debug/pspdbg.py ISO --out D --route tools/routes/boot.txt dump 08804000 2da000 F`);
disassemble it with `disasm.py dis|xref work/exe/main_ram.bin ADDR --arch mips --base 08804000`.

## Script loader (verified)
- `0x089F22E4(a0, type, chapter, sub)`: polled state machine; context pointer at `*(0x0922A718)`, state byte at
  ctx+0. State 0 builds `PW/%s%02d_%02d.PWX`/`.KSF` (types 6, 9: `PW/%s.PWX`) into ctx+0x381C / ctx+0x3860, then
  starts the read. Prefix table at 0x08ADC490: 0 MS, 1 FD, 2 FN, 3 ID, 4 IN, 5 DG, 6 KWLNSCR, 7 FS, 8 QS, 9 QUEST.
  Block address = file + u16[ctx+0x3850 index]*4 (`0x089F22C0`).
- Caller: ADV task update `0x089EB498`, state 0 case at `0x089EB4D8`: params struct `s1 = task+0x38`:
  +0 state (u32), +4 chapter (s16), +6 sub (s16), +8 type (s8); copied to ctx+0x3918..0x391A, then the loader.
  New Game loads MS00_00 there at frame ~1720 of `tools/routes/boot.txt`.
- **Warp** (`tools/debug/warp.py`): breakpoint at 0x089EB4D8, rewrite +4/+6/+8 to the target script on the first
  hit. Tested: MS01_00 and MS02_00 run from block 0 with correct backgrounds and captions; the player name is
  the default 七代 千馗 (name entry skipped).
- Chapter structure (from the scripts): MSnn_00 holds `opmovie` + `scenetitle` (chapter opening and card),
  MSnn_03 holds `edmovie` + `interval` (episode ending + eyecatch). The ADV part of a chapter ends in free movement
  on the school map (field).
- The ADV can show system screens itself: MS01_00 shows the report card (成績表); circle does not close it, cross
  does. The emotion-input wheel needs a direction then circle.

## Tables (CSVB, row size in Info): scene flow (guess, not yet used)
`app_init.pak/table/mainscenetable.bin`: 26 rows x 12 bytes, keyed (chapter u8, part u8) = (0,0),(0,1),(1,0)...
(13,1) with increasing u16 ids (0x2F, 0x3C, 0x3E, ...); `scenetable.bin` 27 rows, `dungeonscenetable.bin` 87 rows.
Likely the story-progress step the save holds. Not needed yet; look here for a save editor field.

## Leftover debug menu (dead end so far)
RTTI `13CLDbgMenuTask` (typeinfo 0x08AC0D50, vtable 0x08AC0D80, static instance in .bss near 0x08ADDEB8;
methods 0x08841F4C-0x08842214 cycle an index mod 257). No debug strings found for it; not pursued.

## Field and menus (verified)
`field_ch01` in `tools/debug/scenes.txt`: warp MS01_00 + mash 50,000 frames reaches the school map by ~f30,000.
Main menu (start): アイテム, 装備, 札強化, マップ (grey), 携帯電話, ??? (grey), セーブ・ロード; cursor skips grey
entries and wraps (up from アイテム = セーブ・ロード). Wait ~90 frames after start before the first press.

## Saves
Saving from the field menu writes `PSP/SAVEDATA/ULJM05638_KARASUNOMORI_0000/{DATA.BIN,PARAM.SFO,ICON0,PIC1}`.
DATA.BIN (152,865 bytes) is encrypted (entropy 8.0, PARAM.SFO has SAVEDATA_PARAMS): the PSP savedata crypto.
Plan for `save.py`: don't implement the crypto; load a game-written save in game, poke the fields in RAM (find them
by diffing RAM before/after a known change), and re-save through the game's own Save menu, which encrypts.
