# -*- coding: utf-8 -*-
"""PRE-REGISTRATION — COMISET Lab encoder comparison (v7).

COMMITTED BEFORE THE RUN. Nothing in this file may be edited once the run has
started; a changed hypothesis is a new pre-registration with a new commit.

-------------------------------------------------------------------------------
WHAT THIS EXPERIMENT IS, AND WHAT IT IS NOT
-------------------------------------------------------------------------------
IT IS: an architecture comparison for NEXT-TECHNIQUE PREDICTION on real attacker
behaviour from the COMISET Lab (Malicious Test Environment) corpus.

IT IS NOT: a deception-success (DSR) experiment. Measured beforehand and
disclosed: COMISET's campaign profiles yield headroom +0.0391, below the 0.05
validity gate used for the CAM-LDS environment, so COMISET cannot support a
decoy-type decision problem. DSR claims remain the CAM-LDS environment's job.
See GROUNDING.md.

-------------------------------------------------------------------------------
FULL DISCLOSURE OF WHAT PRECEDED THIS (so "how many things did you try?" has a
written answer)
-------------------------------------------------------------------------------
1. The shipped corpus (thesis_system/data/comiset_sessions.json) was found to
   contain 10 of the raw file's 53 techniques. Cause: the v1 extractor mapped
   through the 25-token v1 vocabulary and discarded the rest, including T1036
   (45.5% of all labelled records) and T1059.001 (24.2%).
2. The corpus was re-extracted with the 86-token union vocabulary plus MITRE
   revoked-by normalisation -> 6,796 usable sessions, 19 techniques, 8 tactics.
   THIS REPAIR WAS PERFORMED BEFORE ANY ARCHITECTURE WAS RUN ON THE CORPUS and
   is architecture-blind: no model influenced it.
3. Exploratory measurements on the repaired corpus, already taken: history
   information 0.688 bits, sequence value +0.1198, campaign headroom +0.0391.
   None of these involve a trainable architecture.
4. No encoder has been trained on the repaired corpus at the time of writing.

-------------------------------------------------------------------------------
HYPOTHESES
-------------------------------------------------------------------------------
The thesis claims attention suits attacker-technique sequences. On CAM-LDS that
claim was NOT supported (v5/v6: bounded within +-0.007 DSR). This tests the same
claim on real data and on the prediction task directly.

H1  Transformer-RoPE  >  GRU          on Top-1 next-technique accuracy
H2  Transformer-RoPE  >  LSTM         on Top-1
H3  Transformer-RoPE  >  SetEncoder   on Top-1   (does ORDER matter at all?)
H4  GRU               vs LSTM         on Top-1   (no direction predicted)

All tests two-sided, including H1-H3 where a direction is predicted. A one-sided
test would be the easier claim and this project has already retired one result
for optional-stopping reasons.

PRIMARY METRIC  : Top-1 accuracy on the held-out TEST split.
SECONDARY       : Top-3 accuracy, macro-F1, perplexity, encoder parameters,
                  wall-clock seconds. Reported for every arm, never substituted
                  for the primary if the primary disappoints.

-------------------------------------------------------------------------------
VALIDITY GATE (checked and reported FIRST; if it fails the comparison is VOID)
-------------------------------------------------------------------------------
G1  Every arm must beat the MAJORITY-CLASS baseline on test Top-1 (p < 0.05,
    paired across seeds). v1 reported Top-1 0.341 against a majority class of
    0.372 -- i.e. it lost to a constant predictor and did not notice.
G2  Every arm must beat the BIGRAM baseline (empirical P(next|prev) from train).
    An arm that cannot beat a lookup table has not learned sequence structure.
An arm failing G1 or G2 is reported as failed and excluded from H1-H4, which are
then reported over the remaining arms with the exclusion stated.

-------------------------------------------------------------------------------
DESIGN
-------------------------------------------------------------------------------
SEEDS        : 0..9 inclusive (n = 10), PAIRED across arms -- every arm sees the
               same split and the same initialisation seed.
SPLIT        : session-level 70/15/15 via data_real.session_split, re-drawn per
               seed. Never window-level: windows from one chain share a prefix.
BUDGET       : identical for every arm -- STEPS steps, BATCH batch, AdamW,
               LR with cosine decay. Model selection on VALIDATION Top-1 every
               EVAL_EVERY steps; the selected checkpoint is scored ONCE on test.
CAPACITY     : parameter counts are NOT equalised; they are REPORTED. Equalising
               would require changing width per arm, which is its own confound.
               The Transformer is expected to be the smallest, as in v5.

-------------------------------------------------------------------------------
STATISTICS
-------------------------------------------------------------------------------
Paired t-test across the 10 seeds per contrast; Holm-Bonferroni over the 4
contrasts; 95% CI and paired Cohen's d reported for every contrast whatever the
outcome. Additionally TOST equivalence at margin EQUIV_MARGIN Top-1, declared
here, so a null can be reported as bounded rather than merely undetected.

EVERY DECLARED CONTRAST WILL BE REPORTED, including those that contradict the
thesis hypothesis.
"""

CORPUS = "data_local/comiset_lab_sessions.json"

ARMS = ["Transformer-RoPE", "GRU", "LSTM", "SetEncoder"]

SEEDS = list(range(10))

STEPS = 3000
BATCH = 256
LR = 5e-4
WEIGHT_DECAY = 1e-4
EVAL_EVERY = 250
MAX_LEN = 16

SPLIT_FRAC = (0.70, 0.15, 0.15)

PRIMARY_METRIC = "top1"
SECONDARY_METRICS = ["top3", "macro_f1", "perplexity", "params", "seconds"]

CONTRASTS = [
    ("H1", "Transformer-RoPE", "GRU"),
    ("H2", "Transformer-RoPE", "LSTM"),
    ("H3", "Transformer-RoPE", "SetEncoder"),
    ("H4", "GRU", "LSTM"),
]

# The direction each hypothesis predicts for (first - second). Declared here so
# that a significant result in the OPPOSITE direction is reported as
# CONTRADICTED rather than quietly logged as "significant".
PREDICTED_DIRECTION = {"H1": +1, "H2": +1, "H3": +1, "H4": 0}

GATES = ["majority", "bigram"]

ALPHA = 0.05
EQUIV_MARGIN = 0.01          # Top-1 accuracy points, for TOST
