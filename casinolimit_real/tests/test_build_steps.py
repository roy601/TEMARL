"""Tests for casinolimit_real/build_steps.py.

    python -m unittest discover -s casinolimit_real/tests
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import build_steps as B  # noqa: E402


def row(inst, order, fe, tech, cmd, t="2024-05-18 01:00:00.000Z", doubt="False", by="auto-triggers"):
    return {"instance": inst, "order": str(order), "time": t, "first_event": fe, "machines": fe.split("-")[1],
            "technique": tech, "by": by, "doubt": doubt, "command": cmd}


class Build(unittest.TestCase):
    def test_labels_on_one_event_become_one_multi_label_step(self):
        rows = [row("a", 1, "10-start", "T1033", "id"),
                row("a", 2, "11-start", "T1046", "nmap x", "2024-05-18 01:00:05.500Z"),
                row("a", 3, "11-start", "T1595", "nmap x", "2024-05-18 01:00:05.500Z", doubt="True", by="validation1"),
                row("a", 4, "12-bastion", "T1021", "ssh y", "2024-05-18 01:01:00.000Z")]
        s = B.build(rows)
        self.assertEqual([x["techniques_parent"] for x in s], [["T1033"], ["T1046", "T1595"], ["T1021"]])
        self.assertEqual([x["exec_index"] for x in s], [0, 1, 2])
        self.assertEqual([x["machine"] for x in s], ["start", "start", "bastion"])
        self.assertEqual(s[1]["doubt"], ["T1595"])
        self.assertEqual(s[1]["labelled_by"], ["auto-triggers", "validation1"])
        self.assertEqual(s[1]["source_row"], 1)
        self.assertEqual(s[1]["start"] - s[0]["start"], 5.5)
        self.assertEqual(s[0]["techniques_sub"], s[0]["techniques_parent"])
        self.assertEqual(s[0]["start"], 1715994000.0)          # 2024-05-18 01:00:00 UTC

    def test_same_command_and_labels_again_is_a_repeat(self):
        rows = [row("a", 1, "1-start", "T1033", "id"), row("a", 2, "2-start", "T1057", "ps"),
                row("a", 3, "3-start", "T1033", "id"), row("a", 4, "4-start", "T1033", "id -u")]
        s = B.build(rows)
        self.assertEqual([(x["event_id"], x["occurrence"], x["n_occurrences"]) for x in s],
                         [(1, 1, 2), (2, 1, 1), (1, 2, 2), (3, 1, 1)])

    def test_runs_are_separate_and_sorted_by_order(self):
        rows = [row("b", 2, "2-start", "T1057", "ps"), row("a", 1, "1-start", "T1033", "id"),
                row("b", 1, "1-start", "T1033", "id")]
        s = B.build(rows)
        self.assertEqual([(x["run"], x["exec_index"], x["cmd"]) for x in s], [("a", 0, "id"), ("b", 0, "id"), ("b", 1, "ps")])
        self.assertEqual({x["base_scenario"] for x in s}, {"casinolimit"})

    def test_broken_input_is_refused(self):
        with self.assertRaises(ValueError):                       # order has a gap
            B.build([row("a", 1, "1-start", "T1033", "id"), row("a", 3, "2-start", "T1057", "ps")])
        with self.assertRaises(ValueError):                       # one event, two commands
            B.build([row("a", 1, "1-start", "T1033", "id"), row("a", 2, "1-start", "T1057", "ps")])
        with self.assertRaises(ValueError):                       # one event split by another
            B.build([row("a", 1, "1-start", "T1033", "id"), row("a", 2, "2-start", "T1057", "ps"),
                     row("a", 3, "1-start", "T1083", "id")])

    def test_measures_repeat_and_novel_points(self):
        steps = B.build([row("a", 1, "1-start", "T1033", "id"), row("a", 2, "2-start", "T1033", "whoami"),
                         row("a", 3, "3-start", "T1057", "ps"), row("a", 4, "3-start", "T1033", "ps")])
        m = B.measures(steps, w=1)
        self.assertEqual(m["prediction points (every step except a run's first)"], 2)
        self.assertEqual(m["target labels already in the 1-step window ('repeat')"], "2 of 3 (66.7%)")
        self.assertEqual(m["points with a label never seen before in the run"], "1 of 2 (50.0%)")
        self.assertEqual(m["runs with 1 step (no prediction point)"], 0)


if __name__ == "__main__":
    unittest.main()
