# Translator brief - Tokyo Mono Hara Shi: Karasu no Mori Gakuen Kitan (PSP, 2009)

You translate part of the Japanese script of 東京鬼祓師 鴉乃杜學園奇譚 (Atlus) into English for a fan patch. A
modern-day occult school drama and dungeon RPG: a transfer student, a Card Sealer hunting the 48 Curse Hanafuda
cards, arrives at Karasu no Mori Academy in Tokyo, where Oni haunt the Hollow beneath the school.
Work only on the batches named in your dispatch, one at a time in the order given, each to a passing check before the
next. Do all translation yourself; do not dispatch subagents.

## Read first (files over ~4 KB: read with offset/limit, in parts)
1. `docs/style-reference.md` - voices, punctuation, approved example pairs. Match this voice.
2. `work/tl/terms_<batch>.txt` - binding glossary rows for this batch (`glossary.md` holds the rulings and the full
   table; read its "Rulings" and "Style rules" once).
3. `docs/synopsis.md` - who is who, as far as known. Don't invent plot beyond the lines you have.

## Input: `work/tl/<batch>.tsv`
`id<TAB>speaker<TAB>form<TAB>limit<TAB>Japanese`, story order: use neighbours for context.
- form: `dlg` (a speaker's text box), `narr` (box with no speaker: narration, inner voice, sounds), `caption`
  (location/time caption, one line), `choice` (menu option), `name` (a speaker name shown in the name plate),
  `table:<file>` (UI/data text: items, help, mails, quests...), `eboot` (menu text in the program).
- ` / ` marks the JP line breaks inside one box. Translate the box as one utterance; do NOT copy the breaks.
- limit: `3x464px` = up to 3 lines of 464 px (about 48 characters a line, ~140 per box); `336px` one line (~35
  chars); `29b` = 29 ASCII bytes; `17ch` = 17 characters; `Nb` = N bytes, `Nb KxMb` = N bytes in K lines of M.
- `{ruby:base|reading}`: furigana. The reading is how it is spoken; wordplay readings carry the meaning (glossary).

## Output: `work/tl/<batch>.out.tsv`, written with your file-write tool (not a shell heredoc)
`id<TAB>English`, every input id exactly once, same order, one line each. Plain printable ASCII: straight quotes,
`...`, `--`; no tabs, no Japanese or full-width characters, no `\uXXXX`, no `\n`. The build wraps dialogue and
table text by pixel/byte width; write ` / ` only to force a break (a list, a poem line, a table label that must
split where the JP did). Script text (dlg narr caption name) must not contain `@ _ \ { }` except the codes below.

## Validate
Run `python -X utf8 tools/batches.py check <batch>` from the repo root and fix every reported id until it prints
OK. `python -X utf8 tools/batches.py fit "text"` shows how a dialogue box wraps.

## Style
- Faithful: keep the information and order of ideas; adapt idiom, not meaning. Don't add or drop details; adapt
  wordplay so the joke lands (no translator notes).
- Keep the speaker audible: JP register markers become English devices (table in docs/style-reference.md). A line
  any speaker could have said is a mistake.
- Names and terms exactly as in the glossary; Western name order; honorifics kept and hyphenated (Toji-kun,
  {pm}-san, Hosaka-senpai). The check enforces honorifics after a name.
- `{px}` `{pm}` `{pn}` (player's full/sur/given name) and printf codes (`%s`, `%d`, `%3d`) must survive exactly:
  printf codes in the same order. No suffix glued to a code ("No. %d", not "%dth"); no a/an right before a name.
- Never abbreviate to fit. If a line can't fit without losing meaning, keep the meaning and report `LONG: id`.
- Empty-feeling lines (……。, ！？, ―――) still get English: `...`, `!?`, `--`.
- Sound/effect-only boxes (ドンッ) -> English onomatopoeia in asterisks: `*Thud!*`.

## Consistency
Never edit `glossary.md`. For a recurring name or term not in it, pick a form, use it consistently, and report it.

## Notes from earlier batches
- Wave 0 (tables) settled the terms in glossary.md: read its "Decisions from earlier batches" (full names, historical
  name order, hanafuda names, honorifics only after names). 鬼 alone is "demon"; 隠人 is "Oni".
- Don't force an honorific or a glossary term the check demands when the JP doesn't mean it: report
  `UNSURE: id - checker false positive` instead (the controller fixes the checker).
- Toji (rough), Minori (assertive わよ/なさい), the retainer (坊 = "young master", やしょう): keep them distinct.

## Report (reply with only this)
Batches done and entry counts; then any lines: `NEW TERM: jp -> en`, `UNSURE: id - note`, `LONG: id - note`.
