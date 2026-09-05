param(
    [string]$RepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$QwenWorkspace = 'Z:\AI\QwenImageEditSpike'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "G3S-A BOOTSTRAP: FAIL - $Message" -ForegroundColor Red
    exit 1
}

function Run-Step([string]$Label, [string]$ScriptPath, [string[]]$Args) {
    if (-not (Test-Path $ScriptPath -PathType Leaf)) { Fail "Required script missing: $ScriptPath" }
    Write-Host ''
    Write-Host "[$Label] $ScriptPath" -ForegroundColor Cyan
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ScriptPath @Args
    $code = $LASTEXITCODE
    if ($code -ne 0) { Fail "${Label} failed with exit code $code" }
}

Write-Host ''
Write-Host 'Roguelite - G3S-A ONE-COMMAND BOOTSTRAP + STATIC SOURCE' -ForegroundColor Cyan
Write-Host 'Provision missing isolated Qwen runtime/models, then execute G3S-A.'
Write-Host 'No animation frames are generated.' -ForegroundColor Yellow
Write-Host ''

if (-not (Test-Path $RepoRoot -PathType Container)) { Fail "Repository root not found: $RepoRoot" }

$FailureMarker = Join-Path $RepoRoot 'tools\deterministic-character-pipeline\g3v_failure.json'
if (-not (Test-Path $FailureMarker -PathType Leaf)) { Fail "G3V failure marker missing: $FailureMarker. Run git pull --ff-only first." }
$Failure = Get-Content $FailureMarker -Raw | ConvertFrom-Json
if ($Failure.gate -ne 'G3V' -or $Failure.status -ne 'FAIL') { Fail 'G3V is not canonically recorded FAIL.' }

$QwenTools = Join-Path $RepoRoot 'tools\qwen-image-edit-2509-spike'
$Preflight = Join-Path $QwenTools '00_preflight.ps1'
$InstallRuntime = Join-Path $QwenTools '01_install_runtime.ps1'
$DownloadModels = Join-Path $QwenTools '02_download_models.ps1'
$RunG3SA = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\01_run_g3s_a.ps1'

$PortableRoot = Join-Path $QwenWorkspace 'ComfyUI_windows_portable'
$ComfyRoot = Join-Path $PortableRoot 'ComfyUI'
$Python = Join-Path $PortableRoot 'python_embeded\python.exe'
$MainPy = Join-Path $ComfyRoot 'main.py'
$Model = Join-Path $ComfyRoot 'models\unet\Qwen-Image-Edit-2509-Q4_0.gguf'
$Clip = Join-Path $ComfyRoot 'models\text_encoders\qwen_2.5_vl_7b_fp8_scaled.safetensors'
$Vae = Join-Path $ComfyRoot 'models\vae\qwen_image_vae.safetensors'

$RuntimeReady = (Test-Path $Python -PathType Leaf) -and (Test-Path $MainPy -PathType Leaf)
$ModelsReady = (Test-Path $Model -PathType Leaf) -and (Test-Path $Clip -PathType Leaf) -and (Test-Path $Vae -PathType Leaf)

if (-not $RuntimeReady -or -not $ModelsReady) {
    Write-Host '[INFO] Missing G3S-A Qwen dependencies detected.' -ForegroundColor Yellow
    Write-Host '[INFO] Bootstrap may download ~21.5 GB of model weights plus ComfyUI portable.' -ForegroundColor Yellow
    Write-Host '[INFO] Existing valid files are reused; pinned model files are SHA256-verified.' -ForegroundColor Yellow

    # The preserved preflight checks Windows 11, >=40 GB RAM, NVIDIA VRAM,
    # >=40 GB free disk, canonical master, git/curl and 7-Zip/winget availability.
    Run-Step 'PREFLIGHT' $Preflight @('-RepoRoot', $RepoRoot, '-Workspace', $QwenWorkspace)

    if (-not $RuntimeReady) {
        Run-Step 'RUNTIME SETUP' $InstallRuntime @('-Workspace', $QwenWorkspace)
    } else {
        Write-Host '[OK] Existing isolated ComfyUI runtime found.' -ForegroundColor Green
    }

    # Always run the pinned model step when any model was missing. It reuses
    # already-valid files and verifies SHA256 for every model before PASS.
    if (-not $ModelsReady) {
        Run-Step 'MODEL SETUP' $DownloadModels @('-Workspace', $QwenWorkspace)
    }
}

# Final hard verification before inference.
$Required = @($Python,$MainPy,$Model,$Clip,$Vae)
$Missing = @($Required | Where-Object { -not (Test-Path $_ -PathType Leaf) })
if ($Missing.Count -gt 0) {
    Write-Host 'Missing after bootstrap:' -ForegroundColor Red
    $Missing | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    Fail 'Provisioning did not produce all required G3S-A runtime files.'
}

Write-Host ''
Write-Host '[OK] G3S-A runtime/model prerequisites are present.' -ForegroundColor Green
Write-Host '[RUN] Static Exilada source-art gate...' -ForegroundColor Cyan

Run-Step 'G3S-A' $RunG3SA @('-RepoRoot', $RepoRoot, '-QwenWorkspace', $QwenWorkspace)

Write-Host ''
Write-Host 'G3S-A BOOTSTRAP + RUN: COMPLETE' -ForegroundColor Green
Write-Host 'STOP at the G3S-A review artifact. Do not start decomposition or animation.' -ForegroundColor Yellow
