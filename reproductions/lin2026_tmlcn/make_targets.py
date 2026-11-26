# -*- coding: utf-8 -*-
"""Writes TARGETS.csv for Lin et al. 2026 (IEEE TMLCN). Every value is typed from the published PDF
(SHA-256 in SOURCES.md): the text of Sections IV-C, VI and VII and Table 6. Figures 6-11 are raster images,
so no value is read off a figure; only numbers printed in the text are targets.

    python reproductions/lin2026_tmlcn/make_targets.py
"""
import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEEDS = "over 10 training seeds"
INT = f"MATCH if the printed integer equals the mode of our per-session maximum tactic, {SEEDS}"
SHARE = f"MATCH if the printed percentage (+-0.5 point) is inside our 95% CI {SEEDS}; CLOSE if within 5 points"
EPISODE = f"MATCH if the printed episode (+-50, the text says 'about') is inside our 95% CI {SEEDS}; CLOSE if within 150"
TACTIC = f"MATCH if the printed tactic (+-0.5) is inside our 95% CI {SEEDS}; CLOSE if within 1 tactic"
SECONDS = f"MATCH if the printed duration (+-10%, the text says 'approximately') is inside our 95% CI {SEEDS}"
RATIO = f"MATCH if our 95% CI of the ratio {SEEDS} lies above the printed bound"
QV = f"MATCH if the printed value (+-0.005) is inside our 95% CI {SEEDS}; CLOSE if within 1.0 (one sustain reward)"

ROWS = [
    # id, where, quantity, published, tolerance, primary
    ("A.static0.ceiling", "Abstract; Sec. VI-B; Fig. 6", "Static0 (unmodified Conpot): tactic level at which the per-session maximum tactic levels off", "4", INT, "yes"),
    ("A.static1.ceiling", "Abstract; Sec. VI-B; Fig. 6", "Static1 (extended Modbus handler): tactic level at which the per-session maximum tactic levels off", "7", INT, "yes"),
    ("A.rl.depth_by_700", "Abstract; Sec. VII", "Dynamic (RL, small state, default alpha 1e-4, gamma 0.90, rho 0.95): smoothed maximum tactic at episode 700 is 10-11 ('reached tactic levels 10-11 within 700 episodes')", "10-11", TACTIC + " (published interval 10-11)", "yes"),
    ("S6B.window1.final_share", "Sec. VI-B; Fig. 8", "Dynamic: share of sessions 1-400 whose final tactic is 11 ('approximately 3%')", "3%", SHARE, "yes"),
    ("S6B.window2.final_share", "Sec. VI-B; Fig. 8", "Dynamic: share of sessions 401-800 whose final tactic is 11", "28%", SHARE, "yes"),
    ("S6B.window3.final_share", "Sec. VI-B; Fig. 8; Sec. VII", "Dynamic: share of sessions 801-1200 whose final tactic is 11", "60%", SHARE, "yes"),
    ("S6B.static0.duration", "Sec. VI-B; Fig. 7", "Static0: average session duration, seconds ('approximately 17')", "17", SECONDS, "no"),
    ("S6B.static1.duration", "Sec. VI-B; Fig. 7", "Static1: average session duration, seconds ('around 40')", "40", SECONDS, "no"),
    ("S6B.rl.duration_final", "Sec. VI-B; Fig. 7", "Dynamic: session duration (moving average) at the end of training, seconds ('surpassing 70')", ">70", "MATCH if our 95% CI of the final moving average " + SEEDS + " lies above 70 s", "no"),
    ("S6B.rl.duration_ratio", "Abstract; Sec. VI-B; Sec. VII", "Dynamic vs static: engagement time 'more than doubles' (abstract: average; Sec. VI-B and VII: median)", ">2x", RATIO + " (reported against Static0 and Static1 separately)", "no"),
    ("S6B.small.surpass_static1", "Sec. VI-B; Fig. 6", "Small-state RL: episode at which the depth curve surpasses Static1 ('around episode 400')", "400", EPISODE, "no"),
    ("S6B.small.near11", "Sec. VI-B; Sec. VI-C; Sec. VII", "Small-state RL: episode by which depth approaches tactic 11 (10-11) ('by episode 1000')", "1000", EPISODE, "no"),
    ("S6B.big.catchup", "Sec. VI-B; Sec. VI-C; Sec. VII", "Big-state RL: episode at which it catches up with small-state ('approximately episode 1400')", "1400", EPISODE, "no"),
    ("S6C.big.cross9_lag", "Sec. VI-C", "Big-state RL crosses tactic 9 about this many episodes after the small-state agent", "300", EPISODE.replace("printed episode", "printed lag"), "no"),
    ("S6C.early_depth", "Sec. VI-C", "Both RL variants during the first 300 episodes typically reach only around tactic", "5", TACTIC, "no"),
    ("S6B.gain_vs_static0", "Sec. VI-B", "After several hundred episodes the adaptive honeypot surpasses Static0 by approximately this many tactics", "6", TACTIC.replace("printed tactic", "printed gain"), "no"),
    ("S6B.gain_vs_static1", "Sec. VI-B", "... and Static1 by", "3", TACTIC.replace("printed tactic", "printed gain"), "no"),
    ("S6D.a1e-3.tactic8_within", "Sec. VI-D; Fig. 10", "alpha 1e-3: episodes needed to reach tactic 8 ('fewer than 150')", "<150", f"MATCH if our 95% CI {SEEDS} lies below 150", "no"),
    ("S6D.a1e-3.oscillation", "Sec. VI-D; Fig. 10", "alpha 1e-3: depth then 'bounces up and down by three tactics' (peak-to-trough, tactics)", "3", TACTIC.replace("printed tactic", "printed swing"), "no"),
    ("S6D.a1e-4.leveloff", "Sec. VI-D; Fig. 10", "alpha 1e-4: episode at which depth levels off ('around episode 800')", "800", EPISODE, "no"),
    ("S6D.rho099.extra_depth", "Sec. VI-D; Fig. 10", "rho 0.99 vs 0.95: final depth higher by about (tactics)", "1", TACTIC.replace("printed tactic", "printed difference"), "no"),
    ("S6D.rho099.explore_ratio", "Sec. VI-D", "rho 0.99 keeps the agent exploring for roughly this many times as many episodes as rho 0.95", "2", "MATCH if the printed ratio (+-0.5) is inside our 95% CI of the ratio of steps until epsilon reaches epsilon_min", "no"),
    ("S6D.gamma095.slowdown", "Sec. VI-D; Fig. 10", "gamma 0.95 vs 0.90: convergence slower by (episodes)", "100-150", EPISODE.replace("printed episode", "printed interval") + " (published interval 100-150)", "no"),
    ("S6D.gamma097.stall", "Sec. VI-D", "pilot gamma 0.97: curve stalls around tactic", "8", TACTIC, "no"),
    ("S6D.stable.tactic10_by800", "Sec. VI-D", "stable profile (alpha 1e-4, gamma 0.90, rho 0.95): consistently achieves tactic 10 within (episodes)", "800", EPISODE, "yes"),
    ("S6D.fast.similar_by300", "Sec. VI-D; Sec. VII", "fast profile (alpha 5e-4, gamma 0.95, rho 0.99): reaches a similar depth in under (episodes)", "<300", f"MATCH if our 95% CI {SEEDS} lies below 300", "no"),
    ("S6D.fast.oscillation", "Sec. VI-D", "fast profile: oscillation after convergence (tactics, +-)", "1", TACTIC.replace("printed tactic", "printed swing"), "no"),
    ("S6D.all_beat_static1_by500", "Sec. VI-D; Sec. VII", "every one of the 16 grid settings surpasses Static1 (tactic 7) within (episodes)", "500", f"MATCH if, for all 16 settings, the upper end of our 95% CI {SEEDS} of the crossing episode is at most 500", "no"),
    ("S6D.dynamic.tactic11_by400", "Sec. VI-D; Sec. VII; Fig. 11", "TD-error-based dynamic learning rate: reaches tactic 11 in roughly (episodes)", "400", EPISODE, "no"),
    ("S7.dynamic.stability", "Sec. VII", "dynamic learning rate: depth stays within (+- tactics) after convergence", "0.5", TACTIC.replace("printed tactic", "printed band"), "no"),
    ("S4C.mapper.accuracy", "Sec. IV-C", "LLM mapper (ChatGPT-4o-mini): correct single-tactic labels on 120 synthetic interactions", ">95%", "MATCH if at least 115 of the 120 cases are correct (needs the authors' 120 cases and prompt)", "no"),
]

TACTICS = ["Initial Access", "Execution", "Persistence", "Privilege escalation", "Evasion", "Discovery",
           "Lateral Movement", "Collection", "C&C", "Inhibit Response Function", "Impair Process Control", "Impact"]
ACTIONS = ["Allow", "Restore", "Delay", "Modify", "Block", "System Error", "Jitter"]
TABLE6 = [  # typed from Table 6, rows = TACTICS, columns = ACTIONS
    [10.08, 2.29, 3.3, 3.53, -4.76, 2.49, 3.18],
    [11.5, 6.97, 2.34, 2.66, -4.6, 9.58, 2.44],
    [11.12, 3.08, 2.53, 4.55, -4.07, -2.12, 2.45],
    [3.65, 1.18, 3.22, 11.79, -3.25, 1.16, 3.14],
    [13.51, 4.05, 2.71, 3.47, -3.25, 0.93, 2.33],
    [14.44, 1.3, 3.51, 5.31, -3.58, 2.94, 3.54],
    [13.55, 5.43, 4.52, 0.31, -4.07, 0.69, 4.74],
    [14.45, 0.18, 2.46, 12.24, -2.34, 1.86, 2.41],
    [12.26, 3.57, 3.73, 5.85, -4.24, 1.17, 3.2],
    [13.71, 5.96, 8.35, 9.94, -4.98, 3.08, 10.51],
    [14.5, 5.35, 10.06, 9.78, -4.96, 7.45, 8.25],
    [-4.99, 11.29, 3.31, 2.02, -4.99, 4.59, 2.1],
]


def slug(s):
    return "".join(ch for ch in s.title() if ch.isalnum())


def rows():
    out = [dict(zip(("id", "table_or_figure", "quantity", "published", "tolerance", "primary"), r)) for r in ROWS]
    for t, vals in zip(TACTICS, TABLE6):
        for a, v in zip(ACTIONS, vals):
            out.append({"id": f"T6.{slug(t)}.{slug(a)}", "table_or_figure": "Table 6",
                        "quantity": f"final Q-value, state '{t}', action '{a}' (configuration not stated)",
                        "published": repr(v), "tolerance": QV, "primary": "no"})
    return out


if __name__ == "__main__":
    data = rows()
    with (HERE / "TARGETS.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(data[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(data)
    print(len(data), "targets,", sum(r["primary"] == "yes" for r in data), "primary")
