# -*- coding: utf-8 -*-
"""CAGE 4 reproduction: fetch the released repositories at their pinned commits (DECISIONS.md 2, 7, 15).

    python reproductions/cage4/fetch.py

Clones into reproductions/cage4/external/ (not committed), checks out the pinned commits, and checks the
SHA-256 of the released weights and code against DECISIONS.md. Safe to run again: existing clones are
only checked.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXT = HERE / "external"
REPOS = {
    "cage-challenge-4": ("https://github.com/cage-challenge/cage-challenge-4.git",
                         "8c3c50ca54b176c2de199847944e8dcc035497e3"),
    "cage-4-submission": ("https://github.com/cybermonic/cage-4-submission.git",
                          "2afd652d80ce9d4051a07c23c2538f3dec6bb6c6"),
    "cage-4-submissions-punch": ("https://github.com/PUNCH-Cyber/cage-4-submissions.git",   # DECISIONS 15
                                 "9cc4ff83d600b0c810dad2ec428e35c0f3a0b6b0"),
}
SHA256 = {   # DECISIONS.md, decision 7
    "cage-4-submission/weights/gnn_ppo-0.pt": "991d96cb5132eec36595f6d407e67b93b2e5045c960dc4d25586e0c0bf124e60",
    "cage-4-submission/weights/gnn_ppo-1.pt": "27072ef12bab1e1b2ec9b9143845d07af7545c615c92ef44c59b67268cb98502",
    "cage-4-submission/weights/gnn_ppo-2.pt": "a76ea99d830976aa4c7f370c1fc575746de7c8a1618dd239ff34f0525da11478",
    "cage-4-submission/weights/gnn_ppo-3.pt": "acca6460545401e47c1dfe30d9f761f4955437b9c13f8098d5856e7995163fe4",
    "cage-4-submission/weights/gnn_ppo-4.pt": "ea9c664085987f4c191b74f2d4ffa44453461990d0c8cc1c1525ec4d8f7372d2",
    "cage-4-submission/submission.py": "e4ded7b8d60093892f5abb3544a4b48bcc19042a993a6c297722578302709570",
    "cage-4-submission/models/cage4.py": "922949d38d856c5a995976ddb889fc0e88eadef0dac1cedb5d941c2825df4751",
    "cage-4-submission/wrapper/graph_wrapper.py": "1ec7529a6cf1dad63f25e625d4444287821128dbdf072a51ff7c48290d82062f",
    "cage-challenge-4/CybORG/Evaluation/evaluation.py": "8c01f269c25a6f8e61916524321aca2ecf5c1b572f6568cc71eb18f89a7ce28d",
    "cage-4-submissions-punch/punch_analyse_restore_v1/submission.py": "06d0ec52e8e2e36efe0f433da395697eb43e36a79909267d2673f5bb59fd8c56",
    "cage-4-submissions-punch/punch_analyse_restore_v1/punchagents.py": "9b170f8950498c622b1037be753ff52c461a47f0a25835115ebcaf1f49e0754e",
    "cage-4-submissions-punch/punch_analyse_restore_v1/punchwrappers.py": "9caf35eabd35fe1803c0f7ae8c59ee905aa8381dcdfe2c0e9d51713f1325a209",
}


def git(cwd, *args) -> str:
    r = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed in {cwd}: {r.stderr.strip()}")
    return r.stdout.strip()


def sha_raw(path: Path) -> str:
    """SHA-256 of the raw bytes. The clones are made with core.autocrlf=false, so text files keep the
    repository's LF endings; the weight files are binary and must never be line-ending converted."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check() -> list:
    """Problems with the clones (empty list = all pinned and unchanged)."""
    bad = []
    for name, (_, commit) in REPOS.items():
        d = EXT / name
        if not (d / ".git").exists():
            bad.append(f"{name}: not cloned")
            continue
        if git(d, "rev-parse", "HEAD") != commit:
            bad.append(f"{name}: not at the pinned commit {commit[:8]}")
        if git(d, "status", "--porcelain"):
            bad.append(f"{name}: local changes")
    for rel, want in SHA256.items():
        p = EXT / rel
        if not p.exists() or sha_raw(p) != want:
            bad.append(f"{rel}: missing or SHA-256 differs")
    return bad


def main():
    EXT.mkdir(parents=True, exist_ok=True)
    for name, (url, commit) in REPOS.items():
        d = EXT / name
        if not (d / ".git").exists():
            print(f"cloning {url}")
            subprocess.run(["git", "-c", "core.autocrlf=false", "clone", "-q", url, str(d)], check=True)
            git(d, "config", "core.autocrlf", "false")
        git(d, "-c", "advice.detachedHead=false", "checkout", "-q", commit)
        print(f"{name}: {git(d, 'rev-parse', 'HEAD')}")
    bad = check()
    if bad:
        print("FAIL:\n  " + "\n  ".join(bad))
        sys.exit(1)
    print(f"OK: all {len(REPOS)} repositories at their pinned commits; {len(SHA256)} released files match DECISIONS.md")


if __name__ == "__main__":
    main()
