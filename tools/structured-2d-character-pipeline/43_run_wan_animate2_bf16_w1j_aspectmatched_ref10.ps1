param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$Workspace = 'Z:\AI\WanAnimate2',
    [int]$Port = 8188,
    [int]$TimeoutMinutes = 240
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "RUNNER43-WAN-W1J: FAIL - $Message" -ForegroundColor Red
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

$Executor = Join-Path $ProjectRepoRoot 'tools\wan-animate2-spike\run_w1j_ref10_aspectmatched.py'
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
Write-Host 'Roguelite Runner 43 - Wan-Animate-2 Base BF16 W1J / W1H aspect-matched branch / reference strength 1.0' -ForegroundColor Cyan
Write-Host "[WORKSPACE] $Workspace" -ForegroundColor Green
Write-Host '[PARENT] Exact completed W1H: untouched raw driver, 512x912 aspect-matched canvas, pose_end_percent=1.0, reference_image_strength=1.5.' -ForegroundColor Green
Write-Host '[W1I VERDICT] pose_end_percent 0.70 produced no material perceptual blur improvement; high-motion blur remained and the output stayed extremely close to W1H.' -ForegroundColor Yellow
Write-Host '[ONE VARIABLE FROM W1H] reference_image_strength 1.5 -> 1.0.' -ForegroundColor Yellow
Write-Host '[WHY] Earlier 640x800 tests made 1.0 look cleaner but structurally weaker. W1H proved that 640x800 discarded ~29.7% of vertical driver conditioning, so ref=1.0 must be retested on the corrected 512x912 geometry.' -ForegroundColor Yellow
Write-Host '[UNCHANGED] Original raw driver, 512x912 geometry, Exilada reference/prompt, BF16 stack, 37 frames, 16 fps, 20 steps, CFG 1.0, Euler/simple, shift 5.0, seed 0, pose strength 1.0, pose start 0.0, pose end 1.0, CLIP pose branch, negative prompt.' -ForegroundColor Green
Write-Host '[MEMORY] Keep proven --disable-pinned-memory workaround.' -ForegroundColor Yellow
Write-Host ''

$Base = "http://127.0.0.1:$Port"
$UserDir = Join-Path $ComfyRoot 'user'
New-Item -ItemType Directory -Force -Path $UserDir | Out-Null
$StdoutLog = Join-Path $UserDir "comfyui_${Port}_stdout.log"
$StderrLog = Join-Path $UserDir "comfyui_${Port}_stderr.log"
$ExecutorLog = Join-Path $Workspace 'w1j_executor.log'
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
    Write-Host "Stopping previous managed ComfyUI PID $oldPid for a clean W1J launch..." -ForegroundColor Yellow
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

Write-Host 'Submitting W1J: exact W1H geometry/motion branch with reference strength lowered to 1.0...' -ForegroundColor Cyan
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
    Write-Host 'W1J executor diagnostics:' -ForegroundColor Red
    if (Test-Path $ExecutorLog) { Get-Content -LiteralPath $ExecutorLog -Tail 120 }
    Write-Host ''
    Write-Host 'ComfyUI stderr tail (secondary context only):' -ForegroundColor DarkYellow
    if (Test-Path $StderrLog) { Get-Content $StderrLog -Tail 80 }
    Fail "W1J inference exited with code $executorExit"
}

$Output = Join-Path $Workspace 'w1j_exilada_aspectmatched_ref10.mp4'
$Manifest = Join-Path $Workspace 'w1j_run_manifest.json'
$Prompt = Join-Path $Workspace 'w1j_api_prompt.json'
foreach ($f in @($Output,$Manifest,$Prompt)) {
    if (-not (Test-Path $f -PathType Leaf)) { Fail "expected W1J proof file missing after inference: $f" }
}

Write-Host ''
Write-Host 'RUNNER43-WAN-W1J: PASS - ASPECT-MATCHED REF-1.0 DIAGNOSTIC GENERATED' -ForegroundColor Green
Write-Host "Video:        $Output" -ForegroundColor Cyan
Write-Host "Manifest:     $Manifest" -ForegroundColor Cyan
Write-Host "Prompt:       $Prompt" -ForegroundColor Cyan
Write-Host "Executor log: $ExecutorLog" -ForegroundColor Cyan
Write-Host ''
Write-Host 'Next gate: compare W1H ref1.5 vs W1J ref1.0 frame-by-frame. Prefer 1.0 only if blur/ghosting improves materially without reintroducing missing or displaced body parts/topology.' -ForegroundColor Yellow
