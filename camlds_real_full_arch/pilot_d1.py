# -*- coding: utf-8 -*-
"""Protocol D1.0 pilot (before the freeze): a small trial on VALIDATION data only.

    python camlds_real_full_arch/pilot_d1.py              # about 1 hour on a CPU

Purpose (PROTOCOL_D1.0.md, Section 7a): see that the whole chain works, and settle the reward choice by a
rule declared before the pilot ran. Nothing about history vs no history is decided here.

  folds    1_cron_sshkey (S1), 3_vnc_puppet (S3), 6_macro_cron (S6): validation runs from three scenarios
  data     training runs for learning, validation runs for scoring. No test run is used: test episodes
           are never built (asserted).
  seeds    101, 102, 103 (disjoint from the main seeds 0-9); validation randomness 100000 + seed
  learners MAPPO, 200,000 environment steps per cell (10% of the main budget), 10 repeats per run
  arms     allpos, NoHistory, lstm_allpos (the proposal's "MARL without the Transformer")
  encoders trained here on the fold's training runs with the protocol 1.2 budget and patience,
           selected on validation (the main-study checkpoints exist only for seeds 0-9)
  rewards  engagement (D6) and proposal (+1 bonus per newly engaged technique, -5 on exposure)
  references on the same validation episodes: none, random, static (best single decoy type everywhere),
           fixed (best joint action), greedy, planner, clairvoyant; static, fixed and planner fitted on
           the fold's training runs

Decision rules (declared before the pilot ran):
  R1 works   in every pilot fold, each learned arm with the engagement reward has a higher mean
             validation E1 than none and than random. If not, stop and investigate before any freeze.
  R2 reward  the main study uses the proposal reward only if, over all pilot cells, its mean validation
             E1 is at least 95% of the engagement reward's AND its mean validation depth or P1 is higher.
             Otherwise the engagement reward (D6) stays.
  R3         allpos - NoHistory and allpos - lstm_allpos differences are reported but decide nothing.
"""
from __future__ import annotations

import itertools
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_d1 as R  # noqa: E402
import gate_d1 as G  # noqa: E402

P, env, marl, data, variants, port = R.P, R.env, R.marl, R.data, R.variants, R.port
B = G.B

FOLDS = ("1_cron_sshkey", "3_vnc_puppet", "6_macro_cron")
SEEDS = (101, 102, 103)
ENV_STEPS = 200_000
REPEATS = 10
ARMS = ("allpos", "NoHistory", "lstm_allpos")
REWARDS = ("engagement", "proposal")
OUT = HERE / "results_d1" / "pilot"
FIT_SEED = 500000


def encoder(arm, fold, seed, device):
    if arm == "NoHistory":
        return None
    cell = OUT / "encoders" / arm / fold["fold"] / f"s{seed}"
    path = cell / "encoder.pt"
    d = data.fold_data(fold)
    if not path.exists():
        cell.mkdir(parents=True, exist_ok=True)
        variants.train_variant(arm, data.W, seed, d["train"], d["val"], R.ENCODER_BUDGET[arm],
                               device=torch.device(device), checkpoint_dir=str(cell),
                               patience_checks=16, progress=False)
    ck = torch.load(path, map_location="cpu", weights_only=False)
    model = variants.build_variant(arm, data.W).to(device)
    model.load_state_dict(ck["state_dict"], strict=True)
    model.eval()
    va = variants.numpy_logits(model, *d["val"][:2], torch.device(device))
    if abs(port.Mx.bce(va, d["val"][2]) - ck["validation_bce"]) > 1e-4:
        raise ValueError(f"{path}: does not reproduce its validation BCE")
    return model


def summarise(rows):
    p1 = [r for r in rows if r["p1"]]
    return {"E1": float(np.mean([r["dwell"] for r in rows])),
            "P1": float(np.mean([r["protected"] for r in p1])) if p1 else None,
            "depth": float(np.mean([r["depth"] for r in rows])),
            "exposed": float(np.mean([r["exposed"] for r in rows])),
            "undefended": float(np.mean([r["undefended_commands"] for r in rows]))}


def references(fold, va, cfg):
    train = P.runs(fold, "train")
    fit = R.specs(train, FIT_SEED, 2, cfg)
    score = lambda pol, sp: G.score(pol, sp, cfg)["E1"]
    static = max(range(1, env.N_ACTIONS), key=lambda a: score(B.StaticPolicy(a), fit))
    fixed = max(itertools.product(range(env.N_ACTIONS), repeat=env.N_AGENTS),
                key=lambda j: score(B.FixedJointPolicy(j), fit))
    pols = {"none": B.NullPolicy(), "random": B.RandomPolicy(FIT_SEED), "static": B.StaticPolicy(static),
            "fixed": B.FixedJointPolicy(fixed), "greedy": B.ReactivePolicy(cfg),
            "planner": G.TransitionPlanner(train, cfg), "clairvoyant": B.ClairvoyantCoordPolicy(cfg)}
    e = env.CommandEngagementEnv(cfg)
    out = {n: summarise([env.run_episode(e, s, pol) for s in va]) for n, pol in pols.items()}
    out["static"]["chosen"] = int(static)
    out["fixed"]["chosen"] = list(fixed)
    return out


def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch.set_num_threads(4)
    OUT.mkdir(parents=True, exist_ok=True)
    folds = {f["fold"]: f for f in P.ordered_folds("frozen")}
    res = {"design": {"folds": FOLDS, "seeds": SEEDS, "env_steps": ENV_STEPS, "repeats": REPEATS,
                      "arms": ARMS, "rewards": REWARDS, "device": device}, "folds": {}}
    path = OUT / "PILOT_RESULTS.json"
    if path.exists():
        res = json.loads(path.read_text(encoding="utf-8"))
    t0 = time.time()
    for fid in FOLDS:
        f = folds[fid]
        test_ids = set(f["test_runs"])
        blk = res["folds"].setdefault(fid, {"validation_runs": f["val_runs"], "cells": {}})
        base_cfg = env.EnvConfig()
        va_by_seed = {s: R.specs(P.runs(f, "val"), R.VAL_SEED + s, REPEATS, base_cfg) for s in SEEDS}
        assert not any(sp.run_id in test_ids for v in va_by_seed.values() for sp in v), "a test run leaked"
        if "references" not in blk:
            blk["references"] = references(f, va_by_seed[SEEDS[0]], base_cfg)
        for seed in SEEDS:
            for arm in ARMS:
                model = None
                for reward in REWARDS:
                    key = f"{arm}|{reward}|{seed}"
                    if key in blk["cells"]:
                        continue
                    if model is None:
                        model = encoder(arm, f, seed, device)
                    cfg = env.EnvConfig(reward=reward)
                    va = R.specs(P.runs(f, "val"), R.VAL_SEED + seed, REPEATS, cfg)
                    tc = time.time()
                    r = marl.train(model, cfg, P.runs(f, "train"), va, [], seed, ENV_STEPS, data.W, 64,
                                   True, device, False)
                    actor = marl.Actor().to(device)
                    actor.load_state_dict(r["actor_state"])
                    bank = marl.HistoryBank(model, data.W, device, h_zero=(model is None))
                    rows = marl.evaluate_team(actor, cfg, va, bank, 64, device)
                    blk["cells"][key] = {**summarise(rows), "best_update": r["best_update"],
                                         "best_validation_E1": r["best_validation_dwell"],
                                         "curve_val_E1": [c["val_dwell"] for c in r["curve"]],
                                         "seconds": time.time() - tc}
                    path.write_text(json.dumps(res, indent=1), encoding="utf-8")
                    print(f"{fid} {key}: {time.time() - t0:.0f}s", flush=True)
    res["decisions"] = decide(res)
    path.write_text(json.dumps(res, indent=1), encoding="utf-8")
    (OUT / "PILOT_RESULTS.md").write_text(report(res), encoding="utf-8")
    print(report(res))


def mean_cells(blk, arm, reward, key):
    vals = [c[key] for k, c in blk["cells"].items()
            if k.startswith(f"{arm}|{reward}|") and c[key] is not None]
    return float(np.mean(vals)) if vals else None


def decide(res):
    r1 = {}
    for fid, blk in res["folds"].items():
        floor = max(blk["references"]["none"]["E1"], blk["references"]["random"]["E1"])
        r1[fid] = {arm: mean_cells(blk, arm, "engagement", "E1") > floor for arm in ARMS}
    works = all(all(v.values()) for v in r1.values())
    agg = {rw: {k: float(np.mean([c[k] for blk in res["folds"].values() for kk, c in blk["cells"].items()
                                  if f"|{rw}|" in kk and c[k] is not None])) for k in ("E1", "depth", "P1")}
           for rw in REWARDS}
    e, p = agg["engagement"], agg["proposal"]
    use_proposal = p["E1"] >= 0.95 * e["E1"] and (p["depth"] > e["depth"] or p["P1"] > e["P1"])
    return {"R1_works": works, "R1_detail": r1, "R2_means": agg,
            "R2_reward_for_main_study": "proposal" if use_proposal else "engagement"}


def report(res):
    L = ["# D1.0 pilot (validation only, before the freeze)", "",
         "Validation runs only; seeds 101-103; 200k environment steps; means over seeds.",
         "E1 = engaged commands per episode; P1 = defense success; depth = distinct techniques engaged; "
         "exposed = share of episodes where the deception was exposed.", ""]
    for fid, blk in res["folds"].items():
        L += [f"## fold {fid} (validation run: {', '.join(blk['validation_runs'])})", "",
              "| policy | E1 | P1 | depth | exposed |", "|---|---|---|---|---|"]
        for n, v in blk["references"].items():
            L.append(f"| {n} | {v['E1']:.2f} | {v['P1']:.2f} | {v['depth']:.2f} | {v['exposed']:.2f} |")
        for arm in ARMS:
            for rw in REWARDS:
                if mean_cells(blk, arm, rw, "E1") is None:
                    continue
                L.append(f"| **{arm}, {rw} reward** | {mean_cells(blk, arm, rw, 'E1'):.2f} | "
                         f"{mean_cells(blk, arm, rw, 'P1'):.2f} | {mean_cells(blk, arm, rw, 'depth'):.2f} | "
                         f"{mean_cells(blk, arm, rw, 'exposed'):.2f} |")
        L.append("")
    d = res.get("decisions")
    if d:
        L += ["## Decisions (rules declared before the pilot)", "",
              f"- R1 works: **{'PASS' if d['R1_works'] else 'FAIL'}** {json.dumps(d['R1_detail'])}",
              f"- R2 reward means: {json.dumps(d['R2_means'])}",
              f"- R2 reward for the main study: **{d['R2_reward_for_main_study']}**",
              "- R3: history differences above are reported only; they decide nothing."]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
