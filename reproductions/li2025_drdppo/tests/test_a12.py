# -*- coding: utf-8 -*-
"""Tests for A12, the sensitivity analysis of the paper's readings (M1-M8)."""
import dataclasses
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import drdppo as D  # noqa: E402
import sensitivity_m as S  # noqa: E402


class Readings(unittest.TestCase):
    def test_defaults_keep_the_logged_keys(self):
        held = json.loads((HERE / "out" / "heldout.json").read_text(encoding="utf-8"))
        self.assertEqual(D.Setting(**held["final_setting"]).key(), held["final_key"])
        self.assertIn("attacker=proportional", D.Setting(attacker="proportional").key())

    def test_proportional_attacker_follows_normalised_importance(self):
        e = D.Env(D.Setting(attacker="proportional"), np.random.default_rng(0))
        e.reset()
        e.apply(D.ADD_H)
        for _ in range(3):
            e.apply(D.ADD_F)
        _, sc, hp = e.scores()
        want = sc[hp].sum() / sc.sum()
        got = np.mean([e.attack() for _ in range(20000)])
        self.assertAlmostEqual(got, want, delta=0.015)
        self.assertGreater(want, 0.0)
        self.assertLess(want, 1.0)

    def test_real_first_ties(self):
        e = D.Env(D.Setting(ties="real_first"), np.random.default_rng(0))
        e.reset()
        e.apply(D.ADD_H)
        for _ in range(5):
            e.apply(D.ADD_F)                                                    # H ties with both servers (P1)
        self.assertEqual({e.attack() for _ in range(200)}, {False})

    def test_alg1_config_draws_valid_configurations(self):
        e = D.Env(D.Setting(alg1="config"), np.random.default_rng(3))
        seen = set()
        for _ in range(300):
            e.reset("config_random")
            nd, nv = int(e.h_on.sum()), int(e.f_on.sum())
            self.assertTrue(0 <= nd <= 2 and 0 <= nv <= 10)
            if nd == 0:
                self.assertEqual(nv, 0)                                          # Eqs. (12), (14)
            self.assertTrue(all(e.h_on[e.f_link[k]] for k in np.flatnonzero(e.f_on)))
            seen.add((nd, nv))
        self.assertGreater(len(seen), 15)

    def test_joint_actions_respect_the_constraints(self):
        e = D.Env(D.Setting(action="joint"), np.random.default_rng(0))
        e.reset()
        md, _ = e.joint_count_masks()
        self.assertEqual(list(np.flatnonzero(md) - D.ALPHA), [0, 1, 2])
        _, mv = e.joint_count_masks(0)
        self.assertEqual(list(np.flatnonzero(mv) - D.BETA), [0])                # no F without an H
        e.step({"dd": 2, "dv": 7, "targets": np.array([1, 0]), "links": np.full(10, 1)})
        self.assertEqual((int(e.h_on.sum()), int(e.f_on.sum())), (2, 7))
        self.assertEqual(list(e.h_target), [1, 0])
        e.step({"dd": -1, "dv": 0, "targets": np.array([0, 0]), "links": np.full(10, 1)})
        self.assertTrue(all(e.f_link[k] == 0 for k in np.flatnonzero(e.f_on)))   # relinked to the active H
        with self.assertRaises(ValueError):
            e.step({"dd": 2, "dv": 0, "targets": np.zeros(2, int), "links": np.zeros(10, int)})

    def test_scripted_joint_wins_in_one_step(self):
        self.assertEqual(D.run_policy(D.Setting(action="joint"), 0, 3, "scripted"), [True] * 3)

    def test_cost_final_is_charged_once(self):
        e = D.Env(D.Setting(cost="final", R1=10, R2=0), np.random.default_rng(0))
        e.reset()
        _, r, _ = e.step(D.ADD_H)
        self.assertEqual(r, 0.0)
        for _ in range(29):
            _, r, done = e.step(D.NOOP)
        self.assertTrue(done)
        self.assertAlmostEqual(r, (10 if e.success else -10) - 0.5)

    def test_f_host_clone_scores(self):
        e = D.Env(D.Setting(f_score="host_clone"), np.random.default_rng(0))
        e.reset()
        e.apply(D.ADD_H)
        e.apply(D.ADD_F)
        names, sc, _ = e.scores()
        self.assertAlmostEqual(sc[names.index("F0")], e.world.vuln["Host1"] + 0.1)

    def test_joint_ppo_learns_without_errors(self):
        r = D.train_ppo(D.Setting(action="joint"), 0, 3, eval_episodes=2)
        self.assertEqual((len(r["train"]), len(r["eval"])), (3, 2))
        r = D.train_ppo(D.Setting(action="joint"), 0, 2, variant="alg2")
        self.assertEqual(len(r["train"]), 2)


class Design(unittest.TestCase):
    def test_full_factorial_and_shared_trials(self):
        base = D.Setting()
        cs = S.combos(base)
        self.assertEqual(len(cs), 256)
        self.assertEqual(len({c.key() for c in cs}), 256)
        need = {(S.effective(c, p).key(), p) for c in cs for p in S.POLICIES}
        self.assertEqual(len(need), 168)
        s = D.Setting(attacker="proportional", ties="real_first", alg1="config", cost="final", R1=100.0)
        self.assertEqual(S.effective(s, "alg3").key(), D.Setting(attacker="proportional").key())
        self.assertEqual(S.effective(s, "drdppo").alg1, "walk")
        self.assertEqual((S.effective(s, "drdppo").cost, S.effective(s, "drdppo").R1), ("final", 100.0))

    def test_decoys_are_the_declared_ones(self):
        t = (HERE / "DECISIONS.md").read_text(encoding="utf-8")
        for d in S.DECOYS:
            self.assertIn("(" + ", ".join(f"{x:.2f}" for x in d) + ")", t)
        self.assertEqual(S.REAL, (28.43, 55.19, 97.09))

    def test_run_once_and_needs_the_committed_protocol(self):
        orig = S.OUT
        with tempfile.TemporaryDirectory() as tmp:
            S.OUT = Path(tmp)
            (Path(tmp) / "heldout.json").write_text((HERE / "out" / "heldout.json").read_text(encoding="utf-8"), encoding="utf-8")
            (Path(tmp) / "sensitivity_m.json").write_text("{}", encoding="utf-8")
            argv = sys.argv
            sys.argv = ["sensitivity_m.py", "run", "--workers", "1"]
            try:
                with self.assertRaises(SystemExit) as cm:
                    S.main()
                self.assertIn("runs once", str(cm.exception))
            finally:
                sys.argv, S.OUT = argv, orig

    def test_reading_rule_and_markdown(self):
        base = D.Setting()
        orig = S.FACTORS
        S.FACTORS = S.FACTORS[:2] + tuple((f, v[:1]) for f, v in S.FACTORS[2:])
        try:
            with tempfile.TemporaryDirectory() as tmp:
                res = S.run(Path(tmp), 1, base, seeds=(0, 1), episodes=3, heldout_eps=(3, 4))
                S.write_md(res, Path(tmp) / "SENSITIVITY_M.md")
                text = (Path(tmp) / "SENSITIVITY_M.md").read_text(encoding="utf-8")
        finally:
            S.FACTORS = orig
        self.assertEqual(res["n_combinations"], 4)
        self.assertIn(res["reading"], text)
        self.assertEqual(len(res["n_fit_decoys"]), 3)


if __name__ == "__main__":
    unittest.main()
