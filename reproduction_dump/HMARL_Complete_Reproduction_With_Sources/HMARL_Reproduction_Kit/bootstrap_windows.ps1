# Bootstrap for PowerShell on Windows 10/11; run from any directory.
# Use installed Python 3.10 (py -3.10) and Git for Windows.
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$HCommit = '6fe960f5931f2d7dc5ef522f09ca4a179f377ee4'
$CCommit = '8c3c50ca54b176c2de199847944e8dcc035497e3'
New-Item -ItemType Directory -Force -Path sources,logs,results | Out-Null
function Run-Native([string]$Cmd,[string[]]$CmdArgs) {
  & $Cmd @CmdArgs
  if ($LASTEXITCODE -ne 0) { throw "Command failed ($LASTEXITCODE): $Cmd $($CmdArgs -join ' ')" }
}
function Get-PinnedRepo([string]$Url, [string]$Path, [string]$Commit) {
  if (-not (Test-Path (Join-Path $Path '.git'))) { Run-Native 'git' @('clone','--branch','main','--depth','1',$Url,$Path) }
  & git -C $Path fetch --depth 1 origin $Commit
  if ($LASTEXITCODE -ne 0) { Run-Native 'git' @('-C',$Path,'fetch','--unshallow','origin') }
  Run-Native 'git' @('-C',$Path,'-c','advice.detachedHead=false','checkout','--detach',$Commit)
  $actual = (& git -C $Path rev-parse HEAD).Trim()
  if ($actual -ne $Commit) { throw "Unexpected upstream commit for $Path : $actual" }
}
Get-PinnedRepo 'https://github.com/adityavs14/Hierarchical-MARL.git' 'sources/Hierarchical-MARL' $HCommit
Get-PinnedRepo 'https://github.com/cage-challenge/cage-challenge-4.git' 'sources/cage-challenge-4' $CCommit
Run-Native 'py' @('-3.10','-m','venv','.venv')
$PythonExe = Join-Path (Get-Location) '.venv\Scripts\python.exe'
Run-Native $PythonExe @('-m','pip','install','--upgrade','pip','setuptools','wheel')
Run-Native $PythonExe @('-m','pip','install','-r','sources/cage-challenge-4/Requirements.txt')
Run-Native $PythonExe @('-m','pip','install','-e','sources/cage-challenge-4')
Run-Native $PythonExe @('-m','pip','install','ray[rllib]==2.10.0')
& $PythonExe -m pip freeze | Out-File -Encoding utf8 results/pip_freeze_after_install.txt
Run-Native $PythonExe @('scripts/patch_metrics.py','--repo','sources/Hierarchical-MARL','--out','results/metrics_patch.json')
Run-Native $PythonExe @('scripts/preflight.py','--repo','sources/Hierarchical-MARL','--cage','sources/cage-challenge-4','--out','results/preflight.json')
Write-Host 'Next: .\.venv\Scripts\python.exe scripts\run_evaluation.py --max-eps 100 --seed 42'
