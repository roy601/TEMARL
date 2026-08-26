# extract_comiset_sessions.py
"""
COMISET Session Extractor
==========================
Streams dataset_comillas2.json (149 GB NDJSON), extracts only records
with rule_technique_id, groups by process_guid into behavioral chains,
maps sub-techniques to vocab IDs, collapses consecutive duplicates,
and writes comiset_sessions.json.

Run once. Output is ~10-50 MB. Takes 30-90 minutes on SSD.

Usage:
    python extract_comiset_sessions.py

Output:
    data/comiset_sessions.json

Output format:
    {
      "metadata": {
        "total_lines_read": int,
        "total_labeled_records": int,
        "sessions_before_filter": int,
        "sessions_after_filter": int,
        "technique_distribution": {technique_id_str: count},
        "avg_sequence_length": float,
        "extraction_time_seconds": float
      },
      "sessions": {
        "<process_guid>": {
          "host_name": str,
          "user_account": str,
          "first_seen": str,
          "last_seen": str,
          "raw_techniques": [str, ...],
          "sequence": [int, ...],
          "padded_sequence": [int, ...]
        },
        ...
      }
    }
"""

import json
import os
import time
from collections import defaultdict, Counter
from datetime import datetime

from mitre_techniques import (
    technique_to_id,
    PAD_ID,
    UNK_ID,
    MAX_SEQ_LEN,
    VOCAB_SIZE,
)

# ── Configuration ─────────────────────────────────────────────────────────────

INPUT_FILE  = r"C:\Users\T25301092\Downloads\Comiset23_Lab_Environment_Dataset\dataset_comillas2.JSON"
OUTPUT_FILE = r"data\comiset_sessions.json"

# Timestamp validity window — reject NTP-drifted records (e.g. 1990-12-18)
TIMESTAMP_MIN = "2020-01-01T00:00:00Z"
TIMESTAMP_MAX = "2026-01-01T00:00:00Z"

# Minimum mapped techniques in a chain to be included
MIN_SEQUENCE_LENGTH = 2

# Progress reporting interval (lines)
REPORT_EVERY = 1_000_000

# ── Timestamp validation ──────────────────────────────────────────────────────

def is_valid_timestamp(ts: str) -> bool:
    """Return True if timestamp string is within expected range."""
    if not ts or not isinstance(ts, str):
        return False
    return TIMESTAMP_MIN <= ts <= TIMESTAMP_MAX

# ── Fallback session key ──────────────────────────────────────────────────────

def session_key(src: dict) -> str:
    """
    Primary grouping: process_guid (present in 85.6% of labeled records).
    Fallback: host_name + user_account composite key.
    Returns a non-empty string always.
    """
    guid = src.get("process_guid")
    if guid and isinstance(guid, str) and guid.strip():
        return guid.strip()
    host = src.get("host_name", "unknown_host")
    user = src.get("user_account", "unknown_user")
    return f"FALLBACK__{host}__{user}"

# ── Sequence builder ──────────────────────────────────────────────────────────

def collapse_consecutive_duplicates(seq: list) -> list:
    """
    Collapse runs of identical technique IDs.
    [2, 2, 20, 20, 8] → [2, 20, 8]
    Mirrors the same logic used in Approach B (cowrie pipeline).
    """
    if not seq:
        return []
    result = [seq[0]]
    for item in seq[1:]:
        if item != result[-1]:
            result.append(item)
    return result

def build_padded_sequence(technique_ids: list) -> list:
    """
    Given a list of technique IDs (already collapsed, UNK removed):
    1. Take last MAX_SEQ_LEN entries (most recent = most predictive)
    2. Left-pad with PAD_ID to reach MAX_SEQ_LEN
    Returns list of exactly MAX_SEQ_LEN integers.
    """
    truncated = technique_ids[-MAX_SEQ_LEN:]
    pad_count = MAX_SEQ_LEN - len(truncated)
    return [PAD_ID] * pad_count + truncated

# ── Main extraction ───────────────────────────────────────────────────────────

def extract_sessions():
    start_time = time.time()

    # Session accumulator:
    # key   → process_guid (or fallback key)
    # value → dict with events list
    sessions = defaultdict(lambda: {
        "host_name":     None,
        "user_account":  None,
        "events":        [],   # list of (timestamp_str, raw_technique_id)
    })

    # Counters
    total_lines        = 0
    parse_errors       = 0
    no_source          = 0
    unlabeled          = 0
    invalid_timestamp  = 0
    unk_technique      = 0
    labeled_used       = 0

    print("=" * 65)
    print("  COMISET Session Extractor")
    print("=" * 65)
    print(f"  Input : {INPUT_FILE}")
    print(f"  Output: {OUTPUT_FILE}")
    print(f"  MIN_SEQ_LEN : {MIN_SEQUENCE_LENGTH}")
    print(f"  MAX_SEQ_LEN : {MAX_SEQ_LEN}")
    print(f"  PAD_ID      : {PAD_ID}")
    print(f"  UNK_ID      : {UNK_ID}")
    print("=" * 65)
    print("  Streaming file... (this will take 30-90 minutes)")
    print()

    with open(INPUT_FILE, 'r', encoding='utf-8', errors='replace') as f:
        for raw_line in f:
            total_lines += 1

            # Progress report
            if total_lines % REPORT_EVERY == 0:
                elapsed = time.time() - start_time
                print(f"  [{elapsed:6.0f}s] Lines read: {total_lines:>12,} | "
                      f"Labeled used: {labeled_used:>8,} | "
                      f"Sessions: {len(sessions):>7,}")

            line = raw_line.strip()
            if not line:
                continue

            # Parse JSON
            try:
                doc = json.loads(line)
            except json.JSONDecodeError:
                parse_errors += 1
                continue

            # Extract _source
            src = doc.get("_source")
            if not src or not isinstance(src, dict):
                no_source += 1
                continue

            # Must have rule_technique_id
            raw_tid = src.get("rule_technique_id")
            if not raw_tid:
                unlabeled += 1
                continue

            # Validate timestamp
            ts = src.get("@timestamp", "")
            if not is_valid_timestamp(ts):
                invalid_timestamp += 1
                continue

            # Map technique to vocab ID
            tid_int = technique_to_id(raw_tid)
            if tid_int == UNK_ID:
                unk_technique += 1
                continue

            # All checks passed — accumulate into session
            key = session_key(src)
            session = sessions[key]

            # Record metadata on first encounter
            if session["host_name"] is None:
                session["host_name"]    = src.get("host_name", "unknown")
                session["user_account"] = src.get("user_account", "unknown")

            session["events"].append((ts, raw_tid, tid_int))
            labeled_used += 1

    elapsed_extraction = time.time() - start_time
    print()
    print(f"  Extraction complete in {elapsed_extraction:.1f}s")
    print(f"  Total lines read     : {total_lines:,}")
    print(f"  Parse errors         : {parse_errors:,}")
    print(f"  No _source           : {no_source:,}")
    print(f"  Unlabeled records    : {unlabeled:,}")
    print(f"  Invalid timestamps   : {invalid_timestamp:,}")
    print(f"  UNK techniques       : {unk_technique:,}")
    print(f"  Labeled records used : {labeled_used:,}")
    print(f"  Raw sessions found   : {len(sessions):,}")
    print()

    # ── Build sequences from accumulated events ───────────────────────────────

    print("  Building sequences...")

    output_sessions = {}
    technique_counter = Counter()
    seq_lengths = []

    sessions_before_filter = len(sessions)
    dropped_short = 0

    for key, data in sessions.items():
        events = data["events"]

        # Sort by timestamp (ISO strings sort correctly lexicographically)
        events.sort(key=lambda e: e[0])

        # Extract technique ID integers in order
        raw_seq = [e[2] for e in events]

        # Collapse consecutive duplicates
        collapsed = collapse_consecutive_duplicates(raw_seq)

        # Drop if below minimum length
        if len(collapsed) < MIN_SEQUENCE_LENGTH:
            dropped_short += 1
            continue

        # Count technique distribution
        for tid in collapsed:
            technique_counter[tid] += 1

        # Build padded sequence
        padded = build_padded_sequence(collapsed)

        # Record raw technique strings for interpretability
        raw_technique_strings = [e[1] for e in events]

        seq_lengths.append(len(collapsed))

        output_sessions[key] = {
            "host_name":       data["host_name"],
            "user_account":    data["user_account"],
            "first_seen":      events[0][0],
            "last_seen":       events[-1][0],
            "raw_techniques":  raw_technique_strings,
            "sequence":        collapsed,
            "padded_sequence": padded,
        }

    sessions_after_filter = len(output_sessions)
    avg_seq_len = sum(seq_lengths) / max(len(seq_lengths), 1)

    print(f"  Sessions before filter : {sessions_before_filter:,}")
    print(f"  Dropped (too short)    : {dropped_short:,}")
    print(f"  Sessions after filter  : {sessions_after_filter:,}")
    print(f"  Avg sequence length    : {avg_seq_len:.2f}")
    print()

    # ── Technique distribution report ────────────────────────────────────────

    from mitre_techniques import ID_TO_TECHNIQUE, ID_TO_META
    print("  Technique distribution in output sequences:")
    print(f"  {'ID':<6} {'Token':<12} {'Name':<45} {'Count':>8}")
    print(f"  {'-'*75}")
    for tid, count in sorted(technique_counter.items(), key=lambda x: -x[1]):
        token = ID_TO_TECHNIQUE.get(tid, "???")
        name  = ID_TO_META.get(tid, {}).get("name", "???")
        print(f"  {tid:<6} {token:<12} {name:<45} {count:>8,}")
    print()

    # ── Write output ──────────────────────────────────────────────────────────

    os.makedirs(os.path.dirname(OUTPUT_FILE) if os.path.dirname(OUTPUT_FILE) else ".", exist_ok=True)

    total_time = time.time() - start_time

    output = {
        "metadata": {
            "total_lines_read":        total_lines,
            "total_labeled_records":   labeled_used,
            "sessions_before_filter":  sessions_before_filter,
            "sessions_after_filter":   sessions_after_filter,
            "dropped_short_sequences": dropped_short,
            "technique_distribution":  {str(k): v for k, v in technique_counter.items()},
            "avg_sequence_length":     round(avg_seq_len, 4),
            "extraction_time_seconds": round(total_time, 1),
            "vocab_size":              VOCAB_SIZE,
            "max_seq_len":             MAX_SEQ_LEN,
            "pad_id":                  PAD_ID,
            "unk_id":                  UNK_ID,
            "min_sequence_length":     MIN_SEQUENCE_LENGTH,
        },
        "sessions": output_sessions,
    }

    print(f"  Writing {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    file_size_mb = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)

    print(f"  Done. File size: {file_size_mb:.1f} MB")
    print()
    print("=" * 65)
    print(f"  EXTRACTION COMPLETE")
    print(f"  Total time          : {total_time:.1f}s ({total_time/60:.1f} min)")
    print(f"  Sessions written    : {sessions_after_filter:,}")
    print(f"  Output file         : {OUTPUT_FILE}")
    print("=" * 65)
    print()

    # ── Decision gate ─────────────────────────────────────────────────────────
    print("  DECISION GATE:")
    if sessions_after_filter >= 500:
        print(f"  ✅ {sessions_after_filter:,} sessions — proceed to dataset_loader_comiset.py")
    elif sessions_after_filter >= 200:
        print(f"  ⚠️  {sessions_after_filter:,} sessions — usable but document class imbalance in Chapter 5")
    else:
        print(f"  ❌ {sessions_after_filter:,} sessions — too sparse. Consult supervisor before proceeding.")
    print()

if __name__ == "__main__":
    extract_sessions()