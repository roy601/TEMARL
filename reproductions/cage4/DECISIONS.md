# Decisions

Written 2026-11-16, after reading the three papers, before downloading the environment or running anything.

| # | gap | choice | why | decided on |
|---|---|---|---|---|
| 1 | Purpose | Two separate uses. (a) **Reproduction:** rerun the published agents in the unchanged environment and compare with Table 3. (b) **Idea 03:** train TEMARL's agents in CAGE 4 and compare with the same Table 3 entries, under the same evaluation (100 episodes x 500 steps). (b) starts only after (a) is reported. | STANDARD.md requirement 10 | 2026-11-16 |
| 2 | Environment version | commit 8c3c50c of cage-challenge-4, unchanged | a fixed version | 2026-11-16 |
| 3 | Agents | Reproduction is attempted only for agents whose code the teams released. Agents without code are NOT ATTEMPTED, with the reason. | no rebuild of a competitor's agent is called a reproduction | 2026-11-16 |
| 4 | Scenario variations | The five variations (constant network size, improved decoy detection, increased phishing, stealthy red, aggressive red) are run only if the repository provides them; otherwise NOT ATTEMPTED. Their exact settings are not given in the paper. | not stated in the paper | 2026-11-16 |
| 5 | Our metrics inside CAGE 4 | Reported beside the CAGE 4 score, never instead of it: decoy events triggered by red (trapping), red actions spent on decoy hosts (engagement proxy), hosts reached with root (protection). Defined from the environment's own logs, before any run. | CAGE 4 scores a joint penalty, not dwell or depth | 2026-11-16 |
| 6 | Which agents (after the availability check, before any run) | Reproduce Team cybermonic only (6 targets). Teams UC, lancer and punch: NOT ATTEMPTED (no code); their Table 3 numbers stay as published reference values for the Idea 03 comparison. | decision 3 | 2026-11-16 |

## Decisions of 2026-11-24 (after inspecting the released code, before any run)

Both repositories were cloned at their pinned commits and read. A 100-step smoke test checked that the
stack runs (it is not a result: no episode finished and nothing was kept).

| # | gap | choice | why | decided on |
|---|---|---|---|---|
| 7 | Released artifacts | Submission `cybermonic/cage-4-submission` at 2afd652 (code last changed 2024-06-14; the 2025-11-18 commit edits the README only), unchanged: `submission.py`, `models/`, `wrapper/` and the five released weight files `weights/gnn_ppo-0..4.pt` (one per blue agent). SHA-256 of the weights and code: below. | the authors' own trained agents: a reproduction in the ACM sense | 2026-11-24 |
| 8 | Software | Python 3.11 (the submission's README), installed per user with `uv`. The environment's `Requirements.txt` at 8c3c50c, with three changes: **Ray 2.10.0** instead of the submission's 2.12.0 (2.12.0 has no Windows build, 2.11.0 has none either; Ray is used only as the `MultiAgentEnv` base class of the wrappers); **torch_geometric 2.3.1** (the submission's pin; the environment's last commit pins 2.5.0); `joblib 1.2.0` and `tqdm 4.65.0` (the submission's pins). Every unpinned package is resolved **as of 2024-06-15** (`uv --exclude-newer`), the day after the submission's last code change (a 2026 pyarrow otherwise needs NumPy 2). The installed versions are written to `out/ENVIRONMENT.json`. | the closest installable copy of the 2024 software; each change stated | 2026-11-24 |
| 9 | Evaluation loop | The official CAGE 4 evaluation: the per-episode loop of `CybORG/Evaluation/evaluation.py` (`run_evaluation`), identical to the submission's own `evaluation.py`. One CybORG object per seed is wrapped once and reset for each of 100 episodes of 500 steps; the episode score is the sum over steps of the mean of the agents' rewards; the loop stops before adding the step at which every agent is done. `run.py` repeats this loop line for line to record each episode's score; its `verify` stage runs the official function on the same seed and must print the same mean. | the score of Table 3 | 2026-11-24 |
| 10 | Seeds and variance | The official evaluation used `seed=None`, so its episodes cannot be replayed. We run **10 evaluation seeds (0-9), 100 episodes each**: CybORG seed s, and Python `random`, NumPy and torch seeded with s before the first episode (the agents sample their actions). The released weights are **one** trained policy, so the variance covers evaluation randomness only. Retraining (`train.py`, new weights, training seeds) is NOT ATTEMPTED in this stage. | STANDARD.md requirement 5, as far as released weights allow | 2026-11-24 |
| 11 | Verdict | As written in `TARGETS.csv`: MATCH if the published mean is inside our 95% CI of the mean; CLOSE if inside our mean ± the published std. Our mean = mean of the 1,000 episodes. **Our 95% CI = t-interval over the 10 seed means** (each a 100-episode mean, as one Table 3 entry is); the episode-level interval is reported too. Each seed's 100-episode mean and std is reported beside Table 3's −193 ± 84. | the seed-level interval is the honest one: one Table 3 number is one 100-episode run | 2026-11-24 |
| 12 | Variations | **NOT ATTEMPTED** (decision 4). The environment at 8c3c50c has no named configuration for any of the five; it has knobs (the green agent's `phishing_error_rate`, the red agent's choice between stealthy and aggressive service discovery, the `DiscoverDeception` action, the scenario generator's sizes), but the paper does not give their values. The organisers are asked (`AUTHOR_CONTACT.md`). | not provided | 2026-11-24 |
| 13 | Decision 5's metrics | Deferred to the Idea 03 stage: the reproduction reports the CAGE 4 score only. | the reproduction is about Table 3; our metrics belong to the comparison | 2026-11-24 |
| 14 | Machine | CPU only, one process per seed (torch threads 1). Any machine with the environment of decision 8; the first run is on the development PC (12 cores), because GPU PC 2 is busy with CL-D1.0. | the agents are small graph networks | 2026-11-24 |
| 15 | **Correction of decision 6: Team punch released code** | Decision 6 missed it. A teammate's kit (`reproduction_dump/`, commit 79ff1e72, 2026-11-23) points to `PUNCH-Cyber/cage-4-submissions` (released 2025-02-07). Its README gives **Analyse Restore v1** a final score of **-142.72, 3rd place**, which is Table 3's Team punch (-142 ± 44). So Team punch is reproduced too: `punch_analyse_restore_v1` at commit 9cc4ff8, unchanged, under decisions 8-11 (same software, loop, seeds and verdict rule). It is a fixed analyse-and-restore heuristic: no weights, no randomness of its own. Its five variations stay NOT ATTEMPTED (decision 12). Teams UC and lancer: still no code found, NOT ATTEMPTED. | released code found before any run | 2026-11-24 |

### SHA-256 of the released files (decision 7)

Raw bytes of the files as stored in the repositories (cloned with `core.autocrlf=false`; text files have LF line
endings, the weight files are binary).

| file | SHA-256 |
|---|---|
| weights/gnn_ppo-0.pt | 991d96cb5132eec36595f6d407e67b93b2e5045c960dc4d25586e0c0bf124e60 |
| weights/gnn_ppo-1.pt | 27072ef12bab1e1b2ec9b9143845d07af7545c615c92ef44c59b67268cb98502 |
| weights/gnn_ppo-2.pt | a76ea99d830976aa4c7f370c1fc575746de7c8a1618dd239ff34f0525da11478 |
| weights/gnn_ppo-3.pt | acca6460545401e47c1dfe30d9f761f4955437b9c13f8098d5856e7995163fe4 |
| weights/gnn_ppo-4.pt | ea9c664085987f4c191b74f2d4ffa44453461990d0c8cc1c1525ec4d8f7372d2 |
| submission.py | e4ded7b8d60093892f5abb3544a4b48bcc19042a993a6c297722578302709570 |
| models/cage4.py | 922949d38d856c5a995976ddb889fc0e88eadef0dac1cedb5d941c2825df4751 |
| wrapper/graph_wrapper.py | 1ec7529a6cf1dad63f25e625d4444287821128dbdf072a51ff7c48290d82062f |
| (environment) CybORG/Evaluation/evaluation.py | 8c01f269c25a6f8e61916524321aca2ecf5c1b572f6568cc71eb18f89a7ce28d |
| (punch, decision 15) punch_analyse_restore_v1/submission.py | 06d0ec52e8e2e36efe0f433da395697eb43e36a79909267d2673f5bb59fd8c56 |
| (punch) punch_analyse_restore_v1/punchagents.py | 9b170f8950498c622b1037be753ff52c461a47f0a25835115ebcaf1f49e0754e |
| (punch) punch_analyse_restore_v1/punchwrappers.py | 9caf35eabd35fe1803c0f7ae8c59ee905aa8381dcdfe2c0e9d51713f1325a209 |

## Notes from reading

- In Table 3 the best agents are heuristics (Team UC -113 +- 35); the only MARL agent scores -193 +- 84. A MARL claim must be measured against -113.
- The AI Magazine and AAAI versions report the same competition; the AI Magazine version is the journal record and is used for targets.
- The submission's README gives its final leaderboard score as -193.68, which Table 3 rounds to -193.
