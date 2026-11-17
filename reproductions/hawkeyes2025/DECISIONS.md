# Decisions

Written 2026-11-16 after reading the result tables only. **The full method decisions (network, attack policies, observation, action grouping, rewards, A2C settings of Table 1) are written after a full read and BEFORE any run.** The earlier rebuild in hawkeyes_faithful/ is checked against the paper and either reused with every difference listed, or replaced.

| # | gap | choice | why | decided on |
|---|---|---|---|---|
| 1 | Targets | Table 3 averages (6 attack policies). Table 4 (detection / decision / deployment times on their testbed) is NOT ATTEMPTED: it measures their hardware. Scenario 2 (Fig. 11, HMARL vs MARL) has no printed numbers. | - | 2026-11-16 |
| 2 | Seeds | 10 seeds, as the paper's 10 runs; verdict from our 95% CI | STANDARD.md requirement 5 | 2026-11-16 |

## Notes

- The paper's metric is called DSP in Table 3 and Defense Success Rate in Sec. 5.2 (Eq. 12).
