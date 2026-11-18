# -*- coding: utf-8 -*-
"""Protocol D1.1 runner: hyperparameter sensitivity of the history effect (PROTOCOL_D1.1.md).
Test outputs are SEALED, as in D1.0.

    python camlds_real_full_arch/run_d1_1.py --device cuda --preflight   # 96 allpos checkpoints, seeds 0-2
    python camlds_real_full_arch/run_d1_1.py --device cuda --timing      # one 15-epoch cell + dry-run check
    python camlds_real_full_arch/run_d1_1.py --device cuda               # 1,728 cells, resumable
    python camlds_real_full_arch/run_d1_1.py --smoke                     # code check, tiny, no freeze needed

Cells: 9 settings (learning rate {1e-4, 5e-4, 1e-3} x PPO epochs {5, 10, 15}) x allpos and NoHistory
(MAPPO) x 32 folds x seeds 0-2. Each cell is a D1.0 primary cell (run_d1.setting(None), the protocol 1.2
encoder of the same fold and seed, policy checkpoint by validation E1, validation seed 100000+seed, test
seed 200000+seed, 20 repeats, sealed test) except for the two swept settings. The D1.0 setting
(5e-4, 10 epochs) is trained again here, never copied from D1.0, so no D1.0 sealed file is read twice.
Real runs refuse unless D1.0's spec and D1.1's spec both pass and a passing D1.1 preflight covers every
checkpoint the run needs.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import itertools
import json
import sys
import time
from pathlib import Path

import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_d1 as R  # noqa: E402
import spec_d1  # noqa: E402
import spec_d1_1  # noqa: E402

P, marl, data = R.P, R.marl, R.data
ARMS = R.PRIMARY_ARMS                      # allpos, NoHistory
LEARNER = "MAPPO"
SEEDS = (0, 1, 2)
LRS = (1e-4, 5e-4, 1e-3)                   # subset of Yu et al. 2022, Table 13: {1e-4, 5e-4, 7e-4, 1e-3}
EPOCHS = (5, 10, 15)                       # Yu et al. 2022, Table 13 (SMAC, Hanabi, Football): {5, 10, 15}
DEFAULT = {"lr": 5e-4, "ppo_epochs": 10}   # the D1.0 setting (mappo_cmd.HP), the centre of the grid


def config_name(c: dict) -> str:
    return f"lr{c['lr']:.0e}_ep{c['ppo_epochs']:02d}"


# grid order = lr ascending, then epochs ascending (the tie-break order after the D1.0 setting)
GRID = {config_name({"lr": lr, "ppo_epochs": ep}): {"lr": lr, "ppo_epochs": ep}
        for lr, ep in itertools.product(LRS, EPOCHS)}
DEFAULT_NAME = config_name(DEFAULT)
TIMING_CONFIG = config_name({"lr": 1e-3, "ppo_epochs": 15})   # the most expensive update phase
OUT = HERE / "results_d1_1"

if {k: marl.HP[k] for k in DEFAULT} != DEFAULT:
    raise RuntimeError("mappo_cmd.HP no longer holds the D1.0 setting that D1.1 is centred on")


@contextlib.contextmanager
def hp(config: str):
    """Set the swept settings of one grid point in mappo_cmd.HP and restore the previous values after,
    also on an exception. Nothing else in HP changes."""
    values = GRID[config]
    old = {k: marl.HP[k] for k in values}
    marl.HP.update(values)
    try:
        yield dict(marl.HP)
    finally:
        marl.HP.update(old)


def cell_dir(out: Path, config: str, arm: str, fold_id: str, seed: int) -> Path:
    return out / "cells" / config / arm / fold_id / f"s{seed}" / LEARNER


def run_cell(arm, config, fold, seed, args, dest: Path, test: bool):
    """run_d1.run_cell for one grid point: the same steps in the same order, with the setting's HP."""
    cfg, order = R.setting(None)
    va = R.specs(P.runs(fold, "val"), R.VAL_SEED + seed, args.eval_repeats, cfg)
    te = R.specs(P.runs(fold, "test"), R.TEST_SEED + seed, args.eval_repeats, cfg) if test else []
    model, enc = R.load_encoder(arm, fold, seed, Path(args.encoder_root), args.device,
                                cell=dest.parent, order=order)
    t0 = time.time()
    with hp(config) as used:
        res = marl.train(model, cfg, P.runs(fold, "train"), va, te, seed, args.env_steps, data.W, 64,
                         True, args.device, args.verbose)
    dest.mkdir(parents=True, exist_ok=True)
    torch.save(res.pop("actor_state"), dest / "actor.pt")
    sealed = {"test": res.pop("test"), "test_summary": res.pop("test_summary"),
              "test_h0_summary": res.pop("test_h0_summary")}
    blob = json.dumps(sealed, sort_keys=True).encode("utf-8")
    if test:
        (dest / "sealed_test.json").write_bytes(blob)
    res.update(protocol="D1.1", config=config, hp=used, arm=arm, learner=LEARNER, fold=fold["fold"],
               family=fold["family"], seed=seed, test_runs=fold["test_runs"], encoder=enc,
               env_config=cfg.to_dict(), order=order, setting="primary",
               sealed_test_sha256=R.sha_bytes(blob) if test else None, wall_seconds=time.time() - t0,
               eval_repeats=args.eval_repeats, val_seed=R.VAL_SEED + seed, test_seed=R.TEST_SEED + seed)
    P.write(dest / "result.json", res)
    return res


def validation_summary(out: Path):
    rows = []
    for p in sorted(out.glob("cells/*/*/*/s*/*/result.json")):
        r = json.loads(p.read_text(encoding="utf-8"))
        rows.append(f"| {r['config']} | {r['arm']} | {r['fold']} | {r['seed']} | {r['best_update']} | "
                    f"{r['best_validation_dwell']:.3f} | {r['wall_seconds']:.0f} |")
    head = ["# D1.1 validation summary (no test number appears here)", "",
            "| setting | arm | fold | seed | best update | best validation E1 | seconds |",
            "|---|---|---|---|---|---|---|"]
    (out / "VALIDATION_SUMMARY.md").write_text("\n".join(head + rows) + "\n", encoding="utf-8")


def spec_sha():
    return hashlib.sha256(spec_d1_1.SPEC.read_bytes()).hexdigest() if spec_d1_1.SPEC.exists() else None


def needed_checkpoints(arms, folds, seeds):
    return {(arm, f["fold"], s) for arm in arms if arm != "NoHistory" for f in folds for s in seeds}


def preflight(a, folds):
    """Load every protocol 1.2 checkpoint the cells need and check its validation BCE. No training,
    no test data. Writes PREFLIGHT.json (with the D1.1 spec's SHA-256) in the output directory."""
    ok, bad = [], []
    for arm, fold_id, seed in sorted(needed_checkpoints(a.arms, folds, a.seeds)):
        f = next(x for x in folds if x["fold"] == fold_id)
        try:
            _, info = R.load_encoder(arm, f, seed, Path(a.encoder_root), a.device)
            ok.append({**info, "fold": fold_id, "seed": seed})
        except (FileNotFoundError, ValueError, RuntimeError, KeyError) as e:
            bad.append({"arm": arm, "fold": fold_id, "seed": seed, "error": f"{type(e).__name__}: {e}"})
    rep = {"pass": not bad and bool(ok), "spec_sha256": spec_sha(), "checked": len(ok) + len(bad),
           "ok": [[r["arm"], r["fold"], r["seed"]] for r in ok], "failures": bad, "checkpoints": ok}
    P.write(a.output / "PREFLIGHT.json", rep)
    print(f"D1.1 preflight: {'PASS' if rep['pass'] else 'FAIL'} ({len(ok)} checkpoints reproduce their "
          f"validation BCE, {len(bad)} failures) -> {a.output / 'PREFLIGHT.json'}")
    for b in bad[:10]:
        print("  ", b)
    return rep


def require_preflight(out: Path, need):
    pf = out / "PREFLIGHT.json"
    rep = json.loads(pf.read_text(encoding="utf-8")) if pf.exists() else None
    if rep is None or not rep["pass"] or rep["spec_sha256"] != spec_sha():
        raise SystemExit("run --preflight first, after the D1.1 freeze, with the same output directory")
    missing = need - {tuple(x) for x in rep["ok"]}
    if missing:
        raise SystemExit(f"preflight did not check {len(missing)} needed checkpoints, e.g. {sorted(missing)[:3]}")


def identity_of(a, all_folds):
    """Everything that decides what a cell contains (checked on every start, as in D1.0)."""
    cfg, order = R.setting(None)
    return {"protocol": "D1.1", "spec_d1": json.loads(spec_d1.SPEC.read_text(encoding="utf-8")),
            "spec_d1_1": json.loads(spec_d1_1.SPEC.read_text(encoding="utf-8")),
            "base_hp": dict(marl.HP), "grid": GRID, "env_config": cfg.to_dict(), "order": order,
            "env_steps": a.env_steps, "eval_repeats": a.eval_repeats,
            "val_seed": R.VAL_SEED, "test_seed": R.TEST_SEED,
            "folds": [{k: v for k, v in f.items() if k != "_steps"} for f in all_folds]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    ap.add_argument("--output", type=Path, default=OUT)
    ap.add_argument("--encoder-root", default=str(P.REPO / "camlds_encoder" / "out"))
    ap.add_argument("--arms", nargs="+", choices=ARMS, default=list(ARMS))
    ap.add_argument("--configs", nargs="+", choices=list(GRID), default=list(GRID))
    ap.add_argument("--folds", nargs="+")
    ap.add_argument("--seeds", nargs="+", type=int, default=list(SEEDS))
    ap.add_argument("--env-steps", type=int, default=2_000_000)
    ap.add_argument("--eval-repeats", type=int, default=20)
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--timing", action="store_true",
                    help=f"one cell (first fold, seed 0, allpos, {TIMING_CONFIG}) + its dry-run check, no test")
    ap.add_argument("--preflight", action="store_true",
                    help="load and check every protocol 1.2 checkpoint the cells need; no training, no test")
    ap.add_argument("--smoke", action="store_true", help="tiny code check; NoHistory; no test")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    if set(a.seeds) - set(SEEDS):
        raise SystemExit("D1.1 uses seeds 0-2 only")
    torch.set_num_threads(a.threads)
    if a.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable")
    all_folds = P.ordered_folds("frozen")
    folds = [f for f in all_folds if not a.folds or f["fold"] in a.folds]
    if a.folds and set(a.folds) - {f["fold"] for f in folds}:
        raise ValueError("unknown fold")

    if a.smoke:
        marl.HP.update(n_envs=2, rollout_len=4, n_evals=1)         # the swept settings stay the grid's
        a.env_steps, a.eval_repeats = 8, 1
        smoke_configs = a.configs if a.configs != list(GRID) else [DEFAULT_NAME, TIMING_CONFIG]
        for config in smoke_configs:
            dest = cell_dir(a.output / "smoke", config, "NoHistory", folds[0]["fold"], 0)
            run_cell("NoHistory", config, folds[0], 0, a, dest, test=False)
            print("smoke OK:", dest)
        return
    if a.preflight:
        rep = preflight(a, folds)
        raise SystemExit(0 if rep["pass"] else 1)
    if a.timing:
        dest = cell_dir(a.output / "timing", TIMING_CONFIG, "allpos", folds[0]["fold"], 0)
        r = run_cell("allpos", TIMING_CONFIG, folds[0], 0, a, dest, test=False)
        n = len(all_folds) * len(SEEDS) * len(GRID) * len(ARMS)
        print(f"timing: one {TIMING_CONFIG} cell {r['wall_seconds']:.0f} s on {a.device} "
              f"-> {n} D1.1 cells at most about {n * r['wall_seconds'] / 3600:.1f} h (test episodes not included)")
        model, _ = R.load_encoder("allpos", folds[0], 0, Path(a.encoder_root), a.device, cell=dest.parent)
        got, rec = R.revalidate(dest, folds[0], 0, model, a.device, R.setting(None)[0])
        same = abs(got - rec) <= 1e-9
        P.write(dest.parent / "TIMING_DRY_RUN.json", {"device": a.device, "config": TIMING_CONFIG, "recorded": rec,
                                                      "measured": got, "pass": same, "seconds": r["wall_seconds"]})
        print(f"dry-run reproduction on {a.device}: recorded {rec!r}, re-evaluated {got!r} -> "
              f"{'PASS' if same else 'FAIL: the dry run would fail on this device'}")
        raise SystemExit(0 if same else 1)

    spec_d1.require()
    spec_d1_1.require()
    out = a.output
    require_preflight(out, needed_checkpoints(a.arms, folds, a.seeds))
    out.mkdir(parents=True, exist_ok=True)
    R.write_manifest(out, identity_of(a, all_folds),
                     {"started": time.strftime("%Y-%m-%d %H:%M:%S"),
                      "arguments": {k: str(v) if isinstance(v, Path) else v for k, v in vars(a).items()}})
    lock = R.acquire_lock(out)
    try:
        # seed first, so that each finished seed holds every fold, setting and arm (paired blocks)
        for seed in a.seeds:
            for f in folds:
                for config in a.configs:
                    for arm in a.arms:
                        dest = cell_dir(out, config, arm, f["fold"], seed)
                        if (dest / "result.json").exists():
                            continue
                        print(f"D1.1 cell: {config} {arm} {f['fold']} s{seed}", flush=True)
                        run_cell(arm, config, f, seed, a, dest, test=True)
                        validation_summary(out)
    finally:
        lock.unlink(missing_ok=True)
    validation_summary(out)
    print(f"FINISHED (test sealed): {out}")


if __name__ == "__main__":
    main()
