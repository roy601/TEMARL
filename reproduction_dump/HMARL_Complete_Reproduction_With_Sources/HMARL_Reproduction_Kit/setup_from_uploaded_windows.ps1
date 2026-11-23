# Reproduce Table 3 from the two ALREADY BUNDLED source archives.
# Requires Windows with Python 3.10, internet access to PyPI for wheels,
# compatible PyTorch/Ray packages and enough available RAM/storage.
# Run in PowerShell: powershell -ExecutionPolicy Bypass -File .\setup_from_uploaded_windows.ps1
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
function RunNative([string]$Exe,[string[]]$Args) {
    & $Exe @Args
    if ($LASTEXITCODE -ne 0) { throw "Command failed [$LASTEXITCODE]: $Exe $($Args -join ' ')" }
}
if (-not (Test-Path 'sources\Hierarchical-MARL\README.md')) { throw 'Original H-MARL source missing' }
if (-not (Test-Path 'sources\cage-challenge-4\CybORG\__init__.py')) { throw 'Original CybORG source missing' }
New-Item -Force -ItemType Directory -Path logs,results | Out-Null
RunNative 'py' @('-3.10','-m','venv','.venv')
$Py = Join-Path (Get-Location).Path '.venv\Scripts\python.exe'
RunNative $Py @('-m','pip','install','--upgrade','pip','setuptools','wheel')
RunNative $Py @('-m','pip','install','numpy==1.26.4')
RunNative $Py @('-m','pip','install','ray[rllib]==2.10.0')
RunNative $Py @('-m','pip','install','-r','sources/cage-challenge-4/Requirements.txt')
RunNative $Py @('-m','pip','install','-e','sources/cage-challenge-4')
& $Py -m pip freeze | Out-File -Encoding utf8 results\pip_freeze_after_install.txt
RunNative $Py @('scripts/patch_metrics.py','--repo','sources/Hierarchical-MARL')
RunNative $Py @('scripts/instrument_metrics.py','--repo','sources/Hierarchical-MARL')
RunNative $Py @('-m','unittest','discover','-s','tests','-v')
RunNative $Py @('scripts/preflight.py','--repo','sources/Hierarchical-MARL','--cage','sources/cage-challenge-4','--out','results/preflight.json')
Write-Host 'Installation checks passed. To run the 100-episode evaluation:'
Write-Host '.\.venv\Scripts\python.exe scripts\run_evaluation.py --max-eps 100 --seed 42'
Write-Host '.\.venv\Scripts\python.exe scripts\compare_results.py'
