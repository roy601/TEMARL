# Splunk Attack Data audit

Requires Python 3.10+, Git, and Git LFS. Python dependencies, regression tests,
repository cloning, full LFS download, and the audit are handled by:

```powershell
& .\Splunk_Attack_Data_test\run_full_audit.ps1
```

Run from the extracted code root. The script downloads the full current working
snapshot into `Splunk_Attack_Data_test/data/attack_data`. A shallow clone omits
old Git history, not datasets. Existing checkouts are audited at their existing
revision; they are never reset. LFS include/exclude filters are cleared for the
pull. Failed downloads or missing tracked files stop the script. Git and Git LFS
must already be installed. No Splunk server or Splunk replay dependencies are needed.

Direct run after downloading:

```powershell
python .\Splunk_Attack_Data_test\run_pipeline.py --repo .\Splunk_Attack_Data_test\data\attack_data --output-dir .\Splunk_Attack_Data_test\output_verified
```

## Interpretation

Metadata coverage counts distinct ATT&CK IDs per YAML capture, with the example
TEMPLATE.yml excluded. Metadata list order is never treated as execution order.
Event labels come from explicit technique fields, including Sysmon RuleName;
process names, command lines, folder names and capture labels are not propagated
into event annotations. Zero labelled sequences remains a possible valid result.

Sessions group by uniquely mapped YAML capture plus host. Unmapped or multiply
mapped files stay isolated; unmapped ZIP members are isolated individually.
Sort by event timestamps, split gaps over 30 minutes, cap session duration at
4 hours, and collapse consecutive equal label sets. A-B-A remains A-B-A.
Naive ISO timestamps assume UTC. Missing host/time excludes a labelled event
from reconstruction. Configure --session-gap-minutes and --max-session-hours.

B1 reports sessions containing only single-label steps. B2 retains all candidate
sessions as ordered label sets, including B1 sessions. Labels inside a set have
no established internal order. Neither representation proves a campaign or
successful malicious execution. B1 step counts, B2 set-step counts, and metadata
coverage lengths must not be treated as equivalent CAM-LDS sequence lengths.

## Coverage and output

The entire datasets tree is visited without a sample or technique filter.
JSON objects/arrays, JSONL/NDJSON, CSV, Windows Event XML, and corresponding
ZIP/GZIP text members are supported. Files are read, never executed or replayed.
Arbitrary plaintext, binary EVTX, nested archives, and TAR archives are not
decoded; exclusions and parse gaps are reported. Large JSON arrays and collected
labelled events are held in memory. Allow sufficient RAM for the full repository.

With --output-dir (as used by the script), outputs are:

- statistics.txt / statistics.json: metadata, B1, B2, and coverage status.
- sequences.json: all sessions, including ambiguous steps and source references.
- capture_inventory.json and session_audit.json: provenance and exclusions.
- intermediate/file_coverage.json: per-file parser counts and missing references.
- intermediate/scan_audit.json: aggregate scan counts.
- intermediate/splunk_attack_data_ground_truth.json: explicit labelled events;
  the legacy filename does not imply independently validated ground truth.
- repository_commit.txt: revision recorded by the PowerShell script.

--no-logs intentionally performs metadata-only scanning. Without --output-dir,
intermediate data uses the existing data directory and reports use output_verified.
Inspect coverage_status and file_coverage.json before claiming complete telemetry
coverage. An unreadable/quarantined file is a coverage gap, never a successful read.
The code does not alter antivirus settings or copy raw commands/scripts to reports.

Source: https://github.com/splunk/attack_data#anatomy-of-a-dataset-
