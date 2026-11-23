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

- Story flow: ending free movement (select, はい) runs `0x088ED5xx` = play MS<chapter>_<next> (chapter from the
  game state, see Saves); a warp leaves chapter 0, so field_end -> MS00_01 (prologue), `set=chapter=1` -> MS01_01.

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

## Saves (verified)
Saving from the field menu writes `PSP/SAVEDATA/ULJM05638_KARASUNOMORI_0000/{DATA.BIN,PARAM.SFO,ICON0,PIC1}`.
By default PPSSPP encrypts DATA.BIN (152,865 B). `tools/debug/noenc.ini` (`[SystemParam] EncryptSave = False`, passed
by `pspdbg.Session` as `--appendconfig`) makes it write plain saves (152,849 B) and load them; the SFO then has no
hash. Plain DATA.BIN = the game-state block: the load copies it whole to `*(0x09256ED8)` (0x08835830: checks only the
header u32 size 0x25510), so **save offset = game-state offset**, and there is **no checksum** (verified: money edited
to 98,765 and 500,000 shows in the menu). The folder name must be exactly `ULJM05638_KARASUNOMORI_0000` (psp.py
`--sav DIR` names it after DIR: pass the parent). Fields: money u32 @0xBD4, chapter s16 @0x3060 (0 = prologue; read by
0x088ED5DC to pick the next MSnn script; `chapter=3` loads a chapter-3 field with マップ/成績表 enabled), names SJIS
@0x442 (千馗) / 0x462 (七代), readings @0x482 / 0x4A2. `save.py make|edit|show|load`; warp.py `set=field=v`.

## Tasks (verified)
Static task objects, table at 0x0924711C (ptr per id); `SetNextTask(id)` = 0x08A38294 (writes id to 0x08ADD370 and 1
to byte 0x09247119); warp.py `task=ID` does the same. Ids: 0 Title, 3 GameMain, 7 Dungeon, 12 EndSave (クリアデータを
セーブしますか？), 13 Continue (after-clear はじめから / つづきから screen), 14 CheckMS, 15 Badend, 16 Trueend, 17
DbgMenu (blank screen, no menu drawn), 256 Startup. Badend/Trueend load MS<chapter>_04 / _03 (chapter 0 from a warp:
MS00_04 does not exist, black). Bad-end movie: BadEndLost/BadEndSeal by flags 0x263/0x264 (0x08960AC0), TrueEnd.pmf;
per-chapter movie tables at 0x08AD6A98 (opening) / 0x08AD6B08 (episode end). `tools/debug/rtti.py CLASS` finds a
class's vtable and constructor.

## Dungeons, endings
- A DG script, when it ends, enters the dungeon of the game-state chapter: chapter 0 = the tutorial 模擬演習場
  (DG00_00 lands in it; MSxx warps that fall through to the dungeon land there too), `set=chapter=1` after
  DG01_00 = the chapter-1 dungeon (scene `dg01`, `dun1_walk`). Battles are turn-based on the dungeon map, started
  by events/positions (help.bin); the tutorial battle has game over disabled (d100scr.bin). Not reached yet.
- Endings: MS11_04 (bad end) and MS13_03 (true end) play the ending movie with the staff roll (scenes `badend`,
  `trueend`).
- Probes: `bplog.py` (regs at code breakpoints), `watchw.py` (memory read/write breakpoints), `findval.py` (load a
  state, find a u32 such as a vtable in RAM, or dump a range), `find_cmd.py` (which script/block holds a command),
  `tools/csvb.py` (print CSVB table rows).
- **dg01 / dun1_walk are the tutorial dungeon, not chapter 1** (verified 2026-11-23: same room as dun_tut, item
  模擬演習用蝋燭, box 模擬演習用に作られた巨大な木箱). The dungeon a DG script ends in is not picked by the chapter
  field; the real way in is unknown (field △探索 + circle moved to a classroom instead). Leads: d01scr.bin's SSCR
  scripts, `dungeon/%s.ini` (a1_00.ini = section with start floor/pos), dungeonscenetable.bin (87 rows).
- Dungeon controls: grid crawler. up = step forward, left/right = turn 90°, down = turn round; △ jump, □ investigate,
  ○ palette action (取る take); R (`rtrigger`, not `r`) cycles 3 action palettes (empty in the tutorial until set from
  the dungeon menu). Dungeon menu (start): アイテム 装備 札強化 マップ 携帯電話 成績表 セーブ・ロード 地上へ. Minimap
  purple crosses = objects (statues). Tutorial so far (`_mv3` route from dun1_walk: left, up 1500, circle): take the
  candle on the pedestal before the sealed door 封; next step not found (box 調べる loops its description).
- Battles: the first chapter-1 enemy room plays DG01_11 (白: 隠人が湧いておるか, the season-aura lesson); DG01_01 is
  after that fight, DG01_02 after the boss. d01scr.bin labels `:battlestart`, `:battle`, bosses `ene_b_dogu`,
  `ene_b_aramitama` in `jyoumon_bossnoma`. enemyhaichi.bin (231 rows: chapter, room id, enemy ids, x/y bytes) places
  enemies per room. CLDungeonBtlMgr: vtable 0x08AC2D20, instance 0x09DEAE74 in the dungeon (dun1_walk state).

## Script blocks, shops (verified)
- Start block: the loader reads s16 ctx+0x3850 right after the file loads (0x089F2394, s0 = ctx) as the first block.
  warp.py `block=N` writes it there, so a warp can start mid-script.
- `shop00` (情報屋 QUEST SHOP, the only shop command) sits alone in FNxx_26/27 blocks: scene `shop` = FN08_27 block 3.
  `tradeNN` (15 item trades): scene `trade` = FN05_25 block 3; from a warp the item list is black and circle shows
  its このアイテムを渡しますか？ dialog. FD-type trade scripts (FD03_06) stay black.
- FN scripts run from block 0 are NPC talks with the emotion wheel (direction, then circle).
