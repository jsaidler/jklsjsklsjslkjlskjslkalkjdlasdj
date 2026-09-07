param(
    [string]$RepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$PipelineWorkspace = 'Z:\AI\RogueliteCharacterPipeline'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "G3S-C1C-OVERLAY: FAIL - $Message" -ForegroundColor Red
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
$Exporter = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_c1_export_skeleton_walk.py'
$Review = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_c1_build_skeleton_walk_review.py'
$Overlay = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_c1c_apply_gameplay_walk_overlay.py'
$CanonicalBody = Join-Path $RepoRoot 'assets\source\characters\exilada\body\exilada_body_base_b3b_v4.png'
$G2Dir = Join-Path $PipelineWorkspace 'g2'
$G2Blend = Join-Path $G2Dir 'g2_motion_topology.blend'
$G2Manifest = Join-Path $G2Dir 'g2_manifest.json'
$Python = 'Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\python_embeded\python.exe'
$Workspace = Join-Path $PipelineWorkspace 'g3s_c1c_gameplay_walk_overlay_v1'
$BaselineDir = Join-Path $Workspace 'baseline_az72'
$OverlayDir = Join-Path $Workspace 'overlay_v1'

foreach ($p in @($BaseSpec,$Exporter,$Review,$Overlay,$CanonicalBody,$G2Blend,$G2Manifest,$Python)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Required file missing: $p" }
}

$Blender = Find-BlenderExe
if (-not $Blender) { Fail 'Blender could not be located.' }

$base = Get-Content -LiteralPath $BaseSpec -Raw | ConvertFrom-Json
if ($base.gate -ne 'G3S-C1A' -or $base.revision -ne 'SKELETON_ONLY_WALK_CYCLE_V1') {
    Fail 'Unexpected canonical C1A skeleton spec.'
}

New-Item -ItemType Directory -Force -Path $Workspace | Out-Null
Get-ChildItem -LiteralPath $Workspace -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
New-Item -ItemType Directory -Force -Path $BaselineDir | Out-Null
New-Item -ItemType Directory -Force -Path $OverlayDir | Out-Null

Write-Host ''
Write-Host 'Roguelite - G3S-C1C GAMEPLAY WALK OVERLAY V1' -ForegroundColor Cyan
Write-Host '[LOCK] Gameplay locomotion facing = 72 deg from travel heading.' -ForegroundColor Green
Write-Host '[SOURCE] Same G2_CANONICAL_RIG + CMU 105_34 NormalWalk + same eight C1A phases.' -ForegroundColor Green
Write-Host '[PURPOSE] Art-direct the walk before any more diffusion.' -ForegroundColor Yellow
Write-Host '[OVERLAY] Compact stride + reduced root bob + mild forward torso intent + reduced civilian arm swing + head stabilization.' -ForegroundColor Green
Write-Host '[NO DIFFUSION] Skeleton-only A/B review.' -ForegroundColor Green
Write-Host ''

# Build a fresh 72-degree baseline from the retained real gait.
$spec = ($base | ConvertTo-Json -Depth 20 | ConvertFrom-Json)
$spec.camera.azimuth_from_motion_heading_deg = 72.0
$spec.purpose = 'C1C approved facing baseline 72 deg for gameplay walk overlay A/B'
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

# Apply the authored gameplay overlay in the projected 2D gameplay family.
$overlayGuide = Join-Path $OverlayDir 'g3s_c1c_gameplay_walk_overlay_v1_guide.json'
$overlayMarker = Join-Path $Workspace 'g3s_c1c_gameplay_walk_overlay_v1.json'

Write-Host ''
Write-Host '[AUTHOR] Applying gameplay locomotion overlay V1...' -ForegroundColor Yellow
& $Python $Overlay --input-guide $baselineGuide --output-guide $overlayGuide --marker $overlayMarker
if ($LASTEXITCODE -ne 0) { Fail "Gameplay overlay helper exited with code $LASTEXITCODE" }
if (-not (Test-Path $overlayGuide -PathType Leaf)) { Fail "Overlay guide missing: $overlayGuide" }
if (-not (Test-Path $overlayMarker -PathType Leaf)) { Fail "Overlay marker missing: $overlayMarker" }

& $Python $Review --guide $overlayGuide --workspace $OverlayDir --body-reference $CanonicalBody
if ($LASTEXITCODE -ne 0) { Fail "Overlay review builder exited with code $LASTEXITCODE" }

$marker = Get-Content -LiteralPath $overlayMarker -Raw | ConvertFrom-Json
if ($marker.status -ne 'PASS_OUTPUT_READY_FOR_SKELETON_VISUAL_QA') {
    Fail "Unexpected overlay marker status: $($marker.status)"
}

$baselineZoom = Join-Path $BaselineDir 'g3s_c1_skeleton_walk_zoom.gif'
$baselineSheet = Join-Path $BaselineDir 'g3s_c1_skeleton_walk_contact_sheet.png'
$overlayZoom = Join-Path $OverlayDir 'g3s_c1_skeleton_walk_zoom.gif'
$overlaySheet = Join-Path $OverlayDir 'g3s_c1_skeleton_walk_contact_sheet.png'
foreach ($p in @($baselineZoom,$baselineSheet,$overlayZoom,$overlaySheet)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Expected A/B review artifact missing: $p" }
}

$summary = [ordered]@{
    gate = 'G3S-C1C_GAMEPLAY_WALK_OVERLAY_V1'
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
        guide = $overlayGuide
        marker = $overlayMarker
        zoom_gif = $overlayZoom
        contact_sheet = $overlaySheet
    }
    decision_rule = 'Approve only if overlay reads more natural and more game-authored while preserving gait phase clarity, support contacts, anatomy and non-cartoon physicality.'
}
$summaryPath = Join-Path $Workspace 'g3s_c1c_gameplay_walk_overlay_v1_review.json'
$summary | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $summaryPath -Encoding UTF8

Write-Host ''
Write-Host 'G3S-C1C-OVERLAY: A/B SKELETON REVIEW PACKAGE READY' -ForegroundColor Green
Write-Host "BASELINE SHEET: $baselineSheet" -ForegroundColor Cyan
Write-Host "BASELINE GIF:   $baselineZoom" -ForegroundColor Cyan
Write-Host "OVERLAY SHEET:  $overlaySheet" -ForegroundColor Cyan
Write-Host "OVERLAY GIF:    $overlayZoom" -ForegroundColor Cyan
Write-Host "SUMMARY:        $summaryPath" -ForegroundColor Cyan
Write-Host ''
Write-Host '[NEXT] Share baseline + overlay contact sheets and zoom GIFs. Do not run SSD until the gameplay walk itself passes.' -ForegroundColor Yellow
