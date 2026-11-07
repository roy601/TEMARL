# -*- coding: utf-8 -*-
"""Folds and windows for the ported encoder, built only from the frozen rules.

  folds        split protocol 1.0 (camlds_real/split_spec.py) minus the 2 S2 folds excluded
               by protocol 1.0 (Q2): 29 variant-held-out + 3 scenario-held-out = 32
  train / val  split_spec.split_train_val: first run, in sorted order, of each training
               scenario with >= 2 runs
  windows      command_data.windows (frozen code): W = 16, left-padded, every step except a
               run's first, never crossing a run boundary
  conditions   "main" (904 steps) and "collapse_repeats" (883 steps, protocol 1.1 A3)

Blinding: `fold_data` returns test INPUTS only (X, mask, point ids). Test targets are not loaded
here. They are read only by the evaluation step, after the design is frozen (protocol 1.2).
"""
from __future__ import annotations

import os
import sys

import numpy as np

from port import D, LABEL_ID, REPO

sys.path.insert(0, os.path.join(REPO, "camlds_real"))
import build_sidecar as bs  # noqa: E402  (definitions shared with the side files)
import split_spec as sp  # noqa: E402

W = bs.W                                        # 16, from protocol 1.0 spec
CONDITIONS = bs.CONDITIONS
FAMILIES = (sp.FAMILY_PRIMARY, sp.FAMILY_SECONDARY)


def steps_for(condition: str):
    steps = sp.load(REPO)
    if condition == "main":
        return steps
    if condition == "collapse_repeats":
        return bs.collapse_repeats(steps)
    raise ValueError(condition)


def folds(condition: str = "main"):
    """The 32 frozen folds, in protocol order."""
    st = steps_for(condition)
    out = []
    for fam in FAMILIES:
        for f in sp.folds(st, fam):
            if fam == sp.FAMILY_PRIMARY and f["fold"] in bs.EXCLUDED:
                continue
            tr, va = sp.split_train_val(f)
            out.append({"condition": condition, "family": fam, "fold": f["fold"],
                        "train_runs": sorted({s["run"] for s in tr}),
                        "val_runs": sorted({s["run"] for s in va}),
                        "test_runs": sorted({s["run"] for s in f["test"]}),
                        "_steps": st})
    return out


def _runs(steps, names):
    """Runs in the frozen pipeline's format: id + list of label-id tuples, protocol order."""
    seqs = bs.sequences([s for s in steps if s["run"] in set(names)])
    return [{"id": r, "commands": [tuple(sorted(LABEL_ID[t] for t in s["techniques_parent"])) for s in seqs[r]],
             "source_rows": [s["source_row"] for s in seqs[r]]} for r in sorted(names)]


def windows(steps, names, window: int = W):
    """X (n, W, 81), mask (n, W), Y (n, 81), owners, source_row of each target."""
    runs = _runs(steps, names)
    X, M, Y, owners, _ = D.windows(runs, window)
    rows = [sr for r in runs for sr in r["source_rows"][1:]]
    return X, M, Y, owners, rows


def fold_data(fold: dict, window: int = W) -> dict:
    st = fold["_steps"]
    Xtr, Mtr, Ytr, _, _ = windows(st, fold["train_runs"], window)
    Xva, Mva, Yva, own_va, rows_va = windows(st, fold["val_runs"], window)
    Xte, Mte, _, own_te, rows_te = windows(st, fold["test_runs"], window)
    return {"train": (Xtr, Mtr, Ytr), "val": (Xva, Mva, Yva), "val_owners": own_va,
            "val_source_rows": rows_va,
            "test_inputs": (Xte, Mte), "test_owners": own_te, "test_source_rows": rows_te}


def describe(fold: dict) -> dict:
    d = fold_data(fold)
    return {"fold": fold["fold"], "family": fold["family"], "condition": fold["condition"],
            "train_windows": int(len(d["train"][0])), "val_windows": int(len(d["val"][0])),
            "test_points": int(len(d["test_inputs"][0])), "val_runs": fold["val_runs"],
            "n_train_runs": len(fold["train_runs"])}


def label_matrix_ok(Y: np.ndarray) -> bool:
    return Y.ndim == 2 and Y.shape[1] == len(LABEL_ID) and bool(((Y == 0) | (Y == 1)).all())
