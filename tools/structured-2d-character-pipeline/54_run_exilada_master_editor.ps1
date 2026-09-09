param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$Workspace = 'Z:\AI\FluxKontext',
    [int]$Port = 8191,
    [int]$UiPort = 7860,
    [int]$TimeoutMinutes = 180
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$KontextName = 'flux1-dev-kontext_fp8_scaled.safetensors'
$KontextSha256 = '630ba795ec64283b4230ea23cf79406c2c68b7c578229ed139f30043eadb30a2'
$ClipName = 'clip_l.safetensors'
$ClipSha256 = '660c6f5b1abae9dc498ac2d21e1347d2abdb0cf6c0c8576cd796491d9a6cdd'
$T5Name = 't5xxl_fp16.safetensors'
$T5Sha256 = '6e480b09fae049a72d2a8c5fbccb8d3e92febeb233bbe9dfe7256958a9167635'
$VaeName = 'ae.safetensors'
$VaeSha256 = 'afc8e28272cd15db3919bacdb6918ce9c1ed22e96cb12c4d5ed0fba823529e38'
$GradioSpec = 'gradio==5.44.1'

function Fail([string]$Message) {
    Write-Host "RUNNER54-EXILADA-MASTER-EDITOR: FAIL - $Message" -ForegroundColor Red
    exit 1
}

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Require-Hash([string]$Path, [string]$Expected, [string]$Label) {
    if (-not (Test-Path $Path -PathType Leaf)) { Fail "required $Label missing: $Path" }
    $actual = Get-Sha256 $Path
    if ($actual -ne $Expected.ToLowerInvariant()) { Fail "$Label SHA256 mismatch. Expected $Expected, got $actual" }
    Write-Host "  $Label verified." -ForegroundColor Green
}

function Stop-Managed([string]$PidFile) {
    if (-not (Test-Path $PidFile -PathType Leaf)) { return }
    $pidText = (Get-Content -LiteralPath $PidFile -Raw).Trim()
    $managedPid = 0
    if ([int]::TryParse($pidText, [ref]$managedPid) -and $managedPid -gt 0) {
        $p = Get-Process -Id $managedPid -ErrorAction SilentlyContinue
        if ($p) {
            Write-Host "Stopping managed Kontext ComfyUI PID $managedPid" -ForegroundColor DarkGray
            Stop-Process -Id $managedPid -Force
            Start-Sleep -Seconds 2
        }
    }
    Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue
}

$PortableRoot = Join-Path $Workspace 'ComfyUI_windows_portable'
$ComfyRoot = Join-Path $PortableRoot 'ComfyUI'
$Python = Join-Path $PortableRoot 'python_embeded\python.exe'
$MainPy = Join-Path $ComfyRoot 'main.py'
$Editor = Join-Path $ProjectRepoRoot 'tools\flux-kontext-spike\exilada_master_editor.py'
$CanonicalMaster = Join-Path $ProjectRepoRoot 'assets\source\characters\exilada\reference\exilada_master.png'
$CanonicalBody = Join-Path $ProjectRepoRoot 'assets\source\characters\exilada\reference\exilada_body_turnaround_nude_approved.jpg'
$UiDeps = Join-Path $Workspace 'master_editor_pydeps'

foreach ($f in @($Python,$MainPy,$Editor,$CanonicalMaster)) {
    if (-not (Test-Path $f -PathType Leaf)) { Fail "required file missing: $f" }
}

Write-Host ''
Write-Host 'Roguelite Runner 54 - LOCAL EXILADA MASTER EDITOR' -ForegroundColor Cyan
Write-Host '[PURPOSE] Revise the canonical character design before further H3/spritesheet work.' -ForegroundColor Yellow
Write-Host '[LOCAL ONLY] The editor runs on your installed FLUX.1 Kontext and opens at 127.0.0.1.' -ForegroundColor Green
Write-Host '[DESIGN] Explicit controls for cloth damage/exposure, anatomy, material state and 1980s sword-and-sorcery direction.' -ForegroundColor Green
Write-Host '[REFERENCES] Optional nude anatomy turnaround + two arbitrary visual-direction uploads.' -ForegroundColor Green
Write-Host '[RESOLUTION] Native Kontext output is retained. No 128/192/384px sprite downscale exists in this editor.' -ForegroundColor Green
Write-Host '[VERSIONING] Candidates never replace exilada_master.png until the explicit APPROVE button is pressed.' -ForegroundColor Green
Write-Host ''

Require-Hash (Join-Path $ComfyRoot "models\diffusion_models\$KontextName") $KontextSha256 'Kontext FP8'
Require-Hash (Join-Path $ComfyRoot "models\text_encoders\$ClipName") $ClipSha256 'CLIP-L'
Require-Hash (Join-Path $ComfyRoot "models\text_encoders\$T5Name") $T5Sha256 'T5XXL FP16'
Require-Hash (Join-Path $ComfyRoot "models\vae\$VaeName") $VaeSha256 'Flux VAE'

if (Test-Path $CanonicalBody -PathType Leaf) {
    Write-Host "  Nude anatomy turnaround available: $CanonicalBody" -ForegroundColor Green
} else {
    Write-Host '  Nude anatomy turnaround not found at the canonical path. Editor remains usable; its checkbox will default off.' -ForegroundColor Yellow
}

New-Item -ItemType Directory -Force -Path $UiDeps | Out-Null
$GradioCheck = @"
import sys
sys.path.insert(0, r'''$UiDeps''')
import gradio
print(gradio.__version__)
"@
$gradioReady = $false
try {
    $version = (& $Python -s -c $GradioCheck 2>$null | Select-Object -Last 1).Trim()
    if ($LASTEXITCODE -eq 0 -and $version) {
        Write-Host "  Isolated Gradio UI dependency already present: $version" -ForegroundColor Green
        $gradioReady = $true
    }
} catch { }

if (-not $gradioReady) {
    Write-Host "Installing isolated UI dependency $GradioSpec into $UiDeps" -ForegroundColor Cyan
    & $Python -s -m pip install --disable-pip-version-check --no-warn-script-location --target $UiDeps $GradioSpec
    if ($LASTEXITCODE -ne 0) { Fail "could not install $GradioSpec into isolated UI dependency folder" }
    try {
        $version = (& $Python -s -c $GradioCheck | Select-Object -Last 1).Trim()
        Write-Host "  Gradio ready: $version" -ForegroundColor Green
    } catch {
        Fail 'Gradio installation completed but import verification failed.'
    }
}

$Base = "http://127.0.0.1:$Port"
$PidFile = Join-Path $Workspace '.flux_kontext_master_editor.pid'
$UserDir = Join-Path $ComfyRoot 'user'
New-Item -ItemType Directory -Force -Path $UserDir | Out-Null
$StdoutLog = Join-Path $UserDir "comfyui_master_editor_${Port}_stdout.log"
$StderrLog = Join-Path $UserDir "comfyui_master_editor_${Port}_stderr.log"

Stop-Managed $PidFile
try {
    $null = Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 2
    Fail "port $Port is already serving an unmanaged process; stop it or launch Runner54 with a different -Port"
} catch {
    if ($_.Exception.Message -like '*unmanaged process*') { throw }
}

$launchArgs = @('-s',$MainPy,'--windows-standalone-build','--listen','127.0.0.1','--port',"$Port",'--disable-auto-launch')
$process = Start-Process -FilePath $Python -ArgumentList $launchArgs -WorkingDirectory $ComfyRoot `
    -RedirectStandardOutput $StdoutLog -RedirectStandardError $StderrLog -WindowStyle Hidden -PassThru
Set-Content -LiteralPath $PidFile -Value $process.Id -Encoding ASCII
Write-Host "Started Kontext ComfyUI PID $($process.Id)" -ForegroundColor Green

$ready = $false
for ($i=0; $i -lt 300; $i++) {
    try {
        $null = Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 2
        $ready = $true
        break
    } catch {
        if ($process.HasExited) {
            if (Test-Path $StderrLog) { Get-Content $StderrLog -Tail 180 }
            Stop-Managed $PidFile
            Fail "Kontext ComfyUI exited before the editor started with code $($process.ExitCode)"
        }
        Start-Sleep -Seconds 1
    }
}
if (-not $ready) {
    Stop-Managed $PidFile
    Fail "Kontext API did not become ready at $Base"
}

Write-Host ''
Write-Host "Opening Exilada Master Editor at http://127.0.0.1:$UiPort" -ForegroundColor Cyan
Write-Host 'Close the editor with Ctrl+C in this PowerShell window when you finish.' -ForegroundColor DarkGray
Write-Host ''

$oldPythonPath = $env:PYTHONPATH
try {
    if ($oldPythonPath) {
        $env:PYTHONPATH = "$UiDeps;$oldPythonPath"
    } else {
        $env:PYTHONPATH = $UiDeps
    }
    & $Python -s $Editor `
        --project-root $ProjectRepoRoot `
        --workspace $Workspace `
        --comfy-root $ComfyRoot `
        --port $Port `
        --ui-port $UiPort `
        --timeout-minutes $TimeoutMinutes
    $editorExit = $LASTEXITCODE
} finally {
    $env:PYTHONPATH = $oldPythonPath
    Stop-Managed $PidFile
}

if ($editorExit -ne 0) {
    if (Test-Path $StderrLog) { Get-Content $StderrLog -Tail 220 }
    Fail "editor exited with code $editorExit"
}

Write-Host 'RUNNER54-EXILADA-MASTER-EDITOR: CLOSED CLEANLY' -ForegroundColor Green
