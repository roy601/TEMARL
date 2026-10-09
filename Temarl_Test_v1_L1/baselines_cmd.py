# -*- coding: utf-8 -*-
"""
Temarl_Test_v1_L1 -- reference ladder for the command-level environment
========================================================================
A learned score means nothing on its own. These baselines bracket the range a
policy can occupy, so "dwell 9.2" can be read as a fraction of what is
available rather than as a bare number.

    null                every agent deploys nothing. The floor.
    static              one fixed decoy type, deployed everywhere, always.
                        The genuine "static honeypot" comparator.
    random              uniform random joint action each step.
    best_fixed          the best constant joint action, chosen by exhaustive
                        search over all 6^4 = 1296 tuples on VALIDATION only.
    reactive            each agent deploys the payoff-best decoy for the
                        command it can currently see, independently. No
                        coordination, no anticipation.
    clairvoyant_local   each agent reads the attacker's NEXT command and zone
                        and plays its own best response. Still uncoordinated.
    clairvoyant_coord   capacity-aware and lure-aware: deploys only within
                        capacity, in the zone the attacker is about to enter,
                        and keeps a partner decoy alive so lures can chain.
                        The practical ceiling.

Every baseline obeys the SAME capacity rule as the learned policies: nothing
here is allowed to exceed K decoys for free.

Clairvoyant baselines call `peek_next_*`, which reads the pre-drawn uniforms
and future commands. They are measuring instruments for the ladder, never
arms in the comparison, and the policies never have this access.
"""

from __future__ import annotations

import itertools
from typing import Dict, List, Optional, Sequence

import numpy as np

import _frozen  # noqa: F401
from d3fend_payoff import N_ACTIONS
from env_cmd import (AGENT_ZONE, LURES, N_AGENTS, NULL, ZONE_AGENT,
                     CommandEngagementEnv, EnvConfig, command_payoff,
                     run_episode)


class NullPolicy:
    name = "null"

    def __call__(self, env):
        return [NULL] * N_AGENTS


class StaticPolicy:
    """One fixed decoy type everywhere, every step: a static honeypot."""

    def __init__(self, action: int):
        self.action = int(action)
        self.name = f"static_{action}"

    def __call__(self, env):
        return [self.action] * N_AGENTS


class RandomPolicy:
    name = "random"

    def __init__(self, seed: int = 0):
        self.rng = np.random.default_rng(seed)

    def __call__(self, env):
        return list(self.rng.integers(0, N_ACTIONS, size=N_AGENTS))


class FixedJointPolicy:
    def __init__(self, joint: Sequence[int]):
        self.joint = list(int(a) for a in joint)
        self.name = f"fixed_{''.join(map(str, self.joint))}"

    def __call__(self, env):
        return self.joint


class ReactivePolicy:
    """Payoff-best response to the command currently visible. Uncoordinated.

    Sees only what the agent's own zone showed LAST step, so it is reactive
    rather than anticipatory -- it defends where the attacker just was.
    """

    name = "reactive"

    def __init__(self, cfg: EnvConfig):
        self.how = cfg.aggregation

    def __call__(self, env):
        acts = [NULL] * N_AGENTS
        if not env.cur_cmd:
            return acts
        ag = ZONE_AGENT.get(env.zone)
        if ag is None:
            return acts
        best, best_v = NULL, 0.0
        for d in range(1, N_ACTIONS):
            v = command_payoff(env.cur_cmd, d, self.how)
            if v > best_v:
                best, best_v = d, v
        acts[ag] = best
        return acts


class ClairvoyantLocalPolicy:
    """Each agent best-responds to the next command, independently.

    Uncoordinated: every agent that might be the destination deploys, so this
    routinely exceeds capacity and is degraded by phi exactly like any other
    over-deployment. The gap to `clairvoyant_coord` is the value of
    coordination.
    """

    name = "clairvoyant_local"

    def __init__(self, cfg: EnvConfig):
        self.how = cfg.aggregation

    def __call__(self, env):
        nxt_zone = env.peek_next_zone()
        labels = env.peek_next_command()
        acts = [NULL] * N_AGENTS
        for i, z in enumerate(AGENT_ZONE):
            if z != nxt_zone:
                continue
            best, best_v = NULL, 0.0
            for d in range(1, N_ACTIONS):
                v = command_payoff(labels, d, self.how)
                if v > best_v:
                    best, best_v = d, v
            acts[i] = best
        return acts


class ClairvoyantCoordPolicy:
    """Capacity-aware, lure-aware ceiling.

    Deploys the best decoy in the zone the attacker is about to enter. If that
    best choice is a lure, it also deploys one partner decoy elsewhere so the
    lure can chain instead of dead-ending -- the coordination the learned
    policies must discover. Never exceeds K.
    """

    name = "clairvoyant_coord"

    def __init__(self, cfg: EnvConfig):
        self.cfg = cfg
        self.how = cfg.aggregation

    def __call__(self, env):
        acts = [NULL] * N_AGENTS
        if env.burned:
            return acts                     # deception is spent; deploy nothing
        nxt_zone = env.peek_next_zone()
        labels = env.peek_next_command()
        ag = ZONE_AGENT.get(nxt_zone)
        if ag is None:
            return acts
        best, best_v = NULL, 0.0
        for d in range(1, N_ACTIONS):
            v = command_payoff(labels, d, self.how)
            if v > best_v:
                best, best_v = d, v
        if best == NULL:
            return acts
        acts[ag] = best
        if best in LURES and self.cfg.k_capacity >= 2:
            # One partner so the breadcrumb has somewhere to lead.
            for j, z in enumerate(AGENT_ZONE):
                if j != ag:
                    acts[j] = 1
                    break
        return acts


# ── evaluation ──────────────────────────────────────────────────────────────

def evaluate_policy(policy, specs, cfg: EnvConfig, max_steps: int) -> dict:
    env = CommandEngagementEnv(cfg, max_steps=max_steps)
    stats = [run_episode(env, s, policy) for s in specs]
    keys = ("dwell", "depth", "protected", "exposed", "length",
            "lure_chains", "dead_ends", "capacity_violations",
            "decoys_deployed")
    out = {k: float(np.mean([s[k] for s in stats])) for k in keys}
    out["n_episodes"] = len(stats)
    out["name"] = getattr(policy, "name", type(policy).__name__)
    return out


def best_fixed_joint(specs, cfg: EnvConfig, max_steps: int,
                     metric: str = "dwell") -> dict:
    """Exhaustive search over all 6^4 constant joint actions.

    MUST be run on validation specs. Choosing it on test would tune a baseline
    to the test set and make every comparison against it optimistic.
    """
    best = None
    for joint in itertools.product(range(N_ACTIONS), repeat=N_AGENTS):
        r = evaluate_policy(FixedJointPolicy(joint), specs, cfg, max_steps)
        if best is None or r[metric] > best[1][metric]:
            best = (joint, r)
    joint, r = best
    r["joint"] = list(joint)
    r["name"] = "best_fixed"
    return r


def best_static(specs, cfg: EnvConfig, max_steps: int,
                metric: str = "dwell") -> dict:
    """Best single decoy type deployed everywhere: the static honeypot."""
    best = None
    for a in range(1, N_ACTIONS):
        r = evaluate_policy(StaticPolicy(a), specs, cfg, max_steps)
        if best is None or r[metric] > best[1][metric]:
            best = (a, r)
    a, r = best
    r["action"] = a
    r["name"] = "static_best"
    return r


def ladder(validation_specs, test_specs, cfg: EnvConfig, max_steps: int,
           seed: int = 0) -> dict:
    """Full ladder. Tunable baselines are fitted on validation, then all
    rungs are reported on both splits."""
    fixed = best_fixed_joint(validation_specs, cfg, max_steps)
    static = best_static(validation_specs, cfg, max_steps)

    policies = [
        NullPolicy(),
        StaticPolicy(static["action"]),
        RandomPolicy(seed),
        FixedJointPolicy(fixed["joint"]),
        ReactivePolicy(cfg),
        ClairvoyantLocalPolicy(cfg),
        ClairvoyantCoordPolicy(cfg),
    ]
    names = ["null", "static_best", "random", "best_fixed", "reactive",
             "clairvoyant_local", "clairvoyant_coord"]

    out = {"selected_on_validation": {"best_fixed_joint": fixed["joint"],
                                      "static_action": static["action"]},
           "validation": {}, "test": {}}
    for name, pol in zip(names, policies):
        for split, specs in (("validation", validation_specs),
                             ("test", test_specs)):
            r = evaluate_policy(pol, specs, cfg, max_steps)
            r["name"] = name
            out[split][name] = r
    return out


def headroom(ladder_block: Dict[str, dict], metric: str = "dwell") -> dict:
    """Floor, ceiling and the span a learned policy has to work with."""
    floor = ladder_block["best_fixed"][metric]
    ceiling = ladder_block["clairvoyant_coord"][metric]
    return {"metric": metric, "floor_best_fixed": floor, "ceiling": ceiling,
            "headroom": ceiling - floor,
            "coordination_value": (ladder_block["clairvoyant_coord"][metric]
                                   - ladder_block["clairvoyant_local"][metric])}


def capture(value: float, ladder_block: Dict[str, dict],
            metric: str = "dwell") -> float:
    """Fraction of the best-fixed -> ceiling headroom a score captures."""
    h = headroom(ladder_block, metric)
    span = h["headroom"]
    return float((value - h["floor_best_fixed"]) / span) if span > 0 else float("nan")
