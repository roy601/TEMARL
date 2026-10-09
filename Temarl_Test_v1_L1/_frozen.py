# -*- coding: utf-8 -*-
"""
Temarl_Test_v1_L1 -- frozen inputs, verified before anything runs
==================================================================
This study reuses, unmodified, the D3FEND payoff matrix, the 84-technique
vocabulary, the zone topology and the device helper from `thesis_system/
temarl_v2/`. They are vendored into this folder so the bundle is portable.

This module puts that directory on `sys.path` and verifies every reused file
is byte-identical (modulo line endings) to the version this study was designed
against. If any check fails the study refuses to run: a frozen input changing
underneath an experiment is exactly the silent confound this project exists to
rule out, so the failure is loud and must be resolved by a human.

Line endings are normalised (CRLF -> LF) before hashing: git on Windows may
check files out with CRLF while the GPU machine uses LF. Content is frozen,
not line endings.

No absolute path appears here; everything resolves relative to this file.

What is DELIBERATELY NOT imported
---------------------------------
`profiles_v5` and the Markov chain estimator. This study has no Markov
component: no chain fitting, no smoothing, no synthetic sequence generation,
no generated episodes. Attacker behaviour comes only from replaying recorded
playbooks. `profiles_v5.py` is vendored and hashed for provenance (it is part
of the frozen v2 set) but importing it from study code is a bug.
"""

from __future__ import annotations

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
V2_DIR = os.path.join(HERE, "thesis_system", "temarl_v2")
DATA_DIR = os.path.join(HERE, "thesis_system", "data")

if V2_DIR not in sys.path:
    sys.path.insert(0, V2_DIR)

# sha256 of each frozen file, CRLF normalised to LF, recorded 2026-10-09.
# camlds_commands.json is produced by parse_commands.py from the AttackBed
# repository; its hash pins the exact corpus this study was designed against.
FROZEN_SHA256 = {
    "thesis_system/data/camlds_commands.json":
        "96ab3280f55774b3288f230bad98f5d519b5835e89d4e59432763f3dd4b4d1ed",
    "thesis_system/data/camlds_grounding_verified.json":
        "20006361c0e6b6a46d9da02e67606cdaa0c3e375a4a0c7396c24484d1b88d7be",
    "thesis_system/data/camlds_grounding.json":
        "e8b7bbc110ade5f2e5ac92ad913940263355f2c042f1022c4880bdaf160ff569",
    "thesis_system/temarl_v2/payoff_frozen.json":
        "854ebf25a123e5b471e9571aa2789c5b94d1457b054f2f93acb564232d508f97",
    "thesis_system/temarl_v2/d3fend_payoff.py":
        "ca85718fb88107338d9bf522e947a84b57ef03b437c7b6796df1cfae6621597d",
    "thesis_system/temarl_v2/vocab_v2.py":
        "b57d0e1b21153cfd24ba48969b3a3af071d747b68aaa3218f7a8c7cb60d740d0",
    "thesis_system/temarl_v2/env_v2.py":
        "af9e9d61b67e8564e028faa5b94bad2c06f0a0c393260922ed5b60b184e961fe",
    "thesis_system/temarl_v2/encoders.py":
        "f0c0603229a8b4a0ca170670bb9234c7b1e5796d0358d8ec8ae759f8f690a374",
    "thesis_system/temarl_v2/encoders_rope.py":
        "8a9f036948eb182a3b67bf4ff30479b0b6105e0466e3e913f1ee5b07643be9f2",
    "thesis_system/temarl_v2/policy.py":
        "b77aa6fa5be82373e55084ae79181b07ab03677508974df72cb6d297128f4c57",
    "thesis_system/temarl_v2/device_util.py":
        "e6c867784e9f3c87b3975424055225e23b6d85d262129c1a7eaa526f13f73c1a",
    "thesis_system/temarl_v2/profiles_v5.py":
        "1b0dab40c2545a8b63305f61485666c14244ae2e39ccd1584e84b8befa379fd8",
}

COMMANDS_PATH = os.path.join(DATA_DIR, "camlds_commands.json")


def normalised_sha256(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()


def verify(strict: bool = True) -> dict:
    """Hash every frozen input. Raises RuntimeError on any mismatch."""
    report, bad = {}, []
    for rel, expected in sorted(FROZEN_SHA256.items()):
        path = os.path.join(HERE, rel)
        if not os.path.exists(path):
            report[rel] = "MISSING"
            bad.append(f"{rel}: file missing")
            continue
        actual = normalised_sha256(path)
        ok = actual == expected
        report[rel] = "ok" if ok else f"CHANGED {actual[:16]}..."
        if not ok:
            bad.append(f"{rel}:\n    expected {expected}\n    actual   {actual}")
    if bad and strict:
        raise RuntimeError(
            "Frozen input verification FAILED. This study was designed against "
            "specific inputs; one of them changed.\n\n" + "\n".join(bad) +
            "\n\nDo not bypass this. Either restore the file, or start a new "
            "study folder and record the new hashes deliberately."
        )
    return report


verify()
