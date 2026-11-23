# Reverse-engineering notes

One file per subsystem (text engine, pointers, compression, font, graphics). Mark every finding with how far it is
proven, so a later session doesn't build on a guess:

- **verified** - and how: a decoded known string, a corrupt-and-boot test, a breakpoint hit on the drawing path, a
  passing roundtrip test. Name the test or savestate.
- **guess** - and why it seems likely (byte pattern, another game, an earlier patch's notes). Promote it to verified
  before code depends on it.

Addresses are for the dump in `rom.sha1` unless a note says otherwise.

| File | Covers | State |
|---|---|---|
| pak.md | ISO layout, CROW.PAK archive, nested paks, .zdv compression, EBOOT dump | verified (extract) |
| text.md | SJIS encoding, .pwx script format and control codes, CSVB tables, EBOOT strings, free space | format verified, codes partly guessed |
| graphics.md | graphics-text survey: GIM/g2d images, movies, XMB images | survey |

Prior work: none found (web search 2026-11-23: no English or other fan patch for 東京鬼祓師 鴉乃杜學園奇譚).
