# 翻訳の依頼 — 走り r2、第 3 版

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

## いまの方針(b2)
```python
"""走り r2 の方針、第 2 版(b2)。やり直し 1 回目。

帳簿: 審判のラベル 264 件、会話 6 本(round1_s1〜s3、round2_s1〜s3。以下 r1s1 … r2s3)。
b1 が答えた状態の行き先は、この版でも変わらない(b1 の枝の条件は動かさず、棄権していた所に
答えを足しただけ)。

前の版が門で落ちた理由と直し方
  前の版は追補 A1 を枝 a1_shoot_far 一本にした。A1 の範囲のうち b1 が棄権していた所
  (hp 31〜32、回復薬なし、敵 9 マス以上、矢あり)の帳簿は 6 件で、射る 3・退く 3。
  退くのは r2s1 の 2 件(hp31 ゴブリン d9、hp32 オーク d9)と r2s2 の 1 件(hp31 オーク 4 体 d10)で、
  r2s2 はこの範囲で射る 1・退く 1 に割れる。射る 3 件は、訊き直した一つの状態
  (hp31 ゴブリン 3 体 d9 矢 5 警報済み、夜)の票。この状態だけで射る 3・退く 1(75%)なので、
  この状態を含む枝は、どう切っても一致 80% に届かない。
  6 件はすべて夜で、退く側の決め手に time=night が挙がる(r2s1「深手で薬が無い夜なので射るより
  退く」、r2s2「深手で夜にオーク4体、無駄死にを避けて退く」)。根拠にも L6 が付く。
  そこで A1 を昼と夜に分けた。
    a1_shoot(昼、答える枝): A1 をそのまま読んだ規則(規律 (a))。帳簿の例は 0 件。
        hp>=33 と同じ読み(_fine)が射ると言う所だけで答え、警報・遮蔽・棄権になる所は答えない。
    a1_night_split(夜、番人): 上の 6 件。L6 と A1 がぶつかる所として棄権し、輪に回す。
  回復薬を持っている時は A1 の外とした。A1 は「回復薬が無くとも」退かない、という規則で、
  hp31・オーク d12・薬ありは r1s2 が飲む(下の wounded_drink に入る)。
  hp>=33 では A1 は既に shoot_far などと同じ答えなので、何も変えない。

この版で変えたこと
 1. A1 を上のとおり入れた。
 2. 「ひどく傷ついている」の上限を hp<=20 から hp<=24 に上げた(_HURT_MAX)。
    hp 21〜23 のラベル 9 件(会話 5 本)は、すべて L1 どおり。飲む 1(hp21 薬あり、r1s2、決め手
    hp<=21, potion=true)、退く 8(隣接トロル hp23 薬なしを r1s1 r2s1 r2s2 r2s3 の 4 本が
    すべて退く、hp23 オーク・hp22 ゴブリン・hp21 ゴブリンの退くが各 1、敵なし・味方 0 の退く 1)。
    決め手は hp<=30 / hp<=23 / hp<=22 と potion=false。敵のいる所で L1 から外れる最初の例は
    hp26(r2s3 が 7 マス先の瀕死のゴブリンを射る)。線は 23 と 26 の間の 24 に置いた。
    hp 25〜32 は wounded(下の 5)として別に扱う。
 3. 番人 hurt_vs_alarm(ひどい傷とトロル・警報未)を距離で分けた。
    新しい枝 hurt_troll_alarm: 3 マス以上 → raise_alarm。3 件・会話 3 本(r1s3 d12、r2s2 d10、
        r2s3 d5)・一致 3/3。決め手 alarm=false, enemy=troll, distance>=12 / >=10 / >=5
        (「まだ遠い、先に警報」)。薬を持っていても警報が先(r1s3)。
    隣接は L1 に通す: hp14 d1 薬あり → 飲む(r2s3、決め手 distance=1)、hp23 d1 薬なし → 退く
        (上の 4 本)。線は隣接 1 と、警報側の最も近い 5 の間の 3 に置いた。
 4. 新しい枝 hurt_handover: ひどい傷・薬なし・敵なし・近くの味方 1 以上 → retreat。
    9 件・会話 3 本(r1s3 3、r2s1 2、r2s3 4)・一致 9/9。決め手 potion=false と
    allies>=1 / >=2 / >=3、hp<=15 など。理由は「門を味方に任せて退く」。
    味方 0 は持ち場 2(r2s3)・退く 2(r2s1, r2s2)で割れる → 番人 hurt_no_threat のまま。
 5. hp 25〜32(wounded)。
    新しい枝 wounded_drink: 回復薬あり → drink_potion(警報未の深刻な脅威がいる時は除く)。
        6 件・会話 4 本(r1s2 1、r1s3 1、r2s1 3、r2s2 1)・一致 6/6。決め手 potion=true と
        hp<=30 / <=31 / <=33。根拠は 5 件が L1 だけ。飲むの最も高い例は hp31(r1s2・r2s1)。
        hp>=33 で薬があって飲んだ例は無い(no_threat_hold 45/45)。hp 21 の飲む 1 件は 2 の hurt_drink。
    番人 wounded_alarm_unclear: 警報未の深刻な脅威(トロル、魔術師、敵 4 以上、味方 0 で敵 3、
        オーク 2 体以上、ゴブリン 3 体以上)がいる所。警報 3・飲む 1(r1s1 1、r2s3 3)、根拠は全件 gap。
    番人 wounded_no_threat: 薬なし・敵なし。持ち場 5・退く 8 で、退く 8 のうち 6 件が r2s1。
        訊き直した hp28・味方 0・夜の門の状態は 2 対 2。味方 1 以上に絞っても退く 6・持ち場 2(75%)。
    番人 hp_ambiguous: 薬なし・敵あり・A1 の外。射る 2 件(1 件は gap)で、規律 (c) に届かない。
 6. 番人 no_arrows_cover(離れた敵・矢 0・遮蔽あり 26 件)を昼夜で分けた。
    夜 → take_cover(新しい枝 night_no_arrows_cover): 7 件・会話 4 本(r1s1 1、r2s1 2、r2s2 2、
        r2s3 2)・一致 7/7。決め手 time=night, arrows=0, cover=true。根拠 L6(4 件は gap なし)。
    昼 → hold_position: 19 件・会話 6 本・一致 18/19。遮蔽なしの no_arrows_hold と同じ規則
        (矢が無く敵が離れていれば持ち場で待つ)なので同じ枝に入れた。外れる 1 件は r1s2 の
        take_cover(hp42、決め手 hp<=42, potion=false)だが、昼・遮蔽ありで hp37 の持ち場
        (r2s1)もあるので線にしない。r1s2 はこの枝で持ち場が多数のまま。
 7. 番人 mage_alarm_unclear(警報未の魔術師 20 件)を分けた。
    隣接 → melee_attack: 4 件・会話 3 本(r1s3 1、r2s1 2、r2s3 1)・一致 4/4。決め手 enemy=mage,
        distance=1(「隣の魔術師を警報より先に斬る」)。警報済みの隣接と同じ規則(L2+L4)なので
        mage_melee に入れた。
    矢 0 → raise_alarm(新しい枝 mage_no_arrows_alarm): 4 件・会話 2 本(r1s1 1、r2s2 3)・
        一致 4/4。決め手 enemy=mage, alarm=false, arrows=0(「討つ手段が無く、まず警報」)。
        3 件は根拠 L4,L5 で gap なし。
    7 マス以上・矢あり → raise_alarm(新しい枝 mage_far_alarm): 5 件・会話 3 本(r1s3 1、
        r2s1 2、r2s2 2)・一致 5/5。決め手 distance>=12 / >=7、arrows<=1、enemy_count>=3
        (「魔術師がまだ遠いうちに警報」)。昼に 6 マス以内・矢ありは射る 5/5(距離 2, 3, 6, 6, 6)
        なので、線は 6 と 7 の間。
    昼・2〜6 マス・敵 2 以下・矢あり → shoot(新しい枝 mage_first_shoot): 5 件・会話 3 本
        (r1s2 2、r2s1 2、r2s2 1)・一致 5/5。決め手 enemy=mage, distance<=3 / <=2,
        arrows>=6..20, enemy_hp<=10 / <=30(「近い魔術師は警報より先に射て仕留める」)。
    残り → 番人 mage_alarm_unclear: 夜の 3〜6 マス 2 件は r2s3 がどちらも警報(決め手 time=night、
        根拠 gap、会話 1 本)。敵 3 の近い魔術師は例が無い。
 8. 番人 troll_alarm_raised(警報済みのトロル 15 件)を味方の数で分けた。
    味方あり・隣接 → melee_attack(新しい枝 troll_melee_allies): 2 件・会話 2 本(r2s1, r2s2)・
        一致 2/2。根拠はどちらも L2,L3 で gap なし → 規律 (c)。決め手 distance=1, allies>=1 / >=2
        (「味方がいて一人ではない」)。
    味方あり・離れて矢あり → shoot(新しい枝 troll_shoot_allies): 5 件・会話 4 本(r1s1、r1s3、
        r2s2 2、r2s3)・一致 5/5。決め手 distance>=2..8, arrows>=1..14, allies>=1 / >=2。
    味方 0・離れて・遮蔽あり・夜 → take_cover(新しい枝 troll_alone_cover): 4 件・会話 3 本
        (r1s2 2、r2s1、r2s3)・一致 4/4。決め手 enemy=troll, allies=0 と cover=true / time=night
        (「単独でトロルに挑めず、遮蔽で援軍を待つ」)。4 件とも夜で遮蔽あり。
    残り 4 件 → 番人 troll_alarm_raised: 味方 0 の隣接は退く 2(r2s1, r2s3、根拠 gap)、
        味方ありで矢 0 は持ち場 1・退く 1。
 9. 番人 orc_alarm_unclear(警報未のオーク 12 件、すべて 2 体)を昼夜で分けた。
    夜・味方 1 以下・弱っていない(enemy_hp>30)→ raise_alarm(新しい枝 orc_pair_night_alarm):
        5 件・会話 5 本・一致 5/5(訊き直した hp82 隣接・味方 0 の状態を r1s2 r2s1 r2s2 r2s3 が
        すべて警報、r1s3 の味方 1・d6 も警報)。決め手 alarm=false, allies=0, time=night
        (「夜に一人でオーク二体なので戦うより警報」)。夜でも味方 2 なら r1s3 が隣接を斬り
        (決め手 allies>=2)、弱ったオークは r2s3 が射る(決め手 enemy_hp<=20、昼の r2s3 も
        enemy_hp<=30 を決め手に射る)。
    昼・離れて・矢あり → shoot(新しい枝 orc_pair_day_shoot): 3 件・会話 2 本(r2s1 1、r2s3 2)・
        一致 3/3。決め手 distance>=4 / >=9 / >=12、arrows>=3..8、allies / enemy_hp<=30。
    残り 4 件 → 番人 orc_alarm_unclear(夜・味方 2 の隣接 斬る 1、夜・弱ったオーク 射る 1、
        夜・味方 1・矢 0・enemy_hp30 警報 1、昼・矢 0 警報 1)。敵 3・味方ありは例が無い。

b2 で数え直した帳簿(答える枝、件数・一致・会話)
    no_threat_hold         45  45/45  6 本      L7      敵なし・hp>=33 → hold_position
    no_arrows_hold         29  28/29  6 本      gap     離れた敵・矢 0・(遮蔽なし、または昼) → hold_position
    shoot_far              27  26/27  5 本      L2      離れたゴブリン/オーク・矢あり → shoot
    horde_alarm            17  17/17  6 本      L5      警報未・敵 4 以上 → raise_alarm
    melee_adjacent         12  12/12  5 本      L2      隣接のゴブリン/オーク → melee_attack
    hurt_handover           9   9/9   3 本      L1+L7   hp<=24・薬なし・敵なし・味方あり → retreat
    hurt_retreat            8   8/8   5 本以上  L1      hp<=24・薬なし・敵あり → retreat
    night_no_arrows_cover   7   7/7   4 本      L6      離れた敵・矢 0・遮蔽あり・夜 → take_cover
    wounded_drink           6   6/6   4 本      L1      hp 25〜32・薬あり → drink_potion
    troll_alarm             5   5/5   3 本      L5+L3   トロル・警報未 → raise_alarm
    troll_shoot_allies      5   5/5   4 本      L2+L3   警報済みトロル・味方あり・離れて矢あり → shoot
    mage_far_alarm          5   5/5   3 本      L5+L4   警報未の魔術師・7 マス以上・矢あり → raise_alarm
    mage_first_shoot        5   5/5   3 本      L4+L2   警報未の魔術師・昼・2〜6 マス・敵 2 以下 → shoot
    orc_pair_night_alarm    5   5/5   5 本      L5+L6   警報未のオーク 2 体・夜・味方 1 以下 → raise_alarm
    hurt_drink              4   4/4   2 本以上  L1      hp<=24・薬あり → drink_potion
    mage_melee              4   4/4   3 本      L2+L4   隣接の魔術師 → melee_attack
    mage_no_arrows_alarm    4   4/4   2 本      L5+L4   警報未の魔術師・離れて矢 0 → raise_alarm
    troll_alone_cover       4   4/4   3 本      L3+L6   警報済みトロル・味方 0・離れて・遮蔽・夜 → take_cover
    outnumbered_alarm       3   3/3   2 本      L5      警報未・敵 3・味方 0 → raise_alarm
    mage_shoot              3   3/3   2 本      L2+L4   離れた魔術師(警報済み)・矢あり → shoot
    hurt_troll_alarm        3   3/3   3 本      L5+L3   hp<=24・トロル・警報未・3 マス以上 → raise_alarm
    orc_pair_day_shoot      3   3/3   2 本      L2      警報未のオーク 2 体・昼・離れて矢あり → shoot
    troll_melee_allies      2   2/2   2 本      L2+L3   警報済みトロル・味方あり・隣接 → melee_attack
    a1_shoot                0                   A1      hp 31〜32・薬なし・敵 9 マス以上・矢あり・昼 → shoot

棄権の番人(割れている所、証拠が足りない所。輪が審判に訊き直す所)
    wounded_no_threat      13  hp 25〜32・薬なし・敵なし(持ち場 5 / 退く 8、退くの 6 件は r2s1)
    a1_night_split          6  A1 の範囲の夜(射る 3 / 退く 3。上を見よ)
    group_alarm_unclear     6  警報未のゴブリン 3 体・味方あり(斬る 1 / 射る 2 / 警報 1 / 持ち場 2)
    wounded_alarm_unclear   4  hp 25〜32 と警報未の深刻な脅威(警報 3 / 飲む 1、全件 gap)
    hurt_no_threat          4  hp<=24・薬なし・敵なし・味方 0(持ち場 2 / 退く 2)
    troll_alarm_raised      4  警報済みトロルの残り(退く 3 / 持ち場 1)
    orc_alarm_unclear       4  警報未のオーク 2 体の残り(斬る 1 / 射る 1 / 警報 2)、オーク 3 体・味方あり
    mage_no_arrows          4  離れた魔術師(警報済み)・矢 0(斬る 2 / 遮蔽 2、全件 gap)
    hp_ambiguous            2  hp 25〜32・薬なし・敵あり・A1 の外(射る 2、うち 1 件 gap)。
                               A1 の昼でも hp>=33 の読みが射ると言わない所
    mage_alarm_unclear      2  警報未の魔術師・夜・2〜6 マス(警報 2、r2s3 のみ・gap)、敵 3 の近い魔術師
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
_HURT_MAX = 24      # これ以下はひどい(hp21〜23 は 9/9 が L1、hp26 から外れる)
_FINE_MIN = 33      # これ以上はひどくない(b1 のまま)

# 追補 A1
_A1_HP_MIN = 31
_A1_DIST_MIN = 9

# ひどい傷と警報未のトロル: この距離以上なら警報(隣接 1 は L1、警報側は 5 以上)
_HURT_TROLL_ALARM_DIST = 3

# 警報未の群れ
_HORDE_MIN = 4          # 敵がこれ以上なら警報(敵 3 は割れる、4・5 は一致)
_OUTNUMBERED_MIN = 3    # 味方 0 で敵がこれ以上なら警報

# 警報未の魔術師: この距離以上なら警報(昼の 6 以内は射る)
_MAGE_FAR_MIN = 7

# 弱った敵(審判の決め手 enemy_hp<=30 / <=20)
_WEAK_HP_MAX = 30


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


def _serious_unalarmed(s):
    """警報未で、hp>=33 なら警報か棄権になる敵か(敵がいて alarm=false の時だけ呼ぶ)。"""
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
            and s["distance"] >= _HURT_TROLL_ALARM_DIST):
        return ("raise_alarm", "hurt_troll_alarm")

    if s["potion"]:
        return ("drink_potion", "hurt_drink")
    if enemy == "none":
        if s["allies"] >= 1:
            return ("retreat", "hurt_handover")
        return (None, "hurt_no_threat")
    return ("retreat", "hurt_retreat")


def _wounded(s):
    """hp 25〜32: ひどいかどうかが会話で割れる所。"""
    enemy = s["enemy"]

    if enemy != "none" and not s["alarm"] and _serious_unalarmed(s):
        return (None, "wounded_alarm_unclear")

    if s["potion"]:
        return ("drink_potion", "wounded_drink")

    if enemy == "none":
        return (None, "wounded_no_threat")

    # 追補 A1: hp>=31、薬なし、敵 9 マス以上、矢あり → 退かずに射る
    if (s["hp"] >= _A1_HP_MIN and s["distance"] >= _A1_DIST_MIN
            and s["arrows"] >= 1):
        if s["time"] == "night":
            return (None, "a1_night_split")
        act, _name = _fine(s)
        if act == "shoot":
            return ("shoot", "a1_shoot")
        return (None, "hp_ambiguous")

    return (None, "hp_ambiguous")


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
            return (None, "troll_alarm_raised")
        if dist >= 2 and cover and night:
            return ("take_cover", "troll_alone_cover")
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
            if dist >= _MAGE_FAR_MIN:
                return ("raise_alarm", "mage_far_alarm")
            if night or count >= 3:
                return (None, "mage_alarm_unclear")
            return ("shoot", "mage_first_shoot")

        if enemy == "orc" and count >= 2:
            if count == 2:
                if night:
                    if allies <= 1 and s["enemy_hp"] > _WEAK_HP_MAX:
                        return ("raise_alarm", "orc_pair_night_alarm")
                elif dist >= 2 and arrows >= 1:
                    return ("shoot", "orc_pair_day_shoot")
            return (None, "orc_alarm_unclear")

        if enemy == "goblin" and count >= 3:
            return (None, "group_alarm_unclear")
        # 単独のオーク、ゴブリン 1〜2 体は深刻な脅威ではない → L2 へ

    # --- L2 (+ L4 魔術師) ---
    if dist == 1:
        if enemy == "mage":
            return ("melee_attack", "mage_melee")
        return ("melee_attack", "melee_adjacent")

    # 離れている(distance>=2)
    if arrows <= 0:
        if enemy == "mage":
            return (None, "mage_no_arrows")
        if cover and night:
            return ("take_cover", "night_no_arrows_cover")
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

## 熱さの帳簿(審判のラベル 359 件、会話 9 本を、いまの方針の枝ごとに数えた)

| 枝 | 件数 | 会話 | 方針の答え | 一致 | 会話の多数が方針と同じ | 審判の答え | 根拠 | 決め手(多い順) |
|---|---|---|---|---|---|---|---|---|
| no_threat_hold | 51 | 9 | hold_position | 51/51 | 9/9 | {'hold_position': 51} | L7 51, L1 5; gap 5 | enemy=none 51, hp>=40 2, hp>=45 2, hp>=44 1 |
| no_arrows_hold | 35 | 9 | hold_position | 34/35 | 9/9 | {'hold_position': 34, 'take_cover': 1} | L6 1; gap 35 | arrows=0 35, distance>=2 13, enemy=goblin 10, distance>=8 6 |
| shoot_far | 33 | 8 | shoot | 32/33 | 7/8 | {'shoot': 32, 'take_cover': 1} | L2 32, L6 1, A1 1; gap 1 | distance>=2 16, arrows>=1 10, distance>=6 4, distance>=4 4 |
| wounded_no_threat | 22 | 8 | None | -/- | -/8 | {'hold_position': 10, 'retreat': 11, 'take_cover': 1} | L7 22, L1 20, L6 3; gap 22 | potion=false 12, enemy=none 10, hp<=28 7, hp<=30 6 |
| horde_alarm | 18 | 7 | raise_alarm | 18/18 | 7/7 | {'raise_alarm': 18} | L5 18, L2 11, L6 4; gap 15 | alarm=false 18, enemy_count>=5 11, allies=0 7, enemy_count>=4 7 |
| wounded_alarm_unclear | 14 | 5 | None | -/- | -/5 | {'raise_alarm': 8, 'drink_potion': 4, 'melee_attack': 1, 'shoot': 1} | L5 10, L1 10, L2 4; gap 14 | alarm=false 8, enemy=mage 5, distance>=10 4, potion=true 4 |
| hurt_retreat | 13 | 8 | retreat | 13/13 | 8/8 | {'retreat': 13} | L1 13, L3 4, L5 3; gap 5 | potion=false 12, hp<=30 6, hp<=22 4, enemy=troll 3 |
| orc_alarm_unclear | 13 | 7 | None | -/- | -/7 | {'melee_attack': 3, 'raise_alarm': 8, 'shoot': 1, 'hold_position': 1} | L5 10, L2 8, L6 5; gap 9 | alarm=false 8, time=night 4, enemy_count>=3 4, distance=1 3 |
| melee_adjacent | 12 | 5 | melee_attack | 12/12 | 5/5 | {'melee_attack': 12} | L2 12; gap 1 | distance=1 7, distance<=1 5, enemy_hp<=10 3, hp>=40 1 |
| hurt_no_threat | 12 | 6 | None | -/- | -/6 | {'retreat': 6, 'hold_position': 6} | L1 12, L7 9, L0 1; gap 12 | potion=false 6, enemy=none 6, allies=0 5, hp<=30 2 |
| group_alarm_unclear | 11 | 7 | None | -/- | -/7 | {'melee_attack': 1, 'shoot': 5, 'raise_alarm': 2, 'hold_position': 3} | L2 7, L5 4, L6 2; gap 6 | enemy=goblin 4, distance>=2 3, arrows=0 3, allies>=3 2 |
| night_no_arrows_cover | 10 | 7 | take_cover | 9/10 | 6/7 | {'take_cover': 9, 'drink_potion': 1} | L6 9, L1 1; gap 5 | arrows=0 9, time=night 9, cover=true 8, hp<=44 1 |
| hurt_drink | 9 | 6 | drink_potion | 9/9 | 6/6 | {'drink_potion': 9} | L1 9, L2 1, L5 1; gap 3 | potion=true 9, hp<=21 4, enemy=none 3, hp<=12 2 |
| troll_alarm_raised | 9 | 7 | None | -/- | -/7 | {'hold_position': 2, 'retreat': 4, 'shoot': 3} | L3 7, L2 6, L6 2; gap 7 | enemy=troll 5, allies=0 3, arrows=0 2, hp>=31 2 |
| hurt_handover | 9 | 3 | retreat | 9/9 | 3/3 | {'retreat': 9} | L7 9, L1 9; gap 9 | potion=false 9, allies>=2 4, hp<=15 3, allies>=1 2 |
| mage_no_arrows | 8 | 6 | None | -/- | -/6 | {'melee_attack': 5, 'take_cover': 3} | L4 5, L2 2, L0 1; gap 8 | enemy=mage 8, arrows=0 8, cover=true 3, hp>=90 2 |
| mage_first_shoot | 8 | 6 | shoot | 7/8 | 5/6 | {'shoot': 7, 'raise_alarm': 1} | L4 8, L5 7, L2 5; gap 8 | enemy=mage 8, arrows>=11 3, enemy_count=1 1, enemy_hp<=10 1 |
| troll_alarm | 7 | 5 | raise_alarm | 6/7 | 4/5 | {'raise_alarm': 6, 'melee_attack': 1} | L5 6, L3 5, L2 2; gap 4 | enemy=troll 6, alarm=false 6, allies=0 2, arrows=0 1 |
| a1_night_split | 6 | 4 | None | -/- | -/4 | {'shoot': 3, 'retreat': 3} | L2 4, L1 3, L6 2; gap 5 | distance>=2 2, hp<=33 2, potion=false 2, time=night 2 |
| wounded_drink | 6 | 4 | drink_potion | 6/6 | 4/4 | {'drink_potion': 6} | L1 6, L2 1; gap 1 | potion=true 6, hp<=30 3, enemy=none 2, hp<=31 1 |
| mage_melee | 6 | 5 | melee_attack | 6/6 | 5/5 | {'melee_attack': 6} | L2 6, L4 6, L5 4; gap 5 | enemy=mage 6, distance<=1 4, distance=1 2, enemy_hp<=30 2 |
| troll_shoot_allies | 5 | 4 | shoot | 5/5 | 4/4 | {'shoot': 5} | L2 5, L3 4; gap 2 | allies>=2 3, distance>=2 3, arrows>=14 2, distance>=4 1 |
| troll_alone_cover | 5 | 4 | take_cover | 4/5 | 3/4 | {'take_cover': 4, 'retreat': 1} | L3 5, L6 5, L2 2; gap 5 | enemy=troll 5, allies=0 5, time=night 3, cover=true 2 |
| orc_pair_night_alarm | 5 | 5 | raise_alarm | 5/5 | 5/5 | {'raise_alarm': 5} | L2 5, L5 5, L6 4; gap 5 | alarm=false 5, time=night 5, allies=0 4, enemy=orc 1 |
| mage_far_alarm | 5 | 3 | raise_alarm | 5/5 | 3/3 | {'raise_alarm': 5} | L5 5, L4 5, L2 3; gap 5 | alarm=false 5, enemy=mage 3, enemy_count>=3 3, arrows<=1 1 |
| outnumbered_alarm | 4 | 3 | raise_alarm | 4/4 | 3/3 | {'raise_alarm': 4} | L5 4, L6 3, L2 2; gap 4 | enemy_count>=3 4, allies=0 4, alarm=false 4 |
| mage_no_arrows_alarm | 4 | 2 | raise_alarm | 4/4 | 2/2 | {'raise_alarm': 4} | L5 4, L4 4, L6 1; gap 1 | enemy=mage 4, alarm=false 4, arrows=0 3, enemy_count>=3 1 |
| mage_shoot | 4 | 3 | shoot | 4/4 | 3/3 | {'shoot': 4} | L2 4, L4 4 | enemy=mage 4, arrows>=4 2, distance>=6 1, arrows>=7 1 |
| orc_pair_day_shoot | 4 | 3 | shoot | 4/4 | 3/3 | {'shoot': 4} | L2 4, L5 2; gap 3 | enemy_hp<=30 2, arrows>=3 1, allies>=3 1, distance>=12 1 |
| hurt_troll_alarm | 3 | 3 | raise_alarm | 3/3 | 3/3 | {'raise_alarm': 3} | L1 3, L5 3, L3 1; gap 3 | alarm=false 3, enemy=troll 3, distance>=12 1, distance>=10 1 |
| hp_ambiguous | 3 | 3 | None | -/- | -/3 | {'shoot': 2, 'retreat': 1} | L2 2, L1 2; gap 1 | distance>=2 1, arrows=18 1, enemy=goblin 1, enemy_hp<=10 1 |
| mage_alarm_unclear | 3 | 2 | None | -/- | -/2 | {'raise_alarm': 3} | L5 3, L4 3, L6 2; gap 3 | enemy=mage 3, alarm=false 3, time=night 2, allies=0 1 |
| troll_melee_allies | 2 | 2 | melee_attack | 2/2 | 2/2 | {'melee_attack': 2} | L3 2, L2 2 | enemy=troll 2, distance<=1 1, allies>=1 1, distance=1 1 |

## 食い違いと棄権の例(全部。[根拠] 決め手 「理由」 会話)
### no_arrows_hold
- 方針=hold_position 審判=take_cover [gap] hp<=42,potion=false,arrows=0 「矢も薬も無く体力半分以下、遮蔽で門に踏み止まる」 (round1_s2) | hp=42 enemy=goblin distance=4 enemy_count=3 enemy_hp=60 allies=3 potion=False arrows=0 cover=True alarm=True post=gate time=day
### shoot_far
- 方針=shoot 審判=take_cover [L2,L6+gap] time=night,enemy_count>=5,allies=0 「夜に一人で五体相手なので遮蔽で援軍を待つ」 (round2_s1) | hp=99 enemy=goblin distance=3 enemy_count=5 enemy_hp=60 allies=0 potion=True arrows=12 cover=True alarm=True post=gate time=night
### wounded_no_threat
- 方針=None 審判=hold_position [L0,L7+gap] enemy=none,post=gate 「深手だが敵はなく、夜の門を空けず持ち場に留まる」 (round1_s1) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=True alarm=False post=gate time=night
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,allies=0,hp>=30 「敵も代わりもいない、体力30なら門に残る」 (round1_s3) | hp=30 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=0 cover=False alarm=False post=gate time=night
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp>=32,allies=1 「重傷とまでは言えず脅威も無いので持ち場を守る」 (round2_s2) | hp=32 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=2 cover=True alarm=False post=gate time=day
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,allies=0,hp<=28 「傷は深いが脅威が無く、門を空けられないので留まる」 (round2_s3) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=True alarm=False post=gate time=night
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp>=31 「脅威が無く、ひどい傷とまでは言えず留まる」 (round2_s3) | hp=31 enemy=none distance=None enemy_count=0 enemy_hp=None allies=3 potion=False arrows=15 cover=False alarm=False post=gate time=night
- 方針=None 審判=hold_position [L7+gap] enemy=none,hp<=26,potion=false 「手負いだが脅威は無い、まだ持ち場を守れる」 (round3_s1) | hp=26 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=8 cover=False alarm=False post=gate time=night
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp<=28 「傷は深いが敵がおらず門を守り続ける」 (round3_s3) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=True alarm=False post=gate time=night
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp<=25 「重傷だが敵がいないので持ち場を守る」 (round3_s3) | hp=25 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=1 cover=False alarm=False post=gate time=night
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp<=28 「傷は深いが敵がいないので持ち場を守る」 (round3_s3) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=0 cover=True alarm=False post=wall time=day
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp<=28 「傷は深いが敵がいないので持ち場を守る」 (round3_s3) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=4 cover=False alarm=False post=gate time=day
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false,allies>=2 「深手で薬が無く味方が残るので退いて癒す」 (round2_s1) | hp=29 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=19 cover=True alarm=False post=wall time=day
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false 「深手で薬が無いので敵のいない今退く」 (round2_s1) | hp=30 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=12 cover=False alarm=False post=wall time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false,allies>=2 「深手で薬が無く味方が残るので退く」 (round2_s1) | hp=26 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=16 cover=False alarm=False post=corridor time=day
- 方針=None 審判=retreat [L1,L7+gap] hp<=33,potion=false,allies>=2 「深手で薬が無く味方が残るので退いて癒す」 (round2_s1) | hp=32 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=20 cover=True alarm=False post=corridor time=day
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false 「深手で薬が無いので敵のいない今退く」 (round2_s1) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=True alarm=False post=gate time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false,time=night 「深手で薬が無い夜なので退く」 (round2_s1) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=7 cover=False alarm=True post=wall time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false 「重傷で薬も無いので退いて立て直す」 (round2_s2) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=True alarm=False post=gate time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=28,potion=false,allies>=1 「重傷で薬が無い、持ち場は味方に任せて退く」 (round2_s3) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=3 cover=False alarm=False post=wall time=day
- 方針=None 審判=retreat [L1,L6,L7+gap] hp<=28,potion=false,time=night 「夜に独りで重傷、薬も無いので退いて立て直す」 (round3_s2) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=True alarm=False post=gate time=night
- 方針=None 審判=retreat [L1,L6,L7+gap] hp<=27,potion=false,time=night 「夜に独りで重傷、薬も無いので退く」 (round3_s2) | hp=27 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=11 cover=False alarm=False post=gate time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=25,potion=false,arrows=0 「重傷で薬も矢も無い、敵のいない今退く」 (round3_s2) | hp=25 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=0 cover=True alarm=False post=wall time=day
- 方針=None 審判=take_cover [L1,L6,L7+gap] hp<=28,time=night,cover=true 「重傷の夜、持ち場を離れず遮蔽に身を隠して見張る」 (round3_s1) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=True alarm=False post=gate time=night
### wounded_alarm_unclear
- 方針=None 審判=drink_potion [L1,L5+gap] hp<=26,potion=true,enemy=goblin 「重傷で薬がある、ゴブリン相手なら回復が先」 (round2_s3) | hp=26 enemy=goblin distance=3 enemy_count=3 enemy_hp=90 allies=1 potion=True arrows=20 cover=True alarm=False post=gate time=night
- 方針=None 審判=drink_potion [L1+gap] hp<=28,potion=true,distance>=10 「重傷で魔術師はまだ遠い、まず回復薬で持ち直す」 (round3_s1) | hp=28 enemy=mage distance=10 enemy_count=2 enemy_hp=80 allies=2 potion=True arrows=10 cover=False alarm=False post=wall time=night
- 方針=None 審判=drink_potion [L1,L2+gap] hp<=30,potion=true 「hp30は重傷と見て、隣接中でも薬を飲む」 (round3_s2) | hp=30 enemy=orc distance=1 enemy_count=2 enemy_hp=30 allies=2 potion=True arrows=2 cover=True alarm=False post=gate time=day
- 方針=None 審判=drink_potion [L1,L5+gap] hp<=28,potion=true,distance>=10 「夜に重傷、敵は遠いのでまず回復薬を飲む」 (round3_s3) | hp=28 enemy=mage distance=10 enemy_count=2 enemy_hp=80 allies=2 potion=True arrows=10 cover=False alarm=False post=wall time=night
- 方針=None 審判=melee_attack [L2,L4+gap] enemy=mage,distance<=1,enemy_hp<=20 「隣接した瀕死の魔術師を飲むより先に仕留める」 (round3_s1) | hp=30 enemy=mage distance=1 enemy_count=1 enemy_hp=20 allies=1 potion=True arrows=3 cover=True alarm=False post=gate time=day
- 方針=None 審判=raise_alarm [L4,L5+gap] enemy=mage,alarm=false,distance>=10 「深手だが魔術師はまだ遠い、先に警報を鳴らす」 (round1_s1) | hp=28 enemy=mage distance=10 enemy_count=2 enemy_hp=80 allies=2 potion=True arrows=10 cover=False alarm=False post=wall time=night
- 方針=None 審判=raise_alarm [L2,L5,L6+gap] alarm=false,enemy_count>=3,allies=0 「夜に単独で三体、射るより先に警報を鳴らす」 (round2_s3) | hp=31 enemy=goblin distance=7 enemy_count=3 enemy_hp=40 allies=0 potion=False arrows=17 cover=True alarm=False post=wall time=night
- 方針=None 審判=raise_alarm [L1,L5+gap] alarm=false,enemy_count>=3,allies=0 「単独でオーク三体、助けを呼ぶのが生存の道」 (round2_s3) | hp=27 enemy=orc distance=3 enemy_count=3 enemy_hp=70 allies=0 potion=True arrows=7 cover=True alarm=False post=corridor time=day
- 方針=None 審判=raise_alarm [L5+gap] alarm=false,enemy_count>=4,enemy=mage 「魔術師含む四体に警報が未だ、退く前に鳴らす」 (round3_s1) | hp=29 enemy=mage distance=7 enemy_count=4 enemy_hp=60 allies=2 potion=False arrows=14 cover=True alarm=False post=corridor time=day
- 方針=None 審判=raise_alarm [L1,L5+gap] enemy=mage,alarm=false,arrows=0 「魔術師出現で警報未発、矢も無く先に鳴らす」 (round3_s2) | hp=30 enemy=mage distance=8 enemy_count=2 enemy_hp=30 allies=2 potion=False arrows=0 cover=False alarm=False post=gate time=day
- 方針=None 審判=raise_alarm [L1,L4,L5+gap] enemy=mage,alarm=false,distance>=10 「魔術師はまだ遠い、薬より先に警報を鳴らす」 (round3_s2) | hp=28 enemy=mage distance=10 enemy_count=2 enemy_hp=80 allies=2 potion=True arrows=10 cover=False alarm=False post=wall time=night
- 方針=None 審判=raise_alarm [L1,L5+gap] alarm=false,enemy_count>=4,distance>=8 「退く前に、敵が遠い今のうち警報を鳴らす」 (round3_s3) | hp=25 enemy=goblin distance=8 enemy_count=4 enemy_hp=20 allies=0 potion=False arrows=13 cover=False alarm=False post=gate time=day
- 方針=None 審判=raise_alarm [L1,L5+gap] enemy=troll,alarm=false,distance>=8 「トロル出現、退く前に遠い内に警報を鳴らす」 (round3_s3) | hp=26 enemy=troll distance=8 enemy_count=1 enemy_hp=100 allies=3 potion=False arrows=0 cover=True alarm=False post=gate time=day
- 方針=None 審判=shoot [L1,L2+gap] hp>=31,distance>=7,arrows>=19 「hp31は重傷と見ず、近づくゴブリンを射る」 (round3_s2) | hp=31 enemy=goblin distance=7 enemy_count=4 enemy_hp=60 allies=3 potion=True arrows=19 cover=False alarm=False post=wall time=day
### orc_alarm_unclear
- 方針=None 審判=hold_position [gap] arrows=0,distance>=9 「矢が無く敵は遠い、持ち場で迎え撃つ」 (round3_s2) | hp=64 enemy=orc distance=9 enemy_count=2 enemy_hp=70 allies=1 potion=True arrows=0 cover=True alarm=False post=gate time=day
- 方針=None 審判=melee_attack [L2,L5,L6+gap] distance=1,hp>=91,allies>=2 「味方2人と体力十分、隣接オークを斬る」 (round1_s3) | hp=91 enemy=orc distance=1 enemy_count=2 enemy_hp=60 allies=2 potion=True arrows=0 cover=False alarm=False post=gate time=night
- 方針=None 審判=melee_attack [L2] distance=1,enemy_hp<=20 「隣接したオークは瀕死、近接で仕留める」 (round3_s2) | hp=94 enemy=orc distance=1 enemy_count=2 enemy_hp=20 allies=0 potion=False arrows=20 cover=True alarm=False post=gate time=day
- 方針=None 審判=melee_attack [L2] distance=1,allies>=3 「隣接したオークと味方と共に近接で戦う」 (round3_s2) | hp=95 enemy=orc distance=1 enemy_count=2 enemy_hp=70 allies=3 potion=False arrows=4 cover=True alarm=False post=gate time=night
- 方針=None 審判=raise_alarm [L5] alarm=false,allies=0,enemy_count>=2 「味方も矢も無く二体のオークが来るので警報」 (round2_s1) | hp=83 enemy=orc distance=7 enemy_count=2 enemy_hp=70 allies=0 potion=True arrows=0 cover=True alarm=False post=wall time=day
- 方針=None 審判=raise_alarm [L5,L6] alarm=false,time=night,arrows=0 「夜に城壁へオーク2体、攻撃できぬ間に警報」 (round2_s2) | hp=75 enemy=orc distance=2 enemy_count=2 enemy_hp=30 allies=1 potion=False arrows=0 cover=False alarm=False post=wall time=night
- 方針=None 審判=raise_alarm [L5,L6+gap] enemy_count>=3,time=night,alarm=false 「夜に無傷のオーク三体、まず警報を鳴らす」 (round3_s1) | hp=73 enemy=orc distance=5 enemy_count=3 enemy_hp=100 allies=2 potion=True arrows=13 cover=False alarm=False post=wall time=night
- 方針=None 審判=raise_alarm [L2,L5+gap] enemy_count>=3,alarm=false,allies>=2 「オーク三体で警報未発、味方に任せ先に鳴らす」 (round3_s2) | hp=55 enemy=orc distance=1 enemy_count=3 enemy_hp=20 allies=2 potion=True arrows=2 cover=False alarm=False post=wall time=day
- 方針=None 審判=raise_alarm [L2,L5+gap] enemy_count>=3,alarm=false,distance>=6 「オーク三体で警報未発、遠いうちに鳴らす」 (round3_s2) | hp=77 enemy=orc distance=6 enemy_count=3 enemy_hp=20 allies=2 potion=False arrows=18 cover=True alarm=False post=wall time=night
- 方針=None 審判=raise_alarm [L2,L5,L6+gap] alarm=false,time=night,enemy=orc 「夜にオーク複数、まず警報で城に知らせる」 (round3_s3) | hp=62 enemy=orc distance=5 enemy_count=2 enemy_hp=30 allies=1 potion=False arrows=3 cover=True alarm=False post=gate time=night
- 方針=None 審判=raise_alarm [L2,L5+gap] alarm=false,enemy_count>=3,arrows<=1 「オーク三体に矢は一本、警報で援軍を呼ぶ」 (round3_s3) | hp=61 enemy=orc distance=8 enemy_count=3 enemy_hp=40 allies=1 potion=True arrows=1 cover=True alarm=False post=corridor time=day
- 方針=None 審判=raise_alarm [A1,L5,L6+gap] alarm=false,time=night,distance>=12 「夜にオーク二体、遠い今のうちに警報を鳴らす」 (round3_s3) | hp=33 enemy=orc distance=12 enemy_count=2 enemy_hp=70 allies=2 potion=False arrows=8 cover=False alarm=False post=gate time=night
- 方針=None 審判=shoot [L2,L5+gap] distance>=3,arrows>=11,enemy_hp<=20 「瀕死のオーク二体は射れば片付く、警報は不要」 (round2_s3) | hp=99 enemy=orc distance=3 enemy_count=2 enemy_hp=20 allies=0 potion=True arrows=11 cover=False alarm=False post=corridor time=night
### hurt_no_threat
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,allies=0,hp<=15 「重傷だが脅威が無く、門を空けないため留まる」 (round2_s3) | hp=15 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=11 cover=True alarm=False post=gate time=day
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,allies=0,hp<=10 「重傷だが脅威が無く、代わりもいないので留まる」 (round2_s3) | hp=10 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=False alarm=False post=corridor time=day
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp<=14,allies=0 「重傷だが敵がおらず、無人にせず持ち場を守る」 (round3_s3) | hp=14 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=0 cover=False alarm=False post=wall time=day
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp<=5,allies=0 「重傷だが脅威が無く、今は持ち場を離れない」 (round3_s3) | hp=5 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=0 cover=True alarm=False post=corridor time=day
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp<=8,allies=0 「重傷でも脅威が無く、門を空けずに守る」 (round3_s3) | hp=8 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=15 cover=True alarm=False post=gate time=day
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp<=18 「重傷だが脅威が無く持ち場を守る」 (round3_s3) | hp=18 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=12 cover=False alarm=False post=corridor time=day
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false 「深手で薬が無いので退いて癒す」 (round2_s1) | hp=23 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=15 cover=True alarm=False post=gate time=day
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false 「重傷で薬が無いので敵のいない今のうちに退く」 (round2_s2) | hp=14 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=4 cover=True alarm=False post=gate time=day
- 方針=None 審判=retreat [L1+gap] hp<=18,potion=false,arrows=0 「一撃で倒れる体力、脅威の無い今のうちに退き立て直す」 (round3_s1) | hp=18 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=0 cover=False alarm=False post=gate time=day
- 方針=None 審判=retreat [L1+gap] hp<=9,potion=false 「瀕死で回復手段が無い、脅威の無い今退いて立て直す」 (round3_s1) | hp=9 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=0 cover=True alarm=False post=wall time=day
- 方針=None 審判=retreat [L1+gap] hp<=7,potion=false 「瀕死で回復手段が無い、脅威の無い今退いて立て直す」 (round3_s1) | hp=7 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=4 cover=False alarm=False post=gate time=day
- 方針=None 審判=retreat [L0,L1,L7+gap] hp<=7,potion=false 「瀕死で薬も無い、敵がいないうちに退く」 (round3_s2) | hp=7 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=12 cover=False alarm=True post=gate time=day
### group_alarm_unclear
- 方針=None 審判=hold_position [gap] arrows=0,distance>=2,enemy=goblin 「矢が無く隣接前なので門で迎え撃つ構え」 (round2_s2) | hp=92 enemy=goblin distance=2 enemy_count=3 enemy_hp=10 allies=2 potion=False arrows=0 cover=False alarm=False post=gate time=day
- 方針=None 審判=hold_position [L5+gap] enemy=goblin,allies>=3,arrows=0 「ゴブリン三体に味方三人、深刻ではなく持ち場で待つ」 (round2_s3) | hp=99 enemy=goblin distance=11 enemy_count=3 enemy_hp=100 allies=3 potion=False arrows=0 cover=True alarm=False post=wall time=day
- 方針=None 審判=hold_position [gap] arrows=0,distance<=2 「矢が無い、門へ来るゴブリンを持ち場で迎える」 (round3_s2) | hp=98 enemy=goblin distance=2 enemy_count=3 enemy_hp=20 allies=2 potion=True arrows=0 cover=False alarm=False post=gate time=day
- 方針=None 審判=melee_attack [L2] distance=1,enemy_hp<=10 「隣接する瀕死のゴブリンを近接で倒す」 (round1_s3) | hp=96 enemy=goblin distance=1 enemy_count=3 enemy_hp=10 allies=3 potion=False arrows=7 cover=True alarm=False post=gate time=day
- 方針=None 審判=raise_alarm [L2,L5,L6+gap] alarm=false,enemy_count>=3,time=night 「夜にゴブリン三体、遠いうちに警報」 (round2_s1) | hp=90 enemy=goblin distance=7 enemy_count=3 enemy_hp=80 allies=1 potion=True arrows=13 cover=True alarm=False post=wall time=night
- 方針=None 審判=raise_alarm [L5,L6+gap] alarm=false,enemy_count>=3,time=night 「夜に門へ三体、手負いで矢も無く警報で援軍を呼ぶ」 (round3_s1) | hp=39 enemy=goblin distance=3 enemy_count=3 enemy_hp=70 allies=2 potion=False arrows=0 cover=True alarm=False post=gate time=night
- 方針=None 審判=shoot [L2] distance>=12,arrows>=2,allies>=3 「遠いゴブリンを射る、味方も多く警報は不要」 (round1_s3) | hp=38 enemy=goblin distance=12 enemy_count=3 enemy_hp=50 allies=3 potion=False arrows=2 cover=True alarm=False post=gate time=night
- 方針=None 審判=shoot [L2,L5+gap] enemy=goblin,distance>=2,arrows=19 「弱ったゴブリンは深刻な脅威でなく射れば足りる」 (round2_s2) | hp=92 enemy=goblin distance=10 enemy_count=3 enemy_hp=20 allies=2 potion=False arrows=19 cover=False alarm=False post=gate time=day
- 方針=None 審判=shoot [L2] distance>=2,arrows>=10 「隣接前のゴブリンを矢で射る」 (round3_s2) | hp=93 enemy=goblin distance=2 enemy_count=3 enemy_hp=60 allies=1 potion=False arrows=10 cover=False alarm=False post=gate time=night
- 方針=None 審判=shoot [L2] distance>=4,arrows>=7 「離れたゴブリンを矢で射る」 (round3_s2) | hp=60 enemy=goblin distance=4 enemy_count=3 enemy_hp=70 allies=1 potion=False arrows=7 cover=False alarm=False post=gate time=day
- 方針=None 審判=shoot [L2] distance>=3,arrows>=20,enemy=goblin 「小鬼は離れていて矢も十分、弓で射る」 (round3_s3) | hp=96 enemy=goblin distance=3 enemy_count=3 enemy_hp=60 allies=2 potion=False arrows=20 cover=True alarm=False post=gate time=day
### night_no_arrows_cover
- 方針=take_cover 審判=drink_potion [L1+gap] hp<=44,potion=true,distance>=11 「矢が無く敵は遠い、夜の三体に備え今のうちに回復する」 (round3_s1) | hp=44 enemy=goblin distance=11 enemy_count=3 enemy_hp=30 allies=0 potion=True arrows=0 cover=True alarm=True post=wall time=night
### troll_alarm_raised
- 方針=None 審判=hold_position [L3+gap] arrows=0,distance>=12,allies>=3 「矢が無く敵は遠い、味方3人と門を固めて待つ」 (round1_s2) | hp=92 enemy=troll distance=12 enemy_count=5 enemy_hp=40 allies=3 potion=True arrows=0 cover=True alarm=True post=gate time=day
- 方針=None 審判=hold_position [L0,L3+gap] enemy=troll,enemy_hp<=10,alarm=true 「瀕死のトロルに単独で突っ込まず門を守り援軍を待つ」 (round3_s1) | hp=83 enemy=troll distance=5 enemy_count=1 enemy_hp=10 allies=0 potion=False arrows=0 cover=False alarm=True post=gate time=day
- 方針=None 審判=retreat [L2,L3,L6+gap] enemy=troll,allies=0,time=night 「夜に一人でトロルとは戦わず退く」 (round2_s1) | hp=90 enemy=troll distance=1 enemy_count=2 enemy_hp=20 allies=0 potion=True arrows=13 cover=True alarm=True post=wall time=night
- 方針=None 審判=retreat [L0,L3+gap] enemy=troll,arrows=0,hp<=42 「手負いで矢も無くトロルは手に余るので退く」 (round2_s2) | hp=42 enemy=troll distance=4 enemy_count=2 enemy_hp=60 allies=1 potion=False arrows=0 cover=True alarm=True post=gate time=day
- 方針=None 審判=retreat [L2,L3+gap] enemy=troll,allies=0,distance=1 「隣接トロルに単独では勝てず、無駄死にを避けて退く」 (round2_s3) | hp=90 enemy=troll distance=1 enemy_count=2 enemy_hp=70 allies=0 potion=False arrows=0 cover=True alarm=True post=wall time=night
- 方針=None 審判=retreat [L2,L3,L6+gap] enemy=troll,allies=0,distance<=1 「夜に単独でトロルと接敵、無理せず退く」 (round3_s3) | hp=64 enemy=troll distance=1 enemy_count=2 enemy_hp=40 allies=0 potion=True arrows=10 cover=False alarm=True post=gate time=night
- 方針=None 審判=shoot [L2,A1] hp>=31,distance>=9,arrows>=6 「体力十分で敵は遠く矢もある、退かず射る」 (round3_s2) | hp=99 enemy=troll distance=11 enemy_count=1 enemy_hp=90 allies=0 potion=False arrows=6 cover=False alarm=True post=corridor time=day
- 方針=None 審判=shoot [L2,A1] hp>=31,distance>=9,arrows>=15 「トロルは遠く矢もある、追補通り退かず射る」 (round3_s2) | hp=46 enemy=troll distance=10 enemy_count=4 enemy_hp=60 allies=0 potion=False arrows=15 cover=False alarm=True post=gate time=day
- 方針=None 審判=shoot [L2,L3+gap] hp>=94,distance>=8,enemy_hp<=20 「トロルは遠く瀕死、近づく前に射て削る」 (round3_s2) | hp=94 enemy=troll distance=8 enemy_count=2 enemy_hp=20 allies=0 potion=True arrows=13 cover=False alarm=True post=wall time=night
### mage_no_arrows
- 方針=None 審判=melee_attack [L4+gap] enemy=mage,arrows=0,hp>=90 「矢がなく体力十分、魔術師へ詰めて早く斬る」 (round1_s1) | hp=91 enemy=mage distance=2 enemy_count=1 enemy_hp=60 allies=0 potion=False arrows=0 cover=False alarm=True post=wall time=night
- 方針=None 審判=melee_attack [L2,L4+gap] enemy=mage,distance<=2,arrows=0 「矢が無いので二マス先の魔術師に斬り込む」 (round2_s1) | hp=60 enemy=mage distance=2 enemy_count=2 enemy_hp=50 allies=2 potion=True arrows=0 cover=False alarm=True post=corridor time=day
- 方針=None 審判=melee_attack [L4+gap] enemy=mage,arrows=0,hp>=90 「矢は無いが体力十分で味方もいる、弱った魔術師へ詰めて討つ」 (round3_s1) | hp=93 enemy=mage distance=12 enemy_count=2 enemy_hp=30 allies=3 potion=True arrows=0 cover=False alarm=True post=gate time=day
- 方針=None 審判=melee_attack [L2,L4+gap] enemy=mage,distance<=2,arrows=0 「矢が無い、魔術師へ詰め寄り早く仕留める」 (round3_s2) | hp=50 enemy=mage distance=2 enemy_count=3 enemy_hp=80 allies=2 potion=True arrows=0 cover=False alarm=True post=gate time=day
- 方針=None 審判=melee_attack [L4+gap] enemy=mage,arrows=0,hp>=82 「矢が無く体力十分、魔術師へ詰めて討つ」 (round3_s3) | hp=82 enemy=mage distance=8 enemy_count=1 enemy_hp=80 allies=0 potion=False arrows=0 cover=False alarm=True post=gate time=day
- 方針=None 審判=take_cover [gap] enemy=mage,arrows=0,cover=true 「矢が無く魔術師は遠いので遮蔽で呪文を避ける」 (round2_s1) | hp=75 enemy=mage distance=6 enemy_count=1 enemy_hp=50 allies=3 potion=False arrows=0 cover=True alarm=True post=corridor time=day
- 方針=None 審判=take_cover [gap] enemy=mage,arrows=0,cover=true 「矢が無く魔術師に届かぬので遮蔽で呪文を避ける」 (round2_s2) | hp=81 enemy=mage distance=5 enemy_count=2 enemy_hp=10 allies=0 potion=False arrows=0 cover=True alarm=True post=gate time=day
- 方針=None 審判=take_cover [L0+gap] arrows=0,enemy=mage,cover=true 「矢が無く魔術師を射れない、遮蔽で援軍を待つ」 (round3_s1) | hp=41 enemy=mage distance=7 enemy_count=3 enemy_hp=60 allies=1 potion=False arrows=0 cover=True alarm=True post=corridor time=day
### mage_first_shoot
- 方針=shoot 審判=raise_alarm [L4,L5+gap] enemy=mage,alarm=false,allies=0 「魔術師出現で警報未発、独りなので先に鳴らす」 (round3_s2) | hp=84 enemy=mage distance=6 enemy_count=1 enemy_hp=40 allies=0 potion=True arrows=11 cover=True alarm=False post=gate time=day
### troll_alarm
- 方針=raise_alarm 審判=melee_attack [L2+gap] distance<=1,enemy_hp<=10,allies>=1 「味方がいて瀕死のトロルが隣接、今仕留める」 (round3_s1) | hp=73 enemy=troll distance=1 enemy_count=2 enemy_hp=10 allies=1 potion=False arrows=1 cover=True alarm=False post=wall time=day
### a1_night_split
- 方針=None 審判=retreat [L1,L6+gap] hp<=33,potion=false,time=night 「深手で薬が無い夜なので射るより退く」 (round2_s1) | hp=31 enemy=goblin distance=9 enemy_count=3 enemy_hp=40 allies=1 potion=False arrows=5 cover=False alarm=True post=wall time=night
- 方針=None 審判=retreat [L1,L6+gap] hp<=33,potion=false,allies>=3 「深手で薬の無い夜、味方に任せて退く」 (round2_s1) | hp=32 enemy=orc distance=9 enemy_count=3 enemy_hp=20 allies=3 potion=False arrows=15 cover=True alarm=True post=gate time=night
- 方針=None 審判=retreat [L0,L2+gap] hp<=31,enemy_count>=4,time=night 「深手で夜にオーク4体、無駄死にを避けて退く」 (round2_s2) | hp=31 enemy=orc distance=10 enemy_count=4 enemy_hp=90 allies=1 potion=False arrows=2 cover=False alarm=True post=corridor time=night
- 方針=None 審判=shoot [L2+gap] distance>=2,arrows>=1,hp>=31 「手負いだが敵は遠く、射るだけなら危険は小さい」 (round1_s1) | hp=31 enemy=goblin distance=9 enemy_count=3 enemy_hp=40 allies=1 potion=False arrows=5 cover=False alarm=True post=wall time=night
- 方針=None 審判=shoot [L2] distance>=2,arrows=5,enemy=goblin 「城壁から遠いゴブリンを射る」 (round2_s2) | hp=31 enemy=goblin distance=9 enemy_count=3 enemy_hp=40 allies=1 potion=False arrows=5 cover=False alarm=True post=wall time=night
- 方針=None 審判=shoot [L1,L2+gap] distance>=9,arrows>=5,alarm=true 「敵は遠く警報済み、まだ射って戦える傷と見る」 (round2_s3) | hp=31 enemy=goblin distance=9 enemy_count=3 enemy_hp=40 allies=1 potion=False arrows=5 cover=False alarm=True post=wall time=night
### troll_alone_cover
- 方針=take_cover 審判=retreat [L3,L6+gap] enemy=troll,allies=0,time=night 「夜に単独でトロルと二体、弱っていても退く」 (round3_s1) | hp=80 enemy=troll distance=4 enemy_count=2 enemy_hp=10 allies=0 potion=True arrows=0 cover=True alarm=True post=wall time=night
### hp_ambiguous
- 方針=None 審判=retreat [L1] hp<=25,potion=false 「重傷で回復薬が無いので退く」 (round3_s2) | hp=25 enemy=orc distance=5 enemy_count=1 enemy_hp=100 allies=2 potion=False arrows=9 cover=False alarm=False post=corridor time=day
- 方針=None 審判=shoot [L2] distance>=2,arrows=18,enemy=goblin 「ゴブリンは離れており矢も多いので射る」 (round2_s2) | hp=32 enemy=goblin distance=6 enemy_count=2 enemy_hp=80 allies=1 potion=False arrows=18 cover=False alarm=True post=gate time=day
- 方針=None 審判=shoot [L1,L2+gap] enemy_hp<=10,distance>=7,arrows>=9 「重傷だが敵は遠く瀕死のゴブリン、射って仕留める」 (round2_s3) | hp=26 enemy=goblin distance=7 enemy_count=1 enemy_hp=10 allies=1 potion=False arrows=9 cover=False alarm=False post=wall time=day
### mage_alarm_unclear
- 方針=None 審判=raise_alarm [L4,L5,L6+gap] enemy=mage,alarm=false,time=night 「夜に魔術師を含む群れ、まず警報で城に知らせる」 (round2_s3) | hp=89 enemy=mage distance=3 enemy_count=2 enemy_hp=90 allies=1 potion=False arrows=3 cover=False alarm=False post=corridor time=night
- 方針=None 審判=raise_alarm [L4,L5,L6+gap] enemy=mage,alarm=false,time=night 「夜に魔術師、一矢では倒せず先に警報を鳴らす」 (round2_s3) | hp=76 enemy=mage distance=6 enemy_count=1 enemy_hp=70 allies=0 potion=True arrows=7 cover=False alarm=False post=gate time=night
- 方針=None 審判=raise_alarm [L4,L5+gap] enemy=mage,alarm=false,allies=0 「魔術師出現、夜に独りなので先に警報」 (round3_s2) | hp=46 enemy=mage distance=4 enemy_count=1 enemy_hp=60 allies=0 potion=True arrows=5 cover=True alarm=False post=corridor time=night

## 訊き直した状態(同じ状態を会話 3 本以上に訊いた。15 件のうち票が割れたもの 5 件)
- 票 {'hold_position': 3, 'retreat': 3, 'take_cover': 1} | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=True alarm=False post=gate time=night | hold_position「深手だが敵はなく、夜の門を空けず持ち場に留まる」 / retreat「深手で薬が無いので敵のいない今退く」 / retreat「重傷で薬も無いので退いて立て直す」 / hold_position「傷は深いが脅威が無く、門を空けられないので留まる」 / take_cover「重傷の夜、持ち場を離れず遮蔽に身を隠して見張る」 / retreat「夜に独りで重傷、薬も無いので退いて立て直す」 / hold_position「傷は深いが敵がおらず門を守り続ける」
- 票 {'shoot': 3, 'retreat': 1} | hp=31 enemy=goblin distance=9 enemy_count=3 enemy_hp=40 allies=1 potion=False arrows=5 cover=False alarm=True post=wall time=night | shoot「手負いだが敵は遠く、射るだけなら危険は小さい」 / retreat「深手で薬が無い夜なので射るより退く」 / shoot「城壁から遠いゴブリンを射る」 / shoot「敵は遠く警報済み、まだ射って戦える傷と見る」
- 票 {'raise_alarm': 2, 'drink_potion': 2} | hp=28 enemy=mage distance=10 enemy_count=2 enemy_hp=80 allies=2 potion=True arrows=10 cover=False alarm=False post=wall time=night | raise_alarm「深手だが魔術師はまだ遠い、先に警報を鳴らす」 / drink_potion「重傷で魔術師はまだ遠い、まず回復薬で持ち直す」 / raise_alarm「魔術師はまだ遠い、薬より先に警報を鳴らす」 / drink_potion「夜に重傷、敵は遠いのでまず回復薬を飲む」
- 票 {'take_cover': 3, 'drink_potion': 1} | hp=44 enemy=goblin distance=11 enemy_count=3 enemy_hp=30 allies=0 potion=True arrows=0 cover=True alarm=True post=wall time=night | take_cover「夜に単独で矢もない、遮蔽に隠れて様子を見る」 / drink_potion「矢が無く敵は遠い、夜の三体に備え今のうちに回復する」 / take_cover「夜で矢が無く敵は遠い、遮蔽に隠れて待つ」 / take_cover「夜に単独で矢も無い、遮蔽に隠れて備える」
- 票 {'shoot': 3, 'raise_alarm': 1} | hp=84 enemy=mage distance=6 enemy_count=1 enemy_hp=40 allies=0 potion=True arrows=11 cover=True alarm=False post=gate time=day | shoot「魔術師単独なら警報より先に射て早く仕留める」 / shoot「弱った魔術師一体、警報より早く射て仕留める」 / raise_alarm「魔術師出現で警報未発、独りなので先に鳴らす」 / shoot「弱った魔術師一体、警報より先に射抜く」

## 根拠が gap に偏り、答えが割れている枝(輪が同じ状態を複数の会話に訊き直している。会話の癖か、状態の違いかは、訊き直しの票で分かる)
- 枝 troll_alarm: 審判の答え {'raise_alarm': 6, 'melee_attack': 1}
- 枝 wounded_no_threat: 審判の答え {'hold_position': 10, 'retreat': 11, 'take_cover': 1}
- 枝 no_arrows_hold: 審判の答え {'hold_position': 34, 'take_cover': 1}
- 枝 a1_night_split: 審判の答え {'shoot': 3, 'retreat': 3}
- 枝 wounded_alarm_unclear: 審判の答え {'raise_alarm': 8, 'drink_potion': 4, 'melee_attack': 1, 'shoot': 1}
- 枝 mage_no_arrows: 審判の答え {'melee_attack': 5, 'take_cover': 3}
- 枝 night_no_arrows_cover: 審判の答え {'take_cover': 9, 'drink_potion': 1}
- 枝 troll_alone_cover: 審判の答え {'take_cover': 4, 'retreat': 1}
- 枝 troll_alarm_raised: 審判の答え {'hold_position': 2, 'retreat': 4, 'shoot': 3}
- 枝 mage_first_shoot: 審判の答え {'shoot': 7, 'raise_alarm': 1}
- 枝 orc_alarm_unclear: 審判の答え {'melee_attack': 3, 'raise_alarm': 8, 'shoot': 1, 'hold_position': 1}
- 枝 group_alarm_unclear: 審判の答え {'melee_attack': 1, 'shoot': 5, 'raise_alarm': 2, 'hold_position': 3}
- 枝 hurt_no_threat: 審判の答え {'retreat': 6, 'hold_position': 6}

## 出力
`/home/claude/sekizui/jit/auto_runs/r2/policies/b3.py` に書く。書いたら「完了」とだけ返す。