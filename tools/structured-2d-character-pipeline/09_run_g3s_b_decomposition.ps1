param(
    [string]$RepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$PipelineWorkspace = 'Z:\AI\RogueliteCharacterPipeline'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "G3S-B: FAIL - $Message" -ForegroundColor Red
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
Write-Host 'Roguelite - G3S-B PERSISTENT 2D PART DECOMPOSITION' -ForegroundColor Cyan
Write-Host 'No image model. Rebuilds the pinned provisional 128x128 scaffold and decomposes it into persistent pixel parts.'
Write-Host 'The failed mouth is isolated in a replaceable head/face part. Broken chains are accessory slots, not body pixels.' -ForegroundColor Yellow
Write-Host ''

if (-not (Test-Path $RepoRoot -PathType Container)) { Fail "Repository root not found: $RepoRoot" }

$Python = 'Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\python_embeded\python.exe'
$Control = Join-Path $PipelineWorkspace 'g3s_a_control\g3s_a_control_official_raw.png'
$FailureMarker = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_a1_v2_failure.json'
$Helper = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_b_decompose_v1.py'
$Spec = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_b_parts_spec_v1.json'

foreach ($p in @($Python,$Control,$FailureMarker,$Helper,$Spec)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Required file missing: $p. Run git pull --ff-only first." }
}

$failure = Get-Content -LiteralPath $FailureMarker -Raw | ConvertFrom-Json
if ($failure.gate -ne 'G3S-A1-FACIAL-ANATOMY-LOCK-V2' -or $failure.status -ne 'FAIL') {
    Fail 'G3S-A1 V2 is not canonically closed FAIL; refusing to start G3S-B.'
}

$expectedControlSha = 'ce6d86e65b170e57a390e596a0f96d7e0c62d010bd5382835f83f2b3fc9fe08e'
$controlSha = (Get-FileHash -LiteralPath $Control -Algorithm SHA256).Hash.ToLowerInvariant()
if ($controlSha -ne $expectedControlSha) {
    Fail "Qwen control SHA mismatch: got=$controlSha expected=$expectedControlSha"
}
Write-Host "[OK] Pinned scaffold provenance SHA256 $controlSha" -ForegroundColor Green
Write-Host '[OK] G3S-A1 V2 failure acknowledged; head/face remains replaceable.' -ForegroundColor Green
Write-Host '[OK] Broken chains are separate initial accessory slots.' -ForegroundColor Green

$OutDir = Join-Path $PipelineWorkspace 'g3s_b_decomposition'
Remove-Item $OutDir -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Write-Host '[RUN] deterministic native 128 part extraction + pixel-exact recomposition audit...' -ForegroundColor Cyan
$code = Invoke-PythonSafe -Python $Python -Arguments @(
    $Helper,
    '--control',$Control,
    '--spec',$Spec,
    '--output-dir',$OutDir
)
if ($code -ne 0) { Fail "G3S-B helper exited with code $code" }

$Contact = Join-Path $OutDir 'g3s_b_contact_sheet.png'
$Atlas = Join-Path $OutDir 'g3s_b_parts_atlas.png'
$Manifest = Join-Path $OutDir 'g3s_b_runtime_manifest.json'
$Result = Join-Path $OutDir 'g3s_b_result.json'
foreach ($p in @($Contact,$Atlas,$Manifest,$Result)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Expected output missing: $p" }
}

Write-Host ''
Write-Host 'G3S-B: REVIEW REQUIRED' -ForegroundColor Yellow
Write-Host "CONTACT SHEET: $Contact"
Write-Host "PARTS ATLAS:   $Atlas"
Write-Host "MANIFEST:      $Manifest"
Write-Host "RESULT:        $Result"
Write-Host ''
Write-Host 'STOP. Review part boundaries, hair/cloth separation, hands/feet, pivots and chain sockets. Do not start G3S-C yet.' -ForegroundColor Yellow
