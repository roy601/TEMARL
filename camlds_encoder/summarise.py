# -*- coding: utf-8 -*-
"""Integrity checks and VALIDATION summary of the GPU run. No test score is computed.

    python camlds_encoder/summarise.py

Test logits are opened only to check their hash, shape and point ids. Test targets are never read.
Context baselines (protocol 1.0, Section 3.3) are scored on the same validation windows:
  repeat previous   the previous step's label set
  label prior       training label frequency, threshold chosen on validation from the 1.0 grid
Writes out/VALIDATION_SUMMARY.txt.
"""
from __future__ import annotations

import collections
import hashlib
import json
import os
import statistics as st
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import data  # noqa: E402
from port import Mx, SPEC  # noqa: E402

OUT = os.path.join(HERE, "out")


def load_results(condition="main", arm="Transformer"):
    base = os.path.join(OUT, "train", condition, arm)
    res = []
    for fold in sorted(os.listdir(base)):
        for s in sorted(os.listdir(os.path.join(base, fold))):
            p = os.path.join(base, fold, s, "result.json")
            r = json.load(open(p, encoding="utf-8"))
            r["_dir"] = os.path.dirname(p)
            res.append(r)
    return res


def integrity(res, budget, folds, side):
    chk = {}
    keys = {(r["fold"], r["seed"]) for r in res}
    chk["320 cells, one per fold and seed"] = len(res) == 320 == len(keys) and \
        {f["fold"] for f in folds} == {r["fold"] for r in res} and {r["seed"] for r in res} == set(SPEC.MAIN_SEEDS)
    chk["no smoke cell; 81 labels; window 16"] = all(not r["smoke"] and r["labels"] == 81 and r["window"] == 16 for r in res)
    chk["every cell used the pilot's patience and budget"] = all(
        r["budget"] == {k: budget[k] for k in ("shared_patience", "shared_update_budget")} for r in res)
    chk["no test metric stored (only the sealed block)"] = all(
        [k for k in r if "test" in k] == ["sealed_test"] for r in res)
    want = collections.defaultdict(list)
    for p in side:
        if p["condition"] == "main":
            want[p["fold"]].append(p["source_row"])
    ok_hash = ok_shape = ok_rows = True
    for r in res:
        f = os.path.join(r["_dir"], r["sealed_test"]["file"])
        raw = open(f, "rb").read()
        ok_hash &= hashlib.sha256(raw).hexdigest() == r["sealed_test"]["sha256"]
        lo = np.load(f)
        ok_shape &= lo.shape == (r["sealed_test"]["points"], 81) and bool(np.isfinite(lo).all())
        ok_rows &= r["sealed_test"]["source_rows"] == want[r["fold"]]
    chk["sealed test files match their SHA-256"] = ok_hash
    chk["sealed test outputs: right shape, all finite"] = ok_shape
    chk["sealed test points = protocol 1.1 side file"] = ok_rows
    chk["thresholds inside the frozen grid"] = all(r["threshold"] in SPEC.THRESHOLD_GRID for r in res)
    return chk


def micro_f1(pred, y):
    return Mx.threshold_metrics(pred.astype(np.float64), y, 0.5)["micro_f1"]


def baselines(fold):
    d = data.fold_data(fold)
    Xva, _, Yva = d["val"]
    Ytr = d["train"][2]
    rep = micro_f1(Xva[:, -1, :], Yva)                       # most recent step sits at the end
    prior = np.tile(Ytr.mean(0), (len(Yva), 1))
    th = Mx.select_threshold(prior, Yva)
    pri = Mx.threshold_metrics(prior, Yva, th)["micro_f1"]
    return rep, pri, len(Yva)


def val_copies(fold):
    """Share of validation points whose (window, target) also occurs in the training runs."""
    st_ = fold["_steps"]
    seqs = data.bs.sequences(st_)
    m = data.bs.mark([seqs[r] for r in fold["val_runs"]], [seqs[r] for r in fold["train_runs"]])
    return sum(x["copy"] for x in m), len(m)


def main():
    budget = json.load(open(os.path.join(OUT, "budget.json"), encoding="utf-8"))
    folds = data.folds("main")
    side = [json.loads(x) for x in open(os.path.join(data.REPO, "camlds_real", "out", "sidecar", "points.jsonl"),
                                         encoding="utf-8")]
    res = load_results()
    log = []
    say = log.append

    say("A. INTEGRITY")
    chk = integrity(res, budget, folds, side)
    for k, v in chk.items():
        say(f"  {'PASS' if v else 'FAIL'}  {k}")

    say("\nB. TRAINING")
    say(f"  pilot: {budget['n_pilot_cells']} cells, {budget['seconds'] / 60:.0f} min; patience {budget['shared_patience']} "
        f"checks; budget {budget['shared_update_budget']} updates")
    say(f"  pilot configurations still improving at the 8,192 cap: {len(budget['convergence_unresolved'])} "
        f"{budget['convergence_unresolved']}")
    cap = [r for r in res if r["cap_reached"]]
    say(f"  main cells that used the whole budget (stopped by the cap, not by patience): {len(cap)} of {len(res)}")
    late = [r for r in cap if r["best_update"] > 0.9 * r["updates_completed"]]
    say(f"    of which the best checkpoint was in the last 10%: {len(late)} "
        f"{sorted({(r['fold'], r['seed']) for r in late})[:12]}")
    say(f"  updates: median {st.median(r['updates_completed'] for r in res):.0f}; best update median "
        f"{st.median(r['best_update'] for r in res):.0f}; training time {sum(r['seconds'] for r in res) / 60:.0f} min")
    th = collections.Counter(r["threshold"] for r in res)
    say(f"  thresholds chosen on validation: {dict(sorted(th.items()))} "
        f"(at a grid end: {th[min(SPEC.THRESHOLD_GRID)] + th[max(SPEC.THRESHOLD_GRID)]})")
    say(f"  validation cells predicting nothing for some point: "
        f"{sum(r['validation']['empty_prediction_pct'] > 0 for r in res)}; "
        f"median empty share {st.median(r['validation']['empty_prediction_pct'] for r in res):.1f}%")

    say("\nC. VALIDATION micro-F1 (Transformer: mean over 10 seeds; SD across seeds)")
    say("   Baselines on the same windows. Validation sets are small (one run per scenario), so per-fold numbers are noisy.")
    say(f"  {'fold':<28} {'val pts':>7} {'copies':>7} {'Transformer':>13} {'repeat prev':>11} {'label prior':>11}")
    by_fold = collections.defaultdict(list)
    for r in res:
        by_fold[r["fold"]].append(r["validation"]["micro_f1"])
    rows = []
    for f in folds:
        v = by_fold[f["fold"]]
        rep, pri, n = baselines(f)
        c, nc = val_copies(f)
        rows.append({"fold": f["fold"], "family": f["family"], "scen": "S" + (f["fold"][1] if f["fold"].startswith("S") else f["fold"][0]),
                     "tf": st.mean(v), "sd": st.stdev(v), "rep": rep, "pri": pri, "n": n, "copy": c / nc})
        say(f"  {f['fold']:<28} {n:>7} {c / nc:>6.0%} {st.mean(v):>8.3f} ±{st.stdev(v):.3f} {rep:>11.3f} {pri:>11.3f}")

    say("\nD. BY GROUP (mean of fold means)")
    groups = collections.defaultdict(list)
    for x in rows:
        groups[(x["family"], x["scen"])].append(x)
        groups[(x["family"], "all")].append(x)
    for (fam, sc), xs in sorted(groups.items()):
        win = sum(x["tf"] > x["rep"] for x in xs)
        say(f"  {fam:<18} {sc:<4} folds {len(xs):>2} | Transformer {st.mean(x['tf'] for x in xs):.3f} | "
            f"repeat prev {st.mean(x['rep'] for x in xs):.3f} | label prior {st.mean(x['pri'] for x in xs):.3f} | "
            f"Transformer above repeat-prev in {win} of {len(xs)} folds | validation copies {st.mean(x['copy'] for x in xs):.0%}")

    txt = "\n".join(log) + "\n"
    with open(os.path.join(OUT, "VALIDATION_SUMMARY.txt"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(txt)
    print(txt)
    return 0 if all(chk.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
