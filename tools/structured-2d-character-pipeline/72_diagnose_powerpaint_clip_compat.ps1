param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$RuntimeWorkspace = 'Z:\AI\QwenImageEdit',
    [string]$PowerPaintWorkspace = 'Z:\AI\PowerPaint'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "RUNNER72-CLIP-DIAG: FAIL - $Message" -ForegroundColor Red
    exit 1
}

$PortableRoot = Join-Path $RuntimeWorkspace 'ComfyUI_windows_portable'
$ComfyRoot = Join-Path $PortableRoot 'ComfyUI'
$BasePython = Join-Path $PortableRoot 'python_embeded\python.exe'
$PyDepsRoot = Join-Path $PowerPaintWorkspace 'pydeps'
$OverlayLauncher = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\python_overlay_launcher.py'
$Diagnostic = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\powerpaint_clip_compat_diagnostic.py'
$BaseClip = Join-Path $ComfyRoot 'models\clip\model.fp16.safetensors'
$PowerPaintBin = Join-Path $ComfyRoot 'models\inpaint\powerpaint\pytorch_model.bin'
$Report = Join-Path $PowerPaintWorkspace 'runner72_clip_compat_diagnostic.json'

foreach ($required in @($BasePython,$OverlayLauncher,$Diagnostic,$BaseClip,$PowerPaintBin)) {
    if (-not (Test-Path $required -PathType Leaf)) { Fail "required file missing: $required" }
}
if (-not (Test-Path $PyDepsRoot -PathType Container)) { Fail "dependency overlay missing: $PyDepsRoot" }

Write-Host 'Roguelite Runner72 - PowerPaint CLIP compatibility diagnostic' -ForegroundColor Cyan
Write-Host '[NO DOWNLOAD] [NO DIFFUSION] Compares current ComfyUI CLIP state against learned PowerPaint text encoder.' -ForegroundColor Green
Write-Host ''

Push-Location $ComfyRoot
try {
    & $BasePython -s $OverlayLauncher $PyDepsRoot $Diagnostic `
        --comfy-root $ComfyRoot `
        --base-clip $BaseClip `
        --powerpaint-bin $PowerPaintBin `
        --report $Report
    if ($LASTEXITCODE -ne 0) { Fail "diagnostic executor exited with code $LASTEXITCODE" }
}
finally {
    Pop-Location
}

if (-not (Test-Path $Report -PathType Leaf)) { Fail "diagnostic report was not written: $Report" }
Write-Host ''
Write-Host "RUNNER72-CLIP-DIAG: report=$Report" -ForegroundColor Green
Write-Host 'RUNNER72-CLIP-DIAG: PASS - DIAGNOSTIC COMPLETE / NO INFERENCE EXECUTED' -ForegroundColor Green
