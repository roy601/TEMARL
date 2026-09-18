# -*- coding: utf-8 -*-
"""
TEMARL v7 — confirmatory runner (main family and leave-one-script-out)
======================================================================
Executes exactly the design in `prereg_marl.py`, which must be committed
BEFORE this runs. Every (study, arm, learner, seed[, fold]) cell is written to
its own JSON file, so the run is

  * resumable   -- a finished cell is skipped; re-run the same command,
  * parallel    -- `--workers N` runs N independent cells at once,
  * guarded     -- a cell file records the fingerprint of everything it
                   depends on (frozen inputs, env config, prereg, code); cells
                   with a different fingerprint are never mixed, the runner
                   stops instead.

    python run_marl.py --study main --workers 4
    python run_marl.py --study loso --workers 4
    python run_marl.py --study main --smoke          # code-path test only

Baselines are scored on the very same test episodes as the learned teams of
the same seed (common random numbers), so every comparison is paired.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
CODE_FILES = ("env_marl.py", "scripts_marl.py", "baselines_marl.py", "mappo.py",
              "pretrain_marl.py", "encoders_marl.py", "prereg_marl.py",
              "run_marl.py", "env_config.json")


def _sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()[:16]


def fingerprint():
    import _frozen
    h = hashlib.sha256(_frozen.fingerprint().encode())
    for f in CODE_FILES:
        h.update(f.encode()); h.update(_sha(os.path.join(HERE, f)).encode())
    return h.hexdigest()[:16]


def cells(study, PR, arms=None, seeds=None):
    """The declared cells of a study, as dicts."""
    out = []
    if study == "main":
        for arm, learner in PR.MAIN_ARMS:
            if arms and arm not in arms:
                continue
            for s in (seeds or PR.SEEDS):
                out.append({"study": "main", "arm": arm, "learner": learner,
                            "seed": s, "fold": None})
    else:
        from scripts_marl import loso_folds
        for fold in loso_folds():
            for arm in PR.LOSO_ARMS:
                if arms and arm not in arms:
                    continue
                for s in (seeds or PR.LOSO_SEEDS):
                    out.append({"study": "loso", "arm": arm, "learner": "MAPPO",
                                "seed": s, "fold": fold["held_out"]})
    return out


def cell_name(c):
    f = "" if c["fold"] is None else "_%s" % c["fold"]
    return "%s_%s_%s_s%d%s" % (c["study"], c["arm"], c["learner"], c["seed"], f)


def run_cell(args):
    c, out_dir, smoke, threads, device, fp = args
    import torch
    torch.set_num_threads(threads)
    import _frozen  # noqa: F401
    import prereg_marl as PR
    from env_marl import SCRIPT_IDS, EnvConfig
    from mappo import SEED_TEST, summary, train
    from pretrain_marl import pretrain
    from scripts_marl import loso_folds

    cfg = EnvConfig(**json.load(open(os.path.join(HERE, "env_config.json"),
                                     encoding="utf-8"))["config"])
    if c["fold"] is None:
        pool, test_pool, test_seed = SCRIPT_IDS, SCRIPT_IDS, SEED_TEST + c["seed"]
    else:
        fold = [f for f in loso_folds() if f["held_out"] == c["fold"]][0]
        pool, test_pool = fold["train"], [fold["held_out"]]
        test_seed = SEED_TEST + 10_000 * (1 + SCRIPT_IDS.index(c["fold"])) + c["seed"]
    budget = PR.SMOKE_ENV_STEPS if smoke else PR.ENV_STEPS
    t0 = time.time()
    pre = pretrain(c["arm"], c["seed"], pool, device, smoke=smoke)
    out = train(pre["encoder"], cfg, pool, c["seed"], budget,
                centralised=(c["learner"] == "MAPPO"), device=device,
                test_pool=test_pool, n_test=PR.N_TEST if not smoke else 60,
                test_seed=test_seed)
    os.makedirs(os.path.join(out_dir, "checkpoints"), exist_ok=True)
    torch.save({"actor": out["actor"].state_dict(),
                "encoder": None if pre["encoder"] is None else pre["encoder"].state_dict(),
                "cell": c}, os.path.join(out_dir, "checkpoints", cell_name(c) + ".pt"))
    rec = {"cell": c, "fingerprint": fp, "smoke": smoke, "env_config": cfg.to_dict(),
           "pretrain": pre["metrics"], "curve": out["curve"],
           "best_update": out["best_update"], "val_best": out["val_best"],
           "env_steps": out["env_steps"], "seconds": time.time() - t0,
           "actor_params": out["actor_params"], "critic_params": out["critic_params"],
           "test": out["test_rows"], "test_h0": out["test_rows_h0"],
           "test_summary": summary(out["test_rows"]),
           "test_h0_summary": summary(out["test_rows_h0"])}
    path = os.path.join(out_dir, "cells", cell_name(c) + ".json")
    tmp = path + ".tmp"
    json.dump(rec, open(tmp, "w", encoding="utf-8"), default=float)
    os.replace(tmp, path)
    return cell_name(c), rec["test_summary"]["dwell"], rec["seconds"]


def run_baselines(study, PR, out_dir, smoke):
    """Reference policies on each seed's (and fold's) test episodes."""
    import _frozen  # noqa: F401
    from baselines_marl import (Beliefs, Fixed, Null, Planner, RandomPolicy,
                                Reactive, best_fixed, evaluate, tune_theta)
    from env_marl import SCRIPT_IDS, EnvConfig, EpisodeSource
    from mappo import SEED_TEST
    from scripts_marl import loso_folds
    cfg = EnvConfig(**json.load(open(os.path.join(HERE, "env_config.json"),
                                     encoding="utf-8"))["config"])
    gates = json.load(open(os.path.join(HERE, "results_marl", "gates.json"),
                           encoding="utf-8"))
    n = PR.N_TEST if not smoke else 60
    jobs = []
    if study == "main":
        for s in PR.SEEDS:
            jobs.append((None, s, SCRIPT_IDS, SCRIPT_IDS, SEED_TEST + s))
    else:
        for fold in loso_folds():
            for s in PR.LOSO_SEEDS:
                jobs.append((fold["held_out"], s, fold["train"], [fold["held_out"]],
                             SEED_TEST + 10_000 * (1 + SCRIPT_IDS.index(fold["held_out"])) + s))
    res = {}
    cache = {}
    for fold_id, s, pool, test_pool, seed in jobs:
        specs = EpisodeSource(seed, test_pool).take(n)
        B = Beliefs(pool)
        if fold_id is None:
            bf = gates["meta"]["best_fixed_joint"]
            th = {k: gates["meta"][k]["theta"] for k in ("transition/coord", "clairvoyant/coord")}
        else:
            if fold_id not in cache:
                sel = EpisodeSource(40_000 + 1, pool).take(300)
                bf_f, _ = best_fixed(sel[:120], cfg)
                cache[fold_id] = {
                    "bf": bf_f,
                    "transition/coord": tune_theta(lambda t: Planner("transition", True, B, t), sel, cfg),
                    "clairvoyant/coord": tune_theta(lambda t: Planner("clairvoyant", True, B, t), sel, cfg)}
            bf = cache[fold_id]["bf"]
            th = {k: cache[fold_id][k] for k in ("transition/coord", "clairvoyant/coord")}
        pols = {"null": Null(), "random": RandomPolicy(30_000 + s), "best_fixed": Fixed(bf),
                "reactive/naive": Reactive("naive"), "reactive/averse": Reactive("averse"),
                "transition/coord": Planner("transition", True, B, th["transition/coord"]),
                "clairvoyant/coord": Planner("clairvoyant", True, B, th["clairvoyant/coord"])}
        key = "%s_s%d" % (fold_id or "main", s)
        res[key] = {name: evaluate(p, specs, cfg) for name, p in pols.items()}
        res[key]["_meta"] = {"fold": fold_id, "seed": s, "best_fixed_joint": bf, "theta": th}
    path = os.path.join(out_dir, "baselines_%s.json" % study)
    json.dump(res, open(path, "w", encoding="utf-8"), default=float)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", choices=("main", "loso"), required=True)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--threads", type=int, default=3)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--arms", nargs="*")
    ap.add_argument("--seeds", nargs="*", type=int)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    import prereg_marl as PR
    if not args.smoke:
        PR._check()

    out_dir = os.path.join(HERE, "results_marl", ("smoke_" if args.smoke else "") + args.study)
    os.makedirs(os.path.join(out_dir, "cells"), exist_ok=True)
    fp = fingerprint()
    todo, stale = [], []
    for c in cells(args.study, PR, args.arms, args.seeds):
        p = os.path.join(out_dir, "cells", cell_name(c) + ".json")
        if os.path.exists(p):
            if json.load(open(p, encoding="utf-8")).get("fingerprint") != fp:
                stale.append(cell_name(c))
            continue
        todo.append(c)
    print("=" * 100)
    print("  TEMARL v7 — %s study%s | fingerprint %s | prereg %s"
          % (args.study, " (SMOKE)" if args.smoke else "", fp, PR.PREREG_ID))
    print("  %d cells to run, %d already done" % (len(todo), len(cells(args.study, PR, args.arms, args.seeds)) - len(todo)))
    print("=" * 100)
    if stale:
        print("  !! %d finished cells were produced under a DIFFERENT fingerprint "
              "(code, config or prereg changed):" % len(stale))
        for s in stale[:10]:
            print("     ", s)
        print("  They cannot be mixed with new cells. Move them away, or restore the "
              "exact code they were run with. Stopping.")
        sys.exit(2)
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(run_cell, (c, out_dir, args.smoke, args.threads, args.device, fp))
                for c in todo]
        for k, f in enumerate(as_completed(futs), 1):
            name, dwell, sec = f.result()
            print("  [%3d/%d] %-44s test dwell %6.2f  (%4.0fs; elapsed %.0f min)"
                  % (k, len(todo), name, dwell, sec, (time.time() - t0) / 60))
    print("  baselines ->", os.path.relpath(run_baselines(args.study, PR, out_dir, args.smoke), HERE))
    print("=" * 100)


if __name__ == "__main__":
    main()
