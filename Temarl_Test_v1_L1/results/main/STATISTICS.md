# Statistics

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


- test: two-sided paired t-test across matched training seeds
- correction: holm, alpha = 0.05

_Non-significance is NOT equivalence. An equivalence claim requires a predeclared margin and a TOST; absent that, report 'no clear difference detected'._

_Seeds, environment repeats and prediction windows are NOT independent attack campaigns. The corpus contains 36 playbooks from 7 scenarios; that is the real sample size for any generalisation claim._

## Prediction family (micro_f1)

_All encoder-vs-encoder contrasts at the reference window, all window-vs-reference contrasts within each encoder, and the overlap-vs-ordinary contrast. Corrected together._

| contrast | pairs | delta | 95% CI | p raw | p Holm | verdict |
|---|---:|---:|---|---:|---:|---|
| prediction W16: Transformer - GRU | 10 | +0.00831 | [-0.00380, +0.02043] | 0.15494 | 0.77468 | NO CLEAR DIFFERENCE |
| prediction W16: Transformer - LSTM | 10 | +0.00715 | [-0.00365, +0.01795] | 0.16854 | 0.77468 | NO CLEAR DIFFERENCE |
| prediction W16: Transformer - OrderFree | 10 | +0.03387 | [+0.01953, +0.04822] | 0.00047 | 0.00345 | BETTER |
| prediction W16: GRU - LSTM | 10 | -0.00117 | [-0.01119, +0.00886] | 0.79858 | 1.00000 | NO CLEAR DIFFERENCE |
| prediction W16: GRU - OrderFree | 10 | +0.02556 | [+0.01486, +0.03626] | 0.00043 | 0.00345 | BETTER |
| prediction W16: LSTM - OrderFree | 10 | +0.02673 | [+0.01822, +0.03523] | 0.00006 | 0.00051 | BETTER |
| prediction W16: Transformer - NoHistory | 10 | +0.69181 | [+0.68281, +0.70081] | 0.00000 | 0.00000 | BETTER |
| prediction W16: GRU - NoHistory | 10 | +0.68349 | [+0.67440, +0.69259] | 0.00000 | 0.00000 | BETTER |
| prediction W16: LSTM - NoHistory | 10 | +0.68466 | [+0.67883, +0.69049] | 0.00000 | 0.00000 | BETTER |
| prediction W16: OrderFree - NoHistory | 10 | +0.65793 | [+0.64893, +0.66693] | 0.00000 | 0.00000 | BETTER |
| prediction W16: Transformer overlap - ordinary | 10 | -0.00949 | [-0.01735, -0.00162] | 0.02329 | 0.13976 | NO CLEAR DIFFERENCE |
| prediction W16: GRU overlap - ordinary | 10 | +0.00559 | [-0.00293, +0.01411] | 0.17184 | 0.77468 | NO CLEAR DIFFERENCE |
| prediction W16: LSTM overlap - ordinary | 10 | +0.00019 | [-0.00692, +0.00729] | 0.95366 | 1.00000 | NO CLEAR DIFFERENCE |

## Deception family

_All encoder-vs-encoder, MAPPO-vs-IPPO, encoder-vs-NoHistory and context-window contrasts on dwell, depth and protection. Corrected together, separately from the prediction family._

| contrast | pairs | delta | 95% CI | p raw | p Holm | verdict |
|---|---:|---:|---|---:|---:|---|
| dwell W16: GRU+IPPO - GRU+MAPPO | 10 | -0.2457 | [-0.4582, -0.0332] | 0.02800 | 1.00000 | NO CLEAR DIFFERENCE |
| dwell W16: GRU+IPPO - LSTM+IPPO | 10 | -0.0849 | [-0.2968, +0.1271] | 0.38873 | 1.00000 | NO CLEAR DIFFERENCE |
| dwell W16: GRU+IPPO - NoHistory+IPPO | 10 | +2.8386 | [+2.7020, +2.9752] | 0.00000 | 0.00000 | BETTER |
| dwell W16: GRU+IPPO - OrderFree+IPPO | 10 | -0.2871 | [-0.7247, +0.1504] | 0.17179 | 1.00000 | NO CLEAR DIFFERENCE |
| dwell W16: GRU+IPPO - Transformer+IPPO | 10 | -0.5460 | [-0.8887, -0.2033] | 0.00571 | 0.33692 | NO CLEAR DIFFERENCE |
| dwell W64: GRU+IPPO - GRU+MAPPO | 10 | -0.2360 | [-0.3786, -0.0934] | 0.00460 | 0.29910 | NO CLEAR DIFFERENCE |
| dwell W64: GRU+IPPO - LSTM+IPPO | 10 | -0.1706 | [-0.4753, +0.1341] | 0.23716 | 1.00000 | NO CLEAR DIFFERENCE |
| dwell W64: GRU+IPPO - Transformer+IPPO | 10 | -0.4220 | [-0.7616, -0.0824] | 0.02034 | 0.96297 | NO CLEAR DIFFERENCE |
| dwell W16: GRU+MAPPO - LSTM+MAPPO | 10 | -0.2329 | [-0.5142, +0.0485] | 0.09393 | 1.00000 | NO CLEAR DIFFERENCE |
| dwell W16: GRU+MAPPO - NoHistory+MAPPO | 10 | +2.5940 | [+2.3122, +2.8758] | 0.00000 | 0.00000 | BETTER |
| dwell W16: GRU+MAPPO - OrderFree+MAPPO | 10 | -0.4766 | [-0.7692, -0.1840] | 0.00504 | 0.31672 | NO CLEAR DIFFERENCE |
| dwell W16: GRU+MAPPO - Transformer+MAPPO | 10 | -0.6697 | [-0.8512, -0.4883] | 0.00002 | 0.00133 | WORSE |
| dwell W64: GRU+MAPPO - LSTM+MAPPO | 10 | -0.0640 | [-0.2761, +0.1481] | 0.51201 | 1.00000 | NO CLEAR DIFFERENCE |
| dwell W64: GRU+MAPPO - Transformer+MAPPO | 10 | -0.6023 | [-0.9926, -0.2120] | 0.00682 | 0.38864 | NO CLEAR DIFFERENCE |
| dwell W16: LSTM+IPPO - LSTM+MAPPO | 10 | -0.3937 | [-0.5431, -0.2444] | 0.00021 | 0.01715 | WORSE |
| dwell W16: LSTM+IPPO - NoHistory+IPPO | 10 | +2.9234 | [+2.7510, +3.0959] | 0.00000 | 0.00000 | BETTER |
| dwell W16: LSTM+IPPO - OrderFree+IPPO | 10 | -0.2023 | [-0.5689, +0.1643] | 0.24344 | 1.00000 | NO CLEAR DIFFERENCE |
| dwell W16: LSTM+IPPO - Transformer+IPPO | 10 | -0.4611 | [-0.7370, -0.1853] | 0.00434 | 0.28633 | NO CLEAR DIFFERENCE |
| dwell W64: LSTM+IPPO - LSTM+MAPPO | 10 | -0.1294 | [-0.4168, +0.1579] | 0.33482 | 1.00000 | NO CLEAR DIFFERENCE |
| dwell W64: LSTM+IPPO - Transformer+IPPO | 10 | -0.2514 | [-0.5975, +0.0947] | 0.13471 | 1.00000 | NO CLEAR DIFFERENCE |
| dwell W16: LSTM+MAPPO - NoHistory+MAPPO | 10 | +2.8269 | [+2.4795, +3.1743] | 0.00000 | 0.00000 | BETTER |
| dwell W16: LSTM+MAPPO - OrderFree+MAPPO | 10 | -0.2437 | [-0.5796, +0.0922] | 0.13516 | 1.00000 | NO CLEAR DIFFERENCE |
| dwell W16: LSTM+MAPPO - Transformer+MAPPO | 10 | -0.4369 | [-0.6146, -0.2591] | 0.00035 | 0.02780 | WORSE |
| dwell W64: LSTM+MAPPO - Transformer+MAPPO | 10 | -0.5383 | [-0.8677, -0.2089] | 0.00495 | 0.31672 | NO CLEAR DIFFERENCE |
| dwell W16: NoHistory+IPPO - NoHistory+MAPPO | 10 | -0.4903 | [-0.7941, -0.1864] | 0.00532 | 0.31896 | NO CLEAR DIFFERENCE |
| dwell W16: NoHistory+IPPO - OrderFree+IPPO | 10 | -3.1257 | [-3.5279, -2.7235] | 0.00000 | 0.00000 | WORSE |
| dwell W16: NoHistory+IPPO - Transformer+IPPO | 10 | -3.3846 | [-3.6830, -3.0862] | 0.00000 | 0.00000 | WORSE |
| dwell W16: NoHistory+MAPPO - OrderFree+MAPPO | 10 | -3.0706 | [-3.4539, -2.6872] | 0.00000 | 0.00000 | WORSE |
| dwell W16: NoHistory+MAPPO - Transformer+MAPPO | 10 | -3.2637 | [-3.5399, -2.9875] | 0.00000 | 0.00000 | WORSE |
| dwell W16: OrderFree+IPPO - OrderFree+MAPPO | 10 | -0.4351 | [-0.5584, -0.3119] | 0.00002 | 0.00189 | WORSE |
| dwell W16: OrderFree+IPPO - Transformer+IPPO | 10 | -0.2589 | [-0.7131, +0.1954] | 0.22952 | 1.00000 | NO CLEAR DIFFERENCE |
| dwell W16: OrderFree+MAPPO - Transformer+MAPPO | 10 | -0.1931 | [-0.5416, +0.1554] | 0.24153 | 1.00000 | NO CLEAR DIFFERENCE |
| dwell W16: Transformer+IPPO - Transformer+MAPPO | 10 | -0.3694 | [-0.6352, -0.1037] | 0.01183 | 0.62707 | NO CLEAR DIFFERENCE |
| dwell W64: Transformer+IPPO - Transformer+MAPPO | 10 | -0.4163 | [-0.6834, -0.1492] | 0.00645 | 0.37433 | NO CLEAR DIFFERENCE |
| depth W16: GRU+IPPO - GRU+MAPPO | 10 | -0.1531 | [-0.3639, +0.0577] | 0.13472 | 1.00000 | NO CLEAR DIFFERENCE |
| depth W16: GRU+IPPO - LSTM+IPPO | 10 | -0.0831 | [-0.2524, +0.0861] | 0.29525 | 1.00000 | NO CLEAR DIFFERENCE |
| depth W16: GRU+IPPO - NoHistory+IPPO | 10 | +5.6803 | [+5.4984, +5.8621] | 0.00000 | 0.00000 | BETTER |
| depth W16: GRU+IPPO - OrderFree+IPPO | 10 | -0.3974 | [-0.7675, -0.0274] | 0.03801 | 1.00000 | NO CLEAR DIFFERENCE |
| depth W16: GRU+IPPO - Transformer+IPPO | 10 | -0.6783 | [-1.0450, -0.3115] | 0.00236 | 0.16303 | NO CLEAR DIFFERENCE |
| depth W64: GRU+IPPO - GRU+MAPPO | 10 | -0.2469 | [-0.4670, -0.0268] | 0.03186 | 1.00000 | NO CLEAR DIFFERENCE |
| depth W64: GRU+IPPO - LSTM+IPPO | 10 | -0.1649 | [-0.4178, +0.0881] | 0.17443 | 1.00000 | NO CLEAR DIFFERENCE |
| depth W64: GRU+IPPO - Transformer+IPPO | 10 | -0.6029 | [-0.9263, -0.2794] | 0.00225 | 0.15771 | NO CLEAR DIFFERENCE |
| depth W16: GRU+MAPPO - LSTM+MAPPO | 10 | -0.2143 | [-0.4226, -0.0059] | 0.04499 | 1.00000 | NO CLEAR DIFFERENCE |
| depth W16: GRU+MAPPO - NoHistory+MAPPO | 10 | +5.2514 | [+4.9715, +5.5313] | 0.00000 | 0.00000 | BETTER |
| depth W16: GRU+MAPPO - OrderFree+MAPPO | 10 | -0.5926 | [-1.0025, -0.1826] | 0.00969 | 0.52307 | NO CLEAR DIFFERENCE |
| depth W16: GRU+MAPPO - Transformer+MAPPO | 10 | -0.8580 | [-1.0568, -0.6592] | 0.00000 | 0.00038 | WORSE |
| depth W64: GRU+MAPPO - LSTM+MAPPO | 10 | -0.0840 | [-0.2208, +0.0528] | 0.19837 | 1.00000 | NO CLEAR DIFFERENCE |
| depth W64: GRU+MAPPO - Transformer+MAPPO | 10 | -0.7297 | [-1.1329, -0.3265] | 0.00270 | 0.18360 | NO CLEAR DIFFERENCE |
| depth W16: LSTM+IPPO - LSTM+MAPPO | 10 | -0.2843 | [-0.4917, -0.0769] | 0.01270 | 0.64766 | NO CLEAR DIFFERENCE |
| depth W16: LSTM+IPPO - NoHistory+IPPO | 10 | +5.7634 | [+5.6420, +5.8849] | 0.00000 | 0.00000 | BETTER |
| depth W16: LSTM+IPPO - OrderFree+IPPO | 10 | -0.3143 | [-0.7155, +0.0869] | 0.11014 | 1.00000 | NO CLEAR DIFFERENCE |
| depth W16: LSTM+IPPO - Transformer+IPPO | 10 | -0.5951 | [-0.8653, -0.3250] | 0.00076 | 0.05817 | NO CLEAR DIFFERENCE |
| depth W64: LSTM+IPPO - LSTM+MAPPO | 10 | -0.1660 | [-0.4843, +0.1523] | 0.26839 | 1.00000 | NO CLEAR DIFFERENCE |
| depth W64: LSTM+IPPO - Transformer+IPPO | 10 | -0.4380 | [-0.7784, -0.0976] | 0.01729 | 0.86426 | NO CLEAR DIFFERENCE |
| depth W16: LSTM+MAPPO - NoHistory+MAPPO | 10 | +5.4657 | [+5.0946, +5.8369] | 0.00000 | 0.00000 | BETTER |
| depth W16: LSTM+MAPPO - OrderFree+MAPPO | 10 | -0.3783 | [-0.7602, +0.0036] | 0.05180 | 1.00000 | NO CLEAR DIFFERENCE |
| depth W16: LSTM+MAPPO - Transformer+MAPPO | 10 | -0.6437 | [-0.9603, -0.3271] | 0.00129 | 0.09423 | NO CLEAR DIFFERENCE |
| depth W64: LSTM+MAPPO - Transformer+MAPPO | 10 | -0.6457 | [-1.0409, -0.2505] | 0.00495 | 0.31672 | NO CLEAR DIFFERENCE |
| depth W16: NoHistory+IPPO - NoHistory+MAPPO | 10 | -0.5820 | [-0.8715, -0.2925] | 0.00139 | 0.10006 | NO CLEAR DIFFERENCE |
| depth W16: NoHistory+IPPO - OrderFree+IPPO | 10 | -6.0777 | [-6.4629, -5.6925] | 0.00000 | 0.00000 | WORSE |
| depth W16: NoHistory+IPPO - Transformer+IPPO | 10 | -6.3586 | [-6.6354, -6.0817] | 0.00000 | 0.00000 | WORSE |
| depth W16: NoHistory+MAPPO - OrderFree+MAPPO | 10 | -5.8440 | [-6.2132, -5.4748] | 0.00000 | 0.00000 | WORSE |
| depth W16: NoHistory+MAPPO - Transformer+MAPPO | 10 | -6.1094 | [-6.4035, -5.8154] | 0.00000 | 0.00000 | WORSE |
| depth W16: OrderFree+IPPO - OrderFree+MAPPO | 10 | -0.3483 | [-0.5258, -0.1708] | 0.00162 | 0.11537 | NO CLEAR DIFFERENCE |
| depth W16: OrderFree+IPPO - Transformer+IPPO | 10 | -0.2809 | [-0.7590, +0.1972] | 0.21658 | 1.00000 | NO CLEAR DIFFERENCE |
| depth W16: OrderFree+MAPPO - Transformer+MAPPO | 10 | -0.2654 | [-0.7569, +0.2260] | 0.25281 | 1.00000 | NO CLEAR DIFFERENCE |
| depth W16: Transformer+IPPO - Transformer+MAPPO | 10 | -0.3329 | [-0.5511, -0.1146] | 0.00727 | 0.40005 | NO CLEAR DIFFERENCE |
| depth W64: Transformer+IPPO - Transformer+MAPPO | 10 | -0.3737 | [-0.7192, -0.0282] | 0.03695 | 1.00000 | NO CLEAR DIFFERENCE |
| protected W16: GRU+IPPO - GRU+MAPPO | 10 | -0.0014 | [-0.0160, +0.0132] | 0.82963 | 1.00000 | NO CLEAR DIFFERENCE |
| protected W16: GRU+IPPO - LSTM+IPPO | 10 | -0.0040 | [-0.0230, +0.0150] | 0.64539 | 1.00000 | NO CLEAR DIFFERENCE |
| protected W16: GRU+IPPO - NoHistory+IPPO | 10 | +0.0263 | [+0.0151, +0.0375] | 0.00048 | 0.03774 | BETTER |
| protected W16: GRU+IPPO - OrderFree+IPPO | 10 | -0.0234 | [-0.0543, +0.0074] | 0.12018 | 1.00000 | NO CLEAR DIFFERENCE |
| protected W16: GRU+IPPO - Transformer+IPPO | 10 | -0.0663 | [-0.1034, -0.0291] | 0.00294 | 0.19695 | NO CLEAR DIFFERENCE |
| protected W64: GRU+IPPO - GRU+MAPPO | 10 | -0.0080 | [-0.0182, +0.0022] | 0.11076 | 1.00000 | NO CLEAR DIFFERENCE |
| protected W64: GRU+IPPO - LSTM+IPPO | 10 | -0.0140 | [-0.0385, +0.0105] | 0.22761 | 1.00000 | NO CLEAR DIFFERENCE |
| protected W64: GRU+IPPO - Transformer+IPPO | 10 | -0.0491 | [-0.0874, -0.0109] | 0.01743 | 0.86426 | NO CLEAR DIFFERENCE |
| protected W16: GRU+MAPPO - LSTM+MAPPO | 10 | -0.0183 | [-0.0369, +0.0003] | 0.05310 | 1.00000 | NO CLEAR DIFFERENCE |
| protected W16: GRU+MAPPO - NoHistory+MAPPO | 10 | -0.0157 | [-0.0472, +0.0158] | 0.28837 | 1.00000 | NO CLEAR DIFFERENCE |
| protected W16: GRU+MAPPO - OrderFree+MAPPO | 10 | -0.0400 | [-0.0830, +0.0030] | 0.06484 | 1.00000 | NO CLEAR DIFFERENCE |
| protected W16: GRU+MAPPO - Transformer+MAPPO | 10 | -0.0857 | [-0.1110, -0.0604] | 0.00003 | 0.00259 | WORSE |
| protected W64: GRU+MAPPO - LSTM+MAPPO | 10 | -0.0077 | [-0.0214, +0.0060] | 0.23451 | 1.00000 | NO CLEAR DIFFERENCE |
| protected W64: GRU+MAPPO - Transformer+MAPPO | 10 | -0.0714 | [-0.1052, -0.0377] | 0.00099 | 0.07389 | NO CLEAR DIFFERENCE |
| protected W16: LSTM+IPPO - LSTM+MAPPO | 10 | -0.0157 | [-0.0388, +0.0074] | 0.15771 | 1.00000 | NO CLEAR DIFFERENCE |
| protected W16: LSTM+IPPO - NoHistory+IPPO | 10 | +0.0303 | [+0.0116, +0.0490] | 0.00519 | 0.31672 | NO CLEAR DIFFERENCE |
| protected W16: LSTM+IPPO - OrderFree+IPPO | 10 | -0.0194 | [-0.0569, +0.0180] | 0.27054 | 1.00000 | NO CLEAR DIFFERENCE |
| protected W16: LSTM+IPPO - Transformer+IPPO | 10 | -0.0623 | [-0.0921, -0.0324] | 0.00109 | 0.08056 | NO CLEAR DIFFERENCE |
| protected W64: LSTM+IPPO - LSTM+MAPPO | 10 | -0.0017 | [-0.0266, +0.0232] | 0.87952 | 1.00000 | NO CLEAR DIFFERENCE |
| protected W64: LSTM+IPPO - Transformer+IPPO | 10 | -0.0351 | [-0.0786, +0.0083] | 0.10043 | 1.00000 | NO CLEAR DIFFERENCE |
| protected W16: LSTM+MAPPO - NoHistory+MAPPO | 10 | +0.0026 | [-0.0418, +0.0469] | 0.89857 | 1.00000 | NO CLEAR DIFFERENCE |
| protected W16: LSTM+MAPPO - OrderFree+MAPPO | 10 | -0.0217 | [-0.0677, +0.0243] | 0.31347 | 1.00000 | NO CLEAR DIFFERENCE |
| protected W16: LSTM+MAPPO - Transformer+MAPPO | 10 | -0.0674 | [-0.0938, -0.0411] | 0.00026 | 0.02118 | WORSE |
| protected W64: LSTM+MAPPO - Transformer+MAPPO | 10 | -0.0637 | [-0.0928, -0.0346] | 0.00078 | 0.05942 | NO CLEAR DIFFERENCE |
| protected W16: NoHistory+IPPO - NoHistory+MAPPO | 10 | -0.0434 | [-0.0783, -0.0086] | 0.02006 | 0.96297 | NO CLEAR DIFFERENCE |
| protected W16: NoHistory+IPPO - OrderFree+IPPO | 10 | -0.0497 | [-0.0855, -0.0139] | 0.01196 | 0.62707 | NO CLEAR DIFFERENCE |
| protected W16: NoHistory+IPPO - Transformer+IPPO | 10 | -0.0926 | [-0.1242, -0.0609] | 0.00010 | 0.00799 | WORSE |
| protected W16: NoHistory+MAPPO - OrderFree+MAPPO | 10 | -0.0243 | [-0.0776, +0.0290] | 0.32979 | 1.00000 | NO CLEAR DIFFERENCE |
| protected W16: NoHistory+MAPPO - Transformer+MAPPO | 10 | -0.0700 | [-0.1154, -0.0246] | 0.00682 | 0.38864 | NO CLEAR DIFFERENCE |
| protected W16: OrderFree+IPPO - OrderFree+MAPPO | 10 | -0.0180 | [-0.0483, +0.0123] | 0.21233 | 1.00000 | NO CLEAR DIFFERENCE |
| protected W16: OrderFree+IPPO - Transformer+IPPO | 10 | -0.0429 | [-0.0929, +0.0072] | 0.08464 | 1.00000 | NO CLEAR DIFFERENCE |
| protected W16: OrderFree+MAPPO - Transformer+MAPPO | 10 | -0.0457 | [-0.1039, +0.0125] | 0.10933 | 1.00000 | NO CLEAR DIFFERENCE |
| protected W16: Transformer+IPPO - Transformer+MAPPO | 10 | -0.0209 | [-0.0624, +0.0207] | 0.28528 | 1.00000 | NO CLEAR DIFFERENCE |
| protected W64: Transformer+IPPO - Transformer+MAPPO | 10 | -0.0303 | [-0.0647, +0.0042] | 0.07803 | 1.00000 | NO CLEAR DIFFERENCE |
