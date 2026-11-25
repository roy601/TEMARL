# -*- coding: utf-8 -*-
"""CAGE 4: reproduction of Table 3 (scenario CC4) for the two teams that released code, cybermonic
(trained graph PPO agents) and punch (Analyse Restore v1 heuristic). DECISIONS.md 7-15.
Run with the Python of the CAGE 4 environment (README.md), except `report`.

    <venv python> reproductions/cage4/run.py check             # versions, commits, files -> out/ENVIRONMENT.json
    <venv python> reproductions/cage4/run.py verify            # our loop == official run_evaluation, each team
    <venv python> reproductions/cage4/run.py run --workers 10  # 2 teams x seeds 0-9 x 100 episodes
    <venv python> reproductions/cage4/run.py recheck --team Teamcybermonic --seed 0   # 3 kept episodes rerun
    python reproductions/cage4/run.py report    # out/results.json, out/HASHES.txt and REPORT.md (any Python)

The episode loop is the official CAGE 4 evaluation loop (CybORG/Evaluation/evaluation.py, run_evaluation),
repeated line for line in `episode()` to keep each episode's score; `verify` checks it against the official
function. A finished (team, seed) is never run again (its file is kept); `report` refuses until all exist.
`report` only reads the kept files: it can be run again (for example after another machine's recheck).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
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
OUT = HERE / "out"
TEAMS = {   # Table 3 team id -> released submission folder (DECISIONS 7, 15)
    "Teamcybermonic": EXT / "cage-4-submission",
    "Teampunch": EXT / "cage-4-submissions-punch" / "punch_analyse_restore_v1",
}
SEEDS = tuple(range(10))
EPISODES = 100
EPISODE_LENGTH = 500
T_975_DF9 = 2.2621571627982264                 # Student t, 0.975 quantile, 9 degrees of freedom
SCENARIO_ATTEMPTED = "CC4"
LEADERBOARD = {"Teamcybermonic": -193.68, "Teampunch": -142.72}   # the teams' READMEs; Table 3 truncates


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

def load(team: str):
    """Import CybORG and one team's submission from the pinned clones; refuse unless pinned and unchanged."""
    sys.path.insert(0, str(HERE))
    import fetch
    bad = fetch.check()
    if bad:
        raise SystemExit("run fetch.py first:\n  " + "\n  ".join(bad))
    for p in (str(ENV_DIR), str(TEAMS[team])):
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


def seed_file(team: str, seed: int, out: Path = OUT) -> Path:
    return out / f"episodes_{team}_seed{seed}.json"


def run_seed(team: str, seed: int, episodes: int, dest: Path):
    import torch
    torch.set_num_threads(1)
    L = load(team)
    seed_all(seed)
    wrapped = make_env(L, seed)
    agents = L["Submission"].AGENTS
    rows, t0 = [], time.time()
    for i in range(episodes):
        t = time.time()
        score, steps = episode(wrapped, agents)
        rows.append({"episode": i, "score": score, "steps": steps, "seconds": round(time.time() - t, 2)})
        print(f"{team} seed {seed} episode {i + 1}/{episodes}: {score:.1f} ({steps} steps)", flush=True)
    write_json(dest, {"team": team, "seed": seed, "episodes": rows, "n": len(rows),
                      "mean": statistics.mean(r["score"] for r in rows),
                      "stdev": statistics.stdev(r["score"] for r in rows) if len(rows) > 1 else None,
                      "seconds": round(time.time() - t0, 1), "cyborg_version": L["version"]})


# ── stages ────────────────────────────────────────────────────────────────────

def stage_check():
    import importlib.metadata as md
    import platform
    sys.path.insert(0, str(HERE))
    import fetch
    L = load("Teamcybermonic")
    env = {"python": sys.version, "platform": platform.platform(), "machine": platform.node(),
           "cyborg_version": L["version"],
           "commits": {n: fetch.git(EXT / n, "rev-parse", "HEAD") for n in fetch.REPOS},
           "released_files_sha256_ok": True,
           "packages": sorted(f"{d.metadata['Name']}=={d.version}" for d in md.distributions())}
    write_json(OUT / "ENVIRONMENT.json", env)
    key = {p.split("==")[0].lower().replace("_", "-"): p for p in env["packages"]}
    print("check OK:", env["cyborg_version"], "|", ", ".join(key.get(k, k + " missing") for k in
                                                         ("numpy", "torch", "torch-geometric", "ray", "gymnasium")))


def stage_verify():
    """For each team: the official run_evaluation and our loop, each in a fresh process with the same seeds,
    must give the same mean (seed 0, 2 episodes)."""
    def child(code):
        r = subprocess.run([sys.executable, "-W", "ignore", "-c", code], capture_output=True, text=True, cwd=str(HERE))
        if r.returncode != 0:
            raise SystemExit(r.stdout[-2000:] + r.stderr[-3000:])
        return r.stdout
    rep, ok = {}, True
    for team in TEAMS:
        pre = (f"import sys; sys.path.insert(0, {str(HERE)!r}); import run as R; L = R.load({team!r}); R.seed_all(0); "
               f"import torch; torch.set_num_threads(1); ")
        official = child(pre + "from CybORG.Evaluation.evaluation import run_evaluation; "
                         "run_evaluation(L['Submission'], log_path='unused', max_eps=2, write_to_file=False, seed=0)")
        ours = child(pre + "w = R.make_env(L, 0); s = [R.episode(w, L['Submission'].AGENTS)[0] for _ in range(2)]; "
                     "import statistics; print('OURS', repr(statistics.mean(s)), repr(s))")
        want = float(official.split("Average reward is: ")[1].split(" with")[0])
        got = float(ours.split("OURS ")[1].split(" ")[0])
        rep[team] = {"official_mean": want, "our_mean": got, "pass": got == want}
        ok = ok and got == want
        print(f"verify {team}: official run_evaluation mean {want!r}, our loop {got!r} -> {'PASS' if got == want else 'FAIL'}")
    write_json(OUT / "VERIFY.json", {"seed": 0, "episodes": 2, "teams": rep, "pass": ok})
    if not ok:
        raise SystemExit(1)


def stage_run(workers: int):
    v = OUT / "VERIFY.json"
    if not (v.exists() and json.loads(v.read_text(encoding="utf-8"))["pass"]):
        raise SystemExit("run `verify` first")
    todo = [(t, s) for t in TEAMS for s in SEEDS if not seed_file(t, s).exists()]
    print(f"{len(TEAMS) * len(SEEDS) - len(todo)} (team, seed) runs already finished; {len(todo)} to run with {workers} workers")
    logs = OUT / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, OMP_NUM_THREADS="1", MKL_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1")
    running, failed, t0 = {}, [], time.time()
    while todo or running:
        while todo and len(running) < workers:
            t, s = todo.pop(0)
            fh = (logs / f"{t}_seed{s}.log").open("w", encoding="utf-8")
            running[(t, s)] = (subprocess.Popen([sys.executable, "-W", "ignore", str(HERE / "run.py"), "seed",
                                                 "--team", t, "--seed", str(s)],
                                                stdout=fh, stderr=subprocess.STDOUT, cwd=str(HERE), env=env), fh)
        time.sleep(5)
        for (t, s), (p, fh) in list(running.items()):
            if p.poll() is not None:
                fh.close()
                del running[(t, s)]
                ok = p.returncode == 0 and seed_file(t, s).exists()
                print(f"{t} seed {s}: {'done' if ok else f'FAILED (see out/logs/{t}_seed{s}.log)'} "
                      f"after {(time.time() - t0) / 60:.1f} min", flush=True)
                if not ok:
                    failed.append((t, s))          # the others go on; start `run` again to retry it
    if failed:
        raise SystemExit(f"failed: {failed}. Start `run` again: finished runs are kept, failed ones start over.")
    print("all runs finished; next: python reproductions/cage4/run.py report")


def stage_recheck(team: str, seed: int, episodes: int):
    """Run a finished seed's first episodes again (fresh process state, same seed) and compare them with its
    file: same machine = the kept files stand after a crash; another machine = machine independence."""
    import platform
    import torch
    torch.set_num_threads(1)
    kept = json.loads(seed_file(team, seed).read_text(encoding="utf-8"))["episodes"][:episodes]
    L = load(team)
    seed_all(seed)
    w = make_env(L, seed)
    again = [episode(w, L["Submission"].AGENTS)[0] for _ in range(episodes)]
    same = [k["score"] for k in kept] == again
    dest = OUT / f"RECHECK_{platform.node()}_{team}_seed{seed}.json"
    write_json(dest, {"machine": platform.node(), "team": team, "seed": seed, "episodes": episodes,
                      "kept": [k["score"] for k in kept], "again": again, "identical": same})
    print(f"recheck {team} seed {seed}, {episodes} episodes on {platform.node()}: "
          f"{'IDENTICAL' if same else 'DIFFERENT'} -> {dest.name}")


# ── report (pure; tested) ─────────────────────────────────────────────────────

def summarise(seed_rows: dict) -> dict:
    """seed_rows[seed] = list of episode scores (10 seeds)."""
    means = [statistics.mean(v) for _, v in sorted(seed_rows.items())]
    allv = [x for _, v in sorted(seed_rows.items()) for x in v]
    m = statistics.mean(allv)
    half = T_975_DF9 * statistics.stdev(means) / math.sqrt(len(means)) if len(means) == 10 else float("nan")
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
    team = target_id.split(".")[1]
    if team not in TEAMS:
        return "no code released by this team (DECISIONS 3, 6, 15)"
    return "the environment provides no configuration for this variation (DECISIONS 4, 12)"


def sha_lf(path: Path) -> str:
    """SHA-256 of a saved (text) output as git stores it, CRLF -> LF: the same on every checkout."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def write_hashes(out: Path = OUT) -> dict:
    """out/HASHES.txt: the SHA-256 of every saved output (STANDARD requirement 8), paths relative to out/."""
    files = sorted((p for p in out.rglob("*") if p.is_file() and p.name != "HASHES.txt"
                    and not p.name.endswith(".tmp")), key=lambda p: p.relative_to(out).as_posix())
    h = {p.relative_to(out).as_posix(): sha_lf(p) for p in files}
    (out / "HASHES.txt").write_bytes("".join(f"{v}  {k}\n" for k, v in h.items()).encode("utf-8"))
    return h


def rechecks(out: Path = OUT) -> list:
    """Every recheck file: on which machine a kept seed's first episodes were run again, and the outcome."""
    rows = []
    for p in sorted(out.glob("RECHECK_*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        rows.append({"file": p.name, **{k: d[k] for k in ("machine", "team", "seed", "episodes", "identical")}})
    return rows


def authors_asked(path: Path = HERE / "AUTHOR_CONTACT.md") -> bool:
    return path.exists() and "(draft, not sent)" not in path.read_text(encoding="utf-8")


def checklist(checks: list, run_machine, asked: bool) -> list:
    """The ten requirements of ../STANDARD.md, Section 2; rows 3, 5 and 8 follow the saved files."""
    other = {t: sorted({c["machine"] for c in checks if c["team"] == t and c["identical"]
                        and c["machine"] != run_machine}) for t in TEAMS}
    bad = [c for c in checks if not c["identical"]]
    if bad:
        r5 = "**no**: a recheck gave DIFFERENT scores (" + ", ".join(
            f"{c['team']} seed {c['seed']} on {c['machine']}" for c in bad) + ")"
    else:
        def second(t):
            return f"identical on a second machine ({', '.join(other[t])})" if other[t] else "**second machine not yet**"
        r5 = ("partly. Teampunch (a fixed heuristic, no training): " + second("Teampunch") +
              ". Teamcybermonic: one released trained policy, so no training seeds (DECISIONS 10); "
              "10 evaluation seeds with a 95% CI; " + second("Teamcybermonic"))
    rows = [
        ("targets committed before any result", "yes", "c6084db3 (2026-11-16) before the first result 4f293f36; `audit.py`"),
        ("gaps decided before the run", "yes", "`DECISIONS.md` 1-15 (c6084db3, 2ce5df05, fd82842e, d1c8c010) before "
         "the first run; the run log (1ec82ac2) changes no decision; notes written after the results are marked so"),
        ("authors asked about every gap", "yes" if asked else
         "**not yet**: the question about the five variations is drafted, to be posted by the user", "`AUTHOR_CONTACT.md`"),
        ("exact sources and licence", "yes", "`SOURCES.md`; released files' SHA-256 checked by `fetch.py`"),
        ("variance: two machines identical, or 10+ seeds with CI", r5, "`out/RECHECK_*.json`, DECISIONS 10"),
        ("every target reported", "yes", "table above, `audit.py`"),
        ("environment recorded", "yes", "`out/ENVIRONMENT.json`"),
        ("one command from public inputs, outputs hashed", "yes: a fixed sequence of commands (`README.md`); "
         "every saved output's SHA-256 in `out/HASHES.txt`", "`fetch.py`, `run.py`"),
        ("unit tests for each rule", "yes: the loop, statistics, verdict rule, pins, hashes and this checklist",
         "`tests/test_cage4.py`"),
        ("comparison only after this report; adaptations declared", "not started", "limits in the next section"),
    ]
    return (["## Checklist (STANDARD.md, Section 2)", "", "| # | requirement | met? | where |", "|---|---|---|---|"] +
            [f"| {i} | {a} | {b} | {c} |" for i, (a, b, c) in enumerate(rows, 1)] + [""])


def report(out: Path = OUT, dest: Path = HERE / "REPORT.md") -> dict:
    missing = [(t, s) for t in TEAMS for s in SEEDS if not seed_file(t, s, out).exists()]
    if missing:
        raise SystemExit(f"runs not finished: {missing}")
    summ = {}
    for t in TEAMS:
        data = {s: json.loads(seed_file(t, s, out).read_text(encoding="utf-8")) for s in SEEDS}
        for s, d in data.items():
            if d["seed"] != s or d["n"] != EPISODES or d.get("team", t) != t:
                raise SystemExit(f"{t} seed {s}: wrong team, seed or {d['n']} episodes")
        summ[t] = summarise({k: [r["score"] for r in d["episodes"]] for k, d in data.items()})
    targets = list(csv.DictReader((HERE / "TARGETS.csv").open(encoding="utf-8")))
    rows = []
    for tg in targets:
        pub = float(tg["published"])
        team, scen = tg["id"].split(".")[1], tg["id"].split(".")[2]
        if team in TEAMS and scen == SCENARIO_ATTEMPTED:
            s = summ[team]
            rows.append({"id": tg["id"], "published": pub, "published_std": published_std(tg["quantity"]),
                         "ours": s["mean"], "ci": s["ci_seed_level"], "difference": s["mean"] - pub,
                         "verdict": verdict(pub, published_std(tg["quantity"]), s)})
        else:
            rows.append({"id": tg["id"], "published": pub, "ours": None, "difference": None, "verdict": "NOT ATTEMPTED",
                         "reason": not_attempted_reason(tg["id"])})
    env = json.loads((out / "ENVIRONMENT.json").read_text(encoding="utf-8")) if (out / "ENVIRONMENT.json").exists() else {}
    checks = rechecks(out)
    res = {"summary": summ, "targets": rows, "rechecks": checks,
           "environment": {k: env.get(k) for k in ("python", "cyborg_version", "commits", "machine")}}
    write_json(out / "results.json", res)
    attempted = [r for r in rows if r["ours"] is not None]
    vs = {r["id"]: r["verdict"] for r in attempted}
    if all(v == "MATCH" for v in vs.values()):
        head = "reproduced for the two teams that released code (scenario CC4)"
    elif all(v == "NO MATCH" for v in vs.values()):
        head = "not reproduced (scenario CC4)"
    else:
        head = "partially reproduced: " + "; ".join(f"{k.split('.')[1]} CC4 {v}" for k, v in vs.items())
    L = ["# CAGE 4 (Kiely et al., AI Magazine 2025), Table 3: the two teams that released code", "",
         f"**Paper verdict: {head}.** Teams UC and lancer released no code, and the environment provides none of the",
         "five variations: those 20 targets are NOT ATTEMPTED. Released code and weights, unchanged (DECISIONS 7, 15).",
         "Each team is one fixed policy, so the intervals cover evaluation randomness only (DECISIONS 10).", ""]
    for t in TEAMS:
        s, r = summ[t], next(x for x in attempted if x["id"] == f"T3.{t}.{SCENARIO_ATTEMPTED}")
        L += [f"## {t}, scenario CC4", "",
              f"- Ours: mean **{s['mean']:.1f}** over {s['episodes']} episodes ({s['seeds']} seeds x {EPISODES}); "
              f"95% CI over the seed means [{s['ci_seed_level'][0]:.1f}, {s['ci_seed_level'][1]:.1f}]; "
              f"episode-level CI [{s['ci_episode_level'][0]:.1f}, {s['ci_episode_level'][1]:.1f}]; "
              f"episode std {s['episode_stdev']:.1f}.",
              f"- Published (Table 3): {r['published']:g} ± {r['published_std']:g}, one 100-episode evaluation. Verdict: **{r['verdict']}**.",
              "- Each seed, mean ± std of its 100 episodes (each comparable to one Table 3 entry): " +
              "; ".join(f"s{k} {m:.1f} ± {sd:.1f}" for k, m, sd in zip(SEEDS, s["seed_means"], s["seed_stdevs"])) + ".",
              f"- Added after the results, descriptive (no verdict changes): Table 3 is ONE 100-episode evaluation. "
              f"Our ten 100-episode evaluations range over [{min(s['seed_means']):.1f}, {max(s['seed_means']):.1f}]; "
              f"the published {r['published']:g} is {'inside' if min(s['seed_means']) <= r['published'] <= max(s['seed_means']) else 'outside'} "
              f"that range, and {sum(m >= r['published'] for m in s['seed_means'])} of 10 are at least as good. "
              f"Table 3 appears to truncate the teams' leaderboard scores ({t} README: {LEADERBOARD[t]}); against "
              f"{LEADERBOARD[t]}, {sum(m >= LEADERBOARD[t] for m in s['seed_means'])} of 10 are at least as good.", ""]
    L += ["## Every target", "", "| id | quantity | published | ours | difference | verdict |", "|---|---|---|---|---|---|"]
    for r in rows:
        if r["ours"] is None:
            L.append(f"| {r['id']} | mean episode reward ({r['reason']}) | {r['published']:g} | - | - | {r['verdict']} |")
        else:
            L.append(f"| {r['id']} | mean episode reward, 10 seeds x 100 episodes x 500 steps | {r['published']:g} | "
                     f"{r['ours']:.1f} [{r['ci'][0]:.1f}, {r['ci'][1]:.1f}] | {r['difference']:+.1f} | {r['verdict']} |")
    L += [""] + checklist(checks, env.get("machine"), authors_asked())
    L += ["## Before any comparison (requirement 10)", "",
          "Added 2026-11-25, after the results; no verdict changes. A comparison with these numbers must state:", "",
          "- Teamcybermonic is ONE released trained policy: a comparison is with that policy, not with the method "
          "trained again (retraining with its `train.py` is NOT ATTEMPTED, DECISIONS 10).",
          "- Teams UC (-113) and lancer (-118), the best in Table 3, released no code: their numbers are published "
          "values only, each one 100-episode evaluation with no stated seed.",
          "- The CAGE 4 score is a defence penalty against a scripted red agent; it does not measure engagement with "
          "real attacker command histories (DECISIONS 5, 13)."]
    for r in attempted:
        if r["verdict"] != "MATCH":
            L.append(f"- {r['id'].split('.')[1]} is {r['verdict']}, not reproduced: the published {r['published']:g} is "
                     f"outside our 95% CI; ours differs by {r['difference']:+.1f} "
                     f"({100 * abs(r['difference']) / abs(r['published']):.1f}% of the published value).")
    L += ["", "## Environment", "",
          f"- {env.get('python', '?').split()[0] if env else '?'}; CybORG {env.get('cyborg_version', '?')}; "
          f"commits {env.get('commits', {})}; seeds run on machine {env.get('machine', '?')}. Full package list: "
          "`out/ENVIRONMENT.json`.",
          "- Changes from the 2024 software, all declared before the run (DECISIONS 8): Ray 2.10.0 for 2.12.0 (no",
          "  Windows build), torch_geometric 2.3.1 (cybermonic's pin), unpinned packages resolved as of 2024-06-15.",
          "- Our loop was checked against the official `run_evaluation` for each team (`out/VERIFY.json`).",
          "- Rechecks, the first episodes of a kept seed run again (`out/RECHECK_*.json`): " +
          ("; ".join(f"{c['team']} seed {c['seed']}, {c['episodes']} episodes on {c['machine']}"
                     f"{' (the machine that ran the seeds)' if c['machine'] == env.get('machine') else ''}: "
                     f"{'IDENTICAL' if c['identical'] else 'DIFFERENT'}" for c in checks) or "none yet") + ".",
          "  Identical on the machine that ran the seeds: the seeds that started over after the out-of-memory failure",
          "  (DECISIONS run log) are the episodes their seeds fix. Identical on another machine: the scores do not",
          "  depend on the machine.",
          "- Every saved output's SHA-256, as git stores it (LF line endings): `out/HASHES.txt`.", "",
          "Every episode: `out/episodes_<team>_seed<k>.json`.", ""]
    dest.write_text("\n".join(L), encoding="utf-8")
    write_hashes(out)
    sys.stdout.reconfigure(errors="replace")                 # Windows consoles may not print the ± sign
    print("\n".join(L[:20]))
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=["check", "verify", "run", "seed", "recheck", "report"])
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--team", choices=list(TEAMS))
    ap.add_argument("--seed", type=int)
    ap.add_argument("--episodes", type=int, default=EPISODES)
    a = ap.parse_args()
    if a.stage == "check":
        stage_check()
    elif a.stage == "verify":
        stage_verify()
    elif a.stage == "run":
        stage_run(a.workers)
    elif a.stage == "recheck":
        stage_recheck(a.team or "Teamcybermonic", 0 if a.seed is None else a.seed, 3 if a.episodes == EPISODES else a.episodes)
    elif a.stage == "seed":
        if a.team is None or a.seed not in SEEDS or a.episodes != EPISODES:
            raise SystemExit("--team, a seed 0-9 and 100 episodes (DECISIONS 10)")
        if seed_file(a.team, a.seed).exists():
            raise SystemExit(f"{a.team} seed {a.seed} already finished")
        run_seed(a.team, a.seed, a.episodes, seed_file(a.team, a.seed))
    else:
        report()


if __name__ == "__main__":
    main()
