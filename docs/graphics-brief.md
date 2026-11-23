# Graphics brief - Tokyo Mono Hara Shi: Karasu no Mori Gakuen Kitan (PSP)

You redraw Japanese text drawn as graphics (menu labels, banners, name plates, panels) in English for a fan patch.
Work only on the groups named in your dispatch, one at a time in the order given, each one finished before the next.
Do all the drawing yourself; do not dispatch subagents. Run everything from the repo root with `python -X utf8`.
Files over ~4 KB come back as a stub from a whole-file Read: read them with offset/limit.

## Read first
1. `work/gfx/<group>.txt` - your rows: survey cell, GIM path (under `work/unpacked/`), size, format (idx4 = 16 colours,
   idx8 = 256), the `.g2d` layout beside it. What each cell says: `docs/re/graphics.md` (search the cell number or file
   name); the survey sheets are `work/survey/<tag>_NN.png` (cell numbers drawn on them).
2. The pilot: `tools/gfx_title.py` (generator) and `gfx/title.tsv`; the shared helpers in `tools/gfx.py`
   (`original`, `clear`, `glow`, `save(img, group, path, rects)` which refuses pixels changed outside `rects`,
   `write_tsv`). Copy the pilot's approach: one `tools/gfx_<group>.py` per group, translations as constants in it,
   rerunning it regenerates every PNG of the group and `gfx/<group>.tsv`.
3. `glossary.md` (names exactly as written there: Western order, no macrons) and `docs/fonts.md` (only fonts under
   `fonts/`: `LiberationSans-Bold.ttf` / `-Regular` for UI labels and panels, `LiberationSerif-*` for formal or
   printed-looking text, `KaushanScript-Regular.ttf` for brush lettering, `Anton-Regular.ttf` for condensed display).
4. `$SKILL/references/graphics.md` §Edit and re-import, §Lettering and §When the text is a texture
   (`$SKILL` = output of `python tools/skill.py`).

## Finding where a label sits
- `python -X utf8 tools/g2d.py work/unpacked/<dir>/<file>.g2d [--at X,Y]` lists every sprite cell (u,v,w,h) the layout
  cuts from the atlas: clear and redraw inside the cell that holds the Japanese, never past it (the game draws the
  whole cell). Full-screen 480x272 backgrounds (`adv/bg`) have no cell: work on the text area.
- Decode the original: `gfx.original(path)` (PIL RGBA). Find text rows/columns from the alpha channel or a zoomed crop
  (`$SKILL/scripts/sheet.py PNG --crop x,y,w,h --zoom 4 --out <scratch>.png`).

## You may write only
- `tools/gfx_<group>.py`, `gfx/<group>.tsv` (written by `gfx.write_tsv`), `gfx/out/<group>/` (written by `gfx.save`).
  Don't edit `tools/gfx.py`, `tools/gfx_title.py`, the build, `glossary.md` or another group's files; don't run
  `build.py` or an emulator, and don't commit. If you need a change to shared code, describe it in your report.

## Style
- One font, size and fill per label class within your group (tabs, headers, buttons, panel body text).
- Full words, no abbreviations to fit; condense (`xscale` 0.7-0.9 in `typeset.text_image`) or drop the size first. If
  something still won't fit, use the shortest wording you'd accept and report it.
- Match the original's colour (`typeset.dominant(crop)`), outline, shadow or glow and its position in the cell. Text
  over artwork: `typeset.inpaint(img, box)` before drawing, not a flat clear. Text on a transparent cell: `gfx.clear`.
- The build keeps each GIM's palette and maps every pixel to the nearest entry. idx4 (16-colour) images: draw at
  sizes >= 10 px in colours already in the image, and judge the encoded preview, not your PNG.
- Kept Japanese on purpose (do not redraw): the logo 東京鬼祓師, hanafuda poetry ribbons, school crests, Siddham seed
  syllables, item-icon packaging, grey dev placeholder cards.

## Check every image, offline
- `gfx.save(img, group, path, rects)` with every rect you cleared or drew in: it fails on any pixel changed outside.
- `python -X utf8 tools/gfx.py --sheet <scratch dir>` encodes every row with the real palette and writes
  original|English pairs; zoom yours (`sheet.py <pair>.png --zoom 3`) and read every label: every letter readable,
  nothing left of the Japanese. It exits 1 if any row fails to encode.
- `python -X utf8 $SKILL/scripts/rectcover.py JP.png x,y,w,h..` on each clear rect exits 0 (JP.png: save
  `gfx.original(path)` to your scratch dir).

## Report (your final message)
Per group: rows done, rows not done and why, new terms (`JP<TAB>EN`), any label shortened, shared-code changes you
need. Keep it short: the main thread reads only this.
