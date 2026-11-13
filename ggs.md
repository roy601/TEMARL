# TEMARL: evidence review and practical next steps

Prepared 11 November 2026. Repository inspected: `G:\Desktop\TMARl_1350`.

## Decision at a glance

| Question | Verdict |
|---|---|
| Did sequences come from logs? | They come from released AttackMate execution metadata through the authors' label CSV. They are not techniques inferred from raw host/network telemetry. |
| Is MARL broken? | Not demonstrated. The latest verified-corpus results evaluate prediction only; integration and evaluation on that corpus remain necessary. |
| Why unseen campaigns fail | Strong distribution shift, missing positive training examples for many labels, and limited independent campaigns. Their individual causal contributions have not been isolated. |
| Can CasinoLimit help? | A plausible second prediction corpus. Its suitability for this exact target and for multi-zone deception remains conditional on a file-level audit. |
| Does lookup match the encoders? | The quoted 0.802 baseline cannot be independently located in this checkout. Even if correct, it is a validation comparison, not the final matched test comparison. |
| Is the simulator invalid? | A custom simulator is legitimate; unmeasured transition/payoff assumptions and insufficient independent comparisons limit external validity. |

No available result guarantees a fix, a new state-of-the-art score, or Q1 acceptance. The practical objective is to establish what works under a defensible experiment.

## Scope and verification

I inspected the extraction, reconciliation, split, window-generation, evaluation and MARL interface code and the provenance/correction reports. This was a targeted code audit, not an exhaustive proof that every implementation line is correct. I did not retrain models or re-scan all raw archives in this review.

Checks run now:

- `python -m unittest discover -s camlds_real/tests -q`: **13 passed**.
- `python -m unittest discover -s camlds_encoder/tests -p test_port.py -q`: **9 passed**.
- These checks produced unclosed-file ResourceWarnings. Use context managers when maintaining these readers; the warnings are not evidence that the results are wrong.
- Latest test numbers below are from the Stage-1 report at commit `1457dd5`, verified online in the preceding review. The local checkout inspected earlier was older. Do not confuse its validation dry-run with that report.
- No complete fresh MARL regression suite, gradient audit, or full MARL rerun was performed here. Passing data/port tests does not establish RL correctness.

Primary local evidence:

- [Provenance](camlds_real/PROVENANCE.md)
- [Extractor](camlds_real/extract_camlds.py), especially lines 195–225
- [Execution reconciliation](camlds_real/out/ATTACKMATE_RECONCILE.txt)
- [Audit corrections](camlds_real/DEEP_AUDIT_CORRECTIONS.md)
- [Split specification](camlds_real/split_spec.py)
- [Window construction](camlds_encoder/data.py)
- [Copy/novel definitions](camlds_real/build_sidecar.py)
- [Test scoring](camlds_encoder/evaluate_test.py)
- [Encoder variants](camlds_encoder/variants.py)
- [MARL](Temarl_Test_v1_L1/mappo_cmd.py), [environment](Temarl_Test_v1_L1/env_cmd.py)

## 1. Where CAM-LDS sequences actually come from

### The actual pipeline

```text
AttackBed playbooks containing author-assigned technique metadata
  -> AttackMate execution records (attackmate.json)
  -> authors' extract_attack_logs.py
  -> attack_times.csv
  -> our extract_camlds.py
  -> steps.jsonl + vocabulary + provenance fields
  -> run-level train/validation/test partitions
  -> past-command multi-hot windows
  -> Transformer / GRU / LSTM
  -> next labelled step's technique set
```

The distinction is important: these are recorded attack executions with inherited labels. The predictor does not identify ATT&CK techniques by reading `audit.log`, network packets, or raw command strings. Labels describe the intended operation; the metadata does not independently establish successful execution.

The local provenance pins CAM-LDS **v1**, DOI `10.5281/zenodo.18390561`, and the analysis repository commit `42bbd2cf8409f64a1e6c8fc936c91725e8c558b2`. It deliberately does not silently substitute v2 `18861762`.

### Preprocessing and what the code does

| Step | Code behavior | Meaning |
|---|---|---|
| Read source | `find_csv()` reads semicolon-separated `attack_times.csv`, including from the downloaded archive | Uses released labels rather than invented labels |
| Group | Group rows by run identifier | No windows cross runs |
| Preserve repetitions | Keep all 904 rows and add occurrence indices | Repeated event IDs do not cause data loss |
| Label mapping | Preserve sub-techniques; also reduce each to its parent and deduplicate within a step | 97 source IDs become 81 parent technique classes |
| Preserve sets | One row holds all its technique labels | No artificial order within a multi-label command |
| Provenance | Save `source_row`, original event ID, command, times and run | Predictions can be traced back to their source |
| Split | Hold out runs/scenarios before window construction | Prevents windows from one run being randomly divided across train/test |
| Window | Up to 16 earlier labelled steps, left padded and masked | Input shape is `(batch,16,81)` |
| Target | Next step's multi-hot technique set | Output has 81 labels, not a single exclusive class |

Reconciliation reports **904/904 rows matched**, no unmatched rows, and no source record reused. There are 34 runs, 904 labelled steps and 1,351 technique-label instances. This excludes unlabelled execution records and three labelled sleep records folded into earlier windows by the authors. Therefore “next step” currently means **next retained labelled step**, not necessarily the next shell command among all executed operations.

### Real defect found: ordering terminology and semantics

`extract_camlds.py:197` sorts by `(start,event_id)`. Its comments call `start` reliable execution order. However, the later reconciliation establishes that `start/end` are adjusted log-collection windows. Four S6 runs each have an adjacent pair reversed relative to the AttackMate record order: eight affected positions, four reversed adjacent pairs.

`PROVENANCE.md` also contains inconsistent statements about CSV order and timestamp order. The executable extraction logic and reconciliation must take precedence over the older prose.

**Required correction for a new execution-order study:** join each labelled CSV row to its matched AttackMate record; construct the sequence using the reconciled execution rank; retain collection-window timestamps as separate fields. Preserve all labels and occurrences. Assert unique joins and monotonic ranks, and report the exact changed pairs. Inspect asynchronous commands before claiming a total causal order: launch order does not establish completion order.

Keep the completed study under its original ordering and hashes. Publish a new corpus/protocol version and rerun affected prediction experiments. Do not silently rewrite a previously opened test. This is a correctness repair; the measured impact might be small and is not a promised accuracy gain.

**Thesis wording:** “We predict the next annotated attack step from previously observed technique sets derived from released AttackMate execution metadata.” An operational system still needs a detector to supply those observations.

## 2. What happened to MARL?

The latest `camlds_encoder` run stops at prediction. It creates the representation intended for MARL, but it does not establish a new deception result on the 34-run corpus.

The existing `Temarl_Test_v1_L1/mappo_cmd.py` implements parameter-shared local actors and a centralized MAPPO critic; IPPO uses a local critic. The actor combines local observations with a frozen 64-number history state and selects among six actions. `HistoryBank` calls `model.history()` on past prefixes. The environment replays command sets and uses simulated engagement, movement and exposure rules.

The old label-flattening study and the later command-level `Temarl_Test_v1_L1` study must be distinguished. It is incorrect to call every previous MARL result label-flattened: `env_cmd.py` explicitly limits a command to at most one engaged step. Nevertheless, the newer released 34-run corpus is different from the earlier reconstructed playbooks.

### Concrete integration work

1. Load the verified runs through a dedicated replay adapter. Keep explicit source IDs and termination at sequence exhaustion.
2. Map **technique strings**, not integer positions, to the environment's technique/payoff rows. The encoder now uses 81 labels; the legacy environment imports its older vocabulary. Sharing an integer index would silently associate some labels with the wrong payoff.
3. Audit unsupported labels, host/zone mappings and goal annotations. The scenario-4 firewall is not automatically one of the four defended zones. Document treatment rather than forcing a convenient mapping.
4. Load the selected `allpos` checkpoint through its actual variant class. Check that its `history()` output is reproduced exactly and remains frozen during RL.
5. Test that changing future commands cannot change the current observation or representation; confirm past-only data and target exclusion.
6. Test terminal versus time-limit bootstrap handling, GAE, clipping, actor/critic observation access, value normalization, action validity and common-random-number evaluation. Compare these with the official MAPPO implementation [R1].
7. Run a small smoke experiment, then the frozen multi-seed experiment with the same environment-step budget for every policy. Report the actual step count; earlier 488-update runs used **1,998,848**, not exactly 2,000,000.
8. Include static, random, greedy, NoHistory, OrderFree and the chosen prediction representations. Evaluate MAPPO versus IPPO under identical inputs.

**Verdict:** no evidence here proves the RL optimizer is malfunctioning. The immediate gap is integration, provenance and a clean downstream evaluation. Poor prediction need not imply poor deception because local observations and the reward can still support useful decisions.

## 3. Why unseen campaigns perform badly, and how the test works

### Observed final test results

Micro-F1, mean over seeds then folds; source: [Stage-1 test report](https://raw.githubusercontent.com/roy601/TEMARL/1457dd5/camlds_encoder/out_test/STAGE1_RESULTS.txt).

| Test | Transformer | GRU | LSTM |
|---|---:|---:|---:|
| Variants: all points | 86.1% | 86.6% | 86.3% |
| Variants: novel points | 79.8% | 80.8% | 80.6% |
| Entire S2 held out | 0.0% | 0.2% | 0.5% |
| Entire S3 held out | 13.5% | 13.9% | 16.4% |
| Entire S6 held out | 20.9% | 18.0% | 18.1% |

### Testing procedure checked in code

1. Construct 29 primary folds that hold out one variant, plus three secondary folds holding out S2, S3 or S6 entirely.
2. Select validation runs from the remaining scenarios using the frozen deterministic rule. Exclude them from gradient training.
3. Build windows within runs. At position t, input only preceding retained steps; target the technique set at t.
4. Train each architecture over ten seeds; select checkpoint and decision threshold using validation.
5. Freeze the design, then score saved test logits. Apply sigmoid, threshold, and compute TP/FP/FN. Micro-F1 is `2TP/(2TP+FP+FN)`.
6. Average over seeds within a fold, then folds. Do not interpret these folds as 29 independent campaign families: 18 are S1 variants.
7. Compare encoders using the declared paired analysis. The reported Holm-adjusted p=0.0823 does not establish superiority or equivalence.

`build_sidecar.mark()` calls a test point “copy” if the exact history window **and target** occur in training **or validation**. “Novel” is its complement. Consequently, the earlier claim “novel points cannot be memorised” is too strong: shorter patterns or similar windows may still be memorized. Using validation in this descriptive flag is disclosed; it is not proof of training-set memorization. Report train-only and train-plus-validation overlap separately in a new analysis.

### Causes supported by the corpus

| Evidence | Interpretation | Next diagnostic |
|---|---|---|
| Within-S1 technique-set Jaccard 0.858; across scenarios mean 0.110 | Known variants resemble training; whole scenarios change the problem | Per-scenario, seen-label and unseen-label breakdown |
| Many held-out labels lack positive training examples | Fixed label outputs receive no supervised evidence for those classes | Recompute label support from the actual gradient-training split, after validation removal |
| 34 runs; 18 from S1; 18 labels appear at most three times | Limited independent coverage and rare positives | Train-only frequency/support analysis and grouped learning curves |
| All three encoders fail similarly | Architecture alone is unlikely to be the principal cause | Same-data simple baselines and source-held-out evaluation |

The reported 78.1%, 68.6%, 41.2% values are **seen-label coverage expressed as a recall ceiling under a restricted-output assumption**, not “best possible Micro-F1.” A neural classifier can technically output an unseen label because the head includes it, although it has no positive training evidence. Do not state that this is mathematically impossible. Recompute support after the exact validation split; whole-scenario training-pool counts may overstate coverage.

S2's near-zero score is much worse than label absence alone explains. Ranking metrics, predictions by technique and known-label errors are needed before blaming thresholds or optimization. Do not conclude “no model can predict unseen attacks” from three held-out scenarios.

### Practical improvements, without promised gains

- First repair and quantify execution ordering; freeze a new protocol rather than repeatedly inspecting the same test to pick changes.
- Run frequency, repeat-last and finite-context lookup baselines on identical splits. Measure known-label versus unsupported-label errors.
- Add independently sourced labelled attack behavior and evaluate cross-source holdout. The WILDS experiments demonstrate the importance of evaluating real distribution shift; they do not promise that any specific model solves ours [R2].
- Test Kuwano's external ATT&CK prior in the already-defined comparison. External knowledge can supply evidence unavailable in a small corpus; improvement remains to be measured. Keep original reproduction separate from the next-step adaptation.
- If adding technique-text/semantic features or self-supervised pretraining, treat this as a new experiment with new inputs. CasinoLimit telemetry cannot simply be fed into an 81-label model unchanged.
- Tune training budget using validation learning curves and report updates and wall time [R3]. More epochs cannot supply missing campaign diversity. Repetition is an optimization control, not new evidence.
- For deployment claims, test missed, wrong and delayed observations and preferably replay actual detector outputs. Artificial corruption is a sensitivity experiment, not real-detector validation.

## 4. Can CasinoLimit be used?

**Conditional yes for an additional prediction study. Not yet verified as a direct replacement for the deception environment.**

The official [Zenodo release](https://zenodo.org/records/17256954) is v2, from a CTF with 114 game instances; it accompanies RAID 2025, a conference. It offers `syslogs.zip` (1.7 GB), `syslogs_labels.zip` (19.8 MB), `output.zip` (1.9 MB), `cache.zip` (49.4 MB), and two flow archives. Start the audit with labels and output, then join to system logs. I verified the public listing, not every archive record. The linked Inria datasheet was access-blocked; exact label-event granularity, grouping and topology remain unverified in this review. Confirm licence metadata when acquiring the files.

Audit requirements before training:

1. Hash and inventory the release; read the label schema and annotation method.
2. Establish game/team/session identifiers, chronological event keys and the exact join from labels to commands/processes.
3. Determine whether several log records describe the same action; avoid treating syscall records as independent attacker commands.
4. Preserve multilabel sets and repetitions, with a documented action unit. Unlabelled does not automatically mean benign.
5. Measure usable sequence lengths, technique coverage, duplicates, shared players and challenge overlap.
6. Partition by game/team as supported by the records before window extraction. Keep repeated/shared attack traces together.
7. Train all candidate encoders and simple baselines on the same eligible data; report unsupported labels. For transfer, publish the label intersection and excluded labels rather than silently deleting difficult targets.
8. Treat results as human CTF behavior under one challenge, not arbitrary real-world campaigns.

To use it in MARL, separately verify topology, entry/target information and whether recorded actions remain meaningful under defender interventions. Logs alone do not identify what an attacker would have done after an alternative decoy placement. A replay adapter creates a simulation assumption, not an observed counterfactual. Do not invent zones merely to satisfy the old environment.

## 5. What does the 0.802 lookup claim mean?

**Unverified in this checkout.** I searched the current encoder/comparison code and result reports but did not locate the claimed lookup implementation/report. The values 0.819–0.835 match the older validation dry-run's novel-point neural scores. They are not the final test scores. Obtain the exact lookup file, split, aggregation, fallback rule and prediction outputs before using 0.802 in a thesis table.

A lookup table usually estimates the next label set from matching training contexts, with a fallback for unknown contexts. It can be very competitive on repeated scripted procedures. “No neural training” does not mean “no fitted information”: its entries are derived from training data.

The numerical validation advantage in the quoted comparison is only 1.7–3.3 percentage points. Without paired uncertainty and the same evaluation definition, neither a reliable gain nor a tie is established.

Required fair comparison:

| Check | Requirement |
|---|---|
| Data | Fit lookup counts using gradient-training runs only |
| Context | Declare context length and how command sets are encoded |
| Unknown history | Declare fallback before test evaluation |
| Tuning | Use validation only; match access to validation information |
| Targets | Same next labelled step, same 81 parent labels |
| Reporting | All/novel/copy F1, macro-F1, exact sets, ranking scores where defined, latency and memory |
| Downstream value | Compare deception after giving MAPPO the respective information under matched conditions |

If lookup still matches the neural model, keep that result. A smaller method may be the better engineering choice. Extra neural complexity needs demonstrated accuracy, robustness or downstream benefits; there is no legitimate requirement to make the neural model win.

For a cleaner prediction-to-policy comparison, give every predictor the same-sized technique-score interface, with a common declared transformation. Do not compare one model's rich hidden state to another's hard predictions and attribute all differences to prediction accuracy. Kuwano support rates are not probabilities, may exceed one, and its similarity-one rule uses score pairs; define a finite stable conversion before any RL training. This qualifies the earlier suggestion to pass 81 support values directly.

## 6. How to address the custom-simulator criticism

`env_cmd.py` explicitly states its max/mean technique-to-decoy aggregation is not an empirically measured engagement probability. ATT&CK/D3FEND mappings justify labels and relationships; they do not measure dwell, attraction, movement or exposure probabilities.

A published algorithm in the simulator tests algorithmic competitiveness. It does not independently validate simulator realism. Both are needed.

### Feasible evaluation sequence

1. Publish transition/reward definitions, parameter provenance, budgets and observation access. Keep invented engagement assumptions clearly labelled.
2. Establish sanity tests: fixed-policy reproducibility, no-future leakage, deterministic limits, sequence exhaustion, payoff bounds and capacity accounting.
3. Port the official MAPPO/IPPO implementation [R1] through a documented environment adapter. Compare against the in-house implementation under matched settings. This is an algorithm baseline; it is not reproduction of a honeypot paper.
4. Include static honeypot, random, greedy and centralized controls with equal resources. NoHistory remains a learned policy and must not be called static.
5. Test coordination assumptions: max/mean aggregation, capacity, exposure, lures and attacker movement. Train/evaluate each declared setting appropriately. If the advantage disappears outside one chosen setting, report that dependence.
6. Use multiple seeds and uncertainty estimates rather than only means [R4]. Match evaluation cases across policies; do not claim many replay episodes create many independent campaigns.
7. Audit an independent cyber environment such as CybORG/CAGE [R5] for compatible observations and actions before porting. Its availability makes this practical, but its goals, reward and metrics are not automatically your dwell/depth/protection metrics.
8. Where feasible, run a contained emulation with recorded scripted attacks and measured interactions to calibrate simulator assumptions. Such a test supports those particular conditions, not a claim about Internet attackers generally.

Adding Co-ADAM or Li by name does not resolve this. First establish access to their exact implementation, input requirements and environment semantics. A generic PPO port is not a faithful reproduction of their complete method.

## Research basis and limits of the recommendations

| Ref | Empirical work / implementation | What it supports here | What it does not establish |
|---|---|---|---|
| R1 | Yu et al., *The Surprising Effectiveness of PPO in Cooperative Multi-Agent Games*, NeurIPS 2022; [paper](https://arxiv.org/abs/2103.01955), [official code](https://github.com/marlbenchmark/on-policy) | Practical MAPPO/IPPO controls and implementation checks across cooperative environments | Correctness of our environment's engagement probabilities |
| R2 | Koh et al., *WILDS*, ICML 2021; [paper and experiments](https://proceedings.mlr.press/v139/koh21a.html) | Separate familiar-domain and shifted-domain evaluation | A guaranteed cure for unseen cyber campaigns |
| R3 | Shallue et al., JMLR 2019; [published paper](https://jmlr.org/papers/v20/18-789.html) | Account for optimizer steps and tuning budgets when comparing training | A universal epoch count or a benefit from dataset duplication |
| R4 | Agarwal et al., *Deep RL at the Edge of the Statistical Precipice*, NeurIPS 2021; [official evaluation tools](https://github.com/google-research/rliable) | Report uncertainty and performance across tasks/seeds | Independence of highly similar campaign variants |
| R5 | [CybORG](https://github.com/cage-challenge/CybORG), [CAGE Challenge 4](https://github.com/cage-challenge/cage-challenge-4) | Public independently developed cyber environments to audit and potentially reuse | Automatic equivalence to our honeypot task |
| R6 | CasinoLimit, RAID 2025; [official release](https://zenodo.org/records/17256954) | A concrete public external corpus to inspect | Confirmed compatibility without inspecting its files |

These are empirical papers, released implementations or datasets. Several are conferences; I am not representing them as Q1/Q2 journal publications. No cited paper validates our exact custom pipeline simply because we use its algorithm.

## Ordered action list

1. Preserve completed results and protocols. Synchronize the latest reports before further interpretation.
2. Correct provenance wording and create an execution-rank corpus version; retain the old ordering as sensitivity evidence.
3. Recompute support after validation removal; report seen/unseen-label and per-scenario errors. Correct “recall ceiling” wording and “novel cannot be memorised.”
4. Recover or implement the precisely specified lookup baseline, fit it only on training runs and run a frozen matched comparison. Complete the separately authorized Kuwano evaluation.
5. Integrate the verified corpus with MARL using explicit label-string mappings and checked checkpoint/history interfaces.
6. Run smoke and gradient/terminal/observation checks, then a preregistered multi-seed deception experiment with simple controls and parameter sensitivity.
7. Audit CasinoLimit before adopting it; use it first for independent prediction evidence if its labels permit the task.
8. Add noisy-observation evaluation and an independently implemented controller or compatible external environment. Keep adaptation claims distinct from original-paper reproduction.

**Final verdict:** the strongest immediate fixes are representation/order correctness, verified-corpus MARL integration and properly matched simple baselines. The hardest unsolved issue is independent campaign diversity. It cannot be repaired by selecting another encoder, repeating the same corpus, or renaming a validation score. If simple predictors suffice but history improves defense, that is a defensible result when demonstrated on the corrected pipeline.
