# -*- coding: utf-8 -*-
"""
Temarl_Test_v1_L1 -- multi-label metrics for next-command prediction
=====================================================================
The target is a SET of techniques, so single-label accuracy does not apply.
Reported, per Zhang & Zhou (IEEE TKDE 2014) on multi-label evaluation:

    BCE                 threshold-free, the training objective
    micro-F1            label-instance weighted; dominated by frequent labels
    macro-F1            label-averaged over labels WITH SUPPORT in the split
    exact-set accuracy  fraction of commands whose predicted set is exactly
                        right (strict; a single wrong label fails the command)
    ranking metrics     precision@1, recall@3, recall@5 -- threshold-free, and
                        the closest available analogue to "is the top guess in
                        the true set"

NOT comparable with the previous study
--------------------------------------
Old Top-1 was "did the single predicted token equal the single true token"
over 1,311 flattened transitions. Nothing here is that quantity: the targets
are sets over 853 command transitions. precision@1 is the nearest relative and
is still a different measurement. Never tabulate them together.

Macro-F1 support rule
---------------------
Labels absent from the evaluation split are excluded from the macro average,
and the count of averaged labels is reported alongside, because a macro score
over a different label set is a different number.

Thresholds
----------
A single global threshold is selected on VALIDATION micro-F1 from a fixed
grid. Tie rule: the smallest threshold among ties, fixed in advance so the
choice cannot drift with the data.
"""

from __future__ import annotations

from typing import Dict, List, Sequence

import numpy as np

THRESHOLD_GRID = (0.1, 0.2, 0.3, 0.4, 0.5)


def _sigmoid(z: np.ndarray) -> np.ndarray:
    # Numerically stable; logits can be large negative for rare labels.
    out = np.empty_like(z, dtype=np.float64)
    pos, neg = z >= 0, z < 0
    out[pos] = 1.0 / (1.0 + np.exp(-z[pos]))
    ez = np.exp(z[neg])
    out[neg] = ez / (1.0 + ez)
    return out


def bce(logits: np.ndarray, y: np.ndarray) -> float:
    """Mean binary cross-entropy over all label slots, in nats."""
    z = np.asarray(logits, np.float64)
    t = np.asarray(y, np.float64)
    # log(1+exp(-|z|)) + max(z,0) - z*t  : the stable BCEWithLogits form
    loss = np.maximum(z, 0) - z * t + np.log1p(np.exp(-np.abs(z)))
    return float(loss.mean())


def _prf(tp: float, fp: float, fn: float):
    p = tp / (tp + fp) if (tp + fp) else 0.0
    r = tp / (tp + fn) if (tp + fn) else 0.0
    f = 2 * p * r / (p + r) if (p + r) else 0.0
    return p, r, f


def threshold_metrics(prob: np.ndarray, y: np.ndarray, threshold: float) -> dict:
    pred = prob >= threshold
    t = y > 0.5
    tp = float(np.sum(pred & t))
    fp = float(np.sum(pred & ~t))
    fn = float(np.sum(~pred & t))
    micro_p, micro_r, micro_f1 = _prf(tp, fp, fn)

    supported = np.where(t.any(axis=0))[0]        # labels present in this split
    f1s = []
    for j in supported:
        _, _, f = _prf(float(np.sum(pred[:, j] & t[:, j])),
                       float(np.sum(pred[:, j] & ~t[:, j])),
                       float(np.sum(~pred[:, j] & t[:, j])))
        f1s.append(f)
    return {
        "threshold": float(threshold),
        "micro_precision": micro_p, "micro_recall": micro_r, "micro_f1": micro_f1,
        "macro_f1": float(np.mean(f1s)) if f1s else 0.0,
        "macro_f1_label_count": int(len(supported)),
        "exact_set_accuracy": float(np.mean(np.all(pred == t, axis=1))),
        "mean_predicted_labels": float(pred.sum(axis=1).mean()),
        "mean_true_labels": float(t.sum(axis=1).mean()),
        "empty_prediction_pct": float(100.0 * np.mean(~pred.any(axis=1))),
    }


def ranking_metrics(prob: np.ndarray, y: np.ndarray) -> dict:
    """Threshold-free. recall@k = fraction of true labels inside the top k."""
    order = np.argsort(-prob, axis=1, kind="stable")
    t = y > 0.5
    n = len(y)
    rows = np.arange(n)
    out = {"precision_at_1": float(np.mean(t[rows, order[:, 0]]))}
    for k in (3, 5):
        kk = min(k, prob.shape[1])
        hit = np.take_along_axis(t, order[:, :kk], axis=1).sum(axis=1)
        tot = t.sum(axis=1)
        out[f"recall_at_{k}"] = float(np.mean(np.divide(
            hit, tot, out=np.zeros_like(hit, np.float64), where=tot > 0)))
    return out


def select_threshold(prob: np.ndarray, y: np.ndarray,
                     grid: Sequence[float] = THRESHOLD_GRID) -> float:
    """Pick the threshold maximising micro-F1; ties go to the SMALLEST value.

    Must be called on validation only. The tie rule is fixed in advance.
    """
    best_t, best_f1 = None, -1.0
    for t in sorted(grid):
        f1 = threshold_metrics(prob, y, t)["micro_f1"]
        if f1 > best_f1 + 1e-12:
            best_t, best_f1 = float(t), f1
    return best_t


def evaluate(logits: np.ndarray, y: np.ndarray, owners: Sequence[str],
             threshold: float, scenarios: Dict[str, str] = None) -> dict:
    """Full metric block at a GIVEN threshold (never selected on this split).

    Pooled metrics weight long runs more heavily, because a run contributes
    one window per command. `per_run` and the run/scenario macro averages give
    the equal-weight view; both are reported, as neither is privileged.
    """
    logits = np.asarray(logits, np.float64)
    y = np.asarray(y, np.float64)
    prob = _sigmoid(logits)

    out = {"n": int(len(y)), "bce": bce(logits, y)}
    out.update(threshold_metrics(prob, y, threshold))
    out.update(ranking_metrics(prob, y))

    per_run = {}
    for name in sorted(set(owners)):
        ix = np.array([o == name for o in owners])
        pr = threshold_metrics(prob[ix], y[ix], threshold)
        per_run[name] = {
            "n": int(ix.sum()),
            "bce": bce(logits[ix], y[ix]),
            "micro_f1": pr["micro_f1"],
            "exact_set_accuracy": pr["exact_set_accuracy"],
            "precision_at_1": ranking_metrics(prob[ix], y[ix])["precision_at_1"],
        }
    out["per_run"] = per_run
    out["run_macro_micro_f1"] = float(np.mean([v["micro_f1"] for v in per_run.values()]))
    out["run_macro_bce"] = float(np.mean([v["bce"] for v in per_run.values()]))

    if scenarios:
        by_scn: Dict[str, List[str]] = {}
        for name in per_run:
            by_scn.setdefault(scenarios.get(name, "?"), []).append(name)
        out["scenario_macro_micro_f1"] = float(np.mean([
            float(np.mean([per_run[n]["micro_f1"] for n in names]))
            for names in by_scn.values()]))
        out["per_scenario"] = {
            s: {"runs": len(names),
                "micro_f1": float(np.mean([per_run[n]["micro_f1"] for n in names])),
                "bce": float(np.mean([per_run[n]["bce"] for n in names]))}
            for s, names in sorted(by_scn.items())}
    return out


def per_label_report(logits: np.ndarray, y: np.ndarray, threshold: float) -> dict:
    """Per-label precision/recall/F1 with explicit support counts."""
    prob = _sigmoid(np.asarray(logits, np.float64))
    pred, t = prob >= threshold, np.asarray(y) > 0.5
    rep = {}
    for j in range(y.shape[1]):
        support = int(t[:, j].sum())
        if support == 0 and not pred[:, j].any():
            continue
        p, r, f = _prf(float(np.sum(pred[:, j] & t[:, j])),
                       float(np.sum(pred[:, j] & ~t[:, j])),
                       float(np.sum(~pred[:, j] & t[:, j])))
        rep[int(j)] = {"support": support, "predicted": int(pred[:, j].sum()),
                       "precision": p, "recall": r, "f1": f}
    return rep
