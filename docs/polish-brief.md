# Polish brief (phase 9: tick every line of docs/polish.md)

You get one chunk `work/polish/cNN.txt`: `LINENO<TAB>- [ ] note` per line, each a Minor a reviewer deferred. For every
line decide **fixed** (the English now does what the note asks, or it already did) or **waived** (the note's
suggestion is not better, would break a rule, or needs engine/graphics work). Prefer fixing when the note is right and
the fix fits: voice, accuracy and natural English matter more than keeping the old wording.

Read first (long files in parts, offset/limit; a whole-file read returns a stub): `docs/translator-brief.md`,
`docs/style-reference.md`, `glossary.md`, `docs/decisions.md` (D-numbered rulings).

## Tools (run from repo root)
- Current text: `python -X utf8 tools/batches.py show 'REGEX'` (regex on the id: `'^fn11_11:021:06$'`,
  `'^buddymes:02(2[7-9]|3[0-7])'`), or `show 'REGEX' --en` to find English (term sweeps). Prints id, speaker, form,
  limit, JP and current EN. Batch several ids in one regex with `|`.
- Width dry-run: `python -X utf8 tools/batches.py fit "text" [--form dlg|caption|narr]`.

## Output (only these files; never edit script/, docs/, glossary.md or tools/)
1. `work/tl/pNN.out.tsv` (NN = your chunk number): `id<TAB>English` per entry you change, each id once. English is
   one line; " / " forces a break (dialogue and tables are re-wrapped by width on merge). Keep every control code,
   `{px}`/`{pm}`/`{pn}` and `%d`/`%s` exactly as in the current EN. If you change nothing, write an empty file.
2. `python -X utf8 tools/batches.py batch pNN` then `python -X utf8 tools/batches.py check pNN`: repeat until `OK`.
   A fix that cannot fit: drop its row and waive the line ("waived: no fit in 30b").
3. `work/polish/cNN.ticks.tsv`: `LINENO<TAB>fixed: <what changed, 3-10 words>` or `LINENO<TAB>waived: <reason>`, every
   line of your chunk exactly once.

## Rules
- Names and glossary terms stay as `glossary.md` has them. Do not rename speakers (the 【speaker】 column must match the
  EBOOT character table) or glossary entries; waive such lines with "waived: glossary/speaker name kept".
- A note about a term used in many places ("erosion" vs "Corrosion"): sweep every id with `show --en` and fix them all
  in your out.tsv, or waive.
- Lines about graphics labels, box widths, name entry or other engine behaviour: `waived: engine - <one line>`; the
  lead reviews those.
- No honorific dropped or added against the glossary; no suffix glued to a variable ("%dth").
- Return a final message of at most 5 lines: counts fixed/waived, the `check` result, anything the lead must decide.
