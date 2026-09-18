# -*- coding: utf-8 -*-
"""
TEMARL v3 — Performance by topology and network size
=====================================================
Breaks the aggregate regime numbers down per ZONE COUNT, which the regime-level
table hides: regime D mixes 9-, 11- and 13-zone topologies, so a single D number
cannot show whether degradation is graceful or a cliff.

Loads the checkpoints written by `train_entity.py --save-checkpoints` and
re-derives each seed's FROZEN history encoders deterministically from the seed
(`pretrain_history` is fully seeded), because those are a function of the seed
and the training topology set rather than of the policy.

Defaults to a SUBSET of seeds: this re-pretrains history encoders, which is the
expensive part, and a per-size breakdown is descriptive rather than a
pre-registered test. The pre-registered statistics live in `evaluate_entity.py`
and use all seeds.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict

import numpy as np
import torch

import prereg_v3 as PR
from entity_encoders import match_entity_capacity
from policy_entity import EntityAgentNet
from topology import generate_topology
from train_entity import RUNS, build_topologies, evaluate, pretrain_history

HERE = os.path.dirname(os.path.abspath(__file__))


def sized_topologies(regime: str, n_zones: int):
    """The topologies of exactly one size drawn from a regime's spec."""
    spec = PR.topology_spec()[regime]
    out = []
    for i, s in enumerate(spec["seeds"]):
        nz = spec["sizes"][i % len(spec["sizes"])]
        if nz == n_zones:
            out.append(generate_topology(seed=s, n_zones=nz,
                                         n_agents=PR.N_AGENTS,
                                         p_firewall_block=spec["p_firewall_block"]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="*", default=[0, 1, 2])
    ap.add_argument("--episodes", type=int, default=120)
    ap.add_argument("--out", default=os.path.join(HERE, "results_v3",
                                                  "entity_by_size.json"))
    args = ap.parse_args()
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    train_topos = build_topologies("train")
    sizes = [(rg, nz) for rg, szs in (("B", PR.TRAIN_ZONE_SIZES),
                                      ("C", PR.TRAIN_ZONE_SIZES),
                                      ("D", PR.UNSEEN_ZONE_SIZES))
             for nz in szs]

    print("=" * 96)
    print("  TEMARL v3 — PERFORMANCE BY TOPOLOGY SIZE")
    print("=" * 96)
    print(f"  seeds {args.seeds}  |  {args.episodes} eval episodes per cell")
    print(f"  trained sizes {PR.TRAIN_ZONE_SIZES}   unseen sizes "
          f"{PR.UNSEEN_ZONE_SIZES}\n")

    acc = defaultdict(list)
    for seed in args.seeds:
        hist = {h: pretrain_history(h, seed, train_topos)
                for h in PR.HISTORY_ENCODERS}
        for net_name in PR.NETWORK_ENCODERS:
            for hist_name in PR.HISTORY_ENCODERS:
                ck = os.path.join(RUNS, f"{net_name}_{hist_name}_s{seed}.pt")
                if not os.path.exists(ck):
                    print(f"  [skip] missing checkpoint {os.path.basename(ck)}")
                    continue
                suite, _ = match_entity_capacity()
                net = EntityAgentNet(suite[net_name])
                net.load_state_dict(torch.load(ck, map_location="cpu")["net"])
                for rg, nz in sizes:
                    tp = sized_topologies(rg, nz)
                    if not tp:
                        continue
                    m = evaluate(net, hist[hist_name], tp, args.episodes, seed)
                    acc[(net_name, hist_name, rg, nz)].append(m["dsr"])
        del hist

    print(f"  {'network':<19}{'history':<13}{'regime':<8}"
          + "".join(f"{f'{nz}z':>9}" for nz in
                    sorted(set(PR.TRAIN_ZONE_SIZES) | set(PR.UNSEEN_ZONE_SIZES))))
    print("  " + "-" * 92)
    all_sizes = sorted(set(PR.TRAIN_ZONE_SIZES) | set(PR.UNSEEN_ZONE_SIZES))
    rows = []
    for net_name in PR.NETWORK_ENCODERS:
        for hist_name in PR.HISTORY_ENCODERS:
            for rg in ("B", "C", "D"):
                cells = []
                for nz in all_sizes:
                    v = acc.get((net_name, hist_name, rg, nz))
                    cells.append(f"{np.mean(v):.3f}" if v else "-")
                    if v:
                        rows.append({"network_encoder": net_name,
                                     "history_encoder": hist_name, "regime": rg,
                                     "n_zones": nz, "dsr": float(np.mean(v)),
                                     "n_seeds": len(v)})
                if any(c != "-" for c in cells):
                    print(f"  {net_name:<19}{hist_name:<13}{rg:<8}"
                          + "".join(f"{c:>9}" for c in cells))

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"seeds": args.seeds, "episodes": args.episodes,
                   "trained_sizes": list(PR.TRAIN_ZONE_SIZES),
                   "unseen_sizes": list(PR.UNSEEN_ZONE_SIZES),
                   "rows": rows}, f, indent=1, default=float)
    print(f"\n  wrote -> {os.path.relpath(args.out, HERE)}")
    print("=" * 96)


if __name__ == "__main__":
    main()
