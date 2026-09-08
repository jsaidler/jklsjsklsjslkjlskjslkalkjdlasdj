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
$KontextUrl = 'https://huggingface.co/Comfy-Org/flux1-kontext-dev_ComfyUI/resolve/main/split_files/diffusion_models/flux1-dev-kontext_fp8_scaled.safetensors'
$KontextSha256 = '630ba795ec64283b4230ea23cf79406c2c68b7c578229ed139f30043eadb30a2'

$ClipName = 'clip_l.safetensors'
$ClipUrl = 'https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors'
$ClipSha256 = '660c6f5b1abae9dc498ac2d21e1347d2abdb0cf6c0c0c8576cd796491d9a6cdd'

$T5Name = 't5xxl_fp16.safetensors'
$T5Url = 'https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp16.safetensors'
$T5Sha256 = '6e480b09fae049a72d2a8c5fbccb8d3e92febeb233bbe9dfe7256958a9167635'

$VaeName = 'ae.safetensors'
$VaeUrl = 'https://huggingface.co/Comfy-Org/Lumina_Image_2.0_Repackaged/resolve/main/split_files/vae/ae.safetensors'
$VaeSha256 = 'afc8e28272cd15db3919bacdb6918ce9c1ed22e96cb12c4d5ed0fba823529e38'

function Fail([string]$Message) {
    Write-Host "RUNNER51-KONTEXT-H0-ROWS: FAIL - $Message" -ForegroundColor Red
    exit 1
}

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Download-Verified([string]$Url, [string]$Destination, [string]$ExpectedSha, [string]$Label) {
    $parent = Split-Path -Parent $Destination
    New-Item -ItemType Directory -Force -Path $parent | Out-Null

    if (Test-Path $Destination -PathType Leaf) {
        Write-Host "Hash-checking existing ${Label}: $Destination" -ForegroundColor DarkCyan
        $existingHash = Get-Sha256 $Destination
        if ($existingHash -eq $ExpectedSha.ToLowerInvariant()) {
            Write-Host "  $Label already present and verified." -ForegroundColor Green
            return
        }
        Write-Host "  Existing $Label hash is wrong; deleting it." -ForegroundColor Yellow
        Remove-Item -LiteralPath $Destination -Force
    }

    $partial = "$Destination.part"
    $curl = Get-Command curl.exe -ErrorAction SilentlyContinue
    if (-not $curl) { Fail 'curl.exe is required for resumable verified downloads.' }

    Write-Host "Downloading ${Label}: $Url" -ForegroundColor Cyan
    & $curl.Source '--fail' '--location' '--retry' '5' '--retry-delay' '5' '--retry-all-errors' '--continue-at' '-' '--output' $partial $Url
    if ($LASTEXITCODE -ne 0) { Fail "$Label download failed with curl exit code $LASTEXITCODE" }

    Move-Item -LiteralPath $partial -Destination $Destination -Force
    $actual = Get-Sha256 $Destination
    if ($actual -ne $ExpectedSha.ToLowerInvariant()) {
        Remove-Item -LiteralPath $Destination -Force -ErrorAction SilentlyContinue
        Fail "$Label SHA256 mismatch. Expected $ExpectedSha, got $actual. Corrupt file deleted."
    }
    Write-Host "  $Label verified." -ForegroundColor Green
}

function Stop-Managed([string]$PidFile, [string]$Label) {
    if (-not (Test-Path $PidFile -PathType Leaf)) { return }
    $pidText = (Get-Content -LiteralPath $PidFile -Raw).Trim()
    $managedPid = 0
    if (-not [int]::TryParse($pidText, [ref]$managedPid) -or $managedPid -le 0) {
        Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue
        return
    }
    $p = Get-Process -Id $managedPid -ErrorAction SilentlyContinue
    if ($p) {
        Write-Host "[$Label] stopping managed Kontext ComfyUI PID $managedPid." -ForegroundColor Yellow
        Stop-Process -Id $managedPid -Force
        Start-Sleep -Seconds 2
    }
    Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue
}

$PortableRoot = Join-Path $Workspace 'ComfyUI_windows_portable'
$ComfyRoot = Join-Path $PortableRoot 'ComfyUI'
$Python = Join-Path $PortableRoot 'python_embeded\python.exe'
$MainPy = Join-Path $ComfyRoot 'main.py'
$Executor = Join-Path $ProjectRepoRoot 'tools\flux-kontext-spike\run_h0_dance3x4_temporal_rows_structure_lock.py'
$H0Video = Join-Path $H3Workspace 'h0_exilada_ref2va_448x800_124f_base50.mp4'
$Reference = Join-Path $ProjectRepoRoot 'assets\source\characters\exilada\reference\exilada_master.png'

foreach ($f in @($Python,$MainPy,$Executor,$H0Video,$Reference)) {
    if (-not (Test-Path $f -PathType Leaf)) { Fail "required input/runtime file missing: $f" }
}

foreach ($dir in @(
    (Join-Path $ComfyRoot 'models\diffusion_models'),
    (Join-Path $ComfyRoot 'models\text_encoders'),
    (Join-Path $ComfyRoot 'models\vae'),
    (Join-Path $ComfyRoot 'input'),
    (Join-Path $ComfyRoot 'output'),
    (Join-Path $ComfyRoot 'temp'),
    (Join-Path $ComfyRoot 'user')
)) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
}

Write-Host ''
Write-Host 'Roguelite Runner 51 - FLUX Kontext structure-lock / one coherent animation per row' -ForegroundColor Cyan
Write-Host '[SOURCE] Existing approved H3 Base50 H0 dance/gesture video. No new H3 inference.' -ForegroundColor Green
Write-Host '[FIX 1] One coherent short temporal sequence per final row; no 12-frame global scatter.' -ForegroundColor Green
Write-Host '[FIX 2] Each four-frame row is rendered separately as a 2x2 1024x1024 high-detail input.' -ForegroundColor Green
Write-Host '[FIX 3] Kontext denoise lowered to 0.45 to preserve adult body structure and source pose.' -ForegroundColor Green
Write-Host '[ART LOCK] Heavy Metal / Conan / Red Sonja / Frazetta / Julie Bell mature sword-and-sorcery remains mandatory.' -ForegroundColor Yellow
Write-Host '[HARD BODY LOCK] Do not infantilize, shorten, thicken, cute-ify or change adult proportions.' -ForegroundColor Yellow
Write-Host ''

Download-Verified $KontextUrl (Join-Path $ComfyRoot "models\diffusion_models\$KontextName") $KontextSha256 'FLUX.1 Kontext dev FP8-scaled diffusion (~11.9 GB)'
Download-Verified $ClipUrl (Join-Path $ComfyRoot "models\text_encoders\$ClipName") $ClipSha256 'CLIP-L (~246 MB)'
Download-Verified $T5Url (Join-Path $ComfyRoot "models\text_encoders\$T5Name") $T5Sha256 'T5XXL FP16 (~9.79 GB)'
Download-Verified $VaeUrl (Join-Path $ComfyRoot "models\vae\$VaeName") $VaeSha256 'Flux AE/VAE (~335 MB)'

$Base = "http://127.0.0.1:$Port"
$PidFile = Join-Path $Workspace '.flux_kontext.pid'
$UserDir = Join-Path $ComfyRoot 'user'
$StdoutLog = Join-Path $UserDir "comfyui_kontext_${Port}_stdout.log"
$StderrLog = Join-Path $UserDir "comfyui_kontext_${Port}_stderr.log"
$ExecutorLog = Join-Path $Workspace 'h0_dance3x4_kontext_executor.log'

Stop-Managed $PidFile 'CLEAN-LAUNCH'
$apiRunning = $false
try {
    $null = Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 2
    $apiRunning = $true
} catch {}
if ($apiRunning) {
    Fail "port $Port is already serving an unmanaged process. Stop it or choose another port."
}

$launchArgs = @('-s',$MainPy,'--windows-standalone-build','--listen','127.0.0.1','--port',"$Port",'--disable-auto-launch')
Write-Host 'Starting isolated pinned ComfyUI v0.34.0 for Runner51...' -ForegroundColor Cyan
$process = Start-Process -FilePath $Python -ArgumentList $launchArgs -WorkingDirectory $ComfyRoot `
    -RedirectStandardOutput $StdoutLog -RedirectStandardError $StderrLog -WindowStyle Hidden -PassThru
Set-Content -LiteralPath $PidFile -Value $process.Id -Encoding ASCII
Write-Host "Started Kontext ComfyUI PID $($process.Id)" -ForegroundColor Green

$ready = $false
for ($i=0; $i -lt 300; $i++) {
    try {
        $null = Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 2
        $ready = $true
        break
    } catch {
        if ($process.HasExited) {
            if (Test-Path $StderrLog) { Get-Content $StderrLog -Tail 180 }
            Fail "Kontext ComfyUI exited before Runner51 submission with code $($process.ExitCode)"
        }
        Start-Sleep -Seconds 1
    }
}
if (-not $ready) {
    if (Test-Path $StderrLog) { Get-Content $StderrLog -Tail 180 }
    Stop-Managed $PidFile 'TIMEOUT-CLEANUP'
    Fail "Kontext ComfyUI API did not become ready at $Base"
}

Write-Host 'Submitting Runner51 temporal-row structure-lock proof...' -ForegroundColor Cyan
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
    Write-Host ''
    Write-Host 'Runner51 executor diagnostics:' -ForegroundColor Red
    if (Test-Path $ExecutorLog) { Get-Content -LiteralPath $ExecutorLog -Tail 260 }
    Write-Host ''
    Write-Host 'Pinned ComfyUI stderr tail:' -ForegroundColor DarkYellow
    if (Test-Path $StderrLog) { Get-Content -LiteralPath $StderrLog -Tail 260 }
    Write-Host ''
    Write-Host 'Pinned ComfyUI stdout tail:' -ForegroundColor DarkYellow
    if (Test-Path $StdoutLog) { Get-Content -LiteralPath $StdoutLog -Tail 180 }
    Stop-Managed $PidFile 'FAILURE-CLEANUP'
    Fail "Runner51 executor exited with code $executorExit. Classify the failure layer before changing model/settings."
}

$Expected = @(
    (Join-Path $Workspace 'h0_dance3x4_source_temporal_rows.png'),
    (Join-Path $Workspace 'h0_dance3x4_temporal_selection_manifest.json'),
    (Join-Path $Workspace 'h0_dance3x4_pixelart_sheet_opaque.png'),
    (Join-Path $Workspace 'h0_dance3x4_pixelart_sheet_rgba.png'),
    (Join-Path $Workspace 'h0_dance_row01_preview.gif'),
    (Join-Path $Workspace 'h0_dance_row02_preview.gif'),
    (Join-Path $Workspace 'h0_dance_row03_preview.gif'),
    (Join-Path $Workspace 'h0_dance3x4_kontext_manifest.json')
)
foreach ($f in $Expected) {
    if (-not (Test-Path $f -PathType Leaf)) {
        Stop-Managed $PidFile 'OUTPUT-FAIL-CLEANUP'
        Fail "expected Runner51 output missing: $f"
    }
}

Stop-Managed $PidFile 'PASS-CLEANUP'

Write-Host ''
Write-Host 'RUNNER51-KONTEXT-H0-ROWS: PASS - THREE ROW INFERENCES COMPLETE / VISUAL VERDICT PENDING' -ForegroundColor Green
Write-Host "Source rows:  $(Join-Path $Workspace 'h0_dance3x4_source_temporal_rows.png')" -ForegroundColor Cyan
Write-Host "Opaque sheet: $(Join-Path $Workspace 'h0_dance3x4_pixelart_sheet_opaque.png')" -ForegroundColor Cyan
Write-Host "RGBA sheet:   $(Join-Path $Workspace 'h0_dance3x4_pixelart_sheet_rgba.png')" -ForegroundColor Cyan
Write-Host "Row 1 GIF:    $(Join-Path $Workspace 'h0_dance_row01_preview.gif')" -ForegroundColor Cyan
Write-Host "Row 2 GIF:    $(Join-Path $Workspace 'h0_dance_row02_preview.gif')" -ForegroundColor Cyan
Write-Host "Row 3 GIF:    $(Join-Path $Workspace 'h0_dance_row03_preview.gif')" -ForegroundColor Cyan
Write-Host "Manifest:     $(Join-Path $Workspace 'h0_dance3x4_kontext_manifest.json')" -ForegroundColor Cyan
Write-Host "Executor log: $ExecutorLog" -ForegroundColor Cyan
Write-Host ''
Write-Host 'Review body maturity/proportions, temporal coherence per row, pose preservation, pixel-art quality and 1980s sword-and-sorcery charge separately.' -ForegroundColor Yellow
