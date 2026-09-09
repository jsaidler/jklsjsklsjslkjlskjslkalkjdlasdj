param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$SourcePortable = 'Z:\AI\Flux2Klein\ComfyUI_windows_portable',
    [string]$Workspace = 'Z:\AI\QwenImageEdit',
    [string]$KleinWorkspace = 'Z:\AI\Flux2Klein',
    [int]$Port = 8193,
    [int]$TimeoutMinutes = 360
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ComfyCommit = '672ba9e5e388bd6bfac5ceef61f89ffdd9467200'
$ComfyRepo = 'https://github.com/Comfy-Org/ComfyUI.git'

$ModelName = 'qwen_image_edit_2509_fp8_e4m3fn.safetensors'
$ModelUrl = 'https://huggingface.co/Comfy-Org/Qwen-Image-Edit_ComfyUI/resolve/main/split_files/diffusion_models/qwen_image_edit_2509_fp8_e4m3fn.safetensors'
$ModelSha256 = '318568f61951ab9da21100c7b896e3c1da67f0d2efad6421545e022cfaa2b2b4'
$ModelBytes = [int64]20430698424

$TextEncoderName = 'qwen_2.5_vl_7b_fp8_scaled.safetensors'
$TextEncoderUrl = 'https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors'
$TextEncoderSha256 = 'cb5636d852a0ea6a9075ab1bef496c0db7aef13c02350571e388aea959c5c0b4'
$TextEncoderBytes = [int64]9384670680

$VaeName = 'qwen_image_vae.safetensors'
$VaeUrl = 'https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/vae/qwen_image_vae.safetensors'
$VaeSha256 = 'a70580f0213e67967ee9c95f05bb400e8fb08307e017a924bf3441223e023d1f'
$VaeBytes = [int64]253806246

function Fail([string]$Message) {
    Write-Host "RUNNER62-QWEN2509: FAIL - $Message" -ForegroundColor Red
    exit 1
}

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Test-Verified([string]$Path, [string]$ExpectedSha) {
    if (-not (Test-Path $Path -PathType Leaf)) { return $false }
    return ((Get-Sha256 $Path) -eq $ExpectedSha.ToLowerInvariant())
}

function Require-Hash([string]$Path, [string]$ExpectedSha, [string]$Label) {
    if (-not (Test-Path $Path -PathType Leaf)) { Fail "required $Label missing: $Path" }
    $actual = Get-Sha256 $Path
    if ($actual -ne $ExpectedSha.ToLowerInvariant()) {
        Fail "$Label SHA256 mismatch. Expected $ExpectedSha, got $actual"
    }
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
        Write-Host "  Existing $Label failed hash verification; removing it." -ForegroundColor Yellow
        Remove-Item -LiteralPath $Destination -Force
    }
    $partial = "$Destination.part"
    $curl = Get-Command curl.exe -ErrorAction SilentlyContinue
    if (-not $curl) { Fail 'curl.exe is required for resumable verified downloads.' }
    Write-Host "Downloading $Label" -ForegroundColor Cyan
    Write-Host "  $Url" -ForegroundColor DarkGray
    & $curl.Source '--fail' '--location' '--retry' '8' '--retry-delay' '5' '--retry-all-errors' '--continue-at' '-' '--output' $partial $Url
    if ($LASTEXITCODE -ne 0) {
        Fail "$Label download failed with curl exit code $LASTEXITCODE. Partial retained: $partial"
    }
    Move-Item -LiteralPath $partial -Destination $Destination -Force
    Require-Hash $Destination $ExpectedSha $Label
}

function Stop-Managed([string]$PidFile) {
    if (-not (Test-Path $PidFile -PathType Leaf)) { return }
    $raw = Get-Content -LiteralPath $PidFile -Raw
    if ($null -eq $raw) { Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue; return }
    $pidText = ([string]$raw).Trim()
    $managedPid = 0
    if ([int]::TryParse($pidText, [ref]$managedPid) -and $managedPid -gt 0) {
        $p = Get-Process -Id $managedPid -ErrorAction SilentlyContinue
        if ($p) {
            Stop-Process -Id $managedPid -Force
            Start-Sleep -Seconds 2
        }
    }
    Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue
}

function Invoke-Git([string[]]$GitArgs, [string]$FailureMessage) {
    & git.exe @GitArgs
    if ($LASTEXITCODE -ne 0) { Fail "$FailureMessage (git exit code $LASTEXITCODE)" }
}

function Quote-ProcessArg([string]$Value) {
    if ($Value -match '[\s"]') { return '"' + ($Value -replace '"','\"') + '"' }
    return $Value
}

function Read-TextFileOrEmpty([string]$Path) {
    if (-not (Test-Path $Path -PathType Leaf)) { return '' }
    $value = Get-Content -LiteralPath $Path -Raw
    if ($null -eq $value) { return '' }
    return [string]$value
}

function Print-TextFile([string]$Path, [string]$Header, [int]$Tail = 0) {
    Write-Host $Header -ForegroundColor Yellow
    if (-not (Test-Path $Path -PathType Leaf)) {
        Write-Host "  <missing: $Path>" -ForegroundColor DarkYellow
        return
    }
    if ($Tail -gt 0) { Get-Content -LiteralPath $Path -Tail $Tail } else { Get-Content -LiteralPath $Path }
}

$SourcePythonDir = Join-Path $SourcePortable 'python_embeded'
$SourcePython = Join-Path $SourcePythonDir 'python.exe'
$Executor = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\qwen_image_edit_2509_feasibility_gate.py'
$Adapter = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\qwen_image_edit_2509_adapter.py'
$Protocol = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\adapter_protocol.py'
$SharedHelper = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\flux2_klein_adapter.py'
$SourceOriginal = Join-Path $KleinWorkspace 'spike\flux2_klein_4b_t2i_probe.png'
$KleinPlank = Join-Path $KleinWorkspace 'base_atomic_sequence\atomic_plank.png'
$KleinStrap = Join-Path $KleinWorkspace 'base_atomic_sequence\atomic_strap.png'

foreach ($required in @($SourcePython,$Executor,$Adapter,$Protocol,$SharedHelper,$SourceOriginal,$KleinPlank,$KleinStrap)) {
    if (-not (Test-Path $required -PathType Leaf)) { Fail "required source file missing: $required" }
}
if (-not (Get-Command git.exe -ErrorAction SilentlyContinue)) { Fail 'git.exe is required.' }
if (-not (Get-Command robocopy.exe -ErrorAction SilentlyContinue)) { Fail 'robocopy.exe is required.' }

$PortableRoot = Join-Path $Workspace 'ComfyUI_windows_portable'
$PythonDir = Join-Path $PortableRoot 'python_embeded'
$Python = Join-Path $PythonDir 'python.exe'
$ComfyRoot = Join-Path $PortableRoot 'ComfyUI'
$MainPy = Join-Path $ComfyRoot 'main.py'
$ModelPath = Join-Path $ComfyRoot "models\diffusion_models\$ModelName"
$TextEncoderPath = Join-Path $ComfyRoot "models\text_encoders\$TextEncoderName"
$VaePath = Join-Path $ComfyRoot "models\vae\$VaeName"
$OutputDir = Join-Path $Workspace 'feasibility_gate'
$PidFile = Join-Path $Workspace '.qwen2509_runner62.pid'
$DepsMarker = Join-Path $PortableRoot ".deps_$ComfyCommit.ok"

New-Item -ItemType Directory -Force -Path $Workspace,$PortableRoot,$OutputDir | Out-Null

Write-Host ''
Write-Host 'Roguelite Runner 62 - QWEN-IMAGE-EDIT-2509 FP8 / LOW-VRAM + ATOMIC PRECISION GATE' -ForegroundColor Cyan
Write-Host '[WHY] Runner61 exhausted Klein Base for precise structural editing: it follows coarse intent but over-edits the requested region.' -ForegroundColor Yellow
Write-Host '[SPECIALIST] Qwen 2509 is evaluated specifically as the strong semantic/structural editor behind the generic Asset Studio.' -ForegroundColor Green
Write-Host '[NATIVE GRAPH] Uses ComfyUI TextEncodeQwenImageEditPlus + AuraFlow shift 3 + CFGNorm 1.' -ForegroundColor Green
Write-Host '[NO LIGHTNING] First verdict uses native FP8, Euler/simple, 20 steps, CFG 4, denoise 1.' -ForegroundColor Green
Write-Host '[LOW VRAM] ComfyUI launches with --lowvram; Qwen2.5-VL encoder is explicitly loaded on CPU.' -ForegroundColor Green
Write-Host '[COMPARISON] Original | Klein atomic | Qwen atomic for one-plank removal and one-strap break.' -ForegroundColor Green
Write-Host ''

$missingBytes = [int64]0
if (-not (Test-Verified $ModelPath $ModelSha256)) { $missingBytes += $ModelBytes }
if (-not (Test-Verified $TextEncoderPath $TextEncoderSha256)) { $missingBytes += $TextEncoderBytes }
if (-not (Test-Verified $VaePath $VaeSha256)) { $missingBytes += $VaeBytes }
$runtimeReserve = if (Test-Path $Python -PathType Leaf) { [int64](3GB) } else { [int64](8GB) }
$requiredFree = $missingBytes + $runtimeReserve + [int64](3GB)
$driveRoot = [System.IO.Path]::GetPathRoot($Workspace)
$driveInfo = [System.IO.DriveInfo]::new($driveRoot)
$freeBytes = [int64]$driveInfo.AvailableFreeSpace
$requiredGiB = [math]::Round($requiredFree / 1GB, 2)
$freeGiB = [math]::Round($freeBytes / 1GB, 2)
Write-Host "Disk preflight: free=${freeGiB} GiB; conservative additional requirement=${requiredGiB} GiB." -ForegroundColor Cyan
if ($freeBytes -lt $requiredFree) {
    Fail "insufficient free space on $driveRoot. Need about ${requiredGiB} GiB; found ${freeGiB} GiB."
}

if (-not (Test-Path $Python -PathType Leaf)) {
    Write-Host 'Creating isolated Qwen Python runtime from the proven Flux2Klein portable Python...' -ForegroundColor Cyan
    New-Item -ItemType Directory -Force -Path $PythonDir | Out-Null
    & robocopy.exe $SourcePythonDir $PythonDir /E /COPY:DAT /DCOPY:DAT /R:2 /W:2 /NFL /NDL /NJH /NJS /NP
    $rc = $LASTEXITCODE
    if ($rc -gt 7) { Fail "robocopy of isolated Python runtime failed with code $rc" }
}
if (-not (Test-Path $Python -PathType Leaf)) { Fail "isolated Python was not created: $Python" }

if (-not (Test-Path (Join-Path $ComfyRoot '.git') -PathType Container)) {
    if (Test-Path $ComfyRoot) { Remove-Item -LiteralPath $ComfyRoot -Recurse -Force }
    Write-Host 'Cloning isolated ComfyUI for Qwen...' -ForegroundColor Cyan
    Invoke-Git -GitArgs @('clone','--filter=blob:none','--no-checkout',$ComfyRepo,$ComfyRoot) -FailureMessage 'ComfyUI clone failed'
}
Write-Host "Pinning Qwen ComfyUI to $ComfyCommit" -ForegroundColor Cyan
Invoke-Git -GitArgs @('-C',$ComfyRoot,'fetch','--depth','1','origin',$ComfyCommit) -FailureMessage 'ComfyUI pinned fetch failed'
Invoke-Git -GitArgs @('-C',$ComfyRoot,'checkout','--detach','--force',$ComfyCommit) -FailureMessage 'ComfyUI pinned checkout failed'
$currentCommit = (& git.exe -C $ComfyRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $currentCommit -ne $ComfyCommit) {
    Fail "ComfyUI checkout mismatch. Expected $ComfyCommit, got $currentCommit"
}

if (-not (Test-Path $DepsMarker -PathType Leaf)) {
    Write-Host 'Installing pinned ComfyUI dependencies into isolated Qwen Python...' -ForegroundColor Cyan
    & $Python -s -m pip install --disable-pip-version-check -r (Join-Path $ComfyRoot 'requirements.txt')
    if ($LASTEXITCODE -ne 0) { Fail 'isolated ComfyUI dependency installation failed' }
    Set-Content -LiteralPath $DepsMarker -Value $ComfyCommit -Encoding ASCII
} else {
    Write-Host '  Pinned dependency marker already present.' -ForegroundColor Green
}

Download-Verified $ModelUrl $ModelPath $ModelSha256 'Qwen-Image-Edit-2509 FP8 (20.43 GB)'
Download-Verified $TextEncoderUrl $TextEncoderPath $TextEncoderSha256 'Qwen2.5-VL 7B FP8 encoder (9.38 GB)'
Download-Verified $VaeUrl $VaePath $VaeSha256 'Qwen Image VAE (254 MB)'

$Base = "http://127.0.0.1:$Port"
$StdoutLog = Join-Path $OutputDir "comfyui_runner62_${Port}_stdout.log"
$StderrLog = Join-Path $OutputDir "comfyui_runner62_${Port}_stderr.log"
$ExecutorStdout = Join-Path $OutputDir 'runner62_python_stdout.log'
$ExecutorStderr = Join-Path $OutputDir 'runner62_python_stderr.log'
$ExecutorLog = Join-Path $OutputDir 'runner62_executor.log'

Stop-Managed $PidFile
$portBusy = $false
try {
    $null = Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 2
    $portBusy = $true
} catch { }
if ($portBusy) { Fail "port $Port is already serving an unmanaged process" }

$env:PYTORCH_CUDA_ALLOC_CONF = 'expandable_segments:True'
$launchArgs = @('-s',$MainPy,'--windows-standalone-build','--listen','127.0.0.1','--port',"$Port",'--disable-auto-launch','--lowvram','--reserve-vram','1.0')
$process = Start-Process -FilePath $Python -ArgumentList $launchArgs -WorkingDirectory $ComfyRoot `
    -RedirectStandardOutput $StdoutLog -RedirectStandardError $StderrLog -WindowStyle Hidden -PassThru
Set-Content -LiteralPath $PidFile -Value $process.Id -Encoding ASCII
Write-Host "Started isolated Qwen ComfyUI PID $($process.Id) on port $Port" -ForegroundColor Green

$ready = $false
for ($i=0; $i -lt 360; $i++) {
    try {
        $null = Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 2
        $ready = $true
        break
    } catch {
        if ($process.HasExited) {
            Print-TextFile $StderrLog '--- COMFYUI STDERR ---' 360
            Stop-Managed $PidFile
            Fail "isolated Qwen ComfyUI exited before readiness with code $($process.ExitCode)"
        }
        Start-Sleep -Seconds 1
    }
}
if (-not $ready) {
    Print-TextFile $StderrLog '--- COMFYUI STDERR ---' 360
    Stop-Managed $PidFile
    Fail "isolated Qwen ComfyUI did not become ready at $Base"
}

foreach ($old in @($ExecutorStdout,$ExecutorStderr,$ExecutorLog)) {
    if (Test-Path $old) { Remove-Item -LiteralPath $old -Force }
}

$pythonArgs = @(
    '-s',
    (Quote-ProcessArg $Executor),
    '--comfy-root', (Quote-ProcessArg $ComfyRoot),
    '--workspace', (Quote-ProcessArg $Workspace),
    '--source', (Quote-ProcessArg $SourceOriginal),
    '--klein-plank', (Quote-ProcessArg $KleinPlank),
    '--klein-strap', (Quote-ProcessArg $KleinStrap),
    '--port', "$Port",
    '--timeout-minutes', "$TimeoutMinutes",
    '--comfy-commit', $ComfyCommit
)

$executorExit = 1
try {
    Write-Host 'RUNNER62: launching native Qwen 2509 precision executor...' -ForegroundColor Cyan
    $executorProcess = Start-Process -FilePath $Python -ArgumentList $pythonArgs -WorkingDirectory $ProjectRepoRoot `
        -RedirectStandardOutput $ExecutorStdout -RedirectStandardError $ExecutorStderr -WindowStyle Hidden -PassThru -Wait
    $executorExit = $executorProcess.ExitCode
} finally {
    Stop-Managed $PidFile
}

$stdoutText = Read-TextFileOrEmpty $ExecutorStdout
$stderrText = Read-TextFileOrEmpty $ExecutorStderr
Set-Content -LiteralPath $ExecutorLog -Value (@('=== PYTHON STDOUT ===',$stdoutText,'=== PYTHON STDERR ===',$stderrText) -join [Environment]::NewLine) -Encoding UTF8
Print-TextFile $ExecutorStdout '--- RUNNER62 PYTHON STDOUT ---'
if (-not [string]::IsNullOrWhiteSpace($stderrText)) { Print-TextFile $ExecutorStderr '--- RUNNER62 PYTHON STDERR ---' }

if ($executorExit -ne 0) {
    Write-Host "RUNNER62-PYTHON-EXIT: $executorExit" -ForegroundColor Red
    Print-TextFile $StderrLog '--- QWEN COMFYUI STDERR TAIL ---' 520
    Fail "Qwen 2509 executor exited with code $executorExit"
}

$Expected = @(
    'qwen2509_atomic_plank.png',
    'qwen2509_atomic_strap.png',
    'runner62_qwen2509_vs_klein_contact_sheet.png',
    'runner62_qwen2509_manifest.json',
    'runner62_executor.log'
)
foreach ($name in $Expected) {
    $path = Join-Path $OutputDir $name
    if (-not (Test-Path $path -PathType Leaf)) { Fail "expected output missing: $path" }
}

Write-Host ''
Write-Host 'RUNNER62-QWEN2509: PASS - TECHNICAL ATOMIC MATRIX COMPLETE / VISUAL VERDICT PENDING' -ForegroundColor Green
Write-Host "Contact sheet: $(Join-Path $OutputDir 'runner62_qwen2509_vs_klein_contact_sheet.png')" -ForegroundColor Cyan
Write-Host "Manifest: $(Join-Path $OutputDir 'runner62_qwen2509_manifest.json')" -ForegroundColor Cyan
Write-Host "Executor log: $ExecutorLog" -ForegroundColor Cyan
Write-Host 'Visual gate: Qwen must materially improve atomic precision over Runner61 without losing gate identity/camera.' -ForegroundColor Green
