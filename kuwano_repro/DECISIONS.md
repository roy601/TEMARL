# Decisions

The paper leaves these points unspecified. Each one is settled by evidence (the audit,
or by matching Tables 5–7), never by preference. An entry is closed only with the
evidence that closed it. Nothing below may be decided while writing method code.

| # | Open question | Where the paper is silent | How it will be settled | Status |
|---|---|---|---|---|
| D1 | Which ATT&CK version | Says v11 (2022-04-25) but accessed the site 2023-01-31 (v12.1 live) | Count groups and techniques in each version; the paper says 133 and 191. Then whichever version reproduces Tables 5–7 | OPEN |
| D2 | Group × technique matrix: what counts as "used" | Only "techniques which they have used" (§5.1) | Audit: direct group `uses` technique relations; sub-technique uses rolled up to parent or not; revoked/deprecated objects; techniques used only through software | OPEN |
| D3 | Sub-technique roll-up | 191 implies parent techniques only; never stated | Audit the CISA tables (they list sub-techniques) and the STIX counts | OPEN |
| D4 | Exact technique list and order per advisory | Only "in tactic order" (§6.2); AA22-138B drops one pre-initial-access technique | Audit each advisory's ATT&CK table; the counts must be 26, 13→12, 13; order within a tactic tested against the tables | OPEN |
| D5 | Candidate universe ("after the most late-stage tactic observed", §4.1) | Not in Algorithm 1. Multi-tactic techniques and same-tactic inclusion unstated | Table 5 row 1 has 173 = 191 − 17 Recon/ResDev − 1 input; derive the rule and check it on all 48 rows | OPEN |
| D6 | Weight when Similarity = 1 (d = 0, so 1/d is undefined) | Not handled | Audit whether SDC = 1 occurs at all in the test runs; if it does, test the candidate rules against the tables | OPEN |
| D7 | Threshold comparison: `>` or `>=` 0.17 | Symbol lost in the PDF; text says "higher than" | Test both against the tables | OPEN |
| D8 | Tie-breaking in the top-k sort | Not specified | Audit whether ties straddle the k = 60 boundary with non-zero similarity; if they do, test the candidate rules | OPEN |
| D9 | Are input techniques excluded from the output? | Not stated | Table 5 row 1: TP + FN = 25 = 26 − 1, so the input is excluded from positives; confirm it is excluded from candidates too | OPEN |
