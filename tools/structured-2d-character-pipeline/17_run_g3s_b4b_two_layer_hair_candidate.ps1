param(
    [string]$RepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$PipelineWorkspace = 'Z:\AI\RogueliteCharacterPipeline'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "G3S-B4B-V4: FAIL - $Message" -ForegroundColor Red
    exit 1
}

$Python = 'Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\python_embeded\python.exe'
$Master = Join-Path $RepoRoot 'assets\source\characters\exilada\reference\exilada_master.png'
$Body = Join-Path $RepoRoot 'assets\source\characters\exilada\body\exilada_body_base_b3b_v4.png'
$PreflightMeta = Join-Path $PipelineWorkspace 'g3s_b4_hair_preflight\g3s_b4_hair_preflight.json'
$Helper = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_b4b_pose_anchored_hair_candidate.py'
$Approval = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_b4a_preflight_approval.json'
$V3Failure = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_b4b_v3_pose_mismatch_failure.json'
$V4Spec = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_b4b_v4_pose_anchored_hair_spec.json'
$Workspace = Join-Path $PipelineWorkspace 'g3s_b4b_two_layer_hair'

foreach ($p in @($Python,$Master,$Body,$PreflightMeta,$Helper,$Approval,$V3Failure,$V4Spec)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Required file missing: $p. Run git pull --ff-only first." }
}

Write-Host ''
Write-Host 'Roguelite - G3S-B4B V4 POSE-ANCHORED TWO-LAYER HAIR REVIEW' -ForegroundColor Cyan
Write-Host '[LOCK] canonical B3B body is immutable and hash-verified.' -ForegroundColor Green
Write-Host '[LOCK] minimum depth order: rear_hair -> body -> front_hair.' -ForegroundColor Green
Write-Host '[LOCK] master is identity/style inspiration only; its pose does not drive hair placement.' -ForegroundColor Green
Write-Host '[LOCK] head/shoulder/torso anchors are measured from the actual production B3B body.' -ForegroundColor Green
Write-Host '[LOCK] rear_hair and front_hair are newly authored relative to those production-pose anchors.' -ForegroundColor Green
Write-Host '[LOCK] review-only; no hair asset is promoted or committed by this runner.' -ForegroundColor Yellow
Write-Host ''

New-Item -ItemType Directory -Force -Path $Workspace | Out-Null

& $Python $Helper `
  --master $Master `
  --body $Body `
  --preflight-meta $PreflightMeta `
  --workspace $Workspace

if ($LASTEXITCODE -ne 0) { Fail "V4 helper exited with code $LASTEXITCODE" }

$Rear = Join-Path $Workspace 'g3s_b4b_rear_hair_candidate.png'
$Front = Join-Path $Workspace 'g3s_b4b_front_hair_candidate.png'
$Contact = Join-Path $Workspace 'g3s_b4b_contact_sheet.png'
$Meta = Join-Path $Workspace 'g3s_b4b_two_layer_hair_candidate.json'
foreach ($p in @($Rear,$Front,$Contact,$Meta)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "review output missing: $p" }
}

Write-Host ''
Write-Host 'G3S-B4B V4: POSE-ANCHORED REVIEW PACKAGE READY' -ForegroundColor Green
Write-Host "REAR:    $Rear"
Write-Host "FRONT:   $Front"
Write-Host "CONTACT: $Contact"
Write-Host "META:    $Meta"
Write-Host 'STOP. Share the contact sheet. Do not promote hair and do not start B5/C.' -ForegroundColor Yellow
