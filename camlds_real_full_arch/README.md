# CAM-LDS recorded-data full architecture

This adds IPPO and MAPPO to `camlds_real` + `camlds_encoder`. Existing folders, checkpoints and results are unchanged. The new experiment has not been run to completion; smoke outputs are software checks only.

## Where the data comes from

CAM-LDS v1: https://doi.org/10.5281/zenodo.18390561 . The authors' analysis repository is https://github.com/ait-aecid/attack-manifestations-interpretation (recorded upstream revision `42bbd2cf8409f64a1e6c8fc936c91725e8c558b2`).

The existing `camlds_real` extraction takes the authors' `attack_times.csv`, whose labels come from executed AttackMate `attackmate.json` metadata. Its reconciliation links each retained row to an execution record. This pipeline reads `camlds_real/out/steps.jsonl`, `vocab.json` and `out/sidecar/steps_link.jsonl`: 904 labelled command records, 34 runs, 7 scenarios, 81 parent-technique labels. These are recorded scripted testbed executions, not uncontrolled real attackers. Technique labels are supplied metadata, not inferred by a detector from PCAP/syslog contents. No additional dataset is downloaded by this runner.

One model input position is one command's unordered multi-hot technique set. Parent collapse follows the existing encoder protocol. Unlabelled commands and the three sleep entries folded upstream are not reintroduced: this is replay of the retained labelled execution stream, not every raw shell event.

## Full pipeline

Recorded execution metadata -> run-level train/validation/test folds -> 16-command windows -> next-command technique-set prediction -> validation-best frozen 64-dimensional history -> four local defender actors -> simulated decoy actions -> reward -> IPPO/MAPPO policy training -> held-out replay evaluation.

The four defenders cover DMZ, LAN, User and Admin. The six categorical actions, payoff compatibility, capacity coupling, rewards, exposure and movement mechanics are inherited from `Temarl_Test_v1_L1`. They remain simulator assumptions; engagement, dwell and protection are not observed real honeypot outcomes. Local observations contain prior labelled activity (ideal/oracle telemetry). MAPPO centralises critic information during training; IPPO uses local critics. Both execute local actors.

## Two Transformers, kept separate

| Arm | Meaning |
|---|---|
| allpos | Primary: causal Transformer, next-step BCE at every real position |
| baseline | Earlier Transformer: attention within the past window, last-position BCE |
| gru_allpos | GRU with all-position BCE |
| lstm_allpos | Forget-gate LSTM with all-position BCE |
| NoHistory | No encoder; 64 history values are zero, local telemetry retained |

Both Transformers see only history preceding the current RL action. Neither is an LLM. The existing `variants.py` documents the all-position adaptation of SASRec. This extension does not introduce a new optimizer or claim that the full adaptation was prescribed by that paper.

## Ordering and mapping corrections

Default `--order execution` orders retained records by reconciled `execution_rank`. This fixes four known S6 adjacent swaps caused by adjusted CSV time windows. It keeps every original label set and source-row identity. It requires freshly trained encoders: old checkpoints are not silently reused. `--order frozen` explicitly reproduces the earlier CSV ordering and can reuse lab checkpoints from `camlds_encoder/out`; disclose that ordering limitation when reporting it.

The 81-label corpus and old 84-label simulator have different integer orders. Payoffs and goal masks are remapped by ATT&CK technique string, never by integer coincidence. All 81 labels currently have payoff entries; missing mappings abort. Scenario topology and goals still come from the inherited reconstruction, not raw traffic. S4 is included in RL replay. Because its firewall target is outside the inherited topology, the existing declared fallback maps that target to S4's entry zone; this assumption is recorded in the audit and is not a measured network location. Slash-separated goals retain the inherited first-goal rule; this is a limitation, not a measured intent label. `DATA_AUDIT.json` lists mappings and scenario assumptions.

## Frozen experimental choices

- Existing 32 folds: 29 known-variant folds and 3 unseen-scenario folds, reported separately. Scenario variants are correlated and are not independent campaigns.
- Seeds 0–9; both learners for five arms: 3,200 RL cells for the complete grid. This is a large study. Use `--folds`, `--arms` or `--seeds` only for explicitly labelled subsets in a different output folder.
- Fresh encoder training inherits AdamW/BCE, ordinary shuffled passes, validation frequency and minimum improvement from the frozen encoder trainer. Patience is 16 validation checks. Caps are 9,152 updates for Transformers and 18,304 for GRU/LSTM, following the existing selected protocol. This is NOT equal maximum optimization effort across architectures. Actual updates, curves and cap flags are saved.
- Validation BCE selects encoder checkpoint; validation micro-F1 selects the threshold. Test labels do not select checkpoints, thresholds or RL policies. The test set has previously been examined in the project, so do not claim a newly untouched confirmatory dataset.
- Frozen encoder throughout RL. Shared seed-derived validation/test episode randomness across arms. Each held-out run is evaluated 20 times; those repeats measure simulator stochasticity and do not increase independent dataset size.
- RL request: 2,000,000 steps. Inherited rollout size rounds this down to 1,998,848 actual steps; saved explicitly. Validation dwell chooses policy checkpoint. Final results are held-out evaluations.
- Max aggregation is the inherited set-payoff assumption. Episode termination may truncate recorded sequences, but cannot add or reorder commands. Observation normalization uses 64, not held-out lengths.
- No Markov fitting, prediction or episode generation. No noise-robustness, static-honeypot or published-controller comparison is claimed by this initial extension. NoHistory is a trained RL baseline, not a static honeypot.

## Lab instructions

Keep this folder beside `camlds_encoder`, `camlds_real`, and `Temarl_Test_v1_L1` in the repository. It deliberately reuses their frozen dependencies; copying this folder alone is insufficient. Raw 7+GB archives are not needed once the extracted corpus and reconciliation sidecar are present. Use your existing lab environment with PyTorch; install a CUDA build compatible with the lab driver separately if CUDA is unavailable.

```powershell
cd C:\Users\user5\TEMARL\camlds_real_full_arch
python -m pip install -r requirements.txt
python test_pipeline.py
python pipeline.py --audit-only
python pipeline.py --smoke --device cpu
python -u pipeline.py --device cuda --train-missing --threads 4
```

Or run `powershell -ExecutionPolicy Bypass -File .\run_lab.ps1` from this directory after activating the lab Python environment. This does not reinstall CUDA or modify system settings.

Main output: `results/main/RESULTS.md`. Includes prediction metrics, RL metrics, descriptive summaries and available encoder/RL curves. Detailed per-episode outputs and all remaining metrics are in each `result.json`; actor and encoder checkpoints are saved alongside them. Imported encoder checkpoints do not recreate missing historical training curves.

Repeat the identical command to resume: completed RL cells are skipped; unfinished RL cells restart from update zero. This is cell-level resume, not mid-update optimizer resume. Unique temporary JSON files and bounded retries handle transient Windows replacement errors. A configuration/hash mismatch refuses to mix studies. A concurrent-run lock prevents two writers. After a hard crash, remove `RUNNING.lock` only after confirming the earlier Python process has stopped.

## Interpretation limits

Better prediction does not guarantee better deception. Simulator payoff assumptions, ideal technique labels, small correlated scenarios, unseen-label support, reconstructed goals/topology, and the S4 target-zone fallback constrain conclusions. Protection percentage is goal avoidance in the simulator; dwell is engaged command steps; depth is distinct engaged technique labels. None is wall-clock time. Report known-variant and unseen-scenario results separately and avoid claiming model equivalence from nonsignificance. This package adds the missing downstream stage; it does not establish operational deployment fidelity.
