# -*- coding: utf-8 -*-
"""Protocol D1.1 evaluation (PROTOCOL_D1.1.md, Sections 5-6). Frozen with D1.1.

    python camlds_real_full_arch/evaluate_d1_1.py --validation-dry-run --device cuda   # dry run + selection
    python camlds_real_full_arch/evaluate_d1_1.py --open-test --device cuda            # ONCE

1. Dry run: every cell's saved actor is re-evaluated on its validation episodes and must reproduce the
   best validation E1 recorded at training (tolerance 1e-9). No test file is read. If it passes, the
   nested selection is written to SELECTION.json: for each arm and each fold separately, the setting
   with the highest validation E1 averaged over seeds 0-2 (ties: the D1.0 setting, then grid order).
   Only that fold's own cells are used, so no fold's test run takes part in its own selection.
2. Open the test once: refuses unless both specs pass, all 1,728 cells exist, the dry run passed,
   SELECTION.json equals the selection recomputed from the cells, and TEST_OPENED.json is absent. Every
   sealed file's SHA-256 is checked before it is read, and every cell must carry its declared setting,
   arm, learner, test seed, 20 repeats, environment and order.

Unit = test run of the 29 variant-held-out folds (the 3 scenario-held-out folds are descriptive). Per
unit and arm: the outcome of the setting selected for that arm in that fold, averaged over 20 repeats,
then over seeds 0-2.
Family H (Q5, tested): tuned allpos vs tuned NoHistory on E1 and P1 (2 comparisons), with D1.0's rules
(evaluate_d1: mean paired difference, 95% bootstrap CI with 10,000 resamples of runs, seed 20261103,
two-sided Wilcoxon, Holm within the family; "outperforms" only if Holm p < 0.05 and the CI excludes 0).
Descriptive only (no p-value, no verdict): allpos - NoHistory under each of the 9 settings; tuned - D1.0
setting for each arm; how often each setting is selected; mean validation E1 per setting and arm.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import evaluate_d1 as E  # noqa: E402  (statistics and file rules of D1.0, unchanged)

OUTCOMES = E.OUTCOMES
EVAL_REPEATS = E.EVAL_REPEATS
TIE = 1e-12
FAMILY_H = [("allpos", "NoHistory", m) for m in OUTCOMES]
RESULTS = HERE / "out_test_d1_1"


def cells(out: Path, folds, seeds, grid, arms):
    """{(config, arm, fold, seed): cell directory}, the layout run_d1_1 writes."""
    return {(c, arm, f["fold"], s): out / "cells" / c / arm / f["fold"] / f"s{s}" / "MAPPO"
            for c in grid for arm in arms for f in folds for s in seeds}


def choose(scores: dict, grid, default: str) -> str:
    """The setting with the highest score; ties (within 1e-12): the D1.0 setting, then grid order."""
    best = max(scores.values())
    tied = [c for c in grid if scores[c] >= best - TIE]
    return default if default in tied else tied[0]


def select(validation: dict, folds, seeds, grid, arms, default: str) -> dict:
    """Nested selection. validation[(config, arm, fold, seed)] = best validation E1 of that cell.
    For each arm and fold, only that fold's cells are used."""
    sel = {}
    for arm in arms:
        sel[arm] = {}
        for f in folds:
            scores = {c: float(np.mean([validation[(c, arm, f["fold"], s)] for s in seeds])) for c in grid}
            sel[arm][f["fold"]] = {"chosen": choose(scores, grid, default), "validation_E1": scores}
    return sel


def read_validation(cs: dict) -> dict:
    return {k: json.loads((d / "result.json").read_text(encoding="utf-8"))["best_validation_dwell"]
            for k, d in cs.items()}


def selection_record(sel: dict, folds, grid, arms) -> dict:
    primary = [f["fold"] for f in folds if f["family"] == "variant_held_out"]
    counts = {arm: {g: {c: n for c, n in Counter(sel[arm][fid]["chosen"] for fid in fids).items()}
                    for g, fids in (("variant_folds", primary), ("all_folds", [f["fold"] for f in folds]))}
              for arm in arms}
    mean_val = {arm: {c: float(np.mean([sel[arm][f["fold"]]["validation_E1"][c] for f in folds])) for c in grid}
                for arm in arms}
    return {"rule": "per arm and fold: highest validation E1 averaged over seeds 0-2; ties: the D1.0 "
                    "setting, then grid order; only the fold's own cells", "selection": sel,
            "counts": counts, "mean_validation_E1_over_folds": mean_val}


def merged(rows_of, fold_list, seeds):
    """{outcome: {run: value}} over fold_list; rows_of(fold) -> {seed: test rows}."""
    out = {m: {} for m in OUTCOMES}
    for f in fold_list:
        pr = E.per_run(rows_of(f))
        for m in OUTCOMES:
            out[m].update(pr[m])
    return out


def score(sealed: dict, sel: dict, folds, seeds, grid, arms, default: str) -> dict:
    """sealed[(config, arm, fold, seed)] = test rows. Returns the D1.1 results (Section 6)."""
    primary = [f for f in folds if f["family"] == "variant_held_out"]
    unseen = [f for f in folds if f["family"] != "variant_held_out"]
    tuned, tuned_unseen, per_cfg = {}, {}, {}
    for arm in arms:
        def tuned_rows(f, arm=arm):
            c = sel[arm][f["fold"]]["chosen"]
            return {s: sealed[(c, arm, f["fold"], s)] for s in seeds}
        t = merged(tuned_rows, primary, seeds)
        u = merged(tuned_rows, unseen, seeds)
        for m in OUTCOMES:
            tuned[(arm, m)], tuned_unseen[(arm, m)] = t[m], u[m]
        for c in grid:
            v = merged(lambda f, c=c, arm=arm: {s: sealed[(c, arm, f["fold"], s)] for s in seeds}, primary, seeds)
            for m in OUTCOMES:
                per_cfg[(c, arm, m)] = v[m]
    fam = E.family(tuned, FAMILY_H)

    def described(a, b):
        c = E.contrast(a, b)
        return {"mean": c["mean"], "ci": c["ci"], "n_runs": c["n_runs"], "runs_a_better": c["runs_a_better"],
                "runs_b_better": c["runs_b_better"], "note": "descriptive: not tested, no claim"}
    by_setting = [{"setting": c, "outcome": m, "a": "allpos", "b": "NoHistory",
                   **described(per_cfg[(c, "allpos", m)], per_cfg[(c, "NoHistory", m)])}
                  for c in grid for m in OUTCOMES]
    tuned_vs_default = [{"arm": arm, "outcome": m, "a": "tuned", "b": default,
                         **described(tuned[(arm, m)], per_cfg[(default, arm, m)])}
                        for arm in arms for m in OUTCOMES]
    return {"family_H": fam, "allpos_minus_NoHistory_by_setting": by_setting,
            "tuned_minus_D1_0_setting": tuned_vs_default,
            "means_tuned_primary": {f"{a}|{m}": float(np.mean(list(v.values()))) for (a, m), v in tuned.items()},
            "means_by_setting_primary": {f"{c}|{a}|{m}": float(np.mean(list(v.values())))
                                         for (c, a, m), v in per_cfg.items()},
            "unseen_scenarios_descriptive_tuned": {f"{a}|{m}": v for (a, m), v in tuned_unseen.items()},
            "n_units": {m: len(tuned[("allpos", m)]) for m in OUTCOMES}}


def report(res: dict, sel_rec: dict) -> list:
    L = ["Protocol D1.1 results: hyperparameter sensitivity (test opened once; simulation only;",
         "a sensitivity result, never a replacement for the D1.0 primary result)", "",
         f"units: E1 {res['n_units']['E1']} test runs, P1 {res['n_units']['P1']} (S4 excluded); seeds 0-2", "",
         "Family H (Q5): allpos vs NoHistory, each with its own setting selected per fold on validation"]
    for c in res["family_H"]:
        L.append(f"  {c['outcome']} allpos - NoHistory: {c['mean']:+.3f} [{c['ci'][0]:+.3f}, {c['ci'][1]:+.3f}] "
                 f"p_holm={c['p_holm']:.4f} n={c['n_runs']} -> {c['verdict']}")
    L += ["", "Descriptive only (no test, no correction, no claim): allpos - NoHistory under each setting"]
    for c in res["allpos_minus_NoHistory_by_setting"]:
        L.append(f"  {c['setting']} {c['outcome']}: {c['mean']:+.3f} [{c['ci'][0]:+.3f}, {c['ci'][1]:+.3f}] n={c['n_runs']}")
    L += ["", "Descriptive only: tuned - D1.0 setting, per arm"]
    for c in res["tuned_minus_D1_0_setting"]:
        L.append(f"  {c['arm']} {c['outcome']}: {c['mean']:+.3f} [{c['ci'][0]:+.3f}, {c['ci'][1]:+.3f}] n={c['n_runs']}")
    L += ["", "Settings selected (variant folds): "
          + "; ".join(f"{arm}: " + ", ".join(f"{c} x{n}" for c, n in sorted(v["variant_folds"].items()))
                      for arm, v in sel_rec["counts"].items())]
    return L


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=None)
    ap.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    ap.add_argument("--encoder-root", default=None)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--validation-dry-run", action="store_true")
    g.add_argument("--open-test", action="store_true")
    a = ap.parse_args()

    import spec_d1_1
    spec_d1_1.require()
    import run_d1 as R
    import run_d1_1 as T
    P = R.P
    out = a.output or T.OUT
    cfg, order = R.setting(None)
    folds = P.ordered_folds(order)
    seeds, grid, arms = list(T.SEEDS), list(T.GRID), list(T.ARMS)
    cs = cells(out, folds, seeds, grid, arms)
    missing = [k for k, d in cs.items() if not (d / "result.json").exists()]
    if missing:
        raise SystemExit(f"{len(missing)} of {len(cs)} cells missing, e.g. {missing[:3]}")
    dry, sel_path, opened = out / "DRY_RUN_VALIDATION.json", out / "SELECTION.json", out / "TEST_OPENED.json"

    if a.validation_dry_run:
        root = Path(a.encoder_root or (P.REPO / "camlds_encoder" / "out"))
        encoders, bad = {}, []
        for (c, arm, fold_id, seed), d in cs.items():
            f = next(x for x in folds if x["fold"] == fold_id)
            if (arm, fold_id, seed) not in encoders:
                encoders[(arm, fold_id, seed)] = R.load_encoder(arm, f, seed, root, a.device)[0]
            got, rec = R.revalidate(d, f, seed, encoders[(arm, fold_id, seed)], a.device, cfg)
            if abs(got - rec) > 1e-9:
                bad.append({"cell": [c, arm, fold_id, seed], "recorded": rec, "got": got})
        P.write(dry, {"pass": not bad, "cells": len(cs), "mismatches": bad})
        print(f"D1.1 dry run: {'PASS' if not bad else 'FAIL'} ({len(cs)} cells, {len(bad)} mismatches)")
        if bad:
            raise SystemExit(1)                             # a failed dry run stops any chained command
        rec = selection_record(select(read_validation(cs), folds, seeds, grid, arms, T.DEFAULT_NAME),
                               folds, grid, arms)
        P.write(sel_path, rec)
        print("selection (validation only): " + "; ".join(
            f"{arm}: " + ", ".join(f"{c} x{n}" for c, n in sorted(v["variant_folds"].items()))
            for arm, v in rec["counts"].items()))
        return

    # ── open the test, once ──
    if opened.exists():
        raise SystemExit("the D1.1 test was already opened; it is never opened again")
    if not dry.exists() or not json.loads(dry.read_text(encoding="utf-8"))["pass"]:
        raise SystemExit("the D1.1 validation dry run has not passed")
    if not sel_path.exists():
        raise SystemExit("SELECTION.json is missing: run the validation dry run")
    sel = select(read_validation(cs), folds, seeds, grid, arms, T.DEFAULT_NAME)
    sel_rec = json.loads(sel_path.read_text(encoding="utf-8"))
    if sel_rec["selection"] != json.loads(json.dumps(sel)):
        raise SystemExit("SELECTION.json differs from the selection recomputed from the cells")
    sealed = {}
    for key, d in cs.items():
        res, s = E.read_sealed(d)
        c, arm, _, seed = key
        if (res.get("protocol") != "D1.1" or res["config"] != c
                or {k: res["hp"][k] for k in T.GRID[c]} != T.GRID[c]
                or (res["arm"], res["learner"]) != (arm, "MAPPO") or res["test_seed"] != R.TEST_SEED + seed
                or res["eval_repeats"] != EVAL_REPEATS or res["env_config"] != cfg.to_dict()
                or res["order"] != order):
            raise RuntimeError(f"{d}: setting, arm, learner, test seed, repeats, environment or order "
                               f"differ from the protocol")
        sealed[key] = s["test"]
    res = score(sealed, sel, folds, seeds, grid, arms, T.DEFAULT_NAME)
    res.update(selection=sel_rec, env_config=cfg.to_dict(), order=order, grid=T.GRID)
    dest = RESULTS
    dest.mkdir(exist_ok=True)
    (dest / "D1_1_RESULTS.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    L = report(res, sel_rec)
    (dest / "D1_1_RESULTS.txt").write_text("\n".join(L) + "\n", encoding="utf-8")
    # written once results exist and before anything is shown: the test is never opened again
    P.write(opened, {"opened": True,
                     "protocol_frozen_on": json.loads(spec_d1_1.SPEC.read_text(encoding="utf-8"))["frozen_on"],
                     "cells": len(cs),
                     "results_sha256": hashlib.sha256((dest / "D1_1_RESULTS.json").read_bytes()).hexdigest()})
    print("\n".join(L))


if __name__ == "__main__":
    main()
