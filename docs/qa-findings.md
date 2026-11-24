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
- [ ] Name entry graphics: header 日常と意識に関するアンケート, labels ふりがな/氏名 still Japanese.
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
- [ ] 103 table strings whose JP has a line break and whose English has none (buddymes 48, systemtext 16,
  questshoptext 14, help 10, item 10, dialogmessage 5): check each box's width; systemtext:0041:00 fixed.
  Worker 6: help:08 (dungeon Q&A body) done (batches.TABLE_WRAP). Wrapping every multi-line JP entry at its own
  longest JP line would change 2,474 entries (most boxes are wider than the JP lines): not a rule; needs the box
  width per column in game (dialog boxes systemtext:00 / questshoptext:00 / dialogmessage:04 first, then
  buddymes:08 bubbles, item:0c descriptions). Add a TABLE_WRAP-like per-column px limit once measured.
- [x] Item stats "AP Cost12": label over value (menu_item f000252). The label is EBOOT 2b5148 "Attack ... AP Cost" (values at fixed x): 2 spaces fewer (verify).
- [x] Equipped marker still kanji 装 ("Shinai 1装"): lone EBOOT char the extractor missed (eboot_text.LONE, with
  円 0x2b5210) -> "E" (work/qa/warp/w6/menu_item). Help bar "Switch Type" under the SELECT icon -> "Category".
- [ ] First category tab icon 全 in the item menu (not text: graphics, menus group).
- [x] Phone settings (phone_set f000420): text speed 瞬 (EBOOT 0x2d2538, char[24] array, extractor LONE) ->
  "Instant"; "Short"/"Slow" past the screen: `engine.phone_settings` (start, gap) per row (work/qa/warp/w6/phone_set).
- [ ] Phone settings: ringtone "01: Electronic T…" ellipsised (tables/clctmelody); graphics: "Voice Volum" clipped
  (gfx_phone.py label cell 66 px).
- [x] "--" in dialogue too (fixed with the caption dash) ("Even so--", trueend_sheet_14; prologue2): the dash glyph draws two short hyphens.
- [ ] "□ Show Help" runs to x 480, last p clipped (field_ch01_sheet_27 f014860). systemtext:0659 -> "Help" (verify).
- [ ] Readability: location caption and dialogue (no outline) over bright windows (field_ch01_sheet_28 f016210,
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
- [ ] Emotion wheel labels too wide for their diamonds ("SorrowWorry", "FriendPassion", Passion cut) - gfx_adv_ui.
- [ ] "Arcane Eye" party plate clips the last e (every dungeon HUD frame).
- [ ] "START Open Phone": last e crosses the red frame (ch09 HUD).
- [ ] Dungeon HUD: for one frame after a step '切替' and '秘法眼' show (second texture copy not redrawn; dg01_sheet_5).
- [ ] Game Over banner ゲームオーバー still Japanese (gameover f000792; dungeon:40, status item (b)).
- [ ] Report-card heading 成績表 in one frame (field_ch01_sheet_12 f007270): a copy not redrawn.
- [ ] Staff roll / credits (badend sheets 2-7) and chapter cards (STORYTITLE01 第壱話 稲妻の転校生, field_ch01_sheet_6):
  burned into the PMF movies (Waiting on the user: movies).
