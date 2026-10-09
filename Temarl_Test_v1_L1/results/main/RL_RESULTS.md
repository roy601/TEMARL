# Deception results

> **Scope.** Source-derived annotated playbook sequences from the AttackBed
> repository, evaluated in a simulator. NOT real-world attacker telemetry. The
> environment's engagement, movement and exposure rules are modelling
> assumptions, not measured quantities.
>
> **Representation.** Command-level and multi-label: one step is one annotated
> attacker command, and the techniques within a command are an unordered set.
> Within-command label order is discarded by construction, so the 34.9%
> label-order artefact of the earlier flattened corpus cannot be learned here.
>
> **Not comparable with the earlier study.** Its Top-1 scored one token out of
> a flattened stream; these targets are label SETS over command transitions.
> Its dwell counted label-steps; here dwell counts commands. Different units.
>
> **Sample size.** 36 playbooks from 7 scenarios. Seeds, environment repeats
> and prediction windows are not independent attack campaigns.


**Dwell counts COMMANDS engaged, not technique labels.** One command is one step and earns at most one unit of reward, however many labels it carries. The earlier study's dwell counted label-steps and is a different quantity.

## Reference ladder

_Tunable baselines (best_fixed, static_best) are fitted on VALIDATION. Clairvoyant rungs read future state and are measuring instruments for the ladder, never comparison arms. All baselines obey the same capacity rule as the policies._

Tuned on validation: best fixed joint action `[2, 0, 5, 0]`, static action `5`.

| rung | dwell | depth | protection % | lure chains | exposed |
|---|---:|---:|---:|---:|---:|
| null | 0.000 | 0.000 | 44.0 | 0.00 | 0.000 |
| static_best | 2.911 | 3.231 | 46.3 | 0.00 | 0.431 |
| random | 2.523 | 3.823 | 44.9 | 0.09 | 0.360 |
| best_fixed | 5.220 | 3.571 | 47.1 | 0.00 | 0.263 |
| reactive | 5.497 | 4.226 | 44.6 | 0.00 | 0.291 |
| clairvoyant_local | 14.149 | 14.060 | 59.1 | 0.00 | 0.600 |
| clairvoyant_coord | 16.923 | 16.617 | 74.6 | 2.71 | 0.291 |

- floor (best fixed): **5.220**, ceiling (coordinated clairvoyant): **16.923**, headroom **11.703**
- value of coordination (coordinated - uncoordinated clairvoyant): **+2.774** dwell

## Policies

| arm | learner | window | seeds | dwell | depth | protection % | dwell at h=0 | headroom captured |
|---|---|---:|---:|---|---|---|---|---|
| GRU | IPPO | 16 | 10 | 12.223 +/- 0.217 | 13.109 +/- 0.226 | 61.3 +/- 1.3 | 6.477 +/- 0.503 | 59.8% |
| GRU | IPPO | 64 | 10 | 12.199 +/- 0.197 | 13.065 +/- 0.234 | 60.9 +/- 1.6 | 6.277 +/- 0.505 | 59.6% |
| GRU | MAPPO | 16 | 10 | 12.469 +/- 0.189 | 13.262 +/- 0.183 | 61.5 +/- 1.4 | 6.385 +/- 0.547 | 61.9% |
| GRU | MAPPO | 64 | 10 | 12.435 +/- 0.192 | 13.312 +/- 0.156 | 61.7 +/- 1.0 | 6.497 +/- 0.512 | 61.6% |
| LSTM | IPPO | 16 | 10 | 12.308 +/- 0.206 | 13.192 +/- 0.172 | 61.7 +/- 2.2 | 5.855 +/- 0.438 | 60.6% |
| LSTM | IPPO | 64 | 10 | 12.369 +/- 0.381 | 13.230 +/- 0.417 | 62.3 +/- 4.4 | 6.313 +/- 0.551 | 61.1% |
| LSTM | MAPPO | 16 | 10 | 12.702 +/- 0.295 | 13.477 +/- 0.293 | 63.3 +/- 2.6 | 6.224 +/- 0.510 | 63.9% |
| LSTM | MAPPO | 64 | 10 | 12.499 +/- 0.221 | 13.396 +/- 0.138 | 62.5 +/- 1.6 | 6.227 +/- 0.333 | 62.2% |
| NoHistory | IPPO | 16 | 10 | 9.385 +/- 0.208 | 7.429 +/- 0.196 | 58.7 +/- 1.4 | 9.385 +/- 0.208 | 35.6% |
| NoHistory | MAPPO | 16 | 10 | 9.875 +/- 0.284 | 8.011 +/- 0.279 | 63.0 +/- 4.6 | 9.875 +/- 0.284 | 39.8% |
| OrderFree | IPPO | 16 | 10 | 12.511 +/- 0.443 | 13.507 +/- 0.451 | 63.7 +/- 4.2 | 6.151 +/- 0.378 | 62.3% |
| OrderFree | MAPPO | 16 | 10 | 12.946 +/- 0.393 | 13.855 +/- 0.461 | 65.5 +/- 5.6 | 6.247 +/- 0.357 | 66.0% |
| Transformer | IPPO | 16 | 10 | 12.769 +/- 0.363 | 13.787 +/- 0.351 | 67.9 +/- 4.1 | 6.015 +/- 0.578 | 64.5% |
| Transformer | IPPO | 64 | 10 | 12.621 +/- 0.340 | 13.668 +/- 0.315 | 65.8 +/- 4.5 | 6.031 +/- 0.792 | 63.2% |
| Transformer | MAPPO | 16 | 10 | 13.139 +/- 0.193 | 14.120 +/- 0.333 | 70.0 +/- 3.7 | 6.375 +/- 0.533 | 67.7% |
| Transformer | MAPPO | 64 | 10 | 13.037 +/- 0.439 | 14.042 +/- 0.494 | 68.8 +/- 4.1 | 6.126 +/- 0.575 | 66.8% |

`dwell at h=0` zeroes the history embedding at test time. A large drop means the policy genuinely uses the history channel; no drop means it learned to ignore it.

## Guards

| arm | learner | window | exposed | lure chains | dead ends | capacity violations | episode length |
|---|---|---:|---|---|---|---|---|
| GRU | IPPO | 16 | 0.310 +/- 0.009 | 1.31 +/- 0.15 | 0.02 +/- 0.03 | 0.79 +/- 0.31 | 20.6 +/- 0.1 |
| GRU | IPPO | 64 | 0.319 +/- 0.008 | 1.34 +/- 0.14 | 0.02 +/- 0.03 | 0.87 +/- 0.24 | 20.6 +/- 0.1 |
| GRU | MAPPO | 16 | 0.298 +/- 0.013 | 1.37 +/- 0.11 | 0.00 +/- 0.00 | 0.35 +/- 0.10 | 20.7 +/- 0.1 |
| GRU | MAPPO | 64 | 0.303 +/- 0.011 | 1.38 +/- 0.10 | 0.01 +/- 0.03 | 0.31 +/- 0.16 | 20.7 +/- 0.1 |
| LSTM | IPPO | 16 | 0.321 +/- 0.013 | 1.35 +/- 0.10 | 0.02 +/- 0.05 | 0.80 +/- 0.10 | 20.7 +/- 0.1 |
| LSTM | IPPO | 64 | 0.311 +/- 0.014 | 1.38 +/- 0.23 | 0.03 +/- 0.03 | 0.67 +/- 0.36 | 20.7 +/- 0.3 |
| LSTM | MAPPO | 16 | 0.299 +/- 0.010 | 1.46 +/- 0.11 | 0.01 +/- 0.01 | 0.31 +/- 0.22 | 20.8 +/- 0.2 |
| LSTM | MAPPO | 64 | 0.315 +/- 0.010 | 1.44 +/- 0.08 | 0.01 +/- 0.02 | 0.53 +/- 0.25 | 20.7 +/- 0.1 |
| NoHistory | IPPO | 16 | 0.316 +/- 0.014 | 0.25 +/- 0.11 | 0.00 +/- 0.00 | 0.69 +/- 0.60 | 20.4 +/- 0.2 |
| NoHistory | MAPPO | 16 | 0.319 +/- 0.014 | 0.50 +/- 0.32 | 0.01 +/- 0.04 | 0.50 +/- 0.29 | 20.8 +/- 0.4 |
| OrderFree | IPPO | 16 | 0.301 +/- 0.020 | 1.48 +/- 0.24 | 0.01 +/- 0.01 | 0.67 +/- 0.33 | 21.0 +/- 0.4 |
| OrderFree | MAPPO | 16 | 0.308 +/- 0.009 | 1.74 +/- 0.28 | 0.01 +/- 0.01 | 0.47 +/- 0.17 | 21.2 +/- 0.4 |
| Transformer | IPPO | 16 | 0.312 +/- 0.015 | 1.70 +/- 0.25 | 0.01 +/- 0.02 | 0.75 +/- 0.27 | 21.2 +/- 0.3 |
| Transformer | IPPO | 64 | 0.310 +/- 0.017 | 1.61 +/- 0.16 | 0.02 +/- 0.03 | 0.78 +/- 0.19 | 21.0 +/- 0.3 |
| Transformer | MAPPO | 16 | 0.304 +/- 0.014 | 1.84 +/- 0.20 | 0.00 +/- 0.00 | 0.44 +/- 0.27 | 21.4 +/- 0.3 |
| Transformer | MAPPO | 64 | 0.307 +/- 0.015 | 1.76 +/- 0.20 | 0.00 +/- 0.01 | 0.51 +/- 0.25 | 21.3 +/- 0.3 |

## Context window

- selected window: **64**
- rule: ONE longer window (32 or 64) is preselected on POOLED VALIDATION prediction performance, before any RL run at that window. All six encoder-learner combinations are then retrained there -- not only the architecture that happens to lead.

