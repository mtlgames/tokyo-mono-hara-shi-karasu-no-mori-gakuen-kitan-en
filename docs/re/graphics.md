# Graphics-text survey

Images are GIM (`MIG.00.1PSP`), many wrapped in `.zdv`, with a `.g2d` sprite/layout file beside most of them.
1,934 unique GIMs, all decode with `$SKILL/scripts/gim.py` (0 errors). Roundtrip (decode -> encode -> decode)
not yet run over all of them: do it before the first redraw (phase 8 prep).

## Static sweep (phase 1)
Sheets: `python -X utf8 tools/gimsheet.py work/unpacked work/survey --prefix <group> --max <px> --page 1400x1000`
(regenerable; `work/survey/<tag>.tsv` maps cell number -> md5, path, size). Groups and sheet counts:

| Group (prefix) | Unique | Sheets | --max | Reviewed | Japanese cells (cell no.: what) |
|---|---|---|---|---|---|
| title | 3 | 1 | 256 | yes | 1: title atlas: logo 東京鬼祓師 + subtitle 鴉乃杜學園奇譚 (logo: no official English version known, keep per D5; subtitle: translate), menu はじめから / つづきから (translate). 0: ATLUS logo (English). |
| system | 777 | 20 | 256 | yes (S04, S15-17 = hanafuda faces / monster renders, by filename + spot check) | see "system detail" below |
| adv/ui_scene.pak | 5 | 1 | 256 | yes | 1: name/label atlas: 31 full names (雉明 零 ... 楼 万黎, カルパタル・T・シャンカル), ??? 出口 棚 白 鍵 鈴 雑貨を買う 購買 玩具を買う (T); 4: 探索中 (T) |
| adv/talk | 5 | 1 | 256 | yes | 0: emotion labels 喜 友 嫌 困 愛 燃 怒 悲 (T); 2: 次へ 速度 自動 (T) |
| adv/obj | 9 | 1 | 256 | yes | none (silhouettes) |
| adv/freemove | 14 | 1 | 256 | yes | 6: 鴉乃杜學園 新宿区 周辺 (T); 13: 探索中 (T); 12: map pins with tiny glyphs (check zoomed in tour) |
| dungeon | 66 | 3 | 256 | yes | 0, 2-26: brush-script boss/enemy title cards (七號 ... 隠人 + name, 鬼印盗賊団, 松に鶴 etc.; T, hardest redraw: calligraphy); 35: 隠人 罠の相手 開始 封札 終了 手番, 切替 秘法眼 (T); 36: 迎撃 ターン終了 (T); 40: kanji numerals 一..十, 封 攻, ゲームオバ(ー) (T); 62: 花札配置, 壱弐参肆伍 (T) |
| effect | 117 | 3 | 256 | yes | 75 敵, 80 火, 86 (one brush kanji), 100 斬, 101 (brush kanji), 104 煙: battle-effect kanji (T, stylised); 5, 12 Siddham/Sanskrit seed syllables (K, religious script) |
| adv/scene | 215 | 6 | 160 | S00-01 read; S02-05 by filename (all `ch*ad*` silhouettes) | none |
| adv/effect | 80 | 2 | 160 | yes | none |
| adv/bg | 502 | 5 | 110 | S00, S03, S04 read; flat-colour scan over all 502; S01-02 (bg/ebg photos) only at thumbnail size | see "adv/bg detail" below |
| adv/char | 156 | 1 | 110 | by filename (`ch*_*_*` portraits) | none expected |

### adv/bg detail
- `ebg0121` fiction disclaimer (この物語はフィクションであり… 絶対に真似しないでください) (T)
- `ebg0122` 完 ("The End") (T)
- `exbg0021`-`0024` prologue voice lines: 力が欲しいか？ / 秘法たる瞳を持つ者 尊き血脈に連なる者よ / 力が欲しくば 我を手にせよ—— / さあ—— (T)
- `exbg0136` tutorial panel 感情入力について / 操作方法 (two paragraphs) (T)
- `exbg0083` handwritten note on a card (T); `exbg0106` handwritten letter held in hands (T, check legibility in-game)
- Dev placeholders, grey cards "イベントBG: n <names>" (`ebg0071`-`0115`) and "解説画: n <subject>" (`exbg0010`-`0018`, `0028`, `0054`, `0056`, `0088`, `0093`, `0102`, `0129`, `0130`), `bg0085_01` (その他 青木ヶ原、樹海 昼夕夜): unfinished-art stand-ins, likely never shown (K unless the phase 8 tour or `textcover` shows one in use)
- 3D-rendered location backgrounds (`bg*`, `ebg*`): shop/street signage is scenery, mostly English or illegible at 480x272 (K; flag any legible Japanese sign in the tour)

### system detail (cell: pak, Japanese)
Translate (T) unless marked keep (K).
- 2 `_k_phon` phone UI: 呼出中・・・ 通話中・・・ 通話 拒否 決定 仲間 依頼人 プレイヤー (T)
- 4 `_k_phon` phone main menu: プロフィール帳 メール クエストの確認 OXAS公式サイト 携帯設定 プロフィール入力 (English subtitles already there; T)
- 5 `_k_phon` character name plates, 16 full names in kanji (雉明 零 ... 佐波守 紅緒) (T, glossary names)
- 7 `_k_phon_site` OXAS site: 隠人 用語辞典 解説 (beside English New/Information/Database...), ailments 封呪 骨折 捻挫 麻痺 睡眠 目潰し, ADV 移動 探索 メニュー その他, kana index あかさたなはまやらわ (T)
- 8 `_k_phon_site`: 新規 春夏秋冬 用語辞典 属性 解冥 移動 COST 回転 総AP 攻 入手アイテム 戻る 決定 選択 甲乙丙神 (T)
- 9 `_k_phon_site` settings labels: 基本文字送り速度 照準カーソル速度 自動文字送り状態 感情入力の長押し 効果音の音量 ターン終了確認 声の音量 ナビボイス 着信メロディ BGMの音量 (T)
- 17 `_report_card`: 成績表 (T); 745 `status01` report-card tables (体力 精神力 国語 数学 ... small print, T); 746 `status02` 成績表 header + button legend (T)
- 19 `_report_card` school crests 鴉乃杜 etc (K, emblems)
- 20 `_ui_map`: 鴉乃杜學園周辺 新宿区 (T)
- 28 `_ui_myroom` album categories: 全体 プ(ロローグ) 春夏秋冬 洞 マップ 演習場 龍珠堂 模擬 (T); 29: 第一話..第十話, その他 エンディング プロローグ アルバム (T)
- 57, 61, 65 `card` hanafuda poetry ribbons (あかよろし, みよしの): traditional card art (K); 103/749 card back 試 crest (K)
- 104 `cardarc` month plants 松梅桜藤菖蒲牡丹萩芒菊紅葉柳桐 (T)
- 590 `quest` avatar shirt print 廃人 (T, small); 624 ダウンロード中… (T); 627 依頼達成！ (T)
- 634 `quest` 情報屋 (QUEST SHOP subtitle exists; T)
- 636 `saveload`: セーブ ロード はじめから つづき (T)
- 583 `map_view` floor labels 第一..四階層へ 地上へ, horizontal + vertical (T)
- 639 `site`: 切替 なし 調べる (T); 641 秘法眼 (T); 646 攻 (T); 648 season wheel 春夏秋冬 強弱 (T)
- 649 curse legend 風呪 炎呪 土呪 氷呪 + 春属性化 (夏属性ダメージ10%増) x4 (T); 650 weapon ranges ナイフ 大剣 長剣 グローブ 槍 銃 (T)
- 652-654 ailment help panels (封呪 骨折 捻挫 麻痺 睡眠 目潰し 悪寒 吐き気 頭痛, each with 2-3 lines of rules) (T, long text)
- 656 電話で呼ぶ プロフィール (T); 657 アンケートを覚えている / いない (T); 658 emotion wheel 愛 悲 怒 友 (楽) (T)
- 751 `ui_equip` 装備 武器 防具 (T); 754 `ui_exitem` 貴重品 (T); 755 `ui_flowercard` 札 強化 (T)
- 758 `ui_hensei` 探索準備 武器 防具 (T); 762 `ui_item` アイテム, HP/AP (T); 765 `ui_itemchange` 入替 (T); 766 `ui_itemget` 入手 (T); 767 `ui_itemgive` アイテム (T)
- 770 `ui_loading` 読み込み中… (T); 776 `ui_shop` shop signs 雑貨 購買 玩具屋 (+ one more kanji sign) (T)
- Item icons (198-555): packaging print is illegible at icon size (K).

## Outside the GIMs
- Movies `USRDIR/MOVIE/*.PMF` (H.264): `STORYTITLE01-10` (chapter title cards, almost certainly Japanese text),
  `EYECATCH00-10`, `PROLOGUE`, endings `EPSOTD_END01-09`, `BADEND*`, `TRUEEND` (credits roll likely). Burned-in text
  needs re-encoding + PSMF re-mux: see "Waiting on the user" in `docs/status.md`.
- XMB: `PSP_GAME/ICON0.PNG`, `PIC0.PNG`, `PIC1.PNG` (title art), `PARAM.SFO` title string.
- Boot notices (autosave warning, "memory stick" checks) are drawn as text over a GIM frame: font text from the
  EBOOT (`docs/re/text.md`), not graphics (verified by the strings found in the EBOOT).

## Tour (from the marker build, phase 5/8)
Screens seen so far on the original: autosave notices (text), ATLUS logo, title screen (graphic menu),
disclaimer screen (probably the graphic `adv/bg/ebg0121`, see adv/bg detail; confirm in the marker build). Add every screen whose Japanese doesn't change in the marker build.
