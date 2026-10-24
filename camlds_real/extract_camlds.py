# -*- coding: utf-8 -*-
"""Extract the CAM-LDS release into a faithful, ordered, multi-label corpus.

Every decision here is forced by something measured in the verification pass,
not assumed. The three that matter:

  ORDER COMES FROM `start`, NEVER FROM `event_id`.
      event_id is a playbook STEP IDENTIFIER, not an execution index. It is
      non-monotonic in 27 of 34 runs, and sorting by it breaks timestamp order
      in 28 of 34. Row order in the CSV is closer but still wrong in 4 runs
      (the scenario-6 variants, 2 positions each). Only `start` is reliable.

  REPEATED (run, event_id) KEYS ARE SEPARATE EXECUTIONS.
      attack_times.csv has 904 rows over 883 distinct (scenario, event_id)
      pairs. All 18 repeated keys have fully distinct timestamps -- none
      identical -- so each repetition really ran. Keying on (run, event_id)
      would silently drop 21 rows, so every row is kept and given an
      `occurrence` index.

  THE VOCABULARY IS REBUILT FROM THE RELEASE.
      The old 84-label vocabulary is not reused. Sub-technique -> parent
      collapse is applied explicitly and both forms are emitted, so the choice
      is visible rather than baked in.

Deliberately NOT done here: no windows, no splits, no collapsing of repeats.
Those are modelling decisions and belong downstream, where they can be declared
and varied. This produces the faithful record they operate on.

Zones and goals are NOT written as facts. They are carried from the hand-typed
grounding as `zone_source: "hand-typed"`, optionally alongside a log-volume
cross-check marked as corroborating evidence only -- volume is confounded by
per-service logging verbosity and collection settings, and agreeing with an
existing annotation does not independently validate it.

Usage
-----
    python camlds_real/extract_camlds.py
    python camlds_real/extract_camlds.py --data "<dir with the zips>"   # adds
                                                                        # the
                                                                        # volume
                                                                        # cross-check

Outputs (into camlds_real/out/):
    steps.jsonl          one record per source row; all 904 reconciled
    runs.json            per-run metadata, ordering provenance, zone carry-over
    vocab.json           technique vocabulary built from the release
    EXTRACT_REPORT.md    reconciliation and every declared decision
"""

from __future__ import annotations

import argparse
import collections
import csv
import json
import os
import re
import sys
import zipfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RULE = "=" * 78
log: list[str] = []
INFRA = {"attacker", "wazuh", "mgmt"}
TECH = re.compile(r"^T\d{4}")


def say(s: str = "") -> None:
    print(s)
    log.append(s)


def head(s: str) -> None:
    say("")
    say(RULE)
    say(s)
    say(RULE)


def techs_of(cell: str) -> list[str]:
    """'T1590.002_T1591' -> ['T1590.002', 'T1591'] (order preserved)."""
    return [x for x in cell.replace("_T", "|T").split("|") if TECH.match(x)]


def parent(t: str) -> str:
    return t.split(".")[0]


def find_csv(repo: str, data_dir: str | None) -> tuple[str, list[dict]] | None:
    cands = [os.path.join(repo, "camlds_real", "attack_times.csv")]
    if data_dir:
        cands.append(os.path.join(data_dir, "attack_times.csv"))
    for c in cands:
        if os.path.isfile(c):
            txt = open(c, encoding="utf-8", errors="replace").read()
            return c, list(csv.DictReader(txt.splitlines(), delimiter=";"))
    if data_dir and os.path.isdir(data_dir):
        for root, _, files in os.walk(data_dir):
            for fn in files:
                if fn.lower().endswith(".zip"):
                    try:
                        with zipfile.ZipFile(os.path.join(root, fn)) as z:
                            hit = next((n for n in z.namelist()
                                        if n.endswith("attack_times.csv")), None)
                            if hit:
                                txt = z.read(hit).decode("utf-8", "replace")
                                return (f"{fn}::{hit}",
                                        list(csv.DictReader(txt.splitlines(),
                                                            delimiter=";")))
                    except Exception:  # noqa: BLE001, S112
                        continue
    return None


def volume_crosscheck(data_dir: str | None) -> dict[str, list[tuple[str, int]]]:
    """Per-run, non-infrastructure hosts by log bytes. CORROBORATING ONLY."""
    if not data_dir or not os.path.isdir(data_dir):
        return {}
    mf = None
    for root, _, files in os.walk(data_dir):
        for fn in files:
            if re.match(r"^manifestations_filtered(\s*\(\d+\))?\.zip$", fn, re.I):
                mf = os.path.join(root, fn)
    if not mf:
        return {}
    pat = re.compile(r"^manifestations_filtered/steps/([^/]+?)-(\d+)/([^/]+)/")
    vol: dict[str, collections.Counter] = collections.defaultdict(
        collections.Counter)
    try:
        with zipfile.ZipFile(mf) as z:
            for i in z.infolist():
                m = pat.match(i.filename)
                if m and not i.filename.endswith("/"):
                    if m.group(3).lower() not in INFRA:
                        vol[m.group(1)][m.group(3)] += i.file_size
    except Exception as e:  # noqa: BLE001
        say(f"  volume cross-check unavailable: {e}")
        return {}
    return {k: v.most_common() for k, v in vol.items()}


def main() -> int:
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--data", default=None,
                    help="dir with the release zips (enables the volume cross-check)")
    ap.add_argument("--repo", default=os.path.dirname(here))
    ap.add_argument("--out", default=os.path.join(here, "out"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    say("CAM-LDS extraction")
    say(f"  repo : {os.path.abspath(a.repo)}")
    say(f"  out  : {os.path.abspath(a.out)}")

    got = find_csv(a.repo, a.data)
    if not got:
        say("  !! attack_times.csv not found.")
        return 1
    src, rows = got
    say(f"  source: {src}  ({len(rows)} rows)")

    # ── declared decisions, printed before anything is written ──────────────
    head("DECLARED DECISIONS")
    say("  D1 ORDER = ascending `start` timestamp.")
    say("     event_id is non-monotonic in 27/34 runs and sorting by it breaks")
    say("     timestamp order in 28/34. Row order is wrong in 4 runs. Only the")
    say("     timestamp is reliable, so it is the sole ordering key.")
    say("  D2 EVERY SOURCE ROW IS KEPT. 904 rows over 883 distinct")
    say("     (run, event_id) keys; the 18 repeated keys all have distinct")
    say("     timestamps, so they are separate executions. Each row carries an")
    say("     `occurrence` index. Nothing is merged here.")
    say("  D3 VOCABULARY IS REBUILT from the release. Both sub-technique and")
    say("     parent forms are emitted; no prior vocabulary is imposed.")
    say("  D4 ZONES/GOALS ARE NOT DERIVED. They are carried from the hand-typed")
    say("     grounding and labelled as such. Log volume, where available, is")
    say("     recorded as CORROBORATING evidence only -- it is confounded by")
    say("     per-service logging verbosity and collection settings, and")
    say("     agreeing with an annotation does not validate that annotation.")
    say("  D5 NO WINDOWS, NO SPLITS, NO COLLAPSING. Those are modelling")
    say("     choices and are made downstream where they can be varied.")

    # ── build ───────────────────────────────────────────────────────────────
    for i, r in enumerate(rows):
        r["_row"] = i
    by_run: dict[str, list[dict]] = collections.defaultdict(list)
    for r in rows:
        by_run[r["scenario"]].append(r)

    steps: list[dict] = []
    run_meta: dict[str, dict] = {}
    reorder_counts: dict[str, int] = {}

    for run, rs in sorted(by_run.items()):
        in_file = list(rs)
        ordered = sorted(rs, key=lambda r: (float(r["start"]), int(r["event_id"])))
        moved = sum(1 for x, y in zip(in_file, ordered) if x["_row"] != y["_row"])
        reorder_counts[run] = moved

        seen: collections.Counter = collections.Counter()
        totals = collections.Counter(int(r["event_id"]) for r in rs)
        base = run.split("_")[0]
        variant = run[len(base) + 1:] if "_" in run else ""

        for k, r in enumerate(ordered):
            ev = int(r["event_id"])
            seen[ev] += 1
            sub = techs_of(r["techniques"])
            steps.append({
                "run": run,
                "base_scenario": base,
                "variant": variant,
                "exec_index": k,                  # D1: position in time order
                "event_id": ev,                   # identifier, NOT an order
                "occurrence": seen[ev],           # D2
                "n_occurrences": totals[ev],
                "start": float(r["start"]),
                "end": float(r["end"]),
                "cmd": r["cmd"],
                "techniques_sub": sub,
                "techniques_parent": sorted({parent(t) for t in sub}),
                "n_techniques": len(sub),
                "tactics_raw": r["tactics"],
                "source_row": r["_row"],          # reconciles to attack_times.csv
            })

        span = (ordered[-1]["end"], ordered[0]["start"]) if ordered else (0, 0)
        run_meta[run] = {
            "base_scenario": base,
            "variant": variant,
            "n_steps": len(ordered),
            "n_distinct_event_ids": len(totals),
            "n_repeated_event_ids": sum(1 for c in totals.values() if c > 1),
            "rows_moved_by_time_sort": moved,
            "t_start": ordered[0]["start"] if ordered else None,
            "t_end": ordered[-1]["end"] if ordered else None,
            "duration_s": round(float(span[0]) - float(span[1]), 1) if ordered else None,
        }

    # ── vocabulary, from the release only (D3) ──────────────────────────────
    sub_c = collections.Counter(t for s in steps for t in s["techniques_sub"])
    par_c = collections.Counter(t for s in steps for t in s["techniques_parent"])
    vocab = {
        "built_from": src,
        "note": "Rebuilt from the release (D3). The prior 84-label vocabulary "
                "is NOT imposed.",
        "sub_techniques": sorted(sub_c),
        "parent_techniques": sorted(par_c),
        "n_sub": len(sub_c),
        "n_parent": len(par_c),
        "sub_counts": dict(sub_c.most_common()),
        "parent_counts": dict(par_c.most_common()),
    }

    # ── zones carried, never derived (D4) ───────────────────────────────────
    hand = {}
    for cand in ("thesis_system/data/camlds_grounding.json",
                 "Temarl_Test_v1_L1/thesis_system/data/camlds_grounding.json"):
        p = os.path.join(a.repo, cand)
        if os.path.isfile(p):
            g = json.load(open(p, encoding="utf-8"))
            for s in (g.get("scenarios") or []):
                if isinstance(s, dict) and s.get("id"):
                    hand[re.sub(r"^S", "", str(s["id"]))] = {
                        "entry_zone": s.get("entry_zone"),
                        "target_zone": s.get("target_zone"),
                        "target_host": s.get("target_host"),
                        "goal_tactic": s.get("terminal_tactic"),
                        "zone_source": "hand-typed from the CAM-LDS paper "
                                       "(Sec 3.4, Figs 5-11); NOT derived",
                    }
            break
    vol = volume_crosscheck(a.data)
    for run, m in run_meta.items():
        m.update(hand.get(m["base_scenario"], {"zone_source": "UNKNOWN"}))
        if run in vol:
            m["log_volume_rank"] = [{"host": h, "bytes": b} for h, b in vol[run][:5]]
            m["log_volume_note"] = ("CORROBORATING ONLY (D4): confounded by "
                                    "per-service logging verbosity.")

    # ── write ───────────────────────────────────────────────────────────────
    with open(os.path.join(a.out, "steps.jsonl"), "w", encoding="utf-8") as f:
        for s in steps:
            f.write(json.dumps(s) + "\n")
    with open(os.path.join(a.out, "runs.json"), "w", encoding="utf-8") as f:
        json.dump(run_meta, f, indent=2)
    with open(os.path.join(a.out, "vocab.json"), "w", encoding="utf-8") as f:
        json.dump(vocab, f, indent=2)

    # ── reconciliation ──────────────────────────────────────────────────────
    head("RECONCILIATION — every source row accounted for")
    seen_rows = {s["source_row"] for s in steps}
    say(f"  source rows            : {len(rows)}")
    say(f"  emitted steps          : {len(steps)}")
    say(f"  distinct source rows   : {len(seen_rows)}")
    say(f"  dropped                : {len(rows) - len(seen_rows)}")
    say(f"  merged                 : 0  (D2: nothing is merged here)")
    ok = len(steps) == len(rows) == len(seen_rows)
    say(f"  LOSSLESS               : {'YES' if ok else 'NO  <-- investigate'}")
    say("")
    say(f"  runs                   : {len(run_meta)}")
    say(f"  technique instances    : {sum(s['n_techniques'] for s in steps)}")
    say(f"  sub-techniques         : {vocab['n_sub']}")
    say(f"  parent techniques      : {vocab['n_parent']}")
    multi = sum(1 for s in steps if s["n_techniques"] > 1)
    say(f"  multi-technique steps  : {multi} ({100 * multi / len(steps):.1f}%)")

    head("ORDERING — how far time order moved rows from file order (D1)")
    moved_runs = {k: v for k, v in reorder_counts.items() if v}
    say(f"  runs where sorting by time changed row order: {len(moved_runs)}/{len(run_meta)}")
    for k, v in sorted(moved_runs.items()):
        say(f"      {k:<32} {v} of {run_meta[k]['n_steps']} positions")
    say("")
    say("  If this is empty, file order already was execution order -- but it is")
    say("  the timestamp that guarantees it, which is why D1 sorts explicitly.")

    head("REPEATED EXECUTIONS KEPT (D2)")
    rep = [s for s in steps if s["n_occurrences"] > 1]
    say(f"  rows belonging to a repeated (run, event_id): {len(rep)}")
    bykey = collections.Counter((s["run"], s["event_id"]) for s in rep)
    say(f"  distinct repeated keys: {len(bykey)}")
    for (run, ev), c in sorted(bykey.items())[:12]:
        ex = [s for s in rep if s["run"] == run and s["event_id"] == ev]
        gaps = [round(ex[i + 1]["start"] - ex[i]["start"], 1)
                for i in range(len(ex) - 1)]
        say(f"      {run:<30} ev {ev:<4} x{c}  cmd={ex[0]['cmd'][:16]:<16} "
            f"gaps={gaps}s")
    say("")
    say("  Non-zero gaps confirm separate executions rather than duplicate rows.")

    head("SCENARIO BALANCE — read before choosing a split")
    per_base = collections.Counter(s["base_scenario"] for s in steps)
    runs_base = collections.Counter(m["base_scenario"] for m in run_meta.values())
    say(f"  {'scenario':<10} {'runs':>5} {'steps':>7} {'share':>8}")
    for b in sorted(per_base):
        say(f"  S{b:<9} {runs_base[b]:>5} {per_base[b]:>7} "
            f"{100 * per_base[b] / len(steps):>7.1f}%")
    top = per_base.most_common(1)[0]
    say("")
    say(f"  >> S{top[0]} is {100 * top[1] / len(steps):.0f}% of all steps across "
        f"{runs_base[top[0]]} variants.")
    say("     Split by BASE SCENARIO. A variant-level split leaks the same")
    say("     campaign into train and test.")

    head("ZONES — carried, not derived (D4)")
    for b in sorted(runs_base):
        m = next(v for v in run_meta.values() if v["base_scenario"] == b)
        say(f"  S{b}  entry={str(m.get('entry_zone')):<12} "
            f"target={str(m.get('target_zone')):<12} "
            f"host={str(m.get('target_host')):<14} goal={m.get('goal_tactic')}")
    say("")
    if vol:
        say("  log-volume cross-check (corroborating only):")
        say(f"  {'run':<30} heaviest non-infrastructure hosts")
        for run in sorted(vol)[:40]:
            say(f"  {run:<30} "
                + "  ".join(f"{h}:{b / 1e3:.0f}KB" for h, b in vol[run][:3]))
    else:
        say("  no volume cross-check (pass --data to enable it).")

    head("WHAT IS DELIBERATELY NOT DONE HERE")
    say("  - no windows, no train/test split, no collapsing of repeats (D5)")
    say("  - zones and goals are NOT derived from the release (D4)")
    say("  - execution success is not inferred: the release records none")

    with open(os.path.join(a.out, "EXTRACT_REPORT.md"), "w", encoding="utf-8") as f:
        f.write("```\n" + "\n".join(log) + "\n```\n")
    print(f"\nwrote steps.jsonl, runs.json, vocab.json, EXTRACT_REPORT.md to {a.out}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
