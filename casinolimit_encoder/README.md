# casinolimit_encoder

TEMARL's encoders (the CAM-LDS final design) on CasinoLimit, a second dataset of 114 real human
attackers. Everything for this study runs from this folder and saves into `out/`.

The rules are in [PROTOCOL_CL_1.0.md](PROTOCOL_CL_1.0.md): approved and frozen on 2026-11-12, before
any training. `spec_cl.py` pins every file it depends on; nothing runs if one changes.

## Step 1: train (GPU PC)

```
python casinolimit_encoder/run.py --stage all --device cuda
```

One command does everything: check → pilot → 400 trainings → lookup baseline → validation summary
(about 10 hours). If it stops, run the same command again: finished trainings are kept.
Then commit and push `casinolimit_encoder/out`.

## Step 2: score (this PC, after pulling)

```
python casinolimit_encoder/evaluate.py --validation-dry-run    # validation only; must PASS
python casinolimit_encoder/evaluate.py --open-test             # once; results in out_test/
```

| Other commands | |
|---|---|
| `--stage check` | split and data checks only (seconds) |
| `--stage all --smoke --device cpu` | whole pipeline with tiny budgets (about 2 minutes); NOT a result |
| `python -m unittest discover -s casinolimit_encoder/tests` | tests |

## Files

| file | what it does |
|---|---|
| `cl_port.py` | loads the frozen encoder code through `camlds_encoder/port.py` (hash-checked), sets 66 labels |
| `cl_split.py` | the 5 folds (no randomness) |
| `cl_data.py` | windows (frozen window code), copy/novel marks |
| `lookup.py` | the lookup-table baseline |
| `run.py` | all training stages |
| `evaluate.py` | dry run on validation, then the one-time test scoring |
| `spec_cl.py` | the frozen file hashes (PASS / FAIL) |

No file of `camlds_encoder/`, `camlds_real/` or `Temarl_Test_v1_L1/` is changed.

## Where results are saved (`out/`)

| path | content | committed |
|---|---|---|
| `split.json` | the folds and their sizes | yes |
| `pilot/<model>/<fold>_s<seed>.json` | pilot curves | yes |
| `budget.json` | chosen patience and update budget | yes |
| `train/<condition>/<model>/<fold>/s<seed>/result.json` | validation scores, threshold, hashes | yes |
| `train/.../test_logits.npy` | sealed test outputs | yes |
| `train/.../val_logits.npy` | validation outputs (for the dry run) | yes |
| `train/.../encoder.pt` | checkpoint | no: stays on the GPU PC |
| `lookup/<condition>/<fold>/` | lookup predictions (test sealed) | yes |
| `VALIDATION_SUMMARY.txt` | validation scores, descriptive | yes |
| `../out_test/CL_RESULTS.*` | the test results (Step 2) | yes |
