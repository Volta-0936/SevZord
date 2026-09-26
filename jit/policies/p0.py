"""P0: 指示文だけから書いた番兵の方針(審判のラベルを一件も見ていない)。
返り値: (行動, 番人の名) か (None, 棄権の理由)。番人の名は、どの枝が答えたか(較正と監査の単位)。"""


def decide(s):
    e, hp, d = s["enemy"], s["hp"], s["distance"]
    night = s["time"] == "night"
    if e == "none":
        return "hold_position", "no_threat"
    if hp <= 25:
        return ("drink_potion", "hurt_potion") if s["potion"] else ("retreat", "hurt_no_potion")
    if hp <= 45 and (night or e == "troll" or s["enemy_count"] >= 3):
        return None, "gray_hurt"
    serious = e in ("troll", "mage") or s["enemy_count"] >= 3
    if serious and not s["alarm"]:
        if d == 1:
            return None, "alarm_vs_adjacent"
        return "raise_alarm", "alarm"
    if e == "troll":
        if s["allies"] == 0:
            return "retreat", "troll_alone"
        if s["allies"] == 1:
            return None, "troll_one_ally"
    if d == 1:
        return "melee_attack", "adjacent"
    if s["arrows"] > 0:
        return "shoot", "ranged"
    return None, "no_arrows_far"
