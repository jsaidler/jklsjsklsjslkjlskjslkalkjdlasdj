param(
    [string]$RepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$PipelineWorkspace = 'Z:\AI\RogueliteCharacterPipeline'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "G3S-C1A: FAIL - $Message" -ForegroundColor Red
    exit 1
}

function Find-BlenderExe {
    $candidates = @()
    if ($env:BLENDER_EXE) { $candidates += $env:BLENDER_EXE }
    $cmd = Get-Command blender.exe -ErrorAction SilentlyContinue
    if ($cmd) { $candidates += $cmd.Source }
    foreach ($root in @('C:\Program Files\Blender Foundation','C:\Program Files (x86)\Blender Foundation')) {
        if (Test-Path $root) {
            $candidates += Get-ChildItem -Path $root -Filter blender.exe -Recurse -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName
        }
    }
    $found = @($candidates | Where-Object { $_ -and (Test-Path $_ -PathType Leaf) } | Select-Object -Unique)
    if ($found.Count -eq 0) { return $null }
    return ($found | Sort-Object -Descending | Select-Object -First 1)
}

$ArchitectureLock = Join-Path $RepoRoot 'docs\G3S_ANIMATION_ARCHITECTURE_LOCK.md'
$Spec = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_c1_pose_guide_spec.json'
$Exporter = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_c1_export_hidden_pose_guide_v5.py'
$ReviewBuilder = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_c1_build_pose_guide_review.py'
$RetargetApproval = Join-Path $RepoRoot 'tools\deterministic-character-pipeline\g3v_retarget_approval.json'
$G3VFailure = Join-Path $RepoRoot 'tools\deterministic-character-pipeline\g3v_failure.json'
$CanonicalBody = Join-Path $RepoRoot 'assets\source\characters\exilada\body\exilada_body_base_b3b_v4.png'
$G3VBlend = Join-Path $PipelineWorkspace 'g3v\g3v_representative_proxy.blend'
$Python = 'Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\python_embeded\python.exe'
$Workspace = Join-Path $PipelineWorkspace 'g3s_c1_hidden_pose_guide'

foreach ($p in @($ArchitectureLock,$Spec,$Exporter,$ReviewBuilder,$RetargetApproval,$G3VFailure,$CanonicalBody,$G3VBlend,$Python)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Required file missing: $p" }
}

$specData = Get-Content -LiteralPath $Spec -Raw | ConvertFrom-Json
if ($specData.gate -ne 'G3S-C1A' -or $specData.status -ne 'RUNNER_READY_REVIEW_REQUIRED') {
    Fail 'C1A spec is not in RUNNER_READY_REVIEW_REQUIRED state.'
}

$retarget = Get-Content -LiteralPath $RetargetApproval -Raw | ConvertFrom-Json
if ($retarget.gate -ne 'G3V-R' -or $retarget.status -ne 'PASS' -or $retarget.method -ne 'DIRECTION_SPACE_FK') {
    Fail 'Validated hidden-3D DIRECTION_SPACE_FK backbone is not PASS.'
}

$g3vFail = Get-Content -LiteralPath $G3VFailure -Raw | ConvertFrom-Json
if ($g3vFail.gate -ne 'G3V' -or $g3vFail.status -ne 'FAIL') {
    Fail 'G3V direct-visible-route failure marker is missing or inconsistent.'
}

$bodyHash = (Get-FileHash -LiteralPath $CanonicalBody -Algorithm SHA256).Hash.ToLowerInvariant()
if ($bodyHash -ne '702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858') {
    Fail "Canonical B3B body PNG hash mismatch: $bodyHash"
}

$Blender = Find-BlenderExe
if (-not $Blender) { Fail 'Blender could not be located.' }

New-Item -ItemType Directory -Force -Path $Workspace | Out-Null
Get-ChildItem -LiteralPath $Workspace -File -ErrorAction SilentlyContinue | Remove-Item -Force

Write-Host ''
Write-Host 'Roguelite - G3S-C1A HIDDEN-3D FULL-POSE GUIDE' -ForegroundColor Cyan
Write-Host '[LOCK] Final visible animation remains persistent native 2D pixel art.' -ForegroundColor Green
Write-Host '[LOCK] Hidden 3D owns pose/laterality/near-far/depth/contact guide data only.' -ForegroundColor Green
Write-Host '[LOCK] G3V direct visible 3D route remains FAIL/CLOSED.' -ForegroundColor Green
Write-Host '[LOCK] No single-still warp/cutout/cage animation is used.' -ForegroundColor Green
Write-Host '[LOCK] No model/API/diffusion is used in C1A.' -ForegroundColor Green
Write-Host '[LOCK] Nothing is promoted automatically.' -ForegroundColor Yellow
Write-Host '[FIX] C1A V5 renders camera-space depth directly on the original evaluated G3V_BODY with a guide-only shader. No bake, proxy or topology substitution.' -ForegroundColor DarkCyan
Write-Host "[OK] Blender: $Blender" -ForegroundColor Green
Write-Host ''

$stdout = Join-Path $Workspace 'blender_c1a_stdout.log'
$stderr = Join-Path $Workspace 'blender_c1a_stderr.log'
$argString = '"{0}" --background --python-exit-code 1 --python "{1}" -- --g3v-blend "{2}" --approval "{3}" --output-dir "{4}" --pitch 26 --hero-px 128' -f $G3VBlend,$Exporter,$G3VBlend,$RetargetApproval,$Workspace
$proc = Start-Process -FilePath $Blender -ArgumentList $argString -Wait -PassThru -NoNewWindow -RedirectStandardOutput $stdout -RedirectStandardError $stderr
Get-Content $stdout -ErrorAction SilentlyContinue | Out-Host
if ($proc.ExitCode -ne 0) {
    if (Test-Path $stderr) { Get-Content $stderr | Out-Host }
    Fail "Blender C1A exporter exited with code $($proc.ExitCode)."
}

$PoseJson = Join-Path $Workspace 'g3s_c1_contact_left_pose_guide.json'
$Neutral = Join-Path $Workspace 'g3s_c1_contact_left_hidden3d_neutral.png'
$Silhouette = Join-Path $Workspace 'g3s_c1_contact_left_silhouette_guide.png'
$Regions = Join-Path $Workspace 'g3s_c1_contact_left_regions_guide.png'
$Depth = Join-Path $Workspace 'g3s_c1_contact_left_depth_guide.png'
foreach ($p in @($PoseJson,$Neutral,$Silhouette,$Regions,$Depth)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Expected hidden pose-guide output missing: $p" }
}

& $Python $ReviewBuilder --workspace $Workspace --body-reference $CanonicalBody
if ($LASTEXITCODE -ne 0) { Fail "C1A review builder exited with code $LASTEXITCODE" }

$Skeleton = Join-Path $Workspace 'g3s_c1_contact_left_skeleton_overlay.png'
$Contact = Join-Path $Workspace 'g3s_c1_contact_left_pose_guide_contact_sheet.png'
$Crops = @(
    'g3s_c1_contact_left_neutral_crop_96x160.png',
    'g3s_c1_contact_left_silhouette_crop_96x160.png',
    'g3s_c1_contact_left_regions_crop_96x160.png',
    'g3s_c1_contact_left_depth_crop_96x160.png',
    'g3s_c1_contact_left_skeleton_crop_96x160.png'
) | ForEach-Object { Join-Path $Workspace $_ }
foreach ($p in @($Skeleton,$Contact) + $Crops) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Expected C1A review output missing: $p" }
}

$pose = Get-Content -LiteralPath $PoseJson -Raw | ConvertFrom-Json
if ($pose.gate -ne 'G3S-C1A' -or $pose.status -ne 'REVIEW_REQUIRED') { Fail 'Unexpected C1A pose manifest status.' }
if ($pose.hidden_3d_visible_art_owner -ne $false) { Fail 'Hidden 3D ownership contract violated.' }
if ([double]$pose.travel_vector_screen_dx_px -ge 0) { Fail 'Pose guide does not satisfy left-facing/left-travel direction contract.' }
if ([math]::Abs([double]$pose.camera.measured_body_height_px - 128.0) -gt 4.0) {
    Fail "C1A body height is outside camera tolerance: $($pose.camera.measured_body_height_px)px"
}
if ($pose.depth_guide.mode -ne 'original_body_camera_space_shader') {
    Fail "C1A depth guide did not use the original-body camera-space shader: $($pose.depth_guide.mode)"
}
if ($pose.depth_guide.source_geometry_mutated -ne $false) {
    Fail 'C1A V5 unexpectedly mutated source body geometry.'
}
if ($pose.depth_guide.proxy_object_used -ne $false) {
    Fail 'C1A V5 unexpectedly used a detached geometry proxy.'
}
if ($pose.depth_guide.topology_index_mapping_used -ne $false) {
    Fail 'C1A V5 unexpectedly used source/evaluated polygon-index mapping.'
}
if ([double]$pose.depth_guide.projected_height_delta_px -gt 0.01) {
    Fail "C1A depth shader changed projected guide scale by $($pose.depth_guide.projected_height_delta_px)px"
}

Write-Host ''
Write-Host 'G3S-C1A: FULL POSE GUIDE REVIEW PACKAGE READY' -ForegroundColor Green
Write-Host "EVENT:         $($pose.selected_event)"
Write-Host "SOURCE FRAME:  $($pose.selected_source_frame)"
Write-Host "NEAR SIDE:     $($pose.near_anatomical_side)"
Write-Host "FAR SIDE:      $($pose.far_anatomical_side)"
Write-Host "CONTACT SHEET: $Contact"
Write-Host "POSE JSON:     $PoseJson"
Write-Host ''
Write-Host 'STOP. Share the C1A contact sheet. Do not author/promote C1B pixels until this full hidden-pose guide is visually reviewed.' -ForegroundColor Yellow
