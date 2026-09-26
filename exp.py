"""実験の条件。python3 exp.py <条件名>  → results/<条件名>.npz と .json"""
import json
import os
import sys
import time
import numpy as np
from world import World, Env, make_pool, describe, FULL
from spine import Spine, HDCMatcher
from run import learn, frozen, brain_only

A, B = (14, 4), (10, 6)          # (餌の数, 敵の数)
TA, TB, TF = 20000, 10000, 5000  # 地図 A で学ぶ歩数, 地図 B で学ぶ歩数, 凍結試験の歩数
os.makedirs("results", exist_ok=True)


def maps():
    return World(20, 0.12, seed=1), World(20, 0.22, seed=2)


def matchers():
    return {
        "hs10k": HDCMatcher(10000, sparse=True, codebook="orth", seed=3),
        "hd10k_o": HDCMatcher(10000, sparse=False, codebook="orth", seed=3),
        "hd10k_r": HDCMatcher(10000, sparse=False, codebook="rand", seed=3),
        "hs1k_o": HDCMatcher(1024, sparse=True, codebook="orth", seed=3),
        "hs1k_r": HDCMatcher(1024, sparse=True, codebook="rand", seed=3),
        "hs2k_o": HDCMatcher(2048, sparse=True, codebook="orth", seed=3),
    }


def ledger(sp, pool):
    bits = (1 << pool).astype(np.uint8)
    inhibits = [[] for _ in range(sp.n)]
    for r in range(sp.n):
        for i in sp.inhib_by[r]:
            inhibits[i].append(r)
    rows = []
    for i in range(sp.n):
        cover = float((((sp.masks[i][None, :] & bits) != 0).sum(1) >= 25 - sp.tol[i]).mean())
        rows.append({"id": i, "rule": describe(sp.masks[i], int(sp.act[i])),
                     "act": int(sp.act[i]), "n_constrained": int((sp.masks[i] != FULL).sum()),
                     "counts": sp.counts[i].tolist(), "inhibits": inhibits[i],
                     "inhibited_by": sorted(int(x) for x in sp.inhib_by[i]),
                     "pool_cover": cover, **sp.meta[i]})
    return rows


def dump(name, arrays, info):
    np.savez_compressed(f"results/{name}.npz", **arrays)
    with open(f"results/{name}.json", "w") as f:
        json.dump(info, f, ensure_ascii=False, default=float)


def flat(prefix, rec, sh=None, tm=None):
    out = {f"{prefix}_{k}": v for k, v in rec.items()}
    for k, v in (sh or {}).items():
        out[f"{prefix}_sh_{k}"] = v
    if tm:
        out[f"{prefix}_tsym"], out[f"{prefix}_tdrv"] = tm["sym"], tm["drv"]
        out[f"{prefix}_texp"] = np.array(tm["explain"])
    return out


def exp_spine(name, driver, mode="anchor", tol=0, with_b=True):
    t0 = time.time()
    wA, wB = maps()
    poolA, poolB = make_pool(wA, *A, seed=11), make_pool(wB, *B, seed=12)
    evalpool = make_pool(wA, *A, seed=13)
    sp = Spine()
    shadows = []
    if driver != "sym":
        for k, m in matchers().items():
            sp.attach(k, m)
        shadows = [k for k in sp.matchers if k != driver]
    rng = np.random.default_rng(200)
    recA, shA, tmA, written = learn(sp, Env(wA, *A, seed=100), poolA, TA, rng, mode=mode,
                                    tol=tol, driver=driver, shadows=shadows)
    arrays = flat("A", recA, shA, tmA)
    hows = ("sym",) if driver == "sym" else ("sym", driver)
    fa, ta = frozen(sp, Env(wA, *A, seed=300), TF, hows)
    fb, tb = frozen(sp, Env(wB, *B, seed=301), TF, hows)
    for h in hows:
        arrays[f"fA_{h}"], arrays[f"fB_{h}"] = fa[h], fb[h]
    arrays["fA_truth"], arrays["fB_truth"] = ta, tb
    info = {"ledger_A": ledger(sp, evalpool)}
    if with_b:
        rngB = np.random.default_rng(201)
        recB, shB, tmB, _ = learn(sp, Env(wB, *B, seed=400), poolB, TB, rngB, mode=mode,
                                  tol=tol, driver=driver, shadows=shadows, t0=TA, written=written)
        arrays.update(flat("B", recB, shB, tmB))
        info["ledger_AB"] = ledger(sp, evalpool)
    if driver != "sym":
        info["key_terms"] = {k: m.key_terms for k, m in sp.matchers.items()}
    info["seconds"] = time.time() - t0
    dump(name, arrays, info)


def exp_scratch_b():
    t0 = time.time()
    _, wB = maps()
    poolB = make_pool(wB, *B, seed=12)
    sp = Spine()
    rec, _, tm, _ = learn(sp, Env(wB, *B, seed=400), poolB, TB, np.random.default_rng(201))
    dump("scratchB", flat("B", rec, None, tm), {"seconds": time.time() - t0})


def exp_brain():
    wA, wB = maps()
    dump("brain", {"A": brain_only(Env(wA, *A, seed=100), TA),
                   "B": brain_only(Env(wB, *B, seed=400), TB)}, {})


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "main":
        exp_spine("main", "hs10k")
    elif c == "sym_anchor":
        exp_spine("sym_anchor", "sym")
    elif c == "necessity":
        exp_spine("necessity", "sym", mode="necessity", with_b=False)
    elif c == "noisy":
        exp_spine("noisy", "sym", mode="noisy", with_b=False)
    elif c == "exact":
        exp_spine("exact", "sym", mode="full", tol=0, with_b=False)
    elif c == "sim":
        exp_spine("sim", "sym", mode="sim", tol=2, with_b=False)
    elif c == "scratchB":
        exp_scratch_b()
    elif c == "brain":
        exp_brain()
    elif c == "smoke":
        import exp as _e
        _e.TA, _e.TB, _e.TF = 300, 200, 200
        _e.exp_spine("smoke", "hs10k")
        print("smoke ok")
