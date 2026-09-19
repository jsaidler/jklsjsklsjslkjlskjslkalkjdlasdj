param(
    [string]$WanGpRoot = 'Z:\AI\WanGP',
    [string]$Source = 'Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\VID_20260819_124008056.mp4',
    [string]$OutputDir = 'Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260819_124008056',
    [string]$PoseTrack = 'Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260819_124008056\pose_coco133.jsonl',
    [string]$Audit = 'Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260819_124008056\facial_quality_audit.json'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$Python = Join-Path $WanGpRoot 'env_uv\Scripts\python.exe'
$BehaviorExtractor = Join-Path $PSScriptRoot 'extract_behavior_profile.py'
$BehaviorInspector = Join-Path $PSScriptRoot 'inspect_behavior_profile.py'
$FacialBuilder = Join-Path $PSScriptRoot 'build_facial_behavior_sidecar.py'
$FacialInspector = Join-Path $PSScriptRoot 'inspect_facial_behavior_sidecar.py'

$Manifest = Join-Path $OutputDir 'manifest.json'
$Csv = Join-Path $OutputDir 'motion_units.csv'
$BehaviorInspection = Join-Path $OutputDir 'profile_inspection.json'
$FacialSidecar = Join-Path $OutputDir 'facial_behavior_profile.json'
$FacialInspection = Join-Path $OutputDir 'facial_sidecar_inspection.json'

foreach ($item in @(
    @{ Name='WanGP Python'; Path=$Python },
    @{ Name='Behavior extractor'; Path=$BehaviorExtractor },
    @{ Name='Behavior inspector'; Path=$BehaviorInspector },
    @{ Name='Facial sidecar builder'; Path=$FacialBuilder },
    @{ Name='Facial sidecar inspector'; Path=$FacialInspector },
    @{ Name='Secondary source'; Path=$Source },
    @{ Name='Secondary full pose track'; Path=$PoseTrack },
    @{ Name='Facial quality audit'; Path=$Audit }
)) {
    if (-not (Test-Path -LiteralPath $item.Path -PathType Leaf)) {
        throw ('Missing ' + $item.Name + ': ' + $item.Path)
    }
}
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

Write-Host 'SECONDARY BEHAVIOR PROFILE + FACIAL SIDECAR BUILD'
Write-Host '================================================='
Write-Host ('Source: ' + $Source)
Write-Host ('Pose track: ' + $PoseTrack)
Write-Host ('Facial audit: ' + $Audit)
Write-Host ''
Write-Host 'No DWPose and no Wan-Animate-2 are invoked.'
Write-Host 'Hard facial suspects are excluded only from facial descriptors, not from the base behavior profile.'
Write-Host ''

& $Python $BehaviorExtractor --source $Source --output $OutputDir --pose-track $PoseTrack
if ($LASTEXITCODE -ne 0) { throw 'Secondary behavior-profile build failed.' }
if (-not (Test-Path -LiteralPath $Manifest -PathType Leaf)) { throw 'Secondary manifest missing after build.' }
if (-not (Test-Path -LiteralPath $Csv -PathType Leaf)) { throw 'Secondary motion_units.csv missing after build.' }

Write-Host ''
Write-Host 'Inspecting base behavior profile...'
& $Python $BehaviorInspector --manifest $Manifest --csv $Csv --output $BehaviorInspection
if ($LASTEXITCODE -ne 0) { throw 'Secondary base behavior profile structural inspection failed.' }

Write-Host ''
Write-Host 'Building facial-behavior-profile/v1 sidecar...'
& $Python $FacialBuilder --manifest $Manifest --pose-track $PoseTrack --audit $Audit --output $FacialSidecar
if ($LASTEXITCODE -ne 0) { throw 'Secondary facial sidecar build failed.' }

Write-Host ''
Write-Host 'Inspecting facial sidecar alignment/quality...'
& $Python $FacialInspector --sidecar $FacialSidecar --manifest $Manifest --output $FacialInspection
if ($LASTEXITCODE -ne 0) { throw 'Secondary facial sidecar inspection failed.' }

Write-Host ''
Write-Host 'SECONDARY PROFILE + FACIAL SIDECAR: STRUCTURAL PASS'
Write-Host ('Manifest: ' + $Manifest)
Write-Host ('Behavior inspection: ' + $BehaviorInspection)
Write-Host ('Facial sidecar: ' + $FacialSidecar)
Write-Host ('Facial inspection: ' + $FacialInspection)
Write-Host ''
Write-Host 'Paste the complete terminal output into ChatGPT before secondary curation.'
