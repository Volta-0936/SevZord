"""走り r2 の方針、第 2 版(b2)。やり直し 1 回目。

帳簿: 審判のラベル 264 件、会話 6 本(round1_s1〜s3、round2_s1〜s3。以下 r1s1 … r2s3)。
b1 が答えた状態の行き先は、この版でも変わらない(b1 の枝の条件は動かさず、棄権していた所に
答えを足しただけ)。

前の版が門で落ちた理由と直し方
  前の版は追補 A1 を枝 a1_shoot_far 一本にした。A1 の範囲のうち b1 が棄権していた所
  (hp 31〜32、回復薬なし、敵 9 マス以上、矢あり)の帳簿は 6 件で、射る 3・退く 3。
  退くのは r2s1 の 2 件(hp31 ゴブリン d9、hp32 オーク d9)と r2s2 の 1 件(hp31 オーク 4 体 d10)で、
  r2s2 はこの範囲で射る 1・退く 1 に割れる。射る 3 件は、訊き直した一つの状態
  (hp31 ゴブリン 3 体 d9 矢 5 警報済み、夜)の票。この状態だけで射る 3・退く 1(75%)なので、
  この状態を含む枝は、どう切っても一致 80% に届かない。
  6 件はすべて夜で、退く側の決め手に time=night が挙がる(r2s1「深手で薬が無い夜なので射るより
  退く」、r2s2「深手で夜にオーク4体、無駄死にを避けて退く」)。根拠にも L6 が付く。
  そこで A1 を昼と夜に分けた。
    a1_shoot(昼、答える枝): A1 をそのまま読んだ規則(規律 (a))。帳簿の例は 0 件。
        hp>=33 と同じ読み(_fine)が射ると言う所だけで答え、警報・遮蔽・棄権になる所は答えない。
    a1_night_split(夜、番人): 上の 6 件。L6 と A1 がぶつかる所として棄権し、輪に回す。
  回復薬を持っている時は A1 の外とした。A1 は「回復薬が無くとも」退かない、という規則で、
  hp31・オーク d12・薬ありは r1s2 が飲む(下の wounded_drink に入る)。
  hp>=33 では A1 は既に shoot_far などと同じ答えなので、何も変えない。

この版で変えたこと
 1. A1 を上のとおり入れた。
 2. 「ひどく傷ついている」の上限を hp<=20 から hp<=24 に上げた(_HURT_MAX)。
    hp 21〜23 のラベル 9 件(会話 5 本)は、すべて L1 どおり。飲む 1(hp21 薬あり、r1s2、決め手
    hp<=21, potion=true)、退く 8(隣接トロル hp23 薬なしを r1s1 r2s1 r2s2 r2s3 の 4 本が
    すべて退く、hp23 オーク・hp22 ゴブリン・hp21 ゴブリンの退くが各 1、敵なし・味方 0 の退く 1)。
    決め手は hp<=30 / hp<=23 / hp<=22 と potion=false。敵のいる所で L1 から外れる最初の例は
    hp26(r2s3 が 7 マス先の瀕死のゴブリンを射る)。線は 23 と 26 の間の 24 に置いた。
    hp 25〜32 は wounded(下の 5)として別に扱う。
 3. 番人 hurt_vs_alarm(ひどい傷とトロル・警報未)を距離で分けた。
    新しい枝 hurt_troll_alarm: 3 マス以上 → raise_alarm。3 件・会話 3 本(r1s3 d12、r2s2 d10、
        r2s3 d5)・一致 3/3。決め手 alarm=false, enemy=troll, distance>=12 / >=10 / >=5
        (「まだ遠い、先に警報」)。薬を持っていても警報が先(r1s3)。
    隣接は L1 に通す: hp14 d1 薬あり → 飲む(r2s3、決め手 distance=1)、hp23 d1 薬なし → 退く
        (上の 4 本)。線は隣接 1 と、警報側の最も近い 5 の間の 3 に置いた。
 4. 新しい枝 hurt_handover: ひどい傷・薬なし・敵なし・近くの味方 1 以上 → retreat。
    9 件・会話 3 本(r1s3 3、r2s1 2、r2s3 4)・一致 9/9。決め手 potion=false と
    allies>=1 / >=2 / >=3、hp<=15 など。理由は「門を味方に任せて退く」。
    味方 0 は持ち場 2(r2s3)・退く 2(r2s1, r2s2)で割れる → 番人 hurt_no_threat のまま。
 5. hp 25〜32(wounded)。
    新しい枝 wounded_drink: 回復薬あり → drink_potion(警報未の深刻な脅威がいる時は除く)。
        6 件・会話 4 本(r1s2 1、r1s3 1、r2s1 3、r2s2 1)・一致 6/6。決め手 potion=true と
        hp<=30 / <=31 / <=33。根拠は 5 件が L1 だけ。飲むの最も高い例は hp31(r1s2・r2s1)。
        hp>=33 で薬があって飲んだ例は無い(no_threat_hold 45/45)。hp 21 の飲む 1 件は 2 の hurt_drink。
    番人 wounded_alarm_unclear: 警報未の深刻な脅威(トロル、魔術師、敵 4 以上、味方 0 で敵 3、
        オーク 2 体以上、ゴブリン 3 体以上)がいる所。警報 3・飲む 1(r1s1 1、r2s3 3)、根拠は全件 gap。
    番人 wounded_no_threat: 薬なし・敵なし。持ち場 5・退く 8 で、退く 8 のうち 6 件が r2s1。
        訊き直した hp28・味方 0・夜の門の状態は 2 対 2。味方 1 以上に絞っても退く 6・持ち場 2(75%)。
    番人 hp_ambiguous: 薬なし・敵あり・A1 の外。射る 2 件(1 件は gap)で、規律 (c) に届かない。
 6. 番人 no_arrows_cover(離れた敵・矢 0・遮蔽あり 26 件)を昼夜で分けた。
    夜 → take_cover(新しい枝 night_no_arrows_cover): 7 件・会話 4 本(r1s1 1、r2s1 2、r2s2 2、
        r2s3 2)・一致 7/7。決め手 time=night, arrows=0, cover=true。根拠 L6(4 件は gap なし)。
    昼 → hold_position: 19 件・会話 6 本・一致 18/19。遮蔽なしの no_arrows_hold と同じ規則
        (矢が無く敵が離れていれば持ち場で待つ)なので同じ枝に入れた。外れる 1 件は r1s2 の
        take_cover(hp42、決め手 hp<=42, potion=false)だが、昼・遮蔽ありで hp37 の持ち場
        (r2s1)もあるので線にしない。r1s2 はこの枝で持ち場が多数のまま。
 7. 番人 mage_alarm_unclear(警報未の魔術師 20 件)を分けた。
    隣接 → melee_attack: 4 件・会話 3 本(r1s3 1、r2s1 2、r2s3 1)・一致 4/4。決め手 enemy=mage,
        distance=1(「隣の魔術師を警報より先に斬る」)。警報済みの隣接と同じ規則(L2+L4)なので
        mage_melee に入れた。
    矢 0 → raise_alarm(新しい枝 mage_no_arrows_alarm): 4 件・会話 2 本(r1s1 1、r2s2 3)・
        一致 4/4。決め手 enemy=mage, alarm=false, arrows=0(「討つ手段が無く、まず警報」)。
        3 件は根拠 L4,L5 で gap なし。
    7 マス以上・矢あり → raise_alarm(新しい枝 mage_far_alarm): 5 件・会話 3 本(r1s3 1、
        r2s1 2、r2s2 2)・一致 5/5。決め手 distance>=12 / >=7、arrows<=1、enemy_count>=3
        (「魔術師がまだ遠いうちに警報」)。昼に 6 マス以内・矢ありは射る 5/5(距離 2, 3, 6, 6, 6)
        なので、線は 6 と 7 の間。
    昼・2〜6 マス・敵 2 以下・矢あり → shoot(新しい枝 mage_first_shoot): 5 件・会話 3 本
        (r1s2 2、r2s1 2、r2s2 1)・一致 5/5。決め手 enemy=mage, distance<=3 / <=2,
        arrows>=6..20, enemy_hp<=10 / <=30(「近い魔術師は警報より先に射て仕留める」)。
    残り → 番人 mage_alarm_unclear: 夜の 3〜6 マス 2 件は r2s3 がどちらも警報(決め手 time=night、
        根拠 gap、会話 1 本)。敵 3 の近い魔術師は例が無い。
 8. 番人 troll_alarm_raised(警報済みのトロル 15 件)を味方の数で分けた。
    味方あり・隣接 → melee_attack(新しい枝 troll_melee_allies): 2 件・会話 2 本(r2s1, r2s2)・
        一致 2/2。根拠はどちらも L2,L3 で gap なし → 規律 (c)。決め手 distance=1, allies>=1 / >=2
        (「味方がいて一人ではない」)。
    味方あり・離れて矢あり → shoot(新しい枝 troll_shoot_allies): 5 件・会話 4 本(r1s1、r1s3、
        r2s2 2、r2s3)・一致 5/5。決め手 distance>=2..8, arrows>=1..14, allies>=1 / >=2。
    味方 0・離れて・遮蔽あり・夜 → take_cover(新しい枝 troll_alone_cover): 4 件・会話 3 本
        (r1s2 2、r2s1、r2s3)・一致 4/4。決め手 enemy=troll, allies=0 と cover=true / time=night
        (「単独でトロルに挑めず、遮蔽で援軍を待つ」)。4 件とも夜で遮蔽あり。
    残り 4 件 → 番人 troll_alarm_raised: 味方 0 の隣接は退く 2(r2s1, r2s3、根拠 gap)、
        味方ありで矢 0 は持ち場 1・退く 1。
 9. 番人 orc_alarm_unclear(警報未のオーク 12 件、すべて 2 体)を昼夜で分けた。
    夜・味方 1 以下・弱っていない(enemy_hp>30)→ raise_alarm(新しい枝 orc_pair_night_alarm):
        5 件・会話 5 本・一致 5/5(訊き直した hp82 隣接・味方 0 の状態を r1s2 r2s1 r2s2 r2s3 が
        すべて警報、r1s3 の味方 1・d6 も警報)。決め手 alarm=false, allies=0, time=night
        (「夜に一人でオーク二体なので戦うより警報」)。夜でも味方 2 なら r1s3 が隣接を斬り
        (決め手 allies>=2)、弱ったオークは r2s3 が射る(決め手 enemy_hp<=20、昼の r2s3 も
        enemy_hp<=30 を決め手に射る)。
    昼・離れて・矢あり → shoot(新しい枝 orc_pair_day_shoot): 3 件・会話 2 本(r2s1 1、r2s3 2)・
        一致 3/3。決め手 distance>=4 / >=9 / >=12、arrows>=3..8、allies / enemy_hp<=30。
    残り 4 件 → 番人 orc_alarm_unclear(夜・味方 2 の隣接 斬る 1、夜・弱ったオーク 射る 1、
        夜・味方 1・矢 0・enemy_hp30 警報 1、昼・矢 0 警報 1)。敵 3・味方ありは例が無い。

b2 で数え直した帳簿(答える枝、件数・一致・会話)
    no_threat_hold         45  45/45  6 本      L7      敵なし・hp>=33 → hold_position
    no_arrows_hold         29  28/29  6 本      gap     離れた敵・矢 0・(遮蔽なし、または昼) → hold_position
    shoot_far              27  26/27  5 本      L2      離れたゴブリン/オーク・矢あり → shoot
    horde_alarm            17  17/17  6 本      L5      警報未・敵 4 以上 → raise_alarm
    melee_adjacent         12  12/12  5 本      L2      隣接のゴブリン/オーク → melee_attack
    hurt_handover           9   9/9   3 本      L1+L7   hp<=24・薬なし・敵なし・味方あり → retreat
    hurt_retreat            8   8/8   5 本以上  L1      hp<=24・薬なし・敵あり → retreat
    night_no_arrows_cover   7   7/7   4 本      L6      離れた敵・矢 0・遮蔽あり・夜 → take_cover
    wounded_drink           6   6/6   4 本      L1      hp 25〜32・薬あり → drink_potion
    troll_alarm             5   5/5   3 本      L5+L3   トロル・警報未 → raise_alarm
    troll_shoot_allies      5   5/5   4 本      L2+L3   警報済みトロル・味方あり・離れて矢あり → shoot
    mage_far_alarm          5   5/5   3 本      L5+L4   警報未の魔術師・7 マス以上・矢あり → raise_alarm
    mage_first_shoot        5   5/5   3 本      L4+L2   警報未の魔術師・昼・2〜6 マス・敵 2 以下 → shoot
    orc_pair_night_alarm    5   5/5   5 本      L5+L6   警報未のオーク 2 体・夜・味方 1 以下 → raise_alarm
    hurt_drink              4   4/4   2 本以上  L1      hp<=24・薬あり → drink_potion
    mage_melee              4   4/4   3 本      L2+L4   隣接の魔術師 → melee_attack
    mage_no_arrows_alarm    4   4/4   2 本      L5+L4   警報未の魔術師・離れて矢 0 → raise_alarm
    troll_alone_cover       4   4/4   3 本      L3+L6   警報済みトロル・味方 0・離れて・遮蔽・夜 → take_cover
    outnumbered_alarm       3   3/3   2 本      L5      警報未・敵 3・味方 0 → raise_alarm
    mage_shoot              3   3/3   2 本      L2+L4   離れた魔術師(警報済み)・矢あり → shoot
    hurt_troll_alarm        3   3/3   3 本      L5+L3   hp<=24・トロル・警報未・3 マス以上 → raise_alarm
    orc_pair_day_shoot      3   3/3   2 本      L2      警報未のオーク 2 体・昼・離れて矢あり → shoot
    troll_melee_allies      2   2/2   2 本      L2+L3   警報済みトロル・味方あり・隣接 → melee_attack
    a1_shoot                0                   A1      hp 31〜32・薬なし・敵 9 マス以上・矢あり・昼 → shoot

棄権の番人(割れている所、証拠が足りない所。輪が審判に訊き直す所)
    wounded_no_threat      13  hp 25〜32・薬なし・敵なし(持ち場 5 / 退く 8、退くの 6 件は r2s1)
    a1_night_split          6  A1 の範囲の夜(射る 3 / 退く 3。上を見よ)
    group_alarm_unclear     6  警報未のゴブリン 3 体・味方あり(斬る 1 / 射る 2 / 警報 1 / 持ち場 2)
    wounded_alarm_unclear   4  hp 25〜32 と警報未の深刻な脅威(警報 3 / 飲む 1、全件 gap)
    hurt_no_threat          4  hp<=24・薬なし・敵なし・味方 0(持ち場 2 / 退く 2)
    troll_alarm_raised      4  警報済みトロルの残り(退く 3 / 持ち場 1)
    orc_alarm_unclear       4  警報未のオーク 2 体の残り(斬る 1 / 射る 1 / 警報 2)、オーク 3 体・味方あり
    mage_no_arrows          4  離れた魔術師(警報済み)・矢 0(斬る 2 / 遮蔽 2、全件 gap)
    hp_ambiguous            2  hp 25〜32・薬なし・敵あり・A1 の外(射る 2、うち 1 件 gap)。
                               A1 の昼でも hp>=33 の読みが射ると言わない所
    mage_alarm_unclear      2  警報未の魔術師・夜・2〜6 マス(警報 2、r2s3 のみ・gap)、敵 3 の近い魔術師
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
_HURT_MAX = 24      # これ以下はひどい(hp21〜23 は 9/9 が L1、hp26 から外れる)
_FINE_MIN = 33      # これ以上はひどくない(b1 のまま)

# 追補 A1
_A1_HP_MIN = 31
_A1_DIST_MIN = 9

# ひどい傷と警報未のトロル: この距離以上なら警報(隣接 1 は L1、警報側は 5 以上)
_HURT_TROLL_ALARM_DIST = 3

# 警報未の群れ
_HORDE_MIN = 4          # 敵がこれ以上なら警報(敵 3 は割れる、4・5 は一致)
_OUTNUMBERED_MIN = 3    # 味方 0 で敵がこれ以上なら警報

# 警報未の魔術師: この距離以上なら警報(昼の 6 以内は射る)
_MAGE_FAR_MIN = 7

# 弱った敵(審判の決め手 enemy_hp<=30 / <=20)
_WEAK_HP_MAX = 30


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


def _serious_unalarmed(s):
    """警報未で、hp>=33 なら警報か棄権になる敵か(敵がいて alarm=false の時だけ呼ぶ)。"""
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
            and s["distance"] >= _HURT_TROLL_ALARM_DIST):
        return ("raise_alarm", "hurt_troll_alarm")

    if s["potion"]:
        return ("drink_potion", "hurt_drink")
    if enemy == "none":
        if s["allies"] >= 1:
            return ("retreat", "hurt_handover")
        return (None, "hurt_no_threat")
    return ("retreat", "hurt_retreat")


def _wounded(s):
    """hp 25〜32: ひどいかどうかが会話で割れる所。"""
    enemy = s["enemy"]

    if enemy != "none" and not s["alarm"] and _serious_unalarmed(s):
        return (None, "wounded_alarm_unclear")

    if s["potion"]:
        return ("drink_potion", "wounded_drink")

    if enemy == "none":
        return (None, "wounded_no_threat")

    # 追補 A1: hp>=31、薬なし、敵 9 マス以上、矢あり → 退かずに射る
    if (s["hp"] >= _A1_HP_MIN and s["distance"] >= _A1_DIST_MIN
            and s["arrows"] >= 1):
        if s["time"] == "night":
            return (None, "a1_night_split")
        act, _name = _fine(s)
        if act == "shoot":
            return ("shoot", "a1_shoot")
        return (None, "hp_ambiguous")

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
        if dist >= 2 and cover and night:
            return ("take_cover", "troll_alone_cover")
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
            if dist >= _MAGE_FAR_MIN:
                return ("raise_alarm", "mage_far_alarm")
            if night or count >= 3:
                return (None, "mage_alarm_unclear")
            return ("shoot", "mage_first_shoot")

        if enemy == "orc" and count >= 2:
            if count == 2:
                if night:
                    if allies <= 1 and s["enemy_hp"] > _WEAK_HP_MAX:
                        return ("raise_alarm", "orc_pair_night_alarm")
                elif dist >= 2 and arrows >= 1:
                    return ("shoot", "orc_pair_day_shoot")
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
