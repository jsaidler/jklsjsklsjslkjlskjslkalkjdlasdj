param(
    [string]$Workspace = 'D:\AI\Flux2RefControlSpike'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$PortableRoot = Join-Path $Workspace 'ComfyUI_windows_portable'
$ComfyRoot = Join-Path $PortableRoot 'ComfyUI'
$ComfyMain = Join-Path $ComfyRoot 'main.py'
$LoraMapFile = Join-Path $ComfyRoot 'comfy\lora.py'

if (-not (Test-Path $ComfyMain)) {
    throw "ComfyUI portable not found: $ComfyMain"
}
if (-not (Test-Path $LoraMapFile)) {
    throw "ComfyUI LoRA mapper not found: $LoraMapFile"
}

Write-Host ''
Write-Host 'FLUX.2 Klein + RefControl Pose spike - STEP 3: minimum model weights' -ForegroundColor Cyan
Write-Host 'This step downloads ONLY the four files needed for the key-pose spike.'
Write-Host 'No Pixel Art LoRA, ControlNet, OpenPose model, video model, or interpolation model will be downloaded.'
Write-Host ''

# Pre-download compatibility gate: current ComfyUI must expose generic diffusion_model.* LoRA key mapping.
$loraSource = Get-Content -Raw -Path $LoraMapFile
$hasGenericDiffusionMap = ($loraSource -match 'k\.startswith\("diffusion_model\."\)') -and
                          ($loraSource -match 'generic lora format without any weird key names')
if (-not $hasGenericDiffusionMap) {
    throw 'Current ComfyUI build does not expose the generic diffusion_model.* LoRA key mapping expected by RefControl. No model download was started.'
}
Write-Host '[OK] ComfyUI LoRA compatibility gate: generic diffusion_model.* mapping present.' -ForegroundColor Green

$driveName = ([System.IO.Path]::GetPathRoot($Workspace)).TrimEnd('\').TrimEnd(':')
$drive = Get-PSDrive -Name $driveName -ErrorAction Stop
$freeGB = [math]::Round($drive.Free / 1GB, 2)
if ($freeGB -lt 16) {
    throw "Only $freeGB GB free on $driveName`:; at least 16 GB free is required before model download."
}
Write-Host ("[OK] Free disk space before models: {0:N2} GB" -f $freeGB) -ForegroundColor Green

$DiffusionDir = Join-Path $ComfyRoot 'models\diffusion_models'
$TextEncoderDir = Join-Path $ComfyRoot 'models\text_encoders'
$VaeDir = Join-Path $ComfyRoot 'models\vae'
$LoraDir = Join-Path $ComfyRoot 'models\loras'

@($DiffusionDir, $TextEncoderDir, $VaeDir, $LoraDir) | ForEach-Object {
    New-Item -ItemType Directory -Force -Path $_ | Out-Null
}

function Download-Verified {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Destination,
        [string]$Sha256,
        [Int64]$MinBytes
    )

    Write-Host ''
    Write-Host "[FILE] $Name" -ForegroundColor Cyan
    Write-Host "  source: $Url"
    Write-Host "  target: $Destination"

    if (Test-Path $Destination) {
        $existingHash = (Get-FileHash -Algorithm SHA256 -Path $Destination).Hash.ToLowerInvariant()
        if ($existingHash -eq $Sha256.ToLowerInvariant()) {
            $bytes = (Get-Item $Destination).Length
            Write-Host ("[OK] Already present and SHA256 verified: {0:N2} GB" -f ($bytes / 1GB)) -ForegroundColor Green
            return
        }
        throw "Existing file has the wrong SHA256 and will not be overwritten automatically: $Destination"
    }

    $part = "$Destination.part"
    if (Test-Path $part) {
        Write-Host '[INFO] Partial file found; curl will attempt HTTP resume.' -ForegroundColor Yellow
    }

    & curl.exe -L --fail --retry 3 --retry-delay 2 -C - --progress-bar -o $part $Url
    if ($LASTEXITCODE -ne 0) {
        throw "Download failed for $Name (curl exit $LASTEXITCODE). Partial file is retained for resume: $part"
    }

    $bytes = (Get-Item $part).Length
    if ($bytes -lt $MinBytes) {
        throw "Downloaded file is unexpectedly small for $Name`: $bytes bytes."
    }

    Write-Host '[CHECK] SHA256...' -ForegroundColor Cyan
    $actualHash = (Get-FileHash -Algorithm SHA256 -Path $part).Hash.ToLowerInvariant()
    if ($actualHash -ne $Sha256.ToLowerInvariant()) {
        throw "SHA256 mismatch for $Name. Expected $Sha256 but got $actualHash. File left as $part for inspection."
    }

    Move-Item -Path $part -Destination $Destination
    Write-Host ("[OK] Verified and installed: {0:N2} GB" -f ($bytes / 1GB)) -ForegroundColor Green
}

# Sources match the current ComfyUI Flux.2 Klein blueprint for the base model,
# Qwen encoder and Flux2 VAE. RefControl is downloaded from the author's model repo.
Download-Verified `
    -Name 'FLUX.2 Klein Base 4B FP8' `
    -Url 'https://huggingface.co/black-forest-labs/FLUX.2-klein-base-4b-fp8/resolve/main/flux-2-klein-base-4b-fp8.safetensors' `
    -Destination (Join-Path $DiffusionDir 'flux-2-klein-base-4b-fp8.safetensors') `
    -Sha256 '44bab3a86fe98b85d21dd2a4729ebdc3ae51fb8a39f76e457e18c724219e6840' `
    -MinBytes 3500000000

Download-Verified `
    -Name 'Qwen3 4B text encoder' `
    -Url 'https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors' `
    -Destination (Join-Path $TextEncoderDir 'qwen_3_4b.safetensors') `
    -Sha256 '6c671498573ac2f7a5501502ccce8d2b08ea6ca2f661c458e708f36b36edfc5a' `
    -MinBytes 7500000000

Download-Verified `
    -Name 'Flux2 VAE' `
    -Url 'https://huggingface.co/Comfy-Org/flux2-dev/resolve/main/split_files/vae/flux2-vae.safetensors' `
    -Destination (Join-Path $VaeDir 'flux2-vae.safetensors') `
    -Sha256 'd64f3a68e1cc4f9f4e29b6e0da38a0204fe9a49f2d4053f0ec1fa1ca02f9c4b5' `
    -MinBytes 300000000

Download-Verified `
    -Name 'RefControl Pose LoRA' `
    -Url 'https://huggingface.co/xocialize/refcontrol-FLUX.2-klein-4B-pose-lora/resolve/main/refcontrol-pose-klein-4b.safetensors' `
    -Destination (Join-Path $LoraDir 'refcontrol-pose-klein-4b.safetensors') `
    -Sha256 'f9880f9070576ff1603c0988ed2afc9957deb0d7dd7c52cf15decbd4087f1339' `
    -MinBytes 80000000

Write-Host ''
Write-Host '[CHECK] Installed model files:' -ForegroundColor Cyan
$targets = @(
    (Join-Path $DiffusionDir 'flux-2-klein-base-4b-fp8.safetensors'),
    (Join-Path $TextEncoderDir 'qwen_3_4b.safetensors'),
    (Join-Path $VaeDir 'flux2-vae.safetensors'),
    (Join-Path $LoraDir 'refcontrol-pose-klein-4b.safetensors')
)
foreach ($p in $targets) {
    $item = Get-Item $p
    Write-Host ("  {0}  {1:N2} GB" -f $item.FullName, ($item.Length / 1GB))
}

Write-Host ''
Write-Host 'STEP 3: PASS' -ForegroundColor Green
Write-Host 'Exactly four model files are installed. No generation was performed.'
