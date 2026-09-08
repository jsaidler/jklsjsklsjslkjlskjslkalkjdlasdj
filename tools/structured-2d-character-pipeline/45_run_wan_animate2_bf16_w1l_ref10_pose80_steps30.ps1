param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$Workspace = 'Z:\AI\WanAnimate2',
    [int]$Port = 8188,
    [int]$TimeoutMinutes = 240
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "RUNNER45-WAN-W1L: FAIL - $Message" -ForegroundColor Red
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

$Executor = Join-Path $ProjectRepoRoot 'tools\wan-animate2-spike\run_w1l_ref10_pose80_steps30.py'
$W1HPrompt = Join-Path $Workspace 'w1h_api_prompt.json'
$W1HManifest = Join-Path $Workspace 'w1h_run_manifest.json'
foreach ($f in @($Executor,$W1HPrompt,$W1HManifest)) {
    if (-not (Test-Path $f -PathType Leaf)) { Fail "required file missing: $f" }
}

$ComfyRoot = Find-ComfyRoot $Workspace
if (-not $ComfyRoot) { Fail "ComfyUI root not found under $Workspace" }
$WorkspacePython = Find-WorkspacePython $Workspace $ComfyRoot
if (-not $WorkspacePython) { Fail "ComfyUI Python environment not found under $Workspace" }

Write-Host ''
Write-Host 'Roguelite Runner 45 - Wan-Animate-2 Base BF16 W1L / compound quality test' -ForegroundColor Cyan
Write-Host "[WORKSPACE] $Workspace" -ForegroundColor Green
Write-Host '[PARENT] Exact completed W1H: untouched raw driver, 512x912, pose window 0.0-1.0, ref1.5, pose1.0, 20 steps.' -ForegroundColor Green
Write-Host '[W1I VERDICT] pose_end_percent 0.70 did not materially improve blur or structural stability.' -ForegroundColor Yellow
Write-Host '[SUPERSEDED BEFORE RUN] Runner43/W1J and Runner44/W1K are retained as small prepared tooling but are not the current gate.' -ForegroundColor Yellow
Write-Host '[COMPOUND CHANGES FROM W1H] reference_image_strength 1.5 -> 1.0; pose_strength 1.0 -> 0.80; steps 20 -> 30.' -ForegroundColor Yellow
Write-Host '[POLICY] This is deliberately NOT a one-variable causal test. It searches for a better operating point against heavy motion blur plus structural deformation.' -ForegroundColor Yellow
Write-Host '[UNCHANGED] Raw driver, 512x912 geometry, Exilada reference/prompt, BF16 stack, 37 frames, 16 fps, CFG 1.0, Euler/simple, shift 5.0, seed 0, pose start 0.0, pose end 1.0, CLIP pose branch, negative prompt.' -ForegroundColor Green
Write-Host '[MEMORY] Keep proven --disable-pinned-memory workaround.' -ForegroundColor Yellow
Write-Host ''

$Base = "http://127.0.0.1:$Port"
$UserDir = Join-Path $ComfyRoot 'user'
New-Item -ItemType Directory -Force -Path $UserDir | Out-Null
$StdoutLog = Join-Path $UserDir "comfyui_${Port}_stdout.log"
$StderrLog = Join-Path $UserDir "comfyui_${Port}_stderr.log"
$ExecutorLog = Join-Path $Workspace 'w1l_executor.log'
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
    Write-Host "Stopping previous managed ComfyUI PID $oldPid for a clean W1L launch..." -ForegroundColor Yellow
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

Write-Host 'Submitting W1L: ref1.0 + pose0.80 + 30 steps on exact W1H geometry/raw-driver branch...' -ForegroundColor Cyan
if (Test-Path $ExecutorLog) { Remove-Item -LiteralPath $ExecutorLog -Force }
$executorOutput = & $WorkspacePython $Executor `
    --workspace $Workspace `
    --comfy-root $ComfyRoot `
    --port $Port `
    --timeout-minutes $TimeoutMinutes 2>&1
$executorOutput | Tee-Object -FilePath $ExecutorLog | ForEach-Object { Write-Host $_ }
$executorExit = $LASTEXITCODE
if ($executorExit -ne 0) {
    Write-Host ''
    Write-Host 'W1L executor diagnostics:' -ForegroundColor Red
    if (Test-Path $ExecutorLog) { Get-Content -LiteralPath $ExecutorLog -Tail 120 }
    Write-Host ''
    Write-Host 'ComfyUI stderr tail (secondary context only):' -ForegroundColor DarkYellow
    if (Test-Path $StderrLog) { Get-Content $StderrLog -Tail 80 }
    Fail "W1L inference exited with code $executorExit"
}

$Output = Join-Path $Workspace 'w1l_exilada_aspectmatched_ref10_pose80_steps30.mp4'
$Manifest = Join-Path $Workspace 'w1l_run_manifest.json'
$Prompt = Join-Path $Workspace 'w1l_api_prompt.json'
foreach ($f in @($Output,$Manifest,$Prompt)) {
    if (-not (Test-Path $f -PathType Leaf)) { Fail "expected W1L proof file missing after inference: $f" }
}

Write-Host ''
Write-Host 'RUNNER45-WAN-W1L: PASS - COMPOUND QUALITY DIAGNOSTIC GENERATED' -ForegroundColor Green
Write-Host "Video:        $Output" -ForegroundColor Cyan
Write-Host "Manifest:     $Manifest" -ForegroundColor Cyan
Write-Host "Prompt:       $Prompt" -ForegroundColor Cyan
Write-Host "Executor log: $ExecutorLog" -ForegroundColor Cyan
Write-Host ''
Write-Host 'Next gate: compare W1H vs W1L. W1L wins only if heavy motion blur AND structural changes fall materially while choreography, identity, long-hair/cloth dynamics and framing remain acceptable.' -ForegroundColor Yellow
