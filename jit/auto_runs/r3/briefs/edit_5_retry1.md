# 編集の依頼 — 走り r3、第 5 周(やり直し 1 回目)

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

追補(審判の会話の多数から足した一文。指示文と同じ重みで使う):
A1 オーク三体以上、または味方の無いまま夜か矢四本以下で向き合うオーク二体は深刻な脅威であり、ひどく傷ついていなければ、警報がまだなら鳴らす。

行動: melee_attack(近接攻撃), shoot(弓で射る), retreat(退く), drink_potion(回復薬を飲む), take_cover(遮蔽に隠れる), raise_alarm(警報を鳴らす), hold_position(持ち場を守る)
状態の項目: hp(番兵の体力 0-100), enemy(最も近い敵の種類: none/goblin/orc/mage/troll), distance(その敵までのマス数、敵がいなければ null), enemy_count(見えている敵の数), enemy_hp(最も近い敵の体力 %), allies(近くの味方の数), potion(回復薬を持っているか), arrows(矢の残り), cover(近くに遮蔽物があるか), alarm(警報が既に鳴っているか), post(持ち場: gate/wall/corridor), time(day/night)
```

## 追補(審判の会話の多数から作り、門で機械的に確かめた規則。条件の式をそのまま使ってよい)
- A1: オーク三体以上、または味方の無いまま夜か矢四本以下で向き合うオーク二体は深刻な脅威であり、ひどく傷ついていなければ、警報がまだなら鳴らす。 → `raise_alarm` / 条件 `s['enemy'] == 'orc' and not s['alarm'] and s['hp'] > 36 and (s['enemy_count'] >= 3 or (s['enemy_count'] >= 2 and s['allies'] == 0 and (s['time'] == 'night' or s['arrows'] <= 4)))`

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

## 穴 1: `no_arrows_cover_day::hold_position` — 方針の枝 no_arrows_cover_day で、会話の多数が hold_position に揃った状態 2 件
### 票の割れた状態(正の例)
- hp=47 enemy=goblin distance=8 enemy_count=1 enemy_hp=40 allies=0 potion=False arrows=0 cover=True alarm=False post=wall time=day  票 {'hold_position': 2, 'take_cover': 1}
    - hold_position [gap] arrows=0,enemy=goblin,enemy_count<=1 「矢が無く小鬼一体は遠い、持ち場で待ち構える」
    - hold_position [gap] arrows=0,enemy=goblin,hp>=47 「矢は無いが相手は弱った小鬼、持ち場で待つ」
    - take_cover [gap] arrows=0,distance>=8,hp<=47 「矢が無く射れず、体力半分で単独なので遮蔽で待つ」
- hp=64 enemy=orc distance=9 enemy_count=2 enemy_hp=70 allies=1 potion=True arrows=0 cover=True alarm=False post=gate time=day  票 {'hold_position': 2, 'raise_alarm': 1}
    - hold_position [gap] arrows=0,distance>=9 「矢が無く二対二、持ち場で迎え撃つ」
    - hold_position [gap] arrows=0,distance>=9 「矢が無く敵は遠い、門で迎え撃つ構えで待つ」
    - raise_alarm [L5] alarm=false,enemy_count>=2,arrows=0 「オーク二体が門へ迫り警報が未だ、射れないので鳴らす」
### 同じ枝の近くの状態で、正の例の多数と同じ答えだったもの(15 件、最大 12 件を示す)
- hp=91 enemy=orc distance=6 enemy_count=1 enemy_hp=90 allies=3 potion=True arrows=0 cover=True alarm=True post=corridor time=day  答え {'hold_position': 3} [gap] arrows=0,distance>=2 「矢がなく敵も遠い、味方と通路を固めて待つ」
- hp=71 enemy=goblin distance=10 enemy_count=2 enemy_hp=80 allies=1 potion=False arrows=0 cover=True alarm=True post=corridor time=day  答え {'hold_position': 3} [gap] arrows=0,distance>=2 「矢がなく敵は遠い、持ち場で待つ」
- hp=91 enemy=orc distance=8 enemy_count=1 enemy_hp=50 allies=0 potion=False arrows=0 cover=True alarm=True post=wall time=day  答え {'hold_position': 3} [gap] arrows=0,distance>=8 「矢が無く敵は遠い、持ち場でオークを迎え撃つ」
- hp=86 enemy=goblin distance=7 enemy_count=1 enemy_hp=60 allies=3 potion=True arrows=0 cover=True alarm=False post=corridor time=day  答え {'hold_position': 3} [gap] arrows=0,distance>=7 「矢が無く敵は遠い、持ち場で待ち受ける」
- hp=91 enemy=goblin distance=7 enemy_count=1 enemy_hp=90 allies=0 potion=False arrows=0 cover=True alarm=True post=gate time=day  答え {'hold_position': 3} [gap] arrows=0,enemy=goblin,enemy_count<=1 「矢が無く小鬼一体は遠い、門で待ち構える」
- hp=100 enemy=goblin distance=8 enemy_count=1 enemy_hp=80 allies=1 potion=True arrows=0 cover=True alarm=True post=corridor time=day  答え {'hold_position': 1} [gap] arrows=0,distance>=8,enemy=goblin 「矢が無く小鬼は遠い、持ち場で接近を待つ」
- hp=98 enemy=orc distance=11 enemy_count=2 enemy_hp=50 allies=0 potion=False arrows=0 cover=True alarm=True post=gate time=day  答え {'hold_position': 1} [gap] arrows=0,distance>=11 「矢が無く敵は遠い、昼なので持ち場で待つ」
- hp=97 enemy=goblin distance=8 enemy_count=1 enemy_hp=40 allies=1 potion=True arrows=0 cover=True alarm=True post=corridor time=day  答え {'hold_position': 1} [gap] arrows=0,distance>=8 「矢が無く小鬼は遠い、持ち場で接近を待つ」
- hp=54 enemy=goblin distance=8 enemy_count=1 enemy_hp=60 allies=0 potion=False arrows=0 cover=True alarm=False post=wall time=day  答え {'hold_position': 1} [gap] arrows=0,distance>=8,enemy=goblin 「矢が無く小鬼1体は遠い、持ち場で待つ」
- hp=85 enemy=goblin distance=4 enemy_count=2 enemy_hp=80 allies=1 potion=False arrows=0 cover=True alarm=True post=corridor time=day  答え {'hold_position': 1} [gap] arrows=0,distance>=4 「矢が無く未接敵、持ち場で小鬼を待ち構える」
- hp=99 enemy=goblin distance=11 enemy_count=3 enemy_hp=100 allies=3 potion=False arrows=0 cover=True alarm=False post=wall time=day  答え {'hold_position': 1} [gap] arrows=0,distance>=2,allies>=3 「矢が無く敵は遠い、味方と持ち場で待つ」
- hp=87 enemy=goblin distance=8 enemy_count=1 enemy_hp=40 allies=1 potion=False arrows=0 cover=True alarm=False post=gate time=day  答え {'hold_position': 1} [gap] arrows=0,distance>=2,time=day 「矢が無く敵は遠い、昼なので持ち場で待つ」
### 同じ枝の近くの状態で、別の答えだったもの(反対側の例。1 件、最大 16 件を示す)
- hp=82 enemy=goblin distance=6 enemy_count=5 enemy_hp=80 allies=3 potion=True arrows=0 cover=True alarm=True post=gate time=day  答え {'take_cover': 1} [L0+gap] arrows=0,enemy_count>=5,cover=true 「矢が無く多勢の小鬼、警報済みなので遮蔽で接近を待つ」
### 前に書いた追補が門で落ちた理由(直して書き直すこと)
```
訊き直しで {'take_cover': 3} だった状態を覆っている: hp=42 enemy=goblin distance=4 enemy_count=3 enemy_hp=60 allies=3 potion=False arrows=0 cover=True alarm=True post=gate time=day
覆った範囲: {'covered_labeled_states': 19, 'covered_instances': 37, 'agree': 30, 'inner_instances': 37, 'inner_agree': 30, 'covered_stream_states': 48}
```

## 出力
`/home/claude/sekizui/jit/auto_runs/r3/amend/amend_5_retry1.json` に JSON を一つ書く: {"amendments": [{"branch": "穴の名(例 hp_ambiguous::retreat)", "action": "行動", "when": "Python の式", "text": "追補の一文"}], "skip": [{"branch": "穴の名", "why": "理由"}]}
書いたら「完了」とだけ返す。