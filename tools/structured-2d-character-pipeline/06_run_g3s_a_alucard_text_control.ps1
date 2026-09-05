param(
    [string]$RepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$PipelineWorkspace = 'Z:\AI\RogueliteCharacterPipeline',
    [string]$DependencyRoot = 'Z:\AI\AlucardSpike',
    [long]$Seed = 20260905
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$AlucardCommit = '02d1c60a16142015f7838a6a033da5e6ac9ce4f7'
$ModelRevision = 'b8e7602'

function Fail([string]$Message) {
    Write-Host "G3S-A ALUCARD TEXT CONTROL: FAIL - $Message" -ForegroundColor Red
    exit 1
}

function Invoke-PythonSafe {
    param([Parameter(Mandatory=$true)][string[]]$Arguments)
    $saved = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $captured = @(& $Python @Arguments 2>&1)
        $code = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $saved
    }
    foreach ($line in $captured) { Write-Host ([string]$line) }
    return [int]$code
}

Write-Host ''
Write-Host 'Roguelite - G3S-A ALUCARD TEXT-ONLY UPSTREAM CONTROL' -ForegroundColor Cyan
Write-Host 'No external reference is passed into Alucard. This validates the documented text-to-sprite mode only.' -ForegroundColor Yellow
Write-Host ''

$Python = 'Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\python_embeded\python.exe'
$AlucardRoot = Join-Path $DependencyRoot 'alucard'
$PyDeps = Join-Path $DependencyRoot 'pydeps'
$Model = Join-Path $DependencyRoot 'model\alucard_model.safetensors'
$Control = Join-Path $PipelineWorkspace 'g3s_a_control\g3s_a_control_official_raw.png'
$Helper = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_a_alucard_text_control.py'
foreach ($p in @($Python,$Model,$Control,$Helper)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Required file missing: $p" }
}
foreach ($p in @($AlucardRoot,$PyDeps)) {
    if (-not (Test-Path $p -PathType Container)) { Fail "Required directory missing: $p" }
}
$head = (& git.exe -C $AlucardRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $head -ne $AlucardCommit) { Fail "Alucard code is not at pinned commit $AlucardCommit (got $head)" }

$Probe = "import sys; sys.path.insert(0, r'$PyDeps'); sys.path.insert(0, r'$AlucardRoot'); import torch, torchvision, PIL, numpy, safetensors, huggingface_hub, regex, yaml, tqdm, wcwidth, timm, ftfy, open_clip; print('G3S_A_ALUCARD_TEXT_CONTROL_IMPORTS=PASS'); print(torch.cuda.is_available())"
$probeCode = Invoke-PythonSafe -Arguments @('-c',$Probe)
if ($probeCode -ne 0) { Fail "dependency probe failed (exit $probeCode); rerun 05 once after git pull if dependencies were removed." }

$OutDir = Join-Path $PipelineWorkspace 'g3s_a_alucard_text_control'
Remove-Item $OutDir -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$env:HF_HOME = Join-Path $DependencyRoot 'hf_home'
$env:TORCH_HOME = Join-Path $DependencyRoot 'torch_home'

Write-Host '[RUN] one Alucard native 128x128 TEXT-ONLY candidate using upstream-supported mode...' -ForegroundColor Cyan
$code = Invoke-PythonSafe -Arguments @(
    $Helper,
    '--alucard-root',$AlucardRoot,
    '--pydeps',$PyDeps,
    '--model',$Model,
    '--control',$Control,
    '--output-dir',$OutDir,
    '--seed',[string]$Seed,
    '--code-commit',$AlucardCommit,
    '--model-revision',$ModelRevision
)
if ($code -ne 0) { Fail "text-only helper exited with code $code" }

$Contact = Join-Path $OutDir 'g3s_a_alucard_text_contact_sheet.png'
$Raw = Join-Path $OutDir 'g3s_a_alucard_text_raw128.png'
$Result = Join-Path $OutDir 'g3s_a_alucard_text_result.json'
foreach ($p in @($Contact,$Raw,$Result)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Expected output missing: $p" }
}

Write-Host ''
Write-Host 'G3S-A ALUCARD TEXT CONTROL: REVIEW REQUIRED' -ForegroundColor Yellow
Write-Host "CONTACT SHEET: $Contact"
Write-Host "RAW:           $Raw"
Write-Host "RESULT:        $Result"
Write-Host ''
Write-Host 'STOP. This control decides whether Alucard itself is healthy in text-to-sprite mode. Do not rerun the invalid arbitrary-reference test.' -ForegroundColor Yellow
