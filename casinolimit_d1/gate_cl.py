# -*- coding: utf-8 -*-
"""Protocol CL-D1.0 step 0: the validity gate on CasinoLimit. No learned agent is involved.

The ladder and rules of D1.0's gate (camlds_real_full_arch/gate_d1.py), on the CasinoLimit world
(cl_world.py: D1.0's environment and reference policies, unchanged):
  none          no decoys
  random        uniform random joint action
  fixed         best constant joint action (all 6^4), chosen leaving the scored run out
  greedy        payoff-best decoy for the last command, in the machine where the attacker was last seen
  planner       like greedy, but for the NEXT command predicted from the previous one (empirical
                transitions of all other runs): uses history, no learning
  clairvoyant   sees the next machine and the next command (ceiling; never an arm)
Unit = run (all 114 attackers). Outcome E1 only: CasinoLimit records no attacker goal, so D1.0's
protection outcome P1 and its gate G1 do not exist here.
Randomness: seed 300000, 20 repeats per run, disjoint from validation (100000+s) and test (200000+s).

Pass criteria, both required (D1.0's G2 and G3 on E1; a stop rule, decision C10):
  G2  a real decision problem: clairvoyant - best of {fixed, greedy} > 0, 95% bootstrap CI over runs
      excludes 0
  G3  a simple history rule helps: planner - greedy > 0, 95% CI excludes 0
A failure means "this simple history rule shows no benefit in this setup", not "no history-based method
can help". The fixed and planner policies here are fitted on all other runs (leave-one-run-out), as in
D1.0's gate, so some of those runs are later test runs; the gate is a diagnostic of the environment,
nothing is chosen or tuned after it, and the learned arms' evaluation uses training-run fits only.
Bootstrap: 10,000 resamples of runs, seed 20261103, percentile interval. Also reported, descriptive:
each policy's E1 as a share of the run length.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cl_world as C  # noqa: E402  (first: registers the CasinoLimit environment)

env, B = C.env, C.B
GATE_SEED, REPEATS = 300000, 20
BOOT_N, BOOT_SEED = 10000, 20261103


class TransitionPlanner:
    """Best decoy for the predicted next command, in the zone where the attacker was last seen.
    The text of gate_d1.TransitionPlanner with its environment module passed in (test_cl_d1 checks that,
    run on D1.0's environment, it makes D1.0's planner decisions)."""
    name = "planner"

    def __init__(self, train_runs, cfg, envm=None):
        self.env = envm or env
        self.how = cfg.aggregation
        self.next = defaultdict(Counter)
        for r in train_runs:
            cmds = [tuple(c) for c in r["commands"]]
            for a, b in zip(cmds, cmds[1:]):
                self.next[a][b] += 1
        self.any = Counter(c for r in train_runs for c in map(tuple, r["commands"]))
        self.best = {}

    def _best_for(self, prev):
        if prev not in self.best:
            dist = self.next.get(prev) or self.any
            total = sum(dist.values())
            scores = [sum(n * self.env.command_payoff(c, d, self.how) for c, n in dist.items()) / total
                      for d in range(self.env.N_ACTIONS)]
            d = int(np.argmax(scores))
            self.best[prev] = d if scores[d] > 0 else self.env.NULL
        return self.best[prev]

    def __call__(self, e):
        acts = [self.env.NULL] * self.env.N_AGENTS
        if e.burned or not e.cur_cmd:
            return acts
        ag = self.env.ZONE_AGENT.get(e.zone)
        if ag is not None:
            acts[ag] = self._best_for(tuple(e.cur_cmd))
        return acts


def score(policy, specs, cfg):
    e = env.CommandEngagementEnv(cfg, C.MAX_STEPS)
    rows = [env.run_episode(e, s, policy) for s in specs]
    return {"E1": float(np.mean([r["dwell"] for r in rows])),
            "share": float(np.mean([r["dwell"] / max(r["length"], 1.0) for r in rows]))}


def boot_ci(d):
    d = np.asarray(d, float)
    rng = np.random.default_rng(BOOT_SEED)
    idx = rng.integers(0, len(d), size=(BOOT_N, len(d)))
    m = d[idx].mean(axis=1)
    return float(d.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def run_gate(runs, cfg, repeats=REPEATS, joints=None):
    rng = np.random.default_rng(GATE_SEED)
    meta = C.scenario_metadata()
    specs = {r["id"]: [env.make_spec(r, rng, meta) for _ in range(repeats)] for r in runs}
    ids = [r["id"] for r in runs]
    joints = list(itertools.product(range(env.N_ACTIONS), repeat=env.N_AGENTS)) if joints is None else joints
    table = np.zeros((len(joints), len(ids)))                 # fixed: every joint action on every run, once
    for j, joint in enumerate(joints):
        pol = B.FixedJointPolicy(joint)
        for k, rid in enumerate(ids):
            table[j, k] = score(pol, specs[rid], cfg)["E1"]
    names = ("none", "random", "fixed", "greedy", "planner", "clairvoyant")
    per = {n: {} for n in names}
    chosen = {}
    for k, r in enumerate(runs):
        rid = r["id"]
        others = [i for i in range(len(ids)) if i != k]
        jf = int(np.argmax(table[:, others].mean(axis=1)))
        chosen[rid] = list(joints[jf])
        per["fixed"][rid] = score(B.FixedJointPolicy(joints[jf]), specs[rid], cfg)
        per["none"][rid] = score(B.NullPolicy(), specs[rid], cfg)
        per["random"][rid] = score(B.RandomPolicy(GATE_SEED + k), specs[rid], cfg)
        per["greedy"][rid] = score(B.ReactivePolicy(cfg), specs[rid], cfg)
        per["planner"][rid] = score(TransitionPlanner([x for x in runs if x["id"] != rid], cfg), specs[rid], cfg)
        per["clairvoyant"][rid] = score(B.ClairvoyantCoordPolicy(cfg), specs[rid], cfg)
    vec = lambda n, key="E1": np.array([per[n][rid][key] for rid in ids])
    res = {"n_runs": len(ids), "repeats": repeats, "means": {n: float(vec(n).mean()) for n in names},
           "share_of_length": {n: float(vec(n, "share").mean()) for n in names}, "gates": {}}
    best = "fixed" if vec("fixed").mean() >= vec("greedy").mean() else "greedy"
    mean, lo, hi = boot_ci(vec("clairvoyant") - vec(best))
    res["gates"]["G2"] = {"against": best, "diff": mean, "ci": [lo, hi], "pass": mean > 0 and lo > 0}
    mean, lo, hi = boot_ci(vec("planner") - vec("greedy"))
    res["gates"]["G3"] = {"diff": mean, "ci": [lo, hi], "pass": mean > 0 and lo > 0}
    res["pass"] = res["gates"]["G2"]["pass"] and res["gates"]["G3"]["pass"]
    res["per_run"] = per
    res["fixed_chosen"] = chosen
    return res


def report(res):
    L = ["Protocol CL-D1.0 validity gate (no learned agent; CasinoLimit; E1 only)", "",
         f"runs: {res['n_runs']}; {res['repeats']} repeats per run, seed {GATE_SEED}", "",
         "policy | E1 engaged commands | share of run length"]
    for n, v in res["means"].items():
        L.append(f"{n} | {v:.3f} | {res['share_of_length'][n]:.3f}")
    g2, g3 = res["gates"]["G2"], res["gates"]["G3"]
    L += ["", f"G2 E1: clairvoyant - {g2['against']} = {g2['diff']:.3f} [{g2['ci'][0]:.3f}, {g2['ci'][1]:.3f}] -> "
          f"{'PASS' if g2['pass'] else 'FAIL'}",
          f"G3 E1: planner - greedy = {g3['diff']:.3f} [{g3['ci'][0]:.3f}, {g3['ci'][1]:.3f}] -> "
          f"{'PASS' if g3['pass'] else 'FAIL'}", "", f"GATE: {'PASS' if res['pass'] else 'FAIL'}"]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=HERE / "gate")
    ap.add_argument("--smoke", action="store_true", help="3 runs, 2 repeats, 8 joints: code check only")
    a = ap.parse_args()
    cfg = env.EnvConfig(reward="proposal")
    runs = C.all_runs()
    if a.smoke:
        res = run_gate(runs[:2] + runs[-1:], cfg, repeats=2,
                       joints=list(itertools.product((0, 1), repeat=env.N_AGENTS))[:8])
        report(res)   # built but NOT printed: no gate number is seen before the protocol is frozen
        print("smoke OK:", sorted(res["means"]), "gates", sorted(res["gates"]), "runs", res["n_runs"])
        return
    import spec_cl_d1
    spec_cl_d1.require()        # the gate runs only after the protocol is frozen
    if (a.output / "GATE_RESULT.json").exists():
        raise SystemExit("the gate has already been run under CL-D1.0; it is not rerun")
    res = run_gate(runs, cfg)
    a.output.mkdir(parents=True, exist_ok=True)
    (a.output / "GATE_RESULT.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    (a.output / "GATE_RESULT.txt").write_text(report(res), encoding="utf-8")
    print(report(res))
    raise SystemExit(0 if res["pass"] else 1)          # a failed gate stops any chained command


if __name__ == "__main__":
    main()
