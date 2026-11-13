import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from raw_audit import run_raw_audit
from behavior_rules import infer


class RawAuditTests(unittest.TestCase):
    def test_annotation_pipeline_and_inventory_consistency(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "compound"
            source.mkdir()
            (source / "capture.yaml").write_text("attack_mappings:\n- technique: T1082\n- technique: T1003\n  sub-technique: '001'\nfiles:\n- link: https://raw.githubusercontent.com/OTRF/Security-Datasets/master/datasets/compound/events.jsonl\n")
            event = {"Hostname": "host", "TimeCreated": "2024-01-01T00:00:00Z", "SourceName": "Microsoft-Windows-Sysmon", "EventID": 1,
                     "Image": "C:\\Windows\\System32\\systeminfo.exe", "CommandLine": "systeminfo"}
            (source / "events.jsonl").write_text(json.dumps(event))
            output = root / "out"
            report = run_raw_audit(source, output)
            explicit = json.loads((output / "events.json").read_text())["events"]
            self.assertEqual(explicit, [])
            annotated = json.loads((output / "annotated/events.json").read_text())["events"]
            self.assertEqual(annotated[0]["technique_ids"], ["T1082"])
            self.assertEqual(annotated[0]["label_source"], "rule_based_annotation")
            self.assertEqual(annotated[0]["record_index"], 1)
            comparison = json.loads((output / "annotated/metadata_comparison.json").read_text())["capture.yaml"]
            self.assertEqual(comparison["exact_overlap"], ["T1082"])
            self.assertEqual(comparison["expected_not_observed"], ["T1003.001"])
            self.assertIn("No supported evidence", report)
            self.assertIn("MORDOR: EVENT-ANNOTATED RECONSTRUCTION", report)

    def test_inference_requires_provider_and_process_creation(self):
        e = {"sourcename": "Microsoft-Windows-Sysmon", "eventid": 1,
             "image": "C:\\Windows\\System32\\systeminfo.exe", "commandline": "systeminfo"}
        self.assertEqual(infer(e)[0]["technique_id"], "T1082")
        self.assertEqual(infer(dict(e, eventid=10)), [])
        self.assertEqual(infer(dict(e, sourcename="other")), [])
        self.assertEqual(infer(dict(e, image="not-systeminfo.exe")), [])
        self.assertEqual(infer(dict(e, commandline="")), [])
        self.assertEqual(infer(dict(e, image="cmd.exe", commandline="cmd.exe")), [])
        self.assertEqual(infer(dict(e, image="cmd.exe", commandline="cmd.exe /c whoami"))[0]["technique_id"], "T1059.003")

    def test_archive_labels_and_unlabelled_coverage(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "compound"
            source.mkdir()
            rows = [dict(Hostname="host", TimeCreated="2024-01-01T00:00:00Z", Image="powershell.exe"),
                    dict(Hostname="host", TimeCreated="2024-01-01T00:00:01Z", RuleName="technique_id=T1059.001"),
                    dict(Hostname="host", TimeCreated="2024-01-01T00:00:02Z", RuleName="T1003.001 T1105")]
            with zipfile.ZipFile(source / "events.zip", "w") as archive:
                archive.writestr("events.json", "\n".join(json.dumps(r) for r in rows))
            (source / "metadata.yaml").write_text("files:\n- link: https://raw.githubusercontent.com/OTRF/Security-Datasets/master/datasets/compound/events.zip\n")
            output = root / "out"
            run_raw_audit(source, output)
            audit = json.loads((output / "audit.json").read_text())
            self.assertEqual(audit["records_parsed"], 3)
            self.assertEqual(audit["records_with_host_and_time"], 3)
            self.assertEqual(audit["unlabelled_records"], 1)
            session = json.loads((output / "sequences.json").read_text())["sessions"][0]
            self.assertEqual(session["capture_id"], "metadata.yaml")
            self.assertEqual(session["label_set_length"], 2)
            self.assertFalse(session["ordered"])


if __name__ == "__main__":
    unittest.main()
