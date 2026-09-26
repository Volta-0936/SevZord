"""② r2 — 理由を単位にする自動の輪。

r1(auto_loop.py)との違い:
  - 審判は {行動, 根拠(指示文の行 L0〜L7 / 追補 A1.. / 自分で埋めた gap), 決め手の項目, 一文の理由} を返す。
  - 1 周のラベルを 40 件以下の会話に分ける。証拠の単位は会話(同じ会話の答えは互いに引きずられる)。
  - 根拠が gap に偏り答えが割れている枝から状態を選び、次の周の全会話に入れて票を取る(訊き直し)。
    同じ状態で会話の票が割れ、2/3 以上が揃ったものだけを、編集役(LLM)が指示文の追補一文にする。
    (枝の中の会話ごとの多数で決めると、会話ごとに違う状態を見ているだけの差を「癖」と取り違える。r2 の第 1 周で直した)
    追補は以後の審判と翻訳役に渡る。
  - 門: 範囲の番人、会話の数での熱さ、会話で割れた枝の禁止、共通部分での後退。
  - 監査: 会話 4 本以上が揃い、別の答えを多数にした会話が無い枝は 4%、ほかは 10%。

使い方:
  python auto_loop2.py init <run>
  python auto_loop2.py step <run>      # 次の決まった一歩。LLM の番なら何を待っているかを表示
  python auto_loop2.py status <run>

phase:
  compile_0   翻訳役が briefs/compile_0.md を読んで policies/b0.py を書く
  judge_k     審判が judge_inbox/round{k}_s{j}.jsonl を読んで judge_outbox/round{k}_s{j}.json を書く(会話ごとに一人)
  edit_k      編集役が briefs/edit_k.md を読んで amend/amend_k.json を書く(会話の多数が揃った穴があった時だけ)
  compile_k   翻訳役が briefs/compile_k[_retryN].md を読んで policies/b{k}.py を書く
  done
"""
import json
import math
import os
import sys
import traceback
from collections import Counter, defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from task import gen, ACTIONS  # noqa: E402
from auto_loop import load_policy, fmt, jload, jdump, FUZZ  # noqa: E402
from judge_protocol import numbered, FORMAT, parse_basis  # noqa: E402

ROUNDS, SEG, CAP, SESSION_MAX, MAX_REPLICAS = 5, 500, 120, 40, 8
AUDIT_HI, AUDIT_LO = 0.10, 0.04
NUM_RANGE = {"hp": (5, 100), "distance": (1, 12), "enemy_count": (0, 5), "enemy_hp": (10, 100), "allies": (0, 3),
             "arrows": (0, 20)}
ENUM = {"enemy": ("none", "goblin", "orc", "mage", "troll"), "post": ("gate", "wall", "corridor"),
        "time": ("day", "night")}


def rd(run):
    return os.path.join(HERE, "auto_runs", run)


def sp(run):
    return os.path.join(rd(run), "state.json")


def stream(run):
    return gen(ROUNDS * SEG, jload(sp(run))["stream_seed"])


def envelope_tests(n=450):
    """範囲の外、または知らない値を一つだけ持つ状態。方針はこれら全部で棄権しなければならない。"""
    rng = np.random.default_rng(77)
    fields = list(NUM_RANGE) + list(ENUM)
    out = []
    for i, s in enumerate(gen(n, 78)):
        s = dict(s, id=f"env-{i}")
        f = fields[i % len(fields)]
        if f in NUM_RANGE:
            lo, hi = NUM_RANGE[f]
            s[f] = hi + int(rng.integers(1, 30)) if rng.random() < 0.6 else lo - int(rng.integers(1, 6))
        else:
            s[f] = ["dragon", "tower", "dusk"][list(ENUM).index(f)]
        out.append(s)
    return out


ENV_TESTS = envelope_tests()


# ---------- 審判の答え ----------

def norm(ans):
    out = {}
    for i, r in (ans or {}).items():
        if isinstance(r, str):
            r = {"action": r}
        out[i] = {"action": r.get("action"), "basis": str(r.get("basis", "")),
                  "factors": [str(x) for x in (r.get("factors") or [])][:3], "why": str(r.get("why", ""))[:80]}
    return out


def sessions(run):
    d = os.path.join(rd(run), "judge_outbox")
    out = {}
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if f.startswith("round") and f.endswith(".json"):
            out[f[:-5]] = norm(jload(os.path.join(d, f)))
    return out


def instances(run):
    return [(sn, i, r) for sn, ans in sessions(run).items() for i, r in ans.items() if r["action"] in ACTIONS]


def branch_stats(d, S, inst):
    by = defaultdict(list)
    for sn, i, r in inst:
        a, g = d(S[i])
        by[g].append((sn, i, r, a))
    stats = {}
    for g, rs in by.items():
        a0 = Counter(a for *_, a in rs).most_common(1)[0][0]
        labs = [r["action"] for _, _, r, _ in rs]
        sess = defaultdict(Counter)
        for sn, _, r, _ in rs:
            sess[sn][r["action"]] += 1
        smaj = {sn: c.most_common(1)[0][0] for sn, c in sess.items()}
        stats[g] = {"action": a0, "n": len(rs), "agree": sum(l == a0 for l in labs) if a0 else None,
                    "labels": Counter(labs), "sessions": len(sess),
                    "sess_agree": sum(1 for v in smaj.values() if v == a0) if a0 else None,
                    "sess_major": Counter(smaj.values()),
                    "gap": sum(1 for _, _, r, _ in rs if parse_basis(r["basis"])[1]),
                    "refs": Counter(x for _, _, r, _ in rs for x in sorted(parse_basis(r["basis"])[0])),
                    "facs": Counter(f for _, _, r, _ in rs for f in r["factors"]), "rows": rs}
    return stats


# ---------- 依頼書 ----------

CONTRACT = """## 書く物の約束
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
"""


def ledger_text(run, policy_path):
    st = jload(sp(run))
    d = load_policy(policy_path)
    S = {s["id"]: s for s in stream(run)}
    inst = instances(run)
    stats = branch_stats(d, S, inst)
    lines = [f"## 熱さの帳簿(審判のラベル {len(inst)} 件、会話 {len(sessions(run))} 本を、いまの方針の枝ごとに数えた)", "",
             "| 枝 | 件数 | 会話 | 方針の答え | 一致 | 会話の多数が方針と同じ | 審判の答え | 根拠 | 決め手(多い順) |",
             "|---|---|---|---|---|---|---|---|---|"]
    for g, b in sorted(stats.items(), key=lambda kv: -kv[1]["n"]):
        refs = ", ".join(f"{x} {c}" for x, c in b["refs"].most_common(3))
        lines.append(f"| {g} | {b['n']} | {b['sessions']} | {b['action']} | "
                     f"{b['agree'] if b['action'] else '-'}/{b['n'] if b['action'] else '-'} | "
                     f"{b['sess_agree'] if b['action'] else '-'}/{b['sessions']} | {dict(b['labels'])} | "
                     f"{refs}{'; gap ' + str(b['gap']) if b['gap'] else ''} | "
                     f"{', '.join(f'{f} {c}' for f, c in b['facs'].most_common(4))} |")
    lines += ["", "## 食い違いと棄権の例(全部。[根拠] 決め手 「理由」 会話)"]
    for g, b in sorted(stats.items(), key=lambda kv: -kv[1]["n"]):
        bad = [x for x in b["rows"] if x[3] is None or x[3] != x[2]["action"]]
        if not bad:
            continue
        lines.append(f"### {g}")
        for sn, i, r, a in sorted(bad, key=lambda x: (x[2]["action"], x[0])):
            lines.append(f"- 方針={a} 審判={r['action']} [{r['basis']}] {','.join(r['factors'])} 「{r['why']}」 "
                         f"({sn}) | {fmt(S[i])}")
    votes = replicated_votes(run)
    split = {i: v for i, v in votes.items() if len({r["action"] for _, r in v}) > 1}
    if votes:
        lines += ["", f"## 訊き直した状態(同じ状態を会話 3 本以上に訊いた。{len(votes)} 件のうち票が割れたもの {len(split)} 件)"]
        for i, v in split.items():
            acts = Counter(r["action"] for _, r in v)
            lines.append(f"- 票 {dict(acts)} | {fmt(S[i])} | " +
                         " / ".join(f"{r['action']}「{r['why']}」" for _, r in v))
    pend = st.get("pending", [])
    if pend:
        lines += ["", "## 根拠が gap に偏り、答えが割れている枝(輪が同じ状態を複数の会話に訊き直している。会話の癖か、状態の違いかは、訊き直しの票で分かる)"]
        for p in pend:
            lines.append(f"- 枝 {p['branch']}: 審判の答え {p['votes']}")
    return lines


def write_brief(run, k, retry=0, gate_report=None):
    st = jload(sp(run))
    lines = [f"# 翻訳の依頼 — 走り {run}、第 {k} 版" + (f"(やり直し {retry} 回目)" if retry else ""), "",
             "あなたは翻訳役だ。審判(別の LLM)が指示文に従って下す判断を、番人付きの Python の方針に翻訳する。",
             "目的は、審判の会話の多数と同じ答えを出すこと。会話が割れている所や、証拠が足りない所は棄権して審判に回す。",
             "読んでよいのはこの依頼書だけ。ほかのファイル(ほかの方針、保留のデータ、別の走り)は開かないこと。", "",
             "## 審判が受け取っている指示文(行の記号 L0〜L7、追補 A1.. は根拠の欄で使われる)", "```",
             numbered(st["amendments"]), "```", "", CONTRACT]
    out_path = os.path.join(rd(run), "policies", f"b{k}.py")
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


def write_edit_brief(run, k, settled):
    """settled: {枝: [訊き直して票が割れ、2/3 以上が揃った状態の id]}"""
    st = jload(sp(run))
    S = {s["id"]: s for s in stream(run)}
    votes = replicated_votes(run)
    lines = [f"# 編集の依頼 — 走り {run}、第 {k} 周", "",
             "あなたは編集役だ。番兵 NPC の指示文には書かれていない所(穴)がある。同じ状態を審判(別の LLM)の会話 3 本以上に訊いたところ、",
             "会話によって答えが割れ、2/3 以上の会話が同じ答えを選んだ状態が見つかった。これは指示文が決めていない所を、会話がそれぞれの約束で埋めている印だ。",
             "穴ごとに、多数の会話の判断を指示文の追補として一文で書く。読んでよいのはこの依頼書だけ。", "",
             "## いまの指示文", "```", numbered(st["amendments"]), "```", "",
             "## 書き方の約束",
             "- 一つの穴に一文(同じ枝の状態が同じ理由で揃っていれば一文に纏める)。指示文と同じ文体(である調、短く)。",
             "- 書くのは、多数の会話が選んだ行動。少数の側を書かない。",
             "- 条件は、多数の側が挙げた決め手の項目で書く。状態の項目の名前と値だけを使う(例: 矢が無く、敵が 2 マス以上離れ、遮蔽があるなら)。",
             "- 条件は、下に並べた状態を覆う最も狭いものにする。広げすぎると、指示文の他の行が決めている所まで塗り替えてしまう。",
             "- 既にある行や追補と矛盾させない。既にある行の言い換えは書かない。",
             "- 多数の側の理由が一文に纏まらないほどばらばらなら、その穴は書かずに飛ばす(skip に理由を書く)。", ""]
    for n, (g, ids) in enumerate(settled.items(), 1):
        lines.append(f"## 穴 {n}: 方針の枝 {g}(票の割れた状態 {len(ids)} 件)")
        for i in ids:
            v = votes[i]
            acts = Counter(r["action"] for _, r in v)
            lines.append(f"### 状態 {fmt(S[i])}")
            lines.append(f"会話の票: {dict(acts)}")
            for sn, r in sorted(v, key=lambda x: -acts[x[1]["action"]]):
                lines.append(f"- {r['action']} [{r['basis']}] {','.join(r['factors'])} 「{r['why']}」 ({sn})")
        lines.append("")
    out = os.path.join(rd(run), "amend", f"amend_{k}.json")
    lines += ["## 出力",
              f"`{out}` に JSON を一つ書く: "
              '{"amendments": [{"branch": "枝の名", "text": "追補の一文"}], "skip": [{"branch": "枝の名", "why": "理由"}]}',
              "書いたら「完了」とだけ返す。"]
    p = os.path.join(rd(run), "briefs", f"edit_{k}.md")
    open(p, "w", encoding="utf-8").write("\n".join(lines))
    return p


# ---------- 門 ----------

def gate(run, new_path, prev_path, grounded_extra=None):
    """grounded_extra(枝, 帳簿) が真なら、例が少なくても冷たい翻訳とみなさない(r3: 機械で確かめた追補の条件に入る枝)。"""
    try:
        d = load_policy(new_path)
    except Exception:
        return ["読み込めない:\n" + traceback.format_exc(limit=2)]
    S = stream(run)
    for s in S + FUZZ:
        try:
            a, g = d(s)
        except Exception:
            return [f"例外: {fmt(s)}\n" + traceback.format_exc(limit=2)]
        if a is not None and a not in ACTIONS:
            return [f"知らない行動 {a!r}: {fmt(s)}"]
        if not isinstance(g, str):
            return [f"枝の名が文字列でない: {g!r}"]
    problems = []
    bad = []
    for s in ENV_TESTS:
        try:
            a, g = d(s)
        except Exception:
            return [f"例外(範囲外の状態): {fmt(s)}\n" + traceback.format_exc(limit=2)]
        if a is not None:
            bad.append((s, a, g))
    if bad:
        problems.append(f"範囲の番人: 範囲外・知らない値の状態 {len(ENV_TESTS)} 件のうち {len(bad)} 件に答えた。例: " +
                        " / ".join(f"{fmt(s)} → {a} ({g})" for s, a, g in bad[:3]))
    inst = instances(run)
    if not inst or prev_path is None:
        return problems
    Sd = {s["id"]: s for s in S}
    dp = load_policy(prev_path)
    stn = branch_stats(d, Sd, inst)
    prev_act = {}
    agree_new = agree_old = n_both = 0
    for sn, i, r in inst:
        ap, gp = dp(Sd[i])
        prev_act.setdefault(gp, ap)
        a, _ = d(Sd[i])
        if a is not None and ap is not None:
            n_both += 1
            agree_new += a == r["action"]
            agree_old += ap == r["action"]
    for g, b in stn.items():
        if b["action"] is None:
            continue
        n, ok = b["n"], b["agree"]
        grounded = b["gap"] == 0 and sum(b["refs"].values()) > 0 and ok == n
        is_new = g not in prev_act or prev_act[g] != b["action"]
        if grounded_extra is not None and not grounded:
            grounded = grounded_extra(g, b)
        if is_new and not (n >= 3 and b["sessions"] >= 2) and not grounded:
            problems.append(f"冷たい翻訳: 枝 {g} は例 {n} 件・会話 {b['sessions']} 本で {b['action']} と答えている"
                            "(新しく答える枝は、3 件以上・会話 2 本以上か、全部が指示文の行を根拠にして一致していること)")
        if n >= 3 and ok / n < 0.8:
            problems.append(f"反証された枝: 枝 {g} は例 {n} 件のうち {ok} 件しか一致しない")
        per = Counter(sn for sn, *_ in b["rows"])
        big = [sn for sn, c in per.items() if c >= 2]
        maj = {sn: Counter(r["action"] for s2, _, r, _ in b["rows"] if s2 == sn).most_common(1)[0][0] for sn in big}
        against = sum(1 for sn in big if maj[sn] != b["action"])
        if against >= 2 and against * 3 >= len(big):
            problems.append(f"会話で割れた枝: 枝 {g} は、2 件以上答えた会話 {len(big)} 本のうち {against} 本が別の答えを多数にしている")
    if n_both and agree_new / n_both < agree_old / n_both - 0.01:
        problems.append(f"後退: 前も今も答える {n_both} 件での一致が {agree_old / n_both:.3f} → {agree_new / n_both:.3f}")
    return problems


# ---------- 選ぶ・穴を調べる ----------

def settled_branches(run, d):
    S = {s["id"]: s for s in stream(run)}
    out = set()
    for g, b in branch_stats(d, S, instances(run)).items():
        if b["action"] and b["sess_agree"] >= 4 and b["sess_agree"] == b["sessions"]:
            out.add(g)
    return out


def select(run, k, policy_name):
    st = jload(sp(run))
    d = load_policy(os.path.join(rd(run), "policies", f"{policy_name}.py"))
    S = stream(run)
    Sd = {s["id"]: s for s in S}
    seg = S[(k - 1) * SEG:k * SEG]
    rng = np.random.default_rng(st["stream_seed"] * 100 + k)
    settled = settled_branches(run, d)
    ab, aud = [], []
    for s in seg:
        a, g = d(s)
        if a is None:
            ab.append(s)
        elif rng.random() < (AUDIT_LO if g in settled else AUDIT_HI):
            aud.append(s)
    if len(ab) + len(aud) > CAP:
        keep = sorted(rng.choice(len(ab), max(CAP - len(aud), 0), replace=False))
        ab = [ab[i] for i in keep]
    reps = [Sd[i] for i in st.get("replicate", [])][:MAX_REPLICAS]
    rep_ids = {s["id"] for s in reps}
    pick = [s for s in ab + aud if s["id"] not in rep_ids]
    nsess = max(math.ceil(len(pick) / SESSION_MAX), 3 if reps else 1)
    groups = [[] for _ in range(nsess)]
    for j, idx in enumerate(rng.permutation(len(pick))):
        groups[j % nsess].append(pick[idx])
    inbox = os.path.join(rd(run), "judge_inbox")
    os.makedirs(inbox, exist_ok=True)
    names = []
    for j, grp in enumerate(groups, 1):
        items = grp + reps
        items = [items[i] for i in rng.permutation(len(items))]
        name = f"round{k}_s{j}"
        with open(os.path.join(inbox, name + ".jsonl"), "w", encoding="utf-8") as f:
            for s in items:
                f.write(json.dumps(s, ensure_ascii=False) + "\n")
        names.append(name)
    open(os.path.join(inbox, "INSTRUCTIONS.txt"), "w", encoding="utf-8").write(numbered(st["amendments"]))
    open(os.path.join(inbox, "FORMAT.txt"), "w", encoding="utf-8").write(FORMAT)
    st["rounds"][str(k)] = {"sessions": names, "abstain": len(ab), "audit": len(aud), "replicas": len(reps),
                            "settled_branches": sorted(settled)}
    st["replicate"] = []
    jdump(st, sp(run))
    return len(pick), len(ab), len(aud), nsess, len(reps)


def gap_regions(run, d):
    """根拠が gap に偏り、答えが割れている枝。ここから訊き直す状態を選ぶ(まだ追補の根拠にはしない)。"""
    S = {s["id"]: s for s in stream(run)}
    out = []
    for g, b in branch_stats(d, S, instances(run)).items():
        if b["sessions"] < 2 or b["gap"] * 2 < b["n"] or len(b["labels"]) < 2:
            continue
        out.append({"branch": g, "n": b["n"], "sessions": b["sessions"], "labels": dict(b["labels"]), "rows": b["rows"]})
    return out


def replicated_votes(run):
    """3 本以上の会話が答えた状態(訊き直した状態)の票。{id: [(会話, 答え)]}"""
    v = defaultdict(list)
    for sn, i, r in instances(run):
        v[i].append((sn, r))
    return {i: x for i, x in v.items() if len({sn for sn, _ in x}) >= 3}


# ---------- 輪 ----------

def after_judge(run, k):
    """会話の癖は、同じ状態を複数の会話に訊いた時にしか見えない(枝の中の会話ごとの多数は、状態の組成の違いを拾ってしまう)。
    だから追補の根拠は「訊き直した状態で会話の票が割れ、2/3 以上が揃ったもの」だけにする。"""
    st = jload(sp(run))
    d = load_policy(os.path.join(rd(run), "policies", f"{st['accepted'][-1]}.py"))
    S = {s["id"]: s for s in stream(run)}
    used = set(st.get("amended_ids", []))
    asked = Counter(st.get("asked", []))
    settled, unresolved = defaultdict(list), []
    for i, v in replicated_votes(run).items():
        acts = Counter(r["action"] for _, r in v)
        if len(acts) < 2 or i in used:
            continue
        top, n = acts.most_common(1)[0]
        if n * 3 >= 2 * len(v):
            settled[d(S[i])[1]].append(i)
        elif asked[i] < 2:
            unresolved.append(i)
    rep = list(unresolved)
    regions = gap_regions(run, d)
    for p in sorted(regions, key=lambda p: -p["n"]):
        ids = [i for sn, i, r, a in p["rows"] if parse_basis(r["basis"])[1] and asked[i] == 0 and i not in rep]
        rep += list(dict.fromkeys(ids))[:3]
    st["replicate"] = list(dict.fromkeys(rep))[:MAX_REPLICAS]
    st["asked"] = st.get("asked", []) + st["replicate"]
    st["pending"] = [{"branch": p["branch"], "votes": p["labels"]} for p in regions]
    st["log"].append(f"第{k}周: 訊き直しで票が割れて 2/3 が揃った状態 {sum(len(x) for x in settled.values())} 件"
                     f"(枝 {sorted(settled)})、揃わず再度 {len(unresolved)} 件、次の周に訊き直す {len(st['replicate'])} 件")
    if settled:
        st["phase"] = f"edit_{k}"
        st["settled_now"] = {g: ids for g, ids in settled.items()}
        jdump(st, sp(run))
        st["brief"] = write_edit_brief(run, k, st["settled_now"])
    else:
        st["phase"] = f"compile_{k}"
        jdump(st, sp(run))
        st["brief"] = write_brief(run, k)
    jdump(st, sp(run))
    return st


def step(run):
    st = jload(sp(run))
    ph = st["phase"]
    if ph.startswith("compile_"):
        k = int(ph.split("_")[1])
        newp = os.path.join(rd(run), "policies", f"b{k}.py")
        if not os.path.exists(newp):
            return st, f"待ち: 翻訳役が {newp} を書く(依頼書 {st['brief']})"
        prevp = os.path.join(rd(run), "policies", f"{st['accepted'][-1]}.py") if st["accepted"] else None
        problems = gate(run, newp, prevp)
        st["gate_log"].append({"version": f"b{k}", "retry": st.get("retry", 0), "problems": problems})
        if problems and st.get("retry", 0) < 2:
            st["retry"] = st.get("retry", 0) + 1
            os.rename(newp, newp.replace(".py", f"_rejected{st['retry']}.py"))
            jdump(st, sp(run))
            st["brief"] = write_brief(run, k, st["retry"], "\n".join(problems))
            jdump(st, sp(run))
            return st, f"門で落ちた({len(problems)} 件)→ やり直しの依頼書 {st['brief']}"
        if problems:
            os.rename(newp, newp.replace(".py", "_rejected3.py"))
            st["log"].append(f"b{k} は門を 3 回通らず、{st['accepted'][-1]} を据え置き")
        else:
            st["accepted"].append(f"b{k}")
        st["retry"] = 0
        if k >= ROUNDS:
            st["phase"] = "done"
            jdump(st, sp(run))
            return st, "完了"
        jdump(st, sp(run))
        n, nab, naud, nsess, nrep = select(run, k + 1, st["accepted"][-1])
        st = jload(sp(run))
        st["phase"] = f"judge_{k + 1}"
        st["log"].append(f"第{k + 1}周: 審判へ {n} 件(棄権 {nab}、監査 {naud})を会話 {nsess} 本に分け、"
                         f"訊き直し {nrep} 件を全会話に入れた")
        jdump(st, sp(run))
        return st, st["log"][-1]
    if ph.startswith("judge_"):
        k = int(ph.split("_")[1])
        names = st["rounds"][str(k)]["sessions"]
        missing = [n for n in names if not os.path.exists(os.path.join(rd(run), "judge_outbox", n + ".json"))]
        if missing:
            return st, "待ち: 審判が " + ", ".join(f"judge_outbox/{n}.json" for n in missing) + " を書く"
        st = after_judge(run, k)
        return st, f"{st['log'][-1]} → {st['phase']}、依頼書 {st['brief']}"
    if ph.startswith("edit_"):
        k = int(ph.split("_")[1])
        p = os.path.join(rd(run), "amend", f"amend_{k}.json")
        if not os.path.exists(p):
            return st, f"待ち: 編集役が {p} を書く(依頼書 {st['brief']})"
        ed = jload(p)
        for a in ed.get("amendments", []):
            aid = f"A{len(st['amendments']) + 1}"
            st["amendments"].append({"id": aid, "text": a["text"], "branch": a.get("branch"), "round": k})
        st.setdefault("amended_ids", []).extend(i for ids in st.get("settled_now", {}).values() for i in ids)
        st["log"].append(f"第{k}周の追補: " + " / ".join(f"{a['id']} {a['text']}" for a in st["amendments"]
                                                         if a["round"] == k) + f"(飛ばした: {ed.get('skip', [])})")
        st["phase"] = f"compile_{k}"
        jdump(st, sp(run))
        st["brief"] = write_brief(run, k)
        jdump(st, sp(run))
        return st, st["log"][-1]
    return st, ph


def init(run, stream_seed=4):
    os.makedirs(os.path.join(rd(run), "amend"), exist_ok=True)
    st = {"run": run, "stream_seed": stream_seed, "phase": "compile_0", "accepted": [], "gate_log": [], "log": [],
          "retry": 0, "amendments": [], "replicate": [], "pending": [], "rounds": {}, "amended_branches": []}
    jdump(st, sp(run))
    st["brief"] = write_brief(run, 0)
    jdump(st, sp(run))
    return st


if __name__ == "__main__":
    cmd, run = sys.argv[1], sys.argv[2]
    if cmd == "init":
        print(init(run)["brief"])
    elif cmd == "step":
        st, msg = step(run)
        print(st["phase"], "|", msg)
    elif cmd == "status":
        print(json.dumps(jload(sp(run)), ensure_ascii=False, indent=1))
