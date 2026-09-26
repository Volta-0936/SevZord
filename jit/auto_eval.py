"""自動の輪の結果を、保留2(300 件、審判の答えつき)で一度だけ測る。
比べる物: 手で直した P0..P6、同じラベル数で学ばせた模型、Jev(日本語と英語の指示文)。

    python auto_eval.py r1        → auto_runs/r1/eval.json と画面の表
"""
import json
import os
import sys
import time
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from auto_loop import load_policy, labels as run_labels, stream, rd, SEG  # noqa: E402
from task import load  # noqa: E402

run = sys.argv[1] if len(sys.argv) > 1 else "r1"
H2 = load(os.path.join(HERE, "data", "holdout2.jsonl"))
J2 = {}
for i in range(3):
    J2.update(json.load(open(os.path.join(HERE, "judge_outbox", f"holdout2_{i}.json"), encoding="utf-8")))
ids = [s["id"] for s in H2]
y = np.array([J2[i] for i in ids])
st = json.load(open(os.path.join(rd(run), "state.json"), encoding="utf-8"))
out = {"run": run, "accepted": st["accepted"], "gate_log": st["gate_log"], "policies": {}, "rounds": []}


def measure(decide):
    t = time.perf_counter()
    r = [decide(s) for s in H2]
    us = (time.perf_counter() - t) / len(H2) * 1e6
    a = np.array([x[0] if x[0] is not None else "" for x in r])
    cov = a != ""
    ok = a == y
    return {"coverage": float(cov.mean()), "agree_covered": float(ok[cov].mean()),
            "system_agree": float((ok | ~cov).mean()), "us": us, "n_branches": len({x[1] for x in r})}, a


ans = {}
for v in st["accepted"]:
    out["policies"][v], ans[v] = measure(load_policy(os.path.join(rd(run), "policies", f"{v}.py")))
for k in (0, 6):
    out["policies"][f"P{k}"], ans[f"P{k}"] = measure(load_policy(os.path.join(HERE, "policies", f"p{k}.py")))

# 周ごとの流れ(その周の区間で、前の方針がどれだけ棄権し、監査でどれだけ一致したか)
S = stream(run)
L = run_labels(run)
for k in range(1, len(st["accepted"])):
    d = load_policy(os.path.join(rd(run), "policies", f"{st['accepted'][k - 1]}.py"))
    seg = S[(k - 1) * SEG:k * SEG]
    r = [(s["id"], d(s)[0]) for s in seg]
    aud = [(i, a) for i, a in r if a is not None and i in L]
    out["rounds"].append({"round": k, "policy": st["accepted"][k - 1],
                          "abstain_rate": sum(a is None for _, a in r) / len(r),
                          "labels": sum(1 for i, _ in r if i in L),
                          "audits": len(aud), "audit_agree": sum(a == L[i] for i, a in aud) / max(len(aud), 1)})
out["labels_total"] = len(L)

# Jev(同じ 300 件)
final = st["accepted"][-1]
fa = ans[final]
fcov = fa != ""
for lang, fn in (("ja", "jev_holdout2.json"), ("en", "jev_holdout2_en.json")):
    p = os.path.join(HERE, fn)
    if not os.path.exists(p):
        continue
    J = json.load(open(p, encoding="utf-8"))
    ja = np.array([J[i]["choice"] for i in ids])
    conf = np.array([J[i]["confidence"] or 0.0 for i in ids])
    jok = ja == y
    fok = fa == y
    order = np.argsort(-conf)
    top = order[:int(fcov.sum())]
    both = fcov
    # 対にした比較(同じ状態で):翻訳が正しく Jev が誤り / その逆
    b = int((fok & ~jok & both).sum())
    c = int((~fok & jok & both).sum())
    rng = np.random.default_rng(0)
    idx = np.where(both)[0]
    diffs = []
    for _ in range(4000):
        s = rng.choice(idx, len(idx))
        diffs.append(fok[s].mean() - jok[s].mean())
    out[f"jev_{lang}"] = {
        "agree_all": float(jok.mean()),
        "agree_at_final_coverage_by_conf": float(jok[top].mean()),
        "agree_on_final_covered": float(jok[fcov].mean()),
        "agree_on_final_abstained": float(jok[~fcov].mean()) if (~fcov).any() else None,
        "final_right_jev_wrong": b, "final_wrong_jev_right": c,
        "diff_on_covered_ci95": [float(np.quantile(diffs, .025)), float(np.quantile(diffs, .975))],
        "system_final_then_jev": float(np.where(fcov, fok, jok).mean()),
        "median_ms": float(np.median([J[i]["seconds"] for i in ids]) * 1000),
        "top_confusions": Counter((J2[i], J[i]["choice"]) for i in ids if J[i]["choice"] != J2[i]).most_common(5),
    }

# 同じラベル数の模型(翻訳の輪が集めたラベルで学ばせる / 無作為に集めたラベルで学ばせる)
try:
    from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
    from sklearn.tree import DecisionTreeClassifier
    EN = ["none", "goblin", "orc", "mage", "troll"]

    def feat(s):
        return [s["hp"], *[s["enemy"] == e for e in EN], -1 if s["distance"] is None else s["distance"],
                s["enemy_count"], -1 if s["enemy_hp"] is None else s["enemy_hp"], s["allies"], s["potion"],
                s["arrows"], s["cover"], s["alarm"], s["post"] == "gate", s["post"] == "wall", s["time"] == "night"]

    Sd = {s["id"]: s for s in S}
    X2 = np.array([feat(s) for s in H2], float)
    IID, IS = {}, {s["id"]: s for s in load(os.path.join(HERE, "data", "stream.jsonl"))}
    for k in range(5):
        IID.update(json.load(open(os.path.join(HERE, "judge_outbox", f"iid_{k}.json"), encoding="utf-8")))
    sets = {"run_labels": (sorted(L), L, Sd), "iid_same_n": (sorted(IID)[:len(L)], IID, IS),
            "iid_500": (sorted(IID), IID, IS)}
    out["models"] = {}
    for name, (keys, lab, src) in sets.items():
        X = np.array([feat(src[i]) for i in keys], float)
        yy = np.array([lab[i] for i in keys])
        res = {"n": len(keys)}
        for m, clf in {"tree": DecisionTreeClassifier(random_state=0),
                       "forest": RandomForestClassifier(300, random_state=0),
                       "gbm": HistGradientBoostingClassifier(random_state=0)}.items():
            clf.fit(X, yy)
            P = clf.predict_proba(X2)
            pred = clf.classes_[P.argmax(1)]
            keep = np.argsort(-P.max(1))[:int(fcov.sum())]
            res[m] = {"agree_all": float((pred == y).mean()),
                      "agree_at_final_coverage": float((pred[keep] == y[keep]).mean())}
        out["models"][name] = res
except ImportError:
    out["models"] = "scikit-learn が無いので省いた"

json.dump(out, open(os.path.join(rd(run), "eval.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

LINES = []


def P(*a):
    LINES.append(" ".join(str(x) for x in a))
    print(*a)


P(f"走り {run}: 受け入れた版 {st['accepted']}、審判のラベル {len(L)} 件")
P("門:", [(g["version"], g["retry"], len(g["problems"])) for g in st["gate_log"]])
P("\n周  前の方針  棄権率  ラベル  監査  監査の一致")
for r in out["rounds"]:
    P(f"{r['round']:>2}  {r['policy']:>6}  {r['abstain_rate']:.3f}  {r['labels']:>5}  {r['audits']:>4}  {r['audit_agree']:.3f}")
P("\n保留2(300 件)   覆い    答えた物の一致  棄権を審判へ  枝の数  1 回の時間")
for v, m in out["policies"].items():
    P(f"{v:>4}          {m['coverage']:.3f}   {m['agree_covered']:.3f}           {m['system_agree']:.3f}"
          f"         {m['n_branches']:>3}    {m['us']:.2f} µs")
for lang in ("ja", "en"):
    j = out.get(f"jev_{lang}")
    if j:
        P(f"\nJev({lang}): 全件 {j['agree_all']:.3f}、{final} と同じ覆いに確信度で絞ると {j['agree_at_final_coverage_by_conf']:.3f}、"
              f"{final} が答えた状態で {j['agree_on_final_covered']:.3f}、{final} が棄権した状態で {j['agree_on_final_abstained']}")
        P(f"  同じ状態で {final} が正しく Jev が誤り {j['final_right_jev_wrong']} / 逆 {j['final_wrong_jev_right']}、"
              f"差の 95% 区間 {j['diff_on_covered_ci95'][0]:+.3f}〜{j['diff_on_covered_ci95'][1]:+.3f}")
        P(f"  {final} が答え、棄権は Jev に回す系: {j['system_final_then_jev']:.3f}  Jev の中央値 {j['median_ms']:.0f} ms")
if isinstance(out["models"], dict):
    P("\n模型(全件 / 同じ覆い):")
    for n, r in out["models"].items():
        P(f"  {n:<11} n={r['n']:>3}  " + "  ".join(f"{m} {r[m]['agree_all']:.3f}/{r[m]['agree_at_final_coverage']:.3f}"
                                                  for m in ("tree", "forest", "gbm")))

open(os.path.join(rd(run), "eval.txt"), "w", encoding="utf-8").write("\n".join(LINES) + "\n")
P(f"\n(この表は {os.path.join(rd(run), 'eval.txt')} にも書いた)")
