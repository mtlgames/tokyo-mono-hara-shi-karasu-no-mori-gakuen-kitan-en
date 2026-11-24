# Phase-8 visual-QA findings (tour of build 30bc8c09)

Verdict files: `work/qa/verdicts/chunk_c28c67163a69_NNN.tsv` (gitignored; zoom crops `work/qa/vqa_scratch/NNN/`).
One line per distinct problem; sheets named are examples. Tick when fixed and re-checked in game.

## Engine / layout
- [ ] **ADV re-wrap:** dialogue sometimes ignores the stored `\n` and wraps greedily to x ~470, switching layout
  between consecutive frames (field_ch01 sheets 2/10/11/12/15/18/20). field_ch01_sheet_20 f011410: "Starting
  today, this is your new transfer student, Kazu|ki" runs off screen. Some redraw path wraps by its own rule.
- [ ] **HUD player name** (dungeon + battle, every HUD frame): the name, drawn down the side plate in the original,
  is now one horizontal line "Shichidai Kazuki" over the AP gauge (the global horizontal drawer). Also surname-first.
- [x] **Choice bar** too narrow for proportional text ("Don't shake hands"): engine.choice_bar_px sizes it from the
  options' px width; inkbox 8/7 (work/qa/warp/bar/choice, cold boot).
- [ ] **Wrong speaker plate:** ms01_00:011:35 (Hisae, 久榮) shows under ❖Gentle Schoolgirl❖ (field_ch01_sheet_22
  f012310-f012370); JP shows ❖久榮❖.
- [ ] **School map list** (field_ch01 sheets 29-42): "Audiovisual R", "Student Coun", floor "School Ga" clipped
  at the screen edge.
- [ ] **Main menu** (menu_sheet f000096): labels no longer right-aligned at x ~431; "Equipment", "Card Enhanc…" run
  over the red frame and off screen; "1,000 yen" n past the money plate's arrow tip.
- [ ] **Name entry** (name_entry_sheet_2): mode tabs "Hiragana"/"Katakana"/"ABC/123" spill onto the grid; right
  buttons show only "Cross:"/"Circle:" (action words cut); "Triangle: Input Mode", "Square: Convert" past their
  plates. Graphics: header 日常と意識に関するアンケート, labels ふりがな/氏名 still Japanese.
- [ ] Phone profile "Can't Change" past the phone screen edge (phone_prof_sheet f000236).
- [ ] Caption dash "--" shows as two short hyphens with a gap ("Some years ago -- Public Library"); long caption
  starts at x 1 with no margin (field_ch01_sheet_7 f005290). Captions use "--" and " -- " inconsistently.
- [ ] Help bar overlap also on the school map and myroom_desk.
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
- [ ] **"~" glyph** (sysfont18): tiny raised dash with a gap ("fight~!", dg01 f005950, dun1_sheet_3).

## Graphics
- [ ] Emotion wheel labels too wide for their diamonds ("SorrowWorry", "FriendPassion", Passion cut) - gfx_adv_ui.
- [ ] "Arcane Eye" party plate clips the last e (every dungeon HUD frame).
- [ ] "START Open Phone": last e crosses the red frame (ch09 HUD).
- [ ] Dungeon HUD: for one frame after a step '切替' and '秘法眼' show (second texture copy not redrawn; dg01_sheet_5).
- [ ] Report-card heading 成績表 in one frame (field_ch01_sheet_12 f007270): a copy not redrawn.
- [ ] Staff roll / credits (badend sheets 2-7) and chapter cards (STORYTITLE01 第壱話 稲妻の転校生, field_ch01_sheet_6):
  burned into the PMF movies (Waiting on the user: movies).
