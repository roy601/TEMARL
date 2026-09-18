# TEMARL v7 — a genuinely multi-agent, proposal-faithful deception experiment

This folder is a **new, additive experiment**. Nothing in `thesis_system/` or
`temarl_comiset/` is modified. The frozen inputs it reuses are the D3FEND payoff,
the vocabulary, the v5 chain estimator, the encoders and the GMU trunk. It imports
them from `thesis_system/temarl_v2` through `_frozen.py`, which refuses to run if
any of them has changed. The check uses sha256 with line endings normalised.

## 1. Why v7 exists

An audit of the v5 system found that it was a multi-agent *environment* but not
multi-agent *reinforcement learning*:

| Finding | Evidence |
|---|---|
| The reported policy is behaviour cloning on a privileged oracle, not RL | `run_v5.py:83-117`; under PPO no arm beat the fixed-decoy baseline (`results_v5/ppo_ab.log`) |
| Only the responsible agent's action affects reward, capture or progress, so the team problem decomposes into independent single-agent problems | `env_entity.py:237-246` |
| All four agents are trained toward the same label, with no mixer, no communication and no credit assignment | `run_v5.py:100-102` |
| The decoy-target (pointer) head is never trained under behaviour cloning, so placement in regimes C/D came from an untrained head | `run_v5.py:107-108` (loss on type logits only), `train_entity.py:174` |
| Under containment, the proposal's primary metric runs backwards: dwell time falls as the defence improves | `results_v5/baselines_v5.json`: null policy 21.7 steps, clairvoyant 14.0 |

The proposal promised multi-agent RL, with dwell time, interaction depth and
generalisation to an unseen attack script as its primary metrics. v7 is built to
test exactly that.

## 2. The environment (`env_marl.py`)

The setting is the canonical CAM-LDS 5-zone star: the Internet entry zone and
four defended zones (DMZ, LAN, User, Admin). There are **four agents, one per
defended zone**. Each chooses a D3FEND decoy type every step, or none. As in
v2/v5, actions are chosen *before* the attacker moves, so agents must anticipate
both where it goes and what it does.

### 2.1 Engagement, not containment

A deceived attacker is not removed. It keeps executing its playbook against the
decoy, and every such step is an **interaction step**. The episode return is
therefore the proposal's **dwell time**, and deception lengthens it. The episode
ends when:

- the attacker reaches its objective, or
- the playbook is exhausted.

### 2.2 Three couplings that make the problem multi-agent

| Coupling | Rule | Why it forces coordination | Grounding |
|---|---|---|---|
| **Capacity** (substitutes) | At most K = 2 decoys run at full fidelity. With more, each runs at φ = K/n_active | One agent deploying makes the others' deployments worth less, so the team must allocate | Resource contention makes honeypots slow and fingerprintable (Holz & Raynal 2005; Fu et al. 2006) |
| **Breadcrumbs** (complements) | D3-DUC (credential) and D3-DF (file) are breadcrumbs. When one is engaged, the attacker follows it to an active decoy in *another* zone. With no partner it is a dead end, carrying exposure risk β | A breadcrumb is worthless alone and valuable only with a partner decoy | Honeytokens (Spitzner 2003); D3FEND Decoy User Credential / Decoy File |
| **Shared exposure** (externality) | An engaged decoy exposes the deception with probability β(1 − ρ). After exposure, *every* decoy is ignored | One agent's unrealistic decoy destroys all agents' future engagement | — |

Engagement probability is ρ = φ · PAYOFF[τ, d], using the **frozen D3FEND
payoff**, never refitted.

### 2.3 Observations (decentralised execution)

Each agent sees only:

- its own zone: whether the attacker is present, and the technique it just executed if so
- its own decoy, and whether it was engaged
- two infrastructure signals: the previous step's load n_active/K, and a honeytoken alert that a breadcrumb now points at its decoy
- the step counter
- the shared **SIEM intent embedding h**, computed by the arm's history encoder from the techniques executed so far

`h` is a disclosed *shared channel*, because a SOC SIEM aggregates every zone's
alerts. The NoHistory arm (h = 0) measures what that channel is worth.
`tests_marl.py` proves that an agent's observation is invariant to every other
zone's private state.

### 2.4 The attacker, per real script (`scripts_marl.py`)

| Decision (fixed before any v7 result) | Reason |
|---|---|
| One Markov chain per CAM-LDS script (S1–S7), estimated by the **unchanged v5 estimator** (bit-exact check against `profiles_v5`) | Generalisation to an unseen script requires holding scripts out one at a time |
| Input: the 36 **source-verified AttackBed runs**, not the paper reconstruction | The reconstruction drops `<variant>` placeholders. They contain S1's persistence steps, so S1's goal tactic never occurred in its chain |
| Entry and target zones come from `camlds_grounding.json`. A non-defended target (S4 → Firewall) maps to the entry zone | Real geography per script |
| Goal tactic is the declared terminal tactic. If it never occurs in the runs and it is Exfiltration, Collection is used instead | Fires for S6 only: "keylog / collect and exfiltrate credentials", with keylogging and clipboard collection in every run and no separate exfiltration step |
| Horizon: a real run length of the script (5 steps for S5, up to 61 for S6) | A playbook has a fixed number of actions |
| Objective: the first goal-tactic technique on a real host in the target zone (G = 1) | With real horizons a fixed G = 3 would be unreachable for S7, which has only 2 goal steps per run |

The technique sequence is exogenous and is drawn with every other random quantity
up front (`EpisodeSpec`). All arms therefore face identical attacks (common random
numbers), and every comparison is paired.

## 3. Instrument validation before any learning

### 3.1 Reference ladder (`baselines_marl.py`)

The ladder contains no neural network:

- null
- random
- best fixed joint action (all 6⁴ tuples searched)
- uncoordinated reactive
- belief planners at five information levels (clairvoyant / transition / script / bigram / nointent), each coordinated or uncoordinated

### 3.2 Gates (`gates_marl.py`)

The thresholds were written before any ladder number existed:

| Gate | Requirement |
|---|---|
| G1 discrimination | null < random < best-fixed < ceiling; headroom ≥ 1 step and ≥ 25% of the ceiling |
| **G2 coordination** (the MARL test) | coordinated − best uncoordinated ≥ 15% of the ceiling; a partnered breadcrumb beats an unpartnered one; exceeding capacity hurts |
| G3 intent value | knowing the script ≥ 10% of the ceiling |
| G4 sequence value | script + current technique vs script alone ≥ 3% of the ceiling. If this fails, the architecture contrasts are declared uninterpretable in advance |
| G5 LOSO | every held-out script has measurable headroom |

### 3.3 Calibration (`calibrate_marl.py`)

- **Grid:** β × p_goal × p_stay, 8 cells, scored only by G1–G4.
- **Result:** 3 of 8 cells passed.
- **Selection:** the pre-declared rule takes the passing cell with the **smallest** coordination value: **β = 0.2, p_goal = 0.7, p_stay = 0.8**.
- **Disclosure:** that cell's G3 was a marginal pass on the calibration stream (10.1% against 10%).
- **Re-run:** the final gates were re-run on a **disjoint** episode stream (`results_marl/gates.json`).

## 4. Learner (`mappo.py`)

**MAPPO** (Yu et al. 2022) uses centralised training with decentralised execution:

- **Actor:** decentralised and parameter-shared, with the agent id in its input. It uses the project's GMU trunk (Arevalo et al. 2017) followed by a categorical head.
- **Critic:** centralised, V(global state, h, agent id), used only in training.
- **Hyperparameters:** the paper's recommendations, *identical for every arm*: value normalisation, clip 0.2, one mini-batch, 10 epochs, entropy 0.01, Huber loss, grad-norm 10, lr 5e-4, γ 0.99, λ 0.95.
- **IPPO** (de Witt et al. 2020) is the ablation: the same actor with a local critic.

History encoders are pretrained on next-technique prediction with the COMISET
recipe, then **frozen**. They are capacity-matched to the Transformer's trunk
within +0.3% (67,072 parameters).

The **learning gate** (`learning_gate_marl.py`) uses seeds 900–902. It chooses
the budget: the first of 1M / 2M / 4M environment steps at which MAPPO beats the
best fixed action and the uncoordinated reactive defender on every seed,
capturing ≥ 50% of the headroom. There is no fallback to behaviour cloning.

The approved plan ran this gate on the GRU, so that the budget could not suit
the arm under test. Before it ran, the author directed that it run on the
**Transformer-RoPE** arm, with GRU and LSTM trained later. This is disclosed. To
guard against other arms being under-trained at a Transformer-sized budget, a
**convergence flag** was pre-registered at the same time
(`prereg_marl.CONVERGENCE_RISE_REL`). An arm whose validation dwell is still
rising at the end of training has its contrasts labelled *budget-limited*,
not interpreted.

## 5. Pre-registration (`prereg_marl.py`)

The pre-registration is committed before the confirmatory runs.

- **Main family:** 6 arms × 10 seeds × 500 paired test episodes.
- **Contrasts:** M1 (MAPPO vs IPPO), I1 (vs NoHistory) and A1–A3 (Transformer vs GRU, LSTM, Set), each on dwell *and* depth, with Holm correction.
- **LOSO family:** 4 arms × 7 folds × 5 seeds, with contrasts L1–L3.
- **Tests and reporting:** all tests two-sided with direction-aware verdicts, TOST for nulls, and every contrast reported.

## 6. What v7 cannot claim

- The environment mechanics are **designed, not measured**. The free parameters were fixed only by the architecture-blind calibration, and the calibration grid is reported in full.
- `h` is centralised information, and this is disclosed.
- MARL was expected, before any run, **not** to make the Transformer more likely to win.

## References

- Arevalo, J. et al. (2017). Gated Multimodal Units for Information Fusion. ICLR Workshop, arXiv:1702.01992.
- de Witt, C. S. et al. (2020). Is Independent Learning All You Need in the StarCraft Multi-Agent Challenge? arXiv:2011.09533.
- Fu, X. et al. (2006). On Recognizing Virtual Honeypots and Countermeasures. IEEE DASC.
- Holz, T. & Raynal, F. (2005). Detecting Honeypots and Other Suspicious Environments. IEEE IAW.
- Kaloroumakis, P. E. & Smith, M. J. (2021). Toward a Knowledge Graph of Cybersecurity Countermeasures (MITRE D3FEND).
- Kiekintveld, C., Lisý, V. & Píbil, R. (2015). Game-Theoretic Foundations for the Strategic Use of Honeypots in Network Security. In *Cyber Warfare*, Springer.
- Oliehoek, F. A. & Amato, C. (2016). A Concise Introduction to Decentralized POMDPs. Springer.
- Spitzner, L. (2003). Honeytokens: The Other Honeypot. SecurityFocus.
- TTCP CAGE Working Group (2024). CAGE Challenge 4: multi-agent autonomous cyber defence with decoys (CybORG).
- Yu, C. et al. (2022). The Surprising Effectiveness of PPO in Cooperative Multi-Agent Games. NeurIPS Datasets & Benchmarks.
