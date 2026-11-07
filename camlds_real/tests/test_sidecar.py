"""Tests for the protocol 1.1 side files. Inputs only; no model output, no metric.

    python -m unittest discover -s camlds_real/tests -v
"""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import build_sidecar as bs  # noqa: E402


def run(name, labels, occ=None):
    """A toy run: one step per label tuple, in order."""
    return [{"run": name, "exec_index": i, "source_row": f"{name}{i}", "techniques_parent": list(l),
             "occurrence": (occ or [1] * len(labels))[i]} for i, l in enumerate(labels)]


class Definitions(unittest.TestCase):
    def test_points_skip_first_step_and_window_is_previous_w(self):
        p = bs.points(run("a", [("x",), ("y",), ("z",), ("q",)]), w=2)
        self.assertEqual([i for i, _, _ in p], [1, 2, 3])
        self.assertEqual(p[0][1], (("x",),))
        self.assertEqual(p[2][1], (("y",), ("z",)))      # only the last 2 steps
        self.assertEqual(p[2][2], ("q",))

    def test_labels_inside_a_step_are_order_free(self):
        a = bs.points(run("a", [("x",), ("k", "j")]))
        b = bs.points(run("b", [("x",), ("j", "k")]))
        self.assertEqual(a[0][1:], b[0][1:])

    def test_copy_needs_same_window_and_same_target(self):
        train = run("t", [("a",), ("b",), ("c",)])
        test = run("s", [("a",), ("b",), ("d",)])
        m = bs.mark([test], [train])
        self.assertTrue(m[0]["copy"])     # window (a) -> target b, also in training
        self.assertFalse(m[1]["copy"])    # window (a, b) -> d, training has -> c

    def test_same_last_steps_at_a_different_depth_is_not_a_copy(self):
        train = run("t", [("z",), ("a",), ("b",)])        # window (z, a) -> b
        test = run("s", [("a",), ("b",)])                 # window (a) -> b
        self.assertFalse(bs.mark([test], [train])[0]["copy"])

    def test_no_seen_runs_means_no_copies(self):
        self.assertFalse(any(m["copy"] for m in bs.mark([run("s", [("a",), ("a",)])], [])))

    def test_repeat_means_anywhere_in_the_window(self):
        test = run("s", [("a",), ("b",), ("a", "c")])
        last = bs.mark([test], [])[-1]["targets"]
        self.assertEqual({t["label"]: t["repeat"] for t in last}, {"a": True, "c": False})

    def test_repeat_ignores_steps_older_than_the_window(self):
        test = run("s", [("a",), ("b",), ("c",), ("a",)])
        self.assertFalse(bs.mark([test], [], w=2)[-1]["targets"][0]["repeat"])

    def test_collapse_keeps_first_occurrence_only(self):
        st = run("a", [("x",), ("y",), ("y",), ("z",)], occ=[1, 1, 2, 1])
        self.assertEqual([s["exec_index"] for s in bs.collapse_repeats(st)], [0, 1, 3])


class RealData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.steps = bs.sp.load(bs.REPO)
        cls.links, cls.n_shift = bs.link_rows(cls.steps)

    def test_every_step_linked_once(self):
        self.assertEqual(len(self.links), 904)
        self.assertEqual(len({(l["attackmate_path"], l["attackmate_index"]) for l in self.links}), 904)
        self.assertEqual(self.n_shift, 11)

    def test_shifts_are_the_authors_values(self):
        got = sorted({l["csv_start_shift_s"] for l in self.links})
        self.assertEqual(got, [-150.0, -82.0, -60.0, 0.0, 40.0])

    def test_execution_order_differs_in_four_s6_runs(self):
        runs = {l["run"] for l in self.links if l["execution_rank"] != l["exec_index"]}
        self.assertEqual(len(runs), 4)
        self.assertTrue(all(r.startswith("6_") for r in runs))

    def test_vocabulary_is_the_81_corpus_labels(self):
        v = json.load(open(os.path.join(bs.HERE, "out", "vocab.json"), encoding="utf-8"))["parent_techniques"]
        self.assertEqual(v, sorted({t for s in self.steps for t in s["techniques_parent"]}))
        self.assertEqual(len(v), 81)

    def test_test_points_never_include_a_first_step(self):
        firsts = {s["source_row"] for s in self.steps if s["exec_index"] == 0}
        self.assertFalse(firsts & {p["source_row"] for p in bs.point_rows(self.steps)})


if __name__ == "__main__":
    unittest.main()
