# Thesis version 2310: Is Markov augmentation useful?

**Confidence ablation now included by default:** see
[CONFIDENCE_PROTOCOL.md](CONFIDENCE_PROTOCOL.md). It adds 120 paired policy cells
at ten seeds, reusing the real-only encoder checkpoints. Results are linked from
`RESULTS.md` in `CONFIDENCE_RESULTS.md` and `CONFIDENCE_DETAILS.md`.
This increases runtime; previous estimates do not include the additional study.

Independent runnable copy of `thesis_version_2310`. The original folder was
not edited. No full research experiment has been run during construction.

**Architecture update:** LSTM now includes a forget gate. Read
[MODEL_EQUATION_REVIEW.md](MODEL_EQUATION_REVIEW.md) for equations, paper sources,
adaptations and review limitations. Old LSTM checkpoints/results are not this
architecture. Use a new output directory for fresh training; existing validation
reports describe the earlier code unless explicitly marked otherwise.

Read [STUDY_PROTOCOL.md](STUDY_PROTOCOL.md) for all scientific decisions and
[CHANGES_MARKOV_USEFUL.md](CHANGES_MARKOV_USEFUL.md) for implementation changes.
[VALIDATION_MARKOV.md](VALIDATION_MARKOV.md) records the completed checks and links sample reports.
Older documents retained here describe the original experiment; this README
and STUDY_PROTOCOL govern the new study.

| Test | Conditions / output |
|---|---|
| Transition sparsity | Bigrams, trigrams, singleton transitions, held-out support gaps |
| Markov diagnostics | Order-0 vs order-1 likelihood, PPL, Top-1/3/5 |
| Original-data learning curve | 25%, 50%, 75%, 100% of training groups |
| Augmentation curve | Original data + 25%, 50%, 100%, 200% synthetic sequences |
| Training-effort control | Repeated original windows matching each augmentation dose |
| Quality | Length, duplicates, observed transitions, divergence; AEP = N/A |
| Prediction | Transformer, GRU, LSTM; ten seeds; one shared epoch budget |
| Deception | IPPO/MAPPO for all three encoders at real/Markov-100/repeat-100 |

Generator: **scenario-conditioned first-order categorical Markov chain**, with
inherited floor 0.02, bigram weight 4 and initial weight 2. Fit on training runs
only. Test on original held-out playbook sequences. Smoothing does not ensure
that generated paths are operationally valid.

## How many epochs?

`--epochs auto` runs real-only pilots for all three encoders and three pilot
seeds up to 100 epochs. It takes the largest validation-best epoch as one common
budget for all main conditions. Main training starts fresh and completes every
epoch. Primary tests and downstream encoders use the final common epoch;
validation-best checkpoints are reported separately. A cap warning means
convergence is uncertain. `--epochs 50` instead forces 50 for every main condition;
50 is an example, not a proven sufficient budget.

Same epochs with more data mean more updates. Repeat controls match augmented
windows and optimizer updates without adding information. PPO epochs per rollout
are a separate quantity and remain equal across RL arms.

## Lab GPU run

Copy this entire folder. In PowerShell opened at its root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_lab.ps1
```

This creates a local Python 3.12 environment, installs CUDA PyTorch 2.10.0 and
requirements, verifies GPU availability, runs tests and a smoke check, and starts
the full experiment in the foreground. Keep the terminal and PC awake.
CUDA installation follows the [official PyTorch instructions](https://pytorch.org/get-started/previous-versions/).

```powershell
# Setup and smoke only, no full training
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_lab.ps1 -SmokeOnly
# Exactly 50 main epochs, skipping the selection pilot
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_lab.ps1 -Epochs 50
# CPU smoke if needed
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_lab.ps1 -Device cpu -SmokeOnly
```

Already prepared environment:

```powershell
python -B -m unittest test_markov_study -v
python -B run_markov_study.py --smoke --device cuda --output results_markov\smoke_gpu
python -B -u run_markov_study.py --device cuda --epochs auto --threads 4
```

Default full workload: nine pilots, 360 encoder cells and 200 policy cells.
Runtime depends on hardware and selected epochs; old experiment timing does not
apply. `--prediction-only` skips downstream RL; use a different output folder.
The familiar `run_experiment.py` command also delegates to this new study.

## Human-readable results

Default full output: `results_markov/main/`.

| File | Contents |
|---|---|
| RESULTS.md | Main tables, statistical evidence, quality, six combinations and ablation |
| EPOCH_RESULTS.md | Every completed pilot/main epoch: loss, accuracy, F1, PPL and updates |
| DETAILED_RESULTS.md | Every completed seed and original test run; RL episode outcomes |
| PREDICTION_EXAMPLES.md | Technique names, true next technique, top-three probabilities |
| RL_LEARNING_CURVES.md | Every RL validation point and selected update |
| audit.json | Source hash, exact split membership, support gaps and similarity |
| epoch_selection.json | Shared budget, pilot selections and cap warning |
| synthetic/ | Generated paths and their training-run provenance |
| prediction/ and rl/ | Individual cell JSON and saved model checkpoints |

The main report links all detailed Markdown files. Pending cells are shown as
Pending. Smoke results are marked NOT THESIS EVIDENCE. Regenerate without training:

```powershell
python -B report_markov_study.py results_markov\main
```

Optional separate LOSO fold (repeat S1 through S7 for the much larger full LOSO):

```powershell
python -B -u run_markov_study.py --held-out S1 --device cuda --output results_markov\loso_S1
```

Rerun the same command to resume completed cells. Interrupted cells restart;
completed cells require matching code/config/checkpoint hashes. A crash may leave
`.running`; check the recorded process before removing a stale lock manually.
Changed code/config requires new output. The source is a small derived playbook
corpus and the environment is fixed five-zone. Neither new real-world incidents
nor longer than 16-token model contexts are created by this change.
