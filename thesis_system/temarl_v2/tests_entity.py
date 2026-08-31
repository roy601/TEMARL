# -*- coding: utf-8 -*-
"""
TEMARL v3 — Test suite
=======================
Every test required for the entity environment, its encoders, and its policy,
plus the inherited gates that must not regress. Run directly:

    python tests_entity.py            # all tests
    python tests_entity.py --fast     # skip the 200-episode equivalence sweep

Exit code is 0 only if every test passes. Nothing here tunes a threshold to
make a test pass: thresholds come from `prereg_v3.INHERITED_GATES`.
"""

from __future__ import annotations

import argparse
import sys
import traceback

import numpy as np
import torch
import torch.nn.functional as F

import prereg_v3 as PR

_RESULTS = []


def check(name: str, passed: bool, detail: str = ""):
    _RESULTS.append((name, bool(passed), detail))
    print(f"  [{'PASS' if passed else 'FAIL'}] {name}"
          + (f"   {detail}" if detail else ""))
    return passed


# ── 1. topology ──────────────────────────────────────────────────────────────

def test_seed_reproducibility():
    from topology import generate_topology
    a = generate_topology(seed=42, n_zones=7)
    b = generate_topology(seed=42, n_zones=7)
    c = generate_topology(seed=43, n_zones=7)
    check("seed reproducibility: same seed -> identical hash",
          a.content_hash() == b.content_hash(), a.content_hash())
    check("seed reproducibility: different seed -> different hash",
          a.content_hash() != c.content_hash())


def test_graph_validity():
    from topology import generate_topology, validate_topology
    bad = []
    for nz in (5, 6, 7, 9, 11, 13):
        for s in range(8):
            t = generate_topology(seed=s * 31 + nz, n_zones=nz,
                                  n_agents=PR.N_AGENTS)
            ok, probs = validate_topology(t)
            if not ok:
                bad.append((nz, s, probs))
    check("graph validity & connectivity over 48 topologies", not bad,
          "" if not bad else str(bad[:2]))


def test_canonical_reproduction():
    import env_v2 as e2
    from topology import canonical_topology, validate_topology
    c = canonical_topology(n_agents=e2.N_AGENTS)
    ok, probs = validate_topology(c)
    same = (c.zones == e2.ZONES
            and sorted(c.defended_zones) == sorted(e2.DEFENDED_ZONES)
            and c.entry_zone == e2.ATTACKER_ZONE
            and c.n_agents == e2.N_AGENTS
            and all(c.agent_of_zone[z] == e2.ZONE_TO_AGENT[z]
                    for z in e2.DEFENDED_ZONES)
            and all(sorted(h.name for h in c.hosts_in_zone(i))
                    == sorted(e2.ZONE_HOSTS[z]) for i, z in enumerate(e2.ZONES)))
    check("canonical 5-zone reproduces env_v2 constants", ok and same)


# ── 2. environment ───────────────────────────────────────────────────────────

def test_fixed_environment_equivalence(fast: bool = False):
    from env_entity import equivalence_report
    rep = equivalence_report(n_episodes=25 if fast else 200, verbose=False)
    check("fixed-environment equivalence (rewards/transitions/termination)",
          rep["total"] == PR.INHERITED_GATES["env_v2_equivalence_mismatches"],
          f"{rep['total']} mismatches over {rep['n_steps']} steps")


def test_reward_and_termination_preserved():
    """The v3 constants must be the very objects env_v2 defines, not copies."""
    import env_v2 as e2
    import env_entity as e3
    same = (e3.W_ENGAGE is e2.W_ENGAGE and e3.W_ALIGN is e2.W_ALIGN
            and e3.TERMINAL_PENALTY is e2.TERMINAL_PENALTY
            and e3.GOAL_STEPS is e2.GOAL_STEPS
            and e3.CAP_P_MIN is e2.CAP_P_MIN and e3.CAP_P_MAX is e2.CAP_P_MAX
            and e3.CAP_K is e2.CAP_K and e3.CAP_EMA is e2.CAP_EMA
            and e3.CAP_A_REF is e2.CAP_A_REF)
    check("reward/capture/termination constants imported from env_v2, not copied",
          same)


def test_visibility_restriction():
    """An agent must observe nothing about zones it does not own."""
    from env_entity import EntityDeceptionEnv
    from topology import generate_topology
    env = EntityDeceptionEnv(topology=generate_topology(seed=5, n_zones=7,
                                                        n_agents=PR.N_AGENTS),
                             seed=3)
    env.reset()
    for _ in range(6):
        acts = [(1, int(env.legal_targets(a)[0])) for a in range(env.n_agents)]
        env.step(acts)
    obs = env.observations()
    leaks = 0
    for ag, o in enumerate(obs):
        invis = (o["visibility_mask"] < 0.5)
        if np.abs(o["entities"][invis]).sum() > 0:
            leaks += 1
    check("per-agent visibility: invisible entities are all-zero", leaks == 0,
          f"{leaks} agents leaked")


def test_action_masking():
    from env_entity import EntityDeceptionEnv
    from topology import generate_topology
    env = EntityDeceptionEnv(topology=generate_topology(seed=11, n_zones=6,
                                                        n_agents=PR.N_AGENTS),
                             seed=4)
    obs = env.reset()
    bad = 0
    for ag, o in enumerate(obs):
        legal = set(env.legal_targets(ag).tolist())
        m = o["action_mask"]
        for t in range(m.shape[0]):
            allowed = set(np.nonzero(m[t])[0].tolist())
            if allowed != legal:
                bad += 1
    check("action mask == exactly this agent's legal targets", bad == 0)

    # the environment must REFUSE an illegal target rather than silently accept
    refused = False
    foreign = [i for i in range(env.topo.n_hosts)
               if i not in set(env.legal_targets(0).tolist())]
    try:
        env.step([(1, foreign[0])] + [(0, int(env.legal_targets(a)[0]))
                                      for a in range(1, env.n_agents)])
    except ValueError:
        refused = True
    check("environment rejects an unauthorised target", refused)

    # padded slots are never legal
    padded_legal = any(o["action_mask"][:, env.topo.n_hosts:].sum() > 0
                       for o in obs)
    check("padded entities are never legal targets", not padded_legal)


def test_zero_unknown_camlds():
    import json
    import os
    from vocab_v2 import UNK_ID, technique_to_id
    here = os.path.dirname(os.path.abspath(__file__))
    p = os.path.join(here, "..", "data", "camlds_grounding_verified.json")
    d = json.load(open(p, encoding="utf-8"))
    codes = [c for v in d["runs"].values() for c in v["sequence"]]
    unk = sum(1 for c in codes if technique_to_id(c) == UNK_ID)
    check("zero unknown CAM-LDS labels",
          unk == PR.INHERITED_GATES["vocab_unk_camlds"],
          f"{unk}/{len(codes)} UNK")


# ── 3. encoders ──────────────────────────────────────────────────────────────

def _batch(B=5, N=18):
    from env_entity import ENTITY_FEAT_DIM
    g = torch.Generator().manual_seed(0)
    mask = torch.zeros(B, N)
    for i in range(B):
        mask[i, :int(torch.randint(2, N, (1,), generator=g))] = 1.0
    ent = torch.randn(B, N, ENTITY_FEAT_DIM, generator=g) * mask.unsqueeze(-1)
    adj = (torch.rand(B, N, N, generator=g) < 0.4).float()
    adj = ((adj + adj.transpose(1, 2)) > 0).float()
    adj = adj * mask.unsqueeze(1) * mask.unsqueeze(2)
    return ent, mask, adj


def test_encoder_invariances():
    from entity_encoders import match_entity_capacity
    from env_entity import ENTITY_FEAT_DIM
    suite, counts = match_entity_capacity()
    spread = (max(counts.values()) - min(counts.values())) / max(counts.values())
    check("entity encoder capacity matched",
          spread <= PR.INHERITED_GATES["capacity_spread_max"],
          f"spread {spread:.1%}  {counts}")

    ent, mask, adj = _batch()
    for name, enc in suite.items():
        enc.eval()
        with torch.no_grad():
            out = enc(ent, mask, adj)
        check(f"{name}: finite output", bool(torch.isfinite(out).all()))

        ent2 = torch.cat([ent, torch.randn(ent.shape[0], 9, ENTITY_FEAT_DIM)], 1)
        mask2 = torch.cat([mask, torch.zeros(mask.shape[0], 9)], 1)
        adj2 = torch.zeros(adj.shape[0], adj.shape[1] + 9, adj.shape[2] + 9)
        adj2[:, :adj.shape[1], :adj.shape[2]] = adj
        with torch.no_grad():
            out2 = enc(ent2, mask2, adj2)
        e = (out - out2).abs().max().item()
        check(f"{name}: padding invariance",
              e < PR.INHERITED_GATES["entity_padding_invariance_max"], f"{e:.2e}")

        perm = torch.randperm(ent.shape[1])
        with torch.no_grad():
            outp = enc(ent[:, perm], mask[:, perm], adj[:, perm][:, :, perm])
        e = (out - outp).abs().max().item()
        check(f"{name}: permutation invariance (global output)",
              e < PR.INHERITED_GATES["entity_permutation_invariance_max"],
              f"{e:.2e}")

        okv = True
        for k in (1, 3, 30, 48):
            with torch.no_grad():
                o = enc(torch.randn(2, k, ENTITY_FEAT_DIM), torch.ones(2, k),
                        torch.ones(2, k, k))
            okv &= tuple(o.shape) == (2, 64) and bool(torch.isfinite(o).all())
        check(f"{name}: variable-size batching (N=1/3/30/48)", okv)


def test_gradient_flow_both_branches():
    from env_entity import EntityDeceptionEnv
    from policy_entity import EntityController, obs_to_tensors
    from topology import canonical_topology
    for enc_name in PR.NETWORK_ENCODERS:
        ctrl = EntityController(PR.N_AGENTS, enc_name)
        ctrl.train()
        env = EntityDeceptionEnv(topology=canonical_topology(), seed=0)
        env.reset()
        # h must be non-zero: a zero h gives a zero weight-gradient through the
        # intent branch by construction, which would be a false negative.
        obs = env.observations(h=np.random.default_rng(0).normal(size=64))
        ts = obs_to_tensors(obs)
        tl, gl, _ = ctrl.nets[0](ts[0])
        v = ctrl.nets[0].value(ts[0])
        loss = (tl * torch.randn_like(tl)).sum() + v.sum() \
            + (gl.clamp(min=-1e3) * torch.randn_like(gl)).sum()
        loss.backward()
        gnet = sum(p.grad.abs().sum().item()
                   for p in ctrl.nets[0].net_enc.parameters() if p.grad is not None)
        gh = sum(p.grad.abs().sum().item()
                 for p in ctrl.nets[0].trunk.branch_intent.parameters()
                 if p.grad is not None)
        check(f"{enc_name}: gradient flows through BOTH branches",
              gnet > 0 and gh > 0, f"net={gnet:.2e} history={gh:.2e}")


def test_finite_policy_outputs_across_sizes():
    from env_entity import EntityDeceptionEnv
    from policy_entity import EntityController
    from topology import generate_topology
    for enc_name in PR.NETWORK_ENCODERS:
        ctrl = EntityController(PR.N_AGENTS, enc_name)
        ok = True
        for nz in (5, 7, 9, 13):
            env = EntityDeceptionEnv(
                topology=generate_topology(seed=nz, n_zones=nz,
                                           n_agents=PR.N_AGENTS), seed=1)
            obs = env.reset()
            acts = ctrl.act(obs)
            ok &= all(a[1] in env.legal_targets(i).tolist()
                      for i, a in enumerate(acts))
            _, rw, _, _ = env.step(acts)
            ok &= bool(np.all(np.isfinite(rw)))
        check(f"{enc_name}: finite outputs & legal actions on 5/7/9/13 zones", ok)


# ── 4. inherited gates ───────────────────────────────────────────────────────

def test_inherited_gates():
    from d3fend_payoff import PAYOFF, headroom
    from vocab_v2 import NUM_TECHNIQUES
    check("payoff matrix spans the expanded vocabulary",
          PAYOFF.shape[0] == NUM_TECHNIQUES,
          f"{PAYOFF.shape} vs {NUM_TECHNIQUES} techniques")

    import json
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    fz = json.load(open(os.path.join(here, "payoff_frozen.json"), encoding="utf-8"))
    A = np.array(fz["payoff_matrix"], dtype=np.float64)
    check("frozen payoff rows 0-77 unchanged (never refitted)",
          np.array_equal(A[:78], PAYOFF[:78]),
          f"sum {A[:78].sum():.4f}")


# ── runner ───────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fast", action="store_true")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("=" * 90)
    print("  TEMARL v3 — TEST SUITE")
    print("=" * 90)
    groups = [
        ("topology", [test_seed_reproducibility, test_graph_validity,
                      test_canonical_reproduction]),
        ("environment", [lambda: test_fixed_environment_equivalence(args.fast),
                         test_reward_and_termination_preserved,
                         test_visibility_restriction, test_action_masking,
                         test_zero_unknown_camlds]),
        ("encoders", [test_encoder_invariances, test_gradient_flow_both_branches,
                      test_finite_policy_outputs_across_sizes]),
        ("inherited gates", [test_inherited_gates]),
    ]
    for gname, fns in groups:
        print(f"\n  ── {gname} ──")
        for fn in fns:
            try:
                fn()
            except Exception:
                check(getattr(fn, "__name__", "lambda"), False, "EXCEPTION")
                traceback.print_exc()

    n_pass = sum(1 for _, p, _ in _RESULTS if p)
    n = len(_RESULTS)
    print("\n" + "=" * 90)
    print(f"  {n_pass}/{n} PASSED")
    if n_pass < n:
        print("  FAILURES:")
        for name, p, d in _RESULTS:
            if not p:
                print(f"    - {name}  {d}")
    print("=" * 90)
    return 0 if n_pass == n else 1


if __name__ == "__main__":
    raise SystemExit(main())
