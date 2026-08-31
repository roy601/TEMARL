# -*- coding: utf-8 -*-
"""
TEMARL v3 — Pre-registered statistical analysis
================================================
Consumes `results_v3/entity_results.json` and evaluates EXACTLY the contrast
family declared in `prereg_v3.CONTRAST_FAMILY`. No contrast is added, dropped, or
re-scoped after the fact; every declared contrast is reported whatever its
outcome.

Pairing: every arm was trained and evaluated on the IDENTICAL topology sets with
matched model seeds, so the correct instrument is a paired t-test over per-seed
values, Holm-Bonferroni corrected across the declared family.

Reports DSR, alignment, episode return, engagement length, capture rate,
generalisation gap, parameter counts, training time, 95% CIs, corrected p-values
and paired Cohen's d.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Dict, List, Sequence

import numpy as np
from scipy import stats

import prereg_v3 as PR
from evaluate_v2 import cohens_d, holm_bonferroni

HERE = os.path.dirname(os.path.abspath(__file__))
REGIMES = ("A", "B", "C", "D")
REGIME_LABEL = {"A": "A: canonical 5-zone (control)",
                "B": "B: new topologies, TRAINED sizes",
                "C": "C: unseen structure",
                "D": "D: unseen sizes (9/11/13)"}
METRICS = ("dsr", "alignment", "episode_return", "engagement_length",
           "capture_rate")


def ci95(x: Sequence[float]):
    x = np.asarray(x, dtype=float)
    if len(x) < 2:
        return float(x.mean()) if len(x) else float("nan"), 0.0
    return float(x.mean()), float(1.96 * x.std(ddof=1) / np.sqrt(len(x)))


def series(rows, arm, regime, metric) -> np.ndarray:
    """Per-seed values for one arm, sorted by seed so pairing is aligned."""
    net, hist = arm
    sel = [r for r in rows
           if r["network_encoder"] == net and r["history_encoder"] == hist]
    sel.sort(key=lambda r: r["seed"])
    return np.array([r[f"{regime}_{metric}"] for r in sel], dtype=float)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results",
                    default=os.path.join(HERE, "results_v3", "entity_results.json"))
    ap.add_argument("--out",
                    default=os.path.join(HERE, "results_v3", "entity_analysis.json"))
    args = ap.parse_args()
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    with open(args.results, encoding="utf-8") as f:
        data = json.load(f)
    rows = data["rows"]
    seeds = sorted({r["seed"] for r in rows})

    print("=" * 100)
    print("  TEMARL v3 — PRE-REGISTERED ANALYSIS")
    print("=" * 100)
    print(f"  {len(rows)} runs | {len(PR.ARMS)} arms x {len(seeds)} seeds | "
          f"primary metric = {PR.PRIMARY_METRIC}")
    print(f"  {PR.CORRECTION}")

    # ── per-arm table, all regimes, primary metric ─────────────────────────
    print("\n" + "=" * 100)
    print(f"  {PR.PRIMARY_METRIC.upper()} BY ARM AND REGIME  (mean +- 95% CI over "
          f"{len(seeds)} seeds)")
    print("=" * 100)
    print(f"  {'network':<19}{'history':<13}" + "".join(f"{r:>19}" for r in REGIMES)
          + f"{'gen gap B-D':>14}")
    print("  " + "-" * 96)
    summary = {}
    for arm in PR.ARMS:
        cells, means = [], {}
        for rg in REGIMES:
            m, h = ci95(series(rows, arm, rg, PR.PRIMARY_METRIC))
            means[rg] = m
            cells.append(f"{m:.3f}+-{h:.3f}")
        gap = means["B"] - means["D"]
        key = f"{arm[0]}+{arm[1]}"
        summary[key] = {"means": means, "gen_gap_B_minus_D": gap}
        print(f"  {arm[0]:<19}{arm[1]:<13}" + "".join(f"{c:>19}" for c in cells)
              + f"{gap:>+14.3f}")

    # ── secondary metrics ──────────────────────────────────────────────────
    print("\n" + "=" * 100)
    print("  SECONDARY METRICS (regime B, mean over seeds)")
    print("=" * 100)
    print(f"  {'network':<19}{'history':<13}"
          + "".join(f"{m:>20}" for m in METRICS[1:])
          + f"{'params':>11}{'train s':>10}")
    print("  " + "-" * 96)
    for arm in PR.ARMS:
        vals = []
        for m in METRICS[1:]:
            mu, h = ci95(series(rows, arm, "B", m))
            vals.append(f"{mu:.3f}+-{h:.3f}")
        net, hist = arm
        sel = [r for r in rows if r["network_encoder"] == net
               and r["history_encoder"] == hist]
        npar = int(np.mean([r["n_params"] for r in sel]))
        tsec = float(np.mean([r["train_seconds"] for r in sel]))
        summary[f"{net}+{hist}"]["n_params"] = npar
        summary[f"{net}+{hist}"]["train_seconds"] = tsec
        print(f"  {net:<19}{hist:<13}" + "".join(f"{v:>20}" for v in vals)
              + f"{npar:>11,}{tsec:>10.0f}")

    # ── the declared contrast family ───────────────────────────────────────
    recs, pvals = [], []
    for label, arm_a, arm_b, regime in PR.CONTRAST_FAMILY:
        a = series(rows, tuple(arm_a), regime, PR.PRIMARY_METRIC)
        b = series(rows, tuple(arm_b), regime, PR.PRIMARY_METRIC)
        n = min(len(a), len(b))
        a, b = a[:n], b[:n]
        if n < 2 or np.allclose(a, b):
            t, p = 0.0, 1.0
        else:
            t, p = stats.ttest_rel(a, b)
            if not np.isfinite(p):
                t, p = 0.0, 1.0
        recs.append({"label": label, "arm_a": list(arm_a), "arm_b": list(arm_b),
                     "regime": regime, "n_pairs": int(n),
                     "mean_a": float(a.mean()), "mean_b": float(b.mean()),
                     "delta": float((a - b).mean()), "t": float(t),
                     "p_raw": float(p),
                     "cohens_d": float(cohens_d(a, b)) if n > 1 else 0.0})
        pvals.append(p)
    holm = holm_bonferroni(pvals)

    print("\n" + "=" * 100)
    print(f"  DECLARED CONTRAST FAMILY  (paired t-test, Holm-Bonferroni, "
          f"alpha={PR.ALPHA})")
    print("=" * 100)
    print(f"  {'contrast':<17}{'reg':<5}{'mean A':>9}{'mean B':>9}{'delta':>9}"
          f"{'d':>8}{'p_raw':>10}{'p_holm':>10}   verdict")
    print("  " + "-" * 96)
    for r, h in zip(recs, holm):
        r["p_holm"] = h["p_holm"]
        r["significant"] = h["significant"]
        print(f"  {r['label']:<17}{r['regime']:<5}{r['mean_a']:>9.3f}"
              f"{r['mean_b']:>9.3f}{r['delta']:>+9.3f}{r['cohens_d']:>8.2f}"
              f"{r['p_raw']:>10.2e}{h['p_holm']:>10.2e}   "
              f"{'SIGNIFICANT' if h['significant'] else 'not significant'}")

    # ── hypothesis verdicts ────────────────────────────────────────────────
    print("\n" + "=" * 100)
    print("  HYPOTHESIS VERDICTS")
    print("=" * 100)
    verdicts = {}
    for hkey, desc, _m in PR.HYPOTHESES:
        rel = [r for r in recs if r["label"].startswith(hkey)]
        sig_for = [r for r in rel if r["significant"] and r["delta"] > 0]
        sig_against = [r for r in rel if r["significant"] and r["delta"] < 0]
        if sig_for and not sig_against:
            v = "SUPPORTED"
        elif sig_against and not sig_for:
            v = "CONTRADICTED (effect is significant in the OPPOSITE direction)"
        elif sig_for and sig_against:
            v = "MIXED"
        else:
            v = "NOT SUPPORTED (no significant contrast)"
        verdicts[hkey] = {"verdict": v, "description": desc,
                          "contrasts": [r["label"] for r in rel]}
        print(f"  {hkey}: {v}")
        print(f"      {desc}")
        for r in rel:
            print(f"        {r['label']:<16} delta={r['delta']:+.3f} "
                  f"d={r['cohens_d']:+.2f} p_holm={r['p_holm']:.2e}")

    out = {"prereg": {"hypotheses": PR.HYPOTHESES,
                      "contrast_family": PR.CONTRAST_FAMILY,
                      "correction": PR.CORRECTION,
                      "declaration": PR.DECLARATION},
           "n_seeds": len(seeds), "summary": summary,
           "contrasts": recs, "verdicts": verdicts}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, default=float)
    print(f"\n  wrote -> {os.path.relpath(args.out, HERE)}")
    print("=" * 100)


if __name__ == "__main__":
    main()
