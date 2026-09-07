param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$SsdRoot = 'Z:\AI\SpriteSheetDiffusionSpike',
    [string]$MotionGuide = 'Z:\AI\RogueliteCharacterPipeline\g3s_c1c_gameplay_walk_overlay_v2_feminine\overlay_v2_feminine\g3s_c1c_gameplay_walk_overlay_v2_feminine_guide.json',
    [string]$MasterPath = 'D:\GOOGLE DRIVE\DEV\Roguelite\assets\source\characters\exilada\reference\exilada_master.png'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "G3S-COMPLETE-WALK8: FAIL - $Message" -ForegroundColor Red
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
    if (-not $proc.Start()) { throw "could not start process: $FilePath" }
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
Write-Host 'Roguelite - Exilada COMPLETE CHARACTER walk8 playable spritesheet proof' -ForegroundColor Cyan
Write-Host '[ARCH] Every runtime sprite frame is the complete already-composed character.' -ForegroundColor Green
Write-Host '[ARCH] Runtime body/hair/clothing/equipment layer assembly is abolished.' -ForegroundColor Green
Write-Host '[REFERENCE] exilada_master.png is the initial-state appearance reference.' -ForegroundColor Green
Write-Host '[MOTION] Uses the current 72-degree V2 feminine gameplay walk as a PROVISIONAL driver, not as a final animation approval.' -ForegroundColor Yellow
Write-Host '[SECONDARY] Hair, base cloth, body jiggle/soft motion, bindings, shackles/chains and visible accessories must emerge temporally and be baked into the generated frames.' -ForegroundColor Yellow
Write-Host '[PURPOSE] Produce the actual full-character 8-frame spritesheet now and judge whether this authoring route works as a whole.' -ForegroundColor Cyan
Write-Host '[LOCK] Same proven Moore-compatible graph / released SSD UNets / baseline Moore pose guider+motion.' -ForegroundColor Green
Write-Host '[LOCK] 512x512, 8 frames, 25 steps, CFG 3.5, seed 42, fp16.' -ForegroundColor Green
Write-Host ''

$EnvMarker = Join-Path $SsdRoot 'ssd_environment_bootstrap.json'
$DepMarker = Join-Path $SsdRoot 'ssd_dependencies_bootstrap.json'
$ModelMarker = Join-Path $SsdRoot 'ssd_models_bootstrap.json'
$SupportMarker = Join-Path $SsdRoot 'ssd_authoring_support_bootstrap.json'
$ModelTraining = Join-Path $SsdRoot 'repo\ModelTraining'

$PrepareHelperRepo = Join-Path $ProjectRepoRoot 'tools\structured-2d-character-pipeline\g3s_ssd_prepare_walk8.py'
$PrepareWrapperRepo = Join-Path $ProjectRepoRoot 'tools\structured-2d-character-pipeline\g3s_ssd_walk8_request.py'
$AlignHelperRepo = Join-Path $ProjectRepoRoot 'tools\structured-2d-character-pipeline\g3s_ssd_align_walk8_poses.py'
$CompatHelperRepo = Join-Path $ProjectRepoRoot 'tools\structured-2d-character-pipeline\g3s_ssd_moore_compat_walk8.py'
$PackHelperRepo = Join-Path $ProjectRepoRoot 'tools\structured-2d-character-pipeline\g3s_pack_complete_character_spritesheet.py'

foreach ($required in @(
    $EnvMarker,$DepMarker,$ModelMarker,$SupportMarker,$ModelTraining,
    $MotionGuide,$MasterPath,$PrepareHelperRepo,$PrepareWrapperRepo,
    $AlignHelperRepo,$CompatHelperRepo,$PackHelperRepo
)) {
    if (-not (Test-Path -LiteralPath $required)) { Fail "required path missing: $required" }
}

try {
    $guideData = Get-Content -LiteralPath $MotionGuide -Raw | ConvertFrom-Json
} catch { Fail "cannot parse motion guide: $MotionGuide" }
if ($guideData.gate -ne 'G3S-C1A') { Fail "motion guide has unexpected gate: $($guideData.gate)" }
if ($guideData.frames.Count -ne 8) { Fail "motion guide expected 8 frames, got $($guideData.frames.Count)" }
if (-not $guideData.c1c_gameplay_overlay) { Fail 'motion guide is not the V2 gameplay overlay output.' }
if ($guideData.c1c_gameplay_overlay.revision -ne 'GAMEPLAY_WALK_OVERLAY_V2_FEMININE') {
    Fail "unexpected gameplay overlay revision: $($guideData.c1c_gameplay_overlay.revision)"
}
if ([math]::Abs([double]$guideData.camera.azimuth_from_motion_heading_deg - 72.0) -gt 0.01) {
    Fail "motion guide facing is not locked 72 deg: $($guideData.camera.azimuth_from_motion_heading_deg)"
}

try {
    $envState = Get-Content -LiteralPath $EnvMarker -Raw | ConvertFrom-Json
    $depState = Get-Content -LiteralPath $DepMarker -Raw | ConvertFrom-Json
    $modelState = Get-Content -LiteralPath $ModelMarker -Raw | ConvertFrom-Json
    $supportState = Get-Content -LiteralPath $SupportMarker -Raw | ConvertFrom-Json
} catch { Fail 'cannot parse one or more prerequisite markers.' }
if ($envState.status -ne 'PASS') { Fail 'environment marker is not PASS.' }
if ($depState.status -ne 'PASS') { Fail 'dependency marker is not PASS.' }
if ($modelState.status -ne 'PASS') { Fail 'model marker is not PASS.' }
if ($supportState.status -ne 'PASS') { Fail 'authoring-support marker is not PASS.' }

$CondaExe = [string]$envState.conda_exe
$CondaRoot = Split-Path -Parent (Split-Path -Parent $CondaExe)
$Python = Join-Path $CondaRoot 'envs\ssd\python.exe'
if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) { Fail "ssd python missing: $Python" }
$gitCommand = Get-Command git.exe -ErrorAction SilentlyContinue
if ($null -eq $gitCommand) { Fail 'git.exe is not available.' }
$Git = [string]$gitCommand.Source

$PrepareHelperLocal = Join-Path $SsdRoot 'g3s_ssd_prepare_walk8.py'
$PrepareWrapperLocal = Join-Path $SsdRoot 'g3s_ssd_walk8_request.py'
$AlignHelperLocal = Join-Path $SsdRoot 'g3s_ssd_align_walk8_poses.py'
$CompatHelperLocal = Join-Path $SsdRoot 'g3s_ssd_moore_compat_walk8.py'
$PackHelperLocal = Join-Path $SsdRoot 'g3s_pack_complete_character_spritesheet.py'
Copy-Item -LiteralPath $PrepareHelperRepo -Destination $PrepareHelperLocal -Force
Copy-Item -LiteralPath $PrepareWrapperRepo -Destination $PrepareWrapperLocal -Force
Copy-Item -LiteralPath $AlignHelperRepo -Destination $AlignHelperLocal -Force
Copy-Item -LiteralPath $CompatHelperRepo -Destination $CompatHelperLocal -Force
Copy-Item -LiteralPath $PackHelperRepo -Destination $PackHelperLocal -Force

$ProofRoot = Join-Path $SsdRoot 'exilada_initial_complete_walk8_playable_proof'
$PreparedMarker = Join-Path $ProofRoot 'input.json'
$AlignedMarker = Join-Path $ProofRoot 'aligned_input.json'
$AlignedPoseRoot = Join-Path $ProofRoot 'aligned_poses'
$GeneratedRoot = Join-Path $ProofRoot 'generated_complete_character'
$GeneratedMarker = Join-Path $ProofRoot 'generated_complete_character.json'
$SpriteRoot = Join-Path $ProofRoot 'spritesheet'
$SpriteMetadata = Join-Path $SpriteRoot 'exilada_initial_walk8_complete_spritesheet.json'
$PrepareRequest = Join-Path $ProofRoot 'prepare_request.json'
$AlignRequest = Join-Path $ProofRoot 'align_request.json'
$CompatRequest = Join-Path $ProofRoot 'compat_request.json'
$PackRequest = Join-Path $ProofRoot 'pack_request.json'

Remove-Item -LiteralPath $ProofRoot -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $ProofRoot | Out-Null

$prepareObject = [ordered]@{
    version = 1
    gate = 'G3S_COMPLETE_CHARACTER_WALK8_PREPARE'
    project_repo_root = $ProjectRepoRoot
    model_training = $ModelTraining
    guide = $MotionGuide
    master = $MasterPath
    marker = $PreparedMarker
}
$prepareObject | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $PrepareRequest -Encoding UTF8

Write-Host '[PREP] Building full-master reference + V2 eight-pose package...' -ForegroundColor Yellow
$code = Invoke-NoSpaceProcess -FilePath $Python -Arguments @($PrepareWrapperLocal,'prepare',$PrepareRequest) -WorkingDirectory $SsdRoot
if ($code -ne 0) { Fail "walk8 preparation exited with code $code" }
if (-not (Test-Path -LiteralPath $PreparedMarker -PathType Leaf)) { Fail 'prepared marker missing.' }

$alignObject = [ordered]@{
    version = 1
    gate = 'G3S_COMPLETE_CHARACTER_WALK8_ALIGNMENT'
    model_training = $ModelTraining
    input_marker = $PreparedMarker
    output_root = $AlignedPoseRoot
    output_marker = $AlignedMarker
}
$alignObject | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $AlignRequest -Encoding UTF8

Write-Host '[ALIGN] Registering V2 pose geometry to the complete master reference footprint...' -ForegroundColor Yellow
$code = Invoke-NoSpaceProcess -FilePath $Python -Arguments @($AlignHelperLocal,$AlignRequest) -WorkingDirectory $SsdRoot
if ($code -ne 0) { Fail "pose alignment exited with code $code" }
if (-not (Test-Path -LiteralPath $AlignedMarker -PathType Leaf)) { Fail 'aligned marker missing.' }

$MooreRoot = Join-Path $SsdRoot 'moore_animateanyone'
$MooreCommit = 'a914ef38aae3733c2f02f29853dd0593372e0cc9'
$MooreRemote = 'https://github.com/MooreThreads/Moore-AnimateAnyone.git'
Write-Host "[SOURCE] Ensuring Moore-AnimateAnyone at pinned commit $MooreCommit ..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force $MooreRoot | Out-Null
if (-not (Test-Path -LiteralPath (Join-Path $MooreRoot '.git') -PathType Container)) {
    $code = Invoke-NoSpaceProcess -FilePath $Git -Arguments @('-C',$MooreRoot,'init') -WorkingDirectory $SsdRoot
    if ($code -ne 0) { Fail "git init failed with code $code" }
}
$null = Invoke-NoSpaceProcess -FilePath $Git -Arguments @('-C',$MooreRoot,'remote','remove','origin') -WorkingDirectory $SsdRoot
$code = Invoke-NoSpaceProcess -FilePath $Git -Arguments @('-C',$MooreRoot,'remote','add','origin',$MooreRemote) -WorkingDirectory $SsdRoot
if ($code -ne 0) { Fail "git remote add failed with code $code" }
$code = Invoke-NoSpaceProcess -FilePath $Git -Arguments @('-C',$MooreRoot,'fetch','--depth','1','origin',$MooreCommit) -WorkingDirectory $SsdRoot
if ($code -ne 0) { Fail "git fetch failed with code $code" }
$code = Invoke-NoSpaceProcess -FilePath $Git -Arguments @('-C',$MooreRoot,'checkout','--force','--detach','FETCH_HEAD') -WorkingDirectory $SsdRoot
if ($code -ne 0) { Fail "git checkout failed with code $code" }

$compatObject = [ordered]@{
    version = 1
    gate = 'G3S_COMPLETE_CHARACTER_WALK8_MOORE_COMPAT'
    experiment = 'RUNNER_34_COMPLETE_CHARACTER_PLAYABLE_PROOF'
    moore_root = $MooreRoot
    moore_commit = $MooreCommit
    model_training = $ModelTraining
    input_marker = $AlignedMarker
    output_root = $GeneratedRoot
    result_marker = $GeneratedMarker
}
$compatObject | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $CompatRequest -Encoding UTF8

Write-Host '[INFER] Generating COMPLETE Exilada frames from the initial master...' -ForegroundColor Yellow
Write-Host '[QA] Hair/cloth/jiggle/restraints are part of the same temporal-generation test; detached or frozen secondary masses count as visible failure, not a separate runtime layer task.' -ForegroundColor DarkYellow
$code = Invoke-NoSpaceProcess -FilePath $Python -Arguments @($CompatHelperLocal,$CompatRequest) -WorkingDirectory $SsdRoot
if ($code -ne 0) { Fail "complete-character inference exited with code $code" }
if (-not (Test-Path -LiteralPath $GeneratedMarker -PathType Leaf)) { Fail 'generated result marker missing.' }

$packObject = [ordered]@{
    version = 1
    gate = 'G3S_COMPLETE_CHARACTER_SPRITESHEET_PACK'
    result_marker = $GeneratedMarker
    alignment_marker = $AlignedMarker
    output_root = $SpriteRoot
    metadata_path = $SpriteMetadata
    master = $MasterPath
    frame_duration_ms = 83
}
$packObject | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $PackRequest -Encoding UTF8

Write-Host '[PACK] Removing connected neutral background and packing the eight COMPLETE character frames...' -ForegroundColor Yellow
$code = Invoke-NoSpaceProcess -FilePath $Python -Arguments @($PackHelperLocal,$PackRequest) -WorkingDirectory $SsdRoot
if ($code -ne 0) { Fail "complete-character spritesheet packing exited with code $code" }
if (-not (Test-Path -LiteralPath $SpriteMetadata -PathType Leaf)) { Fail 'spritesheet metadata missing.' }

$meta = Get-Content -LiteralPath $SpriteMetadata -Raw | ConvertFrom-Json
if ($meta.status -ne 'PASS_OUTPUT_READY_FOR_PLAYABLE_VISUAL_QA') { Fail "unexpected spritesheet status: $($meta.status)" }
if (-not $meta.complete_character_baked_per_frame) { Fail 'spritesheet metadata does not declare complete-character frames.' }
if ($meta.runtime_character_layer_assembly) { Fail 'runtime layer assembly unexpectedly enabled.' }

Write-Host ''
Write-Host 'G3S-COMPLETE-WALK8: COMPLETE CHARACTER SPRITESHEET READY FOR QA' -ForegroundColor Green
Write-Host "MASTER:    $MasterPath" -ForegroundColor Cyan
Write-Host "POSE QA:   $((Get-Content -LiteralPath $AlignedMarker -Raw | ConvertFrom-Json).review)" -ForegroundColor Cyan
Write-Host "GEN SHEET: $((Get-Content -LiteralPath $GeneratedMarker -Raw | ConvertFrom-Json).contact_sheet)" -ForegroundColor Cyan
Write-Host "GEN GIF:   $((Get-Content -LiteralPath $GeneratedMarker -Raw | ConvertFrom-Json).gif)" -ForegroundColor Cyan
Write-Host "SPRITE:    $($meta.sheet)" -ForegroundColor Green
Write-Host "PREVIEW:   $($meta.preview_gif)" -ForegroundColor Green
Write-Host "METADATA:  $SpriteMetadata" -ForegroundColor Green
Write-Host ''
Write-Host '[DECISION] Judge the complete motion as one baked character: body locomotion + jiggle + hair + base clothing + restraints/accessories.' -ForegroundColor Yellow
Write-Host '[NOTE] This is a playable-proof artifact, not final production approval. Armor/accessory variation strategy remains a later offline-authoring problem.' -ForegroundColor Yellow
