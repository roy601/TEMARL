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

from mitre_techniques import NUM_TECHNIQUES
from transformer_encoder import AttackerIntentEncoder
from qmix_mixer import QMIXMixer, H_DIM
from simulation_env import (
    HoneypotEnv, N_AGENTS, N_ACTIONS, STATE_DIM, ALIGNMENT_MATRIX
)
from qmix_agent import MultiAgentQMIX, OBS_DIM

RESULTS_DIR   = r"C:\Users\T25301092\thesis_project\thesis_system\results"
N_EVAL_EPS    = 200
ATTACK_STRATS = ["HiE", "HiC", "Ran", "Mix"]
DEVICE        = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ── Model loaders ─────────────────────────────────────────────────────────────

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
    agents  = MultiAgentQMIX(state_masking_prob=0.0, device=device)
    mixer   = QMIXMixer().to(device)
    ckpt    = torch.load(path, map_location=device, weights_only=True)
    encoder.load_state_dict(
        _expand_encoder(ckpt["encoder"], encoder.state_dict()), strict=True)
    for i, agent in enumerate(agents.agents):
        agent.online_net.load_state_dict(ckpt["agents"][i])
    encoder.eval(); agents.eval(); agents.set_masking_prob(0.0); mixer.eval()
    return encoder, agents, mixer

def load_baseline_model(strategy, device):
    path = os.path.join(RESULTS_DIR, f"baseline_notrans_{strategy}.pt")
    assert os.path.exists(path), f"Not found: {path}"
    agents = MultiAgentQMIX(state_masking_prob=0.0, device=device)
    mixer  = QMIXMixer().to(device)
    ckpt   = torch.load(path, map_location=device, weights_only=True)
    for i, agent in enumerate(agents.agents):
        agent.online_net.load_state_dict(ckpt["agents"][i])
    agents.eval(); agents.set_masking_prob(0.0); mixer.eval()
    return agents, mixer


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
        # Generate per-feature mask: 1.0 = keep, 0.0 = zero
        mask = np.random.binomial(1, 1.0 - fog_prob,
                                  size=STATE_DIM).astype(np.float32)
        obs_masked[:STATE_DIM] *= mask   # zero out fog_prob fraction of state
        # h (positions STATE_DIM:) is never touched
        masked.append(obs_masked)
    return masked


# ── Action functions ──────────────────────────────────────────────────────────

def static_action_fn(obs, h):
    return [0] * N_AGENTS

def make_thesis_action_fn(agents, encoder, device, fog_prob=0.0):
    def fn(obs, h):
        full = []
        for o in obs:
            o2 = o.copy(); o2[STATE_DIM:] = h; full.append(o2)
        full = apply_fog_of_war(full, fog_prob)
        return agents.select_actions(full, epsilon=0.0)
    return fn

def make_notrans_action_fn(agents_base, fog_prob=0.0):
    def fn(obs, h):
        hz = np.zeros(H_DIM, dtype=np.float32)
        full = []
        for o in obs:
            o2 = o.copy(); o2[STATE_DIM:] = hz; full.append(o2)
        full = apply_fog_of_war(full, fog_prob)
        return agents_base.select_actions(full, epsilon=0.0)
    return fn


# ── Baseline 3: Single-Agent PPO (untrained) ──────────────────────────────────

class SingleAgentPPO(nn.Module):
    def __init__(self, obs_dim=OBS_DIM, n_agents=N_AGENTS, n_actions=N_ACTIONS):
        super().__init__()
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
    return lambda obs, h: ppo.select_actions(obs[0])


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
        if encoder is not None:
            h = encoder.get_h_numpy(env.get_padded_sequence(), DEVICE)
        actions = action_fn(obs, h)

        curr = env.attacker_sequence[-1] if env.attacker_sequence else 0
        if curr < ALIGNMENT_MATRIX.shape[0]:
            alignments.append(max(ALIGNMENT_MATRIX[curr][a] for a in actions))

        obs, rewards, done, info = env.step(actions, h)

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
    env     = HoneypotEnv(attack_strategy=strategy, max_steps=200)
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

def run_fog_of_war_analysis(fog_levels=(0.0, 0.3, 0.5, 0.7, 0.9)):
    """
    Empirical proof of Transformer value under partial observability.

    For each fog probability level, evaluates:
      - Thesis (Gated Fusion + Transformer): h available, telemetry masked
      - NoTrans (Gated Fusion, h=zeros):     no h, telemetry masked

    Prediction: as fog_prob increases, the Thesis–NoTrans alignment gap
    should WIDEN because the Transformer's h becomes the primary remaining
    signal once telemetry is degraded.

    This mirrors real-world honeypot deployment where network telemetry
    is incomplete, delayed, or attacker-spoofed.
    """
    print("\n" + "=" * 72)
    print("  FOG OF WAR ANALYSIS — Transformer Value Under Partial Observability")
    print("=" * 72)
    print("  Telemetry masking probability (fog) increases left to right.")
    print("  At fog=0.9: agents receive ~10% of state; only h is reliable.")
    print()

    # Use Mix strategy (most balanced) for the fog analysis
    strategy = "Mix"
    n_fog_eps = 100   # fewer episodes per level to keep runtime reasonable

    encoder, agents, mixer = load_thesis_model(strategy, DEVICE)
    agents_base, _         = load_baseline_model(strategy, DEVICE)

    thesis_aligns  = []
    notrans_aligns = []
    gaps           = []

    col = 10
    hdr = (f"  {'Fog%':>6} {'Thesis Align':>{col+2}} "
           f"{'NoTrans Align':>{col+2}} {'Gap (T-NT)':>{col}}")
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))

    for fog in fog_levels:
        thesis_fn  = make_thesis_action_fn(agents, encoder, DEVICE, fog_prob=fog)
        notrans_fn = make_notrans_action_fn(agents_base, fog_prob=fog)

        r_thesis  = evaluate_method("Thesis",  thesis_fn,  strategy,
                                    encoder, n=n_fog_eps)
        r_notrans = evaluate_method("NoTrans", notrans_fn, strategy,
                                    n=n_fog_eps)

        ta = r_thesis["avg_alignment"]
        na = r_notrans["avg_alignment"]
        gap = ta - na

        thesis_aligns.append(ta)
        notrans_aligns.append(na)
        gaps.append(gap)

        trend = "↑" if (len(gaps) > 1 and gap > gaps[-2]) else ""
        print(f"  {fog*100:>5.0f}%  {ta:{col}.3f}       {na:{col}.3f}       "
              f"{gap:+10.3f}  {trend}")

    print()
    max_gap_idx = int(np.argmax(gaps))
    print(f"  Maximum gap: {gaps[max_gap_idx]:+.3f} at fog={fog_levels[max_gap_idx]*100:.0f}%")
    if gaps[-1] > gaps[0]:
        print(f"  RESULT: Gap WIDENS with fog — Transformer h proves its value "
              f"under partial observability.")
    else:
        print(f"  RESULT: Gap does not consistently widen — gate suppresses h "
              f"even with fog (telemetry residual still dominates).")
    print()

    return {
        "fog_levels":     list(fog_levels),
        "thesis_aligns":  [round(x, 4) for x in thesis_aligns],
        "notrans_aligns": [round(x, 4) for x in notrans_aligns],
        "gaps":           [round(x, 4) for x in gaps],
        "strategy":       strategy,
    }


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


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fog", action="store_true",
                        help="Run Fog of War partial observability analysis")
    args = parser.parse_args()

    print(f"\n  Device: {DEVICE} | Episodes: {N_EVAL_EPS}\n")
    os.makedirs(RESULTS_DIR, exist_ok=True)
    all_results = []

    for strategy in ATTACK_STRATS:
        print(f"  Strategy: {strategy}")
        print(f"  " + "-" * 40)

        encoder, agents, mixer = load_thesis_model(strategy, DEVICE)
        agents_base, mixer_base = load_baseline_model(strategy, DEVICE)

        # Thesis: Gated Fusion QMIX + Transformer
        thesis_fn = make_thesis_action_fn(agents, encoder, DEVICE, fog_prob=0.0)
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

        # Static
        r3 = evaluate_method("Static Honeypot", static_action_fn, strategy)
        all_results.append(r3)
        print(f"  Static:   Align={r3['avg_alignment']:.3f} | "
              f"Engage={r3['engagement_length']:.2f} | "
              f"Depth={r3['interaction_depth']:.2f} | "
              f"Reward={r3['avg_reward']:.3f}")

        # Single-Agent PPO (untrained)
        ppo = SingleAgentPPO().to(DEVICE); ppo.eval()
        r4  = evaluate_method("Single-Agent PPO",
                              make_ppo_action_fn(ppo), strategy)
        all_results.append(r4)
        print(f"  PPO:      Align={r4['avg_alignment']:.3f} | "
              f"Engage={r4['engagement_length']:.2f} | "
              f"Depth={r4['interaction_depth']:.2f} | "
              f"Reward={r4['avg_reward']:.3f}")
        print()

    print_results_table(all_results)

    path = os.path.join(RESULTS_DIR, "evaluation_results.json")
    with open(path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\n  Results saved -> {path}")

    # Alignment and engagement summaries
    print("\n  ALIGNMENT SUMMARY:")
    print(f"  {'Strategy':<6} {'Thesis':>8} {'No-Trans':>10} "
          f"{'Static':>8} {'PPO':>8} {'Lift':>8}")
    print(f"  {'-'*52}")
    for strategy in ATTACK_STRATS:
        s       = [r for r in all_results if r["strategy"] == strategy]
        thesis  = next(r for r in s if "Thesis"         in r["method"])
        notrans = next(r for r in s if "no Transformer" in r["method"])
        static  = next(r for r in s if "Static"         in r["method"])
        ppo     = next(r for r in s if "PPO"            in r["method"])
        lift    = thesis["avg_alignment"] - notrans["avg_alignment"]
        print(f"  {strategy:<6} {thesis['avg_alignment']:>8.3f} "
              f"{notrans['avg_alignment']:>10.3f} "
              f"{static['avg_alignment']:>8.3f} "
              f"{ppo['avg_alignment']:>8.3f} {lift:>+8.3f}")

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
        fog_results = run_fog_of_war_analysis()
        fog_path = os.path.join(RESULTS_DIR, "fog_of_war_results.json")
        with open(fog_path, "w") as f:
            json.dump(fog_results, f, indent=2)
        print(f"  Fog of War results saved -> {fog_path}")


if __name__ == "__main__":
    main()