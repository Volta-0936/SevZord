"""P1: P0 を第1周の反例(流れの 112 件)で直したもの。
直した点:
- 傷の閾値:回復薬があれば hp≤35 で飲む(脅威が無くても)。無ければ hp≤25 で退く(脅威が無くても)。
- 深刻な脅威で警報が未だなら警報、が最優先。ただし魔術師は「早く仕留める」が勝つ:離れていて矢があれば射る、
  隣に一体だけで体力が十分なら斬る。hp≤30 なら棄権。
- 中くらいの傷(hp≤45):回復薬なし+(トロル か 敵3体以上)なら退く。
- 矢が無く敵が離れている:回復薬があり hp≤47 なら飲む。遮蔽があり(夜 か 魔術師)なら隠れる。それ以外は持ち場。
"""


def decide(s):
    e, hp, d, n = s["enemy"], s["hp"], s["distance"], s["enemy_count"]
    night = s["time"] == "night"
    if s["potion"] and hp <= 35:
        return "drink_potion", "hurt_potion"
    if not s["potion"] and hp <= 25:
        return "retreat", "hurt_no_potion"
    if e == "none":
        if s["potion"] and hp <= 47:
            return None, "hurt_no_threat"
        return "hold_position", "no_threat"
    serious = e in ("troll", "mage") or n >= 3
    if serious and not s["alarm"]:
        if e == "mage" and d >= 2 and s["arrows"] > 0:
            return "shoot", "mage_quick_ranged"
        if e == "mage" and d == 1 and n == 1 and hp >= 60:
            return "melee_attack", "mage_quick_adjacent"
        if hp <= 30:
            return None, "hurt_serious_no_alarm"
        return "raise_alarm", "alarm"
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
