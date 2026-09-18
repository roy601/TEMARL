# -*- coding: utf-8 -*-
"""Run the pre-registered COMISET Lab encoder comparison (prereg_comiset.py).

    python run_comiset_encoders.py --smoke     # 2 arms x 1 seed x 200 steps
    python run_comiset_encoders.py             # the declared run

Writes results_comiset/encoders_comiset.json. Resumable: completed (arm, seed)
cells are skipped, so an interrupted run continues where it stopped.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time

import numpy as np
import torch

import prereg_comiset as PR
from data_real import load_comiset_sequences, session_split, to_windows
from device_util import pick_device
from encoders import GRUIntentEncoder, LSTMIntentEncoder, SetIntentEncoder
from encoders_rope import TransformerRoPE
from vocab_v2 import NUM_TECHNIQUES

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results_comiset")
OUT = os.path.join(RESULTS, "encoders_comiset.json")

BUILD = {"Transformer-RoPE": TransformerRoPE, "GRU": GRUIntentEncoder,
         "LSTM": LSTMIntentEncoder, "SetEncoder": SetIntentEncoder}


def corpus(path):
    """Expand the shipped .gz and REFUSE to run against a stale expansion.

    A machine that already held an older comiset_lab_sessions.json silently ran
    the whole experiment on the pre-repair corpus, because the original code
    only expanded the .gz when the .json was absent. The .gz in the repository
    is the single source of truth, so its metadata is compared against whatever
    is on disk and the file is rewritten whenever they differ.
    """
    gz = path + ".gz"
    if os.path.exists(gz):
        import gzip
        want = json.loads(gzip.decompress(open(gz, "rb").read()))["metadata"]
        have = None
        if os.path.exists(path):
            try:
                have = json.load(open(path, encoding="utf-8"))["metadata"]
            except Exception:
                have = None
        keys = ("sessions", "distinct_techniques", "total_labeled_records")
        if have is None or any(have.get(k) != want.get(k) for k in keys):
            if have is not None:
                print("!! on-disk corpus does not match the shipped .gz "
                      "(%s vs %s sessions) -- replacing it"
                      % (have.get("sessions"), want.get("sessions")))
            print("expanding", os.path.basename(gz))
            with gzip.open(gz, "rb") as src, open(path, "wb") as dst:
                import shutil
                shutil.copyfileobj(src, dst)

    seqs, info = load_comiset_sequences(path=path)
    X, L, Y, S = to_windows(seqs, max_len=PR.MAX_LEN)
    return X, L, Y, S, info


def fingerprint(path, info, n_windows):
    """Identifies the corpus a result was produced from."""
    h = hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]
    return {"sha256_16": h, "sessions_kept": int(info["n_kept"]),
            "n_windows": int(n_windows)}


def metrics(enc, X, L, Y, device, bs=2048):
    enc.eval()
    top1 = top3 = 0
    nll = 0.0
    preds = np.zeros(len(Y), dtype=np.int64)
    with torch.no_grad():
        for i in range(0, len(Y), bs):
            xb = torch.as_tensor(X[i:i + bs], dtype=torch.long, device=device)
            lb = torch.as_tensor(L[i:i + bs], dtype=torch.long, device=device)
            yb = torch.as_tensor(Y[i:i + bs], dtype=torch.long, device=device)
            _, lg = enc.pretrain_forward(xb, lb)
            top1 += (lg.argmax(-1) == yb).sum().item()
            k = min(3, lg.shape[-1])
            top3 += (lg.topk(k, -1).indices == yb.unsqueeze(1)).any(1).sum().item()
            nll += torch.nn.functional.cross_entropy(lg, yb, reduction="sum").item()
            preds[i:i + bs] = lg.argmax(-1).cpu().numpy()
    enc.train()
    f1s = []
    for c in np.unique(Y):
        tp = float(((preds == c) & (Y == c)).sum())
        fp = float(((preds == c) & (Y != c)).sum())
        fn = float(((preds != c) & (Y == c)).sum())
        denom = 2 * tp + fp + fn
        if denom > 0:
            f1s.append(2 * tp / denom)
    n = len(Y)
    return {"top1": top1 / n, "top3": top3 / n,
            "macro_f1": float(np.mean(f1s)) if f1s else 0.0,
            "perplexity": float(np.exp(nll / n))}


def bigram_baseline(Xtr, Ltr, Ytr, Xte, Lte, Yte):
    """Empirical P(next | previous technique), fitted on TRAIN only."""
    T = np.zeros((NUM_TECHNIQUES, NUM_TECHNIQUES))
    for x, l, y in zip(Xtr, Ltr, Ytr):
        T[x[l - 1], y] += 1.0
    fallback = int(np.bincount(Ytr, minlength=NUM_TECHNIQUES).argmax())
    pred = np.array([int(T[x[l - 1]].argmax()) if T[x[l - 1]].sum() > 0 else fallback
                     for x, l in zip(Xte, Lte)])
    return float((pred == Yte).mean())


def train_one(name, seed, X, L, Y, S, device, steps, batch):
    torch.manual_seed(seed)
    np.random.seed(seed)
    tr, va, te = session_split(S, frac=PR.SPLIT_FRAC, seed=seed)

    enc = BUILD[name](max_len=PR.MAX_LEN).to(device)
    n_params = sum(p.numel() for p in enc.trunk_parameters())
    opt = torch.optim.AdamW(enc.parameters(), lr=PR.LR, weight_decay=PR.WEIGHT_DECAY)
    sch = torch.optim.lr_scheduler.CosineAnnealingLR(opt, steps, eta_min=1e-6)

    Xt = torch.as_tensor(X[tr], dtype=torch.long, device=device)
    Lt = torch.as_tensor(L[tr], dtype=torch.long, device=device)
    Yt = torch.as_tensor(Y[tr], dtype=torch.long, device=device)

    t0 = time.time()
    best_val, best_state = -1.0, None
    enc.train()
    for step in range(1, steps + 1):
        b = torch.randint(0, len(tr), (min(batch, len(tr)),), device=device)
        _, lg = enc.pretrain_forward(Xt[b], Lt[b])
        loss = torch.nn.functional.cross_entropy(lg, Yt[b])
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(enc.parameters(), 1.0)
        opt.step()
        sch.step()
        if step % PR.EVAL_EVERY == 0 or step == steps:
            v = metrics(enc, X[va], L[va], Y[va], device)["top1"]
            if v > best_val:
                best_val = v
                best_state = {k: t.detach().clone()
                              for k, t in enc.state_dict().items()}
    secs = time.time() - t0
    if best_state is not None:
        enc.load_state_dict(best_state)

    m = metrics(enc, X[te], L[te], Y[te], device)
    maj = int(np.bincount(Y[tr], minlength=NUM_TECHNIQUES).argmax())
    m.update({"params": int(n_params), "seconds": round(secs, 1),
              "val_top1": best_val,
              "majority": float((Y[te] == maj).mean()),
              "bigram": bigram_baseline(X[tr], L[tr], Y[tr], X[te], L[te], Y[te]),
              "n_train": int(len(tr)), "n_test": int(len(te))})
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--corpus", default=PR.CORPUS)
    ap.add_argument("--device", default=None, help="cpu | cuda | xpu")
    ap.add_argument("--arms", nargs="*", default=None)
    args = ap.parse_args()

    if args.device:
        os.environ["TEMARL_DEVICE"] = args.device
    device = pick_device(prefer_xpu=True)

    arms = args.arms or PR.ARMS
    seeds = PR.SEEDS
    steps, batch = PR.STEPS, PR.BATCH
    if args.smoke:
        arms, seeds, steps = arms[:2], [0], 200

    path = args.corpus if os.path.isabs(args.corpus) else os.path.join(HERE, args.corpus)
    X, L, Y, S, info = corpus(path)
    print("device      :", device)
    print("corpus      :", path)
    print("sessions    :", info["n_kept"], "| windows:", len(Y))
    print("arms        :", arms, "| seeds:", len(seeds), "| steps:", steps)

    fp = fingerprint(path, info, len(Y))
    print("corpus id   :", fp)

    os.makedirs(RESULTS, exist_ok=True)
    out = {"prereg": "prereg_comiset.py", "smoke": args.smoke, "device": str(device),
           "corpus": os.path.basename(path), "n_windows": int(len(Y)),
           "n_sessions": int(info["n_kept"]), "steps": steps, "batch": batch,
           "corpus_fingerprint": fp, "results": {}}
    if os.path.exists(OUT) and not args.smoke:
        try:
            prev = json.load(open(OUT, encoding="utf-8"))
        except Exception:
            prev = None
        if prev is not None:
            old_fp = prev.get("corpus_fingerprint")
            if old_fp != fp:
                raise SystemExit(
                    "\nREFUSING TO CONTINUE: %s holds results from a DIFFERENT "
                    "corpus.\n  on disk now : %s\n  in results  : %s\n"
                    "Those cells are not comparable with the ones this run would "
                    "add.\nDelete or rename the file and start the run again:\n"
                    "    del results_comiset\\encoders_comiset.json\n" % (OUT, fp, old_fp))
            if prev.get("steps") != steps:
                raise SystemExit(
                    "\nREFUSING TO CONTINUE: existing results used steps=%s, this "
                    "run uses steps=%s.\nDelete the file and start again."
                    % (prev.get("steps"), steps))
            out = prev
            out.setdefault("results", {})

    for arm in arms:
        out["results"].setdefault(arm, {})
        for seed in seeds:
            if str(seed) in out["results"][arm]:
                print("  skip %-18s seed %d (done)" % (arm, seed))
                continue
            t0 = time.time()
            m = train_one(arm, seed, X, L, Y, S, device, steps, batch)
            out["results"][arm][str(seed)] = m
            print("  %-18s seed %d  top1 %.4f  top3 %.4f  f1 %.3f  "
                  "maj %.4f  bigram %.4f  params %d  %.0fs"
                  % (arm, seed, m["top1"], m["top3"], m["macro_f1"],
                     m["majority"], m["bigram"], m["params"], time.time() - t0))
            if not args.smoke:
                json.dump(out, open(OUT, "w", encoding="utf-8"), indent=1)

    if not args.smoke:
        json.dump(out, open(OUT, "w", encoding="utf-8"), indent=1)
        print("\nwrote", OUT)
    else:
        print("\nsmoke test complete (nothing written)")


if __name__ == "__main__":
    main()
