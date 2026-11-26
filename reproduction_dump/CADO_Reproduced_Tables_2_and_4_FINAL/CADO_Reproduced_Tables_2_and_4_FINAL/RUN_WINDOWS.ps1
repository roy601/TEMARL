# Start in the folder containing this file.
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
Write-Host 'Checking the independently reproduced Table 2 and held-out Table 4...'
python .\tools\verify_package.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host 'PASS. For a fresh simulator rerun, execute:'
Write-Host 'python .\tools\reproduce_again.py --output .\local_rerun'
Write-Host 'Add --full for ablations and --prototype for isolated HTTP tests.'
