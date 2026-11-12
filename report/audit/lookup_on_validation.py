# -*- coding: utf-8 -*-
"""Audit question, 2026-11-11: does a lookup table do as well as the neural encoders?

    python report/audit/lookup_on_validation.py

VALIDATION DATA ONLY. No test output and no test label is scored here. Exploratory: this baseline
is not in any protocol. It has no trained weights, no threshold and no tuned setting.

  previous-step lookup   predict the label set that most often followed the same previous step in
                         the fold's training runs
  longest-match lookup   the same, but using the longest run of recent steps (up to 16) that occurs
                         in the training runs
  Unseen context: fall back to the most frequent next label set in training. Ties: sorted order.

Also prints three definitions of the recall ceiling on the test runs (labels only).
"""
import collections
import csv
import json
import os

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = lambda *a: os.path.join(REPO, *a)
OUT, W, SEEDS = P("camlds_encoder", "out"), 16, range(10)

rows = list(csv.DictReader(open(P("camlds_real", "attack_times.csv"), encoding="utf-8"), delimiter=";"))
by = collections.defaultdict(list)
for i, r in enumerate(rows):
    r["i"], r["par"] = i, tuple(sorted({t.split(".")[0] for t in r["techniques"].split("_")}))
    by[r["scenario"]].append(r)
SEQ = {k: [r["par"] for r in sorted(v, key=lambda r: (float(r["start"]), int(r["event_id"])))] for k, v in by.items()}
LABELS = sorted({t for r in rows for t in r["par"]})
ID = {t: k for k, t in enumerate(LABELS)}
scen = lambda run: run.split("_")[0]


def val_rule(pool):
    g = collections.defaultdict(list)
    for r in pool:
        g[scen(r)].append(r)
    return sorted(sorted(v)[0] for v in g.values() if len(v) >= 2)


FOLDS = []
for b in ("1", "3", "6"):
    runs = sorted(r for r in SEQ if scen(r) == b)
    for r in runs:
        pool = [x for x in runs if x != r]
        va = val_rule(pool)
        FOLDS.append(("variant", r, [x for x in pool if x not in va], va, [r]))
for b in ("2", "3", "6"):
    pool = sorted(r for r in SEQ if scen(r) != b)
    va = val_rule(pool)
    FOLDS.append(("scenario", f"S{b}", [x for x in pool if x not in va], va, sorted(r for r in SEQ if scen(r) == b)))


def points(runs):
    return [(tuple(SEQ[r][max(0, t - W):t]), SEQ[r][t]) for r in sorted(runs) for t in range(1, len(SEQ[r]))]


def table(train_pts):
    tab = collections.defaultdict(collections.Counter)
    for win, tgt in train_pts:
        for k in range(1, len(win) + 1):
            tab[win[-k:]][tgt] += 1
        tab[()][tgt] += 1
    return {ctx: sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[0][0] for ctx, c in tab.items()}


def lookup(tab, win, longest):
    for k in (range(len(win), 0, -1) if longest else (1,)):
        if win[-k:] in tab:
            return tab[win[-k:]]
    return tab[()]


def f1(c):
    return 0.0 if c[0] == 0 else 2 * c[0] / (2 * c[0] + c[1] + c[2])


def count(pred_sets, tgt_sets, sel):
    tp = fp = fn = 0
    for p, t, s in zip(pred_sets, tgt_sets, sel):
        if s:
            tp += len(set(p) & set(t)); fp += len(set(p) - set(t)); fn += len(set(t) - set(p))
    return tp, fp, fn


def model_sets(arm, fold, seed, n):
    d = os.path.join(OUT, "variants", arm, fold, f"s{seed}")
    th = json.load(open(os.path.join(d, "result.json"), encoding="utf-8"))["threshold"]
    lo = np.load(os.path.join(d, "val_logits.npy")).astype(np.float64)
    assert len(lo) == n
    return [tuple(LABELS[j] for j in np.where(1 / (1 + np.exp(-z)) >= th)[0]) for z in lo]


res = collections.defaultdict(lambda: collections.defaultdict(list))
for fam, fold, tr, va, te in FOLDS:
    trp, vap = points(tr), points(va)
    tab, seen = table(trp), set(trp)
    tgt = [t for _, t in vap]
    novel = [p not in seen for p in vap]
    for sub, sel in (("all", [True] * len(vap)), ("novel", novel)):
        if not any(sel):
            continue
        res[fam, sub]["previous-step lookup"].append(f1(count([lookup(tab, w, False) for w, _ in vap], tgt, sel)))
        res[fam, sub]["longest-match lookup"].append(f1(count([lookup(tab, w, True) for w, _ in vap], tgt, sel)))
        for arm, name in (("allpos", "Transformer"), ("gru_allpos", "GRU"), ("lstm_allpos", "LSTM")):
            res[fam, sub][name].append(float(np.mean([f1(count(model_sets(arm, fold, s, len(vap)), tgt, sel)) for s in SEEDS])))

print("VALIDATION ONLY. Micro-F1, mean over folds (models: mean over 10 seeds first). Exploratory.\n")
names = ("previous-step lookup", "longest-match lookup", "Transformer", "GRU", "LSTM")
print(f"{'':<34}" + "".join(f"{n:>22}" for n in names))
for fam, label in (("variant", "variant folds (29)"), ("scenario", "scenario folds (3)")):
    for sub in ("all", "novel"):
        print(f"{label + ', ' + sub + ' points':<34}" + "".join(f"{np.mean(res[fam, sub][n]):>22.3f}" for n in names))
v = res["variant", "novel"]
print("\nvariant folds, novel points: folds where the Transformer beats the longest-match lookup:",
      sum(a > b for a, b in zip(v["Transformer"], v["longest-match lookup"])), "of", len(v["Transformer"]))

print("\nRECALL CEILING ON THE TEST RUNS (labels only): share of target labels the model has seen")
print(f"{'':<12}{'published: all test steps,':>30}{'predicted steps only,':>26}{'predicted steps only,':>26}")
print(f"{'':<12}{'seen in train+validation':>30}{'seen in train+validation':>26}{'seen in training only':>26}")
acc = collections.defaultdict(list)
for fam, fold, tr, va, te in FOLDS:
    lab = lambda runs: {t for r in runs for s in SEQ[r] for t in s}
    all_t = [t for r in te for s in SEQ[r] for t in s]
    pred_t = [t for r in te for s in SEQ[r][1:] for t in s]
    row = (np.mean([t in lab(tr + va) for t in all_t]), np.mean([t in lab(tr + va) for t in pred_t]),
           np.mean([t in lab(tr) for t in pred_t]))
    acc[fam].append(row)
    if fam == "scenario":
        print(f"{fold:<12}{row[0]:>30.3f}{row[1]:>26.3f}{row[2]:>26.3f}")
m = np.mean(acc["variant"], axis=0)
print(f"{'variant mean':<12}{m[0]:>30.3f}{m[1]:>26.3f}{m[2]:>26.3f}")
