# CAGE 4 (Kiely et al., AI Magazine 2025), Table 3: the two teams that released code

**Paper verdict: partially reproduced: Teampunch CC4 CLOSE; Teamcybermonic CC4 MATCH.** Teams UC and lancer released no code, and the environment provides none of the
five variations: those 20 targets are NOT ATTEMPTED. Released code and weights, unchanged (DECISIONS 7, 15).
Each team is one fixed policy, so the intervals cover evaluation randomness only (DECISIONS 10).

## Teamcybermonic, scenario CC4

- Ours: mean **-190.3** over 1000 episodes (10 seeds x 100); 95% CI over the seed means [-195.4, -185.2]; episode-level CI [-194.1, -186.5]; episode std 61.7.
- Published (Table 3): -193 ± 84, one 100-episode evaluation. Verdict: **MATCH**.
- Each seed, mean ± std of its 100 episodes (each comparable to one Table 3 entry): s0 -189.2 ± 71.7; s1 -192.5 ± 72.2; s2 -174.9 ± 50.1; s3 -184.4 ± 60.0; s4 -196.0 ± 61.9; s5 -194.7 ± 65.5; s6 -194.7 ± 64.8; s7 -193.0 ± 57.8; s8 -198.5 ± 58.5; s9 -184.8 ± 49.6.
- Added after the results, descriptive (no verdict changes): Table 3 is ONE 100-episode evaluation. Our ten 100-episode evaluations range over [-198.5, -174.9]; the published -193 is inside that range, and 5 of 10 are at least as good. Table 3 appears to truncate the teams' leaderboard scores (Teamcybermonic README: -193.68); against -193.68, 6 of 10 are at least as good.

## Teampunch, scenario CC4

- Ours: mean **-150.1** over 1000 episodes (10 seeds x 100); 95% CI over the seed means [-153.9, -146.2]; episode-level CI [-152.7, -147.4]; episode std 42.1.
- Published (Table 3): -142 ± 44, one 100-episode evaluation. Verdict: **CLOSE**.
- Each seed, mean ± std of its 100 episodes (each comparable to one Table 3 entry): s0 -157.8 ± 44.2; s1 -148.3 ± 42.6; s2 -157.9 ± 46.2; s3 -150.7 ± 39.0; s4 -152.0 ± 44.5; s5 -153.9 ± 45.7; s6 -145.2 ± 37.2; s7 -142.3 ± 39.9; s8 -146.8 ± 38.9; s9 -145.6 ± 40.4.
- Added after the results, descriptive (no verdict changes): Table 3 is ONE 100-episode evaluation. Our ten 100-episode evaluations range over [-157.9, -142.3]; the published -142 is outside that range, and 0 of 10 are at least as good. Table 3 appears to truncate the teams' leaderboard scores (Teampunch README: -142.72); against -142.72, 1 of 10 are at least as good.

## Every target

| id | quantity | published | ours | difference | verdict |
|---|---|---|---|---|---|
| T3.TeamUC.CC4 | mean episode reward (no code released by this team (DECISIONS 3, 6, 15)) | -113 | - | - | NOT ATTEMPTED |
| T3.TeamUC.constant_network_size | mean episode reward (no code released by this team (DECISIONS 3, 6, 15)) | -101 | - | - | NOT ATTEMPTED |
| T3.TeamUC.improved_decoy_detection | mean episode reward (no code released by this team (DECISIONS 3, 6, 15)) | -138 | - | - | NOT ATTEMPTED |
| T3.TeamUC.increased_phishing | mean episode reward (no code released by this team (DECISIONS 3, 6, 15)) | -534 | - | - | NOT ATTEMPTED |
| T3.TeamUC.stealthy_red | mean episode reward (no code released by this team (DECISIONS 3, 6, 15)) | -153 | - | - | NOT ATTEMPTED |
| T3.TeamUC.aggressive_red | mean episode reward (no code released by this team (DECISIONS 3, 6, 15)) | -508 | - | - | NOT ATTEMPTED |
| T3.Teamlancer.CC4 | mean episode reward (no code released by this team (DECISIONS 3, 6, 15)) | -118 | - | - | NOT ATTEMPTED |
| T3.Teamlancer.constant_network_size | mean episode reward (no code released by this team (DECISIONS 3, 6, 15)) | -71 | - | - | NOT ATTEMPTED |
| T3.Teamlancer.improved_decoy_detection | mean episode reward (no code released by this team (DECISIONS 3, 6, 15)) | -151 | - | - | NOT ATTEMPTED |
| T3.Teamlancer.increased_phishing | mean episode reward (no code released by this team (DECISIONS 3, 6, 15)) | -232 | - | - | NOT ATTEMPTED |
| T3.Teamlancer.stealthy_red | mean episode reward (no code released by this team (DECISIONS 3, 6, 15)) | -871 | - | - | NOT ATTEMPTED |
| T3.Teamlancer.aggressive_red | mean episode reward (no code released by this team (DECISIONS 3, 6, 15)) | -801 | - | - | NOT ATTEMPTED |
| T3.Teampunch.CC4 | mean episode reward, 10 seeds x 100 episodes x 500 steps | -142 | -150.1 [-153.9, -146.2] | -8.1 | CLOSE |
| T3.Teampunch.constant_network_size | mean episode reward (the environment provides no configuration for this variation (DECISIONS 4, 12)) | -94 | - | - | NOT ATTEMPTED |
| T3.Teampunch.improved_decoy_detection | mean episode reward (the environment provides no configuration for this variation (DECISIONS 4, 12)) | -171 | - | - | NOT ATTEMPTED |
| T3.Teampunch.increased_phishing | mean episode reward (the environment provides no configuration for this variation (DECISIONS 4, 12)) | -205 | - | - | NOT ATTEMPTED |
| T3.Teampunch.stealthy_red | mean episode reward (the environment provides no configuration for this variation (DECISIONS 4, 12)) | -158 | - | - | NOT ATTEMPTED |
| T3.Teampunch.aggressive_red | mean episode reward (the environment provides no configuration for this variation (DECISIONS 4, 12)) | -837 | - | - | NOT ATTEMPTED |
| T3.Teamcybermonic.CC4 | mean episode reward, 10 seeds x 100 episodes x 500 steps | -193 | -190.3 [-195.4, -185.2] | +2.7 | MATCH |
| T3.Teamcybermonic.constant_network_size | mean episode reward (the environment provides no configuration for this variation (DECISIONS 4, 12)) | -176 | - | - | NOT ATTEMPTED |
| T3.Teamcybermonic.improved_decoy_detection | mean episode reward (the environment provides no configuration for this variation (DECISIONS 4, 12)) | -198 | - | - | NOT ATTEMPTED |
| T3.Teamcybermonic.increased_phishing | mean episode reward (the environment provides no configuration for this variation (DECISIONS 4, 12)) | -350 | - | - | NOT ATTEMPTED |
| T3.Teamcybermonic.stealthy_red | mean episode reward (the environment provides no configuration for this variation (DECISIONS 4, 12)) | -996 | - | - | NOT ATTEMPTED |
| T3.Teamcybermonic.aggressive_red | mean episode reward (the environment provides no configuration for this variation (DECISIONS 4, 12)) | -654 | - | - | NOT ATTEMPTED |

## Environment

- 3.11.9; CybORG 4.0; commits {'cage-challenge-4': '8c3c50ca54b176c2de199847944e8dcc035497e3', 'cage-4-submission': '2afd652d80ce9d4051a07c23c2538f3dec6bb6c6', 'cage-4-submissions-punch': '9cc4ff83d600b0c810dad2ec428e35c0f3a0b6b0'}; machine DESKTOP-Q1DMJ51. Full package list: `out/ENVIRONMENT.json`.
- Changes from the 2024 software, all declared before the run (DECISIONS 8): Ray 2.10.0 for 2.12.0 (no
  Windows build), torch_geometric 2.3.1 (cybermonic's pin), unpinned packages resolved as of 2024-06-15.
- Our loop was checked against the official `run_evaluation` for each team (`out/VERIFY.json`).
- Rerunning the first 3 episodes of a kept seed gives identical scores (`out/RECHECK_*.json`), so the
  seeds that started over after the out-of-memory failure (DECISIONS run log) are the episodes their seeds fix.

Every episode: `out/episodes_<team>_seed<k>.json`.
