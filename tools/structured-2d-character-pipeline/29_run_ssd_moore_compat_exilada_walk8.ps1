param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$SsdRoot = 'Z:\AI\SpriteSheetDiffusionSpike',
    [string]$MotionRoot = 'Z:\AI\RogueliteCharacterPipeline\g3s_c1_skeleton_walk',
    [string]$MasterPath = 'D:\GOOGLE DRIVE\DEV\Roguelite\assets\source\characters\exilada\reference\exilada_master.png'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "SSD-MOORE-COMPAT: FAIL - $Message" -ForegroundColor Red
    exit 1
}

# Use System.Diagnostics.Process rather than PowerShell native stderr handling.
# Every external argument is required to contain no whitespace; all real project
# paths travel inside JSON request files under Z:\AI.
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
Write-Host 'Roguelite - Exilada walk8 / Moore-compatible fallback using released SSD UNets' -ForegroundColor Cyan
Write-Host '[FACT] Exact upstream SSD inference is blocked: the authors did not release its custom multi-scale pose_guider.pth.' -ForegroundColor Yellow
Write-Host '[ROUTE] Use the original Moore-AnimateAnyone graph + released SSD fine-tuned denoising/reference UNets.' -ForegroundColor Green
Write-Host '[ROUTE] Use the already-downloaded Moore baseline pose_guider + motion module.' -ForegroundColor Green
Write-Host '[LOCK] This is explicitly NOT claimed to be the exact published SSD graph.' -ForegroundColor Yellow
Write-Host '[LOCK] No manual pose folder; the approved C1A walk remains the target motion.' -ForegroundColor Green
Write-Host ''

$EnvMarker = Join-Path $SsdRoot 'ssd_environment_bootstrap.json'
$DepMarker = Join-Path $SsdRoot 'ssd_dependencies_bootstrap.json'
$ModelMarker = Join-Path $SsdRoot 'ssd_models_bootstrap.json'
$SupportMarker = Join-Path $SsdRoot 'ssd_authoring_support_bootstrap.json'
$InputMarker = Join-Path $SsdRoot 'ssd_exilada_walk8_input.json'
$ModelTraining = Join-Path $SsdRoot 'repo\ModelTraining'
$Guide = Join-Path $MotionRoot 'g3s_c1_skeleton_walk_guide.json'

$PrepareHelperRepo = Join-Path $ProjectRepoRoot 'tools\structured-2d-character-pipeline\g3s_ssd_prepare_walk8.py'
$PrepareWrapperRepo = Join-Path $ProjectRepoRoot 'tools\structured-2d-character-pipeline\g3s_ssd_walk8_request.py'
$CompatHelperRepo = Join-Path $ProjectRepoRoot 'tools\structured-2d-character-pipeline\g3s_ssd_moore_compat_walk8.py'

$PrepareHelperLocal = Join-Path $SsdRoot 'g3s_ssd_prepare_walk8.py'
$PrepareWrapperLocal = Join-Path $SsdRoot 'g3s_ssd_walk8_request.py'
$CompatHelperLocal = Join-Path $SsdRoot 'g3s_ssd_moore_compat_walk8.py'

$PrepareRequest = Join-Path $SsdRoot 'ssd_walk8_prepare_request.json'
$CompatRequest = Join-Path $SsdRoot 'ssd_moore_compat_walk8_request.json'
$ResultMarker = Join-Path $SsdRoot 'ssd_exilada_walk8_moore_compat.json'
$OutputRoot = Join-Path $SsdRoot 'exilada_walk8_moore_compat'

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
Write-Host "[OK] GPU/deps/models/support: PASS" -ForegroundColor Green
Write-Host ''

# Ensure walk8 preparation exists and is current. Paths with spaces travel in JSON.
Copy-Item -LiteralPath $PrepareHelperRepo -Destination $PrepareHelperLocal -Force
Copy-Item -LiteralPath $PrepareWrapperRepo -Destination $PrepareWrapperLocal -Force
Copy-Item -LiteralPath $CompatHelperRepo -Destination $CompatHelperLocal -Force

$prepareObject = [ordered]@{
    version = 1
    gate = 'SSD_EXILADA_WALK8_PREPARE'
    project_repo_root = $ProjectRepoRoot
    model_training = $ModelTraining
    guide = $Guide
    master = $MasterPath
    marker = $InputMarker
}
$prepareObject | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $PrepareRequest -Encoding UTF8

Write-Host '[PREP] Rebuilding the canonical Exilada master + C1A walk8 pose package...' -ForegroundColor Yellow
$prepareExit = Invoke-NoSpaceProcess -FilePath $Python -Arguments @($PrepareWrapperLocal, 'prepare', $PrepareRequest) -WorkingDirectory $SsdRoot
if ($prepareExit -ne 0) {
    Fail "walk8 preparation exited with code $prepareExit"
}
if (-not (Test-Path -LiteralPath $InputMarker -PathType Leaf)) {
    Fail "walk8 input marker missing: $InputMarker"
}

# Fetch only the pinned Moore source code; all heavyweight model files are reused.
# Bootstrap is idempotent: origin is explicitly created or repaired on every run.
Write-Host ''
Write-Host "[SOURCE] Ensuring Moore-AnimateAnyone source at pinned commit $MooreCommit ..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force $MooreRoot | Out-Null
if (-not (Test-Path -LiteralPath (Join-Path $MooreRoot '.git') -PathType Container)) {
    $code = Invoke-NoSpaceProcess -FilePath $Git -Arguments @('-C', $MooreRoot, 'init') -WorkingDirectory $SsdRoot
    if ($code -ne 0) { Fail "git init failed with code $code" }
}

# Remove/re-add origin so a partially interrupted earlier run cannot leave the
# source bootstrap in an unrecoverable state.
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

$compatObject = [ordered]@{
    version = 1
    gate = 'SSD_EXILADA_WALK8_MOORE_COMPAT'
    moore_root = $MooreRoot
    moore_commit = $MooreCommit
    model_training = $ModelTraining
    input_marker = $InputMarker
    output_root = $OutputRoot
    result_marker = $ResultMarker
}
$compatObject | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $CompatRequest -Encoding UTF8
Remove-Item -LiteralPath $ResultMarker -Force -ErrorAction SilentlyContinue

Write-Host ''
Write-Host '[INFER] Running Moore-compatible graph with released SSD fine-tuned UNets...' -ForegroundColor Yellow
Write-Host '[NOTE] 512x512, 8 frames, 25 steps, CFG 3.5, fp16. Model output is buffered and printed when the process ends.' -ForegroundColor DarkYellow
$inferExit = Invoke-NoSpaceProcess -FilePath $Python -Arguments @($CompatHelperLocal, $CompatRequest) -WorkingDirectory $SsdRoot
if ($inferExit -ne 0) {
    Fail "Moore-compatible inference exited with code $inferExit"
}
if (-not (Test-Path -LiteralPath $ResultMarker -PathType Leaf)) {
    Fail "result marker missing: $ResultMarker"
}
try {
    $result = Get-Content -LiteralPath $ResultMarker -Raw | ConvertFrom-Json
} catch {
    Fail 'cannot parse Moore-compatible result marker.'
}
if ($result.status -ne 'PASS_OUTPUT_READY_FOR_VISUAL_QA') {
    Fail "unexpected result status: $($result.status)"
}

Write-Host ''
Write-Host 'SSD-MOORE-COMPAT: OUTPUT READY FOR VISUAL QA' -ForegroundColor Green
Write-Host "FRAMES: $((Split-Path -Parent $result.frames[0]))" -ForegroundColor Green
Write-Host "SHEET:  $($result.contact_sheet)" -ForegroundColor Cyan
Write-Host "GIF:    $($result.gif)" -ForegroundColor Cyan
Write-Host "MARKER: $ResultMarker" -ForegroundColor Cyan
Write-Host ''
Write-Host '[NEXT] Review identity/anatomy/hair/restraints/motion. This fallback output is not the exact published SSD graph and must be judged empirically.' -ForegroundColor Yellow
