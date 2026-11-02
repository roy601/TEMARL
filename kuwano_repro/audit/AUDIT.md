# Phase 1 audit: inputs

Produced by `audit/audit_inputs.py`; full output in `audit/AUDIT_OUTPUT.txt`. Run on
the files whose SHA-256 match `reference/REFERENCE_MANIFEST.json` (the GPU PC's copy
verified identical, 7/7). Date: 2026-11-02.

Every number below comes from the script, not from reading the paper.

## 1. Which ATT&CK version (D1): v11, and 11.0 vs 11.3 makes no difference

| | v11.0 | v11.3 | v12.1 | paper |
|---|---|---|---|---|
| Live parent techniques | **191** | **191** | 193 | 191 |
| Groups (live / deprecated / revoked) | 131 / 1 / 5 | 130 / 2 / 5 | **133** / 9 / 5 | 133 |
| Live groups using ≥ 1 technique | 128 | 127 | 130 | – |
| Cold-start counts (p. 810) reproduced | **yes, 5/5** | **yes, 5/5** | no (T1497: 5 vs 6) | – |

- v12.1 is ruled out: it has 193 techniques and gets one cold-start count wrong.
- The advisories themselves link to `attack.mitre.org/versions/v11/`.
- v11.0 and v11.3 give the **same technique set for every group**. The only difference is
  that v11.3 deprecates one group, G0141. Since G0141 is in v11.0 and v11.3 has 130 live
  groups, v11.0 is used and v11.3 is redundant.
- **The paper's "133 groups" matches no v11 count.** This is harmless for the method: a
  group with no techniques has SDC = 0 and weight 0, so it can never contribute. It only
  matters for top-k tie-breaking (section 5). Recorded as an unexplained discrepancy.

## 2. What counts as "used" (D2, D3): direct uses, sub-techniques rolled up to parent

Definition tested: live groups, direct `uses` relationships to live techniques, with each
sub-technique counted as its parent. Techniques reached only through software are excluded.

- **Cold-start counts, p. 810:** T1129 = 0, T1497 = 6, T1039 = 7, T1095 = 7, T1029 = 1.
  All five are reproduced exactly. Without roll-up, T1497 would be 1, because 5 of its
  6 groups use only its sub-techniques.
- **Table 1 excerpt, p. 806.** The table is printed one row shifted: its header cell "G0018"
  is really the first data row. Realigned:

  | Group | Paper | With roll-up | Without roll-up |
  |---|---|---|---|
  | G0018 admin@338 | 10101 | 10101 ✓ | 00101 ✗ |
  | G0006 APT1 | 01000 | 11000 ✗ | 00000 ✗ |
  | G0026 APT18 | 10001 | 10001 ✓ | 00001 ✗ |
  | G0007 APT28 | 11101 | 11101 ✓ | 00101 ✗ |
  | G0060 BRONZE BUTLER | 10101 | 10101 ✓ | 00101 ✗ |

  Roll-up matches 4 of 5 rows; without it, none match. The one miss is APT1 × T1059:
  APT1's only link in that family is T1059.003, so roll-up gives 1 but the paper shows 0.
  **Unexplained single-cell discrepancy**, recorded and not acted on.
- 29 group→technique links point to revoked or deprecated techniques. They are excluded.

## 3. Test sequences (D4, D9)

Technique ids are read from **link targets**, not from the visible text, because the visible
text contains typos. Each technique is counted once as its parent, in first-occurrence page order.

| Advisory | Distinct parents | Pre-access dropped | Used | Paper |
|---|---|---|---|---|
| AA22-277A | 26 | – | **26** | 26 ✓ |
| AA22-138B | 13 | T1588 (Resource Development) | **12** | 13 (12) ✓ |
| AA22-174A | 13 | – | **13** | 13 ✓ |

Order used:

- **277A:** T1078 T1047 T1059 T1129 T1569 T1543 T1036 T1070 T1497 T1562 T1574 T1016 T1033 T1049 T1057 T1082 T1083 T1021 T1560 T1039 T1074 T1095 T1105 T1090 T1029 T1567
- **138B:** T1059 T1203 T1505 T1068 T1222 T1070 T1003 T1560 T1071 T1573 T1090 T1105
- **174A:** T1190 T1059 T1053 T1505 T1036 T1021 **T1056 T1560** T1071 T1573 T1105 T1571 T1090

Checks:

- The paper's §5.3 example inputs for 277A are T1078, T1047, T1059, T1129. These are the
  first four above. ✓
- The paper's five unpredictable 277A techniques (T1129, T1497, T1039, T1095, T1029) are all
  in the 277A list. ✓
- **The paper's 13 for 138B needs T1070**, which sits as a second link inside the Defense
  Evasion cell. Reading only the first technique per cell would give 12.

Faults in the source pages, all handled:

- **174A, Collection:** the two rows have their visible text and link targets swapped. The
  row reading "Archive via Utility [T1560.001]" links to T1056/001, and the reverse.
  Following the links gives T1056 then T1560; following the visible text gives T1560 then
  T1056. Both are Collection, so this is part of D4 and is settled in validation.
- **174A:** "Encrypted Channel [1573.001]" is missing its "T"; the link is correct (T1573/001).
- **174A:** the Credential Access row has no technique in the original. Checked in the raw HTML.
- **138B:** the Exfiltration row is labelled TA0004 (that is Privilege Escalation's id) and is empty.
- **277A:** three rows show a parent id but link a sub-technique, or the reverse (T1059 →
  .003, T1070 → .004, T1560.001 → T1560). The parent is the same either way, so this has no effect.
- **277A:** the Wayback server sent this page gzip-compressed. `download.py` now stores it decoded.

## 4. Tactics and the candidate universe (D5)

v11.0 has 14 tactics. **25 parent techniques belong to more than one tactic.** In the test
sequences these are T1078, T1543, T1497 and T1574 (277A), and T1053 and T1056 (174A).
The 17 pre-access techniques (10 Reconnaissance + 7 Resource Development) belong to no
post-access tactic, so excluding them is unambiguous.

Table 5 row 1 has TP + FP + TN + FN = 173 = 191 − 17 − 1. This is consistent with
"exclude pre-access techniques and the input itself" at step 1. The rule for later steps
(same-tactic inclusion, and which tactic a multi-tactic technique belongs to) must be derived
from all 48 rows in validation. That needs the method, so D5 stays open.

## 5. Edge cases on the actual test trajectories (D6, D8)

- **SDC = 1 never occurs**, on any step of any advisory. The undefined 1/0 weight is
  never reached, so D6 is closed with no effect.
- **Ties at the k = 60 boundary occur often**: at 23 of 48 steps there are tied groups with
  non-zero similarity on both sides of the cut, for example "3 of 6 tied groups kept". So
  **the tie-break rule changes the output** and must be settled against Tables 5–7. The
  candidates are STIX file order, group-id order, and group-name order. The excerpt in
  Table 1 (admin@338, APT1, APT18, APT28, BRONZE BUTLER) is in name order, which makes that
  the leading candidate. A five-row excerpt is suggestive, not proof.

## Not yet audited

- The 8 manual cisa.gov cross-checks (current pages, PDFs, STIX). They were never fetched,
  so the snapshot-versus-current comparison is still pending. Each page's "Last Revised"
  date is before the snapshot, which suggests they agree.
