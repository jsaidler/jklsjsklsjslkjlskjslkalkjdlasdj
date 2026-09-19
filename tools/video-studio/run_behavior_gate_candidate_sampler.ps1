param(
    [string]$WanGpRoot = 'Z:\AI\WanGP',
    [string]$Source = 'Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\VID_20260911_140124885.mp4'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$Python = Join-Path $WanGpRoot 'env_uv\Scripts\python.exe'
$Runner = Join-Path $PSScriptRoot 'sample_behavior_gate_candidates.py'
$OutputDir = 'Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1\VID_20260911_140124885\gate_candidates'
$Output = Join-Path $OutputDir 'candidate_contact_sheet.jpg'

if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) { throw "WanGP Python missing: $Python" }
if (-not (Test-Path -LiteralPath $Runner -PathType Leaf)) { throw "Candidate sampler missing: $Runner" }
if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) { throw "Primary source missing: $Source" }
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

Write-Host 'BEHAVIOR GATE CANDIDATE SAMPLER'
Write-Host '==============================='
Write-Host ('Python: ' + $Python)
Write-Host ('Source: ' + $Source)
Write-Host ('Output: ' + $Output)
Write-Host ''
Write-Host 'This samples source frames only. It does not run DWPose and does not run Wan-Animate-2.'

$Args = @(
    $Runner,
    '--source', $Source,
    '--output', $Output,
    '--window', '5',
    '--candidates', '8',
    '--margin', '10'
)

$Saved = $ErrorActionPreference
try {
    $ErrorActionPreference = 'Continue'
    & $Python @Args
    $Exit = $LASTEXITCODE
} finally {
    $ErrorActionPreference = $Saved
}
if ($Exit -ne 0) { throw "Behavior gate candidate sampler failed with exit code $Exit." }

Write-Host ''
Write-Host 'CANDIDATE SAMPLER: PASS'
Write-Host ('Contact sheet: ' + $Output)
Write-Host ('Manifest: ' + $Output + '.json')
Write-Host 'Upload the contact-sheet JPG for visual selection of a clean 5-second gate window.'
