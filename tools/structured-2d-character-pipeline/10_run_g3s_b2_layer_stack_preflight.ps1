param(
    [string]$RepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$PipelineWorkspace = 'Z:\AI\RogueliteCharacterPipeline'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "G3S-B2: FAIL - $Message" -ForegroundColor Red
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
Write-Host 'Roguelite - G3S-B2 LAYER STACK PREFLIGHT' -ForegroundColor Cyan
Write-Host 'Corrects G3S-B V1 architecture: body base, hair and clothing must be separate persistent layers.'
Write-Host 'This gate does NOT invent hidden body pixels. It exposes exactly where the body base is still missing under hair/clothing.' -ForegroundColor Yellow
Write-Host ''

if (-not (Test-Path $RepoRoot -PathType Container)) { Fail "Repository root not found: $RepoRoot" }

$Python = 'Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\python_embeded\python.exe'
$Control = Join-Path $PipelineWorkspace 'g3s_a_control\g3s_a_control_official_raw.png'
$FailureMarker = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_b_v1_failure.json'
$Helper = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_b2_layer_stack_preflight.py'
$Spec = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_b2_layer_stack_spec_v1.json'

foreach ($p in @($Python,$Control,$FailureMarker,$Helper,$Spec)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Required file missing: $p. Run git pull --ff-only first." }
}

$failure = Get-Content -LiteralPath $FailureMarker -Raw | ConvertFrom-Json
if ($failure.gate -ne 'G3S-B-PERSISTENT-PART-DECOMPOSITION-V1' -or $failure.status -ne 'FAIL') {
    Fail 'G3S-B V1 is not canonically closed FAIL; refusing to run B2.'
}

$expectedControlSha = 'ce6d86e65b170e57a390e596a0f96d7e0c62d010bd5382835f83f2b3fc9fe08e'
$controlSha = (Get-FileHash -LiteralPath $Control -Algorithm SHA256).Hash.ToLowerInvariant()
if ($controlSha -ne $expectedControlSha) {
    Fail "Qwen control SHA mismatch: got=$controlSha expected=$expectedControlSha"
}

Write-Host "[OK] Pinned scaffold provenance SHA256 $controlSha" -ForegroundColor Green
Write-Host '[OK] G3S-B V1 failure acknowledged.' -ForegroundColor Green
Write-Host '[LOCK] Body base = complete unclothed anatomy; hair = separate layer; clothing = overlays; chains = accessories.' -ForegroundColor Green

$OutDir = Join-Path $PipelineWorkspace 'g3s_b2_layer_stack'
Remove-Item $OutDir -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Write-Host '[RUN] deterministic material/layer partition + hidden-body requirement map...' -ForegroundColor Cyan
$code = Invoke-PythonSafe -Python $Python -Arguments @(
    $Helper,
    '--control',$Control,
    '--spec',$Spec,
    '--output-dir',$OutDir
)
if ($code -ne 0) { Fail "G3S-B2 helper exited with code $code" }

$Contact = Join-Path $OutDir 'g3s_b2_contact_sheet.png'
$Manifest = Join-Path $OutDir 'g3s_b2_layer_manifest.json'
$Result = Join-Path $OutDir 'g3s_b2_result.json'
foreach ($p in @($Contact,$Manifest,$Result)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Expected output missing: $p" }
}

Write-Host ''
Write-Host 'G3S-B2: REVIEW REQUIRED' -ForegroundColor Yellow
Write-Host "CONTACT SHEET: $Contact"
Write-Host "MANIFEST:      $Manifest"
Write-Host "RESULT:        $Result"
Write-Host ''
Write-Host 'STOP. Review material separation and magenta hidden-body zones. Do not start G3S-C; next gate is body-base completion.' -ForegroundColor Yellow
