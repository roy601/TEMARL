# -*- coding: utf-8 -*-
"""
TEMARL v3 — Entity policy: network encoder x history encoder
=============================================================
Fuses two independent representations through the EXISTING GMU trunk
(`policy.GatedFusionTrunk`, after Arevalo et al., ICLR 2017 Workshop):

    state branch  <- [ network embedding | per-agent global features ]
    intent branch <- h, the attacker-history embedding from `encoders.py`

The two encoder families are varied independently, because they answer different
questions:

    network encoder  : EntityTransformer  vs  DeepSets      (H6 / H7)
    history encoder  : Transformer / GRU / SetEncoder       (already tested)

Composite action (action_type, target_entity) is produced by a factored head:

    type   : a linear head on the fused vector -> N_ACTIONS logits
    target : a POINTER head scoring each entity against the fused vector, then
             masked so only entities this agent legally owns can be selected

Masking is applied to LOGITS before the softmax, so illegal targets receive
exactly zero probability rather than a small one.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from d3fend_payoff import N_ACTIONS
from entity_encoders import NET_EMB_DIM, EntityEncoder, match_entity_capacity
from env_entity import GLOBAL_FEAT_DIM, _G_SIGHTED
from policy import BRANCH_DIM, GatedFusionTrunk

_MASK_NEG = -1e9          # logit for an illegal action: exactly zero probability


class EntityAgentNet(nn.Module):
    """Per-agent network: entity encoder + GMU fusion + factored action heads."""

    def __init__(self, entity_encoder: EntityEncoder, h_dim: int = 64,
                 gate_bias: float = 2.0, state_masking_prob: float = 0.0,
                 head_dim: int = 64):
        super().__init__()
        self.net_enc = entity_encoder
        self.h_dim = h_dim
        self.state_dim = NET_EMB_DIM + GLOBAL_FEAT_DIM
        self.trunk = GatedFusionTrunk(
            state_dim=self.state_dim, h_dim=h_dim, gate_bias=gate_bias,
            sighted_idx=NET_EMB_DIM + _G_SIGHTED,
            state_masking_prob=state_masking_prob)
        self.type_head = nn.Sequential(
            nn.Linear(BRANCH_DIM, head_dim), nn.ReLU(),
            nn.Linear(head_dim, N_ACTIONS))
        self.value_head = nn.Sequential(
            nn.Linear(BRANCH_DIM, head_dim), nn.ReLU(), nn.Linear(head_dim, 1))
        # pointer head: project the fused vector into per-entity space and score
        self.point = nn.Linear(BRANCH_DIM, self.net_enc.per_entity_dim)

    # ── forward ─────────────────────────────────────────────────────────────
    def _fused(self, obs: Dict[str, torch.Tensor], entropy=None):
        per_ent, net_emb = self.net_enc.forward_full(
            obs["entities"], obs["entity_mask"], obs.get("adjacency"))
        state = torch.cat([net_emb, obs["global_feat"]], dim=-1)
        fused, gate, _ = self.trunk(torch.cat([state, obs["h"]], dim=-1), entropy)
        return fused, gate, per_ent

    def forward(self, obs, entropy=None):
        fused, gate, per_ent = self._fused(obs, entropy)
        type_logits = self.type_head(fused)
        q = self.point(fused).unsqueeze(1)                 # (B,1,d_ent)
        target_logits = (q * per_ent).sum(-1)              # (B,N) pointer scores
        legal = (obs["own_mask"] * obs["entity_mask"])
        target_logits = target_logits.masked_fill(legal < 0.5, _MASK_NEG)
        return type_logits, target_logits, gate

    def value(self, obs, entropy=None):
        fused, _, _ = self._fused(obs, entropy)
        return self.value_head(fused).squeeze(-1)

    # ── parameter groups (mirrors policy.AgentNet's decoupling) ────────────
    def actor_parameters(self):
        return (list(self.net_enc.parameters()) + list(self.trunk.parameters())
                + list(self.type_head.parameters()) + list(self.point.parameters()))

    def critic_parameters(self):
        return list(self.value_head.parameters())

    def n_params(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


def obs_to_tensors(obs_list: Sequence[Dict[str, np.ndarray]], device="cpu"
                   ) -> List[Dict[str, torch.Tensor]]:
    """Convert one env observation (a list of per-agent dicts) to batched tensors
    of batch size 1 each."""
    out = []
    for o in obs_list:
        out.append({k: torch.as_tensor(v, dtype=torch.float32,
                                       device=device).unsqueeze(0)
                    for k, v in o.items()})
    return out


def stack_obs(obs_dicts: Sequence[Dict[str, np.ndarray]], device="cpu"
              ) -> Dict[str, torch.Tensor]:
    """Stack a list of single-agent observation dicts into one batch."""
    keys = obs_dicts[0].keys()
    return {k: torch.as_tensor(np.stack([o[k] for o in obs_dicts]),
                               dtype=torch.float32, device=device) for k in keys}


class EntityController:
    """Holds one EntityAgentNet per agent and produces composite actions."""

    def __init__(self, n_agents: int, entity_encoder_name: str = "EntityTransformer",
                 h_dim: int = 64, gate_bias: float = 2.0,
                 state_masking_prob: float = 0.0, device: str = "cpu",
                 share_parameters: bool = True):
        self.n_agents = n_agents
        self.device = device
        self.share = share_parameters
        suite, _ = match_entity_capacity()
        if entity_encoder_name not in suite:
            raise ValueError(f"unknown entity encoder {entity_encoder_name}")
        if share_parameters:
            net = EntityAgentNet(suite[entity_encoder_name], h_dim=h_dim,
                                 gate_bias=gate_bias,
                                 state_masking_prob=state_masking_prob).to(device)
            self.nets = [net] * n_agents
            self._unique = [net]
        else:
            self.nets, self._unique = [], []
            for _ in range(n_agents):
                s, _c = match_entity_capacity()
                nn_ = EntityAgentNet(s[entity_encoder_name], h_dim=h_dim,
                                     gate_bias=gate_bias,
                                     state_masking_prob=state_masking_prob).to(device)
                self.nets.append(nn_); self._unique.append(nn_)

    # ── acting ──────────────────────────────────────────────────────────────
    def act(self, obs_list, entropy=None, greedy: bool = True, rng=None
            ) -> List[Tuple[int, int]]:
        ts = obs_to_tensors(obs_list, self.device)
        acts = []
        with torch.no_grad():
            for ag in range(self.n_agents):
                tl, gl, _ = self.nets[ag](ts[ag], entropy)
                if greedy:
                    t = int(tl.argmax(-1).item())
                    g = int(gl.argmax(-1).item())
                else:
                    pt = F.softmax(tl, -1).cpu().numpy()[0]
                    pg = F.softmax(gl, -1).cpu().numpy()[0]
                    r = rng if rng is not None else np.random.default_rng()
                    t = int(r.choice(len(pt), p=pt))
                    g = int(r.choice(len(pg), p=pg))
                acts.append((t, g))
        return acts

    def actor_parameters(self):
        ps = []
        for n in self._unique:
            ps += n.actor_parameters()
        return ps

    def critic_parameters(self):
        ps = []
        for n in self._unique:
            ps += n.critic_parameters()
        return ps

    def parameters(self):
        ps = []
        for n in self._unique:
            ps += list(n.parameters())
        return ps

    def n_params(self) -> int:
        return sum(n.n_params() for n in self._unique)

    def train(self):
        for n in self._unique:
            n.train()

    def eval(self):
        for n in self._unique:
            n.eval()

    def state_dict(self):
        return {f"net{i}": n.state_dict() for i, n in enumerate(self._unique)}

    def load_state_dict(self, sd):
        for i, n in enumerate(self._unique):
            n.load_state_dict(sd[f"net{i}"])


# ── self-test ────────────────────────────────────────────────────────────────

def _self_test() -> bool:
    import sys
    from env_entity import EntityDeceptionEnv
    from topology import canonical_topology, generate_topology

    ok = True
    print("=" * 88)
    print("  TEMARL v3 — ENTITY POLICY SELF-TEST")
    print("=" * 88)
    torch.manual_seed(0)

    for enc_name in ("EntityTransformer", "DeepSets"):
        print(f"\n  --- {enc_name} ---")
        ctrl = EntityController(4, enc_name)
        print(f"    parameters: {ctrl.n_params():,}")

        # acts on the canonical topology and on a larger unseen one
        for topo, label in ((canonical_topology(), "canonical 5-zone"),
                            (generate_topology(seed=99, n_zones=10), "unseen 10-zone")):
            env = EntityDeceptionEnv(topology=topo, seed=0)
            obs = env.reset()
            acts = ctrl.act(obs)
            legal = all(a[1] in env.legal_targets(i).tolist()
                        for i, a in enumerate(acts))
            _, rw, done, info = env.step(acts)
            fin = all(np.isfinite(rw))
            print(f"    {label:<18} actions={acts}  legal={legal}  "
                  f"reward={rw[0]:+.4f}  {'PASS' if legal and fin else 'FAIL'}")
            ok &= legal and fin

        # masking: illegal targets must have exactly zero probability
        env = EntityDeceptionEnv(topology=canonical_topology(), seed=1)
        obs = env.reset()
        ts = obs_to_tensors(obs)
        with torch.no_grad():
            _, gl, _ = ctrl.nets[0](ts[0])
        p = F.softmax(gl, -1)[0].numpy()
        legal_ids = set(env.legal_targets(0).tolist())
        leak = float(sum(p[i] for i in range(len(p)) if i not in legal_ids))
        print(f"    illegal-target probability mass = {leak:.3e}  "
              f"{'PASS' if leak < 1e-12 else 'FAIL'}")
        ok &= leak < 1e-12

        # gradient reaches BOTH branches (network encoder and history branch).
        # NB: h MUST be non-zero here. reset() defaults h to a zero vector, and a
        # zero input makes the intent branch's weight gradient identically zero
        # (dLinear/dW = h = 0, and LayerNorm of an all-zero vector is degenerate).
        # In training h always comes from the frozen history encoder and is
        # non-zero, so probing with zeros would be a false negative.
        ctrl.train()
        obs = env.observations(h=np.random.default_rng(0).normal(size=64))
        ts = obs_to_tensors(obs)
        tl, gl2, _ = ctrl.nets[0](ts[0])
        loss = tl.sum() + gl2.clamp(min=-1e3).sum()
        loss.backward()
        gnet = sum(p.grad.abs().sum().item() for p in ctrl.nets[0].net_enc.parameters()
                   if p.grad is not None)
        gint = sum(p.grad.abs().sum().item()
                   for p in ctrl.nets[0].trunk.branch_intent.parameters()
                   if p.grad is not None)
        print(f"    grad |network encoder| = {gnet:.3e}   "
              f"|history branch| = {gint:.3e}   "
              f"{'PASS' if gnet > 0 and gint > 0 else 'FAIL'}")
        ok &= gnet > 0 and gint > 0

    print("\n" + "=" * 88)
    print(f"  ENTITY POLICY: {'ALL PASS' if ok else 'FAILURES PRESENT'}")
    print("=" * 88)
    return ok


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(0 if _self_test() else 1)
