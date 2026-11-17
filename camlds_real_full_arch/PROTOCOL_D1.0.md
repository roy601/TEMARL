# Protocol D1.0: history-aware deception agents on verified CAM-LDS (simulation)

**Status: FROZEN, 2026-11-17** (`SPEC_D1.json`, written by `spec_d1.py --freeze` after the user's
approval). At the freeze no main-study agent had been trained or evaluated under this protocol (the
pilot of Section 7a used validation data only). Any change now means a new version (D1.1), never an
edit of this one. The order of events is provable from git history. Decisions D1-D8 were settled by the
user on 2026-11-17 (Section 10); the freeze followed the GPU diagnostics of Section 7 the same day.

Literature basis: `LITERATURE_NOTES.md` (each paper checked against its PDF).

## 1. Claim and questions

Claim under test, **in simulation only**: *deception agents that know the attacker's history keep
attackers engaged longer and protect assets better than agents without history, and than published
deception methods.* D1.0 tests the first two parts. The part "than published deception methods" needs
the replications of decision D7 and is tested only in protocol D1.1; until then no write-up claims it.

- **Q1 (main, Family 1):** does the history arm (frozen `allpos` Transformer embedding h) beat the
  NoHistory arm (h = 0, same network otherwise) on engagement and on protection?
- **Q2 (Family 2):** does the history arm beat the reference policies (Sections 5 and 6, including the
  static honeypot)? The published comparators are a later family (D1.1).
- **Q3 (Family 3):** does the Transformer history beat an LSTM history (`lstm_allpos`, the proposal's
  "MARL without the Transformer")?
- **Q4 (descriptive, D8):** GRU and the old Transformer as the history encoder; IPPO vs MAPPO; allpos vs
  NoHistory under IPPO. Scored at the same single test opening; described, never tested.

## 2. Data

- CAM-LDS v1 (DOI 10.5281/zenodo.18390561), verified: 34 recorded runs, 904 commands, 81 labels. Corpus
  and folds exactly as in encoder protocol 1.2 (frozen order; the 4 adjacent S6 swaps against execution
  rank are disclosed, not corrected). **Measured 2026-11-17 (`checks/ORDER_CHECK.txt`, decision D4):**
  the two orders differ in 4 of 34 runs, all S6, each at its last two commands, where the goal command
  and the command before it are swapped: 8 of 904 positions, 4 of 870 encoder inputs (history windows),
  8 of 870 next-command targets; no recorded zone differs.
- The attacker **replays** a recorded run. The defence can engage a command, end the episode early or
  redirect the attacker's zone through lures; it can never change or invent a command.
- **Reachability audit (done 2026-11-17, before any run):** under the scenario goal tactics, 8 of 34 runs
  contain no goal-tactic command at all (1_pwnkit_pam, 1_sudo_pam, 1_validaccount_pam, and all five S6
  runs). For these runs "protected" is always 1, whatever the agents do. See Section 4 and decision D3.
- **Resolved from sources (2026-11-17, `ZONE_GOAL_CHECK.md`):** S6's hand-typed goal (Exfiltration) is
  not in AttackBed's scenario 6; its stated goal is persistence. T1556 (the pam backdoor) is Persistence in
  ATT&CK but only Credential Access in our single-tactic vocabulary. With goal = Persistence for S6 and
  goal commands read from each command's own released tactic labels (`tactics_raw`, the dataset authors'
  AttackMate metadata, which label T1556.003 credential-access, defense-evasion and persistence), every
  run contains goal commands, and every run counted in P1 has one in its target zone (`d1_data.py`,
  `test_d1.py`). No external ATT&CK file is needed.

## 2a. Earlier exposure of the test runs (disclosed before the freeze)

On 2026-11-15, before this protocol existed, a partial run of the earlier `pipeline.py --stage main` on
GPU PC 1 (old environment: random-walk movement, hand-typed goals, execution order, engagement reward)
produced 1,171 of 3,200 planned deception cells, committed as `b6487fee` in `results/main/`. That runner
wrote test-run outcomes **unsealed** (`test_summary` in each `result.json`; per-cell and summary tables
in `RESULTS.md`) on the same test runs that D1.0 uses, and recomputed the CAM-LDS encoder prediction test
for 469 encoder cells (`prediction.json`; the same checkpoints and validation-selected thresholds as
protocol 1.2, so a recomputation, not a new choice). The files reached the shared repository on
2026-11-17, before the freeze.

- **Not seen:** the user states that nobody looked at these test numbers (2026-11-17); the analyst
  read only the section headings of `RESULTS.md`.
- **Not used:** no D1.0 decision used them. D1-D3 come from source checks, D4 from the order check,
  D6 from the validation-only pilot, and D5, D7 and D8 from cost and design.
- They are not D1.0 results and are never reported as such (`results/main/README_NOT_D1.md`). Their
  environment differs from D1.0's primary setting; the closest D1.0 setting is the `random_walk`
  sensitivity analysis, and this disclosure is repeated with its result.

## 3. Environment (`env_cmd.py`, D1.0 settings)

- 4 defender agents (DMZ, LAN, User, Admin), 6 actions each (none + 5 D3FEND decoy types), capacity
  K = 2 (soft: over K, every decoy's efficacy is scaled by K / active), exposure rate beta = 0.2,
  goal_steps = 1, set aggregation `max`.
- **Attacker position (changed after the D2 check):** each command executes in its **recorded zone**
  (`checks/movement_check.py`). A lure engagement sends the next command to the partner zone, after which
  the replay continues on its recorded path. Commands executing on the attacker machine (Internet) or the
  firewall cannot be engaged; they are counted and reported. The old random-walk model (p_goal 0.7,
  p_stay 0.8) is a sensitivity analysis only.
- One command = one step = at most one engaged command (E1 counts commands, not labels). The reward is
  set in Section 7 (D6); it changes what the agents are trained for, never the environment's dynamics
  (tested: every outcome of a non-learning policy is identical under both rewards).
- Engagement probability = capacity factor x PAYOFF[label, decoy]. PAYOFF is an audited **assumption**,
  not a measured probability (sensitivity in Section 8).
- Common random numbers: every uniform is drawn into the episode spec in advance, so all policies are
  compared on identical randomness (paired comparisons).
- Agents see only their own zone, two infrastructure signals, and the past-only history embedding h.
- **Observation assumption (stated after the audit, 2026-11-17):** h is built from every past command
  of the run, including the 132 commands (14.6%) executed on the attacker's own machine and the 12
  (1.3%) on the firewall. A real defender sees those only through their effects (traffic, logs), so h
  assumes complete technique-level observation of the attacker's past commands: an upper bound on what
  a history-aware defender can know. The local observation is limited to the agent's own zone.

## 4. Outcomes (fixed now)

| # | outcome | definition | role |
|---|---|---|---|
| E1 | **engaged commands** | commands engaged per episode (code name `dwell`) | **primary, engagement** |
| P1 | **defense success probability (DSP)** | episodes in which the attacker never completes its goal / all episodes, as the ratio of Wang et al. 2020, Def. 9. The success criterion is adapted: Wang counts the attacker entering a decoy before the database; we count the goal command never succeeding un-engaged in the target zone. Goals as fixed in D3. S4 is excluded from P1 (its goal commands execute on the firewall, which no agent defends), so P1 uses 33 runs; this is stated with every P1 result. | **primary, protection** |
| S1 | commands until goal | first-passage time to the goal (cf. Huang & Zhu 2019); censored at run length | secondary |
| S2 | engaged fraction | E1 / run length | secondary |
| S3 | exposure rate, distinct techniques engaged, lure chains, dead ends, capacity violations; **team activity**: share of steps with >= 2 decoys out, each agent's share of steps with a decoy out, engagements in each agent's zone | as recorded by `episode_stats`; team activity reported for every arm by `evaluate_d1.py` | descriptive. Under the proposal reward (D6) distinct techniques and exposure are partly rewarded, so they are never claimed as a win |

The names "dwell" and "depth" are never used in the write-up as attacker time or attacker depth: they are
counts of engaged commands and of distinct techniques on engaged commands.

## 5. Step 0: validity gate (run and reported BEFORE any learned agent; `gate_d1.py`)

**Data and randomness.** All 34 runs, seed 300000, 20 repeats per run. This randomness is disjoint from
validation (100000+s) and test (200000+s). *Why not validation only (the first draft):* the validation sets
of the 32 folds contain only 7 distinct runs from 4 of the 7 scenarios (20 of 32 folds use the same run),
too few for a confidence interval to decide anything. The gate involves no learned agent, and the two
fitted rules are fitted **leaving the scored run out**. *Disclosure:* the gate therefore shows how the
fixed reference policies behave on the runs that later serve as test runs (with other randomness). Nothing
is chosen or tuned after the gate, and the protocol is frozen before the gate is run.

| policy | what it does |
|---|---|
| none | no decoys |
| random | uniform random joint action (capacity applies as for every policy) |
| fixed | the best constant joint action over all 6^4, chosen per outcome (E1, P1) on all other runs (Wang's / Anwar's static baseline) |
| greedy | the payoff-best decoy for the last command, in the zone where the attacker was last seen (frozen `ReactivePolicy`) |
| planner | as greedy, but for the next command predicted from the previous one (empirical transitions of all other runs): uses history, no learning |
| clairvoyant | sees the next zone and the next command (frozen `ClairvoyantCoordPolicy`; ceiling only, never an arm) |

**Unit:** the run (E1: 34 runs; P1: the 33 runs with p1). Bootstrap: 10,000 resamples of runs, seed
20261103, percentile 95% interval.

**Pass criteria, all required:**

- G1, protection is measurable: under "none", the goal is reached in at least 50% of P1 episodes.
- G2, headroom: for E1 and for P1, clairvoyant minus the better of {fixed, greedy} > 0, with a CI that
  excludes 0.
- G3, history can matter: planner minus greedy > 0 on E1 or on P1, with a CI that excludes 0. If G3
  fails, Q1 is untestable in this environment: this is reported and the study stops before MARL.

If any gate fails, the environment is not tuned to pass. The failure is reported, and any fix becomes
protocol D1.1 with the fix stated.

## 6. Arms and comparators

- **Primary arms:** `allpos` (history) and NoHistory, both MAPPO (parameter-shared actor, centralised
  critic). They differ only in h.
- **Tested secondary arm (D7, Family 3):** `lstm_allpos`, MAPPO: the proposal's "MARL without the
  Transformer", with the protocol 1.2 LSTM checkpoints (capacity-matched: 77,793 trainable parameters
  against the Transformer's 77,713). Everything else as the primary arms.
- **Descriptive arms (Q4, D8):** `gru_allpos` (77,920 parameters) and `baseline` (old Transformer,
  77,713), both MAPPO with their protocol 1.2 checkpoints; IPPO (independent critics, de Witt et al.
  2020) for allpos and NoHistory. They run in the main run, before the single test opening.
- **Reference policies at evaluation:** none, random, fixed, greedy and planner (Section 5), and the
  **static honeypot** (the proposal's Baseline 1; frozen `StaticPolicy`): one decoy type in every zone at
  every step, the type chosen per outcome on the fold's training runs. With 4 active decoys it exceeds
  capacity K = 2, so each decoy's efficacy is halved. Fixed (the best of all 1,296 constant allocations,
  which include every static choice) is therefore the strongest static comparator; static is reported
  because the proposal names it.
- **Published comparators (D7: protocol D1.1 only)**, entered only after their own replication in
  `reproductions/` (STANDARD.md):
  Hawkeyes 2025 (multi-agent A2C), Li 2025 (single-agent PPO), Wang 2020 (tabular Q-learning). Each is
  ported to this environment as a **declared adaptation** (their algorithm and published hyperparameters,
  our state, actions and reward). The write-up says "adapted", never "their system". A comparator whose
  replication fails is reported as not compared, with the reason.
- Encoders: the validated protocol 1.2 checkpoints (same fold, same seed), checked by SHA-256. Frozen
  during RL.

## 7. Training and selection

- MAPPO settings as in `mappo_cmd.HP` (lr 5e-4, 10 PPO epochs, clip 0.2, gamma 0.99, GAE 0.95, entropy
  0.01, 64 envs x 64 steps), 2,000,000 environment steps per cell.
- **Reward (D6, chosen by pilot rule R2, Section 7a): the proposal reward** (thesis proposal, Section 2.3):
  +1 per engaged command, +1 when the engaged command carries a technique not engaged before in the
  episode, -5 when the deception is exposed (our closest event to the proposal's "attacker
  disconnection"). The values +1 and -5 are our choice, not taken from a paper; the engagement-only
  reward is a sensitivity analysis (Section 8). Protection is **not** rewarded, so P1 still measures a
  side effect.
- Seeds 0-9. Validation randomness seed 100000+seed, test randomness seed 200000+seed, 20 evaluation
  repeats per run (simulation repeats, never treated as independent samples).
- Policy checkpoint chosen by validation E1 only. Nothing else is chosen on validation.
- Primary cells: 2 arms x 32 folds x 10 seeds = 640, all run in full: no reduction of seeds or steps,
  whatever the run time (D5). They run first; then the 320 `lstm_allpos` cells (Family 3); then the
  1,280 descriptive cells (Q4, D8: `gru_allpos` and `baseline` with MAPPO, allpos and NoHistory with
  IPPO). The test is opened only once, after all 2,240 main cells exist (`run_d1.PHASES`).
- Time: measured in the pilot on a CPU, median 35 s per 200,000 steps (max 39 s), so about 6 min per
  2,000,000-step cell: about 62 h for the 640 primary cells, 93 h with Family 3 (960 cells) and 218 h
  for all 2,240 main cells (69 h, 104 h and 243 h at the pilot's maximum), test episodes not included,
  linear scaling assumed. IPPO, GRU and old-Transformer cells were not timed in the pilot. GPU time is
  measured with `run_d1.py --timing` before the main run and reported.
- Every cell's validation learning curve is reported (supplement), so convergence at 2,000,000 steps
  can be checked. All arms use the same MAPPO settings; none is tuned separately.
- Test outputs are written with their SHA-256 and are not scored until Section 9 runs.
- **Restarting:** the run is resumable cell by cell. `MANIFEST.json` stores what decides a cell's content
  (spec, settings, hyperparameters, steps, repeats, seeds, folds) and a log of every invocation; a start
  whose content-defining settings differ is refused. Machine, threads, output path and the choice of arms,
  folds or seeds may differ between starts. After a killed run, delete `RUNNING.lock` and start again.
- **Procedure on the GPU PC (`run_all_d1.py`), one command per stage:** `diagnostics` (before the
  freeze: preflight, timing), `main` (gate, preflight, timing, the 2,240 cells, validation dry run),
  `sensitivity` (Section 8: preflight, cells and dry run per setting) and `open` (opens, once, each test
  whose dry run passed). Each stage logs to `results_d1/logs/`, stops at the first failure (a failed
  gate or dry run included) and can be restarted; only `open` opens a test.
- **Diagnostics before the freeze (allowed):** `--preflight` and `--timing` use no test data and print no
  gate number, so they may be run on the GPU PC before the freeze to find a missing or non-reproducing
  checkpoint, or a dry-run mismatch on the GPU, while a fix is still possible. They are repeated after it.
  **Done 2026-11-17 on GPU PC 1** (`run_all_d1.py diagnostics`): preflight PASS, 1,280 of 1,280
  checkpoints reproduce their validation BCE; one allpos MAPPO cell took 93 s on the GPU (about 58 h for
  the 2,240 main cells, test episodes not included); the dry-run reproduction on the GPU passed
  (recorded 13.85, re-evaluated 13.85).
- **Before the main run, on the GPU PC, after the freeze:** `run_d1.py --preflight` loads every
  protocol 1.2 checkpoint the main run needs (1,280: allpos, lstm_allpos, gru_allpos and baseline x 32
  folds x 10 seeds) and checks that each reproduces its recorded validation BCE; the main run refuses to
  start unless a passing preflight under the frozen spec covers every checkpoint it needs. Then
  `run_d1.py --timing` trains one cell and repeats its dry-run check on that device; if the
  re-evaluation does not reproduce the recorded validation E1 exactly, the main run is not started
  (the dry run would fail) and this is reported.
- Runner: `run_d1.py` (command order always frozen; environment `EnvConfig(reward="proposal")`; a
  sensitivity analysis changes only the entries it names). Encoders are the
  protocol 1.2 checkpoints, loaded unchanged and accepted only if they reproduce their recorded
  validation BCE; the CAM-LDS **prediction** test is never scored again. Each cell writes its test
  episodes to `sealed_test.json` and only that file's SHA-256 into `result.json`; the runner's summary
  contains validation numbers only. `pipeline.py --stage main` is **not** the D1.0 runner (it rescored
  the prediction test and printed test summaries).

## 7a. Pilot before the freeze (`pilot_d1.py`; declared 2026-11-17 before it ran)

Requested by the user: a small trial-and-error check on part of the data, to see the chain work.
**Validation only; no test episode is built** (asserted). Folds 1_cron_sshkey, 3_vnc_puppet,
6_macro_cron (validation runs from S1, S3, S6); seeds 101-103 (disjoint from 0-9); MAPPO; 200,000
environment steps; 10 repeats; arms allpos, NoHistory, lstm_allpos (encoders trained in the pilot with the
protocol 1.2 budget, selected on validation); rewards **engagement** (D6) and **proposal** (thesis
proposal, Section 2.3: +1 per engaged command, +1 bonus when it engages a technique not engaged before in
the episode, -5 when the deception is exposed, our closest event to the proposal's "attacker
disconnection"; the bonus and penalty values are our choice). Reference policies on the same validation
episodes, including **static** (best single decoy type everywhere: the proposal's Baseline 1).

Rules, fixed before the pilot ran:
- R1 works: in every pilot fold, each learned arm with the engagement reward beats none and random on
  mean validation E1. If not, stop and investigate before the freeze.
- R2 reward: the main study uses the proposal reward only if, over all pilot cells, its mean validation
  E1 is at least 95% of the engagement reward's and its mean validation depth or P1 is higher; otherwise
  the engagement reward (D6) stays.
- R3: history differences (allpos vs NoHistory, allpos vs lstm_allpos) are reported and decide nothing.
All pilot numbers are reported in the paper as a pilot.

**Outcome (ran 2026-11-17 on a CPU; `results_d1/pilot/PILOT_RESULTS.md`, pinned):** R1 passed in all
three folds. R2: proposal reward against engagement reward, means over all pilot cells: E1 13.01 vs
12.94 (100.5%), distinct techniques 9.69 vs 9.07, P1 0.396 vs 0.378, so the rule selects the **proposal
reward** (D6). These margins are small and within seed noise: the choice follows the declared rule and
is not evidence that the proposal reward is better. Pilot policies were selected on the same validation
runs they were scored on, so pilot numbers are optimistic. Pilot encoders and policies are not used in
the main study.

## 7b. Audit before the freeze (2026-11-17; `checks/audit_d1.py`, output `checks/AUDIT_D1.txt`)

Validation runs only. Findings: learning works (all 54 pilot cells improved, mean validation E1 4.6 to
13.0); the history reaches the agents (zeroing h changes 7-57% of a trained history agent's decisions,
0% for NoHistory, as it must); the cell path with sealed test output, the dry-run reproduction (MAPPO
and IPPO, difference 0) and the execution-order encoder retraining run correctly. Two design limits
were found and are stated in Sections 3 and 12: the observation assumption behind h, and the small
coordination demand of the recorded runs. A 200,000-step single-seed cell in which the history agent
did worse than NoHistory (fold 3_vnc_puppet: 6.6 vs 14.0) is seed variance, not a fault.

## 8. Sensitivity analyses (declared now, all reported)

1. Efficacy: PAYOFF scaled by 0.5 and 0.75 (1.0 = primary). Ferguson-Walter et al. 2021 (52% of
   IP-addressed red-team commands went to decoys) is cited for the range, not as a calibration.
2. Set aggregation `mean` instead of `max` (separately trained, as `env_cmd.py` states).
3. Movement: the old random-walk model (p_goal 0.7, p_stay 0.8) instead of the recorded zones; goals from
   the old single-tactic mask (P1 then on the runs that still contain goal commands).
4. Execution order instead of frozen order (S6 swaps corrected; 8 of 904 positions differ, Section 2).
5. Reward: the engagement-only reward (+1 per engaged command; no technique bonus, no exposure
   penalty) instead of the proposal reward (D6). This bounds the effect of our choice of +1 and -5.
Each setting changes only what it names; everything else, the proposal reward included, is the primary
setting. Sensitivity runs use allpos and NoHistory, MAPPO, seeds 0-4, all 32 folds (6 settings x 320 =
1,920 cells; `run_d1.py --sensitivity efficacy_0.5 | efficacy_0.75 | mean | random_walk | execution |
reward_engagement`). In
`random_walk`, P1 counts only runs that contain a goal command under the old goals (26 runs). In
`execution`, the encoders are retrained in the cell with the protocol 1.2 budget (9,152 updates for
Transformers, 18,304 for GRU and LSTM) and patience (16 checks), selected on validation. Each setting has
its own dry run and its own single test opening (`evaluate_d1.py --sensitivity NAME`), Family 1 only,
with the same statistics; sensitivity results are reported as such and never replace the primary result.

## 9. Evaluation (frozen with this protocol)

1. Dry run on validation outputs: the scorer must reproduce every validation number recorded at training.
2. Test opened **once**, after all 2,240 main cells exist (the three tested families and Q4 are scored
   at that one opening; nothing is scored later).

- **Unit: the test run.** The 29 known-variant folds each test one run, which gives 29 paired units. Per
  unit: the outcome averaged over 20 repeats, then over 10 seeds. The 3 unseen-scenario folds are reported
  separately and descriptively (n = 3 is too small to test).
- **Family 1 (Q1):** allpos vs NoHistory on E1 and P1 (2 comparisons).
  **Family 2 (Q2):** allpos vs none, random, static, fixed, greedy and planner on E1 and P1
  (12 comparisons). The reference policies are run at evaluation time on the same test episodes as the
  arms (same runs, seed 200000+seed, 20 repeats, same setting); static and fixed (each per outcome) and
  planner are fitted on the fold's training runs only (static and fixed: seed 400000, 5 repeats).
  Clairvoyant is reported as the ceiling, not tested.
  **Family 3 (Q3):** allpos vs lstm_allpos on E1 and P1 (2 comparisons).
  Published comparators that pass replication are added as a separate family in protocol D1.1 (D7).
- Scorer: `evaluate_d1.py` (`--validation-dry-run`, then `--open-test`). The open refuses unless the spec
  passes, all 2,240 main cells exist, the dry run passed and `TEST_OPENED.json` is absent; every sealed
  file's SHA-256 is checked before it is read, and every cell must have the expected arm and learner and
  have used the protocol's test seed, 20 repeats, setting and order.
- Per comparison: mean paired difference, 95% bootstrap CI (10,000 resamples of runs, seed 20261103),
  two-sided Wilcoxon signed-rank (scipy 1.17.1, zero differences dropped), Holm within each family. The
  three families answer different questions and are not corrected across families; this is stated with
  the results.
  "X outperforms Y" only if Holm p < 0.05 and the CI excludes 0; otherwise "no difference shown".
- The number of runs used is reported with every P1 result.
- Every result is reported whatever its direction.
- **Q4 is descriptive (D8):** GRU vs allpos, old Transformer vs allpos, IPPO vs MAPPO (for allpos and
  for NoHistory) and allpos vs NoHistory under IPPO, on E1 and P1: the mean paired difference and its
  95% bootstrap CI over the same units. No p-value, no correction, no verdict, no claim.

## 10. Decisions for the user (recommended choice first)

| # | decision | recommendation | why |
|---|---|---|---|
| D1 | zones | **checked 2026-11-17 (`ZONE_GOAL_CHECK.md`):** hand-typed entry/target zones, which agree with AttackBed's scenario descriptions; with recorded positions (D2) two targets follow from where the goal commands execute: S5 = LAN (credential theft on the LAN Turtle), S4 = firewall (not defended, so S4 is excluded from P1). `derived_zones.json` is not used: its host order is where logs first show activity (DNS server and firewall see all traffic), not where the attacker is | source-verified; the earlier "data-derived" recommendation was wrong |
| D2 | movement | **checked 2026-11-17 (`checks/MOVEMENT_CHECK.txt`):** recorded zone per command primary; random walk as sensitivity | the model makes 9.3 zone changes per run against 1.5 recorded, stays in the target 0.78 against 0.97, and cannot place the 16% of commands that run on the attacker machine or the firewall. Source: AttackMate records from the md5-verified scenario archives |
| D3 | goals | **checked 2026-11-17:** S6 goal = Persistence (AttackBed `client.md`); goal commands from the dataset's own per-command tactic labels (`tactics_raw`). All 34 runs then contain goal commands; no run is dropped | replaces "drop 8 runs", which would have removed all of S6 |
| D4 | command order | **decided 2026-11-17:** frozen order primary, reusing the protocol 1.2 checkpoints; execution order as sensitivity. Measured difference (`checks/ORDER_CHECK.txt`): 4 S6 runs, last two commands swapped (goal command one step earlier in execution order), 8 of 904 positions, 4 of 870 encoder inputs | validated checkpoints exist only for this order (a convenience, not evidence of correctness); the measured difference is small and is bounded by the sensitivity analysis |
| D5 | size | **decided 2026-11-17:** 640 primary cells in full (10 seeds, 2,000,000 steps), no reduction, run first; then the 320 Family 3 cells and the 1,280 Q4 cells (D8). CPU time from the pilot: about 62 h (640), 93 h (960), 218 h (all 2,240 main cells); GPU time measured before the run | the main question first; fewer steps would leave learning unfinished (pilot curves still rising at 200,000) |
| D6 | reward | **decided 2026-11-17:** the proposal reward (+1 per engaged command, +1 per newly engaged technique, -5 on exposure), selected by pilot rule R2 declared before the pilot; engagement-only reward as sensitivity (Section 8); P1 not rewarded | follows the pre-declared rule and the thesis proposal; the pilot margin is within noise, and the constants are ours, so the sensitivity analysis bounds them |
| D7 | comparators | **decided 2026-11-17:** published methods (Hawkeyes, Li 2025, Wang 2020) only after their replication, as a separate family in D1.1; now: the static honeypot in Family 2 and the `lstm_allpos` arm as Family 3 | STANDARD.md (a comparator that is not replicated would be a strawman); static honeypot and LSTM are the proposal's own baselines |
| D8 | descriptive arms | **decided 2026-11-17:** `gru_allpos`, `baseline` (MAPPO) and IPPO for allpos and NoHistory run in the main run, before the single test opening, and are scored at it as described (Q4), never tested | anything scored after the opening would be a second look at the test; the cost (1,280 cells) was accepted |

## 11. Reproducibility

- `spec_d1.py --freeze` writes `SPEC_D1.json` (SHA-256 of 31 pinned files: protocol, checks (movement,
  order, audit), pilot code and results, env, data, learner, gate, runner, stage driver, scorer, tests, frozen reference
  policies, corpus and AttackMate records, encoder modules). The gate, the runner and the scorer refuse to run unless it passes. Each cell also records
  its encoder checkpoint's SHA-256.
- Evaluation is deterministic given a saved actor: the dry run re-evaluates every cell and must match the
  recorded validation E1 exactly (tolerance 1e-9). RL training on a GPU is not bit-reproducible across
  machines; this is covered by 10 training seeds and confidence intervals, and no identical-retraining
  claim is made.
- Code, configuration, per-cell results and sealed test outputs are committed; checkpoints stay on the
  GPU PCs.

## 12. Known limits (stated in any write-up)

- Simulation: the attacker's commands are replayed and react to the defence only through lures (one
  redirected command at a time). Real attackers react (Dowling et al. 2018; Ferguson-Walter et al. 2021). No result is a claim
  about real attackers.
- PAYOFF, capacity, exposure and movement are assumptions; the sensitivity analyses bound them.
- **Little coordination is demanded by the recorded runs.** 27 of 34 runs touch a single defended zone
  (on average 92% of a run's defended commands fall in its busiest zone), and the Admin zone is never
  visited, so the Admin agent can matter only as a lure target. The agents interact through the shared
  capacity (K = 2) and lures. In the audit, one agent acted alone in two of three trained teams. Team
  activity is reported for every arm, and no claim about multi-agent coordination goes beyond it. The
  random-walk sensitivity (9.3 zone changes per run) is the setting that demands the most coordination.
- The history h assumes complete technique-level observation of the attacker's past commands,
  including those on the attacker's own machine (Section 3).
- The reward constants (+1 technique bonus, -5 exposure penalty) are our choice; the engagement-only
  sensitivity analysis bounds them, other values are not tried.
- D1.0 makes no claim about published deception methods (D7); that comparison is protocol D1.1.
- 34 runs from 7 base scenarios on one testbed; scenario 1 has 18 variants.
- The prediction results (protocol 1.2) did not show the encoders beating the best simple rule overall;
  the history arm may therefore have little extra information to use. G3 tests this first.
