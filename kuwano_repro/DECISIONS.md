# Decisions

The paper leaves these points unspecified. Each one is settled by evidence (the audit,
or by matching Tables 5–7), never by preference. An entry is closed only with the
evidence that closed it.

Evidence: `audit/AUDIT.md` (§ = section) for D1–D3, D6; `results/VALIDATION.md` for D4, D5, D7, D8.

| # | Question | Status | Decision and evidence |
|---|---|---|---|
| D1 | Which ATT&CK version | **CLOSED** | **v11.0.** 191 live parents; reproduces all 5 cold-start counts (v12.1 fails one); the advisories link to `/versions/v11/`; v11.3 gives identical technique sets per group but deprecates G0141 [audit §1] |
| D2 | What counts as "used" | **CLOSED** | Live groups, direct `uses` to live techniques; software-mediated techniques excluded; links to revoked or deprecated techniques excluded. 5/5 cold-start counts, 4/5 Table 1 rows [audit §2] |
| D3 | Sub-technique roll-up | **CLOSED** | **Roll up to parent.** Without it, T1497 = 1, not 6, and 0/5 Table 1 rows match [audit §2] |
| D4 | Technique list and order per advisory | **CLOSED** | Ids from link targets, deduplicated to parents in first-occurrence order, pre-access dropped: 26 / 12 / 13 [audit §3]. 174A: **visible-text order** (T1560 before T1056) gives 12/12 rows; link order gives 11/12 [validation] |
| D5 | Candidate universe | **CLOSED** | **any_ge:** a technique (not yet observed) is a candidate if *any* of its tactics is at or after the latest observed tactic, with each observed technique counted at the tactic its advisory lists it under. Prediction/TP/FP/FN match 48/48 rows [validation]. "min" gives identical numbers |
| D6 | Weight when Similarity = 1 | **CLOSED, no effect** | SDC = 1 never occurs on any test step [audit §5]. The code raises if it ever did |
| D7 | `>` or `>=` 0.17 | **CLOSED, no effect** | Identical results on all 48 rows; `>=` used [validation] |
| D8 | Tie-break in the top-k sort | **CLOSED** | **Group name, case-insensitive** (then id). 44/48 rows, against 40 for id order and 36 for STIX order; it is also Table 1's printed order [validation] |
| D9 | Inputs excluded from the output | **CLOSED** | Excluded from candidates and positives; reproduced by the 48-row match |

**Unexplained discrepancies in the paper**, recorded and not acted on:

1. "133 groups": v11.0 has 131 live groups (128 using any technique). Harmless: a group
   with no technique cannot contribute.
2. Table 1, APT1 × T1059: the paper shows 0; v11.0 has APT1 → T1059.003, which rolls up to 1.
3. AA22-277A inputs 2–5: the paper's TN is one higher than ours. Its candidate set held one
   extra technique while the latest tactic was Execution, most likely one of T1195, T1199 or
   T1200 placed at a later tactic. No prediction is affected.
