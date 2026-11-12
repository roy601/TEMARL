# -*- coding: utf-8 -*-
"""PROTOCOL_CL_1.0.md is frozen: the SHA-256 (after CRLF -> LF) of every file it depends on.

    python casinolimit_encoder/spec_cl.py        # PASS or FAIL

run.py (real runs) and evaluate.py refuse to run unless this passes. TEMARL's frozen encoder modules
are checked separately by camlds_encoder/port.py on every import. A FAIL means a pinned file changed:
restore it. A deliberate change needs a new protocol version (CL 1.1), never an edit of these hashes.
"""
from __future__ import annotations

import hashlib
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FROZEN_ON = "2026-11-12"
PINNED = {
    "casinolimit_encoder/PROTOCOL_CL_1.0.md": "e1488505296474a4a3c49a87257859b0823bc888cec3fe6b6cd7ac691dcb6899",
    "casinolimit_encoder/cl_port.py": "d5f821b0e0a1518e1c6e5ecea453a0deb1fbbd70891efdddb9db7c956ee15155",
    "casinolimit_encoder/cl_split.py": "aee4f5b700ad39b5d4c8449096909833cbc5217885e91e8ed72e2727f0137ba8",
    "casinolimit_encoder/cl_data.py": "5b22ec47e7d5b588f6014e86638564bb5ce7f970a501f659bd6dfe058f3965e9",
    "casinolimit_encoder/lookup.py": "de1dc463c54342b6d4f8ebcd18444a3b820fa04a0a1dbea4f08038a0b4b71918",
    "casinolimit_encoder/run.py": "6653b2fce5e9cb934f795d78a56442e1a8069e7b08f37c9a3c99d020781ff890",
    "casinolimit_encoder/evaluate.py": "1b5757530472b29cb9b77e811e17ad6ea160cb3f4aaeab8834f84f6304d36d73",
    "casinolimit_real/build_steps.py": "7e309b08f5df3eaa0c263514a034c003a4aa023a3009a09ca272c3b3144255ad",
    "casinolimit_real/out/steps.jsonl": "399ef563db0223a5fe85d8668ed6fce925fbd43240f79ef7c9b0bc9cbe823c2d",
    "casinolimit_real/out/vocab.json": "b942338a268a4f5843f31331d4327478eeb5f25f40d7da0272b6e027d59e40d3",
    "dataset_survey/casinolimit_steps.py": "00aad6c9878aec37e112f7bf8b50ea2225e6a041dbda167706279228a85d034c",
    "dataset_survey/out/casinolimit_steps/steps.csv": "ad5f329b464a58653312327af4b838da24b877ac183fd6163cd2ee6f79b23203",
    "camlds_encoder/port.py": "e1552880a051546f582705c0b2676ebae7523f49dd0e0f90a7fb3a9b622b0525",
    "camlds_encoder/variants.py": "17cfa896377243ece5d261b83fae222863cc8f85f4544b25a0f55621c9e6c75f",
}


def sha_lf(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read().replace(b"\r\n", b"\n")).hexdigest()


def check(verbose: bool = False) -> int:
    bad = []
    for rel, want in PINNED.items():
        path = os.path.join(REPO, *rel.split("/"))
        got = sha_lf(path) if os.path.exists(path) else "missing"
        if got != want:
            bad.append(rel)
        if verbose:
            print(f"  {'ok     ' if got == want else 'CHANGED'} {rel}")
    print(f"spec_cl (PROTOCOL_CL_1.0, frozen {FROZEN_ON}): {'PASS' if not bad else 'FAIL: ' + ', '.join(bad)}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(check(verbose=True))
