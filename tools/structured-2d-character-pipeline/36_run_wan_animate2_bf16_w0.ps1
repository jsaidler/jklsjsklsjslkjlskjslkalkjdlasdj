param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$Workspace = 'Z:\AI\WanAnimate2',
    [int]$Port = 8188,
    [int]$TimeoutMinutes = 240
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "RUNNER36-WAN-W0: FAIL - $Message" -ForegroundColor Red
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

$Builder = Join-Path $ProjectRepoRoot 'tools\wan-animate2-spike\build_and_run_w0.py'
$Schema = Join-Path $Workspace 'object_info_wan_bf16.json'
$Route = Join-Path $Workspace 'wan_bf16_route.json'
foreach ($f in @($Builder,$Schema,$Route)) {
    if (-not (Test-Path $f -PathType Leaf)) { Fail "required file missing: $f" }
}

$ComfyRoot = Find-ComfyRoot $Workspace
if (-not $ComfyRoot) { Fail "ComfyUI root not found under $Workspace" }
$WorkspacePython = Find-WorkspacePython $Workspace $ComfyRoot
if (-not $WorkspacePython) { Fail "ComfyUI Python environment not found under $Workspace" }

Write-Host ''
Write-Host 'Roguelite Runner 36 — Wan-Animate-2 Base BF16 official W0 inference' -ForegroundColor Cyan
Write-Host "[WORKSPACE] $Workspace" -ForegroundColor Green
Write-Host "[COMFY]     $ComfyRoot" -ForegroundColor Green
Write-Host '[W0] Official upstream demo1 reference + template video.' -ForegroundColor Green
Write-Host '[MODEL] wan_animate_2_bf16.safetensors + UMT5 FP16 + CLIP Vision H + Wan VAE BF16.' -ForegroundColor Green
Write-Host '[SETTINGS] 640x800, 37 frames, 16 fps, 20 steps, CFG 1.0/no CFG, Euler/simple, shift 5.0, seed 0.' -ForegroundColor Green
Write-Host '[SCHEMA] Workflow is built from the exact live installed ComfyUI schema; no stale widget assumptions.' -ForegroundColor Green
Write-Host '[STOP] This is W0 only. It does not use exilada_master.png yet.' -ForegroundColor Yellow
Write-Host ''

$Base = "http://127.0.0.1:$Port"
$serverAlreadyRunning = $false
try {
    $null = Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 2
    $serverAlreadyRunning = $true
} catch {}

$process = $null
if ($serverAlreadyRunning) {
    Write-Host "ComfyUI API already running at $Base" -ForegroundColor Green
} else {
    $UserDir = Join-Path $ComfyRoot 'user'
    New-Item -ItemType Directory -Force -Path $UserDir | Out-Null
    $StdoutLog = Join-Path $UserDir "comfyui_${Port}_stdout.log"
    $StderrLog = Join-Path $UserDir "comfyui_${Port}_stderr.log"
    $PidFile = Join-Path $Workspace '.wan_animate2_spike.pid'
    $MainPy = Join-Path $ComfyRoot 'main.py'
    $launchArgs = @($MainPy,'--listen','127.0.0.1','--port',"$Port",'--disable-auto-launch')

    Write-Host 'Starting ComfyUI with the canonical workspace Python...' -ForegroundColor Cyan
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
}

Write-Host 'Submitting W0 through schema-driven API workflow...' -ForegroundColor Cyan
& $WorkspacePython $Builder `
    --workspace $Workspace `
    --comfy-root $ComfyRoot `
    --port $Port `
    --timeout-minutes $TimeoutMinutes
if ($LASTEXITCODE -ne 0) {
    $stderrLog = Join-Path (Join-Path $ComfyRoot 'user') "comfyui_${Port}_stderr.log"
    if (Test-Path $stderrLog) {
        Write-Host ''
        Write-Host 'Last ComfyUI stderr lines:' -ForegroundColor DarkYellow
        Get-Content $stderrLog -Tail 120
    }
    Fail "official W0 inference exited with code $LASTEXITCODE"
}

$Output = Join-Path $Workspace 'w0_official_baseline.mp4'
$Manifest = Join-Path $Workspace 'w0_run_manifest.json'
foreach ($f in @($Output,$Manifest)) {
    if (-not (Test-Path $f -PathType Leaf)) { Fail "expected W0 proof file missing after inference: $f" }
}

Write-Host ''
Write-Host 'RUNNER36-WAN-W0: PASS — OFFICIAL BF16 BASELINE GENERATED' -ForegroundColor Green
Write-Host "Video:    $Output" -ForegroundColor Cyan
Write-Host "Manifest: $Manifest" -ForegroundColor Cyan
Write-Host ''
Write-Host 'Next gate: visually judge W0. Only if motion transfer is credible do we run W1 with the Exilada master.' -ForegroundColor Yellow
