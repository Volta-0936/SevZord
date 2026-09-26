"""Jev と直接比べる。保留2 の 300 状態を Jev に Choice の問いとして訊き、審判(別の Claude)の答えと突き合わせる。

鍵の探し方(どれか一つでよい):
  1. 環境変数 TYPESAFE_API_KEY
  2. このフォルダの typesafe_key.txt(中身は鍵だけ。.typesafe_key でもよい)
標準ライブラリだけで動く。結果は jev_holdout2.json(一件ずつ)と jev_result.txt(まとめ)に書く。
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def key():
    k = os.environ.get("TYPESAFE_API_KEY", "").strip()
    for name in ("typesafe_key.txt", ".typesafe_key"):
        p = os.path.join(HERE, name)
        if not k and os.path.exists(p):
            k = open(p, encoding="utf-8-sig").read().strip()
    if not k:
        sys.exit("鍵が見つからない: このフォルダに typesafe_key.txt を作り、鍵だけを書いて保存する")
    return k


def load_jsonl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


URL = "https://api.typesafe.ai/v1/systemone"
LANG = sys.argv[1] if len(sys.argv) > 1 else "ja"   # ja: 審判と同じ日本語の指示文 / en: 英訳(Jev に公平かを確かめる)
CRIT = {"ja": {"melee_attack": "近接攻撃", "shoot": "弓で射る", "retreat": "退く", "drink_potion": "回復薬を飲む",
               "take_cover": "遮蔽に隠れる", "raise_alarm": "警報を鳴らす", "hold_position": "持ち場を守る"},
        "en": {"melee_attack": "Attack in melee", "shoot": "Shoot with the bow", "retreat": "Retreat",
               "drink_potion": "Drink a healing potion", "take_cover": "Take cover behind nearby cover",
               "raise_alarm": "Raise the alarm", "hold_position": "Hold position"}}[LANG]
SUFFIX = "" if LANG == "ja" else "_en"


def ask(k, state, instructions):
    body = {"model": "jev-latest", "state": state,
            "questions": {"action": {"type": "choice", "instructions": instructions, "criteria": CRIT}}}
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    for attempt in range(6):
        req = urllib.request.Request(URL, data=data, method="POST",
                                     headers={"Authorization": f"Bearer {k}",
                                              "Content-Type": "application/json"})
        t = time.perf_counter()
        try:
            r = json.load(urllib.request.urlopen(req, timeout=60))
            return r, time.perf_counter() - t
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 529) and attempt < 5:
                time.sleep(2 ** attempt)
                continue
            raise SystemExit(f"HTTP {e.code}: {e.read()[:300]!r}")


def main():
    k = key()
    H2 = load_jsonl(os.path.join(HERE, "data", "holdout2.jsonl"))
    instructions = open(os.path.join(HERE, "data", "INSTRUCTIONS.txt" if LANG == "ja" else "INSTRUCTIONS_en.txt"),
                        encoding="utf-8").read()
    J2 = {}
    for i in range(3):
        J2.update(json.load(open(os.path.join(HERE, "judge_outbox", f"holdout2_{i}.json"), encoding="utf-8")))
    outp = os.path.join(HERE, f"jev_holdout2{SUFFIX}.json")
    out = json.load(open(outp, encoding="utf-8")) if os.path.exists(outp) else {}
    model = None
    for n, s in enumerate(H2):
        if s["id"] in out:
            continue
        state = {x: v for x, v in s.items() if x != "id"}
        r, dt = ask(k, state, instructions)
        a = r["answers"]["action"]
        model = r.get("model", model)
        out[s["id"]] = {"choice": a["choice"], "confidence": a.get("confidence"),
                        "probabilities": a.get("probabilities"), "seconds": dt, "model": r.get("model")}
        if (n + 1) % 25 == 0:
            json.dump(out, open(outp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            print(f"{n + 1}/{len(H2)}", flush=True)
    json.dump(out, open(outp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    ids = [s["id"] for s in H2]
    agree = [out[i]["choice"] == J2[i] for i in ids]
    conf = [out[i]["confidence"] or 0.0 for i in ids]
    lat = sorted(out[i]["seconds"] for i in ids)
    lines = [f"指示文: {LANG}", f"Jev のモデル: {sorted({out[i]['model'] for i in ids})}",
             f"Jev と審判の一致(全件): {sum(agree)}/{len(ids)} = {sum(agree) / len(ids):.3f}",
             f"呼び出しの時間: 中央値 {lat[len(lat) // 2] * 1000:.0f} ms、95% {lat[int(len(lat) * .95)] * 1000:.0f} ms"]
    order = sorted(range(len(ids)), key=lambda j: -conf[j])
    top = order[:round(0.9733 * len(ids))]
    lines.append(f"確信度の高い順に 97.3% に絞った時(P6 と同じ覆い): {sum(agree[j] for j in top)}/{len(top)} = "
                 f"{sum(agree[j] for j in top) / len(top):.3f}")
    lines.append("Jev の確信度と実際の一致:")
    for lo, hi in ((0, .5), (.5, .8), (.8, .95), (.95, 1.01)):
        m = [j for j in range(len(ids)) if lo <= conf[j] < hi]
        if m:
            lines.append(f"  [{lo},{hi}) n={len(m)} 平均確信度 {sum(conf[j] for j in m) / len(m):.3f} "
                         f"実際 {sum(agree[j] for j in m) / len(m):.3f}")
    from collections import Counter
    pairs = Counter((J2[i], out[i]["choice"]) for i in ids if out[i]["choice"] != J2[i])
    lines.append("食い違いの多い組(審判→Jev): " + ", ".join(f"{a}→{b} {c}" for (a, b), c in pairs.most_common(8)))
    lines.append("参考: 翻訳した P6 は覆い 97.3% で 93.2%、棄権を審判に回すと 93.3%。審判の再現性 95.0%。")
    txt = "\n".join(lines)
    open(os.path.join(HERE, f"jev_result{SUFFIX}.txt"), "w", encoding="utf-8").write(txt + "\n")
    print(txt)


if __name__ == "__main__":
    main()
