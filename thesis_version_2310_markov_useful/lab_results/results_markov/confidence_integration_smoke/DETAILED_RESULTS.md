# Per-seed prediction and per-original-run results

Probabilities/accuracies are fractions unless marked percent.

## markov_100 / GRU / seed 0

Original runs: 22; independent groups: 22; synthetic runs: 22; train windows: 1537; optimizer updates: 50.

| Metric | Final-epoch validation | Final-epoch test | Validation-best test (secondary) |
|---|---|---|---|
| top1 | 0.47925 | 0.44118 | 0.44118 |
| top3 | 0.69434 | 0.62500 | 0.62500 |
| top5 | 0.76604 | 0.66912 | 0.66912 |
| macro_f1 | 0.28055 | 0.29773 | 0.29773 |
| nll | 2.55381 | 2.81150 | 2.81150 |
| log_likelihood | -676.75995 | -764.72837 | -764.72837 |
| perplexity | 12.85601 | 16.63487 | 16.63487 |
| run_macro_top1 | 0.43795 | 0.41379 | 0.41379 |
| n | 265 | 272 | 272 |
| f1_label_count | 52 | 51 | 51 |

| Test run | Windows | Top-1 % | NLL |
|---|---|---|---|
| scenario_1_b_c.j2 | 43 | 60.46512 | 2.10188 |
| scenario_1_c_c.j2 | 43 | 58.13953 | 2.14564 |
| scenario_1_d_a.j2 | 50 | 62.00000 | 1.99060 |
| scenario_1_e_a.j2 | 45 | 57.77778 | 2.16253 |
| scenario_3_a_b.j2 | 24 | 20.83333 | 3.82022 |
| scenario_3_b_b.j2 | 23 | 30.43478 | 3.53109 |
| scenario_6_c.j2 | 44 | 0.00000 | 4.82593 |

## markov_100 / LSTM / seed 0

Original runs: 22; independent groups: 22; synthetic runs: 22; train windows: 1537; optimizer updates: 50.

| Metric | Final-epoch validation | Final-epoch test | Validation-best test (secondary) |
|---|---|---|---|
| top1 | 0.47170 | 0.44118 | 0.44118 |
| top3 | 0.67925 | 0.61029 | 0.61029 |
| top5 | 0.75849 | 0.65441 | 0.65441 |
| macro_f1 | 0.24993 | 0.26103 | 0.26103 |
| nll | 2.75276 | 3.10492 | 3.10492 |
| log_likelihood | -729.48183 | -844.53730 | -844.53730 |
| perplexity | 15.68589 | 22.30736 | 22.30736 |
| run_macro_top1 | 0.42892 | 0.40451 | 0.40451 |
| n | 265 | 272 | 272 |
| f1_label_count | 52 | 51 | 51 |

| Test run | Windows | Top-1 % | NLL |
|---|---|---|---|
| scenario_1_b_c.j2 | 43 | 62.79070 | 2.37793 |
| scenario_1_c_c.j2 | 43 | 58.13953 | 2.35289 |
| scenario_1_d_a.j2 | 50 | 64.00000 | 2.21392 |
| scenario_1_e_a.j2 | 45 | 60.00000 | 2.40589 |
| scenario_3_a_b.j2 | 24 | 20.83333 | 3.99068 |
| scenario_3_b_b.j2 | 23 | 17.39130 | 3.83199 |
| scenario_6_c.j2 | 44 | 0.00000 | 5.41451 |

## markov_100 / Transformer / seed 0

Original runs: 22; independent groups: 22; synthetic runs: 22; train windows: 1537; optimizer updates: 50.

| Metric | Final-epoch validation | Final-epoch test | Validation-best test (secondary) |
|---|---|---|---|
| top1 | 0.38868 | 0.35294 | 0.35294 |
| top3 | 0.63396 | 0.56985 | 0.56985 |
| top5 | 0.67170 | 0.60294 | 0.60294 |
| macro_f1 | 0.17991 | 0.17189 | 0.17189 |
| nll | 2.96569 | 3.24382 | 3.24382 |
| log_likelihood | -785.90733 | -882.31780 | -882.31780 |
| perplexity | 19.40805 | 25.63133 | 25.63133 |
| run_macro_top1 | 0.32854 | 0.30835 | 0.30835 |
| n | 265 | 272 | 272 |
| f1_label_count | 52 | 51 | 51 |

| Test run | Windows | Top-1 % | NLL |
|---|---|---|---|
| scenario_1_b_c.j2 | 43 | 51.16279 | 2.54977 |
| scenario_1_c_c.j2 | 43 | 48.83721 | 2.46916 |
| scenario_1_d_a.j2 | 50 | 54.00000 | 2.35802 |
| scenario_1_e_a.j2 | 45 | 53.33333 | 2.53022 |
| scenario_3_a_b.j2 | 24 | 4.16667 | 4.24076 |
| scenario_3_b_b.j2 | 23 | 4.34783 | 4.01372 |
| scenario_6_c.j2 | 44 | 0.00000 | 5.46931 |

## real_100 / GRU / seed 0

Original runs: 22; independent groups: 22; synthetic runs: 0; train windows: 774; optimizer updates: 26.

| Metric | Final-epoch validation | Final-epoch test | Validation-best test (secondary) |
|---|---|---|---|
| top1 | 0.37358 | 0.34926 | 0.34926 |
| top3 | 0.65283 | 0.58088 | 0.58088 |
| top5 | 0.70566 | 0.61397 | 0.61397 |
| macro_f1 | 0.18346 | 0.20193 | 0.20193 |
| nll | 3.03217 | 3.18636 | 3.18636 |
| log_likelihood | -803.52561 | -866.69047 | -866.69047 |
| perplexity | 20.74224 | 24.20023 | 24.20023 |
| run_macro_top1 | 0.34439 | 0.33250 | 0.33250 |
| n | 265 | 272 | 272 |
| f1_label_count | 52 | 51 | 51 |

| Test run | Windows | Top-1 % | NLL |
|---|---|---|---|
| scenario_1_b_c.j2 | 43 | 48.83721 | 2.61356 |
| scenario_1_c_c.j2 | 43 | 44.18605 | 2.69123 |
| scenario_1_d_a.j2 | 50 | 48.00000 | 2.56754 |
| scenario_1_e_a.j2 | 45 | 44.44444 | 2.72354 |
| scenario_3_a_b.j2 | 24 | 12.50000 | 4.06525 |
| scenario_3_b_b.j2 | 23 | 34.78261 | 3.76378 |
| scenario_6_c.j2 | 44 | 0.00000 | 4.62534 |

## real_100 / LSTM / seed 0

Original runs: 22; independent groups: 22; synthetic runs: 0; train windows: 774; optimizer updates: 26.

| Metric | Final-epoch validation | Final-epoch test | Validation-best test (secondary) |
|---|---|---|---|
| top1 | 0.34340 | 0.30515 | 0.30515 |
| top3 | 0.54340 | 0.48529 | 0.48529 |
| top5 | 0.63019 | 0.55515 | 0.55515 |
| macro_f1 | 0.11891 | 0.12389 | 0.12389 |
| nll | 3.28992 | 3.51010 | 3.51010 |
| log_likelihood | -871.82781 | -954.74854 | -954.74854 |
| perplexity | 26.84062 | 33.45178 | 33.45178 |
| run_macro_top1 | 0.29413 | 0.26866 | 0.26866 |
| n | 265 | 272 | 272 |
| f1_label_count | 52 | 51 | 51 |

| Test run | Windows | Top-1 % | NLL |
|---|---|---|---|
| scenario_1_b_c.j2 | 43 | 44.18605 | 3.02613 |
| scenario_1_c_c.j2 | 43 | 46.51163 | 2.97261 |
| scenario_1_d_a.j2 | 50 | 42.00000 | 2.94214 |
| scenario_1_e_a.j2 | 45 | 46.66667 | 2.98954 |
| scenario_3_a_b.j2 | 24 | 0.00000 | 4.23568 |
| scenario_3_b_b.j2 | 23 | 8.69565 | 4.10790 |
| scenario_6_c.j2 | 44 | 0.00000 | 4.97793 |

## real_100 / Transformer / seed 0

Original runs: 22; independent groups: 22; synthetic runs: 0; train windows: 774; optimizer updates: 26.

| Metric | Final-epoch validation | Final-epoch test | Validation-best test (secondary) |
|---|---|---|---|
| top1 | 0.28302 | 0.26103 | 0.26103 |
| top3 | 0.46038 | 0.41176 | 0.41176 |
| top5 | 0.56981 | 0.50368 | 0.50368 |
| macro_f1 | 0.10319 | 0.12748 | 0.12748 |
| nll | 3.40242 | 3.61155 | 3.61155 |
| log_likelihood | -901.64005 | -982.34278 | -982.34278 |
| perplexity | 30.03656 | 37.02355 | 37.02355 |
| run_macro_top1 | 0.23573 | 0.22267 | 0.22267 |
| n | 265 | 272 | 272 |
| f1_label_count | 52 | 51 | 51 |

| Test run | Windows | Top-1 % | NLL |
|---|---|---|---|
| scenario_1_b_c.j2 | 43 | 37.20930 | 3.10053 |
| scenario_1_c_c.j2 | 43 | 34.88372 | 3.03992 |
| scenario_1_d_a.j2 | 50 | 46.00000 | 3.03327 |
| scenario_1_e_a.j2 | 45 | 37.77778 | 3.04903 |
| scenario_3_a_b.j2 | 24 | 0.00000 | 4.34484 |
| scenario_3_b_b.j2 | 23 | 0.00000 | 4.21490 |
| scenario_6_c.j2 | 44 | 0.00000 | 5.18670 |

## repeat_100 / GRU / seed 0

Original runs: 22; independent groups: 22; synthetic runs: 0; train windows: 1537; optimizer updates: 50.

| Metric | Final-epoch validation | Final-epoch test | Validation-best test (secondary) |
|---|---|---|---|
| top1 | 0.52830 | 0.48529 | 0.48529 |
| top3 | 0.75472 | 0.67279 | 0.67279 |
| top5 | 0.80000 | 0.69853 | 0.69853 |
| macro_f1 | 0.37153 | 0.38380 | 0.38380 |
| nll | 2.46486 | 2.73177 | 2.73177 |
| log_likelihood | -653.18863 | -743.04176 | -743.04176 |
| perplexity | 11.76187 | 15.36007 | 15.36007 |
| run_macro_top1 | 0.49439 | 0.46321 | 0.46321 |
| n | 265 | 272 | 272 |
| f1_label_count | 52 | 51 | 51 |

| Test run | Windows | Top-1 % | NLL |
|---|---|---|---|
| scenario_1_b_c.j2 | 43 | 65.11628 | 1.98315 |
| scenario_1_c_c.j2 | 43 | 62.79070 | 2.09495 |
| scenario_1_d_a.j2 | 50 | 66.00000 | 1.97196 |
| scenario_1_e_a.j2 | 45 | 62.22222 | 2.12449 |
| scenario_3_a_b.j2 | 24 | 33.33333 | 3.59818 |
| scenario_3_b_b.j2 | 23 | 34.78261 | 3.27810 |
| scenario_6_c.j2 | 44 | 0.00000 | 4.81207 |

## repeat_100 / LSTM / seed 0

Original runs: 22; independent groups: 22; synthetic runs: 0; train windows: 1537; optimizer updates: 50.

| Metric | Final-epoch validation | Final-epoch test | Validation-best test (secondary) |
|---|---|---|---|
| top1 | 0.44528 | 0.40809 | 0.40809 |
| top3 | 0.70189 | 0.63971 | 0.63971 |
| top5 | 0.77358 | 0.68382 | 0.68382 |
| macro_f1 | 0.20727 | 0.22993 | 0.22993 |
| nll | 2.66808 | 3.02716 | 3.02716 |
| log_likelihood | -707.04233 | -823.38770 | -823.38770 |
| perplexity | 14.41233 | 20.63855 | 20.63855 |
| run_macro_top1 | 0.40706 | 0.37965 | 0.37965 |
| n | 265 | 272 | 272 |
| f1_label_count | 52 | 51 | 51 |

| Test run | Windows | Top-1 % | NLL |
|---|---|---|---|
| scenario_1_b_c.j2 | 43 | 58.13953 | 2.23913 |
| scenario_1_c_c.j2 | 43 | 53.48837 | 2.28443 |
| scenario_1_d_a.j2 | 50 | 56.00000 | 2.28066 |
| scenario_1_e_a.j2 | 45 | 55.55556 | 2.33069 |
| scenario_3_a_b.j2 | 24 | 20.83333 | 3.71729 |
| scenario_3_b_b.j2 | 23 | 21.73913 | 3.55384 |
| scenario_6_c.j2 | 44 | 0.00000 | 5.43197 |

## repeat_100 / Transformer / seed 0

Original runs: 22; independent groups: 22; synthetic runs: 0; train windows: 1537; optimizer updates: 50.

| Metric | Final-epoch validation | Final-epoch test | Validation-best test (secondary) |
|---|---|---|---|
| top1 | 0.44528 | 0.41544 | 0.41544 |
| top3 | 0.61132 | 0.56985 | 0.56985 |
| top5 | 0.68302 | 0.63971 | 0.63971 |
| macro_f1 | 0.23782 | 0.24181 | 0.24181 |
| nll | 2.91570 | 3.20572 | 3.20572 |
| log_likelihood | -772.65986 | -871.95548 | -871.95548 |
| perplexity | 18.46169 | 24.67323 | 24.67323 |
| run_macro_top1 | 0.36987 | 0.36964 | 0.36964 |
| n | 265 | 272 | 272 |
| f1_label_count | 52 | 51 | 51 |

| Test run | Windows | Top-1 % | NLL |
|---|---|---|---|
| scenario_1_b_c.j2 | 43 | 62.79070 | 2.42158 |
| scenario_1_c_c.j2 | 43 | 62.79070 | 2.40975 |
| scenario_1_d_a.j2 | 50 | 58.00000 | 2.43725 |
| scenario_1_e_a.j2 | 45 | 57.77778 | 2.44363 |
| scenario_3_a_b.j2 | 24 | 0.00000 | 4.12192 |
| scenario_3_b_b.j2 | 23 | 17.39130 | 3.80432 |
| scenario_6_c.j2 | 44 | 0.00000 | 5.58993 |

## markov_100 / GRU+IPPO / seed 0

Environment steps: 16; PPO epochs per rollout: 1; selected update: 1.

| Metric | Test | Test with history zeroed |
|---|---|---|
| dwell | 3.00000 | 3.00000 |
| depth | 2.71429 | 2.85714 |
| protected | 0.14286 | 0.14286 |
| exposed | 0.71429 | 0.71429 |
| lure_chains | 0.42857 | 0.28571 |
| dead_ends | 0.00000 | 0.00000 |
| capacity_violations | 24.14286 | 24.14286 |
| length | 24.14286 | 24.14286 |
| decoys_deployed | 95.42857 | 95.57143 |

| Run | Environment repeat | Dwell | Depth | Protected | Exposed | Length |
|---|---|---|---|---|---|---|
| scenario_1_b_c.j2 | 0 | 3.00000 | 3.00000 | 1.00000 | 1.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 4.00000 | 4.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 5.00000 | 5.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 |
| scenario_3_b_b.j2 | 0 | 5.00000 | 3.00000 | 0.00000 | 1.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 |

## markov_100 / GRU+MAPPO / seed 0

Environment steps: 16; PPO epochs per rollout: 1; selected update: 1.

| Metric | Test | Test with history zeroed |
|---|---|---|
| dwell | 2.71429 | 3.57143 |
| depth | 1.42857 | 1.85714 |
| protected | 0.14286 | 0.14286 |
| exposed | 0.42857 | 0.57143 |
| lure_chains | 0.00000 | 0.00000 |
| dead_ends | 0.14286 | 0.14286 |
| capacity_violations | 13.00000 | 12.42857 |
| length | 24.28571 | 24.28571 |
| decoys_deployed | 56.14286 | 55.14286 |

| Run | Environment repeat | Dwell | Depth | Protected | Exposed | Length |
|---|---|---|---|---|---|---|
| scenario_1_b_c.j2 | 0 | 6.00000 | 3.00000 | 1.00000 | 0.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 3.00000 | 1.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 5.00000 | 1.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 1.00000 | 1.00000 | 0.00000 | 0.00000 | 16.00000 |
| scenario_3_b_b.j2 | 0 | 1.00000 | 1.00000 | 0.00000 | 0.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 1.00000 | 1.00000 | 0.00000 | 0.00000 | 3.00000 |

## markov_100 / LSTM+IPPO / seed 0

Environment steps: 16; PPO epochs per rollout: 1; selected update: 1.

| Metric | Test | Test with history zeroed |
|---|---|---|
| dwell | 2.71429 | 2.71429 |
| depth | 2.71429 | 2.00000 |
| protected | 0.14286 | 0.14286 |
| exposed | 0.71429 | 0.71429 |
| lure_chains | 0.00000 | 0.00000 |
| dead_ends | 0.00000 | 0.00000 |
| capacity_violations | 24.14286 | 24.14286 |
| length | 24.14286 | 24.14286 |
| decoys_deployed | 95.14286 | 95.57143 |

| Run | Environment repeat | Dwell | Depth | Protected | Exposed | Length |
|---|---|---|---|---|---|---|
| scenario_1_b_c.j2 | 0 | 3.00000 | 3.00000 | 1.00000 | 1.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 3.00000 | 3.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 6.00000 | 6.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 |
| scenario_3_b_b.j2 | 0 | 3.00000 | 3.00000 | 0.00000 | 1.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 |

## markov_100 / LSTM+MAPPO / seed 0

Environment steps: 16; PPO epochs per rollout: 1; selected update: 1.

| Metric | Test | Test with history zeroed |
|---|---|---|
| dwell | 2.57143 | 3.42857 |
| depth | 1.42857 | 1.71429 |
| protected | 0.14286 | 0.14286 |
| exposed | 0.42857 | 0.57143 |
| lure_chains | 0.00000 | 0.14286 |
| dead_ends | 0.00000 | 0.00000 |
| capacity_violations | 8.28571 | 8.00000 |
| length | 24.71429 | 24.71429 |
| decoys_deployed | 47.14286 | 45.57143 |

| Run | Environment repeat | Dwell | Depth | Protected | Exposed | Length |
|---|---|---|---|---|---|---|
| scenario_1_b_c.j2 | 0 | 4.00000 | 2.00000 | 1.00000 | 0.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 1.00000 | 1.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 4.00000 | 1.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 5.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 1.00000 | 1.00000 | 0.00000 | 0.00000 | 16.00000 |
| scenario_3_b_b.j2 | 0 | 1.00000 | 1.00000 | 0.00000 | 0.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 0.00000 | 6.00000 |

## markov_100 / Transformer+IPPO / seed 0

Environment steps: 16; PPO epochs per rollout: 1; selected update: 1.

| Metric | Test | Test with history zeroed |
|---|---|---|
| dwell | 2.57143 | 2.57143 |
| depth | 2.28571 | 2.28571 |
| protected | 0.14286 | 0.14286 |
| exposed | 0.57143 | 0.57143 |
| lure_chains | 0.42857 | 0.42857 |
| dead_ends | 0.00000 | 0.00000 |
| capacity_violations | 24.14286 | 24.14286 |
| length | 24.14286 | 24.14286 |
| decoys_deployed | 96.57143 | 96.57143 |

| Run | Environment repeat | Dwell | Depth | Protected | Exposed | Length |
|---|---|---|---|---|---|---|
| scenario_1_b_c.j2 | 0 | 5.00000 | 5.00000 | 1.00000 | 1.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 3.00000 | 3.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 |
| scenario_3_b_b.j2 | 0 | 6.00000 | 4.00000 | 0.00000 | 1.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 |

## markov_100 / Transformer+MAPPO / seed 0

Environment steps: 16; PPO epochs per rollout: 1; selected update: 1.

| Metric | Test | Test with history zeroed |
|---|---|---|
| dwell | 2.71429 | 2.57143 |
| depth | 2.71429 | 2.57143 |
| protected | 0.14286 | 0.14286 |
| exposed | 0.71429 | 0.71429 |
| lure_chains | 0.00000 | 0.00000 |
| dead_ends | 0.00000 | 0.00000 |
| capacity_violations | 24.14286 | 24.14286 |
| length | 24.14286 | 24.14286 |
| decoys_deployed | 95.57143 | 95.57143 |

| Run | Environment repeat | Dwell | Depth | Protected | Exposed | Length |
|---|---|---|---|---|---|---|
| scenario_1_b_c.j2 | 0 | 3.00000 | 3.00000 | 1.00000 | 1.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 4.00000 | 4.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 6.00000 | 6.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 |
| scenario_3_b_b.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 1.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 |

## real_100 / GRU+IPPO / seed 0

Environment steps: 16; PPO epochs per rollout: 1; selected update: 1.

| Metric | Test | Test with history zeroed |
|---|---|---|
| dwell | 2.57143 | 2.71429 |
| depth | 2.28571 | 2.57143 |
| protected | 0.14286 | 0.14286 |
| exposed | 0.71429 | 0.71429 |
| lure_chains | 0.42857 | 0.28571 |
| dead_ends | 0.00000 | 0.00000 |
| capacity_violations | 24.14286 | 24.14286 |
| length | 24.14286 | 24.14286 |
| decoys_deployed | 95.42857 | 95.57143 |

| Run | Environment repeat | Dwell | Depth | Protected | Exposed | Length |
|---|---|---|---|---|---|---|
| scenario_1_b_c.j2 | 0 | 3.00000 | 3.00000 | 1.00000 | 1.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 3.00000 | 3.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 3.00000 | 3.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 |
| scenario_3_b_b.j2 | 0 | 5.00000 | 3.00000 | 0.00000 | 1.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 |

## real_100 / GRU+MAPPO / seed 0

Environment steps: 16; PPO epochs per rollout: 1; selected update: 1.

| Metric | Test | Test with history zeroed |
|---|---|---|
| dwell | 2.85714 | 3.00000 |
| depth | 1.85714 | 1.85714 |
| protected | 0.14286 | 0.14286 |
| exposed | 0.71429 | 0.71429 |
| lure_chains | 0.42857 | 0.42857 |
| dead_ends | 0.00000 | 0.00000 |
| capacity_violations | 24.14286 | 24.14286 |
| length | 24.14286 | 24.14286 |
| decoys_deployed | 96.57143 | 96.57143 |

| Run | Environment repeat | Dwell | Depth | Protected | Exposed | Length |
|---|---|---|---|---|---|---|
| scenario_1_b_c.j2 | 0 | 2.00000 | 2.00000 | 1.00000 | 1.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 3.00000 | 3.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 3.00000 | 1.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 4.00000 | 1.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 |
| scenario_3_b_b.j2 | 0 | 6.00000 | 4.00000 | 0.00000 | 1.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 |

## real_100 / LSTM+IPPO / seed 0

Environment steps: 16; PPO epochs per rollout: 1; selected update: 1.

| Metric | Test | Test with history zeroed |
|---|---|---|
| dwell | 2.42857 | 2.85714 |
| depth | 2.42857 | 2.71429 |
| protected | 0.14286 | 0.14286 |
| exposed | 0.71429 | 0.71429 |
| lure_chains | 0.00000 | 0.28571 |
| dead_ends | 0.00000 | 0.00000 |
| capacity_violations | 24.14286 | 24.14286 |
| length | 24.14286 | 24.14286 |
| decoys_deployed | 95.42857 | 95.57143 |

| Run | Environment repeat | Dwell | Depth | Protected | Exposed | Length |
|---|---|---|---|---|---|---|
| scenario_1_b_c.j2 | 0 | 3.00000 | 3.00000 | 1.00000 | 1.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 4.00000 | 4.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 4.00000 | 4.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 |
| scenario_3_b_b.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 1.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 |

## real_100 / LSTM+MAPPO / seed 0

Environment steps: 16; PPO epochs per rollout: 1; selected update: 1.

| Metric | Test | Test with history zeroed |
|---|---|---|
| dwell | 3.42857 | 2.85714 |
| depth | 1.85714 | 1.57143 |
| protected | 0.14286 | 0.14286 |
| exposed | 0.57143 | 0.71429 |
| lure_chains | 0.00000 | 0.00000 |
| dead_ends | 0.00000 | 0.00000 |
| capacity_violations | 24.14286 | 24.14286 |
| length | 24.14286 | 24.14286 |
| decoys_deployed | 96.57143 | 96.57143 |

| Run | Environment repeat | Dwell | Depth | Protected | Exposed | Length |
|---|---|---|---|---|---|---|
| scenario_1_b_c.j2 | 0 | 8.00000 | 6.00000 | 1.00000 | 0.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 5.00000 | 1.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 6.00000 | 1.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 |
| scenario_3_b_b.j2 | 0 | 1.00000 | 1.00000 | 0.00000 | 1.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 |

## real_100 / NoHistory+IPPO / seed 0

Environment steps: 16; PPO epochs per rollout: 1; selected update: 1.

| Metric | Test | Test with history zeroed |
|---|---|---|
| dwell | 3.00000 | 3.00000 |
| depth | 2.14286 | 2.14286 |
| protected | 0.14286 | 0.14286 |
| exposed | 0.71429 | 0.71429 |
| lure_chains | 0.28571 | 0.28571 |
| dead_ends | 0.00000 | 0.00000 |
| capacity_violations | 24.14286 | 24.14286 |
| length | 24.14286 | 24.14286 |
| decoys_deployed | 95.57143 | 95.57143 |

| Run | Environment repeat | Dwell | Depth | Protected | Exposed | Length |
|---|---|---|---|---|---|---|
| scenario_1_b_c.j2 | 0 | 3.00000 | 3.00000 | 1.00000 | 1.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 5.00000 | 2.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 5.00000 | 3.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 |
| scenario_3_b_b.j2 | 0 | 4.00000 | 3.00000 | 0.00000 | 1.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 |

## real_100 / NoHistory+MAPPO / seed 0

Environment steps: 16; PPO epochs per rollout: 1; selected update: 1.

| Metric | Test | Test with history zeroed |
|---|---|---|
| dwell | 3.57143 | 3.57143 |
| depth | 2.14286 | 2.14286 |
| protected | 0.14286 | 0.14286 |
| exposed | 0.57143 | 0.57143 |
| lure_chains | 0.14286 | 0.14286 |
| dead_ends | 0.00000 | 0.00000 |
| capacity_violations | 24.14286 | 24.14286 |
| length | 24.14286 | 24.14286 |
| decoys_deployed | 96.57143 | 96.57143 |

| Run | Environment repeat | Dwell | Depth | Protected | Exposed | Length |
|---|---|---|---|---|---|---|
| scenario_1_b_c.j2 | 0 | 5.00000 | 5.00000 | 1.00000 | 0.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 3.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 6.00000 | 2.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 5.00000 | 1.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 |
| scenario_3_b_b.j2 | 0 | 4.00000 | 3.00000 | 0.00000 | 1.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 |

## real_100 / Transformer+IPPO / seed 0

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
| scenario_1_b_c.j2 | 0 | 3.00000 | 3.00000 | 1.00000 | 1.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 3.00000 | 3.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 0.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 |
| scenario_3_b_b.j2 | 0 | 5.00000 | 3.00000 | 0.00000 | 1.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 |

## real_100 / Transformer+MAPPO / seed 0

Environment steps: 16; PPO epochs per rollout: 1; selected update: 1.

| Metric | Test | Test with history zeroed |
|---|---|---|
| dwell | 2.57143 | 3.00000 |
| depth | 2.28571 | 2.71429 |
| protected | 0.14286 | 0.14286 |
| exposed | 0.57143 | 0.71429 |
| lure_chains | 0.42857 | 0.42857 |
| dead_ends | 0.00000 | 0.00000 |
| capacity_violations | 24.14286 | 24.14286 |
| length | 24.14286 | 24.14286 |
| decoys_deployed | 96.57143 | 96.57143 |

| Run | Environment repeat | Dwell | Depth | Protected | Exposed | Length |
|---|---|---|---|---|---|---|
| scenario_1_b_c.j2 | 0 | 2.00000 | 2.00000 | 1.00000 | 1.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 3.00000 | 3.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 3.00000 | 3.00000 | 0.00000 | 0.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 |
| scenario_3_b_b.j2 | 0 | 6.00000 | 4.00000 | 0.00000 | 1.00000 | 15.00000 |
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
| decoys_deployed | 95.57143 | 95.57143 |

| Run | Environment repeat | Dwell | Depth | Protected | Exposed | Length |
|---|---|---|---|---|---|---|
| scenario_1_b_c.j2 | 0 | 3.00000 | 3.00000 | 1.00000 | 1.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 3.00000 | 3.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 0.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 |
| scenario_3_b_b.j2 | 0 | 5.00000 | 3.00000 | 0.00000 | 1.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 |

## repeat_100 / GRU+MAPPO / seed 0

Environment steps: 16; PPO epochs per rollout: 1; selected update: 1.

| Metric | Test | Test with history zeroed |
|---|---|---|
| dwell | 3.28571 | 4.28571 |
| depth | 2.14286 | 2.71429 |
| protected | 0.14286 | 0.14286 |
| exposed | 0.71429 | 0.71429 |
| lure_chains | 0.00000 | 0.00000 |
| dead_ends | 0.00000 | 0.00000 |
| capacity_violations | 24.14286 | 24.14286 |
| length | 24.14286 | 24.14286 |
| decoys_deployed | 96.57143 | 96.57143 |

| Run | Environment repeat | Dwell | Depth | Protected | Exposed | Length |
|---|---|---|---|---|---|---|
| scenario_1_b_c.j2 | 0 | 5.00000 | 5.00000 | 1.00000 | 1.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 3.00000 | 3.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 7.00000 | 3.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 5.00000 | 1.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 |
| scenario_3_b_b.j2 | 0 | 1.00000 | 1.00000 | 0.00000 | 1.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 |

## repeat_100 / LSTM+IPPO / seed 0

Environment steps: 16; PPO epochs per rollout: 1; selected update: 1.

| Metric | Test | Test with history zeroed |
|---|---|---|
| dwell | 3.14286 | 3.00000 |
| depth | 2.42857 | 2.14286 |
| protected | 0.14286 | 0.14286 |
| exposed | 0.71429 | 0.71429 |
| lure_chains | 0.00000 | 0.28571 |
| dead_ends | 0.00000 | 0.00000 |
| capacity_violations | 22.57143 | 22.85714 |
| length | 24.14286 | 24.14286 |
| decoys_deployed | 91.71429 | 93.00000 |

| Run | Environment repeat | Dwell | Depth | Protected | Exposed | Length |
|---|---|---|---|---|---|---|
| scenario_1_b_c.j2 | 0 | 4.00000 | 4.00000 | 1.00000 | 1.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 7.00000 | 4.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 5.00000 | 3.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 1.00000 | 1.00000 | 0.00000 | 0.00000 | 16.00000 |
| scenario_3_b_b.j2 | 0 | 3.00000 | 3.00000 | 0.00000 | 1.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 |

## repeat_100 / LSTM+MAPPO / seed 0

Environment steps: 16; PPO epochs per rollout: 1; selected update: 1.

| Metric | Test | Test with history zeroed |
|---|---|---|
| dwell | 2.28571 | 2.57143 |
| depth | 1.42857 | 1.71429 |
| protected | 0.14286 | 0.14286 |
| exposed | 0.71429 | 0.71429 |
| lure_chains | 0.00000 | 0.00000 |
| dead_ends | 0.00000 | 0.00000 |
| capacity_violations | 24.14286 | 24.14286 |
| length | 24.14286 | 24.14286 |
| decoys_deployed | 96.57143 | 96.57143 |

| Run | Environment repeat | Dwell | Depth | Protected | Exposed | Length |
|---|---|---|---|---|---|---|
| scenario_1_b_c.j2 | 0 | 1.00000 | 1.00000 | 1.00000 | 1.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 5.00000 | 2.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 5.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 |
| scenario_3_b_b.j2 | 0 | 1.00000 | 1.00000 | 0.00000 | 1.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 |

## repeat_100 / Transformer+IPPO / seed 0

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
| scenario_1_b_c.j2 | 0 | 5.00000 | 5.00000 | 1.00000 | 1.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 3.00000 | 3.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 |
| scenario_3_b_b.j2 | 0 | 5.00000 | 3.00000 | 0.00000 | 1.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 |

## repeat_100 / Transformer+MAPPO / seed 0

Environment steps: 16; PPO epochs per rollout: 1; selected update: 1.

| Metric | Test | Test with history zeroed |
|---|---|---|
| dwell | 2.85714 | 2.85714 |
| depth | 2.71429 | 2.71429 |
| protected | 0.14286 | 0.14286 |
| exposed | 0.71429 | 0.71429 |
| lure_chains | 0.28571 | 0.28571 |
| dead_ends | 0.00000 | 0.00000 |
| capacity_violations | 24.14286 | 24.14286 |
| length | 24.14286 | 24.14286 |
| decoys_deployed | 96.57143 | 96.57143 |

| Run | Environment repeat | Dwell | Depth | Protected | Exposed | Length |
|---|---|---|---|---|---|---|
| scenario_1_b_c.j2 | 0 | 2.00000 | 2.00000 | 1.00000 | 1.00000 | 44.00000 |
| scenario_1_c_c.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_1_d_a.j2 | 0 | 4.00000 | 4.00000 | 0.00000 | 1.00000 | 32.00000 |
| scenario_1_e_a.j2 | 0 | 5.00000 | 5.00000 | 0.00000 | 1.00000 | 30.00000 |
| scenario_3_a_b.j2 | 0 | 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 |
| scenario_3_b_b.j2 | 0 | 5.00000 | 4.00000 | 0.00000 | 1.00000 | 15.00000 |
| scenario_6_c.j2 | 0 | 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 |

