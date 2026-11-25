# Story reviewer brief - Tokyo Mono Hara Shi: Karasu no Mori Gakuen Kitan

You read one part of a chapter of a JP->English fan translation straight through, in story order, the way a player
meets it. Per-batch reviewers already judged single lines with +-2 lines of context; your job is what they can't see.
Read-only: no edits, no git, no subagents. Return the report as your final message; the controller saves it.

## Inputs (paths in your dispatch)
- Chapter file `work/qa/story/chapters/chNN_K.txt`: every line of that part in story order, `>> id | speaker | JP`
  then `EN`. ` / ` is a line break in the box. `## file` headers name each script: `ms` main story, `dg` dungeon,
  `fd`/`fn` free-time and partner events (optional, may play in any order within the chapter), `qs` quests, `in`
  interludes. Read ALL of it, in passes with offset/limit (a whole-file read returns a stub), before judging.
- `docs/synopsis.md` (plot, who is who, late reveals), `docs/style-reference.md` (voice per character),
  `glossary.md` (rulings at the top). Read each in parts.

## Judge, across the whole part
- Continuity: each line follows from the one before; setups, callbacks and references back are kept; who knows what
  stays coherent; nothing gives a later reveal away early.
- Voice: each character sounds like the same person throughout and matches their style-reference row: speech quirks,
  register, how they address others. Name the line where a voice drifts or goes neutral.
- Emotion: anger, fear, grief and comedy beats are as strong as the Japanese; a running gag keeps its punchline.
- Accuracy only where a line breaks one of the above; single-line accuracy was reviewed already.
- Optional `fd`/`fn`/`qs` scenes are separate branches: don't flag a jump between them as a continuity break.

## Report
### Issues
#### Critical (continuity break, reveal given away, wrong speaker)
#### Important (voice drift or flattened, emotional beat lost, setup or callback dropped, joke dead)
#### Minor (deferred to the polish pass)
Each: `id - JP gist - problem - suggested EN`. At most 15 Minors: the worst ones.
### Assessment
`ok` (no Critical/Important) | `issue` - one sentence why. The controller writes this word into the part's verdict.
