# 編集の依頼 — 走り r2、第 5 周

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
A4 警報が鳴っておらず、hp が 28 以下で回復薬があり、敵が魔術師で 10 マス以上離れているなら、警報より先に回復薬を飲む。
A5 警報が鳴っており、矢が無く、味方が 3 人以上いて、敵が 4 マス以上離れているなら、遮蔽があっても持ち場を守る。
A6 敵がおらず、hp が 30 以下で回復薬が無いなら、味方が 1 人以上いれば退き、味方がいなければ持ち場を守る。

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

## 穴 1: 方針の枝 mild_no_threat_hold(票の割れた状態 1 件)
### 状態 hp=32 enemy=none distance=None enemy_count=0 enemy_hp=None allies=2 potion=False arrows=20 cover=True alarm=False post=corridor time=day
会話の票: {'retreat': 1, 'hold_position': 3}
- hold_position [L7] enemy=none,hp>=32 「脅威が無く傷も浅めなので持ち場を守る」 (round5_s1)
- hold_position [L7] enemy=none,hp>=31 「敵なしで重傷とまでは言えず持ち場を守る」 (round5_s2)
- hold_position [L7] enemy=none,hp>=31 「脅威が無く、深手とまでは言えないので持ち場を守る」 (round5_s3)
- retreat [L1,L7+gap] hp<=33,potion=false,allies>=2 「深手で薬が無く味方が残るので退いて癒す」 (round2_s1)

## 穴 2: 方針の枝 hurt_no_threat(票の割れた状態 2 件)
### 状態 hp=23 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=15 cover=True alarm=False post=gate time=day
会話の票: {'retreat': 1, 'hold_position': 3}
- hold_position [A6] enemy=none,potion=false,allies=0 「敵なしで味方もいないので持ち場を守る」 (round5_s1)
- hold_position [A6] enemy=none,hp<=30,allies=0 「敵なし・薬なし・味方なしなので持ち場を守る」 (round5_s2)
- hold_position [A6] enemy=none,hp<=30,allies=0 「敵がおらず味方もいないので持ち場を守る」 (round5_s3)
- retreat [L1,L7+gap] hp<=30,potion=false 「深手で薬が無いので退いて癒す」 (round2_s1)
### 状態 hp=14 enemy=none distance=None enemy_count=0 enemy_hp=None allies=0 potion=False arrows=4 cover=True alarm=False post=gate time=day
会話の票: {'retreat': 1, 'hold_position': 3}
- hold_position [A6] enemy=none,potion=false,allies=0 「敵なしで味方もいないので持ち場を守る」 (round5_s1)
- hold_position [A6] enemy=none,hp<=30,allies=0 「敵なし・薬なし・味方なしなので持ち場を守る」 (round5_s2)
- hold_position [A6] enemy=none,hp<=30,allies=0 「敵がおらず味方もいないので持ち場を守る」 (round5_s3)
- retreat [L1,L7+gap] hp<=30,potion=false 「重傷で薬が無いので敵のいない今のうちに退く」 (round2_s2)

## 出力
`/home/claude/sekizui/jit/auto_runs/r2/amend/amend_5.json` に JSON を一つ書く: {"amendments": [{"branch": "枝の名", "text": "追補の一文"}], "skip": [{"branch": "枝の名", "why": "理由"}]}
書いたら「完了」とだけ返す。