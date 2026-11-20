# -*- coding: utf-8 -*-
"""Tests for the Li 2025 DRD-PPO calibrated replication (simulator, policies, learner, calibration rules, report).

    python -m unittest discover -s reproductions/li2025_drdppo/tests
"""
import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import drdppo as D  # noqa: E402
import calibrate as C  # noqa: E402
import report as Rp  # noqa: E402


def env(**kw):
    return D.Env(D.Setting(**kw), np.random.default_rng(0))


class Data(unittest.TestCase):
    def test_cvss_from_the_saved_nvd_records(self):
        v2 = D.load_impacts("v2")
        complete = {c for c, v in v2.items() if v == (0.66, 0.66, 0.66)}
        partial = {c for c, v in v2.items() if v == (0.275, 0.275, 0.275)}
        self.assertEqual(partial, {"CVE-2018-8245", "CVE-2014-0226"})                 # Host1, Host3
        self.assertEqual(len(complete), 5)                                           # incl. both servers (F1)
        v3 = D.load_impacts("v3")
        self.assertEqual(v3["CVE-2014-0226"], v2["CVE-2014-0226"])                    # no v3 record (A10)
        self.assertEqual(v3["CVE-2016-1930"], (0.56, 0.56, 0.56))
        sums = (HERE / "data" / "nvd" / "SHA256SUMS.txt").read_text().split()
        import hashlib
        for h, name in zip(sums[0::2], sums[1::2]):
            name = name.lstrip("*")
            self.assertEqual(hashlib.sha256((HERE / "data" / "nvd" / name).read_bytes()).hexdigest(), h, name)

    def test_network_and_links(self):
        self.assertEqual(len(D.HOSTS), 5)
        self.assertEqual(len(D.SERVERS), 2)
        for pat, want in (("P1", (5, 5)), ("P2", (2, 3)), ("P3", (2, 5))):
            w = D.World(D.Setting(links=pat))
            self.assertEqual((w.nl["Server1"], w.nl["Server2"]), want, pat)
        self.assertEqual(D.World(D.Setting(links="P2")).top_server, 1)


class Attacker(unittest.TestCase):
    def test_eq2_scores_by_hand(self):
        e = env(w=0.1)
        e.reset()
        names, sc, hp = e.scores()
        self.assertAlmostEqual(sc[names.index("Server1")], 1 - 0.34 ** 3 + 5 * 0.1)
        self.assertAlmostEqual(sc[names.index("Host1")], 1 - 0.725 ** 3 + 2 * 0.1)
        self.assertFalse(hp.any())

    def test_h_honeypot_needs_more_f_than_the_server_has_links(self):          # A1 / F2
        for pat, need in (("P1", 6), ("P2", 4), ("P3", 6)):
            for w in (0.05, 0.5):
                e = env(links=pat, w=w)
                e.reset()
                e.apply(D.ADD_H)
                if e.h_target[0] != e.world.top_server:
                    e.apply(D.RETARGET0 + e.world.top_server)
                for _ in range(need - 1):
                    e.apply(D.ADD_F)
                _, sc, hp = e.scores()
                self.assertLessEqual(sc[hp].max(), sc[~hp].max() + 1e-12, (pat, w))   # not yet strictly above
                e.apply(D.ADD_F)
                _, sc, hp = e.scores()
                self.assertGreater(sc[hp].max(), sc[~hp].max(), (pat, w))

    def test_ties_are_broken_at_random(self):
        e = D.Env(D.Setting(links="P1"), np.random.default_rng(1))
        e.reset()
        e.apply(D.ADD_H)
        for _ in range(5):
            e.apply(D.ADD_F)                                                     # H ties with both servers
        self.assertEqual({e.attack() for _ in range(200)}, {True, False})


class Constraints(unittest.TestCase):
    def test_eqs_10_to_14(self):
        e = env()
        e.reset()
        m = e.mask()
        self.assertFalse(m[D.ADD_F])                                             # Eq. (12): no F without H
        self.assertFalse(m[D.REM_H])
        e.apply(D.ADD_H)
        e.apply(D.ADD_F)
        self.assertFalse(e.mask()[D.REM_H])                                      # Eq. (14): last H keeps its F
        e.apply(D.ADD_H)
        self.assertFalse(e.mask()[D.ADD_H])                                      # Eq. (10): at most 2
        e.apply(D.RELINK0 + 2 * 0 + 1)                                           # F0 -> H1
        e.apply(D.REM_H)                                                         # removes H1; F0 moves to H0
        self.assertEqual(int(e.f_link[0]), 0)
        for _ in range(9):
            e.apply(D.ADD_F)
        self.assertFalse(e.mask()[D.ADD_F])                                      # Eq. (11): at most 10
        self.assertFalse(e.mask()[D.RETARGET0 + 0])                              # re-target to the same server
        with self.assertRaises(ValueError):
            e.apply(D.ADD_F)

    def test_relation_only_actions_never_change_counts(self):
        e = env()
        e.reset("full_random")
        for _ in range(200):
            e.apply(D.random_action(e, D.RELATION_ACTIONS))
            self.assertEqual((int(e.h_on.sum()), int(e.f_on.sum())), (2, 10))


class Episodes(unittest.TestCase):
    def test_last_step_attack_and_eq5_reward(self):
        e = env(R1=10, R2=0.25)
        e.reset()
        _, r, done = e.step(D.ADD_H)
        self.assertFalse(done)
        self.assertAlmostEqual(r, 0.25 - 0.5)
        for t in range(2, 31):
            _, r, done = e.step(D.NOOP)
            self.assertEqual(done, t == 30)
        self.assertAlmostEqual(r, (10 if e.success else -10) - 0.5)

    def test_random_attack_step_ends_the_episode(self):
        seen = set()
        for sd in range(60):
            e = D.Env(D.Setting(timing="random"), np.random.default_rng(sd))
            e.reset()
            n = 0
            while not e.done:
                e.step(D.NOOP)
                n += 1
            self.assertEqual(n, e.attack_at)
            seen.add(n)
        self.assertTrue(min(seen) >= 1 and max(seen) <= 30 and len(seen) > 10)

    def test_policies_run(self):
        s = D.Setting()
        self.assertEqual(D.run_policy(s, 0, 3, "scripted"), [True, True, True])   # 1 H + 6 F well before step 30
        self.assertEqual(len(D.run_policy(s, 0, 4, "alg1")), 4)
        self.assertEqual(len(D.run_policy(s, 0, 4, "alg3")), 4)


class Learner(unittest.TestCase):
    def test_ppo_variants(self):
        r = D.train_ppo(D.Setting(), 0, 3, eval_episodes=2)
        self.assertEqual((len(r["train"]), len(r["eval"])), (3, 2))
        r = D.train_ppo(D.Setting(), 0, 2, variant="alg2")
        self.assertEqual(len(r["train"]), 2)

    def test_random_initialised_reference_does_not_learn(self):
        import torch
        torch.manual_seed(5)
        a0, _ = D.make_nets(56)
        r1 = D.train_ppo(D.Setting(), 5, 4, learn=False)
        r2 = D.train_ppo(D.Setting(), 5, 4, learn=False)
        self.assertEqual(r1["train"], r2["train"])                                # deterministic, no updates
        self.assertEqual(D.Env(D.Setting(), np.random.default_rng(0)).state_dim, 56)


class Calibration(unittest.TestCase):
    def test_grids_follow_the_protocol(self):
        self.assertEqual(len(C.STAGE1_GRID), 24)
        self.assertEqual((C.STAGE1_GRID[0].w, C.STAGE1_GRID[0].links, C.STAGE1_GRID[0].timing), (0.1, "P1", "last"))
        self.assertEqual(len(C.STAGE2_GRID), 12)
        self.assertEqual(C.SEEDS, tuple(range(10)))

    def test_verdict_rules(self):
        s = {"mean": 97.5, "ci": [96.8, 98.2]}
        self.assertEqual(C.verdict(s, 98.0, {"scripted": 100.0})[0], "UNINFORMATIVE")
        self.assertEqual(C.verdict(s, 98.0, {"scripted": 80.0, "random_init": 30.0})[0], "MATCH")
        self.assertEqual(C.verdict(s, 99.0, {"scripted": 80.0})[0], "CLOSE")
        self.assertEqual(C.verdict(s, 90.0, {"scripted": 80.0})[0], "NO MATCH")

    def test_extra_trials_need_a_commit_and_stage2_rows_set_only_the_learner(self):
        orig = (C.EXTRA, C.committed_unchanged)
        with tempfile.TemporaryDirectory() as tmp:
            C.EXTRA = Path(tmp) / "EXTRA_TRIALS.csv"
            C.EXTRA.write_text("stage,w,links,timing,cvss,h_links,R1,R2,clip,note\n1,0.3,P2,last,,,,,,guess\n"
                               "2,0.3,,,,,5,0,0.2,bad\n", encoding="utf-8")
            try:
                C.committed_unchanged = lambda p: False
                with self.assertRaises(SystemExit):
                    C.extra_settings(1)
                C.committed_unchanged = lambda p: True
                s = C.extra_settings(1)
                self.assertEqual((s[0].w, s[0].links), (0.3, "P2"))
                with self.assertRaises(SystemExit):
                    C.extra_settings(2, D.Setting())
            finally:
                C.EXTRA, C.committed_unchanged = orig

    def test_heldout_needs_the_closed_calibration_and_runs_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            with self.assertRaises(SystemExit):
                C.heldout(out, 1, check_git=False)
            (out / "heldout.json").write_text("{}", encoding="utf-8")
            with self.assertRaises(SystemExit) as cm:
                C.heldout(out, 1, check_git=False)
            self.assertIn("computed once", str(cm.exception))
            with self.assertRaises(SystemExit):
                C.stage1(out, 1)                                                  # no calibration afterwards

    def test_end_to_end_tiny_and_the_report_passes_the_audit_parser(self):
        import audit
        g1, g2 = C.STAGE1_GRID, C.STAGE2_GRID
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            C.STAGE1_GRID, C.STAGE2_GRID = g1[:2], g2[:1]
            try:
                C.stage1(out, 1, episodes=4, seeds=(0, 1))
                C.stage2(out, 1, episodes=4, seeds=(0, 1))
                C.heldout(out, 1, check_git=False, seeds=(0, 1), episodes=(4, 5))
            finally:
                C.STAGE1_GRID, C.STAGE2_GRID = g1, g2
            text = (out / "REPORT.md").read_text(encoding="utf-8")
            with (HERE / "TARGETS.csv").open(encoding="utf-8") as fh:
                ids = {r["id"] for r in csv.DictReader(fh)}
            v = audit.report_verdicts(text, ids)
            self.assertEqual(set(v), ids)
            self.assertTrue(set(v.values()) <= set(audit.VERDICTS))
            self.assertEqual(v["T3.DRD-PPO"], "CALIBRATION TARGET")
            self.assertEqual(v["T4.DRD-DQN"], "NOT ATTEMPTED")
            log = list(csv.DictReader((out / "calibration_log.csv").open(encoding="utf-8")))
            self.assertTrue(any(r["stage"] == "heldout" for r in log))
            n = len(log)
            C.STAGE1_GRID = g1[:2]
            try:                                                                  # logged trials are never re-run
                C.run_trials(out, "stage1", g1[:2], ("alg1",), 4, 1, seeds=(0, 1))
            finally:
                C.STAGE1_GRID = g1
            self.assertEqual(len(list(csv.DictReader((out / "calibration_log.csv").open(encoding="utf-8")))), n)
        self.assertFalse((HERE / "REPORT.md").exists() and "calibrated replication" in (HERE / "REPORT.md").read_text(encoding="utf-8")
                         and not (HERE / "out" / "heldout.json").exists())


class Protocol(unittest.TestCase):
    def test_decisions_declare_the_amendments(self):
        t = (HERE / "DECISIONS.md").read_text(encoding="utf-8")
        for s in ("A1, F2 corrected", "A2, informativeness test", "A6, attack timing", "A10, user trials",
                  "C4, held-out targets", "6 under", "CALIBRATION TARGET"):
            self.assertIn(s, t)


if __name__ == "__main__":
    unittest.main()
