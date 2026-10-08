# Markov augmentation usefulness study

**SMOKE TEST ONLY: NOT THESIS EVIDENCE.**

Prediction cells: 0/9. Deception cells: 0/20.
Training seeds: [0]. Source SHA256: `2a1deea60f8b3fdc4a73f7a4456b8525ed576aff72e58c7d08de249bc25d195c`.

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
Main cells complete every epoch. Lowest validation NLL selects encoder checkpoints; lowest test loss never selects anything.
PPO epochs are separate: the same PPO passes per rollout and environment-step budget apply to every IPPO/MAPPO arm.

Epoch budget pending. Default: real-only validation pilots for all three encoders, capped at 100 epochs; take the maximum validation-best epoch across pilots.

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
| real_100 | Transformer | 0 | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| real_100 | GRU | 0 | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| real_100 | LSTM | 0 | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| markov_100 | Transformer | 0 | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| markov_100 | GRU | 0 | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| markov_100 | LSTM | 0 | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| repeat_100 | Transformer | 0 | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| repeat_100 | GRU | 0 | Pending | Pending | Pending | Pending | Pending | Pending | Pending |
| repeat_100 | LSTM | 0 | Pending | Pending | Pending | Pending | Pending | Pending | Pending |

## 4. Paired evidence for augmentation

Primary prediction metric: Top-1. Paired tests compare matched training seeds; 95% t intervals describe seed variability conditional on this fixed split. Holm correction covers all listed prediction contrasts. These intervals do not establish population-wide campaign generalization.

| Contrast | Paired seeds | Delta (fraction) | 95% CI | Raw p | Holm p |
|---|---|---|---|---|---|
| Transformer: markov_100 minus real_100 | 0 | N/A | N/A | N/A | N/A |
| Transformer: markov_100 minus repeat_100 | 0 | N/A | N/A | N/A | N/A |
| GRU: markov_100 minus real_100 | 0 | N/A | N/A | N/A | N/A |
| GRU: markov_100 minus repeat_100 | 0 | N/A | N/A | N/A | N/A |
| LSTM: markov_100 minus real_100 | 0 | N/A | N/A | N/A | N/A |
| LSTM: markov_100 minus repeat_100 | 0 | N/A | N/A | N/A | N/A |

Interpretation rule: a positive mean alone is inconclusive. A candidate benefit needs a positive paired interval, Holm p < 0.05, and at least +0.01 absolute Top-1 against both original-only and its repeat control. This is a predeclared practical threshold, not a universal standard. Sequence plausibility must be evaluated separately.
A flat/noisy curve gives no evidence of benefit; it does not prove equivalence or establish that real additional campaigns would be useless.

## 5. Synthetic sequence quality

Every generated corpus is saved under synthetic/. Statistical resemblance does not validate causal or executable attack behavior. AEP validity is N/A because no AEP validator is bundled.

| Dose | Seed | Sequences | Unique | Duplicate % | Train-copy % | Mean length | Min | Max | Known IDs % | Train-observed bigrams % | Bigram JS (nats) | Techniques | AEP-valid % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## 6. Downstream deception: IPPO and MAPPO

Primary downstream comparison: original-only, +100% Markov, and the +100% matched-repeat encoder control. Markov condition changes both encoder training data and policy training episodes; this estimates full-system augmentation, not an isolated encoder effect.
Every policy is evaluated on identical held-out original sequences and matched environment uniforms. Repeats add simulation variation, not new attack data.
Dwell = decoy-engaged steps; depth = distinct parent techniques engaged; protection = configured attacker objective not reached before termination.

| Condition | Model | Seeds | Dwell (steps) | Depth (techniques) | Asset protection % |
|---|---|---|---|---|---|
| real_100 | Transformer + IPPO | 0 | Pending | Pending | Pending |
| real_100 | Transformer + MAPPO | 0 | Pending | Pending | Pending |
| real_100 | GRU + IPPO | 0 | Pending | Pending | Pending |
| real_100 | GRU + MAPPO | 0 | Pending | Pending | Pending |
| real_100 | LSTM + IPPO | 0 | Pending | Pending | Pending |
| real_100 | LSTM + MAPPO | 0 | Pending | Pending | Pending |
| real_100 | NoHistory + IPPO | 0 | Pending | Pending | Pending |
| real_100 | NoHistory + MAPPO | 0 | Pending | Pending | Pending |
| markov_100 | Transformer + IPPO | 0 | Pending | Pending | Pending |
| markov_100 | Transformer + MAPPO | 0 | Pending | Pending | Pending |
| markov_100 | GRU + IPPO | 0 | Pending | Pending | Pending |
| markov_100 | GRU + MAPPO | 0 | Pending | Pending | Pending |
| markov_100 | LSTM + IPPO | 0 | Pending | Pending | Pending |
| markov_100 | LSTM + MAPPO | 0 | Pending | Pending | Pending |
| repeat_100 | Transformer + IPPO | 0 | Pending | Pending | Pending |
| repeat_100 | Transformer + MAPPO | 0 | Pending | Pending | Pending |
| repeat_100 | GRU + IPPO | 0 | Pending | Pending | Pending |
| repeat_100 | GRU + MAPPO | 0 | Pending | Pending | Pending |
| repeat_100 | LSTM + IPPO | 0 | Pending | Pending | Pending |
| repeat_100 | LSTM + MAPPO | 0 | Pending | Pending | Pending |

### Downstream paired tests

Holm correction is separate from the prediction family and includes all 36 downstream comparisons. Protection deltas are fractions, not percentage points.

| Contrast | Metric | Seeds | Delta | 95% CI | Raw p | Holm p |
|---|---|---|---|---|---|---|
| Transformer+IPPO: markov_100 minus real_100 | dwell | 0 | N/A | N/A | N/A | N/A |
| Transformer+IPPO: markov_100 minus real_100 | depth | 0 | N/A | N/A | N/A | N/A |
| Transformer+IPPO: markov_100 minus real_100 | protected | 0 | N/A | N/A | N/A | N/A |
| Transformer+IPPO: markov_100 minus repeat_100 | dwell | 0 | N/A | N/A | N/A | N/A |
| Transformer+IPPO: markov_100 minus repeat_100 | depth | 0 | N/A | N/A | N/A | N/A |
| Transformer+IPPO: markov_100 minus repeat_100 | protected | 0 | N/A | N/A | N/A | N/A |
| Transformer+MAPPO: markov_100 minus real_100 | dwell | 0 | N/A | N/A | N/A | N/A |
| Transformer+MAPPO: markov_100 minus real_100 | depth | 0 | N/A | N/A | N/A | N/A |
| Transformer+MAPPO: markov_100 minus real_100 | protected | 0 | N/A | N/A | N/A | N/A |
| Transformer+MAPPO: markov_100 minus repeat_100 | dwell | 0 | N/A | N/A | N/A | N/A |
| Transformer+MAPPO: markov_100 minus repeat_100 | depth | 0 | N/A | N/A | N/A | N/A |
| Transformer+MAPPO: markov_100 minus repeat_100 | protected | 0 | N/A | N/A | N/A | N/A |
| GRU+IPPO: markov_100 minus real_100 | dwell | 0 | N/A | N/A | N/A | N/A |
| GRU+IPPO: markov_100 minus real_100 | depth | 0 | N/A | N/A | N/A | N/A |
| GRU+IPPO: markov_100 minus real_100 | protected | 0 | N/A | N/A | N/A | N/A |
| GRU+IPPO: markov_100 minus repeat_100 | dwell | 0 | N/A | N/A | N/A | N/A |
| GRU+IPPO: markov_100 minus repeat_100 | depth | 0 | N/A | N/A | N/A | N/A |
| GRU+IPPO: markov_100 minus repeat_100 | protected | 0 | N/A | N/A | N/A | N/A |
| GRU+MAPPO: markov_100 minus real_100 | dwell | 0 | N/A | N/A | N/A | N/A |
| GRU+MAPPO: markov_100 minus real_100 | depth | 0 | N/A | N/A | N/A | N/A |
| GRU+MAPPO: markov_100 minus real_100 | protected | 0 | N/A | N/A | N/A | N/A |
| GRU+MAPPO: markov_100 minus repeat_100 | dwell | 0 | N/A | N/A | N/A | N/A |
| GRU+MAPPO: markov_100 minus repeat_100 | depth | 0 | N/A | N/A | N/A | N/A |
| GRU+MAPPO: markov_100 minus repeat_100 | protected | 0 | N/A | N/A | N/A | N/A |
| LSTM+IPPO: markov_100 minus real_100 | dwell | 0 | N/A | N/A | N/A | N/A |
| LSTM+IPPO: markov_100 minus real_100 | depth | 0 | N/A | N/A | N/A | N/A |
| LSTM+IPPO: markov_100 minus real_100 | protected | 0 | N/A | N/A | N/A | N/A |
| LSTM+IPPO: markov_100 minus repeat_100 | dwell | 0 | N/A | N/A | N/A | N/A |
| LSTM+IPPO: markov_100 minus repeat_100 | depth | 0 | N/A | N/A | N/A | N/A |
| LSTM+IPPO: markov_100 minus repeat_100 | protected | 0 | N/A | N/A | N/A | N/A |
| LSTM+MAPPO: markov_100 minus real_100 | dwell | 0 | N/A | N/A | N/A | N/A |
| LSTM+MAPPO: markov_100 minus real_100 | depth | 0 | N/A | N/A | N/A | N/A |
| LSTM+MAPPO: markov_100 minus real_100 | protected | 0 | N/A | N/A | N/A | N/A |
| LSTM+MAPPO: markov_100 minus repeat_100 | dwell | 0 | N/A | N/A | N/A | N/A |
| LSTM+MAPPO: markov_100 minus repeat_100 | depth | 0 | N/A | N/A | N/A | N/A |
| LSTM+MAPPO: markov_100 minus repeat_100 | protected | 0 | N/A | N/A | N/A | N/A |

## 7. Generalization and limitations

Held-out scenario: None: grouped variant holdout, not LOSO.
Use --held-out S1 ... S7 in separate output folders for optional scenario holdout. Single-fold or variant results must not be labeled seven-fold LOSO.
Singleton scenarios are training-only in the main split. Variant similarity remains and is reported above. Test-set size limits generalization claims.
The inherited vocabulary, payoff, goals and environment calibration were fixed using the earlier corpus. The new split isolates estimator/encoder/policy fitting, not historical environment design.
This source bundle contains a fixed five-zone coordinated-engagement simulator; it is not the earlier variable-topology v3 experiment.
No new raw telemetry or independent incidents are created by augmentation. Preserving the estimator does not establish the validity of every generated chain.
No full experiment was run during package construction. Only smoke/test outputs may be present until the lab run completes.

