# Independent audit of the CAM-LDS encoder study

**Date: 2026-11-11. Scope: the dataset, preprocessing, training, selection and Stage 1 test results
(`camlds_real/`, `camlds_encoder/`, protocols 1.0 to 1.2). Not in scope: MAPPO and the Kuwano comparison,
which have not been run on this dataset.**

Evidence: `AUDIT_OUTPUT.txt` (from `independent_audit.py`) and `LOOKUP_ON_VALIDATION.txt` (from
`lookup_on_validation.py`). No project file was changed.

## Verdict

**The work is correct.** The data handling, training, model selection and published test scores all
reproduce, and no error or data leak was found. **The conclusions are valid only as narrowly as the
study states them**, and one important comparison is missing (finding 1).

## What was checked

| # | Check | Result |
|---|---|---|
| 1 | Our label file against the authors' file on GitHub (commit `42bbd2c`) | Byte-identical |
| 2 | Sequences, labels and repeat marks rebuilt from the CSV with new code | Equal to `steps.jsonl` and `vocab.json` (904 steps, 34 runs, 81 labels) |
| 3 | Folds rebuilt from the written rule | 29 + 3 folds; train, validation and test runs never overlap |
| 4 | Model inputs and targets rebuilt with new code | Bit-identical to the project's arrays (26,206 windows) |
| 5 | Copy and repeat marks | Equal on all 2,212 points; 425 of 790 copies (53.8%) |
| 6 | All 2,240 trainings: threshold, stopping point, seeds | Each threshold is the validation-best one; each run stopped where the rule says; no seed reused |
| 7 | Stage 1 test scores recomputed with new metric code | Equal to the published file (largest difference 1e-16) |
| 8 | Statistics recomputed, with an exact Wilcoxon test | Same means and intervals; exact Holm p = 0.082; "no difference shown" stands |
| 9 | Rules written before results | Every design and rule was committed before its results; the keep-or-reject rule never changed; no frozen file changed after the freeze |
| 10 | Built-in checks | Protocol 1.2, 1.1, 1.0 pass; 103 tests pass |

29 of 29 independent checks passed.

## Not re-checked here

- **The 49 GB of raw logs.** They are on the GPU PC only. This audit relies on the committed scan record
  (`camlds_real/out/scan/`). No model reads the logs.
- **The training runs themselves.** The saved models are on the GPU PC. Their recorded outputs are
  consistent in every way that can be checked here.
- **Blinding.** File fingerprints prove the sealed test outputs were not changed. They cannot prove that
  nobody looked at them early; that rests on the procedure.

## Findings

| # | Finding | Severity | What to do |
|---|---|---|---|
| 1 | **A lookup table does almost as well as the neural models, on validation.** With no training, it predicts the label set that followed the longest matching run of recent steps in the training runs. Novel points, variant folds: lookup 0.802, Transformer 0.819, GRU 0.830, LSTM 0.835. The Transformer beats it in 10 of 29 folds. This baseline is in no protocol and has not been run on the test split | **Important** | Declare it as an added baseline (protocol 1.3) and report it with Stage 2. Until then, do not claim the neural encoder is needed |
| 2 | **The published recall ceiling is slightly off.** It counts each run's first step, which is never predicted, and counts labels in validation runs as seen. Corrected: S2 0.774 (published 0.781), S3 0.661 (0.686), S6 0.419 (0.412), variant mean 0.966 (0.973) | Minor | Report the corrected values. No score changes |
| 3 | **The 29 folds are not independent** (18 are S1, sharing training runs), so the p-values are approximate | Known, stated in 1.0 | Keep reporting per scenario |
| 4 | **The headline depends on weighting.** Fold mean 0.861; with S1, S3 and S6 weighted equally it is 0.788 (novel 0.730) | Known, stated in 1.2 | Report both |
| 5 | **No reference point on the test yet.** Without Stage 2 there is no baseline on the test split, so 0.80 cannot yet be called good or bad | Open | Run Stage 2 |

## What the thesis may and may not claim (from this study)

**May claim:** on new variants of known attack campaigns, the encoder predicts the next step's
techniques with micro-F1 0.861 (0.798 on steps that cannot be memorised); the Transformer, GRU and LSTM
perform alike; the result does not depend on repeated steps.

**May not claim:** that the Transformer is better than GRU or LSTM; that the model works on unseen
campaigns (0.00 to 0.21); that the neural encoder beats a simple lookup (untested on the test split);
anything about raw logs, real attackers, or deception performance (MAPPO has not been run here).
