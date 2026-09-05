param(
    [string]$RepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$PipelineWorkspace = 'Z:\AI\RogueliteCharacterPipeline'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "G3S-A AUTHORED: FAIL - $Message" -ForegroundColor Red
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
Write-Host 'Roguelite - G3S-A AUTHORED NATIVE SOURCE V1' -ForegroundColor Cyan
Write-Host 'Model search is closed. This runner performs explicit deterministic edits on a native 128x128 scaffold.'
Write-Host 'The Qwen control is provenance/design scaffolding only; it never owns animation frames.' -ForegroundColor Yellow
Write-Host ''

if (-not (Test-Path $RepoRoot -PathType Container)) { Fail "Repository root not found: $RepoRoot" }

$Python = 'Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\python_embeded\python.exe'
$Control = Join-Path $PipelineWorkspace 'g3s_a_control\g3s_a_control_official_raw.png'
$FailureMarker = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_a_alucard_failure.json'
$Helper = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_a_authored_native_v1.py'
$Patch = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_a_authored_patch_v1.json'

foreach ($p in @($Python,$Control,$FailureMarker,$Helper,$Patch)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Required file missing: $p. Run git pull --ff-only first." }
}

$failure = Get-Content -LiteralPath $FailureMarker -Raw | ConvertFrom-Json
if ($failure.gate -ne 'G3S-A-ALUCARD' -or $failure.status -ne 'FAIL') {
    Fail 'Alucard is not canonically closed FAIL; refusing to start authored-source gate.'
}

$expectedControlSha = 'ce6d86e65b170e57a390e596a0f96d7e0c62d010bd5382835f83f2b3fc9fe08e'
$controlSha = (Get-FileHash -LiteralPath $Control -Algorithm SHA256).Hash.ToLowerInvariant()
if ($controlSha -ne $expectedControlSha) {
    Fail "Qwen control SHA mismatch: got=$controlSha expected=$expectedControlSha"
}
Write-Host "[OK] Qwen design control pinned SHA256 $controlSha" -ForegroundColor Green

$OutDir = Join-Path $PipelineWorkspace 'g3s_a_authored'
Remove-Item $OutDir -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Write-Host '[RUN] native 128 scaffold + explicit authored mouth/restraint/chain patch...' -ForegroundColor Cyan
$code = Invoke-PythonSafe -Python $Python -Arguments @(
    $Helper,
    '--control',$Control,
    '--patch',$Patch,
    '--output-dir',$OutDir
)
if ($code -ne 0) { Fail "authored native helper exited with code $code" }

$Contact = Join-Path $OutDir 'g3s_a_authored_contact_sheet.png'
$Candidate = Join-Path $OutDir 'g3s_a_authored_candidate_v1.png'
$Result = Join-Path $OutDir 'g3s_a_authored_result.json'
foreach ($p in @($Contact,$Candidate,$Result)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Expected output missing: $p" }
}

Write-Host ''
Write-Host 'G3S-A AUTHORED: REVIEW REQUIRED' -ForegroundColor Yellow
Write-Host "CONTACT SHEET: $Contact"
Write-Host "CANDIDATE:     $Candidate"
Write-Host "RESULT:        $Result"
Write-Host ''
Write-Host 'STOP. Review at 1x. If changes are needed, the next revision edits explicit native pixel patch data; do not search another model.' -ForegroundColor Yellow
