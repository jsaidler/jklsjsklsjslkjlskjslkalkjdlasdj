param(
    [string]$RepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$PipelineWorkspace = 'Z:\AI\RogueliteCharacterPipeline'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "G3S-B3B-V4-PROMOTE: FAIL - $Message" -ForegroundColor Red
    exit 1
}

$Python = 'Z:\AI\QwenImageEditSpike\ComfyUI_windows_portable\python_embeded\python.exe'
$ReviewRunner = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\14_run_g3s_b3b_v4_pixel_reference_candidate.ps1'
$Promoter = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_b3b_v4_promote_body_base.py'
$Approval = Join-Path $RepoRoot 'tools\structured-2d-character-pipeline\g3s_b3b_v4_visual_approval.json'

foreach ($p in @($Python,$ReviewRunner,$Promoter,$Approval)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "Required file missing: $p. Run git pull --ff-only first." }
}

Write-Host ''
Write-Host 'Roguelite - G3S-B3B V4 BODY-BASE PROMOTION' -ForegroundColor Cyan
Write-Host '[LOCK] Visual candidate already passed review; promotion may not alter its pixels.' -ForegroundColor Green
Write-Host '[LOCK] Only canonical body PNG + provenance JSON will be committed by this runner.' -ForegroundColor Green
Write-Host ''

# Rebuild the review candidate deterministically from the exact locked source.
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ReviewRunner -RepoRoot $RepoRoot -PipelineWorkspace $PipelineWorkspace
if ($LASTEXITCODE -ne 0) { Fail "review runner exited with code $LASTEXITCODE" }

$Candidate = Join-Path $PipelineWorkspace 'g3s_b3b_v4_pixel_reference\g3s_b3b_v4_pixel_reference_candidate.png'
if (-not (Test-Path $Candidate -PathType Leaf)) { Fail "candidate missing after review runner: $Candidate" }

& $Python $Promoter --candidate $Candidate --repo-root $RepoRoot
if ($LASTEXITCODE -ne 0) { Fail "promotion helper exited with code $LASTEXITCODE" }

$Asset = Join-Path $RepoRoot 'assets\source\characters\exilada\body\exilada_body_base_b3b_v4.png'
$Meta = Join-Path $RepoRoot 'assets\source\characters\exilada\body\exilada_body_base_b3b_v4.json'
foreach ($p in @($Asset,$Meta)) {
    if (-not (Test-Path $p -PathType Leaf)) { Fail "promoted output missing: $p" }
}

Write-Host '[GIT] committing only promoted body-base asset files...' -ForegroundColor Cyan
& git -C $RepoRoot add -- 'assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png' 'assets/source/characters/exilada/body/exilada_body_base_b3b_v4.json'
if ($LASTEXITCODE -ne 0) { Fail 'git add failed' }

$diff = & git -C $RepoRoot diff --cached --name-only -- 'assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png' 'assets/source/characters/exilada/body/exilada_body_base_b3b_v4.json'
if ($LASTEXITCODE -ne 0) { Fail 'git diff --cached failed' }

if ($diff) {
    & git -C $RepoRoot commit -m 'Promote approved Exilada B3B V4 body base' -- 'assets/source/characters/exilada/body/exilada_body_base_b3b_v4.png' 'assets/source/characters/exilada/body/exilada_body_base_b3b_v4.json'
    if ($LASTEXITCODE -ne 0) { Fail 'git commit failed' }
    & git -C $RepoRoot push
    if ($LASTEXITCODE -ne 0) { Fail 'git push failed; local commit exists and should not be recreated' }
} else {
    Write-Host '[GIT] Canonical body asset already matches the approved candidate; no new commit required.' -ForegroundColor Yellow
}

Write-Host ''
Write-Host 'G3S-B3B-V4: BODY BASE PROMOTED' -ForegroundColor Green
Write-Host "ASSET: $Asset"
Write-Host "META:  $Meta"
Write-Host 'NEXT GATE AFTER DOCUMENT SYNC: G3S-B4 HAIR' -ForegroundColor Cyan
