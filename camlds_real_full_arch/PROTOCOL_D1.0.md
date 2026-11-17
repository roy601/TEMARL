# Protocol D1.0: history-aware deception agents on verified CAM-LDS (simulation)

**Status: DRAFT, 2026-11-17. Not frozen.** No deception agent has been trained or evaluated under this
protocol. It is frozen only after the user approves the decisions in Section 10. After that, any change
means a new version (D1.1), never an edit of this one. The order of events is provable from git history.

Literature basis: `LITERATURE_NOTES.md` (each paper checked against its PDF).

## 1. Claim and questions

Claim under test, **in simulation only**: *deception agents that know the attacker's history keep
attackers engaged longer and protect assets better than agents without history, and than published
deception methods.*

- **Q1 (main):** does the history arm (frozen `allpos` Transformer embedding h) beat the NoHistory arm
  (h = 0, same network otherwise) on engagement and on protection?
- **Q2:** does the history arm beat the reference policies (Section 5) and the published comparators
  (Section 6)?
- **Q3 (secondary, descriptive):** GRU, LSTM and the old Transformer as the history encoder; IPPO vs MAPPO.

## 2. Data

- CAM-LDS v1 (DOI 10.5281/zenodo.18390561), verified: 34 recorded runs, 904 commands, 81 labels. Corpus
  and folds exactly as in encoder protocol 1.2 (frozen order; the 4 adjacent S6 swaps against execution
  rank are disclosed, not corrected).
- The attacker **replays** a recorded run. The defence can engage a command, end the episode early or
  redirect the attacker's zone through lures; it can never change or invent a command.
- **Reachability audit (done 2026-11-17, before any run):** under the scenario goal tactics, 8 of 34 runs
  contain no goal-tactic command at all (1_pwnkit_pam, 1_sudo_pam, 1_validaccount_pam, and all five S6
  runs). For these runs "protected" is always 1, whatever the agents do. See Section 4 and decision D3.
- **Resolved from sources (2026-11-17, `ZONE_GOAL_CHECK.md`):** S6's hand-typed goal (Exfiltration) is
  not in AttackBed's scenario 6; its stated goal is persistence. T1556 (the pam backdoor) is Persistence in
  ATT&CK but only Credential Access in our single-tactic vocabulary. With goal = Persistence for S6 and a
  goal mask from ATT&CK's full tactic membership, all 34 runs contain goal commands.

## 3. Environment (`env_cmd.py`, D1.0 settings)

- 4 defender agents (DMZ, LAN, User, Admin), 6 actions each (none + 5 D3FEND decoy types), capacity
  K = 2 (soft: over K, every decoy's efficacy is scaled by K / active), exposure rate beta = 0.2,
  attacker movement p_goal = 0.7, p_stay = 0.8, goal_steps = 1, set aggregation `max`.
- One command = one step = at most one unit of engagement reward.
- Engagement probability = capacity factor x PAYOFF[label, decoy]. PAYOFF is an audited **assumption**,
  not a measured probability (sensitivity in Section 8).
- Common random numbers: every uniform is drawn into the episode spec in advance, so all policies are
  compared on identical randomness (paired comparisons).
- Agents see only their own zone, two infrastructure signals, and the past-only history embedding h.

## 4. Outcomes (fixed now)

| # | outcome | definition | role |
|---|---|---|---|
| E1 | **engaged commands** | commands engaged per episode (code name `dwell`) | **primary, engagement** |
| P1 | **defense success probability (DSP)** | episodes in which the attacker never completes its goal / all episodes, as the ratio of Wang et al. 2020, Def. 9. The success criterion is adapted: Wang counts the attacker entering a decoy before the database; we count the goal command never succeeding un-engaged in the target zone. Goals as fixed in D3; any run still without a goal command is excluded from P1 and listed. | **primary, protection** |
| S1 | commands until goal | first-passage time to the goal (cf. Huang & Zhu 2019); censored at run length | secondary |
| S2 | engaged fraction | E1 / run length | secondary |
| S3 | exposure rate, distinct techniques engaged, lure chains, dead ends, capacity violations | as recorded by `episode_stats` | descriptive |

The names "dwell" and "depth" are never used in the write-up as attacker time or attacker depth: they are
counts of engaged commands and of distinct techniques on engaged commands.

## 5. Step 0: validity gate (run and reported BEFORE any learned agent)

Reference ladder, evaluated on the **validation** runs of every fold with the evaluation randomness of
Section 7:

| policy | what it does |
|---|---|
| none | no decoys |
| random | random action per agent, capacity respected |
| fixed (best static) | the single joint allocation with the best validation E1, kept all episode (Wang's / Anwar's static baseline) |
| greedy (reactive) | each step, decoys in the zones where the attacker is or was last seen, best payoff for the last command |
| transition planner | greedy using the empirical next-command distribution from the fold's training runs given the previous command (uses history, no learning) |
| clairvoyant ceiling | sees the next zone and the next command (upper bound only) |

**Pass criteria, all required, judged on validation only:**

- G1, protection is measurable: under "none", the goal is reached in at least 50% of goal-reachable
  validation episodes.
- G2, headroom: for E1 and for P1, clairvoyant minus best of {fixed, greedy} > 0, with a 95% bootstrap CI
  over runs that excludes 0.
- G3, history can matter: transition planner minus greedy > 0 on E1 or P1, with a CI that excludes 0. If
  G3 fails, Q1 is untestable in this environment: this is reported and the study stops before MARL.

If any gate fails, the environment is not tuned to pass. The failure is reported, and any fix becomes
protocol D1.1 with the fix stated.

## 6. Arms and comparators

- **Primary arms:** `allpos` (history) and NoHistory, both MAPPO (parameter-shared actor, centralised
  critic). They differ only in h.
- **Secondary arms:** `gru_allpos`, `lstm_allpos`, `baseline` (old Transformer); IPPO for allpos and
  NoHistory.
- **Published comparators**, entered only after their own replication in `reproductions/` (STANDARD.md):
  Hawkeyes 2025 (multi-agent A2C), Li 2025 (single-agent PPO), Wang 2020 (tabular Q-learning). Each is
  ported to this environment as a **declared adaptation** (their algorithm and published hyperparameters,
  our state, actions and reward). The write-up says "adapted", never "their system". A comparator whose
  replication fails is reported as not compared, with the reason.
- Encoders: the validated protocol 1.2 checkpoints (same fold, same seed), checked by SHA-256. Frozen
  during RL.

## 7. Training and selection

- MAPPO settings as in `mappo_cmd.HP` (lr 5e-4, 10 PPO epochs, clip 0.2, gamma 0.99, GAE 0.95, entropy
  0.01, 64 envs x 64 steps), 2,000,000 environment steps per cell. The reward is the engagement reward only;
  protection is **not** rewarded, so P1 measures a side effect (D6).
- Seeds 0-9. Validation randomness seed 100000+seed, test randomness seed 200000+seed, 20 evaluation
  repeats per run (simulation repeats, never treated as independent samples).
- Policy checkpoint chosen by validation E1 only. Nothing else is chosen on validation.
- Primary cells: 2 arms x 32 folds x 10 seeds = 640. Secondary cells run afterwards, on either GPU PC.
- Test outputs are written with their SHA-256 and are not scored until Section 9 runs.

## 8. Sensitivity analyses (declared now, all reported)

1. Efficacy: PAYOFF scaled by 0.5 and 0.75 (1.0 = primary). Ferguson-Walter et al. 2021 (52% of
   IP-addressed red-team commands went to decoys) is cited for the range, not as a calibration.
2. Set aggregation `mean` instead of `max` (separately trained, as `env_cmd.py` states).
3. Zones: S4 target DMZ (old rule) instead of LAN; goals from the old single-tactic mask (P1 then on the
   26 runs that contain goal commands).
4. Execution order instead of frozen order (S6 swaps corrected).
Sensitivity runs use allpos and NoHistory, MAPPO, seeds 0-4.

## 9. Evaluation (frozen with this protocol)

1. Dry run on validation outputs: the scorer must reproduce every validation number recorded at training.
2. Test opened **once**, after all primary cells exist.

- **Unit: the test run.** The 29 known-variant folds each test one run, which gives 29 paired units. Per
  unit: the outcome averaged over 20 repeats, then over 10 seeds. The 3 unseen-scenario folds are reported
  separately and descriptively (n = 3 is too small to test).
- **Family 1 (Q1):** allpos vs NoHistory on E1 and P1 (2 comparisons).
  **Family 2 (Q2):** allpos vs each reference policy and each comparator that passed replication, on E1
  and P1.
- Per comparison: mean paired difference, 95% bootstrap CI (10,000 resamples of runs, seed 20261103),
  two-sided Wilcoxon signed-rank (scipy 1.17.1, zero differences dropped), Holm within each family.
  "X outperforms Y" only if Holm p < 0.05 and the CI excludes 0; otherwise "no difference shown".
- The number of runs used is reported with every P1 result.
- Every result is reported whatever its direction. Q3 is descriptive.

## 10. Decisions for the user (recommended choice first)

| # | decision | recommendation | why |
|---|---|---|---|
| D1 | zones | **checked 2026-11-17 (`ZONE_GOAL_CHECK.md`):** hand-typed entry/target zones, which agree with AttackBed's scenario descriptions for 6 of 7 scenarios; S4 target = LAN (where the attack ends), DMZ as sensitivity. `derived_zones.json` is not used: its host order is where logs first show activity (DNS server and firewall see all traffic), not where the attacker is | source-verified; the earlier "data-derived" recommendation was wrong |
| D2 | movement | not yet checked: p_goal / p_stay come from the old environment's calibration | to be checked against per-command hosts (needs a verified `manifestations_filtered.zip`) |
| D3 | goals | **checked 2026-11-17:** S6 goal = Persistence (AttackBed `client.md`); goal mask from ATT&CK's full tactic membership (pinned release). All 34 runs then contain goal commands; no run is dropped | replaces "drop 8 runs", which would have removed all of S6 |
| D4 | command order | frozen order, reuse protocol 1.2 checkpoints; execution order as sensitivity | validated checkpoints exist only for this order |
| D5 | size | 640 primary cells first (about 1.5 days on GPU PC 1), the rest afterwards | the main question first |
| D6 | reward | engagement only; P1 as a measured side effect | a fair test of "protects better" without training for it; a combined reward would be a new arm, declared before any run |
| D7 | comparators | Hawkeyes, Li, Wang 2020, only after their replication | STANDARD.md |

## 11. Reproducibility

- `spec` file with SHA-256 of every input (corpus, folds, checkpoints, PAYOFF, env and learner code);
  every stage refuses to run if one changes.
- Two of the 640 cells rerun on GPU PC 2; results must be identical (CPU evaluation) or within a declared
  tolerance stated before the rerun.
- Code, configuration, per-cell results and sealed test outputs are committed; checkpoints stay on the
  GPU PCs.

## 12. Known limits (stated in any write-up)

- Simulation: the attacker's commands are replayed and react to the defence only through the movement
  model. Real attackers react (Dowling et al. 2018; Ferguson-Walter et al. 2021). No result is a claim
  about real attackers.
- PAYOFF, capacity, exposure and movement are assumptions; the sensitivity analyses bound them.
- 34 runs from 7 base scenarios on one testbed; scenario 1 has 18 variants.
- The prediction results (protocol 1.2) did not show the encoders beating the best simple rule overall;
  the history arm may therefore have little extra information to use. G3 tests this first.
