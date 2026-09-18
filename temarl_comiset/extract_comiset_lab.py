# -*- coding: utf-8 -*-
"""Re-extract the COMISET LAB corpus with the UNION vocabulary.

Replaces thesis_system/extract_comiset_sessions.py, which mapped through the
25-token v1 vocabulary (mitre_techniques.py) and dropped every technique it
could not place. Measured consequence: the raw file holds 53 distinct
techniques and the shipped extraction holds 10 -- T1036 (45.5% of all labelled
records) and T1059.001 (24.2%) among the casualties.

This version stores NORMALISED technique strings and lets the 86-token union
vocabulary do the mapping at load time, so both corpora share one vocabulary.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import time
from collections import Counter, defaultdict

from technique_norm import normalise

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_IN = os.path.join(os.path.expanduser("~"), "Downloads",
                          "Comiset23_Lab_Environment_Dataset", "dataset_comillas2.json")
DEFAULT_OUT = os.path.join(HERE, "data_local", "comiset_lab_sessions.json")

TS_MIN, TS_MAX = "2020-01-01T00:00:00Z", "2026-01-01T00:00:00Z"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default=DEFAULT_IN)
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--max-lines", type=int, default=0)
    args = ap.parse_args()

    t0 = time.time()
    sessions = defaultdict(lambda: {"host_name": None, "user_account": None, "events": []})
    n = n_lab = n_unusable = n_badts = 0
    tech = Counter()

    with io.open(args.path, encoding="utf-8", errors="replace") as f:
        for line in f:
            n += 1
            if args.max_lines and n > args.max_lines:
                break
            if n % 10_000_000 == 0:
                print("  [%6.0fs] lines=%s labelled=%s sessions=%s"
                      % (time.time() - t0, format(n, ","), format(n_lab, ","),
                         format(len(sessions), ",")), flush=True)
            line = line.strip().rstrip(",")
            if not line or line in "[]":
                continue
            try:
                doc = json.loads(line)
            except Exception:
                continue
            s = doc.get("_source") if isinstance(doc, dict) else None
            if not isinstance(s, dict):
                continue
            raw = s.get("rule_technique_id")
            if not raw:
                continue
            if isinstance(raw, list):
                raw = raw[0] if raw else None
            t = normalise(raw)
            if not t:
                n_unusable += 1
                continue
            ts = s.get("@timestamp", "")
            if not (isinstance(ts, str) and TS_MIN <= ts <= TS_MAX):
                n_badts += 1
                continue
            guid = s.get("process_guid") or "FB__%s__%s" % (
                s.get("host_name", "?"), s.get("user_account", "?"))
            rec = sessions[str(guid)]
            if rec["host_name"] is None:
                rec["host_name"] = s.get("host_name", "unknown")
                rec["user_account"] = s.get("user_account", "unknown")
            rec["events"].append((ts, t))
            tech[t] += 1
            n_lab += 1

    out = {}
    for k, rec in sessions.items():
        ev = sorted(rec["events"], key=lambda e: e[0])
        if not ev:
            continue
        out[k] = {"host_name": rec["host_name"], "user_account": rec["user_account"],
                  "first_seen": ev[0][0], "last_seen": ev[-1][0],
                  "raw_techniques": [e[1] for e in ev]}

    meta = {"source": "COMISET Lab / Malicious Test Environment",
            "input": args.path, "total_lines_read": n,
            "total_labeled_records": n_lab, "unusable_labels": n_unusable,
            "invalid_timestamp": n_badts, "sessions": len(out),
            "distinct_techniques": len(tech),
            "technique_distribution": dict(tech.most_common()),
            "normalisation": "technique_norm.normalise (MITRE revoked-by + label cleanup)",
            "extraction_time_seconds": round(time.time() - t0, 1)}
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"metadata": meta, "sessions": out}, f)
    print("\nlines %s | labelled %s | sessions %s | distinct techniques %d | %.0fs"
          % (format(n, ","), format(n_lab, ","), format(len(out), ","),
             len(tech), time.time() - t0))
    print("wrote", args.out)


if __name__ == "__main__":
    main()
