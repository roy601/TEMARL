# -*- coding: utf-8 -*-
"""
TEMARL v3 — PRE-REGISTRATION
=============================
Written and committed BEFORE any v3 training run. Nothing in this file may be
edited after results are observed. It fixes the hypotheses, the primary metric,
the topology splits, the seed lists, and the statistical procedure.

This mirrors the discipline already used in `evaluate_v2.py`, where the
hypothesis family is declared in source rather than chosen after the fact.

THE TWO FACTORS ARE INDEPENDENT
-------------------------------
    NETWORK encoder  : EntityTransformer | DeepSets      <- H6, H7 test THIS
    HISTORY encoder  : Transformer | GRU | SetEncoder    <- H8 re-tests this
                                                            under variable topology

A prior CAM-LDS result (45 matched pairs, Holm-corrected) found the HISTORY GRU
beat the HISTORY Transformer by +0.1388 Top-1, d = 1.65, p_holm = 5.7e-14. That
says nothing about the NETWORK encoder, which encodes a different object. H6/H7
are therefore genuinely open, and H8 asks only whether the history result
survives a change of environment regime.

NO OUTCOME IS PRIVILEGED. If DeepSets matches or beats the Entity Transformer,
that is the reported result and the architectural claim is retired.
"""

from __future__ import annotations

# ── factors ──────────────────────────────────────────────────────────────────
NETWORK_ENCODERS = ("EntityTransformer", "DeepSets")
HISTORY_ENCODERS = ("Transformer", "GRU", "SetEncoder")
ARMS = [(n, h) for n in NETWORK_ENCODERS for h in HISTORY_ENCODERS]

# ── metrics ──────────────────────────────────────────────────────────────────
PRIMARY_METRIC = "dsr"              # Deception Success Rate: the thesis's headline
MECHANISM_METRIC = "alignment"      # why DSR moves, not a second headline
SECONDARY_METRICS = ("episode_return", "engagement_length", "capture_rate")
ALPHA = 0.05

# ── topology splits (disjoint by construction; seeds never overlap) ─────────
# Regime A: the frozen 5-zone control, identical to env_v2.
# Regime B: NEW topologies at a size the model trained on.
# Regime C: NEW structures at trained sizes, generated with a different
#           firewall-density parameter so the wiring distribution differs.
# Regime D: sizes never seen in training.
TRAIN_ZONE_SIZES = (5, 6, 7)
TRAIN_TOPOLOGY_SEEDS = tuple(range(0, 24))          # 8 per trained size
REGIME_B_SEEDS = tuple(range(100, 112))             # unseen seeds, trained sizes
REGIME_C_SEEDS = tuple(range(200, 212))             # unseen structure
REGIME_C_FIREWALL_P = 0.45                          # vs 0.15 in training
UNSEEN_ZONE_SIZES = (9, 11, 13)                     # regime D
REGIME_D_SEEDS = tuple(range(300, 312))

N_AGENTS = 4                        # fixed: QMIX mixes a constant agent count
MAX_ENTITIES = 48
TRAIN_FIREWALL_P = 0.15

# ── experiment budget ────────────────────────────────────────────────────────
SEEDS = tuple(range(10))            # 10 paired model seeds
TRAIN_EPISODES = 600
EVAL_EPISODES = 200
MAX_STEPS = 40

# ── hypotheses ───────────────────────────────────────────────────────────────
HYPOTHESES = [
    ("H6", "EntityTransformer > DeepSets on regime B "
           "(new topologies, TRAINED sizes)", "dsr"),
    ("H7", "EntityTransformer > DeepSets on regimes C and D "
           "(unseen structure, unseen sizes)", "dsr"),
    ("H8", "History GRU >= History Transformer under variable topology "
           "(does the CAM-LDS finding survive the regime change?)", "dsr"),
]

# ── statistics ───────────────────────────────────────────────────────────────
# Paired by model seed: every arm sees the IDENTICAL topology set and the
# IDENTICAL evaluation seeds, so a paired test is the correct instrument.
TEST = "paired t-test on per-seed means"
CORRECTION = "Holm-Bonferroni over the declared contrast family, alpha=0.05"
EFFECT_SIZE = "paired Cohen's d = mean(diff) / sd(diff)"
CONTRAST_FAMILY = [
    # (label, arm_a, arm_b, regime)  -- exactly these, fixed in advance
    ("H6-Transformer", ("EntityTransformer", "Transformer"),
     ("DeepSets", "Transformer"), "B"),
    ("H6-GRU", ("EntityTransformer", "GRU"), ("DeepSets", "GRU"), "B"),
    ("H6-SetEncoder", ("EntityTransformer", "SetEncoder"),
     ("DeepSets", "SetEncoder"), "B"),
    ("H7-C-GRU", ("EntityTransformer", "GRU"), ("DeepSets", "GRU"), "C"),
    ("H7-D-GRU", ("EntityTransformer", "GRU"), ("DeepSets", "GRU"), "D"),
    ("H8-hist-B", ("EntityTransformer", "GRU"),
     ("EntityTransformer", "Transformer"), "B"),
    ("H8-hist-D", ("EntityTransformer", "GRU"),
     ("EntityTransformer", "Transformer"), "D"),
]

# ── gates that must still pass after every v3 change ────────────────────────
INHERITED_GATES = {
    "vocab_unk_camlds": 0,
    "vocab_unk_comiset": 0,
    "payoff_headroom_min": 0.15,
    "env_v2_equivalence_mismatches": 0,
    "entity_padding_invariance_max": 1e-5,
    "entity_permutation_invariance_max": 1e-5,
    "capacity_spread_max": 0.10,
}

DECLARATION = (
    "Pre-registered before any v3 training run. Hypotheses, metric, splits, "
    "seeds, contrast family and correction are fixed here and are not to be "
    "modified after observing results. A null or negative outcome is a valid "
    "result and will be reported as such."
)


def topology_spec():
    """The exact topology sets each regime uses. Deterministic from this file."""
    return {
        "train": {"sizes": TRAIN_ZONE_SIZES, "seeds": TRAIN_TOPOLOGY_SEEDS,
                  "p_firewall_block": TRAIN_FIREWALL_P},
        "A": {"canonical": True},
        "B": {"sizes": TRAIN_ZONE_SIZES, "seeds": REGIME_B_SEEDS,
              "p_firewall_block": TRAIN_FIREWALL_P},
        "C": {"sizes": TRAIN_ZONE_SIZES, "seeds": REGIME_C_SEEDS,
              "p_firewall_block": REGIME_C_FIREWALL_P},
        "D": {"sizes": UNSEEN_ZONE_SIZES, "seeds": REGIME_D_SEEDS,
              "p_firewall_block": TRAIN_FIREWALL_P},
    }


if __name__ == "__main__":
    import json
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("=" * 86)
    print("  TEMARL v3 — PRE-REGISTRATION")
    print("=" * 86)
    print(f"  primary metric : {PRIMARY_METRIC}")
    print(f"  arms           : {len(ARMS)}  {ARMS}")
    print(f"  model seeds    : {len(SEEDS)}")
    print(f"  test           : {TEST}")
    print(f"  correction     : {CORRECTION}")
    print(f"\n  hypotheses:")
    for k, d, m in HYPOTHESES:
        print(f"    {k}: {d}  [{m}]")
    print(f"\n  contrast family ({len(CONTRAST_FAMILY)} declared):")
    for lab, a, b, r in CONTRAST_FAMILY:
        print(f"    {lab:<16} {a} vs {b}  regime {r}")
    print(f"\n  topology spec: {json.dumps(topology_spec(), default=list)[:300]}...")
    print(f"\n  {DECLARATION}")
    print("=" * 86)
