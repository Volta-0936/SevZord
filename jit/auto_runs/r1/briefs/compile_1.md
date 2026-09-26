# 翻訳の依頼 — 走り r1、第 1 版

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

## いまの方針(a0)
```python
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

```

## 熱さの帳簿(これまでの審判のラベル 120 件を、いまの方針の枝ごとに数えた)

| 枝 | 件数 | 方針の答え | 一致 | 審判の答え |
|---|---|---|---|---|
| hp_borderline: not clearly badly hurt | 31 | None | 0/- | {'drink_potion': 9, 'retreat': 11, 'shoot': 1, 'hold_position': 7, 'raise_alarm': 2, 'melee_attack': 1} |
| no_threat | 19 | hold_position | 19/19 | {'hold_position': 19} |
| group_alarm_silent: unclear whether serious threat | 12 | None | 0/- | {'raise_alarm': 10, 'shoot': 1, 'melee_attack': 1} |
| ranged_no_arrows: no rule for distant enemy without arrows | 10 | None | 0/- | {'hold_position': 10} |
| mage_alarm_silent: kill-fast vs alarm unclear | 9 | None | 0/- | {'shoot': 2, 'raise_alarm': 5, 'melee_attack': 2} |
| outnumbered: fight vs retreat unclear | 8 | None | 0/- | {'shoot': 7, 'hold_position': 1} |
| ranged_shoot | 7 | shoot | 7/7 | {'shoot': 7} |
| night_cover: shoot vs take_cover unclear | 6 | None | 0/- | {'shoot': 6} |
| night_alarm_silent: night caution may mean alarm | 6 | None | 0/- | {'melee_attack': 3, 'shoot': 3} |
| hurt_no_threat_no_potion: retreat vs hold unclear | 3 | None | 0/- | {'retreat': 3} |
| troll_alone_ranged: shoot vs cover vs retreat unclear | 2 | None | 0/- | {'retreat': 2} |
| adjacent_melee | 2 | melee_attack | 2/2 | {'melee_attack': 2} |
| troll_adjacent_alarm_silent: alarm vs retreat unclear | 1 | None | 0/- | {'raise_alarm': 1} |
| hurt_vs_alarm: badly hurt while serious threat and alarm silent | 1 | None | 0/- | {'drink_potion': 1} |
| alarm_troll | 1 | raise_alarm | 1/1 | {'raise_alarm': 1} |
| troll_alone_retreat | 1 | retreat | 1/1 | {'retreat': 1} |
| badly_hurt_potion | 1 | drink_potion | 1/1 | {'drink_potion': 1} |

## 食い違いと棄権の例(全部)
### hp_borderline: not clearly badly hurt
- 方針=None 審判=drink_potion | hp=28 enemy=goblin distance=9 enemy_count=1 enemy_hp=20 allies=0 potion=True arrows=0 cover=False alarm=False post=gate time=day
- 方針=None 審判=retreat | hp=23 enemy=orc distance=6 enemy_count=2 enemy_hp=40 allies=2 potion=False arrows=0 cover=False alarm=False post=corridor time=day
- 方針=None 審判=retreat | hp=29 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=1 cover=True alarm=False post=gate time=day
- 方針=None 審判=drink_potion | hp=28 enemy=mage distance=10 enemy_count=2 enemy_hp=80 allies=2 potion=True arrows=10 cover=False alarm=False post=wall time=night
- 方針=None 審判=shoot | hp=35 enemy=orc distance=3 enemy_count=1 enemy_hp=50 allies=1 potion=False arrows=17 cover=False alarm=True post=gate time=day
- 方針=None 審判=retreat | hp=23 enemy=troll distance=1 enemy_count=3 enemy_hp=10 allies=0 potion=False arrows=14 cover=True alarm=False post=corridor time=day
- 方針=None 審判=retreat | hp=25 enemy=goblin distance=3 enemy_count=3 enemy_hp=100 allies=0 potion=False arrows=0 cover=True alarm=True post=gate time=day
- 方針=None 審判=hold_position | hp=35 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=12 cover=False alarm=False post=gate time=night
- 方針=None 審判=raise_alarm | hp=34 enemy=orc distance=1 enemy_count=3 enemy_hp=10 allies=0 potion=False arrows=20 cover=False alarm=False post=wall time=day
- 方針=None 審判=drink_potion | hp=26 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=True arrows=2 cover=True alarm=True post=wall time=day
- 方針=None 審判=hold_position | hp=38 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=True arrows=2 cover=False alarm=False post=gate time=night
- 方針=None 審判=retreat | hp=23 enemy=troll distance=4 enemy_count=1 enemy_hp=60 allies=0 potion=False arrows=0 cover=False alarm=False post=wall time=day
- 方針=None 審判=drink_potion | hp=26 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=True arrows=0 cover=True alarm=False post=wall time=night
- 方針=None 審判=retreat | hp=30 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=0 cover=False alarm=False post=wall time=day
- 方針=None 審判=drink_potion | hp=28 enemy=orc distance=3 enemy_count=1 enemy_hp=30 allies=0 potion=True arrows=1 cover=True alarm=True post=gate time=day
- 方針=None 審判=drink_potion | hp=30 enemy=goblin distance=11 enemy_count=2 enemy_hp=90 allies=1 potion=True arrows=1 cover=False alarm=False post=wall time=night
- 方針=None 審判=drink_potion | hp=23 enemy=orc distance=11 enemy_count=3 enemy_hp=70 allies=3 potion=True arrows=1 cover=False alarm=False post=corridor time=day
- 方針=None 審判=hold_position | hp=36 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=8 cover=False alarm=False post=gate time=night
- 方針=None 審判=retreat | hp=24 enemy=orc distance=5 enemy_count=2 enemy_hp=70 allies=1 potion=False arrows=6 cover=False alarm=True post=gate time=night
- 方針=None 審判=retreat | hp=23 enemy=goblin distance=12 enemy_count=1 enemy_hp=70 allies=1 potion=False arrows=0 cover=False alarm=False post=corridor time=day
- 方針=None 審判=drink_potion | hp=35 enemy=orc distance=5 enemy_count=4 enemy_hp=80 allies=1 potion=True arrows=16 cover=False alarm=True post=corridor time=day
- 方針=None 審判=hold_position | hp=39 enemy=none distance=None enemy_count=0 enemy_hp=None allies=3 potion=False arrows=8 cover=False alarm=False post=wall time=day
- 方針=None 審判=hold_position | hp=36 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=16 cover=False alarm=False post=wall time=day
- 方針=None 審判=raise_alarm | hp=37 enemy=goblin distance=7 enemy_count=4 enemy_hp=100 allies=0 potion=False arrows=2 cover=False alarm=False post=gate time=day
- 方針=None 審判=melee_attack | hp=37 enemy=mage distance=1 enemy_count=4 enemy_hp=60 allies=2 potion=False arrows=5 cover=False alarm=False post=gate time=day
- 方針=None 審判=retreat | hp=30 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=0 cover=False alarm=False post=gate time=night
- 方針=None 審判=retreat | hp=21 enemy=goblin distance=5 enemy_count=2 enemy_hp=50 allies=0 potion=False arrows=0 cover=False alarm=True post=wall time=night
- 方針=None 審判=retreat | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=True alarm=False post=gate time=night
- 方針=None 審判=drink_potion | hp=22 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=True arrows=12 cover=False alarm=False post=gate time=night
- 方針=None 審判=hold_position | hp=37 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=18 cover=True alarm=False post=wall time=day
- 方針=None 審判=hold_position | hp=35 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=16 cover=False alarm=False post=gate time=night
### group_alarm_silent: unclear whether serious threat
- 方針=None 審判=raise_alarm | hp=88 enemy=orc distance=4 enemy_count=2 enemy_hp=40 allies=0 potion=False arrows=0 cover=True alarm=False post=gate time=day
- 方針=None 審判=raise_alarm | hp=86 enemy=goblin distance=3 enemy_count=4 enemy_hp=70 allies=3 potion=False arrows=20 cover=False alarm=False post=gate time=night
- 方針=None 審判=raise_alarm | hp=75 enemy=goblin distance=11 enemy_count=4 enemy_hp=20 allies=0 potion=False arrows=10 cover=False alarm=False post=corridor time=night
- 方針=None 審判=raise_alarm | hp=47 enemy=orc distance=3 enemy_count=5 enemy_hp=100 allies=2 potion=False arrows=18 cover=True alarm=False post=wall time=night
- 方針=None 審判=shoot | hp=95 enemy=orc distance=4 enemy_count=2 enemy_hp=50 allies=3 potion=True arrows=4 cover=False alarm=False post=corridor time=day
- 方針=None 審判=raise_alarm | hp=85 enemy=goblin distance=1 enemy_count=3 enemy_hp=90 allies=1 potion=False arrows=0 cover=True alarm=False post=gate time=night
- 方針=None 審判=raise_alarm | hp=84 enemy=orc distance=4 enemy_count=3 enemy_hp=50 allies=0 potion=False arrows=7 cover=True alarm=False post=gate time=day
- 方針=None 審判=melee_attack | hp=91 enemy=orc distance=1 enemy_count=2 enemy_hp=60 allies=2 potion=True arrows=0 cover=False alarm=False post=gate time=night
- 方針=None 審判=raise_alarm | hp=89 enemy=goblin distance=4 enemy_count=4 enemy_hp=90 allies=0 potion=False arrows=0 cover=False alarm=False post=gate time=night
- 方針=None 審判=raise_alarm | hp=61 enemy=orc distance=6 enemy_count=2 enemy_hp=40 allies=1 potion=False arrows=9 cover=False alarm=False post=gate time=night
- 方針=None 審判=raise_alarm | hp=41 enemy=goblin distance=2 enemy_count=4 enemy_hp=90 allies=0 potion=False arrows=8 cover=False alarm=False post=gate time=day
- 方針=None 審判=raise_alarm | hp=83 enemy=orc distance=6 enemy_count=4 enemy_hp=20 allies=1 potion=False arrows=0 cover=False alarm=False post=gate time=day
### ranged_no_arrows: no rule for distant enemy without arrows
- 方針=None 審判=hold_position | hp=86 enemy=goblin distance=7 enemy_count=1 enemy_hp=60 allies=3 potion=True arrows=0 cover=True alarm=False post=corridor time=day
- 方針=None 審判=hold_position | hp=83 enemy=goblin distance=3 enemy_count=1 enemy_hp=80 allies=0 potion=False arrows=0 cover=False alarm=True post=corridor time=night
- 方針=None 審判=hold_position | hp=92 enemy=orc distance=6 enemy_count=1 enemy_hp=30 allies=0 potion=False arrows=0 cover=False alarm=False post=gate time=day
- 方針=None 審判=hold_position | hp=72 enemy=goblin distance=8 enemy_count=1 enemy_hp=10 allies=0 potion=False arrows=0 cover=False alarm=False post=gate time=day
- 方針=None 審判=hold_position | hp=80 enemy=mage distance=3 enemy_count=1 enemy_hp=50 allies=2 potion=True arrows=0 cover=False alarm=True post=gate time=day
- 方針=None 審判=hold_position | hp=79 enemy=goblin distance=2 enemy_count=1 enemy_hp=20 allies=2 potion=False arrows=0 cover=False alarm=True post=corridor time=day
- 方針=None 審判=hold_position | hp=71 enemy=goblin distance=3 enemy_count=1 enemy_hp=20 allies=1 potion=True arrows=0 cover=False alarm=False post=wall time=day
- 方針=None 審判=hold_position | hp=47 enemy=orc distance=2 enemy_count=3 enemy_hp=50 allies=2 potion=False arrows=0 cover=False alarm=True post=gate time=day
- 方針=None 審判=hold_position | hp=48 enemy=goblin distance=2 enemy_count=2 enemy_hp=100 allies=2 potion=False arrows=0 cover=False alarm=True post=gate time=day
- 方針=None 審判=hold_position | hp=91 enemy=orc distance=6 enemy_count=1 enemy_hp=90 allies=3 potion=True arrows=0 cover=True alarm=True post=corridor time=day
### mage_alarm_silent: kill-fast vs alarm unclear
- 方針=None 審判=shoot | hp=84 enemy=mage distance=6 enemy_count=1 enemy_hp=40 allies=0 potion=True arrows=11 cover=True alarm=False post=gate time=day
- 方針=None 審判=raise_alarm | hp=81 enemy=mage distance=7 enemy_count=1 enemy_hp=50 allies=1 potion=False arrows=0 cover=True alarm=False post=gate time=day
- 方針=None 審判=raise_alarm | hp=83 enemy=mage distance=4 enemy_count=4 enemy_hp=10 allies=2 potion=False arrows=0 cover=True alarm=False post=corridor time=day
- 方針=None 審判=raise_alarm | hp=92 enemy=mage distance=12 enemy_count=1 enemy_hp=40 allies=1 potion=True arrows=0 cover=False alarm=False post=wall time=night
- 方針=None 審判=shoot | hp=91 enemy=mage distance=12 enemy_count=1 enemy_hp=20 allies=1 potion=False arrows=2 cover=False alarm=False post=wall time=day
- 方針=None 審判=raise_alarm | hp=80 enemy=mage distance=3 enemy_count=3 enemy_hp=100 allies=1 potion=False arrows=1 cover=True alarm=False post=gate time=night
- 方針=None 審判=melee_attack | hp=56 enemy=mage distance=1 enemy_count=2 enemy_hp=10 allies=0 potion=False arrows=4 cover=False alarm=False post=corridor time=day
- 方針=None 審判=melee_attack | hp=46 enemy=mage distance=1 enemy_count=2 enemy_hp=10 allies=0 potion=False arrows=6 cover=True alarm=False post=gate time=day
- 方針=None 審判=raise_alarm | hp=90 enemy=mage distance=5 enemy_count=1 enemy_hp=50 allies=0 potion=False arrows=0 cover=False alarm=False post=wall time=night
### outnumbered: fight vs retreat unclear
- 方針=None 審判=shoot | hp=100 enemy=mage distance=2 enemy_count=5 enemy_hp=60 allies=2 potion=True arrows=20 cover=True alarm=True post=corridor time=day
- 方針=None 審判=shoot | hp=85 enemy=goblin distance=6 enemy_count=4 enemy_hp=70 allies=0 potion=False arrows=18 cover=True alarm=True post=gate time=day
- 方針=None 審判=shoot | hp=82 enemy=orc distance=4 enemy_count=4 enemy_hp=90 allies=0 potion=False arrows=11 cover=True alarm=True post=wall time=night
- 方針=None 審判=shoot | hp=84 enemy=goblin distance=6 enemy_count=4 enemy_hp=20 allies=1 potion=False arrows=9 cover=False alarm=True post=wall time=day
- 方針=None 審判=shoot | hp=61 enemy=orc distance=8 enemy_count=3 enemy_hp=60 allies=0 potion=False arrows=12 cover=False alarm=True post=corridor time=day
- 方針=None 審判=hold_position | hp=57 enemy=goblin distance=2 enemy_count=3 enemy_hp=100 allies=0 potion=True arrows=0 cover=True alarm=True post=corridor time=day
- 方針=None 審判=shoot | hp=100 enemy=orc distance=12 enemy_count=4 enemy_hp=10 allies=0 potion=True arrows=1 cover=False alarm=True post=gate time=night
- 方針=None 審判=shoot | hp=48 enemy=mage distance=9 enemy_count=3 enemy_hp=40 allies=0 potion=True arrows=4 cover=True alarm=True post=corridor time=night
### night_cover: shoot vs take_cover unclear
- 方針=None 審判=shoot | hp=89 enemy=orc distance=4 enemy_count=1 enemy_hp=40 allies=1 potion=True arrows=3 cover=True alarm=True post=wall time=night
- 方針=None 審判=shoot | hp=52 enemy=goblin distance=3 enemy_count=1 enemy_hp=60 allies=0 potion=True arrows=17 cover=True alarm=True post=corridor time=night
- 方針=None 審判=shoot | hp=49 enemy=troll distance=11 enemy_count=2 enemy_hp=90 allies=3 potion=False arrows=17 cover=True alarm=True post=wall time=night
- 方針=None 審判=shoot | hp=94 enemy=goblin distance=9 enemy_count=1 enemy_hp=100 allies=2 potion=True arrows=13 cover=True alarm=True post=gate time=night
- 方針=None 審判=shoot | hp=45 enemy=goblin distance=7 enemy_count=1 enemy_hp=100 allies=0 potion=False arrows=17 cover=True alarm=True post=wall time=night
- 方針=None 審判=shoot | hp=76 enemy=orc distance=5 enemy_count=1 enemy_hp=30 allies=3 potion=False arrows=19 cover=True alarm=True post=corridor time=night
### night_alarm_silent: night caution may mean alarm
- 方針=None 審判=melee_attack | hp=57 enemy=goblin distance=1 enemy_count=1 enemy_hp=80 allies=3 potion=False arrows=11 cover=False alarm=False post=corridor time=night
- 方針=None 審判=shoot | hp=70 enemy=goblin distance=2 enemy_count=1 enemy_hp=50 allies=2 potion=False arrows=12 cover=False alarm=False post=gate time=night
- 方針=None 審判=melee_attack | hp=80 enemy=orc distance=1 enemy_count=1 enemy_hp=60 allies=1 potion=False arrows=3 cover=True alarm=False post=gate time=night
- 方針=None 審判=melee_attack | hp=40 enemy=goblin distance=1 enemy_count=2 enemy_hp=70 allies=3 potion=True arrows=13 cover=True alarm=False post=wall time=night
- 方針=None 審判=shoot | hp=55 enemy=goblin distance=4 enemy_count=1 enemy_hp=70 allies=1 potion=False arrows=10 cover=True alarm=False post=wall time=night
- 方針=None 審判=shoot | hp=93 enemy=orc distance=11 enemy_count=1 enemy_hp=50 allies=2 potion=True arrows=12 cover=True alarm=False post=wall time=night
### hurt_no_threat_no_potion: retreat vs hold unclear
- 方針=None 審判=retreat | hp=20 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=20 cover=True alarm=False post=wall time=night
- 方針=None 審判=retreat | hp=19 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=0 cover=False alarm=True post=gate time=night
- 方針=None 審判=retreat | hp=6 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=6 cover=True alarm=False post=wall time=day
### troll_alone_ranged: shoot vs cover vs retreat unclear
- 方針=None 審判=retreat | hp=99 enemy=troll distance=3 enemy_count=4 enemy_hp=30 allies=0 potion=False arrows=6 cover=True alarm=True post=gate time=night
- 方針=None 審判=retreat | hp=53 enemy=troll distance=3 enemy_count=4 enemy_hp=10 allies=0 potion=True arrows=2 cover=False alarm=True post=wall time=night
### troll_adjacent_alarm_silent: alarm vs retreat unclear
- 方針=None 審判=raise_alarm | hp=68 enemy=troll distance=1 enemy_count=1 enemy_hp=40 allies=1 potion=True arrows=19 cover=False alarm=False post=corridor time=day
### hurt_vs_alarm: badly hurt while serious threat and alarm silent
- 方針=None 審判=drink_potion | hp=17 enemy=troll distance=12 enemy_count=4 enemy_hp=10 allies=0 potion=True arrows=1 cover=True alarm=False post=wall time=day

## 出力
`/home/claude/sekizui/jit/auto_runs/r1/policies/a1.py` に書く。書いたら「完了」とだけ返す。