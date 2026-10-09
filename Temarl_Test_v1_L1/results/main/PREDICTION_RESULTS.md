# Prediction results

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


Primary metric: **micro_f1** on the held-out test split, at the validation-selected threshold, from the validation-best checkpoint. The final checkpoint is reported as secondary.

`precision@1` is the nearest relative of the earlier study's Top-1, and is still a different measurement. Do not tabulate them together.

## Main table (mean +/- SD across seeds)

| arm | window | sampler | seeds | micro-F1 | macro-F1 | exact-set | p@1 | r@3 | BCE |
|---|---:|---|---:|---|---|---|---|---|---|
| GRU | 8 | ordinary | 10 | 0.8766 +/- 0.0072 | 0.7900 +/- 0.0209 | 0.8196 +/- 0.0101 | 0.8896 +/- 0.0096 | 0.8847 +/- 0.0078 | 0.01666 +/- 0.00114 |
| GRU | 16 | ordinary | 10 | 0.8780 +/- 0.0127 | 0.8065 +/- 0.0309 | 0.8202 +/- 0.0224 | 0.9043 +/- 0.0148 | 0.8973 +/- 0.0095 | 0.01612 +/- 0.00188 |
| GRU | 16 | overlap | 10 | 0.8836 +/- 0.0065 | 0.8169 +/- 0.0226 | 0.8270 +/- 0.0150 | 0.8963 +/- 0.0117 | 0.8922 +/- 0.0071 | 0.01642 +/- 0.00123 |
| GRU | 32 | ordinary | 10 | 0.8782 +/- 0.0102 | 0.8012 +/- 0.0167 | 0.8172 +/- 0.0141 | 0.8933 +/- 0.0145 | 0.8959 +/- 0.0134 | 0.01601 +/- 0.00128 |
| GRU | 64 | ordinary | 10 | 0.8754 +/- 0.0109 | 0.8049 +/- 0.0180 | 0.8123 +/- 0.0136 | 0.8945 +/- 0.0091 | 0.8927 +/- 0.0118 | 0.01624 +/- 0.00129 |
| LSTM | 8 | ordinary | 10 | 0.8743 +/- 0.0085 | 0.7793 +/- 0.0158 | 0.8135 +/- 0.0072 | 0.8853 +/- 0.0071 | 0.8860 +/- 0.0090 | 0.01680 +/- 0.00126 |
| LSTM | 16 | ordinary | 10 | 0.8792 +/- 0.0081 | 0.8003 +/- 0.0141 | 0.8215 +/- 0.0089 | 0.8951 +/- 0.0117 | 0.8987 +/- 0.0083 | 0.01537 +/- 0.00087 |
| LSTM | 16 | overlap | 10 | 0.8794 +/- 0.0137 | 0.8026 +/- 0.0162 | 0.8264 +/- 0.0108 | 0.8945 +/- 0.0107 | 0.8998 +/- 0.0115 | 0.01586 +/- 0.00137 |
| LSTM | 32 | ordinary | 10 | 0.8780 +/- 0.0106 | 0.8011 +/- 0.0184 | 0.8215 +/- 0.0117 | 0.8926 +/- 0.0139 | 0.8967 +/- 0.0073 | 0.01549 +/- 0.00088 |
| LSTM | 64 | ordinary | 10 | 0.8788 +/- 0.0111 | 0.8026 +/- 0.0200 | 0.8221 +/- 0.0104 | 0.8945 +/- 0.0163 | 0.8953 +/- 0.0065 | 0.01545 +/- 0.00095 |
| NoHistory | 16 | ordinary | 10 | 0.1945 +/- 0.0000 | 0.0080 +/- 0.0000 | 0.1902 +/- 0.0000 | 0.2393 +/- 0.0000 | 0.3596 +/- 0.0186 | 0.17844 +/- 0.00062 |
| OrderFree | 8 | ordinary | 10 | 0.8327 +/- 0.0088 | 0.6814 +/- 0.0195 | 0.7344 +/- 0.0082 | 0.8172 +/- 0.0141 | 0.8623 +/- 0.0195 | 0.02064 +/- 0.00157 |
| OrderFree | 16 | ordinary | 10 | 0.8524 +/- 0.0126 | 0.7230 +/- 0.0492 | 0.7632 +/- 0.0292 | 0.8693 +/- 0.0247 | 0.8908 +/- 0.0176 | 0.01736 +/- 0.00171 |
| OrderFree | 32 | ordinary | 10 | 0.8496 +/- 0.0055 | 0.7324 +/- 0.0280 | 0.7650 +/- 0.0100 | 0.8675 +/- 0.0203 | 0.8889 +/- 0.0178 | 0.01789 +/- 0.00166 |
| OrderFree | 64 | ordinary | 10 | 0.8508 +/- 0.0165 | 0.7196 +/- 0.0335 | 0.7669 +/- 0.0237 | 0.8626 +/- 0.0169 | 0.8865 +/- 0.0208 | 0.01810 +/- 0.00178 |
| Transformer | 8 | ordinary | 10 | 0.8887 +/- 0.0078 | 0.8402 +/- 0.0159 | 0.8387 +/- 0.0108 | 0.8969 +/- 0.0103 | 0.9055 +/- 0.0060 | 0.01442 +/- 0.00058 |
| Transformer | 16 | ordinary | 10 | 0.8863 +/- 0.0126 | 0.8490 +/- 0.0170 | 0.8472 +/- 0.0084 | 0.9067 +/- 0.0103 | 0.9121 +/- 0.0070 | 0.01425 +/- 0.00097 |
| Transformer | 16 | overlap | 10 | 0.8768 +/- 0.0101 | 0.8377 +/- 0.0264 | 0.8472 +/- 0.0106 | 0.9080 +/- 0.0077 | 0.9061 +/- 0.0070 | 0.01455 +/- 0.00078 |
| Transformer | 32 | ordinary | 10 | 0.8889 +/- 0.0081 | 0.8512 +/- 0.0157 | 0.8485 +/- 0.0133 | 0.9043 +/- 0.0088 | 0.9097 +/- 0.0066 | 0.01428 +/- 0.00082 |
| Transformer | 64 | ordinary | 10 | 0.8894 +/- 0.0111 | 0.8506 +/- 0.0183 | 0.8448 +/- 0.0142 | 0.9031 +/- 0.0081 | 0.9113 +/- 0.0041 | 0.01432 +/- 0.00086 |

## Equal-weight views

Pooled metrics weight long runs more heavily (one window per command). These weight each run, and each scenario, equally.

| arm | window | sampler | pooled micro-F1 | run-macro | scenario-macro |
|---|---:|---|---|---|---|
| GRU | 8 | ordinary | 0.8766 +/- 0.0072 | 0.8168 +/- 0.0102 | 0.7420 +/- 0.0189 |
| GRU | 16 | ordinary | 0.8780 +/- 0.0127 | 0.8249 +/- 0.0196 | 0.7569 +/- 0.0276 |
| GRU | 16 | overlap | 0.8836 +/- 0.0065 | 0.8296 +/- 0.0099 | 0.7643 +/- 0.0165 |
| GRU | 32 | ordinary | 0.8782 +/- 0.0102 | 0.8243 +/- 0.0155 | 0.7581 +/- 0.0215 |
| GRU | 64 | ordinary | 0.8754 +/- 0.0109 | 0.8226 +/- 0.0141 | 0.7570 +/- 0.0180 |
| LSTM | 8 | ordinary | 0.8743 +/- 0.0085 | 0.8112 +/- 0.0107 | 0.7294 +/- 0.0156 |
| LSTM | 16 | ordinary | 0.8792 +/- 0.0081 | 0.8241 +/- 0.0101 | 0.7525 +/- 0.0133 |
| LSTM | 16 | overlap | 0.8794 +/- 0.0137 | 0.8259 +/- 0.0172 | 0.7601 +/- 0.0280 |
| LSTM | 32 | ordinary | 0.8780 +/- 0.0106 | 0.8247 +/- 0.0127 | 0.7565 +/- 0.0207 |
| LSTM | 64 | ordinary | 0.8788 +/- 0.0111 | 0.8256 +/- 0.0157 | 0.7566 +/- 0.0232 |
| NoHistory | 16 | ordinary | 0.1945 +/- 0.0000 | 0.1655 +/- 0.0000 | 0.1125 +/- 0.0000 |
| OrderFree | 8 | ordinary | 0.8327 +/- 0.0088 | 0.7385 +/- 0.0114 | 0.6415 +/- 0.0134 |
| OrderFree | 16 | ordinary | 0.8524 +/- 0.0126 | 0.7779 +/- 0.0274 | 0.7039 +/- 0.0422 |
| OrderFree | 32 | ordinary | 0.8496 +/- 0.0055 | 0.7771 +/- 0.0159 | 0.7075 +/- 0.0218 |
| OrderFree | 64 | ordinary | 0.8508 +/- 0.0165 | 0.7756 +/- 0.0262 | 0.7033 +/- 0.0333 |
| Transformer | 8 | ordinary | 0.8887 +/- 0.0078 | 0.8399 +/- 0.0094 | 0.7665 +/- 0.0157 |
| Transformer | 16 | ordinary | 0.8863 +/- 0.0126 | 0.8446 +/- 0.0097 | 0.7811 +/- 0.0118 |
| Transformer | 16 | overlap | 0.8768 +/- 0.0101 | 0.8401 +/- 0.0120 | 0.7803 +/- 0.0199 |
| Transformer | 32 | ordinary | 0.8889 +/- 0.0081 | 0.8454 +/- 0.0077 | 0.7813 +/- 0.0144 |
| Transformer | 64 | ordinary | 0.8894 +/- 0.0111 | 0.8463 +/- 0.0119 | 0.7803 +/- 0.0210 |

## Secondary: final checkpoint

| arm | window | sampler | micro-F1 (final) | micro-F1 (val-best) |
|---|---:|---|---|---|
| GRU | 8 | ordinary | 0.8753 +/- 0.0060 | 0.8766 +/- 0.0072 |
| GRU | 16 | ordinary | 0.8709 +/- 0.0348 | 0.8780 +/- 0.0127 |
| GRU | 16 | overlap | 0.8833 +/- 0.0074 | 0.8836 +/- 0.0065 |
| GRU | 32 | ordinary | 0.8829 +/- 0.0076 | 0.8782 +/- 0.0102 |
| GRU | 64 | ordinary | 0.8785 +/- 0.0118 | 0.8754 +/- 0.0109 |
| LSTM | 8 | ordinary | 0.8781 +/- 0.0061 | 0.8743 +/- 0.0085 |
| LSTM | 16 | ordinary | 0.8792 +/- 0.0098 | 0.8792 +/- 0.0081 |
| LSTM | 16 | overlap | 0.8745 +/- 0.0119 | 0.8794 +/- 0.0137 |
| LSTM | 32 | ordinary | 0.8829 +/- 0.0101 | 0.8780 +/- 0.0106 |
| LSTM | 64 | ordinary | 0.8834 +/- 0.0093 | 0.8788 +/- 0.0111 |
| NoHistory | 16 | ordinary | 0.1945 +/- 0.0000 | 0.1945 +/- 0.0000 |
| OrderFree | 8 | ordinary | 0.8268 +/- 0.0117 | 0.8327 +/- 0.0088 |
| OrderFree | 16 | ordinary | 0.8537 +/- 0.0173 | 0.8524 +/- 0.0126 |
| OrderFree | 32 | ordinary | 0.8580 +/- 0.0098 | 0.8496 +/- 0.0055 |
| OrderFree | 64 | ordinary | 0.8532 +/- 0.0122 | 0.8508 +/- 0.0165 |
| Transformer | 8 | ordinary | 0.8787 +/- 0.0177 | 0.8887 +/- 0.0078 |
| Transformer | 16 | ordinary | 0.8827 +/- 0.0135 | 0.8863 +/- 0.0126 |
| Transformer | 16 | overlap | 0.8708 +/- 0.0155 | 0.8768 +/- 0.0101 |
| Transformer | 32 | ordinary | 0.8853 +/- 0.0129 | 0.8889 +/- 0.0081 |
| Transformer | 64 | ordinary | 0.8706 +/- 0.0160 | 0.8894 +/- 0.0111 |

## Thresholds and training effort

| arm | window | sampler | threshold | best update | updates | mean window exposure | seconds |
|---|---:|---|---|---|---|---|---|
| GRU | 8 | ordinary | 0.48 +/- 0.04 | 2259 +/- 163 | 3226 +/- 163 | 201.6 +/- 10.2 | 41 +/- 2 |
| GRU | 16 | ordinary | 0.49 +/- 0.03 | 2592 +/- 385 | 3526 +/- 421 | 220.4 +/- 26.3 | 84 +/- 10 |
| GRU | 16 | overlap | 0.49 +/- 0.03 | 2918 +/- 365 | 3770 +/- 471 | 243.5 +/- 30.4 | 88 +/- 11 |
| GRU | 32 | ordinary | 0.50 +/- 0.00 | 2458 +/- 240 | 3379 +/- 193 | 211.2 +/- 12.0 | 156 +/- 8 |
| GRU | 64 | ordinary | 0.50 +/- 0.00 | 2509 +/- 344 | 3456 +/- 353 | 216.0 +/- 22.1 | 312 +/- 31 |
| LSTM | 8 | ordinary | 0.47 +/- 0.07 | 2304 +/- 306 | 3194 +/- 233 | 199.6 +/- 14.5 | 26 +/- 2 |
| LSTM | 16 | ordinary | 0.47 +/- 0.05 | 2490 +/- 330 | 3398 +/- 214 | 212.4 +/- 13.4 | 48 +/- 3 |
| LSTM | 16 | overlap | 0.47 +/- 0.05 | 2682 +/- 380 | 3520 +/- 160 | 227.4 +/- 10.3 | 47 +/- 5 |
| LSTM | 32 | ordinary | 0.48 +/- 0.04 | 2445 +/- 286 | 3277 +/- 200 | 204.8 +/- 12.5 | 86 +/- 6 |
| LSTM | 64 | ordinary | 0.44 +/- 0.05 | 2586 +/- 238 | 3539 +/- 254 | 221.2 +/- 15.9 | 172 +/- 20 |
| NoHistory | 16 | ordinary | 0.20 +/- 0.00 | 4672 +/- 0 | 4672 +/- 0 | 292.0 +/- 0.0 | 5 +/- 0 |
| OrderFree | 8 | ordinary | 0.50 +/- 0.00 | 2202 +/- 412 | 3123 +/- 430 | 195.2 +/- 26.9 | 6 +/- 1 |
| OrderFree | 16 | ordinary | 0.50 +/- 0.00 | 2477 +/- 406 | 3501 +/- 406 | 218.8 +/- 25.4 | 7 +/- 1 |
| OrderFree | 32 | ordinary | 0.45 +/- 0.07 | 2541 +/- 260 | 3334 +/- 284 | 208.4 +/- 17.7 | 7 +/- 1 |
| OrderFree | 64 | ordinary | 0.49 +/- 0.03 | 2637 +/- 432 | 3514 +/- 511 | 219.6 +/- 31.9 | 8 +/- 1 |
| Transformer | 8 | ordinary | 0.50 +/- 0.00 | 2893 +/- 358 | 3821 +/- 367 | 238.8 +/- 22.9 | 17 +/- 2 |
| Transformer | 16 | ordinary | 0.50 +/- 0.00 | 3232 +/- 565 | 4122 +/- 419 | 257.6 +/- 26.2 | 18 +/- 2 |
| Transformer | 16 | overlap | 0.49 +/- 0.03 | 2976 +/- 579 | 3962 +/- 510 | 255.9 +/- 32.9 | 18 +/- 3 |
| Transformer | 32 | ordinary | 0.50 +/- 0.00 | 3386 +/- 386 | 4147 +/- 342 | 259.2 +/- 21.4 | 19 +/- 1 |
| Transformer | 64 | ordinary | 0.50 +/- 0.00 | 3379 +/- 306 | 4282 +/- 298 | 267.6 +/- 18.6 | 19 +/- 3 |

## Capacity, runtime and memory

Trainable parameters are matched across arms; the positional-encoding buffer is NOT trainable and grows with the window, so a window result is never a capacity result.

| arm | window | trunk params | total trainable | PE buffer elements | peak MB |
|---|---:|---:|---:|---:|---:|
| GRU | 8 | 67279 | 78307 | 0 | 68.3 |
| GRU | 16 | 67279 | 78307 | 0 | 70.0 |
| GRU | 32 | 67279 | 78307 | 0 | 73.8 |
| GRU | 64 | 67279 | 78307 | 0 | 81.6 |
| LSTM | 8 | 67152 | 78180 | 0 | 68.4 |
| LSTM | 16 | 67152 | 78180 | 0 | 70.6 |
| LSTM | 32 | 67152 | 78180 | 0 | 75.0 |
| LSTM | 64 | 67152 | 78180 | 0 | 83.9 |
| NoHistory | 16 | 0 | 11028 | 0 | 66.5 |
| OrderFree | 8 | 67256 | 78284 | 0 | 67.6 |
| OrderFree | 16 | 67256 | 78284 | 0 | 68.9 |
| OrderFree | 32 | 67256 | 78284 | 0 | 71.6 |
| OrderFree | 64 | 67256 | 78284 | 0 | 76.9 |
| Transformer | 8 | 67072 | 78100 | 512 | 69.9 |
| Transformer | 16 | 67072 | 78100 | 1024 | 73.5 |
| Transformer | 32 | 67072 | 78100 | 2048 | 82.3 |
| Transformer | 64 | 67072 | 78100 | 4096 | 110.5 |
