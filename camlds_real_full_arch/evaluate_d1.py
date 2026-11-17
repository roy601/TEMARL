# -*- coding: utf-8 -*-
"""Protocol D1.0 evaluation (Section 9). Frozen with the protocol.

    python camlds_real_full_arch/evaluate_d1.py --validation-dry-run --device cuda
    python camlds_real_full_arch/evaluate_d1.py --open-test --device cuda       # ONCE

1. Dry run: every primary cell's saved actor is re-evaluated on its validation episodes and must
   reproduce the best validation E1 recorded at training. No test file is read.
2. Open the test once: refuses unless the spec passes, all 640 primary cells exist, the dry run passed
   and the test was never opened. Every sealed file's SHA-256 is checked before it is read.

Unit = test run of the 29 variant-held-out folds (the 3 scenario-held-out folds are descriptive). Per
unit: the outcome averaged over 20 repeats, then over 10 seeds. E1 = engaged commands; P1 = defense
success on runs with p1 (S4 excluded).
Family 1: allpos vs NoHistory on E1 and P1. Family 2: allpos vs none, random, fixed, greedy, planner
on E1 and P1 (the reference policies are run here on the same test episodes; fixed and planner are
fitted on the fold's training runs only). Per comparison: mean paired difference, 95% bootstrap CI
(10,000 resamples of runs, seed 20261103), two-sided Wilcoxon signed-rank (zero differences dropped),
Holm within the family. "X outperforms Y" only if Holm p < 0.05 and the CI excludes 0.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import scipy.stats as sps

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

ALPHA, BOOT_N, BOOT_SEED = 0.05, 10_000, 20261103
ARMS = ("allpos", "NoHistory")
REFERENCES = ("none", "random", "fixed", "greedy", "planner")
NAMES = {"allpos": "history agents (allpos)", "NoHistory": "agents without history",
         "none": "no decoys", "random": "random", "fixed": "best fixed allocation",
         "greedy": "greedy (reactive)", "planner": "transition planner", "clairvoyant": "clairvoyant"}
FIT_SEED, FIT_REPEATS = 400000, 5
OUTCOMES = ("E1", "P1")


# ── statistics (identical rules to casinolimit_encoder/evaluate.py; unit = run) ──

def bootstrap_ci(d):
    d = np.asarray(d, np.float64)
    rng = np.random.default_rng(BOOT_SEED)
    means = d[rng.integers(0, len(d), (BOOT_N, len(d)))].mean(axis=1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def wilcoxon_p(d):
    d = np.asarray(d, np.float64)
    if np.count_nonzero(d) < 2:
        return None
    return float(sps.wilcoxon(d, zero_method="wilcox", correction=False, alternative="two-sided",
                              method="auto").pvalue)


def holm(ps):
    order, adj, running = np.argsort(ps), [0.0] * len(ps), 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(ps) - rank) * ps[i]))
        adj[i] = running
    return adj


def contrast(a: dict, b: dict) -> dict:
    keys = sorted(set(a) & set(b))
    d = np.array([a[k] - b[k] for k in keys])
    lo, hi = bootstrap_ci(d)
    return {"mean": float(d.mean()), "ci": [lo, hi], "p": wilcoxon_p(d), "n_runs": len(keys),
            "runs_a_better": int((d > 0).sum()), "runs_b_better": int((d < 0).sum())}


def verdict(c) -> str:
    excludes_zero = c["ci"][0] > 0 or c["ci"][1] < 0
    if not (excludes_zero and c["p_holm"] < ALPHA):
        return "no difference shown"
    win, lose = (c["a"], c["b"]) if c["mean"] > 0 else (c["b"], c["a"])
    return f"{NAMES[win]} outperforms {NAMES[lose]}"


def family(values: dict, pairs) -> list:
    """values[(name, outcome)] = {run: value}; pairs = [(a, b, outcome)]. Holm over the whole family."""
    out = [{"a": a, "b": b, "outcome": m, **contrast(values[(a, m)], values[(b, m)])} for a, b, m in pairs]
    ps = [c["p"] if c["p"] is not None else 1.0 for c in out]
    for c, ph in zip(out, holm(ps)):
        c["p_holm"] = ph
        c["verdict"] = verdict(c)
    return out


def per_run(rows_by_seed) -> dict:
    """rows_by_seed: {seed: [episode rows]} -> {outcome: {run: mean over repeats, then over seeds}}."""
    acc = {m: defaultdict(list) for m in OUTCOMES}
    for seed, rows in rows_by_seed.items():
        by_run = defaultdict(list)
        for r in rows:
            by_run[r["run"]].append(r)
        for run, rs in by_run.items():
            acc["E1"][run].append(float(np.mean([x["dwell"] for x in rs])))
            if all(x["p1"] for x in rs):
                acc["P1"][run].append(float(np.mean([x["protected"] for x in rs])))
    return {m: {run: float(np.mean(v)) for run, v in acc[m].items()} for m in OUTCOMES}


# ── file handling ─────────────────────────────────────────────────────────────

def cells(out: Path, folds, seeds, learner="MAPPO"):
    return {(arm, f["fold"], s): out / "cells" / arm / f["fold"] / f"s{s}" / learner
            for arm in ARMS for f in folds for s in seeds}


def read_sealed(dest: Path):
    res = json.loads((dest / "result.json").read_text(encoding="utf-8"))
    blob = (dest / "sealed_test.json").read_bytes()
    if hashlib.sha256(blob).hexdigest() != res["sealed_test_sha256"]:
        raise RuntimeError(f"{dest}: sealed test file does not match its recorded SHA-256")
    return res, json.loads(blob)


# ── reference policies on the test episodes ──────────────────────────────────

def reference_rows(fold, seed, repeats, env, P, G, fixed_joint):
    B = G.B
    cfg = env.EnvConfig()
    train = P.runs(fold, "train")
    specs = P.specs(P.runs(fold, "test"), 200000 + seed, repeats)
    pols = {"none": B.NullPolicy(), "random": B.RandomPolicy(200000 + seed),
            "greedy": B.ReactivePolicy(cfg), "planner": G.TransitionPlanner(train, cfg),
            "clairvoyant": B.ClairvoyantCoordPolicy(cfg)}
    out = {}
    e = env.CommandEngagementEnv(cfg)
    for name, pol in pols.items():
        out[name] = [env.run_episode(e, s, pol) for s in specs]
    for m in OUTCOMES:
        out[f"fixed_{m}"] = [env.run_episode(e, s, B.FixedJointPolicy(fixed_joint[m])) for s in specs]
    return out


def fit_fixed(fold, env, P, G):
    """Best constant joint action per outcome on the fold's TRAINING runs only."""
    B = G.B
    cfg = env.EnvConfig()
    train = P.runs(fold, "train")
    specs = P.specs(train, FIT_SEED, FIT_REPEATS)
    best = {}
    for m in OUTCOMES:
        use = specs if m == "E1" else [s for s in specs if s.p1]
        top = None
        for joint in itertools.product(range(env.N_ACTIONS), repeat=env.N_AGENTS):
            s = G.score(B.FixedJointPolicy(joint), use, cfg)[m]
            if top is None or s > top[0]:
                top = (s, list(joint))
        best[m] = top[1]
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=HERE / "results_d1" / "main")
    ap.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    ap.add_argument("--encoder-root", default=None)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--validation-dry-run", action="store_true")
    g.add_argument("--open-test", action="store_true")
    a = ap.parse_args()

    import spec_d1
    spec_d1.require()
    import pipeline as P
    import run_d1 as R
    import gate_d1 as G
    import torch
    env, marl = P.env, P.marl
    out = a.output
    folds = P.ordered_folds("frozen")
    seeds = list(range(10))
    cs = cells(out, folds, seeds)
    missing = [k for k, d in cs.items() if not (d / "result.json").exists()]
    if missing:
        raise SystemExit(f"{len(missing)} primary cells missing, e.g. {missing[:3]}")
    dry = out / "DRY_RUN_VALIDATION.json"
    opened = out / "TEST_OPENED.json"

    if a.validation_dry_run:
        root = Path(a.encoder_root or (P.REPO / "camlds_encoder" / "out"))
        bad = []
        for (arm, fold_id, seed), d in cs.items():
            res = json.loads((d / "result.json").read_text(encoding="utf-8"))
            f = next(x for x in folds if x["fold"] == fold_id)
            model, _ = R.load_encoder(arm, f, seed, root, a.device)
            actor = marl.Actor().to(a.device)
            actor.load_state_dict(torch.load(d / "actor.pt", map_location=a.device))
            va = P.specs(P.runs(f, "val"), R.VAL_SEED + seed, res["eval_repeats"])
            bank = marl.HistoryBank(model, P.data.W, a.device, h_zero=(model is None))
            rows = marl.evaluate_team(actor, env.EnvConfig(), va, bank, 64, a.device)
            got = marl.mean_of(rows)
            if abs(got - res["best_validation_dwell"]) > 1e-9:
                bad.append({"cell": [arm, fold_id, seed], "recorded": res["best_validation_dwell"], "got": got})
        P.write(dry, {"pass": not bad, "cells": len(cs), "mismatches": bad})
        print(f"dry run: {'PASS' if not bad else 'FAIL'} ({len(cs)} cells, {len(bad)} mismatches)")
        return

    # ── open the test, once ──
    if opened.exists():
        raise SystemExit("the D1.0 test was already opened; it is never opened again")
    if not dry.exists() or not json.loads(dry.read_text(encoding="utf-8"))["pass"]:
        raise SystemExit("the validation dry run has not passed")
    sealed = {}
    for key, d in cs.items():
        res, s = read_sealed(d)
        sealed[key] = s["test"]
    primary_folds = [f for f in folds if f["family"] == "variant_held_out"]

    values, descriptive = {}, {}
    for arm in ARMS:
        for group, fs in (("primary", primary_folds), ("unseen", [f for f in folds if f not in primary_folds])):
            merged = {m: {} for m in OUTCOMES}
            for f in fs:
                pr = per_run({s: sealed[(arm, f["fold"], s)] for s in seeds})
                for m in OUTCOMES:
                    merged[m].update(pr[m])
            for m in OUTCOMES:
                (values if group == "primary" else descriptive)[(arm, m)] = merged[m]
    # reference policies on the same test episodes
    ref_vals = {(n, m): {} for n in (*REFERENCES, "clairvoyant") for m in OUTCOMES}
    fixed_chosen = {}
    for f in primary_folds:
        fixed_chosen[f["fold"]] = fit_fixed(f, env, P, G)
        rows = {n: {} for n in (*REFERENCES, "clairvoyant")}
        for s in seeds:
            rr = reference_rows(f, s, 20, env, P, G, fixed_chosen[f["fold"]])
            for n in ("none", "random", "greedy", "planner", "clairvoyant"):
                rows[n][s] = rr[n]
            rows["fixed"][s] = {m: rr[f"fixed_{m}"] for m in OUTCOMES}
        for n in ("none", "random", "greedy", "planner", "clairvoyant"):
            pr = per_run(rows[n])
            for m in OUTCOMES:
                ref_vals[(n, m)].update(pr[m])
        for m in OUTCOMES:
            pr = per_run({s: rows["fixed"][s][m] for s in seeds})
            ref_vals[("fixed", m)].update(pr[m])
    values.update(ref_vals)

    f1 = family(values, [("allpos", "NoHistory", m) for m in OUTCOMES])
    f2 = family(values, [("allpos", r, m) for r in REFERENCES for m in OUTCOMES])
    means = {f"{n}|{m}": float(np.mean(list(v.values()))) for (n, m), v in values.items()}
    res = {"family_1": f1, "family_2": f2, "means_primary": means,
           "unseen_scenarios_descriptive": {f"{n}|{m}": v for (n, m), v in descriptive.items()},
           "fixed_chosen_on_training": fixed_chosen,
           "n_units": {m: len(values[("allpos", m)]) for m in OUTCOMES}}
    dest = HERE / "out_test_d1"
    dest.mkdir(exist_ok=True)
    (dest / "D1_RESULTS.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    L = ["Protocol D1.0 results (test opened once; simulation only)", "",
         f"units: E1 {res['n_units']['E1']} test runs, P1 {res['n_units']['P1']} (S4 excluded)", ""]
    for name, fam in (("Family 1 (history vs no history)", f1), ("Family 2 (history vs reference policies)", f2)):
        L.append(name)
        for c in fam:
            L.append(f"  {c['outcome']} {c['a']} - {c['b']}: {c['mean']:+.3f} [{c['ci'][0]:+.3f}, {c['ci'][1]:+.3f}] "
                     f"p_holm={c['p_holm']:.4f} n={c['n_runs']} -> {c['verdict']}")
        L.append("")
    L.append("means (primary units): " + "; ".join(f"{k} {v:.3f}" for k, v in sorted(means.items())))
    (dest / "D1_RESULTS.txt").write_text("\n".join(L) + "\n", encoding="utf-8")
    # written once results exist and before anything is shown: the test is never opened again
    P.write(opened, {"opened": True,
                     "protocol_frozen_on": json.loads(spec_d1.SPEC.read_text(encoding="utf-8"))["frozen_on"],
                     "cells": len(cs),
                     "results_sha256": hashlib.sha256((dest / "D1_RESULTS.json").read_bytes()).hexdigest()})
    print("\n".join(L))


if __name__ == "__main__":
    main()
