# -*- coding: utf-8 -*-
"""
PHASE 2.4 — Hyperparameter artefact test (equal-budget random search)
======================================================================
HYPOTHESIS. The Transformer loses because its hyperparameters were never tuned
(the defaults 2 layers / 4 heads / d_ff 128 / dropout 0.1 / lr 5e-4 were fixed
once and inherited), while the comparison treats them as if they were.

PREDICTION IF TRUE. Given an equal search budget, the Transformer's best
configuration closes or reverses the gap.

FAIRNESS PROTOCOL (this is what makes the comparison valid).
  * EQUAL BUDGET: every architecture gets the SAME number of random trials.
    Tuning only the Transformer would be exactly the confound this phase exists
    to remove.
  * Configuration is selected on a VALIDATION split and reported on a
    HELD-OUT TEST split it never saw, so the reported number is not the max of a
    search (which is biased upward).
  * Identical seeds, identical data pools, identical step budget per trial.

The search space per architecture is declared below BEFORE running, and the
number of trials is fixed, so "how many things did you try?" has a written
answer: exactly N_TRIALS per architecture.

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

from data_real import (load_camlds_verified, load_comiset_sequences,
                       session_split, to_windows)
from encoders import GRUIntentEncoder, SetIntentEncoder, TransformerIntentEncoder
from phase2_seqlen_pe import TransformerNoPE, TransformerRoPE, camlds_split, score

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results_v3")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ── declared search spaces (fixed before the run) ───────────────────────────
SPACE = {
    "Transformer-Sin": {
        "cls": TransformerIntentEncoder,
        "n_layers": [1, 2, 3, 4], "n_heads": [2, 4, 8],
        "d_ff": [64, 128, 256, 512], "d_model": [32, 64, 128],
        "lr": [1e-4, 3e-4, 5e-4, 1e-3],
    },
    "Transformer-NoPE": {
        "cls": TransformerNoPE,
        "n_layers": [1, 2, 3, 4], "n_heads": [2, 4, 8],
        "d_ff": [64, 128, 256, 512], "d_model": [32, 64, 128],
        "lr": [1e-4, 3e-4, 5e-4, 1e-3],
    },
    "Transformer-RoPE": {
        "cls": TransformerRoPE,
        "n_layers": [1, 2, 3, 4], "n_heads": [2, 4, 8],
        "d_ff": [64, 128, 256, 512], "d_model": [32, 64, 128],
        "lr": [1e-4, 3e-4, 5e-4, 1e-3],
    },
    "GRU": {
        "cls": GRUIntentEncoder,
        "hidden": [64, 112, 192, 256], "n_layers": [1, 2, 3],
        "d_model": [32, 64, 128], "lr": [1e-4, 3e-4, 5e-4, 1e-3],
    },
    "SetEncoder": {
        "cls": SetIntentEncoder,
        "hidden": [128, 256, 520, 768], "d_model": [32, 64, 128],
        "lr": [1e-4, 3e-4, 5e-4, 1e-3],
    },
}


def sample_cfg(name, rng):
    sp = SPACE[name]
    cfg = {k: sp[k][int(rng.integers(len(sp[k])))]
           for k in sp if k != "cls"}
    # heads must divide d_model
    if "n_heads" in cfg:
        valid = [h for h in sp["n_heads"] if cfg["d_model"] % h == 0]
        cfg["n_heads"] = valid[int(rng.integers(len(valid)))]
    return cfg


def build(name, cfg, max_len):
    kw = {k: v for k, v in cfg.items() if k != "lr"}
    return SPACE[name]["cls"](max_len=max_len, **kw).to(DEVICE)


def run_trial(name, cfg, X, L, Y, pool, val, steps, bs, seed, max_len):
    torch.manual_seed(seed)
    np.random.seed(seed)
    enc = build(name, cfg, max_len)
    opt = torch.optim.AdamW(enc.parameters(), lr=cfg["lr"], weight_decay=1e-4)
    sch = torch.optim.lr_scheduler.CosineAnnealingLR(opt, steps, eta_min=1e-6)
    Xt = torch.as_tensor(X[pool], dtype=torch.long, device=DEVICE)
    Lt = torch.as_tensor(L[pool], dtype=torch.long, device=DEVICE)
    Yt = torch.as_tensor(Y[pool], dtype=torch.long, device=DEVICE)
    enc.train()
    for _ in range(steps):
        b = torch.randint(0, len(pool), (min(bs, len(pool)),), device=DEVICE)
        _, lg = enc.pretrain_forward(Xt[b], Lt[b])
        loss = F.cross_entropy(lg, Yt[b])
        opt.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(enc.parameters(), 1.0)
        opt.step()
        sch.step()
    v = score(enc, X[val], L[val], Y[val])
    npar = sum(p.numel() for p in enc.parameters() if p.requires_grad)
    return enc, v, npar


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=16,
                    help="RANDOM TRIALS PER ARCHITECTURE (equal budget)")
    ap.add_argument("--steps", type=int, default=1000)
    ap.add_argument("--batch", type=int, default=128)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--max-len", type=int, default=16)
    ap.add_argument("--corpus", default="both", choices=["CAM-LDS", "COMISET", "both"])
    ap.add_argument("--comiset-pool", type=int, default=15000)
    ap.add_argument("--out", default=os.path.join(RESULTS, "phase2_hparams.json"))
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("=" * 100)
    print("  PHASE 2.4 - EQUAL-BUDGET HYPERPARAMETER SEARCH")
    print("=" * 100)
    print("  device=%s  trials/arch=%d  steps=%d  max_len=%d  seed=%d"
          % (DEVICE, args.trials, args.steps, args.max_len, args.seed))
    print("  architectures: %s" % list(SPACE))

    corpora = ["CAM-LDS", "COMISET"] if args.corpus == "both" else [args.corpus]
    rows, best = [], {}
    t0 = time.time()

    for corpus in corpora:
        print("\n  === %s ===" % corpus)
        if corpus == "CAM-LDS":
            cseqs, cscen, _ = load_camlds_verified()
            X, L, Y, S = to_windows(cseqs, max_len=args.max_len)
            trw, tew = camlds_split(cscen, S, args.seed)
            # carve a validation set out of TRAIN sequences only
            rng0 = np.random.default_rng(99)
            useqs = sorted(set(S[trw].tolist()))
            vsel = set(rng0.choice(useqs, size=max(1, len(useqs) // 5),
                                   replace=False).tolist())
            val = np.array([i for i in trw if S[i] in vsel])
            pool = np.array([i for i in trw if S[i] not in vsel])
        else:
            coseqs, _ = load_comiset_sequences()
            X, L, Y, S = to_windows(coseqs, max_len=args.max_len)
            tr, va, te = session_split(S)
            rng0 = np.random.default_rng(1000 + args.seed)
            pool = rng0.choice(tr, size=min(args.comiset_pool, len(tr)),
                               replace=False)
            val, tew = va, te
        print("    pool=%d val=%d test=%d" % (len(pool), len(val), len(tew)))

        for name in SPACE:
            rng = np.random.default_rng(hash((name, args.seed)) % (2**31))
            bv, bcfg, benc, bpar = -1.0, None, None, 0
            for t in range(args.trials):
                cfg = sample_cfg(name, rng)
                try:
                    enc, v, npar = run_trial(name, cfg, X, L, Y, pool, val,
                                             args.steps, args.batch,
                                             args.seed, args.max_len)
                except Exception as e:
                    rows.append({"corpus": corpus, "model": name, "trial": t,
                                 "cfg": cfg, "val": None, "error": str(e)[:80]})
                    continue
                rows.append({"corpus": corpus, "model": name, "trial": t,
                             "cfg": cfg, "val": v, "n_params": npar})
                if v > bv:
                    bv, bcfg, bpar = v, cfg, npar
                    benc = enc
                else:
                    del enc
            te_acc = score(benc, X[tew], L[tew], Y[tew]) if benc is not None else float("nan")
            best[(corpus, name)] = {"val": bv, "test": te_acc, "cfg": bcfg,
                                    "n_params": bpar}
            print("    %-18s best val=%.3f -> TEST=%.3f  (%s, %d params)"
                  % (name, bv, te_acc, bcfg, bpar))
            del benc

    print("\n" + "=" * 100)
    print("  BEST-BY-VALIDATION, SCORED ON HELD-OUT TEST  (equal %d trials each)"
          % args.trials)
    print("=" * 100)
    out = []
    for corpus in corpora:
        print("\n  %s" % corpus)
        print("  %-18s %8s %8s %10s   %s" % ("model", "val", "TEST", "params", "config"))
        print("  " + "-" * 92)
        gru = best[(corpus, "GRU")]["test"]
        for name in SPACE:
            b = best[(corpus, name)]
            out.append({"corpus": corpus, "model": name, **b})
            print("  %-18s %8.3f %8.3f %10d   %s"
                  % (name, b["val"], b["test"], b["n_params"], b["cfg"]))
        bt = max(best[(corpus, n)]["test"] for n in SPACE if n.startswith("Transformer"))
        print("  " + "-" * 92)
        # An exact tie must not print as "GRU still ahead" -- that mislabelled
        # the CAM-LDS result (+0.0000) on the first run.
        d = bt - gru
        verdict = ("TRANSFORMER AHEAD" if d > 1e-9 else
                   "EXACT TIE" if abs(d) <= 1e-9 else "GRU AHEAD")
        print("  best Transformer TEST %.3f  vs  tuned GRU TEST %.3f  ->  %+.4f  (%s)"
              % (bt, gru, d, verdict))

    os.makedirs(RESULTS, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"config": vars(args), "device": DEVICE,
                   "trials_per_architecture": args.trials,
                   "search_space": {k: {kk: vv for kk, vv in v.items() if kk != "cls"}
                                    for k, v in SPACE.items()},
                   "all_trials": rows, "best": out,
                   "seconds": time.time() - t0}, f, indent=1, default=float)
    print("\n  wrote -> %s (%.0fs)"
          % (os.path.relpath(args.out, HERE), time.time() - t0))
    print("=" * 100)


if __name__ == "__main__":
    main()
