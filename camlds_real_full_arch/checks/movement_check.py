# -*- coding: utf-8 -*-
"""D2 check: does the environment's random-walk attacker movement match the recorded runs?

Read-only. No training, no policy, no test scoring. Writes checks/MOVEMENT_CHECK.txt.

Recorded zone of each command: d1_data.positions() (AttackMate execution records + AttackBed sources;
every rule is documented there). Model: env_cmd's own random-walk `_move` (p_goal 0.7, p_stay 0.8),
no defence, over each run's full length, with the hand-typed targets the model was built with
(scenario_metadata("hand")) and uniforms drawn exactly as make_spec draws them; 20 draws per run.
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import pipeline as P  # noqa: E402  (sets the frozen paths exactly as the study does)

env = P.env
UNDEFENDED = ("Internet", "Firewall")


def all_runs():
    runs = {}
    for f in P.data.folds():
        for split in ("train", "val", "test"):
            for r in P.runs(f, split):
                runs[r["id"]] = r
    return runs


def model_zones(run, meta, seed):
    e = env.CommandEngagementEnv(env.EnvConfig(movement="random_walk"))
    spec = env.make_spec(run, np.random.default_rng(seed), meta)
    e.reset(spec)
    zs = []
    for t in range(spec.horizon):
        e.zone = e._move(spec.u[env.U_MOVE, t], spec.u[env.U_LATERAL, t])
        zs.append(env.POSITIONS[e.zone])
    return zs


def stats(zs, target):
    stay = [b == a for a, b in zip(zs, zs[1:]) if a == target]
    return {"changes": sum(a != b for a, b in zip(zs, zs[1:])),
            "frac_target": float(np.mean([z == target for z in zs])),
            "stay_target": float(np.mean(stay)) if stay else float("nan"),
            "frac_undefended": float(np.mean([z in UNDEFENDED for z in zs]))}


def main():
    meta = env.scenario_metadata("hand")
    runs = all_runs()
    lines = ["D2 movement check (read-only). Zone = where the command executes.", "",
             "run | n | target | recorded: changes / in-target / stay-in-target / undefended | "
             "model (mean of 20 draws): changes / in-target / stay-in-target", ""]
    agg = {"rec": [], "mod": []}
    pairs = Counter()
    for k, rid in enumerate(sorted(runs)):
        r = runs[rid]
        zs = r["positions"]
        tgt = env.POSITIONS[meta[r["scenario"]]["target"]]
        a = stats(zs, tgt)
        ms = [stats(model_zones(r, meta, 900000 + 100 * k + d), tgt) for d in range(20)]
        b = {key: float(np.nanmean([m[key] for m in ms])) for key in ms[0]}
        agg["rec"].append(a)
        agg["mod"].append(b)
        for x, y in zip(zs, zs[1:]):
            pairs["same" if x == y else "move"] += 1
        path = []
        for z in zs:
            if not path or path[-1][0] != z:
                path.append([z, 0])
            path[-1][1] += 1
        lines.append(f"{rid} | {len(zs)} | {tgt} | {a['changes']} / {a['frac_target']:.2f} / "
                     f"{a['stay_target']:.2f} / {a['frac_undefended']:.2f} | {b['changes']:.1f} / "
                     f"{b['frac_target']:.2f} / {b['stay_target']:.2f}")
        lines.append("    recorded path: " + " -> ".join(f"{z}x{c}" for z, c in path))
    lines.append("")
    for name in ("rec", "mod"):
        A = agg[name]
        lines.append(f"{'recorded' if name == 'rec' else 'model   '}: mean zone changes per run "
                     f"{np.mean([x['changes'] for x in A]):.2f}; mean share of commands in target "
                     f"{np.mean([x['frac_target'] for x in A]):.3f}; mean stay-in-target "
                     f"{np.nanmean([x['stay_target'] for x in A]):.3f}; mean share in undefended zones "
                     f"{np.mean([x['frac_undefended'] for x in A]):.3f}")
    lines.append(f"recorded: {pairs['same']} consecutive command pairs in the same zone, "
                 f"{pairs['move']} zone changes, over {sum(len(r['positions']) for r in runs.values())} commands")
    (HERE / "MOVEMENT_CHECK.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[-4:]))


if __name__ == "__main__":
    main()
