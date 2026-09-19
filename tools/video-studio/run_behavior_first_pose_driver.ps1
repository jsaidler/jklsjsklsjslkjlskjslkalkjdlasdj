param(
    [string]$WanGpRoot = 'Z:\AI\WanGP',
    [string]$Library = 'Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\joao_motion_library_v1.json',
    [string]$OutputDir = 'Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\first_driver',
    [string]$Audio = '',
    [double]$Duration = 4.5,
    [double]$Fps = 24.0
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$Python = Join-Path $WanGpRoot 'env_uv\Scripts\python.exe'
$Synth = Join-Path $PSScriptRoot 'synthesize_behavioral_pose_driver.py'

foreach ($item in @(
    @{ Name='WanGP Python'; Path=$Python },
    @{ Name='Behavioral pose-driver synthesizer'; Path=$Synth },
    @{ Name='Unified motion library'; Path=$Library }
)) {
    if (-not (Test-Path -LiteralPath $item.Path -PathType Leaf)) {
        throw ('Missing ' + $item.Name + ': ' + $item.Path)
    }
}
if ($Audio -and -not (Test-Path -LiteralPath $Audio -PathType Leaf)) { throw ('Target audio missing: ' + $Audio) }
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

Write-Host 'FIRST MULTI-SOURCE BEHAVIORAL POSE DRIVER'
Write-Host '=========================================='
Write-Host ('Library: ' + $Library)
Write-Host ('Duration: ' + $Duration + ' s')
Write-Host ('FPS: ' + $Fps)
if ($Audio) {
    Write-Host ('Target audio: ' + $Audio)
} else {
    Write-Host 'Target audio: NONE (neutral 4.5 s synthesis QA target; not production retrieval)'
}
Write-Host 'Wan-Animate-2 is NOT invoked.'
Write-Host ''

$Args = @(
    $Synth,
    '--library', $Library,
    '--output-dir', $OutputDir,
    '--duration', [string]$Duration,
    '--fps', [string]$Fps
)
if ($Audio) { $Args += @('--audio', $Audio) }

$Saved = $ErrorActionPreference
try {
    $ErrorActionPreference = 'Continue'
    & $Python @Args
    $Exit = $LASTEXITCODE
} finally {
    $ErrorActionPreference = $Saved
}
if ($Exit -ne 0) { throw ('Behavioral pose-driver synthesis failed with exit code ' + $Exit) }

$Plan = Join-Path $OutputDir 'driver_plan.json'
$Track = Join-Path $OutputDir 'behavioral_driver_coco133.jsonl'
$Preview = Join-Path $OutputDir 'behavioral_driver_pose_preview.mp4'
foreach ($p in @($Plan,$Track,$Preview)) {
    if (-not (Test-Path -LiteralPath $p -PathType Leaf)) { throw ('Expected driver artifact missing: ' + $p) }
}

Write-Host ''
Write-Host 'FIRST BEHAVIORAL POSE DRIVER: COMPLETE'
Write-Host ('Plan: ' + $Plan)
Write-Host ('Pose track: ' + $Track)
Write-Host ('Upload this preview for QA: ' + $Preview)
Write-Host 'Do not run Wan-Animate-2 before the pose-driver preview passes.'
