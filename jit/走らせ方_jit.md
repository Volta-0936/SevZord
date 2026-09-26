# ② 思考の JIT — 走らせ方(Windows)

このフォルダ: リポジトリの `jit`

## いちばん簡単な方法(ダブルクリック)

| やりたいこと | ダブルクリックするもの | 結果が書かれる所 |
|---|---|---|
| 自動の輪 r1・r2 の結果を見る(数秒、LLM も鍵も要らない) | `run_eval.bat` | `auto_runs\r1\eval.txt`、`auto_runs\r1\spec_gaps.txt`、`holdout3\eval2.txt`、`probe_faith\score.txt` |
| Jev と比べる(300 回呼ぶ、約 2 分×2) | `run_jev.bat` | `jev_result.txt`、`jev_result_en.txt` |

- `run_jev.bat` は、このフォルダの `typesafe_key.txt`(中身は鍵だけ)を読む。鍵は画面にも記録にも出さない。
- Jev の答えは `jev_holdout2.json` に一件ずつ貯まり、次に走らせた時は続きから呼ぶ。全部呼び直したい時は `jev_holdout2.json` と `jev_holdout2_en.json` を消してから走らせる。
- `run_eval.bat` が「numpy / scikit-learn is missing」と言ったら、下の 0. を一度だけやる。

## コマンドで走らせる

### 0. 準備(一度だけ)
スタートメニューで「PowerShell」と打って開き、次を一行ずつ打つ。

```powershell
cd <リポジトリを置いた場所>\jit
python --version                         # Python 3.12.x と出ればよい
python -m pip install numpy scikit-learn
```

### 1. 結果を確かめる(LLM を呼ばない。どれも数秒)

```powershell
python eval2.py             # r2・r3(理由つき): b0〜b5・c0〜c5 と a0〜a5・P6 を、保留3 の審判 3 会話の多数で測る
python probe_faith.py score # 理由の忠実さ: 審判が挙げた決め手を反転すると答えが変わるか
python auto_eval.py r1      # 自動の輪 r1: a0〜a5 を保留2 で測る。Jev・手の P0/P6・模型と並べる
python spec_gaps.py r1      # 審判の答えが割れる所を、「状態で分かれる」か「会話で分かれる」かに分ける
python final_eval.py        # 手で直した P0〜P6 と模型(→ final_eval.json)
python evalh.py 0 6         # 保留1 での P0 と P6
python profile.py 6         # 熱さの帳簿: P6 の枝ごとのラベル数と審判の答え
python show.py 6 20         # P6 の食い違いと棄権を 20 件
```

### 2. Jev と比べる

```powershell
python jev_compare.py ja    # 審判と同じ日本語の指示文
python jev_compare.py en    # 英訳した指示文(Jev に公平かを確かめる)
```

### 3. 自動の輪を新しく回す

```powershell
python auto_loop3.py init r4     # いちばん新しい輪(r3 の作り: 追補は条件の式つきで門を通す)。流れの種 4、500 状態×5 周
python auto_loop3.py step r4     # 次の決まった一歩。何を待っているかを表示する
python auto_loop3.py status r4
```

r2 の作りは `auto_loop2.py`(方針の名は b)、r3 の作りは `auto_loop3.py`(方針の名は c)。

r1 の作り(答えだけを集める輪)は `auto_loop.py` で、使い方は同じ。

`step` は、LLM が要らない部分(流れを通す、審判に回す状態を選ぶ、熱さの帳簿と依頼書を書く、書かれた方針を門で検査する)だけをする。LLM の番になると止まって、次のどちらかを表示する。

- `待ち: 審判が ...\judge_outbox\roundK_sJ.json を書く` → 会話ごとに別の LLM に、`judge_inbox\INSTRUCTIONS.txt`・`FORMAT.txt`・`roundK_sJ.jsonl` を読ませ、理由つきの JSON を書かせる。
- `待ち: 編集役が ...\amend\amend_K.json を書く` → LLM に `briefs\edit_K.md` だけを読ませ、指示文への追補を書かせる。
- `待ち: 翻訳役が ...\policies\bK.py を書く` → LLM に `briefs\compile_K.md` だけを読ませ、Python を一つ書かせる。

どちらかを置いたら、もう一度 `step`。今は、この二つの LLM の番を、私(Claude)がこの会話の中で別の Claude を起こして回している。君の手元だけで自動で回すには、Claude の API 鍵を使ってこの二つを呼ぶ運転役が要る(まだ書いていない)。

## ファイル

- `auto_loop3.py` r3 の輪。追補は `when`(Python の条件)と `action` つきで、追補の門(amend_gate)を通った物だけが指示文に入る
- `auto_runs\r3\` r3 一式。`policies\c0.py`〜`c5.py`(c0・c1 は r2 の b0・b1 と同じ)、`amend\` 追補の下書き、state.json の amend_gate_log に門の記録
- `auto_loop2.py` 理由を単位にする輪(r2)。審判の答え方は `judge_protocol.py`、門の規則はファイルの冒頭と gate()
- `auto_runs\r2\` 理由つきの輪の一回目。`policies\b0.py`〜`b5.py`、`amend\` 追補、`briefs\edit_K.md` 編集役への依頼書
- `holdout3\` 保留3(200 状態)を理由つきの審判 3 会話ずつ(`h3a_r1`…)と、理由なし 1 会話ずつ(`h3a_p`…)で答えさせたもの
- `probe_faith\` 理由の忠実さの試験(元の状態・決め手を反転した双子・持ち場だけ変えた双子)
- `auto_loop.py` 答えだけを集める輪(r1)。決まった部分と門(コードが守る検査)
- `auto_runs\r1\` 自動の輪の一回目
  - `policies\a0.py`〜`a5.py` 翻訳役が書いた方針。冒頭に、何を変えたかと根拠の件数
  - `briefs\compile_K.md` 翻訳役に渡した依頼書(指示文・約束・熱さの帳簿・食い違いの全例)
  - `judge_inbox\`、`judge_outbox\` 審判に渡した状態と、審判の答え
  - `eval.txt`、`eval.json` 保留2 での結果。`spec_gaps.txt` 指示文の穴の候補
  - `probe_sessions\` 同じ 60 状態を三つの審判の会話に訊いた試験
- `policies\p0.py`〜`p6.py` 手で回した輪(私が翻訳した)
- `judge_outbox\` 手の輪・保留1・保留2・無作為・再現性の審判の答え。審判は同じ答えを二度と出さないので、再現にはこれを使う
- `data\` 状態(保留1 = 種 1、流れ = 種 2、保留2 = 種 3)と審判に渡した指示文
- `jev_compare.py`、`run_jev.bat`、`run_jev.ps1` Jev との比較
