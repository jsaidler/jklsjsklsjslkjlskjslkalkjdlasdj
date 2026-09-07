param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$SsdRoot = 'Z:\AI\SpriteSheetDiffusionSpike'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "SSD-DEPS: FAIL - $Message" -ForegroundColor Red
    exit 1
}

function Find-Conda {
    $cmd = Get-Command conda.exe -ErrorAction SilentlyContinue
    if ($null -ne $cmd) { return $cmd.Source }

    $candidates = @(
        (Join-Path $env:USERPROFILE 'miniconda3\Scripts\conda.exe'),
        (Join-Path $env:LOCALAPPDATA 'miniconda3\Scripts\conda.exe'),
        (Join-Path $env:LOCALAPPDATA 'Programs\Miniconda3\Scripts\conda.exe'),
        'C:\ProgramData\miniconda3\Scripts\conda.exe'
    )
    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) { return $candidate }
    }
    return $null
}

# IMPORTANT POWERSHELL RULE:
# Native programs are never executed under ErrorActionPreference=Stop directly here.
# Windows PowerShell can promote native STDERR into NativeCommandError/RemoteException,
# which previously aborted an expected probe before LASTEXITCODE could be inspected.
function Invoke-NativeStreaming {
    param(
        [Parameter(Mandatory=$true)][string]$FilePath,
        [Parameter(Mandatory=$true)][string[]]$Arguments,
        [Parameter(Mandatory=$true)][string]$FailureMessage,
        [string]$WorkingDirectory = ''
    )

    $oldPreference = $ErrorActionPreference
    $exitCode = -1
    $pushed = $false
    try {
        $ErrorActionPreference = 'Continue'
        if ($WorkingDirectory) {
            Push-Location -LiteralPath $WorkingDirectory
            $pushed = $true
        }
        & $FilePath @Arguments
        $exitCode = $LASTEXITCODE
    } finally {
        if ($pushed) { Pop-Location }
        $ErrorActionPreference = $oldPreference
    }

    if ($exitCode -ne 0) {
        Fail "$FailureMessage (exit $exitCode)"
    }
}

function Invoke-NativeCapture {
    param(
        [Parameter(Mandatory=$true)][string]$FilePath,
        [Parameter(Mandatory=$true)][string[]]$Arguments,
        [string]$WorkingDirectory = ''
    )

    $oldPreference = $ErrorActionPreference
    $exitCode = -1
    $raw = @()
    $pushed = $false
    try {
        $ErrorActionPreference = 'Continue'
        if ($WorkingDirectory) {
            Push-Location -LiteralPath $WorkingDirectory
            $pushed = $true
        }
        $raw = @(& $FilePath @Arguments 2>&1)
        $exitCode = $LASTEXITCODE
    } finally {
        if ($pushed) { Pop-Location }
        $ErrorActionPreference = $oldPreference
    }

    $lines = @()
    foreach ($item in $raw) {
        $lines += $item.ToString()
    }

    return [pscustomobject]@{
        ExitCode = $exitCode
        Lines = $lines
        Text = ($lines -join [Environment]::NewLine)
    }
}

$UpstreamRepo = Join-Path $SsdRoot 'repo'
$ModelTraining = Join-Path $UpstreamRepo 'ModelTraining'
$Inference = Join-Path $ModelTraining 'inference.py'
$UpstreamRequirements = Join-Path $ModelTraining 'requirements.txt'
$EnvMarker = Join-Path $SsdRoot 'ssd_environment_bootstrap.json'
$DependencyMarker = Join-Path $SsdRoot 'ssd_dependencies_bootstrap.json'
$DependencyProbeJson = Join-Path $SsdRoot 'ssd_dependency_probe.json'
$DependencyFreeze = Join-Path $SsdRoot 'ssd_dependency_freeze.txt'
$ProbeScript = Join-Path $SsdRoot 'ssd_dependency_probe.py'
$TorchProbeJson = Join-Path $SsdRoot 'ssd_torch_probe.json'
$TorchProbeScript = Join-Path $SsdRoot 'ssd_torch_probe.py'
$ProjectRequirements = Join-Path $ProjectRepoRoot 'tools\structured-2d-character-pipeline\ssd_windows_inference_requirements.txt'

Write-Host ''
Write-Host 'Roguelite - Sprite Sheet Diffusion Windows dependency bootstrap' -ForegroundColor Cyan
Write-Host '[SCOPE] Inference Python stack + CUDA probe only.' -ForegroundColor Green
Write-Host '[LOCK] No model/checkpoint downloads in this gate.' -ForegroundColor Green
Write-Host '[LOCK] No xformers in this gate; SSD inference treats it as optional.' -ForegroundColor Green
Write-Host '[LOCK] Training/UI-only dependencies are intentionally omitted.' -ForegroundColor Green
Write-Host '[FIX] Native STDERR is isolated from PowerShell ErrorActionPreference=Stop.' -ForegroundColor Green
Write-Host ''

if (-not (Test-Path -LiteralPath $EnvMarker -PathType Leaf)) {
    Fail "environment PASS marker missing: $EnvMarker"
}
try {
    $envState = Get-Content -LiteralPath $EnvMarker -Raw | ConvertFrom-Json
} catch {
    Fail "cannot parse environment marker: $EnvMarker"
}
if ($envState.status -ne 'PASS') {
    Fail 'environment marker is not PASS'
}

foreach ($required in @($UpstreamRepo, $ModelTraining, $Inference, $UpstreamRequirements, $ProjectRequirements)) {
    if (-not (Test-Path -LiteralPath $required)) {
        Fail "required path missing: $required"
    }
}

$script:Conda = Find-Conda
if ($null -eq $script:Conda) {
    Fail 'conda.exe could not be located.'
}
Write-Host "[OK] conda.exe: $script:Conda" -ForegroundColor Green

$CondaRoot = Split-Path -Parent (Split-Path -Parent $script:Conda)
$EnvPython = Join-Path $CondaRoot 'envs\ssd\python.exe'
if (-not (Test-Path -LiteralPath $EnvPython -PathType Leaf)) {
    Fail "ssd environment Python not found: $EnvPython"
}
Write-Host "[OK] env python: $EnvPython" -ForegroundColor Green

$pythonVersionResult = Invoke-NativeCapture -FilePath $EnvPython -Arguments @('--version')
if ($pythonVersionResult.ExitCode -ne 0) {
    Fail "cannot execute Python in env ssd: $($pythonVersionResult.Text)"
}
$pythonVersion = $pythonVersionResult.Text.Trim()
if ($pythonVersion -notmatch '^Python\s+3\.10\.') {
    Fail "expected Python 3.10.x in env ssd, got: $pythonVersion"
}
Write-Host "[OK] environment ssd: $pythonVersion" -ForegroundColor Green

$upstreamRequirementsHash = (Get-FileHash -LiteralPath $UpstreamRequirements -Algorithm SHA256).Hash.ToLowerInvariant()
$projectRequirementsHash = (Get-FileHash -LiteralPath $ProjectRequirements -Algorithm SHA256).Hash.ToLowerInvariant()
Write-Host "[OK] upstream requirements located: $UpstreamRequirements" -ForegroundColor Green
Write-Host "[OK] Windows inference lock:       $ProjectRequirements" -ForegroundColor Green

# Probe Torch without ever returning a non-zero process status for a missing/broken install.
# The Python probe records its own status in JSON, avoiding the PowerShell native STDERR trap.
$torchProbeSource = @'
import json
import os
from pathlib import Path

result = {"installed": False}
try:
    import torch
    import torchvision
    result.update({
        "installed": True,
        "torch": torch.__version__,
        "torchvision": torchvision.__version__,
        "cuda_build": torch.version.cuda,
        "cuda_available": bool(torch.cuda.is_available()),
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
    })
except Exception as exc:
    result["error"] = f"{type(exc).__name__}: {exc}"

Path(os.environ["SSD_TORCH_PROBE_JSON"]).write_text(json.dumps(result, indent=2), encoding="utf-8")
'@
Set-Content -LiteralPath $TorchProbeScript -Value $torchProbeSource -Encoding UTF8
Remove-Item -LiteralPath $TorchProbeJson -Force -ErrorAction SilentlyContinue
$env:SSD_TORCH_PROBE_JSON = $TorchProbeJson
Invoke-NativeStreaming -FilePath $EnvPython -Arguments @($TorchProbeScript) -FailureMessage 'Torch preflight probe process failed'

if (-not (Test-Path -LiteralPath $TorchProbeJson -PathType Leaf)) {
    Fail "Torch preflight probe did not write: $TorchProbeJson"
}
$torchState = Get-Content -LiteralPath $TorchProbeJson -Raw | ConvertFrom-Json
$torchReady = ($torchState.installed -eq $true) -and
              ($torchState.torch -match '^2\.0\.1') -and
              ($torchState.torchvision -match '^0\.15\.2') -and
              ($torchState.cuda_build -eq '11.8') -and
              ($torchState.cuda_available -eq $true)

if (-not $torchReady) {
    if ($torchState.installed -eq $true) {
        Write-Host "[REPAIR] Existing Torch stack is incompatible: torch=$($torchState.torch), torchvision=$($torchState.torchvision), CUDA=$($torchState.cuda_build), available=$($torchState.cuda_available)" -ForegroundColor Yellow
        $torchInstallArgs = @('-m','pip','install','--disable-pip-version-check','--no-cache-dir','--force-reinstall','torch==2.0.1','torchvision==0.15.2','--index-url','https://download.pytorch.org/whl/cu118')
    } else {
        Write-Host '[INSTALL] PyTorch 2.0.1 + torchvision 0.15.2 CUDA 11.8 official wheels...' -ForegroundColor Yellow
        $torchInstallArgs = @('-m','pip','install','--disable-pip-version-check','--no-cache-dir','torch==2.0.1','torchvision==0.15.2','--index-url','https://download.pytorch.org/whl/cu118')
    }
    Invoke-NativeStreaming -FilePath $EnvPython -Arguments $torchInstallArgs -FailureMessage 'PyTorch CUDA install failed'
} else {
    Write-Host '[OK] Required CUDA PyTorch stack already present.' -ForegroundColor Green
}

# Mandatory post-install Torch verification. Probe still exits cleanly and writes JSON.
Remove-Item -LiteralPath $TorchProbeJson -Force -ErrorAction SilentlyContinue
Invoke-NativeStreaming -FilePath $EnvPython -Arguments @($TorchProbeScript) -FailureMessage 'Torch verification probe process failed'
$torchState = Get-Content -LiteralPath $TorchProbeJson -Raw | ConvertFrom-Json
$torchReady = ($torchState.installed -eq $true) -and
              ($torchState.torch -match '^2\.0\.1') -and
              ($torchState.torchvision -match '^0\.15\.2') -and
              ($torchState.cuda_build -eq '11.8') -and
              ($torchState.cuda_available -eq $true)
if (-not $torchReady) {
    Fail "Torch CUDA verification failed. See $TorchProbeJson"
}
Write-Host "[OK] Torch $($torchState.torch), torchvision $($torchState.torchvision), CUDA $($torchState.cuda_build), GPU $($torchState.gpu)" -ForegroundColor Green

Write-Host '[INSTALL] SSD Windows inference-only dependency lock...' -ForegroundColor Yellow
Invoke-NativeStreaming -FilePath $EnvPython -Arguments @('-m','pip','install','--disable-pip-version-check','--no-cache-dir','-r',$ProjectRequirements) -FailureMessage 'SSD inference dependency install failed'

Write-Host '[CHECK] pip dependency consistency...' -ForegroundColor Yellow
Invoke-NativeStreaming -FilePath $EnvPython -Arguments @('-m','pip','check') -FailureMessage 'pip check reported dependency conflicts'

$probeSource = @'
import importlib.util
import json
import os
import sys
import traceback
from pathlib import Path

result = {"status": "FAIL"}
try:
    # The probe script lives outside ModelTraining. Add the inherited working directory
    # explicitly so importing the upstream inference entry point resolves local packages.
    sys.path.insert(0, os.getcwd())

    import torch
    import torchvision
    import av
    import cv2
    import diffusers
    import einops
    import ffmpeg
    import matplotlib
    import mediapipe
    import numpy
    import omegaconf
    import PIL
    import scipy
    import skimage
    import transformers

    if not torch.cuda.is_available():
        raise RuntimeError("torch.cuda.is_available() is False")

    # Import the real SSD entry point and local OpenPose/model/pipeline graph.
    # main() is not executed, so no checkpoint is loaded in this gate.
    import inference

    result.update({
        "status": "PASS",
        "python": sys.version.split()[0],
        "torch": torch.__version__,
        "torchvision": torchvision.__version__,
        "torch_cuda_build": torch.version.cuda,
        "cuda_available": bool(torch.cuda.is_available()),
        "gpu": torch.cuda.get_device_name(0),
        "av": av.__version__,
        "opencv": cv2.__version__,
        "diffusers": diffusers.__version__,
        "mediapipe": mediapipe.__version__,
        "numpy": numpy.__version__,
        "transformers": transformers.__version__,
        "ssd_inference_import": "PASS",
        "xformers_installed": importlib.util.find_spec("xformers") is not None,
    })
except Exception as exc:
    result.update({
        "error": f"{type(exc).__name__}: {exc}",
        "traceback": traceback.format_exc(),
        "ssd_inference_import": "FAIL",
    })

Path(os.environ["SSD_DEP_PROBE_JSON"]).write_text(json.dumps(result, indent=2), encoding="utf-8")
print(f"SSD_INFERENCE_IMPORT={result.get('ssd_inference_import', 'FAIL')}")
if result.get("status") == "PASS":
    print(f"GPU={result['gpu']}")
    print(f"TORCH={result['torch']} CUDA_BUILD={result['torch_cuda_build']}")
else:
    print(f"PROBE_ERROR={result.get('error', 'unknown')}")
'@
Set-Content -LiteralPath $ProbeScript -Value $probeSource -Encoding UTF8
Remove-Item -LiteralPath $DependencyProbeJson -Force -ErrorAction SilentlyContinue
$env:SSD_DEP_PROBE_JSON = $DependencyProbeJson

Write-Host '[PROBE] CUDA + real SSD inference import graph...' -ForegroundColor Yellow
Invoke-NativeStreaming -FilePath $EnvPython -Arguments @($ProbeScript) -FailureMessage 'SSD inference probe process itself failed' -WorkingDirectory $ModelTraining

if (-not (Test-Path -LiteralPath $DependencyProbeJson -PathType Leaf)) {
    Fail "dependency probe did not write: $DependencyProbeJson"
}
$probe = Get-Content -LiteralPath $DependencyProbeJson -Raw | ConvertFrom-Json
if ($probe.status -ne 'PASS' -or $probe.ssd_inference_import -ne 'PASS' -or -not $probe.cuda_available) {
    $detail = if ($null -ne $probe.error) { $probe.error } else { 'unknown probe failure' }
    Fail "SSD inference import probe failed: $detail. Full diagnostic: $DependencyProbeJson"
}

$freezeResult = Invoke-NativeCapture -FilePath $EnvPython -Arguments @('-m','pip','freeze')
if ($freezeResult.ExitCode -ne 0) {
    Fail "pip freeze failed after dependency installation: $($freezeResult.Text)"
}
$freezeResult.Lines | Set-Content -LiteralPath $DependencyFreeze -Encoding UTF8

$markerData = [ordered]@{
    gate = 'SSD_WINDOWS_INFERENCE_DEPENDENCIES'
    status = 'PASS'
    date = (Get-Date).ToString('o')
    ssd_root = $SsdRoot
    upstream_repo = $UpstreamRepo
    model_training = $ModelTraining
    conda_exe = $script:Conda
    env_python = $EnvPython
    environment = 'ssd'
    python = $pythonVersion
    upstream_requirements = $UpstreamRequirements
    upstream_requirements_sha256 = $upstreamRequirementsHash
    project_inference_lock = $ProjectRequirements
    project_inference_lock_sha256 = $projectRequirementsHash
    torch = $probe.torch
    torchvision = $probe.torchvision
    torch_cuda_build = $probe.torch_cuda_build
    gpu = $probe.gpu
    av = $probe.av
    diffusers = $probe.diffusers
    mediapipe = $probe.mediapipe
    numpy = $probe.numpy
    transformers = $probe.transformers
    ssd_inference_import = $probe.ssd_inference_import
    xformers_installed_by_this_gate = $false
    model_weights_downloaded_by_this_gate = $false
    training_ui_dependencies_intentionally_omitted = $true
    native_stderr_handling = 'wrapper temporarily uses ErrorActionPreference=Continue and inspects LASTEXITCODE'
    pip_freeze = $DependencyFreeze
}
$markerData | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $DependencyMarker -Encoding UTF8

Write-Host ''
Write-Host 'SSD-DEPS: PASS' -ForegroundColor Green
Write-Host "GPU:     $($probe.gpu)" -ForegroundColor Green
Write-Host "TORCH:   $($probe.torch) / CUDA build $($probe.torch_cuda_build)" -ForegroundColor Green
Write-Host 'IMPORT:  SSD inference graph PASS' -ForegroundColor Green
Write-Host "MARKER:  $DependencyMarker" -ForegroundColor Cyan
Write-Host "FREEZE:  $DependencyFreeze" -ForegroundColor Cyan
Write-Host ''
Write-Host '[NEXT] Stop here. Model/checkpoint download is the next separate documented gate.' -ForegroundColor Yellow
