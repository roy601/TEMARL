# -*- coding: utf-8 -*-
"""
PHASE 2.2 + 2.5 — Context-length and positional-encoding artefact tests
=======================================================================
TWO HYPOTHESES, tested together because they interact.

  H-2.2 CONTEXT LENGTH. The Transformer loses because MAX_SEQ_LEN = 16 is too
        short for attention to express anything a recurrence cannot. Prediction
        if true: the (Transformer - GRU) gap improves with longer context.

  H-2.5 POSITIONAL ENCODING. Absolute sinusoidal PE is the wrong choice for this
        task (it is what produced the v1 clock leak). Relative/rotary position,
        or none at all, should do better. Prediction if true: RoPE or NoPE beats
        the sinusoidal baseline at equal context.

FAIRNESS. Every variant is trained with identical steps, batch, LR schedule and
seeds, on identical pools, and evaluated on identical held-out sets. The GRU and
SetEncoder are swept over the SAME context lengths, because a context change
that helped only the Transformer's arm would be a confound rather than a result.

New encoder variants subclass the existing `TransformerIntentEncoder` contract
and are additive: `encoders.py` is not modified.

ARTEFACT-ELIMINATION experiment, not the pre-registered test.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from data_real import (load_camlds_verified, load_comiset_sequences,
                       session_split, to_windows)
from encoders import (DROPOUT, GRUIntentEncoder, IntentEncoder,
                      SetIntentEncoder, TransformerIntentEncoder)

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results_v3")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


# Rotary / no-position encoders now live in encoders_rope.py so the final
# experiment can import them without depending on an experiment module.
from encoders_rope import TransformerNoPE, TransformerRoPE


VARIANTS = {
    "Transformer-Sin": TransformerIntentEncoder,   # current baseline
    "Transformer-RoPE": TransformerRoPE,
    "Transformer-NoPE": TransformerNoPE,
    "GRU": GRUIntentEncoder,
    "SetEncoder": SetIntentEncoder,
}


# ── shared train / score ────────────────────────────────────────────────────

def score(enc, X, L, Y, bs=2048):
    enc.eval()
    top1 = 0
    with torch.no_grad():
        for i in range(0, len(Y), bs):
            xb = torch.as_tensor(X[i:i + bs], dtype=torch.long, device=DEVICE)
            lb = torch.as_tensor(L[i:i + bs], dtype=torch.long, device=DEVICE)
            yb = torch.as_tensor(Y[i:i + bs], dtype=torch.long, device=DEVICE)
            _, lg = enc.pretrain_forward(xb, lb)
            top1 += (lg.argmax(-1) == yb).sum().item()
    enc.train()
    return top1 / len(Y)


def train(name, max_len, X, L, Y, pool, steps, bs, seed, lr=5e-4):
    torch.manual_seed(seed)
    np.random.seed(seed)
    enc = VARIANTS[name](max_len=max_len).to(DEVICE)
    opt = torch.optim.AdamW(enc.parameters(), lr=lr, weight_decay=1e-4)
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
    n = sum(p.numel() for p in enc.parameters() if p.requires_grad)
    return enc, n


def camlds_split(cscen, cS, seed):
    counts = {s: cscen.count(s) for s in set(cscen)}
    elig = sorted([s for s, c in counts.items() if c >= 5],
                  key=lambda x: int(x[1:]))
    rng = np.random.default_rng(seed)
    te_seq, tr_seq = [], []
    for s in elig:
        idx = np.nonzero(np.array(cscen) == s)[0]
        p = rng.permutation(idx)
        cut = max(1, len(p) // 3)
        te_seq += list(p[:cut])
        tr_seq += list(p[cut:])
    tr_seq += [i for i, sc in enumerate(cscen) if sc not in elig]
    return (np.nonzero(np.isin(cS, tr_seq))[0],
            np.nonzero(np.isin(cS, te_seq))[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lens", type=int, nargs="*", default=[8, 16, 32, 64])
    ap.add_argument("--steps", type=int, default=1200)
    ap.add_argument("--batch", type=int, default=128)
    ap.add_argument("--seeds", type=int, nargs="*", default=[0, 1, 2])
    ap.add_argument("--comiset-pool", type=int, default=20000)
    ap.add_argument("--out", default=os.path.join(RESULTS, "phase2_seqlen_pe.json"))
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("=" * 100)
    print("  PHASE 2.2/2.5 - CONTEXT LENGTH x POSITIONAL ENCODING")
    print("=" * 100)
    print("  device=%s steps=%d batch=%d seeds=%s lens=%s"
          % (DEVICE, args.steps, args.batch, args.seeds, args.lens))

    cseqs, cscen, cinfo = load_camlds_verified()
    coseqs, coinfo = load_comiset_sequences()
    print("  CAM-LDS %d runs | COMISET %d sessions (pool %d)\n"
          % (cinfo["n_runs"], coinfo["n_kept"], args.comiset_pool))

    rows = []
    t0 = time.time()
    for corpus in ("CAM-LDS", "COMISET"):
        print("  --- %s ---" % corpus)
        for ml in args.lens:
            if corpus == "CAM-LDS":
                X, L, Y, S = to_windows(cseqs, max_len=ml)
            else:
                X, L, Y, S = to_windows(coseqs, max_len=ml)
                tr, va, te = session_split(S)
            for seed in args.seeds:
                if corpus == "CAM-LDS":
                    pool, tew = camlds_split(cscen, S, seed)
                else:
                    rng = np.random.default_rng(1000 + seed)
                    pool = rng.choice(tr, size=min(args.comiset_pool, len(tr)),
                                      replace=False)
                    tew = te
                got = {}
                for name in VARIANTS:
                    enc, npar = train(name, ml, X, L, Y, pool, args.steps,
                                      args.batch, seed)
                    a = score(enc, X[tew], L[tew], Y[tew])
                    got[name] = a
                    rows.append({"corpus": corpus, "max_len": ml, "seed": seed,
                                 "model": name, "top1": a, "n_params": npar})
                    del enc
                print("    L=%-3d seed=%d  Sin=%.3f RoPE=%.3f NoPE=%.3f "
                      "GRU=%.3f Set=%.3f   best-T minus GRU=%+.4f"
                      % (ml, seed, got["Transformer-Sin"], got["Transformer-RoPE"],
                         got["Transformer-NoPE"], got["GRU"], got["SetEncoder"],
                         max(got["Transformer-Sin"], got["Transformer-RoPE"],
                             got["Transformer-NoPE"]) - got["GRU"]))

    print("\n" + "=" * 100)
    print("  RESULTS  (mean Top-1 over %d seeds)" % len(args.seeds))
    print("=" * 100)
    summary = []
    for corpus in ("CAM-LDS", "COMISET"):
        print("\n  %s" % corpus)
        print("  %-6s %14s %14s %14s %10s %10s %12s"
              % ("len", "Trans-Sin", "Trans-RoPE", "Trans-NoPE", "GRU",
                 "SetEnc", "bestT - GRU"))
        print("  " + "-" * 88)
        for ml in args.lens:
            g = {}
            for name in VARIANTS:
                v = [r["top1"] for r in rows if r["corpus"] == corpus
                     and r["max_len"] == ml and r["model"] == name]
                g[name] = float(np.mean(v)) if v else float("nan")
            bt = max(g["Transformer-Sin"], g["Transformer-RoPE"],
                     g["Transformer-NoPE"])
            summary.append({"corpus": corpus, "max_len": ml,
                            "gap_best_T_minus_GRU": bt - g["GRU"], **g})
            print("  %-6d %14.3f %14.3f %14.3f %10.3f %10.3f %+12.4f"
                  % (ml, g["Transformer-Sin"], g["Transformer-RoPE"],
                     g["Transformer-NoPE"], g["GRU"], g["SetEncoder"],
                     bt - g["GRU"]))

    print("\n  VERDICTS")
    for corpus in ("CAM-LDS", "COMISET"):
        rs = [s for s in summary if s["corpus"] == corpus]
        gaps = [s["gap_best_T_minus_GRU"] for s in rs]
        print("    %s: gap at L=%d is %+.4f -> at L=%d is %+.4f  (%s)"
              % (corpus, rs[0]["max_len"], gaps[0], rs[-1]["max_len"], gaps[-1],
                 "IMPROVES with context" if gaps[-1] > gaps[0] + 0.005
                 else "no context benefit"))
        best_pe = max(("Transformer-Sin", "Transformer-RoPE", "Transformer-NoPE"),
                      key=lambda k: np.mean([s[k] for s in rs]))
        print("      best PE variant: %s" % best_pe)

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
