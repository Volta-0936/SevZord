"""②の題材:城の番兵NPCの行動選択。構造化された状態と、曖昧な自然言語の指示。"""
import json
import numpy as np

ACTIONS = ["melee_attack", "shoot", "retreat", "drink_potion", "take_cover", "raise_alarm",
           "hold_position"]

INSTRUCTIONS = """城の番兵NPCの、このターンの行動を一つ選ぶ。番兵は忠実だが、無駄死にはしない。門を守りつつ生き延びること。
- ひどく傷ついているなら、回復薬があれば飲み、なければ退く。
- 敵が離れていて矢が残っていれば弓で射る。隣接していれば近接で戦う。
- トロルは一人で相手にするには強すぎる。
- 魔術師は早く仕留めるべきだ。
- 警報がまだ鳴っておらず、深刻な脅威が現れたなら警報を鳴らす。
- 夜は用心深く。
- 脅威が無ければ持ち場を守る。

行動: melee_attack(近接攻撃), shoot(弓で射る), retreat(退く), drink_potion(回復薬を飲む), take_cover(遮蔽に隠れる), raise_alarm(警報を鳴らす), hold_position(持ち場を守る)
状態の項目: hp(番兵の体力 0-100), enemy(最も近い敵の種類: none/goblin/orc/mage/troll), distance(その敵までのマス数、敵がいなければ null), enemy_count(見えている敵の数), enemy_hp(最も近い敵の体力 %), allies(近くの味方の数), potion(回復薬を持っているか), arrows(矢の残り), cover(近くに遮蔽物があるか), alarm(警報が既に鳴っているか), post(持ち場: gate/wall/corridor), time(day/night)"""


def gen(n, seed):
    rng = np.random.default_rng(seed)
    out = []
    for i in range(n):
        threat = rng.random() < 0.55
        s = {}
        u = rng.random()
        s["hp"] = int(rng.integers(70, 101) if u < 0.6 else rng.integers(35, 70) if u < 0.85
                      else rng.integers(5, 35))
        if threat:
            s["enemy"] = str(rng.choice(["goblin", "orc", "mage", "troll"], p=[0.5, 0.25, 0.15, 0.1]))
            s["distance"] = int(rng.choice([1, int(rng.integers(2, 5)), int(rng.integers(5, 9)),
                                            int(rng.integers(9, 13))], p=[0.2, 0.3, 0.3, 0.2]))
            s["enemy_count"] = int(rng.choice([1, 2, 3, 4, 5], p=[0.45, 0.25, 0.15, 0.1, 0.05]))
            s["enemy_hp"] = int(rng.integers(1, 11) * 10)
        else:
            s["enemy"], s["distance"], s["enemy_count"], s["enemy_hp"] = "none", None, 0, None
        s["allies"] = int(rng.choice([0, 1, 2, 3], p=[0.4, 0.3, 0.2, 0.1]))
        s["potion"] = bool(rng.random() < 0.4)
        a = rng.random()
        s["arrows"] = 0 if a < 0.25 else int(rng.integers(1, 6)) if a < 0.5 else int(rng.integers(6, 21))
        s["cover"] = bool(rng.random() < 0.5)
        s["alarm"] = bool(rng.random() < (0.45 if threat else 0.15))
        s["post"] = str(rng.choice(["gate", "wall", "corridor"], p=[0.5, 0.3, 0.2]))
        s["time"] = "night" if rng.random() < 0.4 else "day"
        out.append({"id": f"s{seed}-{i:04d}", **s})
    return out


def dump(states, path):
    with open(path, "w", encoding="utf-8") as f:
        for s in states:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")


def load(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


if __name__ == "__main__":
    import os
    os.makedirs("data", exist_ok=True)
    H = gen(300, 1)
    S = gen(3000, 2)
    dump(H, "data/holdout.jsonl")
    dump(S, "data/stream.jsonl")
    rng = np.random.default_rng(9)
    C = [H[i] for i in sorted(rng.choice(300, 60, replace=False))]
    dump(C, "data/consistency.jsonl")
    for k in range(3):
        dump(H[100 * k:100 * (k + 1)], f"data/judge_holdout_{k}.jsonl")
    print("holdout", len(H), "stream", len(S), "consistency", len(C))
    import collections
    print(collections.Counter(s["enemy"] for s in S))
