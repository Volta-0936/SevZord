# 翻訳の依頼 — 走り r3、第 5 版

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
A1 オーク三体以上、または味方の無いまま夜か矢四本以下で向き合うオーク二体は深刻な脅威であり、ひどく傷ついていなければ、警報がまだなら鳴らす。
A2 昼に矢が尽きても、遮蔽があり、離れた小鬼かオークが二体までなら、ひどく傷ついていない限り持ち場で待ち構える(A1 で警報を鳴らす時を除く)。

行動: melee_attack(近接攻撃), shoot(弓で射る), retreat(退く), drink_potion(回復薬を飲む), take_cover(遮蔽に隠れる), raise_alarm(警報を鳴らす), hold_position(持ち場を守る)
状態の項目: hp(番兵の体力 0-100), enemy(最も近い敵の種類: none/goblin/orc/mage/troll), distance(その敵までのマス数、敵がいなければ null), enemy_count(見えている敵の数), enemy_hp(最も近い敵の体力 %), allies(近くの味方の数), potion(回復薬を持っているか), arrows(矢の残り), cover(近くに遮蔽物があるか), alarm(警報が既に鳴っているか), post(持ち場: gate/wall/corridor), time(day/night)
```

## 追補(審判の会話の多数から作り、門で機械的に確かめた規則。条件の式をそのまま使ってよい)
- A1: オーク三体以上、または味方の無いまま夜か矢四本以下で向き合うオーク二体は深刻な脅威であり、ひどく傷ついていなければ、警報がまだなら鳴らす。 → `raise_alarm` / 条件 `s['enemy'] == 'orc' and not s['alarm'] and s['hp'] > 36 and (s['enemy_count'] >= 3 or (s['enemy_count'] >= 2 and s['allies'] == 0 and (s['time'] == 'night' or s['arrows'] <= 4)))`
- A2: 昼に矢が尽きても、遮蔽があり、離れた小鬼かオークが二体までなら、ひどく傷ついていない限り持ち場で待ち構える(A1 で警報を鳴らす時を除く)。 → `hold_position` / 条件 `s['arrows'] == 0 and s['cover'] and s['time'] == 'day' and s['enemy'] in ('goblin', 'orc') and s['distance'] >= 2 and s['enemy_count'] <= 2 and s['hp'] > 36 and not (s['enemy'] == 'orc' and not s['alarm'] and s['enemy_count'] >= 2 and s['allies'] == 0)`

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

- 追補をそのまま読んだ枝は、例が少なくても答えてよい(門は、その枝のラベルつきの状態が全部、同じ行動の追補の条件に入るかを確かめる)。

## いまの方針(c4)
```python
"""走り r3 の方針、第 4 版(c4)。前の版は c3。やり直し 1 回目。

帳簿: 審判のラベル 374 件、会話 10 本(round1_s1/s2/s3、round2_s1/s2/s3、round3_s1/s2、
round4_s1/s2。以下 r1s1 … r4s2)。範囲の番人は c3 のまま。

c3 の答える枝は、374 件で数え直しても全部が門を通る(一致 80% 以上、別の答えを多数にした
会話は 1 本以下)ので、条件を変えない。この版で変えたのは、c3 が棄権していた所のうち
round4 の 2 本で会話の多数が揃った所と、答えていたのに訊き直しで 3 本とも外れた所。

やり直しの理由と直し方
    前の版の wounded_cover_day(答える枝、take_cover)は例 4 件のうち 3 件しか一致せず(75%)、
    規律 (b) の 80% に届かなかった。3 件は訊き直した同じ状態(hp42・小鬼 3 体・distance 4・
    味方 3・薬なし・矢 0・遮蔽あり・警報済み・昼・門)で、r1s2、r4s1、r4s2 の 3 本とも
    take_cover。残る 1 件は hold なので、この所は割れている。答えるのをやめ、名前を付けた
    番人 worn_cover_day で棄権にした(下の 4.)。c3 の no_arrows_cover_day はこの 3 件を
    hold と答えて外していたので、それも止まる。

この版で変えたこと
 1. orc_pair_melee_allied(新しい枝、番人 orc_alarm_unclear から):
    警報未・オーク 2 体・隣接・味方 1 以上 → melee_attack。
    7 件・会話 4 本(r1s3、r3s2、r4s1 3、r4s2 2)・一致 7/7。根拠 L2(一部 L5/L6+gap)。
    決め手 distance<=1 7、allies>=2 3 / >=3 1、hp>=91 2(「隣接したオークに味方と共に近接で
    当たる」「隣接、夜でも味方が多く近接で戦う」)。昼 2・夜 5 とも melee なので時刻は条件に
    しない。
    味方 0 の隣接は残す(訊き直した hp82・夜・単独は raise 2(r1s2、r2s1)/ melee 1(r2s3)、
    raise の決め手 allies=0「夜の門で単独、オーク2体に先に警報」。昼の単独は melee 1、gap)。
    味方の線は、raise の決め手 allies=0 と melee の決め手 allies>=2 の間の 1
    (_ORC_PAIR_ALLIES_MIN)。オーク 3 体の隣接(r3s2 raise 1「オーク三体で未警報、隣の敵は
    味方に任す」、決め手 enemy_count>=3)は外す(敵 2 体に限る)。

 2. orc_alone_noarrow_alarm(新しい枝、番人 orc_alarm_unclear から):
    警報未・オーク 2 体・昼・distance>=2・味方 0・矢 0 → raise_alarm。
    3 件・会話 3 本(r2s1、r4s1、r4s2。訊き直した同じ状態 hp83・distance 7・wall)・一致 3/3。
    根拠 L5(+gap)。決め手 allies=0 3、enemy_count>=2 3、alarm=false 3(「味方も矢も無く
    オーク二体、警報で助けを呼ぶ」「味方なしで敵二体、矢も無いので警報で援軍を呼ぶ」)。
    矢ありは割れる(raise 1 r3s1 矢 4 / shoot 1 r2s3 矢 8、shoot の決め手 distance>=2,
    arrows>=1)ので、shoot の決め手の外(矢 0)に限り、矢ありは番人に残す。
    夜は c3 の orc_night_alarm が先に取る。

 3. 昼・オーク 2 体・味方あり・離れ・矢 0 を、L2 の矢なしの枝へ流した(新しい名前は作らない)。
    c3 の orc_pair_day_shoot は「味方が多くオーク二体は深刻でない」と読んで射ていたが、
    矢 0 は外して番人に残していた。いま hold 2 件・会話 2 本(r3s1 d9 遮蔽あり、r4s2 d2
    遮蔽なし)・一致 2/2、決め手 arrows=0 2、distance>=2 / >=9、allies>=3(「矢が無く二対二、
    持ち場で迎え撃つ」「矢が無く敵は二マス先、味方と通路で待ち構える」)。これは既にある
    no_arrows_cover_day と no_arrows_hold(離れ・矢 0 → hold、決め手 arrows=0)と同じ規則
    なので、同じ名前で答える。no_arrows_hold は 9/9、no_arrows_cover_day は hold が 1 件増える。

 4. 番人 worn_cover_day(新しい番人、no_arrows_cover_day から切り出す):
    昼・離れ・矢 0・遮蔽あり・hp 42 以下 → 棄権。
    take_cover 3(上の訊き直した状態。決め手 arrows=0 3、hp<=42 2、cover=true 2、
    potion=false 1、distance>=4 1「矢も薬も無く体力半分以下、遮蔽で門に踏み止まる」
    「矢が無く傷も浅くないので遮蔽で接近を待つ」)と hold 1 で割れる(75%)。根拠 gap。
    線は take_cover の決め手 hp<=42 のまま(_WORN_MAX)。薬ありの手負いも(魔術師の所の
    hp39・薬ありは drink、r4s1)競うかもしれないので、薬は条件にしない。
    これで no_arrows_cover_day の外れは r4s2 の 1 件(hp82・小鬼 5 体・薬あり、決め手
    arrows=0, enemy_count>=5, cover=true)だけになる。

 5. near_fine_hold(新しい枝、番人 hp_ambiguous から):
    hp 31〜32・薬なし・敵なしで、hp が 31.5 以上 → hold_position。
    5 件・会話 4 本(r2s1、r2s2、r4s1 2、r4s2。全部 hp32・昼)・一致 5/5。根拠 L7(+L1、gap)。
    決め手 enemy=none 5、hp>=32 3、time=day 1、hp<=32 1(「脅威が無く深手でもないので持ち場を
    守る」「敵は無く、退くほどの深手でもないので持ち場を守る」)。
    退いた hp31(r2s3、夜・味方 3、決め手 hp<=33, potion=false, allies>=1「深手で薬も無い、
    味方に門を任せて退く」)が残るので、線は hold の決め手 hp>=32 と退いた 31 の間の 31.5
    (_NEAR_FINE_MIN)。hp31 の敵なしは番人 hp_ambiguous に残す。

変えなかった番人
    hp_ambiguous 8: hp 31〜32・薬なしの残り。敵あり retreat 5(r2s1 2、r2s2、r2s3、r4s1)/
        shoot 2(r1s1、r2s2)で 71%。夜だけでも retreat 4 / shoot 1 のちょうど 80% で、訊き
        直した状態(hp31・小鬼 3 体・夜)も retreat 2 / shoot 1。昼は retreat 1 / shoot 1。
        敵なしの hp31 は retreat 1(gap)。
    no_arrows_cover 15: 夜・離れ・矢 0・遮蔽ありの残り(take_cover 8 / hold 4 / raise 2 /
        drink 1)。会話の多数は take_cover 5 本(r2s2、r2s3、r3s2、r4s1、r4s2)/ hold 2 本
        (r2s1、r3s1)。味方あり・警報済みは take_cover 4 / hold 3、味方あり・警報未は
        take_cover 2(r4s1、r4s2、どちらも L6+gap)/ raise 1 / drink 1、単独・警報未は
        take_cover 2 / hold 1 / raise 1。どの切り方でも 80% に届かないか、例が 2 件以下で gap。
    orc_alarm_unclear 8: 隣接・単独(夜 raise 2 / melee 1、昼 melee 1)、昼・単独・離れ・矢あり
        (raise 1 / shoot 1)、オーク 3 体・味方あり(raise 2、どちらも r3s2 の 1 本、gap)。
    wounded_vs_alarm 5、mage_no_arrows 3、troll_no_arrows 2、hurt_vs_alarm 1、
        weak_troll_alone 1、weak_mage_unclear 1: c3 のまま。例が少ないか割れていて、根拠は gap。

c4 で数え直した帳簿(答える枝、件数・一致・会話)
    no_threat_hold          60  60/60  10 本     L7      敵なし・hp>=33 → hold_position
    shoot_far               36  34/36   8 本     L2      離れたゴブリン/オーク・矢あり → shoot
    no_arrows_cover_day     28-k-3+1  外れ 1  gap 離れ・矢 0・遮蔽あり・昼・hp>=43 → hold_position
    horde_alarm             17  17/17   7 本     L5      警報未・敵 4 以上 → raise_alarm
    melee_adjacent          15  15/15   6 本     L2      隣接のゴブリン/オーク → melee_attack
    mage_alarm              15  14/15   7 本     L5+L4   警報未・離れた魔術師 → raise_alarm
    hurt_no_threat_retreat  13  13/13   5 本     L1      hp<=20・薬なし・敵なし → retreat
    wounded_drink           11  11/11   7 本     L1      hp 21〜32・薬あり → drink_potion
    wounded_retreat         10   9/10   8 本     L1      hp 21〜30・薬なし・敵あり → retreat
    orc_night_alarm         10   9/10   7 本     L5+L6   警報未のオーク 2〜3・夜・離れ → raise_alarm
    no_arrows_hold           9   9/9           gap     離れ・矢 0・遮蔽なし → hold_position
    troll_alarm              8   8/8    5 本     L5+L3   トロル・警報未 → raise_alarm
    wounded_alone_hold       8   7/8    6 本     L7      hp 21〜30・薬なし・敵なし・味方 0 → hold_position
    orc_pair_melee_allied    7   7/7    4 本     L2      警報未のオーク 2・隣接・味方あり → melee_attack(新)
    hurt_drink               6   6/6    4 本     L1      hp<=20・薬あり → drink_potion
    mage_melee_first         6   6/6    5 本     L4+L2   警報未・隣接の魔術師 → melee_attack
    wounded_handover         6   6/6    3 本     L1      hp 21〜30・薬なし・敵なし・味方あり → retreat
    troll_alone_retreat      6   6/6    4 本     L3      警報済みトロル・単独・隣接か遮蔽なし → retreat
    near_fine_hold           5   5/5    4 本     L7      hp 32・薬なし・敵なし → hold_position(新)
    troll_shoot_allied       5   5/5    4 本     L2+L3   警報済みトロル・味方あり・離れ・矢あり → shoot
    weak_mage_shoot          5   5/5    4 本     L4      警報未・弱い魔術師・敵 2 以下・矢 4 以上 → shoot
    outnumbered_alarm        4   4/4    3 本     L5      警報未・敵 3・味方 0 → raise_alarm
    night_alone_cover        4   4/4    4 本     L6      夜・単独・警報済み・離れ・矢 0・遮蔽 → take_cover
    troll_alone_cover        4   4/4    3 本     L3+L6   警報済みトロル・単独・離れ・遮蔽 → take_cover
    mage_shoot               4   4/4    3 本     L2+L4   離れた魔術師(警報済み)・矢あり → shoot
    orc_pair_day_shoot       4   4/4    3 本     L2      警報未のオーク 2・昼・味方あり・離れ・矢あり → shoot
    orc_alone_noarrow_alarm  3   3/3    3 本     L5      警報未のオーク 2・昼・単独・離れ・矢 0 → raise_alarm(新)
    mage_close_melee         3   3/3    3 本     L4      警報済み魔術師・矢 0・distance 2・遮蔽なし → melee_attack
    hurt_retreat             3   3/3    3 本     L1      hp<=20・薬なし・敵あり → retreat
    hurt_troll_alarm         3   3/3    3 本     L5+L3   hp<=32・警報未トロル・distance>=3 → raise_alarm
    mage_no_arrows_cover     3   3/3    3 本     gap     警報済み魔術師・矢 0・distance>=3・遮蔽 → take_cover
    hurt_horde_alarm         3   3/3    3 本     L5+L1   hp<=32・薬なし・警報未の群れ・distance>=3 → raise_alarm
    wounded_mage_alarm       3   3/3    2 本     L5+L1   hp 21〜32・薬なし・警報未の魔術師・distance>=3 → raise_alarm
    troll_melee_allied       2   2/2    2 本     L2+L3   警報済みトロル・味方あり・隣接 → melee_attack
    mage_melee               0                   L2+L4   隣接の魔術師(警報済み) → melee_attack
    答える 327-k 件、一致 320-k(k は worn_cover_day に入る昼の遮蔽の hold。c3 は 313 件で一致 303)。

棄権の番人(割れている所、証拠が足りない所。輪が審判に訊き直す所)
    no_arrows_cover      15  夜・離れ・矢 0・遮蔽ありの残り(take_cover 8 / hold 4 / raise 2 / drink 1)
    hp_ambiguous          8  hp 31〜32・薬なしの残り(retreat 6 / shoot 2)
    orc_alarm_unclear     8  警報未のオーク 2〜3 体の残り(raise 5 / melee 2 / shoot 1)
    wounded_vs_alarm      5  hp 21〜32 で L1 と L5 が競る残り(raise 2 / drink 2 / melee 1)
    worn_cover_day      3+k  昼・離れ・矢 0・遮蔽・hp 33〜42(take_cover 3 / hold k)(新)
    mage_no_arrows        3  警報済み魔術師・矢 0 の残り(hold 2 / drink 1)
    troll_no_arrows       2  警報済みトロル・味方あり・離れ・矢 0(hold 1 / take_cover 1)
    weak_troll_alone      1  警報済みトロル・単独・隣接か遮蔽なし・敵の体力 15 以下(hold 1)
    weak_mage_unclear     1  警報未・離れた弱い魔術師・矢ありの残り(raise 1)
    hurt_vs_alarm         1  hp<=20・警報未トロル・distance<=2・薬あり(drink 1、gap)
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

# 「ひどく傷ついている」の帯
_HURT_MAX = 20      # これ以下は明らかにひどい
_WOUNDED_MAX = 30   # 21〜30 は手負い。決め手 hp<=30 が最も多い。31〜32 は会話で割れる
_FINE_MIN = 33      # これ以上はひどくない(飲む最高の 31 と、次の例 35 の間)
# 31〜32・薬なし・敵なしで持ち場を守る下限(hold の決め手 hp>=32 と、退いた hp31 の間)
_NEAR_FINE_MIN = 31.5

# 警報未の群れ
_HORDE_MIN = 4          # 敵がこれ以上なら警報
_OUTNUMBERED_MIN = 3    # 味方 0 で敵がこれ以上なら警報

# 傷と警報が競るとき、これ以上離れていれば警報が先(隣接 1 は退く・飲む、5 以上は警報)
_ALARM_FIRST_DIST = 3

# 警報未の離れた魔術師を「弱っている」と見る敵の体力の上限(shoot の 30 と raise の 40 の間)
_WEAK_MAGE_MAX = 35
# 弱った魔術師を射るのに要る矢(raise の決め手 arrows<=2 と shoot の決め手 arrows>=6 の間)
_WEAK_MAGE_ARROWS_MIN = 4

# 矢の無いとき、魔術師に「詰めて斬る」距離(melee の決め手 distance<=2)
_MAGE_CLOSE_MAX = 2

# 単独で向き合うトロルを「瀕死」と見る敵の体力の上限(hold の 10 と retreat の 20 の間)
_WEAK_TROLL_MAX = 15

# 警報未のオーク二体の隣で「味方と共に斬る」味方の数(raise の allies=0 と melee の allies>=2 の間)
_ORC_PAIR_ALLIES_MIN = 1

# 昼・矢 0・遮蔽ありで、take_cover と hold が割れる体力の上限(take_cover の決め手 hp<=42)
_WORN_MAX = 42


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


def decide(s):
    bad = _guard(s)
    if bad is not None:
        return (None, bad)

    hp = s["hp"]
    enemy = s["enemy"]
    dist = s["distance"]
    count = s["enemy_count"]
    enemy_hp = s["enemy_hp"]
    allies = s["allies"]
    potion = s["potion"]
    arrows = s["arrows"]
    cover = s["cover"]
    alarm = s["alarm"]
    time = s["time"]

    fine = hp >= _FINE_MIN
    hurt = hp <= _HURT_MAX
    serious_group = enemy != "none" and (
        count >= _HORDE_MIN or (count >= _OUTNUMBERED_MIN and allies == 0))

    # --- L1 と L5 が競る所: 敵が遠いうちは、傷があっても警報が先 ---
    if (not fine and enemy != "none" and not alarm
            and dist >= _ALARM_FIRST_DIST):
        if enemy == "troll":
            return ("raise_alarm", "hurt_troll_alarm")
        if not potion:
            if enemy == "mage" and not hurt:
                return ("raise_alarm", "wounded_mage_alarm")
            if serious_group:
                return ("raise_alarm", "hurt_horde_alarm")

    # --- L1: ひどく傷ついている(hp<=20) ---
    if hurt:
        if enemy == "troll" and not alarm:
            # 近いトロル(distance<=2)。隣接では生き延びが先
            if potion:
                return (None, "hurt_vs_alarm")
            return ("retreat", "hurt_retreat")
        if potion:
            return ("drink_potion", "hurt_drink")
        if enemy == "none":
            return ("retreat", "hurt_no_threat_retreat")
        return ("retreat", "hurt_retreat")

    # --- 手負い(21<=hp<=32) ---
    if not fine:
        if not alarm and enemy == "mage":
            # 薬あり、または distance<=2(遠くて薬なしは上で警報)
            return (None, "wounded_vs_alarm")
        if potion:
            if not alarm and (enemy == "troll" or count >= _HORDE_MIN):
                return (None, "wounded_vs_alarm")
            return ("drink_potion", "wounded_drink")
        if hp > _WOUNDED_MAX:
            # 31〜32、薬なし
            if enemy == "none" and hp >= _NEAR_FINE_MIN:
                return ("hold_position", "near_fine_hold")
            return (None, "hp_ambiguous")
        # 21<=hp<=30、薬なし
        if enemy == "none":
            if allies >= 1:
                return ("retreat", "wounded_handover")
            return ("hold_position", "wounded_alone_hold")
        return ("retreat", "wounded_retreat")

    # ここから先は hp>=33(ひどくない)

    # --- L7: 脅威が無い ---
    if enemy == "none":
        return ("hold_position", "no_threat_hold")

    # --- L3 + L5: トロル ---
    if enemy == "troll":
        if not alarm:
            return ("raise_alarm", "troll_alarm")
        # 警報済み。L3 は「一人で」相手にするなと言う
        if allies >= 1:
            if dist == 1:
                return ("melee_attack", "troll_melee_allied")
            if arrows >= 1:
                return ("shoot", "troll_shoot_allied")
            return (None, "troll_no_arrows")
        if dist >= 2 and cover:
            return ("take_cover", "troll_alone_cover")
        if enemy_hp <= _WEAK_TROLL_MAX:
            return (None, "weak_troll_alone")
        return ("retreat", "troll_alone_retreat")

    # --- L5: 警報未のとき、深刻な脅威かどうか ---
    if not alarm:
        if count >= _HORDE_MIN:
            return ("raise_alarm", "horde_alarm")
        if count >= _OUTNUMBERED_MIN and allies == 0:
            return ("raise_alarm", "outnumbered_alarm")
        if enemy == "mage":
            if dist == 1:
                return ("melee_attack", "mage_melee_first")
            if arrows >= 1 and enemy_hp <= _WEAK_MAGE_MAX:
                if count <= 2 and arrows >= _WEAK_MAGE_ARROWS_MIN:
                    return ("shoot", "weak_mage_shoot")
                return (None, "weak_mage_unclear")
            return ("raise_alarm", "mage_alarm")
        if enemy == "orc" and count >= 2:
            # ここに来るのは、オーク 2 体、またはオーク 3 体・味方あり
            if dist == 1:
                if count == 2 and allies >= _ORC_PAIR_ALLIES_MIN:
                    return ("melee_attack", "orc_pair_melee_allied")
                return (None, "orc_alarm_unclear")
            # 離れている(distance>=2)
            if time == "night":
                return ("raise_alarm", "orc_night_alarm")
            # 昼
            if count != 2:
                return (None, "orc_alarm_unclear")
            if allies == 0:
                if arrows <= 0:
                    return ("raise_alarm", "orc_alone_noarrow_alarm")
                return (None, "orc_alarm_unclear")
            # 昼・オーク 2 体・味方あり: 深刻な脅威ではない → L2
            if arrows >= 1:
                return ("shoot", "orc_pair_day_shoot")
            # 矢 0 は下の L2 の矢なしの枝へ
        # 単独のオーク、ゴブリン 1〜3 体(3 体なら味方あり)は深刻な脅威ではない → L2 へ

    # --- L2 (+ L4 魔術師) ---
    if dist == 1:
        if enemy == "mage":
            return ("melee_attack", "mage_melee")
        return ("melee_attack", "melee_adjacent")

    # 離れている(distance>=2)
    if arrows <= 0:
        if enemy == "mage":
            # ここに来る魔術師は警報済み
            if dist <= _MAGE_CLOSE_MAX and not cover:
                return ("melee_attack", "mage_close_melee")
            if dist > _MAGE_CLOSE_MAX and cover:
                return ("take_cover", "mage_no_arrows_cover")
            return (None, "mage_no_arrows")
        if cover:
            if time == "day":
                if hp <= _WORN_MAX:
                    return (None, "worn_cover_day")
                return ("hold_position", "no_arrows_cover_day")
            if alarm and allies == 0:
                return ("take_cover", "night_alone_cover")
            return (None, "no_arrows_cover")
        return ("hold_position", "no_arrows_hold")
    if enemy == "mage":
        return ("shoot", "mage_shoot")
    return ("shoot", "shoot_far")

```

## 熱さの帳簿(審判のラベル 417 件、会話 12 本を、いまの方針の枝ごとに数えた)

| 枝 | 件数 | 会話 | 方針の答え | 一致 | 会話の多数が方針と同じ | 審判の答え | 根拠 | 決め手(多い順) |
|---|---|---|---|---|---|---|---|---|
| no_threat_hold | 64 | 12 | hold_position | 64/64 | 12/12 | {'hold_position': 64} | L7 64, L1 8, L6 1; gap 8 | enemy=none 64, hp>=40 2, hp>=39 2, hp>=34 2 |
| shoot_far | 38 | 9 | shoot | 36/38 | 9/9 | {'shoot': 36, 'raise_alarm': 1, 'take_cover': 1} | L2 37, L6 1, L5 1; gap 2 | distance>=2 13, arrows>=1 12, distance>=6 4, arrows>=2 4 |
| no_arrows_cover_day | 32 | 12 | hold_position | 29/32 | 12/12 | {'hold_position': 29, 'take_cover': 2, 'raise_alarm': 1} | L0 3, L5 1; gap 31 | arrows=0 32, enemy=goblin 8, distance>=8 7, distance>=2 6 |
| horde_alarm | 18 | 8 | raise_alarm | 18/18 | 8/8 | {'raise_alarm': 18} | L5 18, L2 7, L6 5; gap 14 | alarm=false 18, enemy_count>=5 10, enemy_count>=4 8, allies=0 6 |
| melee_adjacent | 17 | 8 | melee_attack | 17/17 | 8/8 | {'melee_attack': 17} | L2 17; gap 1 | distance<=1 10, distance=1 7, enemy_hp<=10 4, allies>=3 2 |
| orc_alarm_unclear | 17 | 7 | None | -/- | -/7 | {'raise_alarm': 10, 'shoot': 2, 'melee_attack': 4, 'retreat': 1} | L2 14, L5 12, L6 2; gap 11 | alarm=false 10, allies=0 6, enemy_count>=3 5, enemy_count>=2 4 |
| no_arrows_cover | 17 | 9 | None | -/- | -/9 | {'hold_position': 4, 'take_cover': 10, 'raise_alarm': 2, 'drink_potion': 1} | L6 13, L5 2, L1 1; gap 11 | arrows=0 15, time=night 13, cover=true 10, enemy=goblin 2 |
| mage_alarm | 16 | 8 | raise_alarm | 15/16 | 7/8 | {'raise_alarm': 15, 'shoot': 1} | L5 16, L4 12, L6 3; gap 12 | enemy=mage 16, alarm=false 15, arrows=0 5, arrows<=1 2 |
| hurt_no_threat_retreat | 13 | 5 | retreat | 13/13 | 5/5 | {'retreat': 13} | L7 13, L1 13; gap 13 | potion=false 13, allies>=1 7, hp<=20 6, hp<=15 2 |
| wounded_retreat | 12 | 10 | retreat | 11/12 | 9/10 | {'retreat': 11, 'shoot': 1} | L1 12, L2 4, L3 3; gap 8 | potion=false 10, allies=0 5, hp<=30 4, hp<=22 4 |
| hp_ambiguous | 11 | 7 | None | -/- | -/7 | {'shoot': 2, 'retreat': 8, 'hold_position': 1} | L1 9, L2 5, L6 3; gap 9 | potion=false 9, hp<=31 5, time=night 2, hp<=32 2 |
| wounded_drink | 11 | 7 | drink_potion | 11/11 | 7/7 | {'drink_potion': 11} | L1 11, L2 3, L5 1; gap 5 | potion=true 11, hp<=21 3, enemy=none 3, hp<=31 2 |
| orc_night_alarm | 10 | 7 | raise_alarm | 9/10 | 6/7 | {'raise_alarm': 9, 'shoot': 1} | L6 9, L5 9, L2 8; gap 8 | time=night 9, alarm=false 9, allies<=1 3, enemy=orc 2 |
| no_arrows_hold | 9 | 6 | hold_position | 9/9 | 6/6 | {'hold_position': 9} | ; gap 9 | arrows=0 9, distance>=2 5, enemy=goblin 2, cover=false 2 |
| troll_alarm | 8 | 5 | raise_alarm | 8/8 | 5/5 | {'raise_alarm': 8} | L5 8, L3 7, L2 3; gap 5 | enemy=troll 8, alarm=false 8, allies=0 2, arrows=0 1 |
| wounded_alone_hold | 8 | 6 | hold_position | 7/8 | 5/6 | {'hold_position': 7, 'retreat': 1} | L7 8, L1 6, L0 5; gap 8 | enemy=none 7, allies=0 7, potion=false 2, post=gate 1 |
| orc_pair_melee_allied | 7 | 4 | melee_attack | 7/7 | 4/4 | {'melee_attack': 7} | L2 7, L6 2, L5 2; gap 3 | distance<=1 6, allies>=2 3, hp>=91 2, distance=1 1 |
| hurt_drink | 6 | 4 | drink_potion | 6/6 | 4/4 | {'drink_potion': 6} | L1 6, L5 1, L4 1; gap 1 | potion=true 6, hp<=12 2, hp<=30 1, enemy=none 1 |
| troll_no_arrows | 6 | 4 | None | -/- | -/4 | {'hold_position': 2, 'take_cover': 3, 'retreat': 1} | L3 3, L6 2, L1 1; gap 3 | arrows=0 6, cover=true 3, allies>=3 2, time=night 2 |
| worn_cover_day | 6 | 6 | None | -/- | -/6 | {'take_cover': 4, 'hold_position': 1, 'retreat': 1} | L0 1, L1 1; gap 5 | arrows=0 5, allies>=3 3, hp<=42 2, potion=false 2 |
| mage_melee_first | 6 | 5 | melee_attack | 6/6 | 5/5 | {'melee_attack': 6} | L2 6, L4 6, L5 4; gap 6 | enemy=mage 6, distance<=1 5, enemy_hp<=30 2, distance=1 1 |
| wounded_handover | 6 | 3 | retreat | 6/6 | 3/3 | {'retreat': 6} | L7 6, L1 6; gap 6 | potion=false 6, allies>=1 5, hp<=30 4, hp<=33 1 |
| troll_alone_retreat | 6 | 4 | retreat | 6/6 | 4/4 | {'retreat': 6} | L3 6, L2 5, L6 2; gap 6 | enemy=troll 6, allies=0 6, time=night 2, enemy_count>=2 1 |
| outnumbered_alarm | 5 | 4 | raise_alarm | 5/5 | 4/4 | {'raise_alarm': 5} | L5 5, L2 3, L6 2; gap 5 | enemy_count>=3 5, allies=0 5, alarm=false 5 |
| wounded_vs_alarm | 5 | 3 | None | -/- | -/3 | {'raise_alarm': 2, 'drink_potion': 2, 'melee_attack': 1} | L1 4, L4 3, L5 3; gap 5 | enemy=mage 3, distance>=10 3, alarm=false 2, potion=true 2 |
| troll_shoot_allied | 5 | 4 | shoot | 5/5 | 4/4 | {'shoot': 5} | L2 5, L3 5; gap 2 | allies>=2 4, arrows>=1 2, distance>=2 2, distance>=4 1 |
| weak_mage_shoot | 5 | 4 | shoot | 5/5 | 4/4 | {'shoot': 5} | L4 5, L2 4, L5 3; gap 5 | enemy=mage 5, enemy_hp<=10 3, enemy_hp<=30 2, arrows>=6 1 |
| near_fine_hold | 5 | 4 | hold_position | 5/5 | 4/4 | {'hold_position': 5} | L7 5, L1 2; gap 4 | enemy=none 5, hp>=32 3, time=day 1, hp<=32 1 |
| night_alone_cover | 4 | 4 | take_cover | 4/4 | 4/4 | {'take_cover': 4} | L6 4; gap 3 | arrows=0 4, cover=true 4, time=night 3, allies=0 1 |
| troll_alone_cover | 4 | 3 | take_cover | 4/4 | 3/3 | {'take_cover': 4} | L6 4, L3 4, L2 1; gap 4 | enemy=troll 4, allies=0 4, cover=true 4 |
| mage_shoot | 4 | 3 | shoot | 4/4 | 3/3 | {'shoot': 4} | L2 4, L4 4 | enemy=mage 4, arrows>=4 2, distance>=6 1, arrows>=7 1 |
| orc_pair_day_shoot | 4 | 3 | shoot | 4/4 | 3/3 | {'shoot': 4} | L2 4; gap 1 | distance>=12 2, arrows>=1 2, distance>=2 2, allies>=3 1 |
| mage_no_arrows | 4 | 4 | None | -/- | -/4 | {'hold_position': 3, 'drink_potion': 1} | L4 1, L1 1; gap 4 | arrows=0 4, cover=false 2, distance>=12 1, hp>=82 1 |
| mage_close_melee | 3 | 3 | melee_attack | 3/3 | 3/3 | {'melee_attack': 3} | L4 3, L2 1; gap 3 | enemy=mage 3, arrows=0 3, distance<=2 2, hp>=90 1 |
| hurt_retreat | 3 | 3 | retreat | 3/3 | 3/3 | {'retreat': 3} | L1 3, L0 1, L5 1; gap 1 | potion=false 3, hp<=30 1, hp<=20 1, hp<=7 1 |
| hurt_troll_alarm | 3 | 3 | raise_alarm | 3/3 | 3/3 | {'raise_alarm': 3} | L5 3, L1 3, L3 1; gap 3 | alarm=false 3, enemy=troll 3, distance>=12 1, distance>=10 1 |
| orc_alone_noarrow_alarm | 3 | 3 | raise_alarm | 3/3 | 3/3 | {'raise_alarm': 3} | L5 3; gap 3 | alarm=false 3, enemy_count>=2 3, allies=0 2, allies<=0 1 |
| mage_no_arrows_cover | 3 | 3 | take_cover | 3/3 | 3/3 | {'take_cover': 3} | ; gap 3 | arrows=0 3, cover=true 3, enemy=mage 2, distance>=6 1 |
| hurt_horde_alarm | 3 | 3 | raise_alarm | 3/3 | 3/3 | {'raise_alarm': 3} | L5 3, L1 3, L6 1; gap 3 | alarm=false 3, enemy_count>=4 2, allies=0 1, distance>=5 1 |
| wounded_mage_alarm | 3 | 2 | raise_alarm | 3/3 | 2/2 | {'raise_alarm': 3} | L1 3, L5 3, L4 1; gap 3 | alarm=false 3, enemy=mage 3, enemy_count>=4 1, hp<=21 1 |
| weak_mage_unclear | 3 | 2 | None | -/- | -/2 | {'raise_alarm': 2, 'shoot': 1} | L4 3, L5 3, L2 1; gap 3 | alarm=false 2, enemy=mage 2, enemy_count>=3 1, distance>=12 1 |
| troll_melee_allied | 2 | 2 | melee_attack | 2/2 | 2/2 | {'melee_attack': 2} | L2 2, L3 2 | distance<=1 2, enemy=troll 1, allies>=1 1, allies>=2 1 |
| hurt_vs_alarm | 1 | 1 | None | -/- | -/1 | {'drink_potion': 1} | L5 1, L1 1, L3 1; gap 1 | hp<=20 1, potion=true 1, enemy=troll 1 |
| weak_troll_alone | 1 | 1 | None | -/- | -/1 | {'hold_position': 1} | L0 1, L3 1; gap 1 | enemy_hp<=10 1, hp>=83 1, arrows=0 1 |

## 食い違いと棄権の例(全部。[根拠] 決め手 「理由」 会話)
### shoot_far
- 方針=shoot 審判=raise_alarm [L5,L6+gap] alarm=false,time=night,enemy_count>=3 「夜に小鬼の群れが来た、遠いうちに警報を鳴らす」 (round2_s1) | hp=90 enemy=goblin distance=7 enemy_count=3 enemy_hp=80 allies=1 potion=True arrows=13 cover=True alarm=False post=wall time=night
- 方針=shoot 審判=take_cover [L0,L2+gap] hp<=38,enemy_count>=4,cover=true 「体力が減り小鬼4体、警報済みなので隠れて援軍を待つ」 (round2_s2) | hp=38 enemy=goblin distance=2 enemy_count=4 enemy_hp=70 allies=1 potion=False arrows=1 cover=True alarm=True post=gate time=day
### no_arrows_cover_day
- 方針=hold_position 審判=raise_alarm [L5] alarm=false,enemy_count>=2,arrows=0 「オーク二体が門へ迫り警報が未だ、射れないので鳴らす」 (round5_s2) | hp=64 enemy=orc distance=9 enemy_count=2 enemy_hp=70 allies=1 potion=True arrows=0 cover=True alarm=False post=gate time=day
- 方針=hold_position 審判=take_cover [L0+gap] arrows=0,enemy_count>=5,cover=true 「矢が無く多勢の小鬼、警報済みなので遮蔽で接近を待つ」 (round4_s2) | hp=82 enemy=goblin distance=6 enemy_count=5 enemy_hp=80 allies=3 potion=True arrows=0 cover=True alarm=True post=gate time=day
- 方針=hold_position 審判=take_cover [gap] arrows=0,distance>=8,hp<=47 「矢が無く射れず、体力半分で単独なので遮蔽で待つ」 (round5_s2) | hp=47 enemy=goblin distance=8 enemy_count=1 enemy_hp=40 allies=0 potion=False arrows=0 cover=True alarm=False post=wall time=day
### orc_alarm_unclear
- 方針=None 審判=melee_attack [L2] distance<=1,hp>=34 「隣接したオークと近接で戦う」 (round2_s3) | hp=82 enemy=orc distance=1 enemy_count=2 enemy_hp=80 allies=0 potion=False arrows=3 cover=False alarm=False post=gate time=night
- 方針=None 審判=melee_attack [L2,L5+gap] distance<=1,enemy_hp<=20 「隣接する瀕死のオークを先に倒すのが最善」 (round3_s1) | hp=94 enemy=orc distance=1 enemy_count=2 enemy_hp=20 allies=0 potion=False arrows=20 cover=True alarm=False post=gate time=day
- 方針=None 審判=melee_attack [L2] distance<=1,enemy_hp<=20,hp>=94 「隣接する弱ったオークを近接で仕留める」 (round5_s1) | hp=94 enemy=orc distance=1 enemy_count=2 enemy_hp=20 allies=0 potion=False arrows=20 cover=True alarm=False post=gate time=day
- 方針=None 審判=melee_attack [L2,L5+gap] distance<=1,enemy_hp<=20,hp>=94 「隣接の敵は瀕死、警報より先に仕留める方が得」 (round5_s2) | hp=94 enemy=orc distance=1 enemy_count=2 enemy_hp=20 allies=0 potion=False arrows=20 cover=True alarm=False post=gate time=day
- 方針=None 審判=raise_alarm [L2,L5,L6+gap] alarm=false,allies=0,time=night 「夜の門で単独、オーク2体に先に警報を鳴らす」 (round1_s2) | hp=82 enemy=orc distance=1 enemy_count=2 enemy_hp=80 allies=0 potion=False arrows=3 cover=False alarm=False post=gate time=night
- 方針=None 審判=raise_alarm [L5,L6+gap] alarm=false,enemy_count>=2,allies=0 「夜に単独でオーク二体、斬り合う前に警報を鳴らす」 (round2_s1) | hp=82 enemy=orc distance=1 enemy_count=2 enemy_hp=80 allies=0 potion=False arrows=3 cover=False alarm=False post=gate time=night
- 方針=None 審判=raise_alarm [L5,L2+gap] allies=0,enemy_count>=2,alarm=false 「単独でオーク二体、距離のあるうちに警報」 (round3_s1) | hp=96 enemy=orc distance=7 enemy_count=2 enemy_hp=30 allies=0 potion=True arrows=4 cover=False alarm=False post=gate time=day
- 方針=None 審判=raise_alarm [L5,L2+gap] alarm=false,enemy_count>=3,enemy=orc 「オーク三体は深刻、矢一本より警報が先」 (round3_s2) | hp=61 enemy=orc distance=8 enemy_count=3 enemy_hp=40 allies=1 potion=True arrows=1 cover=True alarm=False post=corridor time=day
- 方針=None 審判=raise_alarm [L5,L2+gap] alarm=false,enemy_count>=3,allies>=2 「オーク三体で未警報、隣の敵は味方に任す」 (round3_s2) | hp=55 enemy=orc distance=1 enemy_count=3 enemy_hp=20 allies=2 potion=True arrows=2 cover=False alarm=False post=wall time=day
- 方針=None 審判=raise_alarm [L5,L2+gap] enemy_count>=3,alarm=false,allies<=1 「無傷に近いオーク3体は深刻、まず警報を鳴らす」 (round5_s1) | hp=73 enemy=orc distance=4 enemy_count=3 enemy_hp=90 allies=1 potion=False arrows=2 cover=True alarm=False post=gate time=day
- 方針=None 審判=raise_alarm [L5,L2+gap] enemy_count>=3,alarm=false 「オーク3体が門に迫る、射るより先に警報」 (round5_s1) | hp=82 enemy=orc distance=3 enemy_count=3 enemy_hp=40 allies=2 potion=False arrows=3 cover=False alarm=False post=gate time=day
- 方針=None 審判=raise_alarm [L5] alarm=false,enemy_count>=3,arrows=0 「オーク三体は深刻な脅威で警報が未だなので鳴らす」 (round5_s2) | hp=91 enemy=orc distance=7 enemy_count=3 enemy_hp=40 allies=3 potion=True arrows=0 cover=True alarm=False post=wall time=day
- 方針=None 審判=raise_alarm [L2,L5+gap] alarm=false,allies=0,enemy_count>=2 「夜に単独でオーク二体、斬るより先に警報で助けを呼ぶ」 (round5_s2) | hp=71 enemy=orc distance=1 enemy_count=2 enemy_hp=70 allies=0 potion=False arrows=9 cover=False alarm=False post=wall time=night
- 方針=None 審判=raise_alarm [L2,L5+gap] alarm=false,allies=0,enemy_count>=2 「単独でオーク二体、矢四本では足りず先に警報を鳴らす」 (round5_s2) | hp=96 enemy=orc distance=7 enemy_count=2 enemy_hp=30 allies=0 potion=True arrows=4 cover=False alarm=False post=gate time=day
- 方針=None 審判=retreat [L1,L0] hp<=36,potion=false,allies=0 「重傷で薬も味方も無く隣接二体、無駄死にせず退く」 (round5_s1) | hp=36 enemy=orc distance=1 enemy_count=2 enemy_hp=100 allies=0 potion=False arrows=5 cover=False alarm=False post=gate time=day
- 方針=None 審判=shoot [L2] distance>=2,arrows>=1 「離れたオークを矢で射る」 (round2_s3) | hp=98 enemy=orc distance=4 enemy_count=2 enemy_hp=30 allies=0 potion=False arrows=8 cover=False alarm=False post=corridor time=day
- 方針=None 審判=shoot [L2] distance>=7,arrows=4,hp>=96 「敵は離れ矢があり体力も十分、弓で射る」 (round5_s1) | hp=96 enemy=orc distance=7 enemy_count=2 enemy_hp=30 allies=0 potion=True arrows=4 cover=False alarm=False post=gate time=day
### no_arrows_cover
- 方針=None 審判=drink_potion [L1,L6+gap] hp<=33,potion=true,time=night 「夜で体力も心細い、敵が来る前に飲む」 (round3_s2) | hp=33 enemy=goblin distance=4 enemy_count=1 enemy_hp=40 allies=2 potion=True arrows=0 cover=True alarm=False post=corridor time=night
- 方針=None 審判=hold_position [gap] arrows=0,distance>=7,enemy=goblin 「矢が無く小鬼は遠い、門で迎え撃つ構え」 (round2_s1) | hp=97 enemy=goblin distance=7 enemy_count=2 enemy_hp=70 allies=2 potion=False arrows=0 cover=True alarm=True post=gate time=night
- 方針=None 審判=hold_position [gap] arrows=0,distance>=8,alarm=true 「矢が無く敵は遠い、警報済みで通路を固める」 (round2_s1) | hp=90 enemy=goblin distance=8 enemy_count=4 enemy_hp=40 allies=1 potion=False arrows=0 cover=True alarm=True post=corridor time=night
- 方針=None 審判=hold_position [gap] arrows=0,distance>=2,allies>=3 「矢が無いので味方と持ち場で迎え撃つ」 (round3_s1) | hp=82 enemy=goblin distance=2 enemy_count=2 enemy_hp=80 allies=3 potion=False arrows=0 cover=True alarm=True post=corridor time=night
- 方針=None 審判=hold_position [gap] enemy=goblin,enemy_hp<=30,arrows=0 「弱いゴブリン一体、持ち場で迎え撃つ」 (round3_s1) | hp=91 enemy=goblin distance=4 enemy_count=1 enemy_hp=30 allies=0 potion=True arrows=0 cover=True alarm=False post=corridor time=night
- 方針=None 審判=raise_alarm [L5,L6+gap] time=night,allies=0,arrows=0 「夜に単独で射てず、用心して警報を鳴らす」 (round3_s1) | hp=96 enemy=orc distance=7 enemy_count=1 enemy_hp=100 allies=0 potion=True arrows=0 cover=True alarm=False post=gate time=night
- 方針=None 審判=raise_alarm [L5,L6+gap] enemy_count>=3,alarm=false,time=night 「夜の門に小鬼三体、未警報なので鳴らす」 (round3_s2) | hp=39 enemy=goblin distance=3 enemy_count=3 enemy_hp=70 allies=2 potion=False arrows=0 cover=True alarm=False post=gate time=night
- 方針=None 審判=take_cover [L6] time=night,arrows=0,cover=true 「夜で矢も無い、遮蔽に隠れて接近を待つ」 (round2_s2) | hp=65 enemy=orc distance=12 enemy_count=2 enemy_hp=20 allies=2 potion=False arrows=0 cover=True alarm=True post=corridor time=night
- 方針=None 審判=take_cover [L6] time=night,arrows=0,cover=true 「夜で矢も無い、遮蔽に隠れて接近を待つ」 (round2_s2) | hp=82 enemy=orc distance=11 enemy_count=1 enemy_hp=50 allies=2 potion=False arrows=0 cover=True alarm=True post=gate time=night
- 方針=None 審判=take_cover [L6+gap] arrows=0,time=night,cover=true 「矢が無い夜、遮蔽に隠れて寄るのを待つ」 (round2_s3) | hp=95 enemy=goblin distance=12 enemy_count=1 enemy_hp=40 allies=0 potion=False arrows=0 cover=True alarm=False post=gate time=night
- 方針=None 審判=take_cover [L6] time=night,arrows=0,cover=true 「夜で矢が無い、遮蔽に隠れて接近を待つ」 (round3_s2) | hp=93 enemy=goblin distance=7 enemy_count=1 enemy_hp=20 allies=0 potion=False arrows=0 cover=True alarm=False post=gate time=night
- 方針=None 審判=take_cover [L6] time=night,arrows=0,cover=true 「夜に小鬼四体、矢が無く遮蔽で備える」 (round3_s2) | hp=75 enemy=goblin distance=2 enemy_count=4 enemy_hp=10 allies=1 potion=False arrows=0 cover=True alarm=True post=corridor time=night
- 方針=None 審判=take_cover [L6+gap] time=night,arrows=0,cover=true 「夜で矢が無く、遮蔽に入って小鬼の接近を待つ」 (round4_s1) | hp=87 enemy=goblin distance=3 enemy_count=2 enemy_hp=70 allies=3 potion=True arrows=0 cover=True alarm=False post=gate time=night
- 方針=None 審判=take_cover [L6+gap] time=night,arrows=0,cover=true 「夜で矢が無く、遮蔽でオークの接近を待つ」 (round4_s1) | hp=67 enemy=orc distance=7 enemy_count=1 enemy_hp=10 allies=2 potion=False arrows=0 cover=True alarm=True post=corridor time=night
- 方針=None 審判=take_cover [L6+gap] time=night,cover=true,arrows=0 「夜で矢も無く傷もある、遮蔽で様子を見る」 (round4_s2) | hp=42 enemy=goblin distance=6 enemy_count=2 enemy_hp=30 allies=2 potion=False arrows=0 cover=True alarm=False post=wall time=night
- 方針=None 審判=take_cover [L6] time=night,arrows=0,cover=true 「夜で矢が無い、遮蔽に隠れて小鬼の接近を待つ」 (round5_s1) | hp=96 enemy=goblin distance=3 enemy_count=1 enemy_hp=100 allies=1 potion=True arrows=0 cover=True alarm=False post=corridor time=night
- 方針=None 審判=take_cover [L6] time=night,arrows=0,cover=true 「夜で矢も無いので遮蔽に隠れて敵の接近を待つ」 (round5_s2) | hp=85 enemy=goblin distance=7 enemy_count=1 enemy_hp=100 allies=3 potion=False arrows=0 cover=True alarm=True post=wall time=night
### mage_alarm
- 方針=raise_alarm 審判=shoot [L4,L5+gap] enemy=mage,enemy_count=1,arrows>=11 「魔術師単独なら警報より先に射て早く仕留める」 (round1_s2) | hp=84 enemy=mage distance=6 enemy_count=1 enemy_hp=40 allies=0 potion=True arrows=11 cover=True alarm=False post=gate time=day
### wounded_retreat
- 方針=retreat 審判=shoot [L1,L2+gap] enemy_hp<=10,enemy_count<=1,distance>=7 「傷は深いが遠くの瀕死ゴブリン一体を射止める」 (round2_s3) | hp=26 enemy=goblin distance=7 enemy_count=1 enemy_hp=10 allies=1 potion=False arrows=9 cover=False alarm=False post=wall time=day
### hp_ambiguous
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp<=31,potion=false 「深手寸前だが脅威が無く退く理由が薄いので持ち場を守る」 (round5_s2) | hp=31 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=12 cover=True alarm=False post=gate time=day
- 方針=None 審判=retreat [L1,L6+gap] hp<=31,potion=false,time=night 「夜に体力が低く薬も無い、無理せず退く」 (round2_s1) | hp=31 enemy=goblin distance=9 enemy_count=3 enemy_hp=40 allies=1 potion=False arrows=5 cover=False alarm=True post=wall time=night
- 方針=None 審判=retreat [L1,L6+gap] hp<=32,potion=false,time=night 「夜に体力が低く薬も無い、門を味方に任せ退く」 (round2_s1) | hp=32 enemy=orc distance=9 enemy_count=3 enemy_hp=20 allies=3 potion=False arrows=15 cover=True alarm=True post=gate time=night
- 方針=None 審判=retreat [L1,L6,L2+gap] hp<=31,enemy_count>=4,potion=false 「深手で夜にオーク4体、薬も遮蔽も無く退く」 (round2_s2) | hp=31 enemy=orc distance=10 enemy_count=4 enemy_hp=90 allies=1 potion=False arrows=2 cover=False alarm=True post=corridor time=night
- 方針=None 審判=retreat [L1,L2+gap] hp<=33,potion=false,alarm=true 「深手で薬も無い、警報済みなので退く」 (round2_s3) | hp=31 enemy=goblin distance=9 enemy_count=3 enemy_hp=40 allies=1 potion=False arrows=5 cover=False alarm=True post=wall time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=33,potion=false,allies>=1 「深手で薬も無い、味方に門を任せて退く」 (round2_s3) | hp=31 enemy=none distance=None enemy_count=0 enemy_hp=None allies=3 potion=False arrows=15 cover=False alarm=False post=gate time=night
- 方針=None 審判=retreat [L1,L2+gap] hp<=32,potion=false,enemy_count>=3 「深手で薬が無く、オーク三体が来る前に退く」 (round4_s1) | hp=32 enemy=orc distance=10 enemy_count=3 enemy_hp=80 allies=2 potion=False arrows=5 cover=True alarm=True post=gate time=day
- 方針=None 審判=retreat [L1] hp<=31,potion=false 「重傷で薬が無く、単独で無傷のオークには退く」 (round5_s1) | hp=31 enemy=orc distance=3 enemy_count=1 enemy_hp=100 allies=0 potion=False arrows=5 cover=True alarm=False post=gate time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=31,potion=false,alarm=true 「警報下で重傷かつ薬無し、敵が来る前に退き立て直す」 (round5_s1) | hp=31 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=9 cover=False alarm=True post=gate time=day
- 方針=None 審判=shoot [L2+gap] distance>=2,arrows>=1,hp>=31 「手負いだが敵は遠く、射るだけなら危険は小さい」 (round1_s1) | hp=31 enemy=goblin distance=9 enemy_count=3 enemy_hp=40 allies=1 potion=False arrows=5 cover=False alarm=True post=wall time=night
- 方針=None 審判=shoot [L2] distance>=6,arrows>=18 「敵は離れ矢も十分、深手ほどではなく射る」 (round2_s2) | hp=32 enemy=goblin distance=6 enemy_count=2 enemy_hp=80 allies=1 potion=False arrows=18 cover=False alarm=True post=gate time=day
### orc_night_alarm
- 方針=raise_alarm 審判=shoot [L2] distance>=2,arrows>=1,enemy_hp<=20 「離れた手負いのオークを矢で射る」 (round2_s3) | hp=99 enemy=orc distance=3 enemy_count=2 enemy_hp=20 allies=0 potion=True arrows=11 cover=False alarm=False post=corridor time=night
### wounded_alone_hold
- 方針=hold_position 審判=retreat [L1,L7+gap] hp<=28,potion=false,allies=0 「深手で薬も無く夜に単独、今のうちに退く」 (round2_s2) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=True alarm=False post=gate time=night
### troll_no_arrows
- 方針=None 審判=hold_position [L3+gap] arrows=0,distance>=12,allies>=3 「矢が無く敵は遠い、味方3人と門を固めて待つ」 (round1_s2) | hp=92 enemy=troll distance=12 enemy_count=5 enemy_hp=40 allies=3 potion=True arrows=0 cover=True alarm=True post=gate time=day
- 方針=None 審判=hold_position [gap] allies>=3,arrows=0,distance>=9 「トロルは遠く矢も無い、味方がいるので門を固める」 (round5_s2) | hp=87 enemy=troll distance=9 enemy_count=4 enemy_hp=80 allies=3 potion=False arrows=0 cover=True alarm=True post=gate time=day
- 方針=None 審判=retreat [L1,L3] hp<=35,potion=false,arrows=0 「重傷で薬も矢も無い、トロルは味方に任せ退く」 (round5_s1) | hp=35 enemy=troll distance=12 enemy_count=1 enemy_hp=20 allies=2 potion=False arrows=0 cover=False alarm=True post=corridor time=day
- 方針=None 審判=take_cover [L3+gap] enemy=troll,arrows=0,cover=true 「矢が無く体力も半ば、迫るトロルに備え隠れる」 (round2_s2) | hp=42 enemy=troll distance=4 enemy_count=2 enemy_hp=60 allies=1 potion=False arrows=0 cover=True alarm=True post=gate time=day
- 方針=None 審判=take_cover [L6] time=night,arrows=0,cover=true 「夜にトロルが迫り矢も無いので遮蔽から味方と迎える」 (round5_s2) | hp=82 enemy=troll distance=4 enemy_count=2 enemy_hp=60 allies=3 potion=False arrows=0 cover=True alarm=True post=gate time=night
- 方針=None 審判=take_cover [L6] time=night,arrows=0,cover=true 「夜にトロルが迫り矢も無いので遮蔽から味方と迎える」 (round5_s2) | hp=84 enemy=troll distance=4 enemy_count=1 enemy_hp=80 allies=2 potion=True arrows=0 cover=True alarm=True post=wall time=night
### worn_cover_day
- 方針=None 審判=hold_position [gap] arrows=0,distance>=2,allies>=3 「矢が無く敵は一歩先、無理に出ず門で迎える」 (round2_s1) | hp=37 enemy=orc distance=2 enemy_count=1 enemy_hp=30 allies=3 potion=False arrows=0 cover=True alarm=True post=gate time=day
- 方針=None 審判=retreat [L1] hp<=37,potion=false,allies>=3 「重傷で薬が無い、弱ったオークは味方に任せ退く」 (round5_s1) | hp=37 enemy=orc distance=2 enemy_count=1 enemy_hp=30 allies=3 potion=False arrows=0 cover=True alarm=True post=gate time=day
- 方針=None 審判=take_cover [gap] hp<=42,potion=false,arrows=0 「矢も薬も無く体力半分以下、遮蔽で門に踏み止まる」 (round1_s2) | hp=42 enemy=goblin distance=4 enemy_count=3 enemy_hp=60 allies=3 potion=False arrows=0 cover=True alarm=True post=gate time=day
- 方針=None 審判=take_cover [L0+gap] arrows=0,hp<=42,cover=true 「矢が無く傷も浅くないので遮蔽で接近を待つ」 (round4_s1) | hp=42 enemy=goblin distance=4 enemy_count=3 enemy_hp=60 allies=3 potion=False arrows=0 cover=True alarm=True post=gate time=day
- 方針=None 審判=take_cover [gap] arrows=0,distance>=4,cover=true 「矢が無く敵は遠い、傷もあるので遮蔽で待つ」 (round4_s2) | hp=42 enemy=goblin distance=4 enemy_count=3 enemy_hp=60 allies=3 potion=False arrows=0 cover=True alarm=True post=gate time=day
- 方針=None 審判=take_cover [gap] hp<=37,arrows=0,allies>=3 「手負いだが瀕死ではなく、弱った敵は味方に任せ遮蔽へ」 (round5_s2) | hp=37 enemy=orc distance=2 enemy_count=1 enemy_hp=30 allies=3 potion=False arrows=0 cover=True alarm=True post=gate time=day
### wounded_vs_alarm
- 方針=None 審判=drink_potion [L1,L5+gap] hp<=28,potion=true,distance>=10 「重傷で敵は遠い、今のうちに薬を飲む」 (round3_s1) | hp=28 enemy=mage distance=10 enemy_count=2 enemy_hp=80 allies=2 potion=True arrows=10 cover=False alarm=False post=wall time=night
- 方針=None 審判=drink_potion [L1+gap] hp<=31,potion=true,distance>=7 「体力が三割、敵が遠いうちに薬を飲む」 (round3_s1) | hp=31 enemy=goblin distance=7 enemy_count=4 enemy_hp=60 allies=3 potion=True arrows=19 cover=False alarm=False post=wall time=day
- 方針=None 審判=melee_attack [L2,L4,L1+gap] enemy=mage,distance<=1,enemy_hp<=20 「隣の瀕死の魔術師を倒せば脅威が消える」 (round3_s1) | hp=30 enemy=mage distance=1 enemy_count=1 enemy_hp=20 allies=1 potion=True arrows=3 cover=True alarm=False post=gate time=day
- 方針=None 審判=raise_alarm [L4,L5+gap] enemy=mage,alarm=false,distance>=10 「深手だが魔術師はまだ遠い、先に警報を鳴らす」 (round1_s1) | hp=28 enemy=mage distance=10 enemy_count=2 enemy_hp=80 allies=2 potion=True arrows=10 cover=False alarm=False post=wall time=night
- 方針=None 審判=raise_alarm [L5,L1,L4+gap] alarm=false,enemy=mage,distance>=10 「魔術師が遠いうちに警報、回復は次」 (round3_s2) | hp=28 enemy=mage distance=10 enemy_count=2 enemy_hp=80 allies=2 potion=True arrows=10 cover=False alarm=False post=wall time=night
### mage_no_arrows
- 方針=None 審判=drink_potion [L1,L4+gap] hp<=39,potion=true,arrows=0 「深手で矢も無く魔術師に届かず、先に回復する」 (round4_s1) | hp=39 enemy=mage distance=3 enemy_count=1 enemy_hp=50 allies=1 potion=True arrows=0 cover=False alarm=True post=gate time=day
- 方針=None 審判=hold_position [gap] arrows=0,distance>=12 「矢が無く魔術師は遠い、持ち場を守る」 (round3_s1) | hp=93 enemy=mage distance=12 enemy_count=2 enemy_hp=30 allies=3 potion=True arrows=0 cover=False alarm=True post=gate time=day
- 方針=None 審判=hold_position [gap] arrows=0,cover=false,hp>=82 「矢も遮蔽も無いが体力はある、門を守る」 (round3_s2) | hp=82 enemy=mage distance=8 enemy_count=1 enemy_hp=80 allies=0 potion=False arrows=0 cover=False alarm=True post=gate time=day
- 方針=None 審判=hold_position [gap] arrows=0,cover=false,hp>=51 「魔術師を射る矢も遮蔽も無いが体力は保つので門に留まる」 (round5_s2) | hp=51 enemy=mage distance=10 enemy_count=1 enemy_hp=90 allies=0 potion=False arrows=0 cover=False alarm=True post=gate time=night
### weak_mage_unclear
- 方針=None 審判=raise_alarm [L5,L4+gap] alarm=false,enemy_count>=3,distance>=12 「魔術師込み三体、遠いうちに警報」 (round3_s2) | hp=99 enemy=mage distance=12 enemy_count=3 enemy_hp=30 allies=1 potion=False arrows=17 cover=False alarm=False post=gate time=day
- 方針=None 審判=raise_alarm [L5,L4+gap] alarm=false,enemy=mage,arrows=1 「夜の遠距離で矢は1本、確実な警報を先にする」 (round5_s1) | hp=86 enemy=mage distance=12 enemy_count=1 enemy_hp=30 allies=1 potion=True arrows=1 cover=True alarm=False post=gate time=night
- 方針=None 審判=shoot [L4,L2,L5+gap] enemy=mage,enemy_hp<=20,arrows=18 「瀕死の魔術師が射程内、一射で仕留めるのを優先」 (round5_s1) | hp=75 enemy=mage distance=6 enemy_count=3 enemy_hp=20 allies=3 potion=False arrows=18 cover=False alarm=False post=gate time=day
### hurt_vs_alarm
- 方針=None 審判=drink_potion [L1,L3,L5+gap] hp<=20,potion=true,enemy=troll 「瀕死でトロルが隣、まず回復薬で持ちこたえる」 (round2_s3) | hp=14 enemy=troll distance=1 enemy_count=1 enemy_hp=10 allies=0 potion=True arrows=3 cover=False alarm=False post=corridor time=day
### weak_troll_alone
- 方針=None 審判=hold_position [L0,L3+gap] enemy_hp<=10,hp>=83,arrows=0 「瀕死のトロルなら門で迎え撃てる」 (round3_s2) | hp=83 enemy=troll distance=5 enemy_count=1 enemy_hp=10 allies=0 potion=False arrows=0 cover=False alarm=True post=gate time=day

## 訊き直した状態(同じ状態を会話 3 本以上に訊いた。24 件のうち票が割れたもの 8 件)
- 票 {'hold_position': 2, 'retreat': 1} | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=True alarm=False post=gate time=night | hold_position「深手だが敵はなく、夜の門を空けず持ち場に留まる」 / retreat「深手で薬も無く夜に単独、今のうちに退く」 / hold_position「脅威が無く単独、門を空けず持ち場を守る」
- 票 {'shoot': 1, 'retreat': 2} | hp=31 enemy=goblin distance=9 enemy_count=3 enemy_hp=40 allies=1 potion=False arrows=5 cover=False alarm=True post=wall time=night | shoot「手負いだが敵は遠く、射るだけなら危険は小さい」 / retreat「夜に体力が低く薬も無い、無理せず退く」 / retreat「深手で薬も無い、警報済みなので退く」
- 票 {'raise_alarm': 2, 'drink_potion': 1} | hp=28 enemy=mage distance=10 enemy_count=2 enemy_hp=80 allies=2 potion=True arrows=10 cover=False alarm=False post=wall time=night | raise_alarm「深手だが魔術師はまだ遠い、先に警報を鳴らす」 / drink_potion「重傷で敵は遠い、今のうちに薬を飲む」 / raise_alarm「魔術師が遠いうちに警報、回復は次」
- 票 {'raise_alarm': 2, 'melee_attack': 1} | hp=82 enemy=orc distance=1 enemy_count=2 enemy_hp=80 allies=0 potion=False arrows=3 cover=False alarm=False post=gate time=night | raise_alarm「夜の門で単独、オーク2体に先に警報を鳴らす」 / raise_alarm「夜に単独でオーク二体、斬り合う前に警報を鳴らす」 / melee_attack「隣接したオークと近接で戦う」
- 票 {'hold_position': 1, 'retreat': 1, 'take_cover': 1} | hp=37 enemy=orc distance=2 enemy_count=1 enemy_hp=30 allies=3 potion=False arrows=0 cover=True alarm=True post=gate time=day | hold_position「矢が無く敵は一歩先、無理に出ず門で迎える」 / retreat「重傷で薬が無い、弱ったオークは味方に任せ退く」 / take_cover「手負いだが瀕死ではなく、弱った敵は味方に任せ遮蔽へ」
- 票 {'hold_position': 2, 'take_cover': 1} | hp=47 enemy=goblin distance=8 enemy_count=1 enemy_hp=40 allies=0 potion=False arrows=0 cover=True alarm=False post=wall time=day | hold_position「矢が無く小鬼一体は遠い、持ち場で待ち構える」 / hold_position「矢は無いが相手は弱った小鬼、持ち場で待つ」 / take_cover「矢が無く射れず、体力半分で単独なので遮蔽で待つ」
- 票 {'raise_alarm': 2, 'shoot': 1} | hp=96 enemy=orc distance=7 enemy_count=2 enemy_hp=30 allies=0 potion=True arrows=4 cover=False alarm=False post=gate time=day | raise_alarm「単独でオーク二体、距離のあるうちに警報」 / shoot「敵は離れ矢があり体力も十分、弓で射る」 / raise_alarm「単独でオーク二体、矢四本では足りず先に警報を鳴らす」
- 票 {'hold_position': 2, 'raise_alarm': 1} | hp=64 enemy=orc distance=9 enemy_count=2 enemy_hp=70 allies=1 potion=True arrows=0 cover=True alarm=False post=gate time=day | hold_position「矢が無く二対二、持ち場で迎え撃つ」 / hold_position「矢が無く敵は遠い、門で迎え撃つ構えで待つ」 / raise_alarm「オーク二体が門へ迫り警報が未だ、射れないので鳴らす」

## 根拠が gap に偏り、答えが割れている枝(輪が同じ状態を複数の会話に訊き直している。会話の癖か、状態の違いかは、訊き直しの票で分かる)
- 枝 wounded_retreat: 審判の答え {'retreat': 11, 'shoot': 1}
- 枝 wounded_alone_hold: 審判の答え {'hold_position': 7, 'retreat': 1}
- 枝 hp_ambiguous: 審判の答え {'shoot': 2, 'retreat': 8, 'hold_position': 1}
- 枝 no_arrows_cover_day: 審判の答え {'hold_position': 29, 'take_cover': 2, 'raise_alarm': 1}
- 枝 wounded_vs_alarm: 審判の答え {'raise_alarm': 2, 'drink_potion': 2, 'melee_attack': 1}
- 枝 mage_alarm: 審判の答え {'raise_alarm': 15, 'shoot': 1}
- 枝 troll_no_arrows: 審判の答え {'hold_position': 2, 'take_cover': 3, 'retreat': 1}
- 枝 worn_cover_day: 審判の答え {'take_cover': 4, 'hold_position': 1, 'retreat': 1}
- 枝 orc_alarm_unclear: 審判の答え {'raise_alarm': 10, 'shoot': 2, 'melee_attack': 4, 'retreat': 1}
- 枝 orc_night_alarm: 審判の答え {'raise_alarm': 9, 'shoot': 1}
- 枝 no_arrows_cover: 審判の答え {'hold_position': 4, 'take_cover': 10, 'raise_alarm': 2, 'drink_potion': 1}
- 枝 mage_no_arrows: 審判の答え {'hold_position': 3, 'drink_potion': 1}
- 枝 weak_mage_unclear: 審判の答え {'raise_alarm': 2, 'shoot': 1}

## 出力
`/home/claude/sekizui/jit/auto_runs/r3/policies/c5.py` に書く。書いたら「完了」とだけ返す。