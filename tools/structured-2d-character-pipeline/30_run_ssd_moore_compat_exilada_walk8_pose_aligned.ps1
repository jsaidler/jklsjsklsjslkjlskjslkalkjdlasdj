param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$SsdRoot = 'Z:\AI\SpriteSheetDiffusionSpike',
    [string]$MotionRoot = 'Z:\AI\RogueliteCharacterPipeline\g3s_c1_skeleton_walk',
    [string]$MasterPath = 'D:\GOOGLE DRIVE\DEV\Roguelite\assets\source\characters\exilada\reference\exilada_master.png'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "SSD-MOORE-POSE-ALIGNED: FAIL - $Message" -ForegroundColor Red
    exit 1
}

function Invoke-NoSpaceProcess(
    [string]$FilePath,
    [string[]]$Arguments,
    [string]$WorkingDirectory
) {
    foreach ($arg in $Arguments) {
        if ($arg -match '\s') {
            throw "external argument contains whitespace; transport it through JSON instead: $arg"
        }
    }

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $FilePath
    $psi.Arguments = ($Arguments -join ' ')
    $psi.WorkingDirectory = $WorkingDirectory
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true

    $proc = New-Object System.Diagnostics.Process
    $proc.StartInfo = $psi
    if (-not $proc.Start()) {
        throw "could not start process: $FilePath"
    }
    $stdoutTask = $proc.StandardOutput.ReadToEndAsync()
    $stderrTask = $proc.StandardError.ReadToEndAsync()
    $proc.WaitForExit()
    $stdout = $stdoutTask.Result
    $stderr = $stderrTask.Result
    if ($stdout) { Write-Host $stdout.TrimEnd() }
    if ($stderr) { Write-Host $stderr.TrimEnd() -ForegroundColor DarkYellow }
    return [int]$proc.ExitCode
}

Write-Host ''
Write-Host 'Roguelite - Exilada walk8 / runner 30 pose-scale registration discriminant' -ForegroundColor Cyan
Write-Host '[CONTROL] Runner 29 technical PASS, visual FAIL: pose obedience weak and lower-limb/foot topology unstable.' -ForegroundColor Yellow
Write-Host '[DEFECT] Previous prep maps 640x360 C1A coordinates to 512x512 with independent X/Y normalization.' -ForegroundColor Yellow
Write-Host '[DEFECT] That equals X scale 0.8 and Y scale 1.4222: 1.7778x relative vertical stretch.' -ForegroundColor Yellow
Write-Host '[TEST] Register the C1A target skeleton uniformly to the DWPose body footprint extracted from the Exilada master.' -ForegroundColor Green
Write-Host '[LOCK] Same model graph, weights, seed, resolution, steps and CFG as runner 29.' -ForegroundColor Green
Write-Host '[LOCK] No crop, no FILM, no CFG/seed sweep, no new action, no model change.' -ForegroundColor Green
Write-Host '[LOCK] Root travel is removed only for target-pose registration; runtime locomotion remains separate from sprite playback.' -ForegroundColor Green
Write-Host ''

$EnvMarker = Join-Path $SsdRoot 'ssd_environment_bootstrap.json'
$DepMarker = Join-Path $SsdRoot 'ssd_dependencies_bootstrap.json'
$ModelMarker = Join-Path $SsdRoot 'ssd_models_bootstrap.json'
$SupportMarker = Join-Path $SsdRoot 'ssd_authoring_support_bootstrap.json'
$BaselineInputMarker = Join-Path $SsdRoot 'ssd_exilada_walk8_input.json'
$AlignedInputMarker = Join-Path $SsdRoot 'ssd_exilada_walk8_pose_aligned_input.json'
$ModelTraining = Join-Path $SsdRoot 'repo\ModelTraining'
$Guide = Join-Path $MotionRoot 'g3s_c1_skeleton_walk_guide.json'

$PrepareHelperRepo = Join-Path $ProjectRepoRoot 'tools\structured-2d-character-pipeline\g3s_ssd_prepare_walk8.py'
$PrepareWrapperRepo = Join-Path $ProjectRepoRoot 'tools\structured-2d-character-pipeline\g3s_ssd_walk8_request.py'
$AlignHelperRepo = Join-Path $ProjectRepoRoot 'tools\structured-2d-character-pipeline\g3s_ssd_align_walk8_poses.py'
$CompatHelperRepo = Join-Path $ProjectRepoRoot 'tools\structured-2d-character-pipeline\g3s_ssd_moore_compat_walk8.py'

$PrepareHelperLocal = Join-Path $SsdRoot 'g3s_ssd_prepare_walk8.py'
$PrepareWrapperLocal = Join-Path $SsdRoot 'g3s_ssd_walk8_request.py'
$AlignHelperLocal = Join-Path $SsdRoot 'g3s_ssd_align_walk8_poses.py'
$CompatHelperLocal = Join-Path $SsdRoot 'g3s_ssd_moore_compat_walk8.py'

$PrepareRequest = Join-Path $SsdRoot 'ssd_walk8_prepare_request.json'
$AlignRequest = Join-Path $SsdRoot 'ssd_walk8_pose_align_request.json'
$CompatRequest = Join-Path $SsdRoot 'ssd_moore_compat_walk8_pose_aligned_request.json'
$AlignedPoseRoot = Join-Path $SsdRoot 'exilada_walk8_pose_aligned_inputs'
$ResultMarker = Join-Path $SsdRoot 'ssd_exilada_walk8_moore_compat_pose_aligned.json'
$OutputRoot = Join-Path $SsdRoot 'exilada_walk8_moore_compat_pose_aligned'

$MooreRoot = Join-Path $SsdRoot 'moore_animateanyone'
$MooreCommit = 'a914ef38aae3733c2f02f29853dd0593372e0cc9'
$MooreRemote = 'https://github.com/MooreThreads/Moore-AnimateAnyone.git'

foreach ($required in @(
    $EnvMarker,
    $DepMarker,
    $ModelMarker,
    $SupportMarker,
    $ModelTraining,
    $Guide,
    $PrepareHelperRepo,
    $PrepareWrapperRepo,
    $AlignHelperRepo,
    $CompatHelperRepo
)) {
    if (-not (Test-Path -LiteralPath $required)) {
        Fail "required path missing: $required"
    }
}
if (-not (Test-Path -LiteralPath $MasterPath -PathType Leaf)) {
    Fail "Exilada master missing: $MasterPath"
}

try {
    $envState = Get-Content -LiteralPath $EnvMarker -Raw | ConvertFrom-Json
    $depState = Get-Content -LiteralPath $DepMarker -Raw | ConvertFrom-Json
    $modelState = Get-Content -LiteralPath $ModelMarker -Raw | ConvertFrom-Json
    $supportState = Get-Content -LiteralPath $SupportMarker -Raw | ConvertFrom-Json
} catch {
    Fail 'cannot parse one or more prerequisite markers.'
}
if ($envState.status -ne 'PASS') { Fail 'environment marker is not PASS.' }
if ($depState.status -ne 'PASS') { Fail 'dependency marker is not PASS.' }
if ($modelState.status -ne 'PASS') { Fail 'model marker is not PASS.' }
if ($supportState.status -ne 'PASS') { Fail 'authoring-support marker is not PASS.' }

$CondaExe = [string]$envState.conda_exe
$CondaRoot = Split-Path -Parent (Split-Path -Parent $CondaExe)
$Python = Join-Path $CondaRoot 'envs\ssd\python.exe'
if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
    Fail "ssd python missing: $Python"
}

$gitCommand = Get-Command git.exe -ErrorAction SilentlyContinue
if ($null -eq $gitCommand) {
    Fail 'git.exe is not available.'
}
$Git = [string]$gitCommand.Source

Write-Host "[OK] Python: $Python" -ForegroundColor Green
Write-Host '[OK] GPU/deps/models/support: PASS' -ForegroundColor Green
Write-Host ''

Copy-Item -LiteralPath $PrepareHelperRepo -Destination $PrepareHelperLocal -Force
Copy-Item -LiteralPath $PrepareWrapperRepo -Destination $PrepareWrapperLocal -Force
Copy-Item -LiteralPath $AlignHelperRepo -Destination $AlignHelperLocal -Force
Copy-Item -LiteralPath $CompatHelperRepo -Destination $CompatHelperLocal -Force

# Rebuild the same canonical baseline package used by runner 29 so the DWPose
# reference body footprint and the exact eight approved C1A states are current.
$prepareObject = [ordered]@{
    version = 1
    gate = 'SSD_EXILADA_WALK8_PREPARE'
    project_repo_root = $ProjectRepoRoot
    model_training = $ModelTraining
    guide = $Guide
    master = $MasterPath
    marker = $BaselineInputMarker
}
$prepareObject | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $PrepareRequest -Encoding UTF8

Write-Host '[PREP] Rebuilding canonical Exilada + C1A baseline inputs...' -ForegroundColor Yellow
$prepareExit = Invoke-NoSpaceProcess -FilePath $Python -Arguments @($PrepareWrapperLocal, 'prepare', $PrepareRequest) -WorkingDirectory $SsdRoot
if ($prepareExit -ne 0) {
    Fail "baseline walk8 preparation exited with code $prepareExit"
}
if (-not (Test-Path -LiteralPath $BaselineInputMarker -PathType Leaf)) {
    Fail "baseline input marker missing: $BaselineInputMarker"
}

# Single discriminant: target-pose spatial registration. The master image and
# every inference parameter remain untouched.
Remove-Item -LiteralPath $AlignedPoseRoot -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath $AlignedInputMarker -Force -ErrorAction SilentlyContinue
$alignObject = [ordered]@{
    version = 1
    gate = 'SSD_EXILADA_WALK8_POSE_ALIGNMENT'
    model_training = $ModelTraining
    input_marker = $BaselineInputMarker
    output_root = $AlignedPoseRoot
    output_marker = $AlignedInputMarker
}
$alignObject | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $AlignRequest -Encoding UTF8

Write-Host ''
Write-Host '[ALIGN] Uniformly registering C1A pose geometry to master DWPose body footprint...' -ForegroundColor Yellow
$alignExit = Invoke-NoSpaceProcess -FilePath $Python -Arguments @($AlignHelperLocal, $AlignRequest) -WorkingDirectory $SsdRoot
if ($alignExit -ne 0) {
    Fail "pose alignment exited with code $alignExit"
}
if (-not (Test-Path -LiteralPath $AlignedInputMarker -PathType Leaf)) {
    Fail "aligned input marker missing: $AlignedInputMarker"
}
try {
    $aligned = Get-Content -LiteralPath $AlignedInputMarker -Raw | ConvertFrom-Json
} catch {
    Fail 'cannot parse aligned input marker.'
}
if ($aligned.status -ne 'PASS') {
    Fail "aligned input status is not PASS: $($aligned.status)"
}

Write-Host ''
Write-Host "[ALIGN] Review artifact: $($aligned.review)" -ForegroundColor Cyan
Write-Host "[ALIGN] Registered height ratio: $($aligned.aligned_to_reference_height_ratio)" -ForegroundColor Cyan
Write-Host ''

# Ensure the exact same pinned Moore source used by runner 29.
Write-Host "[SOURCE] Ensuring Moore-AnimateAnyone source at pinned commit $MooreCommit ..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force $MooreRoot | Out-Null
if (-not (Test-Path -LiteralPath (Join-Path $MooreRoot '.git') -PathType Container)) {
    $code = Invoke-NoSpaceProcess -FilePath $Git -Arguments @('-C', $MooreRoot, 'init') -WorkingDirectory $SsdRoot
    if ($code -ne 0) { Fail "git init failed with code $code" }
}
$null = Invoke-NoSpaceProcess -FilePath $Git -Arguments @('-C', $MooreRoot, 'remote', 'remove', 'origin') -WorkingDirectory $SsdRoot
$code = Invoke-NoSpaceProcess -FilePath $Git -Arguments @('-C', $MooreRoot, 'remote', 'add', 'origin', $MooreRemote) -WorkingDirectory $SsdRoot
if ($code -ne 0) { Fail "git remote add failed with code $code" }
$code = Invoke-NoSpaceProcess -FilePath $Git -Arguments @('-C', $MooreRoot, 'fetch', '--depth', '1', 'origin', $MooreCommit) -WorkingDirectory $SsdRoot
if ($code -ne 0) { Fail "git fetch Moore commit failed with code $code" }
$code = Invoke-NoSpaceProcess -FilePath $Git -Arguments @('-C', $MooreRoot, 'checkout', '--force', '--detach', 'FETCH_HEAD') -WorkingDirectory $SsdRoot
if ($code -ne 0) { Fail "git checkout Moore commit failed with code $code" }
if (-not (Test-Path -LiteralPath (Join-Path $MooreRoot 'src\models\pose_guider.py') -PathType Leaf)) {
    Fail 'pinned Moore source is incomplete after checkout.'
}

Remove-Item -LiteralPath $OutputRoot -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath $ResultMarker -Force -ErrorAction SilentlyContinue

$compatObject = [ordered]@{
    version = 1
    gate = 'SSD_EXILADA_WALK8_MOORE_COMPAT_POSE_ALIGNED'
    experiment = 'RUNNER_30_POSE_SCALE_REGISTRATION_DISCRIMINANT'
    moore_root = $MooreRoot
    moore_commit = $MooreCommit
    model_training = $ModelTraining
    input_marker = $AlignedInputMarker
    output_root = $OutputRoot
    result_marker = $ResultMarker
}
$compatObject | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $CompatRequest -Encoding UTF8

Write-Host ''
Write-Host '[INFER] A/B rerun: same Moore+SSD graph and exact runner-29 generation settings...' -ForegroundColor Yellow
Write-Host '[NOTE] 512x512, 8 frames, 25 steps, CFG 3.5, seed 42, fp16. Only target-pose registration changed.' -ForegroundColor DarkYellow
$inferExit = Invoke-NoSpaceProcess -FilePath $Python -Arguments @($CompatHelperLocal, $CompatRequest) -WorkingDirectory $SsdRoot
if ($inferExit -ne 0) {
    Fail "Moore-compatible aligned inference exited with code $inferExit"
}
if (-not (Test-Path -LiteralPath $ResultMarker -PathType Leaf)) {
    Fail "result marker missing: $ResultMarker"
}
try {
    $result = Get-Content -LiteralPath $ResultMarker -Raw | ConvertFrom-Json
} catch {
    Fail 'cannot parse Moore-compatible aligned result marker.'
}
if ($result.status -ne 'PASS_OUTPUT_READY_FOR_VISUAL_QA') {
    Fail "unexpected result status: $($result.status)"
}

Write-Host ''
Write-Host 'SSD-MOORE-POSE-ALIGNED: OUTPUT READY FOR A/B VISUAL QA' -ForegroundColor Green
Write-Host "POSE REVIEW: $($aligned.review)" -ForegroundColor Cyan
Write-Host "FRAMES:      $((Split-Path -Parent $result.frames[0]))" -ForegroundColor Green
Write-Host "SHEET:       $($result.contact_sheet)" -ForegroundColor Cyan
Write-Host "GIF:         $($result.gif)" -ForegroundColor Cyan
Write-Host "ALIGN MARKER:$AlignedInputMarker" -ForegroundColor Cyan
Write-Host "RESULT:      $ResultMarker" -ForegroundColor Cyan
Write-Host ''
Write-Host '[PASS RULE] Must clearly improve C1A pose readability and lower-limb/foot topology without materially degrading Exilada identity.' -ForegroundColor Yellow
Write-Host '[FAIL RULE] If pose obedience and feet are not clearly better than runner 29, close the Moore-compatible SSD salvage route instead of tuning more parameters.' -ForegroundColor Yellow
