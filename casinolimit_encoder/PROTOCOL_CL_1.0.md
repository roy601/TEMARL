# Protocol CL 1.0: TEMARL's encoders on CasinoLimit

**Status: APPROVED by the user and FROZEN on 2026-11-12, before any real training.**
Both the training plan (Sections 1–6) and the evaluation (Section 7) are fixed now, before any model
is trained on CasinoLimit. `spec_cl.py` records the SHA-256 of every file this depends on; `run.py`
and `evaluate.py` refuse to run if one changes. A change means a new protocol version (CL 1.1),
never an edit of this one.

## 1. Questions

1. **Main:** do the encoders predict the next step of an *unseen human attacker* better than the best
   simple baseline?
2. Is the Transformer different from the GRU and the LSTM? (as in CAM-LDS protocol 1.2)

Nothing is designed or tuned on CasinoLimit. Every model choice was fixed on CAM-LDS before
CasinoLimit was used. CasinoLimit tests whether those results hold on a second, independent dataset
of real human attackers.

## 2. Data and split

- Source: CasinoLimit (Kilian et al., RAID 2025), Zenodo 10.5281/zenodo.17256954, CC BY 4.0; files
  checked against the published md5. Each label is placed in time by finding its auditd events in
  the raw logs (`dataset_survey/casinolimit_steps.py`: 9,243 of 9,243 labels placed).
- Corpus: `casinolimit_real/out/steps.jsonl` (SHA-256 after CRLF→LF
  `399ef563db0223a5fe85d8668ed6fce925fbd43240f79ef7c9b0bc9cbe823c2d`): 114 attackers, 8,201
  commands, 66 techniques. A command = the labels on one auditd event (multi-label, as in CAM-LDS).
- Conditions: **main** (all commands; primary), and **collapse_repeats** (a re-run of the same command
  with the same labels is dropped: 4,990 commands), as in CAM-LDS.
- Unit: one attacker. An attacker is never split across training, validation and test.
- 5 folds, no randomness (`cl_split.py`): attackers sorted by length (longest first, ties by name),
  dealt to F1–F5 in snake order. For test fold Fi: validation = the next fold (F5 → F1), training =
  the other 3. Every attacker is tested exactly once.
- Window W = 16 (frozen window code). Every command except an attacker's first is a prediction point.

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
| `allpos` (Transformer) | frozen Transformer + all-position loss (final CAM-LDS design) | main encoder |
| `gru_allpos`, `lstm_allpos` | frozen GRU / LSTM + all-position loss | compared with the Transformer |
| `baseline` (Old Transformer) | frozen Transformer, last-position loss | descriptive only |

The encoder code is loaded through `camlds_encoder/port.py`, which checks the SHA-256 of TEMARL's
frozen modules; `cl_port.py` only sets the label count to 66.

## 4. Simple baselines (no training)

Built from the fold's training attackers only (`lookup.py`):
- **lookup, longest match:** the label set that most often followed the longest matching run of
  recent steps (the rule of the 2026-11-11 audit);
- **lookup, previous step:** the same with only the last step;
- **repeat last step:** predict the last step's labels again.

For each fold, the **best simple baseline** is the rule with the highest validation micro-F1 (ties:
the order above). It is the comparator of question 1, so the encoders face the strongest simple rule.

*Disclosure (order of events):* the two lookup rules were in the first draft. A smoke run then showed
their validation micro-F1 on folds F1–F2 (main: longest 0.237 / 0.243, previous 0.278 / 0.303).
"Repeat last step" and the "best of the rules on validation" choice were then added, before
repeat last's numbers were seen; the next smoke run showed them (0.288 / 0.369). No encoder result
(other than meaningless 128-update smoke trainings) had been seen at any point.

## 5. Training (the frozen rules of `Temarl_Test_v1_L1/study_spec.py`, as for CAM-LDS)

- Pilot: seeds 101–103 × 5 folds × the 4 encoders, main condition, to a cap of max(8,192, 300
  epochs) updates with full validation curves. One shared patience (grid 16/32/64 checks) and one
  shared update budget (1.25 × the largest median best update) are chosen by the frozen functions,
  from validation curves only. Both conditions use them.
- Main: seeds 0–9 × 5 folds × 4 encoders × 2 conditions = 400 trainings. Batch 32, learning rate
  5e-4, weight decay 0.01, validation every 64 updates, validation-best checkpoint, threshold from
  {0.1, 0.2, 0.3, 0.4, 0.5} maximising validation micro-F1 (ties: the smallest).
- One command on the GPU PC (`run.py --stage all`), about 10–12 hours, resumable.

## 6. Sealing

Test outputs are saved with their SHA-256 in `result.json` and are not scored until Section 7 runs.
Validation scores are descriptive (`out/VALIDATION_SUMMARY.txt`). Nothing is chosen on validation
except the checkpoint, the threshold, and the best simple baseline (Section 4).

## 7. Evaluation (`evaluate.py`, frozen now)

1. **Dry run first** (`--validation-dry-run`): the scorer is run on the validation outputs and must
   reproduce every validation micro-F1 recorded at training time. No test file is read.
2. **Open the test once** (`--open-test`): refuses unless the frozen files are unchanged, the dry run
   passed, all 400 trainings and all baseline outputs exist, and the test was never opened. Every test
   file's SHA-256 and point order are checked before scoring. Results: `out_test/`.

- **Unit of comparison: the attacker.** Five folds are too few for a test (a Wilcoxon test on 5
  pairs cannot reach p < 0.05). Per attacker: micro-F1 over that attacker's test points, averaged
  over the 10 seeds. Attackers without points in a subset are left out of that subset.
- **Primary result:** main condition, all points, family 1. **Metric:** micro-F1.
- **Subsets:** all points; novel and copy points (copy = the same window and target occur in the
  fold's training or validation attackers; as CAM-LDS); **reviewed points** (every label of the
  target command was labelled by a CasinoLimit reviewer, none automatic, none marked "doubt"),
  to show the result does not depend on the automatic labels.
- **Secondary metrics:** pooled micro-F1 (mean over seeds), macro-F1, exact-set accuracy, BCE
  (encoders only), with TEMARL's frozen metric code; the recall ceiling (label slots whose label
  occurs in the fold's training attackers).
- **Family 1:** Transformer, GRU, LSTM each vs the best simple baseline (3 comparisons).
  **Family 2:** Transformer vs GRU, Transformer vs LSTM (2 comparisons).
- Per comparison: mean difference over attackers, 95% bootstrap CI (10,000 resamples of attackers,
  seed 20261103), two-sided Wilcoxon signed-rank (scipy, zero differences dropped), Holm correction
  within each family and each (condition, subset) table. "X outperforms Y" only if Holm p < 0.05 and
  the CI excludes 0; otherwise "no difference shown". The Old Transformer is descriptive only.
- Every result is reported, whatever its direction. The test is opened once; no model or rule changes
  after.

## 8. Known limits (stated in any write-up)

- One CTF challenge: every attacker faces the same network, so this is generalisation to new
  attackers, not to new networks.
- 5,060 of 9,243 labels come from CasinoLimit's automatic rules (the reviewed subset addresses this).
- Repeats for `collapse_repeats` are judged on the masked command text (long tokens such as URLs
  become `<token:N>`), so two different long commands of equal length can count as one.
- Only 12 labels are on the intranet machine; 48 of 114 attackers stay on one machine.
