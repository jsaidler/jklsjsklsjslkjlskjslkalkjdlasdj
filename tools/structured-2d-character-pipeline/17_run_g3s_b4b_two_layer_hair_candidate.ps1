param(
    [string]$RepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$PipelineWorkspace = 'Z:\AI\RogueliteCharacterPipeline'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "G3S-B4B: FAIL - $Message" -ForegroundColor Red
    exit 1
}

$Python = 'Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\python_embeded\python.exe'
$Master = Join-Path $RepoRoot 'assets\source\characters\exilada\reference\exilada_master.png'
$Body = Join-Path $RepoRoot 'assets\source\characters\exilada\body\exilada_body_base_b3b_v4.png'
$PreflightMeta = Join-Path $PipelineWorkspace 'g3s_b4_hair_preflight\g3s_b4_hair_preflight.json'
$Helper = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_b4b_two_layer_hair_candidate.py'
$Approval = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_b4a_preflight_approval.json'
$V1FailureMarker = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_b4b_v1_extraction_route_failure.json'
$V2FailureMarker = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_b4b_v2_visual_failure.json'
$Workspace = Join-Path $PipelineWorkspace 'g3s_b4b_two_layer_hair'

foreach ($p in @($Python,$Master,$Body,$PreflightMeta,$Helper,$Approval,$V1FailureMarker,$V2FailureMarker)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Required file missing: $p. Run git pull --ff-only first." }
}

Write-Host ''
Write-Host 'Roguelite - G3S-B4B V3 AUTHORED TWO-LAYER HAIR REVIEW' -ForegroundColor Cyan
Write-Host '[LOCK] canonical B3B body is immutable and hash-verified.' -ForegroundColor Green
Write-Host '[LOCK] minimum depth order: rear_hair -> body -> front_hair.' -ForegroundColor Green
Write-Host '[LOCK] canonical master is inspiration/identity reference only.' -ForegroundColor Green
Write-Host '[LOCK] no master hair pixels are extracted, copied, traced, or split into final layers.' -ForegroundColor Green
Write-Host '[V3] rear_hair is dominant/asymmetric; front_hair is sparse lateral framing.' -ForegroundColor Green
Write-Host '[LOCK] review-only; no hair asset is promoted or committed by this runner.' -ForegroundColor Yellow
Write-Host ''

New-Item -ItemType Directory -Force -Path $Workspace | Out-Null

& $Python $Helper `
  --master $Master `
  --body $Body `
  --preflight-meta $PreflightMeta `
  --workspace $Workspace

if ($LASTEXITCODE -ne 0) { Fail "B4B V3 helper exited with code $LASTEXITCODE" }

$Rear = Join-Path $Workspace 'g3s_b4b_rear_hair_candidate.png'
$Front = Join-Path $Workspace 'g3s_b4b_front_hair_candidate.png'
$Contact = Join-Path $Workspace 'g3s_b4b_contact_sheet.png'
$Meta = Join-Path $Workspace 'g3s_b4b_two_layer_hair_candidate.json'
foreach ($p in @($Rear,$Front,$Contact,$Meta)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "review output missing: $p" }
}

Write-Host ''
Write-Host 'G3S-B4B V3: REVIEW PACKAGE READY' -ForegroundColor Green
Write-Host "REAR:    $Rear"
Write-Host "FRONT:   $Front"
Write-Host "CONTACT: $Contact"
Write-Host "META:    $Meta"
Write-Host 'STOP. Share the contact sheet. Do not promote hair and do not start B5/C.' -ForegroundColor Yellow
