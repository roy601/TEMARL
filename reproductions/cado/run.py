# -*- coding: utf-8 -*-
"""CADO (Future Internet 2026): rerun the authors' released simulator and analysis, unchanged, and compare
with the published tables. DECISIONS.md. Run with any Python 3.9+ (standard library only); the authors'
code runs in the venv of README.md (Python 3.13.5 and the authors' pins).

    python reproductions/cado/fetch.py          # unpack and check the supplement (external/s1)
    python reproductions/cado/run.py check      # venv versions == the authors' pins -> out/ENVIRONMENT.json
    python reproductions/cado/run.py run        # simulate afresh, then the authors' analysis on OUR episodes
    python reproductions/cado/run.py report     # TARGETS.csv vs ours -> REPORT.md, out/results.json, out/HASHES.txt
    python reproductions/cado/run.py recheck    # second machine: the whole run again, scientific hashes compared

What `run` does (DECISIONS 5-7):
  1. a working copy of S1 (external/work_fresh): the authors' code/reproduce_submitted.py simulates every
     experiment afresh into reproduced_results/ and checks it against their archived results (1e-12).
  2. a second working copy (external/work_table4) whose submitted_results/ CSVs are REPLACED by step 1's
     fresh ones: the authors' code/revision_analysis.py then computes the held-out analysis (Table 4) from
     our episodes. (As released, it reads the authors' archived episodes, so running it unchanged would not
     reproduce Table 4 from a fresh simulation.)
  3. outputs copied to out/fresh and out/revision; timing columns are never compared (host-dependent).
`run` never overwrites out/fresh; a second run goes through `recheck`.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXT = HERE / "external"
S1 = EXT / "s1"
VENV = EXT / "venv"
VPY = VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
OUT = HERE / "out"
PY_VERSION = "3.13.5"                                          # the authors' experiment_config.json
PINS = {"numpy": "2.1.3", "pandas": "2.2.3", "scipy": "1.15.3", "matplotlib": "3.10.0"}   # their requirements.txt
REVISION_OUTPUTS = ("sensitivity_settings.json", "default_episode_reanalysis.csv", "reproduction_validation.json",
                    "sensitivity_seed_metrics.csv", "sensitivity_paired_comparisons.csv",
                    "primary_heldout_consensus_paired.csv", "heldout_paired_statistical_comparisons.csv",
                    "heldout_summary_statistics.csv", "revision_environment.json")
POLICIES = ("Static", "Adaptive", "Consensus", "CADO")
METRICS = ("utility", "redirection_precision", "engagement_rate", "benign_false_redirect_rate",
           "unsafe_action_rate", "normalized_cost")


# ── pure helpers (tested) ─────────────────────────────────────────────────────

def is_timing(file_name: str, column: str) -> bool:
    """The authors' own exclusion rule (code/reproduce_submitted.py): host timings are never compared."""
    c = column.lower()
    if any(k in c for k in ("latency", "throughput", "elapsed", "records_s")):
        return True
    return file_name == "normalization_benchmark.csv" and any(k in column for k in ("_us", "_ms", "seconds"))


def read_csv(path: Path) -> list:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def as_float(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def scientific_sha256(path: Path) -> str:
    """SHA-256 of a CSV without its timing columns, rows joined with LF: equal on two machines if and only
    if every scientific value is byte-identical."""
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    keep = [i for i, c in enumerate(rows[0]) if not is_timing(path.name, c)]
    text = "\n".join(",".join(r[i] for i in keep) for r in rows) + "\n"
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def compare_csv(ours: Path, theirs: Path) -> dict:
    """Cell-by-cell comparison with the authors' archived file (timing columns excluded)."""
    a, b = read_csv(theirs), read_csv(ours)
    if len(a) != len(b) or (a and list(a[0]) != list(b[0])):
        return {"file": ours.name, "same_shape": False}
    cols = [c for c in (a[0] if a else []) if not is_timing(ours.name, c)]
    worst, text_diff = {}, []
    for c in cols:
        x = [as_float(r[c]) for r in a]
        y = [as_float(r[c]) for r in b]
        if all(v is not None for v in x + y):
            d = [abs(p - q) for p, q in zip(x, y) if not (math.isnan(p) and math.isnan(q))]
            worst[c] = max(d, default=0.0)
        elif [r[c] for r in a] != [r[c] for r in b]:
            text_diff.append(c)
    return {"file": ours.name, "same_shape": True, "rows": len(a), "max_abs_difference": worst,
            "text_columns_different": text_diff,
            "within_1e-12": not text_diff and all(v <= 1e-12 for v in worst.values())}


def decimals(published: str) -> int:
    s = published.strip()
    return len(s.split(".")[1]) if "." in s else 0


def verdict(ours: float, published: str) -> str:
    """Deterministic method (DECISIONS 9): MATCH if ours rounds to the printed value (within half a unit of
    the last printed digit), CLOSE if within one unit, else NO MATCH."""
    half = 0.5 * 10 ** (-decimals(published))
    d = abs(ours - float(published))
    if d <= half + 1e-12:
        return "MATCH"
    if d <= 2 * half + 1e-12:
        return "CLOSE"
    return "NO MATCH"


def lookup(target_id: str, out: Path = OUT):
    """Our value for a target id (DECISIONS 8), or None if the id names nothing we compute.
    T2.<policy>.<metric>.<mean|ci_low|ci_high>   primary summary (out/fresh/summary_statistics.csv)
    T4.<Consensus|CADO>.<metric>.<stat>           held-out summary (out/revision/heldout_summary_statistics.csv)
    T4.diff.<metric>.<mean_difference|ci_low|ci_high|p_holm|effect_size_dz>   CADO - Consensus, held out"""
    p = target_id.split(".")
    if p[0] == "T2" and len(p) == 4:
        rows = read_csv(out / "fresh" / "summary_statistics.csv")
        hit = [r for r in rows if r["dataset"] == "primary" and r["policy"] == p[1] and r["metric"] == p[2]]
    elif p[0] == "T4" and p[1] == "diff" and len(p) == 4:
        rows = read_csv(out / "revision" / "heldout_paired_statistical_comparisons.csv")
        hit = [r for r in rows if r["comparison"] == "CADO - Consensus" and r["metric"] == p[2]]
    elif p[0] == "T4" and len(p) == 4:
        rows = read_csv(out / "revision" / "heldout_summary_statistics.csv")
        hit = [r for r in rows if r["policy"] == p[1] and r["metric"] == p[2]]
    else:
        return None
    if len(hit) != 1 or p[3] not in hit[0]:
        raise SystemExit(f"target {target_id}: {len(hit)} matching rows or no column {p[3]}")
    return float(hit[0][p[3]])


def sha_lf(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def write_hashes(out: Path = OUT) -> dict:
    files = sorted((p for p in out.rglob("*") if p.is_file() and p.name != "HASHES.txt"),
                   key=lambda p: p.relative_to(out).as_posix())
    h = {p.relative_to(out).as_posix(): sha_lf(p) for p in files}
    (out / "HASHES.txt").write_bytes("".join(f"{v}  {k}\n" for k, v in h.items()).encode("utf-8"))
    return h


def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1), encoding="utf-8")


# ── environment and run (call the venv) ──────────────────────────────────────

def venv_versions() -> dict:
    if not VPY.exists():
        raise SystemExit(f"no venv at {VENV}: see README.md")
    code = ("import json,sys,platform,importlib.metadata as m;"
            "print(json.dumps({'python':sys.version,'platform':platform.platform(),"
            "'packages':sorted(f\"{d.metadata['Name']}=={d.version}\" for d in m.distributions())}))")
    return json.loads(subprocess.run([str(VPY), "-c", code], capture_output=True, text=True, check=True).stdout)


def stage_check(out: Path = OUT) -> dict:
    sys.path.insert(0, str(HERE))
    import fetch
    bad = fetch.check()
    v = venv_versions()
    have = {p.split("==")[0].lower(): p.split("==")[1] for p in v["packages"]}
    bad += [f"{k} {have.get(k)} installed, the authors pin {want}" for k, want in PINS.items() if have.get(k) != want]
    if not v["python"].startswith(PY_VERSION + " "):
        bad.append(f"Python {v['python'].split()[0]}, the authors used {PY_VERSION}")
    if bad:
        raise SystemExit("check FAILED:\n  " + "\n  ".join(bad))
    env = {**v, "machine": platform.node(), "s1_zip_sha256": fetch.ZIP_SHA256, "pins_ok": True}
    write_json(out / "ENVIRONMENT.json", env)
    print(f"check OK: Python {v['python'].split()[0]}, " + ", ".join(f"{k} {have[k]}" for k in PINS) +
          f"; S1 unchanged ({fetch.ZIP_SHA256[:12]}...)")
    return env


def authors_script(work: Path, script: str, log: Path) -> dict:
    env = dict(os.environ, MPLBACKEND="Agg", PYTHONIOENCODING="utf-8")
    log.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    with log.open("w", encoding="utf-8") as fh:
        rc = subprocess.run([str(VPY), script], cwd=str(work), stdout=fh, stderr=subprocess.STDOUT, env=env).returncode
    print(f"  {script} in {work.name}: exit {rc} after {(time.time() - t0) / 60:.1f} min (log {log.name})", flush=True)
    return {"script": script, "exit_code": rc, "minutes": round((time.time() - t0) / 60, 2), "log": log.name}


def pipeline(out: Path, tag: str) -> dict:
    """Steps 1-3 of the module docstring, into `out` (fresh/, revision/, logs/, RUN.json)."""
    fresh, t4 = EXT / f"work_fresh{tag}", EXT / f"work_table4{tag}"
    for w in (fresh, t4):
        if w.exists():
            shutil.rmtree(w)                                   # our own scratch copies of S1
        shutil.copytree(S1, w)
    start = time.time()
    steps = [authors_script(fresh, "code/reproduce_submitted.py", out / "logs" / "reproduce_submitted.log")]
    produced = sorted((fresh / "reproduced_results").glob("*"))
    if not any(p.name == "summary_statistics.csv" for p in produced):
        raise SystemExit("the fresh simulation wrote no summary_statistics.csv: see the log")
    for p in produced:                                       # step 2: our episodes in place of the archived ones
        if (t4 / "submitted_results" / p.name).exists():
            shutil.copy2(p, t4 / "submitted_results" / p.name)
    steps.append(authors_script(t4, "code/revision_analysis.py", out / "logs" / "revision_analysis.log"))
    (out / "fresh").mkdir(parents=True, exist_ok=True)
    (out / "revision").mkdir(parents=True, exist_ok=True)
    for p in produced:
        shutil.copy2(p, out / "fresh" / p.name)
    stale = []
    for name in REVISION_OUTPUTS:
        p = t4 / "revision_results" / name
        if not p.exists() or p.stat().st_mtime < start:
            stale.append(name)
        else:
            shutil.copy2(p, out / "revision" / name)
    run = {"machine": platform.node(), "steps": steps, "fresh_files": [p.name for p in produced],
           "revision_files_not_regenerated": stale}
    archived = [compare_csv(out / "fresh" / p.name, S1 / "submitted_results" / p.name)
                for p in produced if p.suffix == ".csv" and (S1 / "submitted_results" / p.name).exists()]
    archived += [compare_csv(out / "revision" / n, S1 / "revision_results" / n)
                 for n in REVISION_OUTPUTS if n.endswith(".csv") and (out / "revision" / n).exists()
                 and (S1 / "revision_results" / n).exists()]
    write_json(out / "ARCHIVE_COMPARISON.json", archived)
    write_json(out / "SCIENTIFIC_SHA256.json",
               {f"{d}/{p.name}": scientific_sha256(p) for d in ("fresh", "revision")
                for p in sorted((out / d).glob("*.csv"))})
    write_json(out / "RUN.json", run)
    return run


def targets_committed() -> bool:
    """Requirement 1: TARGETS.csv and DECISIONS.md are committed and unchanged since."""
    def git(*a):
        return subprocess.run(["git", *a], cwd=str(HERE), capture_output=True, text=True).stdout.strip()
    names = ("TARGETS.csv", "DECISIONS.md")
    return all(git("log", "-1", "--format=%H", "--", n) for n in names) and not git("status", "--porcelain", "--", *names)


def stage_run():
    if (OUT / "fresh").exists():
        raise SystemExit("out/fresh exists: results are never overwritten (use `recheck`)")
    if not targets_committed():
        raise SystemExit("TARGETS.csv and DECISIONS.md must be committed, unchanged, before the first run")
    stage_check()
    run = pipeline(OUT, "")
    print("run finished:", json.dumps({s["script"]: s["exit_code"] for s in run["steps"]}),
          "| not regenerated:", run["revision_files_not_regenerated"] or "none")
    print("next: python reproductions/cado/run.py report")


def stage_recheck():
    if not (OUT / "SCIENTIFIC_SHA256.json").exists():
        raise SystemExit("no first run to compare with")
    tmp = EXT / "recheck_out"
    if tmp.exists():
        shutil.rmtree(tmp)
    stage_check(tmp)
    pipeline(tmp, "_recheck")
    a = json.loads((OUT / "SCIENTIFIC_SHA256.json").read_text(encoding="utf-8"))
    b = json.loads((tmp / "SCIENTIFIC_SHA256.json").read_text(encoding="utf-8"))
    diff = sorted(k for k in a.keys() | b.keys() if a.get(k) != b.get(k))
    dest = OUT / f"RECHECK_{platform.node()}.json"
    write_json(dest, {"machine": platform.node(), "files": len(a), "identical": not diff, "different": diff,
                      "environment": {k: v for k, v in json.loads((tmp / "ENVIRONMENT.json").read_text(
                          encoding="utf-8")).items() if k != "packages"}})
    print(f"recheck on {platform.node()}: {'IDENTICAL' if not diff else 'DIFFERENT ' + str(diff)} "
          f"({len(a)} scientific files) -> {dest.name}")


# ── report (pure) ─────────────────────────────────────────────────────────────

def stage_report(out: Path = OUT, dest: Path = HERE / "REPORT.md"):
    raise SystemExit("report is written after TARGETS.csv is committed (requirement 1)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=["check", "run", "report", "recheck"])
    a = ap.parse_args()
    {"check": stage_check, "run": stage_run, "report": stage_report, "recheck": stage_recheck}[a.stage]()


if __name__ == "__main__":
    main()
