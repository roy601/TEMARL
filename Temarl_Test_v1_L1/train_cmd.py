# -*- coding: utf-8 -*-
"""
Temarl_Test_v1_L1 -- training harness for the multi-label command predictor
============================================================================
Primary sampler: ORDINARY TRAINING. Shuffle the training windows and visit
each exactly once per epoch (random reshuffling). Repeated epochs give more
optimisation, not more information -- the finite-sum view of Bottou, Curtis &
Nocedal (SIAM Review 2018). Random reshuffling follows Gurbuzbalaban, Ozdaglar
& Parrilo (Math. Prog. 2021); their guarantees hold under assumptions this
setting does not verify, so we cite the practice, not a superiority claim.

Ablation sampler: 50%-OVERLAP batches (`--sampler overlap`), a
persistency-inspired condition in the sense of Lapucci & Pucci (COAP 2026).
It is an explicitly labelled experiment, not the default, and it does not
change the optimiser, the window, or the environment.

Training effort is measured in OPTIMIZER UPDATES, not epochs. Equal epochs
across conditions with different window counts would not equalise effort
(Shallue et al., JMLR 2019). Every budget, schedule and stopping rule below is
expressed in updates.

Validation and stopping
-----------------------
Validation runs every `VAL_EVERY` updates on mean validation BCE. Two distinct
records are kept, because they answer different questions:

  * `improvements`   -- every STRICT improvement; each would save a checkpoint
  * `patience_resets`-- improvements exceeding `MIN_DELTA`; these reset patience

A pilot run trains to a cap and records the whole curve. Stopping rules are
then evaluated RETROSPECTIVELY, each using only information available before
its own simulated stop, so one trajectory scores every candidate patience
without leaking the future. `simulate_patience()` does that replay.

Thresholds and checkpoint selection use validation only. Test data is touched
once, at the end, by the reporting layer.
"""

from __future__ import annotations

import json
import math
import os
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

import numpy as np
import torch
from torch import nn

import _frozen
from encoders_cmd import build_model, parameter_report
from vocab_v2 import NUM_TECHNIQUES as NT

# ── protocol constants (OUR protocol; not published optima) ────────────────
BATCH_SIZE = 32
LEARNING_RATE = 5e-4
WEIGHT_DECAY = 0.01
GRAD_CLIP = 1.0
VAL_EVERY = 64                       # optimizer updates between validations
MIN_DELTA = 1e-4                     # mean-BCE improvement that resets patience
PATIENCE_GRID = (16, 32, 64)         # in validation checks -> 1024/2048/4096 updates
PILOT_SEEDS = (101, 102, 103)
MAIN_SEEDS = tuple(range(10))
WINDOWS = (8, 16, 32, 64)
PILOT_MIN_UPDATES = 8192
PILOT_EPOCH_EQUIVALENTS = 300


def device_of(spec: str = "auto") -> torch.device:
    """Resolve the device, failing loudly if CUDA was asked for and is absent.

    Without this check an explicit `--device cuda` on a CPU-only torch build
    returns a cuda device object and dies hours later inside a training loop
    with an opaque error. The usual cause is `pip install torch`, which fetches
    the CPU-only wheel on Windows and replaces a working CUDA install.
    """
    if spec == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if spec == "cuda" and not torch.cuda.is_available():
        raise SystemExit(
            f"--device cuda requested but CUDA is not available.\n"
            f"  torch {torch.__version__}, CUDA build: {torch.version.cuda}\n"
            f"This torch is not a CUDA build (or no GPU is visible).\n"
            f"Install the CUDA wheel explicitly, e.g.\n"
            f"  pip install torch --index-url https://download.pytorch.org/whl/cu124\n"
            f"or run with --device cpu (much slower).")
    return torch.device(spec)


def set_seed(seed: int) -> None:
    torch.manual_seed(seed)
    np.random.seed(seed % (2 ** 32))
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


# ── samplers ────────────────────────────────────────────────────────────────

class OrdinarySampler:
    """Shuffle once per epoch; every window seen exactly once per epoch."""

    name = "ordinary"

    def __init__(self, n: int, batch_size: int, seed: int):
        self.n, self.bs = n, batch_size
        self.rng = np.random.default_rng(seed)
        self.exposure = np.zeros(n, np.int64)

    def epochs(self):
        while True:
            order = self.rng.permutation(self.n)
            for i in range(0, self.n, self.bs):
                idx = order[i:i + self.bs]
                self.exposure[idx] += 1
                yield idx


class OverlapSampler:
    """50%-overlap batches: consecutive batches share half their windows.

    Each batch is half fresh windows and half carried over from the previous
    batch, so a window is seen in two consecutive updates and then not again
    for roughly a pass.

    What this does and does NOT change, measured rather than assumed: at equal
    updates the TOTAL exposure is essentially unchanged (mean 2.95 vs 3.00 per
    window over 30 batches of 10 from 100 windows). What changes is the
    DISTRIBUTION: ordinary gives every window exactly the same count, while
    overlap spreads it (min 2, max 4) and makes consecutive gradient steps
    share half their data.

    So this is a test of gradient-correlation and exposure variance, NOT of
    "more passes over the data". `exposure` records the realised counts and
    the report prints them, so the claim can be checked rather than believed.
    """

    name = "overlap50"

    def __init__(self, n: int, batch_size: int, seed: int, overlap: float = 0.5):
        if not 0.0 < overlap < 1.0:
            raise ValueError("overlap must be in (0, 1)")
        self.n, self.bs = n, batch_size
        self.fresh = max(1, int(round(batch_size * (1.0 - overlap))))
        self.rng = np.random.default_rng(seed)
        self.exposure = np.zeros(n, np.int64)

    def epochs(self):
        carry = np.empty(0, np.int64)
        while True:
            order = self.rng.permutation(self.n)
            for i in range(0, self.n, self.fresh):
                fresh = order[i:i + self.fresh]
                idx = np.concatenate([carry, fresh])[-self.bs:]
                self.exposure[idx] += 1
                carry = idx[-(self.bs - self.fresh):] if self.bs > self.fresh else idx
                yield idx


def make_sampler(kind: str, n: int, batch_size: int, seed: int):
    if kind == "ordinary":
        return OrdinarySampler(n, batch_size, seed)
    if kind == "overlap":
        return OverlapSampler(n, batch_size, seed)
    raise ValueError(f"Unknown sampler: {kind}")


# ── training ────────────────────────────────────────────────────────────────

@dataclass
class TrainResult:
    arm: str
    window: int
    seed: int
    sampler: str
    updates_completed: int
    curve: List[dict] = field(default_factory=list)
    improvements: List[dict] = field(default_factory=list)
    patience_resets: List[dict] = field(default_factory=list)
    best_update: int = 0
    best_val_bce: float = float("inf")
    cap_reached: bool = False
    seconds: float = 0.0
    exposure: Dict[str, float] = field(default_factory=dict)
    parameters: Dict[str, int] = field(default_factory=dict)
    peak_memory_mb: float = 0.0


def _batches(X, M, Y, idx, device):
    return (torch.from_numpy(X[idx]).to(device),
            torch.from_numpy(M[idx]).to(device),
            torch.from_numpy(Y[idx]).to(device))


@torch.no_grad()
def predict(model, X, M, device, batch_size: int = 512) -> np.ndarray:
    """Logits for every window. Restores train mode so callers cannot be
    surprised by a model left in eval."""
    was_training = model.training
    model.eval()
    out = []
    for i in range(0, len(X), batch_size):
        x = torch.from_numpy(X[i:i + batch_size]).to(device)
        m = torch.from_numpy(M[i:i + batch_size]).to(device)
        out.append(model(x, m).float().cpu().numpy())
    if was_training:
        model.train()
    return np.concatenate(out) if out else np.zeros((0, NT), np.float32)


@torch.no_grad()
def _val_bce(model, X, M, Y, device, batch_size: int = 512) -> float:
    model.eval()
    crit = nn.BCEWithLogitsLoss(reduction="sum")
    total, count = 0.0, 0
    for i in range(0, len(X), batch_size):
        x, m, y = _batches(X, M, Y, slice(i, i + batch_size), device)
        total += crit(model(x, m), y).item()
        count += y.numel()
    model.train()
    return total / max(1, count)


def train_one(arm: str, window: int, seed: int,
              train_data, val_data,
              max_updates: int,
              sampler_kind: str = "ordinary",
              device: Optional[torch.device] = None,
              checkpoint_dir: Optional[str] = None,
              patience_checks: Optional[int] = None,
              progress: bool = False) -> TrainResult:
    """Train one cell to `max_updates`, recording the full validation curve.

    `patience_checks=None` (pilots) trains the whole budget so every candidate
    stopping rule can be replayed afterwards. Passing a value stops early, for
    main runs where the rule is already frozen.

    The best-validation checkpoint is written to `checkpoint_dir/encoder.pt`
    when given. The final state is also returned in the model object, so the
    caller can report validation-best (primary) and final (secondary).
    """
    device = device or device_of()
    set_seed(seed)
    Xtr, Mtr, Ytr = train_data
    Xva, Mva, Yva = val_data

    model = build_model(arm, window).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE,
                            weight_decay=WEIGHT_DECAY)
    crit = nn.BCEWithLogitsLoss()
    sampler = make_sampler(sampler_kind, len(Xtr), BATCH_SIZE, seed)
    stream = sampler.epochs()

    res = TrainResult(arm=arm, window=window, seed=seed, sampler=sampler.name,
                      updates_completed=0,
                      parameters=parameter_report(arm, window))
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)

    best_state = None
    checks_since_reset = 0
    t0 = time.time()
    running, running_n = 0.0, 0

    for update in range(1, max_updates + 1):
        idx = next(stream)
        x, m, y = _batches(Xtr, Mtr, Ytr, idx, device)
        loss = crit(model(x, m), y)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), GRAD_CLIP)
        opt.step()
        running += loss.item() * len(idx)
        running_n += len(idx)
        res.updates_completed = update

        if update % VAL_EVERY == 0 or update == max_updates:
            v = _val_bce(model, Xva, Mva, Yva, device)
            point = {"update": update,
                     "train_bce_running": running / max(1, running_n),
                     "validation_bce": v,
                     "epoch_equivalents": update * BATCH_SIZE / max(1, len(Xtr))}
            res.curve.append(point)
            running, running_n = 0.0, 0

            if v < res.best_val_bce:                       # strict improvement
                improved_by = res.best_val_bce - v
                res.best_val_bce, res.best_update = v, update
                res.improvements.append({"update": update, "validation_bce": v})
                best_state = {k: t.detach().cpu().clone()
                              for k, t in model.state_dict().items()}
                if improved_by > MIN_DELTA:                # meaningful
                    res.patience_resets.append({"update": update,
                                                "validation_bce": v,
                                                "improved_by": improved_by})
                    checks_since_reset = 0
                else:
                    checks_since_reset += 1
            else:
                checks_since_reset += 1

            if progress:
                print(f"    [{arm} W{window} s{seed}] upd {update:6d} "
                      f"val_bce {v:.5f} best {res.best_val_bce:.5f}", flush=True)

            if patience_checks is not None and checks_since_reset >= patience_checks:
                break

    res.seconds = time.time() - t0
    res.cap_reached = (res.updates_completed >= max_updates)
    res.exposure = {
        "mean": float(sampler.exposure.mean()),
        "min": int(sampler.exposure.min()),
        "max": int(sampler.exposure.max()),
        "n_windows": int(len(Xtr)),
        "unseen_windows": int((sampler.exposure == 0).sum()),
    }
    if device.type == "cuda":
        res.peak_memory_mb = torch.cuda.max_memory_allocated(device) / (1024 ** 2)

    if checkpoint_dir and best_state is not None:
        os.makedirs(checkpoint_dir, exist_ok=True)
        torch.save({"arm": arm, "window": window, "seed": seed,
                    "sampler": sampler.name, "update": res.best_update,
                    "validation_bce": res.best_val_bce,
                    "state_dict": best_state},
                   os.path.join(checkpoint_dir, "encoder.pt"))

    model._best_state = best_state                    # noqa: SLF001
    return res, model


def load_best(model, result_or_state) -> None:
    """Restore the validation-best weights (primary checkpoint)."""
    state = getattr(model, "_best_state", None)
    if state is None:
        raise ValueError("No best state recorded for this model")
    model.load_state_dict(state)


# ── retrospective patience evaluation ──────────────────────────────────────

def simulate_patience(curve: Sequence[dict], patience_checks: int,
                      min_delta: float = MIN_DELTA) -> dict:
    """Replay a recorded curve under one stopping rule.

    Uses only points at or before the simulated stop, so the decision never
    depends on information the rule could not have had. Returns the update the
    rule would have stopped at and the best validation BCE it would have kept.
    """
    best, best_update = float("inf"), 0
    since = 0
    for point in curve:
        v = point["validation_bce"]
        if v < best:
            improved = best - v
            best, best_update = v, point["update"]
            since = 0 if improved > min_delta else since + 1
        else:
            since += 1
        if since >= patience_checks:
            return {"patience_checks": patience_checks,
                    "stopped_at_update": point["update"],
                    "selected_update": best_update,
                    "validation_bce": best,
                    "triggered": True}
    return {"patience_checks": patience_checks,
            "stopped_at_update": curve[-1]["update"] if curve else 0,
            "selected_update": best_update,
            "validation_bce": best,
            "triggered": False}


def choose_patience(pilot_curves: Dict[str, List[dict]],
                    grid: Sequence[int] = PATIENCE_GRID,
                    tolerance: float = 1e-3) -> dict:
    """Smallest patience within `tolerance` mean-BCE of the best.

    Each pilot configuration contributes equally, so a configuration with more
    seeds or a longer curve does not dominate. Validation only.
    """
    per_patience: Dict[int, List[float]] = {p: [] for p in grid}
    detail: Dict[str, Dict[int, dict]] = {}
    for key, curve in sorted(pilot_curves.items()):
        detail[key] = {}
        for p in grid:
            sim = simulate_patience(curve, p)
            per_patience[p].append(sim["validation_bce"])
            detail[key][p] = sim
    means = {p: float(np.mean(v)) for p, v in per_patience.items()}
    best_p = min(means, key=lambda p: means[p])
    chosen = min(p for p in grid if means[p] <= means[best_p] + tolerance)
    return {"mean_validation_bce_by_patience": means,
            "best_patience": int(best_p), "chosen_patience": int(chosen),
            "tolerance": tolerance, "per_configuration": detail,
            "rule": "smallest patience within tolerance of the best mean "
                    "validation BCE, configurations weighted equally"}


def choose_update_budget(pilot_results: Dict[str, List[TrainResult]],
                         factor: float = 1.25, round_to: int = VAL_EVERY) -> dict:
    """1.25 x max configuration-wise median validation-best update, rounded up.

    A budget heuristic, not a convergence proof. If any pilot reached its cap
    without its best moving away from the end, convergence is unresolved and
    the report says so.
    """
    medians = {k: float(np.median([r.best_update for r in v]))
               for k, v in sorted(pilot_results.items())}
    raw = factor * max(medians.values()) if medians else 0.0
    budget = int(math.ceil(raw / round_to) * round_to)
    unresolved = sorted(k for k, v in pilot_results.items()
                        if any(r.cap_reached and
                               r.best_update > 0.9 * r.updates_completed for r in v))
    return {"median_best_update_by_configuration": medians,
            "factor": factor, "raw": raw, "shared_update_budget": budget,
            "configurations_with_unresolved_cap": unresolved,
            "rule": f"ceil({factor} x max configuration-wise median "
                    f"validation-best update / {round_to}) x {round_to}"}
