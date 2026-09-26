"""保留3(200 状態、理由つきの審判の会話 3 本ずつ)の多数を的にして、方針を測る。
    python eval2.py            → holdout3/eval2.txt と eval2.json
的: 3 会話のうち 2 以上が揃った答え(揃わない状態は的から外す)。
併せて、理由なしの会話(1 本)を的にした時の一致も出す(r1 と同じ測り方)。
"""
import json
import os
import sys
import time
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from auto_loop import load_policy  # noqa: E402
from auto_loop2 import norm  # noqa: E402
from judge_protocol import parse_basis  # noqa: E402
from task import load  # noqa: E402

H3 = load(os.path.join(HERE, "data", "holdout3.jsonl"))
ids = [s["id"] for s in H3]
R = {}
for h in "ab":
    for r in (1, 2, 3):
        R.setdefault(r, {}).update(norm(json.load(open(os.path.join(HERE, "holdout3", "outbox", f"h3{h}_r{r}.json"),
                                                       encoding="utf-8"))))
P = {}
for h in "ab":
    P.update(json.load(open(os.path.join(HERE, "holdout3", "outbox", f"h3{h}_p.json"), encoding="utf-8")))
cons, unanimous, gapy = {}, set(), set()
for i in ids:
    c = Counter(R[r][i]["action"] for r in R)
    a, n = c.most_common(1)[0]
    if n >= 2:
        cons[i] = a
    if n == 3:
        unanimous.add(i)
    if sum(parse_basis(R[r][i]["basis"])[1] for r in R) >= 2:
        gapy.add(i)

POL = [("P6", os.path.join(HERE, "policies", "p6.py"))]
for run, pre in (("r1", "a"), ("r2", "b"), ("r3", "c")):
    st = os.path.join(HERE, "auto_runs", run, "state.json")
    if os.path.exists(st):
        for v in json.load(open(st, encoding="utf-8"))["accepted"]:
            POL.append((f"{run}:{v}", os.path.join(HERE, "auto_runs", run, "policies", f"{v}.py")))

out = {"n": len(ids), "consensus": len(cons), "unanimous": len(unanimous), "gap_states": len(gapy), "policies": {}}
lines = [f"保留3: {len(ids)} 状態、多数あり {len(cons)}、全会一致 {len(unanimous)}、2 会話以上が gap と答えた状態 {len(gapy)}",
         "", "方針           覆い    多数との一致  全会一致の所  gap の所   理由なし会話との一致  棄権を審判へ  1 回",
         ]
for name, path in POL:
    d = load_policy(path)
    t = time.perf_counter()
    r = {i: d(s)[0] for i, s in zip(ids, H3)}
    us = (time.perf_counter() - t) / len(ids) * 1e6
    cov = [i for i in ids if r[i] is not None]
    cc = [i for i in cov if i in cons]
    m = {"coverage": len(cov) / len(ids),
         "agree_consensus": sum(r[i] == cons[i] for i in cc) / max(len(cc), 1),
         "agree_unanimous": sum(r[i] == cons[i] for i in cc if i in unanimous) / max(sum(1 for i in cc if i in unanimous), 1),
         "agree_gap": (sum(r[i] == cons[i] for i in cc if i in gapy) / max(sum(1 for i in cc if i in gapy), 1)),
         "n_gap_covered": sum(1 for i in cc if i in gapy),
         "agree_plain": sum(r[i] == P[i] for i in cov) / max(len(cov), 1),
         "system_consensus": sum((r[i] == cons[i]) if r[i] is not None else True for i in cons) / len(cons),
         "us": us}
    out["policies"][name] = m
    lines.append(f"{name:<12} {m['coverage']:.3f}   {m['agree_consensus']:.3f}        {m['agree_unanimous']:.3f}"
                 f"        {m['agree_gap']:.3f}({m['n_gap_covered']:>2})  {m['agree_plain']:.3f}"
                 f"               {m['system_consensus']:.3f}        {m['us']:.2f}µs")
# 審判の側の数字
loo = []
for r in R:
    ok = n = 0
    for i in ids:
        o = [R[q][i]["action"] for q in R if q != r]
        if o[0] == o[1]:
            n += 1
            ok += R[r][i]["action"] == o[0]
    loo.append(ok / n)
out["judge_loo"] = loo
out["plain_vs_consensus"] = sum(P[i] == cons[i] for i in cons) / len(cons)
lines += ["", f"審判: 理由つきの会話が、他の二つが揃った時にそれと一致 {[round(x, 3) for x in loo]}",
          f"      理由なしの会話と多数の一致 {out['plain_vs_consensus']:.3f}",
          f"      gap の状態の全会一致 {len(gapy & unanimous)}/{len(gapy)}、gap でない状態の全会一致 "
          f"{len(unanimous - gapy)}/{len(ids) - len(gapy)}"]
txt = "\n".join(lines)
print(txt)
open(os.path.join(HERE, "holdout3", "eval2.txt"), "w", encoding="utf-8").write(txt + "\n")
json.dump(out, open(os.path.join(HERE, "holdout3", "eval2.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
