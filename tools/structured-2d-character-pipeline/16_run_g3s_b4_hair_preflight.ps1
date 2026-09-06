param(
    [string]$RepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$PipelineWorkspace = 'Z:\AI\RogueliteCharacterPipeline'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "G3S-B4-PREFLIGHT: FAIL - $Message" -ForegroundColor Red
    exit 1
}

$Python = 'Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\python_embeded\python.exe'
$Master = Join-Path $RepoRoot 'assets\source\characters\exilada\reference\exilada_master.png'
$Body = Join-Path $RepoRoot 'assets\source\characters\exilada\body\exilada_body_base_b3b_v4.png'
$Helper = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_b4_hair_preflight.py'
$Workspace = Join-Path $PipelineWorkspace 'g3s_b4_hair_preflight'

foreach ($p in @($Python,$Master,$Body,$Helper)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Required file missing: $p" }
}

New-Item -ItemType Directory -Force -Path $Workspace | Out-Null

Write-Host ''
Write-Host 'Roguelite - G3S-B4 HAIR PREFLIGHT' -ForegroundColor Cyan
Write-Host '[LOCK] Body base must remain byte/pixel unchanged.' -ForegroundColor Green
Write-Host '[LOCK] Hair minimum depth split is rear_hair -> body -> front_hair.' -ForegroundColor Green
Write-Host '[LOCK] This step creates diagnostic review outputs only; no production hair pixels.' -ForegroundColor Yellow
Write-Host ''

& $Python $Helper `
  --master $Master `
  --body $Body `
  --workspace $Workspace

if ($LASTEXITCODE -ne 0) { Fail "preflight helper exited with code $LASTEXITCODE" }

$Contact = Join-Path $Workspace 'g3s_b4_hair_preflight_contact_sheet.png'
if (-not (Test-Path $Contact -PathType Leaf)) { Fail "contact sheet missing: $Contact" }

Write-Host ''
Write-Host 'G3S-B4-PREFLIGHT: COMPLETE' -ForegroundColor Green
Write-Host "CONTACT: $Contact"
Write-Host 'STOP. Share the contact sheet. Do not author/promote B4 hair or start B5/C yet.' -ForegroundColor Yellow
