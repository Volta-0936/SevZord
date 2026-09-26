"""脊髄:反射の台帳(記号)と、超次元の照合器(MAP 双極)。

反射 = 役割ごとに「許す値の集合」(mask)と、行動の票(counts)。
記号の照合はそのまま集合の包含で、超次元の照合は束縛した役割⊗値の内積で行う。
両者は同じ台帳を共有するので、食い違いはそのまま混信の量になる。

衝突の解き方(既定の階層, Holland の default hierarchy):
発火した反射のうち、より特殊な反射(許す集合が包含で狭い)に包まれるものは黙る。
残った反射の行動が揃えば決める。揃わなければ「拮抗」で脳へ上げる。
特殊な反射が一般の反射を黙らせる結び目は、書き込みの時に一度だけ計算する(側抑制)。
"""
import numpy as np
from world import NROLE, NVAL, FULL, EN_ROLE, EMPTY

H4 = np.array([[1, 1, 1, 1], [1, -1, 1, -1], [1, 1, -1, -1], [1, -1, -1, 1]], np.float32)


class HDCMatcher:
    def __init__(self, D, sparse=True, codebook="orth", seed=0, cap=512):
        rng = np.random.default_rng(seed)
        self.D, self.sparse, self.codebook = D, sparse, codebook
        Rr = rng.choice(np.array([-1, 1], np.float32), size=(NROLE, D))

        def book(k):
            if codebook == "orth":  # 厳密に直交する値の符号(D は 4 の倍数)
                base = rng.choice(np.array([-1, 1], np.float32), size=D)
                tiles = np.tile(H4, (1, D // 4))
                return (base[None, :] * tiles)[:, rng.permutation(D)][:k]
            return rng.choice(np.array([-1, 1], np.float32), size=(k, D))

        Vc, Ve = book(4), book(3)
        self.PV = np.zeros((NROLE, 4, D), np.float32)  # 役割⊗値
        for j in range(NROLE):
            V = Ve if j == EN_ROLE else Vc
            for v in range(NVAL[j]):
                self.PV[j, v] = Rr[j] * V[v]
        self.Kp = np.zeros((cap, D), np.float32)
        self.Kn = np.zeros((cap, D), np.float32)
        self.npos = np.zeros(cap, np.float32)
        self.tol = np.zeros(cap, np.float32)
        self.n = 0
        self.key_terms = []

    def _grow(self):
        cap = len(self.Kp) * 2
        for name in ("Kp", "Kn"):
            A = np.zeros((cap, self.D), np.float32)
            A[: self.n] = getattr(self, name)[: self.n]
            setattr(self, name, A)
        for name in ("npos", "tol"):
            a = np.zeros(cap, np.float32)
            a[: self.n] = getattr(self, name)[: self.n]
            setattr(self, name, a)

    def add(self, mask, tol=0):
        if self.n == len(self.Kp):
            self._grow()
        kp = np.zeros(self.D, np.float32)
        kn = np.zeros(self.D, np.float32)
        npos, nterm = 0, 0
        for j in range(NROLE):
            m = int(mask[j])
            if m == FULL[j]:
                continue
            allowed = [v for v in range(NVAL[j]) if (m >> v) & 1]
            banned = [v for v in range(NVAL[j]) if not (m >> v) & 1]
            if self.sparse and j != EN_ROLE:
                if EMPTY not in allowed:  # 「何かが在る」は正の選言
                    kp += self.PV[j, allowed].sum(0)
                    npos += 1
                    nterm += len(allowed)
                else:                     # 空を許すなら、禁じる値だけを負に
                    kn += self.PV[j, banned].sum(0)
                    nterm += len(banned)
            else:
                if len(allowed) == 1:
                    kp += self.PV[j, allowed[0]]
                    npos += 1
                    nterm += 1
                else:
                    kn += self.PV[j, banned].sum(0)
                    nterm += len(banned)
        i = self.n
        self.Kp[i], self.Kn[i], self.npos[i], self.tol[i] = kp, kn, npos, tol
        self.key_terms.append(nterm)
        self.n += 1

    def encode(self, obs):
        if self.sparse:
            js = [j for j in range(NROLE) if j == EN_ROLE or obs[j] != EMPTY]
        else:
            js = range(NROLE)
        js = np.fromiter(js, int)
        return self.PV[js, obs[js]].sum(0)

    def fire(self, s):
        n = self.n
        if n == 0:
            return np.zeros(0, int), np.zeros(0)
        cp = self.Kp[:n] @ s / self.D
        cn = self.Kn[:n] @ s / self.D
        viol = np.maximum(self.npos[:n] - cp, 0) + np.maximum(cn, 0)
        return np.where(viol < self.tol[:n] + 0.5)[0], viol


class Spine:
    def __init__(self, cap=1024):
        self.masks = np.zeros((cap, NROLE), np.uint8)
        self.counts = np.zeros((cap, 6), np.int32)
        self.act = np.zeros(cap, np.int8)
        self.tol = np.zeros(cap, np.int16)
        self.inhib_by = []
        self.meta = []
        self.n = 0
        self.matchers = {}

    def attach(self, name, matcher):
        for i in range(self.n):
            matcher.add(self.masks[i], int(self.tol[i]))
        self.matchers[name] = matcher

    def _grow(self):
        cap = len(self.masks) * 2
        for name in ("masks", "counts", "act", "tol"):
            old = getattr(self, name)
            new = np.zeros((cap,) + old.shape[1:], old.dtype)
            new[: self.n] = old[: self.n]
            setattr(self, name, new)

    # ---- 照合
    def sym_fire(self, obs):
        n = self.n
        if n == 0:
            return np.zeros(0, int), np.zeros(0)
        bits = (1 << obs).astype(np.uint8)
        viol = ((self.masks[:n] & bits[None, :]) == 0).sum(1)
        return np.where(viol <= self.tol[:n])[0], viol

    def resolve(self, fired, viol):
        """発火した反射 → (行動 or None, 状態, 投票した反射)"""
        if len(fired) == 0:
            return None, "none", []
        F = set(fired.tolist())
        keep = [r for r in fired if not (self.inhib_by[r] & F)]
        acts = self.act[keep]
        if (acts == acts[0]).all():
            return int(acts[0]), "ok", keep
        if self.tol[keep].max() > 0:  # 近さで照合する反射だけの規則:最も近いものが勝つ
            v = np.asarray(viol)[keep]
            best = [r for r, x in zip(keep, v) if x <= v.min() + 1e-9]
            a2 = self.act[best]
            if (a2 == a2[0]).all():
                return int(a2[0]), "ok", best
        return None, "conflict", keep

    def decide(self, obs, how="sym", s=None):
        if how == "sym":
            fired, viol = self.sym_fire(obs)
        else:
            m = self.matchers[how]
            fired, viol = m.fire(m.encode(obs) if s is None else s)
        return self.resolve(fired, viol)

    # ---- 書き込み(脳の答え+説明 → 反射)
    def write(self, mask, a, tol=0, meta=None):
        n = self.n
        if n:
            same = np.where((self.masks[:n] == mask[None, :]).all(1) & (self.tol[:n] == tol))[0]
            if len(same):
                r = int(same[0])
                self.counts[r, a] += 1
                self.act[r] = int(self.counts[r].argmax())
                return r, False
        if n == len(self.masks):
            self._grow()
        self.masks[n], self.tol[n] = mask, tol
        self.counts[n, a] = 1
        self.act[n] = a
        inhib = set()
        if n:
            M = self.masks[:n]
            new_in_old = ((mask[None, :] & ~M) == 0).all(1)   # 新しい方が狭い
            old_in_new = ((M & ~mask[None, :]) == 0).all(1)   # 古い方が狭い
            for r in np.where(new_in_old)[0]:
                self.inhib_by[r].add(n)
            inhib = set(np.where(old_in_new)[0].tolist())
        self.inhib_by.append(inhib)
        self.meta.append(meta or {})
        self.n += 1
        for m in self.matchers.values():
            m.add(mask, tol)
        return n, True
