
# train.py
# Hawkeyes faithful reproduction — Do Hoang et al. (2026)
# Implements: Algorithm 1 — complete training workflow

import sys
import os
import numpy as np
import random
import torch
import time
import json

sys.path.insert(0, r'C:\thesis_project\hawkeyes_faithful')

from network_topology import HYPERPARAMS, ATTACK_STRATEGIES, NMS_CONFIGS
from environment import HawkeyesEnv, SCENARIO3_ACCESS_RULES
from agents import HawkeyesMARL, DEVICE

# =============================================================
# REPRODUCIBILITY
# Set seeds for reproducible results across trials
# =============================================================

def set_seeds(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)


# =============================================================
# SINGLE TRAINING RUN
# Trains MARL agents for T_max attacker steps
# Returns trained agents + training history
# =============================================================

def train_single(
    attack_strategy="Ran",
    fnr=0.05,
    fpr=0.02,
    training_steps=30000,
    seed=42,
    access_rules=None,
    verbose=False
):
    """
    Single complete training run — Algorithm 1.

    Parameters:
        attack_strategy: one of HiE, HiC, Ran, RanE, RanC, Mix
        fnr:             false negative rate for NMS
        fpr:             false positive rate for NMS
        training_steps:  T_max from Table 1 (30,000)
        seed:            random seed for reproducibility
        access_rules:    None for original, SCENARIO3 for Scenario 3
        verbose:         print progress every 1000 steps

    Returns:
        marl:    trained HawkeyesMARL object
        history: dict with training metrics
    """
    set_seeds(seed)

    # Initialize environment
    env = HawkeyesEnv(
        fnr=fnr,
        fpr=fpr,
        attack_strategy=attack_strategy,
        access_rules=access_rules
    )

    # Initialize MARL system
    marl = HawkeyesMARL(
        state_dim=env.state_dim,
        action_dim=env.action_dim,
        n_agents=HYPERPARAMS["num_agents"]  # 2
    )

    # Training history
    history = {
        "steps":          [],
        "episode_rewards":[],
        "episode_lengths":[],
        "losses":         [],
        "dsr_checkpoints":[]
    }

    # --- Algorithm 1: Training loop ---
    t         = 0           # global step counter
    episode   = 0
    done      = True        # triggers reset on first iteration
    state     = None

    ep_reward = 0.0
    ep_length = 0

    start_time = time.time()

    while t < training_steps:

        # --- Algorithm 1 line 7: Initialize new episode ---
        if done:
            state     = env.reset()
            done      = False
            ep_reward = 0.0
            ep_length = 0
            episode  += 1

        # --- Algorithm 1 line 12: Select high-level strategy ---
        strategy     = env.get_high_level_strategy()
        valid_actions = env.get_valid_actions(strategy)

        # --- Algorithm 1 lines 13-27: Agents select actions ---
        agent_results = marl.select_actions(state, valid_actions)
        actions       = [r[0] for r in agent_results]

        # --- Algorithm 1 lines 29-34: Step environment ---
        next_state, reward, done, info = env.step(actions)

        # --- Store experience (shared reward) ---
        marl.store_experience(state, agent_results, reward)

        ep_reward += reward
        ep_length += 1
        state      = next_state
        t         += 1

        # --- Algorithm 1 lines 35-40: Update policy at episode end ---
        if done:
            loss = marl.update_all()
            history["episode_rewards"].append(ep_reward)
            history["episode_lengths"].append(ep_length)
            history["losses"].append(loss)
            history["steps"].append(t)

            if verbose and episode % 100 == 0:
                elapsed = time.time() - start_time
                print(f"  Step {t:6d}/{training_steps} | "
                      f"Episode {episode:4d} | "
                      f"Loss {loss:.4f} | "
                      f"Elapsed {elapsed:.1f}s")

    total_time = time.time() - start_time

    if verbose:
        print(f"\n  Training complete: {total_time:.2f}s "
              f"for {training_steps} steps")

    history["total_time"] = total_time
    history["episodes"]   = episode

    return marl, history


# =============================================================
# DSR EVALUATION — Equation 12
# Evaluates trained policy over N_total attack attempts
# =============================================================

def evaluate_dsr(
    marl,
    attack_strategy="Ran",
    fnr=0.05,
    fpr=0.02,
    n_trials=1000,
    seed=None,
    access_rules=None
):
    """
    Evaluate Defense Success Rate — Equation 12.
    DSR = N_succ / N_total * 100

    Uses GREEDY policy (no exploration) for evaluation.
    """
    if seed is not None:
        set_seeds(seed)

    env = HawkeyesEnv(
        fnr=fnr,
        fpr=fpr,
        attack_strategy=attack_strategy,
        access_rules=access_rules
    )

    n_succ = 0

    for _ in range(n_trials):
        state = env.reset()
        done  = False

        while not done:
            strategy      = env.get_high_level_strategy()
            valid_actions = env.get_valid_actions(strategy)

            # Greedy action selection during evaluation
            actions = []
            for agent in marl.agents:
                with torch.no_grad():
                    probs, _ = agent.network(
                        torch.FloatTensor(state).to(DEVICE)
                    )
                    probs = probs.squeeze(0)

                    # Apply action mask
                    mask = torch.zeros(env.action_dim).to(DEVICE)
                    for a in valid_actions:
                        mask[a] = 1.0
                    masked = probs * mask
                    if masked.sum() > 0:
                        masked = masked / masked.sum()
                    else:
                        masked = mask / mask.sum()

                    # Greedy: take highest probability action
                    action = masked.argmax().item()
                    actions.append(action)

            state, reward, done, info = env.step(actions)

        if info["success"]:
            n_succ += 1

    dsr = n_succ / n_trials * 100.0
    return dsr


# =============================================================
# BASELINE POLICIES — Random and Critical (Section 5.4.1)
# =============================================================

def evaluate_random_policy(
    attack_strategy="Ran",
    fnr=0.05,
    fpr=0.02,
    n_trials=1000,
    seed=None,
    access_rules=None
):
    """
    Random baseline: honeypots placed at random groups.
    Section 5.4.1: "Random Policy — honeypots deployed
    arbitrarily across the network"
    """
    if seed is not None:
        set_seeds(seed)

    env = HawkeyesEnv(
        fnr=fnr,
        fpr=fpr,
        attack_strategy=attack_strategy,
        access_rules=access_rules
    )

    n_succ = 0
    all_groups = list(range(env.action_dim))

    for _ in range(n_trials):
        state = env.reset()
        done  = False

        while not done:
            # Random action — ignore strategy
            actions = [random.choice(all_groups)
                       for _ in range(len(marl_placeholder)
                                      if False else 2)]
            state, reward, done, info = env.step(actions)

        if info["success"]:
            n_succ += 1

    return n_succ / n_trials * 100.0


def evaluate_critical_policy(
    attack_strategy="Ran",
    fnr=0.05,
    fpr=0.02,
    n_trials=1000,
    seed=None,
    access_rules=None
):
    """
    Critical baseline: honeypots always protect critical nodes.
    Section 5.4.1: "Critical Policy — deception nodes positioned
    to protect critical nodes only"
    """
    if seed is not None:
        set_seeds(seed)

    env = HawkeyesEnv(
        fnr=fnr,
        fpr=fpr,
        attack_strategy=attack_strategy,
        access_rules=access_rules
    )

    # Critical group = group containing DBServer = Group 3
    critical_groups = []
    from network_topology import GROUP_MEMBERSHIP, CRITICAL_NODES
    for group_id, members in GROUP_MEMBERSHIP.items():
        if any(m in CRITICAL_NODES for m in members):
            critical_groups.append(group_id)

    n_succ = 0

    for _ in range(n_trials):
        state = env.reset()
        done  = False

        while not done:
            # Always place in critical group
            actions = [critical_groups[0], critical_groups[0]]
            state, reward, done, info = env.step(actions)

        if info["success"]:
            n_succ += 1

    return n_succ / n_trials * 100.0


# =============================================================
# ONE COMPLETE TRIAL
# Train + evaluate all 3 policies for one configuration
# =============================================================

def run_one_trial(
    trial_id,
    attack_strategy,
    fnr,
    fpr,
    training_steps=30000,
    n_eval_trials=1000,
    access_rules=None,
    verbose=False
):
    """
    Complete one trial:
    1. Train HMARL agents
    2. Evaluate HMARL DSR
    3. Evaluate Random baseline DSR
    4. Evaluate Critical baseline DSR

    Returns dict with all results.
    """
    seed = trial_id * 100 + hash(attack_strategy) % 100

    if verbose:
        print(f"\n  Trial {trial_id} | {attack_strategy} | "
              f"FNR={fnr} FPR={fpr}")

    # Train
    marl, history = train_single(
        attack_strategy=attack_strategy,
        fnr=fnr,
        fpr=fpr,
        training_steps=training_steps,
        seed=seed,
        access_rules=access_rules,
        verbose=False
    )

    # Evaluate HMARL
    dsr_hmarl = evaluate_dsr(
        marl,
        attack_strategy=attack_strategy,
        fnr=fnr,
        fpr=fpr,
        n_trials=n_eval_trials,
        seed=seed + 1,
        access_rules=access_rules
    )

    # Evaluate Random baseline
    env_tmp = HawkeyesEnv(fnr=fnr, fpr=fpr,
                          attack_strategy=attack_strategy,
                          access_rules=access_rules)
    set_seeds(seed + 2)
    n_succ = 0
    for _ in range(n_eval_trials):
        s = env_tmp.reset()
        d = False
        while not d:
            acts = [random.randint(0, env_tmp.action_dim - 1),
                    random.randint(0, env_tmp.action_dim - 1)]
            s, r, d, info = env_tmp.step(acts)
        if info["success"]:
            n_succ += 1
    dsr_random = n_succ / n_eval_trials * 100.0

    # Evaluate Critical baseline
    from network_topology import GROUP_MEMBERSHIP, CRITICAL_NODES
    crit_group = [g for g, m in GROUP_MEMBERSHIP.items()
                  if any(n in CRITICAL_NODES for n in m)][0]
    env_tmp2 = HawkeyesEnv(fnr=fnr, fpr=fpr,
                           attack_strategy=attack_strategy,
                           access_rules=access_rules)
    set_seeds(seed + 3)
    n_succ2 = 0
    for _ in range(n_eval_trials):
        s = env_tmp2.reset()
        d = False
        while not d:
            s, r, d, info = env_tmp2.step([crit_group, crit_group])
        if info["success"]:
            n_succ2 += 1
    dsr_critical = n_succ2 / n_eval_trials * 100.0

    result = {
        "trial_id":       trial_id,
        "attack_strategy":attack_strategy,
        "fnr":            fnr,
        "fpr":            fpr,
        "dsr_hmarl":      round(dsr_hmarl, 2),
        "dsr_random":     round(dsr_random, 2),
        "dsr_critical":   round(dsr_critical, 2),
        "training_time":  round(history["total_time"], 2),
        "episodes":       history["episodes"],
    }

    if verbose:
        print(f"    HMARL:    {dsr_hmarl:.2f}%")
        print(f"    Random:   {dsr_random:.2f}%")
        print(f"    Critical: {dsr_critical:.2f}%")

    return result


# =============================================================
# QUICK VERIFICATION — one fast training run
# =============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TRAIN.PY VERIFICATION")
    print("=" * 60)

    print("\nRunning quick training test (1000 steps)...")
    marl, history = train_single(
        attack_strategy="Ran",
        fnr=0.05,
        fpr=0.02,
        training_steps=1000,
        seed=42,
        verbose=True
    )

    print(f"\nTraining complete:")
    print(f"  Episodes:      {history['episodes']}")
    print(f"  Total time:    {history['total_time']:.2f}s")
    print(f"  Avg loss:      {np.mean(history['losses']):.4f}")

    print("\nEvaluating DSR (100 trials)...")
    dsr = evaluate_dsr(
        marl,
        attack_strategy="Ran",
        fnr=0.05,
        fpr=0.02,
        n_trials=100,
        seed=123
    )
    print(f"  DSR (HMARL):  {dsr:.2f}%")

    print("\nRunning one complete trial (1000 steps, 100 eval)...")
    result = run_one_trial(
        trial_id=1,
        attack_strategy="Ran",
        fnr=0.05,
        fpr=0.02,
        training_steps=1000,
        n_eval_trials=100,
        verbose=True
    )
    print(f"\nTrial result:")
    print(f"  HMARL:    {result['dsr_hmarl']}%")
    print(f"  Random:   {result['dsr_random']}%")
    print(f"  Critical: {result['dsr_critical']}%")
    print(f"  Time:     {result['training_time']}s")

    print("\ntrain.py verification complete.")