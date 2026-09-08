param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$Workspace = 'Z:\AI\MiniMaxH3',
    [int]$Port = 8190,
    [int]$TimeoutMinutes = 480
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$AudioVaeName = 'minimax_h3_audio_vae_fp32.safetensors'
$AudioVaeUrl = 'https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_audio_vae_fp32.safetensors'
$AudioVaeSha256 = '8e505d95dd1561d47abd43d4238fd40d9bb1ae9e147ed0a4cba778d76ae4db48'
$AudioVaeBytes = 605254808

function Fail([string]$Message) {
    Write-Host "RUNNER48-H3-H0R: FAIL - $Message" -ForegroundColor Red
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

    Write-Host "Downloading required H3 Ref2VA audio VAE (~605 MB): $Url" -ForegroundColor Cyan
    & $curl.Source '--fail' '--location' '--retry' '5' '--retry-delay' '5' '--retry-all-errors' '--continue-at' '-' '--output' $partial $Url
    if ($LASTEXITCODE -ne 0) { Fail "audio VAE download failed with curl exit code $LASTEXITCODE" }

    Move-Item -LiteralPath $partial -Destination $Destination -Force
    $actual = Get-Sha256 $Destination
    if ($actual -ne $ExpectedSha.ToLowerInvariant()) {
        Remove-Item -LiteralPath $Destination -Force -ErrorAction SilentlyContinue
        Fail "audio VAE SHA256 mismatch. Expected $ExpectedSha, got $actual. Corrupt file deleted."
    }
    $bytes = (Get-Item -LiteralPath $Destination).Length
    if ($bytes -ne $AudioVaeBytes) {
        Fail "audio VAE byte size mismatch after hash verification: expected $AudioVaeBytes, got $bytes"
    }
    Write-Host '  audio VAE verified.' -ForegroundColor Green
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
$Executor = Join-Path $ProjectRepoRoot 'tools\minimax-h3-spike\run_h0_ref2va_audio_vae_required.py'
$Bootstrap = Join-Path $Workspace 'h3_bootstrap_manifest.json'
$DriverManifest = Join-Path $Workspace 'h0_driver_manifest.json'

foreach ($f in @($Python,$MainPy,$Executor,$Bootstrap,$DriverManifest)) {
    if (-not (Test-Path $f -PathType Leaf)) {
        Fail "required H3 H0R file missing: $f. Pull the repository first; Runner46 must already have passed."
    }
}

$bootstrapData = Get-Content -LiteralPath $Bootstrap -Raw | ConvertFrom-Json
if ([string]$bootstrapData.status -ne 'PREPARED') {
    Fail "Runner46 bootstrap status is '$($bootstrapData.status)', expected PREPARED."
}

Write-Host ''
Write-Host 'Roguelite Runner 48 - MiniMax H3 Base Ref2VA H0 / required audio-VAE integration fix' -ForegroundColor Cyan
Write-Host "[WORKSPACE] $Workspace" -ForegroundColor Green
Write-Host '[INCIDENT] Runner47 failed before prompt_id: ComfyUI v0.34.0 validates MiniMaxH3ReferenceToVideo.audio_vae as REQUIRED even when no audio reference is used.' -ForegroundColor Yellow
Write-Host '[CLASSIFICATION] INTEGRATION_FAIL only. No H3 inference occurred; no model-quality evidence was produced.' -ForegroundColor Yellow
Write-Host '[FIX] Download/wire the official 605 MB H3 audio VAE only to satisfy the Ref2VA node schema. H0 still does not use audio reference or audio decode.' -ForegroundColor Green
Write-Host '[UNCHANGED QUALITY SETTINGS] Picture1/Video1, 448x800, 124f@24, ref_image_size=match, Base50, res_multistep/beta, seed0.' -ForegroundColor Green
Write-Host ''

$AudioVaePath = Join-Path $ComfyRoot "models\vae\$AudioVaeName"
Download-Verified $AudioVaeUrl $AudioVaePath $AudioVaeSha256

$Base = "http://127.0.0.1:$Port"
$PidFile = Join-Path $Workspace '.minimax_h3_spike.pid'
$UserDir = Join-Path $ComfyRoot 'user'
New-Item -ItemType Directory -Force -Path $UserDir | Out-Null
$StdoutLog = Join-Path $UserDir "comfyui_h3_${Port}_stdout.log"
$StderrLog = Join-Path $UserDir "comfyui_h3_${Port}_stderr.log"
$ExecutorLog = Join-Path $Workspace 'h0_executor.log'

Stop-ManagedH3 $PidFile 'CLEAN-LAUNCH'
$apiRunning = $false
try {
    $null = Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 2
    $apiRunning = $true
} catch {}
if ($apiRunning) {
    Fail "port $Port is already serving an unmanaged process. Stop it or choose a different port; Runner48 will not kill an unknown server."
}

$launchArgs = @('-s',$MainPy,'--windows-standalone-build','--listen','127.0.0.1','--port',"$Port",'--disable-auto-launch')
Write-Host 'Starting clean pinned ComfyUI v0.34.0 for repaired H3 H0...' -ForegroundColor Cyan
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
            Fail "ComfyUI exited before H0R submission with code $($process.ExitCode)"
        }
        Start-Sleep -Seconds 1
    }
}
if (-not $ready) {
    if (Test-Path $StderrLog) { Get-Content $StderrLog -Tail 180 }
    Stop-ManagedH3 $PidFile 'TIMEOUT-CLEANUP'
    Fail "ComfyUI API did not become ready at $Base"
}

Write-Host 'Submitting repaired H3 H0 Base Ref2VA...' -ForegroundColor Cyan
if (Test-Path $ExecutorLog) { Remove-Item -LiteralPath $ExecutorLog -Force }
& $Python $Executor `
    --workspace $Workspace `
    --comfy-root $ComfyRoot `
    --port $Port `
    --timeout-minutes $TimeoutMinutes 2>&1 | Tee-Object -FilePath $ExecutorLog | ForEach-Object { Write-Host $_ }
$executorExit = $LASTEXITCODE

if ($executorExit -ne 0) {
    Write-Host ''
    Write-Host 'H3 H0R executor diagnostics:' -ForegroundColor Red
    if (Test-Path $ExecutorLog) { Get-Content -LiteralPath $ExecutorLog -Tail 180 }
    Write-Host ''
    Write-Host 'Pinned ComfyUI stderr tail:' -ForegroundColor DarkYellow
    if (Test-Path $StderrLog) { Get-Content -LiteralPath $StderrLog -Tail 200 }
    Write-Host ''
    Write-Host 'Pinned ComfyUI stdout tail:' -ForegroundColor DarkYellow
    if (Test-Path $StdoutLog) { Get-Content -LiteralPath $StdoutLog -Tail 120 }
    Stop-ManagedH3 $PidFile 'FAILURE-CLEANUP'
    Fail "H3 H0R executor exited with code $executorExit. Classify the new exact failure layer; do not call this model-quality evidence unless a prompt_id was issued and generation completed."
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
Write-Host 'RUNNER48-H3-H0R: PASS - INFERENCE COMPLETE / HUMAN QUALITY VERDICT PENDING' -ForegroundColor Green
Write-Host "Video:          $Output" -ForegroundColor Cyan
Write-Host "Manifest:       $Manifest" -ForegroundColor Cyan
Write-Host "Prompt:         $Prompt" -ForegroundColor Cyan
Write-Host "Executor log:   $ExecutorLog" -ForegroundColor Cyan
$GameplayPreview = Join-Path $Workspace 'h0_gameplay_scale_proxy_frame160.mp4'
if (Test-Path $GameplayPreview -PathType Leaf) {
    Write-Host "Gameplay proxy: $GameplayPreview" -ForegroundColor Cyan
}
Write-Host ''
Write-Host 'Review order: full-res topology/identity/motion first, then gameplay proxy. Audio VAE presence is an integration requirement only and does not change the intended video-only H0 task.' -ForegroundColor Yellow
