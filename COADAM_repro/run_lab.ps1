param([string]$Matlab = "", [switch]$SmokeOnly, [switch]$ReportOnly)
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUNBUFFERED = "1"
Set-Location $PSScriptRoot
if (!(Test-Path -LiteralPath ".venv\Scripts\python.exe")) {
    py -3.12 -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw "Python 3.12 environment creation failed" }
}
$studyPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
& $studyPython -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw "Dependencies failed" }
& $studyPython -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { throw "Package tests failed" }
if (!$ReportOnly -and !$Matlab) {
    $found = Get-Command matlab -ErrorAction SilentlyContinue
    if ($found) { $Matlab = $found.Source }
    else {
        $candidate = Join-Path $env:ProgramFiles "MATLAB\R2025b\bin\matlab.exe"
        if (Test-Path -LiteralPath $candidate) { $Matlab = $candidate }
        else { throw 'Supply -Matlab "C:\Program Files\MATLAB\R2025b\bin\matlab.exe"' }
    }
}
$studyArgs = @("-u", "run_study.py")
if ($Matlab) { $studyArgs += @("--matlab", $Matlab) }
if ($SmokeOnly) { $studyArgs += "--smoke-only" }
if ($ReportOnly) { $studyArgs += "--report-only" }
& $studyPython @studyArgs
if ($LASTEXITCODE -ne 0) { throw "Study stopped. Inspect logs; repeat this command to resume completed stages." }
Write-Host "Finished. Results: outputs\main\RESULTS.md (smoke: outputs\main_smoke\RESULTS.md)" -ForegroundColor Green
