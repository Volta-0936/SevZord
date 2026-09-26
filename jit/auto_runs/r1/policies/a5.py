"""城の番兵NPC 方針 — 走り r1、第 5 版 (a5)

この版で変えたこと(根拠は熱さの帳簿 405 件と、その食い違い・棄権の例の一覧)
------------------------------------------------------------------------------
1. 警報未鳴動・昼・離れて矢ありの魔術師 3 体以上(番人 mage_group_day_alarm_silent)を
   多勢に無勢かどうかで分けた。
   - 10 件で raise_alarm 7 / shoot 3(70%)で、まとめると 80% に届かない。
     a4 の時点の 6 件に 4 件加わった(raise_alarm 3 / shoot 1)。
   - 多勢に無勢(敵の数 − (番兵+味方) >= 2。a4 から使っている OUTNUMBERED_MARGIN で、
     新しい線ではない)→ 警報 (mage_group_day_outnumbered_alarm)。5 件で raise_alarm 5/5。
     5 体・味方1 が 2 件(hp64 距離7、hp60 距離12)、4 体・味方1 が 1 件(hp73 距離4)、
     3 体・味方0 が 2 件(hp86 距離7、hp99 距離11)。enemy_hp は 40〜90。
     番兵側が数で負けている魔術師の群れは「深刻な脅威」と読める。
     5 体と 4 体だけ(3/3)でも線は引けるが、3 体・味方0 の 2 件も同じ答えなので、
     体数ではなく既存の多勢の線でまとめた。
   - 多勢でない → 棄権のまま (mage_group_day_alarm_silent)。5 件で raise_alarm 2 / shoot 3。
     raise_alarm は 3 体・味方1 hp99 距離12、3 体・味方3 hp59 距離11。
     shoot は 3 体・味方1 hp80 距離7、3 体・味方2 hp89 距離10、3 体・味方3 hp75 距離6。
     距離 11 以上は raise_alarm 2/2 だが 2 件しか無く、a4 と同じく mage_ranged_shoot は
     距離によらず射っているので、距離の線は引かない。
   - hp 33〜39・回復薬なしで多勢の魔術師の群れは例 0 件なので、答えずにこの番人に残す。
2. 警報未鳴動で隣接の魔術師に多勢に無勢(番人 outnumbered_adjacent_alarm_silent)を
   昼夜で分けた。
   - 4 件で raise_alarm 3 / melee 1(75%)。a4 の時点の 3 件に、
     4 体・味方1・昼(hp51・enemy_hp80)の raise_alarm が 1 件加わり、昼が 3 件になった。
   - 昼 → 警報 (outnumbered_adjacent_day_alarm)。3 件で raise_alarm 3/3。
     5 体・味方0 hp74 enemy_hp30、3 体・味方0 hp60 enemy_hp70、4 体・味方1 hp51 enemy_hp80。
     1. の多勢の魔術師の群れ(昼・離れて)の警報 5/5 とも揃う。
   - 夜の 1 件(3 体・味方0 hp58 → melee)は enemy_hp 10 で、夜のせいか
     「魔術師は早く仕留めるべきだ」で止めを刺したのか、1 件では分からない。
     そこで次の番人を足した。
   - 新しい番人 mage_nearly_dead_alarm_silent: 1. と 2. の答える枝では、
     enemy_hp が 20 以下(または不明)の魔術師は棄権する。
     線 20 は、夜の melee の 10 と、昼の警報の最小 30 の間に置いた
     (1. の多勢の警報は enemy_hp 40 以上、多勢でない群れの shoot には enemy_hp20 がある)。
     この番人に入る例は夜の melee の 1 件だけ。
   - 夜で enemy_hp 21 以上は例 0 件なので outnumbered_adjacent_alarm_silent で棄権する。
     hp 33〜39・回復薬なしも例 0 件なので、この番人に残す。
3. 警報既鳴・味方ありのトロルが離れていて矢なし(番人 troll_no_arrows)を距離で分けた。
   - 4 件で take_cover 3 / hold 1(75%)。a4 の時点の 1 件に 3 件加わった。
   - 遮蔽あり・距離 6 以下 → 遮蔽に隠れる (troll_no_arrows_cover)。3 件で take_cover 3/3。
     3 件とも距離 4・遮蔽あり(2 体・味方1・昼 hp42、1 体・味方2・夜 hp84、
     2 体・味方3・夜 hp82)。hold の 1 件は距離 9(4 体・味方3・昼 hp87)。
     線 6 は 4 と 9 の間に置いた。
     「トロルは一人で相手にするには強すぎる」うえに矢が無くて射てないので、
     近いトロルからは遮蔽に隠れる、と読める。遮蔽が無ければ隠れられないので遮蔽ありに限る。
   - 距離 7 以上(hold 1 件)と遮蔽なし(例 0 件)は棄権のまま (troll_no_arrows)。
     hp_mid_no_potion_fight にも遠いトロル・矢なしの hold が 1 件(距離12 hp35)あるが、
     合わせても 2 件なので「遠ければ持ち場」の線は引かない。
4. 棄権の理由に書いた件数を帳簿に合わせて直した(枝の名は変えない)。
   - mid_potion_no_threat: 7 件で drink 4 / hold 3(57%)。新しい 1 件は hp37・味方0・城壁 → hold。
     持ち場で見ると門は drink 4 / hold 1(80%)、門以外は hold 2/2 だが、
     門は 80% ちょうどで門の hold が 1 件増えれば崩れ、門以外は 2 件しか無い。
     持ち場で回復薬を飲むかどうかが変わる理由も指示文からは読めないので、線は引かない。
   - hp_mid_no_potion_fight: 6 件で retreat 2 / melee 1 / raise_alarm 1 / hold 1 / shoot 1。
     新しい 3 件は、オーク 2 体隣接・昼・味方0 hp36 → raise_alarm、
     トロル 1 体・距離12・警報既鳴・矢なし hp35 → hold、
     魔術師 2 体・距離3・警報既鳴・昼 hp38 → shoot。どれも別の状況で 1 件ずつなので線は引けない。

変えなかった所
--------------
- 「ひどく傷ついている」の線 hp <= 32、重傷は警報より先
  (badly_hurt_potion 22/22、badly_hurt_retreat 32/33)。
  badly_hurt_retreat の食い違い 1 件(hp26・トロル 2 体・距離10・警報未鳴動・矢なし → raise_alarm)は
  1 件なので、重傷と警報の順は変えない。
- no_threat 98/100(98%)。食い違いは a4 と同じ 2 件(hp 33〜39・回復薬なし・敵なし → retreat)。
  「脅威が無ければ持ち場を守る」をそのまま読んだ規則として hold を保つ。
- ranged_shoot 45/46(98%)、no_arrows_hold 26/27(96%)。食い違いは a4 と同じ 1 件ずつ。
- alarm_group 22/25(88%)。食い違い 3 件はどれもゴブリン 3 体・昼。
  hold(矢なし・味方0・距離6)が 1 件、shoot(味方1・矢あり、距離10 門 / 距離2 廊下)が 2 件。
  ゴブリン 3 体・昼・味方1 の shoot は 2 件だけで、帳簿は alarm_group をまとめて数えているので
  同じ状況の raise_alarm の件数が分からない。線は引かない。
- alarm_troll 12/13(92%)。食い違い 1 件(トロル 1 体・距離2・enemy_hp10・味方0・昼 → shoot)。
  1 件なので変えない。
- mage_ranged_shoot 16/16、adjacent_melee 15/15、troll_alone_retreat 10/10、
  outnumbered_adjacent_melee 8/8、mid_hurt_potion 6/6、mage_group_night_alarm 5/5、
  mage_no_arrows_alarm 4/4、orc_pair_day_shoot 4/4、mage_adjacent_melee 4/4、
  mid_hp_single_fight 3/3、orc_pair_adjacent_melee 3/3。
- mid_potion_night_drink 5/6(83%)、orc_pair_no_arrows_hold 4/5、outnumbered_night_shoot 4/5、
  mid_hp_pair_retreat 4/5、orc_pair_night_alone_alarm 4/5(各 80%)。
  a4 から例が増えておらず、中身は同じ。

棄権のまま残した所
------------------
- mid_potion_no_threat(昼): 上の 4. のとおり 7 件で drink 4 / hold 3。
- orc_pair_night(味方あり): 4 件で raise_alarm 2 / shoot 2。a4 と同じ。
- mage_group_day_alarm_silent(多勢でない): 上の 1. のとおり 5 件で raise_alarm 2 / shoot 3。
- mage_nearly_dead_alarm_silent(新しい番人): 上の 2. のとおり 1 件(夜・隣接・enemy_hp10 → melee)。
- hp_mid_no_potion_fight: 上の 4. のとおり 6 件で答えが 5 通りに割れている。
- outnumbered_adjacent_alarm_silent(夜で体力のある魔術師、または hp 33〜39・回復薬なし): 例 0 件。
- outnumbered_adjacent: トロルの多勢は例 0 件。
- troll_no_arrows(距離 7 以上、または遮蔽なし): hold 1 件(距離9)。

枝の名(答える枝)
------------------
no_threat, badly_hurt_potion, badly_hurt_retreat, mid_potion_night_drink, mid_hurt_potion,
alarm_troll, alarm_group, mage_adjacent_melee, outnumbered_adjacent_day_alarm,
mage_no_arrows_alarm, mage_group_night_alarm, mage_group_day_outnumbered_alarm,
mage_ranged_shoot, orc_pair_day_shoot, orc_pair_adjacent_melee, orc_pair_no_arrows_hold,
orc_pair_night_alone_alarm, mid_hp_pair_retreat, troll_alone_retreat, mid_hp_single_fight,
outnumbered_adjacent_melee, adjacent_melee, troll_no_arrows_cover, no_arrows_hold,
outnumbered_night_shoot, ranged_shoot
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
GROUP_MIN = 3            # この数以上なら群れ(ゴブリン/オーク 22/25 が raise_alarm、魔術師の警報もすべて 3 体以上)
OUTNUMBERED_MARGIN = 2   # 敵の数が番兵+味方より、これ以上多ければ多勢に無勢
MAGE_NEARLY_DEAD_MAX = 20  # 多勢の魔術師: 夜の隣接 melee は enemy_hp10、昼の警報は enemy_hp30〜90。10 と 30 の間
TROLL_COVER_MAX_DIST = 6   # トロル・矢なし・遮蔽あり: 距離4 の take_cover 3/3、距離9 の hold 1。4 と 9 の間


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
    enemy_hp = _num(s.get("enemy_hp"))
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
        "hp_mid_no_potion_fight: answers split at hp 33-39 without potion "
        "(6 cases: retreat 2 / melee 1 / alarm 1 / hold 1 / shoot 1)"
    )
    mage_nearly_dead_reason = (
        "mage_nearly_dead_alarm_silent: finish vs alarm unclear for an outnumbering "
        "mage group at enemy_hp <= 20 or unknown (1 case: night adjacent enemy_hp 10 -> melee)"
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
            # 昼: drink 4 / hold 3
            return None, "mid_potion_no_threat: drink vs hold split by day (7 cases, drink 4 / hold 3)"
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
    mage_hp_unclear = enemy_hp is None or enemy_hp <= MAGE_NEARLY_DEAD_MAX

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
            # 「警報がまだ鳴っておらず、深刻な脅威が現れたなら警報を鳴らす」(12/13)
            return "raise_alarm", "alarm_troll"
        if enemy == "mage":
            if adjacent:
                if outnumbered:
                    if not mid_hp_no_potion:
                        if mage_hp_unclear:
                            return None, mage_nearly_dead_reason
                        if time == "day":
                            # 隣接の魔術師に多勢に無勢・昼 → 警報(3/3)
                            return "raise_alarm", "outnumbered_adjacent_day_alarm"
                    return None, (
                        "outnumbered_adjacent_alarm_silent: no example at night with "
                        "enemy_hp > 20, or at hp 33-39 without potion (0 cases)"
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
                if outnumbered and not mid_hp_no_potion:
                    if mage_hp_unclear:
                        return None, mage_nearly_dead_reason
                    # 魔術師の群れに多勢に無勢・昼 → 警報(5/5)
                    return "raise_alarm", "mage_group_day_outnumbered_alarm"
                # 昼・多勢でない: raise_alarm 2 / shoot 3
                return None, (
                    "mage_group_day_alarm_silent: shoot vs alarm split when not outnumbered "
                    "(5 cases, alarm 2 / shoot 3; outnumbered at hp 33-39 without potion 0 cases)"
                )
            if mid_hp_no_potion:
                return None, mid_fight_reason
            # 魔術師 2 体まで・離れて・矢あり → 射る(16/16)
            return "shoot", "mage_ranged_shoot"
        # goblin / orc
        if enemy_count >= GROUP_MIN:
            # 3 体以上は深刻な脅威 → 警報(隣接していても。22/25)
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
        # 「トロルは一人で相手にするには強すぎる」+「無駄死にはしない」(10/10)
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
                # 警報既鳴・多勢に無勢でも隣接なら近接(8/8)
                return "melee_attack", "outnumbered_adjacent_melee"
            return None, "outnumbered_adjacent: no examples for troll or alarm not raised (0 cases)"
        # 「隣接していれば近接で戦う」(15/15)
        return "melee_attack", "adjacent_melee"

    # --- 離れている ---
    if arrows <= 0:
        if enemy == "troll":
            if cover and d <= TROLL_COVER_MAX_DIST:
                # 味方ありのトロル・矢なし・近い・遮蔽あり → 隠れる(3/3、すべて距離 4)
                return "take_cover", "troll_no_arrows_cover"
            return None, (
                "troll_no_arrows: far troll or no cover without arrows "
                "(1 case, distance 9 -> hold)"
            )
        # 矢が無ければ持ち場を守る(26/27)
        return "hold_position", "no_arrows_hold"

    if outnumbered and time == "night" and cover:
        # 多勢・夜・遮蔽あり: shoot 4 / take_cover 1(80%)
        return "shoot", "outnumbered_night_shoot"

    # 「敵が離れていて矢が残っていれば弓で射る」(45/46)
    return "shoot", "ranged_shoot"
