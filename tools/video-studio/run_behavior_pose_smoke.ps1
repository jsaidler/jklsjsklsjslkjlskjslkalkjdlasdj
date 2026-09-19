param(
    [double]$Start = 30.0,
    [double]$Duration = 5.0,
    [double]$Fps = 4.0,
    [string]$Provider = 'auto',
    [string]$WanGpRoot = 'Z:\AI\WanGP',
    [string]$Source = 'Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\VID_20260911_140124885.mp4'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$Python = Join-Path $WanGpRoot 'env_uv\Scripts\python.exe'
$Runner = Join-Path $PSScriptRoot 'extract_dwpose_track.py'
$OutputDir = 'Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\smoke'
$Output = Join-Path $OutputDir 'pose_smoke_coco133.jsonl'

if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) { throw "WanGP Python missing: $Python" }
if (-not (Test-Path -LiteralPath $Runner -PathType Leaf)) { throw "Pose extractor missing: $Runner" }
if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) { throw "Primary source missing: $Source" }
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

Write-Host 'BEHAVIOR POSE SMOKE'
Write-Host '==================='
Write-Host ('Python: ' + $Python)
Write-Host ('Source: ' + $Source)
Write-Host ('Start: ' + $Start + ' s')
Write-Host ('Duration: ' + $Duration + ' s')
Write-Host ('FPS: ' + $Fps)
Write-Host ('Provider: ' + $Provider)
Write-Host ('Output: ' + $Output)
Write-Host ''
Write-Host 'This is pose extraction only. It does not run Wan-Animate-2.'

$Args = @(
    $Runner,
    '--source', $Source,
    '--wangp-root', $WanGpRoot,
    '--output', $Output,
    '--start', $Start,
    '--duration', $Duration,
    '--fps', $Fps,
    '--provider', $Provider
)

$Saved = $ErrorActionPreference
try {
    $ErrorActionPreference = 'Continue'
    & $Python @Args
    $Exit = $LASTEXITCODE
} finally {
    $ErrorActionPreference = $Saved
}
if ($Exit -ne 0) { throw "Behavior pose smoke failed with exit code $Exit." }

Write-Host ''
Write-Host 'POSE SMOKE: PASS'
Write-Host ('Track: ' + $Output)
Write-Host ('Summary: ' + $Output + '.summary.json')
