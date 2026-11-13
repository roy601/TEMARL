"""Stream COMISET ZIP telemetry into disk-backed process sequences."""
import argparse
import csv
import hashlib
import io
import json
import re
import sqlite3
import statistics
import time
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

TECHNIQUE = re.compile(r"(?<![A-Z0-9])T\d{4}(?:\.\d{3})?(?![\d.])")


def labels(value):
    # Multiple labels describe one event, not an ordered list of actions.
    if isinstance(value, list):
        return sorted({t for v in value for t in labels(v)})
    return sorted(set(TECHNIQUE.findall(str(value).upper()))) if value else []


def timestamp(value):
    if not isinstance(value, str):
        raise ValueError("Missing timestamp")
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("Timestamp has no timezone")
    return dt.astimezone(timezone.utc)


def analyze(zip_path, output, member=None, max_lines=0, gap_minutes=0,
            length_metric="raw_events"):
    if length_metric not in ("raw_events", "collapsed_label_steps"):
        raise ValueError("Unknown sequence length metric: " + length_metric)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    db_path = output / "events.sqlite"
    if db_path.exists():
        raise ValueError("Output already has events.sqlite; use a NEW output directory.")
    counts = Counter()
    started = time.monotonic()
    complete = True
    with zipfile.ZipFile(zip_path) as archive:
        candidates = [i.filename for i in archive.infolist()
                      if i.filename.lower().endswith((".json", ".jsonl", ".ndjson"))]
        if member is None:
            if len(candidates) != 1:
                raise ValueError("Select --member from: " + repr(candidates))
            member = candidates[0]
        info = archive.getinfo(member)
        provenance = {"zip": str(Path(zip_path).resolve()), "member": member,
                      "uncompressed_bytes": info.file_size, "zip_crc32": f"{info.CRC:08x}"}
        db = sqlite3.connect(db_path)
        try:
            db.execute("CREATE TABLE events (identity TEXT PRIMARY KEY, session TEXT, "
                       "ts REAL, stamp TEXT, line INTEGER, techniques TEXT)")
            with archive.open(member) as raw, io.TextIOWrapper(raw, encoding="utf-8-sig") as stream:
                for line_number, line in enumerate(stream, 1):
                    if max_lines and line_number > max_lines:
                        complete = False
                        break
                    counts["lines_read"] += 1
                    if line_number % 100000 == 0:
                        db.commit()
                        print(f"Lines {line_number:,}; kept {counts['events_kept']:,}; "
                              f"elapsed {time.monotonic()-started:.0f}s", flush=True)
                    if not line.strip():
                        counts["blank_lines"] += 1
                        continue
                    try:
                        doc = json.loads(line)
                    except json.JSONDecodeError:
                        counts["malformed_json_lines"] += 1
                        continue
                    source = doc.get("_source") if isinstance(doc, dict) else None
                    if not isinstance(source, dict):
                        counts["missing_source"] += 1
                        continue
                    technique_ids = labels(source.get("rule_technique_id"))
                    if not technique_ids:
                        counts["no_valid_technique"] += 1
                        continue
                    counts["labeled_records"] += 1
                    host, guid = source.get("host_name"), source.get("process_guid")
                    if not host or not guid or str(guid).strip().lower() in ("-", "null", "none"):
                        counts["missing_host_or_process_guid"] += 1
                        continue
                    try:
                        dt = timestamp(source.get("@timestamp"))
                    except (ValueError, TypeError, OverflowError):
                        counts["invalid_timestamp"] += 1
                        continue
                    if not 2020 <= dt.year < 2026:
                        counts["timestamp_outside_2020_2025"] += 1
                        continue
                    session = json.dumps([str(host).lower(), str(guid).lower()])
                    identity = (json.dumps([doc.get("_index"), doc["_id"]])
                                if doc.get("_id") else hashlib.sha256(line.strip().encode()).hexdigest())
                    cursor = db.execute("INSERT OR IGNORE INTO events VALUES (?,?,?,?,?,?)",
                                        (identity, session, dt.timestamp(), dt.isoformat(),
                                         line_number, json.dumps(technique_ids)))
                    counts["events_kept" if cursor.rowcount else "duplicate_records"] += 1
            db.commit()
            db.execute("CREATE INDEX event_order ON events(session, ts, line)")
            lengths = {"raw_events": [], "collapsed_label_steps": [], "unique_techniques": []}
            scalar_lengths = []
            vocabulary = set()
            with (output / "sequences.jsonl").open("w", encoding="utf-8") as seq_file, \
                    (output / "sequence_lengths.csv").open("w", newline="", encoding="utf-8") as table:
                writer = csv.writer(table)
                writer.writerow(["sequence_id", "host", "process_guid", "raw_events",
                                 "collapsed_label_steps", "unique_techniques", "multi_label_events"])
                def emit(key, events):
                    if not events:
                        return
                    host, guid = json.loads(key)
                    steps = []
                    for event in events:
                        if not steps or steps[-1] != event["techniques"]:
                            steps.append(event["techniques"])
                    unique = {t for step in steps for t in step}
                    multi = sum(len(e["techniques"]) > 1 for e in events)
                    sid = len(lengths["raw_events"]) + 1
                    for name, value in zip(lengths, [len(events), len(steps), len(unique)]):
                        lengths[name].append(value)
                    if not multi:
                        scalar_lengths.append(len(steps))
                    vocabulary.update(unique)
                    record = {"sequence_id": sid, "host": host, "process_guid": guid,
                              "events": events, "collapsed_label_steps": steps,
                              "scalar_sequence": [s[0] for s in steps] if not multi else None}
                    seq_file.write(json.dumps(record) + "\n")
                    writer.writerow([sid, host, guid, len(events), len(steps), len(unique), multi])

                current, events, last = None, [], None
                for key, ts, stamp, line, ids in db.execute(
                        "SELECT session,ts,stamp,line,techniques FROM events ORDER BY session,ts,line"):
                    if key != current or (gap_minutes and last is not None and ts-last > gap_minutes*60):
                        emit(current, events)
                        events = []
                    current, last = key, ts
                    events.append({"timestamp": stamp, "source_line": line, "techniques": json.loads(ids)})
                emit(current, events)
            def stats(values):
                return {"count": len(values), "mean": statistics.mean(values) if values else 0,
                        "median": statistics.median(values) if values else 0,
                        "max": max(values, default=0),
                        "more_than_25": sum(v > 25 for v in values),
                        "more_than_30": sum(v > 30 for v in values)}
            metrics = {k: stats(v) for k, v in lengths.items()}
            metrics["unambiguous_collapsed_sequences"] = stats(scalar_lengths)
            distribution = [{"sequence_length": length, "sequence_count": count}
                            for length, count in sorted(Counter(lengths[length_metric]).items())]
            with (output / "sequence_length_counts.csv").open(
                    "w", newline="", encoding="utf-8") as table:
                writer = csv.DictWriter(table, fieldnames=["sequence_length", "sequence_count"])
                writer.writeheader()
                writer.writerows(distribution)
            result = {"source": provenance, "complete_archive_scan": complete,
                      "counts": dict(counts), "metrics": metrics,
                      "sequence_length_metric": length_metric,
                      "sequence_length_counts": distribution,
                      "gap_minutes": gap_minutes, "technique_vocabulary": sorted(vocabulary),
                      "elapsed_seconds": round(time.monotonic()-started, 2)}
            (output / "statistics.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
            report = ["# COMISET Sequence Audit", "",
                      "Status: " + ("FULL ARCHIVE SCAN" if complete else "PARTIAL SMOKE TEST - NOT FINAL COUNTS"),
                      "", f"Length: {length_metric}; grouped by host + process GUID; inactivity gap: {gap_minutes} minutes (0 = no split).",
                      "", "| Sequence length | Number of sequences |", "|---:|---:|"]
            for row in distribution:
                report.append(f"| {row['sequence_length']} | {row['sequence_count']} |")
            if not distribution:
                report += ["", "No usable sequences found. See statistics.json for processing counts."]
            (output / "RESULTS.md").write_text("\n".join(report) + "\n", encoding="utf-8")
            print(f"Finished. Report: {(output / 'RESULTS.md').resolve()}", flush=True)
            return result
        finally:
            db.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "results")
    parser.add_argument("--member", help="JSON member name if the ZIP contains multiple data files")
    parser.add_argument("--max-lines", type=int, default=0, help="Smoke test only; 0 scans the whole ZIP")
    parser.add_argument("--gap-minutes", type=float, default=0,
                        help="Optional inactivity split within a host/process; default is no split")
    parser.add_argument("--length-metric", choices=("raw_events", "collapsed_label_steps"),
                        default="raw_events", help="Length definition for the grouped count table")
    args = parser.parse_args()
    if args.max_lines < 0 or args.gap_minutes < 0:
        parser.error("Limits must be nonnegative")
    analyze(args.zip, args.output, args.member, args.max_lines, args.gap_minutes,
            args.length_metric)


if __name__ == "__main__":
    main()
