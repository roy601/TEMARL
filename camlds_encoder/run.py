# -*- coding: utf-8 -*-
"""B2 runner: TEMARL's encoder on CAM-LDS. Validation only; test outputs are sealed, never scored.

    python camlds_encoder/run.py --stage check
    python camlds_encoder/run.py --stage pilot --device cuda     # chooses patience and update budget
    python camlds_encoder/run.py --stage train --device cuda     # 32 folds x 10 seeds
    python camlds_encoder/run.py --stage all --smoke             # a few minutes on CPU; NOT a result

  check  verifies every pinned input and that the test points equal protocol 1.1's side file
  pilot  3 pilot seeds x 32 folds, trained to a cap with full validation curves. Patience and the
         shared update budget are then chosen by the FROZEN rules of Temarl_Test_v1_L1/study_spec.py,
         from validation curves only. Done on the main condition; collapse_repeats reuses it.
  train  one cell per (fold, seed): validation-best checkpoint, threshold chosen on validation,
         validation metrics. Test logits are saved and hashed. No test metric is computed.

Resumable: a finished cell is never retrained. A `.running` lock stops two processes sharing an
output folder. Checkpoints (encoder.pt) stay on the machine that trained them; they are not
committed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import data  # noqa: E402
from port import NT, OLD_NT, SPEC, Mx, T  # noqa: E402

PRIMARY_ARM = "Transformer"                     # protocol 1.0, Q4
ALLOWED_ARMS = ("Transformer", "GRU", "LSTM")   # GRU/LSTM only if decided before any test result
SMOKE_CAP, SMOKE_FOLDS = 128, ("1_autostart_localaccount", "S2")


def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, indent=1, default=lambda o: o.item() if hasattr(o, "item") else list(o))
    os.replace(tmp, path)


def read_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def sha_file(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


class Lock:
    def __init__(self, out):
        self.path = os.path.join(out, ".running")

    def __enter__(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if os.path.exists(self.path):
            raise SystemExit(f"Locked by: {open(self.path).read()}\nIf that process is gone, delete {self.path}.")
        with open(self.path, "w") as fh:
            fh.write(f"pid={os.getpid()} host={platform.node()} started={time.strftime('%Y-%m-%d %H:%M:%S')}")
        return self

    def __exit__(self, *exc):
        if os.path.exists(self.path):
            os.remove(self.path)


def pick_folds(condition, smoke):
    fs = data.folds(condition)
    return [f for f in fs if f["fold"] in SMOKE_FOLDS] if smoke else fs


# ── stages ────────────────────────────────────────────────────────────────────

def stage_check(args, out):
    sys.path.insert(0, os.path.join(data.REPO, "idea01_kuwano"))
    import spec_1_1
    if spec_1_1._main() != 0:
        raise SystemExit("protocol 1.1 check failed")
    side = [json.loads(x) for x in open(os.path.join(data.REPO, "camlds_real", "out", "sidecar", "points.jsonl"),
                                         encoding="utf-8")]
    lines, ok = [], True
    for cond in data.CONDITIONS:
        for f in data.folds(cond):
            d = data.fold_data(f)
            want = [p["source_row"] for p in side
                    if p["condition"] == cond and p["family"] == f["family"] and p["fold"] == f["fold"]]
            same = want == d["test_source_rows"]
            ok &= same
            lines.append(f"  {cond:<16} {f['fold']:<28} train {len(d['train'][0]):>4} val {len(d['val'][0]):>3} "
                         f"test {len(d['test_inputs'][0]):>3}  test points = side file: {same}")
    print(f"labels: {NT} (frozen pipeline had {OLD_NT}); window {data.W}; folds per condition "
          f"{len(data.folds('main'))}")
    print("\n".join(lines))
    print(f"\nCHECK: {'PASS' if ok else 'FAIL'}")
    write_json(os.path.join(out, "check.json"), {"pass": ok, "labels": NT, "rows": lines})
    return ok


def stage_pilot(args, out, device):
    curves, results = {}, {}
    seeds = SPEC.PILOT_SEEDS[:1] if args.smoke else SPEC.PILOT_SEEDS
    jobs = [(a, f, s) for a in args.arms for f in pick_folds("main", args.smoke) for s in seeds]
    t0 = time.time()
    for i, (arm, f, seed) in enumerate(jobs, 1):
        path = os.path.join(out, "pilot", arm, f"{f['fold']}_s{seed}.json")
        if os.path.exists(path):
            rec = read_json(path)
        else:
            d = data.fold_data(f)
            n = len(d["train"][0])
            cap = SMOKE_CAP if args.smoke else max(SPEC.PILOT_MIN_UPDATES,
                                                   int(SPEC.PILOT_EPOCH_EQUIVALENTS * n / SPEC.BATCH_SIZE))
            print(f"  [{i}/{len(jobs)}] pilot {arm} {f['fold']} s{seed} cap {cap}", flush=True)
            res, _ = T.train_one(arm, data.W, seed, d["train"], d["val"], cap, device=device,
                                 patience_checks=None, progress=args.verbose)
            rec = {"arm": arm, "fold": f["fold"], "family": f["family"], "seed": seed, "cap": cap,
                   "train_windows": n, "curve": res.curve, "best_update": res.best_update,
                   "best_validation_bce": res.best_val_bce, "cap_reached": res.cap_reached,
                   "updates_completed": res.updates_completed, "seconds": res.seconds}
            write_json(path, rec)
        key = f"{arm}_{rec['fold']}"
        curves[f"{key}_s{rec['seed']}"] = rec["curve"]
        results.setdefault(key, []).append(T.TrainResult(
            arm=arm, window=data.W, seed=rec["seed"], sampler="ordinary",
            updates_completed=rec["updates_completed"], curve=rec["curve"],
            best_update=rec["best_update"], best_val_bce=rec["best_validation_bce"],
            cap_reached=rec["cap_reached"]))
    patience = T.choose_patience(curves, SPEC.PATIENCE_GRID, SPEC.PATIENCE_TOLERANCE)
    budget = T.choose_update_budget(results, SPEC.BUDGET_FACTOR, SPEC.VAL_EVERY_UPDATES)
    block = {"chosen_from": "validation curves of the pilot cells only (main condition)",
             "arms": list(args.arms), "n_pilot_cells": len(jobs), "smoke": args.smoke,
             "shared_patience": patience["chosen_patience"],
             "shared_update_budget": budget["shared_update_budget"],
             "convergence_unresolved": budget["configurations_with_unresolved_cap"],
             "patience_selection": patience, "budget_selection": budget,
             "seconds": round(time.time() - t0, 1)}
    write_json(os.path.join(out, "budget.json"), block)
    print(f"  -> patience {block['shared_patience']} checks, budget {block['shared_update_budget']} updates; "
          f"unresolved caps: {len(block['convergence_unresolved'])}")
    return block


def stage_train(args, out, device):
    bpath = os.path.join(out, "budget.json")
    if not os.path.exists(bpath):
        raise SystemExit("No budget.json: run --stage pilot first.")
    budget = read_json(bpath)
    if budget.get("smoke") and not args.smoke:
        raise SystemExit("budget.json comes from a smoke run; it cannot be used for a real run.")
    seeds = SPEC.MAIN_SEEDS[:1] if args.smoke else SPEC.MAIN_SEEDS
    jobs = [(a, f, s) for a in args.arms for f in pick_folds(args.condition, args.smoke) for s in seeds]
    for i, (arm, f, seed) in enumerate(jobs, 1):
        cell = os.path.join(out, "train", args.condition, arm, f["fold"], f"s{seed}")
        if os.path.exists(os.path.join(cell, "result.json")):
            continue
        print(f"  [{i}/{len(jobs)}] train {args.condition} {arm} {f['fold']} s{seed}", flush=True)
        d = data.fold_data(f)
        res, model = T.train_one(arm, data.W, seed, d["train"], d["val"], budget["shared_update_budget"],
                                 device=device, checkpoint_dir=cell,
                                 patience_checks=budget["shared_patience"], progress=args.verbose)
        T.load_best(model, res)                                    # validation-best is primary
        Xva, Mva, Yva = d["val"]
        lo_va = T.predict(model, Xva, Mva, device)
        th = Mx.select_threshold(Mx._sigmoid(lo_va), Yva)          # validation only
        val = Mx.evaluate(lo_va, Yva, d["val_owners"], th)
        lo_te = T.predict(model, *d["test_inputs"], device).astype(np.float32)
        np.save(os.path.join(cell, "test_logits.npy"), lo_te)      # sealed: not scored here
        write_json(os.path.join(cell, "result.json"), {
            "condition": args.condition, "family": f["family"], "fold": f["fold"], "arm": arm, "seed": seed,
            "window": data.W, "labels": NT, "threshold": th, "validation": val,
            "updates_completed": res.updates_completed, "best_update": res.best_update,
            "best_validation_bce": res.best_val_bce, "cap_reached": res.cap_reached,
            "seconds": res.seconds, "parameters": res.parameters, "exposure": res.exposure,
            "curve": res.curve, "budget": {k: budget[k] for k in ("shared_patience", "shared_update_budget")},
            "sealed_test": {"file": "test_logits.npy", "sha256": sha_file(os.path.join(cell, "test_logits.npy")),
                            "points": int(len(lo_te)), "source_rows": d["test_source_rows"],
                            "owners": d["test_owners"]},
            "smoke": args.smoke})


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", default="check", choices=("check", "pilot", "train", "all"))
    ap.add_argument("--condition", default="main", choices=data.CONDITIONS)
    ap.add_argument("--arms", nargs="+", default=[PRIMARY_ARM], choices=ALLOWED_ARMS)
    ap.add_argument("--device", default="auto", choices=("auto", "cpu", "cuda"))
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--out", default=None)
    ap.add_argument("--smoke", action="store_true", help="tiny budgets, 2 folds, 1 seed; NOT a result")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    out = args.out or os.path.join(HERE, "out_smoke" if args.smoke else "out")
    torch.set_num_threads(args.threads)
    device = T.device_of(args.device)
    print(f"camlds_encoder | stage {args.stage} | condition {args.condition} | arms {args.arms} | device {device}"
          f"{' | SMOKE: not a result' if args.smoke else ''}")
    write_json(os.path.join(out, "environment.json"), {
        "python": sys.version.split()[0], "torch": torch.__version__, "numpy": np.__version__,
        "platform": platform.platform(), "cuda": torch.cuda.is_available(),
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None})
    with Lock(out):
        if args.stage in ("check", "all") and not stage_check(args, out):
            return 1
        if args.stage in ("pilot", "all"):
            stage_pilot(args, out, device)
        if args.stage in ("train", "all"):
            stage_train(args, out, device)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
