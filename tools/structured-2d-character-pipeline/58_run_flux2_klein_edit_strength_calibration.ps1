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
    Write-Host "RUNNER58-FLUX2-KLEIN-EDIT-CALIBRATION: FAIL - $Message" -ForegroundColor Red
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
    if ($Value -match '[\s"]') {
        return '"' + ($Value -replace '"','\"') + '"'
    }
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
$Executor = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\flux2_klein_edit_strength_calibration.py'
$Adapter = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\flux2_klein_adapter.py'
$Protocol = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\adapter_protocol.py'
$Original = Join-Path $Workspace 'spike\flux2_klein_4b_t2i_probe.png'

foreach ($required in @($Python,$MainPy,$Executor,$Adapter,$Protocol,$Original)) {
    if (-not (Test-Path $required -PathType Leaf)) { Fail "required file missing: $required" }
}

Write-Host ''
Write-Host 'Roguelite Runner 58 - FLUX.2 KLEIN 4B / EDIT STRENGTH + MULTI-REFERENCE OBEDIENCE CALIBRATION' -ForegroundColor Cyan
Write-Host '[PREREQUISITE] Runner56 T2I passed; Runner57 single+multi edit passed technically but visual edit strength was insufficient.' -ForegroundColor Green
Write-Host '[NO DOWNLOAD] Reuses the exact Runner56 Klein runtime and checkpoints.' -ForegroundColor Green
Write-Host '[SINGLE MATRIX] Same original + explicit binary edits at 4 / 8 / 12 steps.' -ForegroundColor Green
Write-Host '[MATERIAL REF] Generates one separate severe-decay material board automatically.' -ForegroundColor Green
Write-Host '[MULTI MATRIX] Original structure + material board at 4 / 8 / 12 steps.' -ForegroundColor Green
Write-Host '[METRICS] Records pixel-difference magnitude against the original; visual review remains authoritative.' -ForegroundColor Green
Write-Host ''

Require-Hash (Join-Path $ComfyRoot "models\diffusion_models\$ModelName") $ModelSha256 'FLUX.2 Klein 4B distilled FP8'
Require-Hash (Join-Path $ComfyRoot "models\text_encoders\$TextEncoderName") $TextEncoderSha256 'Qwen3-4B text encoder'
Require-Hash (Join-Path $ComfyRoot "models\vae\$VaeName") $VaeSha256 'FLUX.2 VAE'

if (-not (Get-Command git.exe -ErrorAction SilentlyContinue)) { Fail 'git.exe is required.' }
$currentCommit = (& git.exe -C $ComfyRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $currentCommit -ne $ComfyCommit) {
    Fail "isolated ComfyUI commit mismatch. Expected $ComfyCommit, got $currentCommit"
}
Write-Host "  ComfyUI pinned commit verified: $currentCommit" -ForegroundColor Green

$Base = "http://127.0.0.1:$Port"
$OutputDir = Join-Path $Workspace 'edit_strength_calibration'
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$PidFile = Join-Path $Workspace '.flux2_klein_runner58.pid'
$StdoutLog = Join-Path $OutputDir "comfyui_runner58_${Port}_stdout.log"
$StderrLog = Join-Path $OutputDir "comfyui_runner58_${Port}_stderr.log"
$ExecutorStdout = Join-Path $OutputDir 'runner58_python_stdout.log'
$ExecutorStderr = Join-Path $OutputDir 'runner58_python_stderr.log'
$ExecutorLog = Join-Path $OutputDir 'runner58_executor.log'

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
            Print-TextFile $StderrLog '--- COMFYUI STDERR ---' 240
            Stop-Managed $PidFile
            Fail "isolated ComfyUI exited before readiness with code $($process.ExitCode)"
        }
        Start-Sleep -Seconds 1
    }
}
if (-not $ready) {
    Print-TextFile $StderrLog '--- COMFYUI STDERR ---' 240
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
    Write-Host 'RUNNER58: launching calibration executor...' -ForegroundColor Cyan
    $executorProcess = Start-Process -FilePath $Python -ArgumentList $pythonArgs -WorkingDirectory $ProjectRepoRoot `
        -RedirectStandardOutput $ExecutorStdout -RedirectStandardError $ExecutorStderr -WindowStyle Hidden -PassThru -Wait
    $executorExit = $executorProcess.ExitCode
} finally {
    Stop-Managed $PidFile
}

$stdoutText = Read-TextFileOrEmpty $ExecutorStdout
$stderrText = Read-TextFileOrEmpty $ExecutorStderr
Set-Content -LiteralPath $ExecutorLog -Value (@('=== PYTHON STDOUT ===',$stdoutText,'=== PYTHON STDERR ===',$stderrText) -join [Environment]::NewLine) -Encoding UTF8

Print-TextFile $ExecutorStdout '--- RUNNER58 PYTHON STDOUT ---'
if (-not [string]::IsNullOrWhiteSpace($stderrText)) {
    Print-TextFile $ExecutorStderr '--- RUNNER58 PYTHON STDERR ---'
}

if ($executorExit -ne 0) {
    Write-Host "RUNNER58-PYTHON-EXIT: $executorExit" -ForegroundColor Red
    Print-TextFile $StderrLog '--- COMFYUI STDERR TAIL ---' 320
    Fail "calibration executor exited with code $executorExit"
}

$Expected = @(
    'single_binary_steps04.png',
    'single_binary_steps08.png',
    'single_binary_steps12.png',
    'material_decay_reference.png',
    'multi_structure_material_steps04.png',
    'multi_structure_material_steps08.png',
    'multi_structure_material_steps12.png',
    'runner58_contact_sheet.png',
    'runner58_manifest.json',
    'runner58_executor.log'
)
foreach ($name in $Expected) {
    $path = Join-Path $OutputDir $name
    if (-not (Test-Path $path -PathType Leaf)) { Fail "expected output missing: $path" }
}

Write-Host ''
Write-Host 'RUNNER58-FLUX2-KLEIN-EDIT-CALIBRATION: PASS - TECHNICAL MATRIX COMPLETE / VISUAL VERDICT PENDING' -ForegroundColor Green
Write-Host "Contact sheet: $(Join-Path $OutputDir 'runner58_contact_sheet.png')" -ForegroundColor Cyan
Write-Host "Manifest: $(Join-Path $OutputDir 'runner58_manifest.json')" -ForegroundColor Cyan
Write-Host "Executor log: $ExecutorLog" -ForegroundColor Cyan
Write-Host 'Visual gate: approve production reference editing only if at least one single and one multi recipe produce strong requested changes without losing gate identity/camera.' -ForegroundColor Green
