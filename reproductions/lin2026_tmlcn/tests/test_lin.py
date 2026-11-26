# -*- coding: utf-8 -*-
"""Tests for the Lin et al. 2026 package (standard library only).

    python -m unittest discover -s reproductions/lin2026_tmlcn/tests
"""
import csv
import random
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "checks"))
import check_paper as C  # noqa: E402
import make_targets as M  # noqa: E402


class Targets(unittest.TestCase):
    def test_file_matches_generator(self):
        with (HERE / "TARGETS.csv").open(encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(rows, M.rows())
        self.assertEqual((len(rows), sum(r["primary"] == "yes" for r in rows)), (115, 7))
        self.assertEqual(len({r["id"] for r in rows}), 115)

    def test_table6_shape_and_spot_values(self):
        self.assertEqual([len(r) for r in M.TABLE6], [7] * 12)
        self.assertEqual(M.TABLE6[0][0], 10.08)          # Initial Access / Allow
        self.assertEqual(M.TABLE6[3][3], 11.79)          # Privilege escalation / Modify
        self.assertEqual(M.TABLE6[11][1], 11.29)         # Impact / Restore
        self.assertEqual(sum(v < 0 for r in M.TABLE6 for v in r), 14)


class Algorithm1(unittest.TestCase):
    def test_never_negative_and_impact_row_untouched(self):
        rng = random.Random(1)
        for s in range(5):
            Q = C.algorithm1(C.random_attacker(s), 200, rng, alpha=0.1)
            self.assertGreaterEqual(min(min(r) for r in Q), 0.0)
            self.assertEqual(Q[-1], [0.0] * 7)
            self.assertGreater(max(max(r) for r in Q), 0.0)    # it does learn something

    def test_penalty_bound(self):
        self.assertEqual(C.penalties_needed(-3.0, 1e-4), 0)
        n = C.penalties_needed(-4.99, 1e-4)
        q = -3.5
        for _ in range(n):
            q = (1 - 1e-4) * q - 5e-4
        self.assertLessEqual(q, -4.99)                          # n updates suffice ...
        q = -3.5
        for _ in range(n - 1):
            q = (1 - 1e-4) * q - 5e-4
        self.assertGreater(q, -4.99)                            # ... and n - 1 do not


if __name__ == "__main__":
    unittest.main()
