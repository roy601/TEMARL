# -*- coding: utf-8 -*-
"""
TEMARL v5 — PPO update A/B  (ARCHITECTURE-BLIND)
=================================================
Trains ONLY the GRU. No Transformer is built, loaded or referenced, so nothing
here can be steered by which architecture wins.

QUESTION
--------
The v3/v4 update collapsed `rollout`'s per-agent log-prob and value tensors
(shape [n_agents]) with `.mean()` into one scalar per timestep. That makes the
PPO importance ratio

    exp( mean_a [ logp_new(a) - logp_old(a) ] )

i.e. the geometric mean of the four agents' ratios rather than a per-sample
ratio. Clipping at 0.2 then constrains the AVERAGE, so the effective per-agent
trust region is much tighter than intended; and all four agents receive
identical credit even though only the agent owning the entered zone affects
alignment.

Does treating each (timestep, agent) as its own PPO sample -- the standard
IPPO/MAPPO treatment -- let the learner reach the memoryless baseline it failed
to reach in v4 and in the first v5 sweep?

Reference points, regime B (`results_v5/baselines_v5.json`):
    random 0.4935 | best_fixed 0.5475 | transition oracle 0.6390

First v5 sweep, on the OLD update: 240 eps -> 0.510, 1200 eps -> 0.523.
Both below best_fixed, i.e. worse than ignoring the attacker entirely.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

import numpy as np

import prereg_v5 as P5
from train_entity_v5 import (RESULTS, build_topologies, evaluate,
                             pretrain_history, train_arm)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="*", default=[0, 1])
    ap.add_argument("--updates", type=int, default=60)
    ap.add_argument("--batch-eps", type=int, default=8)
    ap.add_argument("--eval", type=int, default=150)
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    with open(os.path.join(RESULTS, "baselines_v5.json"), encoding="utf-8") as f:
        b = json.load(f)["results"]["B"]
    rnd = b["random"]["dsr_mean"]
    bf = b["best_fixed"]["dsr_mean"]
    orc = b["transition"]["dsr_mean"]

    topos = build_topologies("B")
    print("=" * 96)
    print("  TEMARL v5 — PPO UPDATE A/B  (GRU only, architecture-blind)")
    print("=" * 96)
    print("  reference: random %.4f | best_fixed %.4f | transition oracle %.4f"
          % (rnd, bf, orc))
    print("  budget: %d updates x %d episodes = %d episodes, %d seeds\n"
          % (args.updates, args.batch_eps, args.updates * args.batch_eps,
             len(args.seeds)))
    print("  %-34s %10s %12s %10s %8s"
          % ("PPO update", "DSR", "vs best_fix", "capture", "sec"))
    print("  " + "-" * 82)

    out = {}
    for label, per_agent in (("v4: agent-averaged scalar", False),
                             ("v5: per-agent samples", True)):
        t0, dsrs = time.time(), []
        for seed in args.seeds:
            enc = pretrain_history("GRU", P5.OBJECTIVE, seed, topos)
            net = train_arm(enc, "DeepSets", topos, seed, args.updates,
                            args.batch_eps, per_agent=per_agent)
            dsrs.append(evaluate(net, enc, topos, args.eval, seed)["dsr"])
        m = float(np.mean(dsrs))
        cap = 100.0 * (m - bf) / (orc - bf)
        out[label] = {"dsr": m, "per_seed": dsrs, "capture_pct": cap,
                      "seconds": time.time() - t0}
        print("  %-34s %10.4f %+12.4f %9.1f%% %8.0f"
              % (label, m, m - bf, cap, time.time() - t0))

    a = out["v4: agent-averaged scalar"]["dsr"]
    c = out["v5: per-agent samples"]["dsr"]
    print("\n  delta from fixing the update: %+.4f DSR" % (c - a))
    print("  %s" % ("the fix moves the learner ABOVE the memoryless baseline"
                    if c > bf else
                    "the learner is STILL below the memoryless baseline -- the "
                    "collapse was not the (only) cause"))
    os.makedirs(RESULTS, exist_ok=True)
    with open(os.path.join(RESULTS, "ppo_ab.json"), "w", encoding="utf-8") as f:
        json.dump({"architecture": "GRU only", "random": rnd, "best_fixed": bf,
                   "transition_oracle": orc, "budget": [args.updates,
                                                        args.batch_eps],
                   "results": out}, f, indent=1, default=float)
    print("  wrote -> results_v5/ppo_ab.json")
    print("=" * 96)


if __name__ == "__main__":
    main()
