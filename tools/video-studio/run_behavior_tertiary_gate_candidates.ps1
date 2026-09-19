param(
    [string]$WanGpRoot = 'Z:\AI\WanGP',
    [string]$Source = 'Z:\AI\VideoStudio\profiles\joao\behavior\avatar_v\sources\SIENA_BRUTO.mp4'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$Python = Join-Path $WanGpRoot 'env_uv\Scripts\python.exe'
$Runner = Join-Path $PSScriptRoot 'sample_behavior_gate_candidates.py'
$Stem = [System.IO.Path]::GetFileNameWithoutExtension($Source)
$OutputDir = Join-Path 'Z:\AI\VideoStudio\profiles\joao\behavior\profile_v1' (Join-Path $Stem 'gate_candidates')
$Output = Join-Path $OutputDir 'candidate_contact_sheet.jpg'

if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) { throw "WanGP Python missing: $Python" }
if (-not (Test-Path -LiteralPath $Runner -PathType Leaf)) { throw "Candidate sampler missing: $Runner" }
if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) { throw "SIENA source missing: $Source" }
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

Write-Host 'TERTIARY / SIENA BEHAVIOR GATE CANDIDATE SAMPLER'
Write-Host '================================================='
Write-Host ('Python: ' + $Python)
Write-Host ('Source: ' + $Source)
Write-Host ('Output: ' + $Output)
Write-Host ''
Write-Host 'Purpose: choose a clean 5-second gesture/posture gate and identify prop/occlusion spans before any DWPose full pass.'
Write-Host 'This samples source frames only. It does not run DWPose and does not run Wan-Animate-2.'

$Args = @(
    $Runner,
    '--source', $Source,
    '--output', $Output,
    '--window', '5',
    '--candidates', '8',
    '--margin', '5'
)

$Saved = $ErrorActionPreference
try {
    $ErrorActionPreference = 'Continue'
    & $Python @Args
    $Exit = $LASTEXITCODE
} finally {
    $ErrorActionPreference = $Saved
}
if ($Exit -ne 0) { throw "SIENA behavior gate candidate sampler failed with exit code $Exit." }

Write-Host ''
Write-Host 'SIENA CANDIDATE SAMPLER: PASS'
Write-Host ('Contact sheet: ' + $Output)
Write-Host ('Manifest: ' + $Output + '.json')
Write-Host 'Upload the contact-sheet JPG. We will choose for useful free gesture/posture and mark prop/occlusion intervals separately.'
