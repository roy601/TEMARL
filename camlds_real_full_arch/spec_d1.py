# -*- coding: utf-8 -*-
"""Protocol D1.0 pinning: the SHA-256 (after CRLF -> LF) of every file the deception study depends on.

    python camlds_real_full_arch/spec_d1.py            # PASS or FAIL
    python camlds_real_full_arch/spec_d1.py --freeze   # once, when the user approves the protocol

`--freeze` writes SPEC_D1.json and refuses if it already exists. After that, gate_d1.py, run_d1.py
(real runs) and evaluate_d1.py refuse to run unless the check passes. A deliberate change needs a new
protocol version (D1.1) with a new spec file, never an edit of SPEC_D1.json.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
SPEC = HERE / "SPEC_D1.json"
FILES = (
    # protocol and checks
    "camlds_real_full_arch/PROTOCOL_D1.0.md",
    "camlds_real_full_arch/ZONE_GOAL_CHECK.md",
    "camlds_real_full_arch/LITERATURE_NOTES.md",
    "camlds_real_full_arch/checks/movement_check.py",
    "camlds_real_full_arch/checks/MOVEMENT_CHECK.txt",
    # study code
    "camlds_real_full_arch/env_cmd.py",
    "camlds_real_full_arch/d1_data.py",
    "camlds_real_full_arch/mappo_cmd.py",
    "camlds_real_full_arch/pipeline.py",
    "camlds_real_full_arch/gate_d1.py",
    "camlds_real_full_arch/run_d1.py",
    "camlds_real_full_arch/evaluate_d1.py",
    "camlds_real_full_arch/test_d1.py",
    "camlds_real_full_arch/spec_d1.py",
    # frozen reference policies and data
    "Temarl_Test_v1_L1/baselines_cmd.py",
    "camlds_real/out/steps.jsonl",
    "camlds_real/out/sidecar/steps_link.jsonl",
    "camlds_real/out/scan/ATTACKMATE_ALL.jsonl",
    "camlds_real/split_spec.py",
    "camlds_real/build_sidecar.py",
    # encoder side (protocol 1.2), loaded unchanged
    "camlds_encoder/port.py",
    "camlds_encoder/data.py",
    "camlds_encoder/variants.py",
)


def sha_lf(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def current() -> dict:
    return {rel: (sha_lf(REPO / rel) if (REPO / rel).exists() else "missing") for rel in FILES}


def check(verbose: bool = False) -> bool:
    if not SPEC.exists():
        print("spec_d1: NOT FROZEN (SPEC_D1.json missing): protocol D1.0 is still a draft")
        return False
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    now = current()
    bad = [rel for rel, want in spec["sha256"].items() if now.get(rel) != want]
    missing = [rel for rel in FILES if rel not in spec["sha256"]]
    if verbose:
        for rel, want in spec["sha256"].items():
            print(f"  {'ok     ' if now.get(rel) == want else 'CHANGED'} {rel}")
    ok = not bad and not missing
    print(f"spec_d1 (PROTOCOL_D1.0, frozen {spec['frozen_on']}): "
          f"{'PASS' if ok else 'FAIL: ' + ', '.join(bad + missing)}")
    return ok


def require():
    if not check():
        raise SystemExit("protocol D1.0 is not frozen or a pinned file changed: refusing to run")


def freeze(approved_on: str):
    if SPEC.exists():
        raise SystemExit("SPEC_D1.json exists: D1.0 is already frozen; a change needs protocol D1.1")
    now = current()
    if "missing" in now.values():
        raise SystemExit("cannot freeze, missing: " + ", ".join(k for k, v in now.items() if v == "missing"))
    SPEC.write_text(json.dumps({"protocol": "D1.0", "frozen_on": approved_on,
                                "written": datetime.datetime.now().isoformat(timespec="seconds"),
                                "sha256": now}, indent=1), encoding="utf-8")
    print(f"frozen: {len(now)} files -> {SPEC.name}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--freeze", metavar="APPROVED_ON", help="date the user approved the protocol")
    a = ap.parse_args()
    if a.freeze:
        freeze(a.freeze)
    sys.exit(0 if check(verbose=True) else 1)
