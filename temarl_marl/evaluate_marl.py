# -*- coding: utf-8 -*-
"""
TEMARL v7 — pre-registered analysis
===================================
Reports, in this order, for the study named on the command line:

  1. the VALIDITY GATE: every learned arm vs the best fixed joint action and
     the better uncoordinated reactive baseline (paired over seeds). A contrast
     involving a failing arm is printed but marked VOID.
  2. every declared contrast of `prereg_marl`, whatever its outcome, with
     Holm-Bonferroni correction over the whole family and a direction-aware
     verdict (SUPPORTED / CONTRADICTED / NOT SUPPORTED),
  3. TOST equivalence at the pre-declared margin, so a null is bounded,
  4. the full per-arm table: dwell, depth, protection, exposure, breadcrumb
     chains, capacity violations, reliance on h, parameters, wall-clock.

Nothing here chooses what to report: the family comes from prereg_marl.

    python evaluate_marl.py --study main
    python evaluate_marl.py --study loso
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))


def paired(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = a - b
    n = len(d)
    mean = float(d.mean())
    sd = float(d.std(ddof=1)) if n > 1 else 0.0
    se = sd / np.sqrt(n) if sd > 0 else 0.0
    t, p = stats.ttest_rel(a, b) if n > 1 and sd > 0 else (0.0, 1.0)
    ci = float(stats.t.ppf(0.975, n - 1) * se) if n > 1 and se > 0 else 0.0
    return {"mean": mean, "ci": ci, "t": float(t), "p": float(p),
            "d": mean / sd if sd > 0 else 0.0, "n": n}


def holm(pairs):
    order = sorted(pairs, key=lambda kv: kv[1])
    m, out, prev = len(order), {}, 0.0
    for i, (k, p) in enumerate(order):
        adj = min(1.0, max(prev, (m - i) * p))
        out[k] = adj
        prev = adj
    return out


def tost(a, b, margin):
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = a - b
    n = len(d)
    sd = d.std(ddof=1) if n > 1 else 0.0
    if n < 2 or sd == 0:
        return 1.0
    se = sd / np.sqrt(n)
    p1 = 1 - stats.t.cdf((d.mean() + margin) / se, n - 1)
    p2 = stats.t.cdf((d.mean() - margin) / se, n - 1)
    return float(max(p1, p2))


def load(study, smoke=False):
    d = os.path.join(HERE, "results_marl", ("smoke_" if smoke else "") + study)
    cells = [json.load(open(p, encoding="utf-8"))
             for p in sorted(glob.glob(os.path.join(d, "cells", "*.json")))]
    bpath = os.path.join(d, "baselines_%s.json" % study)
    base = json.load(open(bpath, encoding="utf-8")) if os.path.exists(bpath) else {}
    return cells, base


def per_seed(cells, arm, learner, metric, h0=False, folds=None):
    """{seed: value}. For LOSO the value is the mean over folds of that seed."""
    acc = {}
    for c in cells:
        k = c["cell"]
        if k["arm"] != arm or k["learner"] != learner:
            continue
        if folds is not None and k["fold"] not in folds:
            continue
        rows = c["test_h0"] if h0 else c["test"]
        acc.setdefault(k["seed"], []).append(np.mean([r[metric] for r in rows]))
    return {s: float(np.mean(v)) for s, v in acc.items()}


def base_seed(base, name, metric):
    acc = {}
    for key, blk in base.items():
        s = blk["_meta"]["seed"]
        acc.setdefault(s, []).append(np.mean([r[metric] for r in blk[name]]))
    return {s: float(np.mean(v)) for s, v in acc.items()}


def aligned(x, y):
    ks = sorted(set(x) & set(y))
    return [x[k] for k in ks], [y[k] for k in ks]


def convergence(cells, rise_rel):
    """Pre-registered flag: a cell is POSSIBLY UNDER-TRAINED when its best
    validation dwell came at the final evaluation and beat the previous one by
    more than `rise_rel`. Returns {arm: (n_flagged, n_cells)}."""
    out = {}
    for c in cells:
        arm = (c["cell"]["arm"], c["cell"]["learner"])
        cur = c.get("curve") or []
        flag = False
        if len(cur) >= 2 and c.get("best_update") == cur[-1]["update"]:
            prev = cur[-2]["val_dwell"]
            flag = cur[-1]["val_dwell"] > prev * (1.0 + rise_rel)
        n, k = out.get(arm, (0, 0))
        out[arm] = (n + int(flag), k + 1)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", choices=("main", "loso"), default="main")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    import prereg_marl as PR
    cells, base = load(args.study, args.smoke)
    if not cells:
        raise SystemExit("no cells for study '%s' -- run run_marl.py first" % args.study)
    gates = json.load(open(os.path.join(HERE, "results_marl", "gates.json"), encoding="utf-8"))
    ceil = gates["summary"]["clairvoyant/coord"]
    fams = PR.MAIN_CONTRASTS if args.study == "main" else PR.LOSO_CONTRASTS
    arms = sorted({(c["cell"]["arm"], c["cell"]["learner"]) for c in cells},
                  key=lambda a: (a[1], a[0]))

    print("=" * 108)
    print("  TEMARL v7 — PRE-REGISTERED ANALYSIS: %s study%s   (prereg %s)"
          % (args.study, " [SMOKE]" if args.smoke else "", PR.PREREG_ID))
    fps = {c["fingerprint"] for c in cells}
    print("  cells %d | fingerprints %s | ceiling dwell %.3f depth %.3f"
          % (len(cells), sorted(fps), ceil["dwell"], ceil["depth"]))
    if len(fps) > 1:
        print("  !! cells from more than one fingerprint -- the analysis is invalid")
    print("=" * 108)

    # 1. validity gate
    print("\n--- 1. VALIDITY GATE (reported first; can VOID contrasts) " + "-" * 49)
    bf = base_seed(base, "best_fixed", "dwell")
    rn = base_seed(base, "reactive/naive", "dwell")
    ra = base_seed(base, "reactive/averse", "dwell")
    unc = {s: max(rn[s], ra[s]) for s in rn}
    passing = set()
    for arm in arms:
        x = per_seed(cells, *arm, "dwell")
        g1 = paired(*aligned(x, bf))
        g2 = paired(*aligned(x, unc))
        ok = (g1["mean"] > 0 and g1["p"] < PR.ALPHA and g2["mean"] > 0 and g2["p"] < PR.ALPHA)
        if ok:
            passing.add(arm)
        print("  %-26s dwell %6.3f | vs best-fixed %+6.3f (p=%.4f) | vs uncoordinated "
              "%+6.3f (p=%.4f)  %s" % ("%s/%s" % arm, np.mean(list(x.values())),
                                       g1["mean"], g1["p"], g2["mean"], g2["p"],
                                       "PASS" if ok else "FAIL"))
    print("  gate: %d of %d arms pass" % (len(passing), len(arms)))

    conv = convergence(cells, PR.CONVERGENCE_RISE_REL)
    limited = {a for a, (n, k) in conv.items() if n > k / 2}
    print("\n  convergence flag (pre-registered): cells whose best validation came at "
          "the last evaluation, still rising > %.0f%%" % (100 * PR.CONVERGENCE_RISE_REL))
    for arm in arms:
        n, k = conv.get(arm, (0, 0))
        print("    %-26s %d / %d seeds flagged%s" % ("%s/%s" % arm, n, k,
              "  -> BUDGET-LIMITED" if arm in limited else ""))

    # 2. declared family
    print("\n--- 2. DECLARED CONTRASTS (all reported; Holm over the family) " + "-" * 44)
    rows, ps = [], []
    for tag, a, b, direction in fams:
        for metric in PR.PRIMARY:
            key = "%s-%s" % (tag, metric)
            xa = per_seed(cells, *a, metric)
            xb = per_seed(cells, *b, metric)
            if not xa or not xb:
                rows.append((key, a, b, direction, metric, None, "MISSING"))
                continue
            st = paired(*aligned(xa, xb))
            void = a not in passing or b not in passing
            rows.append((key, a, b, direction, metric, st, "VOID" if void else ""))
            ps.append((key, st["p"]))
    adj = holm(ps)
    uninterp = set(PR.UNINTERPRETABLE_IF_G4_FAILS) if not gates["gates"]["G4"]["pass"] else set()
    print("  %-10s %-48s %9s %20s %7s %8s  verdict"
          % ("", "contrast", "diff", "95% CI", "d_z", "p_holm"))
    for key, a, b, direction, metric, st, flag in rows:
        name = "%s/%s - %s/%s" % (a[0], a[1], b[0], b[1])
        if st is None:
            print("  %-10s %-48s  %s" % (key, name, flag)); continue
        p = adj.get(key, 1.0)
        sig = p < PR.ALPHA
        got = 1 if st["mean"] > 0 else -1
        verdict = ("NOT SUPPORTED" if not sig else
                   "SUPPORTED" if got == direction else "CONTRADICTED")
        margin = PR.TOST_REL * ceil[metric]
        pt = tost(*aligned(per_seed(cells, *a, metric), per_seed(cells, *b, metric)), margin)
        extra = "; TOST-equivalent within %.3f (p=%.4f)" % (margin, pt) if (not sig and pt < PR.ALPHA) else ""
        if key.split("-")[0] in uninterp:
            verdict += " [UNINTERPRETABLE: G4 failed]"
        if a in limited or b in limited:
            verdict += " [BUDGET-LIMITED]"
        if flag:
            verdict += " [%s]" % flag
        print("  %-10s %-48s %+9.3f [%+8.3f,%+8.3f] %+7.2f %8.4f  %s%s"
              % (key, name, st["mean"], st["mean"] - st["ci"], st["mean"] + st["ci"],
                 st["d"], p, verdict, extra))

    # 4. per-arm table
    print("\n--- 3. PER ARM (means over seeds; test episodes) " + "-" * 58)
    keys = ("dwell", "depth", "protected", "exposed", "lure_chains",
            "capacity_violations", "dead_ends")
    print("  %-26s " % "arm" + " ".join("%9s" % k[:9] for k in keys) + "  h=0 dwell  pretrain  params  min/run")
    for arm in arms:
        cs = [c for c in cells if (c["cell"]["arm"], c["cell"]["learner"]) == arm]
        vals = [np.mean(list(per_seed(cells, *arm, k).values())) for k in keys]
        h0 = np.mean(list(per_seed(cells, *arm, "dwell", h0=True).values()))
        pt = np.mean([c["pretrain"].get("top1", np.nan) for c in cs])
        print("  %-26s " % ("%s/%s" % arm) + " ".join("%9.3f" % v for v in vals)
              + "  %9.3f  %8.3f  %6d  %6.1f" % (h0, pt, cs[0]["actor_params"],
                                               np.mean([c["seconds"] for c in cs]) / 60))
    for name in ("null", "random", "best_fixed", "reactive/naive", "reactive/averse",
                 "transition/coord", "clairvoyant/coord"):
        if base and name in next(iter(base.values())):
            vals = [np.mean(list(base_seed(base, name, k).values())) for k in keys]
            print("  %-26s " % ("[%s]" % name) + " ".join("%9.3f" % v for v in vals))
    print("=" * 108)


if __name__ == "__main__":
    main()
