# Protocol 1.1: amendment to protocol 1.0

**Status: approved 2026-11-07. It is frozen by the commit that adds it, and that commit must be
pushed before any test result is opened.** Constants: `idea01_kuwano/spec_1_1.py`. Check:
`python idea01_kuwano/spec_1_1.py`.

Protocol 1.0 (`PROTOCOL.md`, `spec.py`) and split protocol 1.0 (`camlds_real/split_spec.py`) stay in
force and are not edited. This file only adds to them. No test result exists for our model: it has
never been run on this corpus.

## 1. Why

The full dataset check (`camlds_real/DATASET_REPORT.md`) found that a single overall score can mislead:

- **53.8%** of the primary family's test points are exact copies of a point the model has seen.
- **48.4%** of their target labels already appear in the 16-step window.

A model can score well by memorising or repeating. 1.1 adds the reporting that separates these cases.
It also defines two things 1.0 required but left undefined.

## 2. What is added

| # | Item | Rule |
|---|---|---|
| A1 | **Copy or novel** (new) | A test point is a **copy** when the same 16-step window and the same target occur at a prediction point of a run the fold does not test (training or validation). Otherwise it is **novel**. Every metric is reported on all, novel and copy points |
| A2 | **Repeat or new** (new) | A target label is a **repeat** when it occurs anywhere in the 16-step window, otherwise **new**. Micro-F1 is reported separately for each group. A predicted label goes in the group its window decides, exactly like a target label |
| A3 | **`collapse_repeats`** (required by 1.0, defined here) | Keep the first execution of each (run, event_id): `occurrence == 1`, 883 steps. The whole pipeline (train, select, test) is rerun on it with the 1.0 rules, and reported beside the main result, never instead of it |
| A4 | **Label list** (required by 1.0, pinned here) | `camlds_real/out/vocab.json`, key `parent_techniques`: 81 labels, sorted. Output index = position in the list. Every model uses it |
| A5 | **Order** (unchanged) | Ascending CSV `start`, as in 1.0. Stated limitation: it differs from execution order in 4 runs (all S6), one neighbouring pair each, 4 of 870 transitions. No sensitivity run |
| A6 | **No time features** | No model uses timestamps, durations or time gaps. TiSASRec is not used: 47.9% of attack time is fixed scripted `sleep` |
| A7 | **Precondition B1 met** | Analysis repository commit `42bbd2cf8409f64a1e6c8fc936c91725e8c558b2` (`camlds_real/PROVENANCE.md` §2) |

## 3. Pinned files

SHA-256 after CRLF → LF. Rebuild with `python camlds_real/build_sidecar.py` (9 checks). Tests:
`python -m unittest discover -s camlds_real/tests` (13 tests).

| File | SHA-256 |
|---|---|
| `camlds_real/out/steps.jsonl` (unchanged) | `2d0886115d8082ef9dba5d2d001cd65f241ef5a84e4c0bf16d173e71fa0bff42` |
| `camlds_real/out/vocab.json` | `04e134e5d9b9b2d23909535e787e19732b0e43164ad72d1b2d9d0e519428f64c` |
| `camlds_real/out/sidecar/points.jsonl` | `de8f7c5de71bb9ef419f786e226b1028b7fa8fc22d7d1649fb532c8d8c7b969d` |
| `camlds_real/out/sidecar/steps_link.jsonl` | `1353136bf41d6f02f77c012568f25988182ec3a9c36d8e9751823cc999f593fa` |

## 4. Measured on the inputs (no model output)

| Condition | Family | Test points | Copies | Target labels | Repeats |
|---|---|---|---|---|---|
| Main | Variant held out (primary) | 790 | **425 (53.8%)**: S1 67%, S3 24%, S6 39% | 1,158 | 560 (48.4%) |
| Main | Scenario held out | 331 | 0 | 437 | 254 (58.1%) |
| `collapse_repeats` | Variant held out | 769 | 419 (54.5%) | 1,130 | 532 (47.1%) |
| `collapse_repeats` | Scenario held out | 322 | 0 | 421 | 238 (56.5%) |

The scenario-held-out family has no copies, so A1 matters only for the primary family there.

## 5. What does not change

Folds, exclusions, validation rule, window, label space, metrics, thresholds, seeds and the analysis in
1.0 Section 7. The primary test still uses all points. A1 and A2 are reported beside it.

## 6. Not decided here

Encoder changes (training at every position, a repeat/new head, Asymmetric Loss;
`report/TRANSFORMER_REVIEW.md`) are chosen on **validation data only**, then frozen as **protocol 1.2**
before any test result is opened. The GRU/LSTM decision is made then too, as 1.0 requires.

**Training count.** A3 reruns the pipeline, so the Transformer needs 320 trainings for the main
condition and 320 for `collapse_repeats`.
