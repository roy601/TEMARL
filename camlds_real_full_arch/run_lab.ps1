param([string]$Device = 'cuda', [switch]$Smoke)
$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
$env:PYTHONUNBUFFERED = '1'
Set-Location -LiteralPath $PSScriptRoot
function Invoke-CheckedPython {
    & python @args
    if ($LASTEXITCODE -ne 0) { throw 'Python failed. Preserve the output directory and diagnose the error.' }
}
Invoke-CheckedPython -m pip install -r requirements.txt
Invoke-CheckedPython test_pipeline.py
if ($Device -eq 'cuda') {
    Invoke-CheckedPython -c "import torch; print(torch.__version__); assert torch.cuda.is_available(), 'CUDA unavailable: install GPU PyTorch for your lab driver'"
}
$runArgs = @('pipeline.py', '--device', $Device, '--train-missing')
if ($Smoke) { $runArgs += '--smoke' }
Invoke-CheckedPython @runArgs
Write-Host 'Finished. See results/main/RESULTS.md (or results/main/smoke/RESULTS.md).' -ForegroundColor Green
