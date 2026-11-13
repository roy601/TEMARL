# Decisions

Written 2026-11-13, after reading the paper in full and before any code, data request or run.

## Status: blocked, not reproducible as published

| # | gap | choice | why | decided on |
|---|---|---|---|---|
| 1 | Data for the published numbers | Every target (Tables 4 and 5, Figure 13) is computed on all 4,400 sequences (Table 3); 3,600 are the authors' own (Table 2) and not released. **No target is attempted until the authors release them.** | The 3,600 cannot be regenerated: the paper says they needed manual "supplements and corrections" to the technique lists, about 1,000 manual tactic additions to an ATT&CK-v3 Atomic Red Team checkout, and network environment files that are not published (Sec. 3.2). A model trained on the 800 public sequences alone would answer a different question from every table. | 2026-11-13 |
| 2 | Code | none released; a rebuild would need every setting in decision 4 | — | 2026-11-13 |
| 3 | The 800 public sequences | requested by the user through the APTGen page (institutional e-mail) | needed for any later replication | 2026-11-13 |

## Gaps to settle with the authors before any run (none decided yet)

4. Training settings: epochs, batch size, optimiser and learning rate, dropout value, embedding size, attention score function, teacher forcing, early stopping.
5. Windows: how scenarios are cut into input/output windows (stride, whether windows overlap), and whether the 0.8 / 0.2 split is by window or by scenario. The paper shuffles "the data" before splitting (Sec. 4.1); if that is by window, windows of the same scenario fall on both sides.
6. Accuracy: per predicted step, or the whole output sequence; with or without padding and end tokens.
7. Vocabulary: Table 3 says 74 techniques; Sec. 3.2 says the model outputs a 76-dimensional vector (perhaps 74 + `<GO>` + `<EOS>`, unconfirmed).
8. Figure 13: the bar values are read from the figure's labels in the order shown (overall shuffled 0.85, dataset 1 to 6: 0.58, 0.56, 0.72, 0.76, 0.74, 0.70); the overall value agrees with Table 4, id 6 (input 5, output 3, 0.85).

## Inconsistencies recorded

1. Vocabulary 74 (Table 3) vs a 76-dimensional output (Sec. 3.2), see 7.
2. "Data Availability: the data and data generation tool ... are all public", but 3,600 of the 4,400 sequences are not released, and the public 800 need an e-mail request.
3. Table 2 lists T1093, T1060 and T1076 twice for Patchwork.
