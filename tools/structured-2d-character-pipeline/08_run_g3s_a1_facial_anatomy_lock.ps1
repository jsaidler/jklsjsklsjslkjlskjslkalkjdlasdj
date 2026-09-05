param(
    [string]$RepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$PipelineWorkspace = 'Z:\AI\RogueliteCharacterPipeline'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "G3S-A1: FAIL - $Message" -ForegroundColor Red
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
Write-Host 'Roguelite - G3S-A1 FACIAL / ANATOMY LOCK' -ForegroundColor Cyan
Write-Host 'V1 is closed FAIL because its mouth pixels existed technically but did not read visually.'
Write-Host 'This gate strengthens native facial structure and exposes face/hands/feet diagnostics before any animation.' -ForegroundColor Yellow
Write-Host ''

if (-not (Test-Path $RepoRoot -PathType Container)) { Fail "Repository root not found: $RepoRoot" }

$Python = 'Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\python_embeded\python.exe'
$Control = Join-Path $PipelineWorkspace 'g3s_a_control\g3s_a_control_official_raw.png'
$FailureMarker = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_a_authored_v1_failure.json'
$Helper = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_a1_facial_anatomy_lock.py'
$Patch = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_a_anatomy_patch_v2.json'
$BaseHelper = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_a_authored_native_v1.py'

foreach ($p in @($Python,$Control,$FailureMarker,$Helper,$Patch,$BaseHelper)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Required file missing: $p. Run git pull --ff-only first." }
}

$failure = Get-Content -LiteralPath $FailureMarker -Raw | ConvertFrom-Json
if ($failure.gate -ne 'G3S-A-AUTHORED-NATIVE-V1' -or $failure.status -ne 'FAIL') {
    Fail 'Authored V1 is not canonically closed FAIL; refusing to run G3S-A1.'
}

$expectedControlSha = 'ce6d86e65b170e57a390e596a0f96d7e0c62d010bd5382835f83f2b3fc9fe08e'
$controlSha = (Get-FileHash -LiteralPath $Control -Algorithm SHA256).Hash.ToLowerInvariant()
if ($controlSha -ne $expectedControlSha) {
    Fail "Qwen control SHA mismatch: got=$controlSha expected=$expectedControlSha"
}
Write-Host "[OK] Qwen design scaffold pinned SHA256 $controlSha" -ForegroundColor Green
Write-Host '[OK] Authored V1 failure marker acknowledged.' -ForegroundColor Green

$OutDir = Join-Path $PipelineWorkspace 'g3s_a1_anatomy_lock'
Remove-Item $OutDir -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Write-Host '[RUN] native 128 facial/anatomy lock + explicit diagnostics...' -ForegroundColor Cyan
$code = Invoke-PythonSafe -Python $Python -Arguments @(
    $Helper,
    '--control',$Control,
    '--patch',$Patch,
    '--output-dir',$OutDir
)
if ($code -ne 0) { Fail "G3S-A1 helper exited with code $code" }

$Contact = Join-Path $OutDir 'g3s_a1_contact_sheet.png'
$Candidate = Join-Path $OutDir 'g3s_a1_candidate_v2.png'
$Face = Join-Path $OutDir 'g3s_a1_face_zoom.png'
$Extremities = Join-Path $OutDir 'g3s_a1_extremities_zoom.png'
$Result = Join-Path $OutDir 'g3s_a1_result.json'
foreach ($p in @($Contact,$Candidate,$Face,$Extremities,$Result)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Expected output missing: $p" }
}

Write-Host ''
Write-Host 'G3S-A1: REVIEW REQUIRED' -ForegroundColor Yellow
Write-Host "CONTACT SHEET: $Contact"
Write-Host "CANDIDATE:     $Candidate"
Write-Host "FACE ZOOM:     $Face"
Write-Host "EXTREMITIES:   $Extremities"
Write-Host "RESULT:        $Result"
Write-Host ''
Write-Host 'STOP. Mouth readability is judged visually, not merely by pixel existence. Do not start G3S-B or animation.' -ForegroundColor Yellow
