param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$QwenWorkspace = 'Z:\AI\QwenImageEdit',
    [string]$KleinWorkspace = 'Z:\AI\Flux2Klein',
    [string]$StudioRoot = 'Z:\AI\RogueliteAssetStudio'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "RUNNER65-HIERARCHICAL-LOCALIZATION: FAIL - $Message" -ForegroundColor Red
    exit 1
}
function Quote-ProcessArg([string]$Value) {
    if ($Value -match '[\s"]') { return '"' + ($Value -replace '"','\"') + '"' }
    return $Value
}
function Read-TextFileOrEmpty([string]$Path) {
    if (-not (Test-Path $Path -PathType Leaf)) { return '' }
    $v = Get-Content -LiteralPath $Path -Raw
    if ($null -eq $v) { return '' }
    return [string]$v
}
function Print-TextFile([string]$Path,[string]$Header,[int]$Tail=0) {
    Write-Host $Header -ForegroundColor Yellow
    if (-not (Test-Path $Path -PathType Leaf)) {
        Write-Host "  <missing: $Path>"
        return
    }
    if ($Tail -gt 0) { Get-Content -LiteralPath $Path -Tail $Tail }
    else { Get-Content -LiteralPath $Path }
}

$PortableRoot = Join-Path $QwenWorkspace 'ComfyUI_windows_portable'
$Python = Join-Path $PortableRoot 'python_embeded\python.exe'
$Original = Join-Path $KleinWorkspace 'spike\flux2_klein_4b_t2i_probe.png'
$Localizer = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\hierarchical_region_localizer.py'
$BaseLocalizer = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\automatic_region_localizer.py'
$LocalizationRoot = Join-Path $StudioRoot 'localization'
$ModelCache = Join-Path $LocalizationRoot 'hf_cache'
$Output = Join-Path $LocalizationRoot 'runner65_gate'

foreach ($required in @($Python,$Original,$Localizer,$BaseLocalizer,$ModelCache)) {
    if (-not (Test-Path $required)) { Fail "required prerequisite missing: $required" }
}

Write-Host ''
Write-Host 'Roguelite Runner 65 - HIERARCHICAL SUBCOMPONENT LOCALIZATION' -ForegroundColor Cyan
Write-Host '[WHY] Runner64 proved the regional compositor but selected stone blocks instead of the requested door plank/strap.' -ForegroundColor Yellow
Write-Host '[NO QWEN] This gate spends no 20-step Qwen inference until perception itself is visually approved.' -ForegroundColor Green
Write-Host '[PARENT] First localize the wooden double door in the full asset.' -ForegroundColor Green
Write-Host '[CHILD] Crop/upscale the parent and re-run open-vocabulary grounding for the requested subcomponent.' -ForegroundColor Green
Write-Host '[RERANK] SAM2 masks top proposals and geometry/containment constraints rerank them.' -ForegroundColor Green
Write-Host '[NO DOWNLOAD] Reuses the Runner64 Grounding DINO Tiny + SAM2.1 cache only.' -ForegroundColor Green
Write-Host '[NO MANUAL MASKS] No user box/mask input is accepted.' -ForegroundColor Green
Write-Host ''

& $Python -s -c "from transformers import AutoModelForZeroShotObjectDetection, AutoProcessor, Sam2Model, Sam2Processor; print('Runner65 perception APIs OK')"
if ($LASTEXITCODE -ne 0) { Fail 'required Transformers perception APIs are unavailable in the Qwen portable Python' }

$env:HF_HOME = $ModelCache
$env:HF_HUB_CACHE = Join-Path $ModelCache 'hub'
$env:HF_HUB_OFFLINE = '1'
$env:TRANSFORMERS_OFFLINE = '1'
$env:HF_HUB_DISABLE_XET = '1'
$env:PYTORCH_CUDA_ALLOC_CONF = 'expandable_segments:True'

New-Item -ItemType Directory -Force -Path $Output | Out-Null

$Stdout = Join-Path $Output 'runner65_stdout.log'
$Stderr = Join-Path $Output 'runner65_stderr.log'
foreach ($p in @($Stdout,$Stderr)) {
    if (Test-Path $p) { Remove-Item -LiteralPath $p -Force }
}

$argsList = @(
    '-s',(Quote-ProcessArg $Localizer),
    '--source',(Quote-ProcessArg $Original),
    '--output-dir',(Quote-ProcessArg $Output),
    '--model-cache',(Quote-ProcessArg $ModelCache),
    '--device','cuda',
    '--component-long-side','1280',
    '--max-sam-candidates','10'
)

Write-Host 'RUNNER65: launching perception-only hierarchical localization...' -ForegroundColor Cyan
$proc = Start-Process `
    -FilePath $Python `
    -ArgumentList $argsList `
    -WorkingDirectory $ProjectRepoRoot `
    -RedirectStandardOutput $Stdout `
    -RedirectStandardError $Stderr `
    -WindowStyle Hidden `
    -PassThru `
    -Wait

Print-TextFile $Stdout '--- RUNNER65 STDOUT ---'
$stderrText = Read-TextFileOrEmpty $Stderr
if (-not [string]::IsNullOrWhiteSpace($stderrText)) {
    Print-TextFile $Stderr '--- RUNNER65 STDERR ---' 300
}
if ($proc.ExitCode -ne 0) {
    Fail "hierarchical localizer exited with code $($proc.ExitCode)"
}

$Manifest = Join-Path $Output 'runner65_hierarchical_localization_manifest.json'
$Contact = Join-Path $Output 'runner65_hierarchical_localization_contact_sheet.png'
$Expected = @(
    'parent_detection.png',
    'parent_crop.png',
    'parent_crop_upscaled.png',
    'plank_hierarchical_detection.png',
    'plank_mask.png',
    'plank_mask_overlay.png',
    'plank_crop.png',
    'plank_crop_mask.png',
    'strap_hierarchical_detection.png',
    'strap_mask.png',
    'strap_mask_overlay.png',
    'strap_crop.png',
    'strap_crop_mask.png',
    'runner65_hierarchical_localization_contact_sheet.png',
    'runner65_hierarchical_localization_manifest.json'
)
foreach ($name in $Expected) {
    if (-not (Test-Path (Join-Path $Output $name) -PathType Leaf)) {
        Fail "expected perception output missing: $name"
    }
}

$m = Get-Content -LiteralPath $Manifest -Raw | ConvertFrom-Json
Write-Host ''
Write-Host "Runner65 auto geometry gate: $($m.auto_geometry_gate_pass)" -ForegroundColor Cyan
Write-Host "  parent: $($m.parent.selected_label) / detector=$([math]::Round([double]$m.parent.detector_score,4)) / box=$($m.parent.expanded_box -join ',')" -ForegroundColor Cyan
Write-Host "  plank: auto_valid=$($m.tasks.plank.auto_valid) / label=$($m.tasks.plank.selected.label) / final_score=$([math]::Round([double]$m.tasks.plank.selected.final_score,4))" -ForegroundColor Cyan
Write-Host "  strap: auto_valid=$($m.tasks.strap.auto_valid) / label=$($m.tasks.strap.selected.label) / final_score=$([math]::Round([double]$m.tasks.strap.selected.final_score,4))" -ForegroundColor Cyan
Write-Host ''
Write-Host 'RUNNER65-HIERARCHICAL-LOCALIZATION: PASS - TECHNICAL PERCEPTION GATE COMPLETE / VISUAL VERDICT PENDING' -ForegroundColor Green
Write-Host "Contact sheet: $Contact" -ForegroundColor Cyan
Write-Host "Manifest: $Manifest" -ForegroundColor Cyan
Write-Host 'Do not run Qwen regional editing until the parent/plank/strap localization images are visually approved.' -ForegroundColor Yellow
