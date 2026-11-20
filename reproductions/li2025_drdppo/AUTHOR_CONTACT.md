# Author contact log

All messages are sent by the user (not by Claude). Corresponding author: Hao Wu, hwu@bjtu.edu.cn (p. 1, and
"Correspondence and requests for materials should be addressed to H.W.").

| date | to | question | reply or "no reply after N days" |
|---|---|---|---|
| (not sent yet) | Hao Wu (hwu@bjtu.edu.cn) | the draft below (decisions 4-12) | - |

## Draft (for the user to send)

Subject: Reproducing "Multiple deception resources deployment strategy based on reinforcement learning" (Sci Rep 2025)

Dear Prof. Wu,

I am a final-year student at BRAC University replicating your Scientific Reports 2025 paper (DRD-PPO) as a
baseline for my thesis. I could not find released code, and a few settings are not stated in the paper. Could you
tell me:

1. The value of the weight w in Eq. (2).
2. The host-server communication relationships (L1) of the experimental network: which hosts communicate with
   which servers? Fig. 3 shows the physical topology only.
3. Which CVSS version (v2 or v3) gives VC, VI and VA, and how F-honeypots are scored in Eq. (2).
4. The reward values R1 and R2, and when the attacker attacks within an episode (every step or at the end).
5. How states and actions are encoded for the networks (action space size), and the critic architecture.
6. The clip factor: 0.2 (text) or 0.9 (Table 2)? And the GAE lambda, number of update epochs and minibatch size.
7. Whether the DSP of Tables 3 and 4 is the success rate over the training episodes (500 and 1500) or over
   separate evaluation runs, and how many random seeds were used.
8. The settings of the six other RL algorithms in Table 4.

If code or configuration files are available, they would answer all of these. Thank you for your time.

Kind regards,
Apurba Roy
