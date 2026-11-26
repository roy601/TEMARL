# -*- coding: utf-8 -*-
"""Protocol CL-D1.0 runner (PROTOCOL_CL_D1.0.md). Test outputs are SEALED.

    python casinolimit_d1/run_cl.py --device cuda --preflight          # every CL 1.0 checkpoint (200)
    python casinolimit_d1/run_cl.py --device cuda --timing             # one cell + dry-run check, no test
    python casinolimit_d1/run_cl.py --device cuda --study main         # 350 cells, resumable
    python casinolimit_d1/run_cl.py --device cuda --study efficacy_0.5 # Section 8: 50 cells each (5 settings)
    python casinolimit_d1/run_cl.py --device cuda --study tune         # Section 9: 270 cells
    python casinolimit_d1/run_cl.py --smoke                            # code check, tiny, no freeze

Studies (all cells exist before the single test opening, evaluate_cl.py --open-test):
  main         Family 1 allpos, NoHistory (MAPPO); Family 3 lstm_allpos (MAPPO); Q4 gru_allpos, baseline
               (MAPPO), allpos and NoHistory (IPPO); 5 folds x seeds 0-9 = 350 cells
  efficacy_0.5, efficacy_0.75, mean, reward_engagement, payoff_permuted
               allpos and NoHistory (MAPPO), 5 folds x seeds 0-4 = 50 cells each (250);
               payoff_permuted uses cl_world.PAYOFF_PERMUTED (which decoy suits which tactic changed)
  tune         learning rate {1e-4, 5e-4, 1e-3} x PPO epochs {5, 10, 15} (as protocol D1.1), allpos and
               NoHistory (MAPPO), 5 folds x seeds 0-2 = 270 cells
Each cell: D1.0's cell (run_d1.run_cell) on the CasinoLimit world. The encoder is the CL 1.0 checkpoint
of the same arm, fold and seed, accepted only if it matches CL 1.0's committed record for it
(casinolimit_encoder/out/train/main/.../result.json): variant, fold, seed, window, label count and
validation rows; the committed validation logits file (by its recorded SHA-256), which the checkpoint's
own validation logits must reproduce within 1e-3; and the recorded validation BCE, within 1e-5.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import itertools
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cl_world as C  # noqa: E402  (first: registers the CasinoLimit environment)
import spec_cl_d1  # noqa: E402

env, marl = C.env, C.marl
REPO = C.REPO
PRIMARY_REWARD = "proposal"                  # D1.0 decision D6, carried over unchanged
PHASES = (
    ("primary (Family 1)", (("allpos", "MAPPO"), ("NoHistory", "MAPPO"))),
    ("Family 3", (("lstm_allpos", "MAPPO"),)),
    ("descriptive (Q4)", (("gru_allpos", "MAPPO"), ("baseline", "MAPPO"), ("allpos", "IPPO"), ("NoHistory", "IPPO"))),
)
MAIN_CELLS = tuple(c for _, cs in PHASES for c in cs)
PRIMARY_CELLS = PHASES[0][1]
SENSITIVITIES = {"efficacy_0.5": {"efficacy": 0.5}, "efficacy_0.75": {"efficacy": 0.75},
                 "mean": {"aggregation": "mean"}, "reward_engagement": {"reward": "engagement"},
                 "payoff_permuted": {}}                  # changes the payoff table, not EnvConfig
PAYOFF_TABLES = {"payoff_permuted": C.PAYOFF_PERMUTED}
LRS, EPOCHS = (1e-4, 5e-4, 1e-3), (5, 10, 15)        # protocol D1.1's grid
DEFAULT = {"lr": 5e-4, "ppo_epochs": 10}


def config_name(c):
    return f"lr{c['lr']:.0e}_ep{c['ppo_epochs']:02d}"


GRID = {config_name({"lr": lr, "ppo_epochs": ep}): {"lr": lr, "ppo_epochs": ep}
        for lr, ep in itertools.product(LRS, EPOCHS)}
DEFAULT_NAME = config_name(DEFAULT)
STUDIES = ("main", *SENSITIVITIES, "tune")
SEEDS = {"main": tuple(range(10)), **{s: tuple(range(5)) for s in SENSITIVITIES}, "tune": (0, 1, 2)}
VAL_SEED, TEST_SEED = 100000, 200000
EVAL_REPEATS = 20
ENCODER_ARMS = ("allpos", "baseline", "gru_allpos", "lstm_allpos")
OUT = HERE / "results_cl"
CL10_RECORDS = REPO / "casinolimit_encoder" / "out" / "train" / "main"
BCE_TOL = 1e-5
LOGIT_TOL = 1e-3                             # max |logit difference| from CL 1.0's committed validation logits

if {k: marl.HP[k] for k in DEFAULT} != DEFAULT:
    raise RuntimeError("mappo_cmd.HP no longer holds D1.0's setting")


def setting(study: str):
    """EnvConfig of a study: D1.0's primary setting (proposal reward), or a Section 8 change of one entry."""
    return env.EnvConfig(**{"reward": PRIMARY_REWARD, **SENSITIVITIES.get(study, {})})


def table(study: str):
    """The payoff table a study uses: D1.0's rule (cl_world.PAYOFF), or a Section 8 replacement."""
    return PAYOFF_TABLES.get(study, C.PAYOFF)


def table_sha(study: str) -> str:
    return C.table_sha256(table(study))


@contextlib.contextmanager
def payoff(study: str):
    """Put the study's payoff table into the environment (in place, where command_payoff reads it);
    restore D1.0's table after, also on an exception."""
    if not np.array_equal(env.PAYOFF, C.PAYOFF):
        raise RuntimeError("the environment's payoff table is not D1.0's rule on entry")
    env.PAYOFF[:] = table(study)
    try:
        yield
    finally:
        env.PAYOFF[:] = C.PAYOFF


def plan(study: str):
    """[(config, arm, learner)] of a study, in run order."""
    if study == "main":
        return [(DEFAULT_NAME, arm, lr) for arm, lr in MAIN_CELLS]
    if study in SENSITIVITIES:
        return [(DEFAULT_NAME, arm, lr) for arm, lr in PRIMARY_CELLS]
    if study == "tune":
        return [(c, arm, "MAPPO") for c in GRID for arm, _ in PRIMARY_CELLS]
    raise ValueError(study)


def cell_dir(out: Path, study, config, arm, fold_id, seed, learner) -> Path:
    return out / study / "cells" / config / arm / fold_id / f"s{seed}" / learner


def all_cells(out: Path, study: str, folds) -> dict:
    return {(study, c, arm, f["fold"], s, lr): cell_dir(out, study, c, arm, f["fold"], s, lr)
            for c, arm, lr in plan(study) for f in folds for s in SEEDS[study]}


@contextlib.contextmanager
def hp(config: str):
    """Set the grid point's swept settings in mappo_cmd.HP; restore them after, also on an exception."""
    values = GRID[config]
    old = {k: marl.HP[k] for k in values}
    marl.HP.update(values)
    try:
        yield dict(marl.HP)
    finally:
        marl.HP.update(old)


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def checkpoint(arm, fold_id, seed, root: Path) -> Path:
    return Path(root) / "train" / "main" / arm / fold_id / f"s{seed}" / "encoder.pt"


def cl10_record(arm, fold_id, seed, records: Path = CL10_RECORDS) -> dict:
    return json.loads((Path(records) / arm / fold_id / f"s{seed}" / "result.json").read_text(encoding="utf-8"))


def cl10_bce(arm, fold_id, seed, records: Path = CL10_RECORDS) -> float:
    return float(cl10_record(arm, fold_id, seed, records)["validation"]["bce"])


def check_record(rec: dict, arm, fold, seed, d) -> None:
    """CL 1.0's record must describe this arm, fold, seed, window, label count and validation rows."""
    want = {"variant": arm, "fold": fold["fold"], "seed": seed, "window": C.W, "labels": C.NT}
    got = {k: rec.get(k) for k in want}
    if got != want:
        raise ValueError(f"CL 1.0 record {got} does not describe {want}: not the CL 1.0 checkpoint")
    if rec.get("val_source_rows") != json.loads(json.dumps(d["val_source_rows"])):
        raise ValueError("CL 1.0 record's validation rows differ from this fold's: preprocessing changed")


def load_encoder(arm, fold, seed, root, device, records: Path = CL10_RECORDS):
    """The CL 1.0 checkpoint, unchanged, accepted only if it matches CL 1.0's committed record: identity
    fields and validation rows, the committed validation logits (SHA-256 as recorded; reproduced within
    LOGIT_TOL) and the recorded validation BCE (within BCE_TOL). NoHistory has no encoder."""
    if arm == "NoHistory":
        return None, {"arm": "NoHistory", "checkpoint": None}
    path = checkpoint(arm, fold["fold"], seed, root)
    if not path.exists():
        raise FileNotFoundError(f"{path}: CL 1.0 checkpoint missing (copy it from GPU PC 1)")
    ck = torch.load(path, map_location="cpu", weights_only=False)
    if ck.get("window", C.W) != C.W or ck.get("seed", seed) != seed or ck.get("variant", arm) != arm:
        raise ValueError(f"{path}: window, seed or variant mismatch")
    model = C.CP.V.build_variant(arm, C.W).to(device)
    model.load_state_dict(ck["state_dict"], strict=True)
    model.eval()
    d = C.CD.fold_data(fold)
    rec = cl10_record(arm, fold["fold"], seed, records)
    check_record(rec, arm, fold, seed, d)
    vfile = Path(records) / arm / fold["fold"] / f"s{seed}" / rec["val"]["file"]
    if not vfile.exists() or sha_file(vfile) != rec["val"]["sha256"]:
        raise ValueError(f"{vfile}: CL 1.0's committed validation logits are missing or changed")
    stored = np.load(vfile)
    logits = np.asarray(C.CP.V.numpy_logits(model, *d["val"][:2], torch.device(device)))
    if stored.shape != logits.shape or stored.shape[0] != rec["val"]["points"]:
        raise ValueError(f"{path}: validation logits shape {logits.shape} differs from CL 1.0's {stored.shape}")
    gap = float(np.max(np.abs(logits.astype(np.float64) - stored.astype(np.float64))))
    if gap > LOGIT_TOL:
        raise ValueError(f"{path}: validation logits differ from CL 1.0's by up to {gap}: not the CL 1.0 checkpoint")
    measured = float(C.CP.Mx.bce(logits, d["val"][2]))
    expected = float(rec["validation"]["bce"])
    if abs(measured - expected) > BCE_TOL:
        raise ValueError(f"{path}: validation BCE {measured} differs from CL 1.0's recorded {expected}: "
                         f"not the CL 1.0 checkpoint")
    return model, {"arm": arm, "checkpoint": str(path), "checkpoint_sha256": sha_file(path),
                   "validation_bce": measured, "cl10_validation_bce": expected,
                   "validation_logits_max_abs_diff": gap, "cl10_val_logits_sha256": rec["val"]["sha256"]}


def run_cell(study, config, arm, learner, fold, seed, args, dest: Path, test: bool):
    """run_d1.run_cell on the CasinoLimit world, with the grid point's HP (D1.0's for every study but tune)."""
    cfg = setting(study)
    va = C.specs(C.runs(fold, "val"), VAL_SEED + seed, args.eval_repeats)
    te = C.specs(C.runs(fold, "test"), TEST_SEED + seed, args.eval_repeats) if test else []
    model, enc = load_encoder(arm, fold, seed, Path(args.encoder_root), args.device, Path(args.records))
    t0 = time.time()
    with hp(config) as used, payoff(study):
        res = marl.train(model, cfg, C.runs(fold, "train"), va, te, seed, args.env_steps, C.W, C.MAX_STEPS,
                         learner == "MAPPO", args.device, args.verbose)
    dest.mkdir(parents=True, exist_ok=True)
    torch.save(res.pop("actor_state"), dest / "actor.pt")
    sealed = {"test": res.pop("test"), "test_summary": res.pop("test_summary"),
              "test_h0_summary": res.pop("test_h0_summary")}
    blob = json.dumps(sealed, sort_keys=True).encode("utf-8")
    if test:
        (dest / "sealed_test.json").write_bytes(blob)
    res.update(protocol="CL-D1.0", study=study, config=config, hp=used, arm=arm, learner=learner,
               fold=fold["fold"], seed=seed, test_runs=fold["test_runs"], encoder=enc, env_config=cfg.to_dict(),
               payoff_sha256=table_sha(study),
               sealed_test_sha256=sha_bytes(blob) if test else None, wall_seconds=time.time() - t0,
               eval_repeats=args.eval_repeats, val_seed=VAL_SEED + seed, test_seed=TEST_SEED + seed)
    write(dest / "result.json", res)
    return res


def write(path: Path, obj):
    """Atomic JSON write (non-finite floats as null), as pipeline.write."""
    import math
    import uuid

    def clean(v):
        if isinstance(v, float) and not math.isfinite(v):
            return None
        if isinstance(v, dict):
            return {k: clean(x) for k, x in v.items()}
        if isinstance(v, (list, tuple)):
            return [clean(x) for x in v]
        return v
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    tmp.write_text(json.dumps(clean(obj), indent=2, allow_nan=False), encoding="utf-8")
    for attempt in range(12):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            if attempt == 11:
                raise
            time.sleep(min(0.1 * 2 ** attempt, 2))


def revalidate(dest: Path, fold, seed, model, device, cfg):
    """Dry-run check of one cell: reload actor.pt, re-evaluate its validation episodes, return
    (measured, recorded) best validation E1. Reads no test file."""
    res = json.loads((dest / "result.json").read_text(encoding="utf-8"))
    actor = marl.Actor().to(device)
    actor.load_state_dict(torch.load(dest / "actor.pt", map_location=device))
    va = C.specs(C.runs(fold, "val"), VAL_SEED + seed, res["eval_repeats"])
    bank = marl.HistoryBank(model, C.W, device, h_zero=(model is None))
    with payoff(res["study"]):
        got = marl.mean_of(marl.evaluate_team(actor, cfg, va, bank, C.MAX_STEPS, device))
    return got, res["best_validation_dwell"]


def validation_summary(out: Path, study: str):
    rows = []
    for p in sorted((out / study).glob("cells/*/*/*/s*/*/result.json")):
        r = json.loads(p.read_text(encoding="utf-8"))
        rows.append(f"| {r['config']} | {r['arm']} | {r['learner']} | {r['fold']} | {r['seed']} | "
                    f"{r['best_update']} | {r['best_validation_dwell']:.3f} | {r['wall_seconds']:.0f} |")
    head = [f"# CL-D1.0 validation summary, study {study} (no test number appears here)", "",
            "| setting | arm | learner | fold | seed | best update | best validation E1 | seconds |",
            "|---|---|---|---|---|---|---|---|"]
    (out / study / "VALIDATION_SUMMARY.md").write_text("\n".join(head + rows) + "\n", encoding="utf-8")


def spec_sha():
    return hashlib.sha256(spec_cl_d1.SPEC.read_bytes()).hexdigest() if spec_cl_d1.SPEC.exists() else None


def needed_checkpoints(folds):
    """Every CL 1.0 checkpoint any study loads: the 4 encoder arms x folds x seeds 0-9 (200)."""
    return {(arm, f["fold"], s) for arm in ENCODER_ARMS for f in folds for s in SEEDS["main"]}


def preflight(a, folds):
    ok, bad = [], []
    for arm, fold_id, seed in sorted(needed_checkpoints(folds)):
        f = next(x for x in folds if x["fold"] == fold_id)
        try:
            _, info = load_encoder(arm, f, seed, Path(a.encoder_root), a.device, Path(a.records))
            ok.append({**info, "fold": fold_id, "seed": seed})
        except (FileNotFoundError, ValueError, RuntimeError, KeyError) as e:
            bad.append({"arm": arm, "fold": fold_id, "seed": seed, "error": f"{type(e).__name__}: {e}"})
    rep = {"pass": not bad and bool(ok), "spec_sha256": spec_sha(), "checked": len(ok) + len(bad),
           "ok": [[r["arm"], r["fold"], r["seed"]] for r in ok], "failures": bad, "checkpoints": ok}
    write(a.output / "PREFLIGHT.json", rep)
    gap = max((r["validation_logits_max_abs_diff"] for r in ok), default=float("nan"))
    print(f"CL-D1.0 preflight: {'PASS' if rep['pass'] else 'FAIL'} ({len(ok)} checkpoints match CL 1.0's records: "
          f"identity, validation rows, validation logits (largest difference {gap:.2e}) and BCE; "
          f"{len(bad)} failures) -> {a.output / 'PREFLIGHT.json'}")
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


def identity_of(a, study, folds):
    """What decides a cell's content; a restart must match it (machine, threads, filters may differ)."""
    return {"protocol": "CL-D1.0", "study": study, "spec": json.loads(spec_cl_d1.SPEC.read_text(encoding="utf-8")),
            "base_hp": dict(marl.HP), "grid": GRID if study == "tune" else {DEFAULT_NAME: GRID[DEFAULT_NAME]},
            "env_config": setting(study).to_dict(), "payoff_sha256": table_sha(study),
            "env_steps": a.env_steps, "eval_repeats": a.eval_repeats,
            "val_seed": VAL_SEED, "test_seed": TEST_SEED, "seeds": list(SEEDS[study]), "max_steps": C.MAX_STEPS,
            "folds": [{k: v for k, v in f.items() if k != "_steps"} for f in folds]}


def write_manifest(out: Path, identity: dict, invocation: dict):
    mp = out / "MANIFEST.json"
    log = []
    if mp.exists():
        old = json.loads(mp.read_text(encoding="utf-8"))
        if old["identity"] != json.loads(json.dumps(identity)):
            raise RuntimeError("configuration or pinned files changed: use a new output directory")
        log = old["invocations"]
    write(mp, {"identity": identity, "invocations": log + [invocation]})


def acquire_lock(out: Path) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    lock = out / "RUNNING.lock"
    try:
        with lock.open("x") as fh:
            fh.write(str(os.getpid()))
    except FileExistsError:
        raise SystemExit(f"{lock} exists: another run uses this directory, or an earlier run was killed "
                         f"(power cut, closed window). If none is running, delete the lock and start again; "
                         f"finished cells are kept and skipped.")
    return lock


def order(study, folds):
    """Run order: main and sensitivities phase by phase over folds and seeds (D1.0); tune seed first."""
    if study == "tune":
        return [(c, arm, lr, f, s) for s in SEEDS[study] for f in folds for c, arm, lr in plan(study)]
    out = []
    phases = PHASES if study == "main" else (("primary", PRIMARY_CELLS),)
    for _, pairs in phases:
        for f in folds:
            for s in SEEDS[study]:
                out += [(DEFAULT_NAME, arm, lr, f, s) for arm, lr in pairs]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    ap.add_argument("--output", type=Path, default=OUT)
    ap.add_argument("--study", choices=STUDIES, default="main")
    ap.add_argument("--encoder-root", default=str(REPO / "casinolimit_encoder" / "out"))
    ap.add_argument("--records", default=str(CL10_RECORDS), help="CL 1.0's committed per-checkpoint records")
    ap.add_argument("--folds", nargs="+")
    ap.add_argument("--env-steps", type=int, default=2_000_000)
    ap.add_argument("--eval-repeats", type=int, default=EVAL_REPEATS)
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--preflight", action="store_true")
    ap.add_argument("--timing", action="store_true", help="one allpos MAPPO cell (F1, seed 0) + dry-run check")
    ap.add_argument("--smoke", action="store_true", help="tiny code check; NoHistory; no test; no freeze")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    torch.set_num_threads(a.threads)
    if a.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable")
    all_folds = C.folds()
    folds = [f for f in all_folds if not a.folds or f["fold"] in a.folds]
    if a.folds and set(a.folds) - {f["fold"] for f in folds}:
        raise ValueError("unknown fold")

    if a.smoke:
        marl.HP.update(n_envs=2, rollout_len=4, n_evals=1)
        a.env_steps, a.eval_repeats = 8, 1
        for study, config, learner in (("main", DEFAULT_NAME, "MAPPO"), ("main", DEFAULT_NAME, "IPPO"),
                                       ("efficacy_0.5", DEFAULT_NAME, "MAPPO"), ("tune", "lr1e-03_ep15", "MAPPO")):
            dest = cell_dir(a.output / "smoke", study, config, "NoHistory", folds[0]["fold"], 0, learner)
            run_cell(study, config, "NoHistory", learner, folds[0], 0, a, dest, test=False)
            print("smoke OK:", dest)
        return
    if a.preflight:
        rep = preflight(a, folds)
        raise SystemExit(0 if rep["pass"] else 1)
    if a.timing:
        dest = cell_dir(a.output / "timing", "main", DEFAULT_NAME, "allpos", folds[0]["fold"], 0, "MAPPO")
        r = run_cell("main", DEFAULT_NAME, "allpos", "MAPPO", folds[0], 0, a, dest, test=False)
        n = sum(len(all_cells(a.output, s, all_folds)) for s in STUDIES)
        print(f"timing: one cell {r['wall_seconds']:.0f} s on {a.device} -> {n} CL-D1.0 cells about "
              f"{n * r['wall_seconds'] / 3600:.1f} h (test episodes not included)")
        model, _ = load_encoder("allpos", folds[0], 0, Path(a.encoder_root), a.device, Path(a.records))
        got, rec = revalidate(dest, folds[0], 0, model, a.device, setting("main"))
        same = abs(got - rec) <= 1e-9
        write(dest.parent / "TIMING_DRY_RUN.json", {"device": a.device, "recorded": rec, "measured": got,
                                                    "pass": same, "seconds": r["wall_seconds"]})
        print(f"dry-run reproduction on {a.device}: recorded {rec!r}, re-evaluated {got!r} -> "
              f"{'PASS' if same else 'FAIL: the dry run would fail on this device'}")
        raise SystemExit(0 if same else 1)

    spec_cl_d1.require()
    gate = HERE / "gate" / "GATE_RESULT.json"
    if not (gate.exists() and json.loads(gate.read_text(encoding="utf-8"))["pass"]):
        raise SystemExit("the CL-D1.0 validity gate has not passed: no learned agent is trained (Section 5)")
    require_preflight(a.output, needed_checkpoints(all_folds))
    out = a.output / a.study
    out.mkdir(parents=True, exist_ok=True)
    write_manifest(out, identity_of(a, a.study, all_folds),
                   {"started": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "arguments": {k: str(v) if isinstance(v, Path) else v for k, v in vars(a).items()}})
    lock = acquire_lock(out)
    try:
        for config, arm, learner, f, seed in order(a.study, folds):
            dest = cell_dir(a.output, a.study, config, arm, f["fold"], seed, learner)
            if (dest / "result.json").exists():
                continue
            print(f"CL-D1.0 cell [{a.study}]: {config} {arm} {learner} {f['fold']} s{seed}", flush=True)
            run_cell(a.study, config, arm, learner, f, seed, a, dest, test=True)
            validation_summary(a.output, a.study)
    finally:
        lock.unlink(missing_ok=True)
    validation_summary(a.output, a.study)
    print(f"FINISHED (test sealed): {out}")


if __name__ == "__main__":
    main()
