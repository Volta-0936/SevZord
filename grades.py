"""脳の採点:選んだ一つではなく、各選択肢が最善の集合に入るか。world.brain と同じ計算。"""
from collections import deque
from world import EMPTY, WALL, FOOD, ENEMY, LOW, SIDE, CENTER, CELL_FLAT, EN_ROLE, NBF, MOVEF


def brain_eval(obs):
    """→ (pick, explore, best) best は同点をすべて含む最善の行動の集合(0..4)。"""
    g = [EMPTY] * (SIDE * SIDE)
    for i, f in enumerate(CELL_FLAT):
        g[f] = obs[i]
    low = obs[EN_ROLE] == LOW
    dist = [-1] * (SIDE * SIDE)
    q = deque()
    danger = set()
    for f in range(SIDE * SIDE):
        if g[f] == FOOD:
            dist[f] = 0
            q.append(f)
        elif g[f] == ENEMY:
            danger.add(f)
            danger.update(NBF[f])
    while q:
        f = q.popleft()
        for n in NBF[f]:
            if dist[n] < 0 and g[n] != WALL and g[n] != ENEMY:
                dist[n] = dist[f] + 1
                q.append(n)
    if dist[CENTER] < 0 and CENTER not in danger:
        return 5, True, frozenset()
    wd, wf, wx = (3.0, 4.0, 1.0) if low else (10.0, 2.0, 0.5)
    sc = []
    for a in range(5):
        p = MOVEF[a]
        blocked = False
        if g[p] == WALL:
            p, blocked = CENTER, a != 4
        s = 0.0
        if p in danger:
            s -= wd
        if p != CENTER and g[p] == FOOD:
            s += wf
        s -= wx * (dist[p] if dist[p] >= 0 else 9)
        if blocked:
            s -= 0.1
        sc.append(s)
    m = max(sc)
    best = frozenset(a for a in range(5) if sc[a] > m - 1e-9)
    return min(best), False, best
