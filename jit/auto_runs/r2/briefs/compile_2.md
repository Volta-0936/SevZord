# 翻訳の依頼 — 走り r2、第 2 版

あなたは翻訳役だ。審判(別の LLM)が指示文に従って下す判断を、番人付きの Python の方針に翻訳する。
目的は、審判の会話の多数と同じ答えを出すこと。会話が割れている所や、証拠が足りない所は棄権して審判に回す。
読んでよいのはこの依頼書だけ。ほかのファイル(ほかの方針、保留のデータ、別の走り)は開かないこと。

## 審判が受け取っている指示文(行の記号 L0〜L7、追補 A1.. は根拠の欄で使われる)
```
L0 城の番兵NPCの、このターンの行動を一つ選ぶ。番兵は忠実だが、無駄死にはしない。門を守りつつ生き延びること。
L1 ひどく傷ついているなら、回復薬があれば飲み、なければ退く。
L2 敵が離れていて矢が残っていれば弓で射る。隣接していれば近接で戦う。
L3 トロルは一人で相手にするには強すぎる。
L4 魔術師は早く仕留めるべきだ。
L5 警報がまだ鳴っておらず、深刻な脅威が現れたなら警報を鳴らす。
L6 夜は用心深く。
L7 脅威が無ければ持ち場を守る。

追補(審判の会話の多数から足した一文。指示文と同じ重みで使う):
A1 hp が 31 以上あれば、回復薬が無くとも、敵が 9 マス以上離れ矢が残っている間は退かずに弓で射る。

行動: melee_attack(近接攻撃), shoot(弓で射る), retreat(退く), drink_potion(回復薬を飲む), take_cover(遮蔽に隠れる), raise_alarm(警報を鳴らす), hold_position(持ち場を守る)
状態の項目: hp(番兵の体力 0-100), enemy(最も近い敵の種類: none/goblin/orc/mage/troll), distance(その敵までのマス数、敵がいなければ null), enemy_count(見えている敵の数), enemy_hp(最も近い敵の体力 %), allies(近くの味方の数), potion(回復薬を持っているか), arrows(矢の残り), cover(近くに遮蔽物があるか), alarm(警報が既に鳴っているか), post(持ち場: gate/wall/corridor), time(day/night)
```

## 書く物の約束
- ファイルは Python 一つ。関数 `decide(s)` を一つ定義する。`s` は状態の dict(項目は下の指示文、distance と enemy_hp は敵がいなければ None)。
- 返り値は `(行動, 枝の名)` か `(None, 棄権の理由)`。行動は次の 7 つの文字列のどれか: melee_attack, shoot, retreat, drink_potion, take_cover, raise_alarm, hold_position。
- 枝の名は、その答えを出した規則の短い英字の名前。同じ規則には同じ名前を使い続ける(帳簿は枝の名で数える)。一つの枝の名は一つの行動だけを返す。
- 標準ライブラリ以外を import しない。外部の状態を持たない。
- ファイルの冒頭の docstring に、この版で何を変えたかと、その根拠(件数と会話の本数、審判が挙げた決め手)を書く。
- 範囲の番人: 関数の最初で状態の値を確かめ、次の範囲の外や知らない値があれば `(None, "out_of_range: 項目")` を返す。
  数: hp 5〜100、distance 1〜12(敵がいなければ None)、enemy_count 0〜5、enemy_hp 10〜100(敵がいなければ None)、allies 0〜3、arrows 0〜20。
  種類: enemy は none/goblin/orc/mage/troll、post は gate/wall/corridor、time は day/night。potion・cover・alarm は真偽。
  敵の有無と distance・enemy_count・enemy_hp が食い違う状態も棄権する。門はこれを、範囲外の状態 450 件で検査する。

## 翻訳の規律(門がコードで検査する)
- 審判の答えには、根拠(指示文の行 L0〜L7、追補 A1..、または審判が自分で埋めた gap)と、決め手になった項目と、一文の理由が付いている。枝の条件は、審判が挙げた決め手から作る。例から閾値を当て推量しない。
- 証拠の単位は会話(審判への 1 回の依頼)だ。同じ会話の答えは互いに引きずられるので、件数より会話の本数を重く見る。
- 枝が新しく答えてよいのは、次のどれかの時だけ。(a) 指示文・追補をそのまま読んだ規則。(b) その状況の例が 3 件以上・会話 2 本以上あり、一致が 80% 以上。(c) 例が 1〜2 件でも、その全部が指示文の行を根拠にして(gap なし)一致している。
- 会話どうしで答えが割れている所(とくに根拠が gap の所)は、名前を付けた番人で棄権のまま残す。割れは輪が審判に訊き直し、会話の多数が揃えば追補になって戻ってくる。
- 既にある枝でも、会話 2 本以上(かつ会話の 1/3 以上)が別の答えを多数にしていれば門で落ちる。例 3 件以上で一致 80% 未満の枝も落ちる。
- 帳簿の例に過剰に合わせない。閾値は例の間に置く。

## いまの方針(b1)
```python
"""走り r2 の方針、第 1 版(b1)。

帳簿: 審判のラベル 120 件、会話 3 本(round1_s1 / s2 / s3、以下 s1 s2 s3)。
b0 の答えた枝(no_threat_hold 13、shoot_far 6、melee_adjacent 4、troll_alarm 3、
mage_shoot 2、hurt_drink 1、hurt_retreat 1)は全件一致だったので、そのまま残す。
b0 が答えた状態の行き先は、この版でも変わらない。

この版で変えたこと
 1. 「ひどく傷ついていない」の下限を hp>=50 から hp>=33 に下げた(_FINE_MIN)。
    hp_ambiguous の 36 件のうち hp>=35 の 26 件では、どの会話も L1(飲む・退く)を
    使っていない。飲む・退くの最も高い例は hp=31(s2 が飲む)。敵がいない hp 35〜49 の
    14 件(会話 3 本)はすべて hold_position。
    審判の決め手は、傷の側が hp<=30 / hp<=31、平気の側が hp>=30 / hp>=31 / hp>=39 /
    hp>=40 …。30〜31 は会話で割れる(s2 は 31 で飲む、s1 は 31 を「手負い」と言いつつ射る、
    s3 は 30 で持ち場に残る)。線は割れている例 31 と、その上の次の例 35 の間の 33 に置いた。
    hp 21〜32 は hp_ambiguous のまま棄権(10 件: 飲む 3・退く 3・持ち場 2・警報 1・射る 1)。
    傷の側の上限 hp<=20 は据え置いた。hp 21〜23 の L1 の例は、枝ごとに見ると
    hurt_drink 1 件(gap)・hurt_retreat 2 件(うち 1 件 gap)で、規律 (b)(c) に届かない。
 2. 番人 many_enemies を外した。警報済み・敵 3 以上の 8 件・会話 3 本がすべて L2 どおり
    (隣接 2 件は melee_attack、離れて矢あり 6 件は shoot)。根拠は 8 件とも L2 で gap なし。
    決め手は distance と arrows だけで、enemy_count は一度も挙がっていない。
 3. 番人 night_cover_far を外した。夜・遮蔽あり・離れた敵・矢ありの 5 件・会話 3 本が
    すべて shoot(根拠 L2、gap なし。決め手 distance>=2, arrows>=1)。L6 は遮蔽を指していない。
 4. 新しい枝 horde_alarm: 警報未・敵 4 以上(トロル以外)→ raise_alarm。
    10 件・会話 3 本・一致 10/10(オーク 5、ゴブリン 3、魔術師 2。s1 2 件、s2 5 件、s3 3 件)。
    決め手は alarm=false と enemy_count>=4 / enemy_count>=5。敵 3 は割れる
    (raise 3・melee 1・shoot 1)ので、線は 3 と 4 の間に置いた。
 5. 新しい枝 outnumbered_alarm: 警報未・敵 3・近くの味方 0 → raise_alarm。
    3 件・会話 2 本(s1 ゴブリン 1、s3 オーク 2)・一致 3/3。決め手は 3 件とも
    enemy_count>=3, allies=0, alarm=false。
 6. 警報未の単独のオークを、深刻な脅威でないとして L2 へ通した(orc_alarm_unclear から外した)。
    2 件(s3 隣接 melee_attack、s1 離れて shoot)、どちらも根拠 L2 だけ・gap なしで L2 と一致
    → 規律 (c)。決め手は distance=1 / distance>=2, arrows>=1 だけ。
    警報未のゴブリン 2 体も L2 へ通した(group_alarm_unclear から外した)。
    4 件・会話 3 本・一致 4/4(隣接 melee_attack 1、離れて shoot 3)。決め手は distance / arrows。
 7. 離れた敵・矢 0(no_arrows_far)を三つに分けた。
    no_arrows_hold(新しい枝、遮蔽なし・魔術師以外 → hold_position):
        5 件・会話 3 本・一致 5/5。決め手 arrows=0, distance>=2(s3 は cover=false も挙げる)。
    no_arrows_cover(番人、遮蔽あり): hold 4・take_cover 2 で割れる。take_cover は s1 と s2 に
        一つずつあり、決め手は cover=true, time=night / hp<=42, potion=false。
    mage_no_arrows(番人、魔術師): 1 件(melee_attack、根拠 L4+gap)で足りない。

b1 で数え直した帳簿(答える枝、件数・一致・会話)
    no_threat_hold      27  27/27  s1 s2 s3   L7  敵なし・hp>=33 → hold_position
    shoot_far           22  22/22  s1 s2 s3   L2  離れたゴブリン/オーク・矢あり → shoot
    horde_alarm         10  10/10  s1 s2 s3   L5  警報未・敵 4 以上 → raise_alarm
    melee_adjacent       9   9/9   s1 s2 s3   L2  隣接のゴブリン/オーク → melee_attack
    no_arrows_hold       5   5/5   s1 s2 s3   gap 離れた敵・矢 0・遮蔽なし → hold_position
    outnumbered_alarm    3   3/3   s1 s3      L5  警報未・敵 3・味方 0 → raise_alarm
    troll_alarm          3   3/3   2 本       L5+L3  トロル・警報未 → raise_alarm
    mage_shoot           3   3/3   3 本       L2+L4  離れた魔術師(警報済み)・矢あり → shoot
    hurt_drink           1   1/1              L1  hp<=20・回復薬あり → drink_potion
    hurt_retreat         1   1/1              L1  hp<=20・回復薬なし・敵あり → retreat
    mage_melee           0                    L2+L4  隣接の魔術師(警報済み) → melee_attack

棄権の番人(割れている所、証拠が足りない所。輪が審判に訊き直す所)
    hp_ambiguous         10  21<=hp<=32。30〜31 で会話が割れ、21〜32 の答えは 5 種に散る
    no_arrows_cover       6  離れた敵・矢 0・遮蔽あり(hold 4 / take_cover 2)
    mage_alarm_unclear    5  警報未の魔術師(敵 3 以下、敵 3 なら味方あり)。
                             melee 1 / raise 2 / shoot 2、根拠はほぼ gap
    troll_alarm_raised    5  警報済みのトロル(hold 1 / shoot 2 / take_cover 2、全件 gap)
    orc_alarm_unclear     3  警報未のオーク 2〜3 体(敵 3 なら味方あり)。
                             オーク 2 体は raise 2(s2, s3)/ melee 1(s3)
    hurt_no_threat        3  hp<=20・薬なし・敵なし。retreat 3 だが会話 1 本(s3)・gap
    group_alarm_unclear   2  警報未のゴブリン 3 体・味方あり。L2 どおり 2 件だが会話 1 本(s3)、
                             味方 0 では警報(outnumbered_alarm)なので味方の数が効く
    mage_no_arrows        1  離れた魔術師・矢 0(melee 1 件、gap)
    hurt_vs_alarm         1  hp<=20 とトロル・警報未が重なる(raise 1 件、gap)
"""

import math

_ACTIONS = (
    "melee_attack", "shoot", "retreat", "drink_potion",
    "take_cover", "raise_alarm", "hold_position",
)

_ENEMIES = ("none", "goblin", "orc", "mage", "troll")
_POSTS = ("gate", "wall", "corridor")
_TIMES = ("day", "night")

_KEYS = (
    "hp", "enemy", "distance", "enemy_count", "enemy_hp", "allies",
    "potion", "arrows", "cover", "alarm", "post", "time",
)

# 「ひどく傷ついている」
_HURT_MAX = 20      # これ以下は明らかにひどい(b0 のまま)
_FINE_MIN = 33      # これ以上はひどくない(割れている 31 と次の例 35 の間)

# 警報未の群れ
_HORDE_MIN = 4          # 敵がこれ以上なら警報(敵 3 は割れる、4・5 は 10/10)
_OUTNUMBERED_MIN = 3    # 味方 0 で敵がこれ以上なら警報(3/3)


def _is_num(v):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return False
    if isinstance(v, float) and not math.isfinite(v):
        return False
    return True


def _is_count(v):
    if not _is_num(v):
        return False
    return float(v).is_integer()


def _in(v, lo, hi, integral=False):
    if integral:
        if not _is_count(v):
            return False
    elif not _is_num(v):
        return False
    return lo <= v <= hi


def _guard(s):
    """範囲の番人。問題があれば棄権の理由の文字列、無ければ None。"""
    if not isinstance(s, dict):
        return "out_of_range: state"
    for k in _KEYS:
        if k not in s:
            return "out_of_range: " + k

    if not _in(s["hp"], 5, 100):
        return "out_of_range: hp"

    enemy = s["enemy"]
    if not isinstance(enemy, str) or enemy not in _ENEMIES:
        return "out_of_range: enemy"

    if enemy == "none":
        if s["distance"] is not None:
            return "out_of_range: distance"
        if not _in(s["enemy_count"], 0, 0, integral=True):
            return "out_of_range: enemy_count"
        if s["enemy_hp"] is not None:
            return "out_of_range: enemy_hp"
    else:
        if not _in(s["distance"], 1, 12, integral=True):
            return "out_of_range: distance"
        if not _in(s["enemy_count"], 1, 5, integral=True):
            return "out_of_range: enemy_count"
        if not _in(s["enemy_hp"], 10, 100):
            return "out_of_range: enemy_hp"

    if not _in(s["allies"], 0, 3, integral=True):
        return "out_of_range: allies"
    if not _in(s["arrows"], 0, 20, integral=True):
        return "out_of_range: arrows"

    for k in ("potion", "cover", "alarm"):
        if not isinstance(s[k], bool):
            return "out_of_range: " + k

    if not isinstance(s["post"], str) or s["post"] not in _POSTS:
        return "out_of_range: post"
    if not isinstance(s["time"], str) or s["time"] not in _TIMES:
        return "out_of_range: time"
    return None


def decide(s):
    bad = _guard(s)
    if bad is not None:
        return (None, bad)

    hp = s["hp"]
    enemy = s["enemy"]
    dist = s["distance"]
    count = s["enemy_count"]
    allies = s["allies"]
    potion = s["potion"]
    arrows = s["arrows"]
    cover = s["cover"]
    alarm = s["alarm"]

    hurt = hp <= _HURT_MAX
    fine = hp >= _FINE_MIN

    # --- L1: ひどく傷ついている ---
    if hurt:
        if enemy == "troll" and not alarm:
            return (None, "hurt_vs_alarm")
        if potion:
            return ("drink_potion", "hurt_drink")
        if enemy == "none":
            return (None, "hurt_no_threat")
        return ("retreat", "hurt_retreat")

    if not fine:
        return (None, "hp_ambiguous")

    # ここから先は hp>=33(ひどくない)

    # --- L7: 脅威が無い ---
    if enemy == "none":
        return ("hold_position", "no_threat_hold")

    # --- L3 + L5: トロル ---
    if enemy == "troll":
        if not alarm:
            return ("raise_alarm", "troll_alarm")
        return (None, "troll_alarm_raised")

    # --- L5: 警報未のとき、深刻な脅威かどうか ---
    if not alarm:
        if count >= _HORDE_MIN:
            return ("raise_alarm", "horde_alarm")
        if count >= _OUTNUMBERED_MIN and allies == 0:
            return ("raise_alarm", "outnumbered_alarm")
        if enemy == "mage":
            return (None, "mage_alarm_unclear")
        if enemy == "orc" and count >= 2:
            return (None, "orc_alarm_unclear")
        if enemy == "goblin" and count >= 3:
            return (None, "group_alarm_unclear")
        # 単独のオーク、ゴブリン 1〜2 体は深刻な脅威ではない → L2 へ

    # --- L2 (+ L4 魔術師) ---
    if dist == 1:
        if enemy == "mage":
            return ("melee_attack", "mage_melee")
        return ("melee_attack", "melee_adjacent")

    # 離れている(distance>=2)
    if arrows <= 0:
        if enemy == "mage":
            return (None, "mage_no_arrows")
        if cover:
            return (None, "no_arrows_cover")
        return ("hold_position", "no_arrows_hold")
    if enemy == "mage":
        return ("shoot", "mage_shoot")
    return ("shoot", "shoot_far")

```

## 熱さの帳簿(審判のラベル 264 件、会話 6 本を、いまの方針の枝ごとに数えた)

| 枝 | 件数 | 会話 | 方針の答え | 一致 | 会話の多数が方針と同じ | 審判の答え | 根拠 | 決め手(多い順) |
|---|---|---|---|---|---|---|---|---|
| no_threat_hold | 45 | 6 | hold_position | 45/45 | 6/6 | {'hold_position': 45} | L7 45, L1 5; gap 5 | enemy=none 45, hp>=40 2, hp>=45 2, hp>=44 1 |
| hp_ambiguous | 40 | 6 | None | -/- | -/6 | {'retreat': 19, 'hold_position': 5, 'shoot': 5, 'raise_alarm': 3, 'drink_potion': 8} | L1 33, L7 14, L2 10; gap 31 | potion=false 17, hp<=30 15, potion=true 8, enemy=none 7 |
| shoot_far | 27 | 5 | shoot | 26/27 | 4/5 | {'shoot': 26, 'take_cover': 1} | L2 27, L6 1; gap 1 | distance>=2 15, arrows>=1 9, distance>=6 3, enemy=goblin 2 |
| no_arrows_cover | 26 | 6 | None | -/- | -/6 | {'hold_position': 18, 'take_cover': 8} | L6 7; gap 22 | arrows=0 26, distance>=2 9, time=night 7, cover=true 7 |
| mage_alarm_unclear | 20 | 6 | None | -/- | -/6 | {'raise_alarm': 11, 'shoot': 5, 'melee_attack': 4} | L4 20, L5 20, L2 10; gap 17 | enemy=mage 18, alarm=false 11, enemy_count>=3 4, arrows=0 3 |
| horde_alarm | 17 | 6 | raise_alarm | 17/17 | 6/6 | {'raise_alarm': 17} | L5 17, L2 11, L6 4; gap 14 | alarm=false 17, enemy_count>=5 11, allies=0 6, enemy_count>=4 6 |
| troll_alarm_raised | 15 | 6 | None | -/- | -/6 | {'shoot': 5, 'take_cover': 4, 'hold_position': 1, 'retreat': 3, 'melee_attack': 2} | L3 14, L2 11, L6 5; gap 10 | enemy=troll 9, allies=0 6, allies>=2 4, distance>=2 3 |
| melee_adjacent | 12 | 5 | melee_attack | 12/12 | 5/5 | {'melee_attack': 12} | L2 12; gap 1 | distance=1 7, distance<=1 5, enemy_hp<=10 3, hp>=40 1 |
| orc_alarm_unclear | 12 | 5 | None | -/- | -/5 | {'raise_alarm': 7, 'melee_attack': 1, 'shoot': 4} | L5 11, L2 10, L6 6; gap 9 | alarm=false 7, time=night 6, allies=0 5, enemy=orc 1 |
| hurt_no_threat | 12 | 4 | None | -/- | -/4 | {'retreat': 10, 'hold_position': 2} | L7 12, L1 12; gap 12 | potion=false 10, hp<=15 4, allies>=2 4, hp<=30 3 |
| no_arrows_hold | 10 | 6 | hold_position | 10/10 | 6/6 | {'hold_position': 10} | L6 1; gap 10 | arrows=0 10, distance>=2 4, enemy=goblin 4, distance>=3 3 |
| group_alarm_unclear | 6 | 4 | None | -/- | -/4 | {'melee_attack': 1, 'shoot': 2, 'raise_alarm': 1, 'hold_position': 2} | L2 4, L5 3, L6 1; gap 4 | enemy=goblin 3, allies>=3 2, distance>=2 2, arrows=0 2 |
| troll_alarm | 5 | 3 | raise_alarm | 5/5 | 3/3 | {'raise_alarm': 5} | L5 5, L3 4; gap 2 | enemy=troll 5, alarm=false 5, allies=0 2, arrows=0 1 |
| mage_no_arrows | 4 | 3 | None | -/- | -/3 | {'melee_attack': 2, 'take_cover': 2} | L4 2, L2 1; gap 4 | enemy=mage 4, arrows=0 4, cover=true 2, hp>=90 1 |
| hurt_vs_alarm | 4 | 3 | None | -/- | -/3 | {'raise_alarm': 3, 'drink_potion': 1} | L5 4, L1 4, L3 1; gap 4 | alarm=false 3, enemy=troll 3, distance>=12 1, distance>=10 1 |
| outnumbered_alarm | 3 | 2 | raise_alarm | 3/3 | 2/2 | {'raise_alarm': 3} | L5 3, L6 2, L2 2; gap 3 | enemy_count>=3 3, allies=0 3, alarm=false 3 |
| mage_shoot | 3 | 2 | shoot | 3/3 | 2/2 | {'shoot': 3} | L4 3, L2 3 | enemy=mage 3, arrows>=4 2, distance>=6 1, arrows>=7 1 |
| hurt_drink | 2 | 2 | drink_potion | 2/2 | 2/2 | {'drink_potion': 2} | L1 2 | potion=true 2, enemy=none 2, hp<=30 1, hp<=12 1 |
| hurt_retreat | 1 | 1 | retreat | 1/1 | 1/1 | {'retreat': 1} | L1 1 | hp<=30 1, potion=false 1 |

## 食い違いと棄権の例(全部。[根拠] 決め手 「理由」 会話)
### hp_ambiguous
- 方針=None 審判=drink_potion [L1,L2+gap] hp<=21,potion=true 「重傷なので隣の敵より先に回復薬を飲む」 (round1_s2) | hp=21 enemy=goblin distance=1 enemy_count=2 enemy_hp=20 allies=3 potion=True arrows=6 cover=True alarm=False post=corridor time=day
- 方針=None 審判=drink_potion [L1,L2+gap] hp<=31,potion=true,distance>=12 「深手で敵はまだ遠い、今のうちに回復薬を飲む」 (round1_s2) | hp=31 enemy=orc distance=12 enemy_count=2 enemy_hp=30 allies=0 potion=True arrows=10 cover=False alarm=True post=wall time=day
- 方針=None 審判=drink_potion [L1] hp<=26,potion=true,enemy=none 「重傷で敵のいない今、回復薬を飲む」 (round1_s3) | hp=26 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=True arrows=2 cover=True alarm=True post=wall time=day
- 方針=None 審判=drink_potion [L1] hp<=30,potion=true 「深手で敵もいないので今のうちに回復薬を飲む」 (round2_s1) | hp=30 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=True arrows=3 cover=False alarm=False post=wall time=night
- 方針=None 審判=drink_potion [L1] hp<=33,potion=true,enemy=none 「深手なので敵のいない今回復薬を飲む」 (round2_s1) | hp=31 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=True arrows=18 cover=True alarm=False post=gate time=day
- 方針=None 審判=drink_potion [L1] hp<=30,potion=true 「深手なので回復薬を飲む」 (round2_s1) | hp=29 enemy=goblin distance=2 enemy_count=2 enemy_hp=60 allies=0 potion=True arrows=0 cover=True alarm=False post=gate time=night
- 方針=None 審判=drink_potion [L1] hp<=30,potion=true,distance>=2 「重傷で薬があり敵も遠いので今飲む」 (round2_s2) | hp=29 enemy=goblin distance=11 enemy_count=1 enemy_hp=80 allies=1 potion=True arrows=20 cover=False alarm=True post=wall time=day
- 方針=None 審判=drink_potion [L1,L5+gap] hp<=26,potion=true,enemy=goblin 「重傷で薬がある、ゴブリン相手なら回復が先」 (round2_s3) | hp=26 enemy=goblin distance=3 enemy_count=3 enemy_hp=90 allies=1 potion=True arrows=20 cover=True alarm=False post=gate time=night
- 方針=None 審判=hold_position [L0,L7+gap] enemy=none,post=gate 「深手だが敵はなく、夜の門を空けず持ち場に留まる」 (round1_s1) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=True alarm=False post=gate time=night
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,allies=0,hp>=30 「敵も代わりもいない、体力30なら門に残る」 (round1_s3) | hp=30 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=0 cover=False alarm=False post=gate time=night
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp>=32,allies=1 「重傷とまでは言えず脅威も無いので持ち場を守る」 (round2_s2) | hp=32 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=2 cover=True alarm=False post=gate time=day
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,allies=0,hp<=28 「傷は深いが脅威が無く、門を空けられないので留まる」 (round2_s3) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=True alarm=False post=gate time=night
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp>=31 「脅威が無く、ひどい傷とまでは言えず留まる」 (round2_s3) | hp=31 enemy=none distance=None enemy_count=0 enemy_hp=None allies=3 potion=False arrows=15 cover=False alarm=False post=gate time=night
- 方針=None 審判=raise_alarm [L4,L5+gap] enemy=mage,alarm=false,distance>=10 「深手だが魔術師はまだ遠い、先に警報を鳴らす」 (round1_s1) | hp=28 enemy=mage distance=10 enemy_count=2 enemy_hp=80 allies=2 potion=True arrows=10 cover=False alarm=False post=wall time=night
- 方針=None 審判=raise_alarm [L2,L5,L6+gap] alarm=false,enemy_count>=3,allies=0 「夜に単独で三体、射るより先に警報を鳴らす」 (round2_s3) | hp=31 enemy=goblin distance=7 enemy_count=3 enemy_hp=40 allies=0 potion=False arrows=17 cover=True alarm=False post=wall time=night
- 方針=None 審判=raise_alarm [L1,L5+gap] alarm=false,enemy_count>=3,allies=0 「単独でオーク三体、助けを呼ぶのが生存の道」 (round2_s3) | hp=27 enemy=orc distance=3 enemy_count=3 enemy_hp=70 allies=0 potion=True arrows=7 cover=True alarm=False post=corridor time=day
- 方針=None 審判=retreat [L1,L3+gap] hp<=30,potion=false,enemy=troll 「瀕死で薬なし、隣にトロルがいるので警報より退く」 (round1_s1) | hp=23 enemy=troll distance=1 enemy_count=3 enemy_hp=10 allies=0 potion=False arrows=14 cover=True alarm=False post=corridor time=day
- 方針=None 審判=retreat [L1] hp<=30,potion=false 「深手で薬も矢もないので退く」 (round1_s1) | hp=23 enemy=orc distance=6 enemy_count=2 enemy_hp=40 allies=2 potion=False arrows=0 cover=False alarm=False post=corridor time=day
- 方針=None 審判=retreat [L1,L2+gap] hp<=22,potion=false,allies=0 「重傷で薬も味方も無い、射たずに退く」 (round1_s2) | hp=22 enemy=goblin distance=2 enemy_count=2 enemy_hp=100 allies=0 potion=False arrows=4 cover=False alarm=False post=gate time=day
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false,allies>=2 「深手で薬が無く味方が残るので退いて癒す」 (round2_s1) | hp=29 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=19 cover=True alarm=False post=wall time=day
- 方針=None 審判=retreat [L1,L3,L5+gap] hp<=30,potion=false,enemy=troll 「深手で薬も無く一人でトロルには勝てないので退く」 (round2_s1) | hp=23 enemy=troll distance=1 enemy_count=3 enemy_hp=10 allies=0 potion=False arrows=14 cover=True alarm=False post=corridor time=day
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false 「深手で薬が無いので敵のいない今退く」 (round2_s1) | hp=30 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=12 cover=False alarm=False post=wall time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false,allies>=2 「深手で薬が無く味方が残るので退く」 (round2_s1) | hp=26 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=16 cover=False alarm=False post=corridor time=day
- 方針=None 審判=retreat [L1,L6+gap] hp<=33,potion=false,time=night 「深手で薬が無い夜なので射るより退く」 (round2_s1) | hp=31 enemy=goblin distance=9 enemy_count=3 enemy_hp=40 allies=1 potion=False arrows=5 cover=False alarm=True post=wall time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=33,potion=false,allies>=2 「深手で薬が無く味方が残るので退いて癒す」 (round2_s1) | hp=32 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=20 cover=True alarm=False post=corridor time=day
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false 「深手で薬が無いので敵のいない今退く」 (round2_s1) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=True alarm=False post=gate time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false,time=night 「深手で薬が無い夜なので退く」 (round2_s1) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=7 cover=False alarm=True post=wall time=night
- 方針=None 審判=retreat [L1] hp<=30,potion=false 「深手で薬が無いので退く」 (round2_s1) | hp=21 enemy=goblin distance=8 enemy_count=2 enemy_hp=60 allies=1 potion=False arrows=5 cover=False alarm=False post=gate time=day
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false 「深手で薬が無いので退いて癒す」 (round2_s1) | hp=23 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=15 cover=True alarm=False post=gate time=day
- 方針=None 審判=retreat [L1,L6+gap] hp<=33,potion=false,allies>=3 「深手で薬の無い夜、味方に任せて退く」 (round2_s1) | hp=32 enemy=orc distance=9 enemy_count=3 enemy_hp=20 allies=3 potion=False arrows=15 cover=True alarm=True post=gate time=night
- 方針=None 審判=retreat [L0,L2+gap] hp<=31,enemy_count>=4,time=night 「深手で夜にオーク4体、無駄死にを避けて退く」 (round2_s2) | hp=31 enemy=orc distance=10 enemy_count=4 enemy_hp=90 allies=1 potion=False arrows=2 cover=False alarm=True post=corridor time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false 「重傷で薬も無いので退いて立て直す」 (round2_s2) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=True alarm=False post=gate time=night
- 方針=None 審判=retreat [L1,L3,L5+gap] hp<=30,enemy=troll,distance=1 「重傷で単独、隣のトロルから退く」 (round2_s2) | hp=23 enemy=troll distance=1 enemy_count=3 enemy_hp=10 allies=0 potion=False arrows=14 cover=True alarm=False post=corridor time=day
- 方針=None 審判=retreat [L1,L3,L5+gap] hp<=23,potion=false,distance=1 「重傷で薬が無く隣にトロル、警報より退避を優先」 (round2_s3) | hp=23 enemy=troll distance=1 enemy_count=3 enemy_hp=10 allies=0 potion=False arrows=14 cover=True alarm=False post=corridor time=day
- 方針=None 審判=retreat [L1,L7+gap] hp<=28,potion=false,allies>=1 「重傷で薬が無い、持ち場は味方に任せて退く」 (round2_s3) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=3 cover=False alarm=False post=wall time=day
- 方針=None 審判=shoot [L2+gap] distance>=2,arrows>=1,hp>=31 「手負いだが敵は遠く、射るだけなら危険は小さい」 (round1_s1) | hp=31 enemy=goblin distance=9 enemy_count=3 enemy_hp=40 allies=1 potion=False arrows=5 cover=False alarm=True post=wall time=night
- 方針=None 審判=shoot [L2] distance>=2,arrows=18,enemy=goblin 「ゴブリンは離れており矢も多いので射る」 (round2_s2) | hp=32 enemy=goblin distance=6 enemy_count=2 enemy_hp=80 allies=1 potion=False arrows=18 cover=False alarm=True post=gate time=day
- 方針=None 審判=shoot [L2] distance>=2,arrows=5,enemy=goblin 「城壁から遠いゴブリンを射る」 (round2_s2) | hp=31 enemy=goblin distance=9 enemy_count=3 enemy_hp=40 allies=1 potion=False arrows=5 cover=False alarm=True post=wall time=night
- 方針=None 審判=shoot [L1,L2+gap] enemy_hp<=10,distance>=7,arrows>=9 「重傷だが敵は遠く瀕死のゴブリン、射って仕留める」 (round2_s3) | hp=26 enemy=goblin distance=7 enemy_count=1 enemy_hp=10 allies=1 potion=False arrows=9 cover=False alarm=False post=wall time=day
- 方針=None 審判=shoot [L1,L2+gap] distance>=9,arrows>=5,alarm=true 「敵は遠く警報済み、まだ射って戦える傷と見る」 (round2_s3) | hp=31 enemy=goblin distance=9 enemy_count=3 enemy_hp=40 allies=1 potion=False arrows=5 cover=False alarm=True post=wall time=night
### shoot_far
- 方針=shoot 審判=take_cover [L2,L6+gap] time=night,enemy_count>=5,allies=0 「夜に一人で五体相手なので遮蔽で援軍を待つ」 (round2_s1) | hp=99 enemy=goblin distance=3 enemy_count=5 enemy_hp=60 allies=0 potion=True arrows=12 cover=True alarm=True post=gate time=night
### no_arrows_cover
- 方針=None 審判=hold_position [gap] arrows=0,distance>=2 「矢がなく敵も遠い、味方と通路を固めて待つ」 (round1_s1) | hp=91 enemy=orc distance=6 enemy_count=1 enemy_hp=90 allies=3 potion=True arrows=0 cover=True alarm=True post=corridor time=day
- 方針=None 審判=hold_position [gap] arrows=0,distance>=2 「矢がなく敵は遠い、持ち場で待つ」 (round1_s1) | hp=71 enemy=goblin distance=10 enemy_count=2 enemy_hp=80 allies=1 potion=False arrows=0 cover=True alarm=True post=corridor time=day
- 方針=None 審判=hold_position [gap] arrows=0,distance>=8 「矢が無く敵は遠い、持ち場でオークを迎え撃つ」 (round1_s2) | hp=91 enemy=orc distance=8 enemy_count=1 enemy_hp=50 allies=0 potion=False arrows=0 cover=True alarm=True post=wall time=day
- 方針=None 審判=hold_position [gap] arrows=0,distance>=7 「矢が無く敵は遠い、持ち場で待ち受ける」 (round1_s3) | hp=86 enemy=goblin distance=7 enemy_count=1 enemy_hp=60 allies=3 potion=True arrows=0 cover=True alarm=False post=corridor time=day
- 方針=None 審判=hold_position [gap] arrows=0,distance>=8,enemy=goblin 「矢が無く遠いゴブリン一体なので持ち場で待つ」 (round2_s1) | hp=47 enemy=goblin distance=8 enemy_count=1 enemy_hp=40 allies=0 potion=False arrows=0 cover=True alarm=False post=wall time=day
- 方針=None 審判=hold_position [gap] arrows=0,distance>=6,enemy_count=1 「矢が無く遠いオーク一体なので持ち場で待つ」 (round2_s1) | hp=91 enemy=orc distance=6 enemy_count=1 enemy_hp=90 allies=3 potion=True arrows=0 cover=True alarm=True post=corridor time=day
- 方針=None 審判=hold_position [gap] arrows=0,distance>=2,allies>=3 「矢が無く傷も中程度なので味方と門で待ち受ける」 (round2_s1) | hp=37 enemy=orc distance=2 enemy_count=1 enemy_hp=30 allies=3 potion=False arrows=0 cover=True alarm=True post=gate time=day
- 方針=None 審判=hold_position [gap] arrows=0,distance>=7,enemy_count=1 「矢が無く遠いゴブリン一体なので門で待つ」 (round2_s1) | hp=91 enemy=goblin distance=7 enemy_count=1 enemy_hp=90 allies=0 potion=False arrows=0 cover=True alarm=True post=gate time=day
- 方針=None 審判=hold_position [gap] arrows=0,distance>=2,allies>=3 「矢は無いが味方が多く通路で待ち構える」 (round2_s2) | hp=91 enemy=orc distance=6 enemy_count=1 enemy_hp=90 allies=3 potion=True arrows=0 cover=True alarm=True post=corridor time=day
- 方針=None 審判=hold_position [gap] arrows=0,distance>=2 「矢が無いので持ち場で接近を待つ」 (round2_s2) | hp=100 enemy=goblin distance=8 enemy_count=1 enemy_hp=80 allies=1 potion=True arrows=0 cover=True alarm=True post=corridor time=day
- 方針=None 審判=hold_position [gap] arrows=0,enemy=goblin,distance>=2 「矢が無く単独のゴブリンなので持ち場で待つ」 (round2_s2) | hp=54 enemy=goblin distance=8 enemy_count=1 enemy_hp=60 allies=0 potion=False arrows=0 cover=True alarm=False post=wall time=day
- 方針=None 審判=hold_position [gap] arrows=0,distance>=2 「矢が無いので持ち場で接近を待つ」 (round2_s2) | hp=97 enemy=goblin distance=8 enemy_count=1 enemy_hp=40 allies=1 potion=True arrows=0 cover=True alarm=True post=corridor time=day
- 方針=None 審判=hold_position [gap] arrows=0,distance>=2 「矢が無く敵も遠いので門を守って待つ」 (round2_s2) | hp=98 enemy=orc distance=11 enemy_count=2 enemy_hp=50 allies=0 potion=False arrows=0 cover=True alarm=True post=gate time=day
- 方針=None 審判=hold_position [gap] arrows=0,distance>=2 「矢が無いので通路で接近を待つ」 (round2_s2) | hp=85 enemy=goblin distance=4 enemy_count=2 enemy_hp=80 allies=1 potion=False arrows=0 cover=True alarm=True post=corridor time=day
- 方針=None 審判=hold_position [gap] arrows=0,distance>=6,alarm=true 「矢が無く敵は遠い、警報済みなので持ち場で迎える」 (round2_s3) | hp=91 enemy=orc distance=6 enemy_count=1 enemy_hp=90 allies=3 potion=True arrows=0 cover=True alarm=True post=corridor time=day
- 方針=None 審判=hold_position [gap] arrows=0,distance>=8,enemy=goblin 「矢が無く敵は遠い、門で待ち受ける」 (round2_s3) | hp=87 enemy=goblin distance=8 enemy_count=1 enemy_hp=40 allies=1 potion=False arrows=0 cover=True alarm=False post=gate time=day
- 方針=None 審判=hold_position [gap] arrows=0,distance=2,enemy=goblin 「矢が無く隣接もしていない、門で待ち受ける」 (round2_s3) | hp=59 enemy=goblin distance=2 enemy_count=2 enemy_hp=80 allies=0 potion=False arrows=0 cover=True alarm=False post=gate time=day
- 方針=None 審判=hold_position [gap] arrows=0,distance>=4 「矢が無く隣接もしていない、持ち場で待ち受ける」 (round2_s3) | hp=63 enemy=orc distance=4 enemy_count=1 enemy_hp=50 allies=1 potion=True arrows=0 cover=True alarm=False post=wall time=day
- 方針=None 審判=take_cover [L6+gap] arrows=0,time=night,cover=true 「夜に単独で矢もない、遮蔽に隠れて様子を見る」 (round1_s1) | hp=44 enemy=goblin distance=11 enemy_count=3 enemy_hp=30 allies=0 potion=True arrows=0 cover=True alarm=True post=wall time=night
- 方針=None 審判=take_cover [gap] hp<=42,potion=false,arrows=0 「矢も薬も無く体力半分以下、遮蔽で門に踏み止まる」 (round1_s2) | hp=42 enemy=goblin distance=4 enemy_count=3 enemy_hp=60 allies=3 potion=False arrows=0 cover=True alarm=True post=gate time=day
- 方針=None 審判=take_cover [L6] time=night,arrows=0,cover=true 「夜で矢が無いので遮蔽に隠れて敵を待つ」 (round2_s1) | hp=97 enemy=goblin distance=7 enemy_count=2 enemy_hp=70 allies=2 potion=False arrows=0 cover=True alarm=True post=gate time=night
- 方針=None 審判=take_cover [L6] time=night,arrows=0,cover=true 「夜で矢が無いので遮蔽に隠れて待つ」 (round2_s1) | hp=90 enemy=goblin distance=8 enemy_count=4 enemy_hp=40 allies=1 potion=False arrows=0 cover=True alarm=True post=corridor time=night
- 方針=None 審判=take_cover [L6] arrows=0,time=night,cover=true 「夜で矢も無いので遮蔽に入り接近を待つ」 (round2_s2) | hp=65 enemy=orc distance=12 enemy_count=2 enemy_hp=20 allies=2 potion=False arrows=0 cover=True alarm=True post=corridor time=night
- 方針=None 審判=take_cover [L6] time=night,arrows=0,cover=true 「夜で矢も無いので遮蔽に入り接近を待つ」 (round2_s2) | hp=82 enemy=orc distance=11 enemy_count=1 enemy_hp=50 allies=2 potion=False arrows=0 cover=True alarm=True post=gate time=night
- 方針=None 審判=take_cover [L6+gap] time=night,arrows=0,cover=true 「夜で矢も無く、遮蔽に隠れて敵の接近を待つ」 (round2_s3) | hp=82 enemy=goblin distance=2 enemy_count=2 enemy_hp=50 allies=0 potion=False arrows=0 cover=True alarm=True post=gate time=night
- 方針=None 審判=take_cover [L6+gap] time=night,arrows=0,cover=true 「夜で矢も無い、遮蔽に隠れて様子を見る」 (round2_s3) | hp=95 enemy=goblin distance=12 enemy_count=1 enemy_hp=40 allies=0 potion=False arrows=0 cover=True alarm=False post=gate time=night
### mage_alarm_unclear
- 方針=None 審判=melee_attack [L2,L4,L5+gap] enemy=mage,distance=1,enemy_hp<=30 「隣の弱った魔術師を警報より先に仕留める」 (round1_s3) | hp=93 enemy=mage distance=1 enemy_count=1 enemy_hp=30 allies=1 potion=True arrows=0 cover=False alarm=False post=gate time=night
- 方針=None 審判=melee_attack [L2,L4,L5+gap] enemy=mage,distance<=1,enemy_hp<=30 「隣の弱った魔術師を警報より先に斬る」 (round2_s1) | hp=80 enemy=mage distance=1 enemy_count=1 enemy_hp=30 allies=0 potion=False arrows=0 cover=True alarm=False post=corridor time=day
- 方針=None 審判=melee_attack [L2,L4,L5+gap] enemy=mage,distance<=1 「隣の魔術師を警報より先に斬る」 (round2_s1) | hp=78 enemy=mage distance=1 enemy_count=2 enemy_hp=60 allies=1 potion=False arrows=17 cover=True alarm=False post=gate time=night
- 方針=None 審判=melee_attack [L2,L4,L5+gap] enemy=mage,distance=1 「隣接した魔術師は今叩く好機、警報より優先」 (round2_s3) | hp=37 enemy=mage distance=1 enemy_count=2 enemy_hp=100 allies=1 potion=True arrows=0 cover=True alarm=False post=gate time=day
- 方針=None 審判=raise_alarm [L4,L5] enemy=mage,alarm=false,arrows=0 「魔術師が現れ未警報、矢もないので警報を鳴らす」 (round1_s1) | hp=89 enemy=mage distance=6 enemy_count=2 enemy_hp=80 allies=1 potion=False arrows=0 cover=False alarm=False post=corridor time=night
- 方針=None 審判=raise_alarm [L2,L4,L5+gap] alarm=false,enemy=mage,arrows<=1 「矢1本では魔術師を仕留めきれず先に警報」 (round1_s3) | hp=71 enemy=mage distance=9 enemy_count=2 enemy_hp=70 allies=1 potion=True arrows=1 cover=True alarm=False post=wall time=day
- 方針=None 審判=raise_alarm [L2,L4,L5+gap] alarm=false,enemy=mage,distance>=12 「魔術師がまだ遠いうちに警報を鳴らす」 (round2_s1) | hp=50 enemy=mage distance=12 enemy_count=2 enemy_hp=90 allies=1 potion=True arrows=15 cover=False alarm=False post=gate time=day
- 方針=None 審判=raise_alarm [L2,L4,L5+gap] alarm=false,enemy_count>=3,distance>=7 「魔術師を含む三体がまだ遠いので警報」 (round2_s1) | hp=80 enemy=mage distance=7 enemy_count=3 enemy_hp=60 allies=1 potion=False arrows=5 cover=False alarm=False post=gate time=day
- 方針=None 審判=raise_alarm [L4,L5,L6+gap] enemy=mage,alarm=false,arrows=0 「矢が無く魔術師を討てないので警報を優先する」 (round2_s2) | hp=65 enemy=mage distance=3 enemy_count=1 enemy_hp=50 allies=0 potion=False arrows=0 cover=True alarm=False post=gate time=night
- 方針=None 審判=raise_alarm [L4,L5+gap] alarm=false,enemy=mage,enemy_count>=3 「無傷の魔術師と群れ、矢2本では足りず警報」 (round2_s2) | hp=91 enemy=mage distance=8 enemy_count=3 enemy_hp=100 allies=1 potion=True arrows=2 cover=True alarm=False post=wall time=night
- 方針=None 審判=raise_alarm [L4,L5] enemy=mage,alarm=false,arrows=0 「魔術師を討つ手段が無く、まず警報で知らせる」 (round2_s2) | hp=81 enemy=mage distance=6 enemy_count=1 enemy_hp=60 allies=0 potion=True arrows=0 cover=False alarm=False post=gate time=night
- 方針=None 審判=raise_alarm [L4,L5+gap] alarm=false,enemy_count>=3,arrows=1 「矢1本では心許なく、遠い今のうちに警報」 (round2_s2) | hp=89 enemy=mage distance=10 enemy_count=3 enemy_hp=40 allies=2 potion=False arrows=1 cover=True alarm=False post=gate time=day
- 方針=None 審判=raise_alarm [L4,L5] alarm=false,enemy=mage,enemy_count>=3 「魔術師を含む群れが来たので警報を鳴らす」 (round2_s2) | hp=66 enemy=mage distance=11 enemy_count=3 enemy_hp=100 allies=1 potion=True arrows=0 cover=False alarm=False post=wall time=day
- 方針=None 審判=raise_alarm [L4,L5,L6+gap] enemy=mage,alarm=false,time=night 「夜に魔術師を含む群れ、まず警報で城に知らせる」 (round2_s3) | hp=89 enemy=mage distance=3 enemy_count=2 enemy_hp=90 allies=1 potion=False arrows=3 cover=False alarm=False post=corridor time=night
- 方針=None 審判=raise_alarm [L4,L5,L6+gap] enemy=mage,alarm=false,time=night 「夜に魔術師、一矢では倒せず先に警報を鳴らす」 (round2_s3) | hp=76 enemy=mage distance=6 enemy_count=1 enemy_hp=70 allies=0 potion=True arrows=7 cover=False alarm=False post=gate time=night
- 方針=None 審判=shoot [L4,L5+gap] enemy=mage,enemy_count=1,arrows>=11 「魔術師単独なら警報より先に射て早く仕留める」 (round1_s2) | hp=84 enemy=mage distance=6 enemy_count=1 enemy_hp=40 allies=0 potion=True arrows=11 cover=True alarm=False post=gate time=day
- 方針=None 審判=shoot [L4,L5+gap] enemy=mage,enemy_hp<=10,arrows>=6 「瀕死の魔術師を一射で仕留められるので射る」 (round1_s2) | hp=54 enemy=mage distance=6 enemy_count=2 enemy_hp=10 allies=0 potion=False arrows=6 cover=False alarm=False post=wall time=day
- 方針=None 審判=shoot [L2,L4,L5+gap] enemy=mage,distance<=3,arrows>=9 「近い魔術師は警報より先に射て早く仕留める」 (round2_s1) | hp=91 enemy=mage distance=3 enemy_count=2 enemy_hp=60 allies=2 potion=False arrows=9 cover=False alarm=False post=gate time=day
- 方針=None 審判=shoot [L2,L4,L5+gap] enemy=mage,distance<=2,arrows>=10 「近い魔術師を警報より先に射て仕留める」 (round2_s1) | hp=76 enemy=mage distance=2 enemy_count=1 enemy_hp=70 allies=0 potion=False arrows=10 cover=False alarm=False post=gate time=day
- 方針=None 審判=shoot [L2,L4,L5+gap] enemy=mage,enemy_hp<=30,arrows=20 「弱った魔術師を今射れば仕留められる」 (round2_s2) | hp=69 enemy=mage distance=6 enemy_count=2 enemy_hp=30 allies=1 potion=True arrows=20 cover=False alarm=False post=corridor time=day
### troll_alarm_raised
- 方針=None 審判=hold_position [L3+gap] arrows=0,distance>=12,allies>=3 「矢が無く敵は遠い、味方3人と門を固めて待つ」 (round1_s2) | hp=92 enemy=troll distance=12 enemy_count=5 enemy_hp=40 allies=3 potion=True arrows=0 cover=True alarm=True post=gate time=day
- 方針=None 審判=melee_attack [L2,L3] enemy=troll,distance<=1,allies>=1 「味方がいるので隣のトロルと近接で戦う」 (round2_s1) | hp=97 enemy=troll distance=1 enemy_count=2 enemy_hp=40 allies=1 potion=False arrows=17 cover=False alarm=True post=corridor time=day
- 方針=None 審判=melee_attack [L2,L3] distance=1,enemy=troll,allies>=2 「味方がいて一人ではないので隣接トロルと戦う」 (round2_s2) | hp=73 enemy=troll distance=1 enemy_count=4 enemy_hp=60 allies=2 potion=False arrows=3 cover=True alarm=True post=gate time=day
- 方針=None 審判=retreat [L2,L3,L6+gap] enemy=troll,allies=0,time=night 「夜に一人でトロルとは戦わず退く」 (round2_s1) | hp=90 enemy=troll distance=1 enemy_count=2 enemy_hp=20 allies=0 potion=True arrows=13 cover=True alarm=True post=wall time=night
- 方針=None 審判=retreat [L0,L3+gap] enemy=troll,arrows=0,hp<=42 「手負いで矢も無くトロルは手に余るので退く」 (round2_s2) | hp=42 enemy=troll distance=4 enemy_count=2 enemy_hp=60 allies=1 potion=False arrows=0 cover=True alarm=True post=gate time=day
- 方針=None 審判=retreat [L2,L3+gap] enemy=troll,allies=0,distance=1 「隣接トロルに単独では勝てず、無駄死にを避けて退く」 (round2_s3) | hp=90 enemy=troll distance=1 enemy_count=2 enemy_hp=70 allies=0 potion=False arrows=0 cover=True alarm=True post=wall time=night
- 方針=None 審判=shoot [L2,L3+gap] distance>=4,arrows>=1,allies>=2 「味方がいて矢も多い、近づく前にトロルを射る」 (round1_s1) | hp=78 enemy=troll distance=4 enemy_count=3 enemy_hp=80 allies=2 potion=False arrows=20 cover=True alarm=True post=corridor time=night
- 方針=None 審判=shoot [L2,L3+gap] allies>=1,distance>=2,arrows>=14 「味方がいて間合いもある、トロルを矢で削る」 (round1_s3) | hp=86 enemy=troll distance=3 enemy_count=1 enemy_hp=80 allies=1 potion=False arrows=14 cover=False alarm=True post=gate time=day
- 方針=None 審判=shoot [L2,L3] distance>=2,arrows=2,allies>=2 「味方がいてトロルは遠いので矢を射る」 (round2_s2) | hp=87 enemy=troll distance=8 enemy_count=2 enemy_hp=50 allies=2 potion=True arrows=2 cover=True alarm=True post=gate time=day
- 方針=None 審判=shoot [L2] distance>=2,arrows=10,alarm=true 「警報は既に鳴り、遠いトロルを城壁から射る」 (round2_s2) | hp=87 enemy=troll distance=7 enemy_count=4 enemy_hp=60 allies=2 potion=True arrows=10 cover=True alarm=True post=wall time=night
- 方針=None 審判=shoot [L2,L3] allies>=2,distance>=5,arrows>=14 「味方がいて単独ではない、遠いトロルを射る」 (round2_s3) | hp=39 enemy=troll distance=5 enemy_count=2 enemy_hp=40 allies=2 potion=False arrows=14 cover=False alarm=True post=gate time=day
- 方針=None 審判=take_cover [L2,L3,L6+gap] enemy=troll,allies=0,cover=true 「トロル含む4体に単独、夜なので射ずに遮蔽で門に留まる」 (round1_s2) | hp=99 enemy=troll distance=3 enemy_count=4 enemy_hp=30 allies=0 potion=False arrows=6 cover=True alarm=True post=gate time=night
- 方針=None 審判=take_cover [L3,L6+gap] enemy=troll,allies=0,cover=true 「単独でトロルに挑めず夜、遮蔽で援軍を待つ」 (round1_s2) | hp=95 enemy=troll distance=6 enemy_count=4 enemy_hp=40 allies=0 potion=False arrows=0 cover=True alarm=True post=corridor time=night
- 方針=None 審判=take_cover [L2,L3,L6+gap] enemy=troll,allies=0,time=night 「夜に一人でトロルは無理なので遮蔽で援軍を待つ」 (round2_s1) | hp=72 enemy=troll distance=6 enemy_count=2 enemy_hp=50 allies=0 potion=True arrows=3 cover=True alarm=True post=gate time=night
- 方針=None 審判=take_cover [L3,L6+gap] enemy=troll,allies=0,time=night 「夜に単独でトロル、警報済みなので遮蔽で援軍を待つ」 (round2_s3) | hp=94 enemy=troll distance=10 enemy_count=1 enemy_hp=100 allies=0 potion=False arrows=0 cover=True alarm=True post=gate time=night
### orc_alarm_unclear
- 方針=None 審判=melee_attack [L2,L5,L6+gap] distance=1,hp>=91,allies>=2 「味方2人と体力十分、隣接オークを斬る」 (round1_s3) | hp=91 enemy=orc distance=1 enemy_count=2 enemy_hp=60 allies=2 potion=True arrows=0 cover=False alarm=False post=gate time=night
- 方針=None 審判=raise_alarm [L2,L5,L6+gap] alarm=false,allies=0,time=night 「夜の門で単独、オーク2体に先に警報を鳴らす」 (round1_s2) | hp=82 enemy=orc distance=1 enemy_count=2 enemy_hp=80 allies=0 potion=False arrows=3 cover=False alarm=False post=gate time=night
- 方針=None 審判=raise_alarm [L2,L5,L6+gap] time=night,alarm=false,enemy=orc 「夜に門へオーク2体、用心して先に警報」 (round1_s3) | hp=61 enemy=orc distance=6 enemy_count=2 enemy_hp=40 allies=1 potion=False arrows=9 cover=False alarm=False post=gate time=night
- 方針=None 審判=raise_alarm [L5] alarm=false,allies=0,enemy_count>=2 「味方も矢も無く二体のオークが来るので警報」 (round2_s1) | hp=83 enemy=orc distance=7 enemy_count=2 enemy_hp=70 allies=0 potion=True arrows=0 cover=True alarm=False post=wall time=day
- 方針=None 審判=raise_alarm [L2,L5,L6+gap] alarm=false,allies=0,time=night 「夜に一人でオーク二体なので戦うより警報」 (round2_s1) | hp=82 enemy=orc distance=1 enemy_count=2 enemy_hp=80 allies=0 potion=False arrows=3 cover=False alarm=False post=gate time=night
- 方針=None 審判=raise_alarm [L5,L6] alarm=false,time=night,arrows=0 「夜に城壁へオーク2体、攻撃できぬ間に警報」 (round2_s2) | hp=75 enemy=orc distance=2 enemy_count=2 enemy_hp=30 allies=1 potion=False arrows=0 cover=False alarm=False post=wall time=night
- 方針=None 審判=raise_alarm [L2,L5+gap] alarm=false,allies=0,time=night 「夜の門に単独でオーク2体、まず警報を鳴らす」 (round2_s2) | hp=82 enemy=orc distance=1 enemy_count=2 enemy_hp=80 allies=0 potion=False arrows=3 cover=False alarm=False post=gate time=night
- 方針=None 審判=raise_alarm [L2,L5,L6+gap] alarm=false,allies=0,time=night 「夜の門に単独でオーク二体、殴るより警報が先」 (round2_s3) | hp=82 enemy=orc distance=1 enemy_count=2 enemy_hp=80 allies=0 potion=False arrows=3 cover=False alarm=False post=gate time=night
- 方針=None 審判=shoot [L2] arrows>=3,allies>=3,distance>=12 「味方が多く深刻ではないので遠いオークを射る」 (round2_s1) | hp=82 enemy=orc distance=12 enemy_count=2 enemy_hp=90 allies=3 potion=True arrows=3 cover=False alarm=False post=gate time=day
- 方針=None 審判=shoot [L2,L5+gap] distance>=4,arrows>=8,enemy_hp<=30 「弱ったオーク二体は射って削れる、警報は不要」 (round2_s3) | hp=98 enemy=orc distance=4 enemy_count=2 enemy_hp=30 allies=0 potion=False arrows=8 cover=False alarm=False post=corridor time=day
- 方針=None 審判=shoot [L2,L5+gap] distance>=3,arrows>=11,enemy_hp<=20 「瀕死のオーク二体は射れば片付く、警報は不要」 (round2_s3) | hp=99 enemy=orc distance=3 enemy_count=2 enemy_hp=20 allies=0 potion=True arrows=11 cover=False alarm=False post=corridor time=night
- 方針=None 審判=shoot [L2,L5+gap] distance>=9,arrows>=5,allies>=1 「昼で味方もいる、遠いオークは射って削る」 (round2_s3) | hp=37 enemy=orc distance=9 enemy_count=2 enemy_hp=90 allies=1 potion=False arrows=5 cover=False alarm=False post=wall time=day
### hurt_no_threat
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,allies=0,hp<=15 「重傷だが脅威が無く、門を空けないため留まる」 (round2_s3) | hp=15 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=11 cover=True alarm=False post=gate time=day
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,allies=0,hp<=10 「重傷だが脅威が無く、代わりもいないので留まる」 (round2_s3) | hp=10 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=False alarm=False post=corridor time=day
- 方針=None 審判=retreat [L1,L7+gap] hp<=15,potion=false,allies>=2 「重傷で薬も無い、門を味方に任せて退く」 (round1_s3) | hp=15 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=2 cover=False alarm=False post=gate time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=15,potion=false,allies>=2 「重傷で薬も無い、門を味方に任せて退く」 (round1_s3) | hp=15 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=0 cover=False alarm=True post=gate time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=14,potion=false,allies>=1 「重傷で薬も無い、門を味方に任せて退く」 (round1_s3) | hp=14 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=0 cover=True alarm=True post=gate time=day
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false 「瀕死で薬が無いので退く」 (round2_s1) | hp=19 enemy=none distance=None enemy_count=0 enemy_hp=None allies=3 potion=False arrows=5 cover=False alarm=True post=gate time=day
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false,allies>=2 「瀕死で薬が無く味方が残るので退く」 (round2_s1) | hp=16 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=15 cover=False alarm=False post=gate time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false 「重傷で薬が無いので敵のいない今のうちに退く」 (round2_s2) | hp=14 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=4 cover=True alarm=False post=gate time=day
- 方針=None 審判=retreat [L1,L7+gap] hp<=7,potion=false,allies>=3 「瀕死で薬が無い、門は味方に任せて退く」 (round2_s3) | hp=7 enemy=none distance=None enemy_count=0 enemy_hp=None allies=3 potion=False arrows=1 cover=True alarm=False post=gate time=day
- 方針=None 審判=retreat [L1,L7+gap] hp<=15,potion=false,allies>=3 「重傷で薬が無い、門は味方に任せて退く」 (round2_s3) | hp=15 enemy=none distance=None enemy_count=0 enemy_hp=None allies=3 potion=False arrows=0 cover=True alarm=False post=gate time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=13,potion=false,allies>=1 「重傷で薬が無い、持ち場は味方に任せて退く」 (round2_s3) | hp=13 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=1 cover=True alarm=False post=wall time=day
- 方針=None 審判=retreat [L1,L7+gap] hp<=19,potion=false,allies>=2 「重傷で薬が無い、門は味方に任せて退く」 (round2_s3) | hp=19 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=0 cover=False alarm=False post=gate time=day
### group_alarm_unclear
- 方針=None 審判=hold_position [gap] arrows=0,distance>=2,enemy=goblin 「矢が無く隣接前なので門で迎え撃つ構え」 (round2_s2) | hp=92 enemy=goblin distance=2 enemy_count=3 enemy_hp=10 allies=2 potion=False arrows=0 cover=False alarm=False post=gate time=day
- 方針=None 審判=hold_position [L5+gap] enemy=goblin,allies>=3,arrows=0 「ゴブリン三体に味方三人、深刻ではなく持ち場で待つ」 (round2_s3) | hp=99 enemy=goblin distance=11 enemy_count=3 enemy_hp=100 allies=3 potion=False arrows=0 cover=True alarm=False post=wall time=day
- 方針=None 審判=melee_attack [L2] distance=1,enemy_hp<=10 「隣接する瀕死のゴブリンを近接で倒す」 (round1_s3) | hp=96 enemy=goblin distance=1 enemy_count=3 enemy_hp=10 allies=3 potion=False arrows=7 cover=True alarm=False post=gate time=day
- 方針=None 審判=raise_alarm [L2,L5,L6+gap] alarm=false,enemy_count>=3,time=night 「夜にゴブリン三体、遠いうちに警報」 (round2_s1) | hp=90 enemy=goblin distance=7 enemy_count=3 enemy_hp=80 allies=1 potion=True arrows=13 cover=True alarm=False post=wall time=night
- 方針=None 審判=shoot [L2] distance>=12,arrows>=2,allies>=3 「遠いゴブリンを射る、味方も多く警報は不要」 (round1_s3) | hp=38 enemy=goblin distance=12 enemy_count=3 enemy_hp=50 allies=3 potion=False arrows=2 cover=True alarm=False post=gate time=night
- 方針=None 審判=shoot [L2,L5+gap] enemy=goblin,distance>=2,arrows=19 「弱ったゴブリンは深刻な脅威でなく射れば足りる」 (round2_s2) | hp=92 enemy=goblin distance=10 enemy_count=3 enemy_hp=20 allies=2 potion=False arrows=19 cover=False alarm=False post=gate time=day
### mage_no_arrows
- 方針=None 審判=melee_attack [L4+gap] enemy=mage,arrows=0,hp>=90 「矢がなく体力十分、魔術師へ詰めて早く斬る」 (round1_s1) | hp=91 enemy=mage distance=2 enemy_count=1 enemy_hp=60 allies=0 potion=False arrows=0 cover=False alarm=True post=wall time=night
- 方針=None 審判=melee_attack [L2,L4+gap] enemy=mage,distance<=2,arrows=0 「矢が無いので二マス先の魔術師に斬り込む」 (round2_s1) | hp=60 enemy=mage distance=2 enemy_count=2 enemy_hp=50 allies=2 potion=True arrows=0 cover=False alarm=True post=corridor time=day
- 方針=None 審判=take_cover [gap] enemy=mage,arrows=0,cover=true 「矢が無く魔術師は遠いので遮蔽で呪文を避ける」 (round2_s1) | hp=75 enemy=mage distance=6 enemy_count=1 enemy_hp=50 allies=3 potion=False arrows=0 cover=True alarm=True post=corridor time=day
- 方針=None 審判=take_cover [gap] enemy=mage,arrows=0,cover=true 「矢が無く魔術師に届かぬので遮蔽で呪文を避ける」 (round2_s2) | hp=81 enemy=mage distance=5 enemy_count=2 enemy_hp=10 allies=0 potion=False arrows=0 cover=True alarm=True post=gate time=day
### hurt_vs_alarm
- 方針=None 審判=drink_potion [L1,L5+gap] hp<=14,potion=true,distance=1 「瀕死でトロルが隣接、警報より先に回復薬を飲む」 (round2_s3) | hp=14 enemy=troll distance=1 enemy_count=1 enemy_hp=10 allies=0 potion=True arrows=3 cover=False alarm=False post=corridor time=day
- 方針=None 審判=raise_alarm [L1,L5+gap] alarm=false,enemy=troll,distance>=12 「敵はまだ遠い、薬より先に警報で城へ知らせる」 (round1_s3) | hp=17 enemy=troll distance=12 enemy_count=4 enemy_hp=10 allies=0 potion=True arrows=1 cover=True alarm=False post=wall time=day
- 方針=None 審判=raise_alarm [L1,L5+gap] alarm=false,enemy=troll,distance>=10 「トロルはまだ遠く、退く前に一度警報を鳴らす」 (round2_s2) | hp=10 enemy=troll distance=10 enemy_count=3 enemy_hp=60 allies=2 potion=False arrows=4 cover=False alarm=False post=corridor time=night
- 方針=None 審判=raise_alarm [L1,L3,L5+gap] alarm=false,enemy=troll,distance>=5 「トロルはまだ遠い、退く前に警報を鳴らす」 (round2_s3) | hp=13 enemy=troll distance=5 enemy_count=1 enemy_hp=70 allies=0 potion=False arrows=15 cover=True alarm=False post=gate time=day

## 訊き直した状態(同じ状態を会話 3 本以上に訊いた。8 件のうち票が割れたもの 2 件)
- 票 {'hold_position': 2, 'retreat': 2} | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=True alarm=False post=gate time=night | hold_position「深手だが敵はなく、夜の門を空けず持ち場に留まる」 / retreat「深手で薬が無いので敵のいない今退く」 / retreat「重傷で薬も無いので退いて立て直す」 / hold_position「傷は深いが脅威が無く、門を空けられないので留まる」
- 票 {'shoot': 3, 'retreat': 1} | hp=31 enemy=goblin distance=9 enemy_count=3 enemy_hp=40 allies=1 potion=False arrows=5 cover=False alarm=True post=wall time=night | shoot「手負いだが敵は遠く、射るだけなら危険は小さい」 / retreat「深手で薬が無い夜なので射るより退く」 / shoot「城壁から遠いゴブリンを射る」 / shoot「敵は遠く警報済み、まだ射って戦える傷と見る」

## 根拠が gap に偏り、答えが割れている枝(輪が同じ状態を複数の会話に訊き直している。会話の癖か、状態の違いかは、訊き直しの票で分かる)
- 枝 hp_ambiguous: 審判の答え {'retreat': 19, 'hold_position': 5, 'shoot': 5, 'raise_alarm': 3, 'drink_potion': 8}
- 枝 no_arrows_cover: 審判の答え {'hold_position': 18, 'take_cover': 8}
- 枝 mage_no_arrows: 審判の答え {'melee_attack': 2, 'take_cover': 2}
- 枝 troll_alarm_raised: 審判の答え {'shoot': 5, 'take_cover': 4, 'hold_position': 1, 'retreat': 3, 'melee_attack': 2}
- 枝 mage_alarm_unclear: 審判の答え {'raise_alarm': 11, 'shoot': 5, 'melee_attack': 4}
- 枝 orc_alarm_unclear: 審判の答え {'raise_alarm': 7, 'melee_attack': 1, 'shoot': 4}
- 枝 hurt_vs_alarm: 審判の答え {'raise_alarm': 3, 'drink_potion': 1}
- 枝 hurt_no_threat: 審判の答え {'retreat': 10, 'hold_position': 2}
- 枝 group_alarm_unclear: 審判の答え {'melee_attack': 1, 'shoot': 2, 'raise_alarm': 1, 'hold_position': 2}

## 出力
`/home/claude/sekizui/jit/auto_runs/r2/policies/b2.py` に書く。書いたら「完了」とだけ返す。