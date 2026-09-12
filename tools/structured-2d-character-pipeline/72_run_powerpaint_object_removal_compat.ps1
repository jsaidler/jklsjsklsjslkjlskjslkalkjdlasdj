param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$RuntimeWorkspace = 'Z:\AI\QwenImageEdit',
    [string]$PowerPaintWorkspace = 'Z:\AI\PowerPaint'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$BrushNetCommit = '505d8ef917ddf3896afd1926770ecc9b099704e2'
$PortableRoot = Join-Path $RuntimeWorkspace 'ComfyUI_windows_portable'
$BasePython = Join-Path $PortableRoot 'python_embeded\python.exe'
$ComfyRoot = Join-Path $PortableRoot 'ComfyUI'
$BrushNetRoot = Join-Path $ComfyRoot 'custom_nodes\ComfyUI-BrushNet'
$BrushNetNodes = Join-Path $BrushNetRoot 'brushnet_nodes.py'
$ModelPatch = Join-Path $BrushNetRoot 'model_patch.py'
$Patcher = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\apply_powerpaint_clip_loader_compat.py'
$Runner = Join-Path $ProjectRepoRoot 'tools\structured-2d-character-pipeline\72_bootstrap_and_run_powerpaint_object_removal.ps1'

function Fail([string]$Message) {
    Write-Host "RUNNER72-COMPAT: FAIL - $Message" -ForegroundColor Red
    exit 1
}

foreach ($required in @($BasePython,$BrushNetNodes,$ModelPatch,$Patcher,$Runner)) {
    if (-not (Test-Path $required -PathType Leaf)) { Fail "required file missing: $required" }
}
if (-not (Test-Path (Join-Path $BrushNetRoot '.git') -PathType Container)) {
    Fail "ComfyUI-BrushNet checkout missing or not a git checkout: $BrushNetRoot"
}

$actualCommit = (& git.exe -C $BrushNetRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $actualCommit -ne $BrushNetCommit) {
    Fail "ComfyUI-BrushNet commit mismatch. Expected $BrushNetCommit got $actualCommit"
}
Write-Host "RUNNER72-COMPAT: pinned ComfyUI-BrushNet commit verified: $actualCommit" -ForegroundColor Green

Write-Host 'RUNNER72-COMPAT: applying verified automatic BrushNet compatibility layer...' -ForegroundColor Cyan
& $BasePython -s $Patcher --brushnet-nodes $BrushNetNodes --model-patch $ModelPatch
if ($LASTEXITCODE -ne 0) { Fail "compatibility patcher exited with code $LASTEXITCODE" }

Write-Host 'RUNNER72-COMPAT: launching canonical Runner72...' -ForegroundColor Cyan
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $Runner `
    -ProjectRepoRoot $ProjectRepoRoot `
    -RuntimeWorkspace $RuntimeWorkspace `
    -PowerPaintWorkspace $PowerPaintWorkspace
$runnerExit = $LASTEXITCODE
if ($runnerExit -ne 0) { Fail "canonical Runner72 exited with code $runnerExit" }

Write-Host ''
Write-Host 'RUNNER72-COMPAT: PASS - AUTOMATIC COMPATIBILITY LAYER + CANONICAL RUNNER72 COMPLETE' -ForegroundColor Green
