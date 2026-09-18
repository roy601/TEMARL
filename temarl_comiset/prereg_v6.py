# -*- coding: utf-8 -*-
"""
TEMARL v6 — PRE-REGISTERED REPLICATION of H19-DG at adequate power
===================================================================
Written and committed BEFORE this replication ran. Nothing here may be edited
once its results are observed.

WHY A REPLICATION, AND WHY THIS IS NOT p-HACKING
-------------------------------------------------
v5 declared 8 contrasts and reported all 8. One of them, **H19-DG**, came out

    GRU/EntityTransformer vs GRU/DeepSets, unseen topology sizes (regime D)
    delta = +0.0180   paired d = 0.61   p_raw = 0.0862   p_holm = 0.690
    90% CI [+0.0009, +0.0351]

n = 10 has 80% power only for d >= 1.00. An effect of d = 0.61 is therefore
**underpowered, not refuted** -- the v5 design could not have detected it even
if it is real. A formal power analysis (`equivalence_v5.py`) gives:

    80% power at d=0.61  ->  n = 24
    90% power at d=0.61  ->  n = 31
    95% power at d=0.61  ->  n = 38

This replication fixes **n = 31** in advance and runs once.

The distinction that matters:

  * FORBIDDEN (optional stopping): add seeds, re-test, stop when p < 0.05.
  * LEGITIMATE (this): a contrast declared in advance came out underpowered;
    compute the required n from the observed effect size; pre-register a
    replication at that FIXED n; run it once; report whatever it shows.

To keep the replication INDEPENDENT of the pilot it replicates, it uses **fresh
seeds 100-130**, disjoint from v5's 0-9. Both the independent replication and
the pooled n = 41 estimate are reported. If the replication comes out null, the
pooled estimate is the final word and H19-DG is retired.

WHY THIS PARTICULAR CONTRAST
-----------------------------
It is the only one of the eight whose 90% CI does not contain zero, and it is
the ONE hypothesis in this project with independent published support:
Symes Thompson, Caron, Hicks & Mavroudis (arXiv:2410.17647) report that entity
attention outperforms permutation-invariant pooling "across fixed-size networks
of varying topologies" -- which is exactly regime D. Note this is the ENTITY
half of that paper's claim, over network hosts, not the history half over
attacker techniques; v5 tested the history half and found equivalence.

It was NOT selected for being the largest p-hacked effect: it is one of 8
pre-declared contrasts, its direction was predicted by prior published work
before any v5 data existed, and every one of the other 7 is reported unchanged.

WHAT IS HELD FIXED
------------------
Everything. The v5 environment (`profiles_v5`, cap_scale 0.35, goal_steps 3),
the frozen payoff, behaviour cloning on the transition oracle, BC_EPISODES=300,
BC_STEPS=2500, PRETRAIN_STEPS=1500, context 16, 200 evaluation episodes, and the
DeepSets/EntityTransformer capacity match. Only the seed count changes.
"""

from __future__ import annotations

import prereg_v5 as V5

# ── the two arms, unchanged from v5 ─────────────────────────────────────────
ARMS = [("GRU", "EntityTransformer"), ("GRU", "DeepSets")]

# Fresh, disjoint from v5's 0-9, so the replication is independent.
SEEDS = tuple(range(100, 131))          # n = 31, fixed in advance
N_PLANNED = 31
POWER_TARGET = 0.90
EFFECT_REPLICATED = 0.61                # observed paired d in v5

# ── inherited verbatim from v5 ──────────────────────────────────────────────
TRAINING = V5.TRAINING
BC_EPISODES = V5.BC_EPISODES
BC_STEPS = V5.BC_STEPS
PRETRAIN_STEPS = V5.PRETRAIN_STEPS
OBJECTIVE = V5.OBJECTIVE
MAX_SEQ_LEN = V5.MAX_SEQ_LEN
CAP_SCALE = V5.CAP_SCALE
GOAL_STEPS = V5.GOAL_STEPS
HPARAMS = V5.HPARAMS
EVAL_EPISODES = V5.EVAL_EPISODES
REGIMES = V5.REGIMES
REGIME_DESC = V5.REGIME_DESC
PRIMARY_METRIC = "dsr"
MECHANISM_METRIC = "alignment"
ALPHA = 0.05

# ── the single confirmatory hypothesis ──────────────────────────────────────
# ONE pre-declared contrast, so no multiplicity correction is required or
# applied. The three other regimes are reported as SECONDARY and are explicitly
# not part of the confirmatory test.
PRIMARY_CONTRAST = ("H19-DG-rep", ("GRU", "EntityTransformer"),
                    ("GRU", "DeepSets"), "D")
SECONDARY_REGIMES = ("A", "B", "C")

HYPOTHESES = [
    ("H19-DG-rep",
     "At unseen topology sizes, the EntityTransformer network encoder beats "
     "DeepSets on DSR, with the GRU history encoder held fixed "
     "(replication of v5 H19-DG at n=31, 90% power for d=0.61)", "dsr"),
]

TEST = "one-sided paired t-test on per-seed means (direction predicted in advance)"
CORRECTION = ("none required: ONE pre-declared confirmatory contrast. The three "
              "secondary regimes are reported but are not confirmatory and "
              "carry no claim.")
EFFECT_SIZE = "paired Cohen's d = mean(diff) / sd(diff)"
REPORT_ALSO = ("the independent n=31 replication AND the pooled n=41 estimate; "
               "the v5 result beside it; 95% CI on both; and the per-seed "
               "differences in full")

VALIDITY_GATE = {
    "rule": "both arms must beat the best_fixed baseline on regime D by a "
            "paired t-test over the 31 seeds, p < 0.05",
    "baseline_file": "results_v5/baselines_v5.json",
    "if_failed": "the contrast is reported but labelled VOID, exactly as in v5",
}

DECLARATION = (
    "Pre-registered before the replication ran, at a sample size FIXED in "
    "advance by a power analysis on the v5 effect size. Seeds are disjoint from "
    "v5's, so the replication is independent. The result is reported whatever "
    "it shows: if null, the pooled n=41 estimate is the final word and H19-DG "
    "is retired along with the rest of the architecture claim. No seed will be "
    "added after seeing the outcome, and no other contrast is re-tested. The "
    "seven other v5 contrasts stand exactly as reported."
)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("=" * 92)
    print("  TEMARL v6 — PRE-REGISTERED REPLICATION (single contrast)")
    print("=" * 92)
    print("  contrast   : %s" % PRIMARY_CONTRAST[0])
    print("               %s/%s  vs  %s/%s   regime %s"
          % (*PRIMARY_CONTRAST[1], *PRIMARY_CONTRAST[2], PRIMARY_CONTRAST[3]))
    print("  replicating: v5 H19-DG  delta +0.0180, d 0.61, p_raw 0.0862")
    print("  n          : %d (fixed in advance; %.0f%% power for d=%.2f)"
          % (N_PLANNED, 100 * POWER_TARGET, EFFECT_REPLICATED))
    print("  seeds      : %d-%d (disjoint from v5's 0-9)"
          % (SEEDS[0], SEEDS[-1]))
    print("  test       : %s" % TEST)
    print("  correction : %s" % CORRECTION)
    print("  training   : %s (unchanged)" % TRAINING)
    print("\n  %s" % DECLARATION)
    print("=" * 92)
