param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$SsdRoot = 'Z:\AI\SpriteSheetDiffusionSpike',
    [string]$MotionRoot = 'Z:\AI\RogueliteCharacterPipeline\g3s_c1_skeleton_walk',
    [string]$MasterPath = 'D:\GOOGLE DRIVE\DEV\Roguelite\assets\source\characters\exilada\reference\exilada_master.png'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "SSD-WALK8: FAIL - $Message" -ForegroundColor Red
    exit 1
}

# Windows PowerShell 5.1 Start-Process -ArgumentList ultimately rebuilds one
# command-line string and is not reliable enough for this project when argv
# contains whitespace-bearing paths. Do not use Start-Process for Python here.
# The call operator (&) with an argument array preserves each array item as one
# native argv item. Native stderr is allowed to print, but is not used as
# control flow; the process exit code is checked explicitly.
function Invoke-ControlledPython(
    [string]$PythonExe,
    [string[]]$Arguments,
    [string]$WorkingDirectory
) {
    $previousPreference = $ErrorActionPreference
    $exitCode = 1
    Push-Location -LiteralPath $WorkingDirectory
    try {
        $ErrorActionPreference = 'Continue'
        & $PythonExe @Arguments 2>&1 | Out-Host
        if ($null -ne $LASTEXITCODE) {
            $exitCode = [int]$LASTEXITCODE
        }
    } finally {
        $ErrorActionPreference = $previousPreference
        Pop-Location
    }
    return $exitCode
}

Write-Host ''
Write-Host 'Roguelite - first real Sprite Sheet Diffusion Exilada walk8 proof' -ForegroundColor Cyan
Write-Host '[LOCK] Uses complete Exilada master as appearance reference.' -ForegroundColor Green
Write-Host '[LOCK] DWPose extracts the reference-image pose automatically.' -ForegroundColor Green
Write-Host '[LOCK] The 8 walk target poses are generated automatically from the approved C1A guide.' -ForegroundColor Green
Write-Host '[LOCK] No external/manual pose PNGs are required from the operator.' -ForegroundColor Green
Write-Host '[LOCK] FILM disabled for this identity/temporal-coherence proof.' -ForegroundColor Green
Write-Host '[LOCK] Upstream inference.py is not overwritten; a deterministic local patched copy is generated.' -ForegroundColor Green
Write-Host '[LOCK] Python is invoked with PowerShell call-operator argv splatting; Start-Process is forbidden for this runner.' -ForegroundColor Green
Write-Host '[LOCK] Native argv transport is preflight-tested with the actual paths containing spaces.' -ForegroundColor Green
Write-Host ''

$EnvMarker = Join-Path $SsdRoot 'ssd_environment_bootstrap.json'
$DepMarker = Join-Path $SsdRoot 'ssd_dependencies_bootstrap.json'
$ModelMarker = Join-Path $SsdRoot 'ssd_models_bootstrap.json'
$SupportMarker = Join-Path $SsdRoot 'ssd_authoring_support_bootstrap.json'
$InputMarker = Join-Path $SsdRoot 'ssd_exilada_walk8_input.json'
$ResultMarker = Join-Path $SsdRoot 'ssd_exilada_walk8_inference.json'
$ModelTraining = Join-Path $SsdRoot 'repo\ModelTraining'
$Guide = Join-Path $MotionRoot 'g3s_c1_skeleton_walk_guide.json'
$Helper = Join-Path $ProjectRepoRoot 'tools\structured-2d-character-pipeline\g3s_ssd_prepare_walk8.py'
$ReviewRoot = Join-Path $SsdRoot 'exilada_walk8_review'

foreach ($required in @($EnvMarker, $DepMarker, $ModelMarker, $SupportMarker, $ModelTraining, $Guide, $Helper)) {
    if (-not (Test-Path -LiteralPath $required)) {
        Fail "required path missing: $required"
    }
}
if (-not (Test-Path -LiteralPath $MasterPath -PathType Leaf)) {
    Fail "Exilada master missing at canonical local path: $MasterPath"
}

try {
    $envState = Get-Content -LiteralPath $EnvMarker -Raw | ConvertFrom-Json
    $depState = Get-Content -LiteralPath $DepMarker -Raw | ConvertFrom-Json
    $modelState = Get-Content -LiteralPath $ModelMarker -Raw | ConvertFrom-Json
    $supportState = Get-Content -LiteralPath $SupportMarker -Raw | ConvertFrom-Json
} catch {
    Fail 'cannot parse one or more prerequisite PASS markers.'
}

if ($envState.status -ne 'PASS') { Fail 'environment marker is not PASS.' }
if ($depState.status -ne 'PASS') { Fail 'dependency marker is not PASS.' }
if ($modelState.status -ne 'PASS') { Fail 'core model marker is not PASS.' }
if ($supportState.status -ne 'PASS') { Fail 'authoring support marker is not PASS.' }

$CondaExe = [string]$envState.conda_exe
if (-not (Test-Path -LiteralPath $CondaExe -PathType Leaf)) {
    Fail "conda.exe missing: $CondaExe"
}
$CondaRoot = Split-Path -Parent (Split-Path -Parent $CondaExe)
$Python = Join-Path $CondaRoot 'envs\ssd\python.exe'
if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
    Fail "ssd python.exe missing: $Python"
}

Write-Host "[OK] Python:       $Python" -ForegroundColor Green
Write-Host "[OK] ModelTraining:$ModelTraining" -ForegroundColor Green
Write-Host "[OK] Master:       $MasterPath" -ForegroundColor Green
Write-Host "[OK] C1A guide:    $Guide" -ForegroundColor Green
Write-Host ''

# Regression guard for both runner-28 path failures: use the exact project root
# and master path and require Python to receive them as two intact argv items.
$ArgProbeScript = Join-Path $SsdRoot 'ssd_native_arg_probe.py'
$ArgProbeResult = Join-Path $SsdRoot 'ssd_native_arg_probe.json'
$argProbeSource = @'
import json
import sys
from pathlib import Path
Path(sys.argv[1]).write_text(json.dumps(sys.argv[2:]), encoding="utf-8")
'@
Set-Content -LiteralPath $ArgProbeScript -Value $argProbeSource -Encoding UTF8
Remove-Item -LiteralPath $ArgProbeResult -Force -ErrorAction SilentlyContinue

Write-Host '[PREFLIGHT] Verifying native argument transport for paths containing spaces...' -ForegroundColor Yellow
$argProbeExit = Invoke-ControlledPython -PythonExe $Python -Arguments @($ArgProbeScript, $ArgProbeResult, $ProjectRepoRoot, $MasterPath) -WorkingDirectory $SsdRoot
if ($argProbeExit -ne 0) {
    Fail "native argument preflight exited with code $argProbeExit"
}
if (-not (Test-Path -LiteralPath $ArgProbeResult -PathType Leaf)) {
    Fail "native argument preflight did not write: $ArgProbeResult"
}
try {
    $argProbeValues = @(Get-Content -LiteralPath $ArgProbeResult -Raw | ConvertFrom-Json)
} catch {
    Fail 'cannot parse native argument preflight result.'
}
if ($argProbeValues.Count -ne 2 -or
    [string]$argProbeValues[0] -ne $ProjectRepoRoot -or
    [string]$argProbeValues[1] -ne $MasterPath) {
    Write-Host "[PREFLIGHT] expected[0]: $ProjectRepoRoot" -ForegroundColor DarkYellow
    Write-Host "[PREFLIGHT] expected[1]: $MasterPath" -ForegroundColor DarkYellow
    Write-Host "[PREFLIGHT] received count: $($argProbeValues.Count)" -ForegroundColor DarkYellow
    for ($i = 0; $i -lt $argProbeValues.Count; $i++) {
        Write-Host "[PREFLIGHT] received[$i]: $([string]$argProbeValues[$i])" -ForegroundColor DarkYellow
    }
    Fail 'native argument transport preflight failed; refusing to run preparation with corrupted argv.'
}
Write-Host '[OK] Native argument transport preflight PASS.' -ForegroundColor Green
Write-Host ''

Write-Host '[PREP] Extracting Exilada reference pose with DWPose and building 8 clean target pose maps...' -ForegroundColor Yellow
$prepArgs = @(
    $Helper,
    'prepare',
    '--model-training', $ModelTraining,
    '--guide', $Guide,
    '--master', $MasterPath,
    '--marker', $InputMarker
)
$prepExit = Invoke-ControlledPython -PythonExe $Python -Arguments $prepArgs -WorkingDirectory $ModelTraining
if ($prepExit -ne 0) {
    Fail "input preparation exited with code $prepExit"
}
if (-not (Test-Path -LiteralPath $InputMarker -PathType Leaf)) {
    Fail "input-preparation marker missing: $InputMarker"
}
try { $inputState = Get-Content -LiteralPath $InputMarker -Raw | ConvertFrom-Json } catch { Fail 'cannot parse input-preparation marker.' }
if ($inputState.status -ne 'PASS') { Fail 'input-preparation marker is not PASS.' }
if ([int]$inputState.target_pose_count -ne 8) { Fail 'input-preparation marker does not contain 8 target poses.' }

Write-Host ''
Write-Host '[INFER] Running SSD: 512x512, 8 target frames, 25 steps, CFG 3.5, fp16...' -ForegroundColor Yellow
Write-Host '[NOTE] First model load may take a while. Do not interrupt unless the process emits a controlled failure.' -ForegroundColor DarkYellow

$PatchedInference = [string]$inputState.patched_inference
if (-not (Test-Path -LiteralPath $PatchedInference -PathType Leaf)) {
    Fail "patched inference copy missing: $PatchedInference"
}
$relativeConfig = '.\configs\prompts\inference_exilada_walk8.yaml'

$before = Get-Date
$inferArgs = @(
    $PatchedInference,
    '--config', $relativeConfig,
    '-W', '512',
    '-H', '512',
    '-L', '8',
    '--steps', '25',
    '--cfg', '3.5',
    '--fps', '8'
)
$inferExit = Invoke-ControlledPython -PythonExe $Python -Arguments $inferArgs -WorkingDirectory $ModelTraining
if ($inferExit -ne 0) {
    Fail "SSD inference exited with code $inferExit"
}

$outputRoot = Join-Path $ModelTraining 'output'
if (-not (Test-Path -LiteralPath $outputRoot -PathType Container)) {
    Fail "SSD output root not created: $outputRoot"
}

$predictDirs = Get-ChildItem -LiteralPath $outputRoot -Directory -Recurse -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Name -eq 'predict' -and
        $_.FullName -match '[\\/]exilada[\\/]motions[\\/]walk8[\\/]predict$' -and
        $_.LastWriteTime -ge $before.AddMinutes(-2)
    } |
    Sort-Object LastWriteTime -Descending

if (-not $predictDirs -or $predictDirs.Count -lt 1) {
    $predictDirs = Get-ChildItem -LiteralPath $outputRoot -Directory -Recurse -ErrorAction SilentlyContinue |
        Where-Object {
            $_.Name -eq 'predict' -and
            $_.FullName -match '[\\/]exilada[\\/]motions[\\/]walk8[\\/]predict$'
        } |
        Sort-Object LastWriteTime -Descending
}
if (-not $predictDirs -or $predictDirs.Count -lt 1) {
    Fail 'could not locate SSD walk8 predict directory after successful inference process.'
}

$PredictDir = $predictDirs[0].FullName
$generated = Get-ChildItem -LiteralPath $PredictDir -File -Filter 'frame_*.png' | Sort-Object Name
if ($generated.Count -ne 8) {
    Fail "expected 8 generated frames, found $($generated.Count) in $PredictDir"
}

Write-Host ''
Write-Host '[REVIEW] Building contact sheet and GIF without altering source frames...' -ForegroundColor Yellow
$reviewArgs = @(
    $Helper,
    'review',
    '--predict-dir', $PredictDir,
    '--review-root', $ReviewRoot,
    '--marker', $ResultMarker
)
$reviewExit = Invoke-ControlledPython -PythonExe $Python -Arguments $reviewArgs -WorkingDirectory $ModelTraining
if ($reviewExit -ne 0) {
    Fail "review package exited with code $reviewExit"
}
if (-not (Test-Path -LiteralPath $ResultMarker -PathType Leaf)) {
    Fail "inference result marker missing: $ResultMarker"
}

try { $result = Get-Content -LiteralPath $ResultMarker -Raw | ConvertFrom-Json } catch { Fail 'cannot parse inference result marker.' }
if ($result.status -ne 'PASS_OUTPUT_READY_FOR_VISUAL_QA') {
    Fail "unexpected result status: $($result.status)"
}

Write-Host ''
Write-Host 'SSD-WALK8: OUTPUT READY FOR VISUAL QA' -ForegroundColor Green
Write-Host "FRAMES: $($result.predict_dir)" -ForegroundColor Green
Write-Host "SHEET:  $($result.contact_sheet)" -ForegroundColor Cyan
Write-Host "GIF:    $($result.gif)" -ForegroundColor Cyan
Write-Host "MARKER: $ResultMarker" -ForegroundColor Cyan
Write-Host ''
Write-Host '[NEXT] Inspect the sheet/GIF. This gate is not a visual PASS until identity, anatomy, hair/equipment and motion coherence are reviewed.' -ForegroundColor Yellow
