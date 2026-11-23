# Fonts

Every font or glyph sheet the build reads ends up inside the released patch, so its licence must allow that. One row
per file; a font with no known licence doesn't go into a release.

| File | Source (URL, version) | Licence | Redistributable in a patch | Used for | Changes made |
|---|---|---|---|---|---|
| game's own sysfont*.fnt | the game | - | ships as the game's own glyphs | dialogue/menus (tools/fontpatch.py widens ASCII) | ASCII advance widths |
| fonts/LiberationSans-{Regular,Bold}.ttf, LiberationSerif-{Regular,Bold}.ttf | https://github.com/liberationfonts/liberation-fonts 2.1.5 | OFL 1.1 (fonts/LICENSE-Liberation.txt) | yes, as rendered pixels | graphics labels, menus, panels (tools/gfx_*.py) | - |
| fonts/KaushanScript-Regular.ttf | https://github.com/google/fonts ofl/kaushanscript | OFL 1.1 (fonts/OFL-kaushanscript.txt) | yes, as rendered pixels | brush-style lettering (title menu, subtitle, brush title cards) | - |
| fonts/Anton-Regular.ttf | https://github.com/google/fonts ofl/anton | OFL 1.1 (fonts/OFL-anton.txt) | yes, as rendered pixels | condensed display labels | - |
