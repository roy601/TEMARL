# Window-length sensitivity

> **Scope.** Source-derived annotated playbook sequences from the AttackBed
> repository, evaluated in a simulator. NOT real-world attacker telemetry. The
> environment's engagement, movement and exposure rules are modelling
> assumptions, not measured quantities.
>
> **Representation.** Command-level and multi-label: one step is one annotated
> attacker command, and the techniques within a command are an unordered set.
> Within-command label order is discarded by construction, so the 34.9%
> label-order artefact of the earlier flattened corpus cannot be learned here.
>
> **Not comparable with the earlier study.** Its Top-1 scored one token out of
> a flattened stream; these targets are label SETS over command transitions.
> Its dwell counted label-steps; here dwell counts commands. Different units.
>
> **Sample size.** 36 playbooks from 7 scenarios. Seeds, environment repeats
> and prediction windows are not independent attack campaigns.


Every window predicts the SAME targets: short prefixes are padded, never discarded, so the comparison is paired. Equal update budgets equalise optimisation effort, not runtime.

| arm | window | test full-history % | micro-F1 | BCE |
|---|---:|---:|---|---|
| GRU | 8 | 34.4 | 0.8766 +/- 0.0072 | 0.01666 +/- 0.00114 |
| GRU | 16 | 68.7 | 0.8780 +/- 0.0127 | 0.01612 +/- 0.00188 |
| GRU | 32 | 98.8 | 0.8782 +/- 0.0102 | 0.01601 +/- 0.00128 |
| GRU | 64 | 100.0 | 0.8754 +/- 0.0109 | 0.01624 +/- 0.00129 |
| LSTM | 8 | 34.4 | 0.8743 +/- 0.0085 | 0.01680 +/- 0.00126 |
| LSTM | 16 | 68.7 | 0.8792 +/- 0.0081 | 0.01537 +/- 0.00087 |
| LSTM | 32 | 98.8 | 0.8780 +/- 0.0106 | 0.01549 +/- 0.00088 |
| LSTM | 64 | 100.0 | 0.8788 +/- 0.0111 | 0.01545 +/- 0.00095 |
| NoHistory | 16 | 68.7 | 0.1945 +/- 0.0000 | 0.17844 +/- 0.00062 |
| OrderFree | 8 | 34.4 | 0.8327 +/- 0.0088 | 0.02064 +/- 0.00157 |
| OrderFree | 16 | 68.7 | 0.8524 +/- 0.0126 | 0.01736 +/- 0.00171 |
| OrderFree | 32 | 98.8 | 0.8496 +/- 0.0055 | 0.01789 +/- 0.00166 |
| OrderFree | 64 | 100.0 | 0.8508 +/- 0.0165 | 0.01810 +/- 0.00178 |
| Transformer | 8 | 34.4 | 0.8887 +/- 0.0078 | 0.01442 +/- 0.00058 |
| Transformer | 16 | 68.7 | 0.8863 +/- 0.0126 | 0.01425 +/- 0.00097 |
| Transformer | 32 | 98.8 | 0.8889 +/- 0.0081 | 0.01428 +/- 0.00082 |
| Transformer | 64 | 100.0 | 0.8894 +/- 0.0111 | 0.01432 +/- 0.00086 |

## Paired contrasts vs the reference window (16)

| contrast | pairs | delta | 95% CI | p raw | p Holm | verdict |
|---|---:|---:|---|---:|---:|---|
| Transformer: W8 - W16 | 10 | +0.00233 | [-0.00668, +0.01135] | 0.57256 | 1.00000 | NO CLEAR DIFFERENCE |
| Transformer: W32 - W16 | 10 | +0.00254 | [-0.00777, +0.01284] | 0.59075 | 1.00000 | NO CLEAR DIFFERENCE |
| Transformer: W64 - W16 | 10 | +0.00308 | [-0.00725, +0.01341] | 0.51715 | 1.00000 | NO CLEAR DIFFERENCE |
| GRU: W8 - W16 | 10 | -0.00137 | [-0.01212, +0.00939] | 0.77998 | 1.00000 | NO CLEAR DIFFERENCE |
| GRU: W32 - W16 | 10 | +0.00024 | [-0.00719, +0.00768] | 0.94331 | 1.00000 | NO CLEAR DIFFERENCE |
| GRU: W64 - W16 | 10 | -0.00260 | [-0.01051, +0.00530] | 0.47501 | 1.00000 | NO CLEAR DIFFERENCE |
| LSTM: W8 - W16 | 10 | -0.00489 | [-0.01324, +0.00346] | 0.21772 | 1.00000 | NO CLEAR DIFFERENCE |
| LSTM: W32 - W16 | 10 | -0.00119 | [-0.00706, +0.00468] | 0.65784 | 1.00000 | NO CLEAR DIFFERENCE |
| LSTM: W64 - W16 | 10 | -0.00038 | [-0.00724, +0.00649] | 0.90420 | 1.00000 | NO CLEAR DIFFERENCE |
| OrderFree: W8 - W16 | 10 | -0.01972 | [-0.03066, -0.00878] | 0.00277 | 0.03328 | WORSE |
| OrderFree: W32 - W16 | 10 | -0.00284 | [-0.01124, +0.00555] | 0.46311 | 1.00000 | NO CLEAR DIFFERENCE |
| OrderFree: W64 - W16 | 10 | -0.00163 | [-0.01050, +0.00723] | 0.68652 | 1.00000 | NO CLEAR DIFFERENCE |

_Non-significance is NOT equivalence. An equivalence claim requires a predeclared margin and a TOST; absent that, report 'no clear difference detected'._

