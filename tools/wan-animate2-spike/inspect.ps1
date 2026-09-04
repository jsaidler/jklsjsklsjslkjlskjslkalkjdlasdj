param(
    [string]$Workspace = 'D:\AI\WanAnimate2',
    [int]$Port = 8188
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Find-ComfyRoot([string]$Base) {
    foreach ($candidate in @($Base, (Join-Path $Base 'ComfyUI'))) {
        if ((Test-Path (Join-Path $candidate 'main.py')) -and (Test-Path (Join-Path $candidate '.git'))) {
            return $candidate
        }
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
if (-not $ComfyRoot) {
    throw "ComfyUI not found at $Workspace or $(Join-Path $Workspace 'ComfyUI'). Run bootstrap.ps1 first."
}
$WorkspacePython = Find-WorkspacePython $Workspace $ComfyRoot
if (-not $WorkspacePython) {
    throw 'ComfyUI workspace Python was not found.'
}

Write-Host "Resolved ComfyUI root: $ComfyRoot" -ForegroundColor Green
Write-Host "ComfyUI Python:      $WorkspacePython" -ForegroundColor Green

$Stdout = Join-Path $Workspace "comfyui_$Port.stdout.log"
$Stderr = Join-Path $Workspace "comfyui_$Port.stderr.log"

$Base = "http://127.0.0.1:$Port"
$alreadyRunning = $false
try {
    $null = Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 2
    $alreadyRunning = $true
    Write-Host "ComfyUI is already responding at $Base" -ForegroundColor Green
} catch { }

if (-not $alreadyRunning) {
    Write-Host 'Starting ComfyUI headlessly in background...' -ForegroundColor Cyan
    $proc = Start-Process -FilePath $WorkspacePython `
        -ArgumentList @('main.py','--listen','127.0.0.1','--port',"$Port") `
        -WorkingDirectory $ComfyRoot `
        -RedirectStandardOutput $Stdout `
        -RedirectStandardError $Stderr `
        -PassThru
    Write-Host "PID: $($proc.Id)"
}

$ok = $false
for ($i = 0; $i -lt 120; $i++) {
    try {
        $null = Invoke-RestMethod -Uri "$Base/system_stats" -TimeoutSec 2
        $ok = $true
        break
    } catch {
        Start-Sleep -Seconds 1
    }
}
if (-not $ok) {
    if (Test-Path $Stderr) {
        Write-Host '--- stderr tail ---' -ForegroundColor Yellow
        Get-Content $Stderr -Tail 80
    }
    throw "ComfyUI API did not become available at $Base"
}

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

foreach ($log in @($Stdout, $Stderr)) {
    if (Test-Path $log) {
        Write-Host ''
        Write-Host "Relevant lines from: $log"
        $imports = Select-String -Path $log -Pattern 'IMPORT FAILED|Rebels|GGUF|WanAnimate2|ERROR|Traceback' -SimpleMatch:$false
        if ($imports) { $imports | Select-Object -Last 50 | ForEach-Object { $_.Line } }
    }
}

if ($failed) {
    throw 'Wan-Animate-2 CLI preflight FAILED. Do not build or run the workflow yet.'
}

Write-Host ''
Write-Host 'CLI preflight PASSED.' -ForegroundColor Green
Write-Host 'Important: model class=WAN_Animate2 can only be proven when the GGUF is actually loaded during a workflow run.' -ForegroundColor Yellow
Write-Host 'The next step is to generate a headless API workflow from the installed schemas, then execute it from the command line.'
