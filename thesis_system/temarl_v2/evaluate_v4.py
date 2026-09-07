# -*- coding: utf-8 -*-
"""
TEMARL v4 — Pre-registered analysis of the final experiment
============================================================
Consumes `results_v4/entity_v4.json` and evaluates EXACTLY the contrast family
declared in `prereg_v4.CONTRAST_FAMILY` (committed as 7499d29 before the run).
No contrast is added, dropped, or re-scoped after the fact; every declared
contrast is reported whatever its outcome.

Reports, for every contrast: mean of each arm, paired delta, Cohen's d, raw and
Holm-corrected p, and a **95% confidence interval**. The CI is not decoration:
at n = 10 a paired t-test only detects d >= 1.00, so a bound on the effect is
what carries the argument, not the p-value.

Also reports the v3 -> v4 comparison, which is the point of the whole exercise:
how much of the previously reported Transformer deficit was our own artefact.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
from scipy import stats

import prereg_v4 as PR
from evaluate_v2 import cohens_d, holm_bonferroni

HERE = os.path.dirname(os.path.abspath(__file__))
REGIME_ORDER = ("A", "B", "C", "D")


def series(rows, arm, regime, metric):
    """Per-seed values for one arm, sorted by seed so pairing lines up."""
    hist, obj = arm
    sel = [r for r in rows
           if r["history_encoder"] == hist and r["objective"] == obj]
    sel.sort(key=lambda r: r["seed"])
    return np.array([r["%s_%s" % (regime, metric)] for r in sel], dtype=float)


def ci95(x):
    x = np.asarray(x, dtype=float)
    if len(x) < 2:
        return (float(x.mean()) if len(x) else float("nan")), 0.0
    return float(x.mean()), float(1.96 * x.std(ddof=1) / np.sqrt(len(x)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results",
                    default=os.path.join(HERE, "results_v4", "entity_v4.json"))
    ap.add_argument("--out",
                    default=os.path.join(HERE, "results_v4", "analysis_v4.json"))
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    with open(args.results, encoding="utf-8") as f:
        data = json.load(f)
    rows = data["rows"]
    seeds = sorted({r["seed"] for r in rows})
    complete = data.get("complete", False)

    print("=" * 104)
    print("  TEMARL v4 — PRE-REGISTERED ANALYSIS  (prereg commit %s)"
          % data.get("prereg_commit", "?"))
    print("=" * 104)
    print("  %d runs | %d arms x %d seeds | primary metric = %s | %s"
          % (len(rows), len(PR.ARMS), len(seeds), PR.PRIMARY_METRIC,
             "COMPLETE" if complete else "PARTIAL - interim only"))
    if not complete:
        print("  [!] The experiment has not finished. Numbers below are interim "
              "and are NOT the pre-registered result.")
    print("  %s" % PR.CORRECTION)

    # ── per-arm DSR table ───────────────────────────────────────────────────
    print("\n" + "=" * 104)
    print("  %s BY ARM AND REGIME  (mean +- 95%% CI over %d seeds)"
          % (PR.PRIMARY_METRIC.upper(), len(seeds)))
    print("=" * 104)
    print("  %-18s %-8s" % ("history encoder", "objtv")
          + "".join("%20s" % ("%s: %s" % (r, PR.REGIME_DESC[r][:12]))
                    for r in REGIME_ORDER))
    print("  " + "-" * 100)
    summary = {}
    for arm in PR.ARMS:
        cells, means = [], {}
        for rg in REGIME_ORDER:
            s = series(rows, arm, rg, PR.PRIMARY_METRIC)
            if len(s) == 0:
                cells.append("%20s" % "-")
                continue
            m, h = ci95(s)
            means[rg] = m
            cells.append("%20s" % ("%.3f+-%.3f" % (m, h)))
        summary["%s/%s" % arm] = {"means": means, "n": len(seeds)}
        print("  %-18s %-8s" % (arm[0], arm[1]) + "".join(cells))

    # ── mechanism metric ────────────────────────────────────────────────────
    print("\n  MECHANISM (%s, regime B) — explains HOW a DSR difference arises"
          % PR.MECHANISM_METRIC)
    print("  %-18s %-8s %18s %14s %12s" % ("history encoder", "objtv",
                                           PR.MECHANISM_METRIC, "hist params",
                                           "train s"))
    print("  " + "-" * 78)
    for arm in PR.ARMS:
        s = series(rows, arm, "B", PR.MECHANISM_METRIC)
        if len(s) == 0:
            continue
        m, h = ci95(s)
        sel = [r for r in rows if r["history_encoder"] == arm[0]
               and r["objective"] == arm[1]]
        print("  %-18s %-8s %18s %14d %12.0f"
              % (arm[0], arm[1], "%.3f+-%.3f" % (m, h),
                 int(np.mean([r["n_params_hist"] for r in sel])),
                 float(np.mean([r["train_seconds"] for r in sel]))))

    # ── declared contrast family ────────────────────────────────────────────
    recs, pvals = [], []
    for label, arm_a, arm_b, regime in PR.CONTRAST_FAMILY:
        a = series(rows, tuple(arm_a), regime, PR.PRIMARY_METRIC)
        b = series(rows, tuple(arm_b), regime, PR.PRIMARY_METRIC)
        n = min(len(a), len(b))
        a, b = a[:n], b[:n]
        if n < 2 or np.allclose(a, b):
            t, p, d = 0.0, 1.0, 0.0
            lo = hi = 0.0
        else:
            t, p = stats.ttest_rel(a, b)
            if not np.isfinite(p):
                t, p = 0.0, 1.0
            d = cohens_d(a, b)
            diff = a - b
            se = diff.std(ddof=1) / np.sqrt(n)
            lo, hi = diff.mean() - 1.96 * se, diff.mean() + 1.96 * se
        recs.append({"label": label, "arm_a": list(arm_a), "arm_b": list(arm_b),
                     "regime": regime, "n_pairs": int(n),
                     "mean_a": float(a.mean()) if n else float("nan"),
                     "mean_b": float(b.mean()) if n else float("nan"),
                     "delta": float((a - b).mean()) if n else float("nan"),
                     "ci_low": float(lo), "ci_high": float(hi),
                     "t": float(t), "p_raw": float(p), "cohens_d": float(d)})
        pvals.append(p)
    holm = holm_bonferroni(pvals)

    print("\n" + "=" * 104)
    print("  DECLARED CONTRAST FAMILY  (paired t-test, Holm-Bonferroni, "
          "alpha=%.2f, n=%d)" % (PR.ALPHA, len(seeds)))
    print("=" * 104)
    print("  %-9s %-4s %8s %8s %9s %20s %7s %10s   %s"
          % ("contrast", "reg", "mean A", "mean B", "delta", "95% CI on delta",
             "d", "p_holm", "verdict"))
    print("  " + "-" * 100)
    for r, h in zip(recs, holm):
        r["p_holm"] = h["p_holm"]
        r["significant"] = h["significant"]
        print("  %-9s %-4s %8.3f %8.3f %+9.4f %20s %+7.2f %10.2e   %s"
              % (r["label"], r["regime"], r["mean_a"], r["mean_b"], r["delta"],
                 "[%+.4f, %+.4f]" % (r["ci_low"], r["ci_high"]),
                 r["cohens_d"], h["p_holm"],
                 "SIGNIFICANT" if h["significant"] else "not significant"))

    # ── hypothesis verdicts ─────────────────────────────────────────────────
    print("\n" + "=" * 104)
    print("  HYPOTHESIS VERDICTS")
    print("=" * 104)
    verdicts = {}
    for hkey, desc, _m in PR.HYPOTHESES:
        rel = [r for r in recs if r["label"].startswith(hkey + "-")]
        pro = [r for r in rel if r["significant"] and r["delta"] > 0]
        con = [r for r in rel if r["significant"] and r["delta"] < 0]
        if pro and not con:
            v = "SUPPORTED"
        elif con and not pro:
            v = "CONTRADICTED (significant in the OPPOSITE direction)"
        elif pro and con:
            v = "MIXED"
        else:
            v = "NOT SUPPORTED (no significant contrast)"
        verdicts[hkey] = {"verdict": v, "description": desc,
                          "contrasts": [r["label"] for r in rel]}
        print("  %s: %s" % (hkey, v))
        print("      %s" % desc)
        for r in rel:
            print("        %-9s delta=%+.4f  CI [%+.4f, %+.4f]  d=%+.2f  "
                  "p_holm=%.2e"
                  % (r["label"], r["delta"], r["ci_low"], r["ci_high"],
                     r["cohens_d"], r["p_holm"]))

    # ── what changed vs v3 ──────────────────────────────────────────────────
    print("\n" + "=" * 104)
    print("  WHAT THE ARTEFACT CORRECTION BOUGHT (v4 vs the v3 configuration)")
    print("=" * 104)
    try:
        v3p = os.path.join(HERE, "results_v3", "entity_results_gpu.json")
        v3 = json.load(open(v3p, encoding="utf-8"))["rows"]
        g3 = [r for r in v3 if r["history_encoder"] == "GRU"
              and r["network_encoder"] == "DeepSets"]
        t3 = [r for r in v3 if r["history_encoder"] == "Transformer"
              and r["network_encoder"] == "DeepSets"]
        d3 = np.mean([r["B_dsr"] for r in t3]) - np.mean([r["B_dsr"] for r in g3])
        a4 = series(rows, ("Transformer-RoPE", "action"), "B", "dsr")
        b4 = series(rows, ("GRU", "action"), "B", "dsr")
        d4 = float((a4 - b4).mean()) if len(a4) and len(b4) else float("nan")
        print("  v3 (sinusoidal PE, next objective, L=16, untuned):"
              "  Transformer - GRU on DSR-B = %+.4f" % d3)
        print("  v4 (rotary PE, action objective, L=8, tuned)      :"
              "  Transformer - GRU on DSR-B = %+.4f" % d4)
        print("  shift attributable to artefact correction         : %+.4f"
              % (d4 - d3))
    except Exception as e:
        print("  [skip] %s" % str(e)[:90])

    out = {"prereg_commit": data.get("prereg_commit"),
           "complete": complete, "n_seeds": len(seeds),
           "summary": summary, "contrasts": recs, "verdicts": verdicts,
           "prereg": {"hypotheses": PR.HYPOTHESES,
                      "contrast_family": PR.CONTRAST_FAMILY,
                      "correction": PR.CORRECTION,
                      "declaration": PR.DECLARATION}}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, default=float)
    print("\n  wrote -> %s" % os.path.relpath(args.out, HERE))
    print("=" * 104)


if __name__ == "__main__":
    main()
