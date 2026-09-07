# -*- coding: utf-8 -*-
"""
TEMARL v6 — analysis of the pre-registered replication
=======================================================
Tests EXACTLY the single contrast declared in `prereg_v6.py`, committed before
the replication ran:

    H19-DG-rep : GRU/EntityTransformer vs GRU/DeepSets, regime D (unseen sizes)
                 one-sided paired t-test, n = 31 fixed in advance
                 no multiplicity correction -- one pre-declared contrast

Reports three things, all of them regardless of outcome:
  * the INDEPENDENT n=31 replication (seeds 100-130)
  * the ORIGINAL v5 result (seeds 0-9) beside it
  * the POOLED n=41 estimate, which is the final word

Regimes A/B/C are reported as SECONDARY and carry no claim; they were declared
non-confirmatory in the pre-registration.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
from scipy import stats

import prereg_v6 as PR

HERE = os.path.dirname(os.path.abspath(__file__))
V6 = os.path.join(HERE, "results_v6")
V5 = os.path.join(HERE, "results_v5")


def series(rows, arm, regime, metric="dsr"):
    h, n = arm
    sel = sorted([r for r in rows if r["history_encoder"] == h
                  and r["network_encoder"] == n], key=lambda r: r["seed"])
    return np.array([r["%s_%s" % (regime, metric)] for r in sel], float)


def paired(a, b, one_sided=True):
    d = a - b
    n = len(d)
    m, sd = d.mean(), d.std(ddof=1)
    se = sd / np.sqrt(n)
    t, p2 = stats.ttest_rel(a, b)
    p = p2 / 2 if (one_sided and t > 0) else (1 - p2 / 2 if one_sided else p2)
    return {"n": n, "mean_a": float(a.mean()), "mean_b": float(b.mean()),
            "delta": float(m), "se": float(se), "d": float(m / sd) if sd else 0.0,
            "t": float(t), "p": float(p), "p_two_sided": float(p2),
            "ci_low": float(m - 1.96 * se), "ci_high": float(m + 1.96 * se)}


def show(tag, r, alpha=0.05):
    print("  %-34s n=%-3d  %.4f vs %.4f   delta %+.4f  CI [%+.4f,%+.4f]  "
          "d %+.2f  p %.4f  %s"
          % (tag, r["n"], r["mean_a"], r["mean_b"], r["delta"], r["ci_low"],
             r["ci_high"], r["d"], r["p"],
             "SIGNIFICANT" if r["p"] < alpha else "not significant"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=os.path.join(V6, "entity_v6.json"))
    ap.add_argument("--v5", default=os.path.join(V5, "entity_v5.json"))
    ap.add_argument("--baselines", default=os.path.join(V5, "baselines_v5.json"))
    ap.add_argument("--out", default=os.path.join(V6, "analysis_v6.json"))
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    data = json.load(open(args.results, encoding="utf-8"))
    rows = data["rows"]
    v5rows = json.load(open(args.v5, encoding="utf-8"))["rows"]
    base = json.load(open(args.baselines, encoding="utf-8"))["results"]
    A, B = PR.PRIMARY_CONTRAST[1], PR.PRIMARY_CONTRAST[2]
    complete = data.get("complete", False)

    print("=" * 108)
    print("  TEMARL v6 — PRE-REGISTERED REPLICATION  (prereg %s)"
          % data.get("prereg_commit", "?"))
    print("=" * 108)
    print("  %d runs | planned n = %d | %s"
          % (len(rows), PR.N_PLANNED, "COMPLETE" if complete else
             "PARTIAL - interim, NOT the pre-registered result"))
    print("  contrast: %s/%s  vs  %s/%s   regime %s"
          % (*A, *B, PR.PRIMARY_CONTRAST[3]))
    print("  test    : %s" % PR.TEST)
    print("  %s" % PR.CORRECTION)

    # ── validity gate ───────────────────────────────────────────────────────
    print("\n" + "=" * 108)
    print("  1. VALIDITY GATE (regime D) — %s" % PR.VALIDITY_GATE["rule"])
    print("=" * 108)
    bfs = np.array(base["D"]["best_fixed"]["per_seed_dsr"], float)
    gate_ok, gate_rows = True, []
    for arm in (A, B):
        a = series(rows, arm, "D")
        if len(a) < 2:
            continue
        n = min(len(a), len(bfs))
        t, p = stats.ttest_rel(a[:n], bfs[:n])
        ok = bool(p < 0.05 and (a[:n] - bfs[:n]).mean() > 0)
        gate_ok &= ok
        gate_rows.append({"arm": "%s/%s" % arm, "dsr": float(a.mean()),
                          "p": float(p), "passes": ok})
        print("  %-34s DSR %.4f  vs best_fixed %.4f  delta %+.4f  p %.4f  %s"
              % ("%s/%s" % arm, a.mean(), bfs[:n].mean(),
                 (a[:n] - bfs[:n]).mean(), p, "PASS" if ok else "FAIL"))

    # ── primary contrast ────────────────────────────────────────────────────
    print("\n" + "=" * 108)
    print("  2. PRIMARY CONFIRMATORY CONTRAST — %s" % PR.PRIMARY_CONTRAST[0])
    print("=" * 108)
    a6, b6 = series(rows, A, "D"), series(rows, B, "D")
    n = min(len(a6), len(b6))
    a6, b6 = a6[:n], b6[:n]
    a5, b5 = series(v5rows, A, "D"), series(v5rows, B, "D")

    r5 = paired(a5, b5)
    show("v5 original (seeds 0-9)", r5)
    print("       ^ shown with the REPLICATION's one-sided test purely for")
    print("         comparability. The v5 result stands as pre-registered:")
    print("         two-sided, Holm-corrected over 8 contrasts, p_holm = 0.690,")
    print("         NOT SIGNIFICANT. Re-testing v5 one-sided after the fact")
    print("         would be exactly the practice this project forbids, and no")
    print("         claim here rests on that number.")
    rep = None
    if n >= 2:
        rep = paired(a6, b6)
        show("v6 replication (seeds 100-130)", rep)
        pool_a, pool_b = np.concatenate([a5, a6]), np.concatenate([b5, b6])
        rp = paired(pool_a, pool_b)
        show("POOLED (n=%d)" % len(pool_a), rp)
        print("\n  per-seed differences, replication:")
        print("    %s" % np.round(a6 - b6, 3).tolist())
    else:
        rp = None

    # ── verdict ─────────────────────────────────────────────────────────────
    print("\n" + "=" * 108)
    print("  3. VERDICT")
    print("=" * 108)
    if not complete:
        print("  INTERIM — the experiment has not finished. Not the result.")
    elif not gate_ok:
        print("  VOID — an arm failed the validity gate; no claim may rest on")
        print("  this contrast, per the pre-registration.")
    elif rep and rep["p"] < PR.ALPHA:
        print("  H19-DG-rep is SUPPORTED. The EntityTransformer network encoder")
        print("  beats DeepSets at unseen topology sizes: delta %+.4f, d %.2f,"
              % (rep["delta"], rep["d"]))
        print("  p = %.4f (one-sided, n=%d, powered in advance)."
              % (rep["p"], rep["n"]))
        print("  This REPLICATES v5's H19-DG (%+.4f, d %.2f) on independent"
              % (r5["delta"], r5["d"]))
        print("  seeds, and matches the entity-attention prediction of")
        print("  Symes Thompson et al. (arXiv:2410.17647).")
        print("  Pooled n=%d: delta %+.4f, p %.4f."
              % (rp["n"], rp["delta"], rp["p"]))
    elif rep:
        print("  H19-DG-rep is NOT SUPPORTED. delta %+.4f, d %.2f, p %.4f at"
              % (rep["delta"], rep["d"], rep["p"]))
        print("  n=%d, which had %.0f%% power for the v5 effect size (d=%.2f)."
              % (rep["n"], 100 * PR.POWER_TARGET, PR.EFFECT_REPLICATED))
        print("  The v5 result does not replicate. Pooled n=%d: delta %+.4f,"
              % (rp["n"], rp["delta"]))
        print("  p %.4f — this pooled estimate is the final word, and H19-DG"
              % rp["p"])
        print("  is retired along with the rest of the architecture claim.")
        print("  No further seeds will be added.")

    # ── secondary ───────────────────────────────────────────────────────────
    if n >= 2:
        print("\n" + "=" * 108)
        print("  4. SECONDARY REGIMES (declared non-confirmatory; no claim)")
        print("=" * 108)
        for rg in PR.SECONDARY_REGIMES:
            sa, sb = series(rows, A, rg)[:n], series(rows, B, rg)[:n]
            show("regime %s" % rg, paired(sa, sb))

    out = {"prereg_commit": data.get("prereg_commit"), "complete": complete,
           "validity_gate": gate_rows, "gate_ok": gate_ok,
           "v5_original": r5, "v6_replication": rep, "pooled": rp,
           "prereg": {"hypotheses": PR.HYPOTHESES,
                      "primary_contrast": PR.PRIMARY_CONTRAST,
                      "n_planned": PR.N_PLANNED,
                      "declaration": PR.DECLARATION}}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, default=float)
    print("\n  wrote -> %s" % os.path.relpath(args.out, HERE))
    print("=" * 108)


if __name__ == "__main__":
    main()
