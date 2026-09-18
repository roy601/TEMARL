# -*- coding: utf-8 -*-
"""
TEMARL v7 — learning gate (Transformer-RoPE arm; chooses the training BUDGET)
=============================================================================
Before any architecture is compared, the learner itself must work: a team
trained by MAPPO has to beat the memoryless and the uncoordinated baselines.
v4/v5 skipped the equivalent check under PPO and ended with behaviour cloning;
v7 must not. The rule below was written before the gate ran.

  ARM        Transformer-RoPE (the thesis model), MAPPO, centralised critic.
             DISCLOSURE: the approved plan ran this gate on the GRU so that the
             budget could not be chosen to suit the arm under test. On
             2026-09-19, before the gate ran, the author directed that it run
             on the Transformer instead (GRU and LSTM are trained later, in the
             confirmatory run). The chosen budget is therefore "the smallest
             budget at which the TRANSFORMER team works", and it is applied
             unchanged to every arm. The risk this creates -- other arms
             under-trained at a Transformer-sized budget -- is guarded by the
             pre-registered convergence flag in prereg_marl.py.
  SEEDS      900, 901, 902 -- disjoint from the confirmatory seeds 0-9, so the
             confirmatory runs are fresh.
  BUDGETS    1M, 2M, 4M environment steps, tried in increasing order; the
             first budget that passes is chosen.
  PASS       (a) on EVERY seed, MAPPO's test dwell exceeds both the best fixed
                 joint action and the better uncoordinated reactive baseline,
                 all scored on the same test episodes (common random numbers);
             (b) averaged over seeds, MAPPO captures >= 50% of the headroom
                 between the best fixed action and the transition planner
                 (a central allocator that is TOLD the hidden script).
  FAILURE    if no budget passes, the learner is reported as failing. The
             experiment then stops: there is no fallback to behaviour cloning,
             which would not be multi-agent RL. At most two logged diagnostic
             rounds (on the same arm, applied identically to all arms) may follow, each recorded.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ARM = "Transformer-RoPE"
SEEDS = (900, 901, 902)
BUDGETS = (1_000_000, 2_000_000, 4_000_000)
CAPTURE_MIN = 0.50


def _one(args):
    seed, budget, threads, device = args
    import torch
    torch.set_num_threads(threads)
    import _frozen  # noqa: F401
    from baselines_marl import Beliefs, Fixed, Planner, Reactive, evaluate
    from env_marl import SCRIPT_IDS, EnvConfig, EpisodeSource
    from mappo import SEED_TEST, summary, train
    from pretrain_marl import pretrain

    cfg_d = json.load(open(os.path.join(HERE, "env_config.json"), encoding="utf-8"))["config"]
    cfg = EnvConfig(**cfg_d)
    gates = json.load(open(os.path.join(HERE, "results_marl", "gates.json"),
                           encoding="utf-8"))
    pre = pretrain(ARM, seed, SCRIPT_IDS, device)
    out = train(pre["encoder"], cfg, SCRIPT_IDS, seed, budget, centralised=True,
                device=device)
    specs = EpisodeSource(SEED_TEST + seed, SCRIPT_IDS).take(500)
    B = Beliefs(SCRIPT_IDS)
    th = gates["meta"]["transition/coord"]["theta"]
    base = {
        "best_fixed": summary(evaluate(Fixed(gates["meta"]["best_fixed_joint"]), specs, cfg)),
        "reactive/naive": summary(evaluate(Reactive("naive"), specs, cfg)),
        "reactive/averse": summary(evaluate(Reactive("averse"), specs, cfg)),
        "transition/coord": summary(evaluate(Planner("transition", True, B, th), specs, cfg)),
    }
    return {"seed": seed, "budget": budget, "pretrain": pre["metrics"],
            "mappo": summary(out["test_rows"]), "mappo_h0": summary(out["test_rows_h0"]),
            "baselines": base, "curve": out["curve"], "best_update": out["best_update"],
            "seconds": out["seconds"]}


def judge(res):
    ok_every, captures = True, []
    for r in res:
        m = r["mappo"]["dwell"]
        b = r["baselines"]
        unc = max(b["reactive/naive"]["dwell"], b["reactive/averse"]["dwell"])
        ok_every &= (m > b["best_fixed"]["dwell"]) and (m > unc)
        span = b["transition/coord"]["dwell"] - b["best_fixed"]["dwell"]
        captures.append((m - b["best_fixed"]["dwell"]) / span if span > 0 else 0.0)
    cap = float(np.mean(captures))
    return {"beats_baselines_every_seed": bool(ok_every), "capture": cap,
            "captures": captures, "pass": bool(ok_every and cap >= CAPTURE_MIN)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--threads", type=int, default=3)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--out", default=os.path.join(HERE, "results_marl", "learning_gate.json"))
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    log = {"rule": {"arm": ARM, "seeds": SEEDS, "budgets": BUDGETS,
                    "capture_min": CAPTURE_MIN},
           "rounds": [], "chosen_budget": None}
    print("=" * 100)
    print("  TEMARL v7 — LEARNING GATE (%s, seeds %s)" % (ARM, SEEDS))
    print("=" * 100)
    for budget in BUDGETS:
        t0 = time.time()
        with ProcessPoolExecutor(max_workers=len(SEEDS)) as ex:
            res = list(ex.map(_one, [(s, budget, args.threads, args.device) for s in SEEDS]))
        j = judge(res)
        log["rounds"].append({"budget": budget, "results": res, "judgement": j})
        print("\n  budget %dM env-steps  (%.0f s)" % (budget // 1_000_000, time.time() - t0))
        for r in res:
            b = r["baselines"]
            print("    seed %d  MAPPO dwell %6.2f depth %5.2f prot %.3f | best-fixed %6.2f "
                  "reactive %6.2f/%6.2f transition %6.2f | h=0 %6.2f | pretrain top1 %.3f"
                  % (r["seed"], r["mappo"]["dwell"], r["mappo"]["depth"],
                     r["mappo"]["protected"], b["best_fixed"]["dwell"],
                     b["reactive/naive"]["dwell"], b["reactive/averse"]["dwell"],
                     b["transition/coord"]["dwell"], r["mappo_h0"]["dwell"],
                     r["pretrain"]["top1"]))
        print("    beats baselines on every seed: %s | capture %.1f%% (need >= %.0f%%) -> %s"
              % (j["beats_baselines_every_seed"], 100 * j["capture"],
                 100 * CAPTURE_MIN, "PASS" if j["pass"] else "not yet"))
        json.dump(log, open(args.out, "w", encoding="utf-8"), indent=1, default=float)
        if j["pass"]:
            log["chosen_budget"] = budget
            break
    json.dump(log, open(args.out, "w", encoding="utf-8"), indent=1, default=float)
    print("\n  CHOSEN BUDGET: %s" % (log["chosen_budget"] or "NONE -- the learner fails the gate"))
    print("=" * 100)


if __name__ == "__main__":
    main()
