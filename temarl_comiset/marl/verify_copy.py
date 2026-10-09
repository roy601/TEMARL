# -*- coding: utf-8 -*-
"""
Prove that temarl_comiset/marl/ runs the SAME experiment code as the
pre-registered CAM-LDS study (temarl_marl/ at commit 33782b1), except for the
declared differences below. Every other file must be byte-identical (line
endings normalised), so "the same thing as CAM-LDS" is verified, not asserted.

    python verify_copy.py
"""

from __future__ import annotations

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
SOURCE_COMMIT = "33782b1"

IDENTICAL = ("env_marl.py", "baselines_marl.py", "gates_marl.py",
             "calibrate_marl.py", "encoders_marl.py", "pretrain_marl.py",
             "mappo.py", "learning_gate_marl.py", "run_marl.py",
             "evaluate_marl.py", "requirements.txt")
DECLARED = {
    "_frozen.py": "one line: REPO is two levels up (the folder is one level deeper)",
    "scripts_marl.py": "REPLACED: the COMISET-grounded attacker (same interface, same estimator)",
    "tests_marl.py": "adapted: mechanics tests use a COMISET script (home zone User)",
    "prereg_marl.py": "the COMISET pre-registration (same arms, contrasts, tests, thresholds)",
}


def committed(name):
    out = subprocess.run(["git", "show", "%s:temarl_marl/%s" % (SOURCE_COMMIT, name)],
                         cwd=REPO, capture_output=True, check=True)
    return out.stdout.replace(b"\r\n", b"\n")


def local(name):
    with open(os.path.join(HERE, name), "rb") as f:
        return f.read().replace(b"\r\n", b"\n")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ok = True
    print("comparing temarl_comiset/marl/ with temarl_marl/ @ %s" % SOURCE_COMMIT)
    for name in IDENTICAL:
        same = committed(name) == local(name)
        ok &= same
        print("  %-22s %s" % (name, "identical" if same else "DIFFERS  <-- not allowed"))
    for name, why in DECLARED.items():
        same = committed(name) == local(name)
        print("  %-22s %s" % (name, "identical" if same else "declared difference: " + why))
    a = committed("_frozen.py").decode().splitlines()
    b = local("_frozen.py").decode().splitlines()
    changed = [(x, y) for x, y in zip(a, b) if x != y]
    one_line = len(a) == len(b) and len(changed) == 1 and changed[0][1].startswith("REPO =")
    ok &= one_line
    print("  _frozen.py differs in exactly the REPO line: %s" % one_line)
    print("RESULT: %s" % ("OK -- same experiment code" if ok else "FAIL"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
