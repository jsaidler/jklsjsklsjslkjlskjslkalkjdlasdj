param(
    [string]$Workspace = 'D:\AI\WanAnimate2',
    [string]$Master = '',
    [switch]$UseOfficialBaseInt8
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Require-Command([string]$Name, [string]$Hint) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "$Name was not found.`n$Hint"
    }
}

function Find-ComfyRoot([string]$Base) {
    $candidates = @($Base, (Join-Path $Base 'ComfyUI'))
    foreach ($candidate in $candidates) {
        if ((Test-Path (Join-Path $candidate 'main.py')) -and (Test-Path (Join-Path $candidate '.git'))) {
            return $candidate
        }
    }
    return $null
}

function Find-WorkspacePython([string]$Base, [string]$ComfyRoot) {
    $candidates = @((Join-Path $ComfyRoot '.venv\Scripts\python.exe'), (Join-Path $Base '.venv\Scripts\python.exe')) | Select-Object -Unique
    foreach ($candidate in $candidates) { if (Test-Path $candidate) { return $candidate } }
    return $null
}

Require-Command 'py.exe' 'Python launcher is required. Your existing Python 3.14 is sufficient for comfy-cli.'
Require-Command 'git.exe' 'Git for Windows is required.'

Write-Host 'Installing/updating pipx in the user Python...' -ForegroundColor Cyan
& py.exe -3.14 -m pip install --user --upgrade pipx
if ($LASTEXITCODE -ne 0) { throw 'pipx installation failed.' }

function Invoke-Comfy {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Args)
    Push-Location 'D:\AI'
    try {
        & py.exe -3.14 -m pipx run --spec comfy-cli comfy @Args
        if ($LASTEXITCODE -ne 0) { throw "comfy-cli failed: comfy $($Args -join ' ')" }
    } finally { Pop-Location }
}

$ComfyRoot = Find-ComfyRoot $Workspace
if (-not $ComfyRoot) {
    if (Test-Path $Workspace) {
        $items = @(Get-ChildItem -Force -Path $Workspace -ErrorAction Stop)
        if ($items.Count -eq 0) { Remove-Item -Force $Workspace }
        else { throw "$Workspace exists, is not a ComfyUI git repository, and is not empty." }
    }
    Write-Host "Installing ComfyUI for NVIDIA into $Workspace ..." -ForegroundColor Cyan
    Invoke-Comfy --skip-prompt --workspace $Workspace install --nvidia --skip-manager
    $ComfyRoot = Find-ComfyRoot $Workspace
    if (-not $ComfyRoot) { throw 'comfy-cli returned success, but ComfyUI root could not be resolved.' }
} else {
    Write-Host "ComfyUI repository found at $ComfyRoot" -ForegroundColor Green
    Write-Host 'Restoring/verifying ComfyUI dependencies with normal pip (no --fast-deps)...' -ForegroundColor Cyan
    Invoke-Comfy --skip-prompt --workspace $Workspace install --restore --nvidia --skip-manager
}

Write-Host "Resolved ComfyUI root: $ComfyRoot" -ForegroundColor Green
$WorkspacePython = Find-WorkspacePython $Workspace $ComfyRoot
if (-not $WorkspacePython) { throw 'ComfyUI workspace Python was not found.' }
Write-Host "ComfyUI Python: $WorkspacePython" -ForegroundColor Green

# This validation route uses the official Base INT8 ConvRot checkpoint. It uses
# native ComfyUI Wan-Animate-2 support and therefore DOES NOT need ComfyUI-GGUF
# or Rebels_w3a8_Loader. Do not add irrelevant custom-node failure modes here.
if (-not $UseOfficialBaseInt8) {
    throw @"
The originally planned public BASE GGUF Q4_K_M is no longer available at the validated repository.
No silent Distilled/TURBO substitution will be made.
Rerun with -UseOfficialBaseInt8 to use the official Comfy-Org Base INT8 ConvRot checkpoint.
"@
}

$Models = Join-Path $ComfyRoot 'models'
$Diffusion = Join-Path $Models 'diffusion_models'
$TextEnc = Join-Path $Models 'text_encoders'
$ClipVision = Join-Path $Models 'clip_vision'
$Vae = Join-Path $Models 'vae'
$InputDir = Join-Path $ComfyRoot 'input'
foreach ($p in @($Diffusion, $TextEnc, $ClipVision, $Vae, $InputDir)) { New-Item -ItemType Directory -Force -Path $p | Out-Null }

function Invoke-HF {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Args)
    & py.exe -3.14 -m pipx run --spec huggingface_hub hf @Args
    if ($LASTEXITCODE -ne 0) { throw "Hugging Face download failed: hf $($Args -join ' ')" }
}

$MainModel = Join-Path $Diffusion 'wan_animate_2_int8_convrot.safetensors'
if (-not (Test-Path $MainModel)) {
    Write-Host 'Downloading OFFICIAL Wan-Animate-2 BASE INT8 ConvRot...' -ForegroundColor Cyan
    Invoke-HF download Comfy-Org/Wan-Animate-2 diffusion_models/wan_animate_2_int8_convrot.safetensors --local-dir $Models
}
$TextModel = Join-Path $TextEnc 'umt5_xxl_fp8_e4m3fn_scaled.safetensors'
if (-not (Test-Path $TextModel)) { Invoke-HF download Comfy-Org/Wan-Animate-2 text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors --local-dir $Models }
$ClipModel = Join-Path $ClipVision 'clip_vision_h.safetensors'
if (-not (Test-Path $ClipModel)) { Invoke-HF download Comfy-Org/Wan-Animate-2 clip_vision/clip_vision_h.safetensors --local-dir $Models }
$VaeModel = Join-Path $Vae 'Wan2_1_VAE_bf16.safetensors'
if (-not (Test-Path $VaeModel)) { Invoke-HF download Comfy-Org/Wan-Animate-2 vae/Wan2_1_VAE_bf16.safetensors --local-dir $Models }

if ($Master) {
    if (-not (Test-Path $Master)) { throw "Master image not found: $Master" }
    Copy-Item $Master (Join-Path $InputDir 'exilada_master.png') -Force
    Write-Host 'Copied canonical master to ComfyUI input.' -ForegroundColor Green
}

$RouteFile = Join-Path $Workspace 'spike_model_route.txt'
@"
route=official_base_int8_convrot
model=wan_animate_2_int8_convrot.safetensors
source=Comfy-Org/Wan-Animate-2
precision=int8_convrot
base_or_distilled=base
"@ | Set-Content -Path $RouteFile -Encoding utf8

Write-Host ''
Write-Host 'CLI Wan-Animate-2 spike bootstrap complete.' -ForegroundColor Green
Write-Host "Workspace:  $Workspace"
Write-Host "ComfyUI:    $ComfyRoot"
Write-Host "Python:     $WorkspacePython"
Write-Host 'Model route: official BASE INT8 ConvRot (not Distilled).'
