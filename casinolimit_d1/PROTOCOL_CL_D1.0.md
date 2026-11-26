# Protocol CL-D1.0: history-aware deception agents on CasinoLimit (simulation)

**Status: FROZEN, 2026-11-22** (`SPEC_CL_D1.json`, written by `spec_cl_d1.py --freeze` after the
user's approval; decisions C1-C10 settled the same day). Revised before the freeze after the design
review of 2026-11-18. At the freeze:
- no CL-D1.0 agent had been trained or evaluated, and the gate had not run;
- only the validation-only check of Section 2b, the diagnostics of Section 7 (2026-11-21 and
  2026-11-22) and code tests had run;
- the D1.0 test (CAM-LDS) had not been opened, so no D1.0 test number could influence this protocol.

Any change now needs a new version. The order of events is provable from git history.

## 0. What CL-D1.0 is

CL-D1.0 is the second dataset for the deception claim of protocol D1.0. It uses D1.0's frozen
environment, learner, reference policies, reward, settings and statistics, unchanged, on CasinoLimit.

It is a **follow-up study on previously analysed folds**: an exploratory CasinoLimit run on the same
folds wrote its test outcomes unsealed (Section 2a). That run can be reported later as exploratory
evidence, with its limits, after the CL-D1.0 opening. It is never presented as a confirmatory result.

The code is D1.0's code. `cl_world.py` loads D1.0's own files `env_cmd.py`, `mappo_cmd.py` and
`baselines_cmd.py`, which must be byte-identical to their `SPEC_D1.json` pins. It gives them
CasinoLimit's inputs: labels, payoff rows, machines and runs. CL 1.0 reused the frozen encoder the same
way (`cl_port.py`).

## 1. Claim and questions

Claim under test, **in simulation only**: *deception agents that know the attacker's history increase
simulated engaged-command counts, compared with agents without history.* Replayed commands and
simulated lures do not show that real attackers stay engaged longer. There is **no protection outcome**
on CasinoLimit (Section 4), so the "protect assets better" part of the thesis claim is not tested here.

- **Q1 (main, Family 1):** does the history arm (frozen CL 1.0 `allpos` Transformer embedding h) beat
  NoHistory (h = 0, same network otherwise) on E1?
- **Q2 (Family 2):** does the history arm beat the reference policies on E1?
- **Q3 (Family 3):** does the Transformer history beat an LSTM history (`lstm_allpos`)?
- **Q4 (descriptive):** GRU and the old Transformer as the encoder; IPPO vs MAPPO; allpos vs NoHistory
  under IPPO. These are described, never tested.
- **Q5 (Section 9, Family H):** does Q1's answer hold when each arm gets its own hyperparameters, tuned
  on validation (protocol D1.1's design)?

Published deception methods are not compared here (D1.0 decision D7). The Kuwano recommender is a
technique-recommendation method, not a deception controller; putting it into this RL system would be
our adaptation, and it stays out until it is replicated (decision C5).

## 2. Data

- **Corpus:** CasinoLimit (human CTF), exactly as in CL 1.0: `casinolimit_real/out/steps.jsonl`
  (SHA-256 `399ef563…`), 114 attackers, 8,201 commands, 66 parent techniques (the dataset's released
  labels), ordered by `exec_index`.
- **Folds:** CL 1.0's 5 whole-attacker folds (`cl_split.py`): test Fi, validation F(i+1), training the
  other 3. Each attacker is the test run of exactly one fold, which gives 114 test units. As on CAM-LDS,
  each fold's validation runs are another fold's test runs.
- **Recorded machine of every command:**

  | machine | commands |
  |---|---|
  | start | 3,978 |
  | bastion | 2,463 |
  | meet | 1,748 |
  | intranet | 12 |

  - 48 of 114 attackers use a single machine.
  - 6 attackers reach intranet.
  - 113 attackers begin on start, 1 on bastion.
- **Reproducibility:** CasinoLimit records no attacker goal. Every command executes on one of the four
  machines.

## 2a. Earlier exposure of the test runs (disclosed before the freeze)

**What it was:**
- An exploratory run of `casinolimit_real_full_arch/pipeline.py` (teammate's runner, no protocol)
  finished on GPU PC 2 on 2026-11-18. The results are in commit `5980bfde`, with the warning note
  `casinolimit_real_full_arch/results/main/README_NOT_PROTOCOL.md`.
- It wrote test outcomes **unsealed**, including a per-cell table of test summaries
  (`results/main/RESULTS.md`), on the same CasinoLimit test runs that CL-D1.0 uses.
- Its environment differed: decoys were on/off with no decoy type, efficacy 0.5, fog levels, and its
  encoders were retrained on PC 2.

**Exposure:**
- The user stated on 2026-11-18 that they had not read its test numbers.
- The check of that run, for this protocol, read only code, file structure and validation fields.
- A design review written afterwards states that its results had been shown in a conversation.
- Neither statement can be verified from the repository.

So CL-D1.0 treats these test runs as **previously exposed**. Sealing CL-D1.0's own outputs does not make
the underlying test runs unseen.

**Used, from validation only:** at the best validation checkpoint, every arm, NoHistory included, was
within about 2% of its environment's ceiling (validation E1 about 35.4 against about 36.0). That setup
therefore leaves **limited room** for a detectable history effect. This is why CL-D1.0 uses D1.0's
environment with decoy types (decision C1). No other decision used that run.

## 2b. Validation-only learning check before the freeze (2026-11-18)

**Setup:**
- Folds F1 and F3, using their validation runs only. These are the test runs of F2 and F4.
- 5 repeats, randomness seed 100101.
- NoHistory MAPPO, seed 101, 200,000 steps, on a CPU.
- No test episode was built, and no history arm was trained.

**Validation E1:**

| policy | F1 | F3 |
|---|---|---|
| none | 0.00 | 0.00 |
| random | 4.58 | 4.86 |
| greedy | 14.24 | 13.90 |
| planner | 16.30 | 16.51 |
| NoHistory MAPPO, best of the curve | 18.45 | 18.88 |
| clairvoyant | 28.03 | 27.17 |

**What it shows:**
- Learning works: the curve rises from 5.7 to 18.5.
- After 200,000 steps the environment is not saturated: NoHistory reaches about two thirds of the
  clairvoyant ceiling. At the planned 2,000,000 steps NoHistory may close part of this gap, so this is
  not proof that room remains for history.

Nothing was changed after this check. These numbers are reported as a pre-freeze check, not as results.

## 3. Environment (D1.0's `env_cmd.py`, unchanged; CasinoLimit's inputs from `cl_world.py`)

- **Agents and actions:** 4 defender agents, one per machine (start, bastion, meet, intranet). Each
  has 6 actions: none plus 5 D3FEND decoy types.
- **Why decoy types (decision C1):**
  - The five types are D1.0's, frozen for CAM-LDS on 2026-11-17 from D3FEND's decoy categories,
    before any CasinoLimit agent existed.
  - They are not chosen to favour any arm.
  - They make the defender choose a decoy that suits the attacker's next technique. The on/off
    environment had no such choice, and every arm, NoHistory included, saturated it.
  - The result is reported whichever arm it favours.
- **Settings:** capacity K = 2, exposure rate beta = 0.2, set aggregation `max`, efficacy 1.0,
  recorded movement, and the two lure decoy types. These are D1.0's settings.
- **Reward:** the proposal reward, D1.0's decision D6, carried over unchanged. It gives +1 per engaged
  command, +1 when the engaged command carries a technique not engaged before in the episode, and −5 on
  exposure.
- **Payoff (PAYOFF[technique, decoy]):** D1.0's rule from `d3fend_payoff.py`, with its four constants
  and its PRIMARY / ADJACENT tactic sets, applied to each technique's tactic.
  - **45 of the 66 techniques** are in D1.0's frozen vocabulary. Their rows are identical to D1.0's
    (tested).
  - **The other 21** take their tactic from **ATT&CK v15.1** (MITRE's official STIX release of
    2024-05-02, current when the CasinoLimit commands were recorded in May 2024; the bundle SHA-256 is
    pinned; `attack_v15_1_tactics.json` holds the extract).
    - Each of the 21 has exactly one tactic, so no tie rule is needed.
    - For the 45, the frozen tactic is always one of ATT&CK's listed tactics (45/45).
    - The rule "earliest tactic in ATT&CK order" would agree on 42 of 45; it differs for T1053, T1550
      and T1556, and is not used.
  - **Resource Development** (T1587, 160 commands; T1608, 18) has no decoy in D1.0's tactic sets, so
    the rule gives every decoy 0.10. This is stated, not adjusted.
  - **ATT&CK supplies the tactic labels only.** It does not validate the payoff values. These are
    modelling assumptions, bounded by the sensitivity analyses of Section 8, including one that changes
    which decoy suits which tactic.
- **No goal, no target:** no command is a goal command, there is no target zone, and the entry machine
  is start.
- **Normaliser:** the step input t / max_steps uses max_steps = 512, at least as long as the longest
  run (482), as D1.0's 64 is for its 42. This is a normaliser only, not a cap.
- **What each agent sees before it acts** (audited for the review; `env_cmd.local_obs`; tested):
  - its own machine;
  - whether the attacker is now on its machine, and, if so, the labels of the command just executed
    there;
  - its own current decoy, and whether that decoy engaged the last command;
  - whether a lure has sent the attacker to its machine next;
  - whether its machine is compromised;
  - the team's decoy count, and the step number;
  - the past-only history embedding h (commands before the current step only).

  No agent sees the next command, the next machine or the next outcome. Those reach only the
  clairvoyant ceiling (`peek_next_*`).
  - The centralised critic of MAPPO, used in training only, also sees the global state, which includes
    the number of recorded commands left in the run. It is never an input at test time.
  - All CasinoLimit commands run on defended machines, so unlike D1.0 (where 14.6% of h's commands ran
    on the attacker's own machine), h contains only commands on defended machines. h still assumes
    complete technique-level observation of those commands.
- **What is simulated, not recorded** (audited for the review): the attacker's commands and machines
  are replayed from the recording, except for these simulated mechanics:
  - **Engagement:** a decoy engages a command with probability φ · efficacy · PAYOFF, where
    φ = min(1, K / active decoys).
    - Capacity is a **soft** limit: above 2 active decoys every decoy's chance shrinks.
    - Capacity violations are counted.
  - **Exposure:** an engaged command exposes the deception with probability β(1 − ρ). After exposure no
    decoy engages for the rest of the episode.
  - **Lures:** an engaged lure with a partner decoy on another machine moves the attacker's next
    command to that machine. This is the only simulated attacker reaction. A lure without a partner is
    a dead end, which exposes the deception with probability β.
- **Common random numbers** as in D1.0: every arm and reference policy meets the same simulation
  randomness on the same episode, so comparisons are paired.

## 4. Outcomes (fixed now)

| # | outcome | definition | role |
|---|---|---|---|
| E1 | engaged commands | commands engaged per episode (code name `dwell`) | **primary** |
| S2 | engaged fraction | E1 / episode length | secondary, descriptive; also reported as Family 1's contrast (Section 10) |
| S3 | distinct techniques engaged, exposure, lure chains, dead ends, capacity violations, team activity (share of steps with ≥ 2 decoys; each agent's decoy share and engagements) | `episode_stats` | descriptive; techniques and exposure are partly rewarded, so they are never claimed as a win |

There is **no protection outcome**. CasinoLimit records no attacker goal, and only 6 of 114 attackers
reach the intranet, so neither D1.0's P1 nor S1 can be defined.

## 5. Step 0: validity gate (run after the freeze, before any learned agent; `gate_cl.py`)

**Setup:**
- All 114 runs, seed 300000, 20 repeats per run (disjoint from validation and test randomness).
- The ladder is D1.0's:
  - none, random and greedy;
  - fixed: the best of the 6^4 constant joint actions, chosen leaving the scored run out;
  - planner: a transition rule fitted on all other runs; it uses history, with no learning;
  - clairvoyant: the ceiling.
- The planner's code is D1.0's, and a test checks that it makes D1.0's decisions on CAM-LDS.
- Unit = run; 10,000-resample bootstrap with seed 20261103.

**Pass criteria, both required (D1.0's G2 and G3 on E1; D1.0's G1 is about protection and does not
apply):**
- **G2, a real decision problem:** clairvoyant − best of {fixed, greedy} > 0, with a CI that excludes 0.
- **G3, a simple history rule helps:** planner − greedy > 0, with a CI that excludes 0.

**A stop rule (decision C10, as in D1.0):** if the gate fails, no learned agent is trained.
- The failure is reported as the CasinoLimit result: *in this setup, a simple history rule shows no
  benefit over the greedy rule*. It does **not** show that no history-based method could help.
- The gate runs once, on the frozen environment. It selects nothing and tunes nothing: the environment
  is not changed after it, whatever it shows.

**Fitted on other runs:** the gate's fixed and planner policies use all other runs, including runs that
later serve as test runs. So the gate is a diagnostic of the environment, not an untouched-test
evaluation. The learned arms' reference policies (Section 6) are fitted on each fold's training runs
only.

## 6. Arms and comparators

- **Primary arms:** `allpos` (history) and NoHistory, both MAPPO. They differ only in h.
- **Family 3:** `lstm_allpos`, MAPPO.
- **Q4 (descriptive):** `gru_allpos` and `baseline` (old Transformer) with MAPPO; allpos and NoHistory
  with IPPO.
- **Encoders: the CL 1.0 checkpoints, unchanged.**
  - A checkpoint is accepted only if it matches CL 1.0's committed record for it
    (`casinolimit_encoder/out/train/main/<arm>/<fold>/s<seed>/result.json`, committed with CL 1.0),
    on all of these:
    - **identity:** arm, fold, seed, window (16) and label count (66);
    - **preprocessing:** the fold's validation rows equal the recorded ones;
    - **outputs:** the committed validation logits file has its recorded SHA-256, and the checkpoint's
      own validation logits reproduce it within 1e-3;
    - **score:** its validation BCE reproduces the recorded one within 1e-5.
  - Each checkpoint's SHA-256 is written to the preflight record.
  - 200 checkpoints in total: 4 arms × 5 folds × seeds 0-9. They are frozen during RL.
  - The encoders retrained on PC 2 are valid trained models, but they are not the reported CL 1.0
    checkpoints. They were moved out of the repository, not deleted, before the CL 1.0 files were
    copied from PC 1 (2026-11-21).
- **Reference policies at evaluation:** none, random, static honeypot, fixed, greedy and planner, with
  clairvoyant as the ceiling only.
  - They are run on the arms' test episodes.
  - Static, fixed and the planner are fitted on the fold's training runs only (static and fixed:
    seed 400000, 5 repeats).

## 7. Training and procedure

- **Settings:** D1.0's MAPPO settings (`mappo_cmd.HP`, unchanged), 2,000,000 environment steps per
  cell.
- **Randomness:** seeds 0-9; validation randomness 100000+seed, test randomness 200000+seed;
  20 repeats per run. The repeats are repeated simulations of the same recorded attackers, with fresh
  simulation randomness. They are not new attackers.
- **Selection:** the policy checkpoint is chosen by validation E1 only.
- **Main study (`run_cl.py --study main`):** 7 (arm, learner) pairs × 5 folds × 10 seeds = **350
  cells**. The 100 primary cells run first.
- **Sealing:** test outputs are sealed (`sealed_test.json`; only its SHA-256 goes into `result.json`).
- **Restarting:** `MANIFEST.json` records what decides a cell (including the payoff table's SHA-256),
  plus an invocation log; `RUNNING.lock` works as in D1.0.
- **Procedure (`run_all_cl.py`):**
  - `diagnostics` (before the freeze): preflight of the 200 checkpoints, then one timed cell with its
    dry-run check.
  - `run`: the gate (once; the stage stops if it fails), preflight under the frozen spec, timing, then
    each study's cells and its dry run, and the tuning selection.
  - `open`: opens the test once (Section 10).
- **Machine:** GPU PC 2. Before the diagnostics (2026-11-21):
  1. PC 2's retrained encoders were moved out of the repository.
  2. The 200 CL 1.0 files were copied from GPU PC 1.
- **Diagnostics, before the freeze:**
  - 2026-11-21, under the earlier BCE-only check: all 200 checkpoints reproduced CL 1.0's validation
    BCE.
  - 2026-11-22, under the full identity check of Section 6: all 200 checkpoints passed, with the
    largest validation-logit difference 2.86e-06 (tolerance 1e-3).
  - Both times one cell took 96 s on PC 2's GPU, and its dry-run reproduction was exact.

  The `run` stage repeats the preflight under the frozen spec.
- **Time:** 870 cells at 96 s each, about **23 h**, plus test episodes.

## 8. Sensitivity analyses (declared now, all reported)

1. **Efficacy:** PAYOFF scaled by 0.5 and by 0.75.
2. **Set aggregation:** `mean` instead of `max`.
3. **Reward:** engagement-only reward instead of the proposal reward.
4. **Decoy–tactic table (`payoff_permuted`).** Scaling tests the overall strength of the payoff; this
   one tests whether the assumed **ranking** of decoy types creates the result.
   - **Rule:** for each tactic, in name order, one permutation of the five decoy columns is drawn from
     a generator seeded with **20261122**. It is redrawn until the tactic's best decoy changes, and is
     applied to every technique of that tactic.
   - **What it keeps:** each row keeps its values and its "none" column, and techniques of one tactic
     still share a best decoy. Only which decoy suits which tactic changes.
   - **Computed before the freeze (`cl_world.PERMUTATION_INFO`):**
     - 13 of the 14 tactics change their best decoy. Resource Development's row is constant, so it has
       no best decoy to change.
     - 64 of the 66 rows differ.
     - Discovery carries 57% of the technique labels in the corpus (5,239 of 9,243). Its best decoy
       moves from `decoy_network_resource` to `decoy_environment`.
   - **What it changes:** only the payoff table. The environment's settings are D1.0's. Each cell
     records the table's SHA-256, and the opening checks it.

**Size:** each setting changes only what it names. Each uses allpos and NoHistory (MAPPO), seeds 0-4
and all 5 folds: 5 × 50 = **250 cells**. Each is scored with Family 1's statistics and its descriptive
additions, and reported as a sensitivity result, never as the main claim.

**Not applicable on CasinoLimit:**
- D1.0's random-walk movement, which needs target zones.
- The execution-order sensitivity: CasinoLimit has one recorded order.

## 9. Hyperparameter sensitivity (protocol D1.1's design)

- **Grid:** learning rate {1e-4, 5e-4, 1e-3} × PPO epochs {5, 10, 15}, a subset of the MAPPO authors'
  own sweep. D1.0's setting is the centre.
- **Cells:** allpos and NoHistory (MAPPO), 5 folds, seeds 0-2: 9 × 2 × 5 × 3 = **270 cells**. Both arms
  get the same budget.
- **Selection, nested:** per arm and fold, on that fold's validation runs only, the setting with the
  highest validation E1 averaged over seeds 0-2. Ties: D1.0's setting, then grid order. The selection
  is written to `results_cl/tune/SELECTION.json` before the opening and recomputed at it.
- **Family H:** tuned allpos vs tuned NoHistory on E1.
- **Descriptive:** allpos − NoHistory under each setting; tuned − D1.0's setting.
- **Reading, declared now:**
  - If Family H's verdict equals Family 1's, the result agrees under per-arm tuning in this grid.
  - If not, the Family 1 result depends on the hyperparameters, and both are reported.

## 10. Evaluation (`evaluate_cl.py`, frozen with this protocol)

1. **Dry run, per study:** every cell's actor is re-evaluated on its validation episodes, under the
   study's payoff table, and must reproduce its recorded validation E1 exactly (1e-9). For `tune`, the
   nested selection is written next.
2. **One opening for all 870 cells** (main 350, sensitivity 250, tuning 270). The test is opened
   **once**, after every study's cells exist and every dry run has passed. The opening refuses unless:
   - the spec passes and the gate passed;
   - the selection file matches the recomputed selection;
   - `TEST_OPENED.json` is absent.

   Every sealed file's SHA-256 is checked before it is read. Every cell must carry its declared study,
   setting, arm, learner, test seed, 20 repeats, environment and payoff table.

- **Unit: the run (attacker), 114 test units.** Per unit, E1 is averaged over 20 repeats, then over
  seeds. The 114 attackers took part in one CTF event, so they are not independent draws from all
  attackers.
- **Family 1:** allpos vs NoHistory (1 comparison).
- **Family 2:** allpos vs none, random, static, fixed, greedy and planner (6 comparisons).
- **Family 3:** allpos vs lstm_allpos (1 comparison).
- **Statistics:**
  - Each comparison gets a mean paired difference, a 95% bootstrap CI (10,000 resamples of runs, seed
    20261103), a two-sided Wilcoxon signed-rank test and Holm correction within the family (D1.0's
    `evaluate_d1`, unchanged).
  - "X outperforms Y" only if Holm p < 0.05 and the CI excludes 0; otherwise "no difference shown".
- **Family 1, descriptive additions** (main study and every sensitivity setting; no test, no claim):
  - **Engaged fraction:** the same contrast on E1 / run length per unit. Long runs can dominate the
    count; the fraction weighs every run equally.
  - **By run length:** the contrast within each third of the 114 runs, sorted by length.
  - **By training seed:** the mean difference for each seed, with the spread across seeds. Averaging
    seeds before the run-level statistics gives an interval conditional on these seeds; the per-seed
    spread shows the training variability that this interval does not cover.
- **Not corrected across families:** the families, the sensitivity analyses and Family H answer
  different questions. This is stated with the results.
- **Q4 and the other descriptive results:** mean paired difference and CI only.
- **Every result is reported whatever its direction.**

## 11. Decisions (settled by the user on 2026-11-22: every one as recommended)

| # | decision | choice | why |
|---|---|---|---|
| C1 | environment | D1.0's frozen environment (5 decoy types, capacity, exposure, lures) on CasinoLimit, replacing the on/off environment | the on/off environment saturated on validation for every arm (Section 2a). With decoy types, the agent must match the decoy to the *next* technique, which is where history can help. The types were fixed for CAM-LDS before any CasinoLimit agent existed (Section 3) |
| C2 | payoff | D1.0's rule and constants; 45 rows identical to D1.0, 21 tactics from ATT&CK v15.1 (one tactic each) | no new constant and no hand choice; the ATT&CK release is the one current when the data were recorded. ATT&CK does not validate the values; Section 8 bounds them |
| C3 | outcome | E1 only; no protection outcome | CasinoLimit has no goal data; only 6 attackers reach intranet |
| C4 | settings and reward | D1.0's (proposal reward, K = 2, beta 0.2, max, efficacy 1.0, MAPPO settings), unchanged | no new choice. The shared code makes this a controlled comparison across the two datasets. Raw E1 levels are still not comparable across them: run lengths, machines and techniques differ |
| C5 | arms | D1.0's arms; no published method (Kuwano excluded) | D1.0 decision D7: comparators only after their replication. Kuwano is a recommendation method, so including it would be our adaptation |
| C6 | size | main 350 + sensitivity 250 + tuning 270 = 870 cells, about 23 h on PC 2 | the same design as D1.0 and D1.1 at CasinoLimit's 5 folds, plus the payoff-ranking sensitivity the review asked for |
| C7 | encoders | the CL 1.0 checkpoints only, accepted on identity, preprocessing, validation logits and BCE; run on GPU PC 2 after copying them from PC 1 | the encoders the thesis reports |
| C8 | fog | not included | not part of D1.0; the exploratory run's fog policies were trained under fog, a different question. So no claim of robustness to missing telemetry is made |
| C9 | opening | one opening for all 870 cells | nothing is seen until everything exists |
| C10 | gate | a stop rule (G2 and G3, as in D1.0), with the wording of Section 5 | the gate runs once and changes nothing after it, so it cannot bias the comparison; keeping D1.0's rule keeps the two datasets consistent |

## 12. Reproducibility

- `spec_cl_d1.py --freeze` writes `SPEC_CL_D1.json`. It holds the SHA-256 (after CRLF→LF) of:
  - this protocol and its code, tests and ATT&CK extract;
  - `SPEC_D1.json`, which pins D1.0's environment, learner, reference policies and statistics;
  - `evaluate_d1.py`, the frozen payoff and vocabulary files, and the corpus and vocabulary;
  - the CL 1.0 port, data and split files, CL 1.0's protocol, the encoder modules and the disclosure
    note;
  - one digest over CL 1.0's 200 checkpoint records. Each record holds its validation logits file's
    SHA-256, which the preflight checks.

  The check also runs D1.0's check. The gate, the runner and the scorer refuse to run unless it passes.
- Evaluation is deterministic given a saved actor, which the dry run checks. RL training on a GPU is
  not bit-reproducible; seeds and CIs cover this.
- **Tests (`test_cl_d1.py`):**
  - the world is D1.0's files, and a CAM-LDS environment in the same process is refused;
  - the payoff rows and their sources; the permuted table (rule, seed, what it keeps and changes);
  - runs, folds and machines;
  - the history inputs equal the encoder's windows;
  - no agent observation before a step depends on that step's command or machine;
  - recorded movement, and that the reward does not change any outcome;
  - the planner equals D1.0's; gate smoke run and seeds;
  - cell counts and settings; the setting reaches the optimiser; the study's payoff table is in force
    during training and the dry run, and is restored after; sealing; smoke run;
  - refusal without the freeze; only the CL 1.0 checkpoint is accepted (identity, validation rows,
    logits, BCE); timing dry run; restart identity;
  - nested selection; scoring and the Family 1 descriptive additions; references fitted on training
    runs only and run on the arms' episodes; the opening's per-cell check, payoff table included;
  - the spec and the stage driver.

## 13. Known limits (stated in any write-up)

- **Simulation:** attackers are replayed and react only through lures. PAYOFF, capacity and exposure
  are assumptions, bounded by the sensitivity analyses. Sharing D1.0's code makes the comparison
  controlled, but it does not make the simulation realistic.
- **Previously exposed test runs:** the folds are the ones an exploratory run already evaluated
  unsealed (Section 2a).
- **Engagement only:** no protection result exists for CasinoLimit.
- **Labels:** the technique labels are the dataset's automatic labels. The two Resource Development
  techniques can be engaged only weakly (payoff 0.10).
- **Little coordination is demanded:**
  - 48 of 114 attackers use one machine;
  - the intranet agent sees 12 commands in total, so it matters mainly as a lure target;
  - team activity is reported for every arm.
- **Little information in history:** the CL 1.0 encoders did not beat the best simple rule on
  next-technique prediction (+0.018, CI includes 0). G3 tests whether a simple history rule helps.
- **One CTF:** a single event, so the results apply to it.
- **No fog:** no claim about robustness to missing telemetry.
- **Tuning:** only 2 settings are swept, with 3 values each.
