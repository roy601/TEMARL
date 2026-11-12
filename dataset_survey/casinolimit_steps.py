# -*- coding: utf-8 -*-
"""CasinoLimit: rebuild every attacker's labelled steps, in time order, and measure them.

    python dataset_survey/casinolimit_steps.py

Reads (from dataset_survey/data/casinolimit/, downloaded by survey.py; nothing is changed):
  * output.zip   output/system_labels/<instance>.json   the reviewed technique labels
                 output/steps.csv                       how far each player got in the challenge
  * syslogs.zip  syslogs/<instance>/<machine>/audit.log  the raw auditd logs

A label says: technique T, seen in auditd events "<serial>-<machine>". This script finds each of
those events in that instance's audit.log on that machine (every line is read), takes its time and
the command line (PROCTITLE, else EXECVE, else exe), and orders the labels by time. Then it reports,
per instance and in total: number of steps, machines touched, machine switches (moves between
zones), techniques, how often a step repeats a technique already seen (our "copy" points), who
labelled it (automatic rule or a human reviewer), and every label whose events could not be found.

Writes dataset_survey/out/casinolimit_steps/: REPORT.txt, instances.csv, steps.csv, report.json.
Standard library only.
"""
from __future__ import annotations

import argparse
import collections
import csv
import io
import json
import os
import re
import statistics as st
import sys
import time
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from survey import mask  # noqa: E402  (same masking of long tokens as the survey reports)

AUDIT = re.compile(rb"msg=audit\((\d+(?:\.\d+)?):(\d+)\)")
FIELD = re.compile(rb'(\w+)=("[^"]*"|\S+)')
# machine key used in the labels -> how its folder in syslogs.zip starts
MACHINES = {"start": "start", "intranet": "intranet", "meet": "meetingcam", "bastion": "bastion"}
SAME_EVENT_SECONDS = 2.0      # one serial seen at times further apart than this = two different events


def machine_of(folder: str) -> str | None:
    for key, prefix in MACHINES.items():
        if folder.startswith(prefix):
            return key
    return None


def decode_hex(v: bytes) -> str:
    v = v.strip(b'"')
    if len(v) % 2 == 0 and re.fullmatch(rb"[0-9A-Fa-f]+", v or b"x"):
        try:
            return bytes.fromhex(v.decode()).replace(b"\x00", b" ").decode("utf-8", "replace").strip()
        except ValueError:
            pass
    return v.decode("utf-8", "replace")


def load_labels(output_zip: str):
    z = zipfile.ZipFile(output_zip)
    labels, problems = {}, []
    for name in sorted(z.namelist()):
        if not (name.startswith("output/system_labels/") and name.endswith(".json")):
            continue
        inst = os.path.basename(name)[:-5]
        rows = []
        for lid, v in json.loads(z.read(name)).items():
            events = []
            for uid in v.get("event_uids", []):
                serial, _, mach = uid.partition("-")
                if not serial.isdigit() or mach not in MACHINES:
                    problems.append(f"{inst}: label {lid} has an event id I cannot read: {uid!r}")
                    continue
                events.append((mach, int(serial)))
            if v.get("instance_name", inst) != inst:
                problems.append(f"{inst}: label {lid} names instance {v.get('instance_name')!r}")
            rows.append({"id": lid, "technique": v["technique"], "events": events,
                         "by": sorted({b[0] for b in v.get("labelled_by", [])}),
                         "rejected": bool(v.get("rejected_by")), "doubt": bool(v.get("doubt"))})
        labels[inst] = rows
    progress = {}
    with z.open("output/steps.csv") as fh:
        for r in csv.DictReader(io.TextIOWrapper(fh, encoding="utf-8")):
            progress[r["instance"]] = int(r["step_count"])
    return labels, progress, problems


def scan_audit(syslogs_zip: str, wanted: dict, say):
    """wanted[(inst, mach)] = set of serials. Returns found[(inst, mach, serial)] = event dict, stats."""
    z = zipfile.ZipFile(syslogs_zip)
    found, stats = {}, collections.Counter()
    folders = collections.defaultdict(list)         # (inst, mach) -> audit files
    for info in z.infolist():
        parts = info.filename.split("/")
        if len(parts) == 4 and parts[0] == "syslogs" and parts[3].startswith("audit.log"):
            mach = machine_of(parts[2])
            if mach:
                folders[(parts[1], mach)].append(info)
            else:
                stats["audit files on an unknown machine"] += 1
    stats["audit files"] = sum(len(v) for v in folders.values())
    todo = sorted(k for k in folders if k in wanted)
    t0 = time.time()
    for i, key in enumerate(todo, 1):
        want = wanted[key]
        for info in folders[key]:
            stats["audit bytes"] += info.file_size
            with z.open(info) as fh:
                for line in fh:
                    stats["audit lines"] += 1
                    m = AUDIT.search(line)
                    if not m:
                        stats["audit lines without an event id"] += 1
                        continue
                    serial = int(m.group(2))
                    if serial not in want:
                        continue
                    ts = float(m.group(1))
                    ev = found.setdefault((*key, serial), {"t": ts, "t_max": ts, "proctitle": "", "execve": "",
                                                           "exe": "", "types": set(), "file": info.filename})
                    ev["t"], ev["t_max"] = min(ev["t"], ts), max(ev["t_max"], ts)
                    if ev["file"] != info.filename:
                        ev["in_two_files"] = True
                    rtype = line[5:line.find(b" ")] if line.startswith(b"type=") else b"?"
                    ev["types"].add(rtype.decode("ascii", "replace"))
                    body = line[m.end():]
                    if rtype == b"PROCTITLE":
                        f = dict(FIELD.findall(body))
                        if b"proctitle" in f:
                            ev["proctitle"] = decode_hex(f[b"proctitle"])
                    elif rtype == b"EXECVE":
                        args = [(int(k[1:]), decode_hex(v)) for k, v in FIELD.findall(body)
                                if k[:1] == b"a" and k[1:].isdigit()]
                        ev["execve"] = " ".join(a for _, a in sorted(args))
                    elif rtype == b"SYSCALL":
                        f = dict(FIELD.findall(body))
                        if b"exe" in f:
                            ev["exe"] = decode_hex(f[b"exe"])
        if i % 20 == 0 or i == len(todo):
            say(f"  read {i}/{len(todo)} machine logs, {stats['audit lines']:,} lines, {time.time() - t0:.0f} s")
    stats["machine logs read"] = len(todo)
    missing_logs = sorted(k for k in wanted if k not in folders)
    return found, stats, missing_logs


def describe(xs):
    if not xs:
        return "none"
    xs = sorted(xs)
    return f"min {xs[0]}, median {st.median(xs):g}, mean {st.mean(xs):.1f}, max {xs[-1]}"


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-dir", default=os.path.join(HERE, "data", "casinolimit"))
    ap.add_argument("--out", default=os.path.join(HERE, "out", "casinolimit_steps"))
    a = ap.parse_args()
    say = lambda s: print(s, flush=True)  # noqa: E731
    t_start = time.time()
    for f in ("output.zip", "syslogs.zip"):
        if not os.path.isfile(os.path.join(a.data_dir, f)):
            say(f"MISSING: {os.path.join(a.data_dir, f)}. Run first: python dataset_survey/survey.py --only casinolimit")
            return 1

    say("reading labels ...")
    labels, progress, problems = load_labels(os.path.join(a.data_dir, "output.zip"))
    wanted = collections.defaultdict(set)
    for inst, rows in labels.items():
        for r in rows:
            for mach, serial in r["events"]:
                wanted[(inst, mach)].add(serial)
    say(f"  {len(labels)} instances, {sum(map(len, labels.values())):,} labels, "
        f"{sum(map(len, wanted.values())):,} distinct events to find")

    say("reading every line of the audit logs that the labels point to ...")
    found, stats, missing_logs = scan_audit(os.path.join(a.data_dir, "syslogs.zip"), wanted, say)
    for inst, mach in missing_logs:
        problems.append(f"{inst}: labels point to machine {mach!r} but syslogs.zip has no audit.log for it")

    # ---- build the ordered steps
    steps, per_inst = [], []
    tot = collections.Counter()
    tech_all = collections.Counter()
    by_all = collections.Counter()
    n_cmd_total, labels_per_cmd, cmd_novel = [], [], [0]
    for inst in sorted(labels):
        rows = []
        for r in labels[inst]:
            evs = [found.get((inst, m, s)) for m, s in r["events"]]
            hit = [e for e in evs if e]
            tot["labels"] += 1
            tot["events"] += len(evs)
            tot["events found"] += len(hit)
            if r["rejected"]:
                tot["labels rejected by a reviewer"] += 1
            for e in hit:
                if e["t_max"] - e["t"] > SAME_EVENT_SECONDS or e.get("in_two_files"):
                    tot["events whose serial is not unique"] += 1
            if not hit:
                tot["labels with no event found"] += 1
                problems.append(f"{inst}: label {r['id']} ({r['technique']}) - none of its {len(evs)} events found")
                continue
            pairs = [(e["t"], m, s) for (m, s), e in zip(r["events"], evs) if e]
            t_first, m_first, s_first = min(pairs)
            first = found[(inst, m_first, s_first)]
            cmd = first["proctitle"] or first["execve"] or first["exe"]
            if not cmd:
                tot["steps without a command line"] += 1
            rows.append({"instance": inst, "time": first["t"], "first_event": f"{s_first}-{m_first}", "end": max(e["t_max"] for e in hit),
                         "machines": sorted({m for (m, s), e in zip(r["events"], evs) if e}),
                         "technique": r["technique"].split(":")[0].strip(), "technique_name": r["technique"],
                         "by": "+".join(r["by"]), "doubt": r["doubt"], "events": len(evs), "events_found": len(hit),
                         "command": mask(cmd, 300)})
        rows.sort(key=lambda x: (x["time"], x["first_event"], x["technique"]))
        # one command = the labels whose earliest event is the same auditd event (multi-label, like CAM-LDS)
        cmds, cseen, c_novel = [], set(), 0
        for x in rows:
            if not cmds or cmds[-1]["first_event"] != x["first_event"]:
                cmds.append({"first_event": x["first_event"], "labels": set()})
            cmds[-1]["labels"].add(x["technique"])
        for c in cmds:
            c_novel += bool(c["labels"] - cseen)
            cseen |= c["labels"]
        n_cmd_total.append(len(cmds))
        labels_per_cmd.extend(len(c["labels"]) for c in cmds)
        cmd_novel[0] += c_novel
        seen, prev_m, switches, copies, same_as_prev = set(), None, 0, 0, 0
        for k, x in enumerate(rows):
            x["order"] = k + 1
            x["seen_before"] = x["technique"] in seen
            copies += x["seen_before"]
            same_as_prev += k > 0 and x["technique"] == rows[k - 1]["technique"]
            seen.add(x["technique"])
            m = x["machines"][0]
            if prev_m is not None and m != prev_m:
                switches += 1
            prev_m = m
            tech_all[x["technique"]] += 1
            by_all[x["by"]] += 1
        steps += rows
        mach_order = []
        for x in rows:
            if not mach_order or mach_order[-1] != x["machines"][0]:
                mach_order.append(x["machines"][0])
        per_inst.append({"instance": inst, "labels": len(labels[inst]), "steps": len(rows), "commands": len(cmds),
                         "commands_with_a_new_technique": c_novel,
                         "techniques": len(seen), "machines": len({m for x in rows for m in x["machines"]}),
                         "machine_switches": switches, "machine_path": ">".join(mach_order)[:200],
                         "repeat_of_earlier": copies, "same_as_previous": same_as_prev,
                         "duration_min": round((rows[-1]["end"] - rows[0]["time"]) / 60, 1) if rows else 0,
                         "challenge_steps_reached": progress.get(inst, "")})
    tot["steps"] = len(steps)
    no_labels = sorted(i for i in progress if i not in labels)

    # ---- write
    os.makedirs(a.out, exist_ok=True)
    fields = ["instance", "order", "time", "first_event", "machines", "technique", "technique_name", "seen_before", "by", "doubt",
              "events", "events_found", "command"]
    with open(os.path.join(a.out, "steps.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fields, extrasaction="ignore")
        w.writeheader()
        for x in steps:
            w.writerow({**x, "time": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(x["time"])) + f".{int(x['time'] % 1 * 1000):03d}Z",
                        "machines": "+".join(x["machines"])})
    with open(os.path.join(a.out, "instances.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, list(per_inst[0]))
        w.writeheader()
        w.writerows(per_inst)

    S = [p["steps"] for p in per_inst]
    multi = [p for p in per_inst if p["machines"] > 1]
    n_copy = sum(p["repeat_of_earlier"] for p in per_inst)
    n_prev = sum(p["same_as_previous"] for p in per_inst)
    reach = collections.Counter(p["challenge_steps_reached"] for p in per_inst)
    L = []
    add = L.append
    add("CASINOLIMIT: THE LABELLED STEPS OF EVERY ATTACKER, IN TIME ORDER")
    add(f"Made by dataset_survey/casinolimit_steps.py on {time.strftime('%Y-%m-%d %H:%M')} in {time.time() - t_start:.0f} s. "
        "The dataset was not changed.")
    add("")
    add("1. WHAT WAS READ")
    add(f"   instances with a label file {len(labels)} | instances in steps.csv without one {len(no_labels)}")
    add(f"   labels {tot['labels']:,} | auditd events they point to {tot['events']:,} | found in the logs "
        f"{tot['events found']:,} ({100 * tot['events found'] / max(tot['events'], 1):.1f}%)")
    add(f"   audit files in syslogs.zip {stats['audit files']} | machine logs read {stats['machine logs read']} | "
        f"lines read {stats['audit lines']:,} | size {stats['audit bytes'] / 2**30:.1f} GB")
    add(f"   lines without an auditd event id {stats['audit lines without an event id']:,}")
    add("")
    add("2. CAN EVERY LABEL BE PLACED IN TIME?")
    add(f"   labels placed {tot['steps']:,} of {tot['labels']:,} | with no event found {tot['labels with no event found']:,}")
    add(f"   steps without a command line {tot['steps without a command line']:,} | "
        f"events whose serial is not unique {tot['events whose serial is not unique']:,} | rejected labels {tot['labels rejected by a reviewer']}")
    add("")
    add("3. HOW LONG IS ONE ATTACK? (steps = placed labels, per instance)")
    add(f"   {describe(S)}")
    for lo, hi in ((0, 0), (1, 9), (10, 29), (30, 99), (100, 10**9)):
        n = sum(lo <= s <= hi for s in S)
        add(f"   {lo:>4}-{'' if hi > 10**8 else hi:<5} steps: {n} instances")
    lpc = collections.Counter(min(n, 4) for n in labels_per_cmd)
    add(f"   COMMANDS (labels on the same auditd event merged into one multi-label step, as in CAM-LDS):")
    add(f"      commands {sum(n_cmd_total):,} | per instance {describe(n_cmd_total)}")
    add(f"      labels per command: " + ", ".join(f"{'4+' if k == 4 else k}: {v:,}" for k, v in sorted(lpc.items())))
    add(f"   minutes from first to last step: {describe([p['duration_min'] for p in per_inst if p['steps']])}")
    add("")
    add("4. ZONES: DOES THE ATTACKER MOVE BETWEEN MACHINES?")
    mc = collections.Counter(m for x in steps for m in x["machines"])
    add(f"   steps per machine: " + ", ".join(f"{k} {v:,}" for k, v in mc.most_common()))
    add(f"   instances touching 1/2/3/4 machines: " +
        " / ".join(str(sum(p['machines'] == k for p in per_inst)) for k in (1, 2, 3, 4)))
    add(f"   machine switches per instance: {describe([p['machine_switches'] for p in per_inst])}")
    paths = collections.Counter(p["machine_path"] for p in multi)
    add("   most common machine paths (instances with more than one machine):")
    for path, n in paths.most_common(10):
        add(f"      {n:>4}  {path}")
    add("")
    add("5. TECHNIQUES (the label set)")
    add(f"   distinct techniques {len(tech_all)} | per instance {describe([p['techniques'] for p in per_inst])}")
    add("   " + ", ".join(f"{k} {v}" for k, v in tech_all.most_common(30)))
    inst_per_tech = collections.Counter(t for _, t in {(x["instance"], x["technique"]) for x in steps})
    add(f"   techniques used by only 1 instance: {sum(v == 1 for v in inst_per_tech.values())} | "
        f"by 10 or more instances: {sum(v >= 10 for v in inst_per_tech.values())}")
    add("")
    add("6. REPEATS (compare: CAM-LDS 'copy' points)")
    add(f"   steps whose technique was already seen earlier in the same attack: {n_copy:,} of {len(steps):,} "
        f"({100 * n_copy / max(len(steps), 1):.1f}%)")
    add(f"   steps with the same technique as the step just before: {n_prev:,} ({100 * n_prev / max(len(steps), 1):.1f}%)")
    add(f"   commands that bring at least one technique not seen before in the attack ('novel'): "
        f"{cmd_novel[0]:,} of {sum(n_cmd_total):,} ({100 * cmd_novel[0] / max(sum(n_cmd_total), 1):.1f}%)")
    add("")
    add("7. WHO LABELLED THE STEPS")
    for k, v in by_all.most_common():
        add(f"   {k or '(nobody recorded)':<40} {v:,}")
    add(f"   marked 'doubt' by a reviewer: {sum(x['doubt'] for x in steps):,}")
    add("")
    add("8. HOW FAR PLAYERS GOT IN THE CHALLENGE (step_count in output/steps.csv, instances with labels)")
    add("   " + ", ".join(f"{k} steps: {v}" for k, v in sorted(reach.items(), key=lambda kv: str(kv[0]))))
    add("")
    add("9. EXAMPLE: THE LONGEST ATTACK THAT USES THE MOST MACHINES (first 25 steps)")
    if per_inst:
        best = max(per_inst, key=lambda p: (p["machines"], p["steps"]))
        add(f"   instance {best['instance']}: {best['steps']} steps, {best['machines']} machines, path {best['machine_path']}")
        for x in [x for x in steps if x["instance"] == best["instance"]][:25]:
            add(f"   {x['order']:>4} {time.strftime('%H:%M:%S', time.gmtime(x['time']))} {'+'.join(x['machines']):<10} "
                f"{x['technique']:<10} {mask(x['command'], 90)}")
    add("")
    add("10. PROBLEMS")
    if no_labels:
        add(f"   instances in steps.csv with no label file ({len(no_labels)}): {', '.join(no_labels)}")
    for p in problems[:200]:
        add(f"   {p}")
    if len(problems) > 200:
        add(f"   ... and {len(problems) - 200} more (all in report.json)")
    if not problems and not no_labels:
        add("   none")
    text = "\n".join(L) + "\n"
    with open(os.path.join(a.out, "REPORT.txt"), "w", encoding="utf-8") as fh:
        fh.write(text)
    with open(os.path.join(a.out, "report.json"), "w", encoding="utf-8") as fh:
        json.dump({"totals": dict(tot), "scan": dict(stats), "techniques": dict(tech_all.most_common()),
                   "labelled_by": dict(by_all), "instances": per_inst, "problems": problems,
                   "instances_without_labels": no_labels}, fh, indent=1)
    say(text)
    say(f"written: {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
