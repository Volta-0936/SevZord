"""指示文の穴を探す。審判の答えが割れる所を、方針の枝ごとに、次の二つに分ける。

  状態で説明できる割れ: 枝の中で、ある一つの項目の値で答えが分かれる → 翻訳役が枝を分ければ済む
  会話で説明できる割れ: 同じような状態でも、審判の会話(1 回の依頼 = 1 つのファイル)ごとに答えが揃って違う
                        → 審判は「その会話の中で決めた約束」で答えている。指示文に一文足りない印

審判の答えは、これまでの全ての会話(手の輪・自動の輪・無作為・保留1・保留2・再現性)から集める。

    python spec_gaps.py r1            → 画面と auto_runs/r1/spec_gaps.txt
"""
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from auto_loop import load_policy, rd, fmt  # noqa: E402
from task import gen, load  # noqa: E402

run = sys.argv[1] if len(sys.argv) > 1 else "r1"
st = json.load(open(os.path.join(rd(run), "state.json"), encoding="utf-8"))
decide = load_policy(os.path.join(rd(run), "policies", f"{st['accepted'][-1]}.py"))

# 状態: id の頭の数字が gen の種
STATES = {}
for seed, n in ((1, 300), (2, 3000), (3, 300), (st["stream_seed"], 2500)):
    for s in gen(n, seed):
        STATES[s["id"]] = s

# 会話 = 審判の答えのファイル一つ
SESS = {}
for d, tag in ((os.path.join(HERE, "judge_outbox"), "手"), (os.path.join(rd(run), "judge_outbox"), run)):
    for f in sorted(os.listdir(d)):
        if f.endswith(".json"):
            SESS[f"{tag}:{f[:-5]}"] = json.load(open(os.path.join(d, f), encoding="utf-8"))

rows = []   # (枝, 会話, 状態, 答え)
for sname, ans in SESS.items():
    for i, lab in ans.items():
        if i in STATES:
            a, g = decide(STATES[i])
            rows.append((g.split(":")[0], sname, STATES[i], lab))

FEATS = ("hp", "enemy", "distance", "enemy_count", "enemy_hp", "allies", "potion", "arrows", "cover", "alarm",
         "post", "time")


def stump(items):
    """一つの項目の一つの切れ目で、答えを最もよく分けるもの(両側に 3 件以上)。"""
    labs = [l for _, l in items]
    base = Counter(labs).most_common(1)[0][1]
    best = (base, None)
    for f in FEATS:
        vals = sorted({s[f] for s, _ in items if s[f] is not None}, key=lambda v: (str(type(v)), v))
        for v in vals:
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                side = [(s[f] is not None and s[f] <= v) for s, _ in items]
                name = f"{f}<={v}"
            else:
                side = [s[f] == v for s, _ in items]
                name = f"{f}={v}"
            L = [l for (s, l), x in zip(items, side) if x]
            R = [l for (s, l), x in zip(items, side) if not x]
            if len(L) < 3 or len(R) < 3:
                continue
            sc = Counter(L).most_common(1)[0][1] + Counter(R).most_common(1)[0][1]
            if sc > best[0]:
                best = (sc, f"{name} → {Counter(L).most_common(1)[0][0]} / 他 → {Counter(R).most_common(1)[0][0]}")
    return best


def session_loo(items_s):
    """同じ会話の他の答えの多数で当てる(一つ抜き)。当てた数と、使えた数。"""
    by = defaultdict(list)
    for sname, l in items_s:
        by[sname].append(l)
    hit = used = 0
    for sname, l in items_s:
        others = list(by[sname])
        others.remove(l)
        if others:
            used += 1
            hit += Counter(others).most_common(1)[0][0] == l
    return hit, used


by = defaultdict(list)
for g, sname, s, lab in rows:
    by[g].append((sname, s, lab))

out = []
for g, rs in sorted(by.items(), key=lambda kv: -len(kv[1])):
    labs = Counter(l for _, _, l in rs)
    top, ntop = labs.most_common(1)[0]
    purity = ntop / len(rs)
    if len(rs) < 6 or purity >= 0.9:
        continue
    sc, rule = stump([(s, l) for _, s, l in rs])
    hit, used = session_loo([(sn, l) for sn, _, l in rs])
    base_used = sum(1 for sn, _, l in rs if l == top)  # 目安
    sess = defaultdict(Counter)
    for sn, _, l in rs:
        sess[sn][l] += 1
    split_sessions = [(sn, dict(c)) for sn, c in sess.items() if sum(c.values()) >= 2]
    out.append({"branch": g, "n": len(rs), "answers": dict(labs), "purity": purity,
                "stump_acc": sc / len(rs), "stump": rule,
                "session_loo_acc": hit / used if used else None, "session_used": used,
                "sessions": split_sessions})

lines = [f"方針 {st['accepted'][-1]} の枝で、審判の答えが 90% 未満しか揃わない所(会話 {len(SESS)} 本、答え {len(rows)} 件)", ""]
for o in out:
    lines.append(f"■ {o['branch']}  {o['n']} 件  {o['answers']}  多数の割合 {o['purity']:.2f}")
    lines.append(f"   一つの項目で分けると {o['stump_acc']:.2f}  ({o['stump']})")
    if o["session_loo_acc"] is not None:
        lines.append(f"   同じ会話の他の答えで当てると {o['session_loo_acc']:.2f}  (当てられた {o['session_used']} 件)")
    lines.append("   会話ごと: " + "; ".join(f"{sn} {c}" for sn, c in o["sessions"]))
    lines.append("")
txt = "\n".join(lines)
print(txt)
open(os.path.join(rd(run), "spec_gaps.txt"), "w", encoding="utf-8").write(txt + "\n")
json.dump(out, open(os.path.join(rd(run), "spec_gaps.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
