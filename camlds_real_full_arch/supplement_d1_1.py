# -*- coding: utf-8 -*-
"""Protocol D1.1, Section 6a: supplementary analyses of D1.0's main cells, declared before D1.0's opening.

    python camlds_real_full_arch/supplement_d1_1.py --validation-by-scenario   # any time: validation only
    python camlds_real_full_arch/supplement_d1_1.py --dry-run --device cuda    # after D1.0's main stage and
                                                                               #   BEFORE D1.0's opening; no test
    python camlds_real_full_arch/supplement_d1_1.py --open --device cuda       # ONCE, after D1.0's opening

Why (devil's-advocate review and a second review, 2026-11-18): every one of D1.0's 29 primary folds trains
only on sibling variants of its test run's scenario (18 of the 29 units are S1). A history effect may come
from shared scenario information rather than from transferable use of the run's own past. These analyses
investigate that explanation; they cannot settle it alone. All are descriptive (mean paired difference and
95% bootstrap CI, unadjusted, no p-value, no verdict) and change no D1.0 result.

  A  per-scenario effect: allpos - NoHistory (MAPPO) on E1 and P1, separately for S1 (18 runs), S3 (6), S6 (5)
  B  scenario-balanced effect: the mean of the three scenario effects, stratified bootstrap (runs resampled
     within each scenario; 10,000 resamples, seed 20261103). It describes these 3 scenarios only.
  C  held-out scenarios: allpos - NoHistory on the test runs of D1.0's 3 scenario-held-out folds (S2: 2 runs,
     S3: 6, S6: 5), each scenario reported separately; the pooled value is descriptive only. Evidence about
     3 held-out scenarios, not about 13 independent campaigns.
  D  history-substitution sensitivity (evaluation only, no retraining): each trained allpos MAPPO actor
     (29 variant folds x seeds 0-9) is evaluated on its own test episodes (D1.0's test seed, 20 repeats) with
       own      its own h (must reproduce D1.0's sealed rows exactly, every reported field)
       sibling  the h of a same-scenario donor: the fold's FIRST training run (not the validation run the
                checkpoint was selected on)
       cross    the h of a different-scenario donor: the first run (sorted) of the next scenario in the
                order S1 -> S3 -> S6 -> S1
       zero     h = 0 (D1.0's sealed test_h0_summary)
     At step t a donor gives its h after min(t, donor length) commands. Substituted h is input the actor
     never saw in training, so every difference may also reflect mismatched timing, length or content.
     Reading (declared now; "about 0" means the 95% CI includes 0):
       own - sibling about 0 and sibling - cross > 0 (CI excludes 0): consistent with shared scenario
         information being used; not conclusive
       own - sibling > 0 and own - cross > 0: run-specific history OR sensitivity to mismatched input;
         the two cannot be separated here
       anything else: reported as observed, without interpretation
  V  validation gap by scenario (validation only, any time after D1.0's main stage).
Multiplicity: A-D give about 30 unadjusted intervals; no single interval supports a claim, and D1.0's
Family 1 verdict is reported unchanged next to them.

`--dry-run` (validation episodes only, no test file): every allpos MAPPO actor of the 29 variant folds
must reproduce its recorded best validation E1 with its own h, and both donor paths must run. `--open`
refuses unless D1.1's spec passes, the dry run passed, D1.0's main test has been opened (D1.0's opening
stays the first look) and the supplement has not run before.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import evaluate_d1 as E  # noqa: E402

OUTCOMES = E.OUTCOMES
MAIN = HERE / "results_d1" / "main"
DONE = HERE / "results_d1_1" / "SUPPLEMENT_DONE.json"
RESULTS = HERE / "out_test_d1_1"
SEEDS = tuple(range(10))
PAIR = (("allpos", "MAPPO"), ("NoHistory", "MAPPO"))


def described(d_by_run: dict) -> dict:
    d = np.array(list(d_by_run.values()), float)
    lo, hi = E.bootstrap_ci(d) if len(d) else (None, None)
    return {"mean": float(d.mean()) if len(d) else None, "ci": [lo, hi], "n_runs": len(d),
            "runs_positive": int((d > 0).sum()), "runs_negative": int((d < 0).sum()),
            "note": "descriptive: not tested, no claim"}


def diff(a: dict, b: dict) -> dict:
    return {k: a[k] - b[k] for k in sorted(set(a) & set(b))}


def stratified(d_by_run: dict, scenario_of: dict) -> dict:
    """Scenario-balanced mean (each scenario weight 1/k) and a stratified bootstrap CI."""
    groups = defaultdict(list)
    for run, v in d_by_run.items():
        groups[scenario_of[run]].append(v)
    keys = sorted(groups)
    arr = [np.asarray(groups[k], float) for k in keys]
    point = float(np.mean([g.mean() for g in arr]))
    rng = np.random.default_rng(E.BOOT_SEED)
    boots = np.mean([g[rng.integers(0, len(g), (E.BOOT_N, len(g)))].mean(axis=1) for g in arr], axis=0)
    return {"mean": point, "ci": [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
            "scenarios": {k: {"n_runs": len(g), "mean": float(g.mean())} for k, g in zip(keys, arr)},
            "note": "descriptive: scenario-balanced, stratified bootstrap; not tested, no claim"}


def by_scenario(values: dict, scenario_of: dict) -> dict:
    """values[(arm, outcome)] = {run: v} -> per scenario and outcome: allpos - NoHistory."""
    out = {}
    for m in OUTCOMES:
        d = diff(values[("allpos", m)], values[("NoHistory", m)])
        for s in sorted({scenario_of[r] for r in d}):
            out[f"{s}|{m}"] = described({r: v for r, v in d.items() if scenario_of[r] == s})
        out[f"all|{m}"] = described(d)
    return out


ROW_KEYS = ("run", "dwell", "protected", "p1", "length", "horizon", "depth", "exposed", "episode_reward")
SCENARIO_ORDER = ("S1", "S3", "S6")
DRY = HERE / "results_d1_1" / "SUPPLEMENT_DRY_RUN.json"


def same_rows(a: list, b: list) -> bool:
    """Exact reproduction: the same episodes in the same order, with identical values in every field used."""
    pick = lambda rows: [tuple(r.get(k) for k in ROW_KEYS) for r in rows]
    return pick(a) == pick(b)


def donors(fold: dict, runs_of, all_runs: dict) -> tuple:
    """(sibling, cross) donor runs of a variant fold. sibling = the fold's first training run (a sibling of
    the test run's scenario, not the validation run the checkpoint was chosen on); cross = the first run,
    sorted by id, of the next scenario in SCENARIO_ORDER."""
    train = sorted(runs_of(fold, "train"), key=lambda r: r["id"])
    test_s = runs_of(fold, "test")[0]["scenario"]
    nxt = SCENARIO_ORDER[(SCENARIO_ORDER.index(test_s) + 1) % len(SCENARIO_ORDER)]
    cross = min((r for r in all_runs.values() if r["scenario"] == nxt), key=lambda r: r["id"])
    return train[0], cross


class DonorBank:
    """History tables for evaluate_team: every test spec gets the donor's h, aligned by step."""

    def __init__(self, donor_table: np.ndarray):
        self.donor = donor_table

    def tables(self, specs):
        return [self.aligned(s.horizon) for s in specs]

    def aligned(self, horizon: int) -> np.ndarray:
        idx = np.minimum(np.arange(horizon + 1), len(self.donor) - 1)
        return self.donor[idx]


def unit_values(rows_by_fold_seed: dict, folds) -> dict:
    """{fold_id: {seed: rows}} -> {outcome: {run: value}} (evaluate_d1.per_run, merged over folds)."""
    out = {m: {} for m in OUTCOMES}
    for f in folds:
        pr = E.per_run(rows_by_fold_seed[f["fold"]])
        for m in OUTCOMES:
            out[m].update(pr[m])
    return out


def h0_rows(sealed: dict) -> list:
    """D1.0 stores h = 0 as a summary (mean over the cell's test episodes). For a variant fold the cell
    tests one run, so the summary is that run's mean over repeats; returned as one row per cell."""
    s = sealed["test_h0_summary"]
    run = sealed["test"][0]["run"]
    return [{"run": run, "dwell": s["dwell"], "protected": s["protected"], "p1": sealed["test"][0]["p1"]}]


def validation_by_scenario(main: Path = MAIN) -> dict:
    """V: allpos - NoHistory on best validation E1, by the scenario of each fold's test run."""
    import pipeline as P
    folds = P.ordered_folds("frozen")
    rows = {}
    for f in folds:
        for arm, lr in PAIR:
            vals = []
            for s in SEEDS:
                p = main / "cells" / arm / f["fold"] / f"s{s}" / lr / "result.json"
                if p.exists():
                    vals.append(json.loads(p.read_text(encoding="utf-8"))["best_validation_dwell"])
            rows[(arm, f["fold"])] = float(np.mean(vals)) if vals else None
    out = defaultdict(list)
    for f in folds:
        a, b = rows[("allpos", f["fold"])], rows[("NoHistory", f["fold"])]
        if a is not None and b is not None:
            key = "unseen" if f["family"] != "variant_held_out" else "S" + f["fold"].split("_")[0]
            out[key].append(a - b)
    return {k: {"folds": len(v), "mean_gap": float(np.mean(v))} for k, v in sorted(out.items())}


def _setup():
    import pipeline as P
    import run_d1 as R
    cfg, order = R.setting(None)
    folds = P.ordered_folds(order)
    all_runs = {r["id"]: r for f in folds for sp in ("train", "val", "test") for r in P.runs(f, sp)}
    return P, R, cfg, folds, all_runs


def _actor(P, R, f, s, root, device):
    import torch
    d = MAIN / "cells" / "allpos" / f["fold"] / f"s{s}" / "MAPPO"
    model, _ = R.load_encoder("allpos", f, s, root, device)
    actor = P.marl.Actor().to(device)
    actor.load_state_dict(torch.load(d / "actor.pt", map_location=device))
    return d, model, actor


def dry_run(device, root) -> dict:
    """Validation episodes only: own-h reproduction of best validation E1 and both donor paths, every
    allpos MAPPO cell of the 29 variant folds. Reads no test file."""
    P, R, cfg, folds, all_runs = _setup()
    marl, bad, n = P.marl, [], 0
    for f in [x for x in folds if x["family"] == "variant_held_out"]:
        sib, cross = donors(f, P.runs, all_runs)
        for s in SEEDS:
            d, model, actor = _actor(P, R, f, s, root, device)
            res = json.loads((d / "result.json").read_text(encoding="utf-8"))
            va = R.specs(P.runs(f, "val"), R.VAL_SEED + s, res["eval_repeats"], cfg)
            bank = marl.HistoryBank(model, P.data.W, device)
            got = marl.mean_of(marl.evaluate_team(actor, cfg, va, bank, 64, device))
            for donor in (sib, cross):
                rows = marl.evaluate_team(actor, cfg, va, DonorBank(bank.table(R.specs([donor], 0, 1, cfg)[0])), 64, device)
                if len(rows) != len(va):
                    bad.append({"cell": [f["fold"], s], "error": f"donor {donor['id']}: {len(rows)} rows"})
            if abs(got - res["best_validation_dwell"]) > 1e-9:
                bad.append({"cell": [f["fold"], s], "recorded": res["best_validation_dwell"], "got": got})
            n += 1
    return {"pass": not bad and n > 0, "cells": n, "problems": bad}


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--validation-by-scenario", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--open", action="store_true")
    ap.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    ap.add_argument("--encoder-root", default=None)
    a = ap.parse_args()
    if a.validation_by_scenario:
        res = validation_by_scenario()
        print("validation only, allpos - NoHistory best validation E1 (mean over seeds, then folds):")
        for k, v in res.items():
            print(f"  {k}: {v['mean_gap']:+.3f} over {v['folds']} folds")
        return

    import spec_d1_1
    spec_d1_1.require()
    root = Path(a.encoder_root) if a.encoder_root else None
    if a.dry_run:
        import pipeline as P0
        rep = dry_run(a.device, root or (P0.REPO / "camlds_encoder" / "out"))
        P0.write(DRY, rep)
        print(f"D1.1 supplement dry run (validation only): {'PASS' if rep['pass'] else 'FAIL'} "
              f"({rep['cells']} cells, {len(rep['problems'])} problems)")
        raise SystemExit(0 if rep["pass"] else 1)

    if not (DRY.exists() and json.loads(DRY.read_text(encoding="utf-8")).get("pass")):
        raise SystemExit("the supplement's validation dry run has not passed: run --dry-run before D1.0's opening")
    if not (MAIN / "TEST_OPENED.json").exists():
        raise SystemExit("D1.0's main test has not been opened: D1.0's opening must be the first look")
    if DONE.exists():
        raise SystemExit("the D1.1 supplement has already run; it is not run again")
    P, R, cfg, folds, all_runs = _setup()
    marl = P.marl
    root = root or (P.REPO / "camlds_encoder" / "out")
    variant = [f for f in folds if f["family"] == "variant_held_out"]
    unseen = [f for f in folds if f["family"] != "variant_held_out"]
    scenario_of = {rid: r["scenario"] for rid, r in all_runs.items()}
    sealed = {}
    for arm, lr in PAIR:
        for f in folds:
            for s in SEEDS:
                d = MAIN / "cells" / arm / f["fold"] / f"s{s}" / lr
                res, blob = E.read_sealed(d)
                if (res["arm"], res["learner"], res["test_seed"]) != (arm, lr, R.TEST_SEED + s):
                    raise RuntimeError(f"{d}: not the declared cell")
                sealed[(arm, f["fold"], s)] = blob

    # S3 and S6 runs are test runs twice (variant fold and held-out-scenario fold): never merge the groups
    def group_values(fs):
        return {(arm, m): v for arm, _ in PAIR
                for m, v in unit_values({f["fold"]: {s: sealed[(arm, f["fold"], s)]["test"] for s in SEEDS}
                                         for f in fs}, fs).items()}
    vv, vu = group_values(variant), group_values(unseen)
    out = {"A_per_scenario": by_scenario(vv, scenario_of),
           "B_scenario_balanced": {m: stratified(diff(vv[("allpos", m)], vv[("NoHistory", m)]), scenario_of)
                                   for m in OUTCOMES},
           "C_held_out_scenarios": by_scenario(vu, scenario_of)}
    conds = {k: defaultdict(dict) for k in ("own", "sibling", "cross", "zero")}
    mismatches = []
    for f in variant:
        sib, cross = donors(f, P.runs, all_runs)
        for s in SEEDS:
            d, model, actor = _actor(P, R, f, s, root, a.device)
            te = R.specs(P.runs(f, "test"), R.TEST_SEED + s, E.EVAL_REPEATS, cfg)
            bank = marl.HistoryBank(model, P.data.W, a.device)
            again = marl.evaluate_team(actor, cfg, te, bank, 64, a.device)
            if not same_rows(again, sealed[("allpos", f["fold"], s)]["test"]):
                mismatches.append([f["fold"], s])
            conds["own"][f["fold"]][s] = again
            for name, donor in (("sibling", sib), ("cross", cross)):
                dbank = DonorBank(bank.table(R.specs([donor], 0, 1, cfg)[0]))
                conds[name][f["fold"]][s] = marl.evaluate_team(actor, cfg, te, dbank, 64, a.device)
            conds["zero"][f["fold"]][s] = h0_rows(sealed[("allpos", f["fold"], s)])
    if mismatches:
        raise SystemExit(f"re-evaluation with the actors' own h does not reproduce D1.0's sealed rows: {mismatches[:5]}")
    v = {k: unit_values(c, variant) for k, c in conds.items()}
    pairs = (("own", "sibling"), ("own", "cross"), ("sibling", "cross"), ("sibling", "zero"), ("own", "zero"))
    out["D_history_substitution"] = {
        "donors": {f["fold"]: [x["id"] for x in donors(f, P.runs, all_runs)] for f in variant},
        **{f"{x}_minus_{y}|{m}": described(diff(v[x][m], v[y][m])) for x, y in pairs for m in OUTCOMES},
        "means": {f"{k}|{m}": float(np.mean(list(v[k][m].values()))) for k in v for m in OUTCOMES},
        "reading": "declared in PROTOCOL_D1.1.md Section 6a; 'about 0' = the 95% CI includes 0; not conclusive"}
    out["multiplicity"] = "all intervals descriptive and unadjusted; no single interval supports a claim"
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "D1_1_SUPPLEMENT.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    DONE.parent.mkdir(parents=True, exist_ok=True)
    P.write(DONE, {"done": True, "results": str(RESULTS / "D1_1_SUPPLEMENT.json")})
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
