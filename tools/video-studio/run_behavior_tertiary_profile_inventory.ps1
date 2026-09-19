param(
    [string]$WanGpRoot = 'Z:\AI\WanGP',
    [string]$Source = 'Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\SIENA_BRUTO.mp4',
    [string]$ProfileDir = 'Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\SIENA_BRUTO'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$Python = Join-Path $WanGpRoot 'env_uv\Scripts\python.exe'
$Extractor = Join-Path $PSScriptRoot 'extract_behavior_profile.py'
$Inspector = Join-Path $PSScriptRoot 'inspect_behavior_profile.py'
$Analyzer = Join-Path $PSScriptRoot 'analyze_behavior_inventory.py'
$Renderer = Join-Path $PSScriptRoot 'render_behavior_inventory_review.py'

$Pose = Join-Path $ProfileDir 'pose_coco133.jsonl'
$Manifest = Join-Path $ProfileDir 'manifest.json'
$MotionCsv = Join-Path $ProfileDir 'motion_units.csv'
$Inspection = Join-Path $ProfileDir 'profile_inspection.json'
$Analysis = Join-Path $ProfileDir 'inventory_analysis.json'
$UnitCsv = Join-Path $ProfileDir 'inventory_units.csv'
$Sheet = Join-Path $ProfileDir 'inventory_review_sheet.jpg'

foreach ($item in @(
    @{ Name='WanGP Python'; Path=$Python },
    @{ Name='Behavior extractor'; Path=$Extractor },
    @{ Name='Behavior inspector'; Path=$Inspector },
    @{ Name='Inventory analyzer'; Path=$Analyzer },
    @{ Name='Inventory renderer'; Path=$Renderer },
    @{ Name='SIENA source'; Path=$Source },
    @{ Name='Full SIENA pose track'; Path=$Pose }
)) {
    if (-not (Test-Path -LiteralPath $item.Path -PathType Leaf)) {
        throw ('Missing ' + $item.Name + ': ' + $item.Path)
    }
}

New-Item -ItemType Directory -Force -Path $ProfileDir | Out-Null

Write-Host 'SIENA BEHAVIOR PROFILE + INVENTORY REVIEW'
Write-Host '========================================='
Write-Host ('Python: ' + $Python)
Write-Host ('Source: ' + $Source)
Write-Host ('Pose: ' + $Pose)
Write-Host ('Profile: ' + $ProfileDir)
Write-Host ''
Write-Host 'No DWPose and no Wan-Animate-2 are invoked.'
Write-Host 'This builds behavior-profile/v1, validates it, analyzes per-unit reliability, and renders a review sheet.'
Write-Host ''

Write-Host '[1/4] Building behavior-profile/v1...'
$Saved = $ErrorActionPreference
try {
    $ErrorActionPreference = 'Continue'
    & $Python $Extractor '--source' $Source '--output' $ProfileDir '--pose-track' $Pose
    $Exit = $LASTEXITCODE
} finally {
    $ErrorActionPreference = $Saved
}
if ($Exit -ne 0) { throw "SIENA behavior profile extraction failed with exit code $Exit." }
if (-not (Test-Path -LiteralPath $Manifest -PathType Leaf)) { throw 'SIENA profile produced no manifest.json.' }
if (-not (Test-Path -LiteralPath $MotionCsv -PathType Leaf)) { throw 'SIENA profile produced no motion_units.csv.' }

Write-Host ''
Write-Host '[2/4] Inspecting profile structure...'
$Saved = $ErrorActionPreference
try {
    $ErrorActionPreference = 'Continue'
    & $Python $Inspector '--manifest' $Manifest '--csv' $MotionCsv '--output' $Inspection
    $Exit = $LASTEXITCODE
} finally {
    $ErrorActionPreference = $Saved
}
if ($Exit -ne 0) { throw "SIENA profile structural inspection failed with exit code $Exit." }

Write-Host ''
Write-Host '[3/4] Analyzing unit/group reliability...'
$Saved = $ErrorActionPreference
try {
    $ErrorActionPreference = 'Continue'
    & $Python $Analyzer '--manifest' $Manifest '--pose-track' $Pose '--output-json' $Analysis '--output-csv' $UnitCsv
    $Exit = $LASTEXITCODE
} finally {
    $ErrorActionPreference = $Saved
}
if ($Exit -ne 0) { throw "SIENA inventory analysis failed with exit code $Exit." }

Write-Host ''
Write-Host '[4/4] Rendering visual inventory review...'
$Saved = $ErrorActionPreference
try {
    $ErrorActionPreference = 'Continue'
    & $Python $Renderer '--source' $Source '--manifest' $Manifest '--analysis' $Analysis '--output' $Sheet
    $Exit = $LASTEXITCODE
} finally {
    $ErrorActionPreference = $Saved
}
if ($Exit -ne 0) { throw "SIENA inventory review rendering failed with exit code $Exit." }
if (-not (Test-Path -LiteralPath $Sheet -PathType Leaf)) { throw 'SIENA inventory review sheet was not produced.' }

Write-Host ''
Write-Host 'SIENA PROFILE + INVENTORY REVIEW: COMPLETE'
Write-Host ('Manifest: ' + $Manifest)
Write-Host ('Profile inspection: ' + $Inspection)
Write-Host ('Inventory analysis: ' + $Analysis)
Write-Host ('Inventory CSV: ' + $UnitCsv)
Write-Host ('Upload this sheet: ' + $Sheet)
Write-Host ''
Write-Host 'Paste the complete terminal output and upload the review sheet before SIENA semantic exclusions/curation.'
