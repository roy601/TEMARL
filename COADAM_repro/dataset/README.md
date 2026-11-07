# Dataset storage

Keep downloaded datasets here. Large raw files are intentionally excluded from git.

For the default Tables 5/6 experiment, **download nothing**: the released processed simulator configuration is included in `../upstream/data/processed/`.

The authors' broader preprocessing pipeline references:

| Dataset | Official source | Intended local location if you separately audit preprocessing |
|---|---|---|
| CIC-IIoT2025 | https://www.unb.ca/cic/datasets/iiot-dataset-2025.html | `CIC-IIoT-2025/` |
| WUSTL-IIoT-2021 | https://www.cse.wustl.edu/~jain/iiot2/index.html | `WUSTL-IIoT-2021/` |
| Edge-IIoTset | https://ieee-dataport.org/documents/edge-iiotset-new-comprehensive-realistic-cyber-security-dataset-iot-and-iiot-applications | `Edge-IIoTset/` |

Availability, licensing and the identity of raw file versions must be checked before a raw-data rebuild. The full raw data have not been downloaded or inspected for this package. Dropping CSVs into these folders does not make the default runner use them.

If you independently run and validate the original preprocessing/configuration stages, put `environment_config.mat` and `threat_profiles.mat` in `dataset/processed/`, then use `--config-dir dataset/processed --output outputs/rebuilt_config`. Preserve the original input files, checksums, preprocessing changes and logs. This alternative changes the experiment's provenance and does not inherit the bundled configuration's results.
