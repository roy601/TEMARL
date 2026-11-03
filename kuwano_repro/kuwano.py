"""Algorithm 1 of Kuwano et al. (2023) and the evaluation procedure of its §6.2.

Exact arithmetic (fractions.Fraction) throughout, so ties and the threshold comparison
are decided on exact values, never on floating-point rounding.

Every point the paper leaves open is an explicit argument (see DECISIONS.md):
  tiebreak        D8  order among groups with equal similarity: 'name' | 'id' | 'stix'
  inclusive       D7  True: SupportRate >= threshold; False: SupportRate > threshold
  universe        D5  which techniques are candidates after the latest observed tactic
  observed_tactic D5  which tactic a multi-tactic observed technique counts as
D4 (input order) is a property of the sequence passed in, not of this module.
"""
from __future__ import annotations

import csv
import json
import os
from dataclasses import dataclass
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
DERIVED = os.path.join(HERE, "data", "derived")

K = 60
THRESHOLD = Fraction(17, 100)
TACTIC_ORDER = ["reconnaissance", "resource-development", "initial-access", "execution", "persistence",
                "privilege-escalation", "defense-evasion", "credential-access", "discovery",
                "lateral-movement", "collection", "command-and-control", "exfiltration", "impact"]
TIEBREAKS = ("name", "id", "stix")
UNIVERSES = ("any_ge", "all_ge", "any_gt", "all_gt", "everything")
OBSERVED_TACTICS = ("listed", "min", "max")


@dataclass(frozen=True)
class Data:
    techniques: tuple            # column order (sorted ids)
    tactics: dict                # technique -> tuple of tactic indices
    groups: dict                 # group id -> frozenset of techniques
    rank: dict                   # tiebreak -> {group id -> position}


def load(derived: str = DERIVED, version: str = "11.0") -> Data:
    with open(os.path.join(derived, f"matrix_v{version}.csv"), newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    techniques = tuple(rows[0][1:])
    groups = {r[0]: frozenset(t for t, v in zip(techniques, r[1:]) if v == "1") for r in rows[1:]}
    with open(os.path.join(derived, f"techniques_v{version}.csv"), newline="", encoding="utf-8") as fh:
        tactics = {r["technique"]: tuple(TACTIC_ORDER.index(x) for x in r["tactics"].split(";"))
                   for r in csv.DictReader(fh)}
    with open(os.path.join(derived, f"groups_v{version}.csv"), newline="", encoding="utf-8") as fh:
        meta = list(csv.DictReader(fh))
    rank = {
        "name": {g["group"]: i for i, g in enumerate(sorted(meta, key=lambda g: (g["name"].casefold(), g["group"])))},
        "id": {g["group"]: i for i, g in enumerate(sorted(meta, key=lambda g: g["group"]))},
        "stix": {g["group"]: int(g["stix_order"]) for g in meta},
    }
    return Data(techniques, tactics, groups, rank)


def load_sequences(derived: str = DERIVED) -> dict:
    with open(os.path.join(derived, "sequences.json"), encoding="utf-8") as fh:
        return json.load(fh)["advisories"]


def sdc(a: frozenset, b: frozenset) -> Fraction:
    """Sørensen–Dice coefficient, eq. (1)."""
    n = len(a) + len(b)
    return Fraction(2 * len(a & b), n) if n else Fraction(0)


def recommend(observed, data: Data, *, k: int = K, threshold: Fraction = THRESHOLD,
              tiebreak: str = "name", inclusive: bool = True):
    """Algorithm 1. Returns (support rate per technique, set of recommended techniques)."""
    obs = frozenset(observed)
    sim = {g: sdc(obs, T) for g, T in data.groups.items()}
    order = data.rank[tiebreak]
    top = sorted(sim, key=lambda g: (-sim[g], order[g]))[:k]
    support = {}
    for t in data.techniques:
        score = Fraction(0)
        for g in top:
            s = sim[g]
            if s != 0:
                if s == 1:   # D6: d = 0, weight undefined. The audit shows this never occurs.
                    raise ZeroDivisionError(f"Similarity 1 with group {g}; the paper defines no weight")
                if t in data.groups[g]:
                    score += 1 / (1 - s)
        support[t] = score / k
    rec = {t for t, r in support.items() if (r >= threshold if inclusive else r > threshold)}
    return support, rec


def recommend_limit(observed, data: Data, *, k: int = K, threshold: Fraction = THRESHOLD,
                    tiebreak: str = "name", inclusive: bool = True):
    """Algorithm 1 with a declared rule for Similarity = 1. For Idea 01 only.

    The paper defines no weight when d = 1 - Similarity = 0. Here the limit is taken: as
    Similarity -> 1 the weight 1/d -> infinity, so a technique's score behaves like
    n/eps + finite, where n is the number of identical neighbours using it. Each technique
    therefore gets the pair (n, SupportRate of the non-identical neighbours), compared
    lexicographically, and any technique with n > 0 is recommended.

    `recommend()` above is the validated reproduction and is left exactly as it was. When
    no neighbour has Similarity 1, every n is 0 and this function returns the same
    SupportRate and the same recommendations (asserted in tests).
    """
    obs = frozenset(observed)
    sim = {g: sdc(obs, T) for g, T in data.groups.items()}
    order = data.rank[tiebreak]
    top = sorted(sim, key=lambda g: (-sim[g], order[g]))[:k]
    scores = {}
    for t in data.techniques:
        n, score = 0, Fraction(0)
        for g in top:
            s = sim[g]
            if s != 0 and t in data.groups[g]:
                if s == 1:
                    n += 1
                else:
                    score += 1 / (1 - s)
        scores[t] = (n, score / k)
    rec = {t for t, (n, r) in scores.items()
           if n > 0 or (r >= threshold if inclusive else r > threshold)}
    return scores, rec


def tactic_of(t, listed, data: Data, how: str) -> int:
    if how == "listed":
        return TACTIC_ORDER.index(listed)
    return (min if how == "min" else max)(data.tactics[t])


def candidates(observed, listed, data: Data, *, universe: str, observed_tactic: str) -> set:
    """Techniques that count as predictions and analysis targets at this step (§4.1)."""
    obs = set(observed)
    rest = [t for t in data.techniques if t not in obs]
    if universe == "everything":
        return set(rest)
    latest = max(tactic_of(t, l, data, observed_tactic) for t, l in zip(observed, listed))
    pick = {"any": max, "all": min}[universe.split("_")[0]]
    if universe.endswith("_ge"):
        return {t for t in rest if pick(data.tactics[t]) >= latest}
    return {t for t in rest if pick(data.tactics[t]) > latest}


def evaluate(seq, listed, data: Data, *, tiebreak="name", inclusive=True,
             universe="any_ge", observed_tactic="listed", k=K, threshold=THRESHOLD):
    """§6.2: input the first i techniques (i = 1 .. N-1), score the rest. One row per i."""
    rows = []
    for i in range(1, len(seq)):
        observed, remaining = seq[:i], set(seq[i:])
        cand = candidates(observed, listed[:i], data, universe=universe, observed_tactic=observed_tactic)
        _, rec = recommend(observed, data, k=k, threshold=threshold, tiebreak=tiebreak, inclusive=inclusive)
        pred = rec & cand
        tp = len(pred & remaining)
        fp = len(pred - remaining)
        fn = len(remaining - pred)
        tn = len(cand - pred - remaining)
        rows.append({"input": i, "prediction": tp + fp, "tp": tp, "fp": fp, "tn": tn, "fn": fn,
                     "uncovered_positives": len(remaining - cand)})
    return rows
