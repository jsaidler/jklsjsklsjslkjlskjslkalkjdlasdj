param(
    [string]$WanGpRoot = 'Z:\AI\WanGP',
    [string]$Source = 'Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\VID_20260911_140124885.mp4',
    [string]$OutputDir = 'Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885',
    [string]$PoseTrack = 'Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\pose_coco133.jsonl'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$Python = Join-Path $WanGpRoot 'env_uv\Scripts\python.exe'
$Extractor = Join-Path $PSScriptRoot 'extract_behavior_profile.py'
$Inspector = Join-Path $PSScriptRoot 'inspect_behavior_profile.py'
$Manifest = Join-Path $OutputDir 'manifest.json'
$Csv = Join-Path $OutputDir 'motion_units.csv'
$Inspection = Join-Path $OutputDir 'profile_inspection.json'

foreach ($item in @(
    @{ Name='WanGP Python'; Path=$Python },
    @{ Name='Behavior extractor'; Path=$Extractor },
    @{ Name='Behavior inspector'; Path=$Inspector },
    @{ Name='Primary source'; Path=$Source },
    @{ Name='Full pose track'; Path=$PoseTrack }
)) {
    if (-not (Test-Path -LiteralPath $item.Path -PathType Leaf)) {
        throw ('Missing ' + $item.Name + ': ' + $item.Path)
    }
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

Write-Host 'PRIMARY BEHAVIOR PROFILE BUILD'
Write-Host '=============================='
Write-Host ('Python: ' + $Python)
Write-Host ('Source: ' + $Source)
Write-Host ('Pose track: ' + $PoseTrack)
Write-Host ('Output: ' + $OutputDir)
Write-Host ''
Write-Host 'This builds the renderer-independent behavior-profile/v1.'
Write-Host 'It does not run Wan-Animate-2.'
Write-Host ''

$ExtractArgs = @(
    $Extractor,
    '--source', $Source,
    '--output', $OutputDir,
    '--pose-track', $PoseTrack
)

$Saved = $ErrorActionPreference
try {
    $ErrorActionPreference = 'Continue'
    & $Python @ExtractArgs
    $ExtractExit = $LASTEXITCODE
} finally {
    $ErrorActionPreference = $Saved
}
if ($ExtractExit -ne 0) { throw "Behavior profile extraction failed with exit code $ExtractExit." }
if (-not (Test-Path -LiteralPath $Manifest -PathType Leaf)) { throw 'Behavior profile produced no manifest.json.' }
if (-not (Test-Path -LiteralPath $Csv -PathType Leaf)) { throw 'Behavior profile produced no motion_units.csv.' }

Write-Host ''
Write-Host 'Inspecting generated profile...'

$InspectArgs = @(
    $Inspector,
    '--manifest', $Manifest,
    '--csv', $Csv,
    '--output', $Inspection
)

$Saved = $ErrorActionPreference
try {
    $ErrorActionPreference = 'Continue'
    & $Python @InspectArgs
    $InspectExit = $LASTEXITCODE
} finally {
    $ErrorActionPreference = $Saved
}
if ($InspectExit -ne 0) { throw "Behavior profile structural inspection failed with exit code $InspectExit." }

Write-Host ''
Write-Host 'PRIMARY BEHAVIOR PROFILE: STRUCTURAL PASS'
Write-Host ('Manifest: ' + $Manifest)
Write-Host ('Motion units: ' + $Csv)
Write-Host ('Inspection: ' + $Inspection)
Write-Host ''
Write-Host 'Paste the final inspection output into ChatGPT before any behavioral-driver synthesis.'
