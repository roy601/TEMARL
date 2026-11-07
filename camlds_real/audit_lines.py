# -*- coding: utf-8 -*-
"""Row-by-row audit of attack_times.csv and of the extracted corpus built from it.

    python camlds_real/audit_lines.py --attack-new <enterprise-attack.json> --attack-v11 <...json>

Every row and every field is tested. Read-only: it changes no data file and uses no model
output. The two ATT&CK bundles are the official MITRE STIX files (mitre/cti release tags).
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import re
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = ["scenario", "tactics", "techniques", "technique_names", "event_id", "cmd", "start", "end"]
STRICT = re.compile(r"^T\d{4}(\.\d{3})?$")
RUN = re.compile(r"^([1-7])(_[a-z0-9_]+)?$")


def head(s):
    print(f"\n{'=' * 78}\n{s}\n{'=' * 78}")


def attack(path):
    """id -> (status, tactics), tactic names longest first."""
    objs = json.load(open(path, encoding="utf-8"))["objects"]
    out, tactics = {}, set()
    for o in objs:
        if o["type"] == "x-mitre-tactic":
            tactics.add(o["x_mitre_shortname"])
        if o["type"] == "attack-pattern":
            tid = next((r["external_id"] for r in o.get("external_references", [])
                        if r.get("source_name") == "mitre-attack"), None)
            st = "revoked" if o.get("revoked") else "deprecated" if o.get("x_mitre_deprecated") else "live"
            ts = [k["phase_name"] for k in o.get("kill_chain_phases", []) if k.get("kill_chain_name") == "mitre-attack"]
            if tid not in out or st == "live":
                out[tid] = (st, ts, o.get("name"))
    return out, sorted(tactics, key=len, reverse=True)


def split_tactics(cell, names):
    """Greedy parse of the concatenated tactics cell; returns (parts, leftover)."""
    parts, rest = [], cell.replace("_", "")   # the separator is sometimes "_", sometimes nothing
    while rest:
        for n in names:
            if rest.startswith(n):
                parts.append(n)
                rest = rest[len(n):]
                break
        else:
            return parts, rest
    return parts, ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--attack-new", required=True)
    ap.add_argument("--attack-v11", required=True)
    a = ap.parse_args()
    new, names_new = attack(a.attack_new)
    v11, names_v11 = attack(a.attack_v11)
    # newer releases renamed tactics, so the cell can only be parsed with both name lists
    tnames = sorted(set(names_new) | set(names_v11), key=len, reverse=True)

    raw = open(os.path.join(HERE, "attack_times.csv"), "rb").read()
    head("A. FILE LEVEL")
    print(f"  bytes {len(raw):,} | BOM {raw[:3] == bytes([239, 187, 191])} | CRLF lines {raw.count(b'\r\n')} "
          f"| non-ASCII bytes {sum(b > 127 for b in raw)} | double quotes {raw.count(b'\"')}")
    lines = raw.decode("utf-8").splitlines()
    print(f"  lines {len(lines)} (header + {len(lines) - 1} rows) | header ok {lines[0].split(';') == FIELDS}")

    rows, bad_fields = [], []
    for i, ln in enumerate(lines[1:]):
        p = ln.split(";")
        if len(p) != len(FIELDS):
            bad_fields.append((i, len(p), ln[:100]))
            continue
        rows.append({"i": i, **dict(zip(FIELDS, p))})
    print(f"  rows with wrong field count: {len(bad_fields)} {bad_fields[:5]}")
    print(f"  fully duplicated rows: {len(lines) - 1 - len(set(lines[1:]))}")

    head("B. EVERY FIELD OF EVERY ROW")
    P = collections.Counter()
    ex = collections.defaultdict(list)

    def flag(k, r, note=""):
        P[k] += 1
        if len(ex[k]) < 6:
            ex[k].append(f"row {r['i']} {r['scenario']} ev{r['event_id']} {note}")

    tok_c = collections.Counter()
    for r in rows:
        for f in FIELDS:
            v = r[f]
            if v == "":
                flag(f"empty:{f}", r)
            if v != v.strip():
                flag(f"whitespace:{f}", r)
        if not RUN.match(r["scenario"]):
            flag("bad run name", r, r["scenario"])
        if not r["event_id"].isdigit():
            flag("event_id not integer", r, r["event_id"])
        if r["technique_names"] != "NA":
            flag("technique_names not NA", r, r["technique_names"][:40])
        try:
            s, e = float(r["start"]), float(r["end"])
            r["s"], r["e"] = s, e
            if e < s:
                flag("end before start", r, f"{s} {e}")
            if e == s:
                flag("end equals start", r)
            if float(r["end"]).is_integer():
                P["end is a whole second"] += 1
            if float(r["start"]).is_integer():
                P["start is a whole second"] += 1
        except ValueError:
            flag("timestamp not numeric", r, r["start"] + " " + r["end"])
        toks = r["techniques"].split("_")
        r["toks"] = toks
        for t in toks:
            tok_c[t] += 1
            if not STRICT.match(t):
                flag("MALFORMED technique token", r, repr(t) + " in " + r["techniques"])
            else:
                st = new.get(t)
                if st is None:
                    flag(f"technique absent from latest ATT&CK", r, t)
                elif st[0] != "live":
                    flag(f"technique {st[0]} in latest ATT&CK", r, t)
                if t not in v11:
                    flag("technique absent from ATT&CK v11", r, t)
                elif v11[t][0] != "live":
                    flag(f"technique {v11[t][0]} in ATT&CK v11", r, t)
        if len(set(toks)) != len(toks):
            flag("same technique twice in one row", r, r["techniques"])
        if len({t.split('.')[0] for t in toks}) != len(toks):
            P["two labels share a parent"] += 1
        parts, left = split_tactics(r["tactics"], tnames)
        r["tacs"] = parts
        if left:
            flag("tactics cell not parseable", r, repr(left))
        else:
            # the cell lists tactics for the row, not one per technique
            known = {x for t in toks for src in (new, v11) for x in (src.get(t) or (0, []))[1]}
            for tac in parts:
                if tac not in known:
                    flag("tactic belongs to no technique of the row in ATT&CK", r, f"{tac} / {r['techniques']}")
            for t in toks:
                own = {x for src in (new, v11) for x in (src.get(t) or (0, []))[1]}
                if not own & set(parts):
                    flag("technique has none of the row's tactics in ATT&CK", r, f"{t} {sorted(own)} / {r['tactics']}")
    for k, v in sorted(P.items()):
        print(f"  {v:>5}  {k}")
        for e in ex[k]:
            print(f"         {e}")
    print(f"  distinct technique tokens: {len(tok_c)} | parent tokens: {len({t.split('.')[0] for t in tok_c})}"
          f" | instances: {sum(tok_c.values())}")

    head("C. TIME ORDER WITHIN EACH RUN")
    runs = collections.defaultdict(list)
    for r in rows:
        runs[r["scenario"]].append(r)
    print(f"  runs {len(runs)} | steps per run min {min(map(len, runs.values()))} max {max(map(len, runs.values()))}")
    dur, gaps, overlap, dupstart = [], [], 0, 0
    for name, ss in runs.items():
        ss.sort(key=lambda r: r["s"])
        dupstart += len(ss) - len({r["s"] for r in ss})
        for x, y in zip(ss, ss[1:]):
            g = y["s"] - x["e"]
            gaps.append(g)
            if g < 0:
                overlap += 1
                print(f"  overlap: {name} ev{x['event_id']}->ev{y['event_id']} {g:.2f}s")
        dur += [r["e"] - r["s"] for r in ss]
    print(f"  duplicate starts {dupstart} | overlaps {overlap}")
    print(f"  duration s: median {statistics.median(dur):.1f} max {max(dur):.0f} | gap s: median {statistics.median(gaps):.1f} max {max(gaps):.0f}")
    days = sorted({int(r["s"] // 86400) for r in rows})
    print(f"  start-time span: {days[0]} .. {days[-1]} (days since epoch), {len(days)} distinct days")

    head("D. LABEL CONSISTENCY: same command, different labels")
    by_cmd = collections.defaultdict(collections.Counter)
    for r in rows:
        by_cmd[r["cmd"]][tuple(sorted(r["toks"]))] += 1
    print(f"  distinct commands {len(by_cmd)}")
    conflict = {c: v for c, v in by_cmd.items() if len(v) > 1}
    print(f"  commands carrying more than one label set: {len(conflict)}, covering {sum(sum(v.values()) for v in conflict.values())} rows")
    for c, v in sorted(conflict.items(), key=lambda kv: -sum(kv[1].values()))[:40]:
        print(f"    {c[:60]:<60} {dict(v)}")
    by_key = collections.defaultdict(lambda: collections.defaultdict(set))
    for r in rows:
        base = r["scenario"].split("_")[0]
        by_key[base][r["event_id"]].add((r["cmd"], tuple(sorted(r["toks"]))))
    n = sum(1 for b in by_key.values() for e in b.values() if len(e) > 1)
    print(f"  (scenario, event_id) with different content across variants: {n} of {sum(len(b) for b in by_key.values())}")

    head("E. EXTRACTED CORPUS vs SOURCE, ROW BY ROW")
    steps = [json.loads(x) for x in open(os.path.join(HERE, "out", "steps.jsonl"), encoding="utf-8")]
    by_row = {s["source_row"]: s for s in steps}
    mism = collections.Counter()
    for r in rows:
        s = by_row.get(r["i"])
        if s is None:
            mism["missing"] += 1
            continue
        if s["techniques_sub"] != r["toks"]:
            mism["techniques_sub"] += 1
        if s["techniques_parent"] != sorted({t.split('.')[0] for t in r["toks"]}):
            mism["techniques_parent"] += 1
        if s["run"] != r["scenario"]:
            mism["run"] += 1
        if s["cmd"] != r["cmd"]:
            mism["cmd"] += 1
        if float(s["start"]) != r["s"]:
            mism["start"] += 1
        if str(s["event_id"]) != r["event_id"]:
            mism["event_id"] += 1
    print(f"  source rows {len(rows)} | corpus steps {len(steps)} | mismatches {dict(mism) or 'none'}")
    order = sum(1 for k, ss in runs.items()
                if [r["i"] for r in ss] != [s["source_row"] for s in sorted((s for s in steps if s["run"] == k), key=lambda s: s["exec_index"])])
    print(f"  runs whose exec_index order differs from time order: {order}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
