# Rule for keeping a Transformer improvement

**Declared 2026-11-07, before any variant result exists. Validation data only. Implemented in
`compare_validation.py`.**

## The candidates, tested in this order

| # | Candidate | What changes | Paper |
|---|---|---|---|
| 1 | `allpos` | Causal attention, and the loss at every position, not only the last | SASRec (Kang & McAuley, ICDM 2018) |
| 2 | Repeat/new head | A gate that separates repeating a technique from predicting a new one | RepeatNet (AAAI 2019) |
| 3 | Asymmetric Loss | Replaces plain BCE | Ridnik et al. (ICCV 2021) |

Each candidate is compared with the **current design**: the baseline at first, then whatever has
been kept. `causal` (causal attention, last-position loss) is a **control** reported beside
candidate 1, to show whether a change comes from the mask or from the extra training signal. It
is not a candidate.

## The score

1. **Validation points** are split into **novel** and **copy** by the protocol 1.1 definition: a
   copy is a validation point whose window and target also occur in the fold's training runs.
2. Each training cell uses its own threshold, chosen on all its validation points, as always.
3. **Micro-F1 is pooled within 4 groups:** S1 variants, S3 variants, S6 variants, and the
   scenario-held-out folds. The groups are then averaged with **equal weight**. This stops S1 from
   dominating: 17 of its 18 folds validate on the same run.
4. Seeds are paired: seed *s* starts from the same weights for every variant.

## Keep the candidate only if all three hold

| # | Condition |
|---|---|
| 1 | **Novel points improve:** the score on novel validation points, averaged over the 10 seeds, is higher than the current design's |
| 2 | **Consistently:** it is higher in **at least 8 of the 10 seeds** |
| 3 | **No harm overall:** the score on all validation points does not fall by more than **0.01** |

Otherwise the current design stays.

**Also reported, but not part of the rule:** scores on copy points, micro-F1 on repeat and new
target labels, each group separately, and training length.

The kept design, and whether GRU/LSTM are run, are then frozen as **protocol 1.2** before any test
result is opened.
