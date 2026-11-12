"""Tests for casinolimit_encoder (port, split, windows, lookup).

    python -m unittest discover -s casinolimit_encoder/tests
"""
import os
import sys
import unittest

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import cl_data as CD  # noqa: E402
import cl_port as CP  # noqa: E402
import cl_split as S  # noqa: E402
import lookup as LK  # noqa: E402


class Port(unittest.TestCase):
    def test_every_model_and_window_has_66_labels(self):
        self.assertEqual(CP.NT, 66)
        for m in (CP.Enc, CP.T, CP.D, CP.V):
            self.assertEqual(m.NT, 66)
        for v in ("allpos", "gru_allpos", "lstm_allpos", "baseline"):
            model = CP.V.build_variant(v, CD.W)
            x = torch.zeros(2, CD.W, 66)
            x[:, -1, 3] = 1
            m = torch.zeros(2, CD.W)
            m[:, -1] = 1
            self.assertEqual(tuple(CP.T.predict(model, x.numpy(), m.numpy(), torch.device("cpu")).shape), (2, 66), v)

    def test_frozen_encoder_code_is_still_checked(self):
        self.assertTrue(hasattr(CP.P, "verify"))
        CP.P.verify()                                    # raises if a frozen module changed


class Split(unittest.TestCase):
    def test_folds_are_fixed_balanced_and_disjoint(self):
        folds = S.folds(CP.STEPS)
        runs = sorted({s["run"] for s in CP.STEPS})
        self.assertEqual(sorted(r for f in folds for r in f["test_runs"]), runs)
        for i, f in enumerate(folds):
            self.assertEqual(f["val_runs"], folds[(i + 1) % S.K]["test_runs"])
            self.assertFalse(set(f["train_runs"]) & (set(f["test_runs"]) | set(f["val_runs"])))
            self.assertEqual(len(f["train_runs"]) + len(f["val_runs"]) + len(f["test_runs"]), len(runs))
        self.assertLessEqual(max(len(f["test_runs"]) for f in folds) - min(len(f["test_runs"]) for f in folds), 1)
        self.assertEqual(S.folds(CP.STEPS), folds)       # no randomness

    def test_snake_order(self):
        steps = [{"run": r, "exec_index": i} for r, n in zip("abcdefg", (7, 6, 5, 4, 3, 2, 1)) for i in range(n)]
        self.assertEqual(S.assign(steps, 3), {"a": "F1", "b": "F2", "c": "F3", "d": "F3", "e": "F2", "f": "F1", "g": "F1"})

    def test_both_conditions_use_the_same_runs_per_fold(self):
        for a, b in zip(CD.folds("main"), CD.folds("collapse_repeats")):
            self.assertEqual({k: a[k] for k in ("test_runs", "val_runs", "train_runs")},
                             {k: b[k] for k in ("test_runs", "val_runs", "train_runs")})


class Windows(unittest.TestCase):
    def test_windows_match_the_corpus(self):
        f = CD.folds("main")[0]
        d = CD.fold_data(f)
        seqs = CD.label_seqs(CP.STEPS, f["val_runs"])
        X, M, Y = d["val"]
        self.assertEqual(len(Y), sum(len(q) - 1 for q in seqs.values()))
        q = next(iter(seqs.values()))
        self.assertEqual(sorted(CP.LABELS[i] for i in np.flatnonzero(Y[0])), list(q[1]))
        self.assertEqual(sorted(CP.LABELS[i] for i in np.flatnonzero(X[0, -1])), list(q[0]))
        self.assertEqual(M[0].tolist(), [0.0] * 15 + [1.0])
        self.assertEqual(set(d), {"train", "val", "val_owners", "val_source_rows",
                                  "test_inputs", "test_owners", "test_source_rows"})   # no test targets
        self.assertEqual(len(d["test_inputs"]), 2)                                     # X and mask only

    def test_copy_and_repeat_marks(self):
        seen = {"s": [("A",), ("B",), ("A",)]}
        test = {"t": [("A",), ("B",), ("C",), ("A",)]}
        m = CD.mark(test, seen, w=2)
        self.assertEqual([p["copy"] for p in m], [True, False, False])
        self.assertEqual([[t["repeat"] for t in p["targets"]] for p in m], [[False], [False], [False]])
        m = CD.mark({"t": [("A",), ("B",), ("A",)]}, {}, w=2)
        self.assertEqual(m[1]["targets"], [{"label": "A", "repeat": True}])


class Lookup(unittest.TestCase):
    def test_longest_match_previous_step_and_fallback(self):
        train = {"r1": [("A",), ("B",), ("C",)], "r2": [("X",), ("B",), ("D",)], "r3": [("X",), ("B",), ("D",)]}
        tab = LK.table(train, w=4)
        self.assertEqual(LK.predict(tab, (("A",), ("B",))), ("C",))          # longest context wins
        self.assertEqual(LK.predict(tab, (("A",), ("B",)), longest=False), ("D",))   # B -> D twice
        self.assertEqual(LK.predict(tab, (("Q",),)), ("B",))                 # unseen: most frequent target
        ids = {"A": 0, "B": 1, "C": 2, "D": 3, "X": 4}
        p = LK.predictions(tab, {"t": [("A",), ("B",), ("C",)]}, ids, w=4)
        self.assertEqual(p.tolist(), [[0, 1, 0, 0, 0], [0, 0, 1, 0, 0]])


if __name__ == "__main__":
    unittest.main()
