# evaluate.py
"""
File 8 of 8 — Evaluation & Results
======================================
Evaluates thesis system (Gated Fusion QMIX + Transformer) against baselines.

Metrics pulled directly from environment accessors — no manual counters:
  env.get_engagement_length()  → dwell time with stall bonuses
  env.get_interaction_depth()  → unique MITRE techniques attempted
  alignment                    → mean technique-action alignment [0,1]
  DSR                          → Deception Success Rate (secondary)
  avg_reward                   → mean cumulative episode reward

Fog of War mode (--fog):
  Masks a configurable fraction of the 310-dim telemetry at each step,
  forcing agents to rely on the Transformer intent vector h.
  Used to empirically prove Transformer value under partial observability.

Run AFTER train_thesis.py completes all 3 phases.
"""

import torch
import torch.nn as nn
import numpy as np
import json
import os
import argparse
from collections import defaultdict

try:
    from scipy import stats as _scipy_stats
    _SCIPY = True
except ImportError:
    _SCIPY = False

from mitre_techniques import NUM_TECHNIQUES
from transformer_encoder import AttackerIntentEncoder
from qmix_mixer import QMIXMixer, H_DIM
from simulation_env import (
    HoneypotEnv, N_AGENTS, N_ACTIONS, STATE_DIM, LOCAL_STATE_DIM, ALIGNMENT_MATRIX,
    LOCAL_ATTACKER_PRESENT_IDX, NODE_TO_AGENT
)
from qmix_agent import MultiAgentQMIX, OBS_DIM

RESULTS_DIR   = r"results"
N_EVAL_EPS    = 200
# ── Model vs environment are now DECOUPLED ────────────────────────────────────
# ONE model is trained on the Hybrid mixture (hidden profile resampled every
# episode). It is then evaluated against the mixture AND against each forced
# profile, so the per-campaign breakdown is an honest generalisation test of a
# single model rather than four separately-memorised specialists.
MODEL_STRATEGY = "Hybrid"          # which checkpoint to load
ATTACK_STRATS  = ["Hybrid", "P_Exploit", "P_Recon", "P_Lateral", "P_Exfil"]
DEVICE        = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ── Observability mode (must match how the models were trained) ───────────────
# LOCAL_OBS=True  → Dec-POMDP: each agent sees only its own subnet (52-dim) ‖ h.
# LOCAL_OBS=False → legacy fully-observable models (310-dim global ‖ h).
# STATE_DIM (310) is always the global state; H_DIM (64) always the trailing
# slot of any observation, so h is written at obs[-H_DIM:] in both modes.
# Toggle at runtime with --global-obs to evaluate pre-rework checkpoints.
LOCAL_OBS       = True
AGENT_STATE_DIM = LOCAL_STATE_DIM if LOCAL_OBS else STATE_DIM
AGENT_OBS_DIM   = AGENT_STATE_DIM + H_DIM
AGENT_SIGHTED_IDX = LOCAL_ATTACKER_PRESENT_IDX if LOCAL_OBS else None

# RAIF Stage A — PEAP intent prior. Imported from train_thesis so training and
# evaluation use the identical u = A^T p definition (single source of truth).
from train_thesis import USE_INTENT_PRIOR, peap_prior


# ── Model loaders ─────────────────────────────────────────────────────────────

def _load_agents_tolerant(agents, agent_sds, tag=""):
    """
    Load agent weights tolerantly so PRE-RAIF (Retrain #4) checkpoints stay
    evaluable under the Stage A code. A missing `lambda_p` simply keeps its 0.0
    initialisation, which makes the PEAP prior contribute exactly nothing — i.e.
    the loaded model reproduces #4 behaviour bit-for-bit. Any OTHER mismatch is
    reported loudly, so this never silently hides a real shape/name bug.
    """
    BENIGN = {"lambda_p"}
    saw_pre_raif = False
    for i, agent in enumerate(agents.agents):
        missing, unexpected = agent.online_net.load_state_dict(agent_sds[i], strict=False)
        hard_missing = [k for k in missing if k not in BENIGN]
        if hard_missing or unexpected:
            raise RuntimeError(
                f"Incompatible checkpoint{tag} (agent {i}): "
                f"missing={hard_missing} unexpected={list(unexpected)}")
        if any(k in BENIGN for k in missing):
            saw_pre_raif = True
    if saw_pre_raif:
        print(f"    NOTE{tag}: pre-RAIF checkpoint (no lambda_p) — PEAP prior "
              f"inactive, reproducing Retrain #4 behaviour exactly.")


def _expand_encoder(old, new_sd):
    for key in ("embedding.weight", "pretrain_head.weight", "pretrain_head.bias"):
        if key in old and old[key].shape != new_sd[key].shape:
            src = old[key]; dst = new_sd[key].clone()
            dst[:src.shape[0]] = src; old[key] = dst
    return old

def load_thesis_model(strategy, device):
    path = os.path.join(RESULTS_DIR, f"model_{strategy}.pt")
    assert os.path.exists(path), f"Not found: {path}"
    encoder = AttackerIntentEncoder().to(device)
    agents  = MultiAgentQMIX(state_masking_prob=0.0, device=device,
                             state_dim=AGENT_STATE_DIM, obs_dim=AGENT_OBS_DIM,
                             sighted_idx=AGENT_SIGHTED_IDX,
                             use_intent_prior=USE_INTENT_PRIOR)
    mixer   = QMIXMixer().to(device)
    ckpt    = torch.load(path, map_location=device, weights_only=True)
    encoder.load_state_dict(
        _expand_encoder(ckpt["encoder"], encoder.state_dict()), strict=True)
    encoder.set_temperature(float(ckpt.get("temperature", 1.0)))   # intent calibration (HiC fix)
    _load_agents_tolerant(agents, ckpt["agents"], tag=f" [thesis/{strategy}]")
    encoder.eval(); agents.eval(); agents.set_masking_prob(0.0); mixer.eval()
    return encoder, agents, mixer

def load_baseline_model(strategy, device):
    path = os.path.join(RESULTS_DIR, f"baseline_notrans_{strategy}.pt")
    assert os.path.exists(path), f"Not found: {path}"
    agents = MultiAgentQMIX(state_masking_prob=0.0, device=device,
                            state_dim=AGENT_STATE_DIM, obs_dim=AGENT_OBS_DIM,
                            sighted_idx=AGENT_SIGHTED_IDX,
                            use_intent_prior=USE_INTENT_PRIOR)
    mixer  = QMIXMixer().to(device)
    ckpt   = torch.load(path, map_location=device, weights_only=True)
    _load_agents_tolerant(agents, ckpt["agents"], tag=f" [notrans/{strategy}]")
    agents.eval(); agents.set_masking_prob(0.0); mixer.eval()
    return agents, mixer


_MODEL_CACHE = {}

def get_models(device=None):
    """
    Load the SINGLE Hybrid-trained model + its NoTrans ablation (cached).

    Evaluation loops iterate over ENVIRONMENTS (the mixture and each forced
    profile) but always use this one model, so a per-profile breakdown measures
    generalisation of one intent-inferring policy rather than four specialists.
    """
    device = device or DEVICE
    if "thesis" not in _MODEL_CACHE:
        _MODEL_CACHE["thesis"]  = load_thesis_model(MODEL_STRATEGY, device)
        _MODEL_CACHE["notrans"] = load_baseline_model(MODEL_STRATEGY, device)
    return _MODEL_CACHE["thesis"], _MODEL_CACHE["notrans"]


def load_policy_model(strategy, device):
    """FIX-1: load the imitation+PPO policy head (policy_STRATEGY.pt). Returns the
    MultiAgentQMIX whose policy heads are queried greedily. Returns None if the
    checkpoint does not exist (so evaluation degrades gracefully)."""
    path = os.path.join(RESULTS_DIR, f"policy_{strategy}.pt")
    if not os.path.exists(path):
        return None
    agents = MultiAgentQMIX(state_masking_prob=0.0, device=device,
                            state_dim=AGENT_STATE_DIM, obs_dim=AGENT_OBS_DIM,
                            sighted_idx=AGENT_SIGHTED_IDX,
                            use_intent_prior=USE_INTENT_PRIOR)
    ckpt = torch.load(path, map_location=device, weights_only=True)
    _load_agents_tolerant(agents, ckpt["agents"], tag=f" [policy/{strategy}]")
    agents.eval(); agents.set_masking_prob(0.0)
    return agents


def get_policy_model(device=None):
    """Cached FIX-1 policy (shares the Hybrid checkpoint's frozen encoder for h)."""
    device = device or DEVICE
    if "policy" not in _MODEL_CACHE:
        _MODEL_CACHE["policy"] = load_policy_model(MODEL_STRATEGY, device)
    return _MODEL_CACHE["policy"]


# ── Step-counter oracle baseline ──────────────────────────────────────────────

_COUNTER_TABLE = None

def _fit_counter_oracle(n_eps=400):
    """
    Fit the STEP-COUNTER ORACLE: a defender with a perfect clock but NO intent
    model. For each step index t it plays argmax_a E[A[tau,a] | t], with the
    technique distribution estimated from the Hybrid mixture.

    This is the null model that DEMOLISHED the legacy environment (a bare counter
    beat the Transformer on all four legacy strategies). Reporting it as an
    explicit baseline turns the project's biggest prior vulnerability into
    evidence: any advantage over this row cannot be explained by timing alone.
    """
    global _COUNTER_TABLE
    if _COUNTER_TABLE is not None:
        return _COUNTER_TABLE
    from collections import defaultdict
    counts = defaultdict(lambda: np.zeros(NUM_TECHNIQUES))
    hz = np.zeros(H_DIM, dtype=np.float32)
    env = HoneypotEnv(attack_strategy=MODEL_STRATEGY, max_steps=200, local_obs=LOCAL_OBS)
    for _ in range(n_eps):
        env.reset(); done = False; t = 0
        while not done:
            _, _, done, info = env.step([0] * N_AGENTS, hz)
            tau = info["technique_id"]
            if 0 <= tau < NUM_TECHNIQUES:
                counts[min(t, 15)][tau] += 1
            t += 1
    A = ALIGNMENT_MATRIX[:NUM_TECHNIQUES]
    table = {}
    for t, c in counts.items():
        if c.sum() > 0:
            table[t] = int(np.argmax((c / c.sum()) @ A))
    # fall back to the globally best fixed action for unseen step indices
    tot = sum(counts.values()) if counts else np.ones(NUM_TECHNIQUES)
    table["default"] = int(np.argmax((tot / tot.sum()) @ A))
    _COUNTER_TABLE = table
    return table


def counter_oracle_action_fn(obs, h, entropy_scalar=None, global_state=None, step_idx=None):
    """Perfect-clock, zero-intent defender (see _fit_counter_oracle)."""
    tbl = _fit_counter_oracle()
    a = tbl.get(min(step_idx, 15) if step_idx is not None else -1, tbl["default"])
    return [a] * N_AGENTS


# ── Fog of War telemetry masking ──────────────────────────────────────────────

def apply_fog_of_war(observations: list, fog_prob: float) -> list:
    """
    Partially mask the 310-dim telemetry portion of each agent's observation.
    The 64-dim intent vector h (positions 310:374) is NEVER masked.

    Args:
        observations: list of np.ndarray shape (374,)
        fog_prob:     fraction of telemetry features to zero (0.0 = no fog)

    Returns:
        list of masked observations, same shape

    Mathematical effect:
        Let s = obs[:310], h = obs[310:].
        Each feature s_i is zeroed independently with probability fog_prob.
        When fog_prob → 1.0, agents receive only h as useful signal.
        This simulates POMDP / partial observability conditions
        matching real-world honeypot deployments where telemetry
        is incomplete, delayed, or spoofed by the attacker.
    """
    if fog_prob <= 0.0:
        return observations
    masked = []
    for obs in observations:
        obs_masked = obs.copy()
        # Telemetry portion = everything except the trailing H_DIM intent vector.
        # Mode-agnostic: 310 in global mode, LOCAL_STATE_DIM in local mode.
        sdim = obs_masked.shape[0] - H_DIM
        # Generate per-feature mask: 1.0 = keep, 0.0 = zero
        mask = np.random.binomial(1, 1.0 - fog_prob,
                                  size=sdim).astype(np.float32)
        obs_masked[:sdim] *= mask   # zero out fog_prob fraction of telemetry
        # h (trailing H_DIM positions) is never touched
        masked.append(obs_masked)
    return masked


# ── Action functions ──────────────────────────────────────────────────────────

def static_action_fn(obs, h, entropy_scalar=None, global_state=None, step_idx=None):
    return [0] * N_AGENTS

def random_action_fn(obs, h, entropy_scalar=None, global_state=None, step_idx=None):
    return [np.random.randint(0, N_ACTIONS) for _ in range(N_AGENTS)]

def critical_action_fn(obs, h, entropy_scalar=None, global_state=None, step_idx=None):
    """Rule-based expert: action chosen by observed compromise phase.
    Mirrors Hawkeyes-style critical-node heuristic adapted to behavioral actions.
    Phase 0 (0-2 nodes): early recon      -> credential trap (3)
    Phase 1 (3-5 nodes): lateral movement -> fake vulnerability (2)
    Phase 2 (6+  nodes): exfiltration     -> data exfil bait (4)

    This is a privileged centralized baseline: it reads the global compromise
    vector (M_com = first 10 dims of the global state). In local-obs mode the
    per-agent observation no longer contains it, so the true global state is
    threaded in via `global_state` (from env.get_global_state()).
    """
    if global_state is not None:
        m_com = global_state[0:10]
    else:
        # Global-obs fallback: M_com is the first 10 dims of the agent obs.
        m_com = obs[0][0:10]
    n_compromised = int(round(np.asarray(m_com).sum()))
    if n_compromised <= 2:
        action = 3
    elif n_compromised <= 5:
        action = 2
    else:
        action = 4
    return [action] * N_AGENTS

def make_thesis_action_fn(agents, encoder, device, fog_prob=0.0, entropy_threshold=1.01):
    """
    entropy_threshold: if entropy_scalar > threshold, zero out h before calling agents.
    This is a hard entropy masking layer on top of the soft entropy-aware gate.
    Default 1.01 = disabled (entropy is always in [0,1] so 1.01 never triggers).
    Principled choice: when the Transformer is maximally uncertain, fall back to
    pure telemetry MARL (same as NoTrans), avoiding noisy h polluting Q-values.
    """
    def fn(obs, h, entropy_scalar=None, global_state=None, step_idx=None):
        h_used = h
        ent_used = entropy_scalar
        if entropy_scalar is not None and entropy_scalar > entropy_threshold:
            h_used = np.zeros(H_DIM, dtype=np.float32)
            ent_used = 1.0
        full = []
        for o in obs:
            o2 = o.copy(); o2[-H_DIM:] = h_used; full.append(o2)
        full = apply_fog_of_war(full, fog_prob)
        # PEAP prior from the EFFECTIVE h (matches training-time computation)
        intent_prior = None
        if USE_INTENT_PRIOR:
            with torch.no_grad():
                h_t = torch.FloatTensor(h_used).unsqueeze(0).to(device)
                intent_prior = peap_prior(encoder.pretrain_head(h_t)).squeeze(0)
        return agents.select_actions(full, epsilon=0.0, entropy_val=ent_used,
                                     intent_prior=intent_prior)
    return fn

def make_notrans_action_fn(agents_base, fog_prob=0.0):
    def fn(obs, h, entropy_scalar=None, global_state=None, step_idx=None):
        hz = np.zeros(H_DIM, dtype=np.float32)
        full = []
        for o in obs:
            o2 = o.copy(); o2[-H_DIM:] = hz; full.append(o2)
        full = apply_fog_of_war(full, fog_prob)
        # NoTrans: h=zeros -> uniform probs -> max entropy (1.0)
        return agents_base.select_actions(full, epsilon=0.0, entropy_val=1.0)
    return fn

def make_policy_action_fn(agents, fog_prob=0.0):
    """FIX-1: greedy policy head pi_theta(a|f). Uses the real intent vector h
    (never zeroed); under fog the telemetry is masked and the gate leans on h,
    so this policy is fog-robust by construction."""
    def fn(obs, h, entropy_scalar=None, global_state=None, step_idx=None):
        full = []
        for o in obs:
            o2 = o.copy(); o2[-H_DIM:] = h; full.append(o2)
        full = apply_fog_of_war(full, fog_prob)
        return agents.select_actions_policy(full, entropy_val=None, greedy=True)
    return fn


# ── Baseline 3: Single-Agent PPO (untrained) ──────────────────────────────────

class SingleAgentPPO(nn.Module):
    def __init__(self, obs_dim=None, n_agents=N_AGENTS, n_actions=N_ACTIONS):
        super().__init__()
        # Resolve at call time so a --global-obs override is honored.
        if obs_dim is None:
            obs_dim = AGENT_OBS_DIM
        self.n_agents = n_agents; self.n_actions = n_actions
        self.net = nn.Sequential(
            nn.Linear(obs_dim, 256), nn.ReLU(),
            nn.Linear(256, 128),     nn.ReLU(),
            nn.Linear(128, n_agents * n_actions),
        )
    def forward(self, obs):
        return self.net(obs).view(-1, self.n_agents, self.n_actions)
    def select_actions(self, obs_np):
        with torch.no_grad():
            obs_t  = torch.FloatTensor(obs_np).unsqueeze(0).to(
                next(self.parameters()).device)
            logits = self.forward(obs_t)
        return logits.argmax(dim=-1).squeeze(0).tolist()

def make_ppo_action_fn(ppo):
    return (lambda obs, h, entropy_scalar=None, global_state=None, step_idx=None:
            ppo.select_actions(obs[0]))

def train_ppo_baseline(strategy, device, n_episodes=800):
    """Train SingleAgentPPO via REINFORCE on the given attack strategy."""
    ppo = SingleAgentPPO().to(device)
    optimizer = torch.optim.Adam(ppo.parameters(), lr=3e-4)
    env = HoneypotEnv(attack_strategy=strategy, max_steps=200, local_obs=LOCAL_OBS)
    GAMMA = 0.99
    h_zeros = np.zeros(H_DIM, dtype=np.float32)
    print(f"    Training PPO on {strategy} ({n_episodes} episodes) ...")
    for ep in range(n_episodes):
        obs = env.reset()
        log_probs = []
        rewards_buf = []
        done = False
        while not done:
            full_obs = obs[0].copy()
            full_obs[-H_DIM:] = h_zeros
            obs_t  = torch.FloatTensor(full_obs).unsqueeze(0).to(device)
            logits = ppo(obs_t).squeeze(0)           # (N_AGENTS, N_ACTIONS)
            dist   = torch.distributions.Categorical(logits=logits)  # numerically stable
            actions_t = dist.sample()                # (N_AGENTS,)
            log_prob  = dist.log_prob(actions_t).sum()
            obs, step_rewards, done, _ = env.step(actions_t.cpu().tolist(), h_zeros)
            log_probs.append(log_prob)
            rewards_buf.append(float(step_rewards[0]))
        G = 0.0
        returns = []
        for r in reversed(rewards_buf):
            G = r + GAMMA * G
            returns.insert(0, G)
        returns_t = torch.FloatTensor(returns).to(device)
        if returns_t.numel() > 1:
            returns_t = (returns_t - returns_t.mean()) / (returns_t.std() + 1e-8)
        loss = -(torch.stack(log_probs) * returns_t).mean()
        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(ppo.parameters(), 1.0)
        optimizer.step()
        if (ep + 1) % 200 == 0:
            print(f"    [{strategy}] PPO ep {ep+1}/{n_episodes} loss={loss.item():.4f}")
    return ppo

def load_trained_ppo(strategy, device):
    """Load trained PPO checkpoint if it exists and matches the current
    observability mode, else return an untrained model. A stale checkpoint
    (saved under a different obs_dim, e.g. before the local-obs rework) is
    skipped with a warning rather than crashing the whole evaluation run."""
    path = os.path.join(RESULTS_DIR, f"ppo_{strategy}.pt")
    ppo  = SingleAgentPPO().to(device)
    if os.path.exists(path):
        ckpt = torch.load(path, map_location=device, weights_only=True)
        ckpt_obs_dim = ckpt["net.0.weight"].shape[1]
        if ckpt_obs_dim != AGENT_OBS_DIM:
            print(f"    WARNING: {path} was saved with obs_dim={ckpt_obs_dim}, "
                  f"current mode expects {AGENT_OBS_DIM}. Skipping stale checkpoint "
                  f"-- run --train-ppo to retrain. Using untrained.")
        else:
            ppo.load_state_dict(ckpt)
            print(f"    Loaded trained PPO: {path}")
    else:
        print(f"    PPO not trained ({path}). Run --train-ppo first. Using untrained.")
    ppo.eval()
    return ppo


# ── Unified episode runner ─────────────────────────────────────────────────────

def run_episode(env, action_fn, encoder=None):
    """
    Run one evaluation episode.

    Reward fix (Problem 2):
        ep_reward is initialised to 0.0 and accumulated with += at every step.
        The final value is returned in the dict under 'ep_reward'.
        evaluate_method() stores this per episode and averages across N episodes.
        No default dict key or get() call can zero it out.

    Metrics read from env accessors — no manual counters.
    """
    obs        = env.reset()
    h          = np.zeros(H_DIM, dtype=np.float32)
    done       = False
    alignments = []
    trapped    = False
    ep_reward  = 0.0   # ← initialised here, accumulated below

    while not done:
        entropy_scalar = None
        if encoder is not None:
            h, entropy_scalar = encoder.get_h_and_entropy_numpy(env.get_padded_sequence(), DEVICE)
        actions = action_fn(obs, h, entropy_scalar, env.get_global_state(),
                            env.step_count)

        obs, rewards, done, info = env.step(actions, h)
        alignments.append(info["best_affinity"])

        # ── Reward accumulation (Problem 2 fix) ───────────────────────────
        # rewards is a list of length N_AGENTS (shared cooperative reward).
        # We take rewards[0] — all agents receive the same value.
        ep_reward += rewards[0]   # ← accumulated every step, never reset here

        if info["trapped"]:
            trapped = True

    return {
        "alignment":         float(np.mean(alignments)) if alignments else 0.0,
        "trapped":           1.0 if trapped else 0.0,
        "ep_reward":         ep_reward,               # ← returned in dict
        "engagement_length": env.get_engagement_length(),
        "interaction_depth": float(env.get_interaction_depth()),
    }


def evaluate_method(method_name, action_fn, strategy,
                    encoder=None, n=N_EVAL_EPS):
    env     = HoneypotEnv(attack_strategy=strategy, max_steps=200, local_obs=LOCAL_OBS)
    results = defaultdict(list)
    for _ in range(n):
        r = run_episode(env, action_fn, encoder)
        for k, v in r.items():
            results[k].append(v)          # ep_reward is now in r, so it lands here
    return {
        "method":             method_name,
        "strategy":           strategy,
        "dsr":                float(np.mean(results["trapped"])),
        "dsr_std":            float(np.std(results["trapped"])),
        "engagement_length":  float(np.mean(results["engagement_length"])),
        "engagement_std":     float(np.std(results["engagement_length"])),
        "interaction_depth":  float(np.mean(results["interaction_depth"])),
        "depth_std":          float(np.std(results["interaction_depth"])),
        "avg_alignment":      float(np.mean(results["alignment"])),
        "alignment_std":      float(np.std(results["alignment"])),
        "avg_reward":         float(np.mean(results["ep_reward"])),  # ← now populated
        "reward_std":         float(np.std(results["ep_reward"])),
        "n_episodes":         n,
    }


# ── Fog of War evaluation ─────────────────────────────────────────────────────

def run_fog_of_war_analysis(fog_levels=(0.0, 0.25, 0.5, 0.75, 0.9),
                            entropy_th=1.01,
                            n_seeds=1):
    """
    Empirical proof of Transformer value under partial observability.

    Five anchor points: 0%, 25%, 50%, 75%, 90%.
    n_fog_eps=200 matches the main evaluation for statistical consistency.

    Key design choice: entropy masking is DISABLED during fog > 0.
    Rationale: when telemetry is already degraded, even a noisy h is more
    informative than zeros. Entropy masking is appropriate at fog=0 (full
    telemetry available as fallback), but counterproductive at high fog
    where h is the only remaining signal. At fog=0 the user-specified
    entropy_th is applied; at fog>0 masking is disabled (threshold=1.01).

    Fog design: masking zeros the 310-dim telemetry (dim 0:310) only.
    The 64-dim intent vector h (dim 310:374) is NEVER masked. This isolates
    the Transformer's contribution under degraded state signal specifically.

    Statistical mode (n_seeds > 1): each seed produces one alignment sample
    (mean over n_fog_eps episodes). CI and paired t-test are computed across
    the n_seeds samples per (strategy, fog_level) pair.

    Ran architectural note: Ran (random attacker) may show alignment gains
    under fog despite h being uninformative for random sequences. This
    reflects the gated architecture's robustness to partial observations —
    the gate was trained with STATE_MASKING_PROB=0.3, learning to suppress
    noise and handle missing features. This is a distinct contribution from
    Transformer intent modeling and should be reported as such.
    """
    print("\n" + "=" * 110)
    print("  FOG OF WAR ANALYSIS — Transformer Value Under Partial Observability")
    print("=" * 110)
    print(f"  Anchor points: 0% | 25% | 50% | 75% | 90%  "
          f"(200 episodes × {n_seeds} seed{'s' if n_seeds > 1 else ''})")
    print("  Entropy masking: active at fog=0%, DISABLED at fog>0% (h beats zeros under fog)")
    print("  Fog scope: telemetry dim 0:310 only — h (dim 310:374) is NEVER masked.")
    if n_seeds > 1:
        print(f"  Statistics: 95% CI + paired t-test across {n_seeds} seeds per condition.")
    print()

    n_fog_eps = 200
    all_strategy_results = {}

    if n_seeds > 1:
        hdr = (f"  {'Fog%':>6}  {'T-Align':>9} {'NT-Align':>9} {'AlignGap':>9}"
               f" {'±95%CI':>7} {'p-val':>7} {'Sig':>4}"
               f"  {'EngGap':>7}  {'CDSGap':>8} {'CSig':>4}")
    else:
        hdr = (f"  {'Fog%':>6}  {'T-Align':>9} {'NT-Align':>9} {'AlignGap':>9}"
               f"  {'T-Engage':>9} {'NT-Engage':>9} {'EngGap':>7}"
               f"  {'RateGap':>9}")
    sep = "  " + "-" * (len(hdr) - 2)

    for strategy in ATTACK_STRATS:
        print(f"  Strategy: {strategy}  (ExpRate = depth/engage; RateGap<0 = Thesis confines better)")
        print(hdr)
        print(sep)

        (encoder, agents, _), (agents_base, _) = get_models(DEVICE)

        thesis_aligns    = []
        notrans_aligns   = []
        align_gaps       = []
        thesis_exprates  = []
        notrans_exprates = []
        thesis_engages   = []
        notrans_engages  = []
        rate_gaps        = []
        align_gap_cis    = []
        align_gap_pvals  = []
        align_gap_sigs   = []
        norm_engage      = None
        norm_depth       = None
        thesis_cdss      = []
        notrans_cdss     = []
        cds_gaps         = []
        cds_gap_cis      = []
        cds_gap_pvals    = []
        cds_gap_sigs     = []

        for fog in fog_levels:
            # Disable entropy masking under fog so h is never zeroed when
            # telemetry is already degraded — noisy h > zeros.
            eff_eth   = entropy_th if fog == 0.0 else 1.01
            thesis_fn = make_thesis_action_fn(agents, encoder, DEVICE,
                                              fog_prob=fog,
                                              entropy_threshold=eff_eth)
            notrans_fn = make_notrans_action_fn(agents_base, fog_prob=fog)

            if n_seeds > 1:
                ta_seeds, na_seeds = [], []
                te_seeds, ne_seeds = [], []
                td_seeds, nd_seeds = [], []
                for seed_i in range(n_seeds):
                    np.random.seed(seed_i * 13 + 1)
                    r_t = evaluate_method("Thesis",  thesis_fn,  strategy,
                                          encoder, n=n_fog_eps)
                    np.random.seed(seed_i * 13 + 500)
                    r_n = evaluate_method("NoTrans", notrans_fn, strategy,
                                          n=n_fog_eps)
                    ta_seeds.append(r_t["avg_alignment"])
                    na_seeds.append(r_n["avg_alignment"])
                    te_seeds.append(r_t["engagement_length"])
                    ne_seeds.append(r_n["engagement_length"])
                    td_seeds.append(r_t["interaction_depth"])
                    nd_seeds.append(r_n["interaction_depth"])

                ta = float(np.mean(ta_seeds))
                na = float(np.mean(na_seeds))
                te = float(np.mean(te_seeds))
                ne = float(np.mean(ne_seeds))
                td = float(np.mean(td_seeds))
                nd = float(np.mean(nd_seeds))

                t_stat, p_val, cih_lift, _ = _paired_ttest(ta_seeds, na_seeds)
                sig = ("***" if p_val < 0.001 else
                       "**"  if p_val < 0.01  else
                       "*"   if p_val < 0.05  else "ns")
            else:
                r_t = evaluate_method("Thesis",  thesis_fn,  strategy,
                                      encoder, n=n_fog_eps)
                r_n = evaluate_method("NoTrans", notrans_fn, strategy,
                                      n=n_fog_eps)
                ta = r_t["avg_alignment"];     na = r_n["avg_alignment"]
                te = r_t["engagement_length"]; ne = r_n["engagement_length"]
                td = r_t["interaction_depth"]; nd = r_n["interaction_depth"]
                cih_lift = 0.0; p_val = 1.0; sig = ""

            align_gap_cis.append(round(cih_lift, 4))
            align_gap_pvals.append(round(p_val, 4))
            align_gap_sigs.append(sig)

            t_er = td / te if te > 0 else 0.0
            n_er = nd / ne if ne > 0 else 0.0

            align_gap = ta - na
            eng_gap   = te - ne
            rate_gap  = t_er - n_er   # negative = Thesis confines better

            thesis_aligns.append(ta);     notrans_aligns.append(na)
            align_gaps.append(align_gap); thesis_engages.append(te)
            notrans_engages.append(ne);   thesis_exprates.append(t_er)
            notrans_exprates.append(n_er); rate_gaps.append(rate_gap)

            # CDS under fog — fixed normalizers from no-fog baseline
            if fog == 0.0:
                norm_engage = max(te, ne, 1.0)
                norm_depth  = max(td, nd, 1.0)
            NE = norm_engage if norm_engage is not None else max(te, ne, 1.0)
            ND = norm_depth  if norm_depth  is not None else max(td, nd, 1.0)
            t_cds   = 0.5 * ta + 0.3 * (te / NE) + 0.2 * (td / ND)
            n_cds   = 0.5 * na + 0.3 * (ne / NE) + 0.2 * (nd / ND)
            cds_gap = t_cds - n_cds
            if n_seeds > 1:
                tc_per = [0.5*ta_s + 0.3*(te_s/NE) + 0.2*(td_s/ND)
                          for ta_s, te_s, td_s in zip(ta_seeds, te_seeds, td_seeds)]
                nc_per = [0.5*na_s + 0.3*(ne_s/NE) + 0.2*(nd_s/ND)
                          for na_s, ne_s, nd_s in zip(na_seeds, ne_seeds, nd_seeds)]
                _, cds_p, cds_ci, _ = _paired_ttest(tc_per, nc_per)
                cds_sig = ("***" if cds_p < 0.001 else
                           "**"  if cds_p < 0.01  else
                           "*"   if cds_p < 0.05  else "ns")
                cds_gap_cis.append(round(cds_ci, 4))
                cds_gap_pvals.append(round(cds_p, 4))
                cds_gap_sigs.append(cds_sig)
            else:
                cds_sig = ""
                cds_gap_cis.append(0.0)
                cds_gap_pvals.append(1.0)
                cds_gap_sigs.append("")
            thesis_cdss.append(round(t_cds, 4))
            notrans_cdss.append(round(n_cds, 4))
            cds_gaps.append(round(cds_gap, 4))

            align_trend = "↑" if (len(align_gaps) > 1 and align_gap > align_gaps[-2]) else ""

            if n_seeds > 1:
                print(f"  {fog*100:>5.0f}%  {ta:>9.4f} {na:>9.4f} {align_gap:>+9.4f}"
                      f" {cih_lift:>7.4f} {p_val:>7.4f} {sig:>4}"
                      f"  {eng_gap:>+7.2f}  {cds_gap:>+8.4f} {cds_sig:>4}")
            else:
                print(f"  {fog*100:>5.0f}%  {ta:>9.3f} {na:>9.3f} {align_gap:>+9.3f}"
                      f"  {te:>9.2f} {ne:>9.2f} {eng_gap:>+7.2f}"
                      f"  {rate_gap:>+9.4f}  {align_trend}")

        max_align_idx = int(np.argmax(align_gaps))
        best_rate_idx = int(np.argmin(rate_gaps))
        n_pos_align   = sum(1 for g in align_gaps if g > 0)
        n_sig         = sum(1 for s in align_gap_sigs if s not in ("", "ns"))
        trend = ("monotone ↑" if all(align_gaps[i] <= align_gaps[i+1]
                                     for i in range(len(align_gaps)-1))
                 else "peaks at fog=" + f"{fog_levels[max_align_idx]*100:.0f}%")
        print(f"  Peak align gap : {align_gaps[max_align_idx]:+.4f} at fog={fog_levels[max_align_idx]*100:.0f}%"
              f"  | trend: {trend}  | positive at {n_pos_align}/{len(fog_levels)} levels"
              + (f"  | sig at {n_sig}/{len(fog_levels)} levels" if n_seeds > 1 else ""))
        print(f"  Best rate gap  : {rate_gaps[best_rate_idx]:+.4f} at fog={fog_levels[best_rate_idx]*100:.0f}%"
              f"  ({'Thesis confines better' if rate_gaps[best_rate_idx] < 0 else 'NoTrans confines better'})")
        if n_seeds > 1:
            n_cds_pos = sum(1 for g in cds_gaps if g > 0)
            n_cds_sig = sum(1 for s in cds_gap_sigs if s not in ("", "ns"))
            max_cds_idx = int(np.argmax(cds_gaps))
            print(f"  Peak CDS gap   : {cds_gaps[max_cds_idx]:+.4f} at fog={fog_levels[max_cds_idx]*100:.0f}%"
                  f"  | positive at {n_cds_pos}/{len(fog_levels)} levels"
                  f"  | CDS sig at {n_cds_sig}/{len(fog_levels)} levels")

        if strategy == "Ran":
            print(f"  [Ran note] h is uninformative for random sequences (no temporal structure to model).")
            print(f"             Any fog benefit for Ran reflects gated architecture robustness trained")
            print(f"             with STATE_MASKING_PROB=0.3: the gate suppresses noise (g→1) and the")
            print(f"             LayerNorm branches handle missing features. Report as 'architectural")
            print(f"             benefit of gated fusion', distinct from Transformer intent modeling.")
        print()

        all_strategy_results[strategy] = {
            "fog_levels":         list(fog_levels),
            "thesis_aligns":      [round(x, 4) for x in thesis_aligns],
            "notrans_aligns":     [round(x, 4) for x in notrans_aligns],
            "align_gaps":         [round(x, 4) for x in align_gaps],
            "align_gap_cis":      align_gap_cis,
            "align_gap_pvals":    align_gap_pvals,
            "align_gap_sigs":     align_gap_sigs,
            "thesis_engages":     [round(x, 4) for x in thesis_engages],
            "notrans_engages":    [round(x, 4) for x in notrans_engages],
            "thesis_exprates":    [round(x, 4) for x in thesis_exprates],
            "notrans_exprates":   [round(x, 4) for x in notrans_exprates],
            "rate_gaps":          [round(x, 4) for x in rate_gaps],
            "thesis_cdss":        thesis_cdss,
            "notrans_cdss":       notrans_cdss,
            "cds_gaps":           cds_gaps,
            "cds_gap_cis":        cds_gap_cis,
            "cds_gap_pvals":      cds_gap_pvals,
            "cds_gap_sigs":       cds_gap_sigs,
            "n_seeds":            n_seeds,
        }

    # Cross-strategy summary
    print("  CROSS-STRATEGY SUMMARY  (at fog=90%)")
    print(f"  {'Strategy':>10}  {'AlignGap@90%':>13}  {'EngGap@90%':>11}  "
          f"{'CDSGap@90%':>12}  {'AlignSig':>9}  {'CDSSig':>7}  {'Verdict':>30}")
    print("  " + "-" * 105)
    for strategy, res in all_strategy_results.items():
        ag90   = res["align_gaps"][-1]
        rg90   = res["rate_gaps"][-1]
        cg90   = res["cds_gaps"][-1] if res.get("cds_gaps") else 0.0
        te90   = res["thesis_engages"][-1]
        ne90   = res["notrans_engages"][-1]
        eg90   = te90 - ne90
        asig90 = res["align_gap_sigs"][-1] if res.get("align_gap_sigs") else ""
        csig90 = res["cds_gap_sigs"][-1]   if res.get("cds_gap_sigs")   else ""
        verdict = ("Thesis better: align↑ CDS↑"  if ag90 > 0 and cg90 > 0
                   else "Thesis better: CDS↑ only"     if cg90 > 0
                   else "Thesis better: align↑ only"   if ag90 > 0
                   else "NoTrans holds edge at 90% fog")
        print(f"  {strategy:>10}  {ag90:>+13.4f}  {eg90:>+11.2f}  "
              f"{cg90:>+12.4f}  {asig90:>9}  {csig90:>7}  {verdict}")
    print()

    return all_strategy_results


# ── Results table ─────────────────────────────────────────────────────────────

def print_results_table(all_results):
    print("\n" + "=" * 108)
    print("  THESIS RESULTS — Gated Fusion MARL vs Baselines")
    print("=" * 108)
    print(f"  {'Strategy':<6} {'Method':<32} {'DSR':>7} {'Engage':>9} "
          f"{'Depth':>7} {'Align':>7} {'Reward':>8}")
    print("  " + "-" * 90)
    for strategy in ATTACK_STRATS:
        rows = sorted(
            [r for r in all_results if r["strategy"] == strategy],
            key=lambda x: -x["avg_alignment"]
        )
        for i, r in enumerate(rows):
            prefix = f"  {strategy:<6}" if i == 0 else f"  {'':6}"
            print(f"{prefix} {r['method']:<32} "
                  f"{r['dsr']:>6.1%} {r['engagement_length']:>9.2f} "
                  f"{r['interaction_depth']:>7.2f} {r['avg_alignment']:>7.3f} "
                  f"{r['avg_reward']:>8.3f}")
        print("  " + "-" * 90)
    print("=" * 108)
    print("  DSR    = Deception Success Rate (secondary; topology-saturated)")
    print("  Engage = dwell time with high-affinity stall bonuses")
    print("  Depth  = unique MITRE techniques attempted")
    print("  Align  = technique-action alignment [0,1]  <- KEY METRIC")
    print("  Reward = mean cumulative episode reward")


# ── Composite deception score ─────────────────────────────────────────────────

def compute_composite_scores(all_results,
                              w_align=0.5, w_engage=0.3, w_depth=0.2):
    """
    Composite Deception Score (CDS):
        CDS = w_align * Align
            + w_engage * (Engage / max_Engage_in_strategy)
            + w_depth  * (Depth  / max_Depth_in_strategy)

    Normalisation is per-strategy so scores are comparable across strategies.
    Weights: alignment is primary (0.5), engagement demonstrates dwell-time
    effectiveness (0.3), depth captures attacker exploration breadth (0.2).

    Returns all_results with a new 'composite_score' key per entry.
    """
    for strategy in ATTACK_STRATS:
        rows        = [r for r in all_results if r["strategy"] == strategy]
        max_engage  = max(r["engagement_length"] for r in rows) or 1.0
        max_depth   = max(r["interaction_depth"]  for r in rows) or 1.0
        for r in rows:
            r["composite_score"] = (
                w_align  * r["avg_alignment"] +
                w_engage * r["engagement_length"] / max_engage +
                w_depth  * r["interaction_depth"]  / max_depth
            )
    return all_results


def print_composite_table(all_results, w_align=0.5, w_engage=0.3, w_depth=0.2):
    """
    Print composite score table sorted by CDS per strategy.
    Also prints Thesis vs NoTrans composite lift with 95% CI note.
    """
    print("\n" + "=" * 100)
    print("  COMPOSITE DECEPTION SCORE (CDS)")
    print(f"  CDS = {w_align}×Align  +  {w_engage}×(Engage/max)  +  {w_depth}×(Depth/max)")
    print(f"  Normalised per-strategy. Higher is better.")
    print("=" * 100)
    print(f"  {'Strategy':<8} {'Method':<32} {'Align':>7} {'Engage':>8} "
          f"{'Depth':>7} {'CDS':>7}")
    print("  " + "-" * 78)

    composite_lifts = {}
    for strategy in ATTACK_STRATS:
        rows = sorted(
            [r for r in all_results if r["strategy"] == strategy],
            key=lambda x: -x["composite_score"]
        )
        for i, r in enumerate(rows):
            prefix = f"  {strategy:<8}" if i == 0 else f"  {'':8}"
            marker = " ◄" if "Thesis" in r["method"] else ""
            print(f"{prefix} {r['method']:<32} "
                  f"{r['avg_alignment']:>7.3f} "
                  f"{r['engagement_length']:>8.2f} "
                  f"{r['interaction_depth']:>7.2f} "
                  f"{r['composite_score']:>7.4f}{marker}")
        print("  " + "-" * 78)

        thesis  = next((r for r in rows if "Thesis"         in r["method"]), None)
        notrans = next((r for r in rows if "no Transformer" in r["method"]), None)
        if thesis and notrans:
            composite_lifts[strategy] = thesis["composite_score"] - notrans["composite_score"]

    print()
    print("  COMPOSITE LIFT  (Thesis CDS − NoTrans CDS):")
    print(f"  {'Strategy':<8} {'Thesis CDS':>11} {'NoTrans CDS':>12} {'Lift':>8}")
    print("  " + "-" * 46)
    lifts = []
    for strategy in ATTACK_STRATS:
        rows     = [r for r in all_results if r["strategy"] == strategy]
        thesis   = next((r for r in rows if "Thesis"         in r["method"]), None)
        notrans  = next((r for r in rows if "no Transformer" in r["method"]), None)
        if thesis and notrans:
            lift = thesis["composite_score"] - notrans["composite_score"]
            lifts.append(lift)
            sign = "✓" if lift >= 0 else "✗"
            print(f"  {strategy:<8} {thesis['composite_score']:>11.4f} "
                  f"{notrans['composite_score']:>12.4f} {lift:>+8.4f}  {sign}")
    if lifts:
        mean_lift = float(np.mean(lifts))
        n_pos     = sum(1 for l in lifts if l >= 0)
        print(f"  {'Mean':<8} {'':<11} {'':<12} {mean_lift:>+8.4f}  "
              f"({n_pos}/{len(lifts)} strategies positive)")
    print()
    print("  ◄ = TEMARL (Thesis system)  |  CDS range [0, 1]")
    print("=" * 100)


# ── Entropy Distribution Diagnostics ─────────────────────────────────────────

def diagnose_entropy_distributions(n_eps=100):
    """
    Measure actual entropy distribution from the trained encoder per attack strategy.
    Used to calibrate the entropy_threshold in make_thesis_action_fn.

    Entropy = normalized prediction uncertainty of the Transformer.
      Low  (< 0.80): Transformer is confident -> keep h, let it help
      High (> 0.90): Transformer is uncertain -> zero out h, fall back to telemetry

    Recommendation: set entropy_threshold between p90(HiE/HiC) and p10(Ran).
    """
    print("\n" + "=" * 70)
    print("  ENTROPY DISTRIBUTION DIAGNOSTICS")
    print("=" * 70)
    print(f"  Episodes: {n_eps} per strategy")
    print(f"  Entropy 0=fully confident  1=maximally uncertain")
    print()
    print(f"  {'Strategy':>8}  {'Mean':>7} {'Std':>7} {'p10':>7} {'p50':>7} {'p90':>7} {'p95':>7}")
    print("  " + "-" * 60)

    strategy_data = {}
    for strategy in ATTACK_STRATS:
        try:
            (encoder, agents, _), _nt = get_models(DEVICE)
        except AssertionError:
            print(f"  [{strategy}] model not found, skipping.")
            continue
        env = HoneypotEnv(attack_strategy=strategy, max_steps=200, local_obs=LOCAL_OBS)
        entropies = []
        for _ in range(n_eps):
            obs = env.reset()
            done = False
            while not done:
                h, ent = encoder.get_h_and_entropy_numpy(
                    env.get_padded_sequence(), DEVICE)
                entropies.append(ent)
                full_obs = []
                for o in obs:
                    o2 = o.copy(); o2[-H_DIM:] = h; full_obs.append(o2)
                actions = agents.select_actions(full_obs, epsilon=0.0, entropy_val=ent)
                obs, _, done, _ = env.step(actions, h)
        e = np.array(entropies)
        strategy_data[strategy] = e
        print(f"  {strategy:>8}  {e.mean():>7.3f} {e.std():>7.3f} "
              f"{np.percentile(e,10):>7.3f} {np.percentile(e,50):>7.3f} "
              f"{np.percentile(e,90):>7.3f} {np.percentile(e,95):>7.3f}")

    if "HiE" in strategy_data and "Ran" in strategy_data:
        hie_p90 = np.percentile(strategy_data["HiE"], 90)
        ran_p10 = np.percentile(strategy_data["Ran"], 10)
        recommended = round((hie_p90 + ran_p10) / 2, 2)
        print()
        print(f"  HiE p90 = {hie_p90:.3f}  |  Ran p10 = {ran_p10:.3f}")
        print(f"  Recommended threshold = midpoint = {recommended:.2f}")
        print(f"  Run: python evaluate.py --entropy-th {recommended:.2f}")
    print()


# ── Main ──────────────────────────────────────────────────────────────────────

# ── Gate Collapse Diagnosis ───────────────────────────────────────────────────

def diagnose_gate_collapse(n_diag_eps=50):
    """
    Step 1 diagnostic: measure gate vector g statistics across attack strategies.

    Loads each trained thesis model and runs n_diag_eps episodes per strategy.
    At every step, records the mean gate value across all 64 gate dimensions
    and all 4 agents.

    Interpretation:
      g mean > 0.90 across all strategies → gate collapsed (never left init bias)
      g mean (Ran) > g mean (HiE)        → gate correctly responds to noise
      g mean (HiE) ≈ g mean (Ran)        → gate not differentiating (problem)

    Expected after good training:
      HiE/HiC (structured):  g mean ≈ 0.60-0.80  (blending intent with telemetry)
      Ran      (random):     g mean ≈ 0.85-0.95  (suppressing noisy h)
    """
    print("\n" + "=" * 70)
    print("  GATE COLLAPSE DIAGNOSIS")
    print("=" * 70)
    print(f"  Episodes per strategy: {n_diag_eps}")
    print(f"  Gate value g in (0,1): g->1 = trust telemetry, g->0 = trust intent")
    print(f"  Init bias sigmoid(+2.0) ~0.880 -- if unchanged, gate collapsed")
    print()

    strategy_stats = {}

    for strategy in ATTACK_STRATS:
        try:
            (encoder, agents, _), _nt = get_models(DEVICE)
        except AssertionError as e:
            print(f"  [{strategy}] Model not found — skipping. ({e})")
            continue

        env = HoneypotEnv(attack_strategy=strategy, max_steps=200, local_obs=LOCAL_OBS)
        all_gate_vals = []

        for _ in range(n_diag_eps):
            obs  = env.reset()
            h    = np.zeros(H_DIM, dtype=np.float32)
            done = False

            while not done:
                h = encoder.get_h_numpy(env.get_padded_sequence(), DEVICE)

                # Build full observations for all agents
                full_obs = []
                for o in obs:
                    o2 = o.copy(); o2[-H_DIM:] = h
                    full_obs.append(o2)

                # Collect gate values for all agents at this step
                for agent in agents.agents:
                    obs_t = torch.FloatTensor(
                        np.stack([full_obs[agent.agent_id]])
                    ).to(DEVICE)
                    g = agent.online_net.get_gate_value(obs_t)  # (1, 64)
                    all_gate_vals.append(g.mean().item())

                actions = agents.select_actions(full_obs, epsilon=0.0)
                obs, _, done, _ = env.step(actions, h)

        g_arr = np.array(all_gate_vals)
        strategy_stats[strategy] = {
            "mean": float(g_arr.mean()),
            "std":  float(g_arr.std()),
            "min":  float(g_arr.min()),
            "max":  float(g_arr.max()),
            "p10":  float(np.percentile(g_arr, 10)),
            "p90":  float(np.percentile(g_arr, 90)),
        }

        status = ""
        if g_arr.mean() > 0.90:
            status = "  *** COLLAPSED — stuck at init bias ***"
        elif g_arr.mean() > 0.85:
            status = "  WARNING — barely moved from init"
        else:
            status = "  OK — gate learned to adapt"

        print(f"  [{strategy}] mean={g_arr.mean():.4f}  std={g_arr.std():.4f}"
              f"  min={g_arr.min():.4f}  max={g_arr.max():.4f}"
              f"  p10={np.percentile(g_arr,10):.4f}  p90={np.percentile(g_arr,90):.4f}"
              f"{status}")

    print()
    print("  VERDICT:")
    if not strategy_stats:
        print("  No models found. Train first with train_thesis.py.")
        return

    means = {s: v["mean"] for s, v in strategy_stats.items()}
    overall_mean = np.mean(list(means.values()))

    if overall_mean > 0.90:
        print(f"  Overall mean gate = {overall_mean:.4f}")
        print(f"  GATE COLLAPSED. The Transformer h is being ignored.")
        print(f"  Root cause of negative Transformer lift confirmed.")
        print(f"  -> Implement entropy-aware gating (Step 2).")
    elif overall_mean > 0.85:
        print(f"  Overall mean gate = {overall_mean:.4f}")
        print(f"  Gate barely adapted. h has limited influence.")
        print(f"  -> Entropy-aware gating still recommended.")
    else:
        print(f"  Overall mean gate = {overall_mean:.4f}")
        print(f"  Gate adapted during training.")

    if "HiE" in means and "Ran" in means:
        diff = means["Ran"] - means["HiE"]
        print(f"\n  HiE gate mean = {means['HiE']:.4f}  |  Ran gate mean = {means['Ran']:.4f}")
        if diff > 0.02:
            print(f"  Ran gate > HiE gate by {diff:.4f} — gate IS responding to noise (correct direction)")
        elif diff < -0.02:
            print(f"  HiE gate > Ran gate by {abs(diff):.4f} — gate responding backwards (unexpected)")
        else:
            print(f"  Ran ≈ HiE (diff={diff:+.4f}) — gate NOT differentiating by attacker structure")

    print()
    return strategy_stats


# ── Multi-seed CI + paired t-test ────────────────────────────────────────────

def _paired_ttest(a, b):
    """
    Paired t-test: H0: mean(a-b) == 0.
    Returns (t_stat, p_value, ci_half_95) using scipy if available,
    else falls back to a lookup table for df 1..19 and normal approx beyond.
    """
    d  = np.array(a) - np.array(b)
    n  = len(d)
    md = d.mean()
    se = d.std(ddof=1) / np.sqrt(n) if n > 1 else 1e-9
    t  = md / se if se > 1e-12 else 0.0

    if _SCIPY:
        p   = float(2 * _scipy_stats.t.sf(abs(t), df=n - 1))
        cih = float(_scipy_stats.t.ppf(0.975, df=n - 1) * se)
    else:
        # t critical values for two-tailed α=0.05, df=1..19
        _tcrit = [12.706,4.303,3.182,2.776,2.571,2.447,2.365,
                  2.306,2.262,2.228,2.201,2.179,2.160,2.145,
                  2.131,2.120,2.110,2.101,2.093]
        df   = min(n - 1, 19)
        tc   = _tcrit[df - 1] if df >= 1 else 12.706
        cih  = float(tc * se)
        # Rough p-value: just flag significance
        p    = 0.0 if abs(t) > tc else 1.0   # 0 = significant, 1 = not

    return float(t), float(p), float(cih), float(md)


def _anticipation_rollout(strategy, use_h, n_eps, encoder, net):
    """
    One rollout collecting the responsible agent's alignment split by whether
    that agent could SEE the attacker at decision time.

    For each step: the attacker executes technique T then moves; the agent whose
    subnet contains the attacker's new node is 'responsible' (matches the reward's
    NODE_TO_AGENT credit assignment). If the attacker was NOT already in that
    agent's subnet at decision time, the agent was BLIND and had to anticipate
    (using h); otherwise it was SIGHTED (h not needed). Returns per-step
    alignment lists for the two buckets.
    """
    import random as _random
    env = HoneypotEnv(attack_strategy=strategy, max_steps=200, local_obs=LOCAL_OBS)
    blind_al, sighted_al = [], []
    for _ in range(n_eps):
        obs = env.reset()
        prev_node = env.attacker_node
        done = False
        while not done:
            intent_prior = None
            if use_h:
                h, ent = encoder.get_h_and_entropy_numpy(env.get_padded_sequence(), DEVICE)
                if USE_INTENT_PRIOR:
                    with torch.no_grad():
                        h_t = torch.FloatTensor(h).unsqueeze(0).to(DEVICE)
                        intent_prior = peap_prior(encoder.pretrain_head(h_t)).squeeze(0)
            else:
                h, ent = np.zeros(H_DIM, dtype=np.float32), 1.0
            full = [o.copy() for o in obs]
            for o in full:
                o[-H_DIM:] = h
            actions = net.select_actions(full, epsilon=0.0, entropy_val=ent,
                                         intent_prior=intent_prior)
            prev_subnet = NODE_TO_AGENT.get(prev_node)
            obs, _, done, info = env.step(actions, h)
            T   = info["technique_id"]
            cur = info["attacker_node"]
            resp = NODE_TO_AGENT.get(cur)
            if resp is not None and 0 <= T < ALIGNMENT_MATRIX.shape[0]:
                al = float(ALIGNMENT_MATRIX[T][actions[resp]])
                (sighted_al if prev_subnet == resp else blind_al).append(al)
            prev_node = cur
    return blind_al, sighted_al


def run_anticipation_analysis(n_seeds=5, n_eps=N_EVAL_EPS):
    """
    ANTICIPATION ANALYSIS (the mechanism experiment).

    Isolates WHEN the Transformer intent vector h actually helps: it should
    help precisely when a responsible agent is BLIND (attacker just crossed into
    its subnet) and must anticipate, and add nothing when the agent is SIGHTED
    (already observing the attacker locally). Reports the Thesis-vs-NoTrans
    alignment gap separately for BLIND and SIGHTED steps, with 95% CIs and
    paired t-tests across seeds.

    Expected signature of a working intent model:
      - BLIND gap  > 0 and significant for structured strategies (HiE/HiC/Mix)
      - BLIND gap  <= 0 for Ran (h is noise for random attackers)
      - SIGHTED gap ~ 0 everywhere (h irrelevant when attacker is observed)
    """
    import random as _random
    print("\n" + "=" * 96)
    print("  ANTICIPATION ANALYSIS — does h help precisely when agents are BLIND?")
    print(f"  Seeds: {n_seeds} × {n_eps} eps   |   responsible agent = attacker's post-move subnet owner")
    print("  BLIND  = attacker just crossed INTO responsible agent's subnet (needs h)")
    print("  SIGHTED= attacker already in responsible agent's subnet last step (h not needed)")
    print("=" * 96)

    summary = {}
    for strategy in ATTACK_STRATS:
        (encoder, agents, _), (agents_base, _) = get_models(DEVICE)

        tb_seed, nb_seed = [], []   # per-seed BLIND means (thesis, notrans)
        ts_seed, ns_seed = [], []   # per-seed SIGHTED means
        pct_blind = []
        for seed_i in range(n_seeds):
            _random.seed(seed_i * 17 + 3);  np.random.seed(seed_i * 17 + 3)
            tb, ts = _anticipation_rollout(strategy, True,  n_eps, encoder, agents)
            _random.seed(seed_i * 17 + 3);  np.random.seed(seed_i * 17 + 3)
            nb, ns = _anticipation_rollout(strategy, False, n_eps, None, agents_base)
            if tb: tb_seed.append(np.mean(tb))
            if nb: nb_seed.append(np.mean(nb))
            if ts: ts_seed.append(np.mean(ts))
            if ns: ns_seed.append(np.mean(ns))
            tot = len(tb) + len(ts)
            pct_blind.append(100.0 * len(tb) / tot if tot else 0.0)

        t_b, p_b, ci_b, md_b = _paired_ttest(tb_seed, nb_seed)
        t_s, p_s, ci_s, md_s = _paired_ttest(ts_seed, ns_seed)
        sig_b = ("***" if p_b < 0.001 else "**" if p_b < 0.01 else "*" if p_b < 0.05 else "ns")
        sig_s = ("***" if p_s < 0.001 else "**" if p_s < 0.01 else "*" if p_s < 0.05 else "ns")

        print(f"\n  Strategy: {strategy}   (BLIND steps = {np.mean(pct_blind):.0f}% of scored steps)")
        print(f"    {'':10} {'Thesis':>8} {'NoTrans':>8} {'Gap':>9} {'±95%CI':>8} {'p-val':>8}  Sig")
        print(f"    {'BLIND':10} {np.mean(tb_seed):>8.3f} {np.mean(nb_seed):>8.3f} "
              f"{md_b:>+9.4f} {ci_b:>8.4f} {p_b:>8.4f}  {sig_b}")
        print(f"    {'SIGHTED':10} {np.mean(ts_seed):>8.3f} {np.mean(ns_seed):>8.3f} "
              f"{md_s:>+9.4f} {ci_s:>8.4f} {p_s:>8.4f}  {sig_s}")

        summary[strategy] = {
            "blind_thesis": float(np.mean(tb_seed)), "blind_notrans": float(np.mean(nb_seed)),
            "blind_gap": md_b, "blind_ci": ci_b, "blind_p": p_b, "blind_sig": sig_b,
            "sighted_thesis": float(np.mean(ts_seed)), "sighted_notrans": float(np.mean(ns_seed)),
            "sighted_gap": md_s, "sighted_ci": ci_s, "sighted_p": p_s, "sighted_sig": sig_s,
            "pct_blind": float(np.mean(pct_blind)),
        }

    print("\n" + "=" * 96)
    print("  SUMMARY — BLIND-step alignment gap (Thesis − NoTrans), the core mechanism claim")
    print(f"  {'Strategy':<8} {'BlindGap':>10} {'p-val':>8} {'Sig':>5}   {'SightedGap':>11} {'p-val':>8} {'Sig':>5}   Reads as")
    print("  " + "-" * 92)
    for s, r in summary.items():
        verdict = ("h HELPS when blind" if r["blind_gap"] > 0 and r["blind_sig"] not in ("ns",)
                   else "h helps (n.s.)" if r["blind_gap"] > 0
                   else "h is noise (as expected)" if s == "Ran"
                   else "h does not help here")
        print(f"  {s:<8} {r['blind_gap']:>+10.4f} {r['blind_p']:>8.4f} {r['blind_sig']:>5}   "
              f"{r['sighted_gap']:>+11.4f} {r['sighted_p']:>8.4f} {r['sighted_sig']:>5}   {verdict}")
    print("=" * 96 + "\n")
    return summary


def multiseed_alignment_analysis(n_seeds=10, n_eps=200, entropy_th=1.01):
    """
    Run evaluation n_seeds times, each with a fresh numpy seed, to get
    confidence intervals and paired t-test p-values for Thesis vs NoTrans.

    Each seed produces one sample (mean alignment over n_eps episodes).
    With n_seeds samples we compute:
      - 95% CI via t-distribution  (mean ± t_{0.025,df} * se)
      - Paired t-test p-value       (H0: lift == 0)

    Interpretation:
      p > 0.05  → lift NOT statistically significant  → "no sig diff" finding
      p < 0.05  → lift IS significant                 → strong positive claim
    """
    print("\n" + "=" * 90)
    print(f"  MULTI-SEED CONFIDENCE INTERVAL ANALYSIS")
    print(f"  Seeds: {n_seeds}  ×  Episodes/seed: {n_eps}  =  {n_seeds*n_eps} obs per method")
    print(f"  Entropy threshold: {entropy_th}")
    if not _SCIPY:
        print("  Note: scipy not installed — using lookup table for t-critical values.")
    print("=" * 90)

    summary = {}

    for strategy in ATTACK_STRATS:
        (encoder, agents, _), (agents_base, _) = get_models(DEVICE)

        thesis_fn  = make_thesis_action_fn(agents, encoder, DEVICE,
                                           entropy_threshold=entropy_th)
        notrans_fn = make_notrans_action_fn(agents_base)

        thesis_aligns  = []
        notrans_aligns = []

        print(f"\n  Strategy: {strategy}")
        print(f"  {'Seed':>5}  {'Thesis':>8}  {'NoTrans':>8}  {'Lift':>8}")
        print(f"  {'-'*38}")

        for seed_i in range(n_seeds):
            np.random.seed(seed_i * 7 + 1)
            r_t = evaluate_method("Thesis",  thesis_fn,  strategy,
                                  encoder, n=n_eps)
            np.random.seed(seed_i * 7 + 500)
            r_n = evaluate_method("NoTrans", notrans_fn, strategy, n=n_eps)

            ta = r_t["avg_alignment"]
            na = r_n["avg_alignment"]
            thesis_aligns.append(ta)
            notrans_aligns.append(na)
            print(f"  {seed_i+1:>5}  {ta:>8.4f}  {na:>8.4f}  {ta-na:>+8.4f}")

        t_stat, p_val, cih_lift, mean_lift = _paired_ttest(
            thesis_aligns, notrans_aligns)

        mean_t  = float(np.mean(thesis_aligns))
        std_t   = float(np.std(thesis_aligns, ddof=1))
        se_t    = std_t / np.sqrt(n_seeds)
        mean_n  = float(np.mean(notrans_aligns))
        std_n   = float(np.std(notrans_aligns, ddof=1))
        se_n    = std_n / np.sqrt(n_seeds)

        if _SCIPY:
            cih_t = float(_scipy_stats.t.ppf(0.975, df=n_seeds-1) * se_t)
            cih_n = float(_scipy_stats.t.ppf(0.975, df=n_seeds-1) * se_n)
        else:
            _tcrit = [12.706,4.303,3.182,2.776,2.571,2.447,2.365,
                      2.306,2.262,2.228,2.201,2.179,2.160,2.145,
                      2.131,2.120,2.110,2.101,2.093]
            df   = min(n_seeds - 1, 19)
            tc   = _tcrit[df - 1] if df >= 1 else 12.706
            cih_t = tc * se_t
            cih_n = tc * se_n

        sig = ("***" if p_val < 0.001 else
               "**"  if p_val < 0.01  else
               "*"   if p_val < 0.05  else "ns")

        print(f"  {'-'*38}")
        print(f"  Thesis  : {mean_t:.4f} ± {cih_t:.4f}  (95% CI)")
        print(f"  NoTrans : {mean_n:.4f} ± {cih_n:.4f}  (95% CI)")
        print(f"  Lift    : {mean_lift:+.4f} ± {cih_lift:.4f}  (95% CI)")
        print(f"  t={t_stat:+.3f}  p={p_val:.4f}  [{sig}]")
        if sig == "ns":
            print(f"  -> NOT significant (p>0.05). Thesis ≈ NoTrans on alignment.")
            print(f"     Publishable finding: 'No statistically significant difference'")
        else:
            direction = "BETTER" if mean_lift > 0 else "WORSE"
            print(f"  -> SIGNIFICANT (p<0.05). Thesis is {direction} than NoTrans.")

        summary[strategy] = {
            "mean_thesis":   mean_t,  "ci_thesis":   cih_t,
            "mean_notrans":  mean_n,  "ci_notrans":  cih_n,
            "mean_lift":     mean_lift, "ci_lift":   cih_lift,
            "t_stat":        t_stat,  "p_val":       p_val,
            "significant":   sig != "ns",
        }

    # Final table
    print("\n" + "=" * 90)
    print(f"  SUMMARY TABLE  (mean ± 95%CI, paired t-test vs NoTrans)")
    print(f"  {'Strategy':<8} {'Thesis':>14}  {'NoTrans':>14}  {'Lift':>14}  "
          f"{'t-stat':>7}  {'p-val':>7}  {'Sig':>4}")
    print("  " + "-" * 80)
    for s, r in summary.items():
        print(f"  {s:<8} {r['mean_thesis']:>6.4f}±{r['ci_thesis']:.4f}  "
              f"{r['mean_notrans']:>6.4f}±{r['ci_notrans']:.4f}  "
              f"{r['mean_lift']:>+6.4f}±{r['ci_lift']:.4f}  "
              f"{r['t_stat']:>+7.3f}  {r['p_val']:>7.4f}  "
              f"{'*' if r['significant'] else 'ns':>4}")
    print("=" * 90)
    print("  Sig: *** p<0.001  ** p<0.01  * p<0.05  ns = not significant (publishable 'no diff')")
    print()

    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fog", action="store_true",
                        help="Run Fog of War partial observability analysis")
    parser.add_argument("--fog-seeds", type=int, default=1, metavar="N",
                        help="Seeds for fog-of-war CI + t-test (default 1 = single run, "
                             "use 5 for 95%% CI and p-values). "
                             "Total episodes: 4 strategies × 5 levels × N × 2 × 200.")
    parser.add_argument("--gate", action="store_true",
                        help="Run gate collapse diagnosis (Step 1 diagnostic)")
    parser.add_argument("--train-ppo", action="store_true",
                        help="Train PPO baselines via REINFORCE (800 eps/strategy), save to results/")
    parser.add_argument("--diag-entropy", action="store_true",
                        help="Measure entropy distributions per strategy to calibrate --entropy-th")
    parser.add_argument("--entropy-th", type=float, default=1.01,
                        help="Hard entropy threshold: zero out h when entropy > threshold. "
                             "Run --diag-entropy first to find the right value. Default 1.01 = disabled.")
    parser.add_argument("--ci", type=int, default=0, metavar="N_SEEDS",
                        help="Run multi-seed CI + paired t-test with N_SEEDS seeds (e.g. --ci 10). "
                             "Each seed runs N_EVAL_EPS episodes. Reports 95%% CI and p-values.")
    parser.add_argument("--global-obs", action="store_true",
                        help="Evaluate legacy fully-observable (310-dim) checkpoints. "
                             "Default expects Dec-POMDP local-obs (52-dim) models.")
    parser.add_argument("--anticipation", type=int, default=0, metavar="N_SEEDS",
                        help="Run the anticipation (blind-vs-sighted) mechanism analysis "
                             "with N_SEEDS seeds (e.g. --anticipation 5). Splits alignment "
                             "by whether the responsible agent was blind to the attacker.")
    args = parser.parse_args()

    if args.global_obs:
        global LOCAL_OBS, AGENT_STATE_DIM, AGENT_OBS_DIM, AGENT_SIGHTED_IDX
        LOCAL_OBS         = False
        AGENT_STATE_DIM   = STATE_DIM
        AGENT_OBS_DIM     = STATE_DIM + H_DIM
        AGENT_SIGHTED_IDX = None

    print(f"\n  Device: {DEVICE} | Episodes: {N_EVAL_EPS}")
    print(f"  Observability: {'LOCAL per-subnet (Dec-POMDP)' if LOCAL_OBS else 'GLOBAL (legacy)'}"
          f"  |  agent obs dim = {AGENT_OBS_DIM}\n")
    os.makedirs(RESULTS_DIR, exist_ok=True)

    if args.ci > 0:
        ci_summary = multiseed_alignment_analysis(
            n_seeds=args.ci, n_eps=N_EVAL_EPS, entropy_th=args.entropy_th)
        ci_path = os.path.join(RESULTS_DIR, "ci_analysis.json")
        with open(ci_path, "w") as f:
            json.dump(ci_summary, f, indent=2)
        print(f"  CI analysis saved -> {ci_path}")
        return

    if args.anticipation > 0:
        anticip = run_anticipation_analysis(n_seeds=args.anticipation, n_eps=N_EVAL_EPS)
        with open(os.path.join(RESULTS_DIR, "anticipation_analysis.json"), "w") as f:
            json.dump(anticip, f, indent=2)
        print(f"  Anticipation analysis saved -> {os.path.join(RESULTS_DIR, 'anticipation_analysis.json')}")
        return

    if args.gate:
        diagnose_gate_collapse()
        return

    if args.diag_entropy:
        diagnose_entropy_distributions()
        return

    if args.train_ppo:
        print("  Training PPO baselines (REINFORCE, 800 episodes per strategy) ...")
        for strat in ATTACK_STRATS:
            ppo  = train_ppo_baseline(strat, DEVICE)
            path = os.path.join(RESULTS_DIR, f"ppo_{strat}.pt")
            torch.save(ppo.state_dict(), path)
            print(f"    Saved -> {path}")
        print("  PPO training complete. Run evaluate.py (no flags) to include in results.")
        return

    all_results = []

    for strategy in ATTACK_STRATS:
        print(f"  Strategy: {strategy}")
        print(f"  " + "-" * 40)

        (encoder, agents, mixer), (agents_base, mixer_base) = get_models(DEVICE)

        # Thesis: Gated Fusion QMIX + Transformer (+ optional hard entropy masking)
        thesis_fn = make_thesis_action_fn(agents, encoder, DEVICE, fog_prob=0.0,
                                          entropy_threshold=args.entropy_th)
        r1 = evaluate_method("MARL + Transformer (Thesis)", thesis_fn,
                             strategy, encoder)
        all_results.append(r1)
        print(f"  Thesis:   Align={r1['avg_alignment']:.3f} | "
              f"Engage={r1['engagement_length']:.2f} | "
              f"Depth={r1['interaction_depth']:.2f} | "
              f"Reward={r1['avg_reward']:.3f}")

        # Ablation: h=zeros
        notrans_fn = make_notrans_action_fn(agents_base, fog_prob=0.0)
        r2 = evaluate_method("MARL (no Transformer)", notrans_fn, strategy)
        all_results.append(r2)
        print(f"  NoTrans:  Align={r2['avg_alignment']:.3f} | "
              f"Engage={r2['engagement_length']:.2f} | "
              f"Depth={r2['interaction_depth']:.2f} | "
              f"Reward={r2['avg_reward']:.3f}")

        # FIX-1: imitation+PPO policy head on the frozen intent representation.
        # This is the learner moved OFF the divergent TD value function.
        policy_agents = get_policy_model(DEVICE)
        if policy_agents is not None:
            policy_fn = make_policy_action_fn(policy_agents, fog_prob=0.0)
            r_pol = evaluate_method("Policy Head (FIX-1)", policy_fn, strategy, encoder)
            all_results.append(r_pol)
            print(f"  Policy:   Align={r_pol['avg_alignment']:.3f} | "
                  f"Engage={r_pol['engagement_length']:.2f} | "
                  f"Depth={r_pol['interaction_depth']:.2f} | "
                  f"Reward={r_pol['avg_reward']:.3f}   <- FIX-1 (imitation+PPO on h)")

        # Step-counter oracle: perfect clock, NO intent model. This is the null
        # model that beat the Transformer in the legacy environment; any Thesis
        # advantage over THIS row cannot be attributed to timing alone.
        r_cnt = evaluate_method("Step-Counter Oracle", counter_oracle_action_fn, strategy)
        all_results.append(r_cnt)
        print(f"  Counter:  Align={r_cnt['avg_alignment']:.3f} | "
              f"Engage={r_cnt['engagement_length']:.2f} | "
              f"Depth={r_cnt['interaction_depth']:.2f} | "
              f"Reward={r_cnt['avg_reward']:.3f}   <- perfect clock, zero intent")

        # Static
        r3 = evaluate_method("Static Honeypot", static_action_fn, strategy)
        all_results.append(r3)
        print(f"  Static:   Align={r3['avg_alignment']:.3f} | "
              f"Engage={r3['engagement_length']:.2f} | "
              f"Depth={r3['interaction_depth']:.2f} | "
              f"Reward={r3['avg_reward']:.3f}")

        # Random policy baseline
        r4 = evaluate_method("Random Policy", random_action_fn, strategy)
        all_results.append(r4)
        print(f"  Random:   Align={r4['avg_alignment']:.3f} | "
              f"Engage={r4['engagement_length']:.2f} | "
              f"Depth={r4['interaction_depth']:.2f} | "
              f"Reward={r4['avg_reward']:.3f}")

        # Critical (rule-based expert) baseline
        r5 = evaluate_method("Critical Policy", critical_action_fn, strategy)
        all_results.append(r5)
        print(f"  Critical: Align={r5['avg_alignment']:.3f} | "
              f"Engage={r5['engagement_length']:.2f} | "
              f"Depth={r5['interaction_depth']:.2f} | "
              f"Reward={r5['avg_reward']:.3f}")

        # Single-Agent PPO (trained if checkpoint exists, untrained otherwise)
        ppo = load_trained_ppo(strategy, DEVICE)
        r6  = evaluate_method("Single-Agent PPO", make_ppo_action_fn(ppo), strategy)
        all_results.append(r6)
        print(f"  PPO:      Align={r6['avg_alignment']:.3f} | "
              f"Engage={r6['engagement_length']:.2f} | "
              f"Depth={r6['interaction_depth']:.2f} | "
              f"Reward={r6['avg_reward']:.3f}")
        print()

    print_results_table(all_results)
    all_results = compute_composite_scores(all_results)
    print_composite_table(all_results)

    path = os.path.join(RESULTS_DIR, "evaluation_results.json")
    with open(path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\n  Results saved -> {path}")

    # Alignment and engagement summaries
    print("\n  ALIGNMENT SUMMARY:")
    print(f"  {'Strategy':<6} {'Thesis':>8} {'No-Trans':>10} "
          f"{'Static':>8} {'Random':>8} {'Critical':>9} {'PPO':>8} {'Lift':>8}")
    print(f"  {'-'*64}")
    for strategy in ATTACK_STRATS:
        s        = [r for r in all_results if r["strategy"] == strategy]
        thesis   = next(r for r in s if "Thesis"         in r["method"])
        notrans  = next(r for r in s if "no Transformer" in r["method"])
        static   = next(r for r in s if "Static"         in r["method"])
        rand_r   = next(r for r in s if "Random"         in r["method"])
        crit_r   = next(r for r in s if "Critical"       in r["method"])
        ppo_r    = next(r for r in s if "PPO"            in r["method"])
        lift     = thesis["avg_alignment"] - notrans["avg_alignment"]
        print(f"  {strategy:<6} {thesis['avg_alignment']:>8.3f} "
              f"{notrans['avg_alignment']:>10.3f} "
              f"{static['avg_alignment']:>8.3f} "
              f"{rand_r['avg_alignment']:>8.3f} "
              f"{crit_r['avg_alignment']:>9.3f} "
              f"{ppo_r['avg_alignment']:>8.3f} {lift:>+8.3f}")

    print("\n  ENGAGEMENT vs DEPTH (decoupled):")
    print(f"  {'Strategy':<6} {'Method':<28} {'Engage':>8} {'Depth':>8}")
    print(f"  {'-'*52}")
    for strategy in ATTACK_STRATS:
        for r in [x for x in all_results if x["strategy"] == strategy]:
            print(f"  {strategy:<6} {r['method']:<28} "
                  f"{r['engagement_length']:>8.2f} "
                  f"{r['interaction_depth']:>8.2f}")
        print(f"  {'-'*52}")

    # Optional Fog of War analysis
    if args.fog:
        fog_results = run_fog_of_war_analysis(
            fog_levels=(0.0, 0.25, 0.5, 0.75, 0.9),
            entropy_th=args.entropy_th,
            n_seeds=args.fog_seeds)
        fog_path = os.path.join(RESULTS_DIR, "fog_of_war_results.json")
        with open(fog_path, "w") as f:
            json.dump(fog_results, f, indent=2)
        print(f"  Fog of War results saved -> {fog_path}")


if __name__ == "__main__":
    main()