"""身体(格子世界)と脳(視野上の計画器)と、脳の説明器。

役割(roles)は自己中心の視野 5x5 の 24 マスと、エネルギーの段階の計 25 本。
脳は観測だけを見て決める。脊髄が見るものと脳が見るものは同じにしてある
(脳が見えないものに依存すると、どんな反射もそれを写せないため)。
"""
from collections import deque
import numpy as np

EMPTY, WALL, FOOD, ENEMY = 0, 1, 2, 3
CELL_NAMES = ["空", "壁", "餌", "敵"]
LOW, MID, HIGH = 0, 1, 2
EN_NAMES = ["低", "中", "高"]
R = 2
SIDE = 2 * R + 1
CENTER = R * SIDE + R                      # 平らな番号での中心(=自分)
CELL_FLAT = [f for f in range(SIDE * SIDE) if f != CENTER]
NCELL = len(CELL_FLAT)                     # 24
EN_ROLE = NCELL                            # 24
NROLE = NCELL + 1                          # 25
NVAL = np.array([4] * NCELL + [3])
FULL = ((1 << NVAL) - 1).astype(np.uint8)  # 役割ごとの「制約なし」の値集合
ACTS = ["N", "E", "S", "W", "STAY", "EXPLORE"]
DELTA = [(-1, 0), (0, 1), (1, 0), (0, -1), (0, 0)]

# 5x5 の近傍(平らな番号)
NBF = []
for f in range(SIDE * SIDE):
    r, c = divmod(f, SIDE)
    NBF.append([(r + dr) * SIDE + (c + dc) for dr, dc in DELTA[:4]
                if 0 <= r + dr < SIDE and 0 <= c + dc < SIDE])
MOVEF = [CENTER + dr * SIDE + dc for dr, dc in DELTA]


def role_name(j):
    if j == EN_ROLE:
        return "エネルギー"
    f = CELL_FLAT[j]
    r, c = divmod(f, SIDE)
    dy, dx = r - R, c - R
    return f"({dx:+d},{dy:+d})"


# ---------------------------------------------------------------- 脳
def brain(obs):
    """観測(25 整数)→ 行動 0..5。一歩先読み+視野内の餌への BFS 距離。"""
    g = [EMPTY] * (SIDE * SIDE)
    for i, f in enumerate(CELL_FLAT):
        g[f] = obs[i]
    low = obs[EN_ROLE] == LOW
    dist = [-1] * (SIDE * SIDE)
    q = deque()
    danger = set()
    for f in range(SIDE * SIDE):
        v = g[f]
        if v == FOOD:
            dist[f] = 0
            q.append(f)
        elif v == ENEMY:
            danger.add(f)
            danger.update(NBF[f])
    while q:
        f = q.popleft()
        for n in NBF[f]:
            if dist[n] < 0 and g[n] != WALL and g[n] != ENEMY:
                dist[n] = dist[f] + 1
                q.append(n)
    if dist[CENTER] < 0 and CENTER not in danger:
        return 5  # 見える所に届く餌が無く、危険も無い → 歩行の中枢(CPG)に任せる
    w_danger = 3.0 if low else 10.0
    w_food = 4.0 if low else 2.0
    w_dist = 1.0 if low else 0.5
    best, best_sc = 4, -1e9
    for a in range(5):
        p = MOVEF[a]
        blocked = False
        if g[p] == WALL:
            p, blocked = CENTER, a != 4
        sc = 0.0
        if p in danger:
            sc -= w_danger
        if p != CENTER and g[p] == FOOD:
            sc += w_food
        d = dist[p] if dist[p] >= 0 else 9
        sc -= w_dist * d
        if blocked:
            sc -= 0.1
        if sc > best_sc + 1e-9:
            best, best_sc = a, sc
    return best


# ---------------------------------------------------------------- 説明器
def explain(obs, a, pool, rng, mode="anchor", tau=0.95, m=64, rounds=6):
    """脳の答え a について、どの役割がどの値の範囲にあれば a が保たれるか。

    返り値: (mask[25] uint8 = 役割ごとに許す値の集合, 推定精度, 脳の呼び出し回数)
    anchor   : 一つずつ動かして必要な制約を集め(必要性)、観測分布からの標本で
               十分性を確かめ、足りなければ締める(Ribeiro ら 2018 の Anchors 型)。
    necessity: 必要性だけ(十分性を確かめない)。
    noisy    : anchor の後、制約を一つ落とす/無関係な制約を一つ足す(説明の誤り)。
    full     : 観測全体を固定(=全状態キャッシュ)。
    """
    obs = np.asarray(obs, dtype=np.int64)
    calls = 0
    if mode in ("full", "sim"):
        return (1 << obs).astype(np.uint8), 1.0, 0
    mask = FULL.copy()
    for j in range(NROLE):
        for v in range(NVAL[j]):
            if v == obs[j]:
                continue
            s2 = obs.copy()
            s2[j] = v
            calls += 1
            if brain(s2) != a:
                mask[j] &= ~np.uint8(1 << v)
    if mode == "necessity":
        return mask, float("nan"), calls

    def measure(mask):
        idx = rng.integers(0, len(pool), m)
        S = pool[idx].copy()
        allowed = (mask[None, :] >> S.astype(np.uint8)) & 1
        S = np.where(allowed == 1, S, obs[None, :])
        res = np.array([brain(s) for s in S])
        return S, np.where(res != a)[0]

    prec = 0.0
    for _ in range(rounds):
        S, fail = measure(mask)
        calls += m
        prec = 1.0 - len(fail) / m
        if prec >= tau:
            break
        counts = np.zeros(NROLE)
        bad = [set() for _ in range(NROLE)]
        for k in fail[:16]:
            s = S[k]
            for j in np.where(s != obs)[0]:
                s2 = s.copy()
                s2[j] = obs[j]
                calls += 1
                if brain(s2) == a:
                    counts[j] += 1
                    bad[j].add(int(s[j]))
        if counts.max() == 0:
            diff = (S[fail] != obs[None, :]).sum(0)
            j = int(np.argmax(diff))
            mask[j] = np.uint8(1 << obs[j])
        else:
            j = int(np.argmax(counts))
            for v in bad[j]:
                mask[j] &= ~np.uint8(1 << v)
    else:
        S, fail = measure(mask)
        calls += m
        prec = 1.0 - len(fail) / m

    if mode == "noisy":
        constrained = np.where(mask != FULL)[0]
        free = np.where(mask == FULL)[0]
        if len(constrained) and rng.random() < 0.3:
            j = rng.choice(constrained)
            mask[j] = FULL[j]  # 落とす(見落とし)
        if len(free) and rng.random() < 0.3:
            j = rng.choice(free)
            mask[j] = np.uint8(1 << obs[j])  # 足す(余計な条件)
    return mask, prec, calls


def describe(mask, action):
    parts = []
    for j in range(NROLE):
        if mask[j] == FULL[j]:
            continue
        names = EN_NAMES if j == EN_ROLE else CELL_NAMES
        allowed = [names[v] for v in range(NVAL[j]) if (mask[j] >> v) & 1]
        banned = [names[v] for v in range(NVAL[j]) if not (mask[j] >> v) & 1]
        if len(allowed) == 1:
            parts.append(f"{role_name(j)}={allowed[0]}")
        elif len(banned) <= len(allowed):
            parts.append(f"{role_name(j)}≠{'/'.join(banned)}")
        else:
            parts.append(f"{role_name(j)}∈{'/'.join(allowed)}")
    return " ∧ ".join(parts) + f" → {ACTS[action]}"


# ---------------------------------------------------------------- 身体
class World:
    """静的な地図(壁)。自由マスの最大連結成分だけを残す。"""

    def __init__(self, size=20, wall_density=0.12, seed=1):
        rng = np.random.default_rng(seed)
        W = rng.random((size, size)) < wall_density
        W[0, :] = W[-1, :] = W[:, 0] = W[:, -1] = True
        comp = -np.ones((size, size), int)
        best, best_n, k = -1, 0, 0
        for y in range(size):
            for x in range(size):
                if W[y, x] or comp[y, x] >= 0:
                    continue
                q, n = deque([(y, x)]), 0
                comp[y, x] = k
                while q:
                    cy, cx = q.popleft()
                    n += 1
                    for dy, dx in DELTA[:4]:
                        ny, nx = cy + dy, cx + dx
                        if not W[ny, nx] and comp[ny, nx] < 0:
                            comp[ny, nx] = k
                            q.append((ny, nx))
                if n > best_n:
                    best, best_n = k, n
                k += 1
        W |= comp != best
        self.size, self.wall = size, W
        self.free = [tuple(p) for p in np.argwhere(~W)]


class Env:
    def __init__(self, world, n_food=14, n_enemy=4, seed=0):
        self.w, self.rng = world, np.random.default_rng(seed)
        self.n_food, self.n_enemy = n_food, n_enemy
        self.agent = self._rand_free(set())
        self.food = set()
        while len(self.food) < n_food:
            self.food.add(self._rand_free({self.agent} | self.food))
        self.enemies = []
        for _ in range(n_enemy):
            self.enemies.append(self._far_free())
        self.energy, self.heading = 25, int(self.rng.integers(4))

    def _rand_free(self, taken):
        while True:
            p = self.w.free[self.rng.integers(len(self.w.free))]
            if p not in taken:
                return p

    def _far_free(self):
        while True:
            p = self._rand_free(set(self.enemies) | {self.agent})
            if abs(p[0] - self.agent[0]) + abs(p[1] - self.agent[1]) >= 5:
                return p

    def obs(self):
        ay, ax = self.agent
        en = set(self.enemies)
        o = np.empty(NROLE, np.int64)
        for i, f in enumerate(CELL_FLAT):
            r, c = divmod(f, SIDE)
            p = (ay + r - R, ax + c - R)
            if not (0 <= p[0] < self.w.size and 0 <= p[1] < self.w.size) or self.w.wall[p]:
                o[i] = WALL
            elif p in en:
                o[i] = ENEMY
            elif p in self.food:
                o[i] = FOOD
            else:
                o[i] = EMPTY
        o[EN_ROLE] = LOW if self.energy <= 8 else (MID if self.energy <= 18 else HIGH)
        return o

    def _open(self, p):
        return not self.w.wall[p] and p not in self.enemies

    def step(self, a):
        ev = {"ate": 0, "contact": 0, "faint": 0}
        ay, ax = self.agent
        if a == 5:  # 歩行の中枢:向きを保ち、塞がれたら/時々向きを変える
            dy, dx = DELTA[self.heading]
            if not self._open((ay + dy, ax + dx)) or self.rng.random() < 0.1:
                opts = [h for h in range(4) if self._open((ay + DELTA[h][0], ax + DELTA[h][1]))]
                if opts:
                    self.heading = int(self.rng.choice(opts))
            dy, dx = DELTA[self.heading]
        else:
            dy, dx = DELTA[a]
        t = (ay + dy, ax + dx)
        if not self.w.wall[t]:
            self.agent = t
        if self.agent in self.enemies:
            ev["contact"] += 1
            self.enemies[self.enemies.index(self.agent)] = self._far_free()
        if self.agent in self.food:
            self.food.discard(self.agent)
            ev["ate"] += 1
            self.food.add(self._rand_free({self.agent} | self.food | set(self.enemies)))
        ay, ax = self.agent
        for k, (ey, ex) in enumerate(self.enemies):
            others = set(self.enemies[:k] + self.enemies[k + 1:])
            cand = [(ey + dy, ex + dx) for dy, dx in DELTA]
            cand = [p for p in cand if not self.w.wall[p] and p not in others]
            d0 = abs(ey - ay) + abs(ex - ax)
            if d0 <= 5 and self.rng.random() < 0.6:
                closer = [p for p in cand if abs(p[0] - ay) + abs(p[1] - ax) < d0]
                cand = closer or cand
            np_ = cand[self.rng.integers(len(cand))]
            if np_ == self.agent:
                ev["contact"] += 1
                self.enemies[k] = self._far_free()
            else:
                self.enemies[k] = np_
        self.energy -= 1 + 6 * ev["contact"]
        if ev["ate"]:
            self.energy = min(30, self.energy + 12 * ev["ate"])
        if self.energy <= 0:
            ev["faint"] = 1
            self.energy = 15
        return ev


def make_pool(world, n_food, n_enemy, seed, steps=3000, size=4000):
    """脳が動かした身体の観測を集める(説明器の十分性の標本の元)。"""
    env = Env(world, n_food, n_enemy, seed)
    obs = []
    for _ in range(steps):
        o = env.obs()
        obs.append(o)
        env.step(brain(o))
    P = np.array(obs)
    rng = np.random.default_rng(seed + 7)
    return P[rng.permutation(len(P))[:size]]
