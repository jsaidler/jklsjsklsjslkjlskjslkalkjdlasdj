param(
    [int]$Seed = 0,
    [int]$Steps = 30,
    [string]$Resolution = '720x1280',
    [int]$TimeoutMinutes = 180,
    [switch]$DryRun,
    [string]$WanGpRoot = 'Z:\AI\WanGP'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$Runner = Join-Path $PSScriptRoot 'run_hunyuan_avatar_benchmark.py'
$WanPython = Join-Path $WanGpRoot 'env_uv\Scripts\python.exe'

if (-not (Test-Path -LiteralPath $Runner -PathType Leaf)) {
    throw "Hunyuan Avatar benchmark runner missing: $Runner"
}
if (-not (Test-Path -LiteralPath $WanPython -PathType Leaf)) {
    throw "WanGP Python missing: $WanPython"
}
if ($Steps -lt 1) {
    throw 'Steps must be >= 1.'
}
if ($TimeoutMinutes -lt 1) {
    throw 'TimeoutMinutes must be >= 1.'
}

# Keep cache traffic off Z:. The Python runner repeats this as a defense in depth.
$CacheRoot = Join-Path $env:LOCALAPPDATA 'VideoStudio\huggingface'
New-Item -ItemType Directory -Force -Path $CacheRoot | Out-Null
$env:HF_HOME = $CacheRoot
$env:HF_HUB_CACHE = Join-Path $CacheRoot 'hub'
$env:HF_XET_CACHE = Join-Path $CacheRoot 'xet'
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'

$Args = @(
    $Runner,
    '--wangp-root', $WanGpRoot,
    '--seed', $Seed,
    '--steps', $Steps,
    '--resolution', $Resolution,
    '--timeout-minutes', $TimeoutMinutes
)
if ($DryRun) {
    $Args += '--dry-run'
}

Write-Host 'HUNYUAN-AVATAR-BENCHMARK-01'
Write-Host '============================'
Write-Host ('Repo root: ' + $RepoRoot)
Write-Host ('WanGP root: ' + $WanGpRoot)
Write-Host ('Python: ' + $WanPython)
Write-Host ('Resolution: ' + $Resolution)
Write-Host ('Steps: ' + $Steps)
Write-Host ('Seed: ' + $Seed)
Write-Host ('Timeout: ' + $TimeoutMinutes + ' min')
Write-Host ('Dry run: ' + [bool]$DryRun)
Write-Host ''
Write-Host 'The runner uses WanGP shared/api.py directly; no Gradio/browser automation is involved.'
Write-Host 'Profile 4 + SDPA + TeaCache off are locked for this quality gate.'
Write-Host ''

Push-Location $RepoRoot
try {
    # WanGP and PyTorch can legitimately write progress/diagnostics to stderr.
    # Do not let Windows PowerShell 5.1 promote that native stderr into a terminating NativeCommandError.
    $PreviousPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & $WanPython @Args
        $ExitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $PreviousPreference
    }

    if ($ExitCode -ne 0) {
        throw "Hunyuan Avatar benchmark failed with exit code $ExitCode."
    }
}
finally {
    Pop-Location
}
