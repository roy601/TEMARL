# Protocol 1.2: amendment to protocols 1.0 and 1.1

**Status: approved 2026-11-09. It is frozen by the commit that adds it, and that commit must be
pushed before any test result is opened. No test result has been opened.** Constants and
fingerprints: `idea01_kuwano/spec_1_2.py`. Check: `python idea01_kuwano/spec_1_2.py`.

Protocols 1.0 and 1.1 stay in force and are not edited. This file only adds to them.

## 1. Why

Protocol 1.1 left the final encoder design and the GRU/LSTM decision open, to be chosen on
validation data only. Both are now decided. This file records them and fixes how the test results
will be opened and counted, **before anyone sees them**.

## 2. The final design

| Item | Decision |
|---|---|
| **Primary encoder** | Transformer `allpos`. Wherever 1.0 says "Transformer", it now means this model |
| What differs from the frozen Transformer | Two things: a step attends only to itself and earlier steps, and the loss is taken at every position (SASRec, Kang & McAuley, ICDM 2018). Same layers and size (77,713 parameters) |
| **Secondary encoders** | The frozen GRU and LSTM, trained with the same loss at every position. They enter the Holm family, as 1.0 requires. **They never replace the Transformer, whatever the test shows** |
| History `h` used by MAPPO | The 64-number state at the last position. Its size does not change |
| Patience | 16 checks, all encoders |
| Update limit | Main condition: 9,152 for the Transformer (no training reached it), 18,304 for GRU and LSTM. `collapse_repeats`: 18,304 for all three. It is a safety limit only |
| Folds, window, labels, seeds, threshold rule, metrics | Unchanged from 1.0 and 1.1. No grid is extended |

## 3. Everything that was tried

All on validation data, under the rule in `camlds_encoder/SELECTION_RULE.md`, written before the
first candidate ran. Scores are micro-F1, pooled within 4 groups, groups weighted equally.

| Design | What it changes | Novel points | All points | Decision |
|---|---|---|---|---|
| `baseline` | The frozen Transformer | 0.729 | 0.814 | Starting point |
| `causal` | Attention mask only (control) | 0.737 | 0.820 | Control, not a candidate |
| **`allpos`** | Mask, and loss at every position | **0.774** | **0.852** | **Kept** |
| `repeat` | `allpos` + separate output for repeated labels (RepeatNet) | 0.706 | 0.795 | Rejected |
| `asl` | `allpos` with Asymmetric Loss | 0.756 | 0.818 | Rejected |
| `asl_long` | `asl` with twice the update limit | 0.764 | 0.823 | Rejected |
| GRU | Secondary encoder | 0.772 | 0.848 | Reported, no decision |
| LSTM | Secondary encoder | 0.775 | 0.849 | Reported, no decision |

**Disclosure.** `asl_long` was a second chance, decided after `asl` was rejected, because 274 of its
320 trainings had used the whole update limit. The rule did not change, and it also failed.

## 4. What is still to be trained

`collapse_repeats` (1.1, A3): Transformer `allpos`, GRU and LSTM × 32 folds × 10 seeds = **960
trainings**. Each training selects its own checkpoint and threshold on validation, as always. The
design is **not** chosen again.

## 5. How the test results are opened

1. **Freeze first.** This file and `spec_1_2.py` are committed and pushed. `python
   idea01_kuwano/spec_1_2.py` must pass.
2. **Run `collapse_repeats`.** Its test outputs are sealed like the others.
3. **Stage 1, once: our encoders.** Main and `collapse_repeats` are scored together, by the pinned
   script (Section 9).
4. **Stage 2, later: the comparison with Kuwano**, by 1.0 Section 7.
5. **After opening, nothing changes.** No design, threshold, grid or rule is touched, whatever the
   results are.

**Change from 1.0.** 1.0 opens all test numbers together. Here they are opened in
two stages. This is safe because neither side can be adjusted to the other: Kuwano's predictions
have been sealed since 2026-11-03 (`idea01_kuwano/sealed/predictions.jsonl`), and our design is
frozen here.

**Never opened:** `causal`, `repeat`, `asl`, `asl_long`. Their test files stay sealed.

## 6. What Stage 1 reports

| Item | Rule |
|---|---|
| Encoders | Transformer `allpos`, GRU, LSTM |
| **`baseline`** | Main condition only, descriptive: does the improvement chosen on validation hold on data it never saw? Reported by the score that chose it (`SELECTION_RULE.md`) and per fold. It cannot change the design |
| Conditions | Main. `collapse_repeats` beside it, never instead of it |
| Variant-held-out family (29 folds) | The primary result |
| Scenario-held-out family (3 folds) | Descriptive only, no significance test, as 1.0 |
| Metrics | 1.0 Section 6, same code, with the unseen-label ceiling beside every number |
| Split by points | All, novel and copy (1.1, A1) |
| Split by labels | Repeat and new (1.1, A2) |
| Split by scenario | S1, S3 and S6 each on its own. The S1 result is stated plainly (Section 8) |
| Variance | Mean ± SD over the 10 seeds, per fold |

## 7. Transformer against GRU and LSTM (new)

1.0 compares GRU and LSTM only with Kuwano. To answer "is the Transformer needed?", two more
comparisons are added on the primary family, as their **own family of two**, so the 1.0 family is
unchanged.

- For each fold f: d_f = Transformer `allpos` micro-F1 − GRU (or LSTM) micro-F1, each the mean over
  its 10 seeds.
- Mean of d_f with a 95% bootstrap CI (10,000 resamples over folds, seed 20261103), two-sided
  Wilcoxon signed-rank test, Holm correction over the two comparisons.
- "Outperforms" may be said only if the CI excludes 0 and the corrected p < 0.05. **Otherwise the
  thesis says "no difference shown".**
- As in 1.0, the claim must state whether the direction holds in each of S1, S3 and S6.
- The Wilcoxon test is `scipy.stats.wilcoxon` (scipy 1.17.1, default method); zero differences are
  dropped.
- These two comparisons are made on the **main condition**. On `collapse_repeats` the same numbers
  are shown beside them as a sensitivity check, with no claim.

## 8. Limits stated in advance

- **The three encoders were tied on validation** (novel points 0.774, 0.772, 0.775).
- **S1 got worse with `allpos`** on validation (novel −0.033), measured on the same 8 steps of one
  validation run.
- **Weighting.** 18 of the 29 variant-held-out folds are S1, so a mean over folds leans towards S1.
  On validation, `allpos` improved much less by the fold mean (novel 0.815 → 0.819) than by the
  score that chose it (0.729 → 0.774). Both are reported on the test.
- **Patience** was chosen from the Transformer's pilot only.
- **Threshold grid.** It stops at 0.5, and 124 of 320 `allpos` trainings chose 0.5 (GRU 157, LSTM 175).
- **ASL** was tested only at the authors' published settings. The result is "no benefit shown on
  validation", not "ASL is worse".
- **Step order** is CSV order (1.1, A5). **No time features** are used (1.1, A6).

## 9. Pinned at the freeze

`spec_1_2.py` records the SHA-256 of:

- this file, the 1.0 and 1.1 files, and `camlds_encoder/SELECTION_RULE.md`;
- the code that trains and scores: `port.py`, `data.py`, `run.py`, `variants.py`, `run_variants.py`,
  `evaluate_test.py` and `camlds_real/build_sidecar.py`, and the patience and limit in `budget.json`;
- the sealed test outputs of each of the 8 designs on the main condition, as one combined fingerprint
  per design, and Kuwano's sealed predictions.

`collapse_repeats` does not exist yet. Each of its test outputs is fingerprinted when it is produced,
and the scoring script checks every one before opening.

`evaluate_test.py` was run on validation data before the freeze. It reproduced the recorded validation
scores exactly (`camlds_encoder/out/STAGE1_DRYRUN_ON_VALIDATION.txt`). It refuses to open the test
unless `spec_1_2.py` passes, every training is present and intact, and no result exists yet.
