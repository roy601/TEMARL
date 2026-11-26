# Decisions

Written 2026-11-26, after reading the final IEEE PDF in full, before any code that models the honeypot or
the attacker. Nothing has been run except `checks/check_paper.py`, which only does arithmetic on printed
numbers and exercises Algorithm 1 as printed (no reproduction result).

## Status: not reproducible as published

| # | gap | choice | why | decided on |
|---|---|---|---|---|
| 1 | What decides the results | **No target is attempted now.** Every result (Figs. 6-11, Table 6, the text numbers) comes from one closed loop: Conpot patched by the authors, an LLM mapper (ChatGPT-4o-mini with an unpublished prompt), and **scripted Metasploit/Python attacks whose reaction to each deception action** (continue, repeat, advance, disconnect) produces the depth, duration and reward. None of the three is released, and the paper never says how a scripted attack reacts to Delay, Modify, Restore, System Error or Jitter. A rebuild would have to invent that reaction, and the invented attacker would decide every number. | STANDARD.md Section 1: a replication must follow the paper; here the decisive component is not in the paper | 2026-11-26 |
| 2 | Calibrated replication (STANDARD 3a) | **Not done.** In Li 2025 a calibrated replication with 8 declared readings found 0 of 256 that fit; here the attacker model is completely free (12 tactics x 7 actions x continue/stay/advance/disconnect probabilities), so a fit could be made to almost any curve and would show nothing about the method. | lesson from `../li2025_drdppo/` (devil's-advocate STOP on knob search) | 2026-11-26 |
| 3 | Pre-registration | The 115 targets (7 primary) are recorded anyway (`make_targets.py`: the text numbers and the 84 Table 6 values), so a later run with the authors' materials is bound to them. Figures 6-11 are raster images; no value is read off a figure. | STANDARD.md requirement 1 | 2026-11-26 |
| 4 | Seeds | If the authors' materials arrive: **10 training seeds** per configuration, 95% CI over seeds (the tolerances in TARGETS.csv). The paper reports one run per configuration. | STANDARD.md requirement 5 | 2026-11-26 |
| 5 | Use in the thesis | Lin's **Algorithm 1** is fully specified as a learner (state = tactic, 7 actions, reward, alpha, gamma, epsilon schedule), so it can be an adapted baseline arm in **our** environment. That is a comparison, not a reproduction, and needs its own protocol (STANDARD requirement 10), written and frozen only on the user's word. Findings C1-C3 below must then be handled explicitly (we would implement Algorithm 1 as printed and say so). | separation of reproduction and comparison | 2026-11-26 |

## Gaps to settle with the authors before any run (none decided)

6. The attack scripts: the MITRE Campaign workflows used (2015 Ukraine only, or also C0025/C0034), their commands, and how each script branches on the honeypot's response (when it repeats, advances, or disconnects).
7. The Conpot patch for Static1 and the Dynamic proxy: Sec. V-B describes Static1 as "extended Modbus handler, custom register mappings, extended address ranges", Sec. VI-A as "Conpot with simple boundary checks".
8. The mapper: the prompt, the model version and temperature, and the 120 synthetic validation cases (Sec. IV-C, >95%).
9. Tactic indexing: Table 6 lists 12 tactics with Impact as tau_T, Fig. 6 says the y-axis ranges 1-12, but Fig. 8 stops at 11 and calls 11 the "final tactic". Whether indices run 0-11 or 1-12, and which tactic Static0's "4" and Static1's "7" are.
10. Which configuration produced Table 6, Fig. 8 and Fig. 9 (small or big state; stable or fast profile; Fig. 10 marks the fast profile "ours", Sec. VI-A gives the stable one as the default).
11. The big state: the protocol and function-code values and how they enter the Q-table key (Algorithm 1 indexes Q by tactic only).
12. The TD-error schedule: the "moving threshold" and the window of the running average.
13. Session timing: how 800 sessions fit in 12 minutes when one session lasts 17-70 s (C6); whether sessions ran in parallel.
14. Number of runs and seeds per curve; the smoothing window of Figs. 6, 7, 9.

## Internal-consistency findings (from the published text and Table 6 only; `checks/CHECKS.txt`)

| # | finding | kind |
|---|---|---|
| C1 | Table 6 has **14 negative Q-values** (all 12 Block entries, Persistence/System Error -2.12, Impact/Allow -4.99). Under Algorithm 1 as printed no Q-value can be negative: the -5 penalty is set (line 13) and the loop breaks (line 14) before the update, every other reward is >= 1, and Q starts at 0, so every update is a convex combination of non-negative numbers. | proof |
| C2 | Table 6's **Impact row** (tau_T) is non-zero. In Algorithm 1 the loop stops as soon as t' = tau_T (lines 4, 29), so Q[tau_T, .] is never updated and stays 0. | proof |
| C3 | Even if the penalty **were** applied (not Algorithm 1): a penalty ends its session, so there are at most 2000 penalties (1200 in Sec. VII). Below -3.5 only penalty updates can lower a cell (other targets are >= 1 + 0.9 x (-5) = -3.5). With alpha = 1e-4 the cells below -3.5 need at least 228,075 penalty updates; even with alpha = 1e-3, the largest value in the grid, at least 22,802. Table 6 is inconsistent with every learning rate in the paper. | proof (bound) |
| C4 | The text says tactics 6-9 "increasingly favor Modify" and later stages "shift toward Delay and Jitter"; in Table 6 the largest value in each of tactics 6-11 is **Allow**. Modify is best only in Privilege escalation, Restore only in Impact. | text vs table |
| C5 | Epsilon is reset to 0.8 at the start of **every episode** (line 3) and decays per step: it reaches 0.01 after 85 steps (rho 0.95) or 436 steps (rho 0.99), a ratio of 5.1. The text says rho 0.99 explores for "roughly twice as many episodes"; with the reset, exploration does not carry across episodes. | text vs algorithm |
| C6 | "Tactic 10 within 800 episodes (approximately 12 minutes)" is 0.9 s per session, "300 episodes (around 4 minutes)" 0.8 s, "first 400 sessions ... initial five minutes" 0.75 s; but one session lasts 17-70 s (Fig. 7), so 800 consecutive sessions take 3.8-15.6 hours. | text vs text |
| C7 | Session counts differ: 2000 consecutive sessions (Sec. VI-B, Fig. 6), 1200 (Fig. 8, Sec. VII), 1000 (Figs. 7, 9-11), "700 attack-response cycles" (abstract). | text vs text |
| C8 | The abstract says "more than doubles the average engagement time", Secs. VI-B and VII the **median**; Fig. 7 shows moving averages only: > 70 s vs Static1 about 40 s is 1.75x (4.1x vs Static0). | text vs figure |
| C9 | Fig. 7: the RL curve starts near 5 s, below Static0 (17 s), but the text says it "begins with comparable session lengths". | text vs figure |

What C1-C3 mean: the Q-table in Table 6 was produced by code that differs from Algorithm 1 (penalty applied,
tau_T treated as a normal state) and, given C3, by more updates or a larger learning rate than stated. This
does not show the method fails; it shows the published description is not the code that produced Table 6.
