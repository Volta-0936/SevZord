"""lanes.sh / lanes2.sh の代わり。Windows でも Mac でも Linux でも、このフォルダで

    python run_all.py v0                 # 脊髄 v0 の 8 条件 → results\\ と集計(2 列で約 3 分)
    python run_all.py v1                 # v1・v2 の 15 条件 × 種 3 → results2\\ と集計(約 5 分)
    python run_all.py v1 grade_lazy flat_risknarrow   # 条件を選んで走らせる(種は 0,1,2)

条件の名前は exp.py の末尾と exp2.py の COND にある。numpy だけで動く(GPU 不要)。
"""
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
V0 = ["main", "sym_anchor", "exact", "sim", "necessity", "noisy", "scratchB", "brain"]


def v1_conditions():
    sys.path.insert(0, HERE)
    cwd = os.getcwd()
    os.chdir(HERE)
    try:
        from exp2 import COND
    finally:
        os.chdir(cwd)
    return list(COND)


def run(cmd):
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", PYTHONIOENCODING="utf-8")
    t = time.time()
    r = subprocess.run([sys.executable, *cmd], cwd=HERE, env=env, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    msg = f"{' '.join(cmd[1:]):<32} {time.time() - t:6.1f} 秒  " + ("済" if r.returncode == 0 else "失敗")
    print(msg, flush=True)
    if r.returncode != 0:
        print(r.stderr[-1500:], flush=True)
    return r.returncode


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("v0", "v1"):
        sys.exit(__doc__)
    which, names = sys.argv[1], sys.argv[2:]
    if which == "v0":
        jobs = [["exp.py", c] for c in (names or V0)]
        summary = "analyze.py"
    else:
        jobs = [["exp2.py", c, str(s)] for c in (names or v1_conditions()) for s in (0, 1, 2)]
        summary = "analyze2.py"
    lanes = max(1, min(4, (os.cpu_count() or 2) - 1))
    print(f"{len(jobs)} 本を {lanes} 列で走らせる", flush=True)
    t = time.time()
    with ThreadPoolExecutor(lanes) as ex:
        fails = sum(1 for rc in ex.map(run, jobs) if rc)
    print(f"全部で {time.time() - t:.0f} 秒、失敗 {fails} 本。集計:", flush=True)
    r = subprocess.run([sys.executable, summary], cwd=HERE, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    print(r.stdout[-4000:])


if __name__ == "__main__":
    main()
