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
| 雉明 | Chiaki | | Zero Chiaki (雉明零; the game reads 零 ぜろ, so "Zero", not "Rei") | Rei |
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
| 武藤 | Muto | | Ichiru Muto | |
| 牧村 | Makimura | | Hisae Makimura (牧村先生 Makimura-sensei) | |
| 羽鳥 | Hatori | | Asako / Seishiro Hatori; 羽鳥家 Hatori Home (caption 羽鳥家居間 "Hatori Home, Living Room") | |
| 鹿島 | Kashima | | Migiri Kashima | |
| 香ノ巣 | Konosu | | Ayahito Konosu | |
| 鬼丸 | Onimaru | | Gio Onimaru | |
| 大督 | Daisuke | | ruby だいすけ; Daisuke Isachi | |
| 信維 | Nobuyuki | | Nobuyuki Chikushi | |
| 楼 | Takadono | | ruby たかどの; Banri Takadono | |
| 坂口 | Sakaguchi | | young detective (坂口巡査 Officer Sakaguchi) | |
| 要 | Kaname | | (not enforced) Kaname Kotokuji; 要 is also "need"/"key" (要らん) | |
| 清 | Sei | | (not enforced) Seishiro: Suzu's 清さま Sei-sama, Ken's 清さん Sei-san; 清める is "purify" | |
| 花 | Hana | | (not enforced) Togashi's given name (花さん Hana-san); otherwise "flower" | |
| 西園寺 | Saionji | | the house Rin's clan serves; 西園寺殿 Lord Saionji | |
| ミカ | Mika | | Kaname's name for Dokai (ミカちゃん Mika-chan) | |
| ミカみゅん | Mikamyun | | Dokai's self-name | |
| カナめん | Kanamen | | Dokai's nickname for Kaname | |
| ミギー | Miggy | | Angie's nickname for Migiri | |
| カル | Kal | | Kalpataru's nickname; カルさん Kal-san (his third-person self-reference) | |
| カモっち | Kamocchi | | Kalpataru's nickname for Hideo | |

## Places
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 鴉乃杜學園 / 鴉乃杜学園 | Karasu no Mori Academy / Karasu no Mori Acad. / Karasu Acad. | | the school; "Acad." only in dictionary:0039:04 (20b, fit-queue); "Karasu Acad." only in the city map list (97 px, fit-queue) | |
| 鴉乃杜 | Karasu no Mori | | | |
| 寇聖 | Kosei | | rival school (寇聖高校 Kosei High) | Kousei |
| 新宿 | Shinjuku | | | |
| 歌舞伎町 | Kabukicho | | | |
| 霞ヶ関 | Kasumigaseki | | | |
| 中央公園 | Central Park | | 新宿中央公園 Shinjuku Central Park | |
| 花園神社 | Hanazono Shrine / Hanazono | | "Hanazono" only in the city map list (97 px, fit-queue) | |
| 鴉羽神社 / 鴉羽 | Karasuba | | ruby からすば; 鴉羽神社 Karasuba Shrine | |
| 新宿署 | Shinjuku Police / Shinjuku PD | | Togashi's police station | |
| 国立国会図書館 / 国会図書館 | Diet Library | | National Diet Library ("Diet Library" in tight captions) | |
| 都庁 | City Hall | | (not enforced) Tokyo Metropolitan Government Building; 都庁ロボ Tocho Robo | |
| ドッグタグ | Dog Tag | | Shibukawa's Kabukicho cafe | |
| カレー桃源郷 | Curry Shangri-La | | Kalpataru's curry shop | |
| リグ・マサラヴェーダ | Rig Masala Veda | | Kalpataru's curry shop (sign name) | |
| イエス！サブリミナル | Yes! Subliminal | | toy shop | |
| 千枚葉湯 | Mille-Feuille | | ruby ミルフィーユ; the Mille-Feuille Bath (bathhouse) | |
| 五龍山 | Mount Goryu | | 五龍城 Goryu Castle | |
| 春の洞 | Spring Hollow / (Spring) | | "(Spring)" only as an enemy-name suffix | |
| 夏の洞 | Summer Hollow / (Summer) | | as above | |
| 秋の洞 | Autumn Hollow | | 大洞 great Hollow | |
| 冬の洞 | Winter Hollow / (Winter) | | as above | |
| 四季の洞 | Four Seasons Hollow | | | |
| 龍穴 | Dragon Lair | | 人工龍穴 Artificial Dragon Lair | |
| 生徒会 | student council / council | | 生徒会長 Student Council President | |
| 風紀委員 | disciplinary committee | | | |
| 司書室 | Librarian's Office / Librarian's Room / Librarian | | "Librarian" only in the school map room list (97 px panel, fit-queue) | |
| 進路指導室 | Guidance Office / Guidance | | "Guidance" only in the school map room list (fit-queue) | |
| 武道場 | Martial Arts Hall / Dojo | | "Dojo" only in the school map room list (fit-queue) | |
| 下駄箱 | shoe locker | | caption "Shoe Lockers" | |
| グラウンド | Athletic Field | | (not enforced) caption "Athletic Field--"; "field" in dialogue | |

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
| ＯＲＤＳ | ORDS | | ruby カミフダ; NOT an organisation: the information-bearing cards themselves ("what humans call ORDS", "ORDS latch onto living things"); no article needed | |
| カミフダ | ORDS / cards | | (not enforced) the ORDS cards (above) or, in card-game text, the paper cards themselves ("cards") | |
| 隠者の杖 | Hermit's Staff | | | |
| 秘儀を伝授されし者 | Initiate | | ruby イニシエ | |
| 体力 | Stamina | | stat | Vitality |
| 瞬発力 | Reflexes | | stat | |
| 精神力 | Willpower | | stat | Spirit |
| 脚力 | Speed | | stat | Footwork |
| 判断力 | Judgment | | stat | |
| 外国語 | Languages | | school subject | Foreign Language |
| 現代社会 | Social Studies / Soc.St / Social St. | | school subject; "Soc.St" only in item:0326-0328:10 stat lines (24b, fit-queue); "Social St." = systemtext:0070 (status page subject cell, 56 px) | Modern Society |
| 麻痺 | Paralysis | | ailment | Paralyze |
| 悪寒 | Chills | | ailment | |
| 札強化 | Card Enhance / Enhance | | | Card Boost |
| 調合 | Mix | | | Combine |
| 依頼 | Quest | | (not enforced) quest board; 依頼人 Client | |
| 特別依頼 | Bonus Quest | | | Special Quest / Special Job |
| 八汎學院 / 八汎学院 | Yahiro Academy / Yahiro Acad. | | ruby 八汎|やひろ; "Yahiro Acad." only in the city map list (fit-queue) | Happan / Yahiro Institute |
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
| 陰陽五行 | Yin-Yang and Five Elements / Yin-Yang 5 Elements | | "5" only in dictionary:0018:04 (20b, fit-queue) | Yin-Yang Five Phases |
| 隠者の刻印 | Hermit's Mark | | | |
| 夜狩機構 | Yagari Agency | | | |
| 五光ノ獣 / 五光の獣 | Five Brights Beast | | | |
| 白札 | White Card | | | |
| 帝都防衛軍 | Imperial Defense Force / Imperial Def. | | "Def." only in questclnt:0009:00, questrewarditem:0036:00 (18b, fit-queue) | Capital Defenders |
| 帝都 | Imperial Capital | | (not enforced) short table text may say "capital" | |
| 氣 | ki | | (not enforced) capital Ki in 《氣》; prose may say "energy"/"spirit"; not "Qi" | |
| 勁術 | Keijutsu | | ruby けいじゅつ | |
| 大いなる遺志 | Great Will | | | |
| 極めし者 | Adept | | ruby アデプト | |
| 虚空蔵 | Akashic Record | | ruby アカシックレコード | |
| 鳳凰 | Phoenix / Phnx | | the Paulownia Bright card; "Phnx" only in hanafuda:0047:04 (14b, fit-queue) | |
| 人札 | Man Card | | | |
| 特課試札 | Division Trial Card / Trial Card | | | |
| 人龍計画 | Human Dragon Project | | | |
| 分龍 | Branch Dragon | | (not enforced) prose: "a branch of the dragon vein" | |
| 特務課 / 収集部特務課 / 国立国会図書館収集部特務課 | Special Duties Division / Collection Division | | National Diet Library Collection Department, Special Duties Division (Isachi's unit); dictionary title "Collection Division" | |
| 内閣緊急事態管理室 | Cabinet Emergency Management Office / JEMA | | | |
| ＪＥＭＡ | JEMA | | | |
| 特別機動捜査隊 | Special Mobile Investigation Unit | | 機捜隊 mobile investigation unit | |
| 総括官補佐 / 総括参事官補佐 / 筑紫総括官補佐 / 統括官補佐 | Assistant Director-General | | Chikushi's JEMA title | |
| 少年課 | Juvenile | | Juvenile Division (police) | |
| 宮内庁 | Imperial Household Agency | | | |
| 富樫刑事 | Detective Togashi | | | |
| 盗賊王 | Bandit King | | Gio | |
| オカシラ | Boss | | the Bandits' (and Angie's) name for Gio | |
| 黒き札 | Black Card | | | |
| 神札 | Divine Card | | old name for ORDS | |
| 隠札 | Hidden Card | | old name for ORDS | |
| 太陽の石 | Sun Stone | | | |
| 札憑きの印 | Mark of the Card-Possessed | | | |
| 情報の断片 | fragment | | Information Fragments in 《》 | |
| 東京ＢＭ | Tokyo BM | | masked hero / hero show | |
| 夜刀神 / 夜刀 | Yatogami / Yato | | serpent god; 夜刀さん Lord Yato | |
| 仔犬 | pup | | Ken's 仔犬ちゃん for Suzu: "the little pup" (no -chan) | |
| 白殿 | Lady Mao | | Ken's address for Mao (殿 -> Lord/Lady) | |
| 白札の君 | Lady of the White Card | | | |
| 竜胆の君 | Gentian Prince | | Dokai's beloved | |
| 相棒 | partner | | Toji's word for the hero | |
| ぬしさま | Master | | Suzu's address for the hero | |
| お嬢 | young miss | | (not enforced) Ken, of Asako: "the young miss" | |
| 居候 | freeloader | | (not enforced) Togashi/Seishiro on the hero; "lodger" in neutral lines | |
| 四角 | square / squarish / squaaare | | Shu's catchword, kept literal | |
| 押忍 | Osu | | | |
| 情報屋 | info broker / information broker / informant | | | |
| 旋火流 / 旋火 | Senka | | Senka-ryu, Rin's ninja school (旋火流忍法 Senka-ryu Ninja Art), not "Senkaryu" | |
| 忍法 | Ninja Art / Ninja | | | |
| 大散華 | Big Bang | | ruby ビックバン | |
| 英雄拳 | Hero Knuckle | | ruby ヒーロー・ナックル | |
| 陰陽師 | onmyoji | | | |
| 式神 | shikigami | | (not enforced) "familiar" in short quest text | |
| 賀茂 | Kamo | | | |
| 天神玉命 | Amanokamutama | | | |
| 七不思議 / 學園七不思議 | Seven Mysteries | | | |
| 黒服 | men in black / man in black | | | |
| 狛犬 | komainu / guardian dog / lion-dog | | | |
| 覆面の男 | masked man | | | |
| 加哩魔神 | Asura Curry | | | |
| 仲間スキル | Partner Skill | | systemtext "Partner Skill(s)"; 仲間 = partner in menus | Ally Skill |

## Graphics labels (phase 8 redraws; generators tools/gfx_*.py)
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 初めから / 続きから | New Game / Continue | | (not enforced) title + save/load | |
| 鴉乃杜學園奇譚 | Strange Tales of Karasu no Mori Academy | | (not enforced) title subtitle | |
| 喜 友 嫌 困 愛 燃 怒 悲 | Joy, Friend, Dislike, Worry, Love, Passion, Anger, Sorrow | | (not enforced) emotion input (adv_emotion); the wheel itself shows 燃 "Fire" and 悲 "Sad" (middle row, 24 px apart); quest_site 658 wheel uses 3x5 caps LOVE JOY HATE RAGE SAD UPSET PAL FIRE (polish: align) | |
| 次へ 速度 自動 | Next, Speed, Auto | | (not enforced) ADV buttons | |
| 探索中 | Exploring | | (not enforced)  | |
| 呼出中 / 通話中 / 通話 / 拒否 | Calling... / In Call... / Answer / Decline | | (not enforced) phone | |
| 依頼人 / プレイヤー | Client / Player | | (not enforced) phone | |
| プロフィール帳 / クエストの確認 / 携帯設定 / プロフィール入力 | Profile Book / Check Quests / Phone Settings / Enter Profile | | (not enforced) phone menu | |
| 用語辞典 / 解説 | Glossary / Guide | | (not enforced) OXAS site | |
| 解罠 | Disarm | | (not enforced)  | |
| 依頼達成！ | QUEST COMPLETE! | | (not enforced)  | |
| 迎撃 / ターン終了 / 手番 | Counter / End Turn / Turn | | (not enforced) battle UI | |
| 花札配置 | Place Cards | | (not enforced)  | |
| 切替 / 秘法眼 | Switch / Arcane Eye | | (not enforced)  | |
| 風呪 炎呪 土呪 氷呪 | Wind / Fire / Earth / Ice Curse | | (not enforced)  | |
| 成績表 / 学科値 / 能力値 | Report Card / Subject / Attribute | | (not enforced)  | |
| 模擬演習場 | Drill Ground | | (not enforced) dungeonareainfo name | |
| 地上へ / 第N階層へ | To Surface / To NF | | (not enforced) map_view | |
| 雑貨 / 購買 / 玩具屋 | Sundries / School Store / Toy Store | | (not enforced) shop signs | |
| 入手 / 入替 / 貴重品 / 探索準備 / 札強化 | Obtain / Swap / Key Items / Explore Prep / Enhance | | (not enforced) menus | |
| バディ | Buddy | | (not enforced)  | |

## Decisions from earlier batches
- wave 0: full names from the EBOOT profiles: Ichiru Muto, Shu Takarakata, Gio Onimaru, Migiri Kashima, Kaname
  Kotokuji, Ayahito Konosu, Rin Himukai, Benio Sawakami, Asako / Seishiro Hatori, Daisuke Isachi, Nobuyuki Chikushi,
  Hisae Makimura, Gengo Shibukawa, Banri Takadono, Angie (Angela Dorothy Orphen), Kalpataru T. Shankar, Nagahide
  Shishido, Dokai Gamo (calls herself Mikamyun), Tomoe Tobisaka, Zero Chiaki (wave 1: 零 is read ぜろ in ms00_01/ms11_00 and the profile), Toji Dan, Minori Hosaka; default hero
  Kazuki Shichidai.
- wave 0: pre-Meiji historical figures keep traditional order (Oda Nobunaga, Minamoto no Yoriyoshi); modern people
  Western order.
- wave 0: hanafuda card names are the systemtext list ("Pine and Crane", "Pine Poetry Ribbon", "Chrysanthemum Chaff
  I"); a shorter form only where a field can't hold it (listed in docs/fit-queue.tsv). 光札/種札/冊札/素札 Bright /
  Animal / Ribbon / Chaff cards; 屑 Chaff; 赤短/青短 Red/Blue Ribbon; あかよろし/みよしの Poetry Ribbon.
  Short form (only where the full name can't fit; every such line in docs/fit-queue.tsv): drop "and", then
  "Chaff" / "Ribbon" / "Maker's", in that order ("Cherry Curtain", "Wisteria I", "Peony Blue", "Paulownia Mark",
  "Cherry Poetry"); the flower is always spelled out (Chrysanthemum, never "Mum": British readers read it as mother).
- wave 0: honorifics only after names; 敵さん "the enemy", オレ様 "the great me" (not "-san"/"Ore-sama").
- wave 0: ☆ -> `~`; button glyphs spelled (Triangle, Circle, Cross, Square); full-width ％ in a printf string -> `%%`.
- review fixes: item stat lines use the b045 format "Stat +N  Stat -N" (two spaces between pairs); weapon ailment
  lines 攻撃した敵をN％の確率でX状態にする -> "Inflicts <ailment> (N%)." with systemtext ailment names.
