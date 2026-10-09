# -*- coding: utf-8 -*-
"""
Temarl_Test_v1_L1 -- command-level set encoders with a multi-label head
========================================================================
Three history encoders over sequences of COMMANDS, where each command is an
unordered set of ATT&CK parent techniques:

    (B, W, 84) multi-hot  ->  SetEmbedding  ->  trunk  ->  64-D history h
                                                        ->  Linear -> 84 logits

Shared by construction, so the comparison isolates the trunk
-------------------------------------------------------------
Every arm uses the SAME set embedding, the SAME 64-D interface, the SAME
multi-label head, and sees the SAME inputs. Only the trunk differs.

Order invariance
----------------
`SetEmbedding` is a single Linear applied to a multi-hot vector. For multi-hot
m, `Linear(m) = sum_{i in set} W[:, i] + b` -- exactly the sum of the member
techniques' embedding vectors. There is no position inside a command, so no
within-command order can be represented, let alone learned. `tests_cmd.py`
asserts this numerically by permuting label order and requiring bit-identical
output.

Positional encoding counts POSITIONS, not parameters
-----------------------------------------------------
The Transformer's sinusoidal table is a registered buffer, not a Parameter.
Growing W from 8 to 64 changes memory and compute but leaves the trainable
parameter count unchanged. `parameter_report()` separates the two so that a
window-length result is never confused with a capacity result.

Capacity matching
-----------------
GRU and LSTM hidden sizes are chosen so their trunk parameter counts land
within 10% of the Transformer's. Matching is on TRAINABLE PARAMETERS only;
runtime and memory differ substantially between attention and recurrence and
are measured separately rather than equalised.

Cell equations
--------------
`ChoGRUCell` and `ForgetGateLSTMCell` are carried over unchanged from the
audited `encoders_marl.py` of the previous study, so the equations behind any
architecture claim are the same ones already reviewed.
"""

from __future__ import annotations

import math
from functools import lru_cache

import torch
from torch import nn

import _frozen
from vocab_v2 import NUM_TECHNIQUES as NT

H_DIM = 64
DROPOUT = 0.1
ARMS = ("Transformer", "GRU", "LSTM", "OrderFree", "NoHistory")
CAPACITY_TOLERANCE = 0.10


# ── cells (equations unchanged from the audited previous study) ─────────────

class ChoGRUCell(nn.Module):
    """Cho et al. (2014), equations 5-8: U(r * h), not r * U(h)."""

    def __init__(self, input_size: int, hidden_size: int):
        super().__init__()
        self.x = nn.Linear(input_size, 3 * hidden_size)
        self.h_gates = nn.Linear(hidden_size, 2 * hidden_size, bias=False)
        self.h_candidate = nn.Linear(hidden_size, hidden_size, bias=False)

    def forward(self, x, h):
        xr, xz, xn = self.x(x).chunk(3, -1)
        hr, hz = self.h_gates(h).chunk(2, -1)
        r, z = torch.sigmoid(xr + hr), torch.sigmoid(xz + hz)
        candidate = torch.tanh(xn + self.h_candidate(r * h))
        return z * h + (1 - z) * candidate


class ForgetGateLSTMCell(nn.LSTMCell):
    """Non-peephole LSTM: c' = f*c + i*tanh(g), h' = o*tanh(c').

    Forget gate per Gers et al. (2000); PyTorch's standard tanh variant, not a
    verbatim reproduction of the 2000 experimental implementation. This is the
    SAME cell the previous study used -- note it is the forget-gate LSTM, not
    the 1997 no-forget-gate design used in the older TEMARL_version study.
    """


# ── shared pieces ───────────────────────────────────────────────────────────

class SetEmbedding(nn.Module):
    """Order-invariant command embedding: multi-hot -> sum of embeddings."""

    def __init__(self, d_model: int = H_DIM):
        super().__init__()
        self.lin = nn.Linear(NT, d_model)
        self.norm = nn.LayerNorm(d_model)
        self.drop = nn.Dropout(DROPOUT)

    def forward(self, x):                      # (B, W, NT) -> (B, W, d)
        return self.drop(self.norm(self.lin(x)))


class SinusoidalPE(nn.Module):
    """Vaswani et al. (2017) absolute PE, stored as a buffer.

    Inputs are LEFT-padded, so the final position is always the most recent
    command for every sample regardless of how much history exists.
    """

    def __init__(self, d_model: int, max_len: int):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        pos = torch.arange(max_len, dtype=torch.float32)[:, None]
        div = torch.exp(torch.arange(0, d_model, 2, dtype=torch.float32)
                        * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(pos * div)
        pe[:, 1::2] = torch.cos(pos * div)
        self.register_buffer("pe", pe, persistent=False)   # buffer, not Parameter
        self.drop = nn.Dropout(DROPOUT)

    def forward(self, x):
        return self.drop(x + self.pe[:x.shape[1]][None])


# ── trunks ──────────────────────────────────────────────────────────────────

class _Encoder(nn.Module):
    """Common interface: (X, mask) -> (B, H_DIM) history embedding."""

    def trunk_parameters(self):
        """Trainable parameters EXCLUDING the shared set embedding and head."""
        shared = set(id(p) for p in self.embed.parameters())
        return [p for p in self.parameters()
                if p.requires_grad and id(p) not in shared]

    @staticmethod
    def _check(x, mask):
        if x.ndim != 3 or x.shape[-1] != NT:
            raise ValueError(f"Expected (B, W, {NT}) multi-hot, got {tuple(x.shape)}")
        if x.shape[0] == 0:
            # An empty batch reaches torch's nested-tensor fast path and dies
            # with an unhelpful error. Fail here with a clear one instead.
            raise ValueError("Empty batch: encoders need at least one window")
        if mask.shape != x.shape[:2]:
            raise ValueError("mask shape must be (B, W)")
        # Left padding: every real command must sit at the END of the window.
        lengths = mask.sum(1).long()
        W = x.shape[1]
        idx = torch.arange(W, device=x.device)[None]
        expected = idx >= (W - lengths)[:, None]
        if not torch.equal(mask.bool(), expected):
            raise ValueError("Windows must be LEFT-padded with no internal gaps")
        if (x.sum(-1) > 0).float().mul(1 - mask).any():
            raise ValueError("Labels present at a padded position")
        return lengths


class TransformerEncoderCmd(_Encoder):
    """Shallow last-position-pooling encoder (FlowTransformer-informed)."""

    def __init__(self, max_len: int, n_layers: int = 2, n_heads: int = 4,
                 d_ff: int = 128):
        super().__init__()
        self.embed = SetEmbedding()
        self.pos = SinusoidalPE(H_DIM, max_len)
        layer = nn.TransformerEncoderLayer(
            d_model=H_DIM, nhead=n_heads, dim_feedforward=d_ff,
            dropout=DROPOUT, batch_first=True, norm_first=False)
        self.enc = nn.TransformerEncoder(layer, num_layers=n_layers,
                                         norm=nn.LayerNorm(H_DIM))

    def forward(self, x, mask):
        self._check(x, mask)
        h = self.pos(self.embed(x))
        pad = mask < 0.5
        # A row with zero real commands would make every key padded, which
        # makes attention undefined. Such rows cannot occur (every window has
        # at least one history command), but assert rather than assume.
        if pad.all(dim=1).any():
            raise ValueError("A window has no real commands")
        out = self.enc(h, src_key_padding_mask=pad)
        return out[:, -1]                      # left-padded: last = most recent


class RecurrentEncoderCmd(_Encoder):
    """Masked step-by-step recurrence over commands."""

    def __init__(self, kind: str, max_len: int, hidden: int = 100,
                 n_layers: int = 2):
        super().__init__()
        if kind not in ("GRU", "LSTM"):
            raise ValueError(f"Unknown recurrent encoder: {kind}")
        self.kind, self.hidden = kind, hidden
        self.embed = SetEmbedding()
        cell = ChoGRUCell if kind == "GRU" else ForgetGateLSTMCell
        self.cells = nn.ModuleList(
            cell(H_DIM if i == 0 else hidden, hidden) for i in range(n_layers))
        self.drop = nn.Dropout(DROPOUT)
        self.proj = nn.Identity() if hidden == H_DIM else nn.Linear(hidden, H_DIM)
        self.norm = nn.LayerNorm(H_DIM)

    def forward(self, x, mask):
        self._check(x, mask)
        seq = self.embed(x)
        live_all = mask > 0.5
        for layer, cell in enumerate(self.cells):
            h = seq.new_zeros(len(seq), self.hidden)
            c = torch.zeros_like(h)
            outputs = []
            for t in range(seq.shape[1]):
                live = live_all[:, t][:, None]
                if self.kind == "GRU":
                    h = torch.where(live, cell(seq[:, t], h), h)
                else:
                    hn, cn = cell(seq[:, t], (h, c))
                    h = torch.where(live, hn, h)
                    c = torch.where(live, cn, c)
                outputs.append(h)
            seq = torch.stack(outputs, 1)
            if layer < len(self.cells) - 1:
                seq = self.drop(seq)
        return self.norm(self.proj(h))         # h = state after the last command


class OrderFreeEncoder(_Encoder):
    """Order-free control: mean-pools the command embeddings, no positions.

    THE control this project has been missing. It sees exactly WHICH commands
    occurred and how often, but not in what order. So:

        OrderFree > NoHistory          -> knowing the history content helps
        Sequence arms > OrderFree      -> the ORDER of commands additionally helps
        Sequence arms == OrderFree     -> "history matters, order does not
                                          detectably" -- a legitimate finding

    Without this arm, a win over NoHistory only shows that history helps, not
    that sequence modelling does. The previous study dropped it, which is why
    its "sequence matters" claim could only be stated as "history matters".

    Mean pooling (not sum) so the representation does not scale with how many
    commands happen to be available, which would leak sequence length.
    """

    def __init__(self, max_len: int, hidden: int = 256, n_layers: int = 2):
        super().__init__()
        self.embed = SetEmbedding()
        layers, d = [], H_DIM
        for _ in range(n_layers):
            layers += [nn.Linear(d, hidden), nn.ReLU(), nn.Dropout(DROPOUT)]
            d = hidden
        self.mlp = nn.Sequential(*layers)
        self.proj = nn.Linear(hidden, H_DIM)
        self.norm = nn.LayerNorm(H_DIM)

    def forward(self, x, mask):
        self._check(x, mask)
        e = self.embed(x) * mask[..., None]
        pooled = e.sum(1) / mask.sum(1, keepdim=True).clamp(min=1.0)
        return self.norm(self.proj(self.mlp(pooled)))


class NoHistoryEncoder(_Encoder):
    """Control: emits a constant zero history. Trains only the head."""

    def __init__(self, max_len: int):
        super().__init__()
        self.embed = SetEmbedding()            # present but unused, for symmetry
        self.max_len = max_len

    def forward(self, x, mask):
        self._check(x, mask)
        return x.new_zeros(len(x), H_DIM)

    def trunk_parameters(self):
        return []


# ── capacity matching ───────────────────────────────────────────────────────

@lru_cache(maxsize=8)
def arm_specs(max_len: int) -> dict:
    """Hidden sizes putting GRU/LSTM trunks within tolerance of the Transformer.

    `fork_rng` keeps the capacity search from perturbing the global RNG, so
    model initialisation is unaffected by whether this ran.
    """
    with torch.random.fork_rng(devices=[]):
        target = sum(p.numel()
                     for p in TransformerEncoderCmd(max_len).trunk_parameters())

    specs = {"Transformer": {"kwargs": {}, "trunk_params": target},
             "NoHistory": {"kwargs": {}, "trunk_params": 0}}

    # OrderFree is capacity-matched too, so a difference against it cannot be
    # explained by it being a smaller model.
    best = None
    for hidden in range(32, 513):
        for layers in (1, 2):
            p = 0
            d = H_DIM
            for _ in range(layers):
                p += hidden * (d + 1)
                d = hidden
            p += H_DIM * (hidden + 1) + 2 * H_DIM
            cand = (abs(p - target), hidden, layers, p)
            if best is None or cand < best:
                best = cand
    _, hidden, layers, count = best
    if abs(count - target) / target > CAPACITY_TOLERANCE:
        raise RuntimeError(f"OrderFree capacity matching failed: {count} vs {target}")
    specs["OrderFree"] = {"kwargs": {"hidden": hidden, "n_layers": layers},
                          "trunk_params": count}
    for kind in ("GRU", "LSTM"):
        gates, biases = (3, 1) if kind == "GRU" else (4, 2)
        best = None
        for hidden in range(32, 257):
            for layers in (1, 2):
                p = sum(gates * hidden * ((H_DIM if i == 0 else hidden) + hidden + biases)
                        for i in range(layers))
                p += 0 if hidden == H_DIM else hidden * H_DIM + H_DIM
                p += 2 * H_DIM                       # final LayerNorm
                cand = (abs(p - target), hidden, layers, p)
                if best is None or cand < best:
                    best = cand
        _, hidden, layers, count = best
        if abs(count - target) / target > CAPACITY_TOLERANCE:
            raise RuntimeError(
                f"{kind} capacity matching failed: {count} vs target {target}")
        specs[kind] = {"kwargs": {"hidden": hidden, "n_layers": layers},
                       "trunk_params": count}
    return specs


# ── full model ──────────────────────────────────────────────────────────────

class CommandPredictor(nn.Module):
    """Encoder + multi-label head. Outputs LOGITS; use BCEWithLogitsLoss."""

    def __init__(self, arm: str, max_len: int):
        super().__init__()
        if arm not in ARMS:
            raise ValueError(f"Unknown arm: {arm}")
        self.arm, self.max_len = arm, max_len
        if arm == "Transformer":
            self.encoder = TransformerEncoderCmd(max_len)
        elif arm == "NoHistory":
            self.encoder = NoHistoryEncoder(max_len)
        elif arm == "OrderFree":
            self.encoder = OrderFreeEncoder(max_len,
                                            **arm_specs(max_len)[arm]["kwargs"])
        else:
            self.encoder = RecurrentEncoderCmd(arm, max_len,
                                               **arm_specs(max_len)[arm]["kwargs"])
        self.head = nn.Linear(H_DIM, NT)

    def history(self, x, mask):
        return self.encoder(x, mask)

    def forward(self, x, mask):
        return self.head(self.encoder(x, mask))


def build_model(arm: str, max_len: int) -> CommandPredictor:
    return CommandPredictor(arm, max_len)


def parameter_report(arm: str, max_len: int) -> dict:
    """Trainable parameters by part, plus the non-trainable PE buffer size.

    Reported separately so a window-length comparison is never read as a
    capacity comparison: the PE buffer grows with W, trainable counts do not.
    """
    m = build_model(arm, max_len)
    trunk = sum(p.numel() for p in m.encoder.trunk_parameters())
    embed = sum(p.numel() for p in m.encoder.embed.parameters())
    head = sum(p.numel() for p in m.head.parameters())
    total = sum(p.numel() for p in m.parameters() if p.requires_grad)
    buffers = sum(b.numel() for b in m.buffers())
    return {"arm": arm, "window": max_len, "trunk_trainable": trunk,
            "set_embedding_trainable": embed, "head_trainable": head,
            "total_trainable": total, "non_trainable_buffer_elements": buffers}
