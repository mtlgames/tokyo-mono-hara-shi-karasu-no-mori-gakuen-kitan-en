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
- **dg01 / dun1_walk are the tutorial dungeon, not chapter 1** (same room as dun_tut, item 模擬演習用蝋燭).
- **Which dungeon (verified)**: the Dungeon task (static object 0x08ADDE74) init at 0x08841DFC looks up
  `app_init.pak/table/dungeonareainfo.bin` row `*(game state +0x6878)` (lookup 0x088134F8 on table set
  `*(0x092B6F1C)+0x60C`; row = name, section, scr, ?, id; string offsets + 0xD0) and copies the section name
  (`bg01_00`) to task+0x20; 0x08859F6C / 0x088619E0 / 0x0886C054 then load `dungeon/<section>.ini`. Rows: 0 bg00_00
  模擬演習場 (tutorial), 1 bg01_00 秋・第一階層, ... 18 a1_00 Ａ１エリア (dev test area); names in the table. save.py
  field `dun_area`; scene `dun1` (DG01_00 + set=chapter=1,dun_area=1) plays the chapter-1 dungeon arrival events and
  ends in free control in **the hub bg100_00 Entrance_Autumn** (秋の洞エントランス; verified from the dungeon object's
  section/floor strings at 0x09DF1118 / 0x09DF1158 = dungeon object 0x09CE0870 + 0x1108A8 / +0x1108E8). The hub has
  one open door (doorlink 1 -> bg01_00 jyoumon_tuuro); its purple chained door says it leads to the third level and is
  locked. The byte at game state +0x25838 (past the save) switches
  0x08859F6C to "resume": section from +0x6878, start position from row +0x687C of table +0x624; setting it to 1 in a
  warp sent the story to the city map instead (not used).
- bg01_00 layout (`bg01_00.ini` doorlinks): 通路 jyoumon_tuuro (door 1 = back to the hub, door 2 = 狩猟の間) -> 狩猟の間 ->
  遊動の間 / 貝塚の間 -> 集落の間 -> 祭壇の間 -> 遺跡の間 -> boss. enemyhaichi.bin: string offsets are TblB-relative;
  chapter-1 rows name syuryounoma (flags 0 / 0x288F), kaidukanoma (0 / 0x28B7; 0x28B8 / 0x2893), saidannoma,
  jyoumon_bossnoma: likely (needed flag, cleared flag). All those flags are 0 in the hub state.
- **Solved since (battle scene, see "Battle, game over")**. Old note: a mash walk from the hub (circle,up,up,up,circle,right) went through two doors, then a third
  transition hung for good on a black screen with the red loading diamond (main loop alive, no file open, no script
  load; PPSSPP log only shows a stale sema id 294 = mutex warning that is there from the start). Not yet known which
  door that was. Next: from `dun1`, walk deliberately (find the hub door, check the floor string after each door), reach
  狩猟の間 and see whether enemies spawn; if the hang is the hub -> bg01_00 load, use scene `dun1_direct` (DG00_00 +
  dun_area=1: the tutorial script, then the dungeon task loads bg01_00 directly; verified: section `bg01_00`, floor
  `jyoumon_tuuro`; game-state chapter stays 0, so enemyhaichi's chapter-1 rows may need set=chapter=1 too).
- Story flags (verified): bit array at game state +0x3080, flag n = bit (n & 31) of u32 (n >> 5); test function
  0x089D30FC. A save.py/warp `set=` for flags is not written yet.
- `tools/debug/fileopen.py`: logs sceIoOpen/sceIoOpenAsync paths (PAK members do not show; CROW.PAK is opened once).
- Dungeon controls: grid crawler. up = step forward, left/right = turn 90°, down = turn round; △ jump, □ investigate,
  ○ palette action (取る take); R (`rtrigger`, not `r`) cycles 3 action palettes (empty in the tutorial until set from
  the dungeon menu). Dungeon menu (start): アイテム 装備 札強化 マップ 携帯電話 成績表 セーブ・ロード 地上へ. Minimap
  purple crosses = objects (statues). Tutorial so far (`_mv3` route from dun1_walk: left, up 1500, circle): take the
  candle on the pedestal before the sealed door 封; next step not found (box 調べる loops its description).
- Battles: the first chapter-1 enemy room plays DG01_11 (白: 隠人が湧いておるか, the season-aura lesson); DG01_01 is
  after that fight, DG01_02 after the boss. d01scr.bin labels `:battlestart`, `:battle`, bosses `ene_b_dogu`,
  `ene_b_aramitama` in `jyoumon_bossnoma`. enemyhaichi.bin (231 rows: chapter, room id, enemy ids, x/y bytes) places
  enemies per room. CLDungeonBtlMgr: vtable 0x08AC2D20, instance 0x09DEAE74 in the dungeon (dun1_walk state).

## Battle, game over (verified)
- Scene `battle`: from `dun1_direct` (bg01_00 jyoumon_tuuro) hold up ~450 frames to door 2 (扉を開く), circle, wait
  900 (floor string -> `syuryounoma` 狩猟の間), hold up 200: four 隠人 engage (battle HUD, ターン終了 on select). Works
  with game-state chapter 0, so the "hang after a third door" was the hub path, not the battle.
- Player HP = game state +0xBDC (s32; save.py field `hp`; the battle HUD shows a poke at once, max is derived).
  `gameover` = battle + hp=1, select (ターン終了 confirm), はい: the enemy turn kills; ゲームオーバー banner ~f700-900,
  then the game resets to the ATLUS logo and title (~f1400).
- `tools/debug/step.py ISO STATE OUT "route" [--mash ..] [--every N]`: one leg of play from a state, prints the
  dungeon section/floor strings, saves the new state (dungeon walking, menu probing).

## Myroom, city map (verified)
- Field object update `0x088E62F0` (a0 = field object): state s32 +0x18 (jump table 0x08AAE060, 17 states), row
  +0x24 into the location table `*(0x08ADE8F0)` (40-byte rows: name ptr, s16 +4, ..., sub-table +0x1C, parent +0x20).
  School table 0x08ACB3A0 (屋上 4F 3F 2F 1F 校門; 校門 is grey in chapter-1 free movement), city table 0x08ACB1E8 (0
  鴉乃杜學園 1 焼却炉 2 鴉羽神社 3 自室 4 カレー屋 5 中央公園 6 八汎學院 7 茶室 8 新宿署 9 都庁). State 9 = arrive at a
  location: sets game state +0x25850/+0x3064/+0x3068 from the row, creates the myroom manager (global 0x092B6FD0,
  `AppMyRoomMgr`, init 0x0896594C) and goes to state 0x10. warp.py `room=N` writes table = city, row = N, state = 9
  on the next field update: scene `myroom` (room=3). Myroom hotspots in chapter 1 and 13 alike: 机 (desk: record
  shelf, ○ 再生 = `myroom_desk`) and 出口; cross leaves to the city map 新宿区周辺 with every destination listed
  (`city_map`), so this also reaches the city free movement.
- **Album (not reached)**: `AppMyRoomReadInit` (vtable 0x08AC5AB0, 0x08962DB4) loads `_ui_myroom.pak` ui_myroom.g2d +
  ui_album.g2d on myroom entry; `AppMyRoomReadAlbum` (0x089616D4, object at mgr data +0x8C) loads
  `system/album_thum%02d.pak`; table `imagealbum.bin` (164 rows). The desk view shows only the record shelf with an
  empty left panel; story flags (+0x3080, 0x400 bytes all set) unlock nothing there. Unlock storage still unknown:
  next, break on 0x089616D4 / reads of the ImageAlbum table, or diff a save after a CG is seen.
- `exbg0136` (感情入力について tutorial panel): no script or data file names it (scripts use `exgNNNN`, which only go to
  0139 and skip 0136); the EBOOT lists it only in the ADV bg name array (0x08ADC800, {0x110, 0x1E0, name} entries,
  read by 0x089FC7B0). Likely unused; translate for completeness, verify only if textcover finds a use.

## Script blocks, shops (verified)
- Start block: the loader reads s16 ctx+0x3850 right after the file loads (0x089F2394, s0 = ctx) as the first block.
  warp.py `block=N` writes it there, so a warp can start mid-script.
- `shop00` (情報屋 QUEST SHOP, the only shop command) sits alone in FNxx_26/27 blocks: scene `shop` = FN08_27 block 3.
  `tradeNN` (15 item trades): scene `trade` = FN05_25 block 3; from a warp the item list is black and circle shows
  its このアイテムを渡しますか？ dialog. FD-type trade scripts (FD03_06) stay black.
- FN scripts run from block 0 are NPC talks with the emotion wheel (direction, then circle).
