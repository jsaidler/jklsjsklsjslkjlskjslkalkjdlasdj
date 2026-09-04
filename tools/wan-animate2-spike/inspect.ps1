param(
    [string]$Workspace = 'D:\AI\WanAnimate2',
    [int]$Port = 8188
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Invoke-Comfy {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Args)
    & py.exe -3.14 -m pipx run --spec comfy-cli comfy @Args
    if ($LASTEXITCODE -ne 0) { throw "comfy-cli failed: comfy $($Args -join ' ')" }
}

$ComfyRoot = Join-Path $Workspace 'ComfyUI'
if (-not (Test-Path (Join-Path $ComfyRoot 'main.py'))) {
    throw "ComfyUI not found at $ComfyRoot. Run bootstrap.ps1 first."
}

Write-Host 'Starting ComfyUI in background...' -ForegroundColor Cyan
try {
    Invoke-Comfy --workspace $Workspace launch --background -- --listen 127.0.0.1 --port $Port
} catch {
    Write-Host 'Background launch may already be active; probing the API before failing.' -ForegroundColor Yellow
}

$Base = "http://127.0.0.1:$Port"
$ok = $false
for ($i = 0; $i -lt 60; $i++) {
    try {
        $null = Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 2
        $ok = $true
        break
    } catch {
        Start-Sleep -Seconds 1
    }
}
if (-not $ok) { throw "ComfyUI API did not become available at $Base" }

$ObjectInfo = Invoke-RestMethod -Uri "$Base/object_info" -TimeoutSec 60
$Required = @(
    'RebelsGGUFUnetLoaderMeta',
    'WanAnimate2ToVideo',
    'LoadImage',
    'LoadVideo',
    'CLIPLoader',
    'CLIPVisionLoader',
    'CLIPVisionEncode',
    'VAELoader'
)

Write-Host ''
Write-Host 'Required node classes:' -ForegroundColor Cyan
$failed = $false
foreach ($name in $Required) {
    $present = $ObjectInfo.PSObject.Properties.Name -contains $name
    if ($present) {
        Write-Host "[OK]   $name" -ForegroundColor Green
    } else {
        Write-Host "[MISS] $name" -ForegroundColor Red
        $failed = $true
    }
}

$Models = Join-Path $ComfyRoot 'models'
$Files = @(
    (Join-Path $Models 'diffusion_models\Wan-Animate-2-14B-Q4_K_M.gguf'),
    (Join-Path $Models 'text_encoders\umt5_xxl_fp8_e4m3fn_scaled.safetensors'),
    (Join-Path $Models 'clip_vision\clip_vision_h.safetensors'),
    (Join-Path $Models 'vae\Wan2_1_VAE_bf16.safetensors'),
    (Join-Path $ComfyRoot 'input\exilada_master.png')
)

Write-Host ''
Write-Host 'Required files:' -ForegroundColor Cyan
foreach ($f in $Files) {
    if (Test-Path $f) {
        $size = [math]::Round((Get-Item $f).Length / 1GB, 3)
        Write-Host "[OK]   $f ($size GB)" -ForegroundColor Green
    } else {
        Write-Host "[MISS] $f" -ForegroundColor Red
        $failed = $true
    }
}

$Probe = [ordered]@{}
foreach ($name in @('RebelsGGUFUnetLoaderMeta','WanAnimate2ToVideo','LoadVideo')) {
    if ($ObjectInfo.PSObject.Properties.Name -contains $name) {
        $Probe[$name] = $ObjectInfo.$name
    }
}
$ProbePath = Join-Path $Workspace 'object_info_spike.json'
$Probe | ConvertTo-Json -Depth 30 | Set-Content -Path $ProbePath -Encoding utf8
Write-Host ''
Write-Host "Saved exact installed node schemas to: $ProbePath" -ForegroundColor Green

$Log = Join-Path $Workspace "user\comfyui_$Port.log"
if (Test-Path $Log) {
    Write-Host ''
    Write-Host "ComfyUI log: $Log"
    $imports = Select-String -Path $Log -Pattern 'IMPORT FAILED|Rebels|GGUF|WanAnimate2' -SimpleMatch:$false
    if ($imports) { $imports | Select-Object -Last 40 | ForEach-Object { $_.Line } }
}

if ($failed) {
    throw 'Wan-Animate-2 CLI preflight FAILED. Do not build or run the workflow yet.'
}

Write-Host ''
Write-Host 'CLI preflight PASSED.' -ForegroundColor Green
Write-Host 'Important: model class=WAN_Animate2 can only be proven when the GGUF is actually loaded during a workflow run.' -ForegroundColor Yellow
Write-Host 'The next step is to generate a headless API workflow from the installed schemas, then execute it with comfy run.'
