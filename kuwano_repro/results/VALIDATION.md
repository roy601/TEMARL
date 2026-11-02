# Phase 4: validation against Tables 5–7

`python validate.py --detail` → `results/VALIDATION.txt` (full ranking of all settings).

## Result

**Prediction, TP, FP and FN match the paper in all 48 rows. TN matches in 44 of 48**;
in the other 4 it is exactly 1 lower than the paper's.

So **recall reproduces exactly at every input count of all three advisories**.
Specificity and accuracy reproduce exactly in 44 rows; in 4 rows they are off by one TN.

## Settings searched

156 settings: tie-break (name, id, stix) × threshold (`>=`, `>`) × candidate universe
(any_ge, all_ge, any_gt, all_gt, everything) × observed tactic (listed, min, max) × 174A
order (links, visible text). Settings where observed tactic has no effect are not repeated.
A row counts as matched only if all five of its numbers match.

| Rank | Rows matched | Wrong cells | Setting |
|---|---|---|---|
| 1 (4 equivalent) | **44 / 48** | 4 | tie = **name**, universe = **any_ge**, observed = listed or min, threshold `>=` or `>`, 174A = **visible text** |
| 2 | 43 / 48 | 7–8 | same, but 174A = links |
| 3 | 40 / 48 | 24 | tie = id |
| … | ≤ 37 | ≥ 32 | tie = stix, observed = max, other universes |

The tie-break is the most decisive switch: name order beats id order by 4 rows and STIX
order by 8. It is also the order the paper's own Table 1 excerpt is printed in.

## The 4 remaining cells

| Advisory | Input | TN paper | TN ours | Everything else |
|---|---|---|---|---|
| AA22-277A | 2 | 112 | 111 | equal |
| AA22-277A | 3 | 126 | 125 | equal |
| AA22-277A | 4 | 126 | 125 | equal |
| AA22-277A | 5 | 121 | 120 | equal |

These are exactly the steps where the latest observed tactic is Execution (inputs 2–5 are
T1047, T1059, T1129, T1569 after T1078). Rows 1 and 6–25 match. So the paper's candidate
set held **one more technique** than ours at those steps, and it was neither predicted nor
a true positive. The only techniques that fit are those whose last tactic in v11.0 is
Initial Access and that are never recommended at inputs 2–5: **T1195, T1199 or T1200**.
The paper must have placed one of them at Execution or later. The counts cannot tell which,
and v11.0 and v12.1 give these techniques the same tactics, so it is not a version effect.
This changes no prediction; it is recorded as an unexplained discrepancy.

## What the data cannot distinguish

- **`>=` vs `>` (D7):** identical on every row. No support rate on any step equals 0.17
  exactly (checked in exact arithmetic; the closest is 5.7 × 10⁻⁶ away), so the choice
  has no effect. Reported as `>=` ("higher than a threshold" read
  inclusively); either gives the same numbers.
- **Observed tactic "listed" vs "min" (D5):** identical on every row. These test sequences
  never contain a multi-tactic technique where the two rules differ in effect. "listed"
  (the tactic the advisory files it under) is kept as the more faithful reading.
