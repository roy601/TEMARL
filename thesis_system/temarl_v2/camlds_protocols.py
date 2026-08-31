# -*- coding: utf-8 -*-
"""
TEMARL v2 — CAM-LDS: what the corpus can and cannot support
============================================================
A single held-out number for CAM-LDS is not defensible, because the answer
depends entirely on what "held out" means. This script measures all three
protocols so the honest estimate is BRACKETED rather than cherry-picked.

  P1  LEAVE-ONE-SCENARIO-OUT  — test campaign never seen.
      Pessimistic bound. Mean ACROSS-scenario Jaccard is 0.078, so ~92% of the
      test campaign's techniques are absent from training: the model is being
      asked to predict labels it has never observed. Near-zero here is a
      property of the CORPUS, not a failure of the model.

  P2  WITHIN-SCENARIO VARIANT HOLD-OUT — campaign type seen, execution variant
      unseen. This is the well-posed task, and the one that matches deployment:
      a honeypot operator knows their threat model but not which variant runs.
      Only S1 (18 variants), S3 (8) and S6 (5) have enough variants to support it.

  P3  RUN-LEVEL RANDOM SPLIT — the protocol a naive pipeline would use.
      Reported ONLY as a contrast: within-scenario Jaccard is 0.871, so this
      places near-duplicates of the test runs into training. The gap P3 - P2 is
      a direct measurement of how much such a number is memorisation.

Reporting P3 alone would materially overstate the system. Reporting P1 alone
would understate it. The pair is the result.
"""

import json
import os
import sys

import numpy as np

from vocab_v2 import NUM_TECHNIQUES
from data_real import (load_camlds_verified, scenario_loso_folds, to_windows,
                       trivial_baselines)
from encoders import build_matched_suite
from train_real import DEVICE, score, train_on_real

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = ("Transformer", "GRU", "SetEncoder")
SEEDS = (0, 1, 2)
STEPS = 600
BATCH = 64
UNIFORM_PPL = float(NUM_TECHNIQUES + 2)


def fit_eval(name, X, L, Y, S, fit_seq, val_seq, te_seq, sd):
    fit_w = np.nonzero(np.isin(S, fit_seq))[0]
    val_w = np.nonzero(np.isin(S, val_seq))[0]
    te_w = np.nonzero(np.isin(S, te_seq))[0]
    if len(fit_w) == 0 or len(te_w) == 0 or len(val_w) == 0:
        return None
    suite, _, _ = build_matched_suite()
    enc = suite[name].to(DEVICE)
    train_on_real(enc, X, L, Y, fit_w, val_w, steps=STEPS, bs=BATCH,
                  device=DEVICE, seed=sd, verbose=False)
    m = score(enc, X[te_w], L[te_w], Y[te_w], DEVICE)
    base = trivial_baselines(Y[fit_w], Y[te_w])
    return {"top1": m["top1"], "top3": m["top3"], "macro_f1": m["macro_f1"],
            "ppl": m["perplexity"], "majority": base["majority_top1"],
            "n_test": int(len(te_w))}


def agg(recs):
    if not recs:
        return None
    k = ("top1", "top3", "macro_f1", "ppl", "majority")
    out = {x: float(np.mean([r[x] for r in recs])) for x in k}
    out["top1_sd"] = float(np.std([r["top1"] for r in recs]))
    out["n_test"] = int(np.sum([r["n_test"] for r in recs]))
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    seqs, scen, info = load_camlds_verified()
    X, L, Y, S = to_windows(seqs)
    scen = np.array(scen)
    n = len(seqs)

    print("=" * 94)
    print("  CAM-LDS — WHAT THE CORPUS CAN AND CANNOT SUPPORT")
    print("=" * 94)
    print(f"  {info['n_runs']} runs / {info['n_steps']} labelled steps / "
          f"{info['n_scenarios']} campaigns -> {len(Y)} windows")
    print(f"  within-scenario Jaccard 0.871 | across-scenario 0.078 (10.4x)")
    print(f"  uniform-baseline perplexity = {UNIFORM_PPL:.0f}\n")

    results = {}

    # ── P1 leave-one-scenario-out ───────────────────────────────────────────
    print("  P1  LEAVE-ONE-SCENARIO-OUT (test campaign never seen)")
    p1 = {m: [] for m in MODELS}
    for held, tr_seq, te_seq in scenario_loso_folds(scen):
        tr_scen = sorted(set(scen[tr_seq]), key=lambda x: int(x[1:]))
        for name in MODELS:
            for sd in SEEDS:
                v = tr_scen[sd % len(tr_scen)]
                fit = np.array([i for i in tr_seq if scen[i] != v])
                val = np.array([i for i in tr_seq if scen[i] == v])
                r = fit_eval(name, X, L, Y, S, fit, val, te_seq, sd)
                if r:
                    p1[name].append(r)
    results["P1_leave_one_scenario_out"] = {m: agg(p1[m]) for m in MODELS}

    # ── P2 within-scenario variant hold-out ─────────────────────────────────
    print("  P2  WITHIN-SCENARIO VARIANT HOLD-OUT (campaign seen, variant unseen)")
    p2 = {m: [] for m in MODELS}
    p2_by_scen = {}
    counts = {s: int((scen == s).sum()) for s in set(scen)}
    eligible = sorted([s for s, c in counts.items() if c >= 5],
                      key=lambda x: int(x[1:]))
    print(f"      eligible scenarios (>=5 variants): "
          f"{ {s: counts[s] for s in eligible} }")
    for s in eligible:
        idx = np.nonzero(scen == s)[0]
        rng = np.random.default_rng(0)
        perm = rng.permutation(idx)
        folds = np.array_split(perm, 3)
        per = {m: [] for m in MODELS}
        for f in folds:
            te_seq = f
            rest = np.array([i for i in range(n) if i not in set(f.tolist())])
            # validate on a different variant of the SAME scenario
            same = np.array([i for i in rest if scen[i] == s])
            if len(same) < 2:
                continue
            for name in MODELS:
                for sd in SEEDS:
                    val = same[[sd % len(same)]]
                    fit = np.array([i for i in rest if i not in set(val.tolist())])
                    r = fit_eval(name, X, L, Y, S, fit, val, te_seq, sd)
                    if r:
                        p2[name].append(r); per[name].append(r)
        p2_by_scen[s] = {m: agg(per[m]) for m in MODELS}
    results["P2_within_scenario_variant"] = {m: agg(p2[m]) for m in MODELS}
    results["P2_by_scenario"] = p2_by_scen

    # ── P3 run-level random split (leaky, contrast only) ────────────────────
    print("  P3  RUN-LEVEL RANDOM SPLIT (leaky — contrast only)")
    p3 = {m: [] for m in MODELS}
    for sd in SEEDS:
        rng = np.random.default_rng(sd)
        perm = rng.permutation(n)
        a, b = int(0.70 * n), int(0.85 * n)
        fit, val, te = perm[:a], perm[a:b], perm[b:]
        for name in MODELS:
            r = fit_eval(name, X, L, Y, S, fit, val, te, sd)
            if r:
                p3[name].append(r)
    results["P3_run_level_random"] = {m: agg(p3[m]) for m in MODELS}

    # ── report ──────────────────────────────────────────────────────────────
    print("\n" + "=" * 94)
    print("  RESULTS — the bracket is the finding")
    print("=" * 94)
    hdr = ("protocol", "model", "Top-1", "vs maj", "Top-3", "macroF1", "PPL")
    print("  %-26s %-12s %8s %8s %8s %9s %9s" % hdr)
    print("  " + "-" * 86)
    for pk in ("P1_leave_one_scenario_out", "P2_within_scenario_variant",
               "P3_run_level_random"):
        for m in MODELS:
            r = results[pk][m]
            if not r:
                continue
            flag = "" if r["ppl"] < UNIFORM_PPL else "  <- WORSE THAN UNIFORM"
            print("  %-26s %-12s %8.3f %+8.3f %8.3f %9.3f %9.2f%s"
                  % (pk.split("_", 1)[0], m, r["top1"],
                     r["top1"] - r["majority"], r["top3"], r["macro_f1"],
                     r["ppl"], flag))
        print()

    a = results["P2_within_scenario_variant"]["Transformer"]
    b = results["P3_run_level_random"]["Transformer"]
    c = results["P1_leave_one_scenario_out"]["Transformer"]
    print("  MEMORISATION GAP (Transformer): P3 - P2 = %+.3f Top-1"
          % (b["top1"] - a["top1"]))
    print("     -> that much of a run-level-split number is near-duplicate recall.")
    print("  GENERALISATION CLIFF: P2 - P1 = %+.3f Top-1"
          % (a["top1"] - c["top1"]))
    print("     -> that much is lost when the campaign itself is unseen.")

    print("\n  P2 BY SCENARIO (Top-1)")
    print("  %-6s %6s " % ("scen", "n_var") + " ".join("%12s" % m for m in MODELS))
    print("  " + "-" * 56)
    for s in eligible:
        row = p2_by_scen[s]
        print("  %-6s %6d " % (s, counts[s])
              + " ".join("%12.3f" % row[m]["top1"] if row[m] else "%12s" % "-"
                         for m in MODELS))

    os.makedirs(os.path.join(HERE, "results_v2"), exist_ok=True)
    out = os.path.join(HERE, "results_v2", "camlds_protocols.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({"corpus": info, "uniform_ppl": UNIFORM_PPL,
                   "results": results}, fh, indent=1, default=float)
    print(f"\n  wrote -> {os.path.relpath(out, HERE)}")
    print("=" * 94)


if __name__ == "__main__":
    main()
