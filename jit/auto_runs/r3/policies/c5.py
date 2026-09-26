"""走り r3 の方針、第 5 版(c5)。前の版は c4。

帳簿: 審判のラベル 417 件、会話 12 本(round1_s1/s2/s3、round2_s1/s2/s3、round3_s1/s2、
round4_s1/s2、round5_s1/s2。以下 r1s1 … r5s2)。範囲の番人は c4 のまま。

c4 の答える枝は、417 件で数え直しても全部が門を通る(一致 80% 以上、別の答えを多数にした
会話は 1 本以下。いちばん低いのは wounded_alone_hold 7/8、no_arrows_cover_day 29/32)ので、
追補 A1・A2 に重なる所の外は条件を変えない。この版で変えたのは、(一)追補 A1・A2 をそのまま
読んだ枝を入れたこと、(二)round5 の 2 本が加わって会話の多数が揃った番人の一部を答える枝に
したこと。

「ひどく傷ついている」の線について
    A1・A2 は「ひどく傷ついていなければ」を hp>36 と書く(_SEVERE_MAX)。この線は A1・A2 に
    重なる所と、その隣で新しく答える枝(下の 2. と 5.)だけに使う。全体の線 _FINE_MIN=33 は
    動かさない: 敵なしの hp 33〜36 は no_threat_hold(64/64)が hold と答えていて、敵ありの
    hp 33〜36 は retreat 2(r5s1 hp36 オーク、r5s1 hp35 トロル)と drink 1(r3s2 hp33)しか
    なく、会話 2 本で答えも二つに分かれる。

この版で変えたこと
 1. orc_serious_alarm(新しい枝、追補 A1 をそのまま読む。規律 (a)):
    条件は A1 の式そのもの(_addendum_a1)→ raise_alarm。置き場所は警報未・オーク 2 体以上の
    所の先頭(horde_alarm、outnumbered_alarm の後)。
    番人 orc_alarm_unclear 17 件のうち 12 件が A1 に入る: raise 10(r1s2、r2s1、r3s1、
    r3s2 2、r5s1 2、r5s2 3)/ melee 1(r2s3、隣接・夜・単独 hp82。訊き直しでは raise 2 /
    melee 1)/ shoot 1(r5s1、昼・単独・矢 4。訊き直しでは raise 2 / shoot 1)。
    決め手 alarm=false 10、allies=0 6、enemy_count>=3 5、enemy_count>=2 4(「オーク三体は
    深刻、矢一本より警報が先」「単独でオーク二体、矢四本では足りず先に警報を鳴らす」「夜に
    単独でオーク二体、斬るより先に警報で助けを呼ぶ」)。
    c4 の orc_alone_noarrow_alarm(3/3、全部 hp83 で A1 の中)はこの枝に吸い込み、名前を
    止める。c4 の orc_night_alarm のうち A1 に入る所(単独、またはオーク 3 体で hp>36)も
    この枝が先に取る。orc_night_alarm の外れ 1 件(r2s3 hp99・単独・夜の shoot)もこちらへ
    移る。帳簿は 12 + 3 + (orc_night_alarm から移る y 件、うち shoot 1)で、外れは 3 件
    (melee 1 r2s3、shoot 2 r5s1・r2s3)、一致は y=0 でも 13/16(81%)。raise 以外を多数に
    した会話は r2s3 の 1 本だけ。
    A1 の外に落ちる hp 33〜36 の単独・昼・矢 0(c4 では orc_alone_noarrow_alarm、例 0)は
    番人 orc_alarm_unclear に戻す。

 2. orc_pair_melee_weak(新しい枝、番人 orc_alarm_unclear から):
    警報未・オーク 2 体・隣接・単独・A1 の外(昼で矢 5 以上)・hp>36・敵の体力 45 以下
    → melee_attack。
    3 件・会話 3 本(r3s1、r5s1、r5s2。訊き直した同じ状態 hp94・敵の体力 20・矢 20・昼・門)・
    一致 3/3。規律 (b)。根拠 L2(2 件は L5+gap も)。決め手 distance<=1 3、enemy_hp<=20 3、
    hp>=94 2(「隣接する瀕死のオークを先に倒すのが最善」「隣接の敵は瀕死、警報より先に
    仕留める方が得」「隣接する弱ったオークを近接で仕留める」)。
    線: 敵の体力は melee の決め手 enemy_hp<=20 と、隣接・単独のオーク二体で raise が出た
    敵の体力 70・80 の間の 45(_WEAK_ORC_MAX)。番兵の体力は A1 の線 hp>36(_SEVERE_MAX)。
    隣接・単独・hp36 で退いた 1 件(r5s1、[L1,L0]、決め手 hp<=36, potion=false, allies=0
    「重傷で薬も味方も無く隣接二体、無駄死にせず退く」、敵の体力 100)は、どちらの線でも
    この枝の外になり、番人 orc_alarm_unclear に残る。

 3. orc_pair_day_shoot を広げる(同じ名前、L2):
    昼・警報未・オーク 2 体・離れ・矢あり・A1 に入らない → shoot。c4 は味方ありだけだった。
    A1 は単独のオーク二体が深刻かを「夜か矢四本以下」で分けているので、その外(昼・矢 5 以上)
    は L2 をそのまま読む。新しく入るのは 1 件(r2s3 hp98・distance 4・矢 8、[L2] gap なし、
    決め手 distance>=2, arrows>=1「離れたオークを矢で射る」)で、規律 (c)。帳簿 5/5。
    hp 33〜36 の単独は A1 の外だが L1 が競うかもしれない(上の hp36 の退き)ので番人に残す。

 4. no_arrows_cover_day を追補 A2 で読み直す(同じ名前、規律 (a)):
    昼・離れ・矢 0・遮蔽の所で、まず A2 の式そのもの(_addendum_a2)に入れば hold_position。
    これで c4 の番人 worn_cover_day(hp 33〜42)のうち A2 に入る 3 件(訊き直した hp37・
    オーク 1 体・distance 2・味方 3・警報済み: hold 1 r2s1 / retreat 1 r5s1 / take_cover 1
    r5s2)を A2 のとおり hold と答える。A2 の外で hp>=43 の所(敵 3 体以上)は c4 のまま
    hold で、同じ名前で答える(下の 5. の take_cover は hp<=42 だけ)。
    c4 の外れ 3 件のうち 2 件は A2 に入り、訊き直しの多数も hold: raise 1(r5s2 hp64・
    オーク 2 体・味方 1。訊き直しは hold 2 / raise 1)、take_cover 1(r5s2 hp47・小鬼 1 体・
    単独。訊き直しは hold 2 / take_cover 1)。残る 1 件(r4s2 hp82・小鬼 5 体)は A2 の外。
    数え直し: c4 の 32 件(hold 29)+ hp37 の 3 件 = 35 件、一致 30/35(86%)。会話の多数は
    12 本とも hold のまま(r5s2 は hold 以外が 3 件になるが 1 本だけ)。

 5. worn_crowd_cover(新しい枝、番人 worn_cover_day から):
    昼・離れ・矢 0・遮蔽・A2 の外(敵 3 体以上)・hp 37〜42・薬なし → take_cover。
    3 件・会話 3 本(r1s2、r4s1、r4s2。訊き直した同じ状態 hp42・小鬼 3 体・distance 4・
    味方 3・薬なし・警報済み・門)・一致 3/3。規律 (b)。根拠 gap(1 件は L0+gap)。
    決め手 arrows=0 3、hp<=42 2、cover=true 2、potion=false 1、distance>=4 1(「矢も薬も
    無く体力半分以下、遮蔽で門に踏み止まる」「矢が無く傷も浅くないので遮蔽で接近を待つ」
    「矢が無く敵は遠い、傷もあるので遮蔽で待つ」)。c4 で割れていたのは hp37・敵 1 体の
    hold で、それが A2 に入ったので、A2 の外に残る例は take_cover だけになった。
    線: 上は take_cover の決め手 hp<=42(_WORN_MAX)。下は A2 の線 hp>36(hp35〜37 で退いた
    例が r5s1 に 2 件あり、それより下は L1 が競う)。薬は決め手 potion=false のとおり条件に
    する(薬ありの手負いには drink が出ている: hp39 の魔術師 r4s1、hp33 の夜の小鬼 r3s2)。
    番人 worn_cover_day は残す: 昼・離れ・矢 0・遮蔽・A2 の外・hp 33〜42 のうち、hp 33〜36
    か薬ありの所。いまの例 0。

 6. near_hurt_night_retreat(新しい枝、番人 hp_ambiguous から):
    hp 31〜32・薬なし・敵あり・夜 → retreat。
    6 件・会話 5 本。retreat 5(r2s1 2、r2s2、r2s3、r5s1)/ shoot 1(r1s1)で 83%。会話の
    多数は retreat 4 本 / shoot 1 本。規律 (b)。根拠 L1(+L6、L2、gap。r5s1 は [L1] だけ)。
    決め手 potion=false、hp<=31 / hp<=32、time=night 2、alarm=true 1、enemy_count>=4 1
    (「夜に体力が低く薬も無い、無理せず退く」「夜に体力が低く薬も無い、門を味方に任せ退く」
    「重傷で薬が無く、単独で無傷のオークには退く」)。訊き直した hp31・小鬼 3 体・distance 9・
    夜は retreat 2 / shoot 1。c4 は夜で retreat 4 / shoot 1 のちょうど 80% で止めていたが、
    r5s1 の 1 件([L1]、gap なし)が加わった。
    昼の敵ありは retreat 1(r4s1)/ shoot 1(r2s2)で割れるので番人 hp_ambiguous に残す。
    敵なしの hp31 は retreat 2(r2s3 夜、r5s1 昼)/ hold 1(r5s2 昼)で番人に残す。

 7. mage_no_arrows_hold(新しい枝、番人 mage_no_arrows から):
    警報済みの魔術師・矢 0・distance 3 以上・遮蔽なし・hp 45 以上 → hold_position。
    3 件・会話 3 本(r3s1、r3s2、r5s2)・一致 3/3。規律 (b)。根拠 gap。決め手 arrows=0 3、
    cover=false 2、distance>=12 1、hp>=82 1、hp>=51 1(「矢が無く魔術師は遠い、持ち場を守る」
    「矢も遮蔽も無いが体力はある、門を守る」「魔術師を射る矢も遮蔽も無いが体力は保つので門に
    留まる」)。
    線: drink の hp39(r4s1、薬あり・distance 3、決め手 hp<=39, potion=true「深手で矢も無く
    魔術師に届かず、先に回復する」)と hold の最低 hp51 の間の 45(_MAGE_HOLD_MIN)。距離は
    c4 の mage_close_melee の線(distance<=2 で詰めて斬る、_MAGE_CLOSE_MAX)の外。
    番人 mage_no_arrows は残す: distance 2・遮蔽あり、または hp 44 以下(drink 1)。

変えなかった番人
    no_arrows_cover 17: 夜・離れ・矢 0・遮蔽の残り(take_cover 10 / hold 4 / raise 2 /
        drink 1 で 59%)。会話の多数は take_cover 7 本(r2s2、r2s3、r3s2、r4s1、r4s2、
        r5s1、r5s2)/ hold 2 本(r2s1、r3s1)。味方あり・警報済みは take 5 / hold 3、単独・
        警報未は take 2 / hold 1 / raise 1、味方あり・警報未は take 3 / raise 1 / drink 1。
        どの切り方でも 80% に届かないか、決め手(time=night, arrows=0, cover=true)に無い
        項目で切ることになる。A2 は昼の規則なので夜には使わない。
    troll_no_arrows 6: 警報済みトロル・味方あり・離れ・矢 0(take_cover 3 / hold 2 /
        retreat 1)。夜の 2 件は take_cover([L6]、gap なし)で規律 (c) の形には入るが、
        2 件とも r5s2 の 1 本で理由も同じ文。隣の夜の小鬼・オークの所が会話で割れている
        (r2s1、r3s1 は hold)ので、1 本だけを根拠には答えない。昼・hp87 以上の hold 2
        (r1s2、r5s2)は gap で 2 件、規律 (b)(c) に届かない。
    orc_alarm_unclear 1: A1 の外の残り(隣接・単独・hp36 の retreat 1 r5s1)。hp 33〜36 の
        オーク 2〜3 体と、隣接・単独・昼・矢 5 以上で敵が弱っていない所もここ。
    hp_ambiguous 5: hp 31〜32・薬なしの残り(retreat 3 / hold 1 / shoot 1)。
    wounded_vs_alarm 5: 訊き直した hp28・魔術師・distance 10・薬あり・夜が raise 2 / drink 1
        (67%)、ほかは drink 1(hp31 小鬼 4 体)と melee 1(hp30 隣の瀕死の魔術師)。gap。
    weak_mage_unclear 3: raise 2(r3s2 敵 3 体、r5s1 矢 1)/ shoot 1(r5s1 敵 3 体・瀕死)。
        敵 3 体では raise 1 / shoot 1 で割れる。gap。
    worn_cover_day 0、mage_no_arrows 1、hurt_vs_alarm 1、weak_troll_alone 1: 上のとおり、
        または c4 のまま。例が少ないか割れていて、根拠は gap。

c5 で数え直した帳簿(答える枝、件数・一致・会話)
    no_threat_hold          64  64/64  12 本     L7      敵なし・hp>=33 → hold_position
    shoot_far               38  36/38   9 本     L2      離れたゴブリン/オーク・矢あり → shoot
    no_arrows_cover_day     35  30/35  12 本     A2      昼・矢 0・遮蔽: A2、または hp>=43 → hold(改)
    horde_alarm             18  18/18   8 本     L5      警報未・敵 4 以上 → raise_alarm
    melee_adjacent          17  17/17   8 本     L2      隣接のゴブリン/オーク → melee_attack
    orc_serious_alarm    15+1+y 13+y   7 本以上 A1      A1 の式 → raise_alarm(新)
    mage_alarm              16  15/16   8 本     L5+L4   警報未・離れた魔術師 → raise_alarm
    hurt_no_threat_retreat  13  13/13   5 本     L1      hp<=20・薬なし・敵なし → retreat
    wounded_retreat         12  11/12  10 本     L1      hp 21〜30・薬なし・敵あり → retreat
    wounded_drink           11  11/11   7 本     L1      hp 21〜32・薬あり → drink_potion
    orc_night_alarm       10-1-y  全部一致       L5+L6   警報未のオーク 2〜3・夜・離れ・A1 の外 → raise_alarm
    no_arrows_hold           9   9/9    6 本     gap     離れ・矢 0・遮蔽なし → hold_position
    troll_alarm              8   8/8    5 本     L5+L3   トロル・警報未 → raise_alarm
    wounded_alone_hold       8   7/8    6 本     L7      hp 21〜30・薬なし・敵なし・味方 0 → hold_position
    orc_pair_melee_allied    7   7/7    4 本     L2      警報未のオーク 2・隣接・味方あり → melee_attack
    hurt_drink               6   6/6    4 本     L1      hp<=20・薬あり → drink_potion
    mage_melee_first         6   6/6    5 本     L4+L2   警報未・隣接の魔術師 → melee_attack
    wounded_handover         6   6/6    3 本     L1      hp 21〜30・薬なし・敵なし・味方あり → retreat
    troll_alone_retreat      6   6/6    4 本     L3      警報済みトロル・単独・隣接か遮蔽なし → retreat
    near_hurt_night_retreat  6   5/6    5 本     L1      hp 31〜32・薬なし・敵あり・夜 → retreat(新)
    near_fine_hold           5   5/5    4 本     L7      hp 32・薬なし・敵なし → hold_position
    outnumbered_alarm        5   5/5    4 本     L5      警報未・敵 3・味方 0 → raise_alarm
    troll_shoot_allied       5   5/5    4 本     L2+L3   警報済みトロル・味方あり・離れ・矢あり → shoot
    weak_mage_shoot          5   5/5    4 本     L4      警報未・弱い魔術師・敵 2 以下・矢 4 以上 → shoot
    orc_pair_day_shoot       5   5/5   3〜4 本   L2      警報未のオーク 2・昼・離れ・矢あり・A1 の外 → shoot(改)
    night_alone_cover        4   4/4    4 本     L6      夜・単独・警報済み・離れ・矢 0・遮蔽 → take_cover
    troll_alone_cover        4   4/4    3 本     L3+L6   警報済みトロル・単独・離れ・遮蔽 → take_cover
    mage_shoot               4   4/4    3 本     L2+L4   離れた魔術師(警報済み)・矢あり → shoot
    orc_pair_melee_weak      3   3/3    3 本     L2      警報未のオーク 2・隣接・単独・A1 の外・敵の体力<=45 → melee(新)
    worn_crowd_cover         3   3/3    3 本     gap     昼・矢 0・遮蔽・A2 の外・hp 37〜42・薬なし → take_cover(新)
    mage_no_arrows_hold      3   3/3    3 本     gap     警報済み魔術師・矢 0・distance>=3・遮蔽なし・hp>=45 → hold(新)
    mage_close_melee         3   3/3    3 本     L4      警報済み魔術師・矢 0・distance 2・遮蔽なし → melee_attack
    hurt_retreat             3   3/3    3 本     L1      hp<=20・薬なし・敵あり → retreat
    hurt_troll_alarm         3   3/3    3 本     L5+L3   hp<=32・警報未トロル・distance>=3 → raise_alarm
    mage_no_arrows_cover     3   3/3    3 本     gap     警報済み魔術師・矢 0・distance>=3・遮蔽 → take_cover
    hurt_horde_alarm         3   3/3    3 本     L5+L1   hp<=32・薬なし・警報未の群れ・distance>=3 → raise_alarm
    wounded_mage_alarm       3   3/3    2 本     L5+L1   hp 21〜32・薬なし・警報未の魔術師・distance>=3 → raise_alarm
    troll_melee_allied       2   2/2    2 本     L2+L3   警報済みトロル・味方あり・隣接 → melee_attack
    mage_melee               0                   L2+L4   隣接の魔術師(警報済み) → melee_attack
    (止めた名前: orc_alone_noarrow_alarm。3 件とも orc_serious_alarm へ)
    答える 377 件、一致 363 件(417 件のうち番人に残るのは 40 件)。

棄権の番人(割れている所、証拠が足りない所。輪が審判に訊き直す所)
    no_arrows_cover      17  夜・離れ・矢 0・遮蔽の残り(take_cover 10 / hold 4 / raise 2 / drink 1)
    troll_no_arrows       6  警報済みトロル・味方あり・離れ・矢 0(take_cover 3 / hold 2 / retreat 1)
    hp_ambiguous          5  hp 31〜32・薬なしの残り(retreat 3 / hold 1 / shoot 1)
    wounded_vs_alarm      5  hp 21〜32 で L1 と L5 が競る残り(raise 2 / drink 2 / melee 1)
    weak_mage_unclear     3  警報未・離れた弱い魔術師・矢ありの残り(raise 2 / shoot 1)
    orc_alarm_unclear     1  警報未のオーク 2〜3 体で A1 の外の残り(retreat 1)
    mage_no_arrows        1  警報済み魔術師・矢 0 の残り(drink 1)
    hurt_vs_alarm         1  hp<=20・警報未トロル・distance<=2・薬あり(drink 1、gap)
    weak_troll_alone      1  警報済みトロル・単独・隣接か遮蔽なし・敵の体力 15 以下(hold 1)
    worn_cover_day        0  昼・離れ・矢 0・遮蔽・A2 の外・hp 33〜42 の残り(hp 33〜36 か薬あり)
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
# 追補 A1・A2 の「ひどく傷ついていなければ」(hp がこれを超える)
_SEVERE_MAX = 36

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
# 矢の無い警報済みの魔術師の前で持ち場を守る体力の下限(drink の hp39 と hold の hp51 の間)
_MAGE_HOLD_MIN = 45

# 単独で向き合うトロルを「瀕死」と見る敵の体力の上限(hold の 10 と retreat の 20 の間)
_WEAK_TROLL_MAX = 15

# 警報未のオーク二体の隣で「味方と共に斬る」味方の数(raise の allies=0 と melee の allies>=2 の間)
_ORC_PAIR_ALLIES_MIN = 1
# 隣接・単独のオーク二体を「瀕死」と見る敵の体力の上限(melee の決め手 enemy_hp<=20 と raise の 70 の間)
_WEAK_ORC_MAX = 45

# 昼・矢 0・遮蔽ありで、A2 の外の手負いの上限(take_cover の決め手 hp<=42)
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


def _addendum_a1(s):
    """追補 A1 の条件(依頼書の式そのまま)。→ raise_alarm"""
    return (s['enemy'] == 'orc' and not s['alarm'] and s['hp'] > 36
            and (s['enemy_count'] >= 3
                 or (s['enemy_count'] >= 2 and s['allies'] == 0
                     and (s['time'] == 'night' or s['arrows'] <= 4))))


def _addendum_a2(s):
    """追補 A2 の条件(依頼書の式そのまま)。→ hold_position"""
    return (s['arrows'] == 0 and s['cover'] and s['time'] == 'day'
            and s['enemy'] in ('goblin', 'orc') and s['distance'] >= 2
            and s['enemy_count'] <= 2 and s['hp'] > 36
            and not (s['enemy'] == 'orc' and not s['alarm']
                     and s['enemy_count'] >= 2 and s['allies'] == 0))


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
            if enemy == "none":
                if hp >= _NEAR_FINE_MIN:
                    return ("hold_position", "near_fine_hold")
                return (None, "hp_ambiguous")
            if time == "night":
                return ("retreat", "near_hurt_night_retreat")
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
            # 追補 A1: オークの深刻な脅威
            if _addendum_a1(s):
                return ("raise_alarm", "orc_serious_alarm")
            # A1 の外: hp 33〜36、またはオーク 2 体で(味方あり、または昼・単独・矢 5 以上)
            if dist == 1:
                if count == 2 and allies >= _ORC_PAIR_ALLIES_MIN:
                    return ("melee_attack", "orc_pair_melee_allied")
                if (count == 2 and allies == 0 and hp > _SEVERE_MAX
                        and enemy_hp <= _WEAK_ORC_MAX):
                    return ("melee_attack", "orc_pair_melee_weak")
                return (None, "orc_alarm_unclear")
            # 離れている(distance>=2)
            if time == "night":
                return ("raise_alarm", "orc_night_alarm")
            # 昼
            if count != 2:
                return (None, "orc_alarm_unclear")
            if allies == 0 and hp <= _SEVERE_MAX:
                return (None, "orc_alarm_unclear")
            # 昼・オーク 2 体で A1 に入らない: 深刻な脅威ではない → L2
            if arrows >= 1:
                return ("shoot", "orc_pair_day_shoot")
            # 矢 0(味方あり)は下の L2 の矢なしの枝へ
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
            if dist > _MAGE_CLOSE_MAX and not cover and hp >= _MAGE_HOLD_MIN:
                return ("hold_position", "mage_no_arrows_hold")
            return (None, "mage_no_arrows")
        # ここに来る敵はゴブリンかオーク
        if cover:
            if time == "day":
                # 追補 A2: 昼・遮蔽・離れた小鬼かオーク二体まで → 持ち場で待ち構える
                if _addendum_a2(s):
                    return ("hold_position", "no_arrows_cover_day")
                # A2 の外(敵 3 体以上、または hp 33〜36)
                if hp <= _WORN_MAX:
                    if not potion and hp > _SEVERE_MAX and count >= 3:
                        return ("take_cover", "worn_crowd_cover")
                    return (None, "worn_cover_day")
                return ("hold_position", "no_arrows_cover_day")
            if alarm and allies == 0:
                return ("take_cover", "night_alone_cover")
            return (None, "no_arrows_cover")
        return ("hold_position", "no_arrows_hold")
    if enemy == "mage":
        return ("shoot", "mage_shoot")
    return ("shoot", "shoot_far")
