# 編集の依頼 — 走り r2、第 1 周

あなたは編集役だ。番兵 NPC の指示文には書かれていない所(穴)がある。審判(別の LLM)の会話が、そこでどう判断したかを集めた。
会話の多数が揃った穴ごとに、指示文に足す追補を一文ずつ書く。読んでよいのはこの依頼書だけ。

## いまの指示文
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

## 書き方の約束
- 一つの穴に一文。指示文と同じ文体(である調、短く)で書く。
- 書くのは、会話の多数が選んだ行動。少数の側を書かない。
- 条件は、多数の側の会話が挙げた決め手の項目で書く。状態の項目の名前と値だけを使う(例: 矢が無く、敵が 2 マス以上離れ、遮蔽があるなら)。
- 既にある行や追補と矛盾させない。既にある行の言い換えは書かない。
- 多数の側の理由が一文に纏まらないほどばらばらなら、その穴は書かずに飛ばしてよい(skip に理由を書く)。

## 穴 1: 方針の枝 orc_alarm_unclear(会話 3 本、会話ごとの多数 {'shoot': 1, 'raise_alarm': 2})
### 審判の答え raise_alarm(7 件、会話 3 本)
- [L5+gap] enemy_count>=5,allies=0,alarm=false 「単独でオーク五体、斬るより先に警報を鳴らす」 (round1_s1) | hp=82 enemy=orc distance=1 enemy_count=5 enemy_hp=70 allies=0 potion=False arrows=3 cover=True alarm=False post=corridor time=day
- [L2,L5+gap] alarm=false,enemy_count>=5 「5体の敵に警報未発、射るより先に警報を鳴らす」 (round1_s2) | hp=72 enemy=orc distance=3 enemy_count=5 enemy_hp=90 allies=1 potion=True arrows=18 cover=True alarm=False post=corridor time=day
- [L2,L5,L6+gap] alarm=false,allies=0,time=night 「夜の門で単独、オーク2体に先に警報を鳴らす」 (round1_s2) | hp=82 enemy=orc distance=1 enemy_count=2 enemy_hp=80 allies=0 potion=False arrows=3 cover=False alarm=False post=gate time=night
- [L2,L5,L6+gap] time=night,alarm=false,enemy=orc 「夜に門へオーク2体、用心して先に警報」 (round1_s3) | hp=61 enemy=orc distance=6 enemy_count=2 enemy_hp=40 allies=1 potion=False arrows=9 cover=False alarm=False post=gate time=night
- [L5] alarm=false,enemy_count>=4,arrows=0 「オーク4体で警報未発、矢も無いので鳴らす」 (round1_s3) | hp=83 enemy=orc distance=6 enemy_count=4 enemy_hp=20 allies=1 potion=False arrows=0 cover=False alarm=False post=gate time=day
- [L2,L5+gap] alarm=false,enemy_count>=3,allies=0 「単独でオーク3体、射るより先に警報」 (round1_s3) | hp=84 enemy=orc distance=4 enemy_count=3 enemy_hp=50 allies=0 potion=False arrows=7 cover=True alarm=False post=gate time=day
- [L2,L5,L6+gap] alarm=false,enemy_count>=3,allies=0 「夜に単独でオーク3体、射るより先に警報」 (round1_s3) | hp=79 enemy=orc distance=4 enemy_count=3 enemy_hp=80 allies=0 potion=False arrows=2 cover=True alarm=False post=gate time=night
### 審判の答え melee_attack(2 件、会話 1 本)
- [L2,L5,L6+gap] distance=1,hp>=91,allies>=2 「味方2人と体力十分、隣接オークを斬る」 (round1_s3) | hp=91 enemy=orc distance=1 enemy_count=2 enemy_hp=60 allies=2 potion=True arrows=0 cover=False alarm=False post=gate time=night
- [L2] distance=1 「隣接したオークと近接で戦う」 (round1_s3) | hp=77 enemy=orc distance=1 enemy_count=1 enemy_hp=50 allies=1 potion=True arrows=0 cover=False alarm=False post=corridor time=day
### 審判の答え shoot(1 件、会話 1 本)
- [L2] distance>=2,arrows>=1 「遠いオーク一体、矢が十分あるので射る」 (round1_s1) | hp=63 enemy=orc distance=6 enemy_count=1 enemy_hp=70 allies=1 potion=True arrows=19 cover=True alarm=False post=gate time=day

## 穴 2: 方針の枝 troll_alarm_raised(会話 3 本、会話ごとの多数 {'shoot': 2, 'take_cover': 1})
### 審判の答え shoot(2 件、会話 2 本)
- [L2,L3+gap] distance>=4,arrows>=1,allies>=2 「味方がいて矢も多い、近づく前にトロルを射る」 (round1_s1) | hp=78 enemy=troll distance=4 enemy_count=3 enemy_hp=80 allies=2 potion=False arrows=20 cover=True alarm=True post=corridor time=night
- [L2,L3+gap] allies>=1,distance>=2,arrows>=14 「味方がいて間合いもある、トロルを矢で削る」 (round1_s3) | hp=86 enemy=troll distance=3 enemy_count=1 enemy_hp=80 allies=1 potion=False arrows=14 cover=False alarm=True post=gate time=day
### 審判の答え take_cover(2 件、会話 1 本)
- [L2,L3,L6+gap] enemy=troll,allies=0,cover=true 「トロル含む4体に単独、夜なので射ずに遮蔽で門に留まる」 (round1_s2) | hp=99 enemy=troll distance=3 enemy_count=4 enemy_hp=30 allies=0 potion=False arrows=6 cover=True alarm=True post=gate time=night
- [L3,L6+gap] enemy=troll,allies=0,cover=true 「単独でトロルに挑めず夜、遮蔽で援軍を待つ」 (round1_s2) | hp=95 enemy=troll distance=6 enemy_count=4 enemy_hp=40 allies=0 potion=False arrows=0 cover=True alarm=True post=corridor time=night
### 審判の答え hold_position(1 件、会話 1 本)
- [L3+gap] arrows=0,distance>=12,allies>=3 「矢が無く敵は遠い、味方3人と門を固めて待つ」 (round1_s2) | hp=92 enemy=troll distance=12 enemy_count=5 enemy_hp=40 allies=3 potion=True arrows=0 cover=True alarm=True post=gate time=day

## 穴 3: 方針の枝 mage_alarm_unclear(会話 3 本、会話ごとの多数 {'raise_alarm': 2, 'melee_attack': 1})
### 審判の答え raise_alarm(4 件、会話 3 本)
- [L4,L5] enemy=mage,alarm=false,arrows=0 「魔術師が現れ未警報、矢もないので警報を鳴らす」 (round1_s1) | hp=89 enemy=mage distance=6 enemy_count=2 enemy_hp=80 allies=1 potion=False arrows=0 cover=False alarm=False post=corridor time=night
- [L4,L5+gap] alarm=false,enemy_count>=4,allies=0 「魔術師含む4体に単独、まず警報で城に知らせる」 (round1_s2) | hp=74 enemy=mage distance=6 enemy_count=4 enemy_hp=30 allies=0 potion=True arrows=15 cover=False alarm=False post=gate time=day
- [L4,L5+gap] alarm=false,enemy_count>=4,enemy_hp>=90 「魔術師は一射で倒せず4体・夜、先に警報」 (round1_s2) | hp=95 enemy=mage distance=6 enemy_count=4 enemy_hp=90 allies=2 potion=False arrows=6 cover=False alarm=False post=corridor time=night
- [L2,L4,L5+gap] alarm=false,enemy=mage,arrows<=1 「矢1本では魔術師を仕留めきれず先に警報」 (round1_s3) | hp=71 enemy=mage distance=9 enemy_count=2 enemy_hp=70 allies=1 potion=True arrows=1 cover=True alarm=False post=wall time=day
### 審判の答え shoot(2 件、会話 1 本)
- [L4,L5+gap] enemy=mage,enemy_count=1,arrows>=11 「魔術師単独なら警報より先に射て早く仕留める」 (round1_s2) | hp=84 enemy=mage distance=6 enemy_count=1 enemy_hp=40 allies=0 potion=True arrows=11 cover=True alarm=False post=gate time=day
- [L4,L5+gap] enemy=mage,enemy_hp<=10,arrows>=6 「瀕死の魔術師を一射で仕留められるので射る」 (round1_s2) | hp=54 enemy=mage distance=6 enemy_count=2 enemy_hp=10 allies=0 potion=False arrows=6 cover=False alarm=False post=wall time=day
### 審判の答え melee_attack(1 件、会話 1 本)
- [L2,L4,L5+gap] enemy=mage,distance=1,enemy_hp<=30 「隣の弱った魔術師を警報より先に仕留める」 (round1_s3) | hp=93 enemy=mage distance=1 enemy_count=1 enemy_hp=30 allies=1 potion=True arrows=0 cover=False alarm=False post=gate time=night

## 出力
`/home/claude/sekizui/jit/auto_runs/r2/amend/amend_1.json` に JSON を一つ書く: {"amendments": [{"branch": "枝の名", "text": "追補の一文"}], "skip": [{"branch": "枝の名", "why": "理由"}]}
書いたら「完了」とだけ返す。