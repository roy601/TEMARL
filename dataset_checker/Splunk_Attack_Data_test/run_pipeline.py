"""Run the local Splunk Attack Data capture and session audit."""
import argparse
from pathlib import Path
import config
import step1_download_splunk
import step2_extract_sequences
import step3_analyze


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", help="Path to a local attack_data checkout")
    parser.add_argument("--output-dir", help="Report directory, outside the repository")
    parser.add_argument("--no-logs", action="store_true", help="Audit metadata only; omit telemetry parsing")
    parser.add_argument("--session-gap-minutes", type=float, default=30)
    parser.add_argument("--max-session-hours", type=float, default=4)
    args = parser.parse_args()
    repo = step1_download_splunk.find_repository(args.repo)
    if args.output_dir:
        config.OUTPUT_DIR = str(Path(args.output_dir).resolve())
        config.DATA_DIR = str(Path(config.OUTPUT_DIR) / "intermediate")
    if Path(config.OUTPUT_DIR).resolve().is_relative_to(repo) or Path(config.DATA_DIR).resolve().is_relative_to(repo):
        parser.error("Output and intermediate directories must be outside the input repository")
    if not 0 < args.session_gap_minutes < float("inf") or not 0 < args.max_session_hours < float("inf"):
        parser.error("Session windows must be finite and positive")
    config.SESSION_GAP_SECONDS = args.session_gap_minutes * 60
    config.SESSION_MAX_DURATION_SECONDS = args.max_session_hours * 3600
    step1_download_splunk.run_download(no_logs=args.no_logs, repo_path=repo)
    step2_extract_sequences.extract_sequences()
    step3_analyze.analyze_sequences()


if __name__ == "__main__":
    main()
