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
