"""最終:保留2(一度だけ見る)で、P0..P6 と、同じラベル数で学ばせた模型を比べる。"""
import json, time
import numpy as np
from task import load, ACTIONS
from jitloop import policy, answers, labels
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

H2 = load("data/holdout2.jsonl")
J2 = {}
for k in range(3):
    J2.update(answers(f"holdout2_{k}"))
S = {s["id"]: s for s in load("data/stream.jsonl")}
JIT = labels()
IID = {}
for k in range(5):
    IID.update(answers(f"iid_{k}"))
EN = ["none", "goblin", "orc", "mage", "troll"]


def feat(s):
    return [s["hp"], *[s["enemy"] == e for e in EN], -1 if s["distance"] is None else s["distance"],
            s["enemy_count"], -1 if s["enemy_hp"] is None else s["enemy_hp"], s["allies"], s["potion"],
            s["arrows"], s["cover"], s["alarm"], s["post"] == "gate", s["post"] == "wall",
            s["time"] == "night"]


X2 = np.array([feat(s) for s in H2], float)
y2 = np.array([J2[s["id"]] for s in H2])
out = {"n_holdout2": len(H2), "policies": {}, "models": {}}
for k in range(7):
    d = policy(k)
    t = time.perf_counter()
    r = [d(s)[0] for s in H2]
    us = (time.perf_counter() - t) / len(H2) * 1e6
    cov = np.array([a is not None for a in r])
    agree = np.array([a == j for a, j in zip(r, y2)])
    out["policies"][f"P{k}"] = {"coverage": float(cov.mean()), "agree_covered": float(agree[cov].mean()),
                                "system_agree": float((agree | ~cov).mean()), "us": us}
p6cov = out["policies"]["P6"]["coverage"]

def fit_eval(name, ids, lab):
    X = np.array([feat(S[i]) for i in ids], float)
    y = np.array([lab[i] for i in ids])
    models = {"tree": DecisionTreeClassifier(random_state=0),
              "forest": RandomForestClassifier(300, random_state=0),
              "gbm": HistGradientBoostingClassifier(random_state=0),
              "knn": make_pipeline(StandardScaler(), KNeighborsClassifier(5)),
              "logreg": make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))}
    res = {}
    for m, clf in models.items():
        clf.fit(X, y)
        t = time.perf_counter()
        P = clf.predict_proba(X2)
        us = (time.perf_counter() - t) / len(X2) * 1e6
        pred = clf.classes_[P.argmax(1)]
        conf = P.max(1)
        thr = np.quantile(conf, 1 - p6cov)
        keep = conf >= thr
        res[m] = {"agree_all": float((pred == y2).mean()),
                  "agree_at_P6_coverage": float((pred[keep] == y2[keep]).mean()),
                  "coverage_used": float(keep.mean()), "us_batch": us}
    out["models"][name] = {"n_labels": len(ids), **res}

fit_eval("jit_labels", sorted(JIT), JIT)
fit_eval("iid_500", sorted(IID), IID)
fit_eval("iid_337", sorted(IID)[:len(JIT)], IID)
json.dump(out, open("final_eval.json", "w"), indent=1)
print(json.dumps(out["policies"], indent=0))
for n, r in out["models"].items():
    print(n, r["n_labels"], {m: (round(v["agree_all"], 3), round(v["agree_at_P6_coverage"], 3)) for m, v in r.items() if m != "n_labels"})
