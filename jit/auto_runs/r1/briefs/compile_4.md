# 翻訳の依頼 — 走り r1、第 4 版

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

## いまの方針(a3)
```python
"""城の番兵NPC 方針 — 走り r1、第 3 版 (a3)

この版で変えたこと(根拠は熱さの帳簿 281 件と、その食い違い・棄権の例の一覧)
------------------------------------------------------------------------------
1. mid_hurt_potion(hp 33〜39・回復薬あり)を敵の有無で分けた。
   - 13 件で drink_potion 10 / hold_position 3(77%)で、80% に届かなくなった。
   - 食い違いの hold 3 件(hp38 夜、hp39 昼、hp35 昼)はすべて敵なし。
     a2 の時点の内訳(敵あり 5/5 drink、敵なし drink 5 / hold 1)に、
     敵なし hold が 2 件加わった(drink は 10 のまま)。
   - 敵あり → 飲む (mid_hurt_potion のまま)。5/5 が drink。
   - 敵なし → 棄権 (mid_potion_no_threat)。8 件で drink 5 / hold 3(63%)。
     hold の hp は 35・38・39 で、drink の最高 hp38 と重なり、線は引けない。
2. hp 33〜39・回復薬なしの番人 hp_mid_no_potion_fight から、
   ゴブリン/オーク 1 体・昼・戦える時(隣接、または離れて矢あり)を外し、
   通常の戦いに戻した (mid_hp_single_fight)。
   - 9 件のうち敵 1 体(トロル以外)は 3 件で、3/3 が通常の戦いの答え
     (離れて矢あり → shoot 2、隣接 → melee_attack 1、退く 0)。
     警報あり 2 / なし 1、味方 0〜2。射るか近接かは指示文どおり距離で決める。
   - 3 件はすべて昼。この帯の夜の例 2 件(オーク 2 体、トロル)はどちらも retreat
     なので、夜の 1 体は例 0 件として棄権に残した。離れて矢なしも例 0 件で棄権。
   - 残りの 6 件は割れたまま棄権: retreat 4 / shoot 1 / melee 1。
     敵 2 体・離れて(ゴブリン 2・オーク 2)は retreat 3 / shoot 1(75%)で 80% に届かない。
     トロル 1 件(retreat)、魔術師 4 体隣接 1 件(melee)は 1 件ずつ。
3. 多勢に無勢・隣接の番人 outnumbered_adjacent を警報で分けた。
   - 7 件で melee_attack 6 / raise_alarm 1。
   - 警報既鳴(トロル以外)→ 近接 (outnumbered_adjacent_melee)。6/6 が melee
     (ゴブリン 4・オーク 1・魔術師 1、夜 4 / 昼 2、味方 0〜1、hp45〜93)。
     「隣接していれば近接で戦う」とも合う。
   - 警報未鳴動の魔術師 → 棄権 (outnumbered_adjacent_alarm_silent)。
     1 件(魔術師 5 体隣接・味方 0 → raise_alarm)。
   - トロルの多勢は例 0 件なので棄権 (outnumbered_adjacent)。
4. 警報未鳴動のオーク 2 体・隣接 → 近接 (orc_pair_adjacent_melee)。
   番人 orc_pair_adjacent を外した。
   - 3/3 が melee_attack(夜 2 / 昼 1、味方 0・2・3、矢 0・4・20)。
   - hp 33〜39・回復薬なしは 2. の番人が先に受ける。
5. 警報未鳴動のオーク 2 体・離れて・矢なし → 持ち場を守る (orc_pair_no_arrows_hold)。
   番人 orc_pair_no_arrows を外した。
   - 5 件で hold_position 4 / raise_alarm 1(80%)。
   - raise_alarm の 1 件(hp88 味方0 昼 遮蔽あり)は、hold の hp83 味方0 昼 遮蔽あり
     と条件で分けられないので、例 1 件の線は引かない。
   - no_arrows_hold(19/20)と同じ答えで、指示文の読み方とも食い違わない。
6. 多勢に無勢・夜・遮蔽あり・離れて矢あり → 射る (outnumbered_night_shoot)。
   番人 outnumbered_night_cover を外した。
   - 5 件で shoot 4 / take_cover 1(80%)。
   - take_cover の 1 件はゴブリン 5 体、shoot は 3〜4 体。1 件で敵の数の線は引かない。
   - 「敵が離れていて矢が残っていれば弓で射る」(ranged_shoot 34/34)と同じ答え。

変えなかった所
--------------
- 「ひどく傷ついている」の線 hp <= 32、重傷は警報より先
  (badly_hurt_potion 18/18、badly_hurt_retreat 21/21)。
- no_threat 59/59、ranged_shoot 34/34、mage_ranged_shoot 13/13、adjacent_melee 10/10、
  alarm_troll 10/10、troll_alone_retreat 8/8、mage_no_arrows_alarm 4/4、
  orc_pair_day_shoot 4/4、mage_group_night_alarm 4/4、mage_adjacent_melee 4/4。
- no_arrows_hold 19/20(95%)。食い違い 1 件(ゴブリン 1 体・夜・遮蔽・味方 0 → take_cover)。
- alarm_group 19/20(95%)。食い違い 1 件(ゴブリン 3 体・離れて・矢なし・味方 0・昼 → hold)。
  どちらも 1 件なので線は引かない。

棄権のまま残した所
------------------
- mage_group_day_alarm_silent: 5 件で raise_alarm 3 / shoot 2(60%)。
  5 体は raise_alarm 2/2、3 体は shoot 2 / raise_alarm 1(67%)。どちらも足りない。
- orc_pair_night: 4 件で shoot 3 / raise_alarm 1(75%)。
- troll_no_arrows: 1 件(味方ありのトロル・離れて矢なし → take_cover 1)。
- hp_mid_no_potion_fight: 上の 2. のとおり 6 件で retreat 4 / shoot 1 / melee 1。
- mid_potion_no_threat, outnumbered_adjacent_alarm_silent, outnumbered_adjacent:
  上のとおり。

枝の名(答える枝)
------------------
no_threat, badly_hurt_potion, badly_hurt_retreat, mid_hurt_potion, alarm_troll,
alarm_group, mage_adjacent_melee, mage_no_arrows_alarm, mage_group_night_alarm,
mage_ranged_shoot, orc_pair_day_shoot, orc_pair_adjacent_melee, orc_pair_no_arrows_hold,
troll_alone_retreat, mid_hp_single_fight, outnumbered_adjacent_melee, adjacent_melee,
no_arrows_hold, outnumbered_night_shoot, ranged_shoot
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
HP_FINE_MIN = 40         # 33〜39 は中間帯。敵ありで回復薬ありなら飲む(5/5、最高 hp38)、hp42 は飲まない
ADJACENT_MAX = 1         # これ以下は隣接
GROUP_MIN = 3            # この数以上なら群れ(ゴブリン/オーク 19/20 が raise_alarm、魔術師の警報もすべて 3 体以上)
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
        "(6 cases: retreat 4 / shoot 1 / melee 1)"
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
            # 敵なし・hp33〜39・回復薬あり: drink 5 / hold 3
            return None, "mid_potion_no_threat: drink vs hold split (8 cases, drink 5 / hold 3)"
        # 「脅威が無ければ持ち場を守る」(hp33〜39・回復薬なしも hold)
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

    # --- 中間帯で回復薬あり・敵あり(警報・魔術師・群れの規則より先。5/5) ---
    if mid_hp_potion:
        return "drink_potion", "mid_hurt_potion"

    # ここから「ひどく傷ついていない」、または hp33〜39 で回復薬なし

    # --- 警報がまだ鳴っていない ---
    if not alarm:
        if enemy == "troll":
            # 「警報がまだ鳴っておらず、深刻な脅威が現れたなら警報を鳴らす」(10/10)
            return "raise_alarm", "alarm_troll"
        if enemy == "mage":
            if adjacent:
                if outnumbered:
                    return None, (
                        "outnumbered_adjacent_alarm_silent: alarm vs melee unclear "
                        "(1 case, raise_alarm)"
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
                    # 魔術師+群れ、夜 → 警報(4/4)
                    return "raise_alarm", "mage_group_night_alarm"
                # 昼: raise_alarm 3 / shoot 2
                return None, (
                    "mage_group_day_alarm_silent: shoot vs alarm split "
                    "(5 cases, alarm 3 / shoot 2)"
                )
            if mid_hp_no_potion:
                return None, mid_fight_reason
            # 魔術師 2 体まで・離れて・矢あり → 射る(13/13)
            return "shoot", "mage_ranged_shoot"
        # goblin / orc
        if enemy_count >= GROUP_MIN:
            # 3 体以上は深刻な脅威 → 警報(隣接していても。19/20)
            return "raise_alarm", "alarm_group"
        if enemy == "orc" and enemy_count >= 2:
            if mid_hp_no_potion:
                return None, mid_fight_reason
            if adjacent:
                # 「隣接していれば近接で戦う」(3/3)
                return "melee_attack", "orc_pair_adjacent_melee"
            if arrows <= 0:
                # 離れて矢なし → 持ち場(hold 4 / alarm 1、80%)
                return "hold_position", "orc_pair_no_arrows_hold"
            if time == "night":
                return None, "orc_pair_night: shoot vs alarm split (4 cases, shoot 3 / alarm 1)"
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
        # 矢が無ければ持ち場を守る(19/20)
        return "hold_position", "no_arrows_hold"

    if outnumbered and time == "night" and cover:
        # 多勢・夜・遮蔽あり: shoot 4 / take_cover 1(80%)
        return "shoot", "outnumbered_night_shoot"

    # 「敵が離れていて矢が残っていれば弓で射る」
    return "shoot", "ranged_shoot"

```

## 熱さの帳簿(これまでの審判のラベル 344 件を、いまの方針の枝ごとに数えた)

| 枝 | 件数 | 方針の答え | 一致 | 審判の答え |
|---|---|---|---|---|
| no_threat | 78 | hold_position | 76/78 | {'hold_position': 76, 'retreat': 2} |
| ranged_shoot | 44 | shoot | 43/44 | {'shoot': 43, 'take_cover': 1} |
| badly_hurt_retreat | 24 | retreat | 24/24 | {'retreat': 24} |
| no_arrows_hold | 24 | hold_position | 23/24 | {'hold_position': 23, 'take_cover': 1} |
| alarm_group | 22 | raise_alarm | 20/22 | {'raise_alarm': 20, 'hold_position': 1, 'shoot': 1} |
| badly_hurt_potion | 21 | drink_potion | 21/21 | {'drink_potion': 21} |
| mage_ranged_shoot | 15 | shoot | 15/15 | {'shoot': 15} |
| adjacent_melee | 13 | melee_attack | 13/13 | {'melee_attack': 13} |
| mid_potion_no_threat: drink vs hold split (8 cases, drink 5 / hold 3) | 12 | None | 0/- | {'hold_position': 3, 'drink_potion': 9} |
| alarm_troll | 11 | raise_alarm | 11/11 | {'raise_alarm': 11} |
| orc_pair_night: shoot vs alarm split (4 cases, shoot 3 / alarm 1) | 9 | None | 0/- | {'raise_alarm': 6, 'shoot': 3} |
| troll_alone_retreat | 8 | retreat | 8/8 | {'retreat': 8} |
| hp_mid_no_potion_fight: fight vs retreat split at hp 33-39 without potion (6 cases: retreat 4 / shoot 1 / melee 1) | 8 | None | 0/- | {'melee_attack': 1, 'retreat': 6, 'shoot': 1} |
| mid_hurt_potion | 6 | drink_potion | 6/6 | {'drink_potion': 6} |
| mage_group_day_alarm_silent: shoot vs alarm split (5 cases, alarm 3 / shoot 2) | 6 | None | 0/- | {'raise_alarm': 4, 'shoot': 2} |
| outnumbered_adjacent_melee | 6 | melee_attack | 6/6 | {'melee_attack': 6} |
| orc_pair_no_arrows_hold | 5 | hold_position | 4/5 | {'raise_alarm': 1, 'hold_position': 4} |
| outnumbered_night_shoot | 5 | shoot | 4/5 | {'shoot': 4, 'take_cover': 1} |
| mage_group_night_alarm | 5 | raise_alarm | 5/5 | {'raise_alarm': 5} |
| mage_no_arrows_alarm | 4 | raise_alarm | 4/4 | {'raise_alarm': 4} |
| orc_pair_day_shoot | 4 | shoot | 4/4 | {'shoot': 4} |
| mage_adjacent_melee | 4 | melee_attack | 4/4 | {'melee_attack': 4} |
| mid_hp_single_fight | 3 | shoot | 3/3 | {'shoot': 2, 'melee_attack': 1} |
| orc_pair_adjacent_melee | 3 | melee_attack | 3/3 | {'melee_attack': 3} |
| outnumbered_adjacent_alarm_silent: alarm vs melee unclear (1 case, raise_alarm) | 3 | None | 0/- | {'raise_alarm': 2, 'melee_attack': 1} |
| troll_no_arrows: cover vs hold unclear (1 case, take_cover) | 1 | None | 0/- | {'take_cover': 1} |

## 食い違いと棄権の例(全部)
### no_threat
- 方針=hold_position 審判=retreat | hp=33 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=7 cover=True alarm=False post=corridor time=day
- 方針=hold_position 審判=retreat | hp=39 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=8 cover=False alarm=False post=gate time=night
### ranged_shoot
- 方針=shoot 審判=take_cover | hp=71 enemy=orc distance=5 enemy_count=2 enemy_hp=90 allies=0 potion=True arrows=13 cover=True alarm=True post=gate time=night
### no_arrows_hold
- 方針=hold_position 審判=take_cover | hp=91 enemy=goblin distance=4 enemy_count=1 enemy_hp=30 allies=0 potion=True arrows=0 cover=True alarm=False post=corridor time=night
### alarm_group
- 方針=raise_alarm 審判=hold_position | hp=79 enemy=goblin distance=6 enemy_count=3 enemy_hp=10 allies=0 potion=True arrows=0 cover=False alarm=False post=gate time=day
- 方針=raise_alarm 審判=shoot | hp=75 enemy=goblin distance=10 enemy_count=3 enemy_hp=50 allies=1 potion=False arrows=18 cover=True alarm=False post=gate time=day
### mid_potion_no_threat: drink vs hold split (8 cases, drink 5 / hold 3)
- 方針=None 審判=hold_position | hp=38 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=True arrows=2 cover=False alarm=False post=gate time=night
- 方針=None 審判=drink_potion | hp=33 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=True arrows=8 cover=False alarm=False post=gate time=day
- 方針=None 審判=drink_potion | hp=38 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=True arrows=0 cover=False alarm=False post=gate time=night
- 方針=None 審判=drink_potion | hp=35 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=True arrows=12 cover=False alarm=False post=gate time=night
- 方針=None 審判=drink_potion | hp=37 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=True arrows=0 cover=True alarm=False post=wall time=night
- 方針=None 審判=drink_potion | hp=35 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=True arrows=6 cover=False alarm=False post=gate time=night
- 方針=None 審判=hold_position | hp=39 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=True arrows=4 cover=False alarm=False post=corridor time=day
- 方針=None 審判=hold_position | hp=35 enemy=none distance=None enemy_count=0 enemy_hp=None allies=3 potion=True arrows=3 cover=True alarm=False post=gate time=day
- 方針=None 審判=drink_potion | hp=39 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=True arrows=0 cover=False alarm=False post=corridor time=night
- 方針=None 審判=drink_potion | hp=39 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=True arrows=0 cover=True alarm=False post=gate time=day
- 方針=None 審判=drink_potion | hp=36 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=True arrows=0 cover=True alarm=False post=gate time=day
- 方針=None 審判=drink_potion | hp=35 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=True arrows=18 cover=False alarm=False post=gate time=day
### orc_pair_night: shoot vs alarm split (4 cases, shoot 3 / alarm 1)
- 方針=None 審判=raise_alarm | hp=61 enemy=orc distance=6 enemy_count=2 enemy_hp=40 allies=1 potion=False arrows=9 cover=False alarm=False post=gate time=night
- 方針=None 審判=shoot | hp=99 enemy=orc distance=3 enemy_count=2 enemy_hp=20 allies=0 potion=True arrows=11 cover=False alarm=False post=corridor time=night
- 方針=None 審判=shoot | hp=85 enemy=orc distance=12 enemy_count=2 enemy_hp=80 allies=1 potion=True arrows=6 cover=False alarm=False post=gate time=night
- 方針=None 審判=shoot | hp=62 enemy=orc distance=5 enemy_count=2 enemy_hp=30 allies=1 potion=False arrows=3 cover=True alarm=False post=gate time=night
- 方針=None 審判=raise_alarm | hp=87 enemy=orc distance=7 enemy_count=2 enemy_hp=30 allies=0 potion=True arrows=11 cover=False alarm=False post=wall time=night
- 方針=None 審判=raise_alarm | hp=40 enemy=orc distance=8 enemy_count=2 enemy_hp=90 allies=1 potion=True arrows=5 cover=False alarm=False post=wall time=night
- 方針=None 審判=raise_alarm | hp=79 enemy=orc distance=7 enemy_count=2 enemy_hp=90 allies=0 potion=True arrows=5 cover=True alarm=False post=gate time=night
- 方針=None 審判=raise_alarm | hp=91 enemy=orc distance=12 enemy_count=2 enemy_hp=40 allies=0 potion=False arrows=19 cover=False alarm=False post=corridor time=night
- 方針=None 審判=raise_alarm | hp=62 enemy=orc distance=4 enemy_count=2 enemy_hp=50 allies=0 potion=False arrows=19 cover=True alarm=False post=gate time=night
### hp_mid_no_potion_fight: fight vs retreat split at hp 33-39 without potion (6 cases: retreat 4 / shoot 1 / melee 1)
- 方針=None 審判=melee_attack | hp=37 enemy=mage distance=1 enemy_count=4 enemy_hp=60 allies=2 potion=False arrows=5 cover=False alarm=False post=gate time=day
- 方針=None 審判=retreat | hp=37 enemy=orc distance=9 enemy_count=2 enemy_hp=90 allies=1 potion=False arrows=5 cover=False alarm=False post=wall time=day
- 方針=None 審判=retreat | hp=34 enemy=goblin distance=7 enemy_count=2 enemy_hp=60 allies=3 potion=False arrows=17 cover=False alarm=False post=corridor time=day
- 方針=None 審判=retreat | hp=33 enemy=orc distance=12 enemy_count=2 enemy_hp=70 allies=2 potion=False arrows=8 cover=False alarm=False post=gate time=night
- 方針=None 審判=shoot | hp=36 enemy=goblin distance=11 enemy_count=2 enemy_hp=20 allies=0 potion=False arrows=7 cover=False alarm=False post=gate time=day
- 方針=None 審判=retreat | hp=37 enemy=troll distance=5 enemy_count=1 enemy_hp=60 allies=1 potion=False arrows=18 cover=True alarm=True post=corridor time=night
- 方針=None 審判=retreat | hp=33 enemy=goblin distance=7 enemy_count=2 enemy_hp=60 allies=1 potion=False arrows=4 cover=False alarm=False post=gate time=day
- 方針=None 審判=retreat | hp=37 enemy=orc distance=9 enemy_count=1 enemy_hp=80 allies=2 potion=False arrows=0 cover=False alarm=False post=corridor time=night
### mage_group_day_alarm_silent: shoot vs alarm split (5 cases, alarm 3 / shoot 2)
- 方針=None 審判=raise_alarm | hp=64 enemy=mage distance=7 enemy_count=5 enemy_hp=40 allies=1 potion=False arrows=9 cover=True alarm=False post=corridor time=day
- 方針=None 審判=shoot | hp=80 enemy=mage distance=7 enemy_count=3 enemy_hp=60 allies=1 potion=False arrows=5 cover=False alarm=False post=gate time=day
- 方針=None 審判=raise_alarm | hp=60 enemy=mage distance=12 enemy_count=5 enemy_hp=90 allies=1 potion=False arrows=16 cover=True alarm=False post=gate time=day
- 方針=None 審判=shoot | hp=89 enemy=mage distance=10 enemy_count=3 enemy_hp=40 allies=2 potion=False arrows=1 cover=True alarm=False post=gate time=day
- 方針=None 審判=raise_alarm | hp=99 enemy=mage distance=12 enemy_count=3 enemy_hp=30 allies=1 potion=False arrows=17 cover=False alarm=False post=gate time=day
- 方針=None 審判=raise_alarm | hp=59 enemy=mage distance=11 enemy_count=3 enemy_hp=60 allies=3 potion=True arrows=5 cover=False alarm=False post=gate time=day
### orc_pair_no_arrows_hold
- 方針=hold_position 審判=raise_alarm | hp=88 enemy=orc distance=4 enemy_count=2 enemy_hp=40 allies=0 potion=False arrows=0 cover=True alarm=False post=gate time=day
### outnumbered_night_shoot
- 方針=shoot 審判=take_cover | hp=99 enemy=goblin distance=3 enemy_count=5 enemy_hp=60 allies=0 potion=True arrows=12 cover=True alarm=True post=gate time=night
### outnumbered_adjacent_alarm_silent: alarm vs melee unclear (1 case, raise_alarm)
- 方針=None 審判=raise_alarm | hp=74 enemy=mage distance=1 enemy_count=5 enemy_hp=30 allies=0 potion=True arrows=0 cover=False alarm=False post=gate time=day
- 方針=None 審判=melee_attack | hp=58 enemy=mage distance=1 enemy_count=3 enemy_hp=10 allies=0 potion=False arrows=6 cover=True alarm=False post=gate time=night
- 方針=None 審判=raise_alarm | hp=60 enemy=mage distance=1 enemy_count=3 enemy_hp=70 allies=0 potion=False arrows=2 cover=True alarm=False post=wall time=day
### troll_no_arrows: cover vs hold unclear (1 case, take_cover)
- 方針=None 審判=take_cover | hp=42 enemy=troll distance=4 enemy_count=2 enemy_hp=60 allies=1 potion=False arrows=0 cover=True alarm=True post=gate time=day

## 出力
`/home/claude/sekizui/jit/auto_runs/r1/policies/a4.py` に書く。書いたら「完了」とだけ返す。