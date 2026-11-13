import io
import json
import tempfile
import subprocess
import sys
import unittest
import zipfile
from pathlib import Path
import audit_core as core


class AuditTests(unittest.TestCase):
    def test_windows_combined_export_is_not_double_counted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "scenario_manifest.csv").write_text("Scenrario_ID,Simulated Techniques\nS01,T1059\n")
            data = "timestamp,host,technique_id\n1704067200,one,T1059\n"
            (root / "01-03-December.csv").write_text(data)
            (root / "combined.csv").write_text(data)
            events, audit = core.scan(root, root / "out")
            self.assertEqual(len(events), 1)
            self.assertEqual(audit["combined_exports_skipped"], 1)

    def test_windows_wazuh_csv_schema(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "wazuh.csv").write_text('_source.agent.name,_source.timestamp,_source.rule.mitre.id\nHOST,"Nov 30, 2024 @ 20:30:08.057",T1059.001\nHOST,"Nov 30, 2024 @ 20:30:09.057",T1003.001\n')
            events, audit = core.scan(root, root / "out")
            self.assertEqual(len(events), 2)
            self.assertEqual(core.sessions(events)[0]["sequence"], ["T1059.001", "T1003.001"])

    def test_windows_and_optc_cli_end_to_end(self):
        workspace = Path(__file__).resolve().parent.parent
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "raw"
            source.mkdir()
            (source / "telemetry.csv").write_text("timestamp,host,technique_id\n1704067200,host,T1059\n1704067201,host,T1003\n")
            for folder in ("Win_APT_test", "DARPA_OpTC_test"):
                output = root / folder
                run = subprocess.run([sys.executable, str(workspace / folder / "run_pipeline.py"),
                                      "--input-dir", str(source), "--output-dir", str(output)],
                                     capture_output=True, text=True)
                self.assertEqual(run.returncode, 0, run.stderr)
                metrics = json.loads((output / "statistics.json").read_text())
                self.assertEqual((metrics["experiment_b"] if folder == "Win_APT_test" else metrics)["max_length"], 2)

    def test_official_manifest_coverage(self):
        workspace = Path(__file__).resolve().parent.parent
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "raw"
            source.mkdir()
            (source / "scenario_manifest.csv").write_text("Scenrario_ID,Scenario_Name,Simulated Techniques\nS01,Example,T1059; T1003; T1059\nS02,Other,T1047\n")
            output = root / "out"
            run = subprocess.run([sys.executable, str(workspace / "Win_APT_test/run_pipeline.py"),
                "--input-dir", str(source), "--output-dir", str(output), "--experiment", "a"], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            stats = json.loads((output / "statistics.json").read_text())["experiment_a"]
            self.assertEqual(stats["total_scenarios"], 2)
            self.assertEqual(stats["max_technique_count"], 2)
            self.assertFalse(stats["ordered"])

    def event(self, ts, label="T1059", host="one", capture="capture"):
        return dict(timestamp=ts, technique_ids=[label], host=host,
                    capture_id=capture, file="events.jsonl", record_index=1)

    def test_numeric_time_units_and_offsets(self):
        expected = 1704067200
        for x in (expected, expected * 1000, expected * 1000000, expected * 1000000000,
                  "2024-01-01T06:00:00+06:00"):
            self.assertEqual(core.timestamp(x), expected)
        for x in (None, "2024-01-01", "123", float("nan"), True):
            self.assertIsNone(core.timestamp(x))

    def test_session_boundaries_and_ambiguity(self):
        rows = [self.event(10), self.event(20, "T1003"), self.event(100),
                self.event(10, host="two"), self.event(10, capture="other")]
        self.assertEqual(len(core.sessions(rows, 30, 60)), 4)
        s = core.sessions([self.event(1), self.event(1, "T1003")])[0]
        self.assertFalse(s["ordered"])
        self.assertEqual(s["sequence"], [])
        for gap in (0, float("inf"), float("nan")):
            with self.assertRaises(ValueError):
                core.sessions([], gap)

    def test_duplicate_collapse_preserves_return(self):
        s = core.sessions([self.event(4), self.event(2), self.event(1), self.event(3, "T1003")])[0]
        self.assertEqual(s["sequence"], ["T1059", "T1003", "T1059"])

    def test_multilabel_session_retained_without_inventing_order(self):
        rows = [self.event(1), self.event(1, "T1003"), self.event(2, "T1021")]
        s = core.sessions(rows)[0]
        self.assertFalse(s["ordered"])
        self.assertEqual(s["sequence"], [])
        self.assertEqual(s["label_set_sequence"], [["T1003", "T1059"], ["T1021"]])
        self.assertEqual(s["label_set_length"], 2)
        self.assertIn("multiple_events_same_timestamp", s["ambiguity_reasons"])
        with tempfile.TemporaryDirectory() as directory:
            core.save(Path(directory) / "sequences.json", {"schema_version": 3, "sessions": [s]})
            metrics = core.analyze(directory, "ambiguous-only")
            self.assertEqual(metrics["label_set_sessions"], 1)
            self.assertEqual(metrics["total_sequences"], 0)
            self.assertEqual(metrics["verdict"], "REQUIRES VALIDATION")

    def test_scan_and_reports(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, output = root / "raw", root / "out"
            source.mkdir()
            rows = [dict(timestamp="2024-01-01T00:00:00Z", host="one", technique_id="T1059"),
                    dict(timestamp="2024-01-01T00:00:01Z", host="one", technique_id="T1003"),
                    dict(host="one", technique_id="T1003"),
                    dict(host="one", process="powershell.exe")]
            (source / "events.json").write_text(json.dumps(rows))
            core.ingest(source, output)
            core.extract(output)
            stats = core.analyze(output, "fixture")
            self.assertEqual(stats["max_length"], 2)
            audit = json.loads((output / "audit.json").read_text())
            self.assertEqual(audit["labelled_records_missing_host_or_time"], 1)
            self.assertEqual(audit["unlabelled_records"], 1)

    def test_archive_not_extracted_and_csv_overflow(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            csv = "timestamp,host,technique_id\n1704067200,one,T1059,extra\n"
            with zipfile.ZipFile(root / "data.zip", "w") as archive:
                archive.writestr("../outside.csv", csv)
            events, audit = core.scan(root, root / "out")
            self.assertEqual(len(events), 1)
            self.assertFalse((root.parent / "outside.csv").exists())

    def test_empty_report_and_legacy_rejection(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            core.save(root / "sequences.json", {"schema_version": 3, "sessions": []})
            self.assertEqual(core.analyze(root, "empty")["total_sequences"], 0)
            core.save(root / "sequences.json", [])
            with self.assertRaises(ValueError):
                core.analyze(root, "legacy")

    def test_nested_host_conflict_and_generated_exclusion(self):
        self.assertIsNone(core.pick(core.flatten({"a": {"hostname": "one"}, "b": {"hostname": "two"}}), core.HOSTS))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "optc_ground_truth_sample.json").write_text('{"technique_id":"T1059"}')
            events, audit = core.scan(root, root / "out")
            self.assertEqual(events, [])
            self.assertEqual(audit["generated_or_cached_files_skipped"], 1)


if __name__ == "__main__":
    unittest.main()
