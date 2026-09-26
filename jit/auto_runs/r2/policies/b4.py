"""走り r2 の方針、第 4 版(b4、やり直し 1 回目)。

帳簿: 審判のラベル 436 件、会話 12 本(round1_s1〜round4_s3。以下 r1s1 … r4s3)。
b3 の答える枝のうち門の条件を割ったのは mage_no_arrows_cover(4 件で 3/4 = 75%)だけで、
ほかは b3 のまま条件を満たす(最も低いのは troll_alone_cover の 4/5 = 80%)。
この版では落ちる枝を直し、新しい追補 A4・A5・A6 を読み、r4 の例で規律 (b)(c) に届いた所を
答えにした。変えたのは次のとおり。

 0. 前に書いた b4 は、新しい枝 a5_hold が門で落ちた(例 1 件・会話 1 本で hold_position)。
    その 1 件は警報済みトロルの状態(hp92 d12 敵 5 体 味方 3 矢 0 遮蔽あり 昼、r1s2、
    根拠 L3+gap、「矢が無く敵は遠い、味方3人と門を固めて待つ」)で、gap なので規律 (c) に届かず、
    (b) の 3 件・会話 2 本にも届かない。a5_hold という答える枝はやめ、A5 がほかの行とぶつかる
    所は名前を付けた番人で棄権に戻した(下の 2)。A5 で答えが決まる所は、既にある
    no_arrows_hold がそのまま同じ答えを出している所だけ。

 1. 追補 A4(警報未・hp<=28・回復薬あり・魔術師・10 マス以上 → 警報より先に回復薬を飲む)。
    帳簿で A4 の範囲に入る例は、元の状態(hp28 魔術師 2 体 d10 ehp80 味方 2 薬あり 矢 10 夜)の
    7 件・会話 7 本だけ。飲む 5(r3s1 r3s3 r4s1 r4s2 r4s3、決め手 potion=true, distance>=10,
    hp<=28。理由「重傷で魔術師はまだ遠い、まず回復薬で持ち直す」)、警報 2(r1s1 r3s2、決め手
    enemy=mage, alarm=false, distance>=10)。b3 では番人 wounded_alarm_unclear の中。
    hp<=24 は既に hurt_drink(L1)で A4 と同じ答えなので何も変えない。
    hp 25〜28 は A4 どおり drink_potion にした(規律 (a))。これを別の枝にすると 5/7 = 71% で
    落ちる。A3 の元の状態(3/4)を mage_first_shoot に残した b3 と同じく、同じ規則(L1: 回復薬が
    あれば飲む)・同じ行動の wounded_drink に入れた。wounded_drink は 11/13 = 85% の見込みで、
    別の答えが多数の会話は r1s1 r3s2 の 2 本(会話 7 本以上の 1/3 未満)。
    A4 が A2・A3 と重なる所は、b3 の a2_hurt_conflict / a3_hurt_conflict のまま棄権。

 2. 追補 A5(警報済み・矢 0・味方 3 以上・敵 4 マス以上 → 遮蔽があっても持ち場を守る)。
    元の状態(hp42 ゴブリン 3 体 d4 味方 3 遮蔽あり 警報済み 昼)は持ち場 3・遮蔽 1 で、既に
    no_arrows_hold(「矢が無く離れた敵には持ち場で待つ」)の中。hp>=33 のゴブリン/オークで、
    昼か遮蔽なしの A5 の範囲は、どこも既に no_arrows_hold で A5 と同じ答えなので変えない。
    A5 がほかの行とぶつかる所は答えず輪に回す(A2・A3 のぶつかる所を番人にした b3 と同じ形):
      a5_night_unclear(番人): 夜・遮蔽ありのゴブリン/オーク。b3 では night_no_arrows_cover
          (L6、9/10、理由「夜に単独で矢もない、遮蔽に隠れて…」)。元の状態は昼で、夜は L6 と
          ぶつかる(夜の A3 を a3_night_unclear にしたのと同じ)。
      a5_troll_unclear(番人): 警報済みトロル・味方 3。例は上の 0 の 1 件(持ち場、gap)だけで、
          L3 とぶつかる。b3 では troll_alarm_raised(棄権)の中。
      a5_mage_unclear(番人): 警報済みの魔術師。例 1 件(hp93 d12 味方 3 遮蔽なし、r3s1)は斬る
          (決め手 enemy=mage, arrows=0, hp>=90、「弱った魔術師へ詰めて討つ」)で A5 と逆。L4 と
          ぶつかる。b3 では番人 mage_no_arrows の中。
      a5_hurt_conflict(番人): hp<=32 の A5。L1(飲む・退く)とぶつかる。

 3. 追補 A6(敵なし・hp<=30・薬なし → 味方が 1 人以上なら退き、いなければ持ち場を守る)。
    元の状態は hp28〜30 の 4 つ。帳簿 12 本では答えが会話ごとに揃い(r2s1 r4s3 は退く、r3s3 r4s1
    は持ち場)、味方の有無では切れない。
      hp 25〜30・味方あり(A6 は退く): 15 件、退く 9 / 持ち場 6(60%)。持ち場が多数の会話は
          r3s3 r4s1 で 6 本中 2 本(1/3)。
      hp 25〜30・味方 0(A6 は持ち場): 16 件、持ち場 7 / 退く 8 / 遮蔽 1(44%)。
      hp<=24・味方 0(A6 は持ち場): 15 件、持ち場 6 / 退く 9(40%)、退くが多数の会話 6 本。
    どれも枝にすれば 80% に届かず会話の割れでも落ちるので、番人 wounded_no_threat /
    hurt_no_threat のまま棄権。hp<=24・味方あり(A6 は退く)は既に hurt_handover(9/10)で同じ答え。

 4. 新しい枝 mild_no_threat_hold: hp 31〜32・薬なし・敵なし → hold_position。
    6 件・会話 6 本・一致 5/6 = 83%(規律 (b))。持ち場 r2s2 r2s3 r4s1 r4s2 r4s3、退く r2s1 の 1 件。
    決め手 hp>=31 / hp>=32,allies=1 / enemy=none(L7)。理由「重傷とまでは言えず脅威も無いので
    持ち場を守る」「体力32は重傷と見ず持ち場を守る」。線 31(_MILD_MIN)は割れている 30 と
    持ち場の 31 の間(A6 の hp<=30 とも A1 の hp>=31 とも合う)。

 5. 番人 hp_ambiguous(hp 25〜32・薬なし・敵あり・A1 の外、6 件)を分けた。
      新しい枝 wounded_retreat: hp 25〜30・敵が弱っていない → retreat。4 件・会話 3 本(r3s2、
          r4s2、r4s3 2)・一致 4/4(規律 (b))。決め手 hp<=25/26/28, potion=false(4 件とも)、
          distance=1、arrows=0。理由「重傷で回復薬が無いので退く」「隣接されたが重傷で薬が無いので
          退く」。hp の線は退く最大の 28 と射る 32 の間の 30。
      弱った敵(enemy_hp<=25、_WEAK_HP_MAX)は射る 1 件(r2s3 hp26 ゴブリン d7 ehp10、決め手
          enemy_hp<=10、gap)なので番人 hp_ambiguous に残す。
      新しい枝 mild_shoot: hp 31〜32・昼・A1 の外で、hp>=33 の読みが shoot_far の所 → shoot。
          1 件(r2s2 hp32 ゴブリン 2 体 d6 矢 18 警報済み)、根拠 L2 で gap なし(規律 (c))。決め手
          distance>=2, arrows=18, enemy=goblin。理由「ゴブリンは離れており矢も多いので射る」。
          夜は a1_night_split が割れているので答えない。
 6. 番人 orc_alarm_unclear から、隣接のオーク 2 体・味方 2 以上 → melee_adjacent。
    5 件・会話 4 本(r1s3、r3s2、r4s1、r4s2 2)・一致 5/5(規律 (b))。決め手は 5 件とも
    distance=1、ほかに allies>=2 / allies>=3、hp>=66 / hp>=91。4 件が根拠 L2 だけ。理由
    「オークが隣接し味方も多いので近接で戦う」。L2 の隣接の規則なので名前は melee_adjacent
    (b3 で昼のゴブリン 3 体の隣接を通したのと同じ)。夜 3 件・昼 2 件、ehp は 30〜70。
    昼の弱ったオーク(orc_pair_day_melee)を先に見る。味方 1 以下の昼の隣接は例が無く番人のまま。
    残り 4 件(持ち場 2 gap、警報 1、射る 1)は orc_alarm_unclear のまま。
 7. mage_no_arrows_cover を 4 マス以上に狭めた(門で落ちる所の直し)。
    r4s3 の hp72 魔術師 d3 ehp40 遮蔽あり 夜 → 斬る(決め手 enemy=mage, arrows=0,
    enemy_hp<=40、「矢が無いので弱った魔術師に詰めて仕留める」)で 3/4 = 75% になった。遮蔽の
    3 件は d5〜7(r2s2 d5、r2s1 d6、r3s1 d7。理由「矢が無く魔術師は遠いので遮蔽で呪文を避ける」)。
    線 4(_MAGE_COVER_MIN)を 3 と 5 の間に置き、3 マスは番人 mage_no_arrows。
    mage_no_arrows_cover は 3/3・会話 3 本に戻る。

熱さの帳簿を b4 で数え直した見込み(答える枝、件数・一致・会話)
    no_threat_hold             63  63/63  12 本   L7      敵なし・hp>=33 → hold_position
    no_arrows_hold             47  46/47  12 本   gap     離れた敵・矢 0・(遮蔽なし、または昼) → hold_position
    shoot_far                  42  41/42  11 本   L2      離れたゴブリン/オーク・矢あり → shoot
    horde_alarm                19  19/19   8 本   L5      警報未・敵 4 以上 → raise_alarm
    melee_adjacent             18  18/18   5 本+4 本 L2   隣接のゴブリン/オーク(オーク 2 体・味方 2 以上を足した) → melee_attack
    hurt_retreat               15  15/15   9 本   L1      hp<=24・薬なし・敵あり → retreat
    wounded_drink              13  11/13   7 本以上 L1+A4 hp 25〜32・薬あり(A4 の hp 25〜28 を足した) → drink_potion
    hurt_drink                 10  10/10   7 本   L1      hp<=24・薬あり → drink_potion
    night_no_arrows_cover      10   9/10   7 本   L6      離れた敵・矢 0・遮蔽あり・夜(A5 の外) → take_cover
    hurt_handover              10   9/10   4 本   L1+A6   hp<=24・薬なし・敵なし・味方あり → retreat
    troll_alarm                10   9/10   6 本   L5+L3   トロル・警報未 → raise_alarm
    mage_first_shoot            8   7/8    6 本   L4+L2   警報未の魔術師・昼・2〜6 マス・敵 2 以下 → shoot
    mage_melee                  8   8/8    7 本   L2+L4   隣接の魔術師 → melee_attack
    wounded_alarm               8   8/8    7 本   L5+L1   hp 25〜32・薬なし・警報未の深刻な脅威・3 マス以上 → raise_alarm
    orc_pair_night_alarm        7   7/7    6 本   L5+L6   警報未のオーク 2 体・夜・味方 1 以下・ehp>25 → raise_alarm
    mild_no_threat_hold         6   5/6    6 本   L7      hp 31〜32・薬なし・敵なし → hold_position(新)
    mage_no_arrows_alarm        6   6/6    3 本   L5+L4   警報未の魔術師・離れて矢 0 → raise_alarm
    mage_far_alarm              6   6/6    4 本   L5+L4   警報未の魔術師・7 マス以上(A3 の外) → raise_alarm
    troll_shoot_allies          5   5/5    4 本   L2+L3   警報済みトロル・味方あり・離れて矢あり → shoot
    troll_alone_cover           5   4/5    4 本   L3+L6   警報済みトロル・味方 0・離れて・遮蔽・夜 → take_cover
    mage_shoot                  5   5/5    4 本   L2+L4   離れた魔術師(警報済み)・矢あり → shoot
    outnumbered_alarm           4   4/4    3 本   L5      警報未・敵 3・味方 0 → raise_alarm
    orc_pair_day_shoot          4   4/4    3 本   L2      警報未のオーク 2 体・昼・離れて矢あり → shoot
    orc_trio_alarm              4   4/4    3 本   L5      警報未のオーク 3 体・味方あり → raise_alarm
    wounded_retreat             4   4/4    3 本   L1      hp 25〜30・薬なし・敵あり・敵が弱っていない → retreat(新)
    mage_no_arrows_cover        3   3/3    3 本   gap     警報済みの魔術師・4 マス以上・矢 0・遮蔽あり → take_cover(狭めた)
    mage_close_in               3   3/3    3 本   L4      警報済みの魔術師・2 マス・矢 0・遮蔽なし → melee_attack
    hurt_troll_alarm            3   3/3    3 本   L5+L3   hp<=24・トロル・警報未・3 マス以上 → raise_alarm
    troll_alone_retreat         3   3/3    3 本   L3      警報済みトロル・味方 0・隣接・夜 → retreat
    mage_night_alarm            3   3/3    2 本   L5+L6   警報未の魔術師・夜・2〜6 マス・敵 2 以下 → raise_alarm
    a1_shoot                    3   3/3    2 本   A1      hp>=31・敵 9 マス以上・矢あり・昼 → shoot
    troll_melee_allies          2   2/2    2 本   L2+L3   警報済みトロル・味方あり・隣接 → melee_attack
    orc_pair_day_no_arrows_alarm 1  1/1    1 本   L5      警報未のオーク 2 体・昼・味方 0・離れて矢 0 → raise_alarm
    orc_pair_day_melee          1   1/1    1 本   L2      警報未のオーク 2 体・昼・隣接・ehp<=25 → melee_attack
    mild_shoot                  1   1/1    1 本   L2      hp 31〜32・薬なし・昼・A1 の外・読みが shoot_far → shoot(新)
    a3_mage_shoot               0                 A3      A3・昼・7 マス以上 → shoot
    (A5 の番人が night_no_arrows_cover・mage_no_arrows_cover・hurt_* から抜く例は、帳簿の
     食い違いの一覧には無く、あっても一致している例が減るだけ。)

棄権の番人(割れている所、証拠が足りない所。輪が審判に訊き直す所)
    wounded_no_threat      31  hp 25〜30・薬なし・敵なし(持ち場 13 / 退く 17 / 遮蔽 1)。A6 と逆の会話が多い
    hurt_no_threat         15  hp<=24・薬なし・敵なし・味方 0(退く 9 / 持ち場 6)。A6 と逆が多数
    a1_night_split          6  A1 の範囲の夜(射る 3 / 退く 3)
    group_alarm_unclear     6  警報未のゴブリン 3 体・味方あり・夜(警報 3 / 射る 2 / 斬る 1)
    wounded_alarm_unclear   5  hp 25〜32・警報未の深刻な脅威で A4 の外の薬あり、3 マス未満、
                               hp>=33 の読みが警報でない所(飲む 2 / 斬る 1 / 警報 1 / 射る 1)
    orc_alarm_unclear       4  警報未のオーク 2 体の残り(持ち場 2 / 警報 1 / 射る 1)
    troll_alarm_raised      3  警報済みトロルの残り(持ち場 1 / 退く 1 / 射る 1)
    mage_no_arrows          3  警報済みの魔術師・矢 0 の残り(斬る 2、gap / 飲む 1)。3 マス・遮蔽ありを含む
    hp_ambiguous            1  hp 25〜30 の弱った敵、hp 31〜32 の A1・mild_shoot の外(射る 1、gap)
    a5_troll_unclear        1  A5 の警報済みトロル(持ち場 1、gap)
    a5_mage_unclear         1  A5 の魔術師(斬る 1、gap)
    a5_night_unclear        0  A5 の夜・遮蔽ありのゴブリン/オーク
    a5_hurt_conflict        0  hp<=32 の A5
    mage_alarm_unclear      0  警報未の魔術師・2〜6 マス・敵 3・味方あり
    a3_night_unclear        0  夜の A3
    a2_hurt_conflict        0  hp<=32 の A2
    a3_hurt_conflict        0  hp<=32 の A3(hp 25〜32 は A4 と重なる所)
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
_MILD_MIN = 31      # hp 31〜32: 敵なし・昼に射る所ではひどいと見ない。hp 25〜30 は退く側(b4)

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
# 警報済みの魔術師・矢 0・遮蔽あり: この距離以上なら遮蔽(斬る d3 と遮蔽 d5 の間、b4)
_MAGE_COVER_MIN = 4

# 弱った敵(夜のオーク 2 体: ehp20 は射る、ehp30 は警報。線は 20 と 30 の間)
_WEAK_HP_MAX = 25

# 警報未のオーク 2 体が隣接: 味方がこれ以上なら斬る(例は味方 2・3、b4)
_ORC_MELEE_ALLIES_MIN = 2


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
    """追補 A4 の範囲: 警報未・hp<=28・回復薬あり・魔術師・10 マス以上。"""
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

    # 追補と L1 がぶつかる所(例なし)
    if _a2(s):
        return (None, "a2_hurt_conflict")
    if _a3(s):
        return (None, "a3_hurt_conflict")
    if _a5(s):
        return (None, "a5_hurt_conflict")

    # L1(A4 の hp<=24 も同じ答え)
    if s["potion"]:
        return ("drink_potion", "hurt_drink")
    if enemy == "none":
        # A6: 味方がいれば退く(帳簿 9/10)。味方 0 の持ち場は帳簿と逆が多数なので棄権
        if s["allies"] >= 1:
            return ("retreat", "hurt_handover")
        return (None, "hurt_no_threat")
    return ("retreat", "hurt_retreat")


def _wounded(s):
    """hp 25〜32: ひどいかどうかが会話で割れる所。"""
    enemy = s["enemy"]
    hp = s["hp"]
    night = s["time"] == "night"

    # 追補 A5 と L1 がぶつかる所
    if _a5(s):
        return (None, "a5_hurt_conflict")

    # 警報未の深刻な脅威
    if enemy != "none" and not s["alarm"] and _serious_unalarmed(s):
        if s["potion"]:
            # 追補 A4: 警報より先に回復薬(L1 の飲む規則と同じ枝)
            if _a4(s):
                if _a2(s):
                    return (None, "a2_hurt_conflict")
                if _a3(s):
                    return (None, "a3_hurt_conflict")
                return ("drink_potion", "wounded_drink")
            return (None, "wounded_alarm_unclear")
        if s["distance"] >= _ALARM_FIRST_DIST:
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
        if hp >= _MILD_MIN:
            return ("hold_position", "mild_no_threat_hold")
        # A6 は帳簿で会話ごとに割れる
        return (None, "wounded_no_threat")

    # 追補 A1: hp>=31、薬なし、敵 9 マス以上、矢あり → 退かずに射る
    if _a1(s):
        if night:
            return (None, "a1_night_split")
        act, _name = _fine(s)
        if act == "shoot":
            return ("shoot", "a1_shoot")
        return (None, "hp_ambiguous")

    if hp >= _MILD_MIN:
        # hp 31〜32: 昼に離れたゴブリン/オークを射る所だけ(L2、gap なしの 1 件)
        if not night:
            _act, name = _fine(s)
            if name == "shoot_far":
                return ("shoot", "mild_shoot")
        return (None, "hp_ambiguous")

    # hp 25〜30・薬なし・敵あり: L1 で退く。弱った敵は射る例があるので棄権
    if s["enemy_hp"] <= _WEAK_HP_MAX:
        return (None, "hp_ambiguous")
    return ("retreat", "wounded_retreat")


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
            if _a5(s):
                return (None, "a5_troll_unclear")
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
                if dist == 1 and allies >= _ORC_MELEE_ALLIES_MIN:
                    return ("melee_attack", "melee_adjacent")
            elif dist >= 2:
                if arrows >= 1:
                    return ("shoot", "orc_pair_day_shoot")
                if allies == 0:
                    return ("raise_alarm", "orc_pair_day_no_arrows_alarm")
            elif weak:
                return ("melee_attack", "orc_pair_day_melee")
            elif allies >= _ORC_MELEE_ALLIES_MIN:
                return ("melee_attack", "melee_adjacent")
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
            if _a5(s):
                return (None, "a5_mage_unclear")
            if cover and dist >= _MAGE_COVER_MIN:
                return ("take_cover", "mage_no_arrows_cover")
            if not cover and dist <= _MAGE_CLOSE_MAX:
                return ("melee_attack", "mage_close_in")
            return (None, "mage_no_arrows")
        if cover and night:
            if _a5(s):
                return (None, "a5_night_unclear")
            return ("take_cover", "night_no_arrows_cover")
        # A5 の昼・遮蔽なしの範囲もここ(同じ答え)
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
