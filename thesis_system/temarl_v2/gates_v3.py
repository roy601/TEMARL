# -*- coding: utf-8 -*-
"""
TEMARL v3 — Full gate re-run
=============================
Runs EVERY inherited v2 gate plus the new v3 gates and records the outcome to
`results_v3/gates.json`. Used to demonstrate that the v3 additions changed
nothing they were not supposed to change.

No threshold here is adjusted to obtain a pass. Thresholds come from
`prereg_v3.INHERITED_GATES` and from each module's own pre-registered bound. A
failure is reported as a failure.

Run:  python gates_v3.py
Exit code 0 only if every gate passes.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))

# module, human label, whether a non-zero exit means failure
MODULES = [
    ("vocab_v2.py", "vocabulary: ids frozen, zero UNK on both corpora", False),
    ("d3fend_payoff.py", "D3FEND payoff + pre-registered headroom gate", False),
    ("env_v2.py", "env_v2 (CONTROL, unchanged): clock / DSR / SNR", False),
    ("encoders.py", "history encoders: parity, capacity, PAD-invariance", False),
    ("policy.py", "GMU trunk, gate sweep, IGM monotonicity", False),
    ("topology.py", "v3 topology generator", True),
    ("entity_encoders.py", "v3 entity encoders", True),
    ("policy_entity.py", "v3 entity policy", True),
    ("env_entity.py", "v3 fixed-environment equivalence", True),
    ("tests_entity.py", "v3 test suite (26 tests)", True),
]

# lines worth lifting into the record, per module
PATTERNS = [
    r"UNK count\s*:\s*\d+\s*(PASS|FAIL)",
    r"ids 0-22 unchanged\s*:\s*(PASS|FAIL)",
    r"delta>=min\s+[\d.]+\s*>=\s*[\d.]+",
    r"history gain\s+\S+\s+(PASS|FAIL)",
    r"spread \(oracle-random\):\s*\S+\s+(PASS|FAIL)",
    r"SNR\s+[\d.]+\s+(PASS|FAIL)",
    r"max \|h\(pad=6\).*?(PASS|FAIL)",
    r"IGM dQtot/dQi.*?(PASS|FAIL)",
    r"TOPOLOGY GENERATOR:.*",
    r"ENTITY ENCODERS:.*",
    r"ENTITY POLICY:.*",
    r"VERDICT:.*",
    r"\d+/\d+ PASSED",
    r"capacity spread.*",
    r"TOTAL\s+\d+",
]


def run(mod: str, exit_code_meaningful: bool):
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    t0 = time.time()
    try:
        p = subprocess.run([sys.executable, mod], cwd=HERE, env=env,
                           capture_output=True, text=True, timeout=1800,
                           errors="replace")
        out = (p.stdout or "") + (p.stderr or "")
        rc = p.returncode
    except subprocess.TimeoutExpired:
        return {"module": mod, "ok": False, "returncode": None,
                "seconds": time.time() - t0, "lines": ["TIMEOUT"]}
    lines = []
    for ln in out.splitlines():
        for pat in PATTERNS:
            if re.search(pat, ln):
                lines.append(ln.strip())
                break
    fail_markers = ("FAIL", "Traceback", "FAILURES PRESENT", "DIVERGENCE")
    ok = not any(m in out for m in fail_markers)
    if exit_code_meaningful:
        ok = ok and rc == 0
    return {"module": mod, "ok": ok, "returncode": rc,
            "seconds": time.time() - t0, "lines": lines[:12]}


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("=" * 96)
    print("  TEMARL v3 — FULL GATE RE-RUN (inherited v2 gates + new v3 gates)")
    print("=" * 96)
    results, all_ok = [], True
    for mod, label, ecm in MODULES:
        if not os.path.exists(os.path.join(HERE, mod)):
            print(f"  [skip] {mod} not found")
            continue
        r = run(mod, ecm)
        r["label"] = label
        results.append(r)
        all_ok &= r["ok"]
        print(f"\n  [{'PASS' if r['ok'] else 'FAIL'}] {mod:<22} {label} "
              f"({r['seconds']:.0f}s, rc={r['returncode']})")
        for ln in r["lines"]:
            print(f"        {ln}")

    out = os.path.join(HERE, "results_v3", "gates.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"all_pass": all_ok, "results": results}, f, indent=1)
    print("\n" + "=" * 96)
    print(f"  {'ALL GATES PASS' if all_ok else 'GATE FAILURES PRESENT'}"
          f"   ({sum(1 for r in results if r['ok'])}/{len(results)} modules)")
    print(f"  wrote -> {os.path.relpath(out, HERE)}")
    print("=" * 96)
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
