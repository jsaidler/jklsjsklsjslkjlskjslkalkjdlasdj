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

function Run-Conda([string[]]$Arguments, [string]$FailureMessage) {
    & $script:Conda @Arguments
    if ($LASTEXITCODE -ne 0) {
        Fail "$FailureMessage (exit $LASTEXITCODE)"
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
$ProjectRequirements = Join-Path $ProjectRepoRoot 'tools\structured-2d-character-pipeline\ssd_windows_inference_requirements.txt'

Write-Host ''
Write-Host 'Roguelite - Sprite Sheet Diffusion Windows dependency bootstrap' -ForegroundColor Cyan
Write-Host '[SCOPE] Inference Python stack + CUDA probe only.' -ForegroundColor Green
Write-Host '[LOCK] No model/checkpoint downloads in this gate.' -ForegroundColor Green
Write-Host '[LOCK] No xformers in this gate; SSD inference treats it as optional.' -ForegroundColor Green
Write-Host '[LOCK] Training/UI-only dependencies are intentionally omitted.' -ForegroundColor Green
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
    Fail "environment marker is not PASS"
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

$pythonVersionOutput = & $script:Conda run -n ssd python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Fail 'cannot execute Python in conda env ssd.'
}
$pythonVersion = ($pythonVersionOutput | Out-String).Trim()
if ($pythonVersion -notmatch '^Python\s+3\.10\.') {
    Fail "expected Python 3.10.x in env ssd, got: $pythonVersion"
}
Write-Host "[OK] environment ssd: $pythonVersion" -ForegroundColor Green

$upstreamRequirementsHash = (Get-FileHash -LiteralPath $UpstreamRequirements -Algorithm SHA256).Hash.ToLowerInvariant()
$projectRequirementsHash = (Get-FileHash -LiteralPath $ProjectRequirements -Algorithm SHA256).Hash.ToLowerInvariant()
Write-Host "[OK] upstream requirements located: $UpstreamRequirements" -ForegroundColor Green
Write-Host "[OK] Windows inference lock:       $ProjectRequirements" -ForegroundColor Green

# Upstream pins torch 2.0.1 / torchvision 0.15.2. Install the official CUDA 11.8 wheels
# explicitly so Windows does not accidentally receive a CPU-only or mismatched build.
$torchReady = $false
$torchProbe = & $script:Conda run -n ssd python -c "import torch, torchvision; print(torch.__version__); print(torchvision.__version__); print(torch.version.cuda); print(torch.cuda.is_available())" 2>&1
if ($LASTEXITCODE -eq 0) {
    $torchText = ($torchProbe | Out-String)
    if (($torchText -match '2\.0\.1') -and ($torchText -match '0\.15\.2') -and ($torchText -match '11\.8') -and ($torchText -match 'True')) {
        $torchReady = $true
    }
}

if (-not $torchReady) {
    Write-Host '[INSTALL] PyTorch 2.0.1 + torchvision 0.15.2 CUDA 11.8 official wheels...' -ForegroundColor Yellow
    Run-Conda @('run','-n','ssd','python','-m','pip','install','--disable-pip-version-check','--no-cache-dir','torch==2.0.1','torchvision==0.15.2','--index-url','https://download.pytorch.org/whl/cu118') 'PyTorch CUDA install failed'
} else {
    Write-Host '[OK] Required CUDA PyTorch stack already present.' -ForegroundColor Green
}

Write-Host '[INSTALL] SSD Windows inference-only dependency lock...' -ForegroundColor Yellow
Run-Conda @('run','-n','ssd','python','-m','pip','install','--disable-pip-version-check','--no-cache-dir','-r',$ProjectRequirements) 'SSD inference dependency install failed'

Write-Host '[CHECK] pip dependency consistency...' -ForegroundColor Yellow
Run-Conda @('run','-n','ssd','python','-m','pip','check') 'pip check reported dependency conflicts'

$probeSource = @'
import json
import os
import sys
from pathlib import Path

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

# This imports the real SSD entry point and its local OpenPose / model / pipeline graph,
# but does not load any checkpoints because main() is not executed.
import inference

result = {
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
    "xformers_installed": False,
}
Path(os.environ["SSD_DEP_PROBE_JSON"]).write_text(json.dumps(result, indent=2), encoding="utf-8")
print("SSD_INFERENCE_IMPORT=PASS")
print(f"GPU={result['gpu']}")
print(f"TORCH={result['torch']} CUDA_BUILD={result['torch_cuda_build']}")
'@
Set-Content -LiteralPath $ProbeScript -Value $probeSource -Encoding UTF8
$env:SSD_DEP_PROBE_JSON = $DependencyProbeJson

Write-Host '[PROBE] CUDA + real SSD inference import graph...' -ForegroundColor Yellow
Push-Location $ModelTraining
try {
    & $script:Conda run -n ssd python $ProbeScript
    if ($LASTEXITCODE -ne 0) {
        Fail "SSD inference import probe failed (exit $LASTEXITCODE)"
    }
} finally {
    Pop-Location
}

if (-not (Test-Path -LiteralPath $DependencyProbeJson -PathType Leaf)) {
    Fail "dependency probe did not write: $DependencyProbeJson"
}
$probe = Get-Content -LiteralPath $DependencyProbeJson -Raw | ConvertFrom-Json
if ($probe.status -ne 'PASS' -or $probe.ssd_inference_import -ne 'PASS' -or -not $probe.cuda_available) {
    Fail 'dependency probe JSON did not report PASS.'
}

$freezeOutput = & $script:Conda run -n ssd python -m pip freeze 2>&1
if ($LASTEXITCODE -ne 0) {
    Fail 'pip freeze failed after dependency installation.'
}
$freezeOutput | Set-Content -LiteralPath $DependencyFreeze -Encoding UTF8

$markerData = [ordered]@{
    gate = 'SSD_WINDOWS_INFERENCE_DEPENDENCIES'
    status = 'PASS'
    date = (Get-Date).ToString('o')
    ssd_root = $SsdRoot
    upstream_repo = $UpstreamRepo
    model_training = $ModelTraining
    conda_exe = $script:Conda
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
    pip_freeze = $DependencyFreeze
}
$markerData | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $DependencyMarker -Encoding UTF8

Write-Host ''
Write-Host 'SSD-DEPS: PASS' -ForegroundColor Green
Write-Host "GPU:     $($probe.gpu)" -ForegroundColor Green
Write-Host "TORCH:   $($probe.torch) / CUDA build $($probe.torch_cuda_build)" -ForegroundColor Green
Write-Host "IMPORT:  SSD inference graph PASS" -ForegroundColor Green
Write-Host "MARKER:  $DependencyMarker" -ForegroundColor Cyan
Write-Host "FREEZE:  $DependencyFreeze" -ForegroundColor Cyan
Write-Host ''
Write-Host '[NEXT] Stop here. Model/checkpoint download is the next separate documented gate.' -ForegroundColor Yellow
