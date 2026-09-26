"""走り r2 の方針、第 2 版(b2)。

帳簿: 審判のラベル 264 件、会話 6 本(round1_s1/s2/s3、round2_s1/s2/s3、以下 r1s1 … r2s3)。
指示文に追補 A1 が加わった。
b1 の答える枝はどれも門の条件を満たしている(不一致は shoot_far の 1 件だけで、別の答えを
多数にした会話は 1 本)ので残す。b1 が答えていた状態の行き先は、下の 3 の注の場合を除いて変わらない。

この版で変えたこと
 1. 追補 A1 を枝 a1_shoot_far(→ shoot)にした。規律 (a)。
    範囲: 31<=hp<33・回復薬なし・敵あり・distance>=9・arrows>=1 で、しかも hp>=33 の規則が
    射る(shoot_far / mage_shoot / troll_shoot_allies)状態だけ。hp>=33 でも警報・遮蔽・棄権に
    なる状態(警報未のトロルや群れなど)は、A1 が警報について何も言わないので hp_ambiguous のまま。
    回復薬ありも hp_ambiguous のまま: A1 は「退かずに」射ると言うだけで、飲むかどうかは決めていない
    (r1s2 は hp=31・d12・薬ありで飲んでいる)。
    帳簿のこの範囲 6 件は A1 より前のラベルで、shoot 3(訊き直した状態 hp=31 goblin d9 の
    r1s1 r2s2 r2s3)・retreat 3(同じ状態の r2s1、hp=32 orc d9 味方 3 の r2s1、hp=31 orc 4 体 d10 の r2s2)。
    A1 はこの割れを訊き直した会話の多数(shoot 3 / retreat 1)から足された一文なので、A1 に従う。
 2. 「ひどく傷ついている」の上限を hp<=20 から hp<=30 に上げた(_HURT_MAX)。
    審判の決め手は傷の側が hp<=30(hp_ambiguous で 15 件、hurt_no_threat で 3 件)が最も多く、ほかに
    hp<=21 / <=26 / <=28 / <=31(r1s2)/ <=33(r2s1)。平気の側は hp>=31(r1s1 射る、r2s3 留まる)・
    hp>=32(r2s2 留まる)。31〜32 は会話で割れるので、線は 30 と 31 の間に置いた
    (hp>=30 を平気とした r1s3 の 1 件は、敵なし・味方 0 で下の棄権に入る)。
    hp 21〜30 はこれで L1 の枝に入る:
      hurt_drink(薬あり): 6/6、会話 5 本(r1s2 r1s3 r2s1×2 r2s2 r2s3)。決め手 potion=true, hp<=21〜30。
        r2s3 のゴブリン 3 体・味方 1(hp=26)も「ゴブリン相手なら回復が先」で飲む。
      hurt_retreat(薬なし・敵あり): 7/8、会話 5 本。retreat 7 のうち 4 件は訊き直した状態
        hp=23 の隣接トロル(r1s1 r2s1 r2s2 r2s3 が全員 retreat)、ほかにオーク 2 体 d6(r1s1)・
        ゴブリン d2(r1s2)・ゴブリン d8(r2s1)。外れは r2s3 の 1 件(hp=26、瀕死のゴブリン
        enemy_hp=10 を射る)。決め手 hp<=30, potion=false。
    hp 31〜32 は A1 の範囲を除いて hp_ambiguous のまま(7 件: drink 2・hold 2・raise 1・retreat 1・shoot 1)。
 3. 新しい枝 hurt_far_alarm: hp<=30・警報未・深刻な脅威が離れている(distance>=2)→ raise_alarm。
    深刻な脅威はトロル・魔術師・敵 4 以上・味方 0 で敵 3 以上(hp>=33 で警報になる群れと同じ線)。
    5/5、会話 4 本: トロル d12 hp17 薬あり(r1s3)・d10 hp10(r2s2)・d5 hp13(r2s3)、
    魔術師 d10 hp28 薬あり(r1s1)、オーク 3 体・味方 0 d3 hp27 薬あり(r2s3)。
    決め手 alarm=false と enemy=troll / enemy=mage / enemy_count>=3,allies=0 と distance>=5/10/12。
    理由は「まだ遠い、薬より先に警報」。隣接は L1 のまま(隣接トロル hp=23 薬なし retreat 4/4・会話 4 本、
    hp=14 薬あり drink 1)。線は隣接の 1 と最も近い例 3 の間、L2 の「隣接/離れて」の境に置いた。
    番人 hurt_vs_alarm はこれで無くなった。
    注: b1 が hp<=20 で drink / retreat と答えていた「警報未の魔術師・群れが離れている」状態は、
    この版では raise_alarm に変わる(帳簿の hurt_drink 2 件はどちらも敵なしで影響しない)。
 4. 新しい枝 hurt_retreat_allies: hp<=30・薬なし・敵なし・味方 1 以上 → retreat。
    14/14、会話 3 本(r1s3 3、r2s1 6、r2s3 5)。決め手 potion=false, allies>=1 / >=2, hp<=15 / <=30。
    理由「門(持ち場)を味方に任せて退く」。
    味方 0 は hold 5・retreat 4 で割れる(訊き直した hp=28 の状態も 2 対 2)ので hurt_no_threat で棄権。
    hp 31〜32 の敵なしは retreat 1(r2s1)・hold 2(r2s2 r2s3)で割れ、hp_ambiguous のまま。
 5. 番人 no_arrows_cover(離れた敵・矢 0・遮蔽あり)を時刻で分けた。hold 18 件はすべて昼、take_cover 8 件は
    夜 7・昼 1。
      昼 → no_arrows_hold に入れた(「離れた敵・矢 0 → 持ち場」と同じ規則)。昼・遮蔽あり 19 件で hold 18、
        会話 6 本。hold の決め手は arrows=0, distance>=2 で、遮蔽を挙げた会話は無い。
        外れは r1s2 の 1 件(hp=42、決め手 hp<=42, potion=false、gap)。
      夜 → 新しい枝 no_arrows_night_cover → take_cover。7/7、会話 4 本(r1s1 1、r2s1 2、r2s2 2、r2s3 2)。
        決め手 time=night, arrows=0, cover=true。根拠 L6。
 6. 番人 troll_alarm_raised(警報済みのトロル)を味方の数と間合いで分けた。L3 は「一人で相手にするには」
    強すぎると言うので、味方がいるかが効く。決め手にも allies=0 / allies>=1,2 が 15 件中 10 件挙がる。
      troll_shoot_allies(味方あり・離れて・矢あり → shoot): 5/5、会話 4 本(r1s1 r1s3 r2s2×2 r2s3)。
        決め手 distance>=2〜5, arrows>=1, allies>=1 / >=2。根拠 L2+L3(3 件は gap なし)。
      troll_melee_allies(味方あり・隣接 → melee_attack): 2/2、会話 2 本(r2s1 r2s2)。
        どちらも根拠 L2+L3 で gap なし → 規律 (c)。決め手 distance<=1, allies>=1 / >=2。
      troll_alone_cover(味方 0・離れて・夜・遮蔽あり → take_cover): 4/4、会話 3 本(r1s2 2、r2s1、r2s3)。
        決め手 enemy=troll, allies=0, cover=true / time=night。理由「一人で夜、遮蔽で援軍を待つ」。
      棄権のまま: troll_no_arrows(味方あり・離れて・矢 0。hold 1 / retreat 1)、
        troll_alone_adjacent(味方 0・隣接。retreat 2 だが 2 件とも gap で (c) に届かない)、
        troll_alone_open(味方 0・離れて・昼か遮蔽なし。例 0)。
 7. 番人 mage_alarm_unclear(警報未の魔術師)から三つ切り出した。
      mage_melee_first(隣接 → melee_attack): 4/4、会話 3 本(r1s3 r2s1×2 r2s3)。
        決め手 enemy=mage, distance=1 / <=1。理由「警報より先に斬る」。
      mage_no_arrows_alarm(離れて・矢 0 → raise_alarm): 4/4、会話 2 本(r1s1 1、r2s2 3)。
        決め手 alarm=false, enemy=mage, arrows=0。2 件は根拠 L4+L5 で gap なし。
      mage_night_alarm(離れて・矢あり・夜 → raise_alarm): 3/3、会話 2 本(r2s2 1、r2s3 2)。
        決め手 enemy=mage, alarm=false, time=night(r2s3)、enemy_count>=3(r2s2)。根拠 L4+L5+L6。
        夜の警報未の魔術師は矢 0 の 3 件と hp=28 の 1 件(r1s1)も警報で、夜の反例は無い。
      棄権のまま: 昼・離れて・矢あり(raise 4 / shoot 5、会話 4 本に散る)。
 8. 番人 orc_alarm_unclear から orc_pack_alone_alarm を切り出した:
    警報未のオーク 2 体・味方 0・夜・隣接 → raise_alarm。4/4、会話 4 本(r1s2 r2s1 r2s2 r2s3、
    訊き直した同じ状態)。決め手はどれも alarm=false, allies=0, time=night。
    離れていると r2s3 が弱ったオーク(決め手 enemy_hp<=20 / <=30, distance>=3)を射て割れるので、
    線は L2 の隣接の境に置いた。残り 8 件(raise 3 / shoot 4 / melee 1)は棄権のまま。

 そのままにした所
    group_alarm_unclear(警報未のゴブリン 3 体・味方あり): melee 1 / shoot 2 / raise 1 / hold 2。
      矢 0 の hold 2 はどちらも gap で (c) に届かない。
    mage_no_arrows(警報済み・離れた魔術師・矢 0): melee 2(d2)/ take_cover 2(遮蔽あり)、全件 gap。
    shoot_far の外れ 1 件(r2s1、夜・ゴブリン 5 体・味方 0・遮蔽あり で take_cover、gap)。
      26/27 で、別の答えを多数にした会話は 1 本なので枝は変えない。

b2 で数え直した帳簿(答える枝、件数・一致・会話)
    no_threat_hold        45  45/45  6 本      L7      敵なし・hp>=33 → hold_position
    no_arrows_hold        29  28/29  6 本      gap     離れた敵・矢 0(遮蔽なし、または昼)→ hold_position
    shoot_far             27  26/27  5 本      L2      離れたゴブリン/オーク・矢あり → shoot
    horde_alarm           17  17/17  6 本      L5      警報未・敵 4 以上 → raise_alarm
    hurt_retreat_allies   14  14/14  3 本      L1+L7   hp<=30・薬なし・敵なし・味方あり → retreat
    melee_adjacent        12  12/12  5 本      L2      隣接のゴブリン/オーク → melee_attack
    hurt_drink             9   9/9   5 本以上  L1      hp<=30・薬あり → drink_potion
    hurt_retreat           9   8/9   5 本以上  L1      hp<=30・薬なし・敵あり → retreat
    no_arrows_night_cover  7   7/7   4 本      L6      離れた敵・矢 0・夜・遮蔽あり → take_cover
    a1_shoot_far           6   3/6   4 本      A1      hp 31〜32・薬なし・d>=9・矢あり → shoot(帳簿は A1 前)
    hurt_far_alarm         5   5/5   4 本      L5+L1   hp<=30・警報未の深刻な脅威が離れて → raise_alarm
    troll_alarm            5   5/5   3 本      L5+L3   トロル・警報未 → raise_alarm
    troll_shoot_allies     5   5/5   4 本      L2+L3   警報済みトロル・味方あり・離れて・矢あり → shoot
    mage_melee_first       4   4/4   3 本      L2+L4   警報未・隣接の魔術師 → melee_attack
    mage_no_arrows_alarm   4   4/4   2 本      L4+L5   警報未・離れた魔術師・矢 0 → raise_alarm
    orc_pack_alone_alarm   4   4/4   4 本      L5+L6   警報未・オーク 2 体・味方 0・夜・隣接 → raise_alarm
    troll_alone_cover      4   4/4   3 本      L3+L6   警報済みトロル・味方 0・離れて・夜・遮蔽 → take_cover
    outnumbered_alarm      3   3/3   2 本      L5      警報未・敵 3・味方 0 → raise_alarm
    mage_night_alarm       3   3/3   2 本      L5+L6   警報未・離れた魔術師・矢あり・夜 → raise_alarm
    mage_shoot             3   3/3   2 本      L2+L4   離れた魔術師(警報済み)・矢あり → shoot
    troll_melee_allies     2   2/2   2 本      L2+L3   警報済みトロル・味方あり・隣接 → melee_attack
    mage_melee             0                   L2+L4   隣接の魔術師(警報済み)→ melee_attack

棄権の番人(割れている所、証拠が足りない所。輪が審判に訊き直す所)
    mage_alarm_unclear     9  警報未・昼・離れた魔術師・矢あり(raise 4 / shoot 5)
    hurt_no_threat         9  hp<=30・薬なし・敵なし・味方 0(hold 5 / retreat 4)
    orc_alarm_unclear      8  警報未のオーク 2〜3 体(隣接・味方 0・夜を除く。raise 3 / shoot 4 / melee 1)
    hp_ambiguous           7  30<hp<33(A1 の範囲を除く。drink 2 / hold 2 / raise 1 / retreat 1 / shoot 1)
    group_alarm_unclear    6  警報未のゴブリン 3 体・味方あり
    mage_no_arrows         4  警報済み・離れた魔術師・矢 0(melee 2 / take_cover 2、全件 gap)
    troll_no_arrows        2  警報済みトロル・味方あり・離れて・矢 0(hold 1 / retreat 1)
    troll_alone_adjacent   2  警報済みトロル・味方 0・隣接(retreat 2、gap)
    troll_alone_open       0  警報済みトロル・味方 0・離れて・昼か遮蔽なし
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
_HURT_MAX = 30      # これ以下はひどい(決め手 hp<=30 が最多、31〜32 は会話で割れる)
_FINE_MIN = 33      # これ以上はひどくない(b1 のまま)

# 追補 A1
_A1_HP_MIN = 31     # hp が 31 以上あれば
_A1_DIST_MIN = 9    # 敵が 9 マス以上離れ

# 警報未の群れ
_HORDE_MIN = 4          # 敵がこれ以上なら警報(敵 3 は割れる、4・5 は 17/17)
_OUTNUMBERED_MIN = 3    # 味方 0 で敵がこれ以上なら警報


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


def _serious(enemy, count, allies):
    """警報を要する深刻な脅威(トロル、魔術師、大きな群れ、味方 0 で 3 体以上)。"""
    if enemy in ("troll", "mage"):
        return True
    if count >= _HORDE_MIN:
        return True
    return count >= _OUTNUMBERED_MIN and allies == 0


def _hurt(s):
    """hp<=30: ひどく傷ついている(L1)。"""
    enemy = s["enemy"]

    # L5: 警報未の深刻な脅威がまだ離れていれば、薬や退却より先に警報
    if (enemy != "none" and not s["alarm"] and s["distance"] >= 2
            and _serious(enemy, s["enemy_count"], s["allies"])):
        return ("raise_alarm", "hurt_far_alarm")

    # L1
    if s["potion"]:
        return ("drink_potion", "hurt_drink")
    if enemy == "none":
        if s["allies"] >= 1:
            return ("retreat", "hurt_retreat_allies")
        return (None, "hurt_no_threat")
    return ("retreat", "hurt_retreat")


def _engaged(s):
    """hp>=33(ひどくない)ときの規則。"""
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
            # 一人ではない → L2 どおり
            if dist == 1:
                return ("melee_attack", "troll_melee_allies")
            if arrows >= 1:
                return ("shoot", "troll_shoot_allies")
            return (None, "troll_no_arrows")
        # 一人でトロル
        if dist == 1:
            return (None, "troll_alone_adjacent")
        if night and cover:
            return ("take_cover", "troll_alone_cover")
        return (None, "troll_alone_open")

    # --- L5: 警報未のとき、深刻な脅威かどうか ---
    if not alarm:
        if count >= _HORDE_MIN:
            return ("raise_alarm", "horde_alarm")
        if count >= _OUTNUMBERED_MIN and allies == 0:
            return ("raise_alarm", "outnumbered_alarm")
        if enemy == "mage":
            if dist == 1:
                return ("melee_attack", "mage_melee_first")
            if arrows <= 0:
                return ("raise_alarm", "mage_no_arrows_alarm")
            if night:
                return ("raise_alarm", "mage_night_alarm")
            return (None, "mage_alarm_unclear")
        if enemy == "orc" and count >= 2:
            if dist == 1 and allies == 0 and night:
                return ("raise_alarm", "orc_pack_alone_alarm")
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
            return ("take_cover", "no_arrows_night_cover")
        return ("hold_position", "no_arrows_hold")
    if enemy == "mage":
        return ("shoot", "mage_shoot")
    return ("shoot", "shoot_far")


def _a1_applies(s):
    """追補 A1: hp>=31・(回復薬なし)・敵が 9 マス以上・矢あり。"""
    return (
        s["hp"] >= _A1_HP_MIN
        and not s["potion"]
        and s["enemy"] != "none"
        and s["distance"] >= _A1_DIST_MIN
        and s["arrows"] >= 1
    )


def decide(s):
    bad = _guard(s)
    if bad is not None:
        return (None, bad)

    hp = s["hp"]

    if hp <= _HURT_MAX:
        return _hurt(s)

    if hp < _FINE_MIN:
        # 30<hp<33: 会話で割れる帯。A1 の範囲で、ひどくない時と同じく射る状態だけ答える
        if _a1_applies(s):
            act, _ = _engaged(s)
            if act == "shoot":
                return ("shoot", "a1_shoot_far")
        return (None, "hp_ambiguous")

    return _engaged(s)
