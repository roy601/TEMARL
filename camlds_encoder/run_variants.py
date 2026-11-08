# -*- coding: utf-8 -*-
"""Validation-only design work on the GPU PC (protocol 1.1, Section 6; SELECTION_RULE.md).

    python camlds_encoder/run_variants.py --stage baseline_val --device cuda
    python camlds_encoder/run_variants.py --stage train --variant causal --device cuda
    python camlds_encoder/run_variants.py --stage train --variant allpos --device cuda
    python camlds_encoder/run_variants.py --stage train --variant repeat --device cuda
    python camlds_encoder/run_variants.py --stage train --variant asl --device cuda
    python camlds_encoder/run_variants.py --stage train --variant asl_long --device cuda
    python camlds_encoder/run_variants.py --stage train --variant gru_allpos --device cuda
    python camlds_encoder/run_variants.py --stage train --variant lstm_allpos --device cuda
    python camlds_encoder/run_variants.py --stage all --smoke --device cpu     # NOT a result

  baseline_val  loads each baseline checkpoint (encoder.pt, kept on the GPU PC), saves its
                validation outputs, and checks they reproduce the recorded validation BCE
  train         one cell per (fold, seed) for a variant, with the pilot's patience and budget.
                Saves validation outputs and sealed test outputs. No test score is computed.

Resumable; a finished cell is skipped. Uses the same lock as run.py.
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import data  # noqa: E402
import run as R  # noqa: E402
import variants as V  # noqa: E402
from port import Enc, Mx, NT, SPEC, T  # noqa: E402

CANDIDATES = ("causal", "allpos", "repeat", "asl", "asl_long", "gru_allpos", "lstm_allpos")
# GRU, LSTM and the ASL rerun: twice the pilot's budget (SELECTION_RULE.md). No allpos training
# reached 9,152 updates, so allpos is the same under this limit.
LONG_UPDATE_BUDGET = 18304
LONG_BUDGET_VARIANTS = (*V.SECONDARY, "asl_long")


def limits_for(variant, budget, smoke):
    """Patience and update budget of a variant. A smoke run always keeps its own tiny budget."""
    limits = {k: budget[k] for k in ("shared_patience", "shared_update_budget")}
    if variant in LONG_BUDGET_VARIANTS and not smoke:
        limits["shared_update_budget"] = LONG_UPDATE_BUDGET
    return limits


def save_logits(cell, name, arr):
    path = os.path.join(cell, name)
    np.save(path, arr.astype(np.float32))
    return {"file": name, "sha256": R.sha_file(path), "points": int(len(arr))}


def stage_baseline_val(args, out, device):
    """Validation outputs of the already-trained baseline, from its own checkpoints."""
    base = os.path.join(out, "train", "main", "Transformer")
    worst = 0.0
    for f in R.pick_folds("main", args.smoke):
        d = data.fold_data(f)
        Xva, Mva, Yva = d["val"]
        for s in (SPEC.MAIN_SEEDS[:1] if args.smoke else SPEC.MAIN_SEEDS):
            cell = os.path.join(base, f["fold"], f"s{s}")
            if os.path.exists(os.path.join(cell, "val_outputs.json")):
                continue
            ck = torch.load(os.path.join(cell, "encoder.pt"), map_location=device, weights_only=False)
            model = Enc.build_model("Transformer", data.W).to(device)
            model.load_state_dict(ck["state_dict"])
            lo = T.predict(model, Xva, Mva, device)
            rec = R.read_json(os.path.join(cell, "result.json"))
            bce = Mx.bce(lo, Yva)
            diff = abs(bce - rec["best_validation_bce"])
            worst = max(worst, diff)
            if diff > 1e-4:
                raise SystemExit(f"{f['fold']} s{s}: checkpoint gives validation BCE {bce:.6f}, "
                                 f"recorded {rec['best_validation_bce']:.6f}. Stop: wrong checkpoint?")
            R.write_json(os.path.join(cell, "val_outputs.json"), {
                "val": save_logits(cell, "val_logits.npy", lo), "val_source_rows": d["val_source_rows"],
                "val_bce_recomputed": bce, "val_bce_recorded": rec["best_validation_bce"]})
    print(f"  baseline validation outputs saved; largest BCE difference from the record: {worst:.2e}")


def stage_train(args, out, device):
    budget = R.read_json(os.path.join(out, "budget.json"))
    if budget.get("smoke") and not args.smoke:
        raise SystemExit("budget.json comes from a smoke run; it cannot be used for a real run.")
    limits = limits_for(args.variant, budget, args.smoke)
    seeds = SPEC.MAIN_SEEDS[:1] if args.smoke else SPEC.MAIN_SEEDS
    jobs = [(f, s) for f in R.pick_folds("main", args.smoke) for s in seeds]
    for i, (f, seed) in enumerate(jobs, 1):
        cell = os.path.join(out, "variants", args.variant, f["fold"], f"s{seed}")
        if os.path.exists(os.path.join(cell, "result.json")):
            continue
        print(f"  [{i}/{len(jobs)}] {args.variant} {f['fold']} s{seed}", flush=True)
        d = data.fold_data(f)
        res, model = V.train_variant(args.variant, data.W, seed, d["train"], d["val"],
                                     limits["shared_update_budget"], device=device, checkpoint_dir=cell,
                                     patience_checks=limits["shared_patience"], progress=args.verbose)
        T.load_best(model, res)
        Xva, Mva, Yva = d["val"]
        lo_va = T.predict(model, Xva, Mva, device)
        th = Mx.select_threshold(Mx._sigmoid(lo_va), Yva)
        lo_te = T.predict(model, *d["test_inputs"], device)
        R.write_json(os.path.join(cell, "result.json"), {
            "variant": args.variant, "family": f["family"], "fold": f["fold"], "seed": seed, "window": data.W,
            "labels": NT, "threshold": th, "validation": Mx.evaluate(lo_va, Yva, d["val_owners"], th),
            "val": save_logits(cell, "val_logits.npy", lo_va), "val_source_rows": d["val_source_rows"],
            "updates_completed": res.updates_completed, "best_update": res.best_update,
            "best_validation_bce": res.best_val_bce, "cap_reached": res.cap_reached, "seconds": res.seconds,
            "parameters": res.parameters, "curve": res.curve,
            "budget": limits,
            "sealed_test": {**save_logits(cell, "test_logits.npy", lo_te),
                            "source_rows": d["test_source_rows"], "owners": d["test_owners"]},
            "smoke": args.smoke})


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", required=True, choices=("baseline_val", "train", "all"))
    ap.add_argument("--variant", choices=CANDIDATES)
    ap.add_argument("--device", default="auto", choices=("auto", "cpu", "cuda"))
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    if args.stage == "train" and not args.variant:
        ap.error("--stage train needs --variant")
    out = os.path.join(HERE, "out_smoke" if args.smoke else "out")
    torch.set_num_threads(args.threads)
    device = T.device_of(args.device)
    print(f"run_variants | stage {args.stage} | variant {args.variant} | device {device}"
          f"{' | SMOKE: not a result' if args.smoke else ''}")
    with R.Lock(out):
        if args.stage in ("baseline_val", "all"):
            stage_baseline_val(args, out, device)
        if args.stage == "train":
            stage_train(args, out, device)
        if args.stage == "all":
            for v in CANDIDATES:
                args.variant = v
                stage_train(args, out, device)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
