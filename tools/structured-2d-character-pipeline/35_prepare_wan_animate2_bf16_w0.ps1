param(
    [string]$ProjectRepoRoot = 'D:\GOOGLE DRIVE\DEV\Roguelite',
    [string]$Workspace = 'D:\AI\WanAnimate2',
    [int]$Port = 8188,
    [int]$MinFreeGB = 70
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message) {
    Write-Host "RUNNER35-WAN-BF16-PREP: FAIL - $Message" -ForegroundColor Red
    exit 1
}

$Bootstrap = Join-Path $ProjectRepoRoot 'tools\wan-animate2-spike\bootstrap.ps1'
$Inspect = Join-Path $ProjectRepoRoot 'tools\wan-animate2-spike\inspect.ps1'
$Master = Join-Path $ProjectRepoRoot 'assets\source\characters\exilada\reference\exilada_master.png'
foreach ($f in @($Bootstrap,$Inspect,$Master)) {
    if (-not (Test-Path $f -PathType Leaf)) { Fail "required file missing: $f" }
}

Write-Host ''
Write-Host 'Roguelite Runner 35 — Wan-Animate-2 Base BF16 / W0 preparation' -ForegroundColor Cyan
Write-Host '[MODEL] Base BF16 32.8 GB — no INT8, no Distilled, no LightX2V LoRA.' -ForegroundColor Green
Write-Host '[TEXT] UMT5 XXL FP16 11.4 GB — FP8 text encoder deliberately excluded for the reference-quality baseline.' -ForegroundColor Green
Write-Host '[AUX] CLIP Vision H + Wan VAE BF16.' -ForegroundColor Green
Write-Host '[DISK] Model payload ~45.7 GB; preflight requires free-space headroom for ComfyUI/temp files.' -ForegroundColor Green
Write-Host '[CLEANUP] Superseded Wan INT8/Distilled/LoRA/FP8 assets are removed if found.' -ForegroundColor Yellow
Write-Host '[W0] Downloads the upstream demo1 reference.png + template.mp4.' -ForegroundColor Green
Write-Host '[STOP] This runner does NOT infer. It stops after capturing the exact fresh ComfyUI node schema.' -ForegroundColor Yellow
Write-Host ''

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $Bootstrap `
    -Workspace $Workspace `
    -Master $Master `
    -MinFreeGB $MinFreeGB
if ($LASTEXITCODE -ne 0) { Fail "BF16 bootstrap exited with code $LASTEXITCODE" }

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $Inspect `
    -Workspace $Workspace `
    -Port $Port
if ($LASTEXITCODE -ne 0) { Fail "BF16 schema preflight exited with code $LASTEXITCODE" }

$Manifest = Join-Path $Workspace 'wan_bf16_route.json'
$Schema = Join-Path $Workspace 'object_info_wan_bf16.json'
foreach ($f in @($Manifest,$Schema)) {
    if (-not (Test-Path $f -PathType Leaf)) { Fail "expected proof file missing: $f" }
}

Write-Host ''
Write-Host 'RUNNER35-WAN-BF16-PREP: PASS — READY TO AUTHOR W0 WORKFLOW' -ForegroundColor Green
Write-Host "Route manifest: $Manifest" -ForegroundColor Cyan
Write-Host "Installed schema: $Schema" -ForegroundColor Cyan
Write-Host ''
Write-Host 'Next action is code-side: build the W0 official-baseline workflow from this exact schema, then run the first BF16 inference.' -ForegroundColor Yellow
