param(
    [string]$Workspace = 'D:\AI\Flux2RefControlSpike'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$DownloadDir = Join-Path $Workspace '_downloads'
$Archive = Join-Path $DownloadDir 'ComfyUI_windows_portable_nvidia.7z'
$PortableRoot = Join-Path $Workspace 'ComfyUI_windows_portable'
$ComfyMain = Join-Path $PortableRoot 'ComfyUI\main.py'
$EmbeddedPython = Join-Path $PortableRoot 'python_embeded\python.exe'
$OfficialUrl = 'https://github.com/Comfy-Org/ComfyUI/releases/latest/download/ComfyUI_windows_portable_nvidia.7z'

function Find-7Zip {
    $candidates = @(
        (Join-Path $env:ProgramFiles '7-Zip\7z.exe'),
        (Join-Path ${env:ProgramFiles(x86)} '7-Zip\7z.exe')
    ) | Where-Object { $_ -and (Test-Path $_) }
    if ($candidates.Count -gt 0) { return $candidates[0] }
    $cmd = Get-Command 7z.exe -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    return $null
}

Write-Host ''
Write-Host 'FLUX.2 Klein + RefControl Pose spike - STEP 1: ComfyUI portable only' -ForegroundColor Cyan
Write-Host 'This step downloads ComfyUI Portable for NVIDIA and extracts it.'
Write-Host 'NO model weights are downloaded by this script.'
Write-Host ''
Write-Host "Workspace: $Workspace"
Write-Host "Official asset: $OfficialUrl"
Write-Host ''

New-Item -ItemType Directory -Force -Path $Workspace | Out-Null
New-Item -ItemType Directory -Force -Path $DownloadDir | Out-Null

$SevenZip = Find-7Zip
if (-not $SevenZip) {
    Write-Host '[INFO] 7-Zip not found. Installing via winget...' -ForegroundColor Yellow
    if (-not (Get-Command winget.exe -ErrorAction SilentlyContinue)) {
        throw '7-Zip is missing and winget is unavailable.'
    }
    & winget.exe install --id 7zip.7zip -e --accept-package-agreements --accept-source-agreements --silent
    if ($LASTEXITCODE -ne 0) { throw "winget failed installing 7-Zip (exit $LASTEXITCODE)." }
    $SevenZip = Find-7Zip
    if (-not $SevenZip) { throw '7-Zip installation completed but 7z.exe still cannot be located.' }
}
Write-Host "[OK] 7-Zip: $SevenZip" -ForegroundColor Green

if (Test-Path $ComfyMain) {
    Write-Host "[INFO] ComfyUI portable already exists at $PortableRoot" -ForegroundColor Yellow
    Write-Host '[INFO] Existing runtime will be validated; archive will not be downloaded again.'
} else {
    if (-not (Test-Path $Archive)) {
        Write-Host '[DOWNLOAD] Fetching official latest ComfyUI NVIDIA portable...' -ForegroundColor Cyan
        & curl.exe -L --fail --progress-bar $OfficialUrl -o $Archive
        if ($LASTEXITCODE -ne 0) { throw "ComfyUI portable download failed (curl exit $LASTEXITCODE)." }
    } else {
        Write-Host "[INFO] Archive already present: $Archive" -ForegroundColor Yellow
    }

    $archiveBytes = (Get-Item $Archive).Length
    if ($archiveBytes -lt 100MB) {
        throw "Downloaded archive is unexpectedly small: $archiveBytes bytes"
    }
    Write-Host ("[OK] Archive size: {0:N2} GB" -f ($archiveBytes / 1GB)) -ForegroundColor Green

    Write-Host '[CHECK] Testing 7z archive integrity...' -ForegroundColor Cyan
    & $SevenZip t $Archive | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "7-Zip archive test failed (exit $LASTEXITCODE)." }

    Write-Host '[EXTRACT] Extracting ComfyUI portable...' -ForegroundColor Cyan
    & $SevenZip x $Archive "-o$Workspace" -y | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "7-Zip extraction failed (exit $LASTEXITCODE)." }
}

if (-not (Test-Path $ComfyMain)) { throw "ComfyUI main.py not found after extraction: $ComfyMain" }
if (-not (Test-Path $EmbeddedPython)) { throw "Embedded Python not found: $EmbeddedPython" }

Write-Host ''
Write-Host '[CHECK] Embedded Python:' -ForegroundColor Cyan
& $EmbeddedPython --version
if ($LASTEXITCODE -ne 0) { throw 'Embedded Python validation failed.' }

Write-Host ''
Write-Host '[CHECK] PyTorch/CUDA runtime:' -ForegroundColor Cyan
$probe = @'
import torch
print(f"torch={torch.__version__}")
print(f"cuda_runtime={torch.version.cuda}")
print(f"cuda_available={torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"gpu={torch.cuda.get_device_name(0)}")
    print(f"vram_gb={torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f}")
'@
& $EmbeddedPython -c $probe
if ($LASTEXITCODE -ne 0) { throw 'PyTorch/CUDA validation failed.' }

Write-Host ''
Write-Host 'STEP 1: PASS' -ForegroundColor Green
Write-Host "ComfyUI portable: $PortableRoot"
Write-Host 'No FLUX, Qwen, VAE, LoRA, OpenPose, or other model files were downloaded.'
