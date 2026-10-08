# TEMARL 2310 2.0: exact CAM-LDS playbook replay

This is a separate experiment bundle. Fresh training is required. No previous
checkpoints, training outputs or lab results are included as current results.
The original thesis_version_2310 folder is unchanged.

## Data pipeline

Official AttackBed playbook metadata -> verified ordered technique labels ->
duplicate-grouped train/validation/test split -> frozen parent-technique IDs ->
history windows and exact-replay simulator episodes -> frozen encoder -> IPPO/MAPPO.

There is no Markov attack-sequence generation. A run can be replayed repeatedly,
but repeated episodes are not additional independent source data. Movement,
engagement and exposure remain stochastic simulation mechanisms.

The 36 playbooks contain 1,347 labelled technique instances. These are ordered
metadata labels, not raw logs, individual shell commands, or real-world attacks.
One command may have several labels, flattened in metadata order. Templates may
contain conditional/runtime behavior; static metadata replay does not reproduce
command execution, timing or actual runtime branches.

## Split and claims

Fixed deterministic split seed: 2310. Split before window extraction:

| Partition | Runs | Scenarios |
|---|---:|---|
| Training | 25 | S1-S7 |
| Validation | 5 | S1, S3, S6 |
| Test | 6 | S1, S2, S3, S6 |

Identical full source sequences and identical parent-ID sequences cannot cross
partitions. The duplicate scenario_5.j2.yml source is an alias of scenario_5.j2.
Scenarios with one unique run remain in training. Two-run strata use train/test.
Other strata reserve roughly 20% each for validation/test, rounded down with at
least one run in each. Assignment uses a fixed hash order, independent of scores.

Near-duplicate variants remain: maximum train/test sequence similarity is 0.9804
(difflib SequenceMatcher, not Jaccard). Shared prefixes/windows can recur across
different runs. This evaluates held-out execution variants, NOT unseen campaigns.
See REPLAY_DATA_AUDIT.json for exact assignments and overlap evidence.
The test set also has 36/237 prediction targets whose parent labels never occur
in training (15.19%). Report this support limitation alongside accuracy.

## Preserved design

- Transformer, original-paper-style GRU and LSTM; 64-dimensional frozen history.
- IPPO/MAPPO, actor/critic networks, optimizer settings and model budgets.
- Fixed five-zone simulator, four agents, six actions each, capacity contention,
  breadcrumbs, exposure, D3FEND payoff, reward and objective rules.
- Six model combinations and NoHistory + IPPO/MAPPO controls: 80 cells / 10 seeds.
- Dwell steps, distinct engaged parent techniques, asset protection.
- Validation-only best-MAPPO encoder selection and the three requested ablations.

Full source labels including sub-techniques are retained on each EpisodeSpec.
The unchanged 84-class vocabulary maps sub-techniques to parent IDs. Every label
still occupies one step, including adjacent repetitions. Predictions and depth
are at parent-technique resolution. Exact replay describes source-label order;
it does not mean the classifier distinguishes sub-techniques.

The original bundle has a fixed five-zone engagement environment. This update
does not introduce variable topologies or claim it contains the older v3 topology
experiment. Zone/objective metadata still comes from the historical reconstruction;
only the ordered attack labels are directly verified against official playbooks.

## Lab PC setup

Copy this entire folder, including thesis_system and source_attackbed. Use
Python 3.12 and a compatible PyTorch environment. In PowerShell at this folder:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -c "import torch; print(torch.__version__); print('CUDA:', torch.cuda.is_available())"
```

For GPU training CUDA must print True. Otherwise install the appropriate
CUDA-enabled PyTorch build using the official PyTorch installation selector.
The simulator still runs on CPU; CUDA runs the neural networks.

Check without training:

```powershell
.\.venv\Scripts\python.exe validate_replay.py
```

Optional lab smoke test (does perform a tiny training run, separate outputs):

```powershell
.\.venv\Scripts\python.exe -u run_experiment.py --smoke --device cuda
```

Full experiment, when ready:

```powershell
.\.venv\Scripts\python.exe -u run_experiment.py --device cuda --threads 4
.\.venv\Scripts\python.exe report_results.py results/main
```

Alternatively run `run_lab.ps1 -Python .\.venv\Scripts\python.exe -Device cuda`.
It checks first, then runs the full experiment. Do not launch both commands.
CPU is supported with --device cpu. The output folder is results/main; the final
human-readable report is RESULTS.md, with metrics.csv, analysis.json, per-cell
records and checkpoints. Interrupted runs resume completed cells; an interrupted
cell restarts. A crash can leave .running: verify no process is running before
removing that lock manually. Never reuse an old results folder.

Each policy seed evaluates the same 500 test episode specs as the other arms.
They cycle across six held-out runs with matched simulator randomness; this is
500 simulator repetitions, not 500 independent playbooks. With 500 repetitions,
the first two runs receive 84 trials and the other four 83. Seed intervals are
conditional on this fixed split. Prediction test scores use every test window
once per seed and report MAPPO pretraining records only to avoid counting the
identical IPPO pretraining twice.

RESULTS.md also explains defence outcomes in plain English and displays matched
prediction examples for Transformer, GRU and LSTM: observed history, actual next
technique, readable technique names, top-three probabilities and correctness.
It uses the smallest shared completed seed and fixed first/middle/last windows
per held-out run; examples are not selected for model success. All test-window
predictions are saved in each cell JSON. Probabilities are uncalibrated model
scores. No ensemble or separate display dataset is used.

## Provenance and historical files

Official source: https://github.com/ait-testbed/attackbed
Bundled source commit: 4d43354115019427e74b8df5f2c3237cd7c38e3d.
The audit parses its templates and checks every full sequence against the frozen
verified JSON. Upstream license files remain in source_attackbed.

legacy_reference contains superseded documents, stochastic attacker code and
Markov-dependent baseline/gate tools for reference only. They are not runnable
entrypoints for this study. Frozen dependency modules also retain historical
utilities for integrity, but the active replay path never samples their chains.
The original full results remain in the original folder; they were not copied.
