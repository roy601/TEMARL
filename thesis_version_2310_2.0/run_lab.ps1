param([string]$Python = 'python', [ValidateSet('cuda','cpu')][string]$Device = 'cuda')
$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
Set-Location -LiteralPath $PSScriptRoot
& $Python validate_replay.py
if ($LASTEXITCODE -ne 0) { throw 'Validation failed; training not started.' }
& $Python -u run_experiment.py --device $Device --threads 4
if ($LASTEXITCODE -ne 0) { throw 'Experiment failed. Completed cells remain resumable.' }
& $Python report_results.py results/main
if ($LASTEXITCODE -ne 0) { throw 'Report generation failed.' }
