# -*- coding: utf-8 -*-
"""Analysis for the pre-registered COMISET Lab encoder comparison.

Reports, in this order:
  1. the VALIDITY GATE (every arm vs majority and bigram baselines),
  2. every declared contrast, whatever its outcome,
  3. TOST equivalence at the pre-declared margin, so a null is bounded,
  4. cost (parameters, wall-clock).

Nothing here selects what to report. The contrast list comes from
prereg_comiset.CONTRASTS and all of it is printed.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
from scipy import stats

import prereg_comiset as PR

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results_comiset", "encoders_comiset.json")


def paired(a, b):
    """Paired difference statistics for a - b."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = a - b
    n = len(d)
    mean = float(d.mean())
    sd = float(d.std(ddof=1)) if n > 1 else 0.0
    se = sd / np.sqrt(n) if sd > 0 else 0.0
    t, p = stats.ttest_rel(a, b) if n > 1 and sd > 0 else (0.0, 1.0)
    ci = stats.t.ppf(0.975, n - 1) * se if n > 1 and se > 0 else 0.0
    dz = mean / sd if sd > 0 else 0.0
    return {"mean": mean, "ci": ci, "t": float(t), "p": float(p), "d": dz, "n": n}


def holm(pairs):
    """Holm-Bonferroni. pairs: [(key, p)] -> {key: p_adjusted}"""
    order = sorted(pairs, key=lambda kv: kv[1])
    m = len(order)
    out, prev = {}, 0.0
    for i, (k, p) in enumerate(order):
        adj = min(1.0, max(prev, (m - i) * p))
        out[k] = adj
        prev = adj
    return out


def tost(a, b, margin):
    """Two one-sided tests: is |a-b| bounded below `margin`?"""
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = a - b
    n = len(d)
    sd = d.std(ddof=1)
    if n < 2 or sd == 0:
        return 1.0
    se = sd / np.sqrt(n)
    t1 = (d.mean() + margin) / se
    t2 = (d.mean() - margin) / se
    p1 = 1 - stats.t.cdf(t1, n - 1)
    p2 = stats.t.cdf(t2, n - 1)
    return float(max(p1, p2))


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if not os.path.exists(RES):
        raise SystemExit("no results at %s -- run run_comiset_encoders.py first" % RES)
    blob = json.load(open(RES, encoding="utf-8"))
    R = blob["results"]

    def col(arm, key):
        seeds = sorted(R.get(arm, {}), key=int)
        return [R[arm][s][key] for s in seeds], seeds

    print("=" * 78)
    print("  COMISET LAB ENCODER COMPARISON — pre-registered analysis")
    print("=" * 78)
    print("pre-registration : %s" % blob.get("prereg"))
    print("corpus           : %s (%d sessions, %d windows)"
          % (blob.get("corpus"), blob.get("n_sessions", 0), blob.get("n_windows", 0)))
    print("device           : %s   steps %s   batch %s"
          % (blob.get("device"), blob.get("steps"), blob.get("batch")))

    arms = [a for a in PR.ARMS if a in R and R[a]]
    print("\n--- 1. VALIDITY GATE (reported first) --------------------------------")
    print("  %-18s %8s %8s %8s   %-22s" % ("arm", "top1", "majority", "bigram", "verdict"))
    passing = []
    for arm in arms:
        t1, seeds = col(arm, "top1")
        mj, _ = col(arm, "majority")
        bg, _ = col(arm, "bigram")
        g1 = paired(t1, mj)
        g2 = paired(t1, bg)
        ok = g1["mean"] > 0 and g1["p"] < PR.ALPHA and g2["mean"] > 0 and g2["p"] < PR.ALPHA
        if ok:
            passing.append(arm)
        print("  %-18s %8.4f %8.4f %8.4f   %s (vs maj p=%.4f, vs bigram p=%.4f)"
              % (arm, np.mean(t1), np.mean(mj), np.mean(bg),
                 "PASS" if ok else "FAIL", g1["p"], g2["p"]))
    print("  gate: %d of %d arms pass" % (len(passing), len(arms)))
    if len(passing) < len(arms):
        print("  NOTE: arms failing the gate are excluded from the contrasts below.")

    print("\n--- 2. PRE-REGISTERED CONTRASTS (all reported) ------------------------")
    rows, ps = [], []
    for tag, a, b in PR.CONTRASTS:
        if a not in passing or b not in passing:
            rows.append((tag, a, b, None))
            continue
        ta, _ = col(a, "top1")
        tb, _ = col(b, "top1")
        st = paired(ta, tb)
        rows.append((tag, a, b, st))
        ps.append((tag, st["p"]))
    adj = holm(ps)
    print("  %-4s %-34s %9s %18s %7s %9s" %
          ("", "contrast", "d top1", "95% CI", "d_z", "p_holm"))
    for tag, a, b, st in rows:
        if st is None:
            print("  %-4s %-34s   EXCLUDED (an arm failed the gate)"
                  % (tag, "%s - %s" % (a, b)))
            continue
        print("  %-4s %-34s %+9.4f  [%+.4f, %+.4f] %+7.2f %9.4f"
              % (tag, "%s - %s" % (a, b), st["mean"], st["mean"] - st["ci"],
                 st["mean"] + st["ci"], st["d"], adj.get(tag, 1.0)))
        sig = adj.get(tag, 1.0) < PR.ALPHA
        want = PR.PREDICTED_DIRECTION.get(tag, 0)
        got = 1 if st["mean"] > 0 else -1
        if not sig:
            verdict = "NOT SUPPORTED (no significant difference)"
        elif want == 0:
            verdict = "SIGNIFICANT (no direction was predicted)"
        elif got == want:
            verdict = "SUPPORTED"
        else:
            verdict = ("CONTRADICTED — significant in the OPPOSITE direction "
                       "to the hypothesis")
        print("       -> %s" % verdict)

    print("\n--- 3. EQUIVALENCE (TOST, margin %.3f top-1) --------------------------"
          % PR.EQUIV_MARGIN)
    for tag, a, b, st in rows:
        if st is None:
            continue
        ta, _ = col(a, "top1")
        tb, _ = col(b, "top1")
        p = tost(ta, tb, PR.EQUIV_MARGIN)
        print("  %-4s %-34s p_tost %.4f  %s"
              % (tag, "%s - %s" % (a, b), p,
                 "EQUIVALENT within margin" if p < PR.ALPHA else "not shown equivalent"))

    print("\n--- 4. COST AND SECONDARY METRICS -------------------------------------")
    print("  %-18s %8s %8s %9s %11s %9s" %
          ("arm", "top1", "top3", "macro_f1", "perplexity", "params"))
    for arm in arms:
        t1, _ = col(arm, "top1")
        t3, _ = col(arm, "top3")
        f1, _ = col(arm, "macro_f1")
        pp, _ = col(arm, "perplexity")
        pr, _ = col(arm, "params")
        sc, _ = col(arm, "seconds")
        print("  %-18s %8.4f %8.4f %9.4f %11.3f %9d  (%.0fs/seed)"
              % (arm, np.mean(t1), np.mean(t3), np.mean(f1), np.mean(pp),
                 int(np.mean(pr)), np.mean(sc)))


if __name__ == "__main__":
    main()
