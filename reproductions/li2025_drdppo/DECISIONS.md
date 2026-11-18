# Decisions

Written 2026-11-16 after reading the result tables only. **The full method decisions (network of Table 1, parameters of Table 2, attacker model, reward, the six RL algorithms' settings) are written after a full read and BEFORE any run.**

| # | gap | choice | why | decided on |
|---|---|---|---|---|
| 1 | Targets | Table 3 (4 methods, 500 confrontations) and Table 4 (7 RL algorithms, 1500 confrontations) | the paper's only numeric results | 2026-11-16 |
| 2 | Seeds | 10 seeds; the paper states none | STANDARD.md requirement 5 | 2026-11-16 |

## Inconsistencies recorded

1. Table 4 is captioned "Comparison of DSP of four methods" but lists seven algorithms.
2. The conclusion says DRD-PPO "improves defensive success probability by at least 3.29%" over other RL methods; 98.61 - 95.32 = 3.29 percentage points (absolute), not a relative percentage.
