# Corrected local dataset audits

Keep this directory layout: Windows APT and OpTC import the root audit_core.py.
Python 3.10 or newer is required. Install PyYAML for Splunk and Mordor:

```powershell
python -m pip install PyYAML
```

Run from the dataset_checker directory, substituting actual local input paths:

```powershell
python Splunk_Attack_Data_test/run_pipeline.py --repo "C:\datasets\attack_data"
python Mordor_test/run_pipeline.py --repo "C:\datasets\Security-Datasets"
python Win_APT_test/run_pipeline.py --input-dir "C:\datasets\Windows-APT"
python DARPA_OpTC_test/run_pipeline.py --input-dir "C:\datasets\OpTC"
```

Each pipeline writes new reports under its output_verified folder. Old reports
and generated intermediates do not become evidence merely because they exist.
No pipeline downloads a repository or fabricates fallback scenarios.

Splunk produces capture/host/time candidate sessions from explicitly annotated
events. Mordor separates metadata inventories from declared simulation order.
Windows APT and OpTC audit explicitly annotated events, keeping source files
and hosts isolated. They no longer evaluate the old hard-coded scenario plans.
This is deliberately narrower than the old heuristic behavior; supported input
schemas and exclusions are documented in each project README.

These are evidence audits, not complete attack detectors. Unlabelled telemetry
needs validated annotations; cross-file campaigns need verified capture links.
Passing regression tests does not validate a dataset's attack chains.

Validation:

```powershell
python -m unittest discover -s tests -v
Push-Location Splunk_Attack_Data_test
python -m unittest discover -s tests -v
Pop-Location
Push-Location Mordor_test
python -m unittest discover -s tests -v
Pop-Location
```

The code-only ZIP excludes datasets, cloned repositories, generated outputs,
and caches. Clone deletion in the working directory was blocked by automatic
approval policy; the Splunk attack_data clone may still be present there.
