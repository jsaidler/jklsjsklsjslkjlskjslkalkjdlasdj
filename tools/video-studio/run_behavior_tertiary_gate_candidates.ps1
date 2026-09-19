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
$Manifest = $Output + '.json'

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
if (-not (Test-Path -LiteralPath $Manifest -PathType Leaf)) { throw "SIENA sampler produced no manifest: $Manifest" }

$M = Get-Content -LiteralPath $Manifest -Raw | ConvertFrom-Json
$ExpectedName = 'SIENA_BRUTO.mp4'
$ActualName = [string]$M.source_name
$Duration = [double]$M.duration_s

Write-Host ''
Write-Host ('Manifest source: ' + $ActualName)
Write-Host ('Manifest duration: ' + $Duration + ' s')

if ($ActualName -ne $ExpectedName) {
    throw "Wrong source sampled. Expected $ExpectedName but manifest says $ActualName"
}
# Canonical SIENA source is approximately 113.3 s. Keep a generous integrity band,
# intended only to catch accidental reuse of the ~282 s secondary source or another file.
if ($Duration -lt 100.0 -or $Duration -gt 130.0) {
    throw "Unexpected SIENA duration: $Duration s. Expected the canonical ~113 s source."
}

Write-Host ''
Write-Host 'SIENA CANDIDATE SAMPLER: PASS'
Write-Host ('Verified source: ' + $ActualName)
Write-Host ('Verified duration: ' + $Duration + ' s')
Write-Host ('Contact sheet: ' + $Output)
Write-Host ('Manifest: ' + $Manifest)
Write-Host 'Upload this exact contact-sheet JPG. Its header now shows source filename and duration.'
