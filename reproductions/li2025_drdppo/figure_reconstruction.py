# -*- coding: utf-8 -*-
"""Li 2025 DRD-PPO: A13, the figure-derived reconstruction (DECISIONS.md, A13). Runs once.

    python reproductions/li2025_drdppo/figure_reconstruction.py smoke   # tiny code check, temporary folder
    python reproductions/li2025_drdppo/figure_reconstruction.py run     # ONCE: readings R-A and R-B, 10 seeds

The settings are derived from the measured plateaus of the paper's Figs. 5-6 (data/figure_values.json); the
tests are Table 3, Table 4 and Fig. 6b's Alg1 value, which no derivation used. A sanity check compares the
simulated random baselines with the arithmetic predictions pre-registered in A13 (a large gap = a code error).
"""
from __future__ import annotations

import argparse
import csv
import dataclasses
import json
import os
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import calibrate as C  # noqa: E402
import drdppo as D  # noqa: E402

OUT = HERE / "out"
RA = D.Setting(w=0.5, links="P2", timing="last", cvss="v2", h_links="f_only", R1=1.0, R2=0.0, clip=0.2,
               attacker="clone_specific", ties="random", alg1="fig", action="single", cost="final", f_score="none",
               full_f=9)                                                  # D1-D7
READINGS = {"R-A": RA, "R-B": dataclasses.replace(RA, attacker="argmax")}
PREDICTED = {"R-A": {"alg1": 36.17, "alg3": 66.41}, "R-B": {"alg1": 60.83, "alg3": 100.00}}   # A13, before any run
# policy -> (episodes, evaluation episodes)
POLICIES = {"alg1": (500, 0), "alg3": (500, 0), "scripted": (500, 0), "drdppo": (500, 500), "drdppo_init": (500, 0),
            "alg2": (500, 500), "alg2_init": (500, 0), "drdppo_1500": (1500, 1500)}
TESTS = [("T3.Alg1_random_deployment", "alg1", "dsp", 28.43), ("T3.Alg3_random_full_deployment", "alg3", "dsp", 55.19),
         ("T3.DRD-PPO", "drdppo", "dsp", 97.09), ("T3.Alg2_intelligent_full_deployment", "alg2", "dsp", 98.31),
         ("T4.DRD-PPO", "drdppo_1500", "dsp", 98.61), ("Fig.6b Alg1 attack probability", "alg1", "attack_probability", 0.621)]
REFS = {"drdppo": ("scripted", "drdppo_init"), "alg2": ("scripted", "alg2_init"), "drdppo_1500": ("scripted", "drdppo_init")}
LOG_FIELDS = ["reading", "policy", "seed", "episodes", "dsp", "dsp_eval", "dsp_last100", "cost_last100",
              "reward_last100", "attack_probability", "first_episode_cost_below_1", "seconds"]


def _job(args):
    reading, s_dict, policy, seed, episodes, eval_eps = args
    s = D.Setting(**s_dict)
    t0 = time.time()
    if policy in ("alg1", "alg3", "scripted"):
        det = D.run_policy(s, 10_000 * ("alg1", "alg3", "scripted").index(policy) + seed, episodes, policy, details=True)
        ev = []
    else:
        variant = "alg2" if policy.startswith("alg2") else "drd"
        r = D.train_ppo(s, seed, episodes, variant=variant, learn=not policy.endswith("_init"), eval_episodes=eval_eps)
        det, ev = r["train_details"], r["eval"]
    succ = np.array([d["success"] for d in det], float)
    cost = np.array([d["cost"] for d in det])
    ma = np.convolve(cost, np.ones(20) / 20, mode="valid") if len(cost) >= 20 else cost
    below = np.flatnonzero(ma < 1.0)
    return {"reading": reading, "policy": policy, "seed": seed, "episodes": episodes,
            "dsp": 100 * succ.mean(), "dsp_eval": 100 * float(np.mean(ev)) if ev else "",
            "dsp_last100": 100 * succ[-100:].mean(), "cost_last100": float(cost[-100:].mean()),
            "reward_last100": float(np.mean([d["reward"] for d in det[-100:]])),
            "attack_probability": float(np.mean([d["attack_probability"] for d in det[-100:]])),
            "first_episode_cost_below_1": int(below[0]) + 20 if len(below) else "",
            "seconds": round(time.time() - t0, 2)}


def run(out: Path, workers: int, seeds=C.SEEDS, policies=POLICIES) -> dict:
    jobs = [(name, dataclasses.asdict(s), p, sd, eps, ev) for name, s in READINGS.items()
            for p, (eps, ev) in policies.items() for sd in seeds]
    print(f"A13: {len(READINGS)} readings x {len(policies)} policies x {len(seeds)} seeds = {len(jobs)} trials, "
          f"{workers} workers", flush=True)
    rows = []
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for i, row in enumerate(ex.map(_job, jobs), 1):
            rows.append(row)
            if i % 20 == 0 or i == len(jobs):
                print(f"  {i}/{len(jobs)}", flush=True)
    out.mkdir(parents=True, exist_ok=True)
    with (out / "figure_reconstruction_log.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=LOG_FIELDS)
        w.writeheader()
        w.writerows(rows)
    fig = json.loads((HERE / "data" / "figure_values.json").read_text(encoding="utf-8"))
    res = {"readings": {k: dataclasses.asdict(v) for k, v in READINGS.items()}, "predicted": PREDICTED,
           "figure_values": {k: {c: v["median"] for c, v in fig[k]["curves"].items()} for k in fig if k.startswith("fig")},
           "results": {}, "seeds": list(seeds), "git_head": C.git_head()}
    for name in READINGS:
        summ = {}
        for p in policies:
            rs = [r for r in rows if r["reading"] == name and r["policy"] == p]
            summ[p] = {m: C.summary([float(r[m]) for r in rs]) for m in
                       ("dsp", "dsp_last100", "cost_last100", "reward_last100", "attack_probability")}
            if rs and rs[0]["dsp_eval"] != "":
                summ[p]["dsp_eval"] = C.summary([float(r["dsp_eval"]) for r in rs])
            fb = [float(r["first_episode_cost_below_1"]) for r in rs if r["first_episode_cost_below_1"] != ""]
            summ[p]["first_episode_cost_below_1"] = {"seeds_reaching": len(fb), "median": float(np.median(fb)) if fb else None}
        tests = []
        for tid, p, metric, pub in TESTS:
            s = summ[p][metric]
            tol = 0.02 if metric == "attack_probability" else 2.0
            refs = {r: summ[r]["dsp"]["mean"] for r in REFS.get(p, ())}
            uninformative = any(abs(v - pub) <= tol for v in refs.values())
            tests.append({"id": tid, "policy": p, "published": pub, "ours": s, "consistent": abs(s["mean"] - pub) <= tol,
                          "references": refs, "uninformative_A2": uninformative})
        sanity = {k: {"predicted": v, "simulated": summ[k]["dsp"]["mean"], "gap": summ[k]["dsp"]["mean"] - v}
                  for k, v in PREDICTED[name].items()}
        res["results"][name] = {"summary": summ, "tests": tests, "sanity_vs_prediction": sanity}
    return res


def write_md(res: dict, dest: Path):
    L = ["# Li 2025 DRD-PPO: figure-derived reconstruction (A13)", "",
         "Settings derived from the measured plateaus of the paper's Figs. 5-6 (DECISIONS.md A13, D1-D7), declared with",
         "exact predictions before the run, run once (10 seeds). Tests = numbers no derivation used. REPORT.md's",
         "verdicts (the calibrated replication) do not change.", ""]
    for name, r in res["results"].items():
        L += [f"## Reading {name}" + (" (primary: clone-specific attacker)" if name == "R-A" else " (secondary: all honeypots compete)"), "",
              "| test | published | ours: mean [95% CI] | consistent (within 2 points / 0.02) | references (A2) |",
              "|---|---|---|---|---|"]
        for t in r["tests"]:
            s = t["ours"]
            refs = ", ".join(f"{k} {v:.2f}" for k, v in t["references"].items()) or "-"
            flag = "UNINFORMATIVE (A2)" if t["uninformative_A2"] else ("yes" if t["consistent"] else "no")
            L.append(f"| {t['id']} | {t['published']} | {s['mean']:.3f} [{max(s['ci'][0], 0):.3f}, {s['ci'][1]:.3f}] | {flag} | {refs} |")
        L += ["", "Sanity check against the arithmetic predictions (a large gap would be a code error): " +
              "; ".join(f"{k} predicted {v['predicted']:.2f}, simulated {v['simulated']:.2f}" for k, v in r["sanity_vs_prediction"].items()), "",
              "Plateaus over the last 100 episodes (descriptive; the DRD-PPO and Alg2 plateaus were used in the derivations):", ""]
        for p in ("drdppo", "alg2", "alg1", "alg3"):
            s = r["summary"][p]
            L.append(f"- {p}: reward {s['reward_last100']['mean']:+.3f}, cost {s['cost_last100']['mean']:.3f}, "
                     f"attack probability {s['attack_probability']['mean']:.3f}")
        fb = r["summary"]["drdppo"]["first_episode_cost_below_1"]
        L += [f"- DRD-PPO's cost (20-episode average) first below 1.0: median episode {fb['median']} "
              f"({fb['seeds_reaching']} of {len(res['seeds'])} seeds); paper's Fig. 6c: about episode 150-200.", ""]
    L += ["Every trial: `out/figure_reconstruction_log.csv`; all numbers: `out/figure_reconstruction.json`.", ""]
    dest.write_text("\n".join(L), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=["smoke", "run"])
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    a = ap.parse_args()
    t0 = time.time()
    if a.stage == "smoke":
        small = {p: (25, 5 if ev else 0) for p, (eps, ev) in POLICIES.items()}
        with tempfile.TemporaryDirectory() as tmp:
            res = run(Path(tmp), a.workers, seeds=(0, 1), policies=small)
            write_md(res, Path(tmp) / "FIGURE_RECONSTRUCTION.md")
        print(f"smoke OK in {time.time() - t0:.0f} s; nothing kept")
        return
    if (OUT / "figure_reconstruction.json").exists():
        raise SystemExit("A13 has already run; it runs once")
    for f in (HERE / "DECISIONS.md", HERE / "data" / "figure_values.json"):
        if not C.committed_unchanged(f):
            raise SystemExit(f"{f.name} must be committed and unchanged before the run (A13 is declared first)")
    res = run(OUT, a.workers)
    C.D_write(OUT / "figure_reconstruction.json", res)
    write_md(res, HERE / "FIGURE_RECONSTRUCTION.md")
    print(f"A13 finished in {(time.time() - t0) / 60:.1f} min")
    for name, r in res["results"].items():
        print(f"{name}: " + "; ".join(f"{t['id']} {t['ours']['mean']:.2f} vs {t['published']} "
                                      f"{'UNINF' if t['uninformative_A2'] else ('ok' if t['consistent'] else 'no')}" for t in r["tests"]))


if __name__ == "__main__":
    main()
