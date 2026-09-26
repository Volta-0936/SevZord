"""走り r2 の方針、第 0 版(b0)。

この版で変えたこと
    最初の版。審判のラベルはまだ 0 件・会話 0 本なので、枝はすべて
    規律 (a)「指示文をそのまま読んだ規則」だけで立てた。例からの閾値は無い。
    指示文の読みが割れうる所は、名前を付けた番人で棄権にしてある。

根拠(件数 0 件・会話 0 本。審判の決め手はまだ無い。以下は指示文の行)
    hurt_drink       L1  ひどく傷つき(hp<=20)、回復薬あり → drink_potion
    hurt_retreat     L1  ひどく傷つき(hp<=20)、回復薬なし、敵あり → retreat
    troll_alarm      L5+L3  トロル(一人で相手にできない=深刻な脅威)、警報未 → raise_alarm
    melee_adjacent   L2  隣接(distance 1)のゴブリン/オーク → melee_attack
    shoot_far        L2  離れた(distance>=2)ゴブリン/オーク、矢あり → shoot
    mage_melee       L2+L4  隣接の魔術師(警報済み) → melee_attack
    mage_shoot       L2+L4  離れた魔術師(警報済み)、矢あり → shoot
    no_threat_hold   L7  敵なし、傷は浅い(hp>=50) → hold_position

    「ひどく傷ついている」の読み: hp<=20 は明らかにひどい、hp>=50 は明らかに
    ひどくない、とだけ置いた。21〜49 は指示文から読めないので、hp が答えを
    左右する所では棄権する(hp_ambiguous)。

棄権の番人(割れうる所、輪が審判に訊く所)
    hp_ambiguous          21<=hp<=49 で L1 が効くか読めない
    hurt_vs_alarm         ひどい傷とトロル・警報未が重なる(L1 と L5 の順が読めない)
    hurt_no_threat        ひどい傷・薬なし・敵なし(L1 の退くと L7 の持ち場が衝突)
    troll_alarm_raised    警報済みのトロル(退く/遮蔽/射る/味方と戦う が読めない)
    mage_alarm_unclear    警報未の魔術師(L4 の即撃と L5 の警報のどちらか)
    orc_alarm_unclear     警報未のオーク(深刻な脅威か読めない)
    group_alarm_unclear   警報未で敵が複数(深刻な脅威か読めない)
    many_enemies          警報済みでも敵 3 以上(無駄死にしない L0 と L2 の衝突)
    night_cover_far       夜・離れた敵・遮蔽あり(L6 の用心が take_cover を指すか)
    no_arrows_far         離れた敵で矢が 0(L2 が行動を定めない)
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

# 「ひどく傷ついている」の、指示文から明らかに言える側だけ
_HURT_MAX = 20      # これ以下は明らかにひどい
_FINE_MIN = 50      # これ以上は明らかにひどくない


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
    potion = s["potion"]
    arrows = s["arrows"]
    cover = s["cover"]
    alarm = s["alarm"]
    night = s["time"] == "night"

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

    # ここから先は hp>=50(明らかにひどくない)

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
        if enemy == "mage":
            return (None, "mage_alarm_unclear")
        if enemy == "orc":
            return (None, "orc_alarm_unclear")
        if count >= 2:
            return (None, "group_alarm_unclear")
        # 単独のゴブリンは深刻な脅威ではない → L2 へ
    elif count >= 3:
        return (None, "many_enemies")

    # --- L2 (+ L4 魔術師) ---
    if dist == 1:
        if enemy == "mage":
            return ("melee_attack", "mage_melee")
        return ("melee_attack", "melee_adjacent")

    # 離れている(distance>=2)
    if arrows <= 0:
        return (None, "no_arrows_far")
    if night and cover:
        return (None, "night_cover_far")
    if enemy == "mage":
        return ("shoot", "mage_shoot")
    return ("shoot", "shoot_far")
