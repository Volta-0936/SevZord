# 翻訳の依頼 — 走り r1、第 2 版

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

## いまの方針(a1)
```python
"""城の番兵NPC 方針 — 走り r1、第 1 版 (a1)

この版で変えたこと(根拠は帳簿 120 件。件数は a0 の枝ごとの表と例の一覧から数えた)
------------------------------------------------------------------------------------
1. 「ひどく傷ついている」の線を hp <= 20 から hp <= 32 へ上げた。
   - hp 21〜30 の例 19 件がすべて「回復薬があれば飲み、なければ退く」だった
     (敵なし 7 件: drink 3 / retreat 4、敵あり 12 件: drink 5 / retreat 7)。
   - 回復薬なしで「傷ついていない」扱いだった最も低い例は hp34(raise_alarm)。
     線は最も高い「傷ついている」例 hp30 と hp34 の間、32 に置いた。
2. hp 33〜39 で回復薬なし → ひどく傷ついていない、として通常の規則へ進める。
   - hp34〜39・回復薬なしの 10 件で退く答えは 0 件
     (敵なし hold 6、敵あり shoot 1 / raise_alarm 2 / melee 1)。
3. hp 33〜39 で回復薬あり → 棄権 (hp_mid_potion)。
   - 2 件で割れる(hp35 敵あり → drink、hp38 敵なし → hold)。
4. ひどく傷ついていれば、警報の規則より先に回復・退却の規則を当てる(hurt_vs_alarm の番人を外した)。
   - 重傷 + 深刻な脅威 + 警報未鳴動 の 4 件がすべて drink 2 / retreat 2(回復薬の有無どおり)。
   - 上の 1. の 19 件でも、重傷時は敵・警報・夜に関係なく必ず回復・退却だった。
5. 重傷で脅威なし・回復薬なし → 退く(badly_hurt_retreat、番人 hurt_no_threat_no_potion を外した)。
   - hp <= 20 の 3 件 + hp28〜30 の 4 件、計 7/7 が retreat。
6. 警報未鳴動のゴブリン/オーク 3 体以上 → 警報を鳴らす (alarm_group)。隣接していない時だけ。
   - 3 体以上・非隣接 8/8 が raise_alarm(group_alarm_silent 7 件 + hp37 の 1 件)。
   - 隣接は 2 件(どちらも raise_alarm)しか無いので棄権 (group_adjacent_alarm_silent)。
7. 警報未鳴動のオーク 2 体 → 棄権のまま (orc_pair_alarm_silent)。
   - 4 件で raise_alarm 2 / shoot 1 / melee 1 と割れる。
8. 警報未鳴動の魔術師を三つに分けた。
   - 隣接 → 近接 (mage_adjacent_melee)。3/3 が melee_attack。
   - 離れていて矢なし → 警報 (mage_no_arrows_alarm)。4/4 が raise_alarm。
   - 離れていて矢あり → 棄権 (mage_ranged_alarm_silent)。3 件で shoot 2 / raise_alarm 1 と割れる。
9. 夜でも、警報未鳴動の小さな脅威(ゴブリン 2 体まで・オーク 1 体)には通常の戦闘の規則を当てる
   (night_alarm_silent の番人を外した)。6/6 が通常の答え(隣接 melee 3、離れて矢あり shoot 3)。
10. 夜に遮蔽があっても射る(night_cover の番人を外した)。
    - night_cover 6/6 + outnumbered のうち夜・遮蔽ありの 2 件、計 8/8 が shoot。
11. 多勢に無勢の番人は隣接している時だけに絞った (outnumbered_adjacent、例 0 件なので棄権)。
    - outnumbered の 8 件はすべて離れた敵で、射撃の規則どおり(矢あり shoot 7/7、矢なし hold 1/1)。
12. 敵が離れていて矢が無い → 持ち場を守る (no_arrows_hold)。
    - ranged_no_arrows 10/10 + outnumbered の 1 件、計 11/11 が hold_position
      (ゴブリン・オーク・魔術師、昼夜、警報の有無を問わず)。
    - トロルの例は 0 件なので棄権 (troll_no_arrows)。

棄権のまま残した所
------------------
- troll_alone_ranged: 2 件(retreat 2)。3 件に届かない。
- troll_adjacent_alarm_silent: 1 件(raise_alarm 1)。
- group_adjacent_alarm_silent: 2 件(raise_alarm 2)。
- mage_ranged_alarm_silent: 3 件で割れる。
- orc_pair_alarm_silent: 4 件で割れる。
- hp_mid_potion: 2 件で割れる。
- outnumbered_adjacent, troll_no_arrows: 0 件。

枝の名(答える枝)
------------------
no_threat, badly_hurt_potion, badly_hurt_retreat, alarm_troll, alarm_group,
mage_adjacent_melee, mage_no_arrows_alarm, troll_alone_retreat, adjacent_melee,
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
HP_BADLY_HURT_MAX = 32   # これ以下は「ひどく傷ついている」(例: hp21〜30 の 19 件すべて重傷扱い、hp34 は非該当)
HP_FINE_MIN = 40         # 回復薬ありの時、これ以上は「ひどく傷ついていない」(33〜39 は 2 件で割れる)
ADJACENT_MAX = 1         # これ以下は隣接
GROUP_MIN = 3            # ゴブリン/オークがこれ以上なら深刻な脅威(非隣接 8/8 が raise_alarm)
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
    mid_hp_with_potion = HP_BADLY_HURT_MAX < hp < HP_FINE_MIN and potion

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
        if mid_hp_with_potion:
            return None, "hp_mid_potion: drink vs carry on unclear (2 cases, split)"
        # 「脅威が無ければ持ち場を守る」
        return "hold_position", "no_threat"

    # --- 敵がいる ---
    if enemy_count is not None and enemy_count <= 0:
        return None, "inconsistent_state: enemy present but enemy_count 0"
    d = _num(distance)
    if d is None:
        return None, "inconsistent_state: enemy present but distance missing"
    adjacent = d <= ADJACENT_MAX
    outnumbered = enemy_count - (allies + 1) >= OUTNUMBERED_MARGIN

    # --- ひどく傷ついている(警報の規則より先。19 + 4 件すべてこの答え) ---
    if badly_hurt:
        if potion:
            return "drink_potion", "badly_hurt_potion"
        return "retreat", "badly_hurt_retreat"

    if mid_hp_with_potion:
        return None, "hp_mid_potion: drink vs carry on unclear (2 cases, split)"

    # ここから「ひどく傷ついていない」

    # --- 警報がまだ鳴っていない ---
    if not alarm:
        if enemy == "troll":
            if adjacent:
                # 例 1 件(raise_alarm)
                return None, "troll_adjacent_alarm_silent: alarm vs retreat unclear (1 case)"
            # 「警報がまだ鳴っておらず、深刻な脅威が現れたなら警報を鳴らす」
            return "raise_alarm", "alarm_troll"
        if enemy == "mage":
            if adjacent:
                if outnumbered:
                    return None, "outnumbered_adjacent: fight vs retreat unclear (0 cases)"
                # 「隣接していれば近接で戦う」+「魔術師は早く仕留める」(3/3)
                return "melee_attack", "mage_adjacent_melee"
            if arrows <= 0:
                # 射てない魔術師には警報(4/4)
                return "raise_alarm", "mage_no_arrows_alarm"
            # shoot 2 / raise_alarm 1
            return None, "mage_ranged_alarm_silent: shoot vs alarm split (3 cases)"
        # goblin / orc
        if enemy_count >= GROUP_MIN:
            if adjacent:
                # 例 2 件(raise_alarm 2)
                return None, "group_adjacent_alarm_silent: alarm vs melee unclear (2 cases)"
            # 3 体以上は深刻な脅威 → 警報(非隣接 8/8)
            return "raise_alarm", "alarm_group"
        if enemy == "orc" and enemy_count >= 2:
            # raise_alarm 2 / shoot 1 / melee 1
            return None, "orc_pair_alarm_silent: alarm vs fight split (4 cases)"
        # ゴブリン 2 体まで・オーク 1 体は深刻ではない。夜でも通常の戦闘へ(6/6)

    # --- トロル(警報は鳴っている)、味方なし ---
    if enemy == "troll" and allies <= 0:
        if adjacent:
            # 「トロルは一人で相手にするには強すぎる」+「無駄死にはしない」
            return "retreat", "troll_alone_retreat"
        # retreat 2 件のみ
        return None, "troll_alone_ranged: shoot vs cover vs retreat unclear (2 cases)"

    # --- 隣接 ---
    if adjacent:
        if outnumbered:
            return None, "outnumbered_adjacent: fight vs retreat unclear (0 cases)"
        # 「隣接していれば近接で戦う」
        return "melee_attack", "adjacent_melee"

    # --- 離れている ---
    if arrows <= 0:
        if enemy == "troll":
            return None, "troll_no_arrows: no cases for distant troll without arrows"
        # 矢が無ければ持ち場を守る(11/11)
        return "hold_position", "no_arrows_hold"

    # 「敵が離れていて矢が残っていれば弓で射る」(夜・遮蔽・多勢でも 8/8, 7/7)
    return "shoot", "ranged_shoot"

```

## 熱さの帳簿(これまでの審判のラベル 214 件を、いまの方針の枝ごとに数えた)

| 枝 | 件数 | 方針の答え | 一致 | 審判の答え |
|---|---|---|---|---|
| no_threat | 42 | hold_position | 42/42 | {'hold_position': 42} |
| ranged_shoot | 29 | shoot | 27/29 | {'shoot': 27, 'take_cover': 1, 'retreat': 1} |
| mage_ranged_alarm_silent: shoot vs alarm split (3 cases) | 21 | None | 0/- | {'shoot': 15, 'raise_alarm': 6} |
| no_arrows_hold | 19 | hold_position | 19/19 | {'hold_position': 19} |
| badly_hurt_retreat | 16 | retreat | 16/16 | {'retreat': 16} |
| badly_hurt_potion | 15 | drink_potion | 15/15 | {'drink_potion': 15} |
| orc_pair_alarm_silent: alarm vs fight split (4 cases) | 12 | None | 0/- | {'raise_alarm': 2, 'shoot': 5, 'melee_attack': 1, 'retreat': 1, 'hold_position': 3} |
| hp_mid_potion: drink vs carry on unclear (2 cases, split) | 11 | None | 0/- | {'hold_position': 1, 'drink_potion': 10} |
| alarm_group | 10 | raise_alarm | 10/10 | {'raise_alarm': 10} |
| adjacent_melee | 8 | melee_attack | 8/8 | {'melee_attack': 8} |
| group_adjacent_alarm_silent: alarm vs melee unclear (2 cases) | 6 | None | 0/- | {'raise_alarm': 6} |
| troll_alone_ranged: shoot vs cover vs retreat unclear (2 cases) | 6 | None | 0/- | {'retreat': 6} |
| troll_adjacent_alarm_silent: alarm vs retreat unclear (1 case) | 5 | None | 0/- | {'raise_alarm': 5} |
| mage_adjacent_melee | 5 | melee_attack | 5/5 | {'melee_attack': 5} |
| mage_no_arrows_alarm | 4 | raise_alarm | 4/4 | {'raise_alarm': 4} |
| alarm_troll | 2 | raise_alarm | 2/2 | {'raise_alarm': 2} |
| troll_alone_retreat | 1 | retreat | 1/1 | {'retreat': 1} |
| troll_no_arrows: no cases for distant troll without arrows | 1 | None | 0/- | {'take_cover': 1} |
| outnumbered_adjacent: fight vs retreat unclear (0 cases) | 1 | None | 0/- | {'melee_attack': 1} |

## 食い違いと棄権の例(全部)
### ranged_shoot
- 方針=shoot 審判=take_cover | hp=99 enemy=goblin distance=3 enemy_count=5 enemy_hp=60 allies=0 potion=True arrows=12 cover=True alarm=True post=gate time=night
- 方針=shoot 審判=retreat | hp=34 enemy=goblin distance=7 enemy_count=2 enemy_hp=60 allies=3 potion=False arrows=17 cover=False alarm=False post=corridor time=day
### mage_ranged_alarm_silent: shoot vs alarm split (3 cases)
- 方針=None 審判=shoot | hp=84 enemy=mage distance=6 enemy_count=1 enemy_hp=40 allies=0 potion=True arrows=11 cover=True alarm=False post=gate time=day
- 方針=None 審判=shoot | hp=91 enemy=mage distance=12 enemy_count=1 enemy_hp=20 allies=1 potion=False arrows=2 cover=False alarm=False post=wall time=day
- 方針=None 審判=raise_alarm | hp=80 enemy=mage distance=3 enemy_count=3 enemy_hp=100 allies=1 potion=False arrows=1 cover=True alarm=False post=gate time=night
- 方針=None 審判=raise_alarm | hp=97 enemy=mage distance=2 enemy_count=5 enemy_hp=60 allies=0 potion=False arrows=17 cover=True alarm=False post=wall time=night
- 方針=None 審判=raise_alarm | hp=64 enemy=mage distance=7 enemy_count=5 enemy_hp=40 allies=1 potion=False arrows=9 cover=True alarm=False post=corridor time=day
- 方針=None 審判=shoot | hp=89 enemy=mage distance=3 enemy_count=2 enemy_hp=90 allies=1 potion=False arrows=3 cover=False alarm=False post=corridor time=night
- 方針=None 審判=shoot | hp=89 enemy=mage distance=8 enemy_count=1 enemy_hp=80 allies=2 potion=True arrows=9 cover=True alarm=False post=gate time=day
- 方針=None 審判=raise_alarm | hp=58 enemy=mage distance=8 enemy_count=3 enemy_hp=70 allies=0 potion=True arrows=13 cover=False alarm=False post=corridor time=night
- 方針=None 審判=shoot | hp=80 enemy=mage distance=7 enemy_count=3 enemy_hp=60 allies=1 potion=False arrows=5 cover=False alarm=False post=gate time=day
- 方針=None 審判=raise_alarm | hp=91 enemy=mage distance=8 enemy_count=3 enemy_hp=100 allies=1 potion=True arrows=2 cover=True alarm=False post=wall time=night
- 方針=None 審判=shoot | hp=76 enemy=mage distance=2 enemy_count=1 enemy_hp=70 allies=0 potion=False arrows=10 cover=False alarm=False post=gate time=day
- 方針=None 審判=shoot | hp=68 enemy=mage distance=2 enemy_count=1 enemy_hp=80 allies=0 potion=True arrows=4 cover=False alarm=False post=wall time=day
- 方針=None 審判=shoot | hp=95 enemy=mage distance=10 enemy_count=2 enemy_hp=30 allies=3 potion=False arrows=8 cover=False alarm=False post=wall time=night
- 方針=None 審判=shoot | hp=91 enemy=mage distance=6 enemy_count=1 enemy_hp=20 allies=3 potion=False arrows=2 cover=True alarm=False post=wall time=day
- 方針=None 審判=shoot | hp=93 enemy=mage distance=7 enemy_count=1 enemy_hp=10 allies=0 potion=False arrows=10 cover=True alarm=False post=gate time=night
- 方針=None 審判=shoot | hp=69 enemy=mage distance=6 enemy_count=2 enemy_hp=30 allies=1 potion=True arrows=20 cover=False alarm=False post=corridor time=day
- 方針=None 審判=raise_alarm | hp=60 enemy=mage distance=12 enemy_count=5 enemy_hp=90 allies=1 potion=False arrows=16 cover=True alarm=False post=gate time=day
- 方針=None 審判=shoot | hp=89 enemy=mage distance=10 enemy_count=3 enemy_hp=40 allies=2 potion=False arrows=1 cover=True alarm=False post=gate time=day
- 方針=None 審判=shoot | hp=50 enemy=mage distance=12 enemy_count=2 enemy_hp=90 allies=1 potion=True arrows=15 cover=False alarm=False post=gate time=day
- 方針=None 審判=shoot | hp=91 enemy=mage distance=3 enemy_count=2 enemy_hp=60 allies=2 potion=False arrows=9 cover=False alarm=False post=gate time=day
- 方針=None 審判=shoot | hp=76 enemy=mage distance=6 enemy_count=1 enemy_hp=70 allies=0 potion=True arrows=7 cover=False alarm=False post=gate time=night
### orc_pair_alarm_silent: alarm vs fight split (4 cases)
- 方針=None 審判=raise_alarm | hp=88 enemy=orc distance=4 enemy_count=2 enemy_hp=40 allies=0 potion=False arrows=0 cover=True alarm=False post=gate time=day
- 方針=None 審判=shoot | hp=95 enemy=orc distance=4 enemy_count=2 enemy_hp=50 allies=3 potion=True arrows=4 cover=False alarm=False post=corridor time=day
- 方針=None 審判=melee_attack | hp=91 enemy=orc distance=1 enemy_count=2 enemy_hp=60 allies=2 potion=True arrows=0 cover=False alarm=False post=gate time=night
- 方針=None 審判=raise_alarm | hp=61 enemy=orc distance=6 enemy_count=2 enemy_hp=40 allies=1 potion=False arrows=9 cover=False alarm=False post=gate time=night
- 方針=None 審判=shoot | hp=98 enemy=orc distance=4 enemy_count=2 enemy_hp=30 allies=0 potion=False arrows=8 cover=False alarm=False post=corridor time=day
- 方針=None 審判=retreat | hp=37 enemy=orc distance=9 enemy_count=2 enemy_hp=90 allies=1 potion=False arrows=5 cover=False alarm=False post=wall time=day
- 方針=None 審判=hold_position | hp=83 enemy=orc distance=7 enemy_count=2 enemy_hp=70 allies=0 potion=True arrows=0 cover=True alarm=False post=wall time=day
- 方針=None 審判=shoot | hp=82 enemy=orc distance=12 enemy_count=2 enemy_hp=90 allies=3 potion=True arrows=3 cover=False alarm=False post=gate time=day
- 方針=None 審判=shoot | hp=99 enemy=orc distance=3 enemy_count=2 enemy_hp=20 allies=0 potion=True arrows=11 cover=False alarm=False post=corridor time=night
- 方針=None 審判=hold_position | hp=56 enemy=orc distance=4 enemy_count=2 enemy_hp=10 allies=2 potion=True arrows=0 cover=True alarm=False post=wall time=day
- 方針=None 審判=shoot | hp=82 enemy=orc distance=4 enemy_count=2 enemy_hp=40 allies=2 potion=False arrows=19 cover=True alarm=False post=corridor time=day
- 方針=None 審判=hold_position | hp=75 enemy=orc distance=2 enemy_count=2 enemy_hp=30 allies=1 potion=False arrows=0 cover=False alarm=False post=wall time=night
### hp_mid_potion: drink vs carry on unclear (2 cases, split)
- 方針=None 審判=hold_position | hp=38 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=True arrows=2 cover=False alarm=False post=gate time=night
- 方針=None 審判=drink_potion | hp=35 enemy=orc distance=5 enemy_count=4 enemy_hp=80 allies=1 potion=True arrows=16 cover=False alarm=True post=corridor time=day
- 方針=None 審判=drink_potion | hp=36 enemy=goblin distance=3 enemy_count=2 enemy_hp=10 allies=3 potion=True arrows=4 cover=False alarm=False post=gate time=night
- 方針=None 審判=drink_potion | hp=33 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=True arrows=8 cover=False alarm=False post=gate time=day
- 方針=None 審判=drink_potion | hp=38 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=True arrows=0 cover=False alarm=False post=gate time=night
- 方針=None 審判=drink_potion | hp=35 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=True arrows=12 cover=False alarm=False post=gate time=night
- 方針=None 審判=drink_potion | hp=37 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=True arrows=0 cover=True alarm=False post=wall time=night
- 方針=None 審判=drink_potion | hp=37 enemy=orc distance=1 enemy_count=4 enemy_hp=30 allies=1 potion=True arrows=7 cover=False alarm=False post=wall time=night
- 方針=None 審判=drink_potion | hp=35 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=True arrows=6 cover=False alarm=False post=gate time=night
- 方針=None 審判=drink_potion | hp=37 enemy=mage distance=1 enemy_count=2 enemy_hp=100 allies=1 potion=True arrows=0 cover=True alarm=False post=gate time=day
- 方針=None 審判=drink_potion | hp=37 enemy=orc distance=4 enemy_count=3 enemy_hp=30 allies=3 potion=True arrows=2 cover=True alarm=False post=corridor time=day
### group_adjacent_alarm_silent: alarm vs melee unclear (2 cases)
- 方針=None 審判=raise_alarm | hp=34 enemy=orc distance=1 enemy_count=3 enemy_hp=10 allies=0 potion=False arrows=20 cover=False alarm=False post=wall time=day
- 方針=None 審判=raise_alarm | hp=85 enemy=goblin distance=1 enemy_count=3 enemy_hp=90 allies=1 potion=False arrows=0 cover=True alarm=False post=gate time=night
- 方針=None 審判=raise_alarm | hp=60 enemy=orc distance=1 enemy_count=4 enemy_hp=20 allies=2 potion=True arrows=8 cover=True alarm=False post=wall time=night
- 方針=None 審判=raise_alarm | hp=42 enemy=goblin distance=1 enemy_count=4 enemy_hp=40 allies=1 potion=True arrows=16 cover=True alarm=False post=gate time=day
- 方針=None 審判=raise_alarm | hp=79 enemy=goblin distance=1 enemy_count=4 enemy_hp=80 allies=3 potion=False arrows=9 cover=False alarm=False post=gate time=night
- 方針=None 審判=raise_alarm | hp=66 enemy=orc distance=1 enemy_count=5 enemy_hp=40 allies=2 potion=False arrows=20 cover=True alarm=False post=gate time=night
### troll_alone_ranged: shoot vs cover vs retreat unclear (2 cases)
- 方針=None 審判=retreat | hp=99 enemy=troll distance=3 enemy_count=4 enemy_hp=30 allies=0 potion=False arrows=6 cover=True alarm=True post=gate time=night
- 方針=None 審判=retreat | hp=53 enemy=troll distance=3 enemy_count=4 enemy_hp=10 allies=0 potion=True arrows=2 cover=False alarm=True post=wall time=night
- 方針=None 審判=retreat | hp=100 enemy=troll distance=4 enemy_count=2 enemy_hp=90 allies=0 potion=False arrows=4 cover=True alarm=True post=gate time=day
- 方針=None 審判=retreat | hp=94 enemy=troll distance=10 enemy_count=1 enemy_hp=100 allies=0 potion=False arrows=0 cover=True alarm=True post=gate time=night
- 方針=None 審判=retreat | hp=72 enemy=troll distance=6 enemy_count=2 enemy_hp=50 allies=0 potion=True arrows=3 cover=True alarm=True post=gate time=night
- 方針=None 審判=retreat | hp=75 enemy=troll distance=12 enemy_count=3 enemy_hp=30 allies=0 potion=True arrows=16 cover=False alarm=True post=wall time=night
### troll_adjacent_alarm_silent: alarm vs retreat unclear (1 case)
- 方針=None 審判=raise_alarm | hp=68 enemy=troll distance=1 enemy_count=1 enemy_hp=40 allies=1 potion=True arrows=19 cover=False alarm=False post=corridor time=day
- 方針=None 審判=raise_alarm | hp=57 enemy=troll distance=1 enemy_count=3 enemy_hp=60 allies=0 potion=False arrows=20 cover=True alarm=False post=gate time=day
- 方針=None 審判=raise_alarm | hp=100 enemy=troll distance=1 enemy_count=1 enemy_hp=60 allies=2 potion=True arrows=5 cover=True alarm=False post=wall time=night
- 方針=None 審判=raise_alarm | hp=41 enemy=troll distance=1 enemy_count=1 enemy_hp=20 allies=1 potion=False arrows=12 cover=False alarm=False post=corridor time=day
- 方針=None 審判=raise_alarm | hp=72 enemy=troll distance=1 enemy_count=4 enemy_hp=90 allies=2 potion=True arrows=5 cover=False alarm=False post=gate time=night
### troll_no_arrows: no cases for distant troll without arrows
- 方針=None 審判=take_cover | hp=42 enemy=troll distance=4 enemy_count=2 enemy_hp=60 allies=1 potion=False arrows=0 cover=True alarm=True post=gate time=day
### outnumbered_adjacent: fight vs retreat unclear (0 cases)
- 方針=None 審判=melee_attack | hp=93 enemy=mage distance=1 enemy_count=4 enemy_hp=80 allies=0 potion=False arrows=3 cover=True alarm=True post=wall time=night

## 出力
`/home/claude/sekizui/jit/auto_runs/r1/policies/a2.py` に書く。書いたら「完了」とだけ返す。