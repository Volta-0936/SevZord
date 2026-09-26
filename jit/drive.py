"""自動の輪(auto_loop3.py)を、LLM を呼びながら最後まで回す運転役。

輪の決まった部分(流れを通す・選ぶ・帳簿・依頼書・門)は auto_loop3.py がする。
この台本は、輪が LLM の番で止まった時に、審判・翻訳役・編集役を呼んで答えを置き、また輪を進める。

    python drive.py r4 --backend anthropic                  # Anthropic の API(環境変数 ANTHROPIC_API_KEY)
    python drive.py r4 --backend claude-code                # Claude Code の CLI(claude -p)。LLM が自分でファイルを読み書きする
    python drive.py r9 --backend replay --replay-from r3    # 記録した走りの答えを再生する(LLM を呼ばない。試験用)

主な選択肢:
    --model NAME        審判・翻訳役・編集役の模型(既定 claude-opus-5-5。役ごとに --judge-model など)
    --parallel N        審判の会話を同時にいくつ呼ぶか(既定 3)
    --max-steps N       輪を何歩まで進めるか(既定 200)

審判の会話は、一つの依頼 = 一つの会話にする(会話の中の答えは互いに引きずられるので、会話を混ぜない)。
"""
import argparse
import concurrent.futures as cf
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import auto_loop3 as L3  # noqa: E402
from auto_loop import jload  # noqa: E402

ACTIONS = ("melee_attack", "shoot", "retreat", "drink_potion", "take_cover", "raise_alarm", "hold_position")


# ---------- 依頼文 ----------

JUDGE_RULES = """守ること:
- 判断は、状態を読んで考えて行うこと。判断のためのプログラムやスクリプトを書いたり走らせたりしないこと(規則を機械的に当てはめる道具を作らない)。
- 各状態は独立に判断する。前の状態の答えに合わせようとしなくてよい。
- 指示文が曖昧な所は、思慮深いゲームデザイナーならこう動かす、という判断で決める。"""


def judge_prompt_inline(instr, fmt, batch):
    return ("あなたはゲームの判断係(審判)です。城の番兵 NPC が、このターンにどの行動を取るべきかを、状態を一件ずつ読んで決めてください。\n\n"
            "## 指示文(方針の行には L0〜L7 の記号、追補があれば A1… の記号が付いている)\n" + instr + "\n\n" + fmt +
            "\n\n## 状態(1 行 1 状態、JSON、\"id\" 付き)\n" + batch + "\n\n" + JUDGE_RULES +
            "\n\n全部の id に答え、答え方の形の JSON を一つだけ返してください(前置きや説明は書かない)。")


def judge_prompt_files(inbox, name, outbox):
    return ("あなたはゲームの判断係(審判)です。城の番兵 NPC が、このターンにどの行動を取るべきかを、状態を一件ずつ読んで決めてください。\n\n"
            f"手順:\n1. {inbox}/INSTRUCTIONS.txt を読む(方針の行には L0〜L7、追補には A1… の記号)。\n"
            f"2. {inbox}/FORMAT.txt を読む(答え方)。\n3. {inbox}/{name}.jsonl を読む。\n"
            "4. 各状態について最もふさわしい行動を 7 つのうちから一つ選び、答え方の通りに根拠・決め手・理由を添える。\n\n" + JUDGE_RULES +
            "\n- 指定した三つのファイル以外は開かないこと。\n\n"
            f"出力: {outbox}/{name}.json に、FORMAT.txt の形の JSON を一つ書く。全部の id に答えること。書き終えたら「完了」とだけ返す。")


def compile_prompt_inline(brief):
    return ("あなたは「翻訳役」です。次の依頼書の通りに Python の方針ファイルを一つ書いてください。"
            "依頼書の「出力」の節にあるファイルへ書く代わりに、ファイルの中身だけを ```python と ``` で囲んで返してください。\n\n" + brief)


def edit_prompt_inline(brief):
    return ("あなたは「編集役」です。次の依頼書の通りに、指示文への追補を JSON で書いてください。"
            "依頼書の「出力」の節にあるファイルへ書く代わりに、JSON だけを ```json と ``` で囲んで返してください。\n\n" + brief)


def file_task_prompt(role, brief_path):
    return (f"あなたは「{role}」です。次の依頼書を読み、書かれている通りにファイルを一つ書いてください。\n\n依頼書: {brief_path}\n\n"
            "守ること:\n- 読んでよいファイルは、この依頼書だけです。ほかのファイルやフォルダは開かない・一覧しないこと。\n"
            "- 書いたファイルが正しく読めるかを確かめるために、python で import したり読み込んだりしてみることはしてよいです。\n"
            "- 書き終えたら「完了」とだけ返してください。")


# ---------- 返事から中身を取り出す ----------

def extract_block(text, lang):
    m = re.search(r"```" + lang + r"\s*\n(.*?)```", text, re.S)
    if m:
        return m.group(1)
    m = re.search(r"```\s*\n(.*?)```", text, re.S)
    return m.group(1) if m else text


def extract_json(text):
    t = extract_block(text, "json")
    i, j = t.find("{"), t.rfind("}")
    return json.loads(t[i:j + 1])


# ---------- 模型の呼び方 ----------

class Anthropic:
    def __init__(self, model, max_tokens=32000):
        self.key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        if not self.key:
            sys.exit("環境変数 ANTHROPIC_API_KEY が無い")
        self.model, self.max_tokens = model, max_tokens

    def ask(self, prompt):
        body = {"model": self.model, "max_tokens": self.max_tokens, "messages": [{"role": "user", "content": prompt}]}
        req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=json.dumps(body).encode("utf-8"),
                                     headers={"x-api-key": self.key, "anthropic-version": "2023-06-01",
                                              "content-type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=900) as r:
            d = json.load(r)
        return "".join(c.get("text", "") for c in d.get("content", []) if c.get("type") == "text")


class ClaudeCode:
    """claude -p で、ファイルを自分で読み書きする LLM を呼ぶ(このリポジトリの実験は、この形で回した)。"""
    def __init__(self, model):
        if not shutil.which("claude"):
            sys.exit("claude(Claude Code の CLI)が見つからない")
        self.model = model

    def run(self, prompt, tools="Read,Write,Bash"):
        cmd = ["claude", "-p", prompt, "--allowedTools", tools, "--permission-mode", "acceptEdits"]
        if self.model:
            cmd += ["--model", self.model]
        subprocess.run(cmd, cwd=HERE, check=True, capture_output=True, text=True, timeout=3600)


# ---------- 役ごとの仕事 ----------

class Driver:
    def __init__(self, run, backend, models, parallel, replay_from=None):
        self.run, self.backend, self.models, self.parallel, self.replay_from = run, backend, models, parallel, replay_from
        if backend == "anthropic":
            self.llm = {r: Anthropic(m) for r, m in models.items()}
        elif backend == "claude-code":
            self.llm = {r: ClaudeCode(m) for r, m in models.items()}
        self.calls = {"judge": 0, "compile": 0, "edit": 0}

    def rdir(self, *p):
        return os.path.join(L3.rd(self.run), *p)

    # 審判
    def judge(self, names):
        inbox, outbox = self.rdir("judge_inbox"), self.rdir("judge_outbox")
        os.makedirs(outbox, exist_ok=True)

        def one(name):
            out = os.path.join(outbox, name + ".json")
            if self.backend == "replay":
                shutil.copy(os.path.join(L3.rd(self.replay_from), "judge_outbox", name + ".json"), out)
                return name
            if self.backend == "claude-code":
                self.llm["judge"].run(judge_prompt_files(inbox, name, outbox), tools="Read,Write")
                return name
            instr = open(os.path.join(inbox, "INSTRUCTIONS.txt"), encoding="utf-8").read()
            fmt = open(os.path.join(inbox, "FORMAT.txt"), encoding="utf-8").read()
            batch = open(os.path.join(inbox, name + ".jsonl"), encoding="utf-8").read()
            want = [json.loads(l)["id"] for l in batch.splitlines() if l.strip()]
            for attempt in range(3):
                ans = extract_json(self.llm["judge"].ask(judge_prompt_inline(instr, fmt, batch)))
                ans = {i: r for i, r in ans.items() if isinstance(r, dict) and r.get("action") in ACTIONS}
                if all(i in ans for i in want):
                    break
            json.dump(ans, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            return name

        with cf.ThreadPoolExecutor(self.parallel) as ex:
            for name in ex.map(one, names):
                self.calls["judge"] += 1
                print(f"    審判 {name}", flush=True)

    # 翻訳役
    def compile(self, k, brief, retry):
        out = self.rdir("policies", f"c{k}.py")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        if self.backend == "replay":
            src = os.path.join(L3.rd(self.replay_from), "policies", f"c{k}_rejected{retry + 1}.py")
            if not os.path.exists(src):
                src = os.path.join(L3.rd(self.replay_from), "policies", f"c{k}.py")
            shutil.copy(src, out)
        elif self.backend == "claude-code":
            self.llm["compile"].run(file_task_prompt("翻訳役", brief))
        else:
            code = extract_block(self.llm["compile"].ask(compile_prompt_inline(open(brief, encoding="utf-8").read())), "python")
            open(out, "w", encoding="utf-8").write(code)
        self.calls["compile"] += 1

    # 編集役
    def edit(self, brief, out):
        os.makedirs(os.path.dirname(out), exist_ok=True)
        if self.backend == "replay":
            shutil.copy(os.path.join(L3.rd(self.replay_from), "amend", os.path.basename(out)), out)
        elif self.backend == "claude-code":
            self.llm["edit"].run(file_task_prompt("編集役", brief))
        else:
            doc = extract_json(self.llm["edit"].ask(edit_prompt_inline(open(brief, encoding="utf-8").read())))
            json.dump(doc, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        self.calls["edit"] += 1

    def go(self, max_steps):
        if not os.path.exists(L3.sp(self.run)):
            L3.init(self.run)
            print(f"新しい走り {self.run}")
        for _ in range(max_steps):
            st, msg = L3.step(self.run)
            print(f"[{st['phase']}] {msg}", flush=True)
            ph = st["phase"]
            if ph == "done":
                break
            if not msg.startswith("待ち"):
                continue
            k = int(ph.split("_")[1])
            if ph.startswith("judge_"):
                names = [n for n in st["rounds"][str(k)]["sessions"]
                         if not os.path.exists(self.rdir("judge_outbox", n + ".json"))]
                self.judge(names)
            elif ph.startswith("compile_"):
                self.compile(k, st["brief"], st.get("retry", 0))
            elif ph.startswith("edit_"):
                self.edit(st["brief"], st["edit"]["out"])
        print("呼んだ回数:", self.calls)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run")
    ap.add_argument("--backend", choices=["anthropic", "claude-code", "replay"], default="anthropic")
    ap.add_argument("--model", default="claude-opus-5-5")
    ap.add_argument("--judge-model")
    ap.add_argument("--compile-model")
    ap.add_argument("--edit-model")
    ap.add_argument("--parallel", type=int, default=3)
    ap.add_argument("--max-steps", type=int, default=200)
    ap.add_argument("--replay-from")
    a = ap.parse_args()
    if a.backend == "replay" and not a.replay_from:
        sys.exit("--backend replay には --replay-from が要る")
    models = {"judge": a.judge_model or a.model, "compile": a.compile_model or a.model, "edit": a.edit_model or a.model}
    Driver(a.run, a.backend, models, a.parallel, a.replay_from).go(a.max_steps)


if __name__ == "__main__":
    main()
