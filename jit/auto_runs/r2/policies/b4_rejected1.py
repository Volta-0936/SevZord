"""走り r2 の方針、第 4 版(b4)。

帳簿: 審判のラベル 436 件、会話 12 本(b3 の 9 本に round4_s1〜s3 を足した。以下 r1s1 … r4s3)。
b3 の答える枝を新しい帳簿で数え直すと、門の線を割るのは mage_no_arrows_cover の 3/4 = 75% だけ
(r4s3 の近接 1 件)。ほかは一致 80% 以上(最も低いのは troll_alone_cover のちょうど 4/5 = 80%)で、
別の答えを多数にした会話は多くて 1 本。新しい追補 A4・A5・A6 を入れ、帳簿の新しい会話で証拠が
揃った所に答えを足した。変えたのは次のとおり。

 1. 追補 A4(警報未・hp<=28・薬あり・魔術師・10 マス以上 → 警報より先に回復薬を飲む。規律 (a))。
    元の状態(hp28 魔術師 2 体 d10 ehp80 味方 2 薬あり 矢 10 夜・警報未)は b3 では番人
    wounded_alarm_unclear。会話 7 本に訊いて、飲む 5(r3s1 r3s3 r4s1 r4s2 r4s3。決め手 potion=true,
    distance>=10, hp<=28 / hp<=30。理由「重傷で魔術師はまだ遠い、まず回復薬で持ち直す」)、警報 2
    (r1s1 r3s2。決め手 enemy=mage, alarm=false, distance>=10)。別の答えを多数にした会話は 2 本で
    1/3 に届かないが、この状態だけで枝を作ると 5/7 = 71% で落ちる。飲む理由はどれも L1 の
    「傷ついていて薬があれば飲む」で、wounded_drink と同じ規則なので、hp 25〜28 の A4 は
    wounded_drink に入れた(b3 で A3 の元の状態を mage_first_shoot に残したのと同じ扱い)。
    wounded_drink は 6/6 から 11/13 = 85% の見込み。hp<=24 の A4 は元から hurt_drink(飲む)。
      a3_a4_conflict(番人、新): hp 25〜28 で A3 と A4 が重なる所(魔術師一体・ehp<=40・10 マス以上・
          矢 11 本以上)。射る・飲むのどちらも「警報より先に」で、例も無い。
      A2 と重なる所(夜・矢 0・味方 0・遮蔽・11 マス以上)は a2_hurt_conflict のまま。
 2. 追補 A5(警報済み・矢 0・味方 3 以上・敵 4 マス以上 → 遮蔽があっても持ち場を守る。規律 (a))。
    元の状態(hp42 ゴブリン 3 体 d4 味方 3 遮蔽あり 昼)は持ち場 3・遮蔽 1(r1s2)で、既に
    no_arrows_hold の中。昼のゴブリン・オークと、夜で遮蔽なしのゴブリン・オークは b3 でも
    no_arrows_hold なので答えは変わらない(A2 の時と同じ)。
      a5_hold(新しい枝): トロル → hold_position。b3 では番人 troll_alarm_raised。例 1 件
          (r1s2 hp92 d12 昼、持ち場、根拠 L3+gap、決め手 arrows=0, distance>=12, allies>=3、
          理由「矢が無く敵は遠い、味方3人と門を固めて待つ」)。夜で遮蔽ありは下の番人。
      a5_night_unclear(番人、新): 夜で遮蔽あり。b3 は L6 の night_no_arrows_cover(遮蔽 9/10)で、
          A5 の元の状態は昼。A1・A3 の夜と同じ形なので、答えず輪に回す。
      a5_mage_unclear(番人、新): 魔術師。L4(早く仕留める)とぶつかる。帳簿の例は r3s1 hp93 d12 の
          近接 1 件(gap、決め手 enemy=mage, arrows=0, hp>=90)で、持ち場の例は無い。
      a5_hurt_conflict(番人、新): hp<=32 の A5。L1 の飲む・退くとぶつかる(A2 と同じ扱い)。
 3. 追補 A6(敵なし・hp<=30・薬なし → 味方が 1 人以上なら退く、いなければ持ち場を守る)。
    帳簿は A6 より前のラベルで、b3 に書いたとおり会話ごとの癖で割れている。範囲を四つに分けて数えた。
      hp<=24・味方あり: hurt_handover 9/10、会話 3/4。A6 と同じ退くなので、そのまま(根拠に A6)。
      hp<=24・味方 0: A6 は持ち場。帳簿は持ち場 6 / 退く 9、持ち場を多数にした会話 2 本(r2s3 r3s3)、
          退く 6 本(r2s1 r2s2 r3s1 r3s2 r4s2 r4s3)。答えると 40%・会話の 6/8 が別の答えで門で
          落ちる。L1(なければ退く)ともぶつかる。番人 hurt_no_threat のまま。
      hp 25〜30・味方あり: A6 は退く。帳簿は退く 9 / 持ち場 6、退くの会話 4 本(r2s1 r2s3 r4s2 r4s3)、
          持ち場 2 本(r3s3 r4s1)。60%・会話のちょうど 1/3 が別の答え → 番人 wounded_no_threat。
      hp 25〜30・味方 0: A6 は持ち場。帳簿は持ち場 7 / 退く 8 / 遮蔽 1、持ち場の会話 6 本(r1s1 r1s3
          r2s3 r3s3 r4s1 r4s2)、退く 4 本(r2s1 r2s2 r3s2 r4s3)、r3s1 は同数。44% → 番人
          wounded_no_threat のまま。
    A6 の下での訊き直しが帳簿に揃えば、次の版で答えにする。
 4. hp 31〜32・薬なし・敵なし → hold_position(no_threat_hold に入れた。規則は L7)。b3 では
    wounded_no_threat。6 件・会話 6 本・持ち場 5/6 = 83%(規律 (b))。持ち場は r2s2 r2s3 r4s1 r4s2
    r4s3、決め手 enemy=none と hp>=31 / hp>=32、理由「重傷とまでは言えず脅威も無い」「体力32は
    重傷と見ず持ち場を守る」。退く 1 件は r2s1 hp32(決め手 hp<=33)。線 31 は A6 の hp<=30 の
    すぐ外で、A1 の hp>=31 と同じ。薬があれば wounded_drink が先(b3 のまま)。
    no_threat_hold は 68/69 の見込み。
 5. 新しい枝 wounded_retreat: hp 25〜30・薬なし・敵あり(警報未の深刻な脅威・A2・A5 の外)→ retreat。
    b3 では番人 hp_ambiguous。5 件・会話 4 本・退く 4/5 = 80%、別の答えの会話 1 本(規律 (b))。
    退くは r3s2 hp25(根拠 L1)、r4s2 hp28、r4s3 hp26(根拠 L1)・hp28。決め手は全件 potion=false と
    hp<=25 / <=26 / <=28、理由「重傷で回復薬が無いので退く」「弱った敵でも無理はしない」。
    外れる 1 件は r2s3 hp26 の射る(決め手 enemy_hp<=10、「瀕死のゴブリン、射って仕留める」)。
    線 30 は退くの最高 28 と射る hp32(r2s2)の間で、A6 の線、hurt_retreat の決め手 hp<=30 と同じ。
    hp 31〜32 は A1 の範囲か番人 hp_ambiguous のまま。
 6. 隣接のオーク 2 体・警報未・味方 2 以上 → melee_attack(melee_adjacent に通した。規則は L2)。
    b3 では番人 orc_alarm_unclear。5 件・会話 4 本(r1s3、r3s2、r4s1、r4s2 2 件)・一致 5/5
    (規律 (b))、根拠は 4 件が L2 だけ(gap なし)。決め手は全件 distance=1、ほかに allies>=2 /
    allies>=3、hp>=91 / hp>=66。理由「オークが隣接し味方も多いので近接で戦う」。昼 2 件・夜 3 件
    なので昼夜を問わない。味方 1 以下の隣接は b3 のまま(夜は orc_pair_night_alarm、昼の弱った
    オークは orc_pair_day_melee、残りは番人)。
 7. mage_no_arrows_cover を弱った魔術師で絞った。新しい帳簿で 3/4 = 75% になり門で落ちるため。
    外れた 1 件は r4s3 hp72 d3 ehp40 遮蔽あり夜・味方 0 の近接(根拠 L4,L6+gap、決め手 enemy=mage,
    arrows=0, enemy_hp<=40、理由「矢が無いので弱った魔術師に詰めて仕留める」)。審判の決め手の
    enemy_hp<=40(A3 の「体力 40% 以下」と同じ線)の魔術師は遮蔽に回さず、番人 mage_no_arrows へ。
    遮蔽の 3 件(r2s1 d6、r2s2 d5、r3s1 d7)は残る見込み。

熱さの帳簿を b4 で数え直した見込み(答える枝、件数・一致・会話)
    no_threat_hold             69  68/69  12 本   L7      敵なし・hp>=33、または hp 31〜32・薬なし → hold_position
    no_arrows_hold             47  46/47  12 本   gap+A5  離れた敵・矢 0・(遮蔽なし、または昼) → hold_position
    shoot_far                  42  41/42  11 本   L2      離れたゴブリン/オーク・矢あり → shoot
    horde_alarm                19  19/19   8 本   L5      警報未・敵 4 以上 → raise_alarm
    melee_adjacent             18  18/18   5 本以上 L2    隣接のゴブリン/オーク(オーク 2 体・味方 2 以上を足した) → melee_attack
    hurt_retreat               15  15/15   9 本   L1      hp<=24・薬なし・敵あり → retreat(A5 の範囲は番人へ)
    wounded_drink              13  11/13   7 本以上 L1+A4  hp 25〜32・薬あり、A4 の hp 25〜28 → drink_potion
    troll_alarm                10   9/10   6 本   L5+L3   トロル・警報未 → raise_alarm
    hurt_drink                 10  10/10   7 本   L1(+A4) hp<=24・薬あり → drink_potion
    hurt_handover              10   9/10   4 本   L1+L7+A6 hp<=24・薬なし・敵なし・味方あり → retreat
    night_no_arrows_cover     <=10  9/10 から A5 の分が抜ける  L6  離れた敵・矢 0・遮蔽あり・夜 → take_cover
    mage_first_shoot            8   7/8    6 本   L4+L2   警報未の魔術師・昼・2〜6 マス・敵 2 以下 → shoot
    mage_melee                  8   8/8    7 本   L2+L4   隣接の魔術師 → melee_attack
    wounded_alarm               8   8/8    7 本   L5+L1   hp 25〜32・薬なし・警報未の深刻な脅威・3 マス以上 → raise_alarm
    orc_pair_night_alarm        7   7/7    6 本   L5+L6   警報未のオーク 2 体・夜・味方 1 以下・ehp>25 → raise_alarm
    mage_no_arrows_alarm        6   6/6    3 本   L5+L4   警報未の魔術師・離れて矢 0 → raise_alarm
    mage_far_alarm              6   6/6    4 本   L5+L4   警報未の魔術師・7 マス以上(A3 の外) → raise_alarm
    troll_shoot_allies          5   5/5    4 本   L2+L3   警報済みトロル・味方あり・離れて矢あり → shoot
    troll_alone_cover           5   4/5    4 本   L3+L6   警報済みトロル・味方 0・離れて・遮蔽・夜 → take_cover
    mage_shoot                  5   5/5    4 本   L2+L4   離れた魔術師(警報済み)・矢あり → shoot
    wounded_retreat             5   4/5    4 本   L1      hp 25〜30・薬なし・敵あり → retreat(新)
    outnumbered_alarm           4   4/4    3 本   L5      警報未・敵 3・味方 0 → raise_alarm
    orc_pair_day_shoot          4   4/4    3 本   L2      警報未のオーク 2 体・昼・離れて矢あり → shoot
    orc_trio_alarm              4   4/4    3 本   L5      警報未のオーク 3 体・味方あり → raise_alarm
    mage_close_in               3   3/3    3 本   L4      警報済みの魔術師・2 マス・矢 0・遮蔽なし → melee_attack
    hurt_troll_alarm            3   3/3    3 本   L5+L3   hp<=24・トロル・警報未・3 マス以上 → raise_alarm
    troll_alone_retreat         3   3/3    3 本   L3      警報済みトロル・味方 0・隣接・夜 → retreat
    mage_night_alarm            3   3/3    2 本   L5+L6   警報未の魔術師・夜・2〜6 マス・敵 2 以下 → raise_alarm
    a1_shoot                    3   3/3    2 本   A1      hp>=31・敵 9 マス以上・矢あり・昼(条件は b3 のまま) → shoot
    mage_no_arrows_cover       <=3  全件一致      gap     警報済みの魔術師・3 マス以上・矢 0・遮蔽あり・ehp>40 → take_cover
    troll_melee_allies          2   2/2    2 本   L2+L3   警報済みトロル・味方あり・隣接 → melee_attack
    a5_hold                     1   1/1    1 本   A5      A5 のトロル(夜で遮蔽ありを除く) → hold_position(新)
    orc_pair_day_no_arrows_alarm 1  1/1    1 本   L5      警報未のオーク 2 体・昼・味方 0・離れて矢 0 → raise_alarm
    orc_pair_day_melee         <=1  1/1           L2      警報未のオーク 2 体・昼・隣接・ehp<=25・味方 1 以下 → melee_attack
    a3_mage_shoot               0                 A3      A3・昼・7 マス以上 → shoot

棄権の番人(割れている所、証拠が足りない所。輪が審判に訊き直す所)
    wounded_no_threat      31  hp 25〜30・薬なし・敵なし(持ち場 13 / 退く 17 / 遮蔽 1)。A6 の範囲だが上の 3 のとおり割れる
    hurt_no_threat         15  hp<=24・薬なし・敵なし・味方 0(退く 9 / 持ち場 6)。A6 は持ち場
    a1_night_split          6  A1 の範囲の夜(射る 3 / 退く 3)
    group_alarm_unclear     6  警報未のゴブリン 3 体・味方あり・夜(警報 3 / 射る 2 / 斬る 1)
    wounded_alarm_unclear   5  hp 25〜32・警報未の深刻な脅威で A4 の外(飲む 2 / 斬る 1 / 警報 1 / 射る 1)
    orc_alarm_unclear       4  上の 6 の残り(持ち場 2 / 警報 1 / 射る 1)
    troll_alarm_raised      3  警報済みトロルの残り(持ち場 1 / 退く 1 / 射る 1)
    mage_no_arrows          3  警報済みの魔術師・矢 0 の残り(斬る 2 / 飲む 1)
    hp_ambiguous            1  hp 31〜32・薬なし・敵あり・A1 で射るに当たらない所(射る 1)
    a5_mage_unclear        1+  A5 の魔術師(斬る 1 と、遮蔽の例のうち味方 3 のもの)
    a5_night_unclear        ?  A5 の夜・遮蔽あり(night_no_arrows_cover から抜けた分)
    a5_hurt_conflict        ?  hp<=32 の A5
    a3_a4_conflict          0  hp 25〜28 で A3 と A4 が重なる所
    mage_alarm_unclear      0  警報未の魔術師・2〜6 マス・敵 3・味方あり
    a3_night_unclear        0  夜の A3
    a2_hurt_conflict        0  hp<=32 の A2
    a3_hurt_conflict        0  hp<=24 の A3
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
_HURT_MAX = 24      # これ以下はひどい(b2 のまま)
_FINE_MIN = 33      # これ以上はひどくない(b1 のまま)

# 追補 A1
_A1_HP_MIN = 31
_A1_DIST_MIN = 9

# 追補 A2
_A2_DIST_MIN = 11

# 追補 A3
_A3_ENEMY_HP_MAX = 40
_A3_DIST_MIN = 6
_A3_ARROWS_MIN = 11

# 追補 A4
_A4_HP_MAX = 28
_A4_DIST_MIN = 10

# 追補 A5
_A5_ALLIES_MIN = 3
_A5_DIST_MIN = 4

# 追補 A6(敵なし・薬なしで、これ以下の hp は A6 の範囲)
_A6_HP_MAX = 30

# hp 25〜32・薬なし・敵あり: これ以下なら退く(退くの最高 hp28 と射る hp32 の間。A6 と同じ線)
_WOUNDED_RETREAT_MAX = 30

# 傷を負っていて警報未の深刻な脅威がいる時、この距離以上なら先に警報
# (hp<=24 のトロルで隣接 1 は L1、警報側は 5 以上。hp 25〜32 でも同じ線を使う)
_ALARM_FIRST_DIST = 3

# 警報未の群れ
_HORDE_MIN = 4          # 敵がこれ以上なら警報
_OUTNUMBERED_MIN = 3    # 味方 0 で敵がこれ以上なら警報

# 警報未の魔術師: この距離以上なら警報(昼の 6 以内は射る)
_MAGE_FAR_MIN = 7

# 警報済みの魔術師・矢 0: この距離以下なら詰めて斬る(審判の決め手 distance<=2)
_MAGE_CLOSE_MAX = 2

# 警報済みの魔術師・矢 0: これ以下の体力なら遮蔽に回さない(審判の決め手 enemy_hp<=40)
_MAGE_WEAK_HP_MAX = 40

# 弱った敵(夜のオーク 2 体: ehp20 は射る、ehp30 は警報。線は 20 と 30 の間)
_WEAK_HP_MAX = 25

# 警報未のオーク 2 体が隣接: 味方がこれ以上なら斬る(審判の決め手 allies>=2 / >=3)
_ORC_PAIR_MELEE_ALLIES_MIN = 2


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


def _a1(s):
    """追補 A1 の範囲(回復薬の有無は問わない。hp 25〜32 では薬ありを先に飲むへ回す)。"""
    return (s["enemy"] != "none" and s["hp"] >= _A1_HP_MIN
            and s["distance"] >= _A1_DIST_MIN and s["arrows"] >= 1)


def _a2(s):
    """追補 A2 の範囲: 夜・矢 0・味方 0・遮蔽あり・敵 11 マス以上。"""
    return (s["enemy"] != "none" and s["time"] == "night"
            and s["arrows"] == 0 and s["allies"] == 0 and s["cover"]
            and s["distance"] >= _A2_DIST_MIN)


def _a3(s):
    """追補 A3 の範囲: 警報未・魔術師一体・体力 40% 以下・6 マス以上・矢 11 本以上。"""
    return (s["enemy"] == "mage" and not s["alarm"]
            and s["enemy_count"] == 1
            and s["enemy_hp"] <= _A3_ENEMY_HP_MAX
            and s["distance"] >= _A3_DIST_MIN
            and s["arrows"] >= _A3_ARROWS_MIN)


def _a4(s):
    """追補 A4 の範囲: 警報未・hp<=28・薬あり・魔術師・10 マス以上。"""
    return (s["enemy"] == "mage" and not s["alarm"]
            and s["hp"] <= _A4_HP_MAX and s["potion"]
            and s["distance"] >= _A4_DIST_MIN)


def _a5(s):
    """追補 A5 の範囲: 警報済み・矢 0・味方 3 以上・敵 4 マス以上。"""
    return (s["enemy"] != "none" and s["alarm"]
            and s["arrows"] == 0 and s["allies"] >= _A5_ALLIES_MIN
            and s["distance"] >= _A5_DIST_MIN)


def _serious_unalarmed(s):
    """hp 25〜32 で深刻な脅威として扱う敵か(敵がいて alarm=false の時だけ呼ぶ)。
    b2 のまま。昼のゴブリン 3 体・味方ありは hp>=33 では L2 に落ちるが、ここでは据え置く。"""
    enemy = s["enemy"]
    count = s["enemy_count"]
    if enemy in ("troll", "mage"):
        return True
    if count >= _HORDE_MIN:
        return True
    if count >= _OUTNUMBERED_MIN and s["allies"] == 0:
        return True
    if enemy == "orc" and count >= 2:
        return True
    if enemy == "goblin" and count >= 3:
        return True
    return False


def _hurt(s):
    """hp<=24: ひどく傷ついている(L1)。"""
    enemy = s["enemy"]

    # L5+L3: 警報未のトロルがまだ遠いなら、先に警報
    if (enemy == "troll" and not s["alarm"]
            and s["distance"] >= _ALARM_FIRST_DIST):
        return ("raise_alarm", "hurt_troll_alarm")

    # 追補と L1 がぶつかる所
    if _a2(s):
        return (None, "a2_hurt_conflict")
    if _a3(s):
        return (None, "a3_hurt_conflict")
    if _a5(s):
        return (None, "a5_hurt_conflict")

    # L1(A4 の hp<=24 もここで飲む)
    if s["potion"]:
        return ("drink_potion", "hurt_drink")
    if enemy == "none":
        # A6: 味方がいれば退く。味方 0 は A6 が持ち場、帳簿は退くが多数で割れる
        if s["allies"] >= 1:
            return ("retreat", "hurt_handover")
        return (None, "hurt_no_threat")
    return ("retreat", "hurt_retreat")


def _wounded(s):
    """hp 25〜32: ひどいかどうかが会話で割れる所。"""
    enemy = s["enemy"]

    # 警報未の深刻な脅威
    if enemy != "none" and not s["alarm"] and _serious_unalarmed(s):
        # 追補 A4: 警報より先に回復薬(L1 の飲むと同じ規則)
        if _a4(s):
            if _a2(s):
                return (None, "a2_hurt_conflict")
            if _a3(s):
                return (None, "a3_a4_conflict")
            return ("drink_potion", "wounded_drink")
        if not s["potion"] and s["distance"] >= _ALARM_FIRST_DIST:
            act, _name = _fine(s)
            if act == "raise_alarm":
                return ("raise_alarm", "wounded_alarm")
        return (None, "wounded_alarm_unclear")

    # 追補 A2・A5 と L1 がぶつかる所
    if _a2(s):
        return (None, "a2_hurt_conflict")
    if _a5(s):
        return (None, "a5_hurt_conflict")

    if s["potion"]:
        return ("drink_potion", "wounded_drink")

    if enemy == "none":
        # A6 の外(hp 31〜32): 脅威が無いので持ち場(L7)
        if s["hp"] > _A6_HP_MAX:
            return ("hold_position", "no_threat_hold")
        # A6 の範囲。帳簿は会話ごとに割れる
        return (None, "wounded_no_threat")

    # 追補 A1: hp>=31、薬なし、敵 9 マス以上、矢あり → 退かずに射る
    if _a1(s):
        if s["time"] == "night":
            return (None, "a1_night_split")
        act, _name = _fine(s)
        if act == "shoot":
            return ("shoot", "a1_shoot")
        return (None, "hp_ambiguous")

    # L1: 重傷で薬が無いので退く
    if s["hp"] <= _WOUNDED_RETREAT_MAX:
        return ("retreat", "wounded_retreat")

    return (None, "hp_ambiguous")


def _fine(s):
    """hp>=33: ひどくない。"""
    enemy = s["enemy"]
    dist = s["distance"]
    count = s["enemy_count"]
    allies = s["allies"]
    arrows = s["arrows"]
    cover = s["cover"]
    alarm = s["alarm"]
    night = s["time"] == "night"

    # --- L7: 脅威が無い ---
    if enemy == "none":
        return ("hold_position", "no_threat_hold")

    # --- 追補 A5: 警報済み・矢 0・味方 3 以上・4 マス以上 → 遮蔽があっても持ち場 ---
    if _a5(s):
        if enemy == "mage":
            return (None, "a5_mage_unclear")
        if night and cover:
            return (None, "a5_night_unclear")
        if enemy == "troll":
            return ("hold_position", "a5_hold")
        # ゴブリン・オークは b3 でも no_arrows_hold
        return ("hold_position", "no_arrows_hold")

    # --- L3 + L5: トロル ---
    if enemy == "troll":
        if not alarm:
            return ("raise_alarm", "troll_alarm")
        if allies >= 1:
            if dist == 1:
                return ("melee_attack", "troll_melee_allies")
            if arrows >= 1:
                return ("shoot", "troll_shoot_allies")
            return (None, "troll_alarm_raised")
        # 味方 0(L3: 一人で相手にするには強すぎる)
        if night:
            if dist == 1:
                return ("retreat", "troll_alone_retreat")
            if cover:
                return ("take_cover", "troll_alone_cover")
            return (None, "troll_alarm_raised")
        if _a1(s):
            return ("shoot", "a1_shoot")
        return (None, "troll_alarm_raised")

    # --- L5: 警報未のとき、深刻な脅威かどうか ---
    if not alarm:
        if count >= _HORDE_MIN:
            return ("raise_alarm", "horde_alarm")
        if count >= _OUTNUMBERED_MIN and allies == 0:
            return ("raise_alarm", "outnumbered_alarm")

        if enemy == "mage":
            if dist == 1:
                return ("melee_attack", "mage_melee")
            if arrows <= 0:
                return ("raise_alarm", "mage_no_arrows_alarm")
            if _a3(s):
                if night:
                    return (None, "a3_night_unclear")
                if dist >= _MAGE_FAR_MIN:
                    return ("shoot", "a3_mage_shoot")
                # 昼の 6 マスは下の mage_first_shoot と同じ答え
            if dist >= _MAGE_FAR_MIN:
                return ("raise_alarm", "mage_far_alarm")
            if count >= 3:
                return (None, "mage_alarm_unclear")
            if night:
                return ("raise_alarm", "mage_night_alarm")
            return ("shoot", "mage_first_shoot")

        if enemy == "orc" and count >= 2:
            if count >= 3:
                # ここに来るのは味方ありのオーク 3 体
                return ("raise_alarm", "orc_trio_alarm")
            # L2: 隣接していて味方が 2 人以上なら、昼夜を問わず近接で戦う
            if dist == 1 and allies >= _ORC_PAIR_MELEE_ALLIES_MIN:
                return ("melee_attack", "melee_adjacent")
            weak = s["enemy_hp"] <= _WEAK_HP_MAX
            if night:
                if allies <= 1 and not weak:
                    return ("raise_alarm", "orc_pair_night_alarm")
            elif dist >= 2:
                if arrows >= 1:
                    return ("shoot", "orc_pair_day_shoot")
                if allies == 0:
                    return ("raise_alarm", "orc_pair_day_no_arrows_alarm")
            elif weak:
                return ("melee_attack", "orc_pair_day_melee")
            return (None, "orc_alarm_unclear")

        if enemy == "goblin" and count >= 3:
            # ここに来るのは味方ありのゴブリン 3 体。昼は深刻な脅威とせず L2 へ
            if night:
                return (None, "group_alarm_unclear")
        # 単独のオーク、ゴブリン 1〜2 体、昼のゴブリン 3 体・味方あり → L2 へ

    # --- L2 (+ L4 魔術師) ---
    if dist == 1:
        if enemy == "mage":
            return ("melee_attack", "mage_melee")
        return ("melee_attack", "melee_adjacent")

    # 離れている(distance>=2)
    if arrows <= 0:
        if enemy == "mage":
            if (cover and dist > _MAGE_CLOSE_MAX
                    and s["enemy_hp"] > _MAGE_WEAK_HP_MAX):
                return ("take_cover", "mage_no_arrows_cover")
            if not cover and dist <= _MAGE_CLOSE_MAX:
                return ("melee_attack", "mage_close_in")
            return (None, "mage_no_arrows")
        if cover and night:
            return ("take_cover", "night_no_arrows_cover")
        return ("hold_position", "no_arrows_hold")
    if enemy == "mage":
        return ("shoot", "mage_shoot")
    return ("shoot", "shoot_far")


def decide(s):
    bad = _guard(s)
    if bad is not None:
        return (None, bad)

    hp = s["hp"]
    if hp <= _HURT_MAX:
        return _hurt(s)
    if hp < _FINE_MIN:
        return _wounded(s)
    return _fine(s)
