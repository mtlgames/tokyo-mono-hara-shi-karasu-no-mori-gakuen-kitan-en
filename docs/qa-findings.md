# Phase-8 visual-QA findings (tour of build 30bc8c09)

Verdict files: `work/qa/verdicts/chunk_c28c67163a69_NNN.tsv` (gitignored; zoom crops `work/qa/vqa_scratch/NNN/`).
One line per distinct problem; sheets named are examples. Tick when fixed and re-checked in game.

## Engine / layout
- [x] **ADV re-wrap:** dialogue sometimes ignores the stored `\n` and wraps greedily to x ~470, switching layout
  between consecutive frames (field_ch01 sheets 2/10/11/12/15/18/20). field_ch01_sheet_20 f011410: "Starting
  today, this is your new transfer student, Kazu|ki" runs off screen. **Not in the current build:** the same mash
  on e69f6e83 (work/qa/warp/cur/field_ch01, frame for frame the same timing) shows the stored wrap everywhere; the
  toured ISO 30bc8c09 carried older text. The re-tour covers the rest.
- [x] **HUD player name** (dungeon + battle, every HUD frame): the name, drawn down the side plate in the original,
  is now one horizontal line "Shichidai Kazuki" over the AP gauge (the global horizontal drawer). Also surname-first.
  Fixed (worker 5): `engine.hud_name` swaps the sprintf args (given first, both "%s %s" sites) and moves it 48 px
  down onto the strip's top, clear of the gauges (cold boot work/qa/warp/w5/battle, battle_dun1_direct).
- [x] **Choice bar** too narrow for proportional text ("Don't shake hands"): engine.choice_bar_px sizes it from the
  options' px width; inkbox 8/7 (work/qa/warp/bar/choice, cold boot).
- [x] **Wrong speaker plate:** ms01_00:011:35 (Hisae, 久榮) shows under ❖Gentle Schoolgirl❖ (field_ch01_sheet_22
  f012310-f012370); JP shows ❖久榮❖. Cause: 17-char names overflow the speaker-id lookup's 29-byte stack buffer
  into saved $s0 (engine.md §Name codes); fixed in engine.patch, cold boot work/qa/warp/spk f012332 shows ❖Hisae❖.
- [x] **Crash at ms01_00:022:08** (worker 4, build 6acc09db; field_ch01 warp died at f016626): speaker lookup
  buffer zeroed only to sp+0x1d -> 15-17 char names got id -1 -> `{px}--` crashed. Zeroed to sp+0x24
  (engine.md §Speaker-id lookups); field_ch01 runs to f52222 exit 0.
- [x] **School map list** (field_ch01 sheets 29-42): "Audiovisual R", "Student Coun", floor "School Ga" clipped
  at the screen edge. List at x ~383, ~92 px to the edge (advfont14); 23 room names and most relationship labels
  (EBOOT 2b1f58..2b21dc) are wider (Student Council Room 158 px). `engine.right_align(0x088E4168, 472, keep)`:
  x = min(x, 472 - width), long names shift left over the map (scene `field_rooms`).
- [x] **Main menu** (menu_sheet f000096): labels no longer right-aligned at x ~431; "Equipment", "Card Enhanc…" run
  over the red frame and off screen. Fixed: `engine.menu_right` (x = 432 - advfont14 width at the draw call
  0x08923BFC), work/qa/warp/w4/menu2. Still open: "1,000 yen" n past the money plate's arrow tip.
- [x] **Name entry** (name_entry_sheet_2): mode tabs "Hiragana"/"Katakana"/"ABC/123" spill onto the grid; right
  buttons show only "Cross:"/"Circle:" (action words cut); "Triangle: Input Mode", "Square: Convert" past their
  plates. Fixed (worker 6): tabs Hira/Kata/ABC/!?#, buttons ×Del/○OK, △Input Mode, □Convert (the fonts' own ×○△□
  SJIS marks, now allowed in table/EBOOT English: insert.BUTTONS), work/qa/warp/w6/name_entry.
- [x] Name entry graphics: header 日常と意識に関するアンケート, labels ふりがな/氏名 still Japanese. Worker 8: the whole
  questionnaire sheet (name entry + Q1-Q3 + footer) is a texture of the 3D model `system/name_input.znt`, which the
  GIM survey never opened; `tools/gfx_survey.py` redraws it (answers start at the JP x, so the pencil circle lands on
  them), gfx.py/gimsheet.py handle `file.znt@0xOFF` GIMs. Cold boot work/qa/warp/w8/survey (f000506 zoom).
- [x] Phone profile "Can't Change" past the phone screen edge (phone_prof_sheet f000236). systemtext:0600 -> "Locked".
- [x] Caption dash "--" shows as two short hyphens with a gap (script "--" now encodes as ― 815C, one solid dash:
  work/qa/warp/dash f005290; the x 1 margin and " -- " vs "--" spacing are still open) ("Some years ago -- Public Library"); long caption
  starts at x 1 with no margin (field_ch01_sheet_7 f005290). Captions use "--" and " -- " inconsistently.
- [x] Help bar overlap also on the school map and myroom_desk; map f000390 "✕ Back○ Confir" (no gap, cut at
  x 480); shop "○ Confirm" cut at x 480. Worker 6: 決定 -> "OK" (eboot:2b4610 map bar, systemtext:0003); map shows
  "× Back○ OK", myroom_desk and shop fit (work/qa/warp/w6). "Back" still touches the ○ sprite on the map bar.
- [x] Main/pause menu labels keep the JP start x: "Equipment", "Report Card" cross the red rule ~x 440,
  "Card Enhanc" cut (menu, menu_cards/equip/item, saveload, report). Right-aligned (same draw loop, menu_right).
- [x] Quest-shop menu "Check Quests" right-aligned to x ~95, starts below x 0, C cut (shop_sheet f002530). The game
  right-aligns by width itself; -> "My Quests" (+ its help heading), work/qa/warp/w6/shop.
- [x] systemtext:0041:00 has no `\n`: "You don't currently own this" runs onto the frame, "card." lost
  (menu_cards f000344; JP 2 lines).
- [x] 103 table strings whose JP has a line break and whose English has none (buddymes 48, systemtext 16,
  questshoptext 14, help 10, item 10, dialogmessage 5): check each box's width; systemtext:0041:00 fixed.
  Worker 6: help:08 (dungeon Q&A body) done (batches.TABLE_WRAP). Wrapping every multi-line JP entry at its own
  longest JP line would change 2,474 entries (most boxes are wider than the JP lines): not a rule; needs the box
  width per column in game (dialog boxes systemtext:00 / questshoptext:00 / dialogmessage:04 first, then
  buddymes:08 bubbles, item:0c descriptions). Add a TABLE_WRAP-like per-column px limit once measured.
  Worker 7: `batches.shape` keeps the JP line count (balanced) when one-line English is longer than the JP's own
  longest line: 85 entries re-wrapped, so no line is wider than a line the box already held (9 short ones stay).
- [x] Item stats "AP Cost12": label over value (menu_item f000252). The label is EBOOT 2b5148 "Attack ... AP Cost" (values at fixed x): 2 spaces fewer (verify).
- [x] Equipped marker still kanji 装 ("Shinai 1装"): lone EBOOT char the extractor missed (eboot_text.LONE, with
  円 0x2b5210) -> "E" (work/qa/warp/w6/menu_item). Help bar "Switch Type" under the SELECT icon -> "Category".
- [x] First category tab icon 全 in the item menu: system/category_icon.gim -> "All" (gfx_menus, work/qa/warp/w7/menu_item).
- [x] Phone settings (phone_set f000420): text speed 瞬 (EBOOT 0x2d2538, char[24] array, extractor LONE) ->
  "Instant"; "Short"/"Slow" past the screen: `engine.phone_settings` (start, gap) per row (work/qa/warp/w6/phone_set).
- [x] Phone settings: ringtone "01: Electronic T…" ellipsised (tables/clctmelody); graphics: "Voice Volum" clipped
  (gfx_phone.py label cell 66 px). Worker 7: "01: Beep Tone" (the game cuts at 16 chars, as in JP for the long
  titles); labels drawn inside their k_phon_set.g2d cells (Voice Volume cell is x 0-63), work/qa/warp/w7/phone_set.
- [x] "--" in dialogue too (fixed with the caption dash) ("Even so--", trueend_sheet_14; prologue2): the dash glyph draws two short hyphens.
- [x] "□ Show Help" runs to x 480, last p clipped (field_ch01_sheet_27 f014860). systemtext:0659 -> "Help" (worker 8:
  5 chars shorter than the clipped label, so it ends ~40 px inside the screen; field bar re-shot w8b/field_ch01).
- [x] (worker 13: moved to docs/polish.md) Readability: location caption and dialogue (no outline) over bright windows (field_ch01_sheet_28 f016210,
  sheet_29 f017470, sheet_3 f003250). The ADV gradient covers only x 0-150 (engine.md §Open): widen/darken it.
- [~] **Status page / report card** (field_ch01_sheet_11/12 f007210-f007420): name letters stacked, stat names over
  the arrows, summary text clipped at screen edge, "Social Studies" over its grade cell, "Best Subject" over
  "Japanese", "Homeroom" over the teacher name, "Before Last" into the value column.
  Worker 5 (cold boot work/qa/warp/w5/report): `engine.status_name` = one "Kazuki Shichidai" from x 80, furigana and
  "Name" off screen; `engine.status_labels` centres headers + stat/subject names in their grid cells (label x are
  code immediates, list work/qa/status_labels.txt); "Condition" 4 px left; summaries shortened to fit 116 px
  (systemtext 0400-0410, polish.md); header "Subject". **Still open:** names wider than the 56 px cell run over the
  value's ▲ (Willpower 68, Judgment 67, Japanese 64, Languages 74, Social Studies 98 px advfont14): needs the grid
  (background image, not status01.gim) widened + value column moved, or short forms; "Best Subject"+"Japanese"
  touch (value x 406 in 0x0892D0CC/0x0892DCC0); "Arcane Eye Max" crosses its divider; Homeroom/Now/Last
  (bonus page, labels 44-49) not looked at; second name block 0x0892DBD8 (partners?) unchanged.
  Worker 8 (cold boot work/qa/warp/w8b/report, zoom.png): `engine.STATUS_VALUES` moves the value columns (stats
  82 -> 89, subjects 325 -> 336; ▲ follows at -14), `STATUS_DOWN` ▼ at +16 (was +20; a zero prints " 0"), eboot:2b4178
  ▼ again (was "v"; insert.BUTTONS takes ▲▼); top-right labels centred left of the value divider (Arcane Eye Max no
  longer crosses); summaries "Crit Dmg Up", "Partner Skills"; 得意科目 "Forte" with its value at x 372 (room for
  any subject); systemtext:0070 "Social St." (glossary). Left: "Judgment" (67 px) crosses its 56 px cell's divider
  art, "Willpower" ends at its ▲; bonus page (Homeroom/Now/Last) and partner pages not looked at.
- [x] **Tutorial Q&A panel** (dun_tut_qa_sheet): body text breaks per character ("mov|e") and runs past the panel;
  OXAS ticker "The Card Sealer exam has begun." runs onto the frame; opening quote shows as "˝", no closing quote.
  Worker 6: the panel wraps every 38 bytes: help:08 stored at 35 chars a line (batches.TABLE_WRAP, 41 entries
  re-wrapped, work/qa/warp/w6/dun_tut_qa); ticker = a 32-byte scrolling window, `engine.ticker` 24 bytes, items
  without quotes, joined by 3 spaces (scene `dun_oxas`).
- [x] **City map** (city_map_sheet f000306): place list clipped at the panel edge ("Karasu no Mo…"). Already fixed
  by the field_rooms right_align (same draw call 0x088E4168): work/qa/warp/w6/city_map.
- [x] **Help bar** (city_map, fend_c1): labels run under the next icon ("End Free Mo△Explo…"). Carried item.
  city_map bar fits now (worker 4 labels; work/qa/warp/w6/city_map); fend_c1 not re-shot.
  Field bar: labels drawn by 0x088E4274 at fixed (x, y) from the EBOOT table 0x08AD5B14 (328/274/206/152/42, y 255),
  icons are sprites placed elsewhere (not in that table; a .g2d layout?). Slots in advfont14: SELECT 96 px, △ 38,
  □ 52, ✕ 38. Field labels shortened to fit (systemtext 0005-0007: Bonds / Look / End Roaming, worker 4). Other
  bars (menu, map, shop, myroom, city map) still overlap: moving icons needs their sprite layout.
- [~] **"~" glyph** (sysfont18): tiny raised dash with a gap ("fight~!", dg01 f005950, dun1_sheet_3). Script ～ now
  keeps the font's own full-width wave (fontpatch.KEEP; 13 lines re-wrapped for its width); not yet seen in game
  (dg01). Table/EBOOT strings still use the ASCII tilde.

## Graphics
- [x] Emotion wheel labels too wide for their diamonds ("SorrowWorry", "FriendPassion", Passion cut) - gfx_adv_ui.
  Worker 7: middle row 24 px apart -> 悲 "Sad", 燃 "Fire" (the quest_site wheel's words), each pushed away from its
  neighbour; no two touch (work/qa/warp/w7/choice_pre f007330).
- [x] "Arcane Eye" party plate clips the last e: drawn inside the g2d cell x 74-121 (xscale 0.84), w7/gameover.
- [x] "START Open Phone": last e crosses the red frame -> eboot:2b0e20 "Phone" (w7/dun_tut).
- [ ] Dungeon HUD: for one frame after a step '切替' and '秘法眼' show (second texture copy not redrawn; dg01_sheet_5).
  Worker 7: no other copy exists (`tools/gimfind.py` exact and 88% matches over all 1,934 GIMs, raw-byte search
  of every CROW.PAK file): the flash frames are fade-ins (grey HUD); re-check in the re-tour.
- [x] Game Over banner ゲームオーバー: the banner sprite (dungeon.g2d +0x8B10, 4 quads) reused the ー cell twice;
  `gfx.LAYOUT` repoints quads 2 and 4 to free cells of dungeon08 and one "GAME OVER" line is sliced over the 7
  diamonds (cold boot work/qa/warp/w7/gameover5 f001134-f001314, intro and outro animation too).
- [ ] Report-card heading 成績表 in one frame (field_ch01_sheet_12 f007270): a copy not redrawn. Worker 7: no other
  copy of the report_card01 cell in any GIM (gimfind 90%); the frame shows it larger (an opening scale animation?):
  re-check in the re-tour.
- [ ] **Dungeon textures inside .znt models** (survey `work/survey/znt/znt_NN.png` + znt.tsv, cell numbers below;
  `python -X utf8 tools/gimsheet.py work/unpacked work/survey/znt --embedded --tag znt --max 160`). Puzzle/sign
  kanji the obj table names in English: 913 jugon_hanahuda01 壱貮参肆伍 (Seated Petitioner 1-5) -> 1-5; 499/501-503
  bg0011_obj003-006 一二三四 walls and 1076 bg0011_004 tiles -> 1-4; 1071 bg0004_005 智義信礼仁徳 (Wisdom/Justice/Faith/
  Propriety/Benevolence/Virtue pillars + holes, obj 0306-0319); 969 bg0007_019 上 木 ? 佐 (Joshu/Kiso/Saku horse
  pillars, obj 0492-0494); 986 bg0004_003 + 1074 bg0004_002 是/非; 912 jugon_boss 敵/将 markers; 1032 bg0007_015 鬼;
  362/365-367 bg0005_obj015-018 南家北家式家京家 (statues; obj text already romanises them: may stay); 170
  bg0008_obj014 点火 (small red sign). Calligraphy scrolls (336 351 371 407 408 411), 106 glyph strip, 576 ancient
  glyphs, 771 福: art (K). Do with gfx (rows `path.znt@0xOFF`), short English in each tile.
  Worker 8-9 (`tools/gfx_dungeon_tiles.py`): numerals 1-4/1-5 (walls, floor tiles, slips), 敵/将 markers -> Foe/Boss,
  鬼 plate -> Oni (stone texture tiled over the glyph). Kept K (D22): virtue pillars, horse pillars, 是/非, house
  plaques (obj text names them), 12x16 px 点火 sign. Not yet seen in game (needs warps into bg11/jugon/seihen rooms).
- [ ] Staff roll / credits (badend sheets 2-7) and chapter cards (STORYTITLE01 第壱話 稲妻の転校生, field_ch01_sheet_6):
  burned into the PMF movies (Waiting on the user: movies).
  Worker 9: `tools/pmf.py` swaps a re-encoded H.264 stream into a PMF keeping the container byte for byte (each
  frame padded to its original size; self-test: same frames -> same file). `tools/movie.py` (WIP, not in build.py):
  STORYTITLE01-10 = 272 frames, video only, same backdrop animation frame for frame in all ten; text frames ~30-125,
  static columns (no pan), glyphs rise from white mist. Erasing is the open problem: a single plate frame is hazy
  (fade-in through mist), a per-pixel "most red" plate is noisy, a cross-card plate fails because every card puts
  第N話 and the title columns in the same spots. Next idea: plate from the cross-card mean where some card is clean,
  else the frame ~125 after the text has faded (or frames 0-30 tower-side texture), or a dark styled panel behind
  the English. English lines (CARDS) and their per-column reveal timing already work (work/movie/01/en).
  Worker 10: **chapter cards done**: the plate fill is followed by a dark blurred "veil" over the columns' bounding
  box, fading with the text (`movie.VEIL_DARK`); no stroke survives. `build.py` splices gfx/movie/STORYTITLE*.PMF
  (`movie.pmfs()`, renders missing ones; gfx/movie gitignored). Credits still open: staff rolls are in BADENDLOST,
  BADENDSEAL, TRUEEND (left column over scenery) and EPSOTD_END01-09 (per-chapter end credits, ~100 s each, cards of
  names over tilted photos). PROLOGUE and EYECATCH00-10 carry only the logo (K).

## Re-tour of 915f3c67 (worker 10 visual QA, verdicts work/qa/verdicts/chunk_bfd6e685d291_*.tsv)
- [x] **Worker 13: fixed.** The EBOOT holds its own zdv copies of ui_loading.g2d/.gim (ELF 0x2A64F0/0x2A6918, a
  scan for zdv headers found no others); `gfx.EBOOT_COPIES` + `build.eboot` recompress the English GIM into that slot
  (6.3 of 6.8 KB). Cold boot w13/dun_tut f002320 shows "Loading...".
  Dungeon loading indicator (dun1_direct f002260-f002290, dun_tut f002260-f002350): 読み込み中 on red diamonds,
  bottom right. Not the ui_loading.gim "Loading..." strip (that one was redrawn): another sprite/atlas.
  Worker 12: ui_loading.g2d does hold the diamonds (8 cells) + the strip prefixes 8,80 x 24..136 the game reveals one
  char per diamond, and the redraw is in gfx/out, yet the dungeon shows 読み込み中: a second copy with other bytes
  (`gimfind.py ui_loading.gim 8,80,136,24` found nothing; try the alpha mode / per-char 24x24 cells, or fileopen.py
  on a dun_tut state to see which pak the dungeon loads).
- [ ] City map destination list (city_map f000306) right-aligned: "Karasu no Mori Academy", "Karasuba Shrine",
  "Yahiro Academy", "Shinjuku Police" run left past the red panel border (x~378) onto the map.
  Same on the **school map room list** (field_ch01 sheets 33-55, f017770/f019570/f026170): "Audiovisual Room",
  "Student Council Room" ("udent" clipped). Worker 10 measured: the red panel is x 378-480, text x 383..472 = 89 px
  in advfont14; **26 EBOOT names 2b1e40..2b2038 are wider** (up to 183 px: city 2b1e40-2b1f18, rooms 2b1f58-2b2038;
  list: scratch rooms.py logic = sum of insert.font_widths("advfont14") > 89). Shortening all 26 guts the city
  names (Karasu Academy is still 120 px), so preferred fix: move the panel left (its g2d quad via gfx.LAYOUT, like
  the GAME OVER banner) and the list x (obj+0xb2, draw call 0x088E4168, engine.FLOOR_RIGHT) to give ~160 px; only
  "Karasu no Mori Academy" then needs a short form (D16). Fallback: short forms per D16 + fit-queue rows.
  **Worker 11:** the panel is no g2d quad found by shape scan (ui_map.g2d has only small cells; likely drawn by
  code/primitive), so took the fallback: `engine.FLOOR_RIGHT` 472 -> 477, `FLOOR_MAX` 97 px (start >= 380), 22 list
  names short (East Exit, Hanazono, Gyoen Park, Shinjuku Sta., Karasu Acad., Karasuba, Yahiro Acad., Shinjuku PD,
  Infirmary, Broadcasting, Custodian, Dojo, Guidance, Chem Lab, PC Lab, Home Ec., Principal, Librarian, Square Club,
  AV Room, Council Room...), full names in fit-queue; `batches.py check` fails a list name over 97 px. Verify next tour.
- [x] Field help bar "End Roaming△Look": no gap before △ (fend_c1 f000066/f000102). Worker 11: "End Roam" (74 px, JP 84).
- [x] Name entry. **Worker 13: accepted.** Clearing the default and typing in ABC mode draws the letters
  proportionally, left to right in the field (scenes `name_type`, `name_max`, w13/name_type). Only kana appended
  after the 9-letter default "Shichidai" land in fixed cells past the field; moved to docs/polish.md. Before (name_entry f003430, chunk 036; worker 12: tabs fixed, engine.NAME_TAB_X 10 -> 7, w12/name_entry; the
  typed-chars-after-default-name field limit still open): mode tabs "Kata"/"ABC" lose their last letter at the tab's right
  edge (カナ/英数 fit). Typed chars after the default "Shichidai" start at x~310, ~2 fit before the field edge x~340
  (JP 七代ああああああ fits): the field width counts the default name's bytes/cells; only seen when typing after the
  default name (players usually clear it). Check the field's max chars vs the 9-letter default.
- [x] Survey choice (choice_pre f008230/f008260, chunk 024; worker 12: bar y = the box's own y0 (0x14($sp) of the
  per-frame code) + CHOICE_BAR_DY instead of a fixed 92, w12/choice_pre f008230 on row 0): options "Remember the survey" / "Don't remember the
  survey" at y~36/56 but the red cursor bar at y~86-106, on neither row (the Shake hands choice is right). JP tour
  has no frame of it (shot every 90): re-shoot JP choice_pre around f008200-f008330 with --shot-every 30 first.
- [x] Status page (field_ch01 f007060/f007090; worker 12, w12/report + report_card: grid cells are 16 px frame tiles
  placed by code (no layout found; the t1 label type 1/2 is no font size), so status-cell short forms Reflex/Will/
  Judgmt/Jpn./Lang. (fit-queue, glossary alternates; engine asserts a label fits); report card Name row = one
  "given surname" string from x 324 (FULLNAME stub, "Name" label off screen) for both builders, Teacher (was
  Homeroom), Activity Log "Earlier" (was "Before Last"); Teacher value still tight to its label) still: Judgment into the Value column, Willpower/Reflexes/Stamina
  touch ▲, Japanese/Languages into the Grade column, ▼ on the Summary border, "Summary" header right-aligned.
  Report card (f007120/f007150): "Kazuki" over "Shichidai" (surname first), "Homeroom" over "Asako Hatori",
  Activity Log "Before" row shows "Last" and the "Last" row is empty. Worker 10: **confirmed on a fresh cold boot**
  of 4a7ae102 (work/qa/warp/mv/field_ch01 f007090 status, f007150 report card): stat names still run over the
  x 61 divider (engine.STATUS_CELLS lets too-wide names run right); report card Name shows "Shichidai" then
  "Kazuki" overprinted (two fixed slots like the status name box: reuse the engine.status_name FULLNAME/EMPTY
  stubs at the report card's surname/given label sites); "Homeroom" label overlaps the teacher name (move the
  value x right or label "Teacher"). Stat-name fix idea: widen the label column in the status frame texture
  (divider 61 -> ~80) and move STATUS_VALUES x 89 -> ~96.
- [x] Shop help bar "○ Confirm" ran off screen (shop f002260): questshoptext:0013 決定 -> "OK" like the other bars
  (worker 10; re-check in the next tour).
- [x] Phone Profile Book submenu "Report Card" touches the bezel (phone_prof f000236). Worker 12: labels x 294 -> 290.
- [x] Phone settings "Voices" (worker 12, was "Voice Volume") drawn condensed vs the other labels (phone_set f000420; its k_phon_set.g2d
  cell is x 0-63, worker 7).
- [x] Map "All Map" sideways label: gap between the words and a stray pixel line above "Map" (map f000390). Worker
  12: All bottom-aligned, Map top-aligned (w12/map); map bar Back x 392 -> 388.
- [x] Help bars (worker 12: `engine.help_bars` moves each menu bar's slots left by the widest label a slot shows;
  0x089D0850 places a slot, 0x089D086C sets its systemtext row; w12/menu_equip, menu_cards all clear): cards "□Armor Effect" under ✕ (menu_cards f000344); equip "△Remove □Range" under □/✕
  (menu_equip f000298); map bar "Back" touching ○. Fixed icon slots (qa-findings §Help bar): shorter words or
  engine layout by width.
- [x] Item menu "View Valuables": last s cut by the green divider at x~247 (menu_item f000252). Worker 11:
  "Valuables"; cards bar 武器効果/防具効果 -> "Weapon"/"Armor" (was "Armor Effect" under ✕). Equip bar still open.
- [x] (worker 13: moved to docs/polish.md, as engine.md §Open rates it; the outline keeps it legible) Readability over bright lights (ch08 f001960-f002410 corridor light at x 235-250, ch03 caption over a
  yellow sign): same as the Readability item above; sysfont18 is a plain 4-bit alpha mask (no outline in the
  font), so the fix is engine-side (shadow pass) or a wider gradient.
