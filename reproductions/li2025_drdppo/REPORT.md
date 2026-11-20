# Li 2025 DRD-PPO: report (calibrated replication)

Written by `report.py` from `out/`. Protocol: DECISIONS.md (decisions 1-16, C1-C9, A1-A11). Rebuilt from the
paper (no code released); unpublished parameters calibrated on Table 3 Alg1, Alg3 and DRD-PPO; Alg2 and
Table 4 DRD-PPO held out and computed once.

**Overall:** **Not reproducible from the published text.** No declared setting came within 2 points of the calibration targets (best: Alg1 3.46 vs 28.43, Alg3 87.90 vs 55.19, DRD-PPO 0.34 vs 97.09, over 24 + 12 settings), and the held-out targets are uninformative (A2). The paper's unpublished mechanics cannot be recovered without the authors' simulator (A11). DRD-PPO enters D1.2 only as an adapted comparator (A4).

Primary targets: T3.DRD-PPO, T4.DRD-PPO. Trials logged: 910 (`out/calibration_log.csv`).

\* 95% t-interval clipped to [0, 100].

| id | table | published | ours: mean [95% CI], 10 seeds | role and notes | verdict |
|---|---|---|---|---|---|
| T3.DRD-PPO | Table 3 | 97.09 | 0.34 [0.00, 0.72]* | calibration target, stage 2 (C3); distance 96.75 | CALIBRATION TARGET |
| T3.Alg1_random_deployment | Table 3 | 28.43 | 3.46 [2.78, 4.14] | calibration target, stage 1 (C2); distance 24.97 | CALIBRATION TARGET |
| T3.Alg2_intelligent_full_deployment | Table 3 | 98.31 | 88.90 [86.24, 91.56] | held out (C4); evaluation DSP 89.76 [85.56, 93.96]; references scripted 100.00, random_init 87.34; a reference policy is within 2 points of the published value (A2) | UNINFORMATIVE |
| T3.Alg3_random_full_deployment | Table 3 | 55.19 | 87.90 [86.49, 89.31] | calibration target, stage 1 (C2); distance 32.71 | CALIBRATION TARGET |
| T4.DRD-PPO | Table 4 | 98.61 | 0.11 [0.00, 0.24]* | held out (C4); evaluation DSP 0.00 [0.00, 0.00]; references scripted 100.00, random_init 3.23; a reference policy is within 2 points of the published value (A2) | UNINFORMATIVE |
| T4.DRD-Q | Table 4 | 95.32 | - | no setting of this algorithm is published (decision 14) | NOT ATTEMPTED |
| T4.DRD-AC | Table 4 | 66.85 | - | no setting of this algorithm is published (decision 14) | NOT ATTEMPTED |
| T4.DRD-DQN | Table 4 | 64.28 | - | no setting of this algorithm is published (decision 14) | NOT ATTEMPTED |
| T4.DRD-SAC | Table 4 | 78.89 | - | no setting of this algorithm is published (decision 14) | NOT ATTEMPTED |
| T4.DRD-PG | Table 4 | 87.13 | - | no setting of this algorithm is published (decision 14) | NOT ATTEMPTED |
| T4.DRD-DDQN | Table 4 | 53.24 | - | no setting of this algorithm is published (decision 14) | NOT ATTEMPTED |

## Calibration

- Stage 1 (environment, 24 settings): selected `w=0.1|links=P1|timing=last|cvss=v2|h_links=f_only|R1=10.0|R2=0.0|clip=0.2`, loss 1693.44. Settings within 2 points of both targets: 0 (C5).
- Stage 2 (learner, 12 settings): selected `w=0.1|links=P1|timing=last|cvss=v2|h_links=f_only|R1=10.0|R2=0.5|clip=0.9`. Settings within 2 points of 97.09: 0 (C5).
- Discrimination (review attack 2): number of stage-1 settings in which the scripted policy is within 2 points of each held-out target: {'T3.Alg2_intelligent_full_deployment': 12, 'T4.DRD-PPO': 12}.
- w is weakly identified by construction: it scales both sides of the H-honeypot-versus-server comparison (DECISIONS.md F2).

## Sensitivity

- CVSS v3 instead of v2 (final setting, DRD-PPO, 500 episodes): 0.34 [0.00, 0.72]*.
- Clip 0.9 (Table 2) versus 0.2 (text): both are in the stage-2 grid; see `out/stage2.json`.

## Readings of the paper (A12, declared sensitivity analysis)

- Table 3 is not produced by any of these 256 readings of the paper. Combinations fitting Table 3 within 2 points: 0 of 256; decoys fitted: [0, 0, 0] (`SENSITIVITY_M.md`).
- Ranges over the 256 readings: Alg1 2.10-82.34, Alg3 32.16-100.00, DRD-PPO 0.34-94.60. No reading reaches Alg3 55.19 or DRD-PPO 97.09 within 2 points, even alone.

## What the paper's own figures imply (A13-A14, algebra only)

Plateaus measured from Figs. 5-6 (`data/figure_values.json`). Under reward = R1(2p - 1) - cost with R1 = 1 and
the cost once per episode (recovered from two independent plateaus: 0.996 and 0.997):

| method | cost (Fig. 6c) | implied success | Table 3 |
|---|---|---|---|
| DRD-PPO | 0.912 | 99.82% | 97.09 |
| Alg1 | 1.534 | 31.20% | 28.43 |
| Alg2 | 1.901 | 99.85% | 98.31 |
| Alg3 | 1.901 | 57.52% | 55.19 |

- The figures and Table 3 agree (gaps +1.5 to +2.8 points); DRD-PPO's learned deployment is 1 H + 4 F.
- No attacker rule we derived reproduces the figure-implied random baselines (31.20%, 57.52%): clone-specific
  36.17% / 66.41%, all honeypots 60.83% / 100% (exact arithmetic). A13's run was therefore not executed (A14).

## Limits

- Every unpublished setting is an assumption (DECISIONS.md decisions 5-11, A6-A9); the corresponding author did
  not answer. A calibrated match is weaker evidence than a replication with the authors' settings.
- DSP is primarily measured over training episodes (decision 12); the evaluation DSP is reported alongside.
- The six other RL algorithms of Table 4 are not attempted (decision 14).
