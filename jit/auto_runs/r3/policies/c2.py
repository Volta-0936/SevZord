"""走り r3 の方針、第 2 版(c2)。前の版は c1。

帳簿: 審判のラベル 252 件、会話 6 本(round1_s1/s2/s3、round2_s1/s2/s3。以下 r1s1 … r2s3)。
c1 の答えた枝は、どれも一致 80% 以上で会話の多数も方針どおりだった(shoot_far 26/27、
ほかは全件一致)ので、条件を変えずに残す。c1 が答えた状態の行き先は、この版でも変わらない。
この版で変えたのは、c1 が棄権していた状態の一部と、番人の分け方。

「ひどく傷ついている」の帯(hp の線)
    hp<=20   ひどい(c1 のまま、_HURT_MAX)
    21〜30   手負い(wounded、_WOUNDED_MAX)。この版で新しく答える帯
    31〜32   割れる帯(hp_ambiguous、薬なしのとき)
    hp>=33   ひどくない(c1 のまま、_FINE_MIN)
  hp_ambiguous の 37 件の決め手で最も多いのは hp<=30(10 件)。31〜32 では同じ状態でも
  会話が割れる(訊き直した hp31 のゴブリン 3 体: retreat 2 / shoot 1。r1s1 は hp31 を
  「手負いだが」と言って射る)。37 件を薬の有無で分けると、薬ありは 10 件中 drink 9 で
  揃い、割れているのは薬なしの側(retreat 17・hold 6・shoot 3・raise 1)。

この版で変えたこと
 1. hurt_no_threat_retreat(新しい枝。番人 hurt_no_threat を答えにした):
    hp<=20・薬なし・敵なし → retreat。
    12 件・会話 4 本(r1s3 3、r2s1 2、r2s2 1、r2s3 6)・一致 12/12。根拠 L1+L7(gap)。
    決め手 potion=false 12、allies>=1 7、hp<=20 6。味方 0 の 3 件(r2s2 1、r2s3 2)も
    retreat なので、味方の数は条件にしない。L1 をそのまま読んだ規則でもある(規律 (a)(b))。

 2. hurt_troll_alarm(新しい枝): hp<=32・警報未のトロル・distance>=3 → raise_alarm。
    3 件・会話 3 本(r1s3、r2s2、r2s3)・一致 3/3(hp 10〜17)。決め手 alarm=false、
    enemy=troll、distance>=12 / >=10 / >=5。薬ありの 1 件も「薬より先に警報」。
    隣接のトロルでは生き延びが先(hp14 薬あり drink 1 件、hp23 薬なし retreat 3 本)
    なので、線は隣接の 1 と警報の最も近い 5 の間の 3(_ALARM_FIRST_DIST)。
    決め手に hp は出ないので、hp 21〜32 の遠いトロル(例なし)もこの枝に入れた。
    hp<=20 の 3/3 と hp>=33 の troll_alarm 5/5 に挟まれ、どちらも raise_alarm。
    番人 hurt_vs_alarm は hp<=20・警報未のトロル・distance<=2・薬ありだけに縮めた
    (drink 1 件、r2s3、根拠 gap)。

 3. hp<=20・警報未のトロルが distance<=2・薬なし を hurt_retreat へ通した(c1 は
    hurt_vs_alarm で棄権、例 0 件)。hp23 の隣接トロルの同じ状態を会話 3 本に訊き、
    3 本とも retreat(「警報より退避を優先」)。決め手 hp<=30、potion=false、enemy=troll、
    distance<=1 を hp<=20 の状態も満たす。L1 をそのまま読んだ答えでもある。

 4. wounded_drink(新しい枝): 21<=hp<=32・薬あり → drink_potion。
    9 件・会話 5 本(r1s2 2、r1s3 1、r2s1 3、r2s2 1、r2s3 2)・一致 9/9。根拠 L1(一部 gap)。
    決め手 potion=true 9、hp<=21 / <=26 / <=29 / <=30 / <=31 / <=33。飲んだ最も高い例は
    hp31(r1s2、r2s1)。hp32 の薬ありは例がなく、hp>=33 で飲む例はないので上の線は
    _FINE_MIN のまま。
    外したもの(番人 wounded_vs_alarm): 警報未の魔術師(r1s1 hp28 は raise_alarm、
    決め手 enemy=mage, alarm=false, distance>=10)、警報未のトロル、警報未の敵 4 以上。
    L5 と競る所で、hp<=20 の遠いトロルは薬より警報が先だった。
    敵 3・味方 0 の警報未は薬ありで drink(r2s3 hp27)なので枝に入れたまま。

 5. wounded_retreat(新しい枝): 21<=hp<=30・薬なし・敵あり → retreat。
    7 件・会話 5 本・一致 6/7(86%)。retreat は r1s1 2、r1s2 1、r2s1 2、r2s2 1。
    決め手 hp<=30 / <=22 / <=23、potion=false、enemy=troll、distance<=1、allies=0。
    隣接の警報未トロル(hp23、同じ状態に r1s1・r2s1・r2s2 の 3 本とも retreat)を含む。
    外れは r2s3 の shoot 1(遠くの瀕死のゴブリン一体、決め手 enemy_hp<=10、
    enemy_count<=1)。別の答えを多数にした会話は 1 本。
    外したもの(番人 wounded_vs_alarm): 警報未の深刻な群れ(敵 4 以上、または敵 3・
    味方 0)が distance>=3。手負い帯の例は 0 件だが、hp31 の r2s3 は敵 3・味方 0・
    distance 7 で「敵が遠いうちに警報」を選んでおり、遠い群れでは L5 が L1 に勝つ。
    警報未の魔術師も同じ番人(手負い帯の薬なしの例は 0 件)。

 6. wounded_handover(新しい枝): 21<=hp<=30・薬なし・敵なし・味方 1 以上 → retreat。
    5 件・会話 2 本(r2s1 4、r2s3 1)・一致 5/5。決め手 hp<=30 / <=33、potion=false、
    allies>=1(「門は味方に任せて退く」)。hp32 の味方ありは hold_position 2 件(r2s1、
    r2s2、決め手 hp>=32)、hp31 は retreat 1 件(r2s3)なので、31〜32 は入れない。
    番人 wounded_alone(味方 0): hold 4(r1s1、r1s3、r2s1、r2s3)/ retreat 1(r2s2)。
    訊き直した hp28・門・夜・単独の状態も hold 2 / retreat 1。根拠は 5 件とも gap、
    一致はちょうど 80%、決め手は「門を空けない」(post=gate、allies=0)と「今のうちに
    退く」に割れるので棄権のまま残す。

 7. hp_ambiguous は hp 31〜32・薬なしだけに縮めた(10 件・会話 5 本: retreat 5、hold 2、
    shoot 2、raise 1)。

 8. 警報済みのトロル(番人 troll_alarm_raised、hold 1 / shoot 5 / take_cover 5 /
    retreat 2 / melee 2)を味方の数で分けた。L3 が言うのは「一人で」相手にするなということ。
    troll_shoot_allied(新しい枝): 味方 1 以上・distance>=2・矢あり → shoot。
        5 件・会話 4 本(r1s1、r1s3、r2s2 2、r2s3)・一致 5/5。
        決め手 allies>=1 / >=2、distance>=2 / >=4 / >=7 / >=8、arrows>=1 / >=2 / >=10 / >=14。
    troll_melee_allied(新しい枝): 味方 1 以上・隣接 → melee_attack。
        2 件(r2s1、r2s2)・一致 2/2。根拠は 2 件とも L2+L3 で gap なし(規律 (c))。
        決め手 distance<=1、allies>=1 / >=2。
    troll_alone_cover(新しい枝): 味方 0・distance>=2・遮蔽あり → take_cover。
        4 件・会話 3 本(r1s2 2、r2s1、r2s3)・一致 4/4。決め手は 4 件とも
        enemy=troll, allies=0, cover=true。4 件とも夜で根拠に L6 が付くが、決め手に
        time は出ないので条件にしない。線は隣接(retreat)と distance 3 の間で、L2 の
        「離れて」と同じ distance>=2。
    番人 troll_no_arrows: 味方あり・離れ・矢 0(hold 1 / take_cover 1)。
    番人 troll_alarm_raised(残り): 味方 0 の隣接は retreat 2(r2s1、r2s3、どちらも夜)
        だが根拠が gap で例 2 件、規律に届かない。味方 0・遮蔽なしの離れは例なし。

 9. no_arrows_cover を昼と夜で分けた。
    no_arrows_cover_day(新しい枝): 離れた敵(魔術師以外)・矢 0・遮蔽あり・昼 → hold_position。
        16 件・会話 6 本・一致 15/16(94%)。決め手 arrows=0、distance>=2、time=day(r2s3 3 件)。
        外れは r1s2 の take_cover 1(hp42、決め手 hp<=42, potion=false)。hp37 で hold の
        例(r2s1)があるので hp では分けない。
    番人 no_arrows_cover(夜): take_cover 5(r1s1、r2s2 2、r2s3 2)/ hold 2(r2s1 2)、71%。
        take_cover の決め手 time=night、cover=true(L6)。

 10. 警報未の魔術師(番人 mage_alarm_unclear、raise 13 / shoot 3 / melee 4)を分けた。
    mage_melee_first(新しい枝): 隣接 → melee_attack。
        4 件・会話 3 本(r1s3、r2s1 2、r2s3)・一致 4/4。決め手 enemy=mage、
        distance<=1 / =1、enemy_hp<=30(2)、「警報より先に仕留める」(L4)。
    mage_alarm(新しい枝): 離れ → raise_alarm。
        14 件・会話 6 本・一致 13/14(93%)。決め手 alarm=false 13、enemy=mage 13、
        arrows=0 4、arrows<=1 / <=2 3、allies=0 2、enemy_count>=2 / >=3 2。
        外れは r1s2 の shoot 1(単独、矢 11、決め手 enemy_count=1, arrows>=11)。会話 1 本。
    番人 weak_mage_unclear: 離れ・敵の体力 35 以下・矢あり。shoot 2(r1s2 ehp10、
        r2s2 ehp30)、決め手 enemy_hp<=10 / <=30、arrows>=6 / >=20(「瀕死の魔術師を一射で」)。
        L4 で射るか L5 で鳴らすかの境。例 2 件・根拠 gap で規律に届かない。
        線は shoot の決め手 30 と、raise の最も低い敵の体力 40 の間の 35(_WEAK_MAGE_MAX)。
        矢 0 は射てないので mage_alarm 側(矢 0 の 4 件はすべて raise、決め手 arrows=0)。

 11. 警報未のゴブリン 3 体・味方あり(番人 group_alarm_unclear)を外し、L2 へ通した。
    6 件・会話 4 本・L2 どおり 5/6(83%): 隣接 melee 1(r1s3)、離れて矢あり shoot 2
    (r1s3、r2s2)、離れて矢 0 hold 2(r2s2 遮蔽なし、r2s3 遮蔽あり・昼)。
    決め手 distance、arrows、enemy=goblin。外れは r2s1 の raise 1(夜、決め手
    alarm=false、time=night、enemy_count>=3)。会話 1 本。味方 0 なら outnumbered_alarm のまま。

変えなかった番人
    orc_alarm_unclear 11: 警報未のオーク 2〜3 体(敵 3 なら味方あり)。L2 どおり 6
        (melee 2、shoot 4)/ raise 5。r2s3 は 4 件すべて L2、ほかの会話は夜に警報
        (決め手 time=night、allies=0)。訊き直した隣接・夜・単独の状態は raise 2 / melee 1。
        会話どうしの割れなので棄権。
    mage_no_arrows 4: 警報済み・離れた魔術師・矢 0。遮蔽なし melee 2(r1s1、r2s1)/
        遮蔽あり take_cover 2(r2s1、r2s2)。どちらも 2 件で根拠 gap。

c2 で数え直した帳簿(答える枝、件数・一致・会話)
    no_threat_hold          45  45/45  6 本      L7      敵なし・hp>=33 → hold_position
    shoot_far               30  28/30  5 本以上  L2      離れたゴブリン/オーク・矢あり → shoot
    no_arrows_cover_day     17  16/17  6 本      gap     離れ・矢 0・遮蔽あり・昼 → hold_position
    horde_alarm             15  15/15  6 本      L5      警報未・敵 4 以上 → raise_alarm
    mage_alarm              14  13/14  6 本      L5+L4   警報未・離れた魔術師 → raise_alarm
    melee_adjacent          13  13/13  5 本以上  L2      隣接のゴブリン/オーク → melee_attack
    hurt_no_threat_retreat  12  12/12  4 本      L1      hp<=20・薬なし・敵なし → retreat
    wounded_drink            9   9/9   5 本      L1      hp 21〜32・薬あり → drink_potion
    no_arrows_hold           8   8/8   5 本以上  gap     離れ・矢 0・遮蔽なし → hold_position
    wounded_retreat          7   6/7   5 本      L1      hp 21〜30・薬なし・敵あり → retreat
    troll_alarm              5   5/5   3 本      L5+L3   トロル・警報未 → raise_alarm
    troll_shoot_allied       5   5/5   4 本      L2+L3   警報済みトロル・味方あり・離れ・矢あり → shoot
    wounded_handover         5   5/5   2 本      L1      hp 21〜30・薬なし・敵なし・味方あり → retreat
    mage_melee_first         4   4/4   3 本      L4+L2   警報未・隣接の魔術師 → melee_attack
    troll_alone_cover        4   4/4   3 本      L3+L6   警報済みトロル・単独・離れ・遮蔽 → take_cover
    outnumbered_alarm        3   3/3   2 本      L5      警報未・敵 3・味方 0 → raise_alarm
    mage_shoot               3   3/3   2 本      L2+L4   離れた魔術師(警報済み)・矢あり → shoot
    hurt_troll_alarm         3   3/3   3 本      L5+L3   hp<=32・警報未トロル・distance>=3 → raise_alarm
    hurt_drink               2   2/2   2 本      L1      hp<=20・薬あり → drink_potion
    troll_melee_allied       2   2/2   2 本      L2+L3   警報済みトロル・味方あり・隣接 → melee_attack
    hurt_retreat             1   1/1   1 本      L1      hp<=20・薬なし・敵あり → retreat
    mage_melee               0                   L2+L4   隣接の魔術師(警報済み) → melee_attack
    答える 207 件、一致 202。

棄権の番人(割れている所、証拠が足りない所。輪が審判に訊き直す所)
    orc_alarm_unclear    11  警報未のオーク 2〜3 体(raise 5 / shoot 4 / melee 2)
    hp_ambiguous         10  hp 31〜32・薬なし(retreat 5 / hold 2 / shoot 2 / raise 1)
    no_arrows_cover       7  離れ・矢 0・遮蔽あり・夜(take_cover 5 / hold 2)
    wounded_alone         5  hp 21〜30・薬なし・敵なし・味方 0(hold 4 / retreat 1、全件 gap)
    mage_no_arrows        4  警報済み・離れた魔術師・矢 0(melee 2 / take_cover 2)
    troll_alarm_raised    2  警報済みトロル・単独・隣接または遮蔽なし(retreat 2、gap)
    troll_no_arrows       2  警報済みトロル・味方あり・離れ・矢 0(hold 1 / take_cover 1)
    weak_mage_unclear     2  警報未・離れた弱い魔術師・矢あり(shoot 2、gap)
    hurt_vs_alarm         1  hp<=20・警報未トロル・distance<=2・薬あり(drink 1、gap)
    wounded_vs_alarm      1  hp 21〜32 で L1 と L5 が競る所(警報未の魔術師 raise 1 ほか)
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

# 「ひどく傷ついている」の帯
_HURT_MAX = 20      # これ以下は明らかにひどい(b0 のまま)
_WOUNDED_MAX = 30   # 21〜30 は手負い。決め手 hp<=30 が最も多い。31〜32 は会話で割れる
_FINE_MIN = 33      # これ以上はひどくない(飲む最高の 31 と、次の例 35 の間)

# 警報未の群れ
_HORDE_MIN = 4          # 敵がこれ以上なら警報(敵 4・5 は 15/15)
_OUTNUMBERED_MIN = 3    # 味方 0 で敵がこれ以上なら警報(3/3)

# 傷と警報が競るとき、これ以上離れていれば警報が先(隣接 1 は退く・飲む、5 以上は警報)
_ALARM_FIRST_DIST = 3

# 警報未の離れた魔術師を「弱っている」と見る敵の体力の上限(shoot の 30 と raise の 40 の間)
_WEAK_MAGE_MAX = 35


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
    enemy_hp = s["enemy_hp"]
    allies = s["allies"]
    potion = s["potion"]
    arrows = s["arrows"]
    cover = s["cover"]
    alarm = s["alarm"]
    time = s["time"]

    fine = hp >= _FINE_MIN

    # --- L1 と L5 が競る所: 遠いトロルは、傷があっても警報が先 ---
    if (not fine and enemy == "troll" and not alarm
            and dist >= _ALARM_FIRST_DIST):
        return ("raise_alarm", "hurt_troll_alarm")

    # --- L1: ひどく傷ついている(hp<=20) ---
    if hp <= _HURT_MAX:
        if enemy == "troll" and not alarm:
            # 近いトロル(distance<=2)。隣接では生き延びが先
            if potion:
                return (None, "hurt_vs_alarm")
            return ("retreat", "hurt_retreat")
        if potion:
            return ("drink_potion", "hurt_drink")
        if enemy == "none":
            return ("retreat", "hurt_no_threat_retreat")
        return ("retreat", "hurt_retreat")

    # --- 手負い(21<=hp<=32) ---
    if not fine:
        if not alarm and enemy == "mage":
            return (None, "wounded_vs_alarm")
        if potion:
            if not alarm and (enemy == "troll" or count >= _HORDE_MIN):
                return (None, "wounded_vs_alarm")
            return ("drink_potion", "wounded_drink")
        if hp > _WOUNDED_MAX:
            return (None, "hp_ambiguous")
        # 21<=hp<=30、薬なし
        if enemy == "none":
            if allies >= 1:
                return ("retreat", "wounded_handover")
            return (None, "wounded_alone")
        if (not alarm and dist >= _ALARM_FIRST_DIST
                and (count >= _HORDE_MIN
                     or (count >= _OUTNUMBERED_MIN and allies == 0))):
            return (None, "wounded_vs_alarm")
        return ("retreat", "wounded_retreat")

    # ここから先は hp>=33(ひどくない)

    # --- L7: 脅威が無い ---
    if enemy == "none":
        return ("hold_position", "no_threat_hold")

    # --- L3 + L5: トロル ---
    if enemy == "troll":
        if not alarm:
            return ("raise_alarm", "troll_alarm")
        # 警報済み。L3 は「一人で」相手にするなと言う
        if allies >= 1:
            if dist == 1:
                return ("melee_attack", "troll_melee_allied")
            if arrows >= 1:
                return ("shoot", "troll_shoot_allied")
            return (None, "troll_no_arrows")
        if dist >= 2 and cover:
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
                return ("melee_attack", "mage_melee_first")
            if arrows >= 1 and enemy_hp <= _WEAK_MAGE_MAX:
                return (None, "weak_mage_unclear")
            return ("raise_alarm", "mage_alarm")
        if enemy == "orc" and count >= 2:
            return (None, "orc_alarm_unclear")
        # 単独のオーク、ゴブリン 1〜3 体(3 体なら味方あり)は深刻な脅威ではない → L2 へ

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
            if time == "day":
                return ("hold_position", "no_arrows_cover_day")
            return (None, "no_arrows_cover")
        return ("hold_position", "no_arrows_hold")
    if enemy == "mage":
        return ("shoot", "mage_shoot")
    return ("shoot", "shoot_far")
