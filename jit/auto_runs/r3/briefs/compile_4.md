# 翻訳の依頼 — 走り r3、第 4 版

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

## いまの方針(c3)
```python
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

```

## 熱さの帳簿(審判のラベル 374 件、会話 10 本を、いまの方針の枝ごとに数えた)

| 枝 | 件数 | 会話 | 方針の答え | 一致 | 会話の多数が方針と同じ | 審判の答え | 根拠 | 決め手(多い順) |
|---|---|---|---|---|---|---|---|---|
| no_threat_hold | 60 | 10 | hold_position | 60/60 | 10/10 | {'hold_position': 60} | L7 60, L1 8, L6 1; gap 8 | enemy=none 60, hp>=40 2, hp>=39 2, hp>=34 2 |
| shoot_far | 36 | 8 | shoot | 34/36 | 8/8 | {'shoot': 34, 'raise_alarm': 1, 'take_cover': 1} | L2 35, L6 1, L5 1; gap 2 | distance>=2 13, arrows>=1 12, distance>=6 4, arrows>=2 4 |
| no_arrows_cover_day | 28 | 10 | hold_position | 24/28 | 9/10 | {'hold_position': 24, 'take_cover': 4} | L0 4; gap 28 | arrows=0 28, distance>=2 7, distance>=8 6, allies>=3 5 |
| orc_alarm_unclear | 20 | 8 | None | -/- | -/8 | {'raise_alarm': 8, 'melee_attack': 9, 'shoot': 1, 'hold_position': 2} | L2 14, L5 11, L6 4; gap 14 | alarm=false 8, distance<=1 8, allies=0 5, enemy_count>=2 5 |
| horde_alarm | 17 | 7 | raise_alarm | 17/17 | 7/7 | {'raise_alarm': 17} | L5 17, L2 6, L6 5; gap 13 | alarm=false 17, enemy_count>=5 9, enemy_count>=4 8, allies=0 5 |
| melee_adjacent | 15 | 6 | melee_attack | 15/15 | 6/6 | {'melee_attack': 15} | L2 15; gap 1 | distance<=1 8, distance=1 7, enemy_hp<=10 4, enemy_hp<=20 2 |
| mage_alarm | 15 | 7 | raise_alarm | 14/15 | 6/7 | {'raise_alarm': 14, 'shoot': 1} | L5 15, L4 11, L6 3; gap 11 | enemy=mage 15, alarm=false 14, arrows=0 5, arrows<=1 2 |
| no_arrows_cover | 15 | 7 | None | -/- | -/7 | {'hold_position': 4, 'take_cover': 8, 'raise_alarm': 2, 'drink_potion': 1} | L6 11, L5 2, L1 1; gap 11 | arrows=0 13, time=night 11, cover=true 8, enemy=goblin 2 |
| hp_ambiguous | 13 | 6 | None | -/- | -/6 | {'shoot': 2, 'retreat': 6, 'hold_position': 5} | L1 8, L7 6, L2 5; gap 11 | potion=false 6, enemy=none 5, hp>=32 3, hp<=32 3 |
| hurt_no_threat_retreat | 13 | 5 | retreat | 13/13 | 5/5 | {'retreat': 13} | L7 13, L1 13; gap 13 | potion=false 13, allies>=1 7, hp<=20 6, hp<=15 2 |
| wounded_drink | 11 | 7 | drink_potion | 11/11 | 7/7 | {'drink_potion': 11} | L1 11, L2 3, L5 1; gap 5 | potion=true 11, hp<=21 3, enemy=none 3, hp<=31 2 |
| wounded_retreat | 10 | 8 | retreat | 9/10 | 7/8 | {'retreat': 9, 'shoot': 1} | L1 10, L3 3, L2 3; gap 7 | potion=false 8, hp<=30 4, allies=0 4, enemy=troll 3 |
| orc_night_alarm | 10 | 7 | raise_alarm | 9/10 | 6/7 | {'raise_alarm': 9, 'shoot': 1} | L6 9, L5 9, L2 8; gap 8 | time=night 9, alarm=false 9, allies<=1 3, enemy=orc 2 |
| troll_alarm | 8 | 5 | raise_alarm | 8/8 | 5/5 | {'raise_alarm': 8} | L5 8, L3 7, L2 3; gap 5 | enemy=troll 8, alarm=false 8, allies=0 2, arrows=0 1 |
| wounded_alone_hold | 8 | 6 | hold_position | 7/8 | 5/6 | {'hold_position': 7, 'retreat': 1} | L7 8, L1 6, L0 5; gap 8 | enemy=none 7, allies=0 7, potion=false 2, post=gate 1 |
| no_arrows_hold | 8 | 5 | hold_position | 8/8 | 5/5 | {'hold_position': 8} | ; gap 8 | arrows=0 8, distance>=2 4, enemy=goblin 2, cover=false 2 |
| hurt_drink | 6 | 4 | drink_potion | 6/6 | 4/4 | {'drink_potion': 6} | L1 6, L5 1, L4 1; gap 1 | potion=true 6, hp<=12 2, hp<=30 1, enemy=none 1 |
| mage_melee_first | 6 | 5 | melee_attack | 6/6 | 5/5 | {'melee_attack': 6} | L2 6, L4 6, L5 4; gap 6 | enemy=mage 6, distance<=1 5, enemy_hp<=30 2, distance=1 1 |
| wounded_handover | 6 | 3 | retreat | 6/6 | 3/3 | {'retreat': 6} | L7 6, L1 6; gap 6 | potion=false 6, allies>=1 5, hp<=30 4, hp<=33 1 |
| troll_alone_retreat | 6 | 4 | retreat | 6/6 | 4/4 | {'retreat': 6} | L3 6, L2 5, L6 2; gap 6 | enemy=troll 6, allies=0 6, time=night 2, enemy_count>=2 1 |
| wounded_vs_alarm | 5 | 3 | None | -/- | -/3 | {'raise_alarm': 2, 'drink_potion': 2, 'melee_attack': 1} | L1 4, L5 3, L4 3; gap 5 | enemy=mage 3, distance>=10 3, alarm=false 2, potion=true 2 |
| troll_shoot_allied | 5 | 4 | shoot | 5/5 | 4/4 | {'shoot': 5} | L2 5, L3 5; gap 2 | allies>=2 4, arrows>=1 2, distance>=2 2, distance>=4 1 |
| weak_mage_shoot | 5 | 4 | shoot | 5/5 | 4/4 | {'shoot': 5} | L4 5, L2 4, L5 3; gap 5 | enemy=mage 5, enemy_hp<=10 3, enemy_hp<=30 2, arrows>=6 1 |
| outnumbered_alarm | 4 | 3 | raise_alarm | 4/4 | 3/3 | {'raise_alarm': 4} | L5 4, L2 3, L6 2; gap 4 | enemy_count>=3 4, allies=0 4, alarm=false 4 |
| night_alone_cover | 4 | 4 | take_cover | 4/4 | 4/4 | {'take_cover': 4} | L6 4; gap 3 | arrows=0 4, cover=true 4, time=night 3, allies=0 1 |
| troll_alone_cover | 4 | 3 | take_cover | 4/4 | 3/3 | {'take_cover': 4} | L6 4, L3 4, L2 1; gap 4 | enemy=troll 4, allies=0 4, cover=true 4 |
| mage_shoot | 4 | 3 | shoot | 4/4 | 3/3 | {'shoot': 4} | L2 4, L4 4 | enemy=mage 4, arrows>=4 2, distance>=6 1, arrows>=7 1 |
| orc_pair_day_shoot | 4 | 3 | shoot | 4/4 | 3/3 | {'shoot': 4} | L2 4; gap 1 | distance>=12 2, arrows>=1 2, distance>=2 2, allies>=3 1 |
| mage_close_melee | 3 | 3 | melee_attack | 3/3 | 3/3 | {'melee_attack': 3} | L4 3, L2 1; gap 3 | enemy=mage 3, arrows=0 3, distance<=2 2, hp>=90 1 |
| hurt_retreat | 3 | 3 | retreat | 3/3 | 3/3 | {'retreat': 3} | L1 3, L0 1, L5 1; gap 1 | potion=false 3, hp<=30 1, hp<=20 1, hp<=7 1 |
| hurt_troll_alarm | 3 | 3 | raise_alarm | 3/3 | 3/3 | {'raise_alarm': 3} | L5 3, L1 3, L3 1; gap 3 | alarm=false 3, enemy=troll 3, distance>=12 1, distance>=10 1 |
| mage_no_arrows_cover | 3 | 3 | take_cover | 3/3 | 3/3 | {'take_cover': 3} | ; gap 3 | arrows=0 3, cover=true 3, enemy=mage 2, distance>=6 1 |
| hurt_horde_alarm | 3 | 3 | raise_alarm | 3/3 | 3/3 | {'raise_alarm': 3} | L5 3, L1 3, L6 1; gap 3 | alarm=false 3, enemy_count>=4 2, allies=0 1, distance>=5 1 |
| mage_no_arrows | 3 | 3 | None | -/- | -/3 | {'hold_position': 2, 'drink_potion': 1} | L1 1, L4 1; gap 3 | arrows=0 3, distance>=12 1, cover=false 1, hp>=82 1 |
| wounded_mage_alarm | 3 | 2 | raise_alarm | 3/3 | 2/2 | {'raise_alarm': 3} | L5 3, L1 3, L4 1; gap 3 | alarm=false 3, enemy=mage 3, enemy_count>=4 1, hp<=21 1 |
| troll_no_arrows | 2 | 2 | None | -/- | -/2 | {'hold_position': 1, 'take_cover': 1} | L3 2; gap 2 | arrows=0 2, distance>=12 1, allies>=3 1, enemy=troll 1 |
| troll_melee_allied | 2 | 2 | melee_attack | 2/2 | 2/2 | {'melee_attack': 2} | L2 2, L3 2 | distance<=1 2, enemy=troll 1, allies>=1 1, allies>=2 1 |
| hurt_vs_alarm | 1 | 1 | None | -/- | -/1 | {'drink_potion': 1} | L5 1, L1 1, L3 1; gap 1 | hp<=20 1, potion=true 1, enemy=troll 1 |
| weak_troll_alone | 1 | 1 | None | -/- | -/1 | {'hold_position': 1} | L0 1, L3 1; gap 1 | enemy_hp<=10 1, hp>=83 1, arrows=0 1 |
| weak_mage_unclear | 1 | 1 | None | -/- | -/1 | {'raise_alarm': 1} | L5 1, L4 1; gap 1 | alarm=false 1, enemy_count>=3 1, distance>=12 1 |

## 食い違いと棄権の例(全部。[根拠] 決め手 「理由」 会話)
### shoot_far
- 方針=shoot 審判=raise_alarm [L5,L6+gap] alarm=false,time=night,enemy_count>=3 「夜に小鬼の群れが来た、遠いうちに警報を鳴らす」 (round2_s1) | hp=90 enemy=goblin distance=7 enemy_count=3 enemy_hp=80 allies=1 potion=True arrows=13 cover=True alarm=False post=wall time=night
- 方針=shoot 審判=take_cover [L0,L2+gap] hp<=38,enemy_count>=4,cover=true 「体力が減り小鬼4体、警報済みなので隠れて援軍を待つ」 (round2_s2) | hp=38 enemy=goblin distance=2 enemy_count=4 enemy_hp=70 allies=1 potion=False arrows=1 cover=True alarm=True post=gate time=day
### no_arrows_cover_day
- 方針=hold_position 審判=take_cover [gap] hp<=42,potion=false,arrows=0 「矢も薬も無く体力半分以下、遮蔽で門に踏み止まる」 (round1_s2) | hp=42 enemy=goblin distance=4 enemy_count=3 enemy_hp=60 allies=3 potion=False arrows=0 cover=True alarm=True post=gate time=day
- 方針=hold_position 審判=take_cover [L0+gap] arrows=0,hp<=42,cover=true 「矢が無く傷も浅くないので遮蔽で接近を待つ」 (round4_s1) | hp=42 enemy=goblin distance=4 enemy_count=3 enemy_hp=60 allies=3 potion=False arrows=0 cover=True alarm=True post=gate time=day
- 方針=hold_position 審判=take_cover [gap] arrows=0,distance>=4,cover=true 「矢が無く敵は遠い、傷もあるので遮蔽で待つ」 (round4_s2) | hp=42 enemy=goblin distance=4 enemy_count=3 enemy_hp=60 allies=3 potion=False arrows=0 cover=True alarm=True post=gate time=day
- 方針=hold_position 審判=take_cover [L0+gap] arrows=0,enemy_count>=5,cover=true 「矢が無く多勢の小鬼、警報済みなので遮蔽で接近を待つ」 (round4_s2) | hp=82 enemy=goblin distance=6 enemy_count=5 enemy_hp=80 allies=3 potion=True arrows=0 cover=True alarm=True post=gate time=day
### orc_alarm_unclear
- 方針=None 審判=hold_position [gap] arrows=0,distance>=9 「矢が無く二対二、持ち場で迎え撃つ」 (round3_s1) | hp=64 enemy=orc distance=9 enemy_count=2 enemy_hp=70 allies=1 potion=True arrows=0 cover=True alarm=False post=gate time=day
- 方針=None 審判=hold_position [gap] arrows=0,distance>=2,allies>=3 「矢が無く敵は二マス先、味方と通路で待ち構える」 (round4_s2) | hp=68 enemy=orc distance=2 enemy_count=2 enemy_hp=80 allies=3 potion=False arrows=0 cover=False alarm=False post=corridor time=day
- 方針=None 審判=melee_attack [L2,L5,L6+gap] distance=1,hp>=91,allies>=2 「味方2人と体力十分、隣接オークを斬る」 (round1_s3) | hp=91 enemy=orc distance=1 enemy_count=2 enemy_hp=60 allies=2 potion=True arrows=0 cover=False alarm=False post=gate time=night
- 方針=None 審判=melee_attack [L2] distance<=1,hp>=34 「隣接したオークと近接で戦う」 (round2_s3) | hp=82 enemy=orc distance=1 enemy_count=2 enemy_hp=80 allies=0 potion=False arrows=3 cover=False alarm=False post=gate time=night
- 方針=None 審判=melee_attack [L2,L5+gap] distance<=1,enemy_hp<=20 「隣接する瀕死のオークを先に倒すのが最善」 (round3_s1) | hp=94 enemy=orc distance=1 enemy_count=2 enemy_hp=20 allies=0 potion=False arrows=20 cover=True alarm=False post=gate time=day
- 方針=None 審判=melee_attack [L2,L6+gap] distance<=1,allies>=3,hp>=95 「隣接、夜でも味方が多く近接で戦う」 (round3_s2) | hp=95 enemy=orc distance=1 enemy_count=2 enemy_hp=70 allies=3 potion=False arrows=4 cover=True alarm=False post=gate time=night
- 方針=None 審判=melee_attack [L2,L5+gap] distance<=1,hp>=91 「オークが隣接しており、警報より先に近接で応じる」 (round4_s1) | hp=91 enemy=orc distance=1 enemy_count=2 enemy_hp=60 allies=2 potion=True arrows=0 cover=False alarm=False post=gate time=night
- 方針=None 審判=melee_attack [L2] distance<=1 「隣接するオークと近接で戦う」 (round4_s1) | hp=66 enemy=orc distance=1 enemy_count=2 enemy_hp=50 allies=2 potion=False arrows=0 cover=False alarm=False post=wall time=day
- 方針=None 審判=melee_attack [L2] distance<=1 「隣接するオークと近接で戦う」 (round4_s1) | hp=81 enemy=orc distance=1 enemy_count=2 enemy_hp=30 allies=3 potion=False arrows=2 cover=False alarm=False post=gate time=day
- 方針=None 審判=melee_attack [L2] distance<=1,allies>=2 「隣接したオークに味方と共に近接で当たる」 (round4_s2) | hp=91 enemy=orc distance=1 enemy_count=2 enemy_hp=60 allies=2 potion=True arrows=0 cover=False alarm=False post=gate time=night
- 方針=None 審判=melee_attack [L2] distance<=1,allies>=2 「隣接したオークに味方と共に近接で当たる」 (round4_s2) | hp=80 enemy=orc distance=1 enemy_count=2 enemy_hp=40 allies=2 potion=False arrows=3 cover=False alarm=False post=corridor time=night
- 方針=None 審判=raise_alarm [L2,L5,L6+gap] alarm=false,allies=0,time=night 「夜の門で単独、オーク2体に先に警報を鳴らす」 (round1_s2) | hp=82 enemy=orc distance=1 enemy_count=2 enemy_hp=80 allies=0 potion=False arrows=3 cover=False alarm=False post=gate time=night
- 方針=None 審判=raise_alarm [L5,L6+gap] alarm=false,enemy_count>=2,allies=0 「夜に単独でオーク二体、斬り合う前に警報を鳴らす」 (round2_s1) | hp=82 enemy=orc distance=1 enemy_count=2 enemy_hp=80 allies=0 potion=False arrows=3 cover=False alarm=False post=gate time=night
- 方針=None 審判=raise_alarm [L5+gap] alarm=false,enemy_count>=2,allies=0 「単独でオーク二体が迫る、遠いうちに警報を鳴らす」 (round2_s1) | hp=83 enemy=orc distance=7 enemy_count=2 enemy_hp=70 allies=0 potion=True arrows=0 cover=True alarm=False post=wall time=day
- 方針=None 審判=raise_alarm [L5,L2+gap] allies=0,enemy_count>=2,alarm=false 「単独でオーク二体、距離のあるうちに警報」 (round3_s1) | hp=96 enemy=orc distance=7 enemy_count=2 enemy_hp=30 allies=0 potion=True arrows=4 cover=False alarm=False post=gate time=day
- 方針=None 審判=raise_alarm [L5,L2+gap] alarm=false,enemy_count>=3,enemy=orc 「オーク三体は深刻、矢一本より警報が先」 (round3_s2) | hp=61 enemy=orc distance=8 enemy_count=3 enemy_hp=40 allies=1 potion=True arrows=1 cover=True alarm=False post=corridor time=day
- 方針=None 審判=raise_alarm [L5,L2+gap] alarm=false,enemy_count>=3,allies>=2 「オーク三体で未警報、隣の敵は味方に任す」 (round3_s2) | hp=55 enemy=orc distance=1 enemy_count=3 enemy_hp=20 allies=2 potion=True arrows=2 cover=False alarm=False post=wall time=day
- 方針=None 審判=raise_alarm [L5+gap] allies=0,enemy_count>=2,alarm=false 「味方も矢も無くオーク二体、警報で助けを呼ぶ」 (round4_s1) | hp=83 enemy=orc distance=7 enemy_count=2 enemy_hp=70 allies=0 potion=True arrows=0 cover=True alarm=False post=wall time=day
- 方針=None 審判=raise_alarm [L5+gap] alarm=false,enemy_count>=2,allies<=0 「味方なしで敵二体、矢も無いので警報で援軍を呼ぶ」 (round4_s2) | hp=83 enemy=orc distance=7 enemy_count=2 enemy_hp=70 allies=0 potion=True arrows=0 cover=True alarm=False post=wall time=day
- 方針=None 審判=shoot [L2] distance>=2,arrows>=1 「離れたオークを矢で射る」 (round2_s3) | hp=98 enemy=orc distance=4 enemy_count=2 enemy_hp=30 allies=0 potion=False arrows=8 cover=False alarm=False post=corridor time=day
### mage_alarm
- 方針=raise_alarm 審判=shoot [L4,L5+gap] enemy=mage,enemy_count=1,arrows>=11 「魔術師単独なら警報より先に射て早く仕留める」 (round1_s2) | hp=84 enemy=mage distance=6 enemy_count=1 enemy_hp=40 allies=0 potion=True arrows=11 cover=True alarm=False post=gate time=day
### no_arrows_cover
- 方針=None 審判=drink_potion [L1,L6+gap] hp<=33,potion=true,time=night 「夜で体力も心細い、敵が来る前に飲む」 (round3_s2) | hp=33 enemy=goblin distance=4 enemy_count=1 enemy_hp=40 allies=2 potion=True arrows=0 cover=True alarm=False post=corridor time=night
- 方針=None 審判=hold_position [gap] arrows=0,distance>=7,enemy=goblin 「矢が無く小鬼は遠い、門で迎え撃つ構え」 (round2_s1) | hp=97 enemy=goblin distance=7 enemy_count=2 enemy_hp=70 allies=2 potion=False arrows=0 cover=True alarm=True post=gate time=night
- 方針=None 審判=hold_position [gap] arrows=0,distance>=8,alarm=true 「矢が無く敵は遠い、警報済みで通路を固める」 (round2_s1) | hp=90 enemy=goblin distance=8 enemy_count=4 enemy_hp=40 allies=1 potion=False arrows=0 cover=True alarm=True post=corridor time=night
- 方針=None 審判=hold_position [gap] arrows=0,distance>=2,allies>=3 「矢が無いので味方と持ち場で迎え撃つ」 (round3_s1) | hp=82 enemy=goblin distance=2 enemy_count=2 enemy_hp=80 allies=3 potion=False arrows=0 cover=True alarm=True post=corridor time=night
- 方針=None 審判=hold_position [gap] enemy=goblin,enemy_hp<=30,arrows=0 「弱いゴブリン一体、持ち場で迎え撃つ」 (round3_s1) | hp=91 enemy=goblin distance=4 enemy_count=1 enemy_hp=30 allies=0 potion=True arrows=0 cover=True alarm=False post=corridor time=night
- 方針=None 審判=raise_alarm [L5,L6+gap] time=night,allies=0,arrows=0 「夜に単独で射てず、用心して警報を鳴らす」 (round3_s1) | hp=96 enemy=orc distance=7 enemy_count=1 enemy_hp=100 allies=0 potion=True arrows=0 cover=True alarm=False post=gate time=night
- 方針=None 審判=raise_alarm [L5,L6+gap] enemy_count>=3,alarm=false,time=night 「夜の門に小鬼三体、未警報なので鳴らす」 (round3_s2) | hp=39 enemy=goblin distance=3 enemy_count=3 enemy_hp=70 allies=2 potion=False arrows=0 cover=True alarm=False post=gate time=night
- 方針=None 審判=take_cover [L6] time=night,arrows=0,cover=true 「夜で矢も無い、遮蔽に隠れて接近を待つ」 (round2_s2) | hp=65 enemy=orc distance=12 enemy_count=2 enemy_hp=20 allies=2 potion=False arrows=0 cover=True alarm=True post=corridor time=night
- 方針=None 審判=take_cover [L6] time=night,arrows=0,cover=true 「夜で矢も無い、遮蔽に隠れて接近を待つ」 (round2_s2) | hp=82 enemy=orc distance=11 enemy_count=1 enemy_hp=50 allies=2 potion=False arrows=0 cover=True alarm=True post=gate time=night
- 方針=None 審判=take_cover [L6+gap] arrows=0,time=night,cover=true 「矢が無い夜、遮蔽に隠れて寄るのを待つ」 (round2_s3) | hp=95 enemy=goblin distance=12 enemy_count=1 enemy_hp=40 allies=0 potion=False arrows=0 cover=True alarm=False post=gate time=night
- 方針=None 審判=take_cover [L6] time=night,arrows=0,cover=true 「夜で矢が無い、遮蔽に隠れて接近を待つ」 (round3_s2) | hp=93 enemy=goblin distance=7 enemy_count=1 enemy_hp=20 allies=0 potion=False arrows=0 cover=True alarm=False post=gate time=night
- 方針=None 審判=take_cover [L6] time=night,arrows=0,cover=true 「夜に小鬼四体、矢が無く遮蔽で備える」 (round3_s2) | hp=75 enemy=goblin distance=2 enemy_count=4 enemy_hp=10 allies=1 potion=False arrows=0 cover=True alarm=True post=corridor time=night
- 方針=None 審判=take_cover [L6+gap] time=night,arrows=0,cover=true 「夜で矢が無く、遮蔽に入って小鬼の接近を待つ」 (round4_s1) | hp=87 enemy=goblin distance=3 enemy_count=2 enemy_hp=70 allies=3 potion=True arrows=0 cover=True alarm=False post=gate time=night
- 方針=None 審判=take_cover [L6+gap] time=night,arrows=0,cover=true 「夜で矢が無く、遮蔽でオークの接近を待つ」 (round4_s1) | hp=67 enemy=orc distance=7 enemy_count=1 enemy_hp=10 allies=2 potion=False arrows=0 cover=True alarm=True post=corridor time=night
- 方針=None 審判=take_cover [L6+gap] time=night,cover=true,arrows=0 「夜で矢も無く傷もある、遮蔽で様子を見る」 (round4_s2) | hp=42 enemy=goblin distance=6 enemy_count=2 enemy_hp=30 allies=2 potion=False arrows=0 cover=True alarm=False post=wall time=night
### hp_ambiguous
- 方針=None 審判=hold_position [L7+gap] enemy=none,hp>=32,time=day 「昼で脅威も無く、まだ持ち場を守れる体力」 (round2_s1) | hp=32 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=20 cover=True alarm=False post=corridor time=day
- 方針=None 審判=hold_position [L7] enemy=none,hp>=32 「脅威が無く深手でもないので持ち場を守る」 (round2_s2) | hp=32 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=2 cover=True alarm=False post=gate time=day
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp<=32 「深手だが脅威が無く、今は持ち場を離れない」 (round4_s1) | hp=32 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=0 cover=True alarm=False post=wall time=day
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none 「深手だが敵は見えず、持ち場を守る」 (round4_s1) | hp=32 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=18 cover=True alarm=True post=gate time=day
- 方針=None 審判=hold_position [L7+gap] enemy=none,hp>=32 「敵は無く、退くほどの深手でもないので持ち場を守る」 (round4_s2) | hp=32 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=11 cover=True alarm=False post=gate time=day
- 方針=None 審判=retreat [L1,L6+gap] hp<=31,potion=false,time=night 「夜に体力が低く薬も無い、無理せず退く」 (round2_s1) | hp=31 enemy=goblin distance=9 enemy_count=3 enemy_hp=40 allies=1 potion=False arrows=5 cover=False alarm=True post=wall time=night
- 方針=None 審判=retreat [L1,L6+gap] hp<=32,potion=false,time=night 「夜に体力が低く薬も無い、門を味方に任せ退く」 (round2_s1) | hp=32 enemy=orc distance=9 enemy_count=3 enemy_hp=20 allies=3 potion=False arrows=15 cover=True alarm=True post=gate time=night
- 方針=None 審判=retreat [L1,L6,L2+gap] hp<=31,enemy_count>=4,potion=false 「深手で夜にオーク4体、薬も遮蔽も無く退く」 (round2_s2) | hp=31 enemy=orc distance=10 enemy_count=4 enemy_hp=90 allies=1 potion=False arrows=2 cover=False alarm=True post=corridor time=night
- 方針=None 審判=retreat [L1,L2+gap] hp<=33,potion=false,alarm=true 「深手で薬も無い、警報済みなので退く」 (round2_s3) | hp=31 enemy=goblin distance=9 enemy_count=3 enemy_hp=40 allies=1 potion=False arrows=5 cover=False alarm=True post=wall time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=33,potion=false,allies>=1 「深手で薬も無い、味方に門を任せて退く」 (round2_s3) | hp=31 enemy=none distance=None enemy_count=0 enemy_hp=None allies=3 potion=False arrows=15 cover=False alarm=False post=gate time=night
- 方針=None 審判=retreat [L1,L2+gap] hp<=32,potion=false,enemy_count>=3 「深手で薬が無く、オーク三体が来る前に退く」 (round4_s1) | hp=32 enemy=orc distance=10 enemy_count=3 enemy_hp=80 allies=2 potion=False arrows=5 cover=True alarm=True post=gate time=day
- 方針=None 審判=shoot [L2+gap] distance>=2,arrows>=1,hp>=31 「手負いだが敵は遠く、射るだけなら危険は小さい」 (round1_s1) | hp=31 enemy=goblin distance=9 enemy_count=3 enemy_hp=40 allies=1 potion=False arrows=5 cover=False alarm=True post=wall time=night
- 方針=None 審判=shoot [L2] distance>=6,arrows>=18 「敵は離れ矢も十分、深手ほどではなく射る」 (round2_s2) | hp=32 enemy=goblin distance=6 enemy_count=2 enemy_hp=80 allies=1 potion=False arrows=18 cover=False alarm=True post=gate time=day
### wounded_retreat
- 方針=retreat 審判=shoot [L1,L2+gap] enemy_hp<=10,enemy_count<=1,distance>=7 「傷は深いが遠くの瀕死ゴブリン一体を射止める」 (round2_s3) | hp=26 enemy=goblin distance=7 enemy_count=1 enemy_hp=10 allies=1 potion=False arrows=9 cover=False alarm=False post=wall time=day
### orc_night_alarm
- 方針=raise_alarm 審判=shoot [L2] distance>=2,arrows>=1,enemy_hp<=20 「離れた手負いのオークを矢で射る」 (round2_s3) | hp=99 enemy=orc distance=3 enemy_count=2 enemy_hp=20 allies=0 potion=True arrows=11 cover=False alarm=False post=corridor time=night
### wounded_alone_hold
- 方針=hold_position 審判=retreat [L1,L7+gap] hp<=28,potion=false,allies=0 「深手で薬も無く夜に単独、今のうちに退く」 (round2_s2) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=True alarm=False post=gate time=night
### wounded_vs_alarm
- 方針=None 審判=drink_potion [L1,L5+gap] hp<=28,potion=true,distance>=10 「重傷で敵は遠い、今のうちに薬を飲む」 (round3_s1) | hp=28 enemy=mage distance=10 enemy_count=2 enemy_hp=80 allies=2 potion=True arrows=10 cover=False alarm=False post=wall time=night
- 方針=None 審判=drink_potion [L1+gap] hp<=31,potion=true,distance>=7 「体力が三割、敵が遠いうちに薬を飲む」 (round3_s1) | hp=31 enemy=goblin distance=7 enemy_count=4 enemy_hp=60 allies=3 potion=True arrows=19 cover=False alarm=False post=wall time=day
- 方針=None 審判=melee_attack [L2,L4,L1+gap] enemy=mage,distance<=1,enemy_hp<=20 「隣の瀕死の魔術師を倒せば脅威が消える」 (round3_s1) | hp=30 enemy=mage distance=1 enemy_count=1 enemy_hp=20 allies=1 potion=True arrows=3 cover=True alarm=False post=gate time=day
- 方針=None 審判=raise_alarm [L4,L5+gap] enemy=mage,alarm=false,distance>=10 「深手だが魔術師はまだ遠い、先に警報を鳴らす」 (round1_s1) | hp=28 enemy=mage distance=10 enemy_count=2 enemy_hp=80 allies=2 potion=True arrows=10 cover=False alarm=False post=wall time=night
- 方針=None 審判=raise_alarm [L5,L1,L4+gap] alarm=false,enemy=mage,distance>=10 「魔術師が遠いうちに警報、回復は次」 (round3_s2) | hp=28 enemy=mage distance=10 enemy_count=2 enemy_hp=80 allies=2 potion=True arrows=10 cover=False alarm=False post=wall time=night
### mage_no_arrows
- 方針=None 審判=drink_potion [L1,L4+gap] hp<=39,potion=true,arrows=0 「深手で矢も無く魔術師に届かず、先に回復する」 (round4_s1) | hp=39 enemy=mage distance=3 enemy_count=1 enemy_hp=50 allies=1 potion=True arrows=0 cover=False alarm=True post=gate time=day
- 方針=None 審判=hold_position [gap] arrows=0,distance>=12 「矢が無く魔術師は遠い、持ち場を守る」 (round3_s1) | hp=93 enemy=mage distance=12 enemy_count=2 enemy_hp=30 allies=3 potion=True arrows=0 cover=False alarm=True post=gate time=day
- 方針=None 審判=hold_position [gap] arrows=0,cover=false,hp>=82 「矢も遮蔽も無いが体力はある、門を守る」 (round3_s2) | hp=82 enemy=mage distance=8 enemy_count=1 enemy_hp=80 allies=0 potion=False arrows=0 cover=False alarm=True post=gate time=day
### troll_no_arrows
- 方針=None 審判=hold_position [L3+gap] arrows=0,distance>=12,allies>=3 「矢が無く敵は遠い、味方3人と門を固めて待つ」 (round1_s2) | hp=92 enemy=troll distance=12 enemy_count=5 enemy_hp=40 allies=3 potion=True arrows=0 cover=True alarm=True post=gate time=day
- 方針=None 審判=take_cover [L3+gap] enemy=troll,arrows=0,cover=true 「矢が無く体力も半ば、迫るトロルに備え隠れる」 (round2_s2) | hp=42 enemy=troll distance=4 enemy_count=2 enemy_hp=60 allies=1 potion=False arrows=0 cover=True alarm=True post=gate time=day
### hurt_vs_alarm
- 方針=None 審判=drink_potion [L1,L3,L5+gap] hp<=20,potion=true,enemy=troll 「瀕死でトロルが隣、まず回復薬で持ちこたえる」 (round2_s3) | hp=14 enemy=troll distance=1 enemy_count=1 enemy_hp=10 allies=0 potion=True arrows=3 cover=False alarm=False post=corridor time=day
### weak_troll_alone
- 方針=None 審判=hold_position [L0,L3+gap] enemy_hp<=10,hp>=83,arrows=0 「瀕死のトロルなら門で迎え撃てる」 (round3_s2) | hp=83 enemy=troll distance=5 enemy_count=1 enemy_hp=10 allies=0 potion=False arrows=0 cover=False alarm=True post=gate time=day
### weak_mage_unclear
- 方針=None 審判=raise_alarm [L5,L4+gap] alarm=false,enemy_count>=3,distance>=12 「魔術師込み三体、遠いうちに警報」 (round3_s2) | hp=99 enemy=mage distance=12 enemy_count=3 enemy_hp=30 allies=1 potion=False arrows=17 cover=False alarm=False post=gate time=day

## 訊き直した状態(同じ状態を会話 3 本以上に訊いた。18 件のうち票が割れたもの 4 件)
- 票 {'hold_position': 2, 'retreat': 1} | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=True alarm=False post=gate time=night | hold_position「深手だが敵はなく、夜の門を空けず持ち場に留まる」 / retreat「深手で薬も無く夜に単独、今のうちに退く」 / hold_position「脅威が無く単独、門を空けず持ち場を守る」
- 票 {'shoot': 1, 'retreat': 2} | hp=31 enemy=goblin distance=9 enemy_count=3 enemy_hp=40 allies=1 potion=False arrows=5 cover=False alarm=True post=wall time=night | shoot「手負いだが敵は遠く、射るだけなら危険は小さい」 / retreat「夜に体力が低く薬も無い、無理せず退く」 / retreat「深手で薬も無い、警報済みなので退く」
- 票 {'raise_alarm': 2, 'drink_potion': 1} | hp=28 enemy=mage distance=10 enemy_count=2 enemy_hp=80 allies=2 potion=True arrows=10 cover=False alarm=False post=wall time=night | raise_alarm「深手だが魔術師はまだ遠い、先に警報を鳴らす」 / drink_potion「重傷で敵は遠い、今のうちに薬を飲む」 / raise_alarm「魔術師が遠いうちに警報、回復は次」
- 票 {'raise_alarm': 2, 'melee_attack': 1} | hp=82 enemy=orc distance=1 enemy_count=2 enemy_hp=80 allies=0 potion=False arrows=3 cover=False alarm=False post=gate time=night | raise_alarm「夜の門で単独、オーク2体に先に警報を鳴らす」 / raise_alarm「夜に単独でオーク二体、斬り合う前に警報を鳴らす」 / melee_attack「隣接したオークと近接で戦う」

## 根拠が gap に偏り、答えが割れている枝(輪が同じ状態を複数の会話に訊き直している。会話の癖か、状態の違いかは、訊き直しの票で分かる)
- 枝 wounded_retreat: 審判の答え {'retreat': 9, 'shoot': 1}
- 枝 wounded_alone_hold: 審判の答え {'hold_position': 7, 'retreat': 1}
- 枝 hp_ambiguous: 審判の答え {'shoot': 2, 'retreat': 6, 'hold_position': 5}
- 枝 no_arrows_cover_day: 審判の答え {'hold_position': 24, 'take_cover': 4}
- 枝 wounded_vs_alarm: 審判の答え {'raise_alarm': 2, 'drink_potion': 2, 'melee_attack': 1}
- 枝 mage_alarm: 審判の答え {'raise_alarm': 14, 'shoot': 1}
- 枝 troll_no_arrows: 審判の答え {'hold_position': 1, 'take_cover': 1}
- 枝 orc_alarm_unclear: 審判の答え {'raise_alarm': 8, 'melee_attack': 9, 'shoot': 1, 'hold_position': 2}
- 枝 orc_night_alarm: 審判の答え {'raise_alarm': 9, 'shoot': 1}
- 枝 no_arrows_cover: 審判の答え {'hold_position': 4, 'take_cover': 8, 'raise_alarm': 2, 'drink_potion': 1}
- 枝 mage_no_arrows: 審判の答え {'hold_position': 2, 'drink_potion': 1}

## 出力
`/home/claude/sekizui/jit/auto_runs/r3/policies/c4.py` に書く。書いたら「完了」とだけ返す。