# -*- coding: utf-8 -*-
"""
TEMARL v5 — PRE-REGISTRATION (repaired-instrument confirmatory experiment)
===========================================================================
Written and committed BEFORE the confirmatory run. Nothing here may be edited
once its results are observed.

THE v4 RESULT STANDS. It is not withdrawn or replaced. v4 asked "does attention
beat recurrence on DSR?" and answered "no declared contrast reached
significance." That remains the pre-registered finding for that environment and
will be reported alongside whatever this experiment produces.

=============================================================================
FULL DISCLOSURE OF THE EXPLORATORY WORK THAT LED HERE
=============================================================================
This experiment is CONFIRMATORY. A pilot found the effect it tests. Reporting a
confirmatory result without disclosing the pilot that motivated it would be
exactly the practice this project forbids, so the whole path is recorded here.

  1. v4 produced 8 null contrasts. Two post-hoc measurements, neither
     referencing which architecture wins, showed the null was uninterpretable:
       - a perfect next-technique model was worth +0.0005 DSR over a 3-way
         campaign label, so the task could not discriminate ANY history
         architecture (`baselines_entity.py`, `verdict_v4.py`);
       - 5 of 6 arms never beat a memoryless fixed action.

  2. ENVIRONMENT REPAIR (`profiles_v5.py`). Removed `T[:, j] += 1.2`, a
     column-constant added to every row of the transition matrix. A quantity
     identical in every row carries zero information about the transition, and
     it outweighed the real bigram evidence ~2:1. Setting it back to 1.2
     reproduces the v2 profiles bit-for-bit, so exactly one factor moved.
         within-campaign I(tau';tau)  0.627 -> 1.935 bits (raw CAM-LDS 4.83)
         sequence value (DSR)         +0.0005 -> +0.0800

  3. CALIBRATION (`calibrate_v5.py`). The repair tripled episode length and
     saturated DSR at 0.79-0.98 -- the failure env_v2's own gate rejects. A grid
     was scored against four criteria fixed in advance using BASELINE POLICIES
     ONLY. Exactly one cell of 20 passed: goal_steps=3, cap_scale=0.35.

  4. TWO FAILED HYPOTHESES ABOUT THE LEARNER, both recorded because they were
     wrong and the record should show it:
       - "the reward fights the metric": measured corr(return, DSR) = +0.983.
         FALSE.
       - "PPO's agent-averaged log-prob collapse is the bug": fixing it moved
         DSR 0.5400 -> 0.5167, i.e. WORSE. FALSE. The fix survives only as the
         opt-in `per_agent` flag, defaulting to the v4 behaviour.

  5. TRAINING METHOD (architecture-blind decision). Under PPO, NO arm cleared
     the memoryless baseline at any budget tried (240 eps 0.510, 1200 eps 0.523,
     best_fixed 0.5475). Behaviour cloning on the transition oracle does clear
     it (GRU 0.5911, 47.7% of headroom). That decision was made from GRU-ONLY
     runs, before any Transformer was cloned. v2 also trained by imitation
     (`train_v2.py`, IL_EPISODES=1200), so this is precedent, not novelty.

  6. THE PILOT (`results_v5/bc_compare.json`, 3 seeds, EXPLORATORY):
         regime B (trained sizes) : Transformer - GRU = -0.0000 DSR
         regime D (unseen sizes)  : Transformer - GRU = +0.0333 DSR
                                    GRU 31.5% of headroom, Transformer 90.0%

  7. CONFOUND CONTROL (`results_v5/confound_v5.json`, 3 seeds, EXPLORATORY).
     The history encoder reads only the technique sequence, so it cannot
     generalise across topologies by itself; what differs downstream is h width
     (Transformer d_model=32, GRU d_model=128). A width-matched GRU-d32 was
     built and tested:
         regime D headroom:  GRU 31.5% | GRU-d32 27.6% | Transformer 82.2%
     The width-matched GRU behaves like the WIDE GRU, not the Transformer, so h
     width does not explain the effect. GRU-d32 is carried below as a DECLARED
     CONTROL ARM rather than discarded.
     The same run at trained sizes:
         regime B headroom:  GRU 54.9% | GRU-d32 62.2% | Transformer 40.4%
     i.e. the Transformer was WORST at trained sizes. Both directions are
     carried into the contrast family below; neither is dropped.

Everything above is n=3, uncorrected, with no statistical test. It is a pilot.
This file exists to test it properly.
=============================================================================

NO OUTCOME IS PRIVILEGED. If the crossover does not survive 10 seeds and Holm
correction, that is the result and the architecture claim is retired again.
"""

from __future__ import annotations

# ── factors ──────────────────────────────────────────────────────────────────
# GRU-d32 is the h-width control, not a hypothesis: it exists so that any
# Transformer advantage at unseen sizes can be attributed to architecture rather
# than to the narrower h the Phase 2.4 tuning happened to give it.
HISTORY_ENCODERS = ("Transformer-RoPE", "GRU", "GRU-d32")
ARMS = [("Transformer-RoPE", "DeepSets"),
        ("GRU", "DeepSets"),
        ("GRU-d32", "DeepSets"),
        ("Transformer-RoPE", "EntityTransformer"),
        ("GRU", "EntityTransformer")]

TRAINING = "behaviour cloning on the transition oracle"
BC_EPISODES = 300           # teacher rollouts collected
BC_STEPS = 2500             # clone gradient steps
PRETRAIN_STEPS = 1500       # history-encoder pretraining, then FROZEN
OBJECTIVE = "action"
MAX_SEQ_LEN = 16
N_AGENTS = 4
MAX_ENTITIES = 48
MAX_STEPS = 40

# ── the calibrated v5 environment (architecture-blind, calibrate_v5.py) ──────
CAP_SCALE = 0.35
GOAL_STEPS = 3
PROFILE_SOURCE = "profiles_v5.profiles_v5  (goal drift removed)"

# ── encoder specs; the two tuned ones are verbatim Phase 2.4, NOT re-tuned ───
HPARAMS = {
    "Transformer-RoPE": {"n_layers": 4, "n_heads": 8, "d_ff": 512,
                         "d_model": 32, "lr": 1e-3},
    "GRU": {"hidden": 256, "n_layers": 1, "d_model": 128, "lr": 3e-4},
    "GRU-d32": {"hidden": 256, "n_layers": 1, "d_model": 32, "lr": 3e-4},
}

SEEDS = tuple(range(10))
EVAL_EPISODES = 200

PRIMARY_METRIC = "dsr"
MECHANISM_METRIC = "alignment"
ALPHA = 0.05
REGIMES = ("A", "B", "C", "D")
REGIME_DESC = {
    "A": "canonical 5-zone control",
    "B": "new topologies, TRAINED sizes",
    "C": "unseen structure (different firewall density)",
    "D": "unseen sizes (9/11/13 zones)",
}

# ── VALIDITY GATE — reported BEFORE any contrast, and it can void them ───────
VALIDITY_GATE = {
    "rule": "every arm must beat the best_fixed baseline on regime B by a "
            "paired t-test over the 10 seeds, p < 0.05",
    "baseline_file": "results_v5/baselines_v5.json",
    "if_failed": "contrasts involving a failing arm are reported IN FULL but "
                 "labelled VOID, and no architecture claim may rest on them",
}

# ── hypotheses ───────────────────────────────────────────────────────────────
HYPOTHESES = [
    ("H16", "At UNSEEN topology sizes the Transformer history encoder beats "
            "the GRU on DSR (the arXiv:2410.17647 pattern)", "dsr"),
    ("H17", "At TRAINED sizes the two are indistinguishable -- the other half "
            "of the same claim, which the pilot did not support: it showed the "
            "Transformer BEHIND at trained sizes", "dsr"),
    ("H18", "The unseen-size advantage is architectural, not an h-width "
            "artefact: the Transformer also beats the width-matched GRU-d32", "dsr"),
    ("H19", "The EntityTransformer network encoder beats DeepSets at unseen "
            "sizes -- the entity-attention half of the same paper, which v4 "
            "could not test because it froze the network encoder", "dsr"),
]

TEST = "paired t-test on per-seed means"
CORRECTION = "Holm-Bonferroni over the declared contrast family, alpha=0.05"
EFFECT_SIZE = "paired Cohen's d = mean(diff) / sd(diff)"
REPORT_ALSO = ("95% CI on every contrast; each arm's headroom capture against "
               "the best_fixed -> transition-oracle span, per regime; wall-clock "
               "and parameter counts; and the v4 numbers side by side")

# (label, arm_a, arm_b, regime) -- exactly these, fixed in advance.
# H17 deliberately includes regimes A/B where the PILOT WENT AGAINST the
# hypothesis. Dropping them after seeing the pilot would be the exact practice
# this project forbids.
CONTRAST_FAMILY = [
    ("H16-D", ("Transformer-RoPE", "DeepSets"), ("GRU", "DeepSets"), "D"),
    ("H16-C", ("Transformer-RoPE", "DeepSets"), ("GRU", "DeepSets"), "C"),
    ("H17-B", ("Transformer-RoPE", "DeepSets"), ("GRU", "DeepSets"), "B"),
    ("H17-A", ("Transformer-RoPE", "DeepSets"), ("GRU", "DeepSets"), "A"),
    ("H18-D", ("Transformer-RoPE", "DeepSets"), ("GRU-d32", "DeepSets"), "D"),
    ("H18-B", ("Transformer-RoPE", "DeepSets"), ("GRU-d32", "DeepSets"), "B"),
    ("H19-DT", ("Transformer-RoPE", "EntityTransformer"),
               ("Transformer-RoPE", "DeepSets"), "D"),
    ("H19-DG", ("GRU", "EntityTransformer"), ("GRU", "DeepSets"), "D"),
]

INHERITED_GATES = {
    "vocab_unk_camlds": 0,
    "env_v2_equivalence_mismatches": 0,
    "payoff_rows_0_77_bit_identical": True,
    "payoff_never_refitted": True,
    "v5_sequence_value_min": 0.03,
}

DECLARATION = (
    "Pre-registered before the confirmatory run. Hypotheses, arms, seeds, "
    "primary metric, contrast family, correction, encoder specs and training "
    "budget are fixed here and are not to be modified after observing results. "
    "Every declared contrast is reported whatever its outcome, including H17 "
    "where the pilot ran AGAINST the hypothesis. The validity gate is reported "
    "FIRST and may void the architecture claim. The full exploratory path that "
    "motivated this experiment -- including two failed hypotheses and a 3-seed "
    "pilot -- is disclosed in this file's docstring. The v4 null is not "
    "withdrawn. A null result here retires the architecture claim again."
)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("=" * 96)
    print("  TEMARL v5 — PRE-REGISTRATION (confirmatory)")
    print("=" * 96)
    print("  training         : %s" % TRAINING)
    print("  arms             : %d x %d seeds = %d runs"
          % (len(ARMS), len(SEEDS), len(ARMS) * len(SEEDS)))
    for a in ARMS:
        print("      %-18s / %-18s%s"
              % (a[0], a[1], "   <- h-width CONTROL" if a[0] == "GRU-d32"
                 else ""))
    print("  env              : cap_scale %.2f, goal_steps %d, %s"
          % (CAP_SCALE, GOAL_STEPS, PROFILE_SOURCE))
    print("  budget           : %d teacher episodes, %d clone steps, %d "
          "pretrain steps" % (BC_EPISODES, BC_STEPS, PRETRAIN_STEPS))
    print("\n  VALIDITY GATE (reported first, can void contrasts):")
    print("    %s" % VALIDITY_GATE["rule"])
    print("\n  hypotheses:")
    for k, d, m in HYPOTHESES:
        print("    %-5s %s" % (k, d))
    print("\n  contrast family (%d declared):" % len(CONTRAST_FAMILY))
    for lab, a, b, r in CONTRAST_FAMILY:
        print("    %-8s %-40s vs %-36s regime %s"
              % (lab, "%s/%s" % a, "%s/%s" % b, r))
    print("\n  %s" % DECLARATION)
    print("=" * 96)
