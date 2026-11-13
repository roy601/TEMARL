param(
    [string]$Repo = (Join-Path $PSScriptRoot 'data\attack_data'),
    [string]$Output = (Join-Path $PSScriptRoot 'output_verified')
)
$ErrorActionPreference = 'Stop'
$Repo = [System.IO.Path]::GetFullPath($Repo)
$Output = [System.IO.Path]::GetFullPath($Output)
function Check-Exit([string]$Step) {
    if ($LASTEXITCODE -ne 0) { throw "$Step failed (exit $LASTEXITCODE). Audit stopped; do not treat this as a complete dataset run." }
}
Get-Command python -ErrorAction Stop | Out-Null
Get-Command git -ErrorAction Stop | Out-Null
python -c "import sys; assert sys.version_info >= (3,10), 'Python 3.10 or newer is required'"
Check-Exit 'Python version check'
python -m pip install -r (Join-Path $PSScriptRoot 'requirements.txt')
Check-Exit 'Dependency installation'
git lfs version
Check-Exit 'Git LFS check (install Git LFS if unavailable)'

if (-not (Test-Path -LiteralPath $Repo)) {
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Repo) | Out-Null
    $PreviousSmudge = $env:GIT_LFS_SKIP_SMUDGE
    try {
        $env:GIT_LFS_SKIP_SMUDGE = '1'
        git clone --depth 1 https://github.com/splunk/attack_data.git "$Repo"
        Check-Exit 'Repository clone'
    } finally {
        $env:GIT_LFS_SKIP_SMUDGE = $PreviousSmudge
    }
}
if (-not (Test-Path -LiteralPath (Join-Path $Repo '.git'))) { throw "Existing path is not a Git checkout: $Repo" }
$Sparse = git -C "$Repo" config --bool core.sparseCheckout
if ($Sparse -eq 'true') { throw 'Sparse checkout is enabled; a full dataset checkout is required.' }
$Origin = git -C "$Repo" remote get-url origin
Check-Exit 'Repository origin check'
if ($Origin -notmatch 'github\.com[:/]splunk/attack_data(?:\.git)?/?$') { throw "Unexpected repository origin: $Origin" }
if (-not (Test-Path -LiteralPath (Join-Path $Repo 'datasets'))) { throw 'Dataset directory is missing.' }
git -C "$Repo" lfs install --local
Check-Exit 'Git LFS setup'
# Empty configured filters ensure the entire checked-out revision is downloaded.
git -C "$Repo" -c 'lfs.fetchinclude=' -c 'lfs.fetchexclude=' lfs pull
Check-Exit 'Full Git LFS download'
git -C "$Repo" lfs fsck
Check-Exit 'Git LFS integrity check'
$MissingFiles = git -C "$Repo" ls-files --deleted -- datasets
Check-Exit 'Missing tracked file check'
if ($MissingFiles) { throw 'Tracked dataset files are missing. Resolve the incomplete checkout before auditing.' }

Push-Location $PSScriptRoot
try {
    python -m unittest discover -s tests -v
    Check-Exit 'Regression tests'
    python -u run_pipeline.py --repo "$Repo" --output-dir "$Output"
    Check-Exit 'Full dataset audit'
} finally {
    Pop-Location
}
git -C "$Repo" rev-parse HEAD | Set-Content -LiteralPath (Join-Path $Output 'repository_commit.txt')
Check-Exit 'Repository revision recording'
Write-Host "Report: $(Join-Path $Output 'statistics.txt')"
Write-Host "Review coverage_status and intermediate\file_coverage.json before claiming complete telemetry coverage."
