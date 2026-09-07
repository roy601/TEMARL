# -*- coding: utf-8 -*-
"""
TEMARL — reference baselines for the ENTITY environment  (EXPLORATORY)
======================================================================
STATUS: exploratory diagnostic. This is NOT part of the v4 pre-registration
(`prereg_v4.py`, commit 7499d29) and changes none of its declared contrasts.
It adds no arm, drops no contrast, and re-scores nothing. It answers a question
the pre-registration never asked, and could not answer:

    **Is a DSR of 0.450 good?**

The v2 evaluation (`evaluate_v2.py`) shipped five reference policies and a
ceiling, so every learned number could be placed on a scale:

    Static-Null 0.3125 | Random 0.4465 | Best-Fixed 0.5000 | h=0 0.5405
    | learned ~0.601 | Profile-Oracle 0.6405

The v3/v4 entity pipeline (`train_entity.py`) has no such reference: every arm
is a trained model. A null result among trained arms is uninterpretable without
one, because two very different worlds produce the same null --

    (a) all arms learned well and sit near a shared ceiling, or
    (b) no arm learned anything and all sit near the floor.

The pre-registered analysis cannot distinguish them. This script can.

THE LADDER
----------
Each rung is a policy given strictly more information than the one above it.
Because an agent may only target hosts in its own zone, and the responsible
agent is by definition the one owning the entered zone, the target choice is
almost never the binding constraint -- alignment reduces to PAYOFF[tau, type]
for whichever agent turns out to be responsible. So the ladder varies exactly
what the history encoder is supposed to supply: knowledge of tau.

    null         action type 0 always                      absolute floor
    random       uniform over action types                 no information
    best_fixed   argmax_a E_mixture[PAYOFF[.,a]]           no intent model
    profile      argmax_a E_{tau~c}[PAYOFF[.,a]], c known  perfect profile ID
    transition   argmax_a E_{tau'~T[tau]}[PAYOFF[.,a]]     perfect NEXT-TECHNIQUE
                                                           model  <-- the exact
                                                           ceiling for a history
                                                           encoder
    clairvoyant  argmax_a PAYOFF[tau_realised, a]          unattainable bound

`transition` is the number that matters. The history encoder's entire job is to
predict the next technique. A policy handed that prediction *perfectly*, for
free, defines the maximum DSR any encoder improvement can ever reach. If the
trained arms already sit at it, the Phase-4 null is fully explained and is a
property of the environment, not of attention vs recurrence.

Protocol is copied from `train_entity.evaluate()` verbatim -- same episode
count, same topology cycling, same env seed stream -- so the numbers are
directly comparable to the v4 arms.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

import numpy as np

import prereg_v4 as PR
from d3fend_payoff import ACTIONS, N_ACTIONS, PAYOFF
from env_entity import EntityDeceptionEnv
from train_entity import build_topologies, profiles
from profiles_v5 import profiles_v5
from env_v2 import CAP_P_MAX, CAP_P_MIN

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results_v4")
REGIMES = ("A", "B", "C", "D")
POLICIES = ("null", "random", "best_fixed", "profile", "transition",
            "clairvoyant")


# ── decision rules ───────────────────────────────────────────────────────────

def profile_tech_dists(profs, n_steps: int = 20000, seed: int = 0):
    """Empirical technique distribution per profile, by simulating its chain.

    Sampled rather than solved for the stationary distribution, because the
    episode is short (<=40 steps) and starts from `init`, so the stationary
    distribution is the wrong object -- what matters is the distribution the
    defender actually faces.
    """
    rng = np.random.default_rng(seed)
    out = {}
    for name, p in profs.items():
        counts = np.zeros(PAYOFF.shape[0])
        tau = int(rng.choice(len(p["init"]), p=p["init"]))
        for i in range(n_steps):
            tau = int(rng.choice(PAYOFF.shape[0], p=p["T"][tau]))
            counts[tau] += 1
            if (i + 1) % PR.MAX_STEPS == 0:          # restart, as episodes do
                tau = int(rng.choice(len(p["init"]), p=p["init"]))
        out[name] = counts / counts.sum()
    return out


def decision_table(profs):
    """Precompute argmax action for each rung that admits a lookup."""
    dists = profile_tech_dists(profs)
    marginal = np.mean([d @ PAYOFF for d in dists.values()], axis=0)
    best_fixed = int(marginal.argmax())
    a_star_profile = {c: int((d @ PAYOFF).argmax()) for c, d in dists.items()}
    # per current technique: argmax_a E_{tau' ~ T[tau]}[PAYOFF[tau', a]]
    # T differs by profile, so this is indexed (profile, tau).
    a_star_trans = {c: (np.asarray(p["T"]) @ PAYOFF).argmax(1)
                    for c, p in profs.items()}
    a_star_clair = PAYOFF.argmax(1)                  # per realised technique
    return {"best_fixed": best_fixed,
            "best_fixed_name": ACTIONS[best_fixed],
            "profile": a_star_profile,
            "transition": a_star_trans,
            "clairvoyant": a_star_clair,
            "marginal": marginal,
            "dists": dists}


def choose(policy: str, env: EntityDeceptionEnv, tbl, rng):
    """One (action_type, target) pair per agent.

    Every rung uses only information available BEFORE the attacker moves, except
    `clairvoyant`, which is explicitly an unattainable bound and peeks at the
    technique the environment is about to emit.
    """
    if policy == "clairvoyant":
        # Peek at the technique the environment is ABOUT to emit, by cloning the
        # RNG state, reproducing `_next_technique()`'s draw exactly, and
        # restoring it -- so the bound costs the episode nothing. Not attainable
        # by any policy; it exists to bound the rungs above.
        st = env.rng.bit_generator.state
        tau_next = int(env.rng.choice(
            PAYOFF.shape[0], p=env.profiles[env._profile]["T"][env.tau]))
        env.rng.bit_generator.state = st
        t = int(tbl["clairvoyant"][tau_next])
    elif policy == "null":
        t = 0
    elif policy == "random":
        t = int(rng.integers(N_ACTIONS))
    elif policy == "best_fixed":
        t = tbl["best_fixed"]
    elif policy == "profile":
        t = tbl["profile"][env._profile]
    elif policy == "transition":
        t = int(tbl["transition"][env._profile][env.tau])
    else:
        raise ValueError(policy)

    acts = []
    for ag in range(env.n_agents):
        legal = env.legal_targets(ag)
        if len(legal) == 0:
            acts.append((0, 0))
            continue
        tt = int(rng.integers(N_ACTIONS)) if policy == "random" else t
        acts.append((tt, int(legal[0])))
    return acts


# ── evaluation, protocol-identical to train_entity.evaluate() ───────────────

def evaluate_policy(policy: str, topos, tbl, n_episodes: int, seed: int,
                    profs=None, env_kw=None):
    env_rng = np.random.default_rng(1_000_000 + seed)     # same stream as v4
    act_rng = np.random.default_rng(7_000_000 + seed)     # separate, so the
    profs = profiles() if profs is None else profs        # env stream matches
    acc = {k: [] for k in ("dsr", "alignment", "episode_return",
                           "engagement_length")}
    for i in range(n_episodes):
        topo = topos[i % len(topos)]
        env = EntityDeceptionEnv(topology=topo, profiles=profs,
                                 max_steps=PR.MAX_STEPS,
                                 max_entities=PR.MAX_ENTITIES,
                                 seed=int(env_rng.integers(1 << 30)),
                                 **(env_kw or {}))
        env.reset()
        ret, aligns, steps, done = 0.0, [], 0, False
        while not done:
            a = choose(policy, env, tbl, act_rng)
            _, rw, done, info = env.step(a)
            ret += float(rw[0]); aligns.append(info["alignment"]); steps += 1
        acc["dsr"].append(1.0 if env.captured else 0.0)
        acc["alignment"].append(float(np.mean(aligns)) if aligns else 0.0)
        acc["episode_return"].append(ret)
        acc["engagement_length"].append(float(steps))
    return {k: float(np.mean(v)) for k, v in acc.items()}


def ci95(x):
    x = np.asarray(x, float)
    if len(x) < 2:
        return float(x.mean()), 0.0
    return float(x.mean()), float(1.96 * x.std(ddof=1) / np.sqrt(len(x)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="*", default=list(PR.SEEDS))
    ap.add_argument("--episodes", type=int, default=PR.EVAL_EPISODES)
    ap.add_argument("--regimes", nargs="*", default=list(REGIMES))
    ap.add_argument("--out", default=os.path.join(RESULTS, "baselines_entity.json"))
    ap.add_argument("--cap-scale", type=float, default=1.0,
                    help="scales (CAP_P_MIN, CAP_P_MAX); v5 calibration = 0.35")
    ap.add_argument("--goal-steps", type=int, default=None,
                    help="objective race length; v5 calibration = 3")
    ap.add_argument("--profiles", choices=("v2", "v5"), default="v2",
                    help="v2 = shipped estimator (goal drift on); "
                         "v5 = repaired estimator (drift removed)")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    t0 = time.time()
    profs = profiles() if args.profiles == 'v2' else profiles_v5()
    env_kw = {"cap_p_min": CAP_P_MIN * args.cap_scale,
              "cap_p_max": CAP_P_MAX * args.cap_scale}
    if args.goal_steps is not None:
        env_kw["goal_steps"] = args.goal_steps
    tbl = decision_table(profs)

    print("=" * 96)
    print("  ENTITY-ENVIRONMENT REFERENCE BASELINES  (EXPLORATORY — not part of")
    print("  the v4 pre-registration; adds and changes no declared contrast)")
    print("=" * 96)
    print("  %d seeds x %d episodes, protocol identical to train_entity.evaluate()"
          % (len(args.seeds), args.episodes))
    print("  best fixed action : %d (%s)"
          % (tbl["best_fixed"], tbl["best_fixed_name"]))
    print("  per-profile a*    : %s"
          % {c: ACTIONS[a] for c, a in tbl["profile"].items()})
    print("  expected payoff   : best-fixed %.4f | profile-oracle %.4f | "
          "headroom %.4f"
          % (tbl["marginal"][tbl["best_fixed"]],
             float(np.mean([ (tbl["dists"][c] @ PAYOFF)[tbl["profile"][c]]
                             for c in tbl["profile"] ])),
             float(np.mean([ (tbl["dists"][c] @ PAYOFF)[tbl["profile"][c]]
                             for c in tbl["profile"] ])
                   - tbl["marginal"][tbl["best_fixed"]])))

    rows, out = [], {}
    for rg in args.regimes:
        topos = build_topologies(rg)
        print("\n  regime %s (%s) — %d topologies"
              % (rg, PR.REGIME_DESC[rg], len(topos)))
        print("  %-14s %18s %18s %14s" % ("policy", "DSR", "alignment", "ep len"))
        print("  " + "-" * 70)
        for pol in POLICIES:
            per_seed = [evaluate_policy(pol, topos, tbl, args.episodes, s,
                                        profs=profs, env_kw=env_kw)
                        for s in args.seeds]
            d_m, d_h = ci95([r["dsr"] for r in per_seed])
            a_m, a_h = ci95([r["alignment"] for r in per_seed])
            l_m, _ = ci95([r["engagement_length"] for r in per_seed])
            out.setdefault(rg, {})[pol] = {
                "dsr_mean": d_m, "dsr_ci95": d_h,
                "alignment_mean": a_m, "alignment_ci95": a_h,
                "engagement_length_mean": l_m,
                "per_seed_dsr": [r["dsr"] for r in per_seed]}
            print("  %-14s %18s %18s %14.2f"
                  % (pol, "%.4f+-%.4f" % (d_m, d_h),
                     "%.4f+-%.4f" % (a_m, a_h), l_m))
            rows.append((rg, pol, d_m))

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"exploratory": True,
                   "profiles": args.profiles,
                   "cap_scale": args.cap_scale,
                   "goal_steps": args.goal_steps,
                   "not_part_of_prereg": "prereg_v4.py / commit 7499d29",
                   "seeds": list(args.seeds), "episodes": args.episodes,
                   "best_fixed_action": tbl["best_fixed"],
                   "best_fixed_name": tbl["best_fixed_name"],
                   "per_profile_a_star": {c: ACTIONS[a]
                                          for c, a in tbl["profile"].items()},
                   "results": out,
                   "seconds": time.time() - t0}, f, indent=1, default=float)
    print("\n  wrote -> %s  (%.0f s)"
          % (os.path.relpath(args.out, HERE), time.time() - t0))
    print("=" * 96)


if __name__ == "__main__":
    main()
