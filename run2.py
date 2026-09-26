"""v1 の学習の輪。監査の規則:blind(一律)/ risk(ê に比例)/ none、と痛みの見直し。"""
from collections import deque
import numpy as np
from world import brain

CAUSE = {"none": 1, "conflict": 2, "audit": 3, "pain": 4}


def learn2(sp, env, pool, steps, rng, audit="blind", target=0.05, floor=0.01, pain=False,
           t0=0, pool_every=10, narrow=False):
    T = steps
    rec = {k: np.zeros(T, np.int32) for k in
           ("dec", "truth", "act", "cause", "nref", "wrong", "caught", "ate", "contact",
            "faint", "calls", "decided", "narrowed")}
    rec["e"] = np.full(T, np.nan)
    rec["p"] = np.zeros(T)
    rec["r"] = np.full(T, -1, np.int32)
    lam = target / 0.01
    recent = deque(maxlen=2)   # 直前の脊髄の判断(痛みの見直しのため)
    buf = deque(maxlen=2000)   # 直近の ê(閾値の監査のため)
    for t in range(T):
        obs = env.obs()
        a_true = brain(obs)
        rec["truth"][t] = a_true
        dec, stat, keep, e, r = sp.decide(obs)
        ctx = sp.context() if stat != "none" else []
        rec["dec"][t] = dec if stat == "ok" else {"none": 6, "conflict": 7}[stat]
        rec["nref"][t] = sp.n()
        if stat != "ok":
            rec["cause"][t] = CAUSE[stat]
            wrong = sp.wrongs(ctx, a_true) if stat == "conflict" else []
            c, _ = sp.learn(obs, a_true, wrong, pool, rng, t0 + t, stat)
            rec["calls"][t] = 1
            act = a_true
        else:
            rec["decided"][t] = 1
            rec["e"][t] = e
            rec["r"][t] = -1 if r is None else r
            rec["wrong"][t] = int(dec != a_true)
            if audit == "blind":
                p = target
            elif audit == "thresh":   # 見つけるための配り方:上位だけ必ず、ほかは床
                buf.append(e)
                thr = np.quantile(buf, 1 - (target - floor)) if len(buf) > 50 else 1.0
                p = 1.0 if e >= thr else floor
            elif audit == "risk":
                p = min(1.0, max(floor, lam * e))
                lam *= np.exp(0.01 * (target - p) / target)
            else:
                p = 0.0
            rec["p"][t] = p
            if rng.random() < p:
                rec["cause"][t] = CAUSE["audit"]
                rec["calls"][t] = 1
                wrong = sp.wrongs(ctx, a_true)
                if dec != a_true:
                    rec["caught"][t] = 1
                    sp.credit(keep, dec, a_true)
                    if narrow:
                        rec["narrowed"][t] = sp.narrow(obs, wrong, pool)
                    sp.learn(obs, a_true, wrong, pool, rng, t0 + t, "audit")
                else:
                    sp.credit(keep, dec, a_true)
                act = a_true
            else:
                act = dec
                recent.append((t, obs, ctx, keep, dec, a_true))
        rec["act"][t] = act
        ev = env.step(act)
        for k in ("ate", "contact", "faint"):
            rec[k][t] = ev[k]
        if pain and ev["contact"]:
            while recent:  # 痛み:直前の判断を脳に見直させる
                tt, o, cx, kp, d, at = recent.popleft()
                if t - tt > 1:
                    continue
                rec["calls"][tt] += 1
                if rec["cause"][tt] == 0:
                    rec["cause"][tt] = CAUSE["pain"]
                sp.credit(kp, d, at)
                if d != at:
                    rec["caught"][tt] = 1
                    sp.learn(o, at, sp.wrongs(cx, at), pool, rng, t0 + tt, "pain")
        if t % pool_every == 0:
            pool[rng.integers(len(pool))] = obs
    return rec
