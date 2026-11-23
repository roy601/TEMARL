# Implementation assumptions — scientific disclosure

The published abstract confirms the qualitative architecture and selected quantitative results. The exact published implementation was not supplied. The following are therefore **independent hypotheses and arbitrary-but-explicit experimental choices**, not author-derived constants:

| Design element | This project | Status |
|---|---|---|
| Graph | 25-node six-role connected ring/bridge topology | Assumed |
| Node categories | Workstation (8), server (5), DB (4), admin (3), DMZ (3), app (2) | Assumed |
| Latent attacker model | 11 ordered MITRE-like tactic stages | Confirmed count; names/ordering assumed |
| Transition | Stage self 0.40, next 0.40, skip 0.15, restart 0.05 | Assumed |
| Emissions | True stage .70 + neighboring stages .10 each + uniform .10 | Assumed |
| Role-node visit prior | Per-stage role probabilities in `ROLE_STAGE` | Assumed |
| Next-node generator | 60% stage role, 30% neighbors, 10% uniform | Assumed |
| HMM node evidence | Stage-specific synthetic role-node prior | Assumed |
| Policy objective weights | Five distinct weight vectors | Assumed |
| Mode scheduling | Rotates every 8 observations | Assumed |
| Fractional feedback | 1 on hit; 0.20 immediate neighbor; 0 otherwise | Assumed |
| Posterior decay | `alpha=1+(alpha-1)*exp(-1.8*belief_shift)`; analogous beta | Assumed |
| Attacker adaptation | None (pre-generated fixed trajectory) | Matches replay concept; parameters assumed |
| Evaluation topology | 25 nodes, 4 decoys | Publication abstract |
| Replay seeds | 50 development + 50 disjoint heldout by default | 50-seed comparison grounded; specific seed IDs and extra holdout ours |
| Replay horizon | 80 events = 79 scored placements | Assumed |
| Hit metric | Next target is one of four selected nodes | Consistent with abstract; full exact paper definition unverified |
| Published reference | BAAHS 25.89%, strongest baseline 15.32% | Publication abstract |
| Baselines | Seven simplified implementations | Inspired by classes, not faithful author code |

## Reproduction risks

- Shared synthetic simulator and HMM likelihoods are **coupled**; HMM-style methods can be advantaged.
- No operational attacker can react to deception in the fixed replay.
- The strongest baseline in this project may be a **different method** than the strongest principal comparison baseline in the publication.
- The matched aggregates, if they occur, may reflect coincidental hit rates or stopping bias.
- Paper figures/tables cannot be recreated without access to their exact experiment definitions and inputs.
- The `--repeat-until-match` flag is **exploratory**; a first match is not an inferential success and cannot be used as a formal paper-reproduction claim.
