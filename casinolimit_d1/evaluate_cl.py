# -*- coding: utf-8 -*-
"""Protocol CL-D1.0 evaluation (PROTOCOL_CL_D1.0.md, Sections 8-10). Frozen with the protocol.

    python casinolimit_d1/evaluate_cl.py --validation-dry-run --study main --device cuda   # each study
    python casinolimit_d1/evaluate_cl.py --open-test --device cuda                         # ONCE, all studies

1. Dry run, per study: every cell's saved actor is re-evaluated on its validation episodes and must
   reproduce its recorded best validation E1 (tolerance 1e-9). No test file is read. For `tune`, a passing
   dry run then writes SELECTION.json: per arm and fold, the setting with the highest validation E1
   averaged over seeds 0-2; ties: D1.0's setting, then grid order (protocol D1.1's rule, nested in the fold).
2. ONE opening for every study: refuses unless the spec passes, the gate passed, every cell of every study
   exists, every study's dry run passed, SELECTION.json equals the selection recomputed from the cells, and
   TEST_OPENED.json is absent. Every sealed file's SHA-256 is checked before it is read, and every cell must
   carry its declared study, setting, arm, learner, test seed, 20 repeats and environment.

Unit = run (attacker): each of the 114 runs is the test run of exactly one fold. Per unit: E1 averaged
over 20 repeats, then over seeds. Statistics are D1.0's (evaluate_d1: mean paired difference, 95%
bootstrap CI with 10,000 resamples of runs, seed 20261103, two-sided Wilcoxon, Holm within a family;
"X outperforms Y" only if Holm p < 0.05 and the CI excludes 0).
  Family 1   allpos vs NoHistory (MAPPO), E1                                      1 comparison
  Family 2   allpos vs none, random, static, fixed, greedy, planner, E1            6 comparisons
  Family 3   allpos vs lstm_allpos, E1                                            1 comparison
  Q4         descriptive (mean difference and CI only): GRU and old Transformer vs allpos; IPPO vs MAPPO
  Family 1, descriptive additions (Section 10): the same contrast on the engaged fraction (E1 / run length),
             by run-length tertile, and per training seed (spread of the seed-level differences)
  Section 8  each sensitivity setting: Family 1 on its own cells (seeds 0-4); reported as sensitivity
  Section 9  Family H: tuned allpos vs tuned NoHistory (seeds 0-2); descriptive per-setting differences
Reference policies are run here on the arms' test episodes (same runs, seed 200000+seed, 20 repeats,
same setting); static and fixed are fitted on the fold's training runs only (seed 400000, 5 repeats),
the planner on the fold's training runs.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cl_world as C  # noqa: E402  (first: registers the CasinoLimit environment)
sys.path.insert(0, str(C.REPO / "camlds_real_full_arch"))
import evaluate_d1 as E  # noqa: E402  (D1.0's statistics, unchanged; imports no environment)

env = C.env
REFERENCES = ("none", "random", "static", "fixed", "greedy", "planner")
SIMPLE = ("none", "random", "greedy", "planner", "clairvoyant")
FIT_SEED, FIT_REPEATS = 400000, 5
TIE = 1e-12
Q4 = (("gru_allpos", "allpos"), ("baseline", "allpos"), ("allpos_IPPO", "allpos"),
      ("NoHistory_IPPO", "NoHistory"), ("allpos_IPPO", "NoHistory_IPPO"))
RESULTS = HERE / "out_test_cl"


def unit_name(arm, learner):
    return arm if learner == "MAPPO" else f"{arm}_{learner}"


def e1_per_run(rows_by_seed) -> dict:
    """{run: E1 averaged over repeats, then over seeds} (evaluate_d1.per_run, E1 only)."""
    return E.per_run(rows_by_seed)["E1"]


def merged(rows_of, folds) -> dict:
    out = {}
    for f in folds:
        out.update(e1_per_run(rows_of(f)))
    return out


def team_activity(rows) -> dict:
    """Descriptive, per run mean over repeats and seeds, then over runs (evaluate_d1.team_activity with
    CasinoLimit's machines)."""
    acc = defaultdict(lambda: defaultdict(list))
    for r in rows:
        n = max(r["length"], 1.0)
        acc[r["run"]]["multi_decoy_share"].append(r["multi_decoy_steps"] / n)
        acc[r["run"]]["lure_chains"].append(r["lure_chains"])
        for z in C.MACHINES:
            acc[r["run"]][f"decoy_share_{z}"].append(r[f"decoy_steps_{z}"] / n)
            acc[r["run"]][f"engaged_{z}"].append(r[f"engaged_{z}"])
    per = [{k: float(np.mean(v)) for k, v in d.items()} for d in acc.values()]
    return {k: float(np.mean([p[k] for p in per])) for k in per[0]} if per else {}


def secondary(rows) -> dict:
    """Descriptive S2 and S3 means over runs (each run averaged first)."""
    acc = defaultdict(lambda: defaultdict(list))
    for r in rows:
        acc[r["run"]]["engaged_fraction"].append(r["dwell"] / max(r["length"], 1.0))
        for k in ("depth", "exposed", "lure_chains", "dead_ends", "capacity_violations"):
            acc[r["run"]][k].append(r[k])
    per = [{k: float(np.mean(v)) for k, v in d.items()} for d in acc.values()]
    return {k: float(np.mean([p[k] for p in per])) for k in per[0]} if per else {}


def fraction_per_run(rows_by_seed) -> dict:
    """{run: engaged fraction (E1 / run length) averaged over repeats, then over seeds}."""
    acc = defaultdict(list)
    for rows in rows_by_seed.values():
        by_run = defaultdict(list)
        for r in rows:
            by_run[r["run"]].append(r["dwell"] / max(r["length"], 1.0))
        for run, v in by_run.items():
            acc[run].append(float(np.mean(v)))
    return {run: float(np.mean(v)) for run, v in acc.items()}


def length_tertiles(lengths: dict) -> list:
    """The runs split into three groups by length (ties broken by run id), sizes as equal as possible."""
    order = sorted(lengths, key=lambda r: (lengths[r], r))
    return [list(g) for g in np.array_split(np.array(order, dtype=object), 3)]


def family1_descriptive(sealed_rows, folds, seeds, a=("allpos", "MAPPO"), b=("NoHistory", "MAPPO")) -> dict:
    """Family 1's contrast, descriptive only: on the engaged fraction, by run-length tertile, and per seed.
    sealed_rows[(arm, learner, fold, seed)] = test rows."""
    of = lambda key, f: {s: sealed_rows[(*key, f["fold"], s)] for s in seeds}
    e1 = {k: merged(lambda f, k=k: of(k, f), folds) for k in (a, b)}
    frac = {}
    for k in (a, b):
        frac[k] = {}
        for f in folds:
            frac[k].update(fraction_per_run(of(k, f)))
    lengths = {r["run"]: float(r["length"]) for f in folds for s in seeds for r in sealed_rows[(*a, f["fold"], s)]}
    groups = []
    for g in length_tertiles(lengths):
        keep = set(g)
        sub = lambda d: {r: v for r, v in d.items() if r in keep}
        groups.append({"runs": len(g), "length_min": min(lengths[r] for r in g), "length_max": max(lengths[r] for r in g),
                       **described(sub(e1[a]), sub(e1[b]))})
    per_seed = []
    for s in seeds:
        va, vb = {}, {}
        for f in folds:
            va.update(e1_per_run({s: sealed_rows[(*a, f["fold"], s)]}))
            vb.update(e1_per_run({s: sealed_rows[(*b, f["fold"], s)]}))
        per_seed.append({"seed": s, "mean_difference": float(np.mean([va[r] - vb[r] for r in va]))})
    diffs = np.array([x["mean_difference"] for x in per_seed])
    return {"engaged_fraction": described(frac[a], frac[b]),
            "by_length_tertile": groups,
            "per_seed": per_seed,
            "per_seed_summary": {"mean": float(diffs.mean()), "sd": float(diffs.std(ddof=1)) if len(diffs) > 1 else None,
                                 "min": float(diffs.min()), "max": float(diffs.max()),
                                 "seeds_positive": int((diffs > 0).sum()), "seeds": len(diffs)},
            "note": "descriptive: not tested, no claim; the run-level CI of Family 1 stays the primary interval"}


def cell_matches(res: dict, key, cfg) -> bool:
    """A sealed cell carries exactly its declared study, setting, arm, learner, test seed, repeats,
    environment and payoff table."""
    import run_cl as R
    study, c, arm, _, seed, lr = key
    return (res.get("protocol") == "CL-D1.0" and res["study"] == study and res["config"] == c
            and {k: res["hp"][k] for k in R.GRID[c]} == R.GRID[c] and (res["arm"], res["learner"]) == (arm, lr)
            and res["test_seed"] == R.TEST_SEED + seed and res["eval_repeats"] == R.EVAL_REPEATS
            and res["env_config"] == cfg.to_dict() and res.get("payoff_sha256") == R.table_sha(study))


def described(a: dict, b: dict) -> dict:
    c = E.contrast(a, b)
    return {"mean": c["mean"], "ci": c["ci"], "n_runs": c["n_runs"], "runs_a_better": c["runs_a_better"],
            "runs_b_better": c["runs_b_better"], "note": "descriptive: not tested, no claim"}


# ── nested selection (protocol D1.1's rule) ───────────────────────────────────

def choose(scores: dict, grid, default: str) -> str:
    best = max(scores.values())
    tied = [c for c in grid if scores[c] >= best - TIE]
    return default if default in tied else tied[0]


def select(validation: dict, folds, seeds, grid, arms, default: str) -> dict:
    """validation[(config, arm, fold, seed)] = best validation E1; per arm and fold, that fold's cells only."""
    sel = {}
    for arm in arms:
        sel[arm] = {}
        for f in folds:
            sc = {c: float(np.mean([validation[(c, arm, f["fold"], s)] for s in seeds])) for c in grid}
            sel[arm][f["fold"]] = {"chosen": choose(sc, grid, default), "validation_E1": sc}
    return sel


def selection_record(sel, grid) -> dict:
    return {"rule": "per arm and fold: highest validation E1 averaged over seeds 0-2; ties: D1.0's setting, "
                    "then grid order; only the fold's own cells", "selection": sel,
            "counts": {arm: dict(Counter(v["chosen"] for v in d.values())) for arm, d in sel.items()},
            "mean_validation_E1_over_folds": {arm: {c: float(np.mean([v["validation_E1"][c] for v in d.values()]))
                                                    for c in grid} for arm, d in sel.items()}}


# ── reference policies on the test episodes ──────────────────────────────────

def fit_static_fixed(fold, cfg, joints=None):
    """On the fold's TRAINING runs only (seed 400000, 5 repeats): static = the best single decoy type in
    every machine; fixed = the best constant joint action of all 6^4. Ties: the first in action order."""
    import gate_cl as G
    specs = C.specs(C.runs(fold, "train"), FIT_SEED, FIT_REPEATS)
    joints = list(itertools.product(range(env.N_ACTIONS), repeat=env.N_AGENTS)) if joints is None else joints
    st = [G.score(C.B.StaticPolicy(a), specs, cfg)["E1"] for a in range(1, env.N_ACTIONS)]
    fj = [G.score(C.B.FixedJointPolicy(j), specs, cfg)["E1"] for j in joints]
    return {"static": 1 + int(np.argmax(st)), "fixed": list(joints[int(np.argmax(fj))])}


def reference_rows(fold, seed, repeats, cfg, chosen) -> dict:
    import gate_cl as G
    B = C.B
    specs = C.specs(C.runs(fold, "test"), 200000 + seed, repeats)
    pols = {"none": B.NullPolicy(), "random": B.RandomPolicy(200000 + seed), "greedy": B.ReactivePolicy(cfg),
            "planner": G.TransitionPlanner(C.runs(fold, "train"), cfg), "clairvoyant": B.ClairvoyantCoordPolicy(cfg),
            "static": B.StaticPolicy(chosen["static"]), "fixed": B.FixedJointPolicy(chosen["fixed"])}
    e = env.CommandEngagementEnv(cfg, C.MAX_STEPS)
    return {n: [env.run_episode(e, s, p) for s in specs] for n, p in pols.items()}


# ── scoring (pure functions of the sealed rows; tested on synthetic rows) ─────

def score_main(sealed, folds, seeds, refs) -> dict:
    """sealed[(arm, learner, fold, seed)] = test rows; refs[(name, fold, seed)] = rows."""
    import run_cl as R
    values = {}
    for arm, lr in R.MAIN_CELLS:
        values[unit_name(arm, lr)] = merged(lambda f, a=arm, l=lr: {s: sealed[(a, l, f["fold"], s)] for s in seeds}, folds)
    for n in (*REFERENCES, "clairvoyant"):
        values[n] = merged(lambda f, n=n: {s: refs[(n, f["fold"], s)] for s in seeds}, folds)
    V = {(k, "E1"): v for k, v in values.items()}
    fams = {"family_1": E.family(V, [("allpos", "NoHistory", "E1")]),
            "family_2": E.family(V, [("allpos", r, "E1") for r in REFERENCES]),
            "family_3": E.family(V, [("allpos", "lstm_allpos", "E1")])}
    q4 = [{"a": a, "b": b, "outcome": "E1", **described(values[a], values[b])} for a, b in Q4]
    rows = lambda key: [r for f in folds for s in seeds for r in (sealed[(*key, f["fold"], s)])]
    team = {unit_name(a, l): team_activity(rows((a, l))) for a, l in R.MAIN_CELLS}
    sec = {unit_name(a, l): secondary(rows((a, l))) for a, l in R.MAIN_CELLS}
    return {**fams, "q4_descriptive": q4, "team_activity_descriptive": team, "secondary_descriptive": sec,
            "family_1_descriptive": family1_descriptive(sealed, folds, seeds),
            "means": {k: float(np.mean(list(v.values()))) for k, v in values.items()},
            "n_units": len(values["allpos"])}


def score_sensitivity(sealed, folds, seeds) -> dict:
    v = {(a, "E1"): merged(lambda f, a=a: {s: sealed[(a, "MAPPO", f["fold"], s)] for s in seeds}, folds)
         for a in ("allpos", "NoHistory")}
    return {"family_1": E.family(v, [("allpos", "NoHistory", "E1")]),
            "family_1_descriptive": family1_descriptive(sealed, folds, seeds),
            "means": {a: float(np.mean(list(x.values()))) for (a, _), x in v.items()}, "n_units": len(v[("allpos", "E1")])}


def score_tune(sealed, sel, folds, seeds, grid, default) -> dict:
    """sealed[(config, arm, fold, seed)]; sel = select(...)."""
    tuned, per_cfg = {}, {}
    for arm in ("allpos", "NoHistory"):
        tuned[(arm, "E1")] = merged(lambda f, a=arm: {s: sealed[(sel[a][f["fold"]]["chosen"], a, f["fold"], s)]
                                                       for s in seeds}, folds)
        for c in grid:
            per_cfg[(c, arm)] = merged(lambda f, a=arm, c=c: {s: sealed[(c, a, f["fold"], s)] for s in seeds}, folds)
    return {"family_H": E.family(tuned, [("allpos", "NoHistory", "E1")]),
            "allpos_minus_NoHistory_by_setting": [{"setting": c, **described(per_cfg[(c, "allpos")], per_cfg[(c, "NoHistory")])}
                                                  for c in grid],
            "tuned_minus_D1_0_setting": [{"arm": a, **described(tuned[(a, "E1")], per_cfg[(default, a)])}
                                         for a in ("allpos", "NoHistory")],
            "means_tuned": {a: float(np.mean(list(v.values()))) for (a, _), v in tuned.items()},
            "n_units": len(tuned[("allpos", "E1")])}


def report(res) -> list:
    L = ["Protocol CL-D1.0 results: CasinoLimit (test opened once; simulation only)", "",
         f"units: {res['main']['n_units']} test runs (attackers); outcome E1 (engaged commands)", ""]

    def fam(title, rows):
        L.append(title)
        for c in rows:
            L.append(f"  E1 {c['a']} - {c['b']}: {c['mean']:+.3f} [{c['ci'][0]:+.3f}, {c['ci'][1]:+.3f}] "
                     f"p_holm={c['p_holm']:.4f} n={c['n_runs']} -> {c['verdict']}")
        L.append("")
    m = res["main"]
    fam("Family 1 (history vs no history)", m["family_1"])
    fam("Family 2 (history vs reference policies)", m["family_2"])
    fam("Family 3 (Transformer history vs LSTM history)", m["family_3"])
    L.append("Q4, descriptive only (no test, no correction, no claim)")
    for c in m["q4_descriptive"]:
        L.append(f"  E1 {c['a']} - {c['b']}: {c['mean']:+.3f} [{c['ci'][0]:+.3f}, {c['ci'][1]:+.3f}] n={c['n_runs']}")
    L += ["", "means (E1 per run): " + "; ".join(f"{k} {v:.3f}" for k, v in sorted(m["means"].items())), ""]

    def f1d(d, title):
        L.append(title)
        c = d["engaged_fraction"]
        L.append(f"  engaged fraction allpos - NoHistory: {c['mean']:+.4f} [{c['ci'][0]:+.4f}, {c['ci'][1]:+.4f}]")
        for g in d["by_length_tertile"]:
            L.append(f"  runs of length {g['length_min']:.0f}-{g['length_max']:.0f} ({g['runs']} runs): "
                     f"{g['mean']:+.3f} [{g['ci'][0]:+.3f}, {g['ci'][1]:+.3f}]")
        s = d["per_seed_summary"]
        sd = "n/a" if s["sd"] is None else f"{s['sd']:.3f}"
        L.append(f"  per training seed: mean {s['mean']:+.3f}, SD {sd}, range [{s['min']:+.3f}, {s['max']:+.3f}], "
                 f"{s['seeds_positive']} of {s['seeds']} seeds positive")
        L.append("")
    f1d(m["family_1_descriptive"], "Family 1, descriptive (engaged fraction, run length, training seeds; no claim)")
    for s, r in res["sensitivity"].items():
        fam(f"Sensitivity {s} (Family 1, seeds 0-4; never replaces the primary result)", r["family_1"])
        f1d(r["family_1_descriptive"], f"Sensitivity {s}, descriptive")
    t = res["tune"]
    fam("Section 9, Family H (each arm tuned per fold on validation; seeds 0-2)", t["family_H"])
    L.append("Descriptive: allpos - NoHistory under each setting")
    for c in t["allpos_minus_NoHistory_by_setting"]:
        L.append(f"  {c['setting']}: {c['mean']:+.3f} [{c['ci'][0]:+.3f}, {c['ci'][1]:+.3f}]")
    return L


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=None)
    ap.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    ap.add_argument("--encoder-root", default=None)
    ap.add_argument("--study", default="main")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--validation-dry-run", action="store_true")
    g.add_argument("--open-test", action="store_true")
    a = ap.parse_args()

    import spec_cl_d1
    spec_cl_d1.require()
    import run_cl as R
    out = a.output or R.OUT
    folds = C.folds()
    gate = HERE / "gate" / "GATE_RESULT.json"
    if not (gate.exists() and json.loads(gate.read_text(encoding="utf-8"))["pass"]):
        raise SystemExit("the CL-D1.0 validity gate has not passed")
    studies = list(R.STUDIES)
    cells = {s: R.all_cells(out, s, folds) for s in studies}
    missing = {s: [k for k, d in cs.items() if not (d / "result.json").exists()] for s, cs in cells.items()}
    opened = out / "TEST_OPENED.json"

    if a.validation_dry_run:
        if a.study not in studies:
            raise SystemExit(f"unknown study {a.study}")
        cs = cells[a.study]
        if missing[a.study]:
            raise SystemExit(f"{len(missing[a.study])} of {len(cs)} cells missing, e.g. {missing[a.study][:3]}")
        root = Path(a.encoder_root or (C.REPO / "casinolimit_encoder" / "out"))
        cfg = R.setting(a.study)
        enc, bad = {}, []
        for (study, c, arm, fold_id, seed, lr), d in cs.items():
            f = next(x for x in folds if x["fold"] == fold_id)
            if (arm, fold_id, seed) not in enc:
                enc[(arm, fold_id, seed)] = R.load_encoder(arm, f, seed, root, a.device)[0]
            got, rec = R.revalidate(d, f, seed, enc[(arm, fold_id, seed)], a.device, cfg)
            if abs(got - rec) > 1e-9:
                bad.append({"cell": [c, arm, lr, fold_id, seed], "recorded": rec, "got": got})
        R.write(out / a.study / "DRY_RUN_VALIDATION.json", {"pass": not bad, "cells": len(cs), "mismatches": bad})
        print(f"CL-D1.0 dry run [{a.study}]: {'PASS' if not bad else 'FAIL'} ({len(cs)} cells, {len(bad)} mismatches)")
        if bad:
            raise SystemExit(1)
        if a.study == "tune":
            val = {(c, arm, fid, s): json.loads((d / "result.json").read_text(encoding="utf-8"))["best_validation_dwell"]
                   for (_, c, arm, fid, s, _l), d in cs.items()}
            rec = selection_record(select(val, folds, R.SEEDS["tune"], list(R.GRID), ("allpos", "NoHistory"),
                                          R.DEFAULT_NAME), list(R.GRID))
            R.write(out / "tune" / "SELECTION.json", rec)
            print("selection (validation only):", rec["counts"])
        return

    # ── open the test, once, for every study ──
    if opened.exists():
        raise SystemExit("the CL-D1.0 test was already opened; it is never opened again")
    for s in studies:
        if missing[s]:
            raise SystemExit(f"study {s}: {len(missing[s])} of {len(cells[s])} cells missing")
        dry = out / s / "DRY_RUN_VALIDATION.json"
        if not (dry.exists() and json.loads(dry.read_text(encoding="utf-8"))["pass"]):
            raise SystemExit(f"study {s}: the validation dry run has not passed")
    sel_path = out / "tune" / "SELECTION.json"
    if not sel_path.exists():
        raise SystemExit("tune/SELECTION.json is missing: run the tune dry run")
    val = {(c, arm, fid, s): json.loads((d / "result.json").read_text(encoding="utf-8"))["best_validation_dwell"]
           for (_, c, arm, fid, s, _l), d in cells["tune"].items()}
    sel = select(val, folds, R.SEEDS["tune"], list(R.GRID), ("allpos", "NoHistory"), R.DEFAULT_NAME)
    if json.loads(sel_path.read_text(encoding="utf-8"))["selection"] != json.loads(json.dumps(sel)):
        raise SystemExit("tune/SELECTION.json differs from the selection recomputed from the cells")
    sealed = {}
    for s in studies:
        cfg = R.setting(s)
        for key, d in cells[s].items():
            res, blob = E.read_sealed(d)
            if not cell_matches(res, key, cfg):
                raise RuntimeError(f"{d}: study, setting, arm, learner, test seed, repeats, environment or "
                                   f"payoff table differ")
            sealed[key] = blob["test"]
    cfg = R.setting("main")
    refs, chosen = {}, {}
    for f in folds:
        chosen[f["fold"]] = fit_static_fixed(f, cfg)
        for s in R.SEEDS["main"]:
            for n, rows in reference_rows(f, s, R.EVAL_REPEATS, cfg, chosen[f["fold"]]).items():
                refs[(n, f["fold"], s)] = rows
    main_sealed = {(arm, lr, fid, s): v for (st, c, arm, fid, s, lr), v in sealed.items() if st == "main"}
    res = {"main": score_main(main_sealed, folds, R.SEEDS["main"], refs),
           "sensitivity": {st: score_sensitivity({(arm, lr, fid, s): v for (x, c, arm, fid, s, lr), v in sealed.items()
                                                  if x == st}, folds, R.SEEDS[st]) for st in R.SENSITIVITIES},
           "tune": score_tune({(c, arm, fid, s): v for (x, c, arm, fid, s, lr), v in sealed.items() if x == "tune"},
                              sel, folds, R.SEEDS["tune"], list(R.GRID), R.DEFAULT_NAME),
           "static_fixed_chosen_on_training": chosen, "selection": json.loads(sel_path.read_text(encoding="utf-8"))}
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "CL_D1_RESULTS.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    L = report(res)
    (RESULTS / "CL_D1_RESULTS.txt").write_text("\n".join(L) + "\n", encoding="utf-8")
    R.write(opened, {"opened": True, "protocol_frozen_on": json.loads(spec_cl_d1.SPEC.read_text(encoding="utf-8"))["frozen_on"],
                     "cells": sum(len(cs) for cs in cells.values()),
                     "results_sha256": hashlib.sha256((RESULTS / "CL_D1_RESULTS.json").read_bytes()).hexdigest()})
    print("\n".join(L))


if __name__ == "__main__":
    main()
