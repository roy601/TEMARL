# -*- coding: utf-8 -*-
"""Protocol D1.0 on the GPU PC: the whole procedure in four one-line stages.

    python camlds_real_full_arch/run_all_d1.py diagnostics   # BEFORE the freeze: preflight + timing
    python camlds_real_full_arch/run_all_d1.py main          # after the freeze: gate, preflight, timing,
                                                             #   2,240 cells, validation dry run
    python camlds_real_full_arch/run_all_d1.py sensitivity   # the 6 Section 8 settings: preflight, cells,
                                                             #   validation dry run, each
    python camlds_real_full_arch/run_all_d1.py open          # opens, ONCE, every test whose dry run passed
    add --plan to print a stage's steps without running anything

Each stage runs unattended, writes everything it prints to results_d1/logs/, and stops at the first
failure with the reason. Only `open` opens a test: the main and sensitivity stages end on validation,
so a fault can still be found and fixed before any test is seen. Every stage can be started again after
a crash or power cut: finished cells, a gate that has run and an opened test are never repeated.
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
sys.path.insert(0, str(HERE))
import spec_d1  # noqa: E402

OUT = HERE / "results_d1"
GATE = HERE / "gate" / "GATE_RESULT.json"
SENSITIVITIES = ("efficacy_0.5", "efficacy_0.75", "mean", "random_walk", "execution", "reward_engagement")


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def _passed(path: Path) -> bool:
    d = _json(path)
    return bool(d and d.get("pass"))


def py(script, *args):
    return [sys.executable, "-u", str(HERE / script), *args]


def shown(cmd):
    return " ".join([os.path.relpath(cmd[2], REPO), *cmd[3:]])


# a step: (label, command or None, pre) -- pre() returns None (run), ("skip", why) or ("stop", why)
def _frozen():
    return None if spec_d1.SPEC.exists() and spec_d1.check() else ("stop", "protocol D1.0 is not frozen (or a pinned file changed)")


def _gate_pre():
    d = _json(GATE)
    if d is None:
        return None
    return ("skip", "the gate has already run and passed") if d["pass"] else ("stop", "the validity gate FAILED: the study stops before MARL (Section 5)")


def _gate_passed():
    return None if _passed(GATE) else ("stop", "the validity gate has not passed")


def _dry_pre(name):
    return lambda: ("skip", "dry run already passed") if _passed(OUT / name / "DRY_RUN_VALIDATION.json") else None


def _open_pre(name):
    def pre():
        if (OUT / name / "TEST_OPENED.json").exists():
            return ("skip", "test already opened (never again)")
        if not _passed(OUT / name / "DRY_RUN_VALIDATION.json"):
            return ("skip", "its validation dry run has not passed: not opened")
        return None
    return pre


def plan(stage: str, device: str):
    dev = ["--device", device]
    if stage == "diagnostics":
        return [("preflight: every protocol 1.2 checkpoint", py("run_d1.py", *dev, "--preflight"), None),
                ("timing + dry-run check on this device", py("run_d1.py", *dev, "--timing"), None)]
    if stage == "main":
        return [("protocol frozen", None, _frozen),
                ("validity gate (once)", py("gate_d1.py"), _gate_pre),
                ("preflight under the frozen spec", py("run_d1.py", *dev, "--preflight"), None),
                ("timing + dry-run check under the frozen spec", py("run_d1.py", *dev, "--timing"), None),
                ("main run: 2,240 cells (test sealed)", py("run_d1.py", *dev), None),
                ("validation dry run", py("evaluate_d1.py", *dev, "--validation-dry-run"), _dry_pre("main"))]
    if stage == "sensitivity":
        steps = [("protocol frozen", None, _frozen), ("validity gate passed", None, _gate_passed)]
        for s in SENSITIVITIES:
            if s != "execution":                     # execution-order encoders are trained in the cell
                steps.append((f"{s}: preflight", py("run_d1.py", *dev, "--sensitivity", s, "--preflight"), None))
            steps += [(f"{s}: 320 cells (test sealed)", py("run_d1.py", *dev, "--sensitivity", s), None),
                      (f"{s}: validation dry run",
                       py("evaluate_d1.py", *dev, "--sensitivity", s, "--validation-dry-run"), _dry_pre(s))]
        return steps
    if stage == "open":
        steps = [("protocol frozen", None, _frozen),
                 ("open the main test ONCE", py("evaluate_d1.py", *dev, "--open-test"), _open_pre("main"))]
        steps += [(f"{s}: open its test ONCE", py("evaluate_d1.py", *dev, "--sensitivity", s, "--open-test"),
                   _open_pre(s)) for s in SENSITIVITIES]
        return steps
    raise ValueError(stage)


def summary(stage: str) -> list:
    L = []
    if stage in ("diagnostics", "main"):
        pf = _json(OUT / "main" / "PREFLIGHT.json")
        if pf:
            L.append(f"preflight: {'PASS' if pf['pass'] else 'FAIL'}, {len(pf['ok'])} checkpoints ok, "
                     f"{len(pf['failures'])} failures")
        td = next(iter(sorted((OUT / "timing").rglob("TIMING_DRY_RUN.json"))), None)
        if td:
            d = _json(td)
            L.append(f"timing: one cell {d['seconds']:.0f} s on {d['device']} -> 2,240 main cells about "
                     f"{2240 * d['seconds'] / 3600:.0f} h; dry-run reproduction {'PASS' if d['pass'] else 'FAIL'}")
    if stage == "main":
        L.append(f"validation summary: {OUT / 'main' / 'VALIDATION_SUMMARY.md'} (no test number in it)")
        L.append("next: commit and push the results, then run the `open` stage")
    return L


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=["diagnostics", "main", "sensitivity", "open"])
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
        say(f"D1.0 stage '{a.stage}' on {a.device}, started {time.strftime('%Y-%m-%d %H:%M:%S')}; log {log}")
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
        for s in summary(a.stage):
            say("  " + s)
        say(f"  send me {log}")


if __name__ == "__main__":
    main()
