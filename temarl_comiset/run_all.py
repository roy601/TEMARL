# -*- coding: utf-8 -*-
"""Train every cell of the pre-registered comparison, then evaluate."""
import sys, time, json, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from env_v2 import build_profiles_from_camlds
from train_v2 import train_arm

CFG = dict(enc_eps=900, enc_steps=2500, il_steps=2000, ppo_iters=15)
ARMS = [("Transformer", True), ("GRU", True), ("SetEncoder", True),
        ("Transformer", False)]          # last = NoTrans (h=0) ablation

profiles, _ = build_profiles_from_camlds()
summary = {}
t0 = time.time()
for name, use_h in ARMS:
    tag = f"{name}{'' if use_h else '_NoTrans'}"
    print(f"\n{'='*70}\n  TRAINING {tag}\n{'='*70}", flush=True)
    r = train_arm(name, profiles, seed=0, use_h=use_h, verbose=True, **CFG)
    a = r["encoder"]["after"]
    summary[tag] = {
        "top1": a["top1"], "majority": a["majority"], "beats_majority": a["beats_majority"],
        "top3": a["top3"], "freq3": a["freq_top3"], "beats_freq3": a["beats_freq3"],
        "macro_f1": a["macro_f1"], "ppl": a["perplexity"], "uniform_ppl": a["uniform_ppl"],
        "imitation_align": r["imitation"]["alignment"], "imitation_dsr": r["imitation"]["dsr"],
        "ppo_best_align": r["ppo"]["best_alignment"],
    }
    print(f"  [{tag}] done  imitation={r['imitation']['alignment']:.4f} "
          f"ppo_best={r['ppo']['best_alignment']:.4f}  "
          f"({time.time()-t0:.0f}s elapsed)", flush=True)

json.dump(summary, open("results_v2/training_summary.json", "w"), indent=1)
print(f"\nALL ARMS TRAINED in {time.time()-t0:.0f}s")
for k, v in summary.items():
    print(f"  {k:<22} top1={v['top1']:.3f} (maj {v['majority']:.3f}) "
          f"macroF1={v['macro_f1']:.3f} imit={v['imitation_align']:.4f}")
