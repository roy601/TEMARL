# CasinoLimit — Prediction Run 1

Final test results opened on **13 November 2026**, under protocol CL 1.0.

Sources: [complete test report](casinolimit_encoder/out_test/CL_RESULTS.txt), [protocol](casinolimit_encoder/PROTOCOL_CL_1.0.md), [per-attacker results](casinolimit_encoder/out_test/CL_RESULTS_PER_ATTACKER.csv).

These are prediction results only. This run does not evaluate MARL, honeypot dwell, interaction depth or asset protection.

## Experiment and metric definitions

| Item | Setting |
|---|---|
| Dataset | CasinoLimit |
| Output vocabulary | 66 technique labels |
| Evaluation | Five folds; separate training, validation and test attackers |
| Neural runs | Ten seeds per model, fold and condition; 400 trainings including the old Transformer |
| Main test | 8,087 prediction points from 113 attackers with evaluable points |
| Primary comparison unit | Per-attacker micro-F1, averaged over seeds and then attackers |
| Main condition | Original command sequences |
| Sensitivity condition | `collapse_repeats`: repeated commands collapsed under the protocol's masked-command rule |
| Model selection | Validation-selected checkpoint and threshold |
| Simple comparator | Best simple rule selected separately for each fold using validation |

All F1 and accuracy values below are **percentages**. BCE is a loss, not a percentage; lower is better. Tables reproduce the source's three-decimal precision after conversion. No standard deviations are invented.

| Metric/subset | Meaning |
|---|---|
| Pooled micro-F1 | Combines label decisions across test points, then averages over seeds; longer attacker sequences contribute more |
| Per-attacker micro-F1 | Each attacker receives equal weight; used for paired statistical comparisons |
| Macro-F1 | Averages label-level F1; exposes performance across the label vocabulary |
| Exact-set accuracy | The entire predicted technique set must match the target set |
| Novel | Exact history-window plus target combination does not occur in training or validation; does not mean an entirely new campaign |
| Copy | Exact history-window plus target combination occurs in training or validation |
| Reviewed | Every target label was reviewer-assigned, with no automatic or doubtful target labels |

## Table 1 — Main results: all 8,087 test points

| Model | Pooled micro-F1 % | Per-attacker micro-F1 % | Macro-F1 % | Exact-set accuracy % | BCE |
|---|---:|---:|---:|---:|---:|
| Transformer (allpos) | 32.8 | 28.7 | 5.9 | 18.8 | 0.061 |
| GRU | 33.7 | 28.7 | 5.3 | 20.2 | 0.061 |
| LSTM | 33.3 | 28.5 | 5.3 | 20.0 | 0.061 |
| Old Transformer — descriptive | 33.0 | 29.4 | 6.4 | 19.5 | 0.060 |
| Validation-selected simple baseline | 28.1 | 26.8 | 10.6 | 24.8 | — |
| Lookup: longest match | 22.3 | 20.4 | 5.8 | 19.9 | — |
| Lookup: previous step | 27.5 | 25.6 | 6.7 | 24.5 | — |
| Repeat last step | 29.5 | 28.4 | 16.3 | 26.0 | — |

**Explanation:** GRU has the highest pooled micro-F1. The three current neural models are close. Repeat-last has higher macro-F1 and exact-set accuracy than the neural models. Thus the neural models do not dominate across metrics.

## Table 2 — Primary statistical comparisons

Differences are in **percentage points of per-attacker micro-F1**, not differences between pooled micro-F1 columns. Differences use unrounded underlying scores.

| Comparison | Mean difference | 95% confidence interval | Holm-adjusted p | Protocol verdict |
|---|---:|---|---:|---|
| Transformer − selected simple baseline | +1.8 | −0.6 to +3.6 | <0.0001 | No difference established |
| GRU − selected simple baseline | +1.9 | −0.6 to +3.8 | 0.0001 | No difference established |
| LSTM − selected simple baseline | +1.6 | −0.8 to +3.5 | 0.0002 | No difference established |
| Transformer − GRU | −0.1 | −0.8 to +0.7 | 0.7774 | No difference established |
| Transformer − LSTM | +0.2 | −0.6 to +0.9 | 0.7774 | No difference established |

**Explanation:** The declared rule requires both a confidence interval excluding zero and a corrected p-value below 0.05. The mean-difference intervals include zero here. Small Wilcoxon p-values alone do not satisfy that rule; Wilcoxon and the bootstrap mean interval summarize differences differently. “No difference established” does not prove equivalence.

## Table 3 — Main condition: novel points (7,919)

| Model | Pooled micro-F1 % | Per-attacker micro-F1 % | Macro-F1 % | Exact-set accuracy % | BCE |
|---|---:|---:|---:|---:|---:|
| Transformer | 32.7 | 29.9 | 5.9 | 18.7 | 0.061 |
| GRU | 33.7 | 30.0 | 5.3 | 20.3 | 0.061 |
| LSTM | 33.3 | 29.7 | 5.3 | 20.1 | 0.061 |
| Old Transformer | 33.0 | 30.7 | 6.3 | 19.4 | 0.061 |
| Selected simple baseline | 28.0 | 26.8 | 10.6 | 24.8 | — |
| Lookup: longest match | 22.3 | 20.8 | 5.8 | 19.9 | — |
| Lookup: previous step | 27.5 | 27.1 | 6.6 | 24.6 | — |
| Repeat last step | 29.4 | 27.9 | 16.2 | 25.9 | — |

| Comparison against selected baseline | Per-attacker gain | 95% confidence interval | Holm p | Verdict |
|---|---:|---|---:|---|
| Transformer | +3.1 points | +1.7 to +4.5 | <0.0001 | Outperforms baseline |
| GRU | +3.2 points | +1.6 to +4.8 | <0.0001 | Outperforms baseline |
| LSTM | +2.9 points | +1.3 to +4.6 | 0.0001 | Outperforms baseline |

**Explanation:** All three neural encoders beat the selected baseline on this secondary subset under the reported rule. Transformer versus GRU/LSTM remains inconclusive. This subset result does not replace the primary all-points conclusion, and it is not a comparison against every individual simple rule.

## Table 4 — Main condition: copy points (168)

| Model | Pooled micro-F1 % | Per-attacker micro-F1 % | Macro-F1 % | Exact-set accuracy % | BCE |
|---|---:|---:|---:|---:|---:|
| Transformer | 35.1 | 17.9 | 18.3 | 24.8 | 0.053 |
| GRU | 32.5 | 12.4 | 17.0 | 15.7 | 0.053 |
| LSTM | 32.3 | 12.6 | 17.1 | 15.8 | 0.053 |
| Old Transformer | 34.7 | 18.1 | 19.2 | 22.1 | 0.052 |
| Selected simple baseline | 31.1 | 18.3 | 20.6 | 26.2 | — |
| Lookup: longest match | 23.8 | 13.9 | 16.1 | 19.6 | — |
| Lookup: previous step | 28.0 | 14.2 | 19.1 | 22.6 | — |
| Repeat last step | 34.0 | 21.3 | 22.2 | 29.8 | — |

**Explanation:** Transformer exceeds GRU and LSTM on per-attacker F1 in this small secondary subset, but has no established advantage over the selected baseline. Only 168 points contribute; avoid treating this as the overall finding.

## Table 5 — Main condition: reviewed targets (3,746)

| Model | Pooled micro-F1 % | Per-attacker micro-F1 % | Macro-F1 % | Exact-set accuracy % | BCE |
|---|---:|---:|---:|---:|---:|
| Transformer | 26.1 | 23.6 | 4.9 | 15.4 | 0.064 |
| GRU | 25.4 | 22.4 | 4.2 | 15.8 | 0.064 |
| LSTM | 25.1 | 22.2 | 4.2 | 15.5 | 0.064 |
| Old Transformer | 26.5 | 24.1 | 5.2 | 16.5 | 0.064 |
| Selected simple baseline | 25.1 | 23.6 | 10.5 | 23.8 | — |
| Lookup: longest match | 18.0 | 17.6 | 5.1 | 17.1 | — |
| Lookup: previous step | 22.4 | 21.4 | 5.8 | 21.5 | — |
| Repeat last step | 27.2 | 25.4 | 14.6 | 25.8 | — |

**Explanation:** Transformer exceeds GRU/LSTM on this subset, but none of the neural models demonstrates superiority over the selected simple baseline. Restricting to reviewed targets also changes the evaluated examples, so the score drop alone does not establish annotation errors as its cause.

## Table 6 — Collapsed-repeat sensitivity: all points (4,876)

| Model | Pooled micro-F1 % | Per-attacker micro-F1 % | Macro-F1 % | Exact-set accuracy % | BCE |
|---|---:|---:|---:|---:|---:|
| Transformer | 33.5 | 28.5 | 5.4 | 21.3 | 0.062 |
| GRU | 32.6 | 27.4 | 4.6 | 19.8 | 0.063 |
| LSTM | 32.8 | 27.6 | 4.3 | 20.4 | 0.063 |
| Old Transformer | 33.9 | 28.5 | 5.4 | 21.5 | 0.062 |
| Selected simple baseline | 34.2 | 29.5 | 14.6 | 29.8 | — |
| Lookup: longest match | 24.1 | 22.0 | 6.3 | 20.0 | — |
| Lookup: previous step | 33.2 | 28.5 | 8.7 | 29.0 | — |
| Repeat last step | 34.1 | 30.0 | 18.1 | 29.7 | — |

**Explanation:** Collapsing repeated commands changes both training and evaluation sequences. Transformer exceeds GRU/LSTM under the reported per-attacker tests, but no neural model establishes an advantage over the selected baseline.

## Table 7 — Collapsed-repeat sensitivity: novel points (4,724)

| Model | Pooled micro-F1 % | Per-attacker micro-F1 % | Macro-F1 % | Exact-set accuracy % | BCE |
|---|---:|---:|---:|---:|---:|
| Transformer | 33.7 | 29.9 | 5.2 | 21.4 | 0.062 |
| GRU | 32.7 | 28.6 | 4.4 | 20.0 | 0.063 |
| LSTM | 33.0 | 28.9 | 4.2 | 20.6 | 0.063 |
| Old Transformer | 34.1 | 30.2 | 5.2 | 21.5 | 0.062 |
| Selected simple baseline | 34.4 | 29.9 | 14.7 | 29.9 | — |
| Lookup: longest match | 23.9 | 22.1 | 6.1 | 19.8 | — |
| Lookup: previous step | 33.3 | 30.3 | 8.6 | 29.1 | — |
| Repeat last step | 34.3 | 29.9 | 18.2 | 29.7 | — |

**Explanation:** The neural advantage over the selected baseline observed on main-condition novel points is not established after repeats are collapsed. Transformer remains ahead of GRU/LSTM in this secondary analysis.

## Table 8 — Collapsed-repeat sensitivity: copy points (152)

| Model | Pooled micro-F1 % | Per-attacker micro-F1 % | Macro-F1 % | Exact-set accuracy % | BCE |
|---|---:|---:|---:|---:|---:|
| Transformer | 28.3 | 15.4 | 19.6 | 19.0 | 0.056 |
| GRU | 26.4 | 13.9 | 17.7 | 13.6 | 0.055 |
| LSTM | 25.0 | 12.8 | 17.3 | 14.1 | 0.056 |
| Old Transformer | 26.9 | 15.6 | 18.2 | 19.3 | 0.054 |
| Selected simple baseline | 26.9 | 20.2 | 17.7 | 25.7 | — |
| Lookup: longest match | 30.6 | 21.4 | 22.4 | 27.6 | — |
| Lookup: previous step | 27.9 | 20.0 | 18.2 | 26.3 | — |
| Repeat last step | 28.0 | 21.3 | 20.6 | 27.0 | — |

**Explanation:** No neural model establishes superiority over the selected baseline. Transformer exceeds LSTM, while its difference from GRU is inconclusive under the declared rule.

## Table 9 — Collapsed-repeat sensitivity: reviewed targets (2,814)

| Model | Pooled micro-F1 % | Per-attacker micro-F1 % | Macro-F1 % | Exact-set accuracy % | BCE |
|---|---:|---:|---:|---:|---:|
| Transformer | 26.2 | 22.7 | 4.2 | 18.0 | 0.063 |
| GRU | 25.0 | 22.0 | 3.5 | 16.6 | 0.063 |
| LSTM | 25.1 | 21.7 | 3.3 | 17.0 | 0.064 |
| Old Transformer | 26.3 | 22.7 | 4.1 | 18.4 | 0.063 |
| Selected simple baseline | 29.0 | 25.6 | 13.4 | 27.9 | — |
| Lookup: longest match | 19.1 | 18.4 | 5.3 | 18.2 | — |
| Lookup: previous step | 26.5 | 24.1 | 7.2 | 25.7 | — |
| Repeat last step | 29.3 | 26.0 | 16.3 | 27.8 | — |

| Neural model − selected baseline | Mean difference | 95% confidence interval | Holm p |
|---|---:|---|---:|
| Transformer | −2.9 points | −5.3 to −0.8 | 0.0319 |
| GRU | −3.6 points | −6.1 to −1.5 | 0.0080 |
| LSTM | −3.8 points | −6.6 to −1.6 | 0.0080 |

**Explanation:** The selected simple baseline outperforms all three neural encoders on this secondary subset under the reported rule. This result must be included alongside the more favorable novel-point result.

## Table 10 — What “best simple baseline” means

| Fold | Main condition | Collapsed repeats |
|---|---|---|
| F1 | Repeat last step | Repeat last step |
| F2 | Repeat last step | Repeat last step |
| F3 | Previous-step lookup | Previous-step lookup |
| F4 | Previous-step lookup | Previous-step lookup |
| F5 | Previous-step lookup | Repeat last step |

**Explanation:** “Best” means selected on validation, not whichever scores highest on the test. Therefore repeat-last can have a higher overall test score than the fixed selected comparator. The comparator must not be changed after seeing test results.

## Findings to present

1. On the primary all-points comparison, no neural encoder demonstrates superiority over the validation-selected simple baseline under the declared joint CI/p-value rule.
2. Transformer, GRU and LSTM show no established difference on the primary comparison. This is not proof of equivalence.
3. On main-condition novel points, all three outperform the selected baseline; this is a secondary result.
4. Simple rules achieve higher macro-F1 and exact-set accuracy. High pooled performance does not imply broad performance across technique classes.
5. The neural advantage is sensitive to the evaluated subset and repetition handling. On collapsed, reviewed points, the selected simple baseline wins.
6. CasinoLimit represents a different task distribution from CAM-LDS. Differences in labels, participants, annotation and splits prevent attributing their absolute score gap solely to the choice of dataset or architecture.

The source report includes additional paired tests for each subset. See [CL_RESULTS.txt](casinolimit_encoder/out_test/CL_RESULTS.txt) for every confidence interval and corrected p-value. Rounded `0.0000` p-values are displayed here as `<0.0001`, never as a probability exactly equal to zero.
