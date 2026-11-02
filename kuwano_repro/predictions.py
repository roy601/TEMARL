"""List the techniques the validated method predicts at every step of every advisory.

    python predictions.py      -> results/PREDICTIONS.csv and results/PREDICTIONS.md

Uses the settings closed in DECISIONS.md (the defaults of kuwano.py) and the 174A
visible-text order. Each predicted technique is listed with its support rate and whether
the advisory really goes on to use it.
"""
from __future__ import annotations

import csv
import os
import sys

import kuwano as kw

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "results")


def main():
    data, seqs = kw.load(), kw.load_sequences()
    with open(os.path.join(kw.DERIVED, "techniques_v11.0.csv"), newline="", encoding="utf-8") as fh:
        names = {r["technique"]: r["name"] for r in csv.DictReader(fh)}
    os.makedirs(OUT, exist_ok=True)
    rows, md = [], ["# Predictions of the reproduced method", "",
                    "Settings: DECISIONS.md (v11.0, k = 60, threshold 0.17, tie-break by name, universe any_ge). "
                    "174A in visible-text order. ✓ = the advisory really uses it later. "
                    "Support rates are rounded here only; the method uses exact values.", ""]
    for adv, v in seqs.items():
        seq = v["variants"]["visible_text"] if "variants" in v else v["sequence"]
        pos = dict(zip(v["sequence"], v["listed_tactic"]))
        listed = [pos[t] for t in seq]
        md += [f"## {adv}", "", f"Sequence ({len(seq)}): {' '.join(seq)}", "",
               "| Inputs | Latest input | Predicted (✓ = used later) | TP | FP | FN | Missed |",
               "|---|---|---|---|---|---|---|"]
        for i in range(1, len(seq)):
            sup, rec = kw.recommend(seq[:i], data)
            cand = kw.candidates(seq[:i], listed[:i], data, universe="any_ge", observed_tactic="listed")
            rem = set(seq[i:])
            pred = sorted(rec & cand, key=lambda t: (-sup[t], t))
            for t in pred:
                rows.append({"advisory": adv, "inputs": i, "technique": t, "name": names[t],
                             "support_rate": f"{float(sup[t]):.6f}", "used_later": int(t in rem)})
            hits = [t for t in pred if t in rem]
            missed = sorted(rem - set(pred))
            cell = ", ".join(f"{t}{' ✓' if t in rem else ''}" for t in pred)
            md.append(f"| {i} | {seq[i - 1]} {names[seq[i - 1]]} | {cell} | {len(hits)} | "
                      f"{len(pred) - len(hits)} | {len(missed)} | {' '.join(missed)} |")
        md.append("")
    with open(os.path.join(OUT, "PREDICTIONS.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(OUT, "PREDICTIONS.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")
    print(f"{len(rows)} predictions written to results/PREDICTIONS.csv and .md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
