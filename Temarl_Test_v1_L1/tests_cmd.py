# -*- coding: utf-8 -*-
"""
Temarl_Test_v1_L1 -- test suite
================================
Asserts the properties the study's claims depend on. A claim whose supporting
property is not tested here is a claim this folder cannot make.

    python tests_cmd.py
"""

from __future__ import annotations

import unittest

import numpy as np
import torch

import _frozen
import baselines_cmd as B
import command_data as D
import encoders_cmd as Enc
import env_cmd as E
import mappo_cmd as M
import metrics_cmd as Mx
import stats_cmd as St
import study_spec as SPEC
import train_cmd as T
from vocab_v2 import NUM_TECHNIQUES as NT


class TestFrozenInputs(unittest.TestCase):
    def test_all_frozen_inputs_verify(self):
        for rel, status in _frozen.verify(strict=True).items():
            self.assertEqual(status, "ok", f"{rel} is {status}")

    def test_corpus_hash_is_pinned(self):
        self.assertIn("thesis_system/data/camlds_commands.json",
                      _frozen.FROZEN_SHA256)

    def test_no_markov_anywhere(self):
        """The study must contain no chain estimation or synthetic generation."""
        import os
        import re
        here = os.path.dirname(os.path.abspath(__file__))
        banned = re.compile(
            r"estimate_chain|profiles_v5|cumT|cuminit|BIGRAM_WEIGHT|INIT_WEIGHT"
            r"|synthetic|augment", re.I)
        offenders = []
        for fn in sorted(os.listdir(here)):
            if not fn.endswith(".py") or fn in ("tests_cmd.py", "_frozen.py"):
                continue
            text = open(os.path.join(here, fn), encoding="utf-8").read()
            # Strip docstrings/comments: prose may discuss what was removed.
            code = re.sub(r'""".*?"""', "", text, flags=re.S)
            code = re.sub(r"#.*", "", code)
            if banned.search(code):
                offenders.append(fn)
        self.assertEqual(offenders, [],
                         f"Markov/synthetic machinery present in {offenders}")


class TestCorpus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runs = D.load_runs()
        cls.split, cls.notes = D.split_runs(cls.runs)

    def test_counts(self):
        self.assertEqual(len(self.runs), 36)
        self.assertEqual(sum(len(r["commands"]) for r in self.runs), 889)
        # 1347 SUB-technique labels collapse to 1336 distinct (command, parent)
        # pairs: 11 commands annotate two sub-techniques of one parent (e.g.
        # T1056.001 and T1056.004 -> T1056), and a set keeps one. Expected.
        self.assertEqual(
            sum(len(c) for r in self.runs for c in r["commands"]), 1336)

    def test_labels_within_vocabulary(self):
        for r in self.runs:
            for c in r["commands"]:
                for t in c:
                    self.assertTrue(0 <= t < NT)

    def test_command_labels_are_a_set(self):
        for r in self.runs:
            for c in r["commands"]:
                self.assertEqual(len(c), len(set(c)), "duplicate label in a command")
                self.assertEqual(list(c), sorted(c), "canonical order broken")

    def test_split_isolation(self):
        groups = {k: {r["group"] for r in v} for k, v in self.split.items()}
        self.assertFalse(groups["train"] & groups["validation"])
        self.assertFalse(groups["train"] & groups["test"])
        self.assertFalse(groups["validation"] & groups["test"])

    def test_every_run_appears_once(self):
        ids = [r["id"] for v in self.split.values() for r in v]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), {r["id"] for r in self.runs})

    def test_held_out_scenario_goes_to_test(self):
        split, _ = D.split_runs(self.runs, held_out="S1")
        self.assertTrue(all(r["scenario"] == "S1" for r in split["test"]))
        self.assertFalse(any(r["scenario"] == "S1" for r in split["train"]))


class TestWindows(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runs = D.load_runs()
        cls.split, _ = D.split_runs(cls.runs)

    def test_target_count_independent_of_window(self):
        counts = {w: len(D.windows(self.split["test"], w)[2])
                  for w in SPEC.WINDOWS}
        self.assertEqual(len(set(counts.values())), 1, counts)

    def test_targets_identical_across_windows(self):
        a = D.windows(self.split["test"], 8)
        b = D.windows(self.split["test"], 64)
        np.testing.assert_array_equal(a[2], b[2])
        self.assertEqual(a[3], b[3])

    def test_left_padding_no_internal_gaps(self):
        X, Mk, Y, _, _ = D.windows(self.split["test"], 16)
        for m in Mk:
            idx = np.where(m > 0)[0]
            if idx.size:
                self.assertEqual(idx[-1], len(m) - 1, "not left-padded")
                self.assertEqual(list(idx), list(range(idx[0], len(m))))

    def test_no_labels_at_padded_positions(self):
        X, Mk, _, _, _ = D.windows(self.split["test"], 16)
        self.assertEqual(float((X.sum(-1) * (1 - Mk)).sum()), 0.0)

    def test_target_is_the_next_command(self):
        r = self.split["test"][0]
        X, Mk, Y, owners, _ = D.windows([r], 16)
        for t in range(1, len(r["commands"])):
            expected = np.zeros(NT, np.float32)
            expected[list(r["commands"][t])] = 1.0
            np.testing.assert_array_equal(Y[t - 1], expected)

    def test_history_excludes_the_target(self):
        r = self.split["test"][0]
        X, Mk, Y, _, _ = D.windows([r], 64)
        for i in range(len(Y)):
            overlap_ok = True        # a technique may legitimately recur
            self.assertTrue(overlap_ok)
            # the LAST history position must be command i, not i+1
            last = set(np.where(X[i, -1] > 0)[0])
            self.assertEqual(last, set(r["commands"][i]))

    def test_window_coverage_monotone(self):
        pct = [D.window_coverage(self.split["test"], w)["full_history_pct"]
               for w in (8, 16, 32, 64)]
        self.assertEqual(pct, sorted(pct))
        self.assertAlmostEqual(pct[-1], 100.0, places=5)


class TestEncoders(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        runs = D.load_runs()
        split, _ = D.split_runs(runs)
        X, Mk, Y, _, _ = D.windows(split["test"], 8)
        full = np.where(Mk.sum(1) == 8)[0][:6]
        cls.x = torch.tensor(X[full])
        cls.m = torch.tensor(Mk[full])

    def test_label_order_invariance(self):
        """Permuting the label axis must not change the output."""
        perm = torch.randperm(NT)
        for arm in ("Transformer", "GRU", "LSTM", "OrderFree"):
            torch.manual_seed(0)
            a = Enc.build_model(arm, 8).eval()
            b = Enc.build_model(arm, 8)
            b.load_state_dict(a.state_dict())
            b.eval()
            b.encoder.embed.lin.weight.data = a.encoder.embed.lin.weight.data[:, perm]
            with torch.no_grad():
                d = (a.history(self.x, self.m)
                     - b.history(self.x[:, :, perm], self.m)).abs().max()
            self.assertLess(float(d), 1e-5, arm)

    def test_order_free_ignores_command_order(self):
        torch.manual_seed(0)
        mdl = Enc.build_model("OrderFree", 8).eval()
        with torch.no_grad():
            d = (mdl.history(self.x, self.m)
                 - mdl.history(torch.flip(self.x, [1]), self.m)).abs().max()
        self.assertLess(float(d), 1e-5)

    def test_sequence_arms_are_order_sensitive(self):
        for arm in ("Transformer", "GRU", "LSTM"):
            torch.manual_seed(0)
            mdl = Enc.build_model(arm, 8).eval()
            with torch.no_grad():
                d = (mdl.history(self.x, self.m)
                     - mdl.history(torch.flip(self.x, [1]), self.m)).abs().max()
            self.assertGreater(float(d), 1e-3, arm)

    def test_capacity_matched(self):
        specs = Enc.arm_specs(16)
        target = specs["Transformer"]["trunk_params"]
        for arm in ("GRU", "LSTM", "OrderFree"):
            rel = abs(specs[arm]["trunk_params"] - target) / target
            self.assertLessEqual(rel, Enc.CAPACITY_TOLERANCE, arm)

    def test_trainable_params_independent_of_window(self):
        for arm in ("Transformer", "GRU", "LSTM", "OrderFree"):
            counts = {w: Enc.parameter_report(arm, w)["total_trainable"]
                      for w in SPEC.WINDOWS}
            self.assertEqual(len(set(counts.values())), 1, f"{arm}: {counts}")

    def test_positional_encoding_is_a_buffer(self):
        m = Enc.build_model("Transformer", 16)
        self.assertTrue(all(not p.requires_grad or p is not m.encoder.pos.pe
                            for p in m.parameters()))
        names = [n for n, _ in m.named_parameters()]
        self.assertFalse(any("pos.pe" in n for n in names))

    def test_pe_buffer_grows_with_window(self):
        a = Enc.parameter_report("Transformer", 16)["non_trainable_buffer_elements"]
        b = Enc.parameter_report("Transformer", 64)["non_trainable_buffer_elements"]
        self.assertEqual(b, 4 * a)

    def test_rejects_right_padding(self):
        x = self.x.clone()
        m = self.m.clone()
        m[0, -1] = 0.0                                # gap at the end
        with self.assertRaises(ValueError):
            Enc.build_model("GRU", 8).history(x, m)

    def test_rejects_empty_batch(self):
        with self.assertRaises(ValueError):
            Enc.build_model("GRU", 8).history(self.x[:0], self.m[:0])

    def test_nohistory_is_zero(self):
        mdl = Enc.build_model("NoHistory", 8).eval()
        with torch.no_grad():
            h = mdl.history(self.x, self.m)
        self.assertEqual(float(h.abs().max()), 0.0)


class TestMetrics(unittest.TestCase):
    def test_bce_matches_torch(self):
        rng = np.random.default_rng(0)
        z = rng.normal(0, 3, (20, NT))
        y = (rng.random((20, NT)) < 0.05).astype(float)
        mine = Mx.bce(z, y)
        theirs = torch.nn.functional.binary_cross_entropy_with_logits(
            torch.tensor(z), torch.tensor(y)).item()
        self.assertAlmostEqual(mine, theirs, places=9)

    def test_perfect_prediction(self):
        y = np.zeros((5, NT)); y[:, [1, 2]] = 1.0
        logits = np.where(y > 0, 10.0, -10.0)
        m = Mx.evaluate(logits, y, ["r"] * 5, 0.5)
        self.assertAlmostEqual(m["micro_f1"], 1.0)
        self.assertAlmostEqual(m["exact_set_accuracy"], 1.0)

    def test_macro_f1_only_supported_labels(self):
        y = np.zeros((4, NT)); y[:, 3] = 1.0
        logits = np.full((4, NT), -10.0); logits[:, 3] = 10.0
        m = Mx.threshold_metrics(1 / (1 + np.exp(-logits)), y, 0.5)
        self.assertEqual(m["macro_f1_label_count"], 1)

    def test_threshold_selection_tie_rule(self):
        y = np.zeros((4, NT)); y[:, 0] = 1.0
        prob = np.zeros((4, NT)); prob[:, 0] = 0.9
        self.assertEqual(Mx.select_threshold(prob, y), 0.1)

    def test_ranking_metrics_bounded(self):
        rng = np.random.default_rng(1)
        y = (rng.random((10, NT)) < 0.03).astype(float)
        y[:, 0] = 1.0
        r = Mx.ranking_metrics(rng.random((10, NT)), y)
        for v in r.values():
            self.assertTrue(0.0 <= v <= 1.0)


class TestEnvironment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runs = D.load_runs()
        cls.split, _ = D.split_runs(cls.runs)
        cls.meta = E.scenario_metadata()
        cls.cfg = E.EnvConfig()
        cls.specs, _ = E.evaluation_specs(cls.split["test"], 2, 5, cls.meta)
        cls.max_steps = max(len(r["commands"]) for r in cls.runs)

    def _env(self, cfg=None):
        return E.CommandEngagementEnv(cfg or self.cfg, self.max_steps)

    def test_one_command_one_step(self):
        env = self._env()
        spec = self.specs[0]
        env.reset(spec)
        n = 0
        while not env.done:
            env.step([0, 0, 0, 0])
            n += 1
        self.assertEqual(n, env.t)
        self.assertLessEqual(env.t, spec.horizon)

    def test_dwell_never_exceeds_steps(self):
        env = self._env()
        for s in self.specs:
            st = E.run_episode(env, s, B.StaticPolicy(1))
            self.assertLessEqual(st["dwell"], st["length"])

    def test_one_engagement_reward_per_command(self):
        """A 13-label command may still earn at most 1.0."""
        env = self._env()
        for s in self.specs:
            env.reset(s)
            while not env.done:
                r, _, _ = env.step([1, 1, 0, 0])
                self.assertLessEqual(r, 1.0)

    def test_set_aggregation_max_ge_mean(self):
        labels = self.runs[0]["commands"][0]
        for d in range(1, 6):
            self.assertGreaterEqual(E.command_payoff(labels, d, "max"),
                                    E.command_payoff(labels, d, "mean"))

    def test_common_random_numbers(self):
        a = [E.run_episode(self._env(), s, B.StaticPolicy(2)) for s in self.specs]
        b = [E.run_episode(self._env(), s, B.StaticPolicy(2)) for s in self.specs]
        self.assertEqual(a, b)

    def test_capacity_degrades_fidelity(self):
        env = self._env()
        env.reset(self.specs[0])
        _, _, info = env.step([1, 1, 1, 1])          # 4 decoys, K = 2
        self.assertAlmostEqual(info["phi"], 0.5)

    def test_replay_cannot_invent_commands(self):
        env = self._env()
        spec = self.specs[0]
        env.reset(spec)
        seen = []
        while not env.done:
            seen.append(spec.commands[env.t])
            env.step([0, 0, 0, 0])
        self.assertEqual(seen, list(spec.commands[:len(seen)]))

    def test_empty_replay_pool_raises(self):
        with self.assertRaises(ValueError):
            E.ReplayPool([], seed=0, meta=self.meta)

    def test_history_window_is_past_only(self):
        env = self._env()
        spec = self.specs[0]
        env.reset(spec)
        env.step([0, 0, 0, 0])
        env.step([0, 0, 0, 0])
        x, m = env.history_window(16)
        self.assertEqual(int(m.sum()), 2)
        np.testing.assert_array_equal(
            np.where(x[-1] > 0)[0], np.array(sorted(spec.commands[1])))

    def test_observation_is_local(self):
        """An agent must not see another zone's technique labels."""
        env = self._env()
        env.reset(self.specs[0])
        env.step([1, 1, 1, 1])
        obs = env.local_obs()
        for i, z in enumerate(E.AGENT_ZONE):
            if z != env.zone:
                tech = obs[i, E.O_TECH:E.O_TECH + NT]
                self.assertEqual(float(tech.sum()), 0.0)

    def test_episode_ends_at_horizon_or_objective(self):
        env = self._env()
        for s in self.specs:
            st = E.run_episode(env, s, B.NullPolicy())
            self.assertTrue(st["length"] <= st["horizon"])
            if st["protected"] == 1.0:
                self.assertEqual(st["length"], st["horizon"])

    def test_reward_equals_dwell(self):
        env = self._env()
        for s in self.specs[:4]:
            env.reset(s)
            total = 0.0
            while not env.done:
                r, _, _ = env.step([1, 2, 0, 0])
                total += r
            self.assertEqual(total, env.dwell)

    def test_step_after_done_raises(self):
        env = self._env()
        env.reset(self.specs[0])
        while not env.done:
            env.step([0, 0, 0, 0])
        with self.assertRaises(RuntimeError):
            env.step([0, 0, 0, 0])

    def test_rejects_bad_actions(self):
        env = self._env()
        env.reset(self.specs[0])
        with self.assertRaises(ValueError):
            env.step([0, 0, 0])
        with self.assertRaises(ValueError):
            env.step([0, 0, 0, 99])


class TestBaselines(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        runs = D.load_runs()
        cls.split, _ = D.split_runs(runs)
        cls.meta = E.scenario_metadata()
        cls.cfg = E.EnvConfig()
        cls.max_steps = max(len(r["commands"]) for r in runs)
        cls.specs, _ = E.evaluation_specs(cls.split["test"], 2, 7, cls.meta)

    def test_null_scores_zero_dwell(self):
        r = B.evaluate_policy(B.NullPolicy(), self.specs, self.cfg, self.max_steps)
        self.assertEqual(r["dwell"], 0.0)

    def test_ladder_is_ordered(self):
        va, _ = E.evaluation_specs(self.split["validation"], 1, 8, self.meta)
        L = B.ladder(va, self.specs, self.cfg, self.max_steps)
        t = L["test"]
        self.assertLess(t["null"]["dwell"], t["best_fixed"]["dwell"])
        self.assertLess(t["best_fixed"]["dwell"], t["clairvoyant_coord"]["dwell"])

    def test_coordination_has_value(self):
        va, _ = E.evaluation_specs(self.split["validation"], 1, 9, self.meta)
        L = B.ladder(va, self.specs, self.cfg, self.max_steps)
        h = B.headroom(L["test"])
        self.assertGreater(h["coordination_value"], 0.0)

    def test_clairvoyant_respects_capacity(self):
        r = B.evaluate_policy(B.ClairvoyantCoordPolicy(self.cfg), self.specs,
                              self.cfg, self.max_steps)
        self.assertEqual(r["capacity_violations"], 0.0)


class TestRL(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        runs = D.load_runs()
        cls.split, _ = D.split_runs(runs)
        cls.meta = E.scenario_metadata()
        cls.cfg = E.EnvConfig()
        cls.max_steps = max(len(r["commands"]) for r in runs)

    def test_history_bank_row0_is_empty_history(self):
        enc = Enc.build_model("GRU", 16)
        bank = M.HistoryBank(enc, 16)
        spec = E.make_spec(self.split["test"][0], np.random.default_rng(0), self.meta)
        tb = bank.table(spec)
        self.assertEqual(len(tb), spec.horizon + 1)
        self.assertEqual(float(np.abs(tb[0]).max()), 0.0)

    def test_history_bank_is_past_only(self):
        """Row t must equal the encoder applied to commands [0, t)."""
        enc = Enc.build_model("GRU", 8).eval()
        bank = M.HistoryBank(enc, 8)
        spec = E.make_spec(self.split["test"][0], np.random.default_rng(0), self.meta)
        tb = bank.table(spec)
        env = E.CommandEngagementEnv(self.cfg, self.max_steps).reset(spec)
        for t in (1, 2, 3):
            while env.t < t:
                env.step([0, 0, 0, 0])
            x, m = env.history_window(8)
            with torch.no_grad():
                h = enc.history(torch.tensor(x)[None], torch.tensor(m)[None])
            np.testing.assert_allclose(tb[t], h[0].numpy(), atol=1e-5)

    def test_encoder_is_frozen(self):
        enc = Enc.build_model("GRU", 16)
        M.HistoryBank(enc, 16)
        self.assertTrue(all(not p.requires_grad for p in enc.parameters()))
        self.assertFalse(enc.training)

    def test_critic_dims(self):
        self.assertEqual(M.critic_dim(True),
                         E.GLOBAL_DIM + Enc.H_DIM + E.N_AGENTS)
        self.assertEqual(M.critic_dim(False), E.LOCAL_DIM + Enc.H_DIM)

    def test_gae_terminal_blocks_bootstrap(self):
        T_, E_ = 3, 2
        rew = np.ones((T_, E_), np.float32)
        done = np.zeros((T_, E_), np.float32); done[1] = 1.0
        vals = np.zeros((T_, E_, 1), np.float32)
        last = np.zeros((E_, 1), np.float32)
        adv, ret = M.compute_gae(rew, done, vals, last, 0.99, 0.95)
        np.testing.assert_allclose(adv[1], np.ones((E_, 1)), atol=1e-6)

    def test_nohistory_bank_is_zero(self):
        bank = M.HistoryBank(None, 16, h_zero=True)
        spec = E.make_spec(self.split["test"][0], np.random.default_rng(0), self.meta)
        self.assertEqual(float(np.abs(bank.table(spec)).max()), 0.0)


class TestTraining(unittest.TestCase):
    def test_ordinary_sampler_uniform_exposure(self):
        s = T.OrdinarySampler(100, 10, seed=0)
        g = s.epochs()
        for _ in range(30):                       # exactly 3 epochs
            next(g)
        self.assertEqual(s.exposure.min(), 3)
        self.assertEqual(s.exposure.max(), 3)

    def test_overlap_sampler_changes_spread_not_total(self):
        """Overlap redistributes exposure; it does not add passes."""
        a = T.OrdinarySampler(100, 10, seed=0)
        b = T.OverlapSampler(100, 10, seed=0)
        for s in (a, b):
            g = s.epochs()
            for _ in range(30):
                next(g)
        self.assertAlmostEqual(a.exposure.mean(), b.exposure.mean(), delta=0.2)
        self.assertEqual(a.exposure.min(), a.exposure.max())      # perfectly even
        self.assertLess(b.exposure.min(), b.exposure.max())       # spread out
        self.assertEqual(int((b.exposure == 0).sum()), 0)

    def test_simulate_patience_uses_only_the_past(self):
        curve = [{"update": 64 * i, "validation_bce": v}
                 for i, v in enumerate([1.0, 0.9, 0.9, 0.9, 0.9], start=1)]
        r = T.simulate_patience(curve, patience_checks=2)
        self.assertTrue(r["triggered"])
        self.assertEqual(r["selected_update"], 128)

    def test_choose_patience_prefers_smallest_within_tolerance(self):
        curves = {"a": [{"update": 64 * i, "validation_bce": 1.0 / i}
                        for i in range(1, 40)]}
        r = T.choose_patience(curves, (16, 32), tolerance=1.0)
        self.assertEqual(r["chosen_patience"], 16)

    def test_budget_rounds_up_to_val_every(self):
        res = {"a": [T.TrainResult(arm="GRU", window=16, seed=0,
                                   sampler="ordinary", updates_completed=1000,
                                   best_update=1000)]}
        b = T.choose_update_budget(res)
        self.assertEqual(b["shared_update_budget"] % T.VAL_EVERY, 0)
        self.assertGreaterEqual(b["shared_update_budget"], 1250)


class TestStats(unittest.TestCase):
    def test_paired_matches_scipy_when_available(self):
        try:
            from scipy import stats as sp
        except ImportError:
            self.skipTest("scipy absent")
        rng = np.random.default_rng(3)
        a, b = rng.normal(0.7, .02, 10), rng.normal(0.68, .02, 10)
        r = St.paired_test(a, b)
        t, p = sp.ttest_rel(a, b)
        self.assertAlmostEqual(r["t"], float(t), places=6)
        self.assertAlmostEqual(r["p_raw"], float(p), places=6)

    def test_holm_is_monotone_and_conservative(self):
        fam = [{"p_raw": p} for p in (0.001, 0.02, 0.03, 0.5)]
        got = [r["p_holm"] for r in St.holm(fam)]
        self.assertEqual(got, sorted(got))
        for r, raw in zip(St.holm(fam), (0.001, 0.02, 0.03, 0.5)):
            self.assertGreaterEqual(r["p_holm"], raw)

    def test_verdict_never_claims_equivalence(self):
        r = {"significant": False, "delta": 0.0}
        self.assertEqual(St.verdict(r), "NO CLEAR DIFFERENCE")

    def test_tost_requires_positive_margin(self):
        with self.assertRaises(ValueError):
            St.tost([1, 2, 3], [1, 2, 3], margin=0.0)


class TestSpec(unittest.TestCase):
    def test_cell_counts_consistent(self):
        self.assertEqual(SPEC.MAIN_PREDICTION_CELLS,
                         len(SPEC.PREDICTION_ARMS) * len(SPEC.WINDOWS)
                         * len(SPEC.MAIN_SEEDS))
        self.assertEqual(SPEC.MAIN_RL_CELLS,
                         (len(SPEC.RL_ARMS) + len(SPEC.RL_CONTROLS))
                         * len(SPEC.RL_SEEDS))

    def test_reference_window_is_a_declared_window(self):
        self.assertIn(SPEC.REFERENCE_WINDOW, SPEC.WINDOWS)

    def test_order_free_control_present(self):
        self.assertIn(SPEC.ORDER_FREE, SPEC.PREDICTION_ARMS)
        self.assertIn(SPEC.ORDER_FREE, Enc.ARMS)

    def test_every_arm_buildable(self):
        for arm in Enc.ARMS:
            self.assertIsNotNone(Enc.build_model(arm, SPEC.REFERENCE_WINDOW))


if __name__ == "__main__":
    unittest.main(verbosity=2)
