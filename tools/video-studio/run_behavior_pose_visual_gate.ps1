param(
    [string]$WanGpRoot = 'Z:\AI\WanGP',
    [string]$Source = 'Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\VID_20260911_140124885.mp4',
    [string]$Track = 'Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\pose_smoke_5s.jsonl',
    [string]$Output = 'Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\pose_smoke_5s_overlay.mp4',
    [double]$Fps = 6.0,
    [double]$MinScore = 0.05
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$Python = Join-Path $WanGpRoot 'env_uv\Scripts\python.exe'
$Renderer = Join-Path $PSScriptRoot 'render_pose_overlay.py'

foreach ($item in @(
    @{ Name='WanGP Python'; Path=$Python },
    @{ Name='Overlay renderer'; Path=$Renderer },
    @{ Name='Primary source'; Path=$Source },
    @{ Name='Pose smoke track'; Path=$Track }
)) {
    if (-not (Test-Path -LiteralPath $item.Path -PathType Leaf)) {
        throw ('Missing ' + $item.Name + ': ' + $item.Path)
    }
}

Write-Host 'BEHAVIOR POSE VISUAL GATE'
Write-Host '========================='
Write-Host ('Python: ' + $Python)
Write-Host ('Source: ' + $Source)
Write-Host ('Track: ' + $Track)
Write-Host ('Output: ' + $Output)
Write-Host ('FPS: ' + $Fps)
Write-Host ('Minimum displayed score: ' + $MinScore)
Write-Host ''
Write-Host 'This only renders an inspection overlay from the existing pose JSONL.'
Write-Host 'It does not run DWPose and does not run Wan-Animate-2.'
Write-Host ''

$Args = @(
    $Renderer,
    '--source', $Source,
    '--track', $Track,
    '--output', $Output,
    '--fps', $Fps,
    '--min-score', $MinScore
)

$Saved = $ErrorActionPreference
try {
    $ErrorActionPreference = 'Continue'
    & $Python @Args
    $Exit = $LASTEXITCODE
} finally {
    $ErrorActionPreference = $Saved
}
if ($Exit -ne 0) { throw "Behavior pose visual gate failed with exit code $Exit." }

if (-not (Test-Path -LiteralPath $Output -PathType Leaf)) {
    throw 'Visual gate completed without producing the expected overlay.'
}

Write-Host ''
Write-Host 'POSE VISUAL GATE RENDER: PASS'
Write-Host ('Open this video and inspect body/hands/face tracking: ' + $Output)
