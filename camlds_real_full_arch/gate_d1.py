# -*- coding: utf-8 -*-
"""Protocol D1.0 step 0: the validity gate. No learned agent is involved.

Reference ladder (PROTOCOL_D1.0.md Section 5), every policy obeying the same environment rules:
  none          no decoys
  random        uniform random joint action
  fixed         best constant joint action (all 6^4), chosen per metric leaving the scored run out
  greedy        payoff-best decoy for the last command, in the zone where the attacker was last seen
  planner       like greedy, but for the NEXT command predicted from the previous one
                (empirical transitions of all other runs): uses history, no learning
  clairvoyant   sees the next zone and the next command (ceiling; never an arm)
Unit = run. E1 (engaged commands) on all 34 runs; P1 (defense success) on the runs with p1 = True.
Randomness: seed 300000, 20 repeats per run, disjoint from validation (100000+s) and test (200000+s).

Pass criteria, all required:
  G1  under none, the goal is reached in >= 50% of P1 episodes
  G2  for E1 and for P1: clairvoyant - best of {fixed, greedy} > 0, 95% bootstrap CI over runs excludes 0
  G3  planner - greedy > 0 on E1 or on P1, 95% CI excludes 0
Bootstrap: 10,000 resamples of runs, seed 20261103, percentile interval.
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
import pipeline as P  # noqa: E402  (frozen paths, D1.0 runs)
import baselines_cmd as B  # noqa: E402  (frozen reference policies, Temarl_Test_v1_L1)

env = P.env
assert B.CommandEngagementEnv is env.CommandEngagementEnv, "baselines must use the D1.0 environment"

GATE_SEED, REPEATS = 300000, 20
BOOT_N, BOOT_SEED = 10000, 20261103
METRICS = ("E1", "P1")


class TransitionPlanner:
    """Best decoy for the predicted next command, in the zone where the attacker was last seen."""
    name = "planner"

    def __init__(self, train_runs, cfg):
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
            scores = [sum(n * env.command_payoff(c, d, self.how) for c, n in dist.items()) / total
                      for d in range(env.N_ACTIONS)]
            d = int(np.argmax(scores))
            self.best[prev] = d if scores[d] > 0 else env.NULL
        return self.best[prev]

    def __call__(self, e):
        acts = [env.NULL] * env.N_AGENTS
        if e.burned or not e.cur_cmd:
            return acts
        ag = env.ZONE_AGENT.get(e.zone)
        if ag is not None:
            acts[ag] = self._best_for(tuple(e.cur_cmd))
        return acts


def all_runs():
    out = {}
    for f in P.ordered_folds("frozen"):
        for split in ("train", "val", "test"):
            for r in P.runs(f, split):
                out[r["id"]] = r
    return [out[k] for k in sorted(out)]


def score(policy, specs, cfg):
    e = env.CommandEngagementEnv(cfg)
    rows = [env.run_episode(e, s, policy) for s in specs]
    return {"E1": float(np.mean([r["dwell"] for r in rows])),
            "P1": float(np.mean([r["protected"] for r in rows])),
            "goal_reached": float(np.mean([1.0 - r["protected"] for r in rows])),
            "undefended": float(np.mean([r["undefended_commands"] for r in rows]))}


def boot_ci(d):
    d = np.asarray(d, float)
    rng = np.random.default_rng(BOOT_SEED)
    idx = rng.integers(0, len(d), size=(BOOT_N, len(d)))
    m = d[idx].mean(axis=1)
    return float(d.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def run_gate(runs, cfg, repeats=REPEATS, joints=None):
    specs = {}
    rng = np.random.default_rng(GATE_SEED)
    meta = env.scenario_metadata()
    for r in runs:
        specs[r["id"]] = [env.make_spec(r, rng, meta) for _ in range(repeats)]
    ids = [r["id"] for r in runs]
    p1 = {r["id"]: bool(meta[r["scenario"]]["p1"]) for r in runs}
    joints = list(itertools.product(range(env.N_ACTIONS), repeat=env.N_AGENTS)) if joints is None else joints

    # fixed: score every constant joint action on every run once, then choose leaving the run out
    table = {m: np.zeros((len(joints), len(ids))) for m in METRICS}
    for j, joint in enumerate(joints):
        pol = B.FixedJointPolicy(joint)
        for k, rid in enumerate(ids):
            s = score(pol, specs[rid], cfg)
            for m in METRICS:
                table[m][j, k] = s[m]
    per = {name: {} for name in ("none", "random", "greedy", "planner", "clairvoyant", "fixed_E1", "fixed_P1")}
    chosen = {}
    for k, r in enumerate(runs):
        rid = r["id"]
        others = [i for i in range(len(ids)) if i != k]
        p1_others = [i for i in others if p1[ids[i]]]
        jE = int(np.argmax(table["E1"][:, others].mean(axis=1)))
        jP = int(np.argmax(table["P1"][:, p1_others].mean(axis=1)))
        chosen[rid] = {"fixed_E1": list(joints[jE]), "fixed_P1": list(joints[jP])}
        per["fixed_E1"][rid] = {m: float(table[m][jE, k]) for m in METRICS}
        per["fixed_P1"][rid] = {m: float(table[m][jP, k]) for m in METRICS}
        per["none"][rid] = score(B.NullPolicy(), specs[rid], cfg)
        per["random"][rid] = score(B.RandomPolicy(GATE_SEED + k), specs[rid], cfg)
        per["greedy"][rid] = score(B.ReactivePolicy(cfg), specs[rid], cfg)
        per["planner"][rid] = score(TransitionPlanner([x for x in runs if x["id"] != rid], cfg), specs[rid], cfg)
        per["clairvoyant"][rid] = score(B.ClairvoyantCoordPolicy(cfg), specs[rid], cfg)

    def units(metric):
        return [rid for rid in ids if metric == "E1" or p1[rid]]

    def vec(name, metric):
        return np.array([per[name][rid][metric] for rid in units(metric)])

    res = {"n_runs": {m: len(units(m)) for m in METRICS}, "repeats": repeats,
           "means": {n: {m: float(vec(n, m).mean()) for m in METRICS} for n in per}, "gates": {}}
    g1 = float(np.mean([per["none"][rid]["goal_reached"] for rid in units("P1")]))
    res["gates"]["G1"] = {"goal_reached_under_none": g1, "pass": g1 >= 0.5}
    g2 = {}
    for m in METRICS:
        fixed = "fixed_E1" if m == "E1" else "fixed_P1"
        best = fixed if vec(fixed, m).mean() >= vec("greedy", m).mean() else "greedy"
        mean, lo, hi = boot_ci(vec("clairvoyant", m) - vec(best, m))
        g2[m] = {"against": best, "diff": mean, "ci": [lo, hi], "pass": mean > 0 and lo > 0}
    res["gates"]["G2"] = {**g2, "pass": all(g2[m]["pass"] for m in METRICS)}
    g3 = {}
    for m in METRICS:
        mean, lo, hi = boot_ci(vec("planner", m) - vec("greedy", m))
        g3[m] = {"diff": mean, "ci": [lo, hi], "pass": mean > 0 and lo > 0}
    res["gates"]["G3"] = {**g3, "pass": any(g3[m]["pass"] for m in METRICS)}
    res["pass"] = all(res["gates"][g]["pass"] for g in ("G1", "G2", "G3"))
    res["per_run"] = per
    res["fixed_chosen"] = chosen
    by_s = defaultdict(list)
    for r in runs:
        by_s[r["scenario"]].append(r["id"])
    res["per_scenario"] = {s: {n: {m: float(np.mean([per[n][rid][m] for rid in rs])) for m in METRICS}
                               for n in per} for s, rs in sorted(by_s.items())}
    return res


def report(res):
    L = ["Protocol D1.0 validity gate (no learned agent)", "",
         f"runs: E1 {res['n_runs']['E1']}, P1 {res['n_runs']['P1']}; {res['repeats']} repeats per run, seed {GATE_SEED}", "",
         "policy | E1 engaged commands | P1 defense success"]
    for n, v in res["means"].items():
        L.append(f"{n} | {v['E1']:.3f} | {v['P1']:.3f}")
    g = res["gates"]
    L += ["", f"G1 goal reached under none: {g['G1']['goal_reached_under_none']:.3f} -> {'PASS' if g['G1']['pass'] else 'FAIL'}"]
    for m in METRICS:
        x = g["G2"][m]
        L.append(f"G2 {m}: clairvoyant - {x['against']} = {x['diff']:.3f} [{x['ci'][0]:.3f}, {x['ci'][1]:.3f}] -> {'pass' if x['pass'] else 'fail'}")
    L.append(f"G2 -> {'PASS' if g['G2']['pass'] else 'FAIL'}")
    for m in METRICS:
        x = g["G3"][m]
        L.append(f"G3 {m}: planner - greedy = {x['diff']:.3f} [{x['ci'][0]:.3f}, {x['ci'][1]:.3f}] -> {'pass' if x['pass'] else 'fail'}")
    L.append(f"G3 -> {'PASS' if g['G3']['pass'] else 'FAIL'}")
    L += ["", f"GATE: {'PASS' if res['pass'] else 'FAIL'}", "", "per scenario (E1 / P1):"]
    for s, v in res["per_scenario"].items():
        L.append(s + " | " + " | ".join(f"{n} {v[n]['E1']:.2f}/{v[n]['P1']:.2f}" for n in v))
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=HERE / "gate")
    ap.add_argument("--smoke", action="store_true", help="3 runs, 2 repeats, 8 joints: code check only")
    a = ap.parse_args()
    cfg = env.EnvConfig()
    runs = all_runs()
    if a.smoke:
        res = run_gate(runs[:2] + runs[-1:], cfg, repeats=2,
                       joints=list(itertools.product((0, 1), repeat=env.N_AGENTS))[:8])
        report(res)   # built but NOT printed: no gate number is seen before the protocol is frozen
        print("smoke OK:", sorted(res["means"]), "gates", sorted(res["gates"]), "runs", res["n_runs"])
        return
    import spec_d1
    spec_d1.require()           # the gate runs only after the protocol is frozen
    if (a.output / "GATE_RESULT.json").exists():
        raise SystemExit("the gate has already been run under D1.0; it is not rerun")
    res = run_gate(runs, cfg)
    a.output.mkdir(parents=True, exist_ok=True)
    (a.output / "GATE_RESULT.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    (a.output / "GATE_RESULT.txt").write_text(report(res), encoding="utf-8")
    print(report(res))
    raise SystemExit(0 if res["pass"] else 1)          # a failed gate stops any chained command


if __name__ == "__main__":
    main()
