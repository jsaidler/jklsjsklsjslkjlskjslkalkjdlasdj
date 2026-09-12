param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$RuntimeWorkspace = 'Z:\AI\QwenImageEdit',
    [string]$InpaintWorkspace = 'Z:\AI\SDXLInpaint',
    [string]$KleinWorkspace = 'Z:\AI\Flux2Klein',
    [string]$StudioRoot = 'Z:\AI\RogueliteAssetStudio',
    [int]$Port = 8197,
    [int]$TimeoutMinutes = 180
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ComfyCommit = '6eba895f7d3615284da81e95bf49eaed4a5f7309'
$InpaintName = 'sdxl_inpaint_0.1_fp16.safetensors'
$InpaintSha = '6470840731e98cc16713ddf3ac7ee458c9fdbcb881a98c6727cd4a938f227d3f'
$BaseName = 'sd_xl_base_1.0.safetensors'
$BaseSha = '31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b'

function Fail([string]$Message) {
    Write-Host "RUNNER70-SDXL-1024: FAIL - $Message" -ForegroundColor Red
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
$Runner69Manifest = Join-Path $InpaintWorkspace 'runner69_precision_gate\runner69_sdxl_inpaint_manifest.json'
$Runner69Plank = Join-Path $InpaintWorkspace 'runner69_precision_gate\plank_sdxl_region_final.png'
$Runner69Strap = Join-Path $InpaintWorkspace 'runner69_precision_gate\strap_sdxl_region_final.png'
$Executor = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\sdxl_inpaint_1024_parity_gate.py'
$Adapter = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\sdxl_inpaint_adapter.py'
$Protocol = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\adapter_protocol.py'
$SharedAdapter = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\flux2_klein_adapter.py'
$Output = Join-Path $InpaintWorkspace 'runner70_1024_parity_gate'

foreach ($required in @($Python,$MainPy,$Original,$Runner66Manifest,$Runner66Plank,$Runner66Strap,$Runner69Manifest,$Runner69Plank,$Runner69Strap,$Executor,$Adapter,$Protocol,$SharedAdapter)) {
    if (-not (Test-Path $required -PathType Leaf)) { Fail "required prerequisite missing: $required" }
}
Require-Hash $InpaintModel $InpaintSha 'SDXL Inpainting 0.1 FP16 UNet'
Require-Hash $BaseCheckpoint $BaseSha 'SDXL Base 1.0 checkpoint'
$currentCommit = (& git.exe -C $ComfyRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $currentCommit -ne $ComfyCommit) { Fail "shared ComfyUI commit mismatch. Expected $ComfyCommit got $currentCommit" }
Write-Host "  Shared ComfyUI commit verified: $currentCommit" -ForegroundColor Green

$m66 = Get-Content -LiteralPath $Runner66Manifest -Raw | ConvertFrom-Json
if (-not [bool]$m66.auto_geometry_gate_pass) { Fail 'Runner66 automatic geometry gate did not pass' }
if (-not [bool]$m66.atomic_plank_auto_valid) { Fail 'Runner66 atomic plank mask is not auto-valid' }
if (-not [bool]$m66.strap_runner65_auto_valid) { Fail 'Runner66 retained strap mask is not auto-valid' }
$m69 = Get-Content -LiteralPath $Runner69Manifest -Raw | ConvertFrom-Json
if ([string]$m69.technical_status -ne 'COMPLETE') { Fail 'Runner69 technical evidence is not complete' }

New-Item -ItemType Directory -Force -Path $Output | Out-Null

Write-Host ''
Write-Host 'Roguelite Runner 70 - SDXL INPAINTING 0.1 / 1024 TRAINING-RESOLUTION PARITY' -ForegroundColor Cyan
Write-Host '[WHY] Runner69 used 256x512 and 384x256 crops although SDXL Inpainting 0.1 was trained at 1024x1024.' -ForegroundColor Yellow
Write-Host '[ONE VARIABLE] Same model, masks, operation semantics, 30 steps, CFG 6, DPM++ 2M/Karras and seed 0.' -ForegroundColor Green
Write-Host '[SOURCE CONTEXT] Each accepted target is placed in a source-authoritative 512x512 square crop.' -ForegroundColor Green
Write-Host '[MODEL INPUT] Source and mask are scaled together to exactly 1024x1024 before InpaintModelConditioning.' -ForegroundColor Green
Write-Host '[RETURN] Generated 1024 result is downsampled to the exact 512 source crop then deterministically composited.' -ForegroundColor Green
Write-Host '[NO DOWNLOAD] Reuses the verified Runner69 SDXL Inpaint + Base payload.' -ForegroundColor Green
Write-Host '[NO MANUAL MASKS] Runner66 automatic masks remain authoritative.' -ForegroundColor Green
Write-Host ''

$Base = "http://127.0.0.1:$Port"
$PidFile = Join-Path $InpaintWorkspace '.sdxl_inpaint_runner70.pid'
$ComfyStdout = Join-Path $Output "comfyui_runner70_${Port}_stdout.log"
$ComfyStderr = Join-Path $Output "comfyui_runner70_${Port}_stderr.log"
Stop-Managed $PidFile
$portBusy = $false
try { $null = Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 2; $portBusy = $true } catch { }
if ($portBusy) { Fail "port $Port already serves an unmanaged process" }

$env:PYTORCH_CUDA_ALLOC_CONF = 'expandable_segments:True'
$launchArgs = @('-s',$MainPy,'--windows-standalone-build','--listen','127.0.0.1','--port',"$Port",'--disable-auto-launch','--lowvram','--reserve-vram','1.0')
$process = Start-Process -FilePath $Python -ArgumentList $launchArgs -WorkingDirectory $ComfyRoot -RedirectStandardOutput $ComfyStdout -RedirectStandardError $ComfyStderr -WindowStyle Hidden -PassThru
Set-Content -LiteralPath $PidFile -Value $process.Id -Encoding ASCII
Write-Host "Started shared pinned ComfyUI PID $($process.Id) for SDXL 1024 parity on port $Port" -ForegroundColor Green

$ready = $false
for ($i=0; $i -lt 360; $i++) {
    try { $null = Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 2; $ready=$true; break }
    catch {
        if ($process.HasExited) { Print-TextFile $ComfyStderr '--- COMFYUI STDERR ---' 300; Stop-Managed $PidFile; Fail "ComfyUI exited before readiness: $($process.ExitCode)" }
        Start-Sleep -Seconds 1
    }
}
if (-not $ready) { Print-TextFile $ComfyStderr '--- COMFYUI STDERR ---' 300; Stop-Managed $PidFile; Fail 'ComfyUI did not become ready' }

$ExecStdout = Join-Path $Output 'runner70_python_stdout.log'
$ExecStderr = Join-Path $Output 'runner70_python_stderr.log'
$ExecLog = Join-Path $Output 'runner70_executor.log'
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
    Write-Host 'RUNNER70: launching SDXL 1024 parity executor...' -ForegroundColor Cyan
    $ep = Start-Process -FilePath $Python -ArgumentList $execArgs -WorkingDirectory $ProjectRepoRoot -RedirectStandardOutput $ExecStdout -RedirectStandardError $ExecStderr -WindowStyle Hidden -PassThru -Wait
    $executorExit = $ep.ExitCode
} finally { Stop-Managed $PidFile }

$stdoutText = Read-TextFileOrEmpty $ExecStdout
$stderrText = Read-TextFileOrEmpty $ExecStderr
Set-Content -LiteralPath $ExecLog -Value (@('=== PYTHON STDOUT ===',$stdoutText,'=== PYTHON STDERR ===',$stderrText) -join [Environment]::NewLine) -Encoding UTF8
Print-TextFile $ExecStdout '--- RUNNER70 PYTHON STDOUT ---'
if (-not [string]::IsNullOrWhiteSpace($stderrText)) { Print-TextFile $ExecStderr '--- RUNNER70 PYTHON STDERR ---' 250 }
if ($executorExit -ne 0) {
    Print-TextFile $ComfyStderr '--- COMFYUI STDERR TAIL ---' 350
    Fail "SDXL 1024 parity executor exited with code $executorExit"
}

foreach ($name in @(
    'plank_source_context_512.png','plank_model_source_1024.png','plank_inpaint_mask_1024.png','plank_approved_target_overlay.png','plank_sdxl_1024_raw.png','plank_sdxl_1024_downsampled_512.png','plank_sdxl_1024_region_final.png','plank_allowed_region.png',
    'strap_source_context_512.png','strap_model_source_1024.png','strap_inpaint_mask_1024.png','strap_approved_target_overlay.png','strap_sdxl_1024_raw.png','strap_sdxl_1024_downsampled_512.png','strap_sdxl_1024_region_final.png','strap_allowed_region.png',
    'runner70_sdxl_1024_contact_sheet.png','runner70_sdxl_1024_manifest.json','runner70_executor.log'
)) {
    if (-not (Test-Path (Join-Path $Output $name) -PathType Leaf)) { Fail "expected Runner70 output missing: $name" }
}

Write-Host ''
Write-Host 'RUNNER70-SDXL-1024: PASS - TECHNICAL RESOLUTION-PARITY MATRIX COMPLETE / VISUAL VERDICT PENDING' -ForegroundColor Green
Write-Host "Contact sheet: $(Join-Path $Output 'runner70_sdxl_1024_contact_sheet.png')" -ForegroundColor Cyan
Write-Host "Manifest: $(Join-Path $Output 'runner70_sdxl_1024_manifest.json')" -ForegroundColor Cyan
Write-Host "Executor log: $ExecLog" -ForegroundColor Cyan
Write-Host 'Visual gate: 1024 parity must remove the one plank as an opening and remove only the strap center without Runner69 shiny artifacts. If not, SDXL Inpainting is exhausted for this precision role.' -ForegroundColor Green
