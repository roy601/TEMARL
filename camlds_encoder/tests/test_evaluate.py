"""Tests for the Stage 1 scoring script. Every test output here is synthetic: random numbers written
to a temporary folder. No real test output is read or scored.

    python -m unittest discover -s camlds_encoder/tests -v
"""
import itertools
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import data  # noqa: E402
import evaluate_test as E  # noqa: E402
import run as R  # noqa: E402
from port import Mx, SPEC  # noqa: E402


class Statistics(unittest.TestCase):
    def test_holm_by_hand(self):
        self.assertEqual(E.holm([0.01, 0.04]), [0.02, 0.04])
        self.assertEqual(E.holm([0.04, 0.01]), [0.04, 0.02])
        self.assertEqual(E.holm([0.03, 0.04]), [0.06, 0.06])           # stays non-decreasing
        self.assertEqual(E.holm([0.8, 0.9]), [1.0, 1.0])

    def test_wilcoxon_equals_full_enumeration(self):
        d = np.array([0.5, -1.1, 2.3, 3.7, 4.9, -0.2])                 # no ties, no zeros
        ranks = np.argsort(np.argsort(np.abs(d))) + 1
        observed = ranks[d > 0].sum()
        full = ranks.sum()
        tail = min(observed, full - observed)
        all_sums = [sum(r for r, s in zip(ranks, signs) if s) for signs in itertools.product([0, 1], repeat=6)]
        want = 2 * sum(x <= tail for x in all_sums) / 2 ** 6
        self.assertAlmostEqual(E.wilcoxon_p(d), want, places=10)

    def test_wilcoxon_needs_two_nonzero_differences(self):
        self.assertIsNone(E.wilcoxon_p([0.0, 0.0, 0.1]))

    def test_bootstrap_is_fixed_and_uses_the_protocol_settings(self):
        d = np.arange(29, dtype=float) / 100 - 0.1
        g = np.random.default_rng(20261103)
        means = d[g.integers(0, 29, (10000, 29))].mean(axis=1)
        self.assertEqual(E.bootstrap_ci(d), (float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))))

    def test_bootstrap_of_a_constant_is_that_constant(self):
        lo, hi = E.bootstrap_ci([0.02] * 29)
        self.assertAlmostEqual(lo, 0.02)
        self.assertAlmostEqual(hi, 0.02)

    def _c(self, mean, lo, hi, p, per):
        return {"mean": mean, "ci": [lo, hi], "p_holm": p, "per_scenario": per}

    def test_verdict_needs_both_the_interval_and_the_p_value(self):
        self.assertEqual(E.verdict(self._c(0.1, 0.02, 0.2, 0.2, {"1": 0.1}), "A", "B"), "no difference shown")
        self.assertEqual(E.verdict(self._c(0.1, -0.02, 0.2, 0.01, {"1": 0.1}), "A", "B"), "no difference shown")
        self.assertIn("A outperforms B", E.verdict(self._c(0.1, 0.02, 0.2, 0.01, {"1": 0.1}), "A", "B"))

    def test_verdict_can_go_against_the_transformer_and_states_the_scenarios(self):
        v = E.verdict(self._c(-0.1, -0.2, -0.02, 0.01, {"1": -0.2, "3": 0.05}), "A", "B")
        self.assertIn("B outperforms A", v)
        self.assertIn("does NOT hold", v)

    def test_contrast_is_a_minus_b_per_fold(self):
        a = {"1_x": 0.9, "1_y": 0.8, "3_z": 0.7, "6_w": 0.6}
        b = {"1_x": 0.8, "1_y": 0.9, "3_z": 0.5, "6_w": 0.6}
        c = E.contrast(a, b)
        self.assertAlmostEqual(c["mean"], np.mean([0.1, -0.1, 0.2, 0.0]))
        self.assertEqual(c["folds_a_better"], 2)
        self.assertAlmostEqual(c["per_scenario"]["1"], 0.0)
        self.assertAlmostEqual(c["per_scenario"]["3"], 0.2)


class Scoring(unittest.TestCase):
    def setUp(self):
        # 3 points, 3 labels; label 0 and 1 are in the window, label 2 is not. Threshold 0.5.
        self.logits = np.array([[5., -5., 5.], [5., 5., -5.], [-5., -5., 5.]])
        self.tr = {"y": np.array([[1., 0., 1.], [1., 0., 0.], [0., 1., 0.]]),
                   "copy": np.array([False, False, True]),
                   "in_window": np.array([[True, True, False]] * 3)}

    def test_points_by_hand(self):
        c = E.score_cell(self.logits, 0.5, self.tr)
        # all: predicted {0,2},{0,1},{2}; true {0,2},{0},{1} -> TP 3, FP 2, FN 1
        self.assertAlmostEqual(c["all"]["micro_f1"], 2 * 3 / (2 * 3 + 2 + 1))
        self.assertAlmostEqual(c["novel"]["micro_f1"], 2 * 3 / (2 * 3 + 1 + 0))       # first two points
        self.assertEqual(c["copy"]["micro_f1"], 0.0)                                  # third point
        self.assertAlmostEqual(c["all"]["exact_set_accuracy"], 1 / 3)

    def test_empty_subset_is_absent_not_zero(self):
        tr = dict(self.tr, copy=np.array([False, False, False]))
        self.assertIsNone(E.score_cell(self.logits, 0.5, tr)["copy"])

    def test_repeat_and_new_labels_by_hand(self):
        c = E.score_cell(self.logits, 0.5, self.tr)["labels"]
        # labels 0,1 (repeat): TP 2, FP 1, FN 1. label 2 (new): TP 1, FP 1, FN 0
        self.assertAlmostEqual(c["repeat"], 2 * 2 / (2 * 2 + 1 + 1))
        self.assertAlmostEqual(c["new"], 2 * 1 / (2 * 1 + 1 + 0))

    def test_label_group_with_nothing_in_it_is_absent(self):
        logits = np.array([[-5., -5., 5.]])
        tr = {"y": np.array([[0., 0., 1.]]), "copy": np.array([False]), "in_window": np.array([[True, True, False]])}
        self.assertIsNone(E.score_cell(logits, 0.5, tr)["labels"]["repeat"])

    def test_selection_score_by_hand(self):
        def cell(tp, fp, fn):
            return {"counts": {"all": [tp, fp, fn], "novel": None}}
        res = {"main": {
            "1_a": {"family": E.FAMILY, "arms": {"allpos": [cell(2, 0, 0)]}},
            "1_b": {"family": E.FAMILY, "arms": {"allpos": [cell(0, 2, 0)]}},     # pooled S1: TP 2, FP 2
            "3_c": {"family": E.FAMILY, "arms": {"allpos": [cell(1, 0, 1)]}},
            "S2": {"family": E.SCENARIO_FAMILY, "arms": {"allpos": [cell(1, 1, 0)]}}}}
        s1 = 2 * 2 / (2 * 2 + 2)
        s3 = 2 * 1 / (2 * 1 + 1)
        held = 2 * 1 / (2 * 1 + 1)
        self.assertAlmostEqual(E.selection_score(res, "main", "allpos", "all"), (s1 + s3 + held) / 3)

    def test_metrics_are_the_frozen_functions(self):
        c = E.score_cell(self.logits, 0.5, self.tr)["all"]
        prob = Mx._sigmoid(self.logits)
        self.assertEqual(c["micro_f1"], Mx.threshold_metrics(prob, self.tr["y"], 0.5)["micro_f1"])
        self.assertEqual(c["recall_at_3"], Mx.ranking_metrics(prob, self.tr["y"])["recall_at_3"])


def build_synthetic(out, conditions=("main",)):
    """Random logits for the 2 smoke folds, in the real folder layout. Nothing here is a result."""
    g = np.random.default_rng(0)
    seed = SPEC.MAIN_SEEDS[0]
    for cond in conditions:
        for f in R.pick_folds(cond, True):
            d = data.fold_data(f)
            for arm in E.ENCODERS + ((E.BASELINE,) if cond == "main" else ()):
                c = E.cell_dir(out, cond, arm, f["fold"], seed)
                os.makedirs(c)
                lo_va = g.normal(-3, 2, (len(d["val"][0]), 81)).astype(np.float32)
                lo_te = g.normal(-3, 2, (len(d["test_inputs"][0]), 81)).astype(np.float32)
                np.save(os.path.join(c, "val_logits.npy"), lo_va)
                np.save(os.path.join(c, "test_logits.npy"), lo_te)
                val = {"file": "val_logits.npy", "sha256": R.sha_file(os.path.join(c, "val_logits.npy")), "points": len(lo_va)}
                res = {"threshold": 0.3, "smoke": True,
                       "validation": Mx.evaluate(lo_va.astype(np.float64), d["val"][2], d["val_owners"], 0.3),
                       "sealed_test": {"file": "test_logits.npy", "sha256": R.sha_file(os.path.join(c, "test_logits.npy")),
                                       "points": len(lo_te), "source_rows": d["test_source_rows"], "owners": d["test_owners"]}}
                if arm == E.BASELINE:
                    R.write_json(os.path.join(c, "val_outputs.json"), {"val": val, "val_source_rows": d["val_source_rows"]})
                else:
                    res.update({"val": val, "val_source_rows": d["val_source_rows"]})
                R.write_json(os.path.join(c, "result.json"), res)


class Pipeline(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.out = self.tmp.name
        build_synthetic(self.out)
        self.addCleanup(self.tmp.cleanup)
        self.seed = SPEC.MAIN_SEEDS[0]

    def _spy(self):
        real, seen = np.load, []

        def spy(path, *a, **k):
            seen.append(str(path))
            return real(path, *a, **k)
        return mock.patch.object(E.np, "load", spy), seen

    def test_dry_run_never_reads_a_test_output(self):
        p, seen = self._spy()
        with p:
            res, worst = E.score_all("val", self.out, True, ("main",))
        self.assertTrue(seen)
        self.assertFalse([s for s in seen if "test_logits" in s])
        self.assertLessEqual(worst, 1e-12)
        self.assertEqual(sorted(res["main"]), sorted(f["fold"] for f in R.pick_folds("main", True)))

    def test_test_mode_reads_only_test_outputs(self):
        p, seen = self._spy()
        with p:
            E.score_all("test", self.out, True, ("main",))
        self.assertTrue(seen)
        self.assertFalse([s for s in seen if "val_logits" in s])

    def _cell(self, arm="allpos", name="1_autostart_localaccount"):
        return E.cell_dir(self.out, "main", arm, name, self.seed)

    def test_a_changed_file_stops_the_run(self):
        path = os.path.join(self._cell(), "test_logits.npy")
        a = np.load(path)
        a[0, 0] += 1
        np.save(path, a)
        with self.assertRaisesRegex(SystemExit, "fingerprint"):
            E.score_all("test", self.out, True, ("main",))

    def test_a_missing_training_stops_the_run(self):
        os.remove(os.path.join(self._cell("lstm_allpos"), "test_logits.npy"))
        with self.assertRaisesRegex(SystemExit, "missing"):
            E.score_all("test", self.out, True, ("main",))

    def test_nothing_is_read_if_any_output_is_missing(self):
        with tempfile.TemporaryDirectory() as t:
            build_synthetic(t, ("main", "collapse_repeats"))
            cell = E.cell_dir(t, "collapse_repeats", "lstm_allpos", "S2", self.seed)
            os.remove(os.path.join(cell, "test_logits.npy"))
            p, seen = self._spy()
            with p, self.assertRaisesRegex(SystemExit, "missing"):
                E.score_all("test", t, True, ("main", "collapse_repeats"))
            self.assertEqual(seen, [])

    def test_every_metric_is_reported_on_all_novel_and_copy(self):
        res, _ = E.score_all("val", self.out, True, ("main",))
        text = E.report(res, E.summarise(res), "t")
        for m in E.METRICS:
            for sub in E.SUBSETS:
                self.assertIn(f"{E.METRIC_NAMES[m]}, {sub}", text)

    def test_wrong_points_stop_the_run(self):
        path = os.path.join(self._cell(), "result.json")
        r = R.read_json(path)
        r["sealed_test"]["source_rows"] = r["sealed_test"]["source_rows"][::-1]
        R.write_json(path, r)
        with self.assertRaisesRegex(SystemExit, "not the fold's points"):
            E.score_all("test", self.out, True, ("main",))

    def test_a_threshold_off_the_grid_stops_the_run(self):
        path = os.path.join(self._cell(), "result.json")
        r = R.read_json(path)
        r["threshold"] = 0.65
        R.write_json(path, r)
        with self.assertRaisesRegex(SystemExit, "frozen grid"):
            E.score_all("test", self.out, True, ("main",))

    def test_dry_run_stops_if_it_cannot_reproduce_the_record(self):
        path = os.path.join(self._cell(), "result.json")
        r = R.read_json(path)
        r["validation"]["micro_f1"] += 0.01
        R.write_json(path, r)
        with self.assertRaisesRegex(SystemExit, "differs from the record"):
            E.score_all("val", self.out, True, ("main",))

    def test_summary_and_report_run_end_to_end(self):
        res, _ = E.score_all("val", self.out, True, ("main",))
        S = E.summarise(res)
        text = E.report(res, S, "t")
        self.assertIn("Transformer", text)
        self.assertIn("Does the improvement hold", text)
        self.assertIn("Per fold", E.per_fold_report(res))
        json.dumps(S)


class Gate(unittest.TestCase):
    def test_refuses_if_the_protocol_check_fails(self):
        with tempfile.TemporaryDirectory() as t, mock.patch.object(E.subprocess, "run") as run:
            run.return_value = mock.Mock(returncode=1, stdout="PROTOCOL 1.2 CHECK FAILED")
            with self.assertRaisesRegex(SystemExit, "stays closed"):
                E.open_gate(t)

    def test_passes_only_on_the_exact_pass_line(self):
        with tempfile.TemporaryDirectory() as t, mock.patch.object(E.subprocess, "run") as run:
            run.return_value = mock.Mock(returncode=0, stdout="something else")
            with self.assertRaises(SystemExit):
                E.open_gate(t)
            run.return_value = mock.Mock(returncode=0, stdout="...\nPROTOCOL 1.2 CHECK: PASS\n")
            E.open_gate(t)

    def test_opens_only_once(self):
        with tempfile.TemporaryDirectory() as t:
            open(os.path.join(t, E.RESULTS + ".json"), "w").close()
            with self.assertRaisesRegex(SystemExit, "once"):
                E.open_gate(t)


if __name__ == "__main__":
    unittest.main()
