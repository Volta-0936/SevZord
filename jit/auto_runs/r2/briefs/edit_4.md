# 編集の依頼 — 走り r2、第 4 周

あなたは編集役だ。番兵 NPC の指示文には書かれていない所(穴)がある。同じ状態を審判(別の LLM)の会話 3 本以上に訊いたところ、
会話によって答えが割れ、2/3 以上の会話が同じ答えを選んだ状態が見つかった。これは指示文が決めていない所を、会話がそれぞれの約束で埋めている印だ。
穴ごとに、多数の会話の判断を指示文の追補として一文で書く。読んでよいのはこの依頼書だけ。

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

追補(審判の会話の多数から足した一文。指示文と同じ重みで使う):
A1 hp が 31 以上あれば、回復薬が無くとも、敵が 9 マス以上離れ矢が残っている間は退かずに弓で射る。
A2 夜に矢が無く、味方がおらず、遮蔽があり、敵が 11 マス以上離れているなら、遮蔽に隠れる。
A3 警報が鳴っておらず、敵が魔術師一体で体力 40% 以下、6 マス以上離れ矢が 11 本以上残っているなら、警報より先に弓で射る。

行動: melee_attack(近接攻撃), shoot(弓で射る), retreat(退く), drink_potion(回復薬を飲む), take_cover(遮蔽に隠れる), raise_alarm(警報を鳴らす), hold_position(持ち場を守る)
状態の項目: hp(番兵の体力 0-100), enemy(最も近い敵の種類: none/goblin/orc/mage/troll), distance(その敵までのマス数、敵がいなければ null), enemy_count(見えている敵の数), enemy_hp(最も近い敵の体力 %), allies(近くの味方の数), potion(回復薬を持っているか), arrows(矢の残り), cover(近くに遮蔽物があるか), alarm(警報が既に鳴っているか), post(持ち場: gate/wall/corridor), time(day/night)
```

## 書き方の約束
- 一つの穴に一文(同じ枝の状態が同じ理由で揃っていれば一文に纏める)。指示文と同じ文体(である調、短く)。
- 書くのは、多数の会話が選んだ行動。少数の側を書かない。
- 条件は、多数の側が挙げた決め手の項目で書く。状態の項目の名前と値だけを使う(例: 矢が無く、敵が 2 マス以上離れ、遮蔽があるなら)。
- 条件は、下に並べた状態を覆う最も狭いものにする。広げすぎると、指示文の他の行が決めている所まで塗り替えてしまう。
- 既にある行や追補と矛盾させない。既にある行の言い換えは書かない。
- 多数の側の理由が一文に纏まらないほどばらばらなら、その穴は書かずに飛ばす(skip に理由を書く)。

## 穴 1: 方針の枝 wounded_alarm_unclear(票の割れた状態 1 件)
### 状態 hp=28 enemy=mage distance=10 enemy_count=2 enemy_hp=80 allies=2 potion=True arrows=10 cover=False alarm=False post=wall time=night
会話の票: {'raise_alarm': 2, 'drink_potion': 5}
- drink_potion [L1+gap] hp<=28,potion=true,distance>=10 「重傷で魔術師はまだ遠い、まず回復薬で持ち直す」 (round3_s1)
- drink_potion [L1,L5+gap] hp<=28,potion=true,distance>=10 「夜に重傷、敵は遠いのでまず回復薬を飲む」 (round3_s3)
- drink_potion [L1,L5+gap] hp<=30,potion=true,distance>=10 「重傷で敵はまだ遠い、今のうちに回復薬を飲む」 (round4_s1)
- drink_potion [L1,L5+gap] hp<=28,potion=true,distance>=10 「重傷で薬がある、敵が遠いうちに飲む」 (round4_s2)
- drink_potion [L1,L5+gap] hp<=28,potion=true,enemy=mage 「魔術師の射程内で重傷、味方もいるのでまず薬」 (round4_s3)
- raise_alarm [L4,L5+gap] enemy=mage,alarm=false,distance>=10 「深手だが魔術師はまだ遠い、先に警報を鳴らす」 (round1_s1)
- raise_alarm [L1,L4,L5+gap] enemy=mage,alarm=false,distance>=10 「魔術師はまだ遠い、薬より先に警報を鳴らす」 (round3_s2)

## 穴 2: 方針の枝 no_arrows_hold(票の割れた状態 1 件)
### 状態 hp=42 enemy=goblin distance=4 enemy_count=3 enemy_hp=60 allies=3 potion=False arrows=0 cover=True alarm=True post=gate time=day
会話の票: {'take_cover': 1, 'hold_position': 3}
- hold_position [gap] arrows=0,distance>=2,alarm=true 「矢が無く未接敵、警報済みで門を固めて待つ」 (round4_s1)
- hold_position [gap] arrows=0,distance>=4,allies>=3 「矢が無く敵は離れており、味方と門を固める」 (round4_s2)
- hold_position [gap] arrows=0,distance>=4,allies>=3 「矢が無く敵はまだ届かず、味方と門で迎え撃つ」 (round4_s3)
- take_cover [gap] hp<=42,potion=false,arrows=0 「矢も薬も無く体力半分以下、遮蔽で門に踏み止まる」 (round1_s2)

## 穴 3: 方針の枝 wounded_no_threat(票の割れた状態 3 件)
### 状態 hp=30 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=0 cover=False alarm=False post=gate time=night
会話の票: {'hold_position': 3, 'retreat': 1}
- hold_position [L1,L7+gap] enemy=none,allies=0,hp>=30 「敵も代わりもいない、体力30なら門に残る」 (round1_s3)
- hold_position [L1,L7+gap] enemy=none,hp<=30,potion=false 「深手だが敵がいないので門を離れず守る」 (round4_s1)
- hold_position [L1,L7+gap] enemy=none,allies=0,alarm=false 「脅威が無く単独、門を空けずに持ち場を守る」 (round4_s2)
- retreat [L1,L7+gap] hp<=30,potion=false,enemy=none 「重傷で薬が無く夜に単独なので退く」 (round4_s3)
### 状態 hp=29 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=19 cover=True alarm=False post=wall time=day
会話の票: {'retreat': 3, 'hold_position': 1}
- retreat [L1,L7+gap] hp<=30,potion=false,allies>=2 「深手で薬が無く味方が残るので退いて癒す」 (round2_s1)
- retreat [L1,L7+gap] hp<=29,potion=false,allies>=2 「重傷で薬が無く、味方が持ち場を守れるので退く」 (round4_s2)
- retreat [L1,L7+gap] hp<=29,potion=false,allies=2 「重傷で薬が無く、味方二人に任せて退く」 (round4_s3)
- hold_position [L1,L7+gap] enemy=none,hp<=30,potion=false 「深手だが脅威が無いので持ち場に留まる」 (round4_s1)
### 状態 hp=30 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=12 cover=False alarm=False post=wall time=night
会話の票: {'retreat': 3, 'hold_position': 1}
- retreat [L1,L7+gap] hp<=30,potion=false 「深手で薬が無いので敵のいない今退く」 (round2_s1)
- retreat [L1,L7+gap] hp<=30,potion=false,allies>=1 「重傷で薬が無く、味方がいるので退いて癒す」 (round4_s2)
- retreat [L1,L7+gap] hp<=30,potion=false,allies=1 「重傷で薬が無く、壁は味方に任せて退く」 (round4_s3)
- hold_position [L1,L7+gap] enemy=none,hp<=30,potion=false 「深手だが脅威が無く、退く理由がないので持ち場に留まる」 (round4_s1)

## 出力
`/home/claude/sekizui/jit/auto_runs/r2/amend/amend_4.json` に JSON を一つ書く: {"amendments": [{"branch": "枝の名", "text": "追補の一文"}], "skip": [{"branch": "枝の名", "why": "理由"}]}
書いたら「完了」とだけ返す。