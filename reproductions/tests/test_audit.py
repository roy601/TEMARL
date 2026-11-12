"""Tests for reproductions/audit.py, on a small temporary git repository.

    python -m unittest discover -s reproductions/tests
"""
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import audit as A  # noqa: E402

SOURCES = ("# Sources\n\n- Paper (authors, venue, year, DOI): X et al., J, 2020, 10.1/x\n"
           "- Version read (date, file SHA-256): 2026-11-12, abc\n- Code (URL and commit, or \"none released\"): none released\n"
           "- Data (DOI, checksum and licence, or \"none released\"): 10.5/z, md5 1, CC BY\n"
           "- Type (Reproduced / Replicated / Not reproducible; see STANDARD.md Section 1): Replicated\n"
           "- Stochastic (yes = training seeds needed, no = deterministic): no\n")
TARGETS = "id,table_or_figure,quantity,published,tolerance,primary\nT1,Table 5,recall at 3 inputs,0.61,exact,yes\nT2,Table 5,TN,170,exact,no\n"
REPORT = ("# Report\n\n| id | quantity | published | ours | difference | verdict |\n|---|---|---|---|---|---|\n"
          "| T1 | recall | 0.61 | 0.61 | 0 | MATCH |\n| T2 | TN | 170 | 169 | -1 | NO MATCH |\n")


class Audit(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = self.tmp.name
        self.root = os.path.join(self.repo, "reproductions")
        self.paper = os.path.join(self.root, "paper_x")
        os.makedirs(self.paper)
        self.git("init", "-q")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "t")
        self.git("config", "commit.gpgsign", "false")
        self.clock = 1_700_000_000

    def git(self, *args):
        self.clock = getattr(self, "clock", 1_700_000_000) + 60
        env = {**os.environ, "GIT_AUTHOR_DATE": f"{self.clock} +0000", "GIT_COMMITTER_DATE": f"{self.clock} +0000"}
        subprocess.run(["git", *args], cwd=self.repo, check=True, capture_output=True, env=env)

    def put(self, name, text):
        path = os.path.join(self.paper, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)

    def commit(self, msg):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", msg)

    def run_audit(self):
        with mock.patch("builtins.print"):
            code = A.main(self.root)
        return code, open(os.path.join(self.root, "AUDIT.txt"), encoding="utf-8").read()

    def prepared(self):
        for name, text in (("SOURCES.md", SOURCES), ("TARGETS.csv", TARGETS), ("DECISIONS.md", "# Decisions\n\n| 1 | gap | choice | why | 2026-11-12 |\n"),
                           ("AUTHOR_CONTACT.md", "# Log\n\n| 2026-11-12 | a@b | gap 1 | no reply after 14 days |\n")):
            self.put(name, text)
        self.commit("targets and decisions")

    def test_before_any_result_it_waits(self):
        self.prepared()
        code, text = self.run_audit()
        self.assertEqual(code, 0)
        self.assertIn("paper_x: NOT RUN YET", text)
        self.assertIn("TARGETS.csv: 2 targets, 1 primary", text)

    def test_a_correct_reproduction_passes(self):
        self.prepared()
        self.put("out/results.json", "{}")
        self.put("REPORT.md", REPORT)
        self.commit("results")
        code, text = self.run_audit()
        self.assertEqual(code, 0, text)
        self.assertIn("paper_x: PASS", text)
        self.assertIn("ORDER: no target changed after the first result", text)
        self.assertIn("MATCH 1, CLOSE 0, NO MATCH 1, NOT ATTEMPTED 0", text)

    def test_targets_written_after_the_result_fail(self):
        self.put("SOURCES.md", SOURCES)
        self.put("AUTHOR_CONTACT.md", "x\n")
        self.put("out/results.json", "{}")
        self.commit("results first")
        self.put("TARGETS.csv", TARGETS)
        self.put("DECISIONS.md", "x\n")
        self.put("REPORT.md", REPORT)
        self.commit("targets later")
        code, text = self.run_audit()
        self.assertEqual(code, 1)
        self.assertIn("ORDER: TARGETS.csv was not committed before the first result", text)
        self.assertIn("ORDER: DECISIONS.md was not committed before the first result", text)

    def test_a_target_changed_or_added_after_the_result_fails(self):
        self.prepared()
        self.put("out/results.json", "{}")
        self.commit("results")
        self.put("TARGETS.csv", TARGETS.replace("170", "169") + "T3,Table 6,x,1,exact,no\n")
        self.put("REPORT.md", REPORT + "| T3 | x | 1 | 1 | 0 | MATCH |\n")
        self.commit("edited targets")
        code, text = self.run_audit()
        self.assertEqual(code, 1)
        self.assertIn("targets added, removed or changed after the first result: T3, T2", text)

    def test_missing_report_rows_wrong_verdicts_and_empty_sources_fail(self):
        self.prepared()
        self.put("SOURCES.md", SOURCES.replace(": Replicated", ":"))
        self.put("out/results.json", "{}")
        self.put("REPORT.md", REPORT.replace("| T2 | TN | 170 | 169 | -1 | NO MATCH |\n", "").replace("MATCH |", "GOOD |"))
        self.commit("results")
        code, text = self.run_audit()
        self.assertEqual(code, 1)
        self.assertIn("SOURCES.md fields not filled: Type", text)
        self.assertIn("REPORT.md: no row for targets T2", text)
        self.assertIn("REPORT.md: verdict not in the fixed list for T1", text)

    def test_template_and_helper_folders_are_skipped(self):
        os.makedirs(os.path.join(self.root, "TEMPLATE"))
        os.makedirs(os.path.join(self.root, "out"))
        self.prepared()
        _, text = self.run_audit()
        self.assertNotIn("TEMPLATE", text)

    def test_source_values_ignores_the_colon_inside_the_hint(self):
        v = A.source_values("- Type (a: b; c): Replicated\n- Paper (x):\n")
        self.assertEqual(v, {"Type": "Replicated", "Paper": ""})


if __name__ == "__main__":
    unittest.main()
