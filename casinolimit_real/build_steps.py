# -*- coding: utf-8 -*-
"""CasinoLimit -> the same step format as CAM-LDS (camlds_real/out/steps.jsonl).

    python casinolimit_real/build_steps.py

Input : dataset_survey/out/casinolimit_steps/steps.csv  (one row per label, in time order; made by
        dataset_survey/casinolimit_steps.py from the Zenodo 17256954 files, md5 checked)
Output: casinolimit_real/out/steps.jsonl   one row per command, same fields as CAM-LDS
        casinolimit_real/out/vocab.json    label space (same keys as CAM-LDS vocab.json)
        casinolimit_real/out/runs.json     one entry per attacker
        casinolimit_real/out/CORPUS_REPORT.txt  measures, side by side with CAM-LDS

Definitions (each one is tested in casinolimit_real/tests/test_build_steps.py):
  step         one command = all labels whose earliest auditd event is the same event
               (first_event). CAM-LDS steps are also one command with one or more labels.
  run          one CasinoLimit instance = one human attacker. base_scenario is "casinolimit" for
               all runs (one challenge); variant is the instance name.
  order        exec_index = the order of the command in time (ties broken by event id), from
               the "order" column of steps.csv.
  labels       techniques_parent = the technique IDs of the step's labels. CasinoLimit labels are
               parent techniques only (no sub-techniques), so techniques_sub = techniques_parent.
  repeats      event_id / occurrence: CAM-LDS marks a re-run of the same scripted event with
               occurrence > 1. Here a re-run is the same command text with the same label set in
               the same run. Commands are the masked text of steps.csv (long tokens such as URLs
               become <token:N>), so two different long commands of equal length can count as one;
               this affects only the "collapse_repeats" condition.
  machine      the machine of the step's earliest event (start, bastion, meet, intranet). Derived
               from the logs, not hand-typed (CAM-LDS zones were hand-typed from its paper).
  doubt        techniques of the step that a CasinoLimit reviewer marked "doubt". They are kept as
               labels (they are the dataset's own final labels) and listed so a later condition can
               drop them.
Nothing here uses a model, a split or a test set.
"""
from __future__ import annotations

import calendar
import collections
import csv
import hashlib
import json
import os
import statistics as st
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SOURCE = os.path.join(REPO, "dataset_survey", "out", "casinolimit_steps", "steps.csv")
CAMLDS = os.path.join(REPO, "camlds_real", "out", "steps.jsonl")
OUT = os.path.join(HERE, "out")
W = 16                                   # window of the encoder (CAM-LDS protocol 1.0)
SCENARIO = "casinolimit"


def epoch(ts: str) -> float:
    """'2024-05-18 01:08:14.257Z' (UTC) -> seconds."""
    base, _, ms = ts.rstrip("Z").partition(".")
    return calendar.timegm(time.strptime(base, "%Y-%m-%d %H:%M:%S")) + int(ms or 0) / 1000


def build(rows: list[dict]) -> list[dict]:
    """Label rows (steps.csv) -> command steps in CAM-LDS format."""
    by_run = collections.defaultdict(list)
    for i, r in enumerate(rows):
        by_run[r["instance"]].append((int(r["order"]), i, r))
    steps = []
    for run in sorted(by_run):
        items = sorted(by_run[run])
        if [o for o, _, _ in items] != list(range(1, len(items) + 1)):
            raise ValueError(f"{run}: 'order' is not 1..n")
        groups = []
        for _, i, r in items:
            if groups and groups[-1]["first_event"] == r["first_event"]:
                g = groups[-1]
            else:
                if any(g["first_event"] == r["first_event"] for g in groups):
                    raise ValueError(f"{run}: event {r['first_event']} is split by another step")
                g = {"first_event": r["first_event"], "rows": []}
                groups.append(g)
            g["rows"].append((i, r))
        event_ids, occ = {}, collections.Counter()
        run_steps = []
        for k, g in enumerate(groups):
            rs = [r for _, r in g["rows"]]
            cmds, times = {r["command"] for r in rs}, {r["time"] for r in rs}
            if len(cmds) != 1 or len(times) != 1:
                raise ValueError(f"{run}: event {g['first_event']} has {len(cmds)} commands, {len(times)} times")
            techs = sorted({r["technique"] for r in rs})
            if len(techs) != len(rs):
                raise ValueError(f"{run}: event {g['first_event']} has a technique twice")
            cmd = rs[0]["command"]
            key = (cmd, tuple(techs))
            event_ids.setdefault(key, len(event_ids) + 1)
            occ[key] += 1
            run_steps.append({
                "run": run, "base_scenario": SCENARIO, "variant": run, "exec_index": k,
                "event_id": event_ids[key], "occurrence": occ[key], "_key": key,
                "start": epoch(rs[0]["time"]), "end": None, "cmd": cmd,
                "techniques_sub": techs, "techniques_parent": techs, "n_techniques": len(techs),
                "tactics_raw": None, "source_row": min(i for i, _ in g["rows"]),
                "machine": g["first_event"].split("-", 1)[1], "first_event": g["first_event"],
                "doubt": sorted({r["technique"] for r in rs if r["doubt"] == "True"}),
                "labelled_by": sorted({r["by"] for r in rs}),
            })
        for s in run_steps:
            s["n_occurrences"] = occ[s.pop("_key")]
        steps += run_steps
    return steps


def load_csv(path: str) -> list[dict]:
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def measures(steps: list[dict], w: int = W) -> dict:
    """Fold-free measures, computed the same way for both corpora."""
    runs = collections.defaultdict(list)
    for s in steps:
        runs[s["run"]].append(s)
    lens, n_points, n_targets, n_repeat, novel_pts = [], 0, 0, 0, 0
    label_runs = collections.defaultdict(set)
    for r, seq in runs.items():
        seq.sort(key=lambda s: s["exec_index"])
        lens.append(len(seq))
        lab = [set(s["techniques_parent"]) for s in seq]
        for t in set().union(*lab):
            label_runs[t].add(r)
        for i in range(1, len(seq)):
            window = set().union(*lab[max(0, i - w):i])
            before = set().union(*lab[:i])
            n_points += 1
            n_targets += len(lab[i])
            n_repeat += len(lab[i] & window)
            novel_pts += bool(lab[i] - before)
    lens.sort()
    cards = collections.Counter(len(s["techniques_parent"]) for s in steps)
    return {
        "runs": len(runs), "steps": len(steps), "labels": len(label_runs),
        "steps per run": f"min {lens[0]}, median {st.median(lens):g}, mean {st.mean(lens):.1f}, max {lens[-1]}",
        "runs with 1 step (no prediction point)": sum(n == 1 for n in lens),
        "runs with 30+ steps": sum(n >= 30 for n in lens),
        "prediction points (every step except a run's first)": n_points,
        "labels per step (1/2/3+)": f"{cards[1]} / {cards[2]} / {sum(v for k, v in cards.items() if k >= 3)}",
        f"target labels already in the {w}-step window ('repeat')": f"{n_repeat} of {n_targets} ({100 * n_repeat / max(n_targets, 1):.1f}%)",
        "points with a label never seen before in the run": f"{novel_pts} of {n_points} ({100 * novel_pts / max(n_points, 1):.1f}%)",
        "labels used by only 1 run": sum(len(v) == 1 for v in label_runs.values()),
        "labels used by 10+ runs": sum(len(v) >= 10 for v in label_runs.values()),
        "steps if repeats are collapsed (occurrence 1 only)": sum(s["occurrence"] == 1 for s in steps),
    }


def sha(path: str) -> str:
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if not os.path.isfile(SOURCE):
        print(f"MISSING: {SOURCE}")
        return 1
    rows = load_csv(SOURCE)
    steps = build(rows)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "steps.jsonl"), "w", encoding="utf-8", newline="\n") as fh:
        for s in steps:
            fh.write(json.dumps(s, ensure_ascii=False) + "\n")

    counts = collections.Counter(t for s in steps for t in s["techniques_parent"])
    labels = sorted(counts)
    with open(os.path.join(OUT, "vocab.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"built_from": "dataset_survey/out/casinolimit_steps/steps.csv",
                   "note": "CasinoLimit labels are parent techniques only, so sub = parent.",
                   "sub_techniques": labels, "parent_techniques": labels,
                   "n_sub": len(labels), "n_parent": len(labels),
                   "sub_counts": dict(sorted(counts.items())), "parent_counts": dict(sorted(counts.items()))},
                  fh, indent=2)

    runs = {}
    for r in sorted({s["run"] for s in steps}):
        seq = [s for s in steps if s["run"] == r]
        path = [m for i, m in enumerate(s["machine"] for s in seq) if i == 0 or m != seq[i - 1]["machine"]]
        runs[r] = {"base_scenario": SCENARIO, "variant": r, "n_steps": len(seq),
                   "n_distinct_event_ids": len({s["event_id"] for s in seq}),
                   "n_repeated_event_ids": sum(s["occurrence"] > 1 for s in seq),
                   "t_start": seq[0]["start"], "t_end": seq[-1]["start"],
                   "duration_s": round(seq[-1]["start"] - seq[0]["start"], 1),
                   "machines": sorted({s["machine"] for s in seq}), "machine_switches": len(path) - 1,
                   "entry_machine": seq[0]["machine"],
                   "zone_source": "derived: machine of each step's earliest auditd event"}
    with open(os.path.join(OUT, "runs.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(runs, fh, indent=2)

    mc = measures(steps)
    cam = measures([json.loads(l) for l in open(CAMLDS, encoding="utf-8")]) if os.path.isfile(CAMLDS) else {}
    L = ["CASINOLIMIT IN THE CAM-LDS STEP FORMAT",
         f"Made by casinolimit_real/build_steps.py on {time.strftime('%Y-%m-%d %H:%M')}.",
         f"Input  steps.csv  sha256 {sha(SOURCE)}  ({len(rows):,} label rows)",
         f"Output steps.jsonl sha256 {sha(os.path.join(OUT, 'steps.jsonl'))}",
         "",
         "1. SIDE BY SIDE (same code for both; W = 16; no split, no model)",
         f"   {'measure':<58}{'CasinoLimit':>40}{'CAM-LDS':>40}"]
    for k in mc:
        L.append(f"   {k:<58}{str(mc[k]):>40}{str(cam.get(k, '')):>40}")
    mach = collections.Counter(s["machine"] for s in steps)
    entry = collections.Counter(v["entry_machine"] for v in runs.values())
    nm = collections.Counter(len(v["machines"]) for v in runs.values())
    L += ["",
          "2. MACHINES (CasinoLimit only; zones in CAM-LDS were hand-typed per run)",
          "   steps per machine: " + ", ".join(f"{k} {v:,}" for k, v in mach.most_common()),
          "   first machine of each run: " + ", ".join(f"{k} {v}" for k, v in entry.most_common()),
          "   runs touching 1/2/3/4 machines: " + " / ".join(str(nm[k]) for k in (1, 2, 3, 4)),
          "",
          "3. LABEL QUALITY (CasinoLimit only)",
          f"   steps with at least one 'doubt' label: {sum(bool(s['doubt']) for s in steps):,} of {len(steps):,}",
          "   steps by labeller: " + ", ".join(f"{k} {v:,}" for k, v in collections.Counter(
              "+".join(s["labelled_by"]) for s in steps).most_common()),
          "",
          "4. CHECKS",
          f"   every label row used once: {sum(s['n_techniques'] for s in steps) == len(rows)}",
          f"   exec_index is 0..n-1 in every run: "
          f"{all([s['exec_index'] for s in steps if s['run'] == r] == list(range(v['n_steps'])) for r, v in runs.items())}",
          f"   time never goes backwards inside a run: "
          f"{all(a['start'] <= b['start'] for a, b in zip(steps, steps[1:]) if a['run'] == b['run'])}",
          f"   every label is in the vocabulary: {all(t in counts for s in steps for t in s['techniques_parent'])}",
          "",
          "Not done here, on purpose: no split, no training, no test scores. The split must be fixed",
          "and written down before any model sees this corpus."]
    text = "\n".join(L) + "\n"
    with open(os.path.join(OUT, "CORPUS_REPORT.txt"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
