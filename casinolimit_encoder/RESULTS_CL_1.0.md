# CasinoLimit results (protocol CL 1.0), opened once on 2026-11-13

Full numbers: `out_test/CL_RESULTS.txt` (every condition and subset), per attacker:
`out_test/CL_RESULTS_PER_ATTACKER.csv`. Validation dry run before opening: PASS (largest difference
5.55e-17, `out/DRY_RUN_VALIDATION.txt`). Frozen files unchanged (`spec_cl.py` PASS).

## Primary result (main condition, all 8,087 test points, 113 attackers)

| model | micro-F1 | per-attacker micro-F1 | macro-F1 | exact set |
|---|---|---|---|---|
| Transformer (allpos) | 0.328 | 0.287 | 0.059 | 0.188 |
| GRU | 0.337 | 0.287 | 0.053 | 0.202 |
| LSTM | 0.333 | 0.285 | 0.053 | 0.200 |
| Old Transformer (descriptive) | 0.330 | 0.294 | 0.064 | 0.195 |
| Best simple baseline (chosen per fold on validation) | 0.281 | 0.268 | 0.106 | 0.248 |
| Repeat last step | 0.295 | 0.284 | 0.163 | 0.260 |

| comparison (per attacker) | mean difference [95% CI] | Holm p | verdict |
|---|---|---|---|
| Transformer − best simple baseline | +0.018 [−0.006, +0.036] | <0.0001 | no difference shown |
| GRU − best simple baseline | +0.019 [−0.006, +0.038] | 0.0001 | no difference shown |
| LSTM − best simple baseline | +0.016 [−0.008, +0.035] | 0.0002 | no difference shown |
| Transformer − GRU | −0.001 [−0.008, +0.007] | 0.78 | no difference shown |
| Transformer − LSTM | +0.002 [−0.006, +0.009] | 0.78 | no difference shown |

The encoders are ahead in about two thirds of attackers and the Wilcoxon p-values are small, but the
95% CI includes 0, so the pre-registered rule says "no difference shown".

## Other subsets and the second condition (secondary)

- **Novel points** (main, 7,919): all three encoders **outperform** the best simple baseline
  (+0.029 to +0.032, CI above 0, Holm p ≤ 0.0001). Transformer vs GRU / LSTM: no difference shown.
- **Copy points** (main, 168): the Transformer outperforms GRU and LSTM; vs the baseline no
  difference shown. Very few points.
- **Reviewed labels only** (main, 3,746): vs the baseline no difference shown; the Transformer
  outperforms GRU (+0.012) and LSTM (+0.014).
- **collapse_repeats** (repeats removed): vs the baseline no difference shown on all and novel
  points; on reviewed points the **best simple baseline outperforms** all three encoders (−0.029
  to −0.038). The Transformer outperforms GRU and LSTM on all, novel and reviewed points (+0.008 to
  +0.013).

## Plain reading

1. On new human attackers, the encoders are **not shown** to beat the best simple rule overall. They
   do beat it on the points that are not copies of training windows.
2. The simple rules have **higher macro-F1 and exact-set accuracy** than the encoders: the encoders
   predict mostly frequent techniques.
3. "Repeat last step" alone scores higher on test (0.295) than the comparator chosen on validation
   (0.281). The comparator rule is fixed by the protocol and is not changed after the result.
4. Transformer vs GRU / LSTM: tied on the primary result, as on CAM-LDS; the Transformer is ahead
   in several secondary subsets.
