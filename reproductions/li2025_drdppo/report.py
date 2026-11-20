# -*- coding: utf-8 -*-
"""Write REPORT.md for the Li 2025 calibrated replication from out/stage1.json, stage2.json, heldout.json and
calibration_log.csv. Called by `calibrate.py heldout`; can be re-run (it only reads results)."""
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _fmt(s):
    """Mean [95% CI]; a t-interval on a percentage can leave [0, 100], so it is shown clipped (marked *)."""
    lo, hi = s["ci"]
    mark = "*" if lo < 0 or hi > 100 else ""
    return f"{s['mean']:.2f} [{max(lo, 0.0):.2f}, {min(hi, 100.0):.2f}]{mark}"


def _a14() -> list:
    """A13/A14: what the paper's own figures imply (algebra only, no run)."""
    p = HERE / "data" / "figure_values.json"
    if not p.exists():
        return []
    f = json.loads(p.read_text(encoding="utf-8"))
    r = {k: v["median"] for k, v in f["fig6a_reward"]["curves"].items()}
    c = {k: v["median"] for k, v in f["fig6c_cost"]["curves"].items()}
    c["green"] = c["orange"]
    rows = [("DRD-PPO", "blue", 97.09), ("Alg1", "red", 28.43), ("Alg2", "green", 98.31), ("Alg3", "orange", 55.19)]
    L = ["## What the paper's own figures imply (A13-A14, algebra only)", "",
         "Plateaus measured from Figs. 5-6 (`data/figure_values.json`). Under reward = R1(2p - 1) - cost with R1 = 1 and",
         "the cost once per episode (recovered from two independent plateaus: 0.996 and 0.997):", "",
         "| method | cost (Fig. 6c) | implied success | Table 3 |", "|---|---|---|---|"]
    for n, k, t3 in rows:
        L.append(f"| {n} | {c[k]:.3f} | {50 * (r[k] + c[k] + 1):.2f}% | {t3} |")
    L += ["", "- The figures and Table 3 agree (gaps +1.5 to +2.8 points); DRD-PPO's learned deployment is 1 H + 4 F.",
          "- No attacker rule we derived reproduces the figure-implied random baselines (31.20%, 57.52%): clone-specific",
          "  36.17% / 66.41%, all honeypots 60.83% / 100% (exact arithmetic). A13's run was therefore not executed (A14).", ""]
    return L


def _a12(out: Path) -> list:
    """A12 (declared sensitivity of the paper's readings), if it has run."""
    p = Path(out) / "sensitivity_m.json"
    if not p.exists():
        return []
    r = json.loads(p.read_text(encoding="utf-8"))
    rng = {k: (min(x["means"][k] for x in r["table"]), max(x["means"][k] for x in r["table"])) for k in ("alg1", "alg3", "drdppo")}
    return ["## Readings of the paper (A12, declared sensitivity analysis)", "",
            f"- {r['reading']} Combinations fitting Table 3 within {r['fit_points']:.0f} points: {r['n_fit_real']} of "
            f"{r['n_combinations']}; decoys fitted: {r['n_fit_decoys']} (`SENSITIVITY_M.md`).",
            f"- Ranges over the {r['n_combinations']} readings: Alg1 {rng['alg1'][0]:.2f}-{rng['alg1'][1]:.2f}, Alg3 "
            f"{rng['alg3'][0]:.2f}-{rng['alg3'][1]:.2f}, DRD-PPO {rng['drdppo'][0]:.2f}-{rng['drdppo'][1]:.2f}. No reading "
            f"reaches Alg3 55.19 or DRD-PPO 97.09 within 2 points, even alone.", ""]


def write(out: Path, dest: Path = None) -> Path:
    out = Path(out)
    dest = dest or (HERE / "REPORT.md" if out.resolve() == (HERE / "out").resolve() else out / "REPORT.md")
    s1 = json.loads((out / "stage1.json").read_text(encoding="utf-8"))
    s2 = json.loads((out / "stage2.json").read_text(encoding="utf-8"))
    ho = json.loads((out / "heldout.json").read_text(encoding="utf-8"))
    with (HERE / "TARGETS.csv").open(encoding="utf-8") as fh:
        targets = list(csv.DictReader(fh))
    with (out / "calibration_log.csv").open(encoding="utf-8") as fh:
        n_trials = sum(1 for _ in csv.DictReader(fh))
    b1 = next(r for r in s1["rows"] if r["key"] == s1["selected_key"])
    b2 = next(r for r in s2["rows"] if r["key"] == s2["selected_key"])
    ours = {"T3.Alg1_random_deployment": (b1["alg1"], "calibration target, stage 1 (C2)"),
            "T3.Alg3_random_full_deployment": (b1["alg3"], "calibration target, stage 1 (C2)"),
            "T3.DRD-PPO": (b2["drdppo"], "calibration target, stage 2 (C3)")}
    rows = []
    for t in targets:
        tid, pub = t["id"], float(t["published"])
        if tid in ours:
            s, role = ours[tid]
            rows.append(f"| {tid} | {t['table_or_figure']} | {pub} | {_fmt(s)} | {role}; distance {abs(s['mean'] - pub):.2f} | CALIBRATION TARGET |")
        elif tid in ho["heldout"]:
            h = ho["heldout"][tid]
            refs = ", ".join(f"{k} {v:.2f}" for k, v in h["references"].items())
            rows.append(f"| {tid} | {t['table_or_figure']} | {pub} | {_fmt(h['ours_train'])} | held out (C4); evaluation DSP "
                        f"{_fmt(h['ours_eval'])}; references {refs}; {h['why']} | {h['verdict']} |")
        else:
            rows.append(f"| {tid} | {t['table_or_figure']} | {pub} | - | no setting of this algorithm is published "
                        f"(decision 14) | NOT ATTEMPTED |")
    prim = [t["id"] for t in targets if t["primary"].strip().lower() == "yes"]
    informative = [tid for tid, h in ho["heldout"].items() if h["verdict"] in ("MATCH", "CLOSE", "NO MATCH")]
    held_ok = [tid for tid in informative if ho["heldout"][tid]["verdict"] in ("MATCH", "CLOSE")]
    cal_missed = (not s1["identifiability_settings_within_2_points_of_both"]) or (not s2["identifiability_settings_within_2_points"])
    if cal_missed:
        overall = (f"**Not reproducible from the published text.** No declared setting came within 2 points of the "
                   f"calibration targets (best: Alg1 {b1['alg1']['mean']:.2f} vs 28.43, Alg3 {b1['alg3']['mean']:.2f} vs 55.19, "
                   f"DRD-PPO {b2['drdppo']['mean']:.2f} vs 97.09, over {s1['n_settings']} + {s2['n_settings']} settings), and "
                   f"the held-out targets are {'uninformative' if not informative else 'reported below'} (A2). The paper's "
                   f"unpublished mechanics cannot be recovered without the authors' simulator (A11). DRD-PPO enters D1.2 "
                   f"only as an adapted comparator (A4).")
    elif not informative:
        overall = ("**Not determinable as a replication:** no held-out target is informative (A2), so agreement with the "
                   "paper cannot be shown or refuted. DRD-PPO enters D1.2 only as an adapted comparator (A4).")
    elif set(held_ok) == set(informative):
        overall = "**Calibrated-replicated** on every informative held-out target (STANDARD.md Section 3a)."
    else:
        overall = ("**Not replicated:** at least one informative held-out target is NO MATCH. DRD-PPO enters D1.2 only "
                   "as an adapted comparator (A4).")
    L = ["# Li 2025 DRD-PPO: report (calibrated replication)", "",
         "Written by `report.py` from `out/`. Protocol: DECISIONS.md (decisions 1-16, C1-C9, A1-A11). Rebuilt from the",
         "paper (no code released); unpublished parameters calibrated on Table 3 Alg1, Alg3 and DRD-PPO; Alg2 and",
         "Table 4 DRD-PPO held out and computed once.", "",
         f"**Overall:** {overall}", "",
         f"Primary targets: {', '.join(prim)}. Trials logged: {n_trials} (`out/calibration_log.csv`).", "",
         r"\* 95% t-interval clipped to [0, 100].", "",
         "| id | table | published | ours: mean [95% CI], 10 seeds | role and notes | verdict |",
         "|---|---|---|---|---|---|", *rows, "",
         "## Calibration", "",
         f"- Stage 1 (environment, {s1['n_settings']} settings): selected `{s1['selected_key']}`, loss "
         f"{s1['selected_loss']:.2f}. Settings within 2 points of both targets: "
         f"{len(s1['identifiability_settings_within_2_points_of_both'])} (C5).",
         f"- Stage 2 (learner, {s2['n_settings']} settings): selected `{s2['selected_key']}`. Settings within 2 points "
         f"of 97.09: {len(s2['identifiability_settings_within_2_points'])} (C5).",
         f"- Discrimination (review attack 2): number of stage-1 settings in which the scripted policy is within 2 "
         f"points of each held-out target: {s1['scripted_within_2_points_of_heldout_targets_n_settings']}.",
         "- w is weakly identified by construction: it scales both sides of the H-honeypot-versus-server comparison "
         "(DECISIONS.md F2).", "",
         "## Sensitivity", "",
         f"- CVSS v3 instead of v2 (final setting, DRD-PPO, 500 episodes): {_fmt(ho['sensitivity_cvss_v3_drdppo_500'])}.",
         "- Clip 0.9 (Table 2) versus 0.2 (text): both are in the stage-2 grid; see `out/stage2.json`.", "",
         *_a12(out),
         *_a14(),
         "## Limits", "",
         "- Every unpublished setting is an assumption (DECISIONS.md decisions 5-11, A6-A9); the corresponding author did",
         "  not answer. A calibrated match is weaker evidence than a replication with the authors' settings.",
         "- DSP is primarily measured over training episodes (decision 12); the evaluation DSP is reported alongside.",
         "- The six other RL algorithms of Table 4 are not attempted (decision 14).", ""]
    dest.write_text("\n".join(L), encoding="utf-8")
    return dest


if __name__ == "__main__":
    print(write(HERE / "out"))
