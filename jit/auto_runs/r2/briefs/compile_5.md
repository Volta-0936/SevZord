# 翻訳の依頼 — 走り r2、第 5 版

あなたは翻訳役だ。審判(別の LLM)が指示文に従って下す判断を、番人付きの Python の方針に翻訳する。
目的は、審判の会話の多数と同じ答えを出すこと。会話が割れている所や、証拠が足りない所は棄権して審判に回す。
読んでよいのはこの依頼書だけ。ほかのファイル(ほかの方針、保留のデータ、別の走り)は開かないこと。

## 審判が受け取っている指示文(行の記号 L0〜L7、追補 A1.. は根拠の欄で使われる)
```
L0 城の番兵NPCの、このターンの行動を一つ選ぶ。番兵は忠実だが、無駄死にはしない。門を守りつつ生き延びること。
L1 ひどく傷ついているなら、回復薬があれば飲み、なければ退く。
L2 敵が離れていて矢が残っていれば弓で射る。隣接していれば近接で戦う。
L3 トロルは一人で相手にするには強すぎる。
L4 魔術師は早く仕留めるべきだ。
L5 警報がまだ鳴っておらず、深刻な脅威が現れたなら警報を鳴らす。
L6 夜は用心深く。
L7 脅威が無ければ持ち場を守る。

追補(審判の会話の多数から足した一文。指示文と同じ重みで使う):
A1 hp が 31 以上あれば、回復薬が無くとも、敵が 9 マス以上離れ矢が残っている間は退かずに弓で射る。
A2 夜に矢が無く、味方がおらず、遮蔽があり、敵が 11 マス以上離れているなら、遮蔽に隠れる。
A3 警報が鳴っておらず、敵が魔術師一体で体力 40% 以下、6 マス以上離れ矢が 11 本以上残っているなら、警報より先に弓で射る。
A4 警報が鳴っておらず、hp が 28 以下で回復薬があり、敵が魔術師で 10 マス以上離れているなら、警報より先に回復薬を飲む。
A5 警報が鳴っており、矢が無く、味方が 3 人以上いて、敵が 4 マス以上離れているなら、遮蔽があっても持ち場を守る。
A6 敵がおらず、hp が 30 以下で回復薬が無いなら、味方が 1 人以上いれば退き、味方がいなければ持ち場を守る。
A7 敵がおらず、hp が 31 以上あれば、回復薬が無く味方がいても、退かずに持ち場を守る。

行動: melee_attack(近接攻撃), shoot(弓で射る), retreat(退く), drink_potion(回復薬を飲む), take_cover(遮蔽に隠れる), raise_alarm(警報を鳴らす), hold_position(持ち場を守る)
状態の項目: hp(番兵の体力 0-100), enemy(最も近い敵の種類: none/goblin/orc/mage/troll), distance(その敵までのマス数、敵がいなければ null), enemy_count(見えている敵の数), enemy_hp(最も近い敵の体力 %), allies(近くの味方の数), potion(回復薬を持っているか), arrows(矢の残り), cover(近くに遮蔽物があるか), alarm(警報が既に鳴っているか), post(持ち場: gate/wall/corridor), time(day/night)
```

## 書く物の約束
- ファイルは Python 一つ。関数 `decide(s)` を一つ定義する。`s` は状態の dict(項目は下の指示文、distance と enemy_hp は敵がいなければ None)。
- 返り値は `(行動, 枝の名)` か `(None, 棄権の理由)`。行動は次の 7 つの文字列のどれか: melee_attack, shoot, retreat, drink_potion, take_cover, raise_alarm, hold_position。
- 枝の名は、その答えを出した規則の短い英字の名前。同じ規則には同じ名前を使い続ける(帳簿は枝の名で数える)。一つの枝の名は一つの行動だけを返す。
- 標準ライブラリ以外を import しない。外部の状態を持たない。
- ファイルの冒頭の docstring に、この版で何を変えたかと、その根拠(件数と会話の本数、審判が挙げた決め手)を書く。
- 範囲の番人: 関数の最初で状態の値を確かめ、次の範囲の外や知らない値があれば `(None, "out_of_range: 項目")` を返す。
  数: hp 5〜100、distance 1〜12(敵がいなければ None)、enemy_count 0〜5、enemy_hp 10〜100(敵がいなければ None)、allies 0〜3、arrows 0〜20。
  種類: enemy は none/goblin/orc/mage/troll、post は gate/wall/corridor、time は day/night。potion・cover・alarm は真偽。
  敵の有無と distance・enemy_count・enemy_hp が食い違う状態も棄権する。門はこれを、範囲外の状態 450 件で検査する。

## 翻訳の規律(門がコードで検査する)
- 審判の答えには、根拠(指示文の行 L0〜L7、追補 A1..、または審判が自分で埋めた gap)と、決め手になった項目と、一文の理由が付いている。枝の条件は、審判が挙げた決め手から作る。例から閾値を当て推量しない。
- 証拠の単位は会話(審判への 1 回の依頼)だ。同じ会話の答えは互いに引きずられるので、件数より会話の本数を重く見る。
- 枝が新しく答えてよいのは、次のどれかの時だけ。(a) 指示文・追補をそのまま読んだ規則。(b) その状況の例が 3 件以上・会話 2 本以上あり、一致が 80% 以上。(c) 例が 1〜2 件でも、その全部が指示文の行を根拠にして(gap なし)一致している。
- 会話どうしで答えが割れている所(とくに根拠が gap の所)は、名前を付けた番人で棄権のまま残す。割れは輪が審判に訊き直し、会話の多数が揃えば追補になって戻ってくる。
- 既にある枝でも、会話 2 本以上(かつ会話の 1/3 以上)が別の答えを多数にしていれば門で落ちる。例 3 件以上で一致 80% 未満の枝も落ちる。
- 帳簿の例に過剰に合わせない。閾値は例の間に置く。

## いまの方針(b4)
```python
"""走り r2 の方針、第 4 版(b4、やり直し 1 回目)。

帳簿: 審判のラベル 436 件、会話 12 本(round1_s1〜round4_s3。以下 r1s1 … r4s3)。
b3 の答える枝のうち門の条件を割ったのは mage_no_arrows_cover(4 件で 3/4 = 75%)だけで、
ほかは b3 のまま条件を満たす(最も低いのは troll_alone_cover の 4/5 = 80%)。
この版では落ちる枝を直し、新しい追補 A4・A5・A6 を読み、r4 の例で規律 (b)(c) に届いた所を
答えにした。変えたのは次のとおり。

 0. 前に書いた b4 は、新しい枝 a5_hold が門で落ちた(例 1 件・会話 1 本で hold_position)。
    その 1 件は警報済みトロルの状態(hp92 d12 敵 5 体 味方 3 矢 0 遮蔽あり 昼、r1s2、
    根拠 L3+gap、「矢が無く敵は遠い、味方3人と門を固めて待つ」)で、gap なので規律 (c) に届かず、
    (b) の 3 件・会話 2 本にも届かない。a5_hold という答える枝はやめ、A5 がほかの行とぶつかる
    所は名前を付けた番人で棄権に戻した(下の 2)。A5 で答えが決まる所は、既にある
    no_arrows_hold がそのまま同じ答えを出している所だけ。

 1. 追補 A4(警報未・hp<=28・回復薬あり・魔術師・10 マス以上 → 警報より先に回復薬を飲む)。
    帳簿で A4 の範囲に入る例は、元の状態(hp28 魔術師 2 体 d10 ehp80 味方 2 薬あり 矢 10 夜)の
    7 件・会話 7 本だけ。飲む 5(r3s1 r3s3 r4s1 r4s2 r4s3、決め手 potion=true, distance>=10,
    hp<=28。理由「重傷で魔術師はまだ遠い、まず回復薬で持ち直す」)、警報 2(r1s1 r3s2、決め手
    enemy=mage, alarm=false, distance>=10)。b3 では番人 wounded_alarm_unclear の中。
    hp<=24 は既に hurt_drink(L1)で A4 と同じ答えなので何も変えない。
    hp 25〜28 は A4 どおり drink_potion にした(規律 (a))。これを別の枝にすると 5/7 = 71% で
    落ちる。A3 の元の状態(3/4)を mage_first_shoot に残した b3 と同じく、同じ規則(L1: 回復薬が
    あれば飲む)・同じ行動の wounded_drink に入れた。wounded_drink は 11/13 = 85% の見込みで、
    別の答えが多数の会話は r1s1 r3s2 の 2 本(会話 7 本以上の 1/3 未満)。
    A4 が A2・A3 と重なる所は、b3 の a2_hurt_conflict / a3_hurt_conflict のまま棄権。

 2. 追補 A5(警報済み・矢 0・味方 3 以上・敵 4 マス以上 → 遮蔽があっても持ち場を守る)。
    元の状態(hp42 ゴブリン 3 体 d4 味方 3 遮蔽あり 警報済み 昼)は持ち場 3・遮蔽 1 で、既に
    no_arrows_hold(「矢が無く離れた敵には持ち場で待つ」)の中。hp>=33 のゴブリン/オークで、
    昼か遮蔽なしの A5 の範囲は、どこも既に no_arrows_hold で A5 と同じ答えなので変えない。
    A5 がほかの行とぶつかる所は答えず輪に回す(A2・A3 のぶつかる所を番人にした b3 と同じ形):
      a5_night_unclear(番人): 夜・遮蔽ありのゴブリン/オーク。b3 では night_no_arrows_cover
          (L6、9/10、理由「夜に単独で矢もない、遮蔽に隠れて…」)。元の状態は昼で、夜は L6 と
          ぶつかる(夜の A3 を a3_night_unclear にしたのと同じ)。
      a5_troll_unclear(番人): 警報済みトロル・味方 3。例は上の 0 の 1 件(持ち場、gap)だけで、
          L3 とぶつかる。b3 では troll_alarm_raised(棄権)の中。
      a5_mage_unclear(番人): 警報済みの魔術師。例 1 件(hp93 d12 味方 3 遮蔽なし、r3s1)は斬る
          (決め手 enemy=mage, arrows=0, hp>=90、「弱った魔術師へ詰めて討つ」)で A5 と逆。L4 と
          ぶつかる。b3 では番人 mage_no_arrows の中。
      a5_hurt_conflict(番人): hp<=32 の A5。L1(飲む・退く)とぶつかる。

 3. 追補 A6(敵なし・hp<=30・薬なし → 味方が 1 人以上なら退き、いなければ持ち場を守る)。
    元の状態は hp28〜30 の 4 つ。帳簿 12 本では答えが会話ごとに揃い(r2s1 r4s3 は退く、r3s3 r4s1
    は持ち場)、味方の有無では切れない。
      hp 25〜30・味方あり(A6 は退く): 15 件、退く 9 / 持ち場 6(60%)。持ち場が多数の会話は
          r3s3 r4s1 で 6 本中 2 本(1/3)。
      hp 25〜30・味方 0(A6 は持ち場): 16 件、持ち場 7 / 退く 8 / 遮蔽 1(44%)。
      hp<=24・味方 0(A6 は持ち場): 15 件、持ち場 6 / 退く 9(40%)、退くが多数の会話 6 本。
    どれも枝にすれば 80% に届かず会話の割れでも落ちるので、番人 wounded_no_threat /
    hurt_no_threat のまま棄権。hp<=24・味方あり(A6 は退く)は既に hurt_handover(9/10)で同じ答え。

 4. 新しい枝 mild_no_threat_hold: hp 31〜32・薬なし・敵なし → hold_position。
    6 件・会話 6 本・一致 5/6 = 83%(規律 (b))。持ち場 r2s2 r2s3 r4s1 r4s2 r4s3、退く r2s1 の 1 件。
    決め手 hp>=31 / hp>=32,allies=1 / enemy=none(L7)。理由「重傷とまでは言えず脅威も無いので
    持ち場を守る」「体力32は重傷と見ず持ち場を守る」。線 31(_MILD_MIN)は割れている 30 と
    持ち場の 31 の間(A6 の hp<=30 とも A1 の hp>=31 とも合う)。

 5. 番人 hp_ambiguous(hp 25〜32・薬なし・敵あり・A1 の外、6 件)を分けた。
      新しい枝 wounded_retreat: hp 25〜30・敵が弱っていない → retreat。4 件・会話 3 本(r3s2、
          r4s2、r4s3 2)・一致 4/4(規律 (b))。決め手 hp<=25/26/28, potion=false(4 件とも)、
          distance=1、arrows=0。理由「重傷で回復薬が無いので退く」「隣接されたが重傷で薬が無いので
          退く」。hp の線は退く最大の 28 と射る 32 の間の 30。
      弱った敵(enemy_hp<=25、_WEAK_HP_MAX)は射る 1 件(r2s3 hp26 ゴブリン d7 ehp10、決め手
          enemy_hp<=10、gap)なので番人 hp_ambiguous に残す。
      新しい枝 mild_shoot: hp 31〜32・昼・A1 の外で、hp>=33 の読みが shoot_far の所 → shoot。
          1 件(r2s2 hp32 ゴブリン 2 体 d6 矢 18 警報済み)、根拠 L2 で gap なし(規律 (c))。決め手
          distance>=2, arrows=18, enemy=goblin。理由「ゴブリンは離れており矢も多いので射る」。
          夜は a1_night_split が割れているので答えない。
 6. 番人 orc_alarm_unclear から、隣接のオーク 2 体・味方 2 以上 → melee_adjacent。
    5 件・会話 4 本(r1s3、r3s2、r4s1、r4s2 2)・一致 5/5(規律 (b))。決め手は 5 件とも
    distance=1、ほかに allies>=2 / allies>=3、hp>=66 / hp>=91。4 件が根拠 L2 だけ。理由
    「オークが隣接し味方も多いので近接で戦う」。L2 の隣接の規則なので名前は melee_adjacent
    (b3 で昼のゴブリン 3 体の隣接を通したのと同じ)。夜 3 件・昼 2 件、ehp は 30〜70。
    昼の弱ったオーク(orc_pair_day_melee)を先に見る。味方 1 以下の昼の隣接は例が無く番人のまま。
    残り 4 件(持ち場 2 gap、警報 1、射る 1)は orc_alarm_unclear のまま。
 7. mage_no_arrows_cover を 4 マス以上に狭めた(門で落ちる所の直し)。
    r4s3 の hp72 魔術師 d3 ehp40 遮蔽あり 夜 → 斬る(決め手 enemy=mage, arrows=0,
    enemy_hp<=40、「矢が無いので弱った魔術師に詰めて仕留める」)で 3/4 = 75% になった。遮蔽の
    3 件は d5〜7(r2s2 d5、r2s1 d6、r3s1 d7。理由「矢が無く魔術師は遠いので遮蔽で呪文を避ける」)。
    線 4(_MAGE_COVER_MIN)を 3 と 5 の間に置き、3 マスは番人 mage_no_arrows。
    mage_no_arrows_cover は 3/3・会話 3 本に戻る。

熱さの帳簿を b4 で数え直した見込み(答える枝、件数・一致・会話)
    no_threat_hold             63  63/63  12 本   L7      敵なし・hp>=33 → hold_position
    no_arrows_hold             47  46/47  12 本   gap     離れた敵・矢 0・(遮蔽なし、または昼) → hold_position
    shoot_far                  42  41/42  11 本   L2      離れたゴブリン/オーク・矢あり → shoot
    horde_alarm                19  19/19   8 本   L5      警報未・敵 4 以上 → raise_alarm
    melee_adjacent             18  18/18   5 本+4 本 L2   隣接のゴブリン/オーク(オーク 2 体・味方 2 以上を足した) → melee_attack
    hurt_retreat               15  15/15   9 本   L1      hp<=24・薬なし・敵あり → retreat
    wounded_drink              13  11/13   7 本以上 L1+A4 hp 25〜32・薬あり(A4 の hp 25〜28 を足した) → drink_potion
    hurt_drink                 10  10/10   7 本   L1      hp<=24・薬あり → drink_potion
    night_no_arrows_cover      10   9/10   7 本   L6      離れた敵・矢 0・遮蔽あり・夜(A5 の外) → take_cover
    hurt_handover              10   9/10   4 本   L1+A6   hp<=24・薬なし・敵なし・味方あり → retreat
    troll_alarm                10   9/10   6 本   L5+L3   トロル・警報未 → raise_alarm
    mage_first_shoot            8   7/8    6 本   L4+L2   警報未の魔術師・昼・2〜6 マス・敵 2 以下 → shoot
    mage_melee                  8   8/8    7 本   L2+L4   隣接の魔術師 → melee_attack
    wounded_alarm               8   8/8    7 本   L5+L1   hp 25〜32・薬なし・警報未の深刻な脅威・3 マス以上 → raise_alarm
    orc_pair_night_alarm        7   7/7    6 本   L5+L6   警報未のオーク 2 体・夜・味方 1 以下・ehp>25 → raise_alarm
    mild_no_threat_hold         6   5/6    6 本   L7      hp 31〜32・薬なし・敵なし → hold_position(新)
    mage_no_arrows_alarm        6   6/6    3 本   L5+L4   警報未の魔術師・離れて矢 0 → raise_alarm
    mage_far_alarm              6   6/6    4 本   L5+L4   警報未の魔術師・7 マス以上(A3 の外) → raise_alarm
    troll_shoot_allies          5   5/5    4 本   L2+L3   警報済みトロル・味方あり・離れて矢あり → shoot
    troll_alone_cover           5   4/5    4 本   L3+L6   警報済みトロル・味方 0・離れて・遮蔽・夜 → take_cover
    mage_shoot                  5   5/5    4 本   L2+L4   離れた魔術師(警報済み)・矢あり → shoot
    outnumbered_alarm           4   4/4    3 本   L5      警報未・敵 3・味方 0 → raise_alarm
    orc_pair_day_shoot          4   4/4    3 本   L2      警報未のオーク 2 体・昼・離れて矢あり → shoot
    orc_trio_alarm              4   4/4    3 本   L5      警報未のオーク 3 体・味方あり → raise_alarm
    wounded_retreat             4   4/4    3 本   L1      hp 25〜30・薬なし・敵あり・敵が弱っていない → retreat(新)
    mage_no_arrows_cover        3   3/3    3 本   gap     警報済みの魔術師・4 マス以上・矢 0・遮蔽あり → take_cover(狭めた)
    mage_close_in               3   3/3    3 本   L4      警報済みの魔術師・2 マス・矢 0・遮蔽なし → melee_attack
    hurt_troll_alarm            3   3/3    3 本   L5+L3   hp<=24・トロル・警報未・3 マス以上 → raise_alarm
    troll_alone_retreat         3   3/3    3 本   L3      警報済みトロル・味方 0・隣接・夜 → retreat
    mage_night_alarm            3   3/3    2 本   L5+L6   警報未の魔術師・夜・2〜6 マス・敵 2 以下 → raise_alarm
    a1_shoot                    3   3/3    2 本   A1      hp>=31・敵 9 マス以上・矢あり・昼 → shoot
    troll_melee_allies          2   2/2    2 本   L2+L3   警報済みトロル・味方あり・隣接 → melee_attack
    orc_pair_day_no_arrows_alarm 1  1/1    1 本   L5      警報未のオーク 2 体・昼・味方 0・離れて矢 0 → raise_alarm
    orc_pair_day_melee          1   1/1    1 本   L2      警報未のオーク 2 体・昼・隣接・ehp<=25 → melee_attack
    mild_shoot                  1   1/1    1 本   L2      hp 31〜32・薬なし・昼・A1 の外・読みが shoot_far → shoot(新)
    a3_mage_shoot               0                 A3      A3・昼・7 マス以上 → shoot
    (A5 の番人が night_no_arrows_cover・mage_no_arrows_cover・hurt_* から抜く例は、帳簿の
     食い違いの一覧には無く、あっても一致している例が減るだけ。)

棄権の番人(割れている所、証拠が足りない所。輪が審判に訊き直す所)
    wounded_no_threat      31  hp 25〜30・薬なし・敵なし(持ち場 13 / 退く 17 / 遮蔽 1)。A6 と逆の会話が多い
    hurt_no_threat         15  hp<=24・薬なし・敵なし・味方 0(退く 9 / 持ち場 6)。A6 と逆が多数
    a1_night_split          6  A1 の範囲の夜(射る 3 / 退く 3)
    group_alarm_unclear     6  警報未のゴブリン 3 体・味方あり・夜(警報 3 / 射る 2 / 斬る 1)
    wounded_alarm_unclear   5  hp 25〜32・警報未の深刻な脅威で A4 の外の薬あり、3 マス未満、
                               hp>=33 の読みが警報でない所(飲む 2 / 斬る 1 / 警報 1 / 射る 1)
    orc_alarm_unclear       4  警報未のオーク 2 体の残り(持ち場 2 / 警報 1 / 射る 1)
    troll_alarm_raised      3  警報済みトロルの残り(持ち場 1 / 退く 1 / 射る 1)
    mage_no_arrows          3  警報済みの魔術師・矢 0 の残り(斬る 2、gap / 飲む 1)。3 マス・遮蔽ありを含む
    hp_ambiguous            1  hp 25〜30 の弱った敵、hp 31〜32 の A1・mild_shoot の外(射る 1、gap)
    a5_troll_unclear        1  A5 の警報済みトロル(持ち場 1、gap)
    a5_mage_unclear         1  A5 の魔術師(斬る 1、gap)
    a5_night_unclear        0  A5 の夜・遮蔽ありのゴブリン/オーク
    a5_hurt_conflict        0  hp<=32 の A5
    mage_alarm_unclear      0  警報未の魔術師・2〜6 マス・敵 3・味方あり
    a3_night_unclear        0  夜の A3
    a2_hurt_conflict        0  hp<=32 の A2
    a3_hurt_conflict        0  hp<=32 の A3(hp 25〜32 は A4 と重なる所)
"""

import math

_ACTIONS = (
    "melee_attack", "shoot", "retreat", "drink_potion",
    "take_cover", "raise_alarm", "hold_position",
)

_ENEMIES = ("none", "goblin", "orc", "mage", "troll")
_POSTS = ("gate", "wall", "corridor")
_TIMES = ("day", "night")

_KEYS = (
    "hp", "enemy", "distance", "enemy_count", "enemy_hp", "allies",
    "potion", "arrows", "cover", "alarm", "post", "time",
)

# 「ひどく傷ついている」
_HURT_MAX = 24      # これ以下はひどい(b2 のまま)
_FINE_MIN = 33      # これ以上はひどくない(b1 のまま)
_MILD_MIN = 31      # hp 31〜32: 敵なし・昼に射る所ではひどいと見ない。hp 25〜30 は退く側(b4)

# 追補 A1
_A1_HP_MIN = 31
_A1_DIST_MIN = 9

# 追補 A2
_A2_DIST_MIN = 11

# 追補 A3
_A3_ENEMY_HP_MAX = 40
_A3_DIST_MIN = 6
_A3_ARROWS_MIN = 11

# 追補 A4
_A4_HP_MAX = 28
_A4_DIST_MIN = 10

# 追補 A5
_A5_ALLIES_MIN = 3
_A5_DIST_MIN = 4

# 傷を負っていて警報未の深刻な脅威がいる時、この距離以上なら先に警報
# (hp<=24 のトロルで隣接 1 は L1、警報側は 5 以上。hp 25〜32 でも同じ線を使う)
_ALARM_FIRST_DIST = 3

# 警報未の群れ
_HORDE_MIN = 4          # 敵がこれ以上なら警報
_OUTNUMBERED_MIN = 3    # 味方 0 で敵がこれ以上なら警報

# 警報未の魔術師: この距離以上なら警報(昼の 6 以内は射る)
_MAGE_FAR_MIN = 7

# 警報済みの魔術師・矢 0: この距離以下なら詰めて斬る(審判の決め手 distance<=2)
_MAGE_CLOSE_MAX = 2
# 警報済みの魔術師・矢 0・遮蔽あり: この距離以上なら遮蔽(斬る d3 と遮蔽 d5 の間、b4)
_MAGE_COVER_MIN = 4

# 弱った敵(夜のオーク 2 体: ehp20 は射る、ehp30 は警報。線は 20 と 30 の間)
_WEAK_HP_MAX = 25

# 警報未のオーク 2 体が隣接: 味方がこれ以上なら斬る(例は味方 2・3、b4)
_ORC_MELEE_ALLIES_MIN = 2


def _is_num(v):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return False
    if isinstance(v, float) and not math.isfinite(v):
        return False
    return True


def _is_count(v):
    if not _is_num(v):
        return False
    return float(v).is_integer()


def _in(v, lo, hi, integral=False):
    if integral:
        if not _is_count(v):
            return False
    elif not _is_num(v):
        return False
    return lo <= v <= hi


def _guard(s):
    """範囲の番人。問題があれば棄権の理由の文字列、無ければ None。"""
    if not isinstance(s, dict):
        return "out_of_range: state"
    for k in _KEYS:
        if k not in s:
            return "out_of_range: " + k

    if not _in(s["hp"], 5, 100):
        return "out_of_range: hp"

    enemy = s["enemy"]
    if not isinstance(enemy, str) or enemy not in _ENEMIES:
        return "out_of_range: enemy"

    if enemy == "none":
        if s["distance"] is not None:
            return "out_of_range: distance"
        if not _in(s["enemy_count"], 0, 0, integral=True):
            return "out_of_range: enemy_count"
        if s["enemy_hp"] is not None:
            return "out_of_range: enemy_hp"
    else:
        if not _in(s["distance"], 1, 12, integral=True):
            return "out_of_range: distance"
        if not _in(s["enemy_count"], 1, 5, integral=True):
            return "out_of_range: enemy_count"
        if not _in(s["enemy_hp"], 10, 100):
            return "out_of_range: enemy_hp"

    if not _in(s["allies"], 0, 3, integral=True):
        return "out_of_range: allies"
    if not _in(s["arrows"], 0, 20, integral=True):
        return "out_of_range: arrows"

    for k in ("potion", "cover", "alarm"):
        if not isinstance(s[k], bool):
            return "out_of_range: " + k

    if not isinstance(s["post"], str) or s["post"] not in _POSTS:
        return "out_of_range: post"
    if not isinstance(s["time"], str) or s["time"] not in _TIMES:
        return "out_of_range: time"
    return None


def _a1(s):
    """追補 A1 の範囲(回復薬の有無は問わない。hp 25〜32 では薬ありを先に飲むへ回す)。"""
    return (s["enemy"] != "none" and s["hp"] >= _A1_HP_MIN
            and s["distance"] >= _A1_DIST_MIN and s["arrows"] >= 1)


def _a2(s):
    """追補 A2 の範囲: 夜・矢 0・味方 0・遮蔽あり・敵 11 マス以上。"""
    return (s["enemy"] != "none" and s["time"] == "night"
            and s["arrows"] == 0 and s["allies"] == 0 and s["cover"]
            and s["distance"] >= _A2_DIST_MIN)


def _a3(s):
    """追補 A3 の範囲: 警報未・魔術師一体・体力 40% 以下・6 マス以上・矢 11 本以上。"""
    return (s["enemy"] == "mage" and not s["alarm"]
            and s["enemy_count"] == 1
            and s["enemy_hp"] <= _A3_ENEMY_HP_MAX
            and s["distance"] >= _A3_DIST_MIN
            and s["arrows"] >= _A3_ARROWS_MIN)


def _a4(s):
    """追補 A4 の範囲: 警報未・hp<=28・回復薬あり・魔術師・10 マス以上。"""
    return (s["enemy"] == "mage" and not s["alarm"]
            and s["hp"] <= _A4_HP_MAX and s["potion"]
            and s["distance"] >= _A4_DIST_MIN)


def _a5(s):
    """追補 A5 の範囲: 警報済み・矢 0・味方 3 以上・敵 4 マス以上。"""
    return (s["enemy"] != "none" and s["alarm"]
            and s["arrows"] == 0 and s["allies"] >= _A5_ALLIES_MIN
            and s["distance"] >= _A5_DIST_MIN)


def _serious_unalarmed(s):
    """hp 25〜32 で深刻な脅威として扱う敵か(敵がいて alarm=false の時だけ呼ぶ)。
    b2 のまま。昼のゴブリン 3 体・味方ありは hp>=33 では L2 に落ちるが、ここでは据え置く。"""
    enemy = s["enemy"]
    count = s["enemy_count"]
    if enemy in ("troll", "mage"):
        return True
    if count >= _HORDE_MIN:
        return True
    if count >= _OUTNUMBERED_MIN and s["allies"] == 0:
        return True
    if enemy == "orc" and count >= 2:
        return True
    if enemy == "goblin" and count >= 3:
        return True
    return False


def _hurt(s):
    """hp<=24: ひどく傷ついている(L1)。"""
    enemy = s["enemy"]

    # L5+L3: 警報未のトロルがまだ遠いなら、先に警報
    if (enemy == "troll" and not s["alarm"]
            and s["distance"] >= _ALARM_FIRST_DIST):
        return ("raise_alarm", "hurt_troll_alarm")

    # 追補と L1 がぶつかる所(例なし)
    if _a2(s):
        return (None, "a2_hurt_conflict")
    if _a3(s):
        return (None, "a3_hurt_conflict")
    if _a5(s):
        return (None, "a5_hurt_conflict")

    # L1(A4 の hp<=24 も同じ答え)
    if s["potion"]:
        return ("drink_potion", "hurt_drink")
    if enemy == "none":
        # A6: 味方がいれば退く(帳簿 9/10)。味方 0 の持ち場は帳簿と逆が多数なので棄権
        if s["allies"] >= 1:
            return ("retreat", "hurt_handover")
        return (None, "hurt_no_threat")
    return ("retreat", "hurt_retreat")


def _wounded(s):
    """hp 25〜32: ひどいかどうかが会話で割れる所。"""
    enemy = s["enemy"]
    hp = s["hp"]
    night = s["time"] == "night"

    # 追補 A5 と L1 がぶつかる所
    if _a5(s):
        return (None, "a5_hurt_conflict")

    # 警報未の深刻な脅威
    if enemy != "none" and not s["alarm"] and _serious_unalarmed(s):
        if s["potion"]:
            # 追補 A4: 警報より先に回復薬(L1 の飲む規則と同じ枝)
            if _a4(s):
                if _a2(s):
                    return (None, "a2_hurt_conflict")
                if _a3(s):
                    return (None, "a3_hurt_conflict")
                return ("drink_potion", "wounded_drink")
            return (None, "wounded_alarm_unclear")
        if s["distance"] >= _ALARM_FIRST_DIST:
            act, _name = _fine(s)
            if act == "raise_alarm":
                return ("raise_alarm", "wounded_alarm")
        return (None, "wounded_alarm_unclear")

    # 追補 A2 と L1 がぶつかる所(例なし)
    if _a2(s):
        return (None, "a2_hurt_conflict")

    if s["potion"]:
        return ("drink_potion", "wounded_drink")

    if enemy == "none":
        if hp >= _MILD_MIN:
            return ("hold_position", "mild_no_threat_hold")
        # A6 は帳簿で会話ごとに割れる
        return (None, "wounded_no_threat")

    # 追補 A1: hp>=31、薬なし、敵 9 マス以上、矢あり → 退かずに射る
    if _a1(s):
        if night:
            return (None, "a1_night_split")
        act, _name = _fine(s)
        if act == "shoot":
            return ("shoot", "a1_shoot")
        return (None, "hp_ambiguous")

    if hp >= _MILD_MIN:
        # hp 31〜32: 昼に離れたゴブリン/オークを射る所だけ(L2、gap なしの 1 件)
        if not night:
            _act, name = _fine(s)
            if name == "shoot_far":
                return ("shoot", "mild_shoot")
        return (None, "hp_ambiguous")

    # hp 25〜30・薬なし・敵あり: L1 で退く。弱った敵は射る例があるので棄権
    if s["enemy_hp"] <= _WEAK_HP_MAX:
        return (None, "hp_ambiguous")
    return ("retreat", "wounded_retreat")


def _fine(s):
    """hp>=33: ひどくない。"""
    enemy = s["enemy"]
    dist = s["distance"]
    count = s["enemy_count"]
    allies = s["allies"]
    arrows = s["arrows"]
    cover = s["cover"]
    alarm = s["alarm"]
    night = s["time"] == "night"

    # --- L7: 脅威が無い ---
    if enemy == "none":
        return ("hold_position", "no_threat_hold")

    # --- L3 + L5: トロル ---
    if enemy == "troll":
        if not alarm:
            return ("raise_alarm", "troll_alarm")
        if allies >= 1:
            if dist == 1:
                return ("melee_attack", "troll_melee_allies")
            if arrows >= 1:
                return ("shoot", "troll_shoot_allies")
            if _a5(s):
                return (None, "a5_troll_unclear")
            return (None, "troll_alarm_raised")
        # 味方 0(L3: 一人で相手にするには強すぎる)
        if night:
            if dist == 1:
                return ("retreat", "troll_alone_retreat")
            if cover:
                return ("take_cover", "troll_alone_cover")
            return (None, "troll_alarm_raised")
        if _a1(s):
            return ("shoot", "a1_shoot")
        return (None, "troll_alarm_raised")

    # --- L5: 警報未のとき、深刻な脅威かどうか ---
    if not alarm:
        if count >= _HORDE_MIN:
            return ("raise_alarm", "horde_alarm")
        if count >= _OUTNUMBERED_MIN and allies == 0:
            return ("raise_alarm", "outnumbered_alarm")

        if enemy == "mage":
            if dist == 1:
                return ("melee_attack", "mage_melee")
            if arrows <= 0:
                return ("raise_alarm", "mage_no_arrows_alarm")
            if _a3(s):
                if night:
                    return (None, "a3_night_unclear")
                if dist >= _MAGE_FAR_MIN:
                    return ("shoot", "a3_mage_shoot")
                # 昼の 6 マスは下の mage_first_shoot と同じ答え
            if dist >= _MAGE_FAR_MIN:
                return ("raise_alarm", "mage_far_alarm")
            if count >= 3:
                return (None, "mage_alarm_unclear")
            if night:
                return ("raise_alarm", "mage_night_alarm")
            return ("shoot", "mage_first_shoot")

        if enemy == "orc" and count >= 2:
            if count >= 3:
                # ここに来るのは味方ありのオーク 3 体
                return ("raise_alarm", "orc_trio_alarm")
            weak = s["enemy_hp"] <= _WEAK_HP_MAX
            if night:
                if allies <= 1 and not weak:
                    return ("raise_alarm", "orc_pair_night_alarm")
                if dist == 1 and allies >= _ORC_MELEE_ALLIES_MIN:
                    return ("melee_attack", "melee_adjacent")
            elif dist >= 2:
                if arrows >= 1:
                    return ("shoot", "orc_pair_day_shoot")
                if allies == 0:
                    return ("raise_alarm", "orc_pair_day_no_arrows_alarm")
            elif weak:
                return ("melee_attack", "orc_pair_day_melee")
            elif allies >= _ORC_MELEE_ALLIES_MIN:
                return ("melee_attack", "melee_adjacent")
            return (None, "orc_alarm_unclear")

        if enemy == "goblin" and count >= 3:
            # ここに来るのは味方ありのゴブリン 3 体。昼は深刻な脅威とせず L2 へ
            if night:
                return (None, "group_alarm_unclear")
        # 単独のオーク、ゴブリン 1〜2 体、昼のゴブリン 3 体・味方あり → L2 へ

    # --- L2 (+ L4 魔術師) ---
    if dist == 1:
        if enemy == "mage":
            return ("melee_attack", "mage_melee")
        return ("melee_attack", "melee_adjacent")

    # 離れている(distance>=2)
    if arrows <= 0:
        if enemy == "mage":
            if _a5(s):
                return (None, "a5_mage_unclear")
            if cover and dist >= _MAGE_COVER_MIN:
                return ("take_cover", "mage_no_arrows_cover")
            if not cover and dist <= _MAGE_CLOSE_MAX:
                return ("melee_attack", "mage_close_in")
            return (None, "mage_no_arrows")
        if cover and night:
            if _a5(s):
                return (None, "a5_night_unclear")
            return ("take_cover", "night_no_arrows_cover")
        # A5 の昼・遮蔽なしの範囲もここ(同じ答え)
        return ("hold_position", "no_arrows_hold")
    if enemy == "mage":
        return ("shoot", "mage_shoot")
    return ("shoot", "shoot_far")


def decide(s):
    bad = _guard(s)
    if bad is not None:
        return (None, bad)

    hp = s["hp"]
    if hp <= _HURT_MAX:
        return _hurt(s)
    if hp < _FINE_MIN:
        return _wounded(s)
    return _fine(s)

```

## 熱さの帳簿(審判のラベル 508 件、会話 15 本を、いまの方針の枝ごとに数えた)

| 枝 | 件数 | 会話 | 方針の答え | 一致 | 会話の多数が方針と同じ | 審判の答え | 根拠 | 決め手(多い順) |
|---|---|---|---|---|---|---|---|---|
| no_threat_hold | 66 | 14 | hold_position | 66/66 | 14/14 | {'hold_position': 66} | L7 66, L1 5; gap 5 | enemy=none 66, hp>=40 2, hp>=45 2, hp>=44 1 |
| no_arrows_hold | 56 | 15 | hold_position | 55/56 | 15/15 | {'hold_position': 55, 'take_cover': 1} | L5 1, L6 1; gap 56 | arrows=0 56, distance>=2 19, enemy=goblin 19, allies>=3 8 |
| shoot_far | 54 | 14 | shoot | 53/54 | 13/14 | {'shoot': 53, 'take_cover': 1} | L2 53, A1 2, L6 1; gap 2 | distance>=2 22, arrows>=1 13, enemy=goblin 7, distance>=4 7 |
| wounded_no_threat | 41 | 14 | None | -/- | -/14 | {'hold_position': 15, 'retreat': 25, 'take_cover': 1} | L7 31, L1 29, A6 10; gap 31 | enemy=none 26, potion=false 22, hp<=30 21, allies>=1 10 |
| hurt_no_threat | 25 | 11 | None | -/- | -/11 | {'retreat': 9, 'hold_position': 16} | L1 15, L7 12, A6 10; gap 15 | enemy=none 16, allies=0 15, potion=false 13, hp<=30 8 |
| horde_alarm | 20 | 9 | raise_alarm | 20/20 | 9/9 | {'raise_alarm': 20} | L5 20, L2 12, L6 4; gap 17 | alarm=false 20, enemy_count>=5 11, enemy_count>=4 9, allies=0 8 |
| melee_adjacent | 19 | 9 | melee_attack | 19/19 | 9/9 | {'melee_attack': 19} | L2 19, L6 1, L5 1; gap 2 | distance=1 13, distance<=1 6, enemy_hp<=10 4, allies>=3 3 |
| hurt_retreat | 15 | 9 | retreat | 15/15 | 9/9 | {'retreat': 15} | L1 15, L3 5, L5 3; gap 5 | potion=false 14, hp<=30 6, enemy=troll 4, hp<=22 4 |
| wounded_drink | 13 | 11 | drink_potion | 11/13 | 9/11 | {'raise_alarm': 2, 'drink_potion': 11} | L1 12, L5 6, L4 2; gap 8 | potion=true 11, distance>=10 6, hp<=30 4, hp<=28 4 |
| troll_alarm_raised | 11 | 5 | None | -/- | -/5 | {'retreat': 7, 'hold_position': 2, 'shoot': 1, 'take_cover': 1} | L3 9, L0 6, L2 2; gap 10 | enemy=troll 8, allies=0 6, arrows=0 3, enemy_count>=2 2 |
| troll_alarm | 10 | 6 | raise_alarm | 9/10 | 5/6 | {'raise_alarm': 9, 'melee_attack': 1} | L5 9, L3 8, L2 4; gap 6 | enemy=troll 9, alarm=false 9, allies=0 2, arrows=0 1 |
| night_no_arrows_cover | 10 | 7 | take_cover | 9/10 | 6/7 | {'take_cover': 9, 'drink_potion': 1} | L6 9, L1 1; gap 5 | arrows=0 9, time=night 9, cover=true 8, hp<=44 1 |
| hurt_handover | 10 | 4 | retreat | 9/10 | 3/4 | {'retreat': 9, 'hold_position': 1} | L1 10, L7 10; gap 10 | potion=false 10, allies>=2 4, hp<=15 3, hp<=30 3 |
| hurt_drink | 9 | 7 | drink_potion | 9/9 | 7/7 | {'drink_potion': 9} | L1 9, L2 1, L5 1; gap 3 | potion=true 9, enemy=none 4, hp<=21 4, hp<=30 2 |
| mild_no_threat_hold | 9 | 9 | hold_position | 8/9 | 8/9 | {'retreat': 1, 'hold_position': 8} | L7 9, L1 4; gap 4 | enemy=none 8, hp>=31 4, hp>=32 3, allies=1 2 |
| wounded_alarm | 9 | 8 | raise_alarm | 9/9 | 8/8 | {'raise_alarm': 9} | L5 9, L6 4, L1 4; gap 9 | alarm=false 9, enemy_count>=3 4, allies=0 4, enemy_count>=4 2 |
| mage_shoot | 8 | 6 | shoot | 8/8 | 6/6 | {'shoot': 8} | L2 8, L4 8 | enemy=mage 8, arrows>=4 2, distance>=4 2, arrows>=18 2 |
| mage_first_shoot | 8 | 6 | shoot | 7/8 | 5/6 | {'shoot': 7, 'raise_alarm': 1} | L4 8, L5 7, L2 5; gap 8 | enemy=mage 8, arrows>=11 3, enemy_count=1 1, enemy_hp<=10 1 |
| mage_melee | 8 | 7 | melee_attack | 8/8 | 7/7 | {'melee_attack': 8} | L2 8, L4 8, L5 6; gap 7 | enemy=mage 8, distance=1 4, distance<=1 4, enemy_hp<=30 2 |
| orc_pair_night_alarm | 7 | 6 | raise_alarm | 7/7 | 6/6 | {'raise_alarm': 7} | L5 7, L6 6, L2 6; gap 6 | alarm=false 7, time=night 7, allies=0 4, enemy=orc 2 |
| group_alarm_unclear | 7 | 7 | None | -/- | -/7 | {'shoot': 2, 'raise_alarm': 3, 'melee_attack': 2} | L2 6, L5 4, L6 3; gap 4 | alarm=false 3, enemy_count>=3 3, time=night 3, distance=1 2 |
| wounded_alarm_unclear | 7 | 5 | None | -/- | -/5 | {'raise_alarm': 1, 'drink_potion': 2, 'melee_attack': 1, 'shoot': 2, 'retreat': 1} | L1 5, L5 3, L2 3; gap 6 | potion=true 2, hp>=31 2, alarm=false 1, enemy_count>=3 1 |
| a1_night_split | 6 | 4 | None | -/- | -/4 | {'shoot': 3, 'retreat': 3} | L2 4, L1 3, L6 2; gap 5 | distance>=2 2, hp<=33 2, potion=false 2, time=night 2 |
| mage_no_arrows_alarm | 6 | 3 | raise_alarm | 6/6 | 3/3 | {'raise_alarm': 6} | L5 6, L4 4, L6 2; gap 1 | enemy=mage 6, alarm=false 6, arrows=0 5, enemy_count>=3 1 |
| mage_far_alarm | 6 | 4 | raise_alarm | 6/6 | 4/4 | {'raise_alarm': 6} | L5 6, L4 6, L2 3; gap 6 | alarm=false 6, enemy=mage 4, enemy_count>=3 3, arrows<=1 1 |
| orc_alarm_unclear | 6 | 6 | None | -/- | -/6 | {'shoot': 1, 'hold_position': 2, 'raise_alarm': 3} | L5 4, L2 2, L6 1; gap 5 | arrows=0 3, alarm=false 3, enemy_count>=2 2, distance>=3 1 |
| troll_shoot_allies | 5 | 4 | shoot | 5/5 | 4/4 | {'shoot': 5} | L2 5, L3 4; gap 2 | allies>=2 3, distance>=2 3, arrows>=14 2, distance>=4 1 |
| troll_alone_cover | 5 | 4 | take_cover | 4/5 | 3/4 | {'take_cover': 4, 'retreat': 1} | L6 5, L3 5, L2 2; gap 5 | enemy=troll 5, allies=0 5, time=night 3, cover=true 2 |
| outnumbered_alarm | 4 | 3 | raise_alarm | 4/4 | 3/3 | {'raise_alarm': 4} | L5 4, L6 3, L2 2; gap 4 | enemy_count>=3 4, allies=0 4, alarm=false 4 |
| orc_pair_day_shoot | 4 | 3 | shoot | 4/4 | 3/3 | {'shoot': 4} | L2 4, L5 2; gap 3 | enemy_hp<=30 2, arrows>=3 1, allies>=3 1, distance>=12 1 |
| orc_trio_alarm | 4 | 3 | raise_alarm | 4/4 | 3/3 | {'raise_alarm': 4} | L5 4, L2 3, L6 1; gap 4 | enemy_count>=3 4, alarm=false 4, time=night 1, allies>=2 1 |
| wounded_retreat | 4 | 3 | retreat | 4/4 | 3/3 | {'retreat': 4} | L1 4, L2 2; gap 2 | potion=false 4, hp<=28 2, hp<=25 1, hp<=26 1 |
| mage_no_arrows | 4 | 4 | None | -/- | -/4 | {'melee_attack': 2, 'drink_potion': 1, 'hold_position': 1} | L4 2, L1 1, L6 1; gap 4 | arrows=0 4, enemy=mage 2, hp>=82 1, hp<=39 1 |
| mage_close_in | 3 | 3 | melee_attack | 3/3 | 3/3 | {'melee_attack': 3} | L4 3, L2 2; gap 3 | enemy=mage 3, arrows=0 3, distance<=2 2, hp>=90 1 |
| a5_troll_unclear | 3 | 3 | None | -/- | -/3 | {'hold_position': 3} | A5 2, L3 1; gap 1 | arrows=0 3, allies>=3 3, alarm=true 2, distance>=12 1 |
| hurt_troll_alarm | 3 | 3 | raise_alarm | 3/3 | 3/3 | {'raise_alarm': 3} | L1 3, L5 3, L3 1; gap 3 | alarm=false 3, enemy=troll 3, distance>=12 1, distance>=10 1 |
| troll_alone_retreat | 3 | 3 | retreat | 3/3 | 3/3 | {'retreat': 3} | L2 3, L3 3, L6 2; gap 3 | enemy=troll 3, allies=0 3, time=night 1, distance=1 1 |
| mage_night_alarm | 3 | 2 | raise_alarm | 3/3 | 2/2 | {'raise_alarm': 3} | L4 3, L5 3, L6 2; gap 3 | enemy=mage 3, alarm=false 3, time=night 2, allies=0 1 |
| a1_shoot | 3 | 2 | shoot | 3/3 | 2/2 | {'shoot': 3} | L2 3, A1 2, L3 1; gap 1 | hp>=31 2, distance>=9 2, arrows>=6 1, arrows>=15 1 |
| a5_mage_unclear | 2 | 2 | None | -/- | -/2 | {'take_cover': 1, 'melee_attack': 1} | L4 1; gap 2 | enemy=mage 2, arrows=0 2, cover=true 1, hp>=90 1 |
| troll_melee_allies | 2 | 2 | melee_attack | 2/2 | 2/2 | {'melee_attack': 2} | L2 2, L3 2 | enemy=troll 2, distance<=1 1, allies>=1 1, distance=1 1 |
| mage_no_arrows_cover | 2 | 2 | take_cover | 2/2 | 2/2 | {'take_cover': 2} | L0 1; gap 2 | enemy=mage 2, arrows=0 2, cover=true 2 |
| hp_ambiguous | 2 | 2 | None | -/- | -/2 | {'shoot': 1, 'raise_alarm': 1} | L2 2, L1 1, L5 1; gap 2 | enemy_hp<=10 1, distance>=7 1, arrows>=9 1, alarm=false 1 |
| orc_pair_day_no_arrows_alarm | 1 | 1 | raise_alarm | 1/1 | 1/1 | {'raise_alarm': 1} | L5 1 | alarm=false 1, allies=0 1, enemy_count>=2 1 |
| mild_shoot | 1 | 1 | shoot | 1/1 | 1/1 | {'shoot': 1} | L2 1 | distance>=2 1, arrows=18 1, enemy=goblin 1 |
| orc_pair_day_melee | 1 | 1 | melee_attack | 1/1 | 1/1 | {'melee_attack': 1} | L2 1 | distance=1 1, enemy_hp<=20 1 |
| a5_hurt_conflict | 1 | 1 | None | -/- | -/1 | {'drink_potion': 1} | L1 1 | hp<=12 1, potion=true 1 |
| a5_night_unclear | 1 | 1 | None | -/- | -/1 | {'hold_position': 1} | A5 1 | alarm=true 1, arrows=0 1, allies>=3 1 |
| mage_alarm_unclear | 1 | 1 | None | -/- | -/1 | {'raise_alarm': 1} | L4 1, L5 1; gap 1 | alarm=false 1, enemy=mage 1, enemy_count>=3 1 |

## 食い違いと棄権の例(全部。[根拠] 決め手 「理由」 会話)
### no_arrows_hold
- 方針=hold_position 審判=take_cover [gap] hp<=42,potion=false,arrows=0 「矢も薬も無く体力半分以下、遮蔽で門に踏み止まる」 (round1_s2) | hp=42 enemy=goblin distance=4 enemy_count=3 enemy_hp=60 allies=3 potion=False arrows=0 cover=True alarm=True post=gate time=day
### shoot_far
- 方針=shoot 審判=take_cover [L2,L6+gap] time=night,enemy_count>=5,allies=0 「夜に一人で五体相手なので遮蔽で援軍を待つ」 (round2_s1) | hp=99 enemy=goblin distance=3 enemy_count=5 enemy_hp=60 allies=0 potion=True arrows=12 cover=True alarm=True post=gate time=night
### wounded_no_threat
- 方針=None 審判=hold_position [L0,L7+gap] enemy=none,post=gate 「深手だが敵はなく、夜の門を空けず持ち場に留まる」 (round1_s1) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=True alarm=False post=gate time=night
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,allies=0,hp>=30 「敵も代わりもいない、体力30なら門に残る」 (round1_s3) | hp=30 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=0 cover=False alarm=False post=gate time=night
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,allies=0,hp<=28 「傷は深いが脅威が無く、門を空けられないので留まる」 (round2_s3) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=True alarm=False post=gate time=night
- 方針=None 審判=hold_position [L7+gap] enemy=none,hp<=26,potion=false 「手負いだが脅威は無い、まだ持ち場を守れる」 (round3_s1) | hp=26 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=8 cover=False alarm=False post=gate time=night
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp<=28 「傷は深いが敵がおらず門を守り続ける」 (round3_s3) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=True alarm=False post=gate time=night
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp<=25 「重傷だが敵がいないので持ち場を守る」 (round3_s3) | hp=25 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=1 cover=False alarm=False post=gate time=night
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp<=28 「傷は深いが敵がいないので持ち場を守る」 (round3_s3) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=0 cover=True alarm=False post=wall time=day
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp<=28 「傷は深いが敵がいないので持ち場を守る」 (round3_s3) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=4 cover=False alarm=False post=gate time=day
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp<=30,potion=false 「深手だが脅威が無く、退く理由がないので持ち場に留まる」 (round4_s1) | hp=30 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=12 cover=False alarm=False post=wall time=night
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp<=30,potion=false 「深手だが敵がいないので門を離れず守る」 (round4_s1) | hp=30 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=0 cover=False alarm=False post=gate time=night
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp<=30,potion=false 「深手だが脅威が無いので持ち場に留まる」 (round4_s1) | hp=25 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=4 cover=False alarm=False post=corridor time=day
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp<=30,potion=false 「深手だが脅威が無いので持ち場に留まる」 (round4_s1) | hp=29 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=19 cover=True alarm=False post=wall time=day
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,allies=0,alarm=false 「脅威が無く単独、門を空けずに持ち場を守る」 (round4_s2) | hp=30 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=0 cover=False alarm=False post=gate time=night
- 方針=None 審判=hold_position [A6] enemy=none,hp<=29,allies=0 「敵なしで味方もいないので持ち場を守る」 (round5_s1) | hp=29 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=2 cover=False alarm=False post=gate time=day
- 方針=None 審判=hold_position [A6] enemy=none,hp<=30,allies=0 「敵がおらず味方もいないので持ち場を守る」 (round5_s3) | hp=27 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=11 cover=False alarm=False post=gate time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false,allies>=2 「深手で薬が無く味方が残るので退いて癒す」 (round2_s1) | hp=29 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=19 cover=True alarm=False post=wall time=day
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false 「深手で薬が無いので敵のいない今退く」 (round2_s1) | hp=30 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=12 cover=False alarm=False post=wall time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false,allies>=2 「深手で薬が無く味方が残るので退く」 (round2_s1) | hp=26 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=16 cover=False alarm=False post=corridor time=day
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false 「深手で薬が無いので敵のいない今退く」 (round2_s1) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=True alarm=False post=gate time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false,time=night 「深手で薬が無い夜なので退く」 (round2_s1) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=7 cover=False alarm=True post=wall time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false 「重傷で薬も無いので退いて立て直す」 (round2_s2) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=True alarm=False post=gate time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=28,potion=false,allies>=1 「重傷で薬が無い、持ち場は味方に任せて退く」 (round2_s3) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=3 cover=False alarm=False post=wall time=day
- 方針=None 審判=retreat [L1,L6,L7+gap] hp<=28,potion=false,time=night 「夜に独りで重傷、薬も無いので退いて立て直す」 (round3_s2) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=True alarm=False post=gate time=night
- 方針=None 審判=retreat [L1,L6,L7+gap] hp<=27,potion=false,time=night 「夜に独りで重傷、薬も無いので退く」 (round3_s2) | hp=27 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=11 cover=False alarm=False post=gate time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=25,potion=false,arrows=0 「重傷で薬も矢も無い、敵のいない今退く」 (round3_s2) | hp=25 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=0 cover=True alarm=False post=wall time=day
- 方針=None 審判=retreat [L1,L7+gap] hp<=29,potion=false,allies>=2 「重傷で薬が無く、味方が持ち場を守れるので退く」 (round4_s2) | hp=29 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=19 cover=True alarm=False post=wall time=day
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false,allies>=1 「重傷で薬が無く、味方がいるので退いて癒す」 (round4_s2) | hp=30 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=12 cover=False alarm=False post=wall time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false,enemy=none 「重傷で薬が無く夜に単独、敵不在の今のうちに退く」 (round4_s3) | hp=30 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=0 cover=False alarm=False post=gate time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=29,potion=false,enemy=none 「重傷で薬も矢も無いので退いて立て直す」 (round4_s3) | hp=29 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=0 cover=True alarm=False post=gate time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false,enemy=none 「重傷で薬が無く夜に単独なので退く」 (round4_s3) | hp=30 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=0 cover=False alarm=False post=gate time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false,allies=1 「重傷で薬が無く、壁は味方に任せて退く」 (round4_s3) | hp=30 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=12 cover=False alarm=False post=wall time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=29,potion=false,allies=2 「重傷で薬が無く、味方二人に任せて退く」 (round4_s3) | hp=29 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=19 cover=True alarm=False post=wall time=day
- 方針=None 審判=retreat [A6] enemy=none,hp<=28,allies>=1 「敵なしで深手、薬無く味方がいるので退く」 (round5_s1) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=7 cover=False alarm=True post=wall time=night
- 方針=None 審判=retreat [A6] enemy=none,hp<=26,allies>=1 「敵なしで深手、薬無く味方がいるので退く」 (round5_s1) | hp=26 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=16 cover=False alarm=False post=corridor time=day
- 方針=None 審判=retreat [A6] enemy=none,hp<=30,allies>=1 「傷が深く薬なし、味方がいるので退く」 (round5_s2) | hp=26 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=16 cover=False alarm=False post=corridor time=day
- 方針=None 審判=retreat [A6] enemy=none,hp<=30,allies>=1 「傷が深く薬なし、味方がいるので退く」 (round5_s2) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=3 potion=False arrows=9 cover=False alarm=False post=gate time=night
- 方針=None 審判=retreat [A6] enemy=none,hp<=30,allies>=1 「傷が深く薬なし、味方がいるので退く」 (round5_s2) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=7 cover=False alarm=True post=wall time=night
- 方針=None 審判=retreat [A6] enemy=none,hp<=30,allies>=1 「傷が深く薬なし、味方がいるので退く」 (round5_s2) | hp=27 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=17 cover=False alarm=False post=corridor time=day
- 方針=None 審判=retreat [A6] enemy=none,hp<=30,allies>=1 「敵がおらず深手で薬も無く、味方がいるので退く」 (round5_s3) | hp=26 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=16 cover=False alarm=False post=corridor time=day
- 方針=None 審判=retreat [A6] enemy=none,hp<=30,allies>=1 「敵がおらず深手で薬も無く、味方がいるので退く」 (round5_s3) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=7 cover=False alarm=True post=wall time=night
- 方針=None 審判=take_cover [L1,L6,L7+gap] hp<=28,time=night,cover=true 「重傷の夜、持ち場を離れず遮蔽に身を隠して見張る」 (round3_s1) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=True alarm=False post=gate time=night
### hurt_no_threat
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,allies=0,hp<=15 「重傷だが脅威が無く、門を空けないため留まる」 (round2_s3) | hp=15 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=11 cover=True alarm=False post=gate time=day
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,allies=0,hp<=10 「重傷だが脅威が無く、代わりもいないので留まる」 (round2_s3) | hp=10 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=False alarm=False post=corridor time=day
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp<=14,allies=0 「重傷だが敵がおらず、無人にせず持ち場を守る」 (round3_s3) | hp=14 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=0 cover=False alarm=False post=wall time=day
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp<=5,allies=0 「重傷だが脅威が無く、今は持ち場を離れない」 (round3_s3) | hp=5 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=0 cover=True alarm=False post=corridor time=day
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp<=8,allies=0 「重傷でも脅威が無く、門を空けずに守る」 (round3_s3) | hp=8 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=15 cover=True alarm=False post=gate time=day
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp<=18 「重傷だが脅威が無く持ち場を守る」 (round3_s3) | hp=18 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=12 cover=False alarm=False post=corridor time=day
- 方針=None 審判=hold_position [A6] enemy=none,potion=false,allies=0 「敵なしで味方もいないので持ち場を守る」 (round5_s1) | hp=8 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=6 cover=True alarm=False post=wall time=day
- 方針=None 審判=hold_position [A6] enemy=none,potion=false,allies=0 「敵なしで味方もいないので持ち場を守る」 (round5_s1) | hp=14 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=4 cover=True alarm=False post=gate time=day
- 方針=None 審判=hold_position [A6] enemy=none,potion=false,allies=0 「敵なしで味方もいないので持ち場を守る」 (round5_s1) | hp=23 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=15 cover=True alarm=False post=gate time=day
- 方針=None 審判=hold_position [A6] enemy=none,potion=false,allies=0 「敵なしで味方もいないので持ち場を守る」 (round5_s1) | hp=12 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=14 cover=False alarm=False post=wall time=day
- 方針=None 審判=hold_position [A6] enemy=none,hp<=30,allies=0 「敵なし・薬なし・味方なしなので持ち場を守る」 (round5_s2) | hp=8 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=10 cover=False alarm=False post=gate time=night
- 方針=None 審判=hold_position [A6] enemy=none,hp<=30,allies=0 「敵なし・薬なし・味方なしなので持ち場を守る」 (round5_s2) | hp=6 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=0 cover=False alarm=False post=wall time=day
- 方針=None 審判=hold_position [A6] enemy=none,hp<=30,allies=0 「敵なし・薬なし・味方なしなので持ち場を守る」 (round5_s2) | hp=23 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=15 cover=True alarm=False post=gate time=day
- 方針=None 審判=hold_position [A6] enemy=none,hp<=30,allies=0 「敵なし・薬なし・味方なしなので持ち場を守る」 (round5_s2) | hp=14 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=4 cover=True alarm=False post=gate time=day
- 方針=None 審判=hold_position [A6] enemy=none,hp<=30,allies=0 「敵がおらず味方もいないので持ち場を守る」 (round5_s3) | hp=23 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=15 cover=True alarm=False post=gate time=day
- 方針=None 審判=hold_position [A6] enemy=none,hp<=30,allies=0 「敵がおらず味方もいないので持ち場を守る」 (round5_s3) | hp=14 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=4 cover=True alarm=False post=gate time=day
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false 「深手で薬が無いので退いて癒す」 (round2_s1) | hp=23 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=15 cover=True alarm=False post=gate time=day
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false 「重傷で薬が無いので敵のいない今のうちに退く」 (round2_s2) | hp=14 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=4 cover=True alarm=False post=gate time=day
- 方針=None 審判=retreat [L1+gap] hp<=18,potion=false,arrows=0 「一撃で倒れる体力、脅威の無い今のうちに退き立て直す」 (round3_s1) | hp=18 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=0 cover=False alarm=False post=gate time=day
- 方針=None 審判=retreat [L1+gap] hp<=9,potion=false 「瀕死で回復手段が無い、脅威の無い今退いて立て直す」 (round3_s1) | hp=9 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=0 cover=True alarm=False post=wall time=day
- 方針=None 審判=retreat [L1+gap] hp<=7,potion=false 「瀕死で回復手段が無い、脅威の無い今退いて立て直す」 (round3_s1) | hp=7 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=4 cover=False alarm=False post=gate time=day
- 方針=None 審判=retreat [L0,L1,L7+gap] hp<=7,potion=false 「瀕死で薬も無い、敵がいないうちに退く」 (round3_s2) | hp=7 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=12 cover=False alarm=True post=gate time=day
- 方針=None 審判=retreat [L1,L7+gap] hp<=14,potion=false,alarm=true 「瀕死で薬も無く、警報は鳴っているので退く」 (round4_s2) | hp=14 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=14 cover=True alarm=True post=wall time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=13,potion=false 「瀕死で薬が無いので退く」 (round4_s3) | hp=13 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=19 cover=False alarm=False post=gate time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=20,potion=false 「重傷で薬が無いので夜のうちに退く」 (round4_s3) | hp=20 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=20 cover=False alarm=False post=gate time=night
### wounded_drink
- 方針=drink_potion 審判=raise_alarm [L4,L5+gap] enemy=mage,alarm=false,distance>=10 「深手だが魔術師はまだ遠い、先に警報を鳴らす」 (round1_s1) | hp=28 enemy=mage distance=10 enemy_count=2 enemy_hp=80 allies=2 potion=True arrows=10 cover=False alarm=False post=wall time=night
- 方針=drink_potion 審判=raise_alarm [L1,L4,L5+gap] enemy=mage,alarm=false,distance>=10 「魔術師はまだ遠い、薬より先に警報を鳴らす」 (round3_s2) | hp=28 enemy=mage distance=10 enemy_count=2 enemy_hp=80 allies=2 potion=True arrows=10 cover=False alarm=False post=wall time=night
### troll_alarm_raised
- 方針=None 審判=hold_position [L0,L3+gap] enemy=troll,enemy_hp<=10,alarm=true 「瀕死のトロルに単独で突っ込まず門を守り援軍を待つ」 (round3_s1) | hp=83 enemy=troll distance=5 enemy_count=1 enemy_hp=10 allies=0 potion=False arrows=0 cover=False alarm=True post=gate time=day
- 方針=None 審判=hold_position [gap] arrows=0,distance>=12,allies>=2 「矢が無く敵は遠い。味方と共に弱ったトロルを待つ」 (round5_s3) | hp=35 enemy=troll distance=12 enemy_count=1 enemy_hp=20 allies=2 potion=False arrows=0 cover=False alarm=True post=corridor time=day
- 方針=None 審判=retreat [L0,L3+gap] enemy=troll,arrows=0,hp<=42 「手負いで矢も無くトロルは手に余るので退く」 (round2_s2) | hp=42 enemy=troll distance=4 enemy_count=2 enemy_hp=60 allies=1 potion=False arrows=0 cover=True alarm=True post=gate time=day
- 方針=None 審判=retreat [L2,L3+gap] enemy=troll,enemy_count>=2,allies=0 「トロル二体に単独で挑むのは無駄死になので退く」 (round5_s1) | hp=48 enemy=troll distance=5 enemy_count=2 enemy_hp=30 allies=0 potion=False arrows=5 cover=False alarm=True post=wall time=day
- 方針=None 審判=retreat [L3,L0+gap] enemy=troll,allies=0,enemy_count>=2 「味方無しでトロルに一人では勝てないので、射つより退く」 (round5_s3) | hp=83 enemy=troll distance=4 enemy_count=2 enemy_hp=70 allies=0 potion=False arrows=8 cover=True alarm=True post=gate time=day
- 方針=None 審判=retreat [L3,L0+gap] enemy=troll,allies=0,distance<=1 「単独でトロルに隣接され、近接より退くを選ぶ」 (round5_s3) | hp=68 enemy=troll distance=1 enemy_count=1 enemy_hp=40 allies=0 potion=False arrows=12 cover=True alarm=True post=gate time=day
- 方針=None 審判=retreat [L3,L0+gap] enemy=troll,allies=0,distance<=1 「一人でトロルとは戦えないので退く」 (round5_s3) | hp=88 enemy=troll distance=1 enemy_count=1 enemy_hp=70 allies=0 potion=False arrows=5 cover=True alarm=True post=gate time=day
- 方針=None 審判=retreat [L3,L6+gap] enemy=troll,allies=0,time=night 「夜に単独でトロルを相手にできないので退く」 (round5_s3) | hp=74 enemy=troll distance=6 enemy_count=2 enemy_hp=40 allies=0 potion=False arrows=8 cover=False alarm=True post=gate time=night
- 方針=None 審判=retreat [L3,L0] enemy=troll,allies=0,enemy_count>=4 「矢も味方も無く、トロルを含む四体には勝てないので退く」 (round5_s3) | hp=95 enemy=troll distance=4 enemy_count=4 enemy_hp=50 allies=0 potion=False arrows=0 cover=False alarm=True post=wall time=day
- 方針=None 審判=shoot [L2,L3+gap] hp>=94,distance>=8,enemy_hp<=20 「トロルは遠く瀕死、近づく前に射て削る」 (round3_s2) | hp=94 enemy=troll distance=8 enemy_count=2 enemy_hp=20 allies=0 potion=True arrows=13 cover=False alarm=True post=wall time=night
- 方針=None 審判=take_cover [L6+gap] time=night,arrows=0,cover=true 「夜で矢が無く、トロルの接近を遮蔽で待つ」 (round5_s3) | hp=84 enemy=troll distance=4 enemy_count=1 enemy_hp=80 allies=2 potion=True arrows=0 cover=True alarm=True post=wall time=night
### troll_alarm
- 方針=raise_alarm 審判=melee_attack [L2+gap] distance<=1,enemy_hp<=10,allies>=1 「味方がいて瀕死のトロルが隣接、今仕留める」 (round3_s1) | hp=73 enemy=troll distance=1 enemy_count=2 enemy_hp=10 allies=1 potion=False arrows=1 cover=True alarm=False post=wall time=day
### night_no_arrows_cover
- 方針=take_cover 審判=drink_potion [L1+gap] hp<=44,potion=true,distance>=11 「矢が無く敵は遠い、夜の三体に備え今のうちに回復する」 (round3_s1) | hp=44 enemy=goblin distance=11 enemy_count=3 enemy_hp=30 allies=0 potion=True arrows=0 cover=True alarm=True post=wall time=night
### hurt_handover
- 方針=retreat 審判=hold_position [L1,L7+gap] enemy=none,hp<=30,potion=false 「深手でも脅威が無いので持ち場を空けない」 (round4_s1) | hp=17 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=0 cover=True alarm=False post=gate time=day
### mild_no_threat_hold
- 方針=hold_position 審判=retreat [L1,L7+gap] hp<=33,potion=false,allies>=2 「深手で薬が無く味方が残るので退いて癒す」 (round2_s1) | hp=32 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=20 cover=True alarm=False post=corridor time=day
### mage_first_shoot
- 方針=shoot 審判=raise_alarm [L4,L5+gap] enemy=mage,alarm=false,allies=0 「魔術師出現で警報未発、独りなので先に鳴らす」 (round3_s2) | hp=84 enemy=mage distance=6 enemy_count=1 enemy_hp=40 allies=0 potion=True arrows=11 cover=True alarm=False post=gate time=day
### group_alarm_unclear
- 方針=None 審判=melee_attack [L2,L5+gap] distance=1,enemy=goblin,hp>=76 「隣接の小鬼に近接、小鬼の群れは深刻とまで見ない」 (round4_s3) | hp=76 enemy=goblin distance=1 enemy_count=3 enemy_hp=90 allies=1 potion=False arrows=20 cover=False alarm=False post=gate time=night
- 方針=None 審判=melee_attack [L2] distance=1,enemy=goblin 「ゴブリンが隣接しているので近接で戦う」 (round5_s2) | hp=93 enemy=goblin distance=1 enemy_count=3 enemy_hp=50 allies=2 potion=True arrows=3 cover=False alarm=False post=gate time=night
- 方針=None 審判=raise_alarm [L2,L5,L6+gap] alarm=false,enemy_count>=3,time=night 「夜にゴブリン三体、遠いうちに警報」 (round2_s1) | hp=90 enemy=goblin distance=7 enemy_count=3 enemy_hp=80 allies=1 potion=True arrows=13 cover=True alarm=False post=wall time=night
- 方針=None 審判=raise_alarm [L5,L6+gap] alarm=false,enemy_count>=3,time=night 「夜に門へ三体、手負いで矢も無く警報で援軍を呼ぶ」 (round3_s1) | hp=39 enemy=goblin distance=3 enemy_count=3 enemy_hp=70 allies=2 potion=False arrows=0 cover=True alarm=False post=gate time=night
- 方針=None 審判=raise_alarm [L2,L5,L6+gap] time=night,enemy_count>=3,alarm=false 「夜に三体が迫る、距離のあるうちに警報」 (round4_s2) | hp=51 enemy=goblin distance=12 enemy_count=3 enemy_hp=30 allies=2 potion=False arrows=11 cover=True alarm=False post=gate time=night
- 方針=None 審判=shoot [L2] distance>=12,arrows>=2,allies>=3 「遠いゴブリンを射る、味方も多く警報は不要」 (round1_s3) | hp=38 enemy=goblin distance=12 enemy_count=3 enemy_hp=50 allies=3 potion=False arrows=2 cover=True alarm=False post=gate time=night
- 方針=None 審判=shoot [L2] distance>=2,arrows>=10 「隣接前のゴブリンを矢で射る」 (round3_s2) | hp=93 enemy=goblin distance=2 enemy_count=3 enemy_hp=60 allies=1 potion=False arrows=10 cover=False alarm=False post=gate time=night
### wounded_alarm_unclear
- 方針=None 審判=drink_potion [L1,L5+gap] hp<=26,potion=true,enemy=goblin 「重傷で薬がある、ゴブリン相手なら回復が先」 (round2_s3) | hp=26 enemy=goblin distance=3 enemy_count=3 enemy_hp=90 allies=1 potion=True arrows=20 cover=True alarm=False post=gate time=night
- 方針=None 審判=drink_potion [L1,L2+gap] hp<=30,potion=true 「hp30は重傷と見て、隣接中でも薬を飲む」 (round3_s2) | hp=30 enemy=orc distance=1 enemy_count=2 enemy_hp=30 allies=2 potion=True arrows=2 cover=True alarm=False post=gate time=day
- 方針=None 審判=melee_attack [L2,L4+gap] enemy=mage,distance<=1,enemy_hp<=20 「隣接した瀕死の魔術師を飲むより先に仕留める」 (round3_s1) | hp=30 enemy=mage distance=1 enemy_count=1 enemy_hp=20 allies=1 potion=True arrows=3 cover=True alarm=False post=gate time=day
- 方針=None 審判=raise_alarm [L1,L5+gap] alarm=false,enemy_count>=3,allies=0 「単独でオーク三体、助けを呼ぶのが生存の道」 (round2_s3) | hp=27 enemy=orc distance=3 enemy_count=3 enemy_hp=70 allies=0 potion=True arrows=7 cover=True alarm=False post=corridor time=day
- 方針=None 審判=retreat [L1,L5+gap] hp<=28,potion=false,distance<=2 「深手で薬も無く敵が迫っているので退く」 (round5_s1) | hp=28 enemy=orc distance=2 enemy_count=2 enemy_hp=30 allies=0 potion=False arrows=15 cover=True alarm=False post=corridor time=night
- 方針=None 審判=shoot [L1,L2+gap] hp>=31,distance>=7,arrows>=19 「hp31は重傷と見ず、近づくゴブリンを射る」 (round3_s2) | hp=31 enemy=goblin distance=7 enemy_count=4 enemy_hp=60 allies=3 potion=True arrows=19 cover=False alarm=False post=wall time=day
- 方針=None 審判=shoot [A3,A1] enemy_hp<=40,arrows>=11,hp>=31 「弱った魔術師一体を警報より先に射る」 (round5_s3) | hp=31 enemy=mage distance=11 enemy_count=1 enemy_hp=20 allies=1 potion=False arrows=15 cover=True alarm=False post=wall time=night
### a1_night_split
- 方針=None 審判=retreat [L1,L6+gap] hp<=33,potion=false,time=night 「深手で薬が無い夜なので射るより退く」 (round2_s1) | hp=31 enemy=goblin distance=9 enemy_count=3 enemy_hp=40 allies=1 potion=False arrows=5 cover=False alarm=True post=wall time=night
- 方針=None 審判=retreat [L1,L6+gap] hp<=33,potion=false,allies>=3 「深手で薬の無い夜、味方に任せて退く」 (round2_s1) | hp=32 enemy=orc distance=9 enemy_count=3 enemy_hp=20 allies=3 potion=False arrows=15 cover=True alarm=True post=gate time=night
- 方針=None 審判=retreat [L0,L2+gap] hp<=31,enemy_count>=4,time=night 「深手で夜にオーク4体、無駄死にを避けて退く」 (round2_s2) | hp=31 enemy=orc distance=10 enemy_count=4 enemy_hp=90 allies=1 potion=False arrows=2 cover=False alarm=True post=corridor time=night
- 方針=None 審判=shoot [L2+gap] distance>=2,arrows>=1,hp>=31 「手負いだが敵は遠く、射るだけなら危険は小さい」 (round1_s1) | hp=31 enemy=goblin distance=9 enemy_count=3 enemy_hp=40 allies=1 potion=False arrows=5 cover=False alarm=True post=wall time=night
- 方針=None 審判=shoot [L2] distance>=2,arrows=5,enemy=goblin 「城壁から遠いゴブリンを射る」 (round2_s2) | hp=31 enemy=goblin distance=9 enemy_count=3 enemy_hp=40 allies=1 potion=False arrows=5 cover=False alarm=True post=wall time=night
- 方針=None 審判=shoot [L1,L2+gap] distance>=9,arrows>=5,alarm=true 「敵は遠く警報済み、まだ射って戦える傷と見る」 (round2_s3) | hp=31 enemy=goblin distance=9 enemy_count=3 enemy_hp=40 allies=1 potion=False arrows=5 cover=False alarm=True post=wall time=night
### orc_alarm_unclear
- 方針=None 審判=hold_position [gap] arrows=0,distance>=9 「矢が無く敵は遠い、持ち場で迎え撃つ」 (round3_s2) | hp=64 enemy=orc distance=9 enemy_count=2 enemy_hp=70 allies=1 potion=True arrows=0 cover=True alarm=False post=gate time=day
- 方針=None 審判=hold_position [gap] arrows=0,distance>=2,allies>=3 「矢が無く未接敵、味方と通路で迎え撃つ」 (round4_s1) | hp=68 enemy=orc distance=2 enemy_count=2 enemy_hp=80 allies=3 potion=False arrows=0 cover=False alarm=False post=corridor time=day
- 方針=None 審判=raise_alarm [A1,L5,L6+gap] alarm=false,time=night,distance>=12 「夜にオーク二体、遠い今のうちに警報を鳴らす」 (round3_s3) | hp=33 enemy=orc distance=12 enemy_count=2 enemy_hp=70 allies=2 potion=False arrows=8 cover=False alarm=False post=gate time=night
- 方針=None 審判=raise_alarm [L2,L5+gap] alarm=false,enemy_count>=2,allies=0 「孤立してオーク二体が迫るので斬り合うより先に警報」 (round5_s2) | hp=36 enemy=orc distance=1 enemy_count=2 enemy_hp=100 allies=0 potion=False arrows=5 cover=False alarm=False post=gate time=day
- 方針=None 審判=raise_alarm [L5] alarm=false,enemy_count>=2,arrows=0 「警報未発でオーク二体が門に迫るので鳴らす」 (round5_s3) | hp=70 enemy=orc distance=2 enemy_count=2 enemy_hp=20 allies=1 potion=False arrows=0 cover=False alarm=False post=gate time=day
- 方針=None 審判=shoot [L2,L5+gap] distance>=3,arrows>=11,enemy_hp<=20 「瀕死のオーク二体は射れば片付く、警報は不要」 (round2_s3) | hp=99 enemy=orc distance=3 enemy_count=2 enemy_hp=20 allies=0 potion=True arrows=11 cover=False alarm=False post=corridor time=night
### troll_alone_cover
- 方針=take_cover 審判=retreat [L3,L6+gap] enemy=troll,allies=0,time=night 「夜に単独でトロルと二体、弱っていても退く」 (round3_s1) | hp=80 enemy=troll distance=4 enemy_count=2 enemy_hp=10 allies=0 potion=True arrows=0 cover=True alarm=True post=wall time=night
### mage_no_arrows
- 方針=None 審判=drink_potion [L1+gap] hp<=39,potion=true,arrows=0 「矢が無く届かない間に傷を回復薬で癒す」 (round4_s2) | hp=39 enemy=mage distance=3 enemy_count=1 enemy_hp=50 allies=1 potion=True arrows=0 cover=False alarm=True post=gate time=day
- 方針=None 審判=hold_position [gap] arrows=0,cover=false,distance>=10 「矢も遮蔽も無く、魔術師が近づくまで門を守る」 (round5_s3) | hp=51 enemy=mage distance=10 enemy_count=1 enemy_hp=90 allies=0 potion=False arrows=0 cover=False alarm=True post=gate time=night
- 方針=None 審判=melee_attack [L4+gap] enemy=mage,arrows=0,hp>=82 「矢が無く体力十分、魔術師へ詰めて討つ」 (round3_s3) | hp=82 enemy=mage distance=8 enemy_count=1 enemy_hp=80 allies=0 potion=False arrows=0 cover=False alarm=True post=gate time=day
- 方針=None 審判=melee_attack [L4,L6+gap] enemy=mage,arrows=0,enemy_hp<=40 「矢が無いので弱った魔術師に詰めて仕留める」 (round4_s3) | hp=72 enemy=mage distance=3 enemy_count=1 enemy_hp=40 allies=0 potion=True arrows=0 cover=True alarm=True post=corridor time=night
### a5_troll_unclear
- 方針=None 審判=hold_position [L3+gap] arrows=0,distance>=12,allies>=3 「矢が無く敵は遠い、味方3人と門を固めて待つ」 (round1_s2) | hp=92 enemy=troll distance=12 enemy_count=5 enemy_hp=40 allies=3 potion=True arrows=0 cover=True alarm=True post=gate time=day
- 方針=None 審判=hold_position [A5] alarm=true,arrows=0,allies>=3 「警報済みで味方が三人、矢が無いので持ち場を守る」 (round5_s1) | hp=82 enemy=troll distance=4 enemy_count=2 enemy_hp=60 allies=3 potion=False arrows=0 cover=True alarm=True post=gate time=night
- 方針=None 審判=hold_position [A5] alarm=true,arrows=0,allies>=3 「警報済・矢なし・味方3人以上で遠い敵には持ち場を守る」 (round5_s2) | hp=87 enemy=troll distance=9 enemy_count=4 enemy_hp=80 allies=3 potion=False arrows=0 cover=True alarm=True post=gate time=day
### a5_mage_unclear
- 方針=None 審判=melee_attack [L4+gap] enemy=mage,arrows=0,hp>=90 「矢は無いが体力十分で味方もいる、弱った魔術師へ詰めて討つ」 (round3_s1) | hp=93 enemy=mage distance=12 enemy_count=2 enemy_hp=30 allies=3 potion=True arrows=0 cover=False alarm=True post=gate time=day
- 方針=None 審判=take_cover [gap] enemy=mage,arrows=0,cover=true 「矢が無く魔術師は遠いので遮蔽で呪文を避ける」 (round2_s1) | hp=75 enemy=mage distance=6 enemy_count=1 enemy_hp=50 allies=3 potion=False arrows=0 cover=True alarm=True post=corridor time=day
### hp_ambiguous
- 方針=None 審判=raise_alarm [L2,L5+gap] alarm=false,allies=0,hp<=31 「夜に単独で傷も深い、オーク接近をまず知らせる」 (round5_s1) | hp=31 enemy=orc distance=3 enemy_count=1 enemy_hp=100 allies=0 potion=False arrows=5 cover=True alarm=False post=gate time=night
- 方針=None 審判=shoot [L1,L2+gap] enemy_hp<=10,distance>=7,arrows>=9 「重傷だが敵は遠く瀕死のゴブリン、射って仕留める」 (round2_s3) | hp=26 enemy=goblin distance=7 enemy_count=1 enemy_hp=10 allies=1 potion=False arrows=9 cover=False alarm=False post=wall time=day
### a5_hurt_conflict
- 方針=None 審判=drink_potion [L1] hp<=12,potion=true 「瀕死なので手持ちの回復薬を飲む」 (round3_s3) | hp=12 enemy=mage distance=5 enemy_count=1 enemy_hp=70 allies=3 potion=True arrows=0 cover=True alarm=True post=gate time=night
### a5_night_unclear
- 方針=None 審判=hold_position [A5] alarm=true,arrows=0,allies>=3 「警報済みで矢が無く味方が多いので持ち場を守る」 (round5_s1) | hp=85 enemy=goblin distance=7 enemy_count=1 enemy_hp=100 allies=3 potion=False arrows=0 cover=True alarm=True post=wall time=night
### mage_alarm_unclear
- 方針=None 審判=raise_alarm [L4,L5+gap] alarm=false,enemy=mage,enemy_count>=3 「魔術師を含む三体の襲来、まず警報を鳴らす」 (round5_s1) | hp=75 enemy=mage distance=6 enemy_count=3 enemy_hp=20 allies=3 potion=False arrows=18 cover=False alarm=False post=gate time=day

## 訊き直した状態(同じ状態を会話 3 本以上に訊いた。30 件のうち票が割れたもの 12 件)
- 票 {'hold_position': 3, 'retreat': 3, 'take_cover': 1} | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=True alarm=False post=gate time=night | hold_position「深手だが敵はなく、夜の門を空けず持ち場に留まる」 / retreat「深手で薬が無いので敵のいない今退く」 / retreat「重傷で薬も無いので退いて立て直す」 / hold_position「傷は深いが脅威が無く、門を空けられないので留まる」 / take_cover「重傷の夜、持ち場を離れず遮蔽に身を隠して見張る」 / retreat「夜に独りで重傷、薬も無いので退いて立て直す」 / hold_position「傷は深いが敵がおらず門を守り続ける」
- 票 {'shoot': 3, 'retreat': 1} | hp=31 enemy=goblin distance=9 enemy_count=3 enemy_hp=40 allies=1 potion=False arrows=5 cover=False alarm=True post=wall time=night | shoot「手負いだが敵は遠く、射るだけなら危険は小さい」 / retreat「深手で薬が無い夜なので射るより退く」 / shoot「城壁から遠いゴブリンを射る」 / shoot「敵は遠く警報済み、まだ射って戦える傷と見る」
- 票 {'raise_alarm': 2, 'drink_potion': 5} | hp=28 enemy=mage distance=10 enemy_count=2 enemy_hp=80 allies=2 potion=True arrows=10 cover=False alarm=False post=wall time=night | raise_alarm「深手だが魔術師はまだ遠い、先に警報を鳴らす」 / drink_potion「重傷で魔術師はまだ遠い、まず回復薬で持ち直す」 / raise_alarm「魔術師はまだ遠い、薬より先に警報を鳴らす」 / drink_potion「夜に重傷、敵は遠いのでまず回復薬を飲む」 / drink_potion「重傷で敵はまだ遠い、今のうちに回復薬を飲む」 / drink_potion「重傷で薬がある、敵が遠いうちに飲む」 / drink_potion「魔術師の射程内で重傷、味方もいるのでまず薬」
- 票 {'take_cover': 3, 'drink_potion': 1} | hp=44 enemy=goblin distance=11 enemy_count=3 enemy_hp=30 allies=0 potion=True arrows=0 cover=True alarm=True post=wall time=night | take_cover「夜に単独で矢もない、遮蔽に隠れて様子を見る」 / drink_potion「矢が無く敵は遠い、夜の三体に備え今のうちに回復する」 / take_cover「夜で矢が無く敵は遠い、遮蔽に隠れて待つ」 / take_cover「夜に単独で矢も無い、遮蔽に隠れて備える」
- 票 {'take_cover': 1, 'hold_position': 3} | hp=42 enemy=goblin distance=4 enemy_count=3 enemy_hp=60 allies=3 potion=False arrows=0 cover=True alarm=True post=gate time=day | take_cover「矢も薬も無く体力半分以下、遮蔽で門に踏み止まる」 / hold_position「矢が無く未接敵、警報済みで門を固めて待つ」 / hold_position「矢が無く敵は離れており、味方と門を固める」 / hold_position「矢が無く敵はまだ届かず、味方と門で迎え撃つ」
- 票 {'shoot': 3, 'raise_alarm': 1} | hp=84 enemy=mage distance=6 enemy_count=1 enemy_hp=40 allies=0 potion=True arrows=11 cover=True alarm=False post=gate time=day | shoot「魔術師単独なら警報より先に射て早く仕留める」 / shoot「弱った魔術師一体、警報より早く射て仕留める」 / raise_alarm「魔術師出現で警報未発、独りなので先に鳴らす」 / shoot「弱った魔術師一体、警報より先に射抜く」
- 票 {'hold_position': 3, 'retreat': 1} | hp=30 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=0 cover=False alarm=False post=gate time=night | hold_position「敵も代わりもいない、体力30なら門に残る」 / hold_position「深手だが敵がいないので門を離れず守る」 / hold_position「脅威が無く単独、門を空けずに持ち場を守る」 / retreat「重傷で薬が無く夜に単独なので退く」
- 票 {'retreat': 3, 'hold_position': 1} | hp=29 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=19 cover=True alarm=False post=wall time=day | retreat「深手で薬が無く味方が残るので退いて癒す」 / hold_position「深手だが脅威が無いので持ち場に留まる」 / retreat「重傷で薬が無く、味方が持ち場を守れるので退く」 / retreat「重傷で薬が無く、味方二人に任せて退く」
- 票 {'retreat': 3, 'hold_position': 1} | hp=30 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=12 cover=False alarm=False post=wall time=night | retreat「深手で薬が無いので敵のいない今退く」 / hold_position「深手だが脅威が無く、退く理由がないので持ち場に留まる」 / retreat「重傷で薬が無く、味方がいるので退いて癒す」 / retreat「重傷で薬が無く、壁は味方に任せて退く」
- 票 {'retreat': 1, 'hold_position': 3} | hp=32 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=20 cover=True alarm=False post=corridor time=day | retreat「深手で薬が無く味方が残るので退いて癒す」 / hold_position「脅威が無く傷も浅めなので持ち場を守る」 / hold_position「敵なしで重傷とまでは言えず持ち場を守る」 / hold_position「脅威が無く、深手とまでは言えないので持ち場を守る」
- 票 {'retreat': 1, 'hold_position': 3} | hp=23 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=15 cover=True alarm=False post=gate time=day | retreat「深手で薬が無いので退いて癒す」 / hold_position「敵なしで味方もいないので持ち場を守る」 / hold_position「敵なし・薬なし・味方なしなので持ち場を守る」 / hold_position「敵がおらず味方もいないので持ち場を守る」
- 票 {'retreat': 1, 'hold_position': 3} | hp=14 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=4 cover=True alarm=False post=gate time=day | retreat「重傷で薬が無いので敵のいない今のうちに退く」 / hold_position「敵なしで味方もいないので持ち場を守る」 / hold_position「敵なし・薬なし・味方なしなので持ち場を守る」 / hold_position「敵がおらず味方もいないので持ち場を守る」

## 根拠が gap に偏り、答えが割れている枝(輪が同じ状態を複数の会話に訊き直している。会話の癖か、状態の違いかは、訊き直しの票で分かる)
- 枝 troll_alarm: 審判の答え {'raise_alarm': 9, 'melee_attack': 1}
- 枝 wounded_no_threat: 審判の答え {'hold_position': 15, 'retreat': 25, 'take_cover': 1}
- 枝 no_arrows_hold: 審判の答え {'hold_position': 55, 'take_cover': 1}
- 枝 a1_night_split: 審判の答え {'shoot': 3, 'retreat': 3}
- 枝 wounded_drink: 審判の答え {'raise_alarm': 2, 'drink_potion': 11}
- 枝 night_no_arrows_cover: 審判の答え {'take_cover': 9, 'drink_potion': 1}
- 枝 troll_alone_cover: 審判の答え {'take_cover': 4, 'retreat': 1}
- 枝 mage_first_shoot: 審判の答え {'shoot': 7, 'raise_alarm': 1}
- 枝 hurt_handover: 審判の答え {'retreat': 9, 'hold_position': 1}
- 枝 group_alarm_unclear: 審判の答え {'shoot': 2, 'raise_alarm': 3, 'melee_attack': 2}
- 枝 a5_mage_unclear: 審判の答え {'take_cover': 1, 'melee_attack': 1}
- 枝 hurt_no_threat: 審判の答え {'retreat': 9, 'hold_position': 16}
- 枝 troll_alarm_raised: 審判の答え {'retreat': 7, 'hold_position': 2, 'shoot': 1, 'take_cover': 1}
- 枝 wounded_alarm_unclear: 審判の答え {'raise_alarm': 1, 'drink_potion': 2, 'melee_attack': 1, 'shoot': 2, 'retreat': 1}
- 枝 orc_alarm_unclear: 審判の答え {'shoot': 1, 'hold_position': 2, 'raise_alarm': 3}
- 枝 hp_ambiguous: 審判の答え {'shoot': 1, 'raise_alarm': 1}
- 枝 mage_no_arrows: 審判の答え {'melee_attack': 2, 'drink_potion': 1, 'hold_position': 1}

## 出力
`/home/claude/sekizui/jit/auto_runs/r2/policies/b5.py` に書く。書いたら「完了」とだけ返す。