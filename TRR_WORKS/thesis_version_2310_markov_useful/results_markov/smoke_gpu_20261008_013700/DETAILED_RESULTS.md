# Per-seed prediction and per-original-run results

Probabilities/accuracies are fractions unless marked percent.

## markov_100 / GRU / seed 0

Original runs: 22; independent groups: 22; synthetic runs: 22; train windows: 1537; optimizer updates: 50.

| Metric | Final-epoch validation | Final-epoch test | Validation-best test (secondary) |
|---|---|---|---|
| top1 | 0.48679 | 0.44853 | 0.44853 |
| top3 | 0.69434 | 0.61765 | 0.61765 |
| top5 | 0.76226 | 0.66912 | 0.66912 |
| macro_f1 | 0.28213 | 0.31432 | 0.31432 |
| nll | 2.55614 | 2.81529 | 2.81529 |
| log_likelihood | -677.37788 | -765.75879 | -765.75879 |
| perplexity | 12.88602 | 16.69801 | 16.69801 |
| run_macro_top1 | 0.44591 | 0.42260 | 0.42260 |
| n | 265 | 272 | 272 |
| f1_label_count | 52 | 51 | 51 |

| Test run | Windows | Top-1 % | NLL |
|---|---|---|---|
| scenario_1_b_c.j2 | 43 | 60.46512 | 2.10522 |
| scenario_1_c_c.j2 | 43 | 58.13953 | 2.14697 |
| scenario_1_d_a.j2 | 50 | 64.00000 | 1.98488 |
| scenario_1_e_a.j2 | 45 | 57.77778 | 2.16311 |
| scenario_3_a_b.j2 | 24 | 25.00000 | 3.82067 |
| scenario_3_b_b.j2 | 23 | 30.43478 | 3.54789 |
| scenario_6_c.j2 | 44 | 0.00000 | 4.84167 |

## markov_100 / LSTM / seed 0

Original runs: 22; independent groups: 22; synthetic runs: 22; train windows: 1537; optimizer updates: 50.

| Metric | Final-epoch validation | Final-epoch test | Validation-best test (secondary) |
|---|---|---|---|
| top1 | 0.46792 | 0.43015 | 0.43015 |
| top3 | 0.67170 | 0.61397 | 0.61397 |
| top5 | 0.75849 | 0.64706 | 0.64706 |
| macro_f1 | 0.22603 | 0.24646 | 0.24646 |
| nll | 2.75261 | 3.10762 | 3.10762 |
| log_likelihood | -729.44095 | -845.27284 | -845.27284 |
| perplexity | 15.68347 | 22.36776 | 22.36776 |
| run_macro_top1 | 0.42256 | 0.39180 | 0.39180 |
| n | 265 | 272 | 272 |
| f1_label_count | 52 | 51 | 51 |

| Test run | Windows | Top-1 % | NLL |
|---|---|---|---|
| scenario_1_b_c.j2 | 43 | 60.46512 | 2.37760 |
| scenario_1_c_c.j2 | 43 | 58.13953 | 2.35147 |
| scenario_1_d_a.j2 | 50 | 64.00000 | 2.21984 |
| scenario_1_e_a.j2 | 45 | 57.77778 | 2.40736 |
| scenario_3_a_b.j2 | 24 | 20.83333 | 3.98757 |
| scenario_3_b_b.j2 | 23 | 13.04348 | 3.82907 |
| scenario_6_c.j2 | 44 | 0.00000 | 5.42795 |

## markov_100 / Transformer / seed 0

Original runs: 22; independent groups: 22; synthetic runs: 22; train windows: 1537; optimizer updates: 50.

| Metric | Final-epoch validation | Final-epoch test | Validation-best test (secondary) |
|---|---|---|---|
| top1 | 0.37358 | 0.33456 | 0.33456 |
| top3 | 0.61509 | 0.55882 | 0.55882 |
| top5 | 0.66415 | 0.59926 | 0.59926 |
| macro_f1 | 0.17050 | 0.16669 | 0.16669 |
| nll | 2.97526 | 3.26336 | 3.26336 |
| log_likelihood | -788.44295 | -887.63411 | -887.63411 |
| perplexity | 19.59465 | 26.13723 | 26.13723 |
| run_macro_top1 | 0.31505 | 0.28652 | 0.28652 |
| n | 265 | 272 | 272 |
| f1_label_count | 52 | 51 | 51 |

| Test run | Windows | Top-1 % | NLL |
|---|---|---|---|
| scenario_1_b_c.j2 | 43 | 48.83721 | 2.58718 |
| scenario_1_c_c.j2 | 43 | 48.83721 | 2.50209 |
| scenario_1_d_a.j2 | 50 | 54.00000 | 2.35053 |
| scenario_1_e_a.j2 | 45 | 48.88889 | 2.53948 |
| scenario_3_a_b.j2 | 24 | 0.00000 | 4.26539 |
| scenario_3_b_b.j2 | 23 | 0.00000 | 4.04981 |
| scenario_6_c.j2 | 44 | 0.00000 | 5.48812 |

## real_100 / GRU / seed 0

Original runs: 22; independent groups: 22; synthetic runs: 0; train windows: 774; optimizer updates: 26.

| Metric | Final-epoch validation | Final-epoch test | Validation-best test (secondary) |
|---|---|---|---|
| top1 | 0.37358 | 0.35294 | 0.35294 |
| top3 | 0.64906 | 0.58456 | 0.58456 |
| top5 | 0.71321 | 0.61765 | 0.61765 |
| macro_f1 | 0.18361 | 0.20569 | 0.20569 |
| nll | 3.02414 | 3.18641 | 3.18641 |
| log_likelihood | -801.39711 | -866.70473 | -866.70473 |
| perplexity | 20.57630 | 24.20150 | 24.20150 |
| run_macro_top1 | 0.34439 | 0.33510 | 0.33510 |
| n | 265 | 272 | 272 |
| f1_label_count | 52 | 51 | 51 |

| Test run | Windows | Top-1 % | NLL |
|---|---|---|---|
| scenario_1_b_c.j2 | 43 | 48.83721 | 2.60830 |
| scenario_1_c_c.j2 | 43 | 44.18605 | 2.68274 |
| scenario_1_d_a.j2 | 50 | 50.00000 | 2.56198 |
| scenario_1_e_a.j2 | 45 | 44.44444 | 2.71673 |
| scenario_3_a_b.j2 | 24 | 16.66667 | 4.06580 |
| scenario_3_b_b.j2 | 23 | 30.43478 | 3.75885 |
| scenario_6_c.j2 | 44 | 0.00000 | 4.65466 |

## real_100 / LSTM / seed 0

Original runs: 22; independent groups: 22; synthetic runs: 0; train windows: 774; optimizer updates: 26.

| Metric | Final-epoch validation | Final-epoch test | Validation-best test (secondary) |
|---|---|---|---|
| top1 | 0.33585 | 0.29044 | 0.29044 |
| top3 | 0.52075 | 0.47059 | 0.47059 |
| top5 | 0.62264 | 0.55882 | 0.55882 |
| macro_f1 | 0.09887 | 0.09139 | 0.09139 |
| nll | 3.28842 | 3.50630 | 3.50630 |
| log_likelihood | -871.43249 | -953.71337 | -953.71337 |
| perplexity | 26.80061 | 33.32471 | 33.32471 |
| run_macro_top1 | 0.28988 | 0.25572 | 0.25572 |
| n | 265 | 272 | 272 |
| f1_label_count | 52 | 51 | 51 |

| Test run | Windows | Top-1 % | NLL |
|---|---|---|---|
| scenario_1_b_c.j2 | 43 | 41.86047 | 3.02313 |
| scenario_1_c_c.j2 | 43 | 44.18605 | 2.97055 |
| scenario_1_d_a.j2 | 50 | 40.00000 | 2.93543 |
| scenario_1_e_a.j2 | 45 | 44.44444 | 2.98788 |
| scenario_3_a_b.j2 | 24 | 4.16667 | 4.23519 |
| scenario_3_b_b.j2 | 23 | 4.34783 | 4.10579 |
| scenario_6_c.j2 | 44 | 0.00000 | 4.97003 |

## real_100 / Transformer / seed 0

Original runs: 22; independent groups: 22; synthetic runs: 0; train windows: 774; optimizer updates: 26.

| Metric | Final-epoch validation | Final-epoch test | Validation-best test (secondary) |
|---|---|---|---|
| top1 | 0.27547 | 0.25368 | 0.25368 |
| top3 | 0.47170 | 0.42279 | 0.42279 |
| top5 | 0.55472 | 0.50368 | 0.50368 |
| macro_f1 | 0.09375 | 0.10013 | 0.10013 |
| nll | 3.41231 | 3.61812 | 3.61812 |
| log_likelihood | -904.26162 | -984.13000 | -984.13000 |
| perplexity | 30.33518 | 37.26763 | 37.26763 |
| run_macro_top1 | 0.23285 | 0.21696 | 0.21696 |
| n | 265 | 272 | 272 |
| f1_label_count | 52 | 51 | 51 |

| Test run | Windows | Top-1 % | NLL |
|---|---|---|---|
| scenario_1_b_c.j2 | 43 | 34.88372 | 3.11083 |
| scenario_1_c_c.j2 | 43 | 37.20930 | 3.05182 |
| scenario_1_d_a.j2 | 50 | 42.00000 | 3.03021 |
| scenario_1_e_a.j2 | 45 | 37.77778 | 3.07127 |
| scenario_3_a_b.j2 | 24 | 0.00000 | 4.33769 |
| scenario_3_b_b.j2 | 23 | 0.00000 | 4.18928 |
| scenario_6_c.j2 | 44 | 0.00000 | 5.20366 |

## repeat_100 / GRU / seed 0

Original runs: 22; independent groups: 22; synthetic runs: 0; train windows: 1537; optimizer updates: 50.

| Metric | Final-epoch validation | Final-epoch test | Validation-best test (secondary) |
|---|---|---|---|
| top1 | 0.52830 | 0.48162 | 0.48162 |
| top3 | 0.75094 | 0.66912 | 0.66912 |
| top5 | 0.80000 | 0.69853 | 0.69853 |
| macro_f1 | 0.37182 | 0.37683 | 0.37683 |
| nll | 2.46690 | 2.73495 | 2.73495 |
| log_likelihood | -653.72939 | -743.90737 | -743.90737 |
| perplexity | 11.78589 | 15.40903 | 15.40903 |
| run_macro_top1 | 0.49439 | 0.45725 | 0.45725 |
| n | 265 | 272 | 272 |
| f1_label_count | 52 | 51 | 51 |

| Test run | Windows | Top-1 % | NLL |
|---|---|---|---|
| scenario_1_b_c.j2 | 43 | 65.11628 | 1.98023 |
| scenario_1_c_c.j2 | 43 | 62.79070 | 2.08908 |
| scenario_1_d_a.j2 | 50 | 66.00000 | 1.97320 |
| scenario_1_e_a.j2 | 45 | 62.22222 | 2.12011 |
| scenario_3_a_b.j2 | 24 | 29.16667 | 3.60924 |
| scenario_3_b_b.j2 | 23 | 34.78261 | 3.29215 |
| scenario_6_c.j2 | 44 | 0.00000 | 4.83001 |

## repeat_100 / LSTM / seed 0

Original runs: 22; independent groups: 22; synthetic runs: 0; train windows: 1537; optimizer updates: 50.

| Metric | Final-epoch validation | Final-epoch test | Validation-best test (secondary) |
|---|---|---|---|
| top1 | 0.44151 | 0.40441 | 0.40441 |
| top3 | 0.70943 | 0.64338 | 0.64338 |
| top5 | 0.76604 | 0.65809 | 0.65809 |
| macro_f1 | 0.20378 | 0.23049 | 0.23049 |
| nll | 2.66720 | 3.03123 | 3.03123 |
| log_likelihood | -706.80812 | -824.49427 | -824.49427 |
| perplexity | 14.39960 | 20.72268 | 20.72268 |
| run_macro_top1 | 0.40420 | 0.37968 | 0.37968 |
| n | 265 | 272 | 272 |
| f1_label_count | 52 | 51 | 51 |

| Test run | Windows | Top-1 % | NLL |
|---|---|---|---|
| scenario_1_b_c.j2 | 43 | 58.13953 | 2.24673 |
| scenario_1_c_c.j2 | 43 | 51.16279 | 2.28914 |
| scenario_1_d_a.j2 | 50 | 54.00000 | 2.28221 |
| scenario_1_e_a.j2 | 45 | 55.55556 | 2.33502 |
| scenario_3_a_b.j2 | 24 | 20.83333 | 3.71864 |
| scenario_3_b_b.j2 | 23 | 26.08696 | 3.55060 |
| scenario_6_c.j2 | 44 | 0.00000 | 5.43987 |

## repeat_100 / Transformer / seed 0

Original runs: 22; independent groups: 22; synthetic runs: 0; train windows: 1537; optimizer updates: 50.

| Metric | Final-epoch validation | Final-epoch test | Validation-best test (secondary) |
|---|---|---|---|
| top1 | 0.43396 | 0.39706 | 0.39706 |
| top3 | 0.63396 | 0.59559 | 0.59559 |
| top5 | 0.69057 | 0.64706 | 0.64706 |
| macro_f1 | 0.21700 | 0.22559 | 0.22559 |
| nll | 2.91905 | 3.21465 | 3.21465 |
| log_likelihood | -773.54826 | -874.38545 | -874.38545 |
| perplexity | 18.52368 | 24.89464 | 24.89464 |
| run_macro_top1 | 0.36600 | 0.35167 | 0.35167 |
| n | 265 | 272 | 272 |
| f1_label_count | 52 | 51 | 51 |

| Test run | Windows | Top-1 % | NLL |
|---|---|---|---|
| scenario_1_b_c.j2 | 43 | 55.81395 | 2.44133 |
| scenario_1_c_c.j2 | 43 | 55.81395 | 2.42517 |
| scenario_1_d_a.j2 | 50 | 64.00000 | 2.43901 |
| scenario_1_e_a.j2 | 45 | 53.33333 | 2.44957 |
| scenario_3_a_b.j2 | 24 | 4.16667 | 4.11297 |
| scenario_3_b_b.j2 | 23 | 13.04348 | 3.78958 |
| scenario_6_c.j2 | 44 | 0.00000 | 5.61529 |

## markov_100 / GRU+IPPO / seed 0

Environment steps: 16; PPO epochs per rollout: 1; selected update: 1.

| Metric | Test | Test with history zeroed |
|---|---|---|
| dwell | 3.00000 | 2.85714 |
| depth | 2.71429 | 2.71429 |
| protected | 0.14286 | 0.14286 |
| exposed | 0.71429 | 0.71429 |
| lure_chains | 0.57143 | 0.28571 |
| dead_ends | 0.00000 | 0.00000 |
| capacity_violations | 24.14286 | 24.14286 |
| length | 24.14286 | 24.14286 |
| decoys_deployed | 96.57143 | 96.57143 |

| Run | Environment repeat | Dwell | Depth | Protected | Exposed | Length |
|---|---|---|---|---|---|---|
| scenario_1_b_c.j2 | 0 | 5.00000 | 5.00000 | 1.00000 | 1.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 3.00000 | 3.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 3.00000 | 3.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 |
| scenario_3_b_b.j2 | 0 | 6.00000 | 4.00000 | 0.00000 | 1.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 |

## markov_100 / GRU+MAPPO / seed 0

Environment steps: 16; PPO epochs per rollout: 1; selected update: 1.

| Metric | Test | Test with history zeroed |
|---|---|---|
| dwell | 2.57143 | 4.42857 |
| depth | 2.42857 | 4.14286 |
| protected | 0.28571 | 0.14286 |
| exposed | 0.57143 | 0.57143 |
| lure_chains | 0.28571 | 1.57143 |
| dead_ends | 0.14286 | 0.00000 |
| capacity_violations | 19.00000 | 15.71429 |
| length | 25.42857 | 26.42857 |
| decoys_deployed | 73.42857 | 68.57143 |

| Run | Environment repeat | Dwell | Depth | Protected | Exposed | Length |
|---|---|---|---|---|---|---|
| scenario_1_b_c.j2 | 0 | 7.00000 | 7.00000 | 1.00000 | 1.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 1.00000 | 1.00000 | 0.00000 | 0.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 5.00000 | 4.00000 | 1.00000 | 0.00000 | 25.00000 |
| scenario_3_b_b.j2 | 0 | 1.00000 | 1.00000 | 0.00000 | 1.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 |

## markov_100 / LSTM+IPPO / seed 0

Environment steps: 16; PPO epochs per rollout: 1; selected update: 1.

| Metric | Test | Test with history zeroed |
|---|---|---|
| dwell | 2.42857 | 2.42857 |
| depth | 2.14286 | 2.14286 |
| protected | 0.14286 | 0.14286 |
| exposed | 0.57143 | 0.57143 |
| lure_chains | 0.42857 | 0.42857 |
| dead_ends | 0.00000 | 0.00000 |
| capacity_violations | 24.14286 | 24.14286 |
| length | 24.14286 | 24.14286 |
| decoys_deployed | 96.57143 | 96.57143 |

| Run | Environment repeat | Dwell | Depth | Protected | Exposed | Length |
|---|---|---|---|---|---|---|
| scenario_1_b_c.j2 | 0 | 4.00000 | 4.00000 | 1.00000 | 1.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 3.00000 | 3.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 |
| scenario_3_b_b.j2 | 0 | 6.00000 | 4.00000 | 0.00000 | 1.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 |

## markov_100 / LSTM+MAPPO / seed 0

Environment steps: 16; PPO epochs per rollout: 1; selected update: 1.

| Metric | Test | Test with history zeroed |
|---|---|---|
| dwell | 2.28571 | 2.28571 |
| depth | 2.00000 | 2.00000 |
| protected | 0.14286 | 0.14286 |
| exposed | 0.57143 | 0.57143 |
| lure_chains | 0.42857 | 0.42857 |
| dead_ends | 0.00000 | 0.00000 |
| capacity_violations | 24.14286 | 24.14286 |
| length | 24.14286 | 24.14286 |
| decoys_deployed | 95.57143 | 95.57143 |

| Run | Environment repeat | Dwell | Depth | Protected | Exposed | Length |
|---|---|---|---|---|---|---|
| scenario_1_b_c.j2 | 0 | 4.00000 | 4.00000 | 1.00000 | 1.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 3.00000 | 3.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 |
| scenario_3_b_b.j2 | 0 | 5.00000 | 3.00000 | 0.00000 | 1.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 |

## markov_100 / Transformer+IPPO / seed 0

Environment steps: 16; PPO epochs per rollout: 1; selected update: 1.

| Metric | Test | Test with history zeroed |
|---|---|---|
| dwell | 2.28571 | 2.71429 |
| depth | 2.14286 | 2.71429 |
| protected | 0.14286 | 0.14286 |
| exposed | 0.71429 | 0.71429 |
| lure_chains | 0.14286 | 0.14286 |
| dead_ends | 0.00000 | 0.00000 |
| capacity_violations | 24.14286 | 24.14286 |
| length | 24.14286 | 24.14286 |
| decoys_deployed | 96.57143 | 96.57143 |

| Run | Environment repeat | Dwell | Depth | Protected | Exposed | Length |
|---|---|---|---|---|---|---|
| scenario_1_b_c.j2 | 0 | 5.00000 | 5.00000 | 1.00000 | 1.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 3.00000 | 3.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 2.00000 | 1.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 1.00000 | 1.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 |
| scenario_3_b_b.j2 | 0 | 3.00000 | 3.00000 | 0.00000 | 1.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 |

## markov_100 / Transformer+MAPPO / seed 0

Environment steps: 16; PPO epochs per rollout: 1; selected update: 1.

| Metric | Test | Test with history zeroed |
|---|---|---|
| dwell | 2.14286 | 2.14286 |
| depth | 1.85714 | 1.85714 |
| protected | 0.14286 | 0.14286 |
| exposed | 0.57143 | 0.57143 |
| lure_chains | 0.42857 | 0.42857 |
| dead_ends | 0.00000 | 0.00000 |
| capacity_violations | 23.14286 | 23.14286 |
| length | 24.14286 | 24.14286 |
| decoys_deployed | 94.57143 | 94.57143 |

| Run | Environment repeat | Dwell | Depth | Protected | Exposed | Length |
|---|---|---|---|---|---|---|
| scenario_1_b_c.j2 | 0 | 4.00000 | 4.00000 | 1.00000 | 1.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 1.00000 | 1.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 3.00000 | 3.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 |
| scenario_3_b_b.j2 | 0 | 5.00000 | 3.00000 | 0.00000 | 1.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 |

## real_100 / GRU+IPPO / seed 0

Environment steps: 16; PPO epochs per rollout: 1; selected update: 1.

| Metric | Test | Test with history zeroed |
|---|---|---|
| dwell | 2.42857 | 2.42857 |
| depth | 2.14286 | 2.14286 |
| protected | 0.14286 | 0.14286 |
| exposed | 0.57143 | 0.57143 |
| lure_chains | 0.42857 | 0.42857 |
| dead_ends | 0.00000 | 0.00000 |
| capacity_violations | 24.14286 | 24.14286 |
| length | 24.14286 | 24.14286 |
| decoys_deployed | 96.57143 | 96.57143 |

| Run | Environment repeat | Dwell | Depth | Protected | Exposed | Length |
|---|---|---|---|---|---|---|
| scenario_1_b_c.j2 | 0 | 4.00000 | 4.00000 | 1.00000 | 1.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 3.00000 | 3.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 |
| scenario_3_b_b.j2 | 0 | 6.00000 | 4.00000 | 0.00000 | 1.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 |

## real_100 / GRU+MAPPO / seed 0

Environment steps: 16; PPO epochs per rollout: 1; selected update: 1.

| Metric | Test | Test with history zeroed |
|---|---|---|
| dwell | 3.14286 | 2.71429 |
| depth | 2.85714 | 2.42857 |
| protected | 0.14286 | 0.14286 |
| exposed | 0.57143 | 0.57143 |
| lure_chains | 1.00000 | 1.00000 |
| dead_ends | 0.14286 | 0.00000 |
| capacity_violations | 10.71429 | 8.00000 |
| length | 25.42857 | 24.14286 |
| decoys_deployed | 61.42857 | 53.57143 |

| Run | Environment repeat | Dwell | Depth | Protected | Exposed | Length |
|---|---|---|---|---|---|---|
| scenario_1_b_c.j2 | 0 | 11.00000 | 11.00000 | 1.00000 | 1.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 2.00000 | 1.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 3.00000 | 3.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 1.00000 | 1.00000 | 0.00000 | 0.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 4.00000 | 3.00000 | 0.00000 | 0.00000 | 25.00000 |
| scenario_3_b_b.j2 | 0 | 1.00000 | 1.00000 | 0.00000 | 1.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 |

## real_100 / LSTM+IPPO / seed 0

Environment steps: 16; PPO epochs per rollout: 1; selected update: 1.

| Metric | Test | Test with history zeroed |
|---|---|---|
| dwell | 2.28571 | 3.14286 |
| depth | 2.00000 | 2.14286 |
| protected | 0.14286 | 0.14286 |
| exposed | 0.57143 | 0.71429 |
| lure_chains | 0.42857 | 0.42857 |
| dead_ends | 0.00000 | 0.00000 |
| capacity_violations | 24.14286 | 24.14286 |
| length | 24.14286 | 24.14286 |
| decoys_deployed | 95.57143 | 95.57143 |

| Run | Environment repeat | Dwell | Depth | Protected | Exposed | Length |
|---|---|---|---|---|---|---|
| scenario_1_b_c.j2 | 0 | 4.00000 | 4.00000 | 1.00000 | 1.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 3.00000 | 3.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 |
| scenario_3_b_b.j2 | 0 | 5.00000 | 3.00000 | 0.00000 | 1.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 |

## real_100 / LSTM+MAPPO / seed 0

Environment steps: 16; PPO epochs per rollout: 1; selected update: 1.

| Metric | Test | Test with history zeroed |
|---|---|---|
| dwell | 2.28571 | 2.28571 |
| depth | 2.00000 | 2.00000 |
| protected | 0.14286 | 0.14286 |
| exposed | 0.57143 | 0.57143 |
| lure_chains | 0.42857 | 0.42857 |
| dead_ends | 0.00000 | 0.00000 |
| capacity_violations | 24.14286 | 24.14286 |
| length | 24.14286 | 24.14286 |
| decoys_deployed | 95.28571 | 94.28571 |

| Run | Environment repeat | Dwell | Depth | Protected | Exposed | Length |
|---|---|---|---|---|---|---|
| scenario_1_b_c.j2 | 0 | 4.00000 | 4.00000 | 1.00000 | 1.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 3.00000 | 3.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 |
| scenario_3_b_b.j2 | 0 | 5.00000 | 3.00000 | 0.00000 | 1.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 |

## real_100 / NoHistory+IPPO / seed 0

Environment steps: 16; PPO epochs per rollout: 1; selected update: 1.

| Metric | Test | Test with history zeroed |
|---|---|---|
| dwell | 2.42857 | 2.42857 |
| depth | 2.14286 | 2.14286 |
| protected | 0.14286 | 0.14286 |
| exposed | 0.57143 | 0.57143 |
| lure_chains | 0.42857 | 0.42857 |
| dead_ends | 0.00000 | 0.00000 |
| capacity_violations | 24.14286 | 24.14286 |
| length | 24.14286 | 24.14286 |
| decoys_deployed | 96.57143 | 96.57143 |

| Run | Environment repeat | Dwell | Depth | Protected | Exposed | Length |
|---|---|---|---|---|---|---|
| scenario_1_b_c.j2 | 0 | 4.00000 | 4.00000 | 1.00000 | 1.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 3.00000 | 3.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 |
| scenario_3_b_b.j2 | 0 | 6.00000 | 4.00000 | 0.00000 | 1.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 |

## real_100 / NoHistory+MAPPO / seed 0

Environment steps: 16; PPO epochs per rollout: 1; selected update: 1.

| Metric | Test | Test with history zeroed |
|---|---|---|
| dwell | 2.42857 | 2.42857 |
| depth | 2.14286 | 2.14286 |
| protected | 0.14286 | 0.14286 |
| exposed | 0.57143 | 0.57143 |
| lure_chains | 0.42857 | 0.42857 |
| dead_ends | 0.00000 | 0.00000 |
| capacity_violations | 24.14286 | 24.14286 |
| length | 24.14286 | 24.14286 |
| decoys_deployed | 95.57143 | 95.57143 |

| Run | Environment repeat | Dwell | Depth | Protected | Exposed | Length |
|---|---|---|---|---|---|---|
| scenario_1_b_c.j2 | 0 | 4.00000 | 4.00000 | 1.00000 | 1.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 3.00000 | 3.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 3.00000 | 3.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 |
| scenario_3_b_b.j2 | 0 | 5.00000 | 3.00000 | 0.00000 | 1.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 |

## real_100 / Transformer+IPPO / seed 0

Environment steps: 16; PPO epochs per rollout: 1; selected update: 1.

| Metric | Test | Test with history zeroed |
|---|---|---|
| dwell | 3.28571 | 3.57143 |
| depth | 2.14286 | 2.42857 |
| protected | 0.14286 | 0.14286 |
| exposed | 0.57143 | 0.57143 |
| lure_chains | 0.14286 | 0.28571 |
| dead_ends | 0.00000 | 0.00000 |
| capacity_violations | 24.57143 | 24.57143 |
| length | 24.57143 | 24.57143 |
| decoys_deployed | 98.28571 | 98.28571 |

| Run | Environment repeat | Dwell | Depth | Protected | Exposed | Length |
|---|---|---|---|---|---|---|
| scenario_1_b_c.j2 | 0 | 3.00000 | 3.00000 | 1.00000 | 0.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 4.00000 | 3.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 4.00000 | 2.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 4.00000 | 1.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 3.00000 | 2.00000 | 0.00000 | 0.00000 | 19.00000 |
| scenario_3_b_b.j2 | 0 | 5.00000 | 4.00000 | 0.00000 | 1.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 |

## real_100 / Transformer+MAPPO / seed 0

Environment steps: 16; PPO epochs per rollout: 1; selected update: 1.

| Metric | Test | Test with history zeroed |
|---|---|---|
| dwell | 2.85714 | 3.00000 |
| depth | 1.85714 | 2.00000 |
| protected | 0.14286 | 0.14286 |
| exposed | 0.57143 | 0.57143 |
| lure_chains | 0.42857 | 0.42857 |
| dead_ends | 0.00000 | 0.00000 |
| capacity_violations | 24.14286 | 24.14286 |
| length | 24.14286 | 24.14286 |
| decoys_deployed | 95.57143 | 95.57143 |

| Run | Environment repeat | Dwell | Depth | Protected | Exposed | Length |
|---|---|---|---|---|---|---|
| scenario_1_b_c.j2 | 0 | 3.00000 | 3.00000 | 1.00000 | 0.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 3.00000 | 3.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 3.00000 | 1.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 4.00000 | 1.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 |
| scenario_3_b_b.j2 | 0 | 5.00000 | 3.00000 | 0.00000 | 1.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 |

## repeat_100 / GRU+IPPO / seed 0

Environment steps: 16; PPO epochs per rollout: 1; selected update: 1.

| Metric | Test | Test with history zeroed |
|---|---|---|
| dwell | 2.42857 | 2.42857 |
| depth | 2.14286 | 2.14286 |
| protected | 0.14286 | 0.14286 |
| exposed | 0.57143 | 0.57143 |
| lure_chains | 0.42857 | 0.42857 |
| dead_ends | 0.00000 | 0.00000 |
| capacity_violations | 24.14286 | 24.14286 |
| length | 24.14286 | 24.14286 |
| decoys_deployed | 96.57143 | 96.57143 |

| Run | Environment repeat | Dwell | Depth | Protected | Exposed | Length |
|---|---|---|---|---|---|---|
| scenario_1_b_c.j2 | 0 | 4.00000 | 4.00000 | 1.00000 | 1.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 3.00000 | 3.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 |
| scenario_3_b_b.j2 | 0 | 6.00000 | 4.00000 | 0.00000 | 1.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 |

## repeat_100 / GRU+MAPPO / seed 0

Environment steps: 16; PPO epochs per rollout: 1; selected update: 1.

| Metric | Test | Test with history zeroed |
|---|---|---|
| dwell | 1.28571 | 2.85714 |
| depth | 1.28571 | 2.85714 |
| protected | 0.14286 | 0.14286 |
| exposed | 0.28571 | 0.28571 |
| lure_chains | 0.00000 | 1.14286 |
| dead_ends | 0.28571 | 0.00000 |
| capacity_violations | 9.28571 | 10.00000 |
| length | 24.14286 | 24.14286 |
| decoys_deployed | 52.14286 | 56.28571 |

| Run | Environment repeat | Dwell | Depth | Protected | Exposed | Length |
|---|---|---|---|---|---|---|
| scenario_1_b_c.j2 | 0 | 3.00000 | 3.00000 | 1.00000 | 0.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 1.00000 | 1.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 3.00000 | 3.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 1.00000 | 1.00000 | 0.00000 | 0.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 1.00000 | 1.00000 | 0.00000 | 0.00000 | 16.00000 |
| scenario_3_b_b.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 |

## repeat_100 / LSTM+IPPO / seed 0

Environment steps: 16; PPO epochs per rollout: 1; selected update: 1.

| Metric | Test | Test with history zeroed |
|---|---|---|
| dwell | 2.42857 | 2.42857 |
| depth | 2.14286 | 2.14286 |
| protected | 0.14286 | 0.14286 |
| exposed | 0.57143 | 0.57143 |
| lure_chains | 0.42857 | 0.42857 |
| dead_ends | 0.00000 | 0.00000 |
| capacity_violations | 24.14286 | 24.14286 |
| length | 24.14286 | 24.14286 |
| decoys_deployed | 96.57143 | 96.57143 |

| Run | Environment repeat | Dwell | Depth | Protected | Exposed | Length |
|---|---|---|---|---|---|---|
| scenario_1_b_c.j2 | 0 | 4.00000 | 4.00000 | 1.00000 | 1.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 3.00000 | 3.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 |
| scenario_3_b_b.j2 | 0 | 6.00000 | 4.00000 | 0.00000 | 1.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 |

## repeat_100 / LSTM+MAPPO / seed 0

Environment steps: 16; PPO epochs per rollout: 1; selected update: 1.

| Metric | Test | Test with history zeroed |
|---|---|---|
| dwell | 2.28571 | 3.28571 |
| depth | 2.00000 | 2.14286 |
| protected | 0.14286 | 0.14286 |
| exposed | 0.57143 | 0.71429 |
| lure_chains | 0.42857 | 0.42857 |
| dead_ends | 0.00000 | 0.00000 |
| capacity_violations | 24.14286 | 24.14286 |
| length | 24.14286 | 24.14286 |
| decoys_deployed | 95.00000 | 90.14286 |

| Run | Environment repeat | Dwell | Depth | Protected | Exposed | Length |
|---|---|---|---|---|---|---|
| scenario_1_b_c.j2 | 0 | 4.00000 | 4.00000 | 1.00000 | 1.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 3.00000 | 3.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 |
| scenario_3_b_b.j2 | 0 | 5.00000 | 3.00000 | 0.00000 | 1.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 |

## repeat_100 / Transformer+IPPO / seed 0

Environment steps: 16; PPO epochs per rollout: 1; selected update: 1.

| Metric | Test | Test with history zeroed |
|---|---|---|
| dwell | 3.00000 | 3.28571 |
| depth | 2.14286 | 2.28571 |
| protected | 0.14286 | 0.14286 |
| exposed | 0.57143 | 0.57143 |
| lure_chains | 0.14286 | 0.28571 |
| dead_ends | 0.00000 | 0.00000 |
| capacity_violations | 24.42857 | 24.14286 |
| length | 24.42857 | 24.14286 |
| decoys_deployed | 97.71429 | 96.57143 |

| Run | Environment repeat | Dwell | Depth | Protected | Exposed | Length |
|---|---|---|---|---|---|---|
| scenario_1_b_c.j2 | 0 | 3.00000 | 3.00000 | 1.00000 | 0.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 3.00000 | 3.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 4.00000 | 2.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 4.00000 | 1.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 0.00000 | 18.00000 |
| scenario_3_b_b.j2 | 0 | 5.00000 | 4.00000 | 0.00000 | 1.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 |

## repeat_100 / Transformer+MAPPO / seed 0

Environment steps: 16; PPO epochs per rollout: 1; selected update: 1.

| Metric | Test | Test with history zeroed |
|---|---|---|
| dwell | 2.85714 | 2.85714 |
| depth | 2.00000 | 2.00000 |
| protected | 0.14286 | 0.14286 |
| exposed | 0.71429 | 0.71429 |
| lure_chains | 0.42857 | 0.42857 |
| dead_ends | 0.00000 | 0.00000 |
| capacity_violations | 24.14286 | 24.14286 |
| length | 24.14286 | 24.14286 |
| decoys_deployed | 96.57143 | 96.57143 |

| Run | Environment repeat | Dwell | Depth | Protected | Exposed | Length |
|---|---|---|---|---|---|---|
| scenario_1_b_c.j2 | 0 | 5.00000 | 5.00000 | 1.00000 | 1.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 3.00000 | 1.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 3.00000 | 1.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 |
| scenario_3_b_b.j2 | 0 | 5.00000 | 3.00000 | 0.00000 | 1.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 |

