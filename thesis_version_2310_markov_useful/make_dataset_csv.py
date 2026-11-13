# -*- coding: utf-8 -*-
"""Export the usable CAM-LDS / AttackBed corpus to CSV.

Source of truth: thesis_system/data/camlds_grounding_verified.json
  (36 AttackMate playbooks parsed from github.com/ait-testbed/attackbed,
   1347 labelled steps; frozen in _frozen.FROZEN_SHA256).

Scenario-level deception grounding (entry zone / target host / target zone /
terminal tactic) exists ONLY in the hand-typed reconstruction
camlds_grounding.json, so it is exported to a SEPARATE file with an explicit
provenance column. Step-level rows stay source-verified.

Writes dataset_csv/:
  camlds_steps.csv       one row per attack step   (the training/eval corpus)
  camlds_scenarios.csv   one row per scenario      (grounding, mixed provenance)
  camlds_techniques.csv  one row per parent technique (union-vocab inventory)
Read-only with respect to every existing file.
"""
import csv
import json
import os
import sys
from collections import Counter

import _frozen  # puts thesis_system/temarl_v2 on sys.path
from vocab_v2 import TECHNIQUES, UNK_ID, technique_to_id
from markov_data import SOURCE, load_runs, split_runs

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "dataset_csv")
HAND = os.path.join(ROOT, "thesis_system", "data", "camlds_grounding.json")


def meta_of(code):
    """Parent-level name/tactic/vocab id for a (possibly sub-)technique code."""
    parent = code.split(".")[0]
    entry = TECHNIQUES.get(parent, {})
    vid = technique_to_id(code)
    return parent, entry.get("name", ""), entry.get("tactic", ""), vid


def main():
    verified = json.loads(open(SOURCE, encoding="utf-8").read())
    hand = json.loads(open(HAND, encoding="utf-8").read())
    scen_meta = {s["id"]: s for s in hand["scenarios"]}
    runs = load_runs()
    split, notes = split_runs(runs)
    part_of = {r["id"]: p for p, rs in split.items() for r in rs}
    group_of = {r["id"]: r["group"] for r in runs}
    os.makedirs(OUT, exist_ok=True)

    # ── steps ────────────────────────────────────────────────────────────────
    rows = []
    for name, rec in sorted(verified["runs"].items()):
        seq, tactics = rec["sequence"], rec["tactics"]
        for i, code in enumerate(seq):
            parent, pname, ptactic, vid = meta_of(code)
            nxt = seq[i + 1] if i + 1 < len(seq) else ""
            rows.append(dict(
                run_id=name,
                scenario=rec["scenario"],
                scenario_name=scen_meta.get(rec["scenario"], {}).get("name", ""),
                step_index=i,
                run_length=len(seq),
                technique=code,
                parent_technique=parent,
                is_subtechnique=int("." in code),
                technique_name=pname,
                tactic_labelled=tactics[i],
                tactic_parent_vocab=ptactic,
                vocab_id=vid,
                next_parent_technique=nxt.split(".")[0] if nxt else "",
                is_last_step=int(i + 1 == len(seq)),
                leakage_group=group_of[name][:12],
                split_seed2310=part_of[name],
            ))
    write(os.path.join(OUT, "camlds_steps.csv"), rows)

    # ── scenarios ────────────────────────────────────────────────────────────
    srows = []
    for sid, info in sorted(verified["scenarios"].items()):
        h = scen_meta.get(sid, {})
        sruns = [r for r in runs if r["scenario"] == sid]
        steps = [c for r in sruns for c in r["original"]]
        srows.append(dict(
            scenario=sid,
            name=h.get("name", ""),
            n_runs=len(sruns),
            n_independent_groups=len({r["group"] for r in sruns}),
            n_steps=len(steps),
            n_unique_parent_techniques=len({c.split(".")[0] for c in steps}),
            entry_zone=h.get("entry_zone", ""),
            target_host=h.get("target_host", ""),
            target_zone=h.get("target_zone", ""),
            terminal_tactic=h.get("terminal_tactic", ""),
            objective=h.get("objective", ""),
            grounding_provenance="hand-reconstructed from paper (NOT source-verified)",
            sequence_provenance="source-verified (AttackBed playbooks)",
            variant_files=";".join(info.get("variant_files", [])),
        ))
    write(os.path.join(OUT, "camlds_scenarios.csv"), srows)

    # ── technique inventory ──────────────────────────────────────────────────
    freq = Counter(c.split(".")[0] for r in runs for c in r["original"])
    subs = {}
    for r in runs:
        for c in r["original"]:
            subs.setdefault(c.split(".")[0], set()).add(c)
    trows = []
    for parent, n in sorted(freq.items()):
        e = TECHNIQUES.get(parent, {})
        trows.append(dict(
            parent_technique=parent,
            name=e.get("name", ""),
            tactic=e.get("tactic", ""),
            vocab_id=technique_to_id(parent),
            vocab_source=e.get("source", "unmapped"),
            n_occurrences=n,
            n_runs_present=sum(parent in {c.split(".")[0] for c in r["original"]} for r in runs),
            observed_codes=";".join(sorted(subs[parent])),
        ))
    write(os.path.join(OUT, "camlds_techniques.csv"), trows)

    unk = [r for r in rows if r["vocab_id"] == UNK_ID]
    print("steps:", len(rows), "runs:", len(verified["runs"]),
          "scenarios:", len(srows), "parent techniques:", len(trows))
    print("UNK-mapped steps:", len(unk))
    print("split counts:", {k: len(v) for k, v in split.items()})
    for n in notes:
        print("note:", n)


def write(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("wrote", os.path.relpath(path, ROOT), f"({len(rows)} rows)")


if __name__ == "__main__":
    sys.exit(main())
