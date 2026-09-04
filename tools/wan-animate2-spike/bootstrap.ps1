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

Require-Command 'py.exe' 'Python launcher is required. Your existing Python 3.14 is sufficient.'
Require-Command 'git.exe' 'Git for Windows is required.'

Write-Host 'Installing/updating pipx in the user Python...' -ForegroundColor Cyan
& py.exe -3.14 -m pip install --user --upgrade pipx
if ($LASTEXITCODE -ne 0) { throw 'pipx installation failed.' }

function Invoke-Comfy {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Args)
    & py.exe -3.14 -m pipx run --spec comfy-cli comfy @Args
    if ($LASTEXITCODE -ne 0) { throw "comfy-cli failed: comfy $($Args -join ' ')" }
}

$ComfyRoot = Join-Path $Workspace 'ComfyUI'
$CustomNodes = Join-Path $ComfyRoot 'custom_nodes'

New-Item -ItemType Directory -Force -Path $Workspace | Out-Null

if (-not (Test-Path (Join-Path $ComfyRoot 'main.py'))) {
    Write-Host "Installing ComfyUI into $Workspace ..." -ForegroundColor Cyan
    Invoke-Comfy --workspace $Workspace install --fast-deps
} else {
    Write-Host "ComfyUI already exists at $ComfyRoot" -ForegroundColor Green
}

$GGUFDir = Join-Path $CustomNodes 'ComfyUI-GGUF'
if (-not (Test-Path $GGUFDir)) {
    & git.exe clone https://github.com/city96/ComfyUI-GGUF.git $GGUFDir
    if ($LASTEXITCODE -ne 0) { throw 'Failed to clone ComfyUI-GGUF.' }
} else {
    & git.exe -C $GGUFDir pull --ff-only
    if ($LASTEXITCODE -ne 0) { throw 'Failed to update ComfyUI-GGUF.' }
}

$RebelsDir = Join-Path $CustomNodes 'Rebels_w3a8_Loader'
if (-not (Test-Path $RebelsDir)) {
    & git.exe clone https://github.com/RealRebelAI/Rebels_w3a8_Loader.git $RebelsDir
    if ($LASTEXITCODE -ne 0) { throw 'Failed to clone Rebels_w3a8_Loader.' }
} else {
    & git.exe -C $RebelsDir pull --ff-only
    if ($LASTEXITCODE -ne 0) { throw 'Failed to update Rebels_w3a8_Loader.' }
}

$WorkspacePython = Join-Path $Workspace '.venv\Scripts\python.exe'
if (-not (Test-Path $WorkspacePython)) {
    throw "ComfyUI workspace Python was not found at $WorkspacePython"
}

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
    & py.exe -3.14 -m pipx run --spec huggingface_hub hf @Args
    if ($LASTEXITCODE -ne 0) { throw "Hugging Face download failed: hf $($Args -join ' ')" }
}

$MainModel = Join-Path $Diffusion 'Wan-Animate-2-14B-Q4_K_M.gguf'
if (-not (Test-Path $MainModel)) {
    Write-Host 'Downloading Wan-Animate-2 Base Q4_K_M...' -ForegroundColor Cyan
    Invoke-HF download realrebelai/Wan-Animate-2-14B-GGUF Wan-Animate-2-14B-Q4_K_M.gguf --local-dir $Diffusion
}

$TextModel = Join-Path $TextEnc 'umt5_xxl_fp8_e4m3fn_scaled.safetensors'
if (-not (Test-Path $TextModel)) {
    Invoke-HF download Comfy-Org/Wan-Animate-2 text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors --local-dir $Models
}

$ClipModel = Join-Path $ClipVision 'clip_vision_h.safetensors'
if (-not (Test-Path $ClipModel)) {
    Invoke-HF download Comfy-Org/Wan-Animate-2 clip_vision/clip_vision_h.safetensors --local-dir $Models
}

$VaeModel = Join-Path $Vae 'Wan2_1_VAE_bf16.safetensors'
if (-not (Test-Path $VaeModel)) {
    Invoke-HF download Comfy-Org/Wan-Animate-2 vae/Wan2_1_VAE_bf16.safetensors --local-dir $Models
}

if ($Master) {
    if (-not (Test-Path $Master)) { throw "Master image not found: $Master" }
    Copy-Item $Master (Join-Path $InputDir 'exilada_master.png') -Force
    Write-Host 'Copied canonical master to ComfyUI input.' -ForegroundColor Green
}

Write-Host ''
Write-Host 'CLI Wan-Animate-2 spike bootstrap complete.' -ForegroundColor Green
Write-Host "Workspace: $Workspace"
Write-Host 'Next: run .\inspect.ps1, then prepare the 17-frame driver with .\make_driver.ps1.'
