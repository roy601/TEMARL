# Independent Review of Completed Lab Results

Source: `G:\Desktop\TMARl_1350\thesis_version_2310_markov_useful\lab_results\results_markov\full_gpu_20261008_013700`

All results below are conditional on the saved fixed split and simulator. Original means source-derived playbook sequences, not real-world attack logs.
Means +/- sample SD are over 10 training seeds; test episodes are repeated evaluations of seven playbooks, not independent campaigns.

## Verdicts

- Checkpoint files were not included in this copy: 720 prediction checkpoint files (final and validation-best), 200 RL policies and 120 confidence policies are missing. This prevents checkpoint hash verification and fresh model inference; saved-result arithmetic remains verifiable.
- Prediction: no Markov dose improved mean Top-1 over either control; some decreases survive Holm correction. This rejects usefulness of this generator under this protocol, not every Markov model.
- Deception: Markov lowers mean dwell and depth in all six combinations against both controls. No downstream contrast survives the 36-test Holm correction; no demonstrated benefit, not proof of universal harm.
- Confidence: no primary dwell contrast survives correction; probability calibration improves without a demonstrated policy benefit.
- Original sequence history is associated with a large engagement advantage over NoHistory; architecture rankings and MAPPO superiority are not established by mean rankings alone.
- Repeated data can improve Top-1 while worsening NLL/perplexity. More optimization is not more independent data, and identical epochs are not identical update budgets.

## Verification

|Check|Pass|Detail|
|---|---|---|
|prediction count|True|360|
|prediction fingerprints|True||
|prediction checkpoint hashes|False|missing=720, mismatches=0|
|rl count|True|200|
|rl fingerprints|True||
|rl checkpoint hashes|False|missing=200, mismatches=0|
|confidence count|True|120|
|confidence fingerprints|True||
|confidence checkpoint hashes|False|missing=120, mismatches=0|
|Local implementation fingerprint|True||
|Source corpus hash|True||
|Saved split reproduced|True||
|Coverage reproduced|True||
|No duplicate input sequences across splits|True||
|Exact prediction cell identities|True||
|Exact RL cell identities|True||
|Exact confidence cell identities|True||
|All encoder epochs complete|True||
|Prediction curve and summary agree|True||
|Test prediction windows|True||
|RL step budgets|True||
|Repeat matched windows and updates|True||
|Confidence parameter counts matched|True||
|Confidence baselines reproduce main RL|True||
|350 matched labeled test episodes per policy|True|0|
|Episode summaries recomputed|True|0.0|
|Episode metric bounds|True|0|
|Independent paired tests and Holm reproduced|True|2.220446049250313e-16|
|Synthetic sequences regenerated from training only|True||
|Calibration provenance|True||

## Prediction Top-1 (%)

|Condition|Transformer|GRU|LSTM|
|---|---|---|---|
|real_25|59.154 +/- 2.508|59.963 +/- 2.933|61.176 +/- 2.320|
|real_50|62.426 +/- 3.576|64.044 +/- 2.925|64.706 +/- 2.623|
|real_75|65.551 +/- 2.583|67.243 +/- 2.090|67.757 +/- 1.201|
|real_100|69.890 +/- 1.325|70.846 +/- 1.214|71.066 +/- 0.814|
|markov_25|69.375 +/- 1.570|70.110 +/- 0.756|70.441 +/- 0.798|
|repeat_25|70.882 +/- 1.235|70.919 +/- 1.181|70.772 +/- 1.288|
|markov_50|68.713 +/- 0.987|70.257 +/- 1.017|70.257 +/- 0.924|
|repeat_50|70.735 +/- 1.322|70.846 +/- 1.041|71.581 +/- 1.097|
|markov_100|67.978 +/- 1.545|70.221 +/- 1.408|70.184 +/- 1.181|
|repeat_100|71.581 +/- 0.966|71.066 +/- 0.918|71.434 +/- 0.521|
|markov_200|65.515 +/- 1.529|69.191 +/- 1.816|68.088 +/- 1.687|
|repeat_200|72.279 +/- 0.779|71.250 +/- 1.247|71.544 +/- 0.698|

## Original-Only Learning Curve: Actual Data Size

|Condition|Original runs (range)|Windows (range)|Optimizer updates (range)|
|---|---|---|---|
|real_25|9 - 9|261 - 311|460 - 460|
|real_50|13 - 13|418 - 460|644 - 736|
|real_75|19 - 19|651 - 665|1012 - 1012|
|real_100|22 - 22|774 - 774|1196 - 1196|
|repeat_100|22 - 22|1461 - 1628|2116 - 2392|
|repeat_200|22 - 22|2172 - 2405|3128 - 3496|

## Prediction Accuracy Versus Probability Quality

|Encoder|Original Top-1 %|Repeat200 Top-1 %|Original NLL|Repeat200 NLL|
|---|---|---|---|---|
|Transformer|69.890 +/- 1.325|72.279 +/- 0.779|1.747 +/- 0.164|2.101 +/- 0.224|
|GRU|70.846 +/- 1.214|71.250 +/- 1.247|1.908 +/- 0.103|2.286 +/- 0.190|
|LSTM|71.066 +/- 0.814|71.544 +/- 0.698|1.943 +/- 0.187|2.307 +/- 0.234|

## Deception Results

|Condition|Encoder|RL|Dwell (steps)|Depth (unique engaged techniques)|Protection %|
|---|---|---|---|---|---|
|real_100|Transformer|IPPO|14.678 +/- 0.505|10.044 +/- 0.588|33.429 +/- 3.136|
|real_100|Transformer|MAPPO|15.047 +/- 0.740|10.227 +/- 0.645|34.543 +/- 5.222|
|real_100|GRU|IPPO|15.313 +/- 0.839|10.476 +/- 0.720|37.286 +/- 6.124|
|real_100|GRU|MAPPO|15.291 +/- 0.767|10.466 +/- 0.643|36.600 +/- 4.239|
|real_100|LSTM|IPPO|15.272 +/- 0.765|10.417 +/- 0.572|38.400 +/- 3.179|
|real_100|LSTM|MAPPO|15.233 +/- 0.340|10.478 +/- 0.292|37.343 +/- 3.127|
|real_100|NoHistory|IPPO|11.263 +/- 0.498|7.766 +/- 0.341|27.657 +/- 2.882|
|real_100|NoHistory|MAPPO|11.529 +/- 0.333|7.876 +/- 0.205|28.886 +/- 2.169|
|markov_100|Transformer|IPPO|14.072 +/- 0.419|9.551 +/- 0.397|35.600 +/- 4.163|
|markov_100|Transformer|MAPPO|14.120 +/- 0.850|9.529 +/- 0.627|35.143 +/- 4.581|
|markov_100|GRU|IPPO|14.016 +/- 0.702|9.555 +/- 0.553|33.771 +/- 4.654|
|markov_100|GRU|MAPPO|14.811 +/- 0.733|10.029 +/- 0.518|35.257 +/- 5.199|
|markov_100|LSTM|IPPO|14.285 +/- 0.645|9.780 +/- 0.555|32.371 +/- 5.670|
|markov_100|LSTM|MAPPO|14.394 +/- 1.264|9.782 +/- 0.860|33.886 +/- 4.319|
|repeat_100|Transformer|IPPO|15.045 +/- 0.861|10.227 +/- 0.729|36.800 +/- 3.730|
|repeat_100|Transformer|MAPPO|15.425 +/- 0.517|10.526 +/- 0.331|36.971 +/- 4.795|
|repeat_100|GRU|IPPO|15.188 +/- 0.537|10.373 +/- 0.492|36.171 +/- 4.504|
|repeat_100|GRU|MAPPO|15.436 +/- 0.702|10.507 +/- 0.566|37.143 +/- 4.710|
|repeat_100|LSTM|IPPO|14.987 +/- 0.893|10.218 +/- 0.651|36.143 +/- 4.776|
|repeat_100|LSTM|MAPPO|15.595 +/- 0.443|10.727 +/- 0.282|39.000 +/- 2.674|

## Markov +100% Minus Original: Deception

|Model|Delta dwell|Delta depth|Delta protection (pp)|
|---|---|---|---|
|Transformer+IPPO|-0.606|-0.493|+2.171|
|Transformer+MAPPO|-0.927|-0.699|+0.600|
|GRU+IPPO|-1.297|-0.921|-3.514|
|GRU+MAPPO|-0.480|-0.437|-1.343|
|LSTM+IPPO|-0.987|-0.637|-6.029|
|LSTM+MAPPO|-0.839|-0.696|-3.457|

## Confidence Dwell Ablation

|Model|Baseline dwell|Confidence dwell|Delta|95% CI|Holm p|
|---|---|---|---|---|---|
|Transformer+IPPO|14.678 +/- 0.505|14.814 +/- 0.721|+0.136|[-0.194, 0.467]|1.00000|
|Transformer+MAPPO|15.047 +/- 0.740|15.042 +/- 0.653|-0.005|[-0.569, 0.558]|1.00000|
|GRU+IPPO|15.313 +/- 0.839|15.179 +/- 0.578|-0.134|[-0.701, 0.433]|1.00000|
|GRU+MAPPO|15.291 +/- 0.767|15.623 +/- 0.642|+0.332|[-0.322, 0.986]|1.00000|
|LSTM+IPPO|15.272 +/- 0.765|14.939 +/- 0.745|-0.333|[-1.161, 0.496]|1.00000|
|LSTM+MAPPO|15.233 +/- 0.340|15.376 +/- 0.448|+0.143|[-0.264, 0.55]|1.00000|

## Calibration (Mean Across Seeds)

|Encoder|Raw test NLL|Scaled test NLL|Raw ECE %|Scaled ECE %|
|---|---|---|---|---|
|Transformer|1.7474|1.5824|10.9897|8.9931|
|GRU|1.9084|1.6538|11.5527|9.4904|
|LSTM|1.9428|1.6700|11.6606|9.8019|

## Significant Prediction Contrasts (Saved Holm Family)

|Contrast|Delta Top-1 (pp)|Holm p|
|---|---|---|
|Transformer: markov_25 minus repeat_25|-1.507|0.0463956|
|Transformer: markov_50 minus repeat_50|-2.022|0.0207890|
|Transformer: markov_100 minus repeat_100|-3.603|0.0036989|
|Transformer: markov_200 minus real_100|-4.375|0.0066327|
|Transformer: markov_200 minus repeat_200|-6.765|0.0000053|
|LSTM: markov_200 minus real_100|-2.978|0.0354570|
|LSTM: markov_200 minus repeat_200|-3.456|0.0067085|

## Interpretation and Audit Limitations

1. The actual loader reads all 36 runs (1,347 steps), split into 22/7/7 runs with 796/272/279 steps. Training contains 79 technique IDs, not the alleged 61-technique seven-summary corpus.
2. The environment is fixed five-zone, not a variable-topology evaluation. No LOSO was run. Test scenarios are S1/S3/S6, variants of training scenarios; maximum train-test bigram Jaccard is 0.90.
3. Exact duplicates are grouped, but distinct sequence hashes do not establish independent campaigns. Ten seeds quantify training randomness, not ten independently sampled datasets.
4. Markov RL changes both pretraining data and the attack replay pool. A 2x2 design is required to separate these mechanisms. Original-only RL already runs by replaying original training runs; Markov is not required for the simulator to run.
5. Pooled order-1 next-step prediction (Top-1 53.676%, PPL 6.653) beats order-0 (14.338%, 127.556), but this is not operational validation of the scenario-conditioned generator. AEP/causal validity was not tested.
6. Repeat controls match window counts and updates, but repeat_windows uses cyclic indexing and truncates its last cycle. This gives early windows one extra copy when counts are not exact multiples. It is not always uniform repetition or exactly equivalent to three ordinary epochs.
7. The 25/50/75/100% curve changes data amount AND updates at fixed epochs. It indicates performance sensitivity, but does not isolate additional information from optimization effort. Actual fractions differ because small scenarios are retained.
8. The pilot cap warning does not prove all models were undertrained. Repetition increases Top-1 but worsens NLL; validate training schedules and checkpoint criteria without selecting them using the already-inspected test set.
9. Reward equals one per engaged step, hence episode_reward and dwell are the same quantity, not independent evidence. Protection means attacker objective not completed before termination, not absence of all asset compromise. Depth counts unique engaged techniques.
10. Confidence is calibrated normalized entropy, not an ensemble of the three encoders and not probability of correctness. Calibration gains need not cause policy gains.
11. Saved source/config fingerprints match the local implementation. Checkpoint hashes are recorded but cannot be verified because the .pt files are absent. Fingerprints alone do not prove timestamped preregistration. Earlier environment/payoff design used the corpus before this split.
12. This review checks saved arithmetic, source hashes, split reconstruction and sequence generation, not a full GPU training reproduction. Simulator-to-real-world validity remains unmeasured.
13. NoHistory is an RL policy without the sequence embedding, NOT a static honeypot. This run does not supply a static-honeypot comparison, and none should be fabricated from NoHistory.
14. Environment tests document an S6 goal fallback rather than a declared goal. Campaign goal provenance therefore has an exception; simulation movement/goal metadata must not all be described as source-observed.

## Additional Tests Run During This Review

- `python -m unittest test_markov_study test_confidence test_bundle`: 35 tests passed.
- `python tests_marl.py`: 27/27 environment checks passed.
- These are CPU integrity/smoke tests, not retraining the full lab study.

## Next Steps

1. Copy the final/best encoder and policy .pt files from the lab PC before deleting or moving the original run. They may have been omitted by Git ignore rules; confirm on the lab PC.
2. Use original-only training as the supported default for this setup; preserve Markov and confidence results as negative/ inconclusive ablations.
3. Validate an optimizer-update budget and checkpoint criterion, with balanced repeated sampling if used. Do not call repeat_200 new independent data or claim its advantage proves all original models undertrained.
4. Separate encoder augmentation and RL episode augmentation in a crossed study only if mechanism attribution is needed.
5. Use scenario-held-out or external-corpus validation to extend claims beyond similar known-scenario variants. Do not retrofit preregistration or claim statistical equivalence from nonsignificant tests.
