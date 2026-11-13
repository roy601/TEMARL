import json
from pathlib import Path
import tempfile
import unittest
import gzip
import zipfile
from unittest.mock import patch
from collections import Counter
import config
from step1_download_splunk import parse_timestamp, read_records, scan_splunk_datasets, fields, find_repository, telemetry_records
from step2_extract_sequences import build_sequences, extract_sequences
from step3_analyze import analyze_sequences


class SessionTests(unittest.TestCase):
    def event(self, time, tech="T1059.001", capture="capture-a", host="host-a", index=1):
        return dict(timestamp=time, technique_ids=[tech], capture_id=capture,
                    host=host, file="events.jsonl", record_index=index)

    def test_capture_host_and_windows(self):
        records = [self.event(0), self.event(10, "T1003.001"), self.event(100),
                   self.event(0, capture="capture-b"), self.event(0, host="host-b")]
        sessions, excluded = build_sequences(records, gap_seconds=30, max_duration_seconds=90)
        self.assertEqual(len(sessions), 4)
        self.assertEqual(sessions[0]["sequence"], ["T1059.001", "T1003.001"])
        self.assertEqual(excluded, 0)
        sessions, _ = build_sequences([self.event(t) for t in (0, 20, 40, 60)], 30, 60)
        self.assertEqual(len(sessions), 2)

    def test_numeric_order_and_repeated_flow(self):
        events = [self.event(100, "T1003.001"), self.event(9), self.event(10), self.event(110)]
        sessions, _ = build_sequences(events)
        self.assertEqual(sessions[0]["sequence"], ["T1059.001", "T1003.001", "T1059.001"])
        self.assertEqual(sessions[0]["unique_technique_count"], 2)

    def test_missing_and_simultaneous(self):
        records = [self.event(None), self.event(1, host=None), self.event(10), self.event(10, "T1003.001")]
        sessions, excluded = build_sequences(records)
        self.assertEqual(excluded, 2)
        self.assertFalse(sessions[0]["ordered"])
        self.assertEqual(sessions[0]["sequence"], [])
        self.assertEqual(len(sessions[0]["steps"][0]["technique_ids"]), 2)

    def test_timestamps(self):
        self.assertEqual(parse_timestamp("2024-01-01T06:00:00+06:00"), parse_timestamp("2024-01-01T00:00:00Z"))
        self.assertEqual(parse_timestamp("1704067200000"), parse_timestamp("1704067200"))
        for value in ("123", "2024-01-01", "pid=1704067200", "garbage", float("nan")):
            self.assertIsNone(parse_timestamp(value))


class PipelineTests(unittest.TestCase):
    def test_archives_template_and_file_coverage(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = root / "repo"
            repo.mkdir()
            record = json.dumps({"timestamp": "2024-01-01T00:00:00Z", "host": "host", "RuleName": "T1059.001"})
            with zipfile.ZipFile(repo / "logs.zip", "w") as archive:
                archive.writestr("one.jsonl", record)
                archive.writestr("two.jsonl", record)
                archive.writestr("unsupported.bin", "not telemetry")
            with gzip.open(repo / "events.jsonl.gz", "wt") as stream:
                stream.write(record)
            (repo / "TEMPLATE.yml").write_text("datasets: [{path: missing.log}]\n")
            (repo / "unsupported.evtx").write_bytes(b"unsupported")
            with patch.object(config, "DATA_DIR", str(root / "data")), patch.object(config, "OUTPUT_DIR", str(root / "output")):
                payload = json.loads(Path(scan_splunk_datasets(repo)).read_text())
                self.assertEqual(len(payload["events"]), 3)
                self.assertEqual(len({e["capture_id"] for e in payload["events"]}), 3)
                self.assertEqual(payload["audit"]["templates_skipped"], 1)
                self.assertEqual(payload["audit"]["referenced_files_missing"], 0)
                self.assertEqual(payload["audit"]["unsupported_files"], 1)
                self.assertEqual(payload["audit"]["unsupported_archive_members"], 1)
                self.assertTrue((root / "data" / "file_coverage.json").is_file())
                extract_sequences()
                metrics = analyze_sequences()
                self.assertEqual(metrics["experiment_b2"]["total_sessions"], 3)
                self.assertEqual(metrics["coverage_status"], "PARTIAL / REVIEW COVERAGE")

    def test_b2_retains_ambiguous_sessions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sessions, _ = build_sequences([SessionTests().event(10), SessionTests().event(10, "T1003.001")])
            (root / "sequences.json").write_text(json.dumps(sessions))
            (root / "capture_inventory.json").write_text("[]")
            (root / "session_audit.json").write_text('{"scan_audit": {}}')
            with patch.object(config, "OUTPUT_DIR", str(root)):
                metrics = analyze_sequences()
            self.assertEqual(metrics["total_sequences"], 0)
            self.assertEqual(metrics["experiment_b2"]["total_sessions"], 1)
            self.assertEqual(metrics["experiment_b2"]["technique_vocabulary_size"], 2)

    def test_surplus_csv_fields(self):
        self.assertEqual(fields({"Computer": "host", None: ["extra"]}), {"computer": "host"})

    def test_explicit_missing_repo_does_not_fall_back(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(config, "BASE_DIR", directory), self.assertRaises(FileNotFoundError):
                (Path(directory) / "attack_data").mkdir()
                find_repository(Path(directory) / "missing")

    def test_xml_files_are_scanned(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = root / "repo"
            repo.mkdir()
            (repo / "events.xml").write_text('<Event><System><TimeCreated SystemTime="2024-01-01T00:00:00Z"/><Computer>host</Computer></System><EventData><Data Name="RuleName">T1059.001</Data></EventData></Event>')
            with patch.object(config, "DATA_DIR", str(root / "data")):
                result = json.loads(Path(scan_splunk_datasets(repo)).read_text())
            self.assertEqual(len(result["events"]), 1)

    def test_formats(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, content in {
                "array.json": '[\n{"technique_id":"T1003.001"}\n]',
                "object.json": '{\n"technique_id":"T1003.001"\n}',
                "events.csv": 'Computer,technique_id\nhost,T1003.001\n',
                "events.log": '<Event><System><TimeCreated SystemTime="2024-01-01T00:00:00Z"/><Computer>host</Computer></System><EventData><Data Name="RuleName">technique_id=T1003.001</Data></EventData></Event>\n',
            }.items():
                path = root / name
                path.write_text(content, encoding="utf-8")
                records = list(read_records(path, Counter()))
                self.assertEqual(len(records), 1, name)
            pointer = root / "pointer.log"
            pointer.write_text("version https://git-lfs.github.com/spec/v1\noid sha256:123", encoding="utf-8")
            audit = Counter()
            self.assertEqual(list(read_records(pointer, audit)), [])
            self.assertEqual(audit["lfs_pointers"], 1)

    def test_end_to_end_metadata_not_events_and_no_heuristics(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = root / "repo"
            capture = repo / "datasets" / "T1059.001" / "capture"
            capture.mkdir(parents=True)
            (capture / "capture.yml").write_text('id: example\nmitre_technique: [T1059.001, T1003.001]\ndatasets:\n  - path: /datasets/T1059.001/capture/events.jsonl\n', encoding="utf-8")
            records = [
                {"timestamp": "2024-01-01T00:00:00Z", "Computer": "HOST", "Image": "powershell.exe", "CommandLine": "lsass T1047"},
                {"timestamp": "2024-01-01T00:00:01Z", "Computer": "HOST", "technique_id": "T1059.001"},
                {"timestamp": "2024-01-01T00:00:02Z", "Computer": "host", "technique_id": "T1003.001"},
                {"Computer": "host", "technique_id": "T1047"},
            ]
            (capture / "events.jsonl").write_text("\n".join(json.dumps(r) for r in records), encoding="utf-8")
            with patch.object(config, "DATA_DIR", str(root / "data")), patch.object(config, "OUTPUT_DIR", str(root / "output")):
                path = scan_splunk_datasets(repo)
                payload = json.loads(Path(path).read_text(encoding="utf-8"))
                self.assertEqual(len(payload["captures"]), 1)
                self.assertEqual(len(payload["events"]), 3)
                sessions = extract_sequences()
                self.assertEqual(sessions[0]["sequence"], ["T1059.001", "T1003.001"])
                metrics = analyze_sequences()
                self.assertEqual(metrics["max_length"], 2)
                self.assertEqual(metrics["verdict"], "REQUIRES VALIDATION")
                scan_splunk_datasets(repo, no_logs=True)
                self.assertEqual(extract_sequences(), [])
                self.assertEqual(analyze_sequences()["total_sequences"], 0)

    def test_legacy_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "splunk_attack_data_ground_truth.json").write_text('{"folder": []}', encoding="utf-8")
            with patch.object(config, "DATA_DIR", directory), self.assertRaisesRegex(ValueError, "Legacy"):
                extract_sequences()


if __name__ == "__main__":
    unittest.main()
