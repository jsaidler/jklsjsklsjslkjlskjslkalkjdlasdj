param(
    [switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Models = Join-Path $Root 'models'

function Ensure-Dir([string]$Path) {
    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

function Download-File {
    param(
        [Parameter(Mandatory=$true)][string]$Url,
        [Parameter(Mandatory=$true)][string]$Destination,
        [string]$Sha256 = ''
    )

    Ensure-Dir (Split-Path -Parent $Destination)

    if ((Test-Path $Destination) -and -not $Force) {
        if ($Sha256) {
            $actual = (Get-FileHash -Algorithm SHA256 $Destination).Hash.ToLowerInvariant()
            if ($actual -eq $Sha256.ToLowerInvariant()) {
                Write-Host "OK (already downloaded): $Destination"
                return
            }
            Write-Warning "Checksum mismatch on existing file. Re-downloading: $Destination"
        } else {
            Write-Host "Exists (checksum not pinned): $Destination"
            return
        }
    }

    $tmp = "$Destination.part"
    if (Test-Path $tmp) { Remove-Item $tmp -Force }

    Write-Host "Downloading: $Destination"
    & curl.exe -L --fail --retry 5 --retry-delay 2 --output $tmp $Url
    if ($LASTEXITCODE -ne 0) {
        throw "Download failed: $Url"
    }

    Move-Item $tmp $Destination -Force

    if ($Sha256) {
        $actual = (Get-FileHash -Algorithm SHA256 $Destination).Hash.ToLowerInvariant()
        if ($actual -ne $Sha256.ToLowerInvariant()) {
            Remove-Item $Destination -Force
            throw "SHA256 mismatch for $Destination`nExpected: $Sha256`nActual:   $actual"
        }
    }
}

if (-not (Get-Command curl.exe -ErrorAction SilentlyContinue)) {
    throw 'curl.exe was not found. Windows 11 normally ships it in System32.'
}

# Sprite-Sheet-Diffusion finetuned UNets recovered/re-hosted by fszontagh.
Download-File `
    'https://huggingface.co/fszontagh/sprite-sheet-diffusion/resolve/main/denoising_unet.pth?download=true' `
    (Join-Path $Models 'ssd\denoising_unet.pth') `
    '341cca53cfaa4e0c05098e511b8a3dc1a0db90c6ec68f345ba14115e0d3e43ac'

Download-File `
    'https://huggingface.co/fszontagh/sprite-sheet-diffusion/resolve/main/reference_unet.pth?download=true' `
    (Join-Path $Models 'ssd\reference_unet.pth') `
    '84194364a42b5ae8b2a93a60b02a36ed0f989c230bb4c3ee33d7956bba5d0dcc'

# Baseline AnimateAnyone components required because SSD never released its trained pose guider.
Download-File `
    'https://huggingface.co/patrolli/AnimateAnyone/resolve/main/pose_guider.pth?download=true' `
    (Join-Path $Models 'animate-anyone\pose_guider.pth') `
    '1a8b7c1b4db92980fd977b4fd003c1396bbae9a9cdea00c35d452136d5e4f488'

Download-File `
    'https://huggingface.co/patrolli/AnimateAnyone/resolve/main/motion_module.pth?download=true' `
    (Join-Path $Models 'animate-anyone\motion_module.pth') `
    '0d11e01a281b39880da2efeea892215c1313e5713fca3d100a7fbb72ee312ef9'

# CLIP vision encoder used by AnimateAnyone.
Download-File `
    'https://huggingface.co/lambda/sd-image-variations-diffusers/resolve/main/image_encoder/pytorch_model.bin?download=true' `
    (Join-Path $Models 'image_encoder\pytorch_model.bin')

# VAE.
Download-File `
    'https://huggingface.co/stabilityai/sd-vae-ft-mse/resolve/main/diffusion_pytorch_model.safetensors?download=true' `
    (Join-Path $Models 'sd-vae-ft-mse\diffusion_pytorch_model.safetensors') `
    'a1d993488569e928462932c8c38a0760b874d166399b14414135bd9c42df5815'

Write-Host ''
Write-Host 'All animation model files are present.' -ForegroundColor Green
