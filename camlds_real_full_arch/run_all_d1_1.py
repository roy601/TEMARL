# -*- coding: utf-8 -*-
"""Protocol D1.1 on the GPU PC: the whole procedure in two one-line stages.

    python camlds_real_full_arch/run_all_d1_1.py tune   # checks, preflight, timing, 1,728 cells,
                                                        #   validation dry run + nested selection
    python camlds_real_full_arch/run_all_d1_1.py open   # opens the D1.1 test, ONCE
    add --plan to print a stage's steps without running anything

As run_all_d1.py: each stage runs unattended, writes everything it prints to results_d1_1/logs/, stops
at the first failure with the reason and can be started again after a crash or power cut (finished cells
are kept; a passed dry run and an opened test are never repeated). Only `open` opens a test.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))
import run_all_d1 as D  # noqa: E402  (D1.0's gate result and helpers, unchanged)
import spec_d1  # noqa: E402
import spec_d1_1  # noqa: E402

OUT = HERE / "results_d1_1"
py, shown, _json, _passed = D.py, D.shown, D._json, D._passed


def _frozen():
    if not (spec_d1.SPEC.exists() and spec_d1.check()):
        return ("stop", "protocol D1.0 is not frozen (or a pinned file changed)")
    if not (spec_d1_1.SPEC.exists() and spec_d1_1.check()):
        return ("stop", "protocol D1.1 is not frozen (or a pinned file changed)")
    return None


def _gate_passed():
    return None if _passed(D.GATE) else ("stop", "the D1.0 validity gate has not passed (D1.0 Section 5)")


def _dry_pre():
    return ("skip", "dry run and selection already done") if (
        _passed(OUT / "DRY_RUN_VALIDATION.json") and (OUT / "SELECTION.json").exists()) else None


def _open_pre():
    if (OUT / "TEST_OPENED.json").exists():
        return ("skip", "test already opened (never again)")
    if not (_passed(OUT / "DRY_RUN_VALIDATION.json") and (OUT / "SELECTION.json").exists()):
        return ("skip", "its validation dry run and selection have not passed: not opened")
    return None


def plan(stage: str, device: str):
    dev = ["--device", device]
    if stage == "tune":
        return [("protocols D1.0 and D1.1 frozen", None, _frozen),
                ("D1.0 validity gate passed", None, _gate_passed),
                ("preflight: 96 allpos checkpoints (seeds 0-2)", py("run_d1_1.py", *dev, "--preflight"), None),
                ("timing + dry-run check (one 15-epoch cell, no test)", py("run_d1_1.py", *dev, "--timing"), None),
                ("D1.1 run: 1,728 cells (test sealed)", py("run_d1_1.py", *dev), None),
                ("validation dry run + nested selection", py("evaluate_d1_1.py", *dev, "--validation-dry-run"),
                 _dry_pre)]
    if stage == "open":
        return [("protocols D1.0 and D1.1 frozen", None, _frozen),
                ("open the D1.1 test ONCE", py("evaluate_d1_1.py", *dev, "--open-test"), _open_pre)]
    raise ValueError(stage)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=["tune", "open"])
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
        say(f"D1.1 stage '{a.stage}' on {a.device}, started {time.strftime('%Y-%m-%d %H:%M:%S')}; log {log}")
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
        if a.stage == "tune":
            say(f"  selection (validation only): {OUT / 'SELECTION.json'}")
            say("  next: commit and push results_d1_1, then run the `open` stage")
        say(f"  send me {log}")


if __name__ == "__main__":
    main()
