"""流れのラベルで、方針の食い違いと棄権を見る(直すための材料)。"""
import sys, collections
from task import load
from jitloop import policy, labels

S = {s["id"]: s for s in load("data/stream.jsonl")}
L = labels()
k = int(sys.argv[1])
d = policy(k)
rows = collections.defaultdict(list)
for i, lab in L.items():
    s = S[i]
    a, g = d(s)
    rows[g].append((a, lab, s))
keys = lambda s: {x: s[x] for x in ("hp", "enemy", "distance", "enemy_count", "enemy_hp", "allies", "potion", "arrows", "cover", "alarm", "post", "time")}
for g, rs in sorted(rows.items(), key=lambda kv: -len(kv[1])):
    wrong = [r for r in rs if r[0] is not None and r[0] != r[1]]
    ab = [r for r in rs if r[0] is None]
    print(f"== {g}: {len(rs)} labelled | answered {len(rs)-len(ab)}, wrong {len(wrong)} | abstained {len(ab)} -> judge said {dict(collections.Counter(r[1] for r in ab))}")
    for a, lab, s in (wrong + ab)[: int(sys.argv[2]) if len(sys.argv) > 2 else 12]:
        print(f"   P={a} J={lab} | " + " ".join(f"{x}={v}" for x, v in keys(s).items()))
