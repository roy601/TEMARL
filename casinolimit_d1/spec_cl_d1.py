# -*- coding: utf-8 -*-
"""Protocol CL-D1.0 pinning: the SHA-256 (after CRLF -> LF) of every file the CasinoLimit deception study
depends on, plus one digest over CL 1.0's 200 committed checkpoint records.

    python casinolimit_d1/spec_cl_d1.py                         # PASS or FAIL
    python casinolimit_d1/spec_cl_d1.py --freeze APPROVED_ON    # once, after the user's approval

`--freeze` writes SPEC_CL_D1.json and refuses if it exists or if D1.0's spec check fails (the
environment, learner and reference policies are D1.0's frozen files). The gate, the runner and the
scorer refuse to run unless the check passes. A change after the freeze needs a new protocol version.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
SPEC = HERE / "SPEC_CL_D1.json"
D10_SPEC = REPO / "camlds_real_full_arch" / "SPEC_D1.json"
FILES = (
    # this protocol
    "casinolimit_d1/PROTOCOL_CL_D1.0.md",
    "casinolimit_d1/cl_world.py",
    "casinolimit_d1/gate_cl.py",
    "casinolimit_d1/run_cl.py",
    "casinolimit_d1/evaluate_cl.py",
    "casinolimit_d1/run_all_cl.py",
    "casinolimit_d1/spec_cl_d1.py",
    "casinolimit_d1/test_cl_d1.py",
    "casinolimit_d1/attack_v15_1_tactics.json",
    "casinolimit_d1/checks/attack_extract.py",
    # D1.0's freeze record: pins env_cmd.py, mappo_cmd.py, baselines_cmd.py, evaluate_d1.py and more
    "camlds_real_full_arch/SPEC_D1.json",
    # statistics reused from D1.0 (also pinned in SPEC_D1.json)
    "camlds_real_full_arch/evaluate_d1.py",
    # frozen payoff rule and vocabulary
    "Temarl_Test_v1_L1/thesis_system/temarl_v2/d3fend_payoff.py",
    "Temarl_Test_v1_L1/thesis_system/temarl_v2/vocab_v2.py",
    # CasinoLimit data and the CL 1.0 encoder side
    "casinolimit_real/out/steps.jsonl",
    "casinolimit_real/out/vocab.json",
    "casinolimit_encoder/cl_port.py",
    "casinolimit_encoder/cl_data.py",
    "casinolimit_encoder/cl_split.py",
    "casinolimit_encoder/PROTOCOL_CL_1.0.md",
    "camlds_encoder/port.py",
    "camlds_encoder/variants.py",
    # the earlier exploratory run, disclosed (Section 2a)
    "casinolimit_real_full_arch/results/main/README_NOT_PROTOCOL.md",
)
RECORDS = "casinolimit_encoder/out/train/main"          # CL 1.0: one result.json per arm, fold and seed


def sha_lf(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def records_digest() -> str:
    """One SHA-256 over 'relative path:sha' of every CL 1.0 checkpoint record, sorted."""
    paths = sorted((REPO / RECORDS).glob("*/*/s*/result.json"))
    lines = [f"{p.relative_to(REPO).as_posix()}:{sha_lf(p)}" for p in paths]
    return hashlib.sha256(("\n".join(lines) + f"\n{len(lines)}").encode("utf-8")).hexdigest() if lines else "missing"


def current() -> dict:
    out = {rel: (sha_lf(REPO / rel) if (REPO / rel).exists() else "missing") for rel in FILES}
    out[RECORDS + " (CL 1.0 records, digest)"] = records_digest()
    return out


def _d10_ok() -> bool:
    sys.path.insert(0, str(REPO / "camlds_real_full_arch"))
    import spec_d1
    return spec_d1.check()


def check(verbose: bool = False) -> bool:
    d10 = _d10_ok()
    if not SPEC.exists():
        print("spec_cl_d1: NOT FROZEN (SPEC_CL_D1.json missing): protocol CL-D1.0 is still a draft")
        return False
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    now = current()
    bad = [rel for rel, want in spec["sha256"].items() if now.get(rel) != want]
    missing = [rel for rel in now if rel not in spec["sha256"]]
    if verbose:
        for rel, want in spec["sha256"].items():
            print(f"  {'ok     ' if now.get(rel) == want else 'CHANGED'} {rel}")
    ok = d10 and not bad and not missing
    why = bad + missing + ([] if d10 else ["D1.0 spec check"])
    print(f"spec_cl_d1 (PROTOCOL_CL_D1.0, frozen {spec['frozen_on']}): {'PASS' if ok else 'FAIL: ' + ', '.join(why)}")
    return ok


def require():
    if not check():
        raise SystemExit("protocol CL-D1.0 is not frozen, a pinned file changed, or D1.0's check fails: refusing to run")


def git_head():
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(REPO), capture_output=True, text=True, timeout=30)
        return r.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def freeze(approved_on: str):
    if SPEC.exists():
        raise SystemExit("SPEC_CL_D1.json exists: CL-D1.0 is already frozen; a change needs a new version")
    if not _d10_ok():
        raise SystemExit("D1.0's spec check fails: CL-D1.0 reuses D1.0's frozen files")
    now = current()
    if "missing" in now.values():
        raise SystemExit("cannot freeze, missing: " + ", ".join(k for k, v in now.items() if v == "missing"))
    SPEC.write_text(json.dumps({"protocol": "CL-D1.0", "frozen_on": approved_on,
                                "written": datetime.datetime.now().isoformat(timespec="seconds"),
                                "git_head_at_freeze": git_head(), "sha256": now}, indent=1), encoding="utf-8")
    print(f"frozen: {len(now)} entries -> {SPEC.name}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--freeze", metavar="APPROVED_ON", help="date the user approved protocol CL-D1.0")
    a = ap.parse_args()
    if a.freeze:
        freeze(a.freeze)
    sys.exit(0 if check(verbose=True) else 1)
