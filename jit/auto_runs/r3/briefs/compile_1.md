# 翻訳の依頼 — 走り r3、第 1 版

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

- 追補をそのまま読んだ枝は、例が少なくても答えてよい(門は、その枝のラベルつきの状態が全部、同じ行動の追補の条件に入るかを確かめる)。

## いまの方針(c0)
```python
"""走り r2 の方針、第 0 版(b0)。

この版で変えたこと
    最初の版。審判のラベルはまだ 0 件・会話 0 本なので、枝はすべて
    規律 (a)「指示文をそのまま読んだ規則」だけで立てた。例からの閾値は無い。
    指示文の読みが割れうる所は、名前を付けた番人で棄権にしてある。

根拠(件数 0 件・会話 0 本。審判の決め手はまだ無い。以下は指示文の行)
    hurt_drink       L1  ひどく傷つき(hp<=20)、回復薬あり → drink_potion
    hurt_retreat     L1  ひどく傷つき(hp<=20)、回復薬なし、敵あり → retreat
    troll_alarm      L5+L3  トロル(一人で相手にできない=深刻な脅威)、警報未 → raise_alarm
    melee_adjacent   L2  隣接(distance 1)のゴブリン/オーク → melee_attack
    shoot_far        L2  離れた(distance>=2)ゴブリン/オーク、矢あり → shoot
    mage_melee       L2+L4  隣接の魔術師(警報済み) → melee_attack
    mage_shoot       L2+L4  離れた魔術師(警報済み)、矢あり → shoot
    no_threat_hold   L7  敵なし、傷は浅い(hp>=50) → hold_position

    「ひどく傷ついている」の読み: hp<=20 は明らかにひどい、hp>=50 は明らかに
    ひどくない、とだけ置いた。21〜49 は指示文から読めないので、hp が答えを
    左右する所では棄権する(hp_ambiguous)。

棄権の番人(割れうる所、輪が審判に訊く所)
    hp_ambiguous          21<=hp<=49 で L1 が効くか読めない
    hurt_vs_alarm         ひどい傷とトロル・警報未が重なる(L1 と L5 の順が読めない)
    hurt_no_threat        ひどい傷・薬なし・敵なし(L1 の退くと L7 の持ち場が衝突)
    troll_alarm_raised    警報済みのトロル(退く/遮蔽/射る/味方と戦う が読めない)
    mage_alarm_unclear    警報未の魔術師(L4 の即撃と L5 の警報のどちらか)
    orc_alarm_unclear     警報未のオーク(深刻な脅威か読めない)
    group_alarm_unclear   警報未で敵が複数(深刻な脅威か読めない)
    many_enemies          警報済みでも敵 3 以上(無駄死にしない L0 と L2 の衝突)
    night_cover_far       夜・離れた敵・遮蔽あり(L6 の用心が take_cover を指すか)
    no_arrows_far         離れた敵で矢が 0(L2 が行動を定めない)
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

# 「ひどく傷ついている」の、指示文から明らかに言える側だけ
_HURT_MAX = 20      # これ以下は明らかにひどい
_FINE_MIN = 50      # これ以上は明らかにひどくない


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
    potion = s["potion"]
    arrows = s["arrows"]
    cover = s["cover"]
    alarm = s["alarm"]
    night = s["time"] == "night"

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

    # ここから先は hp>=50(明らかにひどくない)

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
        if enemy == "mage":
            return (None, "mage_alarm_unclear")
        if enemy == "orc":
            return (None, "orc_alarm_unclear")
        if count >= 2:
            return (None, "group_alarm_unclear")
        # 単独のゴブリンは深刻な脅威ではない → L2 へ
    elif count >= 3:
        return (None, "many_enemies")

    # --- L2 (+ L4 魔術師) ---
    if dist == 1:
        if enemy == "mage":
            return ("melee_attack", "mage_melee")
        return ("melee_attack", "melee_adjacent")

    # 離れている(distance>=2)
    if arrows <= 0:
        return (None, "no_arrows_far")
    if night and cover:
        return (None, "night_cover_far")
    if enemy == "mage":
        return ("shoot", "mage_shoot")
    return ("shoot", "shoot_far")

```

## 熱さの帳簿(審判のラベル 120 件、会話 3 本を、いまの方針の枝ごとに数えた)

| 枝 | 件数 | 会話 | 方針の答え | 一致 | 会話の多数が方針と同じ | 審判の答え | 根拠 | 決め手(多い順) |
|---|---|---|---|---|---|---|---|---|
| hp_ambiguous | 36 | 3 | None | -/- | -/3 | {'hold_position': 17, 'retreat': 3, 'shoot': 5, 'raise_alarm': 4, 'take_cover': 2, 'melee_attack': 2, 'drink_potion': 3} | L7 16, L2 13, L1 12; gap 20 | enemy=none 17, potion=false 4, alarm=false 4, hp>=40 3 |
| no_threat_hold | 13 | 3 | hold_position | 13/13 | 3/3 | {'hold_position': 13} | L7 13 | enemy=none 13 |
| orc_alarm_unclear | 10 | 3 | None | -/- | -/3 | {'shoot': 1, 'raise_alarm': 7, 'melee_attack': 2} | L2 8, L5 8, L6 4; gap 7 | alarm=false 7, allies=0 4, enemy_count>=5 2, time=night 2 |
| no_arrows_far | 9 | 3 | None | -/- | -/3 | {'hold_position': 8, 'melee_attack': 1} | L4 1; gap 9 | arrows=0 9, distance>=2 3, distance>=7 2, enemy=mage 1 |
| many_enemies | 8 | 3 | None | -/- | -/3 | {'shoot': 6, 'melee_attack': 2} | L2 8 | distance>=2 3, arrows>=1 3, distance>=6 3, distance=1 2 |
| mage_alarm_unclear | 7 | 3 | None | -/- | -/3 | {'raise_alarm': 4, 'shoot': 2, 'melee_attack': 1} | L4 7, L5 7, L2 2; gap 6 | enemy=mage 5, alarm=false 4, enemy_count>=4 2, arrows=0 1 |
| group_alarm_unclear | 6 | 3 | None | -/- | -/3 | {'raise_alarm': 3, 'shoot': 2, 'melee_attack': 1} | L5 3, L2 3, L6 2; gap 1 | alarm=false 3, enemy_count>=3 1, allies=0 1, enemy_count>=5 1 |
| shoot_far | 6 | 2 | shoot | 6/6 | 2/2 | {'shoot': 6} | L2 6 | distance>=2 4, arrows>=1 4, distance>=8 1, arrows>=3 1 |
| night_cover_far | 5 | 3 | None | -/- | -/3 | {'shoot': 5} | L2 5 | distance>=2 1, arrows>=1 1, distance>=9 1, arrows>=13 1 |
| troll_alarm_raised | 5 | 3 | None | -/- | -/3 | {'shoot': 2, 'take_cover': 2, 'hold_position': 1} | L3 5, L2 3, L6 2; gap 5 | enemy=troll 2, allies=0 2, cover=true 2, distance>=4 1 |
| melee_adjacent | 4 | 3 | melee_attack | 4/4 | 3/3 | {'melee_attack': 4} | L2 4 | distance<=1 2, distance=1 2, hp>=86 1, enemy_hp<=10 1 |
| troll_alarm | 3 | 2 | raise_alarm | 3/3 | 2/2 | {'raise_alarm': 3} | L3 3, L5 3; gap 1 | enemy=troll 3, alarm=false 3, allies=0 1, arrows=0 1 |
| hurt_no_threat | 3 | 1 | None | -/- | -/1 | {'retreat': 3} | L7 3, L1 3; gap 3 | potion=false 3, hp<=15 2, allies>=2 2, hp<=14 1 |
| mage_shoot | 2 | 2 | shoot | 2/2 | 2/2 | {'shoot': 2} | L4 2, L2 2 | enemy=mage 2, distance>=6 1, arrows>=7 1, distance>=2 1 |
| hurt_drink | 1 | 1 | drink_potion | 1/1 | 1/1 | {'drink_potion': 1} | L1 1 | hp<=30 1, potion=true 1, enemy=none 1 |
| hurt_retreat | 1 | 1 | retreat | 1/1 | 1/1 | {'retreat': 1} | L1 1 | hp<=30 1, potion=false 1 |
| hurt_vs_alarm | 1 | 1 | None | -/- | -/1 | {'raise_alarm': 1} | L1 1, L5 1; gap 1 | alarm=false 1, enemy=troll 1, distance>=12 1 |

## 食い違いと棄権の例(全部。[根拠] 決め手 「理由」 会話)
### hp_ambiguous
- 方針=None 審判=drink_potion [L1,L2+gap] hp<=21,potion=true 「重傷なので隣の敵より先に回復薬を飲む」 (round1_s2) | hp=21 enemy=goblin distance=1 enemy_count=2 enemy_hp=20 allies=3 potion=True arrows=6 cover=True alarm=False post=corridor time=day
- 方針=None 審判=drink_potion [L1,L2+gap] hp<=31,potion=true,distance>=12 「深手で敵はまだ遠い、今のうちに回復薬を飲む」 (round1_s2) | hp=31 enemy=orc distance=12 enemy_count=2 enemy_hp=30 allies=0 potion=True arrows=10 cover=False alarm=True post=wall time=day
- 方針=None 審判=drink_potion [L1] hp<=26,potion=true,enemy=none 「重傷で敵のいない今、回復薬を飲む」 (round1_s3) | hp=26 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=True arrows=2 cover=True alarm=True post=wall time=day
- 方針=None 審判=hold_position [L7] enemy=none,hp>=40 「敵影なし、体力も半分近くあり持ち場を守る」 (round1_s1) | hp=48 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=True arrows=18 cover=True alarm=True post=wall time=day
- 方針=None 審判=hold_position [L0,L7+gap] enemy=none,post=gate 「深手だが敵はなく、夜の門を空けず持ち場に留まる」 (round1_s1) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=True alarm=False post=gate time=night
- 方針=None 審判=hold_position [L7] enemy=none 「脅威が無いので持ち場を守る」 (round1_s1) | hp=37 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=8 cover=True alarm=False post=corridor time=night
- 方針=None 審判=hold_position [L7] enemy=none 「脅威が無いので持ち場を守る」 (round1_s1) | hp=35 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=16 cover=False alarm=False post=gate time=night
- 方針=None 審判=hold_position [gap] arrows=0,distance>=2 「矢がなく届かない、門で寄ってくるのを待つ」 (round1_s1) | hp=48 enemy=goblin distance=2 enemy_count=2 enemy_hp=100 allies=2 potion=False arrows=0 cover=False alarm=True post=gate time=day
- 方針=None 審判=hold_position [L7] enemy=none 「脅威が無いので持ち場を守る」 (round1_s1) | hp=41 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=4 cover=False alarm=True post=corridor time=day
- 方針=None 審判=hold_position [L7] enemy=none 「脅威が無いので持ち場を守る」 (round1_s1) | hp=49 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=13 cover=False alarm=False post=corridor time=day
- 方針=None 審判=hold_position [L7] enemy=none 「脅威が無く重傷でもないので持ち場を守る」 (round1_s2) | hp=48 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=3 cover=True alarm=False post=gate time=night
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp>=45 「脅威が無くまだ深手ではない、薬は温存し持ち場へ」 (round1_s2) | hp=45 enemy=none distance=None enemy_count=0 enemy_hp=None allies=3 potion=True arrows=1 cover=True alarm=False post=gate time=day
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp>=44 「脅威が無くまだ深手ではない、薬は温存し持ち場へ」 (round1_s2) | hp=44 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=True arrows=19 cover=False alarm=False post=gate time=day
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp>=40 「脅威が無くまだ深手ではない、薬は温存し持ち場へ」 (round1_s2) | hp=40 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=True arrows=4 cover=True alarm=False post=corridor time=night
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp>=42 「敵がいないので退く必要はなく持ち場を守る」 (round1_s2) | hp=42 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=0 cover=False alarm=False post=corridor time=night
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp>=39 「敵がいないので退く必要はなく持ち場を守る」 (round1_s2) | hp=39 enemy=none distance=None enemy_count=0 enemy_hp=None allies=3 potion=False arrows=8 cover=False alarm=False post=wall time=day
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,allies=0,hp>=30 「敵も代わりもいない、体力30なら門に残る」 (round1_s3) | hp=30 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=0 cover=False alarm=False post=gate time=night
- 方針=None 審判=hold_position [L7] enemy=none 「脅威が無く体力も保っているので持ち場を守る」 (round1_s3) | hp=45 enemy=none distance=None enemy_count=0 enemy_hp=None allies=3 potion=True arrows=20 cover=True alarm=False post=gate time=night
- 方針=None 審判=hold_position [L7] enemy=none 「脅威が無いので持ち場を守る」 (round1_s3) | hp=38 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=10 cover=True alarm=False post=gate time=night
- 方針=None 審判=hold_position [L7] enemy=none,hp>=46 「重傷ではなく敵もいない、薬は温存し持ち場に」 (round1_s3) | hp=46 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=True arrows=2 cover=False alarm=True post=gate time=day
- 方針=None 審判=melee_attack [L2+gap] distance<=1,hp>=40,allies>=3 「隣接の小鬼、体力はまだ持ち味方も多いので斬る」 (round1_s1) | hp=40 enemy=goblin distance=1 enemy_count=2 enemy_hp=70 allies=3 potion=True arrows=13 cover=True alarm=False post=wall time=night
- 方針=None 審判=melee_attack [L2] distance=1,enemy_hp<=20 「隣接した弱ったオークを近接で仕留める」 (round1_s3) | hp=39 enemy=orc distance=1 enemy_count=1 enemy_hp=20 allies=0 potion=False arrows=18 cover=True alarm=True post=wall time=day
- 方針=None 審判=raise_alarm [L4,L5+gap] enemy=mage,alarm=false,distance>=10 「深手だが魔術師はまだ遠い、先に警報を鳴らす」 (round1_s1) | hp=28 enemy=mage distance=10 enemy_count=2 enemy_hp=80 allies=2 potion=True arrows=10 cover=False alarm=False post=wall time=night
- 方針=None 審判=raise_alarm [L2,L5+gap] alarm=false,enemy_count>=4,allies=0 「単独で4体に迫られ警報未発、まず援軍を呼ぶ」 (round1_s2) | hp=41 enemy=goblin distance=2 enemy_count=4 enemy_hp=90 allies=0 potion=False arrows=8 cover=False alarm=False post=gate time=day
- 方針=None 審判=raise_alarm [L2,L5,L6+gap] alarm=false,enemy_count>=5,time=night 「夜にオーク5体、射るより先に警報を鳴らす」 (round1_s3) | hp=47 enemy=orc distance=3 enemy_count=5 enemy_hp=100 allies=2 potion=False arrows=18 cover=True alarm=False post=wall time=night
- 方針=None 審判=raise_alarm [L2,L5,L6+gap] alarm=false,enemy_count>=5,time=night 「夜にオーク5体、斬り合うより警報が先」 (round1_s3) | hp=45 enemy=orc distance=1 enemy_count=5 enemy_hp=30 allies=1 potion=False arrows=4 cover=False alarm=False post=wall time=night
- 方針=None 審判=retreat [L1,L3+gap] hp<=30,potion=false,enemy=troll 「瀕死で薬なし、隣にトロルがいるので警報より退く」 (round1_s1) | hp=23 enemy=troll distance=1 enemy_count=3 enemy_hp=10 allies=0 potion=False arrows=14 cover=True alarm=False post=corridor time=day
- 方針=None 審判=retreat [L1] hp<=30,potion=false 「深手で薬も矢もないので退く」 (round1_s1) | hp=23 enemy=orc distance=6 enemy_count=2 enemy_hp=40 allies=2 potion=False arrows=0 cover=False alarm=False post=corridor time=day
- 方針=None 審判=retreat [L1,L2+gap] hp<=22,potion=false,allies=0 「重傷で薬も味方も無い、射たずに退く」 (round1_s2) | hp=22 enemy=goblin distance=2 enemy_count=2 enemy_hp=100 allies=0 potion=False arrows=4 cover=False alarm=False post=gate time=day
- 方針=None 審判=shoot [L2+gap] distance>=2,arrows>=1,hp>=31 「手負いだが敵は遠く、射るだけなら危険は小さい」 (round1_s1) | hp=31 enemy=goblin distance=9 enemy_count=3 enemy_hp=40 allies=1 potion=False arrows=5 cover=False alarm=True post=wall time=night
- 方針=None 審判=shoot [L2] distance>=9,arrows>=2 「オークはまだ遠く矢も残るので射る」 (round1_s2) | hp=49 enemy=orc distance=9 enemy_count=1 enemy_hp=100 allies=1 potion=False arrows=2 cover=True alarm=True post=gate time=day
- 方針=None 審判=shoot [L2,L4] enemy=mage,distance>=9,arrows>=4 「遠くの魔術師を矢で早く仕留めにかかる」 (round1_s3) | hp=48 enemy=mage distance=9 enemy_count=3 enemy_hp=40 allies=0 potion=True arrows=4 cover=True alarm=True post=corridor time=night
- 方針=None 審判=shoot [L2] distance>=2,arrows>=7 「隣接前のゴブリンを矢で射る」 (round1_s3) | hp=47 enemy=goblin distance=2 enemy_count=2 enemy_hp=100 allies=0 potion=True arrows=7 cover=True alarm=False post=gate time=night
- 方針=None 審判=shoot [L2] distance>=12,arrows>=2,allies>=3 「遠いゴブリンを射る、味方も多く警報は不要」 (round1_s3) | hp=38 enemy=goblin distance=12 enemy_count=3 enemy_hp=50 allies=3 potion=False arrows=2 cover=True alarm=False post=gate time=night
- 方針=None 審判=take_cover [L6+gap] arrows=0,time=night,cover=true 「夜に単独で矢もない、遮蔽に隠れて様子を見る」 (round1_s1) | hp=44 enemy=goblin distance=11 enemy_count=3 enemy_hp=30 allies=0 potion=True arrows=0 cover=True alarm=True post=wall time=night
- 方針=None 審判=take_cover [gap] hp<=42,potion=false,arrows=0 「矢も薬も無く体力半分以下、遮蔽で門に踏み止まる」 (round1_s2) | hp=42 enemy=goblin distance=4 enemy_count=3 enemy_hp=60 allies=3 potion=False arrows=0 cover=True alarm=True post=gate time=day
### orc_alarm_unclear
- 方針=None 審判=melee_attack [L2,L5,L6+gap] distance=1,hp>=91,allies>=2 「味方2人と体力十分、隣接オークを斬る」 (round1_s3) | hp=91 enemy=orc distance=1 enemy_count=2 enemy_hp=60 allies=2 potion=True arrows=0 cover=False alarm=False post=gate time=night
- 方針=None 審判=melee_attack [L2] distance=1 「隣接したオークと近接で戦う」 (round1_s3) | hp=77 enemy=orc distance=1 enemy_count=1 enemy_hp=50 allies=1 potion=True arrows=0 cover=False alarm=False post=corridor time=day
- 方針=None 審判=raise_alarm [L5+gap] enemy_count>=5,allies=0,alarm=false 「単独でオーク五体、斬るより先に警報を鳴らす」 (round1_s1) | hp=82 enemy=orc distance=1 enemy_count=5 enemy_hp=70 allies=0 potion=False arrows=3 cover=True alarm=False post=corridor time=day
- 方針=None 審判=raise_alarm [L2,L5+gap] alarm=false,enemy_count>=5 「5体の敵に警報未発、射るより先に警報を鳴らす」 (round1_s2) | hp=72 enemy=orc distance=3 enemy_count=5 enemy_hp=90 allies=1 potion=True arrows=18 cover=True alarm=False post=corridor time=day
- 方針=None 審判=raise_alarm [L2,L5,L6+gap] alarm=false,allies=0,time=night 「夜の門で単独、オーク2体に先に警報を鳴らす」 (round1_s2) | hp=82 enemy=orc distance=1 enemy_count=2 enemy_hp=80 allies=0 potion=False arrows=3 cover=False alarm=False post=gate time=night
- 方針=None 審判=raise_alarm [L2,L5,L6+gap] time=night,alarm=false,enemy=orc 「夜に門へオーク2体、用心して先に警報」 (round1_s3) | hp=61 enemy=orc distance=6 enemy_count=2 enemy_hp=40 allies=1 potion=False arrows=9 cover=False alarm=False post=gate time=night
- 方針=None 審判=raise_alarm [L5] alarm=false,enemy_count>=4,arrows=0 「オーク4体で警報未発、矢も無いので鳴らす」 (round1_s3) | hp=83 enemy=orc distance=6 enemy_count=4 enemy_hp=20 allies=1 potion=False arrows=0 cover=False alarm=False post=gate time=day
- 方針=None 審判=raise_alarm [L2,L5+gap] alarm=false,enemy_count>=3,allies=0 「単独でオーク3体、射るより先に警報」 (round1_s3) | hp=84 enemy=orc distance=4 enemy_count=3 enemy_hp=50 allies=0 potion=False arrows=7 cover=True alarm=False post=gate time=day
- 方針=None 審判=raise_alarm [L2,L5,L6+gap] alarm=false,enemy_count>=3,allies=0 「夜に単独でオーク3体、射るより先に警報」 (round1_s3) | hp=79 enemy=orc distance=4 enemy_count=3 enemy_hp=80 allies=0 potion=False arrows=2 cover=True alarm=False post=gate time=night
- 方針=None 審判=shoot [L2] distance>=2,arrows>=1 「遠いオーク一体、矢が十分あるので射る」 (round1_s1) | hp=63 enemy=orc distance=6 enemy_count=1 enemy_hp=70 allies=1 potion=True arrows=19 cover=True alarm=False post=gate time=day
### no_arrows_far
- 方針=None 審判=hold_position [gap] arrows=0,distance>=2 「矢がなく届かないので門で迎え撃つ構え」 (round1_s1) | hp=93 enemy=goblin distance=3 enemy_count=1 enemy_hp=100 allies=0 potion=True arrows=0 cover=False alarm=True post=gate time=day
- 方針=None 審判=hold_position [gap] arrows=0,distance>=2 「矢がなく敵も遠い、味方と通路を固めて待つ」 (round1_s1) | hp=91 enemy=orc distance=6 enemy_count=1 enemy_hp=90 allies=3 potion=True arrows=0 cover=True alarm=True post=corridor time=day
- 方針=None 審判=hold_position [gap] arrows=0,distance>=2 「矢がなく敵は遠い、持ち場で待つ」 (round1_s1) | hp=71 enemy=goblin distance=10 enemy_count=2 enemy_hp=80 allies=1 potion=False arrows=0 cover=True alarm=True post=corridor time=day
- 方針=None 審判=hold_position [gap] arrows=0,distance>=8 「矢が無く敵は遠い、持ち場でオークを迎え撃つ」 (round1_s2) | hp=91 enemy=orc distance=8 enemy_count=1 enemy_hp=50 allies=0 potion=False arrows=0 cover=True alarm=True post=wall time=day
- 方針=None 審判=hold_position [gap] arrows=0,distance>=3,enemy=goblin 「矢が無く未接近の弱い敵、持ち場で待ち構える」 (round1_s2) | hp=71 enemy=goblin distance=3 enemy_count=1 enemy_hp=20 allies=1 potion=True arrows=0 cover=False alarm=False post=wall time=day
- 方針=None 審判=hold_position [gap] arrows=0,distance>=7,alarm=true 「矢は無いが敵は遠く警報済み、持ち場で援軍を待つ」 (round1_s2) | hp=52 enemy=orc distance=7 enemy_count=2 enemy_hp=70 allies=0 potion=False arrows=0 cover=False alarm=True post=wall time=day
- 方針=None 審判=hold_position [gap] arrows=0,distance>=6,cover=false 「矢も遮蔽も無い、持ち場でゴブリンを待ち受ける」 (round1_s3) | hp=90 enemy=goblin distance=6 enemy_count=1 enemy_hp=90 allies=1 potion=False arrows=0 cover=False alarm=True post=wall time=night
- 方針=None 審判=hold_position [gap] arrows=0,distance>=7 「矢が無く敵は遠い、持ち場で待ち受ける」 (round1_s3) | hp=86 enemy=goblin distance=7 enemy_count=1 enemy_hp=60 allies=3 potion=True arrows=0 cover=True alarm=False post=corridor time=day
- 方針=None 審判=melee_attack [L4+gap] enemy=mage,arrows=0,hp>=90 「矢がなく体力十分、魔術師へ詰めて早く斬る」 (round1_s1) | hp=91 enemy=mage distance=2 enemy_count=1 enemy_hp=60 allies=0 potion=False arrows=0 cover=False alarm=True post=wall time=night
### many_enemies
- 方針=None 審判=melee_attack [L2] distance=1,enemy_hp<=10 「隣接した瀕死のゴブリンを近接で討つ」 (round1_s2) | hp=99 enemy=goblin distance=1 enemy_count=3 enemy_hp=10 allies=0 potion=False arrows=13 cover=True alarm=True post=corridor time=night
- 方針=None 審判=melee_attack [L2] distance=1,arrows=0 「隣接したゴブリンと近接で戦う」 (round1_s3) | hp=94 enemy=goblin distance=1 enemy_count=3 enemy_hp=50 allies=2 potion=False arrows=0 cover=True alarm=True post=corridor time=day
- 方針=None 審判=shoot [L2] distance>=2,arrows>=1 「警報済み、遠い小鬼に矢を射かける」 (round1_s1) | hp=71 enemy=goblin distance=8 enemy_count=3 enemy_hp=90 allies=3 potion=False arrows=17 cover=False alarm=True post=wall time=day
- 方針=None 審判=shoot [L2] distance>=2,arrows>=1 「警報済み、離れた小鬼に残りの矢を射る」 (round1_s1) | hp=86 enemy=goblin distance=3 enemy_count=4 enemy_hp=100 allies=0 potion=True arrows=2 cover=True alarm=True post=gate time=day
- 方針=None 審判=shoot [L2] distance>=2,arrows>=1 「警報済み、離れた小鬼に矢を射る」 (round1_s1) | hp=58 enemy=goblin distance=5 enemy_count=3 enemy_hp=80 allies=3 potion=True arrows=9 cover=True alarm=True post=corridor time=day
- 方針=None 審判=shoot [L2] distance>=6,arrows>=18 「敵は離れていて矢が十分あるので射る」 (round1_s2) | hp=85 enemy=goblin distance=6 enemy_count=4 enemy_hp=70 allies=0 potion=False arrows=18 cover=True alarm=True post=gate time=day
- 方針=None 審判=shoot [L2] distance>=6,arrows>=2 「敵は離れていて矢が残るので射る」 (round1_s2) | hp=86 enemy=orc distance=6 enemy_count=4 enemy_hp=100 allies=2 potion=False arrows=2 cover=False alarm=True post=gate time=day
- 方針=None 審判=shoot [L2] distance>=6,arrows>=9 「離れたゴブリンの群れを矢で射る」 (round1_s3) | hp=84 enemy=goblin distance=6 enemy_count=4 enemy_hp=20 allies=1 potion=False arrows=9 cover=False alarm=True post=wall time=day
### mage_alarm_unclear
- 方針=None 審判=melee_attack [L2,L4,L5+gap] enemy=mage,distance=1,enemy_hp<=30 「隣の弱った魔術師を警報より先に仕留める」 (round1_s3) | hp=93 enemy=mage distance=1 enemy_count=1 enemy_hp=30 allies=1 potion=True arrows=0 cover=False alarm=False post=gate time=night
- 方針=None 審判=raise_alarm [L4,L5] enemy=mage,alarm=false,arrows=0 「魔術師が現れ未警報、矢もないので警報を鳴らす」 (round1_s1) | hp=89 enemy=mage distance=6 enemy_count=2 enemy_hp=80 allies=1 potion=False arrows=0 cover=False alarm=False post=corridor time=night
- 方針=None 審判=raise_alarm [L4,L5+gap] alarm=false,enemy_count>=4,allies=0 「魔術師含む4体に単独、まず警報で城に知らせる」 (round1_s2) | hp=74 enemy=mage distance=6 enemy_count=4 enemy_hp=30 allies=0 potion=True arrows=15 cover=False alarm=False post=gate time=day
- 方針=None 審判=raise_alarm [L4,L5+gap] alarm=false,enemy_count>=4,enemy_hp>=90 「魔術師は一射で倒せず4体・夜、先に警報」 (round1_s2) | hp=95 enemy=mage distance=6 enemy_count=4 enemy_hp=90 allies=2 potion=False arrows=6 cover=False alarm=False post=corridor time=night
- 方針=None 審判=raise_alarm [L2,L4,L5+gap] alarm=false,enemy=mage,arrows<=1 「矢1本では魔術師を仕留めきれず先に警報」 (round1_s3) | hp=71 enemy=mage distance=9 enemy_count=2 enemy_hp=70 allies=1 potion=True arrows=1 cover=True alarm=False post=wall time=day
- 方針=None 審判=shoot [L4,L5+gap] enemy=mage,enemy_count=1,arrows>=11 「魔術師単独なら警報より先に射て早く仕留める」 (round1_s2) | hp=84 enemy=mage distance=6 enemy_count=1 enemy_hp=40 allies=0 potion=True arrows=11 cover=True alarm=False post=gate time=day
- 方針=None 審判=shoot [L4,L5+gap] enemy=mage,enemy_hp<=10,arrows>=6 「瀕死の魔術師を一射で仕留められるので射る」 (round1_s2) | hp=54 enemy=mage distance=6 enemy_count=2 enemy_hp=10 allies=0 potion=False arrows=6 cover=False alarm=False post=wall time=day
### group_alarm_unclear
- 方針=None 審判=melee_attack [L2] distance=1,enemy_hp<=10 「隣接する瀕死のゴブリンを近接で倒す」 (round1_s3) | hp=96 enemy=goblin distance=1 enemy_count=3 enemy_hp=10 allies=3 potion=False arrows=7 cover=True alarm=False post=gate time=day
- 方針=None 審判=raise_alarm [L5,L6+gap] enemy_count>=3,allies=0,alarm=false 「夜に単独で小鬼三体、矢も一本なので先に警報」 (round1_s1) | hp=94 enemy=goblin distance=3 enemy_count=3 enemy_hp=60 allies=0 potion=False arrows=1 cover=False alarm=False post=wall time=night
- 方針=None 審判=raise_alarm [L5,L6] enemy_count>=5,alarm=false,time=night 「夜に小鬼五体、未警報なので警報を鳴らす」 (round1_s1) | hp=82 enemy=goblin distance=6 enemy_count=5 enemy_hp=100 allies=1 potion=False arrows=0 cover=False alarm=False post=gate time=night
- 方針=None 審判=raise_alarm [L5] alarm=false,enemy_count>=4,arrows=0 「ゴブリン4体が迫り警報未発、矢も無いので警報」 (round1_s2) | hp=100 enemy=goblin distance=3 enemy_count=4 enemy_hp=60 allies=1 potion=False arrows=0 cover=False alarm=False post=gate time=day
- 方針=None 審判=shoot [L2] distance>=2,arrows>=15,enemy=goblin 「隣接前のゴブリン2体、矢があるので射る」 (round1_s2) | hp=100 enemy=goblin distance=2 enemy_count=2 enemy_hp=40 allies=0 potion=False arrows=15 cover=True alarm=False post=gate time=night
- 方針=None 審判=shoot [L2] distance>=4,arrows>=4 「離れたゴブリンを矢で射る」 (round1_s3) | hp=70 enemy=goblin distance=4 enemy_count=2 enemy_hp=70 allies=2 potion=False arrows=4 cover=False alarm=False post=gate time=night
### night_cover_far
- 方針=None 審判=shoot [L2] distance>=2,arrows>=1 「弱った小鬼一体、離れているので射る」 (round1_s1) | hp=73 enemy=goblin distance=6 enemy_count=1 enemy_hp=10 allies=0 potion=False arrows=13 cover=True alarm=False post=wall time=night
- 方針=None 審判=shoot [L2] distance>=9,arrows>=13 「遠いゴブリン1体、矢があるので射る」 (round1_s2) | hp=94 enemy=goblin distance=9 enemy_count=1 enemy_hp=100 allies=2 potion=True arrows=13 cover=True alarm=True post=gate time=night
- 方針=None 審判=shoot [L2] distance>=3,arrows>=17 「離れたゴブリン1体、矢があるので射る」 (round1_s2) | hp=52 enemy=goblin distance=3 enemy_count=1 enemy_hp=60 allies=0 potion=True arrows=17 cover=True alarm=True post=corridor time=night
- 方針=None 審判=shoot [L2] distance>=8,arrows>=3 「離れたゴブリンに矢が残るので射る」 (round1_s3) | hp=65 enemy=goblin distance=8 enemy_count=2 enemy_hp=30 allies=3 potion=False arrows=3 cover=True alarm=True post=gate time=night
- 方針=None 審判=shoot [L2] distance>=4,arrows>=10,enemy_count=1 「離れたゴブリン1体を矢で射る」 (round1_s3) | hp=55 enemy=goblin distance=4 enemy_count=1 enemy_hp=70 allies=1 potion=False arrows=10 cover=True alarm=False post=wall time=night
### troll_alarm_raised
- 方針=None 審判=hold_position [L3+gap] arrows=0,distance>=12,allies>=3 「矢が無く敵は遠い、味方3人と門を固めて待つ」 (round1_s2) | hp=92 enemy=troll distance=12 enemy_count=5 enemy_hp=40 allies=3 potion=True arrows=0 cover=True alarm=True post=gate time=day
- 方針=None 審判=shoot [L2,L3+gap] distance>=4,arrows>=1,allies>=2 「味方がいて矢も多い、近づく前にトロルを射る」 (round1_s1) | hp=78 enemy=troll distance=4 enemy_count=3 enemy_hp=80 allies=2 potion=False arrows=20 cover=True alarm=True post=corridor time=night
- 方針=None 審判=shoot [L2,L3+gap] allies>=1,distance>=2,arrows>=14 「味方がいて間合いもある、トロルを矢で削る」 (round1_s3) | hp=86 enemy=troll distance=3 enemy_count=1 enemy_hp=80 allies=1 potion=False arrows=14 cover=False alarm=True post=gate time=day
- 方針=None 審判=take_cover [L2,L3,L6+gap] enemy=troll,allies=0,cover=true 「トロル含む4体に単独、夜なので射ずに遮蔽で門に留まる」 (round1_s2) | hp=99 enemy=troll distance=3 enemy_count=4 enemy_hp=30 allies=0 potion=False arrows=6 cover=True alarm=True post=gate time=night
- 方針=None 審判=take_cover [L3,L6+gap] enemy=troll,allies=0,cover=true 「単独でトロルに挑めず夜、遮蔽で援軍を待つ」 (round1_s2) | hp=95 enemy=troll distance=6 enemy_count=4 enemy_hp=40 allies=0 potion=False arrows=0 cover=True alarm=True post=corridor time=night
### hurt_no_threat
- 方針=None 審判=retreat [L1,L7+gap] hp<=15,potion=false,allies>=2 「重傷で薬も無い、門を味方に任せて退く」 (round1_s3) | hp=15 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=2 cover=False alarm=False post=gate time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=15,potion=false,allies>=2 「重傷で薬も無い、門を味方に任せて退く」 (round1_s3) | hp=15 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=0 cover=False alarm=True post=gate time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=14,potion=false,allies>=1 「重傷で薬も無い、門を味方に任せて退く」 (round1_s3) | hp=14 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=0 cover=True alarm=True post=gate time=day
### hurt_vs_alarm
- 方針=None 審判=raise_alarm [L1,L5+gap] alarm=false,enemy=troll,distance>=12 「敵はまだ遠い、薬より先に警報で城へ知らせる」 (round1_s3) | hp=17 enemy=troll distance=12 enemy_count=4 enemy_hp=10 allies=0 potion=True arrows=1 cover=True alarm=False post=wall time=day

## 根拠が gap に偏り、答えが割れている枝(輪が同じ状態を複数の会話に訊き直している。会話の癖か、状態の違いかは、訊き直しの票で分かる)
- 枝 hp_ambiguous: 審判の答え {'hold_position': 17, 'retreat': 3, 'shoot': 5, 'raise_alarm': 4, 'take_cover': 2, 'melee_attack': 2, 'drink_potion': 3}
- 枝 no_arrows_far: 審判の答え {'hold_position': 8, 'melee_attack': 1}
- 枝 orc_alarm_unclear: 審判の答え {'shoot': 1, 'raise_alarm': 7, 'melee_attack': 2}
- 枝 troll_alarm_raised: 審判の答え {'shoot': 2, 'take_cover': 2, 'hold_position': 1}
- 枝 mage_alarm_unclear: 審判の答え {'raise_alarm': 4, 'shoot': 2, 'melee_attack': 1}

## 出力
`/home/claude/sekizui/jit/auto_runs/r3/policies/c1.py` に書く。書いたら「完了」とだけ返す。