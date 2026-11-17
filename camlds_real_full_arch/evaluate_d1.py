# -*- coding: utf-8 -*-
"""Protocol D1.0 evaluation (Section 9). Frozen with the protocol.

    python camlds_real_full_arch/evaluate_d1.py --validation-dry-run --device cuda
    python camlds_real_full_arch/evaluate_d1.py --open-test --device cuda       # ONCE
    ... --sensitivity mean    (Section 8: its own dry run and its own single opening; Family 1 only,
                               seeds 0-4, reported as a sensitivity result, never as the main claim)

1. Dry run: every main cell's saved actor is re-evaluated on its validation episodes and must
   reproduce the best validation E1 recorded at training. No test file is read.
2. Open the test once: refuses unless the spec passes, all 2,240 main cells exist (run_d1.MAIN_CELLS:
   7 arm/learner pairs x 32 folds x 10 seeds), the dry run passed and the test was never opened. Every sealed
   file's SHA-256 is checked before it is read, and every cell must have used the protocol's test seed,
   20 repeats, setting and order, so the reference policies below are scored on exactly the arms' test
   episodes.

Unit = test run of the 29 variant-held-out folds (the 3 scenario-held-out folds are descriptive). Per
unit: the outcome averaged over 20 repeats, then over 10 seeds. E1 = engaged commands; P1 = defense
success on runs with p1 (S4 excluded).
Family 1 (Q1): allpos vs NoHistory on E1 and P1 (2 comparisons).
Family 2 (Q2): allpos vs none, random, static, fixed, greedy, planner on E1 and P1 (12 comparisons). The
reference policies are run here on the same test episodes; static, fixed (each per outcome) and planner
are fitted on the fold's training runs only.
Family 3 (D7): allpos vs lstm_allpos on E1 and P1 (2 comparisons): the proposal's "MARL without the
Transformer".
Q4 (D8), descriptive only, scored at the same single opening: GRU and old-Transformer history vs
allpos; IPPO vs MAPPO for allpos and for NoHistory; allpos vs NoHistory under IPPO. Mean paired
difference and 95% bootstrap CI only: no test, no correction, no verdict, no claim.
Per comparison: mean paired difference, 95% bootstrap CI (10,000 resamples of runs, seed 20261103),
two-sided Wilcoxon signed-rank (zero differences dropped), Holm within each family (the families answer
different questions and are not corrected across). "X outperforms Y" only if Holm p < 0.05 and the CI
excludes 0.
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
PRIMARY_ARMS = ("allpos", "NoHistory")              # Family 1; every sensitivity analysis
MAIN_ARMS = PRIMARY_ARMS + ("lstm_allpos",)          # + Family 3
MAIN_CELLS = (("allpos", "MAPPO"), ("NoHistory", "MAPPO"), ("lstm_allpos", "MAPPO"),     # tested
              ("gru_allpos", "MAPPO"), ("baseline", "MAPPO"),                            # Q4, descriptive
              ("allpos", "IPPO"), ("NoHistory", "IPPO"))
SENSITIVITY_CELLS = (("allpos", "MAPPO"), ("NoHistory", "MAPPO"))
REFERENCES = ("none", "random", "static", "fixed", "greedy", "planner")
SIMPLE = ("none", "random", "greedy", "planner", "clairvoyant")   # nothing chosen per outcome
FITTED = ("static", "fixed")                         # chosen per outcome on the fold's training runs
NAMES = {"allpos": "history agents (allpos)", "NoHistory": "agents without history",
         "lstm_allpos": "history agents (LSTM encoder)", "gru_allpos": "history agents (GRU encoder)",
         "baseline": "history agents (old Transformer)", "allpos_IPPO": "history agents, IPPO",
         "NoHistory_IPPO": "agents without history, IPPO",
         "none": "no decoys", "random": "random", "static": "static honeypot (one decoy type everywhere)",
         "fixed": "best fixed allocation", "greedy": "greedy (reactive)", "planner": "transition planner",
         "clairvoyant": "clairvoyant"}
FIT_SEED, FIT_REPEATS = 400000, 5
EVAL_REPEATS = 20
OUTCOMES = ("E1", "P1")


# Q4 (D8): described, never tested
DESCRIPTIVE_CONTRASTS = (("gru_allpos", "allpos"), ("baseline", "allpos"), ("allpos_IPPO", "allpos"),
                         ("NoHistory_IPPO", "NoHistory"), ("allpos_IPPO", "NoHistory_IPPO"))


def unit_name(arm, learner):
    """Name of an arm/learner pair in the results: the arm for MAPPO, arm_IPPO for IPPO."""
    return arm if learner == "MAPPO" else f"{arm}_{learner}"


def describe(values: dict) -> list:
    """Q4: mean paired difference and 95% bootstrap CI per contrast and outcome. No p-value, no verdict."""
    out = []
    for a, b in DESCRIPTIVE_CONTRASTS:
        for m in OUTCOMES:
            c = contrast(values[(a, m)], values[(b, m)])
            out.append({"a": a, "b": b, "outcome": m, "mean": c["mean"], "ci": c["ci"], "n_runs": c["n_runs"],
                        "runs_a_better": c["runs_a_better"], "runs_b_better": c["runs_b_better"],
                        "note": "descriptive: not tested, no claim"})
    return out


def family_pairs():
    """The three tested families of Section 9, each Holm-corrected on its own."""
    return {"family_1": [("allpos", "NoHistory", m) for m in OUTCOMES],
            "family_2": [("allpos", r, m) for r in REFERENCES for m in OUTCOMES],
            "family_3": [("allpos", "lstm_allpos", m) for m in OUTCOMES]}


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

def cells(out: Path, folds, seeds, pairs):
    """{(arm, learner, fold, seed): cell directory}, the layout run_d1 writes."""
    return {(arm, lr, f["fold"], s): out / "cells" / arm / f["fold"] / f"s{s}" / lr
            for arm, lr in pairs for f in folds for s in seeds}


def read_sealed(dest: Path):
    res = json.loads((dest / "result.json").read_text(encoding="utf-8"))
    blob = (dest / "sealed_test.json").read_bytes()
    if hashlib.sha256(blob).hexdigest() != res["sealed_test_sha256"]:
        raise RuntimeError(f"{dest}: sealed test file does not match its recorded SHA-256")
    return res, json.loads(blob)


# ── reference policies on the test episodes ──────────────────────────────────

def reference_rows(fold, seed, repeats, env, P, G, R, cfg, chosen):
    """Reference policies on the fold's test episodes: the same runs, test seed, repeats and setting as
    the arms' cells (R.specs), so every comparison is paired on identical randomness."""
    B = G.B
    train = P.runs(fold, "train")
    specs = R.specs(P.runs(fold, "test"), R.TEST_SEED + seed, repeats, cfg)
    pols = {"none": B.NullPolicy(), "random": B.RandomPolicy(R.TEST_SEED + seed),
            "greedy": B.ReactivePolicy(cfg), "planner": G.TransitionPlanner(train, cfg),
            "clairvoyant": B.ClairvoyantCoordPolicy(cfg)}
    out = {}
    e = env.CommandEngagementEnv(cfg)
    for name, pol in pols.items():
        out[name] = [env.run_episode(e, s, pol) for s in specs]
    for m in OUTCOMES:
        out[f"static_{m}"] = [env.run_episode(e, s, B.StaticPolicy(chosen["static"][m])) for s in specs]
        out[f"fixed_{m}"] = [env.run_episode(e, s, B.FixedJointPolicy(chosen["fixed"][m])) for s in specs]
    return out


def fit_static_fixed(fold, env, P, G, R, cfg, joints=None):
    """Per outcome, on the fold's TRAINING runs only (seed 400000, 5 repeats): static = the best single
    decoy type deployed in every zone (the proposal's static honeypot); fixed = the best constant joint
    action over all 6^4. P1 is fitted on the training runs with p1. Ties: the first in action order."""
    B = G.B
    specs = R.specs(P.runs(fold, "train"), FIT_SEED, FIT_REPEATS, cfg)
    joints = list(itertools.product(range(env.N_ACTIONS), repeat=env.N_AGENTS)) if joints is None else joints
    best = {"static": {}, "fixed": {}}
    for m in OUTCOMES:
        use = specs if m == "E1" else [s for s in specs if s.p1]
        sc = [G.score(B.StaticPolicy(a), use, cfg)[m] for a in range(1, env.N_ACTIONS)]
        best["static"][m] = 1 + int(np.argmax(sc))
        fj = [G.score(B.FixedJointPolicy(j), use, cfg)[m] for j in joints]
        best["fixed"][m] = list(joints[int(np.argmax(fj))])
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=None)
    ap.add_argument("--sensitivity", default=None)
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
    if a.sensitivity and a.sensitivity not in R.SENSITIVITIES:
        raise SystemExit(f"unknown sensitivity {a.sensitivity}")
    if (PRIMARY_ARMS, MAIN_ARMS, MAIN_CELLS, SENSITIVITY_CELLS) != \
            (R.PRIMARY_ARMS, R.MAIN_ARMS, R.MAIN_CELLS, R.SENSITIVITY_CELLS):
        raise SystemExit("evaluate_d1 and run_d1 disagree on the arms or cells")
    out = a.output or (HERE / "results_d1" / (a.sensitivity or "main"))
    cfg, order = R.setting(a.sensitivity)
    folds = P.ordered_folds(order)
    seeds = list(range(5)) if a.sensitivity else list(range(10))
    plan = SENSITIVITY_CELLS if a.sensitivity else MAIN_CELLS
    cs = cells(out, folds, seeds, plan)
    missing = [k for k, d in cs.items() if not (d / "result.json").exists()]
    if missing:
        raise SystemExit(f"{len(missing)} of {len(cs)} cells missing, e.g. {missing[:3]}")
    dry = out / "DRY_RUN_VALIDATION.json"
    opened = out / "TEST_OPENED.json"

    if a.validation_dry_run:
        root = Path(a.encoder_root or (P.REPO / "camlds_encoder" / "out"))
        bad = []
        for (arm, learner, fold_id, seed), d in cs.items():
            res = json.loads((d / "result.json").read_text(encoding="utf-8"))
            f = next(x for x in folds if x["fold"] == fold_id)
            model, _ = R.load_encoder(arm, f, seed, root, a.device, cell=d.parent, order=order)
            actor = marl.Actor().to(a.device)
            actor.load_state_dict(torch.load(d / "actor.pt", map_location=a.device))
            va = R.specs(P.runs(f, "val"), R.VAL_SEED + seed, res["eval_repeats"], cfg)
            bank = marl.HistoryBank(model, P.data.W, a.device, h_zero=(model is None))
            rows = marl.evaluate_team(actor, cfg, va, bank, 64, a.device)
            got = marl.mean_of(rows)
            if abs(got - res["best_validation_dwell"]) > 1e-9:
                bad.append({"cell": [arm, learner, fold_id, seed], "recorded": res["best_validation_dwell"],
                            "got": got})
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
        if (res["test_seed"] != R.TEST_SEED + key[3] or res["eval_repeats"] != EVAL_REPEATS
                or res["env_config"] != cfg.to_dict() or res["order"] != order
                or (res["arm"], res["learner"]) != key[:2]):
            raise RuntimeError(f"{d}: arm, learner, test seed, repeats, setting or order differ from the protocol")
        sealed[key] = s["test"]
    primary_folds = [f for f in folds if f["family"] == "variant_held_out"]

    values, descriptive = {}, {}
    for arm, lr in plan:
        name = unit_name(arm, lr)
        for group, fs in (("primary", primary_folds), ("unseen", [f for f in folds if f not in primary_folds])):
            merged = {m: {} for m in OUTCOMES}
            for f in fs:
                pr = per_run({s: sealed[(arm, lr, f["fold"], s)] for s in seeds})
                for m in OUTCOMES:
                    merged[m].update(pr[m])
            for m in OUTCOMES:
                (values if group == "primary" else descriptive)[(name, m)] = merged[m]
    pairs = family_pairs()
    f1 = family(values, pairs["family_1"])
    if a.sensitivity:
        res = {"setting": a.sensitivity, "env_config": cfg.to_dict(), "order": order, "family_1": f1,
               "means_primary": {f"{n}|{m}": float(np.mean(list(v.values()))) for (n, m), v in values.items()},
               "n_units": {m: len(values[("allpos", m)]) for m in OUTCOMES}}
        dest = HERE / "out_test_d1"
        dest.mkdir(exist_ok=True)
        (dest / f"D1_SENSITIVITY_{a.sensitivity}.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
        L = [f"Protocol D1.0 sensitivity '{a.sensitivity}' (simulation only; not the main claim)",
             f"units: E1 {res['n_units']['E1']}, P1 {res['n_units']['P1']}; seeds 0-4"]
        for c in f1:
            L.append(f"  {c['outcome']} allpos - NoHistory: {c['mean']:+.3f} [{c['ci'][0]:+.3f}, {c['ci'][1]:+.3f}] "
                     f"p_holm={c['p_holm']:.4f} -> {c['verdict']}")
        P.write(opened, {"opened": True, "setting": a.sensitivity, "cells": len(cs)})
        print("\n".join(L))
        return
    # reference policies on the same test episodes
    ref_vals = {(n, m): {} for n in (*SIMPLE, *FITTED) for m in OUTCOMES}
    chosen = {}
    for f in primary_folds:
        chosen[f["fold"]] = fit_static_fixed(f, env, P, G, R, cfg)
        rows = {n: {} for n in SIMPLE}
        fitted = {(n, m): {} for n in FITTED for m in OUTCOMES}
        for s in seeds:
            rr = reference_rows(f, s, EVAL_REPEATS, env, P, G, R, cfg, chosen[f["fold"]])
            for n in SIMPLE:
                rows[n][s] = rr[n]
            for n, m in fitted:
                fitted[(n, m)][s] = rr[f"{n}_{m}"]
        for n in SIMPLE:
            pr = per_run(rows[n])
            for m in OUTCOMES:
                ref_vals[(n, m)].update(pr[m])
        for (n, m), by_seed in fitted.items():
            ref_vals[(n, m)].update(per_run(by_seed)[m])
    values.update(ref_vals)

    f2 = family(values, pairs["family_2"])
    f3 = family(values, pairs["family_3"])
    q4 = describe(values)
    means = {f"{n}|{m}": float(np.mean(list(v.values()))) for (n, m), v in values.items()}
    res = {"family_1": f1, "family_2": f2, "family_3": f3, "q4_descriptive": q4, "means_primary": means,
           "unseen_scenarios_descriptive": {f"{n}|{m}": v for (n, m), v in descriptive.items()},
           "static_fixed_chosen_on_training": chosen, "env_config": cfg.to_dict(),
           "n_units": {m: len(values[("allpos", m)]) for m in OUTCOMES}}
    dest = HERE / "out_test_d1"
    dest.mkdir(exist_ok=True)
    (dest / "D1_RESULTS.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    L = ["Protocol D1.0 results (test opened once; simulation only)", "",
         f"units: E1 {res['n_units']['E1']} test runs, P1 {res['n_units']['P1']} (S4 excluded)", ""]
    for name, fam in (("Family 1 (history vs no history)", f1), ("Family 2 (history vs reference policies)", f2),
                      ("Family 3 (Transformer history vs LSTM history)", f3)):
        L.append(name)
        for c in fam:
            L.append(f"  {c['outcome']} {c['a']} - {c['b']}: {c['mean']:+.3f} [{c['ci'][0]:+.3f}, {c['ci'][1]:+.3f}] "
                     f"p_holm={c['p_holm']:.4f} n={c['n_runs']} -> {c['verdict']}")
        L.append("")
    L.append("Q4, descriptive only (no test, no correction, no claim)")
    for c in q4:
        L.append(f"  {c['outcome']} {c['a']} - {c['b']}: {c['mean']:+.3f} [{c['ci'][0]:+.3f}, {c['ci'][1]:+.3f}] "
                 f"n={c['n_runs']}")
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
