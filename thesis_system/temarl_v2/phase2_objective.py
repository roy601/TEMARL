# -*- coding: utf-8 -*-
"""
PHASE 2.6 — Pretraining-objective artefact test
================================================
HYPOTHESIS. The history encoder is trained on the WRONG objective. It is
optimised for next-technique prediction, but the policy needs whatever predicts
the OPTIMAL DECEPTION ACTION. Phase 1 / v3 measured no positive relationship
between next-technique accuracy and DSR (r = -0.175, p = 0.18), so the objective
and the downstream goal may simply be misaligned -- and an architecture ranking
measured on the wrong objective would not transfer.

PREDICTION IF TRUE. Ranking architectures by "how decodable is the optimal
action from a frozen h" gives a different ordering than ranking them by
next-technique accuracy -- possibly one in which attention wins.

WHY THIS PROBE AND NOT FULL RL. The alignment term that drives DSR is
PAYOFF[tau_next, action]. So the quantity the policy actually needs from h is
argmax_a PAYOFF[tau_next, a]. Probing that directly isolates the representation
question from RL optimisation noise, at a fraction of the cost. It is a proxy
for DSR, not DSR itself, and is reported as such.

FOUR OBJECTIVES, each trained then FROZEN, then probed by a linear head:
  next        next-technique cross-entropy          (the current objective)
  action      optimal decoy action directly         (the aligned objective)
  masked      masked-technique reconstruction       (BERT-style)
  contrastive same-campaign vs different-campaign   (InfoNCE)

THREE PROBES on the frozen h:
  next        next technique          (what we currently optimise)
  action      optimal decoy action    (what the policy needs)
  profile     latent campaign class   (what intent modelling claims to recover)

ARTEFACT-ELIMINATION experiment, not the pre-registered test.
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

from d3fend_payoff import N_ACTIONS, PAYOFF
from data_real import load_camlds_verified, to_windows
from encoders import GRUIntentEncoder, SetIntentEncoder, TransformerIntentEncoder
from phase2_seqlen_pe import TransformerRoPE, camlds_split
from vocab_v2 import NUM_TECHNIQUES

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results_v3")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
# Phase 2.5 result: RoPE > absolute sinusoidal at every context length, so
# both are carried here -- comparing objectives on the handicapped variant
# alone would repeat the artefact this phase exists to remove.
BUILD = {"Transformer-Sin": TransformerIntentEncoder,
         "Transformer-RoPE": TransformerRoPE,
         "GRU": GRUIntentEncoder,
         "SetEncoder": SetIntentEncoder}
MODELS = tuple(BUILD)
OBJECTIVES = ("next", "action", "masked", "contrastive")

# optimal decoy action for each technique, from the FROZEN payoff matrix
OPT_ACTION = np.asarray(PAYOFF).argmax(1)


def build_targets(Y, S, scen_of_seq):
    """action target = argmax_a PAYOFF[next_technique, a]; profile = campaign."""
    act = OPT_ACTION[np.clip(Y, 0, len(OPT_ACTION) - 1)]
    scen_names = sorted(set(scen_of_seq))
    sid = {s: i for i, s in enumerate(scen_names)}
    prof = np.array([sid[scen_of_seq[s]] for s in S])
    return act.astype(np.int64), prof.astype(np.int64), len(scen_names)


def train_encoder(name, objective, X, L, Y, A, pool, steps, bs, seed,
                  n_prof=None, P=None, lr=5e-4):
    torch.manual_seed(seed)
    np.random.seed(seed)
    enc = BUILD[name]().to(DEVICE)
    head = None
    if objective == "action":
        head = nn.Linear(enc.d_model, N_ACTIONS).to(DEVICE)
    params = list(enc.parameters()) + (list(head.parameters()) if head else [])
    opt = torch.optim.AdamW(params, lr=lr, weight_decay=1e-4)
    sch = torch.optim.lr_scheduler.CosineAnnealingLR(opt, steps, eta_min=1e-6)

    Xt = torch.as_tensor(X[pool], dtype=torch.long, device=DEVICE)
    Lt = torch.as_tensor(L[pool], dtype=torch.long, device=DEVICE)
    Yt = torch.as_tensor(Y[pool], dtype=torch.long, device=DEVICE)
    At = torch.as_tensor(A[pool], dtype=torch.long, device=DEVICE)
    Pt = torch.as_tensor(P[pool], dtype=torch.long, device=DEVICE) if P is not None else None

    enc.train()
    for _ in range(steps):
        b = torch.randint(0, len(pool), (min(bs, len(pool)),), device=DEVICE)
        if objective == "next":
            _, lg = enc.pretrain_forward(Xt[b], Lt[b])
            loss = F.cross_entropy(lg, Yt[b])
        elif objective == "action":
            h = enc(Xt[b], Lt[b])
            loss = F.cross_entropy(head(h), At[b])
        elif objective == "masked":
            xb = Xt[b].clone()
            m = (torch.rand_like(xb.float()) < 0.15) & (xb != enc.pad_id)
            tgt = xb.clone()
            xb[m] = enc.pad_id
            _, lg = enc.pretrain_forward(xb, Lt[b])
            # reconstruct the LAST real token when it was masked; otherwise
            # fall back to next-token so the batch is never empty
            last = (Lt[b] - 1).clamp(min=0)
            gold = tgt.gather(1, last[:, None]).squeeze(1)
            loss = F.cross_entropy(lg, gold)
        elif objective == "contrastive":
            h = F.normalize(enc(Xt[b], Lt[b]), dim=-1)
            sim = h @ h.t() / 0.1
            same = (Pt[b][:, None] == Pt[b][None, :]).float()
            same.fill_diagonal_(0)
            sim.fill_diagonal_(-1e9)
            # InfoNCE with all same-campaign windows as positives
            logp = F.log_softmax(sim, dim=-1)
            denom = same.sum(-1).clamp(min=1)
            loss = -((logp * same).sum(-1) / denom).mean()
        else:
            raise ValueError(objective)
        opt.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(params, 1.0)
        opt.step()
        sch.step()
    enc.freeze()
    return enc


def linear_probe(enc, X, L, T, tr, te, n_cls, steps=400, bs=256, seed=0):
    """Train a LINEAR head on the FROZEN h; report held-out accuracy."""
    torch.manual_seed(seed)
    with torch.no_grad():
        def emb(idx):
            out = []
            for i in range(0, len(idx), 2048):
                j = idx[i:i + 2048]
                out.append(enc(torch.as_tensor(X[j], dtype=torch.long, device=DEVICE),
                               torch.as_tensor(L[j], dtype=torch.long, device=DEVICE)))
            return torch.cat(out)
        Htr, Hte = emb(tr), emb(te)
    ytr = torch.as_tensor(T[tr], dtype=torch.long, device=DEVICE)
    yte = torch.as_tensor(T[te], dtype=torch.long, device=DEVICE)
    head = nn.Linear(Htr.shape[1], n_cls).to(DEVICE)
    opt = torch.optim.AdamW(head.parameters(), lr=1e-3, weight_decay=1e-4)
    for _ in range(steps):
        b = torch.randint(0, len(Htr), (min(bs, len(Htr)),), device=DEVICE)
        loss = F.cross_entropy(head(Htr[b]), ytr[b])
        opt.zero_grad(); loss.backward(); opt.step()
    with torch.no_grad():
        acc = (head(Hte).argmax(-1) == yte).float().mean().item()
    return acc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=1000)
    ap.add_argument("--batch", type=int, default=128)
    ap.add_argument("--seeds", type=int, nargs="*", default=[0, 1, 2])
    ap.add_argument("--out", default=os.path.join(RESULTS, "phase2_objective.json"))
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("=" * 100)
    print("  PHASE 2.6 - PRETRAINING OBJECTIVE x ARCHITECTURE")
    print("=" * 100)
    print("  device=%s steps=%d seeds=%s" % (DEVICE, args.steps, args.seeds))
    print("  probe target that matters: OPTIMAL DECOY ACTION "
          "(argmax_a PAYOFF[next_technique, a])")

    seqs, scen, info = load_camlds_verified()
    X, L, Y, S = to_windows(seqs)
    A, P, n_prof = build_targets(Y, S, scen)
    print("  CAM-LDS %d runs -> %d windows | %d action classes | %d campaigns\n"
          % (info["n_runs"], len(Y), N_ACTIONS, n_prof))

    rows = []
    t0 = time.time()
    for seed in args.seeds:
        tr, te = camlds_split(scen, S, seed)
        # majority baselines on this split
        bmaj = {
            "next": float((Y[te] == np.bincount(Y[tr]).argmax()).mean()),
            "action": float((A[te] == np.bincount(A[tr]).argmax()).mean()),
            "profile": float((P[te] == np.bincount(P[tr]).argmax()).mean()),
        }
        for obj in OBJECTIVES:
            for m in MODELS:
                enc = train_encoder(m, obj, X, L, Y, A, tr, args.steps,
                                    args.batch, seed, n_prof, P)
                pn = linear_probe(enc, X, L, Y, tr, te, NUM_TECHNIQUES + 2, seed=seed)
                pa = linear_probe(enc, X, L, A, tr, te, N_ACTIONS, seed=seed)
                pp = linear_probe(enc, X, L, P, tr, te, n_prof, seed=seed)
                rows.append({"seed": seed, "objective": obj, "model": m,
                             "probe_next": pn, "probe_action": pa,
                             "probe_profile": pp, "baselines": bmaj})
                del enc
            g = {r["model"]: r for r in rows if r["seed"] == seed
                 and r["objective"] == obj}
            bt = max(g["Transformer-Sin"]["probe_action"],
                     g["Transformer-RoPE"]["probe_action"])
            print("    seed=%d obj=%-11s action-probe  Sin=%.3f RoPE=%.3f "
                  "GRU=%.3f Set=%.3f  bestT-GRU=%+.4f"
                  % (seed, obj, g["Transformer-Sin"]["probe_action"],
                     g["Transformer-RoPE"]["probe_action"],
                     g["GRU"]["probe_action"], g["SetEncoder"]["probe_action"],
                     bt - g["GRU"]["probe_action"]))

    print("\n" + "=" * 100)
    print("  DOES THE OBJECTIVE CHANGE THE ARCHITECTURE RANKING?")
    print("=" * 100)
    b = rows[0]["baselines"]
    print("  majority baselines: next=%.3f action=%.3f profile=%.3f"
          % (b["next"], b["action"], b["profile"]))
    summary = []
    for probe in ("next", "action", "profile"):
        print("\n  probe: %s" % probe.upper())
        print("  %-12s %10s %10s %10s %10s %12s   %s"
              % ("objective", "Sin", "RoPE", "GRU", "SetEnc",
                 "bestT - GRU", "winner"))
        print("  " + "-" * 88)
        for obj in OBJECTIVES:
            g = {m: float(np.mean([r["probe_" + probe] for r in rows
                                   if r["objective"] == obj and r["model"] == m]))
                 for m in MODELS}
            win = max(g, key=g.get)
            bt = max(g["Transformer-Sin"], g["Transformer-RoPE"])
            summary.append({"probe": probe, "objective": obj, "winner": win,
                            "gap_bestT_minus_G": bt - g["GRU"], **g})
            print("  %-12s %10.3f %10.3f %10.3f %10.3f %+12.4f   %s"
                  % (obj, g["Transformer-Sin"], g["Transformer-RoPE"],
                     g["GRU"], g["SetEncoder"], bt - g["GRU"], win))

    wins = [s for s in summary if s["winner"].startswith("Transformer")]
    print("\n  Transformer wins %d of %d (probe x objective) cells: %s"
          % (len(wins), len(summary),
             [(s["probe"], s["objective"]) for s in wins] or "none"))

    os.makedirs(RESULTS, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"config": vars(args), "device": DEVICE, "rows": rows,
                   "summary": summary, "seconds": time.time() - t0},
                  f, indent=1, default=float)
    print("\n  wrote -> %s (%.0fs)"
          % (os.path.relpath(args.out, HERE), time.time() - t0))
    print("=" * 100)


if __name__ == "__main__":
    main()
