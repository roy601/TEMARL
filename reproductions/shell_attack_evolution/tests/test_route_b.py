"""Tests for route B's own code (not the authors' scripts).

    python -m unittest discover -s reproductions/shell_attack_evolution/tests
"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import run_route_b as B  # noqa: E402

ONE = '''"""doc"""
import os
import pandas as pd
from primary_process import PrimaryProcessing
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
RAW_ROOT = os.path.join(DATA_DIR, "cowrie")

# The block below reads the cowrie logs by directory; because it takes too long,
# def read_dataset():
#     x = 1
#
#     return x
# merged_df = read_dataset()
# port_filterd.to_csv(os.path.join(DATA_DIR, "port_filterd.csv"))
merged_df = pd.read_csv("port_filterd.csv")
'''


class StepZero(unittest.TestCase):
    def test_the_commented_block_is_uncommented_exactly(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "01_extract_sessions.py"), "w", encoding="utf-8") as fh:
                fh.write(ONE)
            src = B.step00_source(d)
        self.assertIn("import pandas as pd\nfrom primary_process import PrimaryProcessing\nDATA_DIR =", src)
        self.assertIn("def read_dataset():\n    x = 1\n\n    return x\nmerged_df = read_dataset()\n", src)
        self.assertTrue(src.rstrip().endswith('port_filterd.to_csv(os.path.join(DATA_DIR, "port_filterd.csv"))'))
        self.assertNotIn("pd.read_csv", src)                           # code after the block is not taken
        compile(src, "step00", "exec")


class Scoring(unittest.TestCase):
    def test_periods_and_route_b_rules(self):
        S = [{"session_id": "a", "commands": ["uname"], "command_count": 1, "session_pattern": "x",
              "attack_techniques": ["T1082"]}]
        M = {"sessions": B.R.session_measures(S), "techniques": B.R.technique_measures(S),
             "commands": B.R.command_measures([{"command": "uname", "frequency": 3, "command_pattern": None}])}
        targets = [
            {"id": "T1.attacks.2024", "quantity": "q", "published": "3914173", "tolerance": "exact (route B)", "primary": "no"},
            {"id": "T1.attacks.2021_2022", "quantity": "q", "published": "1", "tolerance": "exact (route B)", "primary": "no"},
            {"id": "S4B.ubuntu_share.2024", "quantity": "q", "published": "48.44", "tolerance": "+-0.01 (route B)", "primary": "no"},
            {"id": "T7.T1082.2024", "quantity": "q", "published": "100", "tolerance": "+-0.001", "primary": "yes"},
        ]
        rows = {r["id"]: r for r in B.score(targets, M, 3914173, {"T1082": 99.0})}
        self.assertEqual(rows["T1.attacks.2024"]["verdict"], "MATCH")
        self.assertEqual(rows["T1.attacks.2021_2022"]["verdict"], "NOT ATTEMPTED")
        self.assertIn("DECISIONS.md 18", rows["T1.attacks.2021_2022"]["note"])
        self.assertEqual(rows["S4B.ubuntu_share.2024"]["verdict"], "NOT ATTEMPTED")
        self.assertEqual(rows["T7.T1082.2024"]["verdict"], "MATCH")
        self.assertEqual(rows["T7.T1082.2024"]["alternates"]["authors_07b"], 99.0)

    def test_complex_test_is_the_one_07a_uses(self):
        self.assertTrue(B.COMPLEX.search("cat /proc/cpuinfo | grep name"))
        self.assertFalse(B.COMPLEX.search("uname -a"))


if __name__ == "__main__":
    unittest.main()
