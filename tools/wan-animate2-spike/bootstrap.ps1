param(
    [string]$Workspace = 'Z:\AI\WanAnimate2',
    [string]$Master = 'D:\GOOGLE DRIVE\DEV\Roguelite\assets\source\characters\exilada\reference\exilada_master.png',
    [int]$MinFreeGB = 70
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Require-Command([string]$Name, [string]$Hint) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) { throw "$Name was not found.`n$Hint" }
}

function Find-ComfyRoot([string]$Base) {
    foreach ($candidate in @($Base, (Join-Path $Base 'ComfyUI'))) {
        if ((Test-Path (Join-Path $candidate 'main.py')) -and (Test-Path (Join-Path $candidate '.git'))) { return $candidate }
    }
    return $null
}

function Find-WorkspacePython([string]$Base, [string]$ComfyRoot) {
    foreach ($candidate in @((Join-Path $ComfyRoot '.venv\Scripts\python.exe'), (Join-Path $Base '.venv\Scripts\python.exe')) | Select-Object -Unique) {
        if (Test-Path $candidate) { return $candidate }
    }
    return $null
}

function Invoke-Comfy {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Args)
    $workingRoot = Split-Path -Parent $Workspace
    if (-not $workingRoot) { throw "Cannot resolve workspace parent from: $Workspace" }
    if (-not (Test-Path $workingRoot -PathType Container)) {
        New-Item -ItemType Directory -Force -Path $workingRoot | Out-Null
    }
    Push-Location $workingRoot
    try {
        & py.exe -3.14 -m pipx run --spec comfy-cli comfy @Args
        if ($LASTEXITCODE -ne 0) { throw "comfy-cli failed: comfy $($Args -join ' ')" }
    } finally { Pop-Location }
}

function Invoke-HF {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Args)
    & py.exe -3.14 -m pipx run --spec 'huggingface_hub[hf_xet]' hf @Args
    if ($LASTEXITCODE -ne 0) { throw "Hugging Face download failed: hf $($Args -join ' ')" }
}

function Remove-Obsolete([string]$Path) {
    if (Test-Path $Path -PathType Leaf) {
        $size = [math]::Round((Get-Item $Path).Length / 1GB, 3)
        Write-Host "[CLEAN] Removing obsolete Wan asset: $Path ($size GB)" -ForegroundColor DarkYellow
        Remove-Item -LiteralPath $Path -Force
    }
}

Require-Command 'py.exe' 'Python launcher is required.'
Require-Command 'git.exe' 'Git for Windows is required.'

$qualifier = Split-Path -Qualifier $Workspace
if (-not $qualifier) { throw "Workspace must be on an absolute Windows drive path: $Workspace" }
$driveName = $qualifier.TrimEnd(':')
$drive = Get-PSDrive -Name $driveName -ErrorAction Stop
$freeGB = [math]::Round($drive.Free / 1GB, 1)

Write-Host ''
Write-Host 'Wan-Animate-2 Base BF16 reference-route bootstrap' -ForegroundColor Cyan
Write-Host "Workspace: $Workspace"
Write-Host "Free on $qualifier $freeGB GB"
Write-Host ''
Write-Host 'Canonical download set (no Distilled, no INT8, no LoRA):' -ForegroundColor Green
Write-Host '  wan_animate_2_bf16.safetensors             ~32.8 GB'
Write-Host '  umt5_xxl_fp16.safetensors                  ~11.4 GB'
Write-Host '  clip_vision_h.safetensors                   ~1.26 GB'
Write-Host '  Wan2_1_VAE_bf16.safetensors                ~0.254 GB'
Write-Host '  Total model payload                         ~45.7 GB'
Write-Host "  Required free-space floor for install/temp  ${MinFreeGB} GB"
Write-Host ''

if ($freeGB -lt $MinFreeGB) { throw "Insufficient free space on $qualifier. Need at least $MinFreeGB GB before rebuilding the BF16 reference route." }

Write-Host 'Installing/updating pipx in the user Python...' -ForegroundColor Cyan
& py.exe -3.14 -m pip install --user --upgrade pipx
if ($LASTEXITCODE -ne 0) { throw 'pipx installation failed.' }

$ComfyRoot = Find-ComfyRoot $Workspace
if (-not $ComfyRoot) {
    if (Test-Path $Workspace) {
        $items = @(Get-ChildItem -Force -Path $Workspace -ErrorAction Stop)
        if ($items.Count -eq 0) { Remove-Item -Force $Workspace }
        else { throw "$Workspace exists, is not a ComfyUI git repository, and is not empty. Refusing to overwrite unknown material." }
    }
    Write-Host "Installing isolated ComfyUI for NVIDIA into $Workspace ..." -ForegroundColor Cyan
    Invoke-Comfy --skip-prompt --workspace $Workspace install --nvidia --skip-manager
    $ComfyRoot = Find-ComfyRoot $Workspace
    if (-not $ComfyRoot) { throw 'comfy-cli returned success, but ComfyUI root could not be resolved.' }
} else {
    Write-Host "ComfyUI repository found at $ComfyRoot" -ForegroundColor Green
    Write-Host 'Restoring/updating dependencies...' -ForegroundColor Cyan
    Invoke-Comfy --skip-prompt --workspace $Workspace install --restore --nvidia --skip-manager
}

$WorkspacePython = Find-WorkspacePython $Workspace $ComfyRoot
if (-not $WorkspacePython) { throw 'ComfyUI workspace Python was not found.' }
Write-Host "Resolved ComfyUI root: $ComfyRoot" -ForegroundColor Green
Write-Host "ComfyUI Python: $WorkspacePython" -ForegroundColor Green

$Models = Join-Path $ComfyRoot 'models'
$Diffusion = Join-Path $Models 'diffusion_models'
$TextEnc = Join-Path $Models 'text_encoders'
$ClipVision = Join-Path $Models 'clip_vision'
$Vae = Join-Path $Models 'vae'
$Lora = Join-Path $Models 'loras'
$InputDir = Join-Path $ComfyRoot 'input'
foreach ($p in @($Diffusion,$TextEnc,$ClipVision,$Vae,$Lora,$InputDir)) { New-Item -ItemType Directory -Force -Path $p | Out-Null }

$Obsolete = @(
    (Join-Path $Diffusion 'wan_animate_2_int8_convrot.safetensors'),
    (Join-Path $Diffusion 'wan_animate_2_distill_bf16.safetensors'),
    (Join-Path $Diffusion 'wan_animate_2_distill_int8_convrot.safetensors'),
    (Join-Path $Lora 'lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors'),
    (Join-Path $TextEnc 'umt5_xxl_fp8_e4m3fn_scaled.safetensors')
)
foreach ($f in $Obsolete) { Remove-Obsolete $f }

$env:HF_HOME = Join-Path $Workspace '.hf_cache'
New-Item -ItemType Directory -Force -Path $env:HF_HOME | Out-Null

$MainModel = Join-Path $Diffusion 'wan_animate_2_bf16.safetensors'
$TextModel = Join-Path $TextEnc 'umt5_xxl_fp16.safetensors'
$ClipModel = Join-Path $ClipVision 'clip_vision_h.safetensors'
$VaeModel = Join-Path $Vae 'Wan2_1_VAE_bf16.safetensors'

if (-not (Test-Path $MainModel -PathType Leaf)) { Write-Host 'Downloading Wan-Animate-2 BASE BF16 (32.8 GB)...' -ForegroundColor Cyan; Invoke-HF download Comfy-Org/Wan-Animate-2 diffusion_models/wan_animate_2_bf16.safetensors --local-dir $Models }
if (-not (Test-Path $TextModel -PathType Leaf)) { Write-Host 'Downloading UMT5 XXL FP16 (11.4 GB)...' -ForegroundColor Cyan; Invoke-HF download Comfy-Org/Wan-Animate-2 text_encoders/umt5_xxl_fp16.safetensors --local-dir $Models }
if (-not (Test-Path $ClipModel -PathType Leaf)) { Write-Host 'Downloading CLIP Vision H (1.26 GB)...' -ForegroundColor Cyan; Invoke-HF download Comfy-Org/Wan-Animate-2 clip_vision/clip_vision_h.safetensors --local-dir $Models }
if (-not (Test-Path $VaeModel -PathType Leaf)) { Write-Host 'Downloading Wan VAE BF16 (0.254 GB)...' -ForegroundColor Cyan; Invoke-HF download Comfy-Org/Wan-Animate-2 vae/Wan2_1_VAE_bf16.safetensors --local-dir $Models }

foreach ($f in @($MainModel,$TextModel,$ClipModel,$VaeModel)) { if (-not (Test-Path $f -PathType Leaf)) { throw "Required BF16 route asset missing after download: $f" } }

$W0Dir = Join-Path $InputDir 'wan_animate2_w0'
New-Item -ItemType Directory -Force -Path $W0Dir | Out-Null
$W0Reference = Join-Path $W0Dir 'official_demo1_reference.png'
$W0Driver = Join-Path $W0Dir 'official_demo1_template.mp4'
if (-not (Test-Path $W0Reference -PathType Leaf)) { Invoke-WebRequest -UseBasicParsing -Uri 'https://raw.githubusercontent.com/Wan-Video/Wan-Animate-2/main/examples/demo1/reference.png' -OutFile $W0Reference }
if (-not (Test-Path $W0Driver -PathType Leaf)) { Invoke-WebRequest -UseBasicParsing -Uri 'https://raw.githubusercontent.com/Wan-Video/Wan-Animate-2/main/examples/demo1/template.mp4' -OutFile $W0Driver }

if ($Master -and (Test-Path $Master -PathType Leaf)) { Copy-Item -LiteralPath $Master -Destination (Join-Path $InputDir 'exilada_master.png') -Force }
elseif ($Master) { Write-Host "[WARN] Exilada master not copied because path is absent: $Master" -ForegroundColor Yellow }

foreach ($oldInput in @((Join-Path $InputDir 'exilada_driver_17f.mp4'),(Join-Path $InputDir 'exilada_complete_motion_driver_17f.mp4'))) {
    if (Test-Path $oldInput -PathType Leaf) { Write-Host "[CLEAN] Removing obsolete old-spike input: $oldInput" -ForegroundColor DarkYellow; Remove-Item -LiteralPath $oldInput -Force }
}

$manifest = [ordered]@{
    gate = 'WAN_ANIMATE2_W0_BF16_REFERENCE_PREP'; status = 'ASSETS_READY_FOR_SCHEMA_PREFLIGHT'; route = 'base_bf16_reference'; workspace = $Workspace; comfy_root = $ComfyRoot
    model = $MainModel; text_encoder = $TextModel; clip_vision = $ClipModel; vae = $VaeModel; lora = $null; distilled = $false; quantized_main_model = $false
    official_w0_reference = $W0Reference; official_w0_driver = $W0Driver
    upstream_repo_semantics = [ordered]@{ width=640; height=800; frame_num=37; fps=16; sample_steps_repo_yaml=20; base_seed=0 }
    downloaded_bytes = [ordered]@{ model=(Get-Item $MainModel).Length; text_encoder=(Get-Item $TextModel).Length; clip_vision=(Get-Item $ClipModel).Length; vae=(Get-Item $VaeModel).Length }
    intentionally_absent = @('wan_animate_2_int8_convrot.safetensors','wan_animate_2_distill_bf16.safetensors','wan_animate_2_distill_int8_convrot.safetensors','lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors','umt5_xxl_fp8_e4m3fn_scaled.safetensors')
}
$ManifestPath = Join-Path $Workspace 'wan_bf16_route.json'
$manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ManifestPath -Encoding UTF8

if (Test-Path $env:HF_HOME) { Write-Host "[CLEAN] Removing completed Hugging Face download cache: $env:HF_HOME" -ForegroundColor DarkYellow; Remove-Item -LiteralPath $env:HF_HOME -Recurse -Force }

Write-Host ''
Write-Host 'WAN BF16 PREP: ASSETS READY FOR SCHEMA PREFLIGHT' -ForegroundColor Green
Write-Host "Manifest: $ManifestPath" -ForegroundColor Green
Write-Host "W0 reference: $W0Reference"
Write-Host "W0 driver:    $W0Driver"
Write-Host ''
Write-Host 'Next step: run inspect.ps1. Do not run inference until the installed WanAnimate2ToVideo schema is captured for this fresh ComfyUI build.' -ForegroundColor Yellow
