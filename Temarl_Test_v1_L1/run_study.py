# -*- coding: utf-8 -*-
"""
Temarl_Test_v1_L1 -- study runner
==================================
Stages, in order. Each is resumable: a completed cell is never retrained, and
an interrupted cell restarts from initialisation rather than from a partial
state (a half-trained model is not a checkpoint).

  audit      corpus, splits, label support, similarity, window coverage
  pilots     3 seeds x every arm x every window, trained to a cap, full curves
             kept so all patience rules can be replayed afterwards
  budget     choose shared patience and shared update budget FROM PILOTS ONLY
  predict    main prediction cells at the frozen budget
  ladder     baseline reference ladder for the deception environment
  rl         main deception cells at the reference window
  context    deception at ONE preselected longer window
  report     tables

Usage
-----
    python run_study.py --stage all --device cuda
    python run_study.py --stage all --smoke            # minutes, not hours
    python run_study.py --stage predict --output runs/my_run
    python run_study.py --stage all --aggregation mean # sensitivity condition

Windows safety: every JSON write goes to a temporary file and is then
atomically replaced, so an interrupted write cannot corrupt a result file.
A `.running` lock prevents two processes writing the same output directory.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import sys
import time
from typing import Dict, List, Optional, Sequence

import numpy as np
import torch

import _frozen
import baselines_cmd as B
import command_data as D
import encoders_cmd as Enc
import env_cmd as E
import mappo_cmd as M
import metrics_cmd as Mx
import stats_cmd as St
import study_spec as SPEC
import train_cmd as T

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT = os.path.join(HERE, "results", "run")


# ── io helpers ──────────────────────────────────────────────────────────────

def write_json(path: str, obj) -> None:
    """Atomic write: temp file then replace. Safe on Windows."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=1, default=_jsonable)
    os.replace(tmp, path)


def _jsonable(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (set, tuple)):
        return list(o)
    raise TypeError(f"not JSON serialisable: {type(o)}")


def read_json(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


class Lock:
    def __init__(self, out: str):
        self.path = os.path.join(out, ".running")

    def __enter__(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if os.path.exists(self.path):
            info = open(self.path, encoding="utf-8").read().strip()
            raise SystemExit(
                f"Output directory is locked by:\n  {info}\n"
                f"If that process is gone, delete {self.path} and rerun.")
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(f"pid={os.getpid()} host={platform.node()} "
                    f"started={time.strftime('%Y-%m-%d %H:%M:%S')}")
        return self

    def __exit__(self, *exc):
        if os.path.exists(self.path):
            os.remove(self.path)


def cell_done(path: str) -> bool:
    return os.path.exists(path)


# Smoke mode runs a reduced but SELF-CONSISTENT design: the arms trained in the
# prediction stage must be exactly the arms the RL stage needs an encoder for,
# otherwise RL fails on a missing checkpoint (it refuses to substitute an
# untrained one). One definition, used by every stage.
SMOKE_ENCODERS = ("Transformer", "GRU")


def active_arms(smoke: bool):
    """(prediction arms, RL arms, RL controls) for this run."""
    if not smoke:
        return (SPEC.PREDICTION_ARMS, SPEC.RL_ARMS, SPEC.RL_CONTROLS)
    enc = SMOKE_ENCODERS
    pred = enc + (SPEC.ORDER_FREE,)
    rl = tuple((e, l) for l in SPEC.LEARNERS for e in enc)
    ctl = tuple((c, l) for l in SPEC.LEARNERS
                for c in (SPEC.ORDER_FREE, SPEC.NO_HISTORY))
    return pred, rl, ctl


# ── data ────────────────────────────────────────────────────────────────────

class Corpus:
    def __init__(self, split_seed: int, held_out: Optional[str], smoke: bool):
        self.runs = D.load_runs()
        self.split, self.notes = D.split_runs(self.runs, split_seed, held_out)
        self.scenario_of = {r["id"]: r["scenario"] for r in self.runs}
        self.smoke = smoke

    def windows(self, part: str, window: int):
        X, Mk, Y, owners, avail = D.windows(self.split[part], window)
        return X, Mk, Y, owners, avail

    def data(self, part: str, window: int):
        X, Mk, Y, _, _ = self.windows(part, window)
        return X, Mk, Y


# ── prediction cells ────────────────────────────────────────────────────────

def train_prediction_cell(corpus: Corpus, arm: str, window: int, seed: int,
                          max_updates: int, sampler: str, device,
                          out_dir: str, patience: Optional[int],
                          verbose: bool) -> dict:
    tr = corpus.data("train", window)
    va = corpus.data("validation", window)
    res, model = T.train_one(arm, window, seed, tr, va, max_updates,
                             sampler_kind=sampler, device=device,
                             checkpoint_dir=out_dir, patience_checks=patience,
                             progress=verbose)

    Xva, Mva, Yva = va
    Xte, Mte, Yte = corpus.data("test", window)
    _, _, _, va_owners, _ = corpus.windows("validation", window)
    _, _, _, te_owners, _ = corpus.windows("test", window)

    def score(tag: str) -> dict:
        lo_va = T.predict(model, Xva, Mva, device)
        lo_te = T.predict(model, Xte, Mte, device)
        prob_va = 1.0 / (1.0 + np.exp(-np.clip(lo_va, -60, 60)))
        th = Mx.select_threshold(prob_va, Yva)       # validation only
        return {
            "checkpoint": tag, "threshold": th,
            "validation": Mx.evaluate(lo_va, Yva, va_owners, th, corpus.scenario_of),
            "test": Mx.evaluate(lo_te, Yte, te_owners, th, corpus.scenario_of),
            "test_per_label": Mx.per_label_report(lo_te, Yte, th),
        }

    final = score("final")                           # secondary
    T.load_best(model, res)
    best = score("validation_best")                  # PRIMARY

    return {
        "arm": arm, "window": window, "seed": seed, "sampler": sampler,
        "updates_completed": res.updates_completed,
        "best_update": res.best_update,
        "best_validation_bce": res.best_val_bce,
        "cap_reached": res.cap_reached,
        "seconds": res.seconds,
        "exposure": res.exposure,
        "parameters": res.parameters,
        "peak_memory_mb": res.peak_memory_mb,
        "curve": res.curve,
        "improvements": res.improvements,
        "patience_resets": res.patience_resets,
        "primary": best, "secondary": final,
    }


# ── stages ──────────────────────────────────────────────────────────────────

def stage_audit(corpus: Corpus, out: str) -> dict:
    a = D.audit(corpus.split, corpus.notes, SPEC.WINDOWS)
    a["frozen_inputs"] = _frozen.verify(strict=True)
    a["environment"] = {
        "python": sys.version.split()[0], "torch": torch.__version__,
        "numpy": np.__version__, "platform": platform.platform(),
        "cuda_available": torch.cuda.is_available(),
        "cuda_device": (torch.cuda.get_device_name(0)
                        if torch.cuda.is_available() else None),
    }
    write_json(os.path.join(out, "audit.json"), a)
    return a


def stage_pilots(corpus: Corpus, out: str, device, args) -> dict:
    n_train = len(corpus.data("train", SPEC.REFERENCE_WINDOW)[0])
    cap = max(SPEC.PILOT_MIN_UPDATES,
              int(SPEC.PILOT_EPOCH_EQUIVALENTS * n_train / SPEC.BATCH_SIZE))
    if args.smoke:
        cap = 128
    seeds = SPEC.PILOT_SEEDS[:1] if args.smoke else SPEC.PILOT_SEEDS
    windows = (SPEC.REFERENCE_WINDOW,) if args.smoke else SPEC.WINDOWS
    arms, _, _ = active_arms(args.smoke)

    print(f"  pilot cap = {cap} updates "
          f"({cap * SPEC.BATCH_SIZE / n_train:.0f} epoch-equivalents)")
    results: Dict[str, List[T.TrainResult]] = {}
    curves: Dict[str, List[dict]] = {}

    overlap_arms = SMOKE_ENCODERS if args.smoke else SPEC.ENCODERS
    jobs = [(a, w, s, "ordinary") for a in arms for w in windows for s in seeds]
    jobs += [(a, SPEC.REFERENCE_WINDOW, s, "overlap")
             for a in overlap_arms for s in seeds]

    for i, (arm, w, seed, sampler) in enumerate(jobs, 1):
        tag = f"{arm}_W{w}_{sampler}_s{seed}"
        path = os.path.join(out, "pilot", tag, "result.json")
        if cell_done(path):
            rec = read_json(path)
        else:
            print(f"  [{i}/{len(jobs)}] pilot {tag}", flush=True)
            tr, va = corpus.data("train", w), corpus.data("validation", w)
            res, _ = T.train_one(arm, w, seed, tr, va, cap,
                                 sampler_kind=sampler, device=device,
                                 patience_checks=None, progress=args.verbose)
            rec = {"arm": arm, "window": w, "seed": seed, "sampler": sampler,
                   "curve": res.curve, "best_update": res.best_update,
                   "best_validation_bce": res.best_val_bce,
                   "cap_reached": res.cap_reached, "seconds": res.seconds,
                   "updates_completed": res.updates_completed}
            write_json(path, rec)
        key = f"{rec['arm']}_W{rec['window']}_{rec['sampler']}"
        curves[f"{key}_s{rec['seed']}"] = rec["curve"]
        r = T.TrainResult(arm=rec["arm"], window=rec["window"], seed=rec["seed"],
                          sampler=rec["sampler"],
                          updates_completed=rec["updates_completed"],
                          curve=rec["curve"], best_update=rec["best_update"],
                          best_val_bce=rec["best_validation_bce"],
                          cap_reached=rec["cap_reached"])
        results.setdefault(key, []).append(r)

    patience = T.choose_patience(curves, SPEC.PATIENCE_GRID, SPEC.PATIENCE_TOLERANCE)
    budget = T.choose_update_budget(results, SPEC.BUDGET_FACTOR, SPEC.VAL_EVERY_UPDATES)
    block = {"cap": cap, "n_pilot_cells": len(jobs),
             "patience_selection": patience, "budget_selection": budget,
             "shared_patience": patience["chosen_patience"],
             "shared_update_budget": budget["shared_update_budget"],
             "convergence_unresolved": budget["configurations_with_unresolved_cap"]}
    write_json(os.path.join(out, "budget.json"), block)
    print(f"  -> patience {block['shared_patience']} checks, "
          f"budget {block['shared_update_budget']} updates")
    if block["convergence_unresolved"]:
        print(f"  [!] convergence unresolved for "
              f"{len(block['convergence_unresolved'])} configuration(s); "
              f"reported, not silently accepted")
    return block


def stage_predict(corpus: Corpus, out: str, device, args, budget: dict) -> None:
    updates = budget["shared_update_budget"]
    patience = budget["shared_patience"]
    seeds = SPEC.MAIN_SEEDS[:2] if args.smoke else SPEC.MAIN_SEEDS
    windows = (SPEC.REFERENCE_WINDOW,) if args.smoke else SPEC.WINDOWS
    arms, _, _ = active_arms(args.smoke)
    overlap_arms = SMOKE_ENCODERS if args.smoke else SPEC.ENCODERS

    jobs = [(a, w, s, "ordinary") for a in arms for w in windows for s in seeds]
    jobs += [(SPEC.NO_HISTORY, SPEC.REFERENCE_WINDOW, s, "ordinary") for s in seeds]
    jobs += [(a, SPEC.REFERENCE_WINDOW, s, "overlap")
             for a in overlap_arms for s in seeds]

    for i, (arm, w, seed, sampler) in enumerate(jobs, 1):
        tag = f"{arm}_W{w}_{sampler}_s{seed}"
        cell = os.path.join(out, "prediction", tag)
        if cell_done(os.path.join(cell, "result.json")):
            continue
        print(f"  [{i}/{len(jobs)}] predict {tag}", flush=True)
        rec = train_prediction_cell(corpus, arm, w, seed, updates, sampler,
                                    device, cell, patience, args.verbose)
        write_json(os.path.join(cell, "result.json"), rec)


def stage_ladder(corpus: Corpus, out: str, cfg: E.EnvConfig, args) -> dict:
    path = os.path.join(out, "ladder.json")
    if cell_done(path):
        return read_json(path)
    meta = E.scenario_metadata()
    vr = 2 if args.smoke else SPEC.RL_VAL_REPEATS
    tr = 2 if args.smoke else SPEC.RL_TEST_REPEATS
    va, _ = E.evaluation_specs(corpus.split["validation"], vr, 700_001, meta)
    te, _ = E.evaluation_specs(corpus.split["test"], tr, 700_002, meta)
    max_steps = max(len(r["commands"]) for r in corpus.runs)
    print(f"  ladder: {len(va)} validation / {len(te)} test episodes")
    L = B.ladder(va, te, cfg, max_steps)
    L["headroom_test"] = {m: B.headroom(L["test"], m) for m in ("dwell", "depth")}
    L["max_steps"] = max_steps
    write_json(path, L)
    return L


def _encoder_for(out: str, arm: str, window: int, seed: int, device):
    """Load the frozen validation-best predictor for an RL cell."""
    if arm == SPEC.NO_HISTORY:
        return None
    ckpt = os.path.join(out, "prediction",
                        f"{arm}_W{window}_ordinary_s{seed}", "encoder.pt")
    if not os.path.exists(ckpt):
        raise FileNotFoundError(
            f"Missing encoder checkpoint {ckpt}. Run --stage predict first; "
            f"RL must not silently train on a fresh untrained encoder.")
    blob = torch.load(ckpt, map_location=device, weights_only=True)
    model = Enc.build_model(arm, window)
    model.load_state_dict(blob["state_dict"])
    return model


def stage_rl(corpus: Corpus, out: str, cfg: E.EnvConfig, device, args,
             window: int, label: str, arms) -> None:
    meta = E.scenario_metadata()
    vr = 2 if args.smoke else SPEC.RL_VAL_REPEATS
    tr = 2 if args.smoke else SPEC.RL_TEST_REPEATS
    steps = 24_576 if args.smoke else SPEC.RL_ENV_STEPS
    seeds = SPEC.RL_SEEDS[:2] if args.smoke else SPEC.RL_SEEDS
    va, _ = E.evaluation_specs(corpus.split["validation"], vr, 800_001, meta)
    te, te_labels = E.evaluation_specs(corpus.split["test"], tr, 800_002, meta)
    max_steps = max(len(r["commands"]) for r in corpus.runs)

    jobs = [(a, l, s) for (a, l) in arms for s in seeds]
    for i, (arm, learner, seed) in enumerate(jobs, 1):
        tag = f"{arm}_{learner}_W{window}_s{seed}"
        cell = os.path.join(out, label, tag)
        if cell_done(os.path.join(cell, "result.json")):
            continue
        print(f"  [{i}/{len(jobs)}] {label} {tag}", flush=True)
        enc = _encoder_for(out, arm, window, seed, device)
        r = M.train(enc, cfg, corpus.split["train"], va, te, seed=seed,
                    env_steps=steps, window=window, max_steps=max_steps,
                    centralised=(learner == "MAPPO"), device=str(device),
                    verbose=args.verbose)
        actor_state = r.pop("actor_state")
        os.makedirs(cell, exist_ok=True)
        torch.save({"arm": arm, "learner": learner, "window": window,
                    "seed": seed, "state_dict": actor_state},
                   os.path.join(cell, "actor.pt"))
        r.update({"arm": arm, "learner": learner, "episode_labels": te_labels})
        write_json(os.path.join(cell, "result.json"), r)


def pick_context_window(out: str) -> Optional[int]:
    """One longer window, chosen on POOLED VALIDATION prediction only.

    Declared in `study_spec.CONTEXT_WINDOW_RULE` before any result existed:
    all six encoder-learner combinations are retrained at whichever of 32 / 64
    has the better pooled validation micro-F1 -- never only the architecture
    that happens to lead.
    """
    pool: Dict[int, List[float]] = {}
    root = os.path.join(out, "prediction")
    if not os.path.isdir(root):
        return None
    for name in os.listdir(root):
        p = os.path.join(root, name, "result.json")
        if not os.path.exists(p):
            continue
        rec = read_json(p)
        if rec["sampler"] != "ordinary" or rec["arm"] not in SPEC.ENCODERS:
            continue
        if rec["window"] in (32, 64):
            pool.setdefault(rec["window"], []).append(
                rec["primary"]["validation"][SPEC.PRIMARY_PREDICTION_METRIC])
    if not pool:
        return None
    return max(pool, key=lambda w: float(np.mean(pool[w])))


# ── main ────────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", default="all",
                    choices=("all", "audit", "pilots", "predict", "ladder",
                             "rl", "context", "report"))
    ap.add_argument("--output", default=DEFAULT_OUT)
    ap.add_argument("--device", default="auto", choices=("auto", "cpu", "cuda"))
    ap.add_argument("--split-seed", type=int, default=D.DEFAULT_SPLIT_SEED)
    ap.add_argument("--held-out", choices=[f"S{i}" for i in range(1, 8)],
                    help="scenario-level holdout; use a SEPARATE output dir")
    ap.add_argument("--aggregation", default=SPEC.AGGREGATION_PRIMARY,
                    choices=E.AGGREGATIONS,
                    help="set-based engagement rule; 'mean' is the sensitivity "
                         "condition and needs its own output directory")
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--smoke", action="store_true",
                    help="tiny budgets end-to-end; NOT a scientific result")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    torch.set_num_threads(max(1, args.threads))
    device = T.device_of(args.device)
    out = os.path.abspath(args.output)

    print("=" * 78)
    print("  Temarl_Test_v1_L1 -- command-level multi-label deception study")
    print("=" * 78)
    print(f"  output     : {out}")
    print(f"  device     : {device}"
          + (f" ({torch.cuda.get_device_name(0)})" if device.type == "cuda" else ""))
    print(f"  aggregation: {args.aggregation}   split seed: {args.split_seed}"
          + (f"   held out: {args.held_out}" if args.held_out else ""))
    if args.smoke:
        print("  [SMOKE] tiny budgets; excluded from scientific conclusions")
    print()

    corpus = Corpus(args.split_seed, args.held_out, args.smoke)
    cfg = E.EnvConfig(aggregation=args.aggregation)
    stage = args.stage

    with Lock(out):
        write_json(os.path.join(out, "manifest.json"), {
            "spec": {k: v for k, v in vars(SPEC).items()
                     if k.isupper() and not k.startswith("_")},
            "args": vars(args), "device": str(device),
            "env_config": cfg.to_dict(),
            "started": time.strftime("%Y-%m-%d %H:%M:%S"),
            "smoke": args.smoke,
        })

        if stage in ("all", "audit"):
            print("[1/7] audit")
            stage_audit(corpus, out)

        budget = None
        if stage in ("all", "pilots"):
            print("[2/7] pilots")
            budget = stage_pilots(corpus, out, device, args)
        if budget is None and os.path.exists(os.path.join(out, "budget.json")):
            budget = read_json(os.path.join(out, "budget.json"))

        if stage in ("all", "predict"):
            if budget is None:
                raise SystemExit("No budget.json; run --stage pilots first.")
            print("[3/7] prediction")
            stage_predict(corpus, out, device, args, budget)

        if stage in ("all", "ladder"):
            print("[4/7] baseline ladder")
            stage_ladder(corpus, out, cfg, args)

        if stage in ("all", "rl"):
            print("[5/7] deception (reference window)")
            _, rl_arms, rl_ctl = active_arms(args.smoke)
            stage_rl(corpus, out, cfg, device, args, SPEC.REFERENCE_WINDOW,
                     "rl", list(rl_arms) + list(rl_ctl))

        if stage in ("all", "context"):
            w = pick_context_window(out)
            if w is None:
                print("[6/7] context: skipped (no 32/64 prediction results)")
            else:
                print(f"[6/7] context window = {w} "
                      f"(pooled validation {SPEC.PRIMARY_PREDICTION_METRIC})")
                write_json(os.path.join(out, "context_window.json"),
                           {"window": w, "rule": SPEC.CONTEXT_WINDOW_RULE})
                _, rl_arms, _ = active_arms(args.smoke)
                stage_rl(corpus, out, cfg, device, args, w, "context",
                         list(rl_arms))

        if stage in ("all", "report"):
            print("[7/7] report")
            import report_study
            report_study.build(out)

    print("\ndone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
