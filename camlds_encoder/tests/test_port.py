"""Tests for the B2 port. Inputs and validation only; no test metric is computed.

    python -m unittest discover -s camlds_encoder/tests -v
"""
import json
import os
import sys
import unittest

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import data  # noqa: E402
import port  # noqa: E402


def _with_nt(n, fn):
    """Build something with the frozen modules set to n labels, then restore 81."""
    for m in (port.Enc, port.T, port.D):
        m.NT = n
    try:
        return fn()
    finally:
        for m in (port.Enc, port.T, port.D):
            m.NT = port.NT


class Port(unittest.TestCase):
    def test_label_count_is_the_only_change(self):
        self.assertEqual((port.OLD_NT, port.NT), (84, 81))
        old = _with_nt(84, lambda: port.Enc.parameter_report("Transformer", 16))
        new = port.Enc.parameter_report("Transformer", 16)
        self.assertEqual(old["trunk_trainable"], new["trunk_trainable"])          # trunk untouched
        # 3 fewer labels: embedding loses 3 x 64 weights, head loses 3 x (64 + 1)
        self.assertEqual(old["total_trainable"] - new["total_trainable"], 3 * 64 + 3 * 65)

    def test_model_reads_and_writes_81_labels(self):
        m = port.Enc.build_model("Transformer", 16)
        self.assertEqual(m.encoder.embed.lin.in_features, 81)
        self.assertEqual(m.head.out_features, 81)
        x, mk = torch.zeros(2, 16, 81), torch.zeros(2, 16)
        x[:, -1, 0], mk[:, -1] = 1, 1
        self.assertEqual(tuple(m(x, mk).shape), (2, 81))
        self.assertEqual(tuple(m.history(x, mk).shape), (2, 64))                  # h for MAPPO
        with self.assertRaises(ValueError):
            m(torch.zeros(2, 16, 84), mk)

    def test_labels_are_the_pinned_list(self):
        v = json.load(open(port.VOCAB_PATH, encoding="utf-8"))["parent_techniques"]
        self.assertEqual(port.LABELS, v)
        self.assertEqual(port.LABELS, sorted(port.LABELS))


class Folds(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f = {c: data.folds(c) for c in data.CONDITIONS}

    def test_32_folds_and_the_exclusion(self):
        for fs in self.f.values():
            names = [f["fold"] for f in fs]
            self.assertEqual(len(names), 32)
            self.assertEqual(sum(f["family"] == "scenario_held_out" for f in fs), 3)
            self.assertFalse({"2_cron", "2_rootkit"} & set(names))

    def test_runs_never_overlap(self):
        for fs in self.f.values():
            for f in fs:
                tr, va, te = (set(f[k]) for k in ("train_runs", "val_runs", "test_runs"))
                self.assertFalse(tr & va or tr & te or va & te, f["fold"])
                self.assertTrue(va, f"{f['fold']} has no validation run")

    def test_test_targets_are_not_returned(self):
        d = data.fold_data(self.f["main"][0])
        self.assertEqual(len(d["test_inputs"]), 2)
        self.assertNotIn("test", d)
        self.assertFalse(any("target" in k or k == "test_y" for k in d))


class Windows(unittest.TestCase):
    def test_windows_match_the_corpus(self):
        steps = data.steps_for("main")
        run = "5"
        X, M, Y, owners, rows = data.windows(steps, [run])
        seq = sorted((s for s in steps if s["run"] == run), key=lambda s: s["exec_index"])
        self.assertEqual(len(X), len(seq) - 1)
        self.assertEqual(rows, [s["source_row"] for s in seq[1:]])
        self.assertEqual(M[0].tolist(), [0.0] * 15 + [1.0])                      # left-padded
        for i, s in enumerate(seq[1:]):
            self.assertEqual({port.LABELS[j] for j in np.flatnonzero(Y[i])}, set(s["techniques_parent"]))
        last_hist = {port.LABELS[j] for j in np.flatnonzero(X[-1, -1])}
        self.assertEqual(last_hist, set(seq[-2]["techniques_parent"]))           # most recent at the end
        self.assertTrue(data.label_matrix_ok(Y))

    def test_window_is_capped_at_16(self):
        steps = data.steps_for("main")
        X, M, _, _, _ = data.windows(steps, ["1_autostart_localaccount"])
        self.assertEqual(X.shape[1], 16)
        self.assertEqual(int(M.sum(1).max()), 16)


class Training(unittest.TestCase):
    def test_tiny_training_gives_finite_81_label_logits(self):
        f = data.folds("main")[-1]                                                 # S6, scenario held out
        d = data.fold_data(f)
        res, model = port.T.train_one("Transformer", 16, 0, d["train"], d["val"], 8,
                                      device=torch.device("cpu"), patience_checks=None)
        port.T.load_best(model, res)
        lo = port.T.predict(model, *d["test_inputs"], torch.device("cpu"))
        self.assertEqual(lo.shape, (len(d["test_source_rows"]), 81))
        self.assertTrue(np.isfinite(lo).all())


if __name__ == "__main__":
    unittest.main()
