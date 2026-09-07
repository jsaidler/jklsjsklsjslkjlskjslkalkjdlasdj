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

Write-Host ''
Write-Host 'Roguelite - first real Sprite Sheet Diffusion Exilada walk8 proof' -ForegroundColor Cyan
Write-Host '[LOCK] Uses complete Exilada master as appearance reference.' -ForegroundColor Green
Write-Host '[LOCK] DWPose extracts the reference-image pose automatically.' -ForegroundColor Green
Write-Host '[LOCK] The 8 walk target poses are generated automatically from the approved C1A guide.' -ForegroundColor Green
Write-Host '[LOCK] No external/manual pose PNGs are required from the operator.' -ForegroundColor Green
Write-Host '[LOCK] FILM disabled for this identity/temporal-coherence proof.' -ForegroundColor Green
Write-Host '[LOCK] Upstream inference.py is not overwritten; a deterministic local patched copy is generated.' -ForegroundColor Green
Write-Host '[LOCK] No whitespace-bearing project path is passed through native argv.' -ForegroundColor Green
Write-Host '[LOCK] Path payload is transported in a JSON request file under Z:\AI.' -ForegroundColor Green
Write-Host ''

$EnvMarker = Join-Path $SsdRoot 'ssd_environment_bootstrap.json'
$DepMarker = Join-Path $SsdRoot 'ssd_dependencies_bootstrap.json'
$ModelMarker = Join-Path $SsdRoot 'ssd_models_bootstrap.json'
$SupportMarker = Join-Path $SsdRoot 'ssd_authoring_support_bootstrap.json'
$InputMarker = Join-Path $SsdRoot 'ssd_exilada_walk8_input.json'
$ResultMarker = Join-Path $SsdRoot 'ssd_exilada_walk8_inference.json'
$ModelTraining = Join-Path $SsdRoot 'repo\ModelTraining'
$Guide = Join-Path $MotionRoot 'g3s_c1_skeleton_walk_guide.json'
$HelperRepo = Join-Path $ProjectRepoRoot 'tools\structured-2d-character-pipeline\g3s_ssd_prepare_walk8.py'
$RequestWrapperRepo = Join-Path $ProjectRepoRoot 'tools\structured-2d-character-pipeline\g3s_ssd_walk8_request.py'
$HelperLocal = Join-Path $SsdRoot 'g3s_ssd_prepare_walk8.py'
$RequestWrapperLocal = Join-Path $SsdRoot 'g3s_ssd_walk8_request.py'
$PrepareRequest = Join-Path $SsdRoot 'ssd_walk8_prepare_request.json'
$TransportProbe = Join-Path $SsdRoot 'ssd_walk8_transport_probe.json'
$ReviewRoot = Join-Path $SsdRoot 'exilada_walk8_review'

foreach ($required in @(
    $EnvMarker,
    $DepMarker,
    $ModelMarker,
    $SupportMarker,
    $ModelTraining,
    $Guide,
    $HelperRepo,
    $RequestWrapperRepo
)) {
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

Write-Host "[OK] Python:        $Python" -ForegroundColor Green
Write-Host "[OK] ModelTraining: $ModelTraining" -ForegroundColor Green
Write-Host "[OK] Master:        $MasterPath" -ForegroundColor Green
Write-Host "[OK] C1A guide:     $Guide" -ForegroundColor Green
Write-Host ''

# Copy the Python control scripts to the SSD workspace. Their native invocation
# paths therefore contain no spaces. All real project paths travel as JSON data,
# not command-line arguments. This deliberately removes the PowerShell 5.1 argv
# failure class instead of trying to quote around it again.
Copy-Item -LiteralPath $HelperRepo -Destination $HelperLocal -Force
Copy-Item -LiteralPath $RequestWrapperRepo -Destination $RequestWrapperLocal -Force

$requestObject = [ordered]@{
    version = 1
    gate = 'SSD_EXILADA_WALK8_PREPARE'
    project_repo_root = $ProjectRepoRoot
    model_training = $ModelTraining
    guide = $Guide
    master = $MasterPath
    marker = $InputMarker
}
$requestObject | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $PrepareRequest -Encoding UTF8
Remove-Item -LiteralPath $TransportProbe -Force -ErrorAction SilentlyContinue

Write-Host '[PREFLIGHT] Verifying JSON control-plane transport of the actual Windows paths...' -ForegroundColor Yellow
$previousPreference = $ErrorActionPreference
try {
    $ErrorActionPreference = 'Continue'
    Push-Location -LiteralPath $SsdRoot
    try {
        & $Python $RequestWrapperLocal 'probe' $PrepareRequest $TransportProbe 2>&1 | Out-Host
        $probeExit = if ($null -eq $LASTEXITCODE) { 1 } else { [int]$LASTEXITCODE }
    } finally {
        Pop-Location
    }
} finally {
    $ErrorActionPreference = $previousPreference
}
if ($probeExit -ne 0) {
    Fail "JSON transport preflight exited with code $probeExit"
}
if (-not (Test-Path -LiteralPath $TransportProbe -PathType Leaf)) {
    Fail "JSON transport preflight did not write: $TransportProbe"
}
try {
    $transport = Get-Content -LiteralPath $TransportProbe -Raw | ConvertFrom-Json
} catch {
    Fail 'cannot parse JSON transport preflight result.'
}
if ($transport.status -ne 'PASS' -or
    [string]$transport.project_repo_root -ne $ProjectRepoRoot -or
    [string]$transport.master -ne $MasterPath -or
    [string]$transport.model_training -ne $ModelTraining -or
    [string]$transport.guide -ne $Guide -or
    [string]$transport.marker -ne $InputMarker) {
    Write-Host "[PREFLIGHT] expected project root: $ProjectRepoRoot" -ForegroundColor DarkYellow
    Write-Host "[PREFLIGHT] received project root: $([string]$transport.project_repo_root)" -ForegroundColor DarkYellow
    Write-Host "[PREFLIGHT] expected master: $MasterPath" -ForegroundColor DarkYellow
    Write-Host "[PREFLIGHT] received master: $([string]$transport.master)" -ForegroundColor DarkYellow
    Fail 'JSON control-plane transport did not preserve the exact path payload.'
}
Write-Host '[OK] JSON path transport preflight PASS.' -ForegroundColor Green
Write-Host ''

Write-Host '[PREP] Extracting Exilada reference pose with DWPose and building 8 clean target pose maps...' -ForegroundColor Yellow
$previousPreference = $ErrorActionPreference
try {
    $ErrorActionPreference = 'Continue'
    Push-Location -LiteralPath $SsdRoot
    try {
        & $Python $RequestWrapperLocal 'prepare' $PrepareRequest 2>&1 | Out-Host
        $prepExit = if ($null -eq $LASTEXITCODE) { 1 } else { [int]$LASTEXITCODE }
    } finally {
        Pop-Location
    }
} finally {
    $ErrorActionPreference = $previousPreference
}
if ($prepExit -ne 0) {
    Fail "input preparation exited with code $prepExit"
}
if (-not (Test-Path -LiteralPath $InputMarker -PathType Leaf)) {
    Fail "input-preparation marker missing: $InputMarker"
}
try {
    $inputState = Get-Content -LiteralPath $InputMarker -Raw | ConvertFrom-Json
} catch {
    Fail 'cannot parse input-preparation marker.'
}
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

# Every argument in this native call is now a no-space path or scalar literal.
$previousPreference = $ErrorActionPreference
try {
    $ErrorActionPreference = 'Continue'
    Push-Location -LiteralPath $ModelTraining
    try {
        & $Python $PatchedInference '--config' $relativeConfig '-W' '512' '-H' '512' '-L' '8' '--steps' '25' '--cfg' '3.5' '--fps' '8' 2>&1 | Out-Host
        $inferExit = if ($null -eq $LASTEXITCODE) { 1 } else { [int]$LASTEXITCODE }
    } finally {
        Pop-Location
    }
} finally {
    $ErrorActionPreference = $previousPreference
}
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
$previousPreference = $ErrorActionPreference
try {
    $ErrorActionPreference = 'Continue'
    Push-Location -LiteralPath $SsdRoot
    try {
        & $Python $HelperLocal 'review' '--predict-dir' $PredictDir '--review-root' $ReviewRoot '--marker' $ResultMarker 2>&1 | Out-Host
        $reviewExit = if ($null -eq $LASTEXITCODE) { 1 } else { [int]$LASTEXITCODE }
    } finally {
        Pop-Location
    }
} finally {
    $ErrorActionPreference = $previousPreference
}
if ($reviewExit -ne 0) {
    Fail "review package exited with code $reviewExit"
}
if (-not (Test-Path -LiteralPath $ResultMarker -PathType Leaf)) {
    Fail "inference result marker missing: $ResultMarker"
}

try {
    $result = Get-Content -LiteralPath $ResultMarker -Raw | ConvertFrom-Json
} catch {
    Fail 'cannot parse inference result marker.'
}
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
