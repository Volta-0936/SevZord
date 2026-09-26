"""② 自動の翻訳の輪(思考の JIT)。人(私)は方針を書かない。書くのは「翻訳役」の LLM、答えるのは「審判」の LLM。
この台本は輪の決まった部分だけをする:流れを通す・審判に回す物を選ぶ・熱さの帳簿を作る・翻訳役への依頼書を書く・
書かれた方針を門で検査する。LLM の呼び出しは外(運転役)がする。次に何が要るかは state.json の phase に書く。

使い方:
  python auto_loop.py init <run>          # 新しい走り
  python auto_loop.py step <run>          # 次の決まった一歩。phase が judge_k / compile_k なら LLM の番
  python auto_loop.py status <run>

phase:
  compile_0        翻訳役が briefs/compile_0.md を読んで policies/a0.py を書く(指示文だけ)
  judge_k          審判が judge_inbox/round{k}.jsonl を読んで judge_outbox/round{k}.json を書く
  compile_k        翻訳役が briefs/compile_k[_retryN].md を読んで policies/a{k}.py を書く
  done

門(方針を受け入れる前の検査。これは LLM ではなくコードが守る):
  1. 動く:流れ全部と無作為な 2 万状態で例外を出さず、答えは 7 つの行動か None。
  2. 冷たい翻訳の禁止:答える枝で、ラベルの例が 1〜2 件しかないのに、前の方針に無い(または答えが変わった)もの。
  3. 反証された枝の禁止:答える枝で、ラベルの例が 3 件以上あり、一致が 80% 未満のもの。
  4. 後退の禁止:前も今も答えるラベルつきの状態で、一致が前の方針より 1 点を超えて下がる。
  (1 と 4 は r1 の後に変異試験で直した。r1 の 6 版は直した門でも全部通る)
門を 2 回続けて通らなければ、前の方針を据え置いて次の周へ進む。
"""
import importlib.util
import json
import os
import sys
import traceback
from collections import Counter, defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from task import gen, INSTRUCTIONS, ACTIONS  # noqa: E402

ROUNDS, SEG, AUDIT, CAP = 5, 500, 0.10, 120
FUZZ = gen(20000, 99)   # 門が例外と知らない行動を探すための状態(審判には回さない)
KEYS = ("hp", "enemy", "distance", "enemy_count", "enemy_hp", "allies", "potion", "arrows", "cover",
        "alarm", "post", "time")


def rd(run):
    return os.path.join(HERE, "auto_runs", run)


def jload(p, default=None):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else default


def jdump(o, p):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(o, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def load_policy(path):
    spec = importlib.util.spec_from_file_location(os.path.basename(path)[:-3], path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.decide


def stream(run):
    return gen(ROUNDS * SEG, jload(os.path.join(rd(run), "state.json"))["stream_seed"])


def labels(run):
    out = {}
    d = os.path.join(rd(run), "judge_outbox")
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if f.startswith("round") and f.endswith(".json"):
            out.update(jload(os.path.join(d, f)))
    return out


def fmt(s):
    return " ".join(f"{k}={s[k]}" for k in KEYS)


CONTRACT = """## 書く物の約束
- ファイルは Python 一つ。関数 `decide(s)` を一つ定義する。`s` は状態の dict(項目は下の指示文を参照、distance と enemy_hp は敵がいなければ None)。
- 返り値は `(行動, 枝の名)` か `(None, 棄権の理由)`。行動は次の 7 つの文字列のどれか: melee_attack, shoot, retreat, drink_potion, take_cover, raise_alarm, hold_position。
- 枝の名は、その答えを出した規則の短い英字の名前(例: "no_threat")。同じ規則には同じ名前を使い続ける(帳簿は枝の名で数える)。
- 標準ライブラリ以外を import しない。外部の状態を持たない。
- ファイルの冒頭の docstring に、この版で何を変えたかと、その根拠(帳簿の件数)を書く。

## 翻訳の規律(門がコードで検査する)
- 枝が答えてよいのは、(a) 指示文をそのまま読んだ規則か、(b) 帳簿でその状況の一貫した例が 3 件以上あり、その答えが 80% 以上を占める時だけ。
- 例が 1〜2 件しかない状況、または審判の答えが割れている状況は、名前を付けた番人で棄権する(`return None, "理由"`)。棄権は失敗ではない。審判に任せる正しい手だ。
- 帳簿の例に過剰に合わせない。閾値は例の間に置き、根拠の件数を docstring に書く。
"""


def write_brief(run, k, retry=0, gate_report=None):
    st = jload(os.path.join(rd(run), "state.json"))
    lines = [f"# 翻訳の依頼 — 走り {run}、第 {k} 版" + (f"(やり直し {retry} 回目)" if retry else ""), "",
             "あなたは翻訳役だ。審判(別の LLM)が指示文に従って下す判断を、番人付きの Python の方針に翻訳する。",
             "目的は、審判と同じ答えを出すこと。審判の答えが割れている所や、例が足りない所は棄権して審判に回す。",
             "読んでよいのはこの依頼書だけ。ほかのファイル(ほかの方針、保留のデータ、別の走り)は開かないこと。", "",
             "## 審判が受け取っている指示文", "```", INSTRUCTIONS, "```", "", CONTRACT]
    out_path = os.path.join(rd(run), "policies", f"a{k}.py")
    if k == 0:
        lines += ["## この版", "まだ審判のラベルは一件も無い。指示文だけを読んで、はっきり読める所は答え、曖昧な所は棄権する最初の方針を書く。"]
    else:
        prev = st["accepted"][-1]
        src = open(os.path.join(rd(run), "policies", f"{prev}.py"), encoding="utf-8").read()
        lines += [f"## いまの方針({prev})", "```python", src, "```", ""]
        lines += ledger_text(run, os.path.join(rd(run), "policies", f"{prev}.py"))
    if gate_report:
        lines += ["", "## 前に書いた版が門で落ちた理由(直して書き直すこと)", "```", gate_report, "```"]
    lines += ["", "## 出力", f"`{out_path}` に書く。書いたら「完了」とだけ返す。"]
    p = os.path.join(rd(run), "briefs", f"compile_{k}" + (f"_retry{retry}" if retry else "") + ".md")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write("\n".join(lines))
    return p


def ledger_text(run, policy_path):
    d = load_policy(policy_path)
    S = {s["id"]: s for s in stream(run)}
    L = labels(run)
    by = defaultdict(list)
    for i, lab in L.items():
        a, g = d(S[i])
        by[g].append((a, lab, S[i]))
    lines = [f"## 熱さの帳簿(これまでの審判のラベル {len(L)} 件を、いまの方針の枝ごとに数えた)", "",
             "| 枝 | 件数 | 方針の答え | 一致 | 審判の答え |", "|---|---|---|---|---|"]
    for g, rs in sorted(by.items(), key=lambda kv: -len(kv[1])):
        a0 = rs[0][0]
        ok = sum(1 for a, lab, _ in rs if a == lab)
        lines.append(f"| {g} | {len(rs)} | {a0} | {ok}/{len(rs) if a0 is not None else '-'} | "
                     f"{dict(Counter(lab for _, lab, _ in rs))} |")
    lines += ["", "## 食い違いと棄権の例(全部)"]
    for g, rs in sorted(by.items(), key=lambda kv: -len(kv[1])):
        bad = [(a, lab, s) for a, lab, s in rs if a is None or a != lab]
        if not bad:
            continue
        lines.append(f"### {g}")
        for a, lab, s in bad:
            lines.append(f"- 方針={a} 審判={lab} | {fmt(s)}")
    return lines


def gate(run, new_path, prev_path):
    """方針を受け入れる前の検査。問題の一覧を返す(空なら通過)。"""
    problems = []
    try:
        d = load_policy(new_path)
    except Exception:
        return ["読み込めない:\n" + traceback.format_exc(limit=2)]
    S = stream(run)
    # 流れ全部と、別の種の無作為な状態 2 万件(1 回 1µs 程度なので 20ms ほど)。変異試験で、
    # 流れの頭 600 件だけでは珍しい状態(hp=13 など)での例外を見逃すと分かったため広げた。
    for s in S + FUZZ:
        try:
            a, g = d(s)
        except Exception:
            return [f"例外: {fmt(s)}\n" + traceback.format_exc(limit=2)]
        if a is not None and a not in ACTIONS:
            return [f"知らない行動 {a!r}: {fmt(s)}"]
        if not isinstance(g, str):
            return [f"枝の名が文字列でない: {g!r}"]
    L = labels(run)
    if not L or prev_path is None:
        return problems
    Sd = {s["id"]: s for s in S}
    dp = load_policy(prev_path)
    by, byp = defaultdict(list), {}
    agree_new = agree_old = n_both = 0
    for i, lab in L.items():
        try:
            a, g = d(Sd[i])
        except Exception:
            return [f"例外: {fmt(Sd[i])}\n" + traceback.format_exc(limit=2)]
        ap, gp = dp(Sd[i])
        by[g].append((a, lab))
        byp.setdefault(gp, ap)
        # 後退は「前も今も答える状態」だけで比べる。答えた物全体の一致で比べると、覆いを難しい所へ
        # 広げただけで下がって見える(覆いと精度の曲線の別の点を比べてしまう)。広げた所は枝の規則が見る。
        if a is not None and ap is not None:
            n_both += 1
            agree_new += a == lab
            agree_old += ap == lab
    for g, rs in by.items():
        a0 = rs[0][0]
        if a0 is None:
            continue
        n = len(rs)
        ok = sum(1 for a, lab in rs if a == lab)
        if 1 <= n < 3 and (g not in byp or byp[g] != a0):
            problems.append(f"冷たい翻訳: 枝 {g} は例 {n} 件だけで {a0} と答えている(3 件未満なら棄権する)")
        if n >= 3 and ok / n < 0.8:
            problems.append(f"反証された枝: 枝 {g} は例 {n} 件のうち {ok} 件しか一致しない")
    if n_both and agree_new / n_both < agree_old / n_both - 0.01:
        problems.append(f"後退: 前も今も答える {n_both} 件での一致が {agree_old / n_both:.3f} → {agree_new / n_both:.3f}")
    return problems


def select(run, k, policy_name):
    st = jload(os.path.join(rd(run), "state.json"))
    d = load_policy(os.path.join(rd(run), "policies", f"{policy_name}.py"))
    seg = stream(run)[(k - 1) * SEG:k * SEG]
    rng = np.random.default_rng(st["stream_seed"] * 100 + k)
    ab, cov = [], []
    for s in seg:
        (ab if d(s)[0] is None else cov).append(s)
    aud = [cov[i] for i in sorted(rng.choice(len(cov), min(int(round(AUDIT * len(cov))), len(cov)), replace=False))]
    if len(ab) + len(aud) > CAP:   # 監査は全部残し、棄権の方を無作為に間引く(監査を捨てると答えた枝の誤りが見えない)
        keep = sorted(rng.choice(len(ab), max(CAP - len(aud), 0), replace=False))
        ab = [ab[i] for i in keep]
    pick = ab + aud
    p = os.path.join(rd(run), "judge_inbox", f"round{k}.jsonl")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        for s in pick:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    open(os.path.join(rd(run), "judge_inbox", "INSTRUCTIONS.txt"), "w", encoding="utf-8").write(INSTRUCTIONS)
    return len(pick), len(ab), len(aud)


def step(run):
    sp = os.path.join(rd(run), "state.json")
    st = jload(sp)
    ph = st["phase"]
    if ph.startswith("compile_"):
        k = int(ph.split("_")[1])
        newp = os.path.join(rd(run), "policies", f"a{k}.py")
        if not os.path.exists(newp):
            return st, f"待ち: 翻訳役が {newp} を書く(依頼書 {st['brief']})"
        prevp = os.path.join(rd(run), "policies", f"{st['accepted'][-1]}.py") if st["accepted"] else None
        problems = gate(run, newp, prevp)
        rec = {"version": f"a{k}", "retry": st.get("retry", 0), "problems": problems}
        st["gate_log"].append(rec)
        if problems and st.get("retry", 0) < 2:
            st["retry"] = st.get("retry", 0) + 1
            os.rename(newp, newp.replace(".py", f"_rejected{st['retry']}.py"))
            st["brief"] = write_brief(run, k, st["retry"], "\n".join(problems))
            jdump(st, sp)
            return st, f"門で落ちた({len(problems)} 件)→ やり直しの依頼書 {st['brief']}"
        if problems:
            os.rename(newp, newp.replace(".py", "_rejected3.py"))
            st["log"].append(f"a{k} は門を 3 回通らず、{st['accepted'][-1]} を据え置き")
        else:
            st["accepted"].append(f"a{k}")
        st["retry"] = 0
        if k >= ROUNDS:
            st["phase"] = "done"
            jdump(st, sp)
            return st, "完了"
        n, nab, naud = select(run, k + 1, st["accepted"][-1])
        st["phase"] = f"judge_{k + 1}"
        st["log"].append(f"第{k + 1}周: 審判へ {n} 件(棄権 {nab}、監査 {naud})")
        jdump(st, sp)
        return st, st["log"][-1]
    if ph.startswith("judge_"):
        k = int(ph.split("_")[1])
        p = os.path.join(rd(run), "judge_outbox", f"round{k}.json")
        if not os.path.exists(p):
            return st, f"待ち: 審判が {p} を書く"
        st["phase"] = f"compile_{k}"
        st["brief"] = write_brief(run, k)
        jdump(st, sp)
        return st, f"依頼書 {st['brief']}"
    return st, ph


def init(run, stream_seed=4):
    os.makedirs(rd(run), exist_ok=True)
    st = {"run": run, "stream_seed": stream_seed, "phase": "compile_0", "accepted": [], "gate_log": [],
          "log": [], "retry": 0}
    jdump(st, os.path.join(rd(run), "state.json"))
    st["brief"] = write_brief(run, 0)
    jdump(st, os.path.join(rd(run), "state.json"))
    return st


if __name__ == "__main__":
    cmd, run = sys.argv[1], sys.argv[2]
    if cmd == "init":
        print(init(run)["brief"])
    elif cmd == "step":
        st, msg = step(run)
        print(st["phase"], "|", msg)
    elif cmd == "status":
        print(json.dumps(jload(os.path.join(rd(run), "state.json")), ensure_ascii=False, indent=1))
