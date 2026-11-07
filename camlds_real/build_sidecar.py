# -*- coding: utf-8 -*-
"""Build the preprocessing side files approved on 2026-11-07 (protocol 1.1, idea01_kuwano/PROTOCOL_1.1.md).

    python camlds_real/build_sidecar.py

steps.jsonl is NOT changed: it is pinned by SHA-256. Everything new goes into out/sidecar/:

  steps_link.jsonl    one row per step, keyed by source_row: its attackmate.json record, the full
                      command, the exact command start, the authors' manual window shift, its rank
                      in execution order, and whether it survives collapse_repeats
  points.jsonl        one row per TEST prediction point, for each condition, family and fold:
                      copy or novel, and every target label marked repeat or new
  SIDECAR_REPORT.txt  totals, checks against earlier measurements, and SHA-256 of the files

Inputs: out/steps.jsonl, out/vocab.json, out/scan/ATTACKMATE_ALL.jsonl. Read-only on all.
No model output is read and no metric is computed. Deterministic: no randomness, sorted output.
"""
from __future__ import annotations

import collections
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "idea01_kuwano"))
import reconcile_attackmate as ra  # noqa: E402
import split_spec as sp  # noqa: E402
import spec as p1  # noqa: E402  frozen protocol 1.0 constants

OUT = os.path.join(HERE, "out", "sidecar")
W = p1.WINDOW                                   # 16
EXCLUDED = set(p1.EXCLUDED_VARIANT_FOLDS)       # 2_cron, 2_rootkit
CONDITIONS = ("main", "collapse_repeats")


# ── definitions (each one is tested in camlds_real/tests/test_sidecar.py) ─────

def collapse_repeats(steps):
    """Keep the first execution of each (run, event_id); drop the re-executions (occurrence > 1)."""
    return [s for s in steps if s["occurrence"] == 1]


def sequences(steps):
    """run -> its steps in protocol order (ascending CSV start = exec_index)."""
    by = collections.defaultdict(list)
    for s in steps:
        by[s["run"]].append(s)
    return {r: sorted(v, key=lambda s: s["exec_index"]) for r, v in by.items()}


def points(seq, w=W):
    """Prediction points of one run: every step except the first. The window is the previous
    min(w, i) steps; each step is its sorted tuple of parent techniques."""
    lab = [tuple(sorted(s["techniques_parent"])) for s in seq]
    return [(i, tuple(lab[max(0, i - w):i]), lab[i]) for i in range(1, len(lab))]


def mark(test_seqs, seen_seqs, w=W):
    """Mark every test point. copy = the same window AND the same target occur at a prediction
    point of a run the fold does not test (its training or validation runs). A target label is
    a repeat when it occurs anywhere in the window, otherwise new."""
    seen = {(win, tgt) for q in seen_seqs for _, win, tgt in points(q, w)}
    out = []
    for q in test_seqs:
        for i, win, tgt in points(q, w):
            in_win = {t for step in win for t in step}
            out.append({"position": i, "source_row": q[i]["source_row"], "copy": (win, tgt) in seen,
                        "targets": [{"label": t, "repeat": t in in_win} for t in tgt]})
    return out


# ── builders ──────────────────────────────────────────────────────────────────

def link_rows(steps):
    _, recs, by = ra.load()
    pairs, shifted, _ = ra.join(steps, by)
    if len(pairs) != len(steps) or len({id(r) for r in pairs.values()}) != len(steps):
        raise SystemExit("join is not one-to-one; refusing to write")
    rank = {}
    for run, rs in by.items():
        used = sorted((r["index"], sr) for sr, r in pairs.items() if r["path"].split("/")[0] == "scenario_" + run)
        rank.update({sr: k for k, (_, sr) in enumerate(used)})
    rows = []
    for s in sorted(steps, key=lambda s: s["source_row"]):
        r = pairs[s["source_row"]]
        shift = (ra.usec_float(s["start"]) + ra.USUAL - r["t"]) / ra.US
        rows.append({
            "source_row": s["source_row"], "run": s["run"], "exec_index": s["exec_index"],
            "attackmate_path": r["path"], "attackmate_index": r["index"], "type": r["record"]["type"],
            "command_start_utc": r["record"]["start-datetime"],
            "cmd_full": r["record"]["cmd"],
            "csv_start_shift_s": round(shift, 6),
            "execution_rank": rank[s["source_row"]],
            "in_collapse_repeats": s["occurrence"] == 1,
        })
    return rows, len(shifted)


def point_rows(steps):
    rows = []
    for cond in CONDITIONS:
        st = steps if cond == "main" else collapse_repeats(steps)
        seqs = sequences(st)
        for fam in (sp.FAMILY_PRIMARY, sp.FAMILY_SECONDARY):
            for f in sp.folds(st, fam):
                if fam == sp.FAMILY_PRIMARY and f["fold"] in EXCLUDED:
                    continue
                test = sorted({s["run"] for s in f["test"]})
                seen = sorted({s["run"] for s in f["train"]})
                for r, m in zip(*_per_run(test, seen, seqs)):
                    rows.append({"condition": cond, "family": fam, "fold": f["fold"], "run": r, **m})
    return rows


def _per_run(test, seen, seqs):
    names, marks = [], []
    for r in test:
        for m in mark([seqs[r]], [seqs[x] for x in seen]):
            names.append(r)
            marks.append(m)
    return names, marks


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read().replace(b"\r\n", b"\n")).hexdigest()


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n")


def main():
    steps = sp.load(REPO)
    vocab = json.load(open(os.path.join(HERE, "out", "vocab.json"), encoding="utf-8"))["parent_techniques"]
    os.makedirs(OUT, exist_ok=True)
    links, n_shift = link_rows(steps)
    pts = point_rows(steps)
    write_jsonl(os.path.join(OUT, "steps_link.jsonl"), links)
    write_jsonl(os.path.join(OUT, "points.jsonl"), pts)

    log = ["CAM-LDS side files (protocol 1.1). Rebuild: python camlds_real/build_sidecar.py", ""]
    say = log.append
    say("1. LINK TO COMMAND RECORDS")
    say(f"  steps linked {len(links)} of {len(steps)}, one-to-one | CSV start moved by the authors: {n_shift}")
    swapped = sorted({x['run'] for x in links if x['execution_rank'] != x['exec_index']})
    say(f"  runs whose CSV order differs from execution order: {len(swapped)} {swapped}")

    say("\n4. COLLAPSE_REPEATS")
    col = collapse_repeats(steps)
    say(f"  steps {len(steps)} -> {len(col)} (removed {len(steps) - len(col)} re-executions); runs {len({s['run'] for s in col})}")

    say("\n5. LABEL LIST")
    used = sorted({t for s in steps for t in s["techniques_parent"]})
    say(f"  out/vocab.json parent_techniques: {len(vocab)} | equals the labels in steps.jsonl: {sorted(vocab) == used}"
        f" | sorted: {vocab == sorted(vocab)} | SHA-256 {sha(os.path.join(HERE, 'out', 'vocab.json'))}")

    say("\n2 and 3. TEST POINTS: COPY OR NOVEL; TARGET LABELS: REPEAT OR NEW")
    for cond in CONDITIONS:
        for fam in (sp.FAMILY_PRIMARY, sp.FAMILY_SECONDARY):
            q = [x for x in pts if x["condition"] == cond and x["family"] == fam]
            c = sum(x["copy"] for x in q)
            t = [y for x in q for y in x["targets"]]
            rp = sum(y["repeat"] for y in t)
            per = collections.defaultdict(lambda: [0, 0])
            for x in q:
                k = "S" + x["run"].split("_")[0]
                per[k][0] += x["copy"]
                per[k][1] += 1
            say(f"  {cond:<16} {fam:<18} points {len(q):>4} | copy {c:>4} ({c / len(q):.1%}) "
                f"{ {k: f'{a / b:.0%}' for k, (a, b) in sorted(per.items())} } | target labels {len(t):>4}, "
                f"repeat {rp} ({rp / len(t):.1%})")

    say("\nCHECKS AGAINST EARLIER MEASUREMENTS")
    allp = [m for s in sequences(steps).values() for m in mark([s], [])]
    tl = [y for x in allp for y in x["targets"]]
    rp = sum(y["repeat"] for y in tl)
    main_v = [x for x in pts if x["condition"] == "main" and x["family"] == sp.FAMILY_PRIMARY]
    main_s = [x for x in pts if x["condition"] == "main" and x["family"] == sp.FAMILY_SECONDARY]
    checks = {
        "corpus-wide points 870": len(allp) == 870,
        "corpus-wide repeat labels 600 of 1,270": (rp, len(tl)) == (600, 1270),
        "variant points 790 (protocol 1.0)": len(main_v) == 790,
        "scenario points 331 (protocol 1.0)": len(main_s) == 331,
        "variant copy share 53.8% (DATASET_REPORT)": round(100 * sum(x["copy"] for x in main_v) / len(main_v), 1) == 53.8,
        "scenario copy share 0%": sum(x["copy"] for x in main_s) == 0,
        "collapse leaves 883 steps": len(col) == 883,
        "81 labels": len(vocab) == 81 and sorted(vocab) == used,
        "steps.jsonl unchanged (protocol 1.0 hash)": sha(os.path.join(HERE, "out", "steps.jsonl")) == p1.INPUTS["camlds_real/out/steps.jsonl"],
    }
    for k, v in checks.items():
        say(f"  {'PASS' if v else 'FAIL'}  {k}")

    say("\nFILES (SHA-256 after CRLF->LF)")
    for f in ("steps_link.jsonl", "points.jsonl"):
        say(f"  out/sidecar/{f}  {sha(os.path.join(OUT, f))}")
    txt = "\n".join(log) + "\n"
    with open(os.path.join(OUT, "SIDECAR_REPORT.txt"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(txt)
    print(txt)
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
