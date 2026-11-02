"""Phase 2: raw -> data/derived/. Applies only the rules closed in DECISIONS.md.

    python preprocess.py [--raw data/raw] [--out data/derived]

Writes
  techniques_v11.0.csv  191 live parent techniques: id, name, tactics (';'-joined, ATT&CK order)
  groups_v11.0.csv      every live group: id, name, stix_order, n_techniques
  matrix_v11.0.csv      group x technique, 0/1, rows by group id, columns by technique id (D1-D3)
  sequences.json        the three test sequences in input order (D4), with the open 174A variant
  DERIVED_MANIFEST.json SHA-256 of each file above

Fails loudly if any gate in README Phase 2 is not met.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "audit"))
from audit_inputs import ADVISORIES, PRE_ACCESS, attack_id, live, load_attack, parse_advisory  # noqa: E402

VERSION = "11.0"
TACTIC_ORDER = ["reconnaissance", "resource-development", "initial-access", "execution", "persistence",
                "privilege-escalation", "defense-evasion", "credential-access", "discovery",
                "lateral-movement", "collection", "command-and-control", "exfiltration", "impact"]
EXPECT = {"techniques": 191, "AA22-277A": 26, "AA22-138B": 12, "AA22-174A": 13}


def sequence(path, tactics, tactic_names):
    """Parents in first-occurrence order, each with the tactic of the row it first appears under."""
    seq, listed = [], {}
    for tac, ids, _, _ in parse_advisory(path):
        for i in ids:
            p = i.split(".")[0]
            if p not in seq:
                seq.append(p)
                listed[p] = tactic_names[tac]
    dropped = [p for p in seq if set(tactics[p]) <= PRE_ACCESS]
    kept = [p for p in seq if p not in dropped]
    return kept, [listed[p] for p in kept], dropped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=os.path.join(HERE, "data", "raw"))
    ap.add_argument("--out", default=os.path.join(HERE, "data", "derived"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    d = load_attack(os.path.join(a.raw, f"attack_v{VERSION}", "enterprise-attack.json"))
    tech = sorted(d["parents"])
    tactics = {t: sorted(d["tactics"][t], key=TACTIC_ORDER.index) for t in tech}
    stix_order = [g for g in (o["id"] for o in d["objs"] if o["type"] == "intrusion-set")
                  if live(d["groups"][g])]
    groups = sorted(stix_order, key=lambda g: attack_id(d["groups"][g]))

    problems = []
    if len(tech) != EXPECT["techniques"]:
        problems.append(f"techniques {len(tech)} != {EXPECT['techniques']}")
    unknown = {t for g in groups for t in d["uses"][g]} - set(tech)
    if unknown:
        problems.append(f"matrix uses techniques outside the column set: {sorted(unknown)}")

    files = {}
    p = os.path.join(a.out, f"techniques_v{VERSION}.csv")
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["technique", "name", "tactics"])
        for t in tech:
            w.writerow([t, d["parents"][t]["name"], ";".join(tactics[t])])
    files["techniques"] = p

    p = os.path.join(a.out, f"groups_v{VERSION}.csv")
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["group", "name", "stix_order", "n_techniques"])
        for g in groups:
            w.writerow([attack_id(d["groups"][g]), d["groups"][g]["name"], stix_order.index(g), len(d["uses"][g])])
    files["groups"] = p

    p = os.path.join(a.out, f"matrix_v{VERSION}.csv")
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["group"] + tech)
        for g in groups:
            w.writerow([attack_id(d["groups"][g])] + [int(t in d["uses"][g]) for t in tech])
    files["matrix"] = p

    # advisory tactic cells are either "TA0002" or a header like "Command and Control"
    tactic_names = {}
    for o in d["objs"]:
        if o["type"] == "x-mitre-tactic":
            tactic_names[attack_id(o)] = o["x_mitre_shortname"]
            tactic_names[o["name"]] = o["x_mitre_shortname"]
    seqs = {}
    for adv, (rel, _) in ADVISORIES.items():
        s, listed, dropped = sequence(os.path.join(a.raw, rel), tactics, tactic_names)
        seqs[adv] = {"source": rel, "dropped_pre_access": dropped, "sequence": s,
                     "listed_tactic": listed}
        bad = [(t, l) for t, l in zip(s, listed) if l not in tactics[t]]
        if bad:
            problems.append(f"{adv}: listed under a tactic ATT&CK does not give it: {bad}")
        if len(s) != EXPECT[adv]:
            problems.append(f"{adv}: {len(s)} techniques != {EXPECT[adv]}")
        missing = [t for t in s if t not in tech]
        if missing:
            problems.append(f"{adv}: not in the column set: {missing}")
    s = seqs["AA22-174A"]["sequence"]
    i, j = s.index("T1056"), s.index("T1560")
    alt = list(s)
    alt[i], alt[j] = alt[j], alt[i]
    seqs["AA22-174A"]["variants"] = {
        "links": s,
        "visible_text": alt,
        "note": "D4 open: the two Collection rows have text and link targets swapped",
    }
    p = os.path.join(a.out, "sequences.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump({"attack_version": VERSION, "advisories": seqs}, fh, indent=2)
    files["sequences"] = p

    man = {}
    for k, p in files.items():
        with open(p, "rb") as fh:
            man[os.path.basename(p)] = hashlib.sha256(fh.read()).hexdigest()
    with open(os.path.join(a.out, "DERIVED_MANIFEST.json"), "w", encoding="utf-8") as fh:
        json.dump(man, fh, indent=2, sort_keys=True)

    ones = sum(len(d["uses"][g]) for g in groups)
    print(f"techniques {len(tech)} | live groups {len(groups)} "
          f"({sum(1 for g in groups if d['uses'][g])} non-empty) | matrix ones {ones}")
    for adv, v in seqs.items():
        print(f"{adv}: {len(v['sequence'])} techniques, dropped {v['dropped_pre_access']}")
    for f, h in man.items():
        print(f"  {f:<24} {h}")
    if problems:
        print("GATE FAILED:\n  " + "\n  ".join(problems))
        return 1
    print("Phase 2 gate: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
