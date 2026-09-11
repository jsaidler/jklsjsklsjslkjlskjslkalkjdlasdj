param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$RuntimeWorkspace = 'Z:\AI\QwenImageEdit',
    [string]$InpaintWorkspace = 'Z:\AI\SDXLInpaint',
    [string]$KleinWorkspace = 'Z:\AI\Flux2Klein',
    [string]$StudioRoot = 'Z:\AI\RogueliteAssetStudio',
    [int]$Port = 8196,
    [int]$TimeoutMinutes = 180
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ComfyCommit = '6eba895f7d3615284da81e95bf49eaed4a5f7309'

$InpaintName = 'sdxl_inpaint_0.1_fp16.safetensors'
$InpaintUrl = 'https://huggingface.co/diffusers/stable-diffusion-xl-1.0-inpainting-0.1/resolve/main/unet/diffusion_pytorch_model.fp16.safetensors'
$InpaintSha = '6470840731e98cc16713ddf3ac7ee458c9fdbcb881a98c6727cd4a938f227d3f'
$InpaintApproxBytes = [int64]5520000000

$BaseName = 'sd_xl_base_1.0.safetensors'
$BaseUrl = 'https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors'
$BaseSha = '31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b'
$BaseApproxBytes = [int64]7460000000

function Fail([string]$Message) {
    Write-Host "RUNNER69-SDXL-INPAINT: FAIL - $Message" -ForegroundColor Red
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
function Download-Verified([string]$Url,[string]$Destination,[string]$Expected,[string]$Label) {
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Destination) | Out-Null
    if (Test-Path $Destination -PathType Leaf) {
        $actual = Get-Sha256 $Destination
        if ($actual -eq $Expected.ToLowerInvariant()) {
            Write-Host "  $Label already present and verified." -ForegroundColor Green
            return
        }
        Remove-Item -LiteralPath $Destination -Force
    }
    $partial = "$Destination.part"
    $curl = Get-Command curl.exe -ErrorAction SilentlyContinue
    if (-not $curl) { Fail 'curl.exe is required.' }
    Write-Host "Downloading $Label" -ForegroundColor Cyan
    Write-Host "  $Url" -ForegroundColor DarkGray
    & $curl.Source '--fail' '--location' '--retry' '10' '--retry-delay' '5' '--retry-all-errors' '--continue-at' '-' '--output' $partial $Url
    if ($LASTEXITCODE -ne 0) { Fail "$Label download failed. Partial retained: $partial" }
    Move-Item -LiteralPath $partial -Destination $Destination -Force
    Require-Hash $Destination $Expected $Label
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

$PortableRoot = Join-Path $RuntimeWorkspace 'ComfyUI_windows_portable'
$Python = Join-Path $PortableRoot 'python_embeded\python.exe'
$ComfyRoot = Join-Path $PortableRoot 'ComfyUI'
$MainPy = Join-Path $ComfyRoot 'main.py'
$InpaintModel = Join-Path $ComfyRoot "models\diffusion_models\$InpaintName"
$BaseCheckpoint = Join-Path $ComfyRoot "models\checkpoints\$BaseName"
$Original = Join-Path $KleinWorkspace 'spike\flux2_klein_4b_t2i_probe.png'
$Runner66Dir = Join-Path $StudioRoot 'localization\runner66_gate'
$Runner66Manifest = Join-Path $Runner66Dir 'runner66_repeated_element_manifest.json'
$Runner66Plank = Join-Path $Runner66Dir 'plank_atomic_mask.png'
$Runner66Strap = Join-Path $Runner66Dir 'strap_retained_mask.png'
$Runner68Manifest = Join-Path $RuntimeWorkspace 'runner68_latent_mask_region_edit\runner68_latent_mask_manifest.json'
$Runner68Plank = Join-Path $RuntimeWorkspace 'runner68_latent_mask_region_edit\plank_latent_mask_region_final.png'
$Runner68Strap = Join-Path $RuntimeWorkspace 'runner68_latent_mask_region_edit\strap_latent_mask_region_final.png'
$Executor = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\sdxl_inpaint_region_gate.py'
$Adapter = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\sdxl_inpaint_adapter.py'
$Protocol = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\adapter_protocol.py'
$SharedAdapter = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\flux2_klein_adapter.py'
$Output = Join-Path $InpaintWorkspace 'runner69_precision_gate'

foreach ($required in @($Python,$MainPy,$Original,$Runner66Manifest,$Runner66Plank,$Runner66Strap,$Runner68Manifest,$Runner68Plank,$Runner68Strap,$Executor,$Adapter,$Protocol,$SharedAdapter)) {
    if (-not (Test-Path $required -PathType Leaf)) { Fail "required prerequisite missing: $required" }
}

$currentCommit = (& git.exe -C $ComfyRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $currentCommit -ne $ComfyCommit) { Fail "shared ComfyUI commit mismatch. Expected $ComfyCommit got $currentCommit" }
Write-Host "  Shared ComfyUI commit verified: $currentCommit" -ForegroundColor Green

$m66 = Get-Content -LiteralPath $Runner66Manifest -Raw | ConvertFrom-Json
if (-not [bool]$m66.auto_geometry_gate_pass) { Fail 'Runner66 automatic geometry gate did not pass' }
if (-not [bool]$m66.atomic_plank_auto_valid) { Fail 'Runner66 atomic plank mask is not auto-valid' }
if (-not [bool]$m66.strap_runner65_auto_valid) { Fail 'Runner66 retained strap mask is not auto-valid' }
$m68 = Get-Content -LiteralPath $Runner68Manifest -Raw | ConvertFrom-Json
if ([string]$m68.technical_status -ne 'COMPLETE') { Fail 'Runner68 evidence is not technically complete' }

New-Item -ItemType Directory -Force -Path $Output | Out-Null

Write-Host ''
Write-Host 'Roguelite Runner 69 - SDXL INPAINTING 0.1 / DEDICATED MASK-NATIVE PRECISION' -ForegroundColor Cyan
Write-Host '[WHY] Runner68 proved automatic masks + native containment but Qwen2511 remained semantically near-no-op inside the mask.' -ForegroundColor Yellow
Write-Host '[EDITOR CHANGE ONLY] Perception, Runner66 masks, operation semantics and deterministic final compositor remain authoritative.' -ForegroundColor Green
Write-Host '[DEDICATED MODEL] SDXL Inpainting 0.1 FP16 UNet is explicitly trained for mask-native inpainting.' -ForegroundColor Green
Write-Host '[CLIP/VAE] SDXL Base 1.0 checkpoint is loaded only as CLIP/VAE authority; its base MODEL output is unused.' -ForegroundColor Green
Write-Host '[PAYLOAD] Approximately 12.1 GB new weights total; resumable downloads + SHA256 verification.' -ForegroundColor Green
Write-Host '[LICENSE] CreativeML Open RAIL++-M; retain license/use-restriction review in production provenance.' -ForegroundColor Green
Write-Host '[NO MANUAL MASKS] Uses accepted Runner66 automatic masks only.' -ForegroundColor Green
Write-Host ''

$missingBytes = [int64]0
if (-not (Test-Path $InpaintModel -PathType Leaf)) { $missingBytes += $InpaintApproxBytes }
if (-not (Test-Path $BaseCheckpoint -PathType Leaf)) { $missingBytes += $BaseApproxBytes }
$driveRoot = [System.IO.Path]::GetPathRoot($InpaintWorkspace)
$driveInfo = [System.IO.DriveInfo]::new($driveRoot)
$freeBytes = [int64]$driveInfo.AvailableFreeSpace
$requiredFree = $missingBytes + [int64](5GB)
Write-Host ("Disk preflight: free={0:N2} GiB; required~={1:N2} GiB." -f ($freeBytes/1GB),($requiredFree/1GB)) -ForegroundColor Cyan
if ($freeBytes -lt $requiredFree) { Fail 'insufficient free space for missing SDXL inpaint payload plus runtime margin.' }

Download-Verified $InpaintUrl $InpaintModel $InpaintSha 'SDXL Inpainting 0.1 FP16 UNet (~5.14 GB)'
Download-Verified $BaseUrl $BaseCheckpoint $BaseSha 'SDXL Base 1.0 checkpoint (~6.94 GB; CLIP/VAE source)'

$Base = "http://127.0.0.1:$Port"
$PidFile = Join-Path $InpaintWorkspace '.sdxl_inpaint_runner69.pid'
$ComfyStdout = Join-Path $Output "comfyui_runner69_${Port}_stdout.log"
$ComfyStderr = Join-Path $Output "comfyui_runner69_${Port}_stderr.log"
Stop-Managed $PidFile
$portBusy = $false
try { $null = Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 2; $portBusy = $true } catch { }
if ($portBusy) { Fail "port $Port already serves an unmanaged process" }

$env:PYTORCH_CUDA_ALLOC_CONF = 'expandable_segments:True'
$launchArgs = @('-s',$MainPy,'--windows-standalone-build','--listen','127.0.0.1','--port',"$Port",'--disable-auto-launch','--lowvram','--reserve-vram','1.0')
$process = Start-Process -FilePath $Python -ArgumentList $launchArgs -WorkingDirectory $ComfyRoot -RedirectStandardOutput $ComfyStdout -RedirectStandardError $ComfyStderr -WindowStyle Hidden -PassThru
Set-Content -LiteralPath $PidFile -Value $process.Id -Encoding ASCII
Write-Host "Started shared pinned ComfyUI PID $($process.Id) for SDXL Inpaint on port $Port" -ForegroundColor Green

$ready = $false
for ($i=0; $i -lt 360; $i++) {
    try { $null = Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 2; $ready=$true; break }
    catch {
        if ($process.HasExited) { Print-TextFile $ComfyStderr '--- COMFYUI STDERR ---' 300; Stop-Managed $PidFile; Fail "ComfyUI exited before readiness: $($process.ExitCode)" }
        Start-Sleep -Seconds 1
    }
}
if (-not $ready) { Print-TextFile $ComfyStderr '--- COMFYUI STDERR ---' 300; Stop-Managed $PidFile; Fail 'ComfyUI did not become ready' }

$ExecStdout = Join-Path $Output 'runner69_python_stdout.log'
$ExecStderr = Join-Path $Output 'runner69_python_stderr.log'
$ExecLog = Join-Path $Output 'runner69_executor.log'
foreach ($p in @($ExecStdout,$ExecStderr,$ExecLog)) { if (Test-Path $p) { Remove-Item -LiteralPath $p -Force } }
$execArgs = @(
    '-s',(Quote-ProcessArg $Executor),
    '--comfy-root',(Quote-ProcessArg $ComfyRoot),
    '--workspace',(Quote-ProcessArg $InpaintWorkspace),
    '--qwen-workspace',(Quote-ProcessArg $RuntimeWorkspace),
    '--klein-workspace',(Quote-ProcessArg $KleinWorkspace),
    '--runner66-dir',(Quote-ProcessArg $Runner66Dir),
    '--port',"$Port",
    '--timeout-minutes',"$TimeoutMinutes",
    '--comfy-commit',$ComfyCommit
)
$executorExit = 1
try {
    Write-Host 'RUNNER69: launching dedicated SDXL inpaint executor...' -ForegroundColor Cyan
    $ep = Start-Process -FilePath $Python -ArgumentList $execArgs -WorkingDirectory $ProjectRepoRoot -RedirectStandardOutput $ExecStdout -RedirectStandardError $ExecStderr -WindowStyle Hidden -PassThru -Wait
    $executorExit = $ep.ExitCode
} finally { Stop-Managed $PidFile }

$stdoutText = Read-TextFileOrEmpty $ExecStdout
$stderrText = Read-TextFileOrEmpty $ExecStderr
Set-Content -LiteralPath $ExecLog -Value (@('=== PYTHON STDOUT ===',$stdoutText,'=== PYTHON STDERR ===',$stderrText) -join [Environment]::NewLine) -Encoding UTF8
Print-TextFile $ExecStdout '--- RUNNER69 PYTHON STDOUT ---'
if (-not [string]::IsNullOrWhiteSpace($stderrText)) { Print-TextFile $ExecStderr '--- RUNNER69 PYTHON STDERR ---' 250 }
if ($executorExit -ne 0) {
    Print-TextFile $ComfyStderr '--- COMFYUI STDERR TAIL ---' 350
    Fail "SDXL inpaint executor exited with code $executorExit"
}

foreach ($name in @(
    'plank_source_crop.png','plank_inpaint_mask.png','plank_approved_target_overlay.png','plank_inpaint_operation_overlay.png','plank_sdxl_raw_crop.png','plank_sdxl_region_final.png','plank_allowed_region.png',
    'strap_source_crop.png','strap_inpaint_mask.png','strap_approved_target_overlay.png','strap_inpaint_operation_overlay.png','strap_sdxl_raw_crop.png','strap_sdxl_region_final.png','strap_allowed_region.png',
    'runner69_sdxl_inpaint_contact_sheet.png','runner69_sdxl_inpaint_manifest.json','runner69_executor.log'
)) {
    if (-not (Test-Path (Join-Path $Output $name) -PathType Leaf)) { Fail "expected Runner69 output missing: $name" }
}

Write-Host ''
Write-Host 'RUNNER69-SDXL-INPAINT: PASS - TECHNICAL MASK-NATIVE MATRIX COMPLETE / VISUAL VERDICT PENDING' -ForegroundColor Green
Write-Host "Contact sheet: $(Join-Path $Output 'runner69_sdxl_inpaint_contact_sheet.png')" -ForegroundColor Cyan
Write-Host "Manifest: $(Join-Path $Output 'runner69_sdxl_inpaint_manifest.json')" -ForegroundColor Cyan
Write-Host "Executor log: $ExecLog" -ForegroundColor Cyan
Write-Host 'Visual gate: plank must become a true narrow opening; strap middle must disappear and reveal coherent wood while both ends remain; unrelated geometry stays source-authoritative.' -ForegroundColor Green
