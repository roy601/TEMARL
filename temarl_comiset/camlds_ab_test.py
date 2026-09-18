# -*- coding: utf-8 -*-
"""
TEMARL v2 — CAM-LDS Model A vs Model B: paired significance test
=================================================================
camlds_protocols.py reported that on CAM-LDS the GRU beats the Transformer by a
wide margin under protocol P2 (0.633 vs 0.493 Top-1). That is a claim about the
thesis's central premise -- "Transformer-Enhanced" -- so it must not rest on a
difference of means. This script re-runs P2 with the comparison PAIRED and
tested, at the same standard as the simulator side of the thesis.

DESIGN
------
Protocol P2 (within-scenario variant hold-out) over the three scenarios with
enough variants: S1 (18), S3 (8), S6 (5). For every (scenario, fold, seed)
triple all three encoders are trained on IDENTICAL data with an IDENTICAL seed,
so each triple yields one matched observation per model and the models can be
compared pairwise rather than across independent runs.

  3 scenarios x 3 folds x SEEDS  =>  matched observations per model

Paired t-tests over the three pairwise contrasts, Holm-Bonferroni corrected at
alpha = 0.05, with Cohen's d for the paired differences.

PRE-REGISTERED HERE, BEFORE THE RUN
-----------------------------------
  primary metric : Top-1 next-technique accuracy on the held-out variants
  contrasts      : (GRU vs Transformer), (SetEncoder vs Transformer),
                   (GRU vs SetEncoder)
  correction     : Holm-Bonferroni over exactly those 3, alpha = 0.05
No metric or contrast may be added after seeing the numbers.
"""

import json
import os
import sys

import numpy as np
from scipy import stats

from data_real import load_camlds_verified, to_windows, trivial_baselines
from encoders import build_matched_suite
from evaluate_v2 import cohens_d, holm_bonferroni
from train_real import DEVICE, score, train_on_real

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = ("Transformer", "GRU", "SetEncoder")
SEEDS = (0, 1, 2, 3, 4)
STEPS = 600
BATCH = 64
CONTRASTS = [("GRU", "Transformer"), ("SetEncoder", "Transformer"),
             ("GRU", "SetEncoder")]


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("=" * 92)
    print("  CAM-LDS — MODEL A vs MODEL B, PAIRED  (protocol P2)")
    print("=" * 92)

    seqs, scen, info = load_camlds_verified()
    X, L, Y, S = to_windows(seqs)
    scen = np.array(scen)
    n = len(seqs)
    counts = {s: int((scen == s).sum()) for s in set(scen)}
    eligible = sorted([s for s, c in counts.items() if c >= 5],
                      key=lambda x: int(x[1:]))
    print(f"  scenarios with >=5 variants: {[(s, counts[s]) for s in eligible]}")
    print(f"  {len(eligible)} scenarios x 3 folds x {len(SEEDS)} seeds "
          f"= {len(eligible) * 3 * len(SEEDS)} matched observations per model\n")

    obs = {m: [] for m in MODELS}
    labels = []
    for s in eligible:
        idx = np.nonzero(scen == s)[0]
        folds = np.array_split(np.random.default_rng(0).permutation(idx), 3)
        for fi, f in enumerate(folds):
            te_seq = f
            rest = np.array([i for i in range(n) if i not in set(f.tolist())])
            same = np.array([i for i in rest if scen[i] == s])
            if len(same) < 2:
                continue
            for sd in SEEDS:
                val = same[[sd % len(same)]]
                fit = np.array([i for i in rest if i not in set(val.tolist())])
                fit_w = np.nonzero(np.isin(S, fit))[0]
                val_w = np.nonzero(np.isin(S, val))[0]
                te_w = np.nonzero(np.isin(S, te_seq))[0]
                if not (len(fit_w) and len(val_w) and len(te_w)):
                    continue
                labels.append((s, fi, sd))
                for name in MODELS:
                    suite, _, _ = build_matched_suite()
                    enc = suite[name].to(DEVICE)
                    train_on_real(enc, X, L, Y, fit_w, val_w, steps=STEPS,
                                  bs=BATCH, device=DEVICE, seed=sd, verbose=False)
                    m = score(enc, X[te_w], L[te_w], Y[te_w], DEVICE)
                    obs[name].append(m["top1"])
            print(f"    {s} fold {fi + 1}/3 done "
                  f"({len(obs['Transformer'])} obs so far)")

    arr = {m: np.array(obs[m]) for m in MODELS}
    N = len(arr["Transformer"])
    print(f"\n  matched observations: {N}\n")
    print(f"  {'model':<13} {'Top-1 mean':>11} {'sd':>8} {'min':>8} {'max':>8}")
    print("  " + "-" * 52)
    for m in MODELS:
        a = arr[m]
        print(f"  {m:<13} {a.mean():>11.3f} {a.std(ddof=1):>8.3f} "
              f"{a.min():>8.3f} {a.max():>8.3f}")

    # Persist the raw observations BEFORE computing statistics: the training
    # above costs ~12 minutes and must not be lost to a downstream error.
    out = os.path.join(HERE, "results_v2", "camlds_ab_test.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    payload = {"protocol": "P2 within-scenario variant hold-out, paired",
               "n_matched": N, "labels": labels,
               "means": {m: float(arr[m].mean()) for m in MODELS},
               "raw": {m: arr[m].tolist() for m in MODELS}}
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1, default=float)

    pvals, rec = [], []
    for a, b in CONTRASTS:
        d = arr[a] - arr[b]
        t, p = stats.ttest_rel(arr[a], arr[b])
        rec.append({"contrast": f"{a} - {b}", "delta": float(d.mean()),
                    "t": float(t), "p_raw": float(p),
                    "cohens_d": float(cohens_d(arr[a], arr[b]))})
        pvals.append(p)
    holm = holm_bonferroni(pvals)   # returns a list of per-contrast dicts

    print("\n" + "=" * 92)
    print(f"  PAIRED CONTRASTS — Holm-Bonferroni, alpha=0.05, N={N} matched pairs")
    print("=" * 92)
    print(f"  {'contrast':<26} {'delta Top-1':>12} {'d':>8} {'p_raw':>10} "
          f"{'p_holm':>10}   verdict")
    print("  " + "-" * 86)
    for r, h in zip(rec, holm):
        r["p_holm"] = h["p_holm"]
        r["significant"] = h["significant"]
        print(f"  {r['contrast']:<26} {r['delta']:>+12.4f} {r['cohens_d']:>8.2f} "
              f"{r['p_raw']:>10.2e} {h['p_holm']:>10.2e}   "
              f"{'SIGNIFICANT' if h['significant'] else 'not significant'}")

    payload["contrasts"] = rec
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1, default=float)
    print(f"\n  wrote -> {os.path.relpath(out, HERE)}")
    print("=" * 92)


if __name__ == "__main__":
    main()
