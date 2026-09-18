# -*- coding: utf-8 -*-
"""Headroom ceiling of the LAB corpus: as shipped vs as it really is.

"as shipped"  = comiset_sessions.json, produced by the v1 extractor (10 techniques)
"as it is"    = lab_technique_distribution.json, a full stream of the raw 149 GB
                file (53 techniques), with MITRE revoked-by repair applied.
"""
import json, os, sys

import numpy as np

from d3fend_payoff import ACTIONS, PAYOFF
from data_real import load_comiset_sequences
from vocab_v2 import NUM_TECHNIQUES, tactic_of, technique_to_id

HERE = os.path.dirname(os.path.abspath(__file__))
DEP = json.load(open(os.path.join(HERE, "attack_deprecation_map.json")))["revoked_to_current"]
ALIAS = {"1210": "T1210", "Port Monitors": "T1013"}


def clean(t):
    t = t.split(";")[0].strip()           # "T1055; Possible Cobalt Strike ..." 
    t = ALIAS.get(t, t)
    return t if t.startswith("T") and len(t) > 2 else None


def resolve(t, repair):
    if not repair:
        return technique_to_id(t)
    t = clean(t)
    if not t:
        return NUM_TECHNIQUES
    t = DEP.get(t, t)
    i = technique_to_id(t)
    if i >= NUM_TECHNIQUES and "." in t:
        i = technique_to_id(t.split(".")[0])
    return i


def report(counts, label, repair):
    d = np.zeros(NUM_TECHNIQUES)
    lost = 0
    for t, c in counts.items():
        i = resolve(t, repair)
        if i < NUM_TECHNIQUES:
            d[i] += c
        else:
            lost += c
    tot = sum(counts.values())
    p = d / d.sum()
    oracle = float(sum(p[t] * PAYOFF[t].max() for t in range(NUM_TECHNIQUES) if p[t] > 0))
    ev = p @ PAYOFF
    bf = int(ev.argmax())
    tac = {}
    for t in range(NUM_TECHNIQUES):
        if p[t] > 0:
            tac[tactic_of(t)] = tac.get(tactic_of(t), 0.0) + p[t]
    print("\n%s" % label)
    print("  techniques kept : %d of %d      mass discarded: %.2f%%"
          % (int((d > 0).sum()), len(counts), 100 * lost / tot))
    for k, v in sorted(tac.items(), key=lambda kv: -kv[1]):
        print("     %-22s %5.1f%%" % (k, 100 * v))
    print("  oracle %.4f | best fixed %.4f (%s) | CEILING %+.4f  %s"
          % (oracle, ev[bf], ACTIONS[bf], oracle - ev[bf],
             "PASS" if oracle - ev[bf] > 0.05 else "FAIL"))
    return oracle - ev[bf]


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    raw = dict(json.load(open(os.path.join(HERE, "lab_technique_distribution.json"))))

    print("=" * 74)
    print("  COMISET LAB — what our pipeline kept vs what the file contains")
    print("=" * 74)

    seqs, _ = load_comiset_sequences()
    shipped = {}
    for s in seqs:
        for t in s:
            shipped[t] = shipped.get(t, 0) + 1
    d = np.zeros(NUM_TECHNIQUES)
    for i, c in shipped.items():
        d[i] += c
    p = d / d.sum()
    oracle = float(sum(p[t] * PAYOFF[t].max() for t in range(NUM_TECHNIQUES) if p[t] > 0))
    ev = p @ PAYOFF
    bf = int(ev.argmax())
    print("\nAS SHIPPED (comiset_sessions.json, v1 extractor)")
    print("  techniques kept : %d" % int((d > 0).sum()))
    print("  oracle %.4f | best fixed %.4f (%s) | CEILING %+.4f  FAIL"
          % (oracle, ev[bf], ACTIONS[bf], oracle - ev[bf]))

    a = report(raw, "RAW FILE, v1-style mapping (no deprecation repair)", False)
    b = report(raw, "RAW FILE, WITH MITRE deprecation repair", True)

    print("\n" + "=" * 74)
    print("  shipped %+.4f  ->  raw %+.4f  ->  repaired %+.4f   (gate > 0.05)"
          % (oracle - ev[bf], a, b))
    print("  CAM-LDS reference: +0.2698")


if __name__ == "__main__":
    main()
