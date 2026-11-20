# Author contact

| date | to | question | reply |
|---|---|---|---|
| (draft, not sent) | Shuo Wang, corresponding author (address in the article) | see the draft below | - |

## Draft (for the user to send, or not)

Subject: Question on the simulation settings of "An Intelligent Deployment Policy for Deception Resources Based on Reinforcement Learning" (IEEE Access 2020)

Dear Dr. Wang,

We are rebuilding the simulation of your IEEE Access 2020 paper for a reproducibility study and would be grateful
for the settings that the paper does not state:

1. The attacker's interestingness I(n) for each node, the weights alpha and beta of Eq. (1), and whether J(n) is
   the user or the root probability of Fig. 8.
2. The interestingness and success probability of a decoy node, as a function of where it is deployed.
3. How ties in Eq. (1) are broken, and what the attacker does after a failed exploit.
4. The alarm model: is an alarm drawn at every step for every compromised node (with FNR) and every other node
   (with FPR)?
5. The episode length limit, gamma and epsilon of Algorithm 1, and what one "training step" in Figs. 13-14 is.
6. Was the random-dynamic policy drawn once per experiment (Fig. 11)? Did the static runs of Fig. 10 use 1000
   experiments per point in every FNR/FPR setting?
7. Is the code available?

Thank you for your time.
