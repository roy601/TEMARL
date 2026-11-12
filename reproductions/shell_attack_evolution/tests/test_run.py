"""Tests for the Shell Attack Evolution reproduction, on small made-up sessions (no real data).

    python -m unittest discover -s reproductions/shell_attack_evolution/tests
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import run as R  # noqa: E402

S = [
    {"session_id": "a", "commands": ["uname", "w", "id"], "command_count": 3, "session_pattern": ["uname", "w", "id"],
     "attack_techniques": ["T1082 System Information Discovery", "T1033", "T1082"]},
    {"session_id": "b", "commands": ["uname", "w", "id"], "command_count": 3, "session_pattern": ["uname", "w", "id"],
     "attack_techniques": ["T1082", "T1070"]},
    {"session_id": "c", "commands": ["cd ~ ; chattr -ia .ssh"], "command_count": 1, "session_pattern": ["cd ; chattr"],
     "attack_techniques": ["T1222", "T1070", "not an id"]},
]


class Definitions(unittest.TestCase):
    def test_ids_are_read_as_written(self):
        self.assertEqual(R.tech_ids(S[0]), ["T1082", "T1033", "T1082"])
        self.assertEqual(R.tech_ids({"attack_techniques": ["T1059.004 x", "T1655"]}), ["T1059.004", "T1655"])

    def test_session_measures(self):
        m = R.session_measures(S)
        self.assertEqual(m["session_counts"], 3)
        self.assertAlmostEqual(m["avg_session_length"], 7 / 3)
        self.assertEqual(m["session_kinds"], 2)                       # two distinct command lists
        self.assertAlmostEqual(m["avg_length_per_kind"], 2.0)          # (3 + 1) / 2
        self.assertEqual(m["n_session_patterns"], 2)
        self.assertEqual(m["session_pattern_row__info_patterns_shared_by_2plus"], 1)
        self.assertEqual(m["command_count_equals_len_commands"], 3)

    def test_technique_shares_primary_and_alternates(self):
        t = R.technique_measures(S)
        # presence: T1082 2 sessions, T1033 1, T1070 2, T1222 1 -> total 6
        self.assertAlmostEqual(t["technique_share"]["T1082"], 100 * 2 / 6)
        # occurrence: T1082 3, T1033 1, T1070 2, T1222 1 -> total 7
        self.assertAlmostEqual(t["technique_share__alt_occurrence"]["T1082"], 100 * 3 / 7)
        # command-weighted presence: T1082 3+3, T1033 3, T1070 3+1, T1222 1 -> total 14
        self.assertAlmostEqual(t["technique_share__alt_command_weighted"]["T1070"], 100 * 4 / 14)
        self.assertAlmostEqual(t["technique_share__alt_presence_over_sessions"]["T1070"], 100 * 2 / 3)
        self.assertEqual(t["n_techniques"], 4)
        self.assertEqual(t["entries_without_an_id"], 1)

    def test_tactics_follow_table_vi_and_count_once_per_session(self):
        t = R.technique_measures(S)
        # session a: Discovery, Execution? no. a: T1082, T1033 -> Discovery. b: T1082, T1070 -> Discovery, Defense Evasion.
        # c: T1222, T1070 -> Defense Evasion.  presences: Discovery 2, Defense Evasion 2 -> 50 / 50
        self.assertAlmostEqual(t["tactic_share"]["Discovery"], 50.0)
        self.assertAlmostEqual(t["tactic_share"]["Defense Evasion"], 50.0)
        self.assertAlmostEqual(t["tactic_share__alt_sum_of_technique_shares"]["Discovery"], 100 * 3 / 6)

    def test_ordered_pairs(self):
        t = R.technique_measures(S)
        # pairs: a: 1082->1033, 1033->1082 ; b: 1082->1070 ; c: 1222->1070  -> 4 pairs
        self.assertAlmostEqual(t["pair_share"]["T1082->T1033"], 25.0)
        self.assertEqual(t["pair_rank"]["T1033->T1082"], 1)                 # ties broken by name
        self.assertNotIn("T1033->T1082", {p for p, _ in t["top10_pairs"][1:]})

    def test_discovery_std_uses_the_ten_table_vi_techniques(self):
        t = R.technique_measures(S)
        vals = [t["technique_share"].get(x, 0.0) / 100 for x in R.DISCOVERY]
        self.assertEqual(len(R.DISCOVERY), 10)
        self.assertAlmostEqual(t["discovery_std"], R.statistics.pstdev(vals))

    def test_most_frequent_command(self):
        c = R.command_measures([{"command": "w", "frequency": 5, "command_pattern": "w"},
                                {"command": "uname", "frequency": 9, "command_pattern": "uname"},
                                {"command": "uname -a", "frequency": 7, "command_pattern": "uname"}])
        self.assertEqual((c["rank1_command"], c["rank1_command__alt_pattern"]), ("uname", "uname"))


class Verdicts(unittest.TestCase):
    def test_fixed_rules(self):
        self.assertEqual(R.verdict("12.65", 12.655, "+-0.01")[0], "MATCH")
        self.assertEqual(R.verdict("12.65", 12.668, "+-0.01")[0], "CLOSE")
        self.assertEqual(R.verdict("12.65", 12.7, "+-0.01")[0], "NO MATCH")
        self.assertEqual(R.verdict("5365", 5365, "exact")[0], "MATCH")
        self.assertEqual(R.verdict("5365", 5364, "exact")[0], "NO MATCH")
        self.assertEqual(R.verdict("41.43", 41.4, "+-0.01 (route B)")[0], "NOT ATTEMPTED")
        self.assertEqual(R.verdict("144", None, "exact")[0], "NOT ATTEMPTED")
        self.assertEqual(R.verdict("cd ~ ; chattr -ia .ssh", "cd ~;chattr -ia .ssh", "exact text, spaces around ; ignored")[0], "MATCH")

    def test_every_target_id_is_understood(self):
        import csv
        with open(os.path.join(R.HERE, "TARGETS.csv"), encoding="utf-8") as fh:
            targets = list(csv.DictReader(fh))
        M = {p: {"sessions": R.session_measures(S), "techniques": R.technique_measures(S),
                 "commands": R.command_measures([{"command": "uname", "frequency": 1, "command_pattern": "uname"}])}
             for p in R.PERIODS}
        for r in targets:
            R.ours_for(r["id"], r["quantity"], M)                    # raises on an unknown id
        self.assertEqual(len(targets), 116)

    def test_paper_internal_checks_use_published_values_only(self):
        import csv
        with open(os.path.join(R.HERE, "TARGETS.csv"), encoding="utf-8") as fh:
            checks = R.paper_internal_checks(list(csv.DictReader(fh)))
        self.assertEqual(checks["techniques_with_nonzero_share_in_table_vii.2021_2022"], 22)
        self.assertEqual(checks["techniques_with_nonzero_share_in_table_vii.2024"], 27)


if __name__ == "__main__":
    unittest.main()
