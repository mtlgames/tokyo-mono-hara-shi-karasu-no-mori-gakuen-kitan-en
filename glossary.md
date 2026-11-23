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
| 壇 | Dan | | Toji's surname | |
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
| 絢人 | Ayato | | | |
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
| ＯＲＤＳ / カミフダ | ORDS | | ruby カミフダ; organisation | |
| 隠者の杖 | Hermit's Staff | | | |
| 秘儀を伝授されし者 | Initiate | | ruby イニシエ | |

## Decisions from earlier batches
- (none yet)
