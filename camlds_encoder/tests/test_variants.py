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


class Repeat(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(0)
        self.m = V.build_variant("repeat", 16).eval()

    def test_starts_from_the_allpos_weights_plus_one_layer(self):
        torch.manual_seed(7)
        a = V.build_variant("allpos", 16).state_dict()
        torch.manual_seed(7)
        r = V.build_variant("repeat", 16).state_dict()
        self.assertEqual(set(r) - set(a), {"repeat_head.weight", "repeat_head.bias"})
        for k in a:
            self.assertTrue(torch.equal(a[k], r[k]), k)
        extra = sum(r[k].numel() for k in ("repeat_head.weight", "repeat_head.bias"))
        self.assertEqual(extra, 64 * 81 + 81)

    def test_seen_labels_use_the_repeat_layer_and_others_the_new_layer(self):
        x, mk, _ = toy()
        with torch.no_grad():
            h = self.m.history(x, mk)
            out, rep, new = self.m(x, mk), self.m.repeat_head(h), self.m.head(h)
        seen = x.amax(1) > 0.5
        self.assertTrue(seen.any() and (~seen).any())
        self.assertTrue(torch.equal(out[seen], rep[seen]))
        self.assertTrue(torch.equal(out[~seen], new[~seen]))

    def test_seen_at_a_position_ignores_later_steps(self):
        x, mk, _ = toy(B=1, real=(16,))
        x2 = x.clone()
        x2[0, 10] = 0
        x2[0, 10, 5] = 1                                          # change step 10 only
        with torch.no_grad():
            a = self.m.position_logits(self.m.states(x, mk), x)
            b = self.m.position_logits(self.m.states(x2, mk), x2)
        self.assertTrue(torch.allclose(a[0, :10], b[0, :10], atol=1e-6))
        s = V.RepeatPredictor.seen(x)
        self.assertTrue(torch.equal(s[0, 3], x[0, :4].amax(0) > 0.5))

    def test_last_position_of_training_logits_is_the_prediction(self):
        x, mk, _ = toy()
        with torch.no_grad():
            a = self.m.position_logits(self.m.states(x, mk), x)[:, -1]
            self.assertTrue(torch.allclose(a, self.m(x, mk), atol=1e-6))

    def test_loss_is_allpos_loss_on_the_routed_logits(self):
        x, mk, y = toy(B=2, real=(3, 16))
        with torch.no_grad():
            logits = self.m.position_logits(self.m.states(x, mk), x)
            want, n = 0.0, 0
            for b in range(2):
                for k in range(16):
                    if mk[b, k] < 0.5:
                        continue
                    tgt = y[b] if k == 15 else x[b, k + 1]
                    want += torch.nn.functional.binary_cross_entropy_with_logits(logits[b, k], tgt).item()
                    n += 1
            self.assertAlmostEqual(self.m.loss(x, mk, y).item(), want / n, places=5)

    def test_no_nan_with_heavy_padding(self):
        x, mk, y = toy()
        for mode in (True, False):
            self.m.train(mode)
            self.assertTrue(torch.isfinite(self.m.loss(x, mk, y)))
            self.assertTrue(torch.isfinite(self.m(x, mk)).all())


class Recurrent(unittest.TestCase):
    PAIRS = (("gru_allpos", "GRU", "gru_last"), ("lstm_allpos", "LSTM", "lstm_last"))

    def test_harness_reproduces_the_frozen_train_one_exactly(self):
        f = data.folds("main")[-1]
        d = data.fold_data(f)
        torch.set_num_threads(1)
        for _, arm, last in self.PAIRS:
            a, ma = port.T.train_one(arm, 16, 3, d["train"], d["val"], 65, device=CPU, patience_checks=None)
            b, mb = V.train_variant(last, 16, 3, d["train"], d["val"], 65, device=CPU)
            self.assertEqual([p["validation_bce"] for p in a.curve], [p["validation_bce"] for p in b.curve], arm)
            for k, t in ma.state_dict().items():
                self.assertTrue(torch.equal(t, mb.state_dict()[k]), (arm, k))

    def test_same_weights_and_same_prediction_as_the_frozen_arm(self):
        x, mk, _ = toy()
        for v, arm, _ in self.PAIRS:
            torch.manual_seed(7)
            frozen = port.Enc.build_model(arm, 16).eval()
            torch.manual_seed(7)
            m = V.build_variant(v, 16).eval()
            self.assertEqual(frozen.state_dict().keys(), m.state_dict().keys())
            for k, t in frozen.state_dict().items():
                self.assertTrue(torch.equal(t, m.state_dict()[k]), (arm, k))
            with torch.no_grad():
                self.assertTrue(torch.equal(frozen(x, mk), m(x, mk)), arm)

    def test_last_state_is_the_frozen_output_even_with_dropout(self):
        x, mk, _ = toy()
        for v, arm, _ in self.PAIRS:
            torch.manual_seed(0)
            m = V.build_variant(v, 16).train()
            torch.manual_seed(5)
            a = m.encoder(x, mk)
            torch.manual_seed(5)
            last = m.recurrence(x, mk)[:, -1].clone()   # contiguous memory, like the frozen h
            self.assertTrue(torch.equal(a, m.encoder.norm(m.encoder.proj(last))), arm)  # bit-identical
            torch.manual_seed(5)
            b = m.states(x, mk)[:, -1]                            # projected at (B, W, H): rounding
            self.assertTrue(torch.allclose(a, b, atol=2e-6), arm)

    def test_a_step_never_sees_later_steps(self):
        x, mk, _ = toy(B=1, real=(16,))
        x2 = x.clone()
        x2[0, 10] = 0
        x2[0, 10, 5] = 1
        for v, arm, _ in self.PAIRS:
            torch.manual_seed(0)
            m = V.build_variant(v, 16).eval()
            with torch.no_grad():
                a, b = m.states(x, mk), m.states(x2, mk)
            self.assertTrue(torch.equal(a[0, :10], b[0, :10]), arm)
            self.assertFalse(torch.allclose(a[0, 10:], b[0, 10:]), arm)

    def test_loss_uses_next_steps_and_real_positions_only(self):
        x, mk, y = toy(B=2, real=(3, 16))
        for v, arm, _ in self.PAIRS:
            torch.manual_seed(0)
            m = V.build_variant(v, 16).eval()
            with torch.no_grad():
                logits = m.head(m.states(x, mk))
                want, n = 0.0, 0
                for b in range(2):
                    for k in range(16):
                        if mk[b, k] < 0.5:
                            continue
                        tgt = y[b] if k == 15 else x[b, k + 1]
                        want += torch.nn.functional.binary_cross_entropy_with_logits(logits[b, k], tgt).item()
                        n += 1
                self.assertAlmostEqual(m.loss(x, mk, y).item(), want / n, places=5, msg=arm)

    def test_finite_with_heavy_padding(self):
        x, mk, y = toy()
        for v, arm, _ in self.PAIRS:
            torch.manual_seed(0)
            m = V.build_variant(v, 16).train()
            self.assertTrue(torch.isfinite(m.loss(x, mk, y)), arm)


def asl_by_hand(z, y, gneg=4.0, gpos=0.0, clip=0.05, eps=1e-8):
    """The authors' formula in float64 numpy, written out independently."""
    p = 1 / (1 + np.exp(-z))
    pneg = np.minimum(1 - p + clip, 1)
    l = y * np.log(np.maximum(p, eps)) + (1 - y) * np.log(np.maximum(pneg, eps))
    pt = p * y + pneg * (1 - y)
    return -l * (1 - pt) ** (gpos * y + gneg * (1 - y))


class ASL(unittest.TestCase):
    def setUp(self):
        g = np.random.default_rng(1)
        self.z = g.normal(0, 4, (64, 81))
        self.y = (g.random((64, 81)) < 0.1).astype(np.float64)
        self.crit = V.AsymmetricLoss()

    def test_settings_are_the_authors_train_py(self):
        self.assertEqual((V.ASL_GAMMA_NEG, V.ASL_GAMMA_POS, V.ASL_CLIP, V.ASL_EPS), (4.0, 0.0, 0.05, 1e-8))

    def test_matches_the_formula_written_by_hand(self):
        got = self.crit(torch.from_numpy(self.z), torch.from_numpy(self.y)).numpy()
        np.testing.assert_allclose(got, asl_by_hand(self.z, self.y), rtol=1e-10, atol=1e-12)

    def test_easy_negatives_count_zero(self):
        z = torch.tensor([[-4.0, -10.0]], dtype=torch.float64)       # p < 0.05
        self.assertTrue(torch.equal(self.crit(z, torch.zeros_like(z)), torch.zeros_like(z)))

    def test_no_gradient_through_the_focusing_weight(self):
        z = torch.from_numpy(self.z).requires_grad_(True)
        self.crit(z, torch.from_numpy(self.y)).sum().backward()
        p, y = 1 / (1 + np.exp(-self.z)), self.y
        pneg = np.minimum(1 - p + 0.05, 1)
        w = (1 - (p * y + pneg * (1 - y))) ** (4 * (1 - y))
        d_neg = np.where(1 - p + 0.05 < 1, p * (1 - p) / pneg, 0.0)  # d(-log pneg)/dz, 0 when clipped
        want = y * -(1 - p) + (1 - y) * w * d_neg                    # weight held constant
        np.testing.assert_allclose(z.grad.numpy(), want, rtol=1e-8, atol=1e-12)

    def test_without_focusing_and_clip_it_is_bce(self):
        z, y = torch.from_numpy(self.z / 4), torch.from_numpy(self.y)
        bce = torch.nn.functional.binary_cross_entropy_with_logits(z, y, reduction="none")
        self.assertTrue(torch.allclose(V.AsymmetricLoss(0.0, 0.0, 0.0)(z, y), bce, atol=1e-10))

    def test_same_weights_and_same_random_stream_as_allpos(self):
        out = {}
        for v in ("allpos", "asl"):
            torch.manual_seed(7)
            m = V.build_variant(v, 16)
            out[v] = (m.state_dict(), torch.rand(5))
        self.assertEqual(out["asl"][0].keys(), out["allpos"][0].keys())
        for k in out["allpos"][0]:
            self.assertTrue(torch.equal(out["asl"][0][k], out["allpos"][0][k]), k)
        self.assertTrue(torch.equal(out["asl"][1], out["allpos"][1]))

    def test_loss_is_the_allpos_average_of_asl(self):
        torch.manual_seed(0)
        m = V.build_variant("asl", 16).eval()
        x, mk, y = toy(B=2, real=(3, 16))
        with torch.no_grad():
            logits = m.head(m.states(x, mk)).double().numpy()
            want, n = 0.0, 0
            for b in range(2):
                for k in range(16):
                    if mk[b, k] < 0.5:
                        continue
                    tgt = (y[b] if k == 15 else x[b, k + 1]).double().numpy()
                    want += asl_by_hand(logits[b, k], tgt).mean()
                    n += 1
            self.assertAlmostEqual(m.loss(x, mk, y).item(), want / n, places=5)

    def test_finite_with_padding_and_extreme_logits(self):
        torch.manual_seed(0)
        m = V.build_variant("asl", 16).train()
        x, mk, y = toy()
        self.assertTrue(torch.isfinite(m.loss(x, mk, y)))
        z = torch.tensor([[-80.0, 80.0, 0.0]])
        self.assertTrue(torch.isfinite(self.crit(z, torch.tensor([[1.0, 0.0, 1.0]]))).all())


if __name__ == "__main__":
    unittest.main()
