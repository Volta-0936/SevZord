"""走り r2 の方針、第 5 版(b5)。

帳簿: 審判のラベル 508 件、会話 15 本(round1_s1〜round5_s3。以下 r1s1 … r5s3)。
b4 の答える枝は、この帳簿でもすべて門の条件を満たす(最も低いのは troll_alone_cover の
4/5 = 80%、wounded_drink は 11/13 = 85% で別の答えが多数の会話は r1s1 r3s2 の 2 本、会話 11 本の
1/3 未満)。この版では新しい追補 A7 を読み、r5 の例で規律 (a)(b)(c) に届いた番人を答えにした。
変えたのは次のとおり。

 1. 追補 A7(敵なし・hp>=31・薬なし → 味方がいても退かずに持ち場を守る)。
    hp>=33 は no_threat_hold、hp 31〜32 は b4 の mild_no_threat_hold がすでに同じ答え。コードは
    変えず、mild_no_threat_hold の根拠を L7+A7 とした(規律 (a))。帳簿 9 件・会話 9 本・一致 8/9
    (退く 1 件は r2s1 hp32 味方 2、決め手 hp<=33, potion=false, allies>=2)。

 2. 新しい枝 a5_hold: 追補 A5 がトロル・夜の遮蔽とぶつかるとして番人にしていた所 → hold_position。
    番人 a5_troll_unclear と a5_night_unclear の例が 4 件・会話 3 本(r1s2、r5s1 2、r5s2)で、
    4 件とも持ち場(規律 (a) で A5 をそのまま読み、(b) も満たす)。
      r1s2 hp92 トロル 5 体 d12 味方 3 昼 [L3+gap] 決め手 arrows=0, distance>=12, allies>=3
          「矢が無く敵は遠い、味方3人と門を固めて待つ」
      r5s1 hp82 トロル 2 体 d4 味方 3 遮蔽 夜 [A5] 決め手 alarm=true, arrows=0, allies>=3
          「警報済みで味方が三人、矢が無いので持ち場を守る」
      r5s2 hp87 トロル 4 体 d9 味方 3 昼 [A5] 「警報済・矢なし・味方3人以上で遠い敵には持ち場を守る」
      r5s1 hp85 ゴブリン d7 味方 3 遮蔽 夜 [A5] 決め手 alarm=true, arrows=0, allies>=3
          「警報済みで矢が無く味方が多いので持ち場を守る」
    A5 の昼・遮蔽なしのゴブリン/オークは b4 のまま no_arrows_hold(同じ答え)。
    A5 の魔術師(a5_mage_unclear: 斬る 1 / 遮蔽 1、どちらも gap)と hp 25〜32 の A5 は番人のまま。

 3. A5 と L1 がぶつかる所のうち、hp<=24・回復薬あり → drink_potion(既にある hurt_drink、L1)。
    例 1 件(r3s3 hp12 魔術師 d5 味方 3 矢 0 遮蔽 警報済み 夜)、根拠 L1 だけで gap なし、
    決め手 hp<=12, potion=true、「瀕死なので手持ちの回復薬を飲む」(規律 (c))。
    hp<=24 で薬なし、hp 25〜32 の A5 は例が無く番人 a5_hurt_conflict のまま。
    hurt_drink は 10/10(会話 7 本+r3s3)。

 4. troll_alone_retreat を広げた: 警報済みトロル・味方 0 で、弱っていない(enemy_hp>25)所の
    退く規則(L3「一人で相手にするには強すぎる」)。番人 troll_alarm_raised から 6 件。
      昼(A1 の外): 5 件・会話 2 本(r5s1、r5s3 4)、一致 5/5(規律 (b))。
          r5s1 hp48 トロル 2 体 d5 [L2,L3+gap] 決め手 enemy=troll, enemy_count>=2, allies=0
              「トロル二体に単独で挑むのは無駄死になので退く」
          r5s3 hp83 d4 / hp68 d1 / hp88 d1 [L3,L0+gap] 決め手 enemy=troll, allies=0(ほかに
              enemy_count>=2 / distance<=1)「一人でトロルとは戦えないので退く」
          r5s3 hp95 トロルを含む 4 体 d4 矢 0 [L3,L0](gap なし)「…四体には勝てないので退く」
      夜・遮蔽なし・離れて(A1 の外): 1 件(r5s3 hp74 d6 [L3,L6+gap] 決め手 enemy=troll,
          allies=0, time=night「夜に単独でトロルを相手にできないので退く」)。
    決め手はどれも enemy=troll と allies=0 で、b4 の troll_alone_retreat(夜・隣接、3/3、
    決め手 enemy=troll 3, allies=0 3)と同じ規則なので同じ名前にした(b4 で melee_adjacent を
    広げたのと同じ形)。枝は 9/9、会話 3 本+2 本。
    弱った(enemy_hp<=25、既にある _WEAK_HP_MAX)トロルは番人に残す。例は 2 件で、どちらも
    決め手に enemy_hp を挙げて退かない: r3s1 hp83 昼 d5 ehp10 → 持ち場(「瀕死のトロルに単独で
    突っ込まず門を守り援軍を待つ」)、r3s2 hp94 夜 d8 ehp20 → 射る(「トロルは遠く瀕死、近づく前に
    射て削る」)。線 25 は弱った 20 と退く最小の 30 の間。
    夜・遮蔽なしで A1 の範囲は例が無く番人のまま。夜・遮蔽ありは b4 のまま troll_alone_cover。

 5. a3_mage_shoot を、A3 と A1 がともに掛かる夜に広げた(hp>=31、薬なし)。
    例 1 件(r5s3 hp31 魔術師一体 d11 ehp20 矢 15 警報未 夜)、根拠 A3・A1 で gap なし、
    決め手 enemy_hp<=40, arrows>=11, hp>=31、「弱った魔術師一体を警報より先に射る」(規律 (c))。
    b4 では番人 wounded_alarm_unclear の中。A1 の掛からない夜の A3 は a3_night_unclear のまま、
    hp 31〜32 で昼の A3 の 7〜8 マスも wounded_alarm_unclear のまま。

 6. wounded_retreat を、警報未の深刻な脅威が 3 マス未満に迫る hp 25〜30・薬なしに広げた(L1)。
    例 1 件(r5s1 hp28 オーク 2 体 d2 ehp30 味方 0 夜)、決め手 hp<=28, potion=false, distance<=2、
    「深手で薬も無く敵が迫っているので退く」。wounded_retreat の決め手(hp<=25/26/28,
    potion=false, distance=1)・理由(「隣接されたが重傷で薬が無いので退く」)と同じ規則。
    枝は 5/5・会話 4 本(r3s2、r4s2、r4s3、r5s1)。弱った敵は b4 と同じく答えない。

変えなかった所(帳簿 15 本で数え直しても割れる)
    A6 の敵なし・hp<=30・薬なし: r5 の会話 3 本は A6 どおりに揃うが、r1〜r4 が会話ごとに割れる。
      hp 25〜30・味方あり(A6 は退く): 23 件、退く 17 / 持ち場 6(74%)、持ち場が多数は r3s3 r4s1。
      hp 25〜30・味方 0(A6 は持ち場): 18 件、持ち場 9 / 退く 8 / 遮蔽 1(50%)。
      hp<=24・味方 0(A6 は持ち場): 25 件、持ち場 16 / 退く 9(64%)、退くが多数の会話 6 本 / 11 本。
      どれも 80% に届かないので番人 wounded_no_threat / hurt_no_threat のまま。
    group_alarm_unclear の隣接(斬る 2 件・会話 2 本、r4s3 は gap)は (b)(c) に届かない。
    orc_alarm_unclear の昼・離れて矢 0・味方あり(持ち場 2 gap / 警報 1)は割れている。
    a1_night_split(射る 3 / 退く 3)、mage_no_arrows、hp_ambiguous、mage_alarm_unclear(1 件、gap)
    も b4 のまま。

熱さの帳簿を b5 で数え直した見込み(答える枝、件数・一致・会話)
    no_threat_hold             66  66/66  14 本   L7+A7   敵なし・hp>=33 → hold_position
    no_arrows_hold             56  55/56  15 本   gap     離れた敵・矢 0・(遮蔽なし、または昼) → hold_position
    shoot_far                  54  53/54  14 本   L2      離れたゴブリン/オーク・矢あり → shoot
    horde_alarm                20  20/20   9 本   L5      警報未・敵 4 以上 → raise_alarm
    melee_adjacent             19  19/19   9 本   L2      隣接のゴブリン/オーク → melee_attack
    hurt_retreat               15  15/15   9 本   L1      hp<=24・薬なし・敵あり → retreat
    wounded_drink              13  11/13  11 本   L1+A4   hp 25〜32・薬あり → drink_potion
    hurt_drink                 10  10/10   7 本+1 本 L1   hp<=24・薬あり(A5 の所を足した) → drink_potion
    troll_alarm                10   9/10   6 本   L5+L3   トロル・警報未 → raise_alarm
    night_no_arrows_cover      10   9/10   7 本   L6      離れた敵・矢 0・遮蔽あり・夜(A5 の外) → take_cover
    hurt_handover              10   9/10   4 本   L1+A6   hp<=24・薬なし・敵なし・味方あり → retreat
    troll_alone_retreat         9   9/9    3 本+2 本 L3   警報済みトロル・味方 0・弱っていない・遮蔽に隠れない所 → retreat(広げた)
    mild_no_threat_hold         9   8/9    9 本   L7+A7   hp 31〜32・薬なし・敵なし → hold_position
    wounded_alarm               9   9/9    8 本   L5+L1   hp 25〜32・薬なし・警報未の深刻な脅威・3 マス以上 → raise_alarm
    mage_shoot                  8   8/8    6 本   L2+L4   離れた魔術師(警報済み)・矢あり → shoot
    mage_first_shoot            8   7/8    6 本   L4+L2   警報未の魔術師・昼・2〜6 マス・敵 2 以下 → shoot
    mage_melee                  8   8/8    7 本   L2+L4   隣接の魔術師 → melee_attack
    orc_pair_night_alarm        7   7/7    6 本   L5+L6   警報未のオーク 2 体・夜・味方 1 以下・ehp>25 → raise_alarm
    mage_no_arrows_alarm        6   6/6    3 本   L5+L4   警報未の魔術師・離れて矢 0 → raise_alarm
    mage_far_alarm              6   6/6    4 本   L5+L4   警報未の魔術師・7 マス以上(A3 の外) → raise_alarm
    troll_shoot_allies          5   5/5    4 本   L2+L3   警報済みトロル・味方あり・離れて矢あり → shoot
    troll_alone_cover           5   4/5    4 本   L3+L6   警報済みトロル・味方 0・離れて・遮蔽・夜 → take_cover
    wounded_retreat             5   5/5    4 本   L1      hp 25〜30・薬なし・敵あり・弱っていない → retreat(広げた)
    a5_hold                     4   4/4    3 本   A5      A5 のトロル・A5 の夜の遮蔽あり → hold_position(新)
    outnumbered_alarm           4   4/4    3 本   L5      警報未・敵 3・味方 0 → raise_alarm
    orc_pair_day_shoot          4   4/4    3 本   L2      警報未のオーク 2 体・昼・離れて矢あり → shoot
    orc_trio_alarm              4   4/4    3 本   L5      警報未のオーク 3 体・味方あり → raise_alarm
    mage_close_in               3   3/3    3 本   L4      警報済みの魔術師・2 マス・矢 0・遮蔽なし → melee_attack
    hurt_troll_alarm            3   3/3    3 本   L5+L3   hp<=24・トロル・警報未・3 マス以上 → raise_alarm
    mage_night_alarm            3   3/3    2 本   L5+L6   警報未の魔術師・夜・2〜6 マス・敵 2 以下 → raise_alarm
    a1_shoot                    3   3/3    2 本   A1      hp>=31・敵 9 マス以上・矢あり・昼 → shoot
    troll_melee_allies          2   2/2    2 本   L2+L3   警報済みトロル・味方あり・隣接 → melee_attack
    mage_no_arrows_cover        2   2/2    2 本   gap     警報済みの魔術師・4 マス以上・矢 0・遮蔽あり → take_cover
    a3_mage_shoot               1   1/1    1 本   A3+A1   A3・昼 7 マス以上、または A1 も掛かる夜 → shoot(広げた)
    orc_pair_day_no_arrows_alarm 1  1/1    1 本   L5      警報未のオーク 2 体・昼・味方 0・離れて矢 0 → raise_alarm
    orc_pair_day_melee          1   1/1    1 本   L2      警報未のオーク 2 体・昼・隣接・ehp<=25 → melee_attack
    mild_shoot                  1   1/1    1 本   L2      hp 31〜32・薬なし・昼・A1 の外・読みが shoot_far → shoot

棄権の番人(割れている所、証拠が足りない所。輪が審判に訊き直す所)
    wounded_no_threat      41  hp 25〜30・薬なし・敵なし(持ち場 15 / 退く 25 / 遮蔽 1)
    hurt_no_threat         25  hp<=24・薬なし・敵なし・味方 0(持ち場 16 / 退く 9)
    group_alarm_unclear     7  警報未のゴブリン 3 体・味方あり・夜(警報 3 / 射る 2 / 斬る 2)
    a1_night_split          6  hp 31〜32 の A1 の範囲の夜(射る 3 / 退く 3)
    orc_alarm_unclear       6  警報未のオーク 2 体の残り(警報 3 / 持ち場 2 / 射る 1)
    troll_alarm_raised      5  警報済みトロルの残り: 味方 1〜2 で矢 0、弱ったトロルに一人、
                               夜・遮蔽なしの A1(持ち場 2 / 退く 1 / 射る 1 / 遮蔽 1)
    wounded_alarm_unclear   5  hp 25〜32・警報未の深刻な脅威で A4 の外の薬あり、hp 31〜32 か
                               弱った敵の 3 マス未満、hp>=33 の読みが警報でない所
                               (飲む 2 / 斬る 1 / 警報 1 / 射る 1)
    mage_no_arrows          4  警報済みの魔術師・矢 0 の残り(斬る 2 / 飲む 1 / 持ち場 1)
    a5_mage_unclear         2  A5 の魔術師(斬る 1 / 遮蔽 1、どちらも gap)
    hp_ambiguous            2  hp 25〜30 の弱った敵、hp 31〜32 の A1・mild_shoot の外(射る 1 / 警報 1)
    mage_alarm_unclear      1  警報未の魔術師・2〜6 マス・敵 3・味方あり(警報 1、gap)
    a5_hurt_conflict        0  hp<=24・薬なしの A5、hp 25〜32 の A5
    a3_night_unclear        0  A1 の掛からない夜の A3
    a2_hurt_conflict        0  hp<=32 の A2
    a3_hurt_conflict        0  hp<=32 の A3 で A4 と重なる所
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
_MILD_MIN = 31      # hp 31〜32: 敵なし・昼に射る所ではひどいと見ない(A1・A7 とも合う)。hp 25〜30 は退く側

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

# 弱った敵(夜のオーク 2 体: ehp20 は射る、ehp30 は警報。一人のトロル: ehp10・20 は退かず、
# ehp30 以上は退く。線は 20 と 30 の間)
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


def _weak(s):
    """敵が弱っている(敵がいる時だけ呼ぶ)。"""
    return s["enemy_hp"] <= _WEAK_HP_MAX


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
        # 回復薬があれば L1 で飲む(r3s3 の 1 件、根拠 L1 のみ、b5)
        if s["potion"]:
            return ("drink_potion", "hurt_drink")
        return (None, "a5_hurt_conflict")

    # L1(A4 の hp<=24 も同じ答え)
    if s["potion"]:
        return ("drink_potion", "hurt_drink")
    if enemy == "none":
        # A6: 味方がいれば退く(帳簿 9/10)。味方 0 の持ち場は帳簿で 64% なので棄権
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
            # 追補 A3 と A1 がともに射ると言う所(hp 31〜32・薬なし、b5)
            if _a3(s) and _a1(s):
                return ("shoot", "a3_mage_shoot")
            act, _name = _fine(s)
            if act == "raise_alarm":
                return ("raise_alarm", "wounded_alarm")
        elif hp < _MILD_MIN and not _weak(s):
            # 3 マス未満に迫られ、薬が無い: L1 で退く(b5)
            return ("retreat", "wounded_retreat")
        return (None, "wounded_alarm_unclear")

    # 追補 A2 と L1 がぶつかる所(例なし)
    if _a2(s):
        return (None, "a2_hurt_conflict")

    if s["potion"]:
        return ("drink_potion", "wounded_drink")

    if enemy == "none":
        if hp >= _MILD_MIN:
            # L7+A7
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
    if _weak(s):
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
                # 追補 A5(b5: 帳簿 3 件・会話 3 本、全部持ち場)
                return ("hold_position", "a5_hold")
            return (None, "troll_alarm_raised")
        # 味方 0(L3: 一人で相手にするには強すぎる)
        if night:
            if dist == 1:
                return ("retreat", "troll_alone_retreat")
            if cover:
                return ("take_cover", "troll_alone_cover")
            if _weak(s) or _a1(s):
                return (None, "troll_alarm_raised")
            return ("retreat", "troll_alone_retreat")
        if _a1(s):
            return ("shoot", "a1_shoot")
        if _weak(s):
            # 弱ったトロルには退かない例(持ち場・射る)があり、割れる
            return (None, "troll_alarm_raised")
        return ("retreat", "troll_alone_retreat")

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
                    # A3 と A1 がともに掛かる夜は射る(b5)
                    if _a1(s):
                        return ("shoot", "a3_mage_shoot")
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
            weak = _weak(s)
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
                # 追補 A5: 遮蔽があっても持ち場(b5: r5s1 の 1 件、根拠 A5)
                return ("hold_position", "a5_hold")
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
