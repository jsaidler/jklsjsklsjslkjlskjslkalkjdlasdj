param(
    [string]$WanGpRoot = 'Z:\AI\WanGP',
    [string]$Library = 'Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\joao_motion_library_v1.json',
    [string]$OutputDir = 'Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\first_driver_v3',
    [string]$Audio = '',
    [double]$Duration = 4.5,
    [double]$Fps = 24.0,
    [double]$BlendDuration = 0.75
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$Python = Join-Path $WanGpRoot 'env_uv\Scripts\python.exe'
$Synth = Join-Path $PSScriptRoot 'synthesize_behavioral_pose_driver_v3.py'
$Inspector = Join-Path $PSScriptRoot 'inspect_behavioral_pose_driver_overlap.py'

foreach ($item in @(
    @{ Name='WanGP Python'; Path=$Python },
    @{ Name='v3 behavioral compositor'; Path=$Synth },
    @{ Name='Overlap-aware QA inspector'; Path=$Inspector },
    @{ Name='Unified motion library'; Path=$Library }
)) {
    if (-not (Test-Path -LiteralPath $item.Path -PathType Leaf)) {
        throw ('Missing ' + $item.Name + ': ' + $item.Path)
    }
}
if ($Audio -and -not (Test-Path -LiteralPath $Audio -PathType Leaf)) { throw ('Target audio missing: ' + $Audio) }
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

Write-Host 'FIRST MULTI-SOURCE BEHAVIORAL POSE DRIVER v3 + QA'
Write-Host '================================================='
Write-Host ('Library: ' + $Library)
Write-Host ('Output: ' + $OutputDir)
Write-Host ('Duration/FPS: ' + $Duration + ' s / ' + $Fps)
Write-Host ('Overlap blend: ' + $BlendDuration + ' s')
if ($Audio) { Write-Host ('Target audio: ' + $Audio) }
else { Write-Host 'Target audio: NONE (neutral synthesis QA only)' }
Write-Host 'No DWPose and no Wan-Animate-2 are invoked.'
Write-Host ''

Write-Host '[1/2] Synthesizing v3 driver...'
$Args = @(
    $Synth,
    '--library', $Library,
    '--output-dir', $OutputDir,
    '--duration', [string]$Duration,
    '--fps', [string]$Fps,
    '--blend-duration', [string]$BlendDuration
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
if ($Exit -ne 0) { throw ('v3 behavioral pose synthesis failed with exit code ' + $Exit) }

$Plan = Join-Path $OutputDir 'driver_plan.json'
$Track = Join-Path $OutputDir 'behavioral_driver_coco133.jsonl'
$Preview = Join-Path $OutputDir 'behavioral_driver_pose_preview.mp4'
$Qa = Join-Path $OutputDir 'driver_qa.json'
foreach ($p in @($Plan,$Track,$Preview)) {
    if (-not (Test-Path -LiteralPath $p -PathType Leaf)) { throw ('Expected v3 artifact missing: ' + $p) }
}

Write-Host ''
Write-Host '[2/2] Running overlap-aware numeric QA...'
try {
    $ErrorActionPreference = 'Continue'
    & $Python $Inspector '--track' $Track '--plan' $Plan '--output' $Qa
    $Exit = $LASTEXITCODE
} finally {
    $ErrorActionPreference = $Saved
}
if ($Exit -ne 0) { throw ('v3 numeric QA failed with exit code ' + $Exit) }
if (-not (Test-Path -LiteralPath $Qa -PathType Leaf)) { throw 'v3 QA JSON was not produced.' }

Write-Host ''
Write-Host 'FIRST DRIVER v3 + NUMERIC QA: COMPLETE'
Write-Host ('Plan: ' + $Plan)
Write-Host ('Pose track: ' + $Track)
Write-Host ('QA JSON: ' + $Qa)
Write-Host ('Upload this preview: ' + $Preview)
Write-Host 'Wan-Animate-2 remains blocked until v3 numeric + visual QA pass.'
