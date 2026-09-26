"""結果の集計。python3 analyze.py → 標準出力と results/summary.json"""
import json
import os
import numpy as np
from collections import Counter

W = 500
R = "results"


def load(name):
    p = f"{R}/{name}.npz"
    if not os.path.exists(p):
        return None, None
    d = np.load(p)
    j = f"{R}/{name}.json"
    return d, (json.load(open(j)) if os.path.exists(j) else {})


def windows(x, w=W):
    n = len(x) // w
    return x[: n * w].reshape(n, w).mean(1)


def phase(d, P):
    esc = d[f"{P}_cause"] > 0
    dec = ~esc
    ok = d[f"{P}_act"] == d[f"{P}_truth"]
    seen = d[f"{P}_seen"].astype(bool)
    T = len(esc)
    L = slice(T - 5000, T) if T >= 10000 else slice(T // 2, T)
    out = {
        "esc_first500": float(esc[:500].mean()),
        "esc_last2000": float(esc[-2000:].mean()),
        "impasse_last2000": float((d[f"{P}_cause"][-2000:] % 3 != 0).mean()),
        "none_last2000": float((d[f"{P}_cause"][-2000:] == 1).mean()),
        "conflict_last2000": float((d[f"{P}_cause"][-2000:] == 2).mean()),
        "audit_last2000": float((d[f"{P}_cause"][-2000:] == 3).mean()),
        "brain_calls_total": int(esc.sum()),
        "nref_end": int(d[f"{P}_nref"][-1]),
        "acc_decided_late": float(ok[L][dec[L]].mean()),
        "unseen_frac_late": float((~seen[L][dec[L]]).mean()),
        "acc_unseen_late": float(ok[L][dec[L] & ~seen[L]].mean()),
        "acc_seen_late": float(ok[L][dec[L] & seen[L]].mean()) if (dec[L] & seen[L]).any() else None,
        "audit_wrong_total": int(d[f"{P}_audit_wrong"].sum()),
        "decided_wrong_late": int((~ok[L] & dec[L]).sum()),
        "food_per1000": float(d[f"{P}_ate"].mean() * 1000),
        "contact_per1000": float(d[f"{P}_contact"].mean() * 1000),
        "faint_per1000": float(d[f"{P}_faint"].mean() * 1000),
        "esc_curve": windows(esc.astype(float)).round(4).tolist(),
        "err_curve": [float(np.mean(~ok[i:i + W][dec[i:i + W]])) if dec[i:i + W].any() else None
                      for i in range(0, T - W + 1, W)],
        "nref_curve": d[f"{P}_nref"][W - 1::W].tolist(),
    }
    ch = d[f"{P}_changed"]
    moved = ch > 0
    out["changed_mean_when_changed"] = float(ch[moved].mean())
    out["changed_frac_ge10_when_changed"] = float((ch[moved] >= 10).mean())
    if f"{P}_texp" in d.files and len(d[f"{P}_texp"]):
        out["explain_ms_median"] = float(np.median(d[f"{P}_texp"]) * 1e3)
        out["brain_calls_per_explain"] = float(d[f"{P}_calls"][d[f"{P}_calls"] > 0].mean())
    out["sym_us_median"] = float(np.median(d[f"{P}_tsym"]) * 1e6)
    td = d[f"{P}_tdrv"]
    if (td > 0).any():
        nref = d[f"{P}_nref"]
        bins = {}
        for lo, hi in ((0, 100), (100, 200), (200, 400), (400, 800), (800, 1600), (1600, 5000)):
            m = (nref >= lo) & (nref < hi) & (td > 0)
            if m.any():
                bins[f"{lo}-{hi}"] = float(np.median(td[m]) * 1e3)
        out["drv_ms_by_nref"] = bins
    return out


def crosstalk(d, P, ref=f"sym"):
    sym = d[f"{P}_sym"]
    res = {}
    keys = [k for k in d.files if k.startswith(f"{P}_sh_")] + [f"{P}_dec"]
    for k in keys:
        x = d[k]
        dis = x != sym
        sym_dec, x_dec = sym < 6, x < 6
        name = k.replace(f"{P}_sh_", "").replace(f"{P}_dec", "driver")
        nref = d[f"{P}_nref"]
        by = {}
        for lo, hi in ((0, 100), (100, 200), (200, 400), (400, 800), (800, 1600)):
            m = (nref >= lo) & (nref < hi)
            if m.any():
                by[f"{lo}-{hi}"] = float(dis[m].mean())
        res[name] = {
            "disagree": float(dis.mean()),
            "false_fire(decides,sym_impasse)": float((x_dec & ~sym_dec).mean()),
            "miss(impasse,sym_decides)": float((~x_dec & sym_dec).mean()),
            "wrong_action(both_decide)": float((x_dec & sym_dec & (x != sym)).mean()),
            "by_nref": by,
        }
    return res


def frozen(d, h):
    out = {}
    for M in ("A", "B"):
        k = f"f{M}_{h}"
        if k not in d.files:
            continue
        x, t = d[k], d[f"f{M}_truth"]
        dec = x < 6
        out[M] = {"coverage": float(dec.mean()), "acc": float((x[dec] == t[dec]).mean()),
                  "none": float((x == 6).mean()), "conflict": float((x == 7).mean())}
    return out


def ledger_stats(rows):
    if not rows:
        return {}
    nc = np.array([r["n_constrained"] for r in rows])
    acts = Counter(r["act"] for r in rows)
    fires = np.array([r["fires"] for r in rows])
    top = sorted(rows, key=lambda r: -r["fires"])[:8]
    tp = [(r["true_ok"], r["true_bad"]) for r in rows]
    cover = np.array([r["pool_cover"] for r in rows])
    return {
        "n": len(rows), "constrained_mean": float(nc.mean()), "constrained_median": float(np.median(nc)),
        "acts": {k: acts[k] for k in sorted(acts)},
        "exceptions": int(sum(1 for r in rows if r["over"])),
        "with_inhibition_links": int(sum(1 for r in rows if r["inhibits"])),
        "never_fired": int((fires == 0).sum()),
        "fires_top8_share": float(fires[np.argsort(-fires)[:8]].sum() / max(fires.sum(), 1)),
        "pool_cover_mean": float(cover.mean()), "pool_cover_median": float(np.median(cover)),
        "top8": [{"id": r["id"], "fires": r["fires"], "born": r["born"], "cause": r["cause"],
                  "true_prec": r["true_ok"] / max(r["true_ok"] + r["true_bad"], 1),
                  "cover": r["pool_cover"], "rule": r["rule"]} for r in top],
        "first10": [(r["born"], r["act"], r["cause"]) for r in rows[:10]],
        "explore_reflexes_born_before_2000": int(sum(1 for r in rows if r["act"] == 5 and r["born"] < 2000)),
        "reflexes_born_before_2000": int(sum(1 for r in rows if r["born"] < 2000)),
        "true_prec_weighted": float(sum(a for a, b in tp) / max(sum(a + b for a, b in tp), 1)),
    }


def main():
    S = {}
    for name in ("main", "sym_anchor", "exact", "sim", "necessity", "noisy"):
        d, info = load(name)
        if d is None:
            continue
        s = {"A": phase(d, "A")}
        if "B_cause" in d.files:
            s["B"] = phase(d, "B")
        s["frozen_sym"] = frozen(d, "sym")
        if name == "main":
            s["frozen_driver"] = frozen(d, "hs10k")
            s["crosstalk_A"] = crosstalk(d, "A")
            s["crosstalk_B"] = crosstalk(d, "B")
            kt = info.get("key_terms", {})
            s["key_terms_median"] = {k: float(np.median(v)) for k, v in kt.items()}
        s["ledger_A"] = ledger_stats(info.get("ledger_A"))
        s["seconds"] = info.get("seconds")
        S[name] = s
    d, _ = load("scratchB")
    if d is not None:
        S["scratchB"] = {"B": phase(d, "B")}
    d, _ = load("brain")
    if d is not None:
        S["brain"] = {M: {"food_per1000": float(d[M][:, 0].mean() * 1000),
                          "contact_per1000": float(d[M][:, 1].mean() * 1000),
                          "faint_per1000": float(d[M][:, 2].mean() * 1000)} for M in ("A", "B")}
    json.dump(S, open(f"{R}/summary.json", "w"), ensure_ascii=False, indent=1)
    return S


if __name__ == "__main__":
    S = main()
    for name, s in S.items():
        print("=" * 20, name)
        for P in ("A", "B"):
            if P in s:
                x = {k: v for k, v in s[P].items() if not k.endswith("curve")}
                print(P, json.dumps(x, ensure_ascii=False))
        for k in ("frozen_sym", "frozen_driver", "crosstalk_A", "key_terms_median"):
            if k in s:
                print(k, json.dumps(s[k], ensure_ascii=False))
        if "ledger_A" in s:
            L = {k: v for k, v in s["ledger_A"].items() if k != "top8"}
            print("ledger_A", json.dumps(L, ensure_ascii=False))
