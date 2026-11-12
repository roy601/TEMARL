# -*- coding: utf-8 -*-
"""Lookup-table baseline (PROTOCOL_CL_1.0.md, Section 4). No weights, no threshold, nothing tuned.

The same rule as report/audit/lookup_on_validation.py (the 2026-11-11 audit), so the two corpora
are measured the same way:
  longest match   for a window, find the longest run of most recent steps (up to W = 16) that
                  occurs as a context in the TRAINING runs, and predict the label set that most
                  often followed it there. Unseen context: the most frequent next label set in
                  training. Ties: the smallest label set in sorted order.
  previous step   the same with only the last step as context.
  repeat last     predict the label set of the last step again (no table at all).
The three rules are the "simple baselines". For each fold, the one with the highest validation
micro-F1 is the comparator (PROTOCOL_CL_1.0.md, Section 4).
"""
from __future__ import annotations

import collections

import numpy as np

from cl_data import W, points


def table(train_seqs: dict, w: int = W) -> dict:
    tab = collections.defaultdict(collections.Counter)
    for q in train_seqs.values():
        for _, win, tgt in points(q, w):
            for k in range(1, len(win) + 1):
                tab[win[-k:]][tgt] += 1
            tab[()][tgt] += 1
    return {ctx: sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[0][0] for ctx, c in tab.items()}


def predict(tab: dict, win: tuple, longest: bool = True) -> tuple:
    for k in (range(len(win), 0, -1) if longest else (1,)):
        if win[-k:] in tab:
            return tab[win[-k:]]
    return tab[()]


RULES = ("longest", "previous", "repeat_last")


def predict_rule(rule: str, tab: dict, win: tuple) -> tuple:
    if rule == "longest":
        return predict(tab, win, True)
    if rule == "previous":
        return predict(tab, win, False)
    if rule == "repeat_last":
        return win[-1]
    raise ValueError(rule)


def predictions(tab: dict, seqs: dict, label_id: dict, rule: str = "longest", w: int = W) -> np.ndarray:
    """(n_points, n_labels) 0/1, points in the same order as cl_data.windows."""
    rows = []
    for q in seqs.values():
        for _, win, _ in points(q, w):
            y = np.zeros(len(label_id), np.float32)
            y[[label_id[t] for t in predict_rule(rule, tab, win)]] = 1.0
            rows.append(y)
    return np.asarray(rows, np.float32).reshape(-1, len(label_id))
