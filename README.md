# SevZord

TypeSafe の Jev(System One)を、私たちなりに作り直す試みです。

Jev は、状態と問いを受け取り、型の決まった答えを二百ミリ秒ほどで返す小さな模型です。SevZord は同じ役目を別の作り方で果たします。大きな LLM に自分の判断を読める Python の方針へ翻訳させ、1 回数マイクロ秒で答えさせます。分からない所は答えずに LLM へ返します。模型を学習させる代わりに、LLM がプログラムを書き、コードの門がそれを検査します。

ゲームの NPC に毎ターン LLM を呼べば、1 回に数百ミリ秒と料金がかかります。小さく速い模型に任せれば、今度は指示文の行間を読み違えます。「夜は用心深く」が、弓を射るのをやめることなのか、遮蔽に隠れることなのか、警報を鳴らすことなのか。欲しかったのは、速さは反射で、判断は大きな LLM のまま、というものでした。

名前は、Sekizui(脊髄)/ spinal cord の S と Jev で **Sev**、髄(zui)と cord で **Zord**。LLM が脳なら、これは脊髄です。

TypeSafe とは関係のない、独立した実験です。

## 結果

題材は城の番兵 NPC です。状態は 12 項目(体力、敵の種類と距離、矢、遮蔽、警報、昼夜…)、行動は 7 つ(近接、射る、退く、回復薬、隠れる、警報、持ち場)。指示文はわざと曖昧に、7 行だけ書きました。正解は、新しい 200 状態を審判(Claude)の会話 3 本ずつに答えさせ、その多数で決めています。

| | 覆い | 審判の多数との一致 | 1 回の判断 |
|---|---|---|---|
| r1: 答えだけを集めて翻訳 | 98.0% | 91.3% | 約 1.4 µs |
| r2: 答えと理由を集めて翻訳 | 98.5% | 95.9% | 約 3 µs |
| **r3: 理由 + 門で確かめた追補** | **99.0%** | **97.5%** | **約 3 µs** |
| 参考: 審判一人が、他の二人の揃った答えと一致する率 | — | 96.4〜98.9% | 数十秒 |
| 参考: r3 と同じラベルで学ばせた勾配ブースティング | 100% | 92.0% | — |

r3 は、審判一人と同じ高さまで来ました。ここから上に残っているのは、審判自身の揺れです。審判に訊いたのは 5 周で 417 件で、残りの 1% は答えずに審判へ返します。

TypeSafe の Jev(System One)にも、同じ指示文で別の 300 状態を訊きました。審判との一致は 71.0%、1 回の中央値は 208 ms でした。ただし、正解が Claude の読み方なので、この比べ方は最初から Claude の側に有利です。数字と事情は [ledger.md](ledger.md) にあります。

## どう動くか

```
ゲームの状態 ─→ 方針(Python)─ 答える ─→ 行動(数 µs)
                    │
                    └ 棄権 ─→ 審判(LLM)が「行動・根拠の行・決め手・一文の理由」を返す
                                  │
          帳簿(枝ごとの件数と会話の数) ←┘
                    │
          翻訳役(LLM)が方針を書き直す ─→ 門(コード)が検査 ─→ 次の方針
                    │
          会話で割れた所は、同じ状態を別の会話に訊き直す
                    │
          2 件以上揃ったら、編集役(LLM)が指示文に追補を一文と条件の式で書く ─→ 追補の門(コード)
```

LLM が受け持つのは、審判、翻訳役、編集役の三つだけです。どの状態を訊くか、帳簿、依頼書、門は、全部コードが決めます。LLM が書いた物は、どれも門を通るまで使いません。

## 分かったこと

**審判は、会話ごとに約束を作る。** 同じ 12 状態(矢が無く、敵が離れ、遮蔽がある)を三つの会話に訊くと、「遮蔽に隠れる」と答えた数は 1、5、0 に分かれました(Cochran の Q、p ≈ 0.015)。同じ会話の答えは互いに引きずられます。だから証拠はラベルの件数ではなく、会話の本数で数えます。

**審判は、自分が穴を埋めていることを知っている。** 理由の欄に「指示文に書いていない所を自分で決めた(gap)」と書かせると、その印の付いた状態では三会話の全会一致が 72% に落ちます。印の無い状態では 97.6% です。どこを訊き直すべきかは、審判自身が教えてくれます。

**理由は後付けではない。** 審判が挙げた決め手を一つだけ反転した双子を同じ会話に訊くと、30 件中 25 件で答えが変わりました。持ち場の項目だけを変えた双子では、30 件中 0 件でした。

**理由があると、翻訳は統計に勝つ。** 答えしか集めなかった r1 では、翻訳した方針と勾配ブースティングはほぼ同じ精度でした。理由を集めた r3 では、同じラベルで 5 点開きました。統計の学習器は答えしか見られません。翻訳役は、決め手を枝の条件にできます。

**一つの状態から書いた規則は、雑音になる。** 訊き直しの 3 票の多数は、走りを変えると裏返ります。同じ状態が、r2 では「射る」3 対 1、r3 では「退く」2 対 1 でした。r2 は、こういう一状態から追補を 7 つ書きました。r3 は、同じ所に割れた状態が 2 件たまるまで書かず、反対側の例を覆う条件を門で落とします。追補は 2 つに減り、どちらも 17〜19 状態を覆う規則になり、精度は 95.9% から 97.5% に上がりました。

**知らない物には答えない。** 翻訳役は、見たことのない敵(dragon)や、範囲外の値には棄権する番人を書きます。門は範囲外の状態 450 件で、それを確かめています。

## 試す

Python 3.10 以上で動きます。

```bash
git clone https://github.com/Volta-0936/SevZord
cd SevZord
python -m pip install -r requirements.txt
cd jit
python check_replay.py      # LLM を呼ばずに、記録した走り r3 を再生して、輪が記録どおりに回るかを確かめる
python eval2.py             # 保留3 での表(r1・r2・r3 の全版)
python probe_faith.py score # 理由の忠実さの試験の集計
```

自分の鍵で輪を回すには、次のどちらかを使います。

```bash
export ANTHROPIC_API_KEY=...
python drive.py r4 --backend anthropic --model claude-opus-5-5
# または Claude Code の CLI で(ファイルを LLM が自分で読み書きする。記録した走りに最も近い形)
python drive.py r4 --backend claude-code
```

1 周ずつ手で進めることもできます(`python auto_loop3.py step r4`)。止まった所で何を待っているかを表示します。Windows での手順と、各ファイルの役目は [jit/走らせ方_jit.md](jit/走らせ方_jit.md) にあります。

## 自分の題材にするには

今のコードは番兵の題材に合わせてあります。差し替えるのは次の所です。

- `jit/task.py` の `ACTIONS`(行動)、`INSTRUCTIONS`(指示文。方針の行は `- ` で始める)、`gen`(状態を作る関数)
- `jit/auto_loop2.py` の `NUM_RANGE` と `ENUM`(範囲の番人が使う、各項目の範囲)
- `jit/auto_loop.py` の `KEYS`(帳簿に状態を書く時の項目の順)
- 評価の台本(`eval2.py` ほか)の正解データと、模型との比べに使う `feat`

状態が決まった形の dict で書けることが前提です。自由な文章を扱うなら、先に LLM で状態に直してから渡します。

## 限界

題材は一つで、合成したものです。審判も翻訳役も編集役も Claude で、正解も Claude の会話の多数です。「Claude の判断をどれだけ失わずに反射へ落とせるか」は測れていますが、その判断が良い判断かどうかは測っていません。記録した走りの LLM 呼び出しは、Claude Code の中から下請けのエージェントに依頼文を渡して行いました。`drive.py` の `anthropic` と `claude-code` はほぼ同じ依頼文を送りますが、このリポジトリの中で本物の API を相手に回したことはまだありません。LLM を呼ばない部分は `check_replay.py` で確かめられます。

## 中身

- `jit/` ② 思考の JIT(この README の本題)
  - `auto_loop3.py` いちばん新しい輪。`auto_loop2.py`(理由を集める輪)と `auto_loop.py`(答えだけの輪)の上に建つ
  - `drive.py` 輪を LLM と一緒に最後まで回す運転役
  - `judge_protocol.py` 審判への渡し方(行の記号、答え方)
  - `auto_runs/r1`〜`r3` 記録した走り。依頼書、審判の答え、方針の全版、門の記録、追補
  - `holdout3/` 正解に使った 200 状態と、審判の会話 3 本ずつの答え(理由つき)と、理由なしの会話の答え
  - `probe_sessions/`(r1 の中)、`probe_faith/` 会話の癖の試験と、理由の忠実さの試験
- 一番上の `world.py`、`spine*.py` ほか: 脊髄 v0〜v2。格子世界で、脳(先読み)の判断を超次元の反射表に覚えさせた最初の実験。`python run_all.py v0` で走る([走らせ方.md](走らせ方.md))
- [ledger.md](ledger.md) 帳簿。走らせる前に書いた予測と、観測、当たり外れ、途中の誤りと訂正を、全部そのまま残してあります

## 帳簿について

予測は、走らせる前に帳簿へ書きました。外れた予測も消していません。r1 では 4 つのうち 3 つが外れました(門は一度も落とさなかったし、ラベルは予想より多かった)。r2 では、ラベルの予測が外れました。途中で組み方を誤って止めた所も、止めた理由と一緒に残しています。この実験の中身は、数字より、その外れ方にあると思っています。

## 誰が作ったか

方向と判断は、このリポジトリの持ち主(設計者)が決めました。コード、実験、帳簿は Claude(Anthropic の LLM)が書きました。

## License

Apache License 2.0([LICENSE](LICENSE))

---

## English summary

**SevZord** is our own attempt at rebuilding what Jev (TypeSafe's System One) does: typed, fast decisions from a state. Instead of training a small model, it has a large LLM compile its own judgment into a readable, guarded Python policy that answers in microseconds and abstains, handing the case back to the LLM, wherever it is unsure. The name: **S**ekizui (spinal cord) + J**ev** → Sev; seki**zui** + **cord** → Zord. If the LLM is the brain, this is the spinal cord. It is an independent project, not affiliated with TypeSafe.

Three LLM roles do the work: a *judge* that answers states with an action, the instruction line it relied on (or "gap" when it filled a hole in the spec itself), the deciding fields, and a one-line reason; a *compiler* that rewrites the policy from a ledger of those answers; and an *editor* that turns agreed-upon gap decisions into spec amendments with a machine-checkable condition. Everything else (which states to ask, the ledger, the briefs, and the gates that reject policies and amendments) is plain code.

On a synthetic NPC task (12 state fields, 7 actions, a deliberately vague 7-line spec), the r3 policy covers 99.0% of fresh states and agrees with a 3-session judge majority 97.5% of the time, at about 3 µs per decision, using 417 judge labels. A single judge session agrees with the other two 96.4–98.9% of the time. A gradient-boosted model trained on the same labels reaches 92.0%.

Findings: judge sessions form their own conventions, so evidence is counted in sessions, not labels. The judge's own "gap" tag predicts where sessions disagree (72% vs 97.6% unanimity). The reasons are causal: flipping a cited factor changes the answer in 25 of 30 cases, while flipping an irrelevant field changes it in 0 of 30. With reasons, the compiled policy beats the statistical learner by 5 points. Rules written from a single split vote are noise; requiring two agreeing split states plus a code gate on each amendment fixes this.

Limits: one synthetic task, and Claude is both the judge and the source of ground truth. `check_replay.py` verifies the deterministic loop without any LLM calls. The recorded runs were driven through Claude Code sub-agents; the `anthropic` and `claude-code` backends of `drive.py` send essentially the same prompts but have not yet been run against the live API inside this repository. Code comments and docs are in Japanese.
