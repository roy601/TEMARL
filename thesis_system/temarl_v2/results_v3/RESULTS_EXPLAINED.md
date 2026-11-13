# TEMARL v3 Results: Simple and Complex Environments

## 1. Scope of this report

This report explains the completed TEMARL v3 GPU experiment. It separates:

- **Simple environment:** Regime A, the original fixed 5-zone control topology.
- **Complex environment:** Regimes B, C, and D, which use changing topology layouts, firewall configurations, and network sizes.

All values are calculated from `entity_results_gpu.json`. Unless stated otherwise,
values are the mean across 10 independent seeds. Values shown as `mean +/- SD`
include the sample standard deviation across those seeds.

Important limitation: Regime A uses the original simple topology, but it evaluates
the new v3 EntityTransformer and DeepSets policies. It is not a rerun of every old
P2 baseline such as Static Honeypot or Single-Agent PPO.

## 2. Experiment validity

| Check | Result | Meaning |
|---|---:|---|
| Model combinations | 6 | 2 network encoders x 3 history encoders |
| Independent seeds | 10 | Seeds 0 through 9 |
| Completed training arms | 60/60 | Every model combination completed for every seed |
| History pretraining runs | 30/30 | Transformer, GRU, and SetEncoder for every seed |
| Training episodes | 600 per arm | Fixed by `prereg_v3.py` |
| Evaluation episodes | 200 per regime | Fixed by `prereg_v3.py` |
| Training topologies | 24 | Eight each at 5, 6, and 7 zones |
| Regime A topologies | 1 | Canonical fixed 5-zone control |
| Regime B topologies | 12 | New layouts at trained sizes |
| Regime C topologies | 12 | New structures with higher firewall density |
| Regime D topologies | 12 | Unseen 9, 11, and 13-zone networks |
| Environment gates | All passed | Includes exact equivalence with `env_v2` on the control |
| Entity tests | 26/26 passed | Entity observations and environment behavior validated |
| Total GPU runtime | 6,804.95 seconds | About 1 hour 53 minutes |

## 3. Models being compared

### Network encoders

| Encoder | What it does | Why it is included |
|---|---|---|
| EntityTransformer (ET) | Uses attention to model hosts, zones, services, and their relationships | Tests whether entity attention helps on changing networks |
| DeepSets (DS) | Encodes each entity and combines them without attention | Simpler baseline for testing whether attention is necessary |

### Attack-history encoders

| Encoder | What it does |
|---|---|
| Transformer (T) | Encodes the ordered MITRE ATT&CK technique history using attention |
| GRU (G) | Encodes the same history recurrently, one step at a time |
| SetEncoder (S) | Encodes observed techniques without using their order |

The labels `ET+T`, `DS+G`, and similar labels identify one network encoder plus one
attack-history encoder.

## 4. Evaluation environments

| Regime | Environment type | Description | Question answered |
|---|---|---|---|
| A | Simple control | Original 5-zone, 10-host topology reproduced from `env_v2` | Does v3 still work on the original environment? |
| B | Complex layout | New network layouts at familiar 5, 6, and 7-zone sizes | Can the policy handle unseen layouts of known sizes? |
| C | Complex structure | New 5, 6, and 7-zone layouts with firewall-block probability increased from 0.15 to 0.45 | Can it handle a different connectivity/security distribution? |
| D | Complex size | New 9, 11, and 13-zone networks never used during training | Can it generalize to larger networks? |

## 5. Meaning of the metrics

| Metric | Meaning | Direction |
|---|---|---|
| DSR | Deception Success Rate: fraction of evaluation episodes in which the defender succeeds | Higher is better |
| Capture Rate | Fraction of episodes in which the attacker is captured | Higher is better |
| Alignment Score | Semantic fit between the current attacker technique and the selected deception action | Higher is better |
| Episode Return | Total reward received by the RL defender during an episode | Higher is better |
| Engagement Length | Number of time steps for which the attacker remains engaged | Context dependent; longer is not always better |
| Pretraining Top-1 | Fraction of times the history encoder's first prediction is the correct next ATT&CK technique | Higher is better for prediction |
| B-D gap | DSR on new familiar-sized layouts minus DSR on unseen sizes | Lower is better for size generalization |
| Cohen's d | Paired standardized effect size; sign shows the direction of the declared contrast | Positive supports the hypothesis |
| Holm p-value | p-value corrected across the seven pre-registered comparisons | Significant only when below 0.05 |

In this result file, Capture Rate equals DSR in all 60 rows. They are therefore the
same observed outcome and should not be presented as two independent findings.

## 6. Simple environment results: Regime A

### 6.1 All Regime A metrics

| Model | DSR / Capture Rate | Alignment | Episode Return | Engagement Length |
|---|---:|---:|---:|---:|
| ET + Transformer | 0.4685 +/- 0.0475 | 0.3495 +/- 0.0570 | 1.1289 +/- 0.1987 | 5.4480 +/- 0.2210 |
| ET + GRU | 0.4575 +/- 0.0724 | 0.3482 +/- 0.1070 | 1.1393 +/- 0.4253 | 5.5125 +/- 0.3113 |
| ET + SetEncoder | 0.4415 +/- 0.0483 | 0.3246 +/- 0.0602 | 1.0691 +/- 0.2057 | **5.5510 +/- 0.2619** |
| **DS + Transformer** | **0.4845 +/- 0.0545** | **0.3894 +/- 0.0514** | **1.2817 +/- 0.2315** | 5.4200 +/- 0.2476 |
| DS + GRU | 0.4625 +/- 0.0337 | 0.3522 +/- 0.0102 | 1.1653 +/- 0.0567 | 5.4980 +/- 0.2053 |
| DS + SetEncoder | 0.4590 +/- 0.0465 | 0.3544 +/- 0.0135 | 1.1680 +/- 0.0581 | 5.4940 +/- 0.2397 |

### 6.2 Meaning of the simple-environment result

- DeepSets + Transformer has the highest raw DSR, Alignment Score, and Episode Return.
- EntityTransformer does not show a visible advantage on the original fixed topology.
- Engagement Length selects a different model and does not agree with the success metrics. It should remain a secondary metric.
- This result confirms compatibility with the simple environment, not superiority over all original P2 baselines.

## 7. Complex environment results

### 7.1 Deception Success Rate

| Model | B: new layouts | C: new firewall structure | D: unseen sizes |
|---|---:|---:|---:|
| ET + Transformer | 0.4450 +/- 0.0464 | 0.4540 +/- 0.0472 | 0.3795 +/- 0.0502 |
| ET + GRU | 0.4335 +/- 0.0629 | 0.4315 +/- 0.0617 | 0.3680 +/- 0.0385 |
| ET + SetEncoder | 0.4245 +/- 0.0486 | 0.4230 +/- 0.0461 | 0.3650 +/- 0.0442 |
| **DS + Transformer** | **0.4595 +/- 0.0545** | **0.4555 +/- 0.0592** | **0.3830 +/- 0.0522** |
| DS + GRU | 0.4390 +/- 0.0280 | 0.4450 +/- 0.0276 | 0.3710 +/- 0.0301 |
| DS + SetEncoder | 0.4400 +/- 0.0450 | 0.4410 +/- 0.0425 | 0.3635 +/- 0.0387 |

**Meaning:** DeepSets + Transformer has the highest raw mean DSR in B, C, and D.
All models lose performance on larger unseen networks. The statistical tests do not
show a significant advantage for any declared architecture comparison.

### 7.2 Alignment Score

| Model | B: new layouts | C: new firewall structure | D: unseen sizes |
|---|---:|---:|---:|
| ET + Transformer | 0.2911 +/- 0.0523 | 0.2926 +/- 0.0518 | 0.1554 +/- 0.0361 |
| ET + GRU | 0.2873 +/- 0.0900 | 0.2901 +/- 0.0901 | 0.1486 +/- 0.0509 |
| ET + SetEncoder | 0.2737 +/- 0.0493 | 0.2691 +/- 0.0487 | 0.1509 +/- 0.0279 |
| **DS + Transformer** | **0.3279 +/- 0.0467** | **0.3261 +/- 0.0471** | **0.1677 +/- 0.0313** |
| DS + GRU | 0.2941 +/- 0.0109 | 0.2931 +/- 0.0104 | 0.1578 +/- 0.0231 |
| DS + SetEncoder | 0.2965 +/- 0.0142 | 0.2981 +/- 0.0161 | 0.1521 +/- 0.0129 |

**Meaning:** Semantic action-to-technique alignment drops sharply on unseen network
sizes. DeepSets + Transformer has the highest descriptive mean, but Alignment Score
was not the pre-registered primary metric for v3, so these comparisons are secondary.

### 7.3 Episode Return

| Model | B: new layouts | C: new firewall structure | D: unseen sizes |
|---|---:|---:|---:|
| ET + Transformer | 0.9043 +/- 0.1766 | 0.9154 +/- 0.1865 | 0.3901 +/- 0.1530 |
| ET + GRU | 0.9041 +/- 0.3606 | 0.9175 +/- 0.3624 | 0.3716 +/- 0.2210 |
| ET + SetEncoder | 0.8625 +/- 0.1722 | 0.8431 +/- 0.1746 | 0.3720 +/- 0.1317 |
| **DS + Transformer** | **1.0503 +/- 0.2070** | **1.0444 +/- 0.2044** | **0.4445 +/- 0.1438** |
| DS + GRU | 0.9452 +/- 0.0343 | 0.9374 +/- 0.0481 | 0.3968 +/- 0.0900 |
| DS + SetEncoder | 0.9453 +/- 0.0425 | 0.9510 +/- 0.0423 | 0.3759 +/- 0.0519 |

**Meaning:** Total defensive reward follows the same broad pattern as DSR and
Alignment Score. The largest decline occurs on unseen network sizes.

### 7.4 Engagement Length

| Model | B: new layouts | C: new firewall structure | D: unseen sizes |
|---|---:|---:|---:|
| ET + Transformer | 5.5470 +/- 0.2549 | 5.5400 +/- 0.2285 | 5.7865 +/- 0.2237 |
| ET + GRU | 5.6145 +/- 0.2744 | **5.6330 +/- 0.2782** | **5.8365 +/- 0.2348** |
| ET + SetEncoder | **5.6235 +/- 0.2547** | 5.6305 +/- 0.2533 | 5.8115 +/- 0.2269 |
| DS + Transformer | 5.5185 +/- 0.2642 | 5.5245 +/- 0.2662 | 5.7590 +/- 0.2597 |
| DS + GRU | 5.5965 +/- 0.2049 | 5.5795 +/- 0.1965 | 5.8190 +/- 0.1966 |
| DS + SetEncoder | 5.5720 +/- 0.2592 | 5.5780 +/- 0.2436 | 5.8285 +/- 0.2142 |

**Meaning:** Engagement becomes longer on larger networks even while DSR,
Alignment, and Return become worse. Larger networks create longer paths, so
Engagement Length alone must not be interpreted as better deception.

## 8. Prediction versus deception

| History encoder | Pretraining Top-1 | Regime-B DSR averaged across network encoders |
|---|---:|---:|
| Transformer | 0.3611 +/- 0.0092 | **0.4523** |
| GRU | **0.5577 +/- 0.0128** | 0.4363 |
| SetEncoder | 0.5105 +/- 0.0142 | 0.4323 |

**Meaning:** GRU predicts the exact next attacker technique much better than the
Transformer, but this does not produce better deception. Across the 60 runs, the
reported association is `r = -0.175, p = 0.18`, which is not statistically
significant. The correct conclusion is that this experiment found no reliable
relationship between next-technique accuracy and deception success.

## 9. Generalization and efficiency

| Model | B DSR | D DSR | B-D gap | Parameters | Mean training time |
|---|---:|---:|---:|---:|---:|
| ET + Transformer | 0.4450 | 0.3795 | 0.0655 | 110,984 | 127.30 s |
| ET + GRU | 0.4335 | 0.3680 | 0.0655 | 110,984 | 123.98 s |
| ET + SetEncoder | 0.4245 | 0.3650 | **0.0595** | 110,984 | 122.26 s |
| DS + Transformer | **0.4595** | **0.3830** | 0.0765 | 116,943 | 70.35 s |
| DS + GRU | 0.4390 | 0.3710 | 0.0680 | 116,943 | 67.16 s |
| DS + SetEncoder | 0.4400 | 0.3635 | 0.0765 | 116,943 | **65.02 s** |

**Meaning:** All models generalize to new layouts and firewall structures better
than they generalize to unseen network sizes. No architecture has a statistically
established size-generalization advantage. Averaged across history encoders,
DeepSets trains in 67.51 seconds versus 124.52 seconds for EntityTransformer,
making DeepSets approximately 1.84 times faster.

## 10. Pre-registered hypothesis tests

The v3 primary metric is DSR. The difference is always `first named model minus
comparison model`, so a negative value points against the hypothesis.

| Hypothesis contrast | Regime | DSR difference | Cohen's d | Raw p | Holm p | Decision |
|---|---:|---:|---:|---:|---:|---|
| H6: ET vs DS, Transformer history | B | -0.0145 | -0.37 | 0.2761 | 1.000 | Not supported |
| H6: ET vs DS, GRU history | B | -0.0055 | -0.10 | 0.7569 | 1.000 | Not supported |
| H6: ET vs DS, Set history | B | -0.0155 | -0.39 | 0.2511 | 1.000 | Not supported |
| H7: ET vs DS, GRU history | C | -0.0135 | -0.28 | 0.3949 | 1.000 | Not supported |
| H7: ET vs DS, GRU history | D | -0.0030 | -0.11 | 0.7284 | 1.000 | Not supported |
| H8: GRU vs Transformer history, ET network | B | -0.0115 | -0.18 | 0.5736 | 1.000 | Not supported |
| H8: GRU vs Transformer history, ET network | D | -0.0115 | -0.34 | 0.3170 | 1.000 | Not supported |

### Hypothesis decisions

| Hypothesis | Expected result | Actual decision |
|---|---|---|
| H6 | EntityTransformer beats DeepSets on new layouts of trained sizes | **Not supported** |
| H7 | EntityTransformer beats DeepSets on unseen structures and sizes | **Not supported** |
| H8 | GRU history encoder matches or beats Transformer under variable topology | **Not supported** |

All seven declared differences point against their respective hypotheses. None is
statistically significant after Holm-Bonferroni correction. With only 10 paired
seeds, small effects cannot be excluded solely from the p-values, so the report
should state both the direction and the uncertainty.

## 11. Decisive findings

1. The simple and complex environment experiment completed correctly and passed all validation gates.
2. DeepSets + Transformer has the best raw DSR, Alignment Score, and Episode Return in A, B, C, and D.
3. EntityTransformer does not significantly outperform the simpler DeepSets encoder.
4. DeepSets trains approximately 1.84 times faster than EntityTransformer.
5. All models handle new layouts and firewall changes better than completely unseen network sizes.
6. The DSR loss from B to D is approximately 0.060 to 0.077 for every model.
7. GRU has the best next-technique Top-1 accuracy, but it does not produce the best deception result.
8. Better intent prediction is not demonstrated to cause better defensive decisions.
9. The Transformer superiority claim is not supported by v3.
10. The defensible contribution is the validated variable-topology environment, source-grounded deception design, pre-registered factorial evaluation, and its negative architectural result.

## 12. Results not provided by this v3 run

The following P2-style results are not contained in `entity_results_gpu.json`:

- Interaction Depth.
- Top-3 next-technique accuracy.
- Perplexity.
- Per-action honeypot usage counts.
- Deception cost.
- Critical-host compromise rate.
- Fog-of-war evaluation for the v3 policies.
- Static Honeypot, Random Policy, Single-Agent PPO, and original v2 policy baselines under the v3 topology protocol.

These must not be claimed as v3 results. Some can be evaluated from saved
checkpoints without repeating full training; metrics that require missing
episode-level traces need a new checkpoint evaluation run.

## 13. Source files

- Raw completed GPU results: `entity_results_gpu.json`
- Pre-registered statistical analysis: `entity_analysis_gpu.json`
- Complete training log: `train_gpu.log`
- Environment validation: `gates.json`

