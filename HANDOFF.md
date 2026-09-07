# TEMARL — Session Handoff

Paste this into a new session to resume with full context. Everything below is
verified against the code and result files, not recalled.

Last updated: 2026-09-02 · **corrections appended 2026-09-08**

> ## ⚠ THIS DOCUMENT PREDATES v4 AND v5 — read the corrections first
>
> Written after v3. Four of its claims have since been measured and found wrong,
> and are corrected inline below (each marked **[CORRECTED]**):
>
> | Claim here | Status |
> |---|---|
> | "81 techniques / 13 tactics matching Table 3 **exactly**" | **WITHDRAWN** — the parse yields 82; the match was an artefact of three parser bugs (Phase 1) |
> | "COMISET is **1156×** larger" | **MISLEADING** — 98.5% self-loops collapse 1.5M steps to 23,754 usable windows; the real advantage is **≈18×** |
> | "the Transformer has **never won**" | **TOO STRONG** — on DSR with the DeepSets encoder v3's history Transformer was nominally *ahead* (0.459 vs 0.439) |
> | "the hand reconstruction **invented** T1095" | **FALSE** — T1095 is real at `scenario_7.j2:95`; reconstruction precision is 100%, not 98.7% |
>
> **The current state of the project is not v3.** See, in order:
> - `thesis_system/temarl_v2/results_v4/VERDICT.md` — why the v4 null was
>   uninterpretable (the task could not reward sequence modelling; 5 of 6 arms
>   never beat a constant action)
> - `thesis_system/temarl_v2/results_v5/PHASE5_RESULT.md` — **the current
>   result**: on a repaired and validated instrument, all 8 pre-registered
>   contrasts null, with 5 of 5 arms passing the validity gate and the effect
>   bounded within ±0.007 DSR

---

## 1. Project

**TEMARL** — BRAC University B.Sc. thesis, *"Transformer-Enhanced Multi-Agent
Reinforcement Learning for Adaptive Honeypot Deception."*

- **Students:** Apurba Roy (23101012), Tushit Roy (23101350), Mark Dipto Gomes
  (23101537), Farjana Akter Shumi (23101059)
- **Supervisor:** Md. Sakir Hossain
- **Repo:** `https://github.com/roy601/TEMARL.git`, branch `main`
- **Code:** `thesis_system/temarl_v2/` — all scripts import siblings by bare
  name, so **every command must be run from that directory**
- **Environment:** Python 3.11.9, torch 2.4.1+cpu, numpy 2.4.6, scipy 1.17.1.
  CPU-only; one run was done on an RTX 4080 SUPER.

**What the system does.** Four defender agents place D3FEND decoys in a
segmented network while a scripted attacker (driven by CAM-LDS campaign
profiles) advances through MITRE ATT&CK techniques. A frozen intent encoder
reads the attacker's technique history into an embedding `h`; a GMU gate fuses
`h` with telemetry; QMIX mixes the agents. The headline metric is **DSR**
(Deception Success Rate = fraction of episodes where the attacker is contained).

---

## 2. Hard constraints — do not re-litigate these

1. **`env_v2.py` is the frozen scientific control.** Never modify it. v3 adds
   `env_entity.py` *alongside*, and must keep reproducing v2 exactly in
   canonical mode. Current status: **0 mismatches over 1,126 steps** across
   technique, zone, credited agent, alignment, capture probability, reward,
   termination and done-flag.
2. **`payoff_frozen.json` is never refitted.** It was *extended* 78 → 84 rows by
   the identical D3FEND rule and identical constants. Rows 0–77 were verified
   **bit-identical** (sum 132.6000, 0 mismatching cells) before the extension.
   Extension ≠ refit. Do not "re-tune to make a gate pass."
3. **Pre-registration lives in source** — `evaluate_v2.py` and `prereg_v3.py`.
   Hypotheses, primary metric, splits, seeds, contrast family and correction are
   fixed *before* running and are not edited afterwards. **Negative results are
   reported as results.**
4. **The vocabulary is append-only.** 78 → 84 techniques. Source verification
   against the AttackBed playbooks found 6 techniques the paper-based
   reconstruction had missed (T1069, T1218, T1518, T1572, T1614, T1615 —
   **6.20%** of CAM-LDS technique instances were silently falling to UNK). They
   were appended at ids **78–83** so ids 0–77 stay valid. Consequence:
   **checkpoints predating this (80-wide output heads) are unusable and must
   never be loaded.**
5. **CAM-LDS grounding is source-verified**, parsed from 36 AttackBed playbooks
   by `parse_attackbed.py` → `data/camlds_grounding_verified.json`.
   **[CORRECTED]** This originally read "81 parent techniques and 13 tactics,
   matching the CAM-LDS paper's Table 3 **exactly**." That match was an artefact
   of three parser defects found in Phase 1 by an independent second parser: a
   block-order bug (`tactics:` before `techniques:` emitted nothing) and two
   inline-`#`-comment bugs. Fixing them recovers 8 lost instances and yields
   **82** parent techniques against the paper's 81. **The "matches exactly"
   claim is withdrawn and must not be used as evidence of parse completeness.**
6. **COMISET is not redistributed** (licensing). The **entire v3 chain has zero
   COMISET dependency** — verified module by module.
7. **No hard-coded absolute paths.** Everything resolves relative to the module
   or comes from CLI arguments.

---

## 3. Key constants (verified by import, 2026-09-02)

```
vocab      NUM_TECHNIQUES=84  VOCAB_SIZE=86  PAD=84  UNK=85  MAX_SEQ_LEN=16
payoff     shape (84, 6)  sum 143.8500  (rows 0-77 sum 132.6000, frozen)
actions    null_response, decoy_network_resource, decoy_environment,
           decoy_credential, decoy_file, decoy_persona
env_v2     N_AGENTS=4  N_ZONES=5  GOAL_STEPS=5  TERMINAL_PENALTY=-0.50
           reward R = 0.30*r1 + 0.70*r2   (weights identical in both arms)
capture    p_min=0.030 p_max=0.160 k=7.0 ema=0.70 a_ref=0.3667
entity     ENTITY_FEAT_DIM=47  GLOBAL_FEAT_DIM=105
encoders   EntityTransformer 74,369 params | DeepSets 73,828 (0.7% apart)
```

---

## 4. File map (`thesis_system/temarl_v2/`)

**Shared foundation**
| File | Role |
|---|---|
| `vocab_v2.py` | Union vocabulary, append-only; sub-technique → parent mapping |
| `d3fend_payoff.py` | Payoff generated BY RULE from D3FEND — 4 constants replace 115 hand-authored cells; headroom gate |
| `payoff_frozen.json` | The frozen record (84×6). Extended, never refitted |
| `encoders.py` | **History** encoders: Transformer / GRU / SetEncoder, capacity-matched |
| `policy.py` | GMU trunk (Arevalo et al. 2017), AgentNet, IntentQMixer, IGM check |

**v2 — the control**
| File | Role |
|---|---|
| `env_v2.py` | **FROZEN CONTROL.** 5-zone Dec-POMDP deception env |
| `train_v2.py`, `run_all.py` | Two-stage training (pretrain+freeze, then policy) |
| `evaluate_v2.py` | Pre-registered H1–H5, Holm–Bonferroni, Cohen's *d* |
| `data_real.py` | COMISET + CAM-LDS loaders, session/scenario splits, baselines |
| `train_real.py` | COMISET encoder training (**needs COMISET**) |
| `parse_attackbed.py` | AttackBed playbooks → source-verified grounding |
| `train_camlds.py`, `camlds_protocols.py`, `camlds_ab_test.py` | CAM-LDS LOSO / 3-protocol bracket / paired A-B test |

**v3 — variable-topology entity system**
| File | Role |
|---|---|
| `prereg_v3.py` | **Pre-registration.** H6/H7/H8, splits, seeds, contrast family |
| `topology.py` | Deterministic topology generator + canonical (control) config |
| `env_entity.py` | Entity environment + `equivalence_report()` vs env_v2 |
| `entity_encoders.py` | **Network** encoders: EntityTransformer vs DeepSets |
| `policy_entity.py` | Fusion + factored (action_type, target_entity) head with masking |
| `train_entity.py` | 2×3 factorial training, 4-regime evaluation |
| `evaluate_entity.py` | Pre-registered Holm-corrected analysis |
| `analyze_by_size.py` | Per-zone-size breakdown from checkpoints |
| `tests_entity.py` | 26-test suite |
| `gates_v3.py` | Runs all 10 gate modules → `results_v3/gates.json` |

---

## 5. The environments — how each one is built

Two environments exist. **v2 is the frozen control; v3 is additive.** v3 must
keep reproducing v2 exactly on the canonical topology, and currently does
(0 mismatches / 1,126 steps).

### 5.1 v2 — `env_v2.DeceptionEnvV2` (fixed 5-zone)

**Topology is hard-coded**, mirroring the CAM-LDS testbed segmentation:

| Zone | id | Hosts | Defended by |
|---|---|---|---|
| Internet | 0 | CorpDNS, PublicDNS, Attacker | none (attacker home) |
| DMZ | 1 | DockerServer, RepositoryServer, VideoServer | agent 0 |
| LAN | 2 | FileShare, AdminLAN | agent 1 |
| User | 3 | Client | agent 2 |
| Admin | 4 | AdminHost | agent 3 |

Movement is a **star through a firewall hub**: from Internet the attacker may
enter any defended zone; from a defended zone it may reach any other. Note that
`ZONE_HOSTS` is declarative only — **v2's dynamics are zone-level; hosts play no
mechanical role at all.** That is precisely the limitation v3 removes.

**Per-step sequence** (this exact order matters — v3 must consume the random
stream identically or equivalence breaks):

1. Attacker emits a technique: `tau ~ T_c[tau_prev]`, a Markov chain of the
   hidden campaign profile `c`.
2. Attacker moves. From Internet, into any defended zone. Otherwise a 0.45 dwell
   test first, then a move weighted by `1 + 0.8 * compromised[z]`.
3. **Anticipatory credit (the key design choice):** the responsible agent is the
   owner of the zone the attacker moved *into*, and its action was chosen
   *before* the move — so it was blind if the attacker was elsewhere.
   Alignment `= PAYOFF[tau, action]`.
4. **Containment is alignment-driven**, not fixed:
   `ema = 0.70*ema + 0.30*align`, then
   `p_cap = 0.030 + 0.130 * sigmoid(7.0 * (ema - 0.3667))`.
   Capture is a *race*, not a certainty. An earlier version used
   `p_cap` in [0.35, 0.95] every step, which compounds to ~1 over 60 steps and
   re-saturated DSR at 0.97-1.00. That bug is why these constants look small.
5. **Reward** `R = 0.30*r1 + 0.70*r2`, where `r1 = 1` if contained this step and
   `r2 = alignment`. Identical in every arm — a v1 defect was different weights
   per arm, which made the ablation a comparison of different MDPs.
6. **Termination**: captured; or `progress >= GOAL_STEPS (5)` goal-tactic
   advances, so the attacker wins and `TERMINAL_PENALTY = -0.5` is added
   (**additive, not replacing** the step reward — replacing it would make that
   step's return action-independent); or `max_steps` reached.

**Observation** is per-agent and *local* (Dec-POMDP): own-zone one-hot, an
attacker-sighted flag, own-zone compromise, global compromise fraction, alert
level, normalised step, and the observed technique **only when sighted** —
concatenated with the 64-d intent embedding `h`.

`padded_sequence()` returns **RIGHT-padded** ids plus a true length. This is not
cosmetic: v1 left-padded, and combined with absolute sinusoidal position encoding
that let the encoder read episode-step off the padding geometry (h -> step-index
probe R^2 = 0.97). Encoders must gather the last *real* token at `length-1`.

### 5.2 v3 — `topology.py` + `env_entity.EntityDeceptionEnv` (variable topology)

Follows Symes Thompson, Caron, Hicks & Mavroudis (2024), arXiv:2410.17647. The
*formulation* is ported, not the Yawning Titan code.

**How a topology is generated** (`generate_topology(seed, n_zones, ...)`, fully
deterministic from the seed):

1. Zones: `Internet` (entry, id 0) plus `Zone1..Zone(n-1)`, all defended.
2. Zone graph: start from the same firewall hub as v2 (complete among defended,
   plus Internet to every defended zone). Then drop each defended-defended edge
   with probability `p_firewall_block` — **but restore it if removal would
   disconnect the graph**, so connectivity holds by construction rather than by
   rejection sampling.
3. Hosts: one `Attacker` (entry) plus 1-2 external DNS hosts in zone 0; then 1-3
   hosts per defended zone, each with a random node type (of 8), 1-3 services
   (of 8), and 0-5 vulnerabilities.
4. Critical assets: `n_critical` chosen among defender-owned hosts.
5. Agent ownership: `zone -> zone_index % n_agents`, round-robin.
6. **Validated against 10 explicit checks**: connectivity from entry, symmetric
   adjacency, no self-loops, exactly one entry host and it lives in the entry
   zone, at least one critical asset and it is defender-owned, in-range
   zones/types/services/vuln counts, no duplicate host ids, no empty zone,
   firewall rules consistent with the edge set, and every agent owns at least
   one zone. Generation **raises** on an invalid topology.
7. Serialised with its seed and a **SHA-256 content hash** over the structure
   (excluding the name), so topologies round-trip verifiably.

`canonical_topology()` reproduces v2's map exactly and is the **control**
configuration — checked against `env_v2`'s own constants in the self-test.

**Hard constraint:** `n_agents <= n_zones - 1`. QMIX mixes a *fixed* number of
agents, so scale varies in **entities, not agents**. With the default 4 agents,
use `n_zones >= 5`.

**Entity observation.** Every host is an entity with a **47-d** feature vector:
node-type one-hot (8), zone one-hot (16), services multi-hot (8), normalised
vulnerability count, is-critical, is-entry, defender-owned, compromised,
decoy-active, decoy-type one-hot (6), visible-to-me, owned-by-me, attacker-here.
Each agent also gets a **105-d** global vector (its zones multi-hot, sighted
flag, own and global compromise, alert, normalised step, and the technique
one-hot when sighted).

Each agent's observation is a dict: `entities`, `entity_mask` (real vs padded),
`visibility_mask`, `own_mask`, `adjacency`, `action_mask`, `global_feat`, `h`.
**Entities the agent cannot see are zeroed**, so invisible state cannot leak
through the encoder. Padding exists only so batches stack: padded slots are zero,
excluded from attention and pooling, and can never be a legal target.

**Composite action `(action_type, target_entity)`.** The type indexes the same
six D3FEND classes; the target names the host the decoy is placed on. Alignment
is credited **only if the decoy sits in the zone the attacker entered**. On the
canonical topology each agent owns exactly one zone, so any legal target is
inside that zone and the term reduces to v2's exactly — which is what makes
exact equivalence achievable rather than approximate. On larger topologies an
agent owns several zones and *placement becomes a real decision*. The
environment **raises** on an unauthorised target rather than silently accepting
it.

### 5.3 How equivalence is proven

`env_entity.equivalence_report()` runs both environments on identical seeds and
identical action types and compares **full trajectories**, not summary
statistics: technique id, zone, responsible agent, blind flag, alignment, capture
probability, captured, reached-objective, reward, and done. Current result:
**0 mismatches across 1,126 steps / 200 episodes**, with mean return, episode
length and capture rate identical to six decimal places.

---

## 6. The datasets

Three distinct data objects with **different provenance**. The distinction
matters and is easy to get wrong.

### 6.1 CAM-LDS — source-verified (encoder corpus + vocabulary)

`parse_attackbed.py` parses the published AttackMate playbooks from
`github.com/ait-testbed/attackbed`. Each command carries ordered metadata
(`techniques:`, `tactics:`, `technique_name:`), and because those blocks appear
in command order, reading them top to bottom recovers the true executed
technique sequence at full step resolution.

| Property | Value |
|---|---|
| Playbooks | **36** (37 files; `scenario_5.j2.yml` deduped against `scenario_5.j2`) |
| Labelled technique instances | **1,339** |
| Independent campaigns | **7** (S1=18 runs, S2=2, S3=8, S4=1, S5=1, S6=5, S7=1) |
| Parent techniques | **81** |
| Tactics | **13** |

**[CORRECTED]** This originally claimed the counts "match the CAM-LDS paper's
Table 3 exactly." **Withdrawn** — see Phase 1. After fixing three further parser
defects the parse yields **82** parent techniques against the paper's 81, and the
apparent exact match was an artefact of the bugs cancelling out.

Parser bugs found and fixed, in two rounds:
- *round 1* — 35 playbooks use `tactics:` but the two scenario-5 files use the
  singular `tactic:` (silently dropping an entire scenario); `.j2` / `.j2.yml`
  are the same playbook (double-counting S5).
- *round 2 (Phase 1, via an independent second parser)* — a block-order bug
  (`tactics:` appearing before `techniques:` emitted nothing, losing T1190,
  T1059.004, T1095) and two inline-`#`-comment bugs after quoted values (losing
  1× T1222.002 and 4× T1219). **8 instances recovered**, 1,339 → 1,347.

**[CORRECTED]** The hand reconstruction was scored at **precision 98.7% / recall
92.6%**, "having invented T1095." **T1095 is real**, at `scenario_7.j2:95` — it
was hidden by the block-order bug. Reconstruction precision is **100%**.

**Statistical character** — this is why CAM-LDS is the better test corpus:
self-loop rate **18.6%**, majority baseline **0.108**, within-scenario Jaccard
**0.871** against across-scenario **0.078** (10.4x). That last ratio is why
splitting must be by *scenario*, and why leave-one-scenario-out collapses to near
zero: roughly 92% of a held-out campaign's techniques were never seen in
training. That is a corpus property, not a model failure.

### 6.2 COMISET — encoder corpus only

Perez-Sanchez, Palacios & Lopez, *Data in Brief* 2025,
doi:10.1016/j.dib.2025.111723. **Not redistributed** — obtain it separately and
place it at `thesis_system/data/comiset_sessions.json`.

| Property | Value |
|---|---|
| Sessions | 5,637 |
| Raw steps | 1,547,359 |
| **Usable windows after run-collapsing** | **23,754** — see below |
| Size advantage over CAM-LDS | **≈18×** *(not 1156×)* |
| Self-loop rate | **98.5%** |
| Majority baseline | 0.375 |

**[CORRECTED]** This table originally reported "1,547,359 steps (**1156×**
CAM-LDS)". That number counts raw steps, 98.5% of which are self-loops — the
same technique repeated. Collapsing runs leaves **23,754** distinct transition
windows, so the real data advantage is **≈18×**, not 1156×. Every COMISET
comparison in this document that relies on the 1156× figure is overstated by
roughly 64×.

The 98.5% self-loop rate is the caveat that must accompany every COMISET number:
much of the headline accuracy is "repeat the previous technique." Splitting is by
**session**, never by window — windows from one session share a prefix, so a
window-level split leaks the same campaign across train and test.

**Transfer direction matters.** COMISET's 5 observed tactics are a strict
*subset* of CAM-LDS's 13, so COMISET -> CAM-LDS is not a generalisation test
(8 of 13 classes unseen at test time) and indeed failed at Top-1 0.010. The valid
headline direction is CAM-LDS -> COMISET. Only 24.2% of tactic support is shared;
that is a label-space problem no amount of data fixes.

### 6.3 The vocabulary

Union of both corpora, **append-only**: ids 0-22 frozen from v1, 23-77 from the
reconstruction, **78-83 appended** after source verification. Now
`NUM_TECHNIQUES = 84`, `VOCAB_SIZE = 86` (PAD 84, UNK 85). Sub-techniques map to
their parent (`T1574.002 -> T1574`). **Zero UNK on both corpora.**

Tactic-level aggregation was considered and **rejected on measured grounds**: it
destroys 82% of the predictable information (0.651 -> 0.117 bits) and inflates
the majority class from 37.2% to 68.9%.

### 6.4 How CAM-LDS becomes the simulator's attacker

`env_v2.build_profiles_from_camlds()` estimates a per-campaign Markov chain
`T_c[tau_prev] -> tau_next` from the scenario orderings (Laplace floor 0.02,
transition weight +4.0, and a goal-drift term +1.2 toward the objective tactic).

The 7 scenarios are consolidated into **3 decision-distinct classes** by
`d3fend_payoff.consolidate_intent_classes`: campaigns demanding the *same*
optimal deception are the same intent as far as the defender is concerned, and
reporting 7 would inflate the benchmark.

| Profile | Member scenarios | Goal tactic |
|---|---|---|
| `decoy_persona` | S1, S4 | Command and Control |
| `decoy_file` | S2, S3, S6 | Collection |
| `decoy_credential` | S5, S7 | Credential Access |

> **PROVENANCE SPLIT — verified 2026-09-02, must be disclosed**
>
> **The attacker profiles are still built from the OLD hand reconstruction**
> (`data/camlds_grounding.json`), not from the source-verified file.
> `build_profiles_from_camlds()` defaults to that path and reads a `scenarios`
> **list** carrying `technique_sequence`; the verified file stores `scenarios` as
> a **dict**, so passing it raises `TypeError`.
>
> Therefore the "source-verified" claim covers the **vocabulary** and the
> **CAM-LDS encoder experiments**, but **not** the simulator's attacker model.
> Every v2 and v3 DSR number rests on the reconstruction-derived attacker. The
> reconstruction was 98.7% precise, so the effect is probably small — but it is
> **unmeasured**, and should be stated rather than glossed.
>
> **Fix, if this needs closing:** add a schema adapter so profiles can be built
> from the verified grounding, then re-run the payoff headroom gate (delta >=
> 0.15) and all four env gates. Do **not** re-tune `payoff_frozen.json` to
> accommodate any shift.

### 6.5 The payoff matrix (not a dataset, but the other grounded object)

Generated **by rule** from the MITRE D3FEND Deceive tactic (Kaloroumakis & Smith,
2021): **4 free constants** (`W_PRIMARY 0.90`, `W_ADJACENT 0.45`, `W_OTHER 0.10`,
`W_NULL 0.05`) plus disjoint primary tactic sets per decoy class, replacing the
115 hand-authored cells of v1. Headroom delta = **0.2698** (v1: 0.0740).

Frozen at `payoff_frozen.json`; extended 78 -> 84 rows by the identical rule with
rows 0-77 verified bit-identical (sum 132.6000).

**Standing disclosure:** `decoy_network_resource` and `decoy_environment` are
*never optimal* under this corpus, because no CAM-LDS scenario terminates in
Reconnaissance or Initial Access. Exercising them requires recon-terminal or
access-broker campaigns.

---

## 7. Results so far

### 7.1 v2 simulator (10 seeds, Holm-corrected)
H1 Step-Counter Oracle **+0.113** (*d*=4.12), H2 Best-Fixed **+0.101** (*d*=5.28),
H3 NoTrans **+0.061** (*d*=1.75) — all SUPPORTED.
H4 SetEncoder −0.006 and H5 GRU +0.0005 — **not significant**.

### 7.2 COMISET (session-level split; majority 0.375)
| Model | Top-1 | Top-3 | PPL |
|---|---|---|---|
| Transformer | 0.646 | 0.917 | 2.68 |
| GRU | 0.649 | 0.910 | 2.61 |
| SetEncoder | 0.461 | 0.906 | 3.69 |
| *v1 (old)* | *0.341* | *0.715* | *133* |

COMISET has a **98.5% self-loop rate**, so much of that accuracy is "repeat the
last technique."

### 7.3 CAM-LDS (source-verified: 36 runs, 1,339 steps, **7 campaigns**)
Corpus properties: self-loop rate **18.6%**, majority baseline **0.108**,
within-scenario Jaccard **0.871** vs across-scenario **0.078** (10.4×).
COMISET is **1156× larger** in RAW steps -- but **[CORRECTED]** 98.5% of
those are self-loops. After run-collapsing it holds 23,754 usable windows,
so the real advantage is **~18×**.

Three protocols bracket the truth:

| Protocol | What's held out | Transformer | GRU | SetEncoder |
|---|---|---|---|---|
| P1 LOSO | whole campaign | 0.066 | 0.046 | 0.019 |
| P2 variant hold-out | unseen execution variant | 0.493 | **0.633** | 0.484 |
| P3 run-level random | leaky contrast | 0.545 | 0.694 | 0.549 |

P1 is near-zero because ~92% of a held-out campaign's techniques are unseen —
a **corpus property, not a model failure**. The defensible claim is P2.
Memorisation gap P3−P2 = +0.052; generalisation cliff P2−P1 = +0.427.

**Paired test, 45 matched pairs, Holm-corrected:**

| Contrast | Δ Top-1 | *d* | p_holm |
|---|---|---|---|
| **GRU − Transformer** | **+0.1388** | **1.65** | 5.7e-14 |
| GRU − SetEncoder | +0.1678 | 1.75 | 1.2e-14 |
| Transformer − SetEncoder | +0.0290 | 0.34 | 0.028 |

Reading: sequence order *does* carry signal (Transformer beats the order-blind
SetEncoder), **but attention is the wrong instrument for exploiting it** — the
GRU beats the Transformer by ~5× that margin.

### 7.4 v3 entity experiment (RTX 4080 SUPER, 10 seeds, 6,805 s, 60/60 runs)

All 10 gates passed on the GPU machine. The analysis was independently re-run
and reproduces the shipped file to **0.00e+00**.

DSR by arm and regime (mean ± 95% CI, n=10):

| Network | History | A control | B trained sizes | C unseen struct | D unseen sizes | gap B−D |
|---|---|---|---|---|---|---|
| EntityTransformer | Transformer | 0.469±0.029 | 0.445±0.029 | 0.454±0.029 | 0.380±0.031 | +0.066 |
| EntityTransformer | GRU | 0.458±0.045 | 0.433±0.039 | 0.431±0.038 | 0.368±0.024 | +0.066 |
| EntityTransformer | SetEncoder | 0.441±0.030 | 0.424±0.030 | 0.423±0.029 | 0.365±0.027 | +0.059 |
| **DeepSets** | **Transformer** | **0.485±0.034** | **0.459±0.034** | 0.455±0.037 | **0.383±0.032** | +0.076 |
| DeepSets | GRU | 0.463±0.021 | 0.439±0.017 | 0.445±0.017 | 0.371±0.019 | +0.068 |
| DeepSets | SetEncoder | 0.459±0.029 | 0.440±0.028 | 0.441±0.026 | 0.363±0.024 | +0.077 |

**All 7 pre-registered contrasts are non-significant (p_holm = 1.000), and all 7
point AGAINST the hypotheses.** H6, H7, H8 all **NOT SUPPORTED**.

- Best arm in every regime is a **DeepSets** arm.
- DeepSets trains **1.84×** faster (68 s vs 125 s) at matched encoder capacity.
- Generalisation gap is +0.059…+0.077 for **all six arms** — no architecture
  transfers to unseen network sizes better than any other.
- **Power caveat:** n=10 detects only *d* ≥ 1.00 (α=.05) or *d* ≥ 1.41 (Holm);
  observed |*d*| ≤ 0.39. Small effects are not excluded by the p-values.
- **But the effect is bounded.** Pooled (exploratory, n=30): Δ = −0.0118,
  **95% CI [−0.028, +0.004]**. Any true attention benefit is ≤ 0.4 pp of DSR.

### 7.5 The most important finding

Intent-prediction accuracy does **not** translate into deception success, and the
ordering is inverted:

| History encoder | Pretrain Top-1 | Regime-B DSR |
|---|---|---|
| GRU | **0.558** (best predictor) | 0.436 |
| SetEncoder | 0.511 | 0.432 |
| Transformer | **0.361** (worst predictor) | **0.452** (best DSR) |

Across all 60 runs: Pearson *r* = **−0.175** (p=0.18), Spearman *ρ* = −0.104
(p=0.43) — **not significantly different from zero**, so report as *"no
relationship"*, not as a demonstrated negative one. Still: a 54% relative gain in
intent prediction bought **zero** DSR improvement. The thesis pipeline assumes
that link; the data do not support it.

---

## 8. Where this leaves the thesis

**[CORRECTED]** This originally read: "Across four independent tests the
Transformer has **never won**, and on CAM-LDS it *significantly lost*." Both
halves are now known to be too strong:

- **"never won"** — on DSR with the DeepSets network encoder, v3's history
  Transformer was nominally *ahead* (0.459 vs 0.439). On that metric the history
  encoders were always within noise of one another.
- **"on CAM-LDS it significantly lost"** — the reported GRU advantage of
  **+0.1388** (*d* = 1.65, p_holm = 5.7e-14) was measured on a Transformer
  handicapped by our own configuration: absolute sinusoidal position at untuned
  defaults. With rotary position and an equal 16-trial tuning budget applied to
  both arms, the gap closes to **+0.0000** — with the Transformer at **44%** of
  the GRU's parameters (Phase 2.4/2.5).

The architecture claim in the title still cannot be sustained, but for a
different and better-established reason. The current statement of it is in
`results_v5/PHASE5_RESULT.md`: on an instrument that demonstrably rewards
sequence modelling, with 5 of 5 arms clearing the memoryless baseline, all 8
pre-registered contrasts are null and any attention advantage is **bounded within
±0.007 DSR** at the canonical topology.

**Defensible contributions:**
1. A variable-topology entity environment reproducing its fixed control
   **exactly** (0/1,126) — a real validity contribution.
2. A D3FEND-grounded payoff generated by rule (4 constants, not 115 hand cells),
   with headroom δ = 0.2698, frozen and never refitted.
3. A source-verified CAM-LDS grounding, parsed from the AttackBed playbooks with
   five parser defects found and fixed across two rounds. **[CORRECTED]** — this
   originally read "matching the published paper's counts"; the parse yields 82
   parent techniques against the paper's 81, and the earlier exact match was an
   artefact of the bugs. The defensible contribution is the *audit*, not the
   agreement.
4. A pre-registered, Holm-corrected, 10-seed factorial that answers its question
   **in the negative with the effect bounded** — not merely undetected.

**No longer claimable:** that the Transformer is what makes TEMARL work; that
better intent prediction drives deception performance; cross-OS generalisation
(COMISET→CAM-LDS transfer failed at Top-1 0.010 — only 24.2% shared tactic
support, a label-space problem no data volume fixes).

---

## 9. Reproduction

Full runbooks: `RUN_V3.md` (v3) and `REPRODUCE.md` (v2). Short form:

```bash
cd thesis_system/temarl_v2
# Windows first: $env:PYTHONUTF8="1"; $env:PYTHONIOENCODING="utf-8"

python gates_v3.py                          # all 10 gates, ~30 s
python train_entity.py --quick              # smoke test, ~2 min
python train_entity.py --save-checkpoints   # full run, ~3 h CPU / ~1.9 h GPU
python evaluate_entity.py                   # pre-registered stats
```

Expected: `ALL GATES PASS (10/10)`, equivalence **0 mismatches**,
`tests_entity` **26/26**, headroom **0.2698**, CAM-LDS UNK **0/1339**.

---

## 10. Gotchas that have already cost time

| Symptom | Cause / fix |
|---|---|
| Training appears stuck, empty log | Python buffers when redirected — use `python -u` |
| Extremely slow training | `EntityDeceptionEnv` was rebuilding CAM-LDS profiles from JSON every episode. Fixed by the `profiles()` cache in `train_entity.py`; keep it |
| `UnicodeEncodeError` on Windows | Set `PYTHONUTF8=1` before redirecting output |
| `ModuleNotFoundError` | Not running from `thesis_system/temarl_v2/` |
| `attackbed/` empty after clone | Recorded as a bare gitlink with no `.gitmodules`. Harmless — the verified grounding is committed. Clone AttackBed separately only to re-run the parser |
| Gradient probe shows zero | Two false negatives were hit before: (a) `.sum()` of a LayerNorm output is constant, so gradients vanish — use a random projection; (b) probing the history branch with `h = 0` gives a zero weight-gradient by construction. **Both were test bugs, not model bugs** |
| `n_agents N exceeds defended zones` | Topologies need `n_zones >= n_agents + 1` (default 4 agents → `n_zones >= 5`) |
| GPU log unreadable | PowerShell redirects as UTF-16; decode with `utf-16` |

---

## 11. Open items

1. **Revised Chapter 5** — rewrite around the four defensible claims above.
   Offered several times, not yet taken up. This is the main remaining writing task.
2. **Manuscript defects** still unfixed (write-up only): agent count stated as 3
   vs 4; Fig 1.1 says "five … HP1–HP4"; Ch-5 cross-refs point to "6.x"/"Chapter 7";
   50k vs 80k steps inconsistency; 1.8021 vs 1.8007; duplicate Bibliography; © 2024.
3. **Disclosures to add**: F-DAT-03/04/05/09, F-RWD-02, F-ENV-06.
4. **Optional experiments**: larger training budget (DSR was still improving at
   500 episodes); a learning attacker (from the CyberBattleSim deception paper);
   recon-terminal campaigns so `decoy_network_resource` / `decoy_environment`
   become exercisable — the payoff gate currently forces a disclosure that they
   are never optimal.

---

## 12. Working preferences

- Confirm before file operations; the user has previously rejected an
  unconfirmed copy ("stay how it is").
- Report failures plainly with the output; never tune a threshold to make a gate
  pass; diagnose instead.
- A well-tested negative result is a valid deliverable and is preferred over an
  unsupported positive claim.
