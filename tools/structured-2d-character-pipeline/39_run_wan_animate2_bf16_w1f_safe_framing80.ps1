param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$Workspace = 'Z:\AI\WanAnimate2',
    [int]$Port = 8188,
    [int]$TimeoutMinutes = 240,
    [double]$SafeScale = 0.80
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "RUNNER39-WAN-W1F: FAIL - $Message" -ForegroundColor Red
    exit 1
}

function Find-ComfyRoot([string]$Base) {
    foreach ($candidate in @($Base, (Join-Path $Base 'ComfyUI'))) {
        if (Test-Path (Join-Path $candidate 'main.py') -PathType Leaf) { return $candidate }
    }
    return $null
}

function Find-WorkspacePython([string]$Base, [string]$ComfyRoot) {
    foreach ($candidate in @(
        (Join-Path $ComfyRoot '.venv\Scripts\python.exe'),
        (Join-Path $Base '.venv\Scripts\python.exe')
    ) | Select-Object -Unique) {
        if (Test-Path $candidate -PathType Leaf) { return $candidate }
    }
    return $null
}

$Executor = Join-Path $ProjectRepoRoot 'tools\wan-animate2-spike\run_w1f_safe_framing.py'
$W1Prompt = Join-Path $Workspace 'w1_api_prompt.json'
$W1Manifest = Join-Path $Workspace 'w1_run_manifest.json'
foreach ($f in @($Executor,$W1Prompt,$W1Manifest)) {
    if (-not (Test-Path $f -PathType Leaf)) { Fail "required file missing: $f" }
}

$ComfyRoot = Find-ComfyRoot $Workspace
if (-not $ComfyRoot) { Fail "ComfyUI root not found under $Workspace" }
$WorkspacePython = Find-WorkspacePython $Workspace $ComfyRoot
if (-not $WorkspacePython) { Fail "ComfyUI Python environment not found under $Workspace" }

Write-Host ''
Write-Host 'Roguelite Runner 39 — Wan-Animate-2 Base BF16 W1F / automatic safe-framing proof' -ForegroundColor Cyan
Write-Host "[WORKSPACE] $Workspace" -ForegroundColor Green
Write-Host '[PARENT] W1 at reference_image_strength=1.0, retained as the better motion/appearance balance after W1A.' -ForegroundColor Green
Write-Host "[ONE VARIABLE] Driver framing only: contain the entire original raw frame inside a fixed centered $([int]($SafeScale*100))% safe box." -ForegroundColor Yellow
Write-Host '[NO CROP] No person pixels are intentionally cropped; no temporal tracking/camera breathing; no manual alignment.' -ForegroundColor Green
Write-Host '[UNCHANGED] Exilada reference/prompt, Base BF16 stack, 640x800, 37 frames, 16 fps, 20 steps, CFG 1.0, Euler/simple, shift 5.0, seed 0, pose strength 1.0, reference strength 1.0, negative prompt.' -ForegroundColor Green
Write-Host '[PURPOSE] Fix the inherited head/body edge crop before artistic prompt changes or Internet-driver W2.' -ForegroundColor Yellow
Write-Host '[MEMORY] Keep proven --disable-pinned-memory workaround.' -ForegroundColor Yellow
Write-Host ''

# W1F is the first current runner that preprocesses video with OpenCV. The isolated
# ComfyUI environment does not guarantee cv2 as a core dependency, so validate it
# explicitly and install only this small preprocessing dependency if absent.
Write-Host '[PREFLIGHT] Checking automatic video-preprocessing dependencies...' -ForegroundColor Cyan
& $WorkspacePython -c "import cv2, numpy; print('opencv=' + cv2.__version__)"
if ($LASTEXITCODE -ne 0) {
    Write-Host '[PREFLIGHT] OpenCV is absent from the isolated ComfyUI environment; installing opencv-python-headless only.' -ForegroundColor Yellow
    & $WorkspacePython -m pip install --disable-pip-version-check --no-input 'opencv-python-headless>=4.10,<5'
    if ($LASTEXITCODE -ne 0) { Fail 'could not install opencv-python-headless required by the automatic safe-framing preprocessor' }
    & $WorkspacePython -c "import cv2, numpy; print('opencv=' + cv2.__version__)"
    if ($LASTEXITCODE -ne 0) { Fail 'OpenCV installation completed but import still fails' }
}
Write-Host '[PREFLIGHT] Automatic video-preprocessing dependencies: PASS' -ForegroundColor Green

$Base = "http://127.0.0.1:$Port"
$UserDir = Join-Path $ComfyRoot 'user'
New-Item -ItemType Directory -Force -Path $UserDir | Out-Null
$StdoutLog = Join-Path $UserDir "comfyui_${Port}_stdout.log"
$StderrLog = Join-Path $UserDir "comfyui_${Port}_stderr.log"
$PidFile = Join-Path $Workspace '.wan_animate2_spike.pid'
$MainPy = Join-Path $ComfyRoot 'main.py'

$apiRunning = $false
try {
    $null = Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 2
    $apiRunning = $true
} catch {}

if ($apiRunning) {
    if (-not (Test-Path $PidFile -PathType Leaf)) {
        Fail "ComfyUI is already listening on port $Port but no managed PID file exists. Stop that server manually rather than killing an unknown process."
    }
    $oldPidText = (Get-Content -LiteralPath $PidFile -Raw).Trim()
    $oldPid = 0
    if (-not [int]::TryParse($oldPidText, [ref]$oldPid) -or $oldPid -le 0) {
        Fail "invalid managed ComfyUI PID file: $PidFile"
    }
    $oldProcess = Get-Process -Id $oldPid -ErrorAction SilentlyContinue
    if (-not $oldProcess) {
        Fail "port $Port is active but managed PID $oldPid is not running; refusing to stop an unknown server."
    }
    Write-Host "Stopping previous managed ComfyUI PID $oldPid for a clean W1F launch..." -ForegroundColor Yellow
    Stop-Process -Id $oldPid -Force
    for ($i=0; $i -lt 30; $i++) {
        try {
            $null = Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 1
            Start-Sleep -Seconds 1
        } catch { break }
    }
}

$launchArgs = @(
    $MainPy,
    '--listen','127.0.0.1',
    '--port',"$Port",
    '--disable-auto-launch',
    '--disable-pinned-memory'
)

Write-Host 'Starting fresh ComfyUI with pinned memory disabled...' -ForegroundColor Cyan
$process = Start-Process -FilePath $WorkspacePython -ArgumentList $launchArgs -WorkingDirectory $ComfyRoot `
    -RedirectStandardOutput $StdoutLog -RedirectStandardError $StderrLog -WindowStyle Hidden -PassThru
Set-Content -Path $PidFile -Value $process.Id -Encoding ascii
Write-Host "Started PID $($process.Id)" -ForegroundColor Green

$ready = $false
for ($i=0; $i -lt 180; $i++) {
    try {
        $null = Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 2
        $ready = $true
        break
    } catch {
        if ($process.HasExited) {
            if (Test-Path $StderrLog) { Get-Content $StderrLog -Tail 120 }
            Fail "ComfyUI exited early with code $($process.ExitCode)"
        }
        Start-Sleep -Seconds 1
    }
}
if (-not $ready) {
    if (Test-Path $StderrLog) { Get-Content $StderrLog -Tail 120 }
    Fail "ComfyUI API did not become available at $Base"
}

Write-Host 'Preparing fixed safe-contained raw driver and submitting W1F...' -ForegroundColor Cyan
& $WorkspacePython $Executor `
    --workspace $Workspace `
    --comfy-root $ComfyRoot `
    --port $Port `
    --timeout-minutes $TimeoutMinutes `
    --safe-scale $SafeScale
if ($LASTEXITCODE -ne 0) {
    if (Test-Path $StderrLog) {
        Write-Host ''
        Write-Host 'Last ComfyUI stderr lines:' -ForegroundColor DarkYellow
        Get-Content $StderrLog -Tail 160
    }
    Fail "W1F safe-framing inference exited with code $LASTEXITCODE"
}

$Output = Join-Path $Workspace 'w1f_exilada_safe_framing80.mp4'
$Manifest = Join-Path $Workspace 'w1f_run_manifest.json'
$Prompt = Join-Path $Workspace 'w1f_api_prompt.json'
$DriverManifest = Join-Path $Workspace 'w1f_safe_driver_manifest.json'
foreach ($f in @($Output,$Manifest,$Prompt,$DriverManifest)) {
    if (-not (Test-Path $f -PathType Leaf)) { Fail "expected W1F proof file missing after inference: $f" }
}

Write-Host ''
Write-Host 'RUNNER39-WAN-W1F: PASS — SAFE-FRAMING DIAGNOSTIC GENERATED' -ForegroundColor Green
Write-Host "Video:           $Output" -ForegroundColor Cyan
Write-Host "Manifest:        $Manifest" -ForegroundColor Cyan
Write-Host "Prompt:          $Prompt" -ForegroundColor Cyan
Write-Host "Driver manifest: $DriverManifest" -ForegroundColor Cyan
Write-Host ''
Write-Host 'Next gate: compare W1 vs W1F. The test passes only if the complete head/hair/body remains safely inside frame without unacceptable loss of subject scale or motion quality.' -ForegroundColor Yellow
