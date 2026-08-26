# real_data_evaluate_b.py
"""
Real Data Evaluation (Path B) — Held-Out Test Set Comparison
=============================================================
Measures whether fine-tuning on real COMISET data improves next-token
prediction on REAL attack sequences the encoder never trained on.

Fair comparison on the SAME held-out test set:

    Encoder      Trained on                    Evaluated on
    ---------    --------------------------    ------------------
    Sim-only     synthetic sequences only      held-out COMISET test
    Real-FT      synthetic + COMISET train     held-out COMISET test

Metrics (all standard sequence-model metrics):
    - Top-1 accuracy   : top prediction is the true next technique
    - Top-3 accuracy    : true technique is within top 3 predictions
    - Perplexity        : exp(cross-entropy) — lower = less surprised by real data

Three-way split (70/15/15), self-contained in this file:
    - train : fine-tune encoder on this
    - val   : select best checkpoint
    - test  : final evaluation, touched ONCE per encoder

Usage:
    python real_data_evaluate_b.py

Outputs:
    results/encoder_finetuned_real_b.pt   — fine-tuned encoder (Path B split)
    results/real_data_lift_table_b.json   — quantitative results for Chapter 5
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
from torch.utils.data import Dataset, DataLoader

from mitre_techniques import (
    PAD_ID, UNK_ID, VOCAB_SIZE, NUM_TECHNIQUES, MAX_SEQ_LEN,
    ID_TO_TECHNIQUE, ID_TO_META,
)
from transformer_encoder import AttackerIntentEncoder

# ── Configuration ─────────────────────────────────────────────────────────────

SESSIONS_FILE    = r"data\comiset_sessions.json"
PRETRAINED_PATH  = r"results\encoder_pretrained.pt"
FINETUNED_PATH   = r"results\encoder_finetuned_real_b.pt"
LIFT_TABLE_PATH  = r"results\real_data_lift_table_b.json"

# Three-way split ratios
TRAIN_RATIO = 0.70
VAL_RATIO   = 0.15
# TEST_RATIO = 0.15 (remainder)

# Fine-tuning hyperparameters (same as Path A for consistency)
FINETUNE_EPOCHS = 20
FINETUNE_LR     = 5e-5
WEIGHT_DECAY    = 1e-4
WARMUP_EPOCHS   = 2
BATCH_SIZE      = 64

# Device + reproducibility
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SEED   = 42
torch.manual_seed(SEED)
np.random.seed(SEED)

# ── Dataset ───────────────────────────────────────────────────────────────────

class ComisetSequenceDataset(Dataset):
    """Next-token prediction dataset. Each row is one left-padded sequence."""
    def __init__(self, sequences: np.ndarray):
        self.sequences = torch.from_numpy(sequences).long()

    def __len__(self):
        return len(self.sequences)

    def __getitem__(self, idx):
        seq        = self.sequences[idx]
        input_seq  = seq[:-1]                  # [MAX_SEQ_LEN - 1]
        target_seq = seq[1:]                   # [MAX_SEQ_LEN - 1]
        mask       = (target_seq != PAD_ID)    # real-token positions only
        return input_seq, target_seq, mask

# ── Three-way split ───────────────────────────────────────────────────────────

def load_and_split():
    """
    Load comiset_sessions.json, build sequence array, split 70/15/15.
    Returns train_loader, val_loader, test_loader, metadata.
    The test set is held out from ALL training.
    """
    if not os.path.exists(SESSIONS_FILE):
        raise FileNotFoundError(
            f"Sessions file not found: {SESSIONS_FILE}\n"
            f"Run extract_comiset_sessions.py first."
        )

    print(f"  Loading {SESSIONS_FILE}...")
    with open(SESSIONS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    metadata     = data["metadata"]
    sessions     = data["sessions"]
    session_keys = list(sessions.keys())
    n            = len(session_keys)

    sequences = np.zeros((n, MAX_SEQ_LEN), dtype=np.int64)
    for i, key in enumerate(session_keys):
        sequences[i] = sessions[key]["padded_sequence"]

    # Deterministic shuffle and split
    rng     = np.random.default_rng(SEED)
    indices = rng.permutation(n)

    n_train = int(n * TRAIN_RATIO)
    n_val   = int(n * VAL_RATIO)

    train_idx = indices[:n_train]
    val_idx   = indices[n_train:n_train + n_val]
    test_idx  = indices[n_train + n_val:]

    train_seqs = sequences[train_idx]
    val_seqs   = sequences[val_idx]
    test_seqs  = sequences[test_idx]

    print(f"  Total sessions : {n:,}")
    print(f"  Train          : {len(train_seqs):,}  ({100*len(train_seqs)/n:.1f}%)")
    print(f"  Val            : {len(val_seqs):,}  ({100*len(val_seqs)/n:.1f}%)")
    print(f"  Test (held-out): {len(test_seqs):,}  ({100*len(test_seqs)/n:.1f}%)")

    train_loader = DataLoader(ComisetSequenceDataset(train_seqs), batch_size=BATCH_SIZE,
                              shuffle=True,  num_workers=0, pin_memory=True)
    val_loader   = DataLoader(ComisetSequenceDataset(val_seqs),   batch_size=BATCH_SIZE,
                              shuffle=False, num_workers=0, pin_memory=True)
    test_loader  = DataLoader(ComisetSequenceDataset(test_seqs),  batch_size=BATCH_SIZE,
                              shuffle=False, num_workers=0, pin_memory=True)

    split_sizes = {
        "total": n,
        "train": len(train_seqs),
        "val":   len(val_seqs),
        "test":  len(test_seqs),
    }
    return train_loader, val_loader, test_loader, metadata, split_sizes

# ── Checkpoint loader with vocab expansion ────────────────────────────────────

def pretrain_baseline_encoder(device, path):
    """
    Automatically pre-train a baseline encoder on random synthetic sequences
    in case results/encoder_pretrained.pt is missing (e.g. clean rerun).
    This matches train_thesis.py Phase 1 pre-training.
    """
    print(f"  [Auto-Pretrain] {path} not found. Training one on synthetic sequences now...")
    encoder = AttackerIntentEncoder().to(device)
    encoder.train()
    optimizer = optim.Adam(encoder.parameters(), lr=1e-3)
    criterion = nn.CrossEntropyLoss()
    
    for step in range(5000):
        seq_len     = np.random.randint(2, MAX_SEQ_LEN + 1)
        # Vocabulary size for Phase 1 is 22
        techniques  = [np.random.randint(0, 22) for _ in range(seq_len)]
        input_seq   = techniques[:-1]
        target_tech = techniques[-1]
        pad_len     = MAX_SEQ_LEN - len(input_seq)
        padded      = [PAD_ID] * pad_len + input_seq

        token_ids = torch.LongTensor([padded]).to(device)
        target    = torch.LongTensor([target_tech]).to(device)

        optimizer.zero_grad()
        h, logits = encoder.pretrain_forward(token_ids)
        loss      = criterion(logits, target)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(encoder.parameters(), 1.0)
        optimizer.step()

        if (step + 1) % 1000 == 0:
            print(f"    Step {step+1:5d}/5000 | Loss: {loss.item():.4f}")

    os.makedirs(os.path.dirname(path), exist_ok=True)
    torch.save(encoder.state_dict(), path)
    print(f"  [Auto-Pretrain] Saved pre-trained baseline encoder -> {path}")

def load_encoder_with_expansion(path: str, device: torch.device) -> AttackerIntentEncoder:
    """
    Load pre-trained encoder (vocab 22) into expanded model (vocab 25).
    Rows 0-21 copied; rows 22-24 randomly initialized.
    """
    if not os.path.exists(path):
        if path.endswith("encoder_pretrained.pt"):
            pretrain_baseline_encoder(device, path)
        else:
            raise FileNotFoundError(
                f"Encoder not found: {path}"
            )

    encoder    = AttackerIntentEncoder().to(device)
    checkpoint = torch.load(path, map_location=device, weights_only=False)

    if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
        old_state = checkpoint["model_state_dict"]
    elif isinstance(checkpoint, dict) and "state_dict" in checkpoint:
        old_state = checkpoint["state_dict"]
    else:
        old_state = checkpoint

    new_state = encoder.state_dict()

    # Expand embedding.weight [22,64] -> [25,64]
    old_emb = old_state["embedding.weight"]
    new_emb = new_state["embedding.weight"].clone()
    new_emb[:old_emb.shape[0], :] = old_emb
    new_state["embedding.weight"] = new_emb

    # Expand pretrain_head.weight [22,64] -> [25,64]
    old_hw = old_state["pretrain_head.weight"]
    new_hw = new_state["pretrain_head.weight"].clone()
    new_hw[:old_hw.shape[0], :] = old_hw
    new_state["pretrain_head.weight"] = new_hw

    # Expand pretrain_head.bias [22] -> [25]
    old_hb = old_state["pretrain_head.bias"]
    new_hb = new_state["pretrain_head.bias"].clone()
    new_hb[:old_hb.shape[0]] = old_hb
    new_state["pretrain_head.bias"] = new_hb

    for k, v in old_state.items():
        if k not in ("embedding.weight", "pretrain_head.weight", "pretrain_head.bias"):
            if k in new_state and new_state[k].shape == v.shape:
                new_state[k] = v

    encoder.load_state_dict(new_state, strict=True)
    return encoder

# ── LM-head wrapper for fine-tuning ───────────────────────────────────────────

class EncoderWithLMHead(nn.Module):
    """Full-sequence next-token prediction wrapper around the encoder."""
    def __init__(self, encoder: AttackerIntentEncoder):
        super().__init__()
        self.encoder = encoder
        self.lm_head = nn.Linear(encoder.d_model, VOCAB_SIZE, bias=False)
        self.lm_head.weight = encoder.embedding.weight   # weight tying

    def forward(self, input_seq: torch.LongTensor) -> torch.Tensor:
        x = self.encoder.embedding(input_seq)
        x = self.encoder.pos_enc(x)
        pad_mask = (input_seq == PAD_ID)
        for layer in self.encoder.transformer.layers:
            x = layer(x, src_key_padding_mask=pad_mask)
        return self.lm_head(x)    # [B, L, VOCAB_SIZE]

# ── Metric computation ────────────────────────────────────────────────────────

def evaluate_on_test(model_lm: EncoderWithLMHead, test_loader) -> dict:
    """
    Compute Top-1 accuracy, Top-3 accuracy, and perplexity on the
    held-out test set. Metrics are computed only on real (non-PAD) positions.
    """
    model_lm.eval()
    criterion = nn.CrossEntropyLoss(ignore_index=PAD_ID, reduction='sum')

    total_correct_top1 = 0
    total_correct_top3 = 0
    total_positions    = 0
    total_loss         = 0.0
    total_loss_tokens  = 0

    with torch.no_grad():
        for input_seq, target_seq, mask in test_loader:
            input_seq  = input_seq.to(DEVICE)
            target_seq = target_seq.to(DEVICE)
            mask       = mask.to(DEVICE)

            logits = model_lm(input_seq)               # [B, L, V]
            B, L, V = logits.shape

            # Perplexity components (CrossEntropy already ignores PAD)
            loss = criterion(logits.reshape(B * L, V), target_seq.reshape(B * L))
            n_real = int(mask.sum().item())
            total_loss        += loss.item()
            total_loss_tokens += n_real

            # Top-1 and Top-3 on real positions only
            top3 = logits.topk(3, dim=-1).indices       # [B, L, 3]
            tgt  = target_seq.unsqueeze(-1)             # [B, L, 1]

            correct_top1 = (top3[..., 0:1] == tgt).squeeze(-1) & mask    # [B, L]
            correct_top3 = (top3 == tgt).any(dim=-1) & mask             # [B, L]

            total_correct_top1 += int(correct_top1.sum().item())
            total_correct_top3 += int(correct_top3.sum().item())
            total_positions    += n_real

    top1_acc   = total_correct_top1 / max(total_positions, 1)
    top3_acc   = total_correct_top3 / max(total_positions, 1)
    avg_loss   = total_loss / max(total_loss_tokens, 1)
    perplexity = float(np.exp(avg_loss))

    return {
        "top1_accuracy": round(top1_acc, 4),
        "top3_accuracy": round(top3_acc, 4),
        "cross_entropy": round(avg_loss, 4),
        "perplexity":    round(perplexity, 4),
        "test_positions": total_positions,
    }

# ── Fine-tuning ───────────────────────────────────────────────────────────────

def finetune(encoder: AttackerIntentEncoder, train_loader, val_loader):
    """Fine-tune encoder on COMISET train split; select best by val loss."""
    model     = EncoderWithLMHead(encoder).to(DEVICE)
    optimizer = optim.AdamW(model.parameters(), lr=FINETUNE_LR, weight_decay=WEIGHT_DECAY)

    total_steps  = FINETUNE_EPOCHS * len(train_loader)
    warmup_steps = WARMUP_EPOCHS  * len(train_loader)
    scheduler    = CosineAnnealingLR(optimizer, T_max=total_steps - warmup_steps, eta_min=1e-6)
    criterion    = nn.CrossEntropyLoss(ignore_index=PAD_ID)

    print(f"  {'Epoch':<6} {'Train Loss':>12} {'Val Loss':>10} {'LR':>12}  {'Time':>8}")
    print(f"  {'-'*54}")

    best_val   = float('inf')
    best_state = None
    step       = 0
    curves     = {"train": [], "val": []}

    for epoch in range(1, FINETUNE_EPOCHS + 1):
        t0 = time.time()
        model.train()
        ep_loss, nb = 0.0, 0

        for input_seq, target_seq, mask in train_loader:
            input_seq  = input_seq.to(DEVICE)
            target_seq = target_seq.to(DEVICE)

            if step < warmup_steps:
                scale = (step + 1) / max(warmup_steps, 1)
                for pg in optimizer.param_groups:
                    pg['lr'] = FINETUNE_LR * scale

            optimizer.zero_grad()
            logits  = model(input_seq)
            B, L, V = logits.shape
            loss    = criterion(logits.reshape(B * L, V), target_seq.reshape(B * L))
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            if step >= warmup_steps:
                scheduler.step()

            ep_loss += loss.item()
            nb      += 1
            step    += 1

        # Validation
        model.eval()
        v_loss, vn = 0.0, 0
        with torch.no_grad():
            for input_seq, target_seq, mask in val_loader:
                input_seq  = input_seq.to(DEVICE)
                target_seq = target_seq.to(DEVICE)
                logits  = model(input_seq)
                B, L, V = logits.shape
                loss    = criterion(logits.reshape(B * L, V), target_seq.reshape(B * L))
                v_loss += loss.item()
                vn     += 1

        avg_t = ep_loss / max(nb, 1)
        avg_v = v_loss / max(vn, 1)
        curves["train"].append(round(avg_t, 4))
        curves["val"].append(round(avg_v, 4))
        lr = optimizer.param_groups[0]['lr']
        print(f"  {epoch:<6} {avg_t:>12.4f} {avg_v:>10.4f} {lr:>12.2e}  {time.time()-t0:>6.1f}s")

        if avg_v < best_val:
            best_val   = avg_v
            best_state = copy.deepcopy(model.encoder.state_dict())

    print(f"\n  Best val loss: {best_val:.4f}")
    encoder.load_state_dict(best_state)
    return encoder, curves

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 65)
    print("  Real Data Evaluation — Path B (Held-Out Test Set)")
    print("=" * 65)
    print()

    os.makedirs("results", exist_ok=True)

    # Step 1: Load and split 70/15/15
    print("Step 1: Loading and splitting COMISET (70/15/15)...")
    train_loader, val_loader, test_loader, metadata, split_sizes = load_and_split()
    print()

    # Step 2: Evaluate SIM-ONLY encoder on held-out test set
    print("Step 2: Evaluating sim-only encoder on held-out test set...")
    sim_encoder = load_encoder_with_expansion(PRETRAINED_PATH, DEVICE)
    sim_lm      = EncoderWithLMHead(sim_encoder).to(DEVICE)
    sim_metrics = evaluate_on_test(sim_lm, test_loader)
    print(f"  Top-1 accuracy : {sim_metrics['top1_accuracy']:.4f}")
    print(f"  Top-3 accuracy : {sim_metrics['top3_accuracy']:.4f}")
    print(f"  Perplexity     : {sim_metrics['perplexity']:.4f}")
    print(f"  Test positions : {sim_metrics['test_positions']:,}")
    print()

    # Step 3: Fine-tune on COMISET train split
    print("Step 3: Fine-tuning encoder on COMISET train split...")
    ft_encoder = load_encoder_with_expansion(PRETRAINED_PATH, DEVICE)
    ft_encoder, curves = finetune(ft_encoder, train_loader, val_loader)
    print()

    # Step 4: Save fine-tuned encoder
    print("Step 4: Saving fine-tuned encoder...")
    torch.save(ft_encoder.state_dict(), FINETUNED_PATH)
    print(f"  Saved → {FINETUNED_PATH}")
    print()

    # Step 5: Evaluate REAL-FT encoder on the SAME held-out test set
    print("Step 5: Evaluating fine-tuned encoder on held-out test set...")
    ft_lm      = EncoderWithLMHead(ft_encoder).to(DEVICE)
    ft_metrics = evaluate_on_test(ft_lm, test_loader)
    print(f"  Top-1 accuracy : {ft_metrics['top1_accuracy']:.4f}")
    print(f"  Top-3 accuracy : {ft_metrics['top3_accuracy']:.4f}")
    print(f"  Perplexity     : {ft_metrics['perplexity']:.4f}")
    print()

    # Step 6: Real Data Lift Table (proper metrics, held-out test)
    print("=" * 65)
    print("  REAL DATA LIFT TABLE — Path B (Chapter 5)")
    print("  Held-out test set: {:,} sessions, {:,} prediction positions".format(
        split_sizes["test"], sim_metrics["test_positions"]))
    print("=" * 65)
    print(f"  {'Metric':<18} {'Sim-Only':>10} {'Real-FT':>10} {'Lift':>12}")
    print(f"  {'-'*52}")

    def lift_row(name, sim_v, ft_v, higher_better=True):
        lift = ft_v - sim_v
        if higher_better:
            pct = 100 * lift / max(sim_v, 1e-6)
            marker = "↑" if lift > 0.001 else ("↓" if lift < -0.001 else "~")
        else:  # perplexity: lower is better
            pct = 100 * (-lift) / max(sim_v, 1e-6)
            marker = "↑" if lift < -0.001 else ("↓" if lift > 0.001 else "~")
        print(f"  {name:<18} {sim_v:>10.4f} {ft_v:>10.4f} {lift:>+9.4f} {marker}")
        return {"sim_only": round(sim_v,4), "real_ft": round(ft_v,4),
                "absolute_lift": round(lift,4), "relative_pct": round(pct,2)}

    lift_table = {
        "top1_accuracy": lift_row("Top-1 Accuracy", sim_metrics["top1_accuracy"],
                                   ft_metrics["top1_accuracy"], higher_better=True),
        "top3_accuracy": lift_row("Top-3 Accuracy", sim_metrics["top3_accuracy"],
                                   ft_metrics["top3_accuracy"], higher_better=True),
        "perplexity":    lift_row("Perplexity",     sim_metrics["perplexity"],
                                   ft_metrics["perplexity"],    higher_better=False),
    }
    print()
    print("  (Top-1/Top-3: higher is better.  Perplexity: lower is better.)")
    print()

    # Step 7: Save results
    output = {
        "metadata": {
            "split_ratios":     {"train": TRAIN_RATIO, "val": VAL_RATIO,
                                  "test": round(1 - TRAIN_RATIO - VAL_RATIO, 2)},
            "split_sizes":      split_sizes,
            "finetune_epochs":  FINETUNE_EPOCHS,
            "finetune_lr":      FINETUNE_LR,
            "vocab_size":       VOCAB_SIZE,
            "test_positions":   sim_metrics["test_positions"],
            "comiset_metadata": metadata,
        },
        "training_curves": curves,
        "sim_only_metrics": sim_metrics,
        "real_ft_metrics":  ft_metrics,
        "lift_table":       lift_table,
    }
    with open(LIFT_TABLE_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    print(f"  Results saved → {LIFT_TABLE_PATH}")
    print()
    print("=" * 65)
    print("  ✅ real_data_evaluate_b.py COMPLETE")
    print("  This table is defensible: same held-out real test set,")
    print("  standard metrics, no division-by-near-zero artifacts.")
    print("=" * 65)


if __name__ == "__main__":
    main()