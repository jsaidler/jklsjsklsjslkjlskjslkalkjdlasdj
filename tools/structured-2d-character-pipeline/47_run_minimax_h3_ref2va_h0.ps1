param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$Workspace = 'Z:\AI\MiniMaxH3',
    [int]$Port = 8190,
    [int]$TimeoutMinutes = 480
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "RUNNER47-H3-H0: FAIL - $Message" -ForegroundColor Red
    exit 1
}

function Stop-ManagedH3([string]$PidFile, [string]$Label) {
    if (-not (Test-Path $PidFile -PathType Leaf)) { return }
    $pidText = (Get-Content -LiteralPath $PidFile -Raw).Trim()
    $managedPid = 0
    if (-not [int]::TryParse($pidText, [ref]$managedPid) -or $managedPid -le 0) {
        Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue
        return
    }
    $p = Get-Process -Id $managedPid -ErrorAction SilentlyContinue
    if ($p) {
        Write-Host "[$Label] stopping managed H3 ComfyUI PID $managedPid." -ForegroundColor Yellow
        Stop-Process -Id $managedPid -Force
        Start-Sleep -Seconds 2
    }
    Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue
}

$PortableRoot = Join-Path $Workspace 'ComfyUI_windows_portable'
$ComfyRoot = Join-Path $PortableRoot 'ComfyUI'
$Python = Join-Path $PortableRoot 'python_embeded\python.exe'
$MainPy = Join-Path $ComfyRoot 'main.py'
$Executor = Join-Path $ProjectRepoRoot 'tools\minimax-h3-spike\run_h0_ref2va.py'
$Bootstrap = Join-Path $Workspace 'h3_bootstrap_manifest.json'
$DriverManifest = Join-Path $Workspace 'h0_driver_manifest.json'

foreach ($f in @($Python,$MainPy,$Executor,$Bootstrap,$DriverManifest)) {
    if (-not (Test-Path $f -PathType Leaf)) {
        Fail "required H3 H0 file missing: $f. Run Runner46 first."
    }
}

$bootstrapData = Get-Content -LiteralPath $Bootstrap -Raw | ConvertFrom-Json
if ([string]$bootstrapData.status -ne 'PREPARED') {
    Fail "Runner46 bootstrap status is '$($bootstrapData.status)', expected PREPARED."
}

Write-Host ''
Write-Host 'Roguelite Runner 47 - MiniMax H3 Base Ref2VA H0' -ForegroundColor Cyan
Write-Host "[WORKSPACE] $Workspace" -ForegroundColor Green
Write-Host '[CONTRACT] Picture1 = Exilada appearance/identity; Video1 = motion/performance only.' -ForegroundColor Green
Write-Host '[H0] 448x800 / 124 frames / 24 fps / ref_image_size=match / Base 50 steps / res_multistep + beta / seed0.' -ForegroundColor Green
Write-Host '[MODEL SET] Ref2VA pruned INT8 ConvRot + Qwen3-VL NVFP4 AWQ + video VAE. No FL2VA/Turbo/embedding/audio-VAE.' -ForegroundColor Green
Write-Host '[MEMORY] Pinned ComfyUI v0.34.0 starts with its default DynamicVRAM behavior. No Wan memory flags are inherited.' -ForegroundColor Yellow
Write-Host '[VERDICT] A successful inference is not automatically a model PASS; full-res topology and gameplay-scale QA are reviewed afterward.' -ForegroundColor Yellow
Write-Host ''

$Base = "http://127.0.0.1:$Port"
$PidFile = Join-Path $Workspace '.minimax_h3_spike.pid'
$UserDir = Join-Path $ComfyRoot 'user'
New-Item -ItemType Directory -Force -Path $UserDir | Out-Null
$StdoutLog = Join-Path $UserDir "comfyui_h3_${Port}_stdout.log"
$StderrLog = Join-Path $UserDir "comfyui_h3_${Port}_stderr.log"
$ExecutorLog = Join-Path $Workspace 'h0_executor.log'

Stop-ManagedH3 $PidFile 'CLEAN-LAUNCH'
try {
    $null = Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 2
    Fail "port $Port is already serving an unmanaged process. Stop it or choose a different port; Runner47 will not kill an unknown server."
} catch {
    # Expected when the port is free. Fail() uses exit, so a live unmanaged server never reaches here.
}

$launchArgs = @('-s',$MainPy,'--windows-standalone-build','--listen','127.0.0.1','--port',"$Port",'--disable-auto-launch')
Write-Host 'Starting clean pinned ComfyUI v0.34.0 for H3 H0...' -ForegroundColor Cyan
$process = Start-Process -FilePath $Python -ArgumentList $launchArgs -WorkingDirectory $ComfyRoot `
    -RedirectStandardOutput $StdoutLog -RedirectStandardError $StderrLog -WindowStyle Hidden -PassThru
Set-Content -LiteralPath $PidFile -Value $process.Id -Encoding ASCII
Write-Host "Started H3 ComfyUI PID $($process.Id)" -ForegroundColor Green

$ready = $false
for ($i=0; $i -lt 300; $i++) {
    try {
        $null = Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 2
        $ready = $true
        break
    } catch {
        if ($process.HasExited) {
            Write-Host 'ComfyUI stderr:' -ForegroundColor Red
            if (Test-Path $StderrLog) { Get-Content $StderrLog -Tail 180 }
            Fail "ComfyUI exited before H0 submission with code $($process.ExitCode)"
        }
        Start-Sleep -Seconds 1
    }
}
if (-not $ready) {
    if (Test-Path $StderrLog) { Get-Content $StderrLog -Tail 180 }
    Stop-ManagedH3 $PidFile 'TIMEOUT-CLEANUP'
    Fail "ComfyUI API did not become ready at $Base"
}

Write-Host 'Submitting H3 H0 Base Ref2VA...' -ForegroundColor Cyan
if (Test-Path $ExecutorLog) { Remove-Item -LiteralPath $ExecutorLog -Force }
$executorOutput = & $Python $Executor `
    --workspace $Workspace `
    --comfy-root $ComfyRoot `
    --port $Port `
    --timeout-minutes $TimeoutMinutes 2>&1
$executorOutput | Tee-Object -FilePath $ExecutorLog | ForEach-Object { Write-Host $_ }
$executorExit = $LASTEXITCODE

if ($executorExit -ne 0) {
    Write-Host ''
    Write-Host 'H3 H0 executor diagnostics:' -ForegroundColor Red
    if (Test-Path $ExecutorLog) { Get-Content -LiteralPath $ExecutorLog -Tail 160 }
    Write-Host ''
    Write-Host 'Pinned ComfyUI stderr tail:' -ForegroundColor DarkYellow
    if (Test-Path $StderrLog) { Get-Content -LiteralPath $StderrLog -Tail 180 }
    Write-Host ''
    Write-Host 'Pinned ComfyUI stdout tail:' -ForegroundColor DarkYellow
    if (Test-Path $StdoutLog) { Get-Content -LiteralPath $StdoutLog -Tail 100 }
    Stop-ManagedH3 $PidFile 'FAILURE-CLEANUP'
    Fail "H3 H0 executor exited with code $executorExit. This is not a model-quality verdict until the exact failure layer is classified."
}

$Output = Join-Path $Workspace 'h0_exilada_ref2va_448x800_124f_base50.mp4'
$Manifest = Join-Path $Workspace 'h0_run_manifest.json'
$Prompt = Join-Path $Workspace 'h0_api_prompt.json'
foreach ($f in @($Output,$Manifest,$Prompt)) {
    if (-not (Test-Path $f -PathType Leaf)) {
        Stop-ManagedH3 $PidFile 'OUTPUT-FAIL-CLEANUP'
        Fail "expected H0 proof file missing after completed executor: $f"
    }
}

Stop-ManagedH3 $PidFile 'PASS-CLEANUP'

Write-Host ''
Write-Host 'RUNNER47-H3-H0: PASS - INFERENCE COMPLETE / HUMAN QUALITY VERDICT PENDING' -ForegroundColor Green
Write-Host "Video:          $Output" -ForegroundColor Cyan
Write-Host "Manifest:       $Manifest" -ForegroundColor Cyan
Write-Host "Prompt:         $Prompt" -ForegroundColor Cyan
Write-Host "Executor log:   $ExecutorLog" -ForegroundColor Cyan
$GameplayPreview = Join-Path $Workspace 'h0_gameplay_scale_proxy_frame160.mp4'
if (Test-Path $GameplayPreview -PathType Leaf) {
    Write-Host "Gameplay proxy: $GameplayPreview" -ForegroundColor Cyan
}
Write-Host ''
Write-Host 'Review order: (1) full-res anatomy/topology/identity/motion; (2) tiny gameplay proxy. Do not call H0 a model PASS merely because inference completed.' -ForegroundColor Yellow
