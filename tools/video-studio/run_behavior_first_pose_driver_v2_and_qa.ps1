param(
    [string]$WanGpRoot = 'Z:\AI\WanGP',
    [string]$Library = 'Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\joao_motion_library_v1.json',
    [string]$OutputDir = 'Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\unified\first_driver_v2',
    [string]$Audio = '',
    [double]$Duration = 4.5,
    [double]$Fps = 24.0,
    [double]$BlendDuration = 0.75
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$Python = Join-Path $WanGpRoot 'env_uv\Scripts\python.exe'
$Synth = Join-Path $PSScriptRoot 'synthesize_behavioral_pose_driver_v2.py'
$Inspector = Join-Path $PSScriptRoot 'inspect_behavioral_pose_driver_overlap.py'

foreach ($item in @(
    @{ Name='WanGP Python'; Path=$Python },
    @{ Name='Unified motion library'; Path=$Library },
    @{ Name='Driver v2 synthesizer'; Path=$Synth },
    @{ Name='Overlap QA inspector'; Path=$Inspector }
)) {
    if (-not (Test-Path -LiteralPath $item.Path -PathType Leaf)) {
        throw ('Missing ' + $item.Name + ': ' + $item.Path)
    }
}
if ($Audio -and -not (Test-Path -LiteralPath $Audio -PathType Leaf)) { throw ('Target audio missing: ' + $Audio) }
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

Write-Host 'FIRST MULTI-SOURCE BEHAVIORAL POSE DRIVER v2 + QA'
Write-Host '================================================='
Write-Host ('Library: ' + $Library)
Write-Host ('Output: ' + $OutputDir)
Write-Host ('Duration/FPS: ' + $Duration + ' s / ' + $Fps)
Write-Host ('Overlap blend: ' + $BlendDuration + ' s')
if ($Audio) { Write-Host ('Target audio: ' + $Audio) }
else { Write-Host 'Target audio: NONE (neutral synthesis QA only)' }
Write-Host 'No DWPose and no Wan-Animate-2 are invoked.'
Write-Host ''

$Args = @($Synth,'--library',$Library,'--output-dir',$OutputDir,'--duration',[string]$Duration,'--fps',[string]$Fps,'--blend-duration',[string]$BlendDuration)
if ($Audio) { $Args += @('--audio',$Audio) }

Write-Host '[1/2] Synthesizing v2 driver...'
$Saved = $ErrorActionPreference
try {
    $ErrorActionPreference = 'Continue'
    & $Python @Args
    $Exit = $LASTEXITCODE
} finally { $ErrorActionPreference = $Saved }
if ($Exit -ne 0) { throw ('Driver v2 synthesis failed with exit code ' + $Exit) }

$Plan = Join-Path $OutputDir 'driver_plan.json'
$Track = Join-Path $OutputDir 'behavioral_driver_coco133.jsonl'
$Preview = Join-Path $OutputDir 'behavioral_driver_pose_preview.mp4'
$Qa = Join-Path $OutputDir 'driver_qa.json'
foreach ($p in @($Plan,$Track,$Preview)) {
    if (-not (Test-Path -LiteralPath $p -PathType Leaf)) { throw ('Expected v2 artifact missing: ' + $p) }
}

Write-Host ''
Write-Host '[2/2] Running overlap-aware numeric QA...'
$Saved = $ErrorActionPreference
try {
    $ErrorActionPreference = 'Continue'
    & $Python $Inspector '--track' $Track '--plan' $Plan '--output' $Qa
    $Exit = $LASTEXITCODE
} finally { $ErrorActionPreference = $Saved }
if ($Exit -ne 0) { throw ('Driver v2 QA failed with exit code ' + $Exit) }
if (-not (Test-Path -LiteralPath $Qa -PathType Leaf)) { throw 'Driver v2 QA JSON missing.' }

Write-Host ''
Write-Host 'FIRST DRIVER v2 + NUMERIC QA: COMPLETE'
Write-Host ('Plan: ' + $Plan)
Write-Host ('Pose track: ' + $Track)
Write-Host ('QA JSON: ' + $Qa)
Write-Host ('Upload this preview: ' + $Preview)
Write-Host 'Wan-Animate-2 remains blocked until v2 numeric + visual QA pass.'
