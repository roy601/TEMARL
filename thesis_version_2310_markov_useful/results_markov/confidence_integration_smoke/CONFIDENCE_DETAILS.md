# Confidence ablation: every measured record

## GRU seed 0 calibration
Temperature: 0.5523936561546727; episode thresholds: [0.29897865653038025, 0.4529545307159424]; encoder SHA256: c7b187621869ccf78dd4fc9f74a1da64e0176ef5b41f7ebb2b8a62709922833d

| Partition | Bin | Count | Mean max probability | Accuracy |
|---|---|---|---|---|
| validation_raw | 0 | 141 | 0.06006 | 0.28369 |
| validation_raw | 1 | 59 | 0.14155 | 0.33898 |
| validation_raw | 2 | 29 | 0.23637 | 0.48276 |
| validation_raw | 3 | 6 | 0.34902 | 0.00000 |
| validation_raw | 4 | 19 | 0.47313 | 0.73684 |
| validation_raw | 5 | 11 | 0.51462 | 1.00000 |
| validation_raw | 6 | 0 | N/A | N/A |
| validation_raw | 7 | 0 | N/A | N/A |
| validation_raw | 8 | 0 | N/A | N/A |
| validation_raw | 9 | 0 | N/A | N/A |
| validation_scaled | 0 | 44 | 0.08245 | 0.11364 |
| validation_scaled | 1 | 48 | 0.14044 | 0.20833 |
| validation_scaled | 2 | 46 | 0.24318 | 0.43478 |
| validation_scaled | 3 | 16 | 0.33746 | 0.56250 |
| validation_scaled | 4 | 20 | 0.43507 | 0.55000 |
| validation_scaled | 5 | 14 | 0.53111 | 0.35714 |
| validation_scaled | 6 | 16 | 0.66332 | 0.00000 |
| validation_scaled | 7 | 16 | 0.74003 | 0.37500 |
| validation_scaled | 8 | 11 | 0.83947 | 0.72727 |
| validation_scaled | 9 | 34 | 0.95509 | 0.73529 |
| test_raw | 0 | 161 | 0.05572 | 0.21118 |
| test_raw | 1 | 51 | 0.14192 | 0.47059 |
| test_raw | 2 | 26 | 0.23651 | 0.46154 |
| test_raw | 3 | 4 | 0.35919 | 0.00000 |
| test_raw | 4 | 19 | 0.47313 | 0.73684 |
| test_raw | 5 | 11 | 0.51462 | 1.00000 |
| test_raw | 6 | 0 | N/A | N/A |
| test_raw | 7 | 0 | N/A | N/A |
| test_raw | 8 | 0 | N/A | N/A |
| test_raw | 9 | 0 | N/A | N/A |
| test_scaled | 0 | 63 | 0.08652 | 0.11111 |
| test_scaled | 1 | 60 | 0.13311 | 0.13333 |
| test_scaled | 2 | 35 | 0.23872 | 0.40000 |
| test_scaled | 3 | 13 | 0.33505 | 0.69231 |
| test_scaled | 4 | 18 | 0.42757 | 0.77778 |
| test_scaled | 5 | 12 | 0.53270 | 0.41667 |
| test_scaled | 6 | 15 | 0.66189 | 0.06667 |
| test_scaled | 7 | 14 | 0.74000 | 0.28571 |
| test_scaled | 8 | 8 | 0.83152 | 1.00000 |
| test_scaled | 9 | 34 | 0.95509 | 0.73529 |
## LSTM seed 0 calibration
Temperature: 0.5416488577525241; episode thresholds: [0.23369891941547394, 0.3773441016674042]; encoder SHA256: 2fd87764fbbbe7ea17891580f03370583c01c93c26c01971306a4f19cc21c06b

| Partition | Bin | Count | Mean max probability | Accuracy |
|---|---|---|---|---|
| validation_raw | 0 | 165 | 0.05777 | 0.24242 |
| validation_raw | 1 | 53 | 0.14409 | 0.39623 |
| validation_raw | 2 | 23 | 0.25543 | 0.43478 |
| validation_raw | 3 | 24 | 0.30826 | 0.83333 |
| validation_raw | 4 | 0 | N/A | N/A |
| validation_raw | 5 | 0 | N/A | N/A |
| validation_raw | 6 | 0 | N/A | N/A |
| validation_raw | 7 | 0 | N/A | N/A |
| validation_raw | 8 | 0 | N/A | N/A |
| validation_raw | 9 | 0 | N/A | N/A |
| validation_scaled | 0 | 56 | 0.07287 | 0.19643 |
| validation_scaled | 1 | 56 | 0.15852 | 0.35714 |
| validation_scaled | 2 | 39 | 0.23915 | 0.23077 |
| validation_scaled | 3 | 21 | 0.35397 | 0.00000 |
| validation_scaled | 4 | 13 | 0.47088 | 0.23077 |
| validation_scaled | 5 | 20 | 0.55466 | 0.65000 |
| validation_scaled | 6 | 13 | 0.65804 | 0.38462 |
| validation_scaled | 7 | 8 | 0.76136 | 0.37500 |
| validation_scaled | 8 | 39 | 0.85418 | 0.69231 |
| validation_scaled | 9 | 0 | N/A | N/A |
| test_raw | 0 | 201 | 0.05349 | 0.19403 |
| test_raw | 1 | 31 | 0.14583 | 0.51613 |
| test_raw | 2 | 16 | 0.26105 | 0.50000 |
| test_raw | 3 | 24 | 0.30826 | 0.83333 |
| test_raw | 4 | 0 | N/A | N/A |
| test_raw | 5 | 0 | N/A | N/A |
| test_raw | 6 | 0 | N/A | N/A |
| test_raw | 7 | 0 | N/A | N/A |
| test_raw | 8 | 0 | N/A | N/A |
| test_raw | 9 | 0 | N/A | N/A |
| test_scaled | 0 | 81 | 0.07956 | 0.12346 |
| test_scaled | 1 | 75 | 0.14170 | 0.26667 |
| test_scaled | 2 | 29 | 0.22636 | 0.31034 |
| test_scaled | 3 | 20 | 0.34855 | 0.00000 |
| test_scaled | 4 | 6 | 0.48710 | 0.16667 |
| test_scaled | 5 | 15 | 0.56271 | 0.80000 |
| test_scaled | 6 | 6 | 0.65805 | 0.50000 |
| test_scaled | 7 | 4 | 0.76978 | 0.50000 |
| test_scaled | 8 | 36 | 0.85649 | 0.72222 |
| test_scaled | 9 | 0 | N/A | N/A |
## Transformer seed 0 calibration
Temperature: 0.547889749017796; episode thresholds: [0.19570745527744293, 0.35760247707366943]; encoder SHA256: b989c513df1e56bafb9c56728c4d5a5e5136494157781199097c9815301e6f82

| Partition | Bin | Count | Mean max probability | Accuracy |
|---|---|---|---|---|
| validation_raw | 0 | 204 | 0.05929 | 0.18627 |
| validation_raw | 1 | 29 | 0.14351 | 0.51724 |
| validation_raw | 2 | 3 | 0.21548 | 0.33333 |
| validation_raw | 3 | 29 | 0.38390 | 0.72414 |
| validation_raw | 4 | 0 | N/A | N/A |
| validation_raw | 5 | 0 | N/A | N/A |
| validation_raw | 6 | 0 | N/A | N/A |
| validation_raw | 7 | 0 | N/A | N/A |
| validation_raw | 8 | 0 | N/A | N/A |
| validation_raw | 9 | 0 | N/A | N/A |
| validation_scaled | 0 | 60 | 0.08228 | 0.13333 |
| validation_scaled | 1 | 88 | 0.13882 | 0.18182 |
| validation_scaled | 2 | 28 | 0.24174 | 0.28571 |
| validation_scaled | 3 | 37 | 0.33119 | 0.27027 |
| validation_scaled | 4 | 4 | 0.42318 | 1.00000 |
| validation_scaled | 5 | 5 | 0.55846 | 0.00000 |
| validation_scaled | 6 | 11 | 0.64499 | 0.63636 |
| validation_scaled | 7 | 3 | 0.73763 | 0.33333 |
| validation_scaled | 8 | 0 | N/A | N/A |
| validation_scaled | 9 | 29 | 0.92863 | 0.72414 |
| test_raw | 0 | 209 | 0.05974 | 0.17703 |
| test_raw | 1 | 33 | 0.12839 | 0.36364 |
| test_raw | 2 | 1 | 0.20290 | 1.00000 |
| test_raw | 3 | 29 | 0.38390 | 0.72414 |
| test_raw | 4 | 0 | N/A | N/A |
| test_raw | 5 | 0 | N/A | N/A |
| test_raw | 6 | 0 | N/A | N/A |
| test_raw | 7 | 0 | N/A | N/A |
| test_raw | 8 | 0 | N/A | N/A |
| test_raw | 9 | 0 | N/A | N/A |
| test_scaled | 0 | 56 | 0.08320 | 0.14286 |
| test_scaled | 1 | 102 | 0.15125 | 0.12745 |
| test_scaled | 2 | 26 | 0.23413 | 0.38462 |
| test_scaled | 3 | 44 | 0.33799 | 0.22727 |
| test_scaled | 4 | 4 | 0.42318 | 1.00000 |
| test_scaled | 5 | 4 | 0.56229 | 0.00000 |
| test_scaled | 6 | 6 | 0.64059 | 0.66667 |
| test_scaled | 7 | 1 | 0.71594 | 1.00000 |
| test_scaled | 8 | 0 | N/A | N/A |
| test_scaled | 9 | 29 | 0.92863 | 0.72414 |
## GRU IPPO baseline seed 0

| update | env_steps | train_dwell | val_dwell | val_depth | seconds |
|---|---|---|---|---|---|
| 1 | 16 | 0.00000 | 3.85714 | 3.71429 | 3.32089 |
| dwell | depth | protected | exposed | length | horizon | script | capacity_violations | lure_engagements | lure_chains | dead_ends | decoys_deployed | engaged_in_target | exposed_at | episode_reward | run | group | environment_repeat | sequence_certainty | confidence_group |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3.00000 | 3.00000 | 1.00000 | 1.00000 | 44.00000 | 44.00000 | S1 | 44.00000 | 0.00000 | 0.00000 | 0.00000 | 175.00000 | 3.00000 | 5.00000 | 3.00000 | scenario_1_b_c.j2 | 93fb0bdece9eb4b06d5621759bdddb12a4c6cb73cb9d85bcc4686567c973febd | 0 | 0.47259 | high |
| 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 | 44.00000 | S1 | 30.00000 | 0.00000 | 0.00000 | 0.00000 | 119.00000 | 2.00000 | 2.00000 | 2.00000 | scenario_1_c_c.j2 | b8894870ed5dd26fd324b7e5242c0dbc9ca42971f6f40e580f3f4abc5c88b233 | 0 | 0.48682 | high |
| 3.00000 | 3.00000 | 0.00000 | 1.00000 | 32.00000 | 51.00000 | S1 | 32.00000 | 3.00000 | 0.00000 | 0.00000 | 127.00000 | 1.00000 | 23.00000 | 3.00000 | scenario_1_d_a.j2 | f78f864ba7b16a4cb55909a2f99f016c3cb0a56c3d6915054ecb65e62b7edfe0 | 0 | 0.47639 | high |
| 3.00000 | 3.00000 | 0.00000 | 1.00000 | 30.00000 | 46.00000 | S1 | 30.00000 | 0.00000 | 0.00000 | 0.00000 | 119.00000 | 3.00000 | 28.00000 | 3.00000 | scenario_1_e_a.j2 | 3519cf18b1dfaed57f30a4ac04c186e8e9f9063aa1012ac46be0d8339f2c7499 | 0 | 0.44296 | medium |
| 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 | 25.00000 | S3 | 16.00000 | 2.00000 | 0.00000 | 0.00000 | 63.00000 | 1.00000 | -1.00000 | 2.00000 | scenario_3_a_b.j2 | 5fd306c58b8996decd7b5f08199ce000446ea0262cdb556ef4e998c4ddc403fe | 0 | 0.13014 | low |
| 5.00000 | 3.00000 | 0.00000 | 1.00000 | 15.00000 | 24.00000 | S3 | 15.00000 | 5.00000 | 3.00000 | 0.00000 | 58.00000 | 2.00000 | 7.00000 | 5.00000 | scenario_3_b_b.j2 | 339f6d168b5df02964f55501786fc78bdd0460dcad2eaf1cfc7d24f3f5ca5e97 | 0 | 0.15416 | low |
| 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 | 45.00000 | S6 | 2.00000 | 0.00000 | 0.00000 | 0.00000 | 7.00000 | 0.00000 | -1.00000 | 0.00000 | scenario_6_c.j2 | 497137828a7e4894a21fcb0a2ca19c647410f50cd8eec09905696391186176e2 | 0 | 0.16012 | low |
## GRU IPPO confidence seed 0

| update | env_steps | train_dwell | val_dwell | val_depth | seconds |
|---|---|---|---|---|---|
| 1 | 16 | 0.00000 | 3.85714 | 3.71429 | 3.36811 |
| dwell | depth | protected | exposed | length | horizon | script | capacity_violations | lure_engagements | lure_chains | dead_ends | decoys_deployed | engaged_in_target | exposed_at | episode_reward | run | group | environment_repeat | sequence_certainty | confidence_group |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3.00000 | 3.00000 | 1.00000 | 1.00000 | 44.00000 | 44.00000 | S1 | 44.00000 | 0.00000 | 0.00000 | 0.00000 | 175.00000 | 3.00000 | 5.00000 | 3.00000 | scenario_1_b_c.j2 | 93fb0bdece9eb4b06d5621759bdddb12a4c6cb73cb9d85bcc4686567c973febd | 0 | 0.47259 | high |
| 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 | 44.00000 | S1 | 30.00000 | 0.00000 | 0.00000 | 0.00000 | 119.00000 | 2.00000 | 2.00000 | 2.00000 | scenario_1_c_c.j2 | b8894870ed5dd26fd324b7e5242c0dbc9ca42971f6f40e580f3f4abc5c88b233 | 0 | 0.48682 | high |
| 3.00000 | 3.00000 | 0.00000 | 1.00000 | 32.00000 | 51.00000 | S1 | 32.00000 | 3.00000 | 0.00000 | 0.00000 | 127.00000 | 1.00000 | 23.00000 | 3.00000 | scenario_1_d_a.j2 | f78f864ba7b16a4cb55909a2f99f016c3cb0a56c3d6915054ecb65e62b7edfe0 | 0 | 0.47639 | high |
| 3.00000 | 3.00000 | 0.00000 | 1.00000 | 30.00000 | 46.00000 | S1 | 30.00000 | 0.00000 | 0.00000 | 0.00000 | 119.00000 | 3.00000 | 28.00000 | 3.00000 | scenario_1_e_a.j2 | 3519cf18b1dfaed57f30a4ac04c186e8e9f9063aa1012ac46be0d8339f2c7499 | 0 | 0.44296 | medium |
| 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 | 25.00000 | S3 | 16.00000 | 2.00000 | 0.00000 | 0.00000 | 63.00000 | 1.00000 | -1.00000 | 2.00000 | scenario_3_a_b.j2 | 5fd306c58b8996decd7b5f08199ce000446ea0262cdb556ef4e998c4ddc403fe | 0 | 0.13014 | low |
| 5.00000 | 3.00000 | 0.00000 | 1.00000 | 15.00000 | 24.00000 | S3 | 15.00000 | 5.00000 | 3.00000 | 0.00000 | 59.00000 | 2.00000 | 7.00000 | 5.00000 | scenario_3_b_b.j2 | 339f6d168b5df02964f55501786fc78bdd0460dcad2eaf1cfc7d24f3f5ca5e97 | 0 | 0.15416 | low |
| 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 | 45.00000 | S6 | 2.00000 | 0.00000 | 0.00000 | 0.00000 | 7.00000 | 0.00000 | -1.00000 | 0.00000 | scenario_6_c.j2 | 497137828a7e4894a21fcb0a2ca19c647410f50cd8eec09905696391186176e2 | 0 | 0.16012 | low |
## GRU MAPPO baseline seed 0

| update | env_steps | train_dwell | val_dwell | val_depth | seconds |
|---|---|---|---|---|---|
| 1 | 16 | 0.00000 | 2.71429 | 2.57143 | 3.43841 |
| dwell | depth | protected | exposed | length | horizon | script | capacity_violations | lure_engagements | lure_chains | dead_ends | decoys_deployed | engaged_in_target | exposed_at | episode_reward | run | group | environment_repeat | sequence_certainty | confidence_group |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2.00000 | 2.00000 | 1.00000 | 1.00000 | 44.00000 | 44.00000 | S1 | 44.00000 | 1.00000 | 0.00000 | 0.00000 | 176.00000 | 2.00000 | 35.00000 | 2.00000 | scenario_1_b_c.j2 | 93fb0bdece9eb4b06d5621759bdddb12a4c6cb73cb9d85bcc4686567c973febd | 0 | 0.47259 | high |
| 3.00000 | 3.00000 | 0.00000 | 1.00000 | 30.00000 | 44.00000 | S1 | 30.00000 | 0.00000 | 0.00000 | 0.00000 | 120.00000 | 3.00000 | 10.00000 | 3.00000 | scenario_1_c_c.j2 | b8894870ed5dd26fd324b7e5242c0dbc9ca42971f6f40e580f3f4abc5c88b233 | 0 | 0.48682 | high |
| 3.00000 | 1.00000 | 0.00000 | 1.00000 | 32.00000 | 51.00000 | S1 | 32.00000 | 1.00000 | 0.00000 | 0.00000 | 128.00000 | 2.00000 | 16.00000 | 3.00000 | scenario_1_d_a.j2 | f78f864ba7b16a4cb55909a2f99f016c3cb0a56c3d6915054ecb65e62b7edfe0 | 0 | 0.47639 | high |
| 4.00000 | 1.00000 | 0.00000 | 1.00000 | 30.00000 | 46.00000 | S1 | 30.00000 | 0.00000 | 0.00000 | 0.00000 | 120.00000 | 4.00000 | 14.00000 | 4.00000 | scenario_1_e_a.j2 | 3519cf18b1dfaed57f30a4ac04c186e8e9f9063aa1012ac46be0d8339f2c7499 | 0 | 0.44296 | medium |
| 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 | 25.00000 | S3 | 16.00000 | 2.00000 | 0.00000 | 0.00000 | 64.00000 | 1.00000 | -1.00000 | 2.00000 | scenario_3_a_b.j2 | 5fd306c58b8996decd7b5f08199ce000446ea0262cdb556ef4e998c4ddc403fe | 0 | 0.13014 | low |
| 6.00000 | 4.00000 | 0.00000 | 1.00000 | 15.00000 | 24.00000 | S3 | 15.00000 | 6.00000 | 3.00000 | 0.00000 | 60.00000 | 3.00000 | 7.00000 | 6.00000 | scenario_3_b_b.j2 | 339f6d168b5df02964f55501786fc78bdd0460dcad2eaf1cfc7d24f3f5ca5e97 | 0 | 0.15416 | low |
| 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 | 45.00000 | S6 | 2.00000 | 0.00000 | 0.00000 | 0.00000 | 8.00000 | 0.00000 | -1.00000 | 0.00000 | scenario_6_c.j2 | 497137828a7e4894a21fcb0a2ca19c647410f50cd8eec09905696391186176e2 | 0 | 0.16012 | low |
## GRU MAPPO confidence seed 0

| update | env_steps | train_dwell | val_dwell | val_depth | seconds |
|---|---|---|---|---|---|
| 1 | 16 | 0.00000 | 2.28571 | 2.14286 | 3.33316 |
| dwell | depth | protected | exposed | length | horizon | script | capacity_violations | lure_engagements | lure_chains | dead_ends | decoys_deployed | engaged_in_target | exposed_at | episode_reward | run | group | environment_repeat | sequence_certainty | confidence_group |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2.00000 | 2.00000 | 1.00000 | 1.00000 | 44.00000 | 44.00000 | S1 | 44.00000 | 1.00000 | 0.00000 | 0.00000 | 176.00000 | 2.00000 | 35.00000 | 2.00000 | scenario_1_b_c.j2 | 93fb0bdece9eb4b06d5621759bdddb12a4c6cb73cb9d85bcc4686567c973febd | 0 | 0.47259 | high |
| 3.00000 | 3.00000 | 0.00000 | 1.00000 | 30.00000 | 44.00000 | S1 | 30.00000 | 0.00000 | 0.00000 | 0.00000 | 120.00000 | 3.00000 | 10.00000 | 3.00000 | scenario_1_c_c.j2 | b8894870ed5dd26fd324b7e5242c0dbc9ca42971f6f40e580f3f4abc5c88b233 | 0 | 0.48682 | high |
| 3.00000 | 1.00000 | 0.00000 | 1.00000 | 32.00000 | 51.00000 | S1 | 32.00000 | 1.00000 | 0.00000 | 0.00000 | 128.00000 | 2.00000 | 16.00000 | 3.00000 | scenario_1_d_a.j2 | f78f864ba7b16a4cb55909a2f99f016c3cb0a56c3d6915054ecb65e62b7edfe0 | 0 | 0.47639 | high |
| 4.00000 | 1.00000 | 0.00000 | 1.00000 | 30.00000 | 46.00000 | S1 | 30.00000 | 0.00000 | 0.00000 | 0.00000 | 120.00000 | 4.00000 | 14.00000 | 4.00000 | scenario_1_e_a.j2 | 3519cf18b1dfaed57f30a4ac04c186e8e9f9063aa1012ac46be0d8339f2c7499 | 0 | 0.44296 | medium |
| 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 | 25.00000 | S3 | 16.00000 | 2.00000 | 0.00000 | 0.00000 | 64.00000 | 1.00000 | -1.00000 | 2.00000 | scenario_3_a_b.j2 | 5fd306c58b8996decd7b5f08199ce000446ea0262cdb556ef4e998c4ddc403fe | 0 | 0.13014 | low |
| 6.00000 | 4.00000 | 0.00000 | 1.00000 | 15.00000 | 24.00000 | S3 | 15.00000 | 6.00000 | 3.00000 | 0.00000 | 60.00000 | 3.00000 | 7.00000 | 6.00000 | scenario_3_b_b.j2 | 339f6d168b5df02964f55501786fc78bdd0460dcad2eaf1cfc7d24f3f5ca5e97 | 0 | 0.15416 | low |
| 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 | 45.00000 | S6 | 2.00000 | 0.00000 | 0.00000 | 0.00000 | 8.00000 | 0.00000 | -1.00000 | 0.00000 | scenario_6_c.j2 | 497137828a7e4894a21fcb0a2ca19c647410f50cd8eec09905696391186176e2 | 0 | 0.16012 | low |
## LSTM IPPO baseline seed 0

| update | env_steps | train_dwell | val_dwell | val_depth | seconds |
|---|---|---|---|---|---|
| 1 | 16 | 0.00000 | 3.28571 | 3.14286 | 5.71926 |
| dwell | depth | protected | exposed | length | horizon | script | capacity_violations | lure_engagements | lure_chains | dead_ends | decoys_deployed | engaged_in_target | exposed_at | episode_reward | run | group | environment_repeat | sequence_certainty | confidence_group |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3.00000 | 3.00000 | 1.00000 | 1.00000 | 44.00000 | 44.00000 | S1 | 44.00000 | 0.00000 | 0.00000 | 0.00000 | 175.00000 | 3.00000 | 5.00000 | 3.00000 | scenario_1_b_c.j2 | 93fb0bdece9eb4b06d5621759bdddb12a4c6cb73cb9d85bcc4686567c973febd | 0 | 0.31942 | medium |
| 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 | 44.00000 | S1 | 30.00000 | 0.00000 | 0.00000 | 0.00000 | 119.00000 | 2.00000 | 2.00000 | 2.00000 | scenario_1_c_c.j2 | b8894870ed5dd26fd324b7e5242c0dbc9ca42971f6f40e580f3f4abc5c88b233 | 0 | 0.36645 | medium |
| 4.00000 | 4.00000 | 0.00000 | 1.00000 | 32.00000 | 51.00000 | S1 | 32.00000 | 3.00000 | 0.00000 | 0.00000 | 127.00000 | 2.00000 | 23.00000 | 4.00000 | scenario_1_d_a.j2 | f78f864ba7b16a4cb55909a2f99f016c3cb0a56c3d6915054ecb65e62b7edfe0 | 0 | 0.37259 | medium |
| 4.00000 | 4.00000 | 0.00000 | 1.00000 | 30.00000 | 46.00000 | S1 | 30.00000 | 0.00000 | 0.00000 | 0.00000 | 119.00000 | 4.00000 | 28.00000 | 4.00000 | scenario_1_e_a.j2 | 3519cf18b1dfaed57f30a4ac04c186e8e9f9063aa1012ac46be0d8339f2c7499 | 0 | 0.37947 | high |
| 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 | 25.00000 | S3 | 16.00000 | 2.00000 | 0.00000 | 0.00000 | 63.00000 | 1.00000 | -1.00000 | 2.00000 | scenario_3_a_b.j2 | 5fd306c58b8996decd7b5f08199ce000446ea0262cdb556ef4e998c4ddc403fe | 0 | 0.11316 | low |
| 2.00000 | 2.00000 | 0.00000 | 1.00000 | 15.00000 | 24.00000 | S3 | 15.00000 | 2.00000 | 0.00000 | 0.00000 | 58.00000 | 1.00000 | 7.00000 | 2.00000 | scenario_3_b_b.j2 | 339f6d168b5df02964f55501786fc78bdd0460dcad2eaf1cfc7d24f3f5ca5e97 | 0 | 0.12883 | low |
| 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 | 45.00000 | S6 | 2.00000 | 0.00000 | 0.00000 | 0.00000 | 7.00000 | 0.00000 | -1.00000 | 0.00000 | scenario_6_c.j2 | 497137828a7e4894a21fcb0a2ca19c647410f50cd8eec09905696391186176e2 | 0 | 0.14125 | low |
## LSTM IPPO confidence seed 0

| update | env_steps | train_dwell | val_dwell | val_depth | seconds |
|---|---|---|---|---|---|
| 1 | 16 | 0.00000 | 3.28571 | 3.14286 | 4.57442 |
| dwell | depth | protected | exposed | length | horizon | script | capacity_violations | lure_engagements | lure_chains | dead_ends | decoys_deployed | engaged_in_target | exposed_at | episode_reward | run | group | environment_repeat | sequence_certainty | confidence_group |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3.00000 | 3.00000 | 1.00000 | 1.00000 | 44.00000 | 44.00000 | S1 | 44.00000 | 0.00000 | 0.00000 | 0.00000 | 175.00000 | 3.00000 | 5.00000 | 3.00000 | scenario_1_b_c.j2 | 93fb0bdece9eb4b06d5621759bdddb12a4c6cb73cb9d85bcc4686567c973febd | 0 | 0.31942 | medium |
| 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 | 44.00000 | S1 | 30.00000 | 0.00000 | 0.00000 | 0.00000 | 119.00000 | 2.00000 | 2.00000 | 2.00000 | scenario_1_c_c.j2 | b8894870ed5dd26fd324b7e5242c0dbc9ca42971f6f40e580f3f4abc5c88b233 | 0 | 0.36645 | medium |
| 4.00000 | 4.00000 | 0.00000 | 1.00000 | 32.00000 | 51.00000 | S1 | 32.00000 | 3.00000 | 0.00000 | 0.00000 | 127.00000 | 2.00000 | 23.00000 | 4.00000 | scenario_1_d_a.j2 | f78f864ba7b16a4cb55909a2f99f016c3cb0a56c3d6915054ecb65e62b7edfe0 | 0 | 0.37259 | medium |
| 4.00000 | 4.00000 | 0.00000 | 1.00000 | 30.00000 | 46.00000 | S1 | 30.00000 | 0.00000 | 0.00000 | 0.00000 | 119.00000 | 4.00000 | 28.00000 | 4.00000 | scenario_1_e_a.j2 | 3519cf18b1dfaed57f30a4ac04c186e8e9f9063aa1012ac46be0d8339f2c7499 | 0 | 0.37947 | high |
| 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 | 25.00000 | S3 | 16.00000 | 2.00000 | 0.00000 | 0.00000 | 63.00000 | 1.00000 | -1.00000 | 2.00000 | scenario_3_a_b.j2 | 5fd306c58b8996decd7b5f08199ce000446ea0262cdb556ef4e998c4ddc403fe | 0 | 0.11316 | low |
| 2.00000 | 2.00000 | 0.00000 | 1.00000 | 15.00000 | 24.00000 | S3 | 15.00000 | 2.00000 | 0.00000 | 0.00000 | 58.00000 | 1.00000 | 7.00000 | 2.00000 | scenario_3_b_b.j2 | 339f6d168b5df02964f55501786fc78bdd0460dcad2eaf1cfc7d24f3f5ca5e97 | 0 | 0.12883 | low |
| 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 | 45.00000 | S6 | 2.00000 | 0.00000 | 0.00000 | 0.00000 | 7.00000 | 0.00000 | -1.00000 | 0.00000 | scenario_6_c.j2 | 497137828a7e4894a21fcb0a2ca19c647410f50cd8eec09905696391186176e2 | 0 | 0.14125 | low |
## LSTM MAPPO baseline seed 0

| update | env_steps | train_dwell | val_dwell | val_depth | seconds |
|---|---|---|---|---|---|
| 1 | 16 | 0.00000 | 3.85714 | 3.00000 | 4.91504 |
| dwell | depth | protected | exposed | length | horizon | script | capacity_violations | lure_engagements | lure_chains | dead_ends | decoys_deployed | engaged_in_target | exposed_at | episode_reward | run | group | environment_repeat | sequence_certainty | confidence_group |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 8.00000 | 6.00000 | 1.00000 | 0.00000 | 44.00000 | 44.00000 | S1 | 44.00000 | 0.00000 | 0.00000 | 0.00000 | 176.00000 | 8.00000 | -1.00000 | 8.00000 | scenario_1_b_c.j2 | 93fb0bdece9eb4b06d5621759bdddb12a4c6cb73cb9d85bcc4686567c973febd | 0 | 0.31942 | medium |
| 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 | 44.00000 | S1 | 30.00000 | 0.00000 | 0.00000 | 0.00000 | 120.00000 | 2.00000 | 6.00000 | 2.00000 | scenario_1_c_c.j2 | b8894870ed5dd26fd324b7e5242c0dbc9ca42971f6f40e580f3f4abc5c88b233 | 0 | 0.36645 | medium |
| 5.00000 | 1.00000 | 0.00000 | 1.00000 | 32.00000 | 51.00000 | S1 | 32.00000 | 0.00000 | 0.00000 | 0.00000 | 128.00000 | 4.00000 | 16.00000 | 5.00000 | scenario_1_d_a.j2 | f78f864ba7b16a4cb55909a2f99f016c3cb0a56c3d6915054ecb65e62b7edfe0 | 0 | 0.37259 | medium |
| 6.00000 | 1.00000 | 0.00000 | 1.00000 | 30.00000 | 46.00000 | S1 | 30.00000 | 0.00000 | 0.00000 | 0.00000 | 120.00000 | 5.00000 | 14.00000 | 6.00000 | scenario_1_e_a.j2 | 3519cf18b1dfaed57f30a4ac04c186e8e9f9063aa1012ac46be0d8339f2c7499 | 0 | 0.37947 | high |
| 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 | 25.00000 | S3 | 16.00000 | 0.00000 | 0.00000 | 0.00000 | 64.00000 | 1.00000 | -1.00000 | 2.00000 | scenario_3_a_b.j2 | 5fd306c58b8996decd7b5f08199ce000446ea0262cdb556ef4e998c4ddc403fe | 0 | 0.11316 | low |
| 1.00000 | 1.00000 | 0.00000 | 1.00000 | 15.00000 | 24.00000 | S3 | 15.00000 | 0.00000 | 0.00000 | 0.00000 | 60.00000 | 1.00000 | 7.00000 | 1.00000 | scenario_3_b_b.j2 | 339f6d168b5df02964f55501786fc78bdd0460dcad2eaf1cfc7d24f3f5ca5e97 | 0 | 0.12883 | low |
| 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 | 45.00000 | S6 | 2.00000 | 0.00000 | 0.00000 | 0.00000 | 8.00000 | 0.00000 | -1.00000 | 0.00000 | scenario_6_c.j2 | 497137828a7e4894a21fcb0a2ca19c647410f50cd8eec09905696391186176e2 | 0 | 0.14125 | low |
## LSTM MAPPO confidence seed 0

| update | env_steps | train_dwell | val_dwell | val_depth | seconds |
|---|---|---|---|---|---|
| 1 | 16 | 0.00000 | 3.85714 | 3.00000 | 4.78499 |
| dwell | depth | protected | exposed | length | horizon | script | capacity_violations | lure_engagements | lure_chains | dead_ends | decoys_deployed | engaged_in_target | exposed_at | episode_reward | run | group | environment_repeat | sequence_certainty | confidence_group |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 8.00000 | 6.00000 | 1.00000 | 0.00000 | 44.00000 | 44.00000 | S1 | 44.00000 | 0.00000 | 0.00000 | 0.00000 | 176.00000 | 8.00000 | -1.00000 | 8.00000 | scenario_1_b_c.j2 | 93fb0bdece9eb4b06d5621759bdddb12a4c6cb73cb9d85bcc4686567c973febd | 0 | 0.31942 | medium |
| 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 | 44.00000 | S1 | 30.00000 | 0.00000 | 0.00000 | 0.00000 | 120.00000 | 2.00000 | 6.00000 | 2.00000 | scenario_1_c_c.j2 | b8894870ed5dd26fd324b7e5242c0dbc9ca42971f6f40e580f3f4abc5c88b233 | 0 | 0.36645 | medium |
| 5.00000 | 1.00000 | 0.00000 | 1.00000 | 32.00000 | 51.00000 | S1 | 32.00000 | 0.00000 | 0.00000 | 0.00000 | 128.00000 | 4.00000 | 16.00000 | 5.00000 | scenario_1_d_a.j2 | f78f864ba7b16a4cb55909a2f99f016c3cb0a56c3d6915054ecb65e62b7edfe0 | 0 | 0.37259 | medium |
| 6.00000 | 1.00000 | 0.00000 | 1.00000 | 30.00000 | 46.00000 | S1 | 30.00000 | 0.00000 | 0.00000 | 0.00000 | 120.00000 | 5.00000 | 14.00000 | 6.00000 | scenario_1_e_a.j2 | 3519cf18b1dfaed57f30a4ac04c186e8e9f9063aa1012ac46be0d8339f2c7499 | 0 | 0.37947 | high |
| 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 | 25.00000 | S3 | 16.00000 | 0.00000 | 0.00000 | 0.00000 | 64.00000 | 1.00000 | -1.00000 | 2.00000 | scenario_3_a_b.j2 | 5fd306c58b8996decd7b5f08199ce000446ea0262cdb556ef4e998c4ddc403fe | 0 | 0.11316 | low |
| 1.00000 | 1.00000 | 0.00000 | 1.00000 | 15.00000 | 24.00000 | S3 | 15.00000 | 0.00000 | 0.00000 | 0.00000 | 60.00000 | 1.00000 | 7.00000 | 1.00000 | scenario_3_b_b.j2 | 339f6d168b5df02964f55501786fc78bdd0460dcad2eaf1cfc7d24f3f5ca5e97 | 0 | 0.12883 | low |
| 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 | 45.00000 | S6 | 2.00000 | 0.00000 | 0.00000 | 0.00000 | 8.00000 | 0.00000 | -1.00000 | 0.00000 | scenario_6_c.j2 | 497137828a7e4894a21fcb0a2ca19c647410f50cd8eec09905696391186176e2 | 0 | 0.14125 | low |
## Transformer IPPO baseline seed 0

| update | env_steps | train_dwell | val_dwell | val_depth | seconds |
|---|---|---|---|---|---|
| 1 | 16 | 0.00000 | 3.71429 | 3.57143 | 12.77642 |
| dwell | depth | protected | exposed | length | horizon | script | capacity_violations | lure_engagements | lure_chains | dead_ends | decoys_deployed | engaged_in_target | exposed_at | episode_reward | run | group | environment_repeat | sequence_certainty | confidence_group |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3.00000 | 3.00000 | 1.00000 | 1.00000 | 44.00000 | 44.00000 | S1 | 44.00000 | 0.00000 | 0.00000 | 0.00000 | 175.00000 | 3.00000 | 5.00000 | 3.00000 | scenario_1_b_c.j2 | 93fb0bdece9eb4b06d5621759bdddb12a4c6cb73cb9d85bcc4686567c973febd | 0 | 0.32753 | medium |
| 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 | 44.00000 | S1 | 30.00000 | 0.00000 | 0.00000 | 0.00000 | 119.00000 | 2.00000 | 6.00000 | 2.00000 | scenario_1_c_c.j2 | b8894870ed5dd26fd324b7e5242c0dbc9ca42971f6f40e580f3f4abc5c88b233 | 0 | 0.35878 | high |
| 3.00000 | 3.00000 | 0.00000 | 1.00000 | 32.00000 | 51.00000 | S1 | 32.00000 | 3.00000 | 0.00000 | 0.00000 | 127.00000 | 1.00000 | 23.00000 | 3.00000 | scenario_1_d_a.j2 | f78f864ba7b16a4cb55909a2f99f016c3cb0a56c3d6915054ecb65e62b7edfe0 | 0 | 0.31444 | medium |
| 2.00000 | 2.00000 | 0.00000 | 0.00000 | 30.00000 | 46.00000 | S1 | 30.00000 | 0.00000 | 0.00000 | 0.00000 | 119.00000 | 2.00000 | -1.00000 | 2.00000 | scenario_1_e_a.j2 | 3519cf18b1dfaed57f30a4ac04c186e8e9f9063aa1012ac46be0d8339f2c7499 | 0 | 0.36063 | high |
| 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 | 25.00000 | S3 | 16.00000 | 2.00000 | 0.00000 | 0.00000 | 63.00000 | 1.00000 | -1.00000 | 2.00000 | scenario_3_a_b.j2 | 5fd306c58b8996decd7b5f08199ce000446ea0262cdb556ef4e998c4ddc403fe | 0 | 0.14084 | low |
| 5.00000 | 3.00000 | 0.00000 | 1.00000 | 15.00000 | 24.00000 | S3 | 15.00000 | 5.00000 | 3.00000 | 0.00000 | 59.00000 | 2.00000 | 7.00000 | 5.00000 | scenario_3_b_b.j2 | 339f6d168b5df02964f55501786fc78bdd0460dcad2eaf1cfc7d24f3f5ca5e97 | 0 | 0.14938 | low |
| 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 | 45.00000 | S6 | 2.00000 | 0.00000 | 0.00000 | 0.00000 | 7.00000 | 0.00000 | -1.00000 | 0.00000 | scenario_6_c.j2 | 497137828a7e4894a21fcb0a2ca19c647410f50cd8eec09905696391186176e2 | 0 | 0.19675 | medium |
## Transformer IPPO confidence seed 0

| update | env_steps | train_dwell | val_dwell | val_depth | seconds |
|---|---|---|---|---|---|
| 1 | 16 | 0.00000 | 3.71429 | 3.57143 | 12.56138 |
| dwell | depth | protected | exposed | length | horizon | script | capacity_violations | lure_engagements | lure_chains | dead_ends | decoys_deployed | engaged_in_target | exposed_at | episode_reward | run | group | environment_repeat | sequence_certainty | confidence_group |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3.00000 | 3.00000 | 1.00000 | 1.00000 | 44.00000 | 44.00000 | S1 | 44.00000 | 0.00000 | 0.00000 | 0.00000 | 175.00000 | 3.00000 | 5.00000 | 3.00000 | scenario_1_b_c.j2 | 93fb0bdece9eb4b06d5621759bdddb12a4c6cb73cb9d85bcc4686567c973febd | 0 | 0.32753 | medium |
| 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 | 44.00000 | S1 | 30.00000 | 0.00000 | 0.00000 | 0.00000 | 119.00000 | 2.00000 | 6.00000 | 2.00000 | scenario_1_c_c.j2 | b8894870ed5dd26fd324b7e5242c0dbc9ca42971f6f40e580f3f4abc5c88b233 | 0 | 0.35878 | high |
| 3.00000 | 3.00000 | 0.00000 | 1.00000 | 32.00000 | 51.00000 | S1 | 32.00000 | 3.00000 | 0.00000 | 0.00000 | 127.00000 | 1.00000 | 23.00000 | 3.00000 | scenario_1_d_a.j2 | f78f864ba7b16a4cb55909a2f99f016c3cb0a56c3d6915054ecb65e62b7edfe0 | 0 | 0.31444 | medium |
| 2.00000 | 2.00000 | 0.00000 | 0.00000 | 30.00000 | 46.00000 | S1 | 30.00000 | 0.00000 | 0.00000 | 0.00000 | 119.00000 | 2.00000 | -1.00000 | 2.00000 | scenario_1_e_a.j2 | 3519cf18b1dfaed57f30a4ac04c186e8e9f9063aa1012ac46be0d8339f2c7499 | 0 | 0.36063 | high |
| 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 | 25.00000 | S3 | 16.00000 | 2.00000 | 0.00000 | 0.00000 | 63.00000 | 1.00000 | -1.00000 | 2.00000 | scenario_3_a_b.j2 | 5fd306c58b8996decd7b5f08199ce000446ea0262cdb556ef4e998c4ddc403fe | 0 | 0.14084 | low |
| 5.00000 | 3.00000 | 0.00000 | 1.00000 | 15.00000 | 24.00000 | S3 | 15.00000 | 5.00000 | 3.00000 | 0.00000 | 59.00000 | 2.00000 | 7.00000 | 5.00000 | scenario_3_b_b.j2 | 339f6d168b5df02964f55501786fc78bdd0460dcad2eaf1cfc7d24f3f5ca5e97 | 0 | 0.14938 | low |
| 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 | 45.00000 | S6 | 2.00000 | 0.00000 | 0.00000 | 0.00000 | 7.00000 | 0.00000 | -1.00000 | 0.00000 | scenario_6_c.j2 | 497137828a7e4894a21fcb0a2ca19c647410f50cd8eec09905696391186176e2 | 0 | 0.19675 | medium |
## Transformer MAPPO baseline seed 0

| update | env_steps | train_dwell | val_dwell | val_depth | seconds |
|---|---|---|---|---|---|
| 1 | 16 | 0.00000 | 3.71429 | 3.57143 | 12.65576 |
| dwell | depth | protected | exposed | length | horizon | script | capacity_violations | lure_engagements | lure_chains | dead_ends | decoys_deployed | engaged_in_target | exposed_at | episode_reward | run | group | environment_repeat | sequence_certainty | confidence_group |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2.00000 | 2.00000 | 1.00000 | 1.00000 | 44.00000 | 44.00000 | S1 | 44.00000 | 0.00000 | 0.00000 | 0.00000 | 176.00000 | 2.00000 | 5.00000 | 2.00000 | scenario_1_b_c.j2 | 93fb0bdece9eb4b06d5621759bdddb12a4c6cb73cb9d85bcc4686567c973febd | 0 | 0.32753 | medium |
| 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 | 44.00000 | S1 | 30.00000 | 0.00000 | 0.00000 | 0.00000 | 120.00000 | 2.00000 | 2.00000 | 2.00000 | scenario_1_c_c.j2 | b8894870ed5dd26fd324b7e5242c0dbc9ca42971f6f40e580f3f4abc5c88b233 | 0 | 0.35878 | high |
| 3.00000 | 3.00000 | 0.00000 | 1.00000 | 32.00000 | 51.00000 | S1 | 32.00000 | 3.00000 | 0.00000 | 0.00000 | 128.00000 | 1.00000 | 23.00000 | 3.00000 | scenario_1_d_a.j2 | f78f864ba7b16a4cb55909a2f99f016c3cb0a56c3d6915054ecb65e62b7edfe0 | 0 | 0.31444 | medium |
| 3.00000 | 3.00000 | 0.00000 | 0.00000 | 30.00000 | 46.00000 | S1 | 30.00000 | 0.00000 | 0.00000 | 0.00000 | 120.00000 | 3.00000 | -1.00000 | 3.00000 | scenario_1_e_a.j2 | 3519cf18b1dfaed57f30a4ac04c186e8e9f9063aa1012ac46be0d8339f2c7499 | 0 | 0.36063 | high |
| 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 | 25.00000 | S3 | 16.00000 | 2.00000 | 0.00000 | 0.00000 | 64.00000 | 1.00000 | -1.00000 | 2.00000 | scenario_3_a_b.j2 | 5fd306c58b8996decd7b5f08199ce000446ea0262cdb556ef4e998c4ddc403fe | 0 | 0.14084 | low |
| 6.00000 | 4.00000 | 0.00000 | 1.00000 | 15.00000 | 24.00000 | S3 | 15.00000 | 6.00000 | 3.00000 | 0.00000 | 60.00000 | 3.00000 | 7.00000 | 6.00000 | scenario_3_b_b.j2 | 339f6d168b5df02964f55501786fc78bdd0460dcad2eaf1cfc7d24f3f5ca5e97 | 0 | 0.14938 | low |
| 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 | 45.00000 | S6 | 2.00000 | 0.00000 | 0.00000 | 0.00000 | 8.00000 | 0.00000 | -1.00000 | 0.00000 | scenario_6_c.j2 | 497137828a7e4894a21fcb0a2ca19c647410f50cd8eec09905696391186176e2 | 0 | 0.19675 | medium |
## Transformer MAPPO confidence seed 0

| update | env_steps | train_dwell | val_dwell | val_depth | seconds |
|---|---|---|---|---|---|
| 1 | 16 | 0.00000 | 3.71429 | 3.57143 | 12.23709 |
| dwell | depth | protected | exposed | length | horizon | script | capacity_violations | lure_engagements | lure_chains | dead_ends | decoys_deployed | engaged_in_target | exposed_at | episode_reward | run | group | environment_repeat | sequence_certainty | confidence_group |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2.00000 | 2.00000 | 1.00000 | 1.00000 | 44.00000 | 44.00000 | S1 | 44.00000 | 0.00000 | 0.00000 | 0.00000 | 176.00000 | 2.00000 | 5.00000 | 2.00000 | scenario_1_b_c.j2 | 93fb0bdece9eb4b06d5621759bdddb12a4c6cb73cb9d85bcc4686567c973febd | 0 | 0.32753 | medium |
| 2.00000 | 2.00000 | 0.00000 | 1.00000 | 30.00000 | 44.00000 | S1 | 30.00000 | 0.00000 | 0.00000 | 0.00000 | 120.00000 | 2.00000 | 2.00000 | 2.00000 | scenario_1_c_c.j2 | b8894870ed5dd26fd324b7e5242c0dbc9ca42971f6f40e580f3f4abc5c88b233 | 0 | 0.35878 | high |
| 3.00000 | 3.00000 | 0.00000 | 1.00000 | 32.00000 | 51.00000 | S1 | 32.00000 | 3.00000 | 0.00000 | 0.00000 | 128.00000 | 1.00000 | 23.00000 | 3.00000 | scenario_1_d_a.j2 | f78f864ba7b16a4cb55909a2f99f016c3cb0a56c3d6915054ecb65e62b7edfe0 | 0 | 0.31444 | medium |
| 3.00000 | 3.00000 | 0.00000 | 0.00000 | 30.00000 | 46.00000 | S1 | 30.00000 | 0.00000 | 0.00000 | 0.00000 | 120.00000 | 3.00000 | -1.00000 | 3.00000 | scenario_1_e_a.j2 | 3519cf18b1dfaed57f30a4ac04c186e8e9f9063aa1012ac46be0d8339f2c7499 | 0 | 0.36063 | high |
| 2.00000 | 2.00000 | 0.00000 | 0.00000 | 16.00000 | 25.00000 | S3 | 16.00000 | 2.00000 | 0.00000 | 0.00000 | 64.00000 | 1.00000 | -1.00000 | 2.00000 | scenario_3_a_b.j2 | 5fd306c58b8996decd7b5f08199ce000446ea0262cdb556ef4e998c4ddc403fe | 0 | 0.14084 | low |
| 6.00000 | 4.00000 | 0.00000 | 1.00000 | 15.00000 | 24.00000 | S3 | 15.00000 | 6.00000 | 3.00000 | 0.00000 | 60.00000 | 3.00000 | 7.00000 | 6.00000 | scenario_3_b_b.j2 | 339f6d168b5df02964f55501786fc78bdd0460dcad2eaf1cfc7d24f3f5ca5e97 | 0 | 0.14938 | low |
| 0.00000 | 0.00000 | 0.00000 | 0.00000 | 2.00000 | 45.00000 | S6 | 2.00000 | 0.00000 | 0.00000 | 0.00000 | 8.00000 | 0.00000 | -1.00000 | 0.00000 | scenario_6_c.j2 | 497137828a7e4894a21fcb0a2ca19c647410f50cd8eec09905696391186176e2 | 0 | 0.19675 | medium |