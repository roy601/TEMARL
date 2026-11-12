"""Tests for casinolimit_steps.py on a small made-up CasinoLimit.

    python -m unittest discover -s dataset_survey/tests
"""
import csv
import io
import json
import os
import sys
import tempfile
import unittest
import zipfile
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import casinolimit_steps as C  # noqa: E402


def hexs(s):
    return s.encode().replace(b" ", b"\x00").hex().upper()


def audit(ts, serial, cmd):
    return (f'type=SYSCALL msg=audit({ts}:{serial}): arch=c000003e syscall=59 success=yes exe="/usr/bin/x" uid=0\n'
            f'type=EXECVE msg=audit({ts}:{serial}): argc=2 a0="ls" a1="-la"\n'
            f'type=PROCTITLE msg=audit({ts}:{serial}): proctitle={hexs(cmd)}\n')


class Steps(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        d = os.path.join(self.tmp.name, "data")
        os.makedirs(d)
        labels = {
            "a": {"id": "a", "technique": "T1046: Network Service Discovery", "event_uids": ["11-start"],
                  "instance_name": "alpha", "doubt": False, "labelled_by": [["auto-triggers", "x"]], "rejected_by": []},
            "b": {"id": "b", "technique": "T1021: Remote Services", "event_uids": ["5-bastion", "6-bastion"],
                  "instance_name": "alpha", "doubt": True, "labelled_by": [["validation1", "x"]], "rejected_by": []},
            "c": {"id": "c", "technique": "T1046: Network Service Discovery", "event_uids": ["12-start"],
                  "instance_name": "alpha", "doubt": False, "labelled_by": [["auto-triggers", "x"]], "rejected_by": []},
            "d": {"id": "d", "technique": "T1083: File and Directory Discovery", "event_uids": ["999-start"],
                  "instance_name": "alpha", "doubt": False, "labelled_by": [["auto-triggers", "x"]], "rejected_by": []},
        }
        with zipfile.ZipFile(os.path.join(d, "output.zip"), "w") as z:
            z.writestr("output/system_labels/alpha.json", json.dumps(labels))
            z.writestr("output/steps.csv", "instance,step_count,step_0\nalpha,2,x\nbeta,0,N/A\n")
        with zipfile.ZipFile(os.path.join(d, "syslogs.zip"), "w") as z:
            z.writestr("syslogs/alpha/start-3/audit.log",
                       audit("100.000", 11, "nmap -sV 10.0.0.0/24") + audit("300.500", 12, "nmap 10.0.0.5")
                       + "a line without an event id\n")
            z.writestr("syslogs/alpha/bastion.casinolimit.bzh/audit.log",
                       audit("200.250", 5, "ssh user@bastion") + audit("200.300", 6, "id"))
            z.writestr("syslogs/alpha/start-3/syslog", "not an audit log\n")
        self.data, self.out = d, os.path.join(self.tmp.name, "out")

    def run_script(self):
        with mock.patch.object(sys, "argv", ["x", "--data-dir", self.data, "--out", self.out]), \
                mock.patch("builtins.print"):
            self.assertEqual(C.main(), 0)
        return json.load(open(os.path.join(self.out, "report.json"), encoding="utf-8"))

    def test_steps_are_ordered_by_time_with_machine_command_and_repeats(self):
        r = self.run_script()
        rows = list(csv.DictReader(open(os.path.join(self.out, "steps.csv"), encoding="utf-8")))
        self.assertEqual([x["technique"] for x in rows], ["T1046", "T1021", "T1046"])
        self.assertEqual([x["machines"] for x in rows], ["start", "bastion", "start"])
        self.assertEqual(rows[0]["command"], "nmap -sV 10.0.0.0/24")
        self.assertEqual(rows[1]["command"], "ssh user@bastion")
        self.assertEqual([x["seen_before"] for x in rows], ["False", "False", "True"])
        self.assertEqual(rows[1]["by"], "validation1")
        self.assertEqual(rows[1]["doubt"], "True")
        self.assertTrue(rows[0]["time"].startswith("1970-01-01 00:01:40.000"))
        inst = r["instances"][0]
        self.assertEqual((inst["steps"], inst["machines"], inst["machine_switches"], inst["machine_path"]),
                         (3, 2, 2, "start>bastion>start"))
        self.assertEqual((inst["repeat_of_earlier"], inst["same_as_previous"]), (1, 0))
        self.assertEqual((inst["commands"], inst["commands_with_a_new_technique"]), (3, 2))

    def test_labels_on_the_same_event_are_one_command(self):
        with zipfile.ZipFile(os.path.join(self.data, "output.zip")) as z:
            lab = json.loads(z.read("output/system_labels/alpha.json"))
        lab["e"] = {**lab["a"], "id": "e", "technique": "T1595: Active Scanning"}
        with zipfile.ZipFile(os.path.join(self.data, "output.zip"), "w") as z:
            z.writestr("output/system_labels/alpha.json", json.dumps(lab))
            z.writestr("output/steps.csv", "instance,step_count\nalpha,2\n")
        inst = self.run_script()["instances"][0]
        self.assertEqual((inst["steps"], inst["commands"], inst["commands_with_a_new_technique"]), (4, 3, 2))
        with open(os.path.join(self.out, "REPORT.txt"), encoding="utf-8") as fh:
            self.assertIn("labels per command: 1: 2, 2: 1", fh.read())

    def test_missing_events_and_instances_without_labels_are_reported(self):
        r = self.run_script()
        self.assertEqual(r["totals"]["labels"], 4)
        self.assertEqual(r["totals"]["labels with no event found"], 1)
        self.assertEqual(r["totals"]["events found"], 4)
        self.assertEqual(r["scan"]["audit lines without an event id"], 1)
        self.assertEqual(r["instances_without_labels"], ["beta"])
        self.assertTrue(any("T1083" in p for p in r["problems"]))
        text = open(os.path.join(self.out, "REPORT.txt"), encoding="utf-8").read()
        self.assertIn("labels placed 3 of 4", text)

    def test_hex_and_plain_values_are_decoded(self):
        self.assertEqual(C.decode_hex(hexs("cat /etc/passwd").encode()), "cat /etc/passwd")
        self.assertEqual(C.decode_hex(b'"/usr/bin/id"'), "/usr/bin/id")
        self.assertEqual(C.machine_of("meetingcam-12"), "meet")
        self.assertIsNone(C.machine_of("unknown-1"))


if __name__ == "__main__":
    unittest.main()
