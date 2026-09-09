param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$H3Workspace = 'Z:\AI\MiniMaxH3',
    [string]$Workspace = 'Z:\AI\FluxKontext',
    [int]$Port = 8191,
    [int]$TimeoutMinutes = 180
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$KontextName = 'flux1-dev-kontext_fp8_scaled.safetensors'
$KontextSha256 = '630ba795ec64283b4230ea23cf79406c2c68b7c578229ed139f30043eadb30a2'
$ClipName = 'clip_l.safetensors'
$ClipSha256 = '660c6f5b1abae9dc498ac2d21e1347d2abdb0cf6c0c0c8576cd796491d9a6cdd'
$T5Name = 't5xxl_fp16.safetensors'
$T5Sha256 = '6e480b09fae049a72d2a8c5fbccb8d3e92febeb233bbe9dfe7256958a9167635'
$VaeName = 'ae.safetensors'
$VaeSha256 = 'afc8e28272cd15db3919bacdb6918ce9c1ed22e96cb12c4d5ed0fba823529e38'

$LoraName = 'ume_modern_pixelart.safetensors'
$LoraUrl = 'https://huggingface.co/UmeAiRT/FLUX.1-dev-LoRA-Modern_Pixel_art/resolve/main/ume_modern_pixelart.safetensors'
$LoraSha256 = 'ed226c149dca6286ae345b6900d807f791a52b1746ed8f524af41efdfda6f0a4'

function Fail([string]$Message) {
    Write-Host "RUNNER53-KONTEXT-PIXELART-LORA: FAIL - $Message" -ForegroundColor Red
    exit 1
}

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Require-Hash([string]$Path, [string]$Expected, [string]$Label) {
    if (-not (Test-Path $Path -PathType Leaf)) { Fail "required $Label missing: $Path" }
    $actual = Get-Sha256 $Path
    if ($actual -ne $Expected.ToLowerInvariant()) { Fail "$Label SHA256 mismatch. Expected $Expected, got $actual" }
    Write-Host "  $Label verified." -ForegroundColor Green
}

function Download-Verified([string]$Url, [string]$Destination, [string]$ExpectedSha, [string]$Label) {
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Destination) | Out-Null
    if (Test-Path $Destination -PathType Leaf) {
        $actual = Get-Sha256 $Destination
        if ($actual -eq $ExpectedSha.ToLowerInvariant()) {
            Write-Host "  $Label already present and verified." -ForegroundColor Green
            return
        }
        Remove-Item -LiteralPath $Destination -Force
    }
    $partial = "$Destination.part"
    $curl = Get-Command curl.exe -ErrorAction SilentlyContinue
    if (-not $curl) { Fail 'curl.exe is required.' }
    Write-Host "Downloading ${Label}: $Url" -ForegroundColor Cyan
    & $curl.Source '--fail' '--location' '--retry' '5' '--retry-delay' '5' '--retry-all-errors' '--continue-at' '-' '--output' $partial $Url
    if ($LASTEXITCODE -ne 0) { Fail "$Label download failed with curl exit code $LASTEXITCODE" }
    Move-Item -LiteralPath $partial -Destination $Destination -Force
    $actual = Get-Sha256 $Destination
    if ($actual -ne $ExpectedSha.ToLowerInvariant()) {
        Remove-Item -LiteralPath $Destination -Force -ErrorAction SilentlyContinue
        Fail "$Label SHA256 mismatch. Expected $ExpectedSha, got $actual"
    }
    Write-Host "  $Label verified." -ForegroundColor Green
}

function Stop-Managed([string]$PidFile) {
    if (-not (Test-Path $PidFile -PathType Leaf)) { return }
    $pidText = (Get-Content -LiteralPath $PidFile -Raw).Trim()
    $managedPid = 0
    if ([int]::TryParse($pidText, [ref]$managedPid) -and $managedPid -gt 0) {
        $p = Get-Process -Id $managedPid -ErrorAction SilentlyContinue
        if ($p) { Stop-Process -Id $managedPid -Force; Start-Sleep -Seconds 2 }
    }
    Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue
}

$PortableRoot = Join-Path $Workspace 'ComfyUI_windows_portable'
$ComfyRoot = Join-Path $PortableRoot 'ComfyUI'
$Python = Join-Path $PortableRoot 'python_embeded\python.exe'
$MainPy = Join-Path $ComfyRoot 'main.py'
$Executor = Join-Path $ProjectRepoRoot 'tools\flux-kontext-spike\run_h0_dance_chunk2_modern_pixelart_lora_probe.py'
$Helper52 = Join-Path $ProjectRepoRoot 'tools\flux-kontext-spike\run_h0_dance12_single_action_row_structure_lock.py'
$Helper51 = Join-Path $ProjectRepoRoot 'tools\flux-kontext-spike\run_h0_dance3x4_temporal_rows_structure_lock.py'
$H0Video = Join-Path $H3Workspace 'h0_exilada_ref2va_448x800_124f_base50.mp4'
$Reference = Join-Path $ProjectRepoRoot 'assets\source\characters\exilada\reference\exilada_master.png'

foreach ($f in @($Python,$MainPy,$Executor,$Helper52,$Helper51,$H0Video,$Reference)) {
    if (-not (Test-Path $f -PathType Leaf)) { Fail "required file missing: $f" }
}

Write-Host ''
Write-Host 'Roguelite Runner 53 - Kontext + Modern Pixel Art LoRA / one representative chunk only' -ForegroundColor Cyan
Write-Host '[WHY] Runner52 fixed layout/anatomy but final art still lacks deliberate high-level pixel construction.' -ForegroundColor Yellow
Write-Host '[CONTROL] Keep Kontext FP8, 20 steps, guidance2.5, CFG1, Euler/simple, seed0, denoise0.45.' -ForegroundColor Green
Write-Host '[ONLY MODEL CHANGE] Add Ume Modern Pixel Art LoRA strength1.0 and run source frames 46,57,68,79 only.' -ForegroundColor Green
Write-Host '[MASTER SCALE] Preserve 384x384 review/master cells. Gameplay apparent character height is deliberately UNLOCKED.' -ForegroundColor Green
Write-Host '[TIME] One Kontext inference instead of three; expected order of magnitude ~5 minutes after startup on the proven machine.' -ForegroundColor Green
Write-Host ''

Require-Hash (Join-Path $ComfyRoot "models\diffusion_models\$KontextName") $KontextSha256 'Kontext FP8'
Require-Hash (Join-Path $ComfyRoot "models\text_encoders\$ClipName") $ClipSha256 'CLIP-L'
Require-Hash (Join-Path $ComfyRoot "models\text_encoders\$T5Name") $T5Sha256 'T5XXL FP16'
Require-Hash (Join-Path $ComfyRoot "models\vae\$VaeName") $VaeSha256 'Flux VAE'
Download-Verified $LoraUrl (Join-Path $ComfyRoot "models\loras\$LoraName") $LoraSha256 'Modern Pixel Art LoRA (~344 MB)'

$Base = "http://127.0.0.1:$Port"
$PidFile = Join-Path $Workspace '.flux_kontext.pid'
$UserDir = Join-Path $ComfyRoot 'user'
New-Item -ItemType Directory -Force -Path $UserDir | Out-Null
$StdoutLog = Join-Path $UserDir "comfyui_kontext_${Port}_stdout.log"
$StderrLog = Join-Path $UserDir "comfyui_kontext_${Port}_stderr.log"
$ExecutorLog = Join-Path $Workspace 'h0_dance12_chunk02_pixelart_lora_executor.log'

Stop-Managed $PidFile
try { $null = Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 2; Fail "port $Port is already serving an unmanaged process" } catch {
    if ($_.Exception.Message -notlike '*unmanaged process*') { }
}

$launchArgs = @('-s',$MainPy,'--windows-standalone-build','--listen','127.0.0.1','--port',"$Port",'--disable-auto-launch')
$process = Start-Process -FilePath $Python -ArgumentList $launchArgs -WorkingDirectory $ComfyRoot `
    -RedirectStandardOutput $StdoutLog -RedirectStandardError $StderrLog -WindowStyle Hidden -PassThru
Set-Content -LiteralPath $PidFile -Value $process.Id -Encoding ASCII
Write-Host "Started Kontext ComfyUI PID $($process.Id)" -ForegroundColor Green

$ready = $false
for ($i=0; $i -lt 300; $i++) {
    try { $null = Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 2; $ready = $true; break }
    catch {
        if ($process.HasExited) {
            if (Test-Path $StderrLog) { Get-Content $StderrLog -Tail 180 }
            Fail "Kontext ComfyUI exited before Runner53 submission with code $($process.ExitCode)"
        }
        Start-Sleep -Seconds 1
    }
}
if (-not $ready) { Stop-Managed $PidFile; Fail "Kontext API did not become ready at $Base" }

if (Test-Path $ExecutorLog) { Remove-Item -LiteralPath $ExecutorLog -Force }
& $Python $Executor `
    --project-root $ProjectRepoRoot `
    --h3-workspace $H3Workspace `
    --workspace $Workspace `
    --comfy-root $ComfyRoot `
    --port $Port `
    --timeout-minutes $TimeoutMinutes 2>&1 | Tee-Object -FilePath $ExecutorLog | ForEach-Object { Write-Host $_ }
$executorExit = $LASTEXITCODE

if ($executorExit -ne 0) {
    if (Test-Path $ExecutorLog) { Get-Content -LiteralPath $ExecutorLog -Tail 260 }
    if (Test-Path $StderrLog) { Get-Content -LiteralPath $StderrLog -Tail 260 }
    Stop-Managed $PidFile
    Fail "Runner53 executor exited with code $executorExit"
}

$Expected = @(
    (Join-Path $Workspace 'h0_dance12_chunk02_pixelart_lora_full.png'),
    (Join-Path $Workspace 'h0_dance12_chunk02_pixelart_lora_strip_opaque.png'),
    (Join-Path $Workspace 'h0_dance12_chunk02_pixelart_lora_strip_rgba.png'),
    (Join-Path $Workspace 'h0_dance12_chunk02_pixelart_lora_preview.gif'),
    (Join-Path $Workspace 'h0_dance12_chunk02_pixelart_lora_manifest.json')
)
foreach ($f in $Expected) { if (-not (Test-Path $f -PathType Leaf)) { Stop-Managed $PidFile; Fail "expected output missing: $f" } }

Stop-Managed $PidFile
Write-Host ''
Write-Host 'RUNNER53-KONTEXT-PIXELART-LORA: PASS - ONE-CHUNK INFERENCE COMPLETE / VISUAL VERDICT PENDING' -ForegroundColor Green
Write-Host "Full output: $(Join-Path $Workspace 'h0_dance12_chunk02_pixelart_lora_full.png')" -ForegroundColor Cyan
Write-Host "Opaque master strip: $(Join-Path $Workspace 'h0_dance12_chunk02_pixelart_lora_strip_opaque.png')" -ForegroundColor Cyan
Write-Host "RGBA master strip: $(Join-Path $Workspace 'h0_dance12_chunk02_pixelart_lora_strip_rgba.png')" -ForegroundColor Cyan
Write-Host "Preview GIF: $(Join-Path $Workspace 'h0_dance12_chunk02_pixelart_lora_preview.gif')" -ForegroundColor Cyan
Write-Host "Manifest: $(Join-Path $Workspace 'h0_dance12_chunk02_pixelart_lora_manifest.json')" -ForegroundColor Cyan
Write-Host "Executor log: $ExecutorLog" -ForegroundColor Cyan
