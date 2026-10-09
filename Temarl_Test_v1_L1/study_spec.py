# -*- coding: utf-8 -*-
"""
Temarl_Test_v1_L1 -- study specification, frozen before any confirmatory run
=============================================================================
Every arm, metric, comparison, correction family and decision rule is declared
HERE and committed BEFORE results exist. Nothing in this file may be edited
after the confirmatory run starts; a changed question requires a new folder.

Scope and honest framing
------------------------
This studies SOURCE-DERIVED ANNOTATED PLAYBOOK SEQUENCES in a simulator. It is
not real-world attacker telemetry and the simulator's engagement, movement and
exposure rules are modelling assumptions, not measured quantities. No result
here can establish real-world deception effectiveness.

What changed from the previous study
------------------------------------
1. Command-level multi-label prediction replaces flattened single-label
   prediction, removing the 34.9% within-command label-order artefact.
2. The Markov generator is GONE: no chain fitting, no smoothing, no synthetic
   sequences, no generated episodes. Attackers are replayed recordings only.
3. Window length (8/16/32/64) and early-stopping patience (16/32/64 checks)
   are explicitly tested rather than inherited.
4. An order-free control is included, so "sequence matters" can be
   distinguished from "history matters" -- a question the previous study
   could not answer because the control was dropped.
"""

from __future__ import annotations

# ── prediction study ───────────────────────────────────────────────────────
ENCODERS = ("Transformer", "GRU", "LSTM")          # the sequence arms
ORDER_FREE = "OrderFree"                            # order-free control
NO_HISTORY = "NoHistory"                            # no-history control
PREDICTION_ARMS = ENCODERS + (ORDER_FREE,)          # trained at every window
WINDOWS = (8, 16, 32, 64)
PILOT_SEEDS = (101, 102, 103)
MAIN_SEEDS = tuple(range(10))
SAMPLERS = ("ordinary", "overlap")        # overlap is an ablation at W=16 only
REFERENCE_WINDOW = 16

PILOT_CELLS = len(PREDICTION_ARMS) * len(WINDOWS) * len(PILOT_SEEDS)        # 48
OVERLAP_PILOT_CELLS = len(ENCODERS) * len(PILOT_SEEDS)                      # 9
MAIN_PREDICTION_CELLS = len(PREDICTION_ARMS) * len(WINDOWS) * len(MAIN_SEEDS)  # 160
NOHISTORY_PREDICTION_CELLS = len(MAIN_SEEDS)        # reference window only: h=0
                                                    # is identical at every W
OVERLAP_MAIN_CELLS = len(ENCODERS) * len(MAIN_SEEDS)                        # 30

PRIMARY_PREDICTION_METRIC = "micro_f1"
SECONDARY_PREDICTION_METRICS = ("bce", "macro_f1", "exact_set_accuracy",
                                "precision_at_1", "recall_at_3", "recall_at_5")
THRESHOLD_GRID = (0.1, 0.2, 0.3, 0.4, 0.5)
THRESHOLD_RULE = ("maximise validation micro-F1; ties take the SMALLEST "
                  "threshold. Selected on validation only, never on test.")
CHECKPOINT_RULE = ("validation-best is PRIMARY; the final checkpoint is "
                   "reported as secondary. Test never selects anything.")

# ── training protocol (ours, not published optima) ─────────────────────────
BATCH_SIZE = 32
LEARNING_RATE = 5e-4
WEIGHT_DECAY = 0.01
VAL_EVERY_UPDATES = 64
MIN_DELTA = 1e-4
PATIENCE_GRID = (16, 32, 64)              # validation checks -> 1024/2048/4096 updates
PATIENCE_TOLERANCE = 1e-3
BUDGET_FACTOR = 1.25
PILOT_MIN_UPDATES = 8192
PILOT_EPOCH_EQUIVALENTS = 300
PILOT_DOUBLING_ALLOWED = 1                # one predeclared doubling, then stop

PATIENCE_RULE = ("smallest patience whose mean validation BCE is within "
                 f"{PATIENCE_TOLERANCE} of the best, pilot configurations "
                 "weighted equally")
BUDGET_RULE = (f"ceil({BUDGET_FACTOR} x max configuration-wise median "
               f"validation-best update / {VAL_EVERY_UPDATES}) x "
               f"{VAL_EVERY_UPDATES}. A budget heuristic, not a convergence proof.")

# ── deception study ────────────────────────────────────────────────────────
LEARNERS = ("IPPO", "MAPPO")
RL_ARMS = tuple((e, l) for l in LEARNERS for e in ENCODERS)      # 6
RL_CONTROLS = tuple((c, l) for l in LEARNERS
                    for c in (ORDER_FREE, NO_HISTORY))           # 4
RL_SEEDS = tuple(range(10))
RL_ENV_STEPS = 2_000_000
RL_VAL_REPEATS = 10
RL_TEST_REPEATS = 50
RL_PRIMARY_METRIC = "dwell"
RL_SECONDARY_METRICS = ("depth", "protected")
RL_GUARD_METRICS = ("exposed", "lure_chains", "dead_ends",
                    "capacity_violations", "length", "decoys_deployed")
RL_SELECTION = "highest mean validation dwell; test never selects."

MAIN_RL_CELLS = (len(RL_ARMS) + len(RL_CONTROLS)) * len(RL_SEEDS)        # 100
CONTEXT_RL_CELLS = len(RL_ARMS) * len(RL_SEEDS)                          # 60

CONTEXT_WINDOW_RULE = (
    "ONE longer window (32 or 64) is preselected on POOLED VALIDATION "
    "prediction performance, before any RL run at that window. All six "
    "encoder-learner combinations are then retrained there -- not only the "
    "architecture that happens to lead.")

AGGREGATION_PRIMARY = "max"
AGGREGATION_SENSITIVITY = "mean"
AGGREGATION_NOTE = ("Set-based engagement: max compatibility is primary, mean "
                    "is a SEPARATELY TRAINED sensitivity condition. Neither is "
                    "a measured real-world engagement probability.")

# ── baselines ──────────────────────────────────────────────────────────────
BASELINES = ("null", "static_best", "random", "best_fixed", "reactive",
             "clairvoyant_local", "clairvoyant_coord")
BASELINE_NOTE = ("Tunable baselines (best_fixed, static_best) are fitted on "
                 "VALIDATION. Clairvoyant rungs read future state and are "
                 "measuring instruments for the ladder, never comparison arms. "
                 "All baselines obey the same capacity rule as the policies.")

# ── statistics ─────────────────────────────────────────────────────────────
CORRECTION = "holm"
ALPHA = 0.05
TEST = "two-sided paired t-test across matched training seeds"

PREDICTION_FAMILY = (
    "All encoder-vs-encoder contrasts at the reference window, all "
    "window-vs-reference contrasts within each encoder, and the overlap-vs-"
    "ordinary contrast. Corrected together.")
RL_FAMILY = (
    "All encoder-vs-encoder, MAPPO-vs-IPPO, encoder-vs-NoHistory and "
    "context-window contrasts on dwell, depth and protection. Corrected "
    "together, separately from the prediction family.")

EQUIVALENCE_NOTE = (
    "Non-significance is NOT equivalence. An equivalence claim requires a "
    "predeclared margin and a TOST; absent that, report 'no clear difference "
    "detected'.")
INDEPENDENCE_NOTE = (
    "Seeds, environment repeats and prediction windows are NOT independent "
    "attack campaigns. The corpus contains 36 playbooks from 7 scenarios; "
    "that is the real sample size for any generalisation claim.")

# ── declared hypotheses ────────────────────────────────────────────────────
HYPOTHESES = {
    "H1_history": "Encoder arms beat NoHistory on dwell. (Replication: the "
                  "previous study found ~+33% under flattened labels.)",
    "H2_order": "Sequence encoders differ from the OrderFree control, which "
                "sees WHICH commands occurred but not their order. If null, "
                "the finding is 'history matters, order does not detectably' "
                "-- a legitimate outcome, and the question the previous study "
                "could not answer because this control was dropped.",
    "H3_architecture": "No prediction given. Previous studies found no clear "
                       "difference; two-sided and direction-aware.",
    "H4_window": "No prediction given. Longer windows may or may not help; "
                 "a prediction gain need not transfer to deception.",
    "H5_learner": "No prediction given for MAPPO vs IPPO.",
    "H6_patience": "No prediction given; the patience study selects a shared "
                   "budget, it does not test a hypothesis.",
    "H7_overlap": "No prediction given. Overlap repeats windows within the "
                  "same update budget; it adds optimisation, not information.",
}

NEGATIVE_RESULTS_NOTE = (
    "Null and negative results are valid outcomes and are reported in full, "
    "whatever their direction.")
