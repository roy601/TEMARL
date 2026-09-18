# -*- coding: utf-8 -*-
"""
TEMARL v7 — history-encoder arms, capacity-matched
==================================================
Five arms feed the shared SIEM intent embedding h to every agent:

  Transformer-RoPE   2 layers, 4 heads, d_ff 128 (the COMISET configuration)
  GRU / LSTM         recurrent controls, packed sequences (no PAD leakage)
  SetEncoder         order-free control: any permutation gives the same h
  NoHistory          h == 0: measures what the shared intent channel is worth

All four encoders emit d_model = 64, so the policy network is identical across
arms. Their TRUNK parameter counts are matched to the Transformer's within
+-10% by the same exhaustive width search `encoders.match_capacity` uses (it
covers GRU and Set; the LSTM search is added here with the identical rule), so
no architecture contrast can be a capacity contrast.
"""

from __future__ import annotations

import torch

import _frozen  # noqa: F401
from encoders import (GRUIntentEncoder, LSTMIntentEncoder, SetIntentEncoder,
                      match_capacity)
from encoders_rope import TransformerRoPE

ARMS = ("Transformer-RoPE", "GRU", "LSTM", "SetEncoder", "NoHistory")
H_DIM = 64
TRANSFORMER_KW = {"n_layers": 2, "n_heads": 4, "d_ff": 128}

_SPEC = None


def _n(params):
    return sum(p.numel() for p in params)


def arm_specs() -> dict:
    """Constructor kwargs per arm, capacity-matched to the Transformer."""
    global _SPEC
    if _SPEC is not None:
        return _SPEC
    target = _n(TransformerRoPE(**TRANSFORMER_KW).trunk_parameters())
    m = match_capacity(target)
    best = None
    for hid in range(32, 200, 2):
        for nl in (1, 2, 3):
            p = _n(LSTMIntentEncoder(hidden=hid, n_layers=nl).trunk_parameters())
            d = abs(p - target)
            if best is None or d < best[0]:
                best = (d, {"hidden": hid, "n_layers": nl}, p)
    _SPEC = {
        "target_trunk_params": target,
        "Transformer-RoPE": {"kwargs": dict(TRANSFORMER_KW), "params": target},
        "GRU": {"kwargs": m["GRU"]["kwargs"], "params": m["GRU"]["params"]},
        "LSTM": {"kwargs": best[1], "params": best[2]},
        "SetEncoder": {"kwargs": m["SetEncoder"]["kwargs"],
                       "params": m["SetEncoder"]["params"]},
        "NoHistory": {"kwargs": {}, "params": 0},
    }
    for k in ("GRU", "LSTM", "SetEncoder"):
        rel = (_SPEC[k]["params"] - target) / target
        if abs(rel) > 0.10:
            raise RuntimeError(f"{k} trunk not capacity-matched: {rel:+.1%}")
    return _SPEC


def build_encoder(arm: str):
    """A fresh encoder for `arm` (None for NoHistory)."""
    if arm == "NoHistory":
        return None
    kw = arm_specs()[arm]["kwargs"]
    cls = {"Transformer-RoPE": TransformerRoPE, "GRU": GRUIntentEncoder,
           "LSTM": LSTMIntentEncoder, "SetEncoder": SetIntentEncoder}[arm]
    return cls(**kw)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    s = arm_specs()
    print("trunk parameter target (Transformer-RoPE): %d" % s["target_trunk_params"])
    for a in ARMS:
        enc = build_encoder(a)
        tp = _n(enc.trunk_parameters()) if enc is not None else 0
        tot = _n(enc.parameters()) if enc is not None else 0
        rel = (tp - s["target_trunk_params"]) / s["target_trunk_params"]
        print("  %-17s kwargs %-32s trunk %6d (%+.1f%%)  total %6d"
              % (a, s[a]["kwargs"], tp, 100 * rel if enc is not None else 0.0, tot))
    x = torch.randint(0, 80, (3, 16)); L = torch.tensor([16, 5, 1])
    for a in ARMS[:4]:
        h = build_encoder(a).eval()(x, L)
        assert h.shape == (3, 64), (a, h.shape)
    print("  all encoders emit (B, 64)")
