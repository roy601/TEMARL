# Decisions

Wang et al. 2020 (IEEE Access 8:35792). Started 2026-11-20, before any code of ours. Lessons from the Li 2025
replication applied from the start: (1) check the paper's own numbers for internal consistency before writing a
simulator; (2) know which published numbers encode which, so no target is "predicted" from itself; (3) plan the
informativeness test (a trivial policy must not also land on a target) before any run.

## 1. What the paper gives

| item | where | content |
|---|---|---|
| network | Fig. 6, Table 1 | DMZ (web server), subnet 1 (pad, host 1), subnet 2 (hosts 2-4), subnet 3 (print, file, data server); 12 service access rules |
| vulnerabilities | Table 2 | 7 hosts H1-H7, 13 CVEs with attack type, required/obtained privilege and complexity (Low/Medium/High) |
| attack graph | Fig. 8 | NTPG: 20 edges labelled <UP, RP>; transcribed in `data/ntpg.json` (checked in F7) |
| goal | Section V | the data server (H7) holds the confidential resources; reaching it = defence failed; reaching a decoy = defence succeeded |
| decoys | Section V, Table 3 | 2 decoy nodes, one-to-one mapping (Fig. 2c) onto 7 effective locations: 21 actions; state = alarm vector of the 7 locations: 128 states; initial state all zeros |
| attacker | Eq. 1 | next node = argmax over reachable nodes of alpha I(n) + beta J(n); "the attacker's strategy is expressed by the attacker's interestingness distribution" (Section V) |
| alarms | Section II.B, Table 3 | network monitoring system with missed (FNR) and false (FPR) alarms; four settings (0.05, 0.02), (0.10, 0.06), (0.15, 0.10), (0.20, 0.14) |
| baselines | Eqs. 3-5 | static (21 fixed deployments), random-dynamic (random element of AD at each time t), following-alarm (random element of the alarmed set) |
| learner | Eqs. 10, 14, 15, Alg. 1 | reward -1 / +1 / 0; tabular Q-learning, learning rate 1/(1 + visits), epsilon-greedy |
| metric | Eq. 16, Table 3 | dsp = successful defences / experiments, 1000 experiments |
| results | Figs. 10-14 | figures only (no results table); measured from the vector drawings in `data/figure_values.json` |

## 2. Findings from the published numbers (before any code)

All numbers below are produced by `checks/consistency.py` from `data/figure_values.json` (output:
`data/consistency.json`). A dsp out of 1000 experiments has binomial standard error sqrt(p(1-p)/1000), about
1.4 points at p = 0.75.

| # | finding | numbers | consequence for us |
|---|---|---|---|
| F1 | Fig. 10's four FNR/FPR curves vary between settings far more than 1000 experiments allow. A static policy does not read alarms, so the four curves should be replicates. The control, Fig. 12's ten repeats per setting, is exactly binomial at 1000 experiments. | Fig. 10: chi-square 265 on 63 df (p = 1e-26), as if each point had about 238 experiments. Fig. 12: chi-square 36.8 on 36 df (p = 0.43), about 979 experiments. | Fig. 10 cannot be matched curve by curve. The per-policy mean of the 4 curves is the target (`F10.P01`-`F10.P21`). Something changed between settings for the static runs (for example a new attacker drawn per setting, or fewer experiments); the paper does not say. |
| F2 | Fig. 11 (random-dynamic) cannot be "a fresh random deployment for each of 1000 experiments": its ten repeats per setting range from 0.16 to 0.76. So each repeat draws its randomness once and uses it for all its 1000 attacks. Two readings remain. (a) One random static deployment per repeat. (b) One random sequence A_t (Eq. 4, a function of time t) per repeat. | Within-setting chi-square 4043 on 36 df (as if 9 experiments per point). The Fig. 11 mean, 0.511 (SE 0.028), is z = 2.56 from the mean of the 21 static policies (0.440, reading a) and z = -0.67 from the untrained Q-learner (0.530, reading b). With Fig. 10's own spread, no Fig. 11 value is far from every static policy, so (a) is not excluded. | Reading (b) is chosen (D11); (a) is reported as a sensitivity. |
| F3 | Location 7 is the data server, so a decoy behind it is never reached, and policy (x, 7) is "one decoy at x". The figure agrees on both counts. (x, 7) is the lowest policy in each block, and all 15 two-decoy policies satisfy max(s_a, s_b) <= dsp(a, b) <= s_a + s_b within 2 SE. | One-decoy dsp: web server 0.684, pad 0.253, host 1 0.313, host 2 0.337, host 3 0.105, file server 0.170. 0 violations of 15. | Locations are numbered as Table 2 (D1), policies in lexicographic pair order (D3). Fig. 10 is coherent, so it can serve as a calibration target. |
| F4 | The text's numbers come from the figures. "75.6%" is static policy 1 in the first setting (0.757), the best point of that curve. Policy 1's mean over the 4 settings is 0.742, the best mean is policy 2 (0.759), and the largest point is 0.811 (policy 2, second setting). Random-dynamic max 0.759 and min 0.158 match "close to 75%" and "15.8%". Q-learning at 30000 steps is 0.791-0.811 (mean 0.804), matching "nearly 80%". | `data/consistency.json` F4 | The text adds no independent number. `F10.best_text` is kept as a target, but it is a single noisy point. |
| F5 | The untrained Q-learner (Fig. 13 at 0 steps) has dsp 0.51-0.55 (mean 0.530). With Q = 0 everywhere and first-index tie-breaking it would always play policy 1 (0.742). The value matches random-dynamic (0.511) instead. | `data/consistency.json` F5 | Ties in argmax Q are broken at random (D12). |
| F6 | Training takes 0.31-0.34 s per "training step" (Fig. 14): 30000 steps in about 9600 s. One tabular update on a 128 x 21 table takes microseconds. | `data/consistency.json` F6 | What a "training step" contains is unclear (D12); Fig. 14 is NOT ATTEMPTED. |
| F7 | Fig. 8's edge labels follow from Tables 1-2 if complexity Low = 0.8, Medium = 0.6, High = 0.4 and the Tomcat 0-day = 0.05 (Fig. 7). UP is the best exploit giving at least user; RP is the best root exploit, or user then a local root exploit. Examples: Host 1 <0.6, 0.48> = <Medium, max(High, Medium x Low-local)>; the web server's outgoing <0.8, 0.04> = <Low, Low x 0-day>. Two points are not explained. (i) The four USB edges from pad and host 1 to hosts 2 and 3 are <0.32, 0.32> = 0.8 x 0.4, and the factor 0.4 is unstated. (ii) The text says pad and host 1 "can be accessed from" hosts 2 and 3 through USB, but the arrows point the other way. | 18 of 20 edges derived; 4 USB edges (one factor) unexplained | We use Fig. 8 as printed (D2). The NTPG is internally consistent, so the attack graph is not a gap. |
| F8 | Hosts 2 and 3 are identical in Table 2 and symmetric in Fig. 8: the same in-edges, a 0.8 edge each way, the same out-edges. Yet one decoy behind host 2 catches 0.337 of attacks and one behind host 3 only 0.105. | F3 numbers | The attacker separates them through something the paper does not publish: different interestingness I, or argmax ties broken in index order (host 2 = H4 comes first). This constrains the calibration (D3-D6). |

Paper's main claim against its own baselines: Q-learning at 30000 steps (0.804) minus the best static policy
(policy 2, mean 0.759) = 4.46 points. Fig. 10's own spread gives that difference a standard error of about 1.5-2
points (1.5 with F1's pooled spread, 2.0 with policy 2's own four values), before allowing for picking the best of
21. So the paper's numbers support the claim, but only modestly. It is the primary target
`CLAIM.Q_minus_best_static`.

## 3. Gaps and choices

Status: **D1-D22 and Section 4 committed 2026-11-28 with the simulator, before any run of it.** "Calibrate" means the setting is unpublished and Fig. 10 must decide it. Its grid
and the calibration protocol (Section 4) are committed before any run.

| # | gap | choice | why | decided on |
|---|---|---|---|---|
| D1 | which node is deployment location 1-7 | Table 2 order: 1 web server, 2 pad, 3 host 1, 4 host 2, 5 host 3, 6 file server, 7 data server | Table 2 numbers H1-H7; the state is a 7-vector; F3 confirms that 7 = data server | 2026-11-20 |
| D2 | the attack graph | Fig. 8 as printed (`data/ntpg.json`), including the four USB edges' direction | it is the graph the method uses (Alg. 1 line 1); F7 | 2026-11-20 |
| D3 | static policy numbering | lexicographic pairs (1,2), (1,3), ..., (6,7) | the text: policy 1 = "first and second deployment locations"; F3's block structure fits | 2026-11-20 |
| D4 | J(n), the attacker's success probability | J(n) = the best Fig. 8 edge into n from the Internet or any compromised node (D15); **calibrated** between UP and RP (Section 4 grid) | Eq. 1 names J and CVSS, but not which privilege; Table 2 shows user privilege suffices to move on (all "required privilege: User") | 2026-11-28 (grid) |
| D5 | interestingness I(n) and the weights alpha, beta | **calibrated** over the declared family of D17 and alpha in {0.2, 0.5, 0.8}, beta = 1 - alpha (Section 4); never node-by-node free values | not published at all; F8 shows I (or tie-breaking) must separate hosts 2 and 3 | 2026-11-28 (grid) |
| D6 | a decoy's I and J | J: D16. I: **calibrated** between "same as the data server" and "same as the node it sits behind" | the paper: a decoy "is the same as n_cr" apart from fake data, and its location changes I(decoy) but not J(decoy) | 2026-11-28 (grid) |
| D7 | argmax ties and failed exploits | ties in Eq. 1: **calibrated** between index order (D18) and random. A failed exploit leaves the attacker where it is, and it chooses again next step. | not stated; F8 | 2026-11-28 (grid) |
| D8 | episode length ("after a limited number of attack actions") | 20 attack actions, then the episode counts as a failed defence (D19). Fixed: the share of experiments that reach the limit is logged for every trial and does not change the limit | the longest simple path to the data server has 6 edges; the limit must not bind except when the attacker keeps failing | 2026-11-20 |
| D9 | alarm model | each step, a compromised location raises an alarm with probability 1 - FNR, an uncompromised one with probability FPR, independently | the plainest reading of Section II.B and Fig. 3 | 2026-11-20 |
| D10 | following-alarm when the alarmed set does not hold exactly 2 locations | 2 or more alarms: 2 distinct random alarmed locations. 1 alarm: that one plus a random other. 0 alarms: a random element of AD | Eq. 5 picks from AL; two decoys must be placed one-to-one | 2026-11-20 |
| D11 | random-dynamic | reading (b): one random sequence A_t per repeat, used for all 1000 attacks; reading (a) reported too | F2 | 2026-11-20 |
| D12 | Q-learning settings | gamma = 0.9 and epsilon = 0.1, fixed (not tuned: Fig. 13 stays held out); ties at random (F5); a training step = one defender decision (Alg. 1 line 5), episodes restart from s0; the dsp at x steps = the greedy policy over 1000 new experiments | gamma and epsilon not published; common textbook values, declared before any run | 2026-11-20 |
| D13 | when the defender acts | before each attack action, the defender sees the alarms S_t and places both decoys; the attacker then chooses among the nodes reachable from its compromised set, which includes any decoy placed behind one of them | Eq. 2 and Section IV.A: an action at every time t | 2026-11-20 |
| D14 | variance | 10 seeds; each evaluation is 1000 experiments (Table 3) | STANDARD.md requirement 5 | 2026-11-20 |
| D15 | how J is used | J(n) is computed from the attacker's current footholds (the Internet and every compromised node) and is both the J of Eq. 1 and the probability that the attack action on n succeeds | Sec. II.B: "J(n_i) denote[s] the probability that the attacker invades n_i successfully" | 2026-11-28 |
| D16 | a decoy's J | J(decoy) = the data server's best incoming edge under the same reading: 0.8 (UP) or 0.6 (RP), wherever the decoy is | "its location will not affect the attacker's success probability J(n_fr)"; a decoy "is the same as n_cr" | 2026-11-28 |
| D17 | the family of attacker readings (choice rule and I) | Choice rule: **argmax** (Eq. 1) or **proportional** (P(n) proportional to alpha I(n) + beta J(n)). I: **uniform** (1 for every node); **role** (web, file and data server 1; pad and hosts 0.5); **outdegree** (out-degree in Fig. 8 divided by the largest: web 0.5, pad 1, host 1 1, hosts 2-3 0.75, file 0.25, data 0); **random** (I(n) ~ U(0,1) for every node, drawn once per experiment). | argmax: Eq. 1. Proportional: Sec. II.B defines p_n, "the probability that attacker invades n_i in the next step", which grows with I and J. Role: I "is related to the nature of the nodes" (0.5 is our choice). Outdegree: "... the network topology". Random: "the attacker's strategy is expressed by the attacker's interestingness distribution" (Sec. V), read as a population of attackers. | 2026-11-28 |
| D18 | order for index ties | real nodes in Table 2 order (locations 1-7), then decoys in the order of the location they sit behind | Table 2 numbering; decoys are added after the scan | 2026-11-28 |
| D19 | the step limit in training | reaching the limit is S_fail: reward -1 (Eq. 10) and a failed defence in dsp | the attacker has not been trapped | 2026-11-28 |
| D20 | Eq. 15 vs Algorithm 1 | learning rate 1 / (1 + visits) where visits includes the current update (first update 1/2), as Eq. 15 states; Algorithm 1 increments the count after the update, which would give 1 at the first update | Eq. 15 is explicit ("including the nth cycle") | 2026-11-28 |
| D21 | prior exposure | Before this grid was written, one reading was worked out by hand while designing (argmax, UP, uniform I, random ties: one decoy behind the web server would trap about 50%). No reading was simulated before the commit of the grid and the code. The family comes from the text (D17), not from that check. | honesty about the order | 2026-11-28 |
| D22 | machine | development PC, CPU, pure Python (`random`, no NumPy), worker processes; each evaluation has its own seed from its labels (`seed_of`), so the worker count changes nothing | STANDARD.md requirement 7 | 2026-11-28 |

## 4. Calibration and held-out targets (committed 2026-11-28, before any run)

Code: `wang_env.py` (simulator), `run.py` (stages `calibrate`, `heldout`, `report`), `tests/` (rules).

1. **Calibration targets:** the 21 static-policy means `F10.P01`-`F10.P21` (and `F10.best_text`, a point of the
   same figure). Verdict: CALIBRATION TARGET, with the distance reached. Static policies read no alarms and learn
   nothing, so they fix the attacker (D4-D7) without touching the alarm model or the learner.
2. **Grid (144 readings, `run.py` GRID):** choice {argmax, proportional} x J {UP, RP} x I {uniform, role,
   outdegree, random} x decoy I {data, location} x alpha {0.2, 0.5, 0.8} (beta = 1 - alpha) x ties {index,
   random} (argmax only). Some readings coincide (for example alpha does not matter under argmax with uniform I);
   they are run anyway and all are logged.
3. **One trial = one reading:** 21 static policies x 4 settings x 1000 experiments, each evaluation with its own
   seed. Our value per policy = the mean of the 4 settings; loss = RMSE over the 21 policies, in points.
4. **Selection:** the lowest RMSE; an exact tie goes to the earlier trial. One round only: no reading is added
   after the log is seen (that would be a new, dated protocol version, reported as such).
5. **Adequacy:** the calibration is adequate if the best RMSE is at most 5 points (about 3 times the noise of
   Fig. 10's own means, ~1.5 points, F1). The constant predictor (the standard deviation of the 21 published
   means) is reported as the null fit. If it is not adequate, the held-out targets are still computed once and
   reported, and the paper is "not calibrated-replicated".
6. **Then commit** `out/CALIBRATION.json` and `out/calibration_log.csv`. `heldout` refuses to run before that,
   and refuses to run twice.
7. **Held-out, computed once, 10 seeds, the selected reading:** the 21 static policies again (new seeds; the
   distances of step 1 are reported from these); following-alarm, 10 repeats x 1000 experiments per setting
   (`F12.FA.S1`-`S4`); random-dynamic reading (b), 10 repeats per setting, the mean of the 40 (`F11.RD_mean`),
   and reading (a) as a sensitivity; Q-learning trained separately per setting, greedy evaluation on 1000 new
   experiments at 0, 500, 1000, 2000, 5000, 10000, 20000 and 30000 steps (`F13.*`); the claim
   (`CLAIM.Q_minus_best_static`) = Q at 30000 minus the best static policy (the policy with the highest mean in
   our environment), per seed.
8. **Verdicts:** as `TARGETS.csv`: MATCH if the published value is inside our 95% CI (t, 10 seeds), CLOSE if our
   mean is within 2 points, else NO MATCH.
9. **Informativeness (STANDARD.md 3a), checked first:** reference policies = the best static policy,
   following-alarm, random-dynamic (b) and the untrained Q-learner, in our calibrated environment; a policy is
   not its own reference; per-setting targets use the references at that setting; for the claim the references
   are 0 and each reference minus the best static policy. If any reference is within 2 points of the published
   value, the target is UNINFORMATIVE (numbers still reported).
10. **Paper verdict:** calibrated-replicated only if the calibration is adequate and every informative primary
    held-out target (`F13.Q_30000_mean`, `CLAIM.Q_minus_best_static`) is MATCH or CLOSE; otherwise "not
    calibrated-replicated", naming the targets; if no primary target is informative, "uninformative".
11. **Logging:** every trial and every number in `out/calibration_log.csv`; held-out raw values in
    `out/heldout.json`; `REPORT.md` is written by `run.py report`. `F14.time_30000` is NOT ATTEMPTED (F6).
