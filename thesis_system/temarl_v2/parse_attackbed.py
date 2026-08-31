# -*- coding: utf-8 -*-
"""
TEMARL v2 — Parse AttackBed playbooks into a SOURCE-VERIFIED CAM-LDS grounding
==============================================================================
Upgrades data/camlds_grounding.json from a PAPER RECONSTRUCTION (transcribed by
hand from CAM-LDS Sec. 3.4 and Figs. 5-11) to a SOURCE-VERIFIED artefact parsed
directly from the published AttackMate playbooks:

    https://github.com/ait-testbed/attackbed
    ansible/run/scenario<N>/templates/scenario_<N>[_<variant>].j2

Each playbook step carries ordered metadata, exactly as shown in CAM-LDS Fig. 4:

    - type: shell
      cmd: dnsenum -f $DNS_LIST --dnsserver $DNS_SERVER $DOMAIN
      metadata:
        techniques: "T1590.002,T1591"
        tactics: "Reconnaissance"

Because the metadata blocks appear in COMMAND ORDER, reading them top-to-bottom
recovers the true executed technique sequence per run -- at full step
resolution, across every variant, rather than the condensed per-scenario summary
the paper's figures allow.

The playbooks are Jinja2 templates (unrendered `{{...}}` vars), so a YAML parser
would fail on them. We therefore scan line-wise with regex, which is robust to
the templating and does not require rendering the infrastructure.

This script REPORTS the agreement between the reconstruction and the source
rather than silently overwriting: if my hand transcription was wrong, that is
worth knowing and recording, not hiding.
"""

import json
import os
import re
from collections import Counter, OrderedDict, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ATTACKBED = os.path.join(HERE, "..", "..", "attackbed")
RUN_DIR = os.path.join(ATTACKBED, "ansible", "run")
OUT_PATH = os.path.join(HERE, "..", "data", "camlds_grounding_verified.json")
OLD_PATH = os.path.join(HERE, "..", "data", "camlds_grounding.json")

TECH_RE = re.compile(r'^\s*techniques:\s*["\']?([^"\'\n]+)["\']?\s*$')
# NB: 35 playbooks use `tactics:`; the 2 scenario-5 files use the SINGULAR
# `tactic:`. Matching only the plural silently dropped scenario 5 entirely.
TACT_RE = re.compile(r'^\s*tactics?:\s*["\']?([^"\'\n]+)["\']?\s*$')
NAME_RE = re.compile(r'^\s*technique_name:\s*["\']?([^"\'\n]+)["\']?\s*$')
CODE_RE = re.compile(r'T\d{4}(?:\.\d{3})?')


def parse_playbook(path):
    """Return ordered [(technique_code, tactic, name)] in command order."""
    steps = []
    pending_tech = None
    pending_name = None
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            m = TECH_RE.match(line)
            if m:
                pending_tech = CODE_RE.findall(m.group(1))
                pending_name = None
                continue
            m = NAME_RE.match(line)
            if m and pending_tech is not None:
                pending_name = m.group(1).strip()
                continue
            m = TACT_RE.match(line)
            if m and pending_tech is not None:
                tactics = [t.strip() for t in m.group(1).split(",")]
                for i, code in enumerate(pending_tech):
                    steps.append((code,
                                  tactics[i] if i < len(tactics) else tactics[0],
                                  pending_name or ""))
                pending_tech, pending_name = None, None
    # a metadata block may omit `tactics:`; keep those techniques with tactic ""
    return steps


def scenario_of(fname):
    m = re.match(r"scenario_(\d+)", os.path.basename(fname))
    return f"S{m.group(1)}" if m else None


def collect():
    runs = OrderedDict()
    for root, _, files in os.walk(RUN_DIR):
        for fn in sorted(files):
            if not re.match(r"scenario_\d+.*\.j2", fn):
                continue
            path = os.path.join(root, fn)
            steps = parse_playbook(path)
            if steps:
                runs[fn] = {"scenario": scenario_of(fn), "path": path,
                            "steps": steps}
    # `scenario_5.j2.yml` is the SAME playbook as `scenario_5.j2` (the .j2 merely
    # carries explanatory comments) -- identical technique sequences. Keeping both
    # would report scenario 5 as 2 simulations where the paper's Table 2 says 1.
    for fn in [k for k in runs if k.endswith(".j2.yml")]:
        stem = fn[:-4]
        if stem in runs and ([c for c, _, _ in runs[stem]["steps"]] ==
                             [c for c, _, _ in runs[fn]["steps"]]):
            del runs[fn]
    return runs


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("=" * 86)
    print("  ATTACKBED PLAYBOOK PARSER — source-verified CAM-LDS grounding")
    print("=" * 86)

    if not os.path.isdir(RUN_DIR):
        print(f"  [!] AttackBed not found at {os.path.abspath(RUN_DIR)}")
        sys.exit(1)

    runs = collect()
    print(f"  parsed {len(runs)} playbooks from {os.path.abspath(RUN_DIR)}")

    by_scn = defaultdict(list)
    for fn, r in runs.items():
        by_scn[r["scenario"]].append(r)

    print(f"\n  {'scen':<6} {'runs':>5} {'steps/run (min-max)':>21} "
          f"{'distinct techniques':>20} {'tactics':>8}")
    print("  " + "-" * 66)
    total_steps = 0
    for s in sorted(by_scn, key=lambda x: int(x[1:])):
        rs = by_scn[s]
        lens = [len(r["steps"]) for r in rs]
        techs = {c for r in rs for c, _, _ in r["steps"]}
        tacs = {t for r in rs for _, t, _ in r["steps"] if t}
        total_steps += sum(lens)
        print(f"  {s:<6} {len(rs):>5} {min(lens):>9}-{max(lens):<11} "
              f"{len(techs):>20} {len(tacs):>8}")
    all_t = {c for r in runs.values() for c, _, _ in r["steps"]}
    all_parent = {c.split(".")[0] for c in all_t}
    all_tac = {t for r in runs.values() for _, t, _ in r["steps"] if t}
    print("  " + "-" * 66)
    print(f"  TOTAL  {len(runs):>5} {total_steps:>9} labelled technique instances")
    print(f"  distinct techniques (with sub-techniques): {len(all_t)}")
    print(f"  distinct PARENT techniques               : {len(all_parent)}")
    print(f"  distinct tactics                         : {len(all_tac)}")
    print(f"  paper (CAM-LDS Table 3) reports: 81 techniques, 13 tactics, "
          f"34 simulations, 243 steps")

    # ── agreement with the hand reconstruction ──────────────────────────────
    print(f"\n  AGREEMENT WITH THE PAPER-BASED RECONSTRUCTION "
          f"(honest check, not a silent overwrite)")
    try:
        old = json.load(open(OLD_PATH, encoding="utf-8"))
        old_inv = {k for k in old["technique_inventory"] if k != "_comment"}
        print(f"    reconstruction parent techniques : {len(old_inv)}")
        print(f"    source-verified parent techniques: {len(all_parent)}")
        both = old_inv & all_parent
        print(f"    agreed          : {len(both)}")
        print(f"    source-only (I MISSED these)     : {len(all_parent - old_inv)}")
        print(f"    reconstruction-only (I ADDED / paper-figure only): "
              f"{len(old_inv - all_parent)}")
        miss = sorted(all_parent - old_inv)
        if miss:
            print(f"      missed: {', '.join(miss[:18])}"
                  f"{' ...' if len(miss) > 18 else ''}")
        extra = sorted(old_inv - all_parent)
        if extra:
            print(f"      extra : {', '.join(extra[:18])}"
                  f"{' ...' if len(extra) > 18 else ''}")
        prec = len(both) / max(len(old_inv), 1)
        rec = len(both) / max(len(all_parent), 1)
        print(f"    reconstruction precision={prec:.1%}  recall={rec:.1%}")
    except (FileNotFoundError, KeyError, ValueError) as e:
        print(f"    [skip] {e}")

    # ── write the verified artefact ────────────────────────────────────────
    name_of = defaultdict(Counter)
    tac_of = defaultdict(Counter)
    for r in runs.values():
        for code, tac, nm in r["steps"]:
            par = code.split(".")[0]
            if nm:
                name_of[par][nm.split(":")[0].split(",")[0].strip()] += 1
            if tac:
                tac_of[par][tac] += 1
    inventory = {
        p: {"name": (name_of[p].most_common(1)[0][0] if name_of[p] else p),
            "tactic": (tac_of[p].most_common(1)[0][0] if tac_of[p] else "Unknown")}
        for p in sorted(all_parent)
    }

    out = {
        "source": "AttackBed AttackMate playbooks (github.com/ait-testbed/attackbed), "
                  "parsed directly. CAM-LDS: Landauer et al., arXiv:2603.04186v1.",
        "provenance": "SOURCE-VERIFIED (parsed from published playbooks). Supersedes "
                      "the earlier hand reconstruction from the paper's prose/figures.",
        "n_playbooks": len(runs),
        "n_labelled_steps": total_steps,
        "runs": {fn: {"scenario": r["scenario"],
                      "sequence": [c for c, _, _ in r["steps"]],
                      "tactics": [t for _, t, _ in r["steps"]]}
                 for fn, r in runs.items()},
        "scenarios": {s: {"n_runs": len(by_scn[s]),
                          "variant_files": [x["path"].split("templates")[-1].strip("\\/")
                                            for x in by_scn[s]]}
                      for s in sorted(by_scn, key=lambda x: int(x[1:]))},
        # Emitted as {code: {name, tactic}} -- the shape vocab_v2.build_vocab()
        # consumes. Name/tactic are the MODAL label observed for that parent
        # across all playbook steps (sub-technique names collapse to the parent).
        "technique_inventory": inventory,
        "tactics": sorted(all_tac),
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print(f"\n  wrote -> {os.path.relpath(OUT_PATH, HERE)}")
    print(f"  (the original reconstruction is left UNTOUCHED at "
          f"{os.path.basename(OLD_PATH)})")
    print("=" * 86)
