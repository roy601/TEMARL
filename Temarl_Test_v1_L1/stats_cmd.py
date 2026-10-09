# -*- coding: utf-8 -*-
"""
Temarl_Test_v1_L1 -- paired statistics with Holm correction
=============================================================
Two-sided paired t-tests across matched training seeds, Holm-corrected within
a predeclared family (`study_spec.PREDICTION_FAMILY` / `RL_FAMILY`).

What a p-value here does and does not mean
------------------------------------------
Seeds are matched, so a contrast controls for initialisation. The intervals
describe SEED variability conditional on one fixed split of 36 playbooks from
7 scenarios. They do NOT describe variability across attack campaigns, and
they cannot support a claim about attacks the corpus does not contain.

Non-significance is not equivalence. `tost()` is provided for cases where an
equivalence claim is wanted, and it requires a margin declared in advance.
Without that margin, the correct phrasing is "no clear difference detected".
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence

import numpy as np

try:
    from scipy import stats as _scipy_stats
except ImportError:                                   # scipy is optional
    _scipy_stats = None


def _t_sf(t: float, df: int) -> float:
    """Upper-tail P(T > t). Uses scipy when available, else the incomplete
    beta identity, so results do not depend on scipy being installed."""
    if _scipy_stats is not None:
        return float(_scipy_stats.t.sf(t, df))
    x = df / (df + t * t)
    return 0.5 * _betainc(df / 2.0, 0.5, x)


def _betainc(a: float, b: float, x: float) -> float:
    """Regularised incomplete beta I_x(a, b) by continued fraction."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbeta = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    front = math.exp(math.log(x) * a + math.log1p(-x) * b - lbeta) / a
    f, c, d = 1.0, 1.0, 0.0
    for i in range(0, 300):
        m = i // 2
        if i == 0:
            num = 1.0
        elif i % 2 == 0:
            num = (m * (b - m) * x) / ((a + 2 * m - 1) * (a + 2 * m))
        else:
            num = -((a + m) * (a + b + m) * x) / ((a + 2 * m) * (a + 2 * m + 1))
        d = 1.0 + num * d
        d = 1e-30 if abs(d) < 1e-30 else d
        d = 1.0 / d
        c = 1.0 + num / c
        c = 1e-30 if abs(c) < 1e-30 else c
        f *= c * d
        if abs(1.0 - c * d) < 1e-12:
            break
    result = front * (f - 1.0)
    return min(max(result if a > 0 else 0.0, 0.0), 1.0)


def _t_crit(df: int, alpha: float = 0.05) -> float:
    if _scipy_stats is not None:
        return float(_scipy_stats.t.ppf(1 - alpha / 2, df))
    lo, hi = 0.0, 100.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if _t_sf(mid, df) > alpha / 2:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def paired_test(a: Sequence[float], b: Sequence[float],
                label: str = "", alpha: float = 0.05) -> dict:
    """Two-sided paired t-test of (a - b) across matched seeds."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    if a.shape != b.shape:
        raise ValueError(f"{label}: unequal pair counts {a.shape} vs {b.shape}")
    d = a - b
    n = len(d)
    if n < 2:
        raise ValueError(f"{label}: need >= 2 pairs, got {n}")
    mean = float(d.mean())
    sd = float(d.std(ddof=1))
    if sd == 0.0:
        return {"contrast": label, "pairs": n, "delta": mean,
                "ci_low": mean, "ci_high": mean, "t": float("inf") if mean else 0.0,
                "p_raw": 0.0 if mean else 1.0, "sd": 0.0,
                "note": "zero variance across seeds"}
    se = sd / math.sqrt(n)
    t = mean / se
    half = _t_crit(n - 1, alpha) * se
    return {"contrast": label, "pairs": n, "delta": mean,
            "ci_low": mean - half, "ci_high": mean + half,
            "t": float(t), "p_raw": float(2.0 * _t_sf(abs(t), n - 1)),
            "sd": sd, "cohen_dz": float(mean / sd)}


def holm(results: List[dict], alpha: float = 0.05,
         key: str = "p_raw") -> List[dict]:
    """Holm-Bonferroni step-down, applied to one predeclared family."""
    out = [dict(r) for r in results]
    order = sorted(range(len(out)), key=lambda i: out[i][key])
    m = len(out)
    running = 0.0
    for rank, i in enumerate(order):
        adj = min(1.0, (m - rank) * out[i][key])
        running = max(running, adj)              # enforce monotonicity
        out[i]["p_holm"] = running
        out[i]["significant"] = bool(running < alpha)
    for r in out:
        r["family_size"] = m
        r["alpha"] = alpha
    return out


def tost(a: Sequence[float], b: Sequence[float], margin: float,
         label: str = "", alpha: float = 0.05) -> dict:
    """Two one-sided tests. `margin` MUST be declared before seeing results.

    Equivalent means: the paired difference lies entirely inside +/- margin.
    A non-significant difference is NOT equivalence; only this test can
    support that claim.
    """
    if margin <= 0:
        raise ValueError("TOST margin must be positive and predeclared")
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = a - b
    n = len(d)
    mean, sd = float(d.mean()), float(d.std(ddof=1))
    if sd == 0.0:
        equivalent = abs(mean) < margin
        return {"contrast": label, "pairs": n, "delta": mean, "margin": margin,
                "p_tost": 0.0 if equivalent else 1.0, "equivalent": equivalent,
                "note": "zero variance across seeds"}
    se = sd / math.sqrt(n)
    p_lower = _t_sf((mean + margin) / se, n - 1)       # H0: d <= -margin
    p_upper = _t_sf((margin - mean) / se, n - 1)       # H0: d >= +margin
    p = max(p_lower, p_upper)
    return {"contrast": label, "pairs": n, "delta": mean, "margin": margin,
            "p_lower": float(p_lower), "p_upper": float(p_upper),
            "p_tost": float(p), "equivalent": bool(p < alpha)}


def summarise(values: Sequence[float]) -> dict:
    v = np.asarray(values, float)
    return {"n": int(v.size), "mean": float(v.mean()),
            "sd": float(v.std(ddof=1)) if v.size > 1 else 0.0,
            "min": float(v.min()), "max": float(v.max())}


def verdict(result: dict, higher_is_better: bool = True) -> str:
    """Direction-aware label. Never says 'equivalent' from non-significance."""
    if not result.get("significant"):
        return "NO CLEAR DIFFERENCE"
    better = result["delta"] > 0 if higher_is_better else result["delta"] < 0
    return "BETTER" if better else "WORSE"
