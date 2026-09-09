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
$BaseModelSha256 = '44bab3a86fe98b85d21dd2a4729ebdc3ae51fb8a39f76e457e18c724219e6840'
$TextEncoderName = 'qwen_3_4b.safetensors'
$TextEncoderSha256 = '6c671498573ac2f7a5501502ccce8d2b08ea6ca2f661c458e708f36b36edfc5a'
$BaseVaeName = 'full_encoder_small_decoder.safetensors'
$BaseVaeSha256 = 'ea4273f02d1fafbf8e1d1c2cf6018ed8748652eb0bf34f2dd91171f16f15ab62'

function Fail([string]$Message) {
    Write-Host "RUNNER61-FLUX2-KLEIN-BASE-ATOMIC: FAIL - $Message" -ForegroundColor Red
    exit 1
}

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Require-Hash([string]$Path, [string]$ExpectedSha, [string]$Label) {
    if (-not (Test-Path $Path -PathType Leaf)) { Fail "required $Label missing: $Path" }
    $actual = Get-Sha256 $Path
    if ($actual -ne $ExpectedSha.ToLowerInvariant()) {
        Fail "$Label SHA256 mismatch. Expected $ExpectedSha, got $actual"
    }
    Write-Host "  $Label verified." -ForegroundColor Green
}

function Stop-Managed([string]$PidFile) {
    if (-not (Test-Path $PidFile -PathType Leaf)) { return }
    $raw = Get-Content -LiteralPath $PidFile -Raw
    if ($null -eq $raw) { Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue; return }
    $pidText = ([string]$raw).Trim()
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
$Executor = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\flux2_klein_base_atomic_sequence_gate.py'
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
Write-Host 'Roguelite Runner 61 - FLUX.2 KLEIN 4B BASE / ATOMIC + SEQUENTIAL EDIT OBEDIENCE' -ForegroundColor Cyan
Write-Host '[PREREQUISITE] Runner60 established a sane official-parity Base graph; no cyan/posterized recipe failure remains.' -ForegroundColor Green
Write-Host '[NO DOWNLOAD] Reuses the exact Base model, Qwen3-4B encoder and Base VAE already installed.' -ForegroundColor Green
Write-Host '[ATOMIC] Three independent one-fact edits from the original: missing plank / missing capstone / broken strap.' -ForegroundColor Green
Write-Host '[SEQUENCE] Rebuilds the same complex revision as successive approved-state edits, one fact per pass.' -ForegroundColor Green
Write-Host '[MATERIAL] Final pass uses structure=current chain state + material=Runner58 decay board.' -ForegroundColor Green
Write-Host '[RECIPE] Official-parity Base: reference scale 1 MP, empty negative encode, Euler, CFG 5, 20 steps.' -ForegroundColor Green
Write-Host ''

Require-Hash $BaseModelPath $BaseModelSha256 'FLUX.2 Klein Base 4B FP8'
Require-Hash $TextEncoderPath $TextEncoderSha256 'Qwen3-4B text encoder'
Require-Hash $BaseVaePath $BaseVaeSha256 'FLUX.2 full-encoder/small-decoder VAE'

if (-not (Get-Command git.exe -ErrorAction SilentlyContinue)) { Fail 'git.exe is required.' }
$currentCommit = (& git.exe -C $ComfyRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $currentCommit -ne $ComfyCommit) {
    Fail "isolated ComfyUI commit mismatch. Expected $ComfyCommit, got $currentCommit"
}
Write-Host "  ComfyUI pinned commit verified: $currentCommit" -ForegroundColor Green

$Base = "http://127.0.0.1:$Port"
$OutputDir = Join-Path $Workspace 'base_atomic_sequence'
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$PidFile = Join-Path $Workspace '.flux2_klein_runner61.pid'
$StdoutLog = Join-Path $OutputDir "comfyui_runner61_${Port}_stdout.log"
$StderrLog = Join-Path $OutputDir "comfyui_runner61_${Port}_stderr.log"
$ExecutorStdout = Join-Path $OutputDir 'runner61_python_stdout.log'
$ExecutorStderr = Join-Path $OutputDir 'runner61_python_stderr.log'
$ExecutorLog = Join-Path $OutputDir 'runner61_executor.log'

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
            Print-TextFile $StderrLog '--- COMFYUI STDERR ---' 280
            Stop-Managed $PidFile
            Fail "isolated ComfyUI exited before readiness with code $($process.ExitCode)"
        }
        Start-Sleep -Seconds 1
    }
}
if (-not $ready) {
    Print-TextFile $StderrLog '--- COMFYUI STDERR ---' 280
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
    Write-Host 'RUNNER61: launching atomic/sequential executor...' -ForegroundColor Cyan
    $executorProcess = Start-Process -FilePath $Python -ArgumentList $pythonArgs -WorkingDirectory $ProjectRepoRoot `
        -RedirectStandardOutput $ExecutorStdout -RedirectStandardError $ExecutorStderr -WindowStyle Hidden -PassThru -Wait
    $executorExit = $executorProcess.ExitCode
} finally {
    Stop-Managed $PidFile
}

$stdoutText = Read-TextFileOrEmpty $ExecutorStdout
$stderrText = Read-TextFileOrEmpty $ExecutorStderr
Set-Content -LiteralPath $ExecutorLog -Value (@('=== PYTHON STDOUT ===',$stdoutText,'=== PYTHON STDERR ===',$stderrText) -join [Environment]::NewLine) -Encoding UTF8

Print-TextFile $ExecutorStdout '--- RUNNER61 PYTHON STDOUT ---'
if (-not [string]::IsNullOrWhiteSpace($stderrText)) {
    Print-TextFile $ExecutorStderr '--- RUNNER61 PYTHON STDERR ---'
}

if ($executorExit -ne 0) {
    Write-Host "RUNNER61-PYTHON-EXIT: $executorExit" -ForegroundColor Red
    Print-TextFile $StderrLog '--- COMFYUI STDERR TAIL ---' 380
    Fail "atomic/sequential executor exited with code $executorExit"
}

$Expected = @(
    'atomic_plank.png',
    'atomic_capstone.png',
    'atomic_strap.png',
    'chain_stage1_plank.png',
    'chain_stage2_capstone.png',
    'chain_stage3_strap.png',
    'chain_stage4_material.png',
    'runner61_atomic_sequence_contact_sheet.png',
    'runner61_atomic_sequence_manifest.json',
    'runner61_executor.log'
)
foreach ($name in $Expected) {
    $path = Join-Path $OutputDir $name
    if (-not (Test-Path $path -PathType Leaf)) { Fail "expected output missing: $path" }
}

Write-Host ''
Write-Host 'RUNNER61-FLUX2-KLEIN-BASE-ATOMIC: PASS - MATRIX COMPLETE / VISUAL VERDICT PENDING' -ForegroundColor Green
Write-Host "Contact sheet: $(Join-Path $OutputDir 'runner61_atomic_sequence_contact_sheet.png')" -ForegroundColor Cyan
Write-Host "Manifest: $(Join-Path $OutputDir 'runner61_atomic_sequence_manifest.json')" -ForegroundColor Cyan
Write-Host "Executor log: $ExecutorLog" -ForegroundColor Cyan
Write-Host 'Decision: if one-fact edits are reliable and survive the sequential chain, expose Base as an iterative editor; if atomic edits themselves fail, move structural editing to the specialized editor branch.' -ForegroundColor Green
