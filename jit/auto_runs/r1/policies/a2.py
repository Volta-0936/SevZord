"""城の番兵NPC 方針 — 走り r1、第 2 版 (a2)

この版で変えたこと(根拠は熱さの帳簿 214 件と、その食い違い・棄権の例の一覧)
------------------------------------------------------------------------------
1. hp 33〜39 で回復薬あり → 回復薬を飲む (mid_hurt_potion)。番人 hp_mid_potion を外した。
   - hp_mid_potion の 11 件で drink_potion 10 / hold_position 1(91%)。
   - 敵あり 5/5 が drink(ゴブリン・オーク・魔術師、隣接も含む、警報の有無を問わず)。
     警報・魔術師・群れの規則より先に当てる(hp37 オーク4体隣接、hp37 魔術師隣接、
     hp37 オーク3体 が、どれも drink)。
   - 敵なし 6 件で drink 5 / hold 1(83%)。
   - 線は 40 のまま。drink の最も高い例 hp38 と、回復薬ありで飲まなかった hp42
     (ゴブリン4体隣接 → raise_alarm)の間。
2. hp 33〜39 で回復薬なし、敵がいて答えが戦い・持ち場になる時 → 棄権 (hp_mid_no_potion_fight)。
   - a1 の根拠(shoot 1 / melee 1)に対し、新しく retreat 2 件
     (hp34 ゴブリン2体・離れて → ranged_shoot の食い違い、hp37 オーク2体・離れて)。割れている。
   - 警報の答え(群れ・トロル・魔術師)は番人より先に当てる。この帯の警報の例
     (hp34 オーク3体隣接、hp37 群れ)はどれも raise_alarm で、退く答えは無い。
   - 敵なしは a1 どおり hold(hold 6/6、no_threat に食い違い 0)。
   - 味方のいないトロル相手は、どちらに読んでも退くので troll_alone_retreat を先に当てる。
3. 警報未鳴動のゴブリン/オーク 3 体以上は、隣接していても警報 (alarm_group に統合)。
   番人 group_adjacent_alarm_silent を外した。
   - 隣接 6/6 が raise_alarm(多勢に無勢の隣接 3 件、hp34 回復薬なし 1 件を含む)。
   - alarm_group 10/10 と合わせて 16/16。
4. 警報未鳴動のトロルは、隣接していても警報 (alarm_troll に統合)。
   番人 troll_adjacent_alarm_silent を外した。
   - 隣接 5/5 が raise_alarm(味方 0 の 1 件を含む)。alarm_troll 2/2 と合わせて 7/7。
5. 警報が鳴っていて味方のいないトロルは、離れていても退く (troll_alone_retreat に統合)。
   番人 troll_alone_ranged を外した。
   - 離れて 6/6 が retreat(矢なし 1 件、夜 5 / 昼 1、遮蔽の有無を問わず)。
     隣接 1/1 と合わせて 7/7。
6. 警報未鳴動・離れた魔術師(矢あり)の番人 mage_ranged_alarm_silent を、敵の数で分けた。
   - 21 件で shoot 15 / raise_alarm 6。raise_alarm 6 件はすべて敵 3 体以上だった。
   - 敵 2 体まで → 射る (mage_ranged_shoot)。13/13 が shoot(昼 9 / 夜 4)。
   - 敵 3 体以上・夜 → 警報 (mage_group_night_alarm)。4/4 が raise_alarm
     (「夜は用心深く」とも合う)。
   - 敵 3 体以上・昼 → 棄権 (mage_group_day_alarm_silent)。4 件で shoot 2 / raise_alarm 2。
     (3 体以上をまとめると 6/8 = 75% で 80% に届かない。)
7. 警報未鳴動のオーク 2 体の番人 orc_pair_alarm_silent を分けた。
   - 12 件で raise_alarm 2 / shoot 5 / melee 1 / retreat 1 / hold 3。
   - 昼・離れて・矢あり → 射る (orc_pair_day_shoot)。4/4 が shoot。
   - 夜・離れて・矢あり → 棄権 (orc_pair_night)。2 件で shoot 1 / raise_alarm 1。
   - 離れて・矢なし → 棄権 (orc_pair_no_arrows)。4 件で hold 3 / raise_alarm 1(75%)。
   - 隣接 → 棄権 (orc_pair_adjacent)。1 件(melee)。
   - hp37 回復薬なしの retreat 1 件は上の 2. の番人に入る。
8. 多勢に無勢・夜・遮蔽あり・離れて矢あり → 棄権 (outnumbered_night_cover)。
   - a1 の根拠 2 件(shoot)に対し、新しく take_cover 1 件
     (hp99 ゴブリン5体・味方0・夜・遮蔽)。3 件で shoot 2 / take_cover 1(67%)。
   - 夜・遮蔽でも多勢でなければ a1 どおり射る(night_cover 6/6)。
9. ranged_shoot の食い違い 2 件は、上の 2. と 8. の番人に移った。

変えなかった所
--------------
- 「ひどく傷ついている」の線 hp <= 32、重傷は警報より先(badly_hurt_potion 15/15、
  badly_hurt_retreat 16/16)。
- no_threat 42/42、no_arrows_hold 19/19、adjacent_melee 8/8、mage_adjacent_melee 5/5、
  mage_no_arrows_alarm 4/4。

棄権のまま残した所
------------------
- troll_no_arrows: 1 件(味方ありのトロル・離れて矢なし → take_cover 1)。
- outnumbered_adjacent: 1 件(魔術師4体隣接・味方0 → melee 1)。
- mage_group_day_alarm_silent, orc_pair_night, orc_pair_no_arrows, orc_pair_adjacent,
  hp_mid_no_potion_fight, outnumbered_night_cover: 上のとおり。

枝の名(答える枝)
------------------
no_threat, badly_hurt_potion, badly_hurt_retreat, mid_hurt_potion, alarm_troll,
alarm_group, mage_adjacent_melee, mage_no_arrows_alarm, mage_group_night_alarm,
mage_ranged_shoot, orc_pair_day_shoot, troll_alone_retreat, adjacent_melee,
no_arrows_hold, ranged_shoot
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

# 帳簿から置いた線
HP_BADLY_HURT_MAX = 32   # これ以下は「ひどく傷ついている」(hp21〜30 の 19 件すべて重傷扱い、hp34 は非該当)
HP_FINE_MIN = 40         # 33〜39 は中間帯。回復薬ありなら飲む(10/11、最高 hp38)、hp42 は飲まない
ADJACENT_MAX = 1         # これ以下は隣接
GROUP_MIN = 3            # この数以上なら群れ(ゴブリン/オーク 16/16 が raise_alarm、魔術師の警報 6 件もすべて 3 体以上)
OUTNUMBERED_MARGIN = 2   # 敵の数が番兵+味方より、これ以上多ければ多勢に無勢


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
    mid_hp = HP_BADLY_HURT_MAX < hp < HP_FINE_MIN
    mid_hp_potion = mid_hp and potion
    mid_hp_no_potion = mid_hp and not potion

    mid_fight_reason = (
        "hp_mid_no_potion_fight: fight vs retreat split at hp 33-39 without potion "
        "(shoot 1 / melee 1 / retreat 2)"
    )

    # --- 脅威が無い ---
    if enemy == "none":
        if enemy_count and enemy_count > 0:
            return None, "inconsistent_state: enemy none but enemy_count > 0"
        if badly_hurt:
            if potion:
                # 「ひどく傷ついているなら、回復薬があれば飲み」
                return "drink_potion", "badly_hurt_potion"
            # 「なければ退く」— 脅威が無くても退く(7/7)
            return "retreat", "badly_hurt_retreat"
        if mid_hp_potion:
            # 敵なし・hp33〜39・回復薬あり: drink 5 / hold 1
            return "drink_potion", "mid_hurt_potion"
        # 「脅威が無ければ持ち場を守る」(hp33〜39・回復薬なしも hold 6/6)
        return "hold_position", "no_threat"

    # --- 敵がいる ---
    if enemy_count <= 0:
        return None, "inconsistent_state: enemy present but enemy_count 0"
    d = _num(distance)
    if d is None:
        return None, "inconsistent_state: enemy present but distance missing"
    adjacent = d <= ADJACENT_MAX
    outnumbered = enemy_count - (allies + 1) >= OUTNUMBERED_MARGIN

    # --- ひどく傷ついている(警報の規則より先) ---
    if badly_hurt:
        if potion:
            return "drink_potion", "badly_hurt_potion"
        return "retreat", "badly_hurt_retreat"

    # --- 中間帯で回復薬あり(警報・魔術師・群れの規則より先。敵あり 5/5) ---
    if mid_hp_potion:
        return "drink_potion", "mid_hurt_potion"

    # ここから「ひどく傷ついていない」、または hp33〜39 で回復薬なし

    # --- 警報がまだ鳴っていない ---
    if not alarm:
        if enemy == "troll":
            # 「警報がまだ鳴っておらず、深刻な脅威が現れたなら警報を鳴らす」(隣接 5 + 離れて 2、7/7)
            return "raise_alarm", "alarm_troll"
        if enemy == "mage":
            if adjacent:
                if outnumbered:
                    return None, "outnumbered_adjacent: fight vs retreat unclear (1 case, melee)"
                if mid_hp_no_potion:
                    return None, mid_fight_reason
                # 「隣接していれば近接で戦う」+「魔術師は早く仕留める」(5/5)
                return "melee_attack", "mage_adjacent_melee"
            if arrows <= 0:
                # 射てない魔術師には警報(4/4)
                return "raise_alarm", "mage_no_arrows_alarm"
            if enemy_count >= GROUP_MIN:
                if time == "night":
                    # 魔術師+群れ、夜 → 警報(4/4)
                    return "raise_alarm", "mage_group_night_alarm"
                # 昼: shoot 2 / raise_alarm 2
                return None, "mage_group_day_alarm_silent: shoot vs alarm split (4 cases, 2/2)"
            if mid_hp_no_potion:
                return None, mid_fight_reason
            # 魔術師 2 体まで・離れて・矢あり → 射る(13/13)
            return "shoot", "mage_ranged_shoot"
        # goblin / orc
        if enemy_count >= GROUP_MIN:
            # 3 体以上は深刻な脅威 → 警報(隣接していても。16/16)
            return "raise_alarm", "alarm_group"
        if enemy == "orc" and enemy_count >= 2:
            if mid_hp_no_potion:
                return None, mid_fight_reason
            if adjacent:
                return None, "orc_pair_adjacent: alarm vs melee unclear (1 case, melee)"
            if arrows <= 0:
                return None, "orc_pair_no_arrows: hold vs alarm split (4 cases, hold 3 / alarm 1)"
            if time == "night":
                return None, "orc_pair_night: shoot vs alarm split (2 cases, 1/1)"
            # 昼・離れて・矢あり → 射る(4/4)
            return "shoot", "orc_pair_day_shoot"
        # ゴブリン 2 体まで・オーク 1 体は深刻ではない。夜でも通常の戦闘へ(6/6)

    # --- トロル(警報は鳴っている)、味方なし ---
    if enemy == "troll" and allies <= 0:
        # 「トロルは一人で相手にするには強すぎる」+「無駄死にはしない」(隣接 1 + 離れて 6、7/7)
        return "retreat", "troll_alone_retreat"

    # --- 中間帯で回復薬なし: 戦うか退くかが割れる ---
    if mid_hp_no_potion:
        return None, mid_fight_reason

    # --- 隣接 ---
    if adjacent:
        if outnumbered:
            return None, "outnumbered_adjacent: fight vs retreat unclear (1 case, melee)"
        # 「隣接していれば近接で戦う」
        return "melee_attack", "adjacent_melee"

    # --- 離れている ---
    if arrows <= 0:
        if enemy == "troll":
            return None, "troll_no_arrows: cover vs hold unclear (1 case, take_cover)"
        # 矢が無ければ持ち場を守る(19/19)
        return "hold_position", "no_arrows_hold"

    if outnumbered and time == "night" and cover:
        # shoot 2 / take_cover 1
        return None, "outnumbered_night_cover: shoot vs take_cover split (3 cases, 2/1)"

    # 「敵が離れていて矢が残っていれば弓で射る」
    return "shoot", "ranged_shoot"
