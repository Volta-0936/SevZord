"""熱さの帳簿:方針の枝(番人)ごとに、流れのラベルが何件あり、審判がどう答えたか。"""
import sys, collections
from task import load
from jitloop import policy, labels

S = {s["id"]: s for s in load("data/stream.jsonl")}
L = labels()
k = int(sys.argv[1])
d = policy(k)
keys = ("hp", "enemy", "distance", "enemy_count", "enemy_hp", "allies", "potion", "arrows", "cover", "alarm", "time")
by = collections.defaultdict(list)
for i, lab in L.items():
    a, g = d(S[i])
    by[g].append((a, lab, S[i]))
print(f"labels {len(L)}")
for g, rs in sorted(by.items(), key=lambda kv: -len(kv[1])):
    a0 = rs[0][0]
    wrong = sum(1 for a, lab, _ in rs if a is not None and a != lab)
    print(f"{g:28s} n={len(rs):3d} policy={a0} wrong={wrong} judge={dict(collections.Counter(lab for _, lab, _ in rs))}")
    if a0 is None or wrong:
        for a, lab, s in rs:
            if a is None or a != lab:
                print("      J=%-14s " % lab + " ".join(f"{x}={s[x]}" for x in keys))
