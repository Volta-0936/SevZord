"""P2: P1 を第2周の反例(流れの 59 件)で直したもの。
直した点:
- 脅威が無く回復薬がある中くらいの傷:hp≤40 か(夜で hp≤47)なら飲む、それ以外は持ち場。
- 回復薬なしで hp≤30 なら退く(25 から 30 へ)。夜・脅威なし・回復薬なし・hp 31–40 は棄権(例が一つだけ)。
- 魔術師を早く仕留めるのは、魔術師が 2 体以下の時だけ。3 体以上なら警報が先。
- 夜・警報まだ・味方なし・オークは棄権(例が一つだけで、持ち場の常識と食い違う)。
"""


def decide(s):
    e, hp, d, n = s["enemy"], s["hp"], s["distance"], s["enemy_count"]
    night = s["time"] == "night"
    if s["potion"] and hp <= 35:
        return "drink_potion", "hurt_potion"
    if not s["potion"] and hp <= 30:
        return "retreat", "hurt_no_potion"
    if e == "none":
        if s["potion"] and (hp <= 40 or (night and hp <= 47)):
            return "drink_potion", "hurt_no_threat_potion"
        if not s["potion"] and night and hp <= 40:
            return None, "hurt_no_threat_night"
        return "hold_position", "no_threat"
    serious = e in ("troll", "mage") or n >= 3
    if serious and not s["alarm"]:
        if e == "mage" and n <= 2 and d >= 2 and s["arrows"] > 0:
            return "shoot", "mage_quick_ranged"
        if e == "mage" and d == 1 and n == 1 and hp >= 60:
            return "melee_attack", "mage_quick_adjacent"
        return "raise_alarm", "alarm"
    if night and not s["alarm"] and s["allies"] == 0 and e == "orc":
        return None, "night_orc_alone"
    if hp <= 45:
        if s["potion"] and hp <= 37:
            return "drink_potion", "hurt_potion_mid"
        if not s["potion"] and (e == "troll" or n >= 3):
            return "retreat", "hurt_outnumbered"
    if e == "troll" and s["allies"] == 0:
        return "retreat", "troll_alone"
    if d == 1:
        return "melee_attack", "adjacent"
    if s["arrows"] > 0:
        return "shoot", "ranged"
    if s["potion"] and hp <= 47:
        return "drink_potion", "far_no_arrows_hurt"
    if s["cover"] and (night or e == "mage"):
        return "take_cover", "far_no_arrows_cover"
    return "hold_position", "far_no_arrows_hold"
