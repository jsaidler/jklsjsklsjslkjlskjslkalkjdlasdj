param(
    [string]$RepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$PipelineWorkspace = 'Z:\AI\RogueliteCharacterPipeline'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "G3S-C1C-FACING: FAIL - $Message" -ForegroundColor Red
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
$CanonicalBody = Join-Path $RepoRoot 'assets\source\characters\exilada\body\exilada_body_base_b3b_v4.png'
$G2Dir = Join-Path $PipelineWorkspace 'g2'
$G2Blend = Join-Path $G2Dir 'g2_motion_topology.blend'
$G2Manifest = Join-Path $G2Dir 'g2_manifest.json'
$Python = 'Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\python_embeded\python.exe'
$Workspace = Join-Path $PipelineWorkspace 'g3s_c1c_gameplay_facing_audit'

foreach ($p in @($BaseSpec,$Exporter,$Review,$CanonicalBody,$G2Blend,$G2Manifest,$Python)) {
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

$variants = @(
    [ordered]@{ name='az60'; azimuth=60.0; note='30 deg off pure side profile' },
    [ordered]@{ name='az72'; azimuth=72.0; note='18 deg off pure side profile; likely belt-scroller sweet spot' },
    [ordered]@{ name='az84'; azimuth=84.0; note='6 deg off pure side profile' }
)

Write-Host ''
Write-Host 'Roguelite - G3S-C1C GAMEPLAY FACING AUDIT' -ForegroundColor Cyan
Write-Host '[PURPOSE] Stop judging diffusion and first establish the locomotion presentation appropriate to the belt-scroller.' -ForegroundColor Yellow
Write-Host '[LOCK] Same G2_CANONICAL_RIG + CMU 105_34 NormalWalk + same eight C1A phases.' -ForegroundColor Green
Write-Host '[LOCK] Same 640x360, pitch 26 deg, target skeleton height 128 px.' -ForegroundColor Green
Write-Host '[ONLY VARIABLE] Horizontal camera azimuth from motion heading: 60 / 72 / 84 deg.' -ForegroundColor Green
Write-Host '[NOTE] 90 deg is pure side view; the old C1A used 45 deg and is now considered too frontal for production locomotion.' -ForegroundColor DarkYellow
Write-Host '[NO DIFFUSION] This runner generates skeleton-only review packages.' -ForegroundColor Green
Write-Host ''

$summary = [ordered]@{
    gate = 'G3S-C1C_GAMEPLAY_FACING_AUDIT'
    status = 'REVIEW_REQUIRED'
    source_motion = 'CMU 105_34 NormalWalk'
    source_rig = 'G2_CANONICAL_RIG'
    pitch_deg = 26
    target_skeleton_height_px = 128
    variants = @()
}

foreach ($variant in $variants) {
    $name = [string]$variant.name
    $azimuth = [double]$variant.azimuth
    $variantDir = Join-Path $Workspace $name
    New-Item -ItemType Directory -Force -Path $variantDir | Out-Null

    # Deep-copy the canonical C1A spec through JSON so the original file remains untouched.
    $spec = ($base | ConvertTo-Json -Depth 20 | ConvertFrom-Json)
    $spec.camera.azimuth_from_motion_heading_deg = $azimuth
    $spec.purpose = "C1C gameplay-facing audit candidate $name; review-only projection of the validated C1A gait"
    $spec.status = 'RUNNER_READY_REVIEW_REQUIRED'
    $specPath = Join-Path $variantDir "g3s_c1c_${name}_spec.json"
    $spec | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $specPath -Encoding UTF8

    $guide = Join-Path $variantDir "g3s_c1c_${name}_guide.json"
    $stdout = Join-Path $variantDir 'blender_stdout.log'
    $stderr = Join-Path $variantDir 'blender_stderr.log'

    Write-Host "[BUILD] $name - azimuth $azimuth deg ($($variant.note))" -ForegroundColor Yellow
    $argString = '"{0}" --background --python-exit-code 1 --python "{1}" -- --manifest "{2}" --spec "{3}" --output "{4}"' -f $G2Blend,$Exporter,$G2Manifest,$specPath,$guide
    $proc = Start-Process -FilePath $Blender -ArgumentList $argString -Wait -PassThru -NoNewWindow -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    Get-Content $stdout -ErrorAction SilentlyContinue | Out-Host
    if ($proc.ExitCode -ne 0) {
        if (Test-Path $stderr) { Get-Content $stderr | Out-Host }
        Fail "Blender exporter failed for $name with code $($proc.ExitCode)."
    }
    if (-not (Test-Path $guide -PathType Leaf)) { Fail "Guide missing for ${name}: $guide" }

    & $Python $Review --guide $guide --workspace $variantDir --body-reference $CanonicalBody
    if ($LASTEXITCODE -ne 0) { Fail "Review builder failed for $name with code $LASTEXITCODE" }

    $zoom = Join-Path $variantDir 'g3s_c1_skeleton_walk_zoom.gif'
    $sheet = Join-Path $variantDir 'g3s_c1_skeleton_walk_contact_sheet.png'
    foreach ($p in @($zoom,$sheet)) {
        if (-not (Test-Path $p -PathType Leaf)) { Fail "Expected review artifact missing for ${name}: $p" }
    }

    $guideData = Get-Content -LiteralPath $guide -Raw | ConvertFrom-Json
    if ([math]::Abs([double]$guideData.camera.azimuth_from_motion_heading_deg - $azimuth) -gt 0.01) {
        Fail "Guide camera azimuth mismatch for ${name}: $($guideData.camera.azimuth_from_motion_heading_deg)"
    }
    if ($guideData.frames.Count -ne 8) { Fail "Expected 8 frames for $name" }

    $summary.variants += [ordered]@{
        name = $name
        azimuth_deg = $azimuth
        note = [string]$variant.note
        guide = $guide
        zoom_gif = $zoom
        contact_sheet = $sheet
    }
}

$summaryPath = Join-Path $Workspace 'g3s_c1c_gameplay_facing_audit.json'
$summary | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $summaryPath -Encoding UTF8

Write-Host ''
Write-Host 'G3S-C1C-FACING: REVIEW PACKAGE READY' -ForegroundColor Green
Write-Host "ROOT:    $Workspace" -ForegroundColor Cyan
Write-Host "SUMMARY: $summaryPath" -ForegroundColor Cyan
foreach ($row in $summary.variants) {
    Write-Host "[$($row.name)] SHEET: $($row.contact_sheet)" -ForegroundColor Cyan
    Write-Host "[$($row.name)] GIF:   $($row.zoom_gif)" -ForegroundColor Cyan
}
Write-Host ''
Write-Host '[NEXT] Compare gait readability and game-appropriate facing. Do not run SSD again until one facing is approved or all three are rejected.' -ForegroundColor Yellow
