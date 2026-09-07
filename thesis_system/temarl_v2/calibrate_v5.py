# -*- coding: utf-8 -*-
"""
TEMARL v5 — environment calibration  (ARCHITECTURE-BLIND)
==========================================================
Removing the goal drift (`profiles_v5.py`) repaired the information structure --
sequence value went from +0.0002 to +0.1776 expected payoff -- but it also
roughly tripled episode length, and DSR saturated at 0.79-0.98.

That is the exact failure `env_v2`'s own pre-registered gate exists to catch:

    validate_environment(): "spread (oracle-random) > 0.08  else FAIL still
    saturated   (v1: all policies 0.90-0.97)"

v1 of this project was REJECTED for saturating DSR. v5 must not ship saturated
either. So the capture race is recalibrated here, against criteria fixed in this
file BEFORE any architecture is trained on v5.

CRITERIA (declared in advance; all computed from BASELINE policies only, so
nothing here can be steered by which architecture wins)

  C1  de-saturated floor  : null-policy DSR in [0.25, 0.40]
                            (env_v2 canonical measures 0.315)
  C2  discriminating      : clairvoyant - random >= 0.15 DSR
                            (env_v2 canonical measures 0.237)
  C3  a history to encode : mean episode length >= 10 steps
                            (env_v2 measures 5.45, which is why attention had
                             almost no positions to attend over; the CAM-LDS
                             source sequences average 15.1 techniques)
  C4  instrument valid    : sequence value (transition - profile) >= 0.03 DSR
                            (env_v2 measures +0.0005, i.e. no instrument at all)

SELECTION RULE, also fixed in advance: among configurations passing C1-C3,
choose the one MAXIMISING C4. Ties broken by larger C2. No architecture is
trained, loaded, or referenced anywhere in this file.

Only two constants move: `goal_steps` (the objective race) and a scalar on
(`cap_p_min`, `cap_p_max`). The payoff matrix, reward weights, vocabulary,
topology generator and observation layout are untouched.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

import numpy as np

import prereg_v4 as PR
from baselines_entity import choose, decision_table
from env_entity import EntityDeceptionEnv
from env_v2 import CAP_P_MAX, CAP_P_MIN
from profiles_v5 import profiles_v5
from train_entity import build_topologies

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results_v5")
LADDER = ("null", "random", "best_fixed", "profile", "transition", "clairvoyant")

C1_LO, C1_HI = 0.25, 0.40
C2_MIN = 0.15
C3_MIN = 10.0
C4_MIN = 0.03


def run(policy, topos, tbl, profs, goal_steps, cap_scale, n_eps, seed):
    env_rng = np.random.default_rng(1_000_000 + seed)
    act_rng = np.random.default_rng(7_000_000 + seed)
    dsr, lens = [], []
    for i in range(n_eps):
        env = EntityDeceptionEnv(topology=topos[i % len(topos)], profiles=profs,
                                 max_steps=PR.MAX_STEPS,
                                 max_entities=PR.MAX_ENTITIES,
                                 seed=int(env_rng.integers(1 << 30)),
                                 cap_p_min=CAP_P_MIN * cap_scale,
                                 cap_p_max=CAP_P_MAX * cap_scale,
                                 goal_steps=goal_steps)
        env.reset()
        done, n = False, 0
        while not done:
            _, _, done, _ = env.step(choose(policy, env, tbl, act_rng))
            n += 1
        dsr.append(1.0 if env.captured else 0.0)
        lens.append(float(n))
    return float(np.mean(dsr)), float(np.mean(lens))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="*", default=[0, 1, 2])
    ap.add_argument("--episodes", type=int, default=120)
    ap.add_argument("--regime", default="B")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    t0 = time.time()
    profs = profiles_v5()
    tbl = decision_table(profs)
    topos = build_topologies(args.regime)

    print("=" * 112)
    print("  TEMARL v5 — CAPTURE CALIBRATION (architecture-blind)")
    print("=" * 112)
    print("  criteria fixed in advance: C1 null DSR in [%.2f,%.2f] | C2 clairv-random"
          " >= %.2f | C3 ep len >= %.0f | C4 seq value >= %.2f"
          % (C1_LO, C1_HI, C2_MIN, C3_MIN, C4_MIN))
    print("  select: among C1-C3 passers, MAXIMISE C4 (sequence value)")
    print("  regime %s, %d seeds x %d episodes\n" % (args.regime, len(args.seeds),
                                                     args.episodes))
    print("  %-6s %-6s %7s %7s %8s %8s %8s %8s %8s %8s   %s"
          % ("goal", "cap x", "null", "random", "bestfix", "profile", "transit",
             "clairv", "ep len", "SEQ VAL", "gates"))
    print("  " + "-" * 108)

    rows = []
    for goal_steps in (3, 4, 5, 6, 8):
        for cap_scale in (0.35, 0.5, 0.7, 1.0):
            vals, lens = {}, {}
            for pol in LADDER:
                d = [run(pol, topos, tbl, profs, goal_steps, cap_scale,
                         args.episodes, s) for s in args.seeds]
                vals[pol] = float(np.mean([x[0] for x in d]))
                lens[pol] = float(np.mean([x[1] for x in d]))
            seq = vals["transition"] - vals["profile"]
            spread = vals["clairvoyant"] - vals["random"]
            eplen = float(np.mean(list(lens.values())))
            c1 = C1_LO <= vals["null"] <= C1_HI
            c2 = spread >= C2_MIN
            c3 = eplen >= C3_MIN
            c4 = seq >= C4_MIN
            gates = "".join(("C%d" % i) if ok else ".."
                            for i, ok in ((1, c1), (2, c2), (3, c3), (4, c4)))
            rows.append({"goal_steps": goal_steps, "cap_scale": cap_scale,
                         **{k: vals[k] for k in LADDER},
                         "ep_len": eplen, "seq_value": seq, "spread": spread,
                         "c1": c1, "c2": c2, "c3": c3, "c4": c4})
            print("  %-6d %-6.2f %7.3f %7.3f %8.3f %8.3f %8.3f %8.3f %8.1f %+8.4f   %s"
                  % (goal_steps, cap_scale, vals["null"], vals["random"],
                     vals["best_fixed"], vals["profile"], vals["transition"],
                     vals["clairvoyant"], eplen, seq, gates))

    ok = [r for r in rows if r["c1"] and r["c2"] and r["c3"]]
    print("\n" + "=" * 112)
    if not ok:
        print("  NO configuration passes C1-C3. The calibration criteria must be")
        print("  revisited BEFORE any architecture is run, and the revision")
        print("  recorded. Do not proceed to training.")
        best = None
    else:
        best = max(ok, key=lambda r: (r["seq_value"], r["spread"]))
        print("  SELECTED: goal_steps=%d  cap_scale=%.2f"
              % (best["goal_steps"], best["cap_scale"]))
        print("     null %.3f | random %.3f | best_fixed %.3f | profile %.3f | "
              "transition %.3f | clairvoyant %.3f"
              % tuple(best[k] for k in LADDER))
        print("     episode length %.1f | spread %.3f | SEQUENCE VALUE %+.4f"
              % (best["ep_len"], best["spread"], best["seq_value"]))
        print("     C4 (seq value >= %.2f): %s"
              % (C4_MIN, "PASS" if best["c4"] else
                 "FAIL - instrument still cannot discriminate; do NOT train"))
        print("\n     for comparison, env_v2/v4 shipped: seq value +0.0005, "
              "episode length 5.45")

    os.makedirs(RESULTS, exist_ok=True)
    with open(os.path.join(RESULTS, "calibration_v5.json"), "w",
              encoding="utf-8") as f:
        json.dump({"architecture_blind": True,
                   "criteria": {"C1": [C1_LO, C1_HI], "C2": C2_MIN,
                                "C3": C3_MIN, "C4": C4_MIN},
                   "selection_rule": "among C1-C3 passers, maximise C4",
                   "grid": rows, "selected": best,
                   "seconds": time.time() - t0}, f, indent=1, default=float)
    print("\n  wrote -> results_v5/calibration_v5.json  (%.0f s)"
          % (time.time() - t0))
    print("=" * 112)


if __name__ == "__main__":
    main()
