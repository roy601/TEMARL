# -*- coding: utf-8 -*-
"""
TEMARL v7-COMISET — PRE-REGISTRATION (the CAM-LDS v7 design, on COMISET Lab)
============================================================================
DRAFT until the COMISET learning gate has set ENV_STEPS; then committed BEFORE
any confirmatory COMISET run and never edited after a result is observed.

This is the pre-registered CAM-LDS study (temarl_marl/, commit 33782b1) run a
second time with ONLY the attacker replaced by one grounded in the COMISET Lab
corpus. Arms, learner, hyperparameters, gates and their thresholds, the
calibration grid and rule, the contrast families, the tests, the TOST margin
and the convergence flag are all IDENTICAL -- `verify_copy.py` proves the code
is the same apart from the declared files. COMISET is kept SEPARATE from the
CAM-LDS results: the two are reported side by side, never pooled.

FULL DISCLOSURE OF THE PATH THAT LED HERE
-----------------------------------------
1. The author asked (2026-09-19) to run "the same thing as CAM-LDS" on COMISET.
2. Measured BEFORE any COMISET gate or learned result: COMISET Lab is ONE host
   (desktop-4pvps6e) over 10 near-identical days, with no network and no
   lateral movement; 6,796 usable sessions, 19 techniques; median session
   length 3; Persistence ~60% of technique occurrences. It has no named attack
   playbooks and no geography, so both had to be fixed by rules
   (scripts_marl.py docstring): scripts = sessions grouped by terminal tactic
   (>= 30 sessions; 6 scripts, Collection dropped with 9 sessions); goal = the
   terminal tactic; entry = target = User zone (the host is a desktop);
   horizon = real session length capped at 61; the same v5 estimator.
3. Expectation stated in advance: the COMISET grounding is much weaker than
   CAM-LDS (invented geography, very short episodes, one dominant tactic). On
   2026-09-18 COMISET already failed the containment decision-headroom gate
   (+0.039 vs 0.05). Gates G3 (intent value) or G4 (sequence value) may fail
   here too; if so that is the reported result.
4. CALIBRATION and GATES: the same grid, rule and thresholds as CAM-LDS
   (results appended here after they run, before the learning gate).
5. LEARNING GATE: the same rule as CAM-LDS, on the Transformer-RoPE arm (the
   author's standing instruction for v7, disclosed there), seeds 900-902.

NO OUTCOME IS PRIVILEGED. Every declared contrast is reported, including nulls
and contradictions. A failing validity gate voids the contrasts it touches.
"""

from __future__ import annotations

PREREG_ID = "v7-comiset-draft"

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
# over the 6 leave-one-script-out folds (COMISET)
LOSO_CONTRASTS = [
    ("L1", T, ("GRU", "MAPPO"), +1),
    ("L2", T, ("NoHistory", "MAPPO"), +1),
    ("L3", T, ("SetEncoder", "MAPPO"), +1),
]
# If gate G4 (sequence value) failed, these are uninterpretable in advance:
UNINTERPRETABLE_IF_G4_FAILS = ("A1", "A2", "A3", "L1", "L3")

# CONVERGENCE FLAG (pre-registered with the Transformer-run learning gate).
# A trained cell (one per seed in the main study; one per seed and held-out
# script in LOSO) is POSSIBLY UNDER-TRAINED when its best validation dwell came
# at the FINAL evaluation and beat the previous evaluation by more than
# CONVERGENCE_RISE_REL. If more than half of an arm's cells are flagged, every
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
          "LOSO arms %d x 6 folds x %d seeds"
          % (PREREG_ID, ENV_STEPS, len(MAIN_ARMS), len(SEEDS), len(LOSO_ARMS),
             len(LOSO_SEEDS)))
    for tag, a, b, d in MAIN_CONTRASTS + LOSO_CONTRASTS:
        print("  %-3s %s/%s vs %s/%s (predicted %+d)" % (tag, *a, *b, d))
