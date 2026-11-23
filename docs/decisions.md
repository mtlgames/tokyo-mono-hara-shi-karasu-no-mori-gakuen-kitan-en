# Decisions

The user's rulings on scope, style and trade-offs, newest last. Read before asking the user anything; if a later
decision replaces one, mark the old one "replaced by D<n>" instead of deleting it. Binding term spellings live in
`glossary.md`; this file holds the why.

| # | Date | Question | Options offered | Decision and reason |
|---|---|---|---|---|
| D1 | 2026-11-23 | Honorifics and name order | keep (-san), drop; JP or Western order | Keep honorifics; Western order (given name first). Owner's standing answer for one-shot runs. |
| D2 | 2026-11-23 | Romanization source for names | official art, earlier patch, Hepburn | Official English names where they exist, else an earlier fan patch, else Hepburn without macrons. |
| D3 | 2026-11-23 | Credits | stay Japanese, translate | English. |
| D4 | 2026-11-23 | Abbreviations | engine work first (default), abbreviate | Engine work first (default); abbreviate only as a flagged last resort. |
| D5 | 2026-11-23 | Graphics text left in Japanese | none (default), list | Translate all (titles, menus, banners, cards); keep the Japanese logo only if it has no official English version. |
| D6 | 2026-11-23 | Specs and plans | need approval, pre-approved | Pre-approved: keep going through checkpoints, report at the end. |
| D7 | 2026-11-23 | Existing saves / savestates | user's saves, none | None provided; build the debug tool as usual. |
| D8 | 2026-11-23 | English text path (agent call, pre-approved D6) | full-width monospace; proportional font patch; rotate glyphs to keep vertical text; horizontal engine hack | Horizontal + proportional: full-width stand-ins drawn with each font's ASCII glyphs and widths, EBOOT drawer patched to lay text out left to right, ADV lines stacked (3 lines, ~50 chars each). Vertical English is unreadable; monospace full-width wastes half the line. Details `docs/re/engine.md`. |
| D9 | 2026-11-24 | Who translates; register; romanisation detail (agent call, coordinator: decide with defaults) | codex exec (out of quota to 11-26); Claude translator subagents; worker alone | Claude `translate-retro-game:translator` subagents, 5 batches each, as AGENTS.md prescribes; a lone worker would need ~100 contexts. Register modern teen/YA, mythic lines formal; SFX English in asterisks; Hepburn without macrons or ou/uu (Toji, Shu). |
