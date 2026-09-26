"""走り r3 の方針、第 4 版(c4)。前の版は c3。

帳簿: 審判のラベル 374 件、会話 10 本(round1_s1/s2/s3、round2_s1/s2/s3、round3_s1/s2、
round4_s1/s2。以下 r1s1 … r4s2)。範囲の番人は c3 のまま。

c3 の答える枝は、374 件で数え直しても門に落ちるものがない。一致が最も低いのは
no_arrows_cover_day(28 件で 24/28、86%、別の答えを多数にした会話は 1 本)で、ほかの外れの
ある枝は shoot_far 34/36、mage_alarm 14/15、wounded_retreat 9/10、orc_night_alarm 9/10、
wounded_alone_hold 7/8。どれも別の答えを多数にした会話は 1 本以下。
この版で変えたのは、no_arrows_cover_day の外れの一群(訊き直して 3 本とも同じ答え)を
切り出したことと、c3 が棄権していた所のうち会話が揃った所。

この版で変えたこと
 1. wounded_cover_day(新しい枝、no_arrows_cover_day から切り出す):
    昼・離れたゴブリン/オーク・矢 0・遮蔽あり・33<=hp<=42・薬なし → take_cover。
    3 件・会話 3 本(r1s2、r4s1、r4s2)・一致 3/3。根拠 L0(gap)。
    3 件は訊き直した同じ状態(hp42、ゴブリン 3 体、distance 4、味方 3、警報済み、門、昼)で、
    3 本とも take_cover。決め手 arrows=0 3、hp<=42 2、cover=true 2、potion=false 1、
    distance>=4 1(「矢も薬も無く体力半分以下、遮蔽で門に踏み止まる」「矢が無く傷も浅くないので
    遮蔽で接近を待つ」「矢が無く敵は遠い、傷もあるので遮蔽で待つ」)。
    hp の線は決め手 hp<=42 のまま(_WOUNDED_COVER_MAX)。下は _FINE_MIN の 33。
    薬ありは入れない(決め手に potion=false があり、薬ありの手負いには飲む例がある:
        夜の hp33 drink(r3s2)、警報済み魔術師の hp39 drink(r4s1))。
    夜は入れない(夜の hp<=42・矢 0・遮蔽は raise 1(r3s2 hp39)/ take_cover 1(r4s2 hp42)で割れる)。
    警報は条件にしない(決め手に挙がっていない)。
    no_arrows_cover_day の hold の決め手に hp は挙がっていない(arrows=0 28、distance>=2 7、
        distance>=8 6、allies>=3 5)。残る外れは r4s2 の take_cover 1(hp82、ゴブリン 5 体、
        決め手 enemy_count>=5、gap、1 件で規律に届かない)で、枝は 24/25 になる。

 2. calm_day_hold(新しい枝、番人 hp_ambiguous から切り出す):
    hp 32・薬なし・敵なし・昼 → hold_position。
    5 件・会話 4 本(r2s1、r2s2、r4s1 2、r4s2)・一致 5/5。根拠 L7(+L1)(一部 gap)。
    決め手 enemy=none 5、hp>=32 3、time=day 1(「脅威が無く深手でもないので持ち場を守る」
    「深手だが敵は見えず、持ち場を守る」「昼で脅威も無く、まだ持ち場を守れる体力」)。
    hp の線は決め手 hp>=32 のまま(_CALM_HOLD_MIN)。敵なしの外れは r2s3 の retreat 1
    (hp31・夜・味方 3、決め手 hp<=33, potion=false, allies>=1)で、hp31 と夜は枝の外に置く。
    味方は条件にしない(hold の 5 件は味方 1〜2、決め手に挙がっていない)。
    敵ありの hp 31〜32 は変えない(夜は retreat 4 / shoot 1 でちょうど 80%、訊き直した
    hp31・ゴブリン 3 体・夜も retreat 2 / shoot 1。昼は retreat 1(r4s1)/ shoot 1(r2s2))。

 3. orc_pair_adjacent_melee(新しい枝、番人 orc_alarm_unclear から):
    警報未・隣接のオーク 2 体・味方 2 以上 → melee_attack。
    7 件・会話 4 本(r1s3、r3s2、r4s1 3、r4s2 2)・一致 7/7。昼 2・夜 5。根拠 L2(一部 gap)。
    決め手 distance<=1 / =1 7、allies>=2 3、allies>=3 1、hp>=91 2(「隣接したオークに味方と共に
    近接で当たる」「隣接、夜でも味方が多く近接で戦う」)。L2 をそのまま読んだ答えでもある。
    味方の線は決め手 allies>=2 のまま(_ORC_MELEE_ALLIES_MIN)。味方 1 は例がない。
    味方 0 は番人に残す: 夜は訊き直した状態(hp82、門、単独)で raise 2(r1s2、r2s1、
    「斬り合う前に警報」)/ melee 1(r2s3)と会話どうしで割れる。昼は melee 1(r3s1、敵の体力 20)。
    オーク 3 体の隣接も番人(raise 1、r3s2「隣の敵は味方に任す」)。

 4. orc_alone_no_arrows_alarm(新しい枝、番人 orc_alarm_unclear から):
    警報未・昼・離れたオーク 2 体・味方 0・矢 0 → raise_alarm。
    3 件・会話 3 本(r2s1、r4s1、r4s2)・一致 3/3。根拠 L5(gap)。3 件は訊き直した同じ状態
    (hp83、distance 7、壁、昼、薬あり、遮蔽あり)。決め手 allies=0 3、enemy_count>=2 3、
    alarm=false 3(「味方も矢も無くオーク二体、警報で助けを呼ぶ」「味方なしで敵二体、矢も無いので
    警報で援軍を呼ぶ」「単独でオーク二体が迫る、遠いうちに警報を鳴らす」)。
    矢ありの単独は番人に残す(raise 1(r3s1 矢 4)/ shoot 1(r2s3 矢 8、決め手 distance>=2,
        arrows>=1)で会話どうしに割れる。矢で分けずにまとめると 4/5 でちょうど 80% なので、
        hp_ambiguous と同じく線の上に出るまで待つ)。
    矢 0・味方ありも番人(hold 2、r3s1 d9 味方 1・r4s2 d2 味方 3、どちらも gap で規律に届かない)。

変えなかった番人
    no_arrows_cover 15: 夜・離れ・矢 0・遮蔽ありの残り。警報済み・味方ありは hold 3(r2s1 2、
        r3s1)/ take_cover 4(r2s2 2、r3s2、r4s1)で会話どうしに割れる。警報未は take_cover 4 /
        raise 2 / hold 1 / drink 1(薬ありの hp33)で割れる。
    hp_ambiguous 8: 上の 2. の残り(retreat 6 / shoot 2)。
    wounded_vs_alarm 5: 訊き直した hp28・遠い魔術師・薬ありは raise 2(r1s1、r3s2)/ drink 1(r3s1)。
    mage_no_arrows 3: hold 2(gap)/ drink 1(r4s1 hp39 薬あり)。例が少なく根拠 gap。
    troll_no_arrows 2、weak_troll_alone 1、weak_mage_unclear 1、hurt_vs_alarm 1: 例が少なく根拠 gap。

c4 で数え直した帳簿(答える枝、件数・一致・会話)
    no_threat_hold             60  60/60  10 本   L7      敵なし・hp>=33 → hold_position
    shoot_far                  36  34/36   8 本   L2      離れたゴブリン/オーク・矢あり → shoot
    no_arrows_cover_day        25  24/25           gap     離れ・矢 0・遮蔽あり・昼(1. の外)→ hold_position
    horde_alarm                17  17/17   7 本   L5      警報未・敵 4 以上 → raise_alarm
    melee_adjacent             15  15/15   6 本   L2      隣接のゴブリン/オーク → melee_attack
    mage_alarm                 15  14/15   7 本   L5+L4   警報未・離れた魔術師 → raise_alarm
    hurt_no_threat_retreat     13  13/13   5 本   L1      hp<=20・薬なし・敵なし → retreat
    wounded_drink              11  11/11   7 本   L1      hp 21〜32・薬あり → drink_potion
    wounded_retreat            10   9/10   8 本   L1      hp 21〜30・薬なし・敵あり → retreat
    orc_night_alarm            10   9/10   7 本   L5+L6   警報未のオーク 2〜3・夜・離れ → raise_alarm
    troll_alarm                 8   8/8    5 本   L5+L3   トロル・警報未 → raise_alarm
    wounded_alone_hold          8   7/8    6 本   L7      hp 21〜30・薬なし・敵なし・味方 0 → hold_position
    no_arrows_hold              8   8/8    5 本   gap     離れ・矢 0・遮蔽なし → hold_position
    orc_pair_adjacent_melee     7   7/7    4 本   L2      警報未・隣接のオーク 2・味方 2 以上 → melee_attack(新)
    hurt_drink                  6   6/6    4 本   L1      hp<=20・薬あり → drink_potion
    mage_melee_first            6   6/6    5 本   L4+L2   警報未・隣接の魔術師 → melee_attack
    wounded_handover            6   6/6    3 本   L1      hp 21〜30・薬なし・敵なし・味方あり → retreat
    troll_alone_retreat         6   6/6    4 本   L3      警報済みトロル・単独・隣接か遮蔽なし → retreat
    calm_day_hold               5   5/5    4 本   L7      hp 32・薬なし・敵なし・昼 → hold_position(新)
    troll_shoot_allied          5   5/5    4 本   L2+L3   警報済みトロル・味方あり・離れ・矢あり → shoot
    weak_mage_shoot             5   5/5    4 本   L4      警報未・弱い魔術師・敵 2 以下・矢 4 以上 → shoot
    outnumbered_alarm           4   4/4    3 本   L5      警報未・敵 3・味方 0 → raise_alarm
    night_alone_cover           4   4/4    4 本   L6      夜・単独・警報済み・離れ・矢 0・遮蔽 → take_cover
    troll_alone_cover           4   4/4    3 本   L3+L6   警報済みトロル・単独・離れ・遮蔽 → take_cover
    mage_shoot                  4   4/4    3 本   L2+L4   離れた魔術師(警報済み)・矢あり → shoot
    orc_pair_day_shoot          4   4/4    3 本   L2      警報未のオーク 2・昼・味方あり・離れ・矢あり → shoot
    wounded_cover_day           3   3/3    3 本   gap     昼・離れ・矢 0・遮蔽・hp 33〜42・薬なし → take_cover(新)
    orc_alone_no_arrows_alarm   3   3/3    3 本   L5      警報未のオーク 2・昼・離れ・味方 0・矢 0 → raise_alarm(新)
    mage_close_melee            3   3/3    3 本   L4      警報済み魔術師・矢 0・distance 2・遮蔽なし → melee_attack
    hurt_retreat                3   3/3    3 本   L1      hp<=20・薬なし・敵あり → retreat
    hurt_troll_alarm            3   3/3    3 本   L5+L3   hp<=32・警報未トロル・distance>=3 → raise_alarm
    mage_no_arrows_cover        3   3/3    3 本   gap     警報済み魔術師・矢 0・distance>=3・遮蔽 → take_cover
    hurt_horde_alarm            3   3/3    3 本   L5+L1   hp<=32・薬なし・警報未の群れ・distance>=3 → raise_alarm
    wounded_mage_alarm          3   3/3    2 本   L5+L1   hp 21〜32・薬なし・警報未の魔術師・distance>=3 → raise_alarm
    troll_melee_allied          2   2/2    2 本   L2+L3   警報済みトロル・味方あり・隣接 → melee_attack
    mage_melee                  0                 L2+L4   隣接の魔術師(警報済み) → melee_attack
    答える 328 件、一致 321(c3 は 313 件、一致 303)。
    no_arrows_cover_day と wounded_cover_day の数は、表に出た外れと決め手からの数え直し
    (no_arrows_cover_day の hold の各例の hp は表に出ていない)。

棄権の番人(割れている所、証拠が足りない所。輪が審判に訊き直す所)
    no_arrows_cover      15  離れ・矢 0・遮蔽あり・夜の残り(take_cover 8 / hold 4 / raise 2 / drink 1)
    orc_alarm_unclear    10  警報未のオーク 2〜3 体の残り(raise 5 / melee 2 / hold 2 / shoot 1)
    hp_ambiguous          8  hp 31〜32・薬なしの残り(retreat 6 / shoot 2)
    wounded_vs_alarm      5  hp 21〜32 で L1 と L5 が競る残り(raise 2 / drink 2 / melee 1)
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

# hp 31〜32・敵なし・昼で持ち場に留まる下限(決め手 hp>=32)
_CALM_HOLD_MIN = 32

# 昼・矢 0・遮蔽ありで、傷を理由に遮蔽へ入る hp の上限(決め手 hp<=42)
_WOUNDED_COVER_MAX = 42

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

# 警報未・隣接のオーク 2 体に、警報より先に斬りかかる味方の数(決め手 allies>=2)
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
            # 31<=hp<=32、薬なし
            if enemy == "none" and hp >= _CALM_HOLD_MIN and time == "day":
                return ("hold_position", "calm_day_hold")
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
            if dist >= 2:
                if time == "night":
                    return ("raise_alarm", "orc_night_alarm")
                if count == 2 and allies >= 1 and arrows >= 1:
                    return ("shoot", "orc_pair_day_shoot")
                if count == 2 and allies == 0 and arrows <= 0:
                    return ("raise_alarm", "orc_alone_no_arrows_alarm")
            elif count == 2 and allies >= _ORC_MELEE_ALLIES_MIN:
                # 隣接(distance 1)。味方と共に斬る
                return ("melee_attack", "orc_pair_adjacent_melee")
            return (None, "orc_alarm_unclear")
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
                if hp <= _WOUNDED_COVER_MAX and not potion:
                    return ("take_cover", "wounded_cover_day")
                return ("hold_position", "no_arrows_cover_day")
            if alarm and allies == 0:
                return ("take_cover", "night_alone_cover")
            return (None, "no_arrows_cover")
        return ("hold_position", "no_arrows_hold")
    if enemy == "mage":
        return ("shoot", "mage_shoot")
    return ("shoot", "shoot_far")
