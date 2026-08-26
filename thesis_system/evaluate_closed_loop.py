# evaluate_closed_loop.py
"""
Closed-Loop Evaluation — Real Data → Encoder → QMIX → Alignment
================================================================
Closes the integration gap between the two siloed validation steps:

    real_data_evaluate_b.py  →  proves encoder learns real COMISET sequences
    evaluate.py              →  proves QMIX coordinates on synthetic h

This script runs the FULL pathway on real data:

    real COMISET sequence
        → fine-tuned Transformer encoder (encoder_finetuned_real_b.pt)
        → h ∈ ℝ⁶⁴  (Last Token Pooling)
        → QMIX agents select honeypot deception actions
        → alignment = ALIGNMENT_MATRIX[next_real_technique][chosen_action]

Alignment definition (Option A — next-technique-affinity):
    For each position in a real attacker chain, h is computed from the
    prefix up to that position. QMIX selects actions from h. The selected
    actions are scored against the ACTUAL next technique observed in the
    real chain, using the same ALIGNMENT_MATRIX used in simulation.

IMPORTANT — honest scope of this test:
    Network state (310 dims) is ZEROED. COMISET provides attacker behavior
    but NOT honeypot network telemetry. This isolates the encoder→agent
    intent pathway — the core thesis contribution — rather than the full
    simulation. State this explicitly in Chapter 5.

Usage:
    python evaluate_closed_loop.py

Output:
    results/closed_loop_results.json
"""

import os
import json
import time
import numpy as np
import torch

from mitre_techniques import (
    PAD_ID, UNK_ID, VOCAB_SIZE, NUM_TECHNIQUES, MAX_SEQ_LEN,
    ID_TO_TECHNIQUE,
)
from transformer_encoder import AttackerIntentEncoder
from qmix_agent import MultiAgentQMIX, OBS_DIM, N_AGENTS
from qmix_mixer import H_DIM
from simulation_env import STATE_DIM   # 310

# ── Configuration ─────────────────────────────────────────────────────────────

SESSIONS_FILE   = r"data\comiset_sessions.json"
FINETUNED_PATH  = r"results\encoder_finetuned_real_b.pt"
QMIX_MODEL_DIR  = r"results"
OUTPUT_PATH     = r"results\closed_loop_results.json"

# QMIX models are trained per attack strategy; we use the Mixed-strategy
# model as the general-purpose policy for real (unlabeled-strategy) data.
QMIX_STRATEGY   = "Mix"

# Three-way split must match real_data_evaluate_b.py EXACTLY so the
# held-out test sessions here are the SAME 847 sessions never trained on.
TRAIN_RATIO = 0.70
VAL_RATIO   = 0.15
SEED        = 42

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
torch.manual_seed(SEED)
np.random.seed(SEED)

# ── Extended Alignment Matrix (23 × 5) ────────────────────────────────────────
# Rows 0-19 copied verbatim from simulation_env.py.
# Rows 20-22 added for COMISET techniques, reasoned by MITRE tactic and
# kept consistent with the existing matrix's persistence/evasion profiles.
#
#                 min   banner  fake_v  cred    exfil
ALIGNMENT_MATRIX_EXT = np.array([
    [0.1,   0.4,    1.0,    0.2,    0.3],   # 0  T1190 Exploit Public-Facing
    [0.1,   0.6,    0.7,    0.1,    0.1],   # 1  T1566 Phishing
    [0.2,   0.3,    0.5,    0.3,    0.4],   # 2  T1059 Command Interpreter
    [0.1,   0.5,    0.4,    0.2,    0.3],   # 3  T1204 User Execution
    [0.2,   0.3,    0.4,    0.4,    0.3],   # 4  T1053 Scheduled Task
    [0.1,   0.4,    0.5,    0.3,    0.3],   # 5  T1543 Create System Process
    [0.1,   0.5,    0.4,    0.3,    0.2],   # 6  T1547 Boot Autostart
    [0.1,   0.2,    0.8,    0.4,    0.3],   # 7  T1068 Exploit Priv Escalation
    [0.1,   0.2,    0.6,    0.5,    0.3],   # 8  T1055 Process Injection
    [0.2,   0.8,    0.5,    0.1,    0.2],   # 9  T1046 Network Scanning
    [0.2,   0.9,    0.4,    0.1,    0.1],   # 10 T1016 Network Config Discovery
    [0.2,   0.7,    0.6,    0.1,    0.2],   # 11 T1083 File/Dir Discovery
    [0.1,   0.5,    0.6,    0.7,    0.4],   # 12 T1021 Remote Services
    [0.1,   0.4,    0.5,    0.6,    0.4],   # 13 T1072 Software Deploy Tools
    [0.1,   0.3,    0.4,    0.9,    0.3],   # 14 T1550 Alt Auth Material
    [0.1,   0.2,    0.3,    0.5,    0.9],   # 15 T1005 Data from Local System
    [0.1,   0.2,    0.3,    0.4,    0.8],   # 16 T1560 Archive Collected Data
    [0.1,   0.1,    0.2,    0.3,    1.0],   # 17 T1041 Exfil Over C2
    [0.1,   0.2,    0.6,    0.3,    0.5],   # 18 T1486 Data Encrypted (Ransom)
    [0.2,   0.3,    0.5,    0.2,    0.4],   # 19 T1489 Service Stop
    [0.2,   0.5,    0.7,    0.4,    0.3],   # 20 T1036 Masquerading (Defense Evasion)
    [0.1,   0.4,    0.6,    0.5,    0.3],   # 21 T1574 Hijack Execution Flow (Persistence)
    [0.2,   0.6,    0.7,    0.3,    0.2],   # 22 T1553 Subvert Trust Controls (Defense Evasion)
], dtype=np.float32)  # shape: (23, 5)


# ── Load held-out test sessions (same split as Path B) ───────────────────────

def load_test_sessions():
    """
    Reproduce the EXACT 70/15/15 split from real_data_evaluate_b.py
    and return only the held-out TEST sequences.
    """
    if not os.path.exists(SESSIONS_FILE):
        raise FileNotFoundError(f"Sessions file not found: {SESSIONS_FILE}")

    with open(SESSIONS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    session_keys = list(data["sessions"].keys())
    n = len(session_keys)

    sequences = np.zeros((n, MAX_SEQ_LEN), dtype=np.int64)
    for i, key in enumerate(session_keys):
        sequences[i] = data["sessions"][key]["padded_sequence"]

    rng     = np.random.default_rng(SEED)
    indices = rng.permutation(n)

    n_train = int(n * TRAIN_RATIO)
    n_val   = int(n * VAL_RATIO)
    test_idx = indices[n_train + n_val:]   # held-out test

    test_seqs = sequences[test_idx]
    return test_seqs


# ── Encoder loader (vocab-expanded, fine-tuned weights) ───────────────────────

def load_finetuned_encoder():
    """
    Load the fine-tuned encoder. The saved file is already a 25-vocab
    AttackerIntentEncoder state_dict (saved by real_data_evaluate_b.py),
    so no expansion is needed — load directly.
    """
    if not os.path.exists(FINETUNED_PATH):
        raise FileNotFoundError(
            f"Fine-tuned encoder not found: {FINETUNED_PATH}\n"
            f"Run real_data_evaluate_b.py first."
        )
    encoder = AttackerIntentEncoder().to(DEVICE)
    state   = torch.load(FINETUNED_PATH, map_location=DEVICE, weights_only=True)
    encoder.load_state_dict(state, strict=True)
    encoder.eval()
    return encoder


# ── QMIX loader ───────────────────────────────────────────────────────────────

def load_qmix_agents(strategy):
    """Load trained QMIX agents from model_<strategy>.pt."""
    path = os.path.join(QMIX_MODEL_DIR, f"model_{strategy}.pt")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"QMIX model not found: {path}\nRun train_thesis.py first."
        )
    agents = MultiAgentQMIX(device=DEVICE)
    ckpt   = torch.load(path, map_location=DEVICE, weights_only=True)
    for i, agent in enumerate(agents.agents):
        agent.online_net.load_state_dict(ckpt["agents"][i])
    agents.eval()
    return agents


# ── Sequence prefix builder ───────────────────────────────────────────────────

def build_prefix(full_seq_real_tokens, up_to_idx):
    """
    Given the list of REAL (non-PAD) technique ids in temporal order and an
    index, build the left-padded MAX_SEQ_LEN prefix ending at up_to_idx
    (inclusive). This mimics how h is generated step-by-step in evaluate.py:
    h depends only on what the attacker has done so far.

    Returns: np.ndarray shape (MAX_SEQ_LEN,) int64
    """
    prefix = full_seq_real_tokens[:up_to_idx + 1]
    prefix = prefix[-MAX_SEQ_LEN:]                 # keep last MAX_SEQ_LEN
    pad_count = MAX_SEQ_LEN - len(prefix)
    padded = [PAD_ID] * pad_count + list(prefix)
    return np.array(padded, dtype=np.int64)


def extract_real_tokens(padded_seq):
    """Strip PAD tokens, returning the ordered list of real technique ids."""
    return [int(t) for t in padded_seq if int(t) != PAD_ID]


# ── Closed-loop evaluation ────────────────────────────────────────────────────

def run_closed_loop(encoder, agents, test_seqs):
    """
    For each test session, walk its real technique chain position by position.
    At each position i (0-indexed), build prefix [0..i], compute h, let QMIX
    pick actions, and score those actions against the ACTUAL next technique
    at position i+1 using ALIGNMENT_MATRIX_EXT.

    Returns dict of aggregate metrics.
    """
    alignment_scores       = []
    per_technique_align    = {}   # next_technique_id -> list of scores
    positions_evaluated    = 0
    sessions_evaluated     = 0

    # Zeroed network state (COMISET has no honeypot telemetry)
    zero_state = np.zeros(STATE_DIM, dtype=np.float32)

    with torch.no_grad():
        for padded in test_seqs:
            real_tokens = extract_real_tokens(padded)
            if len(real_tokens) < 2:
                continue   # need at least one transition to score
            sessions_evaluated += 1

            # Walk transitions: predict action from prefix[0..i], score vs token[i+1]
            for i in range(len(real_tokens) - 1):
                prefix = build_prefix(real_tokens, i)        # (MAX_SEQ_LEN,)

                # Encoder → h
                h = encoder.get_h_numpy(prefix, DEVICE)       # (64,)

                # Build per-agent observation: [zero_state | h]
                obs_full = np.concatenate([zero_state, h]).astype(np.float32)  # (374,)
                observations = [obs_full.copy() for _ in range(N_AGENTS)]

                # QMIX selects actions (greedy, epsilon=0)
                actions = agents.select_actions(observations, epsilon=0.0)

                # Score against the ACTUAL next technique
                next_tech = real_tokens[i + 1]
                if next_tech >= ALIGNMENT_MATRIX_EXT.shape[0]:
                    continue   # safety guard (should never trigger; UNK excluded upstream)

                best_alignment = max(
                    ALIGNMENT_MATRIX_EXT[next_tech][a] for a in actions
                )
                alignment_scores.append(best_alignment)
                per_technique_align.setdefault(next_tech, []).append(best_alignment)
                positions_evaluated += 1

    mean_alignment = float(np.mean(alignment_scores)) if alignment_scores else 0.0
    std_alignment  = float(np.std(alignment_scores))  if alignment_scores else 0.0

    # Per-technique breakdown
    per_tech_summary = {}
    for tid, scores in sorted(per_technique_align.items(), key=lambda x: -len(x[1])):
        per_tech_summary[ID_TO_TECHNIQUE.get(tid, str(tid))] = {
            "mean_alignment": round(float(np.mean(scores)), 4),
            "count":          len(scores),
        }

    return {
        "mean_alignment":      round(mean_alignment, 4),
        "std_alignment":       round(std_alignment, 4),
        "positions_evaluated": positions_evaluated,
        "sessions_evaluated":  sessions_evaluated,
        "per_technique":       per_tech_summary,
    }


# ── Static-baseline comparison (action 0 always) ──────────────────────────────

def run_static_baseline(test_seqs):
    """
    Same loop but actions are always [0,0,0,0] (minimal_response).
    Provides the static-honeypot reference point on the SAME positions.
    """
    alignment_scores = []
    for padded in test_seqs:
        real_tokens = extract_real_tokens(padded)
        if len(real_tokens) < 2:
            continue
        for i in range(len(real_tokens) - 1):
            next_tech = real_tokens[i + 1]
            if next_tech >= ALIGNMENT_MATRIX_EXT.shape[0]:
                continue
            best_alignment = ALIGNMENT_MATRIX_EXT[next_tech][0]  # action 0 only
            alignment_scores.append(best_alignment)
    return float(np.mean(alignment_scores)) if alignment_scores else 0.0


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    t0 = time.time()
    print("=" * 65)
    print("  Closed-Loop Evaluation — Real Data → Encoder → QMIX → Alignment")
    print("=" * 65)
    print(f"  Device           : {DEVICE}")
    print(f"  Encoder weights  : {FINETUNED_PATH}")
    print(f"  QMIX policy       : model_{QMIX_STRATEGY}.pt")
    print(f"  Alignment matrix : 23 × 5 (extended for T1036/T1574/T1553)")
    print(f"  Network state     : ZEROED (intent-pathway isolation)")
    print("=" * 65)
    print()

    # Load everything
    print("Step 1: Loading held-out test sessions (same split as Path B)...")
    test_seqs = load_test_sessions()
    print(f"  Held-out test sessions: {len(test_seqs):,}")
    print()

    print("Step 2: Loading fine-tuned encoder...")
    encoder = load_finetuned_encoder()
    print(f"  Loaded {FINETUNED_PATH}")
    print()

    print(f"Step 3: Loading QMIX agents (strategy={QMIX_STRATEGY})...")
    agents = load_qmix_agents(QMIX_STRATEGY)
    print(f"  Loaded {N_AGENTS} agents")
    print()

    # Run closed loop
    print("Step 4: Running closed-loop forward pass...")
    metrics = run_closed_loop(encoder, agents, test_seqs)
    print(f"  Sessions evaluated   : {metrics['sessions_evaluated']:,}")
    print(f"  Positions evaluated  : {metrics['positions_evaluated']:,}")
    print()

    # Static baseline on same positions
    print("Step 5: Computing static-honeypot baseline on same positions...")
    static_alignment = run_static_baseline(test_seqs)
    print(f"  Static alignment     : {static_alignment:.4f}")
    print()

    runtime = time.time() - t0

    # ── Results ───────────────────────────────────────────────────────────────
    print("=" * 65)
    print("  CLOSED-LOOP RESULTS (Chapter 5 — Integration)")
    print("=" * 65)
    print(f"  {'Method':<38} {'Alignment':>12}")
    print(f"  {'-'*52}")
    print(f"  {'Closed-loop (Real h → QMIX)':<38} {metrics['mean_alignment']:>12.4f}")
    print(f"  {'Static honeypot (action 0)':<38} {static_alignment:>12.4f}")
    lift = metrics['mean_alignment'] - static_alignment
    lift_pct = 100 * lift / max(static_alignment, 1e-6)
    print(f"  {'-'*52}")
    print(f"  {'Improvement over static':<38} {lift:>+12.4f}  ({lift_pct:+.1f}%)")
    print()

    print("  Per-technique alignment (sorted by frequency):")
    print(f"  {'Technique':<12} {'Mean Align':>12} {'Count':>8}")
    print(f"  {'-'*34}")
    for tech, info in metrics["per_technique"].items():
        print(f"  {tech:<12} {info['mean_alignment']:>12.4f} {info['count']:>8,}")
    print()

    print(f"  Std (alignment)  : {metrics['std_alignment']:.4f}")
    print(f"  Execution runtime: {runtime:.2f}s")
    print()

    # ── Save ──────────────────────────────────────────────────────────────────
    output = {
        "metadata": {
            "encoder_weights":   FINETUNED_PATH,
            "qmix_strategy":     QMIX_STRATEGY,
            "alignment_matrix":  "23x5_extended",
            "network_state":     "zeroed_intent_pathway_isolation",
            "test_sessions":     len(test_seqs),
            "split":             {"train": TRAIN_RATIO, "val": VAL_RATIO,
                                  "test": round(1 - TRAIN_RATIO - VAL_RATIO, 2)},
            "runtime_seconds":   round(runtime, 2),
        },
        "closed_loop": {
            "mean_alignment":      metrics["mean_alignment"],
            "std_alignment":       metrics["std_alignment"],
            "positions_evaluated": metrics["positions_evaluated"],
            "sessions_evaluated":  metrics["sessions_evaluated"],
        },
        "static_baseline_alignment": round(static_alignment, 4),
        "improvement_over_static":   round(lift, 4),
        "improvement_pct":           round(lift_pct, 2),
        "per_technique": metrics["per_technique"],
    }
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    print(f"  Results saved → {OUTPUT_PATH}")
    print()
    print("=" * 65)
    print("  ✅ evaluate_closed_loop.py COMPLETE — loop is closed.")
    print("  The full pathway (real sequence → encoder → h → QMIX → action)")
    print("  now runs end-to-end on held-out real attack data.")
    print("=" * 65)


if __name__ == "__main__":
    main()