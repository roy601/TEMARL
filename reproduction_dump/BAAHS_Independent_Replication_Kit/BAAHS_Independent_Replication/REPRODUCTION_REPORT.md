# Reproduction report — BAAHS independent approximation

**Assessment:** INDEPENDENT IMPLEMENTATION EXECUTED. ORIGINAL PAPER REPRODUCTION **NOT ACHIEVED**.

## Verification outcomes

| Gate | Verdict | Evidence |
|---|---|---|
| Journal, DOI | PASS | IEEE Access, DOI 10.1109/ACCESS.2026.3740819 |
| Main architecture | PARTIAL | 11-state HMM, five objectives, Thompson-inspired placement from published abstract |
| Original authors' code | FAIL | Not included or located as verified research source |
| Original topology and trajectories | FAIL | Not available; independent synthetic generation |
| Original equation-level correspondence | UNVERIFIED | Full mathematical methods not accessed |
| Original experimental seeds | FAIL | New deterministic seeds used |
| Faithful published baselines | UNVERIFIED | Independent proxy baselines only |
| Runnable experimental software | PASS | Python 3.13 and NumPy 2.3.5 test execution completed |
| Tests | PASS | Seven unit/end-to-end tests passed at packaging time |
| Real experimental output from this project | PASS | 50+50 seed CSV/JSONL outputs under `examples/standard_50seed_run/` |
| Numerical agreement with reference | FAIL | Heldout BAAHS 28.05% vs 25.89%; strongest baseline 34.41% vs 15.32% |
| Scientifically faithful paper reproduction | FAIL | Missing original simulator, algorithms and baselines |

## Traceable results

Executed with `python -m baahs.cli run --steps 80 --seeds-per-batch 50 --max-batches 1 --holdout-seeds 50 --output examples/standard_50seed_run`.

| Split | Method | Per-seed mean |
|---|---|---:|
| Development, 50 seeds | baahs_independent | 29.22% |
| Development, 50 seeds | hmm_greedy | 34.15% |
| Heldout, 50 seeds | baahs_independent | 28.05% |
| Heldout, 50 seeds | hmm_greedy | 34.41% |

The published 25.89/15.32 values are stored only under `PAPER_REFERENCE` and only compared during evaluation reporting. They do not appear in the attacker transition, HMM, modes, policy selection, or reward update.

## Meaning of repeat-until-match

With `--repeat-until-match`, all development batches are logged and any match is marked **exploratory**; a separate, disjoint, fixed held-out evaluation runs regardless. This does **not** reconstruct the paper's code or environment. We explicitly reject post hoc cherry-picking of a single seed, hidden parameter-tuning against the target, or reporting a coincidence as author-code reproduction.

**Conclusion:** The toolkit is usable as a *research prototype and comparative simulation harness*. It is not yet evidence that TEMARL outperforms the actual BAAHS method in the original BAAHS environment.
