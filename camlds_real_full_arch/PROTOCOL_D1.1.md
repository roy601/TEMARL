# Protocol D1.1: hyperparameter sensitivity of the history effect (an addition to D1.0; simulation)

**Status: DRAFT, 2026-11-18. Not frozen.** No D1.1 cell has been trained. D1.1 must be frozen
(`spec_d1_1.py --freeze`, after the user's approval) **before the D1.0 test is opened**
(`run_all_d1.py open`). The freeze refuses once `results_d1/main/TEST_OPENED.json` exists, and the order of
the two events is provable from git history (the freeze records the git commit it was made on). After the
freeze, any change means a new version, never an edit of this one.

## 0. What D1.1 is, and what it does not change

- **D1.0 is unchanged.** Every rule, file and number frozen in `SPEC_D1.json` stays as it is. D1.1 pins
  `SPEC_D1.json` itself, and its runner, scorer and stage driver refuse to run unless D1.0's spec check
  passes. D1.1 adds a hyperparameter sensitivity analysis (Sections 1-6) and descriptive supplementary
  analyses of D1.0's main cells (Section 6a). It changes nothing that D1.0 runs, scores or reports, and
  its results never replace D1.0's primary result.
- **Why:** our supervisor noted that MARL results can be poor when hyperparameters are not tuned. D1.0
  uses one untuned setting for every arm (D1.0 Section 7). D1.1 asks whether the D1.0 answer to Q1
  depends on that setting.
- **Numbering:** D1.0 (Sections 1, 6, 9, 10 and 12) assigns the published comparators to "protocol D1.1".
  This analysis must be declared before the D1.0 test opening, which comes before those replications
  exist. It therefore takes the number D1.1, and **the published-comparator family moves to protocol
  D1.2**. Nothing else about that family changes (decision D7).

## 1. Question

- **Q5 (Family H, tested):** if allpos and NoHistory each get their own hyperparameters, tuned on
  validation only with the same tuning budget, does allpos beat NoHistory on E1 and on P1? E1, P1 and
  the arms are as defined in D1.0 (Sections 4 and 6).
- **Descriptive (no test):**
  - the allpos minus NoHistory difference under each of the 9 settings;
  - tuned minus the D1.0 setting, for each arm;
  - how often each setting is selected;
  - mean validation E1 for each setting and arm.

## 2. Where D1.0's settings come from (source check, 2026-11-18)

Checked against Yu et al. 2022, *The Surprising Effectiveness of PPO in Cooperative Multi-Agent Games*
(NeurIPS 2022 Datasets and Benchmarks; arXiv:2103.01955 v4, appendix tables):

- **Common settings (their Table 7) match ours:** gamma 0.99, GAE lambda 0.95, gradient clip norm 10,
  Huber loss with delta 10, Adam with epsilon 1e-5, orthogonal initialisation.
- **Learning rate:** 5e-4 is their SMAC and Football value (MPE uses 7e-4).
- **Clip:** 0.2 is their value on most SMAC maps.
- **Epochs:** 10 is their value for MPE Spread and for three SMAC maps. They use 15 on most SMAC maps and
  5 on the hardest.
- **Entropy coefficient:** 0.01 does not appear in their MPE or SMAC tables (their Hanabi value is
  0.015). It is our choice.

D1.0's text cites `mappo_cmd.HP`, not this paper.

**Their own sweep (their Table 13):**

- learning rate {1e-4, 5e-4, 7e-4, 1e-3} in every domain;
- epochs {5, 10, 15} (MPE also 20);
- mini-batches {1, 2, 4};
- clip {0.05 to 0.5};
- entropy coefficient swept only in Hanabi.

## 3. Grid (declared now)

- **Swept:** learning rate ∈ {1e-4, 5e-4, 1e-3} × PPO epochs ∈ {5, 10, 15}, which gives 9 settings.
  Actor and critic share the learning rate, as in `mappo_cmd.py`.
  - These values are a subset of the MAPPO authors' own sweep (Section 2).
  - The D1.0 setting (5e-4, 10 epochs) is the centre of the grid, so "tuned" is never worse than D1.0 on
    validation.
- **Why these two settings:**
  - The MAPPO authors swept the learning rate in every domain.
  - They name the number of training epochs ("training data usage") among the five factors they found
    critical.
  - They did not sweep the entropy coefficient in MPE or SMAC.
  - D1.0 already follows their suggestions on their other factors: value normalisation is on; the
    MAPPO critic takes global and local input; there is no mini-batch splitting (1 mini-batch); clip is
    0.2; the batch is large (64 envs × 64 steps × 4 agents per update).
- **Not swept:** everything else stays at the D1.0 values. This covers entropy 0.01, clip 0.2, gamma,
  GAE, 64 × 64 rollouts, 2,000,000 environment steps and the network sizes. The environment, reward
  (proposal), command order (frozen), movement (recorded) and encoders (protocol 1.2 checkpoints) are
  D1.0's primary setting (`run_d1.setting(None)`).
- **Equal budget:** both arms get the same 9 settings × 3 seeds × 2,000,000 steps.

## 4. Cells

- **Count:** 9 settings × 2 arms (allpos, NoHistory; MAPPO) × 32 folds × seeds 0-2 = **1,728 cells**
  (`run_d1_1.py`).
- **Same as a D1.0 primary cell except for the two swept settings:** the protocol 1.2 encoder checkpoint
  of the same fold and seed, checked against its validation BCE; policy checkpoint chosen by validation
  E1; validation randomness 100000+seed; test randomness 200000+seed; 20 repeats; sealed test output
  (SHA-256 in `result.json`). Each cell also records its setting and the full hyperparameters it used.
- **The D1.0 setting is trained again here, not copied from D1.0.** Every D1.1 number therefore comes from
  D1.1 cells, and no D1.0 sealed file is read a second time. These cells use the same seeds as D1.0's
  seeds 0-2, so they are not independent of those D1.0 cells. A test checks, on a small CPU run
  (NoHistory), that a D1.1 cell with the D1.0 setting reproduces the D1.0 cell of the same seed exactly.
- **Seeds 0-2:** protocol 1.2 encoder checkpoints exist only for seeds 0-9, and three seeds per setting
  is what the budget allows. D1.0's sensitivity analyses use 5 seeds.
- **Run order:** seed, then fold, then setting, then arm. Each finished seed therefore holds every fold,
  setting and arm.
- **Time:** at D1.0's measured 93 s per cell on GPU PC 1, the 1,728 cells take about 45 h. That figure
  is for 10-epoch cells; 5- and 15-epoch cells differ in the update phase, which is not measured
  separately. The `tune` stage first times one 15-epoch cell and checks its dry-run reproduction on that
  device.

## 5. Selection (nested in each fold; validation only)

- **Rule:** for each arm and each fold separately, the selected setting is the one with the highest
  validation E1, averaged over seeds 0-2. The validation E1 used is the value at the policy checkpoint
  chosen by validation E1 (`best_validation_dwell`).
- **Ties** (difference ≤ 1e-12): the D1.0 setting wins, then the first setting in grid order (learning
  rate ascending, then epochs ascending).
- **Only the fold's own validation run is used. Why not one setting per arm for all folds** (the
  2026-11-18 proposal: tune on 3 folds, apply to all):
  - Each of the 7 validation runs is also the test run of a fold. For example, `1_autostart_localaccount`
    validates 20 of the 32 folds and is the test run of its own fold; `3_ssh_apt` validates 7 folds and
    is tested in 2.
  - A setting chosen on pooled validation scores would therefore be chosen partly on other folds' test
    runs.
  - Choosing inside each fold keeps every fold's test run out of its own selection (nested selection).
- **Only E1 is used for selection; P1 is not**, as in D1.0 Section 7, where nothing but validation E1 is
  chosen on validation.
- **Recording:** the selection is written to `results_d1_1/SELECTION.json` by the validation dry run and
  committed before the opening. The opening recomputes it from the cells and refuses if it differs.

## 6. Evaluation (`evaluate_d1_1.py`)

1. **Dry run:** every cell's saved actor is re-evaluated on its validation episodes and must reproduce
   its recorded best validation E1 exactly (tolerance 1e-9). Only then is `SELECTION.json` written.
2. **Test opened once** (`--open-test`). It refuses unless:
   - both specs pass and all 1,728 cells exist;
   - the dry run passed and `SELECTION.json` matches the recomputed selection;
   - `TEST_OPENED.json` is absent.

   Every sealed file's SHA-256 is checked before it is read. Every cell must carry its declared setting
   and hyperparameters, arm, learner, test seed, 20 repeats, environment and order.

- **Unit:** the test run of each of the 29 known-variant folds. Per unit and arm, the outcome of the
  setting selected for that arm in that fold is averaged over 20 repeats, then over seeds 0-2. The 3
  unseen-scenario folds are reported separately and descriptively.
- **Family H (Q5):** tuned allpos vs tuned NoHistory on E1 and P1 (2 comparisons), with D1.0's rules
  (`evaluate_d1`, unchanged):
  - mean paired difference, with a 95% bootstrap CI (10,000 resamples of runs, seed 20261103);
  - two-sided Wilcoxon signed-rank;
  - Holm within the family;
  - "outperforms" only if Holm p < 0.05 and the CI excludes 0.

  Family H is not corrected together with D1.0's families: it answers a different question. This is
  stated with the results.
- **Descriptive (mean paired difference and 95% bootstrap CI; no p-value, no verdict, no claim):**
  - (a) allpos minus NoHistory under each of the 9 settings, on E1 and P1;
  - (b) tuned minus the D1.0 setting (D1.1's own cells) for each arm;
  - (c) per arm, the number of folds that selected each setting;
  - (d) per arm, the mean validation E1 of each setting.
- **How the result is read (declared now).** For each outcome:
  - If Family H's verdict equals the verdict of D1.0's Family 1, the write-up says the D1.0 result for
    that outcome agrees with the result under per-arm tuning in this grid.
  - If the verdicts differ, it says the D1.0 result for that outcome depends on the hyperparameters, and
    both results are reported.
  - D1.1 never replaces D1.0's primary result.
  - The seed counts differ (D1.0: 10 seeds; D1.1: 3), so the two confidence intervals are not equally
    wide; this is stated.
- Every result is reported whatever its direction.

## 6a. Supplementary analyses of D1.0's main cells (`supplement_d1_1.py`; added 2026-11-18)

**Why.** A devil's-advocate review (2026-11-18) pointed out a structural fact, which was then checked in
code: every one of D1.0's 29 primary folds trains **only** on sibling variants of its test run's scenario
(16 training runs for S1, 4 for S3, 3 for S6), and 18 of the 29 units are S1. A positive D1.0 Family 1
result therefore means "history helps on **held-out variants of known attack scenarios**". Part of that
help may be recognising a known scenario's script rather than using the run's own past. These analyses
separate the two and show how much S1 drives the result. All of them are descriptive (mean paired
difference and 95% bootstrap CI, no p-value, no verdict), and none changes a D1.0 result.

- **A, per-scenario effect:** allpos − NoHistory (MAPPO) on E1 and P1, separately for S1 (18 runs), S3 (6)
  and S6 (5).
- **B, scenario-balanced effect:** the mean of the three scenario effects (each weight 1/3), with a
  stratified bootstrap (runs resampled within each scenario; 10,000 resamples, seed 20261103). A cluster
  bootstrap over scenarios is not used: 3 clusters are too few.
- **C, unseen scenarios:** allpos − NoHistory on the 13 test runs of D1.0's 3 scenario-held-out folds,
  whose scenario never appears in training, overall and per scenario. This is the evidence on
  generalisation to new attacks. The S3 and S6 runs are test runs in both groups, so A and C are computed
  separately and never merged.
- **D, other-run history (evaluation only, no retraining):** each trained allpos MAPPO actor (29 variant
  folds × seeds 0-9) is evaluated on its own test episodes (D1.0's test seed and 20 repeats) with the
  history h of a **donor** run: the fold's validation run, which in every variant fold is a sibling of the
  same scenario. At step t the actor gets the donor's h after min(t, donor length) commands. This is
  compared with its own h (D1.0's sealed rows) and with h = 0 (D1.0's sealed `test_h0_summary`).
  - Reading, declared now: if own − donor > 0 (CI excluding 0), the run's own past matters. If
    donor − zero > 0 while own − donor is about 0, the gain is recognition of the scenario.
  - Harness check: the re-evaluation with each actor's own h must reproduce D1.0's sealed rows exactly,
    or the supplement stops.
- **V, validation gap by scenario (validation only):** the same split as A and C on the cells' best
  validation E1. It can be run any time after D1.0's main stage and reads no test file.

**When:** `--open` runs **once**, after D1.0's single test opening, and refuses before it
(`results_d1/main/TEST_OPENED.json` must exist). D1.0's opening therefore stays the first look at the
test. The supplement reads D1.0's sealed files (SHA-256 checked) and evaluates the trained actors, but it
can change no D1.0 verdict, because every analysis and its reading is fixed here, before the opening.

**Reporting:** D1.0's Family 1 is always reported together with A-C, and with the statement that 18 of the
29 units are S1. The 29 variants are never described as 29 independent campaigns.

## 7. Procedure (`run_all_d1_1.py`, on a GPU PC)

- **`tune`:**
  1. checks: both protocols frozen; D1.0's validity gate passed (`gate/GATE_RESULT.json`);
  2. preflight: the 96 allpos checkpoints (32 folds × seeds 0-2) must reproduce their validation BCE;
  3. timing and dry-run check: one 15-epoch cell, no test;
  4. the 1,728 cells, test sealed;
  5. validation dry run and nested selection.
- **`open`:** opens the D1.1 test once.
- **`supplement`:** Section 6a, once, after D1.0's opening (refused before it).
- As in D1.0, each stage logs to `results_d1_1/logs/`, stops at the first failure and can be restarted.
  `MANIFEST.json` checks what decides a cell's content (both specs, grid, base hyperparameters, setting,
  steps, repeats, folds). After a killed run, delete `RUNNING.lock` and start again.
- **Schedule:**
  1. Freeze D1.1 and push it before `run_all_d1.py open` is run for D1.0.
  2. The D1.1 cells run on GPU PC 1 after D1.0's main stage (and, if the GPU is needed, after its
     sensitivity stage), or on another GPU PC whose D1.1 preflight passes.
  3. D1.1 writes only `results_d1_1/` and `out_test_d1_1/`. The supplement reads D1.0's main cells
     without changing them.

## 8. Known limits (stated with the result)

- Only 2 of the many hyperparameters are tuned, with 3 values each. "Tuned" means "best of this grid on
  validation", not "optimal". The entropy coefficient, clip, batch size, network size and training length
  are not tuned.
- Selection uses one validation run per variant fold (the same run for 20 of the 32 folds) and 3 seeds,
  so it is noisy. Nested selection keeps it honest but does not make it precise.
- The tuned result uses 3 seeds against D1.0's 10.
- Section 6a's unseen-scenario evidence rests on 13 test runs from 3 scenarios; it is descriptive.
- The donor ablation uses one donor per fold (the fold's validation run); another sibling could give a
  different value.
- The other limits of D1.0 (Section 12) apply unchanged.

## 9. Decisions for the user (recommended choice first)

| # | decision | recommendation | why |
|---|---|---|---|
| H1 | grid | learning rate {1e-4, 5e-4, 1e-3} × PPO epochs {5, 10, 15}: 9 settings, about 45 h GPU. Cheaper alternative: learning rate × 2 epoch values, 6 settings, about 30 h | the MAPPO authors swept these two in every domain (Section 2). This replaces the 2026-11-18 proposal of learning rate × entropy: they swept entropy only in Hanabi |
| H2 | selection | nested: per arm and fold, on that fold's validation run | the proposal "tune on 3 folds, apply to all" would let other folds' test runs take part in the selection (Section 5) |
| H3 | seeds | 0-2 | encoder checkpoints exist for seeds 0-9 only; budget |
| H4 | D1.0 setting | trained again in D1.1, not copied | every Family H number comes from D1.1 cells (cost: 192 cells, about 5 h) |
| H5 | numbering | this is D1.1; the published comparators become D1.2 | this analysis must be declared before the D1.0 opening, and the replications are not done |
| H6 | schedule | frozen before the D1.0 opening; run after D1.0's main stage | no D1.0 test number can influence D1.1 |
| H7 | supplementary analyses (Section 6a) | per-scenario, scenario-balanced, unseen-scenario and other-run-history analyses of D1.0's main cells, descriptive, run once after D1.0's opening | the devil's-advocate review: D1.0's primary units are held-out variants of scenarios seen in training (29 of 29), and 18 of 29 are S1 |

## 10. Reproducibility

- `spec_d1_1.py --freeze` writes `SPEC_D1_1.json`: the SHA-256 (after CRLF→LF) of `SPEC_D1.json`, this
  protocol, `run_d1_1.py`, `evaluate_d1_1.py`, `supplement_d1_1.py`, `run_all_d1_1.py`, `test_d1_1.py` and
  `spec_d1_1.py`, plus
  the git commit at the freeze. The check also runs D1.0's check, so D1.0's 31 files stay pinned.
- **Tests (`test_d1_1.py`):**
  - the grid and its source;
  - the setting reaches the optimiser and the PPO loop;
  - with the D1.0 setting, a D1.1 cell reproduces a D1.0 cell exactly;
  - sealing;
  - preflight;
  - restart identity;
  - the nested selection and its tie rule;
  - scoring on the selected settings;
  - every refusal of the single opening;
  - the spec and the stage driver.
- Code, configuration, per-cell results, `SELECTION.json` and sealed test outputs are committed;
  checkpoints stay on the GPU PCs.
