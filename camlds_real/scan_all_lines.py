# -*- coding: utf-8 -*-
"""Read every byte of every file in the CAM-LDS archives. Run on the GPU PC.

    python camlds_real/scan_all_lines.py --data "C:\\Users\\user5\\Downloads\\DATASET 01"

Read-only on the archives. Nothing is sampled. Safe to stop and rerun: each finished archive is
saved in out/scan/parts/ and skipped next time.

For every file it decompresses all bytes, which also verifies the file's CRC-32. It records:
  LINE_SCAN.json         per archive and per kind of file: files, bytes, lines, binary files,
                         lines that are not valid UTF-8, longest line, empty files, CRC errors
  ATTACKMATE_ALL.jsonl   every record of the 34 scenario attackmate.json files, untouched
  MANIFEST_ATTACKMATE.json  for the manifestation copies: records not found in the scenario file
  FACTS_SUMMARY.csv      hostname, addresses and OS from all facts.json files, for all hosts
  LOG_TIME_RANGES.csv    per run and host: first and last timestamp in audit.log and eve.json
  SCAN_REPORT.txt        totals

Commit out/scan/ (the parts/ folder is ignored) and push, so the results can be read line by line.
"""
from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import json
import multiprocessing as mp
import os
import re
import sys
import time
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from deep_audit import classify  # noqa: E402

CHUNK = 1 << 20
AUDIT = re.compile(rb"audit\((\d{10})\.\d+:")
EVE = re.compile(rb'"timestamp":"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})')
CANON = re.compile(r"\s*\(\d+\)(?=\.zip$)", re.I)


def scenario_host(name):
    """'scenario_4/wazuh/logs/...' -> ('scenario_4', 'wazuh'), else None."""
    p = name.split("/")
    return (p[0], p[1]) if len(p) > 2 and p[0].startswith("scenario_") else None


def records(raw):
    """attackmate.json is a JSON document or JSON lines; returns (records, unparsable lines)."""
    txt = raw.decode("utf-8", "replace")
    try:
        o = json.loads(txt)
        return (o if isinstance(o, list) else [o]), 0
    except json.JSONDecodeError:
        out, bad = [], 0
        for ln in txt.splitlines():
            if ln.strip():
                try:
                    out.append(json.loads(ln))
                except json.JSONDecodeError:
                    bad += 1
        return out, bad


def facts_row(name, raw):
    host = scenario_host(name)
    try:
        o = json.loads(raw.decode("utf-8", "replace"))
    except json.JSONDecodeError as e:
        return {"path": name, "error": str(e)[:80]}
    f = o.get("ansible_facts", o) if isinstance(o, dict) else {}
    get = lambda k: f.get(k, f.get(k.replace("ansible_", ""), "")) if isinstance(f, dict) else ""  # noqa: E731
    dflt = get("ansible_default_ipv4")
    return {"path": name, "run": host[0] if host else "", "host": host[1] if host else "",
            "hostname": get("ansible_hostname"), "fqdn": get("ansible_fqdn"),
            "ipv4": " ".join(get("ansible_all_ipv4_addresses") or []),
            "default_ipv4": dflt.get("address", "") if isinstance(dflt, dict) else "",
            "os": f"{get('ansible_distribution')} {get('ansible_distribution_version')}",
            "n_keys": len(f) if isinstance(f, dict) else 0,
            "first_keys": " ".join(list(f)[:8]) if isinstance(f, dict) else ""}


def scan_file(zf, info, st, times):
    host = scenario_host(info.filename)
    base = os.path.basename(info.filename)
    rx = AUDIT if base == "audit.log" and host else EVE if base == "eve.json" and host else None
    keep = base in ("attackmate.json", "facts.json")
    buf, tail, binary, bad, longest, n = [], b"", False, 0, 0, 0
    with zf.open(info) as fh:                        # reading to EOF verifies the CRC
        while True:
            chunk = fh.read(CHUNK)
            if not chunk:
                break
            if keep:
                buf.append(chunk)
            n += chunk.count(b"\n")
            if b"\0" in chunk:
                binary = True
            data = tail + chunk
            cut = data.rfind(b"\n")
            head, tail = (data[:cut + 1], data[cut + 1:]) if cut >= 0 else (b"", data)
            if head:
                longest = max(longest, max(map(len, head.split(b"\n"))))
                if not binary:
                    try:
                        head.decode("utf-8")
                    except UnicodeDecodeError:
                        bad += sum(1 for ln in head.split(b"\n") if not _utf8(ln))
                if rx:
                    hits = rx.findall(head)
                    if hits:
                        times[(host, base)] = _range(times.get((host, base)), hits)
    if tail:
        n += 1
        longest = max(longest, len(tail))
        if not binary and not _utf8(tail):
            bad += 1
    st["lines"] += n
    st["binary_files"] += binary
    st["non_utf8_lines"] += bad
    st["longest_line"] = max(st["longest_line"], longest)
    return b"".join(buf) if keep else None


def _utf8(b):
    try:
        b.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False


def _range(old, hits):
    a, b = hits[0], hits[-1]
    vals = [a, b] if len(hits) < 3 else [min(hits), max(hits)]
    lo, hi, n = old or (vals[0], vals[1], 0)
    return min(lo, *vals), max(hi, *vals), n + len(hits)


def scan_archive(args):
    path, parts = args
    name = CANON.sub("", os.path.basename(path))
    out = os.path.join(parts, name + ".json")
    if os.path.exists(out):
        return name, 0.0
    t0 = time.time()
    cls = collections.defaultdict(lambda: dict(files=0, bytes=0, lines=0, binary_files=0, non_utf8_lines=0,
                                               longest_line=0, empty_files=0, crc_errors=0))
    res = {"archive": name, "attackmate": {}, "manifest_attackmate": [], "attackmate_bad_lines": {},
           "facts": [], "crc_errors": [], "times": {}}
    times = {}
    with zipfile.ZipFile(path) as zf:
        for info in zf.infolist():
            if info.filename.endswith("/"):
                continue
            st = cls[classify(info.filename)]
            st["files"] += 1
            st["bytes"] += info.file_size
            st["empty_files"] += info.file_size == 0
            try:
                raw = scan_file(zf, info, st, times)
            except Exception as e:  # noqa: BLE001 - a damaged file is a finding, not a crash
                st["crc_errors"] += 1
                res["crc_errors"].append([info.filename, str(e)[:120]])
                continue
            base = os.path.basename(info.filename)
            if base == "facts.json":
                res["facts"].append(facts_row(info.filename, raw))
            elif base == "attackmate.json":
                recs, bad = records(raw)
                if info.filename.startswith("scenario_"):
                    res["attackmate"][info.filename] = recs
                    res["attackmate_bad_lines"][info.filename] = bad
                else:
                    res["manifest_attackmate"].append(
                        [info.filename, [[r.get("start-datetime"), r.get("cmd")] for r in recs if isinstance(r, dict)]])
    res["classes"] = cls
    res["times"] = {f"{k[0][0]}|{k[0][1]}|{k[1]}": [v[0].decode(), v[1].decode(), v[2]] for k, v in times.items()}
    res["seconds"] = round(time.time() - t0)
    tmp = out + ".part"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(res, fh)
    os.replace(tmp, out)
    return name, time.time() - t0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", default=os.path.join(HERE, "out", "scan"))
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) // 2))
    a = ap.parse_args()
    parts = os.path.join(a.out, "parts")
    os.makedirs(parts, exist_ok=True)

    seen, jobs, dupes = {}, [], []
    for fn in sorted(os.listdir(a.data)):
        if fn.lower().endswith(".zip"):
            c = CANON.sub("", fn)
            if c in seen:
                dupes.append(fn)
            else:
                seen[c] = fn
                jobs.append((os.path.join(a.data, fn), parts))
    print(f"{len(jobs)} archives, {a.workers} workers; duplicates skipped: {dupes}", flush=True)
    t0 = time.time()
    with mp.Pool(a.workers) as pool:
        for i, (name, sec) in enumerate(pool.imap_unordered(scan_archive, jobs), 1):
            print(f"  [{i}/{len(jobs)}] {name}: {'already done' if sec == 0 else f'{sec:.0f}s'}", flush=True)

    done = [json.load(open(os.path.join(parts, f), encoding="utf-8")) for f in sorted(os.listdir(parts)) if f.endswith(".json")]
    tot = collections.Counter()
    for d in done:
        for c in d["classes"].values():
            for k in ("files", "bytes", "lines", "binary_files", "non_utf8_lines", "empty_files", "crc_errors"):
                tot[k] += c[k]
    with open(os.path.join(a.out, "LINE_SCAN.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump({d["archive"]: {"seconds": d["seconds"], "crc_errors": d["crc_errors"], "classes": d["classes"]}
                   for d in done}, fh, indent=0, sort_keys=True)

    n_am, keys = 0, set()
    with open(os.path.join(a.out, "ATTACKMATE_ALL.jsonl"), "w", encoding="utf-8", newline="\n") as fh:
        for d in done:
            for path, recs in sorted(d["attackmate"].items()):
                for i, r in enumerate(recs):
                    fh.write(json.dumps({"path": path, "index": i, "record": r}, sort_keys=True) + "\n")
                    n_am += 1
                    if isinstance(r, dict):
                        keys.add((r.get("start-datetime"), r.get("cmd")))
    nf, nr, missing = 0, 0, []
    for d in done:
        for path, recs in d["manifest_attackmate"]:
            nf += 1
            for r in recs:
                nr += 1
                if (r[0], r[1]) not in keys:
                    missing.append([path, r[0], (r[1] or "")[:120]])
    with open(os.path.join(a.out, "MANIFEST_ATTACKMATE.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"files": nf, "records": nr, "not_in_scenario_file": len(missing), "examples": missing[:200]}, fh, indent=0)

    facts = sorted((r for d in done for r in d["facts"]), key=lambda r: r["path"])
    cols = ["path", "run", "host", "hostname", "fqdn", "ipv4", "default_ipv4", "os", "n_keys", "first_keys", "error"]
    with open(os.path.join(a.out, "FACTS_SUMMARY.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(facts)
    with open(os.path.join(a.out, "LOG_TIME_RANGES.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["run", "host", "log", "first", "last", "stamped_lines"])
        for d in done:
            for k, v in sorted(d["times"].items()):
                w.writerow(k.split("|") + v)

    crc = [e for d in done for e in d["crc_errors"]]
    lines = [f"CAM-LDS full line scan, finished {dt.datetime.now().isoformat(timespec='seconds')}, {time.time() - t0:.0f}s",
             f"archives scanned      : {len(done)} (duplicates skipped: {dupes})",
             f"files read            : {tot['files']:,}",
             f"bytes read            : {tot['bytes']:,}",
             f"lines read            : {tot['lines']:,}",
             f"binary files (NUL)    : {tot['binary_files']:,}",
             f"empty files           : {tot['empty_files']:,}",
             f"non-UTF-8 lines       : {tot['non_utf8_lines']:,}",
             f"CRC or read errors    : {len(crc)}",
             f"attackmate records    : {n_am:,} in {sum(len(d['attackmate']) for d in done)} scenario files",
             f"attackmate bad lines  : {sum(sum(d['attackmate_bad_lines'].values()) for d in done)}",
             f"manifest attackmate   : {nf:,} files, {nr:,} records, {len(missing):,} not in a scenario file",
             f"facts.json summarised : {len(facts)}"]
    txt = "\n".join(lines + [f"  {e[0]}: {e[1]}" for e in crc[:50]]) + "\n"
    with open(os.path.join(a.out, "SCAN_REPORT.txt"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(txt)
    print("\n" + txt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
