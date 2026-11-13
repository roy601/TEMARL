"""Read Mordor telemetry archives without assigning capture labels to every event."""
import json
import contextlib
import io
import csv
import tarfile
import zipfile
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlparse
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import audit_core as core
from behavior_rules import infer, RULES_VERSION
from event_mapper import annotate, canonical, metadata_comparison, VERSION as MAPPER_VERSION
from report_format import summary_box


def compact_rule_matches(matches):
    return [{key: value for key, value in match.items() if key != "evidence"} for match in matches]


def render_results(output, title, annotation_source):
    """Keep empty machine-readable results, but show a status instead of zero boxes."""
    with contextlib.redirect_stdout(io.StringIO()):
        metrics = core.analyze(output, title)
    data = core._read_json_retry(output / "sequences.json")["sessions"]
    reports = [title, "Label provenance: " + annotation_source,
               "Timestamp order is not campaign validation. Benign activity can match annotation rules.", ""]
    for name, title_part, selected in [("experiment_b1", "B1: STRICT RECONSTRUCTION", [s for s in data if s["ordered"]]),
                                        ("experiment_b2", "B2: UNCERTAINTY-AWARE RECONSTRUCTION", data)]:
        part = title_part + "\n"
        if selected:
            lengths = [len(s["steps"]) for s in selected]
            vocab = {t for s in selected for step in s["steps"] for t in step["technique_ids"]}
            part += summary_box(lengths, len(vocab)) + "\n"
            if name == "experiment_b2":
                part = part.replace("Sequences > 16 techniques:", "Sessions > 16 set-steps:  ")
                part += "Length counts label-set steps. No order is asserted inside a label set. B2 includes B1.\n"
        else:
            part += "No supported evidence for this representation. Empty results retained in JSON.\n"
        part += "Annotation source: " + annotation_source + "\n"
        (output / name / "statistics.txt").write_text(part, encoding="utf-8")
        reports.append(part)
    for path in [output / "statistics.json", *output.glob("experiment_b*/statistics.json")]:
        result = core._read_json_retry(path)
        result["annotation_source"] = annotation_source
        core.save(path, result)
    report = "\n".join(reports)
    (output / "statistics.txt").write_text(report, encoding="utf-8")
    return report


def run_raw_audit(source, output, gap=1800, duration=14400, infer_techniques=False):
    source, output = Path(source).resolve(), Path(output).resolve()
    ownership, expectations = {}, {}
    for path in sorted(source.rglob("*.yaml")) + sorted(source.rglob("*.yml")):
        if "_evaluation_steps" in path.parts or path.is_relative_to(output):
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
        if not isinstance(data, dict):
            continue
        capture_key = path.relative_to(source).as_posix()
        expected = set()
        for entry in data.get("attack_mappings") or []:
            if not isinstance(entry, dict):
                continue
            technique = str(entry.get("technique") or "").upper()
            sub = str(entry.get("sub-technique") or entry.get("sub_technique") or "").lstrip(".")
            if sub and "." not in technique:
                technique += "." + sub.zfill(3)
            if core.TECH.fullmatch(technique):
                expected.add(technique)
        if expected:
            expectations[capture_key] = expected
        for item in data.get("files") or []:
            if not isinstance(item, dict):
                continue
            raw = unquote(urlparse(str(item.get("link", ""))).path)
            marker = "/datasets/compound/"
            if marker not in raw:
                continue
            target = (source / raw.split(marker, 1)[1]).resolve()
            if target.is_relative_to(source):
                ownership.setdefault(target, set()).add(path.relative_to(source).as_posix())
    events, files, inferred_events, annotation_events = [], [], [], []
    rule_counts = Counter()
    provider_counts = Counter()
    total = Counter()
    for path in sorted(source.rglob("*")):
        if not path.is_file() or path.is_relative_to(output) or any(p in {".git", "__pycache__", "_evaluation_steps"} for p in path.parts):
            continue
        if not (core.supported(path.name) or path.name.lower().endswith((".zip", ".gz", ".tar", ".tgz"))):
            continue
        if path.name in core.GENERATED or path.suffix.lower() in {".yaml", ".yml"}:
            continue
        audit = Counter()
        hosts = set()
        earliest = latest = None
        relative = path.relative_to(source).as_posix()
        owners = ownership.get(path, set())
        capture = next(iter(owners)) if len(owners) == 1 else "file:" + relative
        error = None
        try:
            with path.open("rb") as f:
                pointer = f.read(80).startswith(b"version https://git-lfs.github.com/spec")
            if pointer:
                audit["lfs_pointers"] += 1
            else:
                for member, rows in core.records(path, audit):
                    origin = relative + ("::" + member if member else "")
                    for index, record in enumerate(rows, 1):
                        audit["records_parsed"] += 1
                        fields = core.flatten(record)
                        normalized = canonical(fields)
                        provider_counts[(str(normalized.get("sourcename") or normalized.get("providername") or "unknown"),
                                         str(normalized.get("eventid") or "unknown"))] += 1
                        host = core.pick(fields, core.HOSTS)
                        ts = core.timestamp(core.pick(fields, core.TIMES + ("timecreated",)))
                        valid = isinstance(host, str) and bool(host.strip()) and ts is not None
                        if valid:
                            audit["records_with_host_and_time"] += 1
                            hosts.add(host.strip().lower())
                            earliest = ts if earliest is None else min(earliest, ts)
                            latest = ts if latest is None else max(latest, ts)
                        labels = sorted({m.upper() for k, v in fields.items() if k.rsplit(".", 1)[-1] in core.LABELS for m in core.TECH.findall(str(v))})
                        if not labels:
                            annotations = annotate(fields)
                            if annotations:
                                audit["rule_annotated_records"] += 1
                                if valid:
                                    audit["eligible_annotated_events"] += 1
                                    rule_counts.update(m["rule_id"] for m in annotations)
                                    annotation_events.append({"capture_id": capture, "host": host.strip().lower(),
                                        "timestamp": ts, "technique_ids": sorted({m["technique_id"] for m in annotations}),
                                        "file": origin, "record_index": index, "label_source": "rule_based_annotation",
                                        "rule_matches": compact_rule_matches(annotations)})
                                else:
                                    audit["annotated_records_missing_host_or_time"] += 1
                        if infer_techniques and not labels and valid:
                            matches = infer(fields)
                            if matches:
                                audit["inferred_behavior_events"] += 1
                                inferred_events.append({"capture_id": capture, "host": host.strip().lower(), "timestamp": ts,
                                    "technique_ids": sorted({m["technique_id"] for m in matches}), "file": origin,
                                    "record_index": index, "label_source": "inferred_behavior_not_ground_truth",
                                    "rule_matches": compact_rule_matches(matches)})
                        if not labels:
                            audit["unlabelled_records"] += 1
                            continue
                        audit["labelled_records"] += 1
                        if not valid:
                            audit["labelled_records_missing_host_or_time"] += 1
                            continue
                        audit["eligible_labelled_events"] += 1
                        events.append({"capture_id": capture, "host": host.strip().lower(), "timestamp": ts,
                                       "technique_ids": labels, "file": origin, "record_index": index,
                                       "label_source": "explicit_event_field"})
        except (OSError, ValueError, EOFError, csv.Error, tarfile.TarError, zipfile.BadZipFile) as exc:
            audit["file_errors"] += 1
            error = str(exc)
        total.update(audit)
        files.append({"file": relative, "capture_id": capture, "audit": dict(audit),
                      "hosts": sorted(hosts), "first_event": earliest, "last_event": latest, "error": error})
        print(f"[RAW] {relative}: {audit['records_parsed']} records; explicit={audit['eligible_labelled_events']}, annotated={audit['eligible_annotated_events']}")
    total["files_scanned"] = len(files)
    total["referenced_files_missing"] = sum(not p.is_file() for p in ownership)
    core.save(output / "events.json", {"schema_version": 3, "source": str(source), "events": events, "audit": dict(total)})
    core.save(output / "file_coverage.json", files)
    core.extract(output, gap, duration)
    report = render_results(output, "EXPLICIT-LABEL REFERENCE", "explicit_event_field")
    annotated_output = output / "annotated"
    core.save(annotated_output / "events.json", {"schema_version": 3, "source": str(source),
        "events": events + annotation_events, "audit": {"mapper_version": MAPPER_VERSION,
        "explicit_events": len(events), "rule_annotated_events": len(annotation_events),
        "rule_match_counts": dict(rule_counts)}})
    core.extract(annotated_output, gap, duration)
    report += "\n\n" + render_results(annotated_output, "MORDOR: EVENT-ANNOTATED RECONSTRUCTION", "explicit fields or versioned rule annotations; inspect each event label_source")
    comparison = {}
    observed = {}
    for event in events + annotation_events:
        observed.setdefault(event["capture_id"], set()).update(event["technique_ids"])
    for capture in sorted(set(expectations) | set(observed)):
        comparison[capture] = metadata_comparison(expectations.get(capture, set()), observed.get(capture, set()))
    core.save(annotated_output / "metadata_comparison.json", comparison)
    core.save(annotated_output / "annotation_coverage.json", {"mapper_version": MAPPER_VERSION,
        "rule_match_counts": dict(rule_counts), "provider_event_counts": [
            {"provider": p, "event_id": e, "records": n} for (p, e), n in provider_counts.most_common()],
        "metadata_comparison_note": "Consistency only; inventory omissions are not false-positive proof."})
    if infer_techniques:
        inferred_output = output / "experiment_b3_inferred"
        core.save(inferred_output / "events.json", {"schema_version": 3, "source": str(source),
            "events": inferred_events, "audit": {"rules_version": RULES_VERSION,
            "inferred_events": len(inferred_events), "explicit_labels_mixed_in": False}})
        core.extract(inferred_output, gap, duration)
        with contextlib.redirect_stdout(io.StringIO()):
            core.analyze(inferred_output, "Mordor B3: inferred behavior hypotheses")
        warning = ("EXPERIMENT B3: INFERRED BEHAVIOR HYPOTHESES - NOT GROUND TRUTH\n"
                   "Limited rule coverage: systeminfo, whoami, tasklist, cmd /c or /k in Sysmon process creation.\n"
                   "Benign activity may match. These are not validated attack chains.\n"
                   "Review events.json rule_matches before using these inferred labels.\n\n")
        inferred_report = warning + (inferred_output / "statistics.txt").read_text(encoding="utf-8")
        inferred_report = inferred_report.replace("EXPERIMENT B1: STRICT RECONSTRUCTION", "B3 SINGLE-LABEL HYPOTHESIS CHAINS").replace("EXPERIMENT B2: UNCERTAINTY-AWARE RECONSTRUCTION", "B3 TIME-ORDERED HYPOTHESIS SETS")
        inferred_report = inferred_report.replace("Explicit event annotations", "Inferred behavior annotations")
        (inferred_output / "statistics.txt").write_text(inferred_report, encoding="utf-8")
        for path in inferred_output.glob("experiment_b*/statistics.txt"):
            text = path.read_text(encoding="utf-8")
            text = text.replace("EXPERIMENT B1: STRICT RECONSTRUCTION", "B3 SINGLE-LABEL HYPOTHESIS CHAINS").replace("EXPERIMENT B2: UNCERTAINTY-AWARE RECONSTRUCTION", "B3 TIME-ORDERED HYPOTHESIS SETS")
            path.write_text(warning + text, encoding="utf-8")
        for path in inferred_output.rglob("statistics.json"):
            data = json.loads(path.read_text(encoding="utf-8"))
            data.update(label_source="inferred_behavior_not_ground_truth", rules_version=RULES_VERSION)
            core.save(path, data)
        report += "\n\n" + inferred_report
    report = report.replace("Input files are isolated. Cross-file campaigns require a verified capture mapping.",
                            "Files share a capture only through a unique explicit metadata reference; other files are isolated.")
    coverage = "RAW TELEMETRY COVERAGE\n" + "\n".join(f"{k}: {v}" for k, v in total.items())
    coverage += "\nHost/time coverage includes unlabelled events; these are not assigned ATT&CK techniques.\n"
    coverage += "Files explicitly referenced by one metadata capture share that capture; others remain isolated.\n"
    coverage += "Explicit-label B1/B2 contain no inferred labels or capture-level label propagation.\n\n"
    (output / "statistics.txt").write_text(coverage + report, encoding="utf-8")
    return coverage + report
