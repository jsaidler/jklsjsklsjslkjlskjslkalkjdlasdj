param(
    [string]$WanGpRoot = 'Z:\AI\WanGP',
    [string]$Root = 'Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$Python = Join-Path $WanGpRoot 'env_uv\Scripts\python.exe'
$TertiaryRunner = Join-Path $PSScriptRoot 'run_behavior_tertiary_curation.ps1'
$Builder = Join-Path $PSScriptRoot 'build_unified_behavior_library.py'

$PrimaryDir = Join-Path $Root 'VID_20260911_140124885'
$SecondaryDir = Join-Path $Root 'VID_20260819_124008056'
$TertiaryDir = Join-Path $Root 'SIENA_BRUTO'
$LibraryDir = Join-Path $Root 'unified'
$Library = Join-Path $LibraryDir 'joao_motion_library_v1.json'

foreach ($item in @(
    @{ Name='WanGP Python'; Path=$Python },
    @{ Name='SIENA curation runner'; Path=$TertiaryRunner },
    @{ Name='Unified library builder'; Path=$Builder },
    @{ Name='Primary manifest'; Path=(Join-Path $PrimaryDir 'manifest.json') },
    @{ Name='Primary curated inventory'; Path=(Join-Path $PrimaryDir 'curated_inventory.json') },
    @{ Name='Secondary manifest'; Path=(Join-Path $SecondaryDir 'manifest.json') },
    @{ Name='Secondary curated inventory'; Path=(Join-Path $SecondaryDir 'curated_secondary_inventory.json') },
    @{ Name='Tertiary manifest'; Path=(Join-Path $TertiaryDir 'manifest.json') },
    @{ Name='Tertiary inventory analysis'; Path=(Join-Path $TertiaryDir 'inventory_analysis.json') }
)) {
    if (-not (Test-Path -LiteralPath $item.Path -PathType Leaf)) {
        throw ('Missing ' + $item.Name + ': ' + $item.Path)
    }
}

Write-Host 'FINALIZE MULTI-SOURCE BEHAVIOR LIBRARY'
Write-Host '======================================'
Write-Host 'Step 1: materialize reviewed SIENA role-aware curation.'
Write-Host 'Step 2: build unified source-preserving João motion library.'
Write-Host 'No DWPose and no Wan-Animate-2 are invoked.'
Write-Host ''

powershell -ExecutionPolicy Bypass -File $TertiaryRunner -WanGpRoot $WanGpRoot -ProfileDir $TertiaryDir
if ($LASTEXITCODE -ne 0) { throw ('SIENA curation runner failed with exit code ' + $LASTEXITCODE) }

$TertiaryCurated = Join-Path $TertiaryDir 'curated_tertiary_inventory.json'
if (-not (Test-Path -LiteralPath $TertiaryCurated -PathType Leaf)) { throw 'SIENA curated inventory missing after curation.' }
New-Item -ItemType Directory -Force -Path $LibraryDir | Out-Null

Write-Host ''
Write-Host 'Building unified library...'
$Saved = $ErrorActionPreference
try {
    $ErrorActionPreference = 'Continue'
    & $Python $Builder `
        '--primary-manifest' (Join-Path $PrimaryDir 'manifest.json') `
        '--primary-curated' (Join-Path $PrimaryDir 'curated_inventory.json') `
        '--secondary-manifest' (Join-Path $SecondaryDir 'manifest.json') `
        '--secondary-curated' (Join-Path $SecondaryDir 'curated_secondary_inventory.json') `
        '--tertiary-manifest' (Join-Path $TertiaryDir 'manifest.json') `
        '--tertiary-curated' $TertiaryCurated `
        '--output' $Library
    $BuildExit = $LASTEXITCODE
} finally {
    $ErrorActionPreference = $Saved
}
if ($BuildExit -ne 0) { throw ('Unified library build failed with exit code ' + $BuildExit) }
if (-not (Test-Path -LiteralPath $Library -PathType Leaf)) { throw 'Unified library file was not produced.' }

$J = Get-Content -LiteralPath $Library -Raw | ConvertFrom-Json
Write-Host ''
Write-Host 'MULTI-SOURCE BEHAVIOR LIBRARY: COMPLETE'
Write-Host ('Units total: ' + $J.units_total)
Write-Host ('Primary curated units in library: ' + $J.sources.primary.curated_units)
Write-Host ('Secondary curated units in library: ' + $J.sources.secondary.curated_units)
Write-Host ('Tertiary curated units in library: ' + $J.sources.tertiary.curated_units)
Write-Host ('Library: ' + $Library)
Write-Host ''
Write-Host 'Paste the complete terminal output into ChatGPT before first behavioral-driver synthesis.'
