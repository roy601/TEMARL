# Independent BAAHS-style replication: experimental report

**Status: INDEPENDENT SIMULATION, NOT ORIGINAL-AUTHOR REPRODUCTION.**

Original BAAHS experimental assets, equations, seeds, and complete protocol were not available.
This code therefore uses explicit synthetic assumptions. Similar numeric means do not establish equivalence.

## Published reference (not used in policy selection)

- Paper BAAHS: 25.89%
- Paper strongest baseline: 15.32%
- Reference: https://doi.org/10.1109/ACCESS.2026.3740819

## Development / exploratory runs

- Completed batches: 1 (each 50 seeds, except custom sizes)
- Exploratory within ±1.00 percentage points for both rates: **False**
- This condition is ONLY an exploratory flag, not a reproduction claim.

| Method | Seeds | Hit rate (per-seed mean) | Across-seed SD | Normal 95% CI |
|---|---:|---:|---:|---|
| hmm_greedy | 50 | 34.15% | 5.01% | [32.76%, 35.54%] |
| pomdp_proxy | 50 | 32.68% | 5.07% | [31.28%, 34.09%] |
| baahs_independent | 50 | 29.22% | 4.96% | [27.84%, 30.59%] |
| centrality | 50 | 19.65% | 3.61% | [18.65%, 20.65%] |
| discounted_ts | 50 | 17.92% | 5.18% | [16.49%, 19.36%] |
| contextual_bandit | 50 | 17.42% | 4.29% | [16.23%, 18.61%] |
| random | 50 | 16.48% | 4.21% | [15.31%, 17.65%] |
| static | 50 | 15.65% | 5.23% | [14.20%, 17.10%] |

## Frozen held-out validation

Development-selected baseline: **hmm_greedy**

| Method | Seeds | Hit rate | Normal 95% CI | Difference from paper (percentage points) |
|---|---:|---:|---|---:|
| baahs_independent | 50 | 28.05% | [26.46%, 29.65%] | +2.16 |
| hmm_greedy | 50 | 34.41% | [32.78%, 36.03%] | +19.09 |

All other held-out baselines are also in `summary.json`.
Held-out seeds never influence model parameters, stopping, or baseline selection.

## Scientific interpretation

A numerically close result is not proof of having reproduced the original BAAHS study.
Differences in attacker trajectories, HMM probabilities, role mapping, objective weights,
reward updates, and baseline choices can dominate outcomes. The correct evidence level
is an independent simulated method comparison with reference-value diagnostics.

## Outputs

- `dev_runs.csv` / `holdout_runs.csv`: full per-seed results for every policy
- `dev_events.jsonl` / `holdout_events.jsonl`: every placement, outcome and hit
- `summary.json`: full aggregates, configuration, and provenance
