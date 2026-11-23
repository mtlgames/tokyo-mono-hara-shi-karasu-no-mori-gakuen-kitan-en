# Disc layout, CROW.PAK and .zdv

Game ID NPJH50215 (Atlus, 2009). ISO9660 UMD image, SHA-1 in `rom.sha1`.

## ISO (verified: `iso9660.py list`)
- `PSP_GAME/SYSDIR/EBOOT.BIN` 3,986,864 B, encrypted (`~PSP`). `BOOT.BIN` is all zeros (no plain copy on disc).
  Decrypted ELF dumped by PPSSPP v1.20.4 (`DumpFileTypes = 7`): `work/exe/NPJH50215_EBOOT.BIN` (gitignored; redo with
  `tools/ppsspp/memstick/PSP/SYSTEM/ppsspp.ini`, launch the windowed exe with the ISO, set it back to 0).
- `PSP_GAME/USRDIR/CROW.PAK` 387,006,464 B: every game asset except movies.
- `PSP_GAME/USRDIR/MOVIE/*.PMF`: 37 movies (prologue, endings, STORYTITLE01-10 chapter title cards, EYECATCH00-10).
- `PSP_GAME/USRDIR/MODULE/`: Sony PSMF player PRXs. `PARAM.SFO`, `ICON0/PIC0/PIC1.PNG`, `SYSDIR/UPDATE/` (firmware update, untouched).

## CROW.PAK (verified: `tools/pak.py`, all 7343 files extracted, offsets cover the data with no gaps)
LE. Header u32 ndirs (39), u32 nfiles (7343), u32 names_end, u32 data_start (0x31000).
- dir record x ndirs at 0x10, 12 B: u32 name_off, u16 first_subdir, u16 n_subdirs, u16 first_file, u16 n_files.
  Dir 0 is the root named `.`.
- file record x nfiles, 12 B: u32 name_off, u32 offset (relative to data_start), u32 size.
- name table: NUL-terminated ASCII, offsets relative to its start.
- Data: each file 0x800-aligned, zero-padded; file order on disc is not index order (rebuild sorts by original
  offset). The archive ends with 0x3000 zero bytes past the last file (rebuild keeps the original length).
- Nested `.pak` files (1401, one level deep, no pak inside a nested pak) use the same format; `pak.is_pak()` detects
  them. Their data_start is not aligned; members are 4-aligned and zero-padded in original offset order, which
  repacks all 1401 byte-identical (`pak.repack`, verified phase 3).

## .zdv (verified: all 1793 + nested inflate to their stated size)
LE u32 usize, u32 usize, u32 1, u32 csize, zlib stream. csize 0xFFFFFFFF = stored raw (108 nested files).
`tools/zdv.py`. zlib level 6 recompresses all 11,283 compressed originals byte-identical (verified phase 3).

## Identity build (phase 3, verified 2026-11-23)
`build.py --identity` rebuilds CROW.PAK (every nested pak repacked, every zdv recompressed, no edits) and patches it
into a copy of the ISO (`tools/iso9660.py`): sha1 equals `rom.sha1`. `tests/test_build.py::test_identity_build`
keeps it green (~20 s). Edits for later phases: `build.edits()` returns {unpacked path: payload}, same paths as
`unpack_all.py` writes; `pak.member` re-nests and recompresses. EBOOT.BIN is not rebuilt yet (needs re-signing
once it is patched).

## Contents by folder (CROW.PAK top level)
adv/ (bg, char, effect, scene = VN backgrounds/portraits/CG as GIM+g2d), dungeon/ (3D maps, per-dungeon paks with
block/*.bin), effect/, pw/ (script: dg fd fn in ms qs = .pwx text + .ksf), sound/ (at3, phd/pbd), system/ (UI paks,
card, item icons, map_view, quest, site, font), table/ (proftext etc.), title/, app_init.pak (fonts + 82 CSVB tables).

Full recon unpack: `python -X utf8 tools/unpack_all.py work/iso/PSP_GAME/USRDIR/CROW.PAK work/unpacked` (15,540 files).
