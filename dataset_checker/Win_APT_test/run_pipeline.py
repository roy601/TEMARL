"""Windows APT: A = manifest coverage; B = timestamp-ordered event candidates."""
import argparse
import csv
import math
import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import audit_core
from report_format import summary_box


def key(value):
    return re.sub(r"[^a-z0-9]", "", value.lower())


def experiment_a(manifest, output):
    """Read scenario annotations without assuming list order is chronology."""
    scenarios = {}
    missing = 0
    if manifest:
        with Path(manifest).open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            columns = {key(c): c for c in (reader.fieldnames or [])}
            id_col = next((columns[c] for c in ("scenarioid", "scenrarioid") if c in columns), None)
            tech_col = next((columns[c] for c in ("simulatedtechniques", "techniqueid", "techniques", "technique") if c in columns), None)
            name_col = columns.get("scenarioname")
            if not id_col or not tech_col:
                raise ValueError("Manifest requires Scenario_ID (or Scenrario_ID) and Simulated Techniques/technique_id columns")
            # The previous generator wrote these four columns without provenance.
            if set(columns) == {"scenarioid", "scenarioname", "steporder", "techniqueid"}:
                raise ValueError("Legacy four-column generated manifest is not accepted. Use the official scenario manifest.")
            for index, row in enumerate(reader, 2):
                sid = str(row.get(id_col) or "").strip()
                labels = {m.upper() for m in audit_core.TECH.findall(str(row.get(tech_col) or ""))}
                if not sid or not labels:
                    missing += 1
                    continue
                entry = scenarios.setdefault(sid, {"scenario_id": sid,
                    "scenario_name": str(row.get(name_col) or sid), "techniques": set(),
                    "source_rows": [], "ordered": False})
                entry["techniques"].update(labels)
                entry["source_rows"].append(index)
    inventory = []
    for entry in scenarios.values():
        entry["techniques"] = sorted(entry["techniques"])
        entry["technique_count"] = len(entry["techniques"])
        inventory.append(entry)
    lengths = [s["technique_count"] for s in inventory]
    vocabulary = {t for s in inventory for t in s["techniques"]}
    metrics = {"total_scenarios": len(inventory), "average_technique_count": statistics.mean(lengths) if lengths else 0,
        "median_technique_count": statistics.median(lengths) if lengths else 0,
        "min_technique_count": min(lengths, default=0), "max_technique_count": max(lengths, default=0),
        "std_dev_technique_count": statistics.pstdev(lengths) if lengths else 0,
        "scenarios_gt_16": sum(n > 16 for n in lengths), "technique_vocabulary_size": len(vocabulary),
        "rows_missing_id_or_techniques": missing, "manifest": str(Path(manifest).resolve()) if manifest else None,
        "ordered": False, "status": "SCENARIO COVERAGE ONLY" if inventory else "NO MANIFEST EVIDENCE"}
    audit_core.save(Path(output) / "capture_inventory.json", inventory)
    audit_core.save(Path(output) / "statistics.json", metrics)
    box = summary_box(lengths, len(vocabulary)).replace("Total sequences:", "Total scenarios:")
    box = box.replace("Sequences > 16 techniques:", "Scenarios > 16 techniques:")
    report = "EXPERIMENT A: SCENARIO TECHNIQUE COVERAGE\n\n" + box
    report += "\n\nLength means distinct technique IDs per scenario, NOT ordered execution steps.\n"
    report += "Manifest list order does not establish chronology or successful execution.\n"
    report += f"Status: {metrics['status']}\nRows skipped: {missing}\n"
    (Path(output) / "statistics.txt").write_text(report, encoding="utf-8")
    return report


def main():
    base = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", default=str(base / "data"))
    parser.add_argument("--output-dir", default=str(base / "output_verified"))
    parser.add_argument("--manifest", help="Official scenario_manifest.csv; otherwise auto-discovered under input-dir")
    parser.add_argument("--experiment", choices=("a", "b", "both"), default="both")
    parser.add_argument("--session-gap-minutes", type=float, default=30)
    parser.add_argument("--max-session-hours", type=float, default=4)
    args = parser.parse_args()
    source, output = Path(args.input_dir).resolve(), Path(args.output_dir).resolve()
    if not source.is_dir():
        parser.error(f"Input directory does not exist: {source}")
    if source == output or source.is_relative_to(output):
        parser.error("Input must not be inside output")
    gap, duration = args.session_gap_minutes * 60, args.max_session_hours * 3600
    if not all(math.isfinite(x) and x > 0 for x in (gap, duration)):
        parser.error("Session windows must be finite and positive")
    reports = []
    combined_metrics = {}
    if args.experiment in ("a", "both"):
        candidates = [Path(args.manifest).resolve()] if args.manifest else sorted(
            p for p in source.rglob("*.csv") if p.name.lower() == "scenario_manifest.csv" and not p.is_relative_to(output))
        if len(candidates) > 1:
            parser.error("Multiple manifests found; select the official one with --manifest")
        destination = output / "experiment_a"
        reports.append(experiment_a(candidates[0] if candidates else None, destination))
        import json
        combined_metrics["experiment_a"] = json.loads((destination / "statistics.json").read_text())
    if args.experiment in ("b", "both"):
        destination = output / "experiment_b"
        audit_core.ingest(source, destination)
        audit_core.extract(destination, gap, duration)
        combined_metrics["experiment_b"] = audit_core.analyze(destination, "Windows APT - Experiment B")
        reports.append("EXPERIMENT B: RAW EVENT CANDIDATE SESSIONS\n\n" + (destination / "statistics.txt").read_text())
    output.mkdir(parents=True, exist_ok=True)
    report = "\n\n".join(reports)
    (output / "statistics.txt").write_text(report, encoding="utf-8")
    audit_core.save(output / "statistics.json", combined_metrics)
    print(report)


if __name__ == "__main__":
    main()
