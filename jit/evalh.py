"""保留での集計だけを出す(個々の食い違いは見ない)。"""
import json, sys, time, collections
from task import load
from jitloop import policy, answers

H = load("data/holdout.jsonl")
J = {}
for k in range(3):
    J.update(answers(f"holdout_{k}"))


def evaluate(k):
    d = policy(k)
    t = time.perf_counter()
    out = [d(s) for s in H]
    us = (time.perf_counter() - t) / len(H) * 1e6
    cov = [(s, a) for s, (a, g) in zip(H, out) if a is not None]
    agree = sum(J[s["id"]] == a for s, a in cov)
    return {"policy": k, "coverage": len(cov) / len(H), "agree_covered": agree / max(len(cov), 1),
            "system_agree_if_escalate": (agree + len(H) - len(cov)) / len(H), "us_per_decision": us}


if __name__ == "__main__":
    for k in sys.argv[1:]:
        print(json.dumps(evaluate(int(k))))
