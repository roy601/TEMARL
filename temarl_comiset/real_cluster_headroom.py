# -*- coding: utf-8 -*-
"""APPROXIMATE headroom of the REAL corpus's usable chains.

Input is the printed k-means centroids from the full-pass analysis on the other
machine (top-4 techniques per cluster only), renormalised. It is therefore an
ESTIMATE, not the final number -- the exact value needs comiset_real_labelled.csv.gz.
"""
import sys

import numpy as np

from d3fend_payoff import ACTIONS, PAYOFF
from vocab_v2 import NUM_TECHNIQUES, tactic_of, technique_to_id

CLUSTERS = {
    4: [(82,  {"T1047": .27, "T1059.001": .26, "T1055.001": .15, "T1003": .09}),
        (117, {"T1053": .29, "T1003": .26, "T1059.001": .24, "T1073": .08}),
        (206, {"T1055": .36, "T1130": .19, "T1059.001": .19, "T1086": .13}),
        (191, {"T1073": .20, "T1036": .18, "T1543": .14, "T1130": .11})],
    6: [(32,  {"T1073": .32, "T1055": .31, "T1036": .14, "T1130": .08}),
        (171, {"T1073": .19, "T1036": .17, "T1543": .15, "T1130": .12}),
        (88,  {"T1055": .30, "T1130": .19, "T1059.001": .19, "T1003": .11}),
        (112, {"T1053": .30, "T1003": .27, "T1059.001": .24, "T1073": .08}),
        (111, {"T1055": .39, "T1059.001": .20, "T1130": .20, "T1086": .19}),
        (82,  {"T1047": .27, "T1059.001": .26, "T1055.001": .15, "T1003": .09})],
    8: [(44,  {"T1073": .31, "T1055": .25, "T1059.001": .12, "T1130": .11}),
        (79,  {"T1047": .28, "T1059.001": .26, "T1055.001": .16, "T1003": .09}),
        (50,  {"T1130": .25, "T1003": .11, "T1055": .08, "T1197": .06}),
        (77,  {"T1053": .33, "T1003": .31, "T1059.001": .26, "T1130": .04}),
        (87,  {"T1543": .25, "T1036": .17, "T1003": .16, "T1053": .15}),
        (47,  {"T1036": .34, "T1073": .30, "T1130": .20, "T1027": .04}),
        (33,  {"T1073": .31, "T1053": .24, "T1059.001": .24, "T1003": .15}),
        (179, {"T1055": .36, "T1059.001": .21, "T1130": .19, "T1086": .15})],
}


def vec(hist):
    d = np.zeros(NUM_TECHNIQUES)
    lost = 0.0
    for t, w in hist.items():
        i = technique_to_id(t)
        if i < NUM_TECHNIQUES:
            d[i] += w
        else:
            lost += w
    return (d / d.sum() if d.sum() > 0 else d), lost


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("=" * 72)
    print("  REAL corpus — headroom over the 596 USABLE chains (approximate)")
    print("=" * 72)
    for K, cs in CLUSTERS.items():
        tot = sum(n for n, _ in cs)
        oracle, marginal, rows = 0.0, np.zeros(PAYOFF.shape[1]), []
        for n, hist in cs:
            d, lost = vec(hist)
            if d.sum() == 0:
                continue
            p = n / tot
            ev = d @ PAYOFF
            best = int(ev.argmax())
            oracle += p * ev[best]
            marginal += p * ev
            rows.append((n, ACTIONS[best], ev[best],
                         sorted({tactic_of(i) for i in np.nonzero(d)[0]}), lost))
        bf = int(marginal.argmax())
        print("\nK=%d" % K)
        for n, an, v, tacs, lost in rows:
            print("   n=%4d  a*=%-22s value=%.3f  unmapped=%.0f%%  tactics=%s"
                  % (n, an, v, 100 * lost, ", ".join(tacs)))
        print("   oracle %.4f | best fixed %.4f (%s) | HEADROOM %+.4f  %s"
              % (oracle, marginal[bf], ACTIONS[bf], oracle - marginal[bf],
                 "PASS" if oracle - marginal[bf] > 0.05 else "FAIL (gate needs >0.05)"))
        print("   distinct optimal decoys: %d" % len({r[1] for r in rows}))

    print("\nreference: CAM-LDS +0.2698 | COMISET LAB +0.0423 | REAL whole-corpus ceiling +0.0418")


if __name__ == "__main__":
    main()
