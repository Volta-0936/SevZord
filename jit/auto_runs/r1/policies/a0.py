"""城の番兵NPC 方針 — 走り r1、第 0 版 (a0)

この版で変えたこと
------------------
- 最初の版。審判のラベルはまだ 0 件(帳簿の件数: 全状況で 0 件)。
- よって帳簿による規則 (b) は一つも無い。答える枝はすべて (a)「指示文をそのまま読んだ規則」だけ。
- 指示文の読みが割れる所、二つの規則がぶつかる所、閾値が書かれていない所は、名前を付けた番人で棄権する。

閾値の根拠(帳簿 0 件なので、指示文の言葉だけから置いた仮の線)
------------------------------------------------------------------
- 「ひどく傷ついている」: hp <= 20 ははっきり該当、hp >= 40 ははっきり非該当とし、
  21〜39 は読みが割れるので棄権 (hp_borderline)。根拠件数 0。
- 「隣接」: distance <= 1。「離れている」: distance >= 2。
- 「深刻な脅威」: トロルははっきり該当(「一人で相手にするには強すぎる」)。
  1 体のゴブリン、2 体までのゴブリン、1 体のオークははっきり非該当と読む。
  魔術師・3 体以上・2 体以上のオーク・夜の敵は、警報を鳴らすか戦うかが割れるので棄権。根拠件数 0。
- 「多勢に無勢」: 見えている敵の数が、番兵と味方の合計より 2 以上多い時は、
  戦うか退くかが割れるので棄権 (outnumbered)。根拠件数 0。

枝の名(答える枝)
------------------
no_threat, badly_hurt_potion, badly_hurt_retreat, alarm_troll,
troll_alone_retreat, adjacent_melee, ranged_shoot
"""

ACTIONS = (
    "melee_attack",
    "shoot",
    "retreat",
    "drink_potion",
    "take_cover",
    "raise_alarm",
    "hold_position",
)

ENEMIES = ("none", "goblin", "orc", "mage", "troll")

# 指示文の言葉から置いた仮の線(帳簿 0 件)
HP_BADLY_HURT_MAX = 20   # これ以下は「ひどく傷ついている」
HP_FINE_MIN = 40         # これ以上は「ひどく傷ついていない」
ADJACENT_MAX = 1         # これ以下は隣接


def _num(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return v
    return None


def decide(s):
    # --- 入力の番人 ---
    if not isinstance(s, dict):
        return None, "bad_input: state is not a dict"

    hp = _num(s.get("hp"))
    enemy = s.get("enemy")
    distance = s.get("distance")
    enemy_count = _num(s.get("enemy_count"))
    allies = _num(s.get("allies"))
    potion = s.get("potion")
    arrows = _num(s.get("arrows"))
    cover = s.get("cover")
    alarm = s.get("alarm")
    time = s.get("time")

    if hp is None:
        return None, "bad_input: hp missing"
    if enemy not in ENEMIES:
        return None, "bad_input: unknown enemy type"
    if time not in ("day", "night"):
        return None, "bad_input: unknown time"
    if enemy_count is None or allies is None or arrows is None:
        return None, "bad_input: count field missing"
    if not isinstance(potion, bool) or not isinstance(alarm, bool) or not isinstance(cover, bool):
        return None, "bad_input: flag field missing"

    badly_hurt = hp <= HP_BADLY_HURT_MAX
    borderline_hp = HP_BADLY_HURT_MAX < hp < HP_FINE_MIN
    night = time == "night"

    # --- 脅威が無い ---
    if enemy == "none":
        if enemy_count and enemy_count > 0:
            return None, "inconsistent_state: enemy none but enemy_count > 0"
        if badly_hurt:
            if potion:
                # 「ひどく傷ついているなら、回復薬があれば飲み」
                return "drink_potion", "badly_hurt_potion"
            # 退くか持ち場を守るかが割れる(脅威が無いのに退くのか)
            return None, "hurt_no_threat_no_potion: retreat vs hold unclear"
        if borderline_hp:
            return None, "hp_borderline: not clearly badly hurt"
        # 「脅威が無ければ持ち場を守る」
        return "hold_position", "no_threat"

    # --- 敵がいる ---
    if enemy_count is not None and enemy_count <= 0:
        return None, "inconsistent_state: enemy present but enemy_count 0"
    d = _num(distance)
    if d is None:
        return None, "inconsistent_state: enemy present but distance missing"
    adjacent = d <= ADJACENT_MAX

    # --- ひどく傷ついている ---
    if badly_hurt:
        if not alarm and (enemy == "troll" or enemy_count >= 3):
            # 回復・退却の規則と警報の規則がぶつかる
            return None, "hurt_vs_alarm: badly hurt while serious threat and alarm silent"
        if potion:
            return "drink_potion", "badly_hurt_potion"
        return "retreat", "badly_hurt_retreat"

    if borderline_hp:
        return None, "hp_borderline: not clearly badly hurt"

    # ここから hp >= HP_FINE_MIN

    # --- 警報がまだ鳴っていない ---
    if not alarm:
        if enemy == "troll":
            if adjacent:
                # 警報か退くかが割れる
                return None, "troll_adjacent_alarm_silent: alarm vs retreat unclear"
            # 「警報がまだ鳴っておらず、深刻な脅威が現れたなら警報を鳴らす」
            return "raise_alarm", "alarm_troll"
        if enemy == "mage":
            # 「早く仕留める」と「警報」のどちらが先か割れる
            return None, "mage_alarm_silent: kill-fast vs alarm unclear"
        # goblin / orc
        if enemy_count >= 3 or (enemy == "orc" and enemy_count >= 2):
            return None, "group_alarm_silent: unclear whether serious threat"
        if night:
            # 「夜は用心深く」で警報に傾くかが割れる
            return None, "night_alarm_silent: night caution may mean alarm"
        # 1 体のオーク/2 体までのゴブリン、昼 → 深刻ではない。戦闘の規則へ

    # --- トロル(警報は鳴っている) ---
    if enemy == "troll" and allies <= 0:
        if adjacent:
            # 「トロルは一人で相手にするには強すぎる」+「無駄死にはしない」
            return "retreat", "troll_alone_retreat"
        # 射るか、隠れるか、退くかが割れる
        return None, "troll_alone_ranged: shoot vs cover vs retreat unclear"

    # --- 多勢に無勢 ---
    if enemy_count - (allies + 1) >= 2:
        return None, "outnumbered: fight vs retreat unclear"

    # --- 通常の戦闘(ゴブリン/オーク/魔術師/味方のいるトロル) ---
    if adjacent:
        # 「隣接していれば近接で戦う」
        return "melee_attack", "adjacent_melee"

    if arrows <= 0:
        # 矢が無く敵が離れている時の行動は書かれていない
        return None, "ranged_no_arrows: no rule for distant enemy without arrows"
    if night and cover:
        # 「夜は用心深く」で遮蔽に隠れるかが割れる
        return None, "night_cover: shoot vs take_cover unclear"
    # 「敵が離れていて矢が残っていれば弓で射る」
    return "shoot", "ranged_shoot"
