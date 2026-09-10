param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$Workspace = 'Z:\AI\QwenImageEdit',
    [string]$KleinWorkspace = 'Z:\AI\Flux2Klein',
    [int]$Port = 8193,
    [int]$TimeoutMinutes = 480
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ComfyCommit = '6eba895f7d3615284da81e95bf49eaed4a5f7309'
$ComfyRepo = 'https://github.com/Comfy-Org/ComfyUI.git'

$ModelName = 'qwen_image_edit_2511_fp8mixed.safetensors'
$ModelUrl = 'https://huggingface.co/Comfy-Org/Qwen-Image-Edit_ComfyUI/resolve/main/split_files/diffusion_models/qwen_image_edit_2511_fp8mixed.safetensors'
$ModelSha256 = 'c9fdc158e46d3b61ef75f21ae866ca2fe808bf4a53643120d1c1e87c19280a4e'
$ModelBytes = [int64]20533762817

$OldModelName = 'qwen_image_edit_2509_fp8_e4m3fn.safetensors'
$OldModelSha256 = '318568f61951ab9da21100c7b896e3c1da67f0d2efad6421545e022cfaa2b2b4'

$TextEncoderName = 'qwen_2.5_vl_7b_fp8_scaled.safetensors'
$TextEncoderSha256 = 'cb5636d852a0ea6a9075ab1bef496c0db7aef13c02350571e388aea959c5c0b4'
$VaeName = 'qwen_image_vae.safetensors'
$VaeSha256 = 'a70580f0213e67967ee9c95f05bb400e8fb08307e017a924bf3441223e023d1f'

function Fail([string]$Message) {
    Write-Host "RUNNER63-QWEN2511: FAIL - $Message" -ForegroundColor Red
    exit 1
}
function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}
function Require-Hash([string]$Path,[string]$Expected,[string]$Label) {
    if (-not (Test-Path $Path -PathType Leaf)) { Fail "required $Label missing: $Path" }
    $actual = Get-Sha256 $Path
    if ($actual -ne $Expected.ToLowerInvariant()) { Fail "$Label SHA256 mismatch. Expected $Expected, got $actual" }
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
    & $curl.Source '--fail' '--location' '--retry' '8' '--retry-delay' '5' '--retry-all-errors' '--continue-at' '-' '--output' $partial $Url
    if ($LASTEXITCODE -ne 0) { Fail "$Label download failed. Partial retained: $partial" }
    Move-Item -LiteralPath $partial -Destination $Destination -Force
    Require-Hash $Destination $Expected $Label
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
function Invoke-Git([string[]]$GitArgs,[string]$Failure) {
    & git.exe @GitArgs
    if ($LASTEXITCODE -ne 0) { Fail "$Failure (git exit $LASTEXITCODE)" }
}

$PortableRoot = Join-Path $Workspace 'ComfyUI_windows_portable'
$Python = Join-Path $PortableRoot 'python_embeded\python.exe'
$ComfyRoot = Join-Path $PortableRoot 'ComfyUI'
$MainPy = Join-Path $ComfyRoot 'main.py'
$Executor = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\qwen_image_edit_2511_precision_gate.py'
$Adapter = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\qwen_image_edit_2511_adapter.py'
$Protocol = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\adapter_protocol.py'
$SharedHelper = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\flux2_klein_adapter.py'
$Runner62Manifest = Join-Path $Workspace 'feasibility_gate\runner62_qwen2509_manifest.json'
$Runner62Plank = Join-Path $Workspace 'feasibility_gate\qwen2509_atomic_plank.png'
$Runner62Strap = Join-Path $Workspace 'feasibility_gate\qwen2509_atomic_strap.png'
$KleinOriginal = Join-Path $KleinWorkspace 'spike\flux2_klein_4b_t2i_probe.png'
$KleinPlank = Join-Path $KleinWorkspace 'base_atomic_sequence\atomic_plank.png'
$KleinStrap = Join-Path $KleinWorkspace 'base_atomic_sequence\atomic_strap.png'

foreach ($required in @($Python,$Executor,$Adapter,$Protocol,$SharedHelper,$Runner62Manifest,$Runner62Plank,$Runner62Strap,$KleinOriginal,$KleinPlank,$KleinStrap)) {
    if (-not (Test-Path $required -PathType Leaf)) { Fail "required prerequisite missing: $required" }
}
if (-not (Get-Command git.exe -ErrorAction SilentlyContinue)) { Fail 'git.exe is required.' }

$ModelPath = Join-Path $ComfyRoot "models\diffusion_models\$ModelName"
$OldModelPath = Join-Path $ComfyRoot "models\diffusion_models\$OldModelName"
$TextEncoderPath = Join-Path $ComfyRoot "models\text_encoders\$TextEncoderName"
$VaePath = Join-Path $ComfyRoot "models\vae\$VaeName"
$OutputDir = Join-Path $Workspace 'qwen2511_precision_gate'
$PidFile = Join-Path $Workspace '.qwen2511_runner63.pid'
$DepsMarker = Join-Path $PortableRoot ".deps_$ComfyCommit.ok"
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

Write-Host ''
Write-Host 'Roguelite Runner 63 - QWEN-IMAGE-EDIT-2511 FP8MIXED / ATOMIC PRECISION' -ForegroundColor Cyan
Write-Host '[WHY] Runner62 proved Qwen 2509 feasible and conservative, but it still failed exact one-plank / one-strap compliance.' -ForegroundColor Yellow
Write-Host '[2511] Tests the official enhanced Qwen editor branch with stronger consistency/geometric reasoning.' -ForegroundColor Green
Write-Host '[REUSE] Existing Qwen2.5-VL 7B encoder + Qwen image VAE are reused.' -ForegroundColor Green
Write-Host '[MODEL] Only the 20.53 GB 2511 FP8mixed diffusion checkpoint is new.' -ForegroundColor Green
Write-Host '[CLEANUP] Runner62 evidence is preserved; rejected 2509 diffusion checkpoint is removed to avoid model accumulation.' -ForegroundColor Green
Write-Host '[MATRIX] one-plank and one-strap atomic edits at 20 and 40 steps.' -ForegroundColor Green
Write-Host ''

Require-Hash $TextEncoderPath $TextEncoderSha256 'Qwen2.5-VL 7B FP8 encoder'
Require-Hash $VaePath $VaeSha256 'Qwen image VAE'

# Retire the rejected 2509 diffusion payload only after its evidence is confirmed present.
if (Test-Path $OldModelPath -PathType Leaf) {
    $oldHash = Get-Sha256 $OldModelPath
    if ($oldHash -ne $OldModelSha256) { Fail "old Qwen2509 checkpoint exists but hash is unexpected; refusing cleanup: $OldModelPath" }
    Write-Host 'Removing rejected Qwen-Image-Edit-2509 diffusion checkpoint after preserved Runner62 evidence...' -ForegroundColor Yellow
    Remove-Item -LiteralPath $OldModelPath -Force
    Write-Host '  Qwen2509 diffusion payload removed; manifest and generated evidence retained.' -ForegroundColor Green
}

$driveRoot = [System.IO.Path]::GetPathRoot($Workspace)
$driveInfo = [System.IO.DriveInfo]::new($driveRoot)
$freeBytes = [int64]$driveInfo.AvailableFreeSpace
$requiredFree = $ModelBytes + [int64](5GB)
Write-Host ("Disk preflight: free={0:N2} GiB; required={1:N2} GiB." -f ($freeBytes/1GB),($requiredFree/1GB)) -ForegroundColor Cyan
if ($freeBytes -lt $requiredFree) { Fail 'insufficient free space for Qwen2511 checkpoint plus runtime margin.' }

if (-not (Test-Path (Join-Path $ComfyRoot '.git') -PathType Container)) { Fail "existing isolated Qwen ComfyUI checkout missing: $ComfyRoot" }
Write-Host "Pinning Qwen2511 ComfyUI to $ComfyCommit" -ForegroundColor Cyan
Invoke-Git -GitArgs @('-C',$ComfyRoot,'fetch','--depth','1','origin',$ComfyCommit) -Failure 'ComfyUI fetch failed'
Invoke-Git -GitArgs @('-C',$ComfyRoot,'checkout','--detach','--force',$ComfyCommit) -Failure 'ComfyUI checkout failed'
$currentCommit = (& git.exe -C $ComfyRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $currentCommit -ne $ComfyCommit) { Fail "ComfyUI commit mismatch. Expected $ComfyCommit got $currentCommit" }

if (-not (Test-Path $DepsMarker -PathType Leaf)) {
    Write-Host 'Installing dependencies required by the pinned Qwen2511 ComfyUI commit...' -ForegroundColor Cyan
    & $Python -s -m pip install --disable-pip-version-check -r (Join-Path $ComfyRoot 'requirements.txt')
    if ($LASTEXITCODE -ne 0) { Fail 'ComfyUI dependency installation failed' }
    Set-Content -LiteralPath $DepsMarker -Value $ComfyCommit -Encoding ASCII
} else {
    Write-Host '  Dependency marker already present.' -ForegroundColor Green
}

Download-Verified $ModelUrl $ModelPath $ModelSha256 'Qwen-Image-Edit-2511 FP8mixed (20.53 GB)'

$Base = "http://127.0.0.1:$Port"
$StdoutLog = Join-Path $OutputDir "comfyui_runner63_${Port}_stdout.log"
$StderrLog = Join-Path $OutputDir "comfyui_runner63_${Port}_stderr.log"
$ExecutorStdout = Join-Path $OutputDir 'runner63_python_stdout.log'
$ExecutorStderr = Join-Path $OutputDir 'runner63_python_stderr.log'
$ExecutorLog = Join-Path $OutputDir 'runner63_executor.log'

Stop-Managed $PidFile
try { $null = Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 2; Fail "port $Port already serves an unmanaged process" } catch { }

$env:PYTORCH_CUDA_ALLOC_CONF = 'expandable_segments:True'
$launchArgs = @('-s',$MainPy,'--windows-standalone-build','--listen','127.0.0.1','--port',"$Port",'--disable-auto-launch','--lowvram','--reserve-vram','1.0')
$process = Start-Process -FilePath $Python -ArgumentList $launchArgs -WorkingDirectory $ComfyRoot -RedirectStandardOutput $StdoutLog -RedirectStandardError $StderrLog -WindowStyle Hidden -PassThru
Set-Content -LiteralPath $PidFile -Value $process.Id -Encoding ASCII
Write-Host "Started isolated Qwen2511 ComfyUI PID $($process.Id) on port $Port" -ForegroundColor Green

$ready = $false
for ($i=0; $i -lt 360; $i++) {
    try { $null = Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 2; $ready=$true; break }
    catch {
        if ($process.HasExited) { Print-TextFile $StderrLog '--- COMFYUI STDERR ---' 300; Stop-Managed $PidFile; Fail "ComfyUI exited before readiness: $($process.ExitCode)" }
        Start-Sleep -Seconds 1
    }
}
if (-not $ready) { Print-TextFile $StderrLog '--- COMFYUI STDERR ---' 300; Stop-Managed $PidFile; Fail 'ComfyUI did not become ready.' }

foreach ($old in @($ExecutorStdout,$ExecutorStderr,$ExecutorLog)) { if (Test-Path $old) { Remove-Item -LiteralPath $old -Force } }
$pythonArgs = @(
    '-s',(Quote-ProcessArg $Executor),
    '--comfy-root',(Quote-ProcessArg $ComfyRoot),
    '--workspace',(Quote-ProcessArg $Workspace),
    '--klein-workspace',(Quote-ProcessArg $KleinWorkspace),
    '--port',"$Port",
    '--timeout-minutes',"$TimeoutMinutes",
    '--comfy-commit',$ComfyCommit
)
$executorExit = 1
try {
    Write-Host 'RUNNER63: launching Qwen2511 precision executor...' -ForegroundColor Cyan
    $ep = Start-Process -FilePath $Python -ArgumentList $pythonArgs -WorkingDirectory $ProjectRepoRoot -RedirectStandardOutput $ExecutorStdout -RedirectStandardError $ExecutorStderr -WindowStyle Hidden -PassThru -Wait
    $executorExit = $ep.ExitCode
} finally { Stop-Managed $PidFile }

$stdoutText = Read-TextFileOrEmpty $ExecutorStdout
$stderrText = Read-TextFileOrEmpty $ExecutorStderr
Set-Content -LiteralPath $ExecutorLog -Value (@('=== PYTHON STDOUT ===',$stdoutText,'=== PYTHON STDERR ===',$stderrText) -join [Environment]::NewLine) -Encoding UTF8
Print-TextFile $ExecutorStdout '--- RUNNER63 PYTHON STDOUT ---'
if (-not [string]::IsNullOrWhiteSpace($stderrText)) { Print-TextFile $ExecutorStderr '--- RUNNER63 PYTHON STDERR ---' }
if ($executorExit -ne 0) {
    Write-Host "RUNNER63-PYTHON-EXIT: $executorExit" -ForegroundColor Red
    Print-TextFile $StderrLog '--- COMFYUI STDERR TAIL ---' 400
    Fail "precision executor exited with code $executorExit"
}

$Expected = @(
    'qwen2511_atomic_plank_steps20.png','qwen2511_atomic_plank_steps40.png',
    'qwen2511_atomic_strap_steps20.png','qwen2511_atomic_strap_steps40.png',
    'runner63_qwen2511_precision_contact_sheet.png','runner63_qwen2511_precision_manifest.json','runner63_executor.log'
)
foreach ($name in $Expected) {
    $path = Join-Path $OutputDir $name
    if (-not (Test-Path $path -PathType Leaf)) { Fail "expected output missing: $path" }
}

Write-Host ''
Write-Host 'RUNNER63-QWEN2511: PASS - TECHNICAL PRECISION MATRIX COMPLETE / VISUAL VERDICT PENDING' -ForegroundColor Green
Write-Host "Contact sheet: $(Join-Path $OutputDir 'runner63_qwen2511_precision_contact_sheet.png')" -ForegroundColor Cyan
Write-Host "Manifest: $(Join-Path $OutputDir 'runner63_qwen2511_precision_manifest.json')" -ForegroundColor Cyan
Write-Host "Executor log: $ExecutorLog" -ForegroundColor Cyan
Write-Host 'Visual gate: 2511 must execute one-plank and one-strap facts more precisely than Qwen2509 and Klein, not merely preserve the source more strongly.' -ForegroundColor Green
