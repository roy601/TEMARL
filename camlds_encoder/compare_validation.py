# -*- coding: utf-8 -*-
"""Apply SELECTION_RULE.md to the validation outputs. Validation only; no test data is read.

    python camlds_encoder/compare_validation.py --candidate allpos --current baseline
    python camlds_encoder/compare_validation.py --smoke ...                         # NOT a result

Writes out/VALIDATION_COMPARISON_<candidate>.txt.
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import statistics as st
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import data  # noqa: E402
from port import Mx, SPEC  # noqa: E402

GROUPS = ("S1 variants", "S3 variants", "S6 variants", "scenario held out")
SUBSETS = ("novel", "copy", "all")
MIN_SEEDS_BETTER, MAX_ALL_DROP = 8, 0.01               # SELECTION_RULE.md


def group_of(f):
    return "scenario held out" if f["family"] == "scenario_held_out" else f"S{f['fold'][0]} variants"


def cell_dir(out, variant, fold, seed):
    if variant == "baseline":
        return os.path.join(out, "train", "main", "Transformer", fold, f"s{seed}")
    return os.path.join(out, "variants", variant, fold, f"s{seed}")


def load_cell(out, variant, fold, seed, rows_expected):
    d = cell_dir(out, variant, fold, seed)
    res = json.load(open(os.path.join(d, "result.json"), encoding="utf-8"))
    meta = res if variant != "baseline" else json.load(open(os.path.join(d, "val_outputs.json"), encoding="utf-8"))
    if meta["val_source_rows"] != rows_expected:
        raise SystemExit(f"{variant} {fold} s{seed}: validation points differ from the fold's")
    return np.load(os.path.join(d, "val_logits.npy")).astype(np.float64), res["threshold"], res


def counts(pred, y, sel_points, label_mask=None):
    """Pooled TP, FP, FN over the selected points (and, if given, the selected labels)."""
    p, t = pred[sel_points], y[sel_points] > 0.5
    if label_mask is not None:
        lm = label_mask[sel_points]
        return (float(np.sum(p & t & lm)), float(np.sum(p & ~t & lm)), float(np.sum(~p & t & lm)))
    return float(np.sum(p & t)), float(np.sum(p & ~t)), float(np.sum(~p & t))


def f1(c):
    tp, fp, fn = c
    return Mx._prf(tp, fp, fn)[2]


def scores(out, variant, seeds, fold_info):
    """seed -> {subset or label class -> {group -> micro-F1}}."""
    res_all = {}
    for s in seeds:
        acc = collections.defaultdict(lambda: collections.defaultdict(lambda: np.zeros(3)))
        for fi in fold_info:
            lo, th, _ = load_cell(out, variant, fi["fold"], s, fi["rows"])
            pred = Mx._sigmoid(lo) >= th
            y, novel, inwin = fi["y"], fi["novel"], fi["in_window"]
            for name, sel in (("novel", novel), ("copy", ~novel), ("all", np.ones_like(novel))):
                if sel.any():
                    acc[name][fi["group"]] += counts(pred, y, sel)
            allp = np.ones(len(y), bool)
            acc["repeat labels"][fi["group"]] += counts(pred, y, allp, inwin)
            acc["new labels"][fi["group"]] += counts(pred, y, allp, ~inwin)
        res_all[s] = {k: {g: f1(c) for g, c in v.items()} for k, v in acc.items()}
    return res_all


def headline(sc, key):
    """Equal-weight mean over the groups present."""
    return float(np.mean(list(sc[key].values())))


def fold_info_for(smoke):
    import run as R
    info = []
    for f in R.pick_folds("main", smoke):
        d = data.fold_data(f)
        Xva, _, Yva = d["val"]
        seqs = data.bs.sequences(f["_steps"])
        marks = data.bs.mark([seqs[r] for r in f["val_runs"]], [seqs[r] for r in f["train_runs"]])
        if [m["source_row"] for m in marks] != d["val_source_rows"]:
            raise SystemExit(f"{f['fold']}: copy marks do not line up with the validation windows")
        info.append({"fold": f["fold"], "group": group_of(f), "rows": d["val_source_rows"], "y": Yva,
                     "novel": np.array([not m["copy"] for m in marks]),
                     "in_window": Xva.max(axis=1) > 0.5})         # label present anywhere in the window
    return info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--current", default="baseline")
    ap.add_argument("--control", default=None, help="reported beside the candidate, never selected")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    out = os.path.join(HERE, "out_smoke" if a.smoke else "out")
    seeds = SPEC.MAIN_SEEDS[:1] if a.smoke else SPEC.MAIN_SEEDS
    info = fold_info_for(a.smoke)
    arms = [a.current, a.candidate] + ([a.control] if a.control else [])
    S = {v: scores(out, v, seeds, info) for v in arms}

    log = [f"VALIDATION COMPARISON: candidate {a.candidate} vs current {a.current}"
           f"{' (control: ' + a.control + ')' if a.control else ''}{'  [SMOKE: not a result]' if a.smoke else ''}",
           "Validation only. Score = micro-F1 pooled within each group, groups weighted equally. "
           "Rule: SELECTION_RULE.md", ""]
    say = log.append
    n_novel = {g: int(sum(fi["novel"].sum() for fi in info if fi["group"] == g)) for g in GROUPS}
    n_all = {g: int(sum(len(fi["novel"]) for fi in info if fi["group"] == g)) for g in GROUPS}
    say("validation points per group (novel / all): " + ", ".join(f"{g} {n_novel[g]}/{n_all[g]}" for g in GROUPS))

    say(f"\n{'score':<16}" + "".join(f"{v:>14}" for v in arms))
    for key in ("novel", "all", "copy", "repeat labels", "new labels"):
        say(f"{key:<16}" + "".join(f"{st.mean(headline(S[v][s], key) for s in seeds):>14.4f}" for v in arms))
    say("\nper group, novel points (mean over seeds):")
    for g in GROUPS:
        say(f"  {g:<18}" + "".join(f"{st.mean(S[v][s]['novel'].get(g, float('nan')) for s in seeds):>14.4f}" for v in arms))

    d_novel = [headline(S[a.candidate][s], "novel") - headline(S[a.current][s], "novel") for s in seeds]
    d_all = [headline(S[a.candidate][s], "all") - headline(S[a.current][s], "all") for s in seeds]
    better = sum(x > 0 for x in d_novel)
    c1 = st.mean(d_novel) > 0
    c2 = better >= (MIN_SEEDS_BETTER if not a.smoke else 1)
    c3 = st.mean(d_all) >= -MAX_ALL_DROP
    say("\nRULE")
    say(f"  1 novel points improve        : mean difference {st.mean(d_novel):+.4f}  -> {'yes' if c1 else 'no'}")
    say(f"  2 in at least 8 of 10 seeds   : {better} of {len(seeds)} seeds  -> {'yes' if c2 else 'no'}")
    say(f"  3 all points fall <= 0.01     : mean difference {st.mean(d_all):+.4f}  -> {'yes' if c3 else 'no'}")
    keep = c1 and c2 and c3
    say(f"\nDECISION: {'KEEP ' + a.candidate if keep else 'KEEP ' + a.current + ' (candidate rejected)'}")
    say("  per-seed novel differences: " + " ".join(f"{x:+.3f}" for x in d_novel))
    txt = "\n".join(log) + "\n"
    name = f"VALIDATION_COMPARISON_{a.candidate}.txt"
    with open(os.path.join(out, name), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(txt)
    print(txt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
