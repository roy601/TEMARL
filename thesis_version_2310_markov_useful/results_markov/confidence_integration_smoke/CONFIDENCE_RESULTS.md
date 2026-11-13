# Confidence ablation results

Completed policy cells: 12/12.
SMOKE CHECK ONLY; not thesis evidence.

Actor-only intervention: same 64-D embedding; constant 0.5 versus calibrated normalized entropy in the existing gate slot. Critic unchanged.
No generic deception-success metric is invented. Asset protection and engagement are reported separately.

## Main results
Percentages: protected/exposed. Other metrics use their original units.

| Encoder | RL | Mode | Seeds | episode_reward | dwell | depth | protected | exposed | lure_chains | dead_ends | capacity_violations | length | decoys_deployed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| GRU | IPPO | baseline | 1 | 2.571 (n=1; SD N/A) | 2.571 (n=1; SD N/A) | 2.286 (n=1; SD N/A) | 14.286 (n=1; SD N/A) | 71.429 (n=1; SD N/A) | 0.429 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 95.429 (n=1; SD N/A) |
| GRU | IPPO | confidence | 1 | 2.571 (n=1; SD N/A) | 2.571 (n=1; SD N/A) | 2.286 (n=1; SD N/A) | 14.286 (n=1; SD N/A) | 71.429 (n=1; SD N/A) | 0.429 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 95.571 (n=1; SD N/A) |
| GRU | MAPPO | baseline | 1 | 2.857 (n=1; SD N/A) | 2.857 (n=1; SD N/A) | 1.857 (n=1; SD N/A) | 14.286 (n=1; SD N/A) | 71.429 (n=1; SD N/A) | 0.429 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 96.571 (n=1; SD N/A) |
| GRU | MAPPO | confidence | 1 | 2.857 (n=1; SD N/A) | 2.857 (n=1; SD N/A) | 1.857 (n=1; SD N/A) | 14.286 (n=1; SD N/A) | 71.429 (n=1; SD N/A) | 0.429 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 96.571 (n=1; SD N/A) |
| LSTM | IPPO | baseline | 1 | 2.429 (n=1; SD N/A) | 2.429 (n=1; SD N/A) | 2.429 (n=1; SD N/A) | 14.286 (n=1; SD N/A) | 71.429 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 95.429 (n=1; SD N/A) |
| LSTM | IPPO | confidence | 1 | 2.429 (n=1; SD N/A) | 2.429 (n=1; SD N/A) | 2.429 (n=1; SD N/A) | 14.286 (n=1; SD N/A) | 71.429 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 95.429 (n=1; SD N/A) |
| LSTM | MAPPO | baseline | 1 | 3.429 (n=1; SD N/A) | 3.429 (n=1; SD N/A) | 1.857 (n=1; SD N/A) | 14.286 (n=1; SD N/A) | 57.143 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 96.571 (n=1; SD N/A) |
| LSTM | MAPPO | confidence | 1 | 3.429 (n=1; SD N/A) | 3.429 (n=1; SD N/A) | 1.857 (n=1; SD N/A) | 14.286 (n=1; SD N/A) | 57.143 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 96.571 (n=1; SD N/A) |
| Transformer | IPPO | baseline | 1 | 2.429 (n=1; SD N/A) | 2.429 (n=1; SD N/A) | 2.143 (n=1; SD N/A) | 14.286 (n=1; SD N/A) | 57.143 (n=1; SD N/A) | 0.429 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 95.571 (n=1; SD N/A) |
| Transformer | IPPO | confidence | 1 | 2.429 (n=1; SD N/A) | 2.429 (n=1; SD N/A) | 2.143 (n=1; SD N/A) | 14.286 (n=1; SD N/A) | 57.143 (n=1; SD N/A) | 0.429 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 95.571 (n=1; SD N/A) |
| Transformer | MAPPO | baseline | 1 | 2.571 (n=1; SD N/A) | 2.571 (n=1; SD N/A) | 2.286 (n=1; SD N/A) | 14.286 (n=1; SD N/A) | 57.143 (n=1; SD N/A) | 0.429 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 96.571 (n=1; SD N/A) |
| Transformer | MAPPO | confidence | 1 | 2.571 (n=1; SD N/A) | 2.571 (n=1; SD N/A) | 2.286 (n=1; SD N/A) | 14.286 (n=1; SD N/A) | 57.143 (n=1; SD N/A) | 0.429 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 96.571 (n=1; SD N/A) |

## Primary paired contrasts
Confidence minus baseline dwell (steps); two-sided paired t intervals/tests. Holm across all six contrasts only when complete. n=1 has no inferential result.

| Contrast | Pairs | Delta | 95% CI | p raw | p Holm |
|---|---|---|---|---|---|
| GRU+IPPO | 1 | 0.00000 | N/A | N/A | N/A |
| GRU+MAPPO | 1 | 0.00000 | N/A | N/A | N/A |
| LSTM+IPPO | 1 | 0.00000 | N/A | N/A | N/A |
| LSTM+MAPPO | 1 | 0.00000 | N/A | N/A | N/A |
| Transformer+IPPO | 1 | 0.00000 | N/A | N/A | N/A |
| Transformer+MAPPO | 1 | 0.00000 | N/A | N/A | N/A |

## Calibration per seed
Temperature fitted only on validation NLL; validation is also reused for encoder/policy selection, so only test scores are held-out estimates. ECE uses 10 equal-width max-probability bins, not entropy bins.

| Encoder | Seed | T | Partition | N | NLL | Top1 % | ECE % | Brier |
|---|---|---|---|---|---|---|---|---|
| GRU | 0 | 0.55239 | validation_raw | 265 | 3.03217 | 37.35849 | 23.68639 | 0.85728 |
| GRU | 0 | 0.55239 | validation_scaled | 265 | 2.69920 | 37.35849 | 17.71331 | 0.82577 |
| GRU | 0 | 0.55239 | test_raw | 272 | 3.18636 | 34.92647 | 21.84882 | 0.86551 |
| GRU | 0 | 0.55239 | test_scaled | 272 | 2.92929 | 34.92647 | 16.05055 | 0.82620 |
| LSTM | 0 | 0.54165 | validation_raw | 265 | 3.28992 | 34.33962 | 22.85241 | 0.89546 |
| LSTM | 0 | 0.54165 | validation_scaled | 265 | 2.96635 | 34.33962 | 16.52407 | 0.84926 |
| LSTM | 0 | 0.54165 | test_raw | 272 | 3.51010 | 30.51471 | 20.64419 | 0.90678 |
| LSTM | 0 | 0.54165 | test_scaled | 272 | 3.29135 | 30.51471 | 12.74903 | 0.85117 |
| Transformer | 0 | 0.54789 | validation_raw | 265 | 3.40242 | 28.30189 | 17.72233 | 0.90444 |
| Transformer | 0 | 0.54789 | validation_scaled | 265 | 3.13991 | 28.30189 | 8.55473 | 0.86610 |
| Transformer | 0 | 0.54789 | test_raw | 272 | 3.61155 | 26.10294 | 15.78741 | 0.91354 |
| Transformer | 0 | 0.54789 | test_scaled | 272 | 3.50624 | 26.10294 | 9.36762 | 0.88230 |

## Prediction certainty groups
Certainty = 1 - normalized entropy; not probability of being correct. Thresholds: validation-window tertiles. Empty bins are N/A.

| Encoder | Seed | Thresholds | Group | Windows | Accuracy | Mean certainty |
|---|---|---|---|---|---|---|
| GRU | 0 | [0.20564592243702973, 0.43820653170642165] | low | 119 | 0.11765 | 0.14676 |
| GRU | 0 | [0.20564592243702973, 0.43820653170642165] | medium | 67 | 0.52239 | 0.29186 |
| GRU | 0 | [0.20564592243702973, 0.43820653170642165] | high | 86 | 0.53488 | 0.71748 |
| LSTM | 0 | [0.18013930158997937, 0.37120780894386163] | low | 137 | 0.20438 | 0.12713 |
| LSTM | 0 | [0.18013930158997937, 0.37120780894386163] | medium | 69 | 0.17391 | 0.23281 |
| LSTM | 0 | [0.18013930158997937, 0.37120780894386163] | high | 66 | 0.65152 | 0.66079 |
| Transformer | 0 | [0.1498943472813853, 0.27044327199216167] | low | 80 | 0.15000 | 0.12568 |
| Transformer | 0 | [0.1498943472813853, 0.27044327199216167] | medium | 104 | 0.15385 | 0.19543 |
| Transformer | 0 | [0.1498943472813853, 0.27044327199216167] | high | 88 | 0.48864 | 0.52904 |

## Policy results by fixed sequence-certainty group
Groups use whole-playbook mean prefix certainty and validation-playbook tertiles, not policy-dependent visited prefixes. Grouping is retrospective, never input to the policy. Descriptive only: groups may differ in scenario/difficulty; no causal claim.

| Encoder | RL | Mode | Group | Seeds with data | Episodes | episode_reward | dwell | depth | protected | exposed | lure_chains | dead_ends | capacity_violations | length | decoys_deployed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| GRU | IPPO | baseline | low | 1 | 3 | 2.333 (n=1; SD N/A) | 2.333 (n=1; SD N/A) | 1.667 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 1.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 11.000 (n=1; SD N/A) | 11.000 (n=1; SD N/A) | 42.667 (n=1; SD N/A) |
| GRU | IPPO | baseline | medium | 1 | 1 | 3.000 (n=1; SD N/A) | 3.000 (n=1; SD N/A) | 3.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 100.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 119.000 (n=1; SD N/A) |
| GRU | IPPO | baseline | high | 1 | 3 | 2.667 (n=1; SD N/A) | 2.667 (n=1; SD N/A) | 2.667 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 100.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 35.333 (n=1; SD N/A) | 35.333 (n=1; SD N/A) | 140.333 (n=1; SD N/A) |
| GRU | IPPO | baseline | no_history | 0 | 0 | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| GRU | IPPO | confidence | low | 1 | 3 | 2.333 (n=1; SD N/A) | 2.333 (n=1; SD N/A) | 1.667 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 1.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 11.000 (n=1; SD N/A) | 11.000 (n=1; SD N/A) | 43.000 (n=1; SD N/A) |
| GRU | IPPO | confidence | medium | 1 | 1 | 3.000 (n=1; SD N/A) | 3.000 (n=1; SD N/A) | 3.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 100.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 119.000 (n=1; SD N/A) |
| GRU | IPPO | confidence | high | 1 | 3 | 2.667 (n=1; SD N/A) | 2.667 (n=1; SD N/A) | 2.667 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 100.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 35.333 (n=1; SD N/A) | 35.333 (n=1; SD N/A) | 140.333 (n=1; SD N/A) |
| GRU | IPPO | confidence | no_history | 0 | 0 | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| GRU | MAPPO | baseline | low | 1 | 3 | 2.667 (n=1; SD N/A) | 2.667 (n=1; SD N/A) | 2.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 1.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 11.000 (n=1; SD N/A) | 11.000 (n=1; SD N/A) | 44.000 (n=1; SD N/A) |
| GRU | MAPPO | baseline | medium | 1 | 1 | 4.000 (n=1; SD N/A) | 4.000 (n=1; SD N/A) | 1.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 100.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 120.000 (n=1; SD N/A) |
| GRU | MAPPO | baseline | high | 1 | 3 | 2.667 (n=1; SD N/A) | 2.667 (n=1; SD N/A) | 2.000 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 100.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 35.333 (n=1; SD N/A) | 35.333 (n=1; SD N/A) | 141.333 (n=1; SD N/A) |
| GRU | MAPPO | baseline | no_history | 0 | 0 | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| GRU | MAPPO | confidence | low | 1 | 3 | 2.667 (n=1; SD N/A) | 2.667 (n=1; SD N/A) | 2.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 1.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 11.000 (n=1; SD N/A) | 11.000 (n=1; SD N/A) | 44.000 (n=1; SD N/A) |
| GRU | MAPPO | confidence | medium | 1 | 1 | 4.000 (n=1; SD N/A) | 4.000 (n=1; SD N/A) | 1.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 100.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 120.000 (n=1; SD N/A) |
| GRU | MAPPO | confidence | high | 1 | 3 | 2.667 (n=1; SD N/A) | 2.667 (n=1; SD N/A) | 2.000 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 100.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 35.333 (n=1; SD N/A) | 35.333 (n=1; SD N/A) | 141.333 (n=1; SD N/A) |
| GRU | MAPPO | confidence | no_history | 0 | 0 | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| LSTM | IPPO | baseline | low | 1 | 3 | 1.333 (n=1; SD N/A) | 1.333 (n=1; SD N/A) | 1.333 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 11.000 (n=1; SD N/A) | 11.000 (n=1; SD N/A) | 42.667 (n=1; SD N/A) |
| LSTM | IPPO | baseline | medium | 1 | 3 | 3.000 (n=1; SD N/A) | 3.000 (n=1; SD N/A) | 3.000 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 100.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 35.333 (n=1; SD N/A) | 35.333 (n=1; SD N/A) | 140.333 (n=1; SD N/A) |
| LSTM | IPPO | baseline | high | 1 | 1 | 4.000 (n=1; SD N/A) | 4.000 (n=1; SD N/A) | 4.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 100.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 119.000 (n=1; SD N/A) |
| LSTM | IPPO | baseline | no_history | 0 | 0 | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| LSTM | IPPO | confidence | low | 1 | 3 | 1.333 (n=1; SD N/A) | 1.333 (n=1; SD N/A) | 1.333 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 11.000 (n=1; SD N/A) | 11.000 (n=1; SD N/A) | 42.667 (n=1; SD N/A) |
| LSTM | IPPO | confidence | medium | 1 | 3 | 3.000 (n=1; SD N/A) | 3.000 (n=1; SD N/A) | 3.000 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 100.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 35.333 (n=1; SD N/A) | 35.333 (n=1; SD N/A) | 140.333 (n=1; SD N/A) |
| LSTM | IPPO | confidence | high | 1 | 1 | 4.000 (n=1; SD N/A) | 4.000 (n=1; SD N/A) | 4.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 100.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 119.000 (n=1; SD N/A) |
| LSTM | IPPO | confidence | no_history | 0 | 0 | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| LSTM | MAPPO | baseline | low | 1 | 3 | 1.000 (n=1; SD N/A) | 1.000 (n=1; SD N/A) | 1.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 11.000 (n=1; SD N/A) | 11.000 (n=1; SD N/A) | 44.000 (n=1; SD N/A) |
| LSTM | MAPPO | baseline | medium | 1 | 3 | 5.000 (n=1; SD N/A) | 5.000 (n=1; SD N/A) | 3.000 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 66.667 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 35.333 (n=1; SD N/A) | 35.333 (n=1; SD N/A) | 141.333 (n=1; SD N/A) |
| LSTM | MAPPO | baseline | high | 1 | 1 | 6.000 (n=1; SD N/A) | 6.000 (n=1; SD N/A) | 1.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 100.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 120.000 (n=1; SD N/A) |
| LSTM | MAPPO | baseline | no_history | 0 | 0 | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| LSTM | MAPPO | confidence | low | 1 | 3 | 1.000 (n=1; SD N/A) | 1.000 (n=1; SD N/A) | 1.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 11.000 (n=1; SD N/A) | 11.000 (n=1; SD N/A) | 44.000 (n=1; SD N/A) |
| LSTM | MAPPO | confidence | medium | 1 | 3 | 5.000 (n=1; SD N/A) | 5.000 (n=1; SD N/A) | 3.000 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 66.667 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 35.333 (n=1; SD N/A) | 35.333 (n=1; SD N/A) | 141.333 (n=1; SD N/A) |
| LSTM | MAPPO | confidence | high | 1 | 1 | 6.000 (n=1; SD N/A) | 6.000 (n=1; SD N/A) | 1.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 100.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 120.000 (n=1; SD N/A) |
| LSTM | MAPPO | confidence | no_history | 0 | 0 | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| Transformer | IPPO | baseline | low | 1 | 2 | 3.500 (n=1; SD N/A) | 3.500 (n=1; SD N/A) | 2.500 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 50.000 (n=1; SD N/A) | 1.500 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 15.500 (n=1; SD N/A) | 15.500 (n=1; SD N/A) | 61.000 (n=1; SD N/A) |
| Transformer | IPPO | baseline | medium | 1 | 3 | 2.000 (n=1; SD N/A) | 2.000 (n=1; SD N/A) | 2.000 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 66.667 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 26.000 (n=1; SD N/A) | 26.000 (n=1; SD N/A) | 103.000 (n=1; SD N/A) |
| Transformer | IPPO | baseline | high | 1 | 2 | 2.000 (n=1; SD N/A) | 2.000 (n=1; SD N/A) | 2.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 50.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 119.000 (n=1; SD N/A) |
| Transformer | IPPO | baseline | no_history | 0 | 0 | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| Transformer | IPPO | confidence | low | 1 | 2 | 3.500 (n=1; SD N/A) | 3.500 (n=1; SD N/A) | 2.500 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 50.000 (n=1; SD N/A) | 1.500 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 15.500 (n=1; SD N/A) | 15.500 (n=1; SD N/A) | 61.000 (n=1; SD N/A) |
| Transformer | IPPO | confidence | medium | 1 | 3 | 2.000 (n=1; SD N/A) | 2.000 (n=1; SD N/A) | 2.000 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 66.667 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 26.000 (n=1; SD N/A) | 26.000 (n=1; SD N/A) | 103.000 (n=1; SD N/A) |
| Transformer | IPPO | confidence | high | 1 | 2 | 2.000 (n=1; SD N/A) | 2.000 (n=1; SD N/A) | 2.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 50.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 119.000 (n=1; SD N/A) |
| Transformer | IPPO | confidence | no_history | 0 | 0 | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| Transformer | MAPPO | baseline | low | 1 | 2 | 4.000 (n=1; SD N/A) | 4.000 (n=1; SD N/A) | 3.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 50.000 (n=1; SD N/A) | 1.500 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 15.500 (n=1; SD N/A) | 15.500 (n=1; SD N/A) | 62.000 (n=1; SD N/A) |
| Transformer | MAPPO | baseline | medium | 1 | 3 | 1.667 (n=1; SD N/A) | 1.667 (n=1; SD N/A) | 1.667 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 66.667 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 26.000 (n=1; SD N/A) | 26.000 (n=1; SD N/A) | 104.000 (n=1; SD N/A) |
| Transformer | MAPPO | baseline | high | 1 | 2 | 2.500 (n=1; SD N/A) | 2.500 (n=1; SD N/A) | 2.500 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 50.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 120.000 (n=1; SD N/A) |
| Transformer | MAPPO | baseline | no_history | 0 | 0 | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| Transformer | MAPPO | confidence | low | 1 | 2 | 4.000 (n=1; SD N/A) | 4.000 (n=1; SD N/A) | 3.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 50.000 (n=1; SD N/A) | 1.500 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 15.500 (n=1; SD N/A) | 15.500 (n=1; SD N/A) | 62.000 (n=1; SD N/A) |
| Transformer | MAPPO | confidence | medium | 1 | 3 | 1.667 (n=1; SD N/A) | 1.667 (n=1; SD N/A) | 1.667 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 66.667 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 26.000 (n=1; SD N/A) | 26.000 (n=1; SD N/A) | 104.000 (n=1; SD N/A) |
| Transformer | MAPPO | confidence | high | 1 | 2 | 2.500 (n=1; SD N/A) | 2.500 (n=1; SD N/A) | 2.500 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 50.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 120.000 (n=1; SD N/A) |
| Transformer | MAPPO | confidence | no_history | 0 | 0 | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending |

## Every policy seed

| Encoder | RL | Mode | Seed | Steps | Actor params | Critic params | Best update | Validation dwell | episode_reward | dwell | depth | protected | exposed | lure_chains | dead_ends | capacity_violations | length | decoys_deployed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| GRU | IPPO | baseline | 0 | 16 | 23814 | 38089 | 1 | 3.85714 | 2.57143 | 2.57143 | 2.28571 | 0.14286 | 0.71429 | 0.42857 | 0.00000 | 24.14286 | 24.14286 | 95.42857 |
| GRU | IPPO | confidence | 0 | 16 | 23814 | 38089 | 1 | 3.85714 | 2.57143 | 2.57143 | 2.28571 | 0.14286 | 0.71429 | 0.42857 | 0.00000 | 24.14286 | 24.14286 | 95.57143 |
| GRU | MAPPO | baseline | 0 | 16 | 23814 | 43159 | 1 | 2.71429 | 2.85714 | 2.85714 | 1.85714 | 0.14286 | 0.71429 | 0.42857 | 0.00000 | 24.14286 | 24.14286 | 96.57143 |
| GRU | MAPPO | confidence | 0 | 16 | 23814 | 43159 | 1 | 2.28571 | 2.85714 | 2.85714 | 1.85714 | 0.14286 | 0.71429 | 0.42857 | 0.00000 | 24.14286 | 24.14286 | 96.57143 |
| LSTM | IPPO | baseline | 0 | 16 | 23814 | 38089 | 1 | 3.28571 | 2.42857 | 2.42857 | 2.42857 | 0.14286 | 0.71429 | 0.00000 | 0.00000 | 24.14286 | 24.14286 | 95.42857 |
| LSTM | IPPO | confidence | 0 | 16 | 23814 | 38089 | 1 | 3.28571 | 2.42857 | 2.42857 | 2.42857 | 0.14286 | 0.71429 | 0.00000 | 0.00000 | 24.14286 | 24.14286 | 95.42857 |
| LSTM | MAPPO | baseline | 0 | 16 | 23814 | 43159 | 1 | 3.85714 | 3.42857 | 3.42857 | 1.85714 | 0.14286 | 0.57143 | 0.00000 | 0.00000 | 24.14286 | 24.14286 | 96.57143 |
| LSTM | MAPPO | confidence | 0 | 16 | 23814 | 43159 | 1 | 3.85714 | 3.42857 | 3.42857 | 1.85714 | 0.14286 | 0.57143 | 0.00000 | 0.00000 | 24.14286 | 24.14286 | 96.57143 |
| Transformer | IPPO | baseline | 0 | 16 | 23814 | 38089 | 1 | 3.71429 | 2.42857 | 2.42857 | 2.14286 | 0.14286 | 0.57143 | 0.42857 | 0.00000 | 24.14286 | 24.14286 | 95.57143 |
| Transformer | IPPO | confidence | 0 | 16 | 23814 | 38089 | 1 | 3.71429 | 2.42857 | 2.42857 | 2.14286 | 0.14286 | 0.57143 | 0.42857 | 0.00000 | 24.14286 | 24.14286 | 95.57143 |
| Transformer | MAPPO | baseline | 0 | 16 | 23814 | 43159 | 1 | 3.71429 | 2.57143 | 2.57143 | 2.28571 | 0.14286 | 0.57143 | 0.42857 | 0.00000 | 24.14286 | 24.14286 | 96.57143 |
| Transformer | MAPPO | confidence | 0 | 16 | 23814 | 43159 | 1 | 3.71429 | 2.57143 | 2.57143 | 2.28571 | 0.14286 | 0.57143 | 0.42857 | 0.00000 | 24.14286 | 24.14286 | 96.57143 |

Full episode, calibration-bin and policy-learning records: [CONFIDENCE_DETAILS.md](CONFIDENCE_DETAILS.md). Encoder epoch results: [EPOCH_RESULTS.md](EPOCH_RESULTS.md).
