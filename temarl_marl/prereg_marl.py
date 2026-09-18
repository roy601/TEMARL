# -*- coding: utf-8 -*-
"""
TEMARL v7 — PRE-REGISTRATION (genuinely multi-agent, proposal-faithful)
=======================================================================
Written and committed BEFORE the confirmatory runs. Nothing here may be edited
once any confirmatory result has been observed. A change of design is a new
pre-registration in a new commit, and the change is disclosed.

WHY v7 EXISTS (full disclosure of the path that led here)
---------------------------------------------------------
1. An audit of v5 (2026-09-18) found that the system was a multi-agent
   ENVIRONMENT but not multi-agent RL:
     - the reported v5 policy is behaviour cloning on a privileged oracle,
       because PPO never beat the memoryless baseline (results_v5/ppo_ab.log);
     - reward, capture and progress depended only on the responsible agent's
       action (env_entity.py:237-246), so the team problem decomposed into
       independent single-agent problems: there was nothing to coordinate;
     - the teacher gave all four agents the same label; there was no mixer,
       no communication and no credit assignment;
     - the BC loss never trained the decoy-target (pointer) head, so in the
       multi-zone-per-agent regimes C/D placement came from an untrained head.
   The proposal promised multi-agent reinforcement learning, so v7 builds it.
2. The proposal's primary metrics are dwell time, interaction depth and
   generalisation to an unseen attack script. In the containment design dwell
   time was measured to fall as the defence improved (null policy 21.7 steps,
   clairvoyant 14.0), because capture ended the episode. v7 therefore models
   ENGAGEMENT: a deceived attacker keeps interacting with decoys.
3. Environment grounding decisions made while building v7, BEFORE any learned
   result existed (scripts_marl.py docstring): chains estimated by the
   unchanged v5 estimator from the 36 source-verified AttackBed runs; S4's
   Firewall target mapped to its entry zone; S6's unobservable Exfiltration
   goal replaced by its ATT&CK prerequisite Collection; episode horizon = a
   real run length of the script; objective = first goal-tactic technique on a
   real host in the target zone (G = 1).
4. CALIBRATION (calibrate_marl.py, rule fixed in source first): 8 cells of
   beta x p_goal x p_stay, scored only by the architecture-free gates G1-G4.
   3 of 8 passed; the rule chose the passing cell with the smallest
   coordination value: beta 0.2, p_goal 0.7, p_stay 0.8. That cell's intent
   value (G3) was 10.1% of the ceiling against a 10% threshold -- a marginal
   pass, disclosed here. The final gates were re-run on a disjoint stream
   (results_marl/gates.json).
5. LEARNING GATE (learning_gate_marl.py, seeds 900-902): chose the training
   budget ENV_STEPS below. DISCLOSURE: the approved plan ran it on the GRU so
   the budget could not suit the arm under test; before it ran, the author
   directed that it run on the Transformer-RoPE arm instead. So the budget is
   the smallest at which the TRANSFORMER team works, applied unchanged to every
   arm. Because other arms could be under-trained at a Transformer-sized
   budget, the CONVERGENCE flag below was pre-registered at the same time.
   GRU and LSTM were not trained before this file was committed.
6. Expectation stated in advance, so it cannot be rewritten afterwards: making
   the system multi-agent is not expected to make the Transformer win. On
   COMISET the GRU beat it at next-technique prediction with no RL involved.
   All tests are two-sided; the verdicts are direction-aware.

NO OUTCOME IS PRIVILEGED. Every declared contrast is reported, including nulls
and contradictions. A failing validity gate voids the contrasts it touches.
"""

from __future__ import annotations

PREREG_ID = "v7-draft"

# ── arms ─────────────────────────────────────────────────────────────────────
# (history encoder, learner). Capacity-matched encoders (encoders_marl.py).
MAIN_ARMS = [("Transformer-RoPE", "MAPPO"), ("GRU", "MAPPO"), ("LSTM", "MAPPO"),
             ("SetEncoder", "MAPPO"), ("NoHistory", "MAPPO"),
             ("Transformer-RoPE", "IPPO")]
LOSO_ARMS = ("Transformer-RoPE", "GRU", "SetEncoder", "NoHistory")

SEEDS = tuple(range(10))
LOSO_SEEDS = tuple(range(5))

# ── budget (set by the learning gate before this file is committed) ─────────
ENV_STEPS = None
SMOKE_ENV_STEPS = 8192
N_TEST = 500

# ── metrics and tests ───────────────────────────────────────────────────────
PRIMARY = ("dwell", "depth")        # proposal metrics 1 and 2
ALPHA = 0.05
TEST = "paired t-test on per-seed means, two-sided"
CORRECTION = "Holm-Bonferroni within each family"
TOST_REL = 0.05                     # equivalence margin = 5% of the ceiling

VALIDITY_GATE = ("every learned arm must beat BOTH the best fixed joint action "
                 "and the better uncoordinated reactive baseline on dwell, "
                 "paired t-test over seeds, p < 0.05; contrasts touching a "
                 "failing arm are reported but VOID")

T = ("Transformer-RoPE", "MAPPO")
# (tag, arm a, arm b, predicted sign of a - b); each is tested on dwell AND depth
MAIN_CONTRASTS = [
    ("M1", T, ("Transformer-RoPE", "IPPO"), +1),    # centralised training matters
    ("I1", T, ("NoHistory", "MAPPO"), +1),          # the shared intent channel matters
    ("A1", T, ("GRU", "MAPPO"), +1),                # attention vs recurrence
    ("A2", T, ("LSTM", "MAPPO"), +1),
    ("A3", T, ("SetEncoder", "MAPPO"), +1),         # order matters
]
# proposal metric 3: performance on the held-out script, per seed averaged
# over the 7 leave-one-script-out folds
LOSO_CONTRASTS = [
    ("L1", T, ("GRU", "MAPPO"), +1),
    ("L2", T, ("NoHistory", "MAPPO"), +1),
    ("L3", T, ("SetEncoder", "MAPPO"), +1),
]
# If gate G4 (sequence value) failed, these are uninterpretable in advance:
UNINTERPRETABLE_IF_G4_FAILS = ("A1", "A2", "A3", "L1", "L3")

# CONVERGENCE FLAG (pre-registered with the Transformer-run learning gate).
# An arm-seed is POSSIBLY UNDER-TRAINED when its best validation dwell came at
# the FINAL evaluation and beat the previous evaluation by more than
# CONVERGENCE_RISE_REL. If more than half of an arm's seeds are flagged, every
# contrast touching that arm is labelled BUDGET-LIMITED: reported in full, but
# not interpreted as an architecture difference.
CONVERGENCE_RISE_REL = 0.05

EXPLORATORY = ("cross-play between seeds (evidence of learned conventions); "
               "reliance on h (dwell with h := 0); per-script breakdown; "
               "calibration-grid sensitivity. Labelled exploratory wherever "
               "reported.")


def _check():
    if ENV_STEPS is None:
        raise RuntimeError("prereg_marl.ENV_STEPS is not set: run the learning "
                           "gate first, then set it and commit this file")


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("prereg %s | budget %s env-steps | main arms %d x %d seeds | "
          "LOSO arms %d x 7 folds x %d seeds"
          % (PREREG_ID, ENV_STEPS, len(MAIN_ARMS), len(SEEDS), len(LOSO_ARMS),
             len(LOSO_SEEDS)))
    for tag, a, b, d in MAIN_CONTRASTS + LOSO_CONTRASTS:
        print("  %-3s %s/%s vs %s/%s (predicted %+d)" % (tag, *a, *b, d))
