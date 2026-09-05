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
$ModelUrl = "https://huggingface.co/evilsocket/alucard/resolve/$ModelRevision/alucard_model.safetensors?download=true"

function Fail([string]$Message) {
    Write-Host "G3S-A ALUCARD: FAIL - $Message" -ForegroundColor Red
    exit 1
}

Write-Host ''
Write-Host 'Roguelite - G3S-A ALUCARD NATIVE 128 RGBA' -ForegroundColor Cyan
Write-Host 'One static candidate only. This is a native 128x128 sprite model, not high-res diffusion + shrink.'
Write-Host 'Research-only until Alucard production licensing is explicitly accepted/resolved.' -ForegroundColor Yellow
Write-Host ''

if (-not (Test-Path $RepoRoot -PathType Container)) { Fail "Repository root not found: $RepoRoot" }

$FailureMarker = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_a_pixellock_failure.json'
$Helper = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_a_alucard_native.py'
$Control = Join-Path $PipelineWorkspace 'g3s_a_control\g3s_a_control_official_raw.png'
foreach ($p in @($FailureMarker,$Helper,$Control)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Required file missing: $p. Run git pull --ff-only first." }
}
$failure = Get-Content $FailureMarker -Raw | ConvertFrom-Json
if ($failure.gate -ne 'G3S-A-PIXELLOCK' -or $failure.status -ne 'FAIL') { Fail 'PixelLock source route is not canonically closed FAIL.' }

$Python = 'Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\python_embeded\python.exe'
if (-not (Test-Path $Python -PathType Leaf)) { Fail "Existing embedded Python not found: $Python" }

New-Item -ItemType Directory -Force -Path $DependencyRoot | Out-Null
$AlucardRoot = Join-Path $DependencyRoot 'alucard'
if (-not (Test-Path (Join-Path $AlucardRoot '.git') -PathType Container)) {
    Remove-Item $AlucardRoot -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host '[INSTALL] Cloning Alucard code...' -ForegroundColor Cyan
    & git.exe clone --no-checkout 'https://github.com/evilsocket/alucard.git' $AlucardRoot
    if ($LASTEXITCODE -ne 0) { Fail 'git clone Alucard failed.' }
}
& git.exe -C $AlucardRoot fetch --depth 1 origin $AlucardCommit
if ($LASTEXITCODE -ne 0) { Fail "Could not fetch pinned Alucard commit $AlucardCommit" }
& git.exe -C $AlucardRoot checkout --detach --force $AlucardCommit
if ($LASTEXITCODE -ne 0) { Fail "Could not checkout Alucard commit $AlucardCommit" }
$head = (& git.exe -C $AlucardRoot rev-parse HEAD).Trim()
if ($head -ne $AlucardCommit) { Fail "Alucard checkout mismatch: got=$head expected=$AlucardCommit" }
Write-Host "[OK] Alucard code pinned: $head" -ForegroundColor Green

$PyDeps = Join-Path $DependencyRoot 'pydeps'
New-Item -ItemType Directory -Force -Path $PyDeps | Out-Null
$oldPythonPath = $env:PYTHONPATH
$env:PYTHONPATH = "$PyDeps;$AlucardRoot"
$env:HF_HOME = Join-Path $DependencyRoot 'hf_home'
$env:TORCH_HOME = Join-Path $DependencyRoot 'torch_home'

function Test-AlucardImports {
    & $Python -c 'import torch, torchvision, PIL, numpy, safetensors, huggingface_hub, regex; import timm, ftfy, open_clip; print(torch.__version__); print(torch.cuda.is_available())' *> $null
    return ($LASTEXITCODE -eq 0)
}

if (-not (Test-AlucardImports)) {
    Write-Host '[INSTALL] Isolated Alucard Python extras (no Torch replacement)...' -ForegroundColor Cyan
    & $Python -m pip install --disable-pip-version-check --no-warn-script-location --target $PyDeps --no-deps `
        'open_clip_torch==3.2.0' 'timm==1.0.19' 'ftfy==6.3.1'
    if ($LASTEXITCODE -ne 0) { Fail 'Could not install isolated Alucard Python extras.' }
}
if (-not (Test-AlucardImports)) { Fail 'Alucard Python import preflight still fails after isolated dependency install.' }
Write-Host '[OK] Torch/OpenCLIP dependencies ready without replacing ComfyUI Torch.' -ForegroundColor Green

$ModelDir = Join-Path $DependencyRoot 'model'
$Model = Join-Path $ModelDir 'alucard_model.safetensors'
$Receipt = Join-Path $ModelDir 'alucard_model.receipt.json'
New-Item -ItemType Directory -Force -Path $ModelDir | Out-Null
if (-not (Test-Path $Model -PathType Leaf)) {
    $driveName = ([System.IO.Path]::GetPathRoot($DependencyRoot)).TrimEnd('\').TrimEnd(':')
    $drive = Get-PSDrive -Name $driveName -ErrorAction SilentlyContinue
    if ($null -ne $drive -and $drive.Free -lt 2GB) {
        Fail "At least 2 GB free is required for Alucard/CLIP provisioning on drive ${driveName}."
    }
    $part = "$Model.part"
    Write-Host '[DOWNLOAD] Alucard 32M native sprite weights (~128 MB)...' -ForegroundColor Cyan
    & curl.exe -L --fail --retry 4 --retry-delay 4 -C - -o $part $ModelUrl
    if ($LASTEXITCODE -ne 0) { Fail 'Alucard model download failed.' }
    Move-Item -LiteralPath $part -Destination $Model -Force
}
$modelSha = (Get-FileHash -LiteralPath $Model -Algorithm SHA256).Hash.ToLowerInvariant()
if (Test-Path $Receipt -PathType Leaf) {
    $r = Get-Content $Receipt -Raw | ConvertFrom-Json
    if ($r.revision -ne $ModelRevision) { Fail "Alucard model receipt revision mismatch: $($r.revision)" }
    if ($r.sha256 -ne $modelSha) { Fail "Alucard model changed since first verified download: got=$modelSha expected=$($r.sha256)" }
} else {
    [pscustomobject]@{
        source = $ModelUrl
        revision = $ModelRevision
        sha256 = $modelSha
        bytes = (Get-Item -LiteralPath $Model).Length
    } | ConvertTo-Json | Set-Content -LiteralPath $Receipt -Encoding UTF8
}
Write-Host "[OK] Alucard model revision=$ModelRevision SHA256=$modelSha" -ForegroundColor Green

$OutDir = Join-Path $PipelineWorkspace 'g3s_a_alucard'
Remove-Item $OutDir -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

try {
    Write-Host '[RUN] one reference-conditioned native 128x128 RGBA Alucard candidate...' -ForegroundColor Cyan
    Write-Host '[INFO] First run may also fetch the OpenAI CLIP ViT-B/32 text encoder into the isolated TORCH_HOME.' -ForegroundColor DarkGray
    & $Python $Helper `
        --alucard-root $AlucardRoot `
        --model $Model `
        --control $Control `
        --output-dir $OutDir `
        --seed $Seed `
        --code-commit $AlucardCommit `
        --model-revision $ModelRevision
    $code = $LASTEXITCODE
    if ($code -ne 0) { Fail "Alucard helper exited with code $code" }
}
finally {
    $env:PYTHONPATH = $oldPythonPath
}

$Contact = Join-Path $OutDir 'g3s_a_alucard_contact_sheet.png'
$Raw = Join-Path $OutDir 'g3s_a_alucard_raw128.png'
$Result = Join-Path $OutDir 'g3s_a_alucard_result.json'
foreach ($p in @($Contact,$Raw,$Result)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Expected output missing: $p" }
}

Write-Host ''
Write-Host 'G3S-A ALUCARD: REVIEW REQUIRED' -ForegroundColor Yellow
Write-Host "CONTACT SHEET: $Contact"
Write-Host "RAW:           $Raw"
Write-Host "RESULT:        $Result"
Write-Host ''
Write-Host 'STOP. Review topology first, then Exilada identity and actual native pixel language. Do not start G3S-B.' -ForegroundColor Yellow
