"""gfx_dungeon_ui.py: dungeon HUD atlases and battle-effect kanji textures (group dungeon_ui).
Writes gfx/out/dungeon_ui/*.png and gfx/dungeon_ui.tsv.

    python -X utf8 tools/gfx_dungeon_ui.py

Rows: work/gfx/dungeon_ui.txt. Helpers (Edit, draw, erase, gradient_fill) come from gfx_quest_site.py. The HUD words are cut
per Japanese character by dungeon.g2d, so each English word is drawn across the cells of its Japanese word.
Not redrawn: ゲームオバ(ー) (dungeon08) - the game reuses one ー cell inside the word, an English word can't follow that
sequence - and the two halves of the 斬 slash kanji (player_atk_near02/03), which the effect splits across two textures.
"""
import numpy as np
from PIL import Image, ImageFilter

import gfx
import gfx_quest_site
from gfx_quest_site import ANTON, BRUSH, SANS_B, SERIF_B, WHITE, draw, gradient_fill, layer

GROUP = "dungeon_ui"
BLACK = (0, 0, 0, 255)


class Edit(gfx_quest_site.Edit):
    group = GROUP
HUD = dict(font=SANS_B, size=10, fill=WHITE, stroke=(1, (0, 0, 0, 255)))      # button captions and end-turn label


def hud_dungeon03():
    e = Edit("dungeon/ui/ui_dungeon.pak/dungeon/ui/dungeon03.gim")
    # 切替 / 秘法眼 beside the SELECT / START tokens (white, black outline, transparent cell)
    e.erase((73, 63, 52, 17))
    e.draw((73, 63, 52, 17), "Switch", align="l", **HUD)
    e.erase((73, 80, 52, 17))
    e.draw((73, 80, 52, 17), "Arcane Eye", align="l", **HUD)
    # brush banners: two rows of per-character cells; each English word spans the cells of its Japanese word
    band = dict(font=BRUSH, size=27, fill=WHITE, stroke=(1, WHITE))
    for box in ((0, 191, 200, 33), (0, 224, 256, 32)):
        e.erase(box)
    for word, x0, x1, y in (("Oni", 2, 67, 191), ("Trap Foe", 76, 198, 191),
                            ("Start", 2, 69, 224), ("Seal", 72, 125, 224), ("End", 127, 178, 224), ("Turn", 184, 250, 224)):
        e.draw((x0, y, x1 - x0, 32 if y == 224 else 33), word, **band, dy=-1)
    return e.row("切替 秘法眼; banner words 隠人 罠の相手 開始 封札 終了 手番 -> Oni / Trap Foe / Start / Seal / End / Turn")


def hud_dungeon04():
    e = Edit("dungeon/ui/ui_dungeon.pak/dungeon/ui/dungeon04.gim")
    e.erase((208, 88, 48, 15))
    e.draw((208, 88, 48, 15), "Counter", font=SANS_B, size=10, fill=WHITE, stroke=(1, (0, 0, 0, 200)))
    e.erase((184, 103, 72, 19))
    e.draw((184, 103, 72, 19), "End Turn", font=SANS_B, size=13, fill=WHITE, stroke=(1, (0, 0, 0, 255)))
    return e.row("迎撃 -> Counter, ターン終了 -> End Turn; ゲームオバ(ー) is in dungeon08")


def countdown_dungeon08():
    e = Edit("dungeon/ui/ui_dungeon.pak/dungeon/ui/dungeon08.gim")
    num = dict(font=ANTON, size=38, fill=WHITE, stroke=(1, (74, 0, 0, 255)),
               post=gradient_fill((227, 130, 60), (250, 239, 232), (74, 0, 0)))
    for i, word in enumerate(("10", "9", "8", "7", "6", "5", "4", "3", "2", "1")):
        box = (40 * (i % 5), 40 * (i // 5), 40, 40)
        e.erase(box)
        e.draw(box, word, **num, dy=1)
    # 封 / 攻 badges: yellow-orange letters with the same dark red edge
    for box, word, top, bot in (((1, 80, 33, 33), "SEAL", (249, 190, 1), (234, 83, 0)), ((39, 80, 26, 24), "ATK", (253, 222, 1), (245, 130, 3))):
        e.erase(box)
        e.draw(box, word, ANTON, 15, WHITE, stroke=(1, (74, 0, 0, 255)), post=gradient_fill(top, bot, (74, 0, 0)))
    return e.row("kanji numerals -> 10..1, 封 -> SEAL, 攻 -> ATK; ゲームオバ(ー) kept (see module note)")


def trapcard():
    e = Edit("dungeon/ui/ui_trapcard.pak/dungeon/ui/ui_trapcard01.gim")
    col = (0, 8, 26, 95)
    e.erase(col)
    e.vertical(col, "Place Cards", SERIF_B, 19, WHITE)
    for i, (x, box_w) in enumerate(((2, 20), (27, 20), (52, 20), (74, 21), (97, 21))):
        box = (x, 106, box_w, 20)
        e.erase(box)
        e.draw(box, str(i + 1), ANTON, 16, WHITE)
    return e.row("花札配置 (vertical) -> Place Cards, 壱弐参肆伍 -> 1-5")


# ---- battle-effect kanji (black = transparent in the game's additive blend, or real alpha) -----------------------
def flame_text(size, word, font, fs, top, bottom, halo, xscale=1.0, base=BLACK):
    """size x size RGBA: base colour with word in a top-to-bottom gradient and a blurred halo (effect textures)."""
    img = Image.new("RGBA", (size, size), base)
    ln = gradient_fill(top, bottom, (0, 0, 0))(layer(word, font, fs, WHITE, xscale=xscale))
    x, y = (size - ln.width) // 2, (size - ln.height) // 2
    a = Image.new("L", (size, size), 0)
    a.paste(ln.split()[3], (x, y))
    hal = a.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(halo[1])).point(lambda v: min(255, v * halo[2] // 10))
    h = Image.new("RGBA", (size, size), halo[0])
    h.putalpha(hal)
    out = img.copy()
    out.alpha_composite(h)
    out.alpha_composite(ln, (x, y))
    if base[3] == 255:
        out.putalpha(255)
    return out


def effect_enemy():
    e = Edit("effect/effect.pak/effect/enemy.gim")
    box = (0, 0, 64, 64)
    e.rects.append(box)
    img = flame_text(64, "FOE", ANTON, 36, (230, 110, 255), (150, 38, 130), ((180, 40, 220, 255), 1.6, 12), base=(2, 1, 3, 255))
    e.img.paste(img, (0, 0))
    return e.row("敵 -> FOE (purple flame lettering)")


def effect_fire():
    e = Edit("effect/effect.pak/effect/fire01.gim")
    box = (0, 0, 128, 128)
    e.rects.append(box)
    img = flame_text(128, "FIRE", ANTON, 70, (255, 251, 20), (225, 20, 0), ((241, 78, 1, 255), 3, 14), xscale=0.78)
    e.img.paste(img, (0, 0))
    return e.row("火 -> FIRE (flame gradient on black)")


def effect_earth():
    e = Edit("effect/effect.pak/effect/gimmick01.gim")
    box = (0, 0, 64, 64)
    e.rects.append(box)
    e.img.paste((0, 0, 0, 0), box)
    cv = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw(cv, box, "EARTH", ANTON, 25, WHITE, xscale=0.95)
    cv.putalpha(cv.split()[3].filter(ImageFilter.GaussianBlur(0.7)).point(lambda v: min(255, v * 5 // 4)))
    e.img.alpha_composite(cv)
    return e.row("地 (earth gimmick effect) -> EARTH")


def effect_smoke():
    e = Edit("effect/effect.pak/effect/smork01.gim")
    box = (0, 0, 128, 128)
    e.rects.append(box)
    old = e.img.copy()
    e.img.paste((137, 106, 88, 2), box)
    cv = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    draw(cv, (0, 0, 128, 128), "SMOKE", ANTON, 56, WHITE, xscale=0.7,
         post=gradient_fill((151, 91, 64), (91, 54, 36), (0, 0, 0)))
    a = cv.split()[3].filter(ImageFilter.GaussianBlur(2.2)).point(lambda v: min(235, v * 3 // 2))
    cv.putalpha(a)
    e.img.alpha_composite(cv)
    return e.row("煙 -> SMOKE (soft brown lettering)")


def main():
    rows = [hud_dungeon03(), hud_dungeon04(), countdown_dungeon08(), trapcard(),
            effect_enemy(), effect_fire(), effect_earth(), effect_smoke()]
    gfx.write_tsv(GROUP, rows)


if __name__ == "__main__":
    main()
