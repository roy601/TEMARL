# -*- coding: utf-8 -*-
"""CAGE 4, Team cybermonic: reproduction of Table 3 (scenario CC4) with the released weights.
DECISIONS.md 7-14. Run with the Python of the CAGE 4 environment (README.md), except `report`.

    <venv python> reproductions/cage4/run.py check             # versions, commits, weights -> out/ENVIRONMENT.json
    <venv python> reproductions/cage4/run.py verify            # our loop == official run_evaluation (seed 0, 2 episodes)
    <venv python> reproductions/cage4/run.py run --workers 10  # seeds 0-9 x 100 episodes, one process per seed
    python reproductions/cage4/run.py report                   # out/results.json and REPORT.md (any Python)

The episode loop is the official CAGE 4 evaluation loop (CybORG/Evaluation/evaluation.py, run_evaluation),
repeated line for line in `episode()` to keep each episode's score; `verify` checks it against the official
function. A finished seed is never run again (its file is kept); `report` refuses until all 10 exist.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import statistics
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXT = HERE / "external"
ENV_DIR = EXT / "cage-challenge-4"
SUB_DIR = EXT / "cage-4-submission"
OUT = HERE / "out"
SEEDS = tuple(range(10))
EPISODES = 100
EPISODE_LENGTH = 500
T_975_DF9 = 2.2621571627982264                 # Student t, 0.975 quantile, 9 degrees of freedom
TEAM_ATTEMPTED = "Teamcybermonic"
SCENARIO_ATTEMPTED = "CC4"


# ── the official loop ─────────────────────────────────────────────────────────

def episode(wrapped, agents) -> tuple:
    """One episode, exactly as run_evaluation scores it: sum over steps of the mean of the agents' rewards,
    stopping BEFORE adding the step at which every agent is done. Returns (score, steps scored)."""
    observations, _ = wrapped.reset()
    r = []
    for _ in range(EPISODE_LENGTH):
        actions = {
            agent_name: agent.get_action(observations[agent_name], wrapped.action_space(agent_name))
            for agent_name, agent in agents.items()
            if agent_name in wrapped.agents
        }
        observations, rew, term, trunc, info = wrapped.step(actions)
        done = {agent: term.get(agent, False) or trunc.get(agent, False) for agent in wrapped.agents}
        if all(done.values()):
            break
        r.append(statistics.mean(rew.values()))
    return sum(r), len(r)


# ── environment set-up (venv only) ────────────────────────────────────────────

def load():
    """Import CybORG and the submission from the pinned clones; refuse if they are not pinned and unchanged."""
    sys.path.insert(0, str(HERE))
    import fetch
    bad = fetch.check()
    if bad:
        raise SystemExit("run fetch.py first:\n  " + "\n  ".join(bad))
    for p in (str(ENV_DIR), str(SUB_DIR)):
        if p not in sys.path:
            sys.path.insert(0, p)
    from CybORG import CybORG, CYBORG_VERSION
    from CybORG.Agents import SleepAgent, EnterpriseGreenAgent, FiniteStateRedAgent
    from CybORG.Simulator.Scenarios import EnterpriseScenarioGenerator
    from submission import Submission
    return {"CybORG": CybORG, "version": CYBORG_VERSION, "Sleep": SleepAgent, "Green": EnterpriseGreenAgent,
            "Red": FiniteStateRedAgent, "SG": EnterpriseScenarioGenerator, "Submission": Submission}


def seed_all(seed: int):
    import numpy as np
    import torch
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def make_env(L, seed: int):
    sg = L["SG"](blue_agent_class=L["Sleep"], green_agent_class=L["Green"], red_agent_class=L["Red"],
                 steps=EPISODE_LENGTH)
    cyborg = L["CybORG"](sg, "sim", seed=seed)
    return L["Submission"].wrap(cyborg)


def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1), encoding="utf-8")
    os.replace(tmp, path)


def seed_file(seed: int) -> Path:
    return OUT / f"episodes_seed{seed}.json"


def run_seed(seed: int, episodes: int, dest: Path):
    import torch
    torch.set_num_threads(1)
    L = load()
    seed_all(seed)
    wrapped = make_env(L, seed)
    agents = L["Submission"].AGENTS
    rows, t0 = [], time.time()
    for i in range(episodes):
        t = time.time()
        score, steps = episode(wrapped, agents)
        rows.append({"episode": i, "score": score, "steps": steps, "seconds": round(time.time() - t, 2)})
        print(f"seed {seed} episode {i + 1}/{episodes}: {score:.1f} ({steps} steps)", flush=True)
    write_json(dest, {"seed": seed, "episodes": rows, "n": len(rows), "mean": statistics.mean(r["score"] for r in rows),
                      "stdev": statistics.stdev(r["score"] for r in rows) if len(rows) > 1 else None,
                      "seconds": round(time.time() - t0, 1), "cyborg_version": L["version"]})


# ── stages ────────────────────────────────────────────────────────────────────

def stage_check():
    import importlib.metadata as md
    import platform
    sys.path.insert(0, str(HERE))
    import fetch
    L = load()
    env = {"python": sys.version, "platform": platform.platform(), "machine": platform.node(),
           "cyborg_version": L["version"],
           "commits": {n: fetch.git(EXT / n, "rev-parse", "HEAD") for n in fetch.REPOS},
           "released_files_sha256_ok": True,
           "packages": sorted(f"{d.metadata['Name']}=={d.version}" for d in md.distributions()),
           "agents": sorted(L["Submission"].AGENTS)}
    write_json(OUT / "ENVIRONMENT.json", env)
    key = {p.split("==")[0].lower(): p for p in env["packages"]}
    print("check OK:", env["cyborg_version"], "|", ", ".join(key.get(k, k + " missing") for k in
                                                         ("numpy", "torch", "torch-geometric", "ray", "gymnasium")))


def stage_verify():
    """Official run_evaluation and our loop, each in a fresh process with the same seeds: same mean."""
    def child(code):
        r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, cwd=str(HERE))
        if r.returncode != 0:
            raise SystemExit(r.stdout[-2000:] + r.stderr[-3000:])
        return r.stdout
    pre = (f"import sys; sys.path.insert(0, {str(HERE)!r}); import run as R; L = R.load(); R.seed_all(0); "
           f"import torch; torch.set_num_threads(1); ")
    official = child(pre + "from CybORG.Evaluation.evaluation import run_evaluation; "
                     "run_evaluation(L['Submission'], log_path='unused', max_eps=2, write_to_file=False, seed=0)")
    ours = child(pre + "w = R.make_env(L, 0); s = [R.episode(w, L['Submission'].AGENTS)[0] for _ in range(2)]; "
                 "import statistics; print('OURS', repr(statistics.mean(s)), repr(s))")
    want = float(official.split("Average reward is: ")[1].split(" with")[0])
    got = float(ours.split("OURS ")[1].split(" ")[0])
    same = got == want
    write_json(OUT / "VERIFY.json", {"seed": 0, "episodes": 2, "official_mean": want, "our_mean": got, "pass": same})
    print(f"verify: official run_evaluation mean {want!r}, our loop {got!r} -> {'PASS' if same else 'FAIL'}")
    if not same:
        raise SystemExit(1)


def stage_run(workers: int):
    v = OUT / "VERIFY.json"
    if not (v.exists() and json.loads(v.read_text(encoding="utf-8"))["pass"]):
        raise SystemExit("run `verify` first")
    todo = [s for s in SEEDS if not seed_file(s).exists()]
    print(f"{len(SEEDS) - len(todo)} seeds already finished; running {todo} with {workers} workers")
    logs = OUT / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    running, t0 = {}, time.time()
    while todo or running:
        while todo and len(running) < workers:
            s = todo.pop(0)
            fh = (logs / f"seed{s}.log").open("w", encoding="utf-8")
            running[s] = (subprocess.Popen([sys.executable, "-W", "ignore", str(HERE / "run.py"), "seed", "--seed", str(s)],
                                           stdout=fh, stderr=subprocess.STDOUT, cwd=str(HERE)), fh)
        time.sleep(5)
        for s, (p, fh) in list(running.items()):
            if p.poll() is not None:
                fh.close()
                del running[s]
                ok = p.returncode == 0 and seed_file(s).exists()
                print(f"seed {s}: {'done' if ok else 'FAILED (see out/logs/seed%d.log)' % s} "
                      f"after {(time.time() - t0) / 60:.1f} min", flush=True)
                if not ok:
                    raise SystemExit(1)
    print("all seeds finished; next: python reproductions/cage4/run.py report")


# ── report (pure; tested) ─────────────────────────────────────────────────────

def summarise(seed_rows: dict) -> dict:
    """seed_rows[seed] = list of episode scores."""
    means = [statistics.mean(v) for _, v in sorted(seed_rows.items())]
    allv = [x for _, v in sorted(seed_rows.items()) for x in v]
    m = statistics.mean(allv)
    sd_m = statistics.stdev(means)
    half = T_975_DF9 * sd_m / math.sqrt(len(means)) if len(means) == 10 else float("nan")
    sd_e = statistics.stdev(allv)
    return {"mean": m, "ci_seed_level": [m - half, m + half], "seed_means": means,
            "seed_stdevs": [statistics.stdev(v) for _, v in sorted(seed_rows.items())],
            "episode_stdev": sd_e, "ci_episode_level": [m - 1.96 * sd_e / math.sqrt(len(allv)),
                                                        m + 1.96 * sd_e / math.sqrt(len(allv))],
            "episodes": len(allv), "seeds": len(means)}


def verdict(published: float, published_std: float, s: dict) -> str:
    lo, hi = s["ci_seed_level"]
    if lo <= published <= hi:
        return "MATCH"
    if abs(s["mean"] - published) <= published_std:
        return "CLOSE"
    return "NO MATCH"


def published_std(quantity: str) -> float:
    return float(quantity.split("published std ")[1].split(")")[0].split(",")[0])


def not_attempted_reason(target_id: str) -> str:
    team, scen = target_id.split(".")[1], target_id.split(".")[2]
    if team != TEAM_ATTEMPTED:
        return "no code released by this team (DECISIONS 3, 6)"
    return "the environment provides no configuration for this variation (DECISIONS 4, 12)"


def report(out: Path = OUT, dest: Path = HERE / "REPORT.md") -> dict:
    files = {s: out / f"episodes_seed{s}.json" for s in SEEDS}
    missing = [s for s, f in files.items() if not f.exists()]
    if missing:
        raise SystemExit(f"seeds not finished: {missing}")
    data = {s: json.loads(f.read_text(encoding="utf-8")) for s, f in files.items()}
    for s, d in data.items():
        if d["seed"] != s or d["n"] != EPISODES:
            raise SystemExit(f"seed {s}: wrong seed or {d['n']} episodes")
    s = summarise({k: [r["score"] for r in d["episodes"]] for k, d in data.items()})
    targets = list(csv.DictReader((HERE / "TARGETS.csv").open(encoding="utf-8")))
    rows = []
    for t in targets:
        pub = float(t["published"])
        team, scen = t["id"].split(".")[1], t["id"].split(".")[2]
        if team == TEAM_ATTEMPTED and scen == SCENARIO_ATTEMPTED:
            v = verdict(pub, published_std(t["quantity"]), s)
            rows.append({"id": t["id"], "published": pub, "ours": s["mean"], "difference": s["mean"] - pub, "verdict": v})
        else:
            rows.append({"id": t["id"], "published": pub, "ours": None, "difference": None, "verdict": "NOT ATTEMPTED",
                         "reason": not_attempted_reason(t["id"])})
    env = json.loads((out / "ENVIRONMENT.json").read_text(encoding="utf-8")) if (out / "ENVIRONMENT.json").exists() else {}
    res = {"summary": s, "targets": rows, "environment": {k: env.get(k) for k in ("python", "cyborg_version", "commits", "machine")}}
    write_json(out / "results.json", res)
    main_v = next(r for r in rows if r["id"] == f"T3.{TEAM_ATTEMPTED}.{SCENARIO_ATTEMPTED}")["verdict"]
    paper = {"MATCH": "reproduced (scenario CC4); the five variations not attempted",
             "CLOSE": "partially reproduced: scenario CC4 CLOSE, not MATCH; the five variations not attempted",
             "NO MATCH": "not reproduced: scenario CC4 NO MATCH; the five variations not attempted"}[main_v]
    L = ["# CAGE 4 (Kiely et al., AI Magazine 2025), Table 3: Team cybermonic", "",
         f"**Paper verdict: {paper}.** Released code and weights, unchanged (DECISIONS 7); one trained policy, so the",
         "interval covers evaluation randomness only (DECISIONS 10).", "",
         "## Scenario CC4", "",
         f"- Ours: mean **{s['mean']:.1f}** over {s['episodes']} episodes ({s['seeds']} seeds x {EPISODES}); "
         f"95% CI over the seed means [{s['ci_seed_level'][0]:.1f}, {s['ci_seed_level'][1]:.1f}]; "
         f"episode-level CI [{s['ci_episode_level'][0]:.1f}, {s['ci_episode_level'][1]:.1f}]; episode std {s['episode_stdev']:.1f}.",
         "- Published (Table 3): -193 ± 84 (one 100-episode evaluation; the team's leaderboard score -193.68).",
         "- Each seed, mean ± std of its 100 episodes (comparable to one Table 3 entry): " +
         "; ".join(f"s{k} {m:.1f} ± {sd:.1f}" for k, m, sd in zip(SEEDS, s["seed_means"], s["seed_stdevs"])) + ".", "",
         "## Every target", "",
         "| id | quantity | published | ours | difference | verdict |", "|---|---|---|---|---|---|"]
    for r in rows:
        if r["ours"] is None:
            L.append(f"| {r['id']} | mean episode reward ({r['reason']}) | {r['published']:g} | - | - | {r['verdict']} |")
        else:
            L.append(f"| {r['id']} | mean episode reward, 100 episodes x 500 steps | {r['published']:g} | "
                     f"{r['ours']:.1f} [{s['ci_seed_level'][0]:.1f}, {s['ci_seed_level'][1]:.1f}] | {r['difference']:+.1f} | {r['verdict']} |")
    L += ["", "## Environment", "",
          f"- {env.get('python', '?').split()[0] if env else '?'}; CybORG {env.get('cyborg_version', '?')}; "
          f"commits {env.get('commits', {})}; machine {env.get('machine', '?')}. Full package list: `out/ENVIRONMENT.json`.",
          "- Changes from the 2024 software, all declared before the run (DECISIONS 8): Ray 2.10.0 for 2.12.0 (no",
          "  Windows build), torch_geometric 2.3.1 (the submission's pin), unpinned packages resolved as of 2024-06-15.",
          "- Our loop was checked against the official `run_evaluation` (`out/VERIFY.json`).", "",
          "Every episode: `out/episodes_seed0.json` ... `out/episodes_seed9.json`.", ""]
    dest.write_text("\n".join(L), encoding="utf-8")
    sys.stdout.reconfigure(errors="replace")                 # Windows consoles may not print the ± sign
    print("\n".join(L[:12]))
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=["check", "verify", "run", "seed", "report"])
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--seed", type=int)
    ap.add_argument("--episodes", type=int, default=EPISODES)
    a = ap.parse_args()
    if a.stage == "check":
        stage_check()
    elif a.stage == "verify":
        stage_verify()
    elif a.stage == "run":
        stage_run(a.workers)
    elif a.stage == "seed":
        if a.seed not in SEEDS or a.episodes != EPISODES:
            raise SystemExit("seed must be 0-9 and episodes 100 (DECISIONS 10)")
        if seed_file(a.seed).exists():
            raise SystemExit(f"seed {a.seed} already finished")
        run_seed(a.seed, a.episodes, seed_file(a.seed))
    else:
        report()


if __name__ == "__main__":
    main()
