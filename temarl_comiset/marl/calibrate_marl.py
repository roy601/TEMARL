# -*- coding: utf-8 -*-
"""
TEMARL v7 — architecture-blind calibration of the free environment parameters
============================================================================
Three parameters of `env_marl` are not measured from data: the exposure hazard
scale beta and the movement probabilities p_goal / p_stay. (K = 2 and the
objective rule G = 1 are fixed by design; see DESIGN.md.) They are chosen here,
once, by a rule written before any cell was scored:

  GRID       beta in {0.2, 0.4} x p_goal in {0.5, 0.7} x p_stay in {0.6, 0.8}
  SCORE      gates G1-G4 of `gates_marl.py`, computed from the reference ladder
             only -- no neural network and no learned arm is involved, so the
             choice cannot favour any history encoder
  SELECTION  among the cells that pass G1-G4, the one with the SMALLEST
             coordination value (G2), i.e. the most conservative setting for
             the MARL claim; ties -> the smallest sequence value (G4)
  FAILURE    if no cell passes, nothing is chosen and the pipeline stops. The
             grid is not widened after seeing the scores.

The whole grid is written to results_marl/calibration_grid.json and reported.
The chosen cell is frozen to env_config.json; the final gates are then re-run
on a DISJOINT episode stream (gates_marl.py, seed 1) so the selection cannot
flatter them.
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import sys
import time

import _frozen
from baselines_marl import ladder
from env_marl import SCRIPT_IDS, EnvConfig
from gates_marl import THRESHOLDS, file_sha, gates_g1_g4, print_gates

GRID = {"beta": (0.2, 0.4), "p_goal": (0.5, 0.7), "p_stay": (0.6, 0.8)}
FIXED = {"k_capacity": 2, "goal_steps": 1}
HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-sel", type=int, default=400)
    ap.add_argument("--n-eval", type=int, default=1000)
    ap.add_argument("--n-fixed-sel", type=int, default=150)
    ap.add_argument("--out-dir", default=os.path.join(HERE, "results_marl"))
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    os.makedirs(args.out_dir, exist_ok=True)

    print("=" * 110)
    print("  TEMARL v7 — CALIBRATION (architecture-blind; rule fixed in source)")
    print("  thresholds %s" % THRESHOLDS)
    print("  calibrate %s | gates %s | frozen %s"
          % (file_sha(__file__), file_sha(os.path.join(HERE, "gates_marl.py")),
             _frozen.fingerprint()))
    print("=" * 110)
    cells = []
    for beta, pg, ps in itertools.product(*GRID.values()):
        cfg = EnvConfig(beta=beta, p_goal=pg, p_stay=ps, **FIXED)
        t0 = time.time()
        lad = ladder(cfg, SCRIPT_IDS, n_sel=args.n_sel, n_eval=args.n_eval,
                     n_fixed_sel=args.n_fixed_sel, seed=0)
        g = gates_g1_g4(lad)
        ok = all(g[k]["pass"] for k in ("G1", "G2", "G3", "G4"))
        print("\n  cell beta=%.1f p_goal=%.1f p_stay=%.1f   %s   (%.0f s)"
              % (beta, pg, ps, "PASSES G1-G4" if ok else "fails", time.time() - t0))
        print_gates(g)
        cells.append({"config": cfg.to_dict(), "gates": g, "pass": ok,
                      "summary": lad["summary"], "meta": lad["meta"]})

    passing = [c for c in cells if c["pass"]]
    chosen = None
    if passing:
        chosen = min(passing, key=lambda c: (c["gates"]["G2"]["coordination_rel"],
                                             c["gates"]["G4"]["sequence_rel"]))
    prov = {"calibrate_sha": file_sha(__file__),
            "gates_sha": file_sha(os.path.join(HERE, "gates_marl.py")),
            "frozen": _frozen.fingerprint(),
            "date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "grid": GRID, "fixed": FIXED, "thresholds": THRESHOLDS,
            "n_sel": args.n_sel, "n_eval": args.n_eval,
            "n_fixed_sel": args.n_fixed_sel}
    json.dump({"provenance": prov, "cells": cells,
               "chosen": chosen["config"] if chosen else None},
              open(os.path.join(args.out_dir, "calibration_grid.json"), "w",
                   encoding="utf-8"), indent=1, default=float)
    print("\n" + "=" * 110)
    print("  %d / %d cells pass G1-G4" % (len(passing), len(cells)))
    if not chosen:
        print("  NO CELL PASSES. Nothing is chosen; the pipeline stops here.")
        print("=" * 110)
        sys.exit(1)
    print("  CHOSEN (smallest coordination value among passing cells): %s"
          % chosen["config"])
    json.dump({"config": chosen["config"], "provenance": prov},
              open(os.path.join(HERE, "env_config.json"), "w", encoding="utf-8"),
              indent=1)
    print("  wrote env_config.json and results_marl/calibration_grid.json")
    print("=" * 110)


if __name__ == "__main__":
    main()
