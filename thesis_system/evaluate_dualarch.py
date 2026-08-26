# evaluate_dualarch.py
"""
Evaluation script for the Dual-Branch QMIX architecture.
=========================================================
Differences from evaluate.py:
  1. Loads DualBranchQNetwork weights (different shape from old IndividualQNetwork).
  2. Sets state_masking_prob=0.0 for all agents before evaluation (deterministic).
  3. Adds a closed-loop h-variation test directly inside the main evaluation
     to verify the architecture fix: distinct_action_tuples > 1 when only h varies.

Run AFTER retraining with the dual-branch qmix_agent.py:
    python train_thesis.py   (full retrain — 2-4 hours)
    python evaluate_dualarch.py

Output:
    results/evaluation_results_dualarch.json
"""

import torch
import torch.nn as nn
import numpy as np
import json
import os
from collections import defaultdict, Counter

from mitre_techniques import NUM_TECHNIQUES, MAX_SEQ_LEN, PAD_ID
from transformer_encoder import AttackerIntentEncoder
from qmix_mixer import QMIXMixer, H_DIM
from simulation_env import (
    HoneypotEnv, N_AGENTS, N_ACTIONS, STATE_DIM,
    ALIGNMENT_MATRIX, SIM_NUM_TECHNIQUES
)
from qmix_agent import MultiAgentQMIX, OBS_DIM

RESULTS_DIR   = r"results"
N_EVAL_EPS    = 200
ATTACK_STRATS = ["HiE", "HiC", "Ran", "Mix"]
DEVICE        = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ── Model loaders ─────────────────────────────────────────────────────────────

def _expand_encoder(enc_old, enc_new):
    """Expand 22-vocab encoder checkpoint to 25-vocab architecture."""
    for key in ("embedding.weight", "pretrain_head.weight", "pretrain_head.bias"):
        if key in enc_old and enc_old[key].shape != enc_new[key].shape:
            old = enc_old[key]
            new = enc_new[key].clone()
            new[:old.shape[0]] = old
            enc_old[key] = new
    return enc_old


def load_thesis_model(strategy, device):
    """Load dual-branch thesis model. Disables state masking for eval."""
    path = os.path.join(RESULTS_DIR, f"model_{strategy}.pt")
    assert os.path.exists(path), f"Not found: {path}\nRetrain with dual-branch first."
    encoder = AttackerIntentEncoder().to(device)
    agents  = MultiAgentQMIX(state_masking_prob=0.0, device=device)
    ckpt    = torch.load(path, map_location=device, weights_only=True)
    enc_state = _expand_encoder(ckpt["encoder"], encoder.state_dict())
    encoder.load_state_dict(enc_state, strict=True)
    for i, agent in enumerate(agents.agents):
        agent.online_net.load_state_dict(ckpt["agents"][i])
    # Ensure masking is off for evaluation
    agents.eval()
    agents.set_masking_prob(0.0)
    encoder.eval()
    return encoder, agents


def load_baseline_model(strategy, device):
    """Load dual-branch no-Transformer baseline."""
    path = os.path.join(RESULTS_DIR, f"baseline_notrans_{strategy}.pt")
    assert os.path.exists(path), f"Not found: {path}"
    agents = MultiAgentQMIX(state_masking_prob=0.0, device=device)
    ckpt   = torch.load(path, map_location=device, weights_only=True)
    for i, agent in enumerate(agents.agents):
        agent.online_net.load_state_dict(ckpt["agents"][i])
    agents.eval()
    agents.set_masking_prob(0.0)
    return agents


# ── Action functions ──────────────────────────────────────────────────────────

def static_action_fn(obs, h):
    return [0] * N_AGENTS


def make_thesis_action_fn(agents):
    def fn(obs, h):
        full = []
        for o in obs:
            o2 = o.copy(); o2[STATE_DIM:] = h; full.append(o2)
        return agents.select_actions(full, epsilon=0.0)
    return fn


def make_notrans_action_fn(agents_base):
    def fn(obs, h):
        hz = np.zeros(H_DIM, dtype=np.float32)
        full = []
        for o in obs:
            o2 = o.copy(); o2[STATE_DIM:] = hz; full.append(o2)
        return agents_base.select_actions(full, epsilon=0.0)
    return fn


# ── Episode runner ────────────────────────────────────────────────────────────

def run_episode(env, action_fn, encoder=None):
    obs        = env.reset()
    h          = np.zeros(H_DIM, dtype=np.float32)
    done       = False
    alignments = []
    trapped    = False

    while not done:
        if encoder is not None:
            h = encoder.get_h_numpy(env.get_padded_sequence(), DEVICE)
        actions = action_fn(obs, h)
        obs, rewards, done, info = env.step(actions, h)
        alignments.append(info["best_affinity"])
        if info["trapped"]:
            trapped = True

    return {
        "alignment":         float(np.mean(alignments)) if alignments else 0.0,
        "trapped":           1.0 if trapped else 0.0,
        "engagement_length": env.get_engagement_length(),
        "interaction_depth": float(env.get_interaction_depth()),
    }


def evaluate_method(method_name, action_fn, strategy, encoder=None, n=N_EVAL_EPS):
    env = HoneypotEnv(attack_strategy=strategy, max_steps=200)
    results = defaultdict(list)
    for _ in range(n):
        r = run_episode(env, action_fn, encoder)
        for k, v in r.items():
            results[k].append(v)
    return {
        "method":             method_name,
        "strategy":           strategy,
        "dsr":                float(np.mean(results["trapped"])),
        "engagement_length":  float(np.mean(results["engagement_length"])),
        "interaction_depth":  float(np.mean(results["interaction_depth"])),
        "avg_alignment":      float(np.mean(results["alignment"])),
        "alignment_std":      float(np.std(results["alignment"])),
        "n_episodes":         n,
    }


# ── h-variation test ──────────────────────────────────────────────────────────

def run_h_variation_test(agents, encoder):
    """
    Critical diagnostic: load 100 COMISET test sequences, hold network state
    fixed at a representative value, vary ONLY h, and count distinct action
    tuples.

    For the old single-branch architecture this returned 1 (always same actions).
    For the dual-branch with state masking training this should return > 1,
    confirming h now drives action selection.
    """
    sessions_path = r"data\comiset_sessions.json"
    if not os.path.exists(sessions_path):
        print("  h-variation test skipped — comiset_sessions.json not found.")
        return None

    with open(sessions_path, encoding='utf-8') as f:
        data = json.load(f)
    sessions = list(data["sessions"].values())[:100]

    # Representative state: mean of 50 env resets
    env = HoneypotEnv(attack_strategy="Mix", max_steps=200)
    state_acc = np.zeros(STATE_DIM, dtype=np.float64)
    for _ in range(50):
        obs = env.reset()
        state_acc += obs[0][:STATE_DIM]
    rep_state = (state_acc / 50).astype(np.float32)

    action_tuples = []
    with torch.no_grad():
        for sess in sessions:
            padded = np.array(sess["padded_sequence"], dtype=np.int64)
            h      = encoder.get_h_numpy(padded, DEVICE)
            obs_full = np.concatenate([rep_state, h]).astype(np.float32)
            observations = [obs_full.copy() for _ in range(N_AGENTS)]
            actions = agents.select_actions(observations, epsilon=0.0)
            action_tuples.append(tuple(actions))

    distinct = len(set(action_tuples))
    action_dist = Counter(action_tuples)
    print(f"\n  h-VARIATION TEST (key diagnostic for Problem 1):")
    print(f"  Sessions evaluated        : {len(sessions)}")
    print(f"  Distinct action-tuples    : {distinct}")
    if distinct > 1:
        print(f"  PASS — dual-branch architecture responds to h variation.")
        print(f"  Top-3 most common action tuples:")
        for t, cnt in action_dist.most_common(3):
            print(f"    {t}: {cnt} times ({100*cnt/len(sessions):.1f}%)")
    else:
        print(f"  FAIL — agents still select identical actions regardless of h.")
        print(f"  Check that training used state_masking_prob=0.3 and retrain.")
    return {"distinct_action_tuples": distinct, "total_sessions": len(sessions)}


# ── Results table ─────────────────────────────────────────────────────────────

def print_table(all_results):
    print("\n" + "=" * 100)
    print("  DUAL-BRANCH THESIS RESULTS")
    print("=" * 100)
    print(f"  {'Strategy':<6} {'Method':<32} {'DSR':>7} {'Engage':>8} "
          f"{'Depth':>7} {'Align':>7}")
    print("  " + "-" * 75)
    for strategy in ATTACK_STRATS:
        rows = sorted(
            [r for r in all_results if r["strategy"] == strategy],
            key=lambda x: -x["avg_alignment"]
        )
        for i, r in enumerate(rows):
            prefix = f"  {strategy:<6}" if i == 0 else f"  {'':6}"
            print(f"{prefix} {r['method']:<32} "
                  f"{r['dsr']:>6.1%} {r['engagement_length']:>8.2f} "
                  f"{r['interaction_depth']:>7.2f} {r['avg_alignment']:>7.3f}")
        print("  " + "-" * 75)
    print("=" * 100)
    print("  Align  = technique-action alignment (KEY METRIC)")
    print("  Engage = dwell time (with stall bonuses for high-affinity actions)")
    print("  Depth  = unique MITRE techniques attempted")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print(f"\n  Device: {DEVICE} | Episodes: {N_EVAL_EPS}")
    print(f"  Architecture: Dual-Branch (state_masking_prob=0.0 at eval)\n")
    os.makedirs(RESULTS_DIR, exist_ok=True)

    all_results  = []
    h_var_result = None

    for strategy in ATTACK_STRATS:
        print(f"  Strategy: {strategy}")
        print(f"  " + "-" * 40)

        encoder, agents = load_thesis_model(strategy, DEVICE)
        agents_base     = load_baseline_model(strategy, DEVICE)

        thesis_fn   = make_thesis_action_fn(agents)
        notrans_fn  = make_notrans_action_fn(agents_base)

        r1 = evaluate_method("MARL + Transformer (Thesis)", thesis_fn,
                             strategy, encoder)
        r2 = evaluate_method("MARL (no Transformer)", notrans_fn,
                             strategy)
        r3 = evaluate_method("Static Honeypot", static_action_fn,
                             strategy)
        all_results.extend([r1, r2, r3])

        print(f"  Thesis:   Align={r1['avg_alignment']:.3f} | "
              f"Engage={r1['engagement_length']:.2f} | Depth={r1['interaction_depth']:.2f}")
        print(f"  NoTrans:  Align={r2['avg_alignment']:.3f} | "
              f"Engage={r2['engagement_length']:.2f} | Depth={r2['interaction_depth']:.2f}")
        print(f"  Static:   Align={r3['avg_alignment']:.3f} | "
              f"Engage={r3['engagement_length']:.2f} | Depth={r3['interaction_depth']:.2f}")
        print()

        # Run h-variation test once (using the Mix strategy model + real COMISET)
        if strategy == "Mix" and h_var_result is None:
            h_var_result = run_h_variation_test(agents, encoder)

    print_table(all_results)

    path = os.path.join(RESULTS_DIR, "evaluation_results_dualarch.json")
    with open(path, "w") as f:
        json.dump({
            "architecture": "dual_branch",
            "state_masking_prob_training": 0.3,
            "state_masking_prob_eval": 0.0,
            "results": all_results,
            "h_variation_test": h_var_result,
        }, f, indent=2)
    print(f"\n  Results saved -> {path}")


if __name__ == "__main__":
    main()