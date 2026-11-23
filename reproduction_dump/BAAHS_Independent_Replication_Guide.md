# BAAHS — Independent Replication Toolkit

**Deliverable:** executable Python simulator, BAAHS-inspired belief + placement policy, seven baselines, fixed-trajectory paired evaluation, bounded exploratory reference matching, independent held-out validation, automated tests, raw logs, and a detailed methodological report.

> **IMPORTANT: This is NOT original BAAHS author code, NOT a reconstruction of the authors' experimental simulator, and NOT a reproduction of the published tables.** The accessible paper metadata and abstract establish architectural elements and headline results, but the complete paper methods, exact data, emission matrices, algorithm details, and evaluation scripts were not available when this package was created. Everything not documented below as publication-grounded is an **independent modeling assumption**. Do not cite this package as an original-author reproduction.

## 1. Academic reference and evidence

**Publication:** Srinivasan et al., *BAAHS: Behavior-Aware Adaptive Honeypot Placement Using Online Bayesian Attacker Inference and Thompson Sampling*, **IEEE Access**, volume 14, pp. 156329–156363, published 9 October 2026. DOI: <https://doi.org/10.1109/ACCESS.2026.3740819> (publisher: <https://ieeexplore.ieee.org/document/11731822/>).

The accessible publisher abstract supports these architectural and experimental statements:

- Online Bayesian inference with an **11-state HMM** and MITRE ATT&CK-aligned attacker states.
- A **five-mode** engine using expected interaction, data quality, information gain, deception value and operational risk.
- Stochastic **Thompson-inspired** decoy placement with **fractional rewards**, **belief-shift evidence decay**, and **topology-aware scoring**.
- A **25-node** test topology with **four simultaneously deployed honeypots**.
- A **50-seed**, fixed-trajectory replay protocol: placement chosen after event `e_t` is scored only at `e_(t+1)`, avoiding temporal look-ahead.
- Published **25.89%** BAAHS honeypot hit rate versus **15.32%** strongest principal-comparison baseline; these are **reference-only**, never used to generate events, policy selections or reward updates.
- The paper describes other baselines such as a contextual bandit, discounted Thompson sampling, HMM-greedy and a POMDP-inspired policy.

**Not accessible/verified as author artifacts for this package:** exact 25-node graph, complete HMM transition/emission matrices, threat event generator, exact node-role priors, mode control equations/weights, baseline hyperparameters, published attack trajectories, and source evaluation scripts. This project does **not** include DARPA OpTC traces, whose published 28.2% result is explicitly *projected* (not observed decoy interaction).

## 2. Install

Requirements: **Python 3.10+**, NumPy, and a standard terminal (Windows PowerShell, Linux or macOS). No network calls, credentials, containers, GPUs or third-party APIs are needed once NumPy is installed.

```bash
cd BAAHS_Independent_Replication
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
```

Optional editable installation: `python -m pip install -e .`

## 3. Run tests and smoke test

```bash
python -m unittest discover -s tests -v
python -m baahs.cli run --steps 20 --seeds-per-batch 3 --holdout-seeds 3 --output results/smoke
```

`run_smoke.sh` runs the same sequence on Linux/macOS.

## 4. Standard 50-seed experiment

```bash
python -m baahs.cli run \
  --steps 80 \
  --seeds-per-batch 50 \
  --max-batches 1 \
  --holdout-seeds 50 \
  --output results/standard
```

This runs **50 development seeds** plus a separate **50 held-out seeds**. All eight policies see the **same 79 scored next-event opportunities for each seed**. Each policy runs with its own independent stochastic draws. This is not the authors' experiment length, which was not confirmed from full methods.

**Outputs in `results/standard`:**

| Artifact | Contents |
|---|---|
| `dev_runs.csv` | Complete per-seed hit count and hit rate, each policy |
| `holdout_runs.csv` | Untouched per-seed evaluation, each policy |
| `dev_events.jsonl` | Each per-step observation, selected four decoys and next-event outcome |
| `holdout_events.jsonl` | Same event-level audit trail for held-out seeds |
| `summary.json` | Parameters, all means/standard deviations/CIs, dev stopping history and paper reference differences |
| `EVALUATION_REPORT.md` | Human-readable results, frozen baseline and scientific interpretation |

A **real execution** of the bundled implementation using 50 development and 50 held-out seeds is included in `examples/standard_50seed_run/`. It resulted in different figures from the paper, as expected for a different simulator. See Section 8.

## 5. Automated repeat-until-exploratory-match

The program implements the user's requested automated comparison. **It never changes the model or simulator to force the target numbers, never discards bad seeds, and never labels a lucky exploratory match as reproduced.**

```bash
python -m baahs.cli run \
  --steps 80 \
  --seeds-per-batch 50 \
  --max-batches 20 \
  --repeat-until-match \
  --tolerance-pp 1.0 \
  --holdout-seeds 50 \
  --output results/exploratory_matching
```

At the end of each **cumulative** 50-seed batch, it compares the current BAAHS-inspired mean to **25.89%** and the **development-selected strongest baseline** to **15.32%**. If both are within the stated ±1.0 **percentage-point** window, the exploratory process stops, **preserves every prior seed and raw result**, freezes the selected baseline, and runs 50 *disjoint* held-out seeds. Otherwise it runs until the stated cap of 20 batches (up to 1,000 development seeds), then still evaluates the held-out set. **This is exploratory sequential stopping, which biases the discovery sample towards a match.** The held-out sample alone is eligible for fresh validation, and even an independent match would establish numerical agreement only under our synthetic assumptions—not experimental equivalence to the published study.

Do **not** optimize parameters on the held-out set, repeatedly retry holdout seeds, or present a cherry-picked match as scientific reproduction. There is **no guarantee** that a match will ever occur.

## 6. Architecture and data flow

```text
World: 25-node synthetic topology and 11-stage attacker process
     |
     +--> generate 80-event trajectory using seed (BEFORE evaluation)
                   |
                   +--> identical recorded trajectory to each of 8 policies
                                   |
                                   +--> observe node_t and alert_t
                                   |    infer HMM posterior (where applicable)
                                   |    select exactly four honeypot nodes
                                   |
                                   +--> score only next visit node_(t+1)
                                   |    update policy based on observed result
                                   |
                                   +--> persist every hit, miss and placement
     |
     +--> aggregate paired across seeds -> dev results -> (optional stop)
     |
     +--> frozen-policy and baseline definitions -> disjoint held-out seeds
                 |
                 +--> CI + comparison against reference ONLY in reporting
```

### Modules

- `baahs/world.py` — connected role-labeled synthetic 25-node graph; eleven attacker stages; synthetic HMM and role priors; fixed-seed pre-generated attacker events.
- `baahs/belief.py` — causal HMM forward filtering and candidate-specific proxy information gain.
- `baahs/policies.py` — eight placement strategies and belief-shift-based posterior decay.
- `baahs/evaluation.py` — exact per-event next-step scoring, repeated batch audit, held-out validation, CSV and JSONL output, confidence intervals.
- `baahs/cli.py` — command line.
- `tests/test_core.py` — reproducibility, probabilities, cardinality, causality, I/O, end-to-end tests.

### Policies (NOT author-verified baseline implementations)

1. `baahs_independent` — belief-conditioned stochastic node selection; five objectives, Thompson draws, decayed Beta evidence, role and graph features.
2. `random` — uniformly samples four nodes each event.
3. `static` — four random nodes fixed for the whole trajectory.
4. `centrality` — fixed four highest-degree nodes.
5. `contextual_bandit` — Beta bandit conditioned on observed alert and recent node.
6. `discounted_ts` — per-node decayed Thompson sampling.
7. `hmm_greedy` — causal HMM next-node probability ranking.
8. `pomdp_proxy` — myopic one-step interaction + information-gain ranking; **not a solved POMDP**.

## 7. Metric and reproducibility rules

Per seed, each method's **hit rate** is

```text
hit_rate(seed, method) =
    sum_{t=0}^{T-2} 1[ node_(t+1) in placement_method_after_observing_event_t ]
    -------------------------------------------------------------------------
                                  T - 1
```

The primary reported estimate is the **arithmetic mean of seed-level rates**, not the best seed, best batch, or best checkpoint. The report includes across-seed SD and a **normal-approximation 95% CI** (descriptive only, especially approximate for few seeds). All eight methods use identical recorded trajectories per seed and the same honeypot budget.

**Temporal audit:** `t`-step placement uses `node_t`, noisy `alert_t`, and the policy's prior history. It has no access to `node_(t+1)` or hidden attack state. `feedback` is called **only after** the next target is scored. The synthetic attacker does not react to honeypots; this is a limitation shared with fixed-trajectory evaluation as a concept, but it should not be confused with a live cyber range.

### Five objectives in the independent policy

An illustrative weighted score combines expected interaction, data quality, proxy information gain, deception value, and *negative* operational risk. Weights are explicitly specified in `BAAHSInspiredPolicy.WEIGHTS` and modes cycle every eight events so all five can be inspected. **These weights/schedule are not verified from the paper.** Thompson samples draw from per-node Beta posteriors, with fractional neighbor credits of 0.20 and online exponential decay based on the L1 difference between successive HMM beliefs. **These choices are independent design decisions, not claimed original equations.**

## 8. Results actually generated when packaging this code

**This is an execution of our independent simulator, not BAAHS original-author reproduction.** On one 50+50 seed run with `--steps 80`:

| Source / split | BAAHS-inspired | Development-selected strongest baseline |
|---|---:|---:|
| Paper reference (different unpublished simulator) | 25.89% | 15.32% |
| Independent development — 50 seeds | **29.22%** | **34.15%**, `hmm_greedy` |
| Independent held-out — 50 seeds | **28.05%** | **34.41%**, `hmm_greedy` |

The independent BAAHS-style method **does not outperform** our strongest baseline and **does not match** the paper's reference measurements. This is evidence of the modeling differences, *not* a basis for adjusting code to force agreement. The actual event logs and computed summary are packaged in `examples/standard_50seed_run/`.

## 9. What would be required for a faithful reproduction?

To upgrade this independent experimental exercise into original-method table reproduction, obtain and verify: (1) complete BAAHS paper methods and all parameter tables, (2) original 25-node graph, (3) original stage and observation mappings, (4) actual HMM transition and emission matrices, (5) attacker-path generation and all 50 seeds/paths, (6) exact five-mode controller, TS reward update and decay equations, (7) baseline implementation and hyperparameters, and (8) original target-table scripts and raw output. Replace assumptions **one at a time** and explicitly track them with tests. Training/test split and stopping rules must be fixed before the confirmatory evaluation.

### Reproduction status

- **Article published:** yes.
- **Original author source/package included:** no.
- **Original published 50-seed evaluation executed:** no.
- **Independent working simulator:** yes; unit tests and 50+50 seed evaluation executed.
- **Experimental match to published tables:** **no**.
- **Validated TEMARL baseline:** **not yet**; requires shared attack environment and fair benchmark.

## 10. Scope and responsible use

This project is **offline synthetic defensive research** only. It does not perform scanning, intrusion, exploit delivery, or active network deception. Synthetic attacker trajectories reflect hand-designed state and graph transitions, not real attacker probabilities. External datasets and original author assets are **not bundled**. Original code here may be adapted under the included MIT license; please cite the BAAHS paper when referencing its research ideas and **do not represent this implementation as the paper's own source**.
