param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$QwenWorkspace = 'Z:\AI\QwenImageEdit',
    [string]$KleinWorkspace = 'Z:\AI\Flux2Klein',
    [string]$StudioRoot = 'Z:\AI\RogueliteAssetStudio',
    [int]$Port = 8194,
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
    Write-Host "RUNNER67-QWEN2511-ATOMIC-REGION: FAIL - $Message" -ForegroundColor Red
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

$PortableRoot = Join-Path $QwenWorkspace 'ComfyUI_windows_portable'
$Python = Join-Path $PortableRoot 'python_embeded\python.exe'
$ComfyRoot = Join-Path $PortableRoot 'ComfyUI'
$MainPy = Join-Path $ComfyRoot 'main.py'
$QwenModel = Join-Path $ComfyRoot "models\diffusion_models\$QwenModelName"
$TextEncoder = Join-Path $ComfyRoot "models\text_encoders\$TextEncoderName"
$Vae = Join-Path $ComfyRoot "models\vae\$VaeName"
$Original = Join-Path $KleinWorkspace 'spike\flux2_klein_4b_t2i_probe.png'
$Runner66Dir = Join-Path $StudioRoot 'localization\runner66_gate'
$Runner66Manifest = Join-Path $Runner66Dir 'runner66_repeated_element_manifest.json'
$Runner66Plank = Join-Path $Runner66Dir 'plank_atomic_mask.png'
$Runner66Strap = Join-Path $Runner66Dir 'strap_retained_mask.png'
$Runner63Plank = Join-Path $QwenWorkspace 'qwen2511_precision_gate\qwen2511_atomic_plank_steps20.png'
$Runner63Strap = Join-Path $QwenWorkspace 'qwen2511_precision_gate\qwen2511_atomic_strap_steps20.png'
$Executor = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\qwen2511_atomic_region_gate.py'
$QwenAdapter = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\qwen_image_edit_2511_adapter.py'
$Protocol = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\adapter_protocol.py'
$SharedAdapter = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\flux2_klein_adapter.py'
$Output = Join-Path $QwenWorkspace 'runner67_atomic_region_edit'

foreach ($required in @($Python,$MainPy,$Original,$Runner66Manifest,$Runner66Plank,$Runner66Strap,$Runner63Plank,$Runner63Strap,$Executor,$QwenAdapter,$Protocol,$SharedAdapter)) {
    if (-not (Test-Path $required -PathType Leaf)) { Fail "required prerequisite missing: $required" }
}
Require-Hash $QwenModel $QwenModelSha 'Qwen-Image-Edit-2511 FP8mixed'
Require-Hash $TextEncoder $TextEncoderSha 'Qwen2.5-VL 7B FP8 encoder'
Require-Hash $Vae $VaeSha 'Qwen image VAE'
$currentCommit = (& git.exe -C $ComfyRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $currentCommit -ne $ComfyCommit) { Fail "Qwen ComfyUI commit mismatch. Expected $ComfyCommit got $currentCommit" }
Write-Host "  Qwen ComfyUI commit verified: $currentCommit" -ForegroundColor Green

$m66 = Get-Content -LiteralPath $Runner66Manifest -Raw | ConvertFrom-Json
if (-not [bool]$m66.auto_geometry_gate_pass) { Fail 'Runner66 automatic geometry gate did not pass' }
if (-not [bool]$m66.atomic_plank_auto_valid) { Fail 'Runner66 atomic plank mask is not auto-valid' }
if (-not [bool]$m66.strap_runner65_auto_valid) { Fail 'Runner66 retained strap mask is not auto-valid' }

New-Item -ItemType Directory -Force -Path $Output | Out-Null

Write-Host ''
Write-Host 'Roguelite Runner 67 - QWEN2511 / APPROVED AUTOMATIC ATOMIC REGION EDIT' -ForegroundColor Cyan
Write-Host '[WHY] Runner66 visually isolated one plank and retained the correct lower-right strap without manual masks.' -ForegroundColor Yellow
Write-Host '[NO PERCEPTION] Grounding DINO/SAM2 are not rerun; this gate consumes approved Runner66 evidence only.' -ForegroundColor Green
Write-Host '[EDITOR] Reuses installed Qwen-Image-Edit-2511 FP8mixed at the proven 20-step recipe.' -ForegroundColor Green
Write-Host '[CONTROL] Qwen receives a contextual crop + automatic red target guide; final full image is deterministically constrained to the automatic mask neighborhood.' -ForegroundColor Green
Write-Host '[NO DOWNLOAD] No new model or dependency download is expected.' -ForegroundColor Green
Write-Host '[NO MANUAL MASKS] User-drawn masks/boxes are not accepted.' -ForegroundColor Green
Write-Host ''

$Base = "http://127.0.0.1:$Port"
$PidFile = Join-Path $QwenWorkspace '.qwen2511_runner67.pid'
$ComfyStdout = Join-Path $Output "comfyui_runner67_${Port}_stdout.log"
$ComfyStderr = Join-Path $Output "comfyui_runner67_${Port}_stderr.log"
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

$ExecStdout = Join-Path $Output 'runner67_python_stdout.log'
$ExecStderr = Join-Path $Output 'runner67_python_stderr.log'
$ExecLog = Join-Path $Output 'runner67_executor.log'
foreach ($p in @($ExecStdout,$ExecStderr,$ExecLog)) { if (Test-Path $p) { Remove-Item -LiteralPath $p -Force } }
$execArgs = @(
    '-s',(Quote-ProcessArg $Executor),
    '--comfy-root',(Quote-ProcessArg $ComfyRoot),
    '--workspace',(Quote-ProcessArg $QwenWorkspace),
    '--klein-workspace',(Quote-ProcessArg $KleinWorkspace),
    '--runner66-dir',(Quote-ProcessArg $Runner66Dir),
    '--port',"$Port",
    '--timeout-minutes',"$TimeoutMinutes",
    '--comfy-commit',$ComfyCommit
)
$executorExit = 1
try {
    Write-Host 'RUNNER67: launching Qwen2511 atomic regional executor...' -ForegroundColor Cyan
    $ep = Start-Process -FilePath $Python -ArgumentList $execArgs -WorkingDirectory $ProjectRepoRoot -RedirectStandardOutput $ExecStdout -RedirectStandardError $ExecStderr -WindowStyle Hidden -PassThru -Wait
    $executorExit = $ep.ExitCode
} finally { Stop-Managed $PidFile }

$stdoutText = Read-TextFileOrEmpty $ExecStdout
$stderrText = Read-TextFileOrEmpty $ExecStderr
Set-Content -LiteralPath $ExecLog -Value (@('=== PYTHON STDOUT ===',$stdoutText,'=== PYTHON STDERR ===',$stderrText) -join [Environment]::NewLine) -Encoding UTF8
Print-TextFile $ExecStdout '--- RUNNER67 PYTHON STDOUT ---'
if (-not [string]::IsNullOrWhiteSpace($stderrText)) { Print-TextFile $ExecStderr '--- RUNNER67 PYTHON STDERR ---' 250 }
if ($executorExit -ne 0) {
    Print-TextFile $ComfyStderr '--- COMFYUI STDERR TAIL ---' 350
    Fail "atomic regional executor exited with code $executorExit"
}

foreach ($name in @(
    'plank_source_crop.png','plank_crop_mask.png','plank_approved_mask_overlay.png','plank_target_guide.png','plank_raw_crop_edit.png','plank_atomic_region_final.png','plank_allowed_region.png',
    'strap_source_crop.png','strap_crop_mask.png','strap_approved_mask_overlay.png','strap_target_guide.png','strap_raw_crop_edit.png','strap_atomic_region_final.png','strap_allowed_region.png',
    'runner67_atomic_region_contact_sheet.png','runner67_atomic_region_manifest.json','runner67_executor.log'
)) {
    if (-not (Test-Path (Join-Path $Output $name) -PathType Leaf)) { Fail "expected Runner67 output missing: $name" }
}

Write-Host ''
Write-Host 'RUNNER67-QWEN2511-ATOMIC-REGION: PASS - TECHNICAL EDIT MATRIX COMPLETE / VISUAL VERDICT PENDING' -ForegroundColor Green
Write-Host "Contact sheet: $(Join-Path $Output 'runner67_atomic_region_contact_sheet.png')" -ForegroundColor Cyan
Write-Host "Manifest: $(Join-Path $Output 'runner67_atomic_region_manifest.json')" -ForegroundColor Cyan
Write-Host "Executor log: $ExecLog" -ForegroundColor Cyan
Write-Host 'Visual gate: plank must become one narrow same-width opening; strap must break only inside the approved lower-right region; unrelated geometry must remain unchanged.' -ForegroundColor Green
