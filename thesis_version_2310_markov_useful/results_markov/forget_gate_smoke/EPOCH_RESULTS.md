# Every encoder epoch

All values are measured on training or validation data. No test curve is used for selection.
Percent columns are percentages; loss is mean negative log likelihood (nats).

## markov_100 / GRU / seed 0

Primary checkpoint epoch: 2; validation-best (secondary): 2.

| Epoch | Updates | Train NLL | Val NLL | Train Top-1 % | Val Top-1 % | Val Top-3 % | Val Top-5 % | Val Macro-F1 % | Val PPL | Seconds |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 25 | 3.20463 | 3.10431 | 37.60573 | 41.13208 | 57.35849 | 63.77358 | 21.12636 | 22.29389 | 1.42194 |
| 2 | 50 | 2.66914 | 2.55381 | 45.99870 | 47.92453 | 69.43396 | 76.60377 | 28.05474 | 12.85601 | 2.34204 |

## markov_100 / LSTM / seed 0

Primary checkpoint epoch: 2; validation-best (secondary): 2.

| Epoch | Updates | Train NLL | Val NLL | Train Top-1 % | Val Top-1 % | Val Top-3 % | Val Top-5 % | Val Macro-F1 % | Val PPL | Seconds |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 25 | 3.51389 | 3.34738 | 24.91867 | 30.94340 | 52.07547 | 58.86792 | 10.13043 | 28.42818 | 1.33180 |
| 2 | 50 | 2.89730 | 2.75276 | 42.74561 | 47.16981 | 67.92453 | 75.84906 | 24.99309 | 15.68589 | 2.80240 |

## markov_100 / Transformer / seed 0

Primary checkpoint epoch: 2; validation-best (secondary): 2.

| Epoch | Updates | Train NLL | Val NLL | Train Top-1 % | Val Top-1 % | Val Top-3 % | Val Top-5 % | Val Macro-F1 % | Val PPL | Seconds |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 25 | 3.60952 | 3.45431 | 19.45348 | 23.39623 | 44.15094 | 54.33962 | 7.56360 | 31.63636 | 3.63907 |
| 2 | 50 | 3.10690 | 2.96569 | 34.67794 | 38.86792 | 63.39623 | 67.16981 | 17.99125 | 19.40805 | 7.30767 |

## real_100 / GRU / seed 0

Primary checkpoint epoch: 2; validation-best (secondary): 2.

| Epoch | Updates | Train NLL | Val NLL | Train Top-1 % | Val Top-1 % | Val Top-3 % | Val Top-5 % | Val Macro-F1 % | Val PPL | Seconds |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 13 | 3.50960 | 3.48673 | 27.13178 | 27.92453 | 45.66038 | 51.32075 | 8.70059 | 32.67882 | 1.56495 |
| 2 | 26 | 3.01271 | 3.03217 | 39.66408 | 37.35849 | 65.28302 | 70.56604 | 18.34606 | 20.74224 | 3.35031 |

## real_100 / LSTM / seed 0

Primary checkpoint epoch: 2; validation-best (secondary): 2.

| Epoch | Updates | Train NLL | Val NLL | Train Top-1 % | Val Top-1 % | Val Top-3 % | Val Top-5 % | Val Macro-F1 % | Val PPL | Seconds |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 13 | 3.89309 | 3.76450 | 18.34625 | 24.90566 | 35.09434 | 41.50943 | 3.95763 | 43.14224 | 1.52784 |
| 2 | 26 | 3.37416 | 3.28992 | 30.62016 | 34.33962 | 54.33962 | 63.01887 | 11.89116 | 26.84062 | 3.13777 |

## real_100 / Transformer / seed 0

Primary checkpoint epoch: 2; validation-best (secondary): 2.

| Epoch | Updates | Train NLL | Val NLL | Train Top-1 % | Val Top-1 % | Val Top-3 % | Val Top-5 % | Val Macro-F1 % | Val PPL | Seconds |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 13 | 3.91735 | 3.80266 | 16.92506 | 21.50943 | 32.45283 | 38.86792 | 7.15215 | 44.82018 | 1.98152 |
| 2 | 26 | 3.52355 | 3.40242 | 22.60982 | 28.30189 | 46.03774 | 56.98113 | 10.31902 | 30.03656 | 3.85773 |

## repeat_100 / GRU / seed 0

Primary checkpoint epoch: 2; validation-best (secondary): 2.

| Epoch | Updates | Train NLL | Val NLL | Train Top-1 % | Val Top-1 % | Val Top-3 % | Val Top-5 % | Val Macro-F1 % | Val PPL | Seconds |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 25 | 3.03488 | 3.05717 | 40.92388 | 40.75472 | 63.01887 | 69.81132 | 22.39986 | 21.26726 | 1.36561 |
| 2 | 50 | 2.39500 | 2.46486 | 53.54587 | 52.83019 | 75.47170 | 80.00000 | 37.15296 | 11.76187 | 2.43485 |

## repeat_100 / LSTM / seed 0

Primary checkpoint epoch: 2; validation-best (secondary): 2.

| Epoch | Updates | Train NLL | Val NLL | Train Top-1 % | Val Top-1 % | Val Top-3 % | Val Top-5 % | Val Macro-F1 % | Val PPL | Seconds |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 25 | 3.39829 | 3.31395 | 27.19584 | 29.43396 | 52.45283 | 58.49057 | 8.56448 | 27.49342 | 1.30686 |
| 2 | 50 | 2.66869 | 2.66808 | 45.02277 | 44.52830 | 70.18868 | 77.35849 | 20.72715 | 14.41233 | 2.26506 |

## repeat_100 / Transformer / seed 0

Primary checkpoint epoch: 2; validation-best (secondary): 2.

| Epoch | Updates | Train NLL | Val NLL | Train Top-1 % | Val Top-1 % | Val Top-3 % | Val Top-5 % | Val Macro-F1 % | Val PPL | Seconds |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 25 | 3.53116 | 3.43055 | 22.38126 | 28.30189 | 43.39623 | 57.35849 | 8.78556 | 30.89376 | 1.78922 |
| 2 | 50 | 2.95134 | 2.91570 | 41.89980 | 44.52830 | 61.13208 | 68.30189 | 23.78239 | 18.46169 | 3.28178 |

