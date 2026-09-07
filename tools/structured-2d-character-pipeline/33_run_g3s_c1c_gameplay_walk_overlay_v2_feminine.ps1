param(
    [string]$RepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$PipelineWorkspace = 'Z:\AI\RogueliteCharacterPipeline'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "G3S-C1C-FEMININE-V2: FAIL - $Message" -ForegroundColor Red
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

$BaseSpec = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_c1_skeleton_walk_spec.json'
$OverlaySpec = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_c1c_gameplay_walk_overlay_v2_feminine_spec.json'
$Exporter = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_c1_export_skeleton_walk.py'
$Review = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_c1_build_skeleton_walk_review.py'
$Overlay = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_c1c_apply_feminine_walk_overlay_v2.py'
$CanonicalBody = Join-Path $RepoRoot 'assets\source\characters\exilada\body\exilada_body_base_b3b_v4.png'
$G2Dir = Join-Path $PipelineWorkspace 'g2'
$G2Blend = Join-Path $G2Dir 'g2_motion_topology.blend'
$G2Manifest = Join-Path $G2Dir 'g2_manifest.json'
$Python = 'Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\python_embeded\python.exe'
$Workspace = Join-Path $PipelineWorkspace 'g3s_c1c_gameplay_walk_overlay_v2_feminine'
$BaselineDir = Join-Path $Workspace 'baseline_az72'
$OverlayDir = Join-Path $Workspace 'overlay_v2_feminine'

foreach ($p in @($BaseSpec,$OverlaySpec,$Exporter,$Review,$Overlay,$CanonicalBody,$G2Blend,$G2Manifest,$Python)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Required file missing: $p" }
}

$Blender = Find-BlenderExe
if (-not $Blender) { Fail 'Blender could not be located.' }

$base = Get-Content -LiteralPath $BaseSpec -Raw | ConvertFrom-Json
if ($base.gate -ne 'G3S-C1A' -or $base.revision -ne 'SKELETON_ONLY_WALK_CYCLE_V1') {
    Fail 'Unexpected canonical C1A skeleton spec.'
}
$overlaySpecData = Get-Content -LiteralPath $OverlaySpec -Raw | ConvertFrom-Json
if ($overlaySpecData.gate -ne 'G3S-C1C_GAMEPLAY_WALK_OVERLAY' -or $overlaySpecData.revision -ne 'GAMEPLAY_WALK_OVERLAY_V2_FEMININE') {
    Fail 'Unexpected feminine-walk overlay spec.'
}
if ($overlaySpecData.status -ne 'RUNNER_READY_REVIEW_REQUIRED') {
    Fail 'Feminine-walk overlay spec is not runner-ready.'
}
if ([math]::Abs([double]$overlaySpecData.facing_azimuth_deg - 72.0) -gt 0.01) {
    Fail "Feminine-walk overlay spec facing mismatch: $($overlaySpecData.facing_azimuth_deg)"
}

New-Item -ItemType Directory -Force -Path $Workspace | Out-Null
Get-ChildItem -LiteralPath $Workspace -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
New-Item -ItemType Directory -Force -Path $BaselineDir | Out-Null
New-Item -ItemType Directory -Force -Path $OverlayDir | Out-Null

Write-Host ''
Write-Host 'Roguelite - G3S-C1C GAMEPLAY WALK OVERLAY V2 / FEMININE' -ForegroundColor Cyan
Write-Host '[LOCK] Locomotion facing = 72 deg from travel heading.' -ForegroundColor Green
Write-Host '[SOURCE] Same G2_CANONICAL_RIG + CMU 105_34 NormalWalk + same eight C1A phases.' -ForegroundColor Green
Write-Host '[V1 RESULT] Runner 32 failed: more controlled, but still read as generic rather than feminine Exilada locomotion.' -ForegroundColor Yellow
Write-Host '[V2 PURPOSE] Add restrained feminine weight transfer and body counter-motion without catwalk exaggeration.' -ForegroundColor Yellow
Write-Host '[V2] Pelvic obliquity + mild pelvic yaw + torso/shoulder counterbalance + compact arms + clean swing-leg clearance.' -ForegroundColor Green
Write-Host '[NO DIFFUSION] Skeleton-only A/B review. SSD remains paused.' -ForegroundColor Green
Write-Host ''

$spec = ($base | ConvertTo-Json -Depth 20 | ConvertFrom-Json)
$spec.camera.azimuth_from_motion_heading_deg = 72.0
$spec.purpose = 'C1C locked 72-degree baseline for feminine gameplay locomotion V2 A/B'
$spec.status = 'RUNNER_READY_REVIEW_REQUIRED'
$specPath = Join-Path $BaselineDir 'g3s_c1c_az72_baseline_spec.json'
$spec | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $specPath -Encoding UTF8

$baselineGuide = Join-Path $BaselineDir 'g3s_c1c_az72_baseline_guide.json'
$stdout = Join-Path $BaselineDir 'blender_stdout.log'
$stderr = Join-Path $BaselineDir 'blender_stderr.log'

Write-Host '[BUILD] Fresh 72-degree baseline...' -ForegroundColor Yellow
$argString = '"{0}" --background --python-exit-code 1 --python "{1}" -- --manifest "{2}" --spec "{3}" --output "{4}"' -f $G2Blend,$Exporter,$G2Manifest,$specPath,$baselineGuide
$proc = Start-Process -FilePath $Blender -ArgumentList $argString -Wait -PassThru -NoNewWindow -RedirectStandardOutput $stdout -RedirectStandardError $stderr
Get-Content $stdout -ErrorAction SilentlyContinue | Out-Host
if ($proc.ExitCode -ne 0) {
    if (Test-Path $stderr) { Get-Content $stderr | Out-Host }
    Fail "Blender baseline exporter exited with code $($proc.ExitCode)."
}
if (-not (Test-Path $baselineGuide -PathType Leaf)) { Fail "72-degree baseline guide missing: $baselineGuide" }

& $Python $Review --guide $baselineGuide --workspace $BaselineDir --body-reference $CanonicalBody
if ($LASTEXITCODE -ne 0) { Fail "Baseline review builder exited with code $LASTEXITCODE" }

$baselineData = Get-Content -LiteralPath $baselineGuide -Raw | ConvertFrom-Json
if ([math]::Abs([double]$baselineData.camera.azimuth_from_motion_heading_deg - 72.0) -gt 0.01) {
    Fail "Baseline guide azimuth mismatch: $($baselineData.camera.azimuth_from_motion_heading_deg)"
}
if ($baselineData.frames.Count -ne 8) { Fail "Baseline expected 8 frames, got $($baselineData.frames.Count)" }

$overlayGuide = Join-Path $OverlayDir 'g3s_c1c_gameplay_walk_overlay_v2_feminine_guide.json'
$overlayMarker = Join-Path $Workspace 'g3s_c1c_gameplay_walk_overlay_v2_feminine.json'

Write-Host ''
Write-Host '[AUTHOR] Applying feminine gameplay locomotion overlay V2...' -ForegroundColor Yellow
& $Python $Overlay --input-guide $baselineGuide --spec $OverlaySpec --output-guide $overlayGuide --marker $overlayMarker
if ($LASTEXITCODE -ne 0) { Fail "Feminine overlay helper exited with code $LASTEXITCODE" }
if (-not (Test-Path $overlayGuide -PathType Leaf)) { Fail "Overlay guide missing: $overlayGuide" }
if (-not (Test-Path $overlayMarker -PathType Leaf)) { Fail "Overlay marker missing: $overlayMarker" }

& $Python $Review --guide $overlayGuide --workspace $OverlayDir --body-reference $CanonicalBody
if ($LASTEXITCODE -ne 0) { Fail "Overlay review builder exited with code $LASTEXITCODE" }

$marker = Get-Content -LiteralPath $overlayMarker -Raw | ConvertFrom-Json
if ($marker.status -ne 'PASS_OUTPUT_READY_FOR_SKELETON_VISUAL_QA') {
    Fail "Unexpected overlay marker status: $($marker.status)"
}
if ($marker.revision -ne 'GAMEPLAY_WALK_OVERLAY_V2_FEMININE') {
    Fail "Unexpected overlay marker revision: $($marker.revision)"
}
if ([double]$marker.max_projected_hip_y_difference_px -gt 8.0) {
    Fail "Projected hip obliquity safety limit exceeded: $($marker.max_projected_hip_y_difference_px)px"
}

$baselineZoom = Join-Path $BaselineDir 'g3s_c1_skeleton_walk_zoom.gif'
$baselineSheet = Join-Path $BaselineDir 'g3s_c1_skeleton_walk_contact_sheet.png'
$overlayZoom = Join-Path $OverlayDir 'g3s_c1_skeleton_walk_zoom.gif'
$overlaySheet = Join-Path $OverlayDir 'g3s_c1_skeleton_walk_contact_sheet.png'
foreach ($p in @($baselineZoom,$baselineSheet,$overlayZoom,$overlaySheet)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Expected A/B review artifact missing: $p" }
}

$summary = [ordered]@{
    gate = 'G3S-C1C_GAMEPLAY_WALK_OVERLAY_V2_FEMININE'
    status = 'REVIEW_REQUIRED'
    facing_azimuth_deg = 72.0
    source_motion = 'CMU 105_34 NormalWalk'
    source_rig = 'G2_CANONICAL_RIG'
    baseline = [ordered]@{
        guide = $baselineGuide
        zoom_gif = $baselineZoom
        contact_sheet = $baselineSheet
    }
    overlay = [ordered]@{
        spec = $OverlaySpec
        guide = $overlayGuide
        marker = $overlayMarker
        zoom_gif = $overlayZoom
        contact_sheet = $overlaySheet
    }
    decision_rule = 'PASS only if the skeleton reads clearly more feminine without catwalk exaggeration, remains grounded/action-ready, and preserves phase/support/anatomical clarity.'
}
$summaryPath = Join-Path $Workspace 'g3s_c1c_gameplay_walk_overlay_v2_feminine_review.json'
$summary | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $summaryPath -Encoding UTF8

Write-Host ''
Write-Host 'G3S-C1C-FEMININE-V2: A/B SKELETON REVIEW PACKAGE READY' -ForegroundColor Green
Write-Host "BASELINE SHEET: $baselineSheet" -ForegroundColor Cyan
Write-Host "BASELINE GIF:   $baselineZoom" -ForegroundColor Cyan
Write-Host "V2 SHEET:       $overlaySheet" -ForegroundColor Cyan
Write-Host "V2 GIF:         $overlayZoom" -ForegroundColor Cyan
Write-Host "MARKER:         $overlayMarker" -ForegroundColor Cyan
Write-Host "SUMMARY:        $summaryPath" -ForegroundColor Cyan
Write-Host ''
Write-Host '[NEXT] Share baseline + V2 contact sheets and zoom GIFs. Do not run SSD until the feminine gameplay walk itself passes.' -ForegroundColor Yellow
