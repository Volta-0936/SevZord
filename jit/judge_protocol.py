"""r2 の審判への渡し方(理由つき)。指示文に行の記号を付け、追補を足し、答え方を決める。"""
import re

from task import INSTRUCTIONS

FORMAT = """# 答え方

各状態について、次の 4 つを返す。

- action: 7 つの行動のどれか(英字そのまま)。
- basis: この判断の根拠。
  - 指示文の行を使ったなら、その行の記号("L2" など。複数なら "L2,L5")。
  - 追補を使ったなら、その記号("A1" など)。
  - 指示文にも追補にも書いていない所を、自分の判断で埋めたなら "gap"。
  - 指示文の行どうしがぶつかり、どちらを取るかを自分で決めたなら、使った行の記号に "+gap" を付ける(例 "L2,L4+gap")。
- factors: 決め手になった状態の項目を 1〜3 個。"項目=値"、"項目>=数"、"項目<=数" の形で書く(例 ["arrows=0", "distance>=2", "cover=true"])。
- why: 一文の理由(日本語、40 字くらいまで)。

basis と factors は、あなたが実際にその行動を選んだ理由を正直に書くこと。書いていない所を自分で決めたなら、隠さず gap と書くこと。gap は悪いことではない。

出力の形(JSON 一つ):
{"<id>": {"action": "hold_position", "basis": "L7", "factors": ["enemy=none"], "why": "脅威が無いので持ち場を守る"}, ...}
"""


def numbered(amendments=()):
    """指示文の方針の部分(1 行目と箇条書き)に L0..L7 を付け、追補 A1.. を足す。"""
    lines = INSTRUCTIONS.split("\n")
    out, n = [], 0
    for ln in lines:
        if n == 0 and ln.strip() and not ln.startswith("-"):
            out.append(f"L0 {ln}")
            n = 1
        elif ln.startswith("- "):
            out.append(f"L{n} {ln[2:]}")
            n += 1
        else:
            out.append(ln)
    text = "\n".join(out)
    if amendments:
        add = ["", "追補(審判の会話の多数から足した一文。指示文と同じ重みで使う):"]
        add += [f"{a['id']} {a['text']}" for a in amendments]
        # 行動と状態の項目の説明の前に入れる
        i = text.index("\n\n行動:")
        text = text[:i] + "\n" + "\n".join(add) + text[i:]
    return text


def parse_basis(b):
    """"L2,L5+gap" → ({"L2","L5"}, True)。"gap" → (set(), True)。"""
    b = str(b or "")
    gap = "gap" in b.lower()
    refs = set(re.findall(r"[LA]\d+", b))
    return refs, gap
