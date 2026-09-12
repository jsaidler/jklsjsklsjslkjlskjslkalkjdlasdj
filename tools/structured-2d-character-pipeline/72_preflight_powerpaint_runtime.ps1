param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$RuntimeWorkspace = 'Z:\AI\QwenImageEdit',
    [string]$PowerPaintWorkspace = 'Z:\AI\PowerPaint'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "RUNNER72-PREFLIGHT: FAIL - $Message" -ForegroundColor Red
    exit 1
}

$PortableRoot = Join-Path $RuntimeWorkspace 'ComfyUI_windows_portable'
$BasePython = Join-Path $PortableRoot 'python_embeded\python.exe'
$LegacyVenvRoot = Join-Path $PowerPaintWorkspace 'venv'
$PyDepsRoot = Join-Path $PowerPaintWorkspace 'pydeps'
$DepsMarker = Join-Path $PowerPaintWorkspace '.powerpaint_pydeps_0.29.2_0.31.0_0.11.1.ok'
$OverlayLauncher = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\python_overlay_launcher.py'

foreach ($required in @($BasePython,$OverlayLauncher)) {
    if (-not (Test-Path $required -PathType Leaf)) { Fail "required file missing: $required" }
}

New-Item -ItemType Directory -Force -Path $PowerPaintWorkspace | Out-Null

if (Test-Path $LegacyVenvRoot -PathType Container) {
    Write-Host 'Removing failed Runner72 legacy venv...' -ForegroundColor Yellow
    Remove-Item -LiteralPath $LegacyVenvRoot -Recurse -Force
}

Write-Host 'Checking base embedded Python/Torch...' -ForegroundColor Cyan
& $BasePython -s -c "import torch; print('Base portable Torch OK', torch.__version__, 'CUDA', torch.cuda.is_available())"
if ($LASTEXITCODE -ne 0) { Fail 'base portable Python does not see Torch' }

if (-not (Test-Path $DepsMarker -PathType Leaf)) {
    if (Test-Path $PyDepsRoot -PathType Container) {
        Write-Host 'Removing incomplete dependency overlay...' -ForegroundColor Yellow
        Remove-Item -LiteralPath $PyDepsRoot -Recurse -Force
    }
    New-Item -ItemType Directory -Force -Path $PyDepsRoot | Out-Null

    $ok=$false
    for ($attempt=1; $attempt -le 5; $attempt++) {
        Write-Host "Installing PowerPaint process-local dependency overlay (attempt $attempt/5)..." -ForegroundColor Cyan
        & $BasePython -s -m pip install --disable-pip-version-check --retries 12 --timeout 120 --no-deps --upgrade --target $PyDepsRoot 'diffusers==0.29.2' 'accelerate==0.31.0' 'peft==0.11.1'
        if ($LASTEXITCODE -eq 0) { $ok=$true; break }
        if ($attempt -lt 5) { Start-Sleep -Seconds (10*$attempt) }
    }
    if (-not $ok) { Fail 'dependency overlay installation failed' }
    Set-Content -LiteralPath $DepsMarker -Value 'diffusers=0.29.2 accelerate=0.31.0 peft=0.11.1 overlay=pydeps' -Encoding ASCII
}

Write-Host 'Checking process-local overlay imports...' -ForegroundColor Cyan
$probe = "import sys; sys.path.insert(0, r'$PyDepsRoot'); import torch, diffusers, accelerate, peft; assert diffusers.__version__ == '0.29.2'; assert accelerate.__version__ == '0.31.0'; assert peft.__version__ == '0.11.1'; print('PowerPaint overlay imports OK', torch.__version__, diffusers.__version__, accelerate.__version__, peft.__version__)"
& $BasePython -s -c $probe
if ($LASTEXITCODE -ne 0) {
    Remove-Item -LiteralPath $DepsMarker -Force -ErrorAction SilentlyContinue
    Fail 'process-local dependency overlay import check failed'
}

Write-Host ''
Write-Host 'RUNNER72-PREFLIGHT: PASS - BASE TORCH + ISOLATED POWERPAINT OVERLAY VERIFIED' -ForegroundColor Green
Write-Host 'No PowerPaint model payload was downloaded by this preflight.' -ForegroundColor Green
