# Graphics-text survey

Images are GIM (`MIG.00.1PSP`), many wrapped in `.zdv`, with a `.g2d` sprite/layout file beside most of them.
1,934 unique GIMs, all decode with `$SKILL/scripts/gim.py` (0 errors). Roundtrip (decode -> encode -> decode)
not yet run over all of them: do it before the first redraw (phase 8 prep).

## Static sweep (phase 1)
Sheets: `python -X utf8 tools/gimsheet.py work/unpacked work/survey --prefix <group> --max <px> --page 1400x1000`
(regenerable; `work/survey/<tag>.tsv` maps cell number -> md5, path, size). Groups and sheet counts:

| Group (prefix) | Unique | Sheets | --max | Reviewed | Japanese cells (cell no.: what) |
|---|---|---|---|---|---|
| title | 3 | 1 | 256 | yes | 1: title atlas: logo 東京鬼祓師 + subtitle 鴉乃杜學園奇譚 (logo: no official English version known, keep per D5; subtitle: translate), menu はじめから / つづきから (translate). 0: ATLUS logo (English). |
| system | 777 | 20 | 256 | no | |
| adv/ui_scene.pak | 5 | 1 | 256 | no | |
| adv/talk | 5 | 1 | 256 | no | |
| adv/obj | 9 | 1 | 256 | no | |
| adv/freemove | 14 | 1 | 256 | no | |
| dungeon | 66 | 3 | 256 | no | |
| effect | 117 | 3 | 256 | no | |
| adv/scene | 215 | 6 | 160 | no | |
| adv/effect | 80 | 2 | 160 | no | |
| adv/bg | 502 | 5 | 110 | no | (backgrounds: look for signs/posters) |
| adv/char | 156 | 1 | 110 | no | (portraits) |

## Outside the GIMs
- Movies `USRDIR/MOVIE/*.PMF` (H.264): `STORYTITLE01-10` (chapter title cards, almost certainly Japanese text),
  `EYECATCH00-10`, `PROLOGUE`, endings `EPSOTD_END01-09`, `BADEND*`, `TRUEEND` (credits roll likely). Burned-in text
  needs re-encoding + PSMF re-mux: see "Waiting on the user" in `docs/status.md`.
- XMB: `PSP_GAME/ICON0.PNG`, `PIC0.PNG`, `PIC1.PNG` (title art), `PARAM.SFO` title string.
- Boot notices (autosave warning, "memory stick" checks) are drawn as text over a GIM frame: font text from the
  EBOOT (`docs/re/text.md`), not graphics (verified by the strings found in the EBOOT).

## Tour (from the marker build, phase 5/8)
Screens seen so far on the original: autosave notices (text), ATLUS logo, title screen (graphic menu),
disclaimer screen (text). Add every screen whose Japanese doesn't change in the marker build.
