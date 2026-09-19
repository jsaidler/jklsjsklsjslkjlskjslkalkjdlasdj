param(
    [string]$WanGpRoot = 'Z:\AI\WanGP',
    [string]$Source = 'Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\VID_20260819_124008056.mp4',
    [string]$PoseTrack = 'Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260819_124008056\pose_coco133.jsonl'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$Python = Join-Path $WanGpRoot 'env_uv\Scripts\python.exe'
$Auditor = Join-Path $PSScriptRoot 'audit_facial_track_quality.py'
$Renderer = Join-Path $PSScriptRoot 'render_facial_quality_review.py'
$OutDir = 'Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260819_124008056'
$Audit = Join-Path $OutDir 'facial_quality_audit.json'
$Sheet = Join-Path $OutDir 'facial_quality_review_sheet.jpg'

foreach ($item in @(
    @{ Name='WanGP Python'; Path=$Python },
    @{ Name='Facial auditor'; Path=$Auditor },
    @{ Name='Facial review renderer'; Path=$Renderer },
    @{ Name='Secondary source'; Path=$Source },
    @{ Name='Secondary pose track'; Path=$PoseTrack }
)) {
    if (-not (Test-Path -LiteralPath $item.Path -PathType Leaf)) {
        throw ('Missing ' + $item.Name + ': ' + $item.Path)
    }
}
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Write-Host 'SECONDARY FACIAL QUALITY AUDIT'
Write-Host '=============================='
Write-Host ('Pose track: ' + $PoseTrack)
Write-Host 'Policy: source-relative Tukey outer fences (3*IQR); temporal jumps are review-only.'
Write-Host 'No DWPose and no Wan-Animate-2 are invoked.'
Write-Host ''

& $Python $Auditor --pose-track $PoseTrack --output $Audit
if ($LASTEXITCODE -ne 0) { throw 'Facial quality audit failed.' }

$J = Get-Content -LiteralPath $Audit -Raw | ConvertFrom-Json
if ([int]$J.static_hard_suspect_frames -gt 0 -or [int]$J.normalization_failed_frames -gt 0 -or [int]$J.temporal_review_suspect_frames -gt 0) {
    Write-Host ''
    Write-Host 'Rendering suspect-frame contact sheet...'
    & $Python $Renderer --source $Source --audit $Audit --output $Sheet --max-items 24
    if ($LASTEXITCODE -ne 0) { throw 'Facial quality review sheet render failed.' }
    Write-Host ('Review sheet: ' + $Sheet)
} else {
    Write-Host ''
    Write-Host 'No facial QA suspects detected; review sheet not needed.'
}

Write-Host ''
Write-Host 'SECONDARY FACIAL QUALITY AUDIT: COMPLETE'
Write-Host ('Audit JSON: ' + $Audit)
if (Test-Path -LiteralPath $Sheet -PathType Leaf) { Write-Host ('Upload this JPG: ' + $Sheet) }
Write-Host 'Paste the complete terminal output into ChatGPT before facial sidecar/profile construction.'
