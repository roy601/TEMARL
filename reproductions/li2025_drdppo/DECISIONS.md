# Decisions

Decisions 1-2 were written on 2026-11-16 after reading the result tables only. Decisions 3-16 were written on
2026-11-20 after a **full read** of the paper (all 15 pages, figures rendered), and **before any code or run**.
Every choice that fills a gap the paper leaves open is marked *assumed*; each assumed choice is also a question
to the authors (AUTHOR_CONTACT.md). A target computed under assumed choices can at best support "replicated
under stated assumptions".

| # | gap | choice | why | decided on |
|---|---|---|---|---|
| 1 | Targets | Table 3 (4 methods, 500 confrontations) and Table 4 (7 RL algorithms, 1500 confrontations) | the paper's only numeric results | 2026-11-16 |
| 2 | Seeds | 10 seeds; the paper states none | STANDARD.md requirement 5 | 2026-11-16 |
| 3 | Network | 5 hosts (Host1-2 in subnet1, Host3-5 in subnet2) and 2 servers (subnet3), each with the CVE of Table 1 | the text (p. 8), Fig. 3 and Table 1 agree; Table 2's "hosts 2, servers 5" is a label swap (inconsistency 3) | 2026-11-20 |
| 4 | VC, VI, VA in Eq. (2) | CVSS **v2** confidentiality, integrity and availability impact of each CVE, from NVD (fetched 2026-11-20, `data/nvd/`, SHA-256 in `SHA256SUMS.txt`): None 0, Partial 0.275, Complete 0.660. CVSS v3.x (None 0, Low 0.22, High 0.56) as a sensitivity | the paper names CVSS but not the version; v2 exists for all seven CVEs, v3 is missing for CVE-2014-0226 | 2026-11-20 |
| 5 | w in Eq. (2) | *assumed* w = 0.1; sensitivity w = 0.05 and 0.2 | "a constant", value not published | 2026-11-20 |
| 6 | Host-server communication (L1, NL_i) | *assumed*: every host communicates with both servers (NL = 2 per host, 5 per server); hosts do not talk to each other | Fig. 3 shows only the physical topology (router, switches); the text says hosts "interact with different servers due to office business". Critical: with v2, 5 of 7 CVEs have identical impact (Complete/Complete/Complete, both servers included), so the attacker's target is decided almost entirely by these unpublished links (finding F1) | 2026-11-20 |
| 7 | Honeypot nodes in Eq. (2) | *assumed*: an H-honeypot carries the CVE of the server it clones (m1) and NL = the number of F-honeypots linked to it; an F-honeypot has no vulnerability (impact 0) and NL = 1. Both are candidate targets and enter the normalising sum | the paper's mechanism (p. 5: F-honeypots raise the H-honeypot's correlation score); their own scores are unstated | 2026-11-20 |
| 8 | Attacker | picks the node with the highest Eq. (2) importance; ties broken uniformly at random; exploitation succeeds with probability 1; defence succeeds iff the picked node is a honeypot | p. 4-5; the tie-break is the only randomness the published attacker model can have | 2026-11-20 |
| 9 | Episode and reward | *assumed*: 30 steps (Table 2); the attacker evaluates and attacks at the last step only, so R_t = R2 before it and +R1 / -R1 at it; *assumed* R1 = 10, R2 = 0; the cost term of Eq. (5) is subtracted at every step | R1 and R2 are unpublished; R2 ("otherwise") can only occur if the attack does not happen at every step | 2026-11-20 |
| 10 | State and action encoding | *assumed*: state = Eq. (3) flattened (counts, L1, L2, Aim, node states); action = one discrete choice among {no change, add H, remove H, add F, remove F, retarget H_i to server j, relink F_k to H_i}; actions violating Eqs. (10)-(14) are masked | the paper defines the elements, not their encoding; a softmax output (Table 2) implies one discrete distribution | 2026-11-20 |
| 11 | PPO settings | Adam lr 0.005, gamma 0.9, actor one hidden layer of 32 with softmax output (published). Clip **0.2** (text, p. 10) as primary; **0.9** (Table 2) as a sensitivity. *Assumed*: critic one hidden layer of 32, GAE lambda 0.95, 4 epochs per update, one update per episode (batch = 30 steps) | partly published; clip factor contradicts itself (inconsistency 4); lambda, epochs, minibatch and critic unstated | 2026-11-20 |
| 12 | DSP | **primary:** share of defence successes over the training episodes (500 for Table 3, 1500 for Table 4); **alternative:** share over 500 / 1500 evaluation episodes of the trained policy | the same DRD-PPO gives 97.09% (Table 3, 500) and 98.61% (Table 4, 1500), and the paper trains for 500 episodes: the counts match training runs, not a fixed evaluation set | 2026-11-20 |
| 13 | Baselines of Table 3 | Alg1: every component chosen uniformly at random among valid actions; Alg2: 2 H- and 10 F-honeypots fixed, targets and links chosen by PPO; Alg3: same counts, targets and links random | p. 10 descriptions | 2026-11-20 |
| 14 | The six other RL algorithms (Table 4) | **NOT ATTEMPTED** in this replication: only the DRD-PPO row of Table 4 is a target here | no setting of DRD-Q, DQN, DDQN, AC, PG or SAC is published; tuning them ourselves would produce our results, not theirs | 2026-11-20 |
| 15 | Ablations of Figs. 4-5 | not targets (figures only, no numbers in text except "26.7%", which has no stated base) | STANDARD: targets are published numbers | 2026-11-20 |
| 16 | Use in TEMARL (D1.2) | only after this replication: DRD-PPO enters D1.2 as a declared adaptation (single-agent PPO, its published settings, our environment) if at least the primary targets reach CLOSE; otherwise it is reported as not compared, with the reason | D1.0 decision D7 | 2026-11-20 |

## Findings from the full read

- **F1 (critical):** under CVSS v2, Host2, Host4, Host5, Server1 and Server2 all have Complete/Complete/Complete
  impact; Host1 and Host3 have Partial/Partial/Partial. Eq. (2) then ranks the assets almost only by NL_i, the
  number of communicating devices, which the paper does not publish (Fig. 3 is the physical topology). Under
  v3 all six available CVEs are High/High/High. The paper's attacker model therefore cannot be reconstructed
  from the paper alone; decision 6 is the single most influential assumption.
- **F2 (corrected 2026-11-20, see A1):** with decisions 6-8, an H-honeypot that clones the most important
  server outranks it only with **more linked F-honeypots than the server has communicating devices**: 6 under
  link patterns P1 and P3, 4 under P2, for every w (w scales both sides and drops out). Such a deployment
  (1 H + 4-6 F) costs 27-33 over a 30-step episode under decision 9, against R1 <= 10, so whether a
  reward-maximising learner defends at all depends on the reward settings. The first version of F2 ("one
  F-honeypot") was wrong.

## Inconsistencies recorded

1. Table 4 is captioned "Comparison of DSP of four methods" but lists seven algorithms.
2. The conclusion says DRD-PPO "improves defensive success probability by at least 3.29%" over other RL methods;
   98.61 - 95.32 = 3.29 percentage points (absolute), not a relative percentage.
3. Table 2 lists "Number of host (ns) 2" and "Number of server (nh) 5"; the text, Fig. 3 and Table 1 give 5
   hosts and 2 servers, and Eq. (3) uses n_h for hosts and n_s for servers.
4. The clip factor is 0.2 in the text (p. 10) and 0.9 in Table 2.
5. Eq. (3)'s description names "H-honeypots and H-honeypots" for n_d and n_v (the second is F-honeypots).
6. The attack is called vulnerability exploitation (p. 4-5) and a "DDOS attack" (p. 9, step 6).
7. SOURCES.md recorded the licence as CC BY; the article states CC BY-NC-ND 4.0 (corrected in SOURCES.md).

## Calibration protocol (C1-C9), declared 2026-11-20 before any code or run

The corresponding author did not answer earlier requests (user, 2026-11-20). The unpublished settings are
therefore **calibrated** against published numbers, under a split between calibration targets and held-out
targets, so that a match is evidence and not a fit. The result is called a **calibrated replication**.

- **C1, verdicts.** Only held-out targets receive MATCH / CLOSE / NO MATCH. Calibration targets are reported
  as "used for calibration", with the distance reached, never as a match.
- **C2, stage 1: environment, no learning.** Alg1 (random deployment) and Alg3 (random relations, maximum
  counts) have no learning, so their DSP depends only on the environment rules. Calibration targets: Table 3
  Alg1 **28.43** and Alg3 **55.19**. Grid (declared now, 24 settings):
  - w in {0.05, 0.1, 0.2, 0.5};
  - host-server links: P1 every host with both servers; P2 subnet1 hosts with Server1, subnet2 hosts with
    Server2; P3 subnet1 hosts with both servers, subnet2 hosts with Server2;
  - attack timing: at the last step only, or at every step (episode ends at the first attack).

  Each setting: 10 seeds x 500 episodes. Selection: the smallest sum of squared differences from the two
  targets; ties to the earlier setting in the order listed (w = 0.1, P1, last step first).
- **C3, stage 2: the learner.** With the stage-1 environment fixed, calibration target: Table 3 DRD-PPO
  **97.09**. Grid (12 settings): R1 in {1, 5, 10}, R2 in {0, 0.5}, clip in {0.2, 0.9}; other PPO settings as
  decision 11. Each: 10 seeds x 500 training episodes. Selection: the mean DSP closest to 97.09; ties to the
  earlier setting.
- **C4, held-out targets, run once with the final setting:** Table 3 Alg2 **98.31** (PPO chooses relations at
  maximum counts) and Table 4 DRD-PPO **98.61** (1,500 training episodes). They are never used for selection
  and are computed once, after stages 1 and 2 are closed (as a sealed test).
- **C5, identifiability.** Each stage reports how many grid settings land within 2 points of its targets. If
  many do, the calibration is weakly identified, and this is stated with the result.
- **C6, every trial is logged** in `calibration/CALIBRATION_LOG.csv` (stage, setting, seed, DSP) and committed.
  New trials (for example the user's own guesses) are allowed only by adding them to this protocol in a
  commit **before** they run, and never after a held-out target has been computed.
- **C7, the links are a simulation setting.** The paper is a pure NetworkX simulation, so its communication
  links are a setting of the simulator, not empirical data. Only the three declared patterns are tried, not a
  search over all 1,024.
- **C8, raw material used.** No code and no dataset exist ("all data ... included in this published
  article"). Everything available is used: equations (1)-(21), Algorithm 1, Table 1 (CVEs), Table 2, Fig. 3,
  the baseline descriptions, and the NVD records of the seven CVEs (`data/nvd/`). Nothing else needs to be
  downloaded.
- **C9, Table 4's other algorithms** stay NOT ATTEMPTED (decision 14). Exception noted for later: DRD-Q
  follows the paper's reference 8, Wang et al. 2020 (IEEE Access 8, 35792), which is on our comparator list;
  its published Q-learning settings could support DRD-Q (95.32) as a separate, declared step.

## Amendments after the devil's-advocate review (A1-A10), 2026-11-20, before any code or run

The review (verdict STOP on the claim "the held-out verdicts are genuine evidence") showed that both held-out
targets (98.31, 98.61) lie within 2 points of the calibration target 97.09, and that a policy at 100% is CLOSE
to both (gaps 1.69 and 1.39). The protocol is amended as follows; nothing has been run.

- **A1, F2 corrected** (above).
- **A2, informativeness test.** A held-out target receives MATCH / CLOSE / NO MATCH only if two reference
  policies are both **outside** its CLOSE band (more than 2 points away), under the final setting: the
  **scripted** policy (one H-honeypot on the top server, then F-honeypots linked to it until it outranks the
  server, then no change) and the **random-initialised** DRD-PPO (no update, same DSP metric). Otherwise the
  target is reported **UNINFORMATIVE**, with the three numbers.
- **A3, verdict labels** (added to STANDARD.md and audit.py): **CALIBRATION TARGET** for a number used to set
  unpublished parameters (distance reported, no verdict) and **UNINFORMATIVE** as in A2.
- **A4, the claim.** In D1.2, DRD-PPO enters as an **adapted comparator** (its published hyperparameters, our
  environment) whatever this replication finds. "Replicated" is claimed only from informative held-out
  verdicts of MATCH or CLOSE. Decision 16 is read with this amendment.
- **A5, DSP reported three ways.** Primary as decision 12 (over training episodes); also the DSP of the
  trained policy over separate evaluation episodes (same count, sampled actions) and the random-initialised
  policy's DSP (A2). Verdicts use the primary.
- **A6, attack timing replaces "every step".** "Every step, episode ends at the first attack" would end
  every episode after one action, which no policy can defend. The second option is instead: the attack step
  is drawn uniformly from 1-30 at the start of each episode, and the episode ends at the attack (the defender
  does not know when reconnaissance finishes). Stage 1's grid is otherwise unchanged (24 settings).
- **A7, episode start and baselines.** DRD-PPO, Alg1 and the scripted policy start with no honeypot. Alg2 and
  Alg3 start each episode at the maximum counts (2 H, 10 F) with targets and links drawn uniformly at random;
  then Alg2's PPO chooses only re-targeting and re-linking actions, and Alg3 chooses them uniformly at random.
- **A8, action details (decision 10, completed).** 29 discrete actions: no change; add H (lowest free slot,
  target Server1); remove H (highest active slot; its F-honeypots move to the other H); add F (lowest free slot,
  linked to the lowest active H); remove F (highest active slot); re-target H_i to server j (4); re-link F_k to
  H_i (20). Masks follow Eqs. (10)-(14); because Eq. (14) links every F-honeypot to exactly one H-honeypot,
  the last H cannot be removed while F-honeypots exist. Actions that change nothing are masked.
- **A9, PPO details (decision 11, completed).** Actor and critic each one hidden layer of 32 with tanh; masked
  softmax output; Adam lr 0.005 for both; standard clipped surrogate min(r A, clip(r) A) and squared critic
  error (Eqs. (17) and (21) as printed omit these: inconsistencies 8-9); no entropy term (Eq. (17) has none);
  advantages normalised per update; one update of 4 epochs after every episode; CPU, 1 thread.
- **A10, user trials and sensitivities.** The user's own guesses are rows of `EXTRA_TRIALS.csv`; a row runs only
  if the file is committed and unchanged, and is logged like every grid trial. Besides the grid parameters, an
  extra trial may set: `cvss` (v2 or v3; v3 uses CVE-2014-0226's v2 values, which has no v3 record) and `h_links`
  (`f_only`, decision 7, or `f_plus_server`: an H-honeypot also copies its server's communicating devices).
  The calibration log is `out/calibration_log.csv` (C6's path changed so that the audit sees it as a result).

## Inconsistencies recorded (continued)

8. Eq. (17) is printed as A_t min(r_t, clip(r_t)); PPO's surrogate is min(r_t A_t, clip(r_t) A_t).
9. Eq. (21) is printed without the square of the critic error.

## A11, after stages 1-2 and a second devil's-advocate review (2026-11-21, before the held-out run)

- **Stage results:** no stage-1 setting came within 2 points of both Alg1 28.43 and Alg3 55.19 (Alg1 0.9-19.6,
  Alg3 87.6-100; w had no effect, as F2 predicted), and no stage-2 setting came within 2 points of DRD-PPO
  97.09 (0.02-0.34%: under decisions 7-9 a reward-maximising learner does not defend).
- **Proposal rejected:** a search over eight further readings of the paper (M1 proportional attacker, M2 tie rule,
  M3 Alg1 as one random configuration, M4 joint action per step, M5 cost once per episode, M6 larger R1, M7
  F-honeypot as a host clone, M8 H copies server links) until the targets are met. Review verdict STOP: about 9,216
  configurations against 3 numbers, with uninformative held-out targets, cannot separate the authors' mechanics
  from our flexibility; reaching DRD-PPO 97 needs a reward-to-cost dial (M5/M6), not a mechanism.
- **Decision:** the calibration is closed as run. The held-out targets are computed once, and the paper is reported
  as **not reproducible from the published text**. M1-M8 may later be run only as a **declared sensitivity
  analysis** (every combination reported, no selection), with a null-fit rule fixed beforehand: a reading counts
  only if it is within 2 points of all three targets and the same search against three random decoy targets
  fits clearly worse. In D1.2, only conclusions that hold under all readings are claimed.

## A12, declared sensitivity analysis of the paper's readings (2026-11-21, before any code or run)

Requested by the user after the held-out run ("try again with a different approach"); allowed by A11 as a
declared sensitivity analysis. It does **not** change any verdict in REPORT.md, and nothing is selected.

- **Question:** is there any reasonable reading of the paper under which its Table 3 numbers come out?
- **Factors** (each tied to the paper; first value = the reading used so far):
  - M1 attacker: argmax of Eq. (2) / **samples a node with probability proportional to its normalised
    importance** (Eq. 2 normalises; the paper reports an "attack probability");
  - M2 ties: random / real asset first;
  - M3 Alg1: random walk of actions / **one random configuration per episode** (n_d uniform 0-2, n_v uniform
    0-10 when n_d > 0, random targets and links; "randomly configures the number ..., the association
    relationship, and the protection target");
  - M4 action: one change per step (A8) / **one joint action per step** (Eq. 4: change of n_d, change of n_v,
    all targets m1, all links m2; factored softmax heads, the log-probability summed over the heads in use);
  - M5 cost: every step (Eq. 5 as read) / **once, for the deployment at the attack** ("deployment cost of
    H-honeypot and F-honeypot in the ... strategy");
  - M6 R1: 10 / 100;
  - M7 F-honeypot: no vulnerability / **low-level clone of a host** (F_k carries the CVE of Host(k mod 5)+1);
  - M8 H-honeypot links: F links only / also its server's communicating devices (`h_links`).
- **Design:** the full factorial, 2^8 = **256 combinations**, each run once on the closed calibration's final
  setting (w 0.1, links P1, attack at the last step, CVSS v2, R2 0.5, clip 0.9; R1 as M6). Per combination:
  Alg1, Alg3 and DRD-PPO (500 episodes), 10 seeds, DSP as decision 12. Every combination is reported.
- **Null-fit rule:** a combination *fits* a triple if its mean Alg1, Alg3 and DRD-PPO are each within 2 points.
  Three **decoy triples**, drawn before any run (seed 20261121, offsets of 10-30 points with random sign,
  clipped to [1, 99]): D1 = (51.17, 84.51, 99.00), D2 = (39.70, 34.60, 75.48), D3 = (8.24, 75.21, 99.00).
- **Reading, declared now:**
  - no combination fits the real triple (28.43, 55.19, 97.09): *Table 3 is not produced by any of these 256
    readings of the paper*;
  - some fit the real triple, and at least as many fit a decoy: *the readings are flexible enough to fit nearby
    arbitrary numbers, so a fit does not identify the paper's mechanics*;
  - some fit the real triple and no decoy is fitted: those combinations are reported as *candidate readings
    consistent with Table 3* (never "reproduced"), and only for them Alg2 (500 episodes) and Table 4 DRD-PPO
    (1,500 episodes) are run once, descriptively.
- Outputs: `out/sensitivity_m_log.csv` (every trial), `out/sensitivity_m.json`, `SENSITIVITY_M.md`. Runs once.

## A13, figure-derived reconstruction (2026-11-21, before any code change or run)

Requested by the user ("try another way") after A12. Instead of searching, the hidden settings are **derived** from
the paper's own figures, then the model runs **once**. The plateaus of Figs. 5 and 6 were measured from the figure
images in the PDF (`checks/digitize_figures.py`, `data/figure_values.json`; median over episodes 400-500; axis
calibration residual <= 0.002):

| quantity | DRD-PPO | Alg1 | Alg2 | Alg3 | DRD-PPO without F (Fig. 5) |
|---|---|---|---|---|---|
| reward (Figs. 6a, 5a) | +0.084 | -1.910 | -0.904 | -1.750 | -1.004 |
| attack probability (Figs. 6b, 5b) | 0.453 | 0.621 | 0.329 | 0.554 | 1.000 |
| defence cost (Fig. 6c) | 0.912 | 1.534 | 1.901 (hidden under Alg3) | 1.901 | - |

**Derivations** (arithmetic on the measured plateaus; no Table 3 or Table 4 number is used):
- **D1 reward rule:** the plotted episode reward = outcome (+R1 success, -R1 failure) - deployment cost, the cost
  charged **once per episode**. R1 = reward + cost for the converged near-certain successes: 0.084 + 0.912 = 0.996
  (DRD-PPO), -0.904 + 1.901 = 0.997 (Alg2); and without F-honeypots the agent deploys nothing and always fails:
  -1.004. So **R1 = 1, R2 = 0** (an R2 would add 29 R2 to every episode reward), **cost once** (A12's M5 "final").
- **D2 DRD-PPO's converged deployment:** cost 0.912 -> **1 H + 4 F** (the only combination costing 0.9).
- **D3 links:** 4 linked F-honeypots outrank the top server and 3 do not (the learner would otherwise pay 0.8), so
  the top server has exactly **3 communicating devices**: link pattern **P2** (subnet2's three hosts with Server2,
  subnet1's two with Server1).
- **D4 full deployment** (Alg2, Alg3): cost 1.901 -> **2 H + 9 F**.
- **D5 w:** Fig. 6b DRD-PPO 0.453 = (0.9607 + 3w) / (0.9607 + 3w + 0.9607 + 4w) gives w = 0.53; **w = 0.5** (0.454).
- **D6 attacker (an inference):** Fig. 6b's values for Alg3 (0.554) and Alg2 (0.329) contradict an attack
  probability counted over all H-honeypots (0.277 for both) and agree with one counted over the **clones of the
  target only** (about 0.54 and 0.33). Hence the attacker's target is the most important real asset, and only
  H-honeypots cloning that asset compete with it: the attacker attacks the most important of the target and its
  clones (ties uniform), and the defence succeeds iff that is a clone (**"clone_specific"**). Attack probability
  (reported) = importance(target) / (importance(target) + sum over its clones).
- **D7 Alg1:** mean cost 1.534 -> the simplest consistent random configuration: **2 H, F uniform 1-10** (mean
  1.55; F uniform 0-10 gives 1.50, also within the plotted noise).
- **Not derivable, kept from the protocol:** one change per step (A8), attack at the last step (A6), clip 0.2
  (decision 11), A9's PPO settings, CVSS v2, F-honeypots without a vulnerability (decision 7), H links f_only.

**Readings run (10 seeds each):** **R-A (primary)** = D1-D7; **R-B (secondary)** = D1-D5 and D7 with the pre-A13
attacker (all honeypots compete).

**Pre-registered predictions** (exact arithmetic for the non-learning baselines, before any run):

| | R-A | R-B | Table 3 |
|---|---|---|---|
| Alg1 | 36.17% | 60.83% | 28.43 |
| Alg3 | 66.41% | 100.00% | 55.19 |

Both readings are therefore predicted to miss Alg1 and Alg3 by more than 2 points. The learners have no exact
prediction.

**Roles.** Used for the derivations (not tests): the Fig. 5 and Fig. 6 plateaus above, except Alg1's attack
probability (0.621). **Tests** (never used): Table 3 DSP of Alg1 (28.43), Alg3 (55.19), DRD-PPO (97.09) and Alg2
(98.31); Table 4 DRD-PPO (98.61, 1,500 episodes); Fig. 6b Alg1 (0.621); and, descriptively, how fast DRD-PPO's
cost falls below 1.0 (in Fig. 6c, by about episode 150-200). A2's references (scripted, untrained) are reported
for every learner target. A test is "consistent" if within 2 points (0.02 for attack probability).

REPORT.md's verdicts belong to the calibrated replication and do not change. The result is labelled a
**figure-derived reconstruction**: even full consistency would show only that the paper's numbers follow from
mechanics inferred from its own figures. Outputs: `out/figure_reconstruction_log.csv`,
`out/figure_reconstruction.json`, `FIGURE_RECONSTRUCTION.md`. Runs once.
