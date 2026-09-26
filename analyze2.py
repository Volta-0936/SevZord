"""v1 の集計。python3 analyze2.py"""
import glob
import json
import numpy as np
from collections import defaultdict


def auc(score, y):
    y = y.astype(bool)
    if y.all() or (~y).all():
        return float("nan")
    order = np.argsort(score, kind="mergesort")
    ranks = np.empty(len(score))
    ranks[order] = np.arange(1, len(score) + 1)
    # 同順位の平均
    s = score[order]
    i = 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and s[j + 1] == s[i]:
            j += 1
        ranks[order[i:j + 1]] = (i + j + 2) / 2
        i = j + 1
    n1, n0 = y.sum(), (~y).sum()
    return float((ranks[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def ece(p_err, y, bins=(0, .002, .005, .01, .02, .05, .1, .2, 1.01)):
    tot, out = 0.0, []
    for lo, hi in zip(bins[:-1], bins[1:]):
        m = (p_err >= lo) & (p_err < hi)
        if m.any():
            tot += m.sum() * abs(p_err[m].mean() - y[m].mean())
            out.append((lo, hi, int(m.sum()), float(p_err[m].mean()), float(y[m].mean())))
    return tot / len(y), out


def one(path):
    d = np.load(path)
    info = json.load(open(path.replace(".npz", ".json")))
    T = len(d["cause"])
    dec = d["decided"].astype(bool)
    wrong = d["wrong"].astype(bool) & dec
    audited = d["cause"] == 3
    reached = wrong & ~audited          # 身体に届いた誤り
    e = d["e"][dec]
    y = wrong[dec]
    E, table = ece(e, y)
    L = slice(T - 5000, T)
    cause = d["cause"]
    return {
        "calls": int(d["calls"].sum()),
        "impasse": int(((cause == 1) | (cause == 2)).sum()),
        "impasse_first5000": int(((cause[:5000] == 1) | (cause[:5000] == 2)).sum()),
        "audit_calls": int((cause == 3).sum()),
        "pain_calls": int(d["calls"][cause == 4].sum()),
        "wrong": int(wrong.sum()), "reached": int(reached.sum()),
        "caught": int(d["caught"].sum()),
        "err_late": float(wrong[L][dec[L]].mean()),
        "reached_late": int(reached[L].sum()),
        "mean_e": float(e.mean()), "err_rate": float(y.mean()),
        "ece": float(E), "auc": auc(e, y), "rel": table,
        "contact_per1000": float(d["contact"].mean() * 1000),
        "nref": int(d["nref"][-1]), **info,
    }


def main():
    by = defaultdict(list)
    for p in sorted(glob.glob("results2/*.npz")):
        name = p.split("/")[-1].rsplit("_", 1)[0]
        by[name].append(one(p))
    S = {}
    for name, runs in by.items():
        keys = [k for k in runs[0] if isinstance(runs[0][k], (int, float)) and not isinstance(runs[0][k], bool)]
        S[name] = {k: [r[k] for r in runs] for k in keys}
        S[name]["_rel_seed0"] = runs[0]["rel"]
        for k in ("move_reflexes", "move_frame_restricted", "exceptions", "labels"):
            if k in runs[0]:
                S[name][k] = [r[k] for r in runs]
    json.dump(S, open("results2/summary.json", "w"), indent=1)
    return S


if __name__ == "__main__":
    S = main()
    cols = ["calls", "impasse_first5000", "audit_calls", "pain_calls", "wrong", "caught",
            "reached", "reached_late", "err_late", "mean_e", "err_rate", "ece", "auc",
            "contact_per1000", "nref"]
    for name, s in S.items():
        print("==", name, "(seeds:", len(s["calls"]), ")")
        for k in cols:
            v = np.array(s[k], float)
            print(f"   {k:18s} mean {v.mean():10.4f}   per seed {np.round(v, 4).tolist()}")
        for k in ("move_reflexes", "move_frame_restricted", "exceptions", "labels"):
            if k in s:
                print(f"   {k:18s} {s[k]}")
