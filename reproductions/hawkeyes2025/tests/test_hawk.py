# -*- coding: utf-8 -*-
"""Tests of the rebuilt Hawkeyes environment (no training).

    python -m unittest discover -s reproductions/hawkeyes2025/tests
"""
import random
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import hawk_env as H  # noqa: E402


class Network(unittest.TestCase):
    def test_old_network(self):
        n = H.Network()
        self.assertEqual(len(H.REAL), 11)
        self.assertEqual(n.entry, ["Tablet", "Host1", "Web"])
        self.assertEqual(n.out["Web"], ["DB"])
        self.assertNotIn("API", {b for _, b in n.edges})               # no CVE, no edge in
        self.assertEqual((n.init_groups, n.crit_groups, n.crit_only), ([0, 2], [1, 2, 3], [3]))
        self.assertEqual(H.STATE_DIM, 374)

    def test_new_network(self):
        n = H.Network(True)
        self.assertIn("Host2", n.entry)
        self.assertNotIn(("Tablet", "Host2"), n.edges)
        self.assertEqual(n.max_cvss["Host3"], 8.8)


class Attacker(unittest.TestCase):
    def run_hi(self, policy, hp_groups, n=2000):
        env = H.Env(H.Network(), policy, 0.05, 0.02, rng=random.Random(5))
        traps = 0
        for _ in range(n):
            env.reset()
            while True:
                _, r, done, out = env.step(hp_groups)
                if done:
                    traps += out == "trap"
                    break
        return traps / n

    def test_decision24_prediction(self):
        self.assertEqual(self.run_hi("HiC", [2, 0]), 1.0)              # Honeypot 1 next to the Web Server
        self.assertEqual(self.run_hi("HiE", [0, 0]), 0.0)              # no honeypot in Subnet 3
        self.assertAlmostEqual(self.run_hi("HiE", [2, 0]), 0.5, delta=0.04)
        self.assertAlmostEqual(self.run_hi("HiE", [2, 2]), 2 / 3, delta=0.04)

    def test_gate(self):
        env = H.Env(H.Network(), "Ran", 0.0, 0.0, rng=random.Random(1))
        env.reset()
        self.assertEqual(env.allowed_groups()[1], "init")
        env.comp = {"Web"}
        env.alerts = env._observe()
        self.assertEqual(env.allowed_groups(), ([1, 2, 3], "crit"))
        env.comp = {"Tablet"}
        env.alerts = env._observe()
        self.assertEqual(env.allowed_groups()[1], "low")
        self.assertEqual(env.allowed_groups(gated=False)[1], "none")


if __name__ == "__main__":
    unittest.main()
