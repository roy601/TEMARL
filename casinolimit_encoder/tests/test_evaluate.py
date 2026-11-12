"""Tests for casinolimit_encoder/evaluate.py (statistics, truth flags, gates).

    python -m unittest discover -s casinolimit_encoder/tests
"""
import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import cl_data as CD  # noqa: E402
import evaluate as E  # noqa: E402
import lookup as LK  # noqa: E402


class Statistics(unittest.TestCase):
    def test_holm(self):
        self.assertEqual([round(x, 6) for x in E.holm([0.01, 0.04, 0.03])], [0.03, 0.06, 0.06])
        self.assertEqual(E.holm([0.5, 0.9]), [1.0, 1.0])          # 2 x 0.5 = 1.0; never below an earlier one

    def test_bootstrap_is_fixed_and_contains_the_mean(self):
        d = np.linspace(-0.1, 0.3, 40)
        self.assertEqual(E.bootstrap_ci(d), E.bootstrap_ci(d))
        lo, hi = E.bootstrap_ci(d)
        self.assertLess(lo, d.mean())
        self.assertGreater(hi, d.mean())

    def test_verdict_needs_both_ci_and_holm(self):
        c = {"a": "allpos", "b": "simple", "mean": 0.05, "ci": [0.01, 0.09], "p_holm": 0.01}
        self.assertEqual(E.verdict(c), "Transformer outperforms Best simple baseline")
        self.assertEqual(E.verdict({**c, "p_holm": 0.2}), "no difference shown")
        self.assertEqual(E.verdict({**c, "ci": [-0.01, 0.09]}), "no difference shown")
        self.assertEqual(E.verdict({**c, "mean": -0.05, "ci": [-0.09, -0.01]}),
                         "Best simple baseline outperforms Transformer")

    def test_contrast_pairs_by_attacker(self):
        a = {f"r{i}": 0.5 + 0.01 * i for i in range(30)}
        b = {f"r{i}": 0.5 for i in range(30)}
        b["only_b"] = 0.9
        c = E.contrast(a, b)
        self.assertEqual(c["n_attackers"], 30)
        self.assertEqual((c["attackers_a_better"], c["attackers_b_better"]), (29, 0))
        self.assertLess(c["p"], 0.001)

    def test_f1_and_counts(self):
        pred = np.array([[1, 0, 1], [0, 0, 0]], bool)
        Y = np.array([[1, 1, 0], [0, 1, 0]], np.float32)
        tp, fp, fn = E.counts(pred, Y)
        self.assertEqual((tp.tolist(), fp.tolist(), fn.tolist()), ([1, 0], [1, 0], [1, 1]))
        self.assertAlmostEqual(E.f1(1, 1, 2), 0.4)
        self.assertEqual(E.f1(0, 3, 3), 0.0)


class Truth(unittest.TestCase):
    def test_validation_truth_lines_up_with_the_corpus(self):
        f = CD.folds("main")[0]
        tr = E.truth(f, "val")
        _, _, Y, owners, rows = CD.windows(f["_steps"], f["val_runs"])
        self.assertTrue(np.array_equal(tr["Y"], Y))
        self.assertEqual(tr["rows"], rows)
        sub = tr["subset"]
        self.assertTrue(np.array_equal(sub["novel"], ~sub["copy"]))
        self.assertTrue(sub["reviewed"].any() and not sub["reviewed"].all())
        by_row = {s["source_row"]: s for s in f["_steps"]}
        for i in np.flatnonzero(sub["reviewed"])[:50]:
            s = by_row[rows[i]]
            self.assertNotIn("auto-triggers", s["labelled_by"])
            self.assertEqual(s["doubt"], [])
        self.assertLessEqual(tr["unseen_label_slots"], tr["label_slots"])


class Gates(unittest.TestCase):
    def test_models_and_families_are_the_protocol_ones(self):
        self.assertEqual(E.FAMILY_1, [("allpos", "simple"), ("gru_allpos", "simple"), ("lstm_allpos", "simple")])
        self.assertEqual(E.FAMILY_2, [("allpos", "gru_allpos"), ("allpos", "lstm_allpos")])
        self.assertEqual(LK.RULES, ("longest", "previous", "repeat_last"))
        self.assertEqual((E.ALPHA, E.BOOTSTRAP_RESAMPLES, E.BOOTSTRAP_SEED), (0.05, 10_000, 20261103))

    def test_repeat_last_rule(self):
        self.assertEqual(LK.predict_rule("repeat_last", {}, (("A",), ("B", "C"))), ("B", "C"))


if __name__ == "__main__":
    unittest.main()
