# Reviewer brief - Tokyo Mono Hara Shi: Karasu no Mori Gakuen Kitan (PSP, 2009)

You review one group of batches of a JP->English fan translation (Atlus' 東京鬼祓師 鴉乃杜學園奇譚). Review only: change
no file except your report, no git, no subagents. Mechanical validity (ids, control codes, width, glossary spellings,
honorifics after names) is already enforced by `tools/batches.py check` - judge translation quality.

## Inputs (paths in your dispatch; files over ~4 KB: read with offset/limit, in parts)
- Pairs file `work/tl/review/<group>.txt`: every entry as `>> id | speaker | form` / `JP:` / `EN:`, in story order.
  Read ALL of it, in passes.
- `glossary.md` (rulings and style rules at the top, then the tables), `docs/style-reference.md` (voices),
  `docs/synopsis.md`. The translators' reports `work/tl/<batch>.report.txt` (unverified claims: check their UNSURE lines).

## Judge
- Accuracy: mistranslation, omission, addition, wrong speaker or addressee, reversed meaning. Quote the JP and say
  what it means.
- Consistency: glossary names/terms exactly (a one-letter slip is what players notice); honorifics stable within a
  scene; the same recurring phrase or term rendered the same way across the group.
- Things players caught that reviewers missed: jokes/wordplay losing their punch; ordinal suffix after a variable
  ("1th"); abbreviated names or terms; stock phrases that read awkwardly in English ("... GET!").
- Voice: each speaker against their row in the style reference. Quirks and register (Toji rough, Minori assertive
  わよ/なさい, the retainer's archaic 坊/やしょう, old-man じゃ/のう/わし, feminine かしら/わよ/のね, rough ぜ/ねぇ/っス) and
  emotional intensity must come through in English, not be normalised into neutral prose.
- Naturalness: would a fan-translation reader stumble?

## Report: write it to `work/tl/review/<group>.md` (file-write tool)
```
### Critical
- id - JP gist - problem - suggested EN
### Important
- id - JP gist - problem - suggested EN
### Minor
- id - note (one line each; these go to the polish pass)
### Assessment
Approved | Needs fixes - one sentence why.
```
Critical: meaning reversed, broken code grammar, wrong speaker. Important: clear mistranslation, glossary
inconsistency, abbreviation, a voice flattened (quirk, register or emotional beat lost), a dead joke.
Your final reply is one line only: `<group>: C=<n> I=<n> M=<n> Approved|Needs fixes`.
