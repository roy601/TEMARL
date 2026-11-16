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

## Notes from reading

- In Table 3 the best agents are heuristics (Team UC -113 +- 35); the only MARL agent scores -193 +- 84. A MARL claim must be measured against -113.
- The AI Magazine and AAAI versions report the same competition; the AI Magazine version is the journal record and is used for targets.
