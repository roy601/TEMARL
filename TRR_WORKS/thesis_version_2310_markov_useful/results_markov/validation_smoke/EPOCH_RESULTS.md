# Every encoder epoch

All values are measured on training or validation data. No test curve is used for selection.
Percent columns are percentages; loss is mean negative log likelihood (nats).

## markov_100 / GRU / seed 0

Selected checkpoint epoch: 2; completed: 2.

| Epoch | Updates | Train NLL | Val NLL | Train Top-1 % | Val Top-1 % | Val Top-3 % | Val Top-5 % | Val Macro-F1 % | Val PPL | Seconds |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 25 | 3.20463 | 3.10431 | 37.60573 | 41.13208 | 57.35849 | 63.77358 | 21.12636 | 22.29389 | 1.11975 |
| 2 | 50 | 2.66914 | 2.55381 | 45.99870 | 47.92453 | 69.43396 | 76.60377 | 28.05474 | 12.85601 | 2.15443 |

## markov_100 / LSTM / seed 0

Selected checkpoint epoch: 2; completed: 2.

| Epoch | Updates | Train NLL | Val NLL | Train Top-1 % | Val Top-1 % | Val Top-3 % | Val Top-5 % | Val Macro-F1 % | Val PPL | Seconds |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 25 | 3.57318 | 3.53727 | 20.29928 | 20.00000 | 36.98113 | 46.79245 | 2.64272 | 34.37305 | 1.09917 |
| 2 | 50 | 3.17960 | 3.19364 | 28.95250 | 26.79245 | 47.54717 | 58.11321 | 7.04742 | 24.37708 | 2.27755 |

## markov_100 / Transformer / seed 0

Selected checkpoint epoch: 2; completed: 2.

| Epoch | Updates | Train NLL | Val NLL | Train Top-1 % | Val Top-1 % | Val Top-3 % | Val Top-5 % | Val Macro-F1 % | Val PPL | Seconds |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 25 | 3.60952 | 3.45431 | 19.45348 | 23.39623 | 44.15094 | 54.33962 | 7.56360 | 31.63636 | 1.54214 |
| 2 | 50 | 3.10690 | 2.96569 | 34.67794 | 38.86792 | 63.39623 | 67.16981 | 17.99125 | 19.40805 | 2.96618 |

## real_100 / GRU / seed 0

Selected checkpoint epoch: 2; completed: 2.

| Epoch | Updates | Train NLL | Val NLL | Train Top-1 % | Val Top-1 % | Val Top-3 % | Val Top-5 % | Val Macro-F1 % | Val PPL | Seconds |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 13 | 3.50960 | 3.48673 | 27.13178 | 27.92453 | 45.66038 | 51.32075 | 8.70059 | 32.67882 | 0.75267 |
| 2 | 26 | 3.01271 | 3.03217 | 39.66408 | 37.35849 | 65.28302 | 70.56604 | 18.34606 | 20.74224 | 1.39618 |

## real_100 / LSTM / seed 0

Selected checkpoint epoch: 2; completed: 2.

| Epoch | Updates | Train NLL | Val NLL | Train Top-1 % | Val Top-1 % | Val Top-3 % | Val Top-5 % | Val Macro-F1 % | Val PPL | Seconds |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 13 | 3.63688 | 3.71644 | 20.80103 | 20.00000 | 32.45283 | 39.24528 | 2.32992 | 41.11790 | 0.61077 |
| 2 | 26 | 3.21830 | 3.43115 | 28.29457 | 22.26415 | 44.15094 | 53.96226 | 4.92158 | 30.91207 | 1.20446 |

## real_100 / Transformer / seed 0

Selected checkpoint epoch: 2; completed: 2.

| Epoch | Updates | Train NLL | Val NLL | Train Top-1 % | Val Top-1 % | Val Top-3 % | Val Top-5 % | Val Macro-F1 % | Val PPL | Seconds |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 13 | 3.91735 | 3.80266 | 16.92506 | 21.50943 | 32.45283 | 38.86792 | 7.15215 | 44.82018 | 0.83514 |
| 2 | 26 | 3.52355 | 3.40242 | 22.60982 | 28.30189 | 46.03774 | 56.98113 | 10.31902 | 30.03656 | 1.55504 |

## repeat_100 / GRU / seed 0

Selected checkpoint epoch: 2; completed: 2.

| Epoch | Updates | Train NLL | Val NLL | Train Top-1 % | Val Top-1 % | Val Top-3 % | Val Top-5 % | Val Macro-F1 % | Val PPL | Seconds |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 25 | 3.03488 | 3.05717 | 40.92388 | 40.75472 | 63.01887 | 69.81132 | 22.39986 | 21.26726 | 1.14849 |
| 2 | 50 | 2.39500 | 2.46486 | 53.54587 | 52.83019 | 75.47170 | 80.00000 | 37.15296 | 11.76187 | 2.52967 |

## repeat_100 / LSTM / seed 0

Selected checkpoint epoch: 2; completed: 2.

| Epoch | Updates | Train NLL | Val NLL | Train Top-1 % | Val Top-1 % | Val Top-3 % | Val Top-5 % | Val Macro-F1 % | Val PPL | Seconds |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 25 | 3.23376 | 3.43098 | 28.62720 | 23.77358 | 45.66038 | 53.96226 | 6.65683 | 30.90697 | 1.13223 |
| 2 | 50 | 2.66945 | 3.03437 | 46.84450 | 33.96226 | 56.60377 | 64.15094 | 15.90609 | 20.78781 | 2.70553 |

## repeat_100 / Transformer / seed 0

Selected checkpoint epoch: 2; completed: 2.

| Epoch | Updates | Train NLL | Val NLL | Train Top-1 % | Val Top-1 % | Val Top-3 % | Val Top-5 % | Val Macro-F1 % | Val PPL | Seconds |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 25 | 3.53116 | 3.43055 | 22.38126 | 28.30189 | 43.39623 | 57.35849 | 8.78556 | 30.89376 | 1.31774 |
| 2 | 50 | 2.95134 | 2.91570 | 41.89980 | 44.52830 | 61.13208 | 68.30189 | 23.78239 | 18.46170 | 2.70520 |

