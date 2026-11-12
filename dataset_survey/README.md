# Dataset survey

Downloads candidate datasets, reads every file line by line, and writes a plain report for each one.
It only reads: no dataset file is changed.

## Run (GPU PC)

```
git pull
python dataset_survey/survey.py
```

Then commit and push `dataset_survey/out/`. The downloads (about 7.7 GB) go to `dataset_survey/data/`,
which Git ignores.

| Option | What it does |
|---|---|
| `--plan` | Show what would be downloaded, then stop |
| `--only casinolimit ait_ads` | Only these datasets |
| `--force` | Read again even if a report already exists |

**Stopped part-way?** Run the same command again. Finished downloads are not downloaded again, and a
dataset that already has a report for exactly the same files is skipped.

## The datasets

| Name | Source | Size |
|---|---|---|
| `casinolimit` | Zenodo 17256954 (RAID 2025) | 3.5 GB |
| `ait_ads` | Zenodo 8263181 (CSET 2024) | 92 MB |
| `windows_apt_2025` | Mendeley b8fmtzvpy8 (Data in Brief 2026) | 459 MB |
| `shell_attack_evolution` | GitHub zyw-286/shell-attack-evolution-dataset (SRDS 2025) | about 100 MB |
| `cptc_sage_alerts` | GitHub tudelft-cda-lab/SAGE, `alerts/` only | about 90 MB |
| `unraveled` | S3 bucket dapt2021, labelled `processed/` part only (Computer Networks 2023) | 3.5 GB |
| `pwnjutsu` | IEEE DataPort, subscription needed: put `pwnjutsu_dataset.tar` in `dataset_survey/data/pwnjutsu/` and run again | 81 GB |
| `camlds` | Already read on 2026-11-07 (`camlds_real/DATASET_REPORT.md`) | — |

## What each report contains

`dataset_survey/out/<name>/REPORT.txt`:

1. **Downloaded files**, each checked against its published checksum.
2. **Totals:** files, bytes and lines read, binary files, lines that are not UTF-8, read errors.
3. **MITRE ATT&CK technique IDs** found anywhere in the text, which fields hold them, and which files are
   named as labels. An ID in the data is not automatically a label: alert rules also carry IDs.
4. **File types.**
5. **File groups:** files with the same name pattern (numbers shown as `#`).
6. **Fields** of CSV and JSON files: how often each is filled, how many distinct values, examples.
7. **First lines** of the largest file groups, with long tokens masked.
8. **Problems.**

`report.json` has the full detail. `out/SUMMARY.txt` has one line per dataset.

## Known issue: the antivirus

Attack logs contain attack scripts as text, so Windows Defender may delete or block a downloaded file.
On 2026-11-11 it removed `10-December-P1.csv` from Windows-APT 2025 as a trojan. The script records such
a file as **blocked**, carries on, and lists it in the report and in the `blocked` column of the summary.
The file is then missing from that report. Excluding `dataset_survey/data/` from the antivirus would avoid
this, but it lowers protection, so it is your decision.

## Tests

`python -m unittest discover -s dataset_survey/tests` (19 tests, on small made-up data).

## CasinoLimit: the attack steps in time order

`python dataset_survey/casinolimit_steps.py` (after the survey has downloaded CasinoLimit; about 9 minutes)

Each CasinoLimit label points to auditd events on one machine. The script finds every one of those events in
the raw `audit.log` files, takes its time and command line, and puts each attacker's labels in time order.
Output in `dataset_survey/out/casinolimit_steps/`: `REPORT.txt` (summary), `steps.csv` (one row per label:
instance, order, time, machine, technique, command, who labelled it), `instances.csv` (one row per attacker).
The committed output was made on 2026-11-12 from files whose md5 matched the Zenodo record.
