param(
    [string]$Workspace = 'Z:\AI\QwenImageEditSpike'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$PortableRoot = Join-Path $Workspace 'ComfyUI_windows_portable'
$ComfyRoot = Join-Path $PortableRoot 'ComfyUI'
$ModelManifest = Join-Path $Workspace 'model_manifest.json'

$Files = @(
    [ordered]@{
        role = 'diffusion_model_gguf'
        name = 'Qwen-Image-Edit-2509-Q4_0.gguf'
        dest = Join-Path $ComfyRoot 'models\unet\Qwen-Image-Edit-2509-Q4_0.gguf'
        url = 'https://huggingface.co/QuantStack/Qwen-Image-Edit-2509-GGUF/resolve/main/Qwen-Image-Edit-2509-Q4_0.gguf'
        sha256 = '4f6cda402e1dbc36ee4b601b10b9ee0da2dbefedfbfa53eae3efb0ddff48c3e2'
    },
    [ordered]@{
        role = 'text_encoder'
        name = 'qwen_2.5_vl_7b_fp8_scaled.safetensors'
        dest = Join-Path $ComfyRoot 'models\text_encoders\qwen_2.5_vl_7b_fp8_scaled.safetensors'
        url = 'https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors'
        sha256 = 'cb5636d852a0ea6a9075ab1bef496c0db7aef13c02350571e388aea959c5c0b4'
    },
    [ordered]@{
        role = 'vae'
        name = 'qwen_image_vae.safetensors'
        dest = Join-Path $ComfyRoot 'models\vae\qwen_image_vae.safetensors'
        url = 'https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/vae/qwen_image_vae.safetensors'
        sha256 = 'a70580f0213e67967ee9c95f05bb400e8fb08307e017a924bf3441223e023d1f'
    }
)

function Download-Verified([hashtable]$File) {
    $parent = Split-Path -Parent $File.dest
    New-Item -ItemType Directory -Force -Path $parent | Out-Null

    if (Test-Path $File.dest -PathType Leaf) {
        $existing = (Get-FileHash -LiteralPath $File.dest -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($existing -eq $File.sha256) {
            Write-Host "[OK] $($File.name) already present and hash-valid." -ForegroundColor Green
            return
        }
        throw "Existing file has wrong SHA256 and will not be overwritten automatically: $($File.dest)"
    }

    $part = $File.dest + '.part'
    Write-Host "[DOWNLOAD] $($File.name)" -ForegroundColor Cyan
    Write-Host "           $($File.url)" -ForegroundColor DarkGray
    & curl.exe -L --fail --retry 4 --retry-delay 5 -C - --progress-bar $File.url -o $part
    if ($LASTEXITCODE -ne 0) { throw "Download failed for $($File.name) (curl exit $LASTEXITCODE)." }

    $hash = (Get-FileHash -LiteralPath $part -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($hash -ne $File.sha256) {
        throw "SHA256 mismatch for $($File.name). expected=$($File.sha256) actual=$hash"
    }
    Move-Item -LiteralPath $part -Destination $File.dest -Force
    Write-Host "[OK] $($File.name) sha256=$hash" -ForegroundColor Green
}

function Write-Utf8Json([object]$Object, [string]$Path) {
    $json = $Object | ConvertTo-Json -Depth 16
    [System.IO.File]::WriteAllText($Path, $json, [System.Text.UTF8Encoding]::new($false))
}

Write-Host ''
Write-Host 'Qwen-Image-Edit-2509 keypoint spike - STEP 3: DOWNLOAD PINNED MODEL SET' -ForegroundColor Cyan
Write-Host 'Downloads exactly 3 files. No Lightning LoRA. No model load. No inference.' -ForegroundColor Yellow
Write-Host ''

if (-not (Test-Path (Join-Path $ComfyRoot 'main.py') -PathType Leaf)) {
    throw "Isolated ComfyUI runtime not found. Run 01_install_runtime.ps1 first: $ComfyRoot"
}
if (-not (Get-Command curl.exe -ErrorAction SilentlyContinue)) { throw 'curl.exe not found.' }

foreach ($f in $Files) { Download-Verified $f }

$records = @()
foreach ($f in $Files) {
    $info = Get-Item -LiteralPath $f.dest
    $hash = (Get-FileHash -LiteralPath $f.dest -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($hash -ne $f.sha256) { throw "Post-download hash mismatch: $($f.name)" }
    $records += [ordered]@{
        role = $f.role
        name = $f.name
        path = $f.dest
        bytes = [int64]$info.Length
        sha256 = $hash
        source_url = $f.url
    }
}

$manifest = [ordered]@{
    spike = 'Qwen-Image-Edit-2509 native keypoint topology gate'
    stage = 'models_ready_no_inference'
    workspace = $Workspace
    model_choice = 'Q4_0 GGUF selected for RTX 3060 12 GB; better quality than Q3 while allowing low-VRAM offload'
    lightning_lora_used = $false
    files = $records
    inference_performed = $false
    created_at = (Get-Date).ToString('o')
}
Write-Utf8Json $manifest $ModelManifest

Write-Host ''
Write-Host 'STEP 3: PASS' -ForegroundColor Green
Write-Host 'Exactly three pinned model files are present and SHA256-validated.'
Write-Host "Manifest: $ModelManifest"
Write-Host 'No model was loaded and no inference was performed.' -ForegroundColor Green
