# -*- coding: utf-8 -*-
"""
TEMARL — the verdict analysis  (EXPLORATORY)
=============================================
STATUS: exploratory. Not part of `prereg_v4.py` (commit 7499d29). It adds no
declared contrast, drops none, and re-scores none. Everything here is reported
alongside the pre-registered result, never in place of it.

It answers the one question the pre-registration could not, because it declared
only trained-arm-vs-trained-arm contrasts:

    **Did any arm learn to use attacker intent at all?**

Two things are computed.

1. EVERY ARM vs A MEMORYLESS FIXED ACTION.
   `baselines_entity.py` evaluates the reference ladder on the same env seed
   stream the trained arms used (`default_rng(1_000_000 + seed)` in both), so
   arm and baseline are PAIRED per seed and a paired t-test is valid. The
   quantity reported is the fraction of available intent headroom each arm
   captures:

       capture = (arm - best_fixed) / (profile_oracle - best_fixed)

   best_fixed uses no history and no intent. profile_oracle is the ceiling for
   ANY history-based policy in this environment (see 2). An arm at 0% has
   learned nothing the history encoder could have told it.

2. WHAT THE CEILING IS MADE OF.
   The per-profile optimal action is constant across techniques, so a perfect
   next-technique model is worth +0.0001 expected payoff over a 3-way profile
   label. The task is classification, not sequence modelling -- which bounds
   what ANY history architecture can win here, independently of point 1.
"""

from __future__ import annotations

import json
import os
import sys

import numpy as np
from scipy import stats

import prereg_v4 as PR

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results_v4")
REGIMES = ("A", "B", "C", "D")


def arm_series(rows, arm, regime):
    hist, obj = arm
    sel = [r for r in rows if r["history_encoder"] == hist
           and r["objective"] == obj]
    sel.sort(key=lambda r: r["seed"])
    return np.array([r["%s_dsr" % regime] for r in sel], float)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    v4 = json.load(open(os.path.join(RESULTS, "entity_v4.json"),
                        encoding="utf-8"))["rows"]
    base = json.load(open(os.path.join(RESULTS, "baselines_entity.json"),
                          encoding="utf-8"))["results"]

    print("=" * 104)
    print("  TEMARL — VERDICT ANALYSIS  (EXPLORATORY; not in prereg_v4 / 7499d29)")
    print("=" * 104)
    print("  Question the pre-registration could not ask: did ANY arm learn to")
    print("  use attacker intent? Arms and baselines share the env seed stream,")
    print("  so every comparison below is PAIRED over the same 10 seeds.")

    print("\n" + "=" * 104)
    print("  THE REFERENCE LADDER  (DSR, mean +- 95%% CI, n=10 x 200 episodes)")
    print("=" * 104)
    print("  %-14s" % "policy" + "".join("%16s" % r for r in REGIMES)
          + "   information used")
    print("  " + "-" * 100)
    INFO = {"null": "none (floor)",
            "random": "none",
            "best_fixed": "none - no history, no intent",
            "profile": "perfect 3-way profile label",
            "transition": "perfect NEXT-TECHNIQUE model",
            "clairvoyant": "the realised technique (unattainable)"}
    for pol in ("null", "random", "best_fixed", "profile", "transition",
                "clairvoyant"):
        cells = "".join("%16s" % ("%.3f+-%.3f" % (base[r][pol]["dsr_mean"],
                                                  base[r][pol]["dsr_ci95"]))
                        for r in REGIMES)
        print("  %-14s%s   %s" % (pol, cells, INFO[pol]))

    seq_gain = {r: base[r]["transition"]["dsr_mean"] - base[r]["profile"]["dsr_mean"]
                for r in REGIMES}
    print("\n  value of a PERFECT next-technique model over a 3-way profile label:")
    print("     " + "   ".join("%s %+.4f" % (r, seq_gain[r]) for r in REGIMES))
    print("     -> sequence modelling buys nothing this environment can pay for.")

    # ── every arm vs best_fixed, paired ─────────────────────────────────────
    print("\n" + "=" * 104)
    print("  DID ANY ARM BEAT A MEMORYLESS FIXED ACTION?  (paired t-test vs "
          "best_fixed, n=10)")
    print("=" * 104)
    print("  %-18s %-8s %-4s %8s %9s %10s %20s %9s %8s"
          % ("history encoder", "objtv", "reg", "arm DSR", "vs fixed",
             "capture", "95% CI on delta", "p", "verdict"))
    print("  " + "-" * 100)
    out = []
    for arm in PR.ARMS:
        for rg in REGIMES:
            a = arm_series(v4, arm, rg)
            b = np.array(base[rg]["best_fixed"]["per_seed_dsr"], float)
            n = min(len(a), len(b))
            a, b = a[:n], b[:n]
            span = (base[rg]["profile"]["dsr_mean"]
                    - base[rg]["best_fixed"]["dsr_mean"])
            diff = a - b
            se = diff.std(ddof=1) / np.sqrt(n)
            t, p = stats.ttest_rel(a, b)
            lo, hi = diff.mean() - 1.96 * se, diff.mean() + 1.96 * se
            cap = 100.0 * diff.mean() / span if abs(span) > 1e-9 else float("nan")
            out.append({"arm": "%s/%s" % arm, "regime": rg,
                        "arm_dsr": float(a.mean()),
                        "best_fixed_dsr": float(b.mean()),
                        "delta": float(diff.mean()),
                        "ci_low": float(lo), "ci_high": float(hi),
                        "headroom_capture_pct": float(cap),
                        "p_raw": float(p), "beats_fixed": bool(p < 0.05
                                                               and diff.mean() > 0)})
            print("  %-18s %-8s %-4s %8.3f %+9.4f %9.1f%% %20s %9.3f %8s"
                  % (arm[0], arm[1], rg, a.mean(), diff.mean(), cap,
                     "[%+.4f, %+.4f]" % (lo, hi), p,
                     "BEATS" if (p < 0.05 and diff.mean() > 0) else "no"))

    n_beat = sum(r["beats_fixed"] for r in out)
    print("\n  arms beating a memoryless fixed action at p<0.05, uncorrected: "
          "%d of %d" % (n_beat, len(out)))
    print("  (uncorrected -- Holm over 24 would only make this stricter)")

    best = max(out, key=lambda r: r["headroom_capture_pct"])
    print("  best single arm/regime: %s in %s, capturing %.1f%% of the "
          "available intent headroom"
          % (best["arm"], best["regime"], best["headroom_capture_pct"]))

    with open(os.path.join(RESULTS, "verdict_v4.json"), "w",
              encoding="utf-8") as f:
        json.dump({"exploratory": True,
                   "not_part_of_prereg": "prereg_v4.py / commit 7499d29",
                   "sequence_gain_over_profile_dsr": seq_gain,
                   "arms_vs_best_fixed": out,
                   "n_arms_beating_fixed": n_beat}, f, indent=1, default=float)
    print("\n  wrote -> results_v4/verdict_v4.json")
    print("=" * 104)


if __name__ == "__main__":
    main()
