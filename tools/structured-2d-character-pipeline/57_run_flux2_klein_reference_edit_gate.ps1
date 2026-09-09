param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$Workspace = 'Z:\AI\Flux2Klein',
    [int]$Port = 8192,
    [int]$TimeoutMinutes = 180
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ComfyCommit = '672ba9e5e388bd6bfac5ceef61f89ffdd9467200'
$ModelName = 'flux-2-klein-4b-fp8.safetensors'
$ModelSha256 = '97ed34fe0567e436200f2faee3939b88f2b5d99f8af2a4dc16532c4245c0ccb6'
$TextEncoderName = 'qwen_3_4b.safetensors'
$TextEncoderSha256 = '6c671498573ac2f7a5501502ccce8d2b08ea6ca2f661c458e708f36b36edfc5a'
$VaeName = 'flux2-vae.safetensors'
$VaeSha256 = '868fe7b343cc8f3a19dbcfcafbc3d5f888802be3f89bd81b65b3621a066ce8f3'

function Fail([string]$Message) {
    Write-Host "RUNNER57-FLUX2-KLEIN-EDIT: FAIL - $Message" -ForegroundColor Red
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
    $pidRaw = Get-Content -LiteralPath $PidFile -Raw
    if ($null -eq $pidRaw) {
        Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue
        return
    }
    $pidText = ([string]$pidRaw).Trim()
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

function Print-TextFile([string]$Path, [string]$Header, [int]$Tail = 0) {
    Write-Host $Header -ForegroundColor Yellow
    if (-not (Test-Path $Path -PathType Leaf)) {
        Write-Host "  <missing: $Path>" -ForegroundColor DarkYellow
        return
    }
    if ($Tail -gt 0) {
        Get-Content -LiteralPath $Path -Tail $Tail
    } else {
        Get-Content -LiteralPath $Path
    }
}

function Read-TextFileOrEmpty([string]$Path) {
    if (-not (Test-Path $Path -PathType Leaf)) { return '' }
    $raw = Get-Content -LiteralPath $Path -Raw
    if ($null -eq $raw) { return '' }
    return [string]$raw
}

function Quote-ProcessArg([string]$Value) {
    if ($Value -match '[\s"]') {
        return '"' + ($Value -replace '"','\"') + '"'
    }
    return $Value
}

$PortableRoot = Join-Path $Workspace 'ComfyUI_windows_portable'
$Python = Join-Path $PortableRoot 'python_embeded\python.exe'
$ComfyRoot = Join-Path $PortableRoot 'ComfyUI'
$MainPy = Join-Path $ComfyRoot 'main.py'
$Executor = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\flux2_klein_edit_gate.py'
$Protocol = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\adapter_protocol.py'
$Adapter = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\flux2_klein_adapter.py'
$Source = Join-Path $Workspace 'spike\flux2_klein_4b_t2i_probe.png'

foreach ($required in @($Python,$MainPy,$Executor,$Protocol,$Adapter,$Source)) {
    if (-not (Test-Path $required -PathType Leaf)) { Fail "required file missing: $required" }
}

Write-Host ''
Write-Host 'Roguelite Runner 57 - FLUX.2 KLEIN 4B / GENERIC SINGLE + MULTI REFERENCE EDIT GATE' -ForegroundColor Cyan
Write-Host '[PREREQUISITE] Runner56 T2I passed and its isolated runtime is reused.' -ForegroundColor Green
Write-Host '[NO DOWNLOAD] No new checkpoints are downloaded by Runner57.' -ForegroundColor Green
Write-Host '[ADAPTER] Execution goes through the generic Asset Studio adapter contract.' -ForegroundColor Green
Write-Host '[SINGLE] Original gate = previous_approved_state; revise damage/material without replacing identity.' -ForegroundColor Green
Write-Host '[MULTI] Image 1 = structure authority; Image 2 = material/damage authority.' -ForegroundColor Green
Write-Host '[SETTINGS] 768x768, 4 distilled steps, CFG 1.0, Euler, seed 0.' -ForegroundColor Green
Write-Host '[DIAGNOSTICS] Python stdout/stderr are captured as files and empty streams are null-safe.' -ForegroundColor Green
Write-Host ''

Require-Hash (Join-Path $ComfyRoot "models\diffusion_models\$ModelName") $ModelSha256 'FLUX.2 Klein 4B distilled FP8'
Require-Hash (Join-Path $ComfyRoot "models\text_encoders\$TextEncoderName") $TextEncoderSha256 'Qwen3-4B text encoder'
Require-Hash (Join-Path $ComfyRoot "models\vae\$VaeName") $VaeSha256 'FLUX.2 VAE'

if (-not (Get-Command git.exe -ErrorAction SilentlyContinue)) { Fail 'git.exe is required.' }
$currentCommit = (& git.exe -C $ComfyRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $currentCommit -ne $ComfyCommit) {
    Fail "isolated ComfyUI commit mismatch. Expected $ComfyCommit, got $currentCommit. Re-run Runner56 bootstrap before continuing."
}
Write-Host "  ComfyUI pinned commit verified: $currentCommit" -ForegroundColor Green

$Base = "http://127.0.0.1:$Port"
$GateDir = Join-Path $Workspace 'edit_gate'
New-Item -ItemType Directory -Force -Path $GateDir | Out-Null
$PidFile = Join-Path $Workspace '.flux2_klein_edit.pid'
$StdoutLog = Join-Path $GateDir "comfyui_flux2_klein_edit_${Port}_stdout.log"
$StderrLog = Join-Path $GateDir "comfyui_flux2_klein_edit_${Port}_stderr.log"
$ExecutorLog = Join-Path $GateDir 'flux2_klein_edit_gate_executor.log'
$ExecutorStdout = Join-Path $GateDir 'flux2_klein_edit_gate_python_stdout.log'
$ExecutorStderr = Join-Path $GateDir 'flux2_klein_edit_gate_python_stderr.log'

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
            if (Test-Path $StderrLog) { Get-Content -LiteralPath $StderrLog -Tail 220 }
            Stop-Managed $PidFile
            Fail "isolated ComfyUI exited before readiness with code $($process.ExitCode)"
        }
        Start-Sleep -Seconds 1
    }
}
if (-not $ready) {
    Stop-Managed $PidFile
    if (Test-Path $StderrLog) { Get-Content -LiteralPath $StderrLog -Tail 220 }
    Fail "isolated ComfyUI did not become ready at $Base"
}

foreach ($old in @($ExecutorLog,$ExecutorStdout,$ExecutorStderr)) {
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
    Write-Host 'RUNNER57: launching Python executor with deterministic file capture...' -ForegroundColor Cyan
    $executorProcess = Start-Process -FilePath $Python -ArgumentList $pythonArgs -WorkingDirectory $ProjectRepoRoot `
        -RedirectStandardOutput $ExecutorStdout -RedirectStandardError $ExecutorStderr -WindowStyle Hidden -PassThru -Wait
    $executorExit = $executorProcess.ExitCode
} finally {
    Stop-Managed $PidFile
}

$stdoutText = Read-TextFileOrEmpty $ExecutorStdout
$stderrText = Read-TextFileOrEmpty $ExecutorStderr
$combined = @()
$combined += '=== PYTHON STDOUT ==='
$combined += $stdoutText
$combined += '=== PYTHON STDERR ==='
$combined += $stderrText
Set-Content -LiteralPath $ExecutorLog -Value ($combined -join [Environment]::NewLine) -Encoding UTF8

Print-TextFile $ExecutorStdout '--- RUNNER57 PYTHON STDOUT ---'
if (-not [string]::IsNullOrWhiteSpace($stderrText)) {
    Print-TextFile $ExecutorStderr '--- RUNNER57 PYTHON STDERR ---'
}

if ($executorExit -ne 0) {
    Write-Host ''
    Write-Host "RUNNER57-PYTHON-EXIT: $executorExit" -ForegroundColor Red
    Print-TextFile $StderrLog '--- COMFYUI STDERR TAIL ---' 320
    Write-Host "Full combined executor log: $ExecutorLog" -ForegroundColor Yellow
    Fail "reference-edit gate executor exited with code $executorExit"
}

$Single = Join-Path $GateDir 'flux2_klein_single_reference_edit.png'
$Multi = Join-Path $GateDir 'flux2_klein_multi_reference_edit.png'
$Comparison = Join-Path $GateDir 'flux2_klein_edit_gate_comparison_original_single_multi.png'
$Manifest = Join-Path $GateDir 'flux2_klein_edit_gate_manifest.json'
foreach ($expected in @($Single,$Multi,$Comparison,$Manifest,$ExecutorLog)) {
    if (-not (Test-Path $expected -PathType Leaf)) { Fail "expected output missing: $expected" }
}

Write-Host ''
Write-Host 'RUNNER57-FLUX2-KLEIN-EDIT: PASS - TECHNICAL SINGLE+MULTI REFERENCE COMPLETE / VISUAL VERDICT PENDING' -ForegroundColor Green
Write-Host "Single-reference edit: $Single" -ForegroundColor Cyan
Write-Host "Multi-reference edit: $Multi" -ForegroundColor Cyan
Write-Host "Original | Single | Multi comparison: $Comparison" -ForegroundColor Cyan
Write-Host "Manifest: $Manifest" -ForegroundColor Cyan
Write-Host "Executor log: $ExecutorLog" -ForegroundColor Cyan
Write-Host 'Next gate after visual review: activate edit capabilities in the model router and expose the adapter through the generic Studio UI.' -ForegroundColor Green
