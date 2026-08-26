# real_data_finetune_fixed.py
"""
Real Data Fine-Tuning (FIXED VERSION)
=======================================
Fine-tunes a FRESH Transformer encoder on COMISET real attack sequences
via next-token prediction, then saves the fine-tuned encoder.

FIX: The original version required encoder_pretrained.pt (from old
     train_thesis.py Phase 1 random pretraining) to exist first.
     This created a chicken-and-egg problem:
       - real_data_finetune.py needed encoder_pretrained.pt
       - train_thesis.py (Fix 1) needed encoder_finetuned_real.pt

     SOLUTION: Start from a FRESH randomly-initialized encoder and
     fine-tune it directly on COMISET data. No pretrained checkpoint
     needed. This makes real_data_finetune.py fully independent —
     it runs FIRST in the pipeline.

     The "sim-only baseline" comparison (Step 2) now uses the fresh
     untrained encoder as the baseline, which is honest: it shows
     the lift from COMISET fine-tuning vs no training at all.

Produces the Real Data Lift table by comparing alignment scores between:
    1. Fresh encoder        (randomly initialized — no training)
    2. Real-FT encoder      (encoder_finetuned_real.pt — fine-tuned on COMISET)

This table goes directly into Chapter 5 (Results).

Usage:
    python real_data_finetune.py

Outputs:
    results/encoder_finetuned_real.pt   — fine-tuned encoder weights
    results/real_data_lift_table.json   — numeric results for Chapter 5
"""

import os
import json
import time
import copy
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import CosineAnnealingLR

from mitre_techniques import (
    PAD_ID, UNK_ID, VOCAB_SIZE, NUM_TECHNIQUES, MAX_SEQ_LEN,
    ID_TO_TECHNIQUE, ID_TO_META,
)
from transformer_encoder import AttackerIntentEncoder
from dataset_loader_comiset import get_dataloaders

# ── Configuration ─────────────────────────────────────────────────────────────

FINETUNED_PATH   = r"results\encoder_finetuned_real.pt"
LIFT_TABLE_PATH  = r"results\real_data_lift_table.json"

# Fine-tuning hyperparameters
FINETUNE_EPOCHS  = 20
FINETUNE_LR      = 5e-5
WEIGHT_DECAY     = 1e-4
WARMUP_EPOCHS    = 2

# Alignment evaluation
EVAL_EPISODES    = 200

# Device
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Reproducibility
SEED = 42
torch.manual_seed(SEED)
np.random.seed(SEED)

# ── Alignment evaluation ──────────────────────────────────────────────────────

ATTACK_STRATEGIES = {
    "HiE": {"name": "High Evasion",    "technique_probs": {2: 0.3, 20: 0.4, 22: 0.2, 4: 0.1}},
    "HiC": {"name": "High Credential", "technique_probs": {8: 0.4, 21: 0.3, 5: 0.2, 12: 0.1}},
    "Ran": {"name": "Random",          "technique_probs": None},
    "Mix": {"name": "Mixed",           "technique_probs": {2: 0.2, 8: 0.2, 20: 0.2, 21: 0.2, 5: 0.2}},
}

ACTION_TECHNIQUE_AFFINITY = {
    0: {2, 20},
    1: {20, 22},
    2: {5, 21},
    3: {8, 12},
    4: {4, 6},
}

def sample_technique(strategy_key: str, rng: np.random.Generator) -> int:
    strat = ATTACK_STRATEGIES[strategy_key]
    probs = strat["technique_probs"]
    techniques = list(range(NUM_TECHNIQUES))
    if probs is None:
        return int(rng.choice(techniques))
    ids  = list(probs.keys())
    wts  = list(probs.values())
    remaining = [t for t in techniques if t not in ids]
    base_prob = (1.0 - sum(wts)) / max(len(remaining), 1)
    ids += remaining
    wts += [base_prob] * len(remaining)
    wts_arr = np.array(wts, dtype=float)
    wts_arr /= wts_arr.sum()
    return int(rng.choice(ids, p=wts_arr))

def build_episode_sequence(strategy_key: str, length: int, rng: np.random.Generator) -> torch.LongTensor:
    techniques = [sample_technique(strategy_key, rng) for _ in range(length)]
    collapsed = [techniques[0]]
    for t in techniques[1:]:
        if t != collapsed[-1]:
            collapsed.append(t)
    collapsed = collapsed[-MAX_SEQ_LEN:]
    pad_count = MAX_SEQ_LEN - len(collapsed)
    padded = [PAD_ID] * pad_count + collapsed
    return torch.tensor(padded, dtype=torch.long).unsqueeze(0)

def action_alignment(predicted_technique: int, action: int) -> float:
    affinity = ACTION_TECHNIQUE_AFFINITY.get(action, set())
    return 1.0 if predicted_technique in affinity else 0.0

def evaluate_alignment(encoder: AttackerIntentEncoder, strategy_key: str,
                        n_episodes: int, rng: np.random.Generator) -> float:
    encoder.eval()
    alignment_scores = []

    with torch.no_grad():
        for _ in range(n_episodes):
            seq_len = int(rng.integers(3, MAX_SEQ_LEN + 1))
            seq = build_episode_sequence(strategy_key, seq_len, rng).to(DEVICE)

            # Get h then project to technique logits via pretrain_head
            h = encoder(seq)                              # [1, 64]
            logits = encoder.pretrain_head(h)             # [1, VOCAB_SIZE]
            probs = torch.softmax(logits[0, :NUM_TECHNIQUES], dim=0).cpu().numpy()
            # probs[i] = probability encoder assigns to technique i

            # Choose action with highest expected affinity given probs
            best_action = 0
            best_score  = -np.inf
            for action, tech_set in ACTION_TECHNIQUE_AFFINITY.items():
                score = sum(float(probs[t]) for t in tech_set if t < NUM_TECHNIQUES)
                if score > best_score:
                    best_score  = score
                    best_action = action

            # Sample what technique actually arrives next
            actual_technique = sample_technique(strategy_key, rng)
            alignment_scores.append(action_alignment(actual_technique, best_action))

    return float(np.mean(alignment_scores))

# ── Fine-tuning ───────────────────────────────────────────────────────────────

class EncoderWithLMHead(nn.Module):
    """
    Wraps AttackerIntentEncoder with a linear LM head for next-token
    prediction during fine-tuning. Uses full sequence output (not pooled).
    """
    def __init__(self, encoder: AttackerIntentEncoder):
        super().__init__()
        self.encoder = encoder
        d_model = encoder.d_model
        self.lm_head = nn.Linear(d_model, VOCAB_SIZE, bias=False)
        self.lm_head.weight = encoder.embedding.weight

    def forward(self, input_seq: torch.LongTensor) -> torch.Tensor:
        """
        input_seq : [B, L]
        Returns   : logits [B, L, VOCAB_SIZE]
        """
        x = self.encoder.embedding(input_seq)
        x = self.encoder.pos_enc(x)

        pad_mask = (input_seq == PAD_ID)

        for layer in self.encoder.transformer.layers:
            x = layer(x, src_key_padding_mask=pad_mask)

        logits = self.lm_head(x)
        return logits


def finetune_encoder(encoder: AttackerIntentEncoder, train_loader, val_loader, stats: dict):
    """Fine-tune the encoder on COMISET sequences.

    FIX: Now takes an encoder object directly instead of loading from a
    pretrained checkpoint path. This allows starting from a fresh encoder.
    """
    print("  Using provided encoder (fresh or pretrained)...")

    model = EncoderWithLMHead(encoder).to(DEVICE)

    optimizer = optim.AdamW(model.parameters(), lr=FINETUNE_LR, weight_decay=WEIGHT_DECAY)

    total_steps  = FINETUNE_EPOCHS * len(train_loader)
    warmup_steps = WARMUP_EPOCHS  * len(train_loader)
    scheduler    = CosineAnnealingLR(optimizer, T_max=total_steps - warmup_steps, eta_min=1e-6)

    criterion = nn.CrossEntropyLoss(ignore_index=PAD_ID)

    print(f"  Fine-tuning for {FINETUNE_EPOCHS} epochs on {stats['train_sessions']:,} sessions...")
    print(f"  Device: {DEVICE}  |  LR: {FINETUNE_LR}  |  batch_size: {stats['batch_size']}")
    print()
    print(f"  {'Epoch':<6} {'Train Loss':>12} {'Val Loss':>10} {'LR':>12}  {'Time':>8}")
    print(f"  {'-'*54}")

    best_val_loss = float('inf')
    best_state    = None
    train_losses  = []
    val_losses    = []
    step          = 0

    for epoch in range(1, FINETUNE_EPOCHS + 1):
        t0 = time.time()
        model.train()
        epoch_loss = 0.0
        n_batches  = 0

        for input_seq, target_seq, mask in train_loader:
            input_seq  = input_seq.to(DEVICE)
            target_seq = target_seq.to(DEVICE)

            if step < warmup_steps:
                lr_scale = (step + 1) / max(warmup_steps, 1)
                for pg in optimizer.param_groups:
                    pg['lr'] = FINETUNE_LR * lr_scale

            optimizer.zero_grad()
            logits = model(input_seq)             # [B, L-1, VOCAB_SIZE]

            B, L, V = logits.shape
            loss = criterion(
                logits.reshape(B * L, V),
                target_seq.reshape(B * L),
            )
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

            if step >= warmup_steps:
                scheduler.step()

            epoch_loss += loss.item()
            n_batches  += 1
            step       += 1

        model.eval()
        val_loss = 0.0
        n_val    = 0
        with torch.no_grad():
            for input_seq, target_seq, mask in val_loader:
                input_seq  = input_seq.to(DEVICE)
                target_seq = target_seq.to(DEVICE)
                logits     = model(input_seq)
                B, L, V    = logits.shape
                loss       = criterion(
                    logits.reshape(B * L, V),
                    target_seq.reshape(B * L),
                )
                val_loss += loss.item()
                n_val    += 1

        avg_train  = epoch_loss / max(n_batches, 1)
        avg_val    = val_loss   / max(n_val, 1)
        current_lr = optimizer.param_groups[0]['lr']
        elapsed    = time.time() - t0

        train_losses.append(avg_train)
        val_losses.append(avg_val)

        print(f"  {epoch:<6} {avg_train:>12.4f} {avg_val:>10.4f} {current_lr:>12.2e}  {elapsed:>6.1f}s")

        if avg_val < best_val_loss:
            best_val_loss = avg_val
            best_state    = copy.deepcopy(model.encoder.state_dict())

    print()
    print(f"  Best val loss: {best_val_loss:.4f}")
    encoder.load_state_dict(best_state)
    return encoder, train_losses, val_losses

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 65)
    print("  Real Data Fine-Tuning Pipeline (FIXED)")
    print("=" * 65)
    print()

    os.makedirs("results", exist_ok=True)

    # Step 1: Load data
    print("Step 1: Loading COMISET dataset...")
    train_loader, val_loader, stats = get_dataloaders()
    print(f"  Train: {stats['train_sessions']:,} sessions | "
          f"Val: {stats['val_sessions']:,} sessions")
    print()

    # Step 2: Create fresh encoder and evaluate as baseline
    # FIX: Instead of loading encoder_pretrained.pt (which doesn't exist yet),
    # we create a fresh randomly-initialized encoder. This is an honest baseline:
    # it shows the lift from COMISET fine-tuning vs a completely untrained model.
    print("Step 2: Evaluating fresh (untrained) encoder as baseline...")
    fresh_encoder = AttackerIntentEncoder().to(DEVICE)

    rng = np.random.default_rng(SEED)
    baseline_alignment = {}
    for strategy_key in ATTACK_STRATEGIES:
        score = evaluate_alignment(fresh_encoder, strategy_key, EVAL_EPISODES, rng)
        baseline_alignment[strategy_key] = score
        print(f"  Fresh    {strategy_key}: alignment = {score:.3f}")
    print()

    # Step 3: Fine-tune the fresh encoder on COMISET data
    # FIX: Pass the fresh encoder directly instead of loading from a checkpoint path.
    print("Step 3: Fine-tuning encoder on COMISET...")
    ft_encoder, train_losses, val_losses = finetune_encoder(
        fresh_encoder, train_loader, val_loader, stats
    )
    print()

    # Step 4: Save fine-tuned encoder
    print("Step 4: Saving fine-tuned encoder...")
    torch.save(ft_encoder.state_dict(), FINETUNED_PATH)
    print(f"  Saved -> {FINETUNED_PATH}")
    print()

    # Step 5: Evaluate fine-tuned encoder
    print("Step 5: Evaluating fine-tuned encoder...")
    rng = np.random.default_rng(SEED)
    ft_alignment = {}
    for strategy_key in ATTACK_STRATEGIES:
        score = evaluate_alignment(ft_encoder, strategy_key, EVAL_EPISODES, rng)
        ft_alignment[strategy_key] = score
        print(f"  Fine-tuned {strategy_key}: alignment = {score:.3f}")
    print()

    # Step 6: Real Data Lift Table
    print("=" * 65)
    print("  REAL DATA LIFT TABLE (Chapter 5)")
    print("=" * 65)
    print(f"  {'Strategy':<12} {'Fresh':>10} {'Real-FT':>10} {'Lift':>10} {'Lift%':>8}")
    print(f"  {'-'*54}")

    lift_results = {}
    for strategy_key, strat_info in ATTACK_STRATEGIES.items():
        base_score = baseline_alignment[strategy_key]
        ft_score   = ft_alignment[strategy_key]
        lift       = ft_score - base_score
        lift_pct   = 100 * lift / max(base_score, 1e-6)
        lift_results[strategy_key] = {
            "strategy_name":     strat_info["name"],
            "fresh_baseline":    round(base_score, 4),
            "real_finetuned":    round(ft_score,  4),
            "absolute_lift":     round(lift,       4),
            "relative_lift_pct": round(lift_pct,   2),
        }
        if lift > 0.005:
            marker = "UP"
        elif lift < -0.005:
            marker = "DOWN"
        else:
            marker = "~"
        print(f"  {strategy_key:<12} {base_score:>10.3f} {ft_score:>10.3f} "
              f"{lift:>+10.3f} {lift_pct:>+7.1f}% {marker}")
    print()

    # Step 7: Save results
    output = {
        "metadata": {
            "finetune_epochs":  FINETUNE_EPOCHS,
            "finetune_lr":      FINETUNE_LR,
            "eval_episodes":    EVAL_EPISODES,
            "train_sessions":   stats["train_sessions"],
            "val_sessions":     stats["val_sessions"],
            "avg_seq_length":   stats["avg_seq_length"],
            "vocab_size":       VOCAB_SIZE,
            "baseline_type":    "fresh_random_init",
            "finetuned_path":   FINETUNED_PATH,
        },
        "training_curves": {
            "train_losses": [round(x, 4) for x in train_losses],
            "val_losses":   [round(x, 4) for x in val_losses],
        },
        "lift_table": lift_results,
    }

    with open(LIFT_TABLE_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    print(f"  Results saved -> {LIFT_TABLE_PATH}")
    print()
    print("=" * 65)
    print("  real_data_finetune.py COMPLETE (FIXED)")
    print("  Next step: python train_thesis.py")
    print("=" * 65)


if __name__ == "__main__":
    main()
