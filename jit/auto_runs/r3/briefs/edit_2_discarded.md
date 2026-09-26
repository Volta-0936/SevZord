# 編集の依頼 — 走り r3、第 2 周

あなたは編集役だ。番兵 NPC の指示文には書かれていない所(穴)がある。同じ状態を審判(別の LLM)の会話 3 本以上に訊いたところ、
会話によって答えが割れ、2/3 以上の会話が同じ答えを選んだ状態が、同じ所に 2 件以上たまった。指示文が決めていない所を、会話がそれぞれの約束で埋めている印だ。
穴ごとに、多数の会話の判断を、指示文の追補として一文と、その条件の Python 式で書く。読んでよいのはこの依頼書だけ。

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

## 書くもの(穴ごとに一つ)
- `text`: 追補の一文。指示文と同じ文体(である調、短く)。
- `action`: 多数の会話が選んだ行動(7 つの英字のどれか)。少数の側を書かない。
- `when`: 追補が効く条件の Python 式。`s` は状態の dict(例: `s['arrows'] == 0 and s['enemy'] != 'none' and s['distance'] >= 2 and s['cover']`)。distance と enemy_hp は敵がいなければ None なので、比べる前に `s['enemy'] != 'none'` を確かめる。使えるのは s と min/max/abs だけ。

## 境界の決め方(ここが要)
- 一つの状態からは規則の広さは決まらない。境界を決めるのは反対側の例だ。
- 条件は、多数の側が挙げた決め手の項目で作る。
- 正の例(票の割れた状態)と、下の「同じ答えだった近くの状態」をできるだけ覆い、「別の答えだった近くの状態」を覆わない条件のうち、最も広いものを選ぶ。
- 狭すぎる条件(一つの状態の値をそのまま写した条件)は、その状態しか決めない役に立たない追補になる。広すぎる条件は、指示文の他の行が決めている所を塗り替える。
- 既にある行や追補と矛盾させない。既にある行の言い換えは書かない。
- 多数の側の理由が一つの条件に纏まらないなら、その穴は飛ばす(skip に理由を書く)。

## 門(コードが確かめる。落ちたら書き直しを頼む)
1. `when` が流れの全状態で例外を出さない。
2. 正の例(多数が action の、票の割れた状態)を全部覆う。
3. `when` が覆うラベルつきの状態の、審判の答えの 80% 以上が action。
4. 訊き直しで 2/3 以上が別の答えだった状態を覆わない。

## 穴 1: 方針の枝 hp_ambiguous(票の割れた状態 2 件)
### 票の割れた状態(正の例)
- hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=13 cover=True alarm=False post=gate time=night  票 {'hold_position': 2, 'retreat': 1}
    - hold_position [L0,L7+gap] enemy=none,post=gate 「深手だが敵はなく、夜の門を空けず持ち場に留まる」
    - hold_position [L1,L7+gap] enemy=none,allies=0,hp>=21 「脅威が無く単独、門を空けず持ち場を守る」
    - retreat [L1,L7+gap] hp<=28,potion=false,allies=0 「深手で薬も無く夜に単独、今のうちに退く」
- hp=31 enemy=goblin distance=9 enemy_count=3 enemy_hp=40 allies=1 potion=False arrows=5 cover=False alarm=True post=wall time=night  票 {'shoot': 1, 'retreat': 2}
    - retreat [L1,L6+gap] hp<=31,potion=false,time=night 「夜に体力が低く薬も無い、無理せず退く」
    - retreat [L1,L2+gap] hp<=33,potion=false,alarm=true 「深手で薬も無い、警報済みなので退く」
    - shoot [L2+gap] distance>=2,arrows>=1,hp>=31 「手負いだが敵は遠く、射るだけなら危険は小さい」
### 同じ枝の近くの状態で、正の例の多数と同じ答えだったもの(4 件、最大 12 件を示す)
- hp=30 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=0 cover=False alarm=False post=gate time=night  答え {'hold_position': 1} [L1,L7+gap] enemy=none,allies=0,hp>=30 「敵も代わりもいない、体力30なら門に残る」
- hp=23 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=15 cover=True alarm=False post=gate time=day  答え {'hold_position': 1} [L0,L7+gap] enemy=none,allies=0,potion=false 「重傷だが脅威も代わりも無い、門で見張る」
- hp=32 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=20 cover=True alarm=False post=corridor time=day  答え {'hold_position': 1} [L7+gap] enemy=none,hp>=32,time=day 「昼で脅威も無く、まだ持ち場を守れる体力」
- hp=32 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=2 cover=True alarm=False post=gate time=day  答え {'hold_position': 1} [L7] enemy=none,hp>=32 「脅威が無く深手でもないので持ち場を守る」
### 同じ枝の近くの状態で、別の答えだったもの(反対側の例。25 件、最大 16 件を示す)
- hp=23 enemy=troll distance=1 enemy_count=3 enemy_hp=10 allies=0 potion=False arrows=14 cover=True alarm=False post=corridor time=day  答え {'retreat': 3} [L1,L3+gap] hp<=30,potion=false,enemy=troll 「瀕死で薬なし、隣にトロルがいるので警報より退く」
- hp=23 enemy=orc distance=6 enemy_count=2 enemy_hp=40 allies=2 potion=False arrows=0 cover=False alarm=False post=corridor time=day  答え {'retreat': 1} [L1] hp<=30,potion=false 「深手で薬も矢もないので退く」
- hp=28 enemy=mage distance=10 enemy_count=2 enemy_hp=80 allies=2 potion=True arrows=10 cover=False alarm=False post=wall time=night  答え {'raise_alarm': 1} [L4,L5+gap] enemy=mage,alarm=false,distance>=10 「深手だが魔術師はまだ遠い、先に警報を鳴らす」
- hp=21 enemy=goblin distance=1 enemy_count=2 enemy_hp=20 allies=3 potion=True arrows=6 cover=True alarm=False post=corridor time=day  答え {'drink_potion': 1} [L1,L2+gap] hp<=21,potion=true 「重傷なので隣の敵より先に回復薬を飲む」
- hp=22 enemy=goblin distance=2 enemy_count=2 enemy_hp=100 allies=0 potion=False arrows=4 cover=False alarm=False post=gate time=day  答え {'retreat': 1} [L1,L2+gap] hp<=22,potion=false,allies=0 「重傷で薬も味方も無い、射たずに退く」
- hp=31 enemy=orc distance=12 enemy_count=2 enemy_hp=30 allies=0 potion=True arrows=10 cover=False alarm=True post=wall time=day  答え {'drink_potion': 1} [L1,L2+gap] hp<=31,potion=true,distance>=12 「深手で敵はまだ遠い、今のうちに回復薬を飲む」
- hp=26 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=True arrows=2 cover=True alarm=True post=wall time=day  答え {'drink_potion': 1} [L1] hp<=26,potion=true,enemy=none 「重傷で敵のいない今、回復薬を飲む」
- hp=30 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=12 cover=False alarm=False post=wall time=night  答え {'retreat': 1} [L1,L7+gap] hp<=30,potion=false,allies>=1 「重傷で薬が無く、壁は味方に任せて退く」
- hp=30 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=True arrows=3 cover=False alarm=False post=wall time=night  答え {'drink_potion': 1} [L1] hp<=30,potion=true,enemy=none 「重傷で薬があり、敵の居ない今のうちに飲む」
- hp=29 enemy=goblin distance=2 enemy_count=2 enemy_hp=60 allies=0 potion=True arrows=0 cover=True alarm=False post=gate time=night  答え {'drink_potion': 1} [L1] hp<=30,potion=true 「重傷で薬がある、小鬼が寄る前に飲む」
- hp=29 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=19 cover=True alarm=False post=wall time=day  答え {'retreat': 1} [L1,L7+gap] hp<=30,potion=false,allies>=1 「重傷で薬が無く、味方に任せて退き回復する」
- hp=26 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=16 cover=False alarm=False post=corridor time=day  答え {'retreat': 1} [L1,L7+gap] hp<=30,potion=false,allies>=1 「重傷で薬が無く、味方に任せて退き回復する」
- hp=28 enemy=none distance=None enemy_count=0 enemy_hp=None allies=1 potion=False arrows=7 cover=False alarm=True post=wall time=night  答え {'retreat': 1} [L1,L7+gap] hp<=30,potion=false,allies>=1 「重傷で薬が無く、壁は味方に任せて退く」
- hp=31 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=True arrows=18 cover=True alarm=False post=gate time=day  答え {'drink_potion': 1} [L1+gap] hp<=31,potion=true,enemy=none 「危うい体力で薬があり、平穏な今のうちに飲む」
- hp=21 enemy=goblin distance=8 enemy_count=2 enemy_hp=60 allies=1 potion=False arrows=5 cover=False alarm=False post=gate time=day  答え {'retreat': 1} [L1+gap] hp<=30,potion=false 「重傷で薬も無い、小鬼が遠いうちに退く」
- hp=32 enemy=orc distance=9 enemy_count=3 enemy_hp=20 allies=3 potion=False arrows=15 cover=True alarm=True post=gate time=night  答え {'retreat': 1} [L1,L6+gap] hp<=32,potion=false,time=night 「夜に体力が低く薬も無い、門を味方に任せ退く」

## 出力
`/home/claude/sekizui/jit/auto_runs/r3/amend/amend_2.json` に JSON を一つ書く: {"amendments": [{"branch": "枝の名", "action": "行動", "when": "Python の式", "text": "追補の一文"}], "skip": [{"branch": "枝の名", "why": "理由"}]}
書いたら「完了」とだけ返す。