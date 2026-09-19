param(
    [string]$WanGpRoot = 'Z:\AI\WanGP',
    [string]$ProfileDir = 'Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260819_124008056'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$Python = Join-Path $WanGpRoot 'env_uv\Scripts\python.exe'
$Analyzer = Join-Path $PSScriptRoot 'analyze_behavior_inventory.py'
$Curator = Join-Path $PSScriptRoot 'curate_secondary_behavior_source.py'
$Annotations = Join-Path $PSScriptRoot 'behavior_source_annotations_secondary.json'

$Manifest = Join-Path $ProfileDir 'manifest.json'
$PoseTrack = Join-Path $ProfileDir 'pose_coco133.jsonl'
$FacialSidecar = Join-Path $ProfileDir 'facial_behavior_profile.json'
$AnalysisJson = Join-Path $ProfileDir 'inventory_analysis_secondary.json'
$AnalysisCsv = Join-Path $ProfileDir 'inventory_units_secondary.csv'
$CuratedJson = Join-Path $ProfileDir 'curated_secondary_inventory.json'
$CuratedCsv = Join-Path $ProfileDir 'curated_secondary_motion_units.csv'

foreach ($item in @(
    @{ Name='WanGP Python'; Path=$Python },
    @{ Name='Inventory analyzer'; Path=$Analyzer },
    @{ Name='Secondary curator'; Path=$Curator },
    @{ Name='Secondary annotations'; Path=$Annotations },
    @{ Name='Secondary manifest'; Path=$Manifest },
    @{ Name='Secondary pose track'; Path=$PoseTrack },
    @{ Name='Secondary facial sidecar'; Path=$FacialSidecar }
)) {
    if (-not (Test-Path -LiteralPath $item.Path -PathType Leaf)) {
        throw ('Missing ' + $item.Name + ': ' + $item.Path)
    }
}

Write-Host 'SECONDARY ROLE-AWARE BEHAVIOR CURATION'
Write-Host '======================================='
Write-Host ('Profile: ' + $ProfileDir)
Write-Host 'No DWPose and no Wan-Animate-2 are invoked.'
Write-Host 'This source is curated by role: face/head/body-support. Hands are diagnostic only.'
Write-Host ''

Write-Host 'Analyzing pose/group reliability by motion unit...'
& $Python $Analyzer --manifest $Manifest --pose-track $PoseTrack --output-json $AnalysisJson --output-csv $AnalysisCsv
if ($LASTEXITCODE -ne 0) { throw 'Secondary inventory analysis failed.' }

Write-Host ''
Write-Host 'Applying source-role curation + facial sidecar weights...'
& $Python $Curator --analysis $AnalysisJson --facial-sidecar $FacialSidecar --annotations $Annotations --output-json $CuratedJson --output-csv $CuratedCsv
if ($LASTEXITCODE -ne 0) { throw 'Secondary role-aware curation failed.' }

Write-Host ''
Write-Host 'SECONDARY CURATION: COMPLETE'
Write-Host ('Curated JSON: ' + $CuratedJson)
Write-Host ('Curated CSV: ' + $CuratedCsv)
Write-Host ''
Write-Host 'Paste the complete terminal output into ChatGPT before processing SIENA_BRUTO.mp4.'
