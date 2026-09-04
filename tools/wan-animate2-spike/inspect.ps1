param(
    [string]$Workspace = 'D:\AI\WanAnimate2',
    [int]$Port = 8188
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Find-ComfyRoot([string]$Base) {
    $candidates = @($Base, (Join-Path $Base 'ComfyUI'))
    foreach ($candidate in $candidates) {
        if (Test-Path (Join-Path $candidate 'main.py')) { return $candidate }
    }
    return $null
}

function Invoke-Comfy {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Args)
    Push-Location 'D:\AI'
    try {
        & py.exe -3.14 -m pipx run --spec comfy-cli comfy @Args
        if ($LASTEXITCODE -ne 0) { throw "comfy-cli failed: comfy $($Args -join ' ')" }
    } finally {
        Pop-Location
    }
}

$ComfyRoot = Find-ComfyRoot $Workspace
if (-not $ComfyRoot) {
    throw "ComfyUI not found under $Workspace. Run bootstrap.ps1 first."
}

Write-Host "ComfyUI root: $ComfyRoot" -ForegroundColor Green
Write-Host 'Starting ComfyUI in background...' -ForegroundColor Cyan
try {
    Invoke-Comfy --workspace $Workspace launch --background -- --listen 127.0.0.1 --port $Port
} catch {
    Write-Host 'Background launch may already be active; probing the API before failing.' -ForegroundColor Yellow
}

$Base = "http://127.0.0.1:$Port"
$ok = $false
for ($i = 0; $i -lt 90; $i++) {
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

$RouteFile = Join-Path $Workspace 'spike_model_route.txt'
$OfficialBaseInt8 = Test-Path (Join-Path $ComfyRoot 'models\diffusion_models\wan_animate_2_int8_convrot.safetensors')
$BaseQ4 = Test-Path (Join-Path $ComfyRoot 'models\diffusion_models\Wan-Animate-2-14B-Q4_K_M.gguf')

if ($OfficialBaseInt8) {
    $Route = 'official_base_int8_convrot'
    $Required = @(
        'WanAnimate2ToVideo',
        'LoadImage',
        'LoadVideo',
        'UNETLoader',
        'CLIPLoader',
        'CLIPVisionLoader',
        'CLIPVisionEncode',
        'VAELoader'
    )
} elseif ($BaseQ4) {
    $Route = 'base_q4_gguf'
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
} else {
    throw 'No supported Base model file was found. Do not continue with the workflow.'
}

Write-Host "Detected model route: $Route" -ForegroundColor Cyan
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
$MainModel = if ($Route -eq 'official_base_int8_convrot') {
    Join-Path $Models 'diffusion_models\wan_animate_2_int8_convrot.safetensors'
} else {
    Join-Path $Models 'diffusion_models\Wan-Animate-2-14B-Q4_K_M.gguf'
}

$Files = @(
    $MainModel,
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

$Probe = [ordered]@{
    route = $Route
}
foreach ($name in @('RebelsGGUFUnetLoaderMeta','UNETLoader','WanAnimate2ToVideo','LoadVideo')) {
    if ($ObjectInfo.PSObject.Properties.Name -contains $name) {
        $Probe[$name] = $ObjectInfo.$name
    }
}
$ProbePath = Join-Path $Workspace 'object_info_spike.json'
$Probe | ConvertTo-Json -Depth 30 | Set-Content -Path $ProbePath -Encoding utf8
Write-Host ''
Write-Host "Saved exact installed node schemas to: $ProbePath" -ForegroundColor Green

$LogCandidates = @(
    (Join-Path $Workspace "user\comfyui_$Port.log"),
    (Join-Path $ComfyRoot "user\comfyui_$Port.log")
) | Select-Object -Unique
foreach ($Log in $LogCandidates) {
    if (Test-Path $Log) {
        Write-Host ''
        Write-Host "ComfyUI log: $Log"
        $imports = Select-String -Path $Log -Pattern 'IMPORT FAILED|Rebels|GGUF|WanAnimate2|Animate2' -SimpleMatch:$false
        if ($imports) { $imports | Select-Object -Last 40 | ForEach-Object { $_.Line } }
    }
}

if ($failed) {
    throw 'Wan-Animate-2 CLI preflight FAILED. Do not build or run the workflow yet.'
}

Write-Host ''
Write-Host 'CLI preflight PASSED.' -ForegroundColor Green
if ($Route -eq 'base_q4_gguf') {
    Write-Host 'GGUF route: model class=WAN_Animate2 must be proven at actual model load.' -ForegroundColor Yellow
} else {
    Write-Host 'Official Base INT8 route: the safetensors checkpoint carries native Animate-2 metadata; actual model loading will still be checked in the run log.' -ForegroundColor Yellow
}
Write-Host 'Next: prepare the 17-frame driver, then build the headless API workflow from these installed schemas.'
