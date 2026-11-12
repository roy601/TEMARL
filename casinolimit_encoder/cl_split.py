# -*- coding: utf-8 -*-
"""The CasinoLimit split (PROTOCOL_CL_1.0.md, Section 2). No randomness, no seed.

  unit      one run = one human attacker (a CasinoLimit instance). A run is never split.
  folds     K = 5. Runs are sorted by number of steps (longest first, ties by name) and dealt to
            the folds in snake order (F1..F5, F5..F1, ...), so every fold gets long and short
            attacks and about the same number of prediction points.
  roles     for test fold Fi: validation = the next fold F(i+1) (F5 -> F1), training = the other 3.
  condition the folds are made once, from the "main" steps; "collapse_repeats" uses the same runs
            in the same folds.
"""
from __future__ import annotations

import collections

K = 5
FOLD_NAMES = tuple(f"F{i + 1}" for i in range(K))
CONDITIONS = ("main", "collapse_repeats")
# The user approved PROTOCOL_CL_1.0.md on this date (before any real training).
APPROVED_ON = "2026-11-12"


def run_lengths(steps):
    n = collections.Counter(s["run"] for s in steps)
    return dict(sorted(n.items()))


def assign(steps, k: int = K) -> dict:
    """run -> fold name."""
    n = run_lengths(steps)
    order = sorted(n, key=lambda r: (-n[r], r))
    out = {}
    for i, r in enumerate(order):
        lap, pos = divmod(i, k)
        out[r] = FOLD_NAMES[pos if lap % 2 == 0 else k - 1 - pos]
    return out


def folds(steps) -> list[dict]:
    """The 5 folds: test, validation and training runs, from the main steps."""
    fold_of = assign(steps)
    by = collections.defaultdict(list)
    for r, f in fold_of.items():
        by[f].append(r)
    out = []
    for i, name in enumerate(FOLD_NAMES):
        val = FOLD_NAMES[(i + 1) % K]
        out.append({"fold": name, "test_runs": sorted(by[name]), "val_runs": sorted(by[val]),
                    "train_runs": sorted(r for f in FOLD_NAMES if f not in (name, val) for r in by[f])})
    return out
