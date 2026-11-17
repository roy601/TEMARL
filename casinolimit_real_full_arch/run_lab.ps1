param([string]$Python = 'python')
$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
$env:PYTHONUNBUFFERED = '1'
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
& $Python -c "import sys; print(sys.executable); print(sys.version)"
if ($LASTEXITCODE -ne 0) { throw 'Python unavailable; pass -Python with its full executable path' }
& $Python -m pip install -r casinolimit_real_full_arch/requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed' }
& $Python casinolimit_real_full_arch/test_pipeline.py
if ($LASTEXITCODE -ne 0) { throw 'Tests failed' }
& $Python -c "import torch; print('PyTorch:', torch.__version__); assert torch.cuda.is_available(), 'CUDA unavailable'; print(torch.cuda.get_device_name(0)); x=torch.ones(8,device='cuda'); print('GPU computation:', (x*x).sum().item())"
if ($LASTEXITCODE -ne 0) { throw 'Install compatible CUDA PyTorch before running' }
& $Python -u casinolimit_real_full_arch/pipeline.py --device cuda --train-missing
if ($LASTEXITCODE -ne 0) { throw 'Run failed; completed cells are retained for resume' }
Write-Host 'Finished: casinolimit_real_full_arch/results/main/RESULTS.md'
