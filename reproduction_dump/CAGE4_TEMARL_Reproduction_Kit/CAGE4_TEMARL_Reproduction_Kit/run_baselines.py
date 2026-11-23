#!/usr/bin/env python3
"""Run upstream CAGE-4 evaluation without changing PUNCH or Cybermonic code.
Logs original per-run rewards, stderr/stdout, and deterministic source IDs.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
AGENT_PATHS = {
    "punch": ROOT / "external" / "punch" / "punch_analyse_restore_v1",
    "cybermonic": ROOT / "external" / "cybermonic",
}
PUBLISHED = {"punch": (-142.0, 44.0), "cybermonic": (-193.0, 84.0)}


def make_command(agent, episodes, seed, outdir):
    return [sys.executable, "-m", "CybORG.Evaluation.evaluation", "--max-eps", str(episodes), "--seed", str(seed), str(AGENT_PATHS[agent]), str(outdir)]


def safe_name(name):
    if name not in AGENT_PATHS:
        raise ValueError(f"Unknown baseline: {name}")
    return name


def run_one(agent, episodes, seed, *, dry_run=False):
    safe_name(agent)
    output = ROOT / "results" / agent / f"episodes_{episodes}_seed_{seed}"
    cmd = make_command(agent, episodes, seed, output)
    env = os.environ.copy()
    cage_root = str(ROOT / "external" / "cage")
    env["PYTHONPATH"] = os.pathsep.join(filter(None, [cage_root, str(AGENT_PATHS[agent]), env.get("PYTHONPATH", "")]))
    print("COMMAND:", " ".join(cmd), flush=True)
    if dry_run:
        return
    if not (AGENT_PATHS[agent] / "submission.py").exists():
        raise SystemExit(f"Missing {agent} source. Run `python bootstrap.py` first.")
    if output.exists() and (output / "summary.json").exists():
        raise SystemExit(f"Results already exist: {output}. Do not silently overwrite. Choose another seed.")
    output.mkdir(parents=True, exist_ok=True)
    invocation = {
        "agent": agent,
        "episodes": episodes,
        "steps_per_episode": 500,
        "seed": seed,
        "command": cmd,
        "status": "started",
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    (output / "invocation.json").write_text(json.dumps(invocation, indent=2), encoding="utf-8")
    with (output / "runner.log").open("w", encoding="utf-8") as log:
        proc = subprocess.Popen(cmd, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace", bufsize=1)
        for line in proc.stdout:
            sys.stdout.write(line)
            log.write(line)
        rc = proc.wait()
    invocation["returncode"] = rc
    invocation["status"] = "completed" if rc == 0 and (output / "summary.json").exists() else "failed"
    invocation["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    (output / "invocation.json").write_text(json.dumps(invocation, indent=2), encoding="utf-8")
    if invocation["status"] == "failed":
        raise SystemExit(f"Evaluation failed (code {rc}). See {output / 'runner.log'}")
    j = json.loads((output / "summary.json").read_text())
    mean = j.get("reward", {}).get("mean")
    sd = j.get("reward", {}).get("stdev")
    print(f"SUCCESS {agent}: reward {mean} ± {sd} | published reference {PUBLISHED[agent][0]} ± {PUBLISHED[agent][1]}")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--agents", nargs="+", choices=[*AGENT_PATHS, "all"], default=["all"])
    p.add_argument("--episodes", type=int, default=2, help="2 for smoke test; 100 for published evaluation")
    p.add_argument("--seed", type=int, default=12501)
    p.add_argument("--dry-run", action="store_true", help="Print commands without requiring dependencies")
    a = p.parse_args()
    if a.episodes < 2 or a.episodes > 10000:
        p.error("episodes must be >=2 (upstream uses stdev) and <=10000")
    agents = list(AGENT_PATHS) if "all" in a.agents else a.agents
    for agent in agents:
        run_one(agent, a.episodes, a.seed, dry_run=a.dry_run)

if __name__ == "__main__":
    main()
