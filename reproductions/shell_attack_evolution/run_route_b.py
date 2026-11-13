# -*- coding: utf-8 -*-
"""Route B (DECISIONS.md 18-29): run the authors' own 2024 pipeline, unchanged, on the released raw logs.

    pip install pandas openpyxl matplotlib networkx          # once; the authors' scripts need them
    python reproductions/shell_attack_evolution/run_route_b.py
    python reproductions/shell_attack_evolution/run_route_b.py --limit-files 3   # smoke test, NOT a result

1. Uses the same download as route A (commit d5f7fe1).
2. Copies the authors' analysis/period_2024/*.py unchanged into data/route_b/period_2024/ and extracts
   the 236 raw 2024 Cowrie files into its data/cowrie/ (about 1.7 GB; nothing is changed).
3. Runs, each as its own process with MPLBACKEND=Agg and nothing else changed:
     00 the read-raw-logs block of 01_extract_sessions.py (commented out in the release; run as written,
        only the leading "# " removed), then 01, 02, 03, 04, 05, 07a, 07b.
   A failed step is recorded with its error; later steps are NOT ATTEMPTED; nothing is patched.
4. Scores the 2024 targets with the route A primary definitions on the rebuilt data, compares rebuilt
   and released sessions by attacker IP, and labels every command with the authors' own tables.
5. Writes out_route_b/ (smoke: out_route_b_smoke/): results_route_b.json, REPORT_TABLE_ROUTE_B.md,
   per_command_labels.jsonl, HASHES.txt, ENVIRONMENT.json, steps.json. Full step logs stay in data/.
"""
from __future__ import annotations

import argparse
import ast
import contextlib
import csv
import json
import os
import platform
import re
import runpy
import shutil
import subprocess
import sys
import time
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run as R  # noqa: E402  (route A: download, definitions, verdicts)

STEPS = ["01_extract_sessions.py", "02_command_frequency.py", "03_classify_commands.py",
         "04_complex_command_patterns.py", "05_cluster_sessions.py", "07a_map_attack_techniques.py",
         "07b_technique_frequency.py"]
NEEDED = ("pandas", "openpyxl", "matplotlib", "networkx", "numpy")
COMPLEX = re.compile(r"[;|&><()]")          # the test 07a uses to tell complex from simple


# ── preparation ──────────────────────────────────────────────────────────────

def check_libraries():
    missing = []
    for m in NEEDED:
        try:
            __import__(m)
        except ImportError:
            missing.append(m)
    if missing:
        raise SystemExit(f"The authors' scripts need: {' '.join(missing)}. Run once:  pip install {' '.join(missing)}")


def prepare(zpath, work, limit, say):
    """Copy the 2024 scripts unchanged and extract the raw logs. Returns the list of raw files used."""
    z = zipfile.ZipFile(zpath)
    root = z.namelist()[0].split("/")[0]
    scripts = sorted(n for n in z.namelist() if n.startswith(f"{root}/analysis/period_2024/") and n.endswith(".py")
                     and n.count("/") == 3)
    raws = sorted(n for n in z.namelist() if n.startswith(f"{root}/2024/cowrie/") and not n.endswith("/"))
    if limit:
        raws = raws[:limit]
    os.makedirs(os.path.join(work, "data", "cowrie"), exist_ok=True)
    for n in scripts:
        with open(os.path.join(work, os.path.basename(n)), "wb") as fh:
            fh.write(z.read(n))
    have = set(os.listdir(os.path.join(work, "data", "cowrie")))
    want = {os.path.basename(n) for n in raws}
    for extra in sorted(have - want):                                  # a different file set from an earlier run
        os.remove(os.path.join(work, "data", "cowrie", extra))
    for i, n in enumerate(raws, 1):
        dest = os.path.join(work, "data", "cowrie", os.path.basename(n))
        if os.path.exists(dest) and os.path.getsize(dest) == z.getinfo(n).file_size:
            continue
        with z.open(n) as src, open(dest, "wb") as fh:
            shutil.copyfileobj(src, fh, 1 << 20)
        if i % 40 == 0:
            say(f"  extracted {i}/{len(raws)} raw files")
    return [os.path.basename(n) for n in raws], [os.path.basename(n) for n in scripts]


def step00_source(work):
    """The authors' read-raw-logs block, uncommented exactly (decision 19)."""
    src = open(os.path.join(work, "01_extract_sessions.py"), encoding="utf-8").read().splitlines()
    head = []
    for line in src:                                                   # imports and the Config block, as in 01
        if line.startswith("# The block below reads"):
            break
        if line.startswith(("import ", "from ", "DATA_DIR", "RAW_ROOT")):
            head.append(line)
    start = next(i for i, l in enumerate(src) if l.startswith("# def read_dataset():"))
    end = next(i for i, l in enumerate(src) if "port_filterd.to_csv" in l)
    block = []
    for line in src[start:end + 1]:
        if not line.startswith("#"):
            raise SystemExit(f"unexpected uncommented line inside the block: {line!r}")
        block.append(line[2:] if line.startswith("# ") else line[1:])
    return "\n".join(head + [""] + block) + "\n"


def run_steps(work, logs, say):
    env = {**os.environ, "MPLBACKEND": "Agg", "PYTHONIOENCODING": "utf-8"}
    status, records_loaded, authors_07b = [], None, None
    with open(os.path.join(work, "_step00_read_raw_logs.py"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(step00_source(work))
    for name in ["_step00_read_raw_logs.py", *STEPS]:
        if status and status[-1]["status"] != "ok":
            status.append({"step": name, "status": "NOT ATTEMPTED (an earlier step failed)"})
            continue
        say(f"  running {name} ...")
        t0 = time.time()
        p = subprocess.run([sys.executable, name], cwd=work, env=env, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        with open(os.path.join(logs, name + ".log"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(p.stdout + "\n--- stderr ---\n" + p.stderr)
        ok = p.returncode == 0
        status.append({"step": name, "status": "ok" if ok else "FAILED", "seconds": round(time.time() - t0, 1),
                       "error_tail": None if ok else p.stderr.strip().splitlines()[-3:]})
        if ok and name.startswith("_step00"):
            ints = [l.strip() for l in p.stdout.splitlines() if l.strip().isdigit()]
            records_loaded = int(ints[-1]) if ints else None             # the block prints len(merged_df)
        if ok and name.startswith("07b"):
            dicts = [l for l in p.stdout.splitlines() if l.startswith("{")]
            authors_07b = ast.literal_eval(dicts[-1]) if dicts else None
    return status, records_loaded, authors_07b


# ── measures on the rebuilt data ─────────────────────────────────────────────

def load(work, name):
    with open(os.path.join(work, "data", name), encoding="utf-8") as fh:
        return json.load(fh)


def rebuilt_sessions(work):
    """One record per rebuilt session, in the route A format (decisions 22-24)."""
    session_dict = load(work, "session_dict.json")
    groups = load(work, "5-session归类.json")
    techs = load(work, "7-session_tech_no_dup.json")
    out = []
    for pattern, members in groups.items():
        for ip, cmds in members.items():
            out.append({"session_id": ip, "src_ip": ip, "commands": cmds, "command_count": len(cmds),
                        "session_pattern": pattern, "attack_techniques": techs.get(pattern, [])})
    out.sort(key=lambda s: s["session_id"])
    return session_dict, out


def commands_frequency(work):
    c = load(work, "2-sorted_cmd_counter.json")
    items = c.items() if isinstance(c, dict) else c
    return [{"command": k, "frequency": int(v), "command_pattern": None} for k, v in items]


def compare_released(zpath, rebuilt):
    """Decision 28: rebuilt vs released 2024 sessions, by attacker IP."""
    data, _ = R.read_inputs(zpath)
    rel = {s["src_ip"]: s for s in data[("sessions", "2024")]}
    reb = {s["src_ip"]: s for s in rebuilt}
    both = sorted(set(rel) & set(reb))
    same_cmd = sum(rel[i]["commands"] == reb[i]["commands"] for i in both)
    same_tech = sum(R.tech_ids(rel[i]) == R.tech_ids(reb[i]) for i in both)
    return {"released_sessions": len(rel), "rebuilt_sessions": len(reb), "ips_in_both": len(both),
            "ips_only_released": len(set(rel) - set(reb)), "ips_only_rebuilt": len(set(reb) - set(rel)),
            "identical_command_lists": same_cmd, "identical_technique_sequences": same_tech,
            "identical_command_lists_share": same_cmd / len(both) if both else None,
            "identical_technique_sequences_share": same_tech / len(both) if both else None}


def per_command_labels(work, rebuilt, logs):
    """Decision 29: the authors' tables, applied per command exactly as 07a's loop does."""
    os.environ["MPLBACKEND"] = "Agg"
    cwd = os.getcwd()
    try:
        os.chdir(work)
        with open(os.path.join(logs, "per_command_runpy.log"), "w", encoding="utf-8") as fh, \
                contextlib.redirect_stdout(fh):
            g05 = runpy.run_path(os.path.join(work, "05_cluster_sessions.py"))
            g07 = runpy.run_path(os.path.join(work, "07a_map_attack_techniques.py"))
    finally:
        os.chdir(cwd)
    to_pattern, simple, compound = g05["command_to_pattern"], g07["simple_commands_attck"], g07["compound_pattern_mapped_attck"]
    rows, n_cmd, n_labelled = [], 0, 0
    for s in rebuilt:
        labels = []
        for cmd in s["commands"]:
            pat = to_pattern(cmd)
            if COMPLEX.search(pat):
                tech = list(compound.get(pat, []))
            else:
                tech = next(([k] for k, v in simple.items() if pat in v), [])
            ids = [m.group(0) for t in tech for m in [R.TECH_ID.search(str(t))] if m]
            labels.append({"command": cmd, "pattern": pat, "techniques": ids})
            n_cmd += 1
            n_labelled += bool(ids)
        rows.append({"src_ip": s["src_ip"], "labels": labels})
    return rows, {"commands": n_cmd, "commands_with_a_technique": n_labelled,
                  "share_with_a_technique": n_labelled / n_cmd if n_cmd else None,
                  "distinct_techniques": sorted({t for r in rows for x in r["labels"] for t in x["techniques"]})}


# ── scoring ──────────────────────────────────────────────────────────────────

def score(targets, M, records_loaded, authors_07b_share):
    rows = []
    for r in targets:
        tid, tol = r["id"], r["tolerance"]
        period = tid.split(".")[-1]
        alts, note = {}, ""
        if period != "2024":
            ours, note = None, "2021-2022 raw logs not obtainable (DECISIONS.md 18)"
        elif tid.startswith("S4B."):
            ours, note = None, "no Ubuntu list or computation in the release (DECISIONS.md 27)"
        elif tid == "T1.attacks.2024":
            ours = records_loaded
        else:
            ours, alts = R.ours_for(tid, r["quantity"], {"2024": M})
            if tid.startswith("T7.") and authors_07b_share is not None:
                alts["authors_07b"] = authors_07b_share.get(tid.split(".")[1], 0.0)
        v, diff, why = R.verdict(r["published"], ours, tol.replace(" (route B)", ""))
        rows.append({**r, "ours": ours, "difference": diff, "verdict": v, "note": note or why, "alternates": alts})
    return rows


def escape(x):
    return R.fmt(x).replace("|", "\\|")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=None)
    ap.add_argument("--data-dir", default=os.path.join(HERE, "data"))
    ap.add_argument("--limit-files", type=int, default=0, help="smoke test on the first N raw files; NOT a result")
    a = ap.parse_args()
    say = lambda s: print(s, flush=True)  # noqa: E731
    check_libraries()
    out = a.out or os.path.join(HERE, "out_route_b_smoke" if a.limit_files else "out_route_b")
    zpath = os.path.join(a.data_dir, R.ZIP_NAME)
    say(f"authors' repository at {R.COMMIT[:7]}: {R.download(zpath, say)}")
    work = os.path.join(a.data_dir, "route_b_smoke" if a.limit_files else "route_b", "period_2024")
    logs = os.path.join(os.path.dirname(work), "logs")
    os.makedirs(logs, exist_ok=True)
    for f in os.listdir(os.path.join(work, "data")) if os.path.isdir(os.path.join(work, "data")) else []:
        if os.path.isfile(os.path.join(work, "data", f)):
            os.remove(os.path.join(work, "data", f))                    # start every run from the raw logs
    raws, scripts = prepare(zpath, work, a.limit_files, say)
    say(f"  {len(raws)} raw files, {len(scripts)} scripts copied unchanged")
    status, records_loaded, authors_07b = run_steps(work, logs, say)
    result = {"commit": R.COMMIT, "smoke": bool(a.limit_files), "raw_files": len(raws), "steps": status,
              "records_loaded": records_loaded}
    os.makedirs(out, exist_ok=True)
    if all(s["status"] == "ok" for s in status):
        session_dict, rebuilt = rebuilt_sessions(work)
        cmds = commands_frequency(work)
        M = {"sessions": R.session_measures(rebuilt), "techniques": R.technique_measures(rebuilt),
             "commands": R.command_measures(cmds)}
        tot = sum(authors_07b.values()) if authors_07b else 0
        a07 = {}
        if tot:
            for k, v in authors_07b.items():
                m = R.TECH_ID.search(str(k))
                if m:
                    a07[m.group(0)] = a07.get(m.group(0), 0.0) + 100.0 * v / tot
        with open(os.path.join(HERE, "TARGETS.csv"), encoding="utf-8", newline="") as fh:
            targets = list(csv.DictReader(fh))
        rows = score(targets, M, records_loaded, a07 or None)
        labels, label_summary = per_command_labels(work, rebuilt, logs)
        result.update({"session_dict_entries": len(session_dict), "measures_2024": M,
                       "authors_07b_counts": authors_07b, "authors_07b_share": a07,
                       "released_vs_rebuilt": compare_released(zpath, rebuilt),
                       "per_command_labels": label_summary, "targets": rows,
                       "verdict_counts": dict(sorted(R.collections.Counter(x["verdict"] for x in rows).items()))})
        with open(os.path.join(out, "per_command_labels.jsonl"), "w", encoding="utf-8", newline="\n") as fh:
            for r in labels:
                fh.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
        T = ["| id | quantity | published | ours | difference | verdict |", "|---|---|---|---|---|---|"]
        T += [f"| {x['id']} | {escape(x['quantity'])} | {escape(x['published'])} | {escape(x['ours'])} | "
              f"{escape(x['difference'])} | {x['verdict']} |" for x in rows]
        with open(os.path.join(out, "REPORT_TABLE_ROUTE_B.md"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(T) + "\n")
    with open(os.path.join(out, "results_route_b.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(result, fh, indent=1, ensure_ascii=False, sort_keys=True, default=str)
    det = {k: v for k, v in result.items() if k != "steps"}               # step timings differ between machines
    det["steps"] = [{k: v for k, v in s.items() if k != "seconds"} for s in status]
    with open(os.path.join(out, "steps.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(status, fh, indent=1)
    hashes = [f"{R.sha256_bytes(json.dumps(det, ensure_ascii=False, sort_keys=True, default=str).encode())}  results_route_b.json (without step timings)"]
    for f in ("REPORT_TABLE_ROUTE_B.md", "per_command_labels.jsonl"):
        if os.path.exists(os.path.join(out, f)):
            hashes.append(f"{R.sha256_file(os.path.join(out, f))}  {f}")
    with open(os.path.join(out, "HASHES.txt"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(hashes) + "\n")
    libs = {m: __import__(m).__version__ for m in NEEDED}
    rc = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=HERE)
    with open(os.path.join(out, "ENVIRONMENT.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"made": time.strftime("%Y-%m-%d %H:%M"), "python": sys.version.split()[0], "platform": platform.platform(),
                   "libraries": libs, "repository_commit": rc.stdout.strip()}, fh, indent=1)
    say("\nsteps: " + ", ".join(f"{s['step']} {s['status']}" for s in status))
    if "verdict_counts" in result:
        say(f"verdicts: {result['verdict_counts']}")
    say(f"written: {out}" + ("   SMOKE TEST: NOT A RESULT" if a.limit_files else ""))
    return 0 if all(s["status"] == "ok" for s in status) else 1


if __name__ == "__main__":
    sys.exit(main())
