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

## Files

| File | Purpose |
|---|---|
| `port.py` | Imports the frozen modules, checks their hashes, sets 81 labels |
| `data.py` | Folds, train/validation/test runs, windows; returns test inputs only |
| `run.py` | Stages `check`, `pilot`, `train` |
| `summarise.py` | Integrity checks and validation summary of the baseline run |
| `variants.py` | `baseline`, `causal`, `allpos`, `repeat`; the training loop is the frozen one with only the loss line changed |
| `run_variants.py` | Stages `baseline_val`, `train --variant` |
| `compare_validation.py` | Applies `SELECTION_RULE.md` |
| `tests/` | 22 tests: `python -m unittest discover -s camlds_encoder/tests` |
