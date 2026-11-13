# What We Are Doing Now

We are running the complete TEMARL honeypot experiment using attack behaviour
learned from the CAM-LDS playbooks.

## What is being compared?

We are testing three models with two multi-agent learning methods:

| History model | IPPO | MAPPO |
|---|---:|---:|
| Transformer | Yes | Yes |
| GRU | Yes | Yes |
| LSTM | Yes | Yes |

- The history model reads the attack-technique sequence and summarizes the
  attacker's likely intent.
- IPPO trains each defender using local information.
- MAPPO trains the defenders with shared information during training so they
  can learn better teamwork.
- During operation, four defenders decide which honeypot or decoy action to
  use in the DMZ, LAN, User and Admin zones.

We also train models without attack-history information. These **NoIntent**
controls show whether intent prediction actually improves the defence.

## How is CAM-LDS used?

The verified CAM-LDS file contains 36 attack runs from 7 scenarios and 1,347
ATT&CK-labelled steps. The environment learns transition probabilities from
these runs and generates similar synthetic attack sequences during training.
It does not use raw network logs or replay every playbook exactly.

## What will we measure?

- **Dwell time:** how long the attacker remains engaged with decoys. Higher is
  better.
- **Interaction depth:** how many different attack techniques interact with
  decoys. Higher is better.
- **Asset protection:** how often the attacker fails to reach the protected
  objective. Higher is better.

## What will the final comparison show?

The experiment will report all six model combinations. It will then select the
best MAPPO history model using validation results and compare:

1. Selected model + IPPO
2. NoIntent + IPPO
3. Selected model + MAPPO

This tells us whether the history model helps and whether MAPPO teamwork is
better than IPPO.

## Current run

The complete study contains 80 training cells: 8 configurations across 10
random seeds. Each cell requests 2 million environment steps. On the lab RTX
4080 SUPER, the rough estimate is 1-3 days.

Do not close the terminal, turn off the PC, or allow it to sleep. If the run is
interrupted, the same command resumes from completed cells.

When finished, the readable result tables will be in:

```text
results/main/RESULTS.md
```

Files inside `results/smoke_gpu` are only short execution checks. They are not
the thesis results.
