# -*- coding: utf-8 -*-
"""Protocol D1.1, Section 6a: supplementary analyses of D1.0's main cells, declared before D1.0's opening.

    python camlds_real_full_arch/supplement_d1_1.py --validation-by-scenario         # any time: validation only
    python camlds_real_full_arch/supplement_d1_1.py --open --device cuda             # ONCE, after D1.0's opening

Why (devil's-advocate review, 2026-11-18): every one of D1.0's 29 primary folds trains only on sibling
variants of its test run's scenario (18 of the 29 units are S1). A history effect may therefore be
recognition of a known scenario's script rather than use of the run's own past. These analyses separate
the two. They are descriptive (mean paired difference and 95% bootstrap CI, no p-value, no verdict) and
change no D1.0 result.

  A  per-scenario effect: allpos - NoHistory (MAPPO) on E1 and P1, separately for S1, S3 and S6
  B  scenario-balanced effect: the mean of the three scenario effects, with a stratified bootstrap
     (runs resampled within each scenario, 10,000 resamples, seed 20261103)
  C  unseen scenarios: allpos - NoHistory on the 13 test runs of the 3 scenario-held-out folds, whose
     scenario never appears in training (the generalisation evidence), overall and per scenario
  D  other-run history (evaluation only, no retraining): each trained allpos actor (MAPPO, 29 variant
     folds x seeds 0-9) is evaluated on its own test episodes with h taken from the DONOR run, its fold's
     validation run, a sibling of the same scenario (at step t: the donor's h after min(t, donor length)
     commands). Compared with its own h (D1.0) and with h = 0 (D1.0's sealed test_h0_summary):
       own - donor  > 0: the run's own past matters
       donor - zero > 0 with own - donor about 0: the gain is scenario recognition
     The re-evaluation with its own h must reproduce D1.0's sealed rows exactly (a harness check).
  V  validation gap by scenario (validation only, any time after the main stage): the same split as A and
     C on the cells' best validation E1. No test file is read.

`--open` refuses unless D1.1's spec passes, D1.0's main test has been opened (results_d1/main/
TEST_OPENED.json: D1.0's opening stays the first look) and this supplement has not run before.
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


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--validation-by-scenario", action="store_true")
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
    if not (MAIN / "TEST_OPENED.json").exists():
        raise SystemExit("D1.0's main test has not been opened: D1.0's opening must be the first look")
    if DONE.exists():
        raise SystemExit("the D1.1 supplement has already run; it is not run again")
    import torch
    import pipeline as P
    import run_d1 as R
    marl = P.marl
    cfg, order = R.setting(None)
    folds = P.ordered_folds(order)
    variant = [f for f in folds if f["family"] == "variant_held_out"]
    unseen = [f for f in folds if f["family"] != "variant_held_out"]
    scenario_of = {r["id"]: r["scenario"] for f in folds for r in P.runs(f, "test")}
    sealed = {}
    for arm, lr in PAIR:
        for f in folds:
            for s in SEEDS:
                d = MAIN / "cells" / arm / f["fold"] / f"s{s}" / lr
                res, blob = E.read_sealed(d)
                if (res["arm"], res["learner"], res["test_seed"]) != (arm, lr, R.TEST_SEED + s):
                    raise RuntimeError(f"{d}: not the declared cell")
                sealed[(arm, f["fold"], s)] = blob
    # S3 and S6 runs are test runs twice (variant fold and unseen-scenario fold): never merge the groups
    def group_values(fs):
        return {(arm, m): v for arm, _ in PAIR
                for m, v in unit_values({f["fold"]: {s: sealed[(arm, f["fold"], s)]["test"] for s in SEEDS}
                                         for f in fs}, fs).items()}
    vv, vu = group_values(variant), group_values(unseen)
    out = {"A_per_scenario": by_scenario(vv, scenario_of),
           "B_scenario_balanced": {m: stratified(diff(vv[("allpos", m)], vv[("NoHistory", m)]), scenario_of)
                                   for m in OUTCOMES},
           "C_unseen_scenarios": by_scenario(vu, scenario_of)}
    # D: other-run history, variant folds only
    root = Path(a.encoder_root or (P.REPO / "camlds_encoder" / "out"))
    own, donor, zero, mismatches = defaultdict(dict), defaultdict(dict), defaultdict(dict), []
    for f in variant:
        don_run = P.runs(f, "val")[0]
        for s in SEEDS:
            d = MAIN / "cells" / "allpos" / f["fold"] / f"s{s}" / "MAPPO"
            model, _ = R.load_encoder("allpos", f, s, root, a.device)
            actor = marl.Actor().to(a.device)
            actor.load_state_dict(torch.load(d / "actor.pt", map_location=a.device))
            te = R.specs(P.runs(f, "test"), R.TEST_SEED + s, E.EVAL_REPEATS, cfg)
            bank = marl.HistoryBank(model, P.data.W, a.device)
            again = marl.evaluate_team(actor, cfg, te, bank, 64, a.device)
            if [x["dwell"] for x in again] != [x["dwell"] for x in sealed[("allpos", f["fold"], s)]["test"]]:
                mismatches.append([f["fold"], s])
            dspec = R.specs([don_run], 0, 1, cfg)[0]
            rows_d = marl.evaluate_team(actor, cfg, te, DonorBank(bank.table(dspec)), 64, a.device)
            own[f["fold"]][s], donor[f["fold"]][s] = again, rows_d
            zero[f["fold"]][s] = h0_rows(sealed[("allpos", f["fold"], s)])
    if mismatches:
        raise SystemExit(f"re-evaluation with the actors' own h does not reproduce D1.0's sealed rows: {mismatches[:5]}")
    vo, vd, vz = unit_values(own, variant), unit_values(donor, variant), unit_values(zero, variant)
    out["D_other_run_history"] = {
        "donor_rule": "the fold's validation run (a sibling of the same scenario); h at step t = donor's h after "
                      "min(t, donor length) commands",
        **{f"own_minus_donor|{m}": described(diff(vo[m], vd[m])) for m in OUTCOMES},
        **{f"donor_minus_zero|{m}": described(diff(vd[m], vz[m])) for m in OUTCOMES},
        **{f"own_minus_zero|{m}": described(diff(vo[m], vz[m])) for m in OUTCOMES},
        "means": {f"{n}|{m}": float(np.mean(list(v[m].values()))) for n, v in (("own", vo), ("donor", vd), ("zero", vz))
                  for m in OUTCOMES}}
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "D1_1_SUPPLEMENT.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    DONE.parent.mkdir(parents=True, exist_ok=True)
    P.write(DONE, {"done": True, "results": str(RESULTS / "D1_1_SUPPLEMENT.json")})
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
