"""Report candidate sequences without claiming validated campaign ground truth."""
import json
import statistics
from pathlib import Path
import config
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from report_format import summary_box


def renamed_box(lengths, vocabulary, total, threshold):
    return summary_box(lengths, vocabulary).replace("Total sequences:", total.ljust(len("Total sequences:"))).replace(
        "Sequences > 16 techniques:", threshold.ljust(len("Sequences > 16 techniques:")))


def analyze_sequences():
    output = Path(config.OUTPUT_DIR)
    all_sessions = json.loads((output / "sequences.json").read_text(encoding="utf-8"))
    sequences = [s for s in all_sessions if s.get("ordered") and s["length"]]
    lengths = [s["length"] for s in sequences]
    count = len(sequences)
    vocab = {t for s in sequences for t in s["sequence"]}
    captures = json.loads((output / "capture_inventory.json").read_text(encoding="utf-8"))
    audit = json.loads((output / "session_audit.json").read_text(encoding="utf-8"))
    set_lengths = [len(s["steps"]) for s in all_sessions]
    set_vocab = {t for s in all_sessions for step in s["steps"] for t in step["technique_ids"]}
    capture_lengths = [len(c["techniques"]) for c in captures]
    capture_vocab = {t for c in captures for t in c["techniques"]}
    metrics = {"total_sequences": count, "total_candidate_sessions": len(all_sessions),
               "ambiguous_sessions": len(all_sessions) - count,
               "metadata_captures": len(captures),
               "single_technique_captures": sum(len(c["techniques"]) == 1 for c in captures),
               "average_length": statistics.mean(lengths) if lengths else 0,
               "median_length": statistics.median(lengths) if lengths else 0,
               "min_length": min(lengths, default=0), "max_length": max(lengths, default=0),
               "std_dev_length": statistics.pstdev(lengths) if lengths else 0,
               "technique_vocabulary_size": len(vocab),
               "multi_unique_technique_sequences": sum(s["unique_technique_count"] > 1 for s in sequences),
               "verdict": "REQUIRES VALIDATION" if count else "INSUFFICIENT ORDERED EVENT EVIDENCE",
               "session_audit": audit}
    metrics["metadata_coverage"] = {"total_captures": len(captures), "technique_vocabulary_size": len(capture_vocab),
                                    "max_distinct_techniques": max(capture_lengths, default=0)}
    metrics["experiment_b2"] = {"total_sessions": len(all_sessions), "max_label_set_length": max(set_lengths, default=0),
                                 "average_label_set_length": statistics.mean(set_lengths) if set_lengths else 0,
                                 "sessions_gt_16": sum(n > 16 for n in set_lengths), "technique_vocabulary_size": len(set_vocab)}
    coverage_counts = audit["scan_audit"]
    metrics["coverage_status"] = "PARTIAL / REVIEW COVERAGE" if any(coverage_counts.get(k, 0) for k in (
        "file_errors", "metadata_errors", "referenced_files_missing", "lfs_pointers", "unparsed_lines",
        "malformed_records", "unsupported_records", "unsupported_files", "unsupported_archive_members",
        "unsupported_archives", "unsupported_xml_chunks", "unparsed_xml_trailers")) else "NO RECORDED PARSE GAPS"
    if coverage_counts.get("telemetry_scan_skipped"):
        metrics["coverage_status"] = "METADATA ONLY / TELEMETRY NOT SCANNED"
    for name, predicate in [("eq_1", lambda n: n == 1), ("gt_1", lambda n: n > 1),
                            ("gt_16", lambda n: n > 16), ("gt_30", lambda n: n > 30)]:
        number = sum(predicate(n) for n in lengths)
        metrics[f"sequences_{name}"] = number
        metrics[f"pct_sequences_{name}"] = number / count * 100 if count else 0
    lines = ["SPLUNK ATTACK DATA SEQUENCE AUDIT", "",
             "METADATA: UNORDERED CAPTURE COVERAGE",
             renamed_box(capture_lengths, len(capture_vocab), "Total captures:", "Captures > 16 techniques:"),
             "Length counts distinct technique IDs per capture; metadata order is not chronology.", "",
             "B1: STRICT EVENT RECONSTRUCTION",
             summary_box(lengths, len(vocab)), "",
             "B2: UNCERTAINTY-AWARE EVENT RECONSTRUCTION",
             renamed_box(set_lengths, len(set_vocab), "Total sessions:", "Sessions > 16 set-steps:"),
             "B2 retains all candidate sessions, including B1. Labels within a step are unordered.",
             "B2 length counts consecutive distinct label sets, not individually ordered techniques.", "",
             "Lengths count steps after consecutive duplicate removal, not unique techniques.",
             "Metadata labels are unordered capture annotations, excluded from event sequences.",
             "Host/time proximity produces candidates; it does not establish an attack campaign.", ""]
    lines.extend(f"{key}: {value}" for key, value in metrics.items() if key != "session_audit")
    lines.extend(["", "SCAN / SESSION COVERAGE", json.dumps(audit, indent=2), "", "LONGEST ORDERED CANDIDATES"])
    for session in sorted(sequences, key=lambda s: s["length"], reverse=True)[:20]:
        lines.extend([session["scenario_name"],
                      f"  Length={session['length']}; unique={session['unique_technique_count']}; raw={session['raw_length']}",
                      "  " + " -> ".join(session["sequence"][:30])])
    report = "\n".join(lines)
    (output / "statistics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (output / "statistics.txt").write_text(report, encoding="utf-8")
    print(report.encode("ascii", errors="replace").decode("ascii"))
    return metrics


if __name__ == "__main__":
    analyze_sequences()
