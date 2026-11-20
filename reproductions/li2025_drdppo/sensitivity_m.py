# -*- coding: utf-8 -*-
"""Li 2025 DRD-PPO: A12, the declared sensitivity analysis of the paper's readings (DECISIONS.md, A12).

    python reproductions/li2025_drdppo/sensitivity_m.py smoke   # tiny code check, temporary folder
    python reproductions/li2025_drdppo/sensitivity_m.py run     # ONCE: 256 combinations, every one reported

All 2^8 combinations of the readings M1-M8 on the closed calibration's final setting. Nothing is selected and no
REPORT.md verdict changes. Null-fit rule: a combination fits a triple if mean Alg1, Alg3 and DRD-PPO are each
within 2 points; the real triple (28.43, 55.19, 97.09) is compared with three decoys fixed before any run.
Trials whose outcome cannot depend on a reading are run once and shared (a random policy's success does not
depend on R1 or on when cost is charged; Alg3 and DRD-PPO do not depend on the Alg1 reading; ties do not matter
for the proportional attacker).
"""
from __future__ import annotations

import argparse
import csv
import dataclasses
import itertools
import json
import os
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import calibrate as C  # noqa: E402
import drdppo as D  # noqa: E402

OUT = HERE / "out"
FACTORS = (("attacker", ("argmax", "proportional")), ("ties", ("random", "real_first")),
           ("alg1", ("walk", "config")), ("action", ("single", "joint")), ("cost", ("step", "final")),
           ("R1", (10.0, 100.0)), ("f_score", ("none", "host_clone")), ("h_links", ("f_only", "f_plus_server")))
REAL = (28.43, 55.19, 97.09)                              # Table 3: Alg1, Alg3, DRD-PPO
DECOYS = ((51.17, 84.51, 99.00), (39.70, 34.60, 75.48), (8.24, 75.21, 99.00))   # A12, drawn before any run
FIT = 2.0
POLICIES = ("alg1", "alg3", "drdppo")
LOG = "sensitivity_m_log.csv"


def combos(base: D.Setting) -> list:
    names = [f for f, _ in FACTORS]
    return [D.Setting(**{**dataclasses.asdict(base), **dict(zip(names, vals))})
            for vals in itertools.product(*[v for _, v in FACTORS])]


def effective(s: D.Setting, policy: str) -> D.Setting:
    """The same setting with every reading that cannot change this policy's outcome set to its default."""
    kw = dataclasses.asdict(s)
    if kw["attacker"] == "proportional":
        kw["ties"] = "random"
    if policy != "alg1":
        kw["alg1"] = "walk"
    if policy in ("alg1", "alg3"):
        kw["cost"], kw["R1"] = "step", 10.0
    return D.Setting(**kw)


def read_log(out: Path) -> dict:
    p = out / LOG
    if not p.exists():
        return {}
    with p.open(encoding="utf-8") as fh:
        return {(r["setting"], r["policy"], int(r["seed"]), int(r["episodes"])): r for r in csv.DictReader(fh)}


def append(out: Path, rows):
    p = out / LOG
    new = not p.exists()
    out.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=C.LOG_FIELDS)
        if new:
            w.writeheader()
        w.writerows(rows)


def run(out: Path, workers: int, base: D.Setting, seeds=C.SEEDS, episodes: int = 500, heldout_eps=(500, 1500)) -> dict:
    all_c = combos(base)
    need = {}
    for s in all_c:
        for p in POLICIES:
            e = effective(s, p)
            need[(e.key(), p)] = e
    log = read_log(out)
    todo = [("sens_m", dataclasses.asdict(e), p, sd, episodes, 0) for (k, p), e in need.items() for sd in seeds
            if (k, p, sd, episodes) not in log]
    print(f"A12: {len(all_c)} combinations, {len(need)} distinct (setting, policy) pairs, {len(todo)} new trials, "
          f"{workers} workers", flush=True)
    if todo:
        rows = []
        with ProcessPoolExecutor(max_workers=workers) as ex:
            for i, row in enumerate(ex.map(C._job, todo), 1):
                rows.append(row)
                if i % 50 == 0 or i == len(todo):
                    print(f"  {i}/{len(todo)}", flush=True)
                    append(out, rows)
                    rows = []
        log = read_log(out)
    table = []
    for i, s in enumerate(all_c):
        m = {p: C.summary([float(log[(effective(s, p).key(), p, sd, episodes)]["dsp_train"]) for sd in seeds]) for p in POLICIES}
        means = tuple(m[p]["mean"] for p in POLICIES)
        fits = lambda tri: all(abs(a - b) <= FIT for a, b in zip(means, tri))
        table.append({"i": i, "readings": {f: getattr(s, f) for f, _ in FACTORS}, "means": dict(zip(POLICIES, means)),
                      "ci": {p: m[p]["ci"] for p in POLICIES}, "fits_real": fits(REAL),
                      "fits_decoy": [fits(d) for d in DECOYS],
                      "distance_real": float(np.sqrt(sum((a - b) ** 2 for a, b in zip(means, REAL))))})
    n_real = sum(r["fits_real"] for r in table)
    n_decoy = [sum(r["fits_decoy"][j] for r in table) for j in range(len(DECOYS))]
    if n_real == 0:
        reading = "Table 3 is not produced by any of these 256 readings of the paper."
    elif max(n_decoy) >= n_real:
        reading = ("The readings are flexible enough to fit nearby arbitrary numbers: a fit does not identify the "
                   "paper's mechanics.")
    else:
        reading = ("Candidate readings consistent with Table 3 (never 'reproduced'); held-out targets run once, "
                   "descriptively, for them only.")
    held = {}
    if n_real and max(n_decoy) < n_real:
        for r in [r for r in table if r["fits_real"]]:
            s = all_c[r["i"]]
            jobs = [("sens_m_heldout", dataclasses.asdict(effective(s, "drdppo")), "alg2", sd, heldout_eps[0], heldout_eps[0]) for sd in seeds]
            jobs += [("sens_m_heldout", dataclasses.asdict(effective(s, "drdppo")), "drdppo", sd, heldout_eps[1], heldout_eps[1]) for sd in seeds]
            with ProcessPoolExecutor(max_workers=workers) as ex:
                rows = list(ex.map(C._job, jobs))
            append(out, rows)
            held[r["i"]] = {"alg2_500": C.summary([x["dsp_train"] for x in rows if x["policy"] == "alg2"]),
                            "drdppo_1500": C.summary([x["dsp_train"] for x in rows if x["policy"] == "drdppo"])}
    marg = {}
    for f, vals in FACTORS:
        marg[f] = {str(v): {p: float(np.mean([r["means"][p] for r in table if r["readings"][f] == v])) for p in POLICIES}
                   for v in vals}
    best = sorted(table, key=lambda r: r["distance_real"])[:10]
    return {"base": dataclasses.asdict(base), "real": REAL, "decoys": DECOYS, "fit_points": FIT,
            "n_combinations": len(table), "n_fit_real": n_real, "n_fit_decoys": n_decoy, "reading": reading,
            "closest_10_to_real": best, "marginal_means_by_reading": marg, "heldout_descriptive": held,
            "table": table, "seeds": list(seeds), "episodes": episodes, "git_head": C.git_head()}


def write_md(res: dict, dest: Path):
    L = ["# Li 2025 DRD-PPO: sensitivity analysis of the paper's readings (A12)", "",
         "Declared in DECISIONS.md A12 before any code or run. All 2^8 combinations of the readings M1-M8, each run once",
         "(10 seeds x 500 episodes), on the closed calibration's final setting. Nothing is selected; REPORT.md's verdicts",
         "do not change.", "",
         f"**Result:** {res['reading']}", "",
         f"- Combinations within {res['fit_points']:.0f} points of the real triple (Alg1 28.43, Alg3 55.19, DRD-PPO 97.09): "
         f"**{res['n_fit_real']} of {res['n_combinations']}**.",
         f"- Within {res['fit_points']:.0f} points of the decoys D1-D3: {res['n_fit_decoys']}.", "",
         "## The 10 combinations closest to Table 3 (descriptive)", "",
         "| attacker | ties | alg1 | action | cost | R1 | F score | H links | Alg1 | Alg3 | DRD-PPO | distance |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in res["closest_10_to_real"]:
        g, m = r["readings"], r["means"]
        L.append(f"| {g['attacker']} | {g['ties']} | {g['alg1']} | {g['action']} | {g['cost']} | {g['R1']:g} | {g['f_score']} | "
                 f"{g['h_links']} | {m['alg1']:.2f} | {m['alg3']:.2f} | {m['drdppo']:.2f} | {r['distance_real']:.2f} |")
    L += ["", "## Mean of each outcome by reading (over the 128 combinations with that reading)", "",
          "| reading | value | Alg1 | Alg3 | DRD-PPO |", "|---|---|---|---|---|"]
    for f, d in res["marginal_means_by_reading"].items():
        for v, m in d.items():
            L.append(f"| {f} | {v} | {m['alg1']:.2f} | {m['alg3']:.2f} | {m['drdppo']:.2f} |")
    if res["heldout_descriptive"]:
        L += ["", "## Held-out targets for the candidate readings (descriptive, once)", ""]
        for i, h in res["heldout_descriptive"].items():
            L.append(f"- combination {i}: Alg2 {h['alg2_500']['mean']:.2f} (98.31), DRD-PPO 1,500 episodes "
                     f"{h['drdppo_1500']['mean']:.2f} (98.61)")
    L += ["", "Every trial: `out/sensitivity_m_log.csv`; every combination: `out/sensitivity_m.json`.", ""]
    dest.write_text("\n".join(L), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=["smoke", "run"])
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    a = ap.parse_args()
    t0 = time.time()
    held = json.loads((OUT / "heldout.json").read_text(encoding="utf-8"))
    base = D.Setting(**held["final_setting"])
    if a.stage == "smoke":
        global FACTORS
        FACTORS = FACTORS[:3] + tuple((f, v[:1]) for f, v in FACTORS[3:])           # 8 combinations
        with tempfile.TemporaryDirectory() as tmp:
            res = run(Path(tmp), a.workers, base, seeds=(0, 1), episodes=4, heldout_eps=(4, 5))
            write_md(res, Path(tmp) / "SENSITIVITY_M.md")
        print(f"smoke OK ({res['n_combinations']} combinations) in {time.time() - t0:.0f} s; nothing kept")
        return
    if (OUT / "sensitivity_m.json").exists():
        raise SystemExit("A12 has already run; it runs once")
    if not C.committed_unchanged(HERE / "DECISIONS.md"):
        raise SystemExit("DECISIONS.md (A12) must be committed and unchanged before the run")
    res = run(OUT, a.workers, base)
    C.D_write(OUT / "sensitivity_m.json", res)
    write_md(res, HERE / "SENSITIVITY_M.md")
    print(f"A12 finished in {(time.time() - t0) / 60:.1f} min: {res['reading']} "
          f"(real fits {res['n_fit_real']}/{res['n_combinations']}, decoy fits {res['n_fit_decoys']})")


if __name__ == "__main__":
    main()
