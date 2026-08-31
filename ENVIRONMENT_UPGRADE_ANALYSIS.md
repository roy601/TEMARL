# Which Paper Should We Build the Complex Environment From?

**A critical analysis of five candidate references for upgrading the TEMARL v2 environment.**

Status: analysis only. `thesis_system/temarl_v2/env_v2.py` is **not modified** by this
document. Any environment built from this analysis goes in a **new** module
(`env_v3_entity.py`), with `env_v2.py` retained as the frozen comparison baseline.

---

## 0. Verification of the source table

Every paper was fetched and checked before analysis. Four claims in the original
table need correcting, and they change the ranking.

| # | Paper | Original table said | **Verified** |
|---|---|---|---|
| 1 | CybORG++ (Emerson, Bates, Hicks, Mavroudis, 2024) | "Complex defender-side cyber gym" | Correct — but **contains no deception, honeypots, or decoys**. Its headline contribution is *MiniCAGE*, a ~1000× faster CAGE-2 re-implementation. |
| 2 | Entity-based RL (Symes Thompson, Caron, Hicks, Mavroudis, 2024) | "Variable topology + Transformer policy" | Correct, but built on **Yawning Titan, not CybORG** — so it does *not* compose with #1 as the table's recommendation assumes. |
| 3 | Deception in CyberBattleSim (Walter, Ferguson-Walter, Ridley, 2021) | "Honeypots and decoys in RL simulator" | Correct, but **the RL agent is the *attacker*, and decoys are static configuration** — not adaptively placed. This is inverted from TEMARL. |
| 4 | CyGIL (Li, Fayad, Taylor, 2021) | "MITRE ATT&CK-based emulated operations" | Correct — and **emulated**, requiring real infrastructure. |
| 5 | Production-Worthy Simulation (Tholl, El Mezouar, Taylor, Al Mallah, 2025) | "Realistic defender actions in CybORG" | Correct — adds **patch / isolate / unisolate**, none of which are deception actions. |

**The original recommendation — "CybORG++ as the main environment, borrow deception
from CyberBattleSim and topology ideas from Entity-based RL" — does not survive
verification.** CybORG++ has no deception to build a deception thesis on, and #2 is
a different simulator, so the three do not compose into one system.

---

## 1. The decisive criterion: what problem are we actually solving?

A "more complex environment" is not a goal. It is only worth the cost if it fixes a
*measured* defect. As of 2026-09-01 the measured defects are:

| Finding | Measurement | Source |
|---|---|---|
| **The Transformer does not earn its place** | CAM-LDS P2, 45 matched pairs, Holm-corrected: GRU − Transformer = **+0.1388**, *d* = **1.65**, p_holm = **5.7e-14**. COMISET: 0.649 vs 0.646 — a tie. | `results_v2/camlds_ab_test.json` |
| Order matters — but attention is the wrong way to use it | Transformer − SetEncoder = **+0.029**, *d* = 0.34 (small, p_holm = 0.028). GRU − SetEncoder = **+0.168**, *d* = 1.75. | same |
| Simulator H4/H5 nulls | SetEncoder −0.006, GRU +0.0005 vs Transformer, both n.s. | `results_v2/evaluation_v2.json` |
| Cross-campaign transfer fails | LOSO Top-1 0.066 / 0.046 / 0.019 | `results_v2/camlds_protocols.json` |
| The corpus is tiny | 1,339 steps / 36 runs / 7 campaigns; COMISET is 1156× larger | `camlds_grounding_verified.json` |
| Two decoy classes are never optimal | `decoy_network_resource`, `decoy_environment` — no CAM-LDS scenario terminates in Reconnaissance or Initial Access | `d3fend_payoff.py` gate |

**The thesis is called "Transformer-Enhanced". Across four independent tests the
Transformer has never won.** That — not environment size — is the existential
problem. So the correct criterion is:

> Which paper gives us an environment in which a Transformer is *expected to win
> for a principled reason*, without discarding the assets we have already verified?

Environment complexity that does not bear on that question is cost without return.

---

## 2. The single most important piece of evidence

From the Entity-based RL abstract, verified verbatim:

> the Transformer policy "**significantly outperforms an MLP-based policy when
> training across fixed-size networks of varying topologies**" and achieves
> "**zero-shot generalisation to networks of a different size**" — but it merely
> "**matches performance when training on a single network**."

This is the diagnosis of our own result, stated independently in the literature.

**TEMARL v2 trains on a single, fixed 5-zone topology.** That is precisely the regime
in which the paper reports a Transformer *matching, not beating*, a simpler policy.
Our GRU > Transformer result is therefore not a bug and not bad luck — it is the
expected outcome of evaluating attention in a setting with no variable structure for
attention to exploit.

The three-way contrast makes the mechanism sharper than a simple loss would:

- **Sequence order genuinely carries signal** — the Transformer beats the order-blind
  SetEncoder (+0.029, *d* = 0.34, p_holm = 0.028). So this is not a task where order
  is irrelevant.
- **But attention is the wrong instrument for exploiting it here** — the GRU beats the
  Transformer by nearly five times that margin (+0.139, *d* = 1.65, p_holm = 5.7e-14).

Attention pays for itself over **variable-cardinality entity sets**, not over
16-step technique sequences drawn from one fixed map with ~1.3k training windows.
That is the mechanism, it explains all four of our null-or-negative architecture
results at once, and it is testable by changing exactly one thing: the topology.

---

## 3. Per-paper critical assessment

### #2 Entity-based RL for Autonomous Cyber Defence — arXiv:2410.17647

**Fit: highest. This is the only paper that addresses the measured defect.**

- Reformulates observation *and* action space as a set of discrete entities (hosts,
  services, subnets), so one policy handles 12, 20 or 50+ nodes.
- Directly supplies the condition under which our Transformer should win, and an
  evaluation design (train on a topology distribution, test zero-shot on unseen
  sizes) that turns a currently-null contribution into a falsifiable claim.
- **Additive, not destructive**: entity-based observation replaces the 152-dim fixed
  local vector in a *new* env module. The D3FEND payoff, the CAM-LDS grounding, the
  vocabulary, the pre-registered evaluation, and all six gates carry over unchanged.

**Risks, stated honestly:**
- Built on Yawning Titan, so the *code* is not directly reusable — we port the
  *formulation*, not the implementation.
- The 4-agent QMIX mixer assumes a fixed agent count. Variable topology means
  variable agent count, which needs either agent-count-invariant mixing or a fixed
  agent set over a variable entity set. **The latter is the cheaper, safer choice**:
  keep 4 defender agents, let the number of *entities they observe* vary.
- It is a defence-generalisation paper, not a deception paper. It contributes
  structure, not deception semantics.

### #3 Incorporating Deception into CyberBattleSim — arXiv:2108.13980

**Fit: second. The only genuinely deception-focused paper of the five.**

- Its finding — attacker progress depends on the **number and location** of decoys —
  is the closest published analogue to our DSR/alignment objective.
- Its decoy taxonomy (fake services, fake credentials, fake vulnerabilities) maps
  cleanly onto our five D3FEND decoy classes and can justify expanding the action
  set beyond six.
- **The attacker-side RL is an asset, not a liability.** Our current attacker is a
  scripted profile sampler. A *learning* attacker is the standard answer to "your
  defender only beats a fixed opponent," and this paper supplies the precedent.

**Risks:**
- Inverted agent role means the experimental design is not directly transferable.
- Decoys are static configuration there; our whole contribution is that placement is
  adaptive. We are extending it, not reproducing it.
- 2021, CyberBattleSim is abstract and no longer actively developed.

### #1 CybORG++ — arXiv:2410.16324

**Fit: as a benchmark and a speed reference — not as our base environment.**

- Genuinely strong engineering: MiniCAGE's ~1000× speedup is worth studying for our
  own rollout loop, where 10-seed × 200-episode evaluation is already a cost.
- Well-maintained, credible, and a recognised name for the related-work chapter.

**Why it should not be the base, stated plainly:**
- **It has no deception mechanics.** Building a honeypot-deception thesis on a gym
  with no decoys means implementing the entire deception layer ourselves — at which
  point we have written our own environment anyway, but on someone else's abstractions.
- Adopting it **discards our most defensible assets**: the D3FEND-generated payoff
  (4 constants replacing 115 hand-authored cells, headroom δ = 0.2698), the
  source-verified CAM-LDS grounding (81 techniques / 13 tactics, matching the
  paper's Table 3 exactly), the frozen payoff matrix, the pre-registered hypothesis
  family, and all six passing gates. That is the bulk of the v2 rebuild.
- CAGE has a competitive leaderboard with strong tuned baselines. Entering that arena
  at B.Sc. scale invites a comparison we would lose, against a metric that is not
  what our thesis claims.

### #5 Towards Production-Worthy Simulation — arXiv:2508.19278

**Fit: low, and conditional on adopting #1.**

- Adds patch / isolate / unisolate to CAGE-2. Useful realism *if* we were on CybORG.
- **None of the three added actions are deception actions.** They would dilute a
  deception-focused action space, and our payoff gate already shows we cannot
  exercise two of the five decoy classes we have. Adding non-deception actions
  before fixing that is the wrong order.
- Recent (2025) and worth one related-work sentence on operational realism.

### #4 CyGIL — arXiv:2109.03331

**Fit: lowest — because we already have what it provides.**

- CyGIL is an **emulated** ATT&CK-based gym requiring real infrastructure.
- **We already have an emulation testbed: AttackBed, cloned and parsed.** It gave us
  36 playbooks, 1,339 labelled steps, 81 techniques and 13 tactics — verified against
  the CAM-LDS paper exactly. CyGIL would fill a slot that is already filled.
- Emulation is also the wrong cost profile: our entire pipeline is CPU-only and runs
  in minutes. Emulated RL training needs VMs and hours-to-days per run, which does
  not fit a B.Sc. timeline.
- Keep as a citation for ATT&CK-grounded fidelity; do not build on it.

---

## 4. Revised ranking

| Rank | Paper | Role | Why |
|---|---|---|---|
| **1** | **Entity-based RL (2410.17647)** | **Primary architectural reference** | The only one that targets the measured defect. Supplies the condition under which the Transformer is *expected* to win, and is additive to our verified stack. |
| **2** | Deception in CyberBattleSim (2108.13980) | Deception semantics + adaptive attacker | Only deception-native paper; its attacker-side RL answers the "fixed opponent" objection. |
| **3** | CybORG++ (2410.16324) | Benchmark, related work, speed technique | Credible and useful to cite and learn from; too costly and too deception-free to adopt. |
| 4 | Production-Worthy (2508.19278) | Related work only | Conditional on #1; adds non-deception actions. |
| 5 | CyGIL (2109.03331) | Related work only | Redundant with AttackBed, which we already have. |

**This inverts the original table's #1 and #2, and demotes CybORG++ from base
environment to citation.**

---

## 5. Recommended plan

Build `env_v3_entity.py` as a **new module**. `env_v2.py` stays frozen as the
baseline the new environment must beat.

**Stage 1 — entity-based observations, fixed topology (the control).**
Re-express the 152-dim local observation as a variable-length set of entity records
(zone, host, service, decoy-state). Train on the existing 5-zone map. *Expected
result: no significant change.* That is the point — it isolates the encoding change
from the topology change, so Stage 2's effect is attributable.

**Stage 2 — topology distribution (the actual experiment).**
Sample topologies per episode (zone count, connectivity, host counts) instead of
using one fixed map. **Pre-register before running**, in source, as
`evaluate_v2.py` already does:

> **H6.** On a distribution of topologies, the Transformer's DSR exceeds the GRU's.
> **H7.** Trained on 4–8 zones, the Transformer transfers zero-shot to 12 zones with
> less DSR degradation than the GRU.

H6 and H7 are the hypotheses that can rescue the thesis title. They must be written
down before the run, and **reported whatever the outcome** — a well-tested negative
is a legitimate result and is far stronger than the current untested assertion.

**Stage 3 — decoy taxonomy expansion (from #3), only if Stages 1–2 land.**
Add recon-terminal and access-broker campaigns so `decoy_network_resource` and
`decoy_environment` become exercisable, closing the disclosure the payoff gate
currently forces us to make.

**Stage 4 — learning attacker (from #3), only if time permits.** Highest risk: a
co-adapting attacker can destabilise training and invalidate the frozen payoff's
headroom analysis. Do not start this before Stages 1–3 are reported.

---

## 6. What this plan does *not* fix — stated up front

- **It does not fix the data constraint.** 1,339 labelled steps across 7 campaigns
  is the binding limit on the *encoder*. A richer environment generates more
  simulated episodes but no new real attack sequences. LOSO Top-1 stays near zero.
- **It does not fix cross-corpus transfer.** COMISET → CAM-LDS failed at Top-1 0.010
  because only 24.2% of tactic support is shared. That is a label-space problem; no
  environment change touches it.
- **It may not rescue the Transformer.** H6/H7 are genuine hypotheses, not foregone
  conclusions. If the GRU also wins on a topology distribution, the honest conclusion
  is that the architecture claim should be retired and the thesis reframed around the
  contributions that *did* survive: the D3FEND-grounded payoff, the source-verified
  environment, and the pre-registered evaluation. **Plan for that outcome now**, so it
  is a finding rather than a crisis.

---

## 7. Bottom line

Use **Entity-based RL (arXiv:2410.17647)** as the primary reference, and
**Deception in CyberBattleSim (arXiv:2108.13980)** as the secondary. Cite CybORG++,
Production-Worthy and CyGIL in related work; build on none of them.

The reason is a single verified sentence: a Transformer policy *matches* a simpler
one on a single fixed network and only *beats* it across varying topologies. We are
training on one fixed 5-zone map and losing to a GRU by 0.140 Top-1. Variable
topology is not "more complexity" for its own sake — it is the specific, and only,
complexity for which our central architectural claim has a mechanism.
