param(
    [ValidateSet("cuda", "cpu")][string]$Device = "cuda",
    [string]$Epochs = "auto",
    [switch]$SmokeOnly,
    [switch]$SkipInstall
)
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUNBUFFERED = "1"
$env:CUBLAS_WORKSPACE_CONFIG = ":4096:8"
Set-Location -LiteralPath $PSScriptRoot
$studyPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

function Invoke-StudyPython {
    param([string[]]$Arguments)
    & $studyPython @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed (exit $LASTEXITCODE): $($Arguments -join ' ')"
    }
}

if (-not (Test-Path -LiteralPath $studyPython)) {
    & py -3.12 -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw "Python 3.12 is required to create the lab environment." }
}
if (-not $SkipInstall) {
    Invoke-StudyPython -Arguments @("-m", "pip", "install", "--upgrade", "pip")
    $studyIndex = if ($Device -eq "cuda") { "https://download.pytorch.org/whl/cu128" } else { "https://download.pytorch.org/whl/cpu" }
    $studyTorch = if ($Device -eq "cuda") { "torch==2.10.0+cu128" } else { "torch==2.10.0+cpu" }
    Invoke-StudyPython -Arguments @("-m", "pip", "install", $studyTorch, "--index-url", $studyIndex)
    Invoke-StudyPython -Arguments @("-m", "pip", "install", "-r", "requirements.txt")
}
if ($Device -eq "cuda") {
    Invoke-StudyPython -Arguments @("-c", "import torch; print('PyTorch:', torch.__version__); assert torch.cuda.is_available(), 'CUDA unavailable; verify NVIDIA driver and CUDA PyTorch'; print('GPU:', torch.cuda.get_device_name(0))")
}
Invoke-StudyPython -Arguments @("-B", "-m", "unittest", "test_bundle", "test_markov_study", "test_confidence", "-v")
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$smokeFolder = "results_markov\smoke_${Device}_$stamp"
$fullFolder = "results_markov\full_${Device}_$stamp"
Invoke-StudyPython -Arguments @("-B", "-u", "run_markov_study.py", "--smoke", "--device", $Device, "--output", $smokeFolder)
if ($SmokeOnly) {
    Write-Host "SMOKE FINISHED. These are execution checks, not thesis results." -ForegroundColor Green
    return
}
Invoke-StudyPython -Arguments @("-B", "-u", "run_markov_study.py", "--device", $Device, "--epochs", $Epochs, "--threads", "4", "--output", $fullFolder)
Write-Host "FULL EXPERIMENT FINISHED. Open $fullFolder\RESULTS.md and $fullFolder\CONFIDENCE_RESULTS.md" -ForegroundColor Green
