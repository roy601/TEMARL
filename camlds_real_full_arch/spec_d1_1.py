# -*- coding: utf-8 -*-
"""Protocol D1.1 pinning (PROTOCOL_D1.1.md): the SHA-256 (after CRLF -> LF) of every D1.1 file and of
D1.0's own freeze record SPEC_D1.json, which pins D1.0's 31 files. D1.0 is not changed by D1.1.

    python camlds_real_full_arch/spec_d1_1.py                       # PASS or FAIL (D1.0 checked too)
    python camlds_real_full_arch/spec_d1_1.py --freeze APPROVED_ON  # once, after the user's approval

`--freeze` writes SPEC_D1_1.json. It refuses if SPEC_D1_1.json exists, if D1.0's check fails, or if the
D1.0 main test has already been opened (results_d1/main/TEST_OPENED.json): D1.1 must be declared before
any D1.0 test number exists. The git commit at the freeze is recorded, so the order is provable.
"""
from __future__ import annotations

import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))
import spec_d1  # noqa: E402

SPEC = HERE / "SPEC_D1_1.json"
D10_MAIN_OPENED = HERE / "results_d1" / "main" / "TEST_OPENED.json"
FILES = (
    "camlds_real_full_arch/SPEC_D1.json",          # D1.0's freeze record: its 31 files stay as frozen
    "camlds_real_full_arch/PROTOCOL_D1.1.md",
    "camlds_real_full_arch/run_d1_1.py",
    "camlds_real_full_arch/evaluate_d1_1.py",
    "camlds_real_full_arch/run_all_d1_1.py",
    "camlds_real_full_arch/test_d1_1.py",
    "camlds_real_full_arch/spec_d1_1.py",
)


def current() -> dict:
    return {rel: (spec_d1.sha_lf(REPO / rel) if (REPO / rel).exists() else "missing") for rel in FILES}


def check(verbose: bool = False) -> bool:
    d10 = spec_d1.check()
    if not SPEC.exists():
        print("spec_d1_1: NOT FROZEN (SPEC_D1_1.json missing): protocol D1.1 is still a draft")
        return False
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    now = current()
    bad = [rel for rel, want in spec["sha256"].items() if now.get(rel) != want]
    missing = [rel for rel in FILES if rel not in spec["sha256"]]
    if verbose:
        for rel, want in spec["sha256"].items():
            print(f"  {'ok     ' if now.get(rel) == want else 'CHANGED'} {rel}")
    ok = d10 and not bad and not missing
    why = bad + missing + ([] if d10 else ["D1.0 spec check"])
    print(f"spec_d1_1 (PROTOCOL_D1.1, frozen {spec['frozen_on']}): {'PASS' if ok else 'FAIL: ' + ', '.join(why)}")
    return ok


def require():
    if not check():
        raise SystemExit("protocol D1.1 is not frozen, a pinned file changed, or D1.0's check fails: refusing to run")


def git_head():
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(REPO), capture_output=True, text=True, timeout=30)
        return r.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def freeze(approved_on: str):
    if SPEC.exists():
        raise SystemExit("SPEC_D1_1.json exists: D1.1 is already frozen; a change needs a new protocol version")
    if D10_MAIN_OPENED.exists():
        raise SystemExit("the D1.0 main test has been opened: D1.1 can no longer be declared before it")
    if not spec_d1.check():
        raise SystemExit("D1.0's spec check fails: D1.1 is frozen only on top of an intact D1.0")
    now = current()
    if "missing" in now.values():
        raise SystemExit("cannot freeze, missing: " + ", ".join(k for k, v in now.items() if v == "missing"))
    SPEC.write_text(json.dumps({"protocol": "D1.1", "frozen_on": approved_on,
                                "written": datetime.datetime.now().isoformat(timespec="seconds"),
                                "git_head_at_freeze": git_head(),
                                "d10_main_test_opened_at_freeze": False,
                                "sha256": now}, indent=1), encoding="utf-8")
    print(f"frozen: {len(now)} files -> {SPEC.name}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--freeze", metavar="APPROVED_ON", help="date the user approved protocol D1.1")
    a = ap.parse_args()
    if a.freeze:
        freeze(a.freeze)
    sys.exit(0 if check(verbose=True) else 1)
