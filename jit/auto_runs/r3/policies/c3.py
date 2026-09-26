"""走り r3 の方針、第 3 版(c3)。前の版は c2。

帳簿: 審判のラベル 321 件、会話 8 本(round1_s1/s2/s3、round2_s1/s2/s3、round3_s1/s2。
以下 r1s1 … r3s2)。範囲の番人は c2 のまま。

c2 の枝で門に落ちるのは hurt_retreat だけだった(3 件で 2/3、67%。例 3 件以上で一致 80% 未満)。
外れは r3s1 の raise_alarm 1 件(hp5、ゴブリン 4 体、distance 10、味方 0、警報未、
決め手 alarm=false, enemy_count>=4, distance>=10、「瀕死でも敵は遠い、退く前に警報」)。
ほかの答える枝は、一致 80% 以上で、別の答えを多数にした会話も 1 本以下なので、条件を変えない。
この版で変えたのは、hurt_retreat から遠い群れを外したことと、c2 が棄権していた所の一部。

この版で変えたこと
 1. hurt_horde_alarm(新しい枝、hurt_retreat の修理を兼ねる):
    hp<=32・薬なし・警報未・distance>=3・深刻な群れ(敵 4 以上、または敵 3・味方 0)
    → raise_alarm。
    3 件・会話 3 本(r3s1 hp5、r3s2 hp25、r2s3 hp31)・一致 3/3。根拠 L5+L1(gap)。
    決め手 alarm=false 3、enemy_count>=4 2、distance>=10 / >=8 / >=5、allies=0。
    「深手だが小鬼四体、敵が遠いうちに警報」。c2 が wounded_vs_alarm と hp_ambiguous で
    棄権していた同じ形(遠い群れでは L5 が L1 に勝つ)を、hp<=20 にも通した。
    線 distance>=3 は c2 の _ALARM_FIRST_DIST(隣接 1 と警報の最も近い 5 の間)のまま。
    薬ありは入れない(hp31・敵 4・薬ありは drink 1 件、r3s1)。
    これで hurt_retreat は 2/2(会話 2 本)に戻る。

 2. wounded_mage_alarm(新しい枝): 21<=hp<=32・警報未の魔術師・薬なし・distance>=3
    → raise_alarm。
    3 件・会話 2 本(r3s1 hp29 敵 4、r3s2 hp21 敵 3、r3s2 hp30 矢 0)・一致 3/3。
    根拠 L5+L1(+L4)(gap)。決め手 alarm=false 3、enemy=mage 3、enemy_count>=4、hp<=21、
    arrows=0。「深手でも魔術師込み三体、まず警報を優先」。
    薬ありの遠い魔術師は割れる(訊き直した hp28・distance 10 の状態で raise 2(r1s1、r3s2)
    / drink 1(r3s1))ので番人 wounded_vs_alarm に残す。隣接(hp30、melee 1、gap)も残す。

 3. wounded_alone_hold(番人 wounded_alone を答えにした):
    21<=hp<=30・薬なし・敵なし・味方 0 → hold_position。
    8 件・会話 6 本・一致 7/8(88%)。hold は r1s1、r1s3、r2s1、r2s3、r3s1 3。根拠 L7+L0/L1(gap)。
    決め手 enemy=none 7、allies=0 7、post=gate 1(「脅威が無く代わりもいないので持ち場に
    留まる」「門を空にできない」)。外れは r2s2 の retreat 1(訊き直した hp28・門・夜・単独の
    状態の 1 票、決め手 hp<=28, potion=false)。別の答えを多数にした会話は 1 本。
    c2 では 5 件で一致ちょうど 80% だったので残したが、r3s1 の 3 件が加わり線の上に出た。
    持ち場は wall の例(r3s1 hp25)も hold なので、post は条件にしない。
    味方ありの wounded_handover(retreat)と対になる:「門を任せる相手がいるか」。

 4. 警報済みのトロル・単独(番人 troll_alarm_raised、retreat 6 / hold 1)を分けた。
    troll_alone_retreat(新しい枝): 味方 0・(隣接、または離れて遮蔽なし)・敵の体力 16 以上
        → retreat。6 件・会話 4 本(r2s1、r2s3、r3s1 2、r3s2 2)・一致 6/6。根拠 L3+L2(gap)。
        決め手 enemy=troll 6、allies=0 6、time=night 2、distance<=1、enemy_count>=2 / >=4、
        alarm=true(「単独でトロルは無理、警報済みなので退き合流」)。L3 と L0 をそのまま
        読んだ答えでもある。隣接は遮蔽の有無に関わらず 3/3(r2s1・r2s3 は遮蔽あり)。
    番人 weak_troll_alone: 同じ所で敵の体力 15 以下。hold 1(r3s2 hp83、ehp10、決め手
        enemy_hp<=10、「瀕死のトロルなら門で迎え撃てる」)。退いた最も弱いトロルは ehp20
        (r2s1「弱っていても退く」、r3s1)なので、線は 10 と 20 の間の 15(_WEAK_TROLL_MAX)。
    troll_alone_cover(離れ・遮蔽あり)は c2 のまま先に取る。

 5. 警報済み・離れた魔術師・矢 0(番人 mage_no_arrows、melee 3 / take_cover 3 / hold 2)を分けた。
    mage_close_melee(新しい枝): distance 2・遮蔽なし → melee_attack。
        3 件・会話 3 本(r1s1、r2s1、r3s1)・一致 3/3。根拠 L4(+L2)(gap)。
        決め手 enemy=mage 3、arrows=0 3、distance<=2 2、hp>=90(「魔術師へ詰めて早く斬る」)。
    mage_no_arrows_cover(新しい枝): distance>=3・遮蔽あり → take_cover。
        3 件・会話 3 本(r2s1 d6、r2s2 d5、r3s2 d7)・一致 3/3。根拠 gap。
        決め手 arrows=0 3、cover=true 3、enemy=mage 2、distance>=6(「撃ち返せない魔術師には
        遮蔽に隠れる」)。
    線は melee の決め手 distance<=2 のすぐ外(_MAGE_CLOSE_MAX)。distance 2・遮蔽ありは、
    melee の決め手(distance<=2)と cover の決め手(cover=true)が両方かかり例もないので棄権。
    番人 mage_no_arrows(残り): 離れて遮蔽なし hold 2(r3s1 d12、r3s2 d8)、どちらも gap で
        例 2 件、規律に届かない。

 6. 警報未・離れた弱い魔術師・矢あり(番人 weak_mage_unclear、shoot 3 / raise 1)を分けた。
    weak_mage_shoot(新しい枝): 敵 2 以下・矢 4 以上 → shoot。
        3 件・会話 3 本(r1s2 ehp10 矢 6、r2s2 ehp30 矢 20、r3s1 ehp30 矢 19)・一致 3/3。
        根拠 L4+L5(+L2)(gap)。決め手 enemy=mage 3、enemy_hp<=10 / <=30、arrows>=6 / >=20 / >=19
        (「弱った魔術師を矢で早く仕留める」)。
    外れの raise 1(r3s2、敵 3・味方 1、決め手 alarm=false, enemy_count>=3, distance>=12、
        「魔術師込み三体、遠いうちに警報」)の決め手から、敵 3 は外して番人に残す。
    矢の線は、shoot の最も少ない決め手 arrows>=6 と、mage_alarm の raise の決め手
        arrows<=1 / <=2 の間の 4(_WEAK_MAGE_ARROWS_MIN)。矢 1〜3 は例がないので番人。

 7. 警報未のオーク 2〜3 体(番人 orc_alarm_unclear、raise 13 / shoot 6 / melee 4 / hold 1)を
    時刻と味方で分けた。c2 の見立て(r2s3 は L2、ほかの会話は夜に警報)が 8 本で確かめられた。
    orc_night_alarm(新しい枝): 夜・distance>=2 → raise_alarm。
        8 件・会話 5 本・一致 7/8(88%)。raise は r1s3 1、r2s2 1、r3s1 2、r3s2 3。
        根拠 L5+L6(+L2)(一部 gap)。決め手 time=night 7、alarm=false 7、enemy=orc 3、
        enemy_count>=3 2、allies<=1 2(「夜にオーク2体が迫り未発報なので警報」)。
        外れは r2s3 の shoot 1(d3、単独、決め手 distance>=2, arrows>=1)。別の答えを多数に
        した会話は r2s3 の 1 本。味方 2 の夜(r3s1、r3s2)も raise なので味方は条件にしない。
    orc_pair_day_shoot(新しい枝): 昼・敵 2・味方 1 以上・distance>=2・矢あり → shoot。
        4 件・会話 3 本(r2s1、r2s3、r3s2 2)・一致 4/4。根拠 L2(一部 gap)。
        決め手 distance>=2 / >=12、arrows>=1 2 / >=17 / >=20、allies>=3
        (「味方が多くオーク二体は深刻でない、遠くから射る」)。
        外したもの: 味方 0(raise 2(r2s1、r3s1、決め手 allies=0, enemy_count>=2)/ shoot 1
        (r2s3))、敵 3(r3s2 raise 1、決め手 enemy_count>=3「オーク三体は深刻」)、矢 0(hold 1)。
    番人 orc_alarm_unclear(残り 12): 夜の隣接 melee 3(r1s3、r2s3、r3s2)/ raise 2(r1s2、
        r2s1。訊き直した hp82・隣接・夜・単独は raise 2 / melee 1)、昼の単独・敵 3・矢 0・隣接。
        会話どうしの割れなので棄権。

 8. 夜・離れ・矢 0・遮蔽あり(番人 no_arrows_cover、take_cover 9 / hold 4 / raise 2 / drink 1)
    から一つ切り出した。
    night_alone_cover(新しい枝): 味方 0・警報済み → take_cover。
        4 件・会話 4 本(r1s1、r2s3、r3s1、r3s2)・一致 4/4。根拠 L6(一部 gap)。
        決め手 arrows=0 4、cover=true 4、time=night 3、allies=0 1(「夜に単独で射てず、遮蔽で
        援軍を待つ」)。うち 3 件は訊き直した同じ状態(hp44、d11、ゴブリン 3 体)で 3 本とも一致。
    味方 0 でも警報未は割れる(take_cover 2 / hold 1 / raise 1。raise は r3s1「夜に単独で
        射てず、用心して警報」で、警報未のときだけ L5 が競る)ので、警報済みに限った。
    番人 no_arrows_cover(残り 12): 味方ありの警報済みは hold 3(r2s1 2、r3s1)/ take_cover 3
        (r2s2 2、r3s2)で会話どうしに割れる。

変えなかった番人
    hp_ambiguous 9: hp 31〜32・薬なし。敵あり・夜は retreat 4(r2s1 2、r2s2、r2s3)/ shoot 1
        (r1s1)で一致ちょうど 80%、訊き直した状態(hp31・ゴブリン 3 体・夜)も retreat 2 /
        shoot 1。c2 が wounded_alone を 80% で残したのと同じく、線の上に出るまで棄権。
        敵なしは hold 2(hp32・昼)/ retreat 1(hp31・夜)。遠い群れ・警報未は 1. へ移した。
    wounded_vs_alarm 5: 手負い帯で L1 と L5 が競る残り(薬ありの遠い魔術師 raise 2 / drink 1、
        隣接の魔術師 melee 1、薬ありの敵 4 drink 1)。
    troll_no_arrows 2、hurt_vs_alarm 1: 例が少なく根拠 gap。

c3 で数え直した帳簿(答える枝、件数・一致・会話)
    no_threat_hold          50  50/50  8 本      L7      敵なし・hp>=33 → hold_position
    shoot_far               31  29/31  6 本      L2      離れたゴブリン/オーク・矢あり → shoot
    no_arrows_cover_day     21  20/21  8 本      gap     離れ・矢 0・遮蔽あり・昼 → hold_position
    horde_alarm             15  15/15  6 本      L5      警報未・敵 4 以上 → raise_alarm
    mage_alarm              15  14/15  7 本      L5+L4   警報未・離れた魔術師 → raise_alarm
    melee_adjacent          13  13/13  5 本      L2      隣接のゴブリン/オーク → melee_attack
    hurt_no_threat_retreat  13  13/13  5 本      L1      hp<=20・薬なし・敵なし → retreat
    wounded_drink           11  11/11  7 本      L1      hp 21〜32・薬あり → drink_potion
    wounded_retreat          9   8/9   7 本      L1      hp 21〜30・薬なし・敵あり → retreat
    orc_night_alarm          8   7/8   5 本      L5+L6   警報未のオーク 2〜3・夜・離れ → raise_alarm(新)
    wounded_alone_hold       8   7/8   6 本      L7      hp 21〜30・薬なし・敵なし・味方 0 → hold_position(新)
    no_arrows_hold           8   8/8   5 本      gap     離れ・矢 0・遮蔽なし → hold_position
    wounded_handover         6   6/6   3 本      L1      hp 21〜30・薬なし・敵なし・味方あり → retreat
    troll_alone_retreat      6   6/6   4 本      L3      警報済みトロル・単独・隣接か遮蔽なし → retreat(新)
    troll_alarm              5   5/5   3 本      L5+L3   トロル・警報未 → raise_alarm
    troll_shoot_allied       5   5/5   4 本      L2+L3   警報済みトロル・味方あり・離れ・矢あり → shoot
    hurt_drink               5   5/5   3 本      L1      hp<=20・薬あり → drink_potion
    mage_melee_first         5   5/5   4 本      L4+L2   警報未・隣接の魔術師 → melee_attack
    orc_pair_day_shoot       4   4/4   3 本      L2      警報未のオーク 2・昼・味方あり・離れ・矢あり → shoot(新)
    night_alone_cover        4   4/4   4 本      L6      夜・単独・警報済み・離れ・矢 0・遮蔽 → take_cover(新)
    outnumbered_alarm        4   4/4   3 本      L5      警報未・敵 3・味方 0 → raise_alarm
    troll_alone_cover        4   4/4   3 本      L3+L6   警報済みトロル・単独・離れ・遮蔽 → take_cover
    mage_shoot               4   4/4   3 本      L2+L4   離れた魔術師(警報済み)・矢あり → shoot
    hurt_troll_alarm         3   3/3   3 本      L5+L3   hp<=32・警報未トロル・distance>=3 → raise_alarm
    hurt_horde_alarm         3   3/3   3 本      L5+L1   hp<=32・薬なし・警報未の群れ・distance>=3 → raise_alarm(新)
    wounded_mage_alarm       3   3/3   2 本      L5+L1   hp 21〜32・薬なし・警報未の魔術師・distance>=3 → raise_alarm(新)
    mage_no_arrows_cover     3   3/3   3 本      gap     警報済み魔術師・矢 0・distance>=3・遮蔽 → take_cover(新)
    mage_close_melee         3   3/3   3 本      L4      警報済み魔術師・矢 0・distance 2・遮蔽なし → melee_attack(新)
    weak_mage_shoot          3   3/3   3 本      L4      警報未・弱い魔術師・敵 2 以下・矢 4 以上 → shoot(新)
    hurt_retreat             2   2/2   2 本      L1      hp<=20・薬なし・敵あり → retreat
    troll_melee_allied       2   2/2   2 本      L2+L3   警報済みトロル・味方あり・隣接 → melee_attack
    mage_melee               0                   L2+L4   隣接の魔術師(警報済み) → melee_attack
    答える 276 件、一致 269。

棄権の番人(割れている所、証拠が足りない所。輪が審判に訊き直す所)
    orc_alarm_unclear    12  警報未のオーク 2〜3 体の残り(raise 6 / melee 4 / shoot 1 / hold 1)
    no_arrows_cover      12  離れ・矢 0・遮蔽あり・夜の残り(take_cover 5 / hold 4 / raise 2 / drink 1)
    hp_ambiguous          9  hp 31〜32・薬なし(retreat 5 / hold 2 / shoot 2)
    wounded_vs_alarm      5  hp 21〜32 で L1 と L5 が競る残り(raise 2 / drink 2 / melee 1)
    mage_no_arrows        2  警報済み魔術師・矢 0 の残り(hold 2、gap)
    troll_no_arrows       2  警報済みトロル・味方あり・離れ・矢 0(hold 1 / take_cover 1)
    weak_troll_alone      1  警報済みトロル・単独・隣接か遮蔽なし・敵の体力 15 以下(hold 1)
    weak_mage_unclear     1  警報未・離れた弱い魔術師・矢ありの残り(raise 1)
    hurt_vs_alarm         1  hp<=20・警報未トロル・distance<=2・薬あり(drink 1、gap)
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
_HURT_MAX = 20      # これ以下は明らかにひどい
_WOUNDED_MAX = 30   # 21〜30 は手負い。決め手 hp<=30 が最も多い。31〜32 は会話で割れる
_FINE_MIN = 33      # これ以上はひどくない(飲む最高の 31 と、次の例 35 の間)

# 警報未の群れ
_HORDE_MIN = 4          # 敵がこれ以上なら警報
_OUTNUMBERED_MIN = 3    # 味方 0 で敵がこれ以上なら警報

# 傷と警報が競るとき、これ以上離れていれば警報が先(隣接 1 は退く・飲む、5 以上は警報)
_ALARM_FIRST_DIST = 3

# 警報未の離れた魔術師を「弱っている」と見る敵の体力の上限(shoot の 30 と raise の 40 の間)
_WEAK_MAGE_MAX = 35
# 弱った魔術師を射るのに要る矢(raise の決め手 arrows<=2 と shoot の決め手 arrows>=6 の間)
_WEAK_MAGE_ARROWS_MIN = 4

# 矢の無いとき、魔術師に「詰めて斬る」距離(melee の決め手 distance<=2)
_MAGE_CLOSE_MAX = 2

# 単独で向き合うトロルを「瀕死」と見る敵の体力の上限(hold の 10 と retreat の 20 の間)
_WEAK_TROLL_MAX = 15


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
    hurt = hp <= _HURT_MAX
    serious_group = enemy != "none" and (
        count >= _HORDE_MIN or (count >= _OUTNUMBERED_MIN and allies == 0))

    # --- L1 と L5 が競る所: 敵が遠いうちは、傷があっても警報が先 ---
    if (not fine and enemy != "none" and not alarm
            and dist >= _ALARM_FIRST_DIST):
        if enemy == "troll":
            return ("raise_alarm", "hurt_troll_alarm")
        if not potion:
            if enemy == "mage" and not hurt:
                return ("raise_alarm", "wounded_mage_alarm")
            if serious_group:
                return ("raise_alarm", "hurt_horde_alarm")

    # --- L1: ひどく傷ついている(hp<=20) ---
    if hurt:
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
            # 薬あり、または distance<=2(遠くて薬なしは上で警報)
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
            return ("hold_position", "wounded_alone_hold")
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
        if enemy_hp <= _WEAK_TROLL_MAX:
            return (None, "weak_troll_alone")
        return ("retreat", "troll_alone_retreat")

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
                if count <= 2 and arrows >= _WEAK_MAGE_ARROWS_MIN:
                    return ("shoot", "weak_mage_shoot")
                return (None, "weak_mage_unclear")
            return ("raise_alarm", "mage_alarm")
        if enemy == "orc" and count >= 2:
            if dist >= 2:
                if time == "night":
                    return ("raise_alarm", "orc_night_alarm")
                if count == 2 and allies >= 1 and arrows >= 1:
                    return ("shoot", "orc_pair_day_shoot")
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
            # ここに来る魔術師は警報済み
            if dist <= _MAGE_CLOSE_MAX and not cover:
                return ("melee_attack", "mage_close_melee")
            if dist > _MAGE_CLOSE_MAX and cover:
                return ("take_cover", "mage_no_arrows_cover")
            return (None, "mage_no_arrows")
        if cover:
            if time == "day":
                return ("hold_position", "no_arrows_cover_day")
            if alarm and allies == 0:
                return ("take_cover", "night_alone_cover")
            return (None, "no_arrows_cover")
        return ("hold_position", "no_arrows_hold")
    if enemy == "mage":
        return ("shoot", "mage_shoot")
    return ("shoot", "shoot_far")
