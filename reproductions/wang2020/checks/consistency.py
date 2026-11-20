# -*- coding: utf-8 -*-
"""Internal-consistency checks of Wang et al. 2020's published numbers, before any code of ours (DECISIONS.md F1-F6).

    python reproductions/wang2020/checks/consistency.py      # reads data/figure_values.json, writes data/consistency.json

Only the paper's own numbers are used (measured by extract_figures.py). Each check states what the paper's
text implies and whether the figures agree. Table 3 gives "total number of experiments 1000", so a plotted
dsp is a proportion out of 1000 and its binomial standard error is sqrt(p(1-p)/1000).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
FIG = json.loads((ROOT / "data" / "figure_values.json").read_text(encoding="utf-8"))
OUT = ROOT / "data" / "consistency.json"
N = 1000
# Fig. 10's static policies, numbered in lexicographic order of the location pairs (DECISIONS.md D3)
PAIRS = [(a, b) for a in range(1, 8) for b in range(a + 1, 8)]


def ys(panel):
    return np.array([FIG[panel]["curves"][s]["y"] for s in FIG["legend"]])      # settings x points


def dispersion(groups):
    """Pearson chi-square of replicate proportions around their group mean, binomial variance at N."""
    x2, df = 0.0, 0
    for g in groups:
        g = np.asarray(g, float)
        p = g.mean()
        x2 += float(((g - p) ** 2).sum() / (p * (1 - p) / N))
        df += len(g) - 1
    return {"chi2": x2, "df": df, "p_value": float(stats.chi2.sf(x2, df)), "implied_experiments_per_point": N * df / x2}


def main():
    res = {}
    s10, s11, s12, s13 = ys("fig10_static"), ys("fig11_random_dynamic"), ys("fig12_following_alarm"), ys("fig13_q_learning")

    # F1. A static policy does not read alarms, so Fig. 10's four FNR/FPR curves are four replicates of the same
    #     21 numbers. Their spread should be binomial at 1000 experiments. Fig. 12's ten repeats per setting are
    #     the same kind of replicate and serve as the control.
    res["F1_fig10_static_across_settings"] = dispersion(s10.T)
    res["F1_fig12_following_alarm_within_setting"] = dispersion(s12)
    res["F1_fig13_q_learning_final_across_settings"] = dispersion([s13[:, -1]])

    # F2. Fig. 11 (random-dynamic, Eq. 4: a new random element of AD at every time t). If every one of the 1000
    #     experiments draws its own random deployments, the ten repeats differ only by binomial noise.
    res["F2_fig11_within_setting"] = dispersion(s11)
    #     Two readings remain: (a) one random STATIC deployment per experiment, (b) one random SEQUENCE A_t per
    #     experiment, used for all its attacks. Under (a) every Fig. 11 value is near one of Fig. 10's 21 values
    #     and the Fig. 11 mean is near the mean of the 21; under (b) the mean is near the untrained Q-learner's
    #     dsp (Fig. 13 at 0 steps, a fresh random choice at every step) and values between the static ones occur.
    mean10 = s10.mean(0)
    n_eff = res["F1_fig10_static_across_settings"]["implied_experiments_per_point"]
    for label, n in (("binomial_1000", N), ("fig10_own_spread", n_eff)):
        se = np.sqrt(np.clip(mean10 * (1 - mean10), 1e-9, None) / (4 * n))
        far = [float(v) for v in s11.ravel() if np.min(np.abs(v - mean10) / np.sqrt(se ** 2 + v * (1 - v) / n)) > 3]
        res[f"F2_fig11_values_far_from_every_static_policy_{label}"] = {
            "count": len(far), "of": int(s11.size), "values": sorted(round(v, 3) for v in far),
            "rule": f"more than 3 SE from all 21 static-policy means of Fig. 10 (noise of {n:.0f} experiments per point)"}
    m11, se11 = float(s11.mean()), float(s11.std(ddof=1) / np.sqrt(s11.size))
    res["F2_fig11_mean"] = {"mean": round(m11, 4), "se": round(se11, 4),
                            "z_vs_mean_of_21_static_reading_a": round((m11 - float(mean10.mean())) / se11, 2),
                            "z_vs_untrained_q_reading_b": round((m11 - float(s13[:, 0].mean())) / se11, 2)}

    # F3. Location 7 = the data server (Table 2's H7; the attacker's goal), so a decoy behind it is never
    #     reached: policy (x, 7) should equal "one decoy at x". Adding a decoy can only add a way to succeed and
    #     two decoys succeed no more often than the two single decoys added: max(s_a, s_b) <= dsp(a, b) <= s_a + s_b.
    single = {a: (mean10[PAIRS.index((a, 7))], s10[:, PAIRS.index((a, 7))].std(ddof=1) / 2) for a in range(1, 7)}
    rows, viol = [], 0
    for i, (a, b) in enumerate(PAIRS):
        if b == 7:
            continue
        v, sv = mean10[i], s10[:, i].std(ddof=1) / 2
        lo, hi = max(single[a][0], single[b][0]), single[a][0] + single[b][0]
        tol = 2 * np.sqrt(sv ** 2 + max(single[a][1], single[b][1]) ** 2)
        ok = lo - tol <= v <= hi + tol
        viol += not ok
        rows.append({"policy": i + 1, "pair": [a, b], "dsp": round(float(v), 4), "lower_max_single": round(float(lo), 4),
                     "upper_sum_single": round(float(hi), 4), "within_2se": bool(ok)})
    lowest = [all(mean10[PAIRS.index((a, 7))] <= mean10[PAIRS.index((a, b))] + 0.02 for b in range(a + 1, 7))
              for a in range(1, 7)]
    res["F3_fig10_union_bounds"] = {"singletons_from_(x,7)": {a: round(float(v[0]), 4) for a, v in single.items()},
                                    "pairs_checked": len(rows), "violations_at_2se": viol,
                                    "(x,7)_lowest_in_its_block_within_0.02": lowest, "rows": rows}

    # F4. The text's numbers against the figures.
    best = int(np.argmax(mean10))
    res["F4_text_vs_figures"] = {
        "best_static_text_75.6": {"policy1_by_setting": [round(float(v), 4) for v in s10[:, 0]],
                                  "policy1_mean": round(float(mean10[0]), 4),
                                  "best_policy_by_mean": best + 1, "best_mean": round(float(mean10[best]), 4),
                                  "largest_single_point": round(float(s10.max()), 4)},
        "random_dynamic_text_max_75_min_15.8": {"max": round(float(s11.max()), 4), "min": round(float(s11.min()), 4)},
        "q_learning_text_nearly_80": {"at_30000_by_setting": [round(float(v), 4) for v in s13[:, -1]],
                                      "mean": round(float(s13[:, -1].mean()), 4)},
        "following_alarm_means_by_setting": [round(float(v), 4) for v in s12.mean(1)],
    }

    # F5. Untrained Q-learning (Fig. 13, 0 steps; Algorithm 1 starts from Q = 0) against the reference policies.
    res["F5_q_learning_start"] = {"at_0_steps_by_setting": [round(float(v), 4) for v in s13[:, 0]],
                                  "mean_of_21_static": round(float(mean10.mean()), 4),
                                  "static_policy_1_mean": round(float(mean10[0]), 4),
                                  "fig11_random_dynamic_mean": round(float(s11.mean()), 4)}

    # F6. Training time (Fig. 14): seconds per training step.
    t = np.array([FIG["fig14_training_time"]["curves"][s]["y"] for s in FIG["legend"]])
    res["F6_seconds_per_training_step_at_30000"] = [round(float(v / 30000), 3) for v in t[:, -1]]

    OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
    for k, v in res.items():
        if k == "F3_fig10_union_bounds":
            v = {kk: vv for kk, vv in v.items() if kk != "rows"}
        print(k, json.dumps(v))


if __name__ == "__main__":
    main()
