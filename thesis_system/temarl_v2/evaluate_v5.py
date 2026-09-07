# -*- coding: utf-8 -*-
"""
TEMARL v5 — pre-registered analysis
====================================
Consumes `results_v5/entity_v5.json` and evaluates EXACTLY the contrast family
declared in `prereg_v5.CONTRAST_FAMILY`, committed before the run. No contrast
is added, dropped or re-scoped after the fact.

ORDER MATTERS. The VALIDITY GATE is computed and printed FIRST, before any
architecture contrast. v4's central failure was that its null was reported as an
architecture finding when five of six arms had not beaten a memoryless baseline.
`prereg_v5.VALIDITY_GATE` declares in advance that arms failing the gate make the
contrasts uninterpretable, so that outcome cannot be quietly omitted here.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
from scipy import stats

import prereg_v5 as PR
from evaluate_v2 import cohens_d, holm_bonferroni

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results_v5")
REGIME_ORDER = ("A", "B", "C", "D")


def series(rows, arm, regime, metric):
    hist, net = arm
    sel = [r for r in rows if r["history_encoder"] == hist
           and r["network_encoder"] == net]
    sel.sort(key=lambda r: r["seed"])
    return np.array([r["%s_%s" % (regime, metric)] for r in sel], float)


def ci95(x):
    x = np.asarray(x, float)
    if len(x) < 2:
        return (float(x.mean()) if len(x) else float("nan")), 0.0
    return float(x.mean()), float(1.96 * x.std(ddof=1) / np.sqrt(len(x)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=os.path.join(RESULTS, "entity_v5.json"))
    ap.add_argument("--baselines", default=os.path.join(RESULTS,
                                                        "baselines_v5.json"))
    ap.add_argument("--out", default=os.path.join(RESULTS, "analysis_v5.json"))
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    data = json.load(open(args.results, encoding="utf-8"))
    rows = data["rows"]
    base = json.load(open(args.baselines, encoding="utf-8"))["results"]
    seeds = sorted({r["seed"] for r in rows})
    complete = data.get("complete", False)

    print("=" * 108)
    print("  TEMARL v5 — PRE-REGISTERED ANALYSIS  (prereg commit %s)"
          % data.get("prereg_commit", "?"))
    print("=" * 108)
    print("  %d runs | %d arms x %d seeds | primary = %s | %s"
          % (len(rows), len(PR.ARMS), len(seeds), PR.PRIMARY_METRIC,
             "COMPLETE" if complete else "PARTIAL - interim only"))
    if not complete:
        print("  [!] Experiment unfinished. These are NOT the pre-registered "
              "numbers.")

    # ── 0. the instrument ───────────────────────────────────────────────────
    print("\n" + "=" * 108)
    print("  0. THE INSTRUMENT  (reference ladder, from baselines_v5.json)")
    print("=" * 108)
    print("  %-14s" % "policy" + "".join("%12s" % r for r in REGIME_ORDER))
    for pol in ("null", "random", "best_fixed", "profile", "transition",
                "clairvoyant"):
        print("  %-14s" % pol
              + "".join("%12.4f" % base[r][pol]["dsr_mean"]
                        for r in REGIME_ORDER))
    print("  %-14s" % "SEQ VALUE"
          + "".join("%+12.4f" % (base[r]["transition"]["dsr_mean"]
                                 - base[r]["profile"]["dsr_mean"])
                    for r in REGIME_ORDER))
    print("  (v4 measured SEQ VALUE +0.0005 in every regime -- it could not "
          "discriminate history architectures at all)")

    # ── 1. VALIDITY GATE, before any contrast ───────────────────────────────
    print("\n" + "=" * 108)
    print("  1. VALIDITY GATE — did each arm learn to use intent at all?")
    print("     %s" % PR.VALIDITY_GATE["rule"])
    print("=" * 108)
    bf_b = base["B"]["best_fixed"]
    bfs = np.array(bf_b["per_seed_dsr"], float)
    span_b = base["B"]["transition"]["dsr_mean"] - bf_b["dsr_mean"]
    print("  %-18s %-18s %9s %10s %10s %20s %9s %8s"
          % ("history", "network", "DSR-B", "vs fixed", "capture",
             "95% CI on delta", "p", "gate"))
    print("  " + "-" * 104)
    gate, gate_rows = {}, []
    for arm in PR.ARMS:
        a = series(rows, arm, "B", "dsr")
        if len(a) == 0:
            continue
        n = min(len(a), len(bfs))
        d = a[:n] - bfs[:n]
        se = d.std(ddof=1) / np.sqrt(n) if n > 1 else 0.0
        t, p = stats.ttest_rel(a[:n], bfs[:n]) if n > 1 else (0.0, 1.0)
        cap = 100.0 * d.mean() / span_b if abs(span_b) > 1e-9 else float("nan")
        ok = bool(p < PR.ALPHA and d.mean() > 0)
        gate["%s/%s" % arm] = ok
        gate_rows.append({"arm": "%s/%s" % arm, "dsr_b": float(a.mean()),
                          "delta_vs_fixed": float(d.mean()),
                          "capture_pct": float(cap), "p": float(p),
                          "passes": ok})
        print("  %-18s %-18s %9.4f %+10.4f %9.1f%% %20s %9.4f %8s"
              % (arm[0], arm[1], a.mean(), d.mean(), cap,
                 "[%+.4f, %+.4f]" % (d.mean() - 1.96 * se, d.mean() + 1.96 * se),
                 p, "PASS" if ok else "FAIL"))
    n_pass = sum(gate.values())
    print("\n  %d of %d arms beat the memoryless baseline." % (n_pass, len(gate)))
    if n_pass < len(gate):
        print("  [!] Arms that FAILED did not learn to use intent. Contrasts")
        print("      involving them are UNINTERPRETABLE as architecture")
        print("      comparisons, per the pre-registered gate. (In v4, 5 of 6")
        print("      arms failed this gate and it was never checked.)")

    # ── 2. per-arm table ────────────────────────────────────────────────────
    print("\n" + "=" * 108)
    print("  2. %s BY ARM AND REGIME  (mean +- 95%% CI, n=%d)"
          % (PR.PRIMARY_METRIC.upper(), len(seeds)))
    print("=" * 108)
    print("  %-18s %-18s" % ("history", "network")
          + "".join("%18s" % r for r in REGIME_ORDER))
    summary = {}
    for arm in PR.ARMS:
        cells, means = [], {}
        for rg in REGIME_ORDER:
            s = series(rows, arm, rg, PR.PRIMARY_METRIC)
            if len(s) == 0:
                cells.append("%18s" % "-")
                continue
            m, h = ci95(s)
            means[rg] = m
            cells.append("%18s" % ("%.3f+-%.3f" % (m, h)))
        summary["%s/%s" % arm] = {"means": means}
        print("  %-18s %-18s" % arm + "".join(cells))

    print("\n  MECHANISM (%s, regime B) and cost" % PR.MECHANISM_METRIC)
    print("  %-18s %-18s %16s %12s %10s"
          % ("history", "network", PR.MECHANISM_METRIC, "hist params", "train s"))
    for arm in PR.ARMS:
        s = series(rows, arm, "B", PR.MECHANISM_METRIC)
        if len(s) == 0:
            continue
        m, h = ci95(s)
        sel = [r for r in rows if r["history_encoder"] == arm[0]
               and r["network_encoder"] == arm[1]]
        print("  %-18s %-18s %16s %12d %10.0f"
              % (arm[0], arm[1], "%.3f+-%.3f" % (m, h),
                 int(np.mean([r["n_params_hist"] for r in sel])),
                 float(np.mean([r["train_seconds"] for r in sel]))))

    # ── 3. declared contrast family ─────────────────────────────────────────
    recs, pvals = [], []
    for label, arm_a, arm_b, regime in PR.CONTRAST_FAMILY:
        a = series(rows, tuple(arm_a), regime, PR.PRIMARY_METRIC)
        b = series(rows, tuple(arm_b), regime, PR.PRIMARY_METRIC)
        n = min(len(a), len(b))
        a, b = a[:n], b[:n]
        if n < 2 or np.allclose(a, b):
            t, p, d, lo, hi = 0.0, 1.0, 0.0, 0.0, 0.0
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
                     "t": float(t), "p_raw": float(p), "cohens_d": float(d),
                     "both_arms_passed_gate": bool(
                         gate.get("%s/%s" % tuple(arm_a), False)
                         and gate.get("%s/%s" % tuple(arm_b), False))})
        pvals.append(p)
    holm = holm_bonferroni(pvals)

    print("\n" + "=" * 108)
    print("  3. DECLARED CONTRAST FAMILY  (paired t-test, %s)" % PR.CORRECTION)
    print("=" * 108)
    print("  %-8s %-4s %8s %8s %9s %20s %7s %9s %6s  %s"
          % ("contrast", "reg", "mean A", "mean B", "delta", "95% CI on delta",
             "d", "p_holm", "gate", "verdict"))
    print("  " + "-" * 104)
    for r, h in zip(recs, holm):
        r["p_holm"] = h["p_holm"]
        r["significant"] = h["significant"]
        print("  %-8s %-4s %8.3f %8.3f %+9.4f %20s %+7.2f %9.2e %6s  %s"
              % (r["label"], r["regime"], r["mean_a"], r["mean_b"], r["delta"],
                 "[%+.4f, %+.4f]" % (r["ci_low"], r["ci_high"]),
                 r["cohens_d"], h["p_holm"],
                 "ok" if r["both_arms_passed_gate"] else "VOID",
                 "SIGNIFICANT" if h["significant"] else "not significant"))

    # ── 4. verdicts ─────────────────────────────────────────────────────────
    print("\n" + "=" * 108)
    print("  4. HYPOTHESIS VERDICTS")
    print("=" * 108)
    verdicts = {}
    for hkey, desc, _m in PR.HYPOTHESES:
        rel = [r for r in recs if r["label"].startswith(hkey + "-")]
        pro = [r for r in rel if r["significant"] and r["delta"] > 0]
        con = [r for r in rel if r["significant"] and r["delta"] < 0]
        void = [r for r in rel if not r["both_arms_passed_gate"]]
        if pro and not con:
            v = "SUPPORTED"
        elif con and not pro:
            v = "CONTRADICTED (significant in the OPPOSITE direction)"
        elif pro and con:
            v = "MIXED"
        else:
            v = "NOT SUPPORTED (no significant contrast)"
        if void:
            v += "  [%d/%d contrasts VOID - an arm failed the validity gate]" \
                 % (len(void), len(rel))
        verdicts[hkey] = {"verdict": v, "description": desc}
        print("  %s: %s" % (hkey, v))
        print("      %s" % desc)
        for r in rel:
            print("        %-8s delta=%+.4f  CI [%+.4f, %+.4f]  d=%+.2f  "
                  "p_holm=%.2e  %s"
                  % (r["label"], r["delta"], r["ci_low"], r["ci_high"],
                     r["cohens_d"], r["p_holm"],
                     "" if r["both_arms_passed_gate"] else "VOID"))

    # ── 5. v4 side by side ──────────────────────────────────────────────────
    print("\n" + "=" * 108)
    print("  5. v4 vs v5 — WHAT THE REPAIRED INSTRUMENT CHANGED")
    print("=" * 108)
    try:
        v4 = json.load(open(os.path.join(HERE, "results_v4", "entity_v4.json"),
                            encoding="utf-8"))["rows"]
        t4 = np.array([r["B_dsr"] for r in sorted(
            [x for x in v4 if x["history_encoder"] == "Transformer-RoPE"
             and x["objective"] == "action"], key=lambda x: x["seed"])])
        g4 = np.array([r["B_dsr"] for r in sorted(
            [x for x in v4 if x["history_encoder"] == "GRU"
             and x["objective"] == "action"], key=lambda x: x["seed"])])
        a5 = series(rows, ("Transformer-RoPE", "DeepSets"), "B", "dsr")
        b5 = series(rows, ("GRU", "DeepSets"), "B", "dsr")
        print("  instrument sequence value : v4 +0.0005   ->   v5 %+.4f"
              % (base["B"]["transition"]["dsr_mean"]
                 - base["B"]["profile"]["dsr_mean"]))
        print("  Transformer - GRU on DSR-B: v4 %+.4f   ->   v5 %+.4f"
              % (float(t4.mean() - g4.mean()),
                 float((a5 - b5).mean()) if len(a5) and len(b5) else float("nan")))
        print("  arms beating memoryless   : v4 1 of 6   ->   v5 %d of %d"
              % (n_pass, len(gate)))
    except Exception as e:
        print("  [skip] %s" % str(e)[:100])

    out = {"prereg_commit": data.get("prereg_commit"), "complete": complete,
           "n_seeds": len(seeds), "validity_gate": gate_rows,
           "n_arms_passing_gate": n_pass, "summary": summary,
           "contrasts": recs, "verdicts": verdicts,
           "prereg": {"hypotheses": PR.HYPOTHESES,
                      "contrast_family": PR.CONTRAST_FAMILY,
                      "validity_gate": PR.VALIDITY_GATE,
                      "declaration": PR.DECLARATION}}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, default=float)
    print("\n  wrote -> %s" % os.path.relpath(args.out, HERE))
    print("=" * 108)


if __name__ == "__main__":
    main()
