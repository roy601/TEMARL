# -*- coding: utf-8 -*-
"""Protocol CL-D1.0 on the GPU PC: the whole procedure in three one-line stages.

    python casinolimit_d1/run_all_cl.py diagnostics   # BEFORE the freeze: preflight + timing (no test)
    python casinolimit_d1/run_all_cl.py run           # after the freeze: gate (once), preflight, timing,
                                                      #   every study's cells, dry runs, tune selection
    python casinolimit_d1/run_all_cl.py open          # opens the test, ONCE, for every study
    add --plan to print a stage's steps without running anything

As run_all_d1.py: each stage runs unattended, writes everything it prints to results_cl/logs/, stops at
the first failure (a failed gate or dry run included) and can be started again after a crash or power
cut: finished cells, a gate that has run, a passed dry run and an opened test are never repeated. If the
gate fails, no learned agent is trained and the study is reported as stopped (Section 5).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
OUT = HERE / "results_cl"
GATE = HERE / "gate" / "GATE_RESULT.json"
STUDIES = ("main", "efficacy_0.5", "efficacy_0.75", "mean", "reward_engagement", "tune")


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def _passed(path: Path) -> bool:
    d = _json(path)
    return bool(d and d.get("pass"))


def py(script, *args):
    return [sys.executable, "-u", str(HERE / script), *args]


def shown(cmd):
    return " ".join([os.path.relpath(cmd[2], REPO), *cmd[3:]])


def _frozen():
    sys.path.insert(0, str(HERE))
    import spec_cl_d1
    return None if spec_cl_d1.SPEC.exists() and spec_cl_d1.check() else \
        ("stop", "protocol CL-D1.0 is not frozen (or a pinned file changed)")


def _gate_pre():
    d = _json(GATE)
    if d is None:
        return None
    return ("skip", "the gate has already run and passed") if d["pass"] else \
        ("stop", "the validity gate FAILED: the study stops before any learned agent (Section 5)")


def _dry_pre(study):
    def pre():
        ok = _passed(OUT / study / "DRY_RUN_VALIDATION.json")
        if study == "tune":
            ok = ok and (OUT / "tune" / "SELECTION.json").exists()
        return ("skip", "dry run already passed") if ok else None
    return pre


def _open_pre():
    if (OUT / "TEST_OPENED.json").exists():
        return ("skip", "test already opened (never again)")
    for s in STUDIES:
        if not _passed(OUT / s / "DRY_RUN_VALIDATION.json"):
            return ("skip", f"the dry run of study {s} has not passed: not opened")
    return None


def plan(stage: str, device: str):
    dev = ["--device", device]
    if stage == "diagnostics":
        return [("preflight: every CL 1.0 checkpoint (200)", py("run_cl.py", *dev, "--preflight"), None),
                ("timing + dry-run check on this device", py("run_cl.py", *dev, "--timing"), None)]
    if stage == "run":
        steps = [("protocol frozen", None, _frozen),
                 ("validity gate (once)", py("gate_cl.py"), _gate_pre),
                 ("preflight under the frozen spec", py("run_cl.py", *dev, "--preflight"), None),
                 ("timing + dry-run check under the frozen spec", py("run_cl.py", *dev, "--timing"), None)]
        for s in STUDIES:
            steps += [(f"{s}: cells (test sealed)", py("run_cl.py", *dev, "--study", s), None),
                      (f"{s}: validation dry run" + (" + nested selection" if s == "tune" else ""),
                       py("evaluate_cl.py", *dev, "--study", s, "--validation-dry-run"), _dry_pre(s))]
        return steps
    if stage == "open":
        return [("protocol frozen", None, _frozen),
                ("open the test ONCE (every study)", py("evaluate_cl.py", *dev, "--open-test"), _open_pre)]
    raise ValueError(stage)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=["diagnostics", "run", "open"])
    ap.add_argument("--device", default="cuda", choices=["cuda", "cpu"])
    ap.add_argument("--plan", action="store_true", help="print the steps, run nothing")
    a = ap.parse_args()
    steps = plan(a.stage, a.device)
    if a.plan:
        for i, (label, cmd, pre) in enumerate(steps, 1):
            print(f"{i}. {label}" + (f"\n     {shown(cmd)}" if cmd else "  (check)")
                  + ("  [skipped or stopped if already done / not allowed]" if pre else ""))
        return
    logs = OUT / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    log = logs / f"{a.stage}_{time.strftime('%Y%m%d_%H%M%S')}.log"
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1")
    t_all = time.time()
    with log.open("w", encoding="utf-8") as fh:
        def say(s=""):
            print(s, flush=True)
            fh.write(s + "\n")
            fh.flush()
        say(f"CL-D1.0 stage '{a.stage}' on {a.device}, started {time.strftime('%Y-%m-%d %H:%M:%S')}; log {log}")
        for i, (label, cmd, pre) in enumerate(steps, 1):
            p = pre() if pre else None
            if p and p[0] == "skip":
                say(f"\n[{i}/{len(steps)}] {label}: skipped ({p[1]})")
                continue
            if p and p[0] == "stop":
                say(f"\nSTOPPED at [{i}/{len(steps)}] {label}: {p[1]}")
                raise SystemExit(1)
            if cmd is None:
                say(f"\n[{i}/{len(steps)}] {label}: ok")
                continue
            say(f"\n[{i}/{len(steps)}] {label}\n    {shown(cmd)}")
            t0 = time.time()
            proc = subprocess.Popen(cmd, cwd=str(REPO), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    text=True, encoding="utf-8", errors="replace", env=env)
            for line in proc.stdout:
                print(line, end="", flush=True)
                fh.write(line)
                fh.flush()
            rc = proc.wait()
            if rc != 0:
                say(f"\nSTOPPED at [{i}/{len(steps)}] {label}: exit code {rc} after {time.time() - t0:.0f} s. "
                    f"Nothing later in this stage was run. Send me {log}")
                raise SystemExit(1)
            say(f"    done in {(time.time() - t0) / 60:.1f} min")
        say(f"\nSTAGE '{a.stage}' FINISHED in {(time.time() - t_all) / 3600:.2f} h")
        if a.stage == "run":
            say("  next: commit and push results_cl and gate, then run the `open` stage")
        say(f"  send me {log}")


if __name__ == "__main__":
    main()
