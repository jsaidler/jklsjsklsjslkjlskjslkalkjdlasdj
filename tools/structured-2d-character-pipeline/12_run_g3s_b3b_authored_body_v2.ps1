param(
    [string]$RepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$Workspace = 'Z:\AI\RogueliteCharacterPipeline'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "G3S-B3B V2: FAIL - $Message" -ForegroundColor Red
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
Write-Host 'Roguelite - G3S-B3B V2 AUTHORED NATIVE 2D BODY SOURCE' -ForegroundColor Cyan
Write-Host 'Visible RGB, alpha and silhouette are owned by the committed 2D asset.' -ForegroundColor Yellow
Write-Host 'B3A remains reference/guide infrastructure only.' -ForegroundColor Yellow
Write-Host ''

if (-not (Test-Path $RepoRoot -PathType Container)) { Fail "Repository root not found: $RepoRoot" }

$approvalPath = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_b3a_approval.json'
$sourcePath = Join-Path $RepoRoot 'assets\source\characters\exilada\body\g3s_b3b_body_base_source_v2.png'
$metadataPath = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_b3b_body_base_source_v2.json'
$validator = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_b3b_validate_authored_body_v2.py'
$embeddedPython = 'Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\python_embeded\python.exe'

foreach ($p in @($approvalPath,$sourcePath,$metadataPath,$validator,$embeddedPython)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Required file missing: $p. Run git pull --ff-only first." }
}

$b3a = Get-Content -LiteralPath $approvalPath -Raw | ConvertFrom-Json
if ($b3a.gate -ne 'G3S-B3-A-NUDE-ANATOMY-GUIDE' -or $b3a.status -ne 'PASS_CLOSED') {
    Fail 'B3A structural guide approval marker is not PASS_CLOSED.'
}
if ($b3a.revision -ne 'G3S_B3A_NUDE_ANATOMY_GUIDE_V2') {
    Fail "Unexpected B3A approval revision: $($b3a.revision)"
}

$meta = Get-Content -LiteralPath $metadataPath -Raw | ConvertFrom-Json
if ($meta.revision -ne 'G3S_B3B_NATIVE_2D_BODY_SOURCE_V2') { Fail 'Unexpected B3B V2 metadata revision.' }
if ($meta.source_authority -ne 'COMMITTED_NATIVE_2D_PIXEL_ASSET') { Fail 'B3B source authority is not native 2D asset.' }
if ([bool]$meta.ownership.b3a_rgb_sampled -or [bool]$meta.ownership.b3a_mask_sampled -or [bool]$meta.ownership.b3a_silhouette_copied) {
    Fail 'B3B V2 visible ownership incorrectly depends on B3A rendered data.'
}

$outDir = Join-Path $Workspace 'g3s_b3b_authored_body_v2'
Remove-Item $outDir -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

Write-Host '[RUN] validating committed native 2D body asset and generating review artifacts...' -ForegroundColor Cyan
$code = Invoke-NativeSafe -Exe $embeddedPython -Arguments @(
    $validator,
    '--source', $sourcePath,
    '--metadata', $metadataPath,
    '--output-dir', $outDir
)
if ($code -ne 0) { Fail "Validator exited with code $code" }

$manifest = Join-Path $outDir 'g3s_b3b_manifest_v2.json'
$contact = Join-Path $outDir 'g3s_b3b_contact_sheet_v2.png'
$sourceOut = Join-Path $outDir 'g3s_b3b_body_base_source_v2.png'
foreach ($p in @($manifest,$contact,$sourceOut)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Expected output missing: $p" }
}

$data = Get-Content -LiteralPath $manifest -Raw | ConvertFrom-Json
if ($data.gate -ne 'G3S-B3-B-NATIVE-2D-BODY-SOURCE' -or $data.status -ne 'REVIEW_REQUIRED') { Fail 'Unexpected B3B manifest state.' }
if ($data.revision -ne 'G3S_B3B_NATIVE_2D_BODY_SOURCE_V2') { Fail 'Unexpected B3B manifest revision.' }
if ($data.source_authority -ne 'COMMITTED_NATIVE_2D_PIXEL_ASSET') { Fail 'Visible source authority guard failed.' }
if ([bool]$data.ownership.b3a_rgb_sampled -or [bool]$data.ownership.b3a_mask_sampled -or [bool]$data.ownership.b3a_silhouette_copied) {
    Fail 'B3A visible-ownership guard failed.'
}
if ([int]$data.stats.visible_height -ne 128) { Fail "Visible height drift: $($data.stats.visible_height)" }
if ([int]$data.stats.partial_alpha_pixels -ne 0) { Fail 'Partial alpha found.' }

Write-Host ''
Write-Host 'G3S-B3B V2: REVIEW REQUIRED' -ForegroundColor Yellow
Write-Host "CONTACT SHEET: $contact"
Write-Host "NATIVE SOURCE: $sourceOut"
Write-Host "MANIFEST:      $manifest"
Write-Host ''
Write-Host 'STOP. Review the authored native 2D body at 1x before hair, clothing or animation.' -ForegroundColor Yellow
