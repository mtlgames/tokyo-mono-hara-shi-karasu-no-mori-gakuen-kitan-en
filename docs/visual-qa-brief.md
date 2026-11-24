# Visual-QA reviewer brief - Tokyo Mono Hara Shi: Karasu no Mori Gakuen Kitan (PSP)

You review contact sheets from a translated build's QA tour and give each one a verdict. Read-only on everything
except your one verdict file: no edits to the repo, no git, no subagents. Run commands from the repo root with
`python -X utf8`; `$SKILL` = output of `python tools/skill.py`. Files over ~4 KB come back as a stub from a whole-file
Read: read `glossary.md` with offset/limit (or Grep it for a name).

## Inputs (in your dispatch)
- A chunk file: one `id<TAB>path` line per sheet. Read every sheet in it; none may be skipped.
- Your verdict file: `work/qa/verdicts/<chunk>.tsv`.
- The original game's shots of the same scene: `work/qa/warp/jp/<scene>/` (scene = the id's folder name), and
  `glossary.md`.

## How to look
- Read each sheet whole first. Where text is small, zoom into the source frame:
  `python -X utf8 $SKILL/scripts/sheet.py work/qa/warp/en/<scene>/fNNNNNN.png --crop x,y,w,h --zoom 3 --out <scratch>.png`.
  The screen is 480x272.
- When something looks wrong, open the same scene from `work/qa/warp/jp/<scene>/` (`sheet.py EN.png --compare JP.png`).
  If the original shows the same thing, it is the game's own behaviour: `ok`, with a note.
- Zoom into every choice box, selection row and menu label: a few pixels of misalignment don't show at sheet scale.

## Judge
An `issue` is any of:
- Japanese still visible (kanji/kana in text, labels, signs that carry meaning);
- text overflowing a box, clipped by a frame, or running off screen;
- text off-centre where the original centres it: an option in its selection box, a label, a heading;
- garbage glyphs, wrong or missing letters, a strike or stray pixels across letters;
- broken line breaks: a word split mid-line, a page ending mid-sentence;
- an empty box where text belongs;
- a name that differs from `glossary.md`.

Standing non-bugs, `ok`:
- text still typing out, a box mid-fade or mid-scroll, a cursor caught mid-blink;
- a map or scene still loading after a warp; black frames between scenes;
- anything identical in the original's shots;
- dialogue is horizontal and left-aligned in the ADV box (the original is vertical): this is the translation's
  layout, not a bug; speaker names show as ❖Name❖ (decision D8);
- location captions sit at the top right beside a red-diamond strip;
- player names `WWWWW` / nicknames in stress tests are deliberately wide;
- Japanese kept on purpose: the logo 東京鬼祓師, hanafuda poetry ribbons, school crests, Siddham seed syllables,
  item-icon packaging, scenery signs in 3D backgrounds; dungeon wall/floor kanji kept by D22 (virtue pillars
  智義信礼仁徳, horse pillars, 是/非, house plaques 南家北家式家京家, the small 点火 sign, calligraphy scrolls);
- the chapter cards (STORYTITLE 第N話 ...) and the staff roll in the ending movies: burned into PMF movies, a known
  open item; mark `issue` with the note "movie" so it routes to that item, nothing more needed;
- graphics text (menu headers, plates, panels drawn as pictures) still Japanese is an `issue` only if the sheet's
  build is newer than the graphics merge: say "graphics" in the note so it can be routed to the graphics list.

## Verdicts
Write your verdict file once you have read every sheet, one line per id in the chunk:
`id<TAB>ok|issue<TAB>what and where` (for an issue: which frame, which text, what is wrong).
Then return a short summary: counts, and the issues one per line.
