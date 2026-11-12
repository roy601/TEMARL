# -*- coding: utf-8 -*-
"""Windows for CasinoLimit, built with the frozen window code (command_data.windows, W = 16).

Blinding: `fold_data` returns test INPUTS only (X, mask, owners, source rows). Test targets are
read only by the evaluation step, after PROTOCOL_CL_1.0.md is frozen.
"""
from __future__ import annotations

import collections

import numpy as np

import cl_split as S
from cl_port import D, LABEL_ID, STEPS

W = 16                                       # the encoder's window (CAM-LDS protocol 1.0)


def steps_for(condition: str):
    if condition == "main":
        return STEPS
    if condition == "collapse_repeats":      # keep the first run of each (command, labels); as CAM-LDS
        return [s for s in STEPS if s["occurrence"] == 1]
    raise ValueError(condition)


def folds(condition: str = "main"):
    """The 5 folds (made from the main steps), each carrying the steps of `condition`."""
    st = steps_for(condition)
    return [{**f, "condition": condition, "_steps": st} for f in S.folds(STEPS)]


def sequences(steps, names):
    names = set(names)
    by = collections.defaultdict(list)
    for s in steps:
        if s["run"] in names:
            by[s["run"]].append(s)
    return {r: sorted(v, key=lambda s: s["exec_index"]) for r, v in sorted(by.items())}


def windows(steps, names, window: int = W):
    """X (n, W, 66), mask (n, W), Y (n, 66), owners, source_row of each target."""
    seqs = sequences(steps, names)
    runs = [{"id": r, "commands": [tuple(sorted(LABEL_ID[t] for t in s["techniques_parent"])) for s in q]}
            for r, q in seqs.items()]
    X, M, Y, owners, _ = D.windows(runs, window)
    rows = [s["source_row"] for q in seqs.values() for s in q[1:]]
    return X, M, Y, owners, rows


def fold_data(fold: dict, window: int = W) -> dict:
    st = fold["_steps"]
    Xtr, Mtr, Ytr, _, _ = windows(st, fold["train_runs"], window)
    Xva, Mva, Yva, own_va, rows_va = windows(st, fold["val_runs"], window)
    Xte, Mte, _, own_te, rows_te = windows(st, fold["test_runs"], window)
    return {"train": (Xtr, Mtr, Ytr), "val": (Xva, Mva, Yva), "val_owners": own_va, "val_source_rows": rows_va,
            "test_inputs": (Xte, Mte), "test_owners": own_te, "test_source_rows": rows_te}


def label_seqs(steps, names):
    """run -> list of sorted label tuples (technique IDs), protocol order."""
    return {r: [tuple(sorted(s["techniques_parent"])) for s in q] for r, q in sequences(steps, names).items()}


def points(seq, w: int = W):
    return [(i, tuple(seq[max(0, i - w):i]), seq[i]) for i in range(1, len(seq))]


def mark(test_seqs: dict, seen_seqs: dict, w: int = W) -> list[dict]:
    """As camlds_real/build_sidecar.mark: a test point is a COPY when the same window AND the same
    target occur at a prediction point of a run the fold does not test (training or validation);
    otherwise it is NOVEL. A target label is a REPEAT when it occurs in the window."""
    seen = {(win, tgt) for q in seen_seqs.values() for _, win, tgt in points(q, w)}
    out = []
    for r, q in test_seqs.items():
        for i, win, tgt in points(q, w):
            in_win = {t for step in win for t in step}
            out.append({"run": r, "position": i, "copy": (win, tgt) in seen,
                        "targets": [{"label": t, "repeat": t in in_win} for t in tgt]})
    return out


def label_matrix_ok(Y: np.ndarray) -> bool:
    return Y.ndim == 2 and Y.shape[1] == len(LABEL_ID) and bool(((Y == 0) | (Y == 1)).all())
