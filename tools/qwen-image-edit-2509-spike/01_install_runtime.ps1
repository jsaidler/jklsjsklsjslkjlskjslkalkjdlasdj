param(
    [string]$Workspace = 'Z:\AI\QwenImageEditSpike'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$DownloadDir = Join-Path $Workspace '_downloads'
$Archive = Join-Path $DownloadDir 'ComfyUI_windows_portable_nvidia.7z'
$PortableRoot = Join-Path $Workspace 'ComfyUI_windows_portable'
$ComfyRoot = Join-Path $PortableRoot 'ComfyUI'
$ComfyMain = Join-Path $ComfyRoot 'main.py'
$EmbeddedPython = Join-Path $PortableRoot 'python_embeded\python.exe'
$CustomNodeDir = Join-Path $ComfyRoot 'custom_nodes\ComfyUI-GGUF'
$RuntimeManifest = Join-Path $Workspace 'runtime_manifest.json'
$OfficialComfyUrl = 'https://github.com/Comfy-Org/ComfyUI/releases/latest/download/ComfyUI_windows_portable_nvidia.7z'
$GgufRepo = 'https://github.com/city96/ComfyUI-GGUF.git'
$GgufCommit = '6ea2651e7df66d7585f6ffee804b20e92fb38b8a'

function Find-7Zip {
    $candidates = @()
    if ($env:ProgramFiles) { $candidates += (Join-Path $env:ProgramFiles '7-Zip\7z.exe') }
    $pf86 = [Environment]::GetEnvironmentVariable('ProgramFiles(x86)')
    if ($pf86) { $candidates += (Join-Path $pf86 '7-Zip\7z.exe') }
    $cmd = Get-Command 7z.exe -ErrorAction SilentlyContinue
    if ($cmd) { $candidates += $cmd.Source }
    return @($candidates | Where-Object { $_ -and (Test-Path $_) } | Select-Object -Unique)[0]
}

function Write-Utf8Json([object]$Object, [string]$Path) {
    $json = $Object | ConvertTo-Json -Depth 16
    [System.IO.File]::WriteAllText($Path, $json, [System.Text.UTF8Encoding]::new($false))
}

Write-Host ''
Write-Host 'Qwen-Image-Edit-2509 keypoint spike - STEP 2: ISOLATED RUNTIME SETUP' -ForegroundColor Cyan
Write-Host 'Installs ComfyUI Portable + pinned ComfyUI-GGUF only.'
Write-Host 'NO Qwen model weights are downloaded by this step.' -ForegroundColor Yellow
Write-Host "Workspace: $Workspace"
Write-Host ''

New-Item -ItemType Directory -Force -Path $Workspace | Out-Null
New-Item -ItemType Directory -Force -Path $DownloadDir | Out-Null

$SevenZip = Find-7Zip
if (-not $SevenZip) {
    if (-not (Get-Command winget.exe -ErrorAction SilentlyContinue)) {
        throw '7-Zip is missing and winget is unavailable.'
    }
    Write-Host '[INSTALL] 7-Zip via winget...' -ForegroundColor Yellow
    & winget.exe install --id 7zip.7zip -e --accept-package-agreements --accept-source-agreements --silent
    if ($LASTEXITCODE -ne 0) { throw "winget failed installing 7-Zip (exit $LASTEXITCODE)." }
    $SevenZip = Find-7Zip
    if (-not $SevenZip) { throw '7-Zip install finished but 7z.exe still cannot be located.' }
}
Write-Host "[OK] 7-Zip: $SevenZip" -ForegroundColor Green

if (-not (Test-Path $ComfyMain -PathType Leaf)) {
    if (-not (Test-Path $Archive -PathType Leaf)) {
        Write-Host '[DOWNLOAD] Official latest ComfyUI NVIDIA portable...' -ForegroundColor Cyan
        & curl.exe -L --fail --retry 3 --progress-bar $OfficialComfyUrl -o $Archive
        if ($LASTEXITCODE -ne 0) { throw "ComfyUI portable download failed (curl exit $LASTEXITCODE)." }
    } else {
        Write-Host "[INFO] Reusing existing archive: $Archive" -ForegroundColor Yellow
    }

    if ((Get-Item $Archive).Length -lt 100MB) { throw 'ComfyUI archive is unexpectedly small.' }
    Write-Host '[CHECK] Testing ComfyUI archive...' -ForegroundColor Cyan
    & $SevenZip t $Archive | Out-Host
    if ($LASTEXITCODE -ne 0) { throw '7-Zip archive integrity test failed.' }

    Write-Host '[EXTRACT] ComfyUI portable...' -ForegroundColor Cyan
    & $SevenZip x $Archive "-o$Workspace" -y | Out-Host
    if ($LASTEXITCODE -ne 0) { throw 'ComfyUI extraction failed.' }
} else {
    Write-Host "[INFO] Existing isolated ComfyUI portable found: $PortableRoot" -ForegroundColor Yellow
}

if (-not (Test-Path $ComfyMain -PathType Leaf)) { throw "Missing ComfyUI main.py: $ComfyMain" }
if (-not (Test-Path $EmbeddedPython -PathType Leaf)) { throw "Missing embedded Python: $EmbeddedPython" }

if (Test-Path (Join-Path $CustomNodeDir '.git') -PathType Container) {
    $origin = (& git -C $CustomNodeDir remote get-url origin).Trim()
    if ($LASTEXITCODE -ne 0 -or $origin -notmatch 'city96/ComfyUI-GGUF') {
        throw "Existing ComfyUI-GGUF directory has unexpected origin: $origin"
    }
    & git -C $CustomNodeDir fetch --all --tags --prune
    if ($LASTEXITCODE -ne 0) { throw 'Failed to fetch ComfyUI-GGUF.' }
} elseif (Test-Path $CustomNodeDir) {
    throw "Custom node path exists but is not a git checkout: $CustomNodeDir"
} else {
    Write-Host '[CLONE] ComfyUI-GGUF...' -ForegroundColor Cyan
    & git clone $GgufRepo $CustomNodeDir
    if ($LASTEXITCODE -ne 0) { throw 'Failed to clone ComfyUI-GGUF.' }
}

Write-Host "[PIN] ComfyUI-GGUF -> $GgufCommit" -ForegroundColor Cyan
& git -C $CustomNodeDir checkout --detach $GgufCommit
if ($LASTEXITCODE -ne 0) { throw 'Failed to checkout pinned ComfyUI-GGUF commit.' }
$ActualGgufCommit = (& git -C $CustomNodeDir rev-parse HEAD).Trim()
if ($ActualGgufCommit -ne $GgufCommit) { throw "GGUF commit mismatch: $ActualGgufCommit" }

Write-Host '[PIP] Installing ComfyUI-GGUF requirements into embedded Python...' -ForegroundColor Cyan
& $EmbeddedPython -s -m pip install -r (Join-Path $CustomNodeDir 'requirements.txt')
if ($LASTEXITCODE -ne 0) { throw 'ComfyUI-GGUF requirement installation failed.' }

$probePath = Join-Path $Workspace '_runtime_probe.py'
$probeCode = @'
import json, torch, sys
out = {
    "python": sys.version,
    "torch": str(torch.__version__),
    "cuda_runtime": str(torch.version.cuda),
    "cuda_available": bool(torch.cuda.is_available()),
}
if torch.cuda.is_available():
    p = torch.cuda.get_device_properties(0)
    out["gpu"] = torch.cuda.get_device_name(0)
    out["vram_gb"] = round(p.total_memory / (1024**3), 2)
print(json.dumps(out))
'@
[System.IO.File]::WriteAllText($probePath, $probeCode, [System.Text.UTF8Encoding]::new($false))
try {
    $probeRaw = (& $EmbeddedPython $probePath | Select-Object -Last 1)
    if ($LASTEXITCODE -ne 0 -or -not $probeRaw) { throw 'Runtime probe failed.' }
    $probe = $probeRaw | ConvertFrom-Json
} finally {
    Remove-Item $probePath -Force -ErrorAction SilentlyContinue
}

if (-not [bool]$probe.cuda_available) { throw 'CUDA is not available in isolated ComfyUI runtime.' }

$manifest = [ordered]@{
    spike = 'Qwen-Image-Edit-2509 native keypoint topology gate'
    stage = 'runtime_ready_no_models'
    workspace = $Workspace
    comfy_portable = $PortableRoot
    comfy_source = $OfficialComfyUrl
    comfy_gguf_repo = $GgufRepo
    comfy_gguf_commit = $ActualGgufCommit
    python = [string]$probe.python
    torch = [string]$probe.torch
    cuda_runtime = [string]$probe.cuda_runtime
    gpu = [string]$probe.gpu
    vram_gb = [double]$probe.vram_gb
    model_weights_downloaded = $false
    inference_performed = $false
    created_at = (Get-Date).ToString('o')
}
Write-Utf8Json $manifest $RuntimeManifest

Write-Host ''
Write-Host 'STEP 2: PASS' -ForegroundColor Green
Write-Host "ComfyUI portable: $PortableRoot"
Write-Host "ComfyUI-GGUF commit: $ActualGgufCommit"
Write-Host "GPU: $($probe.gpu); VRAM $($probe.vram_gb) GB"
Write-Host "Manifest: $RuntimeManifest"
Write-Host 'No Qwen model weights were downloaded and no inference was performed.' -ForegroundColor Green
