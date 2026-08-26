# train_thesis_fixed.py
"""
File 7 of 8 — Training Loop (FIXED VERSION)
==============================================
Three-phase training:
  Phase 1 — Load COMISET fine-tuned Transformer encoder (Fix 1)
            (replaces random-sequence pretraining)
  Phase 2 — End-to-end QMIX training WITH Transformer (thesis system)
            Now passes predicted_technique to env for proactive reward (Fix 2)
  Phase 3 — QMIX training WITHOUT Transformer (fair ablation baseline)

Fixes applied:
  Fix 1 — Load encoder_finetuned_real.pt instead of random pretraining
  Fix 2 — Compute predicted technique from h and pass to env.step()
  Fix 5 — Deterministic seeding for reproducibility

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

import argparse
import copy
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np
import os
import json
import time
import random
from collections import defaultdict

import math
from mitre_techniques import MAX_SEQ_LEN, PAD_ID, NUM_TECHNIQUES, VOCAB_SIZE
from simulation_env import (HoneypotEnv, N_AGENTS, N_ACTIONS, STATE_DIM,
                            LOCAL_STATE_DIM, LOCAL_ATTACKER_PRESENT_IDX,
                            ALIGNMENT_MATRIX, NODE_TO_AGENT, HYBRID_PROFILE_NAMES)
from transformer_encoder import AttackerIntentEncoder, D_MODEL
from qmix_agent import MultiAgentQMIX, OBS_DIM
from qmix_mixer import QMIXMixer, H_DIM
from replay_buffer import ReplayBuffer

# ── Reproducibility (Fix 5) ──────────────────────────────────────────────────

SEED = 42

def set_seed(seed: int = SEED):
    """Lock all randomness sources for full reproducibility across runs."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark     = False

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
TRAIN_STEPS    = 80_000

# Auxiliary next-technique prediction loss weight (Cause 1 fix).
# Adds a direct supervision signal to the encoder during QMIX training so h
# adapts to simulation sequence patterns, not just COMISET ones.
# 0.1 keeps QMIX TD loss as the primary objective.
AUX_LAMBDA = 0.1

# Hard entropy threshold for training (calibrated from --diag-entropy diagnostic).
# Steps where encoder entropy > threshold have h zeroed before QMIX update,
# so agents learn to operate on telemetry alone when the Transformer is maximally
# uncertain (e.g. random attackers, entropy ~0.928).  Structured strategies
# (HiE/HiC entropy ~0.29-0.31) are unaffected.  Value 0.64 sits at the midpoint
# between HiE p90 (0.345) and Ran p10 (0.925) with a large safety margin.
ENTROPY_THRESHOLD = 0.64

# State masking probability during training (Problem 1 fix).
# 30% of training batches have the state branch zeroed, forcing agents
# to learn h-conditioned Q-values that work without telemetry.
# Set to 0.0 during evaluation for deterministic greedy policy.
STATE_MASKING_PROB_TRAIN = 0.3
STATE_MASKING_PROB_EVAL  = 0.0

# ── Observability mode (Dec-POMDP rework) ─────────────────────────────────────
# LOCAL_OBS=True  → each agent observes ONLY its own subnet (LOCAL_STATE_DIM=52);
#   the global attacker intent is available exclusively through the Transformer
#   vector h, making h non-redundant. The mixer still receives the full 310-dim
#   global state centrally via env.get_global_state() (CTDE preserved).
# LOCAL_OBS=False → legacy fully-observable mode (reproduces the pre-rework
#   models). Toggle at runtime with --global-obs.
#
# STATE_DIM (310) always denotes the GLOBAL state fed to the mixer.
# AGENT_STATE_DIM is the telemetry width each agent's Q-network sees.
# H_DIM (64) always occupies the LAST dims of every observation, so h is
# injected at obs[-H_DIM:] regardless of mode.
LOCAL_OBS       = True
AGENT_STATE_DIM = LOCAL_STATE_DIM if LOCAL_OBS else STATE_DIM
AGENT_OBS_DIM   = AGENT_STATE_DIM + H_DIM
# Index of the "attacker in my subnet" flag the gate reads as an explicit
# sighted signal (local mode only; None in global mode where every agent sees all).
AGENT_SIGHTED_IDX = LOCAL_ATTACKER_PRESENT_IDX if LOCAL_OBS else None

# ── Phase 4 fog fine-tuning ───────────────────────────────────────────────────
# The gate is trained at p=0.3 masking but evaluated at up to p=0.90 fog.
# Phase 4 closes this gap: freeze encoder (h quality stays), fine-tune
# gate + Q-network with fog sampled from [FOG_LOW, FOG_HIGH] so the gate
# learns to shift reliance toward h when state is severely degraded.
FOG_FINETUNE_STEPS = 20_000
FOG_FINETUNE_LR    = 3e-4
FOG_LOW            = 0.50    # minimum fog probability sampled per episode
FOG_HIGH           = 0.95    # maximum fog probability sampled per episode
FOG_MIX_RATIO      = 0.50    # fraction of episodes that use high fog; rest use 0.3

# Train ONE model on the Hybrid mixture: the hidden campaign profile is resampled
# every episode, so the agent CANNOT memorise a single campaign — it must actually
# infer intent from the technique sequence. Per-profile breakdowns are produced at
# EVALUATION time by running this one model against each forced-profile env.
# Legacy ["HiE","HiC","Ran","Mix"] kept below for reproducing the pre-rework results.
ATTACK_STRATEGIES        = ["Hybrid"]
LEGACY_ATTACK_STRATEGIES = ["HiE", "HiC", "Ran", "Mix"]
RESULTS_DIR       = r"results"

# ── Intent-mechanism calibration ──────────────────────────────────────────────
# A single temperature scaling the next-technique predictor so its reported
# entropy reflects true reliability (fixes over-confident HiC predictions that
# the entropy-aware gate wrongly trusts). Fit per-strategy on the trained
# encoder and stored inside each model checkpoint ("temperature" key).
CALIB_EPISODES   = 60   # simulation episodes per strategy for calibration data

# ── RAIF Stage A — PEAP + Decision-Focused Loss ───────────────────────────────
# Rationale (Decision-Sufficiency): the Bayes-optimal defensive action depends on
# the intent posterior p ONLY through u = A^T p. The previous architecture used
# MAP action selection (commit to argmax_tau p) which is provably suboptimal
# under uncertainty and is the root of the HiC bias-variance failure: HiC's
# intent-optimal action (credential_store) is SPECIALIZED and back-fires on the
# ~51% mispredictions, whereas the broadly-safe action wins in expectation.
# u = A^T p hedges AUTOMATICALLY when p is diffuse and commits when p is peaked.
#
# USE_INTENT_PRIOR : inject u into Q as an action-indexed prior (lambda_p init 0)
# DFL_LAMBDA       : weight of the decision-focused loss inside the encoder aux
# DFL_ETA          : softmax temperature for the differentiable argmax relaxation
USE_INTENT_PRIOR = True
DFL_LAMBDA       = 1.0
DFL_ETA          = 0.1

# ── Encoder pre-adaptation + freeze (fixes TD divergence) ─────────────────────
# DIAGNOSIS. train_qmix previously put encoder+agents+mixer in ONE optimiser, so
# the encoder received TD gradients and h changed every step; and encoder.train()
# left DROPOUT ACTIVE, so h was stochastic on every forward pass as well. The
# Q-network's input distribution was therefore doubly non-stationary and TD
# learning diverged: Thesis TD loss ROSE 4.3 -> 7.9 while the NoTrans ablation
# (h frozen at zeros, hence stationary) converged cleanly 9.6 -> 0.8. Downstream
# the Thesis Q-values went flat (range ~0.1), actions went near-uniform (24% on
# the WORST action) and alignment fell to the random-policy level.
#
# FIX (standard two-stage practice). Stage 1: adapt the COMISET encoder to the
# simulation with the supervised next-technique objective. Stage 2: FREEZE it and
# run it in eval() during QMIX, so h is deterministic and stationary and the
# value function can actually converge. The encoder needs no TD signal — it
# already reaches 0.698 on a latent-profile probe and 0.360 next-technique
# accuracy, beating the 0.313 bigram oracle.
FREEZE_ENCODER_IN_QMIX = True
ENC_PRETRAIN_EPISODES  = 1500     # simulation episodes collected for adaptation
ENC_PRETRAIN_STEPS     = 6000     # supervised minibatch steps
ENC_PRETRAIN_LR        = 5e-4
ENC_PRETRAIN_BATCH     = 128

# ── FIX-1: imitation-pretrained, variance-reduced policy learning ─────────────
# The learner is moved OFF the TD value function (which diverged: signal/noise
# ~0.57, TD loss stuck 7-9, flat Q, near-random actions) and ONTO a policy head
# trained by (1) supervised imitation of the profile-optimal action over the
# FROZEN intent representation, then (2) a GUARDED PPO fine-tune with a state-
# value baseline (COMA's counterfactual over other agents degenerates to V(f)
# here because exactly one agent is scored per step).
RUN_POLICY_HEAD        = True     # Phase 2b: train the FIX-1 policy
POLICY_IL_EPISODES     = 1500     # rollouts collected for imitation targets
POLICY_IL_STEPS        = 4000     # imitation minibatch steps
POLICY_IL_LR           = 1e-3
POLICY_IL_BATCH        = 128
POLICY_ASTAR_EPISODES  = 3000     # random-action rollouts to estimate a*(profile)
POLICY_EVAL_EPISODES   = 150      # in-env alignment eval (guard metric)

RUN_POLICY_RL          = True     # Phase 2b step 2: guarded PPO fine-tune
POLICY_RL_ITERS        = 40       # PPO outer iterations
POLICY_RL_ROLLOUT_EPS  = 40       # on-policy episodes per iteration
POLICY_RL_EPOCHS       = 4        # PPO epochs per rollout
POLICY_RL_MINIBATCH    = 256
POLICY_RL_LR           = 1e-4     # small: fine-tune, do not overwrite imitation
PPO_CLIP               = 0.2
PPO_ENT_COEF           = 0.005
PPO_VAL_COEF           = 0.5
PPO_EVAL_EVERY         = 5        # iters between guard evaluations

_ALIGN_T = {}   # device -> torch alignment matrix cache


def peap_prior(logits: torch.Tensor) -> torch.Tensor:
    """
    PEAP: posterior-expected alignment per action,  u = A^T p.

    Restricted to REAL techniques (rows 0..NUM_TECHNIQUES-1); PAD/UNK logits are
    dropped before the softmax so the posterior is a proper distribution over
    techniques the attacker can actually execute.

    logits: (..., VOCAB_SIZE)  ->  u: (..., N_ACTIONS)
    """
    dev = logits.device
    if dev not in _ALIGN_T:
        _ALIGN_T[dev] = torch.as_tensor(ALIGNMENT_MATRIX, dtype=torch.float32, device=dev)
    A = _ALIGN_T[dev]                                   # (NUM_TECHNIQUES, N_ACTIONS)
    p = torch.softmax(logits[..., :NUM_TECHNIQUES], dim=-1)
    return p @ A                                        # (..., N_ACTIONS)


# ── Confidence calibration (Retrain #5) — DISABLED for RAIF Stage A ───────────
# Retrain #5 demonstrated temperature scaling is DECISION-INSUFFICIENT here: it
# is a global monotone map, and because entropy is bounded above, it compresses
# the low-entropy end far more than the high end — destroying the gate's
# discriminative margin exactly on the reliable-h profiles (HiE/Mix collapsed;
# HiE blind gap flipped +0.082 -> -0.094). PEAP replaces it with the
# decision-sufficient statistic u = A^T p. Set True only to reproduce #5.
USE_CALIBRATION  = False
CALIB_REFIT_FRAC = 0.6  # fraction through Phase 2 at which to fit the temperature
                        # (encoder has adapted by then) so the gate trains on the
                        # calibrated entropy it will also see at eval.


# ── Epsilon Schedule ──────────────────────────────────────────────────────────

def get_epsilon(step):
    """Linear decay from EPSILON_START to EPSILON_END over EPSILON_DECAY steps."""
    fraction = min(step / EPSILON_DECAY, 1.0)
    return EPSILON_START + fraction * (EPSILON_END - EPSILON_START)


# ── Stage 1: supervised encoder adaptation to the simulation ─────────────────

def collect_sim_sequences(strategy, n_eps, device):
    """Roll out the environment and collect (padded_sequence -> next technique)."""
    env = HoneypotEnv(attack_strategy=strategy, max_steps=200, local_obs=LOCAL_OBS)
    hz  = np.zeros(H_DIM, dtype=np.float32)
    X, Y = [], []
    for _ in range(n_eps):
        env.reset(); done = False
        while not done:
            seq = env.get_padded_sequence()          # history BEFORE this step
            _, _, done, info = env.step([0] * N_AGENTS, hz)
            tau = info["technique_id"]               # the technique it predicts
            if 0 <= tau < PAD_ID:
                X.append(seq); Y.append(tau)
    return (torch.LongTensor(np.array(X)).to(device),
            torch.LongTensor(np.array(Y)).to(device))


def pretrain_encoder_on_sim(encoder, device, strategy=None,
                            n_eps=ENC_PRETRAIN_EPISODES, n_steps=ENC_PRETRAIN_STEPS,
                            lr=ENC_PRETRAIN_LR, batch=ENC_PRETRAIN_BATCH):
    """
    Adapt the COMISET-fine-tuned encoder to the SIMULATION distribution with the
    supervised next-technique objective (CE + the decision-focused term), so that
    it can subsequently be FROZEN during QMIX. Doing the adaptation here rather
    than through TD gradients is what makes h stationary — see FREEZE_ENCODER_IN_QMIX.
    """
    strategy = strategy or ATTACK_STRATEGIES[0]
    print("=" * 55)
    print(f"  Stage 1: Encoder adaptation on simulation -- {strategy}")
    print(f"  Episodes: {n_eps} | Steps: {n_steps} | LR: {lr}")
    print("=" * 55)

    X, Y = collect_sim_sequences(strategy, n_eps, device)
    n = len(Y); cut = int(0.8 * n)
    perm = torch.randperm(n, device=device)
    tr, va = perm[:cut], perm[cut:]
    print(f"  collected {n:,} (sequence -> next technique) pairs")

    def val_acc():
        encoder.eval()
        with torch.no_grad():
            _, lg = encoder.pretrain_forward(X[va])
            return float((lg.argmax(-1) == Y[va]).float().mean())

    before = val_acc()
    opt = optim.Adam(encoder.parameters(), lr=lr)
    encoder.train()
    for step in range(n_steps):
        idx = tr[torch.randint(0, len(tr), (batch,), device=device)]
        _, logits = encoder.pretrain_forward(X[idx])
        loss = F.cross_entropy(logits, Y[idx])
        if DFL_LAMBDA > 0.0:                       # decision-focused term
            u  = peap_prior(logits)
            pi = torch.softmax(u / DFL_ETA, dim=-1)
            A  = _ALIGN_T[logits.device]
            loss = loss + DFL_LAMBDA * (-(pi * A[Y[idx]]).sum(-1).mean())
        opt.zero_grad(); loss.backward()
        torch.nn.utils.clip_grad_norm_(encoder.parameters(), GRAD_CLIP)
        opt.step()
        if (step + 1) % 2000 == 0:
            print(f"  Step {step+1:5d}/{n_steps} | loss={loss.item():.4f} | val acc={val_acc():.3f}")
            encoder.train()
    after = val_acc()
    encoder.eval()
    print(f"  next-technique accuracy: {before:.3f} -> {after:.3f}"
          f"   (bigram oracle reference ~0.31)\n")
    return after


# ── Confidence calibration (intent-mechanism fix) ─────────────────────────────

def fit_temperature(encoder, device, strategies=ATTACK_STRATEGIES, n_eps=CALIB_EPISODES):
    """
    Fit ONE confidence-calibration temperature for the encoder's next-technique
    predictor by minimizing NLL on held-out simulation rollouts (gradient-free
    grid search, robust). Only flattening is allowed (T >= 1.0) since the
    predictor is over-confident, never under-confident. Saves T to
    CALIB_TEMP_PATH and returns it. Applied so the entropy-aware gate can hedge
    when h is unreliable (the diagnosed HiC failure mode).
    """
    encoder.eval()
    logits_list, labels = [], []
    h_zero = np.zeros(H_DIM, dtype=np.float32)
    with torch.no_grad():
        for strat in strategies:
            env = HoneypotEnv(attack_strategy=strat, max_steps=200, local_obs=LOCAL_OBS)
            for _ in range(n_eps):
                obs = env.reset(); done = False
                while not done:
                    seq = env.get_padded_sequence()   # techniques BEFORE this step
                    h   = encoder.get_h_numpy(seq, device)
                    lg  = encoder.pretrain_head(
                        torch.FloatTensor(h).unsqueeze(0).to(device)).squeeze(0).cpu()
                    # actions do not affect which technique the attacker picks
                    _, _, done, info = env.step([0] * N_AGENTS, h_zero)
                    T = info["technique_id"]
                    if 0 <= T < PAD_ID:               # valid (non-PAD/UNK) label
                        logits_list.append(lg)
                        labels.append(T)
    if not logits_list:
        print("  [calib] no data collected; temperature = 1.0")
        return 1.0

    L = torch.stack(logits_list)          # (N, VOCAB_SIZE)
    y = torch.LongTensor(labels)          # (N,)
    top1 = (L.argmax(dim=-1) == y).float().mean().item()
    best_T, best_nll = 1.0, float("inf")
    for T in np.arange(1.0, 5.01, 0.1):
        nll = F.cross_entropy(L / float(T), y).item()
        if nll < best_nll:
            best_nll, best_T = nll, float(T)

    # Report calibration effect on mean entropy (diagnostic)
    _lv = math.log(VOCAB_SIZE)
    ent_raw = (-(torch.softmax(L, -1) * torch.log_softmax(L, -1)).sum(-1) / _lv).mean().item()
    ent_cal = (-(torch.softmax(L / best_T, -1)
                 * torch.log_softmax(L / best_T, -1)).sum(-1) / _lv).mean().item()
    print(f"  [calib] N={len(y)}  top-1={top1:.3f}  best T={best_T:.2f}  "
          f"NLL {F.cross_entropy(L, y).item():.3f}->{best_nll:.3f}  "
          f"mean entropy {ent_raw:.3f}->{ent_cal:.3f}")
    return best_T


# ── Phase 1: Pre-train Transformer (FALLBACK ONLY) ──────────────────────────
# This function is kept as a fallback in case encoder_finetuned_real.pt
# does not exist. Normally, Fix 1 skips this entirely and loads the
# COMISET fine-tuned encoder directly.

def pretrain_transformer(encoder, device, n_steps=PRETRAIN_STEPS, lr=PRETRAIN_LR):
    """
    Pre-train Transformer on next-technique prediction.
    Forces h to encode sequential attacker behavior patterns before MARL training.
    NOTE: This is the FALLBACK path. Prefer COMISET fine-tuned encoder (Fix 1).
    """
    print("=" * 55)
    print("  Phase 1: Pre-training Transformer Encoder (FALLBACK)")
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
    print(f"  Pre-training complete. Final loss: {final_loss:.4f}\n")
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

    # Compute normalized entropy from stored h values for entropy-aware gate.
    # Recomputing from stored h avoids adding a new buffer field.
    # NoTrans (encoder=None): entropy=1.0 (h=zeros -> uniform probs -> max uncertainty)
    intent_prior_t = next_intent_prior_t = None
    if encoder is not None:
        with torch.no_grad():
            # Temperature-calibrated entropy so the gate trains on the same
            # reliability signal it will see at inference (intent-mechanism fix).
            logits_h       = encoder.pretrain_head(h)
            logits_nh      = encoder.pretrain_head(next_h)
            entropy_t      = encoder.calibrated_entropy(logits_h).unsqueeze(-1)   # (B,1)
            next_entropy_t = encoder.calibrated_entropy(logits_nh).unsqueeze(-1)  # (B,1)
            # PEAP action-indexed prior u = A^T p (no grad: the encoder is shaped
            # by CE + DFL, not by TD noise flowing back through the prior path).
            if USE_INTENT_PRIOR:
                intent_prior_t      = peap_prior(logits_h)    # (B, N_ACTIONS)
                next_intent_prior_t = peap_prior(logits_nh)   # (B, N_ACTIONS)
    else:
        B = h.shape[0]
        entropy_t      = torch.ones(B, 1, device=h.device)
        next_entropy_t = entropy_t

    # Current Q-values for chosen actions
    chosen_q = agents.get_chosen_q_values(obs, actions, use_target=False, entropy_t=entropy_t,
                                          intent_prior_t=intent_prior_t)
    Q_total  = mixer(chosen_q, state, h)              # (B, 1)

    with torch.no_grad():
        # Best next Q-values from target network
        all_next_q   = agents.get_all_q_values(next_obs, use_target=True, entropy_t=next_entropy_t,
                                               intent_prior_t=next_intent_prior_t)
        best_next_q  = all_next_q.max(dim=2).values   # (B, n_agents)
        Q_total_next = mixer(best_next_q, next_state, next_h)  # (B, 1)

        # TD target
        r = rewards.mean(dim=1, keepdim=True)          # (B, 1) shared reward
        d = dones.unsqueeze(1)                         # (B, 1)
        y = torch.clamp(
            r + GAMMA * Q_total_next * (1.0 - d),
            -10.0, 10.0
        )

    td_loss = F.mse_loss(Q_total, y)

    # Auxiliary next-technique prediction loss (Cause 1 fix).
    # Forces the encoder to learn simulation sequence patterns directly,
    # not just through weak Q-gradient backprop from td_loss.
    # Target: last token of next_token_seq = technique just performed.
    # Only active for Thesis (encoder != None); Phase 3 passes encoder=None.
    aux_loss = torch.tensor(0.0, device=h.device)
    dec_loss = torch.tensor(0.0, device=h.device)
    # Skip the encoder-side losses entirely when the encoder is frozen: it was
    # already adapted in Stage 1, and back-propagating here would neither update
    # it nor be desirable (that co-training is what destabilised TD learning).
    enc_trainable = (encoder is not None
                     and any(p.requires_grad for p in encoder.parameters()))
    if enc_trainable:
        token_seq     = batch["token_seq"]             # (B, MAX_SEQ_LEN) LongTensor
        next_tech_tgt = batch["next_token_seq"][:, -1] # (B,) — most recent technique
        valid = next_tech_tgt < PAD_ID                 # exclude PAD=23, UNK=24
        if valid.any():
            _, logits_aux = encoder.pretrain_forward(token_seq[valid])
            aux_loss = F.cross_entropy(logits_aux, next_tech_tgt[valid])

            # ── DFL: Decision-Focused Loss ────────────────────────────────
            # Cross-entropy makes the posterior LIKELY; DFL makes it USEFUL.
            # Relax argmax_a u(a) into a softmax policy and maximise the
            # alignment actually realised against the TRUE technique:
            #     pi~ = softmax(u / eta),   L_dec = -sum_a pi~(a) A[tau_true, a]
            # Gradients flow encoder -> p -> u -> pi~, so the encoder learns to
            # emit posteriors that induce good DECISIONS, hedging toward robust
            # actions when it cannot resolve the technique (the HiC fix).
            if DFL_LAMBDA > 0.0:
                u_aux    = peap_prior(logits_aux)                    # (Bv, N_ACTIONS)
                pi_soft  = torch.softmax(u_aux / DFL_ETA, dim=-1)    # (Bv, N_ACTIONS)
                A_dev    = _ALIGN_T[logits_aux.device]               # (NUM_TECHNIQUES, N_ACTIONS)
                tgt_rows = A_dev[next_tech_tgt[valid]]               # (Bv, N_ACTIONS)
                dec_loss = -(pi_soft * tgt_rows).sum(dim=-1).mean()

    loss = td_loss + AUX_LAMBDA * (aux_loss + DFL_LAMBDA * dec_loss)
    optimizer.zero_grad()
    loss.backward()
    # Clip across ALL parameters this optimizer manages
    torch.nn.utils.clip_grad_norm_(
        [p for group in optimizer.param_groups for p in group["params"]
         if p.requires_grad],
        GRAD_CLIP,
    )
    optimizer.step()
    return td_loss.item()


# ── Phase 2: QMIX Training WITH Transformer ──────────────────────────────────

def train_qmix(encoder, agents, mixer, buffer, device,
               attack_strategy="Mix", n_steps=TRAIN_STEPS,
               checkpoint_every=10_000):
    """
    Main QMIX training — Transformer h injected at every step.
    State masking active during training (STATE_MASKING_PROB_TRAIN=0.3).
    Saves a checkpoint every checkpoint_every steps and keeps the best by DSR,
    restoring it at the end so a bad final state does not overwrite a good one.

    Fix 2: Computes predicted_technique from h and passes it to env.step()
           so the proactive alignment bonus (r5) can be computed.
    """
    print("=" * 55)
    print(f"  Phase 2: QMIX + Transformer -- Strategy: {attack_strategy}")
    print(f"  Steps: {n_steps} | Batch: {BATCH_SIZE} | gamma: {GAMMA}")
    print("=" * 55)

    # Enable state masking for training
    agents.set_masking_prob(STATE_MASKING_PROB_TRAIN)
    agents.train()
    mixer.train()
    # Start uncalibrated; the temperature is fit mid-training (see calib_step)
    # so it is consistent across strategies and independent of prior runs.
    encoder.set_temperature(1.0)
    calib_step = int(CALIB_REFIT_FRAC * n_steps)

    if FREEZE_ENCODER_IN_QMIX:
        # Stationary h: no TD gradients into the encoder AND eval() so dropout is
        # OFF (otherwise h is stochastic on every forward pass). Both were sources
        # of the non-stationarity that made the Thesis TD loss diverge.
        for p in encoder.parameters():
            p.requires_grad = False
        encoder.eval()
        all_params = list(agents.all_parameters()) + list(mixer.parameters())
        print("  Encoder FROZEN (eval mode) -- h is deterministic and stationary")
    else:
        encoder.train()
        all_params = (list(encoder.parameters()) +
                      list(agents.all_parameters()) +
                      list(mixer.parameters()))
    optimizer = optim.Adam(all_params, lr=LR_QMIX)
    env       = HoneypotEnv(attack_strategy=attack_strategy, max_steps=200, local_obs=LOCAL_OBS)

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

    # Checkpoint-best tracking: keep the weights that produced the highest DSR
    # across all checkpoint evaluations, then restore them at the end.
    best_ckpt_dsr  = -1.0
    best_ckpt_state = None   # dict with encoder/agents/mixer state_dicts (CPU)

    # Fix 2: track predicted technique for proactive reward
    # At the start, there is no previous prediction
    current_predicted_technique = None

    for step in range(n_steps):
        # Mid-training calibration refit (intent-mechanism fix): once the encoder
        # has adapted to the simulation, fit the confidence temperature and train
        # the gate on the calibrated entropy for the remaining steps, so the gate
        # sees the SAME reliability signal at train and eval time.
        if USE_CALIBRATION and step == calib_step:
            t_fit = fit_temperature(encoder, device,
                                    strategies=[attack_strategy], n_eps=40)
            encoder.set_temperature(t_fit)
            encoder.train()
            print(f"  [calib] refit at step {step}: temperature = {t_fit:.2f}")

        epsilon   = get_epsilon(step)
        token_seq = env.get_padded_sequence()

        # Get h and normalized entropy in one forward pass
        h, entropy_scalar = encoder.get_h_and_entropy_numpy(token_seq, device)

        # Hard entropy masking: when Transformer is maximally uncertain, zero h.
        # Agents must learn to act on telemetry alone for high-entropy episodes
        # so that the same masking at eval time is in-distribution.
        h_eff   = np.zeros(H_DIM, dtype=np.float32) if entropy_scalar > ENTROPY_THRESHOLD else h
        ent_eff = 1.0 if entropy_scalar > ENTROPY_THRESHOLD else entropy_scalar

        # Compute predicted next technique (argmax of pretrain head) from real h
        with torch.no_grad():
            h_t    = torch.FloatTensor(h).unsqueeze(0).to(device)
            logits = encoder.pretrain_head(h_t)
            new_predicted_technique = logits.argmax(dim=-1).item()
            # PEAP prior from the EFFECTIVE h, so it stays consistent with what
            # _qmix_update recomputes from the stored (possibly masked) h.
            intent_prior = None
            if USE_INTENT_PRIOR:
                h_eff_t      = torch.FloatTensor(h_eff).unsqueeze(0).to(device)
                intent_prior = peap_prior(encoder.pretrain_head(h_eff_t)).squeeze(0)

        # Build per-agent observations: [state | h_eff]
        obs_full = []
        for o in obs:
            o_full = o.copy()
            o_full[-H_DIM:] = h_eff
            obs_full.append(o_full)

        # Pass masked entropy + PEAP prior to the Q-networks
        actions      = agents.select_actions(obs_full, epsilon, entropy_val=ent_eff,
                                             intent_prior=intent_prior)
        global_state = env.get_global_state()

        # Fix 2: pass current_predicted_technique (from previous step's prediction)
        # to env.step() so the reward function can compute r5
        next_obs, rewards, done, info = env.step(
            actions,
            h,
            predicted_technique=current_predicted_technique,  # Fix 2
        )

        # Update prediction for next step
        current_predicted_technique = new_predicted_technique

        # Compute next h and apply same masking
        next_token_seq          = env.get_padded_sequence()
        next_h, next_entropy    = encoder.get_h_and_entropy_numpy(next_token_seq, device)
        next_h_eff = np.zeros(H_DIM, dtype=np.float32) if next_entropy > ENTROPY_THRESHOLD else next_h

        next_obs_full = []
        for o in next_obs:
            o_full = o.copy()
            o_full[-H_DIM:] = next_h_eff
            next_obs_full.append(o_full)

        next_global_state = env.get_global_state()

        buffer.push(
            obs_full, actions, rewards, next_obs_full, done,
            global_state, next_global_state,
            h_eff, next_h_eff, token_seq, next_token_seq,
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
            # Fix 2: reset prediction at episode boundary
            current_predicted_technique = None
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
            print(f"  Step {step+1:6d} | eps={epsilon:.3f} | AvgR={avg_reward:.3f} | "
                  f"TDLoss={avg_loss:.4f} | DSR={dsr:.3f} | "
                  f"Episodes={total_episodes} | Time={elapsed:.0f}s")

        # Checkpoint evaluation — quick greedy rollout every checkpoint_every steps
        if (step + 1) % checkpoint_every == 0:
            agents.set_masking_prob(STATE_MASKING_PROB_EVAL)
            agents.eval(); encoder.eval(); mixer.eval()
            ckpt_dsr, ckpt_rew = evaluate(encoder, agents, mixer, attack_strategy,
                                          n_episodes=30, device=device)
            if ckpt_dsr > best_ckpt_dsr:
                best_ckpt_dsr = ckpt_dsr
                best_ckpt_state = {
                    "encoder": copy.deepcopy(encoder.state_dict()),
                    "agents":  [copy.deepcopy(a.online_net.state_dict())
                                for a in agents.agents],
                    "mixer":   copy.deepcopy(mixer.state_dict()),
                }
                print(f"  [ckpt] step={step+1} DSR={ckpt_dsr:.3f} AvgR={ckpt_rew:.3f}  ← new best")
            else:
                print(f"  [ckpt] step={step+1} DSR={ckpt_dsr:.3f} AvgR={ckpt_rew:.3f}  (best={best_ckpt_dsr:.3f})")
            # Restore training mode (encoder stays frozen/eval when applicable)
            agents.set_masking_prob(STATE_MASKING_PROB_TRAIN)
            agents.train(); mixer.train()
            if not FREEZE_ENCODER_IN_QMIX:
                encoder.train()

    final_dsr = trapped_count / max(total_episodes, 1)
    print(f"\n  Training complete | DSR={final_dsr:.3f} | Episodes={total_episodes}")

    # Restore best checkpoint weights if any were saved
    if best_ckpt_state is not None:
        encoder.load_state_dict(best_ckpt_state["encoder"])
        for i, a in enumerate(agents.agents):
            a.online_net.load_state_dict(best_ckpt_state["agents"][i])
        mixer.load_state_dict(best_ckpt_state["mixer"])
        print(f"  Restored best checkpoint (DSR={best_ckpt_dsr:.3f})")

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
      Train with h=zeros -> evaluate with h=zeros  (FAIR ablation)
      (Previous approach trained with real h, evaluated with h=zeros — UNFAIR)

    The dual-branch architecture is still used, but Branch B always receives
    zeros, so the network learns a state-only policy while Branch B weights
    are idle. This is the correct architectural choice because it keeps
    checkpoint formats identical to the thesis models.

    NOTE: predicted_technique is NOT passed to env.step() here.
          This means prev_predicted_tech=None in _compute_reward(),
          so r5=0 and NoTrans uses the reactive reward weights.
    """
    print("=" * 55)
    print(f"  Phase 3: MARL (no Transformer) -- Strategy: {attack_strategy}")
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
    env        = HoneypotEnv(attack_strategy=attack_strategy, max_steps=200, local_obs=LOCAL_OBS)

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
            o_full[-H_DIM:] = h_zero
            obs_full.append(o_full)

        actions           = agents_base.select_actions(obs_full, epsilon)
        global_state      = env.get_global_state()
        token_seq         = env.get_padded_sequence()

        # NoTrans: predicted_technique is NOT passed (defaults to None)
        # This means r5=0 and NoTrans gets reactive reward weights
        next_obs, rewards, done, info = env.step(actions, h_zero)

        next_obs_full = []
        for o in next_obs:
            o_full = o.copy()
            o_full[-H_DIM:] = h_zero
            next_obs_full.append(o_full)

        next_global_state = env.get_global_state()
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
            print(f"  Step {step+1:6d} | eps={epsilon:.3f} | "
                  f"Loss={avg_loss:.4f} | DSR={dsr:.3f} | Time={elapsed:.0f}s")

    final_dsr = trapped_count / max(total_episodes, 1)
    print(f"\n  Baseline complete | DSR={final_dsr:.3f} | Episodes={total_episodes}")
    return final_dsr


# ── Phase 4: Fog-Aware Fine-tuning ───────────────────────────────────────────

def _apply_obs_fog(obs_full, fog_prob):
    """Zero fog_prob fraction of the telemetry features (everything except the
    trailing H_DIM intent vector) per observation. Mode-agnostic: works for the
    global (310) and local (LOCAL_STATE_DIM) observation layouts alike; h is
    never masked."""
    if fog_prob <= 0.0:
        return obs_full
    result = []
    for o in obs_full:
        o2   = o.copy()
        sdim = o2.shape[0] - H_DIM
        mask = np.random.binomial(1, 1.0 - fog_prob, size=sdim).astype(np.float32)
        o2[:sdim] *= mask
        result.append(o2)
    return result


def train_qmix_fog_finetune(encoder, agents, mixer, device,
                             attack_strategy, n_steps=FOG_FINETUNE_STEPS):
    """
    Phase 4: Fog-aware fine-tuning of the trained TEMARL model.

    Problem solved:
      Phase 2 trains with STATE_MASKING_PROB=0.3, so the gate never learns
      to exploit h aggressively at fog=75-90%. At those levels h is the only
      intact signal, but the gate stays near its init bias (~0.88 telemetry)
      because it was never forced to shift lower.

    Fix:
      Freeze the encoder (h is already well-trained). Fine-tune gate + Q-network
      with fog_prob ~ Uniform(FOG_LOW, FOG_HIGH) on FOG_MIX_RATIO fraction of
      episodes, interleaved with standard p=0.3 episodes to preserve no-fog
      performance. The TD loss reward signal teaches the gate that g→0 (use h)
      yields better Q-values when the state branch carries mostly zeros.

    Expected effect:
      At fog=75-90%: gate shifts to g≈0.4-0.6 (vs ~0.88 before), producing
      statistically significant alignment advantage over NoTrans (h=zeros).
      At fog=0-25%: performance unchanged (preserved by the mixed training).
    """
    print("=" * 60)
    print(f"  Phase 4: Fog Fine-tuning -- Strategy: {attack_strategy}")
    print(f"  Steps: {n_steps} | LR: {FOG_FINETUNE_LR}")
    print(f"  Fog: Uniform({FOG_LOW:.0%}, {FOG_HIGH:.0%}) for {FOG_MIX_RATIO:.0%} of episodes")
    print(f"  Encoder: FROZEN -- only gate + Q-network updated")
    print("=" * 60)

    # Freeze encoder weights — h quality must not degrade
    encoder.eval()
    for p in encoder.parameters():
        p.requires_grad = False

    # Fog applied externally to obs; disable internal masking to avoid double-mask
    agents.set_masking_prob(0.0)
    agents.train()
    mixer.train()

    # Fresh buffer: fog-conditioned experiences only — no stale Phase 2 data
    fog_buffer = ReplayBuffer(capacity=BUFFER_SIZE, obs_dim=AGENT_OBS_DIM, device=device)

    finetune_params = list(agents.all_parameters()) + list(mixer.parameters())
    optimizer  = optim.Adam(finetune_params, lr=FOG_FINETUNE_LR)
    env        = HoneypotEnv(attack_strategy=attack_strategy, max_steps=200, local_obs=LOCAL_OBS)

    td_losses      = []
    total_episodes = 0
    trapped_count  = 0
    episode_fog    = STATE_MASKING_PROB_TRAIN   # first episode uses standard fog
    obs            = env.reset()
    start_time     = time.time()
    current_predicted_technique = None

    for step in range(n_steps):
        # Mild linear decay: 0.20 → 0.05 over all steps
        epsilon = max(0.05, 0.20 - step / n_steps * 0.15)

        token_seq = env.get_padded_sequence()
        with torch.no_grad():
            h_raw, entropy_scalar = encoder.get_h_and_entropy_numpy(token_seq, device)

        h_eff   = np.zeros(H_DIM, dtype=np.float32) if entropy_scalar > ENTROPY_THRESHOLD else h_raw
        ent_eff = 1.0 if entropy_scalar > ENTROPY_THRESHOLD else entropy_scalar

        with torch.no_grad():
            h_t    = torch.FloatTensor(h_raw).unsqueeze(0).to(device)
            logits = encoder.pretrain_head(h_t)
            new_predicted_technique = logits.argmax(dim=-1).item()
            intent_prior = None
            if USE_INTENT_PRIOR:
                h_eff_t      = torch.FloatTensor(h_eff).unsqueeze(0).to(device)
                intent_prior = peap_prior(encoder.pretrain_head(h_eff_t)).squeeze(0)

        obs_full = []
        for o in obs:
            o2 = o.copy(); o2[-H_DIM:] = h_eff; obs_full.append(o2)
        obs_full = _apply_obs_fog(obs_full, episode_fog)

        actions      = agents.select_actions(obs_full, epsilon, entropy_val=ent_eff,
                                             intent_prior=intent_prior)
        global_state = env.get_global_state()

        next_obs, rewards, done, info = env.step(
            actions, h_raw,
            predicted_technique=current_predicted_technique,
        )
        current_predicted_technique = new_predicted_technique

        next_token_seq = env.get_padded_sequence()
        with torch.no_grad():
            next_h_raw, next_entropy = encoder.get_h_and_entropy_numpy(next_token_seq, device)
        next_h_eff = np.zeros(H_DIM, dtype=np.float32) if next_entropy > ENTROPY_THRESHOLD else next_h_raw

        next_obs_full = []
        for o in next_obs:
            o2 = o.copy(); o2[-H_DIM:] = next_h_eff; next_obs_full.append(o2)
        next_obs_full = _apply_obs_fog(next_obs_full, episode_fog)

        fog_buffer.push(
            obs_full, actions, rewards, next_obs_full, done,
            global_state, env.get_global_state(),
            h_eff, next_h_eff, token_seq, next_token_seq,
        )

        if info["trapped"]:
            trapped_count += 1

        if done:
            total_episodes += 1
            obs = env.reset()
            current_predicted_technique = None
            # Sample fog level for the next episode
            if np.random.random() < FOG_MIX_RATIO:
                episode_fog = np.random.uniform(FOG_LOW, FOG_HIGH)
            else:
                episode_fog = STATE_MASKING_PROB_TRAIN
        else:
            obs = next_obs

        if fog_buffer.is_ready(BATCH_SIZE):
            # Pass encoder so entropy is computed from h (not defaulted to 1.0).
            # Encoder grads are zero (requires_grad=False) — optimizer skips them.
            loss = _qmix_update(
                fog_buffer.sample(BATCH_SIZE),
                encoder, agents, mixer, optimizer, device,
            )
            td_losses.append(loss)
            if step % TARGET_SYNC == 0:
                agents.sync_all_targets()

        if (step + 1) % 2000 == 0:
            elapsed  = time.time() - start_time
            avg_loss = np.mean(td_losses[-100:]) if td_losses else 0.0
            dsr      = trapped_count / max(total_episodes, 1)
            print(f"  Step {step+1:5d} | eps={epsilon:.3f} | fog={episode_fog:.2f} | "
                  f"Loss={avg_loss:.4f} | DSR={dsr:.3f} | Time={elapsed:.0f}s")

    # Unfreeze encoder so it can be used / saved normally
    for p in encoder.parameters():
        p.requires_grad = True

    final_dsr = trapped_count / max(total_episodes, 1)
    print(f"\n  Phase 4 complete | DSR={final_dsr:.3f} | Episodes={total_episodes}\n")
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

    env     = HoneypotEnv(attack_strategy=attack_strategy, max_steps=200, local_obs=LOCAL_OBS)
    trapped = 0
    rewards = []

    for _ in range(n_episodes):
        obs       = env.reset()
        h         = np.zeros(H_DIM, dtype=np.float32)
        ep_reward = 0.0
        done      = False
        # Fix 2: track prediction for eval too
        current_predicted_technique = None

        while not done:
            token_seq              = env.get_padded_sequence()
            h, entropy_scalar      = encoder.get_h_and_entropy_numpy(token_seq, device)

            with torch.no_grad():
                h_t    = torch.FloatTensor(h).unsqueeze(0).to(device)
                logits = encoder.pretrain_head(h_t)
                new_predicted_technique = logits.argmax(dim=-1).item()
                intent_prior = peap_prior(logits).squeeze(0) if USE_INTENT_PRIOR else None

            obs_full  = []
            for o in obs:
                o_full = o.copy()
                o_full[-H_DIM:] = h
                obs_full.append(o_full)
            actions = agents.select_actions(obs_full, epsilon=0.0, entropy_val=entropy_scalar,
                                            intent_prior=intent_prior)

            # Fix 2: pass prediction to env
            obs, rews, done, info = env.step(
                actions, h,
                predicted_technique=current_predicted_technique,
            )
            current_predicted_technique = new_predicted_technique

            ep_reward += rews[0]
            if info["trapped"]:
                trapped += 1

        rewards.append(ep_reward)

    return trapped / n_episodes, float(np.mean(rewards))


# ── Main ──────────────────────────────────────────────────────────────────────

# ══════════════════════════════════════════════════════════════════════════════
#  FIX-1 — Imitation-pretrained, variance-reduced policy learning
# ══════════════════════════════════════════════════════════════════════════════

def _compute_astar(strategy, device, n_eps=POLICY_ASTAR_EPISODES):
    """Estimate the profile-optimal deception action a*(c) = argmax_a E[R | c, a]
    and the best/worst information-free fixed actions, from random-action rollouts
    (random actions decorrelate action from state -> unbiased E[R|.,a])."""
    env = HoneypotEnv(attack_strategy=strategy, max_steps=200, local_obs=LOCAL_OBS)
    hz = np.zeros(H_DIM, dtype=np.float32)
    by_a = defaultdict(list); by_pa = defaultdict(list)
    for _ in range(n_eps):
        env.reset(); done = False
        while not done:
            a = [int(np.random.randint(N_ACTIONS)) for _ in range(N_AGENTS)]
            _, _, done, info = env.step(a, hz)
            r = NODE_TO_AGENT.get(info["attacker_node"])
            if r is not None:
                y = info["best_affinity"]; by_a[a[r]].append(y)
                prof = info.get("profile")
                if prof is not None:
                    by_pa[(prof, a[r])].append(y)
    astar = {}
    for p in HYBRID_PROFILE_NAMES:
        vals = {k: float(np.mean(by_pa[(p, k)])) for k in range(N_ACTIONS) if (p, k) in by_pa}
        if vals:
            astar[p] = int(max(vals, key=vals.get))
    mA = {k: float(np.mean(v)) for k, v in by_a.items()}
    best_fixed = int(max(mA, key=mA.get)); worst_fixed = int(min(mA, key=mA.get))
    return astar, best_fixed, worst_fixed, mA


def _collect_policy_imitation_data(encoder, device, strategy, astar, n_eps=POLICY_IL_EPISODES):
    """Roll out the env and gather, per agent, (observation with h -> a*(profile))."""
    env = HoneypotEnv(attack_strategy=strategy, max_steps=200, local_obs=LOCAL_OBS)
    encoder.eval()
    X = [[] for _ in range(N_AGENTS)]; Y = []
    with torch.no_grad():
        for _ in range(n_eps):
            obs = env.reset(); done = False
            prof = getattr(env, "_profile", None)
            if prof is None or prof not in astar:
                continue
            tgt = astar[prof]
            while not done:
                h = encoder.get_h_numpy(env.get_padded_sequence(), device)
                full = [o.copy() for o in obs]
                for o in full:
                    o[-H_DIM:] = h
                for i in range(N_AGENTS):
                    X[i].append(full[i])
                Y.append(tgt)
                obs, _, done, info = env.step([0] * N_AGENTS, h)
    X_t = [torch.tensor(np.array(X[i]), dtype=torch.float32, device=device) for i in range(N_AGENTS)]
    Y_t = torch.tensor(np.array(Y), dtype=torch.long, device=device)
    return X_t, Y_t


def eval_policy_alignment(encoder, agents, device, strategy,
                          n_eps=POLICY_EVAL_EPISODES, seed=12345):
    """In-env anticipatory alignment of the greedy policy head — the guard metric."""
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    encoder.eval(); agents.eval(); agents.set_masking_prob(0.0)
    env = HoneypotEnv(attack_strategy=strategy, max_steps=200, local_obs=LOCAL_OBS)
    al = []
    with torch.no_grad():
        for _ in range(n_eps):
            obs = env.reset(); done = False; ep = []
            while not done:
                h = encoder.get_h_numpy(env.get_padded_sequence(), device)
                full = [o.copy() for o in obs]
                for o in full:
                    o[-H_DIM:] = h
                acts = agents.select_actions_policy(full, entropy_val=None, greedy=True)
                obs, _, done, info = env.step(acts, h)
                r = NODE_TO_AGENT.get(info["attacker_node"])
                if r is not None:
                    ep.append(info["best_affinity"])
            if ep:
                al.append(float(np.mean(ep)))
    return float(np.mean(al)) if al else 0.0


def train_policy_imitation(encoder, agents, device, strategy, astar):
    """Phase 2b.1 — supervised imitation of a*(profile) over the FROZEN encoder.
    State masking stays ON so the policy learns to produce the profile-optimal
    action from h even when telemetry is fogged (fog robustness by construction)."""
    print("=" * 55)
    print(f"  Phase 2b.1: Policy imitation (FIX-1) -- {strategy}")
    print("  a*(profile): " + ", ".join(f"{p}->a{astar[p]}" for p in astar))
    print("=" * 55)
    X_t, Y_t = _collect_policy_imitation_data(encoder, device, strategy, astar)
    n = len(Y_t); cut = int(0.85 * n)
    perm = torch.randperm(n, device=device)
    tr, va = perm[:cut], perm[cut:]
    print(f"  collected {n:,} (obs -> a*) steps x {N_AGENTS} agents")

    opt = optim.Adam(agents.actor_parameters(), lr=POLICY_IL_LR)

    def val_acc():
        agents.eval()
        accs = []
        with torch.no_grad():
            for i in range(N_AGENTS):
                lg = agents.agents[i].online_net.policy_forward(X_t[i][va], entropy=None)
                accs.append((lg.argmax(-1) == Y_t[va]).float().mean().item())
        agents.train(); agents.set_masking_prob(STATE_MASKING_PROB_TRAIN)
        return float(np.mean(accs))

    agents.train(); agents.set_masking_prob(STATE_MASKING_PROB_TRAIN)
    for step in range(POLICY_IL_STEPS):
        idx = tr[torch.randint(0, len(tr), (POLICY_IL_BATCH,), device=device)]
        loss = 0.0
        for i in range(N_AGENTS):
            lg = agents.agents[i].online_net.policy_forward(X_t[i][idx], entropy=None)
            loss = loss + F.cross_entropy(lg, Y_t[idx])
        loss = loss / N_AGENTS
        opt.zero_grad(); loss.backward()
        torch.nn.utils.clip_grad_norm_(agents.actor_parameters(), GRAD_CLIP)
        opt.step()
        if (step + 1) % 1000 == 0:
            print(f"  step {step+1}/{POLICY_IL_STEPS} | CE={loss.item():.4f} | val a*-acc={val_acc():.3f}")
    al = eval_policy_alignment(encoder, agents, device, strategy)
    print(f"  imitation in-env alignment = {al:.3f}\n")
    return al


def train_policy_rl(encoder, agents, device, strategy, baseline_align):
    """Phase 2b.2 — GUARDED PPO fine-tune with a state-value baseline.

    Only the responsible agent (attacker's post-move subnet owner) is scored, so
    each scored step is a single-agent bandit sample: advantage = R - V(f). PPO
    clipping stabilises the update. A best-by-eval checkpoint GUARDS the deployed
    policy so fine-tuning can NEVER regress below the imitation baseline."""
    import copy
    print("=" * 55)
    print(f"  Phase 2b.2: Guarded PPO fine-tune (FIX-1) -- {strategy}")
    print(f"  imitation baseline alignment = {baseline_align:.3f}")
    print("=" * 55)
    encoder.eval()
    actor_opt  = optim.Adam(agents.actor_parameters(),  lr=POLICY_RL_LR)
    critic_opt = optim.Adam(agents.critic_parameters(), lr=1e-3)
    best_align = baseline_align
    best_state = [copy.deepcopy(a.online_net.state_dict()) for a in agents.agents]

    for it in range(POLICY_RL_ITERS):
        # ── on-policy rollout (sampled actions), credit the responsible agent ──
        agents.eval(); agents.set_masking_prob(0.0)
        buf = {i: {"obs": [], "act": [], "ret": [], "logp": []} for i in range(N_AGENTS)}
        env = HoneypotEnv(attack_strategy=strategy, max_steps=200, local_obs=LOCAL_OBS)
        with torch.no_grad():
            for _ in range(POLICY_RL_ROLLOUT_EPS):
                obs = env.reset(); done = False
                while not done:
                    h = encoder.get_h_numpy(env.get_padded_sequence(), device)
                    full = [o.copy() for o in obs]
                    for o in full:
                        o[-H_DIM:] = h
                    acts = []; logps = []
                    for i in range(N_AGENTS):
                        ot = torch.tensor(full[i], dtype=torch.float32, device=device).unsqueeze(0)
                        lg = agents.agents[i].online_net.policy_forward(ot, entropy=None)
                        logp_all = F.log_softmax(lg, -1).squeeze(0)
                        ai = int(torch.multinomial(torch.softmax(lg, -1).squeeze(0), 1).item())
                        acts.append(ai); logps.append(float(logp_all[ai].item()))
                    obs, rewards, done, info = env.step(acts, h)
                    r = NODE_TO_AGENT.get(info["attacker_node"])
                    if r is not None:
                        buf[r]["obs"].append(full[r]); buf[r]["act"].append(acts[r])
                        buf[r]["ret"].append(float(rewards[0])); buf[r]["logp"].append(logps[r])

        # ── PPO update per agent ──
        agents.train(); agents.set_masking_prob(0.0)
        for i in range(N_AGENTS):
            if len(buf[i]["act"]) < 16:
                continue
            O   = torch.tensor(np.array(buf[i]["obs"]), dtype=torch.float32, device=device)
            A_  = torch.tensor(buf[i]["act"],  dtype=torch.long,    device=device)
            Ret = torch.tensor(buf[i]["ret"],  dtype=torch.float32, device=device)
            LPo = torch.tensor(buf[i]["logp"], dtype=torch.float32, device=device)
            net = agents.agents[i].online_net
            for _ep in range(POLICY_RL_EPOCHS):
                perm = torch.randperm(len(A_), device=device)
                for s in range(0, len(A_), POLICY_RL_MINIBATCH):
                    mb = perm[s:s + POLICY_RL_MINIBATCH]
                    lg = net.policy_forward(O[mb], entropy=None)
                    v  = net.value_forward(O[mb], entropy=None)
                    logp = F.log_softmax(lg, -1).gather(1, A_[mb].unsqueeze(1)).squeeze(1)
                    ent  = -(F.softmax(lg, -1) * F.log_softmax(lg, -1)).sum(-1).mean()
                    adv  = (Ret[mb] - v).detach()
                    adv  = (adv - adv.mean()) / (adv.std() + 1e-6)
                    ratio = torch.exp(logp - LPo[mb])
                    s1 = ratio * adv
                    s2 = torch.clamp(ratio, 1 - PPO_CLIP, 1 + PPO_CLIP) * adv
                    pol_loss = -torch.min(s1, s2).mean()
                    val_loss = F.mse_loss(v, Ret[mb])
                    loss = pol_loss + PPO_VAL_COEF * val_loss - PPO_ENT_COEF * ent
                    actor_opt.zero_grad(); critic_opt.zero_grad()
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(agents.actor_parameters(),  GRAD_CLIP)
                    torch.nn.utils.clip_grad_norm_(agents.critic_parameters(), GRAD_CLIP)
                    actor_opt.step(); critic_opt.step()

        # ── guard: keep the best policy by held-out alignment ──
        if (it + 1) % PPO_EVAL_EVERY == 0 or it == POLICY_RL_ITERS - 1:
            al = eval_policy_alignment(encoder, agents, device, strategy)
            flag = ""
            if al > best_align + 1e-4:
                best_align = al
                best_state = [copy.deepcopy(a.online_net.state_dict()) for a in agents.agents]
                flag = "  <- new best (kept)"
            print(f"  PPO iter {it+1}/{POLICY_RL_ITERS} | align={al:.3f} | best={best_align:.3f}{flag}")

    for i, a in enumerate(agents.agents):
        a.online_net.load_state_dict(best_state[i])
    print(f"  PPO complete. Deployed alignment = {best_align:.3f} "
          f"(imitation {baseline_align:.3f}, guard ensures no regression)\n")
    return best_align


def main():
    parser = argparse.ArgumentParser(description="Train TEMARL thesis system")
    parser.add_argument(
        "--only", nargs="+", choices=ATTACK_STRATEGIES, default=None,
        help="Train only these strategies and skip Phase 3 (e.g. --only Mix HiE)",
    )
    parser.add_argument(
        "--seed", type=int, default=SEED,
        help=f"Random seed (default: {SEED})",
    )
    parser.add_argument(
        "--phase4", action="store_true",
        help=(
            "Run fog-aware fine-tuning (Phase 4) on existing Phase 2 models. "
            "Loads results/model_STRATEGY.pt, fine-tunes gate + Q-network with "
            f"fog~Uniform({FOG_LOW:.0%},{FOG_HIGH:.0%}), saves back. "
            f"~{FOG_FINETUNE_STEPS:,} steps per strategy. "
            "Combine with --only to retune select strategies."
        ),
    )
    parser.add_argument(
        "--global-obs", action="store_true",
        help=(
            "Revert to the legacy fully-observable mode (every agent sees the "
            "full 310-dim global state). Default is the Dec-POMDP local-obs "
            "mode where each agent sees only its own subnet and relies on h."
        ),
    )
    args = parser.parse_args()

    # --global-obs reverts to the legacy fully-observable setup (reproduces the
    # pre-rework models). Default is the Dec-POMDP local-observation mode.
    if args.global_obs:
        global LOCAL_OBS, AGENT_STATE_DIM, AGENT_OBS_DIM, AGENT_SIGHTED_IDX
        LOCAL_OBS         = False
        AGENT_STATE_DIM   = STATE_DIM
        AGENT_OBS_DIM     = STATE_DIM + H_DIM
        AGENT_SIGHTED_IDX = None

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n  Device: {device}")
    print(f"  Observability: {'LOCAL per-subnet (Dec-POMDP)' if LOCAL_OBS else 'GLOBAL (legacy)'}"
          f"  |  agent obs dim = {AGENT_OBS_DIM}")
    if torch.cuda.is_available():
        print(f"  GPU: {torch.cuda.get_device_name(0)}")

    set_seed(args.seed)
    print(f"  Seed set to {args.seed} -- deterministic run\n")
    os.makedirs(RESULTS_DIR, exist_ok=True)

    strategies_phase2 = args.only if args.only else ATTACK_STRATEGIES
    run_phase3        = args.only is None and not args.phase4

    # ── Phase 4 standalone mode ───────────────────────────────────────────────
    if args.phase4:
        strats = args.only if args.only else ATTACK_STRATEGIES
        print("\n" + "=" * 60)
        print("  PHASE 4 — Fog-Aware Fine-tuning")
        print(f"  Strategies : {strats}")
        print(f"  Steps      : {FOG_FINETUNE_STEPS:,} per strategy")
        print(f"  Fog range  : [{FOG_LOW:.0%}, {FOG_HIGH:.0%}]  |  Mix: {FOG_MIX_RATIO:.0%} high-fog episodes")
        print("=" * 60)

        for strategy in strats:
            path = os.path.join(RESULTS_DIR, f"model_{strategy}.pt")
            if not os.path.exists(path):
                print(f"  [{strategy}] {path} not found — run Phase 2 first, skipping.")
                continue

            # Load Phase 2 model
            enc_ft    = AttackerIntentEncoder().to(device)
            agents_ft = MultiAgentQMIX(state_masking_prob=0.0, device=device,
                                       state_dim=AGENT_STATE_DIM, obs_dim=AGENT_OBS_DIM,
                                       sighted_idx=AGENT_SIGHTED_IDX,
                                       use_intent_prior=USE_INTENT_PRIOR)
            mixer_ft  = QMIXMixer().to(device)
            ckpt      = torch.load(path, map_location=device, weights_only=True)

            # Handle vocab-size expansion (same as evaluate.py)
            sd_new = enc_ft.state_dict()
            sd_old = ckpt["encoder"]
            for key in ("embedding.weight", "pretrain_head.weight", "pretrain_head.bias"):
                if key in sd_old and sd_old[key].shape != sd_new[key].shape:
                    src = sd_old[key]; dst = sd_new[key].clone()
                    dst[:src.shape[0]] = src; sd_old[key] = dst
            enc_ft.load_state_dict(sd_old, strict=True)
            enc_ft.set_temperature(float(ckpt.get("temperature", 1.0)))
            for i, agent in enumerate(agents_ft.agents):
                agent.online_net.load_state_dict(ckpt["agents"][i])
            print(f"\n  [{strategy}] Loaded Phase 2 model from {path}")

            # Run Phase 4
            train_qmix_fog_finetune(enc_ft, agents_ft, mixer_ft, device, strategy)

            # Quick eval to confirm no regression on standard (no-fog) task
            agents_ft.set_masking_prob(0.0)
            dsr, avg_r = evaluate(enc_ft, agents_ft, mixer_ft, strategy,
                                  n_episodes=100, device=device)
            print(f"  [{strategy}] Post-Phase4 eval (fog=0): DSR={dsr:.3f} | AvgReward={avg_r:.3f}")

            # Overwrite Phase 2 checkpoint with fog-fine-tuned model
            torch.save({
                "encoder": enc_ft.state_dict(),
                "agents":  [a.online_net.state_dict() for a in agents_ft.agents],
                "mixer":   mixer_ft.state_dict(),
            }, path)
            print(f"  [{strategy}] Saved fog-fine-tuned model -> {path}")

        print("\n  Phase 4 complete. Re-run: python evaluate.py --fog --fog-seeds 5\n")
        return

    if args.only:
        print(f"  Mode: retrain only {args.only} (Phase 3 skipped)\n")

    # ── Phase 1: Load COMISET Fine-tuned Encoder (Fix 1) ─────────────────
    # Instead of pretraining on random garbage sequences, we load the
    # encoder that was already fine-tuned on real COMISET attack chains.
    # Run real_data_finetune.py BEFORE this script to produce this file.
    encoder = AttackerIntentEncoder().to(device)

    finetuned_path = os.path.join(RESULTS_DIR, "encoder_finetuned_real.pt")
    pretrain_path  = os.path.join(RESULTS_DIR, "encoder_pretrained.pt")

    if os.path.exists(finetuned_path):
        print(f"  Loading COMISET fine-tuned encoder from: {finetuned_path}")
        encoder.load_state_dict(
            torch.load(finetuned_path, map_location=device, weights_only=True)
        )
        print("  Loaded real-data encoder -- Phase 2 starts with meaningful h\n")
    else:
        print("  WARNING: encoder_finetuned_real.pt not found -- falling back to random pretraining")
        print("  Run real_data_finetune.py first for best results.\n")
        pretrain_transformer(encoder, device)
        torch.save(encoder.state_dict(), pretrain_path)
        print(f"  Saved pre-trained encoder -> {pretrain_path}\n")
        finetuned_path = pretrain_path  # use fallback path below

    # ── Stage 1: adapt the encoder to the simulation, THEN freeze it ─────
    # Done once, before QMIX, so h is stationary during value learning.
    if FREEZE_ENCODER_IN_QMIX:
        pretrain_encoder_on_sim(encoder, device)
        torch.save(encoder.state_dict(),
                   os.path.join(RESULTS_DIR, "encoder_sim_adapted.pt"))
        finetuned_path = os.path.join(RESULTS_DIR, "encoder_sim_adapted.pt")
        print(f"  Saved sim-adapted encoder -> {finetuned_path}\n")

    # ── Phase 2: Train thesis system (QMIX + Transformer) ────────────────
    print("\n" + "=" * 55)
    print("  PHASE 2 -- Thesis System (MARL + Transformer)")
    print("=" * 55)

    all_results = {}

    for strategy in strategies_phase2:
        # Fresh models for each strategy
        agents = MultiAgentQMIX(
            state_masking_prob=STATE_MASKING_PROB_TRAIN,
            device=device,
            state_dim=AGENT_STATE_DIM,
            obs_dim=AGENT_OBS_DIM,
            sighted_idx=AGENT_SIGHTED_IDX,
            use_intent_prior=USE_INTENT_PRIOR,
        )
        mixer  = QMIXMixer().to(device)
        buffer = ReplayBuffer(capacity=BUFFER_SIZE, obs_dim=AGENT_OBS_DIM, device=device)

        # Reload the encoder for each strategy (sim-adapted weights when Stage 1
        # ran, otherwise the COMISET fine-tuned ones). train_qmix will freeze and
        # switch it to eval() when FREEZE_ENCODER_IN_QMIX is set.
        encoder.load_state_dict(
            torch.load(finetuned_path, map_location=device, weights_only=True)
        )
        if not FREEZE_ENCODER_IN_QMIX:
            encoder.train()

        train_qmix(
            encoder, agents, mixer, buffer, device,
            attack_strategy=strategy,
            n_steps=TRAIN_STEPS,
        )

        # Intent calibration (HiC fix): temperature was fit mid-training (60%)
        # so the gate already trained on the calibrated entropy. Persist it for
        # eval via the checkpoint.
        calib_T = float(encoder.temperature)

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
            "encoder":     encoder.state_dict(),
            "agents":      [a.online_net.state_dict() for a in agents.agents],
            "mixer":       mixer.state_dict(),
            "temperature": calib_T,
        }, model_path)
        print(f"  Saved -> {model_path}  (calibration T={calib_T:.2f})\n")

        # ── Phase 2b: FIX-1 policy head (imitation + guarded PPO) ─────────
        # Moves the learner off the divergent TD value function onto a policy
        # trained by imitation of a*(profile) over the frozen encoder, then a
        # guarded PPO fine-tune. Fresh agents so the trunk is learned by
        # imitation, not inherited from the (degenerate) TD-QMIX trunk.
        if RUN_POLICY_HEAD:
            print("\n" + "=" * 55)
            print("  PHASE 2b -- FIX-1 Policy Head (imitation + guarded PPO)")
            print("=" * 55)
            astar, best_fixed, worst_fixed, _mA = _compute_astar(strategy, device)
            policy_agents = MultiAgentQMIX(
                state_masking_prob=STATE_MASKING_PROB_TRAIN, device=device,
                state_dim=AGENT_STATE_DIM, obs_dim=AGENT_OBS_DIM,
                sighted_idx=AGENT_SIGHTED_IDX, use_intent_prior=USE_INTENT_PRIOR,
            )
            encoder.load_state_dict(
                torch.load(finetuned_path, map_location=device, weights_only=True))
            encoder.eval()
            il_align = train_policy_imitation(encoder, policy_agents, device, strategy, astar)
            final_align = il_align
            if RUN_POLICY_RL:
                final_align = train_policy_rl(encoder, policy_agents, device, strategy, il_align)
            policy_path = os.path.join(RESULTS_DIR, f"policy_{strategy}.pt")
            torch.save({
                "encoder":     encoder.state_dict(),
                "agents":      [a.online_net.state_dict() for a in policy_agents.agents],
                "temperature": calib_T,
                "astar":       astar,
                "best_fixed":  best_fixed,
                "worst_fixed": worst_fixed,
                "il_align":    il_align,
                "final_align": final_align,
            }, policy_path)
            print(f"  Saved FIX-1 policy -> {policy_path}  (alignment {final_align:.3f})\n")

    # ── Phase 3: Train MARL without Transformer (fair ablation) ──────────
    if not run_phase3:
        print("\n  Phase 3 skipped (--only mode; existing baseline_notrans_*.pt kept).\n")

    if run_phase3:
        print("\n" + "=" * 55)
        print("  PHASE 3 -- Ablation Baseline (MARL, no Transformer)")
        print("=" * 55)

    for strategy in (ATTACK_STRATEGIES if run_phase3 else []):
        # BUG FIX: agents_base and mixer_base must be fresh instances
        # inside this loop — previous version referenced undefined variables.
        agents_base = MultiAgentQMIX(
            state_masking_prob=STATE_MASKING_PROB_TRAIN,
            device=device,
            state_dim=AGENT_STATE_DIM,
            obs_dim=AGENT_OBS_DIM,
            sighted_idx=AGENT_SIGHTED_IDX,
            use_intent_prior=USE_INTENT_PRIOR,
        )
        mixer_base  = QMIXMixer().to(device)
        buffer_base = ReplayBuffer(capacity=BUFFER_SIZE, obs_dim=AGENT_OBS_DIM, device=device)

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
        print(f"  Saved baseline -> {baseline_path}\n")

    # ── Final summary ─────────────────────────────────────────────────────
    print("\n" + "=" * 55)
    print("  FINAL SUMMARY")
    print("=" * 55)
    print(f"  {'Strategy':<8} {'DSR':>8} {'AvgReward':>12}")
    print(f"  {'-'*30}")
    for strat, res in all_results.items():
        print(f"  {strat:<8} {res['dsr']:>8.3f} {res['avg_reward']:>12.3f}")

    with open(os.path.join(RESULTS_DIR, "training_summary.json"), "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\n  All results saved -> {RESULTS_DIR}")


if __name__ == "__main__":
    main()
