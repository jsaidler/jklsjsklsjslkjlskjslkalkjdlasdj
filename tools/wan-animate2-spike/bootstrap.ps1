param(
    [string]$Workspace = 'D:\AI\WanAnimate2',
    [string]$Master = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Require-Command([string]$Name, [string]$Hint) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "$Name was not found.`n$Hint"
    }
}

function Find-ComfyRoot([string]$Base) {
    $candidates = @(
        $Base,
        (Join-Path $Base 'ComfyUI')
    )
    foreach ($candidate in $candidates) {
        if ((Test-Path (Join-Path $candidate 'main.py')) -and
            (Test-Path (Join-Path $candidate '.git'))) {
            return $candidate
        }
    }
    return $null
}

function Find-WorkspacePython([string]$Base, [string]$ComfyRoot) {
    $candidates = @(
        (Join-Path $ComfyRoot '.venv\Scripts\python.exe'),
        (Join-Path $Base '.venv\Scripts\python.exe')
    ) | Select-Object -Unique
    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) { return $candidate }
    }
    return $null
}

Require-Command 'py.exe' 'Python launcher is required. Your existing Python 3.14 is sufficient for comfy-cli.'
Require-Command 'git.exe' 'Git for Windows is required.'

Write-Host 'Installing/updating pipx in the user Python...' -ForegroundColor Cyan
& py.exe -3.14 -m pip install --user --upgrade pipx
if ($LASTEXITCODE -ne 0) { throw 'pipx installation failed.' }

# Always invoke comfy-cli from a path without spaces. comfy-cli --fast-deps/uv can
# mis-handle an override.txt path when the caller cwd contains spaces (for example
# D:\GOOGLE DRIVE\...). We also deliberately avoid --fast-deps for this spike and
# use the normal pip dependency path: slower, but substantially less brittle.
$CliWorkDir = Split-Path -Parent $Workspace
if (-not $CliWorkDir) { throw "Could not resolve parent directory for workspace: $Workspace" }
New-Item -ItemType Directory -Force -Path $CliWorkDir | Out-Null

function Invoke-Comfy {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Args)
    Push-Location $CliWorkDir
    try {
        & py.exe -3.14 -m pipx run --spec comfy-cli comfy @Args
        if ($LASTEXITCODE -ne 0) { throw "comfy-cli failed: comfy $($Args -join ' ')" }
    } finally {
        Pop-Location
    }
}

$ComfyRoot = Find-ComfyRoot $Workspace

if (-not $ComfyRoot) {
    # comfy-cli refuses to install into an existing non-repository directory.
    # Remove only a completely empty placeholder; never delete unknown user data.
    if (Test-Path $Workspace) {
        $items = @(Get-ChildItem -Force -Path $Workspace -ErrorAction Stop)
        if ($items.Count -eq 0) {
            Write-Host "Removing empty placeholder directory: $Workspace" -ForegroundColor Yellow
            Remove-Item -Force $Workspace
        } else {
            $names = ($items | Select-Object -ExpandProperty Name) -join ', '
            throw @"
$Workspace exists but is not a ComfyUI git repository and is not empty.
Contents: $names

The bootstrap will not delete unknown files automatically.
Move/delete that directory yourself, or rerun with a different -Workspace path.
"@
        }
    }

    Write-Host "Installing ComfyUI for NVIDIA into $Workspace ..." -ForegroundColor Cyan
    Invoke-Comfy --skip-prompt --workspace $Workspace install --nvidia --skip-manager
    $ComfyRoot = Find-ComfyRoot $Workspace
    if (-not $ComfyRoot) {
        throw "comfy-cli returned success, but main.py/.git were not found at $Workspace or $(Join-Path $Workspace 'ComfyUI')."
    }
} else {
    # A previous install may have cloned ComfyUI and created .venv before dependency
    # installation failed. --restore is the supported comfy-cli path for completing
    # or repairing dependencies in an existing valid ComfyUI repository.
    Write-Host "ComfyUI repository found at $ComfyRoot" -ForegroundColor Green
    Write-Host 'Restoring/verifying ComfyUI dependencies with normal pip (no --fast-deps)...' -ForegroundColor Cyan
    Invoke-Comfy --skip-prompt --workspace $ComfyRoot install --restore --nvidia --skip-manager
}

Write-Host "Resolved ComfyUI root: $ComfyRoot" -ForegroundColor Green

$CustomNodes = Join-Path $ComfyRoot 'custom_nodes'
New-Item -ItemType Directory -Force -Path $CustomNodes | Out-Null

$GGUFDir = Join-Path $CustomNodes 'ComfyUI-GGUF'
if (-not (Test-Path (Join-Path $GGUFDir '.git'))) {
    & git.exe clone https://github.com/city96/ComfyUI-GGUF.git $GGUFDir
    if ($LASTEXITCODE -ne 0) { throw 'Failed to clone ComfyUI-GGUF.' }
} else {
    & git.exe -C $GGUFDir pull --ff-only
    if ($LASTEXITCODE -ne 0) { throw 'Failed to update ComfyUI-GGUF.' }
}

$RebelsDir = Join-Path $CustomNodes 'Rebels_w3a8_Loader'
if (-not (Test-Path (Join-Path $RebelsDir '.git'))) {
    & git.exe clone https://github.com/RealRebelAI/Rebels_w3a8_Loader.git $RebelsDir
    if ($LASTEXITCODE -ne 0) { throw 'Failed to clone Rebels_w3a8_Loader.' }
} else {
    & git.exe -C $RebelsDir pull --ff-only
    if ($LASTEXITCODE -ne 0) { throw 'Failed to update Rebels_w3a8_Loader.' }
}

$WorkspacePython = Find-WorkspacePython $Workspace $ComfyRoot
if (-not $WorkspacePython) {
    throw "ComfyUI workspace Python was not found under $ComfyRoot\.venv or $Workspace\.venv"
}
Write-Host "ComfyUI Python: $WorkspacePython" -ForegroundColor Green

Write-Host 'Installing GGUF custom-node dependencies...' -ForegroundColor Cyan
& $WorkspacePython -m pip install --upgrade -r (Join-Path $GGUFDir 'requirements.txt')
if ($LASTEXITCODE -ne 0) { throw 'ComfyUI-GGUF dependency installation failed.' }

$Models = Join-Path $ComfyRoot 'models'
$Diffusion = Join-Path $Models 'diffusion_models'
$TextEnc = Join-Path $Models 'text_encoders'
$ClipVision = Join-Path $Models 'clip_vision'
$Vae = Join-Path $Models 'vae'
$InputDir = Join-Path $ComfyRoot 'input'
foreach ($p in @($Diffusion, $TextEnc, $ClipVision, $Vae, $InputDir)) {
    New-Item -ItemType Directory -Force -Path $p | Out-Null
}

function Invoke-HF {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Args)
    Push-Location $CliWorkDir
    try {
        & py.exe -3.14 -m pipx run --spec huggingface_hub hf @Args
        if ($LASTEXITCODE -ne 0) { throw "Hugging Face download failed: hf $($Args -join ' ')" }
    } finally {
        Pop-Location
    }
}

$MainModel = Join-Path $Diffusion 'Wan-Animate-2-14B-Q4_K_M.gguf'
if (-not (Test-Path $MainModel)) {
    Write-Host 'Downloading Wan-Animate-2 Base Q4_K_M...' -ForegroundColor Cyan
    Invoke-HF download realrebelai/Wan-Animate-2-14B-GGUF Wan-Animate-2-14B-Q4_K_M.gguf --local-dir $Diffusion
}

$TextModel = Join-Path $TextEnc 'umt5_xxl_fp8_e4m3fn_scaled.safetensors'
if (-not (Test-Path $TextModel)) {
    Write-Host 'Downloading UMT5 XXL FP8...' -ForegroundColor Cyan
    Invoke-HF download Comfy-Org/Wan-Animate-2 text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors --local-dir $Models
}

$ClipModel = Join-Path $ClipVision 'clip_vision_h.safetensors'
if (-not (Test-Path $ClipModel)) {
    Write-Host 'Downloading CLIP Vision H...' -ForegroundColor Cyan
    Invoke-HF download Comfy-Org/Wan-Animate-2 clip_vision/clip_vision_h.safetensors --local-dir $Models
}

$VaeModel = Join-Path $Vae 'Wan2_1_VAE_bf16.safetensors'
if (-not (Test-Path $VaeModel)) {
    Write-Host 'Downloading Wan 2.1 VAE...' -ForegroundColor Cyan
    Invoke-HF download Comfy-Org/Wan-Animate-2 vae/Wan2_1_VAE_bf16.safetensors --local-dir $Models
}

if ($Master) {
    if (-not (Test-Path $Master)) { throw "Master image not found: $Master" }
    Copy-Item $Master (Join-Path $InputDir 'exilada_master.png') -Force
    Write-Host 'Copied canonical master to ComfyUI input.' -ForegroundColor Green
}

Write-Host ''
Write-Host 'CLI Wan-Animate-2 spike bootstrap complete.' -ForegroundColor Green
Write-Host "Workspace:  $Workspace"
Write-Host "ComfyUI:    $ComfyRoot"
Write-Host "Python:     $WorkspacePython"
Write-Host 'Next: run .\inspect.ps1, then prepare the 17-frame driver with .\make_driver.ps1.'
