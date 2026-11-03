"""Tests for the Idea 01 Kuwano runner. They use the corpus inputs and validation-side logic
only; no test metric is computed anywhere.

    python -m unittest discover -s idea01_kuwano/tests -v
"""
import collections
import os
import sys
import unittest
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import run_kuwano as rk  # noqa: E402


class Fixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.steps = rk.sp.load(rk.REPO)
        cls.runs = rk.by_run(cls.steps)
        cls.da = rk.kw.load(os.path.join(rk.REPO, "kuwano_repro", "data", "derived"), "11.0")


class Points(Fixture):
    def test_first_step_excluded_and_no_targets_on_test_points(self):
        r = sorted(self.runs)[0]
        tp = rk.points(self.runs, [r], 16, with_target=False)
        self.assertEqual(len(tp), len(self.runs[r]) - 1)
        self.assertTrue(all("target" not in p for p in tp))
        self.assertEqual(tp[0]["pos"], 1)

    def test_window_is_union_of_previous_w_steps(self):
        r = max(self.runs, key=lambda x: len(self.runs[x]))
        ss = self.runs[r]
        p = rk.points(self.runs, [r], 16, with_target=True)[29]          # pos 30
        want = frozenset(t for s in ss[14:30] for t in s["techniques_parent"])
        self.assertEqual(p["observed"], want)
        self.assertEqual(p["target"], frozenset(ss[30]["techniques_parent"]))
        full = rk.points(self.runs, [r], None, with_target=True)[29]
        self.assertEqual(full["observed"], frozenset(t for s in ss[:30] for t in s["techniques_parent"]))

    def test_runs_are_in_time_order(self):
        for ss in self.runs.values():
            self.assertEqual([s["start"] for s in ss], sorted(s["start"] for s in ss))


class Scoring(Fixture):
    def test_ka_scores_are_the_validated_algorithm_restricted_to_our_labels(self):
        r = sorted(self.runs)[0]
        for p in rk.points(self.runs, [r], 16, with_target=False)[:5]:
            s, _ = rk.kw.recommend_limit(p["observed"], self.da, k=60, tiebreak="name")
            want = {t: s[t] for t in rk.LABELS}
            sup, _ = rk.kw.recommend(p["observed"], self.da)          # no similarity 1 here
            self.assertEqual(want, {t: (0, sup[t]) for t in rk.LABELS})

    def test_decide_and_ranking(self):
        score = {t: (0, F(0)) for t in rk.LABELS}
        a, b, c = rk.LABELS[:3]
        score[a], score[b], score[c] = (0, F(1, 5)), (1, F(0)), (0, F(17, 100))
        self.assertEqual(set(rk.decide(score, F(17, 100))), {a, b, c})   # >= and n > 0
        self.assertEqual(set(rk.decide(score, F(18, 100))), {a, b})
        self.assertEqual(rk.ranking(score)[:3], [b, a, c])               # n first, then rate

    def test_select_threshold_ties_take_smallest(self):
        a = rk.LABELS[0]
        vp = [{"target": frozenset({a})}]
        score = {t: (0, F(0)) for t in rk.LABELS}
        score[a] = (0, F(1))
        thr, best, curve = rk.select_threshold((F(1, 2), F(1, 4), F(1)), vp, lambda p: score)
        self.assertEqual(thr, F(1, 4))     # all three give micro-F1 1.0; the smallest wins
        self.assertEqual(best, 1.0)
        self.assertEqual([c[0] for c in curve], ["1/4", "1/2", "1"])


class Folds(Fixture):
    def test_kb_reference_never_contains_validation_or_test_runs(self):
        folds = [f for f in rk.sp.folds(self.steps, rk.sp.FAMILY_PRIMARY)
                 if f["fold"] not in rk.spec.EXCLUDED_VARIANT_FOLDS]
        folds += rk.sp.folds(self.steps, rk.sp.FAMILY_SECONDARY)
        self.assertEqual(len(folds), 32)
        for f in folds:
            tr, va = rk.sp.split_train_val(f)
            ref = {s["run"] for s in tr}
            self.assertFalse(ref & {s["run"] for s in va})
            self.assertFalse(ref & {s["run"] for s in f["test"]})
            self.assertTrue(va)            # every used fold has validation

    def test_point_counts_match_protocol(self):
        var = [f for f in rk.sp.folds(self.steps, rk.sp.FAMILY_PRIMARY)
               if f["fold"] not in rk.spec.EXCLUDED_VARIANT_FOLDS]
        n = sum(len(rk.points(self.runs, sorted({s["run"] for s in f["test"]}), 16, False)) for f in var)
        self.assertEqual(n, rk.spec.EXPECTED["variant_points"])


if __name__ == "__main__":
    unittest.main()
