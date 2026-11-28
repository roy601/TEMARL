# -*- coding: utf-8 -*-
"""Rules taken from the paper (and DECISIONS) for the Wang 2020 rebuild. None of these tests computes a
calibration or held-out number.

    python -m unittest discover -s reproductions/wang2020/tests
"""
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import wang_env as W  # noqa: E402
import run as R  # noqa: E402

WEB, PAD, HOST1, HOST2, HOST3, FILE, DATA = range(7)


def att(**kw):
    base = dict(choice="argmax", j="UP", interest="uniform", decoy_interest="data", alpha=0.5, ties="index")
    base.update(kw)
    return W.Attacker(**base)


class FixedRng(random.Random):
    """random() always returns v (exploits succeed for v = 0, fail for v ~ 1; alarms follow FNR/FPR = 0)."""
    def __init__(self, v):
        super().__init__(0)
        self.v = v

    def random(self):
        return self.v


class Graph(unittest.TestCase):
    def test_fig8(self):
        self.assertEqual(sum(len(v) for v in W.IN_EDGES.values()), 20)
        self.assertEqual(W.OUT_DEGREE, [2, 4, 4, 3, 3, 1, 0])
        self.assertEqual(W.J_DECOY, {"UP": 0.8, "RP": 0.6})          # D16: the data server's best in-edge

    def test_actions_d3(self):
        self.assertEqual(len(W.ACTIONS), 21)
        self.assertEqual(W.ACTIONS[0], (WEB, PAD))                   # policy 1 = locations 1 and 2
        self.assertEqual(W.ACTIONS[5], (WEB, DATA))                  # policy 6 = locations 1 and 7
        self.assertEqual(W.ACTIONS[20], (FILE, DATA))                # policy 21 = locations 6 and 7

    def test_grid(self):
        self.assertEqual(len(R.GRID), 144)
        self.assertEqual(len({a.name for a in R.GRID}), 144)


class Attack(unittest.TestCase):
    def test_entry_targets(self):
        for j, want in (("UP", {WEB: 0.8, PAD: 0.6, HOST1: 0.6}), ("RP", {WEB: 0.6, PAD: 0.6, HOST1: 0.48})):
            env = W.Env(att(j=j), (0.0, 0.0), random.Random(0))
            self.assertEqual({n: jv for kind, n, _, jv in env.targets((PAD, HOST2))}, want)

    def test_best_edge_from_any_foothold(self):                     # D15
        env = W.Env(att(j="RP"), (0.0, 0.0), random.Random(0))
        env.comp[WEB] = True
        self.assertAlmostEqual(dict((n, j) for _, n, _, j in env.targets((PAD, HOST1)))[DATA], 0.04)
        env.comp[HOST2] = True
        self.assertAlmostEqual(dict((n, j) for _, n, _, j in env.targets((PAD, HOST1)))[DATA], 0.6)

    def test_decoy_only_behind_a_held_node(self):
        env = W.Env(att(), (0.0, 0.0), random.Random(0))
        self.assertFalse([t for t in env.targets((WEB, DATA)) if t[0] == "decoy"])
        env.comp[WEB] = True
        decoys = [t for t in env.targets((WEB, DATA)) if t[0] == "decoy"]
        self.assertEqual([(d[1], d[3]) for d in decoys], [(WEB, 0.8)])   # never behind the data server

    def test_decoy_interest_readings(self):                         # D6
        for d_i, want in (("data", 0.0), ("location", 0.5)):
            env = W.Env(att(interest="outdegree", decoy_interest=d_i), (0.0, 0.0), random.Random(0))
            env.comp[WEB] = True
            self.assertEqual([t[2] for t in env.targets((WEB, PAD)) if t[0] == "decoy"], [want])

    def test_index_ties_take_table2_order(self):                   # D7, D18
        env = W.Env(att(j="RP"), (0.0, 0.0), random.Random(0))     # Web 0.6 and Pad 0.6 tie at the start
        self.assertEqual(env.choose(env.targets((HOST2, HOST3)))[1], WEB)

    def test_random_ties_are_uniform(self):
        env = W.Env(att(j="RP", ties="random"), (0.0, 0.0), random.Random(1))
        picks = [env.choose(env.targets((HOST2, HOST3)))[1] for _ in range(4000)]
        self.assertAlmostEqual(picks.count(WEB) / 4000, 0.5, delta=0.03)
        self.assertNotIn(HOST1, picks)

    def test_proportional_choice(self):
        a = att(choice="proportional", ties="none", alpha=0.2)
        env = W.Env(a, (0.0, 0.0), random.Random(2))
        c = env.targets((HOST2, HOST3))
        s = {n: 0.2 + 0.8 * j for _, n, _, j in c}
        picks = [env.choose(c)[1] for _ in range(20000)]
        for n in s:
            self.assertAlmostEqual(picks.count(n) / 20000, s[n] / sum(s.values()), delta=0.015)

    def test_random_interest_drawn_per_experiment(self):           # D17
        env = W.Env(att(interest="random"), (0.0, 0.0), random.Random(3))
        first = env.I
        env.reset()
        self.assertNotEqual(first, env.I)


class Episode(unittest.TestCase):
    def test_trap_fail_and_rewards(self):                          # Eq. 10
        env = W.Env(att(), (0.0, 0.0), FixedRng(0.0))             # every exploit succeeds
        s, r, done, out = env.step((PAD, HOST1))                    # Web (0.8) first
        self.assertEqual((s, r, done, out), (1 << WEB, 0, False, None))
        env2 = W.Env(att(), (0.0, 0.0), FixedRng(0.0))
        env2.comp[WEB] = True
        cands = env2.targets((WEB, PAD))
        top = env2.choose(cands)
        self.assertEqual(top[1], FILE)                              # index order: File (6th) before Data and decoys
        env3 = W.Env(att(decoy_interest="location", interest="role", alpha=0.8), (0.0, 0.0), FixedRng(0.0))
        env3.comp[WEB] = True
        self.assertEqual(env3.step((WEB, PAD))[1:], (0, False, None))  # File, Data and the decoy all score 0.96

    def test_data_server_before_decoys_in_index_ties(self):        # D18
        env = W.Env(att(interest="role", alpha=0.8), (0.0, 0.0), FixedRng(0.0))
        env.comp = [True, True, True, True, True, True, False]
        s, r, done, out = env.step((HOST2, PAD))                    # all three score 0.96
        self.assertEqual((r, done, out), (-1, True, "fail"))

    def test_trap(self):
        env = W.Env(att(interest="outdegree", decoy_interest="location", alpha=0.8), (0.0, 0.0), FixedRng(0.0))
        env.comp = [True, True, True, True, True, True, False]
        s, r, done, out = env.step((HOST2, PAD))                    # decoy behind Pad: 0.96 vs data server 0.16
        self.assertEqual((r, done, out), (1, True, "trap"))

    def test_timeout_counts_as_failed_defence(self):               # D8, D19
        env = W.Env(att(), (0.0, 0.0), FixedRng(0.999))            # every exploit fails
        for _ in range(W.MAX_STEPS - 1):
            self.assertFalse(env.step((PAD, HOST1))[2])
        self.assertEqual(env.step((PAD, HOST1))[1:], (-1, True, "timeout"))

    def test_alarms(self):                                         # D9
        env = W.Env(att(), (0.0, 0.0), random.Random(4))
        env.comp[PAD] = env.comp[HOST1] = True
        env.t = 0
        hits = env.step((HOST2, HOST3))[0]
        self.assertTrue(hits >> PAD & 1 and hits >> HOST1 & 1)
        env = W.Env(att(), (1.0, 1.0), random.Random(4))           # FNR 1: never seen; FPR 1: always alarmed
        env.comp[PAD] = True
        s = env.step((HOST2, HOST3))[0]
        self.assertFalse(s >> PAD & 1)
        self.assertTrue(s >> FILE & 1)

    def test_same_seed_same_run(self):
        a = att(choice="proportional", ties="none", interest="random")
        x = W.evaluate(a, W.SETTINGS[1], W.following_alarm(random.Random(5)), 50, 99)
        y = W.evaluate(a, W.SETTINGS[1], W.following_alarm(random.Random(5)), 50, 99)
        self.assertEqual(x, y)


class Defenders(unittest.TestCase):
    def test_following_alarm_d10(self):
        fa = W.following_alarm(random.Random(6))
        three = (1 << PAD) | (1 << HOST2) | (1 << FILE)
        for _ in range(200):
            self.assertTrue(set(W.ACTIONS[fa(three, 0)]) <= {PAD, HOST2, FILE})
            self.assertIn(HOST2, W.ACTIONS[fa(1 << HOST2, 0)])
            self.assertIn(fa(0, 0), range(21))

    def test_random_dynamic_readings(self):                       # D11
        b = W.random_dynamic(random.Random(7), "b")
        a = W.random_dynamic(random.Random(7), "a")
        self.assertGreater(len({b(0, t) for t in range(W.MAX_STEPS)}), 1)
        self.assertEqual(len({a(0, t) for t in range(W.MAX_STEPS)}), 1)
        self.assertEqual([b(0, t) for t in range(5)], [b(123, t) for t in range(5)])   # ignores the state

    def test_eq15_learning_rate(self):                            # D20
        Q = [[0.0] * 21 for _ in range(128)]
        N = [[0] * 21 for _ in range(128)]
        self.assertEqual(W.q_update(Q, N, 0, 3, 1, 0, True, 0.9), 0.5)
        self.assertEqual(Q[0][3], 0.5)
        self.assertAlmostEqual(W.q_update(Q, N, 0, 3, 1, 0, True, 0.9), 1 / 3)

    def test_greedy_random_ties(self):                            # F5
        rng = random.Random(8)
        self.assertEqual(len({W.greedy([0.0] * 21, rng) for _ in range(500)}), 21)


if __name__ == "__main__":
    unittest.main()
