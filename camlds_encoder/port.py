# -*- coding: utf-8 -*-
"""B2: TEMARL's encoder pipeline, ported to the CAM-LDS corpus (camlds_real) with 81 labels.

The port does NOT copy or edit the encoder code. It imports the frozen modules of
Temarl_Test_v1_L1 and changes exactly one thing: the label count, 84 -> 81. Every other line
(set embedding, Transformer/GRU/LSTM trunks, 64-D history h, BCE training, validation-best
checkpoint, patience replay, threshold rule, metrics, window construction) is the frozen code,
verified by SHA-256 below before anything runs.

Why setting NT works: each frozen module reads its module-level NT when a model is built or a
window is made (encoders_cmd: SetEmbedding, head, input check; command_data: window arrays;
train_cmd: empty-prediction shape). Setting NT in those three modules changes the label count and
nothing else. camlds_encoder/tests/test_port.py checks this.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
FROZEN_DIR = os.path.join(REPO, "Temarl_Test_v1_L1")

# SHA-256 after CRLF -> LF, recorded 2026-11-07 from commit cac1e32. A change means the encoder
# is no longer the one the thesis proposes: stop, do not bypass.
FROZEN_MODULES = {
    "encoders_cmd.py": "00e85a96a906415e0931bd1d286d1bb23163f19778f847dc91bb7a848ece77ce",
    "train_cmd.py": "86d7671339f927561a72b313173cd32159a3f52fb9921448226823c9d4ac5580",
    "metrics_cmd.py": "a2aa8aa7bb1e4225981ed9e25c4530c27fc8958528bb2d2b68e7d80dead1ccfa",
    "command_data.py": "53228fbc7f2e23838092e197d8b7be35b1cf7fe2b238b70e0bfc9b05e8f6c616",
    "_frozen.py": "ef990c02f7a734c4551077e81aec0ea67348bfdf66ec1aa5a1dba9f58d030789",
    "study_spec.py": "814604fdae7b7a0a35ea9a50bc38d9a77ca912203bc09de9e12720a8df2cba45",
}
VOCAB_PATH = os.path.join(REPO, "camlds_real", "out", "vocab.json")
VOCAB_SHA256 = "04e134e5d9b9b2d23909535e787e19732b0e43164ad72d1b2d9d0e519428f64c"   # protocol 1.1, A4


def _sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read().replace(b"\r\n", b"\n")).hexdigest()


def verify():
    bad = [f for f, h in FROZEN_MODULES.items() if _sha(os.path.join(FROZEN_DIR, f)) != h]
    if _sha(VOCAB_PATH) != VOCAB_SHA256:
        bad.append("camlds_real/out/vocab.json")
    if bad:
        raise RuntimeError(f"Frozen input changed: {bad}. Restore it; do not bypass this check.")


verify()
LABELS = json.load(open(VOCAB_PATH, encoding="utf-8"))["parent_techniques"]   # 81, sorted
NT = len(LABELS)
LABEL_ID = {t: i for i, t in enumerate(LABELS)}

if FROZEN_DIR not in sys.path:
    sys.path.insert(0, FROZEN_DIR)
import command_data as D  # noqa: E402
import encoders_cmd as Enc  # noqa: E402
import metrics_cmd as Mx  # noqa: E402
import study_spec as SPEC  # noqa: E402  frozen training protocol: seeds, patience grid, budget rule
import train_cmd as T  # noqa: E402

OLD_NT = Enc.NT                                 # 84, kept for the record
for _m in (Enc, T, D):
    _m.NT = NT
