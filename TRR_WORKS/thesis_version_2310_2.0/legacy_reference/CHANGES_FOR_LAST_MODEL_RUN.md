# Changes Made for the Latest Model Run

## 1. Scope of this record

This file records the changes used by `thesis_version_2310`, compared with the
preceding `temarl_marl` implementation. It separates newly changed code from
environment and data components that were deliberately retained.

The latest main experiment contains six requested combinations and two trained
controls:

| History encoder | IPPO | MAPPO |
|---|---:|---:|
| Transformer | Yes | Yes |
| GRU | Yes | Yes |
| LSTM | Yes | Yes |
| NoHistory control | Yes | Yes |

This is a sequence-model-assisted MARL experiment. The Transformer, GRU and
LSTM are compact ATT&CK-sequence encoders, not general-purpose large language
models.

## 2. CAM-LDS data changes

### What is used now

- The package includes `camlds_grounding_verified.json` locally.
- It contains 36 verified playbook runs from 7 CAM-LDS scenarios and 1,347
  ATT&CK-labelled technique steps.
- The verified file is included in the mandatory frozen-file integrity check.
- Its normalized SHA-256 is
  `20006361c0e6b6a46d9da02e67606cdaa0c3e375a4a0c7396c24484d1b88d7be`.
- Any verified technique outside the 84-technique vocabulary now causes a loud
  error. It can no longer be silently accepted as an unknown token.

### How it is connected to training

1. Runs are grouped by CAM-LDS scenario.
2. The initial-technique probabilities and first-order technique-transition
   probabilities are estimated separately for each scenario.
3. A scenario and run-length-derived horizon are sampled for every episode.
4. The environment generates an attack sequence from that scenario's smoothed
   Markov model.
5. The observed technique history is passed to the selected history encoder.
6. The resulting 64-dimensional history vector is supplied to the shared actor
   and to the appropriate critic.

### Data details intentionally retained

- Scenario entry zone, target zone and terminal tactic metadata still come from
  the older paper reconstruction in `camlds_grounding.json`.
- The actual technique chains and episode horizons come from the verified file.
- Scenario 4's firewall target remains mapped to its defended entry zone.
- Scenario 6 has no Exfiltration terminal technique in its verified runs, so its
  pre-declared fallback remains Collection.
- Markov smoothing, initial weighting and transition weighting remain as
  defined in `scripts_marl.py`.

### What the dataset does not represent

- These are AttackBed playbook sequences, not raw host or network logs.
- Training does not replay each playbook exactly.
- Generated Markov sequences may contain combinations that did not occur in one
  exact original run.
- The data does not prove that every playbook command succeeded on a real host.

### Data-related code corrections

- JSON files are opened with context managers so file handles close reliably.
- Verified runs are converted directly through `technique_to_id()` and checked
  against the valid technique range.
- The previous count of 1,339 was replaced by the current verified count of
  1,347. Tests enforce the new count.
- The verified data is bundled, so AttackBed does not need to be cloned on the
  lab PC to run the experiment.

## 3. Complex environment used in the run

The experiment uses the latest coupled engagement environment in `env_marl.py`.
That file is byte-identical to the preceding `temarl_marl` version; it was
retained rather than redesigned for this package.

### Network and defenders

- Five abstract zones: Internet, DMZ, LAN, User and Admin.
- Four defender agents: one each for DMZ, LAN, User and Admin.
- Internet is the attack entry area and does not have a defender agent.
- The topology has a fixed number of zones. It is not the earlier v3
  variable-size entity-topology experiment.

### Why the environment is complex

- Each defender receives partial local observations.
- Agents share a learned attack-history representation from the SIEM history.
- A capacity limit creates competition when too many decoys are active.
- Breadcrumb actions require coordination with a partner zone.
- An incomplete breadcrumb becomes a dead end and may expose the deception.
- Deception exposure is shared across the team and changes future engagement.
- Attacker objectives and future transitions are hidden from the defenders.
- Attack movement, technique transitions and decoy engagement are stochastic.
- The four agents act simultaneously at every decision step.

### Actions and payoff

- Each defender has six actions: no deployment plus five D3FEND-derived decoy
  action types.
- Engagement probability uses the frozen D3FEND technique-action payoff.
- A successfully engaged step increases dwell and records the technique for
  interaction depth.
- An engaged technique does not touch the real asset during that step.
- Team reward remains the number of engaged dwell steps.

### Environment configuration retained

| Setting | Value | Meaning |
|---|---:|---|
| `beta` | 0.2 | Base deception exposure/dead-end risk parameter |
| `p_goal` | 0.7 | Goal-directed attacker movement probability |
| `p_stay` | 0.8 | Attacker persistence/stay probability |
| `k_capacity` | 2 | Effective simultaneous decoy capacity |
| `goal_steps` | 1 | Required unengaged goal contact for objective completion |

The configuration, D3FEND payoff matrix, environment mechanics, reference
baselines, environment gates and original 27 environment tests are unchanged
from `temarl_marl`.

### Environment limitations preserved

- Movement is an abstract zone transition, not packet routing through a tested
  firewall graph.
- Probabilities are simulator assumptions rather than rates measured from live
  CAM-LDS network traffic.
- Asset protection means the configured attacker objective was not reached
  before the finite episode ended. It does not mean every host stayed clean.

## 4. Transformer changes

- The old Transformer-RoPE experimental arm was replaced for this comparison by
  a FlowTransformer-informed encoder using sinusoidal positional encoding.
- Architecture: 2 encoder layers, 4 attention heads, 64-dimensional token
  embeddings and a 128-dimensional feed-forward layer.
- Input is a rolling window of at most 16 ATT&CK technique IDs.
- The representation is taken from the last real token, not from padding.
- Padding after the declared sequence length is masked.
- Empty histories produce an exact zero history vector.
- The model predicts the next ATT&CK technique during pretraining.
- This adapts FlowTransformer ideas to ATT&CK sequences; it is not a reproduction
  of the paper's complete flow-based intrusion-detection framework.

## 5. GRU changes

- A custom GRU cell was implemented from Cho et al. (2014), equations 5-8.
- The reset gate is applied before the recurrent candidate transformation:
  `U(r * h)`.
- This avoids PyTorch GRU's documented reset-after calculation `r * U(h)`.
- The original update-gate interpolation is retained:
  `h_new = z*h + (1-z)*candidate`.
- Modern task adaptations are ATT&CK embeddings, stacked layers, dropout,
  LayerNorm, a 64-dimensional projection and AdamW/full BPTT training.

## 6. LSTM changes

- A custom LSTM cell was implemented from Hochreiter and Schmidhuber (1997).
- It uses input and output gates with a constant cell self-connection.
- It intentionally has no forget gate, matching the original architecture.
- The cell input uses `2*tanh(x/2)` and the cell output uses `tanh(c/2)`.
- Modern task adaptations are ATT&CK embeddings, stacked layers, dropout,
  LayerNorm, a 64-dimensional projection and full BPTT.
- Old checkpoints from a modern forget-gate LSTM are incompatible with this
  architecture and must not be reused.

## 7. Fair encoder comparison changes

- All three encoders now output the same 64-dimensional history vector.
- All use the same 84-technique vocabulary, 16-token window, prediction head,
  training data, optimizer recipe and validation split.
- GRU and LSTM width/layer count are selected to remain within 10% of the
  Transformer's trunk parameter count.
- Capacity calculation no longer consumes the model initialization random
  stream.
- True sequence lengths are enforced. Padding inside a declared real prefix is
  rejected, and data after the length is ignored.
- PAD and UNK logits are excluded from the next-technique cross-entropy because
  neither is a valid prediction target.
- The encoder is pretrained first, then frozen while PPO learns the deception
  policy. This prevents encoder-policy co-training instability.

## 8. IPPO and MAPPO design used

### Shared components

- Four agents share one actor network and receive an agent-ID feature.
- The actor uses local telemetry plus the selected history embedding.
- PPO clipping, generalized advantage estimation, entropy regularization,
  gradient clipping and value normalization are retained.
- Each encoder is tested with the same actor interface under both learners.

### IPPO

- Uses a local critic for each agent observation and history representation.
- Parameters are shared, but the critic cannot use other agents' private state.

### MAPPO

- Uses centralized training with a critic that receives global environment
  state, history and agent identity.
- Execution still uses the local shared actor.

### Controls

- `NoHistory + IPPO` and `NoHistory + MAPPO` are trained independently.
- NoHistory removes the shared sequence embedding but keeps local telemetry.
- A separate test-time `h=0` intervention is also recorded; it is not used as a
  substitute for the independently trained NoHistory controls.

## 9. Experiment design changes

- Added the missing `GRU + IPPO` and `LSTM + IPPO` arms.
- Added both NoHistory controls.
- Main study: 8 configurations x 10 seeds = 80 training cells.
- Each cell requests 2,000,000 environment steps.
- Complete 4,096-step rollouts give 1,998,848 actual training steps per cell.
- Each trained cell is tested on 500 deterministic episode specifications.
- Separate deterministic random streams are used for training, validation and
  test episodes.
- Stochastic evaluation now uses the explicitly seeded PyTorch generator.
- The best MAPPO encoder is chosen by mean best-validation dwell across seeds.
- Test results are never used to choose the best encoder.
- Stable encoder order is used only to break an exact validation tie.

### Optional generalization study

- A leave-one-scenario-out mode was added.
- It trains on six CAM-LDS scenarios and tests on the seventh.
- It uses 8 configurations x 7 held-out scenarios x 5 seeds = 280 cells.
- The held-out scenario is excluded from encoder pretraining and RL training.
- This tests transfer to an unseen CAM-LDS scenario, not unseen network size or
  transfer to raw logs.

## 10. Metrics and result-table changes

Every requested table now reports:

- **Dwell time (steps):** total steps during which a decoy engaged the attacker.
- **Interaction depth (techniques):** number of distinct ATT&CK techniques that
  engaged with decoys.
- **Asset protection:** fraction of episodes in which the configured objective
  was not reached.

The report produces:

- The six requested Transformer/GRU/LSTM x IPPO/MAPPO rows.
- Both NoHistory control rows.
- The validation-selected three-row ablation:
  selected encoder + IPPO, NoHistory + IPPO, selected encoder + MAPPO.
- An additional NoHistory + MAPPO row for intent ablation under MAPPO.
- Per-scenario tables.
- Mean, sample standard deviation and 95% t confidence interval across seeds.
- Paired seed-level tests with Holm correction across 27 fixed comparisons.
- Markdown, JSON and CSV outputs.

Episodes are not treated as independent statistical replicates. The seed is the
independent unit; LOSO folds are averaged within each seed before testing.

## 11. Runner and reproducibility changes

- Added one portable runner for main, LOSO and smoke studies.
- Added explicit `cpu`, `cuda` and automatic device selection.
- Requesting CUDA now fails clearly if CUDA-enabled PyTorch is unavailable.
- Deterministic algorithms are requested with warnings enabled, and cuDNN
  benchmarking is disabled.
- Runs resume at completed-cell boundaries.
- Each completed cell has a JSON record and an actor/encoder checkpoint.
- Each checkpoint is protected by a recorded SHA-256 hash.
- A code/data/config fingerprint prevents mixing incompatible cells.
- A complete expected-cell manifest is written before training.
- A `.running` lock prevents two processes from writing to one output folder.
- Result JSON uses atomic temporary-file replacement to prevent partial writes.
- Checkpoints store the actor, encoder, cell specification, environment config,
  encoder specifications and experiment fingerprint.
- Checkpoints support evaluation; optimizer state for mid-cell resume is not
  stored, so an interrupted active cell restarts.

## 12. Portability changes

- Frozen dependencies were copied inside `thesis_version_2310`.
- `_frozen.py` resolves all paths relative to this folder.
- Both CAM-LDS grounding files are bundled.
- The supplied Transformer, GRU and LSTM reference papers are bundled.
- No parent repository, AttackBed clone or COMISET dataset is required at
  runtime.
- Package requirements are declared for NumPy, SciPy and PyTorch.
- Generated results, caches and virtual environments are excluded from the
  distributable ZIP.

## 13. Tests added or retained

- Retained 27 environment tests for attacker scripts, capacity, breadcrumbs,
  exposure, objective progress, rewards, locality and deterministic streams.
- Added 13 bundle tests covering frozen files, verified counts, LOSO exclusion,
  original Cho GRU equation, original 1997 LSTM equation, sequence masks,
  gradients, checkpoints, future-history exclusion, IPPO critic locality,
  PPO actor identity, experiment combinations and validation-only selection.
- Ran all six requested combinations and both controls as short CPU smoke tests.
- Verified completed-cell resume behavior.
- Verified the package from a temporary directory outside the parent repository.
- GPU execution was subsequently confirmed on the lab RTX 4080 SUPER by the
  CUDA smoke run before the full experiment began.

## 14. Files changed or added for this run

| File | Change |
|---|---|
| `encoders_marl.py` | New paper-aligned Transformer, custom Cho GRU, custom 1997 LSTM and NoHistory factory |
| `experiment.py` | New six-arm design, controls, seeds, budget, metrics and selection rule |
| `run_experiment.py` | New portable, resumable CPU/CUDA experiment runner |
| `report_results.py` | New overall, ablation, per-scenario and statistical reports |
| `test_bundle.py` | New model, data and pipeline regression tests |
| `pretrain_marl.py` | Uses new encoders and excludes invalid PAD/UNK output classes from loss |
| `mappo.py` | Seeded stochastic evaluation fixed |
| `scripts_marl.py` | Strict verified-vocabulary check and safe JSON reads |
| `_frozen.py` | Standalone paths and verified grounding integrity hash |
| `requirements.txt` | Portable dependency ranges |
| `README.md` | Package, study and execution documentation |
| `ARCHITECTURE_AND_AUDIT.md` | Architecture sources, adaptations and limitations |
| `RESULT_TABLES_TEMPLATE.md` | Required final table structure |
| `VALIDATION.md` | Local test and portability evidence |
| `WHAT_WE_ARE_DOING.md` | Short explanation of the current experiment |

## 15. Files deliberately retained unchanged

The following core files are byte-identical to `temarl_marl`:

- `env_marl.py`
- `env_config.json`
- `baselines_marl.py`
- `gates_marl.py`
- `tests_marl.py`

The frozen D3FEND payoff, vocabulary and supporting v2 modules are also bundled
without scientific retuning. Their integrity is checked when the package loads.

## 16. Interpretation limits

- The new experiment specification was written after earlier project results
  existed, so it is not the historical v7 preregistration.
- The 2-million-step budget was inherited from the older Transformer-RoPE gate
  and was not selected independently for all three new encoders.
- Reward directly optimizes dwell. Interaction depth and asset protection are
  measured outcomes, not objectives guaranteed to improve.
- Passing software tests shows implementation consistency; it does not validate
  the simulator as a faithful model of a live enterprise network.
- No model is assumed to win. Conclusions must follow the final multi-seed
  results and their uncertainty.
