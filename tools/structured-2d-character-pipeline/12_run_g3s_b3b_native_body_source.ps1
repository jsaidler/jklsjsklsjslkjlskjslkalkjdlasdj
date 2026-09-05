param(
    [string]$RepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$Workspace = 'Z:\AI\RogueliteCharacterPipeline'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "G3S-B3B: FAIL - $Message" -ForegroundColor Red
    exit 1
}

function Invoke-NativeSafe {
    param(
        [Parameter(Mandatory=$true)][string]$Exe,
        [Parameter(Mandatory=$true)][string[]]$Arguments
    )
    $saved = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $captured = @(& $Exe @Arguments 2>&1)
        $code = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $saved
    }
    foreach ($line in $captured) { Write-Host ([string]$line) }
    return [int]$code
}

Write-Host ''
Write-Host 'Roguelite - G3S-B3B NATIVE 128 NUDE BODY SOURCE' -ForegroundColor Cyan
Write-Host 'B3A owns structure only. B3B owns visible body RGB pixels.' -ForegroundColor Yellow
Write-Host 'No hair, clothing, bindings, cuffs, shackles or chains.' -ForegroundColor Yellow
Write-Host ''

if (-not (Test-Path $RepoRoot -PathType Container)) { Fail "Repository root not found: $RepoRoot" }

$approvalPath = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_b3a_approval.json'
$targetScript = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_b3b_native_body_source.py'
$embeddedPython = 'Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\python_embeded\python.exe'
$b3aDir = Join-Path $Workspace 'g3s_b3a_nude_guide'
$b3aManifest = Join-Path $b3aDir 'g3s_b3a_manifest.json'

foreach ($p in @($approvalPath,$targetScript,$embeddedPython,$b3aManifest)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Required file missing: $p. Run git pull --ff-only first, and keep the approved B3A V2 output." }
}

$approval = Get-Content -LiteralPath $approvalPath -Raw | ConvertFrom-Json
if ($approval.gate -ne 'G3S-B3-A-NUDE-ANATOMY-GUIDE' -or $approval.status -ne 'PASS_CLOSED') {
    Fail 'Canonical B3A approval marker is not PASS_CLOSED.'
}
if ($approval.revision -ne 'G3S_B3A_NUDE_ANATOMY_GUIDE_V2') {
    Fail "B3A approval revision mismatch: $($approval.revision)"
}

$b3a = Get-Content -LiteralPath $b3aManifest -Raw | ConvertFrom-Json
if ($b3a.revision -ne 'G3S_B3A_NUDE_ANATOMY_GUIDE_V2') { Fail "Local B3A output is not V2: $($b3a.revision)" }
if ($b3a.phenotype_audit.resolved_gender -ne 'female') { Fail 'Local B3A phenotype is not female.' }
if ($b3a.phenotype_audit.resolved_life_stage -ne 'adult') { Fail 'Local B3A phenotype is not adult.' }
if ([int]$b3a.phenotype_audit.male_target_count -ne 0 -or [int]$b3a.phenotype_audit.minor_target_count -ne 0) {
    Fail 'Local B3A phenotype contains male/minor targets.'
}
if ([int]$b3a.layer_audit.hair_objects -ne 0 -or
    [int]$b3a.layer_audit.clothing_objects -ne 0 -or
    [int]$b3a.layer_audit.restraint_objects -ne 0 -or
    [int]$b3a.layer_audit.chains_objects -ne 0) {
    Fail 'Local B3A contains forbidden layer objects.'
}

$outDir = Join-Path $Workspace 'g3s_b3b_native_body_source'
Remove-Item $outDir -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

Write-Host '[RUN] deterministic native-grid body authoring from B3A structural mask only...' -ForegroundColor Cyan
$code = Invoke-NativeSafe -Exe $embeddedPython -Arguments @(
    $targetScript,
    '--b3a-manifest', $b3aManifest,
    '--output-dir', $outDir
)
if ($code -ne 0) { Fail "B3B authoring exited with code $code" }

$manifest = Join-Path $outDir 'g3s_b3b_manifest.json'
$contact = Join-Path $outDir 'g3s_b3b_contact_sheet.png'
$source = Join-Path $outDir 'g3s_b3b_nude_body_source_v1.png'

foreach ($p in @($manifest,$contact,$source)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Expected B3B output missing: $p" }
}

$data = Get-Content -LiteralPath $manifest -Raw | ConvertFrom-Json
if ($data.gate -ne 'G3S-B3-B-NATIVE-NUDE-BODY-SOURCE' -or $data.status -ne 'REVIEW_REQUIRED') {
    Fail 'Unexpected B3B manifest state.'
}
if ($data.revision -ne 'G3S_B3B_NATIVE_NUDE_BODY_SOURCE_V1') { Fail "Unexpected B3B revision: $($data.revision)" }
if (-not [bool]$data.rules.final_visible_rgb_owned_by_b3b) { Fail 'B3B visible-RGB ownership guard failed.' }
if ([bool]$data.rules.b3a_rgb_sampled) { Fail 'B3B illegally sampled B3A lit RGB.' }
if (-not [bool]$data.rules.b3a_mask_used_for_structure_only) { Fail 'B3A structural-guide-only guard failed.' }
if ([int]$data.stats.partial_alpha_pixels -ne 0) { Fail 'B3B contains partial alpha.' }
if ([int]$data.stats.visible_height -lt 126 -or [int]$data.stats.visible_height -gt 128) {
    Fail "B3B visible height is outside native gate: $($data.stats.visible_height)"
}
if ([int]$data.layer_audit.hair_pixels -ne 0 -or
    [int]$data.layer_audit.clothing_pixels -ne 0 -or
    [int]$data.layer_audit.binding_pixels -ne 0 -or
    [int]$data.layer_audit.restraint_pixels -ne 0 -or
    [int]$data.layer_audit.chain_pixels -ne 0) {
    Fail 'Forbidden layer pixels are present in B3B.'
}

Write-Host ''
Write-Host 'G3S-B3B V1: REVIEW REQUIRED' -ForegroundColor Yellow
Write-Host "CONTACT SHEET: $contact"
Write-Host "NATIVE SOURCE: $source"
Write-Host "MANIFEST:      $manifest"
Write-Host ''
Write-Host 'STOP. Review native 1x body art before any hair, clothing or animation work.' -ForegroundColor Yellow
