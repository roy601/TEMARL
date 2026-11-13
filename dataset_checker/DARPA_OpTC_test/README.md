# DARPA OpTC local event audit

Run from this folder:

```powershell
python run_pipeline.py --input-dir "C:\path\to\raw_dataset"
```

Keep ../audit_core.py alongside this project. Python 3.10+; this pipeline uses only the standard library.

Only explicit ATT&CK event labels with a host and valid timestamp enter sessions. No process-name guesses, generated examples, downloads, or row-number timestamps are used. Files and archive members are isolated; a scenario field further partitions each file. Default boundaries are a 30-minute idle gap and four-hour duration. Simultaneous different labels remain ambiguous. Consecutive equal label sets are collapsed.

Supported inputs: CSV, JSON objects/arrays, JSONL/NDJSON, JSON lines in .log, gzip, and supported members of tar/zip archives. Nested archives and non-JSON text logs are counted as unsupported. Archives are never extracted. ISO timestamps without an offset assume UTC; numeric Unix seconds/milliseconds/microseconds/nanoseconds are supported for 2000-2099.

The old scenario_manifest.csv and generated intermediates are deliberately excluded: this pipeline does not validate planned scenario order or reconstruct campaigns from arbitrary metadata. For verified planned scenarios, retain them as a separate evidence source. Unlabelled telemetry needs an independently validated annotation process.

Results are in output_verified: events.json preserves file and record provenance, sequences.json includes ordered and ambiguous candidate sessions, audit.json reports exclusions, and statistics.txt/json summarizes ordered candidates. Old output folders are historical and must not be mixed with new results. An empty result means insufficient supported input evidence, not that the dataset contains no attacks.

