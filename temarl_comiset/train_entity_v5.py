# -*- coding: utf-8 -*-
"""
TEMARL v5 — training on the repaired environment
=================================================
ADDITIVE. `env_v2.py`, `env_entity.py` defaults, `payoff_frozen.json`,
`train_entity.py` and `train_entity_v4.py` are all unchanged. The v4 result
stands exactly as reported.

WHAT v5 CHANGES, AND THE EVIDENCE FOR EACH
-------------------------------------------
1. ATTACKER-MODEL ESTIMATOR (`profiles_v5.py`)
   Removes `T[:, j] += 1.2`, a column-constant added to every row of the
   transition matrix. A quantity identical in every row carries zero information
   about the transition, and it outweighed the real bigram evidence ~2:1.
     within-campaign I(tau'; tau) : 0.627 -> 1.935 bits (raw data has 4.83)
     sequence value (payoff)      : +0.0002 -> +0.1776
     distinct optimal actions/class: 1.33 -> 4.33
   Verified in `profiles_v5.__main__`: setting goal_drift=1.2 reproduces the v2
   profiles bit-for-bit, so exactly one factor moved.

2. CAPTURE CALIBRATION (`calibrate_v5.py`)
   The repair tripled episode length, which SATURATED DSR at 0.79-0.98 -- the
   precise failure mode env_v2's own gate rejects ("v1: all policies 0.90-0.97").
   A grid over (goal_steps, cap_scale) was scored against four criteria fixed
   before any architecture was trained, using ONLY baseline policies. Exactly one
   cell passed all four: goal_steps=3, cap_scale=0.35.
     null 0.367 | random 0.481 | best_fixed 0.561 | profile 0.572
     | transition 0.622 | clairvoyant 0.697
     episode length 18.4 (v4: 5.45) | spread 0.217 | SEQUENCE VALUE +0.050

3. CONTEXT LENGTH 8 -> 16
   Phase 2.2 concluded "longer context is worse; L=8 best". That was measured
   when episodes averaged 5.45 steps -- there was no history beyond token ~6 for
   a longer context to read, so the comparison was between 8 real tokens and 8
   real tokens plus padding. At 18.4 steps the finding no longer applies, and
   L=8 would discard more than half of every episode. v5 uses the environment's
   native 16-token window. This is a change of a Phase-2 setting and is flagged
   as such.

4. BATCHED PPO
   v3/v4 updated from ONE episode (~5 steps) per update, 4 epochs, 600 times --
   about 3,000 environment steps in total. Five of six v4 arms failed to beat a
   memoryless fixed action. v5 accumulates `--batch-eps` episodes per update.
   This is standard PPO practice, applied IDENTICALLY to every arm; the
   advantage estimator, clipping, entropy bonus and optimiser are unchanged from
   v4 so the algorithm is otherwise the same.

   The budget is chosen by `--sweep`, which trains ONLY the GRU -- the incumbent
   that already learned in v4 -- and picks the smallest budget passing the
   learning gate. Tuning the budget on the incumbent biases against the
   Transformer, which is the conservative direction.

WHAT IS NOT CHANGED
   payoff_frozen.json (never refitted), reward weights, the vocabulary, the
   topology generator, the observation layout, the entity encoders, the policy
   network, the frozen-encoder two-timescale design, and the evaluation protocol.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

import prereg_v4 as PR
import train_entity as _te
from d3fend_payoff import N_ACTIONS, PAYOFF
from encoders import GRUIntentEncoder, TransformerIntentEncoder
from encoders_rope import TransformerRoPE
from entity_encoders import match_entity_capacity
from env_entity import EntityDeceptionEnv
from env_v2 import CAP_P_MAX, CAP_P_MIN
from policy_entity import EntityAgentNet
from profiles_v5 import profiles_v5
from train_entity import build_topologies, rollout
from train_entity_v4 import _rewindow

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results_v5")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ── the calibrated v5 environment (from calibrate_v5.py, architecture-blind) ──
CAP_SCALE = 0.35
GOAL_STEPS = 3
MAX_SEQ_LEN = 16
ENV_KW = dict(cap_p_min=CAP_P_MIN * CAP_SCALE,
              cap_p_max=CAP_P_MAX * CAP_SCALE,
              goal_steps=GOAL_STEPS)

BUILD = {"Transformer-RoPE": TransformerRoPE,
         "Transformer-Sin": TransformerIntentEncoder,
         "GRU": GRUIntentEncoder}
OPT_ACTION = np.asarray(PAYOFF).argmax(1)


def make_env(topo, seed, h_dim=64):
    return EntityDeceptionEnv(topology=topo, profiles=profiles_v5(),
                              max_steps=PR.MAX_STEPS,
                              max_entities=PR.MAX_ENTITIES,
                              h_dim=h_dim, seed=seed, **ENV_KW)


def build_history_encoder(name):
    hp = dict(PR.HPARAMS[name])
    hp.pop("lr", None)
    return BUILD[name](**hp).to(DEVICE)


def _h_for_v5(enc, env):
    ids, ln = env.padded_sequence()
    ids, ln = _rewindow(ids, ln, MAX_SEQ_LEN)
    with torch.no_grad():
        h, ent = enc.get_h_and_entropy_numpy(
            np.asarray(ids)[None, :], DEVICE, np.asarray([ln]))
    return h[0], float(ent[0])


# `rollout` is reused verbatim from train_entity, but it calls the module-level
# `_h_for`, which emits the environment's native window with no re-windowing.
# Redirect it, exactly as v4 did (that hook being missed is how the first v4
# smoke test failed).
_te._h_for = _h_for_v5


def pretrain_history(name, objective, seed, topos, n_seq=400, steps=None,
                     verbose=False):
    """Identical to v4's, on v5 rollouts and the 16-token window. Then FREEZE."""
    steps = steps or PR.PRETRAIN_STEPS
    torch.manual_seed(seed)
    np.random.seed(seed)
    rng = np.random.default_rng(seed)
    X, L, Y = [], [], []
    for i in range(n_seq):
        env = make_env(topos[i % len(topos)], int(rng.integers(1 << 30)))
        env.reset()
        done = False
        while not done:
            acts = [(int(rng.integers(0, N_ACTIONS)),
                     int(env.legal_targets(a)[0])) for a in range(env.n_agents)]
            ids, ln = env.padded_sequence()
            ids, ln = _rewindow(ids, ln, MAX_SEQ_LEN)
            _, _, done, info = env.step(acts)
            X.append(ids); L.append(ln); Y.append(info["technique_id"])
    X, L, Y = np.asarray(X), np.asarray(L), np.asarray(Y)
    A = OPT_ACTION[np.clip(Y, 0, len(OPT_ACTION) - 1)].astype(np.int64)

    enc = build_history_encoder(name)
    head = (nn.Linear(enc.d_model, N_ACTIONS).to(DEVICE)
            if objective == "action" else None)
    params = list(enc.parameters()) + (list(head.parameters()) if head else [])
    opt = torch.optim.AdamW(params, lr=PR.HPARAMS[name]["lr"], weight_decay=1e-4)
    sch = torch.optim.lr_scheduler.CosineAnnealingLR(opt, steps, eta_min=1e-6)
    Xt = torch.as_tensor(X, dtype=torch.long, device=DEVICE)
    Lt = torch.as_tensor(L, dtype=torch.long, device=DEVICE)
    Yt = torch.as_tensor(Y, dtype=torch.long, device=DEVICE)
    At = torch.as_tensor(A, dtype=torch.long, device=DEVICE)

    enc.train()
    for _ in range(steps):
        b = torch.randint(0, len(Y), (128,), device=DEVICE)
        if objective == "next":
            _, lg = enc.pretrain_forward(Xt[b], Lt[b])
            loss = F.cross_entropy(lg, Yt[b])
        else:
            loss = F.cross_entropy(head(enc(Xt[b], Lt[b])), At[b])
        opt.zero_grad(); loss.backward()
        nn.utils.clip_grad_norm_(params, 1.0)
        opt.step(); sch.step()
    enc.freeze()
    if verbose:
        with torch.no_grad():
            n = min(2048, len(Y))
            if objective == "next":
                _, lg = enc.pretrain_forward(Xt[:n], Lt[:n])
                acc = (lg.argmax(-1) == Yt[:n]).float().mean().item()
            else:
                acc = (head(enc(Xt[:n], Lt[:n])).argmax(-1)
                       == At[:n]).float().mean().item()
        print("      history[%s/%s] pretrain acc=%.3f (frozen)"
              % (name, objective, acc))
    return enc


def train_arm(hist_enc, net_name, train_topos, seed, updates, batch_eps,
              gamma=0.99, clip=0.2, lr=3e-4, epochs=4, ent_coef=0.01,
              verbose=False, per_agent=True):
    """PPO over `batch_eps` episodes per update, with per-agent samples.

    TWO CHANGES FROM v4, both standard practice and both applied IDENTICALLY to
    every arm. Neither references any architecture.

    1. BATCHING. v3/v4 updated from ONE ~5-step episode at a time.

    2. PER-AGENT SAMPLES (`per_agent=True`). `rollout` returns per-agent tensors
       of shape [n_agents] for log-probs and values, but v3/v4 collapsed them
       with `.mean()` into a single scalar per timestep. Two consequences:

         * the importance ratio became exp(mean_a delta logp_a) -- the geometric
           mean of the four agents' ratios, not a per-sample ratio. Clipping at
           0.2 then bounds the AVERAGE, so the effective per-agent trust region
           is far tighter than intended and the gradient vanishes early.
         * all four agents received identical credit, although only the agent
           owning the entered zone affects alignment. The signal that
           distinguishes a good decoy choice from an irrelevant one was being
           averaged away three times out of four.

       With per_agent=True each (timestep, agent) is its own PPO sample, which
       is the standard IPPO/MAPPO treatment. The team reward, the return
       definition, gamma, clip, entropy bonus, optimiser and grad clipping are
       unchanged. `per_agent=False` reproduces the v4 update exactly, which is
       how the A/B in `results_v5/ppo_ab.json` was run.
    """
    torch.manual_seed(seed)
    np.random.seed(seed)
    suite, _ = match_entity_capacity()
    net = EntityAgentNet(suite[net_name], h_dim=hist_enc.d_model).to(DEVICE)
    opt = torch.optim.AdamW(net.parameters(), lr=lr, weight_decay=1e-5)
    rng = np.random.default_rng(seed)

    for up in range(updates):
        batch = []
        for _ in range(batch_eps):
            topo = train_topos[int(rng.integers(len(train_topos)))]
            env = make_env(topo, int(rng.integers(1 << 30)), hist_enc.d_model)
            env.reset()
            traj, _ = rollout(net, hist_enc, env, rng, greedy=False, collect=True)
            if len(traj["rew"]):
                batch.append(traj)
        if not batch:
            continue

        rets, obs, ent_l, types, targs, olp, vals = [], [], [], [], [], [], []
        for traj in batch:
            R, r_ep = 0.0, []
            for r in reversed(traj["rew"]):
                R = r + gamma * R
                r_ep.append(R)
            r_ep.reverse()
            for t in range(len(traj["rew"])):
                obs.append(traj["obs"][t]); ent_l.append(traj["ent"][t])
                types.append(traj["types"][t]); targs.append(traj["targets"][t])
                if per_agent:
                    # every (timestep, agent) is its own sample; the team reward
                    # is shared, so the return is broadcast across agents while
                    # the value baseline stays per-agent
                    n_ag = traj["logp"][t].shape[0]
                    rets.extend([r_ep[t]] * n_ag)
                    olp.append(traj["logp"][t].detach())
                    vals.append(traj["val"][t].reshape(-1))
                else:
                    rets.append(r_ep[t])
                    olp.append(traj["logp"][t].detach().mean().reshape(1))
                    vals.append(traj["val"][t].mean().reshape(1))
        T = len(obs)
        rets_t = torch.tensor(rets, dtype=torch.float32, device=DEVICE)
        adv = rets_t - torch.cat(vals).detach()
        if adv.numel() > 1:
            adv = (adv - adv.mean()) / (adv.std() + 1e-8)
        old = torch.cat(olp)

        for _ in range(epochs):
            nlp, nv, ents = [], [], []
            for t in range(T):
                b = obs[t]
                tl, gl, _ = net(b, ent_l[t])
                pt, pg = F.softmax(tl, -1), F.softmax(gl, -1)
                lp = (torch.log(pt.gather(1, types[t][:, None]).squeeze(1) + 1e-10)
                      + torch.log(pg.gather(1, targs[t][:, None]).squeeze(1) + 1e-10))
                v = net.value(b, ent_l[t]).reshape(-1)
                if per_agent:
                    nlp.append(lp); nv.append(v)
                else:
                    nlp.append(lp.mean().reshape(1)); nv.append(v.mean().reshape(1))
                ents.append(-(pt * torch.log(pt + 1e-10)).sum(-1).mean())
            nlp, nv = torch.cat(nlp), torch.cat(nv)
            ratio = torch.exp(nlp - old)
            l_pi = -torch.min(ratio * adv,
                              torch.clamp(ratio, 1 - clip, 1 + clip) * adv).mean()
            loss = (l_pi + 0.5 * F.mse_loss(nv, rets_t)
                    - ent_coef * torch.stack(ents).mean())
            opt.zero_grad(); loss.backward()
            nn.utils.clip_grad_norm_(net.parameters(), 0.5)
            opt.step()
        if verbose and (up + 1) % max(1, updates // 4) == 0:
            print("        update %d/%d (%d eps)" % (up + 1, updates,
                                                     (up + 1) * batch_eps))
    return net


def evaluate(net, hist_enc, topos, n_episodes, seed):
    net.eval()
    rng = np.random.default_rng(1_000_000 + seed)
    acc = {k: [] for k in ("dsr", "alignment", "episode_return",
                           "engagement_length", "capture_rate")}
    for i in range(n_episodes):
        env = make_env(topos[i % len(topos)], int(rng.integers(1 << 30)),
                       hist_enc.d_model)
        env.reset()
        _, st = rollout(net, hist_enc, env, rng, greedy=True, collect=False)
        for k in acc:
            acc[k].append(st[k])
    net.train()
    return {k: float(np.mean(v)) for k, v in acc.items()}


# ── learning-gate sweep: GRU ONLY, never the Transformer ────────────────────

def sweep(args):
    """Choose the training budget on the INCUMBENT, before any comparison.

    The learning gate: an arm must capture >= 50% of the available headroom on
    regime B. Only the GRU is trained here, so the budget cannot be selected to
    favour attention.

    The ceiling is the TRANSITION oracle, not the profile oracle. In v4 the two
    were identical (+0.0005 apart) so the choice was immaterial; in v5 they are
    not -- the repair moved the information from the class label to the
    transition, so the profile oracle is now worth only +0.012 over best_fixed
    while the transition oracle is worth +0.092. The transition oracle is in any
    case the correct ceiling for a history-based policy: it is what a perfect
    next-technique model buys, which is exactly the encoder's job.
    """
    with open(os.path.join(RESULTS, "baselines_v5.json"), encoding="utf-8") as f:
        base = json.load(f)["results"]["B"]
    bf = base["best_fixed"]["dsr_mean"]
    po = base["transition"]["dsr_mean"]
    span = po - bf
    # TWO TIERS, both declared before this sweep was run.
    #   GATE-A (target)  : capture >= 50% of the transition-oracle headroom.
    #   GATE-B (minimum) : beat best_fixed by more than best_fixed's own 95% CI,
    #                      i.e. the arm demonstrably uses intent at all. This is
    #                      precisely what 5 of the 6 v4 arms failed to do.
    # Rule fixed in advance: proceed to the architecture comparison ONLY if
    # GATE-B passes. Select the smallest budget passing GATE-A; failing that,
    # the largest budget passing GATE-B. Report which tier was met.
    bfci = base["best_fixed"]["dsr_ci95"]
    print("  GATE-A  capture >= 50%% of (best_fixed %.3f -> TRANSITION oracle "
          "%.3f, span %.3f)  ->  DSR >= %.3f"
          % (bf, po, span, bf + 0.5 * span))
    print("  GATE-B  beat best_fixed by > its 95%% CI (%.3f)  ->  DSR >= %.3f"
          % (bfci, bf + bfci))

    topos_tr, topos_ev = build_topologies("B"), build_topologies("B")
    rows = []
    for updates, batch_eps in args.grid:
        t0 = time.time()
        dsrs = []
        for seed in args.sweep_seeds:
            enc = pretrain_history("GRU", "action", seed, topos_tr)
            net = train_arm(enc, "DeepSets", topos_tr, seed, updates, batch_eps)
            dsrs.append(evaluate(net, enc, topos_ev, args.sweep_eval, seed)["dsr"])
        m = float(np.mean(dsrs))
        cap = 100.0 * (m - bf) / span
        ga, gb = cap >= 50.0, m >= bf + bfci
        rows.append({"updates": updates, "batch_eps": batch_eps,
                     "episodes": updates * batch_eps, "dsr": m,
                     "capture_pct": cap, "gate_a": bool(ga), "gate_b": bool(gb),
                     "per_seed": dsrs, "seconds": time.time() - t0})
        print("  updates=%-4d batch=%-3d (%5d eps)  DSR %.3f  capture %6.1f%%  "
              "A:%-4s B:%-4s  [%.0f s]"
              % (updates, batch_eps, updates * batch_eps, m, cap,
                 "PASS" if ga else "fail", "PASS" if gb else "fail",
                 time.time() - t0))
    os.makedirs(RESULTS, exist_ok=True)
    with open(os.path.join(RESULTS, "budget_sweep_v5.json"), "w",
              encoding="utf-8") as f:
        json.dump({"architecture": "GRU only (incumbent)",
                   "gate_a_pct": 50, "gate_b_threshold": bf + bfci,
                   "best_fixed": bf, "transition_oracle": po, "rows": rows},
                  f, indent=1, default=float)

    ga = [r for r in rows if r["gate_a"]]
    gb = [r for r in rows if r["gate_b"]]
    if ga:
        sel, tier = min(ga, key=lambda r: r["episodes"]), "GATE-A (>=50%)"
    elif gb:
        sel, tier = max(gb, key=lambda r: r["episodes"]), "GATE-B (beats fixed)"
    else:
        sel, tier = None, None
    if sel is None:
        print("\n  NEITHER gate passes at any budget tried. The learner still")
        print("  cannot use the history. Do NOT proceed to the architecture")
        print("  comparison -- it would reproduce v4's uninterpretable null.")
    else:
        print("\n  SELECTED: updates=%d batch_eps=%d (%d episodes)  via %s"
              % (sel["updates"], sel["batch_eps"], sel["episodes"], tier))
        print("     GRU DSR %.3f, capturing %.1f%% of transition-oracle headroom"
              % (sel["dsr"], sel["capture_pct"]))


def _payload(args, rows, t0, prereg_commit):
    import prereg_v5 as P5
    return {"prereg_commit": prereg_commit,
            "prereg": {"hypotheses": P5.HYPOTHESES, "arms": P5.ARMS,
                       "contrast_family": P5.CONTRAST_FAMILY,
                       "validity_gate": P5.VALIDITY_GATE,
                       "hparams": P5.HPARAMS,
                       "budget": [P5.TRAIN_UPDATES, P5.BATCH_EPISODES],
                       "max_seq_len": P5.MAX_SEQ_LEN,
                       "cap_scale": P5.CAP_SCALE, "goal_steps": P5.GOAL_STEPS,
                       "declaration": P5.DECLARATION},
            "config": {k: v for k, v in vars(args).items() if k != "grid"},
            "device": DEVICE, "rows": rows,
            "complete": len(rows) == len(P5.ARMS) * len(P5.SEEDS),
            "seconds": time.time() - t0}


def run_final(args):
    """The pre-registered v5 experiment. Crash-safe: flushes after every arm."""
    import prereg_v5 as P5
    assert P5.TRAIN_UPDATES and P5.BATCH_EPISODES, \
        "prereg_v5 budget is unset; run --sweep and fill it in before running"
    topos = {r: build_topologies(r) for r in P5.REGIMES}
    rows, t0 = [], time.time()
    total = len(P5.ARMS) * len(P5.SEEDS)
    print("  %d arms x %d seeds = %d runs | budget %d updates x %d eps = %d eps"
          % (len(P5.ARMS), len(P5.SEEDS), total, P5.TRAIN_UPDATES,
             P5.BATCH_EPISODES, P5.TRAIN_UPDATES * P5.BATCH_EPISODES))
    for hist_name, net_name in P5.ARMS:
        for seed in P5.SEEDS:
            ts = time.time()
            enc = pretrain_history(hist_name, P5.OBJECTIVE, seed, topos["B"])
            net = train_arm(enc, net_name, topos["B"], seed,
                            P5.TRAIN_UPDATES, P5.BATCH_EPISODES)
            row = {"history_encoder": hist_name, "network_encoder": net_name,
                   "objective": P5.OBJECTIVE, "seed": seed,
                   "n_params_hist": sum(p.numel() for p in enc.parameters()),
                   "n_params_pol": sum(p.numel() for p in net.parameters()),
                   "train_seconds": time.time() - ts}
            for rg in P5.REGIMES:
                m = evaluate(net, enc, topos[rg], P5.EVAL_EPISODES, seed)
                for k, v in m.items():
                    row["%s_%s" % (rg, k)] = v
            rows.append(row)
            with open(args.out, "w", encoding="utf-8") as f:
                json.dump(_payload(args, rows, t0, args.prereg_commit), f,
                          indent=1, default=float)
            print("  [%2d/%2d] %-18s %-18s seed %d  B_dsr %.3f  D_dsr %.3f  "
                  "[%.0f s]"
                  % (len(rows), total, hist_name, net_name, seed,
                     row["B_dsr"], row["D_dsr"], row["train_seconds"]))
    print("\n  DONE %d/%d in %.0f s -> %s"
          % (len(rows), total, time.time() - t0, os.path.relpath(args.out, HERE)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true",
                    help="run the pre-registered v5 experiment")
    ap.add_argument("--out", default=os.path.join(RESULTS, "entity_v5.json"))
    ap.add_argument("--prereg-commit", default="unknown")
    ap.add_argument("--sweep", action="store_true")
    ap.add_argument("--sweep-seeds", type=int, nargs="*", default=[0, 1])
    ap.add_argument("--sweep-eval", type=int, default=150)
    ap.add_argument("--grid", type=str,
                    default="60x4,150x4,150x8,300x8")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args.grid = [tuple(int(x) for x in g.split("x"))
                 for g in args.grid.split(",")]
    os.makedirs(RESULTS, exist_ok=True)
    print("=" * 92)
    print("  TEMARL v5 — %s   device=%s"
          % ("BUDGET SWEEP (GRU only)" if args.sweep else
             "PRE-REGISTERED RUN" if args.run else "TRAIN", DEVICE))
    print("=" * 92)
    if args.sweep:
        sweep(args)
    elif args.run:
        run_final(args)
    else:
        print("  --sweep to size the budget (GRU only), then --run for the")
        print("  pre-registered experiment declared in prereg_v5.py")
    print("=" * 92)


if __name__ == "__main__":
    main()
