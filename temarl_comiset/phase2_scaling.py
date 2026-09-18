# -*- coding: utf-8 -*-
"""
PHASE 2.1 — Data-scale artefact test (scaling curve)
=====================================================
HYPOTHESIS. The history Transformer loses to the GRU because ~1.3k training
windows is far below the regime where attention pays off, not because attention
is the wrong inductive bias for attacker-intent modelling.

PREDICTION IF TRUE. The (Transformer - GRU) Top-1 gap is strongly negative at
small N and rises monotonically toward zero or positive as N grows.

PREDICTION IF FALSE. The gap is flat or stays negative at every N.

DESIGN.
  * COMPUTE-MATCHED: every point trains for the same number of optimiser steps
    with the same batch size. Only the size of the training POOL varies, so a
    difference is attributable to data quantity, not to training length.
  * FIXED TEST SET across every N, so points are comparable.
  * Session-level split (windows from one session share a prefix, so a
    window-level split would leak).
  * Paired seeds: at each N all three encoders see the identical pool and the
    identical seed.

Phase 1 established that this corpus carries 4.006 bits of predictable
information (72.9% of H(next)), so a model that fails here is not being defeated
by an unpredictable target.

This is an ARTEFACT-ELIMINATION experiment, not the pre-registered test. It is
reported in full whichever way it falls.
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
                       session_split, to_windows, trivial_baselines)
from encoders import build_matched_suite
from vocab_v2 import NUM_TECHNIQUES

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results_v3")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODELS = ("Transformer", "GRU", "SetEncoder")


def score(enc, X, L, Y, bs=2048):
    enc.eval()
    n = len(Y)
    top1 = top3 = 0
    with torch.no_grad():
        for i in range(0, n, bs):
            xb = torch.as_tensor(X[i:i + bs], dtype=torch.long, device=DEVICE)
            lb = torch.as_tensor(L[i:i + bs], dtype=torch.long, device=DEVICE)
            yb = torch.as_tensor(Y[i:i + bs], dtype=torch.long, device=DEVICE)
            _, lg = enc.pretrain_forward(xb, lb)
            top1 += (lg.argmax(-1) == yb).sum().item()
            top3 += (lg.topk(3, -1).indices == yb[:, None]).any(-1).sum().item()
    enc.train()
    return top1 / n, top3 / n


def train_pool(name, X, L, Y, pool, steps, bs, seed, lr=5e-4):
    """Train `name` for a FIXED number of steps on a pool of the given size."""
    torch.manual_seed(seed)
    np.random.seed(seed)
    suite, _, _ = build_matched_suite()
    enc = suite[name].to(DEVICE)
    opt = torch.optim.AdamW(enc.parameters(), lr=lr, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, steps, eta_min=1e-6)
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
        sched.step()
    return enc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=1500)
    ap.add_argument("--batch", type=int, default=128)
    ap.add_argument("--seeds", type=int, nargs="*", default=[0, 1, 2])
    ap.add_argument("--sizes", type=int, nargs="*",
                    default=[500, 1000, 2000, 5000, 10000, 25000, 60000,
                             150000, 400000])
    ap.add_argument("--out", default=os.path.join(RESULTS, "phase2_scaling.json"))
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("=" * 96)
    print("  PHASE 2.1 - DATA-SCALE ARTEFACT TEST (compute-matched scaling curve)")
    print("=" * 96)
    print("  device=%s  steps=%d (FIXED)  batch=%d  seeds=%s"
          % (DEVICE, args.steps, args.batch, args.seeds))

    # ---- COMISET provides the large end of the curve --------------------
    seqs, info = load_comiset_sequences()
    X, L, Y, S = to_windows(seqs)
    tr, va, te = session_split(S)
    base = trivial_baselines(Y[tr], Y[te])
    print("  COMISET: %d sessions -> %d windows (train %d / test %d)"
          % (info["n_kept"], len(Y), len(tr), len(te)))
    print("  held-out majority Top-1 = %.3f" % base["majority_top1"])

    # ---- CAM-LDS as the small anchor, on its own held-out campaigns ------
    cseqs, cscen, cinfo = load_camlds_verified()
    cX, cL, cY, cS = to_windows(cseqs)
    print("  CAM-LDS: %d runs -> %d windows (anchor point)"
          % (cinfo["n_runs"], len(cY)))

    sizes = [n for n in args.sizes if n <= len(tr)]
    print("  pool sizes: %s\n" % sizes)

    rows = []
    t0 = time.time()
    for n in sizes:
        for seed in args.seeds:
            rng = np.random.default_rng(1000 + seed)
            pool = rng.choice(tr, size=n, replace=False)
            got = {}
            for m in MODELS:
                enc = train_pool(m, X, L, Y, pool, args.steps, args.batch, seed)
                t1, t3 = score(enc, X[te], L[te], Y[te])
                got[m] = t1
                rows.append({"corpus": "COMISET", "n": n, "seed": seed,
                             "model": m, "top1": t1, "top3": t3})
                del enc
            print("    N=%-7d seed=%d  T=%.3f G=%.3f S=%.3f   T-G=%+.4f"
                  % (n, seed, got["Transformer"], got["GRU"],
                     got["SetEncoder"],
                     got["Transformer"] - got["GRU"]))

    # ---- CAM-LDS anchor: within-scenario variant hold-out (protocol P2) ---
    print("\n  CAM-LDS anchor (within-scenario variant hold-out):")
    counts = {s: cscen.count(s) for s in set(cscen)}
    elig = sorted([s for s, c in counts.items() if c >= 5],
                  key=lambda x: int(x[1:]))
    for seed in args.seeds:
        rng = np.random.default_rng(seed)
        te_seq, tr_seq = [], []
        for s in elig:
            idx = np.nonzero(np.array(cscen) == s)[0]
            p = rng.permutation(idx)
            te_seq += list(p[:max(1, len(p) // 3)])
            tr_seq += list(p[max(1, len(p) // 3):])
        tr_seq += [i for i, sc in enumerate(cscen) if sc not in elig]
        trw = np.nonzero(np.isin(cS, tr_seq))[0]
        tew = np.nonzero(np.isin(cS, te_seq))[0]
        got = {}
        for m in MODELS:
            enc = train_pool(m, cX, cL, cY, trw, args.steps, args.batch, seed)
            t1, t3 = score(enc, cX[tew], cL[tew], cY[tew])
            got[m] = t1
            rows.append({"corpus": "CAM-LDS", "n": int(len(trw)), "seed": seed,
                         "model": m, "top1": t1, "top3": t3})
            del enc
        print("    N=%-7d seed=%d  T=%.3f G=%.3f S=%.3f   T-G=%+.4f"
              % (len(trw), seed, got["Transformer"], got["GRU"],
                 got["SetEncoder"], got["Transformer"] - got["GRU"]))

    # ---- report ----------------------------------------------------------
    print("\n" + "=" * 96)
    print("  SCALING CURVE — (Transformer - GRU) Top-1 gap vs training-pool size")
    print("=" * 96)
    print("  %-9s %9s %10s %10s %10s %12s" % ("corpus", "N", "Transf", "GRU",
                                              "SetEnc", "T - G"))
    print("  " + "-" * 66)
    curve = []
    for corpus in ("CAM-LDS", "COMISET"):
        ns = sorted({r["n"] for r in rows if r["corpus"] == corpus})
        for n in ns:
            g = {m: np.mean([r["top1"] for r in rows
                             if r["corpus"] == corpus and r["n"] == n
                             and r["model"] == m]) for m in MODELS}
            gap = g["Transformer"] - g["GRU"]
            curve.append({"corpus": corpus, "n": n, "gap": float(gap),
                          **{m: float(g[m]) for m in MODELS}})
            print("  %-9s %9d %10.3f %10.3f %10.3f %+12.4f"
                  % (corpus, n, g["Transformer"], g["GRU"], g["SetEncoder"], gap))

    com = [c for c in curve if c["corpus"] == "COMISET"]
    if len(com) >= 3:
        ns = np.log10([c["n"] for c in com])
        gaps = np.array([c["gap"] for c in com])
        slope = np.polyfit(ns, gaps, 1)[0]
        print("\n  gap vs log10(N) slope = %+.4f per decade" % slope)
        print("  first N where the gap turns non-negative: %s"
              % next((c["n"] for c in com if c["gap"] >= 0), "never in range"))
        print("  VERDICT: %s" % (
            "gap CLOSES with data -> the small-N loss is a data artefact"
            if slope > 0.005 else
            "gap does NOT close with data -> not a data-scale artefact"))

    os.makedirs(RESULTS, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"config": vars(args), "device": DEVICE,
                   "comiset_majority": base["majority_top1"],
                   "rows": rows, "curve": curve,
                   "seconds": time.time() - t0}, f, indent=1, default=float)
    print("\n  wrote -> %s  (%.0fs)"
          % (os.path.relpath(args.out, HERE), time.time() - t0))
    print("=" * 96)


if __name__ == "__main__":
    main()
