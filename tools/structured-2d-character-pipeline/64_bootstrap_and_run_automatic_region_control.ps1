param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$QwenWorkspace = 'Z:\AI\QwenImageEdit',
    [string]$KleinWorkspace = 'Z:\AI\Flux2Klein',
    [string]$StudioRoot = 'Z:\AI\RogueliteAssetStudio',
    [int]$Port = 8193,
    [int]$TimeoutMinutes = 480
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ComfyCommit = '6eba895f7d3615284da81e95bf49eaed4a5f7309'
$QwenModelName = 'qwen_image_edit_2511_fp8mixed.safetensors'
$QwenModelSha = 'c9fdc158e46d3b61ef75f21ae866ca2fe808bf4a53643120d1c1e87c19280a4e'
$TextEncoderName = 'qwen_2.5_vl_7b_fp8_scaled.safetensors'
$TextEncoderSha = 'cb5636d852a0ea6a9075ab1bef496c0db7aef13c02350571e388aea959c5c0b4'
$VaeName = 'qwen_image_vae.safetensors'
$VaeSha = 'a70580f0213e67967ee9c95f05bb400e8fb08307e017a924bf3441223e023d1f'

function Fail([string]$Message) {
    Write-Host "RUNNER64-AUTOMATIC-REGION-CONTROL: FAIL - $Message" -ForegroundColor Red
    exit 1
}
function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}
function Require-Hash([string]$Path,[string]$Expected,[string]$Label) {
    if (-not (Test-Path $Path -PathType Leaf)) { Fail "required $Label missing: $Path" }
    $actual = Get-Sha256 $Path
    if ($actual -ne $Expected.ToLowerInvariant()) { Fail "$Label SHA256 mismatch. Expected $Expected got $actual" }
    Write-Host "  $Label verified." -ForegroundColor Green
}
function Quote-ProcessArg([string]$Value) {
    if ($Value -match '[\s"]') { return '"' + ($Value -replace '"','\"') + '"' }
    return $Value
}
function Read-TextFileOrEmpty([string]$Path) {
    if (-not (Test-Path $Path -PathType Leaf)) { return '' }
    $v = Get-Content -LiteralPath $Path -Raw
    if ($null -eq $v) { return '' }
    return [string]$v
}
function Print-TextFile([string]$Path,[string]$Header,[int]$Tail=0) {
    Write-Host $Header -ForegroundColor Yellow
    if (-not (Test-Path $Path -PathType Leaf)) { Write-Host "  <missing: $Path>"; return }
    if ($Tail -gt 0) { Get-Content -LiteralPath $Path -Tail $Tail } else { Get-Content -LiteralPath $Path }
}
function Stop-Managed([string]$PidFile) {
    if (-not (Test-Path $PidFile -PathType Leaf)) { return }
    $raw = Get-Content -LiteralPath $PidFile -Raw
    if ($null -ne $raw) {
        $managedPid = 0
        if ([int]::TryParse(([string]$raw).Trim(), [ref]$managedPid) -and $managedPid -gt 0) {
            $p = Get-Process -Id $managedPid -ErrorAction SilentlyContinue
            if ($p) { Stop-Process -Id $managedPid -Force; Start-Sleep -Seconds 2 }
        }
    }
    Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue
}
function Invoke-PipRetry([string[]]$PipArgs) {
    for ($attempt=1; $attempt -le 5; $attempt++) {
        Write-Host "pip attempt $attempt/5..." -ForegroundColor Cyan
        & $Python -s -m pip --disable-pip-version-check --retries 12 --timeout 120 @PipArgs
        if ($LASTEXITCODE -eq 0) { return }
        if ($attempt -lt 5) {
            $delay = 10 * $attempt
            Write-Host "pip failed with exit code $LASTEXITCODE; retrying in $delay seconds..." -ForegroundColor Yellow
            Start-Sleep -Seconds $delay
        }
    }
    Fail 'required Python dependency installation failed after retries'
}

$PortableRoot = Join-Path $QwenWorkspace 'ComfyUI_windows_portable'
$Python = Join-Path $PortableRoot 'python_embeded\python.exe'
$ComfyRoot = Join-Path $PortableRoot 'ComfyUI'
$MainPy = Join-Path $ComfyRoot 'main.py'
$QwenModel = Join-Path $ComfyRoot "models\diffusion_models\$QwenModelName"
$TextEncoder = Join-Path $ComfyRoot "models\text_encoders\$TextEncoderName"
$Vae = Join-Path $ComfyRoot "models\vae\$VaeName"
$Original = Join-Path $KleinWorkspace 'spike\flux2_klein_4b_t2i_probe.png'
$Runner63Manifest = Join-Path $QwenWorkspace 'qwen2511_precision_gate\runner63_qwen2511_precision_manifest.json'
$Runner63Plank = Join-Path $QwenWorkspace 'qwen2511_precision_gate\qwen2511_atomic_plank_steps20.png'
$Runner63Strap = Join-Path $QwenWorkspace 'qwen2511_precision_gate\qwen2511_atomic_strap_steps20.png'
$Localizer = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\automatic_region_localizer.py'
$RegionExecutor = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\qwen2511_region_control_gate.py'
$QwenAdapter = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\qwen_image_edit_2511_adapter.py'
$Protocol = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\adapter_protocol.py'
$SharedAdapter = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\flux2_klein_adapter.py'

foreach ($required in @($Python,$MainPy,$Original,$Runner63Manifest,$Runner63Plank,$Runner63Strap,$Localizer,$RegionExecutor,$QwenAdapter,$Protocol,$SharedAdapter)) {
    if (-not (Test-Path $required -PathType Leaf)) { Fail "required prerequisite missing: $required" }
}
Require-Hash $QwenModel $QwenModelSha 'Qwen-Image-Edit-2511 FP8mixed'
Require-Hash $TextEncoder $TextEncoderSha 'Qwen2.5-VL 7B FP8 encoder'
Require-Hash $Vae $VaeSha 'Qwen image VAE'
$currentCommit = (& git.exe -C $ComfyRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $currentCommit -ne $ComfyCommit) { Fail "Qwen ComfyUI commit mismatch. Expected $ComfyCommit got $currentCommit" }
Write-Host "  Qwen ComfyUI commit verified: $currentCommit" -ForegroundColor Green

$LocalizationRoot = Join-Path $StudioRoot 'localization'
$ModelCache = Join-Path $LocalizationRoot 'hf_cache'
$LocalizationGate = Join-Path $LocalizationRoot 'runner64_gate'
$RegionOutput = Join-Path $QwenWorkspace 'automatic_region_control'
New-Item -ItemType Directory -Force -Path $LocalizationRoot,$ModelCache,$LocalizationGate,$RegionOutput | Out-Null

Write-Host ''
Write-Host 'Roguelite Runner 64 - AUTOMATIC LOCALIZATION + REGION CONTROL' -ForegroundColor Cyan
Write-Host '[WHY] Runner63 improved one-plank editing but still failed exact lower-right strap control with a global prompt.' -ForegroundColor Yellow
Write-Host '[PERCEPTION] Grounding DINO Tiny -> text-grounded candidate boxes.' -ForegroundColor Green
Write-Host '[SEGMENTATION] SAM2.1 Hiera Small -> precise automatic component mask from the chosen box.' -ForegroundColor Green
Write-Host '[EDIT] Qwen-Image-Edit-2511 edits only a contextual crop and receives an automatic target-guide reference.' -ForegroundColor Green
Write-Host '[COMPOSITE] Only the automatically dilated/feathered target neighborhood is allowed to modify the full image.' -ForegroundColor Green
Write-Host '[NO MANUAL MASKS] All boxes, masks, crops and composites are generated by the pipeline.' -ForegroundColor Green
Write-Host '[DOWNLOAD] First run may fetch ~873 MB of perception weights plus small processor/config files.' -ForegroundColor Green
Write-Host ''

$driveRoot = [System.IO.Path]::GetPathRoot($StudioRoot)
$driveInfo = [System.IO.DriveInfo]::new($driveRoot)
$freeGiB = [math]::Round($driveInfo.AvailableFreeSpace / 1GB, 2)
Write-Host "Disk preflight: free=${freeGiB} GiB; required margin=3 GiB." -ForegroundColor Cyan
if ($driveInfo.AvailableFreeSpace -lt 3GB) { Fail 'insufficient free space for localization models/cache/output margin' }

# Ensure the installed Transformers build exposes both Grounding DINO and SAM2.
& $Python -s -c "from transformers import AutoModelForZeroShotObjectDetection, AutoProcessor, Sam2Model, Sam2Processor; import transformers; print(transformers.__version__)" 2>$null
$transformerProbe = $LASTEXITCODE
if ($transformerProbe -ne 0) {
    Write-Host 'Installed Transformers build lacks the required SAM2/GroundingDINO classes; upgrading within the ComfyUI-compatible >=4.50.3 range...' -ForegroundColor Yellow
    Invoke-PipRetry @('install','transformers>=5.8,<6')
    & $Python -s -c "from transformers import AutoModelForZeroShotObjectDetection, AutoProcessor, Sam2Model, Sam2Processor; import transformers; print(transformers.__version__)"
    if ($LASTEXITCODE -ne 0) { Fail 'Transformers still lacks required localization classes after upgrade' }
} else {
    Write-Host '  Transformers localization APIs verified.' -ForegroundColor Green
}

# Hugging Face downloads are pinned by revision inside the localizer and resumable in this cache.
$env:HF_HOME = $ModelCache
$env:HF_HUB_CACHE = Join-Path $ModelCache 'hub'
$env:HF_HUB_DOWNLOAD_TIMEOUT = '120'
$env:HF_HUB_ETAG_TIMEOUT = '60'
$env:HF_HUB_DISABLE_XET = '1'

$LocStdout = Join-Path $LocalizationGate 'runner64_localizer_stdout.log'
$LocStderr = Join-Path $LocalizationGate 'runner64_localizer_stderr.log'
foreach ($p in @($LocStdout,$LocStderr)) { if (Test-Path $p) { Remove-Item -LiteralPath $p -Force } }
$locArgs = @(
    '-s',(Quote-ProcessArg $Localizer),
    '--source',(Quote-ProcessArg $Original),
    '--output-dir',(Quote-ProcessArg $LocalizationGate),
    '--model-cache',(Quote-ProcessArg $ModelCache),
    '--device','cuda'
)
Write-Host 'RUNNER64: launching automatic component localization...' -ForegroundColor Cyan
$locProcess = Start-Process -FilePath $Python -ArgumentList $locArgs -WorkingDirectory $ProjectRepoRoot -RedirectStandardOutput $LocStdout -RedirectStandardError $LocStderr -WindowStyle Hidden -PassThru -Wait
Print-TextFile $LocStdout '--- RUNNER64 LOCALIZER STDOUT ---'
$locErr = Read-TextFileOrEmpty $LocStderr
if (-not [string]::IsNullOrWhiteSpace($locErr)) { Print-TextFile $LocStderr '--- RUNNER64 LOCALIZER STDERR ---' 250 }
if ($locProcess.ExitCode -ne 0) { Fail "automatic localizer exited with code $($locProcess.ExitCode)" }

$LocalizationManifest = Join-Path $LocalizationGate 'runner64_localization_manifest.json'
foreach ($name in @('plank_detection.png','plank_mask.png','plank_mask_overlay.png','plank_crop.png','plank_crop_mask.png','strap_detection.png','strap_mask.png','strap_mask_overlay.png','strap_crop.png','strap_crop_mask.png','runner64_localization_manifest.json')) {
    if (-not (Test-Path (Join-Path $LocalizationGate $name) -PathType Leaf)) { Fail "localization output missing: $name" }
}

# Localization process has exited, so its GPU models are gone before Qwen starts.
$Base = "http://127.0.0.1:$Port"
$PidFile = Join-Path $QwenWorkspace '.qwen2511_runner64.pid'
$ComfyStdout = Join-Path $RegionOutput "comfyui_runner64_${Port}_stdout.log"
$ComfyStderr = Join-Path $RegionOutput "comfyui_runner64_${Port}_stderr.log"
Stop-Managed $PidFile
$portBusy = $false
try { $null = Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 2; $portBusy = $true } catch { }
if ($portBusy) { Fail "port $Port already serves an unmanaged process" }

$env:PYTORCH_CUDA_ALLOC_CONF = 'expandable_segments:True'
$launchArgs = @('-s',$MainPy,'--windows-standalone-build','--listen','127.0.0.1','--port',"$Port",'--disable-auto-launch','--lowvram','--reserve-vram','1.0')
$process = Start-Process -FilePath $Python -ArgumentList $launchArgs -WorkingDirectory $ComfyRoot -RedirectStandardOutput $ComfyStdout -RedirectStandardError $ComfyStderr -WindowStyle Hidden -PassThru
Set-Content -LiteralPath $PidFile -Value $process.Id -Encoding ASCII
Write-Host "Started isolated Qwen2511 ComfyUI PID $($process.Id) on port $Port" -ForegroundColor Green

$ready = $false
for ($i=0; $i -lt 360; $i++) {
    try { $null = Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 2; $ready=$true; break }
    catch {
        if ($process.HasExited) { Print-TextFile $ComfyStderr '--- COMFYUI STDERR ---' 300; Stop-Managed $PidFile; Fail "ComfyUI exited before readiness: $($process.ExitCode)" }
        Start-Sleep -Seconds 1
    }
}
if (-not $ready) { Print-TextFile $ComfyStderr '--- COMFYUI STDERR ---' 300; Stop-Managed $PidFile; Fail 'ComfyUI did not become ready' }

$ExecStdout = Join-Path $RegionOutput 'runner64_region_python_stdout.log'
$ExecStderr = Join-Path $RegionOutput 'runner64_region_python_stderr.log'
$ExecLog = Join-Path $RegionOutput 'runner64_executor.log'
foreach ($p in @($ExecStdout,$ExecStderr,$ExecLog)) { if (Test-Path $p) { Remove-Item -LiteralPath $p -Force } }
$execArgs = @(
    '-s',(Quote-ProcessArg $RegionExecutor),
    '--comfy-root',(Quote-ProcessArg $ComfyRoot),
    '--workspace',(Quote-ProcessArg $QwenWorkspace),
    '--klein-workspace',(Quote-ProcessArg $KleinWorkspace),
    '--localization-dir',(Quote-ProcessArg $LocalizationGate),
    '--port',"$Port",
    '--timeout-minutes',"$TimeoutMinutes",
    '--comfy-commit',$ComfyCommit
)
$executorExit = 1
try {
    Write-Host 'RUNNER64: launching Qwen2511 regional edit executor...' -ForegroundColor Cyan
    $ep = Start-Process -FilePath $Python -ArgumentList $execArgs -WorkingDirectory $ProjectRepoRoot -RedirectStandardOutput $ExecStdout -RedirectStandardError $ExecStderr -WindowStyle Hidden -PassThru -Wait
    $executorExit = $ep.ExitCode
} finally { Stop-Managed $PidFile }

$stdoutText = Read-TextFileOrEmpty $ExecStdout
$stderrText = Read-TextFileOrEmpty $ExecStderr
Set-Content -LiteralPath $ExecLog -Value (@('=== PYTHON STDOUT ===',$stdoutText,'=== PYTHON STDERR ===',$stderrText) -join [Environment]::NewLine) -Encoding UTF8
Print-TextFile $ExecStdout '--- RUNNER64 REGION STDOUT ---'
if (-not [string]::IsNullOrWhiteSpace($stderrText)) { Print-TextFile $ExecStderr '--- RUNNER64 REGION STDERR ---' 250 }
if ($executorExit -ne 0) {
    Print-TextFile $ComfyStderr '--- COMFYUI STDERR TAIL ---' 350
    Fail "regional edit executor exited with code $executorExit"
}

foreach ($name in @('plank_target_guide.png','plank_raw_crop_edit.png','plank_region_controlled_final.png','strap_target_guide.png','strap_raw_crop_edit.png','strap_region_controlled_final.png','runner64_automatic_region_control_contact_sheet.png','runner64_automatic_region_control_manifest.json','runner64_executor.log')) {
    if (-not (Test-Path (Join-Path $RegionOutput $name) -PathType Leaf)) { Fail "expected regional output missing: $name" }
}

Write-Host ''
Write-Host 'RUNNER64-AUTOMATIC-REGION-CONTROL: PASS - TECHNICAL PIPELINE COMPLETE / VISUAL VERDICT PENDING' -ForegroundColor Green
Write-Host "Localization manifest: $LocalizationManifest" -ForegroundColor Cyan
Write-Host "Contact sheet: $(Join-Path $RegionOutput 'runner64_automatic_region_control_contact_sheet.png')" -ForegroundColor Cyan
Write-Host "Region manifest: $(Join-Path $RegionOutput 'runner64_automatic_region_control_manifest.json')" -ForegroundColor Cyan
Write-Host 'Visual gate: automatic localization must select the intended components, and region-controlled edits must improve exact compliance without any manual mask/box input.' -ForegroundColor Green
