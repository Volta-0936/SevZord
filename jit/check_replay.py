"""入れた環境で輪が正しく動くかを、LLM を呼ばずに確かめる。
記録した走り r3 の答え(審判・翻訳役・編集役)を再生して、輪をもう一度最初から回し、
選ばれる状態・門の判定・追補・受け入れた版が r3 と同じになるかを見る。

    python check_replay.py
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
run = "check_replay"
d = os.path.join(HERE, "auto_runs", run)
shutil.rmtree(d, ignore_errors=True)
r = subprocess.run([sys.executable, os.path.join(HERE, "drive.py"), run, "--backend", "replay", "--replay-from", "r3"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace",
                   env=dict(os.environ, PYTHONIOENCODING="utf-8"))
if r.returncode:
    print(r.stdout[-2000:], r.stderr[-2000:])
    sys.exit("輪が途中で止まった")
a = json.load(open(os.path.join(d, "state.json"), encoding="utf-8"))
b = json.load(open(os.path.join(HERE, "auto_runs", "r3", "state.json"), encoding="utf-8"))
checks = {
    "受け入れた版": a["accepted"] == b["accepted"],
    "門の判定": [(g["version"], g["retry"], len(g["problems"])) for g in a["gate_log"]] ==
               [(g["version"], g["retry"], len(g["problems"])) for g in b["gate_log"]],
    "周ごとの会話": {k: v["sessions"] for k, v in a["rounds"].items()} == {k: v["sessions"] for k, v in b["rounds"].items()},
    "追補の条件": [(x["id"], x["when"]) for x in a["amendments"]] == [(x["id"], x["when"]) for x in b["amendments"]],
}
for n in sorted(os.listdir(os.path.join(HERE, "auto_runs", "r3", "judge_inbox"))):
    p = os.path.join(d, "judge_inbox", n)
    if os.path.exists(p) and open(p, "rb").read() != open(os.path.join(HERE, "auto_runs", "r3", "judge_inbox", n), "rb").read():
        checks["審判に渡した状態"] = False
checks.setdefault("審判に渡した状態", True)
for k, v in checks.items():
    print(f"{'OK ' if v else 'NG '} {k}")
shutil.rmtree(d, ignore_errors=True)
sys.exit(0 if all(checks.values()) else 1)
