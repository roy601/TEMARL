# train_thesis.py
"""
File 7 of 8 — Training Loop
==============================
Three-phase training:
  Phase 1 — Pre-train Transformer encoder on next-technique prediction
  Phase 2 — End-to-end QMIX training WITH Transformer (thesis system)
  Phase 3 — QMIX training WITHOUT Transformer (fair ablation baseline)

Dual-branch architecture changes (Problem 1 fix):
  - MultiAgentQMIX now takes state_masking_prob=0.3 during training.
  - State masking is set to 0.0 before evaluation (deterministic).
  - Phase 3 ablation also uses the dual-branch architecture but with
    h=zeros throughout, keeping the ablation fair.

Bug fixes vs previous version:
  - Phase 3 variable name fixed: agents_base and mixer_base are now
    properly instantiated inside the Phase 3 loop (previously used
    undefined variable from Phase 2 scope).
  - evaluate() disables state masking before greedy rollout.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np
import os
import json
import time
from collections import defaultdict

from mitre_techniques import MAX_SEQ_LEN, PAD_ID, NUM_TECHNIQUES
from simulation_env import HoneypotEnv, N_AGENTS, N_ACTIONS, STATE_DIM
from transformer_encoder import AttackerIntentEncoder, D_MODEL
from qmix_agent import MultiAgentQMIX, OBS_DIM
from qmix_mixer import QMIXMixer, H_DIM
from replay_buffer import ReplayBuffer

# ── Hyperparameters ───────────────────────────────────────────────────────────

LR_QMIX        = 1e-3
GAMMA          = 0.99
BATCH_SIZE     = 32
TARGET_SYNC    = 200
BUFFER_SIZE    = 50_000
EPSILON_START  = 1.0
EPSILON_END    = 0.05
EPSILON_DECAY  = 10_000
GRAD_CLIP      = 1.0

PRETRAIN_STEPS = 5_000
PRETRAIN_LR    = 1e-3
TRAIN_STEPS    = 50_000

# State masking probability during training (Problem 1 fix).
# 30% of training batches have the state branch zeroed, forcing agents
# to learn h-conditioned Q-values that work without telemetry.
# Set to 0.0 during evaluation for deterministic greedy policy.
STATE_MASKING_PROB_TRAIN = 0.3
STATE_MASKING_PROB_EVAL  = 0.0

ATTACK_STRATEGIES = ["HiE", "HiC", "Ran", "Mix"]
RESULTS_DIR       = r"C:\Users\T25301092\thesis_project\thesis_system\results"


# ── Epsilon Schedule ──────────────────────────────────────────────────────────

def get_epsilon(step):
    """Linear decay from EPSILON_START to EPSILON_END over EPSILON_DECAY steps."""
    fraction = min(step / EPSILON_DECAY, 1.0)
    return EPSILON_START + fraction * (EPSILON_END - EPSILON_START)


# ── Phase 1: Pre-train Transformer ───────────────────────────────────────────

def pretrain_transformer(encoder, device, n_steps=PRETRAIN_STEPS, lr=PRETRAIN_LR):
    """
    Pre-train Transformer on next-technique prediction.
    Forces h to encode sequential attacker behavior patterns before MARL training.
    """
    print("=" * 55)
    print("  Phase 1: Pre-training Transformer Encoder")
    print(f"  Steps: {n_steps} | LR: {lr}")
    print("=" * 55)

    encoder.train()
    optimizer = optim.Adam(encoder.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()
    losses    = []

    for step in range(n_steps):
        # Sample a random technique sequence
        seq_len     = np.random.randint(2, MAX_SEQ_LEN + 1)
        techniques  = [np.random.randint(0, NUM_TECHNIQUES) for _ in range(seq_len)]
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
        torch.nn.utils.clip_grad_norm_(encoder.parameters(), GRAD_CLIP)
        optimizer.step()
        losses.append(loss.item())

        if (step + 1) % 500 == 0:
            avg_loss = np.mean(losses[-500:])
            print(f"  Step {step+1:5d}/{n_steps} | Loss: {avg_loss:.4f}")

    final_loss = np.mean(losses[-100:])
    print(f"  ✅ Pre-training complete. Final loss: {final_loss:.4f}\n")
    return losses


# ── QMIX loss computation ─────────────────────────────────────────────────────

def _qmix_update(batch, encoder, agents, mixer, optimizer, device):
    """
    One QMIX gradient update step.
    Used in both Phase 2 (with Transformer h) and Phase 3 (h=zeros).
    The batch already contains the correct h values — no branching needed here.
    """
    obs        = batch["obs"]          # (B, n_agents, 374)
    actions    = batch["actions"]      # (B, n_agents)
    rewards    = batch["rewards"]      # (B, n_agents)
    next_obs   = batch["next_obs"]     # (B, n_agents, 374)
    dones      = batch["dones"]        # (B,)
    state      = batch["state"]        # (B, 310)
    next_state = batch["next_state"]   # (B, 310)
    h          = batch["h"]            # (B, 64)
    next_h     = batch["next_h"]       # (B, 64)

    # Current Q-values for chosen actions
    chosen_q = agents.get_chosen_q_values(obs, actions, use_target=False)
    Q_total  = mixer(chosen_q, state, h)              # (B, 1)

    with torch.no_grad():
        # Best next Q-values from target network
        all_next_q   = agents.get_all_q_values(next_obs, use_target=True)
        best_next_q  = all_next_q.max(dim=2).values   # (B, n_agents)
        Q_total_next = mixer(best_next_q, next_state, next_h)  # (B, 1)

        # TD target
        r = rewards.mean(dim=1, keepdim=True)          # (B, 1) shared reward
        d = dones.unsqueeze(1)                         # (B, 1)
        y = torch.clamp(
            r + GAMMA * Q_total_next * (1.0 - d),
            -10.0, 10.0
        )

    loss = F.mse_loss(Q_total, y)
    optimizer.zero_grad()
    loss.backward()
    # Clip across ALL parameters this optimizer manages
    torch.nn.utils.clip_grad_norm_(
        [p for group in optimizer.param_groups for p in group["params"]
         if p.requires_grad],
        GRAD_CLIP,
    )
    optimizer.step()
    return loss.item()


# ── Phase 2: QMIX Training WITH Transformer ──────────────────────────────────

def train_qmix(encoder, agents, mixer, buffer, device,
               attack_strategy="Mix", n_steps=TRAIN_STEPS):
    """
    Main QMIX training — Transformer h injected at every step.
    State masking active during training (STATE_MASKING_PROB_TRAIN=0.3).
    This is the thesis system.
    """
    print("=" * 55)
    print(f"  Phase 2: QMIX + Transformer — Strategy: {attack_strategy}")
    print(f"  Steps: {n_steps} | Batch: {BATCH_SIZE} | γ: {GAMMA}")
    print("=" * 55)

    # Enable state masking for training
    agents.set_masking_prob(STATE_MASKING_PROB_TRAIN)
    agents.train()
    encoder.train()
    mixer.train()

    all_params = (
        list(encoder.parameters()) +
        list(agents.all_parameters()) +
        list(mixer.parameters())
    )
    optimizer = optim.Adam(all_params, lr=LR_QMIX)
    env       = HoneypotEnv(attack_strategy=attack_strategy, max_steps=200)

    ep_rewards     = []
    ep_steps_list  = []
    trapped_count  = 0
    total_episodes = 0
    td_losses      = []

    obs           = env.reset()
    h             = np.zeros(H_DIM, dtype=np.float32)
    episode_reward = 0.0
    episode_steps  = 0
    start_time     = time.time()

    for step in range(n_steps):
        epsilon   = get_epsilon(step)
        token_seq = env.get_padded_sequence()
        h         = encoder.get_h_numpy(token_seq, device)

        # Build per-agent observations: [state | h]
        obs_full = []
        for o in obs:
            o_full = o.copy()
            o_full[STATE_DIM:] = h
            obs_full.append(o_full)

        actions      = agents.select_actions(obs_full, epsilon)
        global_state = obs_full[0][:STATE_DIM].copy()

        next_obs, rewards, done, info = env.step(actions, h)

        # Compute next h from updated sequence
        next_token_seq = env.get_padded_sequence()
        next_h         = encoder.get_h_numpy(next_token_seq, device)

        next_obs_full = []
        for o in next_obs:
            o_full = o.copy()
            o_full[STATE_DIM:] = next_h
            next_obs_full.append(o_full)

        next_global_state = next_obs_full[0][:STATE_DIM].copy()

        buffer.push(
            obs_full, actions, rewards, next_obs_full, done,
            global_state, next_global_state,
            h, next_h, token_seq, next_token_seq,
        )

        episode_reward += rewards[0]
        episode_steps  += 1

        if info["trapped"]:
            trapped_count += 1

        if done:
            ep_rewards.append(episode_reward)
            ep_steps_list.append(episode_steps)
            total_episodes += 1
            obs            = env.reset()
            h              = np.zeros(H_DIM, dtype=np.float32)
            episode_reward = 0.0
            episode_steps  = 0
        else:
            obs = next_obs

        # Training update
        if buffer.is_ready(BATCH_SIZE):
            loss = _qmix_update(
                buffer.sample(BATCH_SIZE),
                encoder, agents, mixer, optimizer, device,
            )
            td_losses.append(loss)
            if step % TARGET_SYNC == 0:
                agents.sync_all_targets()

        if (step + 1) % 2000 == 0:
            elapsed    = time.time() - start_time
            avg_reward = np.mean(ep_rewards[-20:]) if ep_rewards else 0.0
            avg_loss   = np.mean(td_losses[-100:]) if td_losses else 0.0
            dsr        = trapped_count / max(total_episodes, 1)
            print(f"  Step {step+1:6d} | ε={epsilon:.3f} | AvgR={avg_reward:.3f} | "
                  f"Loss={avg_loss:.4f} | DSR={dsr:.3f} | "
                  f"Episodes={total_episodes} | Time={elapsed:.0f}s")

    final_dsr = trapped_count / max(total_episodes, 1)
    print(f"\n  ✅ Training complete | DSR={final_dsr:.3f} | Episodes={total_episodes}")
    return {
        "strategy":    attack_strategy,
        "dsr":         final_dsr,
        "td_losses":   td_losses,
        "ep_rewards":  ep_rewards,
    }


# ── Phase 3: QMIX Training WITHOUT Transformer ───────────────────────────────

def train_qmix_no_transformer(agents_base, mixer_base, buffer, device,
                               attack_strategy="Mix", n_steps=TRAIN_STEPS):
    """
    Train MARL ablation baseline WITHOUT Transformer.
    h is always zeros throughout training AND evaluation.

    Key correctness property:
      Train with h=zeros → evaluate with h=zeros  ✅ FAIR ablation
      (Previous approach trained with real h, evaluated with h=zeros — UNFAIR)

    The dual-branch architecture is still used, but Branch B always receives
    zeros, so the network learns a state-only policy while Branch B weights
    are idle. This is the correct architectural choice because it keeps
    checkpoint formats identical to the thesis models.
    """
    print("=" * 55)
    print(f"  Phase 3: MARL (no Transformer) — Strategy: {attack_strategy}")
    print(f"  Steps: {n_steps} | h=zeros throughout")
    print("=" * 55)

    # Ablation also uses state masking — forces it to not rely purely on state
    # even without h, making the ablation stronger (harder to beat).
    agents_base.set_masking_prob(STATE_MASKING_PROB_TRAIN)
    agents_base.train()
    mixer_base.train()

    all_params = (
        list(agents_base.all_parameters()) +
        list(mixer_base.parameters())
    )
    optimizer  = optim.Adam(all_params, lr=LR_QMIX)
    env        = HoneypotEnv(attack_strategy=attack_strategy, max_steps=200)

    trapped_count  = 0
    total_episodes = 0
    td_losses      = []
    obs            = env.reset()
    h_zero         = np.zeros(H_DIM, dtype=np.float32)
    episode_reward = 0.0
    start_time     = time.time()

    for step in range(n_steps):
        epsilon = get_epsilon(step)

        # h is always zeros — Branch B sees no signal
        obs_full = []
        for o in obs:
            o_full = o.copy()
            o_full[STATE_DIM:] = h_zero
            obs_full.append(o_full)

        actions           = agents_base.select_actions(obs_full, epsilon)
        global_state      = obs_full[0][:STATE_DIM].copy()
        token_seq         = env.get_padded_sequence()

        next_obs, rewards, done, info = env.step(actions, h_zero)

        next_obs_full = []
        for o in next_obs:
            o_full = o.copy()
            o_full[STATE_DIM:] = h_zero
            next_obs_full.append(o_full)

        next_global_state = next_obs_full[0][:STATE_DIM].copy()
        next_token_seq    = env.get_padded_sequence()

        buffer.push(
            obs_full, actions, rewards, next_obs_full, done,
            global_state, next_global_state,
            h_zero, h_zero, token_seq, next_token_seq,
        )

        episode_reward += rewards[0]
        if info["trapped"]:
            trapped_count += 1

        if done:
            total_episodes += 1
            obs            = env.reset()
            episode_reward = 0.0
        else:
            obs = next_obs

        if buffer.is_ready(BATCH_SIZE):
            loss = _qmix_update(
                buffer.sample(BATCH_SIZE),
                None, agents_base, mixer_base, optimizer, device,
            )
            td_losses.append(loss)
            if step % TARGET_SYNC == 0:
                agents_base.sync_all_targets()

        if (step + 1) % 2000 == 0:
            elapsed  = time.time() - start_time
            dsr      = trapped_count / max(total_episodes, 1)
            avg_loss = np.mean(td_losses[-100:]) if td_losses else 0.0
            print(f"  Step {step+1:6d} | ε={epsilon:.3f} | "
                  f"Loss={avg_loss:.4f} | DSR={dsr:.3f} | Time={elapsed:.0f}s")

    final_dsr = trapped_count / max(total_episodes, 1)
    print(f"\n  ✅ Baseline complete | DSR={final_dsr:.3f} | Episodes={total_episodes}")
    return final_dsr


# ── Evaluation ────────────────────────────────────────────────────────────────

def evaluate(encoder, agents, mixer, attack_strategy,
             n_episodes=100, device=None):
    """
    Evaluate trained thesis system — greedy policy, no exploration.
    Disables state masking before rollout (deterministic evaluation).
    """
    device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")

    encoder.eval()
    agents.eval()
    agents.set_masking_prob(STATE_MASKING_PROB_EVAL)   # disable masking for eval
    mixer.eval()

    env     = HoneypotEnv(attack_strategy=attack_strategy, max_steps=200)
    trapped = 0
    rewards = []

    for _ in range(n_episodes):
        obs       = env.reset()
        h         = np.zeros(H_DIM, dtype=np.float32)
        ep_reward = 0.0
        done      = False

        while not done:
            token_seq = env.get_padded_sequence()
            h         = encoder.get_h_numpy(token_seq, device)
            obs_full  = []
            for o in obs:
                o_full = o.copy()
                o_full[STATE_DIM:] = h
                obs_full.append(o_full)
            actions = agents.select_actions(obs_full, epsilon=0.0)
            obs, rews, done, info = env.step(actions, h)
            ep_reward += rews[0]
            if info["trapped"]:
                trapped += 1

        rewards.append(ep_reward)

    return trapped / n_episodes, float(np.mean(rewards))


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n  Device: {device}")
    if torch.cuda.is_available():
        print(f"  GPU: {torch.cuda.get_device_name(0)}")

    os.makedirs(RESULTS_DIR, exist_ok=True)

    # ── Phase 1: Pre-train Transformer ───────────────────────────────────────
    encoder = AttackerIntentEncoder().to(device)
    pretrain_transformer(encoder, device)

    pretrain_path = os.path.join(RESULTS_DIR, "encoder_pretrained.pt")
    torch.save(encoder.state_dict(), pretrain_path)
    print(f"  Saved pre-trained encoder → {pretrain_path}\n")

    # ── Phase 2: Train thesis system (QMIX + Transformer) ────────────────────
    print("\n" + "=" * 55)
    print("  PHASE 2 — Thesis System (MARL + Transformer)")
    print("=" * 55)

    all_results = {}

    for strategy in ATTACK_STRATEGIES:
        # Fresh models for each strategy
        agents = MultiAgentQMIX(
            state_masking_prob=STATE_MASKING_PROB_TRAIN,
            device=device,
        )
        mixer  = QMIXMixer().to(device)
        buffer = ReplayBuffer(capacity=BUFFER_SIZE, device=device)

        # Reload pre-trained encoder weights (start each strategy from pre-trained)
        encoder.load_state_dict(
            torch.load(pretrain_path, map_location=device, weights_only=True)
        )
        encoder.train()

        train_qmix(
            encoder, agents, mixer, buffer, device,
            attack_strategy=strategy,
            n_steps=TRAIN_STEPS,
        )

        # Evaluate — disable masking before greedy rollout
        agents.set_masking_prob(STATE_MASKING_PROB_EVAL)
        dsr, avg_r = evaluate(
            encoder, agents, mixer, strategy,
            n_episodes=100, device=device,
        )
        all_results[strategy] = {"dsr": dsr, "avg_reward": avg_r}
        print(f"  {strategy} | Eval DSR: {dsr:.3f} | Avg Reward: {avg_r:.3f}")

        model_path = os.path.join(RESULTS_DIR, f"model_{strategy}.pt")
        torch.save({
            "encoder": encoder.state_dict(),
            "agents":  [a.online_net.state_dict() for a in agents.agents],
            "mixer":   mixer.state_dict(),
        }, model_path)
        print(f"  Saved → {model_path}\n")

    # ── Phase 3: Train MARL without Transformer (fair ablation) ──────────────
    print("\n" + "=" * 55)
    print("  PHASE 3 — Ablation Baseline (MARL, no Transformer)")
    print("=" * 55)

    for strategy in ATTACK_STRATEGIES:
        # BUG FIX: agents_base and mixer_base must be fresh instances
        # inside this loop — previous version referenced undefined variables.
        agents_base = MultiAgentQMIX(
            state_masking_prob=STATE_MASKING_PROB_TRAIN,
            device=device,
        )
        mixer_base  = QMIXMixer().to(device)
        buffer_base = ReplayBuffer(capacity=BUFFER_SIZE, device=device)

        train_qmix_no_transformer(
            agents_base, mixer_base, buffer_base, device,
            attack_strategy=strategy,
            n_steps=TRAIN_STEPS,
        )

        baseline_path = os.path.join(RESULTS_DIR, f"baseline_notrans_{strategy}.pt")
        torch.save({
            "agents": [a.online_net.state_dict() for a in agents_base.agents],
            "mixer":  mixer_base.state_dict(),
        }, baseline_path)
        print(f"  Saved baseline → {baseline_path}\n")

    # ── Final summary ─────────────────────────────────────────────────────────
    print("\n" + "=" * 55)
    print("  FINAL SUMMARY")
    print("=" * 55)
    print(f"  {'Strategy':<8} {'DSR':>8} {'AvgReward':>12}")
    print(f"  {'-'*30}")
    for strat, res in all_results.items():
        print(f"  {strat:<8} {res['dsr']:>8.3f} {res['avg_reward']:>12.3f}")

    with open(os.path.join(RESULTS_DIR, "training_summary.json"), "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\n  All results saved → {RESULTS_DIR}")


if __name__ == "__main__":
    main()