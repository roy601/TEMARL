# Protocol CL 1.0: TEMARL's encoders on CasinoLimit

**Status: DRAFT, 2026-11-12. Not approved.** Until it is approved, `run.py` allows only `--stage check`
and `--smoke` runs. Approval = the user says so; then `cl_split.APPROVED_ON` is set in a commit.

Part A (Sections 1–6) must be approved **before any real training**.
Part B (Section 7) must be frozen, with the evaluation code and file hashes, **before any test score**.

## 1. Questions

1. **Main:** do the encoders predict the next step of an *unseen human attacker* better than a lookup table?
2. Is the Transformer different from the GRU and the LSTM? (as in CAM-LDS protocol 1.2)

Nothing is designed or tuned on CasinoLimit. Every model choice was fixed on CAM-LDS before
CasinoLimit was used. CasinoLimit only tests whether those results hold on a second, independent
dataset.

## 2. Data and split

- Corpus: `casinolimit_real/out/steps.jsonl` (SHA-256 after CRLF→LF
  `399ef563db0223a5fe85d8668ed6fce925fbd43240f79ef7c9b0bc9cbe823c2d`): 114 attackers, 8,201
  commands, 66 techniques. `cl_port.py` refuses to run if the file changes.
- Conditions: **main** (all commands), and **collapse_repeats** (only the first run of each
  repeated command with the same labels: 4,990 commands), as in CAM-LDS.
- Unit: one attacker. An attacker is never split across training, validation and test.
- 5 folds, no randomness (`cl_split.py`): attackers are sorted by length (longest first, ties by
  name) and dealt to F1–F5 in snake order, so every fold gets long and short attacks.
- For test fold Fi: validation = the next fold (F5 → F1), training = the other 3 folds.
  Every attacker is tested exactly once.
- Window W = 16, the frozen window code. Every command except an attacker's first is a prediction point.

| fold | attackers test/val/train | points test/val/train (main) |
|---|---|---|
| F1 | 23 / 23 / 68 | 1,749 / 1,678 / 4,660 |
| F2 | 23 / 23 / 68 | 1,678 / 1,576 / 4,833 |
| F3 | 23 / 23 / 68 | 1,576 / 1,581 / 4,930 |
| F4 | 23 / 22 / 69 | 1,581 / 1,503 / 5,003 |
| F5 | 22 / 23 / 69 | 1,503 / 1,749 / 4,835 |

## 3. Models (code unchanged; only the label count is 66)

| name | what it is | role |
|---|---|---|
| `allpos` | frozen Transformer + all-position loss (final CAM-LDS design) | main encoder |
| `gru_allpos`, `lstm_allpos` | frozen GRU / LSTM + all-position loss | compared with the Transformer |
| `baseline` | frozen Transformer, last-position loss | descriptive only |

## 4. Lookup baseline (no training)

From the 2026-11-11 audit (`lookup.py`), built from the training attackers only:
- **longest match:** the label set that most often followed the longest matching run of recent steps;
- **previous step:** the same with only the last step.

For each fold, the **lookup baseline is whichever of the two has the higher validation micro-F1**,
so the encoders are compared with the stronger rule. *Disclosure:* this rule was written after the
smoke run had shown validation micro-F1 for folds F1–F2: longest 0.237 / 0.243, previous 0.278 /
0.303 (main). No encoder result had been seen.

## 5. Training (the frozen rules of `Temarl_Test_v1_L1/study_spec.py`, as for CAM-LDS)

- Pilot: seeds 101–103 × 5 folds × the 4 models, main condition, to a cap of
  max(8,192, 300 epochs) updates with full validation curves. One shared patience (grid 16/32/64
  checks) and one shared update budget (1.25 × the largest median best update) are chosen by the
  frozen functions, from validation curves only. Both conditions use them.
- Main: seeds 0–9 × 5 folds × 4 models × 2 conditions = 400 trainings. Batch 32, learning rate
  5e-4, validation every 64 updates, validation-best checkpoint, threshold from {0.1 … 0.5}
  maximising validation micro-F1.
- Expected time on the RTX 4080 SUPER: about 10 hours. The run can be stopped and continued.

## 6. Sealing

Test outputs (`test_logits.npy`, lookup `test_*.npy`) are saved with their SHA-256 in `result.json`
and are **not scored** until Part B is frozen. Validation scores are descriptive only
(`out/VALIDATION_SUMMARY.txt`); nothing is selected on them except the threshold, the checkpoint
and the lookup rule above.

## 7. Part B, evaluation (DRAFT: to be frozen before the test is opened)

- **Unit of comparison: the attacker.** Five folds are too few for a test (a Wilcoxon test on 5 pairs
  cannot reach p < 0.05). Per attacker: micro-F1 over that attacker's test points, averaged over the
  10 seeds. Attackers with no prediction point are left out (1 attacker).
- **Primary metric:** micro-F1. Reported on all points, novel points and copy points (a copy point =
  the same window and target occur in the fold's training or validation attackers; as CAM-LDS).
  Secondary: macro-F1, BCE.
- **Family 1, main question:** `allpos`, `gru_allpos` and `lstm_allpos` each vs the lookup baseline
  (3 comparisons). **Family 2:** Transformer vs GRU, Transformer vs LSTM (2 comparisons).
- Per comparison: mean difference over attackers, 95% bootstrap CI (10,000 resamples of attackers,
  seed 20261103), two-sided Wilcoxon signed-rank (scipy), Holm correction within each family.
  "Better" needs Holm p < 0.05 and a CI above 0. Otherwise: "no difference shown".
- Both conditions are reported. Main is primary.
- The test is opened once. No model is changed after.
