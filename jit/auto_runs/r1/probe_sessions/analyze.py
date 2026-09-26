"""同じ 60 状態を審判の三つの会話(A・B・C、並べ順だけ違う)に訊いた試験の集計。
    python auto_runs/r1/probe_sessions/analyze.py
組: no_arrows_cover / no_arrows_nocover(a5 の枝 no_arrows_hold、遮蔽あり・なし各 12)、
    mid_potion_no_threat(a5 の番人 12)、filler(無作為 24)。状態は task.gen(20000, 7) と gen(24, 8)。
"""
import json
import os
from collections import Counter

D = os.path.dirname(os.path.abspath(__file__))
T = json.load(open(os.path.join(D, "targets.json"), encoding="utf-8"))
A = {k: json.load(open(os.path.join(D, "outbox", f"sess{k}.json"), encoding="utf-8")) for k in "ABC"}
for grp, ids in T.items():
    print("==", grp)
    for k in "ABC":
        print("  ", k, dict(Counter(A[k][i] for i in ids)))
    print("   三会話一致", sum(len({A[k][i] for k in "ABC"}) == 1 for i in ids), "/", len(ids))
# Cochran の Q(遮蔽ありで take_cover か否か)
ids = T["no_arrows_cover"]
X = [[int(A[k][i] == "take_cover") for k in "ABC"] for i in ids]
C = [sum(r[j] for r in X) for j in range(3)]
R = [sum(r) for r in X]
N = sum(R)
Q = 2 * (3 * sum(c * c for c in C) - N * N) / (3 * N - sum(r * r for r in R))
import math
print(f"Cochran Q(遮蔽ありの take_cover)= {Q:.2f}, 自由度 2, p = {math.exp(-Q / 2):.3f}")
