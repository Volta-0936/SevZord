"""走り r2 の方針、第 3 版(b3)。

帳簿: 審判のラベル 359 件、会話 9 本(round1_s1〜s3、round2_s1〜s3、round3_s1〜s3。
以下 r1s1 … r3s3)。b2 の答える枝は、どれも門の条件を満たしたまま(最も低いのは
troll_alone_cover の 4/5 = 80%、会話で割れるのは r3s1 の 1 本だけ)。b2 の枝の条件は動かさず、
棄権していた所に答えを足し、新しい追補 A2・A3 を入れた。変えたのは次のとおり。

 1. 追補 A3(規律 (a))。警報未・魔術師一体・体力 40% 以下・6 マス以上・矢 11 本以上 → 射る。
    A3 の元の状態(hp84 魔術師 d6 ehp40 味方 0 矢 11 昼)は射る 3・警報 1 で、既に mage_first_shoot
    の中にある。この状態を別の枝に移すと、その枝は 3/4 = 75% で落ちるので、昼の 6 マスは
    mage_first_shoot のまま。
      a3_mage_shoot(新しい枝): 昼・7 マス以上。b2 では mage_far_alarm(警報)だった所を、
          A3 の「警報より先に」どおり射るに変えた。帳簿の例は 0 件か、あっても 1 件。
      a3_night_unclear(番人): 夜の A3。元の状態は昼で、夜の魔術師は下の 4 のとおり警報に
          なる(L6)。A1 の夜が割れた(a1_night_split)のと同じ形なので、答えず輪に回す。
      a3_hurt_conflict(番人): hp<=24 の A3。L1(飲む・退く)とぶつかり、例も無い。
 2. 追補 A2(夜・矢 0・味方 0・遮蔽あり・敵 11 マス以上 → 遮蔽に隠れる)。
    元の状態(hp44 ゴブリン 3 体 d11 薬あり 警報済み 夜)は遮蔽 3・飲む 1 で、night_no_arrows_cover
    の中にある。hp>=33 では A2 の範囲はどこも既に take_cover(night_no_arrows_cover、
    troll_alone_cover、下の mage_no_arrows_cover)か、警報未の深刻な脅威への警報(L5 を先に読む。
    A3 と違い A2 は「警報より先に」と言わない)なので、答えは何も変えない。
      a2_hurt_conflict(番人): hp<=32 の A2 の範囲。L1 の飲む・退くとぶつかり、例も無いので棄権。
          hp<=24 の hurt_drink / hurt_retreat と、hp 25〜32 の wounded_drink からこの範囲を抜いた。
          (警報未のトロルが 3 マス以上なら hurt_troll_alarm、警報未の深刻な脅威は下の 3 が先。)
 3. 新しい枝 wounded_alarm: hp 25〜32・薬なし・警報未の深刻な脅威・3 マス以上で、hp>=33 の読み
    (_fine)が警報と言う所 → raise_alarm。5 件・会話 4 本(r2s3 1、r3s1 1、r3s2 1、r3s3 2)・
    一致 5/5(規律 (b))。決め手は全件 alarm=false と、enemy_count>=3,allies=0 / enemy_count>=4,
    enemy=mage / enemy=mage,arrows=0 / enemy_count>=4,distance>=8 / enemy=troll,distance>=8。
    理由は「退く前に、敵が遠い今のうち警報を鳴らす」「トロル出現、退く前に遠い内に警報」。
    5 件とも 7〜8 マスで、近い側の反例はこの区画に無い。そこで hurt_troll_alarm で隣接 1 と 5 の
    間に置いた線 3(_ALARM_FIRST_DIST)をそのまま使う。
    薬を持っている時は警報 3・飲む 4・斬る 1・射る 1 に割れる(訊き直した hp28 魔術師 d10 の状態も
    警報 2・飲む 2)ので、番人 wounded_alarm_unclear のまま。
 4. 番人 mage_alarm_unclear(警報未の魔術師・夜・2〜6 マス)を答えにした。
    新しい枝 mage_night_alarm → raise_alarm: 3 件・会話 2 本(r2s3 2、r3s2 1)・一致 3/3
    (規律 (b))。決め手 enemy=mage, alarm=false, time=night(2 件)、allies=0(1 件)。理由「夜に
    魔術師、一矢では倒せず先に警報」「魔術師出現、夜に独りなので先に警報」。敵 2 体までの所だけ。
    敵 3 体・味方ありの近い魔術師は例が無く、番人 mage_alarm_unclear に残す。
 5. 番人 mage_no_arrows(警報済みの離れた魔術師・矢 0、8 件)を遮蔽と距離で分けた。
    遮蔽あり・3 マス以上 → take_cover(新しい枝 mage_no_arrows_cover): 3 件・会話 3 本(r2s1 d6、
        r2s2 d5、r3s1 d7)・一致 3/3(規律 (b))。決め手は 3 件とも enemy=mage, arrows=0,
        cover=true。理由「矢が無く魔術師は遠いので遮蔽で呪文を避ける」。
    遮蔽なし・2 マス → melee_attack(新しい枝 mage_close_in): 3 件・会話 3 本(r1s1、r2s1、r3s2)・
        一致 3/3(規律 (b))。決め手 enemy=mage, arrows=0, distance<=2(2 件)、hp>=90。
        理由「矢が無いので二マス先の魔術師に斬り込む」。線は審判の挙げた distance<=2。
    残り → 番人 mage_no_arrows: 遮蔽なしの遠い魔術師(d8、d12)は斬る 2 件だが会話 2 本・
        どちらも gap で、理由が「体力十分」(決め手 hp>=82 / hp>=90)に頼る。規律 (b)(c) に届かない。
        2 マスで遮蔽ありは例が無い。
 6. 番人 troll_alarm_raised(警報済みトロルの残り、9 件)から二つ答えにした。
    味方 0・隣接・夜 → retreat(新しい枝 troll_alone_retreat): 3 件・会話 3 本(r2s1、r2s3、r3s3)・
        一致 3/3(規律 (b))。決め手 enemy=troll, allies=0 と time=night / distance=1 / distance<=1。
        理由「夜に一人でトロルとは戦わず退く」「隣接トロルに単独では勝てず、無駄死にを避けて退く」。
        3 件とも夜なので昼の隣接は答えない(troll_alone_cover を夜に限ったのと同じ)。
    味方 0・昼・A1 の範囲(9 マス以上・矢あり)→ shoot(枝 a1_shoot を hp>=33 にも広げた): 2 件・
        会話 1 本(r3s2)・一致 2/2。根拠はどちらも L2,A1 で gap なし(規律 (a)(c))。決め手 hp>=31,
        distance>=9, arrows>=6 / >=15。理由「トロルは遠く矢もある、追補通り退かず射る」。
        hp>=33 では回復薬の有無を問わない(A1 は「回復薬が無くとも」退かない、という規則)。
        夜は A1 と L6 がぶつかる所(a1_night_split と同じ)なので答えない。
    残り 4 件 → 番人 troll_alarm_raised(持ち場 2 / 退く 1 / 射る 1)。
 7. 番人 orc_alarm_unclear(13 件)を分けた。
    オーク 3 体・味方あり → raise_alarm(新しい枝 orc_trio_alarm): 4 件・会話 3 本(r3s1 1、
        r3s2 2、r3s3 1)・一致 4/4(規律 (b))。決め手は 4 件とも enemy_count>=3、ほかに alarm=false,
        time=night, distance>=6, arrows<=1。隣接(d1、ehp20)でも警報(「オーク三体で警報未発、
        味方に任せ先に鳴らす」)。
    夜のオーク 2 体・味方 1 以下の「弱った」線を enemy_hp<=30 から <=25 に下げた(_WEAK_HP_MAX)。
        ehp30 は警報 2 件(r2s2 決め手 alarm=false,time=night,arrows=0、r3s3 決め手 alarm=false,
        time=night,enemy=orc)、ehp20 は射る 1 件(r2s3 決め手 enemy_hp<=20)。線は 20 と 30 の間。
        orc_pair_night_alarm は 7 件・会話 6 本・一致 7/7 になる。
    昼・オーク 2 体・味方 0・離れて矢 0 → raise_alarm(新しい枝 orc_pair_day_no_arrows_alarm):
        1 件(r2s1、hp83 d7)、根拠 L5 で gap なし(規律 (c))。決め手 alarm=false, allies=0,
        enemy_count>=2。理由「味方も矢も無く二体のオークが来るので警報」。味方 1 の矢 0 は
        持ち場 1 件(gap)なので味方 0 に限る。
    昼・オーク 2 体・隣接・弱っている → melee_attack(新しい枝 orc_pair_day_melee): 1 件
        (r3s2、hp94 d1 ehp20)、根拠 L2 で gap なし(規律 (c))。決め手 distance=1, enemy_hp<=20。
    残り 5 件 → 番人 orc_alarm_unclear: 夜・味方 2 以上(隣接の斬る 2、うち 1 件 gap。d12 の警報 1、
        gap)、夜の弱ったオーク(射る 1、gap)、昼・味方 1・矢 0(持ち場 1、gap)。
 8. 番人 group_alarm_unclear(警報未のゴブリン 3 体・味方あり、11 件)を昼夜で分けた。
    昼の 7 件は全部 L2 どおり: 離れて矢あり 射る 3(r2s2、r3s2、r3s3)、離れて矢 0 持ち場 3
        (r2s2、r2s3、r3s2)、隣接 斬る 1(r1s3、根拠 L2 で gap なし)。理由に「深刻ではなく
        持ち場で待つ」「弱ったゴブリンは深刻な脅威でなく射れば足りる」。そこで昼のゴブリン 3 体・
        味方ありは深刻な脅威とせず、L2 の枝(shoot_far / no_arrows_hold / melee_adjacent)に通した
        (規律 (b)、隣接は (c))。同じ規則なので名前も同じ。
    夜の 4 件は警報 2(r2s1、r3s1、決め手 time=night)・射る 2(r1s3、r3s2)に割れる
        → 番人 group_alarm_unclear のまま。
    hp 25〜32 では据え置き(_serious_unalarmed。深刻な脅威として 3 の判定に回す)。

熱さの帳簿を b3 で数え直した見込み(答える枝、件数・一致・会話)
    no_threat_hold             51  51/51  9 本    L7      敵なし・hp>=33 → hold_position
    no_arrows_hold             38  37/38  9 本    gap     離れた敵・矢 0・(遮蔽なし、または昼) → hold_position
    shoot_far                  36  35/36  8 本以上 L2     離れたゴブリン/オーク・矢あり → shoot
    horde_alarm                18  18/18  7 本    L5      警報未・敵 4 以上 → raise_alarm
    melee_adjacent             13  13/13  5 本以上 L2     隣接のゴブリン/オーク → melee_attack
    hurt_retreat               13  13/13  8 本    L1      hp<=24・薬なし・敵あり → retreat
    night_no_arrows_cover      10   9/10  7 本    L6      離れた敵・矢 0・遮蔽あり・夜 → take_cover
    hurt_drink                  9   9/9   6 本    L1      hp<=24・薬あり → drink_potion
    hurt_handover               9   9/9   3 本    L1+L7   hp<=24・薬なし・敵なし・味方あり → retreat
    mage_first_shoot            8   7/8   6 本    L4+L2   警報未の魔術師・昼・2〜6 マス・敵 2 以下 → shoot
    orc_pair_night_alarm        7   7/7   6 本    L5+L6   警報未のオーク 2 体・夜・味方 1 以下・ehp>25 → raise_alarm
    troll_alarm                 7   6/7   5 本    L5+L3   トロル・警報未 → raise_alarm
    wounded_drink               6   6/6   4 本    L1      hp 25〜32・薬あり → drink_potion
    mage_melee                  6   6/6   5 本    L2+L4   隣接の魔術師 → melee_attack
    wounded_alarm               5   5/5   4 本    L5+L1   hp 25〜32・薬なし・警報未の深刻な脅威・3 マス以上 → raise_alarm(新)
    troll_shoot_allies          5   5/5   4 本    L2+L3   警報済みトロル・味方あり・離れて矢あり → shoot
    troll_alone_cover           5   4/5   4 本    L3+L6   警報済みトロル・味方 0・離れて・遮蔽・夜 → take_cover
    mage_far_alarm              5   5/5   3 本    L5+L4   警報未の魔術師・7 マス以上(A3 の外) → raise_alarm
    outnumbered_alarm           4   4/4   3 本    L5      警報未・敵 3・味方 0 → raise_alarm
    mage_no_arrows_alarm        4   4/4   2 本    L5+L4   警報未の魔術師・離れて矢 0 → raise_alarm
    mage_shoot                  4   4/4   3 本    L2+L4   離れた魔術師(警報済み)・矢あり → shoot
    orc_pair_day_shoot          4   4/4   3 本    L2      警報未のオーク 2 体・昼・離れて矢あり → shoot
    orc_trio_alarm              4   4/4   3 本    L5      警報未のオーク 3 体・味方あり → raise_alarm(新)
    mage_night_alarm            3   3/3   2 本    L5+L6   警報未の魔術師・夜・2〜6 マス・敵 2 以下 → raise_alarm(新)
    mage_no_arrows_cover        3   3/3   3 本    gap     警報済みの魔術師・3 マス以上・矢 0・遮蔽あり → take_cover(新)
    mage_close_in               3   3/3   3 本    L4      警報済みの魔術師・2 マス・矢 0・遮蔽なし → melee_attack(新)
    troll_alone_retreat         3   3/3   3 本    L3      警報済みトロル・味方 0・隣接・夜 → retreat(新)
    hurt_troll_alarm            3   3/3   3 本    L5+L3   hp<=24・トロル・警報未・3 マス以上 → raise_alarm
    a1_shoot                    2   2/2   1 本    A1      hp>=31・敵 9 マス以上・矢あり・昼で、ほかの読みが
                                                          射るか(hp 25〜32・薬なし)、警報済みトロルに独り(hp>=33) → shoot
    troll_melee_allies          2   2/2   2 本    L2+L3   警報済みトロル・味方あり・隣接 → melee_attack
    orc_pair_day_no_arrows_alarm 1  1/1   1 本    L5      警報未のオーク 2 体・昼・味方 0・離れて矢 0 → raise_alarm(新)
    orc_pair_day_melee          1   1/1   1 本    L2      警報未のオーク 2 体・昼・隣接・ehp<=25 → melee_attack(新)
    a3_mage_shoot               0                 A3      A3・昼・7 マス以上 → shoot(新)

棄権の番人(割れている所、証拠が足りない所。輪が審判に訊き直す所)
    wounded_no_threat      22  hp 25〜32・薬なし・敵なし(持ち場 10 / 退く 11 / 遮蔽 1)。会話ごとに
                               揃う(r2s1 r3s2 は退く、r3s3 r1s1 r1s3 は持ち場)ので状態では切れない
    hurt_no_threat         12  hp<=24・薬なし・敵なし・味方 0(持ち場 6 / 退く 6。r2s3 r3s3 が持ち場)
    wounded_alarm_unclear   9  hp 25〜32・警報未の深刻な脅威で、薬あり(警報 3 / 飲む 4 / 斬る 1 / 射る 1)
                               か、3 マス未満か、hp>=33 の読みが警報でない所
    a1_night_split          6  A1 の範囲の夜(射る 3 / 退く 3)
    orc_alarm_unclear       5  上の 7 の残り
    group_alarm_unclear     4  警報未のゴブリン 3 体・味方あり・夜(警報 2 / 射る 2)
    troll_alarm_raised      4  警報済みトロルの残り(持ち場 2 / 退く 1 / 射る 1)
    hp_ambiguous            3  hp 25〜32・薬なし・敵あり・A1 の外(射る 2 / 退く 1)
    mage_no_arrows          2  警報済みの魔術師・矢 0・遮蔽なし・3 マス以上(斬る 2、gap)、2 マスで遮蔽あり
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

# 弱った敵(夜のオーク 2 体: ehp20 は射る、ehp30 は警報。線は 20 と 30 の間)
_WEAK_HP_MAX = 25


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

    # 追補と L1 がぶつかる所(例なし)
    if _a2(s):
        return (None, "a2_hurt_conflict")
    if _a3(s):
        return (None, "a3_hurt_conflict")

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

    # 警報未の深刻な脅威
    if enemy != "none" and not s["alarm"] and _serious_unalarmed(s):
        if not s["potion"] and s["distance"] >= _ALARM_FIRST_DIST:
            act, _name = _fine(s)
            if act == "raise_alarm":
                return ("raise_alarm", "wounded_alarm")
        return (None, "wounded_alarm_unclear")

    # 追補 A2 と L1 がぶつかる所(例なし)
    if _a2(s):
        return (None, "a2_hurt_conflict")

    if s["potion"]:
        return ("drink_potion", "wounded_drink")

    if enemy == "none":
        return (None, "wounded_no_threat")

    # 追補 A1: hp>=31、薬なし、敵 9 マス以上、矢あり → 退かずに射る
    if _a1(s):
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
            if cover and dist > _MAGE_CLOSE_MAX:
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
