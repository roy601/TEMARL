# -*- coding: utf-8 -*-
"""
TEMARL v4 — PRE-REGISTRATION (final experiment)
================================================
Written and committed BEFORE any v4 training run, after Phase 2 and before any
v4 result exists. Nothing here may be edited once results are observed.

WHY THERE IS A v4 AT ALL
------------------------
The v3 experiment (10 seeds, Holm-corrected) found the history Transformer no
better than the GRU on DSR, and the CAM-LDS encoder test found the GRU AHEAD by
+0.1388 (d = 1.65, p_holm = 5.7e-14). Phase 2 established that both numbers were
measured on a Transformer that was handicapped by our own configuration:

  2.5  absolute sinusoidal positional encoding cost 2.6-7.0 Top-1 points vs
       rotary, with the penalty growing with context length
  2.4  hyperparameters had never been tuned; with an equal 16-trial budget the
       CAM-LDS gap closed from -0.1388 to +0.0000
  2.6  the pretraining objective was misaligned: training on the OPTIMAL-ACTION
       target instead of next-technique raised action-decodability from 0.867 to
       0.934 for the Transformer and 0.844 to 0.921 for the GRU

Two candidate explanations were REFUTED and are not revisited: data scale (2.1,
the gap widens with data, slope -0.0187/decade) and context length (2.2, longer
context is worse for every architecture; L = 8 is best).

So v4 asks the question v3 could not: **with the artefact-corrected encoder,
does attention beat recurrence on the deception objective?**

WHAT IS HELD FIXED (so this is a controlled comparison, not a new pipeline)
--------------------------------------------------------------------------
  * environment      : the v3 entity environment, unchanged, still passing exact
                       equivalence with env_v2 (0 mismatches / 1,126 steps)
  * network encoder  : DeepSets, held FIXED. v3 found no EntityTransformer
                       benefit (H6/H7 null); varying it again would confound the
                       history-encoder question this experiment exists to answer.
  * payoff           : payoff_frozen.json, never refitted
  * reward, capture, termination, vocabulary : unchanged
  * context length   : 8 (Phase 2.2)
  * hyperparameters  : per-architecture, from the Phase 2.4 equal-budget search

NO OUTCOME IS PRIVILEGED. If the corrected Transformer still fails to beat the
GRU on DSR, that is the result, and the architecture claim is retired. Phase 2
has already shown the earlier evidence against it was partly our own artefact;
that does not entitle us to the converse.
"""

from __future__ import annotations

# ── factors ──────────────────────────────────────────────────────────────────
HISTORY_ENCODERS = ("Transformer-RoPE", "Transformer-Sin", "GRU")
OBJECTIVES = ("action", "next")
ARMS = [(h, o) for h in HISTORY_ENCODERS for o in OBJECTIVES]

NETWORK_ENCODER = "DeepSets"        # held FIXED (v3 H6/H7 null)
MAX_SEQ_LEN = 8                     # Phase 2.2
N_AGENTS = 4
MAX_ENTITIES = 48

# Best configuration per architecture from the Phase 2.4 equal-budget search on
# CAM-LDS (selected on validation, scored on held-out test). Copied verbatim; not
# re-tuned for this experiment.
HPARAMS = {
    "Transformer-RoPE": {"n_layers": 4, "n_heads": 8, "d_ff": 512,
                         "d_model": 32, "lr": 1e-3},
    "Transformer-Sin": {"n_layers": 3, "n_heads": 8, "d_ff": 256,
                        "d_model": 64, "lr": 1e-3},
    "GRU": {"hidden": 256, "n_layers": 1, "d_model": 128, "lr": 3e-4},
}

# ── metrics ──────────────────────────────────────────────────────────────────
PRIMARY_METRIC = "dsr"              # Deception Success Rate
MECHANISM_METRIC = "alignment"      # explains HOW a DSR difference arises
SECONDARY_METRICS = ("episode_return", "engagement_length", "capture_rate")
ALPHA = 0.05

# ── regimes (identical topology sets to v3, so v3 and v4 are comparable) ────
REGIMES = ("A", "B", "C", "D")
REGIME_DESC = {
    "A": "canonical 5-zone control (identical to env_v2)",
    "B": "new topologies, TRAINED sizes",
    "C": "unseen structure (different firewall density)",
    "D": "unseen sizes (9/11/13 zones)",
}

# ── budget ───────────────────────────────────────────────────────────────────
SEEDS = tuple(range(10))
TRAIN_EPISODES = 600
EVAL_EPISODES = 200
PRETRAIN_STEPS = 1500      # Phase 2 showed 800 steps can INVERT a ranking
MAX_STEPS = 40

# ── hypotheses ───────────────────────────────────────────────────────────────
HYPOTHESES = [
    ("H9", "Artefact-corrected Transformer (RoPE + action objective) beats the "
           "GRU on DSR at trained topology sizes", "dsr"),
    ("H10", "The same holds on unseen topology sizes", "dsr"),
    ("H11", "The aligned ACTION pretraining objective beats next-technique "
            "pretraining on DSR, for BOTH architectures", "dsr"),
    ("H12", "Rotary position beats absolute sinusoidal position on DSR "
            "(quantifies the Phase 2.5 artefact at the deception objective)", "dsr"),
]

# ── statistics ───────────────────────────────────────────────────────────────
TEST = "paired t-test on per-seed means"
CORRECTION = "Holm-Bonferroni over the declared contrast family, alpha=0.05"
EFFECT_SIZE = "paired Cohen's d = mean(diff) / sd(diff)"
REPORT_ALSO = ("95% CI on every contrast, because n=10 detects only d>=1.00; "
               "a CI that bounds the effect carries the argument, not the p-value")

# (label, arm_a, arm_b, regime) -- exactly these, fixed in advance
CONTRAST_FAMILY = [
    ("H9-B", ("Transformer-RoPE", "action"), ("GRU", "action"), "B"),
    ("H9-A", ("Transformer-RoPE", "action"), ("GRU", "action"), "A"),
    ("H10-D", ("Transformer-RoPE", "action"), ("GRU", "action"), "D"),
    ("H10-C", ("Transformer-RoPE", "action"), ("GRU", "action"), "C"),
    ("H11-T", ("Transformer-RoPE", "action"), ("Transformer-RoPE", "next"), "B"),
    ("H11-G", ("GRU", "action"), ("GRU", "next"), "B"),
    ("H12-B", ("Transformer-RoPE", "action"), ("Transformer-Sin", "action"), "B"),
    ("H12-D", ("Transformer-RoPE", "action"), ("Transformer-Sin", "action"), "D"),
]

# ── gates that must still pass ───────────────────────────────────────────────
INHERITED_GATES = {
    "vocab_unk_camlds": 0,
    "payoff_headroom_min": 0.15,
    "env_v2_equivalence_mismatches": 0,
    "payoff_rows_0_77_bit_identical": True,
}

DECLARATION = (
    "Pre-registered before any v4 training run. Hypotheses, primary metric, "
    "arms, seeds, contrast family, correction and hyperparameters are fixed here "
    "and are not to be modified after observing results. Every declared contrast "
    "is reported whatever its outcome. A null or negative result is valid and "
    "will be reported as such -- Phase 2 showed the prior evidence AGAINST the "
    "Transformer was partly our own artefact, which does not entitle us to "
    "assume the converse."
)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("=" * 92)
    print("  TEMARL v4 — PRE-REGISTRATION (final experiment)")
    print("=" * 92)
    print("  primary metric   : %s" % PRIMARY_METRIC)
    print("  history encoders : %s" % list(HISTORY_ENCODERS))
    print("  objectives       : %s" % list(OBJECTIVES))
    print("  arms             : %d  x %d seeds = %d runs"
          % (len(ARMS), len(SEEDS), len(ARMS) * len(SEEDS)))
    print("  network encoder  : %s (HELD FIXED)" % NETWORK_ENCODER)
    print("  context length   : %d   pretrain steps: %d"
          % (MAX_SEQ_LEN, PRETRAIN_STEPS))
    print("  test / correction: %s / %s" % (TEST, CORRECTION))
    print("\n  hypotheses:")
    for k, d, m in HYPOTHESES:
        print("    %-4s %s  [%s]" % (k, d, m))
    print("\n  contrast family (%d declared):" % len(CONTRAST_FAMILY))
    for lab, a, b, r in CONTRAST_FAMILY:
        print("    %-8s %-34s vs %-30s regime %s"
              % (lab, "%s/%s" % a, "%s/%s" % b, r))
    print("\n  hyperparameters (from Phase 2.4, copied verbatim):")
    for k, v in HPARAMS.items():
        print("    %-18s %s" % (k, v))
    print("\n  %s" % DECLARATION)
    print("=" * 92)
