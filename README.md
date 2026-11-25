# Tokyo Mono Hara Shi: Karasu no Mori Gakuen Kitan English translation

Unofficial English fan translation of **Tokyo Mono Hara Shi: Karasu no Mori Gakuen Kitan** (東京鬼祓師 鴉乃杜學園奇譚;
PSP, Atlus, 2010): the source text and tools that build the patch.

**Just want to play?** Download the patch from [Releases](../../releases) and follow its README. This repository holds
no game data you can play; you need your own dump of the Japanese game.

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
helps most.

## Translation status

| Part | Status |
|---|---|
| Story, partner and free-time events, quests | Translated |
| Menus, items, cards, skills, dictionary, mail, system messages | Translated |
| Title screen, menus and banners drawn as graphics, chapter cards, movies' on-screen text | Translated |
| Name entry | English (the kana pages are still there) |
| Credits roll | Translated (staff names in Western order) |
| Voiced lines, songs | Japanese audio |

Known issues: on name entry, clear the default name before typing (letters added after "Shichidai" land past the
field); some 3D dungeon-room wall textures were checked in memory only, not on screen; see
[Issues](../../issues).

## Base image

`Tokyo Mono Hara Shi - Karasu no Mori Gakuen Kitan (Japan).iso` ([Redump](http://redump.org/discs/quicksearch/Tokyo%20Mono%20Hara%20Shi/)),
968,622,080 bytes, CRC32 `45E4EECA`, MD5 `f4b2213627197cb5f9c97c2d202f0257`,
SHA-1 `1d68889899448f0374eddb4b199b9aa827ae9f7b`. Tested in PPSSPP v1.20.4; cold boot after patching (no old
savestates).

## What's here

| Path | What it is |
|---|---|
| `script/` | Every text block: original Japanese and English. Translation fixes go here. |
| `glossary.md` | Binding names, terms and style rules. |
| `tools/` | Python build chain: extract, insert, lint, release. |
| `tests/` | pytest suite (ROM-dependent tests skip when the ROM is absent). |
| `docs/re/` | Reverse-engineering notes. |
| `docs/decisions.md`, `docs/status.md` | Rulings with their reasons; current progress and open bugs. |
| `docs/fonts.md` | Fonts used and their licences. |
| `AGENTS.md` | Instructions for coding agents (`CLAUDE.md` points to it). |
| `.codex/agents/`, `.opencode/agents/` | Subagent types (translator, reviewer, visual QA, playtester, graphics) for Codex and opencode; Claude Code gets them from the plugin. |

## Build your own patched image

Needs Python 3.12+, WSL (to build the EBOOT signer once, see `tools/sign.py`), the decrypted EBOOT
(`docs/re/README.md`) and your own dump of the Japanese game.

```sh
git clone https://github.com/mtlgames/tokyo-mono-hara-shi-karasu-no-mori-gakuen-kitan-en
cd tokyo-mono-hara-shi-karasu-no-mori-gakuen-kitan-en
# copy your dump to: rom/Tokyo Mono Hara Shi - Karasu no Mori Gakuen Kitan (Japan).iso
#   (968622080 bytes, SHA-1 1d68889899448f0374eddb4b199b9aa827ae9f7b; the build refuses any other dump, see rom.sha1)
python -X utf8 build.py                                # -> build/karasu_en.iso
python -X utf8 tools/check.py                          # tests + text lint
```

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

## Licence

Tools and English translation: MIT; `tools/sign_np/` is GPLv3 (its own licence file). The original Japanese text in
`script/` is Atlus's and is included only so the translation can be checked against it. Tokyo Mono Hara Shi: Karasu
no Mori Gakuen Kitan is (c) Atlus; this project is not affiliated with them. Unofficial: do not share patched images.

The translation was made with extensive AI assistance (Claude by Anthropic). Corrections are very welcome.
