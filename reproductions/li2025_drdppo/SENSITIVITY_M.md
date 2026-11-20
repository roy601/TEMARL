# Li 2025 DRD-PPO: sensitivity analysis of the paper's readings (A12)

Declared in DECISIONS.md A12 before any code or run. All 2^8 combinations of the readings M1-M8, each run once
(10 seeds x 500 episodes), on the closed calibration's final setting. Nothing is selected; REPORT.md's verdicts
do not change.

**Result:** Table 3 is not produced by any of these 256 readings of the paper.

- Combinations within 2 points of the real triple (Alg1 28.43, Alg3 55.19, DRD-PPO 97.09): **0 of 256**.
- Within 2 points of the decoys D1-D3: [0, 0, 0].

## The 10 combinations closest to Table 3 (descriptive)

| attacker | ties | alg1 | action | cost | R1 | F score | H links | Alg1 | Alg3 | DRD-PPO | distance |
|---|---|---|---|---|---|---|---|---|---|---|---|
| argmax | real_first | config | joint | final | 100 | none | f_only | 21.76 | 74.82 | 53.60 | 48.18 |
| argmax | real_first | config | joint | final | 100 | host_clone | f_only | 21.76 | 74.82 | 53.60 | 48.18 |
| argmax | real_first | walk | joint | final | 100 | none | f_only | 21.24 | 74.82 | 53.60 | 48.25 |
| argmax | real_first | walk | joint | final | 100 | host_clone | f_only | 21.24 | 74.82 | 53.60 | 48.25 |
| argmax | random | config | joint | final | 10 | none | f_only | 24.70 | 87.78 | 53.78 | 54.33 |
| argmax | random | config | joint | final | 10 | host_clone | f_only | 24.70 | 87.78 | 53.78 | 54.33 |
| argmax | random | walk | joint | final | 10 | none | f_only | 24.10 | 87.78 | 53.78 | 54.37 |
| argmax | random | walk | joint | final | 10 | host_clone | f_only | 24.10 | 87.78 | 53.78 | 54.37 |
| argmax | real_first | walk | joint | final | 100 | none | f_plus_server | 60.06 | 100.00 | 94.60 | 54.91 |
| argmax | real_first | walk | joint | final | 100 | host_clone | f_plus_server | 60.06 | 100.00 | 94.60 | 54.91 |

## Mean of each outcome by reading (over the 128 combinations with that reading)

| reading | value | Alg1 | Alg3 | DRD-PPO |
|---|---|---|---|---|
| attacker | argmax | 41.99 | 90.81 | 40.98 |
| attacker | proportional | 23.76 | 48.56 | 10.67 |
| ties | random | 33.71 | 71.24 | 24.99 |
| ties | real_first | 32.05 | 68.12 | 26.66 |
| alg1 | walk | 32.80 | 69.68 | 25.83 |
| alg1 | config | 32.95 | 69.68 | 25.83 |
| action | single | 33.11 | 69.45 | 23.65 |
| action | joint | 32.64 | 69.91 | 28.00 |
| cost | step | 32.88 | 69.68 | 14.71 |
| cost | final | 32.88 | 69.68 | 36.94 |
| R1 | 10.0 | 32.88 | 69.68 | 18.58 |
| R1 | 100.0 | 32.88 | 69.68 | 33.07 |
| f_score | none | 30.16 | 63.20 | 24.53 |
| f_score | host_clone | 35.59 | 76.16 | 27.12 |
| h_links | f_only | 20.05 | 64.19 | 18.91 |
| h_links | f_plus_server | 45.70 | 75.18 | 32.74 |

Every trial: `out/sensitivity_m_log.csv`; every combination: `out/sensitivity_m.json`.
