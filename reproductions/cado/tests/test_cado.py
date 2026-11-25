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
        self.assertEqual(R.verdict(-0.000208, "-0.000208"), "MATCH")

    def test_scientific_notation_counts_and_timings(self):
        self.assertEqual(R.decimals("3.35e-8"), 10)
        self.assertEqual(R.verdict(3.3527612686157227e-08, "3.35e-8"), "MATCH")
        self.assertEqual(R.verdict(3.36e-08, "3.35e-8"), "CLOSE")
        self.assertEqual(R.verdict(3.4e-08, "3.35e-8"), "NO MATCH")
        exact = "exact: MATCH only if equal"
        self.assertEqual(R.verdict(300.0, "300", exact), "MATCH")
        self.assertEqual(R.verdict(299.0, "300", exact), "NO MATCH")
        self.assertEqual(R.verdict(0.999, "1", exact), "NO MATCH")             # 'all' means all
        self.assertEqual(R.verdict(1.0, "7.31", "NOT ATTEMPTED: host timing"), "NOT ATTEMPTED")

    def test_paper_verdict(self):
        rows = [{"id": "a", "primary": True, "verdict": "MATCH"}, {"id": "b", "primary": False, "verdict": "NO MATCH"},
                {"id": "t", "primary": False, "verdict": "NOT ATTEMPTED"}]
        self.assertTrue(R.paper_verdict(rows).startswith("reproduced"))       # a secondary miss is reported, not decisive
        rows.append({"id": "c", "primary": True, "verdict": "CLOSE"})
        self.assertEqual(R.paper_verdict(rows), "partially reproduced; primary targets not MATCH: c")


class Targets(unittest.TestCase):
    def test_targets_file(self):

        rows = R.read_csv(HERE / "TARGETS.csv")
        self.assertEqual((len(rows), sum(r["primary"] == "yes" for r in rows)), (333, 208))   # DECISIONS 16, 18
        prefixes = {"T2", "T3", "T4", "T5", "T6", "S44", "S51", "S52", "S54", "S55", "S56", "TIME"}
        for r in rows:
            self.assertIn(r["id"].split(".")[0], prefixes, r["id"])
            if r["id"].startswith("TIME."):
                self.assertTrue(r["tolerance"].startswith("NOT ATTEMPTED"))
                self.assertEqual(r["primary"], "no")
            else:
                float(r["published"])
        self.assertFalse(any(r["id"].startswith("T3.") and r["id"].split(".")[2] == "Consensus"
                             and r["id"].endswith("fallback_rate") for r in rows))      # by definition, not a target


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
            self.assertIsNone(R.lookup("TIME.policy_p95_latency_CADO_us", out))
            with self.assertRaises(SystemExit):
                R.lookup("T2.Adaptive.utility.mean", out)                              # no row: refuse
            with self.assertRaises(SystemExit):
                R.lookup("T9.anything.at.all", out)                                    # unknown id: refuse

    def test_table3_table5_and_section_lookups(self):
        with tempfile.TemporaryDirectory() as t:
            out = Path(t)
            write(out / "fresh" / "summary_statistics.csv",
                  "dataset,policy,metric,mean,ci_low,ci_high,n\nprimary,Consensus,utility,0.6953,0,1,30\n"
                  "ood,CADO,fallback_rate,0.9868,0.9831,0.9904,30\nfault,CADO,rollback_success_rate,0.9804,0,1,30\n")
            write(out / "fresh" / "ablation_summary.csv",
                  "dataset,policy,utility,fallback_rate\nprimary,CADO-NoEvidence,0.7024,0.961\nood,CADO-NoEvidence,0.1,0.2\n")
            write(out / "fresh" / "ablation_episode_metrics.csv",
                  "dataset,policy,gate_ood\nprimary,CADO,0.1\nprimary,CADO,0.2\nood,CADO,0.9\nprimary,Consensus,0.9\n")
            write(out / "revision" / "heldout_summary_statistics.csv",
                  "policy,metric,mean,ci_low,ci_high,n\nConsensus,utility,0.6572,0,1,30\n")
            (out / "revision" / "sensitivity_settings.json").write_text(json.dumps(
                [{"name": "default", "family": "default"}, {"name": "ood_limit_1.65", "family": "OOD gate"},
                 {"name": "ood_limit_2.75", "family": "OOD gate"}]), encoding="utf-8")
            write(out / "revision" / "sensitivity_paired_comparisons.csv",
                  "setting,dataset,metric,difference\ndefault,primary,utility,0.006735\n"
                  "ood_limit_1.65,primary,utility,0.004378\nood_limit_2.75,primary,utility,0.006978\n"
                  "ood_limit_1.65,ood,utility,0.0\nood_limit_2.75,ood,utility,0.003932\n")
            write(out / "revision" / "sensitivity_seed_metrics.csv",
                  "dataset,seed,policy,fallback_rate,setting\nood,0,CADO,0.96,a\nood,1,CADO,0.98,a\nood,0,CADO,1.0,b\n"
                  "ood,0,Consensus,0.5,a\nprimary,0,CADO,0.1,a\n")
            self.assertEqual(R.lookup("T3.primary.Consensus.utility", out), 0.6953)   # Consensus: primary summary
            self.assertEqual(R.lookup("T3.ood.Consensus.utility", out), 0.6572)       # Consensus: held-out summary
            self.assertEqual(R.lookup("T3.primary.CADO-NoEvidence.fallback_rate", out), 0.961)
            self.assertEqual(R.lookup("T5.OOD_gate.primary_utility.min", out), 0.004378)
            self.assertEqual(R.lookup("T5.OOD_gate.ood_utility.max", out), 0.003932)
            self.assertEqual(R.lookup("T5.OOD_gate.settings.n", out), 2.0)
            self.assertEqual(R.lookup("T5.default.primary_utility.max", out), 0.006735)
            self.assertAlmostEqual(R.lookup("S52.gate.gate_ood", out), 0.15)          # primary CADO episodes only
            self.assertEqual(R.lookup("S52.ood_fallback.ci_high", out), 0.9904)
            self.assertAlmostEqual(R.lookup("S54.ood_fallback.min", out), 0.97)       # mean per setting, then min
            self.assertEqual(R.lookup("S54.ood_fallback.max", out), 1.0)
            self.assertEqual(R.lookup("S55.rollback.CADO", out), 0.9804)


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
