# -*- coding: utf-8 -*-
"""
TEMARL v2 — Real-Corpus Encoder Training & Held-Out Evaluation
==============================================================
Closes F-DAT-09 (no real-data test of the final system) and gives F-EVL-01/02
their decisive run on REAL data rather than simulator rollouts.

THE TEST THAT MATTERS
---------------------
v1 reported held-out COMISET Top-1 = 0.341 and Top-3 = 0.715 as evidence of
"genuine, transferable representations of real enterprise attack behaviour"
(Contribution 3). Measured against the corpus marginal:

    majority class (T1574)  = 0.372     -> v1 LOST to "always predict T1574"
    top-3 frequency prior   = 0.678     -> v1 gained only +3.7pp

An encoder that cannot beat a constant predictor has not demonstrated learned
structure. This script re-runs that comparison honestly, for all three encoder
families, with a SESSION-LEVEL split (window-level splitting would leak a shared
prefix across train/test and inflate the result).

Reported for every model:
    Top-1 / Top-3 / macro-F1 / perplexity, each beside majority, frequency prior
    and uniform-perplexity references. A model is only credited if it BEATS them.
"""

import json
import os

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from data_real import (load_camlds_sequences, load_comiset_sequences,
                       restricted_support_mask, session_split, to_windows,
                       trivial_baselines)
from encoders import build_matched_suite
from vocab_v2 import ID_TO_TECHNIQUE, NUM_TECHNIQUES, tactic_of

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "results_v2")
os.makedirs(OUT, exist_ok=True)


def macro_f1(pred, true):
    f1 = []
    for c in np.unique(true):
        tp = float(((pred == c) & (true == c)).sum())
        fp = float(((pred != c) & (pred == c)).sum() + ((pred == c) & (true != c)).sum()) - 0.0
        fp = float(((pred == c) & (true != c)).sum())
        fn = float(((pred != c) & (true == c)).sum())
        f1.append(0.0 if tp == 0 else 2 * tp / (2 * tp + fp + fn))
    return float(np.mean(f1)) if f1 else 0.0


def score(enc, X, L, Y, device=DEVICE, bs=1024):
    enc.eval()
    preds, top3, nll = [], [], []
    with torch.no_grad():
        for i in range(0, len(Y), bs):
            xb = torch.as_tensor(X[i:i + bs], dtype=torch.long, device=device)
            lb = torch.as_tensor(L[i:i + bs], dtype=torch.long, device=device)
            yb = torch.as_tensor(Y[i:i + bs], dtype=torch.long, device=device)
            _, lg = enc.pretrain_forward(xb, lb)
            preds.append(lg.argmax(-1).cpu().numpy())
            k = min(3, lg.shape[-1])
            top3.append((lg.topk(k, -1).indices == yb[:, None]).any(-1).cpu().numpy())
            nll.append(F.cross_entropy(lg, yb, reduction="none").cpu().numpy())
    pred = np.concatenate(preds)
    return {"top1": float((pred == Y).mean()),
            "top3": float(np.concatenate(top3).mean()),
            "macro_f1": macro_f1(pred, Y),
            "perplexity": float(np.exp(np.concatenate(nll).mean())),
            "pred": pred}


def train_on_real(enc, X, L, Y, tr, va, steps=3000, lr=5e-4, bs=128,
                  device=DEVICE, class_weighted=True, seed=0, verbose=True):
    torch.manual_seed(seed); np.random.seed(seed)
    w = None
    if class_weighted:
        # weights must span the FULL logit dim (torch: all classes or none);
        # PAD/UNK get 0 so they can never be predicted as a next technique.
        cnt = np.bincount(Y[tr], minlength=enc.vocab_size).astype(np.float64)
        inv = np.zeros(enc.vocab_size)
        nz = cnt > 0
        inv[nz] = 1.0 / cnt[nz]
        inv[nz] /= inv[nz].mean()
        inv[NUM_TECHNIQUES:] = 0.0
        w = torch.as_tensor(inv, dtype=torch.float32, device=device)

    Xt = torch.as_tensor(X, dtype=torch.long, device=device)
    Lt = torch.as_tensor(L, dtype=torch.long, device=device)
    Yt = torch.as_tensor(Y, dtype=torch.long, device=device)
    opt = torch.optim.AdamW(enc.parameters(), lr=lr, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, steps, eta_min=1e-6)
    best, best_sd = -1.0, None
    enc.train()
    for st in range(steps):
        b = tr[np.random.randint(0, len(tr), bs)]
        _, lg = enc.pretrain_forward(Xt[b], Lt[b])
        loss = F.cross_entropy(lg, Yt[b], weight=w)
        opt.zero_grad(); loss.backward()
        nn.utils.clip_grad_norm_(enc.parameters(), 1.0)
        opt.step(); sched.step()
        if (st + 1) % max(1, steps // 6) == 0:
            m = score(enc, X[va], L[va], Y[va], device)
            if m["macro_f1"] > best:                 # select on macro-F1 (imbalance)
                best, best_sd = m["macro_f1"], {k: v.detach().clone()
                                                for k, v in enc.state_dict().items()}
            if verbose:
                print(f"      step {st+1:5d}/{steps} loss={loss.item():.4f} "
                      f"val top1={m['top1']:.3f} macroF1={m['macro_f1']:.3f}")
            enc.train()
    if best_sd:
        enc.load_state_dict(best_sd)
    enc.freeze()
    return best


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("=" * 88)
    print("  TEMARL v2 — REAL-CORPUS ENCODER TRAINING (COMISET)  [F-DAT-09]")
    print("=" * 88)

    seqs, info = load_comiset_sequences()
    X, L, Y, S = to_windows(seqs)
    tr, va, te = session_split(S)
    base = trivial_baselines(Y[tr], Y[te])
    print(f"  sessions {info['n_kept']:,}  windows {len(Y):,}  "
          f"train {len(tr):,}/val {len(va):,}/test {len(te):,}  (SESSION-level split)")
    print(f"  held-out baselines: majority Top-1 = {base['majority_top1']:.3f} "
          f"({ID_TO_TECHNIQUE[base['majority_id']]})   freq Top-3 = {base['freq_topk']:.3f}")
    print(f"  v1 reported Top-1 0.341 / Top-3 0.715  ->  LOST to majority, +3.7pp on Top-3\n")

    results = {}
    for name in ("Transformer", "GRU", "SetEncoder"):
        suite, _, _ = build_matched_suite()
        enc = suite[name].to(DEVICE)
        print(f"  --- {name} ---")
        train_on_real(enc, X, L, Y, tr, va, steps=3000, device=DEVICE, verbose=True)
        m = score(enc, X[te], L[te], Y[te], DEVICE)
        results[name] = {k: v for k, v in m.items() if k != "pred"}
        torch.save({"encoder": enc.state_dict(), "name": name},
                   os.path.join(HERE, "runs", f"real_{name}.pt"))
        print(f"      TEST top1={m['top1']:.3f} top3={m['top3']:.3f} "
              f"macroF1={m['macro_f1']:.3f} ppl={m['perplexity']:.2f}\n")

    print("=" * 88)
    print("  HELD-OUT COMISET TEST  vs  TRIVIAL BASELINES   [F-EVL-01/02 on REAL data]")
    print("=" * 88)
    print(f"  {'model':<14} {'Top-1':>8} {'vs maj':>9} {'Top-3':>8} {'vs freq':>9} "
          f"{'macroF1':>9} {'PPL':>8} {'vs unif':>9}")
    print("  " + "-" * 80)
    uni = float(list(build_matched_suite()[0].values())[0].vocab_size)
    for n, m in results.items():
        d1 = m["top1"] - base["majority_top1"]
        d3 = m["top3"] - base["freq_topk"]
        print(f"  {n:<14} {m['top1']:>8.3f} {d1:>+9.3f} {m['top3']:>8.3f} {d3:>+9.3f} "
              f"{m['macro_f1']:>9.3f} {m['perplexity']:>8.2f} "
              f"{'better' if m['perplexity'] < uni else 'WORSE':>9}")
    print(f"  {'[baseline]':<14} {base['majority_top1']:>8.3f} {'--':>9} "
          f"{base['freq_topk']:>8.3f} {'--':>9} {'--':>9} {uni:>8.1f} {'--':>9}")
    print(f"\n  {'[v1 reported]':<14} {0.341:>8.3f} {0.341-0.372:>+9.3f} "
          f"{0.715:>8.3f} {0.715-0.678:>+9.3f} {'not rep.':>9} {133.22:>8.2f} "
          f"{'WORSE':>9}   <- lost to majority")

    # ---- CAM-LDS held-out real chains (restricted support, F-DAT-08) -------
    cam = load_camlds_sequences()
    Xc, Lc, Yc, Sc = to_windows([v["ids"] for v in cam.values()])
    mask = restricted_support_mask(Yc, Y[tr])
    print(f"\n  CAM-LDS HELD-OUT REAL CHAINS (never trained on)")
    print(f"    {len(cam)} scenarios, {len(Yc)} windows; "
          f"{mask.sum()}/{len(Yc)} ({mask.mean():.1%}) within COMISET tactic support")
    print(f"    [F-DAT-08] COMISET tactics are a strict SUBSET of CAM-LDS's, so a")
    print(f"    COMISET-trained model is scored ONLY on the shared-support subset;")
    print(f"    the full-set number is reported but is NOT a generalisation result.")
    print(f"    {'model':<14} {'full-set top1':>15} {'restricted top1':>17} {'n':>6}")
    for n in results:
        enc = build_matched_suite()[0][n].to(DEVICE)
        enc.load_state_dict(torch.load(os.path.join(HERE, "runs", f"real_{n}.pt"),
                                       map_location=DEVICE)["encoder"])
        enc.freeze()
        full = score(enc, Xc, Lc, Yc, DEVICE)
        rest = score(enc, Xc[mask], Lc[mask], Yc[mask], DEVICE) if mask.sum() else None
        print(f"    {n:<14} {full['top1']:>15.3f} "
              f"{(rest['top1'] if rest else float('nan')):>17.3f} {int(mask.sum()):>6}")
    print(f"    CAVEAT: only {len(Yc)} windows from {len(cam)} chains -- wide intervals;")
    print(f"    this is a VALIDATION that the representation transfers, not a headline.")

    json.dump({"comiset_test": results, "baselines": base},
              open(os.path.join(OUT, "real_data_results.json"), "w"), indent=1)
    print(f"\n  saved -> results_v2/real_data_results.json")
    print("=" * 88)
