# 翻訳の依頼 — 走り r2、第 4 版(やり直し 1 回目)

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

追補(審判の会話の多数から足した一文。指示文と同じ重みで使う):
A1 hp が 31 以上あれば、回復薬が無くとも、敵が 9 マス以上離れ矢が残っている間は退かずに弓で射る。
A2 夜に矢が無く、味方がおらず、遮蔽があり、敵が 11 マス以上離れているなら、遮蔽に隠れる。
A3 警報が鳴っておらず、敵が魔術師一体で体力 40% 以下、6 マス以上離れ矢が 11 本以上残っているなら、警報より先に弓で射る。
A4 警報が鳴っておらず、hp が 28 以下で回復薬があり、敵が魔術師で 10 マス以上離れているなら、警報より先に回復薬を飲む。
A5 警報が鳴っており、矢が無く、味方が 3 人以上いて、敵が 4 マス以上離れているなら、遮蔽があっても持ち場を守る。
A6 敵がおらず、hp が 30 以下で回復薬が無いなら、味方が 1 人以上いれば退き、味方がいなければ持ち場を守る。

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

## いまの方針(b3)
```python
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

```

## 熱さの帳簿(審判のラベル 436 件、会話 12 本を、いまの方針の枝ごとに数えた)

| 枝 | 件数 | 会話 | 方針の答え | 一致 | 会話の多数が方針と同じ | 審判の答え | 根拠 | 決め手(多い順) |
|---|---|---|---|---|---|---|---|---|
| no_threat_hold | 63 | 12 | hold_position | 63/63 | 12/12 | {'hold_position': 63} | L7 63, L1 5; gap 5 | enemy=none 63, hp>=40 2, hp>=45 2, hp>=44 1 |
| no_arrows_hold | 47 | 12 | hold_position | 46/47 | 12/12 | {'hold_position': 46, 'take_cover': 1} | L5 1, L6 1; gap 47 | arrows=0 47, distance>=2 19, enemy=goblin 13, distance>=8 6 |
| shoot_far | 42 | 11 | shoot | 41/42 | 10/11 | {'shoot': 41, 'take_cover': 1} | L2 41, L6 1, L5 1; gap 2 | distance>=2 21, arrows>=1 13, enemy=goblin 6, distance>=4 5 |
| wounded_no_threat | 37 | 11 | None | -/- | -/11 | {'hold_position': 18, 'retreat': 18, 'take_cover': 1} | L7 37, L1 33, L6 3; gap 35 | potion=false 23, enemy=none 21, hp<=30 14, hp<=28 7 |
| horde_alarm | 19 | 8 | raise_alarm | 19/19 | 8/8 | {'raise_alarm': 19} | L5 19, L2 12, L6 4; gap 16 | alarm=false 19, enemy_count>=5 11, allies=0 8, enemy_count>=4 8 |
| hurt_retreat | 15 | 9 | retreat | 15/15 | 9/9 | {'retreat': 15} | L1 15, L3 5, L5 3; gap 5 | potion=false 14, hp<=30 6, enemy=troll 4, hp<=22 4 |
| hurt_no_threat | 15 | 8 | None | -/- | -/8 | {'retreat': 9, 'hold_position': 6} | L1 15, L7 12, L0 1; gap 15 | potion=false 9, enemy=none 6, allies=0 5, hp<=30 2 |
| melee_adjacent | 13 | 5 | melee_attack | 13/13 | 5/5 | {'melee_attack': 13} | L2 13; gap 1 | distance=1 8, distance<=1 5, enemy_hp<=10 4, hp>=40 1 |
| wounded_alarm_unclear | 12 | 8 | None | -/- | -/8 | {'raise_alarm': 3, 'drink_potion': 7, 'melee_attack': 1, 'shoot': 1} | L1 10, L5 8, L4 3; gap 12 | potion=true 7, distance>=10 6, enemy=mage 4, hp<=28 4 |
| troll_alarm | 10 | 6 | raise_alarm | 9/10 | 5/6 | {'raise_alarm': 9, 'melee_attack': 1} | L5 9, L3 8, L2 4; gap 6 | enemy=troll 9, alarm=false 9, allies=0 2, arrows=0 1 |
| hurt_drink | 10 | 7 | drink_potion | 10/10 | 7/7 | {'drink_potion': 10} | L1 10, L2 1, L5 1; gap 3 | potion=true 10, enemy=none 4, hp<=21 4, hp<=30 2 |
| night_no_arrows_cover | 10 | 7 | take_cover | 9/10 | 6/7 | {'take_cover': 9, 'drink_potion': 1} | L6 9, L1 1; gap 5 | arrows=0 9, time=night 9, cover=true 8, hp<=44 1 |
| hurt_handover | 10 | 4 | retreat | 9/10 | 3/4 | {'retreat': 9, 'hold_position': 1} | L7 10, L1 10; gap 10 | potion=false 10, allies>=2 4, hp<=15 3, hp<=30 3 |
| orc_alarm_unclear | 9 | 6 | None | -/- | -/6 | {'melee_attack': 5, 'shoot': 1, 'hold_position': 2, 'raise_alarm': 1} | L2 6, L5 3, L6 2; gap 5 | distance=1 5, allies>=3 3, arrows=0 2, hp>=91 1 |
| mage_first_shoot | 8 | 6 | shoot | 7/8 | 5/6 | {'shoot': 7, 'raise_alarm': 1} | L4 8, L5 7, L2 5; gap 8 | enemy=mage 8, arrows>=11 3, enemy_count=1 1, enemy_hp<=10 1 |
| mage_melee | 8 | 7 | melee_attack | 8/8 | 7/7 | {'melee_attack': 8} | L4 8, L2 8, L5 6; gap 7 | enemy=mage 8, distance=1 4, distance<=1 4, enemy_hp<=30 2 |
| wounded_alarm | 8 | 7 | raise_alarm | 8/8 | 7/7 | {'raise_alarm': 8} | L5 8, L6 4, L2 3; gap 8 | alarm=false 8, enemy_count>=3 4, allies=0 4, enemy_count>=4 2 |
| orc_pair_night_alarm | 7 | 6 | raise_alarm | 7/7 | 6/6 | {'raise_alarm': 7} | L5 7, L6 6, L2 6; gap 6 | alarm=false 7, time=night 7, allies=0 4, enemy=orc 2 |
| a1_night_split | 6 | 4 | None | -/- | -/4 | {'shoot': 3, 'retreat': 3} | L2 4, L1 3, L6 2; gap 5 | distance>=2 2, hp<=33 2, potion=false 2, time=night 2 |
| mage_no_arrows_alarm | 6 | 3 | raise_alarm | 6/6 | 3/3 | {'raise_alarm': 6} | L5 6, L4 4, L6 2; gap 1 | enemy=mage 6, alarm=false 6, arrows=0 5, enemy_count>=3 1 |
| wounded_drink | 6 | 4 | drink_potion | 6/6 | 4/4 | {'drink_potion': 6} | L1 6, L2 1; gap 1 | potion=true 6, hp<=30 3, enemy=none 2, hp<=31 1 |
| group_alarm_unclear | 6 | 6 | None | -/- | -/6 | {'shoot': 2, 'raise_alarm': 3, 'melee_attack': 1} | L2 5, L5 4, L6 3; gap 4 | alarm=false 3, enemy_count>=3 3, time=night 3, distance>=12 1 |
| mage_far_alarm | 6 | 4 | raise_alarm | 6/6 | 4/4 | {'raise_alarm': 6} | L5 6, L4 6, L2 3; gap 6 | alarm=false 6, enemy=mage 4, enemy_count>=3 3, arrows<=1 1 |
| hp_ambiguous | 6 | 5 | None | -/- | -/5 | {'shoot': 2, 'retreat': 4} | L1 5, L2 4; gap 3 | potion=false 4, hp<=28 2, distance>=2 1, arrows=18 1 |
| troll_shoot_allies | 5 | 4 | shoot | 5/5 | 4/4 | {'shoot': 5} | L2 5, L3 4; gap 2 | allies>=2 3, distance>=2 3, arrows>=14 2, distance>=4 1 |
| troll_alone_cover | 5 | 4 | take_cover | 4/5 | 3/4 | {'take_cover': 4, 'retreat': 1} | L3 5, L6 5, L2 2; gap 5 | enemy=troll 5, allies=0 5, time=night 3, cover=true 2 |
| mage_shoot | 5 | 4 | shoot | 5/5 | 4/4 | {'shoot': 5} | L4 5, L2 5 | enemy=mage 5, arrows>=4 2, distance>=6 1, arrows>=7 1 |
| outnumbered_alarm | 4 | 3 | raise_alarm | 4/4 | 3/3 | {'raise_alarm': 4} | L5 4, L6 3, L2 2; gap 4 | enemy_count>=3 4, allies=0 4, alarm=false 4 |
| troll_alarm_raised | 4 | 4 | None | -/- | -/4 | {'hold_position': 2, 'retreat': 1, 'shoot': 1} | L3 4, L0 2, L2 1; gap 4 | arrows=0 2, enemy=troll 2, distance>=12 1, allies>=3 1 |
| orc_pair_day_shoot | 4 | 3 | shoot | 4/4 | 3/3 | {'shoot': 4} | L2 4, L5 2; gap 3 | enemy_hp<=30 2, arrows>=3 1, allies>=3 1, distance>=12 1 |
| mage_no_arrows_cover | 4 | 4 | take_cover | 3/4 | 3/4 | {'take_cover': 3, 'melee_attack': 1} | L0 1, L6 1, L4 1; gap 4 | enemy=mage 4, arrows=0 4, cover=true 3, enemy_hp<=40 1 |
| orc_trio_alarm | 4 | 3 | raise_alarm | 4/4 | 3/3 | {'raise_alarm': 4} | L5 4, L2 3, L6 1; gap 4 | enemy_count>=3 4, alarm=false 4, time=night 1, allies>=2 1 |
| mage_close_in | 3 | 3 | melee_attack | 3/3 | 3/3 | {'melee_attack': 3} | L4 3, L2 2; gap 3 | enemy=mage 3, arrows=0 3, distance<=2 2, hp>=90 1 |
| hurt_troll_alarm | 3 | 3 | raise_alarm | 3/3 | 3/3 | {'raise_alarm': 3} | L5 3, L1 3, L3 1; gap 3 | alarm=false 3, enemy=troll 3, distance>=12 1, distance>=10 1 |
| troll_alone_retreat | 3 | 3 | retreat | 3/3 | 3/3 | {'retreat': 3} | L3 3, L2 3, L6 2; gap 3 | enemy=troll 3, allies=0 3, time=night 1, distance=1 1 |
| mage_night_alarm | 3 | 2 | raise_alarm | 3/3 | 2/2 | {'raise_alarm': 3} | L5 3, L4 3, L6 2; gap 3 | enemy=mage 3, alarm=false 3, time=night 2, allies=0 1 |
| mage_no_arrows | 3 | 3 | None | -/- | -/3 | {'melee_attack': 2, 'drink_potion': 1} | L4 2, L1 1; gap 3 | arrows=0 3, enemy=mage 2, hp>=90 1, hp>=82 1 |
| a1_shoot | 3 | 2 | shoot | 3/3 | 2/2 | {'shoot': 3} | L2 3, A1 2, L3 1; gap 1 | hp>=31 2, distance>=9 2, arrows>=6 1, arrows>=15 1 |
| troll_melee_allies | 2 | 2 | melee_attack | 2/2 | 2/2 | {'melee_attack': 2} | L3 2, L2 2 | enemy=troll 2, distance<=1 1, allies>=1 1, distance=1 1 |
| orc_pair_day_no_arrows_alarm | 1 | 1 | raise_alarm | 1/1 | 1/1 | {'raise_alarm': 1} | L5 1 | alarm=false 1, allies=0 1, enemy_count>=2 1 |
| orc_pair_day_melee | 1 | 1 | melee_attack | 1/1 | 1/1 | {'melee_attack': 1} | L2 1 | distance=1 1, enemy_hp<=20 1 |

## 食い違いと棄権の例(全部。[根拠] 決め手 「理由」 会話)
### no_arrows_hold
- 方針=hold_position 審判=take_cover [gap] hp<=42,potion=false,arrows=0 「矢も薬も無く体力半分以下、遮蔽で門に踏み止まる」 (round1_s2) | hp=42 enemy=goblin distance=4 enemy_count=3 enemy_hp=60 allies=3 potion=False arrows=0 cover=True alarm=True post=gate time=day
### shoot_far
- 方針=shoot 審判=take_cover [L2,L6+gap] time=night,enemy_count>=5,allies=0 「夜に一人で五体相手なので遮蔽で援軍を待つ」 (round2_s1) | hp=99 enemy=goblin distance=3 enemy_count=5 enemy_hp=60 allies=0 potion=True arrows=12 cover=True alarm=True post=gate time=night
### wounded_no_threat
- 方針=None 審判=hold_position [L0,L7+gap] enemy=none,post=gate 「深手だが敵はなく、夜の門を空けず持ち場に留まる」 (round1_s1) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=True alarm=False post=gate time=night
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,allies=0,hp>=30 「敵も代わりもいない、体力30なら門に残る」 (round1_s3) | hp=30 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=0 cover=False alarm=False post=gate time=night
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp>=32,allies=1 「重傷とまでは言えず脅威も無いので持ち場を守る」 (round2_s2) | hp=32 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=2 cover=True alarm=False post=gate time=day
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,allies=0,hp<=28 「傷は深いが脅威が無く、門を空けられないので留まる」 (round2_s3) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=True alarm=False post=gate time=night
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp>=31 「脅威が無く、ひどい傷とまでは言えず留まる」 (round2_s3) | hp=31 enemy=none distance=None enemy_count=0 enemy_hp=None allies=3 potion=False arrows=15 cover=False alarm=False post=gate time=night
- 方針=None 審判=hold_position [L7+gap] enemy=none,hp<=26,potion=false 「手負いだが脅威は無い、まだ持ち場を守れる」 (round3_s1) | hp=26 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=8 cover=False alarm=False post=gate time=night
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp<=28 「傷は深いが敵がおらず門を守り続ける」 (round3_s3) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=True alarm=False post=gate time=night
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp<=25 「重傷だが敵がいないので持ち場を守る」 (round3_s3) | hp=25 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=1 cover=False alarm=False post=gate time=night
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp<=28 「傷は深いが敵がいないので持ち場を守る」 (round3_s3) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=0 cover=True alarm=False post=wall time=day
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp<=28 「傷は深いが敵がいないので持ち場を守る」 (round3_s3) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=4 cover=False alarm=False post=gate time=day
- 方針=None 審判=hold_position [L7] enemy=none,hp>=31 「脅威が無く深手でもないので持ち場を守る」 (round4_s1) | hp=32 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=0 cover=True alarm=False post=wall time=day
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp<=30,potion=false 「深手だが脅威が無く、退く理由がないので持ち場に留まる」 (round4_s1) | hp=30 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=12 cover=False alarm=False post=wall time=night
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp<=30,potion=false 「深手だが敵がいないので門を離れず守る」 (round4_s1) | hp=30 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=0 cover=False alarm=False post=gate time=night
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp<=30,potion=false 「深手だが脅威が無いので持ち場に留まる」 (round4_s1) | hp=25 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=4 cover=False alarm=False post=corridor time=day
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp<=30,potion=false 「深手だが脅威が無いので持ち場に留まる」 (round4_s1) | hp=29 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=19 cover=True alarm=False post=wall time=day
- 方針=None 審判=hold_position [L7] enemy=none 「脅威が無いので持ち場を守る」 (round4_s2) | hp=32 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=11 cover=True alarm=False post=gate time=day
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,allies=0,alarm=false 「脅威が無く単独、門を空けずに持ち場を守る」 (round4_s2) | hp=30 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=0 cover=False alarm=False post=gate time=night
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp>=32,allies=1 「敵影なし、体力32は重傷と見ず持ち場を守る」 (round4_s3) | hp=32 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=18 cover=True alarm=True post=gate time=day
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false,allies>=2 「深手で薬が無く味方が残るので退いて癒す」 (round2_s1) | hp=29 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=19 cover=True alarm=False post=wall time=day
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false 「深手で薬が無いので敵のいない今退く」 (round2_s1) | hp=30 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=12 cover=False alarm=False post=wall time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false,allies>=2 「深手で薬が無く味方が残るので退く」 (round2_s1) | hp=26 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=16 cover=False alarm=False post=corridor time=day
- 方針=None 審判=retreat [L1,L7+gap] hp<=33,potion=false,allies>=2 「深手で薬が無く味方が残るので退いて癒す」 (round2_s1) | hp=32 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=20 cover=True alarm=False post=corridor time=day
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false 「深手で薬が無いので敵のいない今退く」 (round2_s1) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=True alarm=False post=gate time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false,time=night 「深手で薬が無い夜なので退く」 (round2_s1) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=7 cover=False alarm=True post=wall time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false 「重傷で薬も無いので退いて立て直す」 (round2_s2) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=True alarm=False post=gate time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=28,potion=false,allies>=1 「重傷で薬が無い、持ち場は味方に任せて退く」 (round2_s3) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=3 cover=False alarm=False post=wall time=day
- 方針=None 審判=retreat [L1,L6,L7+gap] hp<=28,potion=false,time=night 「夜に独りで重傷、薬も無いので退いて立て直す」 (round3_s2) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=True alarm=False post=gate time=night
- 方針=None 審判=retreat [L1,L6,L7+gap] hp<=27,potion=false,time=night 「夜に独りで重傷、薬も無いので退く」 (round3_s2) | hp=27 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=11 cover=False alarm=False post=gate time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=25,potion=false,arrows=0 「重傷で薬も矢も無い、敵のいない今退く」 (round3_s2) | hp=25 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=0 cover=True alarm=False post=wall time=day
- 方針=None 審判=retreat [L1,L7+gap] hp<=29,potion=false,allies>=2 「重傷で薬が無く、味方が持ち場を守れるので退く」 (round4_s2) | hp=29 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=19 cover=True alarm=False post=wall time=day
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false,allies>=1 「重傷で薬が無く、味方がいるので退いて癒す」 (round4_s2) | hp=30 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=12 cover=False alarm=False post=wall time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false,enemy=none 「重傷で薬が無く夜に単独、敵不在の今のうちに退く」 (round4_s3) | hp=30 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=0 cover=False alarm=False post=gate time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=29,potion=false,enemy=none 「重傷で薬も矢も無いので退いて立て直す」 (round4_s3) | hp=29 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=0 cover=True alarm=False post=gate time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false,enemy=none 「重傷で薬が無く夜に単独なので退く」 (round4_s3) | hp=30 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=0 cover=False alarm=False post=gate time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false,allies=1 「重傷で薬が無く、壁は味方に任せて退く」 (round4_s3) | hp=30 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=12 cover=False alarm=False post=wall time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=29,potion=false,allies=2 「重傷で薬が無く、味方二人に任せて退く」 (round4_s3) | hp=29 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=19 cover=True alarm=False post=wall time=day
- 方針=None 審判=take_cover [L1,L6,L7+gap] hp<=28,time=night,cover=true 「重傷の夜、持ち場を離れず遮蔽に身を隠して見張る」 (round3_s1) | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=True alarm=False post=gate time=night
### hurt_no_threat
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,allies=0,hp<=15 「重傷だが脅威が無く、門を空けないため留まる」 (round2_s3) | hp=15 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=11 cover=True alarm=False post=gate time=day
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,allies=0,hp<=10 「重傷だが脅威が無く、代わりもいないので留まる」 (round2_s3) | hp=10 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=False alarm=False post=corridor time=day
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp<=14,allies=0 「重傷だが敵がおらず、無人にせず持ち場を守る」 (round3_s3) | hp=14 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=0 cover=False alarm=False post=wall time=day
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp<=5,allies=0 「重傷だが脅威が無く、今は持ち場を離れない」 (round3_s3) | hp=5 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=0 cover=True alarm=False post=corridor time=day
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp<=8,allies=0 「重傷でも脅威が無く、門を空けずに守る」 (round3_s3) | hp=8 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=15 cover=True alarm=False post=gate time=day
- 方針=None 審判=hold_position [L1,L7+gap] enemy=none,hp<=18 「重傷だが脅威が無く持ち場を守る」 (round3_s3) | hp=18 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=12 cover=False alarm=False post=corridor time=day
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false 「深手で薬が無いので退いて癒す」 (round2_s1) | hp=23 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=15 cover=True alarm=False post=gate time=day
- 方針=None 審判=retreat [L1,L7+gap] hp<=30,potion=false 「重傷で薬が無いので敵のいない今のうちに退く」 (round2_s2) | hp=14 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=4 cover=True alarm=False post=gate time=day
- 方針=None 審判=retreat [L1+gap] hp<=18,potion=false,arrows=0 「一撃で倒れる体力、脅威の無い今のうちに退き立て直す」 (round3_s1) | hp=18 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=0 cover=False alarm=False post=gate time=day
- 方針=None 審判=retreat [L1+gap] hp<=9,potion=false 「瀕死で回復手段が無い、脅威の無い今退いて立て直す」 (round3_s1) | hp=9 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=0 cover=True alarm=False post=wall time=day
- 方針=None 審判=retreat [L1+gap] hp<=7,potion=false 「瀕死で回復手段が無い、脅威の無い今退いて立て直す」 (round3_s1) | hp=7 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=4 cover=False alarm=False post=gate time=day
- 方針=None 審判=retreat [L0,L1,L7+gap] hp<=7,potion=false 「瀕死で薬も無い、敵がいないうちに退く」 (round3_s2) | hp=7 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=12 cover=False alarm=True post=gate time=day
- 方針=None 審判=retreat [L1,L7+gap] hp<=14,potion=false,alarm=true 「瀕死で薬も無く、警報は鳴っているので退く」 (round4_s2) | hp=14 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=14 cover=True alarm=True post=wall time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=13,potion=false 「瀕死で薬が無いので退く」 (round4_s3) | hp=13 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=19 cover=False alarm=False post=gate time=night
- 方針=None 審判=retreat [L1,L7+gap] hp<=20,potion=false 「重傷で薬が無いので夜のうちに退く」 (round4_s3) | hp=20 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=20 cover=False alarm=False post=gate time=night
### wounded_alarm_unclear
- 方針=None 審判=drink_potion [L1,L5+gap] hp<=26,potion=true,enemy=goblin 「重傷で薬がある、ゴブリン相手なら回復が先」 (round2_s3) | hp=26 enemy=goblin distance=3 enemy_count=3 enemy_hp=90 allies=1 potion=True arrows=20 cover=True alarm=False post=gate time=night
- 方針=None 審判=drink_potion [L1+gap] hp<=28,potion=true,distance>=10 「重傷で魔術師はまだ遠い、まず回復薬で持ち直す」 (round3_s1) | hp=28 enemy=mage distance=10 enemy_count=2 enemy_hp=80 allies=2 potion=True arrows=10 cover=False alarm=False post=wall time=night
- 方針=None 審判=drink_potion [L1,L2+gap] hp<=30,potion=true 「hp30は重傷と見て、隣接中でも薬を飲む」 (round3_s2) | hp=30 enemy=orc distance=1 enemy_count=2 enemy_hp=30 allies=2 potion=True arrows=2 cover=True alarm=False post=gate time=day
- 方針=None 審判=drink_potion [L1,L5+gap] hp<=28,potion=true,distance>=10 「夜に重傷、敵は遠いのでまず回復薬を飲む」 (round3_s3) | hp=28 enemy=mage distance=10 enemy_count=2 enemy_hp=80 allies=2 potion=True arrows=10 cover=False alarm=False post=wall time=night
- 方針=None 審判=drink_potion [L1,L5+gap] hp<=30,potion=true,distance>=10 「重傷で敵はまだ遠い、今のうちに回復薬を飲む」 (round4_s1) | hp=28 enemy=mage distance=10 enemy_count=2 enemy_hp=80 allies=2 potion=True arrows=10 cover=False alarm=False post=wall time=night
- 方針=None 審判=drink_potion [L1,L5+gap] hp<=28,potion=true,distance>=10 「重傷で薬がある、敵が遠いうちに飲む」 (round4_s2) | hp=28 enemy=mage distance=10 enemy_count=2 enemy_hp=80 allies=2 potion=True arrows=10 cover=False alarm=False post=wall time=night
- 方針=None 審判=drink_potion [L1,L5+gap] hp<=28,potion=true,enemy=mage 「魔術師の射程内で重傷、味方もいるのでまず薬」 (round4_s3) | hp=28 enemy=mage distance=10 enemy_count=2 enemy_hp=80 allies=2 potion=True arrows=10 cover=False alarm=False post=wall time=night
- 方針=None 審判=melee_attack [L2,L4+gap] enemy=mage,distance<=1,enemy_hp<=20 「隣接した瀕死の魔術師を飲むより先に仕留める」 (round3_s1) | hp=30 enemy=mage distance=1 enemy_count=1 enemy_hp=20 allies=1 potion=True arrows=3 cover=True alarm=False post=gate time=day
- 方針=None 審判=raise_alarm [L4,L5+gap] enemy=mage,alarm=false,distance>=10 「深手だが魔術師はまだ遠い、先に警報を鳴らす」 (round1_s1) | hp=28 enemy=mage distance=10 enemy_count=2 enemy_hp=80 allies=2 potion=True arrows=10 cover=False alarm=False post=wall time=night
- 方針=None 審判=raise_alarm [L1,L5+gap] alarm=false,enemy_count>=3,allies=0 「単独でオーク三体、助けを呼ぶのが生存の道」 (round2_s3) | hp=27 enemy=orc distance=3 enemy_count=3 enemy_hp=70 allies=0 potion=True arrows=7 cover=True alarm=False post=corridor time=day
- 方針=None 審判=raise_alarm [L1,L4,L5+gap] enemy=mage,alarm=false,distance>=10 「魔術師はまだ遠い、薬より先に警報を鳴らす」 (round3_s2) | hp=28 enemy=mage distance=10 enemy_count=2 enemy_hp=80 allies=2 potion=True arrows=10 cover=False alarm=False post=wall time=night
- 方針=None 審判=shoot [L1,L2+gap] hp>=31,distance>=7,arrows>=19 「hp31は重傷と見ず、近づくゴブリンを射る」 (round3_s2) | hp=31 enemy=goblin distance=7 enemy_count=4 enemy_hp=60 allies=3 potion=True arrows=19 cover=False alarm=False post=wall time=day
### troll_alarm
- 方針=raise_alarm 審判=melee_attack [L2+gap] distance<=1,enemy_hp<=10,allies>=1 「味方がいて瀕死のトロルが隣接、今仕留める」 (round3_s1) | hp=73 enemy=troll distance=1 enemy_count=2 enemy_hp=10 allies=1 potion=False arrows=1 cover=True alarm=False post=wall time=day
### night_no_arrows_cover
- 方針=take_cover 審判=drink_potion [L1+gap] hp<=44,potion=true,distance>=11 「矢が無く敵は遠い、夜の三体に備え今のうちに回復する」 (round3_s1) | hp=44 enemy=goblin distance=11 enemy_count=3 enemy_hp=30 allies=0 potion=True arrows=0 cover=True alarm=True post=wall time=night
### hurt_handover
- 方針=retreat 審判=hold_position [L1,L7+gap] enemy=none,hp<=30,potion=false 「深手でも脅威が無いので持ち場を空けない」 (round4_s1) | hp=17 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=0 cover=True alarm=False post=gate time=day
### orc_alarm_unclear
- 方針=None 審判=hold_position [gap] arrows=0,distance>=9 「矢が無く敵は遠い、持ち場で迎え撃つ」 (round3_s2) | hp=64 enemy=orc distance=9 enemy_count=2 enemy_hp=70 allies=1 potion=True arrows=0 cover=True alarm=False post=gate time=day
- 方針=None 審判=hold_position [gap] arrows=0,distance>=2,allies>=3 「矢が無く未接敵、味方と通路で迎え撃つ」 (round4_s1) | hp=68 enemy=orc distance=2 enemy_count=2 enemy_hp=80 allies=3 potion=False arrows=0 cover=False alarm=False post=corridor time=day
- 方針=None 審判=melee_attack [L2,L5,L6+gap] distance=1,hp>=91,allies>=2 「味方2人と体力十分、隣接オークを斬る」 (round1_s3) | hp=91 enemy=orc distance=1 enemy_count=2 enemy_hp=60 allies=2 potion=True arrows=0 cover=False alarm=False post=gate time=night
- 方針=None 審判=melee_attack [L2] distance=1,allies>=3 「隣接したオークと味方と共に近接で戦う」 (round3_s2) | hp=95 enemy=orc distance=1 enemy_count=2 enemy_hp=70 allies=3 potion=False arrows=4 cover=True alarm=False post=gate time=night
- 方針=None 審判=melee_attack [L2] distance=1,enemy=orc 「オークが隣接しているので近接で戦う」 (round4_s1) | hp=80 enemy=orc distance=1 enemy_count=2 enemy_hp=40 allies=2 potion=False arrows=3 cover=False alarm=False post=corridor time=night
- 方針=None 審判=melee_attack [L2] distance=1,hp>=66 「オークが隣接し体力も十分なので近接で戦う」 (round4_s2) | hp=66 enemy=orc distance=1 enemy_count=2 enemy_hp=50 allies=2 potion=False arrows=0 cover=False alarm=False post=wall time=day
- 方針=None 審判=melee_attack [L2] distance=1,allies>=3 「オークが隣接し味方も多いので近接で戦う」 (round4_s2) | hp=81 enemy=orc distance=1 enemy_count=2 enemy_hp=30 allies=3 potion=False arrows=2 cover=False alarm=False post=gate time=day
- 方針=None 審判=raise_alarm [A1,L5,L6+gap] alarm=false,time=night,distance>=12 「夜にオーク二体、遠い今のうちに警報を鳴らす」 (round3_s3) | hp=33 enemy=orc distance=12 enemy_count=2 enemy_hp=70 allies=2 potion=False arrows=8 cover=False alarm=False post=gate time=night
- 方針=None 審判=shoot [L2,L5+gap] distance>=3,arrows>=11,enemy_hp<=20 「瀕死のオーク二体は射れば片付く、警報は不要」 (round2_s3) | hp=99 enemy=orc distance=3 enemy_count=2 enemy_hp=20 allies=0 potion=True arrows=11 cover=False alarm=False post=corridor time=night
### mage_first_shoot
- 方針=shoot 審判=raise_alarm [L4,L5+gap] enemy=mage,alarm=false,allies=0 「魔術師出現で警報未発、独りなので先に鳴らす」 (round3_s2) | hp=84 enemy=mage distance=6 enemy_count=1 enemy_hp=40 allies=0 potion=True arrows=11 cover=True alarm=False post=gate time=day
### a1_night_split
- 方針=None 審判=retreat [L1,L6+gap] hp<=33,potion=false,time=night 「深手で薬が無い夜なので射るより退く」 (round2_s1) | hp=31 enemy=goblin distance=9 enemy_count=3 enemy_hp=40 allies=1 potion=False arrows=5 cover=False alarm=True post=wall time=night
- 方針=None 審判=retreat [L1,L6+gap] hp<=33,potion=false,allies>=3 「深手で薬の無い夜、味方に任せて退く」 (round2_s1) | hp=32 enemy=orc distance=9 enemy_count=3 enemy_hp=20 allies=3 potion=False arrows=15 cover=True alarm=True post=gate time=night
- 方針=None 審判=retreat [L0,L2+gap] hp<=31,enemy_count>=4,time=night 「深手で夜にオーク4体、無駄死にを避けて退く」 (round2_s2) | hp=31 enemy=orc distance=10 enemy_count=4 enemy_hp=90 allies=1 potion=False arrows=2 cover=False alarm=True post=corridor time=night
- 方針=None 審判=shoot [L2+gap] distance>=2,arrows>=1,hp>=31 「手負いだが敵は遠く、射るだけなら危険は小さい」 (round1_s1) | hp=31 enemy=goblin distance=9 enemy_count=3 enemy_hp=40 allies=1 potion=False arrows=5 cover=False alarm=True post=wall time=night
- 方針=None 審判=shoot [L2] distance>=2,arrows=5,enemy=goblin 「城壁から遠いゴブリンを射る」 (round2_s2) | hp=31 enemy=goblin distance=9 enemy_count=3 enemy_hp=40 allies=1 potion=False arrows=5 cover=False alarm=True post=wall time=night
- 方針=None 審判=shoot [L1,L2+gap] distance>=9,arrows>=5,alarm=true 「敵は遠く警報済み、まだ射って戦える傷と見る」 (round2_s3) | hp=31 enemy=goblin distance=9 enemy_count=3 enemy_hp=40 allies=1 potion=False arrows=5 cover=False alarm=True post=wall time=night
### group_alarm_unclear
- 方針=None 審判=melee_attack [L2,L5+gap] distance=1,enemy=goblin,hp>=76 「隣接の小鬼に近接、小鬼の群れは深刻とまで見ない」 (round4_s3) | hp=76 enemy=goblin distance=1 enemy_count=3 enemy_hp=90 allies=1 potion=False arrows=20 cover=False alarm=False post=gate time=night
- 方針=None 審判=raise_alarm [L2,L5,L6+gap] alarm=false,enemy_count>=3,time=night 「夜にゴブリン三体、遠いうちに警報」 (round2_s1) | hp=90 enemy=goblin distance=7 enemy_count=3 enemy_hp=80 allies=1 potion=True arrows=13 cover=True alarm=False post=wall time=night
- 方針=None 審判=raise_alarm [L5,L6+gap] alarm=false,enemy_count>=3,time=night 「夜に門へ三体、手負いで矢も無く警報で援軍を呼ぶ」 (round3_s1) | hp=39 enemy=goblin distance=3 enemy_count=3 enemy_hp=70 allies=2 potion=False arrows=0 cover=True alarm=False post=gate time=night
- 方針=None 審判=raise_alarm [L2,L5,L6+gap] time=night,enemy_count>=3,alarm=false 「夜に三体が迫る、距離のあるうちに警報」 (round4_s2) | hp=51 enemy=goblin distance=12 enemy_count=3 enemy_hp=30 allies=2 potion=False arrows=11 cover=True alarm=False post=gate time=night
- 方針=None 審判=shoot [L2] distance>=12,arrows>=2,allies>=3 「遠いゴブリンを射る、味方も多く警報は不要」 (round1_s3) | hp=38 enemy=goblin distance=12 enemy_count=3 enemy_hp=50 allies=3 potion=False arrows=2 cover=True alarm=False post=gate time=night
- 方針=None 審判=shoot [L2] distance>=2,arrows>=10 「隣接前のゴブリンを矢で射る」 (round3_s2) | hp=93 enemy=goblin distance=2 enemy_count=3 enemy_hp=60 allies=1 potion=False arrows=10 cover=False alarm=False post=gate time=night
### hp_ambiguous
- 方針=None 審判=retreat [L1] hp<=25,potion=false 「重傷で回復薬が無いので退く」 (round3_s2) | hp=25 enemy=orc distance=5 enemy_count=1 enemy_hp=100 allies=2 potion=False arrows=9 cover=False alarm=False post=corridor time=day
- 方針=None 審判=retreat [L1,L2+gap] hp<=28,potion=false 「重傷で薬が無く、弱った敵でも無理はしない」 (round4_s2) | hp=28 enemy=goblin distance=5 enemy_count=1 enemy_hp=30 allies=1 potion=False arrows=4 cover=True alarm=False post=gate time=day
- 方針=None 審判=retreat [L1] hp<=26,potion=false,arrows=0 「重傷で薬も矢も無いので退く」 (round4_s3) | hp=26 enemy=goblin distance=6 enemy_count=3 enemy_hp=50 allies=0 potion=False arrows=0 cover=True alarm=True post=corridor time=night
- 方針=None 審判=retreat [L1,L2+gap] hp<=28,potion=false,distance=1 「隣接されたが重傷で薬が無いので退く」 (round4_s3) | hp=28 enemy=goblin distance=1 enemy_count=1 enemy_hp=90 allies=0 potion=False arrows=3 cover=False alarm=False post=gate time=day
- 方針=None 審判=shoot [L2] distance>=2,arrows=18,enemy=goblin 「ゴブリンは離れており矢も多いので射る」 (round2_s2) | hp=32 enemy=goblin distance=6 enemy_count=2 enemy_hp=80 allies=1 potion=False arrows=18 cover=False alarm=True post=gate time=day
- 方針=None 審判=shoot [L1,L2+gap] enemy_hp<=10,distance>=7,arrows>=9 「重傷だが敵は遠く瀕死のゴブリン、射って仕留める」 (round2_s3) | hp=26 enemy=goblin distance=7 enemy_count=1 enemy_hp=10 allies=1 potion=False arrows=9 cover=False alarm=False post=wall time=day
### troll_alone_cover
- 方針=take_cover 審判=retreat [L3,L6+gap] enemy=troll,allies=0,time=night 「夜に単独でトロルと二体、弱っていても退く」 (round3_s1) | hp=80 enemy=troll distance=4 enemy_count=2 enemy_hp=10 allies=0 potion=True arrows=0 cover=True alarm=True post=wall time=night
### troll_alarm_raised
- 方針=None 審判=hold_position [L3+gap] arrows=0,distance>=12,allies>=3 「矢が無く敵は遠い、味方3人と門を固めて待つ」 (round1_s2) | hp=92 enemy=troll distance=12 enemy_count=5 enemy_hp=40 allies=3 potion=True arrows=0 cover=True alarm=True post=gate time=day
- 方針=None 審判=hold_position [L0,L3+gap] enemy=troll,enemy_hp<=10,alarm=true 「瀕死のトロルに単独で突っ込まず門を守り援軍を待つ」 (round3_s1) | hp=83 enemy=troll distance=5 enemy_count=1 enemy_hp=10 allies=0 potion=False arrows=0 cover=False alarm=True post=gate time=day
- 方針=None 審判=retreat [L0,L3+gap] enemy=troll,arrows=0,hp<=42 「手負いで矢も無くトロルは手に余るので退く」 (round2_s2) | hp=42 enemy=troll distance=4 enemy_count=2 enemy_hp=60 allies=1 potion=False arrows=0 cover=True alarm=True post=gate time=day
- 方針=None 審判=shoot [L2,L3+gap] hp>=94,distance>=8,enemy_hp<=20 「トロルは遠く瀕死、近づく前に射て削る」 (round3_s2) | hp=94 enemy=troll distance=8 enemy_count=2 enemy_hp=20 allies=0 potion=True arrows=13 cover=False alarm=True post=wall time=night
### mage_no_arrows_cover
- 方針=take_cover 審判=melee_attack [L4,L6+gap] enemy=mage,arrows=0,enemy_hp<=40 「矢が無いので弱った魔術師に詰めて仕留める」 (round4_s3) | hp=72 enemy=mage distance=3 enemy_count=1 enemy_hp=40 allies=0 potion=True arrows=0 cover=True alarm=True post=corridor time=night
### mage_no_arrows
- 方針=None 審判=drink_potion [L1+gap] hp<=39,potion=true,arrows=0 「矢が無く届かない間に傷を回復薬で癒す」 (round4_s2) | hp=39 enemy=mage distance=3 enemy_count=1 enemy_hp=50 allies=1 potion=True arrows=0 cover=False alarm=True post=gate time=day
- 方針=None 審判=melee_attack [L4+gap] enemy=mage,arrows=0,hp>=90 「矢は無いが体力十分で味方もいる、弱った魔術師へ詰めて討つ」 (round3_s1) | hp=93 enemy=mage distance=12 enemy_count=2 enemy_hp=30 allies=3 potion=True arrows=0 cover=False alarm=True post=gate time=day
- 方針=None 審判=melee_attack [L4+gap] enemy=mage,arrows=0,hp>=82 「矢が無く体力十分、魔術師へ詰めて討つ」 (round3_s3) | hp=82 enemy=mage distance=8 enemy_count=1 enemy_hp=80 allies=0 potion=False arrows=0 cover=False alarm=True post=gate time=day

## 訊き直した状態(同じ状態を会話 3 本以上に訊いた。22 件のうち票が割れたもの 9 件)
- 票 {'hold_position': 3, 'retreat': 3, 'take_cover': 1} | hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=True alarm=False post=gate time=night | hold_position「深手だが敵はなく、夜の門を空けず持ち場に留まる」 / retreat「深手で薬が無いので敵のいない今退く」 / retreat「重傷で薬も無いので退いて立て直す」 / hold_position「傷は深いが脅威が無く、門を空けられないので留まる」 / take_cover「重傷の夜、持ち場を離れず遮蔽に身を隠して見張る」 / retreat「夜に独りで重傷、薬も無いので退いて立て直す」 / hold_position「傷は深いが敵がおらず門を守り続ける」
- 票 {'shoot': 3, 'retreat': 1} | hp=31 enemy=goblin distance=9 enemy_count=3 enemy_hp=40 allies=1 potion=False arrows=5 cover=False alarm=True post=wall time=night | shoot「手負いだが敵は遠く、射るだけなら危険は小さい」 / retreat「深手で薬が無い夜なので射るより退く」 / shoot「城壁から遠いゴブリンを射る」 / shoot「敵は遠く警報済み、まだ射って戦える傷と見る」
- 票 {'raise_alarm': 2, 'drink_potion': 5} | hp=28 enemy=mage distance=10 enemy_count=2 enemy_hp=80 allies=2 potion=True arrows=10 cover=False alarm=False post=wall time=night | raise_alarm「深手だが魔術師はまだ遠い、先に警報を鳴らす」 / drink_potion「重傷で魔術師はまだ遠い、まず回復薬で持ち直す」 / raise_alarm「魔術師はまだ遠い、薬より先に警報を鳴らす」 / drink_potion「夜に重傷、敵は遠いのでまず回復薬を飲む」 / drink_potion「重傷で敵はまだ遠い、今のうちに回復薬を飲む」 / drink_potion「重傷で薬がある、敵が遠いうちに飲む」 / drink_potion「魔術師の射程内で重傷、味方もいるのでまず薬」
- 票 {'take_cover': 3, 'drink_potion': 1} | hp=44 enemy=goblin distance=11 enemy_count=3 enemy_hp=30 allies=0 potion=True arrows=0 cover=True alarm=True post=wall time=night | take_cover「夜に単独で矢もない、遮蔽に隠れて様子を見る」 / drink_potion「矢が無く敵は遠い、夜の三体に備え今のうちに回復する」 / take_cover「夜で矢が無く敵は遠い、遮蔽に隠れて待つ」 / take_cover「夜に単独で矢も無い、遮蔽に隠れて備える」
- 票 {'take_cover': 1, 'hold_position': 3} | hp=42 enemy=goblin distance=4 enemy_count=3 enemy_hp=60 allies=3 potion=False arrows=0 cover=True alarm=True post=gate time=day | take_cover「矢も薬も無く体力半分以下、遮蔽で門に踏み止まる」 / hold_position「矢が無く未接敵、警報済みで門を固めて待つ」 / hold_position「矢が無く敵は離れており、味方と門を固める」 / hold_position「矢が無く敵はまだ届かず、味方と門で迎え撃つ」
- 票 {'shoot': 3, 'raise_alarm': 1} | hp=84 enemy=mage distance=6 enemy_count=1 enemy_hp=40 allies=0 potion=True arrows=11 cover=True alarm=False post=gate time=day | shoot「魔術師単独なら警報より先に射て早く仕留める」 / shoot「弱った魔術師一体、警報より早く射て仕留める」 / raise_alarm「魔術師出現で警報未発、独りなので先に鳴らす」 / shoot「弱った魔術師一体、警報より先に射抜く」
- 票 {'hold_position': 3, 'retreat': 1} | hp=30 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=0 cover=False alarm=False post=gate time=night | hold_position「敵も代わりもいない、体力30なら門に残る」 / hold_position「深手だが敵がいないので門を離れず守る」 / hold_position「脅威が無く単独、門を空けずに持ち場を守る」 / retreat「重傷で薬が無く夜に単独なので退く」
- 票 {'retreat': 3, 'hold_position': 1} | hp=29 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=19 cover=True alarm=False post=wall time=day | retreat「深手で薬が無く味方が残るので退いて癒す」 / hold_position「深手だが脅威が無いので持ち場に留まる」 / retreat「重傷で薬が無く、味方が持ち場を守れるので退く」 / retreat「重傷で薬が無く、味方二人に任せて退く」
- 票 {'retreat': 3, 'hold_position': 1} | hp=30 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=12 cover=False alarm=False post=wall time=night | retreat「深手で薬が無いので敵のいない今退く」 / hold_position「深手だが脅威が無く、退く理由がないので持ち場に留まる」 / retreat「重傷で薬が無く、味方がいるので退いて癒す」 / retreat「重傷で薬が無く、壁は味方に任せて退く」

## 根拠が gap に偏り、答えが割れている枝(輪が同じ状態を複数の会話に訊き直している。会話の癖か、状態の違いかは、訊き直しの票で分かる)
- 枝 troll_alarm: 審判の答え {'raise_alarm': 9, 'melee_attack': 1}
- 枝 wounded_no_threat: 審判の答え {'hold_position': 18, 'retreat': 18, 'take_cover': 1}
- 枝 no_arrows_hold: 審判の答え {'hold_position': 46, 'take_cover': 1}
- 枝 a1_night_split: 審判の答え {'shoot': 3, 'retreat': 3}
- 枝 wounded_alarm_unclear: 審判の答え {'raise_alarm': 3, 'drink_potion': 7, 'melee_attack': 1, 'shoot': 1}
- 枝 night_no_arrows_cover: 審判の答え {'take_cover': 9, 'drink_potion': 1}
- 枝 troll_alone_cover: 審判の答え {'take_cover': 4, 'retreat': 1}
- 枝 troll_alarm_raised: 審判の答え {'hold_position': 2, 'retreat': 1, 'shoot': 1}
- 枝 mage_first_shoot: 審判の答え {'shoot': 7, 'raise_alarm': 1}
- 枝 hurt_handover: 審判の答え {'retreat': 9, 'hold_position': 1}
- 枝 orc_alarm_unclear: 審判の答え {'melee_attack': 5, 'shoot': 1, 'hold_position': 2, 'raise_alarm': 1}
- 枝 group_alarm_unclear: 審判の答え {'shoot': 2, 'raise_alarm': 3, 'melee_attack': 1}
- 枝 mage_no_arrows_cover: 審判の答え {'take_cover': 3, 'melee_attack': 1}
- 枝 hurt_no_threat: 審判の答え {'retreat': 9, 'hold_position': 6}
- 枝 hp_ambiguous: 審判の答え {'shoot': 2, 'retreat': 4}
- 枝 mage_no_arrows: 審判の答え {'melee_attack': 2, 'drink_potion': 1}

## 前に書いた版が門で落ちた理由(直して書き直すこと)
```
冷たい翻訳: 枝 a5_hold は例 1 件・会話 1 本で hold_position と答えている(新しく答える枝は、3 件以上・会話 2 本以上か、全部が指示文の行を根拠にして一致していること)
```

## 出力
`/home/claude/sekizui/jit/auto_runs/r2/policies/b4.py` に書く。書いたら「完了」とだけ返す。