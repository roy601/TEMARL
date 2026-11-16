# Decisions

Written 2026-11-16, after reading the paper in full, before any code, data request or run.

## Status: blocked, not reproducible as published

| # | gap | choice | why | decided on |
|---|---|---|---|---|
| 1 | Data | **No target is attempted.** Every result (Table 3, Figs. 6-7) is computed on the authors' own dataset, built by crawling about 2,200 threat reports and running an ontology reasoner (Sec. 3). The dataset is released only by e-mail; its size (number of sequences, vocabulary), length distribution and split are not stated. | A dataset we rebuild from public reports would differ in every respect, so any result would answer a different question. | 2026-11-16 |
| 2 | Code | none released. A rebuild also needs the COASE ontology, the six SWRL rules (Sec. 3.3), a retrained rcATT model and the Extractor tool, none of which is released. | - | 2026-11-16 |
| 3 | Pre-registration | The 41 targets are recorded anyway, before any data or code, so that a later replication with the authors' data is bound to them. | STANDARD.md requirement 1 | 2026-11-16 |

## Gaps to settle with the authors before any run (none decided)

4. Model size: number of layers L, heads h (Fig. 5 uses h = 6, n_cw = 3 only as an example), window sizes cw_i, embedding size d, feed-forward size, dropout.
5. Training: learning rate and batch size (chosen by an unreported grid search), epochs, early-stopping patience, the weights of the "weighted cross entropy" (Algorithm 1) versus the unweighted loss in Eq. 11, Word2Vec settings (dimension, window, training corpus), and whether tactic and technique embeddings are concatenated or summed ("hierarchical embedding").
6. Task and windows: how each sequence is cut into inputs and targets, the minimum sequence length (at least 5 phases), padding, and the 8:1:1 split unit (sequence or attack report) and seed.
7. Metrics: the paper defines TN as "incorrect predictions in the negative sample" and FP as "correct predictions in the negative sample", which are not the standard definitions; whether precision, recall and F1 are macro, micro or weighted over classes is not stated; "computing the average prediction performance across all time steps" (Sec. 4.4) is not specified.
8. Baselines: it "replicates" GRU [17], a Bayesian network [12] and DeepAG [20]. The LSTM row in Table 3 is labelled [20] (DeepAG), which combines a Transformer and an LSTM; its configuration is not given.
9. Multi-step (Fig. 6) and missing-rate (Fig. 7) experiments: values are only in figures; the text gives eleven numbers (targets above). The number of random simulations per missing rate is not stated.
10. Number of runs, seeds, confidence intervals: none stated.

## Inconsistencies recorded

1. Sec. 4.4: "a 3.35% improvement compared to LSTM ... and a 5.9% improvement compared to GRU". From Table 3, (0.894 - 0.865) / 0.865 = 3.35% relative, but (0.894 - 0.835) / 0.835 = 7.07% relative; 5.9 is the absolute difference in points. The two percentages use different bases.
2. "COASE comprises seven top-level classes" (Sec. 3.3) but six are listed; Fig. 4 also shows Tool.
3. The classification metrics are defined with non-standard TN and FP wording (see 7).
4. Sec. 4.2 calls F1 "a combined evaluation metric of accuracy and recall"; F1 combines precision and recall (Eq. 15).
5. The title and abstract frame the work for IIoT, but the dataset is built from general APT reports with no IIoT-specific content.

## Check on the paper itself (no data needed)

F1 recomputed from the printed precision and recall (2PR/(P+R)) matches Table 3 for all five methods within 0.001: DeepOP 0.8933 (0.894), LSTM 0.8649 (0.865), GRU 0.8348 (0.835), Transformer 0.8609 (0.861), Bayesian 0.6134 (0.614). Table 3 is internally consistent.
