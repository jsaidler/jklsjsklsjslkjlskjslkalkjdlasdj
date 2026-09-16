param(
    [switch]$Download,
    [switch]$VerifyLargeSha,
    [string]$WanGpRoot = 'Z:\AI\WanGP'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$PyScript = Join-Path $PSScriptRoot 'prepare_hunyuan_avatar_benchmark.py'
$WanPython = Join-Path $WanGpRoot 'env_uv\Scripts\python.exe'
$ReportDir = Join-Path $PSScriptRoot 'reports'
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$Stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$Report = Join-Path $ReportDir ('hunyuan_avatar_prepare_' + $Stamp + '.txt')

if (-not (Test-Path -LiteralPath $PyScript -PathType Leaf)) {
    throw "Python preparer missing: $PyScript"
}
if (-not (Test-Path -LiteralPath $WanPython -PathType Leaf)) {
    throw "WanGP Python missing: $WanPython"
}

# Keep Hugging Face caches away from Z:. With local_dir downloads, only small metadata
# should be created beside ckpts; global/cache traffic is redirected to C:.
$CacheRoot = Join-Path $env:LOCALAPPDATA 'VideoStudio\huggingface'
New-Item -ItemType Directory -Force -Path $CacheRoot | Out-Null
$env:HF_HOME = $CacheRoot
$env:HF_HUB_CACHE = Join-Path $CacheRoot 'hub'
$env:HF_XET_CACHE = Join-Path $CacheRoot 'xet'
New-Item -ItemType Directory -Force -Path $env:HF_HUB_CACHE | Out-Null
New-Item -ItemType Directory -Force -Path $env:HF_XET_CACHE | Out-Null

$Args = @(
    $PyScript,
    '--wangp-root', $WanGpRoot
)
if ($Download) {
    $Args += '--download'
}
if ($VerifyLargeSha) {
    $Args += '--verify-large-sha'
}

Push-Location $RepoRoot
try {
    Write-Host 'HUNYUAN AVATAR BENCHMARK PREPARER'
    Write-Host '================================='
    Write-Host ('Repo root: ' + $RepoRoot)
    Write-Host ('WanGP root: ' + $WanGpRoot)
    Write-Host ('Download: ' + [bool]$Download)
    Write-Host ('Verify large SHA256: ' + [bool]$VerifyLargeSha)
    Write-Host ('HF cache root: ' + $CacheRoot)
    Write-Host ''

    & $WanPython @Args 2>&1 | Tee-Object -FilePath $Report
    $ExitCode = $LASTEXITCODE
    if ($ExitCode -ne 0) {
        throw "Hunyuan Avatar preparation failed with exit code $ExitCode. Report: $Report"
    }
}
finally {
    Pop-Location
}

Write-Host ''
Write-Host 'REPORT'
Write-Host '======'
Write-Host $Report
