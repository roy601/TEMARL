# Author contact log

Every gap in `DECISIONS.md` is asked here. Replies are quoted, not paraphrased.

| date | to | question (gap #) | reply or "no reply after N days" |
|---|---|---|---|
| (draft, not sent) | the authors, as an issue on github.com/adityavs14/Hierarchical-MARL | unreleased policies and red agents (3); how Red Impact Count combines red agents (7); evaluation seeds (8); the Table 2 / Table 3 difference for H-MARL Collective (11) | - |

## Draft issue (for the user to post, or not)

Title: Reproducing Tables 2 and 3 (RLJ 2025): four questions

Thank you for releasing the code and trained policies of "Hierarchical Multi-agent Reinforcement Learning for
Cyber Network Defense". We are reproducing Tables 2 and 3 with the policies at commit 6fe960f and CAGE 4 at
8c3c50c (Python 3.10, Ray 2.10.0). Four questions:

1. Could you release the policies of MARL Centralized Critic, H-MARL Collective and H-MARL Meta with
   fine-tuning, and the Stealthy, Aggressive and Impact red agents used in Table 2?
2. Table 3's Red Impact Count: is it the sum over red agents of the per-episode Impact counts on operational
   hosts printed by `evaluation_metrics.py`, averaged over episodes?
3. Which seeds were used for the 100 evaluation episodes (the evaluator's default is `seed=None`)?
4. H-MARL Collective against Default Red is -237.61 in Table 2 and -255.56 in Table 3. Were these two
   different evaluations?
