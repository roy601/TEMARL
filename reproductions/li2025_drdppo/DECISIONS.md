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
- **F2:** with decisions 6-8, any policy that clones the most important server with one H-honeypot and links at
  least one F-honeypot to it makes the H-honeypot the strict argmax, so defence succeeds with certainty. A DSP
  below 100% then comes from exploration during training (decision 12) or from tie-breaking.

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
