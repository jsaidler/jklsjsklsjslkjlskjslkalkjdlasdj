param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$Workspace = 'Z:\AI\Flux2Klein',
    [int]$Port = 8192,
    [int]$TimeoutMinutes = 240
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ComfyCommit = '672ba9e5e388bd6bfac5ceef61f89ffdd9467200'

$BaseModelName = 'flux-2-klein-base-4b-fp8.safetensors'
$BaseModelUrl = 'https://huggingface.co/black-forest-labs/FLUX.2-klein-base-4b-fp8/resolve/main/flux-2-klein-base-4b-fp8.safetensors'
$BaseModelSha256 = '44bab3a86fe98b85d21dd2a4729ebdc3ae51fb8a39f76e457e18c724219e6840'
$BaseModelBytes = [int64]4089498488

$TextEncoderName = 'qwen_3_4b.safetensors'
$TextEncoderSha256 = '6c671498573ac2f7a5501502ccce8d2b08ea6ca2f661c458e708f36b36edfc5a'

$BaseVaeName = 'full_encoder_small_decoder.safetensors'
$BaseVaeUrl = 'https://huggingface.co/black-forest-labs/FLUX.2-small-decoder/resolve/main/full_encoder_small_decoder.safetensors'
$BaseVaeSha256 = 'ea4273f02d1fafbf8e1d1c2cf6018ed8748652eb0bf34f2dd91171f16f15ab62'
$BaseVaeBytes = [int64]249519092

function Fail([string]$Message) {
    Write-Host "RUNNER59-FLUX2-KLEIN-BASE-EDIT: FAIL - $Message" -ForegroundColor Red
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
        if ((Get-Sha256 $Destination) -eq $ExpectedSha.ToLowerInvariant()) {
            Write-Host "  $Label already present and verified." -ForegroundColor Green
            return
        }
        Write-Host "  Existing $Label failed hash verification; removing it." -ForegroundColor Yellow
        Remove-Item -LiteralPath $Destination -Force
    }

    $partial = "$Destination.part"
    $curl = Get-Command curl.exe -ErrorAction SilentlyContinue
    if (-not $curl) { Fail 'curl.exe is required for resumable verified model downloads.' }
    Write-Host "Downloading $Label" -ForegroundColor Cyan
    Write-Host "  $Url" -ForegroundColor DarkGray
    & $curl.Source '--fail' '--location' '--retry' '8' '--retry-delay' '5' '--retry-all-errors' '--continue-at' '-' '--output' $partial $Url
    if ($LASTEXITCODE -ne 0) {
        Fail "$Label download failed with curl exit code $LASTEXITCODE. Partial file retained: $partial"
    }
    Move-Item -LiteralPath $partial -Destination $Destination -Force
    Require-Hash $Destination $ExpectedSha $Label
}

function Stop-Managed([string]$PidFile) {
    if (-not (Test-Path $PidFile -PathType Leaf)) { return }
    $pidText = (Get-Content -LiteralPath $PidFile -Raw).Trim()
    $managedPid = 0
    if ([int]::TryParse($pidText, [ref]$managedPid) -and $managedPid -gt 0) {
        $process = Get-Process -Id $managedPid -ErrorAction SilentlyContinue
        if ($process) {
            Stop-Process -Id $managedPid -Force
            Start-Sleep -Seconds 2
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

$PortableRoot = Join-Path $Workspace 'ComfyUI_windows_portable'
$Python = Join-Path $PortableRoot 'python_embeded\python.exe'
$ComfyRoot = Join-Path $PortableRoot 'ComfyUI'
$MainPy = Join-Path $ComfyRoot 'main.py'
$Executor = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\flux2_klein_base_edit_gate.py'
$BaseAdapter = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\flux2_klein_base_adapter.py'
$DistilledAdapter = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\flux2_klein_adapter.py'
$Protocol = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\adapter_protocol.py'
$Original = Join-Path $Workspace 'spike\flux2_klein_4b_t2i_probe.png'
$Material = Join-Path $Workspace 'edit_strength_calibration\material_decay_reference.png'

foreach ($required in @($Python,$MainPy,$Executor,$BaseAdapter,$DistilledAdapter,$Protocol,$Original,$Material)) {
    if (-not (Test-Path $required -PathType Leaf)) { Fail "required file missing: $required" }
}

$BaseModelPath = Join-Path $ComfyRoot "models\diffusion_models\$BaseModelName"
$TextEncoderPath = Join-Path $ComfyRoot "models\text_encoders\$TextEncoderName"
$BaseVaePath = Join-Path $ComfyRoot "models\vae\$BaseVaeName"

Write-Host ''
Write-Host 'Roguelite Runner 59 - FLUX.2 KLEIN 4B BASE / STRONG REFERENCE-EDIT GATE' -ForegroundColor Cyan
Write-Host '[WHY] Runner58 exhausted the distilled recipe enough to reject it as a strong production editor.' -ForegroundColor Yellow
Write-Host '[SAME FAMILY] Tests the non-distilled Apache-2.0 4B Base before changing model families.' -ForegroundColor Green
Write-Host '[REUSE] Reuses Qwen3-4B, ComfyUI runtime, original gate and Runner58 material reference.' -ForegroundColor Green
Write-Host '[DOWNLOAD] Base diffusion 4.089 GB + full-encoder/small-decoder VAE 0.250 GB = ~4.34 GB additional.' -ForegroundColor Green
Write-Host '[OFFICIAL RECIPE BASIS] Euler, CFG 5, 20 steps; also tests 50 steps as the full-step Base branch.' -ForegroundColor Green
Write-Host '[OUTPUT] 768x768; single + ordered multi-reference at 20/50 steps.' -ForegroundColor Green
Write-Host ''

Require-Hash $TextEncoderPath $TextEncoderSha256 'Qwen3-4B text encoder'

$missingBytes = [int64]0
if (-not (Test-Verified $BaseModelPath $BaseModelSha256)) { $missingBytes += $BaseModelBytes }
if (-not (Test-Verified $BaseVaePath $BaseVaeSha256)) { $missingBytes += $BaseVaeBytes }
$requiredFree = $missingBytes + [int64](2GB)
$driveRoot = [System.IO.Path]::GetPathRoot($Workspace)
$driveInfo = [System.IO.DriveInfo]::new($driveRoot)
$freeBytes = [int64]$driveInfo.AvailableFreeSpace
$requiredGiB = [math]::Round($requiredFree / 1GB, 2)
$freeGiB = [math]::Round($freeBytes / 1GB, 2)
Write-Host "Disk preflight: free=${freeGiB} GiB; conservative additional requirement=${requiredGiB} GiB." -ForegroundColor Cyan
if ($freeBytes -lt $requiredFree) {
    Fail "insufficient free space on $driveRoot. Need about ${requiredGiB} GiB additional; found ${freeGiB} GiB."
}

Download-Verified $BaseModelUrl $BaseModelPath $BaseModelSha256 'FLUX.2 Klein Base 4B FP8 (4.09 GB)'
Download-Verified $BaseVaeUrl $BaseVaePath $BaseVaeSha256 'FLUX.2 full-encoder/small-decoder VAE (250 MB)'

if (-not (Get-Command git.exe -ErrorAction SilentlyContinue)) { Fail 'git.exe is required.' }
$currentCommit = (& git.exe -C $ComfyRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $currentCommit -ne $ComfyCommit) {
    Fail "isolated ComfyUI commit mismatch. Expected $ComfyCommit, got $currentCommit"
}
Write-Host "  ComfyUI pinned commit verified: $currentCommit" -ForegroundColor Green

$Base = "http://127.0.0.1:$Port"
$OutputDir = Join-Path $Workspace 'base_edit_gate'
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$PidFile = Join-Path $Workspace '.flux2_klein_runner59.pid'
$StdoutLog = Join-Path $OutputDir "comfyui_runner59_${Port}_stdout.log"
$StderrLog = Join-Path $OutputDir "comfyui_runner59_${Port}_stderr.log"
$ExecutorStdout = Join-Path $OutputDir 'runner59_python_stdout.log'
$ExecutorStderr = Join-Path $OutputDir 'runner59_python_stderr.log'
$ExecutorLog = Join-Path $OutputDir 'runner59_executor.log'

Stop-Managed $PidFile
$portBusy = $false
try {
    $null = Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 2
    $portBusy = $true
} catch { }
if ($portBusy) { Fail "port $Port is already serving an unmanaged process" }

$launchArgs = @('-s',$MainPy,'--windows-standalone-build','--listen','127.0.0.1','--port',"$Port",'--disable-auto-launch')
$process = Start-Process -FilePath $Python -ArgumentList $launchArgs -WorkingDirectory $ComfyRoot `
    -RedirectStandardOutput $StdoutLog -RedirectStandardError $StderrLog -WindowStyle Hidden -PassThru
Set-Content -LiteralPath $PidFile -Value $process.Id -Encoding ASCII
Write-Host "Started isolated FLUX.2 ComfyUI PID $($process.Id) on port $Port" -ForegroundColor Green

$ready = $false
for ($i=0; $i -lt 300; $i++) {
    try {
        $null = Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 2
        $ready = $true
        break
    } catch {
        if ($process.HasExited) {
            Print-TextFile $StderrLog '--- COMFYUI STDERR ---' 260
            Stop-Managed $PidFile
            Fail "isolated ComfyUI exited before readiness with code $($process.ExitCode)"
        }
        Start-Sleep -Seconds 1
    }
}
if (-not $ready) {
    Print-TextFile $StderrLog '--- COMFYUI STDERR ---' 260
    Stop-Managed $PidFile
    Fail "isolated ComfyUI did not become ready at $Base"
}

foreach ($old in @($ExecutorStdout,$ExecutorStderr,$ExecutorLog)) {
    if (Test-Path $old) { Remove-Item -LiteralPath $old -Force }
}

$pythonArgs = @(
    '-s',
    (Quote-ProcessArg $Executor),
    '--comfy-root', (Quote-ProcessArg $ComfyRoot),
    '--workspace', (Quote-ProcessArg $Workspace),
    '--port', "$Port",
    '--timeout-minutes', "$TimeoutMinutes",
    '--comfy-commit', $ComfyCommit
)

$executorExit = 1
try {
    Write-Host 'RUNNER59: launching Base edit executor...' -ForegroundColor Cyan
    $executorProcess = Start-Process -FilePath $Python -ArgumentList $pythonArgs -WorkingDirectory $ProjectRepoRoot `
        -RedirectStandardOutput $ExecutorStdout -RedirectStandardError $ExecutorStderr -WindowStyle Hidden -PassThru -Wait
    $executorExit = $executorProcess.ExitCode
} finally {
    Stop-Managed $PidFile
}

$stdoutText = Read-TextFileOrEmpty $ExecutorStdout
$stderrText = Read-TextFileOrEmpty $ExecutorStderr
Set-Content -LiteralPath $ExecutorLog -Value (@('=== PYTHON STDOUT ===',$stdoutText,'=== PYTHON STDERR ===',$stderrText) -join [Environment]::NewLine) -Encoding UTF8

Print-TextFile $ExecutorStdout '--- RUNNER59 PYTHON STDOUT ---'
if (-not [string]::IsNullOrWhiteSpace($stderrText)) {
    Print-TextFile $ExecutorStderr '--- RUNNER59 PYTHON STDERR ---'
}

if ($executorExit -ne 0) {
    Write-Host "RUNNER59-PYTHON-EXIT: $executorExit" -ForegroundColor Red
    Print-TextFile $StderrLog '--- COMFYUI STDERR TAIL ---' 360
    Fail "Base edit executor exited with code $executorExit"
}

$Expected = @(
    'base_single_binary_steps20.png',
    'base_single_binary_steps50.png',
    'base_multi_structure_material_steps20.png',
    'base_multi_structure_material_steps50.png',
    'runner59_base_contact_sheet.png',
    'runner59_base_manifest.json',
    'runner59_executor.log'
)
foreach ($name in $Expected) {
    $path = Join-Path $OutputDir $name
    if (-not (Test-Path $path -PathType Leaf)) { Fail "expected output missing: $path" }
}

Write-Host ''
Write-Host 'RUNNER59-FLUX2-KLEIN-BASE-EDIT: PASS - TECHNICAL MATRIX COMPLETE / VISUAL VERDICT PENDING' -ForegroundColor Green
Write-Host "Contact sheet: $(Join-Path $OutputDir 'runner59_base_contact_sheet.png')" -ForegroundColor Cyan
Write-Host "Manifest: $(Join-Path $OutputDir 'runner59_base_manifest.json')" -ForegroundColor Cyan
Write-Host "Executor log: $ExecutorLog" -ForegroundColor Cyan
Write-Host 'Visual gate: Base is accepted for production reference editing only if it clearly executes structural facts and material transfer while preserving the gate identity/camera.' -ForegroundColor Green
