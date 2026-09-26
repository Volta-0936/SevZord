"""走り r2 の方針、第 1 版(b1)。

帳簿: 審判のラベル 120 件、会話 3 本(round1_s1 / s2 / s3、以下 s1 s2 s3)。
b0 の答えた枝(no_threat_hold 13、shoot_far 6、melee_adjacent 4、troll_alarm 3、
mage_shoot 2、hurt_drink 1、hurt_retreat 1)は全件一致だったので、そのまま残す。
b0 が答えた状態の行き先は、この版でも変わらない。

この版で変えたこと
 1. 「ひどく傷ついていない」の下限を hp>=50 から hp>=33 に下げた(_FINE_MIN)。
    hp_ambiguous の 36 件のうち hp>=35 の 26 件では、どの会話も L1(飲む・退く)を
    使っていない。飲む・退くの最も高い例は hp=31(s2 が飲む)。敵がいない hp 35〜49 の
    14 件(会話 3 本)はすべて hold_position。
    審判の決め手は、傷の側が hp<=30 / hp<=31、平気の側が hp>=30 / hp>=31 / hp>=39 /
    hp>=40 …。30〜31 は会話で割れる(s2 は 31 で飲む、s1 は 31 を「手負い」と言いつつ射る、
    s3 は 30 で持ち場に残る)。線は割れている例 31 と、その上の次の例 35 の間の 33 に置いた。
    hp 21〜32 は hp_ambiguous のまま棄権(10 件: 飲む 3・退く 3・持ち場 2・警報 1・射る 1)。
    傷の側の上限 hp<=20 は据え置いた。hp 21〜23 の L1 の例は、枝ごとに見ると
    hurt_drink 1 件(gap)・hurt_retreat 2 件(うち 1 件 gap)で、規律 (b)(c) に届かない。
 2. 番人 many_enemies を外した。警報済み・敵 3 以上の 8 件・会話 3 本がすべて L2 どおり
    (隣接 2 件は melee_attack、離れて矢あり 6 件は shoot)。根拠は 8 件とも L2 で gap なし。
    決め手は distance と arrows だけで、enemy_count は一度も挙がっていない。
 3. 番人 night_cover_far を外した。夜・遮蔽あり・離れた敵・矢ありの 5 件・会話 3 本が
    すべて shoot(根拠 L2、gap なし。決め手 distance>=2, arrows>=1)。L6 は遮蔽を指していない。
 4. 新しい枝 horde_alarm: 警報未・敵 4 以上(トロル以外)→ raise_alarm。
    10 件・会話 3 本・一致 10/10(オーク 5、ゴブリン 3、魔術師 2。s1 2 件、s2 5 件、s3 3 件)。
    決め手は alarm=false と enemy_count>=4 / enemy_count>=5。敵 3 は割れる
    (raise 3・melee 1・shoot 1)ので、線は 3 と 4 の間に置いた。
 5. 新しい枝 outnumbered_alarm: 警報未・敵 3・近くの味方 0 → raise_alarm。
    3 件・会話 2 本(s1 ゴブリン 1、s3 オーク 2)・一致 3/3。決め手は 3 件とも
    enemy_count>=3, allies=0, alarm=false。
 6. 警報未の単独のオークを、深刻な脅威でないとして L2 へ通した(orc_alarm_unclear から外した)。
    2 件(s3 隣接 melee_attack、s1 離れて shoot)、どちらも根拠 L2 だけ・gap なしで L2 と一致
    → 規律 (c)。決め手は distance=1 / distance>=2, arrows>=1 だけ。
    警報未のゴブリン 2 体も L2 へ通した(group_alarm_unclear から外した)。
    4 件・会話 3 本・一致 4/4(隣接 melee_attack 1、離れて shoot 3)。決め手は distance / arrows。
 7. 離れた敵・矢 0(no_arrows_far)を三つに分けた。
    no_arrows_hold(新しい枝、遮蔽なし・魔術師以外 → hold_position):
        5 件・会話 3 本・一致 5/5。決め手 arrows=0, distance>=2(s3 は cover=false も挙げる)。
    no_arrows_cover(番人、遮蔽あり): hold 4・take_cover 2 で割れる。take_cover は s1 と s2 に
        一つずつあり、決め手は cover=true, time=night / hp<=42, potion=false。
    mage_no_arrows(番人、魔術師): 1 件(melee_attack、根拠 L4+gap)で足りない。

b1 で数え直した帳簿(答える枝、件数・一致・会話)
    no_threat_hold      27  27/27  s1 s2 s3   L7  敵なし・hp>=33 → hold_position
    shoot_far           22  22/22  s1 s2 s3   L2  離れたゴブリン/オーク・矢あり → shoot
    horde_alarm         10  10/10  s1 s2 s3   L5  警報未・敵 4 以上 → raise_alarm
    melee_adjacent       9   9/9   s1 s2 s3   L2  隣接のゴブリン/オーク → melee_attack
    no_arrows_hold       5   5/5   s1 s2 s3   gap 離れた敵・矢 0・遮蔽なし → hold_position
    outnumbered_alarm    3   3/3   s1 s3      L5  警報未・敵 3・味方 0 → raise_alarm
    troll_alarm          3   3/3   2 本       L5+L3  トロル・警報未 → raise_alarm
    mage_shoot           3   3/3   3 本       L2+L4  離れた魔術師(警報済み)・矢あり → shoot
    hurt_drink           1   1/1              L1  hp<=20・回復薬あり → drink_potion
    hurt_retreat         1   1/1              L1  hp<=20・回復薬なし・敵あり → retreat
    mage_melee           0                    L2+L4  隣接の魔術師(警報済み) → melee_attack

棄権の番人(割れている所、証拠が足りない所。輪が審判に訊き直す所)
    hp_ambiguous         10  21<=hp<=32。30〜31 で会話が割れ、21〜32 の答えは 5 種に散る
    no_arrows_cover       6  離れた敵・矢 0・遮蔽あり(hold 4 / take_cover 2)
    mage_alarm_unclear    5  警報未の魔術師(敵 3 以下、敵 3 なら味方あり)。
                             melee 1 / raise 2 / shoot 2、根拠はほぼ gap
    troll_alarm_raised    5  警報済みのトロル(hold 1 / shoot 2 / take_cover 2、全件 gap)
    orc_alarm_unclear     3  警報未のオーク 2〜3 体(敵 3 なら味方あり)。
                             オーク 2 体は raise 2(s2, s3)/ melee 1(s3)
    hurt_no_threat        3  hp<=20・薬なし・敵なし。retreat 3 だが会話 1 本(s3)・gap
    group_alarm_unclear   2  警報未のゴブリン 3 体・味方あり。L2 どおり 2 件だが会話 1 本(s3)、
                             味方 0 では警報(outnumbered_alarm)なので味方の数が効く
    mage_no_arrows        1  離れた魔術師・矢 0(melee 1 件、gap)
    hurt_vs_alarm         1  hp<=20 とトロル・警報未が重なる(raise 1 件、gap)
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
_HURT_MAX = 20      # これ以下は明らかにひどい(b0 のまま)
_FINE_MIN = 33      # これ以上はひどくない(割れている 31 と次の例 35 の間)

# 警報未の群れ
_HORDE_MIN = 4          # 敵がこれ以上なら警報(敵 3 は割れる、4・5 は 10/10)
_OUTNUMBERED_MIN = 3    # 味方 0 で敵がこれ以上なら警報(3/3)


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
    allies = s["allies"]
    potion = s["potion"]
    arrows = s["arrows"]
    cover = s["cover"]
    alarm = s["alarm"]

    hurt = hp <= _HURT_MAX
    fine = hp >= _FINE_MIN

    # --- L1: ひどく傷ついている ---
    if hurt:
        if enemy == "troll" and not alarm:
            return (None, "hurt_vs_alarm")
        if potion:
            return ("drink_potion", "hurt_drink")
        if enemy == "none":
            return (None, "hurt_no_threat")
        return ("retreat", "hurt_retreat")

    if not fine:
        return (None, "hp_ambiguous")

    # ここから先は hp>=33(ひどくない)

    # --- L7: 脅威が無い ---
    if enemy == "none":
        return ("hold_position", "no_threat_hold")

    # --- L3 + L5: トロル ---
    if enemy == "troll":
        if not alarm:
            return ("raise_alarm", "troll_alarm")
        return (None, "troll_alarm_raised")

    # --- L5: 警報未のとき、深刻な脅威かどうか ---
    if not alarm:
        if count >= _HORDE_MIN:
            return ("raise_alarm", "horde_alarm")
        if count >= _OUTNUMBERED_MIN and allies == 0:
            return ("raise_alarm", "outnumbered_alarm")
        if enemy == "mage":
            return (None, "mage_alarm_unclear")
        if enemy == "orc" and count >= 2:
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
        if cover:
            return (None, "no_arrows_cover")
        return ("hold_position", "no_arrows_hold")
    if enemy == "mage":
        return ("shoot", "mage_shoot")
    return ("shoot", "shoot_far")
