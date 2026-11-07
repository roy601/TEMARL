# -*- coding: utf-8 -*-
"""Encoder variants for VALIDATION-ONLY design work (protocol 1.1, Section 6).

Each variant changes one thing relative to the design it is compared with and keeps the rest
identical: the same encoder layers, the same initial encoder and head weights for a given seed,
the same optimiser, batch size, learning rate, patience, update budget, checkpoint and threshold
rules. Validation BCE and predictions always use the LAST position, i.e. the real task.

  baseline  the frozen Transformer: bidirectional attention inside the window, loss on the last
            position only (Temarl_Test_v1_L1/encoders_cmd.py, unchanged)
  causal    CONTROL: causal attention (a step sees only itself and earlier steps), loss on the
            last position only. Isolates the effect of the mask.
  allpos    causal attention, loss at EVERY real position: position k predicts step k+1, and the
            last position predicts the target. The SASRec training scheme (Kang & McAuley,
            ICDM 2018), here with multi-label BCE.
  repeat    allpos (kept 2026-11-08) + a repeat/new split of the output, after RepeatNet
            (Ren et al., AAAI 2019). Two output layers on the same 64-D state: a label that
            already occurs at or before the position inside the window is scored by the REPEAT
            layer, any other label by the NEW layer (the existing head). Like RepeatNet, the
            repeat side never scores unseen labels and the new side never scores seen ones.
            Multi-label adaptation: RepeatNet's soft repeat-or-explore gate is not used. With
            one sigmoid per label it would cap a step that mixes a seen and a new label at 0.5
            for at least one of them; 50 of the 870 CAM-LDS targets are such steps.
            Adds 5,265 parameters (one 64x81 layer); the encoder and the 64-D h are unchanged.

`train_variant` is train_cmd.train_one with one line changed: the loss is `model.loss(x, m, y)`.
camlds_encoder/tests/test_variants.py proves that for `baseline` it reproduces train_one exactly.
"""
from __future__ import annotations

import os
import time
from typing import Optional

import numpy as np
import torch
from torch import nn

from port import Enc, NT, T

VARIANTS = ("baseline", "causal", "allpos", "repeat")


class BaselinePredictor(Enc.CommandPredictor):
    """The frozen model, with the frozen loss."""

    def __init__(self, max_len: int):
        super().__init__("Transformer", max_len)
        self._crit = nn.BCEWithLogitsLoss()

    def loss(self, x, mask, y):
        return self._crit(self(x, mask), y)


class CausalPredictor(nn.Module):
    """Same encoder and head as the baseline, built in the same order (so identical initial
    weights for a seed); only the attention mask and, for allpos, the loss differ."""

    def __init__(self, max_len: int, all_positions: bool):
        super().__init__()
        self.encoder = Enc.TransformerEncoderCmd(max_len)
        self.head = nn.Linear(Enc.H_DIM, NT)
        self.all_positions = all_positions
        self.max_len = max_len
        self._crit = nn.BCEWithLogitsLoss(reduction="none")

    def _attention_mask(self, mask):
        """True = may NOT attend. A real step attends to real steps at or before it. A padded
        position attends only to itself, so no row is fully masked (which would give NaN)."""
        W = mask.shape[1]
        real = mask > 0.5
        later = torch.triu(torch.ones(W, W, dtype=torch.bool, device=mask.device), 1)
        blocked = later[None] | ~real[:, None, :]
        eye = torch.eye(W, dtype=torch.bool, device=mask.device)[None]
        blocked = blocked & ~eye
        heads = self.encoder.enc.layers[0].self_attn.num_heads
        return blocked.repeat_interleave(heads, dim=0)

    def states(self, x, mask):
        enc = self.encoder
        enc._check(x, mask)
        h = enc.pos(enc.embed(x))
        return enc.enc(h, mask=self._attention_mask(mask))     # (B, W, 64)

    def history(self, x, mask):
        return self.states(x, mask)[:, -1]                     # 64-D h for MAPPO, as before

    def forward(self, x, mask):
        return self.head(self.history(x, mask))

    def position_logits(self, states, x):
        """Logits at every position, (B, W, NT)."""
        return self.head(states)

    def loss(self, x, mask, y):
        if not self.all_positions:
            return self._crit(self(x, mask), y).mean()
        logits = self.position_logits(self.states(x, mask), x)  # (B, W, NT)
        target = torch.cat([x[:, 1:], y[:, None]], 1)          # position k -> step k+1; last -> y
        per_pos = self._crit(logits, target).mean(-1)          # mean over labels, as the baseline
        return (per_pos * mask).sum() / mask.sum()             # real positions only


class RepeatPredictor(CausalPredictor):
    """allpos + RepeatNet's repeat/new split. The repeat layer is built last, so the encoder and
    the new-label head start from exactly the allpos weights for the same seed."""

    def __init__(self, max_len: int):
        super().__init__(max_len, all_positions=True)
        self.repeat_head = nn.Linear(Enc.H_DIM, NT)

    @staticmethod
    def seen(x):
        """(B, W, NT): label occurs at or before each position. Padding is all-zero, so it adds
        nothing. Never looks at later steps."""
        return torch.cummax(x, dim=1).values > 0.5

    def position_logits(self, states, x):
        return torch.where(self.seen(x), self.repeat_head(states), self.head(states))

    def forward(self, x, mask):
        h = self.history(x, mask)
        return torch.where(x.amax(dim=1) > 0.5, self.repeat_head(h), self.head(h))


def build_variant(variant: str, max_len: int) -> nn.Module:
    if variant == "baseline":
        return BaselinePredictor(max_len)
    if variant == "causal":
        return CausalPredictor(max_len, all_positions=False)
    if variant == "allpos":
        return CausalPredictor(max_len, all_positions=True)
    if variant == "repeat":
        return RepeatPredictor(max_len)
    raise ValueError(f"Unknown variant {variant}")


def _parameter_report(variant, window):
    """Builds a second model, exactly where train_one calls parameter_report, so the random
    number stream (and so dropout) matches the frozen harness."""
    m = build_variant(variant, window)
    trunk = sum(p.numel() for p in m.encoder.trunk_parameters())
    total = sum(p.numel() for p in m.parameters() if p.requires_grad)
    return {"variant": variant, "window": window, "trunk_trainable": trunk, "total_trainable": total}


def train_variant(variant: str, window: int, seed: int, train_data, val_data, max_updates: int,
                  device: Optional[torch.device] = None, checkpoint_dir: Optional[str] = None,
                  patience_checks: Optional[int] = None, progress: bool = False):
    """train_cmd.train_one, line for line, except `loss = model.loss(x, m, y)`."""
    device = device or T.device_of()
    T.set_seed(seed)
    Xtr, Mtr, Ytr = train_data
    Xva, Mva, Yva = val_data

    model = build_variant(variant, window).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=T.LEARNING_RATE, weight_decay=T.WEIGHT_DECAY)
    sampler = T.make_sampler("ordinary", len(Xtr), T.BATCH_SIZE, seed)
    stream = sampler.epochs()
    res = T.TrainResult(arm=variant, window=window, seed=seed, sampler=sampler.name,
                        updates_completed=0, parameters=_parameter_report(variant, window))
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)

    best_state, checks_since_reset = None, 0
    t0 = time.time()
    running, running_n = 0.0, 0
    for update in range(1, max_updates + 1):
        idx = next(stream)
        x, m, y = T._batches(Xtr, Mtr, Ytr, idx, device)
        loss = model.loss(x, m, y)                                       # the one changed line
        opt.zero_grad(set_to_none=True)
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), T.GRAD_CLIP)
        opt.step()
        running += loss.item() * len(idx)
        running_n += len(idx)
        res.updates_completed = update

        if update % T.VAL_EVERY == 0 or update == max_updates:
            v = T._val_bce(model, Xva, Mva, Yva, device)                 # last position: the task
            res.curve.append({"update": update, "train_loss_running": running / max(1, running_n),
                              "validation_bce": v,
                              "epoch_equivalents": update * T.BATCH_SIZE / max(1, len(Xtr))})
            running, running_n = 0.0, 0
            if v < res.best_val_bce:
                improved_by = res.best_val_bce - v
                res.best_val_bce, res.best_update = v, update
                res.improvements.append({"update": update, "validation_bce": v})
                best_state = {k: t.detach().cpu().clone() for k, t in model.state_dict().items()}
                if improved_by > T.MIN_DELTA:
                    res.patience_resets.append({"update": update, "validation_bce": v,
                                                "improved_by": improved_by})
                    checks_since_reset = 0
                else:
                    checks_since_reset += 1
            else:
                checks_since_reset += 1
            if progress:
                print(f"    [{variant} s{seed}] upd {update:6d} val_bce {v:.5f} best {res.best_val_bce:.5f}",
                      flush=True)
            if patience_checks is not None and checks_since_reset >= patience_checks:
                break

    res.seconds = time.time() - t0
    res.cap_reached = res.updates_completed >= max_updates
    res.exposure = {"mean": float(sampler.exposure.mean()), "min": int(sampler.exposure.min()),
                    "max": int(sampler.exposure.max()), "n_windows": int(len(Xtr)),
                    "unseen_windows": int((sampler.exposure == 0).sum())}
    if device.type == "cuda":
        res.peak_memory_mb = torch.cuda.max_memory_allocated(device) / (1024 ** 2)
    if checkpoint_dir and best_state is not None:
        os.makedirs(checkpoint_dir, exist_ok=True)
        torch.save({"variant": variant, "window": window, "seed": seed, "update": res.best_update,
                    "validation_bce": res.best_val_bce, "state_dict": best_state},
                   os.path.join(checkpoint_dir, "encoder.pt"))
    model._best_state = best_state                                       # noqa: SLF001
    return res, model


def numpy_logits(model, X, M, device):
    return T.predict(model, X, M, device).astype(np.float32)
