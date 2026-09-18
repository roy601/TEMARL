# -*- coding: utf-8 -*-
"""Headroom ceiling for the REAL corpus, BEFORE vs AFTER deprecation repair.

Counts are the full-corpus totals (202,304,794 lines / 631,606 labelled records).
Repair = MITRE revoked-by mapping, then fall back to the parent technique if the
sub-technique is outside our vocabulary.
"""
import json, os, sys

import numpy as np

from d3fend_payoff import ACTIONS, PAYOFF
from vocab_v2 import NUM_TECHNIQUES, tactic_of, technique_to_id

HERE = os.path.dirname(os.path.abspath(__file__))
DEP = json.load(open(os.path.join(HERE, "attack_deprecation_map.json")))["revoked_to_current"]

REAL_FULL = {
    "T1055": 517395, "T1055.001": 35633, "T1543": 32224, "T1003": 12083,
    "T1053": 7241, "T1093": 5303, "T1130": 4865, "T1047": 2746, "T1036": 2425,
    "1210": 1897, "T1003.002": 1830, "T1073": 1238, "T1059.001": 1127,
    "T1059": 875, "T1546.001": 711, "T1546.012": 658, "T1016": 480,
    "T1490": 446, "T1197": 434, "T1546.011": 407, "T1086": 184,
    "T1059.003": 153, "T1031": 131, "T1204": 118, "T1547.010": 113,
    "T1218.002": 107, "T1547.001": 104, "T1546.008": 89, "T1027": 87,
    "T1018": 67, "T1218": 52, "T1175": 51, "T1089": 47, "T1112": 44,
    "T1099": 44, "Port Monitors": 39, "T1117": 25, "T1202": 18, "T1123": 16,
    "T1033": 14, "T1210": 11, "T1064": 11, "T1557": 10, "T1218.010": 9,
    "T1127": 7, "T1070": 6, "T1553.003": 6, "T1063": 5, "T1003.004": 4,
    "T1218.011": 4, "T1057": 3, "T1049": 2, "T1170": 2, "T1005": 2,
    "T": 1, "T1021.002": 1, "T1021.003": 1,
}

ALIAS = {"1210": "T1210", "Port Monitors": "T1013"}   # label noise, resolvable


def resolve(t, repair):
    if not repair:
        return technique_to_id(t)
    t = ALIAS.get(t, t)
    if t == "T":
        return NUM_TECHNIQUES          # unresolvable
    t = DEP.get(t, t)
    i = technique_to_id(t)
    if i >= NUM_TECHNIQUES and "." in t:       # try the parent technique
        i = technique_to_id(t.split(".")[0])
    return i


def run(repair, label):
    d = np.zeros(NUM_TECHNIQUES)
    lost = 0
    for t, c in REAL_FULL.items():
        i = resolve(t, repair)
        if i < NUM_TECHNIQUES:
            d[i] += c
        else:
            lost += c
    tot = sum(REAL_FULL.values())
    p = d / d.sum()
    oracle = float(sum(p[t] * PAYOFF[t].max() for t in range(NUM_TECHNIQUES) if p[t] > 0))
    ev = p @ PAYOFF
    bf = int(ev.argmax())
    tac = {}
    for t in range(NUM_TECHNIQUES):
        if p[t] > 0:
            tac[tactic_of(t)] = tac.get(tactic_of(t), 0.0) + p[t]
    print("\n%s" % label)
    print("  techniques mapped : %d of %d" % (int((d > 0).sum()), len(REAL_FULL)))
    print("  mass discarded    : %.2f%%" % (100 * lost / tot))
    print("  tactics covered   : %d -> %s" % (len(tac), ", ".join(
        "%s %.1f%%" % (k, 100 * v) for k, v in sorted(tac.items(), key=lambda kv: -kv[1]))))
    print("  oracle %.4f | best fixed %.4f (%s) | CEILING %+.4f"
          % (oracle, ev[bf], ACTIONS[bf], oracle - ev[bf]))
    return oracle - ev[bf]


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("=" * 74)
    print("  REAL corpus, whole-corpus headroom ceiling: before vs after repair")
    print("=" * 74)
    a = run(False, "BEFORE  (v1 behaviour: unmapped ids discarded)")
    b = run(True, "AFTER   (MITRE revoked-by mapping + parent fallback)")
    print("\n  change: %+.4f -> %+.4f   (gate needs > 0.05)" % (a, b))


if __name__ == "__main__":
    main()
