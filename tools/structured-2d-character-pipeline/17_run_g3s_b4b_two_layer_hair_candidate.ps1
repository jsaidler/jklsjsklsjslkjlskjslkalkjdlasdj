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
$Workspace = Join-Path $PipelineWorkspace 'g3s_b4b_two_layer_hair'

foreach ($p in @($Python,$Master,$Body,$PreflightMeta,$Helper,$Approval)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Required file missing: $p" }
}

Write-Host ''
Write-Host 'Roguelite - G3S-B4B TWO-LAYER HAIR REVIEW' -ForegroundColor Cyan
Write-Host '[LOCK] canonical B3B body is immutable and hash-verified.' -ForegroundColor Green
Write-Host '[LOCK] minimum depth order: rear_hair -> body -> front_hair.' -ForegroundColor Green
Write-Host '[LOCK] source hair pixels come only from the canonical Exilada master.' -ForegroundColor Green
Write-Host '[LOCK] review-only; no hair asset is promoted or committed by this runner.' -ForegroundColor Yellow
Write-Host ''

New-Item -ItemType Directory -Force -Path $Workspace | Out-Null

& $Python $Helper `
  --master $Master `
  --body $Body `
  --preflight-meta $PreflightMeta `
  --workspace $Workspace

if ($LASTEXITCODE -ne 0) { Fail "B4B helper exited with code $LASTEXITCODE" }

$Contact = Join-Path $Workspace 'g3s_b4b_contact_sheet.png'
if (-not (Test-Path $Contact -PathType Leaf)) { Fail "contact sheet missing: $Contact" }

Write-Host ''
Write-Host 'G3S-B4B: REVIEW PACKAGE READY' -ForegroundColor Green
Write-Host "CONTACT: $Contact"
Write-Host 'STOP. Share the contact sheet. Do not promote hair and do not start B5/C.' -ForegroundColor Yellow
