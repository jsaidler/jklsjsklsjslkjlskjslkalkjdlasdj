param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$QwenWorkspace = 'Z:\AI\QwenImageEdit',
    [string]$KleinWorkspace = 'Z:\AI\Flux2Klein',
    [string]$StudioRoot = 'Z:\AI\RogueliteAssetStudio'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "RUNNER66-REPEATED-ELEMENT-DECOMPOSITION: FAIL - $Message" -ForegroundColor Red
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
$Runner65 = Join-Path $StudioRoot 'localization\runner65_gate'
$Decomposer = Join-Path $ProjectRepoRoot 'tools\roguelite-asset-studio\repeated_element_decomposer.py'
$Output = Join-Path $StudioRoot 'localization\runner66_gate'

foreach ($required in @(
    $Python,
    $Original,
    $Decomposer,
    (Join-Path $Runner65 'runner65_hierarchical_localization_manifest.json'),
    (Join-Path $Runner65 'plank_mask.png'),
    (Join-Path $Runner65 'plank_mask_overlay.png'),
    (Join-Path $Runner65 'strap_mask.png'),
    (Join-Path $Runner65 'strap_mask_overlay.png')
)) {
    if (-not (Test-Path $required -PathType Leaf)) { Fail "required prerequisite missing: $required" }
}

Write-Host ''
Write-Host 'Roguelite Runner 66 - ATOMIC REPEATED-ELEMENT DECOMPOSITION' -ForegroundColor Cyan
Write-Host '[WHY] Runner65 fixed the parent door and lower-right strap, but its plank mask is the entire left door leaf.' -ForegroundColor Yellow
Write-Host '[NO MODEL] This gate runs no Grounding DINO, SAM2 or Qwen inference.' -ForegroundColor Green
Write-Host '[STRUCTURE] Uses persistent vertical image seams inside the already localized leaf to split repeated boards.' -ForegroundColor Green
Write-Host '[GENERIC] Same decomposer class is intended for repeated slats/bars/ribs/panels/boards after this proof.' -ForegroundColor Green
Write-Host '[FAIL CLOSED] The atomic plank must become narrow, tall, small relative to the parent and span most of the leaf height.' -ForegroundColor Green
Write-Host '[STRAP] Runner65 lower-right strap mask is retained unchanged for review.' -ForegroundColor Green
Write-Host '[NO QWEN] Regional generation remains disabled until both perception masks visually pass.' -ForegroundColor Green
Write-Host ''

New-Item -ItemType Directory -Force -Path $Output | Out-Null
$Stdout = Join-Path $Output 'runner66_stdout.log'
$Stderr = Join-Path $Output 'runner66_stderr.log'
foreach ($p in @($Stdout,$Stderr)) { if (Test-Path $p) { Remove-Item -LiteralPath $p -Force } }

$argsList = @(
    '-s',(Quote-ProcessArg $Decomposer),
    '--source',(Quote-ProcessArg $Original),
    '--runner65-dir',(Quote-ProcessArg $Runner65),
    '--output-dir',(Quote-ProcessArg $Output),
    '--peak-relative-threshold','0.45'
)

Write-Host 'RUNNER66: decomposing the Runner65 repeated plank region...' -ForegroundColor Cyan
$proc = Start-Process `
    -FilePath $Python `
    -ArgumentList $argsList `
    -WorkingDirectory $ProjectRepoRoot `
    -RedirectStandardOutput $Stdout `
    -RedirectStandardError $Stderr `
    -WindowStyle Hidden `
    -PassThru `
    -Wait

Print-TextFile $Stdout '--- RUNNER66 STDOUT ---'
$stderrText = Read-TextFileOrEmpty $Stderr
if (-not [string]::IsNullOrWhiteSpace($stderrText)) { Print-TextFile $Stderr '--- RUNNER66 STDERR ---' 250 }
if ($proc.ExitCode -ne 0) { Fail "atomic decomposer exited with code $($proc.ExitCode)" }

$Manifest = Join-Path $Output 'runner66_repeated_element_manifest.json'
$Contact = Join-Path $Output 'runner66_repeated_element_contact_sheet.png'
$Expected = @(
    'plank_atomic_decomposition.png',
    'plank_atomic_mask.png',
    'plank_atomic_mask_overlay.png',
    'plank_vertical_seam_profile.png',
    'strap_retained_mask.png',
    'strap_retained_mask_overlay.png',
    'runner66_repeated_element_contact_sheet.png',
    'runner66_repeated_element_manifest.json'
)
foreach ($name in $Expected) {
    if (-not (Test-Path (Join-Path $Output $name) -PathType Leaf)) {
        Fail "expected Runner66 output missing: $name"
    }
}

$m = Get-Content -LiteralPath $Manifest -Raw | ConvertFrom-Json
Write-Host ''
Write-Host "Runner66 auto geometry gate: $($m.auto_geometry_gate_pass)" -ForegroundColor Cyan
Write-Host "  seams: $((@($m.seam_peaks) | ForEach-Object { $_.x }) -join ', ')" -ForegroundColor Cyan
Write-Host "  selected plank interval: $($m.selected_interval.left)..$($m.selected_interval.right) / width=$($m.selected_interval.width)" -ForegroundColor Cyan
Write-Host "  plank area/parent=$([math]::Round([double]$m.atomic_plank_metrics.area_rel_parent,4)) / aspect=$([math]::Round([double]$m.atomic_plank_metrics.vertical_aspect,2)) / height/leaf=$([math]::Round([double]$m.atomic_plank_metrics.height_rel_leaf,3))" -ForegroundColor Cyan
Write-Host "  plank auto_valid=$($m.atomic_plank_auto_valid)" -ForegroundColor Cyan
Write-Host "  Runner65 strap retained auto_valid=$($m.strap_runner65_auto_valid)" -ForegroundColor Cyan
Write-Host ''
Write-Host 'RUNNER66-REPEATED-ELEMENT-DECOMPOSITION: PASS - TECHNICAL STRUCTURAL GATE COMPLETE / VISUAL VERDICT PENDING' -ForegroundColor Green
Write-Host "Contact sheet: $Contact" -ForegroundColor Cyan
Write-Host "Manifest: $Manifest" -ForegroundColor Cyan
Write-Host 'Do not run Qwen yet. Visual PASS requires exactly one real plank plus the already-correct lower-right strap.' -ForegroundColor Yellow
