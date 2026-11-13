"""Build conservative host/time sessions within independently identified captures."""
import json
import math
from collections import defaultdict
from pathlib import Path
import config


def build_sequences(events, gap_seconds=None, max_duration_seconds=None):
    gap = config.SESSION_GAP_SECONDS if gap_seconds is None else gap_seconds
    duration = config.SESSION_MAX_DURATION_SECONDS if max_duration_seconds is None else max_duration_seconds
    if not all(math.isfinite(x) and x > 0 for x in (gap, duration)):
        raise ValueError("Session windows must be positive")
    groups = defaultdict(list)
    excluded = 0
    for event in events:
        if event.get("timestamp") is None or not event.get("host"):
            excluded += 1
            continue
        groups[(event["capture_id"], event["host"])].append(event)
    sequences = []
    for (capture, host), records in sorted(groups.items()):
        ordered = sorted(records, key=lambda e: (e["timestamp"], e["file"], e["record_index"]))
        sessions = []
        for event in ordered:
            if not sessions or event["timestamp"] - sessions[-1][-1]["timestamp"] > gap or event["timestamp"] - sessions[-1][0]["timestamp"] >= duration:
                sessions.append([])
            sessions[-1].append(event)
        for index, session in enumerate(sessions, 1):
            # Simultaneous labels are unordered: never turn A,B at one instant into A->B.
            instants = defaultdict(set)
            for event in session:
                instants[event["timestamp"]].update(event["technique_ids"])
            steps = []
            for timestamp, labels in sorted(instants.items()):
                label_set = sorted(labels)
                if not steps or steps[-1]["technique_ids"] != label_set:
                    steps.append({"timestamp": timestamp, "technique_ids": label_set})
            ambiguous = any(len(step["technique_ids"]) != 1 for step in steps)
            chain = [] if ambiguous else [step["technique_ids"][0] for step in steps]
            sequences.append({"scenario_id": f"{capture}::{host}::{index}",
                              "scenario_name": f"{capture} / {host} / {index}",
                              "capture_id": capture, "host": host,
                              "start_time": session[0]["timestamp"], "end_time": session[-1]["timestamp"],
                              "raw_length": len(session), "length": len(chain), "sequence": chain,
                              "steps": steps, "ordered": not ambiguous,
                              "unique_technique_count": len(set().union(*instants.values())),
                              "source_files": sorted({e["file"] for e in session}),
                              "status": "ambiguous_simultaneous_labels" if ambiguous else "candidate_host_session"})
    return sequences, excluded


def extract_sequences():
    source = Path(config.DATA_DIR) / "splunk_attack_data_ground_truth.json"
    data = json.loads(source.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict) or data.get("schema_version") != 2:
        raise ValueError("Legacy ground truth lacks trustworthy host/time/label provenance. Rerun step 1.")
    sessions, excluded = build_sequences(data["events"])
    output = Path(config.OUTPUT_DIR)
    output.mkdir(parents=True, exist_ok=True)
    for filename, value in [("sequences.json", sessions), ("capture_inventory.json", data["captures"]),
                            ("session_audit.json", {"excluded_missing_host_or_time": excluded,
                             "scan_audit": data["audit"], "gap_seconds": config.SESSION_GAP_SECONDS,
                             "max_duration_seconds": config.SESSION_MAX_DURATION_SECONDS})]:
        (output / filename).write_text(json.dumps(value, indent=2), encoding="utf-8")
    print(f"[+] {len(sessions)} candidate host sessions; {excluded} labelled records excluded for missing host/time.")
    return sessions


if __name__ == "__main__":
    extract_sequences()
