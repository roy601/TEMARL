# -*- coding: utf-8 -*-
"""Upper bound on the deception decision problem for COMISET REAL vs LAB.

Uses only the technique distribution, so it needs no access to the 914 GB file.

The bound is rigorous: per-technique knowledge is the FINEST possible partition
of the corpus, so the headroom it yields is an upper bound on the headroom of
ANY clustering into campaign profiles.

    ceiling = SUM_t p(t) max_a A[t,a]   -   max_a SUM_t p(t) A[t,a]
"""
import sys

import numpy as np

from d3fend_payoff import ACTIONS, PAYOFF
from data_real import load_comiset_sequences
from vocab_v2 import NUM_TECHNIQUES, tactic_of, technique_to_id

# from the probe of the REAL archive (40,000,001 lines = 19.8% of the corpus)
REAL = {
    "T1055": 101745, "T1055.001": 6061, "T1543": 4541, "T1003": 2170,
    "T1053": 1643, "T1093": 784, "T1130": 638, "T1047": 469,
    "T1003.002": 236, "T1036": 153, "T1073": 139, "T1059.001": 128,
    "T1490": 72, "T1197": 59, "T1546.001": 57, "T1031": 35,
    "T1546.008": 21, "T1059": 13, "T1218.002": 8, "T1546.012": 8,
    "T1547.001": 7, "T1218": 6, "T1099": 6, "T1027": 5, "T1204": 4,
    "T1202": 4, "T1546.011": 4, "T1112": 3, "T1086": 3, "T1175": 3,
    "T1016": 1, "T1557": 1, "T1210": 1,
}


def ceiling(counts_by_id, label):
    d = np.zeros(NUM_TECHNIQUES)
    for i, c in counts_by_id.items():
        d[i] += c
    p = d / d.sum()
    oracle = float(sum(p[t] * PAYOFF[t].max() for t in range(NUM_TECHNIQUES) if p[t] > 0))
    ev = p @ PAYOFF
    bf = int(ev.argmax())
    print("\n%s" % label)
    print("  techniques with mass : %d" % int((p > 0).sum()))
    tac = {}
    for t in range(NUM_TECHNIQUES):
        if p[t] > 0:
            tac[tactic_of(t)] = tac.get(tactic_of(t), 0.0) + p[t]
    for k, v in sorted(tac.items(), key=lambda kv: -kv[1]):
        print("     %-22s %5.1f%%" % (k, 100 * v))
    print("  oracle (per-technique): %.4f" % oracle)
    print("  best fixed action     : %.4f  (%s)" % (ev[bf], ACTIONS[bf]))
    print("  CEILING on headroom   : %+.4f" % (oracle - ev[bf]))
    return oracle - ev[bf]


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("=" * 70)
    print("  UPPER BOUND ON HEADROOM  (per-technique oracle = finest partition)")
    print("=" * 70)

    mapped, unmapped = {}, []
    for t, c in REAL.items():
        i = technique_to_id(t)
        if i < NUM_TECHNIQUES:
            mapped[i] = mapped.get(i, 0) + c
        else:
            unmapped.append((t, c))
    tot = sum(REAL.values())
    print("REAL: %d of %d techniques map into the union vocabulary" % (len(mapped), len(REAL)))
    print("      unmapped mass: %.1f%%  %s"
          % (100 * sum(c for _, c in unmapped) / tot,
             ", ".join("%s(%d)" % (t, c) for t, c in unmapped[:12])))
    r = ceiling(mapped, "REAL ENVIRONMENT  (probe sample, 119,028 labelled records)")

    seqs, _ = load_comiset_sequences()
    lab = {}
    for s in seqs:
        for t in s:
            lab[t] = lab.get(t, 0) + 1
    l = ceiling(lab, "LAB ENVIRONMENT  (what we already use)")

    print("\n" + "=" * 70)
    print("  gate needs headroom > 0.05 ;  CAM-LDS achieves +0.2698")
    print("  REAL ceiling %+.4f   LAB ceiling %+.4f" % (r, l))
    print("  REAL measured-clustering headroom cannot exceed its ceiling.")


if __name__ == "__main__":
    main()
