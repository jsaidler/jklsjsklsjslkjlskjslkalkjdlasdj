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
$FullVaeName = 'flux2-vae.safetensors'
$FullVaeSha256 = '868fe7b343cc8f3a19dbcfcafbc3d5f888802be3f89bd81b65b3621a066ce8f3'

function Fail([string]$Message) {
    Write-Host "RUNNER60-FLUX2-KLEIN-BASE-PARITY: FAIL - $Message" -ForegroundColor Red
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
$Executor = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\flux2_klein_base_official_parity_gate.py'
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
$FullVaePath = Join-Path $ComfyRoot "models\vae\$FullVaeName"

Write-Host ''
Write-Host 'Roguelite Runner 60 - FLUX.2 KLEIN 4B BASE / OFFICIAL-PARITY DIAGNOSTIC' -ForegroundColor Cyan
Write-Host '[WHY] Runner59 produced cyan/posterized outputs, but its Base graph diverged from the official CFG-5 conditioning recipe.' -ForegroundColor Yellow
Write-Host '[NO DOWNLOAD] Reuses every model file already installed by Runners56/59.' -ForegroundColor Green
Write-Host '[PARITY FIX] Negative conditioning is CLIPTextEncode("") rather than ConditioningZeroOut(positive).' -ForegroundColor Green
Write-Host '[PARITY FIX] Reference images use ImageScaleToTotalPixels nearest-exact at 1 MP; edit resolution follows the scaled first reference.' -ForegroundColor Green
Write-Host '[DIAGNOSTIC] Base small-decoder round-trip + full-VAE control + Base T2I + Base single + Base multi.' -ForegroundColor Green
Write-Host '[SAMPLING] Official Base recipe: Euler, CFG 5, 20 steps.' -ForegroundColor Green
Write-Host ''

Require-Hash $BaseModelPath $BaseModelSha256 'FLUX.2 Klein Base 4B FP8'
Require-Hash $TextEncoderPath $TextEncoderSha256 'Qwen3-4B text encoder'
Require-Hash $BaseVaePath $BaseVaeSha256 'FLUX.2 full-encoder/small-decoder VAE'
Require-Hash $FullVaePath $FullVaeSha256 'FLUX.2 full VAE control'

if (-not (Get-Command git.exe -ErrorAction SilentlyContinue)) { Fail 'git.exe is required.' }
$currentCommit = (& git.exe -C $ComfyRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $currentCommit -ne $ComfyCommit) {
    Fail "isolated ComfyUI commit mismatch. Expected $ComfyCommit, got $currentCommit"
}
Write-Host "  ComfyUI pinned commit verified: $currentCommit" -ForegroundColor Green

$Base = "http://127.0.0.1:$Port"
$OutputDir = Join-Path $Workspace 'base_official_parity'
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$PidFile = Join-Path $Workspace '.flux2_klein_runner60.pid'
$StdoutLog = Join-Path $OutputDir "comfyui_runner60_${Port}_stdout.log"
$StderrLog = Join-Path $OutputDir "comfyui_runner60_${Port}_stderr.log"
$ExecutorStdout = Join-Path $OutputDir 'runner60_python_stdout.log'
$ExecutorStderr = Join-Path $OutputDir 'runner60_python_stderr.log'
$ExecutorLog = Join-Path $OutputDir 'runner60_executor.log'

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
    Write-Host 'RUNNER60: launching official-parity diagnostic executor...' -ForegroundColor Cyan
    $executorProcess = Start-Process -FilePath $Python -ArgumentList $pythonArgs -WorkingDirectory $ProjectRepoRoot `
        -RedirectStandardOutput $ExecutorStdout -RedirectStandardError $ExecutorStderr -WindowStyle Hidden -PassThru -Wait
    $executorExit = $executorProcess.ExitCode
} finally {
    Stop-Managed $PidFile
}

$stdoutText = Read-TextFileOrEmpty $ExecutorStdout
$stderrText = Read-TextFileOrEmpty $ExecutorStderr
Set-Content -LiteralPath $ExecutorLog -Value (@('=== PYTHON STDOUT ===',$stdoutText,'=== PYTHON STDERR ===',$stderrText) -join [Environment]::NewLine) -Encoding UTF8

Print-TextFile $ExecutorStdout '--- RUNNER60 PYTHON STDOUT ---'
if (-not [string]::IsNullOrWhiteSpace($stderrText)) {
    Print-TextFile $ExecutorStderr '--- RUNNER60 PYTHON STDERR ---'
}

if ($executorExit -ne 0) {
    Write-Host "RUNNER60-PYTHON-EXIT: $executorExit" -ForegroundColor Red
    Print-TextFile $StderrLog '--- COMFYUI STDERR TAIL ---' 380
    Fail "official-parity diagnostic executor exited with code $executorExit"
}

$Expected = @(
    'base_small_decoder_roundtrip.png',
    'full_flux2_vae_roundtrip.png',
    'base_official_t2i_steps20.png',
    'base_official_single_steps20.png',
    'base_official_multi_steps20.png',
    'runner60_official_parity_contact_sheet.png',
    'runner60_official_parity_manifest.json',
    'runner60_executor.log'
)
foreach ($name in $Expected) {
    $path = Join-Path $OutputDir $name
    if (-not (Test-Path $path -PathType Leaf)) { Fail "expected output missing: $path" }
}

Write-Host ''
Write-Host 'RUNNER60-FLUX2-KLEIN-BASE-PARITY: PASS - DIAGNOSTIC MATRIX COMPLETE / VISUAL VERDICT PENDING' -ForegroundColor Green
Write-Host "Contact sheet: $(Join-Path $OutputDir 'runner60_official_parity_contact_sheet.png')" -ForegroundColor Cyan
Write-Host "Manifest: $(Join-Path $OutputDir 'runner60_official_parity_manifest.json')" -ForegroundColor Cyan
Write-Host "Executor log: $ExecutorLog" -ForegroundColor Cyan
Write-Host 'Decision: do not reject Base or move to Qwen until this parity matrix identifies whether the Runner59 cyan failure came from VAE, sampling, or the old conditioning graph.' -ForegroundColor Green
