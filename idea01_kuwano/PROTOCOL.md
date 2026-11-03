# Idea 01 protocol: comparison of TEMARL's prediction module with an adapted Kuwano baseline

**Status: FROZEN as protocol 1.0 on 2026-11-03 (from draft v0.3, approved). Constants in
`idea01_kuwano/spec.py`; `python idea01_kuwano/spec.py` re-checks every measured fact.
Nothing had been run on test data when it was frozen.**

- v0.1 (2026-11-02): first draft.
- v0.2 (2026-11-03): decisions Q1–Q4 recorded.
- v0.3 (2026-11-03): revised after review. Task alignment specified and measured
  (Section 4); the similarity-1 rule implemented and tested; the training count
  explained; the exclusions and their consequences documented.

On approval, the constants are frozen in `idea01_kuwano/spec.py` and committed, together
with the code, **before any test result is examined**. Changing anything after that means a
new version and a new commit, never an edit in place.

---

## 1. The claim

> On the CAM-LDS next-step technique-prediction task, under the frozen split protocol
> v1.0 (with the exclusion in Section 2), the micro-F1 of **TEMARL's prediction module**
> is higher than / equal to / lower than that of **an adapted Kuwano et al. (2023)
> baseline**. Both are evaluated on identical prediction points, identical targets, the same
> label space and the same metric code.

**What this does not claim:**

- **Nothing about MAPPO coordination or deception.** Those need separate experiments.
- **Not a reproduction of Kuwano's own numbers.** That was done separately, in `kuwano_repro/`.
- **Not generalisation to unseen campaigns.** The primary family tests new variants of known
  campaigns (Section 2.1). Only the scenario-held-out family bears on unseen campaigns, and
  it has 3 folds.
- **Not equivalence.** A non-significant difference is reported as "no significant
  difference", never as "equal".

---

## 2. Inherited from the frozen split protocol v1.0

`camlds_real/split_spec.py`, frozen 2026-10-24, is not edited. Inherited unchanged:

| Item | Value |
|---|---|
| Corpus | `camlds_real/out/steps.jsonl`: 904 steps, 34 runs, 7 scenarios, 870 prediction points |
| Order | ascending `start` timestamp within a run |
| Label space | 81 parent techniques |
| Validation | first run, in sorted order, of each training scenario with ≥ 2 runs |
| Repeats | kept (main); collapsed as a separate sensitivity condition |
| Window | W = 16, left-padded, never crossing a run boundary |
| Reporting | R1–R6, including the unseen-label ceiling beside every scenario-held-out number |

**One exclusion, declared here (decision Q2).** Folds `2_cron` and `2_rootkit` are removed
from the variant-held-out family, for every model alike:

- **Why.** S2 has only 2 runs. Holding one out leaves a single training run, and the
  validation rule takes one run from each training scenario *with at least 2 runs*, so the
  validation set is empty. Neither model could then select a threshold, and ours could not
  select a checkpoint or stop early. These folds cannot support the validation protocol.
- **What it costs.** The variant family no longer covers S2. **S2 is still evaluated**, as a
  held-out scenario in the scenario-held-out family.

| Family | Folds | Test steps | Prediction points | Claim it supports |
|---|---|---|---|---|
| **Variant held out (primary)** | **29**: S1 × 18, S3 × 6, S6 × 5 | 819 | 790 | performance on a new variant of a known campaign |
| Scenario held out (secondary) | 3: S2, S3, S6 | 344 | 331 | performance on an unseen campaign |

### 2.1 What the primary family can and cannot show

The 29 folds are **29 held-out runs from 3 scenarios**. Their variants are highly similar:
within-scenario technique-set Jaccard is 0.858 for S1, against 0.110 across scenarios
(frozen protocol, CLAIMS). This is a legitimate question, and not leakage (0 of 153 S1
variant pairs are order-identical). But **it supports no claim of generalisation to unseen
scenarios**, and every primary result is labelled accordingly.

---

## 3. The models

### 3.1 TEMARL's prediction module

The proposed framework is CTDE multi-agent RL: MAPPO with a centralised critic and
decentralised, parameter-shared actors (`Temarl_Test_v1_L1/mappo_cmd.py`). Each actor
receives a history embedding h from a **command-level sequence encoder**. That encoder is
trained on its own, with binary cross-entropy, to predict the next step's technique set,
and is then **frozen** inside MAPPO (`requires_grad_(False)` and `eval()`, asserted in the
tests).

- **The framework's technique predictions are exactly the frozen encoder's predictions.**
  They are identical inside and outside the RL, so the encoder is evaluated directly, and no
  RL training is needed here.
- **The MAPPO policy outputs decoy placements, not techniques.** It has no micro-F1 and is
  outside this comparison.

| Setting | Value |
|---|---|
| **Primary encoder** | **Transformer**, the encoder the thesis proposes (decision Q4, confirmed 2026-11-03) |
| Secondary encoders | GRU and LSTM, **if resources permit**. Whether to run them is decided and recorded **before any test result is opened**. If run, they are reported in full and enter the Holm family (Section 7) |
| Training, checkpoint, threshold | As `Temarl_Test_v1_L1/study_spec.py`: BCE, validation-best checkpoint, threshold from (0.1, 0.2, 0.3, 0.4, 0.5) on validation micro-F1, ties to the smallest |
| Window | W = 16 |
| Seeds | 0–9, per fold |
| Corpus | ported from the old 84-label corpus to `camlds_real` (81 labels). This port is precondition B2 |

**Training count.** One training per fold and seed, over **both** families:

| | Folds | × seeds | Trainings |
|---|---|---|---|
| Transformer only | 29 variant + 3 scenario = 32 | 10 | **320** |
| Transformer, GRU and LSTM | 32 per encoder | 10 | **960** |

Pilot runs for the patience and budget rules are extra, if they are redone on this corpus
(part of B2). The variant family alone is 290 per encoder. Kuwano needs no training.

### 3.2 The adapted Kuwano baseline

Algorithm 1 as validated in `kuwano_repro/kuwano.py` (Prediction/TP/FP/FN 48/48 against the
paper's Tables 5–7).

| Condition | Reference "users" | Threshold | Role |
|---|---|---|---|
| **K-A-val** | ATT&CK v11.0 groups (the validated 131 × 191 matrix) | selected on validation | **primary comparator** (Q1) |
| K-A-pub | ATT&CK v11.0 groups | 0.17, as published | secondary; labelled "as published" |
| K-B-val | the fold's training runs, one user per run (its set of parent techniques) | selected on validation | secondary (Q3) |

**Exactly what changes from the reproduced method:**

| Element | Reproduced (paper) | K-A | K-B |
|---|---|---|---|
| Similarity, k = 60, weight 1/(1 − s), SupportRate = Score / k, exact arithmetic | yes | **unchanged** | **unchanged** |
| Reference users | ATT&CK v11.0 groups | unchanged | **training runs** |
| Tie-break among equal similarities | group name | unchanged | **run name** |
| Observed set | all techniques detected so far | **union of the previous 16 steps** (sensitivity: full history) | same |
| Target | all remaining techniques of the attack | **the next step's technique set** | same |
| Drop already-observed techniques | yes | **no** (Section 4) | no |
| Tactic filter | yes | **no** (Section 4) | no |
| Output space | 191 techniques | **restricted to our 81 labels** | the 81 labels |
| Threshold | 0.17 | 0.17 (pub) or selected on validation (val) | selected on validation |
| Similarity = 1 | never reached on the paper's data | **limit rule** (Section 5) | limit rule |

For K-B, every fold has at most 29 training runs, so with k = 60 every training run is a
neighbour. Score is still divided by 60, as Algorithm 1 states. Validation runs are never in
the reference.

### 3.3 Context baselines (deterministic; not part of the claim)

| Baseline | Prediction |
|---|---|
| Repeat previous | the previous step's label set |
| Label prior | each label scored by its training frequency per step; threshold selected on validation from (0.1–0.5) |

---

## 4. Task alignment: every model predicts the same thing

| Question | Answer, identical for every model |
|---|---|
| Prediction point | every step of a test run except its first |
| Target | the set of parent techniques on that step |
| Information used | the previous 16 steps of the same run: as an ordered sequence of multi-hot vectors (TEMARL), or as the union of their techniques (Kuwano). Same information; Kuwano loses only order and repetition |
| Label space | the same 81 parent techniques for every model, from the corpus vocabulary |
| Can an already-observed technique be predicted? | **Yes**, for every model |
| Tactic filter | **None**, for every model |
| Labels a model cannot output | reported as a ceiling beside its results, never silently dropped (Section 6) |

**Why observed techniques stay eligible and the tactic filter is off.** Both are part of the
paper's evaluation, not of Algorithm 1. On this corpus both would remove large shares of the
true targets. Measured over all 870 prediction points as corpus descriptives (no model
output involved):

| If the paper's rule were kept | Target labels it would make unpredictable |
|---|---|
| Drop techniques already in the 16-step window | **600 of 1,270 (47.2%)**, in 541 of 870 points |
| Tactic filter ("after the most late-stage tactic observed"), using the rule validated in `kuwano_repro` with each observed technique at its earliest ATT&CK tactic (equivalent there; this corpus has no clean listed tactic) | **926 of 1,270 (72.9%)**, in 670 of 870 points |

The attacks in CAM-LDS revisit techniques and return to earlier tactics constantly. Keeping
either rule would make Kuwano answer a different question from the encoder and cap its
recall far below any real limit.

**Labels outside a model's reach:**

- **K-A:** the 110 ATT&CK techniques outside our 81 labels are dropped (this removes false
  positives, so it can only help the baseline). 4 of our labels are used by no v11 group:
  T1531, T1490, T1599 and T1525, 15 of 1,341 parent-level instances corpus-wide. K-A can
  never recommend them.
- **K-B and TEMARL:** a label absent from a fold's training runs cannot be learned. This is
  reported as the fold's unseen-label ceiling (frozen R3/R4).

---

## 5. Similarity exactly 1: rule declared, implemented and tested

The paper's weight 1/(1 − s) is undefined at s = 1. This never occurred on the paper's data,
but **occurs at 4 of 870 prediction points** here for K-A (a window's technique set equals a
v11 group's set; measured on inputs only).

**Rule (the limit as s → 1).**

- The weight grows without bound, so a technique's score behaves like n/ε + finite, where n
  is the number of identical neighbours that use it.
- Each technique therefore gets the pair **(n, SupportRate from the other neighbours)**,
  compared lexicographically, so techniques of an identical neighbour rank above all others.
- Any technique with n > 0 is recommended.
- The number of affected prediction points is reported.

**Implementation:** `recommend_limit()` in `kuwano_repro/kuwano.py`. The validated
`recommend()` is **unchanged** and still raises at s = 1.

**Tests**, all passing (16 of 16 in `kuwano_repro/tests/`):

- a hand-computed case with an identical neighbour;
- agreement with `recommend()` on toy cases without s = 1;
- agreement with `recommend()` on every step of the paper's three test sequences.

The reproduction outputs stay byte-identical: `PREDICTIONS.csv` 7b0edf75…,
`VALIDATION.txt` 522cc940…, `TABLES_5_7.csv` 020e0b2e….

---

## 6. Metrics: the same code for every model

Functions from `Temarl_Test_v1_L1/metrics_cmd.py`, called identically:

- **Primary:** micro-F1 over the 81 parent techniques, pooled over a fold's test steps.
- **Secondary:** exact-set accuracy; macro-F1 (reported, never relied on: 10 of the 81 labels
  occur once).
- **Threshold-free:** precision@1, recall@3, recall@5, ranked by probability (TEMARL) or by
  the (n, SupportRate) pair (Kuwano). These need no threshold, so they are the cleanest
  comparison.
- **Ceilings, beside every number:** the unseen-label rate for TEMARL and K-B, and the
  unsupported-label share for K-A (Section 4).
- **Thresholding** is done in exact arithmetic for Kuwano. The metric code receives the
  resulting 0/1 decisions.

### 6.1 Tuning parity

| | TEMARL | Kuwano K-A-val / K-B-val | K-A-pub |
|---|---|---|---|
| Tuned at evaluation | the threshold: 5-value grid, validation only, smallest among ties | the threshold: 9-value grid `(0.05, 0.10, 0.17, 0.25, 0.35, 0.50, 0.75, 1.00, 1.50)`, same rule, validation only | nothing |
| Selected during training | checkpoint (validation-best) and patience, validation only | no training, nothing to select | – |
| Test data | never selects anything | never selects anything | – |

Kuwano's grid is wider because SupportRate is not a probability and can exceed 1. The wider
grid gives the baseline more tuning opportunity, not less, so it works against our claim.
A threshold selected at either end of a grid is reported, and **no grid is extended after
seeing results.**

---

## 7. Analysis

- **Primary test.** Variant-held-out family, 29 folds. For each fold f:
  d_f = (TEMARL Transformer micro-F1, mean over its 10 seeds) − (K-A-val micro-F1).
  - Report the mean of d_f with a 95% bootstrap CI (10,000 resamples over folds, fixed seed).
  - Report a two-sided Wilcoxon signed-rank test.
  - "Outperforms" may be said only if the CI excludes 0 and p < 0.05.
- **Dependence warning, reported with the test.** 18 of the 29 folds are S1 variants
  (Jaccard 0.858), so they are not independent. Per-scenario means (S1, S3, S6) are reported
  beside the pooled result. The claim must state whether the direction holds in each
  scenario.
- **Holm family:**
  - Transformer against K-A-val (primary), K-A-pub and K-B-val;
  - plus GRU and LSTM against K-A-val, if they are run.
- **Scenario-held-out family:** 3 folds, so **descriptive only, no significance test**.
  Report per fold with its ceilings. This is where the ATT&CK prior (K-A) can do something a
  corpus-trained model cannot: recommend labels never seen in training.
- **Variance.** Kuwano is deterministic: one run, zero variance. TEMARL is reported as
  mean ± SD over seeds per fold, with the share of seeds above Kuwano.

---

## 8. Order of work and blinding

1. Approve v0.3. Freeze `spec.py`. Commit it with the code it refers to.
2. Implement the Kuwano conditions and the context baselines. Gate: unit tests pass, and the
   reproduction outputs stay byte-identical.
3. Run them. Write the per-fold outputs and their SHA-256. **Do not open test-split numbers.**
4. Port the encoder pipeline to `camlds_real` (B2). Freeze its configuration. Record the
   GRU/LSTM decision.
5. Train and evaluate TEMARL. Then open all test numbers together and apply Section 7.

Step 3 before step 4 is safe only if the test numbers stay closed. Otherwise the baseline
could influence how our model is configured.

---

## 9. Preconditions before any confirmatory run

| # | Item | Status |
|---|---|---|
| B1 | Record the commit hash of the CAM-LDS analysis repository (`attack_times.csv` was downloaded as a ZIP) | **open** (`camlds_real/PROVENANCE.md` §2, §8) |
| B2 | Port TEMARL's encoder pipeline to `camlds_real` (81 labels, these folds) and test it; no model has ever been run on this corpus | **open** |
| B3 | Folds without validation | **resolved**: excluded (Q2, Section 2) |
| B4 | Similarity-1 rule implemented and tested | **resolved** (Section 5) |

---

## 10. Decisions (recorded 2026-11-03)

| # | Decision | Recorded |
|---|---|---|
| Q1 | Primary comparator | **K-A-val**; K-A-pub reported beside it, labelled "as published" |
| Q2 | The S2 folds without validation | **Excluded from the variant family (29 folds)**, every model alike; S2 remains in the scenario family |
| Q3 | K-B-val | **Included, as secondary** |
| Q4 | Our model | **TEMARL's prediction module**: the frozen encoder of the CTDE-based MARL framework. **Transformer** primary; GRU/LSTM secondary if resources permit, decided before any test result is opened |

---

## 11. Measured facts this protocol relies on

| Fact | Value |
|---|---|
| Our parent techniques present in ATT&CK v11.0 | 81 of 81 (1,341 of 1,341 parent-level instances) |
| Our sub-techniques missing from v11.0 | T1566.004 (12 instances); its parent T1566 is present |
| Our labels no v11 group uses | T1531 (6), T1490 (6), T1599 (2), T1525 (1) |
| Prediction points, corpus-wide (W = 16) | 870; 1,270 target label instances |
| Target labels already in the window | 600 (47.2%) |
| Target labels the paper's tactic filter would drop | 926 (72.9%) |
| Prediction points with similarity 1 for K-A | 4 of 870 |
| Variant-held-out folds (v1.0) | 31; 2 without validation (2_cron, 2_rootkit), excluded |
| Variant-held-out folds used | 29; 819 test steps; 790 prediction points; all have validation |
| Scenario-held-out folds | 3; 344 test steps; 331 prediction points; 25–29 training runs |
| TEMARL's encoder inside MAPPO | frozen: `requires_grad_(False)` + `eval()`, asserted in tests |
