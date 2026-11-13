# Uploaded scenario_1_autostart_pam.zip verification

Tested against the supplied local archive; no attack commands were executed.

| Check | Measured outcome |
|---|---|
| ZIP member integrity | All 10,508 entries passed CRC verification |
| AttackMate execution records | All 53 JSONL records parsed |
| Labelled records | 28 |
| Corresponding corpus steps | 28/28 matched |
| Sub-technique label instances | 44 |
| Unique parent techniques | 26 |
| Multi-label steps | 5 |
| Label or parent-collapse mismatch | 0 |
| Full command / execution-rank sidecar mismatch | 0 |
| Labelled records omitted | 0 |
| CSV order vs execution order for this run | Same |
| Fresh extractor output vs saved steps.jsonl | All 904 records identical |
| Fresh vocabulary vs saved vocabulary | Identical except machine-dependent built_from source path |

The archive has no attack_times.csv. The extractor was rerun using the existing authors' CSV into results/archive_audit/fresh_extract; it does not automatically build that CSV from this ZIP. Independent archive reconciliation verifies this run's actual source records. The remaining 33 runs were not independently checked against their raw archives in this audit.

The 25 unlabelled records are excluded from prediction data. Technique labels originate in execution metadata; this is not automated ATT&CK recognition from syslog/network traffic. Parsing records is not proof every recorded attack succeeded.

Known limitations: the extractor's comment that adjusted CSV timestamps always provide execution order is outdated for four S6 swaps elsewhere in the corpus. The new full architecture uses reconciled execution_rank by default. The reconciliation fallback matches fractional microseconds within a run; it is not a generally sufficient identity rule for arbitrary new datasets. This audit also checked labels and full commands independently for all 28 matched records. Raw telemetry files received CRC checks, not full semantic analysis. Source authenticity was not checked against a publisher checksum.

Reproduce:

```powershell
python camlds_real_full_arch/audit_uploaded_zip.py "C:\Users\Riton\Downloads\scenario_1_autostart_pam.zip"
```

Detailed output: results/archive_audit/ZIP_AUDIT.md and ZIP_AUDIT.json. Existing source data and previous results were not modified.
