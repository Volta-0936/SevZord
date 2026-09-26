"""P3: P2 を第3周の反例(流れの 53 件)で直したもの。
直した点:
- 夜・脅威なし・回復薬なし・hp 31–40:持ち場(例 3 件のうち 2 件)。棄権をやめる。
- 夜・警報まだ・味方なし・オーク:警報(例 2 件とも)。
- 魔術師を早く仕留めるのは 1 体の時。2 体は棄権(射る 1 件、警報 1 件)。
- 深刻な脅威が遠く(5 マス以上)で警報まだなら、傷より警報が先(hp 20 でも警報、例 1 件)。
- 残した食い違い:夜・脅威なし・回復薬あり・hp 33 で持ち場 1 件(同じ帯で飲む 4 件と矛盾。審判の揺れとみなす)。
  2 マス先の弱ったゴブリンに矢なしで斬りかかる 1 件(同じ形で持ち場 2 件)。
"""


def decide(s):
    e, hp, d, n = s["enemy"], s["hp"], s["distance"], s["enemy_count"]
    night = s["time"] == "night"
    serious = e in ("troll", "mage") or n >= 3
    if serious and not s["alarm"] and d is not None and d >= 5 and not (e == "mage" and n == 1 and s["arrows"] > 0):
        return "raise_alarm", "alarm_far_first"
    if s["potion"] and hp <= 35:
        return "drink_potion", "hurt_potion"
    if not s["potion"] and hp <= 30:
        return "retreat", "hurt_no_potion"
    if e == "none":
        if s["potion"] and (hp <= 40 or (night and hp <= 47)):
            return "drink_potion", "hurt_no_threat_potion"
        return "hold_position", "no_threat"
    if serious and not s["alarm"]:
        if e == "mage" and n == 1 and d >= 2 and s["arrows"] > 0:
            return "shoot", "mage_quick_ranged"
        if e == "mage" and n == 2 and d >= 2 and s["arrows"] > 0:
            return None, "mage_pair_ranged"
        if e == "mage" and d == 1 and n == 1 and hp >= 60:
            return "melee_attack", "mage_quick_adjacent"
        return "raise_alarm", "alarm"
    if night and not s["alarm"] and s["allies"] == 0 and e == "orc":
        return "raise_alarm", "night_orc_alone"
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
