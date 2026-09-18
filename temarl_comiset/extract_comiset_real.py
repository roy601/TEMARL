# -*- coding: utf-8 -*-
"""Stream the COMISET REAL-environment corpus out of its zip, without extracting it.

The archive is 31.7 GB compressed and ~914 GB as raw NDJSON, so it is never
unpacked: `zipfile` decompresses member bytes on the fly and we keep only the
labelled records (0.31% of events, per the data paper).

Differences from `thesis_system/extract_comiset_sessions.py`, and why:
  * reads the zip directly instead of an unpacked path;
  * stores RAW technique strings only, and does not map them to ids here. The
    old extractor mapped with the 25-token v1 vocabulary and dropped anything it
    called UNK, which silently discarded techniques the 86-token union vocab
    does cover. Mapping is left to `data_real.to_ids`, so both corpora go
    through one vocabulary.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import time
import zipfile
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ZIP = os.path.join(os.path.expanduser("~"), "Downloads",
                           "Comiset23_Real_Environment_Dataset.zip")
DEFAULT_OUT = os.path.join(HERE, "data_local", "comiset_real_sessions.json")

TIMESTAMP_MIN = "2020-01-01T00:00:00Z"
TIMESTAMP_MAX = "2026-01-01T00:00:00Z"
REPORT_EVERY = 5_000_000


def session_key(src):
    guid = src.get("process_guid")
    if guid and isinstance(guid, str) and guid.strip():
        return guid.strip()
    return "FALLBACK__%s__%s" % (src.get("host_name", "unknown_host"),
                                 src.get("user_account", "unknown_user"))


def pick_member(zf):
    """Largest .json/.ndjson member — the corpus itself."""
    cands = [i for i in zf.infolist()
             if i.filename.lower().endswith((".json", ".ndjson"))]
    if not cands:
        cands = [i for i in zf.infolist() if not i.is_dir()]
    return max(cands, key=lambda i: i.file_size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", default=DEFAULT_ZIP)
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--limit-lines", type=int, default=0,
                    help="stop after N lines (smoke test); 0 = whole corpus")
    args = ap.parse_args()

    t0 = time.time()
    sessions = defaultdict(lambda: {"host_name": None, "user_account": None,
                                    "events": []})
    n_lines = n_labeled = n_parse_err = n_no_src = n_badts = 0
    tech_counts = defaultdict(int)

    with zipfile.ZipFile(args.zip) as zf:
        member = pick_member(zf)
        print("archive member : %s (%.1f GB uncompressed)"
              % (member.filename, member.file_size / 1e9))
        with zf.open(member) as raw:
            stream = io.TextIOWrapper(raw, encoding="utf-8", errors="replace")
            for line in stream:
                n_lines += 1
                if args.limit_lines and n_lines > args.limit_lines:
                    break
                if n_lines % REPORT_EVERY == 0:
                    print("  [%6.0fs] lines %s | labelled %s | sessions %s"
                          % (time.time() - t0, format(n_lines, ","),
                             format(n_labeled, ","), format(len(sessions), ",")))
                line = line.strip()
                if not line:
                    continue
                try:
                    doc = json.loads(line)
                except json.JSONDecodeError:
                    n_parse_err += 1
                    continue
                src = doc.get("_source")
                if not isinstance(src, dict):
                    n_no_src += 1
                    continue
                tid = src.get("rule_technique_id")
                if not tid:
                    continue
                ts = src.get("@timestamp", "")
                if not (isinstance(ts, str) and TIMESTAMP_MIN <= ts <= TIMESTAMP_MAX):
                    n_badts += 1
                    continue
                s = sessions[session_key(src)]
                if s["host_name"] is None:
                    s["host_name"] = src.get("host_name", "unknown")
                    s["user_account"] = src.get("user_account", "unknown")
                s["events"].append((ts, tid))
                tech_counts[tid] += 1
                n_labeled += 1

    out_sessions = {}
    for k, s in sessions.items():
        ev = sorted(s["events"], key=lambda e: e[0])
        if not ev:
            continue
        out_sessions[k] = {"host_name": s["host_name"],
                           "user_account": s["user_account"],
                           "first_seen": ev[0][0], "last_seen": ev[-1][0],
                           "raw_techniques": [e[1] for e in ev]}

    meta = {"source": "COMISET Real Environment (Zenodo 10.5281/zenodo.15375145)",
            "archive": os.path.basename(args.zip),
            "total_lines_read": n_lines, "total_labeled_records": n_labeled,
            "sessions": len(out_sessions), "parse_errors": n_parse_err,
            "no_source": n_no_src, "invalid_timestamp": n_badts,
            "technique_distribution": dict(sorted(tech_counts.items(),
                                                  key=lambda kv: -kv[1])),
            "extraction_time_seconds": round(time.time() - t0, 1),
            "note": "raw technique strings only; id mapping is done by data_real"}

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"metadata": meta, "sessions": out_sessions}, f)
    print("\nlines %s | labelled %s | sessions %s | %.0fs"
          % (format(n_lines, ","), format(n_labeled, ","),
             format(len(out_sessions), ","), time.time() - t0))
    print("distinct raw techniques:", len(tech_counts))
    print("wrote", args.out)


if __name__ == "__main__":
    main()
