"""v1 の条件。python3 exp2.py <条件> <種> → results2/<条件>_<種>.npz/.json"""
import json
import os
import sys
import time
import numpy as np
from world import World, Env, make_pool
from spine2 import FlatSpine, FrameSpine, MOVES, FRAME_ROLE
from spine3 import GradeSpine
from run2 import learn2

A = (14, 4)
TA = 20000
os.makedirs("results2", exist_ok=True)

COND = {
    "flat_blind": dict(kind="flat", audit="blind"),
    "flat_risk": dict(kind="flat", audit="risk"),
    "flat_pain": dict(kind="flat", audit="none", pain=True),
    "flat_riskpain": dict(kind="flat", audit="risk", pain=True),
    "flat_thresh": dict(kind="flat", audit="thresh"),
    "flat_threshpain": dict(kind="flat", audit="thresh", pain=True),
    "flat_threshnarrow": dict(kind="flat", audit="thresh", narrow=True),
    "flat_risknarrow": dict(kind="flat", audit="risk", narrow=True),
    "frame_blind": dict(kind="frame", audit="blind"),
    "flat_risknarrow_scaled": dict(kind="flat", audit="risk", narrow=True, scaled=True),
    "grade_blind": dict(kind="grade", audit="blind"),
    "grade_lazy": dict(kind="grade", audit="blind", lazy=True),
    "grade_lazy_risknarrow": dict(kind="grade", audit="risk", narrow=True, lazy=True),
    "grade_risknarrow": dict(kind="grade", audit="risk", narrow=True),
    "frame_riskpain": dict(kind="frame", audit="risk", pain=True),
}


def main(name, seed):
    c = COND[name]
    t0 = time.time()
    w = World(20, 0.12, seed=1)
    pool = make_pool(w, *A, seed=11)
    sp = {"flat": lambda: FlatSpine(scaled=c.get("scaled", False)), "frame": FrameSpine,
          "grade": lambda: GradeSpine(lazy=c.get("lazy", False))}[c["kind"]]()
    rng = np.random.default_rng(200 + seed)
    rec = learn2(sp, Env(w, *A, seed=100 + seed), pool, TA, rng, audit=c["audit"],
                 pain=c.get("pain", False), narrow=c.get("narrow", False))
    t = sp.t
    info = {"seconds": time.time() - t0, "n": t.n,
            "labels": np.bincount(t.act[: t.n], minlength=t.nlab).tolist(),
            "nc_mean": float(t.nc[: t.n].mean())}
    if c["kind"] == "grade":
        sl = [m["slot"] for m in t.meta[: t.n]]
        info["by_slot"] = np.bincount(sl, minlength=6).tolist()
        mv = [i for i in range(t.n) if t.meta[i]["slot"] < 4]
        info["move_reflexes"] = len(mv)
        info["move_frame_restricted"] = int(sum(1 for i in mv if t.masks[i][FRAME_ROLE] != 0b001111))
        info["exceptions"] = int(sum(1 for m in t.meta[: t.n] if m.get("exc")))
    if c["kind"] == "frame":
        moves = [i for i in range(t.n) if t.masks[i][FRAME_ROLE] & 0b10000 == 0]
        info["move_reflexes"] = len(moves)
        info["move_frame_restricted"] = int(sum(1 for i in moves if t.masks[i][FRAME_ROLE] != MOVES))
        info["exceptions"] = int(sum(1 for m in t.meta[: t.n] if m.get("exc")))
    np.savez_compressed(f"results2/{name}_{seed}.npz", **rec)
    json.dump(info, open(f"results2/{name}_{seed}.json", "w"))


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]))
