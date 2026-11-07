# -*- coding: utf-8 -*-
"""Protocol 1.1: the constants of the amendment in PROTOCOL_1.1.md. Protocol 1.0 (spec.py) stays in force.

    python idea01_kuwano/spec_1_1.py

Re-checks that the 1.0 files are untouched, that every pinned input and side file has its
recorded SHA-256, and that the 1.0 check still passes. Changing anything here after the freeze
means a new version and a new commit, never an edit in place.
"""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys

PROTOCOL_VERSION = "1.1"
AMENDS = "1.0"
PROTOCOL_DOC = "idea01_kuwano/PROTOCOL_1.1.md"
APPROVED_ON = "2026-11-07"

# ── 1.0 files: must stay byte-identical (SHA-256 after CRLF -> LF) ──────────────
FROZEN_1_0 = {
    "idea01_kuwano/PROTOCOL.md": "52a690df0f046c55d4d945efa9c1877ee4f337b236e46b4ca06084f431ba8a49",
    "idea01_kuwano/spec.py": "e35e8cb2cf4ec5ea6ba739eb75cd62effa6f313aef7825b44274e28f4ddf07a0",
    "camlds_real/split_spec.py": "ec8aeca5a5cd9fd652c3824c7f7ee9114b7877e437129a9aeb8e248389566970",
}

# ── inputs and side files of 1.1 ───────────────────────────────────────────────
PINNED = {
    "camlds_real/out/steps.jsonl": "2d0886115d8082ef9dba5d2d001cd65f241ef5a84e4c0bf16d173e71fa0bff42",
    "camlds_real/out/vocab.json": "04e134e5d9b9b2d23909535e787e19732b0e43164ad72d1b2d9d0e519428f64c",
    "camlds_real/out/sidecar/points.jsonl": "de8f7c5de71bb9ef419f786e226b1028b7fa8fc22d7d1649fb532c8d8c7b969d",
    "camlds_real/out/sidecar/steps_link.jsonl": "1353136bf41d6f02f77c012568f25988182ec3a9c36d8e9751823cc999f593fa",
}
BUILDER = "camlds_real/build_sidecar.py"

# ── A1-A7 ─────────────────────────────────────────────────────────────────────
A1_COPY = ("A test point is a COPY when the same 16-step window and the same target occur at a "
           "prediction point of a run the fold does not test (training or validation); otherwise "
           "NOVEL. Every metric is reported on all, novel and copy points.")
A2_REPEAT = ("A target label is a REPEAT when it occurs anywhere in the 16-step window, otherwise NEW. "
             "Micro-F1 is reported separately for the two groups; a predicted label is put in the "
             "group its window decides, exactly like a target label.")
A3_COLLAPSE = ("collapse_repeats keeps the first execution of each (run, event_id), i.e. occurrence == 1: "
               "883 steps. The whole pipeline (train, select, test) is rerun on it with the 1.0 rules, "
               "and reported beside the main result, never instead of it.")
A4_LABELS = ("camlds_real/out/vocab.json, key parent_techniques: 81 labels, sorted; output index = "
             "position in that list. Every model uses it.")
A5_ORDER = ("Unchanged from 1.0: ascending CSV start. Stated limitation: it differs from execution order "
            "in 4 runs (all S6), one neighbouring pair each, 4 of 870 transitions. No sensitivity run.")
A6_TIME = "No model uses timestamps, durations or time gaps. TiSASRec is not used."
A7_B1 = "42bbd2cf8409f64a1e6c8fc936c91725e8c558b2"   # CAM-LDS analysis repository; precondition B1 met

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sha(rel):
    with open(os.path.join(REPO, *rel.split("/")), "rb") as fh:
        return hashlib.sha256(fh.read().replace(b"\r\n", b"\n")).hexdigest()


def _main() -> int:
    bad = []
    print(f"PROTOCOL {PROTOCOL_VERSION} (amends {AMENDS}), approved {APPROVED_ON}")
    for group, files in (("1.0 file unchanged", FROZEN_1_0), ("pinned", PINNED)):
        for rel, want in files.items():
            ok = os.path.exists(os.path.join(REPO, *rel.split("/"))) and sha(rel) == want
            print(f"  {'ok ' if ok else 'BAD'}  {group:<19} {rel}")
            if not ok:
                bad.append(rel)
    r = subprocess.run([sys.executable, os.path.join(REPO, "idea01_kuwano", "spec.py")],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    ok10 = r.returncode == 0 and "PROTOCOL CHECK: PASS" in r.stdout
    print(f"  {'ok ' if ok10 else 'BAD'}  protocol 1.0 check   idea01_kuwano/spec.py")
    if not ok10:
        bad.append("spec.py check")
    if bad:
        print(f"\nPROTOCOL 1.1 CHECK FAILED: {', '.join(bad)}")
        return 1
    print("\nPROTOCOL 1.1 CHECK: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
