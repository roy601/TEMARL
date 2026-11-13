"""Report declared scenario sequences separately from unordered metadata."""
import json
import statistics
from collections import Counter
from pathlib import Path
import config
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from report_format import summary_box


def load_sequences():
    path = Path(config.OUTPUT_DIR) / "sequences.json"
    sequences = json.loads(path.read_text(encoding="utf-8"))
    if any(s.get("schema_version") != 2 or s.get("ordered") is not True for s in sequences):
        raise ValueError("Legacy/unordered sequences are not valid evidence. Rerun step 2.")
    return sequences


def compute_statistics(sequences):
    lengths = [s["length"] for s in sequences]
    counts = Counter(t for s in sequences for t in set(s["techniques"]))
    return {
        "total_sequences": len(sequences),
        "avg_length": round(statistics.mean(lengths), 2) if lengths else 0,
        "median_length": statistics.median(lengths) if lengths else 0,
        "min_length": min(lengths, default=0),
        "max_length": max(lengths, default=0),
        "long_sequences_16_count": sum(n > 16 for n in lengths),
        "long_sequences_30_count": sum(n > 30 for n in lengths),
        "technique_vocab_size": len(counts),
        "top_techniques": counts.most_common(15),
        "verdict": "REQUIRES VALIDATION" if lengths else "INSUFFICIENT ORDERED EVIDENCE",
    }


def format_report(sequences, stats):
    lines = ["MORDOR ATT&CK SEQUENCE AUDIT", "",
             summary_box([s["length"] for s in sequences], stats["technique_vocab_size"]), "",
             f"Ordered scenario sequences: {stats['total_sequences']}",
             f"Unordered metadata captures: {stats.get('unordered_captures', 0)}",
             f"Excluded built-in files: {stats.get('excluded_builtin_files', 0)}",
             f"Average length: {stats['avg_length']}",
             f"Median length: {stats['median_length']}",
             f"Maximum length: {stats['max_length']}",
             f"Sequences >16: {stats['long_sequences_16_count']}",
             f"Sequences >30: {stats['long_sequences_30_count']}",
             f"Verdict: {stats['verdict']}", "",
             "Metadata mappings are inventories; their list order does not establish chronology.",
             "Simulation steps describe declared scenario order, not verified event execution.",
             "Sequence length alone does not establish suitability for model training."]
    if not sequences:
        return "No explicit ordered simulation steps found in metadata. Technique inventories are reported separately.\n"
    for seq in sequences:
        lines.extend(["", seq["scenario"], " -> ".join(seq["techniques"])])
    return "\n".join(lines) + "\n"


def run_analysis():
    sequences = load_sequences()
    stats = compute_statistics(sequences)
    output = Path(config.OUTPUT_DIR)
    audit_path = output / "extraction_audit.json"
    if audit_path.exists():
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        stats["unordered_captures"] = audit["unordered_captures"]
        stats["excluded_builtin_files"] = len(audit["excluded_builtin_files"])
    report = format_report(sequences, stats)
    inventory_path = output / "capture_inventory.json"
    inventory = json.loads(inventory_path.read_text(encoding="utf-8")) if inventory_path.exists() else []
    coverage = [len(set(s["techniques"])) for s in inventory]
    vocabulary = {t for s in inventory for t in s["techniques"]}
    stats["metadata_technique_vocabulary_size"] = len(vocabulary)
    stats["max_metadata_technique_count"] = max(coverage, default=0)
    inventory_box = summary_box(coverage, len(vocabulary)).replace("Total sequences:", "Total captures: ").replace("Sequences > 16 techniques:", "Captures > 16 techniques: ")
    report = ("MORDOR: METADATA TECHNIQUE COVERAGE\n\n" + inventory_box +
              "\nLength means distinct technique IDs per capture; metadata list order is not chronology.\n\n" +
              "DECLARED-ORDER METADATA AUDIT\n" + report +
              "\nRAW TELEMETRY RECONSTRUCTION: NOT RUN by this metadata-only pipeline.\n"
              "Zero declared-order sequences does not establish that the raw dataset lacks attack sequences.\n")
    (output / "statistics.txt").write_text(report, encoding="utf-8")
    (output / "statistics.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    print(report)


if __name__ == "__main__":
    run_analysis()
