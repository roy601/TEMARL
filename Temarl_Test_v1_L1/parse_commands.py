# -*- coding: utf-8 -*-
"""
Temarl_Test_v1_L1 -- command-level parse of the AttackBed playbooks
===================================================================
Builds `thesis_system/data/camlds_commands.json`: one record per *attacker
command*, each carrying the UNORDERED set of ATT&CK technique labels the
playbook annotates it with.

Why this exists
---------------
The earlier corpus (`camlds_grounding_verified.json`) is a FLAT token stream:
a command annotated `techniques: "T1087,T1083,T1201"` became three consecutive
"steps". Measured on this corpus, 458 of 1311 transitions (34.9%) were
transitions *inside* one command, i.e. an artefact of the order somebody typed
labels into a metadata string, not observed execution order. One command
(linpeas) carries 13 labels and produced 12 such transitions, 18 times over.

This parser keeps the command boundary. Label order inside a command is
explicitly discarded downstream (sets, not sequences); only the order of
commands -- which the playbook really does execute top to bottom -- is kept.

Provenance
----------
Source: AttackBed AttackMate playbooks, github.com/ait-testbed/attackbed
        (GPL-3.0), `ansible/run/scenario<N>/templates/scenario_<N>*.j2`.
Dataset paper: CAM-LDS, Landauer et al., arXiv:2603.04186v1.

The playbooks are Jinja2 templates with unrendered `{{...}}`, so a YAML parser
fails on them; we scan line-wise, exactly as the original
`parse_attackbed.py` did. The metadata-block state machine below is taken from
that audited parser unchanged, so the flattened token stream it implies stays
byte-identical to the verified corpus -- `verify_against_verified()` asserts
precisely that. The only addition is that command boundaries are retained.

This script is a BUILD STEP, not part of the experiment runtime. Run it once;
the committed JSON is what the study loads. Re-running it on the same AttackBed
checkout must reproduce the same file.

Usage
-----
    python parse_commands.py --attackbed <path to attackbed repo>
    python parse_commands.py --attackbed ../attackbed --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter, OrderedDict, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(HERE, "thesis_system", "data", "camlds_commands.json")
VERIFIED_PATH = os.path.join(HERE, "thesis_system", "data",
                             "camlds_grounding_verified.json")

# ── the audited state machine from parse_attackbed.py, unchanged ────────────
KEY_RE = re.compile(r'^\s*(techniques|tactics?|technique_name)\s*:\s*(.*)$')
META_RE = re.compile(r'^(\s*)metadata\s*:\s*$')
CMD_RE = re.compile(r'^\s*-\s+type\s*:\s*(.*)$')
CMDLINE_RE = re.compile(r'^\s*cmd\s*:\s*(.*)$')
CODE_RE = re.compile(r'T\d{4}(?:\.\d{3})?')
# Jinja2 control flow. Presence means the rendered run may differ from the
# static command list; the audit records it rather than attempting to render.
JINJA_CTRL_RE = re.compile(r'\{%-?\s*(for|if|elif|else|endfor|endif|while)\b')


def _value(raw: str) -> str:
    """Extract a metadata value, tolerating an inline `#` comment.

    Quoted values take exactly the quoted span; unquoted values stop at the
    first `#`. Several playbooks put a comment after a quoted value, which an
    anchored regex silently dropped in an earlier revision.
    """
    raw = raw.strip()
    if raw[:1] in ('"', "'"):
        q = raw[0]
        end = raw.find(q, 1)
        return raw[1:end] if end > 0 else raw[1:]
    return raw.split("#", 1)[0].strip()


def parse_playbook(path: str) -> dict:
    """Return the ordered command records of one playbook.

    A record is emitted for every `- type:` entry that owns a `metadata:` block
    containing `techniques:`. Commands with no technique annotation are counted
    (`n_unlabelled`) but not emitted: they carry no ATT&CK signal, and
    inventing a label for them would be fabrication.
    """
    commands = []
    n_unlabelled = 0
    n_total_cmds = 0
    jinja_ctrl = 0

    block = None          # metadata keys of the block being read
    meta_indent = None
    cur_type = None       # the `- type:` this block belongs to
    cur_cmd = None        # its `cmd:` line, for human-readable audit
    cur_labelled = False

    def flush():
        """Close the open metadata block, emitting a command if annotated."""
        nonlocal block, meta_indent, cur_labelled
        if block and block.get("techniques"):
            codes = CODE_RE.findall(block["techniques"])
            if codes:
                tactics = [t.strip() for t in block.get("tactics", "").split(",")
                           if t.strip()]
                commands.append({
                    "techniques": codes,          # ORDER HERE IS NOT MEANINGFUL
                    "tactics": tactics,
                    "type": cur_type,
                    "cmd": (cur_cmd or "")[:200],
                })
                cur_labelled = True
        block, meta_indent = None, None

    def close_command():
        nonlocal n_unlabelled, cur_labelled
        if cur_type is not None and not cur_labelled:
            n_unlabelled += 1
        cur_labelled = False

    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            if JINJA_CTRL_RE.search(line):
                jinja_ctrl += 1
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            indent = len(line) - len(line.lstrip())

            m = META_RE.match(line)
            if m:
                flush()
                block, meta_indent = {}, len(m.group(1))
                continue

            m = CMD_RE.match(line)
            if m:
                flush()
                close_command()
                cur_type = _value(m.group(1)) or None
                cur_cmd = None
                n_total_cmds += 1
                continue

            # A line dedented to or past the `metadata:` key ends the block.
            if block is not None and meta_indent is not None and indent <= meta_indent:
                flush()

            if block is None:
                m = CMDLINE_RE.match(line)
                if m and cur_type is not None:
                    cur_cmd = _value(m.group(1))
                continue

            m = KEY_RE.match(line)
            if m:
                key = "tactics" if m.group(1).startswith("tactic") else m.group(1)
                block[key] = _value(m.group(2))

    flush()
    close_command()
    return {
        "commands": commands,
        "n_unlabelled_commands": n_unlabelled,
        "n_total_commands": n_total_cmds,
        "jinja_control_lines": jinja_ctrl,
    }


def scenario_of(fname: str):
    m = re.match(r"scenario_(\d+)", os.path.basename(fname))
    return f"S{m.group(1)}" if m else None


def sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()


def collect(run_dir: str) -> "OrderedDict[str, dict]":
    runs: "OrderedDict[str, dict]" = OrderedDict()
    for root, _, files in os.walk(run_dir):
        for fn in sorted(files):
            if not re.match(r"scenario_\d+.*\.j2", fn):
                continue
            path = os.path.join(root, fn)
            rec = parse_playbook(path)
            if rec["commands"]:
                rec["scenario"] = scenario_of(fn)
                rec["source_sha256"] = sha256_file(path)
                rec["source_path"] = path.split("templates")[-1].strip("\\/")
                runs[fn] = rec

    # `scenario_5.j2.yml` duplicates `scenario_5.j2` (the .j2 only adds
    # comments). Keeping both would report S5 as two simulations where the
    # CAM-LDS paper's Table 2 reports one.
    for fn in [k for k in runs if k.endswith(".j2.yml")]:
        stem = fn[:-4]
        if stem in runs:
            a = [c["techniques"] for c in runs[stem]["commands"]]
            b = [c["techniques"] for c in runs[fn]["commands"]]
            if a == b:
                del runs[fn]
    return runs


def flat_tokens(run: dict):
    """The flattened token stream the OLD corpus used, for the equality check."""
    return [t for c in run["commands"] for t in c["techniques"]]


def verify_against_verified(runs) -> dict:
    """The new parse must imply exactly the old flat corpus.

    This is the guarantee that we changed the REPRESENTATION and nothing else:
    same playbooks, same labels, same command order. Only the grouping differs.
    """
    if not os.path.exists(VERIFIED_PATH):
        return {"checked": False, "reason": "camlds_grounding_verified.json absent"}
    with open(VERIFIED_PATH, encoding="utf-8") as f:
        old = json.load(f)["runs"]
    mine = {fn: flat_tokens(r) for fn, r in runs.items()}
    same_keys = set(mine) == set(old)
    mismatches = [k for k in sorted(set(mine) & set(old))
                  if mine[k] != old[k]["sequence"]]
    return {
        "checked": True,
        "same_run_set": same_keys,
        "only_in_new": sorted(set(mine) - set(old)),
        "only_in_old": sorted(set(old) - set(mine)),
        "sequence_mismatches": mismatches,
        "identical": bool(same_keys and not mismatches),
    }


def build(run_dir: str) -> dict:
    runs = collect(run_dir)
    by_scn = defaultdict(list)
    for fn, r in runs.items():
        by_scn[r["scenario"]].append(fn)

    n_cmd = sum(len(r["commands"]) for r in runs.values())
    n_lab = sum(len(c["techniques"]) for r in runs.values() for c in r["commands"])
    labels_per_cmd = Counter(len(c["techniques"])
                             for r in runs.values() for c in r["commands"])
    all_codes = {t for r in runs.values() for c in r["commands"] for t in c["techniques"]}
    all_parents = {t.split(".")[0] for t in all_codes}
    all_tactics = {t for r in runs.values() for c in r["commands"] for t in c["tactics"]}

    return {
        "source": "AttackBed AttackMate playbooks (github.com/ait-testbed/attackbed, "
                  "GPL-3.0), parsed directly. CAM-LDS: Landauer et al., arXiv:2603.04186v1.",
        "provenance": "SOURCE-DERIVED ANNOTATED PLAYBOOK SEQUENCES, command-level. "
                      "Each record is one annotated attacker command; the technique "
                      "list within a command is an UNORDERED annotation set, not an "
                      "observed execution order. These are scripted playbooks, not "
                      "real-world attack traces.",
        "representation": "command-level, multi-label",
        "label_order_within_command_is_meaningful": False,
        "n_playbooks": len(runs),
        "n_commands": n_cmd,
        "n_technique_labels": n_lab,
        "n_unlabelled_commands": sum(r["n_unlabelled_commands"] for r in runs.values()),
        "n_total_commands_including_unlabelled":
            sum(r["n_total_commands"] for r in runs.values()),
        "playbooks_with_jinja_control_flow":
            sum(1 for r in runs.values() if r["jinja_control_lines"] > 0),
        "labels_per_command_histogram": {str(k): v for k, v in sorted(labels_per_cmd.items())},
        "distinct_techniques_with_subtechniques": len(all_codes),
        "distinct_parent_techniques": len(all_parents),
        "distinct_tactics": len(all_tactics),
        "scenarios": {s: {"n_runs": len(v), "runs": v}
                      for s, v in sorted(by_scn.items(), key=lambda kv: int(kv[0][1:]))},
        "runs": {fn: {"scenario": r["scenario"],
                      "source_path": r["source_path"],
                      "source_sha256": r["source_sha256"],
                      "n_unlabelled_commands": r["n_unlabelled_commands"],
                      "jinja_control_lines": r["jinja_control_lines"],
                      "commands": r["commands"]}
                 for fn, r in runs.items()},
        "equality_with_flat_corpus": verify_against_verified(runs),
        "caveats": [
            "Playbooks contain Jinja2 control flow; the static command list is "
            "parsed without rendering, so a rendered run may repeat or skip "
            "commands. Counts here are of static annotated commands.",
            "Unlabelled commands are excluded from the corpus and counted "
            "separately. Absence of a label is absence of annotation, not "
            "evidence that no technique occurred.",
            "Technique order inside a command is discarded by design.",
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--attackbed", default=os.path.join(HERE, "..", "attackbed"),
                    help="path to the attackbed repository checkout")
    ap.add_argument("--out", default=OUT_PATH)
    ap.add_argument("--check", action="store_true",
                    help="parse and report, but do not write")
    args = ap.parse_args()

    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    run_dir = os.path.join(args.attackbed, "ansible", "run")
    if not os.path.isdir(run_dir):
        print(f"[!] AttackBed run directory not found: {os.path.abspath(run_dir)}")
        print("    Pass --attackbed <path>. Clone: "
              "git clone https://github.com/ait-testbed/attackbed")
        return 1

    data = build(run_dir)

    print("=" * 78)
    print("  COMMAND-LEVEL ATTACKBED PARSE")
    print("=" * 78)
    print(f"  playbooks                      : {data['n_playbooks']}")
    print(f"  annotated commands             : {data['n_commands']}")
    print(f"  technique labels               : {data['n_technique_labels']}")
    print(f"  unlabelled commands (excluded) : {data['n_unlabelled_commands']}")
    print(f"  labels per command             : {data['labels_per_command_histogram']}")
    print(f"  distinct parent techniques     : {data['distinct_parent_techniques']}")
    print(f"  playbooks w/ Jinja control flow: {data['playbooks_with_jinja_control_flow']}")
    print("\n  scenario  runs  commands  labels")
    for s, v in data["scenarios"].items():
        cmds = sum(len(data["runs"][f]["commands"]) for f in v["runs"])
        labs = sum(len(c["techniques"]) for f in v["runs"]
                   for c in data["runs"][f]["commands"])
        print(f"    {s:<7} {v['n_runs']:4d}  {cmds:8d}  {labs:6d}")

    eq = data["equality_with_flat_corpus"]
    print(f"\n  flat-corpus equality check     : {eq}")
    if eq.get("checked") and not eq.get("identical"):
        print("  [!] The flattened stream does NOT match the verified corpus.")
        print("      Refusing to write: the representation change must be the "
              "ONLY difference.")
        return 1

    if args.check:
        print("\n  --check: nothing written.")
        return 0

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=1, sort_keys=False)
    print(f"\n  wrote -> {os.path.relpath(args.out, HERE)}")
    print(f"  sha256 (LF-normalised) = {sha256_file(args.out)}")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
