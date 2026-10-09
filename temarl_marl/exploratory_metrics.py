# -*- coding: utf-8 -*-
"""
TEMARL v7 — EXPLORATORY analysis (added AFTER the pre-registration; label it so)
===============================================================================
Nothing here is a pre-registered test. It answers two follow-up questions:

  1. The pre-registration tested only the TRANSFORMER against NoHistory (I1)
     and SetEncoder (A3). Do GRU and LSTM also beat them?  Paired t-tests over
     the same 10 seeds, Holm-corrected within this exploratory family.

  2. Candidate COMMON metrics for comparing with published honeypot papers,
     which report engagement in different units (seconds, commands, steps):

       REG  Relative Engagement Gain = (E_method - E_static) / E_static
            E = dwell time; "static" = the best fixed (non-adaptive) decoys,
            the analogue of the static honeypot most papers compare against.
       RDG  Relative Depth Gain, the same for interaction depth.
       PSS  Prediction Skill Score = (Top1 - Top1_majority) / (1 - Top1_majority)
            for the next-technique model; removes the effect of how many
            classes a dataset has (19 in some honeypot papers, 84 here).

    python exploratory_metrics.py
"""

from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from evaluate_marl import aligned, base_seed, holm, load, paired, per_seed  # noqa: E402

FP = "b61f7bcb5c893702"
ARMS = [("Transformer-RoPE", "MAPPO"), ("GRU", "MAPPO"), ("LSTM", "MAPPO"),
        ("SetEncoder", "MAPPO"), ("NoHistory", "MAPPO"), ("Transformer-RoPE", "IPPO")]


def ci(x):
    x = np.asarray(x, float)
    from scipy import stats
    h = stats.t.ppf(0.975, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x))
    return x.mean(), h


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    cells, base = load("main")
    fps = {c["fingerprint"] for c in cells}
    print("=" * 100)
    print("  TEMARL v7 — EXPLORATORY metrics (NOT pre-registered)")
    print("  main-study cells %d | fingerprints %s | pre-registered code: %s"
          % (len(cells), sorted(fps), "YES" if fps == {FP} else "NO"))
    print("=" * 100)

    # 1. GRU / LSTM vs NoHistory and SetEncoder
    print("\n1. Do GRU and LSTM also beat NoHistory and SetEncoder?  (paired over 10 seeds, Holm)")
    rows, ps = [], []
    for enc in ("GRU", "LSTM"):
        for ref in ("NoHistory", "SetEncoder"):
            for m in ("dwell", "depth"):
                a = per_seed(cells, enc, "MAPPO", m)
                b = per_seed(cells, ref, "MAPPO", m)
                st = paired(*aligned(a, b))
                key = "%s-%s-%s" % (enc, ref, m)
                rows.append((key, enc, ref, m, st)); ps.append((key, st["p"]))
    adj = holm(ps)
    print("   %-28s %9s %22s %7s %9s  verdict" % ("contrast", "diff", "95% CI", "d_z", "p_holm"))
    for key, enc, ref, m, st in rows:
        p = adj[key]
        v = "BEATS" if (p < 0.05 and st["mean"] > 0) else ("WORSE" if p < 0.05 else "n.s.")
        print("   %-28s %+9.3f [%+8.3f, %+8.3f] %+7.2f %9.5f  %s"
              % ("%s vs %s (%s)" % (enc, ref, m), st["mean"], st["mean"] - st["ci"],
                 st["mean"] + st["ci"], st["d"], p, v))

    # 2. common metrics
    print("\n2. Candidate common metrics (per-seed values, mean and 95% CI)")
    static_d = base_seed(base, "best_fixed", "dwell")
    static_k = base_seed(base, "best_fixed", "depth")
    print("   static reference = best fixed decoys: dwell %.2f, depth %.2f"
          % (np.mean(list(static_d.values())), np.mean(list(static_k.values()))))
    print("   %-26s %20s %20s %16s" % ("arm", "REG (engagement)", "RDG (depth)", "PSS (prediction)"))
    for arm in ARMS:
        d = per_seed(cells, *arm, "dwell")
        k = per_seed(cells, *arm, "depth")
        reg = [(d[s] - static_d[s]) / static_d[s] for s in sorted(d)]
        rdg = [(k[s] - static_k[s]) / static_k[s] for s in sorted(k)]
        r_m, r_h = ci(reg); g_m, g_h = ci(rdg)
        pre = [c["pretrain"] for c in cells if (c["cell"]["arm"], c["cell"]["learner"]) == arm]
        if pre and "top1" in pre[0]:
            pss = [(p["top1"] - p["majority"]) / (1 - p["majority"]) for p in pre]
            pss_s = "%.3f ± %.3f" % ci(pss)
        else:
            pss_s = "n/a (no model)"
        print("   %-26s %+8.1f%% ± %5.1f%%   %+8.1f%% ± %5.1f%%   %16s"
              % ("%s/%s" % arm, 100 * r_m, 100 * r_h, 100 * g_m, 100 * g_h, pss_s))

    pre = [c["pretrain"] for c in cells if c["cell"]["arm"] == "GRU"]
    print("\n   PSS inputs (GRU, CAM-LDS next technique): Top-1 %.3f, majority %.3f, "
          "bigram lookup %.3f" % (np.mean([p["top1"] for p in pre]),
                                  np.mean([p["majority"] for p in pre]),
                                  np.mean([p["bigram"] for p in pre])))

    # unseen attacks, for honesty
    lcells, lbase = load("loso")
    ls = base_seed(lbase, "best_fixed", "dwell")
    print("\n   On UNSEEN attack scripts (LOSO) — REG vs the best fixed decoys chosen on training scripts:")
    for arm in ARMS[:5]:
        if arm[0] == "LSTM":
            continue
        d = per_seed(lcells, *arm, "dwell")
        reg = [(d[s] - ls[s]) / ls[s] for s in sorted(d)]
        print("   %-26s %+8.1f%% ± %5.1f%%" % ("%s/%s" % arm, *(100 * v for v in ci(reg))))
    print("=" * 100)


if __name__ == "__main__":
    main()
