# Idea 01 protocol: Kuwano et al. (2023) as an external baseline on CAM-LDS

**Status: DRAFT v0.2. Decisions Q1–Q3 recorded (2026-11-03); Q4 awaits one confirmation
(the encoder arm, Section 3.1). Not frozen. Nothing has been run.**
Once approved, the constants below are frozen in `idea01_kuwano/spec.py` and committed
*before* any result is computed. Changing anything after that means a new version and a
new commit, never an edit in place.

---

## 1. The claim

> On the CAM-LDS next-step technique-prediction task, under the frozen split protocol
> v1.0, our model's micro-F1 is higher than / equal to / lower than that of the published
> method of Kuwano et al. (2023), with both evaluated on identical prediction points,
> identical targets and identical metric code.

**What this does not claim:**

- that we reproduce Kuwano's own numbers (that was the separate reproduction in `kuwano_repro/`);
- that either method generalises to unseen campaigns, unless the result holds on the
  scenario-held-out family (Section 7);
- equivalence. A non-significant difference is reported as "no significant difference",
  never as "equal".

---

## 2. Inherited unchanged from the frozen split protocol v1.0

`camlds_real/split_spec.py`, frozen 2026-10-24. None of this is re-decided here:

| Item | Value |
|---|---|
| Corpus | `camlds_real/out/steps.jsonl`: 904 steps, 34 runs, 7 scenarios |
| Order | ascending `start` timestamp within a run |
| Label space | 81 parent techniques |
| Families | **variant held out** (primary) and **scenario held out** (secondary; S2, S3, S6; 344 test steps, 331 prediction points) |
| Variant-held-out folds used here | **29**: v1.0's 31 minus `2_cron` and `2_rootkit`, which have no validation run (decision Q2, Section 10). S1 × 18, S3 × 6, S6 × 5; 819 test steps, 790 prediction points. The exclusion applies to every model alike. `split_spec.py` itself is not edited |
| Validation | first run, in sorted order, of each training scenario with ≥ 2 runs |
| Repeats | kept (main); collapsed as a separate sensitivity condition |
| Window | W = 16, left-padded, never crossing a run boundary |
| Reporting | R1–R6, including the unseen-label ceiling beside every scenario-held-out number |

---

## 3. The task: identical for every model

- **Prediction point:** every step of a test run except its first.
- **Target:** the set of parent techniques on that step.
- **Information available:** the previous W = 16 steps of the same run.

Our model reads those 16 steps as an ordered sequence of multi-hot vectors. Kuwano's
method reads a set, so it receives the **union of the parent techniques in the same 16
steps**. That is the same information without order or repetition: no more, no less.
Using the full history instead (as the paper does) is a sensitivity condition.

### 3.1 "Our model": the prediction module of the proposed CTDE framework

The proposed framework is CTDE multi-agent RL: MAPPO with a centralised critic and
decentralised, parameter-shared actors (`Temarl_Test_v1_L1/mappo_cmd.py`). Each actor
receives a history embedding h from a **command-level sequence encoder**. That encoder
is trained on its own, with binary cross-entropy, to predict the next step's technique
set. It is then **frozen** inside MAPPO (`requires_grad_(False)` and `eval()`, asserted in
the tests), so the RL never changes it.

Consequences for this comparison:

- **The framework's technique predictions are exactly the frozen encoder's predictions.**
  They are identical inside and outside the RL, so the encoder is evaluated directly.
  No RL training is needed for Idea 01.
- **The MAPPO policy outputs decoy placements, not techniques.** It has no micro-F1 and
  is not part of this comparison; its deception metrics (dwell, depth) belong to a
  different comparison.

| Setting | Value |
|---|---|
| Encoder arm | **Transformer**, the encoder the thesis proposes. **Awaiting confirmation (Q4).** GRU and LSTM are not compared with Kuwano here |
| Training, checkpoint, threshold | As `Temarl_Test_v1_L1/study_spec.py`: BCE, validation-best checkpoint, threshold from (0.1–0.5) on validation micro-F1, ties to the smallest |
| Window | W = 16 (the study's reference window) |
| Seeds | 0–9 (the study's main seeds), per fold |
| Corpus | ported from the old 84-label corpus to `camlds_real` (81 parent labels). This port is precondition B2 |

**Compute.** Our model is trained once per fold and seed: (29 + 3) folds × 10 seeds =
**320 training runs**. Kuwano needs no training and runs in seconds.

---

## 4. The Kuwano conditions

Algorithm 1 is used **exactly as validated** in `kuwano_repro/kuwano.py`: Sørensen–Dice
similarity, top k = 60 neighbours, weight 1/(1 − similarity), SupportRate = Score / k,
exact rational arithmetic, ties broken by name.

| Condition | Reference "users" | Threshold | Role |
|---|---|---|---|
| **K-A-val** | ATT&CK v11.0 groups (131 × 191, the validated matrix) | selected on validation (Section 4.2) | **primary comparator** |
| K-A-pub | ATT&CK v11.0 groups | 0.17, as published | secondary: the method exactly as published |
| K-B-val | the fold's **training runs**, each as one user (its set of parent techniques) | selected on validation | secondary: the same algorithm fitted to our data |

**Why K-A-val is the primary comparator.** Our model's threshold is selected on
validation. Giving the baseline the same selection is the fair default; K-A-pub is
reported beside it so the published setting is also visible.

### 4.1 Rules common to all three conditions

1. **Output restricted to our 81 labels.** K-A recommends from 191 techniques; the 110
   outside our label space cannot be scored and are dropped. This removes false positives,
   so it can only *help* the baseline.
2. **No evaluation filters from the paper.** The paper's evaluation drops already-observed
   techniques and earlier tactics. Neither is part of Algorithm 1, and our targets repeat
   techniques (T1059 alone is 17.3% of all labels), so both are switched off.
3. **Similarity exactly 1.** Never reached on the paper's data, so the paper defines no
   weight for it. Here it can happen, for example when a window's set equals a short
   group's set. **Limit rule, declared now:** as similarity → 1 the weight → ∞, so every
   technique of an identical neighbour is recommended and ranked above all others (ordered
   among themselves by their finite remainder). The number of affected prediction points
   is reported.
4. **Empty observed set** (cannot occur with W ≥ 1 and every step labelled; declared for
   completeness): all similarities are 0, so nothing is recommended.
5. **K-B specifics.**
   - The reference is built from training runs only; validation runs are never in it.
   - Ties are broken by run name.
   - Every fold has at most 29 training runs, so with k = 60 all of them are neighbours.
     Score is still divided by 60, as Algorithm 1 states.

### 4.2 Threshold selection

The rule is the same as our model's (`Temarl_Test_v1_L1/metrics_cmd.select_threshold`):
take the value maximising validation micro-F1, with ties going to the smallest value.

- **Our model's grid:** 0.1 to 0.5, which suits probabilities.
- **Kuwano grid**, declared now because SupportRate is not a probability and can exceed 1:
  `(0.05, 0.10, 0.17, 0.25, 0.35, 0.50, 0.75, 1.00, 1.50)`. It includes the published 0.17.
- If the selected value is at either end of a grid, that is reported. **The grid is never
  extended after seeing results.**
- Thresholding is done in exact arithmetic. The metric code receives the resulting 0/1
  decisions.

---

## 5. Context baselines (deterministic; not part of the claim)

| Baseline | Prediction |
|---|---|
| Repeat previous | the previous step's label set |
| Label prior | each label scored by its training frequency per step; threshold selected on validation from our model's grid |

These show whether either model beats doing nothing clever.

---

## 6. Metrics: the same code for every model

Functions from `Temarl_Test_v1_L1/metrics_cmd.py`, called identically:

- **Primary:** micro-F1 over the 81 parent techniques, pooled over a fold's test steps.
- **Secondary:** exact-set accuracy, macro-F1 (reported, never relied on: 10 of the 81
  labels occur once).
- **Threshold-free:** precision@1, recall@3, recall@5, ranked by probability (our model)
  or SupportRate (Kuwano). These need no threshold, so they are the cleanest comparison.
- **Ceilings, beside every number** (R3/R4):
  - for our model and K-B, the unseen-label rate of the fold;
  - for K-A, the share of test labels that no v11 group uses. These are T1531, T1490,
    T1599 and T1525: 15 of 1,341 instances corpus-wide, which K-A can never recommend.

---

## 7. Analysis

- **Primary test.** Variant-held-out family. For each fold f:
  d_f = (our model's micro-F1, mean over its seeds) − (K-A-val micro-F1).
  - Report the mean of d_f with a 95% bootstrap CI (10,000 resamples over folds, fixed seed).
  - Report a two-sided Wilcoxon signed-rank test.
  - "Outperforms" may be said only if the CI excludes 0 and p < 0.05.
- **Dependence warning, reported with the test.** 18 of the 29 folds are S1 variants
  (within-scenario Jaccard 0.858), so they are not independent. Per-scenario means (S1, S3,
  S6) are reported beside the pooled result. The claim must state whether the direction
  holds in every scenario.
- **Holm family.** The three comparisons of our model against K-A-val, K-A-pub and K-B-val
  are one family, Holm-corrected. The primary is designated in advance.
- **Scenario-held-out family:** 3 folds, so **descriptive only, no significance test**.
  Report per fold with its ceilings. This is where the ATT&CK prior (K-A) can do something
  a corpus-trained model cannot: predict labels never seen in training.
- **Variance.** Kuwano is deterministic: one run, zero variance. Our model is reported as
  mean ± SD over its seeds per fold, together with the share of seeds above Kuwano.

---

## 8. Order of work and blinding

1. Approve this protocol, freeze `spec.py`, commit.
2. Implement. Add the similarity-1 limit rule to `kuwano.py` as an **opt-in** parameter
   (default: raise, as validated). Gate: all 13 reproduction tests pass, and the
   reproduction outputs stay byte-identical (`PREDICTIONS.csv` 7b0edf75…,
   `VALIDATION.txt` 522cc940…).
3. Run the Kuwano conditions and the context baselines. Write the per-fold outputs and
   their SHA-256. **Do not open test-split numbers yet.**
4. Freeze our model's configuration on this protocol (Section 9, B2).
5. Run our model, then open all test numbers together and apply Section 7.

Step 3 before step 4 is safe only if the test numbers stay closed. Otherwise the baseline
could influence how our model is configured.

---

## 9. Preconditions: must be resolved before any confirmatory run

| # | Blocker | Source |
|---|---|---|
| B1 | Record the commit hash of the CAM-LDS analysis repository (`attack_times.csv` was downloaded as a ZIP) | `camlds_real/PROVENANCE.md` §2, §8 |
| B2 | Our model has **never been run on `camlds_real`**: only the extractor and split spec read it. Its configuration is fixed in Section 3.1, but the encoder pipeline must be ported to this corpus (81 labels, its folds) and tested before any run | measured: no other code reads `steps.jsonl` |
| B3 | ~~Folds 2_cron and 2_rootkit have no validation run~~ **Resolved by Q2:** both excluded, for every model (29 variant folds) | measured; decided 2026-11-03 |
| B4 | The similarity-1 limit rule implemented and tested (Section 8, step 2) | this protocol |

---

## 10. Decisions (recorded 2026-11-03)

| # | Decision | Recorded |
|---|---|---|
| Q1 | Primary comparator | **K-A-val** (threshold selected on validation); K-A-pub reported beside it |
| Q2 | The S2 folds without validation | **Both excluded from the variant family: 29 folds**, every model alike |
| Q3 | K-B (Algorithm 1 fitted to our training runs) | **Included, as secondary** |
| Q4 | Our model | **The proposed CTDE-based multi-agent RL framework**, compared through its prediction module (Section 3.1). Encoder arm: **Transformer, awaiting confirmation** |

---

## 11. Measured facts this protocol relies on

| Fact | Value |
|---|---|
| Our parent techniques present in ATT&CK v11.0 | 81 of 81 (1,341 of 1,341 instances) |
| Our sub-techniques missing from v11.0 | T1566.004 (12 instances); its parent T1566 is present |
| Our labels no v11 group uses | T1531 (6), T1490 (6), T1599 (2), T1525 (1) |
| Variant-held-out folds (v1.0) | 31; test steps 866; training runs per fold 1–16 |
| Folds with no validation run | 2_cron, 2_rootkit (excluded, Q2) |
| Variant-held-out folds used | 29 (S1 × 18, S3 × 6, S6 × 5); test steps 819; prediction points 790; all have validation |
| Scenario-held-out folds | 3; test steps 344; prediction points 331; training runs per fold 25–29 |
| Our model's encoder inside MAPPO | frozen: `requires_grad_(False)` + `eval()`, asserted in tests (`mappo_cmd.py`) |
| Our model's threshold grid and tie rule | (0.1, 0.2, 0.3, 0.4, 0.5); smallest among ties |
