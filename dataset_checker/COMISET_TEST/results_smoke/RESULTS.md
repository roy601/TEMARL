# COMISET Sequence Audit

Status: PARTIAL SMOKE TEST - NOT FINAL COUNTS

These are host/process telemetry sequences, NOT confirmed independent attack runs.
Rule-assigned ATT&CK labels are not proof of attacker execution or ground truth.

| Counting definition | Sequences | Mean length | Median | Maximum | >25 | >30 |
|---|---:|---:|---:|---:|---:|---:|
| raw_events | 0 | 0.00 | 0 | 0 | 0 | 0 |
| collapsed_label_steps | 0 | 0.00 | 0 | 0 | 0 | 0 |
| unique_techniques | 0 | 0.00 | 0 | 0 | 0 | 0 |
| unambiguous_collapsed_sequences | 0 | 0.00 | 0 | 0 | 0 | 0 |

Use the unambiguous_collapsed_sequences row for single-technique token chains.
Raw events retain genuine repeated labels but may greatly inflate apparent length.
Collapsing identical consecutive labels can also merge distinct real executions.
Neither length definition proves the number of actual executed attack steps.
Multi-label events are retained as sets; no arbitrary technique ordering is invented.
No host/user fallback grouping, parent-technique merging, padding or synthetic continuation.
Equal timestamps use source-line order, which is not evidence of causal order.
Only timezone-aware timestamps from 2020 through 2025 are retained (legacy audit window).
Cross-process/cross-host campaigns are not reconstructed. Related sequences must stay together in any later train/test split.

## Processing Counts

```json
{
  "lines_read": 1000,
  "no_valid_technique": 1000
}
```
