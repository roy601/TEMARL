# Transformer review

**Status: recommendation for approval. Nothing has been built or trained.**

## 1. Verdict

**Do not replace the Transformer outright. Improve it with published components, and test each one.**

The evidence does not show our Transformer is behind (old corpus, 10 seeds, W = 16, micro-F1):

| Contrast | Difference | Verdict |
|---|---|---|
| Transformer vs GRU | +0.008 | no clear difference |
| Transformer vs LSTM | +0.007 | no clear difference |
| Transformer vs order-free control | +0.034 | better |

So the professor's concern is valid in a different way. **The gaps are in design and evidence, not in a
measured loss.** Also, that study used a split full of near-copies, so its scores say little about novel
behaviour.

## 2. What our Transformer lacks (from the code)

| Current design (`encoders_cmd.py`, `train_cmd.py`) | Lack | Our data shows |
|---|---|---|
| Custom model, informed by FlowTransformer | No single published architecture to cite for this task | – |
| Ignores time | Timestamps exist now and are unused | Gaps from under 1 s to 461 s |
| No repeat handling | Treats repeated and new techniques alike | 47.2% of target labels repeat |
| Plain binary cross-entropy | No handling of label imbalance | 10 labels occur once |
| Loss on the last position only | Each window gives one target | About 464 training steps per fold (median) |
| About 67,000 trunk parameters | Large for the data | 72 to 774 training steps per fold |
| Never scored on novel points | Copying and predicting look the same | 53.8% of variant test points are copies |

## 3. Suitable options

| Rank | Option | What it adds | Why we need it | Difference from ours | Paper |
|---|---|---|---|---|---|
| 1 | **SASRec** | Causal self-attention, trained at every position | Well-known published base for next-step prediction | Loss at every position, not only the last | [Kang & McAuley, ICDM 2018](https://arxiv.org/abs/1808.09781) |
| 2 | **Repeat-explore head** | Separates "repeat" from "new" | 47.2% of target labels repeat | Adds a gated head; the trunk is unchanged | [RepeatNet, AAAI 2019](https://ojs.aaai.org/index.php/AAAI/article/view/4408); gate idea in [BasketFormer](https://cdn.amazon.science/db/e1/a5a526154cfdb5e29a0baaaa43c5/scipub-approval152129-48092713-basketformer-contrastive-masked-language-modeling-with-temporal-encoding-and-repeatexplore-gating-for-nextbasket-recommendation.pdf) (venue not stated in the PDF) |
| 3 | **TiSASRec** | Time gaps inside attention | Uses our new timestamps | Attention sees time intervals | [Li, Wang & McAuley, WSDM 2020](https://doi.org/10.1145/3336191.3371786) |
| 4 | **Asymmetric Loss** (a loss, not a model) | Reduces the pull of easy negatives | Few positives among 81 labels | Replaces plain BCE | [Ridnik et al., ICCV 2021](https://arxiv.org/abs/2009.14119) |
| 5 | **DNNTSP** (comparison arm) | Built for "sequence of sets", our exact task shape | Independent published benchmark | Graph plus attention, not a pure Transformer | [Yu et al., KDD 2020](https://arxiv.org/abs/2006.11483) |

Supporting evidence:

- [A Next Basket Recommendation Reality Check](https://arxiv.org/abs/2109.14233) (ACM TOIS 2023) finds that
  repeat items are much easier than new ones, so results must separate them.
- [FlowTransformer](https://arxiv.org/abs/2304.14746), a network-intrusion study already in our references,
  reports that the classification head had the largest impact. This supports starting with the head.

**Risk.** Time gaps here come from scripted runs, so TiSASRec may learn script timing rather than attacker
behaviour. It stays only if validation supports it.

## 4. Considered and not recommended

| Option | Reason |
|---|---|
| [BERT4Rec](https://doi.org/10.1145/3357384.3357895) (CIKM 2019) | Its original results could not be reproduced with default settings ([Petrov & Macdonald, RecSys 2022](https://arxiv.org/abs/2207.07483)). Too risky on this little data |
| [GTrXL](https://proceedings.mlr.press/v119/parisotto20a.html) (ICML 2020) | Fixes training instability in RL. Our encoder is frozen and receives no RL gradients |
| [Multi-Agent Transformer](https://arxiv.org/abs/2205.14953) (NeurIPS 2022) | Replaces MAPPO, not the encoder. It would change the framework itself |
| [Set Transformer](https://proceedings.mlr.press/v97/lee19d.html) (ICML 2019) | Only 201 of 904 steps have more than one label, and our set embedding already ignores label order. Low value |
| [DeepOP](https://doi.org/10.3390/electronics14020257) (Electronics 2025) | The only security-specific match found, but its full text was blocked, so **not assessed**. Please download the PDF manually |

## 5. What no Transformer can fix

- **Unseen labels.** On S6, recall cannot exceed 41.2%. A model cannot predict a label absent from training.
- **Few campaigns.** 34 runs from 7 scenarios.
- **Past gains are small.** Encoder differences so far are under 0.01, and seed noise is of similar size.

Expect modest gains. An honest small result is still a valid thesis finding.

## 6. Proposed plan

1. Finish the dataset work first (`camlds_real/DATASET_REPORT.md`).
2. Keep the current Transformer as the **baseline**, and keep the 64-D `h` output so MAPPO needs no change.
3. Add one component at a time: all-position training, then repeat head, time gaps, Asymmetric Loss.
4. Keep a component only if it improves **validation** results across 10 seeds. Never use test data to choose.
5. Judge on **novel points**, not only on the overall score.
6. Freeze the chosen design as a **new protocol version before any test result is opened**. The frozen
   protocol says "Transformer"; the new design must be declared, not swapped silently.

Citation details were checked against publisher or arXiv listings. Summaries come from abstracts and search
results, except BasketFormer's abstract, which was read directly. None of these methods has been tested on
our data yet.
