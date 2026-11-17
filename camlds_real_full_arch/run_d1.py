# -*- coding: utf-8 -*-
"""Protocol D1.0 main study runner. Test outputs are SEALED.

    python camlds_real_full_arch/run_d1.py --device cuda                 # 640 primary cells, resumable
    python camlds_real_full_arch/run_d1.py --device cuda --timing        # one cell, no test episodes
    python camlds_real_full_arch/run_d1.py --smoke                       # code check, tiny, no freeze needed

What differs from pipeline.main (deliberately):
  * command order is always 'frozen' (decision D4), environment = EnvConfig() (recorded positions);
  * encoders are the protocol 1.2 checkpoints, loaded unchanged and checked against their recorded
    validation BCE. The CAM-LDS PREDICTION test is NEVER scored again (pipeline.encoder rescored it);
  * each cell's test episodes are written to sealed_test.json and only its SHA-256 goes into result.json;
    nothing here prints, summarises or reports a test number. evaluate_d1.py --open-test opens them once;
  * real runs refuse unless spec_d1 passes (protocol frozen, no pinned file changed).
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
PRIMARY_ARMS = ("allpos", "NoHistory")
VAL_SEED, TEST_SEED = 100000, 200000
OUT = HERE / "results_d1"


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def load_encoder(arm, fold, seed, root: Path, device):
    """The protocol 1.2 checkpoint, unchanged. Checked on VALIDATION only."""
    if arm == "NoHistory":
        return None, {"arm": "NoHistory", "checkpoint": None}
    path = P.checkpoint(arm, fold["fold"], seed, root)
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
    cfg = env.EnvConfig()
    va = P.specs(P.runs(fold, "val"), VAL_SEED + seed, args.eval_repeats)
    te = P.specs(P.runs(fold, "test"), TEST_SEED + seed, args.eval_repeats) if test else []
    model, enc = load_encoder(arm, fold, seed, Path(args.encoder_root), args.device)
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
               test_runs=fold["test_runs"], encoder=enc, env_config=cfg.to_dict(), order="frozen",
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    ap.add_argument("--output", type=Path, default=OUT / "main")
    ap.add_argument("--encoder-root", default=str(P.REPO / "camlds_encoder" / "out"))
    ap.add_argument("--arms", nargs="+", choices=P.ARMS, default=list(PRIMARY_ARMS))
    ap.add_argument("--learners", nargs="+", choices=["MAPPO", "IPPO"], default=["MAPPO"])
    ap.add_argument("--folds", nargs="+")
    ap.add_argument("--seeds", nargs="+", type=int, default=list(range(10)))
    ap.add_argument("--env-steps", type=int, default=2_000_000)
    ap.add_argument("--eval-repeats", type=int, default=20)
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--timing", action="store_true", help="one cell (first fold, seed 0, allpos, MAPPO), no test")
    ap.add_argument("--smoke", action="store_true", help="tiny code check; NoHistory only; no test")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    torch.set_num_threads(a.threads)
    if a.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable")
    folds = [f for f in P.ordered_folds("frozen") if not a.folds or f["fold"] in a.folds]
    if a.folds and set(a.folds) - {f["fold"] for f in folds}:
        raise ValueError("unknown fold")

    if a.smoke:
        marl.HP.update(n_envs=2, rollout_len=4, ppo_epochs=1, n_evals=1)
        a.env_steps, a.eval_repeats = 8, 1
        dest = a.output.parent / "smoke" / "NoHistory" / folds[0]["fold"] / "s0" / "MAPPO"
        run_cell("NoHistory", "MAPPO", folds[0], 0, a, dest, test=False)
        print("smoke OK:", dest)
        return
    if a.timing:
        dest = a.output.parent / "timing" / "allpos" / folds[0]["fold"] / "s0" / "MAPPO"
        r = run_cell("allpos", "MAPPO", folds[0], 0, a, dest, test=False)
        n = len(P.ordered_folds("frozen")) * 10 * 2
        print(f"timing: one cell {r['wall_seconds']:.0f} s on {a.device} "
              f"-> {n} primary cells about {n * r['wall_seconds'] / 3600:.1f} h (test episodes not included)")
        return

    spec_d1.require()
    out = a.output
    out.mkdir(parents=True, exist_ok=True)
    manifest = {"protocol": "D1.0", "spec": json.loads(spec_d1.SPEC.read_text(encoding="utf-8")),
                "arguments": {k: str(v) if isinstance(v, Path) else v for k, v in vars(a).items()},
                "hp": marl.HP, "env_config": env.EnvConfig().to_dict(),
                "folds": [{k: v for k, v in f.items() if k != "_steps"} for f in folds]}
    mp = out / "MANIFEST.json"
    if mp.exists() and json.loads(mp.read_text(encoding="utf-8")) != json.loads(json.dumps(manifest)):
        raise RuntimeError("configuration or pinned files changed: use a new output directory")
    P.write(mp, manifest)
    lock = out / "RUNNING.lock"
    with lock.open("x") as fh:
        fh.write(str(os.getpid()))
    try:
        for f in folds:
            for seed in a.seeds:
                for arm in a.arms:
                    for learner in a.learners:
                        dest = out / "cells" / arm / f["fold"] / f"s{seed}" / learner
                        if (dest / "result.json").exists():
                            continue
                        print(f"D1.0 cell: {arm} {learner} {f['fold']} s{seed}", flush=True)
                        run_cell(arm, learner, f, seed, a, dest, test=True)
                        validation_summary(out)
    finally:
        lock.unlink(missing_ok=True)
    validation_summary(out)
    print(f"FINISHED (test sealed): {out}")


if __name__ == "__main__":
    main()
