# -*- coding: utf-8 -*-
"""The CAM-LDS encoder pipeline, pointed at CasinoLimit. No encoder code is copied or edited.

camlds_encoder/port.py imports TEMARL's frozen modules and checks their SHA-256. It then sets the
label count NT in those modules (81 for CAM-LDS). This file imports it unchanged and sets NT once
more, to CasinoLimit's 66, in the same three frozen modules and in camlds_encoder/variants.py
(which copied NT when it was imported). Nothing else changes: same layers, same 64-D h, same
optimiser, batch size, learning rate, checkpoint and threshold rules, same all-position loss.
casinolimit_encoder/tests/test_cl_port.py checks that every model and window has 66 labels.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CAMLDS_ENCODER = os.path.join(REPO, "camlds_encoder")
STEPS_PATH = os.path.join(REPO, "casinolimit_real", "out", "steps.jsonl")
VOCAB_PATH = os.path.join(REPO, "casinolimit_real", "out", "vocab.json")
# SHA-256 after CRLF -> LF, from casinolimit_real (commit d04c164). A change means the corpus is
# not the one the split was made for: stop, do not bypass.
STEPS_SHA256 = "399ef563db0223a5fe85d8668ed6fce925fbd43240f79ef7c9b0bc9cbe823c2d"


def sha_lf(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read().replace(b"\r\n", b"\n")).hexdigest()


def verify() -> None:
    if sha_lf(STEPS_PATH) != STEPS_SHA256:
        raise RuntimeError("casinolimit_real/out/steps.jsonl changed. Restore it; do not bypass this check.")


verify()
if CAMLDS_ENCODER not in sys.path:
    sys.path.insert(0, CAMLDS_ENCODER)
import port as P  # noqa: E402  (checks the frozen encoder modules)
import variants as V  # noqa: E402

with open(VOCAB_PATH, encoding="utf-8") as _fh:
    LABELS = json.load(_fh)["parent_techniques"]                                  # 66, sorted
with open(STEPS_PATH, encoding="utf-8") as _fh:
    STEPS = [json.loads(line) for line in _fh]
if LABELS != sorted({t for s in STEPS for t in s["techniques_parent"]}):
    raise RuntimeError("casinolimit_real/out/vocab.json does not match steps.jsonl.")
NT = len(LABELS)
LABEL_ID = {t: i for i, t in enumerate(LABELS)}
for _m in (P.Enc, P.T, P.D, V):
    _m.NT = NT

Enc, T, D, Mx, SPEC = P.Enc, P.T, P.D, P.Mx, P.SPEC
