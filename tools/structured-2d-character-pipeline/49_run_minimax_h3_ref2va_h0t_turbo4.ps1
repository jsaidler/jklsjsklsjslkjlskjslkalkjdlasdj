param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$Workspace = 'Z:\AI\MiniMaxH3',
    [int]$Port = 8190,
    [int]$TimeoutMinutes = 180
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$TurboName = 'minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors'
$TurboUrl = 'https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/loras/minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors'
$TurboSha256 = '5b9ab5ade15d0775676d01a907268a69a1468dc6033b3b0d3ded5502f3ebb84c'

function Fail([string]$Message) {
    Write-Host "RUNNER49-H3-H0T: FAIL - $Message" -ForegroundColor Red
    exit 1
}

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Download-Verified([string]$Url, [string]$Destination, [string]$ExpectedSha) {
    $parent = Split-Path -Parent $Destination
    New-Item -ItemType Directory -Force -Path $parent | Out-Null

    if (Test-Path $Destination -PathType Leaf) {
        Write-Host "Hash-checking existing: $Destination" -ForegroundColor DarkCyan
        $existingHash = Get-Sha256 $Destination
        if ($existingHash -eq $ExpectedSha.ToLowerInvariant()) {
            Write-Host '  already present and verified.' -ForegroundColor Green
            return
        }
        Write-Host '  existing file hash is wrong; deleting it.' -ForegroundColor Yellow
        Remove-Item -LiteralPath $Destination -Force
    }

    $partial = "$Destination.part"
    $curl = Get-Command curl.exe -ErrorAction SilentlyContinue
    if (-not $curl) { Fail 'curl.exe is required for resumable verified downloads.' }

    Write-Host "Downloading official H3 Ref2V Turbo4 LoRA (~1.96 GB): $Url" -ForegroundColor Cyan
    & $curl.Source '--fail' '--location' '--retry' '5' '--retry-delay' '5' '--retry-all-errors' '--continue-at' '-' '--output' $partial $Url
    if ($LASTEXITCODE -ne 0) { Fail "Turbo4 LoRA download failed with curl exit code $LASTEXITCODE" }

    Move-Item -LiteralPath $partial -Destination $Destination -Force
    $actual = Get-Sha256 $Destination
    if ($actual -ne $ExpectedSha.ToLowerInvariant()) {
        Remove-Item -LiteralPath $Destination -Force -ErrorAction SilentlyContinue
        Fail "Turbo4 LoRA SHA256 mismatch. Expected $ExpectedSha, got $actual. Corrupt file deleted."
    }
    Write-Host '  Turbo4 LoRA verified.' -ForegroundColor Green
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
$Executor = Join-Path $ProjectRepoRoot 'tools\minimax-h3-spike\run_h0t_ref2va_turbo4.py'
$H0Manifest = Join-Path $Workspace 'h0_run_manifest.json'
$H0Video = Join-Path $Workspace 'h0_exilada_ref2va_448x800_124f_base50.mp4'

foreach ($f in @($Python,$MainPy,$Executor,$H0Manifest,$H0Video)) {
    if (-not (Test-Path $f -PathType Leaf)) {
        Fail "required H0T prerequisite missing: $f"
    }
}

$h0 = Get-Content -LiteralPath $H0Manifest -Raw | ConvertFrom-Json
if ([string]$h0.status -ne 'INFERENCE_COMPLETE') {
    Fail "H0 manifest status is '$($h0.status)', expected INFERENCE_COMPLETE."
}

Write-Host ''
Write-Host 'Roguelite Runner 49 - MiniMax H3 Ref2VA H0T / official Turbo4 throughput-quality gate' -ForegroundColor Cyan
Write-Host "[WORKSPACE] $Workspace" -ForegroundColor Green
Write-Host '[PARENT] Exact completed H0 inputs/geometry/prompt/seed.' -ForegroundColor Green
Write-Host '[TURBO] Official Ref2V Turbo4 LoRA, strength 1.0, 4 steps, res_multistep/simple.' -ForegroundColor Green
Write-Host '[UNCHANGED] Picture1, Video1, 448x800, 124f@24, ref_image_size=match, seed0.' -ForegroundColor Green
Write-Host '[PURPOSE] Determine whether H3 can become a practical per-action production tool before running a new walk driver.' -ForegroundColor Yellow
Write-Host '[PIXEL ART] This still generates a motion master. Final runtime pixel-art reconstruction is a separate stage.' -ForegroundColor Yellow
Write-Host ''

$TurboPath = Join-Path $ComfyRoot "models\loras\$TurboName"
Download-Verified $TurboUrl $TurboPath $TurboSha256

$Base = "http://127.0.0.1:$Port"
$PidFile = Join-Path $Workspace '.minimax_h3_spike.pid'
$UserDir = Join-Path $ComfyRoot 'user'
New-Item -ItemType Directory -Force -Path $UserDir | Out-Null
$StdoutLog = Join-Path $UserDir "comfyui_h3_${Port}_stdout.log"
$StderrLog = Join-Path $UserDir "comfyui_h3_${Port}_stderr.log"
$ExecutorLog = Join-Path $Workspace 'h0t_executor.log'

Stop-ManagedH3 $PidFile 'CLEAN-LAUNCH'
$apiRunning = $false
try {
    $null = Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 2
    $apiRunning = $true
} catch {}
if ($apiRunning) {
    Fail "port $Port is already serving an unmanaged process. Stop it or choose another port."
}

$launchArgs = @('-s',$MainPy,'--windows-standalone-build','--listen','127.0.0.1','--port',"$Port",'--disable-auto-launch')
Write-Host 'Starting clean pinned ComfyUI v0.34.0 for H0T...' -ForegroundColor Cyan
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
            if (Test-Path $StderrLog) { Get-Content $StderrLog -Tail 180 }
            Fail "ComfyUI exited before H0T submission with code $($process.ExitCode)"
        }
        Start-Sleep -Seconds 1
    }
}
if (-not $ready) {
    if (Test-Path $StderrLog) { Get-Content $StderrLog -Tail 180 }
    Stop-ManagedH3 $PidFile 'TIMEOUT-CLEANUP'
    Fail "ComfyUI API did not become ready at $Base"
}

Write-Host 'Submitting H3 H0T Turbo4...' -ForegroundColor Cyan
if (Test-Path $ExecutorLog) { Remove-Item -LiteralPath $ExecutorLog -Force }
& $Python $Executor `
    --workspace $Workspace `
    --comfy-root $ComfyRoot `
    --port $Port `
    --timeout-minutes $TimeoutMinutes 2>&1 | Tee-Object -FilePath $ExecutorLog | ForEach-Object { Write-Host $_ }
$executorExit = $LASTEXITCODE

if ($executorExit -ne 0) {
    Write-Host ''
    Write-Host 'H3 H0T executor diagnostics:' -ForegroundColor Red
    if (Test-Path $ExecutorLog) { Get-Content -LiteralPath $ExecutorLog -Tail 180 }
    Write-Host ''
    Write-Host 'Pinned ComfyUI stderr tail:' -ForegroundColor DarkYellow
    if (Test-Path $StderrLog) { Get-Content -LiteralPath $StderrLog -Tail 200 }
    Write-Host ''
    Write-Host 'Pinned ComfyUI stdout tail:' -ForegroundColor DarkYellow
    if (Test-Path $StdoutLog) { Get-Content -LiteralPath $StdoutLog -Tail 120 }
    Stop-ManagedH3 $PidFile 'FAILURE-CLEANUP'
    Fail "H0T executor exited with code $executorExit. Classify the exact failure layer before changing settings."
}

$Output = Join-Path $Workspace 'h0t_exilada_ref2va_448x800_124f_turbo4.mp4'
$Manifest = Join-Path $Workspace 'h0t_run_manifest.json'
$Prompt = Join-Path $Workspace 'h0t_api_prompt.json'
foreach ($f in @($Output,$Manifest,$Prompt)) {
    if (-not (Test-Path $f -PathType Leaf)) {
        Stop-ManagedH3 $PidFile 'OUTPUT-FAIL-CLEANUP'
        Fail "expected H0T proof file missing: $f"
    }
}

Stop-ManagedH3 $PidFile 'PASS-CLEANUP'

Write-Host ''
Write-Host 'RUNNER49-H3-H0T: PASS - TURBO4 INFERENCE COMPLETE / QUALITY COMPARISON PENDING' -ForegroundColor Green
Write-Host "Video:        $Output" -ForegroundColor Cyan
Write-Host "Manifest:     $Manifest" -ForegroundColor Cyan
Write-Host "Prompt:       $Prompt" -ForegroundColor Cyan
Write-Host "Executor log: $ExecutorLog" -ForegroundColor Cyan
Write-Host ''
Write-Host 'Compare H0T directly against H0. Do not use Turbo for H1-S until topology/identity/motion quality is accepted.' -ForegroundColor Yellow
