# Patience and budget selection

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


Both are chosen on VALIDATION only, from pilot runs, before any main run. The numbers below are OUR protocol, not published optima.

- pilot cap: **8192** updates across **57** cells
- rule: smallest patience within tolerance of the best mean validation BCE, configurations weighted equally
- **chosen patience: 16 validation checks** (= 1024 updates without a meaningful improvement)

## Mean validation BCE by candidate patience

| patience (checks) | updates | mean validation BCE |
|---:|---:|---:|
| 16 | 1024 | 0.014944 |
| 32 | 2048 | 0.014925 |
| 64 | 4096 | 0.014925 |

## Shared update budget

- rule: ceil(1.25 x max configuration-wise median validation-best update / 64) x 64
- **shared budget: 4672 updates**

| configuration | median validation-best update |
|---|---:|
| `GRU_W16_ordinary` | 2560 |
| `GRU_W16_overlap` | 2560 |
| `GRU_W32_ordinary` | 2304 |
| `GRU_W64_ordinary` | 2304 |
| `GRU_W8_ordinary` | 2432 |
| `LSTM_W16_ordinary` | 2560 |
| `LSTM_W16_overlap` | 2560 |
| `LSTM_W32_ordinary` | 2432 |
| `LSTM_W64_ordinary` | 2432 |
| `LSTM_W8_ordinary` | 2368 |
| `OrderFree_W16_ordinary` | 2432 |
| `OrderFree_W32_ordinary` | 3136 |
| `OrderFree_W64_ordinary` | 2688 |
| `OrderFree_W8_ordinary` | 2048 |
| `Transformer_W16_ordinary` | 3328 |
| `Transformer_W16_overlap` | 3008 |
| `Transformer_W32_ordinary` | 3456 |
| `Transformer_W64_ordinary` | 3712 |
| `Transformer_W8_ordinary` | 2624 |

## Convergence

No configuration had its validation best in the last 10% of the cap, so the cap did not visibly truncate training. This is evidence against truncation, not proof of convergence.

## Per-configuration stopping simulation

Each pilot trajectory replayed under every candidate rule, using only information available before its own simulated stop.

| configuration | patience | stopped at | selected update | val BCE | triggered |
|---|---:|---:|---:|---:|---|
| `GRU_W16_ordinary_s101` | 16 | 3264 | 2432 | 0.014139 | True |
| `GRU_W16_ordinary_s101` | 32 | 4288 | 2432 | 0.014139 | True |
| `GRU_W16_ordinary_s101` | 64 | 6336 | 2432 | 0.014139 | True |
| `GRU_W16_ordinary_s102` | 16 | 3648 | 2624 | 0.013710 | True |
| `GRU_W16_ordinary_s102` | 32 | 4672 | 2624 | 0.013710 | True |
| `GRU_W16_ordinary_s102` | 64 | 6720 | 2624 | 0.013710 | True |
| `GRU_W16_ordinary_s103` | 16 | 3584 | 2560 | 0.013933 | True |
| `GRU_W16_ordinary_s103` | 32 | 4608 | 2560 | 0.013933 | True |
| `GRU_W16_ordinary_s103` | 64 | 6656 | 2560 | 0.013933 | True |
| `GRU_W16_overlap_s101` | 16 | 3264 | 2240 | 0.014443 | True |
| `GRU_W16_overlap_s101` | 32 | 4288 | 2240 | 0.014443 | True |
| `GRU_W16_overlap_s101` | 64 | 6336 | 2240 | 0.014443 | True |
| `GRU_W16_overlap_s102` | 16 | 3584 | 2560 | 0.013664 | True |
| `GRU_W16_overlap_s102` | 32 | 4608 | 2560 | 0.013664 | True |
| `GRU_W16_overlap_s102` | 64 | 6656 | 2560 | 0.013664 | True |
| `GRU_W16_overlap_s103` | 16 | 3776 | 2752 | 0.013208 | True |
| `GRU_W16_overlap_s103` | 32 | 4800 | 2752 | 0.013208 | True |
| `GRU_W16_overlap_s103` | 64 | 6848 | 2752 | 0.013208 | True |
| `GRU_W32_ordinary_s101` | 16 | 3456 | 2432 | 0.014315 | True |
| `GRU_W32_ordinary_s101` | 32 | 4480 | 2432 | 0.014315 | True |
| `GRU_W32_ordinary_s101` | 64 | 6528 | 2432 | 0.014315 | True |
| `GRU_W32_ordinary_s102` | 16 | 3136 | 2112 | 0.014106 | True |
| `GRU_W32_ordinary_s102` | 32 | 4160 | 2112 | 0.014106 | True |
| `GRU_W32_ordinary_s102` | 64 | 6208 | 2112 | 0.014106 | True |
| `GRU_W32_ordinary_s103` | 16 | 3328 | 2304 | 0.013809 | True |
| `GRU_W32_ordinary_s103` | 32 | 4352 | 2304 | 0.013809 | True |
| `GRU_W32_ordinary_s103` | 64 | 6400 | 2304 | 0.013809 | True |
| `GRU_W64_ordinary_s101` | 16 | 3264 | 2240 | 0.014149 | True |
| `GRU_W64_ordinary_s101` | 32 | 4288 | 2240 | 0.014149 | True |
| `GRU_W64_ordinary_s101` | 64 | 6336 | 2240 | 0.014149 | True |
| `GRU_W64_ordinary_s102` | 16 | 3328 | 2304 | 0.014365 | True |
| `GRU_W64_ordinary_s102` | 32 | 4352 | 2304 | 0.014365 | True |
| `GRU_W64_ordinary_s102` | 64 | 6400 | 2304 | 0.014365 | True |
| `GRU_W64_ordinary_s103` | 16 | 3584 | 2560 | 0.013983 | True |
| `GRU_W64_ordinary_s103` | 32 | 4608 | 2560 | 0.013983 | True |
| `GRU_W64_ordinary_s103` | 64 | 6656 | 2560 | 0.013983 | True |
| `GRU_W8_ordinary_s101` | 16 | 3008 | 2432 | 0.014354 | True |
| `GRU_W8_ordinary_s101` | 32 | 4032 | 3136 | 0.014257 | True |
| `GRU_W8_ordinary_s101` | 64 | 6080 | 3136 | 0.014257 | True |
| `GRU_W8_ordinary_s102` | 16 | 3008 | 2048 | 0.014268 | True |
| `GRU_W8_ordinary_s102` | 32 | 4032 | 2048 | 0.014268 | True |
| `GRU_W8_ordinary_s102` | 64 | 6080 | 2048 | 0.014268 | True |
| `GRU_W8_ordinary_s103` | 16 | 3264 | 2432 | 0.013895 | True |
| `GRU_W8_ordinary_s103` | 32 | 4288 | 2432 | 0.013895 | True |
| `GRU_W8_ordinary_s103` | 64 | 6336 | 2432 | 0.013895 | True |
| `LSTM_W16_ordinary_s101` | 16 | 3328 | 2432 | 0.015792 | True |
| `LSTM_W16_ordinary_s101` | 32 | 4352 | 2432 | 0.015792 | True |
| `LSTM_W16_ordinary_s101` | 64 | 6400 | 2432 | 0.015792 | True |
| `LSTM_W16_ordinary_s102` | 16 | 3008 | 2560 | 0.013261 | True |
| `LSTM_W16_ordinary_s102` | 32 | 4032 | 2560 | 0.013261 | True |
| `LSTM_W16_ordinary_s102` | 64 | 6080 | 2560 | 0.013261 | True |
| `LSTM_W16_ordinary_s103` | 16 | 3648 | 2624 | 0.013072 | True |
| `LSTM_W16_ordinary_s103` | 32 | 4672 | 2624 | 0.013072 | True |
| `LSTM_W16_ordinary_s103` | 64 | 6720 | 2624 | 0.013072 | True |
| `LSTM_W16_overlap_s101` | 16 | 3648 | 2624 | 0.014939 | True |
| `LSTM_W16_overlap_s101` | 32 | 4672 | 2624 | 0.014939 | True |
| `LSTM_W16_overlap_s101` | 64 | 6720 | 2624 | 0.014939 | True |
| `LSTM_W16_overlap_s102` | 16 | 3584 | 2560 | 0.013734 | True |
| `LSTM_W16_overlap_s102` | 32 | 4608 | 2560 | 0.013734 | True |
| `LSTM_W16_overlap_s102` | 64 | 6656 | 2560 | 0.013734 | True |
| `LSTM_W16_overlap_s103` | 16 | 3392 | 2368 | 0.014178 | True |
| `LSTM_W16_overlap_s103` | 32 | 4416 | 2368 | 0.014178 | True |
| `LSTM_W16_overlap_s103` | 64 | 6464 | 2368 | 0.014178 | True |
| `LSTM_W32_ordinary_s101` | 16 | 3136 | 2112 | 0.016033 | True |
| `LSTM_W32_ordinary_s101` | 32 | 4160 | 2112 | 0.016033 | True |
| `LSTM_W32_ordinary_s101` | 64 | 6208 | 2112 | 0.016033 | True |
| `LSTM_W32_ordinary_s102` | 16 | 3456 | 2432 | 0.013656 | True |
| `LSTM_W32_ordinary_s102` | 32 | 4480 | 2432 | 0.013656 | True |
| `LSTM_W32_ordinary_s102` | 64 | 6528 | 2432 | 0.013656 | True |
| `LSTM_W32_ordinary_s103` | 16 | 3520 | 3008 | 0.014048 | True |
| `LSTM_W32_ordinary_s103` | 32 | 4544 | 3008 | 0.014048 | True |
| `LSTM_W32_ordinary_s103` | 64 | 6592 | 3008 | 0.014048 | True |
| `LSTM_W64_ordinary_s101` | 16 | 3520 | 2496 | 0.015156 | True |
| `LSTM_W64_ordinary_s101` | 32 | 4544 | 2496 | 0.015156 | True |
| `LSTM_W64_ordinary_s101` | 64 | 6592 | 2496 | 0.015156 | True |
| `LSTM_W64_ordinary_s102` | 16 | 3456 | 2432 | 0.013219 | True |
| `LSTM_W64_ordinary_s102` | 32 | 4480 | 2432 | 0.013219 | True |
| `LSTM_W64_ordinary_s102` | 64 | 6528 | 2432 | 0.013219 | True |
| `LSTM_W64_ordinary_s103` | 16 | 3392 | 2368 | 0.013105 | True |
| `LSTM_W64_ordinary_s103` | 32 | 4416 | 2368 | 0.013105 | True |
| `LSTM_W64_ordinary_s103` | 64 | 6464 | 2368 | 0.013105 | True |
| `LSTM_W8_ordinary_s101` | 16 | 3072 | 2048 | 0.016407 | True |
| `LSTM_W8_ordinary_s101` | 32 | 4096 | 2048 | 0.016407 | True |
| `LSTM_W8_ordinary_s101` | 64 | 6144 | 2048 | 0.016407 | True |
| `LSTM_W8_ordinary_s102` | 16 | 3264 | 2368 | 0.013603 | True |
| `LSTM_W8_ordinary_s102` | 32 | 4288 | 2368 | 0.013603 | True |
| `LSTM_W8_ordinary_s102` | 64 | 6336 | 2368 | 0.013603 | True |
| `LSTM_W8_ordinary_s103` | 16 | 3584 | 2560 | 0.013260 | True |
| `LSTM_W8_ordinary_s103` | 32 | 4608 | 2560 | 0.013260 | True |
| `LSTM_W8_ordinary_s103` | 64 | 6656 | 2560 | 0.013260 | True |
| `OrderFree_W16_ordinary_s101` | 16 | 3328 | 2304 | 0.019224 | True |
| `OrderFree_W16_ordinary_s101` | 32 | 4352 | 2304 | 0.019224 | True |
| `OrderFree_W16_ordinary_s101` | 64 | 6400 | 2304 | 0.019224 | True |
| `OrderFree_W16_ordinary_s102` | 16 | 3776 | 2752 | 0.019511 | True |
| `OrderFree_W16_ordinary_s102` | 32 | 4800 | 2752 | 0.019511 | True |
| `OrderFree_W16_ordinary_s102` | 64 | 6848 | 2752 | 0.019511 | True |
| `OrderFree_W16_ordinary_s103` | 16 | 3456 | 2432 | 0.021046 | True |
| `OrderFree_W16_ordinary_s103` | 32 | 4480 | 2432 | 0.021046 | True |
| `OrderFree_W16_ordinary_s103` | 64 | 6528 | 2432 | 0.021046 | True |
| `OrderFree_W32_ordinary_s101` | 16 | 4096 | 3072 | 0.018471 | True |
| `OrderFree_W32_ordinary_s101` | 32 | 5120 | 3072 | 0.018471 | True |
| `OrderFree_W32_ordinary_s101` | 64 | 7168 | 3072 | 0.018471 | True |
| `OrderFree_W32_ordinary_s102` | 16 | 4160 | 3136 | 0.017464 | True |
| `OrderFree_W32_ordinary_s102` | 32 | 5184 | 3136 | 0.017464 | True |
| `OrderFree_W32_ordinary_s102` | 64 | 7232 | 3136 | 0.017464 | True |
| `OrderFree_W32_ordinary_s103` | 16 | 4288 | 3264 | 0.022236 | True |
| `OrderFree_W32_ordinary_s103` | 32 | 5312 | 3264 | 0.022236 | True |
| `OrderFree_W32_ordinary_s103` | 64 | 7360 | 3264 | 0.022236 | True |
| `OrderFree_W64_ordinary_s101` | 16 | 3328 | 2880 | 0.019655 | True |
| `OrderFree_W64_ordinary_s101` | 32 | 4352 | 2880 | 0.019655 | True |
| `OrderFree_W64_ordinary_s101` | 64 | 6400 | 2880 | 0.019655 | True |
| `OrderFree_W64_ordinary_s102` | 16 | 3712 | 2688 | 0.017961 | True |
| `OrderFree_W64_ordinary_s102` | 32 | 4736 | 2688 | 0.017961 | True |
| `OrderFree_W64_ordinary_s102` | 64 | 6784 | 2688 | 0.017961 | True |
| `OrderFree_W64_ordinary_s103` | 16 | 3200 | 2176 | 0.022628 | True |
| `OrderFree_W64_ordinary_s103` | 32 | 4224 | 2176 | 0.022628 | True |
| `OrderFree_W64_ordinary_s103` | 64 | 6272 | 2176 | 0.022628 | True |
| `OrderFree_W8_ordinary_s101` | 16 | 2816 | 1792 | 0.017767 | True |
| `OrderFree_W8_ordinary_s101` | 32 | 3840 | 1792 | 0.017767 | True |
| `OrderFree_W8_ordinary_s101` | 64 | 5888 | 1792 | 0.017767 | True |
| `OrderFree_W8_ordinary_s102` | 16 | 3264 | 2240 | 0.017948 | True |
| `OrderFree_W8_ordinary_s102` | 32 | 4288 | 2240 | 0.017948 | True |
| `OrderFree_W8_ordinary_s102` | 64 | 6336 | 2240 | 0.017948 | True |
| `OrderFree_W8_ordinary_s103` | 16 | 3072 | 2048 | 0.018725 | True |
| `OrderFree_W8_ordinary_s103` | 32 | 4096 | 2048 | 0.018725 | True |
| `OrderFree_W8_ordinary_s103` | 64 | 6144 | 2048 | 0.018725 | True |
| `Transformer_W16_ordinary_s101` | 16 | 4352 | 3328 | 0.012490 | True |
| `Transformer_W16_ordinary_s101` | 32 | 5376 | 3328 | 0.012490 | True |
| `Transformer_W16_ordinary_s101` | 64 | 7424 | 3328 | 0.012490 | True |
| `Transformer_W16_ordinary_s102` | 16 | 4352 | 3328 | 0.012587 | True |
| `Transformer_W16_ordinary_s102` | 32 | 5376 | 3328 | 0.012587 | True |
| `Transformer_W16_ordinary_s102` | 64 | 7424 | 3328 | 0.012587 | True |
| `Transformer_W16_ordinary_s103` | 16 | 4160 | 3136 | 0.013117 | True |
| `Transformer_W16_ordinary_s103` | 32 | 5184 | 3136 | 0.013117 | True |
| `Transformer_W16_ordinary_s103` | 64 | 7232 | 3136 | 0.013117 | True |
| `Transformer_W16_overlap_s101` | 16 | 4288 | 3456 | 0.013928 | True |
| `Transformer_W16_overlap_s101` | 32 | 5312 | 3456 | 0.013928 | True |
| `Transformer_W16_overlap_s101` | 64 | 7360 | 3456 | 0.013928 | True |
| `Transformer_W16_overlap_s102` | 16 | 4032 | 3008 | 0.013221 | True |
| `Transformer_W16_overlap_s102` | 32 | 5056 | 3008 | 0.013221 | True |
| `Transformer_W16_overlap_s102` | 64 | 7104 | 3008 | 0.013221 | True |
| `Transformer_W16_overlap_s103` | 16 | 3840 | 2816 | 0.014244 | True |
| `Transformer_W16_overlap_s103` | 32 | 4864 | 2816 | 0.014244 | True |
| `Transformer_W16_overlap_s103` | 64 | 6912 | 2816 | 0.014244 | True |
| `Transformer_W32_ordinary_s101` | 16 | 4416 | 3392 | 0.012576 | True |
| `Transformer_W32_ordinary_s101` | 32 | 5440 | 3392 | 0.012576 | True |
| `Transformer_W32_ordinary_s101` | 64 | 7488 | 3392 | 0.012576 | True |
| `Transformer_W32_ordinary_s102` | 16 | 4480 | 3456 | 0.012480 | True |
| `Transformer_W32_ordinary_s102` | 32 | 5504 | 3456 | 0.012480 | True |
| `Transformer_W32_ordinary_s102` | 64 | 7552 | 3456 | 0.012480 | True |
| `Transformer_W32_ordinary_s103` | 16 | 4480 | 3648 | 0.012895 | True |
| `Transformer_W32_ordinary_s103` | 32 | 5504 | 3648 | 0.012895 | True |
| `Transformer_W32_ordinary_s103` | 64 | 7552 | 3648 | 0.012895 | True |
| `Transformer_W64_ordinary_s101` | 16 | 3520 | 2496 | 0.014052 | True |
| `Transformer_W64_ordinary_s101` | 32 | 5760 | 3712 | 0.013078 | True |
| `Transformer_W64_ordinary_s101` | 64 | 7808 | 3712 | 0.013078 | True |
| `Transformer_W64_ordinary_s102` | 16 | 4800 | 3776 | 0.012553 | True |
| `Transformer_W64_ordinary_s102` | 32 | 5824 | 4928 | 0.012514 | True |
| `Transformer_W64_ordinary_s102` | 64 | 7872 | 4928 | 0.012514 | True |
| `Transformer_W64_ordinary_s103` | 16 | 3904 | 3648 | 0.012697 | True |
| `Transformer_W64_ordinary_s103` | 32 | 4928 | 3648 | 0.012697 | True |
| `Transformer_W64_ordinary_s103` | 64 | 6976 | 3648 | 0.012697 | True |
| `Transformer_W8_ordinary_s101` | 16 | 3648 | 2624 | 0.011928 | True |
| `Transformer_W8_ordinary_s101` | 32 | 4672 | 2624 | 0.011928 | True |
| `Transformer_W8_ordinary_s101` | 64 | 6720 | 2624 | 0.011928 | True |
| `Transformer_W8_ordinary_s102` | 16 | 3584 | 2560 | 0.013323 | True |
| `Transformer_W8_ordinary_s102` | 32 | 4608 | 2560 | 0.013323 | True |
| `Transformer_W8_ordinary_s102` | 64 | 6656 | 2560 | 0.013323 | True |
| `Transformer_W8_ordinary_s103` | 16 | 3200 | 2688 | 0.013297 | True |
| `Transformer_W8_ordinary_s103` | 32 | 4224 | 2688 | 0.013297 | True |
| `Transformer_W8_ordinary_s103` | 64 | 6272 | 2688 | 0.013297 | True |
