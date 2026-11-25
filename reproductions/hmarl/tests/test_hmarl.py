# -*- coding: utf-8 -*-
"""Tests for the H-MARL reproduction harness (standard library only; no venv, no CybORG).

    python -m unittest discover -s reproductions/hmarl/tests
"""
import csv
import statistics
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import fetch  # noqa: E402
import run as R  # noqa: E402


def fake_log(rewards, impacts_by_agent):
    """The lines the authors' evaluation_metrics.py prints (structure copied from its print statements)."""
    out, running = ["CybORG v4.0, Scenario4"], []
    for i, r in enumerate(rewards):
        running.append(r)
        out += ["", f"Episode: {i} {statistics.mean(running)!r}", "Infection:",
                "running avg subnet_a noninfection: 0.8 nonprivileged: 0.99",
                f"Noninfection frac across subnets: {0.70 + i / 100:.2f}", "Nonprivileged frac across subnets: 0.97",
                "", "True False pos:", "True pos across subnets: 6.07", "False pos across subnets: 2.2",
                "", "Infection stride length:", "Mean stride across subnets: 44.76",
                "", "Privileged stride length:", "Mean stride  across subnets: 3.1", "", "Impact Actions:"]
        for a, counts in impacts_by_agent.items():
            sofar = counts[:i + 1]
            out.append(f"{a} ['operational_zone_a_subnet'] Impact {sofar} mean {round(statistics.mean(sofar), 2)}")
    out.append(f"Average reward is: {statistics.mean(rewards)!r} with a standard deviation of 1.0")
    return "\n".join(out) + "\n"


class Parse(unittest.TestCase):
    def test_rewards_metrics_and_impacts(self):
        rewards = [-120.5, -140.25, -101.0, -133.75]
        imp = {"red_agent_0": [0, 1, 0, 2], "red_agent_3": [1, 0, 0, 1]}
        res = R.parse_log(fake_log(rewards, imp))
        for a, b in zip(res["rewards"], rewards):
            self.assertAlmostEqual(a, b, places=9)                      # recovered from running means
        self.assertEqual(res["impacts"], [1, 1, 0, 3])                  # summed over red agents, per episode
        m = res["metrics"]
        self.assertAlmostEqual(m["red_impact_count"], 1.25)
        self.assertEqual(m["clean_hosts"], 0.73)                       # the LAST summary (running average)
        self.assertEqual(m["mean_time_to_recover"], 44.76)             # infection stride, not the privileged one
        self.assertAlmostEqual(m["recovery_precision"], 6.07 / 8.27)
        self.assertAlmostEqual(m["recovery_error"], 2.2 / 8.27)

    def test_refuses_inconsistent_output(self):
        text = fake_log([-1.0, -2.0], {"red_agent_0": [0, 0]}).replace("Average reward is: -1.5", "Average reward is: -9.0")
        with self.assertRaises(ValueError):
            R.parse_log(text)
        with self.assertRaises(ValueError):
            R.impact_totals("Episode: 0 -1.0\nred_agent_0 [x] Impact [0, 1] mean 0.5\n", 1)   # list length != episodes


class Stats(unittest.TestCase):
    def test_interval_and_verdict_rules(self):
        s = R.summarise([-130.0 + i for i in range(10)])              # mean -125.5, seed sd 3.03
        half = R.T_975_DF9 * statistics.stdev([-130.0 + i for i in range(10)]) / 10 ** 0.5
        self.assertAlmostEqual(s["ci"][1] - s["mean"], half)
        self.assertGreater(s["prediction"][1] - s["prediction"][0], s["ci"][1] - s["ci"][0])
        reward = "REWARD: ..."
        self.assertEqual(R.verdict(s, "-125.5", reward, 44.6), "MATCH")
        self.assertEqual(R.verdict(s, "-150", reward, 44.6), "CLOSE")  # outside the CI, within one published std
        self.assertEqual(R.verdict(s, "-200", reward, 44.6), "NO MATCH")
        metric = "METRIC: ..."
        self.assertEqual(R.verdict(s, "-130.5", metric), "CLOSE")      # outside the CI, inside the prediction interval
        self.assertEqual(R.verdict(s, "-160", metric), "NO MATCH")
        self.assertEqual(R.verdict(s, "-1", "NOT ATTEMPTED: x"), "NOT ATTEMPTED")
        t = R.summarise([0.806] * 10)
        self.assertEqual(R.verdict(t, "0.81", metric), "MATCH")       # 0.81 stands for [0.805, 0.815]
        self.assertEqual(R.published_sd("x (published std 44.60)"), 44.6)


class Targets(unittest.TestCase):
    def test_targets_file_and_ids(self):
        with (HERE / "TARGETS.csv").open(encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        attempted = [r for r in rows if not r["tolerance"].startswith("NOT ATTEMPTED")]
        self.assertEqual((len(rows), len(attempted), sum(r["primary"] == "yes" for r in rows)), (64, 30, 24))
        for r in rows:
            key = R.target_key(r["id"])
            self.assertEqual(key is not None, r in attempted, r["id"])       # attempted <=> computable
            if r["tolerance"].startswith("REWARD"):
                self.assertIsNotNone(R.published_sd(r["quantity"]), r["id"])
        self.assertEqual({R.target_key(r["id"])[0] for r in attempted}, set(R.METHODS))


class Pins(unittest.TestCase):
    def test_manifest_and_decisions(self):
        lines = (HERE / "POLICY_SHA256.txt").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 87)
        self.assertEqual(sum(ln.endswith("policy_state.pkl") for ln in lines), 25)
        self.assertEqual(fetch.REPOS["Hierarchical-MARL"][1][:7], "6fe960f")
        self.assertEqual(fetch.REPOS["cage-challenge-4"][1][:7], "8c3c50c")
        text = (HERE / "DECISIONS.md").read_text(encoding="utf-8")
        for s in ("Python 3.10", "Ray 2.10.0", "10 evaluation seeds", "COMPUTE_METRICS"):
            self.assertIn(s, text)

    def test_clones_are_pinned_and_unchanged(self):
        if not (fetch.EXT / "Hierarchical-MARL").exists():
            self.skipTest("run fetch.py first")
        self.assertEqual(fetch.check(), [])


if __name__ == "__main__":
    unittest.main()
