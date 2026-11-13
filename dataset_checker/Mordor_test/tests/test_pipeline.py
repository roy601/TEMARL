import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import config
import step2_extract_sequences as extraction
import step3_analyze as analysis


class PipelineTests(unittest.TestCase):
    def test_inventory_and_builtin_are_not_sequences(self):
        with tempfile.TemporaryDirectory() as root:
            data, output = Path(root) / "data", Path(root) / "output"
            data.mkdir()
            (data / "capture.yaml").write_text("title: Capture\nattack_mappings:\n- technique: T1059\n- technique: T1003\n")
            built = data / "_evaluation_steps"
            built.mkdir()
            (built / "demo.yaml").write_text("simulation:\n  steps:\n  - technique: T1059\n")
            with patch.object(config, "DATA_DIR", str(data)), patch.object(config, "OUTPUT_DIR", str(output)):
                extraction.run_extraction()
                analysis.run_analysis()
                self.assertEqual(json.loads((output / "sequences.json").read_text()), [])
                stats = json.loads((output / "statistics.json").read_text())
                self.assertEqual(stats["unordered_captures"], 1)
                self.assertEqual(stats["excluded_builtin_files"], 1)
                self.assertEqual(stats["total_sequences"], 0)

    def test_numeric_steps_and_repeated_technique(self):
        steps = extraction.extract_from_simulation_steps({"simulation": {"steps": [
            {"step_id": 10, "technique": "T1059"},
            {"step_id": 2, "technique": "T1003"},
            {"step_id": 1, "technique": "T1059"}]}})
        self.assertEqual([s["technique"] for s in steps], ["T1059", "T1003", "T1059"])

    def test_report_counts_sequence_presence(self):
        seq = {"scenario": "test", "length": 3, "techniques": ["T1059", "T1003", "T1059"]}
        stats = analysis.compute_statistics([seq])
        self.assertEqual(dict(stats["top_techniques"])["T1059"], 1)
        self.assertIn("REQUIRES VALIDATION", analysis.format_report([seq], stats))

    def test_reject_legacy_output(self):
        with tempfile.TemporaryDirectory() as root:
            (Path(root) / "sequences.json").write_text('[{"length": 10}]')
            with patch.object(config, "OUTPUT_DIR", root), self.assertRaises(ValueError):
                analysis.load_sequences()


if __name__ == "__main__":
    unittest.main()
