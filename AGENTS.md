# Tokyo Mono Hara Shi: Karasu no Mori Gakuen Kitan (PSP) English translation

Skill: translate-retro-game (Claude Code: plugin, enabled in .claude/settings.json; other agents: `<SKILL_DIR>/SKILL.md`; `$SKILL` = the directory holding its SKILL.md, `python tools/skill.py` prints it). Read it before ROM, text or QA work.

## Commands (run from repo root)
- Build:    `python -X utf8 build.py` -> build/karasu_en.iso (checks the dump against `rom.sha1` first)
- Check:    `python -X utf8 tools/check.py` (tests + lint; the pre-commit hook runs this; `git config core.hooksPath tools/hooks` once per clone)
- Smoke:    `python -X utf8 $SKILL/scripts/emu.py build/karasu_en.iso --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Warp:     `python -X utf8 tools/debug/warp.py build/karasu_en.iso <scene|MS03_00> [--shot-every 60]` -> `work/qa/warp/<scene>/final.png` + `work/states/<scene>.ppst`; `--all` regens every state (scenes: `tools/debug/scenes.txt`, notes `docs/re/debug.md`; never ask the user to play to a scene)
- Trace:    `python -X utf8 tools/debug/trace_pw.py ISO --out DIR [--state S] --mash circle,right` logs each script the game loads
- Extract:  `python -X utf8 tools/extract.py [--force]` -> `script/*.json` from the original (never clobbers `en`; format `docs/re/text.md`)
- Release:  `python -X utf8 tools/release.py` (xdelta patch + verify; never publish without the user)
- Clean:    `python -X utf8 tools/clean.py` (published projects: lists rebuildable/downloadable files; `--yes` deletes)

## Paths
- Original ISO: `rom/Tokyo Mono Hara Shi - Karasu no Mori Gakuen Kitan (Japan).iso` (gitignored; SHA-1 in `rom.sha1`, checked by `tools/check_rom.py`).
- Emulator: QA uses PPSSPPHeadless qa-1 (machine-wide, `%LOCALAPPDATA%\translate-retro-game\ppsspp-headless\`, `fetch_emu.py ppsspp-headless`); people play with this repo's `tools/ppsspp/` (PPSSPP v1.20.4, https://github.com/hrydgard/ppsspp/releases/download/v1.20.4/PPSSPP-v1.20.4-Windows-x64.zip; gitignored). Savestates: `work/states/`.
- Text: `script/`. Tables: `tbl/`. Glossary: `glossary.md`. RE notes index: `docs/re/README.md`. Fonts and their licences: `docs/fonts.md`.

## Rulings
- Edit source files (.py .lua .asm .tbl .json) only with the file-edit tool; scripts here read and analyse, never `.replace()` and write back.
- Subagents: dispatch the agent types (translator, reviewer, visual-qa, playtester, graphics) shipped by the plugin as `translate-retro-game:<type>` (Claude Code), `.codex/agents/` (Codex) or `.opencode/agents/` (opencode), never general-purpose: their short tool list cuts each agent's start-up context from ~43k to ~9k tokens.
- The user's decisions, with the options and reasons: `docs/decisions.md`. Read it before asking the user anything; add each new ruling there the same session.
- Player bug reports: GitHub issues (`gh issue list --label bug`). Copy the attached save into `work/states/`, reproduce in the emulator, fix, commit with `Fixes #N`, and update `docs/status.md`.
- Boot: two autosave notices need circle (circle = OK, cross = cancel). `tools/routes/boot.txt` reaches New Game.
- EBOOT.BIN is encrypted (`~PSP`); ship a re-signed EBOOT, never the plain ELF.

## Status
`docs/status.md`: done, next, open bugs. Update it at the end of every session.
