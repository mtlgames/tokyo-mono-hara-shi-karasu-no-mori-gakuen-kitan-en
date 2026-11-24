# Phase-8 visual-QA findings (tour of build 30bc8c09)

Verdict files: `work/qa/verdicts/chunk_c28c67163a69_NNN.tsv` (gitignored; zoom crops `work/qa/vqa_scratch/NNN/`).
One line per distinct problem; sheets named are examples. Tick when fixed and re-checked in game.

## Engine / layout
- [x] **ADV re-wrap:** dialogue sometimes ignores the stored `\n` and wraps greedily to x ~470, switching layout
  between consecutive frames (field_ch01 sheets 2/10/11/12/15/18/20). field_ch01_sheet_20 f011410: "Starting
  today, this is your new transfer student, Kazu|ki" runs off screen. **Not in the current build:** the same mash
  on e69f6e83 (work/qa/warp/cur/field_ch01, frame for frame the same timing) shows the stored wrap everywhere; the
  toured ISO 30bc8c09 carried older text. The re-tour covers the rest.
- [ ] **HUD player name** (dungeon + battle, every HUD frame): the name, drawn down the side plate in the original,
  is now one horizontal line "Shichidai Kazuki" over the AP gauge (the global horizontal drawer). Also surname-first.
- [x] **Choice bar** too narrow for proportional text ("Don't shake hands"): engine.choice_bar_px sizes it from the
  options' px width; inkbox 8/7 (work/qa/warp/bar/choice, cold boot).
- [x] **Wrong speaker plate:** ms01_00:011:35 (Hisae, 久榮) shows under ❖Gentle Schoolgirl❖ (field_ch01_sheet_22
  f012310-f012370); JP shows ❖久榮❖. Cause: 17-char names overflow the speaker-id lookup's 29-byte stack buffer
  into saved $s0 (engine.md §Name codes); fixed in engine.patch, cold boot work/qa/warp/spk f012332 shows ❖Hisae❖.
- [ ] **School map list** (field_ch01 sheets 29-42): "Audiovisual R", "Student Coun", floor "School Ga" clipped
  at the screen edge.
- [ ] **Main menu** (menu_sheet f000096): labels no longer right-aligned at x ~431; "Equipment", "Card Enhanc…" run
  over the red frame and off screen; "1,000 yen" n past the money plate's arrow tip.
- [ ] **Name entry** (name_entry_sheet_2): mode tabs "Hiragana"/"Katakana"/"ABC/123" spill onto the grid; right
  buttons show only "Cross:"/"Circle:" (action words cut); "Triangle: Input Mode", "Square: Convert" past their
  plates. Graphics: header 日常と意識に関するアンケート, labels ふりがな/氏名 still Japanese.
- [ ] Phone profile "Can't Change" past the phone screen edge (phone_prof_sheet f000236).
- [x] Caption dash "--" shows as two short hyphens with a gap (script "--" now encodes as ― 815C, one solid dash:
  work/qa/warp/dash f005290; the x 1 margin and " -- " vs "--" spacing are still open) ("Some years ago -- Public Library"); long caption
  starts at x 1 with no margin (field_ch01_sheet_7 f005290). Captions use "--" and " -- " inconsistently.
- [ ] Help bar overlap also on the school map and myroom_desk; map f000390 "✕ Back○ Confir" (no gap, cut at
  x 480); shop "○ Confirm" cut at x 480.
- [ ] Main/pause menu labels keep the JP start x: "Equipment", "Report Card" cross the red rule ~x 440,
  "Card Enhanc" cut (menu, menu_cards/equip/item, saveload, report). Right-align them.
- [ ] Quest-shop menu "Check Quests" right-aligned to x ~95, starts below x 0, C cut (shop_sheet f002530).
- [ ] systemtext:0041:00 has no `\n`: "You don't currently own this" runs onto the frame, "card." lost
  (menu_cards f000344; JP 2 lines).
- [ ] 103 table strings whose JP has a line break and whose English has none (buddymes 48, systemtext 16,
  questshoptext 14, help 10, item 10, dialogmessage 5): check each box's width; systemtext:0041:00 fixed.
- [ ] Item stats "AP Cost12": label over value (menu_item f000252).
- [ ] Equipped marker still kanji 装 ("Shinai 1装"); first category tab icon 全 (font glyph or graphics?)
  (menu_item f000252).
- [ ] Phone settings (phone_set f000420): text speed value 瞬 still Japanese (not in script/: EBOOT/graphics?);
  "Short" past the phone screen edge, "Slow" touches it; ringtone "01: Electronic T…" ellipsised
  (tables/clctmelody); graphics: "Voice Volum" clipped (gfx_phone.py label cell 66 px).
- [x] "--" in dialogue too (fixed with the caption dash) ("Even so--", trueend_sheet_14; prologue2): the dash glyph draws two short hyphens.
- [ ] "□ Show Help" runs to x 480, last p clipped (field_ch01_sheet_27 f014860).
- [ ] Readability: location caption and dialogue (no outline) over bright windows (field_ch01_sheet_28 f016210,
  sheet_29 f017470, sheet_3 f003250). The ADV gradient covers only x 0-150 (engine.md §Open): widen/darken it.
- [ ] **Status page / report card** (field_ch01_sheet_11/12 f007210-f007420): name letters stacked, stat names over
  the arrows, summary text clipped at screen edge, "Social Studies" over its grade cell, "Best Subject" over
  "Japanese", "Homeroom" over the teacher name, "Before Last" into the value column.
- [ ] **Tutorial Q&A panel** (dun_tut_qa_sheet): body text breaks per character ("mov|e") and runs past the panel;
  OXAS ticker "The Card Sealer exam has begun." runs onto the frame; opening quote shows as "˝", no closing quote.
- [ ] **City map** (city_map_sheet f000306): place list clipped at the panel edge ("Karasu no Mo…").
- [ ] **Help bar** (city_map, fend_c1): labels run under the next icon ("End Free Mo△Explo…"). Carried item.
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
