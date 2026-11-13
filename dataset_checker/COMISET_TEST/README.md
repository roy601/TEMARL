# COMISET_TEST

Standalone Python 3.10+ tool; no external packages, no training, no network downloads.
Reads Comiset23_Lab_Environment_Dataset.zip directly. The inspected 4.9 GB ZIP
contains dataset_comillas2.json (159,730,026,735 uncompressed bytes).
No full extraction is performed, but the complete uncompressed stream must be
decompressed and read. This is a substantial scan; no runtime is promised.
SQLite stores only usable labeled events on disk. Allow free space for that
database, its sorting index and the output sequences. RAM scales with the largest
individual process sequence and the number of sequences, not the full archive.

## Run on the lab PC

Extract comiset_audit_update.zip on the remote PC (or copy this folder), and
download the original dataset ZIP there. Keep the dataset ZIP compressed.
Open PowerShell in the extracted COMISET_TEST folder:

```powershell
python -m unittest -v test_analyzer.py
python -u analyze_comiset.py --zip "C:\path\to\Comiset23_Lab_Environment_Dataset.zip" --output results_full
```

Replace only the ZIP path. Use a fresh output folder for each run. No administrator
permissions or antivirus exclusions are needed by this tool. Never execute dataset
contents. ZIP members are streamed, not extracted to arbitrary filesystem paths.

Optional quick check (NOT final dataset statistics):

```powershell
python -u analyze_comiset.py --zip "C:\path\to\Comiset23_Lab_Environment_Dataset.zip" --max-lines 100000 --output results_smoke
```

## Outputs

- RESULTS.md: two-column table of every observed sequence length and its count,
  sorted by numeric length (no bins or top-N cutoff).
- sequence_length_counts.csv: the same grouped two-column table.
- statistics.json: machine-readable counts and processing audit.
- sequence_lengths.csv: per-sequence lengths.
- sequences.jsonl: timestamped labels, source line references, collapsed labels.
- events.sqlite: intermediate retained labeled records.

The grouped table defaults to raw labeled event counts per host/process after
filtering and deduplication. Repeated labels count; a multilabel event counts once.
To count consecutive-label-collapsed steps instead, add
`--length-metric collapsed_label_steps`. The selected definition and full/partial
scan status appear in RESULTS.md and statistics.json. Zero-count lengths are omitted.
Detailed averages and threshold metrics remain in statistics.json.

## Interpretation

The 37.4 figure cited in the conversation was NOT established for COMISET by this
tool. Do not assume it applies here.

Grouping is host + process GUID. Missing identifiers are excluded, not pooled into
one artificial long host/user sequence. Optional --gap-minutes 30 further splits
process histories after inactivity; it changes the statistical definition and must
be reported. These sequences are not independently verified campaigns/runs.

Labels come from _source.rule_technique_id. Valid technique strings are retained
including sub-techniques; no restricted training vocabulary removes labels. This
checks ID syntax only, not membership in a particular ATT&CK version. Multilabel
events remain unordered label sets. The scalar sequence is null for ambiguous
multilabel sequences. No first-label selection is performed.

Duplicate document IDs (index + ID) are removed; absent IDs use exact-line hashes.
Different observations of the same action may still remain. Timestamp filtering
uses the previous project's 2020-2025 range and reports exclusions explicitly.
Raw repetition counts and consecutive-label-collapsed counts are both reported;
neither guarantees genuine independent attack-step counts. Unique-technique counts
are shown separately. Strict >25 means 26 or more, >30 means 31 or more.

Malformed JSON lines are counted, never silently ignored. The inspected archive is
NDJSON. Pretty-printed JSON arrays and other schemas are not supported. A full
scan with zero usable events or substantial parse errors is NOT a successful
dataset extraction. Review the audit before using results in the thesis.
