# 翻訳の依頼 — 走り r1、第 3 版

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

## いまの方針(a2)
```python
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

```

## 熱さの帳簿(これまでの審判のラベル 281 件を、いまの方針の枝ごとに数えた)

| 枝 | 件数 | 方針の答え | 一致 | 審判の答え |
|---|---|---|---|---|
| no_threat | 59 | hold_position | 59/59 | {'hold_position': 59} |
| ranged_shoot | 34 | shoot | 34/34 | {'shoot': 34} |
| badly_hurt_retreat | 21 | retreat | 21/21 | {'retreat': 21} |
| no_arrows_hold | 20 | hold_position | 19/20 | {'hold_position': 19, 'take_cover': 1} |
| alarm_group | 20 | raise_alarm | 19/20 | {'raise_alarm': 19, 'hold_position': 1} |
| badly_hurt_potion | 18 | drink_potion | 18/18 | {'drink_potion': 18} |
| mage_ranged_shoot | 13 | shoot | 13/13 | {'shoot': 13} |
| mid_hurt_potion | 13 | drink_potion | 10/13 | {'hold_position': 3, 'drink_potion': 10} |
| adjacent_melee | 10 | melee_attack | 10/10 | {'melee_attack': 10} |
| alarm_troll | 10 | raise_alarm | 10/10 | {'raise_alarm': 10} |
| hp_mid_no_potion_fight: fight vs retreat split at hp 33-39 without potion (shoot 1 / melee 1 / retreat 2) | 9 | None | 0/- | {'shoot': 3, 'melee_attack': 2, 'retreat': 4} |
| troll_alone_retreat | 8 | retreat | 8/8 | {'retreat': 8} |
| outnumbered_adjacent: fight vs retreat unclear (1 case, melee) | 7 | None | 0/- | {'melee_attack': 6, 'raise_alarm': 1} |
| orc_pair_no_arrows: hold vs alarm split (4 cases, hold 3 / alarm 1) | 5 | None | 0/- | {'raise_alarm': 1, 'hold_position': 4} |
| outnumbered_night_cover: shoot vs take_cover split (3 cases, 2/1) | 5 | None | 0/- | {'shoot': 4, 'take_cover': 1} |
| mage_group_day_alarm_silent: shoot vs alarm split (4 cases, 2/2) | 5 | None | 0/- | {'raise_alarm': 3, 'shoot': 2} |
| mage_no_arrows_alarm | 4 | raise_alarm | 4/4 | {'raise_alarm': 4} |
| orc_pair_day_shoot | 4 | shoot | 4/4 | {'shoot': 4} |
| mage_group_night_alarm | 4 | raise_alarm | 4/4 | {'raise_alarm': 4} |
| mage_adjacent_melee | 4 | melee_attack | 4/4 | {'melee_attack': 4} |
| orc_pair_night: shoot vs alarm split (2 cases, 1/1) | 4 | None | 0/- | {'raise_alarm': 1, 'shoot': 3} |
| orc_pair_adjacent: alarm vs melee unclear (1 case, melee) | 3 | None | 0/- | {'melee_attack': 3} |
| troll_no_arrows: cover vs hold unclear (1 case, take_cover) | 1 | None | 0/- | {'take_cover': 1} |

## 食い違いと棄権の例(全部)
### no_arrows_hold
- 方針=hold_position 審判=take_cover | hp=91 enemy=goblin distance=4 enemy_count=1 enemy_hp=30 allies=0 potion=True arrows=0 cover=True alarm=False post=corridor time=night
### alarm_group
- 方針=raise_alarm 審判=hold_position | hp=79 enemy=goblin distance=6 enemy_count=3 enemy_hp=10 allies=0 potion=True arrows=0 cover=False alarm=False post=gate time=day
### mid_hurt_potion
- 方針=drink_potion 審判=hold_position | hp=38 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=True arrows=2 cover=False alarm=False post=gate time=night
- 方針=drink_potion 審判=hold_position | hp=39 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=True arrows=4 cover=False alarm=False post=corridor time=day
- 方針=drink_potion 審判=hold_position | hp=35 enemy=none distance=None enemy_count=0 enemy_hp=None allies=3 potion=True arrows=3 cover=True alarm=False post=gate time=day
### hp_mid_no_potion_fight: fight vs retreat split at hp 33-39 without potion (shoot 1 / melee 1 / retreat 2)
- 方針=None 審判=shoot | hp=35 enemy=orc distance=3 enemy_count=1 enemy_hp=50 allies=1 potion=False arrows=17 cover=False alarm=True post=gate time=day
- 方針=None 審判=melee_attack | hp=37 enemy=mage distance=1 enemy_count=4 enemy_hp=60 allies=2 potion=False arrows=5 cover=False alarm=False post=gate time=day
- 方針=None 審判=retreat | hp=37 enemy=orc distance=9 enemy_count=2 enemy_hp=90 allies=1 potion=False arrows=5 cover=False alarm=False post=wall time=day
- 方針=None 審判=retreat | hp=34 enemy=goblin distance=7 enemy_count=2 enemy_hp=60 allies=3 potion=False arrows=17 cover=False alarm=False post=corridor time=day
- 方針=None 審判=shoot | hp=36 enemy=orc distance=2 enemy_count=1 enemy_hp=30 allies=0 potion=False arrows=9 cover=True alarm=True post=gate time=day
- 方針=None 審判=retreat | hp=33 enemy=orc distance=12 enemy_count=2 enemy_hp=70 allies=2 potion=False arrows=8 cover=False alarm=False post=gate time=night
- 方針=None 審判=shoot | hp=36 enemy=goblin distance=11 enemy_count=2 enemy_hp=20 allies=0 potion=False arrows=7 cover=False alarm=False post=gate time=day
- 方針=None 審判=melee_attack | hp=35 enemy=goblin distance=1 enemy_count=1 enemy_hp=100 allies=2 potion=False arrows=8 cover=False alarm=False post=corridor time=day
- 方針=None 審判=retreat | hp=37 enemy=troll distance=5 enemy_count=1 enemy_hp=60 allies=1 potion=False arrows=18 cover=True alarm=True post=corridor time=night
### outnumbered_adjacent: fight vs retreat unclear (1 case, melee)
- 方針=None 審判=melee_attack | hp=93 enemy=mage distance=1 enemy_count=4 enemy_hp=80 allies=0 potion=False arrows=3 cover=True alarm=True post=wall time=night
- 方針=None 審判=melee_attack | hp=87 enemy=goblin distance=1 enemy_count=5 enemy_hp=20 allies=0 potion=False arrows=0 cover=False alarm=True post=corridor time=night
- 方針=None 審判=melee_attack | hp=65 enemy=goblin distance=1 enemy_count=4 enemy_hp=10 allies=0 potion=False arrows=0 cover=True alarm=True post=gate time=night
- 方針=None 審判=melee_attack | hp=45 enemy=orc distance=1 enemy_count=5 enemy_hp=90 allies=1 potion=True arrows=7 cover=True alarm=True post=wall time=day
- 方針=None 審判=raise_alarm | hp=74 enemy=mage distance=1 enemy_count=5 enemy_hp=30 allies=0 potion=True arrows=0 cover=False alarm=False post=gate time=day
- 方針=None 審判=melee_attack | hp=87 enemy=goblin distance=1 enemy_count=4 enemy_hp=90 allies=0 potion=False arrows=7 cover=True alarm=True post=corridor time=night
- 方針=None 審判=melee_attack | hp=93 enemy=goblin distance=1 enemy_count=4 enemy_hp=100 allies=1 potion=False arrows=13 cover=False alarm=True post=wall time=day
### orc_pair_no_arrows: hold vs alarm split (4 cases, hold 3 / alarm 1)
- 方針=None 審判=raise_alarm | hp=88 enemy=orc distance=4 enemy_count=2 enemy_hp=40 allies=0 potion=False arrows=0 cover=True alarm=False post=gate time=day
- 方針=None 審判=hold_position | hp=83 enemy=orc distance=7 enemy_count=2 enemy_hp=70 allies=0 potion=True arrows=0 cover=True alarm=False post=wall time=day
- 方針=None 審判=hold_position | hp=56 enemy=orc distance=4 enemy_count=2 enemy_hp=10 allies=2 potion=True arrows=0 cover=True alarm=False post=wall time=day
- 方針=None 審判=hold_position | hp=75 enemy=orc distance=2 enemy_count=2 enemy_hp=30 allies=1 potion=False arrows=0 cover=False alarm=False post=wall time=night
- 方針=None 審判=hold_position | hp=64 enemy=orc distance=9 enemy_count=2 enemy_hp=70 allies=1 potion=True arrows=0 cover=True alarm=False post=gate time=day
### outnumbered_night_cover: shoot vs take_cover split (3 cases, 2/1)
- 方針=None 審判=shoot | hp=82 enemy=orc distance=4 enemy_count=4 enemy_hp=90 allies=0 potion=False arrows=11 cover=True alarm=True post=wall time=night
- 方針=None 審判=shoot | hp=48 enemy=mage distance=9 enemy_count=3 enemy_hp=40 allies=0 potion=True arrows=4 cover=True alarm=True post=corridor time=night
- 方針=None 審判=take_cover | hp=99 enemy=goblin distance=3 enemy_count=5 enemy_hp=60 allies=0 potion=True arrows=12 cover=True alarm=True post=gate time=night
- 方針=None 審判=shoot | hp=91 enemy=mage distance=7 enemy_count=3 enemy_hp=20 allies=0 potion=True arrows=19 cover=True alarm=True post=gate time=night
- 方針=None 審判=shoot | hp=83 enemy=orc distance=2 enemy_count=3 enemy_hp=40 allies=0 potion=False arrows=19 cover=True alarm=True post=wall time=night
### mage_group_day_alarm_silent: shoot vs alarm split (4 cases, 2/2)
- 方針=None 審判=raise_alarm | hp=64 enemy=mage distance=7 enemy_count=5 enemy_hp=40 allies=1 potion=False arrows=9 cover=True alarm=False post=corridor time=day
- 方針=None 審判=shoot | hp=80 enemy=mage distance=7 enemy_count=3 enemy_hp=60 allies=1 potion=False arrows=5 cover=False alarm=False post=gate time=day
- 方針=None 審判=raise_alarm | hp=60 enemy=mage distance=12 enemy_count=5 enemy_hp=90 allies=1 potion=False arrows=16 cover=True alarm=False post=gate time=day
- 方針=None 審判=shoot | hp=89 enemy=mage distance=10 enemy_count=3 enemy_hp=40 allies=2 potion=False arrows=1 cover=True alarm=False post=gate time=day
- 方針=None 審判=raise_alarm | hp=99 enemy=mage distance=12 enemy_count=3 enemy_hp=30 allies=1 potion=False arrows=17 cover=False alarm=False post=gate time=day
### orc_pair_night: shoot vs alarm split (2 cases, 1/1)
- 方針=None 審判=raise_alarm | hp=61 enemy=orc distance=6 enemy_count=2 enemy_hp=40 allies=1 potion=False arrows=9 cover=False alarm=False post=gate time=night
- 方針=None 審判=shoot | hp=99 enemy=orc distance=3 enemy_count=2 enemy_hp=20 allies=0 potion=True arrows=11 cover=False alarm=False post=corridor time=night
- 方針=None 審判=shoot | hp=85 enemy=orc distance=12 enemy_count=2 enemy_hp=80 allies=1 potion=True arrows=6 cover=False alarm=False post=gate time=night
- 方針=None 審判=shoot | hp=62 enemy=orc distance=5 enemy_count=2 enemy_hp=30 allies=1 potion=False arrows=3 cover=True alarm=False post=gate time=night
### orc_pair_adjacent: alarm vs melee unclear (1 case, melee)
- 方針=None 審判=melee_attack | hp=91 enemy=orc distance=1 enemy_count=2 enemy_hp=60 allies=2 potion=True arrows=0 cover=False alarm=False post=gate time=night
- 方針=None 審判=melee_attack | hp=94 enemy=orc distance=1 enemy_count=2 enemy_hp=20 allies=0 potion=False arrows=20 cover=True alarm=False post=gate time=day
- 方針=None 審判=melee_attack | hp=95 enemy=orc distance=1 enemy_count=2 enemy_hp=70 allies=3 potion=False arrows=4 cover=True alarm=False post=gate time=night
### troll_no_arrows: cover vs hold unclear (1 case, take_cover)
- 方針=None 審判=take_cover | hp=42 enemy=troll distance=4 enemy_count=2 enemy_hp=60 allies=1 potion=False arrows=0 cover=True alarm=True post=gate time=day

## 出力
`/home/claude/sekizui/jit/auto_runs/r1/policies/a3.py` に書く。書いたら「完了」とだけ返す。