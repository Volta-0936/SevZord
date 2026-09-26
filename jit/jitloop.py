"""JIT の輪の道具:方針を読み込み、流れを通し、審判に回す物を選び、答えを集計する。"""
import importlib.util
import json
import os
import numpy as np
from task import load, dump, INSTRUCTIONS

_HERE = os.path.dirname(os.path.abspath(__file__))
INBOX = "/home/claude/judge_inbox" if os.path.isdir("/home/claude/judge_inbox") else os.path.join(_HERE, "judge_inbox")
OUTBOX = "/home/claude/judge_outbox" if os.path.isdir("/home/claude/judge_outbox") else os.path.join(_HERE, "judge_outbox")


def policy(k):
    spec = importlib.util.spec_from_file_location(f"p{k}", f"policies/p{k}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.decide


def select(decide, states, rng, audit=0.10, cap=120):
    """棄権した物は全部、答えた物は audit の割合で審判へ。"""
    ab, cov = [], []
    for s in states:
        a, g = decide(s)
        (ab if a is None else cov).append(s)
    k = int(round(audit * len(cov)))
    aud = [cov[i] for i in sorted(rng.choice(len(cov), min(k, len(cov)), replace=False))]
    pick = ab + aud
    return pick[:cap], len(ab), len(aud)


def write_batch(name, states):
    dump(states, f"{INBOX}/{name}.jsonl")
    with open(f"{INBOX}/INSTRUCTIONS.txt", "w", encoding="utf-8") as f:
        f.write(INSTRUCTIONS)


def answers(name):
    p = f"{OUTBOX}/{name}.json"
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def labels():
    """流れのラベル(審判に回した物だけ)を全部集める。"""
    out = {}
    for f in sorted(os.listdir(OUTBOX)):
        if f.startswith("round"):
            out.update(json.load(open(f"{OUTBOX}/{f}", encoding="utf-8")))
    return out
