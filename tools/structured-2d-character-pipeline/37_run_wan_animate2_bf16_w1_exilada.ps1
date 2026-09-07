param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$Workspace = 'Z:\AI\WanAnimate2',
    [int]$Port = 8188,
    [int]$TimeoutMinutes = 240
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "RUNNER37-WAN-W1: FAIL - $Message" -ForegroundColor Red
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

$Executor = Join-Path $ProjectRepoRoot 'tools\wan-animate2-spike\run_w1_from_w0_prompt.py'
$W0Prompt = Join-Path $Workspace 'w0_api_prompt.json'
$W0Manifest = Join-Path $Workspace 'w0_run_manifest.json'
$Route = Join-Path $Workspace 'wan_bf16_route.json'
foreach ($f in @($Executor,$W0Prompt,$W0Manifest,$Route)) {
    if (-not (Test-Path $f -PathType Leaf)) { Fail "required file missing: $f" }
}

$ComfyRoot = Find-ComfyRoot $Workspace
if (-not $ComfyRoot) { Fail "ComfyUI root not found under $Workspace" }
$WorkspacePython = Find-WorkspacePython $Workspace $ComfyRoot
if (-not $WorkspacePython) { Fail "ComfyUI Python environment not found under $Workspace" }
$ExiladaInput = Join-Path $ComfyRoot 'input\exilada_master.png'
if (-not (Test-Path $ExiladaInput -PathType Leaf)) { Fail "Exilada master missing from ComfyUI input: $ExiladaInput" }

$Base = "http://127.0.0.1:$Port"
$UserDir = Join-Path $ComfyRoot 'user'
New-Item -ItemType Directory -Force -Path $UserDir | Out-Null
$StdoutLog = Join-Path $UserDir "comfyui_${Port}_stdout.log"
$StderrLog = Join-Path $UserDir "comfyui_${Port}_stderr.log"
$PidFile = Join-Path $Workspace '.wan_animate2_spike.pid'
$MainPy = Join-Path $ComfyRoot 'main.py'

Write-Host ''
Write-Host 'Roguelite Runner 37 — Wan-Animate-2 Base BF16 W1 / Exilada cross-identity' -ForegroundColor Cyan
Write-Host "[WORKSPACE] $Workspace" -ForegroundColor Green
Write-Host '[W1] Same successful W0 official driver and execution settings.' -ForegroundColor Green
Write-Host '[TARGET] Replace the W0 cat appearance package with exilada_master.png + matching Exilada appearance prompt.' -ForegroundColor Green
Write-Host '[UNCHANGED] Base BF16, UMT5 FP16, CLIP Vision H, Wan VAE BF16, 640x800, 37 frames, 16 fps, 20 steps, CFG 1.0, Euler/simple, shift 5.0, seed 0, strengths 1.0.' -ForegroundColor Green
Write-Host '[NEGATIVE] Preserved unchanged from successful W0.' -ForegroundColor Green
Write-Host '[MEMORY] Keep the proven --disable-pinned-memory runtime workaround.' -ForegroundColor Yellow
Write-Host '[PURPOSE] Test cross-identity motion transfer + Exilada appearance/style preservation before Internet-driver tests.' -ForegroundColor Yellow
Write-Host ''

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
    Write-Host "Stopping previous managed ComfyUI PID $oldPid for a clean W1 launch..." -ForegroundColor Yellow
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

Write-Host 'Submitting W1 derived from the exact successful W0 API prompt...' -ForegroundColor Cyan
& $WorkspacePython $Executor `
    --workspace $Workspace `
    --comfy-root $ComfyRoot `
    --port $Port `
    --timeout-minutes $TimeoutMinutes
if ($LASTEXITCODE -ne 0) {
    if (Test-Path $StderrLog) {
        Write-Host ''
        Write-Host 'Last ComfyUI stderr lines:' -ForegroundColor DarkYellow
        Get-Content $StderrLog -Tail 160
    }
    Fail "W1 Exilada inference exited with code $LASTEXITCODE"
}

$Output = Join-Path $Workspace 'w1_exilada_official_driver.mp4'
$Manifest = Join-Path $Workspace 'w1_run_manifest.json'
$Prompt = Join-Path $Workspace 'w1_api_prompt.json'
foreach ($f in @($Output,$Manifest,$Prompt)) {
    if (-not (Test-Path $f -PathType Leaf)) { Fail "expected W1 proof file missing after inference: $f" }
}

Write-Host ''
Write-Host 'RUNNER37-WAN-W1: PASS — EXILADA / OFFICIAL DRIVER GENERATED' -ForegroundColor Green
Write-Host "Video:    $Output" -ForegroundColor Cyan
Write-Host "Manifest: $Manifest" -ForegroundColor Cyan
Write-Host "Prompt:   $Prompt" -ForegroundColor Cyan
Write-Host ''
Write-Host 'Next gate: visual W1 diagnosis. Judge identity, complete initial-state preservation, pixel/game-art language, motion adherence, topology, hair/cloth/restraints and driver leakage before W2.' -ForegroundColor Yellow
