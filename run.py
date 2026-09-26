"""実験の走り手。脊髄が決め、決められない時と時々の抜き打ちだけ脳に上げる。"""
import time
import numpy as np
from world import brain, explain, NCELL, EN_ROLE
from spine import Spine

CAUSE = {"none": 1, "conflict": 2, "audit": 3}
STAT = {"none": 6, "conflict": 7}


def code(dec, stat):
    return dec if stat == "ok" else STAT[stat]


def learn(spine, env, pool, steps, rng, mode="anchor", tol=0, eps=0.05, driver="sym",
          shadows=(), t0=0, written=None, pool_every=10):
    written = set() if written is None else written
    T = steps
    rec = {k: np.zeros(T, np.int32) for k in
           ("dec", "truth", "act", "cause", "nref", "seen", "ate", "contact", "faint",
            "changed", "sym", "audit_wrong", "calls")}
    sh = {name: np.zeros(T, np.int8) for name in shadows}
    tm = {"sym": np.zeros(T), "drv": np.zeros(T), "explain": []}
    prev = None
    for t in range(T):
        obs = env.obs()
        a_true = brain(obs)
        rec["truth"][t] = a_true
        rec["changed"][t] = -1 if prev is None else int((obs[:NCELL] != prev[:NCELL]).sum())
        prev = obs
        t1 = time.perf_counter()
        sdec, sstat, skeep = spine.decide(obs, "sym")
        tm["sym"][t] = time.perf_counter() - t1
        rec["sym"][t] = code(sdec, sstat)
        for name in shadows:
            d, s, _ = spine.decide(obs, name)
            sh[name][t] = code(d, s)
        if driver == "sym":
            dec, stat, keep = sdec, sstat, skeep
        else:
            t1 = time.perf_counter()
            dec, stat, keep = spine.decide(obs, driver)
            tm["drv"][t] = time.perf_counter() - t1
        rec["dec"][t] = code(dec, stat)
        rec["nref"][t] = spine.n
        rec["seen"][t] = tuple(obs) in written
        esc = stat != "ok" or rng.random() < eps
        if esc:
            cause = stat if stat != "ok" else "audit"
            rec["cause"][t] = CAUSE[cause]
            act = a_true
            wrong = [r for r in keep if spine.act[r] != a_true]
            if cause == "audit":
                for r in keep:
                    spine.meta[r]["aud"] += 1
                    spine.meta[r]["aud_bad"] += int(spine.act[r] != a_true)
                rec["audit_wrong"][t] = int(bool(wrong))
            if cause != "audit" or wrong:
                t1 = time.perf_counter()
                mask, prec, calls = explain(obs, a_true, pool, rng, mode=mode)
                tm["explain"].append(time.perf_counter() - t1)
                rec["calls"][t] = calls
                if tol == 0:  # 例外は、誤った反射より狭くする(既定の階層の上に載せる)
                    for r in wrong:  # 近さで照合する全状態キャッシュには階層が無いので行わない
                        mask &= spine.masks[r]
                spine.write(mask, a_true, tol, meta={
                    "born": t0 + t, "cause": cause, "prec": prec, "fires": 0,
                    "true_ok": 0, "true_bad": 0, "aud": 0, "aud_bad": 0,
                    "over": [int(r) for r in wrong]})
            written.add(tuple(obs))
        else:
            act = dec
            for r in keep:
                m = spine.meta[r]
                m["fires"] += 1
                m["true_ok" if spine.act[r] == a_true else "true_bad"] += 1
        rec["act"][t] = act
        ev = env.step(act)
        for k in ("ate", "contact", "faint"):
            rec[k][t] = ev[k]
        if t % pool_every == 0:
            pool[rng.integers(len(pool))] = obs
    return rec, sh, tm, written


def frozen(spine, env, steps, hows=("sym",)):
    """脳が身体を動かし、脊髄は書き込まずに答えだけ出す(一般化の試験)。"""
    out = {h: np.zeros(steps, np.int8) for h in hows}
    truth = np.zeros(steps, np.int8)
    for t in range(steps):
        obs = env.obs()
        a = brain(obs)
        truth[t] = a
        for h in hows:
            d, s, _ = spine.decide(obs, h)
            out[h][t] = code(d, s)
        env.step(a)
    return out, truth


def brain_only(env, steps):
    ev = np.zeros((steps, 3), np.int32)
    for t in range(steps):
        e = env.step(brain(env.obs()))
        ev[t] = e["ate"], e["contact"], e["faint"]
    return ev
