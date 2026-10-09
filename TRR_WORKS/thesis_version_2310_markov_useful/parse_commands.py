# -*- coding: utf-8 -*-
"""Command-level re-parse of the AttackBed playbooks.

The verified corpus (camlds_grounding_verified.json) is FLAT: a command whose
`metadata.techniques` lists n codes becomes n consecutive tokens. That
flattening manufactures bigrams that are only metadata-string order, never
observed attacker transitions. This module recovers the COMMAND BOUNDARIES that
the flat file lost, so within-command label order can be separated from real
between-command transitions.

Same source and same regexes as thesis_system/temarl_v2/parse_attackbed.py
(one `metadata:` block == one AttackMate command). Read-only.
"""
import os
import re
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
RUN_DIR = os.path.join(HERE, "..", "..", "attackbed", "ansible", "run")

KEY_RE = re.compile(r'^\s*(techniques|tactics?|technique_name)\s*:\s*(.*)$')
META_RE = re.compile(r'^(\s*)metadata\s*:\s*$')
CMD_RE = re.compile(r'^\s*-\s+type\s*:\s*(.*)$')
CODE_RE = re.compile(r'T\d{4}(?:\.\d{3})?')


def _value(raw):
    raw = raw.strip()
    if raw[:1] in ('"', "'"):
        q = raw[0]
        end = raw.find(q, 1)
        return raw[1:end] if end > 0 else raw[1:]
    return raw.split("#", 1)[0].strip()


def parse_commands(path):
    """Return [{'type', 'techniques':[code], 'tactics':[tactic]}] per command."""
    out, block, meta_indent, ctype = [], None, None, ""

    def flush(b, t):
        if not b or not b.get("techniques"):
            return
        codes = CODE_RE.findall(b["techniques"])
        tactics = [x.strip() for x in b.get("tactics", "").split(",") if x.strip()]
        # Same positional-with-first-fallback rule as the upstream parser.
        labels = [tactics[i] if i < len(tactics) else (tactics[0] if tactics else "")
                  for i in range(len(codes))]
        out.append({"type": t, "techniques": codes, "tactics": labels})

    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            indent = len(line) - len(line.lstrip())
            m = META_RE.match(line)
            if m:
                flush(block, ctype)
                block, meta_indent = {}, len(m.group(1))
                continue
            m = CMD_RE.match(line)
            if m:
                flush(block, ctype)
                block, meta_indent = None, None
                ctype = _value(m.group(1))
                continue
            if block is not None and meta_indent is not None and indent <= meta_indent:
                flush(block, ctype)
                block, meta_indent = None, None
            if block is None:
                continue
            m = KEY_RE.match(line)
            if m:
                key = "tactics" if m.group(1).startswith("tactic") else m.group(1)
                block[key] = _value(m.group(2))
    flush(block, ctype)
    return out


def collect_commands():
    """{playbook_filename: [command, ...]}, with the scenario_5 duplicate dropped."""
    runs = OrderedDict()
    for root, _, files in os.walk(RUN_DIR):
        for fn in sorted(files):
            if not re.match(r"scenario_\d+.*\.j2", fn):
                continue
            cmds = parse_commands(os.path.join(root, fn))
            if cmds:
                runs[fn] = cmds
    # scenario_5.j2.yml is the same playbook as scenario_5.j2 (comments only).
    for fn in [k for k in runs if k.endswith(".j2.yml")]:
        stem = fn[:-4]
        if stem in runs and _flat(runs[stem]) == _flat(runs[fn]):
            del runs[fn]
    return runs


def _flat(cmds):
    return [c for cmd in cmds for c in cmd["techniques"]]


flat = _flat
