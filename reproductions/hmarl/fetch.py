# -*- coding: utf-8 -*-
"""H-MARL (Singh et al., RLJ 2025): clone the authors' repository and the CAGE 4 environment at pinned commits
into external/ and check every released policy file against POLICY_SHA256.txt (raw bytes).

    python reproductions/hmarl/fetch.py            # clone (once) and check
    python reproductions/hmarl/fetch.py --record   # write POLICY_SHA256.txt (done once, before any run)

Clones use core.autocrlf=false so that file bytes are those stored in the repositories. Standard library only.
"""
from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXT = HERE / "external"
REPOS = {
    "Hierarchical-MARL": ("https://github.com/adityavs14/Hierarchical-MARL.git", "6fe960f5931f2d7dc5ef522f09ca4a179f377ee4"),
    "cage-challenge-4": ("https://github.com/cage-challenge/cage-challenge-4.git", "8c3c50ca54b176c2de199847944e8dcc035497e3"),
}
# The released policies of the three methods that can be evaluated (DECISIONS 3), and the code that runs them.
POLICY_DIRS = ("h-marl-3policy/saved_policies/sub/iter_49", "h-marl-3policy/saved_policies/master/iter_49",
               "marl-1policy/models/train_marl/iter_199")
CODE_DIRS = ("h-marl-3policy/subpolicies", "h-marl-3policy/master", "marl-1policy")
MANIFEST = HERE / "POLICY_SHA256.txt"


def git(repo: Path, *args) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout.strip()


def clone():
    EXT.mkdir(parents=True, exist_ok=True)
    for name, (url, commit) in REPOS.items():
        d = EXT / name
        if not d.exists():
            subprocess.run(["git", "-c", "core.autocrlf=false", "clone", "-q", url, str(d)], check=True)
            git(d, "config", "core.autocrlf", "false")
        if git(d, "rev-parse", "HEAD") != commit:
            git(d, "checkout", "-q", commit)


def tracked_files() -> list:
    """Every file of the evaluated policies and of the code that loads and scores them (relative to the repo)."""
    root = EXT / "Hierarchical-MARL"
    out = []
    for d in POLICY_DIRS + CODE_DIRS:
        out += [p for p in sorted((root / d).rglob("*")) if p.is_file() and "__pycache__" not in p.parts
                and (d in POLICY_DIRS or p.parent == root / d)]
    return sorted({p.relative_to(root).as_posix() for p in out})


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def check() -> list:
    problems = []
    for name, (_, commit) in REPOS.items():
        d = EXT / name
        if not d.exists():
            return [f"{name} not cloned: run fetch.py"]
        if git(d, "rev-parse", "HEAD") != commit:
            problems.append(f"{name} is not at {commit[:7]}")
        if git(d, "status", "--porcelain", "--untracked-files=no"):
            problems.append(f"{name} has local changes")
    if not MANIFEST.exists():
        return problems + ["POLICY_SHA256.txt missing"]
    root = EXT / "Hierarchical-MARL"
    want = dict(line.split("  ", 1)[::-1] for line in MANIFEST.read_text(encoding="utf-8").splitlines() if line.strip())
    have = tracked_files()
    if sorted(want) != have:
        problems.append(f"file list differs from POLICY_SHA256.txt ({len(have)} vs {len(want)})")
    problems += [f"changed: {f}" for f in sorted(want) if (root / f).exists() and sha(root / f) != want[f]]
    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--record", action="store_true")
    a = ap.parse_args()
    clone()
    if a.record:
        root = EXT / "Hierarchical-MARL"
        MANIFEST.write_bytes("".join(f"{sha(root / f)}  {f}\n" for f in tracked_files()).encode("utf-8"))
        print(f"recorded {len(tracked_files())} files")
    bad = check()
    if bad:
        raise SystemExit("check FAILED:\n  " + "\n  ".join(bad))
    print(f"external/ pinned and unchanged: H-MARL {REPOS['Hierarchical-MARL'][1][:7]}, CAGE 4 "
          f"{REPOS['cage-challenge-4'][1][:7]}; {len(tracked_files())} policy and code files match POLICY_SHA256.txt")


if __name__ == "__main__":
    sys.exit(main())
