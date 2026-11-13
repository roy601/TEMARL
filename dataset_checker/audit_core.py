"""Conservative local ATT&CK event audit shared by Windows APT and OpTC.

Input labels are annotations, not independently validated ground truth.
Archives are read in place; no archive members are extracted to disk.
"""
import argparse
import csv
import gzip
import io
import json
import math
import re
import tarfile
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from report_format import summary_box

TECH = re.compile(r"(?<![A-Za-z0-9])T\d{4}(?:\.\d{3})?(?![A-Za-z0-9.])", re.I)
LABELS = ("technique_id", "technique_ids", "technique", "mitre_technique", "mitre_techniques", "attack_id", "attack_technique", "rulename")
TIMES = ("timestamp", "@timestamp", "_time", "event_time", "eventtime", "utctime", "systemtime", "time")
HOSTS = ("hostname", "host", "computer", "computername", "device_name")
FIELD_ALIASES = {
    "_source.rule.mitre.id": "technique_ids", "rule.mitre.id": "technique_ids",
    "_source.agent.name": "host", "agent.name": "host", "agent-name": "host",
    "_source.timestamp": "timestamp", "_source.@timestamp": "@timestamp",
    "mitre technique": "mitre_technique",
}
GENERATED = {"scenario_manifest.csv", "raw_csv_manifest.json", "optc_ground_truth_sample.json",
             "sequences.json", "statistics.json", "audit.json", "download_manifest.json",
             "log_to_scenario_mapping.csv", "validation_summary.csv"}

def timestamp(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        n = float(value)
        if not math.isfinite(n):
            return None
        for scale in (1, 1000, 1000000, 1000000000):
            if 946684800 <= n / scale < 4102444800:
                return n / scale
        return None
    except (ValueError, TypeError):
        try:
            text = str(value).strip()
            if "T" not in text and " " not in text:
                return None
            try:
                dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
            except ValueError:
                # Wazuh/Kibana CSV display timestamps in the Windows APT files.
                dt = datetime.strptime(text, "%b %d, %Y @ %H:%M:%S.%f")
            n = dt.replace(tzinfo=dt.tzinfo or timezone.utc).timestamp()
            return n if 946684800 <= n < 4102444800 else None
        except (ValueError, OverflowError, OSError):
            return None

def flatten(record):
    out = {}
    for key, value in record.items():
        if not isinstance(key, str):
            continue
        key = key.lower()
        if isinstance(value, dict):
            # Retain paths to avoid conflating unrelated nested fields.
            for child, item in flatten(value).items():
                out[key + "." + child] = item
            if key == "host" and isinstance(value.get("name"), str):
                out["host"] = value["name"]
        else:
            out[key] = value
    for original, canonical in FIELD_ALIASES.items():
        value = out.get(original)
        if value is not None and str(value).strip():
            out.setdefault(canonical, value)
    return out

def pick(fields, keys):
    for key in keys:
        if key in fields and fields[key] not in (None, ""):
            return fields[key]
    # Accept an unambiguous nested field, never pick among competing values.
    matches = [v for k, v in fields.items() if k.rsplit(".", 1)[-1] in keys and v not in (None, "")]
    return matches[0] if len(matches) == 1 else None

def objects(obj):
    if isinstance(obj, list):
        yield from (x for x in obj if isinstance(x, dict))
    elif isinstance(obj, dict):
        if any(k.lower() in LABELS for k in obj if isinstance(k, str)):
            yield obj
        elif obj and all(isinstance(v, list) for v in obj.values()):
            for scenario, records in obj.items():
                for record in records:
                    if isinstance(record, dict):
                        yield dict(record, scenario_id=scenario)
        else:
            yield obj

def read_stream(stream, name, audit):
    if name.lower().endswith(".csv"):
        yield from csv.DictReader(stream)
        return
    # Arrays/pretty JSON are parsed as a document. JSONL is streamed.
    if name.lower().endswith(".json"):
        text = stream.read()
        try:
            yield from objects(json.loads(text))
            return
        except json.JSONDecodeError:
            stream = io.StringIO(text)
    for line in stream:
        if not line.strip():
            continue
        try:
            yield from objects(json.loads(line))
        except json.JSONDecodeError:
            audit["unparsed_lines"] += 1

def supported(name):
    return name.lower().endswith((".json", ".jsonl", ".ndjson", ".csv", ".log"))

def records(path, audit):
    name = path.name.lower()
    if name.endswith((".tar", ".tar.gz", ".tgz")):
        with tarfile.open(path) as archive:
            for member in archive:
                if member.isfile() and supported(member.name):
                    with archive.extractfile(member) as raw:
                        yield member.name, read_stream(io.TextIOWrapper(raw, encoding="utf-8-sig", errors="replace"), member.name, audit)
                elif member.isfile():
                    audit["unsupported_archive_members"] += 1
    elif name.endswith(".zip"):
        with zipfile.ZipFile(path) as archive:
            for member in archive.infolist():
                if not member.is_dir() and supported(member.filename):
                    with archive.open(member) as raw:
                        yield member.filename, read_stream(io.TextIOWrapper(raw, encoding="utf-8-sig", errors="replace"), member.filename, audit)
                elif not member.is_dir():
                    audit["unsupported_archive_members"] += 1
    elif name.endswith(".gz"):
        with gzip.open(path, "rt", encoding="utf-8-sig", errors="replace") as stream:
            yield "", read_stream(stream, name[:-3], audit)
    elif supported(name):
        with path.open(encoding="utf-8-sig", errors="replace") as stream:
            yield "", read_stream(stream, name, audit)
    else:
        audit["unsupported_files"] += 1

def scan(source, output):
    source, output = Path(source).resolve(), Path(output).resolve()
    if not source.is_dir():
        raise FileNotFoundError(f"Input directory does not exist: {source}")
    if source == output or source.is_relative_to(output):
        raise ValueError("Input must not be the output directory or inside it")
    audit, events = Counter(), []
    for path in sorted(source.rglob("*")):
        if not path.is_file() or path.is_relative_to(output):
            continue
        if path.name.lower() == "combined.csv" and (path.parent / "scenario_manifest.csv").exists():
            period_files = [p for p in path.parent.glob("*.csv")
                            if re.match(r"^\d.*(?:November|December|October)", p.name, re.I)]
            if period_files:
                audit["combined_exports_skipped"] += 1
                continue  # Windows APT combined.csv repeats the per-period exports.
        if any(p in {".git", "__pycache__", "_evaluation_steps", "output", "output_verified"} for p in path.relative_to(source).parts) or path.name in GENERATED:
            audit["generated_or_cached_files_skipped"] += 1
            continue
        audit["files_scanned"] += 1
        try:
            for member, rows in records(path, audit):
                origin = path.relative_to(source).as_posix() + ("::" + member if member else "")
                for index, record in enumerate(rows, 1):
                    audit["records_parsed"] += 1
                    fields = flatten(record)
                    labels = sorted({m.upper() for k, v in fields.items() if k.rsplit(".", 1)[-1] in LABELS for m in TECH.findall(str(v))})
                    if not labels:
                        audit["unlabelled_records"] += 1
                        continue
                    host = pick(fields, HOSTS)
                    ts = timestamp(pick(fields, TIMES))
                    if not isinstance(host, str) or not host.strip() or ts is None:
                        audit["labelled_records_missing_host_or_time"] += 1
                        if not isinstance(host, str) or not host.strip():
                            audit["labelled_records_missing_host"] += 1
                        if ts is None:
                            audit["labelled_records_invalid_time"] += 1
                        continue
                    # Scope scenario IDs to their source: repeated IDs across independent files do not prove shared capture.
                    scenario = pick(fields, ("scenario_id", "scenario", "capture_id", "operation_id"))
                    events.append({"capture_id": origin + ("::" + str(scenario) if scenario else ""),
                                   "host": host.strip().lower(), "timestamp": ts, "technique_ids": labels,
                                   "file": origin, "record_index": index, "label_source": "explicit_event_field"})
                    audit["eligible_labelled_events"] += 1
        except (OSError, ValueError, csv.Error, tarfile.TarError, zipfile.BadZipFile) as error:
            audit["file_errors"] += 1
            print(f"[WARN] {path}: {error}")
    return events, dict(audit)

def sessions(events, gap=1800, duration=14400):
    if not all(math.isfinite(x) and x > 0 for x in (gap, duration)):
        raise ValueError("Session windows must be finite and positive")
    groups = defaultdict(list)
    for e in events:
        groups[(e["capture_id"], e["host"])].append(e)
    result = []
    for (capture, host), rows in sorted(groups.items()):
        chunks = []
        for e in sorted(rows, key=lambda r: r["timestamp"]):
            if not chunks or e["timestamp"] - chunks[-1][-1]["timestamp"] > gap or e["timestamp"] - chunks[-1][0]["timestamp"] >= duration:
                chunks.append([])
            chunks[-1].append(e)
        for i, chunk in enumerate(chunks, 1):
            instants = defaultdict(set)
            for e in chunk:
                instants[e["timestamp"]].update(e["technique_ids"])
            steps = []
            for ts, labels in sorted(instants.items()):
                labels = sorted(labels)
                if not steps or steps[-1]["technique_ids"] != labels:
                    steps.append({"timestamp": ts, "technique_ids": labels})
            ordered = all(len(s["technique_ids"]) == 1 for s in steps)
            chain = [s["technique_ids"][0] for s in steps] if ordered else []
            reasons = []
            if any(len(e["technique_ids"]) > 1 for e in chunk):
                reasons.append("multi_label_event")
            by_time = defaultdict(list)
            for e in chunk:
                by_time[e["timestamp"]].append(set(e["technique_ids"]))
            if any(len(labels) > 1 and len(set.union(*labels)) > 1 for labels in by_time.values()):
                reasons.append("multiple_events_same_timestamp")
            result.append({"scenario_id": f"{capture}::{host}::{i}", "capture_id": capture, "host": host,
                           "ordered": ordered, "sequence": chain, "length": len(chain), "raw_length": len(chunk),
                           "label_set_sequence": [s["technique_ids"] for s in steps],
                           "label_set_length": len(steps), "ambiguity_reasons": reasons,
                           "representation": "single_label_chain" if ordered else "time_ordered_label_sets",
                           "start_time": chunk[0]["timestamp"], "end_time": chunk[-1]["timestamp"], "steps": steps,
                           "source_files": sorted({e["file"] for e in chunk})})
    return result

def save(path, value):
    target = Path(path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(value, indent=2)
    temporary = target.with_name(target.name + ".tmp")
    import os
    try:
        with open(temporary, "w", encoding="utf-8") as fh:
            fh.write(content)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)

def _read_json_retry(path, retries=5, delay=1.0):
    """Read a JSON file with retries to handle Defender/antivirus file locks on Windows."""
    import time
    target = Path(path).resolve()
    for attempt in range(retries):
        try:
            return json.loads(target.read_text(encoding="utf-8"))
        except OSError:
            if attempt == retries - 1:
                raise
            time.sleep(delay)

def ingest(source, output):
    events, audit = scan(source, output)
    save(Path(output) / "events.json", {"schema_version": 3, "source": str(Path(source).resolve()), "events": events, "audit": audit})

def extract(output, gap=1800, duration=14400):
    data = _read_json_retry(Path(output) / "events.json")
    if data.get("schema_version") != 3:
        raise ValueError("Legacy intermediate data: rerun ingestion")
    result = sessions(data["events"], gap, duration)
    save(Path(output) / "sequences.json", {"schema_version": 3, "sessions": result})
    save(Path(output) / "audit.json", dict(data["audit"], source=data["source"], gap_seconds=gap, max_duration_seconds=duration))
    return result

def analyze(output, dataset):
    data = _read_json_retry(Path(output) / "sequences.json")
    if not isinstance(data, dict) or data.get("schema_version") != 3:
        raise ValueError("Legacy sequences: rerun the pipeline")
    all_sessions = data["sessions"]
    ordered = [s for s in all_sessions if s["ordered"] and s["length"]]
    lengths = [s["length"] for s in ordered]
    metrics = {"dataset": dataset, "total_candidate_sessions": len(all_sessions), "total_sequences": len(ordered),
               "ambiguous_sessions": sum(not s["ordered"] for s in all_sessions),
               "max_length": max(lengths, default=0), "sequences_gt_16": sum(n > 16 for n in lengths),
               "sequences_gt_30": sum(n > 30 for n in lengths),
               "verdict": "REQUIRES VALIDATION" if all_sessions else "INSUFFICIENT ORDERED EVENT EVIDENCE"}
    save(Path(output) / "statistics.json", metrics)
    vocabulary = {t for s in ordered for t in s["sequence"]}
    all_vocabulary = {t for s in all_sessions for step in s["steps"] for t in step["technique_ids"]}
    set_lengths = [len(s["steps"]) for s in all_sessions]
    metrics["label_set_sessions"] = len(all_sessions)
    metrics["max_label_set_length"] = max(set_lengths, default=0)
    metrics["label_set_sessions_gt_16"] = sum(n > 16 for n in set_lengths)
    metrics["ambiguity_reason_session_counts"] = dict(Counter(r for s in all_sessions for r in s.get("ambiguity_reasons", [])))
    metrics.update({"ordered_technique_vocabulary_size": len(vocabulary),
                    "all_candidate_technique_vocabulary_size": len(all_vocabulary),
                    "techniques_only_in_ambiguous_sessions": sorted(all_vocabulary - vocabulary),
                    "events_in_ambiguous_sessions": sum(s["raw_length"] for s in all_sessions if not s["ordered"])})
    save(Path(output) / "statistics.json", metrics)
    b1_report = "EXPERIMENT B1: STRICT RECONSTRUCTION\n"
    b1_report += summary_box(lengths, len(vocabulary)) + "\n"
    b1_report += "Single-label steps in timestamp order; attack execution is not independently validated.\n"
    b2_report = "EXPERIMENT B2: UNCERTAINTY-AWARE RECONSTRUCTION\n"
    b2_report += summary_box(set_lengths, len(all_vocabulary)).replace("Total sequences:", "Total sessions: ").replace("Sequences > 16 techniques:", "Sessions > 16 set-steps:  ") + "\n"
    b2_report += "Length counts label-set steps, not individually ordered techniques.\n"
    b2_report += "Multiple labels within a step have no established internal order.\n"
    b2_report += "B2 includes B1 sessions: these are overlapping representations, not independent datasets.\n"
    for name, subset, text, lens, vocab_size in (
        ("experiment_b1", ordered, b1_report, lengths, len(vocabulary)),
        ("experiment_b2", all_sessions, b2_report, set_lengths, len(all_vocabulary)),
    ):
        destination = Path(output) / name
        save(destination / "sequences.json", {"schema_version": 3, "representation": name, "sessions": subset})
        save(destination / "statistics.json", {"total_sessions": len(subset), "max_length": max(lens, default=0),
            "length_unit": "single_label_steps" if name == "experiment_b1" else "label_set_steps",
            "sessions_gt_16": sum(n > 16 for n in lens), "technique_vocabulary_size": vocab_size,
            "verdict": "REQUIRES VALIDATION" if subset else "INSUFFICIENT EVIDENCE"})
        (destination / "statistics.txt").write_text(text, encoding="utf-8")
    report = b1_report + "\n" + b2_report + "\n"
    report += "\n".join(f"{k}: {v}" for k, v in metrics.items() if k != "techniques_only_in_ambiguous_sessions")
    report += "\nFull label lists are retained in statistics.json.\n"
    report += "\n\nExplicit event annotations and host/time proximity produce candidates, not validated campaigns.\n"
    report += "Input files are isolated. Cross-file campaigns require a verified capture mapping.\n"
    report += "Naive timestamps are interpreted as UTC. Check audit.json for excluded input coverage.\n"
    (Path(output) / "statistics.txt").write_text(report, encoding="utf-8")
    review = []
    for s in sorted(all_sessions, key=lambda x: len(x["steps"]), reverse=True)[:10]:
        review.append({"scenario_id": s["scenario_id"], "source_files": s["source_files"],
                       "host": s["host"], "start_time": s["start_time"], "end_time": s["end_time"],
                       "label_set_length": len(s["steps"]), "first_steps": s["steps"][:20],
                       "validation_status": "not_manually_validated"})
    save(Path(output) / "review_examples.json", review)
    print(report)
    return metrics

def main(base, dataset):
    parser = argparse.ArgumentParser(description=f"{dataset}: local explicit-label event audit")
    parser.add_argument("--input-dir", default=str(Path(base) / "data"))
    parser.add_argument("--output-dir", default=str(Path(base) / "output_verified"))
    parser.add_argument("--session-gap-minutes", type=float, default=30)
    parser.add_argument("--max-session-hours", type=float, default=4)
    args = parser.parse_args()
    gap, duration = args.session_gap_minutes * 60, args.max_session_hours * 3600
    if not all(math.isfinite(x) and x > 0 for x in (gap, duration)):
        parser.error("Session windows must be finite and positive")
    ingest(args.input_dir, args.output_dir)
    extract(args.output_dir, gap, duration)
    analyze(args.output_dir, dataset)
