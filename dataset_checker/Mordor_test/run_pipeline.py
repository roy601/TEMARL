"""Audit local Mordor metadata, retaining declared-order evidence separately."""
import argparse
import math
from pathlib import Path
import config
from step1_download_mordor import run_download
from step2_extract_sequences import run_extraction
from step3_analyze import run_analysis

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", help="Local metadata directory or Security-Datasets checkout")
    parser.add_argument("--output-dir")
    parser.add_argument("--skip-download", action="store_true", help="Compatibility option; this audit is always local")
    parser.add_argument("--no-logs", action="store_true", help="Run metadata audit only")
    parser.add_argument("--infer-techniques", action="store_true", help="Also run B3: limited, unvalidated behavior hypotheses")
    parser.add_argument("--session-gap-minutes", type=float, default=30)
    parser.add_argument("--max-session-hours", type=float, default=4)
    args = parser.parse_args()
    gap, duration = args.session_gap_minutes * 60, args.max_session_hours * 3600
    if not all(math.isfinite(x) and x > 0 for x in (gap, duration)):
        parser.error("Session windows must be finite and positive")
    if args.repo:
        root = Path(args.repo).resolve()
        compound = root / "datasets" / "compound"
        config.DATA_DIR = str(compound if compound.is_dir() else root)
    if args.output_dir:
        config.OUTPUT_DIR = str(Path(args.output_dir).resolve())
    source, output = Path(config.DATA_DIR).resolve(), Path(config.OUTPUT_DIR).resolve()
    if source == output or source.is_relative_to(output):
        parser.error("Input must not be the output directory or inside it")
    run_download()
    run_extraction()
    run_analysis()
    if not args.no_logs:
        from raw_audit import run_raw_audit
        raw_report = run_raw_audit(source, output / "raw_telemetry", gap, duration, args.infer_techniques)
        metadata_report = (output / "statistics.txt").read_text(encoding="utf-8")
        metadata_report = metadata_report.replace("RAW TELEMETRY RECONSTRUCTION: NOT RUN by this metadata-only pipeline.",
                                                  "RAW TELEMETRY RECONSTRUCTION: see the raw-telemetry section below.")
        (output / "statistics.txt").write_text(metadata_report + "\n\n" + raw_report, encoding="utf-8")
        print(raw_report)

if __name__ == "__main__":
    main()
