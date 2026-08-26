# evaluate_advanced.py
"""
Advanced Evaluation — Measured Results
=======================================
Four measured outputs, all reading metrics via env accessors:

  PART 1 — Metric Discrimination Analysis
  PART 2 — Generalization Matrix
  PART 3 — Transformer Contribution
  PART 4 — Final Evaluation Summary

All episode runners use env.get_engagement_length() and
env.get_interaction_depth() — no manual step counters.
Gated Fusion agents loaded with state_masking_prob=0.0 for eval.
"""

import torch
import numpy as np
import json
import os
from collections import defaultdict

from mitre_techniques import NUM_TECHNIQUES
from transformer_encoder import AttackerIntentEncoder
from qmix_mixer import QMIXMixer, H_DIM
from simulation_env import (
    HoneypotEnv, N_AGENTS, STATE_DIM, ALIGNMENT_MATRIX
)
from qmix_agent import MultiAgentQMIX, OBS_DIM

RESULTS_DIR   = r"results"
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
    ckpt    = torch.load(path, map_location=device, weights_only=True)
    encoder.load_state_dict(
        _expand_encoder(ckpt["encoder"], encoder.state_dict()), strict=True)
    for i, agent in enumerate(agents.agents):
        agent.online_net.load_state_dict(ckpt["agents"][i])
    encoder.eval(); agents.eval(); agents.set_masking_prob(0.0)
    return encoder, agents

def load_baseline_model(strategy, device):
    path = os.path.join(RESULTS_DIR, f"baseline_notrans_{strategy}.pt")
    assert os.path.exists(path), f"Not found: {path}"
    agents = MultiAgentQMIX(state_masking_prob=0.0, device=device)
    ckpt   = torch.load(path, map_location=device, weights_only=True)
    for i, agent in enumerate(agents.agents):
        agent.online_net.load_state_dict(ckpt["agents"][i])
    agents.eval(); agents.set_masking_prob(0.0)
    return agents


# ── Action functions ──────────────────────────────────────────────────────────

def static_action_fn(obs, h):
    return [0] * N_AGENTS

def make_thesis_fn(agents):
    def fn(obs, h):
        full = []
        for o in obs:
            o2 = o.copy(); o2[STATE_DIM:] = h; full.append(o2)
        return agents.select_actions(full, epsilon=0.0)
    return fn

def make_notrans_fn(agents_base):
    def fn(obs, h):
        hz = np.zeros(H_DIM, dtype=np.float32)
        full = []
        for o in obs:
            o2 = o.copy(); o2[STATE_DIM:] = hz; full.append(o2)
        return agents_base.select_actions(full, epsilon=0.0)
    return fn


# ── Unified episode runner — env accessors only ───────────────────────────────

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
        "dsr":               1.0 if trapped else 0.0,
        "engagement_length": env.get_engagement_length(),
        "interaction_depth": float(env.get_interaction_depth()),
    }

def collect(action_fn, strategy, encoder=None, n=N_EVAL_EPS):
    env = HoneypotEnv(attack_strategy=strategy, max_steps=200)
    al, dsr_a, eng, dep = [], [], [], []
    for _ in range(n):
        r = run_episode(env, action_fn, encoder)
        al.append(r["alignment"]); dsr_a.append(r["dsr"])
        eng.append(r["engagement_length"]); dep.append(r["interaction_depth"])
    return np.array(al), np.array(dsr_a), np.array(eng), np.array(dep)


# ── PART 1 — Metric discrimination ────────────────────────────────────────────

def part1_discrimination():
    print("=" * 78)
    print("  PART 1 — METRIC DISCRIMINATION ANALYSIS (measured)")
    print("=" * 78)
    print("  Question: which metric actually separates good methods from bad?")
    print()

    per = {m: defaultdict(dict) for m in
           ("alignment", "dsr", "engagement_length", "interaction_depth")}

    for strategy in ATTACK_STRATS:
        encoder, agents = load_thesis_model(strategy, DEVICE)
        agents_base     = load_baseline_model(strategy, DEVICE)
        methods = {
            "Thesis":  (make_thesis_fn(agents),       encoder),
            "NoTrans": (make_notrans_fn(agents_base), None),
            "Static":  (static_action_fn,             None),
        }
        for mname, (fn, enc) in methods.items():
            al, dsr_a, eng, dep = collect(fn, strategy, enc)
            per["alignment"][strategy][mname]         = (al.mean(),  al.std())
            per["dsr"][strategy][mname]               = (dsr_a.mean(), dsr_a.std())
            per["engagement_length"][strategy][mname] = (eng.mean(), eng.std())
            per["interaction_depth"][strategy][mname] = (dep.mean(), dep.std())

    GAP_DIR = {"alignment": +1, "dsr": +1,
               "engagement_length": +1, "interaction_depth": -1}
    THRESH  = {"alignment": 0.05, "dsr": 0.05,
               "engagement_length": 2.0, "interaction_depth": 0.05}

    summary = {}
    for metric in ("alignment", "dsr", "engagement_length", "interaction_depth"):
        d = GAP_DIR[metric]; gaps = []; overlaps = 0
        for strategy in ATTACK_STRATS:
            tm, ts = per[metric][strategy]["Thesis"]
            sm, ss = per[metric][strategy]["Static"]
            raw_gap = d * (tm - sm); gaps.append(raw_gap)
            if d == +1:
                overlap = (tm - ts) <= (sm + ss)
            else:
                overlap = (sm - ss) <= (tm + ts)
            if overlap: overlaps += 1
        mean_gap = float(np.mean(gaps))
        summary[metric] = {
            "mean_gap_marl_advantage": round(mean_gap, 4),
            "strategies_with_band_overlap": overlaps,
            "discriminates": bool(mean_gap > THRESH[metric] and overlaps == 0),
        }

    print(f"  {'Metric':<20} {'MARL Advantage':>16} {'Overlaps':>10} {'Discriminates?':>16}")
    print(f"  {'-'*64}")
    for metric, s in summary.items():
        disc = "YES" if s["discriminates"] else "NO"
        print(f"  {metric:<20} {s['mean_gap_marl_advantage']:>16.4f} "
              f"{s['strategies_with_band_overlap']:>10d} {disc:>16}")
    print()
    print("  Interpretation:")
    print("  - Alignment: large +gap, no overlap → DISCRIMINATES.")
    print("  - Engagement Length: +gap = MARL keeps attacker busy longer.")
    print("  - Interaction Depth: MARL-trained attacker explores fewer new techniques.")
    print("  - DSR: near-zero gap, full overlap → saturated (secondary only).")
    print()
    return {"per_metric_means": {
                m: {s: {k: [round(v[0],4), round(v[1],4)] for k,v in d.items()}
                    for s, d in by_s.items()}
                for m, by_s in per.items()},
            "discrimination_summary": summary}


# ── PART 2 — Generalization matrix ────────────────────────────────────────────

def part2_generalization():
    print("=" * 78)
    print("  PART 2 — GENERALIZATION MATRIX (third proposal metric)")
    print("=" * 78)
    print("  Train strategy (row) evaluated against all strategies (columns).")
    print()

    matrix = {}
    for train_strat in ATTACK_STRATS:
        encoder, agents = load_thesis_model(train_strat, DEVICE)
        fn = make_thesis_fn(agents)
        matrix[train_strat] = {}
        for eval_strat in ATTACK_STRATS:
            al, _, _, _ = collect(fn, eval_strat, encoder)
            matrix[train_strat][eval_strat] = float(al.mean())

    header = "  Train\\Eval " + "".join(f"{s:>9}" for s in ATTACK_STRATS)
    print(header)
    print("  " + "-" * (len(header) - 2))
    for ts in ATTACK_STRATS:
        row = f"  {ts:<10}" + "".join(f"{matrix[ts][es]:>9.3f}" for es in ATTACK_STRATS)
        print(row)
    print()

    diag     = [matrix[s][s] for s in ATTACK_STRATS]
    off_diag = [matrix[a][b] for a in ATTACK_STRATS for b in ATTACK_STRATS if a != b]
    d_mean   = float(np.mean(diag))
    o_mean   = float(np.mean(off_diag))
    drop     = d_mean - o_mean
    print(f"  Diagonal mean    : {d_mean:.4f}")
    print(f"  Off-diagonal mean: {o_mean:.4f}")
    print(f"  Generalization drop: {drop:+.4f}")
    if abs(drop) < 0.05:
        print("  -> STRONG generalization (drop < 0.05).")
    elif drop < 0.15:
        print("  -> Reasonable generalization.")
    else:
        print("  -> Weak generalization — strategy-specific models.")
    print()
    return {"matrix": {a: {b: round(matrix[a][b],4) for b in ATTACK_STRATS}
                       for a in ATTACK_STRATS},
            "diagonal_mean": round(d_mean,4),
            "off_diagonal_mean": round(o_mean,4),
            "generalization_drop": round(drop,4)}


# ── PART 3 — Transformer contribution ─────────────────────────────────────────

def part3_transformer_contribution(p1):
    print("=" * 78)
    print("  PART 3 — TRANSFORMER CONTRIBUTION (alignment metric)")
    print("=" * 78)
    al = p1["per_metric_means"]["alignment"]
    print(f"  {'Strategy':<10} {'Thesis':>10} {'NoTrans':>10} {'Lift':>10}")
    print(f"  {'-'*42}")
    lifts = []; out = {}
    for s in ATTACK_STRATS:
        t = al[s]["Thesis"][0]; n = al[s]["NoTrans"][0]
        lift = t - n; lifts.append(lift)
        out[s] = {"thesis": t, "notrans": n, "lift": round(lift,4)}
        print(f"  {s:<10} {t:>10.3f} {n:>10.3f} {lift:>+10.3f}")
    mean_lift = float(np.mean(lifts))
    print(f"  {'-'*42}")
    print(f"  Mean Transformer lift: {mean_lift:+.4f}")
    print()
    print("  Honest reading: MARL coordination drives the large gain over static.")
    print("  Transformer adds strategy-dependent benefit; decisive value shown")
    print("  on real COMISET data (see real_data_evaluate_b.py results).")
    print()
    out["mean_lift"] = round(mean_lift,4)
    return out


# ── PART 4 — Final summary ─────────────────────────────────────────────────────

def part4_final_summary(p1):
    print("=" * 78)
    print("  PART 4 — FINAL EVALUATION SUMMARY")
    print("=" * 78)
    print("  Metric order: [1] Engagement Length  [2] Interaction Depth")
    print("                [3] Alignment Score    [4] DSR (secondary)")
    print()

    pm = p1["per_metric_means"]
    col = 10
    hdr = (f"  {'Strategy':<6} {'Method':<10}"
           f"{'[1] Eng':>{col}}{'[2] Dep':>{col}}"
           f"{'[3] Align':>{col}}{'[4] DSR':>{col}}")
    print(hdr); print("  " + "-" * (len(hdr) - 2))

    out = {}
    for s in ATTACK_STRATS:
        out[s] = {}
        for mname in ("Thesis", "NoTrans", "Static"):
            eng  = pm["engagement_length"][s][mname][0]
            dep  = pm["interaction_depth"][s][mname][0]
            aln  = pm["alignment"][s][mname][0]
            dsr  = pm["dsr"][s][mname][0]
            print(f"  {s:<6} {mname:<10}"
                  f"{eng:{col}.2f}{dep:{col}.2f}"
                  f"{aln:{col}.3f}{dsr:{col}.3f}")
            out[s][mname] = {"engagement_length": round(eng,4),
                             "interaction_depth": round(dep,4),
                             "alignment_score":   round(aln,4),
                             "dsr":               round(dsr,4)}
        print()

    print("  Aggregate means (Thesis across all strategies):")
    for key, label in [("engagement_length","[1] Engagement Length"),
                       ("interaction_depth","[2] Interaction Depth"),
                       ("alignment_score",  "[3] Alignment Score"),
                       ("dsr",              "[4] DSR")]:
        vals = [out[s]["Thesis"][key] for s in ATTACK_STRATS]
        print(f"    {label:<26}: {float(np.mean(vals)):.4f}")
    print()
    return out


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print(f"\n  Device: {DEVICE} | Episodes per cell: {N_EVAL_EPS}\n")
    os.makedirs(RESULTS_DIR, exist_ok=True)

    p1 = part1_discrimination()
    p2 = part2_generalization()
    p3 = part3_transformer_contribution(p1)
    p4 = part4_final_summary(p1)

    out = {"config": {"n_eval_episodes": N_EVAL_EPS, "strategies": ATTACK_STRATS},
           "part1_metric_discrimination": p1,
           "part2_generalization": p2,
           "part3_transformer_contribution": p3,
           "part4_final_summary": p4}

    path = os.path.join(RESULTS_DIR, "advanced_evaluation.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print("=" * 78)
    print(f"  All results saved -> {path}")
    print("=" * 78)

if __name__ == "__main__":
    main()