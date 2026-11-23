# Glossary - Tokyo Mono Hara Shi: Karasu no Mori Gakuen Kitan

Binding for every translator and reviewer. Agents propose additions in reports; only the controller edits this file.
`tools/batches.py check` enforces every table row (a JP form present in the line needs one of the EN forms; `/`
separates alternatives) and the Avoid column.

## Rulings (asked of the user once; options and reasons in docs/decisions.md)
- Honorifics: kept, hyphenated (Name-kun, Name-san, Name-senpai, Name-sensei, Name-chan, Name-sama). The check
  requires the EN form whenever the JP honorific follows a name (kanji/katakana or a {px}/{pm}/{pn} code).
  Name order: Western (given name first): 穂坂弥紀 -> Minori Hosaka.
- Romanisation: official English names where they exist (none known: no official English release), else an earlier
  fan patch (none), else Hepburn without macrons and without "ou"/"uu" spellings: 燈治 Toji, 蒐 Shu, 清司郎 Seishiro.
- Credits: English.
- Register: modern teen/YA drama with occult mystery. Students talk casually; mythic, ritual and historical lines keep
  a formal, slightly archaic tone. Sound effects: English onomatopoeia in asterisks (*thud*), or describe them.
- Abbreviations: full names and terms everywhere, prefer engine changes over shortening (D4).

## Style rules
- Punctuation: 「」 -> "...", 『』 -> "..." (titles, quoted names), 《》 -> no marks (capitalise the term),
  …… -> `...`, ―― -> `--`, ！？ -> `!?`, ～ -> drop or stretch the word ("Heyyy").
- Script text (dlg/narr/caption/name) must not contain `@ _ \ { }` (engine commands); tables and EBOOT text are plain
  ASCII. `{px}` = player's full name, `{pm}` = player's surname, `{pn}` = player's given name: copy them exactly
  ("{pn}-kun"); never put a/an or a suffix right before/after them.
- Ruby `{ruby:base|reading}`: the reading is how the line is spoken. When the reading is wordplay (英雄 read ヒーロー,
  隠人 read おに, 子供 read ガキ) translate the reading's sense ("hero", "Oni", "brat"); never copy the braces.
- Voices: see docs/style-reference.md.

## Characters
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 燈治 | Toji | | Toji Dan (壇燈治), the hero's hot-blooded classmate and partner; rough male speech (ぜ/ねぇ) | Touji |
| 壇 | Dan | | (not enforced) Toji's surname; 壇 alone can be an altar/platform | |
| 弥紀 | Minori | | Minori Hosaka (穂坂弥紀), cheerful classmate | Yaki |
| 穂坂 | Hosaka | | | |
| 雉明 | Chiaki | | Rei Chiaki (雉明零) | |
| 白 | Mao | | (not enforced) ruby まお; when 白 means the colour "white" it is not this name | Haku |
| 巴 | Tomoe | | (not enforced) | |
| いちる | Ichiru | | | |
| 朝子 | Asako | | | |
| 長英 | Nagahide | | | |
| 久榮 | Hisae | | | |
| 義王 | Gio | | ruby ぎおう | Giou |
| 絢人 | Ayahito | | ruby あやひと; Ayahito Konosu (香ノ巣絢人) | Ayato |
| 蒐 | Shu | | ruby しゅう | Shuu |
| アンジー | Angie | | | |
| 鍵 | Ken | | (not enforced) the name (ruby けん); a key (かぎ) is "key" | |
| 鈴 | Suzu | | (not enforced) a bell is "bell" | |
| 伊佐地 | Isachi | | | |
| 道佳 | Dokai | | ruby どうかい | Doukai |
| 紅緒 | Benio | | | |
| 英雄 | Hideo | | (not enforced) the name (ruby ひでお); ruby ヒーロー = "hero" (his catchphrase wordplay) | |
| 輪 | Rin | | (not enforced) a ring/wheel is not the name | |
| 澁川 | Shibukawa | | | |
| カルパタル | Kalpataru | | | |
| 富樫 | Togashi | | | |
| 御霧 | Migiri | | | |
| 清司郎 | Seishiro | | | Seishirou |
| 筑紫 | Chikushi | | | |
| 万黎 | Banri | | | |
| 月舟 | Tsukifune | | | |
| カナエ | Kanae | | | |
| 宍戸 | Shishido | | | |
| 飛坂 | Tobisaka | | | |
| 蒲生 | Gamo | | | Gamou |
| 嘉門 | Kamon | | | |
| 幸徳路 | Kotokuji | | | |
| 日向輪 / 日向 輪 | Rin Himukai | | profile reading ひむかい | Hyuga / Hinata |
| 宝方蒐 / 宝方 蒐 / 宝方 | Takarakata | | Shu Takarakata | Hoho |
| 佐波守紅緒 / 佐波守 | Sawakami | | Benio Sawakami | Sabamori |
| 購買のおばちゃん | Shop Lady | 17 | school store lady (speaker name) | |

## Places
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 鴉乃杜學園 / 鴉乃杜学園 | Karasu no Mori Academy | | the school | |
| 鴉乃杜 | Karasu no Mori | | | |
| 寇聖 | Kosei | | rival school (寇聖高校 Kosei High) | Kousei |
| 新宿 | Shinjuku | | | |

## Items / skills / terms
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 封札師 | Card Sealer | | ruby ふうさつし; one who seals power into cards | Fusatsushi |
| 隠人 | Oni | | ruby おに; the monsters | Hidden Person |
| 呪言花札 | Curse Hanafuda | | ruby じゅごんはなふだ; the 48 cards at the story's core | |
| 花札 | hanafuda | | (not enforced) the card game / cards | |
| 洞 | Hollow | | (not enforced) ruby うろ: the underground labyrinth (秋の洞 Autumn Hollow); 洞窟 etc. are ordinary caves | |
| 秘法眼 | Arcane Eye | | ruby ひほうがん | |
| 神使 | divine messenger | | ruby しんし | |
| 龍脈 | dragon vein | | | |
| ＯＸＡＳ | OXAS | | organisation | |
| ＯＲＤＳ | ORDS | | ruby カミフダ; organisation | |
| カミフダ | ORDS / cards | | (not enforced) the organisation (ORDS) or, in card-game text, the paper cards themselves ("cards") | |
| 隠者の杖 | Hermit's Staff | | | |
| 秘儀を伝授されし者 | Initiate | | ruby イニシエ | |
| 体力 | Stamina | | stat | Vitality |
| 瞬発力 | Reflexes | | stat | |
| 精神力 | Willpower | | stat | Spirit |
| 脚力 | Speed | | stat | Footwork |
| 判断力 | Judgment | | stat | |
| 外国語 | Languages | | school subject | Foreign Language |
| 現代社会 | Social Studies | | school subject | Modern Society |
| 麻痺 | Paralysis | | ailment | Paralyze |
| 悪寒 | Chills | | ailment | |
| 札強化 | Card Enhance / Enhance | | | Card Boost |
| 調合 | Mix | | | Combine |
| 依頼 | Quest | | (not enforced) quest board; 依頼人 Client | |
| 特別依頼 | Bonus Quest | | | Special Quest / Special Job |
| 八汎學院 / 八汎学院 | Yahiro Academy | | ruby 八汎|やひろ | Happan / Yahiro Institute |
| 八汎 | Yahiro | | | Happan |
| 龍珠堂 | Ryujudo | | | Ryuzudo / Ryushudo / Dragon Orb Hall |
| 特課 | Division | | 収集特課 Collection Division | Special Section / the Unit |
| 札憑き | Card-Possessed | | | card-bearer |
| 執行者 | Executor | | | Enforcer |
| 鬼印盗賊団 | Oni Mark Bandits | | 盗賊団員 Bandit | Oni-Mark Thieves / Demon Mark Bandits |
| 鬼印 | Oni Mark | | | Demon Mark |
| 鬼札 | Demon Card | | | |
| 封念ノ神鏡 | Sealing Mirror | | | Thought-Sealing Mirror |
| 封具ノ器 | Sealing Vessel | | | Sealed Tool Vessel |
| 御蔵ノ器 | Storehouse Vessel | | | |
| 縛鍵 | Bind Key | | | Binding Key |
| 封鍵 | Seal Key | | | Sealing Key |
| 陰陽五行 | Yin-Yang and Five Elements | | | Yin-Yang Five Phases |
| 隠者の刻印 | Hermit's Mark | | | |
| 夜狩機構 | Yagari Agency | | | |
| 五光ノ獣 / 五光の獣 | Five Brights Beast | | | |
| 白札 | White Card | | | |
| 帝都防衛軍 | Imperial Defense Force | | | Capital Defenders |

## Decisions from earlier batches
- wave 0: full names from the EBOOT profiles: Ichiru Muto, Shu Takarakata, Gio Onimaru, Migiri Kashima, Kaname
  Kotokuji, Ayahito Konosu, Rin Himukai, Benio Sawakami, Asako / Seishiro Hatori, Daisuke Isachi, Nobuyuki Chikushi,
  Hisae Makimura, Gengo Shibukawa, Banri Takadono, Angie (Angela Dorothy Orphen), Kalpataru T. Shankar, Nagahide
  Shishido, Dokai Gamo (calls herself Mikamyun), Tomoe Tobisaka, Rei Chiaki, Toji Dan, Minori Hosaka; default hero
  Kazuki Shichidai.
- wave 0: pre-Meiji historical figures keep traditional order (Oda Nobunaga, Minamoto no Yoriyoshi); modern people
  Western order.
- wave 0: hanafuda card names are the systemtext list ("Pine and Crane", "Pine Poetry Ribbon", "Chrysanthemum Chaff
  I"); a shorter form only where a field can't hold it (listed in docs/fit-queue.tsv). 光札/種札/冊札/素札 Bright /
  Animal / Ribbon / Chaff cards; 屑 Chaff; 赤短/青短 Red/Blue Ribbon; あかよろし/みよしの Poetry Ribbon.
- wave 0: honorifics only after names; 敵さん "the enemy", オレ様 "the great me" (not "-san"/"Ore-sama").
- wave 0: ☆ -> `~`; button glyphs spelled (Triangle, Circle, Cross, Square); full-width ％ in a printf string -> `%%`.
