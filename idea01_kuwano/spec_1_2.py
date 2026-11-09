# -*- coding: utf-8 -*-
"""Protocol 1.2: the constants and fingerprints of PROTOCOL_1.2.md. Protocols 1.0 and 1.1 stay in force.

    python idea01_kuwano/spec_1_2.py

Checks that every earlier protocol file, the final design's code and every sealed test output is
unchanged, and that the 1.1 and 1.0 checks still pass. The test is opened only if this passes.
Changing anything here after the freeze means a new version and a new commit, never an edit in place.
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import os
import subprocess
import sys

PROTOCOL_VERSION = "1.2"
AMENDS = ("1.0", "1.1")
PROTOCOL_DOC = "idea01_kuwano/PROTOCOL_1.2.md"
APPROVED_ON = "2026-11-09"

FINAL_ENCODER = "allpos"
SECONDARY_ENCODERS = ("gru_allpos", "lstm_allpos")        # never replace the Transformer
DESCRIPTIVE_ONLY = "baseline"                             # main condition, cannot change the design
NEVER_OPENED = ("causal", "repeat", "asl", "asl_long")
COLLAPSE_ENCODERS = ("allpos", "gru_allpos", "lstm_allpos")
PATIENCE_CHECKS = 16
UPDATE_LIMIT = {"main allpos": 9152, "main gru_allpos": 18304, "main lstm_allpos": 18304, "collapse_repeats": 18304}
OPENING = ("Stage 1: our encoders, main and collapse_repeats together, once, by evaluate_test.py",
           "Stage 2: the comparison with Kuwano, by protocol 1.0 Section 7")
TRANSFORMER_VS_RNN = ("Family of two on the main condition, variant held out: per-fold Transformer minus GRU or "
                      "LSTM micro-F1, 95% bootstrap CI, two-sided Wilcoxon, Holm. Otherwise: no difference shown.")
SCIPY_VERSION = "1.17.1"

# -- files that must stay byte-identical (SHA-256 after CRLF -> LF) ------------------------
FROZEN_EARLIER = {
    "idea01_kuwano/PROTOCOL.md":
        "52a690df0f046c55d4d945efa9c1877ee4f337b236e46b4ca06084f431ba8a49",
    "idea01_kuwano/spec.py":
        "e35e8cb2cf4ec5ea6ba739eb75cd62effa6f313aef7825b44274e28f4ddf07a0",
    "camlds_real/split_spec.py":
        "ec8aeca5a5cd9fd652c3824c7f7ee9114b7877e437129a9aeb8e248389566970",
    "idea01_kuwano/PROTOCOL_1.1.md":
        "b76ca4e757b78d986ec372667cdeb917340304b89f01c60344d4dc75f3aea9b3",
    "idea01_kuwano/spec_1_1.py":
        "ec08e0eea88e5b49842fa8fd6a09fe2d8b111c7dd5d6496afe404183ddca8c85",
}

PINNED = {
    "idea01_kuwano/PROTOCOL_1.2.md":
        "a88b9ed2369db6c76fa80de395f7750dfa4e1ceccea5678601cb09f66f960822",
    "camlds_encoder/SELECTION_RULE.md":
        "1721cf6f7128c436585121f65a6a7c2d3728e8a4e7c65077d5a9ff81830244a5",
    "camlds_encoder/port.py":
        "e1552880a051546f582705c0b2676ebae7523f49dd0e0f90a7fb3a9b622b0525",
    "camlds_encoder/data.py":
        "66aa83134388bccef2f7635b268920534775d05d095ae9dd6c7606ff3f0a2e3b",
    "camlds_encoder/run.py":
        "2b465853eb7992a82382e1d645e5aaa803e40ea6c3a9d64dbc4aa4bba36f6fe3",
    "camlds_encoder/variants.py":
        "17cfa896377243ece5d261b83fae222863cc8f85f4544b25a0f55621c9e6c75f",
    "camlds_encoder/run_variants.py":
        "723fe150e479eea5b8198728a84591b6a923a9e23dd612cba5b4fd6a4d79f323",
    "camlds_encoder/evaluate_test.py":
        "2ca9dbfa2695c61f10d8984025ed4b04edacda4aa7d0e9c668da0e9f7ff986c8",
    "camlds_real/build_sidecar.py":
        "bc71f66a13123e1bca1b9e20c2bc9642cf8c70a5b89729965d2ddddfdb94ae14",
    "camlds_encoder/out/budget.json":
        "bea9634454d48f8d870962f6a865d36fdcee663beea9874608aae31ce099ce1e",
}

KUWANO_SEALED = {
    "idea01_kuwano/sealed/predictions.jsonl":
        "65f309988b61de24e1e3fe74f92079fe4edbbbe7fc2c7bd596b0b64ebfca1ccb",
}

# -- sealed test outputs, main condition: SHA-256 over "fold/seed sha" lines, 320 per design --
SEALED_TEST_OUTPUTS = {
    "baseline": ("camlds_encoder/out/train/main/Transformer",
        "8e927654d0f1820e4d4ffe4f791aa9410187ccbb0b3f4654bdd56a22f2e0e383"),
    "causal": ("camlds_encoder/out/variants/causal",
        "38313a24395ea2f74dab5acd05168bb5feed36bce82231b35ba288ae0c1cdc72"),
    "allpos": ("camlds_encoder/out/variants/allpos",
        "7476066146877cdb2d4723ffafa5ac50ca00b0f1fcc478932cfed2f6d3a9c444"),
    "repeat": ("camlds_encoder/out/variants/repeat",
        "dd3c2cc815acc0900e1f51097c7e582f059862b7563253f5f645c2a27087b561"),
    "asl": ("camlds_encoder/out/variants/asl",
        "c12d9ad1a6c6b9df9cd721a34015a554bbbd19b5f0f65c7f488e8218a56ab06f"),
    "asl_long": ("camlds_encoder/out/variants/asl_long",
        "2a2fd7420d7a5fae8b0c8e513d6d2f7dcb0edbd56e020039548c1b12e49380bc"),
    "gru_allpos": ("camlds_encoder/out/variants/gru_allpos",
        "90e33f698ee326b711995fc60c746a3e41a440f46c00df51994bfec2f5f4cea6"),
    "lstm_allpos": ("camlds_encoder/out/variants/lstm_allpos",
        "de206949a16ba7a3afd4455bdd2a08e5a31e33b6c9e021e2fa5d87d4d5b7011d"),
}

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sha(rel):
    with open(os.path.join(REPO, *rel.split("/")), "rb") as fh:
        return hashlib.sha256(fh.read().replace(b"\r\n", b"\n")).hexdigest()


def sealed_fingerprint(root):
    """Combined fingerprint of a design's 320 test outputs. None if any is missing."""
    base = os.path.join(REPO, *root.split("/"))
    lines = []
    for fold in sorted(os.listdir(base)):
        for seed in sorted(os.listdir(os.path.join(base, fold))):
            path = os.path.join(base, fold, seed, "test_logits.npy")
            if not os.path.exists(path):
                return None
            with open(path, "rb") as fh:
                lines.append(f"{fold}/{seed} {hashlib.sha256(fh.read()).hexdigest()}")
    return hashlib.sha256("\n".join(lines).encode()).hexdigest() if len(lines) == 320 else None


def _main() -> int:
    bad = []
    print(f"PROTOCOL {PROTOCOL_VERSION} (amends {', '.join(AMENDS)}), approved {APPROVED_ON}")
    for group, files in (("earlier file", FROZEN_EARLIER), ("pinned", PINNED), ("Kuwano sealed", KUWANO_SEALED)):
        for rel, want in files.items():
            ok = os.path.exists(os.path.join(REPO, *rel.split("/"))) and sha(rel) == want
            print(f"  {'ok ' if ok else 'BAD'}  {group:<14} {rel}")
            if not ok:
                bad.append(rel)
    for design, (root, want) in SEALED_TEST_OUTPUTS.items():
        ok = os.path.isdir(os.path.join(REPO, *root.split("/"))) and sealed_fingerprint(root) == want
        print(f"  {'ok ' if ok else 'BAD'}  sealed outputs {design} (320)")
        if not ok:
            bad.append(f"sealed {design}")
    try:
        have = importlib.metadata.version("scipy")
    except importlib.metadata.PackageNotFoundError:
        have = "not installed"
    ok = have == SCIPY_VERSION
    print(f"  {'ok ' if ok else 'BAD'}  scipy          {have}")
    if not ok:
        bad.append("scipy version")
    r = subprocess.run([sys.executable, os.path.join(REPO, "idea01_kuwano", "spec_1_1.py")],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    ok = r.returncode == 0 and "PROTOCOL 1.1 CHECK: PASS" in r.stdout
    print(f"  {'ok ' if ok else 'BAD'}  protocol 1.1 and 1.0 checks")
    if not ok:
        bad.append("spec_1_1.py check")
    if bad:
        print(f"\nPROTOCOL 1.2 CHECK FAILED: {', '.join(bad)}")
        return 1
    print("\nPROTOCOL 1.2 CHECK: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
