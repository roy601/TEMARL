# -*- coding: utf-8 -*-
"""EXPLORATORY instrument check for COMISET-grounded deception.

Not pre-registered. Its only job is to answer, BEFORE any hypothesis is
declared, whether COMISET can support the deception decision problem at all:

  1. does COMISET cover enough tactics for the D3FEND decoy classes to differ?
  2. do clustered campaign profiles have DISTINCT optimal decoys (headroom > 0)?
  3. does the attacker's technique history carry information beyond the
     campaign-class label (the v4 failure mode)?

If (2) or (3) fails, a COMISET DSR comparison would be uninterpretable in
exactly the way v4 was, and no amount of training would fix it.
"""

from __future__ import annotations

import sys

import numpy as np
from sklearn.cluster import KMeans

from d3fend_payoff import ACTIONS, PAYOFF, consolidate_intent_classes, headroom
from data_real import load_camlds_sequences, load_comiset_sequences
from vocab_v2 import NUM_TECHNIQUES, ID_TO_TECHNIQUE, tactic_of

K_GRID = (2, 3, 4, 5, 6, 7, 8)
SEED = 0
PATH = None            # set by --path; None = the shipped v1 corpus


def histograms(seqs):
    H = np.zeros((len(seqs), NUM_TECHNIQUES))
    for i, s in enumerate(seqs):
        for t in s:
            H[i, t] += 1.0
    return H / np.maximum(H.sum(1, keepdims=True), 1e-9)


def mutual_information(pairs):
    """I(next; prev) in bits, from observed bigrams."""
    if not pairs:
        return 0.0
    joint = {}
    for a, b in pairs:
        joint[(a, b)] = joint.get((a, b), 0) + 1
    n = sum(joint.values())
    pa, pb = {}, {}
    for (a, b), c in joint.items():
        pa[a] = pa.get(a, 0) + c
        pb[b] = pb.get(b, 0) + c
    mi = 0.0
    for (a, b), c in joint.items():
        pab = c / n
        mi += pab * np.log2(pab / ((pa[a] / n) * (pb[b] / n)))
    return float(mi)


def class_label_value(dists, probs):
    """Payoff of knowing the campaign class vs the best fixed action."""
    h = headroom(dists, probs)
    return h


def sequence_value(seqs, labels, dists, probs):
    """Payoff of a PERFECT next-technique oracle MINUS payoff of the class label.

    This is the v4 diagnostic: if it is ~0, the optimal decoy is a function of
    the class label alone and no history model can be distinguished.
    """
    perfect = 0.0
    n = 0
    for s in seqs:
        for t in s[1:]:
            perfect += PAYOFF[t].max()
            n += 1
    perfect = perfect / max(n, 1)

    # value of acting on the class label alone, on the same transitions
    per_class_action = {}
    for c, d in dists.items():
        per_class_action[c] = int((np.asarray(d) @ PAYOFF).argmax())
    lab = 0.0
    n2 = 0
    for s, c in zip(seqs, labels):
        a = per_class_action[c]
        for t in s[1:]:
            lab += PAYOFF[t, a]
            n2 += 1
    lab = lab / max(n2, 1)
    return perfect, lab, perfect - lab


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default=None)
    args, _ = ap.parse_known_args()
    seqs, info = (load_comiset_sequences(path=args.path) if args.path
                  else load_comiset_sequences())
    print("corpus:", args.path or "shipped comiset_sessions.json")
    print("=" * 74)
    print("  COMISET GROUNDING CHECK  (exploratory, not pre-registered)")
    print("=" * 74)
    print("sequences kept      :", info["n_kept"], "of", info["n_raw_sessions"])
    lens = np.array([len(s) for s in seqs])
    print("length  mean/med/max: %.2f / %d / %d" % (lens.mean(), np.median(lens), lens.max()))

    present = sorted({t for s in seqs for t in s})
    tactics = sorted({tactic_of(t) for t in present})
    print("techniques present  :", len(present), [ID_TO_TECHNIQUE[t] for t in present])
    print("tactics present     :", len(tactics), tactics)

    cam = load_camlds_sequences()
    cam_tac = sorted({tactic_of(t) for v in cam.values() for t in v["ids"]})
    print("CAM-LDS tactics     :", len(cam_tac), cam_tac)
    print("COMISET-only tactics:", sorted(set(tactics) - set(cam_tac)))

    print("\n--- 1. does history carry information? -------------------------")
    pairs = [(a, b) for s in seqs for a, b in zip(s, s[1:])]
    print("I(next;prev) over all COMISET bigrams : %.3f bits  (n=%d)"
          % (mutual_information(pairs), len(pairs)))

    print("\n--- 2. clustering into campaign profiles -----------------------")
    H = histograms(seqs)
    print(" K  classes  oracle  best_fixed   delta   distinct optimal decoys")
    best = None
    for K in K_GRID:
        km = KMeans(n_clusters=K, n_init=10, random_state=SEED).fit(H)
        labels = km.labels_
        dists, probs = {}, {}
        for c in range(K):
            m = labels == c
            if m.sum() == 0:
                continue
            d = H[m].sum(0)
            if d.sum() <= 0:
                continue
            dists[c] = d
            probs[c] = float(m.mean())
        h = headroom(dists, probs)
        con = consolidate_intent_classes(dists, probs)
        opt = sorted({ACTIONS[v["a_star"]] for v in h["per_profile"].values()})
        print(" %2d    %2d     %.4f   %.4f    %+.4f   %s"
              % (K, con["n_classes"], h["oracle"], h["best_fixed"], h["delta"],
                 ", ".join(opt)))
        if best is None or h["delta"] > best[1]["delta"]:
            best = (K, h, con, labels, dists, probs)

    K, h, con, labels, dists, probs = best
    print("\n--- 3. sequence value at the best K (K=%d) ---------------------" % K)
    perfect, lab, gain = sequence_value(seqs, labels, dists, probs)
    print("perfect next-technique oracle payoff : %.4f" % perfect)
    print("campaign-class-label payoff          : %.4f" % lab)
    print("SEQUENCE VALUE (oracle - label)      : %+.4f" % gain)
    print("   v5 CAM-LDS reference             : +0.1776 payoff")
    print("   v4 degenerate reference          : +0.0002 payoff")

    print("\n--- verdict ----------------------------------------------------")
    ok_decide = h["delta"] > 0.05 and con["n_classes"] >= 2
    ok_seq = gain > 0.02
    print("decision problem exists (delta>0.05, >=2 classes) :", ok_decide)
    print("history worth modelling (seq value>0.02)          :", ok_seq)
    if not (ok_decide and ok_seq):
        print("\n=> COMISET grounding would reproduce the v4 failure mode.")
    else:
        print("\n=> COMISET can support a DSR comparison; pre-register next.")


if __name__ == "__main__":
    main()
