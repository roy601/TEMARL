# Author contact log

All messages are sent by the user (not by Claude), from the user's official BRAC University address.

| date | to | question | reply or "no reply after N days" |
|---|---|---|---|
| (not sent yet) | Didik Sudyana, didik@gs.ncku.edu.tw (corresponding author as marked in the PDF) | A below | - |

## A. Draft

> Subject: Request for materials: "Reinforcement Learning-Driven Honeypots: Tactic-Based Defense for ICS" (IEEE TMLCN 2026)
>
> Dear Dr. Sudyana,
>
> I am a final-year student at BRAC University (Bangladesh) and I am trying to reproduce your IEEE TMLCN
> 2026 paper with Prof. Lin, Mr. Mankaev, Prof. Lai and Prof. Hwang. Your paper describes the method very
> clearly, but I cannot rebuild the results without a few materials. If possible, could you share:
>
> 1. the attack scripts (Metasploit/Python) and how each one reacts to the honeypot's responses (when it
>    repeats a command, moves to the next tactic, or disconnects);
> 2. the Conpot changes for Static1 and the Dynamic proxy, the YAML configuration, and the Q-learning code;
> 3. the mapper prompt, the model version, and the 120 synthetic validation cases;
> 4. the session logs or Q-table snapshots behind Table 6 and Figures 6-9, and which configuration
>    (small or big state; stable or fast profile) produced them.
>
> I also have three short questions, so that I implement Algorithm 1 correctly:
>
> (a) In Algorithm 1 the loop breaks right after r = -5 (lines 13-14), before the Q-update, so no Q-value
>     could become negative; Table 6 has negative values (for example Block). Is the penalty applied in
>     the update in your code?
> (b) Table 6 has values for Impact, but the loop ends when Impact is reached, so that row would stay 0.
>     Is Impact treated as a normal state in your code?
> (c) Section VI-D says 800 episodes take about 12 minutes, but Fig. 7 shows sessions of 17-70 seconds.
>     Did the sessions run in parallel?
>
> Thank you very much for your time.
>
> Name: [your name]; supervisor: [name]
