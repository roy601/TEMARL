# Mordor metadata audit

## Event annotation (enabled by default)

`event_mapper.py` maps supported provider/event/field combinations to ATT&CK
behavior candidates before reconstruction. It supports Sysmon process creation,
Run/RunOnce writes, SSH-client network connections, Windows Security process
creation, scheduled-task creation and remote-interactive logons, PowerShell
script blocks/download expressions, and service installation. See the source
for all predicates. Event IDs or network ports alone do not create annotations.
Generic traffic, PCAPs, arbitrary process names, and unmatched event schemas
are not automatically classified. These rules are not a complete detector.

The standard command now runs both explicit-label and event-annotated B1/B2:

```powershell
python .\Mordor_test\run_pipeline.py --repo ".\Mordor_test\data\Security-Datasets"
```

Annotated results are under `output_verified/raw_telemetry/annotated/`.
`events.json` contains rule IDs, mapper version, evidence fields, ATT&CK links,
and file/record provenance. `annotation_coverage.json` lists rule-match counts
and input provider/event counts. `metadata_comparison.json` lists overlap,
expected-but-unobserved IDs, and annotations outside capture inventories.
This is a consistency check, not independent detection validation or recall.
Metadata labels never seed event annotations. Explicit and rule-derived event
provenance remain distinguishable. B3 is still the optional original baseline.

Empty representations show a short status instead of an all-zero box; JSON
retains actual zero counts. No positive result is guaranteed or fabricated.

Real-sample validation: LSASS campaign 01 host archive, 53,698 records,
237 rule-annotated events, eight technique IDs, one 17-step candidate under
default session windows. This is not a claim of 17 verified attack actions.

Optional inference: add `--infer-techniques` for **B3**, a separate hypothesis
experiment stored in `raw_telemetry/experiment_b3_inferred`. Four transparent
rules require Sysmon process creation, executable identity, and command-line
evidence for systeminfo, whoami, tasklist, or cmd /c /k. Rule IDs, matched fields,
and ATT&CK references are saved in events.json. This is limited behavior mapping,
not a validated detector; benign administration can match. Inferred events never
enter the explicit-label B1/B2 results. See behavior_rules.py for exact predicates.

The default runner now also executes raw telemetry reconstruction. Use
`--no-logs` for metadata only. ZIP, gzip, tar and supported JSON/CSV members
are read in place, without archive extraction. Raw outputs are under
`output_verified/raw_telemetry`: `file_coverage.json`, `audit.json`,
`events.json`, `sequences.json`, and B1/B2 reports. Files uniquely referenced
by the same metadata capture may share sessions, still separated by host
and time windows. Untagged telemetry is counted but not assigned metadata
techniques. Packet captures and unsupported formats are audited as skipped.

Validation against the official LSASS campaign 01 host archive parsed
53,698 records with host and timestamp, but found zero explicit event-level
ATT&CK labels. This is a verified sample result, not a claim about all logs.

Run: `python run_pipeline.py --repo "C:\path\to\Security-Datasets"`.
Without --repo, reads the local data folder. Requires Python 3.10+ and PyYAML.

No downloads, synthetic fallback data, or telemetry heuristics are used.
Legacy _evaluation_steps examples are excluded. attack_mappings are inventories,
not chronological chains. Only valid simulation.steps produce declared-order
sequences; these describe a plan, not verified execution. Duplicate step IDs
are ambiguous. Missing IDs preserve the declared list order. Invalid steps
prevent claiming a complete ordered chain.

Results go to output_verified: sequences.json, capture_inventory.json,
extraction_audit.json and statistics.txt/json. Historical output folders are
not authoritative. Zero sequences means no supported declared-order evidence
in these inputs, not that all Mordor telemetry lacks attacks.
