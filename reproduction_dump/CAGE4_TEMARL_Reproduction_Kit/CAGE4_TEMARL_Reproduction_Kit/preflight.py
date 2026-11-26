#!/usr/bin/env python3
"""Check dependencies, upstream revision pinning and essential checkpoints."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
SOURCES = json.loads((ROOT / "sources.json").read_text(encoding="utf-8"))["repos"]


def check():
    errors = []
    warnings = []
    print("Python:", sys.version.split()[0])
    if sys.version_info[:2] != (3, 11):
        warnings.append("Python 3.11 is recommended and expected by setup scripts")
    for name, spec in SOURCES.items():
        d = ROOT / spec["path"]
        if not (d / ".git").exists():
            errors.append(f"{name}: upstream source missing (run bootstrap.py)")
            continue
        try:
            rev = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=d, text=True, stderr=subprocess.DEVNULL).strip()
            if rev != spec["commit"]:
                errors.append(f"{name}: commit mismatch {rev}, expected {spec['commit']}")
            else:
                print(f"OK {name}: {rev[:12]}")
        except Exception as exc:
            errors.append(f"{name}: cannot inspect git revision ({exc})")
    d = ROOT / "external" / "cybermonic" / "weights"
    for i in range(5):
        w = d / f"gnn_ppo-{i}.pt"
        if not w.is_file() or w.stat().st_size < 100000:
            errors.append(f"Missing or suspicious Cybermonic checkpoint: {w}")
    modules = ["torch", "torch_geometric", "ray", "gymnasium", "CybORG", "numpy"]
    for name in modules:
        if importlib.util.find_spec(name) is None:
            errors.append(f"Module missing: {name}")
    if not errors:
        print("PASS: source/checkpoint/import preflight. Runtime evaluation still unverified.")
    for w in warnings: print("WARNING:", w)
    for e in errors: print("ERROR:", e)
    return not errors

if __name__ == "__main__":
    sys.exit(0 if check() else 2)
