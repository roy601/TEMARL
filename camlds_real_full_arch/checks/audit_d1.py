# -*- coding: utf-8 -*-
"""Protocol D1.0 audit: does everything that should run actually run, and do the agents use h?

    python camlds_real_full_arch/checks/audit_d1.py      # about 5 min on a CPU; writes checks/AUDIT_D1.txt

Validation runs only. No protocol test run is used: where a code path writes test episodes, this
process redirects pipeline.runs(fold, "test") to the validation runs, and everything goes to a temp
folder that is deleted. Seeds 101 and 777 are outside the protocol's seeds 0-9. Training on a CPU is
deterministic on one machine; another machine may give slightly different numbers in part B.

  A  data: defended zones each recorded run visits (how much team coordination the data asks for);
     commands the history h contains that a defender cannot see directly (attacker machine, firewall)
  B  learning and history: pilot learning curves; agents trained on the 3 pilot folds (seed 101,
     200,000 steps, primary setting): validation E1 with h and with h zeroed, decisions h changes,
     team activity (decoys per step, steps with >= 2 decoys, each agent's decoy share)
  C  code paths the unit tests do not reach: a cell with test=True (sealing, no test number in
     result.json), the dry-run reproduction (MAPPO and IPPO), the execution-order encoder retraining
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
import pipeline as P  # noqa: E402
import run_d1 as R  # noqa: E402
import evaluate_d1 as E  # noqa: E402
import gate_d1 as G  # noqa: E402
import pilot_d1 as PL  # noqa: E402

env, marl, data = P.env, P.marl, P.data
SEED, STEPS = 101, 200_000
DEF = tuple(env.POSITIONS[z] for z in env.AGENT_ZONE)


def part_a():
    runs = G.all_runs()
    visits, share, by_s = Counter(), [], {}
    for r in runs:
        z = [p for p in r["positions"] if p in DEF]
        vis = [d for d in DEF if d in z]
        visits[len(vis)] += 1
        share.append(max(Counter(z).values()) / len(z))
        by_s.setdefault(r["scenario"], Counter())["+".join(vis)] += 1
    allpos = Counter(p for r in runs for p in r["positions"])
    n = sum(allpos.values())
    L = ["A. Data", f"  runs by number of defended zones visited: {dict(sorted(visits.items()))} (of {len(runs)})",
         f"  share of a run's defended commands in its busiest zone: mean {np.mean(share):.2f}, min {min(share):.2f}",
         "  per scenario: " + "; ".join(f"{s} {dict(c)}" for s, c in sorted(by_s.items())),
         f"  commands per position: {dict(allpos)}; Admin visited by the recorded attacker: {allpos.get('Admin', 0)} commands",
         f"  history h includes commands on the attacker machine (Internet) {allpos['Internet']} "
         f"({100 * allpos['Internet'] / n:.1f}%) and on the firewall {allpos['Firewall']} ({100 * allpos['Firewall'] / n:.1f}%)"]
    return L


@torch.no_grad()
def team_rollout(actor, specs, bank, cfg):
    st, per_agent = Counter(), [Counter() for _ in range(env.N_AGENTS)]
    for s in specs:
        tab = bank.table(s)
        e = env.CommandEngagementEnv(cfg).reset(s)
        while not e.done:
            Lo = torch.as_tensor(e.local_obs())
            H = torch.as_tensor(np.repeat(tab[e.t][None], env.N_AGENTS, 0))
            a = actor(Lo, H).argmax(-1).numpy()
            a0 = actor(Lo, torch.zeros_like(H)).argmax(-1).numpy()
            st["decisions"] += env.N_AGENTS
            st["changed_by_h"] += int((a != a0).sum())
            st["steps"] += 1
            st["active"] += int((a != env.NULL).sum())
            st["multi"] += int((a != env.NULL).sum() >= 2)
            for i in range(env.N_AGENTS):
                per_agent[i][int(a[i] != env.NULL)] += 1
            e.step(a)
    return st, [c[1] / max(1, sum(c.values())) for c in per_agent]


def part_b():
    res = json.loads((ROOT / "results_d1" / "pilot" / "PILOT_RESULTS.json").read_text(encoding="utf-8"))
    cur = [c["curve_val_E1"] for blk in res["folds"].values() for c in blk["cells"].values()]
    L = ["B. Learning and history",
         f"  pilot cells whose best validation E1 exceeds their first evaluation: {sum(max(c) > c[0] for c in cur)} of {len(cur)}"
         f" (mean {np.mean([c[0] for c in cur]):.2f} -> {np.mean([max(c) for c in cur]):.2f}); best at the last "
         f"evaluation (still rising at 200,000 steps): {sum(c.index(max(c)) == len(c) - 1 for c in cur)}",
         f"  trained here: seed {SEED}, {STEPS} steps, reward {R.setting(None)[0].reward}, validation runs, 10 repeats"]
    cfg = R.setting(None)[0]
    folds = {f["fold"]: f for f in P.ordered_folds("frozen")}
    for fid in PL.FOLDS:
        f = folds[fid]
        va = R.specs(P.runs(f, "val"), R.VAL_SEED + SEED, 10, cfg)
        assert not {sp.run_id for sp in va} & set(f["test_runs"])
        for arm in ("allpos", "NoHistory"):
            model = PL.encoder(arm, f, SEED, "cpu")
            r = marl.train(model, cfg, P.runs(f, "train"), va, [], SEED, STEPS, data.W, 64, True, "cpu", False)
            actor = marl.Actor()
            actor.load_state_dict(r["actor_state"])
            bank = marl.HistoryBank(model, data.W, "cpu", h_zero=(model is None))
            e1 = marl.mean_of(marl.evaluate_team(actor, cfg, va, bank, 64, "cpu"))
            e0 = marl.mean_of(marl.evaluate_team(actor, cfg, va, bank, 64, "cpu", h_zero=True))
            st, share = team_rollout(actor, va, bank, cfg)
            L.append(f"  {fid} {arm:9s}: val E1 {e1:5.2f}, h zeroed {e0:5.2f}, decisions changed by h "
                     f"{100 * st['changed_by_h'] / st['decisions']:4.1f}%, decoys/step {st['active'] / st['steps']:.2f}, "
                     f"steps with >=2 decoys {100 * st['multi'] / st['steps']:4.1f}%, decoy share per agent "
                     + ", ".join(f"{z} {s:.2f}" for z, s in zip(DEF, share)))
    return L


def part_c():
    L = ["C. Code paths the unit tests do not reach"]
    _runs, _load, budget = P.runs, R.load_encoder, dict(R.ENCODER_BUDGET)
    hp = dict(marl.HP)
    P.runs = lambda fold, split: _runs(fold, "val" if split == "test" else split)
    marl.HP.update(n_envs=8, rollout_len=16, n_evals=3)
    try:
        f = {x["fold"]: x for x in P.ordered_folds("frozen")}["1_cron_sshkey"]
        enc = PL.encoder("allpos", f, SEED, "cpu")
        R.load_encoder = lambda arm, fold, seed, root, device, cell=None, order="frozen": (
            (enc, {"arm": arm, "checkpoint": "pilot"}) if arm != "NoHistory"
            else _load(arm, fold, seed, root, device, cell, order))
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            for arm, learner in (("allpos", "MAPPO"), ("NoHistory", "IPPO")):
                a = argparse.Namespace(sensitivity=None, eval_repeats=3, encoder_root=str(tmp), device="cpu",
                                       env_steps=8 * 16 * 6, verbose=False)
                dest = tmp / "cells" / arm / f["fold"] / "s777" / learner
                R.run_cell(arm, learner, f, 777, a, dest, test=True)
                disk = json.loads((dest / "result.json").read_text(encoding="utf-8"))
                leaked = [k for k in ("test", "test_summary", "test_h0_summary") if k in disk]
                _, sealed = E.read_sealed(dest)
                got, rec = R.revalidate(dest, f, 777, enc if arm != "NoHistory" else None, "cpu", R.setting(None)[0])
                ok = not leaked and bool(sealed["test"]) and abs(got - rec) <= 1e-9
                L.append(f"  {arm} {learner} cell with test=True: sealed file SHA-256 ok, test numbers in result.json: "
                         f"{leaked or 'none'}; dry-run reproduction |difference| {abs(got - rec):.1e} -> {'PASS' if ok else 'FAIL'}")
            R.load_encoder = _load
            R.ENCODER_BUDGET["allpos"] = 64
            ex = {x["fold"]: x for x in P.ordered_folds("execution")}["6_macro_cron"]
            _, info = R.load_encoder("allpos", ex, 777, tmp, "cpu", cell=tmp / "exec" / "s777", order="execution")
            L.append(f"  execution-order encoder (Section 8): trained in the cell, reloaded, validation BCE "
                     f"{info['validation_bce']:.4f} reproduced -> PASS")
    finally:
        P.runs, R.load_encoder = _runs, _load
        R.ENCODER_BUDGET.clear(); R.ENCODER_BUDGET.update(budget)
        marl.HP.clear(); marl.HP.update(hp)
    return L


def main():
    torch.set_num_threads(4)
    L = ["Protocol D1.0 audit (validation runs only; no protocol test run is used)", ""]
    for part in (part_a, part_b, part_c):
        L += part() + [""]
    text = "\n".join(L)
    (HERE / "AUDIT_D1.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
