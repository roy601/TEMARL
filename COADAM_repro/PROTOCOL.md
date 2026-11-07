# Frozen experimental decisions

Version 1. This file and protocol.json must be frozen before lab results are inspected. Outcomes do not alter the seed count, algorithm settings or reported subset.

## Two tracks

| Setting | release | paper_aligned |
|---|---|---|
| Purpose | Run released algorithms with portable paths and real tabular model | Test selected paper-described settings; NOT a complete recovered author configuration |
| Seed indices | 0–9 | Same 0–9 |
| Co-ADAM training | 5,000 episodes × at most 100 steps | Same |
| Architecture | Source 12 → 128 → 64 → 4 | Same |
| Co-ADAM optimizer | Source manual batch gradient updates | Adam; beta1=.9, beta2=.999, epsilon=1e-8 assumed |
| Co-ADAM learning rate / discount | .0005 / .85 | Same |
| Batch / replay capacity | 64 / 100,000 | Same |
| Target network interval | Source 100 episodes | 100 environment steps |
| Clipping | Source scalar TD clipping ±1 | Global norm clipping 2 on averaged gradients |
| Defender non-exploration selection | Source annealed softmax | Greedy argmax; epsilon exploration retained |
| Co-training attacker | Source config lr/gamma; epsilon .20 | lr .01, gamma .90, epsilon .30 |
| Evaluation episodes per method/regime | 100 (released script) | 200 (paper) |
| Evaluation seeds | Original method-specific expressions, offset per repeat | Separate 100,000/random and 200,000/adaptive namespaces; matched initial seed per method |
| Tabular baseline pretraining | Released tabular trainer, 2,000 episodes | Same trainer, 5,000 episodes |
| Individual DQN / deception baseline training | 3,000 episodes each | Unchanged source baseline algorithms and budgets |
| Adaptive attacker fine-tuning | 1,000 episodes PER method | Same; source fine-tuning lr .002 and epsilon .20 retained |
| Stackelberg simulations | 50 per source combination | Same |

Adam's default moments, global-gradient interpretation, greedy replacement, tabular checkpoint provenance/budgets, seed schedule and baseline training interpretation are **declared reconstruction assumptions**. The paper-aligned track applies selected settings to Co-ADAM, not every baseline; it must not be called a fully paper-faithful implementation. The source Individual DQN has six mechanism actions, while Co-ADAM selects four bundles. Changing this would redefine a published baseline, so it is preserved and disclosed.

Seed offset = index × 1,000,000. Shift both initializer RNG and every environment reset: reset reseeds the global MATLAB RNG. Tabular pretraining uses offset+300,000. Source baseline training seed overlaps and some training/evaluation overlaps are retained in `release` as fidelity limitations. The paper-aligned evaluation namespaces separate final evaluation from training, but equal initial seeds do not guarantee identical action-dependent random trajectories. No claim of independent datasets is made.

## Preconditions and checks

1. Pin upstream code and processed inputs; retain unchanged upstream files and README.
2. Freeze protocol, target transcription, seed list and source/config hashes before execution.
3. Run mandatory smoke for each track: 8 training episodes, 20 steps, 3 evaluation episodes; reduced baseline/fine-tuning budgets. Smoke proves execution only, not convergence or fidelity.
4. Check MATLAB/toolbox availability, 12 input features, 4 defender actions, 45 attacker actions, deterministic reset, finite Adam updates.
5. Train a tabular model before baselines. Refuse the upstream silent fallback from missing Tabular_QL to static defense.
6. Run original DQN training, then baselines. Validate all eight method names, raw counts and finite metrics.
7. Save completion markers only after artifact checks. Preserve raw data and failed-stage logs.

## Results contract

Table 5: random attacker, AMR, infection rate, cumulative defender reward, DSR. Table 6: adaptive attacker, AMR, infection rate, reward, degradation. The report also gives DSR for Table 6 and all ten environment metrics for every method/seed. Rates are fractions, rewards use source units. MTTD and dwell retain source definitions and must not be equated with TEMARL command-level dwell without a shared metric contract.

Degradation is calculated using the released baseline report formula:

`AMR_A - AMR_B + Infection_B - Infection_A + 0.5*abs(DSR_A - DSR_B)`.

This formula's correspondence to the published Table 6 is unresolved. Its values are labelled calculated, never replaced with the published values. Source `.mat` arrays have 100 episodes, whereas paper evaluation uses 200; some source means/SDs differ from published entries. No archived array is used as new experimental evidence.

Report all ten seeds; no selection of best or closest seeds. Main aggregation is mean and sample SD of seed means. Within-seed evaluation variability is separate. Partial reports identify their completion count and cannot support final conclusions. The report does not manufacture p-values, equivalence conclusions or a claim of perfect reproduction.

## What is preserved and what is not inferred

Environment dynamics, rewards, skepticism, co-evolution pool logic, state discretization, mechanisms and baseline policy definitions come from the release. Co-ADAM-only `intel_boost_enabled` is preserved, not applied to every baseline. The source trainer's own diagnostic evaluation uses softmax despite a 'greedy' label; final Tables 5/6 use Phase5 action selection. Only final baseline evaluations enter the comparison tables.

No new dataset, external optimizer implementation, invented measurement or unrelated paper's environment is substituted. The custom Adam routine implements the conventional equations; its numerical defaults are assumptions, not recovered author artifacts. Training/evaluation terminal handling and loss scaling follow the source unless explicitly patched; remaining source defects are possible and must be audited before claims of strict reproduction.

## Interpretation rule

If results are close, say 'numerically consistent under the documented assumptions', with differences and variability. If different, report discrepancy and inspect source/measurement definitions. Do not tune until target numbers appear. Neither track can establish the original training seeds or missing checkpoint provenance. Authors' clarification remains necessary for an exact provenance claim. This experiment evaluates Co-ADAM in its released simulator; it is not yet a same-environment comparison against TEMARL.
