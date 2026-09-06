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

$Approval = Join-Path $RepoRoot 'tools\deterministic-character-pipeline\g2_approval.json'
$Spec = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_c1_skeleton_walk_spec.json'
$Exporter = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_c1_export_skeleton_walk.py'
$Review = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_c1_build_skeleton_walk_review.py'
$CanonicalBody = Join-Path $RepoRoot 'assets\source\characters\exilada\body\exilada_body_base_b3b_v4.png'
$G2Dir = Join-Path $PipelineWorkspace 'g2'
$G2Blend = Join-Path $G2Dir 'g2_motion_topology.blend'
$G2Manifest = Join-Path $G2Dir 'g2_manifest.json'
$G2Result = Join-Path $G2Dir 'g2_result.json'
$Python = 'Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\python_embeded\python.exe'
$Workspace = Join-Path $PipelineWorkspace 'g3s_c1_skeleton_walk'
$Guide = Join-Path $Workspace 'g3s_c1_skeleton_walk_guide.json'

foreach ($p in @($Approval,$Spec,$Exporter,$Review,$CanonicalBody,$G2Blend,$G2Manifest,$G2Result,$Python)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Required file missing: $p" }
}

$approvalData = Get-Content -LiteralPath $Approval -Raw | ConvertFrom-Json
if ($approvalData.gate -ne 'G2' -or $approvalData.status -ne 'PASS') { Fail 'Canonical G2 motion/topology gate is not PASS.' }
if ($approvalData.motion_source -ne 'CMU 105_34 NormalWalk') { Fail "Unexpected G2 motion source: $($approvalData.motion_source)" }

$specData = Get-Content -LiteralPath $Spec -Raw | ConvertFrom-Json
if ($specData.gate -ne 'G3S-C1A' -or $specData.revision -ne 'SKELETON_ONLY_WALK_CYCLE_V1' -or $specData.status -ne 'RUNNER_READY_REVIEW_REQUIRED') {
    Fail 'C1A skeleton walk spec is not runner-ready.'
}
if ($specData.hard_locks.skinned_human_mesh_used -ne $false -or $specData.hard_locks.mpfb_body_used -ne $false) {
    Fail 'C1A spec violates the skeleton-only architecture.'
}

$bodyHash = (Get-FileHash -LiteralPath $CanonicalBody -Algorithm SHA256).Hash.ToLowerInvariant()
if ($bodyHash -ne '702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858') {
    Fail "Canonical B3B body hash changed: $bodyHash"
}

$Blender = Find-BlenderExe
if (-not $Blender) { Fail 'Blender could not be located.' }

New-Item -ItemType Directory -Force -Path $Workspace | Out-Null
Get-ChildItem -LiteralPath $Workspace -File -ErrorAction SilentlyContinue | Remove-Item -Force

Write-Host ''
Write-Host 'Roguelite - G3S-C1A SKELETON-ONLY WALK CYCLE' -ForegroundColor Cyan
Write-Host '[LOCK] Source = existing validated G2_CANONICAL_RIG + CMU 105_34 NormalWalk.' -ForegroundColor Green
Write-Host '[LOCK] No MPFB body, no skinned mesh, no hidden human render.' -ForegroundColor Green
Write-Host '[LOCK] No static B3B warp/cutout/cage deformation.' -ForegroundColor Green
Write-Host '[LOCK] No image-generation model, paid API or download.' -ForegroundColor Green
Write-Host '[OUTPUT] Eight real-motion gait states + in-place/travel/zoom animated GIFs.' -ForegroundColor Cyan
Write-Host "[OK] Blender: $Blender" -ForegroundColor Green
Write-Host ''

$stdout = Join-Path $Workspace 'blender_skeleton_stdout.log'
$stderr = Join-Path $Workspace 'blender_skeleton_stderr.log'
$argString = '"{0}" --background --python-exit-code 1 --python "{1}" -- --manifest "{2}" --spec "{3}" --output "{4}"' -f $G2Blend,$Exporter,$G2Manifest,$Spec,$Guide
$proc = Start-Process -FilePath $Blender -ArgumentList $argString -Wait -PassThru -NoNewWindow -RedirectStandardOutput $stdout -RedirectStandardError $stderr
Get-Content $stdout -ErrorAction SilentlyContinue | Out-Host
if ($proc.ExitCode -ne 0) {
    if (Test-Path $stderr) { Get-Content $stderr | Out-Host }
    Fail "Blender skeleton exporter exited with code $($proc.ExitCode)."
}
if (-not (Test-Path $Guide -PathType Leaf)) { Fail "Skeleton guide was not created: $Guide" }

& $Python $Review --guide $Guide --workspace $Workspace --body-reference $CanonicalBody
if ($LASTEXITCODE -ne 0) { Fail "Skeleton review builder exited with code $LASTEXITCODE" }

$InPlace = Join-Path $Workspace 'g3s_c1_skeleton_walk_in_place.gif'
$Travel = Join-Path $Workspace 'g3s_c1_skeleton_walk_travel.gif'
$Zoom = Join-Path $Workspace 'g3s_c1_skeleton_walk_zoom.gif'
$Sheet = Join-Path $Workspace 'g3s_c1_skeleton_walk_contact_sheet.png'
foreach ($p in @($InPlace,$Travel,$Zoom,$Sheet)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Expected review output missing: $p" }
}

$guideData = Get-Content -LiteralPath $Guide -Raw | ConvertFrom-Json
if ($guideData.gate -ne 'G3S-C1A' -or $guideData.revision -ne 'SKELETON_ONLY_WALK_CYCLE_V1' -or $guideData.status -ne 'REVIEW_REQUIRED') {
    Fail 'Unexpected C1A skeleton guide manifest.'
}
if ($guideData.source_rig -ne 'G2_CANONICAL_RIG') { Fail "Unexpected source rig: $($guideData.source_rig)" }
if ($guideData.skinned_human_mesh_used -ne $false -or $guideData.mpfb_body_used -ne $false) { Fail 'Skeleton-only contract violated at runtime.' }
if ($guideData.hidden_3d_visible_art_owner -ne $false) { Fail 'Hidden skeleton was incorrectly marked as visible-art owner.' }
if ($guideData.frames.Count -ne 8) { Fail "Expected 8 gait states, got $($guideData.frames.Count)." }
if ([double]$guideData.root_travel_total_dx_px -ge 0) { Fail "Root travel is not screen-left: $($guideData.root_travel_total_dx_px)px" }
if ([math]::Abs([double]$guideData.camera.max_measured_skeleton_height_px - 128.0) -gt 4.0) {
    Fail "Skeleton guide scale is outside tolerance: $($guideData.camera.max_measured_skeleton_height_px)px"
}
$expectedEvents = @('left_contact','left_down','left_passing','left_up','right_contact','right_down','right_passing','right_up')
for ($i = 0; $i -lt 8; $i++) {
    if ($guideData.frames[$i].event -ne $expectedEvents[$i]) { Fail "Unexpected gait event at index ${i}: $($guideData.frames[$i].event)" }
}

Write-Host ''
Write-Host 'G3S-C1A: SKELETON WALK REVIEW PACKAGE READY' -ForegroundColor Green
Write-Host "IN PLACE: $InPlace"
Write-Host "TRAVEL:   $Travel"
Write-Host "ZOOM:     $Zoom"
Write-Host "SHEET:    $Sheet"
Write-Host "GUIDE:    $Guide"
Write-Host ''
Write-Host 'Share the ZOOM GIF and CONTACT SHEET. This is the last hidden-motion sanity gate before native-2D walk-pose authoring.' -ForegroundColor Yellow
