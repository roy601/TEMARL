# -*- coding: utf-8 -*-
"""
TEMARL v5 — the pre-registered confirmatory run
================================================
Executes exactly the design in `prereg_v5.py`, committed before this ran.
Crash-safe: the results file is rewritten after every arm.

Training is behaviour cloning on the transition oracle, identically for every
arm. The choice of BC over PPO was made from GRU-only runs (no arm cleared the
memoryless baseline under PPO at any budget tried); see the prereg docstring.
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

import prereg_v5 as PR
from d3fend_payoff import N_ACTIONS, PAYOFF
from encoders import GRUIntentEncoder
from encoders_rope import TransformerRoPE
from entity_encoders import match_entity_capacity
from policy_entity import EntityAgentNet, stack_obs
from train_entity_v4 import _rewindow
from train_entity_v5 import (RESULTS, _h_for_v5, build_topologies, evaluate,
                             make_env, DEVICE, MAX_SEQ_LEN, OPT_ACTION)

BUILD = {"Transformer-RoPE": TransformerRoPE, "GRU": GRUIntentEncoder,
         "GRU-d32": GRUIntentEncoder}


def build_enc(name):
    hp = dict(PR.HPARAMS[name])
    hp.pop("lr", None)
    return BUILD[name](**hp).to(DEVICE)


def pretrain(name, seed, topos):
    """History-encoder pretraining on the ACTION objective, then FROZEN."""
    torch.manual_seed(seed); np.random.seed(seed)
    rng = np.random.default_rng(seed)
    X, L, Y = [], [], []
    for i in range(400):
        env = make_env(topos[i % len(topos)], int(rng.integers(1 << 30)))
        env.reset()
        done = False
        while not done:
            acts = [(int(rng.integers(0, N_ACTIONS)),
                     int(env.legal_targets(a)[0])) for a in range(env.n_agents)]
            ids, ln = _rewindow(*env.padded_sequence(), MAX_SEQ_LEN)
            _, _, done, info = env.step(acts)
            X.append(ids); L.append(ln); Y.append(info["technique_id"])
    X, L, Y = np.asarray(X), np.asarray(L), np.asarray(Y)
    A = OPT_ACTION[np.clip(Y, 0, len(OPT_ACTION) - 1)].astype(np.int64)
    enc = build_enc(name)
    head = nn.Linear(enc.d_model, N_ACTIONS).to(DEVICE)
    params = list(enc.parameters()) + list(head.parameters())
    opt = torch.optim.AdamW(params, lr=PR.HPARAMS[name]["lr"], weight_decay=1e-4)
    sch = torch.optim.lr_scheduler.CosineAnnealingLR(opt, PR.PRETRAIN_STEPS,
                                                     eta_min=1e-6)
    Xt = torch.as_tensor(X, dtype=torch.long, device=DEVICE)
    Lt = torch.as_tensor(L, dtype=torch.long, device=DEVICE)
    At = torch.as_tensor(A, dtype=torch.long, device=DEVICE)
    enc.train()
    for _ in range(PR.PRETRAIN_STEPS):
        b = torch.randint(0, len(Y), (128,), device=DEVICE)
        loss = F.cross_entropy(head(enc(Xt[b], Lt[b])), At[b])
        opt.zero_grad(); loss.backward()
        nn.utils.clip_grad_norm_(params, 1.0)
        opt.step(); sch.step()
    enc.freeze()
    return enc


def clone(enc, net_name, seed, topos):
    """Behaviour cloning on the transition oracle."""
    torch.manual_seed(seed); np.random.seed(seed)
    rng = np.random.default_rng(seed)
    suite, _ = match_entity_capacity()
    net = EntityAgentNet(suite[net_name], h_dim=enc.d_model).to(DEVICE)
    B, Y = [], []
    for i in range(PR.BC_EPISODES):
        env = make_env(topos[i % len(topos)], int(rng.integers(1 << 30)),
                       enc.d_model)
        env.reset()
        done = False
        while not done:
            a_star = int((np.asarray(env.profiles[env._profile]["T"][env.tau])
                          @ PAYOFF).argmax())
            h, _ = _h_for_v5(enc, env)
            B.append(stack_obs(env.observations(h), DEVICE)); Y.append(a_star)
            acts = [(a_star, int(env.legal_targets(ag)[0]))
                    for ag in range(env.n_agents)]
            _, _, done, _ = env.step(acts)
    opt = torch.optim.AdamW(net.parameters(), lr=1e-3, weight_decay=1e-5)
    Yt = torch.as_tensor(Y, dtype=torch.long, device=DEVICE)
    for s in range(PR.BC_STEPS):
        i = int(rng.integers(len(B)))
        tl, _, _ = net(B[i], 0.0)
        loss = F.cross_entropy(tl, Yt[i].expand(tl.shape[0]))
        opt.zero_grad(); loss.backward()
        nn.utils.clip_grad_norm_(net.parameters(), 0.5)
        opt.step()
    with torch.no_grad():
        acc = float(np.mean([
            (net(B[i], 0.0)[0].argmax(-1) == Yt[i]).float().mean().item()
            for i in range(0, len(B), max(1, len(B) // 300))]))
    return net, acc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(RESULTS, "entity_v5.json"))
    ap.add_argument("--prereg-commit", default="unknown")
    ap.add_argument("--seeds", type=int, nargs="*", default=list(PR.SEEDS))
    ap.add_argument("--arms", nargs="*", default=None,
                    help='subset of arms as "History/Network" strings')
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    topos = {r: build_topologies(r) for r in PR.REGIMES}
    arms = PR.ARMS
    if args.arms:
        want = {tuple(a.split("/")) for a in args.arms}
        arms = [a for a in PR.ARMS if tuple(a) in want]
        assert len(arms) == len(want), "unknown arm in --arms: %s" % want
    rows, t0 = [], time.time()
    total = len(arms) * len(args.seeds)
    print("=" * 100)
    print("  TEMARL v5 — PRE-REGISTERED CONFIRMATORY RUN  (prereg %s)"
          % args.prereg_commit)
    print("=" * 100)
    print("  %d arms x %d seeds = %d runs | %s | device %s"
          % (len(PR.ARMS), len(args.seeds), total, PR.TRAINING, DEVICE))

    for hist_name, net_name in arms:
        for seed in args.seeds:
            ts = time.time()
            enc = pretrain(hist_name, seed, topos["B"])
            net, acc = clone(enc, net_name, seed, topos["B"])
            row = {"history_encoder": hist_name, "network_encoder": net_name,
                   "objective": PR.OBJECTIVE, "seed": seed,
                   "teacher_acc": acc,
                   "d_model": PR.HPARAMS[hist_name]["d_model"],
                   "n_params_hist": sum(p.numel() for p in enc.parameters()),
                   "n_params_pol": sum(p.numel() for p in net.parameters()),
                   "train_seconds": time.time() - ts}
            for rg in PR.REGIMES:
                m = evaluate(net, enc, topos[rg], PR.EVAL_EPISODES, seed)
                for k, v in m.items():
                    row["%s_%s" % (rg, k)] = v
            rows.append(row)
            with open(args.out, "w", encoding="utf-8") as f:
                json.dump({"prereg_commit": args.prereg_commit,
                           "prereg": {"hypotheses": PR.HYPOTHESES,
                                      "arms": PR.ARMS,
                                      "contrast_family": PR.CONTRAST_FAMILY,
                                      "validity_gate": PR.VALIDITY_GATE,
                                      "hparams": PR.HPARAMS,
                                      "training": PR.TRAINING,
                                      "declaration": PR.DECLARATION},
                           "device": DEVICE, "rows": rows,
                           "complete": len(rows) == total,
                           "arms_run": [list(a) for a in arms],
                           "seeds": list(args.seeds),
                           "seconds": time.time() - t0}, f, indent=1,
                          default=float)
            print("  [%2d/%2d] %-18s %-18s seed %d | acc %.3f | B %.4f  D %.4f "
                  "| %.0f s"
                  % (len(rows), total, hist_name, net_name, seed, acc,
                     row["B_dsr"], row["D_dsr"], row["train_seconds"]))
    print("\n  DONE %d/%d in %.0f s -> %s"
          % (len(rows), total, time.time() - t0,
             os.path.relpath(args.out, RESULTS)))
    print("=" * 100)


if __name__ == "__main__":
    main()
