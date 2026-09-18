# -*- coding: utf-8 -*-
"""
TEMARL v4 — Final experiment: artefact-corrected history encoder on DSR
========================================================================
Runs exactly the design declared in `prereg_v4.py`, committed before this file
was ever executed (commit 7499d29).

WHAT CHANGES FROM v3, AND WHY (each change traces to a Phase 2 result)
  * history encoder may be Transformer-RoPE   <- 2.5 (RoPE > sinusoidal at every
                                                 context length)
  * pretraining objective may be ACTION       <- 2.6 (action-decodability
                                                 0.867 -> 0.934)
  * context length 8 rather than 16           <- 2.2 (longer is worse)
  * per-architecture tuned hyperparameters    <- 2.4 (equal 16-trial budget)
  * 1500 pretrain steps rather than 800       <- 2.5 (at 150 steps RoPE looked
                                                 broken at 0.472; at 1200 it led
                                                 at 0.886 -- training length can
                                                 INVERT a ranking)

WHAT IS HELD FIXED
  the entity environment, the frozen payoff, reward/capture/termination, the
  vocabulary, and the DeepSets network encoder (v3 H6/H7 found no
  EntityTransformer benefit; varying it here would confound the history-encoder
  question).

Results -> results_v4/. Nothing in results_v2/ or results_v3/ is written.
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
from d3fend_payoff import N_ACTIONS, PAYOFF
from encoders import GRUIntentEncoder, TransformerIntentEncoder
from encoders_rope import TransformerRoPE
from env_entity import EntityDeceptionEnv
from policy_entity import EntityAgentNet, stack_obs
import train_entity as _te
from train_entity import (build_topologies, evaluate, profiles,
                          rollout)
from entity_encoders import match_entity_capacity

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results_v4")
RUNS = os.path.join(HERE, "runs_v4")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

BUILD = {"Transformer-RoPE": TransformerRoPE,
         "Transformer-Sin": TransformerIntentEncoder,
         "GRU": GRUIntentEncoder}

# optimal decoy action per technique, read off the FROZEN payoff matrix
OPT_ACTION = np.asarray(PAYOFF).argmax(1)


def build_history_encoder(name):
    """Instantiate with the Phase 2.4 hyperparameters, at the Phase 2.2 length."""
    cfg = {k: v for k, v in PR.HPARAMS[name].items() if k != "lr"}
    return BUILD[name](max_len=PR.MAX_SEQ_LEN, **cfg).to(DEVICE)


def _rewindow(ids, length, max_len):
    """env.padded_sequence() emits MAX_SEQ_LEN(=16) right-padded ids. Take the
    LAST `max_len` REAL tokens and re-pad, so the encoder sees the context length
    the pre-registration declares."""
    from vocab_v2 import PAD_ID
    real = ids[:length]
    keep = real[-max_len:]
    out = np.full(max_len, PAD_ID, dtype=np.int64)
    out[:len(keep)] = keep
    return out, max(len(keep), 1)


def pretrain_history(name, objective, seed, topos, n_seq=400, steps=None,
                     verbose=False):
    """Collect rollouts, train on `objective`, then FREEZE."""
    steps = steps or PR.PRETRAIN_STEPS
    torch.manual_seed(seed)
    np.random.seed(seed)
    rng = np.random.default_rng(seed)
    X, L, Y = [], [], []
    for i in range(n_seq):
        t = topos[i % len(topos)]
        env = EntityDeceptionEnv(topology=t, profiles=profiles(),
                                 max_steps=PR.MAX_STEPS,
                                 max_entities=PR.MAX_ENTITIES,
                                 seed=int(rng.integers(1 << 30)))
        env.reset()
        done = False
        while not done:
            acts = [(int(rng.integers(0, N_ACTIONS)),
                     int(env.legal_targets(a)[0])) for a in range(env.n_agents)]
            ids, ln = env.padded_sequence()
            ids, ln = _rewindow(ids, ln, PR.MAX_SEQ_LEN)
            _, _, done, info = env.step(acts)
            X.append(ids); L.append(ln); Y.append(info["technique_id"])
    X, L, Y = np.asarray(X), np.asarray(L), np.asarray(Y)
    A = OPT_ACTION[np.clip(Y, 0, len(OPT_ACTION) - 1)].astype(np.int64)

    enc = build_history_encoder(name)
    head = nn.Linear(enc.d_model, N_ACTIONS).to(DEVICE) if objective == "action" else None
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
        opt.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(params, 1.0)
        opt.step()
        sch.step()
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


def _h_for_v4(enc, env):
    ids, ln = env.padded_sequence()
    ids, ln = _rewindow(ids, ln, PR.MAX_SEQ_LEN)
    with torch.no_grad():
        h, ent = enc.get_h_and_entropy_numpy(
            np.asarray(ids)[None, :], DEVICE, np.asarray([ln]))
    return h[0], float(ent[0])


# `rollout` and `evaluate` are reused from train_entity so the RL loop is
# IDENTICAL to v3 -- but they call train_entity._h_for, which emits the
# environment's native 16-token window. The pre-registration declares a context
# length of 8 (Phase 2.2), so that module-level hook is redirected here. Without
# this the encoder receives a 16-token sequence and its positional buffer
# mismatches, which is exactly how the first v4 smoke test failed.
_te._h_for = _h_for_v4


def train_arm(hist_enc, train_topos, seed, episodes, gamma=0.99, clip=0.2,
              lr=3e-4, epochs=4, ent_coef=0.01):
    torch.manual_seed(seed)
    np.random.seed(seed)
    suite, _ = match_entity_capacity()
    net = EntityAgentNet(suite[PR.NETWORK_ENCODER],
                         h_dim=hist_enc.d_model).to(DEVICE)
    opt = torch.optim.AdamW(net.parameters(), lr=lr, weight_decay=1e-5)
    rng = np.random.default_rng(seed)
    for ep in range(episodes):
        topo = train_topos[int(rng.integers(len(train_topos)))]
        env = EntityDeceptionEnv(topology=topo, profiles=profiles(),
                                 max_steps=PR.MAX_STEPS,
                                 max_entities=PR.MAX_ENTITIES,
                                 h_dim=hist_enc.d_model,
                                 seed=int(rng.integers(1 << 30)))
        env.reset()
        traj, _ = rollout(net, hist_enc, env, rng, greedy=False, collect=True)
        T = len(traj["rew"])
        if T == 0:
            continue
        ret, R = [], 0.0
        for r in reversed(traj["rew"]):
            R = r + gamma * R
            ret.append(R)
        ret.reverse()
        rets = torch.tensor(ret, dtype=torch.float32, device=DEVICE)
        vals = torch.stack([v.mean() for v in traj["val"]])
        adv = rets - vals.detach()
        if adv.numel() > 1:
            adv = (adv - adv.mean()) / (adv.std() + 1e-8)
        old = torch.stack([lp.detach().mean() for lp in traj["logp"]])
        for _ in range(epochs):
            nlp, nv, ents = [], [], []
            for t in range(T):
                b = traj["obs"][t]
                tl, gl, _ = net(b, traj["ent"][t])
                pt, pg = F.softmax(tl, -1), F.softmax(gl, -1)
                lp = (torch.log(pt.gather(1, traj["types"][t][:, None]).squeeze(1) + 1e-10)
                      + torch.log(pg.gather(1, traj["targets"][t][:, None]).squeeze(1) + 1e-10))
                nlp.append(lp.mean())
                nv.append(net.value(b, traj["ent"][t]).mean())
                ents.append(-(pt * torch.log(pt + 1e-10)).sum(-1).mean())
            nlp, nv = torch.stack(nlp), torch.stack(nv)
            ratio = torch.exp(nlp - old)
            l_pi = -torch.min(ratio * adv,
                              torch.clamp(ratio, 1 - clip, 1 + clip) * adv).mean()
            loss = l_pi + 0.5 * F.mse_loss(nv, rets) \
                - ent_coef * torch.stack(ents).mean()
            opt.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(net.parameters(), 0.5)
            opt.step()
    return net


def _payload(args, rows, t0):
    return {"prereg_commit": "7499d29",
            "prereg": {"hypotheses": PR.HYPOTHESES, "arms": PR.ARMS,
                       "contrast_family": PR.CONTRAST_FAMILY,
                       "hparams": PR.HPARAMS,
                       "max_seq_len": PR.MAX_SEQ_LEN,
                       "network_encoder": PR.NETWORK_ENCODER,
                       "declaration": PR.DECLARATION},
            "config": vars(args), "device": DEVICE, "rows": rows,
            "complete": len(rows) == len(PR.ARMS) * len(args.seeds),
            "total_seconds": time.time() - t0}


def _flush(args, rows, t0):
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(_payload(args, rows, t0), f, indent=1, default=float)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="*", default=list(PR.SEEDS))
    ap.add_argument("--episodes", type=int, default=PR.TRAIN_EPISODES)
    ap.add_argument("--eval-episodes", type=int, default=PR.EVAL_EPISODES)
    ap.add_argument("--out", default=os.path.join(RESULTS, "entity_v4.json"))
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    if args.quick:
        args.seeds, args.episodes, args.eval_episodes = [0], 30, 20
    os.makedirs(RESULTS, exist_ok=True)
    os.makedirs(RUNS, exist_ok=True)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("=" * 100)
    print("  TEMARL v4 — FINAL EXPERIMENT (pre-registered, commit 7499d29)")
    print("=" * 100)
    print("  device=%s  arms=%d  seeds=%s  train_eps=%d  eval_eps=%d"
          % (DEVICE, len(PR.ARMS), args.seeds, args.episodes, args.eval_episodes))
    print("  context=%d  pretrain_steps=%d  network encoder=%s (FIXED)"
          % (PR.MAX_SEQ_LEN, PR.PRETRAIN_STEPS, PR.NETWORK_ENCODER))
    sets = {k: build_topologies(k) for k in ("train", "A", "B", "C", "D")}
    for k, v in sets.items():
        print("  regime %-6s %3d topologies %s"
              % (k, len(v), sorted({t.n_zones for t in v})))
    print()

    rows = []
    t0 = time.time()
    for seed in args.seeds:
        print("  ── seed %d ──" % seed)
        for hname in PR.HISTORY_ENCODERS:
            for obj in PR.OBJECTIVES:
                ts = time.time()
                enc = pretrain_history(hname, obj, seed, sets["train"],
                                       verbose=True)
                net = train_arm(enc, sets["train"], seed, args.episodes)
                tr_s = time.time() - ts
                row = {"seed": seed, "history_encoder": hname,
                       "objective": obj,
                       "network_encoder": PR.NETWORK_ENCODER,
                       "n_params_hist": sum(p.numel() for p in enc.parameters()),
                       "n_params_pol": net.n_params(),
                       "train_seconds": tr_s}
                for rk in ("A", "B", "C", "D"):
                    m = evaluate(net, enc, sets[rk], args.eval_episodes, seed)
                    for k, v in m.items():
                        row["%s_%s" % (rk, k)] = v
                rows.append(row)
                print("    %-18s/%-7s A=%.3f B=%.3f C=%.3f D=%.3f  (%.0fs)"
                      % (hname, obj, row["A_dsr"], row["B_dsr"],
                         row["C_dsr"], row["D_dsr"], tr_s))
                _flush(args, rows, t0)          # crash-safe: persist after each arm
                torch.save({"hist": enc.state_dict(), "net": net.state_dict(),
                            "arm": [hname, obj], "seed": seed},
                           os.path.join(RUNS, "%s_%s_s%d.pt" % (hname, obj, seed)))
                del enc, net

    _flush(args, rows, t0)
    print("\n  wrote -> %s  (%.0fs)"
          % (os.path.relpath(args.out, HERE), time.time() - t0))
    print("=" * 100)


if __name__ == "__main__":
    main()
