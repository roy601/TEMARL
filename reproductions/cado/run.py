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
PROTOTYPE_OUTPUTS = ("poc_summary.json", "poc_trials.csv", "poc_http_requests.jsonl", "poc_state_journal.jsonl",
                     "poc_workflow_example.json")
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
    """Printed decimals; for 3.35e-8 the last printed digit is 1e-10, so 10."""
    s = published.strip().lower()
    exp = 0
    if "e" in s:
        s, e = s.split("e")
        exp = int(e)
    return max(0, (len(s.split(".")[1]) if "." in s else 0) - exp)


def verdict(ours, published: str, tolerance: str = "") -> str:
    """Deterministic method (DECISIONS 9): MATCH if ours rounds to the printed value (within half a unit of
    the last printed digit), CLOSE if within one unit, else NO MATCH. Counts and 'all' claims: exact."""
    if tolerance.strip().lower().startswith("not attempted"):
        return "NOT ATTEMPTED"
    d = abs(ours - float(published))
    if tolerance.strip().lower().startswith("exact"):
        return "MATCH" if d <= 1e-12 else "NO MATCH"
    half = 0.5 * 10 ** (-decimals(published))
    if d <= half + 1e-12:
        return "MATCH"
    if d <= 2 * half + 1e-12:
        return "CLOSE"
    return "NO MATCH"


def one(rows: list, target_id: str, column: str, **where) -> float:
    hit = [r for r in rows if all(r[k] == v for k, v in where.items())]
    if len(hit) != 1 or column not in hit[0]:
        raise SystemExit(f"target {target_id}: {len(hit)} rows match {where} or no column {column}")
    return float(hit[0][column])


def mean(values) -> float:
    v = list(values)
    return sum(v) / len(v)


def lookup(target_id: str, out: Path = OUT):
    """Our value for a target id (DECISIONS 8 and 15), or None for an id with no computed value (timings).
    T2.<policy>.<metric>.<mean|ci_low|ci_high>          Table 2: fresh/summary_statistics.csv, primary
    T3.<primary|ood>.<variant>.<column>                 Table 3: Consensus from the primary or held-out summary,
                                                          CADO variants from fresh/ablation_summary.csv
    T4.<Consensus|CADO>.<metric>.<stat>                 Table 4: revision/heldout_summary_statistics.csv
    T4.diff.<metric>.<stat>                             Table 4: revision/heldout_paired_..., CADO - Consensus
    T5.<family>.<primary_utility|ood_utility|primary_unsafe|settings>.<min|max|n>
                                                        Table 5: revision/sensitivity_paired_comparisons.csv
    T6.<case>.<passed|restored>                         Table 6: prototype/poc_summary.json
    S51.<metric>.<stat>                                 Section 5.1: fresh/paired_statistical_comparisons.csv
    S52.gate.<column> | S52.ood_fallback.<stat> | S52.ood_unsafe.<policy>   Section 5.2
    S54.ood_fallback.<min|max>                          Section 5.4: revision/sensitivity_seed_metrics.csv
    S55.rollback.<policy> | S55.persistence.<policy> | S55.prototype.<key>  Section 5.5
    S56.recovery.<format> | S56.records.total           Section 5.6: fresh/normalization_benchmark.csv
    S44.validation.<episode_rows|scalar_decisions>      Section 4.4: revision/reproduction_validation.json
    TIME.*                                              host timings: None (NOT ATTEMPTED, DECISIONS 7)"""
    p = target_id.split(".")
    fresh, rev, proto = out / "fresh", out / "revision", out / "prototype"
    if p[0] == "TIME":
        return None
    if p[0] == "T2":
        return one(read_csv(fresh / "summary_statistics.csv"), target_id, p[3], dataset="primary", policy=p[1], metric=p[2])
    if p[0] == "T3":
        if p[2] == "Consensus" and p[1] == "primary":
            return one(read_csv(fresh / "summary_statistics.csv"), target_id, "mean", dataset="primary",
                       policy="Consensus", metric=p[3])
        if p[2] == "Consensus":
            return one(read_csv(rev / "heldout_summary_statistics.csv"), target_id, "mean", policy="Consensus", metric=p[3])
        return one(read_csv(fresh / "ablation_summary.csv"), target_id, p[3], dataset=p[1], policy=p[2])
    if p[0] == "T4" and p[1] == "diff":
        return one(read_csv(rev / "heldout_paired_statistical_comparisons.csv"), target_id, p[3],
                   comparison="CADO - Consensus", metric=p[2])
    if p[0] == "T4":
        return one(read_csv(rev / "heldout_summary_statistics.csv"), target_id, p[3], policy=p[1], metric=p[2])
    if p[0] == "T5":
        family = p[1].replace("_", " ")
        names = [s["name"] for s in json.loads((rev / "sensitivity_settings.json").read_text(encoding="utf-8"))
                 if s["family"] == family]
        if not names:
            raise SystemExit(f"target {target_id}: no setting in family {family!r}")
        if p[2] == "settings":
            return float(len(names))
        ds, metric = {"primary_utility": ("primary", "utility"), "ood_utility": ("ood", "utility"),
                      "primary_unsafe": ("primary", "unsafe_action_rate")}[p[2]]
        vals = [float(r["difference"]) for r in read_csv(rev / "sensitivity_paired_comparisons.csv")
                if r["setting"] in names and r["dataset"] == ds and r["metric"] == metric]
        if len(vals) != len(names):
            raise SystemExit(f"target {target_id}: {len(vals)} values for {len(names)} settings")
        return {"min": min(vals), "max": max(vals)}[p[3]]
    if p[0] == "T6":
        cases = json.loads((proto / "poc_summary.json").read_text(encoding="utf-8"))["cases"]
        hit = [c for c in cases if c["case"] == p[1]]
        if len(hit) != 1:
            raise SystemExit(f"target {target_id}: {len(hit)} prototype cases named {p[1]}")
        return float(hit[0][p[2]])
    if p[0] == "S51":
        return one(read_csv(fresh / "paired_statistical_comparisons.csv"), target_id, p[2],
                   comparison="CADO - Consensus", metric=p[1])
    if p[0] == "S52" and p[1] == "gate":
        rows = [r for r in read_csv(fresh / "ablation_episode_metrics.csv") if r["dataset"] == "primary"
                and r["policy"] == "CADO"]
        return mean(float(r[p[2]]) for r in rows)
    if p[0] == "S52" and p[1] == "ood_fallback":
        return one(read_csv(fresh / "summary_statistics.csv"), target_id, p[2], dataset="ood", policy="CADO",
                   metric="fallback_rate")
    if p[0] == "S52" and p[1] == "ood_unsafe":
        return one(read_csv(fresh / "summary_statistics.csv"), target_id, "mean", dataset="ood", policy=p[2],
                   metric="unsafe_action_rate")
    if p[0] == "S54" and p[1] == "ood_fallback":
        by = {}
        for r in read_csv(rev / "sensitivity_seed_metrics.csv"):
            if r["dataset"] == "ood" and r["policy"] == "CADO":
                by.setdefault(r["setting"], []).append(float(r["fallback_rate"]))
        return {"min": min, "max": max}[p[2]](mean(v) for v in by.values())
    if p[0] == "S55" and p[1] in ("rollback", "persistence"):
        metric = "rollback_success_rate" if p[1] == "rollback" else "failed_action_persistence_steps"
        return one(read_csv(fresh / "summary_statistics.csv"), target_id, "mean", dataset="fault", policy=p[2], metric=metric)
    if p[0] == "S55" and p[1] == "prototype":
        return float(json.loads((proto / "poc_summary.json").read_text(encoding="utf-8"))[p[2]])
    if p[0] == "S56":
        rows = read_csv(fresh / "normalization_benchmark.csv")
        if p[1] == "records":
            return float(sum(int(r["records"]) for r in rows))
        return one(rows, target_id, "exact_field_recovery", format=p[2])
    if p[0] == "S44":
        v = json.loads((rev / "reproduction_validation.json").read_text(encoding="utf-8"))
        if p[2] == "scalar_decisions":
            return float(v["scalar_decisions_checked"])
        utility = [c for c in v["episode_comparisons"] if c["metric"] == "utility"]
        return float(sum(c["episodes"] for c in utility))
    raise SystemExit(f"target {target_id}: unknown id")


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
    # step 4 (DECISIONS 15): the HTTP prototype, unchanged, on 127.0.0.1 only, in the fresh working copy
    steps.append(authors_script(fresh, "prototype/run_poc.py", out / "logs" / "run_poc.log"))
    for d in ("fresh", "revision", "prototype"):
        (out / d).mkdir(parents=True, exist_ok=True)
    for p in produced:
        shutil.copy2(p, out / "fresh" / p.name)
    stale = []
    for d, work, names in (("revision", t4, REVISION_OUTPUTS), ("prototype", fresh, PROTOTYPE_OUTPUTS)):
        for name in names:
            p = work / "revision_results" / name
            if not p.exists() or p.stat().st_mtime < start:
                stale.append(f"{d}/{name}")
            else:
                shutil.copy2(p, out / d / name)
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
    a["prototype/poc_summary.json counts"] = prototype_counts(OUT)
    b["prototype/poc_summary.json counts"] = prototype_counts(tmp)
    diff = sorted(k for k in a.keys() | b.keys() if a.get(k) != b.get(k))
    dest = OUT / f"RECHECK_{platform.node()}.json"
    write_json(dest, {"machine": platform.node(), "files": len(a), "identical": not diff, "different": diff,
                      "environment": {k: v for k, v in json.loads((tmp / "ENVIRONMENT.json").read_text(
                          encoding="utf-8")).items() if k != "packages"}})
    print(f"recheck on {platform.node()}: {'IDENTICAL' if not diff else 'DIFFERENT ' + str(diff)} "
          f"({len(a)} scientific files) -> {dest.name}")


def stage_claims(out: Path = OUT):
    """DECISIONS 19 (after the results): the authors' own claim checker, code/verify_claims.py, unchanged, on
    OUR outputs: a working copy of S1 whose result files are replaced by ours from out/."""
    if not (out / "RUN.json").exists():
        raise SystemExit("no run yet")
    w = EXT / "work_claims"
    if w.exists():
        shutil.rmtree(w)
    shutil.copytree(S1, w)
    for p in (out / "fresh").glob("*"):
        shutil.copy2(p, w / "submitted_results" / p.name)
    for d in ("revision", "prototype"):
        for p in (out / d).glob("*"):
            shutil.copy2(p, w / "revision_results" / p.name)
    (w / "revision_results" / "claim_verification.json").unlink(missing_ok=True)
    step = authors_script(w, "code/verify_claims.py", out / "logs" / "verify_claims.log")
    made = w / "revision_results" / "claim_verification.json"
    (out / "claims").mkdir(parents=True, exist_ok=True)
    if made.exists():
        shutil.copy2(made, out / "claims" / "claim_verification.json")
    write_json(out / "claims" / "CLAIMS_RUN.json", {**step, "machine": platform.node(), "output_written": made.exists()})
    print(f"verify_claims.py on our outputs: exit {step['exit_code']}")


def after_checks(out: Path = OUT) -> list:
    """DECISIONS 19: printed claims that TARGETS.csv missed, checked on our outputs AFTER the results (not targets).
    Each: id, where, claim, holds (True/False/None if a file is missing), detail."""
    rows = []

    def add(id_, where, claim, fn):
        try:
            holds, detail = fn()
        except (FileNotFoundError, KeyError, StopIteration, ValueError) as e:
            holds, detail = None, f"not checked: {type(e).__name__} {e}"
        rows.append({"id": id_, "where": where, "claim": claim, "holds": holds, "detail": detail})

    def comp():
        return read_csv(out / "revision" / "sensitivity_paired_comparisons.csv")

    def d(setting, ds, metric, col="difference"):
        return float(next(r[col] for r in comp() if r["setting"] == setting and r["dataset"] == ds and r["metric"] == metric))

    def ex():
        e = json.loads((out / "prototype" / "poc_workflow_example.json").read_text(encoding="utf-8"))
        ok = (round(e["risk"], 6) == 0.786433 and e["consensus_action"] == 2 and e["selected_action"] == 2
              and e["policy_path"] == "noninferiority")
        return ok, f"risk {e['risk']:.6f}, consensus {e['consensus_action']}, selected {e['selected_action']}, path {e['policy_path']}"
    add("A1", "Section 3.6", "worked example: R' = 0.786433, consensus level 2, residual rejected by the value-margin check, action stays 2", ex)

    def foot():
        v = [float(r["difference"]) for r in comp() if r["dataset"] == "ood" and r["metric"] == "unsafe_action_rate"]
        return len(v) == 26 and all(x == 0 for x in v), f"{len(v)} settings, max |difference| {max(abs(x) for x in v):.3g}"
    add("A2", "Table 5 note", "held-out unsafe-rate difference is zero in every one of the 26 configurations", foot)

    def unsafe():
        got = {s: d(s, "primary", "unsafe_action_rate") for s in ("threshold_shift_0.05", "uncertainty_scale_0.5", "joint_0.05_0.5")}
        ok = (round(got["threshold_shift_0.05"], 6) == 0.000023 and round(got["uncertainty_scale_0.5"], 6) == 0.000023
              and round(got["joint_0.05_0.5"], 6) == 0.000046)
        return ok, ", ".join(f"{k} {v:+.6f}" for k, v in got.items())
    add("A3", "Section 5.4", "thresholds +0.05, or the uncertainty penalty halved, raise CADO's primary unsafe rate over Consensus "
        "by 0.000023; both together by 0.000046", unsafe)

    def negative():
        neg = [r for r in comp() if r["dataset"] == "ood" and r["metric"] == "utility" and float(r["difference"]) < 0]
        ok = (len(neg) == 1 and neg[0]["setting"] == "joint_-0.05_1.5" and float(neg[0]["ci_low"]) < 0 < float(neg[0]["ci_high"]))
        return ok, "; ".join(f"{r['setting']} {float(r['difference']):+.6f} [{float(r['ci_low']):+.6f}, {float(r['ci_high']):+.6f}]"
                             for r in neg) or "none"
    add("A4", "Section 5.4", "the only negative held-out utility difference is thresholds -0.05 with penalty x1.5, and its "
        "paired 95% interval includes zero", negative)

    def suppressed():
        fb = {}
        for r in read_csv(out / "revision" / "sensitivity_seed_metrics.csv"):
            if r["dataset"] == "ood" and r["policy"] == "CADO" and r["setting"] in ("ood_limit_1.65", "uncertainty_scale_1.5"):
                fb.setdefault(r["setting"], []).append(float(r["fallback_rate"]))
        ok = len(fb) == 2 and all(x == 1.0 for v in fb.values() for x in v)
        return ok, ", ".join(f"{k}: held-out fallback {mean(v):.4f}" for k, v in fb.items())
    add("A5", "Section 5.4", "an OOD limit of 1.65, or a penalty of x1.5, applied alone, suppresses held-out personalization completely",
        suppressed)

    def radius():
        c = comp()
        zero = all(float(r["difference"]) == 0 for r in c if r["setting"] == "residual_bound_0")
        key = lambda r: (r["dataset"], r["metric"])  # noqa: E731
        # Same decisions give the same means, differences and tests. The bootstrap intervals are NOT compared: the
        # authors seed them with the setting's name (revision_analysis.py, derive_rng('revision-bootstrap', label, ...)),
        # so they differ between settings by construction even when the decisions are identical.
        cols = ("cado_mean", "consensus_mean", "difference", "wilcoxon_statistic", "p_raw", "effect_size_dz",
                "nonzero_pairs", "p_holm_six_endpoints")
        default = {key(r): tuple(r[k] for k in cols) for r in c if r["setting"] == "default"}
        two = {key(r): tuple(r[k] for k in cols) for r in c if r["setting"] == "residual_bound_2"}
        same = default == two and len(two) == 12
        return zero and same, (f"radius 0: all differences zero {zero}; radius 2: means, differences and tests identical "
                               f"to the default {same} (bootstrap intervals differ by construction: seeded by setting name)")
    add("A6", "Section 5.4", "radius zero reproduces Consensus exactly; radius two gives the same results as the default", radius)

    def chain():
        s = json.loads((out / "prototype" / "poc_summary.json").read_text(encoding="utf-8"))
        return s["journal_hash_chain_valid"] is True, f"journal_hash_chain_valid {s['journal_hash_chain_valid']}"
    add("A7", "Section 5.5", "the state journal's hash chain is consistent", chain)

    def decisions():
        n = {}
        for f, ds in (("primary_episode_metrics.csv", "primary"), ("ood_episode_metrics.csv", "ood")):
            for r in read_csv(out / "fresh" / f):
                n[(ds, r["policy"])] = n.get((ds, r["policy"]), 0) + int(r["events"])
        ok = all(v == 43200 for (ds, _), v in n.items() if ds == "primary") and all(
            v == 10800 for (ds, _), v in n.items() if ds == "ood") and len(n) == 8
        return ok, ", ".join(f"{ds} {p} {v}" for (ds, p), v in sorted(n.items()))
    add("A8", "Section 4.2", "43,200 primary decisions per policy (172,800 over four) and 10,800 held-out per policy", decisions)

    def claims():
        run = json.loads((out / "claims" / "CLAIMS_RUN.json").read_text(encoding="utf-8"))
        return run["exit_code"] == 0 and run["output_written"], f"exit {run['exit_code']} (`out/claims/claim_verification.json`)"
    add("A9", "S1 `code/verify_claims.py`", "the authors' own claim checks (benign actions unchanged, radius 0 and 2, one-level "
        "bound, the negative held-out setting, prototype counts) pass on our outputs", claims)
    return rows


def prototype_counts(out: Path) -> dict:
    """The prototype's outcome counts (its logs hold ports and clock readings, so only counts are compared)."""
    s = json.loads((out / "prototype" / "poc_summary.json").read_text(encoding="utf-8"))
    keys = ("trials", "passed_criteria", "requests", "journal_entries", "installed_routes",
            "restored_installed_routes", "persistent_rollback_failures", "journal_hash_chain_valid")
    return {**{k: s.get(k) for k in keys}, "cases": s.get("cases")}


# ── report (pure) ─────────────────────────────────────────────────────────────

def authors_asked(path: Path = HERE / "AUTHOR_CONTACT.md") -> bool:
    return path.exists() and "(draft, not sent)" not in path.read_text(encoding="utf-8")


def fmt(x, published: str) -> str:
    if x is None:
        return "-"
    if "e" in published.lower():
        return f"{x:.4g}"
    return f"{x:.{decimals(published) + 2}f}"


def paper_verdict(rows: list) -> str:
    prim = [r for r in rows if r["primary"] and r["verdict"] != "NOT ATTEMPTED"]
    bad = [r["id"] for r in prim if r["verdict"] != "MATCH"]
    if prim and not bad:
        return "reproduced (every primary target MATCH)"
    if prim and all(r["verdict"] == "NO MATCH" for r in prim):
        return "not reproduced"
    return "partially reproduced; primary targets not MATCH: " + ", ".join(bad)


def checklist(run: dict, checks: list, asked: bool) -> list:
    other = sorted({c["machine"] for c in checks if c["identical"] and c["machine"] != run.get("machine")})
    bad = [c["machine"] for c in checks if not c["identical"]]
    r5 = (f"**no**: DIFFERENT on {', '.join(bad)}" if bad else
          f"yes: identical scientific outputs on a second machine ({', '.join(other)})" if other else
          "**not yet**: the second-machine recheck has not run")
    rows = [
        ("targets committed before any result", "yes", "4b34e1d2 before the first result 8dbeec2d; `audit.py` ORDER"),
        ("gaps decided before the run", "yes: decisions 1-18 before the run; decision 19 is marked as made after the results",
         "`DECISIONS.md`"),
        ("authors asked about every gap", "yes" if asked else
         "**not yet**: the two questions are drafted, to be sent by the user", "`AUTHOR_CONTACT.md`"),
        ("exact sources and licence", "yes", "`SOURCES.md`; S1 SHA-256 and the authors' manifest checked by `fetch.py`"),
        ("variance: two machines identical (deterministic method)", r5, "`out/RECHECK_*.json`, DECISIONS 10"),
        ("every target reported", "yes", "table above, `audit.py`"),
        ("environment recorded", "yes", "`out/ENVIRONMENT.json`"),
        ("one command from public inputs, outputs hashed", "yes: a fixed sequence of commands (`README.md`); "
         "every output's SHA-256 in `out/HASHES.txt`", "`fetch.py`, `run.py`"),
        ("unit tests for each rule", "yes: comparison, verdict, hashing, lookups, S1 check", "`tests/test_cado.py`"),
        ("comparison only after this report; adaptations declared", "not started", "DECISIONS 1"),
    ]
    return (["## Checklist (STANDARD.md, Section 2)", "", "| # | requirement | met? | where |", "|---|---|---|---|"] +
            [f"| {i} | {a} | {b} | {c} |" for i, (a, b, c) in enumerate(rows, 1)] + [""])


def stage_report(out: Path = OUT, dest: Path = HERE / "REPORT.md") -> dict:
    if not (out / "RUN.json").exists():
        raise SystemExit("no run yet")
    run = json.loads((out / "RUN.json").read_text(encoding="utf-8"))
    rows = []
    for t in read_csv(HERE / "TARGETS.csv"):
        ours = lookup(t["id"], out)
        v = verdict(ours, t["published"], t["tolerance"]) if ours is not None else "NOT ATTEMPTED"
        rows.append({"id": t["id"], "table": t["table_or_figure"], "quantity": t["quantity"],
                     "published": t["published"], "ours": ours, "primary": t["primary"].strip().lower() == "yes",
                     "difference": None if ours is None else ours - float(t["published"]), "verdict": v})
    archive = json.loads((out / "ARCHIVE_COMPARISON.json").read_text(encoding="utf-8"))
    checks = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(out.glob("RECHECK_*.json"))]
    head = paper_verdict(rows)
    count = {k: sum(r["verdict"] == k for r in rows) for k in ("MATCH", "CLOSE", "NO MATCH", "NOT ATTEMPTED")}
    pc = {k: sum(r["verdict"] == k for r in rows if r["primary"]) for k in count}
    res = {"paper_verdict": head, "counts": count, "primary_counts": pc, "targets": rows, "run": run,
           "archive_comparison": archive, "rechecks": checks}
    write_json(out / "results.json", res)
    same = [a["file"] for a in archive if a.get("within_1e-12")]
    differ = [a for a in archive if not a.get("within_1e-12")]
    L = ["# CADO (Huang et al., Future Internet 18(10), 552, 2026): reproduction from Supplementary Material S1", "",
         f"**Paper verdict: {head}.**", "",
         f"- Targets: {len(rows)} printed numbers; " + ", ".join(f"{k} {v}" for k, v in count.items()) +
         f". Primary ({sum(pc.values())}): " + ", ".join(f"{k} {v}" for k, v in pc.items()) + ".",
         "- The authors' code ran unchanged (DECISIONS 5, 6, 15): " +
         "; ".join(f"`{s['script']}` exit {s['exit_code']}" for s in run["steps"]) + ". " +
         ("`reproduce_submitted.py` ends with its own comparison of every scientific value with the authors' archived "
          "outputs (1e-12); exit 0 means it passed." if run["steps"][0]["exit_code"] == 0 else
          "`reproduce_submitted.py` did not pass its own 1e-12 comparison with the archived outputs; the next line shows where."),
         f"- Our fresh outputs against the authors' archived ones, timing columns excluded: {len(same)} of "
         f"{len(archive)} files equal within 1e-12" + ("." if not differ else "; different: " + "; ".join(
             f"{a['file']} (" + ", ".join(f"{c} {m:.2g}" for c, m in a.get("max_abs_difference", {}).items() if m > 1e-12)
             + (f"; text columns {a['text_columns_different']}" if a.get("text_columns_different") else "")
             + ("; shape differs" if not a.get("same_shape", True) else "") + ")" for a in differ) + "."),
         "- Host timings (decision and parsing latency, throughput) are NOT ATTEMPTED (DECISIONS 7).",
         "- Scope (DECISIONS 14): a match shows that the released code produces the published numbers. The alerts, "
         "attackers and outcomes are synthetic; nothing here tests the simulator's realism.", "",
         "## Every target", "", "| id | table or section | quantity | published | ours | difference | verdict |",
         "|---|---|---|---|---|---|---|"]
    for r in rows:
        diff = "-" if r["difference"] is None else f"{r['difference']:+.2e}"
        L.append(f"| {r['id']} | {r['table']} | {r['quantity']}{' (primary)' if r['primary'] else ''} | {r['published']} | "
                 f"{fmt(r['ours'], r['published'])} | {diff} | {r['verdict']} |")
    after = after_checks(out)
    res["after_checks"] = after
    write_json(out / "results.json", res)
    L += ["", "## Printed claims that the targets missed (added 2026-11-25, after the results; not targets)", "",
          "A second reading of the paper against `TARGETS.csv`, after the results, found printed claims that the targets "
          "did not cover (DECISIONS 19). They cannot become targets after the results (STANDARD requirement 1), so they "
          "are checked here on our outputs and reported separately. Figures are not compared: they plot the tabled values, "
          "except Figure 4 (host timings).", "",
          "| check | where | claim | holds on our outputs | detail |", "|---|---|---|---|---|"]
    for a in after:
        held = {True: "yes", False: "**no**", None: "not checked"}[a["holds"]]
        L.append(f"| {a['id']} | {a['where']} | {a['claim']} | {held} | {a['detail']} |")
    L += [""] + checklist(run, checks, authors_asked())
    env = json.loads((out / "ENVIRONMENT.json").read_text(encoding="utf-8"))
    L += ["## Environment", "",
          f"- Python {env['python'].split()[0]}, {env['platform']}, machine {env['machine']}; "
          + ", ".join(p for p in env["packages"] if p.split("==")[0].lower() in PINS) + " (the authors' pins); "
          "full list in `out/ENVIRONMENT.json`.",
          "- Rechecks on another machine: " + ("; ".join(f"{c['machine']}: {'IDENTICAL' if c['identical'] else 'DIFFERENT'}"
                                                     for c in checks) or "none yet") + ".",
          "- Every output's SHA-256 (LF line endings): `out/HASHES.txt`; scientific CSVs without timing columns: "
          "`out/SCIENTIFIC_SHA256.json`.", ""]
    dest.write_text("\n".join(L), encoding="utf-8")
    write_hashes(out)
    print("\n".join(L[:9]))
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=["check", "run", "claims", "report", "recheck"])
    a = ap.parse_args()
    {"check": stage_check, "run": stage_run, "claims": stage_claims, "report": stage_report,
     "recheck": stage_recheck}[a.stage]()


if __name__ == "__main__":
    main()
