# Run from this extracted folder using Windows PowerShell 7 or Windows PowerShell 5.1.
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
py -3.11 -m venv .venv
if ($LASTEXITCODE -ne 0) { throw 'Install Python 3.11 and ensure py -3.11 works.' }
$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
& $python bootstrap.py --install
if ($LASTEXITCODE -ne 0) { throw 'Setup failed; check Git, internet access and package compatibility.' }
& $python preflight.py
if ($LASTEXITCODE -ne 0) { throw 'Preflight failed. Resolve errors before evaluation.' }
& $python run_baselines.py --agents all --episodes 2 --seed 12501
if ($LASTEXITCODE -ne 0) { throw 'Smoke test failed; inspect results/<agent>/.../runner.log' }
& $python make_comparison.py
Write-Host '2-episode smoke runs complete. For full runs use .venv\Scripts\python.exe run_baselines.py --agents all --episodes 100 --seed 12502'
