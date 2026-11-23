# Translator reports (wave 0), to merge into glossary.md and check in game

## b070-b073 (systemtext, tokkidata tail)
- NEW TERMS: 屑 Chaff (壱/弐 -> I/II); 赤短 Red Ribbon, 青短 Blue Ribbon, あかよろし/みよしの Poetry Ribbon; 萩 Clover,
  芒 Pampas, 桐 Paulownia, 紅葉 Maple, 菖蒲 Iris, 牡丹 Peony; 特課 Division, 特課札 Division card, 特課試札 Division Trial
  Card; 札憑き card-bearer; 携行 pack; 強化 enhance; 調合 Mix; 研究会 Society, 同好会 Circle, 帰宅部 Go-Home Club;
  封呪/風呪/炎呪/土呪/氷呪 Seal/Wind/Fire/Earth/Ice Curse; 神 (attribute) Divine; 退魔札 exorcism talismans;
  八汎學院 Yahiro Institute; 寇聖高校 Kosei High; OXAS Japan Branch.
- Full names (from furigana): Ichiru Muto, Shu Takarakata, Gio Onimaru, Migiri Kashima, Kaname Kotokuji (guess),
  Ayato Konosu, Rin Himukai, Benio Sawakami, Asako/Seishiro Hatori, Daisuke Isachi, Nobuyuki Chikushi, Hisae
  Makimura, Gengo Shibukawa, Banri Takadono, Angie D.
- QA in game (phase 7/8): systemtext 0168-0171 runtime-joined fragments around item names; 0496-0508 `%%` for JP
  full-width ％ (only right if sprintf formats it); 0039/0040 alignment spaces dropped; 0236-0244 button glyphs
  spelled out; 0129 個 -> "pcs".

## b016-b020 (buddymes)
- NEW: ミカみゅん Mikamyun; 春の洞 Spring Hollow; 怨霊 vengeful spirit; ぬしさま (Suzu) Master; 坊 young master;
  仔犬ちゃん Puppy-chan; 山伏 yamabushi; 勧進帳 Kanjincho; 古墳 burial mound. ☆ -> "~". buddymes has no speaker
  column (voice guessed from markers): reviewer should check voices per partner.
- Checker fixed: honorific only after a glossary name/{p*}; 壇 and カミフダ not enforced (カミフダ = cards in card text).

## b041-b045 (help, item, inputproftext...)
- NEW: 封札システム Sealing System; 封具ノ器 Sealing Vessel; 御蔵ノ器 Storehouse Vessel; 札強化 Card Boost (vs b070
  "enhance": reconcile); 成績表 Report Card; 能力値 attributes: 体力 Stamina, 瞬発力 Reflexes, 精神力 Willpower, 脚力
  Footwork, 判断力 Judgment; 学科値 subjects: 国語 Japanese, 数学 Math, 外国語 Foreign Language, 体育 P.E., 現代社会
  Modern Society, 保健 Health, 生物 Biology; 属性 element; 麻痺 Paralyze, 目潰し Blind, 睡眠 Sleep, 悪寒 Chill, 骨折
  Fracture; 探索準備 expedition prep; 自室 your room; 生徒会特務部 Student Council Special Duties; 鬼印盗賊団 Oni-Mark
  Thieves; 用語辞典 Glossary; 隠人データベース Oni Database.
- Fit pass: item:0056/0077 sword names cut to 16b (Daihannya, Dojigiri), item:0044 "Sharp Pencil"; inputproftext
  0005/0014/0020 have literal `\n` breaks in JP (game expands them) but were written as one line: re-split.
- Checker fixed: printf space flag dropped ("40% of" is prose); literal `\n` allowed where the JP has it.

## b046-b050 (item, itemmix)
- CONFLICTS with b041-b045 (decide, then fix the losers): 体力 Vitality/Stamina, 精神力 Spirit/Willpower, 脚力
  Speed/Footwork, 外国語 Languages/Foreign Language, 現代社会 Society/Modern Society (24b), 麻痺 Paralysis/Paralyze,
  悪寒 Chills/Chill, 札強化 Card Boost/enhance.
- NEW: 防御力 Defense; 攻撃力 Attack; 消費AP AP Cost; 頭痛 Headache; 吐き気 Nausea; 捻挫 Sprain; 執行者 Executor;
  白札 White Card; 蛍草 Dayflower; うまい棒 Umaibo; 東京BM Tokyo BM; ザコ敵 small fry; マス square; 源家八領 the Genji's
  Eight Armors; 春/夏/秋/冬属性 Spring/Summer/Autumn/Winter-type.
- itemmix itm_ ids copied verbatim (resource ids?). item:0339:0c "No description shown" (dev placeholder?).

## b026-b030 (dictionary) and b056-b060 (obj, playerquestsent, questclnt)
- CONFLICTS: 八汎學院 Happan Academy vs Yahiro Institute (ruby 八汎|やひろ -> Yahiro); 特課 the Unit vs Division;
  札憑き Card-Possessed vs card-bearer; 龍珠堂 Ryujudo vs Dragon Orb Hall; フリガナ Pronunciation vs Reading.
- NEW: 収集部特務課 Special Affairs Unit; 鬼札 Demon Card; 人龍計画 Human Dragon Project; 龍穴 dragon lair; 四季の洞
  Four Seasons Hollows; 陰陽五行 Yin-Yang and Five Elements; 氣 ki; 賀茂氏 Kamo clan; 隠者の刻印 Hermit's Mark;
  封札師認定試験 Card Sealer Certification Exam; ヘルメスサイト Hermes Sight; カードアーカイバー Card Archiver; ＪＥＭＡ JEMA;
  ドッグタグ Dog Tag (cafe); 旋火流 Senka-ryu; 風魔一族 Fuma clan; 光札/種札/冊札/素札 Bright/Animal/Ribbon/Chaff Cards;
  封念ノ神鏡 Sealing Mirror; 縛鍵 Binding Key; 封鍵 Sealing Key; 壇 (object) Altar. Historical names given-first.
- Fit pass: dictionary:0058:04 "Diet Library" (20b), 0150:04 Mikkyo, 0103:04, 0124:10 month abbrevs (rule D4!).
  questclnt:0002:00 "American Hacker" (18b). Dictionary sort order is kana-based: check in game.
- objhaichi = placement bytes, not text: batches.NON_TEXT_TABLES skips it (extractor/test should waive it too).

## b051-b055 (itemmix, mail, obj)
- Full names: 武藤いちる Ichiru Muto; 雉明零 Rei Chiaki; 飛坂巴 Tomoe Tobisaka; 鬼丸義王 Gio Onimaru; 鹿島御霧 Migiri
  Kashima; 香ノ巣絢人 Ayato Konosu; 日向輪 Rin Hyuga (CONFLICT Himukai); 幸徳路要 Kaname Kotokuji; アンジー・Ｄ Angie D.;
  宍戸長英 Nagahide Shishido; 蒲生道佳 Dokai Gamo (= ミカみゅん); 宝方蒐 Shu Hoho? (CONFLICT Takarakata); 佐波守紅緒
  Benio Sabamori? (CONFLICT Sawakami); 伊佐地大督 Daisuke Isachi (guess).
- CONFLICTS: 龍珠堂 Ryushudo / Ryujudo / Dragon Orb Hall; 封念ノ神鏡 Thought-Sealing Mirror vs Sealing Mirror;
  封具ノ器 Sealed Tool Vessel vs Sealing Vessel; 八汎學院 Happan (again; ruby says Yahiro).
- NEW: 収集特課 Special Section (ＮＤＬ収特課 NDL Special Section); 鴉羽神社 Karasuba Shrine; 英雄同好会 Hero Club;
  正義通信 Justice Report; 龍気 dragon qi; 陣形 formation; 鬼道 Ghost Way.
- In game: mail ASCII art (Shu's # boxes, rose with @ and `), blank lines; mail:0081:08 tightened to 904b.

## b001-b005 (speakers, EBOOT)
- 絢人 = Ayahito (ruby あやひと; glossary was wrong): fix "Ayato" in b001 b005 b053 (+ any later) in the term pass.
- Profile surnames: Muto, Hatori, Takarakata, Onimaru, Kashima, Kotokuji, Konosu, Himukai, Sawakami, Angela D. Orphen
  (Angie), Olga Kresnik. eboot:2b5704..2b5978 unread names guessed (Tsugio Yasuda ... Tenzen Ubayama).
- NEW: 式神 shikigami; 四角研究会 Square Research Club; 依頼 Quest (CONFLICT b066 "request"); 盗賊団員 Bandit;
  男子生徒/女生徒 Schoolboy/Schoolgirl; 調合 Combine (CONFLICT Mix); 携行アイテム Carried Items.
- In game: runtime-joined EBOOT fragments with leading spaces (2b419c 2b41a4 2b54b8 2b54bc 2b54cc; merge now keeps
  spaces); `%%` for ％ (2b4410 2b51a4 2b51ec 2b51fc); button glyphs as words (2b1538-2b1578); lone-space JP now
  skipped as non-text. Title: "Tokyo Mono Hara Shi: Strange Tales of Karasu no Mori Academy".

## b021-b025 (buddymes tail, dictionary, clct*)
- RULING needed (my default): pre-Meiji historical figures in traditional order (Oda Nobunaga, Minamoto no
  Yoriyoshi), as English histories write them; b026-b030 used Western order -> fix those in the term pass.
- CONFLICTS: 鬼印盗賊団 Demon Mark Bandits vs Oni-Mark Thieves; 陰陽五行 Yin-Yang Five Phases vs ...and Five Elements;
  dictionary :08 reading lines lowercase (b021) vs capitalised (b026).
- NEW: OXAS = "Oopards eXploration and Archives Squad"; ORDS = "Out of place caRDS"; 羽鳥清司郎 Seishiro Hatori;
  勘解由小路 Kadenokoji; 都庁 Metropolitan Government Building ("Tokyo City Hall" in 16b).
- b025 fails: dictionary:0039:04 "Karasu no Mori Academy" 22b in a 20b slot (fit pass / slot measure).
- buddymes:1481-1483 "Enemy-san" written only to pass the old checker (敵さん = "the enemy"): retranslate.

## b006-b010 (EBOOT profiles/labels, buddymes head)
- insert.NON_TEXT now also covers EBOOT 2b79a8-2b7b54 and 2b7e28-2b7ed8 (glyph/kinsoku/name-markup tables).
- 零 reading in EBOOT is ぜろ: "Zero"? vs Rei Chiaki (ruby 雉明|ちあき, 零|ぜろ only 2x): decide (default Rei).
- NEW: 七代千馗 Kazuki Shichidai; 牧村 Makimura; 信維 Nobuyuki; 花子 Hanako; 源伍 Gengo; アンジェラ・ドロシー・オルフェン
  Angela Dorothy Orphen; カルパタル・Ｔ・シャンカル Kalpataru T. Shankar; 五光の獣 Five Brights Beast; 帝都防衛軍
  Imperial Defense Force; 購買 School Store; 校内放送 Intercom; 恐山のイタコ Mt. Osore Medium; 盗賊団員 Thief Gang
  Member (CONFLICT Bandit).
- In game: EBOOT profile blurbs 2b5ac4..2b5ebc hand-broken at ~31 chars x 4 lines; nickname templates
  2d3a10..2d445c keep raw pn/pm/pnyh codes (check expansion); eboot:2b6b88 炯治 = Toji?

## b011-b015 (buddymes)
- CONFLICTS: 執行者 Enforcer vs Executor; 日向輪 Rin Hinata vs Himukai/Hyuga (profile reading ひむかい -> Himukai).
- Forced by the old checker, retranslate: オレ様 "Ore-sama" (0227-0237, 0681; better "the great me"), 弁天様
  Benten-sama (0285:18, fine), ワイルドさん "Wild-san" (0328:18).
- NEW: 鬼印 Oni Mark; 忍法 Ninja Art; 兄さま Nii-sama; 甲骨文字 oracle bone script; 陰陽霊符 Onmyo talismans.

## b036-b040 (enemy, enemydb, exitem, hanafuda)
- LONG (51 lines): hanafuda:*:04 card names in a 14b column (e.g. "Chrysanthemum and Sake Cup"), hanafuda:*:08 7b
  season/type ("Winter Chaff"), enemy:0124:04 / 0136:04 21b vs 20b. Engine/buffer measure in phase 7.
- NEW: 三乗ノ王 Cubed King; 分ケ身 Clone; 春秋ノ連 Spring-Autumn Link; 冬夏ノ理 Winter-Summer Law; 大隠人 Great Oni;
  甲型/乙型 Type-A/Type-B; 元型遠呂智零號 Archetype Orochi No. 0; ＯＲＤＳ封印体 Sealed ORDS; 収集特課 Collection
  Division (CONFLICT Special Section); 血色の魔女 Blood-Red Witch; 鬼の百合若 Yuriwaka the Demon; 縛鍵/封鍵 Bind/Seal Key
  (16b); boss names 加籃 Karan, 皀莢 Saikachi ... 金雀児 Enishida; subject-disable "No P.E." etc.
- In game: b040 stat lines rely on runs of spaces for alignment.

## b031-b035 (enemy, dictionary, dungeon*)
- LONG: dungeondoorexplain:0000:04 扉 2b limit ("Door").
- CONFLICTS: 八汎學院 Yahiro Academy; 龍珠堂 Ryuzudo (4th spelling!); hanafuda short forms ("Pine Poem", "Mum Cup",
  "Demon Drum") vs b036-b040 long systemtext names; 鬼印盗賊団 Oni Mark Bandits.
- NEW: 夜狩機構 Yagari Agency; リグ・マサラヴェーダ Rig Masala Veda; ノ式 Rite; 迎撃 Counter; 魅了 Charm; 浸食 erosion;
  白面 Hakumen; skills 表裏 Heads or Tails, 空蝉の術 Cicada Husk, ミラクル★ラブ Miracle Love, 英雄大解砲 Hero Cannon.
  enemy plant-name readings guessed (enemy:0003-0056).

## b066-b069 (quest words)
- NEW: 龍珠堂 Dragon Orb Hall; 種札/屑札 Animal/Chaff; 短冊 ribbon; 依頼 request, 依頼人 client; 情報料 info fee;
  儀 Rite; 退魔 Exorcism; 学科値 school stat; 愛情/友情 affection/friendship; 特別依頼 "Bonus Quest N" (16b).
- Squeezed to byte caps (flag for engine/fit pass): questwordplace 14b names, questwordpkill 12b rite names.
