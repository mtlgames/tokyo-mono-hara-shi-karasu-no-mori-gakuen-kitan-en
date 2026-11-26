# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 9. **v1.0 published (2026-11-26, user asked):** GitHub release v1.0 with the zip (sha1 1813fe7e).
  Repo is still **PRIVATE**: switching it to public was blocked by the permission classifier, so the user has to do it
  (`gh repo edit --visibility public --accept-visibility-change-consequences`).
- **Post-release fix (2026-11-26, after v1.0 went up):** Player profile showed Japanese blood type "A型": EBOOT
  `%s型` (eboot:2b4360, 5 refs) was skipped by the extractor and the jp scan (ASCII + one kanji = "impure", same as
  the birthday spinners); added to `eboot_text.LONE`, "Type %s", verified in scene `phone_player` (build 99bcb38a).
  Birthday spinners: only in ad-hoc multiplayer Edit Profile (docs/re/debug.md §Script blocks), unreachable in
  headless; unverified. **Leftover sweep (same day):** every EBOOT string at 1+ chars, reachable by code/data word or
  inside a text table: 24 more found and translated (seasons 春秋冬, 円 0x2b55d8, name kanji 壇巴蒐要楼 -> full-width
  Dan/Tomoe/Shu/Kaname/Takadono, emotions 燃怒友 Fire/Rage/Pal, 12 nickname slots pn/pm+君様殿 -kun/-sama/-dono);
  `batches.EBOOT_LIMIT` lets Takadono pass the 3x-JP cap. release.py jp step now also runs `eboot_short` (1-char
  sweep; 0 on build 1ac10dcd). CSVB tables rescanned at 1 char: 0. Other CROW.PAK files at 1 char are binary noise
  (pwx/ksf parsed structurally). Kept on purpose: name-entry kana keyboard + internal name codes (338 untranslated
  eboot entries), jp_known.tsv. Re-tour of **1ac10dcd** (75 scenes, wrap_skip exit 3 as known): 69 new/changed
  sheets, chunks `chunk_b9a213c386f9_000..008`, all ok ("Type A", "1,000 yen" seen). `release.py --version 1.0.1`
  all steps pass: `release/v1.0.1/..._v1.0.1.zip` (140,480,321 B, sha1 ff579312; xdelta sha1 4686b6cf).
  **v1.0.1 published** (user asked; GitHub release v1.0.1, notes as a first release). v1.0 release and tag deleted
  (user asked). Repo still private: the user switches it
  public (`gh repo edit --visibility public --accept-visibility-change-consequences`).
- **Release rebuild (2026-11-26):** gate was STALE (tour on 467e169e). Full re-tour of **22455e6a** (72 states,
  wrap_skip exit 3 as known), `tour_sheets.py`: 49 changed sheets, chunks `chunk_da97de9ed821_000..006`, visual-qa
  verdicts 49 ok. `tools/release.py --force` **all steps pass**: check 30, jp 0, gate, cover 387/387, verify sha1 =
  build, zip `release/v1.0/Tokyo_Mono_Hara_Shi_Karasu_no_Mori_EN_v1.0.zip` (140,480,242 B, sha1 1813fe7e). Birthday
  spinners ("Mo %2d"/"Day %2d") not on any tour sheet: unseen in emulator. Next: publish only on user's say-so;
  hardware test still wanted.
- **Hardware audit (2026-11-26):** one real-hardware bug fixed: the added EBOOT segment sat after .data/.bss, and
  the PSP loader zero-fills only the last PT_LOAD's bss (PPSSPP zeroes all), so 8 MB of .bss would start as leftover
  RAM on PSP/Vita; signed header also had bss_size 0. `eboot.bss_last` (docs/re/text.md), test added. Build
  22455e6a: header bss 0x7DA1EC as the original, smoke + prologue + field_ch01 + report_card ok. Checked fine:
  stubs use aligned loads/stores and 16-byte stack frames, no run-time code writes (no icache flush needed), ISO
  dirs never move (path tables valid), 3 PT_LOADs (limit 4). Not changed: SYSDIR/BOOT.BIN is still the original
  Japanese plain ELF (CFW/Adrenaline boot EBOOT.BIN). release/v1.0 zip rebuilt after this fix (above).
  Hardware test still needed (READMEs now say "PPSSPP only").
- **Phase 9, worker 25 (2026-11-25):** re-tour of 467e169e finished (`--resume`, 72 states, wrap_skip exit 3 as
  known), `tour_sheets.py`: 71 changed sheets, 9 chunks `chunk_15cb49153b50_000..008`, visual-qa verdicts all 71 ok
  (help bar "[LR]Category [SELECT]Valuables" clear of the icon in menu_item/stress_items/stress_list).
  `qa_gate.py check` exit 0 (386 tour + 42 story). Fixed `tools/release.py` (skill.py's SCRIPTS is a str: wrap in
  Path; smoke step crashed). **`tools/release.py` all steps pass**: build 467e169e, check 29, smoke ok, jp 0 unlisted,
  gate, cover 387/387, polish, readme, debug, patch, verify (re-applied sha1 = build), zip
  `release/v1.0/Tokyo_Mono_Hara_Shi_Karasu_no_Mori_EN_v1.0.zip` (xdelta + README.txt, 140,480,162 B, sha1 baa7a484).
- **Next:** nothing left in phase 9. Publishing (GitHub release, upload) only on the user's say-so. Release-notes
  caveats stay: .znt dungeon-room textures RAM-verified only; stress_names_* need build/karasu_names.iso.
- **Phase 9, worker 24 (2026-11-25):** re-tour of 6e9c3389 done (72 exit 0, wrap_skip 3 as known), 15 chunks
  `chunk_5222a93de0d4_000..014` verdicted by visual-qa agents: 116 ok, story-pass dialogue fits everywhere shown;
  **4 issue, one cause, fixed:** item-menu help bar "Switch Category" ran under the SELECT icon -> systemtext:0209
  "Category" (qa-findings §Worker 24). Build `build/karasu_en.iso` **sha1 467e169e**, smoke ok, check green (29).
  New `docs/release-readme.txt` (zip README template; `release.py --steps readme` passes). Pre-ran release steps on
  6e9c3389: check, jp (0 unlisted), cover (387/387), polish (0 unticked), readme: all pass. **Re-tour of 467e169e
  started but Claude Code's memory reaper killed it after 19 scenes (last `choice`).**
- **Old next (worker 24; done by worker 25):** (a) free RAM, then `python -X utf8 tools/debug/warp.py build/karasu_en.iso --all --tag en
  --shot-every 30 --resume >> work/qa/tour_en.log` (the 19 done scenes are this build's; or `rm -rf work/states/en
  work/qa/warp/en` and run in full), `tools/tour_sheets.py`; expect only menu_item/stress_items/stress_list (+ timing
  jitter) to need verdicts; `qa_gate.py check work/qa/manifest.tsv work/qa/verdicts` exit 0. (b) `python -X utf8
  tools/release.py` (all steps) -> release/v1.0/ zip. Never `gh release create`.
- **Phase 9, worker 23 (2026-11-25):** **story pass done.** 42 parts reviewed (reviewer agents; reports in
  work/qa/story/reports/, first verdicts in work/qa/story/verdicts_old/: 24 ok, 18 issue, no Critical). Fixes:
  mechanical sweeps (669 "......" -> "...", " -- " -> "--"; 29 Gio "Whoa" -> "Oi oi"; 6 `{pm} {pn}` -> D1 order),
  then 324 report items + 11 game-wide voice lines in docs/polish.md §"Phase 9 story pass" (`tools/story_polish.py`,
  ids from new `tools/voice_scan.py`), 12 translator agents: ~1,700 strings changed, **polish.md 0 unticked**,
  `batches.py check` 0 problems. Voice rulings D25 + docs/style-reference.md bottom rows (Suzu "it is" on ~300 lines,
  Nagahide ye/yer, Angie "ne", まったく per speaker...). story.py + `qa_gate.py init` re-run, all 42 re-verdicted
  `fixed`: `qa_gate.py check work/qa/story/manifest.tsv work/qa/story/verdicts` exit 0. Build
  `build/karasu_en.iso` **sha1 6e9c3389**, smoke ok. Stopped near the context limit before the re-tour.
- **Old next (worker 23; (2) done by worker 24):** (1) done (story pass). (2) **Re-tour** of 6e9c3389 (`rm -rf
  work/states/en work/qa/warp/en`, `warp.py build/karasu_en.iso --all --tag en --shot-every 30`, `tour_sheets.py`),
  visual-qa verdicts for the chunks `qa_gate.py todo` lists (story pass changed ~1,700 more strings, longer Suzu/Angie
  lines: watch 3-line dialogue overflow; the earlier polish changed ~1,100 strings, captions now `X--Y`,
  some labels longer: 携行 "Carried", フリガナ "Name Reading", "Card Placement"), `qa_gate.py check` exit 0. (3)
  `python -X utf8 tools/release.py` (all steps) -> release/v1.0/ zip. Never `gh release create`.
- **Phase 9, worker 22 (2026-11-25):** **polish pass done**: 861/861 lines ticked (793 fixed, 68 waived; engine/label
  waivers reviewed: D20 short labels or items for the re-tour), 8 translator agents per `docs/polish-brief.md`
  (`tools/polish.py split|apply|count`, new `batches.py show REGEX [--en]` / `batch NAME`), ~1,090 strings changed,
  `batches.py check` 0 problems. **`tools/release.py`** written (steps build check smoke jp gate cover polish readme
  debug patch verify zip; `--steps` to run some). Its jp step (jp_left per text member vs the original; CSVB tables
  scan only what pointers reach, since English is appended; whole-file/offset waivers in `docs/jp_known.tsv`) found
  **two live strings the extractor missed**, now extracted and translated: obj:0817:04 猪牙の印章 "Boar Tusk Seal" (IBM
  kanji FB5E doesn't round-trip; `tables.text` accepts it, `raw` kept for the test) and eboot:2d2370 保持する "Keep"
  (struct byte before it; `eboot_text.ROW_START`, sweep found no other). jp step now 0. **EBOOT signed** (AGENTS.md
  ruling): `tools/sign.py` (sign_np from growlanser-psp-en, GPLv3 src in tools/sign_np/src, binary gitignored, build
  once under WSL; tag 5 = the original's 0xD91613F0, devkit 0x06000010), build.py writes the plain ELF to
  build/karasu_en.elf for scans; D24. README filled (status table, base hashes, known issues). Build
  `build/karasu_en.iso` **sha1 5b914abf**, smoke ok (signed EBOOT boots), check green (29). Release-notes caveats
  still: .znt dungeon-room textures RAM-verified only; stress_names_* need build/karasu_names.iso.
- **Phase 8, worker 21 (2026-11-25):** finished the 917ef4ac re-tour (`warp.py --all --resume`: new flag, skips
  scenes whose state exists, for tours killed by the memory reaper), `tour_sheets.py`: 44 changed sheets, 6 chunks
  `chunk_3dc47d49b0e7_000..005`, all verdicts (visual-qa agents): Counter plate, menu money plate, Chorus colon,
  fresh stress save confirmed; **1 issue, fixed:** quest-shop money plate past its border (qa-findings §Worker 21;
  `stress_shop` scene added). New `tools/debug/bpscene.py` (warp + breakpoints armed from boot: finds which call
  draws a label). Build `build/karasu_en.iso` **sha1 fefac907**, smoke ok, check green (29). Re-tour of fefac907
  (72 exit 0, wrap_skip 3 as known), 42 changed sheets in `chunk_5962f49167bf_000..005`: all ok (shop plate
  confirmed, stress_shop 9,999,999 fits). **Gate exit 0: phase 8 done.**
- **Phase 8, worker 20b (2026-11-25):** worker 20's fixes (money plate, per-run memstick, Counter plate) and its
  uncommitted staff-roll "Chorus      : Aina Kase" (colon now in the Vocals/Lyrics/Music column, checked on frame
  4191 of BADENDLOST) committed. Worker 20's own build.py died mid-movie (its claude.exe was still alive when this
  worker started; decided to let it finish, then built). Build `build/karasu_en.iso` **sha1 917ef4ac**, smoke ok,
  check green (29). **Re-tour started** (`rm -rf work/states/en work/qa/warp/en`, `warp.py --all --tag en
  --shot-every 30`): Claude Code's memory-pressure reaper killed it after 48 scenes (all exit 0; last done
  `wrap_skip`), so work/qa/warp/en holds a partial tour. **Next:** re-run the same tour command in full (free RAM
  first: other repos' harness runs share the machine), `tour_sheets.py`, verdicts for the chunks `qa_gate.py todo`
  lists (expect changes: money plate, Counter plate, stress save title, credits), `qa_gate.py check` exit 0, then
  phase 9 (.znt textures: RAM-verified, a shot not reached; accept that in the release notes).
- **Phase 8, worker 19 (2026-11-25):** all 24 chunks `chunk_4d8a89c9dff5_*` got verdicts (visual-qa agents; codex
  still limited): 188 ok, the ADV shadow clean everywhere; **2 issues, both fixed**: (1) status page: a 0's ▼ sat on
  the Summary divider (stats and subjects) and "Social St." crossed its cell: `engine.STATUS_VALUES/STATUS_DOWN`
  removed (value columns back at the original x 82/325, ▼ +20: ▼ now at JP's x, 10 px clear) and systemtext:0070
  "Soc. St." (glossary); (2) the PSP save dialog cut the title: eboot:2b0f88 "Tokyo Mono Hara Shi", 2b0e90
  "Tokyo Mono Hara Shi - Download Quest" (glossary row 東京鬼祓師; polish line ticked). Verified cold
  (work/qa/warp/w19/report). Build `build/karasu_en.iso` sha1 67a64351, smoke ok, check green (29). **Re-tour of
  67a64351** (`warp.py --all --tag en --shot-every 30`, work/qa/tour_en.log): see Next. **New `tools/debug/startroom.py
  bg11_00=waginoma bg07_00=seihennoma`** builds build/karasu_room.iso (QA only) whose dungeon .ini `startfloor` is
  rewritten, so `warp.py build/karasu_room.iso dun_bg11 --tag room` starts inside that room (verified: RAM shows
  `startfloor = waginoma` and bg0011_004 loaded). Walked a little with play.py (work/play/r11, r07): waginoma is a
  cave with roped rocks (objects = minimap purple crosses), the numbered tiles not yet in view; seihennoma start is
  a south corridor ending at a bridge (east blocked). Gotcha: warp.py reuses `work/states/<tag>/<scene>.ppst` if it
  exists, so after a rebuild delete it first or the shot shows the old code.
- **Phase 8, worker 18 (2026-11-25):** **all 7 open worker-17 findings fixed** (qa-findings §Worker 18), each
  verified in a cold-boot warp (work/qa/warp/w18/): ADV text **drop shadow** (`engine.shadow`, 3 black passes under
  every canvas draw; found that .data/.bss lui/addiu pairs relocate seg1-relative: GE state 0x0922C240, engine.md),
  Save/Load diamonds (gfx.LAYOUT whole-word strips), stress name fallback (FULLNAME stub > 145 px -> given name),
  money plate x, name tabs centred, Attack/AP layout (+ the second Defense copy), report-card Club field. Build
  `build/karasu_en.iso` sha1 da6c9f9e, smoke ok, check green (29). **Re-tour of da6c9f9e done** (work/qa/tour_en.log:
  71 exit 0, wrap_skip exit 3 as known), `tour_sheets.py`: 384 sheets, **190 without a current verdict in 24 chunks
  `work/qa/chunks/chunk_4d8a89c9dff5_000..023`** (the shadow changed every ADV sheet). codex exec still at its usage
  limit (resets 2026-11-26 14:14). Stopped near the context limit.
- **Phase 8, worker 17 (2026-11-24, stopped near the context limit):** (1) **Re-tour of d6101372** (68 scenes exit 0,
  wrap_skip 3 as known), `tour_sheets.py` (fix: a dir holding only final.png is skipped), 31 chunks
  `chunk_0c56a2b13473_000..030`, all handed to `translate-retro-game:visual-qa` agents (codex limit until
  2026-11-26; verdicts in work/qa/verdicts/). Findings in qa-findings §Worker 17: **dialogue unreadable over
  bright backgrounds** (chunk 002, real: white text over white windows; polish.md line 9 was wrong to call it
  legible) and **Save/Load diamond labels** small and off-centre (chunk 007); Council Room 4 px left accepted
  (verdicts overridden). (2) **Defense87 fixed:** `engine.defense_value` (value x0 + 42 -> + 56 at 0x089B2180) +
  label "Defense    "; verified on build/karasu_names.iso (9539370b) stress_items. (3) **Names stress** msg1/msg2
  on the names build: WWWWW spliced, 3 lines fit (work/qa/warp/nm/). (4) **The 34 blank-final sweep scripts:** run
  on the original (work/qa/cover/orig34.log): 19 blank there too; the other 15 (FN*_30 shop stubs, DG13_00, DG00_39
  ...) alternate text/blank in both builds (no background, typewriter or a blinking confirm); exit 3 is the
  final-frame phase, not a bug. `cover.py report` 387/387, exit 0; tables/EBOOT are covered by the menu tours (no
  per-string log; say so in the release report). (5) Scenes `dun_bg04/07/11` (dun_area 4/8/12) load each area's
  entrance (work/qa/warp/w17/); the textured rooms (.znt numerals/signs) are deeper: walk there or find the
  start-room field (debug.md "resume" +0x687C).
- **Phase 8, worker 16 (2026-11-24, stopped near the context limit):** (1) **Re-tour** of fd86cb47 (`warp.py --all
  --tag en --shot-every 30`, log work/qa/tour_en.log, all exit 0 but the known wrap_skip), `tour_sheets.py`: 369
  sheets, 29 chunks `work/qa/chunks/chunk_c8b1503f44a0_000..028` need verdicts (the rest kept theirs). **codex exec
  hit its usage limit (until 2026-11-26)**, so visual QA is done by hand: chunk 000 done (1 issue, fixed). (2)
  **Stress scenes** (scenes.txt §stress): `save.py` fields `items` (item list at 0x524, (row, count) x 425; `wide`,
  `wide16`, `29*1+250*99`), `read_given`/`read_family` (readings), name fields 30s. `stress_list`/`stress_items`
  (all / 16 widest item names x99, 9,999,999 yen: fit), `stress_names` (WWWWW names: status page, report card, save
  dialog fit), `stress_names_battle`, `stress_names_msg1/2` (see qa-findings: need build/karasu_names.iso). Tag `st`
  shots in work/qa/warp/st/. (3) Fixes: "Defense " stat label, `system/newdataicon.png` -> "New Save"
  (`tools/gfx_newdata.py`, gfx.py plain-file rows), 14 buddy bubble lines rewrapped + `batches.TABLE_PX` lint. In
  build d6101372. (4) **Text coverage** `tools/cover.py` (script level: 387
  .pwx with English; ids logged from warp/trace loads; tables/EBOOT need group waivers in docs/text_unshown.tsv):
  tour reached 22; `cover.py sweep` warps into every other script (results work/qa/cover/sweep.tsv, exit codes =
  crash/blank leads). (5) `tools/vqa_codex.py` runs chunks through codex exec once the limit resets.
  (6) **Sweep done: `cover.py report` 387/387 scripts shown** (365 swept: 330 exit 0, 34 exit 3 = blank final frame,
  1 crash). **Crash fixed: DG12_00** `{px}--` under a speaker whose EN differed from the EBOOT character-table EN
  (id -1): 52 table names synced to speakers.json + lint `speaker_table_problems` (qa-findings §Worker 16). Build
  `build/karasu_en.iso` sha1 d6101372 (all worker-16 fixes), smoke ok, check green; New Save icon verified in game
  (work/qa/warp/st/verify.png); "Defense87" not fixed by the space (open). The 34 exit-3 scripts
  (work/qa/cover/sweep.tsv) were not looked at: re-check a few against the original (`warp.py ROM NAME`).
- **Phase 8, worker 15 (2026-11-24, stopped near the context limit):** **EPSOTD_END01-09 credit cards in English.**
  `credits.py`: `card_holds` (a card = 15+ still frames, NCC > 0.97 right of x 255; the closing 企画 アトラス card
  mid-screen from x 150), `Tracker` (per-frame x shift by FFT correlation over the card's text rows + alpha),
  `card_track` (walks out of each hold while the match holds: eased slide-in, drift-out off screen, fades),
  `ink` = neutral pixels only (excludes sepia photos and END06-07's teal cards); English 15 px names / 12 px roles,
  centred lines stay centred. 33 unique cards, 303 rows in `gfx/credits/credits.tsv` (unnamed roles as
  speakers.json). `credits.table()` reads QUOTE_NONE ("Kirifuda" keeps its quotes; rolls re-rendered). All 12
  movies rendered, stamp current. New scene `edmovie1` (MS01_03 -> EPSOTD_END01; cold boot
  work/qa/warp/w15/edmovie1/final.png shows an English card). Build `build/karasu_en.iso` sha1 fd86cb47, smoke ok,
  check green (28).
- **Next (phase 8, worker 20+):** (a) Re-tour of 67a64351 done (71 exit 0, wrap_skip 3), `tour_sheets.py`: 38
  sheets in chunks `chunk_12538c997bbe_000..004`, all verdicts written: status page confirmed fixed; **1 issue**
  (chunk 004, stress_names_sheet): (i) the save dialog f000996 still shows the long title because the stress
  memstick's seeded save `work/qa/warp/en/stress_names/memstick/PSP/SAVEDATA/ULJM05638_KARASUNOMORI_0000/PARAM.SFO`
  dates from the old build (the dialog shows the existing save's SFO): find where warp/save.py seeds it, re-make the
  seed with the new build (or patch its SFO TITLE), re-shoot, check the title fits; (ii) money plate: "yen" n (x
  166-167, y 262-264) touches the arrow's lower diagonal at "1,000 yen" (stress_names f000506/f000720; original 円
  ends x 160): move the money text/unit ~3 px left (qa-findings line ~284 called it fixed). Then rebuild, re-tour,
  verdicts for changed sheets, `qa_gate.py check` exit 0.
  (b) .znt textures in game: `startroom.py` (above), then play.py from work/states/room/*.ppst; look for the yellow
  1-4 tiles (gfx/out/dungeon_tiles/*bg0011_004*.png) and the bg0011_obj003-006 wall numerals in waginoma, the Oni
  plate in seihennoma; jugon_hanahuda01/jugon_boss placement not found (obj.bin names them, objhaichi.bin does not).
  Maybe other floors of bg11_00 hold the walls: try other `startfloor`s. (c) Then phase 9.
- **Old next (worker 19; (a) done):** (a) verdicts for chunks `chunk_4d8a89c9dff5_000..023` (190 sheets, build
  da6c9f9e; do not rebuild first or the gate wants a new tour): `tools/vqa_codex.py --jobs 3` after 2026-11-26 14:14,
  else by hand (~8 sheets per chunk, verdict files work/qa/verdicts/<chunk>.tsv, stop near 150k context). Look for
  the shadow doubling/smearing text and any canvas text (captions, choices, names) it made worse. Then
  `qa_gate.py check` on the manifest must exit 0. (b) .znt texture rooms via dun_bg04/07/11. (c) Then phase 9.
- **Old next (worker 18; (b) done):** (a) all 378 sheets have verdicts (`qa_gate.py check`: 19 not ok, all listed
  in qa-findings §Worker 17). (b) Fix those open items: **readability** (most of the 19: dark band behind the ADV
  lines: find the gradient panel's draw, or a shadow pass in 0x08816988), Save/Load labels (saveload.g2d quads ->
  gfx.LAYOUT), 4-digit Attack value (like engine.defense_value), name-entry tabs centring, status-page stress name
  width, money plate "yen", report-card right-column margins. (c) .znt texture rooms via dun_bg04/07/11. (d) Rebuild
  (includes Defense fix), re-tour, tour_sheets, verdicts for changed sheets, `qa_gate.py check` exit 0.
- **Old next (worker 17; (a)-(d) done but fixes found):** (a) build d6101372 is current: re-tour (`warp.py --all --tag en --shot-every 30`; delete work/states/en/ first; ~45 min; includes the stress
  scenes now) and `tour_sheets.py`; unchanged sheets keep verdicts. (b) Visual QA of `qa_gate.py todo` chunks:
  `tools/vqa_codex.py --jobs 3` after 2026-11-26, else by hand (~8 sheets per chunk, stop near 150k context).
  (c) `cover.py` exits 0 at script level; decide tables/EBOOT (loaded whole at boot: waive as groups or note in
  the release report that the menu tours cover them); the 34 blank-final sweep scripts vs the original. (d) Names build:
  `build.py --qa tools/debug/stress_names.tsv --out build/karasu_names.iso`, run stress_names_msg1/2 on it.
- **Old next (worker 16; re-tour, stress, textcover started):** Re-tour (`warp.py --all --tag en`, delete work/states/en/ first; ~1 h+),
  `tools/tour_sheets.py`, `qa_gate.py todo` -> visual QA of the new manifest (no subagents in Orca runs: review the
  sheets yourself in a fresh read-only pass, or `codex exec`), then stress saves and textcover (skill phase 8
  done-when).
- **Phase 8, worker 14 (2026-11-24, stopped near the context limit):** **Staff roll in English** in BADENDLOST,
  BADENDSEAL, TRUEEND: `tools/credits.py` (scan: measures the scroll, stitches the roll, finds 240 text runs, labelled
  strips in work/movie/credits/; build: per frame fills the JP in the shifted run boxes, stamps English (Liberation
  Serif 15/13/11 px by the JP line height, condensed past x 172) with sub-pixel scroll, x264 per GOP at the lowest
  crf that fits, untouched GOPs kept byte for byte, `pmf.swap`; audio untouched). Text `gfx/credits/credits.tsv`
  (key, jp, en; "=" keep). Romanisation D23. Spliced by build.py via `movie.pmfs()` -> `credits.pmfs()` (renders
  missing/stale movies, stamp gfx/movie/credits.stamp, ~8 min for all three). Verified: frame compares of each movie
  vs the original, cold-boot warp `work/qa/warp/w14/badend` (roll plays in English). Build `build/karasu_en.iso` sha1
  0adbb746, smoke ok, check green (28).
- **Old next (worker 15; (a) done):** (a) **EPSOTD_END01-09 cards** (per-chapter end credits): `credits.py scan
  EPSOTD_END0*` keys 22 unique cards (cast cards 2-3 differ per chapter), but each card slides in from the left
  (~15 frames), holds, then drifts/fades; photos (sepia, G>60) reach x ~250 and pollute the max-over-time mask, so:
  take runs from a hold frame (mid-segment, not the ink peak), track each frame's x offset against it (column
  profile of neutral-white ink, max-min < 12, x >= 255), erase in the offset boxes, stamp English at the offset with
  alpha = ink ratio; re-check `same_card` keys after that. Then transcribe the card runs (most names are already in
  credits.tsv roll rows; new: per-chapter cast, 謎の老人/謎のインド人? roles, アトラス "Planning: Atlus"
  closing card), add them to `credits.DONE`. (b) Re-tour (`warp.py --all --tag en`, delete work/states/en/ first),
  `tools/tour_sheets.py`, visual QA of the new manifest, stress saves, textcover.
- **Phase 8, worker 13 (2026-11-24, stopped near the context limit):** (1) **Dungeon loader 読み込み中 fixed:** the
  EBOOT carries its own zdv copies of ui_loading.g2d/.gim (ELF 0x2A64F0/0x2A6918; RAM dump matched the original
  pixels, a zlib scan of the ELF found them, no other zdv in the ELF); `gfx.EBOOT_COPIES` + `build.eboot(text, ed)`
  recompress the English GIM into the slot (test_eboot_copies); cold boot w13/dun_tut f002320 "Loading...".
  (2) Report card 担任 -> "Tutor" (fit-queue: Homeroom Teacher), fits (w13/report_card); "Go-Home Club" still ends
  1 px on the right frame (values right-aligned to ~472; anchor not found, minor). (3) Name entry: typing an English
  name after clearing the default works (new scenes `name_type`, `name_max`); kana appended to "Shichidai" -> polish.
  (4) Readability -> polish.md. (5) `fileopen.py` runs without --state (cold boot). (6) Credits survey: the 9
  EPSOTD_END movies share some text cards but not all (cast/theme cards differ per chapter: per-movie transcription);
  cards are white serif text, right half, on black with falling red cards and tilted photos (left). Build
  `build/karasu_en.iso` sha1 4e8e811c, smoke ok, check green (27).
- **Old next (worker 14; roll part of (a) done):** (a) **Credits movies** (D3/D22: English): BADENDLOST, BADENDSEAL, TRUEEND (left
  column over scenery) + EPSOTD_END01-09 (~110 s, right-half name cards). Transcribe each card (frame grabs via
  `pmf.es` + ffmpeg, read at full res), romanise names (Hepburn with macrons as the glossary does; company names as
  they style themselves: Atlus, HYDE, Sunset Studio, Esprism), put them in a data file, then extend `tools/movie.py`
  (veil over each card's text rect + English lines with the card's alpha, pmf.swap keeps the container; audio
  untouched). (b) Re-tour (`warp.py --all --tag en`, delete work/states/en/ first), `tools/tour_sheets.py`, visual QA
  of the new manifest, stress saves, textcover.
- **Phase 8, worker 12 (2026-11-24, stopped near the context limit):** qa-findings §Re-tour items fixed, each checked
  in a cold-boot warp (`work/qa/warp/w12/`, tag w12): (1) **help bars** laid out by label width (`engine.help_bars`,
  HELP_BARS: equip/cards/item-get/card-effect bars; equip now "△Remove □Range ✕Back ○Select"); map bar Back x 388.
  (2) **Survey choice bar** follows the box y (CHOICE_BAR_DY). (3) **Status page** short cell forms Reflex/Will/
  Judgmt/Jpn./Lang. (D16 last resort: grid cells are code-placed frame tiles; fit-queue + glossary alternates).
  (4) **Report card**: whole name in one slot (FULLNAME stub now keeps a0 = character id; also on L/R switch),
  Teacher, Activity Log "Earlier". (5) Name entry tabs x 7, phone Profile labels x 290, "Voices", "All Map" caption.
  New scene `report_card`. Build `build/karasu_en.iso` sha1 6f24b0e9, check green (26), smoke ok.
- **Old next (worker 13; (a) done):** (a) left in qa-findings §Re-tour: dungeon 読み込み中 loader (notes there), name-entry
  field after the default name, readability over bright lights, Teacher value tight on the report card. (b) Credits
  movies (pmf.py swap; staff names need a romanised list). (c) Then re-tour (`warp.py --all --tag en`, delete
  work/states/en/ first), `tools/tour_sheets.py`, visual QA of the new manifest, stress saves, textcover.
- **Phase 8, worker 11 (2026-11-24):** (1) **Visual QA chunks 018-041** done by `translate-retro-game:visual-qa`
  agents (`qa_gate.py todo`: 0 of 338 without a verdict). New items in qa-findings §Re-tour: survey choice cursor bar
  off its rows (choice_pre f008230), name entry tabs "Kata"/"ABC" clipped + typed chars after the default name run
  out of the field. The rest were known items (staff-roll movies, room list, readability, loader sprite). (2) **City
  map / school room list fits:** the red panel isn't a g2d quad (shape scan of every UI g2d found none; likely drawn by
  code), so `engine.FLOOR_RIGHT` 477 + `FLOOR_MAX` 97 px and 22 short list names (full names in fit-queue, glossary
  alternates, `batches.py check` fails a list name over 97 px); verified in cold-boot warps `work/qa/warp/w11/
  city_map`, `field_rooms`. (3) Help bars: "End Roam" (gap before △), "Valuables", cards "Weapon"/"Armor". Build
  `build/karasu_en.iso` sha1 fb69132c.
- **Old next (worker 12; (a) mostly done):** (a) remaining qa-findings §Re-tour items: status page/report card (name stubs,
  Homeroom, stat label column), dungeon 読み込み中 loader sprite, equip help bar (Remove/Range in 28-42 px slots:
  engine layout by width), survey choice bar, name entry tabs/field, phone "Report Card" bezel, Voice Volume label,
  All Map label, readability. (b) Credits movies (pmf.py swap; staff names need a romanised list). (c) Then re-tour
  (`warp.py --all --tag en`, delete work/states/en/ first), `tools/tour_sheets.py`, visual QA of the new manifest,
  stress saves, textcover.
- **Phase 8, worker 10 (2026-11-24, stopped at the context limit):** (1) **Chapter cards done:** `tools/movie.py`
  adds a dark blurred veil over the erased columns (no stroke survives), `build.py` splices the 10 STORYTITLE PMFs
  (`movie.pmfs()` renders missing ones into gitignored gfx/movie, ~5 min; needs work/iso from unpack_all), verified
  in a cold-boot warp (work/qa/warp/mv/field_ch01 f004456-f004576, tag mv). Tests: identity build skips movies,
  `test_built_iso_changes` allows exactly the movie bytes. (2) **Visual QA** of chunks 000-017 (144 sheets) by
  `translate-retro-game:visual-qa` agents (codex out of quota to 2026-11-26): verdicts work/qa/verdicts/
  chunk_bfd6e685d291_000..017.tsv; every new problem is in `docs/qa-findings.md` §Re-tour of 915f3c67 (room/city
  lists 89 px panel with 26 names too wide + fix plan, status page/report card overlaps confirmed on a fresh boot,
  dungeon 読み込み中 loader, readability, help bars, phone labels, All Map, View Valuables). (3) Shop bar
  questshoptext:0013 -> "OK". (4) Movie survey: staff rolls in BADENDLOST/BADENDSEAL/TRUEEND + EPSOTD_END01-09;
  PROLOGUE/EYECATCH logo only (K). Build `build/karasu_en.iso` sha1 e0de3d9c, smoke ok, check green.
- Visual-QA dispatch prompt (worked for workers 10-11): brief + chunk + verdict file + "sheet N = frames
  16(N-1)+1..16N" + the known list, max 4 agents at a time.
- **Phase 8, worker 9 (2026-11-24, stopped at the context limit):** (1) `tools/gfx_dungeon_tiles.py`: 敵/将 map
  markers -> Foe/Boss, 鬼 stone plate -> Oni; virtue/horse/是非/plaques/点火 stay kanji (D22). (2) **Re-tour** of
  build `build/karasu_en.iso` sha1 915f3c67 (`warp.py --all --tag en --shot-every 30`, log work/qa/tour_run.log): 57
  scenes exit 0, `wrap_skip` exit 3 (black: the known block-11 warp limit, worker 3; ignore). `tools/tour_sheets.py`
  -> **338 sheets** `work/qa/tour/`, manifest `work/qa/manifest.tsv` (build 915f3c67), **42 chunks
  `work/qa/chunks/chunk_bfd6e685d291_000..041.txt`, none reviewed**. (3) **Movies:** `tools/pmf.py` (swap a
  re-encoded H.264 stream into a PMF, container byte for byte; works, crf 21-24 fits) + `tools/movie.py` (WIP, not in
  build.py): English lines and reveal timing work, erasing the calligraphy is unsolved (qa-findings §Graphics last
  item has what failed and the next ideas). Credits movies (BADEND*/TRUEEND, with audio) not started.
- **Phase 8, worker 8 (2026-11-24, stopped at the context limit):** (1) **Survey gap closed:** 1,560 `.znt` 3D
  models hold 1,091 unique GIMs the survey never opened (`gimsheet.py --embedded`, sheets `work/survey/znt/`; gfx rows
  `container.znt@0xOFF`, spliced back at the same size). The name-entry header was the whole **new-game questionnaire
  sheet** (`system/name_input.znt`): `tools/gfx_survey.py` redraws it with every answer at its JP x (pencil circles
  land right; cold boot work/qa/warp/w8/survey). Title form "Survey on Daily Life and Attitudes" (systemtext:0061 too).
  (2) `tools/gfx_dungeon_tiles.py`: kanji numerals -> 1-4 / 1-5 on dungeon walls, floor tiles and petitioner slips
  (not yet seen in game). Other dungeon kanji tiles listed in qa-findings (virtues, horse pillars, 是非, 敵/将, 鬼, 点火).
  (3) **Status page:** value columns moved, ▼ restored, labels/summaries fit (qa-findings §Status page, w8b/report).
  (4) "Help" verified. Build `build/karasu_en.iso` sha1 09412c49, check green.
- **Phase 8, worker 7 (2026-11-24, stopped at the context limit):** qa-findings ticked, each checked in a cold-boot
  warp (`work/qa/warp/w7/`, states `work/states/w7/`): (1) **GAME OVER banner**: the dungeon.g2d sprite reused the ー
  cell twice; new `gfx.LAYOUT` (byte patches of layout files, original bytes checked) repoints quads 2/4 to free
  dungeon08 cells, one "GAME OVER" line sliced over the 7 diamonds (w7/gameover5). Scene `gameover` now ends two
  turns in 30-frame steps (the first enemy turn can miss). (2) **85 table strings** with a multi-line JP box and
  one-line English longer than the JP's own longest line now keep the JP line count (`batches.shape`, self-test).
  (3) Arcane Eye plate / phone setting labels drawn inside their g2d cells; emotion wheel middle row Sad/Worry/
  Friend/Fire, none touch; item tab 全 -> "All" (category_icon.gim); "Phone" (was "Open Phone"); "01: Beep Tone".
  (4) `tools/gimfind.py`: which GIMs hold a copy of a cell (or of a screenshot crop, --lum/-lum). Dungeon HUD flash
  and report-card 成績表 frame: no other copy exists in any GIM (left for the re-tour). Build `build/karasu_en.iso`
  sha1 b96763ad, smoke ok, check green (26 tests, 0 lint).
- **Phase 8, worker 6 (2026-11-24, stopped at the context limit):** qa-findings ticked (all verified in cold-boot
  warps `work/qa/warp/w6/`): (1) **Q&A panel** wraps every 38 bytes: `batches.TABLE_WRAP` stores help:08 at 35 chars
  a line (41 re-wrapped; lint counts JP lines after the box's own wrap, the panel scrolls). (2) **OXAS ticker:**
  32-byte scrolling window -> `engine.ticker` 24 bytes; siteinfo items without quotes, 3-space gaps; new scene
  `dun_oxas`. (3) **Name entry** labels fit (Hira/Kata/ABC/!?#, ×Del/○OK, △Input Mode, □Convert): `insert.BUTTONS`
  lets table/EBOOT English use the ×○△□ SJIS marks (D20). (4) **Phone settings:** 瞬 -> "Instant" and item 装 -> "E",
  円 -> "yen": lone chars the extractor missed (`eboot_text.LONE`, FIXED char[24] for 瞬); `engine.phone_settings`
  (start, gap) per row so "Short"/"Instant" stay on screen. (5) Quest shop "My Quests"; help bars 決定 -> "OK" (map
  bar fits), item bar "Category"; city map list already fine. `fpregs.py` prints a0. Build `build/karasu_en.iso`
  sha1 5c08950f, smoke ok, check green (26 tests, 0 lint).
- **Phase 8, worker 5 (2026-11-24, stopped at the context limit):** (1) **HUD player name** (dungeon/battle):
  `engine.hud_name` = given name first (both "%s %s" sprintf sites swapped) and a stub on the `j` to the drawer moves
  it 48 px down, clear of the AP gauge (`jal_to` now takes op=j). (2) **Status page:** `engine.status_name` (whole name
  "given surname" in the first slot via a sprintf stub, furigana + "Name" off screen, D19), `engine.status_labels`
  (headers + stat/subject names centred in their grid cells: label x are `addiu $a1` immediates before
  0x0892B6B0, list work/qa/status_labels.txt), summaries shortened (systemtext 0400-0410, polish.md). Still open
  there: names wider than the 56 px cell (Willpower, Judgment, Japanese, Languages, Social Studies) touch the ▲:
  qa-findings §Status page. (3) `tools/debug/fpregs.py` prints the string at a1 too (who draws what at which x).
  Build `build/karasu_en.iso` sha1 5e92832e, smoke ok, check green; warp states `work/states/w5/` (current code).
- **Phase 8, worker 4 (2026-11-24):** (1) **Crash fixed:** 6acc09db died in field_ch01 at ms01_00:022:08
  (`{px}--` after the 17-char "Soft Girl's Voice"): the speaker lookup zeroed its buffer only to sp+0x1d, so
  15-17 char names matched no character (id -1) and {px} under id -1 crashes; `engine.patch` zeroes to sp+0x24
  (engine.md §Speaker-id lookups). field_ch01 runs to the end again. (2) **Main/pause menu labels right-aligned**
  to x 432 by advfont14 px width: `engine.right_align` = stub in the added segment at a DRAW_TEXT (0x08816988)
  call; **school floor/room list** uses it with keep (x = min(x, 472 - width), scene `field_rooms`). (3) Field help
  bar labels fit their slots (Bonds / Look / End Roaming); "Show Help" -> "Help", phone "Can't Change" -> "Locked",
  item "Attack/AP Cost" spacing (EBOOT 2b5148). Help-bar icons are sprites at fixed spots (qa-findings §Help bar).
  Warp states of this worker: `work/states/w4d/` (current code). Build `build/karasu_en.iso` sha1 1f9c3435,
  check green. Not done: the re-tour + visual-QA gate, other help bars (sprite icons), status page/report card,
  tutorial Q&A panel, city map list (EBOOT city names, same right_align idea), name entry, graphics items.
- **Phase 8, worker 3 (2026-11-24):** (1) **ADV re-wrap** finding is not in the current build: replaying the tour
  mash on e69f6e83 (`work/qa/warp/cur/field_ch01`, same timing frame for frame) shows the stored `\n` everywhere;
  the toured 30bc8c09 carried older text. (2) **Speaker plate stuck** (ms01_00:011:35): 17-char English names
  overflowed the speaker-id lookup's 29-byte stack buffer into saved $s0 (also the cause of the 18-char crash);
  `engine.patch` moves the save slot (engine.md §Phase 5 findings "Speaker-id lookups"); cold boot shows ❖Hisae❖
  (`work/qa/warp/spk`). (3) Script `--` -> ― (815C, `fontpatch.DASH`, solid dash verified `work/qa/warp/dash`);
  script `~` keeps the font's full-width wave (`fontpatch.KEEP`), 13 dialogue lines re-wrapped for its width.
  (4) scenes `wrap_type`/`wrap_skip` (block-11 warps of MS01_00: circle after the first line goes black, a
  block-start limit; use `script=MS01_00` + mash instead). Build `build/karasu_en.iso` sha1 6acc09db, check green.
  qa-findings.md ticked: re-wrap, speaker plate, both dash items; "~" pending an in-game look (dg01).
- **Phase 8, worker 2 (2026-11-24):** (1) **Visual QA of all 20 chunks** (157 sheets, build 30bc8c09) by
  `translate-retro-game:visual-qa` agents: verdicts `work/qa/verdicts/*.tsv` (gitignored), most sheets `issue`.
  **Every distinct problem is in `docs/qa-findings.md`** (engine/layout + graphics, tick boxes). Biggest: ADV
  re-wrap ignoring stored `\n` (text runs off screen), HUD player name drawn horizontally over the AP gauge, main
  menu labels not right-aligned, status page/report card overlaps, school/city map lists clipped, help bars, name
  entry screen, tutorial Q&A panel per-char breaks, "--" glyph, emotion wheel labels, Game Over banner. (2) **Choice
  bar fixed:** `engine.choice_bar_px` (code in the added EBOOT segment, relocated jal at 0x089F09DC; `eboot.add_segment`
  now grows that segment on a second call: only one spare phdr slot); inkbox 8/7 on `choice`. (3) systemtext:0041:00
  got its line break. Build `build/karasu_en.iso` sha1 e69f6e83 (choice bar + 0041 fix), smoke ok, check green. qa_gate:
  157 verdicts, 104 issue, 53 ok (STALE vs the new build until the re-tour).
  Note: `warp.py --tag X` reuses `work/states/X/<from>.ppst` (old code): delete the tag dir after an engine change.
- **Phase 8, worker 1 (2026-11-24):** (1) **Graphics pipeline:** `tools/gfx.py` (gfx/<group>.tsv rows `path<TAB>png`; build writes each PNG into every GIM copy with the same original bytes, nearest colour in the original palette; `--sheet DIR` original|English pairs; helpers original/clear/glow/save(rects: fails on pixels changed outside)/write_tsv), `tools/g2d.py` (sprite cells of a .g2d), OFL fonts in `fonts/` (docs/fonts.md), `docs/graphics-brief.md`, row lists `work/gfx/<group>.txt` (gitignored; regenerate from work/survey/*.tsv cells in docs/re/graphics.md). **Pilot** `tools/gfx_title.py`: title menu New Game/Continue + subtitle "Strange Tales of / Karasu no Mori Academy", verified in game (work/qa/smoke/title_zoom.png). (2) **Choice bar:** inkbox fails on `choice` (bar 111-268, "Don't shake hands" runs to ~275): bar w = (bytes/2)*18 from SJIS char count; needs a px width (engine.md §Open .ksf, 0x089FE704). (3) Visual-QA brief `docs/visual-qa-brief.md` (standing non-bugs filled in). (4) **Graphics wave 1 merged** (4 `translate-retro-game:graphics` agents; generators `tools/gfx_<group>.py`, rows `gfx/<group>.tsv`): title 1, phone 6/6, adv_ui 4/5 (freemove:6 is the same GIM as menus' system:20; freemove:12 pins only), adv_bg 9/9, menus 19/19, quest_site 16/16, dungeon_ui 8/10, dungeon_titles 25/26 (cell 15 is art only). Build `build/karasu_en.iso` sha1 30bc8c09, smoke ok, check green. Shortened labels -> docs/polish.md §Graphics; graphics terms -> glossary.md §Graphics labels (not enforced on text). (5) Reference tour of the **original** game: `work/qa/warp/jp/<scene>/` (52 scenes, shot every 90 frames); EN tour of 30bc8c09 -> `work/qa/warp/en/`.
- **Next (phase 8, worker 10+):** (a) Visual QA of the 42 chunks (`qa_gate.py todo` lists them; one
  `translate-retro-game:visual-qa` read-only pass per chunk, max 4 at a time, verdicts in work/qa/verdicts), add new
  problems to qa-findings, fix, rebuild, re-tour only the changed scenes. (b) Chapter cards: finish `tools/movie.py`
  erasing, wire `gfx/movie/*.PMF` into build.py (iso9660 patch of USRDIR/MOVIE), check in game (scene with
  STORYTITLE01: field_ch01 opening). (c) Credits movies (pmf.py swap keeps the audio packs; same approach). (d)
  Readability gradient (polish, below). (e) Stress saves, textcover, fit-queue columns (older lists below).
- **Next (phase 8, worker 9; (a)(c) done, (b) open):** (a) in-game look at the numeral tiles (bg11_00 rooms, jugon_hanahuda01) and decide
  the other .znt kanji tiles (qa-findings "Dungeon textures inside .znt models": virtue tiles need short words or
  stay K with the obj text; default: translate numerals/敵将/鬼 signs, keep house plaques the obj text romanises).
  (b) Readability gradient (polish: dialogue at the top over bright windows; adv_talk.g2d quad is scaled, so g2d.py
  doesn't list it; or thicken the sysfont18 outline in fontpatch). (c) Then rebuild, re-tour (`warp.py --all --tag
  en`; delete `work/states/en/` first), `tools/tour_sheets.py`, `qa_gate.py todo` -> visual-QA the sheets yourself in
  a fresh read-only pass, fix; then the older items below (stress saves, textcover, movies, fit-queue columns).
- **Old next (worker 8, done but (b)(c)):** open `docs/qa-findings.md` items: (a) **name-entry header** 日常と意識に関するアンケート
  and the ふりがな/氏名 plate (pencil icon): not the tables (screen shows hiragana ふりがな, tables have フリガナ and
  are English), not in the EBOOT, and gimfind finds no 1:1 GIM copy (dark-text and alpha modes): probably a scaled
  sprite; next try `tools/debug/bplog.py`/`fileopen.py` on the w7 name_entry state to see which file the screen
  loads, or gimsheet over GIMs near ui_name. Two English forms of that title (systemtext:0061 "Awareness",
  inputproftext:0000 "Attitudes"): pick one. (b) **Status page**: names wider than the 56 px cell touch the value ▲
  (glossary terms, Spirit is in Avoid): move the value column/▲ right (find its draw x: the report state
  `work/states/w5/report.ppst` ends on the school map, make a status-page state first). (c) Readability gradient
  (polish, engine.md §Open). (d) "Help" verify (field_ch01 ~f014860). Then rebuild, re-tour (`warp.py --all --tag
  en`; delete `work/states/en/` first), `tools/tour_sheets.py`, `qa_gate.py todo` -> visual-QA only the changed
  sheets (fresh read-only pass yourself: Orca allows no nested workers); then items (b)-(f) below.
- **Older next list (phase 8, worker 1):** (a) EN tour of 30bc8c09 done (52 scenes exit 0); `tools/tour_sheets.py` made 157 sheets `work/qa/tour/`, `work/qa/manifest.tsv` (build 30bc8c09) and **20 chunks `work/qa/chunks/chunk_c28c67163a69_000..019.txt` (8 sheets each), none reviewed yet**. Rerun `tools/tour_sheets.py` after any rebuild + re-tour. Dispatch `translate-retro-game:visual-qa` agents (docs/visual-qa-brief.md, max 4 at a time), fix issues. (b) **Graphics left:** effect:100/101 斬 split across two textures (needs the UV mapping), ゲームオバ(ー) in dungeon:40 (game reuses one ー cell: check the game-over screen, scene `gameover`), exbg0136 wheel kanji (~9 px), and **in-game verification** of: dungeon title cards' reading order (agent assumed right-to-left sprite order, `CARDS` in tools/gfx_dungeon_titles.py; see scene `battle`/`dg01`), menus' sliced stacked cells (map, album, save/load, flowercard bottom prompt row), phone icon/site label widths, dungeon:35/62 words split across one-char cells. Movies (STORYTITLE chapter cards, credits) still Japanese: re-encode project (Waiting on the user). (c) **inkbox:** choice bar too narrow (engine: px width instead of bytes/2*18). (d) **Stress saves:** save.py lacks inventory/card fields (map by diffing two saves); have money/names/chapter. (e) **textcover:** PPSSPP has no Lua: log per-script loads (trace_pw.py) as `TEXT <id>` or waive with reason. (f) Carried from phase 7 below.
- **Phase-7 review fixes (2026-11-24, worker 3; review `H:\translation\.harness\reviews\...-phase7.md`):** (1) Critical 1: `batches.py` px() counts name codes at their longest value (`var_values`: 5-W player name, widest nickname "Big Bro WWWWW" 164 px; D18), dialogue wrap is balanced (no stub last lines), 9,757 dlg/narr entries re-wrapped (one-off migration, inverted the old greedy wrap), `check` also fails a stored line shape() would re-wrap. (2) Critical 2: `check` fails any text entry with no English; the 57 (49 hanafuda names/labels, 3 item stat lines, 2 dictionary, 扉, 2 帝都防衛軍) got D16 short English ("Win Chf", "Chrysanth. I", "Soc.St +1  Jpn -1", "Dr"...; glossary short-form alternates flagged), full English still in `docs/fit-queue.tsv`. (3) Important 3: `test_built_iso_changes` builds into tmp and compares every CROW.PAK leaf + every table pointer + every other ISO file. (4) Important 4: `eboot.Patcher.log` = write log with expected originals, passed to romdiff; slots only for text entries with English. (5) Important 5: splice analysed (overflow past 161 bytes reaches only the unused pmyh buffer, engine.md §Name codes), in game scenes `splice1`/`splice2` show the name right; lint SPLICE_MAX 300 bytes after splicing. (6) Important 6: done with (1). (7) D11 reworded. Minor 8 (EBOOT re-sign) still open (Waiting on the user). Build `build/karasu_en.iso` sha1 693ea859, smoke ok, check.py green (26 tests).
- **Phase 7 done (2026-11-24, worker 2):** (1) **EBOOT pool:** strings reached only by data words now go to a new PT_LOAD segment past .bss (`eboot.add_segment`, docs/re/text.md §Free space): **no EBOOT string kept Japanese**. (2) **{px} crash fixed:** f8980 went away with the full-width character table once every string was English; the second crash (ms01_00:011:49 "{pn} {pm}-kun") was a game bug in the message name-splice passes (33-byte clear of a 161-byte scratch; `engine.patch`, docs/re/engine.md §Name codes; found with new `tools/debug/bpstr.py`). (3) `check.py` = tests + `batches.py check` (width/byte/code lint, 0 problems) + new `test_eboot_writes_in_range` (romdiff: every changed EBOOT byte is engine patch, string slot, string pointer, phdr or the new segment). (4) **`warp.py --all --tag en`: 52/52 exit 0** on build/karasu_en.iso c3642bd8 (dg01 route end lengthened: it ended in a fade). Fit probe: see engine.md §Width gate "Fit probe".
- **Carried (phase 8, from phase 7):** QA per the skill: contact-sheet tours of the en build (work/qa/warp/en/ already has all 52 finals), visual-QA verdicts (`qa_gate.py`), graphics-text redraws (docs/re/graphics.md T rows), inkbox on choices, stress saves, textcover. Carried from phase 7: (a) `docs/fit-queue.tsv` 87 rows, all now shipped as short English (57 of them got their short form in the phase-7 review fix; hanafuda names 14b / season labels 7b, dungeonsysmes short card names, item stat pairs 24b, 帝都防衛軍 18b, 扉 2b "Dr", 2 item names 16b): the 2x probe showed no crash where rows were visible; needs warp states with cards / quests / dictionary entries owned (save.py fields) to see those columns, then raise `batches.py` limits per column and re-merge the full English from the queue. (b) In-game checks from docs/tl-notes.md (runtime-joined EBOOT fragments, `%%`, mail ASCII art, questsent slot order). (c) Polish pass docs/polish.md + style-reference Minor 6 before the phase-9 story pass. (d) Help-bar icon layout, choice highlight width (polish). (e) EBOOT re-signing (see Waiting on the user).
- **Phase 7, worker 1 (2026-11-24):** phase-6 review (`H:\translation\.harness\reviews\...-phase6.md`) Importants: card names fixed (鬼手に太鼓 = Oni Hand and Drum everywhere; no "Mum"; short-form scheme in glossary + D16, every short dungeonsysmes line in fit-queue). **Open review Important:** item:0339:04 shows "Willow Ribbon" until the item-name column gets room (fit-queue). Minors done: D10-D17 in decisions.md, stale fit-queue row dropped, item:0325:04 queued, `batches.py --help`. Minor 6 (style-reference per-character rows) still open, before the phase-9 story pass.
- {px} crash history (fixed, worker 2): ASCII EBOOT character table (full-width now, D17) + the name-splice bug. Bisect tools: `tools/debug/buildvar.py --only/--qa`, `bpstr.py`. Disk H: is nearly full (~18 GB): delete build/var*.iso, build/karasu_fit.iso and other probe ISOs after use.
- **Phase 6 (2026-11-24, worker 2):** all 308 batches translated (wave 0 b001-b073 tables/speakers/EBOOT, wave 1 b074-b308 scripts), reviewed per 5-batch group (`work/tl/review/gNNN.md`, gitignored), Critical/Important fixed and re-merged (`tools/wave.py fixed`); `batches.py check` 40,572 entries, 0 problems. Glossary +100 rows from translator NEW TERMs (19 conflicts resolved); rulings Zero Chiaki (零 read ぜろ), ORDS = the cards, Partner Skill, stat lines "Stat +N  Stat -N", ailments "Inflicts X (N%).". `docs/synopsis.md` rewritten (cast, terms, chapters, recurring lines). Review Minors in `docs/polish.md` (977 lines, polish pass). Helpers: `tools/pairs.py` (reviewer pairs), `tools/wave.py done|fixed|minors|terms`, `docs/reviewer-brief.md`. **Build:** `build/karasu_en.iso` sha1 85305694 boots (smoke ok, prologue caption English). **EBOOT string pool is ~1.6 KB short:** `insert.eboot_patch` keeps Japanese for ~206 EBOOT strings (build WARNING lists them; docs/re/text.md §Free space has the numbers, segment layout and the phase-7 fix: grow seg1 past .bss). Fit queue: 61 over-limit lines + that pool row (`docs/fit-queue.tsv`).
- **Phase 6 progress (2026-11-24, end of worker 1):** wave 0 (b001-b073: speakers, all tables, EBOOT) translated, fixed and **merged: 8,952 entries, `batches.py check` 0 problems**; 57 over-limit lines wait in `docs/fit-queue.tsv` (hanafuda names in 14b/7b fields, 扉 2b, 帝都防衛軍 18b...: phase 7 buffer/engine work). Translator reports summarised in `docs/tl-notes.md` (in-game checks: runtime-joined EBOOT fragments, `%%`, mail ASCII art, questsent slot order). Minors in `docs/polish.md`. Build with wave 0 boots (smoke ok, karasu_en.iso d5d97ed0 before the last merges). **Wave 1 split: b074-b308** (235 script batches, story order ms/dg/fd/fn/qs per chapter) in work/tl/ (gitignored; regenerate with `batches.py split --only '^pw/'` on a fresh clone - deterministic). **Next:** dispatch `translate-retro-game:translator` agents, 5 batches each ("Read docs/translator-brief.md and follow it for batches bNNN..."), ~8-15 at a time; merge each passing batch (`merge --partial` for LONG-only failures); merge NEW TERMs into glossary between waves; reviewer pass (`translate-retro-game:reviewer`, docs/reviewer-brief.md still to write from the skill's assets/reviewer-brief.md) on every batch group; then update docs/synopsis.md from the translated story. Then phase 6 done.
- **Phase 6 pipeline (2026-11-24):** `tools/batches.py` split/check/merge/fit (px wrap at merge, limits per form, honorific + glossary checks; `--only REGEX` limits split to script paths). Brief `docs/translator-brief.md`, `docs/style-reference.md`, `docs/synopsis.md` (stub), `glossary.md` seeded (characters Hepburn no macrons; "(not enforced)" rows for ambiguous kanji). Wave 0 = b001-b073 (speakers, tables, EBOOT) in work/tl/ dispatched to translator subagents (codex out of quota until 2026-11-26; D9). After wave 0: `batches.py merge` each passing batch, merge NEW TERMs into the glossary, then `split --only '^pw/'` for wave 1 (scripts, ~170 batches), translators 5 batches each, reviewer pass per batch group. Last builds 2026-11-24: build/karasu_marker.iso sha1 39f74ecb (smoke ok), build/karasu_en.iso sha1 f13d8d09 (smoke ok), build/karasu_long.iso cafb9d7a (52/52 scenes exit 0).
- **Session 2026-11-24:** (1) `.ksf` choice cursor: the red bar object turned into a flat highlight that follows the row, keys DOWN/UP (engine.md §Open, verified work/qa/choice_bar*). (2) Long build per-row table caps max(16, 3x JP bytes) (`insert.LONG_ROW/LONG_MIN`; HUD label 0411 buffer 40 ok / 48 crash); `warp.py --all --tag long` 52/52 exit 0. (3) Menu pixel budgets from long-vs-original shots (engine.md §Width gate "Menu pixel budgets"; sheets work/qa/wg_menus1/2.png). (4) `tools/debug/bpsweep.py`: 0x088A69C8 = dungeon area label (now horizontal at x 5), 0x0883CBCC never fires. (5) scenes.txt `choice` needs one more advance.
- **Phase 6 inputs (lint budgets):** ADV line 464 px x 3 (sysfont18), names 17 chars, captions 336 px, notices 160 bytes, .ksf choices 29 bytes, table rows max(16, 3x JP bytes) within the column max, EBOOT strings slot or pool (~13.7 KB), menu px budgets per screen (engine.md). Help-bar labels have fixed ~40-55 px slots: translate short ("Back", "Select", "Map") and flag; engine work to lay icons out by width is a phase 7 candidate.
- **Session 2026-11-23 (b):** (1) `build.py --long` (insert mode `long`, `insert.table_max`): table lines filled to the column's longest original, EBOOT strings to their slot. First try (48 chars a line) crashed at boot: the system notice buffer holds **160 bytes** (measured). Long build boots; `warp.py --all --tag long` crashes at `field_ch01`; `tools/debug/longbisect.py` (new) blames `systemtext:0411:00` 良好 (field HUD status label, small buffer; engine.md §Width gate). (2) **EBOOT pool** (`insert.eboot_patch` + `eboot.pointers`/`same_hi`, test `test_eboot_move`): too-long EBOOT strings move into freed room, pointers retargeted from the relocation table; verified in game (work/qa/eboot_move.tsv: code-ref 閉じる and data-ref city names show moved English). 948/1,014 strings movable, ~13.7 KB pool (docs/re/text.md §Free space). (3) **.ksf choices**: scenes `choice_pre`/`choice` (MS00_01); `engine.patch` lays options out as rows (verified); cursor bar + left/right keys still to do (engine.md §Open has addresses and what failed).
- **Phase 5 so far** (notes `docs/re/engine.md` incl. §Phase 5 marker build findings + §Width gate, decision D8): dialogue was drawn vertically; `tools/engine.py` makes the drawer horizontal/proportional, stacks the 3 line canvases, limits the ADV vertical-form replace pass to 【】 (names show ❖Name❖), moves location captions to x 0 (insert right-aligns them to x 336 beside the red-diamond strip). `tools/fontpatch.py`: full-width stand-ins drawn as proportional ASCII, glyphs clipped by their advance widened (`!`). **`tools/insert.py`** (new): script/ -> game files, modes `en` (entries with `en`) and `marker` (`#n` + filler, n -> id in work/marker_ids.tsv): .pwx spans + speakers (full-width stand-ins, refuses `@ _ \` and stray braces, names > 17 chars), .ksf choices (ASCII, 29 bytes), CSVB tables (appended to the TblB pool + repointed, can grow), EBOOT strings in place (`eboot_room`); `NON_TEXT` excludes the name-entry grid + ASCII table. `build.py --marker` -> build/karasu_marker.iso; `build.py --qa FILE` (id<TAB>text overrides, `tools/widthgate.py` writes the width tests). Tests `tests/test_insert.py`. Debug: `warp.py --tag T` (states/shots apart per build), `tools/debug/poke.py`, `peek.py`, `tools/findtext.py` (which file holds a JP string; "nowhere" = graphics).
- **Width gate so far:** ADV line 464 px x 3 lines; speaker name 17 chars; caption 336 px; system notice 160 bytes; choice rows 29 bytes from x 116; city-map list ~11 chars (all in docs/re/engine.md §Width gate).
- **Next (phase 6):** batch translation per `references/translation.md` (batches in work/tl/, translator agents, reviewer pass), batch check/lint enforcing the budgets above. **Carried to phase 7:** EBOOT re-signing (`~PSP`; no compiler on this machine: `pip install ziglang` then build sign_np with `python -m ziglang cc`), help-bar icon layout, choice highlight width by px (polish).
- **Marker tour (2026-11-23, work/qa/warp/marker/<scene>/final.png, sheets tour*.png):** markers show in dialogue, menus, item/equip/cards, phone mail/quests, report card, shop, map, dungeon HUD, battle, myroom, city map; untranslated JP left on screen was all graphics or player-entered names (checked with findtext.py: phone menu, settings labels, 鴨乃杜 map label, credits, セーブ/ロード, ゲームオーバー). Polish (not blocking): ADV gradient panel covers x 0-150 only (text outline keeps it readable), page-wait icon now bottom-left.
- Phase 4: `tools/extract.py` dumps 40,572 entries to `script/` (pw/<dir>/<stem>.json: 29,758 script spans + 1,225 .ksf choices; speakers.json 221 names; tables/ 8,113 strings in 40 CSVB tables; eboot.json 1,255). Codecs `tools/pwx.py` (spans, inline codes, block table rebuild), `ksf.py`, `tables.py` (+ `csvb.strings`), `eboot_text.py`; reader `tools/source.py` (straight from the ISO). `tests/test_extract.py`: byte roundtrip of every string, pwx file rebuild, coverage (every SJIS byte in a span; table leftovers pinned with reasons), script/ in sync with a fresh extraction. Formats and waivers: `docs/re/text.md`. New finding: choice menus live in `.ksf` (30-byte slots).
- **Phase 5 inputs:** English can't be ASCII in .pwx (ASCII = commands): full-width Latin + VWF, or an engine hook; .ksf choices are 30-byte slots; EBOOT strings are slot-bound (relocation area needed, then re-sign); table strings can grow (append to TblB pool, repoint); speaker names via speakers.json; name entry (namedic.bin) and the nickname formats (`pnセンパイ`) need a plan.
- Phase 3: `build.py` (check dump, rebuild CROW.PAK via `pak.editor`, `iso9660.patch`); `build.py --identity` forces every nested pak repack + zdv recompress (level 6) and gives the original ISO byte for byte; test `tests/test_build.py` (identity + synthetic nested edit). Notes `docs/re/pak.md` §Identity. EBOOT not rebuilt yet: patching it needs re-signing (phase 5/7).
- **Done:** Step 0 (repo, rom.sha1, check + pre-commit hook rejecting failing tests, guard canary blocked, PPSSPP headless + windowed v1.20.4, boot route `tools/routes/boot.txt`, smoke passes on the original). Phase 1: CROW.PAK + .zdv formats (`docs/re/pak.md`, `tools/pak.py`, `tools/zdv.py`, `tools/unpack_all.py`), script/table/EBOOT text located and described (`docs/re/text.md`: SJIS, control codes, free space), decrypted EBOOT dumped to `work/exe/`, graphics-text survey of all 1,934 GIMs (`docs/re/graphics.md`: per-group table, T = translate / K = keep). No prior fan patch exists.
- Phase 2 (`docs/re/debug.md`, `tools/debug/`): `warp.py` + `scenes.txt` reach 53 scenes from a cold boot, all exit 0 in one `warp.py --all` run (2026-11-23); shot sheets `work/qa/warp/all_scenes.png` + `_2.png`, per-scene `work/qa/warp/<scene>/final.png`, states `work/states/<scene>.ppst`. Covered: name entry, prologue, ch01-ch13 openings, school field, main menu + item/equip/cards/phone (5 submenus)/save-load/report card/map, shop, trade, bad + true ending with credits, after-clear screens, tutorial dungeon + Q&A, chapter-1 dungeon (hub `dun1`, direct `dun1_direct`), **battle** (`battle`: 4 隠人 in 狩猟の間), **game over** (`gameover`: hp=1 + end turn), **myroom** (`myroom`, `myroom_desk` record shelf) and the **city map** with every destination (`city_map`), story flow (field_end, prologue2, fend_c1, after_c1). Spec keys: script= block= newgame from= set= (save.py fields: money chapter hp names dun_area) task= room= mash= route=. `save.py make|edit|show|load` edits plain saves that load with no error. Probes: pspdbg, bplog, watchw, findval, fileopen, rtti, find_cmd, trace_pw, `step.py` (one leg of play from a state, prints dungeon floor).
- **Next:** see "Next (phase 8)" above.
- **Known debug gaps (non-blocking, revisit in phase 8):** (1) the myroom **album** (ui_album.g2d, album_thum pak, `imagealbum.bin`) is not reached: the desk only shows the record shelf; unlock storage unknown (leads in debug.md "Myroom"). (2) `exbg0136` tutorial panel is named by no script (likely unused). (3) The hub -> bg01_00 walk in `dun1` hung once after a third door; `dun1_direct` avoids it.
- **Open bugs:** none.
- **Waiting on the user:** (non-blocking) EBOOT signing is done (2026-11-25, D24: the sign_np binary already built by growlanser-psp-en, copied in; signed EBOOT boots in PPSSPP). Owner: growlanser found a sign_np EBOOT black-screens on Vita/Adrenaline where the plain ELF plays; AGENTS.md says ship signed, so signed it is unless you change that line (this game's tag is one sign_np makes natively, unlike growlanser's). (non-blocking) movie text: STORYTITLE01-10 chapter cards and the ending/credits movies are H.264 PMF with burned-in Japanese; re-encoding them is its own project. Default: plan to re-encode the chapter cards and credits (D5 says translate all graphics text) unless the owner says to leave movies Japanese. (non-blocking) Graphics kept Japanese by default: title logo 東京鬼祓師 (no official English logo known), hanafuda poetry ribbons, school crests, Siddham seed syllables, item-icon packaging, dev placeholder cards; everything else in the survey is marked T.
