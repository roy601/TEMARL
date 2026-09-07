# -*- coding: utf-8 -*-
"""
TEMARL v3 — Variable-topology entity environment
=================================================
A Dec-POMDP honeypot-deception environment whose observation and action spaces
are decomposed into discrete ENTITIES (hosts), after

    Symes Thompson, Caron, Hicks & Mavroudis (2024), arXiv:2410.17647.

This module does NOT replace `env_v2.DeceptionEnvV2`. That environment remains
the frozen scientific control and is untouched. Everything the thesis has
already verified is preserved here verbatim:

  * the D3FEND payoff matrix (`PAYOFF`, frozen, never refitted),
  * the CAM-LDS attacker profiles (`build_profiles_from_camlds`),
  * the reward  R = W_ENGAGE*r1 + W_ALIGN*r2  and the additive TERMINAL_PENALTY,
  * alignment-driven capture with its EMA and CAP_* constants,
  * the GOAL_STEPS race and all termination rules,
  * the 84-technique vocabulary and RIGHT-padded sequence contract.

CONTROL-MODE EQUIVALENCE
------------------------
Run on `canonical_topology()`, this environment must reproduce env_v2 exactly,
step for step, given the same seed and the same action types. That requires
consuming the random stream in the IDENTICAL ORDER, because both environments
draw from `np.random.default_rng(seed)`:

    reset : choice(profile name) [Mixture only] -> choice(initial technique)
    step  : choice(next technique) -> [random() dwell test] -> choice(zone)
            -> random() capture test

`_move()` below generalises env_v2's movement to an arbitrary zone graph while
reducing to precisely those calls on the canonical star topology. Any deviation
would show up immediately in `equivalence_report()`, which compares full
trajectories rather than summary statistics.

COMPOSITE ACTIONS
-----------------
An action is a pair (action_type, target_entity). `action_type` indexes the same
six D3FEND classes as env_v2; `target_entity` names the host the decoy is placed
on. Alignment is credited only when the decoy sits in the zone the attacker
actually moved into -- on the canonical topology each agent owns exactly one
zone, so every legal target of the responsible agent is in that zone and the
alignment term is identical to env_v2's. On larger topologies an agent owns
several zones and placement becomes a real decision, which is where entity
awareness can pay for itself.

PADDING
-------
Entity tensors are padded to a fixed capacity purely so batches stack. Padded
slots are zero and carry mask 0; encoders must exclude them from attention and
pooling, and they never enter rewards, actions, or statistics.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from d3fend_payoff import ACTIONS, N_ACTIONS, PAYOFF
from env_v2 import (CAP_A_REF, CAP_EMA, CAP_K, CAP_P_MAX, CAP_P_MIN, GOAL_STEPS,
                    TERMINAL_PENALTY, W_ALIGN, W_ENGAGE,
                    build_profiles_from_camlds)
from topology import (MAX_VULNS, MAX_ZONES, N_NODE_TYPES, N_SERVICES,
                      NODE_TYPE_ID, SERVICE_ID, Topology, canonical_topology)
from vocab_v2 import MAX_SEQ_LEN, NUM_TECHNIQUES, PAD_ID, tactic_of

# ── entity feature layout (fixed width; independent of topology size) ────────
_F_NODE_TYPE = 0
_F_ZONE = _F_NODE_TYPE + N_NODE_TYPES
_F_SERVICES = _F_ZONE + MAX_ZONES
_F_VULN = _F_SERVICES + N_SERVICES
_F_CRITICAL = _F_VULN + 1
_F_ENTRY = _F_CRITICAL + 1
_F_DEF_OWNED = _F_ENTRY + 1
_F_COMPROMISED = _F_DEF_OWNED + 1
_F_DECOY_ACTIVE = _F_COMPROMISED + 1
_F_DECOY_TYPE = _F_DECOY_ACTIVE + 1
_F_VISIBLE_TO_ME = _F_DECOY_TYPE + N_ACTIONS
_F_OWNED_BY_ME = _F_VISIBLE_TO_ME + 1
_F_ATTACKER_HERE = _F_OWNED_BY_ME + 1
ENTITY_FEAT_DIM = _F_ATTACKER_HERE + 1

# ── per-agent global (non-entity) features ──────────────────────────────────
_G_MYZONES = 0
_G_SIGHTED = _G_MYZONES + MAX_ZONES
_G_MY_COMP = _G_SIGHTED + 1
_G_ALL_COMP = _G_MY_COMP + 1
_G_ALERT = _G_ALL_COMP + 1
_G_STEP = _G_ALERT + 1
_G_TECH = _G_STEP + 1
GLOBAL_FEAT_DIM = _G_TECH + NUM_TECHNIQUES

DEFAULT_MAX_ENTITIES = 48


class EntityDeceptionEnv:
    """Variable-topology entity-based Dec-POMDP deception environment."""

    def __init__(self, topology: Optional[Topology] = None, profiles=None,
                 profile_name: str = "Mixture", max_steps: int = 40,
                 seed: Optional[int] = None, alignment_driven_capture: bool = True,
                 max_entities: int = DEFAULT_MAX_ENTITIES,
                 h_dim: int = 64,
                 cap_p_min: float = CAP_P_MIN, cap_p_max: float = CAP_P_MAX,
                 goal_steps: int = GOAL_STEPS):
        self.topo = topology if topology is not None else canonical_topology()
        if self.topo.n_hosts > max_entities:
            raise ValueError(f"topology has {self.topo.n_hosts} hosts > "
                             f"max_entities {max_entities}")
        if profiles is None:
            profiles, _ = build_profiles_from_camlds()
        self.profiles = profiles
        self.names = sorted(profiles)
        self.profile_name = profile_name
        self.max_steps = max_steps
        self.alignment_driven_capture = alignment_driven_capture
        # Capture calibration. Defaults are env_v2's frozen constants, so an
        # unparameterised env is bit-identical to before; v5 overrides them
        # because removing the goal drift roughly tripled episode length, which
        # saturated DSR (env_v2's own gate rejects a saturated DSR).
        self.cap_p_min = cap_p_min
        self.cap_p_max = cap_p_max
        self.goal_steps = goal_steps
        self.max_entities = max_entities
        self.h_dim = h_dim
        self.rng = np.random.default_rng(seed)

        self.n_agents = self.topo.n_agents
        self.entry_zone = self.topo.entry_zone
        self.defended = self.topo.defended_zones
        self.agent_of_zone = dict(self.topo.agent_of_zone)
        self.entity_feat_dim = ENTITY_FEAT_DIM
        self.global_feat_dim = GLOBAL_FEAT_DIM

        self._static = self._build_static_features()
        self._host_zone = np.array([h.zone for h in self.topo.hosts], np.int64)
        self._host_agent = np.array(
            [self.agent_of_zone.get(h.zone, -1) for h in self.topo.hosts], np.int64)
        self.reset()

    # ── static entity features (topology-invariant across an episode) ───────
    def _build_static_features(self) -> np.ndarray:
        F = np.zeros((self.max_entities, ENTITY_FEAT_DIM), np.float32)
        for h in self.topo.hosts:
            r = F[h.hid]
            r[_F_NODE_TYPE + NODE_TYPE_ID[h.node_type]] = 1.0
            r[_F_ZONE + h.zone] = 1.0
            for s in h.services:
                r[_F_SERVICES + SERVICE_ID[s]] = 1.0
            r[_F_VULN] = h.n_vulns / MAX_VULNS
            r[_F_CRITICAL] = float(h.is_critical)
            r[_F_ENTRY] = float(h.is_entry)
            r[_F_DEF_OWNED] = float(h.defender_owned)
        return F

    # ── episode lifecycle (RNG order mirrors env_v2 exactly) ───────────────
    def reset(self):
        self._profile = (self.rng.choice(self.names)
                         if self.profile_name == "Mixture" else self.profile_name)
        p = self.profiles[self._profile]
        self.zone = self.entry_zone
        self.prev_zone = self.entry_zone
        self.seq: List[int] = []
        self.tau = int(self.rng.choice(NUM_TECHNIQUES, p=p["init"]))
        self.step_count = 0
        self.done = False
        self.ema_align = CAP_A_REF
        self.compromised = np.zeros(self.topo.n_zones)
        self.host_compromised = np.zeros(self.max_entities, np.float32)
        self.decoy_active = np.zeros(self.max_entities, np.float32)
        self.decoy_type = np.zeros(self.max_entities, np.int64)
        self.alert = 0.0
        self.captured = False
        self.reached_objective = False
        self.progress = 0
        return self.observations()

    def _next_technique(self) -> int:
        T = self.profiles[self._profile]["T"]
        return int(self.rng.choice(NUM_TECHNIQUES, p=T[self.tau]))

    def _move(self) -> int:
        """Generalisation of env_v2._move() to an arbitrary zone graph.

        On the canonical star topology every defended zone is adjacent to every
        other and to the entry zone, so the candidate sets, the 0.45 dwell test,
        and the compromise-weighted choice reduce to env_v2's exactly -- and the
        random stream is consumed in the same order.
        """
        adj = self.topo.zone_adj
        if self.zone == self.entry_zone:
            cand = [z for z in self.defended if adj[self.zone][z]]
        else:
            if self.rng.random() < 0.45:
                return self.zone
            cand = [z for z in self.defended
                    if z != self.zone and adj[self.zone][z]]
            if not cand:            # firewall-isolated zone: dwell
                return self.zone
        w = np.array([1.0 + 0.8 * self.compromised[z] for z in cand])
        return int(self.rng.choice(cand, p=w / w.sum()))

    # ── step ────────────────────────────────────────────────────────────────
    def step(self, actions: Sequence[Tuple[int, int]], h=None):
        """actions: one (action_type, target_entity) pair per agent."""
        assert len(actions) == self.n_agents, \
            f"expected {self.n_agents} actions, got {len(actions)}"
        a_types = np.array([int(a[0]) for a in actions], np.int64)
        a_targets = np.array([int(a[1]) for a in actions], np.int64)
        if np.any((a_types < 0) | (a_types >= N_ACTIONS)):
            raise ValueError(f"action_type out of range: {a_types.tolist()}")

        self.prev_zone = self.zone

        # 1. attacker emits a technique and moves
        self.tau = self._next_technique()
        self.seq.append(self.tau)
        self.zone = self._move()

        # place decoys (a null action places nothing)
        self.decoy_active[:] = 0.0
        self.decoy_type[:] = 0
        for ag in range(self.n_agents):
            t, tgt = int(a_types[ag]), int(a_targets[ag])
            if t == 0:
                continue
            if not (0 <= tgt < self.topo.n_hosts):
                raise ValueError(f"agent {ag} target {tgt} is not a valid entity")
            if self._host_agent[tgt] != ag:
                raise ValueError(f"agent {ag} may not target entity {tgt} "
                                 f"(owned by agent {self._host_agent[tgt]})")
            self.decoy_active[tgt] = 1.0
            self.decoy_type[tgt] = t

        # 2. ANTICIPATORY single-agent credit, unchanged from env_v2
        resp = self.agent_of_zone.get(self.zone)
        blind = (self.prev_zone != self.zone)
        if resp is None:
            align = 0.0
        else:
            t, tgt = int(a_types[resp]), int(a_targets[resp])
            # the decoy must sit in the zone the attacker entered
            in_zone = (0 <= tgt < self.topo.n_hosts
                       and self._host_zone[tgt] == self.zone)
            align = float(PAYOFF[self.tau, t]) if in_zone else 0.0

        # 3. alignment-driven containment, unchanged
        self.ema_align = CAP_EMA * self.ema_align + (1 - CAP_EMA) * align
        if self.alignment_driven_capture and resp is not None:
            z = CAP_K * (self.ema_align - CAP_A_REF)
            p_cap = self.cap_p_min + (self.cap_p_max - self.cap_p_min) / (
                1.0 + np.exp(-z))
        else:
            p_cap = 0.9
        engaged = bool(self.rng.random() < p_cap)
        p = self.profiles[self._profile]
        if engaged:
            self.captured = True
        else:
            self.compromised[self.zone] = 1.0
            for hh in self.topo.hosts_in_zone(self.zone):
                self.host_compromised[hh.hid] = 1.0
            self.alert = min(1.0, self.alert + 0.15)
            if tactic_of(self.tau) == p["goal_tactic"]:
                self.progress += 1

        # 4. reward — identical formula
        r1 = 1.0 if engaged else 0.0
        r2 = align
        reward = W_ENGAGE * r1 + W_ALIGN * r2

        # 5. termination — identical rules
        self.step_count += 1
        if self.captured:
            self.done = True
        elif self.progress >= self.goal_steps:
            self.reached_objective = True
            self.done = True
            reward += TERMINAL_PENALTY
        elif self.step_count >= self.max_steps:
            self.done = True

        info = {"technique_id": self.tau, "profile": self._profile,
                "responsible_agent": resp, "blind": blind, "alignment": align,
                "ema_align": self.ema_align, "p_capture": float(p_cap),
                "captured": self.captured, "zone": self.zone,
                "reached_objective": self.reached_objective}
        return self.observations(h), [reward] * self.n_agents, self.done, info

    # ── observations ────────────────────────────────────────────────────────
    def observations(self, h=None) -> List[Dict[str, np.ndarray]]:
        hv = (np.zeros(self.h_dim, np.float32) if h is None
              else np.asarray(h, np.float32))
        n = self.topo.n_hosts
        valid = np.zeros(self.max_entities, np.float32)
        valid[:n] = 1.0

        # dynamic columns shared by all agents
        base = self._static.copy()
        base[:, _F_COMPROMISED] = self.host_compromised
        base[:, _F_DECOY_ACTIVE] = self.decoy_active
        for i in range(n):
            if self.decoy_active[i]:
                base[i, _F_DECOY_TYPE + int(self.decoy_type[i])] = 1.0

        adj = self._host_adjacency()
        out = []
        for ag in range(self.n_agents):
            my_zones = self.topo.zone_of_agent(ag)
            vis = np.zeros(self.max_entities, np.float32)
            own = np.zeros(self.max_entities, np.float32)
            for i in range(n):
                z = int(self._host_zone[i])
                if z in my_zones:
                    vis[i] = 1.0
                    own[i] = 1.0
            sighted = self.zone in my_zones

            ent = base.copy()
            ent[:, _F_VISIBLE_TO_ME] = vis
            ent[:, _F_OWNED_BY_ME] = own
            if sighted:
                for i in range(n):
                    if int(self._host_zone[i]) == self.zone:
                        ent[i, _F_ATTACKER_HERE] = 1.0
            # an agent observes only what it can see: everything else is zeroed,
            # so invisible entities cannot leak state through the encoder.
            ent = ent * vis[:, None]
            ent[n:] = 0.0

            g = np.zeros(GLOBAL_FEAT_DIM, np.float32)
            for z in my_zones:
                g[_G_MYZONES + z] = 1.0
            g[_G_SIGHTED] = 1.0 if sighted else 0.0
            g[_G_MY_COMP] = (float(np.mean([self.compromised[z] for z in my_zones]))
                             if my_zones else 0.0)
            g[_G_ALL_COMP] = self.compromised.sum() / self.topo.n_zones
            g[_G_ALERT] = self.alert
            g[_G_STEP] = self.step_count / self.max_steps
            if sighted and self.seq:
                g[_G_TECH + self.tau] = 1.0

            out.append({
                "entities": ent,
                "entity_mask": valid.copy(),
                "visibility_mask": vis,
                "own_mask": own,
                "adjacency": adj,
                "action_mask": self._action_mask(ag, own, valid),
                "global_feat": g,
                "h": hv,
            })
        return out

    def _host_adjacency(self) -> np.ndarray:
        """Host-level relations: same zone, or zones joined in the zone graph."""
        n = self.topo.n_hosts
        A = np.zeros((self.max_entities, self.max_entities), np.float32)
        zs = self._host_zone[:n]
        za = np.asarray(self.topo.zone_adj)
        same = (zs[:, None] == zs[None, :])
        linked = za[np.ix_(zs, zs)] > 0
        A[:n, :n] = (same | linked).astype(np.float32)
        return A

    def _action_mask(self, agent: int, own: np.ndarray,
                     valid: np.ndarray) -> np.ndarray:
        """(N_ACTIONS, max_entities): which (type, target) pairs are legal.

        A target is legal only when it is a real entity, defender-owned, and
        owned by THIS agent. Padded, invisible, foreign and non-existent targets
        are all masked out.
        """
        m = np.zeros((N_ACTIONS, self.max_entities), np.float32)
        legal = own * valid
        m[:, :] = legal[None, :]
        return m

    # ── interfaces shared with env_v2 ───────────────────────────────────────
    def global_state(self) -> np.ndarray:
        """Centralised state for the QMIX mixer. Width is fixed by MAX_ZONES so
        one mixer serves every topology size."""
        comp = np.zeros(MAX_ZONES, np.float32)
        comp[:self.topo.n_zones] = self.compromised
        pos = np.zeros(MAX_ZONES, np.float32)
        pos[self.zone] = 1.0
        extra = np.array([self.alert, self.step_count / self.max_steps,
                          self.ema_align, self.topo.n_zones / MAX_ZONES,
                          self.topo.n_hosts / self.max_entities], np.float32)
        return np.concatenate([comp, pos, extra]).astype(np.float32)

    @property
    def state_dim(self) -> int:
        return 2 * MAX_ZONES + 5

    def padded_sequence(self):
        """RIGHT-padded, identical contract to env_v2.padded_sequence()."""
        s = self.seq[-MAX_SEQ_LEN:]
        n = len(s)
        out = np.full(MAX_SEQ_LEN, PAD_ID, dtype=np.int64)
        if n:
            out[:n] = s
        return out, max(n, 1)

    def legal_targets(self, agent: int) -> np.ndarray:
        """Entity ids this agent may target (never empty for a valid topology)."""
        return np.nonzero(self._host_agent[:self.topo.n_hosts] == agent)[0]


# ── control-mode equivalence against env_v2 ─────────────────────────────────

def equivalence_report(n_episodes: int = 200, max_steps: int = 40,
                       seed0: int = 0, verbose: bool = True) -> Dict:
    """Run both environments on identical seeds and identical action TYPES and
    compare full trajectories, not summary statistics.

    The entity environment is given, for each agent, a target drawn from that
    agent's own zone -- which on the canonical topology is the only thing it can
    legally target anyway. Any divergence in technique, zone, reward, capture
    probability or termination is reported per field.
    """
    from env_v2 import DeceptionEnvV2, N_AGENTS

    profiles, _ = build_profiles_from_camlds()
    topo = canonical_topology()
    fields = ["technique_id", "zone", "responsible_agent", "alignment",
              "p_capture", "captured", "reached_objective", "blind"]
    mismatch = {f: 0 for f in fields}
    mismatch["reward"] = 0
    mismatch["done"] = 0
    n_steps = 0
    ep_stats = {"v2_return": [], "v3_return": [], "v2_len": [], "v3_len": [],
                "v2_cap": [], "v3_cap": []}

    for ep in range(n_episodes):
        s = seed0 + ep
        e2 = DeceptionEnvV2(profiles=profiles, max_steps=max_steps, seed=s)
        e3 = EntityDeceptionEnv(topology=topo, profiles=profiles,
                                max_steps=max_steps, seed=s)
        # identical action-type sequence, drawn from an independent stream
        arng = np.random.default_rng(10_000 + s)
        r2sum = r3sum = 0.0
        l2 = l3 = 0
        d2 = d3 = False
        while not (d2 or d3):
            types = arng.integers(0, N_ACTIONS, size=N_AGENTS).tolist()
            _, rw2, d2, i2 = e2.step(types)
            comp = [(t, int(e3.legal_targets(a)[0])) for a, t in enumerate(types)]
            _, rw3, d3, i3 = e3.step(comp)
            n_steps += 1
            for f in fields:
                if i2[f] != i3[f]:
                    mismatch[f] += 1
            if abs(rw2[0] - rw3[0]) > 1e-12:
                mismatch["reward"] += 1
            if d2 != d3:
                mismatch["done"] += 1
            r2sum += rw2[0]; r3sum += rw3[0]
            l2 += 1; l3 += 1
        ep_stats["v2_return"].append(r2sum); ep_stats["v3_return"].append(r3sum)
        ep_stats["v2_len"].append(l2); ep_stats["v3_len"].append(l3)
        ep_stats["v2_cap"].append(float(e2.captured))
        ep_stats["v3_cap"].append(float(e3.captured))

    total = sum(mismatch.values())
    if verbose:
        print("=" * 84)
        print("  FIXED-ENVIRONMENT EQUIVALENCE  (env_v2  vs  env_entity @ canonical)")
        print("=" * 84)
        print(f"  {n_episodes} episodes, {n_steps} steps, identical seeds and "
              f"action types")
        print(f"  {'field':<22} {'mismatches':>12}")
        print("  " + "-" * 36)
        for k, v in mismatch.items():
            print(f"  {k:<22} {v:>12}")
        print("  " + "-" * 36)
        print(f"  {'TOTAL':<22} {total:>12}")
        for k in ("return", "len", "cap"):
            a = float(np.mean(ep_stats[f"v2_{k}"]))
            b = float(np.mean(ep_stats[f"v3_{k}"]))
            print(f"  mean {k:<8} v2={a:.6f}  v3={b:.6f}  "
                  f"delta={b - a:+.2e}")
        print(f"\n  VERDICT: {'EXACT EQUIVALENCE' if total == 0 else 'DIVERGENCE'}")
        print("=" * 84)
    return {"mismatch": mismatch, "n_steps": n_steps, "total": total,
            "episode_stats": {k: float(np.mean(v)) for k, v in ep_stats.items()}}


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    rep = equivalence_report(n_episodes=200)
    raise SystemExit(0 if rep["total"] == 0 else 1)
