# Markov augmentation usefulness study

**COMPLETE**

Prediction cells: 360/360. Deception cells: 200/200.
Confidence ablation cells: 120/120. [Confidence results](CONFIDENCE_RESULTS.md) | [All confidence records](CONFIDENCE_DETAILS.md).
Training seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]. Source SHA256: `2a1deea60f8b3fdc4a73f7a4456b8525ed576aff72e58c7d08de249bc25d195c`.

The source is an AttackBed-derived playbook corpus. Test sequences are original held-out playbook sequences, not raw real-world logs.
Means +/- sample SD are across training seeds. Repeated windows and environment rollouts are not additional independent attack campaigns.

## Exact Markov model

Scenario-conditioned, time-homogeneous, first-order categorical Markov chain.
`P(j|i,s) = (0.02 + 4*C_s(i,j)) / (84*0.02 + 4*sum_k C_s(i,k))`.
`P(first=j|s) = (0.02 + 2*start_count_s(j)) / (84*0.02 + 2*n_runs_s)`.
This is an observed-state first-order chain, fitted separately for each training scenario. It is not an HMM or MCMC sampler.
Lengths are sampled from same-scenario training runs. Smoothing permits unseen transitions; these are not newly observed attack evidence.

## Protocol and epoch budget

Split complete runs before windowing; group duplicates after the existing parent-technique mapping. Same held-out runs across all cells.
The 25/50/75/100% learning curve uses nested scenario-stratified training groups; small scenarios are retained, so achieved fractions differ from requested percentages.
Augmentation doses add 25/50/100/200% as many synthetic sequences as original training sequences (rounded up). No concatenation into artificial long campaigns.
Repeat controls use original prediction windows repeated to exactly match each augmented condition's windows, batches and updates per epoch.
Main cells complete every epoch. PRIMARY results use the final common epoch. Validation-best checkpoint results are secondary and separately labeled. Test loss never selects anything.
PPO epochs are separate: the same PPO passes per rollout and environment-step budget apply to every IPPO/MAPPO arm.

**Shared encoder budget: 92 epochs.** Selection: Maximum validation-best epoch across all real-only pilots.
Pilot cap reached/approached: True. A cap warning means convergence has not been established.

[Every epoch](EPOCH_RESULTS.md) | [Per-seed and per-run metrics](DETAILED_RESULTS.md) | [Human-readable predictions](PREDICTION_EXAMPLES.md) | [Every RL validation point](RL_LEARNING_CURVES.md)

## 1. Transition sparsity and coverage

| Measure | Train | Validation | Test |
|---|---|---|---|
| runs | 22 | 7 | 7 |
| independent_groups | 22 | 7 | 7 |
| steps | 796 | 272 | 279 |
| unique_techniques | 79 | 53 | 52 |
| unique_bigrams | 210 | 101 | 93 |
| unique_trigrams | 260 | 115 | 106 |
| singleton_bigrams | 82 | 36 | 38 |
| unseen_transition_occurrence_pct | 0.00000 | 6.03774 | 22.05882 |
| unseen_transition_type_pct | 0.00000 | 10.89109 | 20.43011 |
| unseen_technique_occurrence_pct | 0.00000 | 0.00000 | 12.90323 |
| mean_outgoing | 2.76316 | 1.98039 | 1.86000 |
| mathematical_pair_coverage_pct | 2.97619 | 1.43141 | 1.31803 |

Unseen means absent from training. The 84 x 84 denominator is a mathematical upper bound, not the set of operationally possible transitions. Sparsity alone does not prove augmentation is needed.

- S2: 2 independent groups; training only.
- S4: 1 independent groups; training only.
- S5: 1 independent groups; training only.
- S7: 1 independent groups; training only.

### Remaining similarity between variants

| Split | Held-out run | Nearest training run | Bigram Jaccard |
|---|---|---|---|
| validation | scenario_1_c_a.j2 | scenario_1_c_b.j2 | 0.89744 |
| validation | scenario_1_d_c.j2 | scenario_1_d_b.j2 | 0.90000 |
| validation | scenario_1_e_b.j2 | scenario_1_c_b.j2 | 0.78571 |
| validation | scenario_1_e_c.j2 | scenario_1_a_c.j2 | 0.72727 |
| validation | scenario_3_a_c.j2 | scenario_3_b_c.j2 | 0.68571 |
| validation | scenario_3_a_d.j2 | scenario_3_b_d.j2 | 0.65385 |
| validation | scenario_6_a_a.j2 | scenario_6_a_b.j2 | 0.76471 |
| test | scenario_1_b_c.j2 | scenario_1_a_c.j2 | 0.87805 |
| test | scenario_1_c_c.j2 | scenario_1_c_b.j2 | 0.89744 |
| test | scenario_1_d_a.j2 | scenario_1_d_b.j2 | 0.90000 |
| test | scenario_1_e_a.j2 | scenario_1_a_a.j2 | 0.72727 |
| test | scenario_3_a_b.j2 | scenario_3_a_a.j2 | 0.62069 |
| test | scenario_3_b_b.j2 | scenario_3_b_a.j2 | 0.62963 |
| test | scenario_6_c.j2 | scenario_7.j2 | 0.00000 |

## 2. Markov order and held-out next-technique performance

Order-0 and order-1 baselines pool training scenarios and never receive test scenario identity. The validation winner is descriptive; the tested generator remains the inherited per-scenario first-order model.

| Split | Order | Windows | Log likelihood | NLL | PPL | Top-1 % | Top-3 % | Top-5 % |
|---|---|---|---|---|---|---|---|---|
| validation | order0 | 265 | -984.30474 | 3.71436 | 41.03222 | 18.49057 | 33.20755 | 37.73585 |
| validation | order1 | 265 | -394.20992 | 1.48758 | 4.42639 | 58.49057 | 82.64151 | 87.54717 |
| test | order0 | 272 | -1318.80813 | 4.84856 | 127.55649 | 14.33824 | 26.10294 | 30.51471 |
| test | order1 | 272 | -515.47127 | 1.89511 | 6.65331 | 53.67647 | 70.95588 | 74.26471 |

Validation-selected baseline: **order1**.
AIC/BIC are omitted: the inherited weighted, smoothed estimator is not an unconstrained maximum-likelihood fit. Held-out log likelihood is the selection criterion.

## 3. Original-data learning curve and augmentation ablation

All three encoders use the same selected epoch budget. Accuracy equals Top-1 and is not duplicated as a separate statistic. Macro-F1 averages labels with test support.

| Condition | Encoder | Seeds | Top-1 % | Top-3 % | Top-5 % | Macro-F1 % | NLL | PPL | Run-macro Top-1 % |
|---|---|---|---|---|---|---|---|---|---|
| real_25 | Transformer | 10 | 59.154 +/- 2.508 | 69.926 +/- 2.857 | 71.838 +/- 1.985 | 55.067 +/- 2.202 | 2.165 +/- 0.225 | 8.912 +/- 2.037 | 57.468 +/- 2.208 |
| real_25 | GRU | 10 | 59.963 +/- 2.933 | 64.926 +/- 2.274 | 66.544 +/- 2.463 | 57.467 +/- 2.272 | 2.348 +/- 0.193 | 10.649 +/- 2.173 | 58.054 +/- 2.458 |
| real_25 | LSTM | 10 | 61.176 +/- 2.320 | 64.963 +/- 2.080 | 66.471 +/- 1.833 | 57.820 +/- 2.118 | 2.355 +/- 0.243 | 10.830 +/- 2.732 | 59.213 +/- 1.913 |
| real_50 | Transformer | 10 | 62.426 +/- 3.576 | 72.757 +/- 4.048 | 74.191 +/- 3.855 | 61.193 +/- 5.308 | 2.035 +/- 0.273 | 7.909 +/- 2.159 | 61.788 +/- 3.329 |
| real_50 | GRU | 10 | 64.044 +/- 2.925 | 68.456 +/- 3.227 | 70.294 +/- 3.114 | 64.414 +/- 4.501 | 2.256 +/- 0.246 | 9.806 +/- 2.449 | 63.194 +/- 3.131 |
| real_50 | LSTM | 10 | 64.706 +/- 2.623 | 68.640 +/- 3.252 | 70.110 +/- 2.905 | 64.207 +/- 4.483 | 2.172 +/- 0.323 | 9.193 +/- 2.951 | 63.957 +/- 2.558 |
| real_75 | Transformer | 10 | 65.551 +/- 2.583 | 75.110 +/- 1.343 | 76.949 +/- 1.681 | 64.856 +/- 4.155 | 1.904 +/- 0.233 | 6.899 +/- 1.898 | 64.758 +/- 2.417 |
| real_75 | GRU | 10 | 67.243 +/- 2.090 | 71.875 +/- 2.422 | 73.419 +/- 2.445 | 68.039 +/- 4.070 | 2.123 +/- 0.155 | 8.445 +/- 1.318 | 66.432 +/- 2.092 |
| real_75 | LSTM | 10 | 67.757 +/- 1.201 | 71.801 +/- 1.541 | 73.199 +/- 1.359 | 68.351 +/- 3.254 | 2.097 +/- 0.209 | 8.292 +/- 1.604 | 67.069 +/- 1.446 |
| real_100 | Transformer | 10 | 69.890 +/- 1.325 | 77.721 +/- 0.395 | 79.412 +/- 0.245 | 71.088 +/- 2.463 | 1.747 +/- 0.164 | 5.811 +/- 0.975 | 69.540 +/- 1.131 |
| real_100 | GRU | 10 | 70.846 +/- 1.214 | 75.074 +/- 0.962 | 76.728 +/- 0.934 | 73.740 +/- 1.517 | 1.908 +/- 0.103 | 6.775 +/- 0.726 | 70.741 +/- 1.347 |
| real_100 | LSTM | 10 | 71.066 +/- 0.814 | 74.816 +/- 0.937 | 76.250 +/- 0.817 | 73.494 +/- 0.948 | 1.943 +/- 0.187 | 7.086 +/- 1.272 | 71.125 +/- 0.894 |
| markov_25 | Transformer | 10 | 69.375 +/- 1.570 | 77.500 +/- 1.051 | 79.191 +/- 1.322 | 69.789 +/- 2.896 | 1.789 +/- 0.203 | 6.101 +/- 1.320 | 68.933 +/- 1.462 |
| markov_25 | GRU | 10 | 70.110 +/- 0.756 | 75.257 +/- 1.214 | 76.581 +/- 1.320 | 72.850 +/- 1.351 | 2.020 +/- 0.138 | 7.604 +/- 1.088 | 69.886 +/- 0.839 |
| markov_25 | LSTM | 10 | 70.441 +/- 0.798 | 75.184 +/- 1.300 | 76.471 +/- 1.110 | 72.850 +/- 1.254 | 1.944 +/- 0.192 | 7.105 +/- 1.345 | 70.489 +/- 0.877 |
| repeat_25 | Transformer | 10 | 70.882 +/- 1.235 | 77.904 +/- 0.322 | 80.000 +/- 1.378 | 72.919 +/- 1.690 | 1.783 +/- 0.181 | 6.040 +/- 1.177 | 70.392 +/- 1.079 |
| repeat_25 | GRU | 10 | 70.919 +/- 1.181 | 75.331 +/- 0.784 | 76.691 +/- 0.937 | 73.689 +/- 1.467 | 1.977 +/- 0.129 | 7.274 +/- 0.982 | 70.648 +/- 1.468 |
| repeat_25 | LSTM | 10 | 70.772 +/- 1.288 | 75.184 +/- 0.699 | 76.544 +/- 0.570 | 73.949 +/- 1.644 | 1.984 +/- 0.175 | 7.372 +/- 1.245 | 71.017 +/- 1.100 |
| markov_50 | Transformer | 10 | 68.713 +/- 0.987 | 78.162 +/- 1.590 | 79.963 +/- 2.327 | 69.069 +/- 2.345 | 1.856 +/- 0.206 | 6.525 +/- 1.466 | 68.503 +/- 1.038 |
| markov_50 | GRU | 10 | 70.257 +/- 1.017 | 74.816 +/- 0.760 | 76.507 +/- 0.784 | 72.156 +/- 2.196 | 2.076 +/- 0.135 | 8.042 +/- 1.104 | 70.114 +/- 1.145 |
| markov_50 | LSTM | 10 | 70.257 +/- 0.924 | 74.743 +/- 1.238 | 76.287 +/- 1.277 | 72.420 +/- 1.472 | 1.979 +/- 0.183 | 7.344 +/- 1.318 | 70.313 +/- 0.855 |
| repeat_50 | Transformer | 10 | 70.735 +/- 1.322 | 77.831 +/- 0.426 | 79.338 +/- 0.417 | 71.584 +/- 2.579 | 1.852 +/- 0.166 | 6.457 +/- 1.130 | 70.139 +/- 1.456 |
| repeat_50 | GRU | 10 | 70.846 +/- 1.041 | 75.221 +/- 0.779 | 76.471 +/- 0.755 | 73.870 +/- 1.559 | 2.029 +/- 0.143 | 7.679 +/- 1.166 | 70.594 +/- 1.121 |
| repeat_50 | LSTM | 10 | 71.581 +/- 1.097 | 74.963 +/- 0.784 | 76.213 +/- 0.694 | 73.995 +/- 1.490 | 2.031 +/- 0.195 | 7.750 +/- 1.495 | 71.576 +/- 1.096 |
| markov_100 | Transformer | 10 | 67.978 +/- 1.545 | 77.537 +/- 1.347 | 78.897 +/- 1.240 | 68.232 +/- 2.435 | 1.969 +/- 0.142 | 7.232 +/- 1.072 | 67.828 +/- 1.579 |
| markov_100 | GRU | 10 | 70.221 +/- 1.408 | 74.559 +/- 0.914 | 76.691 +/- 1.126 | 71.944 +/- 2.603 | 2.196 +/- 0.194 | 9.140 +/- 1.733 | 69.672 +/- 1.577 |
| markov_100 | LSTM | 10 | 70.184 +/- 1.181 | 75.110 +/- 1.150 | 76.912 +/- 1.173 | 72.278 +/- 2.193 | 2.109 +/- 0.224 | 8.427 +/- 1.810 | 69.978 +/- 1.296 |
| repeat_100 | Transformer | 10 | 71.581 +/- 0.966 | 77.500 +/- 0.417 | 79.375 +/- 1.116 | 73.388 +/- 1.796 | 1.977 +/- 0.228 | 7.392 +/- 1.655 | 71.032 +/- 1.021 |
| repeat_100 | GRU | 10 | 71.066 +/- 0.918 | 75.037 +/- 1.032 | 76.176 +/- 0.930 | 74.032 +/- 1.062 | 2.151 +/- 0.189 | 8.746 +/- 1.866 | 70.715 +/- 0.934 |
| repeat_100 | LSTM | 10 | 71.434 +/- 0.521 | 74.853 +/- 0.698 | 76.360 +/- 0.602 | 74.371 +/- 1.321 | 2.150 +/- 0.184 | 8.715 +/- 1.553 | 71.578 +/- 0.530 |
| markov_200 | Transformer | 10 | 65.515 +/- 1.529 | 77.463 +/- 1.626 | 79.118 +/- 1.605 | 65.193 +/- 1.719 | 2.053 +/- 0.195 | 7.927 +/- 1.525 | 65.473 +/- 1.582 |
| markov_200 | GRU | 10 | 69.191 +/- 1.816 | 74.963 +/- 1.116 | 77.390 +/- 1.955 | 70.196 +/- 2.728 | 2.405 +/- 0.309 | 11.672 +/- 4.845 | 68.734 +/- 1.827 |
| markov_200 | LSTM | 10 | 68.088 +/- 1.687 | 74.522 +/- 1.690 | 76.397 +/- 1.186 | 69.135 +/- 2.902 | 2.555 +/- 0.354 | 13.660 +/- 5.204 | 67.757 +/- 1.806 |
| repeat_200 | Transformer | 10 | 72.279 +/- 0.779 | 78.125 +/- 1.153 | 79.485 +/- 1.427 | 74.341 +/- 1.188 | 2.101 +/- 0.224 | 8.360 +/- 1.905 | 71.654 +/- 0.951 |
| repeat_200 | GRU | 10 | 71.250 +/- 1.247 | 74.926 +/- 0.946 | 76.360 +/- 1.011 | 74.225 +/- 1.783 | 2.286 +/- 0.190 | 9.996 +/- 1.942 | 71.098 +/- 1.274 |
| repeat_200 | LSTM | 10 | 71.544 +/- 0.698 | 74.816 +/- 0.760 | 76.213 +/- 0.650 | 74.617 +/- 0.836 | 2.307 +/- 0.234 | 10.300 +/- 2.426 | 71.573 +/- 0.876 |

### Secondary: validation-best checkpoints

These checkpoints may have different selected epochs. Primary comparisons and downstream encoders use the final common epoch instead.

| Condition | Encoder | Seeds | Selected epoch | Test Top-1 % | Test NLL |
|---|---|---|---|---|---|
| markov_100 | GRU | 10 | 43.500 +/- 8.670 | 68.860 +/- 1.716 | 1.808 +/- 0.118 |
| markov_100 | LSTM | 10 | 44.700 +/- 8.042 | 68.787 +/- 1.391 | 1.821 +/- 0.159 |
| markov_100 | Transformer | 10 | 81.400 +/- 9.070 | 68.015 +/- 1.784 | 1.915 +/- 0.146 |
| markov_200 | GRU | 10 | 34.700 +/- 6.717 | 67.096 +/- 1.735 | 1.812 +/- 0.137 |
| markov_200 | LSTM | 10 | 42.300 +/- 8.420 | 67.243 +/- 1.535 | 1.944 +/- 0.253 |
| markov_200 | Transformer | 10 | 62.400 +/- 15.643 | 64.632 +/- 1.538 | 1.886 +/- 0.251 |
| markov_25 | GRU | 10 | 43.000 +/- 6.515 | 69.265 +/- 0.798 | 1.723 +/- 0.091 |
| markov_25 | LSTM | 10 | 44.200 +/- 5.673 | 69.632 +/- 1.240 | 1.688 +/- 0.148 |
| markov_25 | Transformer | 10 | 69.900 +/- 13.739 | 68.162 +/- 1.322 | 1.696 +/- 0.155 |
| markov_50 | GRU | 10 | 43.500 +/- 6.964 | 69.265 +/- 1.311 | 1.735 +/- 0.137 |
| markov_50 | LSTM | 10 | 46.200 +/- 4.894 | 69.228 +/- 0.832 | 1.724 +/- 0.151 |
| markov_50 | Transformer | 10 | 80.800 +/- 7.391 | 68.382 +/- 1.481 | 1.800 +/- 0.150 |
| real_100 | GRU | 10 | 46.800 +/- 6.460 | 70.257 +/- 1.129 | 1.685 +/- 0.085 |
| real_100 | LSTM | 10 | 49.300 +/- 7.987 | 71.140 +/- 1.100 | 1.703 +/- 0.138 |
| real_100 | Transformer | 10 | 76.200 +/- 8.728 | 68.750 +/- 0.459 | 1.695 +/- 0.169 |
| real_25 | GRU | 10 | 46.600 +/- 11.355 | 59.265 +/- 2.644 | 2.192 +/- 0.142 |
| real_25 | LSTM | 10 | 55.500 +/- 7.835 | 60.956 +/- 2.552 | 2.228 +/- 0.201 |
| real_25 | Transformer | 10 | 77.000 +/- 9.684 | 58.934 +/- 2.768 | 2.138 +/- 0.198 |
| real_50 | GRU | 10 | 40.600 +/- 13.615 | 62.941 +/- 2.728 | 2.003 +/- 0.152 |
| real_50 | LSTM | 10 | 47.700 +/- 12.867 | 64.853 +/- 3.149 | 2.004 +/- 0.257 |
| real_50 | Transformer | 10 | 67.700 +/- 16.276 | 61.875 +/- 4.436 | 1.965 +/- 0.228 |
| real_75 | GRU | 10 | 43.200 +/- 10.218 | 66.250 +/- 1.799 | 1.851 +/- 0.117 |
| real_75 | LSTM | 10 | 42.200 +/- 11.736 | 66.985 +/- 1.235 | 1.855 +/- 0.154 |
| real_75 | Transformer | 10 | 72.600 +/- 8.462 | 65.074 +/- 2.821 | 1.859 +/- 0.245 |
| repeat_100 | GRU | 10 | 24.400 +/- 4.600 | 70.184 +/- 1.194 | 1.678 +/- 0.099 |
| repeat_100 | LSTM | 10 | 26.600 +/- 4.377 | 70.110 +/- 1.110 | 1.721 +/- 0.126 |
| repeat_100 | Transformer | 10 | 40.300 +/- 10.133 | 68.603 +/- 0.904 | 1.707 +/- 0.153 |
| repeat_200 | GRU | 10 | 17.900 +/- 2.331 | 70.515 +/- 1.211 | 1.692 +/- 0.095 |
| repeat_200 | LSTM | 10 | 16.500 +/- 4.528 | 70.294 +/- 0.771 | 1.699 +/- 0.117 |
| repeat_200 | Transformer | 10 | 31.400 +/- 6.603 | 70.037 +/- 1.400 | 1.766 +/- 0.183 |
| repeat_25 | GRU | 10 | 44.300 +/- 8.551 | 70.699 +/- 1.262 | 1.706 +/- 0.090 |
| repeat_25 | LSTM | 10 | 42.100 +/- 6.657 | 70.588 +/- 1.054 | 1.700 +/- 0.121 |
| repeat_25 | Transformer | 10 | 67.700 +/- 13.392 | 69.375 +/- 1.309 | 1.710 +/- 0.149 |
| repeat_50 | GRU | 10 | 34.800 +/- 3.910 | 70.478 +/- 1.026 | 1.670 +/- 0.112 |
| repeat_50 | LSTM | 10 | 34.600 +/- 7.306 | 70.625 +/- 1.002 | 1.683 +/- 0.126 |
| repeat_50 | Transformer | 10 | 53.800 +/- 6.779 | 69.449 +/- 1.046 | 1.707 +/- 0.170 |

## 4. Paired evidence for augmentation

Primary prediction metric: Top-1. Paired tests compare matched training seeds; 95% t intervals describe seed variability conditional on this fixed split. Holm correction covers all listed prediction contrasts. These intervals do not establish population-wide campaign generalization.

| Contrast | Paired seeds | Delta (fraction) | 95% CI | Raw p | Holm p |
|---|---|---|---|---|---|
| Transformer: markov_25 minus real_100 | 10 | -0.00515 | [-0.018568879097328003, 0.008274761450269152] | 0.40820 | 0.94673 |
| Transformer: markov_25 minus repeat_25 | 10 | -0.01507 | [-0.023339302823530014, -0.0068077559999993546] | 0.00258 | 0.04640 |
| GRU: markov_25 minus real_100 | 10 | -0.00735 | [-0.014029406722531158, -0.000676475630410055] | 0.03435 | 0.41214 |
| GRU: markov_25 minus repeat_25 | 10 | -0.00809 | [-0.013876866213465873, -0.0022996043747694293] | 0.01153 | 0.18456 |
| LSTM: markov_25 minus real_100 | 10 | -0.00625 | [-0.014289529132493648, 0.001789529132493627] | 0.11251 | 0.89843 |
| LSTM: markov_25 minus repeat_25 | 10 | -0.00331 | [-0.012868067431774207, 0.0062504203729506795] | 0.45373 | 0.94673 |
| Transformer: markov_50 minus real_100 | 10 | -0.01176 | [-0.023114020164133296, -0.00041539160057263436] | 0.04366 | 0.48031 |
| Transformer: markov_50 minus repeat_50 | 10 | -0.02022 | [-0.029843935078206832, -0.010597241392381392] | 0.00104 | 0.02079 |
| GRU: markov_50 minus real_100 | 10 | -0.00588 | [-0.014839771427432447, 0.0030750655450794816] | 0.17156 | 0.94673 |
| GRU: markov_50 minus repeat_50 | 10 | -0.00588 | [-0.013444046669946056, 0.0016793407875931345] | 0.11230 | 0.89843 |
| LSTM: markov_50 minus real_100 | 10 | -0.00809 | [-0.016386487311987732, 0.00021001672375247672] | 0.05490 | 0.54900 |
| LSTM: markov_50 minus repeat_50 | 10 | -0.01324 | [-0.02362291687774806, -0.0028476713575459854] | 0.01811 | 0.27165 |
| Transformer: markov_100 minus real_100 | 10 | -0.01912 | [-0.03444295784071557, -0.0037923362769315353] | 0.01998 | 0.27165 |
| Transformer: markov_100 minus repeat_100 | 10 | -0.03603 | [-0.049196876473386775, -0.022861947056024984] | 0.00016 | 0.00370 |
| GRU: markov_100 minus real_100 | 10 | -0.00625 | [-0.017817300045509094, 0.0053173000455090935] | 0.25265 | 0.94673 |
| GRU: markov_100 minus repeat_100 | 10 | -0.00846 | [-0.02091868655746759, 0.00400692185158525] | 0.15919 | 0.94673 |
| LSTM: markov_100 minus real_100 | 10 | -0.00882 | [-0.021779171222215763, 0.004132112398686324] | 0.15779 | 0.94673 |
| LSTM: markov_100 minus repeat_100 | 10 | -0.01250 | [-0.02235612385562427, -0.00264387614437577] | 0.01851 | 0.27165 |
| Transformer: markov_200 minus real_100 | 10 | -0.04375 | [-0.06117112441189599, -0.026328875588104005] | 0.00030 | 0.00663 |
| Transformer: markov_200 minus repeat_200 | 10 | -0.06765 | [-0.07868048018502434, -0.05661363746203445] | 0.00000 | 0.00001 |
| GRU: markov_200 minus real_100 | 10 | -0.01654 | [-0.033956416767399654, 0.0008681814732820134] | 0.06010 | 0.54900 |
| GRU: markov_200 minus repeat_200 | 10 | -0.02059 | [-0.033837161012231894, -0.007339309576003384] | 0.00656 | 0.11158 |
| LSTM: markov_200 minus real_100 | 10 | -0.02978 | [-0.045286683493635495, -0.014272140035776303] | 0.00187 | 0.03546 |
| LSTM: markov_200 minus repeat_200 | 10 | -0.03456 | [-0.04843116522804343, -0.020686481830780118] | 0.00032 | 0.00671 |

| Dose | Encoder | Decision against both controls |
|---|---|---|
| markov_25 | Transformer | Benefit criteria not met under this protocol |
| markov_25 | GRU | Benefit criteria not met under this protocol |
| markov_25 | LSTM | Benefit criteria not met under this protocol |
| markov_50 | Transformer | Benefit criteria not met under this protocol |
| markov_50 | GRU | Benefit criteria not met under this protocol |
| markov_50 | LSTM | Benefit criteria not met under this protocol |
| markov_100 | Transformer | Benefit criteria not met under this protocol |
| markov_100 | GRU | Benefit criteria not met under this protocol |
| markov_100 | LSTM | Benefit criteria not met under this protocol |
| markov_200 | Transformer | Benefit criteria not met under this protocol |
| markov_200 | GRU | Benefit criteria not met under this protocol |
| markov_200 | LSTM | Benefit criteria not met under this protocol |

Interpretation rule: a positive mean alone is inconclusive. A candidate benefit needs a positive paired interval, Holm p < 0.05, and at least +0.01 absolute Top-1 against both original-only and its repeat control. This is a predeclared practical threshold, not a universal standard. Sequence plausibility must be evaluated separately.
A flat/noisy curve gives no evidence of benefit; it does not prove equivalence or establish that real additional campaigns would be useless.

## 5. Synthetic sequence quality

Every generated corpus is saved under synthetic/. Statistical resemblance does not validate causal or executable attack behavior. AEP validity is N/A because no AEP validator is bundled.

| Dose | Seed | Sequences | Unique | Duplicate % | Train-copy % | Mean length | Min | Max | Known IDs % | Train-observed bigrams % | Bigram JS (nats) | Techniques | AEP-valid % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| markov_100 | 0 | 22 | 22 | 0.00000 | 0.00000 | 35.68182 | 5 | 48 | 100.00000 | 82.17562 | 0.14862 | 81 | N/A |
| markov_100 | 1 | 22 | 22 | 0.00000 | 0.00000 | 38.77273 | 23 | 51 | 100.00000 | 83.03249 | 0.12907 | 80 | N/A |
| markov_100 | 2 | 22 | 22 | 0.00000 | 4.54545 | 38.45455 | 5 | 61 | 100.00000 | 82.88835 | 0.13073 | 81 | N/A |
| markov_100 | 3 | 22 | 22 | 0.00000 | 0.00000 | 33.63636 | 5 | 61 | 100.00000 | 83.56546 | 0.12509 | 79 | N/A |
| markov_100 | 4 | 22 | 22 | 0.00000 | 0.00000 | 33.72727 | 5 | 61 | 100.00000 | 77.63889 | 0.15000 | 81 | N/A |
| markov_100 | 5 | 22 | 22 | 0.00000 | 0.00000 | 36.04545 | 5 | 61 | 100.00000 | 79.89624 | 0.15702 | 77 | N/A |
| markov_100 | 6 | 22 | 22 | 0.00000 | 0.00000 | 39.81818 | 5 | 51 | 100.00000 | 80.21077 | 0.14663 | 83 | N/A |
| markov_100 | 7 | 22 | 22 | 0.00000 | 0.00000 | 37.04545 | 16 | 61 | 100.00000 | 76.79697 | 0.16732 | 83 | N/A |
| markov_100 | 8 | 22 | 22 | 0.00000 | 0.00000 | 32.22727 | 5 | 51 | 100.00000 | 83.98836 | 0.13416 | 81 | N/A |
| markov_100 | 9 | 22 | 22 | 0.00000 | 0.00000 | 35.27273 | 16 | 51 | 100.00000 | 78.91247 | 0.17817 | 81 | N/A |
| markov_200 | 0 | 44 | 44 | 0.00000 | 0.00000 | 37.63636 | 5 | 61 | 100.00000 | 81.76179 | 0.10310 | 84 | N/A |
| markov_200 | 1 | 44 | 44 | 0.00000 | 0.00000 | 37.22727 | 22 | 61 | 100.00000 | 77.66625 | 0.12939 | 84 | N/A |
| markov_200 | 2 | 44 | 44 | 0.00000 | 2.27273 | 35.29545 | 5 | 61 | 100.00000 | 83.49901 | 0.10389 | 83 | N/A |
| markov_200 | 3 | 44 | 44 | 0.00000 | 0.00000 | 33.68182 | 5 | 61 | 100.00000 | 77.95549 | 0.11108 | 84 | N/A |
| markov_200 | 4 | 44 | 44 | 0.00000 | 0.00000 | 35.97727 | 5 | 61 | 100.00000 | 79.53216 | 0.10843 | 84 | N/A |
| markov_200 | 5 | 44 | 44 | 0.00000 | 0.00000 | 34.50000 | 5 | 61 | 100.00000 | 79.03664 | 0.11764 | 82 | N/A |
| markov_200 | 6 | 44 | 44 | 0.00000 | 0.00000 | 35.29545 | 5 | 61 | 100.00000 | 77.66733 | 0.12297 | 84 | N/A |
| markov_200 | 7 | 44 | 44 | 0.00000 | 0.00000 | 38.06818 | 5 | 61 | 100.00000 | 81.05457 | 0.11031 | 84 | N/A |
| markov_200 | 8 | 44 | 44 | 0.00000 | 0.00000 | 32.77273 | 5 | 61 | 100.00000 | 77.96853 | 0.12667 | 83 | N/A |
| markov_200 | 9 | 44 | 44 | 0.00000 | 0.00000 | 37.43182 | 16 | 61 | 100.00000 | 75.42109 | 0.13084 | 84 | N/A |
| markov_25 | 0 | 6 | 6 | 0.00000 | 0.00000 | 32.83333 | 5 | 45 | 100.00000 | 85.34031 | 0.25960 | 55 | N/A |
| markov_25 | 1 | 6 | 6 | 0.00000 | 0.00000 | 38.16667 | 23 | 48 | 100.00000 | 81.16592 | 0.22381 | 62 | N/A |
| markov_25 | 2 | 6 | 6 | 0.00000 | 0.00000 | 38.33333 | 27 | 44 | 100.00000 | 81.25000 | 0.25421 | 53 | N/A |
| markov_25 | 3 | 6 | 6 | 0.00000 | 0.00000 | 39.66667 | 30 | 45 | 100.00000 | 87.06897 | 0.23131 | 57 | N/A |
| markov_25 | 4 | 6 | 6 | 0.00000 | 0.00000 | 34.50000 | 16 | 61 | 100.00000 | 80.59701 | 0.28036 | 62 | N/A |
| markov_25 | 5 | 6 | 6 | 0.00000 | 0.00000 | 32.50000 | 16 | 51 | 100.00000 | 87.30159 | 0.19619 | 52 | N/A |
| markov_25 | 6 | 6 | 6 | 0.00000 | 0.00000 | 45.50000 | 27 | 51 | 100.00000 | 83.52060 | 0.20625 | 63 | N/A |
| markov_25 | 7 | 6 | 6 | 0.00000 | 0.00000 | 34.33333 | 16 | 48 | 100.00000 | 70.00000 | 0.31484 | 63 | N/A |
| markov_25 | 8 | 6 | 6 | 0.00000 | 0.00000 | 31.66667 | 5 | 51 | 100.00000 | 83.15217 | 0.22941 | 59 | N/A |
| markov_25 | 9 | 6 | 6 | 0.00000 | 0.00000 | 31.66667 | 23 | 44 | 100.00000 | 65.21739 | 0.35912 | 66 | N/A |
| markov_50 | 0 | 11 | 11 | 0.00000 | 0.00000 | 36.09091 | 5 | 45 | 100.00000 | 86.78756 | 0.19294 | 65 | N/A |
| markov_50 | 1 | 11 | 11 | 0.00000 | 0.00000 | 37.54545 | 23 | 48 | 100.00000 | 78.60697 | 0.18733 | 70 | N/A |
| markov_50 | 2 | 11 | 11 | 0.00000 | 0.00000 | 41.00000 | 27 | 45 | 100.00000 | 83.18182 | 0.22555 | 65 | N/A |
| markov_50 | 3 | 11 | 11 | 0.00000 | 0.00000 | 34.54545 | 5 | 45 | 100.00000 | 84.55285 | 0.19772 | 65 | N/A |
| markov_50 | 4 | 11 | 11 | 0.00000 | 0.00000 | 35.90909 | 16 | 61 | 100.00000 | 82.29167 | 0.19746 | 70 | N/A |
| markov_50 | 5 | 11 | 11 | 0.00000 | 0.00000 | 34.63636 | 16 | 51 | 100.00000 | 84.05405 | 0.16025 | 66 | N/A |
| markov_50 | 6 | 11 | 11 | 0.00000 | 0.00000 | 40.81818 | 27 | 51 | 100.00000 | 81.96347 | 0.18061 | 70 | N/A |
| markov_50 | 7 | 11 | 11 | 0.00000 | 0.00000 | 36.45455 | 16 | 61 | 100.00000 | 72.30769 | 0.31422 | 75 | N/A |
| markov_50 | 8 | 11 | 11 | 0.00000 | 0.00000 | 33.90909 | 5 | 51 | 100.00000 | 82.04420 | 0.17791 | 73 | N/A |
| markov_50 | 9 | 11 | 11 | 0.00000 | 0.00000 | 32.90909 | 16 | 45 | 100.00000 | 68.94587 | 0.27635 | 78 | N/A |

## 6. Downstream deception: IPPO and MAPPO

Primary downstream comparison: original-only, +100% Markov, and the +100% matched-repeat encoder control. Markov condition changes both encoder training data and policy training episodes; this estimates full-system augmentation, not an isolated encoder effect.
Every policy is evaluated on identical held-out original sequences and matched environment uniforms. Repeats add simulation variation, not new attack data.
Dwell = decoy-engaged steps; depth = distinct parent techniques engaged; protection = configured attacker objective not reached before termination.

| Condition | Model | Seeds | Dwell (steps) | Depth (techniques) | Asset protection % |
|---|---|---|---|---|---|
| real_100 | Transformer + IPPO | 10 | 14.678 +/- 0.505 | 10.044 +/- 0.588 | 33.429 +/- 3.136 |
| real_100 | Transformer + MAPPO | 10 | 15.047 +/- 0.740 | 10.227 +/- 0.645 | 34.543 +/- 5.222 |
| real_100 | GRU + IPPO | 10 | 15.313 +/- 0.839 | 10.476 +/- 0.720 | 37.286 +/- 6.124 |
| real_100 | GRU + MAPPO | 10 | 15.291 +/- 0.767 | 10.466 +/- 0.643 | 36.600 +/- 4.239 |
| real_100 | LSTM + IPPO | 10 | 15.272 +/- 0.765 | 10.417 +/- 0.572 | 38.400 +/- 3.179 |
| real_100 | LSTM + MAPPO | 10 | 15.233 +/- 0.340 | 10.478 +/- 0.292 | 37.343 +/- 3.127 |
| real_100 | NoHistory + IPPO | 10 | 11.263 +/- 0.498 | 7.766 +/- 0.341 | 27.657 +/- 2.882 |
| real_100 | NoHistory + MAPPO | 10 | 11.529 +/- 0.333 | 7.876 +/- 0.205 | 28.886 +/- 2.169 |
| markov_100 | Transformer + IPPO | 10 | 14.072 +/- 0.419 | 9.551 +/- 0.397 | 35.600 +/- 4.163 |
| markov_100 | Transformer + MAPPO | 10 | 14.120 +/- 0.850 | 9.529 +/- 0.627 | 35.143 +/- 4.581 |
| markov_100 | GRU + IPPO | 10 | 14.016 +/- 0.702 | 9.555 +/- 0.553 | 33.771 +/- 4.654 |
| markov_100 | GRU + MAPPO | 10 | 14.811 +/- 0.733 | 10.029 +/- 0.518 | 35.257 +/- 5.199 |
| markov_100 | LSTM + IPPO | 10 | 14.285 +/- 0.645 | 9.780 +/- 0.555 | 32.371 +/- 5.670 |
| markov_100 | LSTM + MAPPO | 10 | 14.394 +/- 1.264 | 9.782 +/- 0.860 | 33.886 +/- 4.319 |
| repeat_100 | Transformer + IPPO | 10 | 15.045 +/- 0.861 | 10.227 +/- 0.729 | 36.800 +/- 3.730 |
| repeat_100 | Transformer + MAPPO | 10 | 15.425 +/- 0.517 | 10.526 +/- 0.331 | 36.971 +/- 4.795 |
| repeat_100 | GRU + IPPO | 10 | 15.188 +/- 0.537 | 10.373 +/- 0.492 | 36.171 +/- 4.504 |
| repeat_100 | GRU + MAPPO | 10 | 15.436 +/- 0.702 | 10.507 +/- 0.566 | 37.143 +/- 4.710 |
| repeat_100 | LSTM + IPPO | 10 | 14.987 +/- 0.893 | 10.218 +/- 0.651 | 36.143 +/- 4.776 |
| repeat_100 | LSTM + MAPPO | 10 | 15.595 +/- 0.443 | 10.727 +/- 0.282 | 39.000 +/- 2.674 |

### Downstream paired tests

Holm correction is separate from the prediction family and includes all 36 downstream comparisons. Protection deltas are fractions, not percentage points.

| Contrast | Metric | Seeds | Delta | 95% CI | Raw p | Holm p |
|---|---|---|---|---|---|---|
| Transformer+IPPO: markov_100 minus real_100 | dwell | 10 | -0.60600 | [-1.1122267174564382, -0.09977328254356221] | 0.02408 | 0.60190 |
| Transformer+IPPO: markov_100 minus real_100 | depth | 10 | -0.49257 | [-0.9824828365190816, -0.0026600206237761825] | 0.04901 | 1.00000 |
| Transformer+IPPO: markov_100 minus real_100 | protected | 10 | 0.02171 | [-0.008157098916917255, 0.05158567034548869] | 0.13450 | 1.00000 |
| Transformer+IPPO: markov_100 minus repeat_100 | dwell | 10 | -0.97314 | [-1.6251927570862472, -0.32109295719946673] | 0.00818 | 0.22175 |
| Transformer+IPPO: markov_100 minus repeat_100 | depth | 10 | -0.67600 | [-1.2102167472621366, -0.14178325273786363] | 0.01870 | 0.48627 |
| Transformer+IPPO: markov_100 minus repeat_100 | protected | 10 | -0.01200 | [-0.053450351555677275, 0.029450351555677292] | 0.52891 | 1.00000 |
| Transformer+MAPPO: markov_100 minus real_100 | dwell | 10 | -0.92743 | [-1.8815113276819657, 0.02665418482482307] | 0.05543 | 1.00000 |
| Transformer+MAPPO: markov_100 minus real_100 | depth | 10 | -0.69857 | [-1.4855488134429218, 0.08840595630006387] | 0.07557 | 1.00000 |
| Transformer+MAPPO: markov_100 minus real_100 | protected | 10 | 0.00600 | [-0.04282019055518374, 0.05482019055518375] | 0.78728 | 1.00000 |
| Transformer+MAPPO: markov_100 minus repeat_100 | dwell | 10 | -1.30543 | [-2.110671359624178, -0.5001857832329647] | 0.00518 | 0.15529 |
| Transformer+MAPPO: markov_100 minus repeat_100 | depth | 10 | -0.99771 | [-1.55394828305684, -0.4414802883717317] | 0.00285 | 0.09412 |
| Transformer+MAPPO: markov_100 minus repeat_100 | protected | 10 | -0.01829 | [-0.07450946124842425, 0.03793803267699569] | 0.48063 | 1.00000 |
| GRU+IPPO: markov_100 minus real_100 | dwell | 10 | -1.29686 | [-2.0009973305581448, -0.5927169551561406] | 0.00242 | 0.08244 |
| GRU+IPPO: markov_100 minus real_100 | depth | 10 | -0.92143 | [-1.509355990261167, -0.33350115259597624] | 0.00626 | 0.18158 |
| GRU+IPPO: markov_100 minus real_100 | protected | 10 | -0.03514 | [-0.07800529379058882, 0.007719579504874542] | 0.09662 | 1.00000 |
| GRU+IPPO: markov_100 minus repeat_100 | dwell | 10 | -1.17257 | [-1.7867602645964236, -0.5583825925464331] | 0.00194 | 0.06778 |
| GRU+IPPO: markov_100 minus repeat_100 | depth | 10 | -0.81857 | [-1.3182009754112725, -0.318941881731585] | 0.00487 | 0.15108 |
| GRU+IPPO: markov_100 minus repeat_100 | protected | 10 | -0.02400 | [-0.05839277933553485, 0.010392779335534862] | 0.14889 | 1.00000 |
| GRU+MAPPO: markov_100 minus real_100 | dwell | 10 | -0.48029 | [-1.1553817145103307, 0.19481028593890248] | 0.14200 | 1.00000 |
| GRU+MAPPO: markov_100 minus real_100 | depth | 10 | -0.43714 | [-0.9205513048440646, 0.04626559055835028] | 0.07111 | 1.00000 |
| GRU+MAPPO: markov_100 minus real_100 | protected | 10 | -0.01343 | [-0.0509559665849016, 0.024098823727758727] | 0.43912 | 1.00000 |
| GRU+MAPPO: markov_100 minus repeat_100 | dwell | 10 | -0.62514 | [-1.3644902167495716, 0.11420450246385816] | 0.08808 | 1.00000 |
| GRU+MAPPO: markov_100 minus repeat_100 | depth | 10 | -0.47800 | [-1.0388571359858831, 0.08285713598588296] | 0.08595 | 1.00000 |
| GRU+MAPPO: markov_100 minus repeat_100 | protected | 10 | -0.01886 | [-0.05838618894775992, 0.0206719032334742] | 0.30859 | 1.00000 |
| LSTM+IPPO: markov_100 minus real_100 | dwell | 10 | -0.98714 | [-1.8612471064142757, -0.11303860787143905] | 0.03096 | 0.71197 |
| LSTM+IPPO: markov_100 minus real_100 | depth | 10 | -0.63657 | [-1.3177600193930958, 0.044617162250238485] | 0.06366 | 1.00000 |
| LSTM+IPPO: markov_100 minus real_100 | protected | 10 | -0.06029 | [-0.11124574010549323, -0.009325688465935317] | 0.02537 | 0.60879 |
| LSTM+IPPO: markov_100 minus repeat_100 | dwell | 10 | -0.70200 | [-1.4730808546795606, 0.06908085467956027] | 0.06954 | 1.00000 |
| LSTM+IPPO: markov_100 minus repeat_100 | depth | 10 | -0.43800 | [-0.9991028760779637, 0.12310287607796355] | 0.11123 | 1.00000 |
| LSTM+IPPO: markov_100 minus repeat_100 | protected | 10 | -0.03771 | [-0.07827035175440322, 0.002841780325831815] | 0.06473 | 1.00000 |
| LSTM+MAPPO: markov_100 minus real_100 | dwell | 10 | -0.83914 | [-1.7349513163064496, 0.05666560202073512] | 0.06313 | 1.00000 |
| LSTM+MAPPO: markov_100 minus real_100 | depth | 10 | -0.69600 | [-1.3651082551791305, -0.026891744820869756] | 0.04309 | 0.94793 |
| LSTM+MAPPO: markov_100 minus real_100 | protected | 10 | -0.03457 | [-0.0741620733791418, 0.005019216236284631] | 0.07965 | 1.00000 |
| LSTM+MAPPO: markov_100 minus repeat_100 | dwell | 10 | -1.20171 | [-2.002131658541335, -0.4012969128872368] | 0.00792 | 0.22175 |
| LSTM+MAPPO: markov_100 minus repeat_100 | depth | 10 | -0.94514 | [-1.5029434472646737, -0.38734226702104047] | 0.00401 | 0.12829 |
| LSTM+MAPPO: markov_100 minus repeat_100 | protected | 10 | -0.05114 | [-0.07704003089437972, -0.02524568339133459] | 0.00156 | 0.05618 |

### Validation-selected original-only ablation

Selected encoder: LSTM. Selection uses mean validation dwell; test results do not select the winner.

| Model | Dwell | Depth | Protection % |
|---|---|---|---|
| LSTM+IPPO | 15.272 +/- 0.765 | 10.417 +/- 0.572 | 38.400 +/- 3.179 |
| NoHistory+IPPO | 11.263 +/- 0.498 | 7.766 +/- 0.341 | 27.657 +/- 2.882 |
| LSTM+MAPPO | 15.233 +/- 0.340 | 10.478 +/- 0.292 | 37.343 +/- 3.127 |
| NoHistory+MAPPO | 11.529 +/- 0.333 | 7.876 +/- 0.205 | 28.886 +/- 2.169 |

## 7. Generalization and limitations

Held-out scenario: None: grouped variant holdout, not LOSO.
Use --held-out S1 ... S7 in separate output folders for optional scenario holdout. Single-fold or variant results must not be labeled seven-fold LOSO.
Singleton scenarios are training-only in the main split. Variant similarity remains and is reported above. Test-set size limits generalization claims.
The inherited vocabulary, payoff, goals and environment calibration were fixed using the earlier corpus. The new split isolates estimator/encoder/policy fitting, not historical environment design.
This source bundle contains a fixed five-zone coordinated-engagement simulator; it is not the earlier variable-topology v3 experiment.
No new raw telemetry or independent incidents are created by augmentation. Preserving the estimator does not establish the validity of every generated chain.
No full experiment was run during package construction. Only smoke/test outputs may be present until the lab run completes.

