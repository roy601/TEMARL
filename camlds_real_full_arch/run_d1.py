# -*- coding: utf-8 -*-
"""Protocol D1.0 main study runner. Test outputs are SEALED.

    python camlds_real_full_arch/run_d1.py --device cuda                 # 2,240 main cells, resumable
    python camlds_real_full_arch/run_d1.py --device cuda --preflight     # after the freeze: every checkpoint
    python camlds_real_full_arch/run_d1.py --device cuda --timing        # one cell + dry-run check, no test
    python camlds_real_full_arch/run_d1.py --smoke                       # code check, tiny, no freeze needed
    python camlds_real_full_arch/run_d1.py --device cuda --sensitivity mean   # Section 8, seeds 0-4

Main cells (Section 7), run in the order of PHASES, each phase over all folds and seeds:
  1. primary, Family 1   allpos and NoHistory, MAPPO                              640 cells
  2. Family 3            lstm_allpos, MAPPO                                       320 cells
  3. descriptive, Q4     gru_allpos and baseline, MAPPO; allpos and NoHistory, IPPO  1,280 cells
The test is opened only once, after all 2,240 exist (decision D8).

What differs from pipeline.main (deliberately):
  * command order is always 'frozen' (decision D4); environment = EnvConfig(reward="proposal")
    (recorded positions; reward chosen by pilot rule R2, decision D6). Every Section 8 sensitivity
    analysis changes one thing from this primary setting;
  * encoders are the protocol 1.2 checkpoints, loaded unchanged and checked against their recorded
    validation BCE. The CAM-LDS PREDICTION test is NEVER scored again (pipeline.encoder rescored it);
  * each cell's test episodes are written to sealed_test.json and only its SHA-256 goes into result.json;
    nothing here prints, summarises or reports a test number. evaluate_d1.py --open-test opens them once;
  * real runs refuse unless spec_d1 passes (protocol frozen, no pinned file changed) and, for the frozen
    order, unless --preflight has loaded and checked every protocol 1.2 checkpoint the run needs under
    this frozen spec.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pipeline as P  # noqa: E402
import spec_d1  # noqa: E402

env, marl, data, variants, port = P.env, P.marl, P.data, P.variants, P.port
PRIMARY_ARMS = ("allpos", "NoHistory")             # Family 1; also the arms of every sensitivity analysis
MAIN_ARMS = PRIMARY_ARMS + ("lstm_allpos",)         # + Family 3 (D7): the proposal's "MARL without the Transformer"
PRIMARY_REWARD = "proposal"                         # D6, chosen by pilot rule R2 (PROTOCOL_D1.0 Section 7a)
# (arm, learner) per phase, in run order (D5 primary first; D8 descriptive cells before the test opening)
PHASES = (
    ("primary (Family 1)", (("allpos", "MAPPO"), ("NoHistory", "MAPPO"))),
    ("Family 3", (("lstm_allpos", "MAPPO"),)),
    ("descriptive (Q4)", (("gru_allpos", "MAPPO"), ("baseline", "MAPPO"),
                          ("allpos", "IPPO"), ("NoHistory", "IPPO"))),
)
MAIN_CELLS = tuple(c for _, cs in PHASES for c in cs)
SENSITIVITY_CELLS = PHASES[0][1]                    # Section 8: allpos and NoHistory, MAPPO
# Section 8 sensitivity analyses: environment changes and command order
SENSITIVITIES = {
    "efficacy_0.5": ({"efficacy": 0.5}, "frozen"),
    "efficacy_0.75": ({"efficacy": 0.75}, "frozen"),
    "mean": ({"aggregation": "mean"}, "frozen"),
    "random_walk": ({"movement": "random_walk", "goals": "hand"}, "frozen"),
    "execution": ({}, "execution"),
    "reward_engagement": ({"reward": "engagement"}, "frozen"),   # D6: no depth bonus, no exposure penalty
}
ENCODER_BUDGET = {"allpos": 9152, "baseline": 9152, "gru_allpos": 18304, "lstm_allpos": 18304}  # protocol 1.2


def setting(name):
    """(EnvConfig, command order) of the primary study, or of a Section 8 sensitivity analysis, which
    changes only the entries it names: everything else, the reward included, is the primary setting."""
    if name in (None, "primary"):
        return env.EnvConfig(reward=PRIMARY_REWARD), "frozen"
    kw, order = SENSITIVITIES[name]
    return env.EnvConfig(**{"reward": PRIMARY_REWARD, **kw}), order


def specs(rs, seed, repeats, cfg):
    """As pipeline.specs, with the scenario metadata the setting uses."""
    rng = np.random.default_rng(seed)
    meta = env.scenario_metadata(cfg.goals)
    return [env.make_spec(r, rng, meta) for r in rs for _ in range(repeats)]
VAL_SEED, TEST_SEED = 100000, 200000
OUT = HERE / "results_d1"


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def load_encoder(arm, fold, seed, root: Path, device, cell: Path = None, order: str = "frozen"):
    """Frozen order: the protocol 1.2 checkpoint, unchanged. Execution order (sensitivity): an encoder
    trained here on the fold's training runs with the protocol 1.2 budget and patience, selected on
    validation, stored in the cell. Either way it is checked on VALIDATION only."""
    if arm == "NoHistory":
        return None, {"arm": "NoHistory", "checkpoint": None}
    if order == "frozen":
        path = P.checkpoint(arm, fold["fold"], seed, root)
    else:
        path = cell / "encoder.pt"
        if not path.exists():
            d = data.fold_data(fold)
            cell.mkdir(parents=True, exist_ok=True)
            res, _ = variants.train_variant(arm, data.W, seed, d["train"], d["val"], ENCODER_BUDGET[arm],
                                            device=torch.device(device), checkpoint_dir=str(cell),
                                            patience_checks=16, progress=False)
    if not path.exists():
        raise FileNotFoundError(f"{path}: protocol 1.2 checkpoint missing (run on the GPU PC that holds them)")
    ck = torch.load(path, map_location="cpu", weights_only=False)
    if ck.get("window", data.W) != data.W or ck.get("seed", seed) != seed:
        raise ValueError(f"{path}: window/seed mismatch")
    if "variant" in ck and ck["variant"] != arm:
        raise ValueError(f"{path}: variant mismatch")
    model = variants.build_variant(arm, data.W).to(device)
    model.load_state_dict(ck["state_dict"], strict=True)
    model.eval()
    d = data.fold_data(fold)
    va = variants.numpy_logits(model, *d["val"][:2], torch.device(device))
    measured = port.Mx.bce(va, d["val"][2])
    expected = ck.get("validation_bce")
    if expected is None or abs(measured - expected) > 1e-4:
        raise ValueError(f"{path}: does not reproduce its validation BCE ({measured} vs {expected})")
    return model, {"arm": arm, "checkpoint": str(path), "checkpoint_sha256": P.sha(path),
                   "validation_bce": float(measured)}


def run_cell(arm, learner, fold, seed, args, dest: Path, test: bool):
    cfg, order = setting(args.sensitivity)
    va = specs(P.runs(fold, "val"), VAL_SEED + seed, args.eval_repeats, cfg)
    te = specs(P.runs(fold, "test"), TEST_SEED + seed, args.eval_repeats, cfg) if test else []
    model, enc = load_encoder(arm, fold, seed, Path(args.encoder_root), args.device,
                              cell=dest.parent, order=order)
    t0 = time.time()
    res = marl.train(model, cfg, P.runs(fold, "train"), va, te, seed, args.env_steps, data.W, 64,
                     learner == "MAPPO", args.device, args.verbose)
    dest.mkdir(parents=True, exist_ok=True)
    torch.save(res.pop("actor_state"), dest / "actor.pt")
    sealed = {"test": res.pop("test"), "test_summary": res.pop("test_summary"),
              "test_h0_summary": res.pop("test_h0_summary")}
    blob = json.dumps(sealed, sort_keys=True).encode("utf-8")
    if test:
        (dest / "sealed_test.json").write_bytes(blob)
    res.update(arm=arm, learner=learner, fold=fold["fold"], family=fold["family"], seed=seed,
               test_runs=fold["test_runs"], encoder=enc, env_config=cfg.to_dict(), order=order,
               setting=args.sensitivity or "primary",
               sealed_test_sha256=sha_bytes(blob) if test else None, wall_seconds=time.time() - t0,
               eval_repeats=args.eval_repeats, val_seed=VAL_SEED + seed, test_seed=TEST_SEED + seed)
    P.write(dest / "result.json", res)
    return res


def validation_summary(out: Path):
    rows = []
    for p in sorted(out.glob("cells/*/*/s*/*/result.json")):
        r = json.loads(p.read_text(encoding="utf-8"))
        rows.append(f"| {r['arm']} | {r['learner']} | {r['fold']} | {r['seed']} | {r['best_update']} | "
                    f"{r['best_validation_dwell']:.3f} | {r['wall_seconds']:.0f} |")
    head = ["# D1.0 validation summary (no test number appears here)", "",
            "| arm | learner | fold | seed | best update | best validation E1 | seconds |",
            "|---|---|---|---|---|---|---|"]
    (out / "VALIDATION_SUMMARY.md").write_text("\n".join(head + rows) + "\n", encoding="utf-8")


def revalidate(dest: Path, fold, seed, model, device, cfg):
    """The dry-run check of one cell (evaluate_d1 uses this too): reload actor.pt, re-evaluate the cell's
    validation episodes, return (measured, recorded) best validation E1. Reads no test file."""
    res = json.loads((dest / "result.json").read_text(encoding="utf-8"))
    actor = marl.Actor().to(device)
    actor.load_state_dict(torch.load(dest / "actor.pt", map_location=device))
    va = specs(P.runs(fold, "val"), VAL_SEED + seed, res["eval_repeats"], cfg)
    bank = marl.HistoryBank(model, data.W, device, h_zero=(model is None))
    return marl.mean_of(marl.evaluate_team(actor, cfg, va, bank, 64, device)), res["best_validation_dwell"]


def needed_checkpoints(a, folds, plan):
    """(arm, fold, seed) of every protocol 1.2 checkpoint the requested cells load."""
    arms = {arm for arm, lr in plan if arm != "NoHistory" and arm in a.arms and lr in a.learners}
    return {(arm, f["fold"], s) for arm in arms for f in folds for s in a.seeds}


def spec_sha():
    return hashlib.sha256(spec_d1.SPEC.read_bytes()).hexdigest() if spec_d1.SPEC.exists() else None


def preflight(a, folds, plan):
    """Load every needed checkpoint and check that it reproduces its recorded validation BCE.
    No training, no test data. Writes PREFLIGHT.json in the output directory."""
    ok, bad = [], []
    for arm, fold_id, seed in sorted(needed_checkpoints(a, folds, plan)):
        f = next(x for x in folds if x["fold"] == fold_id)
        try:
            _, info = load_encoder(arm, f, seed, Path(a.encoder_root), a.device)
            ok.append({**info, "fold": fold_id, "seed": seed})
        except (FileNotFoundError, ValueError, RuntimeError, KeyError) as e:
            bad.append({"arm": arm, "fold": fold_id, "seed": seed, "error": f"{type(e).__name__}: {e}"})
    rep = {"pass": not bad and bool(ok), "spec_sha256": spec_sha(), "checked": len(ok) + len(bad),
           "ok": [[r["arm"], r["fold"], r["seed"]] for r in ok], "failures": bad, "checkpoints": ok}
    P.write(a.output / "PREFLIGHT.json", rep)
    print(f"preflight: {'PASS' if rep['pass'] else 'FAIL'} ({len(ok)} checkpoints reproduce their validation "
          f"BCE, {len(bad)} failures) -> {a.output / 'PREFLIGHT.json'}")
    for b in bad[:10]:
        print("  ", b)
    return rep


def require_preflight(out: Path, need):
    pf = out / "PREFLIGHT.json"
    rep = json.loads(pf.read_text(encoding="utf-8")) if pf.exists() else None
    if rep is None or not rep["pass"] or rep["spec_sha256"] != spec_sha():
        raise SystemExit("run --preflight first, after the freeze, with the same output directory")
    missing = need - {tuple(x) for x in rep["ok"]}
    if missing:
        raise SystemExit(f"preflight did not check {len(missing)} needed checkpoints, e.g. {sorted(missing)[:3]}")


def identity_of(a, order, cfg, all_folds):
    """Everything that decides what a cell contains. A resumed or later invocation must match it exactly;
    the machine, threads, output path and which arms, folds or seeds this invocation asks for do not."""
    return {"protocol": "D1.0", "spec": json.loads(spec_d1.SPEC.read_text(encoding="utf-8")), "hp": dict(marl.HP),
            "env_config": cfg.to_dict(), "order": order, "env_steps": a.env_steps, "eval_repeats": a.eval_repeats,
            "val_seed": VAL_SEED, "test_seed": TEST_SEED,
            "folds": [{k: v for k, v in f.items() if k != "_steps"} for f in all_folds]}


def write_manifest(out: Path, identity: dict, invocation: dict):
    """MANIFEST.json = identity (checked on every start) + a log of every invocation (not checked).
    Raises RuntimeError if the identity differs from the one the directory was started with."""
    mp = out / "MANIFEST.json"
    log = []
    if mp.exists():
        old = json.loads(mp.read_text(encoding="utf-8"))
        if old["identity"] != json.loads(json.dumps(identity)):
            raise RuntimeError("configuration or pinned files changed: use a new output directory")
        log = old["invocations"]
    P.write(mp, {"identity": identity, "invocations": log + [invocation]})


def acquire_lock(out: Path) -> Path:
    lock = out / "RUNNING.lock"
    try:
        with lock.open("x") as fh:
            fh.write(str(os.getpid()))
    except FileExistsError:
        raise SystemExit(f"{lock} exists: another run uses this directory, or an earlier run was killed "
                         f"(power cut, closed window). If none is running, delete the lock and start again; "
                         f"finished cells are kept and skipped.")
    return lock


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    ap.add_argument("--output", type=Path, default=None)
    ap.add_argument("--sensitivity", choices=sorted(SENSITIVITIES), default=None)
    ap.add_argument("--encoder-root", default=str(P.REPO / "camlds_encoder" / "out"))
    ap.add_argument("--arms", nargs="+", choices=P.ARMS, default=None,
                    help="default: the 3 main arms; for a sensitivity analysis, allpos and NoHistory")
    ap.add_argument("--learners", nargs="+", choices=["MAPPO", "IPPO"], default=None,
                    help="filter; default: every learner of the plan")
    ap.add_argument("--folds", nargs="+")
    ap.add_argument("--seeds", nargs="+", type=int, default=None)
    ap.add_argument("--env-steps", type=int, default=2_000_000)
    ap.add_argument("--eval-repeats", type=int, default=20)
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--timing", action="store_true",
                    help="one cell (first fold, seed 0, allpos, MAPPO) + its dry-run check, no test")
    ap.add_argument("--preflight", action="store_true",
                    help="load and check every protocol 1.2 checkpoint the run needs; no training, no test")
    ap.add_argument("--smoke", action="store_true", help="tiny code check; NoHistory only; no test")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    if a.output is None:
        a.output = OUT / (a.sensitivity or "main")
    if a.seeds is None:
        a.seeds = list(range(5)) if a.sensitivity else list(range(10))
    plan = SENSITIVITY_CELLS if a.sensitivity else MAIN_CELLS
    if a.arms is None:
        a.arms = sorted({arm for arm, _ in plan})
    if a.learners is None:
        a.learners = sorted({lr for _, lr in plan})
    if a.sensitivity and (set(a.arms) - set(PRIMARY_ARMS) or a.learners != ["MAPPO"]):
        raise SystemExit("Section 8: sensitivity runs use allpos and NoHistory with MAPPO only")
    torch.set_num_threads(a.threads)
    if a.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable")
    folds = [f for f in P.ordered_folds(setting(a.sensitivity)[1]) if not a.folds or f["fold"] in a.folds]
    if a.folds and set(a.folds) - {f["fold"] for f in folds}:
        raise ValueError("unknown fold")

    if a.smoke:
        marl.HP.update(n_envs=2, rollout_len=4, ppo_epochs=1, n_evals=1)
        a.env_steps, a.eval_repeats = 8, 1
        learner = "IPPO" if a.learners == ["IPPO"] else "MAPPO"
        dest = a.output.parent / "smoke" / "NoHistory" / folds[0]["fold"] / "s0" / learner
        run_cell("NoHistory", learner, folds[0], 0, a, dest, test=False)
        print("smoke OK:", dest)
        return
    if a.preflight:
        if setting(a.sensitivity)[1] != "frozen":
            raise SystemExit("--preflight checks protocol 1.2 checkpoints; execution-order encoders are trained in the cell")
        rep = preflight(a, folds, plan)
        raise SystemExit(0 if rep["pass"] else 1)
    if a.timing:
        dest = a.output.parent / "timing" / "allpos" / folds[0]["fold"] / "s0" / "MAPPO"
        r = run_cell("allpos", "MAPPO", folds[0], 0, a, dest, test=False)
        n = len(P.ordered_folds("frozen")) * 10 * len(MAIN_CELLS)
        print(f"timing: one cell {r['wall_seconds']:.0f} s on {a.device} "
              f"-> {n} main cells about {n * r['wall_seconds'] / 3600:.1f} h (test episodes not included)")
        model, _ = load_encoder("allpos", folds[0], 0, Path(a.encoder_root), a.device, cell=dest.parent)
        got, rec = revalidate(dest, folds[0], 0, model, a.device, setting(a.sensitivity)[0])
        same = abs(got - rec) <= 1e-9
        P.write(dest.parent / "TIMING_DRY_RUN.json", {"device": a.device, "recorded": rec, "measured": got,
                                                      "pass": same, "seconds": r["wall_seconds"]})
        print(f"dry-run reproduction on {a.device}: recorded {rec!r}, re-evaluated {got!r} -> "
              f"{'PASS' if same else 'FAIL: the dry run would fail on this device'}")
        raise SystemExit(0 if same else 1)

    spec_d1.require()
    out = a.output
    if setting(a.sensitivity)[1] == "frozen":
        require_preflight(out, needed_checkpoints(a, folds, plan))
    out.mkdir(parents=True, exist_ok=True)
    cfg_, order_ = setting(a.sensitivity)
    write_manifest(out, {**identity_of(a, order_, cfg_, P.ordered_folds(order_)),
                         "setting": a.sensitivity or "primary"},
                   {"started": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "arguments": {k: str(v) if isinstance(v, Path) else v for k, v in vars(a).items()}})
    lock = acquire_lock(out)
    try:
        # PHASES order: primary cells over all folds and seeds first (D5), then Family 3, then Q4 (D8)
        phases = [PHASES[0]] if a.sensitivity else PHASES
        for name, pairs in phases:
            pairs = [(arm, lr) for arm, lr in pairs if arm in a.arms and lr in a.learners]
            for f in folds:
                for seed in a.seeds:
                    for arm, learner in pairs:
                        dest = out / "cells" / arm / f["fold"] / f"s{seed}" / learner
                        if (dest / "result.json").exists():
                            continue
                        print(f"D1.0 cell [{name}]: {arm} {learner} {f['fold']} s{seed}", flush=True)
                        run_cell(arm, learner, f, seed, a, dest, test=True)
                        validation_summary(out)
    finally:
        lock.unlink(missing_ok=True)
    validation_summary(out)
    print(f"FINISHED (test sealed): {out}")


if __name__ == "__main__":
    main()
