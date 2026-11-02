"""Phase 4: every setting of the open decisions against all 48 rows of Tables 5-7.

    python validate.py            > results/VALIDATION.txt
    python validate.py --detail   (also prints every mismatched cell of the best settings)

Settings: tiebreak (D8) x inclusive (D7) x universe x observed_tactic (D5) x 174A order (D4).
A row matches only if Prediction, TP, FP, TN and FN all equal the paper's.
"""
from __future__ import annotations

import argparse
import csv
import itertools
import os
import sys

import kuwano as kw

HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = ("prediction", "tp", "fp", "tn", "fn")


def paper_rows():
    with open(os.path.join(HERE, "paper", "tables_5_7.csv"), newline="", encoding="utf-8") as fh:
        out = {}
        for r in csv.DictReader(fh):
            out.setdefault(r["report"], {})[int(r["input"])] = {f: int(r[f]) for f in FIELDS}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--detail", action="store_true")
    a = ap.parse_args()

    data, seqs, paper = kw.load(), kw.load_sequences(), paper_rows()
    orders = {"links": seqs["AA22-174A"]["variants"]["links"],
              "visible_text": seqs["AA22-174A"]["variants"]["visible_text"]}

    def cases(order174):
        for adv, v in seqs.items():
            seq, listed = v["sequence"], v["listed_tactic"]
            if adv == "AA22-174A":
                pos = {t: l for t, l in zip(seq, listed)}
                seq = orders[order174]
                listed = [pos[t] for t in seq]
            yield adv, seq, listed

    # Algorithm 1 depends only on (observed prefix, tiebreak): compute supports once.
    support = {}
    for order174, tb in itertools.product(orders, kw.TIEBREAKS):
        for adv, seq, _ in cases(order174):
            for i in range(1, len(seq)):
                key = (tuple(seq[:i]), tb)
                if key not in support:
                    support[key] = kw.recommend(seq[:i], data, tiebreak=tb)[0]

    results = []
    for order174, tb, inc, uni, ot in itertools.product(orders, kw.TIEBREAKS, (True, False),
                                                       kw.UNIVERSES, kw.OBSERVED_TACTICS):
        if uni == "everything" and ot != "listed":
            continue  # observed_tactic is irrelevant without a tactic filter
        per, cells, mism = {}, 0, []
        for adv, seq, listed in cases(order174):
            ok = 0
            for i in range(1, len(seq)):
                sup = support[(tuple(seq[:i]), tb)]
                rec = {t for t, r in sup.items() if (r >= kw.THRESHOLD if inc else r > kw.THRESHOLD)}
                cand = kw.candidates(seq[:i], listed[:i], data, universe=uni, observed_tactic=ot)
                rem = set(seq[i:])
                pred = rec & cand
                got = {"prediction": len(pred), "tp": len(pred & rem), "fp": len(pred - rem),
                       "tn": len(cand - pred - rem), "fn": len(rem - pred)}
                want = paper[adv][i]
                bad = [f for f in FIELDS if got[f] != want[f]]
                ok += not bad
                cells += len(bad)
                if bad:
                    mism.append((adv, i, {f: (want[f], got[f]) for f in bad}))
            per[adv] = ok
        results.append({"setting": dict(order174=order174, tiebreak=tb, inclusive=inc, universe=uni,
                                        observed_tactic=ot),
                        "rows": sum(per.values()), "per": per, "cells": cells, "mism": mism})

    results.sort(key=lambda r: (-r["rows"], r["cells"]))
    print(f"{len(results)} settings x 48 rows. A row matches only if all five counts match.\n")
    print(f"{'rows':>4} {'277A':>4} {'138B':>4} {'174A':>4} {'bad cells':>9}  setting")
    for r in results:
        s = r["setting"]
        print(f"{r['rows']:>4} {r['per']['AA22-277A']:>4} {r['per']['AA22-138B']:>4} {r['per']['AA22-174A']:>4} "
              f"{r['cells']:>9}  tie={s['tiebreak']:<5} {'>=' if s['inclusive'] else '> '} "
              f"univ={s['universe']:<10} obs={s['observed_tactic']:<6} 174A={s['order174']}")
    if a.detail:
        top = results[0]["rows"]
        for r in results:
            if r["rows"] < top:
                break
            print(f"\n--- mismatches for {r['setting']}  (paper, ours)")
            for adv, i, d in r["mism"]:
                print(f"  {adv} input {i:>2}: {d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
