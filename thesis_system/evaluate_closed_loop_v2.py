# evaluate_closed_loop_v2.py
"""
Closed-Loop Evaluation v2 — Representative State + h-Variation Test
====================================================================
Strengthens evaluate_closed_loop.py. Instead of zeroing the 310-dim
network state (which made QMIX fall back to a near-constant policy),
this version:

  1. Builds a REPRESENTATIVE network state = mean of the simulation's
     base state across many real env resets/steps — the average network
     condition the agents actually trained on.
  2. Holds that state FIXED, and varies ONLY h (from real COMISET
     sequences) across positions.
  3. Measures whether QMIX action selection VARIES with h — i.e. whether
     attacker intent genuinely drives coordination on real data.

This isolates h's causal effect: same network state everywhere, only
attacker intent changes. If actions vary and alignment beats both the
static baseline and the zeroed-state version, h-driven coordination on
real data is demonstrated. If actions DON'T vary, that is reported
honestly as a null finding (agents lean on state, underuse h).

Usage:
    python evaluate_closed_loop_v2.py

Output:
    results/closed_loop_results_v2.json
"""

import os
import json
import time
from collections import Counter
import numpy as np
import torch

from mitre_techniques import PAD_ID, NUM_TECHNIQUES, MAX_SEQ_LEN, ID_TO_TECHNIQUE
from transformer_encoder import AttackerIntentEncoder
from qmix_agent import MultiAgentQMIX, N_AGENTS
from qmix_mixer import H_DIM
from simulation_env import HoneypotEnv, STATE_DIM

# ── Configuration ─────────────────────────────────────────────────────────────

SESSIONS_FILE  = r"data\comiset_sessions.json"
FINETUNED_PATH = r"results\encoder_finetuned_real_b.pt"
QMIX_MODEL_DIR = r"results"
OUTPUT_PATH    = r"results\closed_loop_results_v2.json"

QMIX_STRATEGY  = "Mix"
STATE_SAMPLE_EPISODES = 50      # episodes used to estimate the mean state
TRAIN_RATIO = 0.70
VAL_RATIO   = 0.15
SEED        = 42

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
torch.manual_seed(SEED)
np.random.seed(SEED)

# ── Extended 23×5 alignment matrix (identical to v1) ──────────────────────────
#                 min   banner  fake_v  cred    exfil
ALIGNMENT_MATRIX_EXT = np.array([
    [0.1, 0.4, 1.0, 0.2, 0.3],   # 0  T1190
    [0.1, 0.6, 0.7, 0.1, 0.1],   # 1  T1566
    [0.2, 0.3, 0.5, 0.3, 0.4],   # 2  T1059
    [0.1, 0.5, 0.4, 0.2, 0.3],   # 3  T1204
    [0.2, 0.3, 0.4, 0.4, 0.3],   # 4  T1053
    [0.1, 0.4, 0.5, 0.3, 0.3],   # 5  T1543
    [0.1, 0.5, 0.4, 0.3, 0.2],   # 6  T1547
    [0.1, 0.2, 0.8, 0.4, 0.3],   # 7  T1068
    [0.1, 0.2, 0.6, 0.5, 0.3],   # 8  T1055
    [0.2, 0.8, 0.5, 0.1, 0.2],   # 9  T1046
    [0.2, 0.9, 0.4, 0.1, 0.1],   # 10 T1016
    [0.2, 0.7, 0.6, 0.1, 0.2],   # 11 T1083
    [0.1, 0.5, 0.6, 0.7, 0.4],   # 12 T1021
    [0.1, 0.4, 0.5, 0.6, 0.4],   # 13 T1072
    [0.1, 0.3, 0.4, 0.9, 0.3],   # 14 T1550
    [0.1, 0.2, 0.3, 0.5, 0.9],   # 15 T1005
    [0.1, 0.2, 0.3, 0.4, 0.8],   # 16 T1560
    [0.1, 0.1, 0.2, 0.3, 1.0],   # 17 T1041
    [0.1, 0.2, 0.6, 0.3, 0.5],   # 18 T1486
    [0.2, 0.3, 0.5, 0.2, 0.4],   # 19 T1489
    [0.2, 0.5, 0.7, 0.4, 0.3],   # 20 T1036 Masquerading
    [0.1, 0.4, 0.6, 0.5, 0.3],   # 21 T1574 Hijack Execution Flow
    [0.2, 0.6, 0.7, 0.3, 0.2],   # 22 T1553 Subvert Trust Controls
], dtype=np.float32)

ACTION_NAMES = ["minimal", "banner", "fake_vuln", "cred_store", "exfil_bait"]

# ── Helpers ───────────────────────────────────────────────────────────────────

def load_test_sessions():
    with open(SESSIONS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    keys = list(data["sessions"].keys())
    n = len(keys)
    seqs = np.zeros((n, MAX_SEQ_LEN), dtype=np.int64)
    for i, k in enumerate(keys):
        seqs[i] = data["sessions"][k]["padded_sequence"]
    rng = np.random.default_rng(SEED)
    idx = rng.permutation(n)
    n_train = int(n * TRAIN_RATIO)
    n_val   = int(n * VAL_RATIO)
    return seqs[idx[n_train + n_val:]]

def load_finetuned_encoder():
    enc = AttackerIntentEncoder().to(DEVICE)
    enc.load_state_dict(torch.load(FINETUNED_PATH, map_location=DEVICE, weights_only=True), strict=True)
    enc.eval()
    return enc

def load_qmix_agents(strategy):
    path = os.path.join(QMIX_MODEL_DIR, f"model_{strategy}.pt")
    agents = MultiAgentQMIX(device=DEVICE)
    ckpt = torch.load(path, map_location=DEVICE, weights_only=True)
    for i, agent in enumerate(agents.agents):
        agent.online_net.load_state_dict(ckpt["agents"][i])
    agents.eval()
    return agents

def estimate_representative_state(n_episodes=STATE_SAMPLE_EPISODES):
    """
    Estimate the mean 310-dim base state by resetting the real env many
    times and reading the base-state portion [0:310]. We do NOT call
    env.step() because the env's reward path uses the original 20-row
    ALIGNMENT_MATRIX and crashes on expanded-vocab technique ids. reset()
    alone yields valid, varied initial network states — sufficient for a
    representative average and free of the reward-path bug.
    """
    env = HoneypotEnv(attack_strategy=QMIX_STRATEGY, max_steps=200)
    state_accum = np.zeros(STATE_DIM, dtype=np.float64)
    count = 0
    for _ in range(n_episodes * 4):   # more resets to compensate for no stepping
        obs = env.reset()
        state_accum += obs[0][:STATE_DIM]
        count += 1
    return (state_accum / max(count, 1)).astype(np.float32)
def extract_real_tokens(padded):
    return [int(t) for t in padded if int(t) != PAD_ID]

def build_prefix(real_tokens, up_to_idx):
    prefix = real_tokens[:up_to_idx + 1][-MAX_SEQ_LEN:]
    pad = MAX_SEQ_LEN - len(prefix)
    return np.array([PAD_ID] * pad + list(prefix), dtype=np.int64)

# ── Closed loop with fixed representative state, varying h ────────────────────

def run_closed_loop_v2(encoder, agents, test_seqs, rep_state):
    alignment_scores = []
    per_tech = {}
    action_counter = Counter()          # which actions QMIX picks overall
    actions_per_position = []           # tuple of chosen actions per position
    positions = 0
    sessions = 0

    with torch.no_grad():
        for padded in test_seqs:
            toks = extract_real_tokens(padded)
            if len(toks) < 2:
                continue
            sessions += 1
            for i in range(len(toks) - 1):
                prefix = build_prefix(toks, i)
                h = encoder.get_h_numpy(prefix, DEVICE)            # (64,)
                obs_full = np.concatenate([rep_state, h]).astype(np.float32)  # (374,)
                observations = [obs_full.copy() for _ in range(N_AGENTS)]
                actions = agents.select_actions(observations, epsilon=0.0)

                for a in actions:
                    action_counter[a] += 1
                actions_per_position.append(tuple(actions))

                nxt = toks[i + 1]
                if nxt >= ALIGNMENT_MATRIX_EXT.shape[0]:
                    continue
                best = max(ALIGNMENT_MATRIX_EXT[nxt][a] for a in actions)
                alignment_scores.append(best)
                per_tech.setdefault(nxt, []).append(best)
                positions += 1

    # Action diversity: how many DISTINCT action-tuples did h induce?
    distinct_action_tuples = len(set(actions_per_position))
    mean_align = float(np.mean(alignment_scores)) if alignment_scores else 0.0

    per_tech_summary = {}
    for tid, sc in sorted(per_tech.items(), key=lambda x: -len(x[1])):
        per_tech_summary[ID_TO_TECHNIQUE.get(tid, str(tid))] = {
            "mean_alignment": round(float(np.mean(sc)), 4),
            "std":            round(float(np.std(sc)), 4),
            "count":          len(sc),
        }

    return {
        "mean_alignment": round(mean_align, 4),
        "std_alignment":  round(float(np.std(alignment_scores)), 4) if alignment_scores else 0.0,
        "positions": positions,
        "sessions": sessions,
        "action_distribution": {ACTION_NAMES[a]: c for a, c in sorted(action_counter.items())},
        "distinct_action_tuples": distinct_action_tuples,
        "total_positions_for_diversity": len(actions_per_position),
        "per_technique": per_tech_summary,
    }

def run_static_baseline(test_seqs):
    scores = []
    for padded in test_seqs:
        toks = extract_real_tokens(padded)
        if len(toks) < 2:
            continue
        for i in range(len(toks) - 1):
            nxt = toks[i + 1]
            if nxt >= ALIGNMENT_MATRIX_EXT.shape[0]:
                continue
            scores.append(ALIGNMENT_MATRIX_EXT[nxt][0])
    return float(np.mean(scores)) if scores else 0.0

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    t0 = time.time()
    print("=" * 65)
    print("  Closed-Loop Evaluation v2 — Representative State + h-Variation")
    print("=" * 65)
    print(f"  Device          : {DEVICE}")
    print(f"  Network state    : REPRESENTATIVE (mean of {STATE_SAMPLE_EPISODES} episodes)")
    print(f"  Varying          : ONLY h (real COMISET intent)")
    print("=" * 65)
    print()

    print("Step 1: Loading held-out test sessions...")
    test_seqs = load_test_sessions()
    print(f"  Test sessions: {len(test_seqs):,}")
    print()

    print("Step 2: Loading fine-tuned encoder + QMIX agents...")
    encoder = load_finetuned_encoder()
    agents  = load_qmix_agents(QMIX_STRATEGY)
    print(f"  Loaded.")
    print()

    print(f"Step 3: Estimating representative network state...")
    rep_state = estimate_representative_state()
    print(f"  Mean state norm: {np.linalg.norm(rep_state):.3f}  (dim={rep_state.shape[0]})")
    print()

    print("Step 4: Running closed loop (fixed state, varying h)...")
    m = run_closed_loop_v2(encoder, agents, test_seqs, rep_state)
    print(f"  Sessions: {m['sessions']:,} | Positions: {m['positions']:,}")
    print()

    print("Step 5: Static baseline on same positions...")
    static_align = run_static_baseline(test_seqs)
    print(f"  Static alignment: {static_align:.4f}")
    print()

    runtime = time.time() - t0

    print("=" * 65)
    print("  CLOSED-LOOP v2 RESULTS")
    print("=" * 65)
    print(f"  {'Method':<40} {'Alignment':>12}")
    print(f"  {'-'*54}")
    print(f"  {'Closed-loop v2 (rep state + real h)':<40} {m['mean_alignment']:>12.4f}")
    print(f"  {'Static honeypot':<40} {static_align:>12.4f}")
    lift = m['mean_alignment'] - static_align
    print(f"  {'-'*54}")
    print(f"  {'Improvement over static':<40} {lift:>+12.4f}  ({100*lift/max(static_align,1e-6):+.1f}%)")
    print()

    print("  >>> h-VARIATION TEST (the key diagnostic) <<<")
    print(f"  Total positions evaluated   : {m['total_positions_for_diversity']:,}")
    print(f"  Distinct action-tuples chosen: {m['distinct_action_tuples']}")
    if m['distinct_action_tuples'] > 1:
        print(f"  ✅ QMIX action selection VARIES with h — intent drives coordination.")
    else:
        print(f"  ⚠️  QMIX chose the SAME action-tuple at every position.")
        print(f"      Agents lean on network state, underuse h. Report honestly.")
    print()
    print(f"  Action distribution across all agents/positions:")
    for name, cnt in m['action_distribution'].items():
        print(f"    {name:<12}: {cnt:,}")
    print()

    print("  Per-technique alignment (note std > 0 means h caused variation):")
    print(f"  {'Technique':<12} {'Mean':>8} {'Std':>8} {'Count':>8}")
    print(f"  {'-'*38}")
    for tech, info in m['per_technique'].items():
        print(f"  {tech:<12} {info['mean_alignment']:>8.4f} {info['std']:>8.4f} {info['count']:>8,}")
    print()
    print(f"  Execution runtime: {runtime:.2f}s")
    print()

    output = {
        "metadata": {
            "version": "v2_representative_state",
            "state_sample_episodes": STATE_SAMPLE_EPISODES,
            "qmix_strategy": QMIX_STRATEGY,
            "test_sessions": len(test_seqs),
            "runtime_seconds": round(runtime, 2),
            "rep_state_norm": round(float(np.linalg.norm(rep_state)), 4),
        },
        "closed_loop_v2": {
            "mean_alignment": m["mean_alignment"],
            "std_alignment":  m["std_alignment"],
            "positions": m["positions"],
            "sessions": m["sessions"],
        },
        "h_variation_test": {
            "distinct_action_tuples": m["distinct_action_tuples"],
            "total_positions": m["total_positions_for_diversity"],
            "action_distribution": m["action_distribution"],
            "varies_with_h": m["distinct_action_tuples"] > 1,
        },
        "static_baseline_alignment": round(static_align, 4),
        "improvement_over_static": round(lift, 4),
        "per_technique": m["per_technique"],
    }
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    print(f"  Results saved → {OUTPUT_PATH}")
    print("=" * 65)
    print("  ✅ evaluate_closed_loop_v2.py COMPLETE")
    print("=" * 65)


if __name__ == "__main__":
    main()