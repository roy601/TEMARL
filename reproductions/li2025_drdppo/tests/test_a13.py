# -*- coding: utf-8 -*-
"""Tests for A13, the figure-derived reconstruction."""
import dataclasses
import json
import sys
import tempfile
import unittest
from math import comb
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import drdppo as D  # noqa: E402
import figure_reconstruction as F  # noqa: E402

FIG = json.loads((HERE / "data" / "figure_values.json").read_text(encoding="utf-8"))


def med(panel, colour):
    return FIG[panel]["curves"][colour]["median"]


class Measurements(unittest.TestCase):
    def test_axis_calibration_is_tight(self):
        for k, v in FIG.items():
            if k.startswith("fig"):
                self.assertLess(v["y_fit_max_residual"], 0.005, k)

    def test_measurements_match_the_declared_table(self):
        want = {("fig6a_reward", "blue"): 0.084, ("fig6a_reward", "green"): -0.904, ("fig6c_cost", "blue"): 0.912,
                ("fig6c_cost", "orange"): 1.901, ("fig6c_cost", "red"): 1.534, ("fig6b_attack_probability", "blue"): 0.453,
                ("fig6b_attack_probability", "green"): 0.329, ("fig6b_attack_probability", "orange"): 0.554,
                ("fig6b_attack_probability", "red"): 0.621, ("fig5a_reward", "red"): -1.004}
        for (panel, c), v in want.items():
            self.assertAlmostEqual(med(panel, c), v, delta=0.0006, msg=(panel, c))

    def test_re_measure_from_the_pdf_when_available(self):
        pdf = HERE.parents[1] / "PDF" / "Li et al.—DRD-PPO.pdf"
        if not pdf.exists():
            self.skipTest("article PDF not on this machine")
        import importlib.util
        spec = importlib.util.spec_from_file_location("dig", HERE / "checks" / "digitize_figures.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        again = mod.measure(pdf)
        self.assertAlmostEqual(again["fig6c_cost"]["curves"]["blue"]["median"], med("fig6c_cost", "blue"), places=9)


class Derivations(unittest.TestCase):
    def test_d1_reward_rule_gives_r1_one(self):
        self.assertAlmostEqual(med("fig6a_reward", "blue") + med("fig6c_cost", "blue"), 1.0, delta=0.01)
        self.assertAlmostEqual(med("fig6a_reward", "green") + med("fig6c_cost", "orange"), 1.0, delta=0.01)
        self.assertAlmostEqual(med("fig5a_reward", "red"), -1.0, delta=0.01)

    def test_d2_d4_deployments_are_unique(self):
        def combos(c):
            return [(h, f) for h in range(3) for f in range(11) if abs(h * 0.5 + f * 0.1 - c) < 0.05 and (h > 0 or f == 0)]
        self.assertEqual(combos(med("fig6c_cost", "blue")), [(1, 4)])
        self.assertEqual(combos(med("fig6c_cost", "orange")), [(2, 9)])

    def test_d5_w(self):
        v = 1 - (1 - 0.66) ** 3
        w = (v - med("fig6b_attack_probability", "blue") * 2 * v) / (med("fig6b_attack_probability", "blue") * 7 - 3)
        self.assertAlmostEqual(w, 0.53, delta=0.02)

    def test_readings_follow_d1_to_d7(self):
        ra, rb = F.READINGS["R-A"], F.READINGS["R-B"]
        self.assertEqual((ra.R1, ra.R2, ra.cost, ra.links, ra.w, ra.full_f, ra.alg1, ra.attacker),
                         (1.0, 0.0, "final", "P2", 0.5, 9, "fig", "clone_specific"))
        self.assertEqual(dataclasses.replace(ra, attacker="argmax"), rb)


class Mechanics(unittest.TestCase):
    def env(self, **kw):
        e = D.Env(dataclasses.replace(F.RA, **kw), np.random.default_rng(0))
        e.reset()
        return e

    def test_only_clones_of_the_target_compete(self):
        e = self.env()
        e.apply(D.ADD_H)                                                       # H0 clones Server1 (not the target)
        for _ in range(9):
            e.apply(D.ADD_F)
        self.assertEqual({e.attack() for _ in range(100)}, {False})
        self.assertEqual(e.attack_probability(), 1.0)
        e2 = self.env(attacker="argmax")                                      # R-B: any honeypot competes
        e2.apply(D.ADD_H)
        for _ in range(9):
            e2.apply(D.ADD_F)
        self.assertEqual({e2.attack() for _ in range(100)}, {True})

    def test_four_f_on_a_clone_of_the_target_win_three_tie(self):
        e = self.env()
        e.apply(D.ADD_H)
        e.apply(D.RETARGET0 + 1)                                               # H0 -> Server2, the target (P2)
        for _ in range(3):
            e.apply(D.ADD_F)
        self.assertEqual({e.attack() for _ in range(200)}, {True, False})     # tie, uniform
        e.apply(D.ADD_F)
        self.assertEqual({e.attack() for _ in range(100)}, {True})
        self.assertAlmostEqual(e.attack_probability(), 0.4539, places=4)        # Fig. 6b DRD-PPO 0.453

    def test_episode_reward_is_outcome_minus_cost_once(self):
        e = self.env()
        e.step(D.ADD_H)
        e.step(D.RETARGET0 + 1)
        for _ in range(4):
            e.step(D.ADD_F)
        while not e.done:
            e.step(D.NOOP)
        self.assertEqual(e.stats["cost"], 0.9)
        self.assertAlmostEqual(e.stats["reward"], 1.0 - 0.9)                   # the plotted DRD-PPO plateau

    def test_full_and_figure_configurations(self):
        e = D.Env(F.RA, np.random.default_rng(1))
        e.reset("full_random")
        self.assertEqual((int(e.h_on.sum()), int(e.f_on.sum())), (2, 9))
        seen = set()
        for _ in range(300):
            e.reset("fig_random")
            seen.add(int(e.f_on.sum()))
            self.assertEqual(int(e.h_on.sum()), 2)
        self.assertEqual(seen, set(range(1, 11)))


class Predictions(unittest.TestCase):
    @staticmethod
    def p(n, clone_specific):
        tot = 0.0
        for t1 in (0, 1):
            for t2 in (0, 1):
                for x in range(n + 1):
                    pr = 0.25 * comb(n, x) / 2 ** n
                    ks = [k for k, t in zip((x, n - x), (t1, t2)) if t or not clone_specific]
                    m = max(ks) if ks else -1
                    if m >= 4:
                        tot += pr
                    elif m == 3:
                        tied = sum(k == 3 for k in ks)
                        tot += pr * tied / (tied + 1)
        return 100 * tot

    def test_declared_predictions(self):
        for name, cs in (("R-A", True), ("R-B", False)):
            self.assertAlmostEqual(np.mean([self.p(n, cs) for n in range(1, 11)]), F.PREDICTED[name]["alg1"], places=2)
            self.assertAlmostEqual(self.p(9, cs), F.PREDICTED[name]["alg3"], places=2)
        t = (HERE / "DECISIONS.md").read_text(encoding="utf-8")
        for v in ("36.17%", "66.41%", "60.83%", "100.00%"):
            self.assertIn(v, t)

    def test_simulator_agrees_with_the_arithmetic(self):
        for name, s in F.READINGS.items():
            got = D.dsp(D.run_policy(s, 7, 4000, "alg3"))
            self.assertAlmostEqual(got, F.PREDICTED[name]["alg3"], delta=2.5, msg=name)


class Runner(unittest.TestCase):
    def test_tests_are_targets_or_declared(self):
        import csv
        ids = {r["id"] for r in csv.DictReader((HERE / "TARGETS.csv").open(encoding="utf-8"))}
        for tid, p, metric, pub in F.TESTS:
            self.assertTrue(tid in ids or tid.startswith("Fig.6b"), tid)
            self.assertIn(p, F.POLICIES)

    def test_run_once(self):
        orig = F.OUT
        with tempfile.TemporaryDirectory() as tmp:
            F.OUT = Path(tmp)
            (Path(tmp) / "figure_reconstruction.json").write_text("{}", encoding="utf-8")
            argv = sys.argv
            sys.argv = ["figure_reconstruction.py", "run", "--workers", "1"]
            try:
                with self.assertRaises(SystemExit) as cm:
                    F.main()
                self.assertIn("runs once", str(cm.exception))
            finally:
                sys.argv, F.OUT = argv, orig

    def test_tiny_run_and_report(self):
        small = {p: (6, 2 if ev else 0) for p, (eps, ev) in F.POLICIES.items()}
        with tempfile.TemporaryDirectory() as tmp:
            res = F.run(Path(tmp), 1, seeds=(0, 1), policies=small)
            F.write_md(res, Path(tmp) / "FIGURE_RECONSTRUCTION.md")
            text = (Path(tmp) / "FIGURE_RECONSTRUCTION.md").read_text(encoding="utf-8")
        self.assertEqual(set(res["results"]), {"R-A", "R-B"})
        self.assertIn("T4.DRD-PPO", text)
        self.assertEqual(len(res["results"]["R-A"]["tests"]), 6)


if __name__ == "__main__":
    unittest.main()
