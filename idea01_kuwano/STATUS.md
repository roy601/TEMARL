# Idea 01: status log

Progress against `spec.ORDER_OF_WORK`. The protocol itself (`PROTOCOL.md`, `spec.py`) is
frozen and is not edited; this file only records what has been done.

| Step | What | Status | Evidence |
|---|---|---|---|
| 1 | Freeze the protocol and commit it with its code | **done** 2026-11-03 | commit c1fae6a; `python idea01_kuwano/spec.py` → PASS |
| 2 | Implement the Kuwano conditions and context baselines; tests pass; reproduction hashes unchanged | **done** 2026-11-03 | `run_kuwano.py`; 8/8 tests in `idea01_kuwano/tests`; 16/16 in `kuwano_repro/tests`; reproduction outputs unchanged |
| 3 | Run them; write per-fold outputs and SHA-256; do not open test numbers | **done** 2026-11-03 | `sealed/predictions.jsonl`, SHA-256 (LF) `65f309988b61de24e1e3fe74f92079fe4edbbbe7fc2c7bd596b0b64ebfca1ccb`, 8,968 predictions; two runs byte-identical |
| 4 | Port TEMARL's encoder pipeline to `camlds_real` (B2); freeze its configuration; record the GRU/LSTM decision | open | |
| 5 | Train and evaluate TEMARL; open all test numbers together; apply Section 7 | open | |

Precondition **B1** (commit hash of the CAM-LDS analysis repository) is still open.

## Step 3: what was produced, and what was not

- **Produced:**
  - per condition and fold, the threshold selected on **validation**, with the validation
    micro-F1 at every grid value (`out/validation.json`);
  - per **test** prediction point, the predicted label set and the top-10 ranking
    (`sealed/predictions.jsonl`).
- **Not produced:** any test metric. Test points were built without their targets, so the
  sealed file contains none.

Conditions: K-A-val, K-A-pub, K-B-val, each at W = 16 and with the full history; repeat
previous; label prior. Point counts match the protocol: 790 variant and 331 scenario
prediction points per condition.

## Observations from validation (to be reported, not acted on)

- **Thresholds at a grid edge.** K-B-val selected the smallest Kuwano value (0.05) in 3 folds
  at W = 16 and in 4 folds with the full history. The label prior selected the smallest of our
  values (0.1) in 25 of 32 folds. Under the frozen protocol, edge selections are reported and
  **no grid is extended**.
- **K-A-val** selected 1.0 in 27 folds and 0.75 in 5; never at an edge.
- **Similarity 1 on test inputs:** 2 test points for each K-A condition, all in the
  scenario-held-out family, handled by the declared limit rule. None for K-B.
