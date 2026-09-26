"""脊髄 v1:Jev の複製から借りた三つの構造を入れた版。

1. 反射が確率を持つ(system-one, poorjev: 較正された確率が製品そのもの)。
   反射ごとに行動へのディリクレの票を持つ。生まれた時の票は、説明器が領域の中で
   脳に訊いた標本の答え(+ジェフリーズの ½)。監査のたびに脳の答えを一票足す。
   判断の誤り確率 ê は、発火して投票した反射のうち一番狭いもの(参照クラスの
   一番狭いもの、Reichenbach)の票から出す。
2. 監査を誤りそうな所へ寄せる(poorjev の危険予算、system-one の危険-覆い表)。
   監査の確率 = min(1, max(床, λ·ê))。λ は監査の平均率が目標に揃うように動かす。
3. 選択を「選択肢ごとに、その選択肢の枠で状態を読んで採点」に分ける
   (von/NanoJev の独立採点、jevlike の選択肢ごとの読み)。格子の身体では、
   動く方向が北になるように視野を回した枠で「前が選ばれるか」を一つの表で答える。
   四方向で同じ反射を共有し、脳の同点の崩し方のような非対称だけを枠の同一性で書く。
"""
import numpy as np
from world import (brain, NCELL, EN_ROLE, NROLE, SIDE, CELL_FLAT, CENTER, R,
                   ACTS, EMPTY)

# ---------------------------------------------------------------- 枠(回転)
_GRID_OF_ROLE = [divmod(f, SIDE) for f in CELL_FLAT]


def _rot_index(k):
    """k 回の反時計回り 90° 回転で、役割 j の中身が行く先の役割。"""
    idx = {rc: j for j, rc in enumerate(_GRID_OF_ROLE)}
    out = np.zeros(NCELL, int)
    for j, (r, c) in enumerate(_GRID_OF_ROLE):
        rr, cc = r, c
        for _ in range(k % 4):
            rr, cc = SIDE - 1 - cc, rr
        out[j] = idx[(rr, cc)]
    return out


ROT = [_rot_index(k) for k in range(4)]       # ROT[k][j] = 回した後の番号
UNROT = [np.argsort(ROT[k]) for k in range(4)]
FRAME_ROLE = NROLE                            # 25: 枠の同一性(0..3=方向, 4=基)
BASE = 4


def to_frame(obs, k):
    """絶対の観測 → 方向 k が北になる枠の表現(26 役割)。k=4 は回さない基の枠。"""
    x = np.empty(NROLE + 1, np.int64)
    if k == BASE:
        x[:NROLE] = obs
    else:
        x[ROT[k]] = obs[:NCELL]
        x[EN_ROLE] = obs[EN_ROLE]
    x[FRAME_ROLE] = k
    return x


def from_frame(x):
    k = int(x[FRAME_ROLE])
    if k == BASE:
        return x[:NROLE].copy()
    o = np.empty(NROLE, np.int64)
    o[:NCELL] = x[:NCELL][ROT[k]]
    o[EN_ROLE] = x[EN_ROLE]
    return o


# 自己検査:東の隣は、東の枠では北の隣になる
_N, _E = CELL_FLAT.index(CENTER - SIDE), CELL_FLAT.index(CENTER + 1)
assert ROT[1][_E] == _N


# ---------------------------------------------------------------- 表
class Table:
    """役割ごとに許す値の集合(mask)の表。一番狭いものが勝つ。票はディリクレ。"""

    def __init__(self, nval, nlab, cap=512):
        self.nval = np.asarray(nval)
        self.full = ((1 << self.nval) - 1).astype(np.uint8)
        self.nlab = nlab
        self.masks = np.zeros((cap, len(nval)), np.uint8)
        self.votes = np.zeros((cap, nlab))
        self.act = np.zeros(cap, np.int16)
        self.nc = np.zeros(cap, np.int16)          # 制約の数(狭さ)
        self.inhib_by, self.meta, self.n = [], [], 0

    def _grow(self):
        cap = 2 * len(self.masks)
        for k in ("masks", "votes", "act", "nc"):
            a = getattr(self, k)
            b = np.zeros((cap,) + a.shape[1:], a.dtype)
            b[: self.n] = a[: self.n]
            setattr(self, k, b)

    def fire(self, x):
        if self.n == 0:
            return np.zeros(0, int)
        bits = (1 << x).astype(np.uint8)
        return np.where(((self.masks[: self.n] & bits[None, :]) != 0).all(1))[0]

    def resolve(self, fired):
        if len(fired) == 0:
            return None, "none", []
        F = set(fired.tolist())
        keep = [int(r) for r in fired if not (self.inhib_by[r] & F)]
        acts = self.act[keep]
        if (acts == acts[0]).all():
            return int(acts[0]), "ok", keep
        return None, "conflict", keep

    def err(self, keep):
        """投票した反射のうち一番狭いものの票から、誤り確率を出す。"""
        r = max(keep, key=lambda i: (self.nc[i], -self._e(i)))
        return self._e(r), r

    def _e(self, r):
        v = self.votes[r]
        return 1.0 - v[self.act[r]] / v.sum()

    def prob(self, r):
        return self.votes[r] / self.votes[r].sum()

    def specialize(self, r, j, v):
        """反射 r の役割 j から値 v を外す(版空間の一般側を負例で狭める)。側抑制を結び直す。"""
        self.masks[r, j] &= ~np.uint8(1 << v)
        self.nc[r] = int((self.masks[r] != self.full).sum())
        n, mask = self.n, self.masks[r]
        M = self.masks[:n]
        for q in range(n):
            self.inhib_by[q].discard(r)
        narrower = ((mask[None, :] & ~M) == 0).all(1)
        wider = ((M & ~mask[None, :]) == 0).all(1)
        same = narrower & wider
        for q in np.where(narrower & ~same)[0]:
            self.inhib_by[q].add(r)
        self.inhib_by[r] = set(np.where(wider & ~same)[0].tolist())

    def write(self, mask, lab, hist, meta):
        n = self.n
        if n:
            same = np.where((self.masks[:n] == mask[None, :]).all(1))[0]
            if len(same):
                r = int(same[0])
                self.votes[r] += hist
                self.act[r] = int(self.votes[r].argmax())
                return r, False
        if n == len(self.masks):
            self._grow()
        self.masks[n] = mask
        self.votes[n] = hist
        self.act[n] = lab
        self.nc[n] = int((mask != self.full).sum())
        inhib = set()
        if n:
            M = self.masks[:n]
            for r in np.where(((mask[None, :] & ~M) == 0).all(1))[0]:
                self.inhib_by[r].add(n)
            inhib = set(np.where(((M & ~mask[None, :]) == 0).all(1))[0].tolist())
        self.inhib_by.append(inhib)
        self.meta.append(meta)
        self.n += 1
        return n, True


# ---------------------------------------------------------------- 説明器(一般形)
def explain(x, holds, sample, nval, rng, fixed=(), tau=0.95, m=64, rounds=6, answer=None):
    """表現 x で述語 holds が真であり続ける、役割ごとの値の集合を探す。

    holds(x') -> bool       述語(脳に訊く)
    sample(k) -> [k, R]     観測分布からの標本(表現の空間で)
    fixed                   動かさない役割と、その許す集合 {役割: mask}
    answer(x') -> label     標本での脳の答え(票の元)。None なら holds の真偽を票にする
    返り値: mask, 標本での精度, 票(最後の測りでの答えの数), 脳の呼び出し数
    """
    x = np.asarray(x, np.int64)
    Rn = len(x)
    full = ((1 << np.asarray(nval)) - 1).astype(np.uint8)
    mask = full.copy()
    for j, mj in dict(fixed).items():
        mask[j] = mj
    calls = 0
    for j in range(Rn):
        if j in dict(fixed):
            continue
        for v in range(nval[j]):
            if v == x[j]:
                continue
            x2 = x.copy()
            x2[j] = v
            calls += 1
            if not holds(x2):
                mask[j] &= ~np.uint8(1 << v)

    def measure(mask):
        S = sample(m)
        ok = (mask[None, :] >> S.astype(np.uint8)) & 1
        S = np.where(ok == 1, S, x[None, :])
        res = np.array([holds(s) for s in S])
        return S, np.where(~res)[0]

    for rd in range(rounds + 1):
        S, fail = measure(mask)
        calls += m
        prec = 1.0 - len(fail) / m
        if prec >= tau or rd == rounds:
            break
        counts = np.zeros(Rn)
        bad = [set() for _ in range(Rn)]
        for k in fail[:16]:
            s = S[k]
            for j in np.where(s != x)[0]:
                if j in dict(fixed):
                    continue
                s2 = s.copy()
                s2[j] = x[j]
                calls += 1
                if holds(s2):
                    counts[j] += 1
                    bad[j].add(int(s[j]))
        if counts.max() == 0:
            diff = (S[fail] != x[None, :]).sum(0)
            for j in dict(fixed):
                diff[j] = -1
            j = int(np.argmax(diff))
            mask[j] = np.uint8(1 << x[j])
        else:
            j = int(np.argmax(counts))
            for v in bad[j]:
                mask[j] &= ~np.uint8(1 << v)
    labs = [answer(s) for s in S] if answer else None
    return mask, prec, labs, calls


# ---------------------------------------------------------------- 脊髄(平らな表)
NVAL_FLAT = [4] * NCELL + [3]


def certify(mask, x, holds, pool_x, rng, refine_from, eps_mass=0.0005, cap=4000, rounds=4):
    """観測の標本のうち条件を満たすもの(実際の分布での条件付き)で、反射の失敗率を確かめる。
    許される失敗率は δ = eps_mass / 覆い。超えたら、失敗した標本で締め直す。"""
    calls = 0
    for _ in range(rounds):
        bits = (1 << pool_x).astype(np.uint8)
        inside = np.where(((mask[None, :] & bits) != 0).all(1))[0]
        cover = len(inside) / len(pool_x)
        if len(inside) < 20:
            return mask, cover, calls
        delta = eps_mass / cover
        S = pool_x[inside[rng.permutation(len(inside))[:cap]]]
        res = np.array([holds(s) for s in S])
        calls += len(S)
        fail = np.where(~res)[0]
        if len(fail) <= delta * len(S):
            return mask, cover, calls
        counts = np.zeros(len(x))
        bad = [set() for _ in range(len(x))]
        for k in fail[:32]:
            s = S[k]
            for j in np.where(s != x)[0]:
                s2 = s.copy()
                s2[j] = x[j]
                calls += 1
                if holds(s2):
                    counts[j] += 1
                    bad[j].add(int(s[j]))
        if counts.max() == 0:
            return mask, cover, calls
        j = int(np.argmax(counts))
        for v in bad[j]:
            mask[j] &= ~np.uint8(1 << v)
    return mask, cover, calls


class FlatSpine:
    """v0 と同じ表現(25 役割)、行動 6 択の一つの表。"""
    mode = "flat"

    def __init__(self, scaled=False):
        self.t = Table(NVAL_FLAT, 6)
        self.scaled = scaled

    def decide(self, obs):
        fired = self.t.fire(obs)
        dec, stat, keep = self.t.resolve(fired)
        self._keep = keep
        e, r = self.t.err(keep) if stat == "ok" else (1.0, None)
        return dec, stat, keep, e, r

    def learn(self, obs, a, wrong, pool, rng, t, cause):
        def holds(s):
            return brain(s) == a

        def sample(k):
            return pool[rng.integers(0, len(pool), k)]

        mask, prec, labs, calls = explain(obs, holds, sample, NVAL_FLAT, rng,
                                          answer=brain)
        for r in wrong:
            mask &= self.t.masks[r]
        if self.scaled:
            mask, cover, c2 = certify(mask, obs, holds, pool, rng, None)
            calls += c2
        hist = np.full(6, 0.5) + np.bincount(labs, minlength=6)
        r, new = self.t.write(mask, a, hist, {"born": t, "cause": cause, "prec": prec,
                                              "fires": 0, "ok": 0, "bad": 0, "x0": obs.copy()})
        return calls, new

    def narrow(self, obs, wrong, pool):
        """誤った反射を、この負例を外すように最小に狭める。狭めた数を返す。"""
        done = 0
        for r in wrong:
            x0 = self.t.meta[r].get("x0")
            lab = int(self.t.act[r])
            if x0 is None:
                continue
            cands = []
            for j in np.where(obs != x0)[0]:
                s2 = obs.copy()
                s2[j] = x0[j]
                if brain(s2) == lab:
                    cands.append(j)
            if not cands:
                continue
            j = min(cands, key=lambda j: (pool[:, j] == obs[j]).mean())
            self.t.specialize(r, int(j), int(obs[j]))
            done += 1
        return done

    def context(self):
        return list(self._keep)

    def wrongs(self, ctx, a_true):
        return [r for r in ctx if self.t.act[r] != a_true]

    def credit(self, keep, a_dec, a_true):
        for r in keep:
            self.t.votes[r][a_true] += 1
            self.t.act[r] = int(self.t.votes[r].argmax())

    def n(self):
        return self.t.n


# ---------------------------------------------------------------- 脊髄(回転した枠で共有する表)
NVAL_FRAME = [4] * NCELL + [3, 5]
FWD, NOT = 0, 1          # 移動の枠の表のラベル
MOVES = 0b01111          # 枠の同一性:方向の枠だけ
BASEM = 0b10000          # 基の枠だけ


class FrameSpine:
    """方向ごとに「その方向が北の枠で、前が選ばれるか」を一つの表で答える。
    STAY と EXPLORE は基の枠の表(同じ表、枠の同一性=4)で答える。
    ラベル: 0=前(FWD) 1=前ではない(NOT) 2=STAY 3=EXPLORE"""
    mode = "frames"

    def __init__(self):
        self.t = Table(NVAL_FRAME, 4)

    def _frames(self, obs):
        return [to_frame(obs, k) for k in range(5)]

    def decide(self, obs):
        cands, keeps, conflict = [], [], False
        for k, x in enumerate(self._frames(obs)):
            d, s, keep = self.t.resolve(self.t.fire(x))
            if s == "conflict":
                conflict = True
                keeps.append((k, keep, None))
                continue
            if s == "ok":
                keeps.append((k, keep, d))
                if k < 4 and d == FWD:
                    cands.append((k, keep))
                elif k == BASE and d in (2, 3):
                    cands.append((4 + d - 2, keep))   # 4=STAY, 5=EXPLORE
        allkeep = [r for _, keep, _ in keeps for r in keep]
        self._last = keeps
        if conflict or len(cands) > 1:
            return None, "conflict", allkeep, 1.0, None
        if not cands:
            return None, "none", allkeep, 1.0, None
        a, keep = cands[0]
        e, r = self.t.err(keep)
        return a, "ok", keep, e, r

    def context(self):
        return [(k, list(keep), d) for k, keep, d in self._last]

    def wrongs(self, ctx, a_true):
        """その判断で、誤った答えに票を入れた(枠, 反射)の組。"""
        out = []
        for k, keep, d in ctx:
            for r in keep:
                lab = int(self.t.act[r])
                if k < 4 and lab == FWD and k != a_true:
                    out.append((k, r))
                elif k < 4 and lab == NOT and k == a_true:
                    out.append((k, r))
                elif k == BASE and lab in (2, 3) and 4 + lab - 2 != a_true:
                    out.append((k, r))
                elif k == BASE and lab == NOT and a_true in (4, 5):
                    out.append((k, r))
        return out

    def credit(self, keep, a_dec, a_true):
        for r in keep:
            lab = int(self.t.act[r])
            if lab in (FWD, NOT):
                self.t.votes[r][FWD if a_dec == a_true else NOT] += 1
            else:
                self.t.votes[r][{4: 2, 5: 3}.get(a_true, NOT)] += 1
            self.t.act[r] = int(self.t.votes[r].argmax())

    def learn(self, obs, a, wrong, pool, rng, t, cause):
        calls, new_any = 0, False
        frames = self._frames(obs)

        def sample_move(kk):
            S = pool[rng.integers(0, len(pool), kk)]
            ks = rng.integers(0, 4, kk)
            return np.array([to_frame(s, k) for s, k in zip(S, ks)])

        def sample_base(kk):
            S = pool[rng.integers(0, len(pool), kk)]
            return np.array([to_frame(s, BASE) for s in S])

        # 1) 正しい答えを書く
        if a < 4:
            x = frames[a]
            holds = lambda z: brain(from_frame(z)) == int(z[FRAME_ROLE])
            ans = lambda z: FWD if holds(z) else NOT
            mask, prec, labs, c = explain(x, holds, sample_move, NVAL_FRAME, rng,
                                          fixed={FRAME_ROLE: MOVES}, answer=ans)
            lab = FWD
            # 枠の同一性を絞る必要があるかは、精度の測りで方向を振って確かめている
            x_mask_frame = self._narrow_frame(x, mask, holds, rng)
            mask[FRAME_ROLE] = x_mask_frame
        else:
            x = frames[BASE]
            want = 2 if a == 4 else 3
            holds = lambda z: brain(from_frame(z)) == a
            ans = lambda z: {4: 2, 5: 3}.get(brain(from_frame(z)), NOT)
            mask, prec, labs, c = explain(x, holds, sample_base, NVAL_FRAME, rng,
                                          fixed={FRAME_ROLE: BASEM}, answer=ans)
            lab = want
        calls += c
        hist = np.full(4, 0.5) + np.bincount(labs, minlength=4)
        _, new = self.t.write(mask, lab, hist, {"born": t, "cause": cause, "prec": prec,
                                                "frame": int(x[FRAME_ROLE]), "fires": 0,
                                                "ok": 0, "bad": 0, "exc": False})
        new_any |= new
        # 2) 誤って票を入れた枠ごとに、その枠で例外を書く
        by_frame = {}
        for k, r in wrong:
            by_frame.setdefault(k, []).append(r)
        for k, rs in by_frame.items():
            xk = frames[k]
            if k < 4:
                if k == a:      # 「前ではない」と誤った → この枠で前を書く(上で書いた物が狭ければ足りない)
                    holds = lambda z: brain(from_frame(z)) == int(z[FRAME_ROLE])
                    lab = FWD
                else:           # 「前だ」と誤った → この枠で前ではないを書く
                    holds = lambda z: brain(from_frame(z)) != int(z[FRAME_ROLE])
                    lab = NOT
                ans = lambda z: FWD if brain(from_frame(z)) == int(z[FRAME_ROLE]) else NOT
                mask, prec, labs, c = explain(xk, holds, sample_move, NVAL_FRAME, rng,
                                              fixed={FRAME_ROLE: MOVES}, answer=ans)
                mask[FRAME_ROLE] = self._narrow_frame(xk, mask, holds, rng)
                hist = np.full(4, 0.5) + np.bincount(labs, minlength=4)
            else:
                if a in (4, 5):   # 基の枠で別の答えが勝っていた → 正しい答えを、誤った反射より狭く
                    holds = lambda z: brain(from_frame(z)) == a
                    lab = 2 if a == 4 else 3
                else:             # 基の枠が STAY/EXPLORE と誤った → 基の枠で「ここではない」
                    holds = lambda z: brain(from_frame(z)) not in (4, 5)
                    lab = NOT
                ans = lambda z: {4: 2, 5: 3}.get(brain(from_frame(z)), NOT)
                mask, prec, labs, c = explain(xk, holds, sample_base, NVAL_FRAME, rng,
                                              fixed={FRAME_ROLE: BASEM}, answer=ans)
                hist = np.full(4, 0.5) + np.bincount(labs, minlength=4)
            calls += c
            for r in rs:
                mask &= self.t.masks[r]
            _, new = self.t.write(mask, lab, hist, {"born": t, "cause": cause, "prec": prec,
                                                    "frame": k, "fires": 0, "ok": 0, "bad": 0,
                                                    "exc": True})
            new_any |= new
        return calls, new_any

    def _narrow_frame(self, x, mask, holds, rng):
        """同じ回した状態を他の方向の枠で読んでも述語が保たれるか。保たれない方向は外す。"""
        allowed = 0
        for k in range(4):
            z = x.copy()
            z[FRAME_ROLE] = k
            if holds(z):
                allowed |= 1 << k
        return np.uint8(allowed or (1 << int(x[FRAME_ROLE])))

    def n(self):
        return self.t.n
