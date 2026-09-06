param(
    [string]$RepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$PipelineWorkspace = 'Z:\AI\RogueliteCharacterPipeline',
    [string]$ReferencePath = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "G3S-B3B-V3: FAIL - $Message" -ForegroundColor Red
    exit 1
}

function Invoke-PythonSafe {
    param(
        [Parameter(Mandatory=$true)][string]$Python,
        [Parameter(Mandatory=$true)][string[]]$Arguments
    )
    $saved = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $captured = @(& $Python @Arguments 2>&1)
        $code = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $saved
    }
    foreach ($line in $captured) { Write-Host ([string]$line) }
    return [int]$code
}

Write-Host ''
Write-Host 'Roguelite - G3S-B3B V3 REFERENCE-GUIDED PIXEL TRANSLATION SPIKE' -ForegroundColor Cyan
Write-Host 'Uses the approved Grok four-view body sheet as 2D visual reference only.'
Write-Host '128 px is the locked visible protagonist height in the 640x360 gameplay raster; it is NOT a requirement that every production frame be 128x128.' -ForegroundColor Yellow
Write-Host 'This run does NOT approve or commit a production B3B sprite.' -ForegroundColor Yellow
Write-Host ''

if (-not (Test-Path $RepoRoot -PathType Container)) { Fail "Repository root not found: $RepoRoot" }

$Python = 'Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\python_embeded\python.exe'
$Helper = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_b3b_v3_reference_guided_translation.py'
$ReferenceMarker = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_b3b_body_reference_approval.json'

if ([string]::IsNullOrWhiteSpace($ReferencePath)) {
    $ReferencePath = Join-Path $RepoRoot 'assets\source\characters\exilada\reference\exilada_body_turnaround_approved.png'
}

foreach ($p in @($Python,$Helper,$ReferenceMarker)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Required file missing: $p. Run git pull --ff-only first." }
}

$marker = Get-Content -LiteralPath $ReferenceMarker -Raw | ConvertFrom-Json
if ($marker.gate -ne 'G3S-B3B-BODY-REFERENCE' -or $marker.status -ne 'PASS_APPROVED_REFERENCE_NOT_PRODUCTION_ART') {
    Fail 'Approved body-reference marker is missing or has unexpected status.'
}

$ExpectedReferenceSha = '2773c199b3ff28ad5a72e33feb97201a9567a633f8466620084362fd9aae7474'
if ($marker.source.sha256 -ne $ExpectedReferenceSha) {
    Fail 'Body-reference marker SHA does not match the approved turnaround.'
}

if (-not (Test-Path $ReferencePath -PathType Leaf)) {
    Fail "Approved body reference file is not present at: $ReferencePath"
}

$ReferenceSha = (Get-FileHash -LiteralPath $ReferencePath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($ReferenceSha -ne $ExpectedReferenceSha) {
    Fail "Approved body reference SHA mismatch: got=$ReferenceSha expected=$ExpectedReferenceSha"
}

Write-Host '[OK] Approved Exilada body-reference marker verified.' -ForegroundColor Green
Write-Host "[OK] Approved reference file verified: $ReferencePath" -ForegroundColor Green
Write-Host '[LOCK] 128 px = visible standing-height target at native gameplay scale, not final frame-canvas dimensions.' -ForegroundColor Green
Write-Host '[LOCK] No hidden-3D RGB/mask/silhouette may become final visible art.' -ForegroundColor Green
Write-Host '[LOCK] Candidate is review-only and cannot be promoted automatically.' -ForegroundColor Green

$OutDir = Join-Path $PipelineWorkspace 'g3s_b3b_v3_reference_guided'
Remove-Item $OutDir -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Write-Host '[RUN] building native-scale visual translation candidate from the pinned approved reference...' -ForegroundColor Cyan
$code = Invoke-PythonSafe -Python $Python -Arguments @(
    $Helper,
    '--reference',$ReferencePath,
    '--output-dir',$OutDir
)
if ($code -ne 0) { Fail "V3 helper exited with code $code" }

$Contact = Join-Path $OutDir 'g3s_b3b_v3_contact_sheet.png'
$Candidate = Join-Path $OutDir 'g3s_b3b_v3_translation_candidate.png'
$Guide = Join-Path $OutDir 'g3s_b3b_v3_native_guide.png'
$Result = Join-Path $OutDir 'g3s_b3b_v3_result.json'
foreach ($p in @($Contact,$Candidate,$Guide,$Result)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Expected output missing: $p" }
}

Write-Host ''
Write-Host 'G3S-B3B-V3: REVIEW REQUIRED - NOT A PRODUCTION PASS' -ForegroundColor Yellow
Write-Host "CONTACT SHEET: $Contact"
Write-Host "CANDIDATE:     $Candidate"
Write-Host "GUIDE:         $Guide"
Write-Host "RESULT:        $Result"
Write-Host ''
Write-Host 'STOP. Share the contact sheet. Do not start B4/B5/C and do not promote the candidate before visual review.' -ForegroundColor Yellow
