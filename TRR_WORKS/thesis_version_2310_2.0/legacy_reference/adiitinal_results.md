Based on the full lab run across **10 seeds**, the prediction comparison is:

| Rank | Model | Top-1 Accuracy | Top-3 Accuracy |
|---:|---|---:|---:|
| 1 | **Transformer** | **45.63% ± 1.54%** | **64.14% ± 1.48%** |
| 2 | **LSTM** | **45.32% ± 1.60%** | 63.53% ± 1.62% |
| 3 | **GRU** | **45.08% ± 1.52%** | 63.91% ± 1.42% |

Baselines:

- Bigram: **37.02% Top-1**
- Majority prediction: **5.65% Top-1**

**Conclusion:** The Transformer has the highest next-technique prediction accuracy, but its advantage is small: only **0.30 percentage points over LSTM** and **0.54 points over GRU**. Therefore, describe it as the **descriptive winner**, not yet as significantly better.

These are sequence encoders, not full LLMs. The results come from held-out validation episodes using identical training tasks and budgets.











