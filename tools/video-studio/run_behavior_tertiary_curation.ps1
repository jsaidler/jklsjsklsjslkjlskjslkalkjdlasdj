param(
    [string]$WanGpRoot = 'Z:\AI\WanGP',
    [string]$ProfileDir = 'Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\SIENA_BRUTO'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$Python = Join-Path $WanGpRoot 'env_uv\Scripts\python.exe'
$Curator = Join-Path $PSScriptRoot 'curate_tertiary_behavior_source.py'
$Annotations = Join-Path $PSScriptRoot 'behavior_source_annotations_tertiary.json'
$Analysis = Join-Path $ProfileDir 'inventory_analysis.json'
$OutputJson = Join-Path $ProfileDir 'curated_tertiary_inventory.json'
$OutputCsv = Join-Path $ProfileDir 'curated_tertiary_motion_units.csv'

foreach ($item in @(
    @{ Name='WanGP Python'; Path=$Python },
    @{ Name='SIENA curator'; Path=$Curator },
    @{ Name='SIENA annotations'; Path=$Annotations },
    @{ Name='SIENA inventory analysis'; Path=$Analysis }
)) {
    if (-not (Test-Path -LiteralPath $item.Path -PathType Leaf)) {
        throw ('Missing ' + $item.Name + ': ' + $item.Path)
    }
}

Write-Host 'SIENA ROLE-AWARE BEHAVIOR CURATION'
Write-Host '==================================='
Write-Host ('Profile: ' + $ProfileDir)
Write-Host 'No DWPose and no Wan-Animate-2 are invoked.'
Write-Host 'Reviewed semantic exclusions are applied; hands remain retrieval-disabled for SIENA.'
Write-Host ''

$Saved = $ErrorActionPreference
try {
    $ErrorActionPreference = 'Continue'
    & $Python $Curator `
        '--analysis' $Analysis `
        '--annotations' $Annotations `
        '--output-json' $OutputJson `
        '--output-csv' $OutputCsv
    $Exit = $LASTEXITCODE
} finally {
    $ErrorActionPreference = $Saved
}
if ($Exit -ne 0) { throw "SIENA curation failed with exit code $Exit." }
if (-not (Test-Path -LiteralPath $OutputJson -PathType Leaf)) { throw 'SIENA curation produced no JSON.' }
if (-not (Test-Path -LiteralPath $OutputCsv -PathType Leaf)) { throw 'SIENA curation produced no CSV.' }

$J = Get-Content -LiteralPath $OutputJson -Raw | ConvertFrom-Json
if ([int]$J.units_total -ne 49) { throw ('Unexpected SIENA unit count: ' + $J.units_total) }
if ([int]$J.global_hard_excluded -ne 12) { throw ('Unexpected SIENA hard-excluded count: ' + $J.global_hard_excluded) }

Write-Host ''
Write-Host 'SIENA CURATION: COMPLETE'
Write-Host ('Curated JSON: ' + $OutputJson)
Write-Host ('Curated CSV: ' + $OutputCsv)
Write-Host ''
Write-Host 'Expected reviewed state: 49 total / 12 hard excluded / 37 semantically clean.'
