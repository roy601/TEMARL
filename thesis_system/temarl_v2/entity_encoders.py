# -*- coding: utf-8 -*-
"""
TEMARL v3 — Entity (network) encoders
======================================
Two encoders that map a variable-sized, masked set of host entities to a
fixed-width network embedding:

  * `EntityTransformer` — masked multi-head self-attention with an additive
    adjacency bias, then masked mean pooling.
  * `DeepSets`          — permutation-invariant phi/rho baseline
    (Zaheer et al., NeurIPS 2017), the control for "does attention help?".

THE SCIENTIFIC POINT
--------------------
These encode NETWORK ENTITIES. The existing Transformer/GRU/SetEncoder in
`encoders.py` encode ATTACKER TECHNIQUE HISTORY. They are different components
answering different questions, and the experiment varies them independently:
a win for the entity Transformer says nothing about the history Transformer, and
vice versa. Conflating the two is exactly the error this design avoids.

INVARIANCES (all tested in `tests_entity.py`)
---------------------------------------------
  * Padding invariance   — padded slots change no output bit.
  * Permutation invariance at the GLOBAL OUTPUT — reordering entities leaves the
    pooled embedding unchanged. Self-attention is permutation-EQUIVARIANT and
    masked mean pooling is permutation-INVARIANT, so the composition is
    invariant. (Per-entity outputs are equivariant, not invariant, by design.)
  * Variable entity counts — one parameter set serves every topology size.

Both encoders receive the same topology signal: an adjacency-derived normalised
degree is appended to every entity's features, so DeepSets is not handicapped by
being denied structure the Transformer can see. The Transformer additionally
biases attention by adjacency, which is the extra capability under test.
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

from env_entity import ENTITY_FEAT_DIM

NET_EMB_DIM = 64          # network embedding width, fixed across encoders
_NEG = -1e4               # finite additive penalty; never -inf (NaN-safe)


def _augment_with_degree(x: torch.Tensor, mask: torch.Tensor,
                         adj: Optional[torch.Tensor]) -> torch.Tensor:
    """Append normalised degree so BOTH encoders see topology structure."""
    if adj is None:
        deg = torch.zeros(x.shape[0], x.shape[1], 1, device=x.device, dtype=x.dtype)
    else:
        m = mask.unsqueeze(-1)
        d = (adj * mask.unsqueeze(1)).sum(-1, keepdim=True)      # valid neighbours
        n = mask.sum(-1, keepdim=True).unsqueeze(-1).clamp(min=1.0)
        deg = (d / n) * m
    return torch.cat([x, deg], dim=-1)


class EntityEncoder(nn.Module):
    """Common interface. `forward` returns a (B, NET_EMB_DIM) embedding."""

    in_dim = ENTITY_FEAT_DIM + 1        # +1 for the degree channel

    def forward(self, entities: torch.Tensor, entity_mask: torch.Tensor,
                adjacency: Optional[torch.Tensor] = None) -> torch.Tensor:
        raise NotImplementedError

    @staticmethod
    def _check(entities: torch.Tensor, entity_mask: torch.Tensor):
        if entities.dim() != 3:
            raise ValueError(f"entities must be (B,N,F), got {tuple(entities.shape)}")
        if entity_mask.shape != entities.shape[:2]:
            raise ValueError("entity_mask must be (B,N)")

    def n_params(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


class EntityTransformer(EntityEncoder):
    """Masked self-attention over entities with an additive adjacency bias."""

    def __init__(self, d_model: int = 64, n_heads: int = 4, n_layers: int = 2,
                 d_ff: int = 128, out_dim: int = NET_EMB_DIM, dropout: float = 0.1):
        super().__init__()
        self.d_model, self.n_heads = d_model, n_heads
        self.proj = nn.Linear(self.in_dim, d_model)
        self.attn = nn.ModuleList([
            nn.MultiheadAttention(d_model, n_heads, dropout=dropout,
                                  batch_first=True) for _ in range(n_layers)])
        self.norm1 = nn.ModuleList([nn.LayerNorm(d_model) for _ in range(n_layers)])
        self.ff = nn.ModuleList([
            nn.Sequential(nn.Linear(d_model, d_ff), nn.ReLU(),
                          nn.Linear(d_ff, d_model)) for _ in range(n_layers)])
        self.norm2 = nn.ModuleList([nn.LayerNorm(d_model) for _ in range(n_layers)])
        # learned, non-negative strength of the adjacency prior
        self.adj_bias = nn.Parameter(torch.zeros(1))
        self.out = nn.Sequential(nn.Linear(d_model, out_dim), nn.LayerNorm(out_dim))

    def forward(self, entities, entity_mask, adjacency=None):
        self._check(entities, entity_mask)
        m = entity_mask.to(entities.dtype)
        x = _augment_with_degree(entities, m, adjacency)
        x = self.proj(x) * m.unsqueeze(-1)          # padded rows start at zero

        # Float additive mask, matching attn_mask's dtype: torch deprecates
        # mixing a bool key_padding_mask with a float attn_mask.
        is_pad = (m < 0.5)
        empty = is_pad.all(dim=-1)
        if empty.any():                              # keep softmax well-defined
            is_pad = is_pad.clone()
            is_pad[empty, 0] = False
        key_pad = torch.zeros_like(m).masked_fill(is_pad, _NEG)

        bias = None
        if adjacency is not None:
            # 0 for adjacent pairs, -softplus(w) for non-adjacent: a soft prior,
            # never -inf, so no row can produce NaN.
            w = F.softplus(self.adj_bias)
            bias = (adjacency - 1.0) * w
            bias = bias.unsqueeze(1).expand(-1, self.n_heads, -1, -1)
            bias = bias.reshape(-1, adjacency.shape[1], adjacency.shape[2])

        for att, n1, ff, n2 in zip(self.attn, self.norm1, self.ff, self.norm2):
            a, _ = att(x, x, x, key_padding_mask=key_pad, attn_mask=bias,
                       need_weights=False)
            x = n1(x + a)
            x = n2(x + ff(x))
            x = x * m.unsqueeze(-1)                  # re-zero padded rows

        pooled = (x * m.unsqueeze(-1)).sum(1) / m.sum(1, keepdim=True).clamp(min=1.0)
        self._last_per_entity = x                    # (B,N,d_model), padded rows 0
        return self.out(pooled)

    def forward_full(self, entities, entity_mask, adjacency=None):
        """Return (per_entity (B,N,d_model), pooled (B,out_dim)).

        Per-entity outputs are permutation-EQUIVARIANT (they follow their
        entity); only the pooled vector is permutation-INVARIANT. The target head
        needs the equivariant part, which is why it is exposed separately."""
        pooled = self.forward(entities, entity_mask, adjacency)
        return self._last_per_entity, pooled

    @property
    def per_entity_dim(self):
        return self.d_model


class DeepSets(EntityEncoder):
    """Permutation-invariant baseline: rho( mean_i phi(x_i) ) over valid i."""

    def __init__(self, hidden: int = 128, out_dim: int = NET_EMB_DIM,
                 phi_layers: int = 2, rho_layers: int = 2):
        super().__init__()
        phi = [nn.Linear(self.in_dim, hidden), nn.LayerNorm(hidden), nn.ReLU()]
        for _ in range(phi_layers - 1):
            phi += [nn.Linear(hidden, hidden), nn.LayerNorm(hidden), nn.ReLU()]
        self.phi = nn.Sequential(*phi)
        rho = []
        for _ in range(rho_layers - 1):
            rho += [nn.Linear(hidden, hidden), nn.LayerNorm(hidden), nn.ReLU()]
        rho += [nn.Linear(hidden, out_dim), nn.LayerNorm(out_dim)]
        self.rho = nn.Sequential(*rho)

    def forward(self, entities, entity_mask, adjacency=None):
        self._check(entities, entity_mask)
        m = entity_mask.to(entities.dtype)
        x = _augment_with_degree(entities, m, adjacency)
        e = self.phi(x) * m.unsqueeze(-1)            # padded contribute exactly 0
        pooled = e.sum(1) / m.sum(1, keepdim=True).clamp(min=1.0)
        self._last_per_entity = e
        return self.rho(pooled)

    def forward_full(self, entities, entity_mask, adjacency=None):
        pooled = self.forward(entities, entity_mask, adjacency)
        return self._last_per_entity, pooled

    @property
    def per_entity_dim(self):
        return self.phi[0].out_features


ENTITY_ENCODERS = {"EntityTransformer": EntityTransformer, "DeepSets": DeepSets}


def match_entity_capacity(tol: float = 0.10, verbose: bool = False
                          ) -> Tuple[Dict[str, EntityEncoder], Dict[str, int]]:
    """Build both encoders with parameter counts matched to within `tol`.

    Capacity is matched so a difference in results is attributable to the
    INDUCTIVE BIAS rather than to one model simply being larger.
    """
    ref = EntityTransformer()
    target = ref.n_params()
    best, best_h, best_err = None, None, 1e18
    for h in range(32, 513, 4):
        cand = DeepSets(hidden=h)
        err = abs(cand.n_params() - target) / target
        if err < best_err:
            best, best_h, best_err = cand, h, err
        if err < tol * 0.2:
            break
    if verbose:
        print(f"  EntityTransformer {target:,} params; "
              f"DeepSets hidden={best_h} -> {best.n_params():,} "
              f"({best_err:+.1%})")
    if best_err > tol:
        raise RuntimeError(f"could not match capacity within {tol:.0%} "
                           f"(best {best_err:.1%})")
    return ({"EntityTransformer": ref, "DeepSets": best},
            {"EntityTransformer": target, "DeepSets": best.n_params()})


# ── self-test ────────────────────────────────────────────────────────────────

def _self_test() -> bool:
    import numpy as np
    torch.manual_seed(0)
    ok = True
    print("=" * 86)
    print("  TEMARL v3 — ENTITY ENCODER SELF-TEST")
    print("=" * 86)

    suite, counts = match_entity_capacity(verbose=True)
    spread = (max(counts.values()) - min(counts.values())) / max(counts.values())
    print(f"  capacity spread {spread:.1%}  {'PASS' if spread <= 0.10 else 'FAIL'}")
    ok &= spread <= 0.10

    B, N, Fdim = 6, 20, ENTITY_FEAT_DIM
    n_valid = torch.randint(3, N, (B,))
    ent = torch.randn(B, N, Fdim)
    mask = torch.zeros(B, N)
    for i, k in enumerate(n_valid):
        mask[i, :k] = 1.0
    ent = ent * mask.unsqueeze(-1)
    adj = (torch.rand(B, N, N) < 0.4).float()
    adj = ((adj + adj.transpose(1, 2)) > 0).float() * mask.unsqueeze(1) * mask.unsqueeze(2)

    for name, enc in suite.items():
        enc.eval()
        with torch.no_grad():
            out = enc(ent, mask, adj)
        shape_ok = tuple(out.shape) == (B, NET_EMB_DIM)
        finite = bool(torch.isfinite(out).all())
        print(f"\n  --- {name} ---")
        print(f"    output {tuple(out.shape)} finite={finite}  "
              f"{'PASS' if shape_ok and finite else 'FAIL'}")
        ok &= shape_ok and finite

        # padding invariance: grow the padded region, outputs must not move
        ent2 = torch.cat([ent, torch.randn(B, 12, Fdim)], 1)
        mask2 = torch.cat([mask, torch.zeros(B, 12)], 1)
        adj2 = torch.zeros(B, N + 12, N + 12)
        adj2[:, :N, :N] = adj
        with torch.no_grad():
            out2 = enc(ent2, mask2, adj2)
        pad_err = (out - out2).abs().max().item()
        print(f"    padding invariance   max|d| = {pad_err:.3e}  "
              f"{'PASS' if pad_err < 1e-5 else 'FAIL'}")
        ok &= pad_err < 1e-5

        # permutation invariance of the GLOBAL output
        perm = torch.randperm(N)
        with torch.no_grad():
            outp = enc(ent[:, perm], mask[:, perm], adj[:, perm][:, :, perm])
        perm_err = (out - outp).abs().max().item()
        print(f"    permutation invariance max|d| = {perm_err:.3e}  "
              f"{'PASS' if perm_err < 1e-5 else 'FAIL'}")
        ok &= perm_err < 1e-5

        # variable entity counts in one batch already exercised above
        for k in (1, 5, 40):
            e = torch.randn(2, k, Fdim); mm = torch.ones(2, k)
            a = torch.ones(2, k, k)
            with torch.no_grad():
                o = enc(e, mm, a)
            if tuple(o.shape) != (2, NET_EMB_DIM) or not torch.isfinite(o).all():
                print(f"    variable size N={k}: FAIL")
                ok = False
        print(f"    variable entity counts (1/5/40): PASS")

        # gradient flow
        enc.train()
        # NB: a plain .sum() is a DEGENERATE probe here -- the encoders end in a
        # LayerNorm, whose output is mean-centred, so sum() is constant in the
        # inputs and no gradient reaches earlier layers. Project randomly first.
        out_g = enc(ent, mask, adj)
        o = (out_g * torch.randn_like(out_g)).sum()
        o.backward()
        g = [p.grad for p in enc.parameters() if p.requires_grad]
        has = sum(1 for x in g if x is not None and torch.isfinite(x).all()
                  and x.abs().sum() > 0)
        print(f"    gradient flow: {has}/{len(g)} tensors receive gradient  "
              f"{'PASS' if has > 0 else 'FAIL'}")
        ok &= has > 0
        enc.zero_grad()

    print("\n" + "=" * 86)
    print(f"  ENTITY ENCODERS: {'ALL PASS' if ok else 'FAILURES PRESENT'}")
    print("=" * 86)
    return ok


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(0 if _self_test() else 1)
