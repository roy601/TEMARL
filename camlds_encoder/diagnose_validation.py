# -*- coding: utf-8 -*-
"""Error types and training length of a candidate against the current design. Validation only.

    python camlds_encoder/diagnose_validation.py --candidate asl --current allpos

Writes out/DIAGNOSIS_<candidate>.txt. It explains a decision of compare_validation.py; it does not
make one. Precision, recall and error counts are summed over all (fold, seed) cells.
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import statistics as st

import numpy as np

import compare_validation as C
from port import Mx, SPEC

OUT = os.path.join(C.HERE, "out")
SEEDS = SPEC.MAIN_SEEDS


def results(variant, info):
    return {(fi["fold"], s): json.load(open(os.path.join(C.cell_dir(OUT, variant, fi["fold"], s), "result.json"),
                                            encoding="utf-8"))
            for fi in info for s in SEEDS}


def predictions(variant, fi, seed):
    lo, th, _ = C.load_cell(OUT, variant, fi["fold"], seed, fi["rows"])
    return Mx._sigmoid(lo) >= th


def error_table(variant, info):
    acc = collections.defaultdict(lambda: np.zeros(3))
    per_step = []
    for fi in info:
        everything = np.ones(len(fi["novel"]), bool)
        for s in SEEDS:
            p = predictions(variant, fi, s)
            acc["all points"] += C.counts(p, fi["y"], everything)
            if fi["novel"].any():
                acc["novel points"] += C.counts(p, fi["y"], fi["novel"])
            acc["repeat labels"] += C.counts(p, fi["y"], everything, fi["in_window"])
            acc["new labels"] += C.counts(p, fi["y"], everything, ~fi["in_window"])
            per_step.append(p.sum(1).mean())
    return acc, float(np.mean(per_step))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--current", required=True)
    a = ap.parse_args()
    arms = (a.current, a.candidate)
    info = C.fold_info_for(False)
    R = {v: results(v, info) for v in arms}
    log = [f"DIAGNOSIS: {a.candidate} vs {a.current}. Validation only; explains the decision, does not make it.", ""]
    say = log.append

    say("ERRORS, summed over all 320 cells")
    say(f"  {'':<14}{'arm':<10}{'precision':>10}{'recall':>8}{'false pos':>11}{'false neg':>11}")
    tables = {v: error_table(v, info) for v in arms}
    for key in ("all points", "novel points", "repeat labels", "new labels"):
        for v in arms:
            tp, fp, fn = tables[v][0][key]
            say(f"  {key:<14}{v:<10}{tp / (tp + fp):>10.3f}{tp / (tp + fn):>8.3f}{int(fp):>11}{int(fn):>11}")
    for v in arms:
        say(f"  labels predicted per step, {v}: {tables[v][1]:.2f}")

    say("\nTRAINING LENGTH AND THRESHOLDS")
    for v in arms:
        rs = R[v].values()
        th = collections.Counter(r["threshold"] for r in rs)
        say(f"  {v:<10} hit the update budget {sum(r['cap_reached'] for r in rs)}/320 | median best update "
            f"{st.median(r['best_update'] for r in rs):.0f} | median best validation BCE "
            f"{st.median(r['best_validation_bce'] for r in rs):.5f} | threshold 0.5 chosen {th[0.5]}/320")

    capped = [r for r in R[a.candidate].values() if r["cap_reached"]]
    if capped:
        say(f"\nCANDIDATE CELLS THAT HIT THE BUDGET ({len(capped)}): median validation BCE along the budget")
        for frac in (0.25, 0.5, 0.75, 0.9, 1.0):
            vals = [r["curve"][min(len(r["curve"]) - 1, int(round(frac * len(r["curve"]))) - 1)]["validation_bce"]
                    for r in capped]
            say(f"  at {frac:>4.0%}: {st.median(vals):.5f}")
        last = [r["curve"][int(len(r["curve"]) * .75) - 1]["validation_bce"] - r["curve"][-1]["validation_bce"]
                for r in capped]
        say(f"  still falling over the last quarter: {sum(x > 0 for x in last)}/{len(last)}")

        say("\nNOVEL-POINT MICRO-F1 ON THE SAME CELLS, split by whether the candidate hit the budget")
        say("  (not a random split: which cells hit the budget depends on the fold)")
        for name, want in (("hit the budget", True), ("stopped by patience", False)):
            acc = {v: np.zeros(3) for v in arms}
            n = 0
            for fi in info:
                if not fi["novel"].any():
                    continue
                for s in SEEDS:
                    if R[a.candidate][(fi["fold"], s)]["cap_reached"] != want:
                        continue
                    n += 1
                    for v in arms:
                        acc[v] += C.counts(predictions(v, fi, s), fi["y"], fi["novel"])
            say(f"  {name:<20} cells {n:>3}: " + "  ".join(f"{v} {C.f1(acc[v]):.4f}" for v in arms))

    txt = "\n".join(log) + "\n"
    with open(os.path.join(OUT, f"DIAGNOSIS_{a.candidate}.txt"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(txt)
    print(txt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
