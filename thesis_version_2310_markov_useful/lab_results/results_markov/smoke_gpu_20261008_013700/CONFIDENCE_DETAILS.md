# Confidence ablation: every measured record

## GRU seed 0 calibration
Temperature: 0.5522139107260787; episode thresholds: [0.2991480827331543, 0.45588400959968567]; encoder SHA256: d4821fa0ac56c68f6f47fcbf6175475695607eb1b18a09a1a65836decb9f0640

| Partition | Bin | Count | Mean max probability | Accuracy |
|---|---|---|---|---|
| validation_raw | 0 | 140 | 0.05958 | 0.27857 |
| validation_raw | 1 | 64 | 0.14742 | 0.32812 |
| validation_raw | 2 | 25 | 0.24260 | 0.56000 |
| validation_raw | 3 | 6 | 0.35224 | 0.00000 |
| validation_raw | 4 | 19 | 0.48044 | 0.73684 |
| validation_raw | 5 | 11 | 0.52275 | 1.00000 |
| validation_raw | 6 | 0 | N/A | N/A |
| validation_raw | 7 | 0 | N/A | N/A |
| validation_raw | 8 | 0 | N/A | N/A |
| validation_raw | 9 | 0 | N/A | N/A |
| validation_scaled | 0 | 43 | 0.08259 | 0.11628 |
| validation_scaled | 1 | 62 | 0.14970 | 0.24194 |
| validation_scaled | 2 | 28 | 0.25734 | 0.57143 |
| validation_scaled | 3 | 21 | 0.34019 | 0.38095 |
| validation_scaled | 4 | 19 | 0.44722 | 0.52632 |
| validation_scaled | 5 | 15 | 0.54238 | 0.40000 |
| validation_scaled | 6 | 16 | 0.66045 | 0.00000 |
| validation_scaled | 7 | 16 | 0.74090 | 0.37500 |
| validation_scaled | 8 | 11 | 0.84034 | 0.72727 |
| validation_scaled | 9 | 34 | 0.95763 | 0.73529 |
| test_raw | 0 | 160 | 0.05567 | 0.21875 |
| test_raw | 1 | 56 | 0.14777 | 0.42857 |
| test_raw | 2 | 22 | 0.24361 | 0.54545 |
| test_raw | 3 | 4 | 0.36621 | 0.00000 |
| test_raw | 4 | 19 | 0.48044 | 0.73684 |
| test_raw | 5 | 11 | 0.52275 | 1.00000 |
| test_raw | 6 | 0 | N/A | N/A |
| test_raw | 7 | 0 | N/A | N/A |
| test_raw | 8 | 0 | N/A | N/A |
| test_raw | 9 | 0 | N/A | N/A |
| test_scaled | 0 | 52 | 0.08640 | 0.17308 |
| test_scaled | 1 | 81 | 0.13738 | 0.13580 |
| test_scaled | 2 | 22 | 0.24764 | 0.54545 |
| test_scaled | 3 | 17 | 0.33864 | 0.47059 |
| test_scaled | 4 | 17 | 0.44706 | 0.76471 |
| test_scaled | 5 | 12 | 0.54298 | 0.41667 |
| test_scaled | 6 | 15 | 0.65966 | 0.06667 |
| test_scaled | 7 | 14 | 0.74144 | 0.28571 |
| test_scaled | 8 | 8 | 0.83240 | 1.00000 |
| test_scaled | 9 | 34 | 0.95763 | 0.73529 |
## LSTM seed 0 calibration
Temperature: 0.5425265184202248; episode thresholds: [0.23937225341796875, 0.3730403482913971]; encoder SHA256: 14aff65eb28d040cd556c7d2e696063b585042a1775e39d8d6aeaa2d117a3d1d

| Partition | Bin | Count | Mean max probability | Accuracy |
|---|---|---|---|---|
| validation_raw | 0 | 165 | 0.05768 | 0.23030 |
| validation_raw | 1 | 53 | 0.14653 | 0.39623 |
| validation_raw | 2 | 23 | 0.25559 | 0.43478 |
| validation_raw | 3 | 24 | 0.30980 | 0.83333 |
| validation_raw | 4 | 0 | N/A | N/A |
| validation_raw | 5 | 0 | N/A | N/A |
| validation_raw | 6 | 0 | N/A | N/A |
| validation_raw | 7 | 0 | N/A | N/A |
| validation_raw | 8 | 0 | N/A | N/A |
| validation_raw | 9 | 0 | N/A | N/A |
| validation_scaled | 0 | 56 | 0.07308 | 0.16071 |
| validation_scaled | 1 | 64 | 0.16025 | 0.34375 |
| validation_scaled | 2 | 28 | 0.24596 | 0.25000 |
| validation_scaled | 3 | 22 | 0.34978 | 0.00000 |
| validation_scaled | 4 | 8 | 0.43494 | 0.25000 |
| validation_scaled | 5 | 26 | 0.54230 | 0.53846 |
| validation_scaled | 6 | 14 | 0.66042 | 0.35714 |
| validation_scaled | 7 | 8 | 0.76169 | 0.37500 |
| validation_scaled | 8 | 39 | 0.85255 | 0.69231 |
| validation_scaled | 9 | 0 | N/A | N/A |
| test_raw | 0 | 200 | 0.05268 | 0.17500 |
| test_raw | 1 | 32 | 0.14563 | 0.50000 |
| test_raw | 2 | 16 | 0.25990 | 0.50000 |
| test_raw | 3 | 24 | 0.30980 | 0.83333 |
| test_raw | 4 | 0 | N/A | N/A |
| test_raw | 5 | 0 | N/A | N/A |
| test_raw | 6 | 0 | N/A | N/A |
| test_raw | 7 | 0 | N/A | N/A |
| test_raw | 8 | 0 | N/A | N/A |
| test_raw | 9 | 0 | N/A | N/A |
| test_scaled | 0 | 87 | 0.07867 | 0.06897 |
| test_scaled | 1 | 79 | 0.14854 | 0.29114 |
| test_scaled | 2 | 19 | 0.23429 | 0.31579 |
| test_scaled | 3 | 20 | 0.35542 | 0.00000 |
| test_scaled | 4 | 2 | 0.46315 | 0.50000 |
| test_scaled | 5 | 18 | 0.54659 | 0.66667 |
| test_scaled | 6 | 7 | 0.65379 | 0.42857 |
| test_scaled | 7 | 4 | 0.76564 | 0.50000 |
| test_scaled | 8 | 36 | 0.85471 | 0.72222 |
| test_scaled | 9 | 0 | N/A | N/A |
## Transformer seed 0 calibration
Temperature: 0.5417198724708973; episode thresholds: [0.18225976824760437, 0.35269975662231445]; encoder SHA256: 2e861939434ef4a036913f769533825ab785df7fbedd2247554afe1718294dfd

| Partition | Bin | Count | Mean max probability | Accuracy |
|---|---|---|---|---|
| validation_raw | 0 | 197 | 0.05785 | 0.18274 |
| validation_raw | 1 | 39 | 0.12608 | 0.41026 |
| validation_raw | 2 | 0 | N/A | N/A |
| validation_raw | 3 | 29 | 0.38661 | 0.72414 |
| validation_raw | 4 | 0 | N/A | N/A |
| validation_raw | 5 | 0 | N/A | N/A |
| validation_raw | 6 | 0 | N/A | N/A |
| validation_raw | 7 | 0 | N/A | N/A |
| validation_raw | 8 | 0 | N/A | N/A |
| validation_raw | 9 | 0 | N/A | N/A |
| validation_scaled | 0 | 56 | 0.08141 | 0.01786 |
| validation_scaled | 1 | 90 | 0.14014 | 0.23333 |
| validation_scaled | 2 | 30 | 0.23842 | 0.33333 |
| validation_scaled | 3 | 38 | 0.34018 | 0.21053 |
| validation_scaled | 4 | 10 | 0.46140 | 0.80000 |
| validation_scaled | 5 | 7 | 0.55673 | 0.28571 |
| validation_scaled | 6 | 4 | 0.63673 | 0.50000 |
| validation_scaled | 7 | 1 | 0.70469 | 0.00000 |
| validation_scaled | 8 | 0 | N/A | N/A |
| validation_scaled | 9 | 29 | 0.93417 | 0.72414 |
| test_raw | 0 | 204 | 0.05934 | 0.17157 |
| test_raw | 1 | 39 | 0.12004 | 0.33333 |
| test_raw | 2 | 0 | N/A | N/A |
| test_raw | 3 | 29 | 0.38661 | 0.72414 |
| test_raw | 4 | 0 | N/A | N/A |
| test_raw | 5 | 0 | N/A | N/A |
| test_raw | 6 | 0 | N/A | N/A |
| test_raw | 7 | 0 | N/A | N/A |
| test_raw | 8 | 0 | N/A | N/A |
| test_raw | 9 | 0 | N/A | N/A |
| test_scaled | 0 | 48 | 0.08379 | 0.00000 |
| test_scaled | 1 | 87 | 0.14034 | 0.22989 |
| test_scaled | 2 | 54 | 0.22949 | 0.20370 |
| test_scaled | 3 | 39 | 0.34519 | 0.20513 |
| test_scaled | 4 | 7 | 0.45260 | 0.85714 |
| test_scaled | 5 | 5 | 0.56693 | 0.20000 |
| test_scaled | 6 | 3 | 0.63637 | 0.66667 |
| test_scaled | 7 | 0 | N/A | N/A |
| test_scaled | 8 | 0 | N/A | N/A |
| test_scaled | 9 | 29 | 0.93417 | 0.72414 |
## GRU IPPO baseline seed 0

| update | env_steps | train_dwell | val_dwell | val_depth | seconds |
|---|---|---|---|---|---|
| 1 | 16 | 0.00000 | 2.85714 | 2.71429 | 0.41007 |
| dwell | depth | protected | exposed | length | horizon | script | capacity_violations | lure_engagements | lure_chains | dead_ends | decoys_deployed | engaged_in_target | exposed_at | episode_reward | run | group | environment_repeat | sequence_certainty | confidence_group |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4.00000 | 4.00000 | 1.00000 | 1.00000 | 44.00000 | 44.00000 | S1 | 44.00000 | 4.00000 | 0.00000 | 0.00000 | 176.00000 | 4.00000 | 31.00000 | 4.00000 | scenario_1_b_c.j2 | 93fb0bdece9eb4b06d5621759bdddb12a4c6cb73cb9d85bcc4686567c973febd | 0 | 0.47681 | high |
| 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 | 44.00000 | S1 | 30.00000 | 1.00000 | 0.00000 | 0.00000 | 120.00000 | 2.00000 | 6.00000 | 2.00000 | scenario_1_c_c.j2 | b8894870ed5dd26fd324b7e5242c0dbc9ca42971f6f40e580f3f4abc5c88b233 | 0 | 0.48792 | high |
| 3.00000 | 3.00000 | 0.00000 | 1.00000 | 32.00000 | 51.00000 | S1 | 32.00000 | 3.00000 | 0.00000 | 0.00000 | 128.00000 | 1.00000 | 23.00000 | 3.00000 | scenario_1_d_a.j2 | f78f864ba7b16a4cb55909a2f99f016c3cb0a56c3d6915054ecb65e62b7edfe0 | 0 | 0.47870 | high |
| 0.00000 | 0.00000 | 0.00000 | 0.00000 | 30.00000 | 46.00000 | S1 | 30.00000 | 0.00000 | 0.00000 | 0.00000 | 120.00000 | 0.00000 | -1.00000 | 0.00000 | scenario_1_e_a.j2 | 3519cf18b1dfaed57f30a4ac04c186e8e9f9063aa1012ac46be0d8339f2c7499 | 0 | 0.44507 | medium |
| 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 | 25.00000 | S3 | 16.00000 | 2.00000 | 0.00000 | 0.00000 | 64.00000 | 1.00000 | -1.00000 | 2.00000 | scenario_3_a_b.j2 | 5fd306c58b8996decd7b5f08199ce000446ea0262cdb556ef4e998c4ddc403fe | 0 | 0.12930 | low |
| 6.00000 | 4.00000 | 0.00000 | 1.00000 | 15.00000 | 24.00000 | S3 | 15.00000 | 6.00000 | 3.00000 | 0.00000 | 60.00000 | 3.00000 | 7.00000 | 6.00000 | scenario_3_b_b.j2 | 339f6d168b5df02964f55501786fc78bdd0460dcad2eaf1cfc7d24f3f5ca5e97 | 0 | 0.14982 | low |
| 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 | 45.00000 | S6 | 2.00000 | 0.00000 | 0.00000 | 0.00000 | 8.00000 | 0.00000 | -1.00000 | 0.00000 | scenario_6_c.j2 | 497137828a7e4894a21fcb0a2ca19c647410f50cd8eec09905696391186176e2 | 0 | 0.16539 | low |
## GRU IPPO confidence seed 0

| update | env_steps | train_dwell | val_dwell | val_depth | seconds |
|---|---|---|---|---|---|
| 1 | 16 | 0.00000 | 2.85714 | 2.71429 | 0.41698 |
| dwell | depth | protected | exposed | length | horizon | script | capacity_violations | lure_engagements | lure_chains | dead_ends | decoys_deployed | engaged_in_target | exposed_at | episode_reward | run | group | environment_repeat | sequence_certainty | confidence_group |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4.00000 | 4.00000 | 1.00000 | 1.00000 | 44.00000 | 44.00000 | S1 | 44.00000 | 4.00000 | 0.00000 | 0.00000 | 176.00000 | 4.00000 | 31.00000 | 4.00000 | scenario_1_b_c.j2 | 93fb0bdece9eb4b06d5621759bdddb12a4c6cb73cb9d85bcc4686567c973febd | 0 | 0.47681 | high |
| 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 | 44.00000 | S1 | 30.00000 | 1.00000 | 0.00000 | 0.00000 | 120.00000 | 2.00000 | 6.00000 | 2.00000 | scenario_1_c_c.j2 | b8894870ed5dd26fd324b7e5242c0dbc9ca42971f6f40e580f3f4abc5c88b233 | 0 | 0.48792 | high |
| 3.00000 | 3.00000 | 0.00000 | 1.00000 | 32.00000 | 51.00000 | S1 | 32.00000 | 3.00000 | 0.00000 | 0.00000 | 128.00000 | 1.00000 | 23.00000 | 3.00000 | scenario_1_d_a.j2 | f78f864ba7b16a4cb55909a2f99f016c3cb0a56c3d6915054ecb65e62b7edfe0 | 0 | 0.47870 | high |
| 0.00000 | 0.00000 | 0.00000 | 0.00000 | 30.00000 | 46.00000 | S1 | 30.00000 | 0.00000 | 0.00000 | 0.00000 | 120.00000 | 0.00000 | -1.00000 | 0.00000 | scenario_1_e_a.j2 | 3519cf18b1dfaed57f30a4ac04c186e8e9f9063aa1012ac46be0d8339f2c7499 | 0 | 0.44507 | medium |
| 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 | 25.00000 | S3 | 16.00000 | 2.00000 | 0.00000 | 0.00000 | 64.00000 | 1.00000 | -1.00000 | 2.00000 | scenario_3_a_b.j2 | 5fd306c58b8996decd7b5f08199ce000446ea0262cdb556ef4e998c4ddc403fe | 0 | 0.12930 | low |
| 6.00000 | 4.00000 | 0.00000 | 1.00000 | 15.00000 | 24.00000 | S3 | 15.00000 | 6.00000 | 3.00000 | 0.00000 | 60.00000 | 3.00000 | 7.00000 | 6.00000 | scenario_3_b_b.j2 | 339f6d168b5df02964f55501786fc78bdd0460dcad2eaf1cfc7d24f3f5ca5e97 | 0 | 0.14982 | low |
| 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 | 45.00000 | S6 | 2.00000 | 0.00000 | 0.00000 | 0.00000 | 8.00000 | 0.00000 | -1.00000 | 0.00000 | scenario_6_c.j2 | 497137828a7e4894a21fcb0a2ca19c647410f50cd8eec09905696391186176e2 | 0 | 0.16539 | low |
## GRU MAPPO baseline seed 0

| update | env_steps | train_dwell | val_dwell | val_depth | seconds |
|---|---|---|---|---|---|
| 1 | 16 | 0.00000 | 3.85714 | 3.71429 | 0.42781 |
| dwell | depth | protected | exposed | length | horizon | script | capacity_violations | lure_engagements | lure_chains | dead_ends | decoys_deployed | engaged_in_target | exposed_at | episode_reward | run | group | environment_repeat | sequence_certainty | confidence_group |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 11.00000 | 11.00000 | 1.00000 | 1.00000 | 44.00000 | 44.00000 | S1 | 9.00000 | 11.00000 | 7.00000 | 1.00000 | 89.00000 | 6.00000 | 39.00000 | 11.00000 | scenario_1_b_c.j2 | 93fb0bdece9eb4b06d5621759bdddb12a4c6cb73cb9d85bcc4686567c973febd | 0 | 0.47681 | high |
| 2.00000 | 1.00000 | 0.00000 | 1.00000 | 30.00000 | 44.00000 | S1 | 11.00000 | 2.00000 | 0.00000 | 0.00000 | 74.00000 | 1.00000 | 10.00000 | 2.00000 | scenario_1_c_c.j2 | b8894870ed5dd26fd324b7e5242c0dbc9ca42971f6f40e580f3f4abc5c88b233 | 0 | 0.48792 | high |
| 3.00000 | 3.00000 | 0.00000 | 1.00000 | 32.00000 | 51.00000 | S1 | 18.00000 | 3.00000 | 0.00000 | 0.00000 | 84.00000 | 1.00000 | 23.00000 | 3.00000 | scenario_1_d_a.j2 | f78f864ba7b16a4cb55909a2f99f016c3cb0a56c3d6915054ecb65e62b7edfe0 | 0 | 0.47870 | high |
| 1.00000 | 1.00000 | 0.00000 | 0.00000 | 30.00000 | 46.00000 | S1 | 10.00000 | 1.00000 | 0.00000 | 0.00000 | 61.00000 | 1.00000 | -1.00000 | 1.00000 | scenario_1_e_a.j2 | 3519cf18b1dfaed57f30a4ac04c186e8e9f9063aa1012ac46be0d8339f2c7499 | 0 | 0.44507 | medium |
| 4.00000 | 3.00000 | 0.00000 | 0.00000 | 25.00000 | 25.00000 | S3 | 21.00000 | 4.00000 | 0.00000 | 0.00000 | 83.00000 | 2.00000 | -1.00000 | 4.00000 | scenario_3_a_b.j2 | 5fd306c58b8996decd7b5f08199ce000446ea0262cdb556ef4e998c4ddc403fe | 0 | 0.12930 | low |
| 1.00000 | 1.00000 | 0.00000 | 1.00000 | 15.00000 | 24.00000 | S3 | 5.00000 | 1.00000 | 0.00000 | 0.00000 | 34.00000 | 1.00000 | 7.00000 | 1.00000 | scenario_3_b_b.j2 | 339f6d168b5df02964f55501786fc78bdd0460dcad2eaf1cfc7d24f3f5ca5e97 | 0 | 0.14982 | low |
| 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 | 45.00000 | S6 | 1.00000 | 0.00000 | 0.00000 | 0.00000 | 5.00000 | 0.00000 | -1.00000 | 0.00000 | scenario_6_c.j2 | 497137828a7e4894a21fcb0a2ca19c647410f50cd8eec09905696391186176e2 | 0 | 0.16539 | low |
## GRU MAPPO confidence seed 0

| update | env_steps | train_dwell | val_dwell | val_depth | seconds |
|---|---|---|---|---|---|
| 1 | 16 | 0.00000 | 3.14286 | 3.14286 | 0.44806 |
| dwell | depth | protected | exposed | length | horizon | script | capacity_violations | lure_engagements | lure_chains | dead_ends | decoys_deployed | engaged_in_target | exposed_at | episode_reward | run | group | environment_repeat | sequence_certainty | confidence_group |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 11.00000 | 11.00000 | 1.00000 | 1.00000 | 44.00000 | 44.00000 | S1 | 9.00000 | 11.00000 | 7.00000 | 1.00000 | 89.00000 | 6.00000 | 39.00000 | 11.00000 | scenario_1_b_c.j2 | 93fb0bdece9eb4b06d5621759bdddb12a4c6cb73cb9d85bcc4686567c973febd | 0 | 0.47681 | high |
| 2.00000 | 1.00000 | 0.00000 | 1.00000 | 30.00000 | 44.00000 | S1 | 11.00000 | 2.00000 | 0.00000 | 0.00000 | 74.00000 | 1.00000 | 10.00000 | 2.00000 | scenario_1_c_c.j2 | b8894870ed5dd26fd324b7e5242c0dbc9ca42971f6f40e580f3f4abc5c88b233 | 0 | 0.48792 | high |
| 3.00000 | 3.00000 | 0.00000 | 1.00000 | 32.00000 | 51.00000 | S1 | 18.00000 | 3.00000 | 0.00000 | 0.00000 | 85.00000 | 1.00000 | 23.00000 | 3.00000 | scenario_1_d_a.j2 | f78f864ba7b16a4cb55909a2f99f016c3cb0a56c3d6915054ecb65e62b7edfe0 | 0 | 0.47870 | high |
| 1.00000 | 1.00000 | 0.00000 | 0.00000 | 30.00000 | 46.00000 | S1 | 10.00000 | 1.00000 | 0.00000 | 0.00000 | 61.00000 | 1.00000 | -1.00000 | 1.00000 | scenario_1_e_a.j2 | 3519cf18b1dfaed57f30a4ac04c186e8e9f9063aa1012ac46be0d8339f2c7499 | 0 | 0.44507 | medium |
| 4.00000 | 3.00000 | 0.00000 | 0.00000 | 22.00000 | 25.00000 | S3 | 15.00000 | 4.00000 | 1.00000 | 0.00000 | 68.00000 | 3.00000 | -1.00000 | 4.00000 | scenario_3_a_b.j2 | 5fd306c58b8996decd7b5f08199ce000446ea0262cdb556ef4e998c4ddc403fe | 0 | 0.12930 | low |
| 1.00000 | 1.00000 | 0.00000 | 1.00000 | 15.00000 | 24.00000 | S3 | 4.00000 | 1.00000 | 0.00000 | 0.00000 | 30.00000 | 1.00000 | 7.00000 | 1.00000 | scenario_3_b_b.j2 | 339f6d168b5df02964f55501786fc78bdd0460dcad2eaf1cfc7d24f3f5ca5e97 | 0 | 0.14982 | low |
| 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 | 45.00000 | S6 | 1.00000 | 0.00000 | 0.00000 | 0.00000 | 5.00000 | 0.00000 | -1.00000 | 0.00000 | scenario_6_c.j2 | 497137828a7e4894a21fcb0a2ca19c647410f50cd8eec09905696391186176e2 | 0 | 0.16539 | low |
## LSTM IPPO baseline seed 0

| update | env_steps | train_dwell | val_dwell | val_depth | seconds |
|---|---|---|---|---|---|
| 1 | 16 | 0.00000 | 2.85714 | 2.71429 | 0.36604 |
| dwell | depth | protected | exposed | length | horizon | script | capacity_violations | lure_engagements | lure_chains | dead_ends | decoys_deployed | engaged_in_target | exposed_at | episode_reward | run | group | environment_repeat | sequence_certainty | confidence_group |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4.00000 | 4.00000 | 1.00000 | 1.00000 | 44.00000 | 44.00000 | S1 | 44.00000 | 4.00000 | 0.00000 | 0.00000 | 175.00000 | 4.00000 | 31.00000 | 4.00000 | scenario_1_b_c.j2 | 93fb0bdece9eb4b06d5621759bdddb12a4c6cb73cb9d85bcc4686567c973febd | 0 | 0.31797 | medium |
| 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 | 44.00000 | S1 | 30.00000 | 1.00000 | 0.00000 | 0.00000 | 119.00000 | 2.00000 | 6.00000 | 2.00000 | scenario_1_c_c.j2 | b8894870ed5dd26fd324b7e5242c0dbc9ca42971f6f40e580f3f4abc5c88b233 | 0 | 0.36494 | medium |
| 3.00000 | 3.00000 | 0.00000 | 1.00000 | 32.00000 | 51.00000 | S1 | 32.00000 | 3.00000 | 0.00000 | 0.00000 | 127.00000 | 1.00000 | 23.00000 | 3.00000 | scenario_1_d_a.j2 | f78f864ba7b16a4cb55909a2f99f016c3cb0a56c3d6915054ecb65e62b7edfe0 | 0 | 0.36801 | medium |
| 0.00000 | 0.00000 | 0.00000 | 0.00000 | 30.00000 | 46.00000 | S1 | 30.00000 | 0.00000 | 0.00000 | 0.00000 | 119.00000 | 0.00000 | -1.00000 | 0.00000 | scenario_1_e_a.j2 | 3519cf18b1dfaed57f30a4ac04c186e8e9f9063aa1012ac46be0d8339f2c7499 | 0 | 0.37906 | high |
| 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 | 25.00000 | S3 | 16.00000 | 2.00000 | 0.00000 | 0.00000 | 63.00000 | 1.00000 | -1.00000 | 2.00000 | scenario_3_a_b.j2 | 5fd306c58b8996decd7b5f08199ce000446ea0262cdb556ef4e998c4ddc403fe | 0 | 0.11241 | low |
| 5.00000 | 3.00000 | 0.00000 | 1.00000 | 15.00000 | 24.00000 | S3 | 15.00000 | 5.00000 | 3.00000 | 0.00000 | 59.00000 | 2.00000 | 7.00000 | 5.00000 | scenario_3_b_b.j2 | 339f6d168b5df02964f55501786fc78bdd0460dcad2eaf1cfc7d24f3f5ca5e97 | 0 | 0.12587 | low |
| 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 | 45.00000 | S6 | 2.00000 | 0.00000 | 0.00000 | 0.00000 | 7.00000 | 0.00000 | -1.00000 | 0.00000 | scenario_6_c.j2 | 497137828a7e4894a21fcb0a2ca19c647410f50cd8eec09905696391186176e2 | 0 | 0.14194 | low |
## LSTM IPPO confidence seed 0

| update | env_steps | train_dwell | val_dwell | val_depth | seconds |
|---|---|---|---|---|---|
| 1 | 16 | 0.00000 | 2.85714 | 2.71429 | 0.34544 |
| dwell | depth | protected | exposed | length | horizon | script | capacity_violations | lure_engagements | lure_chains | dead_ends | decoys_deployed | engaged_in_target | exposed_at | episode_reward | run | group | environment_repeat | sequence_certainty | confidence_group |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4.00000 | 4.00000 | 1.00000 | 1.00000 | 44.00000 | 44.00000 | S1 | 44.00000 | 4.00000 | 0.00000 | 0.00000 | 175.00000 | 4.00000 | 31.00000 | 4.00000 | scenario_1_b_c.j2 | 93fb0bdece9eb4b06d5621759bdddb12a4c6cb73cb9d85bcc4686567c973febd | 0 | 0.31797 | medium |
| 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 | 44.00000 | S1 | 30.00000 | 1.00000 | 0.00000 | 0.00000 | 119.00000 | 2.00000 | 6.00000 | 2.00000 | scenario_1_c_c.j2 | b8894870ed5dd26fd324b7e5242c0dbc9ca42971f6f40e580f3f4abc5c88b233 | 0 | 0.36494 | medium |
| 3.00000 | 3.00000 | 0.00000 | 1.00000 | 32.00000 | 51.00000 | S1 | 32.00000 | 3.00000 | 0.00000 | 0.00000 | 127.00000 | 1.00000 | 23.00000 | 3.00000 | scenario_1_d_a.j2 | f78f864ba7b16a4cb55909a2f99f016c3cb0a56c3d6915054ecb65e62b7edfe0 | 0 | 0.36801 | medium |
| 0.00000 | 0.00000 | 0.00000 | 0.00000 | 30.00000 | 46.00000 | S1 | 30.00000 | 0.00000 | 0.00000 | 0.00000 | 119.00000 | 0.00000 | -1.00000 | 0.00000 | scenario_1_e_a.j2 | 3519cf18b1dfaed57f30a4ac04c186e8e9f9063aa1012ac46be0d8339f2c7499 | 0 | 0.37906 | high |
| 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 | 25.00000 | S3 | 16.00000 | 2.00000 | 0.00000 | 0.00000 | 63.00000 | 1.00000 | -1.00000 | 2.00000 | scenario_3_a_b.j2 | 5fd306c58b8996decd7b5f08199ce000446ea0262cdb556ef4e998c4ddc403fe | 0 | 0.11241 | low |
| 5.00000 | 3.00000 | 0.00000 | 1.00000 | 15.00000 | 24.00000 | S3 | 15.00000 | 5.00000 | 3.00000 | 0.00000 | 58.00000 | 2.00000 | 7.00000 | 5.00000 | scenario_3_b_b.j2 | 339f6d168b5df02964f55501786fc78bdd0460dcad2eaf1cfc7d24f3f5ca5e97 | 0 | 0.12587 | low |
| 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 | 45.00000 | S6 | 2.00000 | 0.00000 | 0.00000 | 0.00000 | 7.00000 | 0.00000 | -1.00000 | 0.00000 | scenario_6_c.j2 | 497137828a7e4894a21fcb0a2ca19c647410f50cd8eec09905696391186176e2 | 0 | 0.14194 | low |
## LSTM MAPPO baseline seed 0

| update | env_steps | train_dwell | val_dwell | val_depth | seconds |
|---|---|---|---|---|---|
| 1 | 16 | 0.00000 | 2.85714 | 2.71429 | 0.36991 |
| dwell | depth | protected | exposed | length | horizon | script | capacity_violations | lure_engagements | lure_chains | dead_ends | decoys_deployed | engaged_in_target | exposed_at | episode_reward | run | group | environment_repeat | sequence_certainty | confidence_group |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4.00000 | 4.00000 | 1.00000 | 1.00000 | 44.00000 | 44.00000 | S1 | 44.00000 | 4.00000 | 0.00000 | 0.00000 | 175.00000 | 4.00000 | 31.00000 | 4.00000 | scenario_1_b_c.j2 | 93fb0bdece9eb4b06d5621759bdddb12a4c6cb73cb9d85bcc4686567c973febd | 0 | 0.31797 | medium |
| 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 | 44.00000 | S1 | 30.00000 | 1.00000 | 0.00000 | 0.00000 | 119.00000 | 2.00000 | 6.00000 | 2.00000 | scenario_1_c_c.j2 | b8894870ed5dd26fd324b7e5242c0dbc9ca42971f6f40e580f3f4abc5c88b233 | 0 | 0.36494 | medium |
| 3.00000 | 3.00000 | 0.00000 | 1.00000 | 32.00000 | 51.00000 | S1 | 32.00000 | 3.00000 | 0.00000 | 0.00000 | 127.00000 | 1.00000 | 23.00000 | 3.00000 | scenario_1_d_a.j2 | f78f864ba7b16a4cb55909a2f99f016c3cb0a56c3d6915054ecb65e62b7edfe0 | 0 | 0.36801 | medium |
| 0.00000 | 0.00000 | 0.00000 | 0.00000 | 30.00000 | 46.00000 | S1 | 30.00000 | 0.00000 | 0.00000 | 0.00000 | 119.00000 | 0.00000 | -1.00000 | 0.00000 | scenario_1_e_a.j2 | 3519cf18b1dfaed57f30a4ac04c186e8e9f9063aa1012ac46be0d8339f2c7499 | 0 | 0.37906 | high |
| 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 | 25.00000 | S3 | 16.00000 | 2.00000 | 0.00000 | 0.00000 | 63.00000 | 1.00000 | -1.00000 | 2.00000 | scenario_3_a_b.j2 | 5fd306c58b8996decd7b5f08199ce000446ea0262cdb556ef4e998c4ddc403fe | 0 | 0.11241 | low |
| 5.00000 | 3.00000 | 0.00000 | 1.00000 | 15.00000 | 24.00000 | S3 | 15.00000 | 5.00000 | 3.00000 | 0.00000 | 57.00000 | 3.00000 | 7.00000 | 5.00000 | scenario_3_b_b.j2 | 339f6d168b5df02964f55501786fc78bdd0460dcad2eaf1cfc7d24f3f5ca5e97 | 0 | 0.12587 | low |
| 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 | 45.00000 | S6 | 2.00000 | 0.00000 | 0.00000 | 0.00000 | 7.00000 | 0.00000 | -1.00000 | 0.00000 | scenario_6_c.j2 | 497137828a7e4894a21fcb0a2ca19c647410f50cd8eec09905696391186176e2 | 0 | 0.14194 | low |
## LSTM MAPPO confidence seed 0

| update | env_steps | train_dwell | val_dwell | val_depth | seconds |
|---|---|---|---|---|---|
| 1 | 16 | 0.00000 | 2.85714 | 2.71429 | 0.36599 |
| dwell | depth | protected | exposed | length | horizon | script | capacity_violations | lure_engagements | lure_chains | dead_ends | decoys_deployed | engaged_in_target | exposed_at | episode_reward | run | group | environment_repeat | sequence_certainty | confidence_group |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4.00000 | 4.00000 | 1.00000 | 1.00000 | 44.00000 | 44.00000 | S1 | 44.00000 | 4.00000 | 0.00000 | 0.00000 | 175.00000 | 4.00000 | 31.00000 | 4.00000 | scenario_1_b_c.j2 | 93fb0bdece9eb4b06d5621759bdddb12a4c6cb73cb9d85bcc4686567c973febd | 0 | 0.31797 | medium |
| 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 | 44.00000 | S1 | 30.00000 | 1.00000 | 0.00000 | 0.00000 | 119.00000 | 2.00000 | 6.00000 | 2.00000 | scenario_1_c_c.j2 | b8894870ed5dd26fd324b7e5242c0dbc9ca42971f6f40e580f3f4abc5c88b233 | 0 | 0.36494 | medium |
| 3.00000 | 3.00000 | 0.00000 | 1.00000 | 32.00000 | 51.00000 | S1 | 32.00000 | 3.00000 | 0.00000 | 0.00000 | 127.00000 | 1.00000 | 23.00000 | 3.00000 | scenario_1_d_a.j2 | f78f864ba7b16a4cb55909a2f99f016c3cb0a56c3d6915054ecb65e62b7edfe0 | 0 | 0.36801 | medium |
| 0.00000 | 0.00000 | 0.00000 | 0.00000 | 30.00000 | 46.00000 | S1 | 30.00000 | 0.00000 | 0.00000 | 0.00000 | 119.00000 | 0.00000 | -1.00000 | 0.00000 | scenario_1_e_a.j2 | 3519cf18b1dfaed57f30a4ac04c186e8e9f9063aa1012ac46be0d8339f2c7499 | 0 | 0.37906 | high |
| 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 | 25.00000 | S3 | 16.00000 | 2.00000 | 0.00000 | 0.00000 | 63.00000 | 1.00000 | -1.00000 | 2.00000 | scenario_3_a_b.j2 | 5fd306c58b8996decd7b5f08199ce000446ea0262cdb556ef4e998c4ddc403fe | 0 | 0.11241 | low |
| 5.00000 | 3.00000 | 0.00000 | 1.00000 | 15.00000 | 24.00000 | S3 | 15.00000 | 5.00000 | 3.00000 | 0.00000 | 57.00000 | 3.00000 | 7.00000 | 5.00000 | scenario_3_b_b.j2 | 339f6d168b5df02964f55501786fc78bdd0460dcad2eaf1cfc7d24f3f5ca5e97 | 0 | 0.12587 | low |
| 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 | 45.00000 | S6 | 2.00000 | 0.00000 | 0.00000 | 0.00000 | 7.00000 | 0.00000 | -1.00000 | 0.00000 | scenario_6_c.j2 | 497137828a7e4894a21fcb0a2ca19c647410f50cd8eec09905696391186176e2 | 0 | 0.14194 | low |
## Transformer IPPO baseline seed 0

| update | env_steps | train_dwell | val_dwell | val_depth | seconds |
|---|---|---|---|---|---|
| 1 | 16 | 0.00000 | 3.85714 | 3.28571 | 0.46227 |
| dwell | depth | protected | exposed | length | horizon | script | capacity_violations | lure_engagements | lure_chains | dead_ends | decoys_deployed | engaged_in_target | exposed_at | episode_reward | run | group | environment_repeat | sequence_certainty | confidence_group |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3.00000 | 3.00000 | 1.00000 | 0.00000 | 44.00000 | 44.00000 | S1 | 44.00000 | 0.00000 | 0.00000 | 0.00000 | 176.00000 | 3.00000 | -1.00000 | 3.00000 | scenario_1_b_c.j2 | 93fb0bdece9eb4b06d5621759bdddb12a4c6cb73cb9d85bcc4686567c973febd | 0 | 0.33553 | medium |
| 4.00000 | 3.00000 | 0.00000 | 1.00000 | 30.00000 | 44.00000 | S1 | 30.00000 | 0.00000 | 0.00000 | 0.00000 | 120.00000 | 3.00000 | 10.00000 | 4.00000 | scenario_1_c_c.j2 | b8894870ed5dd26fd324b7e5242c0dbc9ca42971f6f40e580f3f4abc5c88b233 | 0 | 0.36418 | high |
| 4.00000 | 2.00000 | 0.00000 | 1.00000 | 32.00000 | 51.00000 | S1 | 32.00000 | 1.00000 | 0.00000 | 0.00000 | 128.00000 | 2.00000 | 16.00000 | 4.00000 | scenario_1_d_a.j2 | f78f864ba7b16a4cb55909a2f99f016c3cb0a56c3d6915054ecb65e62b7edfe0 | 0 | 0.31872 | medium |
| 4.00000 | 1.00000 | 0.00000 | 1.00000 | 30.00000 | 46.00000 | S1 | 30.00000 | 0.00000 | 0.00000 | 0.00000 | 120.00000 | 4.00000 | 14.00000 | 4.00000 | scenario_1_e_a.j2 | 3519cf18b1dfaed57f30a4ac04c186e8e9f9063aa1012ac46be0d8339f2c7499 | 0 | 0.35479 | high |
| 3.00000 | 2.00000 | 0.00000 | 0.00000 | 19.00000 | 25.00000 | S3 | 19.00000 | 0.00000 | 0.00000 | 0.00000 | 76.00000 | 2.00000 | -1.00000 | 3.00000 | scenario_3_a_b.j2 | 5fd306c58b8996decd7b5f08199ce000446ea0262cdb556ef4e998c4ddc403fe | 0 | 0.14381 | low |
| 5.00000 | 4.00000 | 0.00000 | 1.00000 | 15.00000 | 24.00000 | S3 | 15.00000 | 5.00000 | 1.00000 | 0.00000 | 60.00000 | 4.00000 | 7.00000 | 5.00000 | scenario_3_b_b.j2 | 339f6d168b5df02964f55501786fc78bdd0460dcad2eaf1cfc7d24f3f5ca5e97 | 0 | 0.15366 | low |
| 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 | 45.00000 | S6 | 2.00000 | 0.00000 | 0.00000 | 0.00000 | 8.00000 | 0.00000 | -1.00000 | 0.00000 | scenario_6_c.j2 | 497137828a7e4894a21fcb0a2ca19c647410f50cd8eec09905696391186176e2 | 0 | 0.20622 | medium |
## Transformer IPPO confidence seed 0

| update | env_steps | train_dwell | val_dwell | val_depth | seconds |
|---|---|---|---|---|---|
| 1 | 16 | 0.00000 | 3.85714 | 3.28571 | 0.27205 |
| dwell | depth | protected | exposed | length | horizon | script | capacity_violations | lure_engagements | lure_chains | dead_ends | decoys_deployed | engaged_in_target | exposed_at | episode_reward | run | group | environment_repeat | sequence_certainty | confidence_group |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3.00000 | 3.00000 | 1.00000 | 0.00000 | 44.00000 | 44.00000 | S1 | 44.00000 | 0.00000 | 0.00000 | 0.00000 | 176.00000 | 3.00000 | -1.00000 | 3.00000 | scenario_1_b_c.j2 | 93fb0bdece9eb4b06d5621759bdddb12a4c6cb73cb9d85bcc4686567c973febd | 0 | 0.33553 | medium |
| 4.00000 | 3.00000 | 0.00000 | 1.00000 | 30.00000 | 44.00000 | S1 | 30.00000 | 0.00000 | 0.00000 | 0.00000 | 120.00000 | 3.00000 | 10.00000 | 4.00000 | scenario_1_c_c.j2 | b8894870ed5dd26fd324b7e5242c0dbc9ca42971f6f40e580f3f4abc5c88b233 | 0 | 0.36418 | high |
| 4.00000 | 2.00000 | 0.00000 | 1.00000 | 32.00000 | 51.00000 | S1 | 32.00000 | 1.00000 | 0.00000 | 0.00000 | 128.00000 | 2.00000 | 16.00000 | 4.00000 | scenario_1_d_a.j2 | f78f864ba7b16a4cb55909a2f99f016c3cb0a56c3d6915054ecb65e62b7edfe0 | 0 | 0.31872 | medium |
| 4.00000 | 1.00000 | 0.00000 | 1.00000 | 30.00000 | 46.00000 | S1 | 30.00000 | 0.00000 | 0.00000 | 0.00000 | 120.00000 | 4.00000 | 14.00000 | 4.00000 | scenario_1_e_a.j2 | 3519cf18b1dfaed57f30a4ac04c186e8e9f9063aa1012ac46be0d8339f2c7499 | 0 | 0.35479 | high |
| 3.00000 | 2.00000 | 0.00000 | 0.00000 | 19.00000 | 25.00000 | S3 | 19.00000 | 0.00000 | 0.00000 | 0.00000 | 76.00000 | 2.00000 | -1.00000 | 3.00000 | scenario_3_a_b.j2 | 5fd306c58b8996decd7b5f08199ce000446ea0262cdb556ef4e998c4ddc403fe | 0 | 0.14381 | low |
| 5.00000 | 4.00000 | 0.00000 | 1.00000 | 15.00000 | 24.00000 | S3 | 15.00000 | 5.00000 | 1.00000 | 0.00000 | 60.00000 | 4.00000 | 7.00000 | 5.00000 | scenario_3_b_b.j2 | 339f6d168b5df02964f55501786fc78bdd0460dcad2eaf1cfc7d24f3f5ca5e97 | 0 | 0.15366 | low |
| 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 | 45.00000 | S6 | 2.00000 | 0.00000 | 0.00000 | 0.00000 | 8.00000 | 0.00000 | -1.00000 | 0.00000 | scenario_6_c.j2 | 497137828a7e4894a21fcb0a2ca19c647410f50cd8eec09905696391186176e2 | 0 | 0.20622 | medium |
## Transformer MAPPO baseline seed 0

| update | env_steps | train_dwell | val_dwell | val_depth | seconds |
|---|---|---|---|---|---|
| 1 | 16 | 0.00000 | 2.57143 | 2.42857 | 0.29637 |
| dwell | depth | protected | exposed | length | horizon | script | capacity_violations | lure_engagements | lure_chains | dead_ends | decoys_deployed | engaged_in_target | exposed_at | episode_reward | run | group | environment_repeat | sequence_certainty | confidence_group |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3.00000 | 3.00000 | 1.00000 | 0.00000 | 44.00000 | 44.00000 | S1 | 44.00000 | 0.00000 | 0.00000 | 0.00000 | 175.00000 | 3.00000 | -1.00000 | 3.00000 | scenario_1_b_c.j2 | 93fb0bdece9eb4b06d5621759bdddb12a4c6cb73cb9d85bcc4686567c973febd | 0 | 0.33553 | medium |
| 3.00000 | 3.00000 | 0.00000 | 1.00000 | 30.00000 | 44.00000 | S1 | 30.00000 | 0.00000 | 0.00000 | 0.00000 | 119.00000 | 3.00000 | 10.00000 | 3.00000 | scenario_1_c_c.j2 | b8894870ed5dd26fd324b7e5242c0dbc9ca42971f6f40e580f3f4abc5c88b233 | 0 | 0.36418 | high |
| 3.00000 | 1.00000 | 0.00000 | 1.00000 | 32.00000 | 51.00000 | S1 | 32.00000 | 1.00000 | 0.00000 | 0.00000 | 127.00000 | 2.00000 | 16.00000 | 3.00000 | scenario_1_d_a.j2 | f78f864ba7b16a4cb55909a2f99f016c3cb0a56c3d6915054ecb65e62b7edfe0 | 0 | 0.31872 | medium |
| 4.00000 | 1.00000 | 0.00000 | 1.00000 | 30.00000 | 46.00000 | S1 | 30.00000 | 0.00000 | 0.00000 | 0.00000 | 119.00000 | 4.00000 | 14.00000 | 4.00000 | scenario_1_e_a.j2 | 3519cf18b1dfaed57f30a4ac04c186e8e9f9063aa1012ac46be0d8339f2c7499 | 0 | 0.35479 | high |
| 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 | 25.00000 | S3 | 16.00000 | 2.00000 | 0.00000 | 0.00000 | 63.00000 | 1.00000 | -1.00000 | 2.00000 | scenario_3_a_b.j2 | 5fd306c58b8996decd7b5f08199ce000446ea0262cdb556ef4e998c4ddc403fe | 0 | 0.14381 | low |
| 5.00000 | 3.00000 | 0.00000 | 1.00000 | 15.00000 | 24.00000 | S3 | 15.00000 | 5.00000 | 3.00000 | 0.00000 | 59.00000 | 2.00000 | 7.00000 | 5.00000 | scenario_3_b_b.j2 | 339f6d168b5df02964f55501786fc78bdd0460dcad2eaf1cfc7d24f3f5ca5e97 | 0 | 0.15366 | low |
| 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 | 45.00000 | S6 | 2.00000 | 0.00000 | 0.00000 | 0.00000 | 7.00000 | 0.00000 | -1.00000 | 0.00000 | scenario_6_c.j2 | 497137828a7e4894a21fcb0a2ca19c647410f50cd8eec09905696391186176e2 | 0 | 0.20622 | medium |
## Transformer MAPPO confidence seed 0

| update | env_steps | train_dwell | val_dwell | val_depth | seconds |
|---|---|---|---|---|---|
| 1 | 16 | 0.00000 | 2.85714 | 2.71429 | 0.26863 |
| dwell | depth | protected | exposed | length | horizon | script | capacity_violations | lure_engagements | lure_chains | dead_ends | decoys_deployed | engaged_in_target | exposed_at | episode_reward | run | group | environment_repeat | sequence_certainty | confidence_group |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3.00000 | 3.00000 | 1.00000 | 0.00000 | 44.00000 | 44.00000 | S1 | 44.00000 | 0.00000 | 0.00000 | 0.00000 | 175.00000 | 3.00000 | -1.00000 | 3.00000 | scenario_1_b_c.j2 | 93fb0bdece9eb4b06d5621759bdddb12a4c6cb73cb9d85bcc4686567c973febd | 0 | 0.33553 | medium |
| 3.00000 | 3.00000 | 0.00000 | 1.00000 | 30.00000 | 44.00000 | S1 | 30.00000 | 0.00000 | 0.00000 | 0.00000 | 119.00000 | 3.00000 | 10.00000 | 3.00000 | scenario_1_c_c.j2 | b8894870ed5dd26fd324b7e5242c0dbc9ca42971f6f40e580f3f4abc5c88b233 | 0 | 0.36418 | high |
| 3.00000 | 1.00000 | 0.00000 | 1.00000 | 32.00000 | 51.00000 | S1 | 32.00000 | 1.00000 | 0.00000 | 0.00000 | 127.00000 | 2.00000 | 16.00000 | 3.00000 | scenario_1_d_a.j2 | f78f864ba7b16a4cb55909a2f99f016c3cb0a56c3d6915054ecb65e62b7edfe0 | 0 | 0.31872 | medium |
| 4.00000 | 1.00000 | 0.00000 | 1.00000 | 30.00000 | 46.00000 | S1 | 30.00000 | 0.00000 | 0.00000 | 0.00000 | 119.00000 | 4.00000 | 14.00000 | 4.00000 | scenario_1_e_a.j2 | 3519cf18b1dfaed57f30a4ac04c186e8e9f9063aa1012ac46be0d8339f2c7499 | 0 | 0.35479 | high |
| 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 | 25.00000 | S3 | 16.00000 | 2.00000 | 0.00000 | 0.00000 | 63.00000 | 1.00000 | -1.00000 | 2.00000 | scenario_3_a_b.j2 | 5fd306c58b8996decd7b5f08199ce000446ea0262cdb556ef4e998c4ddc403fe | 0 | 0.14381 | low |
| 5.00000 | 3.00000 | 0.00000 | 1.00000 | 15.00000 | 24.00000 | S3 | 15.00000 | 5.00000 | 3.00000 | 0.00000 | 59.00000 | 2.00000 | 7.00000 | 5.00000 | scenario_3_b_b.j2 | 339f6d168b5df02964f55501786fc78bdd0460dcad2eaf1cfc7d24f3f5ca5e97 | 0 | 0.15366 | low |
| 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 | 45.00000 | S6 | 2.00000 | 0.00000 | 0.00000 | 0.00000 | 7.00000 | 0.00000 | -1.00000 | 0.00000 | scenario_6_c.j2 | 497137828a7e4894a21fcb0a2ca19c647410f50cd8eec09905696391186176e2 | 0 | 0.20622 | medium |