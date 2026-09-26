# 翻訳の依頼 — 走り r1、第 5 版

あなたは翻訳役だ。審判(別の LLM)が指示文に従って下す判断を、番人付きの Python の方針に翻訳する。
目的は、審判と同じ答えを出すこと。審判の答えが割れている所や、例が足りない所は棄権して審判に回す。
読んでよいのはこの依頼書だけ。ほかのファイル(ほかの方針、保留のデータ、別の走り)は開かないこと。

## 審判が受け取っている指示文
```
城の番兵NPCの、このターンの行動を一つ選ぶ。番兵は忠実だが、無駄死にはしない。門を守りつつ生き延びること。
- ひどく傷ついているなら、回復薬があれば飲み、なければ退く。
- 敵が離れていて矢が残っていれば弓で射る。隣接していれば近接で戦う。
- トロルは一人で相手にするには強すぎる。
- 魔術師は早く仕留めるべきだ。
- 警報がまだ鳴っておらず、深刻な脅威が現れたなら警報を鳴らす。
- 夜は用心深く。
- 脅威が無ければ持ち場を守る。

行動: melee_attack(近接攻撃), shoot(弓で射る), retreat(退く), drink_potion(回復薬を飲む), take_cover(遮蔽に隠れる), raise_alarm(警報を鳴らす), hold_position(持ち場を守る)
状態の項目: hp(番兵の体力 0-100), enemy(最も近い敵の種類: none/goblin/orc/mage/troll), distance(その敵までのマス数、敵がいなければ null), enemy_count(見えている敵の数), enemy_hp(最も近い敵の体力 %), allies(近くの味方の数), potion(回復薬を持っているか), arrows(矢の残り), cover(近くに遮蔽物があるか), alarm(警報が既に鳴っているか), post(持ち場: gate/wall/corridor), time(day/night)
```

## 書く物の約束
- ファイルは Python 一つ。関数 `decide(s)` を一つ定義する。`s` は状態の dict(項目は下の指示文を参照、distance と enemy_hp は敵がいなければ None)。
- 返り値は `(行動, 枝の名)` か `(None, 棄権の理由)`。行動は次の 7 つの文字列のどれか: melee_attack, shoot, retreat, drink_potion, take_cover, raise_alarm, hold_position。
- 枝の名は、その答えを出した規則の短い英字の名前(例: "no_threat")。同じ規則には同じ名前を使い続ける(帳簿は枝の名で数える)。
- 標準ライブラリ以外を import しない。外部の状態を持たない。
- ファイルの冒頭の docstring に、この版で何を変えたかと、その根拠(帳簿の件数)を書く。

## 翻訳の規律(門がコードで検査する)
- 枝が答えてよいのは、(a) 指示文をそのまま読んだ規則か、(b) 帳簿でその状況の一貫した例が 3 件以上あり、その答えが 80% 以上を占める時だけ。
- 例が 1〜2 件しかない状況、または審判の答えが割れている状況は、名前を付けた番人で棄権する(`return None, "理由"`)。棄権は失敗ではない。審判に任せる正しい手だ。
- 帳簿の例に過剰に合わせない。閾値は例の間に置き、根拠の件数を docstring に書く。

## いまの方針(a4)
```python
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

```

## 熱さの帳簿(これまでの審判のラベル 405 件を、いまの方針の枝ごとに数えた)

| 枝 | 件数 | 方針の答え | 一致 | 審判の答え |
|---|---|---|---|---|
| no_threat | 100 | hold_position | 98/100 | {'hold_position': 98, 'retreat': 2} |
| ranged_shoot | 46 | shoot | 45/46 | {'shoot': 45, 'take_cover': 1} |
| badly_hurt_retreat | 33 | retreat | 32/33 | {'retreat': 32, 'raise_alarm': 1} |
| no_arrows_hold | 27 | hold_position | 26/27 | {'hold_position': 26, 'take_cover': 1} |
| alarm_group | 25 | raise_alarm | 22/25 | {'raise_alarm': 22, 'hold_position': 1, 'shoot': 2} |
| badly_hurt_potion | 22 | drink_potion | 22/22 | {'drink_potion': 22} |
| mage_ranged_shoot | 16 | shoot | 16/16 | {'shoot': 16} |
| adjacent_melee | 15 | melee_attack | 15/15 | {'melee_attack': 15} |
| alarm_troll | 13 | raise_alarm | 12/13 | {'raise_alarm': 12, 'shoot': 1} |
| troll_alone_retreat | 10 | retreat | 10/10 | {'retreat': 10} |
| mage_group_day_alarm_silent: shoot vs alarm split (6 cases, alarm 4 / shoot 2) | 10 | None | 0/- | {'raise_alarm': 7, 'shoot': 3} |
| outnumbered_adjacent_melee | 8 | melee_attack | 8/8 | {'melee_attack': 8} |
| mid_potion_no_threat: drink vs hold split by day (6 cases, drink 4 / hold 2) | 7 | None | 0/- | {'drink_potion': 4, 'hold_position': 3} |
| mid_potion_night_drink | 6 | drink_potion | 5/6 | {'hold_position': 1, 'drink_potion': 5} |
| mid_hurt_potion | 6 | drink_potion | 6/6 | {'drink_potion': 6} |
| hp_mid_no_potion_fight: fight vs retreat unclear at hp 33-39 without potion (3 cases left: retreat 2 / melee 1) | 6 | None | 0/- | {'melee_attack': 1, 'retreat': 2, 'raise_alarm': 1, 'hold_position': 1, 'shoot': 1} |
| orc_pair_no_arrows_hold | 5 | hold_position | 4/5 | {'raise_alarm': 1, 'hold_position': 4} |
| outnumbered_night_shoot | 5 | shoot | 4/5 | {'shoot': 4, 'take_cover': 1} |
| mage_group_night_alarm | 5 | raise_alarm | 5/5 | {'raise_alarm': 5} |
| mid_hp_pair_retreat | 5 | retreat | 4/5 | {'retreat': 4, 'shoot': 1} |
| orc_pair_night_alone_alarm | 5 | raise_alarm | 4/5 | {'shoot': 1, 'raise_alarm': 4} |
| mage_no_arrows_alarm | 4 | raise_alarm | 4/4 | {'raise_alarm': 4} |
| orc_pair_day_shoot | 4 | shoot | 4/4 | {'shoot': 4} |
| mage_adjacent_melee | 4 | melee_attack | 4/4 | {'melee_attack': 4} |
| orc_pair_night: shoot vs alarm split with allies (4 cases, alarm 2 / shoot 2) | 4 | None | 0/- | {'raise_alarm': 2, 'shoot': 2} |
| troll_no_arrows: cover vs hold unclear (1 case, take_cover) | 4 | None | 0/- | {'take_cover': 3, 'hold_position': 1} |
| outnumbered_adjacent_alarm_silent: alarm vs melee split (3 cases, alarm 2 / melee 1) | 4 | None | 0/- | {'raise_alarm': 3, 'melee_attack': 1} |
| mid_hp_single_fight | 3 | shoot | 3/3 | {'shoot': 2, 'melee_attack': 1} |
| orc_pair_adjacent_melee | 3 | melee_attack | 3/3 | {'melee_attack': 3} |

## 食い違いと棄権の例(全部)
### no_threat
- 方針=hold_position 審判=retreat | hp=33 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=7 cover=True alarm=False post=corridor time=day
- 方針=hold_position 審判=retreat | hp=39 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=8 cover=False alarm=False post=gate time=night
### ranged_shoot
- 方針=shoot 審判=take_cover | hp=71 enemy=orc distance=5 enemy_count=2 enemy_hp=90 allies=0 potion=True arrows=13 cover=True alarm=True post=gate time=night
### badly_hurt_retreat
- 方針=retreat 審判=raise_alarm | hp=26 enemy=troll distance=10 enemy_count=2 enemy_hp=80 allies=1 potion=False arrows=0 cover=True alarm=False post=corridor time=day
### no_arrows_hold
- 方針=hold_position 審判=take_cover | hp=91 enemy=goblin distance=4 enemy_count=1 enemy_hp=30 allies=0 potion=True arrows=0 cover=True alarm=False post=corridor time=night
### alarm_group
- 方針=raise_alarm 審判=hold_position | hp=79 enemy=goblin distance=6 enemy_count=3 enemy_hp=10 allies=0 potion=True arrows=0 cover=False alarm=False post=gate time=day
- 方針=raise_alarm 審判=shoot | hp=75 enemy=goblin distance=10 enemy_count=3 enemy_hp=50 allies=1 potion=False arrows=18 cover=True alarm=False post=gate time=day
- 方針=raise_alarm 審判=shoot | hp=63 enemy=goblin distance=2 enemy_count=3 enemy_hp=20 allies=1 potion=True arrows=7 cover=True alarm=False post=corridor time=day
### alarm_troll
- 方針=raise_alarm 審判=shoot | hp=46 enemy=troll distance=2 enemy_count=1 enemy_hp=10 allies=0 potion=True arrows=11 cover=False alarm=False post=corridor time=day
### mage_group_day_alarm_silent: shoot vs alarm split (6 cases, alarm 4 / shoot 2)
- 方針=None 審判=raise_alarm | hp=64 enemy=mage distance=7 enemy_count=5 enemy_hp=40 allies=1 potion=False arrows=9 cover=True alarm=False post=corridor time=day
- 方針=None 審判=shoot | hp=80 enemy=mage distance=7 enemy_count=3 enemy_hp=60 allies=1 potion=False arrows=5 cover=False alarm=False post=gate time=day
- 方針=None 審判=raise_alarm | hp=60 enemy=mage distance=12 enemy_count=5 enemy_hp=90 allies=1 potion=False arrows=16 cover=True alarm=False post=gate time=day
- 方針=None 審判=shoot | hp=89 enemy=mage distance=10 enemy_count=3 enemy_hp=40 allies=2 potion=False arrows=1 cover=True alarm=False post=gate time=day
- 方針=None 審判=raise_alarm | hp=99 enemy=mage distance=12 enemy_count=3 enemy_hp=30 allies=1 potion=False arrows=17 cover=False alarm=False post=gate time=day
- 方針=None 審判=raise_alarm | hp=59 enemy=mage distance=11 enemy_count=3 enemy_hp=60 allies=3 potion=True arrows=5 cover=False alarm=False post=gate time=day
- 方針=None 審判=raise_alarm | hp=73 enemy=mage distance=4 enemy_count=4 enemy_hp=70 allies=1 potion=True arrows=6 cover=True alarm=False post=wall time=day
- 方針=None 審判=shoot | hp=75 enemy=mage distance=6 enemy_count=3 enemy_hp=20 allies=3 potion=False arrows=18 cover=False alarm=False post=gate time=day
- 方針=None 審判=raise_alarm | hp=86 enemy=mage distance=7 enemy_count=3 enemy_hp=50 allies=0 potion=False arrows=9 cover=False alarm=False post=gate time=day
- 方針=None 審判=raise_alarm | hp=99 enemy=mage distance=11 enemy_count=3 enemy_hp=60 allies=0 potion=True arrows=12 cover=True alarm=False post=gate time=day
### mid_potion_no_threat: drink vs hold split by day (6 cases, drink 4 / hold 2)
- 方針=None 審判=drink_potion | hp=33 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=True arrows=8 cover=False alarm=False post=gate time=day
- 方針=None 審判=hold_position | hp=39 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=True arrows=4 cover=False alarm=False post=corridor time=day
- 方針=None 審判=hold_position | hp=35 enemy=none distance=None enemy_count=0 enemy_hp=None allies=3 potion=True arrows=3 cover=True alarm=False post=gate time=day
- 方針=None 審判=drink_potion | hp=39 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=True arrows=0 cover=True alarm=False post=gate time=day
- 方針=None 審判=drink_potion | hp=36 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=True arrows=0 cover=True alarm=False post=gate time=day
- 方針=None 審判=drink_potion | hp=35 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=True arrows=18 cover=False alarm=False post=gate time=day
- 方針=None 審判=hold_position | hp=37 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=True arrows=5 cover=True alarm=False post=wall time=day
### mid_potion_night_drink
- 方針=drink_potion 審判=hold_position | hp=38 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=True arrows=2 cover=False alarm=False post=gate time=night
### hp_mid_no_potion_fight: fight vs retreat unclear at hp 33-39 without potion (3 cases left: retreat 2 / melee 1)
- 方針=None 審判=melee_attack | hp=37 enemy=mage distance=1 enemy_count=4 enemy_hp=60 allies=2 potion=False arrows=5 cover=False alarm=False post=gate time=day
- 方針=None 審判=retreat | hp=37 enemy=troll distance=5 enemy_count=1 enemy_hp=60 allies=1 potion=False arrows=18 cover=True alarm=True post=corridor time=night
- 方針=None 審判=retreat | hp=37 enemy=orc distance=9 enemy_count=1 enemy_hp=80 allies=2 potion=False arrows=0 cover=False alarm=False post=corridor time=night
- 方針=None 審判=raise_alarm | hp=36 enemy=orc distance=1 enemy_count=2 enemy_hp=100 allies=0 potion=False arrows=5 cover=False alarm=False post=gate time=day
- 方針=None 審判=hold_position | hp=35 enemy=troll distance=12 enemy_count=1 enemy_hp=20 allies=2 potion=False arrows=0 cover=False alarm=True post=corridor time=day
- 方針=None 審判=shoot | hp=38 enemy=mage distance=3 enemy_count=2 enemy_hp=60 allies=1 potion=False arrows=15 cover=False alarm=True post=corridor time=day
### orc_pair_no_arrows_hold
- 方針=hold_position 審判=raise_alarm | hp=88 enemy=orc distance=4 enemy_count=2 enemy_hp=40 allies=0 potion=False arrows=0 cover=True alarm=False post=gate time=day
### outnumbered_night_shoot
- 方針=shoot 審判=take_cover | hp=99 enemy=goblin distance=3 enemy_count=5 enemy_hp=60 allies=0 potion=True arrows=12 cover=True alarm=True post=gate time=night
### mid_hp_pair_retreat
- 方針=retreat 審判=shoot | hp=36 enemy=goblin distance=11 enemy_count=2 enemy_hp=20 allies=0 potion=False arrows=7 cover=False alarm=False post=gate time=day
### orc_pair_night_alone_alarm
- 方針=raise_alarm 審判=shoot | hp=99 enemy=orc distance=3 enemy_count=2 enemy_hp=20 allies=0 potion=True arrows=11 cover=False alarm=False post=corridor time=night
### orc_pair_night: shoot vs alarm split with allies (4 cases, alarm 2 / shoot 2)
- 方針=None 審判=raise_alarm | hp=61 enemy=orc distance=6 enemy_count=2 enemy_hp=40 allies=1 potion=False arrows=9 cover=False alarm=False post=gate time=night
- 方針=None 審判=shoot | hp=85 enemy=orc distance=12 enemy_count=2 enemy_hp=80 allies=1 potion=True arrows=6 cover=False alarm=False post=gate time=night
- 方針=None 審判=shoot | hp=62 enemy=orc distance=5 enemy_count=2 enemy_hp=30 allies=1 potion=False arrows=3 cover=True alarm=False post=gate time=night
- 方針=None 審判=raise_alarm | hp=40 enemy=orc distance=8 enemy_count=2 enemy_hp=90 allies=1 potion=True arrows=5 cover=False alarm=False post=wall time=night
### troll_no_arrows: cover vs hold unclear (1 case, take_cover)
- 方針=None 審判=take_cover | hp=42 enemy=troll distance=4 enemy_count=2 enemy_hp=60 allies=1 potion=False arrows=0 cover=True alarm=True post=gate time=day
- 方針=None 審判=hold_position | hp=87 enemy=troll distance=9 enemy_count=4 enemy_hp=80 allies=3 potion=False arrows=0 cover=True alarm=True post=gate time=day
- 方針=None 審判=take_cover | hp=84 enemy=troll distance=4 enemy_count=1 enemy_hp=80 allies=2 potion=True arrows=0 cover=True alarm=True post=wall time=night
- 方針=None 審判=take_cover | hp=82 enemy=troll distance=4 enemy_count=2 enemy_hp=60 allies=3 potion=False arrows=0 cover=True alarm=True post=gate time=night
### outnumbered_adjacent_alarm_silent: alarm vs melee split (3 cases, alarm 2 / melee 1)
- 方針=None 審判=raise_alarm | hp=74 enemy=mage distance=1 enemy_count=5 enemy_hp=30 allies=0 potion=True arrows=0 cover=False alarm=False post=gate time=day
- 方針=None 審判=melee_attack | hp=58 enemy=mage distance=1 enemy_count=3 enemy_hp=10 allies=0 potion=False arrows=6 cover=True alarm=False post=gate time=night
- 方針=None 審判=raise_alarm | hp=60 enemy=mage distance=1 enemy_count=3 enemy_hp=70 allies=0 potion=False arrows=2 cover=True alarm=False post=wall time=day
- 方針=None 審判=raise_alarm | hp=51 enemy=mage distance=1 enemy_count=4 enemy_hp=80 allies=1 potion=True arrows=18 cover=True alarm=False post=wall time=day

## 出力
`/home/claude/sekizui/jit/auto_runs/r1/policies/a5.py` に書く。書いたら「完了」とだけ返す。