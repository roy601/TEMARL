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
        centre = {"Teamcybermonic": -193.0, "Teampunch": -142.0}
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            for team, c in centre.items():
                for s in R.SEEDS:                                 # seed means spread evenly around the target
                    eps = [{"episode": i, "score": c + ((i % 2) * 2 - 1) * 5 + (s - 4.5) * 0.8, "steps": 499,
                            "seconds": 1.0} for i in range(100)]
                    R.seed_file(team, s, out).write_text(json.dumps({"team": team, "seed": s, "n": 100, "episodes": eps}),
                                                         encoding="utf-8")
            res = R.report(out, out / "REPORT.md")
            text = (out / "REPORT.md").read_text(encoding="utf-8")
        v = {r["id"]: r["verdict"] for r in res["targets"]}
        self.assertEqual(v["T3.Teamcybermonic.CC4"], "MATCH")
        self.assertEqual(v["T3.Teampunch.CC4"], "MATCH")
        self.assertEqual(sum(x == "NOT ATTEMPTED" for x in v.values()), 22)
        self.assertEqual(len(v), 24)
        self.assertIn("Paper verdict: reproduced for the two teams that released code", text)
        for tid in v:
            self.assertIn(f"| {tid} |", text)
        reasons = {r["id"]: r.get("reason") for r in res["targets"]}
        self.assertIn("no code released", reasons["T3.TeamUC.CC4"])
        self.assertIn("no code released", reasons["T3.Teamlancer.CC4"])
        self.assertIn("no configuration for this variation", reasons["T3.Teamcybermonic.stealthy_red"])
        self.assertIn("no configuration for this variation", reasons["T3.Teampunch.aggressive_red"])

    def test_report_writes_checklist_limits_and_hashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            for team, c in {"Teamcybermonic": -193.0, "Teampunch": -150.0}.items():
                for s in R.SEEDS:
                    eps = [{"episode": i, "score": c + ((i % 2) * 2 - 1) * 5 + (s - 4.5) * 0.8, "steps": 499,
                            "seconds": 1.0} for i in range(100)]
                    R.seed_file(team, s, out).write_text(json.dumps({"team": team, "seed": s, "n": 100, "episodes": eps}),
                                                         encoding="utf-8")
            R.report(out, out / "REPORT.md")
            text = (out / "REPORT.md").read_text(encoding="utf-8")
            hashes = (out / "HASHES.txt").read_text(encoding="utf-8").splitlines()
            listed = {line.split("  ")[1] for line in hashes}
            self.assertEqual(R.sha_lf(out / "results.json"),
                             next(line.split("  ")[0] for line in hashes if line.endswith("  results.json")))
        self.assertIn("## Checklist (STANDARD.md, Section 2)", text)
        for i in range(1, 11):
            self.assertIn(f"\n| {i} | ", text)
        self.assertIn("**second machine not yet**", text)                     # no recheck file in this folder
        self.assertIn("Teampunch is CLOSE, not reproduced", text)             # -150 vs -142: CLOSE
        self.assertIn("ONE released trained policy", text)
        self.assertIn("Rechecks, the first episodes of a kept seed run again (`out/RECHECK_*.json`): none yet.", text)
        self.assertIn("results.json", listed)
        self.assertIn("episodes_Teampunch_seed9.json", listed)
        self.assertNotIn("HASHES.txt", listed)

    def test_report_refuses_until_every_seed_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(SystemExit):
                R.report(Path(tmp), Path(tmp) / "REPORT.md")


class Standard(unittest.TestCase):
    def test_hashes_do_not_depend_on_line_endings(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            (Path(a) / "logs").mkdir()
            (Path(b) / "logs").mkdir()
            (Path(a) / "x.json").write_bytes(b'{\r\n "s": 1\r\n}')            # a Windows checkout
            (Path(b) / "x.json").write_bytes(b'{\n "s": 1\n}')                # as git stores it
            (Path(a) / "logs" / "y.log").write_bytes(b"done\r\n")
            (Path(b) / "logs" / "y.log").write_bytes(b"done\n")
            ha, hb = R.write_hashes(Path(a)), R.write_hashes(Path(b))
            self.assertEqual(ha, hb)
            self.assertEqual(list(ha), ["logs/y.log", "x.json"])
            self.assertEqual(R.write_hashes(Path(a)), ha)                      # HASHES.txt never lists itself

    def recheck(self, out, machine, team, identical):
        R.write_json(out / f"RECHECK_{machine}_{team}_seed0.json",
                     {"machine": machine, "team": team, "seed": 0, "episodes": 3, "kept": [], "again": [],
                      "identical": identical})

    def test_second_machine_row_follows_the_recheck_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            self.recheck(out, "DEV", "Teampunch", True)
            row = [r for r in R.checklist(R.rechecks(out), "DEV", False) if r.startswith("| 5 |")][0]
            self.assertEqual(row.count("**second machine not yet**"), 2)       # the same machine does not count
            self.recheck(out, "PC2", "Teampunch", True)
            self.recheck(out, "PC2", "Teamcybermonic", True)
            row = [r for r in R.checklist(R.rechecks(out), "DEV", False) if r.startswith("| 5 |")][0]
            self.assertEqual(row.count("identical on a second machine (PC2)"), 2)
            self.assertIn("no training seeds", row)                            # stays "partly" (DECISIONS 10)
            self.assertTrue(row.split(" | ")[2].startswith("partly"))
            self.recheck(out, "PC3", "Teampunch", False)
            row = [r for r in R.checklist(R.rechecks(out), "DEV", False) if r.startswith("| 5 |")][0]
            self.assertIn("**no**: a recheck gave DIFFERENT scores (Teampunch seed 0 on PC3)", row)

    def test_authors_row_follows_the_contact_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "AUTHOR_CONTACT.md"
            p.write_text("| (draft, not sent) | organisers | variations | - |", encoding="utf-8")
            self.assertFalse(R.authors_asked(p))
            p.write_text("| 2026-11-26 | organisers | variations | no reply after 0 days |", encoding="utf-8")
            self.assertTrue(R.authors_asked(p))
        self.assertIn("| 3 | authors asked about every gap | yes |", "\n".join(R.checklist([], "DEV", True)))
        self.assertIn("**not yet**", "\n".join(R.checklist([], "DEV", False)))


class Pins(unittest.TestCase):
    def test_pins_equal_decisions(self):
        text = (HERE / "DECISIONS.md").read_text(encoding="utf-8")
        for rel, sha in fetch.SHA256.items():
            self.assertIn(sha, text, rel)
        self.assertIn("8c3c50c", text)
        self.assertEqual(fetch.REPOS["cage-challenge-4"][1][:7], "8c3c50c")
        self.assertEqual(fetch.REPOS["cage-4-submission"][1][:7], "2afd652")
        self.assertEqual(fetch.REPOS["cage-4-submissions-punch"][1][:7], "9cc4ff8")
        self.assertEqual(set(R.TEAMS), {"Teamcybermonic", "Teampunch"})
        self.assertIn("| 15 | **Correction of decision 6", text)
        req = (HERE / "requirements_cage4.txt").read_text(encoding="utf-8").split()
        for pin in ("ray[rllib]==2.10.0", "torch_geometric==2.3.1", "numpy==1.26.4", "torch==2.2.0"):
            self.assertIn(pin, req)

    def test_clones_are_pinned_and_unchanged(self):
        if not (fetch.EXT / "cage-challenge-4").exists():
            self.skipTest("run fetch.py first")
        self.assertEqual(fetch.check(), [])


if __name__ == "__main__":
    unittest.main()
