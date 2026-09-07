param(
    [string]$Workspace = 'D:\AI\WanAnimate2',
    [int]$Port = 8188
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Find-ComfyRoot([string]$Base) {
    foreach ($candidate in @($Base, (Join-Path $Base 'ComfyUI'))) {
        if (Test-Path (Join-Path $candidate 'main.py')) { return $candidate }
    }
    return $null
}

function Find-WorkspacePython([string]$Base, [string]$ComfyRoot) {
    foreach ($candidate in @(
        (Join-Path $ComfyRoot '.venv\Scripts\python.exe'),
        (Join-Path $Base '.venv\Scripts\python.exe')
    ) | Select-Object -Unique) {
        if (Test-Path $candidate) { return $candidate }
    }
    return $null
}

$ComfyRoot = Find-ComfyRoot $Workspace
if (-not $ComfyRoot) { throw "ComfyUI not found under $Workspace. Run bootstrap.ps1 first." }
$WorkspacePython = Find-WorkspacePython $Workspace $ComfyRoot
if (-not $WorkspacePython) { throw 'ComfyUI workspace Python environment not found.' }

$Models = Join-Path $ComfyRoot 'models'
$MainModel = Join-Path $Models 'diffusion_models\wan_animate_2_bf16.safetensors'
$TextModel = Join-Path $Models 'text_encoders\umt5_xxl_fp16.safetensors'
$ClipModel = Join-Path $Models 'clip_vision\clip_vision_h.safetensors'
$VaeModel = Join-Path $Models 'vae\Wan2_1_VAE_bf16.safetensors'
$W0Reference = Join-Path $ComfyRoot 'input\wan_animate2_w0\official_demo1_reference.png'
$W0Driver = Join-Path $ComfyRoot 'input\wan_animate2_w0\official_demo1_template.mp4'

$failed = $false
Write-Host "ComfyUI root: $ComfyRoot" -ForegroundColor Green
Write-Host "ComfyUI Python: $WorkspacePython" -ForegroundColor Green
Write-Host ''
Write-Host 'BF16 reference-route files:' -ForegroundColor Cyan
foreach ($f in @($MainModel,$TextModel,$ClipModel,$VaeModel,$W0Reference,$W0Driver)) {
    if (Test-Path $f -PathType Leaf) {
        $size = [math]::Round((Get-Item $f).Length / 1GB, 3)
        Write-Host "[OK]   $f ($size GB)" -ForegroundColor Green
    } else {
        Write-Host "[MISS] $f" -ForegroundColor Red
        $failed = $true
    }
}

$Forbidden = @(
    (Join-Path $Models 'diffusion_models\wan_animate_2_int8_convrot.safetensors'),
    (Join-Path $Models 'diffusion_models\wan_animate_2_distill_bf16.safetensors'),
    (Join-Path $Models 'diffusion_models\wan_animate_2_distill_int8_convrot.safetensors'),
    (Join-Path $Models 'loras\lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors'),
    (Join-Path $Models 'text_encoders\umt5_xxl_fp8_e4m3fn_scaled.safetensors')
)
Write-Host ''
Write-Host 'Obsolete/superseded Wan assets (must be absent):' -ForegroundColor Cyan
foreach ($f in $Forbidden) {
    if (Test-Path $f -PathType Leaf) {
        Write-Host "[FOUND] $f" -ForegroundColor Red
        $failed = $true
    } else {
        Write-Host "[CLEAN] $f" -ForegroundColor Green
    }
}

$Base = "http://127.0.0.1:$Port"
$serverAlreadyRunning = $false
try {
    $null = Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 2
    $serverAlreadyRunning = $true
} catch {}

$UserDir = Join-Path $ComfyRoot 'user'
New-Item -ItemType Directory -Force -Path $UserDir | Out-Null
$StdoutLog = Join-Path $UserDir "comfyui_${Port}_stdout.log"
$StderrLog = Join-Path $UserDir "comfyui_${Port}_stderr.log"
$PidFile = Join-Path $Workspace '.wan_animate2_spike.pid'
$process = $null

if ($serverAlreadyRunning) {
    Write-Host "ComfyUI API is already running at $Base" -ForegroundColor Green
} else {
    Write-Host 'Starting ComfyUI directly with the workspace Python (headless)...' -ForegroundColor Cyan
    $MainPy = Join-Path $ComfyRoot 'main.py'
    $launchArgs = @($MainPy,'--listen','127.0.0.1','--port',"$Port",'--disable-auto-launch')
    $process = Start-Process -FilePath $WorkspacePython -ArgumentList $launchArgs -WorkingDirectory $ComfyRoot `
        -RedirectStandardOutput $StdoutLog -RedirectStandardError $StderrLog -WindowStyle Hidden -PassThru
    Set-Content -Path $PidFile -Value $process.Id -Encoding ascii
    Write-Host "Started PID $($process.Id)" -ForegroundColor Green
}

$ok = $false
for ($i=0; $i -lt 120; $i++) {
    try {
        $null = Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 2
        $ok = $true
        break
    } catch {
        if ($process -and $process.HasExited) {
            if (Test-Path $StderrLog) { Get-Content $StderrLog -Tail 100 }
            throw "ComfyUI exited early with code $($process.ExitCode)."
        }
        Start-Sleep -Seconds 1
    }
}
if (-not $ok) {
    if (Test-Path $StderrLog) { Get-Content $StderrLog -Tail 100 }
    throw "ComfyUI API did not become available at $Base"
}

$ObjectInfo = Invoke-RestMethod -Uri "$Base/object_info" -TimeoutSec 120
$Required = @('WanAnimate2ToVideo','LoadImage','LoadVideo','UNETLoader','CLIPLoader','CLIPVisionLoader','CLIPVisionEncode','VAELoader')
Write-Host ''
Write-Host 'Required node classes:' -ForegroundColor Cyan
foreach ($name in $Required) {
    if ($ObjectInfo.PSObject.Properties.Name -contains $name) {
        Write-Host "[OK]   $name" -ForegroundColor Green
    } else {
        Write-Host "[MISS] $name" -ForegroundColor Red
        $failed = $true
    }
}

$Probe = [ordered]@{
    gate = 'WAN_ANIMATE2_W0_BF16_SCHEMA_PREFLIGHT'
    route = 'base_bf16_reference'
    comfy_root = $ComfyRoot
}
foreach ($name in @('UNETLoader','WanAnimate2ToVideo','LoadVideo','CLIPLoader','CLIPVisionLoader','CLIPVisionEncode','VAELoader','BasicScheduler','KSamplerSelect','ModelSamplingSD3')) {
    if ($ObjectInfo.PSObject.Properties.Name -contains $name) { $Probe[$name] = $ObjectInfo.$name }
}
$ProbePath = Join-Path $Workspace 'object_info_wan_bf16.json'
$Probe | ConvertTo-Json -Depth 50 | Set-Content -Path $ProbePath -Encoding utf8
Write-Host "Saved exact installed node schemas to: $ProbePath" -ForegroundColor Green

if ($failed) { throw 'Wan-Animate-2 BF16 schema preflight FAILED. Do not run W0 inference yet.' }

Write-Host ''
Write-Host 'WAN BF16 SCHEMA PREFLIGHT: PASS' -ForegroundColor Green
Write-Host 'Do not infer yet. The W0 workflow must be built from this exact schema so no widget/cache semantics are guessed.' -ForegroundColor Yellow
