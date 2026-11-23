#!/usr/bin/env python3
"""Fetch pinned upstream sources and optionally install their requirements.
No external code is changed or silently patched. Requires Git and Internet.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
SOURCES = json.loads((ROOT / "sources.json").read_text(encoding="utf-8"))["repos"]


def run(*args, cwd=None):
    print("+", " ".join(map(str, args)), flush=True)
    subprocess.run([str(x) for x in args], cwd=cwd, check=True)


def revision(path):
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=path, text=True).strip()


def fetch_sources():
    for name, spec in SOURCES.items():
        path = ROOT / spec["path"]
        if not (path / ".git").is_dir():
            if path.exists() and any(path.iterdir()):
                raise SystemExit(f"Refusing to overwrite non-repo directory: {path}")
            path.parent.mkdir(parents=True, exist_ok=True)
            run("git", "clone", spec["url"], str(path))
        if revision(path) != spec["commit"]:
            run("git", "fetch", "origin", spec["commit"], cwd=path)
            run("git", "checkout", "--detach", spec["commit"], cwd=path)
        if revision(path) != spec["commit"]:
            raise RuntimeError(f"Incorrect revision for {name}")
    (ROOT / "results").mkdir(exist_ok=True)
    provenance = {
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "python": sys.version,
        "sources": {name: {"commit": revision(ROOT / s["path"]), "url": s["url"]} for name, s in SOURCES.items()},
    }
    (ROOT / "results" / "source_provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    print("PINNED SOURCE REVISIONS VERIFIED.")


def install_deps():
    if sys.version_info[:2] != (3, 11):
        raise SystemExit("Use Python 3.11 for upstream CAGE 4/PyTorch/Ray compatibility. Found " + sys.version.split()[0])
    if sys.prefix == sys.base_prefix:
        raise SystemExit("Activate a dedicated Python 3.11 virtual environment first. Refusing to install into a global interpreter.")
    cage = ROOT / "external" / "cage"
    cyber = ROOT / "external" / "cybermonic"
    run(sys.executable, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel")
    # Install CAGE's official dependencies, then Cybermonic's pinned dependencies.
    # There is an upstream torch_geometric 2.5.0/2.3.1 version conflict; we expose it
    # in README and leave exact original requirements unmodified.
    run(sys.executable, "-m", "pip", "install", "-r", str(cage / "Requirements.txt"))
    run(sys.executable, "-m", "pip", "install", "-r", str(cyber / "requirements.txt"))
    run(sys.executable, "-m", "pip", "install", "--no-deps", "-e", str(cage))
    print("Dependency installation commands finished. Run preflight.py to identify incompatibilities.")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--install", action="store_true", help="Install original third-party dependencies into the active Python 3.11 venv")
    p.add_argument("--sources-only", action="store_true", help="Explicitly fetch/verify pinned sources (default)")
    a = p.parse_args()
    fetch_sources()
    if a.install:
        install_deps()

if __name__ == "__main__":
    main()
