# Confidence ablation results

Completed policy cells: 12/12.
SMOKE CHECK ONLY; not thesis evidence.

Actor-only intervention: same 64-D embedding; constant 0.5 versus calibrated normalized entropy in the existing gate slot. Critic unchanged.
No generic deception-success metric is invented. Asset protection and engagement are reported separately.

## Main results
Percentages: protected/exposed. Other metrics use their original units.

| Encoder | RL | Mode | Seeds | episode_reward | dwell | depth | protected | exposed | lure_chains | dead_ends | capacity_violations | length | decoys_deployed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| GRU | IPPO | baseline | 1 | 2.429 (n=1; SD N/A) | 2.429 (n=1; SD N/A) | 2.143 (n=1; SD N/A) | 14.286 (n=1; SD N/A) | 57.143 (n=1; SD N/A) | 0.429 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 96.571 (n=1; SD N/A) |
| GRU | IPPO | confidence | 1 | 2.429 (n=1; SD N/A) | 2.429 (n=1; SD N/A) | 2.143 (n=1; SD N/A) | 14.286 (n=1; SD N/A) | 57.143 (n=1; SD N/A) | 0.429 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 96.571 (n=1; SD N/A) |
| GRU | MAPPO | baseline | 1 | 3.143 (n=1; SD N/A) | 3.143 (n=1; SD N/A) | 2.857 (n=1; SD N/A) | 14.286 (n=1; SD N/A) | 57.143 (n=1; SD N/A) | 1.000 (n=1; SD N/A) | 0.143 (n=1; SD N/A) | 10.714 (n=1; SD N/A) | 25.429 (n=1; SD N/A) | 61.429 (n=1; SD N/A) |
| GRU | MAPPO | confidence | 1 | 3.143 (n=1; SD N/A) | 3.143 (n=1; SD N/A) | 2.857 (n=1; SD N/A) | 14.286 (n=1; SD N/A) | 57.143 (n=1; SD N/A) | 1.143 (n=1; SD N/A) | 0.143 (n=1; SD N/A) | 9.714 (n=1; SD N/A) | 25.000 (n=1; SD N/A) | 58.857 (n=1; SD N/A) |
| LSTM | IPPO | baseline | 1 | 2.286 (n=1; SD N/A) | 2.286 (n=1; SD N/A) | 2.000 (n=1; SD N/A) | 14.286 (n=1; SD N/A) | 57.143 (n=1; SD N/A) | 0.429 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 95.571 (n=1; SD N/A) |
| LSTM | IPPO | confidence | 1 | 2.286 (n=1; SD N/A) | 2.286 (n=1; SD N/A) | 2.000 (n=1; SD N/A) | 14.286 (n=1; SD N/A) | 57.143 (n=1; SD N/A) | 0.429 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 95.429 (n=1; SD N/A) |
| LSTM | MAPPO | baseline | 1 | 2.286 (n=1; SD N/A) | 2.286 (n=1; SD N/A) | 2.000 (n=1; SD N/A) | 14.286 (n=1; SD N/A) | 57.143 (n=1; SD N/A) | 0.429 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 95.286 (n=1; SD N/A) |
| LSTM | MAPPO | confidence | 1 | 2.286 (n=1; SD N/A) | 2.286 (n=1; SD N/A) | 2.000 (n=1; SD N/A) | 14.286 (n=1; SD N/A) | 57.143 (n=1; SD N/A) | 0.429 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 95.286 (n=1; SD N/A) |
| Transformer | IPPO | baseline | 1 | 3.286 (n=1; SD N/A) | 3.286 (n=1; SD N/A) | 2.143 (n=1; SD N/A) | 14.286 (n=1; SD N/A) | 57.143 (n=1; SD N/A) | 0.143 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 24.571 (n=1; SD N/A) | 24.571 (n=1; SD N/A) | 98.286 (n=1; SD N/A) |
| Transformer | IPPO | confidence | 1 | 3.286 (n=1; SD N/A) | 3.286 (n=1; SD N/A) | 2.143 (n=1; SD N/A) | 14.286 (n=1; SD N/A) | 57.143 (n=1; SD N/A) | 0.143 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 24.571 (n=1; SD N/A) | 24.571 (n=1; SD N/A) | 98.286 (n=1; SD N/A) |
| Transformer | MAPPO | baseline | 1 | 2.857 (n=1; SD N/A) | 2.857 (n=1; SD N/A) | 1.857 (n=1; SD N/A) | 14.286 (n=1; SD N/A) | 57.143 (n=1; SD N/A) | 0.429 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 95.571 (n=1; SD N/A) |
| Transformer | MAPPO | confidence | 1 | 2.857 (n=1; SD N/A) | 2.857 (n=1; SD N/A) | 1.857 (n=1; SD N/A) | 14.286 (n=1; SD N/A) | 57.143 (n=1; SD N/A) | 0.429 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 24.143 (n=1; SD N/A) | 95.571 (n=1; SD N/A) |

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
| GRU | 0 | 0.55221 | validation_raw | 265 | 3.02414 | 37.35849 | 23.54484 | 0.85599 |
| GRU | 0 | 0.55221 | validation_scaled | 265 | 2.69000 | 37.35849 | 17.23795 | 0.82431 |
| GRU | 0 | 0.55221 | test_raw | 272 | 3.18641 | 35.29412 | 22.07505 | 0.86461 |
| GRU | 0 | 0.55221 | test_scaled | 272 | 2.93497 | 35.29412 | 16.36800 | 0.82574 |
| LSTM | 0 | 0.54253 | validation_raw | 265 | 3.28842 | 33.58491 | 22.03867 | 0.89550 |
| LSTM | 0 | 0.54253 | validation_scaled | 265 | 2.96636 | 33.58491 | 14.95392 | 0.85055 |
| LSTM | 0 | 0.54253 | test_raw | 272 | 3.50630 | 29.04412 | 19.19487 | 0.90677 |
| LSTM | 0 | 0.54253 | test_scaled | 272 | 3.28361 | 29.04412 | 11.18017 | 0.85126 |
| Transformer | 0 | 0.54172 | validation_raw | 265 | 3.41231 | 27.54717 | 17.16069 | 0.90617 |
| Transformer | 0 | 0.54172 | validation_scaled | 265 | 3.14680 | 27.54717 | 12.20624 | 0.86661 |
| Transformer | 0 | 0.54172 | test_raw | 272 | 3.61812 | 25.36765 | 15.07405 | 0.91452 |
| Transformer | 0 | 0.54172 | test_scaled | 272 | 3.52227 | 25.36765 | 10.85122 | 0.88442 |

## Prediction certainty groups
Certainty = 1 - normalized entropy; not probability of being correct. Thresholds: validation-window tertiles. Empty bins are N/A.

| Encoder | Seed | Thresholds | Group | Windows | Accuracy | Mean certainty |
|---|---|---|---|---|---|---|
| GRU | 0 | [0.1970503172206478, 0.45378933912685826] | low | 120 | 0.11667 | 0.14860 |
| GRU | 0 | [0.1970503172206478, 0.45378933912685826] | medium | 70 | 0.55714 | 0.30399 |
| GRU | 0 | [0.1970503172206478, 0.45378933912685826] | high | 82 | 0.52439 | 0.73368 |
| LSTM | 0 | [0.1764210438040995, 0.3791455574986573] | low | 135 | 0.17778 | 0.12609 |
| LSTM | 0 | [0.1764210438040995, 0.3791455574986573] | medium | 71 | 0.16901 | 0.22592 |
| LSTM | 0 | [0.1764210438040995, 0.3791455574986573] | high | 66 | 0.65152 | 0.66059 |
| Transformer | 0 | [0.15175815742375276, 0.28096499873566616] | low | 77 | 0.09091 | 0.12926 |
| Transformer | 0 | [0.15175815742375276, 0.28096499873566616] | medium | 109 | 0.17431 | 0.19991 |
| Transformer | 0 | [0.15175815742375276, 0.28096499873566616] | high | 86 | 0.50000 | 0.53844 |

## Policy results by fixed sequence-certainty group
Groups use whole-playbook mean prefix certainty and validation-playbook tertiles, not policy-dependent visited prefixes. Grouping is retrospective, never input to the policy. Descriptive only: groups may differ in scenario/difficulty; no causal claim.

| Encoder | RL | Mode | Group | Seeds with data | Episodes | episode_reward | dwell | depth | protected | exposed | lure_chains | dead_ends | capacity_violations | length | decoys_deployed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| GRU | IPPO | baseline | low | 1 | 3 | 2.667 (n=1; SD N/A) | 2.667 (n=1; SD N/A) | 2.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 1.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 11.000 (n=1; SD N/A) | 11.000 (n=1; SD N/A) | 44.000 (n=1; SD N/A) |
| GRU | IPPO | baseline | medium | 1 | 1 | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 120.000 (n=1; SD N/A) |
| GRU | IPPO | baseline | high | 1 | 3 | 3.000 (n=1; SD N/A) | 3.000 (n=1; SD N/A) | 3.000 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 100.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 35.333 (n=1; SD N/A) | 35.333 (n=1; SD N/A) | 141.333 (n=1; SD N/A) |
| GRU | IPPO | baseline | no_history | 0 | 0 | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| GRU | IPPO | confidence | low | 1 | 3 | 2.667 (n=1; SD N/A) | 2.667 (n=1; SD N/A) | 2.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 1.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 11.000 (n=1; SD N/A) | 11.000 (n=1; SD N/A) | 44.000 (n=1; SD N/A) |
| GRU | IPPO | confidence | medium | 1 | 1 | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 120.000 (n=1; SD N/A) |
| GRU | IPPO | confidence | high | 1 | 3 | 3.000 (n=1; SD N/A) | 3.000 (n=1; SD N/A) | 3.000 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 100.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 35.333 (n=1; SD N/A) | 35.333 (n=1; SD N/A) | 141.333 (n=1; SD N/A) |
| GRU | IPPO | confidence | no_history | 0 | 0 | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| GRU | MAPPO | baseline | low | 1 | 3 | 1.667 (n=1; SD N/A) | 1.667 (n=1; SD N/A) | 1.333 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 9.000 (n=1; SD N/A) | 14.000 (n=1; SD N/A) | 40.667 (n=1; SD N/A) |
| GRU | MAPPO | baseline | medium | 1 | 1 | 1.000 (n=1; SD N/A) | 1.000 (n=1; SD N/A) | 1.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 10.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 61.000 (n=1; SD N/A) |
| GRU | MAPPO | baseline | high | 1 | 3 | 5.333 (n=1; SD N/A) | 5.333 (n=1; SD N/A) | 5.000 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 100.000 (n=1; SD N/A) | 2.333 (n=1; SD N/A) | 0.333 (n=1; SD N/A) | 12.667 (n=1; SD N/A) | 35.333 (n=1; SD N/A) | 82.333 (n=1; SD N/A) |
| GRU | MAPPO | baseline | no_history | 0 | 0 | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| GRU | MAPPO | confidence | low | 1 | 3 | 1.667 (n=1; SD N/A) | 1.667 (n=1; SD N/A) | 1.333 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 0.333 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 6.667 (n=1; SD N/A) | 13.000 (n=1; SD N/A) | 34.333 (n=1; SD N/A) |
| GRU | MAPPO | confidence | medium | 1 | 1 | 1.000 (n=1; SD N/A) | 1.000 (n=1; SD N/A) | 1.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 10.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 61.000 (n=1; SD N/A) |
| GRU | MAPPO | confidence | high | 1 | 3 | 5.333 (n=1; SD N/A) | 5.333 (n=1; SD N/A) | 5.000 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 100.000 (n=1; SD N/A) | 2.333 (n=1; SD N/A) | 0.333 (n=1; SD N/A) | 12.667 (n=1; SD N/A) | 35.333 (n=1; SD N/A) | 82.667 (n=1; SD N/A) |
| GRU | MAPPO | confidence | no_history | 0 | 0 | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| LSTM | IPPO | baseline | low | 1 | 3 | 2.333 (n=1; SD N/A) | 2.333 (n=1; SD N/A) | 1.667 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 1.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 11.000 (n=1; SD N/A) | 11.000 (n=1; SD N/A) | 43.000 (n=1; SD N/A) |
| LSTM | IPPO | baseline | medium | 1 | 3 | 3.000 (n=1; SD N/A) | 3.000 (n=1; SD N/A) | 3.000 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 100.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 35.333 (n=1; SD N/A) | 35.333 (n=1; SD N/A) | 140.333 (n=1; SD N/A) |
| LSTM | IPPO | baseline | high | 1 | 1 | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 119.000 (n=1; SD N/A) |
| LSTM | IPPO | baseline | no_history | 0 | 0 | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| LSTM | IPPO | confidence | low | 1 | 3 | 2.333 (n=1; SD N/A) | 2.333 (n=1; SD N/A) | 1.667 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 1.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 11.000 (n=1; SD N/A) | 11.000 (n=1; SD N/A) | 42.667 (n=1; SD N/A) |
| LSTM | IPPO | confidence | medium | 1 | 3 | 3.000 (n=1; SD N/A) | 3.000 (n=1; SD N/A) | 3.000 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 100.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 35.333 (n=1; SD N/A) | 35.333 (n=1; SD N/A) | 140.333 (n=1; SD N/A) |
| LSTM | IPPO | confidence | high | 1 | 1 | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 119.000 (n=1; SD N/A) |
| LSTM | IPPO | confidence | no_history | 0 | 0 | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| LSTM | MAPPO | baseline | low | 1 | 3 | 2.333 (n=1; SD N/A) | 2.333 (n=1; SD N/A) | 1.667 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 1.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 11.000 (n=1; SD N/A) | 11.000 (n=1; SD N/A) | 42.333 (n=1; SD N/A) |
| LSTM | MAPPO | baseline | medium | 1 | 3 | 3.000 (n=1; SD N/A) | 3.000 (n=1; SD N/A) | 3.000 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 100.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 35.333 (n=1; SD N/A) | 35.333 (n=1; SD N/A) | 140.333 (n=1; SD N/A) |
| LSTM | MAPPO | baseline | high | 1 | 1 | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 119.000 (n=1; SD N/A) |
| LSTM | MAPPO | baseline | no_history | 0 | 0 | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| LSTM | MAPPO | confidence | low | 1 | 3 | 2.333 (n=1; SD N/A) | 2.333 (n=1; SD N/A) | 1.667 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 1.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 11.000 (n=1; SD N/A) | 11.000 (n=1; SD N/A) | 42.333 (n=1; SD N/A) |
| LSTM | MAPPO | confidence | medium | 1 | 3 | 3.000 (n=1; SD N/A) | 3.000 (n=1; SD N/A) | 3.000 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 100.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 35.333 (n=1; SD N/A) | 35.333 (n=1; SD N/A) | 140.333 (n=1; SD N/A) |
| LSTM | MAPPO | confidence | high | 1 | 1 | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 119.000 (n=1; SD N/A) |
| LSTM | MAPPO | confidence | no_history | 0 | 0 | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| Transformer | IPPO | baseline | low | 1 | 2 | 4.000 (n=1; SD N/A) | 4.000 (n=1; SD N/A) | 3.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 50.000 (n=1; SD N/A) | 0.500 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 17.000 (n=1; SD N/A) | 17.000 (n=1; SD N/A) | 68.000 (n=1; SD N/A) |
| Transformer | IPPO | baseline | medium | 1 | 3 | 2.333 (n=1; SD N/A) | 2.333 (n=1; SD N/A) | 1.667 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 26.000 (n=1; SD N/A) | 26.000 (n=1; SD N/A) | 104.000 (n=1; SD N/A) |
| Transformer | IPPO | baseline | high | 1 | 2 | 4.000 (n=1; SD N/A) | 4.000 (n=1; SD N/A) | 2.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 100.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 120.000 (n=1; SD N/A) |
| Transformer | IPPO | baseline | no_history | 0 | 0 | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| Transformer | IPPO | confidence | low | 1 | 2 | 4.000 (n=1; SD N/A) | 4.000 (n=1; SD N/A) | 3.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 50.000 (n=1; SD N/A) | 0.500 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 17.000 (n=1; SD N/A) | 17.000 (n=1; SD N/A) | 68.000 (n=1; SD N/A) |
| Transformer | IPPO | confidence | medium | 1 | 3 | 2.333 (n=1; SD N/A) | 2.333 (n=1; SD N/A) | 1.667 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 26.000 (n=1; SD N/A) | 26.000 (n=1; SD N/A) | 104.000 (n=1; SD N/A) |
| Transformer | IPPO | confidence | high | 1 | 2 | 4.000 (n=1; SD N/A) | 4.000 (n=1; SD N/A) | 2.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 100.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 120.000 (n=1; SD N/A) |
| Transformer | IPPO | confidence | no_history | 0 | 0 | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| Transformer | MAPPO | baseline | low | 1 | 2 | 3.500 (n=1; SD N/A) | 3.500 (n=1; SD N/A) | 2.500 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 50.000 (n=1; SD N/A) | 1.500 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 15.500 (n=1; SD N/A) | 15.500 (n=1; SD N/A) | 61.000 (n=1; SD N/A) |
| Transformer | MAPPO | baseline | medium | 1 | 3 | 2.000 (n=1; SD N/A) | 2.000 (n=1; SD N/A) | 1.333 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 26.000 (n=1; SD N/A) | 26.000 (n=1; SD N/A) | 103.000 (n=1; SD N/A) |
| Transformer | MAPPO | baseline | high | 1 | 2 | 3.500 (n=1; SD N/A) | 3.500 (n=1; SD N/A) | 2.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 100.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 119.000 (n=1; SD N/A) |
| Transformer | MAPPO | baseline | no_history | 0 | 0 | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| Transformer | MAPPO | confidence | low | 1 | 2 | 3.500 (n=1; SD N/A) | 3.500 (n=1; SD N/A) | 2.500 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 50.000 (n=1; SD N/A) | 1.500 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 15.500 (n=1; SD N/A) | 15.500 (n=1; SD N/A) | 61.000 (n=1; SD N/A) |
| Transformer | MAPPO | confidence | medium | 1 | 3 | 2.000 (n=1; SD N/A) | 2.000 (n=1; SD N/A) | 1.333 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 33.333 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 26.000 (n=1; SD N/A) | 26.000 (n=1; SD N/A) | 103.000 (n=1; SD N/A) |
| Transformer | MAPPO | confidence | high | 1 | 2 | 3.500 (n=1; SD N/A) | 3.500 (n=1; SD N/A) | 2.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 100.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 0.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 30.000 (n=1; SD N/A) | 119.000 (n=1; SD N/A) |
| Transformer | MAPPO | confidence | no_history | 0 | 0 | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending |

## Every policy seed

| Encoder | RL | Mode | Seed | Steps | Actor params | Critic params | Best update | Validation dwell | episode_reward | dwell | depth | protected | exposed | lure_chains | dead_ends | capacity_violations | length | decoys_deployed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| GRU | IPPO | baseline | 0 | 16 | 23814 | 38089 | 1 | 2.85714 | 2.42857 | 2.42857 | 2.14286 | 0.14286 | 0.57143 | 0.42857 | 0.00000 | 24.14286 | 24.14286 | 96.57143 |
| GRU | IPPO | confidence | 0 | 16 | 23814 | 38089 | 1 | 2.85714 | 2.42857 | 2.42857 | 2.14286 | 0.14286 | 0.57143 | 0.42857 | 0.00000 | 24.14286 | 24.14286 | 96.57143 |
| GRU | MAPPO | baseline | 0 | 16 | 23814 | 43159 | 1 | 3.85714 | 3.14286 | 3.14286 | 2.85714 | 0.14286 | 0.57143 | 1.00000 | 0.14286 | 10.71429 | 25.42857 | 61.42857 |
| GRU | MAPPO | confidence | 0 | 16 | 23814 | 43159 | 1 | 3.14286 | 3.14286 | 3.14286 | 2.85714 | 0.14286 | 0.57143 | 1.14286 | 0.14286 | 9.71429 | 25.00000 | 58.85714 |
| LSTM | IPPO | baseline | 0 | 16 | 23814 | 38089 | 1 | 2.85714 | 2.28571 | 2.28571 | 2.00000 | 0.14286 | 0.57143 | 0.42857 | 0.00000 | 24.14286 | 24.14286 | 95.57143 |
| LSTM | IPPO | confidence | 0 | 16 | 23814 | 38089 | 1 | 2.85714 | 2.28571 | 2.28571 | 2.00000 | 0.14286 | 0.57143 | 0.42857 | 0.00000 | 24.14286 | 24.14286 | 95.42857 |
| LSTM | MAPPO | baseline | 0 | 16 | 23814 | 43159 | 1 | 2.85714 | 2.28571 | 2.28571 | 2.00000 | 0.14286 | 0.57143 | 0.42857 | 0.00000 | 24.14286 | 24.14286 | 95.28571 |
| LSTM | MAPPO | confidence | 0 | 16 | 23814 | 43159 | 1 | 2.85714 | 2.28571 | 2.28571 | 2.00000 | 0.14286 | 0.57143 | 0.42857 | 0.00000 | 24.14286 | 24.14286 | 95.28571 |
| Transformer | IPPO | baseline | 0 | 16 | 23814 | 38089 | 1 | 3.85714 | 3.28571 | 3.28571 | 2.14286 | 0.14286 | 0.57143 | 0.14286 | 0.00000 | 24.57143 | 24.57143 | 98.28571 |
| Transformer | IPPO | confidence | 0 | 16 | 23814 | 38089 | 1 | 3.85714 | 3.28571 | 3.28571 | 2.14286 | 0.14286 | 0.57143 | 0.14286 | 0.00000 | 24.57143 | 24.57143 | 98.28571 |
| Transformer | MAPPO | baseline | 0 | 16 | 23814 | 43159 | 1 | 2.57143 | 2.85714 | 2.85714 | 1.85714 | 0.14286 | 0.57143 | 0.42857 | 0.00000 | 24.14286 | 24.14286 | 95.57143 |
| Transformer | MAPPO | confidence | 0 | 16 | 23814 | 43159 | 1 | 2.85714 | 2.85714 | 2.85714 | 1.85714 | 0.14286 | 0.57143 | 0.42857 | 0.00000 | 24.14286 | 24.14286 | 95.57143 |

Full episode, calibration-bin and policy-learning records: [CONFIDENCE_DETAILS.md](CONFIDENCE_DETAILS.md). Encoder epoch results: [EPOCH_RESULTS.md](EPOCH_RESULTS.md).
