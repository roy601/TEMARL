# Every encoder epoch

All values are measured on training or validation data. No test curve is used for selection.
Percent columns are percentages; loss is mean negative log likelihood (nats).

## markov_100 / GRU / seed 0

Primary checkpoint epoch: 2; validation-best (secondary): 2.

| Epoch | Updates | Train NLL | Val NLL | Train Top-1 % | Val Top-1 % | Val Top-3 % | Val Top-5 % | Val Macro-F1 % | Val PPL | Seconds |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 25 | 3.20390 | 3.10538 | 35.65387 | 38.49057 | 57.35849 | 63.39623 | 18.01339 | 22.31778 | 0.92127 |
| 2 | 50 | 2.66947 | 2.55614 | 46.19388 | 48.67925 | 69.43396 | 76.22642 | 28.21339 | 12.88602 | 1.97361 |

## markov_100 / LSTM / seed 0

Primary checkpoint epoch: 2; validation-best (secondary): 2.

| Epoch | Updates | Train NLL | Val NLL | Train Top-1 % | Val Top-1 % | Val Top-3 % | Val Top-5 % | Val Macro-F1 % | Val PPL | Seconds |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 25 | 3.51264 | 3.34595 | 24.91867 | 30.94340 | 52.45283 | 60.00000 | 10.13043 | 28.38748 | 0.74840 |
| 2 | 50 | 2.89839 | 2.75261 | 41.37931 | 46.79245 | 67.16981 | 75.84906 | 22.60275 | 15.68347 | 1.55079 |

## markov_100 / Transformer / seed 0

Primary checkpoint epoch: 2; validation-best (secondary): 2.

| Epoch | Updates | Train NLL | Val NLL | Train Top-1 % | Val Top-1 % | Val Top-3 % | Val Top-5 % | Val Macro-F1 % | Val PPL | Seconds |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 25 | 3.61445 | 3.45337 | 19.45348 | 21.88679 | 43.01887 | 53.96226 | 6.14757 | 31.60663 | 0.22434 |
| 2 | 50 | 3.12429 | 2.97526 | 34.15745 | 37.35849 | 61.50943 | 66.41509 | 17.04972 | 19.59465 | 0.44996 |

## real_100 / GRU / seed 0

Primary checkpoint epoch: 2; validation-best (secondary): 2.

| Epoch | Updates | Train NLL | Val NLL | Train Top-1 % | Val Top-1 % | Val Top-3 % | Val Top-5 % | Val Macro-F1 % | Val PPL | Seconds |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 13 | 3.50831 | 3.47924 | 27.64858 | 28.30189 | 47.16981 | 51.69811 | 8.90701 | 32.43517 | 0.50024 |
| 2 | 26 | 3.01275 | 3.02414 | 39.79328 | 37.35849 | 64.90566 | 71.32075 | 18.36131 | 20.57630 | 1.00999 |

## real_100 / LSTM / seed 0

Primary checkpoint epoch: 2; validation-best (secondary): 2.

| Epoch | Updates | Train NLL | Val NLL | Train Top-1 % | Val Top-1 % | Val Top-3 % | Val Top-5 % | Val Macro-F1 % | Val PPL | Seconds |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 13 | 3.89249 | 3.76509 | 18.73385 | 24.90566 | 34.71698 | 41.50943 | 3.91268 | 43.16757 | 0.39959 |
| 2 | 26 | 3.37193 | 3.28842 | 29.32817 | 33.58491 | 52.07547 | 62.26415 | 9.88712 | 26.80061 | 0.82167 |

## real_100 / Transformer / seed 0

Primary checkpoint epoch: 2; validation-best (secondary): 2.

| Epoch | Updates | Train NLL | Val NLL | Train Top-1 % | Val Top-1 % | Val Top-3 % | Val Top-5 % | Val Macro-F1 % | Val PPL | Seconds |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 13 | 3.91693 | 3.80647 | 15.50388 | 20.00000 | 30.94340 | 39.62264 | 7.03381 | 44.99114 | 0.34286 |
| 2 | 26 | 3.52018 | 3.41231 | 22.09302 | 27.54717 | 47.16981 | 55.47170 | 9.37532 | 30.33518 | 0.47613 |

## repeat_100 / GRU / seed 0

Primary checkpoint epoch: 2; validation-best (secondary): 2.

| Epoch | Updates | Train NLL | Val NLL | Train Top-1 % | Val Top-1 % | Val Top-3 % | Val Top-5 % | Val Macro-F1 % | Val PPL | Seconds |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 25 | 3.03403 | 3.06210 | 42.61548 | 41.88679 | 63.01887 | 70.18868 | 23.03710 | 21.37247 | 0.93746 |
| 2 | 50 | 2.39317 | 2.46690 | 53.93624 | 52.83019 | 75.09434 | 80.00000 | 37.18183 | 11.78589 | 2.01288 |

## repeat_100 / LSTM / seed 0

Primary checkpoint epoch: 2; validation-best (secondary): 2.

| Epoch | Updates | Train NLL | Val NLL | Train Top-1 % | Val Top-1 % | Val Top-3 % | Val Top-5 % | Val Macro-F1 % | Val PPL | Seconds |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 25 | 3.40013 | 3.31754 | 27.32596 | 29.43396 | 53.58491 | 58.86792 | 8.48091 | 27.59240 | 0.78205 |
| 2 | 50 | 2.66982 | 2.66720 | 45.15290 | 44.15094 | 70.94340 | 76.60377 | 20.37757 | 14.39960 | 1.60395 |

## repeat_100 / Transformer / seed 0

Primary checkpoint epoch: 2; validation-best (secondary): 2.

| Epoch | Updates | Train NLL | Val NLL | Train Top-1 % | Val Top-1 % | Val Top-3 % | Val Top-5 % | Val Macro-F1 % | Val PPL | Seconds |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 25 | 3.54527 | 3.44172 | 19.77879 | 24.90566 | 44.15094 | 56.22642 | 6.84403 | 31.24060 | 0.21541 |
| 2 | 50 | 2.96362 | 2.91905 | 40.20820 | 43.39623 | 63.39623 | 69.05660 | 21.70025 | 18.52368 | 0.43942 |

