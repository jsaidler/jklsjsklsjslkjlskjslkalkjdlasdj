param(
    [string]$RepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$PipelineWorkspace = 'Z:\AI\RogueliteCharacterPipeline',
    [string]$ReferencePath = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "G3S-B3B-V4: FAIL - $Message" -ForegroundColor Red
    exit 1
}

Write-Host ''
Write-Host 'Roguelite - G3S-B3B V4 PIXEL-REFERENCE CANDIDATE' -ForegroundColor Cyan
Write-Host 'Uses the user-locked pixel-art turnaround as the visual source.'
Write-Host 'No render-to-pixel conversion, palette synthesis, anatomy repair or procedural silhouette authoring.' -ForegroundColor Green
Write-Host 'Output is review-only and cannot be promoted automatically.' -ForegroundColor Yellow
Write-Host ''

if (-not (Test-Path $RepoRoot -PathType Container)) { Fail "Repository root not found: $RepoRoot" }

$Python = 'Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\python_embeded\python.exe'
$Helper = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_b3b_v4_extract_pixel_reference_candidate.py'

foreach ($p in @($Python,$Helper)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Required file missing: $p. Run git pull --ff-only first." }
}

$OutDir = Join-Path $PipelineWorkspace 'g3s_b3b_v4_pixel_reference'
Remove-Item $OutDir -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$argsList = @(
    $Helper,
    '--repo-root',$RepoRoot,
    '--output-dir',$OutDir
)
if (-not [string]::IsNullOrWhiteSpace($ReferencePath)) {
    $argsList += @('--reference',$ReferencePath)
}

Write-Host '[RUN] locating locked pixel-art reference by SHA and building native candidate...' -ForegroundColor Cyan
& $Python @argsList
if ($LASTEXITCODE -ne 0) { Fail "V4 helper exited with code $LASTEXITCODE" }

$Contact = Join-Path $OutDir 'g3s_b3b_v4_contact_sheet.png'
$Candidate = Join-Path $OutDir 'g3s_b3b_v4_pixel_reference_candidate.png'
$Gameplay = Join-Path $OutDir 'g3s_b3b_v4_gameplay_preview_640x360.png'
$Result = Join-Path $OutDir 'g3s_b3b_v4_result.json'
foreach ($p in @($Contact,$Candidate,$Gameplay,$Result)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Expected output missing: $p" }
}

Write-Host ''
Write-Host 'G3S-B3B-V4: REVIEW REQUIRED - NOT A PRODUCTION PASS' -ForegroundColor Yellow
Write-Host "CONTACT SHEET: $Contact"
Write-Host "CANDIDATE:     $Candidate"
Write-Host "GAMEPLAY:      $Gameplay"
Write-Host "RESULT:        $Result"
Write-Host ''
Write-Host 'STOP. Share the contact sheet. Do not start B4/B5/C and do not promote before visual review.' -ForegroundColor Yellow
