# Author contact log

Every gap in `DECISIONS.md` is asked here. Replies are quoted, not paraphrased.

| date | to | question (gap #) | reply or "no reply after N days" |
|---|---|---|---|
| (draft, not sent) | the corresponding author (address from the published PDF) | the missing `README.md` (3); whether Table 4 was computed from the archived held-out episodes (6) | - |

## Draft email (for the user to send, or not)

Subject: CADO (Future Internet 18(10), 552): two questions about Supplementary Material S1

Dear Dr. <corresponding author>,

We are reproducing the results of your paper "CADO: Constraint-Aware Alert-to-Deception Orchestration
for Heterogeneous Security Controls" from Supplementary Material S1, and thank you for releasing the
simulator and analysis code. Two questions:

1. `SHA256SUMS.txt` lists a `README.md` that is not in the S1 archive. Could you share it?
2. `code/revision_analysis.py` computes the held-out statistics of Table 4 from the archived
   `submitted_results/ood_episode_metrics.csv`. Were the printed Table 4 values computed from those
   archived episodes, and is a fresh run of `code/reproduce_submitted.py` expected to give the same
   episodes on any machine?

Thank you for your time.
