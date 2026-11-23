# -*- coding: utf-8 -*-
"""Tests for the CAGE 4 reproduction harness (no CybORG needed: pure parts and a fake environment).

    python -m unittest discover -s reproductions/cage4/tests
"""
import csv
import json
import statistics
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import fetch  # noqa: E402
import run as R  # noqa: E402


class FakeEnv:
    """Two agents; rewards -1 and -3 per step; every agent is done after `stop` steps."""
    def __init__(self, stop):
        self.stop, self.t, self.agents = stop, 0, ["blue_agent_0", "blue_agent_1"]

    def reset(self):
        self.t = 0
        return {a: None for a in self.agents}, {}

    def action_space(self, name):
        return None

    def step(self, actions):
        self.t += 1
        done = self.t >= self.stop
        return ({a: None for a in self.agents}, {"blue_agent_0": -1.0, "blue_agent_1": -3.0},
                {a: done for a in self.agents}, {a: False for a in self.agents}, {})


class Agent:
    def __init__(self):
        self.calls = 0

    def get_action(self, obs, space):
        self.calls += 1
        return 0


class Loop(unittest.TestCase):
    def test_score_is_the_sum_of_mean_rewards_until_all_done(self):
        agents = {"blue_agent_0": Agent(), "blue_agent_1": Agent(), "blue_agent_9": Agent()}
        score, steps = R.episode(FakeEnv(stop=10_000), agents)
        self.assertEqual((score, steps), (-2.0 * R.EPISODE_LENGTH, R.EPISODE_LENGTH))
        self.assertEqual(agents["blue_agent_9"].calls, 0)              # only agents present in the env act
        score, steps = R.episode(FakeEnv(stop=7), agents)
        self.assertEqual((score, steps), (-12.0, 6))                   # the done step is not added (official loop)

    def test_the_loop_is_the_official_one(self):
        src = (fetch.EXT / "cage-challenge-4" / "CybORG" / "Evaluation" / "evaluation.py")
        if not src.exists():
            self.skipTest("run fetch.py first")
        text = src.read_text(encoding="utf-8")
        for line in ("if all(done.values()):", "r.append(mean(rew.values()))", "total_reward.append(sum(r))",
                     "EPISODE_LENGTH = 500", "observations, _ = wrapped_cyborg.reset()"):
            self.assertIn(line, text)


class Report(unittest.TestCase):
    def test_summary_and_seed_level_interval(self):
        rows = {s: [-190.0 + s, -200.0 + s] for s in R.SEEDS}
        s = R.summarise(rows)
        means = [statistics.mean(v) for v in rows.values()]
        self.assertAlmostEqual(s["mean"], statistics.mean(means))
        half = R.T_975_DF9 * statistics.stdev(means) / 10 ** 0.5
        self.assertAlmostEqual(s["ci_seed_level"][1] - s["mean"], half)
        self.assertEqual((s["episodes"], s["seeds"]), (20, 10))

    def test_verdict_rule_is_the_targets_rule(self):
        s = {"mean": -200.0, "ci_seed_level": [-210.0, -190.0]}
        self.assertEqual(R.verdict(-193, 84, s), "MATCH")
        self.assertEqual(R.verdict(-150, 84, s), "CLOSE")
        self.assertEqual(R.verdict(-300, 84, s), "NO MATCH")
        rows = {r["id"]: r for r in csv.DictReader((HERE / "TARGETS.csv").open(encoding="utf-8"))}
        self.assertIn("inside our 95% CI of the mean", rows["T3.Teamcybermonic.CC4"]["tolerance"])
        self.assertEqual(R.published_std(rows["T3.Teamcybermonic.CC4"]["quantity"]), 84.0)
        self.assertEqual(float(rows["T3.Teamcybermonic.CC4"]["published"]), -193.0)

    def test_report_on_synthetic_seed_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            for s in R.SEEDS:
                eps = [{"episode": i, "score": -193.0 + ((i % 2) * 2 - 1) * 5 + (s - 4.5) * 0.8, "steps": 499,
                        "seconds": 1.0} for i in range(100)]          # seed means spread evenly around -193
                (out / f"episodes_seed{s}.json").write_text(json.dumps({"seed": s, "n": 100, "episodes": eps}), encoding="utf-8")
            res = R.report(out, out / "REPORT.md")
            text = (out / "REPORT.md").read_text(encoding="utf-8")
        v = {r["id"]: r["verdict"] for r in res["targets"]}
        self.assertEqual(v["T3.Teamcybermonic.CC4"], "MATCH")
        self.assertEqual(sum(x == "NOT ATTEMPTED" for x in v.values()), 23)
        self.assertEqual(len(v), 24)
        self.assertIn("Paper verdict: reproduced (scenario CC4)", text)
        for tid in v:
            self.assertIn(f"| {tid} |", text)
        reasons = {r["id"]: r.get("reason") for r in res["targets"]}
        self.assertIn("no code released", reasons["T3.TeamUC.CC4"])
        self.assertIn("no configuration for this variation", reasons["T3.Teamcybermonic.stealthy_red"])

    def test_report_refuses_until_every_seed_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(SystemExit):
                R.report(Path(tmp), Path(tmp) / "REPORT.md")


class Pins(unittest.TestCase):
    def test_pins_equal_decisions(self):
        text = (HERE / "DECISIONS.md").read_text(encoding="utf-8")
        for rel, sha in fetch.SHA256.items():
            self.assertIn(sha, text, rel)
        self.assertIn("8c3c50c", text)
        self.assertEqual(fetch.REPOS["cage-challenge-4"][1][:7], "8c3c50c")
        self.assertEqual(fetch.REPOS["cage-4-submission"][1][:7], "2afd652")
        req = (HERE / "requirements_cage4.txt").read_text(encoding="utf-8").split()
        for pin in ("ray[rllib]==2.10.0", "torch_geometric==2.3.1", "numpy==1.26.4", "torch==2.2.0"):
            self.assertIn(pin, req)

    def test_clones_are_pinned_and_unchanged(self):
        if not (fetch.EXT / "cage-challenge-4").exists():
            self.skipTest("run fetch.py first")
        self.assertEqual(fetch.check(), [])


if __name__ == "__main__":
    unittest.main()
