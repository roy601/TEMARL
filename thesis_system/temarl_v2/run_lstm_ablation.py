# -*- coding: utf-8 -*-
"""
TEMARL — LSTM ablation (COMPLETENESS, declared as such)
========================================================
The v1 manuscript listed an LSTM comparison as future work (`encoders.py:14`)
and it stayed future work through v2-v6. So every "attention vs recurrence"
statement in this project has until now been tested against ONE recurrent
architecture. This closes that gap.

STATUS AND HONESTY CONDITIONS
------------------------------
* This is a COMPLETENESS ABLATION, not a confirmatory test. It adds an arm to
  the descriptive comparison; it does not re-open, re-scope or re-test any
  pre-registered contrast. `prereg_v5.py` and `prereg_v6.py` are untouched on
  disk and their verdicts stand exactly as reported.
* The LSTM is given the GRU's Phase 2.4 tuned configuration verbatim
  (hidden=256, n_layers=1, d_model=128, lr=3e-4). It has NOT had its own
  equal-budget hyperparameter search. That is a stated limitation and it biases
  AGAINST the LSTM -- the honest direction, since the LSTM is here as a control,
  not as a hypothesis.
* An LSTM cell carries ~4/3 the parameters of a GRU cell at equal width
  (450,518 vs 351,702), so capacity is REPORTED, not assumed matched.
* Padding discipline is identical (`pack_padded_sequence`, F-ARC-06). Without it
  PAD embeddings contaminate the final hidden state and manufacture a spurious
  "Transformer wins".
* Protocol is identical to v5 in every other respect: same repaired environment,
  same behaviour cloning on the transition oracle, same 10 seeds, same 200
  evaluation episodes, same four regimes.

Whatever this shows is reported. If the LSTM beats both, that is the result.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

import numpy as np

import prereg_v5 as PR
import run_v5
from encoders import LSTMIntentEncoder
from train_entity_v5 import RESULTS, build_topologies, evaluate

# Register the ablation arm at RUNTIME. `prereg_v5.py` is not edited on disk;
# this adds a descriptive arm alongside the pre-registered ones.
run_v5.BUILD["LSTM"] = LSTMIntentEncoder
PR.HPARAMS.setdefault("LSTM", {"hidden": 256, "n_layers": 1, "d_model": 128,
                               "lr": 3e-4})   # GRU's tuned config, verbatim

OUT = os.path.join(os.path.dirname(RESULTS), "results_v7")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="*", default=list(PR.SEEDS))
    ap.add_argument("--network", default="DeepSets")
    ap.add_argument("--out", default=os.path.join(OUT, "lstm_ablation.json"))
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    topos = {r: build_topologies(r) for r in PR.REGIMES}
    rows, t0 = [], time.time()
    print("=" * 100)
    print("  TEMARL — LSTM ABLATION (completeness; not a pre-registered test)")
    print("=" * 100)
    print("  LSTM/%s, %d seeds, protocol identical to v5"
          % (args.network, len(args.seeds)))
    print("  hparams: %s  (GRU's tuned config verbatim; no LSTM-specific search)"
          % PR.HPARAMS["LSTM"])

    for seed in args.seeds:
        ts = time.time()
        enc = run_v5.pretrain("LSTM", seed, topos["B"])
        net, acc = run_v5.clone(enc, args.network, seed, topos["B"])
        row = {"history_encoder": "LSTM", "network_encoder": args.network,
               "objective": PR.OBJECTIVE, "seed": seed, "teacher_acc": acc,
               "d_model": PR.HPARAMS["LSTM"]["d_model"],
               "n_params_hist": sum(p.numel() for p in enc.parameters()),
               "n_params_pol": sum(p.numel() for p in net.parameters()),
               "train_seconds": time.time() - ts}
        for rg in PR.REGIMES:
            for k, v in evaluate(net, enc, topos[rg], PR.EVAL_EPISODES,
                                 seed).items():
                row["%s_%s" % (rg, k)] = v
        rows.append(row)
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump({"ablation": True,
                       "not_part_of_prereg": "prereg_v5.py / prereg_v6.py",
                       "hparams": PR.HPARAMS["LSTM"],
                       "hparam_caveat": "GRU's tuned config; no LSTM-specific "
                                        "equal-budget search was run",
                       "rows": rows,
                       "complete": len(rows) == len(args.seeds),
                       "seconds": time.time() - t0}, f, indent=1, default=float)
        print("  [%2d/%2d] seed %d | acc %.3f | A %.4f  B %.4f  C %.4f  D %.4f "
              "| %.0f s"
              % (len(rows), len(args.seeds), seed, acc, row["A_dsr"],
                 row["B_dsr"], row["C_dsr"], row["D_dsr"], row["train_seconds"]))

    print("\n  DONE %d seeds in %.0f s -> %s"
          % (len(rows), time.time() - t0, os.path.relpath(args.out, RESULTS)))
    for rg in PR.REGIMES:
        v = np.array([r["%s_dsr" % rg] for r in rows])
        print("    regime %s  DSR %.4f +- %.4f"
              % (rg, v.mean(), 1.96 * v.std(ddof=1) / np.sqrt(len(v))))
    print("=" * 100)


if __name__ == "__main__":
    main()
