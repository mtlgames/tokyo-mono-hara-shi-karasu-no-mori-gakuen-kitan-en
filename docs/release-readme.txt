Tokyo Mono Hara Shi: Karasu no Mori Gakuen Kitan - English translation patch v{version}
========================================================================================

Unofficial English fan translation of Tokyo Mono Hara Shi: Karasu no Mori Gakuen Kitan
(PSP, Atlus, 2010). This zip holds only the patch; you need your own dump of the Japanese game.


Base image (must match exactly)
-------------------------------
Tokyo Mono Hara Shi - Karasu no Mori Gakuen Kitan (Japan).iso   (Redump)
Size   968,622,080 bytes
CRC32  45E4EECA
MD5    f4b2213627197cb5f9c97c2d202f0257
SHA-1  1d68889899448f0374eddb4b199b9aa827ae9f7b

A CSO/CHD, another revision or an already-patched copy will not work: convert back to a plain ISO first.


Applying the patch
------------------
The patch is an xdelta3 file: {patch}

  Windows: Delta Patcher or xdelta UI. Original file = your ISO, patch = {patch}.
  Command line:
    xdelta3 -d -s "Tokyo Mono Hara Shi - Karasu no Mori Gakuen Kitan (Japan).iso" {patch} karasu_en.iso

The patched image should be:
CRC32  {crc32}
SHA-1  {sha1}


Playing
-------
Tested in PPSSPP v1.20.4 only; not yet confirmed on a PSP or PS Vita (Adrenaline). Reports
welcome. Start from a cold boot after patching: savestates made with the
Japanese image carry the old text and code. In-game saves (memory stick) carry over fine.

What is translated: story, partner and free-time events, quests; menus, items, cards, skills,
dictionary, mail and system messages; the title screen, menus and banners drawn as graphics,
chapter cards and movies' on-screen text; the credits (staff names in Western order).
Voiced lines and songs stay Japanese audio.

Known issues
- Name entry: clear the default name before typing (letters added after "Shichidai" land past
  the field). The kana pages are still there.
- Some 3D dungeon-room wall textures were checked in memory only, not on screen.


Bugs and source
---------------
Report bugs (untranslated text, typos, overflow, crashes) on the project's GitHub Issues page,
github.com/mtlgames/tokyo-mono-hara-shi-karasu-no-mori-gakuen-kitan-en. A savestate helps most.

Tokyo Mono Hara Shi: Karasu no Mori Gakuen Kitan is (c) Atlus; this project is not affiliated
with them. Do not share patched images. The translation was made with extensive AI assistance
(Claude by Anthropic). Corrections are very welcome.
