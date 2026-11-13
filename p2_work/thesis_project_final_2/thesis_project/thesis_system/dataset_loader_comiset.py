# dataset_loader_comiset.py
"""
COMISET Dataset Loader
=======================
Reads comiset_sessions.json (output of extract_comiset_sessions.py),
converts padded sequences to numpy arrays, splits into train/val sets,
and returns PyTorch DataLoader objects ready for fine-tuning.

Usage (standalone verification):
    python dataset_loader_comiset.py

Usage (import):
    from dataset_loader_comiset import get_dataloaders
    train_loader, val_loader, stats = get_dataloaders()
"""

import json
import os
import numpy as np
from collections import Counter

import torch
from torch.utils.data import Dataset, DataLoader

from mitre_techniques import (
    PAD_ID,
    UNK_ID,
    MAX_SEQ_LEN,
    VOCAB_SIZE,
    NUM_TECHNIQUES,
    ID_TO_TECHNIQUE,
    ID_TO_META,
)

# ── Configuration ─────────────────────────────────────────────────────────────

SESSIONS_FILE  = r"data\comiset_sessions.json"

# Train / validation split ratio
TRAIN_RATIO    = 0.85

# DataLoader settings
BATCH_SIZE     = 64
NUM_WORKERS    = 0       # 0 = main process only (safe on Windows)
SHUFFLE_TRAIN  = True
RANDOM_SEED    = 42

# ── Dataset class ─────────────────────────────────────────────────────────────

class ComisetSequenceDataset(Dataset):
    """
    Each sample is one process_guid behavioral chain.

    __getitem__ returns:
        input_seq  : LongTensor [MAX_SEQ_LEN]   — padded sequence (input to Transformer)
        target_seq : LongTensor [MAX_SEQ_LEN]   — same sequence shifted: predict next token
        mask       : BoolTensor [MAX_SEQ_LEN]   — True where token is NOT PAD (real token)

    Training objective: next-token prediction on real (non-PAD) positions only.
    The Transformer sees input_seq and must predict the next technique at each
    real position. Loss is computed only on mask==True positions.
    """

    def __init__(self, sequences: np.ndarray):
        """
        sequences : np.ndarray shape [N, MAX_SEQ_LEN] dtype int64
                    Each row is one left-padded sequence.
        """
        self.sequences = torch.from_numpy(sequences).long()
        self.n         = len(sequences)

    def __len__(self):
        return self.n

    def __getitem__(self, idx):
        seq = self.sequences[idx]                          # [MAX_SEQ_LEN]

        # Input: all tokens except last
        # Target: all tokens except first (shifted by 1)
        # Both length MAX_SEQ_LEN - 1
        input_seq  = seq[:-1]                              # [MAX_SEQ_LEN - 1]
        target_seq = seq[1:]                               # [MAX_SEQ_LEN - 1]

        # Mask: True on positions where TARGET is a real technique (not PAD)
        mask = (target_seq != PAD_ID)                      # [MAX_SEQ_LEN - 1]

        return input_seq, target_seq, mask


# ── Load and split ────────────────────────────────────────────────────────────

def load_sessions(sessions_file: str = SESSIONS_FILE):
    """
    Load comiset_sessions.json and return:
        sequences  : np.ndarray [N, MAX_SEQ_LEN] int64
        metadata   : dict (from JSON metadata block)
        session_keys: list of process_guid strings (same order as sequences)
    """
    if not os.path.exists(sessions_file):
        raise FileNotFoundError(
            f"Sessions file not found: {sessions_file}\n"
            f"Run extract_comiset_sessions.py first."
        )

    print(f"  Loading {sessions_file}...")
    with open(sessions_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    metadata = data["metadata"]
    sessions = data["sessions"]

    session_keys = list(sessions.keys())
    n = len(session_keys)

    sequences = np.zeros((n, MAX_SEQ_LEN), dtype=np.int64)
    for i, key in enumerate(session_keys):
        padded = sessions[key]["padded_sequence"]
        assert len(padded) == MAX_SEQ_LEN, (
            f"Session {key} has padded_sequence length {len(padded)}, expected {MAX_SEQ_LEN}"
        )
        sequences[i] = padded

    print(f"  Loaded {n:,} sessions → array shape {sequences.shape}")
    return sequences, metadata, session_keys


def split_sequences(sequences: np.ndarray, train_ratio: float = TRAIN_RATIO, seed: int = RANDOM_SEED):
    """
    Randomly split sequences into train and validation sets.
    Returns (train_seqs, val_seqs, train_indices, val_indices).
    """
    rng = np.random.default_rng(seed)
    n = len(sequences)
    indices = rng.permutation(n)

    split = int(n * train_ratio)
    train_idx = indices[:split]
    val_idx   = indices[split:]

    return sequences[train_idx], sequences[val_idx], train_idx, val_idx


def get_dataloaders(
    sessions_file: str = SESSIONS_FILE,
    batch_size:    int  = BATCH_SIZE,
    train_ratio:   float = TRAIN_RATIO,
    seed:          int  = RANDOM_SEED,
):
    """
    Main entry point for training pipeline.

    Returns:
        train_loader : DataLoader
        val_loader   : DataLoader
        stats        : dict with dataset statistics
    """
    sequences, metadata, session_keys = load_sessions(sessions_file)

    train_seqs, val_seqs, train_idx, val_idx = split_sequences(
        sequences, train_ratio=train_ratio, seed=seed
    )

    train_dataset = ComisetSequenceDataset(train_seqs)
    val_dataset   = ComisetSequenceDataset(val_seqs)

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=SHUFFLE_TRAIN,
        num_workers=NUM_WORKERS,
        pin_memory=True,
        drop_last=False,
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=NUM_WORKERS,
        pin_memory=True,
        drop_last=False,
    )

    # Compute technique distribution across all sequences
    real_tokens = sequences[sequences != PAD_ID]
    technique_counts = Counter(real_tokens.tolist())

    stats = {
        "total_sessions":    len(sequences),
        "train_sessions":    len(train_seqs),
        "val_sessions":      len(val_seqs),
        "train_batches":     len(train_loader),
        "val_batches":       len(val_loader),
        "batch_size":        batch_size,
        "max_seq_len":       MAX_SEQ_LEN,
        "vocab_size":        VOCAB_SIZE,
        "pad_id":            PAD_ID,
        "unk_id":            UNK_ID,
        "avg_seq_length":    metadata.get("avg_sequence_length", 0.0),
        "technique_counts":  technique_counts,
        "metadata":          metadata,
    }

    return train_loader, val_loader, stats


# ── Verification ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 65)
    print("  COMISET Dataset Loader — Verification")
    print("=" * 65)
    print()

    # Load
    train_loader, val_loader, stats = get_dataloaders()

    print()
    print("  Dataset split:")
    print(f"  Total sessions   : {stats['total_sessions']:,}")
    print(f"  Train sessions   : {stats['train_sessions']:,}  ({100*stats['train_sessions']/stats['total_sessions']:.1f}%)")
    print(f"  Val sessions     : {stats['val_sessions']:,}  ({100*stats['val_sessions']/stats['total_sessions']:.1f}%)")
    print(f"  Train batches    : {stats['train_batches']:,}  (batch_size={stats['batch_size']})")
    print(f"  Val batches      : {stats['val_batches']:,}")
    print(f"  Avg seq length   : {stats['avg_seq_length']:.2f}")
    print()

    # Technique distribution
    print("  Technique distribution (all sessions):")
    print(f"  {'ID':<6} {'Token':<12} {'Name':<40} {'Count':>8} {'%':>6}")
    print(f"  {'-'*72}")
    total_tokens = sum(stats['technique_counts'].values())
    for tid, count in sorted(stats['technique_counts'].items(), key=lambda x: -x[1]):
        token = ID_TO_TECHNIQUE.get(tid, "???")
        name  = ID_TO_META.get(tid, {}).get("name", "???")[:40]
        pct   = 100 * count / max(total_tokens, 1)
        print(f"  {tid:<6} {token:<12} {name:<40} {count:>8,} {pct:>5.1f}%")
    print(f"  {'':6} {'TOTAL':<12} {'':40} {total_tokens:>8,} {'100.0':>5}%")
    print()

    # Inspect one batch
    print("  Inspecting one training batch...")
    input_seq, target_seq, mask = next(iter(train_loader))
    print(f"  input_seq  shape : {tuple(input_seq.shape)}  dtype={input_seq.dtype}")
    print(f"  target_seq shape : {tuple(target_seq.shape)}  dtype={target_seq.dtype}")
    print(f"  mask       shape : {tuple(mask.shape)}  dtype={mask.dtype}")
    print()

    # Show first 3 samples decoded
    print("  First 3 samples decoded:")
    for i in range(min(3, len(input_seq))):
        inp_tokens  = [ID_TO_TECHNIQUE.get(t.item(), "PAD") if t.item() != PAD_ID else "PAD"
                       for t in input_seq[i]]
        tgt_tokens  = [ID_TO_TECHNIQUE.get(t.item(), "PAD") if t.item() != PAD_ID else "PAD"
                       for t in target_seq[i]]
        mask_str    = ['1' if m else '0' for m in mask[i]]
        print(f"  Sample {i+1}:")
        print(f"    Input  : {inp_tokens}")
        print(f"    Target : {tgt_tokens}")
        print(f"    Mask   : {mask_str}")
    print()

    # Tensor value assertions
    print("  Running assertions...")
    assert input_seq.shape  == (min(BATCH_SIZE, stats['train_sessions']), MAX_SEQ_LEN - 1), \
        f"input_seq shape mismatch: {input_seq.shape}"
    assert target_seq.shape == (min(BATCH_SIZE, stats['train_sessions']), MAX_SEQ_LEN - 1), \
        f"target_seq shape mismatch: {target_seq.shape}"
    assert mask.shape       == (min(BATCH_SIZE, stats['train_sessions']), MAX_SEQ_LEN - 1), \
        f"mask shape mismatch: {mask.shape}"
    assert input_seq.min()  >= 0,          "input_seq contains negative values"
    assert input_seq.max()  <  VOCAB_SIZE, f"input_seq contains id >= VOCAB_SIZE ({VOCAB_SIZE})"
    assert target_seq.min() >= 0,          "target_seq contains negative values"
    assert target_seq.max() <  VOCAB_SIZE, f"target_seq contains id >= VOCAB_SIZE ({VOCAB_SIZE})"
    # UNK should never appear — extraction script dropped UNK records
    assert UNK_ID not in input_seq,  "UNK_ID found in input_seq — check extraction pipeline"
    assert UNK_ID not in target_seq, "UNK_ID found in target_seq — check extraction pipeline"
    print("  ✅ All assertions passed")
    print()

    print("=" * 65)
    print("  ✅ dataset_loader_comiset.py VERIFIED")
    print("  Next step: real_data_finetune.py")
    print("=" * 65)