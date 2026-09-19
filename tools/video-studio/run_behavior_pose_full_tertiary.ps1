param(
    [double]$Fps = 6.0,
    [int]$LongSide = 960,
    [int]$ProgressEvery = 10,
    [string]$Provider = 'cpu',
    [string]$WanGpRoot = 'Z:\AI\WanGP',
    [string]$Source = 'Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\SIENA_BRUTO.mp4'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$Python = Join-Path $WanGpRoot 'env_uv\Scripts\python.exe'
$Extractor = Join-Path $PSScriptRoot 'extract_dwpose_track.py'
$OutputDir = 'Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\SIENA_BRUTO'
$Track = Join-Path $OutputDir 'pose_coco133.jsonl'
$Summary = $Track + '.summary.json'

foreach ($item in @(
    @{ Name='WanGP Python'; Path=$Python },
    @{ Name='Pose extractor'; Path=$Extractor },
    @{ Name='SIENA source'; Path=$Source }
)) {
    if (-not (Test-Path -LiteralPath $item.Path -PathType Leaf)) {
        throw ('Missing ' + $item.Name + ': ' + $item.Path)
    }
}
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

Write-Host 'FULL TERTIARY / SIENA BEHAVIOR POSE EXTRACTION'
Write-Host '================================================'
Write-Host ('Source: ' + $Source)
Write-Host ('FPS: ' + $Fps)
Write-Host ('Long side: ' + $LongSide)
Write-Host ('Provider: ' + $Provider)
Write-Host ('Progress heartbeat: every ' + $ProgressEvery + ' frames')
Write-Host ('Track: ' + $Track)
Write-Host ''
Write-Host 'This runs DWPose only. It does not run Wan-Animate-2.'
Write-Host 'All 133 keypoints are retained.'
Write-Host 'SIENA is currently validated for torso/posture/head; hand retrieval remains pending per-unit quality review.'
Write-Host ''

$Args = @(
    $Extractor,
    '--source', $Source,
    '--wangp-root', $WanGpRoot,
    '--output', $Track,
    '--fps', $Fps,
    '--long-side', $LongSide,
    '--provider', $Provider,
    '--progress-every', $ProgressEvery
)

$Saved = $ErrorActionPreference
try {
    $ErrorActionPreference = 'Continue'
    & $Python @Args
    $Exit = $LASTEXITCODE
} finally {
    $ErrorActionPreference = $Saved
}
if ($Exit -ne 0) { throw "Full SIENA behavior pose extraction failed with exit code $Exit." }
if (-not (Test-Path -LiteralPath $Track -PathType Leaf)) { throw 'Full SIENA pose extraction produced no track.' }
if (-not (Test-Path -LiteralPath $Summary -PathType Leaf)) { throw 'Full SIENA pose extraction produced no summary.' }

$J = Get-Content -LiteralPath $Summary -Raw | ConvertFrom-Json
if ([string]$J.schema -ne 'coco_wholebody_133') { throw ('Unexpected schema: ' + [string]$J.schema) }
if ([int]$J.frames -lt 1) { throw 'Full SIENA pose track contains no frames.' }

Write-Host ''
Write-Host 'FULL SIENA POSE TRACK: COMPLETE'
Write-Host ('Frames: ' + $J.frames)
Write-Host ('Display: ' + $J.display_width + 'x' + $J.display_height + ' / rotation=' + $J.rotation_degrees)
Write-Host ('Analysis: ' + $J.analysis_width + 'x' + $J.analysis_height)
Write-Host ('Provider: ' + $J.onnx_provider)
Write-Host ('Detector fallback: ' + $J.detector_fallback_frames + '/' + $J.frames + ' (' + $J.detector_fallback_ratio + ')')
Write-Host ('Mean keypoint score: ' + $J.mean_keypoint_score)
Write-Host ('Track: ' + $Track)
Write-Host ('Summary: ' + $Summary)
Write-Host ''
Write-Host 'Paste the final summary/output into ChatGPT before building the SIENA behavior profile.'
