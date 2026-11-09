# camlds_encoder: TEMARL's encoder on CAM-LDS (precondition B2)

**What it is.** The Transformer encoder the thesis proposes, from `Temarl_Test_v1_L1/`, run on the
CAM-LDS corpus (`camlds_real/`).

**What changed: only the label count, from 84 to 81.** The code is imported, not copied. `port.py`
checks the SHA-256 of every reused module before anything runs, and a test proves that the trunk is
the same size with 84 or 81 labels.

**What it uses, all frozen:**

- **Folds:** split protocol 1.0 minus the 2 excluded S2 folds, so 32 folds.
- **Validation runs:** the 1.0 rule.
- **Window:** 16 steps.
- **Labels:** the 81 pinned in protocol 1.1.
- **Training rules:** BCE, validation-best checkpoint and threshold, from `study_spec.py`.

**Blinding.** No test score is computed anywhere here. Test outputs are saved and hashed (sealed),
and are scored only after the design is frozen as protocol 1.2.

## Run on the GPU PC

```
git pull
python camlds_encoder/run.py --stage check
python camlds_encoder/run.py --stage pilot --device cuda
python camlds_encoder/run.py --stage train --device cuda
```

| Stage | What it does | Expected time (RTX 4080 SUPER, from the old study's measured speed) |
|---|---|---|
| `check` | Verifies every pinned file; test points match protocol 1.1 | under a minute |
| `pilot` | 32 folds × 3 seeds, trained to a cap; chooses patience and update budget from **validation** curves | about 1 hour |
| `train` | 32 folds × 10 seeds = 320 trainings; validation scores; sealed test outputs | up to about 2 hours |

- **Interrupted?** Run the same command again. Finished trainings are skipped.
- **"Locked by" error?** Another run is using the folder. If none is, delete `camlds_encoder/out/.running`.
- **When finished,** commit and push `camlds_encoder/out/`. Git ignores the `encoder.pt` checkpoints:
  **keep them on the GPU PC**, because MAPPO needs them later.

## Improvement 1 (validation only): training at every position

The rule for keeping an improvement was fixed before any variant ran: `SELECTION_RULE.md`.

```
git pull
python camlds_encoder/run_variants.py --stage baseline_val --device cuda
python camlds_encoder/run_variants.py --stage train --variant causal --device cuda
python camlds_encoder/run_variants.py --stage train --variant allpos --device cuda
```

| Stage | What it does | Expected time |
|---|---|---|
| `baseline_val` | Reloads the 320 baseline checkpoints, saves their validation outputs, checks they reproduce the recorded validation loss | a few minutes |
| `train --variant causal` | Control: causal attention, loss on the last position only. 320 trainings | about 1.3 hours (like the baseline) |
| `train --variant allpos` | Causal attention, loss at every position. 320 trainings | about 1.3 hours, maybe more |

Then commit and push `camlds_encoder/out/` as before. `compare_validation.py` then applies the rule
on this PC.

**Result (2026-11-08): `allpos` kept.** It is now the design every later candidate must beat.

## Improvement 2 (validation only): repeat/new split

`allpos` plus a separate output layer for techniques already seen in the window (RepeatNet). The
exact design is declared in `SELECTION_RULE.md`.

```
git pull
python camlds_encoder/run_variants.py --stage train --variant repeat --device cuda
```

| Stage | What it does | Expected time |
|---|---|---|
| `train --variant repeat` | 320 trainings, like `allpos` | about 1.6 hours (`allpos` took 98 minutes) |

Then commit and push `camlds_encoder/out/`. The comparison is
`compare_validation.py --candidate repeat --current allpos`.

**Result (2026-11-08): `repeat` rejected.** The design stays `allpos`.

## Improvement 3 (validation only): Asymmetric Loss

`allpos` with BCE replaced by the Asymmetric Loss (Ridnik et al., ICCV 2021), the authors' settings.
The exact design, and a known risk, are declared in `SELECTION_RULE.md`.

```
git pull
python camlds_encoder/run_variants.py --stage train --variant asl --device cuda
```

| Stage | What it does | Expected time |
|---|---|---|
| `train --variant asl` | 320 trainings, like `allpos` | about 1.6 hours |

Then commit and push `camlds_encoder/out/`. The comparison is
`compare_validation.py --candidate asl --current allpos`.

**Result (2026-11-08): `asl` rejected** (no benefit shown under the frozen budget and threshold
grid; see `SELECTION_RULE.md`). The design stays `allpos`.

## Improvement 3, second run (validation only): ASL with a larger budget

`asl_long` repeats `asl` with 18,304 updates instead of 9,152. It is a second chance decided after
the first result, and the only rerun ASL gets. See `SELECTION_RULE.md`.

```
git pull
python camlds_encoder/run_variants.py --stage train --variant asl_long --device cuda
```

| Stage | What it does | Expected time |
|---|---|---|
| `train --variant asl_long` | 320 trainings | up to about 7 hours (the first run took about 3.5) |

Then commit and push `camlds_encoder/out/`. The comparison is
`compare_validation.py --candidate asl_long --current allpos`.

**Result (2026-11-09): `asl_long` rejected.** ASL is closed. The final design is `allpos`.

## Secondary encoders (validation only): GRU and LSTM

The frozen GRU and LSTM, trained the same way as `allpos`. They are reported beside the Transformer
and never replace it. The exact design is declared in `SELECTION_RULE.md`.

```
git pull
python camlds_encoder/run_variants.py --stage train --variant gru_allpos --device cuda
python camlds_encoder/run_variants.py --stage train --variant lstm_allpos --device cuda
```

| Stage | What it does | Expected time |
|---|---|---|
| `train --variant gru_allpos` | 320 trainings | not yet measured on the GPU; about 4 to 5 hours if the CPU speed ratio holds |
| `train --variant lstm_allpos` | 320 trainings | the same |

Then commit and push `camlds_encoder/out/`.

## Protocol 1.2: `collapse_repeats`, then Stage 1

The design is frozen in `idea01_kuwano/PROTOCOL_1.2.md`. Check: `python idea01_kuwano/spec_1_2.py`.

```
git pull
python camlds_encoder/run_variants.py --stage train --variant allpos --condition collapse_repeats --device cuda
python camlds_encoder/run_variants.py --stage train --variant gru_allpos --condition collapse_repeats --device cuda
python camlds_encoder/run_variants.py --stage train --variant lstm_allpos --condition collapse_repeats --device cuda
```

| Stage | Trainings | Expected time (from the main condition) |
|---|---|---|
| `allpos` | 320 | about 1.6 hours |
| `gru_allpos` | 320 | about 6 hours |
| `lstm_allpos` | 320 | about 3.8 hours |

Then commit and push `camlds_encoder/out/`. Stage 1 is opened once, on this PC, with
`python camlds_encoder/evaluate_test.py --open-test`.

## Files

| File | Purpose |
|---|---|
| `port.py` | Imports the frozen modules, checks their hashes, sets 81 labels |
| `data.py` | Folds, train/validation/test runs, windows; returns test inputs only |
| `run.py` | Stages `check`, `pilot`, `train` |
| `summarise.py` | Integrity checks and validation summary of the baseline run |
| `variants.py` | `baseline`, `causal`, `allpos`, `repeat`, `asl`, `asl_long`, `gru_allpos`, `lstm_allpos`; the training loop is the frozen one with only the loss line changed |
| `run_variants.py` | Stages `baseline_val`, `train --variant` |
| `compare_validation.py` | Applies `SELECTION_RULE.md` |
| `diagnose_validation.py` | Explains a decision: error types, training length, thresholds |
| `evaluate_test.py` | Stage 1: scores the test split once, after the freeze. `--validation-dry-run` opens nothing |
| `tests/` | 66 tests: `python -m unittest discover -s camlds_encoder/tests` |
