"""脊髄 v2-①:選択肢ごとの成績を、回した枠で共有する表。

六つの問い(スロット)を一つの表で答える。表の最後の役割がスロットの番号。
  0..3  その方向を北に回した枠で「前は最善の集合に入るか」   (四方向で同じ反射を共有)
  4     回さない枠で「EXPLORE か」
  5     回さない枠で「STAY は最善の集合に入るか」
ラベル: 0=はい 1=いいえ
決め方(集合側の固定規則): EXPLORE なら EXPLORE。そうでなければ最善に入る選択肢を
N,E,S,W,STAY の順で最初の一つ。六つが全部答えられない時は脳へ上げ、脳は六つを一度に採点する。
"""
import numpy as np
from grades import brain_eval
from spine2 import Table, explain, to_frame, from_frame, FRAME_ROLE
from world import NCELL

YES, NO = 0, 1
NVAL = [4] * NCELL + [3, 6]
SLOT_MASK = {0: 0b001111, 1: 0b001111, 2: 0b001111, 3: 0b001111, 4: 0b010000, 5: 0b100000}


def slot_x(obs, s):
    x = to_frame(obs, s if s < 4 else 4)
    x[FRAME_ROLE] = s
    return x


def unslot(z):
    z = z.copy()
    if z[FRAME_ROLE] >= 4:
        z[FRAME_ROLE] = 4
    return from_frame(z)


def truth(obs):
    pick, explore, best = brain_eval(obs)
    t = [YES if (not explore and k in best) else NO for k in range(4)]
    t.append(YES if explore else NO)
    t.append(YES if (not explore and 4 in best) else NO)
    return t, pick


def slot_truth(z):
    return truth(unslot(z))[0][int(z[FRAME_ROLE])]


class GradeSpine:
    mode = "grades"

    def __init__(self, lazy=False):
        self.t = Table(NVAL, 2)
        self.lazy = lazy

    def n(self):
        return self.t.n

    def decide(self, obs):
        if self.lazy:
            return self._decide_lazy(obs)
        ans, ctx, stat = {}, [], "ok"
        for s in range(6):
            d, st, keep = self.t.resolve(self.t.fire(slot_x(obs, s)))
            ctx.append((s, keep, d, st))
            if st == "conflict":
                stat = "conflict"
            elif st == "none" and stat == "ok":
                stat = "none"
            ans[s] = d
        self._ctx, self._obs = ctx, obs
        allkeep = [r for _, keep, _, _ in ctx for r in keep]
        if stat != "ok":
            return None, stat, allkeep, 1.0, None
        if ans[4] == YES:
            if any(ans[k] == YES for k in range(4)) or ans[5] == YES:
                return None, "conflict", allkeep, 1.0, None
            a = 5
        else:
            moves = [k for k in range(4) if ans[k] == YES]
            a = moves[0] if moves else (4 if ans[5] == YES else None)
            if a is None:
                return None, "conflict", allkeep, 1.0, None
        e = 0.0
        for s, keep, d, st in ctx:   # 六つのスロットの誤り確率を足す(上界)
            e += self.t.err(keep)[0]
        return a, "ok", allkeep, min(e, 1.0), None

    def _decide_lazy(self, obs):
        """要るスロットだけを順に見る(短絡評価)。"""
        ctx = []
        memo = {}

        def ask(s):
            if s not in memo:
                d, st, keep = self.t.resolve(self.t.fire(slot_x(obs, s)))
                memo[s] = (d, st, keep)
                ctx.append((s, keep, d, st))
            return memo[s]

        def finish(a, stat):
            self._ctx, self._obs = ctx, obs
            allkeep = [r for _, keep, _, _ in ctx for r in keep]
            if stat != "ok":
                return None, stat, allkeep, 1.0, None
            e = sum(self.t.err(keep)[0] for _, keep, _, st in ctx if st == "ok")
            return a, "ok", allkeep, min(e, 1.0), None

        d, st, _ = ask(4)
        if st == "conflict":
            return finish(None, "conflict")
        if st == "ok" and d == YES:
            return finish(5, "ok")
        for k in (0, 1, 2, 3, 5):
            d, st, _ = ask(k)
            if st != "ok":
                return finish(None, st)
            if d == YES:
                return finish(k if k < 4 else 4, "ok")
        return finish(None, "conflict")   # 何も最善でない:答えが食い違っている

    def context(self):
        return (self._obs, list(self._ctx))

    def wrongs(self, ctx, a_true):
        obs, slots = ctx
        tr, _ = truth(obs)
        return [(s, r) for s, keep, d, st in slots for r in keep if self.t.act[r] != tr[s]]

    def _sampler(self, s, pool, rng):
        def sample(k):
            S = pool[rng.integers(0, len(pool), k)]
            ks = rng.integers(0, 4, k) if s < 4 else np.full(k, s)
            return np.array([slot_x(o, int(q)) for o, q in zip(S, ks)])
        return sample

    def learn(self, obs, a_true, wrong, pool, rng, t, cause):
        tr, _ = truth(obs)
        _, slots = self.context() if cause in ("none", "conflict") else (None, self._ctx)
        if cause in ("none", "conflict"):
            wrong = self.wrongs((obs, slots), a_true)
        wrong_by = {}
        for s, r in wrong:
            wrong_by.setdefault(s, []).append(r)
        unresolved = {s for s, keep, d, st in slots if st != "ok"}
        calls = 0
        for s in range(6):
            if s not in unresolved and s not in wrong_by:
                continue
            g = tr[s]
            x = slot_x(obs, s)
            holds = lambda z, g=g: slot_truth(z) == g
            mask, prec, labs, c = explain(x, holds, self._sampler(s, pool, rng), NVAL, rng,
                                          fixed={FRAME_ROLE: SLOT_MASK[s]}, answer=slot_truth)
            calls += c
            if s < 4:   # 四方向で共有してよいかを、この状態を他の枠で読んで確かめる
                allowed = 0
                for k in range(4):
                    z = x.copy()
                    z[FRAME_ROLE] = k
                    if holds(z):
                        allowed |= 1 << k
                mask[FRAME_ROLE] = np.uint8(allowed or (1 << s))
            for r in wrong_by.get(s, []):
                mask &= self.t.masks[r]
            hist = np.full(2, 0.5) + np.bincount(labs, minlength=2)
            self.t.write(mask, g, hist, {"born": t, "cause": cause, "prec": prec, "slot": s,
                                          "x0": x, "exc": s in wrong_by})
        return calls, True

    def credit(self, keep, a_dec, a_true):
        tr, _ = truth(self._obs)
        for s, kp, d, st in self._ctx:
            for r in kp:
                self.t.votes[r][tr[s]] += 1
                self.t.act[r] = int(self.t.votes[r].argmax())

    def narrow(self, obs, wrong, pool):
        done = 0
        for s, r in wrong:
            x0 = self.t.meta[r]["x0"]
            lab = int(self.t.act[r])
            xf = slot_x(obs, s)
            cands = []
            for j in np.where(xf[:FRAME_ROLE] != x0[:FRAME_ROLE])[0]:
                z = xf.copy()
                z[j] = x0[j]
                if slot_truth(z) == lab:
                    cands.append(j)
            if cands:
                # 失う質量が最小の候補:その値が観測分布でどれだけ出るか(マスは位置によらず数える)
                j = min(cands, key=lambda j: (pool[:, :NCELL] == xf[j]).mean() if j < NCELL
                        else (pool[:, NCELL] == xf[j]).mean())
                self.t.specialize(r, int(j), int(xf[j]))
                done += 1
        return done
