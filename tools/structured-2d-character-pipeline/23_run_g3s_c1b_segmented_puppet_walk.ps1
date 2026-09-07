param(
    [string]$RepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$PipelineWorkspace = 'Z:\AI\RogueliteCharacterPipeline'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "G3S-C1B-PUPPET: FAIL - $Message" -ForegroundColor Red
    exit 1
}

$Python = 'Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\python_embeded\python.exe'
$Body = Join-Path $RepoRoot 'assets\source\characters\exilada\body\exilada_body_base_b3b_v4.png'
$Approval = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_c1a_skeleton_walk_approval.json'
$Spec = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_c1b_segmented_puppet_spec.json'
$Builder = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_c1b_build_segmented_puppet.py'
$Guide = Join-Path $PipelineWorkspace 'g3s_c1_skeleton_walk\g3s_c1_skeleton_walk_guide.json'
$Workspace = Join-Path $PipelineWorkspace 'g3s_c1b_segmented_puppet'
$BindManifest = Join-Path $Workspace 'g3s_c1b_puppet_bind_manifest.json'

foreach ($p in @($Python,$Body,$Approval,$Spec,$Builder,$Guide)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Required file missing: $p" }
}

$bodyHash = (Get-FileHash -LiteralPath $Body -Algorithm SHA256).Hash.ToLowerInvariant()
if ($bodyHash -ne '702e2d95325049b5d99ea66db4fbbb9b41d6d24813efb0b1c3a37e112b1c2858') {
    Fail "Canonical B3B hash changed: $bodyHash"
}

$approvalData = Get-Content -LiteralPath $Approval -Raw | ConvertFrom-Json
if ($approvalData.gate -ne 'G3S-C1A' -or $approvalData.status -ne 'PASS') {
    Fail 'C1A skeleton walk is not approved PASS.'
}

$specData = Get-Content -LiteralPath $Spec -Raw | ConvertFrom-Json
if ($specData.gate -ne 'G3S-C1B' -or $specData.revision -ne 'MINIMAL_BEATEMUP_SEGMENTED_PUPPET_V2' -or $specData.status -ne 'RUNNER_READY_REVIEW_REQUIRED') {
    Fail 'Minimal beat-em-up segmented puppet spec is not runner-ready.'
}
if ($specData.presentation_contract.true_isometric -ne $false) { Fail 'Spec drifted back toward true isometric.' }
if ($specData.presentation_contract.first_visible_family -ne 'screen-left_front-three-quarter') { Fail 'Unexpected first directional family.' }
if ($specData.variant_policy.first_proof_uses_base_part_set_only -ne $true) { Fail 'Preemptive part variants are not allowed in first proof.' }

New-Item -ItemType Directory -Force -Path $Workspace | Out-Null
Get-ChildItem -LiteralPath $Workspace -File -ErrorAction SilentlyContinue | Remove-Item -Force

Write-Host ''
Write-Host 'Roguelite - G3S-C1B MINIMAL BEAT-EM-UP SEGMENTED 2D PUPPET' -ForegroundColor Cyan
Write-Host '[LOCK] Presentation remains elevated 2D belt-scroller / false 3D, not isometric.' -ForegroundColor Green
Write-Host '[LOCK] One screen-left front-3/4 visible family only.' -ForegroundColor Green
Write-Host '[LOCK] Same persistent B3B pixels are reused in all eight gait states.' -ForegroundColor Green
Write-Host '[LOCK] Hidden skeleton owns motion, projected bone transforms and depth order only.' -ForegroundColor Green
Write-Host '[LOCK] No Flux/diffusion, no MPFB body, no model download, no paid API.' -ForegroundColor Green
Write-Host '[LOCK] No preemptive foreshortening/orientation variants in this first proof.' -ForegroundColor Green
Write-Host '[LOCK] Hair remains deferred.' -ForegroundColor Green
Write-Host '[OUTPUT] Part atlas + bind manifest + 8 body frames + in-place/zoom/travel GIFs + clean/overlay sheets.' -ForegroundColor Cyan
Write-Host ''

& $Python $Builder `
    --body $Body `
    --guide $Guide `
    --approval $Approval `
    --spec $Spec `
    --workspace $Workspace
if ($LASTEXITCODE -ne 0) { Fail "Segmented puppet builder exited with code $LASTEXITCODE" }
if (-not (Test-Path $BindManifest -PathType Leaf)) { Fail "Bind manifest missing: $BindManifest" }

$manifest = Get-Content -LiteralPath $BindManifest -Raw | ConvertFrom-Json
if ($manifest.gate -ne 'G3S-C1B' -or $manifest.revision -ne 'MINIMAL_BEATEMUP_SEGMENTED_PUPPET_V2' -or $manifest.status -ne 'REVIEW_REQUIRED') {
    Fail 'Unexpected segmented puppet bind manifest.'
}
if ($manifest.hard_locks.per_frame_generation -ne $false) { Fail 'Per-frame generation was incorrectly enabled.' }
if ($manifest.hard_locks.mpfb_body -ne $false) { Fail 'MPFB body was incorrectly enabled.' }
if ($manifest.hard_locks.part_variants_used -ne $false) { Fail 'Part variants were used before a demonstrated need.' }
if ($manifest.frame_pngs.Count -ne 8) { Fail "Expected 8 composited frames, got $($manifest.frame_pngs.Count)." }

$requiredOutputs = @(
    (Join-Path $Workspace 'g3s_c1b_segmented_part_atlas.png'),
    (Join-Path $Workspace 'g3s_c1b_puppet_walk_in_place.gif'),
    (Join-Path $Workspace 'g3s_c1b_puppet_walk_zoom.gif'),
    (Join-Path $Workspace 'g3s_c1b_puppet_walk_travel.gif'),
    (Join-Path $Workspace 'g3s_c1b_puppet_contact_sheet.png'),
    (Join-Path $Workspace 'g3s_c1b_puppet_contact_sheet_skeleton_overlay.png')
)
foreach ($p in $requiredOutputs) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Expected review artifact missing: $p" }
}

Write-Host ''
Write-Host 'G3S-C1B-PUPPET: REVIEW PACKAGE READY' -ForegroundColor Green
Write-Host "ATLAS:   $(Join-Path $Workspace 'g3s_c1b_segmented_part_atlas.png')"
Write-Host "ZOOM:    $(Join-Path $Workspace 'g3s_c1b_puppet_walk_zoom.gif')"
Write-Host "INPLACE: $(Join-Path $Workspace 'g3s_c1b_puppet_walk_in_place.gif')"
Write-Host "TRAVEL:  $(Join-Path $Workspace 'g3s_c1b_puppet_walk_travel.gif')"
Write-Host "SHEET:   $(Join-Path $Workspace 'g3s_c1b_puppet_contact_sheet.png')"
Write-Host "OVERLAY: $(Join-Path $Workspace 'g3s_c1b_puppet_contact_sheet_skeleton_overlay.png')"
Write-Host "BIND:    $BindManifest"
Write-Host ''
Write-Host 'Share the ZOOM GIF and CLEAN CONTACT SHEET first. This result must be judged as the SAME persistent doll moving, not as newly authored frames.' -ForegroundColor Yellow
