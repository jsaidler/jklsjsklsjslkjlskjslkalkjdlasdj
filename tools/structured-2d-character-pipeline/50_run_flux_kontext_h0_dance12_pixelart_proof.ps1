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
$ClipSha256 = '660c6f5b1abae9dc498ac2d21e1347d2abdb0cf6c0c8576cd796491d9a6cdd'

$T5Name = 't5xxl_fp16.safetensors'
$T5Url = 'https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp16.safetensors'
$T5Sha256 = '6e480b09fae049a72d2a8c5fbccb8d3e92febeb233bbe9dfe7256958a9167635'

$VaeName = 'ae.safetensors'
$VaeUrl = 'https://huggingface.co/Comfy-Org/Lumina_Image_2.0_Repackaged/resolve/main/split_files/vae/ae.safetensors'
$VaeSha256 = 'afc8e28272cd15db3919bacdb6918ce9c1ed22e96cb12c4d5ed0fba823529e38'

function Fail([string]$Message) {
    Write-Host "RUNNER50-KONTEXT-H0-DANCE12: FAIL - $Message" -ForegroundColor Red
    exit 1
}

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Download-Verified([string]$Url, [string]$Destination, [string]$ExpectedSha, [string]$Label) {
    $parent = Split-Path -Parent $Destination
    New-Item -ItemType Directory -Force -Path $parent | Out-Null

    if (Test-Path $Destination -PathType Leaf) {
        Write-Host "Hash-checking existing $Label: $Destination" -ForegroundColor DarkCyan
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

    Write-Host "Downloading $Label: $Url" -ForegroundColor Cyan
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

function Ensure-SeparatePortableRuntime([string]$SourcePortable, [string]$DestinationPortable) {
    $dstPython = Join-Path $DestinationPortable 'python_embeded\python.exe'
    $dstMain = Join-Path $DestinationPortable 'ComfyUI\main.py'
    if ((Test-Path $dstPython -PathType Leaf) -and (Test-Path $dstMain -PathType Leaf)) {
        Write-Host 'Separate Flux Kontext portable runtime already exists.' -ForegroundColor Green
        return
    }

    if (-not (Test-Path $SourcePortable -PathType Container)) {
        Fail "pinned H3 portable runtime missing: $SourcePortable"
    }

    New-Item -ItemType Directory -Force -Path $DestinationPortable | Out-Null
    Write-Host 'Cloning the already-proven pinned ComfyUI v0.34.0 runtime without copying H3 models/inputs/outputs...' -ForegroundColor Cyan

    $sourceComfy = Join-Path $SourcePortable 'ComfyUI'
    $exclude = @(
        (Join-Path $sourceComfy 'models'),
        (Join-Path $sourceComfy 'input'),
        (Join-Path $sourceComfy 'output'),
        (Join-Path $sourceComfy 'temp'),
        (Join-Path $sourceComfy 'user')
    )

    $roboArgs = @($SourcePortable, $DestinationPortable, '/E', '/R:2', '/W:2', '/NFL', '/NDL', '/NJH', '/NJS', '/NP', '/XD') + $exclude
    & robocopy.exe @roboArgs | Out-Null
    $rc = $LASTEXITCODE
    if ($rc -ge 8) {
        Fail "robocopy failed while cloning the pinned runtime, exit code $rc"
    }

    if (-not (Test-Path $dstPython -PathType Leaf) -or -not (Test-Path $dstMain -PathType Leaf)) {
        Fail 'separate Kontext portable runtime clone is incomplete.'
    }
}

$SourcePortable = Join-Path $H3Workspace 'ComfyUI_windows_portable'
$PortableRoot = Join-Path $Workspace 'ComfyUI_windows_portable'
$ComfyRoot = Join-Path $PortableRoot 'ComfyUI'
$Python = Join-Path $PortableRoot 'python_embeded\python.exe'
$MainPy = Join-Path $ComfyRoot 'main.py'
$Executor = Join-Path $ProjectRepoRoot 'tools\flux-kontext-spike\run_h0_dance12_pixelart_proof.py'
$H0Video = Join-Path $H3Workspace 'h0_exilada_ref2va_448x800_124f_base50.mp4'
$Reference = Join-Path $ProjectRepoRoot 'assets\source\characters\exilada\reference\exilada_master.png'

foreach ($f in @($Executor,$H0Video,$Reference)) {
    if (-not (Test-Path $f -PathType Leaf)) { Fail "required proof input missing: $f" }
}

$driveLetter = ([IO.Path]::GetPathRoot($Workspace)).Substring(0,1)
$drive = Get-PSDrive -Name $driveLetter -ErrorAction Stop
if ($drive.Free -lt 30GB -and -not (Test-Path $PortableRoot -PathType Container)) {
    Fail "need at least ~30 GB free on $driveLetter`: for the separate Kontext runtime + ~22.3 GB model set; free is $([math]::Round($drive.Free/1GB,2)) GB"
}

Write-Host ''
Write-Host 'Roguelite Runner 50 - FLUX.1 Kontext [dev] / existing H0 dance12 -> pixel-art spritesheet proof' -ForegroundColor Cyan
Write-Host "[H3 SOURCE] $H3Workspace" -ForegroundColor Green
Write-Host "[KONTEXT WORKSPACE] $Workspace" -ForegroundColor Green
Write-Host '[NO NEW H3] Uses the already-approved Base50 H0 video; no video generation is repeated.' -ForegroundColor Green
Write-Host '[RENDERER] Official ComfyUI native FLUX.1 Kontext dev FP8-scaled diffusion + T5XXL FP16.' -ForegroundColor Green
Write-Host '[PURPOSE] Prove the downstream frames -> Kontext -> final-style pixel-art sheet stage before building the Gradio UI.' -ForegroundColor Yellow
Write-Host '[LICENSE] Technical validation only; FLUX.1 dev open weights are under the non-commercial license.' -ForegroundColor Yellow
Write-Host ''

Ensure-SeparatePortableRuntime $SourcePortable $PortableRoot

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

Download-Verified $KontextUrl (Join-Path $ComfyRoot "models\diffusion_models\$KontextName") $KontextSha256 'FLUX.1 Kontext dev FP8-scaled diffusion (~11.9 GB)'
Download-Verified $ClipUrl (Join-Path $ComfyRoot "models\text_encoders\$ClipName") $ClipSha256 'CLIP-L (~246 MB)'
Download-Verified $T5Url (Join-Path $ComfyRoot "models\text_encoders\$T5Name") $T5Sha256 'T5XXL FP16 (~9.79 GB)'
Download-Verified $VaeUrl (Join-Path $ComfyRoot "models\vae\$VaeName") $VaeSha256 'Flux AE/VAE (~335 MB)'

foreach ($f in @($Python,$MainPy)) {
    if (-not (Test-Path $f -PathType Leaf)) { Fail "separate pinned runtime prerequisite missing: $f" }
}

$Base = "http://127.0.0.1:$Port"
$PidFile = Join-Path $Workspace '.flux_kontext.pid'
$UserDir = Join-Path $ComfyRoot 'user'
$StdoutLog = Join-Path $UserDir "comfyui_kontext_${Port}_stdout.log"
$StderrLog = Join-Path $UserDir "comfyui_kontext_${Port}_stderr.log"
$ExecutorLog = Join-Path $Workspace 'h0_dance12_kontext_executor.log'

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
Write-Host 'Starting separate pinned ComfyUI v0.34.0 for Flux Kontext...' -ForegroundColor Cyan
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
            Fail "Kontext ComfyUI exited before submission with code $($process.ExitCode)"
        }
        Start-Sleep -Seconds 1
    }
}
if (-not $ready) {
    if (Test-Path $StderrLog) { Get-Content $StderrLog -Tail 180 }
    Stop-Managed $PidFile 'TIMEOUT-CLEANUP'
    Fail "Kontext ComfyUI API did not become ready at $Base"
}

Write-Host 'Submitting existing-H0 12-frame pixel-art reconstruction proof...' -ForegroundColor Cyan
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
    Write-Host 'Kontext executor diagnostics:' -ForegroundColor Red
    if (Test-Path $ExecutorLog) { Get-Content -LiteralPath $ExecutorLog -Tail 220 }
    Write-Host ''
    Write-Host 'Pinned ComfyUI stderr tail:' -ForegroundColor DarkYellow
    if (Test-Path $StderrLog) { Get-Content -LiteralPath $StderrLog -Tail 240 }
    Write-Host ''
    Write-Host 'Pinned ComfyUI stdout tail:' -ForegroundColor DarkYellow
    if (Test-Path $StdoutLog) { Get-Content -LiteralPath $StdoutLog -Tail 160 }
    Stop-Managed $PidFile 'FAILURE-CLEANUP'
    Fail "Kontext executor exited with code $executorExit. Classify the failure layer before changing model/settings."
}

$Expected = @(
    (Join-Path $Workspace 'h0_dance12_input_sheet.png'),
    (Join-Path $Workspace 'h0_dance12_kontext_full.png'),
    (Join-Path $Workspace 'h0_dance12_pixelart_sheet_opaque.png'),
    (Join-Path $Workspace 'h0_dance12_pixelart_sheet_rgba.png'),
    (Join-Path $Workspace 'h0_dance12_pixelart_preview.gif'),
    (Join-Path $Workspace 'h0_dance12_kontext_manifest.json'),
    (Join-Path $Workspace 'h0_dance12_kontext_api_prompt.json')
)
foreach ($f in $Expected) {
    if (-not (Test-Path $f -PathType Leaf)) {
        Stop-Managed $PidFile 'OUTPUT-FAIL-CLEANUP'
        Fail "expected Kontext proof file missing: $f"
    }
}

Stop-Managed $PidFile 'PASS-CLEANUP'

Write-Host ''
Write-Host 'RUNNER50-KONTEXT-H0-DANCE12: PASS - INFERENCE COMPLETE / VISUAL VERDICT PENDING' -ForegroundColor Green
Write-Host "Input sheet:    $(Join-Path $Workspace 'h0_dance12_input_sheet.png')" -ForegroundColor Cyan
Write-Host "Full Kontext:   $(Join-Path $Workspace 'h0_dance12_kontext_full.png')" -ForegroundColor Cyan
Write-Host "RGBA sheet:     $(Join-Path $Workspace 'h0_dance12_pixelart_sheet_rgba.png')" -ForegroundColor Cyan
Write-Host "Opaque sheet:   $(Join-Path $Workspace 'h0_dance12_pixelart_sheet_opaque.png')" -ForegroundColor Cyan
Write-Host "Preview GIF:    $(Join-Path $Workspace 'h0_dance12_pixelart_preview.gif')" -ForegroundColor Cyan
Write-Host "Manifest:       $(Join-Path $Workspace 'h0_dance12_kontext_manifest.json')" -ForegroundColor Cyan
Write-Host "Executor log:   $ExecutorLog" -ForegroundColor Cyan
Write-Host ''
Write-Host 'Do not call the renderer proven until the 12-frame output is visually reviewed against the H0 motion and canonical Exilada reference.' -ForegroundColor Yellow
