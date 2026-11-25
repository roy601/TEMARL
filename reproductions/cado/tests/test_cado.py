# -*- coding: utf-8 -*-
"""Tests for the CADO reproduction harness (standard library only; no venv, no simulator).

    python -m unittest discover -s reproductions/cado/tests
"""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import fetch  # noqa: E402
import run as R  # noqa: E402


def write(path: Path, text: str, newline="\n"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.replace("\n", newline).encode("utf-8"))


class Timing(unittest.TestCase):
    def test_the_authors_exclusion_rule(self):
        for c in ("decision_latency_us_median", "decision_latency_us_p95", "throughput_records_s", "elapsed_ms"):
            self.assertTrue(R.is_timing("primary_episode_metrics.csv", c), c)
        self.assertTrue(R.is_timing("normalization_benchmark.csv", "median_latency_us"))
        for c in ("utility", "normalized_cost", "seed", "unsafe_action_rate", "p_holm"):
            self.assertFalse(R.is_timing("summary_statistics.csv", c), c)

    def test_scientific_hash_ignores_timing_and_line_endings(self):
        with tempfile.TemporaryDirectory() as t:
            a, b, c = Path(t, "a", "m.csv"), Path(t, "b", "m.csv"), Path(t, "c", "m.csv")
            write(a, "seed,utility,decision_latency_us_median\n0,0.5,12.1\n1,0.6,13.0\n")
            write(b, "seed,utility,decision_latency_us_median\n0,0.5,99.9\n1,0.6,0.1\n", newline="\r\n")
            write(c, "seed,utility,decision_latency_us_median\n0,0.5,12.1\n1,0.7,13.0\n")
            self.assertEqual(R.scientific_sha256(a), R.scientific_sha256(b))
            self.assertNotEqual(R.scientific_sha256(a), R.scientific_sha256(c))


class Archive(unittest.TestCase):
    def test_cell_by_cell_comparison(self):
        with tempfile.TemporaryDirectory() as t:
            theirs, ours = Path(t, "theirs", "x.csv"), Path(t, "ours", "x.csv")
            write(theirs, "policy,utility,decision_latency_us_p95\nCADO,0.70200000000001,5\nStatic,0.6853,5\n")
            write(ours, "policy,utility,decision_latency_us_p95\nCADO,0.702,7\nStatic,0.6853,9\n")
            r = R.compare_csv(ours, theirs)
            self.assertTrue(r["within_1e-12"])
            self.assertNotIn("decision_latency_us_p95", r["max_abs_difference"])
            write(ours, "policy,utility,decision_latency_us_p95\nCADO,0.7021,7\nStatic,0.6853,9\n")
            r = R.compare_csv(ours, theirs)
            self.assertFalse(r["within_1e-12"])
            self.assertAlmostEqual(r["max_abs_difference"]["utility"], 1e-4)
            write(ours, "policy,utility,decision_latency_us_p95\nCADO,0.702,7\n")
            self.assertFalse(R.compare_csv(ours, theirs)["same_shape"])


class Verdict(unittest.TestCase):
    def test_rounding_rule(self):
        self.assertEqual(R.decimals("0.6853"), 4)
        self.assertEqual(R.decimals("0.002897"), 6)
        self.assertEqual(R.verdict(0.68534, "0.6853"), "MATCH")
        self.assertEqual(R.verdict(0.68525, "0.6853"), "MATCH")            # exactly half a unit
        self.assertEqual(R.verdict(0.68539, "0.6853"), "CLOSE")            # 0.9 of a unit
        self.assertEqual(R.verdict(0.68541, "0.6853"), "NO MATCH")         # 1.1 units
        self.assertEqual(R.verdict(0.6855, "0.6853"), "NO MATCH")
        self.assertEqual(R.verdict(1.0, "1.000"), "MATCH")
        self.assertEqual(R.verdict(0.0005049, "0.000505"), "MATCH")


class Lookup(unittest.TestCase):
    def test_ids_pick_one_row(self):
        with tempfile.TemporaryDirectory() as t:
            out = Path(t)
            write(out / "fresh" / "summary_statistics.csv",
                  "dataset,policy,metric,mean,ci_low,ci_high,n\nprimary,CADO,utility,0.702,0.7003,0.7038,30\n"
                  "ood,CADO,utility,0.659,0.65,0.66,30\n")
            write(out / "revision" / "heldout_summary_statistics.csv",
                  "policy,metric,mean,ci_low,ci_high,n\nConsensus,utility,0.6572,0.6523,0.662,30\n")
            write(out / "revision" / "heldout_paired_statistical_comparisons.csv",
                  "metric,comparison,mean_difference,ci_low,ci_high,p_holm,effect_size_dz\n"
                  "utility,CADO - Static,0.1,0,0.2,0.01,1\nutility,CADO - Consensus,0.001792,0.001137,0.0025,0.000505,0.932\n")
            self.assertEqual(R.lookup("T2.CADO.utility.mean", out), 0.702)             # primary, not ood
            self.assertEqual(R.lookup("T4.Consensus.utility.ci_low", out), 0.6523)
            self.assertEqual(R.lookup("T4.diff.utility.p_holm", out), 0.000505)       # CADO - Consensus only
            self.assertIsNone(R.lookup("T5.anything.at.all", out))
            with self.assertRaises(SystemExit):
                R.lookup("T2.Adaptive.utility.mean", out)                              # no row: refuse


class S1Check(unittest.TestCase):
    def test_manifest_rules(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            files = {f"f{i}.txt": f"content {i}".encode() for i in range(fetch.MANIFEST_ENTRIES - 1)}
            for n, b in files.items():
                (root / n).write_bytes(b)
            lines = [f"{hashlib.sha256(b).hexdigest()}  {n}" for n, b in files.items()]
            lines.append(f"{'0' * 64}  README.md")                     # listed, absent: as published
            (root / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
            self.assertEqual(fetch.check(root), [])
            (root / "f0.txt").write_bytes(b"edited")
            self.assertIn("changed: f0.txt", fetch.check(root))
            (root / "f0.txt").write_bytes(files["f0.txt"])
            (root / "f1.txt").unlink()
            self.assertTrue(any("missing files" in p for p in fetch.check(root)))

    def test_unpacked_supplement_is_as_published(self):
        if not (fetch.S1 / "SHA256SUMS.txt").exists():
            self.skipTest("run fetch.py first")
        self.assertEqual(fetch.check(), [])

    def test_pins_are_the_authors(self):
        if not (fetch.S1 / "requirements.txt").exists():
            self.skipTest("run fetch.py first")
        req = dict(l.split("==") for l in (fetch.S1 / "requirements.txt").read_text(encoding="utf-8").split())
        self.assertEqual(req, R.PINS)
        cfg = json.loads((fetch.S1 / "submitted_results" / "experiment_config.json").read_text(encoding="utf-8"))
        self.assertTrue(cfg["python"].startswith(R.PY_VERSION + " "))
        self.assertEqual((cfg["master_seed"], cfg["paired_seeds"], cfg["events_per_episode"]), (20260818, 30, 120))


if __name__ == "__main__":
    unittest.main()
