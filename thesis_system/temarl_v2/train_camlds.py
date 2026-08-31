# -*- coding: utf-8 -*-
"""
TEMARL v2 — CAM-LDS encoder training (leave-one-scenario-out)
=============================================================
Trains Model A (Transformer) / Model B (GRU) / Model C (SetEncoder) on the
SOURCE-VERIFIED CAM-LDS corpus, supplying the CAM-LDS column of the mandated
2x2 {Model A, Model B} x {CAM-LDS, COMISET} comparison.

WHY LEAVE-ONE-SCENARIO-OUT, AND NOT session_split()
---------------------------------------------------
CAM-LDS is 36 runs but only 7 independent campaigns. Scenario 1 alone supplies
18 of the 36 runs, and its variants share a mean pairwise Jaccard of 0.871
against 0.078 across scenarios -- a 10.4x ratio. A run-level split therefore
puts near-duplicates of the test campaign into training and reports
memorisation as generalisation. Holding out a WHOLE scenario is the only
protocol under which a held-out number means "generalises to an unseen
campaign". The cost is honest and severe: the S1 fold trains on 18 runs and
tests on 18, and three folds (S4, S5, S7) have a single test run each, so
per-fold variance is large and MUST be reported rather than averaged away.

SCALE DISCLOSURE (must appear in the thesis)
--------------------------------------------
CAM-LDS  1,339 labelled technique instances / 36 runs / 7 campaigns
COMISET  1,547,359 steps / 5,637 sessions          -> a 1156:1 ratio.
The two columns of the 2x2 are therefore NOT a like-for-like comparison of
dataset difficulty; they are two different regimes. Reporting them side by side
without this ratio would be misleading.

WHY CAM-LDS IS NONETHELESS THE BETTER TEST
------------------------------------------
              self-loop rate    majority baseline
  CAM-LDS         18.6%              0.108
  COMISET         98.5%              0.375
COMISET's headline accuracy is substantially "repeat the previous technique".
CAM-LDS cannot be gamed that way, so it measures what the thesis claims.
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
STEPS = 600          # small corpus: ~1k train windows, bs 64 => ~38 epochs
BATCH = 64


def val_from_train(scen, tr_idx, seed):
    """Hold out ONE training scenario as validation (model selection only).
    Selecting on a scenario the model never trains on keeps early stopping from
    quietly fitting the training campaigns."""
    tr_scen = sorted({scen[i] for i in tr_idx}, key=lambda x: int(x[1:]))
    v = tr_scen[seed % len(tr_scen)]
    fit = np.array([i for i in tr_idx if scen[i] != v])
    val = np.array([i for i in tr_idx if scen[i] == v])
    return fit, val, v


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("=" * 92)
    print("  TEMARL v2 — CAM-LDS ENCODER TRAINING (leave-one-scenario-out)")
    print("=" * 92)

    seqs, scen, info = load_camlds_verified()
    X, L, Y, S = to_windows(seqs)
    print(f"  corpus: {info['n_runs']} runs / {info['n_steps']} labelled steps / "
          f"{info['n_scenarios']} campaigns  ->  {len(Y)} next-technique windows")
    print(f"  SCALE: COMISET is 1,547,359 steps — a 1156:1 ratio over CAM-LDS.\n")

    rows = []
    for held, tr_seq, te_seq in scenario_loso_folds(scen):
        tr_w = np.nonzero(np.isin(S, tr_seq))[0]
        te_w = np.nonzero(np.isin(S, te_seq))[0]
        base = trivial_baselines(Y[tr_w], Y[te_w])
        maj = base["majority_top1"]
        print(f"  --- fold: hold out {held}  "
              f"(train {len(tr_seq)} runs/{len(tr_w)} win | "
              f"test {len(te_seq)} runs/{len(te_w)} win)  "
              f"majority={maj:.3f} ---")
        for name in MODELS:
            accs = []
            for sd in SEEDS:
                fit_seq, val_seq, _ = val_from_train(scen, tr_seq, sd)
                fit_w = np.nonzero(np.isin(S, fit_seq))[0]
                val_w = np.nonzero(np.isin(S, val_seq))[0]
                suite, _, _ = build_matched_suite()
                enc = suite[name].to(DEVICE)
                train_on_real(enc, X, L, Y, fit_w, val_w, steps=STEPS,
                              bs=BATCH, device=DEVICE, seed=sd, verbose=False)
                m = score(enc, X[te_w], L[te_w], Y[te_w], DEVICE)
                accs.append((m["top1"], m["top3"], m["macro_f1"], m["perplexity"]))
            a = np.array(accs)
            t1, sd1 = a[:, 0].mean(), a[:, 0].std()
            rows.append({"fold": held, "model": name,
                         "n_test_windows": int(len(te_w)), "majority": maj,
                         "top1": float(t1), "top1_sd": float(sd1),
                         "top3": float(a[:, 1].mean()),
                         "macro_f1": float(a[:, 2].mean()),
                         "ppl": float(a[:, 3].mean())})
            print(f"      {name:<12} top1={t1:.3f}+-{sd1:.3f} "
                  f"top3={a[:, 1].mean():.3f} macroF1={a[:, 2].mean():.3f} "
                  f"ppl={a[:, 3].mean():.2f}  vs maj {t1 - maj:+.3f}")
        print()

    print("=" * 92)
    print("  CAM-LDS LEAVE-ONE-SCENARIO-OUT SUMMARY  (mean over 7 folds x 3 seeds)")
    print("=" * 92)
    print(f"  {'model':<13} {'Top-1':>16} {'vs majority':>13} {'Top-3':>8} "
          f"{'macroF1':>9} {'PPL':>8}")
    print("  " + "-" * 76)
    summary = {}
    for name in MODELS:
        r = [x for x in rows if x["model"] == name]
        t1 = np.array([x["top1"] for x in r])
        mj = np.array([x["majority"] for x in r])
        summary[name] = {
            "top1_mean": float(t1.mean()),
            "top1_sd_across_folds": float(t1.std()),
            "delta_majority": float((t1 - mj).mean()),
            "top3": float(np.mean([x["top3"] for x in r])),
            "macro_f1": float(np.mean([x["macro_f1"] for x in r])),
            "ppl": float(np.mean([x["ppl"] for x in r])),
            "per_fold": {x["fold"]: {"top1": x["top1"], "majority": x["majority"],
                                     "n_test_windows": x["n_test_windows"]}
                         for x in r},
        }
        s = summary[name]
        print(f"  {name:<13} {s['top1_mean']:>8.3f} +-{s['top1_sd_across_folds']:<5.3f} "
              f"{s['delta_majority']:>+13.3f} {s['top3']:>8.3f} "
              f"{s['macro_f1']:>9.3f} {s['ppl']:>8.2f}")
    print(f"  {'[majority]':<13} {np.mean([x['majority'] for x in rows]):>8.3f} "
          f"{'':<5}  {'--':>13} {'--':>8} {'--':>9} "
          f"{float(NUM_TECHNIQUES + 2):>8.1f}")

    print("\n  PER-FOLD Top-1 (the spread is the result, not noise to average away)")
    print(f"  {'fold':<6} {'n_win':>6} {'major':>7} "
          + " ".join(f"{m:>12}" for m in MODELS))
    print("  " + "-" * 62)
    for held in sorted({x["fold"] for x in rows}, key=lambda x: int(x[1:])):
        f = {x["model"]: x for x in rows if x["fold"] == held}
        any_ = next(iter(f.values()))
        print(f"  {held:<6} {any_['n_test_windows']:>6} {any_['majority']:>7.3f} "
              + " ".join(f"{f[m]['top1']:>12.3f}" for m in MODELS))

    os.makedirs(os.path.join(HERE, "results_v2"), exist_ok=True)
    out = os.path.join(HERE, "results_v2", "camlds_loso.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({"protocol": "leave-one-scenario-out, 7 folds x 3 seeds",
                   "corpus": info, "summary": summary, "rows": rows}, fh,
                  indent=1, default=float)
    print(f"\n  wrote -> {os.path.relpath(out, HERE)}")
    print("=" * 92)


if __name__ == "__main__":
    main()
