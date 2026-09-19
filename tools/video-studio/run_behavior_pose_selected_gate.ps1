param(
    [double]$Start = 88.7,
    [double]$Duration = 5.0,
    [double]$Fps = 6.0,
    [double]$MinScore = 0.05,
    [string]$Provider = 'cpu',
    [string]$WanGpRoot = 'Z:\AI\WanGP',
    [string]$Source = 'Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\VID_20260911_140124885.mp4'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$Python = Join-Path $WanGpRoot 'env_uv\Scripts\python.exe'
$Extractor = Join-Path $PSScriptRoot 'extract_dwpose_track.py'
$Renderer = Join-Path $PSScriptRoot 'render_pose_overlay.py'
$OutputDir = 'Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\selected_gate'
$Track = Join-Path $OutputDir 'pose_gate_c3_88p7_93p7_coco133.jsonl'
$Overlay = Join-Path $OutputDir 'pose_gate_c3_88p7_93p7_overlay.mp4'

foreach ($item in @(
    @{ Name='WanGP Python'; Path=$Python },
    @{ Name='Pose extractor'; Path=$Extractor },
    @{ Name='Overlay renderer'; Path=$Renderer },
    @{ Name='Primary source'; Path=$Source }
)) {
    if (-not (Test-Path -LiteralPath $item.Path -PathType Leaf)) {
        throw ('Missing ' + $item.Name + ': ' + $item.Path)
    }
}
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

Write-Host 'SELECTED BEHAVIOR POSE GATE — C3'
Write-Host '================================'
Write-Host ('Source: ' + $Source)
Write-Host ('Window: ' + $Start + ' s -> ' + ($Start + $Duration) + ' s')
Write-Host ('FPS: ' + $Fps)
Write-Host ('Provider: ' + $Provider)
Write-Host ('Track: ' + $Track)
Write-Host ('Overlay: ' + $Overlay)
Write-Host ''
Write-Host 'This reruns DWPose only for the selected clean 5 s gate and then renders the overlay.'
Write-Host 'It does not run Wan-Animate-2.'
Write-Host ''

$ExtractArgs = @(
    $Extractor,
    '--source', $Source,
    '--wangp-root', $WanGpRoot,
    '--output', $Track,
    '--start', $Start,
    '--duration', $Duration,
    '--fps', $Fps,
    '--provider', $Provider
)

$Saved = $ErrorActionPreference
try {
    $ErrorActionPreference = 'Continue'
    & $Python @ExtractArgs
    $ExtractExit = $LASTEXITCODE
} finally {
    $ErrorActionPreference = $Saved
}
if ($ExtractExit -ne 0) { throw "Selected pose extraction failed with exit code $ExtractExit." }
if (-not (Test-Path -LiteralPath $Track -PathType Leaf)) { throw 'Selected pose extraction produced no track.' }

Write-Host ''
Write-Host 'Rendering visual overlay...'
$RenderArgs = @(
    $Renderer,
    '--source', $Source,
    '--track', $Track,
    '--output', $Overlay,
    '--fps', $Fps,
    '--min-score', $MinScore
)

$Saved = $ErrorActionPreference
try {
    $ErrorActionPreference = 'Continue'
    & $Python @RenderArgs
    $RenderExit = $LASTEXITCODE
} finally {
    $ErrorActionPreference = $Saved
}
if ($RenderExit -ne 0) { throw "Selected pose overlay failed with exit code $RenderExit." }
if (-not (Test-Path -LiteralPath $Overlay -PathType Leaf)) { throw 'Selected pose overlay was not produced.' }

Write-Host ''
Write-Host 'SELECTED POSE GATE RENDER: PASS'
Write-Host ('Track summary: ' + $Track + '.summary.json')
Write-Host ('Inspect and upload this overlay: ' + $Overlay)
