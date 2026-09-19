param(
    [string]$WanGpRoot = 'Z:\AI\WanGP',
    [string]$PoseTrack = 'Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260819_124008056\pose_coco133.jsonl'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$Python = Join-Path $WanGpRoot 'env_uv\Scripts\python.exe'
$Inspector = Join-Path $PSScriptRoot 'inspect_facial_track.py'
$OutDir = 'Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260819_124008056'
$FullOut = Join-Path $OutDir 'facial_probe_full.json'
$GateOut = Join-Path $OutDir 'facial_probe_c3_83p6_88p6.json'

foreach ($item in @(
    @{ Name='WanGP Python'; Path=$Python },
    @{ Name='Facial inspector'; Path=$Inspector },
    @{ Name='Secondary full pose track'; Path=$PoseTrack }
)) {
    if (-not (Test-Path -LiteralPath $item.Path -PathType Leaf)) {
        throw ('Missing ' + $item.Name + ': ' + $item.Path)
    }
}
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Write-Host 'SECONDARY FACIAL DESCRIPTOR PROBE'
Write-Host '================================='
Write-Host ('Pose track: ' + $PoseTrack)
Write-Host 'No DWPose and no Wan-Animate-2 are invoked.'
Write-Host ''

Write-Host '--- FULL TRACK ---'
& $Python $Inspector --pose-track $PoseTrack --output $FullOut
if ($LASTEXITCODE -ne 0) { throw 'Full facial descriptor probe failed.' }

Write-Host ''
Write-Host '--- VALIDATED C3 GATE 83.6-88.6 s ---'
& $Python $Inspector --pose-track $PoseTrack --start 83.6 --duration 5.0 --output $GateOut
if ($LASTEXITCODE -ne 0) { throw 'C3 facial descriptor probe failed.' }

Write-Host ''
Write-Host 'SECONDARY FACIAL PROBE: COMPLETE'
Write-Host ('Full JSON: ' + $FullOut)
Write-Host ('C3 JSON: ' + $GateOut)
Write-Host 'Paste the complete terminal output into ChatGPT before building the secondary profile.'
