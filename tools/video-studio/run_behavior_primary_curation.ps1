$ErrorActionPreference = 'Stop'

$Root = 'Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885'
$Python = 'Z:\AI\WanGP\env_uv\Scripts\python.exe'
$Repo = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$Tool = Join-Path $PSScriptRoot 'curate_behavior_inventory.py'
$Annotations = Join-Path $PSScriptRoot 'behavior_source_annotations_primary.json'
$Analysis = Join-Path $Root 'inventory_analysis.json'
$OutJson = Join-Path $Root 'curated_inventory.json'
$OutCsv = Join-Path $Root 'curated_motion_units.csv'

Write-Host 'PRIMARY BEHAVIOR INVENTORY CURATION'
Write-Host '================================='
Write-Host "Analysis: $Analysis"
Write-Host "Annotations: $Annotations"
Write-Host ''
Write-Host 'No DWPose and no Wan-Animate-2 are invoked.'
Write-Host ''

foreach ($p in @($Python, $Tool, $Annotations, $Analysis)) {
    if (-not (Test-Path -LiteralPath $p)) { throw "Missing required path: $p" }
}

& $Python $Tool `
    --analysis $Analysis `
    --annotations $Annotations `
    --output-json $OutJson `
    --output-csv $OutCsv

if ($LASTEXITCODE -ne 0) { throw 'Primary behavior inventory curation failed.' }

Write-Host ''
Write-Host 'PRIMARY CURATION: COMPLETE'
Write-Host "Curated JSON: $OutJson"
Write-Host "Curated CSV: $OutCsv"
