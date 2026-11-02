# Decisions

The paper leaves these points unspecified. Each one is settled by evidence (the audit,
or by matching Tables 5–7), never by preference. An entry is closed only with the
evidence that closed it. Nothing below may be decided while writing method code.

Evidence for every row: `audit/AUDIT.md` (sections in brackets).

| # | Question | Status | Decision and evidence |
|---|---|---|---|
| D1 | Which ATT&CK version | **CLOSED** | **v11.0.** 191 live parents; reproduces all 5 cold-start counts (v12.1 fails one); the advisories link to `/versions/v11/`; v11.3 gives identical technique sets per group but deprecates G0141 [§1]. Paper's "133 groups" matches no v11 count; harmless except for tie-breaking (D8) |
| D2 | What counts as "used" | **CLOSED** | Live groups, direct `uses` to live techniques; software-mediated techniques excluded; links to revoked or deprecated techniques excluded. Reproduces 5/5 cold-start counts and 4/5 rows of Table 1 [§2]. APT1 × T1059 differs (unexplained, one cell) |
| D3 | Sub-technique roll-up | **CLOSED** | **Roll up to parent.** Without it, T1497 = 1, not 6, and 0/5 Table 1 rows match [§2] |
| D4 | Technique list and order per advisory | **PARTLY CLOSED** | Lists closed: ids from link targets, deduplicated to parents in first-occurrence order, pre-access dropped. Gives 26 / 12 / 13 exactly [§3]. **Open:** in 174A, T1056 then T1560 (links) or T1560 then T1056 (visible text). Settle against Table 7 |
| D5 | Candidate universe after the latest observed tactic | OPEN | Row 1 of Table 5 fits 191 − 17 pre-access − 1 input [§4]. Same-tactic inclusion and multi-tactic assignment (6 test techniques are multi-tactic) need all 48 rows |
| D6 | Weight when Similarity = 1 | **CLOSED, no effect** | SDC = 1 never occurs on any test step [§5] |
| D7 | `>` or `>=` 0.17 | OPEN | Test both against the tables |
| D8 | Tie-breaking in the top-k sort | OPEN, **matters** | Non-zero ties straddle k = 60 at 23 of 48 steps [§5]. Candidates: name order (suggested by Table 1's excerpt), group-id order, STIX file order |
| D9 | Inputs excluded from the output | **PARTLY CLOSED** | Excluded from positives (TP + FN = N − input in all 48 rows). Exclusion from candidates is confirmed together with D5 |

**Unexplained discrepancies in the paper**, recorded and not acted on:

1. "133 groups": v11.0 has 131 live groups (128 using any technique).
2. Table 1, APT1 × T1059: the paper shows 0; v11.0 has APT1 → T1059.003.
