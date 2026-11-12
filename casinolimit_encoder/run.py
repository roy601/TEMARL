# -*- coding: utf-8 -*-
"""CasinoLimit: train and save everything for PROTOCOL_CL_1.0.md. Test outputs are sealed, never scored.

    python casinolimit_encoder/run.py --stage all --device cuda      # everything, resumable (GPU PC)
    python casinolimit_encoder/run.py --stage check                  # split and data checks only
    python casinolimit_encoder/run.py --stage all --smoke            # a few minutes on CPU; NOT a result

Stages (--stage all runs them in this order):
  check     corpus hash, folds, windows; writes out/split.json
  pilot     3 pilot seeds x 5 folds x 4 encoders, trained to the frozen cap with full validation
            curves. Patience and the update budget are chosen by the FROZEN rules of
            Temarl_Test_v1_L1/study_spec.py (as for CAM-LDS), from validation curves only.
  train     10 seeds x 5 folds x 4 encoders x 2 conditions, with that patience and budget.
            Per training: validation-best checkpoint, threshold chosen on validation, validation
            scores; test logits saved and hashed (sealed).
  lookup    the lookup-table baseline: validation scored, test predictions saved and hashed (sealed)
  summary   out/VALIDATION_SUMMARY.txt (validation only, descriptive)

Everything is saved under casinolimit_encoder/out/ (smoke runs: out_smoke/). A finished training is
never redone, so the same command continues after a stop. Checkpoints (encoder.pt) stay on the
machine that trained them (not committed).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import statistics as st
import sys
import time

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cl_data as CD  # noqa: E402
import cl_split as S  # noqa: E402
import lookup as LK  # noqa: E402
from cl_port import LABEL_ID, NT, SPEC, STEPS, Mx, T, V, sha_lf, STEPS_PATH  # noqa: E402

ENCODERS = ("allpos", "gru_allpos", "lstm_allpos", "baseline")
#   allpos      the final design: frozen Transformer + all-position loss (CAM-LDS protocol 1.2)
#   gru_allpos, lstm_allpos   the secondary encoders of protocol 1.2
#   baseline    the frozen Transformer before improvement 1: descriptive only
SMOKE_CAP, SMOKE_FOLDS = 128, ("F1", "F2")


# ── small helpers ─────────────────────────────────────────────────────────────

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


def save_array(cell, name, arr):
    path = os.path.join(cell, name)
    np.save(path, np.asarray(arr, np.float32))
    return {"file": name, "sha256": sha_file(path), "points": int(len(arr))}


def micro_f1(pred01, y):
    tp = float((pred01 * y).sum())
    fp = float((pred01 * (1 - y)).sum())
    fn = float(((1 - pred01) * y).sum())
    return 0.0 if tp == 0 else 2 * tp / (2 * tp + fp + fn)


class Lock:
    def __init__(self, out):
        self.path = os.path.join(out, ".running")

    def __enter__(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if os.path.exists(self.path):
            with open(self.path) as fh:
                raise SystemExit(f"Locked by: {fh.read()}\nIf that process is gone, delete {self.path}.")
        with open(self.path, "w") as fh:
            fh.write(f"pid={os.getpid()} host={platform.node()} started={time.strftime('%Y-%m-%d %H:%M:%S')}")
        return self

    def __exit__(self, *exc):
        if os.path.exists(self.path):
            os.remove(self.path)


def pick_folds(condition, smoke):
    fs = CD.folds(condition)
    return [f for f in fs if f["fold"] in SMOKE_FOLDS] if smoke else fs


def seeds_for(smoke, pilot=False):
    s = SPEC.PILOT_SEEDS if pilot else SPEC.MAIN_SEEDS
    return s[:1] if smoke else s


# ── stages ────────────────────────────────────────────────────────────────────

def stage_check(args, out):
    folds = CD.folds("main")
    runs = sorted({s["run"] for s in STEPS})
    tested = sorted(r for f in folds for r in f["test_runs"])
    ok = tested == runs                                              # every run tested exactly once
    rows = []
    for f in folds:
        roles = set(f["test_runs"]) | set(f["val_runs"]) | set(f["train_runs"])
        disjoint = (not set(f["test_runs"]) & set(f["val_runs"]) and not set(f["test_runs"]) & set(f["train_runs"])
                    and not set(f["val_runs"]) & set(f["train_runs"]))
        ok &= disjoint and roles == set(runs)
        for cond in S.CONDITIONS:
            d = CD.fold_data({**f, "_steps": CD.steps_for(cond)})
            ok &= CD.label_matrix_ok(d["train"][2]) and CD.label_matrix_ok(d["val"][2])
            rows.append({"fold": f["fold"], "condition": cond, "test_runs": len(f["test_runs"]),
                         "val_runs": len(f["val_runs"]), "train_runs": len(f["train_runs"]),
                         "train_points": int(len(d["train"][0])), "val_points": int(len(d["val"][0])),
                         "test_points": int(len(d["test_inputs"][0])), "roles_disjoint": disjoint})
    print(f"labels {NT} | window {CD.W} | runs {len(runs)} | folds {len(folds)} | approved {S.APPROVED_ON}")
    for r in rows:
        print(f"  {r['fold']} {r['condition']:<16} runs test/val/train {r['test_runs']:>3}/{r['val_runs']:>3}/"
              f"{r['train_runs']:>3}  points test/val/train {r['test_points']:>5}/{r['val_points']:>5}/{r['train_points']:>5}")
    print(f"CHECK: {'PASS' if ok else 'FAIL'}")
    write_json(os.path.join(out, "split.json"), {
        "pass": ok, "corpus": "casinolimit_real/out/steps.jsonl", "corpus_sha256_lf": sha_lf(STEPS_PATH),
        "labels": NT, "window": CD.W, "approved_on": S.APPROVED_ON, "rows": rows,
        "folds": [{k: f[k] for k in ("fold", "test_runs", "val_runs", "train_runs")} for f in folds]})
    return ok


def stage_pilot(args, out, device):
    curves, results = {}, {}
    jobs = [(v, f, s) for v in ENCODERS for f in pick_folds("main", args.smoke) for s in seeds_for(args.smoke, True)]
    t0 = time.time()
    for i, (v, f, seed) in enumerate(jobs, 1):
        path = os.path.join(out, "pilot", v, f"{f['fold']}_s{seed}.json")
        if os.path.exists(path):
            rec = read_json(path)
        else:
            d = CD.fold_data(f)
            n = len(d["train"][0])
            cap = SMOKE_CAP if args.smoke else max(SPEC.PILOT_MIN_UPDATES,
                                                   int(SPEC.PILOT_EPOCH_EQUIVALENTS * n / SPEC.BATCH_SIZE))
            print(f"  [{i}/{len(jobs)}] pilot {v} {f['fold']} s{seed} cap {cap}", flush=True)
            res, _ = V.train_variant(v, CD.W, seed, d["train"], d["val"], cap, device=device,
                                     patience_checks=None, progress=args.verbose)
            rec = {"variant": v, "fold": f["fold"], "seed": seed, "cap": cap, "train_windows": n,
                   "curve": res.curve, "best_update": res.best_update, "best_validation_bce": res.best_val_bce,
                   "cap_reached": res.cap_reached, "updates_completed": res.updates_completed,
                   "seconds": res.seconds}
            write_json(path, rec)
        key = f"{v}_{rec['fold']}"
        curves[f"{key}_s{rec['seed']}"] = rec["curve"]
        results.setdefault(key, []).append(T.TrainResult(
            arm=v, window=CD.W, seed=rec["seed"], sampler="ordinary", updates_completed=rec["updates_completed"],
            curve=rec["curve"], best_update=rec["best_update"], best_val_bce=rec["best_validation_bce"],
            cap_reached=rec["cap_reached"]))
    patience = T.choose_patience(curves, SPEC.PATIENCE_GRID, SPEC.PATIENCE_TOLERANCE)
    budget = T.choose_update_budget(results, SPEC.BUDGET_FACTOR, SPEC.VAL_EVERY_UPDATES)
    block = {"chosen_from": "validation curves of the pilot cells only (main condition)",
             "encoders": list(ENCODERS), "n_pilot_cells": len(jobs), "smoke": args.smoke,
             "shared_patience": patience["chosen_patience"], "shared_update_budget": budget["shared_update_budget"],
             "convergence_unresolved": budget["configurations_with_unresolved_cap"],
             "patience_selection": patience, "budget_selection": budget, "seconds": round(time.time() - t0, 1)}
    write_json(os.path.join(out, "budget.json"), block)
    print(f"  -> patience {block['shared_patience']} checks, budget {block['shared_update_budget']} updates; "
          f"unresolved caps: {len(block['convergence_unresolved'])}")
    return block


def stage_train(args, out, device, condition, encoders):
    budget = read_json(os.path.join(out, "budget.json"))
    if budget.get("smoke") and not args.smoke:
        raise SystemExit("budget.json comes from a smoke run; it cannot be used for a real run.")
    jobs = [(v, f, s) for v in encoders for f in pick_folds(condition, args.smoke) for s in seeds_for(args.smoke)]
    for i, (v, f, seed) in enumerate(jobs, 1):
        cell = os.path.join(out, "train", condition, v, f["fold"], f"s{seed}")
        if os.path.exists(os.path.join(cell, "result.json")):
            continue
        print(f"  [{i}/{len(jobs)}] train {condition} {v} {f['fold']} s{seed}", flush=True)
        d = CD.fold_data(f)
        res, model = V.train_variant(v, CD.W, seed, d["train"], d["val"], budget["shared_update_budget"],
                                     device=device, checkpoint_dir=cell,
                                     patience_checks=budget["shared_patience"], progress=args.verbose)
        T.load_best(model, res)                                           # validation-best is primary
        Xva, Mva, Yva = d["val"]
        lo_va = T.predict(model, Xva, Mva, device)
        th = Mx.select_threshold(Mx._sigmoid(lo_va), Yva)                 # validation only
        lo_te = T.predict(model, *d["test_inputs"], device)
        write_json(os.path.join(cell, "result.json"), {
            "condition": condition, "variant": v, "fold": f["fold"], "seed": seed, "window": CD.W, "labels": NT,
            "threshold": th, "validation": Mx.evaluate(lo_va, Yva, d["val_owners"], th),
            "val": save_array(cell, "val_logits.npy", lo_va), "val_source_rows": d["val_source_rows"],
            "updates_completed": res.updates_completed, "best_update": res.best_update,
            "best_validation_bce": res.best_val_bce, "cap_reached": res.cap_reached, "seconds": res.seconds,
            "parameters": res.parameters, "curve": res.curve,
            "budget": {k: budget[k] for k in ("shared_patience", "shared_update_budget")},
            "sealed_test": {**save_array(cell, "test_logits.npy", lo_te),
                            "source_rows": d["test_source_rows"], "owners": d["test_owners"]},
            "smoke": args.smoke})


def stage_lookup(args, out, condition):
    for f in pick_folds(condition, args.smoke):
        cell = os.path.join(out, "lookup", condition, f["fold"])
        if os.path.exists(os.path.join(cell, "result.json")):
            continue
        st_ = f["_steps"]
        tab = LK.table(CD.label_seqs(st_, f["train_runs"]))
        val_seqs, test_seqs = CD.label_seqs(st_, f["val_runs"]), CD.label_seqs(st_, f["test_runs"])
        _, _, Yva, _, rows_va = CD.windows(st_, f["val_runs"])
        _, _, _, own_te, rows_te = CD.windows(st_, f["test_runs"])
        rec = {"condition": condition, "fold": f["fold"], "smoke": args.smoke, "val_source_rows": rows_va,
               "validation_micro_f1": {}}
        os.makedirs(cell, exist_ok=True)
        for name, longest in (("longest", True), ("previous", False)):
            pv = LK.predictions(tab, val_seqs, LABEL_ID, longest)
            pt = LK.predictions(tab, test_seqs, LABEL_ID, longest)
            if pv.shape != Yva.shape or len(pt) != len(rows_te):
                raise SystemExit(f"lookup {f['fold']}: predictions do not line up with the windows")
            rec["validation_micro_f1"][name] = micro_f1(pv, Yva)
            rec[f"val_{name}"] = save_array(cell, f"val_{name}.npy", pv)
            rec[f"sealed_test_{name}"] = {**save_array(cell, f"test_{name}.npy", pt),
                                          "source_rows": rows_te, "owners": own_te}
        write_json(os.path.join(cell, "result.json"), rec)
        print(f"  lookup {condition} {f['fold']}: validation micro-F1 longest "
              f"{rec['validation_micro_f1']['longest']:.3f}, previous {rec['validation_micro_f1']['previous']:.3f}")


def stage_summary(args, out):
    lines = ["CASINOLIMIT: VALIDATION SUMMARY (descriptive; no test score; nothing is selected on it)",
             f"made {time.strftime('%Y-%m-%d %H:%M')}{'  SMOKE: NOT A RESULT' if args.smoke else ''}", "",
             f"{'condition':<18}{'model':<17}{'trainings':>10}{'val micro-F1 mean':>19}{'min':>8}{'max':>8}"
             f"{'hit budget':>12}"]
    for cond in S.CONDITIONS:
        for v in ENCODERS:
            base = os.path.join(out, "train", cond, v)
            recs = [read_json(os.path.join(dp, "result.json")) for dp, _, fs in os.walk(base) if "result.json" in fs]
            if not recs:
                continue
            f1 = [r["validation"]["micro_f1"] for r in recs]
            lines.append(f"{cond:<18}{v:<17}{len(recs):>10}{st.mean(f1):>19.3f}{min(f1):>8.3f}{max(f1):>8.3f}"
                         f"{sum(r['cap_reached'] for r in recs):>12}")
        base = os.path.join(out, "lookup", cond)
        if os.path.isdir(base):
            recs = [read_json(os.path.join(base, d, "result.json")) for d in sorted(os.listdir(base))
                    if os.path.exists(os.path.join(base, d, "result.json"))]
            for name in ("longest", "previous"):
                f1 = [r["validation_micro_f1"][name] for r in recs]
                if f1:
                    lines.append(f"{cond:<18}{'lookup ' + name:<17}{len(recs):>10}{st.mean(f1):>19.3f}"
                                 f"{min(f1):>8.3f}{max(f1):>8.3f}{'-':>12}")
    text = "\n".join(lines) + "\n"
    with open(os.path.join(out, "VALIDATION_SUMMARY.txt"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    print(text)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", default="check", choices=("check", "pilot", "train", "lookup", "summary", "all"))
    ap.add_argument("--condition", default="main", choices=S.CONDITIONS, help="for --stage train / lookup")
    ap.add_argument("--encoders", nargs="+", default=list(ENCODERS), choices=ENCODERS, help="for --stage train")
    ap.add_argument("--device", default="auto", choices=("auto", "cpu", "cuda"))
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--smoke", action="store_true", help="tiny budgets, 2 folds, 1 seed; NOT a result")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    if args.stage not in ("check", "summary") and not args.smoke and not S.APPROVED_ON:
        raise SystemExit("PROTOCOL_CL_1.0.md is not approved yet (cl_split.APPROVED_ON). Only --smoke runs "
                         "and --stage check are allowed.")
    out = os.path.join(HERE, "out_smoke" if args.smoke else "out")
    torch.set_num_threads(args.threads)
    device = T.device_of(args.device)
    print(f"casinolimit_encoder | stage {args.stage} | device {device}{' | SMOKE: not a result' if args.smoke else ''}")
    write_json(os.path.join(out, "environment.json"), {
        "python": sys.version.split()[0], "torch": torch.__version__, "numpy": np.__version__,
        "platform": platform.platform(), "cuda": torch.cuda.is_available(),
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None})
    with Lock(out):
        if args.stage in ("check", "all") and not stage_check(args, out):
            return 1
        if args.stage in ("pilot", "all"):
            stage_pilot(args, out, device)
        if args.stage == "train":
            stage_train(args, out, device, args.condition, args.encoders)
        if args.stage == "lookup":
            stage_lookup(args, out, args.condition)
        if args.stage == "all":
            for cond in S.CONDITIONS:
                stage_train(args, out, device, cond, ENCODERS)
                stage_lookup(args, out, cond)
        if args.stage in ("summary", "all"):
            stage_summary(args, out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
