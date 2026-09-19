param(
    [string]$WanGpRoot = 'Z:\AI\WanGP',
    [string]$Source = 'Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\VID_20260911_140124885.mp4',
    [string]$ProfileDir = 'Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$Python = Join-Path $WanGpRoot 'env_uv\Scripts\python.exe'
$Analyzer = Join-Path $PSScriptRoot 'analyze_behavior_inventory.py'
$Renderer = Join-Path $PSScriptRoot 'render_behavior_inventory_review.py'
$Manifest = Join-Path $ProfileDir 'manifest.json'
$Pose = Join-Path $ProfileDir 'pose_coco133.jsonl'
$Analysis = Join-Path $ProfileDir 'inventory_analysis.json'
$UnitCsv = Join-Path $ProfileDir 'inventory_units.csv'
$Sheet = Join-Path $ProfileDir 'inventory_review_sheet.jpg'

foreach ($item in @(
    @{ Name='WanGP Python'; Path=$Python },
    @{ Name='Inventory analyzer'; Path=$Analyzer },
    @{ Name='Review renderer'; Path=$Renderer },
    @{ Name='Source'; Path=$Source },
    @{ Name='Manifest'; Path=$Manifest },
    @{ Name='Pose track'; Path=$Pose }
)) {
    if (-not (Test-Path -LiteralPath $item.Path -PathType Leaf)) {
        throw ('Missing ' + $item.Name + ': ' + $item.Path)
    }
}

Write-Host 'BEHAVIOR INVENTORY REVIEW'
Write-Host '========================='
Write-Host ('Source: ' + $Source)
Write-Host ('Manifest: ' + $Manifest)
Write-Host ('Pose: ' + $Pose)
Write-Host ''
Write-Host 'This analyzes the 123 motion units and renders a local review sheet.'
Write-Host 'It does not run DWPose, Wan-Animate-2, training, or any remote service.'
Write-Host ''

$Saved = $ErrorActionPreference
try {
    $ErrorActionPreference = 'Continue'
    & $Python $Analyzer `
        '--manifest' $Manifest `
        '--pose-track' $Pose `
        '--output-json' $Analysis `
        '--output-csv' $UnitCsv
    $AnalyzeExit = $LASTEXITCODE
} finally {
    $ErrorActionPreference = $Saved
}
if ($AnalyzeExit -ne 0) { throw "Inventory analysis failed with exit code $AnalyzeExit." }

Write-Host ''
$Saved = $ErrorActionPreference
try {
    $ErrorActionPreference = 'Continue'
    & $Python $Renderer `
        '--source' $Source `
        '--manifest' $Manifest `
        '--analysis' $Analysis `
        '--output' $Sheet
    $RenderExit = $LASTEXITCODE
} finally {
    $ErrorActionPreference = $Saved
}
if ($RenderExit -ne 0) { throw "Inventory review rendering failed with exit code $RenderExit." }

if (-not (Test-Path -LiteralPath $Sheet -PathType Leaf)) {
    throw 'Inventory review sheet was not produced.'
}

Write-Host ''
Write-Host 'BEHAVIOR INVENTORY REVIEW: COMPLETE'
Write-Host ('Analysis: ' + $Analysis)
Write-Host ('Units CSV: ' + $UnitCsv)
Write-Host ('Upload this sheet: ' + $Sheet)
