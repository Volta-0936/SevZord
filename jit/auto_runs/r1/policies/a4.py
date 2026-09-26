"""城の番兵NPC 方針 — 走り r1、第 4 版 (a4)

この版で変えたこと(根拠は熱さの帳簿 344 件と、その食い違い・棄権の例の一覧)
------------------------------------------------------------------------------
1. 敵なし・hp 33〜39・回復薬あり(番人 mid_potion_no_threat)を昼夜で分けた。
   - 12 件で drink_potion 9 / hold_position 3(75%)で、まとめると 80% に届かない。
   - 夜 → 飲む (mid_potion_night_drink)。6 件で drink 5 / hold 1(83%)。
     drink は hp35・35・37・38・39、hold は hp38(味方 1・門)の 1 件。
     「夜は用心深く」とも合う。
   - 昼 → 棄権のまま (mid_potion_no_threat)。6 件で drink 4 / hold 2(67%)。
     hold の hp39・35 は drink の hp33〜39 と重なり、hp の線は引けない。
   - hold 3 件だけを分ける項目は矢の数(2〜4)しか無いが、敵のいない時に
     回復薬を飲むかどうかと矢は関わらないので、この線は引かない。
2. hp 33〜39・回復薬なし・警報未鳴動・ゴブリン/オーク 2 体・離れて矢あり → 退く
   (mid_hp_pair_retreat)。番人 hp_mid_no_potion_fight から外した。
   - 5 件で retreat 4 / shoot 1(80%)。a3 の時点の retreat 3 / shoot 1 に、
     ゴブリン 2 体(hp33・昼・味方 1)の retreat が 1 件加わった。
   - retreat: オーク 2 体 hp37 昼 味方1、ゴブリン 2 体 hp34 昼 味方3、
     オーク 2 体 hp33 夜 味方2、ゴブリン 2 体 hp33 昼 味方1。
     shoot: ゴブリン 2 体 hp36 昼 味方0 の 1 件。1 件なので味方の数の線は引かない。
   - 「無駄死にはしない」と合う。敵 1 体・昼なら戦う (mid_hp_single_fight 3/3) ので、
     この帯では敵の数で答えが分かれる。
   - 例はすべて警報未鳴動・距離 7〜12・矢 4〜17。隣接・矢なし・警報既鳴の 2 体は
     例 0 件なので、hp_mid_no_potion_fight の番人に残した。
   - 残りの hp_mid_no_potion_fight は 3 件で retreat 2 / melee 1。
     魔術師 4 体隣接(melee)、トロル・警報既鳴・夜(retreat)、
     オーク 1 体・夜・矢なし(retreat)が 1 件ずつで、どれも線は引けない。
     夜だけ見ると retreat 3/3 だが、そのうち 2 件はオーク 2 体とトロルで別の状況、
     夜の敵 1 体(トロル以外)は 1 件しか無いので、夜の線は引かない。
3. 警報未鳴動のオーク 2 体・夜・離れて矢あり(番人 orc_pair_night)を味方の数で分けた。
   - 9 件で raise_alarm 6 / shoot 3(67%)。
   - 味方なし → 警報 (orc_pair_night_alone_alarm)。5 件で raise_alarm 4 / shoot 1(80%)。
     raise_alarm は hp62〜91・距離 4〜12、shoot の 1 件は hp99・距離 3。
     1 件なので距離の線は引かない。
     番兵ひとりで夜にオーク 2 体は「深刻な脅威」「夜は用心深く」と読める。
   - 味方あり → 棄権のまま (orc_pair_night)。4 件で raise_alarm 2 / shoot 2。
     raise_alarm は hp61・40、shoot は hp85・62 で、線は引けない。
4. 棄権の理由に書いた件数を帳簿に合わせて直した(枝の名は変えない)。
   - mage_group_day_alarm_silent: 6 件で raise_alarm 4 / shoot 2(67%)。
   - outnumbered_adjacent_alarm_silent: 3 件で raise_alarm 2 / melee 1(67%)。
     昼 2 件が raise_alarm、夜 1 件が melee。昼夜それぞれ 2 件以下なので線は引かない。

変えなかった所
--------------
- 「ひどく傷ついている」の線 hp <= 32、重傷は警報より先
  (badly_hurt_potion 21/21、badly_hurt_retreat 24/24)。
- no_threat 76/78(97%)。食い違い 2 件はどちらも hp 33〜39・回復薬なし・敵なし → retreat
  (hp33 昼 廊下 味方1、hp39 夜 門 味方1)。帳簿は no_threat をまとめて数えているので、
  この帯の hold の件数は分からない。「脅威が無ければ持ち場を守る」を
  そのまま読んだ規則として hold を保つ。
- ranged_shoot 43/44(98%)。食い違い 1 件(オーク 2 体・夜・遮蔽・味方 0・警報既鳴 → take_cover)。
- no_arrows_hold 23/24(96%)。食い違い 1 件(ゴブリン 1 体・夜・遮蔽・味方 0 → take_cover)。
- alarm_group 20/22(91%)。食い違い 2 件はどちらもゴブリン 3 体・昼だが、
  答えが hold(矢なし・味方0)と shoot(矢18・味方1・距離10)で別々。1 件ずつなので線は引かない。
- mage_ranged_shoot 15/15、adjacent_melee 13/13、alarm_troll 11/11、troll_alone_retreat 8/8、
  mid_hurt_potion 6/6、outnumbered_adjacent_melee 6/6、mage_group_night_alarm 5/5、
  mage_no_arrows_alarm 4/4、orc_pair_day_shoot 4/4、mage_adjacent_melee 4/4、
  mid_hp_single_fight 3/3、orc_pair_adjacent_melee 3/3。
- orc_pair_no_arrows_hold 4/5(80%)、outnumbered_night_shoot 4/5(80%)。
  a3 から例が増えておらず、中身は同じ。

棄権のまま残した所
------------------
- mid_potion_no_threat(昼): 上の 1. のとおり 6 件で drink 4 / hold 2。
- orc_pair_night(味方あり): 上の 3. のとおり 4 件で raise_alarm 2 / shoot 2。
- mage_group_day_alarm_silent: 6 件で raise_alarm 4 / shoot 2(67%)。
  5 体は raise_alarm 2/2、3 体は raise_alarm 2 / shoot 2。
  距離 11 以上は raise_alarm 3/3 だが、shoot の距離 10 と隣り合って例の間に線を置けず、
  mage_ranged_shoot は距離によらず射っているので、距離の線は引かない。
- hp_mid_no_potion_fight: 上の 2. のとおり 3 件で retreat 2 / melee 1。
- outnumbered_adjacent_alarm_silent: 上の 4. のとおり。
- outnumbered_adjacent: トロルの多勢は例 0 件。
- troll_no_arrows: 1 件(味方ありのトロル・離れて矢なし → take_cover 1)。

枝の名(答える枝)
------------------
no_threat, badly_hurt_potion, badly_hurt_retreat, mid_potion_night_drink, mid_hurt_potion,
alarm_troll, alarm_group, mage_adjacent_melee, mage_no_arrows_alarm, mage_group_night_alarm,
mage_ranged_shoot, orc_pair_day_shoot, orc_pair_adjacent_melee, orc_pair_no_arrows_hold,
orc_pair_night_alone_alarm, mid_hp_pair_retreat, troll_alone_retreat, mid_hp_single_fight,
outnumbered_adjacent_melee, adjacent_melee, no_arrows_hold, outnumbered_night_shoot,
ranged_shoot
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
HP_FINE_MIN = 40         # 33〜39 は中間帯。敵ありで回復薬ありなら飲む(6/6)、hp42 は飲まない
ADJACENT_MAX = 1         # これ以下は隣接
GROUP_MIN = 3            # この数以上なら群れ(ゴブリン/オーク 20/22 が raise_alarm、魔術師の警報もすべて 3 体以上)
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
        "hp_mid_no_potion_fight: fight vs retreat unclear at hp 33-39 without potion "
        "(3 cases left: retreat 2 / melee 1)"
    )

    # --- 脅威が無い ---
    if enemy == "none":
        if enemy_count and enemy_count > 0:
            return None, "inconsistent_state: enemy none but enemy_count > 0"
        if badly_hurt:
            if potion:
                # 「ひどく傷ついているなら、回復薬があれば飲み」
                return "drink_potion", "badly_hurt_potion"
            # 「なければ退く」— 脅威が無くても退く
            return "retreat", "badly_hurt_retreat"
        if mid_hp_potion:
            if time == "night":
                # 敵なし・hp33〜39・回復薬あり・夜: drink 5 / hold 1(83%)。「夜は用心深く」
                return "drink_potion", "mid_potion_night_drink"
            # 昼: drink 4 / hold 2
            return None, "mid_potion_no_threat: drink vs hold split by day (6 cases, drink 4 / hold 2)"
        # 「脅威が無ければ持ち場を守る」(hp33〜39・回復薬なしも hold。食い違い retreat 2 件)
        return "hold_position", "no_threat"

    # --- 敵がいる ---
    if enemy_count <= 0:
        return None, "inconsistent_state: enemy present but enemy_count 0"
    d = _num(distance)
    if d is None:
        return None, "inconsistent_state: enemy present but distance missing"
    adjacent = d <= ADJACENT_MAX
    outnumbered = enemy_count - (allies + 1) >= OUTNUMBERED_MARGIN

    # hp33〜39・回復薬なし・警報未鳴動・ゴブリン/オーク 2 体・離れて矢あり(retreat 4 / shoot 1)
    mid_pair_ranged = (
        mid_hp_no_potion
        and not alarm
        and enemy in ("goblin", "orc")
        and enemy_count == 2
        and not adjacent
        and arrows > 0
    )

    # --- ひどく傷ついている(警報の規則より先) ---
    if badly_hurt:
        if potion:
            return "drink_potion", "badly_hurt_potion"
        return "retreat", "badly_hurt_retreat"

    # --- 中間帯で回復薬あり・敵あり(警報・魔術師・群れの規則より先。6/6) ---
    if mid_hp_potion:
        return "drink_potion", "mid_hurt_potion"

    # ここから「ひどく傷ついていない」、または hp33〜39 で回復薬なし

    # --- 警報がまだ鳴っていない ---
    if not alarm:
        if enemy == "troll":
            # 「警報がまだ鳴っておらず、深刻な脅威が現れたなら警報を鳴らす」(11/11)
            return "raise_alarm", "alarm_troll"
        if enemy == "mage":
            if adjacent:
                if outnumbered:
                    return None, (
                        "outnumbered_adjacent_alarm_silent: alarm vs melee split "
                        "(3 cases, alarm 2 / melee 1)"
                    )
                if mid_hp_no_potion:
                    return None, mid_fight_reason
                # 「隣接していれば近接で戦う」+「魔術師は早く仕留める」(4/4)
                return "melee_attack", "mage_adjacent_melee"
            if arrows <= 0:
                # 射てない魔術師には警報(4/4)
                return "raise_alarm", "mage_no_arrows_alarm"
            if enemy_count >= GROUP_MIN:
                if time == "night":
                    # 魔術師+群れ、夜 → 警報(5/5)
                    return "raise_alarm", "mage_group_night_alarm"
                # 昼: raise_alarm 4 / shoot 2
                return None, (
                    "mage_group_day_alarm_silent: shoot vs alarm split "
                    "(6 cases, alarm 4 / shoot 2)"
                )
            if mid_hp_no_potion:
                return None, mid_fight_reason
            # 魔術師 2 体まで・離れて・矢あり → 射る(15/15)
            return "shoot", "mage_ranged_shoot"
        # goblin / orc
        if enemy_count >= GROUP_MIN:
            # 3 体以上は深刻な脅威 → 警報(隣接していても。20/22)
            return "raise_alarm", "alarm_group"
        if enemy == "orc" and enemy_count >= 2:
            if mid_hp_no_potion:
                if mid_pair_ranged:
                    # 中間帯・回復薬なしで 2 体 → 退く(retreat 4 / shoot 1、80%)
                    return "retreat", "mid_hp_pair_retreat"
                return None, mid_fight_reason
            if adjacent:
                # 「隣接していれば近接で戦う」(3/3)
                return "melee_attack", "orc_pair_adjacent_melee"
            if arrows <= 0:
                # 離れて矢なし → 持ち場(hold 4 / alarm 1、80%)
                return "hold_position", "orc_pair_no_arrows_hold"
            if time == "night":
                if allies <= 0:
                    # 番兵ひとり・夜・オーク 2 体 → 警報(alarm 4 / shoot 1、80%)
                    return "raise_alarm", "orc_pair_night_alone_alarm"
                return None, (
                    "orc_pair_night: shoot vs alarm split with allies "
                    "(4 cases, alarm 2 / shoot 2)"
                )
            # 昼・離れて・矢あり → 射る(4/4)
            return "shoot", "orc_pair_day_shoot"
        # ゴブリン 2 体まで・オーク 1 体は深刻ではない。夜でも通常の戦闘へ

    # --- トロル(警報は鳴っている)、味方なし ---
    if enemy == "troll" and allies <= 0:
        # 「トロルは一人で相手にするには強すぎる」+「無駄死にはしない」(8/8)
        return "retreat", "troll_alone_retreat"

    # --- 中間帯で回復薬なし ---
    if mid_hp_no_potion:
        if (
            enemy in ("goblin", "orc")
            and enemy_count == 1
            and time == "day"
            and (adjacent or arrows > 0)
        ):
            # ゴブリン/オーク 1 体・昼 → 通常の戦い(3/3: shoot 2 / melee 1、退く 0)
            if adjacent:
                return "melee_attack", "mid_hp_single_fight"
            return "shoot", "mid_hp_single_fight"
        if mid_pair_ranged:
            # ゴブリン 2 体(オーク 2 体は上で受ける)→ 退く(retreat 4 / shoot 1、80%)
            return "retreat", "mid_hp_pair_retreat"
        return None, mid_fight_reason

    # --- 隣接 ---
    if adjacent:
        if outnumbered:
            if alarm and enemy in ("goblin", "orc", "mage"):
                # 警報既鳴・多勢に無勢でも隣接なら近接(6/6)
                return "melee_attack", "outnumbered_adjacent_melee"
            return None, "outnumbered_adjacent: no examples for troll or alarm not raised (0 cases)"
        # 「隣接していれば近接で戦う」
        return "melee_attack", "adjacent_melee"

    # --- 離れている ---
    if arrows <= 0:
        if enemy == "troll":
            return None, "troll_no_arrows: cover vs hold unclear (1 case, take_cover)"
        # 矢が無ければ持ち場を守る(23/24)
        return "hold_position", "no_arrows_hold"

    if outnumbered and time == "night" and cover:
        # 多勢・夜・遮蔽あり: shoot 4 / take_cover 1(80%)
        return "shoot", "outnumbered_night_shoot"

    # 「敵が離れていて矢が残っていれば弓で射る」(43/44)
    return "shoot", "ranged_shoot"
