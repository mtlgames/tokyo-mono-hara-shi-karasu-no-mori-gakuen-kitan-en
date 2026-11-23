# Skill gotchas (one line each: reference file, then the fact)

- platform-psp.md: the EBOOT dump (`DumpFileTypes = 7`) does not happen with PPSSPPHeadless via `emu.py --memstick DIR` + `DIR/PSP/SYSTEM/ppsspp.ini`; the windowed PPSSPPWindows64.exe (portable `tools/ppsspp/memstick/`) dumped it within 25 s of launch.
- platform-psp.md: showgim.py only reads `work/gim/<id>.gim` and dies with `max() iterable argument is empty` when nothing matches (also on `--help`); this repo uses its own `tools/gimsheet.py` for numbered survey sheets over any folder.
- platform-psp.md: Atlus PSP (this game) CROW.PAK is not CPK: own dir/file-record archive, nested .pak of the same format, `.zdv` = 16-byte header + zlib (csize 0xFFFFFFFF = stored). Notes in docs/re/pak.md.
