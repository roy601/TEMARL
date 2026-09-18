# -*- coding: utf-8 -*-
"""
TEMARL v5 — h-width confound control  (EXPLORATORY, pre-experiment)
====================================================================
A 3-seed pilot (`results_v5/bc_compare.json`) found, under behaviour cloning on
the transition oracle:

    regime B (trained sizes) : Transformer - GRU = -0.0000 DSR   (tie)
    regime D (unseen sizes)  : Transformer - GRU = +0.0333 DSR
                               GRU captures 31.5% of DSR headroom
                               Transformer captures 90.0%

That is the pattern Symes Thompson et al. (arXiv:2410.17647) predict -- attention
"matches performance when training on a single network" but outperforms "across
fixed-size networks of varying topologies". It is also exactly the kind of result
that should be distrusted until the obvious confound is ruled out.

THE CONFOUND
------------
The history encoder reads ONLY the technique sequence; topology never enters it.
So it cannot generalise across topologies by itself. What differs downstream is
the WIDTH of h handed to the policy alongside topology-varying entity features:

    Transformer-RoPE   d_model =  32   (156,310 encoder params)
    GRU                d_model = 128   (351,702 encoder params)

a 4x difference, inherited from the Phase 2.4 per-architecture tuning. A wider h
gives the policy more capacity to memorise trained-size patterns, which would
degrade unseen-size generalisation for reasons having nothing to do with
attention.

THE CONTROL
-----------
Add GRU-d32: a GRU with d_model=32, width-matched to the Transformer, everything
else unchanged.

    if GRU-d32 generalises LIKE the Transformer  -> the effect is h-width,
                                                    and the architecture claim
                                                    does not survive
    if GRU-d32 still generalises POORLY          -> the effect is architectural

This is run BEFORE the pre-registration is finalised, so that the confirmatory
experiment tests a hypothesis that has already survived its most obvious
alternative explanation.
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

import prereg_v4 as PR4
from d3fend_payoff import PAYOFF
from encoders import GRUIntentEncoder
from encoders_rope import TransformerRoPE
from entity_encoders import match_entity_capacity
from policy_entity import EntityAgentNet, stack_obs
from train_entity_v5 import (RESULTS, _h_for_v5, build_topologies, evaluate,
                             make_env, pretrain_history, DEVICE)

# The control arm. Identical to the tuned GRU except d_model, which is matched
# to the Transformer's 32.
VARIANTS = {
    "GRU":              dict(cls=GRUIntentEncoder,
                             kw=dict(hidden=256, n_layers=1, d_model=128),
                             lr=3e-4),
    "GRU-d32":          dict(cls=GRUIntentEncoder,
                             kw=dict(hidden=256, n_layers=1, d_model=32),
                             lr=3e-4),
    "Transformer-RoPE": dict(cls=TransformerRoPE,
                             kw=dict(n_layers=4, n_heads=8, d_ff=512,
                                     d_model=32),
                             lr=1e-3),
}


def build_enc(name):
    v = VARIANTS[name]
    return v["cls"](**v["kw"]).to(DEVICE)


def pretrain(name, seed, topos, n_seq=400, steps=1500):
    """Same procedure as train_entity_v5.pretrain_history, on the action
    objective, but for an arbitrary encoder spec so the control can be built."""
    torch.manual_seed(seed); np.random.seed(seed)
    rng = np.random.default_rng(seed)
    from d3fend_payoff import N_ACTIONS
    from train_entity_v5 import MAX_SEQ_LEN, OPT_ACTION
    from train_entity_v4 import _rewindow
    X, L, Y = [], [], []
    for i in range(n_seq):
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
    opt = torch.optim.AdamW(params, lr=VARIANTS[name]["lr"], weight_decay=1e-4)
    sch = torch.optim.lr_scheduler.CosineAnnealingLR(opt, steps, eta_min=1e-6)
    Xt = torch.as_tensor(X, dtype=torch.long, device=DEVICE)
    Lt = torch.as_tensor(L, dtype=torch.long, device=DEVICE)
    At = torch.as_tensor(A, dtype=torch.long, device=DEVICE)
    enc.train()
    for _ in range(steps):
        b = torch.randint(0, len(Y), (128,), device=DEVICE)
        loss = F.cross_entropy(head(enc(Xt[b], Lt[b])), At[b])
        opt.zero_grad(); loss.backward()
        nn.utils.clip_grad_norm_(params, 1.0)
        opt.step(); sch.step()
    enc.freeze()
    return enc


def bc(name, seed, topos, n_eps=300, steps=2500):
    torch.manual_seed(seed); np.random.seed(seed)
    rng = np.random.default_rng(seed)
    e = pretrain(name, seed, topos)
    suite, _ = match_entity_capacity()
    net = EntityAgentNet(suite["DeepSets"], h_dim=e.d_model).to(DEVICE)
    B, Y = [], []
    for i in range(n_eps):
        env = make_env(topos[i % len(topos)], int(rng.integers(1 << 30)),
                       e.d_model)
        env.reset()
        done = False
        while not done:
            a_star = int((np.asarray(env.profiles[env._profile]["T"][env.tau])
                          @ PAYOFF).argmax())
            h, _ = _h_for_v5(e, env)
            B.append(stack_obs(env.observations(h), DEVICE)); Y.append(a_star)
            acts = [(a_star, int(env.legal_targets(ag)[0]))
                    for ag in range(env.n_agents)]
            _, _, done, _ = env.step(acts)
    opt = torch.optim.AdamW(net.parameters(), lr=1e-3, weight_decay=1e-5)
    Yt = torch.as_tensor(Y, dtype=torch.long, device=DEVICE)
    for s in range(steps):
        i = int(rng.integers(len(B)))
        tl, _, _ = net(B[i], 0.0)
        loss = F.cross_entropy(tl, Yt[i].expand(tl.shape[0]))
        opt.zero_grad(); loss.backward()
        nn.utils.clip_grad_norm_(net.parameters(), 0.5)
        opt.step()
    return e, net


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="*", default=[0, 1, 2])
    ap.add_argument("--eval", type=int, default=150)
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    base = json.load(open(os.path.join(RESULTS, "baselines_v5.json"),
                          encoding="utf-8"))["results"]
    topos = {"B": build_topologies("B"), "D": build_topologies("D")}

    print("=" * 100)
    print("  h-WIDTH CONFOUND CONTROL — is the regime-D effect attention, or "
          "just a narrower h?")
    print("=" * 100)
    for rg in ("B", "D"):
        b = base[rg]
        print("  regime %s: best_fixed %.4f -> transition oracle %.4f"
              % (rg, b["best_fixed"]["dsr_mean"], b["transition"]["dsr_mean"]))
    print()
    print("  %-18s %6s %-4s %10s %10s %12s %8s"
          % ("encoder", "d_mdl", "reg", "DSR", "alignment", "DSR headroom",
             "sec"))
    print("  " + "-" * 86)

    out = {}
    for name in ("GRU", "GRU-d32", "Transformer-RoPE"):
        for rg in ("B", "D"):
            t0, ds, al = time.time(), [], []
            for seed in args.seeds:
                e, net = bc(name, seed, topos["B"])
                m = evaluate(net, e, topos[rg], args.eval, seed)
                ds.append(m["dsr"]); al.append(m["alignment"])
            bf = base[rg]["best_fixed"]["dsr_mean"]
            orc = base[rg]["transition"]["dsr_mean"]
            cap = 100.0 * (np.mean(ds) - bf) / (orc - bf)
            out["%s/%s" % (name, rg)] = {
                "d_model": VARIANTS[name]["kw"]["d_model"],
                "dsr": float(np.mean(ds)), "alignment": float(np.mean(al)),
                "headroom_pct": float(cap), "per_seed_dsr": ds}
            print("  %-18s %6d %-4s %10.4f %10.4f %11.1f%% %8.0f"
                  % (name, VARIANTS[name]["kw"]["d_model"], rg, np.mean(ds),
                     np.mean(al), cap, time.time() - t0))

    print("\n" + "=" * 100)
    print("  VERDICT ON THE CONFOUND  (regime D, unseen sizes)")
    print("=" * 100)
    g = out["GRU/D"]["headroom_pct"]
    g32 = out["GRU-d32/D"]["headroom_pct"]
    t = out["Transformer-RoPE/D"]["headroom_pct"]
    print("  GRU      (d=128) captures %5.1f%%" % g)
    print("  GRU-d32  (d= 32) captures %5.1f%%   <- the control" % g32)
    print("  Transf.  (d= 32) captures %5.1f%%" % t)
    print()
    if abs(g32 - t) < abs(g32 - g):
        print("  The width-matched GRU behaves like the TRANSFORMER.")
        print("  -> the regime-D effect is an h-WIDTH artefact, not attention.")
        print("     The architecture claim does NOT survive this control.")
    else:
        print("  The width-matched GRU still behaves like the WIDE GRU.")
        print("  -> h width does not explain the effect; it survives as")
        print("     architectural. Proceed to the pre-registered experiment,")
        print("     carrying GRU-d32 as a declared control arm.")
    os.makedirs(RESULTS, exist_ok=True)
    with open(os.path.join(RESULTS, "confound_v5.json"), "w",
              encoding="utf-8") as f:
        json.dump({"exploratory": True, "results": out}, f, indent=1,
                  default=float)
    print("\n  wrote -> results_v5/confound_v5.json")
    print("=" * 100)


if __name__ == "__main__":
    main()
