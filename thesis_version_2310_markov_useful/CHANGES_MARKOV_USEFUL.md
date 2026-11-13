# Changes from thesis_version_2310

Source was only read/copied. Old results, lab results, environments and caches
were excluded. All frozen dependency hashes still pass.

| Area | Original | New controlled study |
|---|---|---|
| Estimator | Per-scenario first-order; floor .02; bigram weight 4; start weight 2 | Same function and constants |
| Fit data | All verified runs | Training runs only |
| Scenario sampling | Uniform over scenarios | Training-run-frequency mixture for augmentation |
| Length | Draw original lengths | Draw same-scenario training lengths only |
| Encoder data | Thousands of synthetic episodes | Original subsets, augmentation doses, repeat controls |
| Training unit | 3,000 random minibatch updates | True epochs: every prediction window once |
| Batch size | 256 | 64 shared across conditions for this small corpus |
| Optimizer | AdamW 5e-4, decay 1e-4, norm clip 1 | Unchanged |
| Epoch budget | Not defined as full passes | Validation-only pilot or explicit common count |
| Primary checkpoint | Final fixed minibatch update | Final shared epoch; validation-best separately reported |
| Validation/test | Synthetic episodes | Held-out original ordered playbook sequences |
| Splits | Episode streams / scenario exclusion | Duplicate-group splits before windowing/generation |
| Controls | NoHistory | NoHistory plus exact window/update-matched original-repeat controls |
| RL source | Implicit corpus-fitted Markov stream | Explicit finite original or augmented training corpus |
| RL evaluation | Markov-generated episodes | Exact original replay, matched environment repeats |
| RL models/budget | IPPO/MAPPO, 4 shared agents | Same architectures, environment steps and PPO epochs |
| Environment | Fixed five-zone coordinated engagement | Same dynamics, actions, reward, payoff, config |
| Encoders | Transformer, Cho GRU, 1997 LSTM adaptations | Transformer/GRU unchanged; LSTM subsequently upgraded to standard forget-gate LSTM, with separate capacity matching. See MODEL_EQUATION_REVIEW.md. |
| Vocabulary | 84 parent-technique IDs | Unchanged; unknown source tokens fail loudly |
| Reporting | Old comparison tables | Epochs, doses, paired CI/Holm, per-run results, predictions |
| Generalization | Scenario setting | Main variant holdout; optional separate LOSO folds |

## Files

- `markov_data.py`: source audit, splits, sampling, metrics and replay sources.
- `markov_training.py`: epochs, validation selection, probabilities/checkpoints.
- `run_markov_study.py`: pilot, manifest, resume, encoder and deception runs.
- `report_markov_study.py`: all Markdown reports and statistical tests.
- `test_markov_study.py`: focused integrity and training-path tests.
- `run_lab.ps1`: setup, CUDA checks, unit tests, smoke and full run.
- `mappo.py`: adds optional explicit training source and validation/test specs;
  old defaults remain compatible. No policy/reward update is changed.
- `run_experiment.py`: old CLI now delegates to the new study.
- `README.md`: new instructions; original saved as README_ORIGINAL_REFERENCE.md.
- `requirements.txt`: PyTorch pinned to 2.10.0; build selected at installation.

No changes make the encoders large language models or extend the 16-token window.
The new study measures usefulness; it does not guarantee a favorable result.
Markov-augmented RL changes both encoder data and policy training episodes, so
that comparison is a full-system effect. Historical corpus-informed vocabulary,
payoff, goals and environment calibration remain an explicitly reported limitation.
No AEP dependency validator is bundled; its result is N/A, never a fabricated score.
