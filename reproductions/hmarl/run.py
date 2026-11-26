# -*- coding: utf-8 -*-
"""H-MARL (Singh et al., RLJ 2025): evaluate the three released methods with the authors' own evaluation code,
unchanged, and compare with Tables 2 and 3. DECISIONS.md. Stages `verify`, `seed` and `recheck` run in the venv
(README.md); `run` and `report` run with any Python 3.9+ (standard library only).

    python reproductions/hmarl/fetch.py
    <venv python> reproductions/hmarl/run.py check                 # versions, pins -> out/ENVIRONMENT.json
    <venv python> reproductions/hmarl/run.py verify                # metrics flag changes nothing; seeds repeat
    python reproductions/hmarl/run.py run --workers 4              # 3 methods x seeds 0-9 x 100 episodes
    python reproductions/hmarl/run.py report                       # TARGETS.csv vs ours -> REPORT.md
    <venv python> reproductions/hmarl/run.py recheck --method HMARL_Expert --seed 0   # another machine

Each (method, seed) runs the authors' `evaluation_metrics.run_evaluation(..., max_eps=100, seed=s)` unchanged, with
the authors' COMPUTE_METRICS switch set to True at run time (their README's instruction; no file is edited) and
Python `random`, NumPy and torch seeded with s. Its printed output is kept in out/logs; the per-episode rewards are
recovered from its running means, and the Table 3 metrics are read from its last summary (DECISIONS 6-8).
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import io
import json
import math
import os
import platform
import random
import statistics
import subprocess
import sys
import time
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXT = HERE / "external"
REPO = EXT / "Hierarchical-MARL"
ENV_DIR = EXT / "cage-challenge-4"
VENV_PY = EXT / "venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
OUT = HERE / "out"
METHODS = {                         # Table row -> (working directory, evaluator directory) (DECISIONS 3)
    "HMARL_Expert": ("h-marl-3policy", "subpolicies"),
    "HMARL_Meta": ("h-marl-3policy", "master"),
    "MARL_Decentralized": ("marl-1policy", "."),
}
SEEDS = tuple(range(10))
EPISODES = 100
T_975_DF9 = 2.2621571627982264
PY_VERSION = "3.10"
METRICS = ("reward", "clean_hosts", "non_escalated_hosts", "mean_time_to_recover", "useful_recoveries",
           "wasted_recoveries", "recovery_precision", "recovery_error", "red_impact_count")


# ── parsing the authors' printed output (pure; tested) ───────────────────────

def last_value(text: str, prefix: str) -> float:
    lines = [ln for ln in text.splitlines() if ln.startswith(prefix)]
    if not lines:
        raise ValueError(f"no line starts with {prefix!r}")
    return float(lines[-1][len(prefix):].split()[0])


def episode_rewards(text: str) -> list:
    """The authors print `Episode: i <running mean>` after each episode; episode i's reward is recovered as
    (i+1) m_i - i m_(i-1)."""
    means = []
    for ln in text.splitlines():
        if ln.startswith("Episode: "):
            i, m = ln.split()[1:3]
            if int(i) != len(means):
                raise ValueError(f"episode {i} out of order")
            means.append(float(m))
    return [(i + 1) * m - i * (means[i - 1] if i else 0.0) for i, m in enumerate(means)]


def impact_totals(text: str, episodes: int) -> list:
    """Red Impact Count per episode: the sum over red agents of the per-episode Impact counts that the authors'
    script prints, in full, after the last episode (only Impact on operational hosts is counted; DECISIONS 7)."""
    block = text[text.rfind("Episode: "):]
    per_agent = {}
    for ln in block.splitlines():
        if ln.startswith("red_agent_") and " Impact [" in ln and "] mean " in ln:
            start = ln.rfind(" Impact [") + len(" Impact ")
            per_agent[ln.split()[0]] = ast.literal_eval(ln[start:ln.rfind("] mean ") + 1])
    if not per_agent:
        raise ValueError("no Impact lines after the last episode")
    if any(len(v) != episodes for v in per_agent.values()):
        raise ValueError("an Impact list does not have one entry per episode")
    return [sum(v[i] for v in per_agent.values()) for i in range(episodes)]


def parse_log(text: str) -> dict:
    rewards = episode_rewards(text)
    n = len(rewards)
    tp, fp = last_value(text, "True pos across subnets: "), last_value(text, "False pos across subnets: ")
    impacts = impact_totals(text, n)
    avg = last_value(text, "Average reward is: ")
    if abs(avg - statistics.mean(rewards)) > 1e-6:
        raise ValueError(f"recovered rewards average {statistics.mean(rewards)}, the script printed {avg}")
    return {"episodes": n, "rewards": rewards, "impacts": impacts, "metrics": {
        "reward": statistics.mean(rewards),
        "clean_hosts": last_value(text, "Noninfection frac across subnets: "),
        "non_escalated_hosts": last_value(text, "Nonprivileged frac across subnets: "),
        "mean_time_to_recover": last_value(text, "Mean stride across subnets: "),
        "useful_recoveries": tp, "wasted_recoveries": fp,
        "recovery_precision": tp / (tp + fp) if tp + fp else float("nan"),
        "recovery_error": fp / (tp + fp) if tp + fp else float("nan"),
        "red_impact_count": statistics.mean(impacts)}}


# ── statistics and verdicts (pure; tested) ───────────────────────────────────

def summarise(values: list) -> dict:
    """values: one per seed (each a 100-episode evaluation, as one published table entry)."""
    n, m = len(values), statistics.mean(values)
    sd = statistics.stdev(values) if n > 1 else float("nan")
    t = T_975_DF9 if n == 10 else float("nan")
    return {"mean": m, "seeds": n, "seed_sd": sd, "ci": [m - t * sd / math.sqrt(n), m + t * sd / math.sqrt(n)],
            "prediction": [m - t * sd * math.sqrt(1 + 1 / n), m + t * sd * math.sqrt(1 + 1 / n)],
            "range": [min(values), max(values)]}


def decimals(published: str) -> int:
    s = published.strip()
    return len(s.split(".")[1]) if "." in s else 0


def overlaps(lo: float, hi: float, a: float, b: float) -> bool:
    return lo <= b and a <= hi


def verdict(s: dict, published: str, tolerance: str, published_sd: float = None) -> str:
    """DECISIONS 9. The printed value stands for an interval of half a unit of its last digit.
    MATCH: that interval meets our 95% CI of the mean over 10 seeds.
    CLOSE (reward): our mean within one published episode std; CLOSE (other metrics): the interval meets our 95%
    prediction interval for one 100-episode evaluation. Else NO MATCH."""
    t = tolerance.strip().upper()
    if t.startswith("NOT ATTEMPTED"):
        return "NOT ATTEMPTED"
    p, h = float(published), 0.5 * 10 ** (-decimals(published))
    if overlaps(p - h, p + h, *s["ci"]):
        return "MATCH"
    if t.startswith("REWARD"):
        return "CLOSE" if published_sd is not None and abs(s["mean"] - p) <= published_sd + h else "NO MATCH"
    return "CLOSE" if overlaps(p - h, p + h, *s["prediction"]) else "NO MATCH"


def published_sd(quantity: str):
    return float(quantity.split("published std ")[1].split(")")[0].split(",")[0]) if "published std " in quantity else None


def target_key(target_id: str):
    """(method, metric) for an attempted target id, or None.
    T2.<method>.Default.mean -> reward; T3.<method>.<metric>."""
    p = target_id.split(".")
    if p[0] == "T2" and len(p) == 4 and p[1] in METHODS and p[2] == "Default" and p[3] == "mean":
        return p[1], "reward"
    if p[0] == "T3" and len(p) == 3 and p[1] in METHODS and p[2] in METRICS:
        return p[1], p[2]
    return None


# ── the venv side ─────────────────────────────────────────────────────────────

def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1), encoding="utf-8")
    os.replace(tmp, path)


def seed_file(method: str, seed: int, out: Path = OUT) -> Path:
    return out / "seeds" / f"{method}_seed{seed}.json"


_PREPARED = []


def prepare(method: str, plain: bool = False):
    """Enter the method's directory, import the authors' evaluator and submission; return (module, Submission).
    One method per process: Python caches `evaluation_metrics` and `submission`, so a second method in the same
    process would silently reuse the first one's code and policies."""
    if _PREPARED and _PREPARED[0] != (method, plain):
        raise RuntimeError(f"{_PREPARED[0]} already loaded in this process; run {(method, plain)} in a new process")
    _PREPARED.append((method, plain))
    sys.path.insert(0, str(HERE))
    import fetch
    bad = fetch.check()
    if bad:
        raise SystemExit("run fetch.py first:\n  " + "\n  ".join(bad))
    work, sub = METHODS[method]
    os.chdir(REPO / work)
    script_dir = str((REPO / work / sub).resolve())
    for p in (script_dir, str(ENV_DIR)):
        if p not in sys.path:
            sys.path.insert(0, p)
    import torch
    torch.set_num_threads(1)
    import importlib
    E = importlib.import_module("evaluation" if plain else "evaluation_metrics")
    Submission = E.load_submission(script_dir)
    import BlueFlatWrapper_CC4 as W                 # the module the submission's wrapper uses
    W.COMPUTE_METRICS = not plain                   # the authors' switch (README), set at run time
    return E, Submission


def seed_all(seed: int):
    import numpy as np
    import torch
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def evaluate(method: str, seed: int, episodes: int, plain: bool = False) -> str:
    """One call of the authors' run_evaluation; returns everything it printed."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        E, Submission = prepare(method, plain)
        seed_all(seed)
        t0 = time.time()
        E.run_evaluation(Submission, log_path="unused", max_eps=episodes, write_to_file=False, seed=seed)
        print(f"WALL_SECONDS {time.time() - t0:.1f}")
    return buf.getvalue()


def stage_seed(method: str, seed: int):
    dest = seed_file(method, seed)
    if dest.exists():
        raise SystemExit(f"{dest.name} exists: results are never overwritten")
    text = evaluate(method, seed, EPISODES)
    log = OUT / "logs" / f"{method}_seed{seed}.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(text, encoding="utf-8")
    res = parse_log(text)
    if res["episodes"] != EPISODES:
        raise SystemExit(f"{res['episodes']} episodes, expected {EPISODES}")
    write_json(dest, {"method": method, "seed": seed, "machine": platform.node(), **res,
                      "log_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()})
    print(f"{method} seed {seed}: reward {res['metrics']['reward']:.2f}")


def stage_check():
    import importlib.metadata as md
    sys.path.insert(0, str(HERE))
    import fetch
    bad = fetch.check()
    if not sys.version.startswith(PY_VERSION + "."):
        bad.append(f"Python {sys.version.split()[0]}; the released policies need {PY_VERSION} (DECISIONS 4)")
    if bad:
        raise SystemExit("check FAILED:\n  " + "\n  ".join(bad))
    env = {"python": sys.version, "platform": platform.platform(), "machine": platform.node(),
           "commits": {n: fetch.git(EXT / n, "rev-parse", "HEAD") for n in fetch.REPOS},
           "packages": sorted(f"{d.metadata['Name']}=={d.version}" for d in md.distributions())}
    write_json(OUT / "ENVIRONMENT.json", env)
    key = {p.split("==")[0].lower(): p for p in env["packages"]}
    print("check OK:", sys.version.split()[0], "|", ", ".join(key.get(k, k + " missing") for k in ("ray", "torch", "numpy", "gym")))


def stage_verify():
    """For each method, in fresh processes, seed 0, 2 episodes: (a) the authors' plain evaluation.py and (b) their
    evaluation_metrics.py with the metrics switch on must print the same average reward, and (c) a second run of
    (b) must repeat it exactly."""
    rep, ok = {}, True
    for m in METHODS:
        got = []
        for plain in (True, False, False):
            code = (f"import sys; sys.path.insert(0, {str(HERE)!r}); import run as R; "
                    f"t = R.evaluate({m!r}, 0, 2, plain={plain}); print('AVG', R.last_value(t, 'Average reward is: '))")
            r = subprocess.run([sys.executable, "-W", "ignore", "-c", code], capture_output=True, text=True)
            if r.returncode != 0:
                raise SystemExit(r.stdout[-1500:] + r.stderr[-3000:])
            got.append(float(r.stdout.split("AVG ")[-1].split()[0]))
        same = got[0] == got[1] == got[2]
        rep[m] = {"plain": got[0], "metrics": got[1], "metrics_again": got[2], "pass": same}
        ok = ok and same
        print(f"verify {m}: plain {got[0]!r}, with metrics {got[1]!r}, again {got[2]!r} -> {'PASS' if same else 'FAIL'}")
    write_json(OUT / "VERIFY.json", {"seed": 0, "episodes": 2, "methods": rep, "pass": ok})
    if not ok:
        raise SystemExit(1)


def stage_recheck(method: str, seed: int, episodes: int = 3):
    kept = json.loads(seed_file(method, seed).read_text(encoding="utf-8"))["rewards"][:episodes]
    again = episode_rewards(evaluate(method, seed, episodes))
    same = all(abs(a - b) < 1e-9 for a, b in zip(kept, again)) and len(again) == episodes
    dest = OUT / f"RECHECK_{platform.node()}_{method}_seed{seed}.json"
    write_json(dest, {"machine": platform.node(), "method": method, "seed": seed, "episodes": episodes,
                      "kept": kept, "again": again, "identical": same})
    print(f"recheck {method} seed {seed} on {platform.node()}: {'IDENTICAL' if same else 'DIFFERENT'} -> {dest.name}")


# ── orchestration (any Python) ───────────────────────────────────────────────

def targets_committed() -> bool:
    def git(*a):
        return subprocess.run(["git", *a], cwd=str(HERE), capture_output=True, text=True).stdout.strip()
    names = ("TARGETS.csv", "DECISIONS.md")
    return all(git("log", "-1", "--format=%H", "--", n) for n in names) and not git("status", "--porcelain", "--", *names)


def stage_run(workers: int):
    if not targets_committed():
        raise SystemExit("TARGETS.csv and DECISIONS.md must be committed, unchanged, before the first run")
    v = OUT / "VERIFY.json"
    if not (v.exists() and json.loads(v.read_text(encoding="utf-8"))["pass"]):
        raise SystemExit("run `verify` first")
    todo = [(m, s) for s in SEEDS for m in METHODS if not seed_file(m, s).exists()]
    print(f"{len(METHODS) * len(SEEDS) - len(todo)} runs finished; {len(todo)} to run with {workers} workers", flush=True)
    env = dict(os.environ, OMP_NUM_THREADS="1", MKL_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
               PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
    (OUT / "logs").mkdir(parents=True, exist_ok=True)
    running, failed, t0 = {}, [], time.time()
    while todo or running:
        while todo and len(running) < workers:
            m, s = todo.pop(0)
            fh = (OUT / "logs" / f"worker_{m}_seed{s}.txt").open("w", encoding="utf-8")
            running[(m, s)] = (subprocess.Popen([str(VENV_PY), "-W", "ignore", str(HERE / "run.py"), "seed",
                                                 "--method", m, "--seed", str(s)], stdout=fh, stderr=subprocess.STDOUT,
                                                env=env), fh)
        time.sleep(5)
        for (m, s), (p, fh) in list(running.items()):
            if p.poll() is not None:
                fh.close()
                del running[(m, s)]
                ok = p.returncode == 0 and seed_file(m, s).exists()
                print(f"{m} seed {s}: {'done' if ok else 'FAILED (out/logs/worker_' + m + '_seed' + str(s) + '.txt)'} "
                      f"after {(time.time() - t0) / 60:.1f} min", flush=True)
                if not ok:
                    failed.append((m, s))
    if failed:
        raise SystemExit(f"failed: {failed}; start `run` again (finished runs are kept)")
    print("all runs finished; next: python reproductions/hmarl/run.py report")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=["check", "verify", "run", "seed", "recheck", "report"])
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--method", choices=list(METHODS))
    ap.add_argument("--seed", type=int)
    a = ap.parse_args()
    if a.stage == "check":
        stage_check()
    elif a.stage == "verify":
        stage_verify()
    elif a.stage == "run":
        stage_run(a.workers)
    elif a.stage == "seed":
        if a.method is None or a.seed not in SEEDS:
            raise SystemExit("--method and a seed 0-9")
        stage_seed(a.method, a.seed)
    elif a.stage == "recheck":
        stage_recheck(a.method or "HMARL_Expert", 0 if a.seed is None else a.seed)
    else:
        import report_hmarl
        report_hmarl.report()


if __name__ == "__main__":
    main()
