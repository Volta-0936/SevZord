"""② r3 — 追補を「機械で確かめた規則」にする輪。

r2(auto_loop2.py)から変えた所(r2 で見えた構造への答え):
  1. 追補の広さは一つの状態からは決まらない(A1 は広すぎ、A2〜A5 は狭すぎ、両側の四状態から書いた A6 だけが原理になった)。
     → 追補を書くのは、同じ枝で「訊き直して票が割れ、2/3 以上が揃った状態」が 2 件以上たまった時だけ。
     → 編集役には、割れた状態(正の例)に加えて、同じ枝の近くの状態(同じ答え/別の答え)を渡す。
     → 編集役は一文と一緒に、その条件の Python 式 `when` と行動 `action` を書く。
  2. 追補の門(コードが守る): `when` は流れの全状態で例外を出さない / 正の例を全部覆う /
     覆うラベルつきの状態の 80% 以上が action / 訊き直しで 2/3 以上が別の答えだった状態を覆わない。
     落ちたら理由を付けて編集役に書き直させる(2 回まで)。通らない追補は捨てる。
  3. 翻訳役の門: 例が少なくても、その枝のラベルつきの状態が全部、同じ行動の追補の `when` に入るなら冷たい翻訳とみなさない
     (追補は会話 3 本以上の多数と門で裏付けられているので)。
  4. 訊き直しを減らす: 1 周 6 状態まで、各状態を 2 会話にだけ入れる(元の会話と合わせて 3 票)。

使い方・phase は auto_loop2.py と同じ(方針の名は c0..c5)。
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
from task import ACTIONS  # noqa: E402
from auto_loop import load_policy, fmt, jload, jdump  # noqa: E402
from judge_protocol import numbered, FORMAT, parse_basis  # noqa: E402
import auto_loop2 as L2  # noqa: E402
from auto_loop2 import (rd, sp, stream, instances, sessions, branch_stats, CONTRACT, ledger_text,  # noqa: E402
                        replicated_votes, gap_regions, settled_branches, ROUNDS, SEG, CAP, SESSION_MAX,
                        AUDIT_HI, AUDIT_LO)

MAX_REPLICAS, REPLICA_SESSIONS, MIN_SPLIT = 6, 2, 2
SAFE = {"min": min, "max": max, "abs": abs, "len": len, "True": True, "False": False, "None": None}


# ---------- 追補の条件 ----------

def when_fn(expr):
    code = compile(expr, "<when>", "eval")
    bad = [n for n in code.co_names if n not in SAFE and n != "s"]
    if bad:
        raise ValueError(f"使えない名前 {bad}")
    g = {"__builtins__": {}, **SAFE}
    return lambda s: bool(eval(code, g, {"s": s}))


def split_settled(run, used=()):
    """訊き直して票が割れ、2/3 以上が揃った状態 {id: (多数の行動, 票)}"""
    out = {}
    for i, v in replicated_votes(run).items():
        acts = Counter(r["action"] for _, r in v)
        if len(acts) < 2 or i in used:
            continue
        top, n = acts.most_common(1)[0]
        if n * 3 >= 2 * len(v):
            out[i] = (top, dict(acts))
    return out


def amend_gate(run, am, positives, d=None, branch=None):
    """追補一つを検査する。問題の一覧と、覆った範囲の報告を返す。
    一致は二か所で測る: 覆う全ラベル(80% 以上)と、「穴の中」= 追補の枝の状態か、根拠が gap のラベルを持つ状態(80% 以上)。
    全体だけで測ると、他の行が既に決めている易しい状態で薄まり、広すぎる追補を見逃す(r2 の A1 がそうだった)。"""
    S = stream(run)
    Sd = {s["id"]: s for s in S}
    try:
        f = when_fn(am["when"])
    except Exception as e:
        return [f"式が読めない: {e}"], {}
    if am.get("action") not in ACTIONS:
        return [f"知らない行動 {am.get('action')!r}"], {}
    try:
        cov_stream = sum(f(s) for s in S)
    except Exception as e:
        return [f"式が例外を出す({type(e).__name__}: {e})。distance・enemy_hp は敵がいなければ None なので、比べる前に確かめる"], {}
    problems = []
    for i, (maj, votes) in positives.items():
        if maj != am["action"]:
            problems.append(f"正の例 {fmt(Sd[i])} の多数は {maj}({votes})で、追補の行動 {am['action']} と違う")
        elif not f(Sd[i]):
            problems.append(f"正の例を覆っていない: {fmt(Sd[i])}(票 {votes})")
    by = defaultdict(list)
    for sn, i, r in instances(run):
        by[i].append(r["action"])
    covered = [i for i in by if f(Sd[i])]
    n_inst = sum(len(by[i]) for i in covered)
    ok = sum(a == am["action"] for i in covered for a in by[i])
    if n_inst and ok / n_inst < 0.8:
        wrong = [i for i in covered if Counter(by[i]).most_common(1)[0][0] != am["action"]]
        problems.append(f"覆うラベルの一致が {ok}/{n_inst} = {ok / n_inst:.2f}(80% 未満)。別の答えだった状態の例: " +
                        " / ".join(f"{fmt(Sd[i])} → {dict(Counter(by[i]))}" for i in wrong[:6]))
    gapl = defaultdict(bool)
    for sn, i, r in instances(run):
        gapl[i] |= parse_basis(r["basis"])[1]
    inner = [i for i in covered if gapl[i] or (d is not None and d(Sd[i])[1] == branch)]
    n_in = sum(len(by[i]) for i in inner)
    ok_in = sum(a == am["action"] for i in inner for a in by[i])
    if n_in >= 3 and ok_in / n_in < 0.8:
        wrong = [i for i in inner if Counter(by[i]).most_common(1)[0][0] != am["action"]]
        problems.append(f"穴の中(追補の枝の状態と、根拠が gap の状態)で覆うラベルの一致が {ok_in}/{n_in} = {ok_in / n_in:.2f}(80% 未満)。"
                        "条件が穴の外まで広がっているか、穴の中に別の答えの所がある。別の答えだった状態の例: " +
                        " / ".join(f"{fmt(Sd[i])} → {dict(Counter(by[i]))}" for i in wrong[:6]))
    for i, v in replicated_votes(run).items():
        acts = Counter(r["action"] for _, r in v)
        top, n = acts.most_common(1)[0]
        if top != am["action"] and n * 3 >= 2 * len(v) and f(Sd[i]):
            problems.append(f"訊き直しで {dict(acts)} だった状態を覆っている: {fmt(Sd[i])}")
    report = {"covered_labeled_states": len(covered), "covered_instances": n_inst, "agree": ok,
              "inner_instances": n_in, "inner_agree": ok_in, "covered_stream_states": cov_stream}
    return problems, report


def amendment_grounded(run):
    """翻訳役の門に渡す: 枝のラベルつきの状態が全部、同じ行動の追補の when に入るか。"""
    st = jload(sp(run))
    fs = [(when_fn(a["when"]), a["action"]) for a in st["amendments"] if a.get("when")]

    def ok(g, b):
        if not fs:
            return False
        for sn, i, r, a in b["rows"]:
            s = STATE[run][i]
            if not any(f(s) and act == b["action"] for f, act in fs):
                return False
        return True
    return ok


STATE = defaultdict(dict)


def _states(run):
    if not STATE[run]:
        STATE[run].update({s["id"]: s for s in stream(run)})
    return STATE[run]


# ---------- 依頼書 ----------

def amendments_block(st):
    if not st["amendments"]:
        return []
    lines = ["## 追補(審判の会話の多数から作り、門で機械的に確かめた規則。条件の式をそのまま使ってよい)"]
    for a in st["amendments"]:
        lines.append(f"- {a['id']}: {a['text']} → `{a['action']}` / 条件 `{a['when']}`")
    return lines + [""]


def write_brief(run, k, retry=0, gate_report=None):
    st = jload(sp(run))
    lines = [f"# 翻訳の依頼 — 走り {run}、第 {k} 版" + (f"(やり直し {retry} 回目)" if retry else ""), "",
             "あなたは翻訳役だ。審判(別の LLM)が指示文に従って下す判断を、番人付きの Python の方針に翻訳する。",
             "目的は、審判の会話の多数と同じ答えを出すこと。会話が割れている所や、証拠が足りない所は棄権して審判に回す。",
             "読んでよいのはこの依頼書だけ。ほかのファイル(ほかの方針、保留のデータ、別の走り)は開かないこと。", "",
             "## 審判が受け取っている指示文(行の記号 L0〜L7、追補 A1.. は根拠の欄で使われる)", "```",
             numbered(st["amendments"]), "```", ""] + amendments_block(st) + [
             CONTRACT,
             "- 追補をそのまま読んだ枝は、例が少なくても答えてよい(門は、その枝のラベルつきの状態が全部、同じ行動の追補の条件に入るかを確かめる)。", ""]
    out_path = os.path.join(rd(run), "policies", f"c{k}.py")
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


def write_edit_brief(run, k, regions, retry=0, reports=None):
    """regions: {枝: [正の例の id]}"""
    st = jload(sp(run))
    S = _states(run)
    d = load_policy(os.path.join(rd(run), "policies", f"{st['accepted'][-1]}.py"))
    votes = replicated_votes(run)
    by = defaultdict(list)
    for sn, i, r in instances(run):
        by[i].append((sn, r))
    lines = [f"# 編集の依頼 — 走り {run}、第 {k} 周" + (f"(やり直し {retry} 回目)" if retry else ""), "",
             "あなたは編集役だ。番兵 NPC の指示文には書かれていない所(穴)がある。同じ状態を審判(別の LLM)の会話 3 本以上に訊いたところ、",
             "会話によって答えが割れ、2/3 以上の会話が同じ答えを選んだ状態が、同じ所に 2 件以上たまった。指示文が決めていない所を、会話がそれぞれの約束で埋めている印だ。",
             "穴ごとに、多数の会話の判断を、指示文の追補として一文と、その条件の Python 式で書く。読んでよいのはこの依頼書だけ。", "",
             "## いまの指示文", "```", numbered(st["amendments"]), "```", ""] + amendments_block(st) + [
             "## 書くもの(穴ごとに一つ)",
             "- `text`: 追補の一文。指示文と同じ文体(である調、短く)。",
             "- `action`: 多数の会話が選んだ行動(7 つの英字のどれか)。少数の側を書かない。",
             "- `when`: 追補が効く条件の Python 式。`s` は状態の dict(例: `s['arrows'] == 0 and s['enemy'] != 'none' and s['distance'] >= 2 and s['cover']`)。"
             "distance と enemy_hp は敵がいなければ None なので、比べる前に `s['enemy'] != 'none'` を確かめる。使えるのは s と min/max/abs だけ。",
             "",
             "## 境界の決め方(ここが要)",
             "- 一つの状態からは規則の広さは決まらない。境界を決めるのは反対側の例だ。",
             "- 条件は、多数の側が挙げた決め手の項目で作る。",
             "- 正の例(票の割れた状態)と、下の「同じ答えだった近くの状態」をできるだけ覆い、「別の答えだった近くの状態」を覆わない条件のうち、最も広いものを選ぶ。",
             "- 狭すぎる条件(一つの状態の値をそのまま写した条件)は、その状態しか決めない役に立たない追補になる。広すぎる条件は、指示文の他の行が決めている所を塗り替える。",
             "- 既にある行や追補と矛盾させない。既にある行の言い換えは書かない。",
             "- 多数の側の理由が一つの条件に纏まらないなら、その穴は飛ばす(skip に理由を書く)。",
             "",
             "## 門(コードが確かめる。落ちたら書き直しを頼む)",
             "1. `when` が流れの全状態で例外を出さない。",
             "2. 正の例(多数が action の、票の割れた状態)を全部覆う。",
             "3. `when` が覆うラベルつきの状態の、審判の答えの 80% 以上が action。",
             "4. 訊き直しで 2/3 以上が別の答えだった状態を覆わない。", ""]
    for n, (rid, ids) in enumerate(regions.items(), 1):
        g, act = rid.split("::")
        lines.append(f"## 穴 {n}: `{rid}` — 方針の枝 {g} で、会話の多数が {act} に揃った状態 {len(ids)} 件")
        lines.append("### 票の割れた状態(正の例)")
        for i in ids:
            v = votes[i]
            acts = Counter(r["action"] for _, r in v)
            lines.append(f"- {fmt(S[i])}  票 {dict(acts)}")
            for sn, r in sorted(v, key=lambda x: -acts[x[1]["action"]]):
                lines.append(f"    - {r['action']} [{r['basis']}] {','.join(r['factors'])} 「{r['why']}」")
        near = [i for i in by if i not in ids and d(S[i])[1] == g]
        maj_pos = act
        same, diff = [], []
        for i in near:
            c = Counter(r["action"] for _, r in by[i])
            (same if c.most_common(1)[0][0] == maj_pos else diff).append((i, c))
        lines.append(f"### 同じ枝の近くの状態で、正の例の多数と同じ答えだったもの({len(same)} 件、最大 12 件を示す)")
        for i, c in same[:12]:
            r = by[i][0][1]
            lines.append(f"- {fmt(S[i])}  答え {dict(c)} [{r['basis']}] {','.join(r['factors'])} 「{r['why']}」")
        lines.append(f"### 同じ枝の近くの状態で、別の答えだったもの(反対側の例。{len(diff)} 件、最大 16 件を示す)")
        for i, c in diff[:16]:
            r = by[i][0][1]
            lines.append(f"- {fmt(S[i])}  答え {dict(c)} [{r['basis']}] {','.join(r['factors'])} 「{r['why']}」")
        if reports and rid in reports:
            lines += ["### 前に書いた追補が門で落ちた理由(直して書き直すこと)", "```", reports[rid], "```"]
        lines.append("")
    out = os.path.join(rd(run), "amend", f"amend_{k}" + (f"_retry{retry}" if retry else "") + ".json")
    lines += ["## 出力",
              f"`{out}` に JSON を一つ書く: "
              '{"amendments": [{"branch": "穴の名(例 hp_ambiguous::retreat)", "action": "行動", "when": "Python の式", "text": "追補の一文"}], '
              '"skip": [{"branch": "穴の名", "why": "理由"}]}',
              "書いたら「完了」とだけ返す。"]
    p = os.path.join(rd(run), "briefs", f"edit_{k}" + (f"_retry{retry}" if retry else "") + ".md")
    open(p, "w", encoding="utf-8").write("\n".join(lines))
    return p, out


# ---------- 選ぶ ----------

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
    nsess = max(math.ceil(len(pick) / SESSION_MAX), REPLICA_SESSIONS if reps else 1)
    groups = [[] for _ in range(nsess)]
    for j, idx in enumerate(rng.permutation(len(pick))):
        groups[j % nsess].append(pick[idx])
    for j, s in enumerate(reps):   # 訊き直しは 2 会話にだけ入れる(元の会話と合わせて 3 票)
        for t in range(REPLICA_SESSIONS):
            groups[(j + t) % nsess].append(s)
    inbox = os.path.join(rd(run), "judge_inbox")
    os.makedirs(inbox, exist_ok=True)
    names = []
    for j, grp in enumerate(groups, 1):
        items = [grp[i] for i in rng.permutation(len(grp))]
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


# ---------- 輪 ----------

def after_judge(run, k):
    st = jload(sp(run))
    d = load_policy(os.path.join(rd(run), "policies", f"{st['accepted'][-1]}.py"))
    S = _states(run)
    used = set(st.get("amended_ids", []))
    asked = Counter(st.get("asked", []))
    settled = split_settled(run, used)
    pools = defaultdict(list)   # 穴 = (枝, 多数の行動)。同じ枝でも多数の答えが違えば別の穴(r3 第 2 周で、同じ枝に hold と retreat の正の例が混ざった)
    for i, (maj, _) in settled.items():
        pools[f"{d(S[i])[1]}::{maj}"].append(i)
    ready = {g: ids for g, ids in pools.items() if len(ids) >= MIN_SPLIT}
    unresolved = []
    for i, v in replicated_votes(run).items():
        acts = Counter(r["action"] for _, r in v)
        top, n = acts.most_common(1)[0]
        if len(acts) > 1 and n * 3 < 2 * len(v) and asked[i] < 2 and i not in used:
            unresolved.append(i)
    rep = list(unresolved)
    for p in sorted(gap_regions(run, d), key=lambda p: -p["n"]):
        ids = [i for sn, i, r, a in p["rows"] if parse_basis(r["basis"])[1] and asked[i] == 0 and i not in rep]
        rep += list(dict.fromkeys(ids))[:3]
    st["replicate"] = list(dict.fromkeys(rep))[:MAX_REPLICAS]
    st["asked"] = st.get("asked", []) + st["replicate"]
    st["pending"] = [{"branch": p["branch"], "votes": p["labels"]} for p in gap_regions(run, d)]
    st["log"].append(f"第{k}周: 票が割れて 2/3 が揃った状態 {len(settled)} 件(枝ごと {dict((g, len(v)) for g, v in pools.items())})、"
                     f"2 件以上たまった枝 {sorted(ready)}、揃わず再度 {len(unresolved)} 件、次の周に訊き直す {len(st['replicate'])} 件")
    if ready:
        st["phase"] = f"edit_{k}"
        st["edit"] = {"regions": ready, "retry": 0, "pending": list(ready)}
        jdump(st, sp(run))
        st["brief"], st["edit"]["out"] = write_edit_brief(run, k, ready)
    else:
        st["phase"] = f"compile_{k}"
        jdump(st, sp(run))
        st["brief"] = write_brief(run, k)
    jdump(st, sp(run))
    return st


def do_edit(run, k):
    st = jload(sp(run))
    ed = st["edit"]
    if not os.path.exists(ed["out"]):
        return st, f"待ち: 編集役が {ed['out']} を書く(依頼書 {st['brief']})"
    doc = jload(ed["out"])
    regions = ed["regions"]
    votes_pos = split_settled(run, set(st.get("amended_ids", [])))
    failed = {}
    def rid_of(x):
        if x in ed["pending"]:
            return x
        c = [r for r in ed["pending"] if r.split("::")[0] == x]
        return c[0] if len(c) == 1 else None
    for am in doc.get("amendments", []):
        g = rid_of(am.get("branch"))
        if g is None:
            continue
        pos = {i: votes_pos[i] for i in regions.get(g, []) if i in votes_pos}
        problems, report = amend_gate(run, am, pos, load_policy(os.path.join(rd(run), "policies", f"{st['accepted'][-1]}.py")),
                                      g.split("::")[0])
        st.setdefault("amend_gate_log", []).append({"round": k, "retry": ed["retry"], "branch": g, "text": am.get("text"),
                                                    "when": am.get("when"), "action": am.get("action"),
                                                    "problems": problems, "report": report})
        if problems:
            failed[g] = "\n".join(problems) + f"\n覆った範囲: {report}"
        else:
            aid = f"A{len(st['amendments']) + 1}"
            st["amendments"].append({"id": aid, "text": am["text"], "when": am["when"], "action": am["action"],
                                     "branch": g, "round": k, "positives": regions[g], "report": report})
            st.setdefault("amended_ids", []).extend(regions[g])
            ed["pending"].remove(g)
    for sk in doc.get("skip", []):
        g = rid_of(sk.get("branch"))
        if g is not None:
            st.setdefault("amend_gate_log", []).append({"round": k, "retry": ed["retry"], "branch": g, "skip": sk.get("why")})
            ed["pending"].remove(g)
            st.setdefault("amended_ids", []).extend(regions[g])
    left = {g: regions[g] for g in ed["pending"]}
    if left and ed["retry"] < 2:
        ed["retry"] += 1
        jdump(st, sp(run))
        st["brief"], ed["out"] = write_edit_brief(run, k, left, ed["retry"],
                                                  {g: failed.get(g, "書かれていなかった") for g in left})
        st["edit"] = ed
        jdump(st, sp(run))
        return st, f"追補の門で落ちた {sorted(left)} → やり直しの依頼書 {st['brief']}"
    for g in left:   # 3 回通らなかった穴は捨てる(正の例は使い切りにする)
        st.setdefault("amended_ids", []).extend(regions[g])
    st["log"].append(f"第{k}周の追補: " + " / ".join(f"{a['id']} {a['text']}" for a in st["amendments"] if a["round"] == k) +
                     (f"(捨てた穴: {sorted(left)})" if left else ""))
    st["phase"] = f"compile_{k}"
    st.pop("edit", None)
    jdump(st, sp(run))
    st["brief"] = write_brief(run, k)
    jdump(st, sp(run))
    return st, st["log"][-1]


def step(run):
    st = jload(sp(run))
    ph = st["phase"]
    if ph.startswith("compile_"):
        k = int(ph.split("_")[1])
        newp = os.path.join(rd(run), "policies", f"c{k}.py")
        if not os.path.exists(newp):
            return st, f"待ち: 翻訳役が {newp} を書く(依頼書 {st['brief']})"
        prevp = os.path.join(rd(run), "policies", f"{st['accepted'][-1]}.py") if st["accepted"] else None
        _states(run)
        problems = L2.gate(run, newp, prevp, amendment_grounded(run))
        st["gate_log"].append({"version": f"c{k}", "retry": st.get("retry", 0), "problems": problems})
        if problems and st.get("retry", 0) < 2:
            st["retry"] = st.get("retry", 0) + 1
            os.rename(newp, newp.replace(".py", f"_rejected{st['retry']}.py"))
            jdump(st, sp(run))
            st["brief"] = write_brief(run, k, st["retry"], "\n".join(problems))
            jdump(st, sp(run))
            return st, f"門で落ちた({len(problems)} 件)→ やり直しの依頼書 {st['brief']}"
        if problems:
            os.rename(newp, newp.replace(".py", "_rejected3.py"))
            st["log"].append(f"c{k} は門を 3 回通らず、{st['accepted'][-1]} を据え置き")
        else:
            st["accepted"].append(f"c{k}")
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
                         f"訊き直し {nrep} 件を {REPLICA_SESSIONS} 会話ずつに入れた")
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
        return do_edit(run, int(ph.split("_")[1]))
    return st, ph


def init(run, stream_seed=4):
    os.makedirs(os.path.join(rd(run), "amend"), exist_ok=True)
    st = {"run": run, "stream_seed": stream_seed, "phase": "compile_0", "accepted": [], "gate_log": [], "log": [],
          "retry": 0, "amendments": [], "replicate": [], "pending": [], "rounds": {}, "amended_ids": [], "asked": []}
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
