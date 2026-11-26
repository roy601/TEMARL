# H-MARL (Singh et al., RLJ 2025): reproduction of Tables 2 and 3 from the released policies

**Paper verdict: partially reproduced; attempted primary targets not MATCH: T2.HMARL_Expert.Default.mean, T3.HMARL_Expert.mean_time_to_recover, T3.HMARL_Expert.red_impact_count, T3.HMARL_Meta.clean_hosts, T3.HMARL_Meta.mean_time_to_recover, T3.HMARL_Meta.useful_recoveries, T3.HMARL_Meta.wasted_recoveries, T3.HMARL_Meta.red_impact_count, T3.MARL_Decentralized.mean_time_to_recover, T3.MARL_Decentralized.useful_recoveries, T3.MARL_Decentralized.wasted_recoveries, T3.MARL_Decentralized.red_impact_count.**

- Targets: 64; MATCH 17, CLOSE 9, NO MATCH 4, NOT ATTEMPTED 34. Attempted: the three methods whose trained policies were released, against Default Red (DECISIONS 3); every other cell is NOT ATTEMPTED with its reason below.
- Each method is one released policy, so the intervals cover evaluation randomness only (DECISIONS 8): 10 seeds x 100 episodes; CI = t over the 10 seed values; prediction interval = where one 100-episode evaluation (as one published table entry) is expected to fall.
- The authors' evaluator ran unchanged; with its metrics switch on, it gives the same rewards as their plain evaluator (`out/VERIFY.json`: HMARL_Expert PASS, HMARL_Meta PASS, MARL_Decentralized PASS).

## Reward against Default Red (Table 2), per method

| method | published mean ± std | ours: mean [95% CI] | our seed values (range) | our episode std | verdict |
|---|---|---|---|---|---|
| HMARL_Expert | -129.53 ± 44.6 | -136.41 [-140.09, -132.73] | -145.22 to -128.91 | 51.56 | CLOSE |
| HMARL_Meta | -181.62 ± 65.85 | -184.11 [-187.16, -181.05] | -190.07 to -177.21 | 73.46 | MATCH |
| MARL_Decentralized | -179.8 ± 92.98 | -178.80 [-183.54, -174.05] | -188.91 to -171.01 | 76.46 | MATCH |

## Every target

| id | table | quantity | published | ours [95% CI] | 95% prediction interval | verdict |
|---|---|---|---|---|---|---|
| T2.MARL_Decentralized.Default.mean | Table 2 | MARL_Decentralized, Default Red: mean evaluation reward, 100 episodes (published std 92.98) (primary) | -179.8 | -178.799 [-183.544, -174.054] | [-194.537, -163.061] | MATCH |
| T2.MARL_Decentralized.Stealthy.mean | Table 2 | MARL_Decentralized, Stealthy Red: mean evaluation reward, 100 episodes (published std 53.45) (this red agent is not in the released code (DECISIONS 3)) | -165.8 | - | - | NOT ATTEMPTED |
| T2.MARL_Decentralized.Aggressive.mean | Table 2 | MARL_Decentralized, Aggressive Red: mean evaluation reward, 100 episodes (published std 87.98) (this red agent is not in the released code (DECISIONS 3)) | -227.93 | - | - | NOT ATTEMPTED |
| T2.MARL_Decentralized.Impact.mean | Table 2 | MARL_Decentralized, Impact Red: mean evaluation reward, 100 episodes (published std 71.53) (this red agent is not in the released code (DECISIONS 3)) | -247.15 | - | - | NOT ATTEMPTED |
| T2.MARL_Centralized_Critic.Default.mean | Table 2 | MARL_Centralized_Critic, Default Red: mean evaluation reward, 100 episodes (published std 132.98) (no trained policy released for this method (DECISIONS 3)) | -245.66 | - | - | NOT ATTEMPTED |
| T2.MARL_Centralized_Critic.Stealthy.mean | Table 2 | MARL_Centralized_Critic, Stealthy Red: mean evaluation reward, 100 episodes (published std 115.06) (no trained policy released for this method (DECISIONS 3)) | -217.52 | - | - | NOT ATTEMPTED |
| T2.MARL_Centralized_Critic.Aggressive.mean | Table 2 | MARL_Centralized_Critic, Aggressive Red: mean evaluation reward, 100 episodes (published std 138.70) (no trained policy released for this method (DECISIONS 3)) | -255.98 | - | - | NOT ATTEMPTED |
| T2.MARL_Centralized_Critic.Impact.mean | Table 2 | MARL_Centralized_Critic, Impact Red: mean evaluation reward, 100 episodes (published std 108.13) (no trained policy released for this method (DECISIONS 3)) | -332.96 | - | - | NOT ATTEMPTED |
| T2.HMARL_Collective.Default.mean | Table 2 | HMARL_Collective, Default Red: mean evaluation reward, 100 episodes (published std 102.6) (no trained policy released for this method (DECISIONS 3)) | -237.61 | - | - | NOT ATTEMPTED |
| T2.HMARL_Collective.Stealthy.mean | Table 2 | HMARL_Collective, Stealthy Red: mean evaluation reward, 100 episodes (published std 83.24) (no trained policy released for this method (DECISIONS 3)) | -204.18 | - | - | NOT ATTEMPTED |
| T2.HMARL_Collective.Aggressive.mean | Table 2 | HMARL_Collective, Aggressive Red: mean evaluation reward, 100 episodes (published std 120.50) (no trained policy released for this method (DECISIONS 3)) | -282.5 | - | - | NOT ATTEMPTED |
| T2.HMARL_Collective.Impact.mean | Table 2 | HMARL_Collective, Impact Red: mean evaluation reward, 100 episodes (published std 115.25) (no trained policy released for this method (DECISIONS 3)) | -350.21 | - | - | NOT ATTEMPTED |
| T2.HMARL_Expert.Default.mean | Table 2 | HMARL_Expert, Default Red: mean evaluation reward, 100 episodes (published std 44.60) (primary) | -129.53 | -136.409 [-140.091, -132.727] | [-148.620, -124.198] | CLOSE |
| T2.HMARL_Expert.Stealthy.mean | Table 2 | HMARL_Expert, Stealthy Red: mean evaluation reward, 100 episodes (published std 38.28) (this red agent is not in the released code (DECISIONS 3)) | -99.54 | - | - | NOT ATTEMPTED |
| T2.HMARL_Expert.Aggressive.mean | Table 2 | HMARL_Expert, Aggressive Red: mean evaluation reward, 100 episodes (published std 37.74) (this red agent is not in the released code (DECISIONS 3)) | -118.16 | - | - | NOT ATTEMPTED |
| T2.HMARL_Expert.Impact.mean | Table 2 | HMARL_Expert, Impact Red: mean evaluation reward, 100 episodes (published std 64.04) (this red agent is not in the released code (DECISIONS 3)) | -173.17 | - | - | NOT ATTEMPTED |
| T2.HMARL_Meta.Default.mean | Table 2 | HMARL_Meta, Default Red: mean evaluation reward, 100 episodes (published std 65.85) (primary) | -181.62 | -184.106 [-187.165, -181.047] | [-194.250, -173.962] | MATCH |
| T2.HMARL_Meta.Stealthy.mean | Table 2 | HMARL_Meta, Stealthy Red: mean evaluation reward, 100 episodes (published std 91.40) (this red agent is not in the released code (DECISIONS 3)) | -184.76 | - | - | NOT ATTEMPTED |
| T2.HMARL_Meta.Aggressive.mean | Table 2 | HMARL_Meta, Aggressive Red: mean evaluation reward, 100 episodes (published std 86.48) (this red agent is not in the released code (DECISIONS 3)) | -207.66 | - | - | NOT ATTEMPTED |
| T2.HMARL_Meta.Impact.mean | Table 2 | HMARL_Meta, Impact Red: mean evaluation reward, 100 episodes (published std 97.76) (this red agent is not in the released code (DECISIONS 3)) | -278.78 | - | - | NOT ATTEMPTED |
| T2.HMARL_Meta_finetuned.Default.mean | Table 2 | HMARL_Meta_finetuned, Default Red: mean evaluation reward, 100 episodes (published std 81.28) (no trained policy released for this method (DECISIONS 3)) | -186.24 | - | - | NOT ATTEMPTED |
| T2.HMARL_Meta_finetuned.Stealthy.mean | Table 2 | HMARL_Meta_finetuned, Stealthy Red: mean evaluation reward, 100 episodes (published std 57.97) (no trained policy released for this method (DECISIONS 3)) | -162.51 | - | - | NOT ATTEMPTED |
| T2.HMARL_Meta_finetuned.Impact.mean | Table 2 | HMARL_Meta_finetuned, Impact Red: mean evaluation reward, 100 episodes (published std 81.53) (no trained policy released for this method (DECISIONS 3)) | -264.96 | - | - | NOT ATTEMPTED |
| T3.HMARL_Expert.clean_hosts | Table 3 | HMARL_Expert, Default Red: clean_hosts, 100-episode average (primary) | 0.81 | 0.809 [0.805, 0.813] | [0.796, 0.822] | MATCH |
| T3.HMARL_Expert.non_escalated_hosts | Table 3 | HMARL_Expert, Default Red: non_escalated_hosts, 100-episode average (primary) | 0.99 | 0.990 [0.990, 0.990] | [0.990, 0.990] | MATCH |
| T3.HMARL_Expert.mean_time_to_recover | Table 3 | HMARL_Expert, Default Red: mean_time_to_recover, 100-episode average (primary) | 44.76 | 45.598 [44.958, 46.238] | [43.476, 47.720] | CLOSE |
| T3.HMARL_Expert.useful_recoveries | Table 3 | HMARL_Expert, Default Red: useful_recoveries, 100-episode average (primary) | 6.07 | 6.074 [6.013, 6.135] | [5.873, 6.275] | MATCH |
| T3.HMARL_Expert.wasted_recoveries | Table 3 | HMARL_Expert, Default Red: wasted_recoveries, 100-episode average (primary) | 2.2 | 2.046 [1.859, 2.233] | [1.425, 2.667] | MATCH |
| T3.HMARL_Expert.recovery_precision | Table 3 | HMARL_Expert, Default Red: recovery_precision, 100-episode average (primary) | 0.73 | 0.749 [0.732, 0.766] | [0.693, 0.804] | MATCH |
| T3.HMARL_Expert.recovery_error | Table 3 | HMARL_Expert, Default Red: recovery_error, 100-episode average | 0.27 | 0.251 [0.234, 0.268] | [0.196, 0.307] | MATCH |
| T3.HMARL_Expert.red_impact_count | Table 3 | HMARL_Expert, Default Red: red_impact_count, 100-episode average (primary) | 0.88 | 3.690 [3.229, 4.151] | [2.161, 5.219] | NO MATCH |
| T3.HMARL_Expert.reward | Table 3 | HMARL_Expert, Default Red: reward (published std 44.60, from Table 2) | -129.53 | -136.409 [-140.091, -132.727] | [-148.620, -124.198] | CLOSE |
| T3.HMARL_Meta.clean_hosts | Table 3 | HMARL_Meta, Default Red: clean_hosts, 100-episode average (primary) | 0.77 | 0.779 [0.777, 0.781] | [0.771, 0.787] | CLOSE |
| T3.HMARL_Meta.non_escalated_hosts | Table 3 | HMARL_Meta, Default Red: non_escalated_hosts, 100-episode average (primary) | 0.97 | 0.970 [0.970, 0.970] | [0.970, 0.970] | MATCH |
| T3.HMARL_Meta.mean_time_to_recover | Table 3 | HMARL_Meta, Default Red: mean_time_to_recover, 100-episode average (primary) | 62.63 | 60.654 [59.705, 61.603] | [57.506, 63.802] | CLOSE |
| T3.HMARL_Meta.useful_recoveries | Table 3 | HMARL_Meta, Default Red: useful_recoveries, 100-episode average (primary) | 5.79 | 5.572 [5.508, 5.636] | [5.360, 5.784] | NO MATCH |
| T3.HMARL_Meta.wasted_recoveries | Table 3 | HMARL_Meta, Default Red: wasted_recoveries, 100-episode average (primary) | 3.74 | 3.410 [3.267, 3.553] | [2.934, 3.886] | CLOSE |
| T3.HMARL_Meta.recovery_precision | Table 3 | HMARL_Meta, Default Red: recovery_precision, 100-episode average (primary) | 0.61 | 0.621 [0.612, 0.629] | [0.592, 0.649] | MATCH |
| T3.HMARL_Meta.recovery_error | Table 3 | HMARL_Meta, Default Red: recovery_error, 100-episode average | 0.39 | 0.379 [0.371, 0.388] | [0.351, 0.408] | MATCH |
| T3.HMARL_Meta.red_impact_count | Table 3 | HMARL_Meta, Default Red: red_impact_count, 100-episode average (primary) | 1.14 | 2.552 [2.229, 2.875] | [1.480, 3.624] | NO MATCH |
| T3.HMARL_Meta.reward | Table 3 | HMARL_Meta, Default Red: reward (published std 65.85, from Table 2) | -181.62 | -184.106 [-187.165, -181.047] | [-194.250, -173.962] | MATCH |
| T3.HMARL_Collective.clean_hosts | Table 3 | HMARL_Collective, Default Red: clean_hosts (no trained policy released for this method (DECISIONS 3)) | 0.85 | - | - | NOT ATTEMPTED |
| T3.HMARL_Collective.non_escalated_hosts | Table 3 | HMARL_Collective, Default Red: non_escalated_hosts (no trained policy released for this method (DECISIONS 3)) | 0.97 | - | - | NOT ATTEMPTED |
| T3.HMARL_Collective.mean_time_to_recover | Table 3 | HMARL_Collective, Default Red: mean_time_to_recover (no trained policy released for this method (DECISIONS 3)) | 35.52 | - | - | NOT ATTEMPTED |
| T3.HMARL_Collective.useful_recoveries | Table 3 | HMARL_Collective, Default Red: useful_recoveries (no trained policy released for this method (DECISIONS 3)) | 3.41 | - | - | NOT ATTEMPTED |
| T3.HMARL_Collective.wasted_recoveries | Table 3 | HMARL_Collective, Default Red: wasted_recoveries (no trained policy released for this method (DECISIONS 3)) | 5.79 | - | - | NOT ATTEMPTED |
| T3.HMARL_Collective.recovery_precision | Table 3 | HMARL_Collective, Default Red: recovery_precision (no trained policy released for this method (DECISIONS 3)) | 0.37 | - | - | NOT ATTEMPTED |
| T3.HMARL_Collective.recovery_error | Table 3 | HMARL_Collective, Default Red: recovery_error (no trained policy released for this method (DECISIONS 3)) | 0.63 | - | - | NOT ATTEMPTED |
| T3.HMARL_Collective.red_impact_count | Table 3 | HMARL_Collective, Default Red: red_impact_count (no trained policy released for this method (DECISIONS 3)) | 1.93 | - | - | NOT ATTEMPTED |
| T3.HMARL_Collective.reward | Table 3 | HMARL_Collective, Default Red: reward (no trained policy released for this method (DECISIONS 3)) | -255.56 | - | - | NOT ATTEMPTED |
| T3.MARL_Decentralized.clean_hosts | Table 3 | MARL_Decentralized, Default Red: clean_hosts, 100-episode average (primary) | 0.77 | 0.777 [0.774, 0.780] | [0.766, 0.788] | MATCH |
| T3.MARL_Decentralized.non_escalated_hosts | Table 3 | MARL_Decentralized, Default Red: non_escalated_hosts, 100-episode average (primary) | 0.97 | 0.970 [0.970, 0.970] | [0.970, 0.970] | MATCH |
| T3.MARL_Decentralized.mean_time_to_recover | Table 3 | MARL_Decentralized, Default Red: mean_time_to_recover, 100-episode average (primary) | 56.08 | 53.949 [53.031, 54.867] | [50.905, 56.993] | CLOSE |
| T3.MARL_Decentralized.useful_recoveries | Table 3 | MARL_Decentralized, Default Red: useful_recoveries, 100-episode average (primary) | 10.45 | 10.247 [10.094, 10.400] | [9.741, 10.753] | CLOSE |
| T3.MARL_Decentralized.wasted_recoveries | Table 3 | MARL_Decentralized, Default Red: wasted_recoveries, 100-episode average (primary) | 27.99 | 28.275 [28.043, 28.507] | [27.506, 29.044] | CLOSE |
| T3.MARL_Decentralized.recovery_precision | Table 3 | MARL_Decentralized, Default Red: recovery_precision, 100-episode average (primary) | 0.27 | 0.266 [0.262, 0.270] | [0.254, 0.278] | MATCH |
| T3.MARL_Decentralized.recovery_error | Table 3 | MARL_Decentralized, Default Red: recovery_error, 100-episode average | 0.73 | 0.734 [0.730, 0.738] | [0.722, 0.746] | MATCH |
| T3.MARL_Decentralized.red_impact_count | Table 3 | MARL_Decentralized, Default Red: red_impact_count, 100-episode average (primary) | 1.54 | 3.045 [2.852, 3.238] | [2.406, 3.684] | NO MATCH |
| T3.MARL_Decentralized.reward | Table 3 | MARL_Decentralized, Default Red: reward (published std 92.98, from Table 2) | -180 | -178.799 [-183.544, -174.054] | [-194.537, -163.061] | MATCH |
| S42.gain_history_pct | Section 4.2 | Figure 4 / Section 4.2: reward gain from observation history (%) (needs retraining (DECISIONS 10)) | 12 | - | - | NOT ATTEMPTED |
| S42.gain_iocs_pct | Section 4.2 | Section 4.2: further reward gain from malicious-file IOCs (%) (needs retraining (DECISIONS 10)) | 42 | - | - | NOT ATTEMPTED |
| S42.gain_decoys_pct | Section 4.2 | Section 4.2: further reward gain from decoy accesses (%) (needs retraining (DECISIONS 10)) | 11 | - | - | NOT ATTEMPTED |
| S51.meta_speedup_min | Section 5.1 | Section 5.1 / Figure 5: H-MARL Meta converges at least this many times faster (needs retraining (DECISIONS 10)) | 3 | - | - | NOT ATTEMPTED |
| S51.meta_speedup_max | Section 5.1 | Section 5.1 / Figure 5: ... at most this many times faster (needs retraining (DECISIONS 10)) | 5 | - | - | NOT ATTEMPTED |

## Notes

- Inconsistency in the paper, found before any run (DECISIONS 11): H-MARL Collective against Default Red is -237.61 in Table 2 and -255.56 in Table 3. Not attempted (no released policy).
- Red Impact Count is our reading of the paper's definition (DECISIONS 7): per episode, the sum over red agents of their Impact counts on operational hosts; asked of the authors.

## Checklist (STANDARD.md, Section 2)

| # | requirement | met? | where |
|---|---|---|---|
| 1 | targets committed before any result | yes | `audit.py` ORDER |
| 2 | gaps decided before the run | yes | `DECISIONS.md` 1-13 |
| 3 | authors asked about every gap | **not yet**: the issue is drafted, to be posted by the user | `AUTHOR_CONTACT.md` |
| 4 | exact sources and licence | yes | `SOURCES.md`; 87 policy and code files pinned (`POLICY_SHA256.txt`) |
| 5 | variance: two machines identical, or 10+ seeds with CI | partly: one released policy per method, so no training seeds (DECISIONS 8); 10 evaluation seeds with a 95% CI; **second machine not yet** | `out/RECHECK_*.json` |
| 6 | every target reported | yes | table above, `audit.py` |
| 7 | environment recorded | yes | `out/ENVIRONMENT.json` |
| 8 | one command from public inputs, outputs hashed | yes: a fixed sequence of commands (`README.md`); every output's SHA-256 in `out/HASHES.txt` | `fetch.py`, `run.py` |
| 9 | unit tests for each rule | yes: parsing, statistics, verdict rule, target ids, pins | `tests/test_hmarl.py` |
| 10 | comparison only after this report; adaptations declared | not started | DECISIONS 1 |

## Environment

- Python 3.10.22, Windows-10-10.0.26100-SP0, machine DESKTOP-Q1DMJ51; commits {'Hierarchical-MARL': '6fe960f5931f2d7dc5ef522f09ca4a179f377ee4', 'cage-challenge-4': '8c3c50ca54b176c2de199847944e8dcc035497e3'}; full package list in `out/ENVIRONMENT.json`.
- Rechecks (kept episodes run again): none yet.
- Every output's SHA-256 (LF line endings): `out/HASHES.txt`; the authors' printed output of every run: `out/logs/`.
