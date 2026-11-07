"""Tests for the validation-only encoder variants. No test metric is computed.

    python -m unittest discover -s camlds_encoder/tests -v
"""
import os
import sys
import unittest

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import data  # noqa: E402
import port  # noqa: E402
import variants as V  # noqa: E402

CPU = torch.device("cpu")


def toy(B=3, W=16, real=(1, 5, 16), seed=0):
    g = np.random.default_rng(seed)
    x = np.zeros((B, W, 81), np.float32)
    m = np.zeros((B, W), np.float32)
    for b, k in enumerate(real):
        m[b, W - k:] = 1
        for t in range(W - k, W):
            x[b, t, g.choice(81, size=g.integers(1, 3), replace=False)] = 1
    y = np.zeros((B, 81), np.float32)
    y[np.arange(B), g.integers(0, 81, B)] = 1
    return torch.from_numpy(x), torch.from_numpy(m), torch.from_numpy(y)


class Harness(unittest.TestCase):
    def test_baseline_reproduces_the_frozen_train_one_exactly(self):
        f = data.folds("main")[-1]
        d = data.fold_data(f)
        torch.set_num_threads(1)
        a, ma = port.T.train_one("Transformer", 16, 3, d["train"], d["val"], 130, device=CPU,
                                 patience_checks=None)
        b, mb = V.train_variant("baseline", 16, 3, d["train"], d["val"], 130, device=CPU)
        self.assertEqual([p["validation_bce"] for p in a.curve], [p["validation_bce"] for p in b.curve])
        self.assertEqual(a.best_update, b.best_update)
        for k, t in ma.state_dict().items():
            self.assertTrue(torch.equal(t, mb.state_dict()[k]), k)

    def test_same_seed_same_initial_weights_and_size(self):
        states = {}
        for v in V.VARIANTS:
            torch.manual_seed(7)
            states[v] = V.build_variant(v, 16).state_dict()
        for v in ("causal", "allpos"):
            self.assertEqual(states[v].keys(), states["baseline"].keys())
            for k in states[v]:
                self.assertTrue(torch.equal(states[v][k], states["baseline"][k]), (v, k))


class Causal(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(0)
        self.m = V.build_variant("allpos", 16).eval()

    def test_no_nan_with_heavy_padding_in_train_and_eval(self):
        x, mk, y = toy()
        for mode in (True, False):
            self.m.train(mode)
            self.assertTrue(torch.isfinite(self.m.states(x, mk)).all())
            self.assertTrue(torch.isfinite(self.m.loss(x, mk, y)))

    def test_a_step_never_sees_later_steps(self):
        x, mk, _ = toy(B=1, real=(16,))
        x2 = x.clone()
        x2[0, 10] = 0
        x2[0, 10, 5] = 1                                          # change step 10 only
        with torch.no_grad():
            a, b = self.m.states(x, mk), self.m.states(x2, mk)
        self.assertTrue(torch.allclose(a[0, :10], b[0, :10], atol=1e-6))   # earlier: unchanged
        self.assertFalse(torch.allclose(a[0, 10:], b[0, 10:]))             # later: changed

    def test_last_position_sees_the_whole_window(self):
        x, mk, _ = toy(B=1, real=(16,))
        x2 = x.clone()
        x2[0, 0] = 0
        x2[0, 0, 7] = 1                                           # change the oldest step
        with torch.no_grad():
            self.assertFalse(torch.allclose(self.m(x, mk), self.m(x2, mk)))

    def test_allpos_loss_uses_next_steps_and_real_positions_only(self):
        x, mk, y = toy(B=2, real=(3, 16))
        with torch.no_grad():
            logits = self.m.head(self.m.states(x, mk))
            want, n = 0.0, 0
            for b in range(2):
                for k in range(16):
                    if mk[b, k] < 0.5:
                        continue
                    tgt = y[b] if k == 15 else x[b, k + 1]
                    want += torch.nn.functional.binary_cross_entropy_with_logits(logits[b, k], tgt).item()
                    n += 1
            self.assertAlmostEqual(self.m.loss(x, mk, y).item(), want / n, places=5)

    def test_causal_control_loss_is_last_position_only(self):
        torch.manual_seed(0)
        c = V.build_variant("causal", 16).eval()
        x, mk, y = toy()
        with torch.no_grad():
            want = torch.nn.functional.binary_cross_entropy_with_logits(c(x, mk), y).item()
            self.assertAlmostEqual(c.loss(x, mk, y).item(), want, places=6)


if __name__ == "__main__":
    unittest.main()
