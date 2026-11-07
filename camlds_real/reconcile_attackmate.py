# -*- coding: utf-8 -*-
"""Match every labelled step to its attackmate.json record, and summarise the full line scan.

    python camlds_real/reconcile_attackmate.py --out camlds_real/out/ATTACKMATE_RECONCILE.txt

Inputs: out/steps.jsonl and out/scan/*. Read-only on all of them. No model output is used, and no
test metric is computed. Writes only the --out report.

Matching rule: the record's start-datetime, read as UTC, in whole microseconds. A step matches
when its CSV start equals the record time minus 2 s, which is how the authors build `start`
(extract_attack_logs.py:583). A step that fails is matched on identical microseconds within the
run, which reveals one of their manual window changes (fix_time_start, same file). Each record
may be used once.
"""
from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import json
import os
import re
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
US = 1_000_000
USUAL = 2 * US
EPOCH = dt.datetime(1970, 1, 1)
# records that run or configure the playbook, or prepare something on the attacker's side
CONTROL = {"sleep", "mktemp", "setvar", "include", "msf-payload", "webserv", "debug", "father"}


def usec_iso(s):
    d = dt.datetime.fromisoformat(s) - EPOCH
    return d.days * 86400 * US + d.seconds * US + d.microseconds


def usec_float(x):
    return round(x * US)


def norm_tactic(s):
    return re.sub(r"[^a-z]", "", s.lower())


def meta(rec):
    return (rec["record"].get("parameters") or {}).get("metadata") or {}


def techs(rec):
    m = meta(rec)
    v = m.get("techniques")
    return [t.strip() for t in str(v).split(",") if t.strip()] if v else []


def load():
    steps = [json.loads(x) for x in open(os.path.join(HERE, "out", "steps.jsonl"), encoding="utf-8")]
    recs = [json.loads(x) for x in open(os.path.join(HERE, "out", "scan", "ATTACKMATE_ALL.jsonl"), encoding="utf-8")]
    by = collections.defaultdict(list)
    for r in recs:
        r["t"] = usec_iso(r["record"]["start-datetime"])
        by[r["path"].split("/")[0][len("scenario_"):]].append(r)
    for v in by.values():
        v.sort(key=lambda r: r["index"])
    return steps, recs, by


def join(steps, by):
    """source_row -> record, list of shifted steps. Exact matches are taken first, so that a
    microsecond collision (S5) cannot steal a record."""
    pairs, used, left = {}, set(), []
    for s in steps:
        want = usec_float(s["start"]) + USUAL
        hit = [r for r in by[s["run"]] if r["t"] == want and id(r) not in used]
        if len(hit) == 1:
            pairs[s["source_row"]] = hit[0]
            used.add(id(hit[0]))
        else:
            left.append(s)
    shifted = []
    for s in left:
        us = usec_float(s["start"]) % US
        hit = [r for r in by[s["run"]] if r["t"] % US == us and id(r) not in used]
        if len(hit) == 1:
            pairs[s["source_row"]] = hit[0]
            used.add(id(hit[0]))
            shifted.append(s)
    return pairs, shifted, used


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    a = ap.parse_args()
    log = []

    def say(*x):
        log.append(" ".join(str(i) for i in x))

    steps, recs, by = load()
    pairs, shifted, used = join(steps, by)
    say("A. JOIN")
    say(f"  labelled steps {len(steps)} | attackmate records {len(recs)} | runs {len(by)}")
    say(f"  steps matched {len(pairs)} | unmatched {len(steps) - len(pairs)} | records used twice "
        f"{len(pairs) - len({id(r) for r in pairs.values()})}")
    say(f"  matched at exactly -2 s: {len(pairs) - len(shifted)} | matched with another shift: {len(shifted)}")
    for s in sorted(shifted, key=lambda s: (s["run"], s["start"])):
        r = pairs[s["source_row"]]
        sh = (usec_float(s["start"]) + USUAL - r["t"]) / US
        say(f"    {s['run']:<26} ev{s['event_id']:<3} rec#{r['index']:<4} CSV time moved {sh:+.0f} s "
            f"meta={ {k: v for k, v in meta(r).items() if k not in ('technique_name', 'tactics')} }")

    say("\nB. LABELS: attack_times.csv vs attackmate metadata, row by row")
    same, order, diff = 0, 0, []
    tac_ok, tac_bad = 0, []
    for s in steps:
        r = pairs[s["source_row"]]
        c, m = s["techniques_sub"], techs(r)
        if c == m:
            same += 1
        elif sorted(c) == sorted(m):
            order += 1
        else:
            diff.append((s["run"], s["event_id"], c, m))
        mt = meta(r).get("tactics") or meta(r).get("tactic") or ""
        want = "".join(norm_tactic(x) for x in re.split(r"[,_]", str(mt)))
        if norm_tactic(s["tactics_raw"]) == want:
            tac_ok += 1
        else:
            tac_bad.append((s["run"], s["event_id"], s["tactics_raw"], mt))
    say(f"  techniques identical, same order: {same} | same set, other order: {order} | different: {len(diff)}")
    for d in diff[:30]:
        say("   ", d)
    say(f"  tactics cell equals metadata text: {tac_ok} | differs: {len(tac_bad)}")
    pat = collections.Counter((b[2], str(b[3])) for b in tac_bad)
    for k, v in pat.most_common(12):
        say(f"    x{v}  {k}")

    say("\nC. RECORDS WITH TECHNIQUES THAT ARE NOT IN attack_times.csv")
    extra = [r for r in recs if techs(r) and id(r) not in used]
    say(f"  {len(extra)} records")
    for r in extra:
        say(f"    {r['path'].split('/')[0]:<38} rec#{r['index']:<4} {r['record']['type']:<12} "
            f"{r['record']['cmd'][:50]!r} {techs(r)}")

    say("\nD. RECORDS NOT IN attack_times.csv, BY TYPE")
    rest = [r for r in recs if id(r) not in used]
    say(f"  {len(rest)} records (1,806 - {len(pairs)})")
    allc = collections.Counter(r["record"]["type"] for r in recs)
    usedc = collections.Counter(r["record"]["type"] for r in recs if id(r) in used)
    for t, n in allc.most_common():
        say(f"    {t:<16} all {n:>4} | labelled {usedc[t]:>4} | unlabelled {n - usedc[t]:>4}")
    keys = collections.Counter(k for r in rest for k in meta(r))
    say(f"  metadata keys on unlabelled records: {dict(keys)}")

    say("\nE. ORDER: CSV start time vs attackmate execution order")
    bad_runs, moved, adj_bad, adj = {}, 0, 0, 0
    for run, ss in sorted(collections.defaultdict(list, {k: [s for s in steps if s["run"] == k] for k in by}).items()):
        t = sorted(ss, key=lambda s: s["exec_index"])
        idx = [pairs[s["source_row"]]["index"] for s in t]
        want = sorted(idx)
        adj += len(idx) - 1
        adj_bad += sum(x > y for x, y in zip(idx, idx[1:]))
        d = sum(x != y for x, y in zip(idx, want))
        if d:
            bad_runs[run] = d
            moved += d
    say(f"  runs in a different order: {len(bad_runs)} of {len(by)} | steps at a different position: {moved}"
        f" | adjacent pairs reversed: {adj_bad} of {adj}")
    for k, v in bad_runs.items():
        say(f"    {k:<26} {v} steps")

    say("\nF. DELAYED-MANIFESTATION AND OTHER METADATA")
    for r in recs:
        m = meta(r)
        if "delayed_manifestation" in m:
            s = next((s for s in steps if pairs[s["source_row"]] is r), None)
            ev = f"ev{s['event_id']}" if s else "not in CSV"
            say(f"    {r['path'].split('/')[0]:<38} rec#{r['index']:<4} {ev:<10} {r['record']['cmd'][:40]!r} "
                f"delayed={m['delayed_manifestation']!r} techniques={m.get('techniques')}")
    odd = collections.Counter(k for r in recs for k in meta(r)
                              if k not in ("techniques", "tactics", "technique_name", "action", "description",
                                           "delayed_manifestation"))
    say(f"  other keys: {dict(odd)}")

    say("\nG. HOSTS REACHED BY COMMAND, PER SCENARIO (parameters.hostname, parameters.target)")
    host = collections.defaultdict(collections.Counter)
    for run, rs in by.items():
        for r in rs:
            p = r["record"].get("parameters") or {}
            for k in ("hostname", "jmp_hostname"):
                if p.get(k):
                    host[run.split("_")[0]][f"{k}={p[k]}"] += 1
    for k in sorted(host):
        say(f"  S{k}: {host[k].most_common(10)}")

    say("\nH. HOW MUCH OF THE TIMING IS SCRIPTED")
    span, slept, n_pairs, n_sleep, gaps = 0.0, 0.0, 0, 0, []
    for rs in by.values():
        sv = [float(r["record"]["parameters"].get("seconds") or 0) if r["record"]["type"] == "sleep" else 0.0
              for r in rs]
        span += (rs[-1]["t"] - rs[0]["t"]) / US
        slept += sum(sv)
        lab = [i for i, r in enumerate(rs) if id(r) in used]
        for x, y in zip(lab, lab[1:]):
            n_pairs += 1
            n_sleep += sum(sv[x:y]) > 0
            gaps.append((rs[y]["t"] - rs[x]["t"]) / US)
    rnd = collections.Counter(str(r["record"]["parameters"].get("random")) for r in recs
                              if r["record"]["type"] == "sleep")
    say(f"  attack time {span:,.0f} s | scripted sleep {slept:,.0f} s ({slept / span:.1%}) | random sleeps {dict(rnd)}")
    say(f"  labelled neighbours {n_pairs} | with a sleep between them {n_sleep} ({n_sleep / n_pairs:.1%})")
    say(f"  gap between labelled steps, execution order: median {statistics.median(gaps):.1f} s, max {max(gaps):,.0f} s")

    say("\nI. UNLABELLED RECORDS, PER SCENARIO")
    tab = collections.defaultdict(collections.Counter)
    for run, rs in by.items():
        b = "S" + run.split("_")[0]
        for r in rs:
            k = "labelled" if id(r) in used else "control" if r["record"]["type"] in CONTROL else "interactive"
            tab[b][k] += 1
    for b in sorted(tab):
        say(f"  {b}: records {sum(tab[b].values()):>4} | labelled {tab[b]['labelled']:>3} | "
            f"interactive {tab[b]['interactive']:>3} | control {tab[b]['control']:>3}")
    tt = sum(tab.values(), collections.Counter())
    say(f"  all: labelled {tt['labelled']} | interactive {tt['interactive']} | control {tt['control']}")

    say("\nJ. RAW FILES, BY FILE NAME (LINE_SCAN.json)")
    scan = json.load(open(os.path.join(HERE, "out", "scan", "LINE_SCAN.json"), encoding="utf-8"))
    names = collections.defaultdict(collections.Counter)
    for d in scan.values():
        for k, c in d["classes"].items():
            names[os.path.basename(k.rstrip("/"))].update(
                {x: c[x] for x in ("files", "bytes", "lines", "binary_files", "non_utf8_lines")})
    bad = collections.Counter()
    for n, c in names.items():
        bad["compose.ISO-8859-*.inc" if n.startswith("compose.ISO-8859") else n] += c["non_utf8_lines"]
    say(f"  non-UTF-8 lines {sum(bad.values()):,}: { {k: v for k, v in bad.most_common() if v} }")
    say(f"  non-UTF-8 lines in names that include a binary file: "
        f"{sum(c['non_utf8_lines'] for c in names.values() if c['binary_files'])}")
    say("  most lines: " + ", ".join(f"{k} {c['lines']:,}" for k, c in
                                     sorted(names.items(), key=lambda kv: -kv[1]["lines"])[:5]))

    say("\nK. HOSTS (FACTS_SUMMARY.csv)")
    facts = list(csv.DictReader(open(os.path.join(HERE, "out", "scan", "FACTS_SUMMARY.csv"), encoding="utf-8")))
    say(f"  files {len(facts)} | parse errors {sum(bool(r.get('error')) for r in facts)}")
    per = collections.defaultdict(set)
    for r in facts:
        per["S" + r["run"].split("_")[1]].add(r["host"])
    for b in sorted(per):
        say(f"  {b}: {sorted(per[b])}")
    for r in facts:
        if r["host"] == "attacker" and r["default_ipv4"] != "192.42.1.174":
            say(f"  attacker elsewhere: {r['run']} {r['default_ipv4']}")
    fw = next(r for r in facts if r["host"] == "inetfw")
    say(f"  inetfw addresses: {sorted(fw['ipv4'].split())}")

    say("\nL. DO THE LOGS COVER EACH ATTACK? (first and last stamp only; gaps inside are not tested)")
    win = {}
    for s in steps:
        w = win.setdefault(s["run"], [s["start"], s["end"]])
        w[0], w[1] = min(w[0], s["start"]), max(w[1], s["end"])

    def stamp(t):
        return int(t) if t.isdigit() else dt.datetime.fromisoformat(t).replace(tzinfo=dt.timezone.utc).timestamp()

    rows = list(csv.DictReader(open(os.path.join(HERE, "out", "scan", "LOG_TIME_RANGES.csv"), encoding="utf-8")))
    ok = sum(stamp(t["first"]) <= win[t["run"][len("scenario_"):]][0]
             and stamp(t["last"]) >= win[t["run"][len("scenario_"):]][1] for t in rows)
    say(f"  log ranges {len(rows)} | cover the whole attack {ok} | do not {len(rows) - ok}")

    txt = "\n".join(log) + "\n"
    if a.out:
        with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(txt)
    print(txt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
