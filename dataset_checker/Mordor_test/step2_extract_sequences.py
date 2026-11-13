#!/usr/bin/env python3
"""
step2_extract_sequences.py
==========================
Parse downloaded Mordor metadata (YAML) and log files (JSON) to produce
ordered ATT&CK technique sequences.

Sources of ordering (used in priority order)
---------------------------------------------
1. ``simulation.steps`` in YAML    explicit stepid ordering.
2. ``attack_mappings`` is an unordered inventory, exported separately.
Log timestamp helpers are not used to infer scenario ownership or attack order.

Output
------
``output/sequences.json``  list of sequence records:

    {
      "scenario":   "apt29/day1",
      "source":     "evaluation_steps",
      "techniques": ["T1566.001", "T1204.002", ],
      "length":     27,
      "tactics":    ["initial-access", "execution", ]
    }
"""

import glob
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

import config

#  YAML metadata parsing 

def _full_technique_id(entry: dict) -> Optional[str]:
    """Build 'T1059.001' from an attack_mappings entry."""
    if not isinstance(entry, dict):
        return None
    tid = str(entry.get("technique") or "")
    if not tid:
        return None
    # Normalise: strip whitespace, ensure uppercase T
    tid = tid.strip()
    if not tid.upper().startswith("T"):
        return None
    tid = tid.upper()
    sub = entry.get("sub_technique") or entry.get("sub-technique") or ""
    sub = str(sub).strip().lstrip(".")
    if sub and "." not in tid:
        tid = f"{tid}.{sub.zfill(3)}"
    return tid if re.fullmatch(r"T\d{4}(?:\.\d{3})?", tid) else None


def extract_from_simulation_steps(meta: dict) -> Optional[List[dict]]:
    """
    If the YAML has ``simulation.steps`` with explicit ordering, return
    an ordered list of {technique, tactic, step_id, description}.
    """
    sim = meta.get("simulation", {})
    if not isinstance(sim, dict):
        return None
    steps = sim.get("steps", [])
    if not isinstance(steps, list) or not steps:
        return None

    results = []
    for s in steps:
        tid = _full_technique_id(s)
        if not tid:
            return None  # Do not silently bridge missing or invalid steps.
        tid = tid.strip().upper()
        results.append({
            "technique": tid,
            "tactic": s.get("tactic", "unknown"),
            "step_id": str(s.get("step_id") or ""),
            "description": s.get("description", ""),
        })

    if not results:
        return None

    # Sort by step_id if present (e.g. "1.A.1", "2.B.3")
    def step_sort_key(item):
        parts = re.split(r"[.\-]", item.get("step_id", "0"))
        key = []
        for p in parts:
            p = p.strip()
            if p.isdigit():
                key.append((0, int(p), ""))
            else:
                key.append((1, 0, p))
        return key

    # Preserve declared list order when identifiers are absent or incomplete.
    if all(s["step_id"] for s in results):
        if len({s["step_id"] for s in results}) != len(results):
            return None  # Multiple techniques on one step have no internal order.
        results.sort(key=step_sort_key)
    return results


def extract_from_attack_mappings(meta: dict) -> Optional[List[dict]]:
    """
    Read the ``attack_mappings`` inventory. List order is not chronology.
    """
    mappings = meta.get("attack_mappings", [])
    if not mappings:
        return None

    results = []
    seen = set()
    for m in mappings:
        tid = _full_technique_id(m)
        if not tid or tid in seen:
            continue
        seen.add(tid)
        tactics = m.get("tactics", [m.get("tactic", "unknown")])
        if isinstance(tactics, list) and tactics:
            tactic = tactics[0]
        else:
            tactic = str(tactics)
        results.append({
            "technique": tid,
            "tactic": tactic,
            "step_id": "",
            "description": "",
        })
    return results if results else None


#  JSON logfile timestamp extraction 

def process_yaml_file(yaml_path: str) -> Optional[dict]:
    """
    Process a single YAML metadata file and return a sequence record.
    """
    if "_evaluation_steps" in Path(yaml_path).parts:
        return None
    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            meta = yaml.safe_load(f)
    except Exception as exc:
        print(f"  [WARN] Cannot parse {yaml_path}: {exc}")
        return None

    if not isinstance(meta, dict):
        return None
    if str(meta.get("source", "")).startswith("MITRE ATT&CK Evaluation ("):
        return None  # Legacy locally generated examples, including relocated copies.

    title = meta.get("title", os.path.basename(yaml_path))

    #  try simulation steps first 
    steps = extract_from_simulation_steps(meta)
    source = "simulation_steps"

    #  fallback to attack_mappings 
    if not steps:
        steps = extract_from_attack_mappings(meta)
        source = "attack_mappings"

    if not steps:
        return None

    techniques = [s["technique"] for s in steps]
    tactics    = [s["tactic"] for s in steps]

    # Deduplicate consecutive duplicates (same technique backtoback)
    deduped_techniques = [techniques[0]]
    deduped_tactics    = [tactics[0]]
    for i in range(1, len(techniques)):
        if techniques[i] != techniques[i - 1]:
            deduped_techniques.append(techniques[i])
            deduped_tactics.append(tactics[i])

    return {
        "schema_version": 2,
        "ordered": source == "simulation_steps",
        "evidence": "declared_simulation_order" if source == "simulation_steps" else "unordered_metadata_mapping",
        "scenario": title,
        "yaml_file": yaml_path,
        "source": source,
        "techniques_raw": techniques,
        "techniques": deduped_techniques,
        "tactics": deduped_tactics,
        "length": len(deduped_techniques),
        "length_raw": len(techniques),
        "steps_detail": steps,
    }


def process_all_scenarios() -> List[dict]:
    """Walk ``data/`` and extract sequences from every YAML file."""
    sequences: List[dict] = []

    if not os.path.isdir(config.DATA_DIR):
        print(f"[ERR] Data directory not found: {config.DATA_DIR}")
        print("      Run step1_download_mordor.py first.")
        return sequences

    yaml_files = (
        glob.glob(os.path.join(config.DATA_DIR, "**", "*.yaml"), recursive=True)
        + glob.glob(os.path.join(config.DATA_DIR, "**", "*.yml"), recursive=True)
    )

    print(f"\n Found {len(yaml_files)} YAML file(s) in {config.DATA_DIR}")

    for yf in sorted(yaml_files):
        if Path(yf).resolve().is_relative_to(Path(config.OUTPUT_DIR).resolve()):
            continue
        print(f"  Processing: {os.path.relpath(yf, config.DATA_DIR)}")
        record = process_yaml_file(yf)
        if record:
            separator = "  " if record["ordered"] else ", "
            seq_str = separator.join(record["techniques"][:8])
            if len(record["techniques"]) > 8:
                seq_str += separator + ""
            print(f"     {record['length']} techniques  ({record['source']})")
            print(f"      {seq_str}")
            sequences.append(record)
        else:
            print(f"     No technique sequence extracted")

    return sequences


#  optional: enrich with log timestamps 

def run_extraction():
    """Extract all sequences and save to output/sequences.json."""
    sequences = process_all_scenarios()

    # Nearby logs are not evidence of ownership or of technique chronology.
    # Keep mappings as inventories, without promoting list order to attack order.
    inventories = [s for s in sequences if not s["ordered"]]
    sequences = [s for s in sequences if s["ordered"]]

    #  save 
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(config.OUTPUT_DIR, "sequences.json")

    # Strip nonserialisable fields for clean JSON
    export = []
    for seq in sequences:
        export.append({
            "schema_version": 2,
            "ordered": True,
            "evidence": seq["evidence"],
            "yaml_file": seq["yaml_file"],
            "scenario":           seq["scenario"],
            "source":             seq["source"],
            "techniques":         seq["techniques"],
            "techniques_raw":     seq["techniques_raw"],
            "tactics":            seq["tactics"],
            "length":             seq["length"],
            "length_raw":         seq["length_raw"],
            "log_first_event":    seq.get("log_first_event"),
            "log_last_event":     seq.get("log_last_event"),
            "log_event_count":    seq.get("log_event_count"),
            "log_technique_matches": seq.get("log_technique_matches"),
        })

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(export, f, indent=2, default=str)
    with open(os.path.join(config.OUTPUT_DIR, "capture_inventory.json"), "w", encoding="utf-8") as f:
        json.dump(inventories, f, indent=2)
    excluded = list(Path(config.DATA_DIR).rglob("_evaluation_steps/*.yaml"))
    with open(os.path.join(config.OUTPUT_DIR, "extraction_audit.json"), "w", encoding="utf-8") as f:
        json.dump({"ordered_sequences": len(export), "unordered_captures": len(inventories),
                   "excluded_builtin_files": [str(p) for p in excluded]}, f, indent=2)
    print(f"\n {len(export)} sequence(s) saved  {out_path}")


if __name__ == "__main__":
    run_extraction()
